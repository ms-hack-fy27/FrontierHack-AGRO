[CmdletBinding()]
param(
    [Parameter()]
    [string] $ResourceGroupPrefix = 'rg-hack-dev',

    [Parameter()]
    [string] $UserPrefix = 'hack-dev',

    [Parameter()]
    [bool] $NoWait = $true,

    [Parameter()]
    [string] $SubscriptionId
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Invoke-AzCli {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Arguments
    )

    $output = & az @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        $joinedArgs = $Arguments -join ' '
        throw "Azure CLI command failed: az $joinedArgs`n$output"
    }

    return $output
}

function Convert-ToList {
    param(
        [Parameter()]
        [AllowNull()]
        [object] $Value
    )

    if ($null -eq $Value) {
        return @()
    }

    if ($Value -is [System.Array]) {
        $items = @($Value | ForEach-Object { [string] $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
        if ($items.Count -gt 0) {
            return $items
        }
    }

    $text = [string] $Value
    if ([string]::IsNullOrWhiteSpace($text)) {
        return @()
    }

    return @($text -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

Write-Host 'Starting hackathon cleanup...'

Invoke-AzCli -Arguments @('version') | Out-Null
Invoke-AzCli -Arguments @('account', 'show', '--query', 'id', '-o', 'tsv') | Out-Null

if (-not [string]::IsNullOrWhiteSpace($SubscriptionId)) {
    Invoke-AzCli -Arguments @('account', 'set', '--subscription', $SubscriptionId) | Out-Null
}

$activeSubscriptionId = ([string] (Invoke-AzCli -Arguments @('account', 'show', '--query', 'id', '-o', 'tsv'))).Trim()
Write-Host "Subscription: $activeSubscriptionId"
Write-Host "Resource group prefix: $ResourceGroupPrefix"
Write-Host "User prefix: $UserPrefix"

$escapedRgPrefix = $ResourceGroupPrefix.Replace("'", "''")
$resourceGroupsRaw = Invoke-AzCli -Arguments @(
    'group', 'list',
    '--query', "[?starts_with(name, '$escapedRgPrefix')].name",
    '-o', 'tsv'
)
$resourceGroups = @(Convert-ToList -Value $resourceGroupsRaw)

$deletedGroups = 0
foreach ($groupName in $resourceGroups) {
    Write-Host "[RG] Deletion started: $groupName"

    if ($NoWait) {
        Invoke-AzCli -Arguments @('group', 'delete', '--name', $groupName, '--yes', '--no-wait', '--only-show-errors') | Out-Null
        Write-Host "[RG] Delete request submitted (no-wait): $groupName"
    }
    else {
        Invoke-AzCli -Arguments @('group', 'delete', '--name', $groupName, '--yes', '--only-show-errors') | Out-Null
        Invoke-AzCli -Arguments @('group', 'wait', '--name', $groupName, '--deleted') | Out-Null
        Write-Host "[RG] Deleted: $groupName"
    }

    $deletedGroups++
}

if ($resourceGroups.Count -eq 0) {
    Write-Host '[RG] No resource groups matched the prefix.'
}

$escapedUserPrefix = $UserPrefix.Replace("'", "''")
$usersJson = [string] (Invoke-AzCli -Arguments @(
        'ad', 'user', 'list',
        '--filter', "startsWith(displayName,'$escapedUserPrefix') or startsWith(userPrincipalName,'$escapedUserPrefix')",
        '--query', '[].{id:id,userPrincipalName:userPrincipalName,displayName:displayName}',
        '-o', 'json'
    ))

$users = @()
if (-not [string]::IsNullOrWhiteSpace($usersJson)) {
    $parsedUsers = $usersJson | ConvertFrom-Json
    $users = @($parsedUsers)
}

$users = @($users)

$deletedUsers = 0
foreach ($user in $users) {
    Write-Host "[USER] Deletion started: $($user.userPrincipalName)"
    Invoke-AzCli -Arguments @('ad', 'user', 'delete', '--id', $user.id) | Out-Null
    Write-Host "[USER] Deleted: $($user.userPrincipalName)"
    $deletedUsers++
}

if ($users.Count -eq 0) {
    Write-Host '[USER] No users matched the prefix.'
}

Write-Host ''
Write-Host 'Cleanup summary:'
Write-Host "Resource groups matched: $($resourceGroups.Count)"
Write-Host "Resource groups deletion requests sent: $deletedGroups"
Write-Host "Users matched: $($users.Count)"
Write-Host "Users deleted: $deletedUsers"
Write-Host ''
Write-Host 'Done.'