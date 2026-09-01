<#
.SYNOPSIS
    Publica a Smart Farm API-AGRO (FastAPI) no Azure App Service (Linux) usando o Azure CLI.

.DESCRIPTION
    Usa o contexto de autenticação já ativo do usuário (az login). Pergunta interativamente
    os valores necessários (ou usa os parâmetros informados na linha de comando para pular
    o prompt), cria (se não existirem) o Resource Group, o App Service Plan (Linux) e o
    Web App (runtime Python), configura o startup command do uvicorn e publica o código
    via zip deploy.

.PARAMETER AppName
    Nome do Web App. Se omitido, será perguntado interativamente.

.PARAMETER ResourceGroup
    Resource Group de destino. Se omitido, será perguntado interativamente (padrão sugerido: "<AppName>-rg").

.PARAMETER Plan
    Nome do App Service Plan. Se omitido, será perguntado interativamente (padrão sugerido: "<AppName>-plan").

.PARAMETER Location
    Região do Azure. Se omitido, será perguntado interativamente.

.PARAMETER Sku
    SKU do App Service Plan (Linux). Se omitido, será perguntado interativamente (padrão sugerido: "P0v3").

.PARAMETER Subscription
    Nome ou ID da subscription. Se omitido, será perguntado interativamente (padrão: subscription atual do az cli).

.EXAMPLE
    ./scripts/deploy-api-agro.ps1

.EXAMPLE
    ./scripts/deploy-api-agro.ps1 -AppName agro-api-demo -Location brazilsouth
#>

[CmdletBinding()]
param(
    [string]$AppName,
    [string]$ResourceGroup,
    [string]$Plan,
    [string]$Location,
    [string]$Sku,
    [string]$Subscription
)

function Read-ValueOrDefault {
    param(
        [string]$Prompt,
        [string]$Default
    )
    $label = if ($Default) { "$Prompt [$Default]" } else { $Prompt }
    $value = Read-Host $label
    if ([string]::IsNullOrWhiteSpace($value)) { return $Default }
    return $value
}

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$apiPath = Join-Path $repoRoot "smart-farm\api-agro"

if (-not (Test-Path $apiPath)) {
    throw "Não encontrei a pasta da API em '$apiPath'."
}

# 1. Contexto de autenticação do usuário (az login já deve ter sido executado)
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    throw "Nenhuma sessão do Azure CLI encontrada. Execute 'az login' antes de rodar este script."
}

if (-not $Subscription) {
    $Subscription = Read-ValueOrDefault -Prompt "Subscription (nome ou ID)" -Default $account.id
}
az account set --subscription $Subscription
$account = az account show | ConvertFrom-Json

Write-Host "Usando subscription: $($account.name) ($($account.id))" -ForegroundColor Cyan

# 2. Valores informados pelo usuário
if (-not $AppName) {
    $AppName = Read-ValueOrDefault -Prompt "Nome do Web App"
    while ([string]::IsNullOrWhiteSpace($AppName)) {
        Write-Host "O nome do Web App é obrigatório." -ForegroundColor Red
        $AppName = Read-ValueOrDefault -Prompt "Nome do Web App"
    }
}
if (-not $ResourceGroup) { $ResourceGroup = Read-ValueOrDefault -Prompt "Resource Group" -Default "$AppName-rg" }
if (-not $Plan) { $Plan = Read-ValueOrDefault -Prompt "App Service Plan" -Default "$AppName-plan" }

if (-not $Location) {
    $cliDefaultLocation = az config get defaults.location -o tsv 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $cliDefaultLocation) { $cliDefaultLocation = "eastus2" }
    $Location = Read-ValueOrDefault -Prompt "Região (location)" -Default $cliDefaultLocation
}

if (-not $Sku) { $Sku = Read-ValueOrDefault -Prompt "SKU do App Service Plan (Linux)" -Default "P0v3" }

Write-Host "Usando estes valores para o deploy:" -ForegroundColor Cyan
Write-Host "  App name        : $AppName"
Write-Host "  Resource group  : $ResourceGroup"
Write-Host "  App Service Plan: $Plan"
Write-Host "  Region          : $Location"
Write-Host "  Plan SKU        : $Sku Linux"
Write-Host "  Runtime         : PYTHON:3.12"

# 3. Resource Group (idempotente)
az group show -n $ResourceGroup --only-show-errors 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Criando resource group '$ResourceGroup'..." -ForegroundColor Yellow
    az group create -n $ResourceGroup -l $Location | Out-Null
}

# 4. App Service Plan Linux (idempotente)
az appservice plan show -n $Plan -g $ResourceGroup --only-show-errors 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Criando App Service Plan '$Plan'..." -ForegroundColor Yellow
    az appservice plan create -n $Plan -g $ResourceGroup --is-linux --sku $Sku -l $Location | Out-Null
}

# 5. Web App com runtime Python (idempotente)
az webapp show -n $AppName -g $ResourceGroup --only-show-errors 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Criando Web App '$AppName'..." -ForegroundColor Yellow
    az webapp create -n $AppName -g $ResourceGroup -p $Plan --runtime "PYTHON:3.12" | Out-Null
}

# 6. Build no lado do servidor (Oryx roda pip install a partir do requirements.txt)
Write-Host "Configurando build automático (Oryx)..." -ForegroundColor Yellow
az webapp config appsettings set -n $AppName -g $ResourceGroup `
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true | Out-Null

# WEBSITE_RUN_FROM_PACKAGE monta o zip como somente-leitura e pula o build do Oryx
# (causa "Could not find virtual environment directory antenv" e ModuleNotFoundError no startup)
az webapp config appsettings delete -n $AppName -g $ResourceGroup `
    --setting-names WEBSITE_RUN_FROM_PACKAGE 2>$null | Out-Null

# 7. Startup command (FastAPI via uvicorn)
Write-Host "Configurando startup command (uvicorn)..." -ForegroundColor Yellow
az webapp config set -n $AppName -g $ResourceGroup `
    --startup-file "python -m uvicorn main:app --host 0.0.0.0" | Out-Null

# 8. Empacotar o código (zip)
$zipPath = Join-Path $env:TEMP "api-agro-deploy.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

Write-Host "Empacotando código de '$apiPath'..." -ForegroundColor Yellow
$exclude = @(".git", ".venv", "venv", "__pycache__", "node_modules")
Push-Location $apiPath
try {
    $items = Get-ChildItem -Force | Where-Object { $exclude -notcontains $_.Name }
    Compress-Archive -Path $items -DestinationPath $zipPath -Force
}
finally {
    Pop-Location
}

# 9. Deploy via zip (track-status true para confirmar que o build do Oryx concluiu)
Write-Host "Publicando via 'az webapp deploy'..." -ForegroundColor Yellow
az webapp deploy -n $AppName -g $ResourceGroup --src-path $zipPath --type zip --track-status true

Remove-Item $zipPath -Force -ErrorAction SilentlyContinue

# 10. Endpoint
$hostName = az webapp show -n $AppName -g $ResourceGroup --query defaultHostName -o tsv

Write-Host ""
Write-Host "Deploy enviado com sucesso." -ForegroundColor Green
Write-Host "URL: https://$hostName" -ForegroundColor Green
Write-Host "Swagger: https://$hostName/swagger" -ForegroundColor Green
Write-Host ""
Write-Host "Obs: o App Service pode levar 2-3 minutos para 'aquecer' o container na primeira requisição." -ForegroundColor DarkGray
Write-Host "Para acompanhar logs: az webapp log tail -n $AppName -g $ResourceGroup" -ForegroundColor DarkGray
