[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [Alias('number-of-users')]
    [ValidateRange(1, 1000)]
    [int] $NumberOfUsers,

    [Parameter()]
    [string] $UpnDomain,

    [Parameter()]
    [string] $Location = 'swedencentral',

    [Parameter()]
    [string[]] $Roles = @('Contributor', 'Foundry User'),

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

function Resolve-UpnDomain {
    param(
        [Parameter()]
        [string] $ConfiguredDomain
    )

    $verifiedDomains = @()
    $defaultVerifiedDomain = ''

    try {
        $verifiedDomainsRaw = Invoke-AzCli -Arguments @(
            'rest', '--method', 'GET',
            '--url', 'https://graph.microsoft.com/v1.0/domains?$select=id,isDefault,isVerified',
            '--query', 'value[?isVerified].id',
            '-o', 'tsv'
        )
        $defaultVerifiedDomain = ([string] (Invoke-AzCli -Arguments @(
                    'rest', '--method', 'GET',
                    '--url', 'https://graph.microsoft.com/v1.0/domains?$select=id,isDefault,isVerified',
                    '--query', 'value[?isVerified && isDefault].id | [0]',
                    '-o', 'tsv'
                ))).Trim()

        if ($null -ne $verifiedDomainsRaw) {
            $verifiedDomains = @([string] $verifiedDomainsRaw -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
        }
    }
    catch {
        $verifiedDomains = @()
        $defaultVerifiedDomain = ''
    }

    if (-not [string]::IsNullOrWhiteSpace($ConfiguredDomain)) {
        $candidate = $ConfiguredDomain.Trim()
        if ($verifiedDomains.Count -eq 0 -or $verifiedDomains -contains $candidate) {
            return $candidate
        }

        $domainList = $verifiedDomains -join ', '
        throw "Domain '$candidate' is not a verified domain in this tenant. Verified domains: $domainList"
    }

    if (-not [string]::IsNullOrWhiteSpace($defaultVerifiedDomain)) {
        return $defaultVerifiedDomain
    }

    $accountUpn = ([string] (Invoke-AzCli -Arguments @('account', 'show', '--query', 'user.name', '-o', 'tsv'))).Trim()
    if ($accountUpn -match '@') {
        return $accountUpn.Split('@')[1]
    }

    throw 'Unable to infer a valid UPN domain. Provide -UpnDomain explicitly using a verified tenant domain (for example: contoso.onmicrosoft.com).'
}

function New-StrongPassword {
    param(
        [int] $Length = 20
    )

    $allowed = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%*_-+='.
        ToCharArray()
    $buffer = New-Object char[] $Length
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] $Length
    $rng.GetBytes($bytes)

    for ($i = 0; $i -lt $Length; $i++) {
        $buffer[$i] = $allowed[$bytes[$i] % $allowed.Length]
    }

    $password = -join $buffer
    if ($password -notmatch '[A-Z]' -or $password -notmatch '[a-z]' -or $password -notmatch '[0-9]' -or $password -notmatch '[^A-Za-z0-9]') {
        return New-StrongPassword -Length $Length
    }

    return $password
}

function Ensure-RoleExists {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RoleName
    )

    $roleId = (Invoke-AzCli -Arguments @('role', 'definition', 'list', '--name', $RoleName, '--query', '[0].id', '-o', 'tsv')).Trim()
    if ([string]::IsNullOrWhiteSpace($roleId)) {
        throw "Role '$RoleName' was not found in this tenant/subscription context."
    }
}

function Ensure-RoleAssignment {
    param(
        [Parameter(Mandatory = $true)]
        [string] $PrincipalObjectId,

        [Parameter(Mandatory = $true)]
        [string] $RoleName,

        [Parameter(Mandatory = $true)]
        [string] $Scope
    )

    $existingRaw = Invoke-AzCli -Arguments @(
            'role', 'assignment', 'list',
            '--assignee-object-id', $PrincipalObjectId,
            '--scope', $Scope,
            '--role', $RoleName,
            '--query', '[0].id',
            '-o', 'tsv'
        )
    $existing = if ($null -eq $existingRaw) { '' } else { ([string] $existingRaw).Trim() }

    if (-not [string]::IsNullOrWhiteSpace($existing)) {
        return 'exists'
    }

    Invoke-AzCli -Arguments @(
        'role', 'assignment', 'create',
        '--assignee-object-id', $PrincipalObjectId,
        '--assignee-principal-type', 'User',
        '--role', $RoleName,
        '--scope', $Scope,
        '--only-show-errors'
    ) | Out-Null

    return 'created'
}

function Get-UserObjectIdByUpn {
    param(
        [Parameter(Mandatory = $true)]
        [string] $UserPrincipalName
    )

    $escapedUpn = $UserPrincipalName.Replace("'", "''")
    $result = Invoke-AzCli -Arguments @(
            'ad', 'user', 'list',
            '--filter', "userPrincipalName eq '$escapedUpn'",
            '--query', '[0].id',
            '-o', 'tsv'
        )

    if ($null -eq $result) {
        return ''
    }

    return ([string] $result).Trim()
}

Write-Host 'Starting hackathon user provisioning...'

Invoke-AzCli -Arguments @('version') | Out-Null
Invoke-AzCli -Arguments @('account', 'show', '--query', 'id', '-o', 'tsv') | Out-Null

if (-not [string]::IsNullOrWhiteSpace($SubscriptionId)) {
    Invoke-AzCli -Arguments @('account', 'set', '--subscription', $SubscriptionId) | Out-Null
}

$activeSubscriptionId = (Invoke-AzCli -Arguments @('account', 'show', '--query', 'id', '-o', 'tsv')).Trim()
$resolvedUpnDomain = Resolve-UpnDomain -ConfiguredDomain $UpnDomain

if ($null -eq $Roles -or $Roles.Count -eq 0) {
    throw 'At least one role must be provided in -Roles.'
}

$resolvedRoles = @($Roles | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_.Trim() })
if ($resolvedRoles.Count -eq 0) {
    throw 'At least one non-empty role must be provided in -Roles.'
}

foreach ($role in $resolvedRoles) {
    Ensure-RoleExists -RoleName $role
}

Write-Host "Subscription: $activeSubscriptionId"
Write-Host "UPN domain: $resolvedUpnDomain"
Write-Host "Roles: $($resolvedRoles -join ', ')"

$results = @()

for ($i = 1; $i -le $NumberOfUsers; $i++) {
    $suffix = '{0:000}' -f $i
    $userAlias = "hack-dev-$suffix"
    $resourceGroupName = "rg-hack-dev-$suffix"
    $userPrincipalName = "$userAlias@$resolvedUpnDomain"
    $mailNickname = $userAlias.Replace('-', '')

    $userState = 'exists'
    $resourceGroupState = 'exists'
    $roleStates = @{}
    $generatedPassword = ''

    Write-Host "[$userAlias] User creation started"

    try {
        $userObjectId = Get-UserObjectIdByUpn -UserPrincipalName $userPrincipalName

        if ([string]::IsNullOrWhiteSpace($userObjectId)) {
            $generatedPassword = 'P@$$w0rd' # New-StrongPassword  ##generate random strong password 
            Invoke-AzCli -Arguments @(
                'ad', 'user', 'create',
                '--display-name', $userAlias,
                '--user-principal-name', $userPrincipalName,
                '--mail-nickname', $mailNickname,
                '--password', $generatedPassword,
                '--force-change-password-next-sign-in', 'true',
                '--only-show-errors'
            ) | Out-Null

            $userObjectId = Get-UserObjectIdByUpn -UserPrincipalName $userPrincipalName
            $userState = 'created'
            Write-Host "[$userAlias] User created: $userPrincipalName"
        }
        else {
            Write-Host "[$userAlias] User already exists: $userPrincipalName"
        }

        Write-Host "[$userAlias] Resource group creation started: $resourceGroupName"
        $groupExists = (Invoke-AzCli -Arguments @('group', 'exists', '--name', $resourceGroupName)).Trim()
        if ($groupExists -ne 'true') {
            Invoke-AzCli -Arguments @(
                'group', 'create',
                '--name', $resourceGroupName,
                '--location', $Location,
                '--only-show-errors'
            ) | Out-Null
            $resourceGroupState = 'created'
            Write-Host "[$userAlias] Resource group created: $resourceGroupName"
        }
        else {
            Write-Host "[$userAlias] Resource group already exists: $resourceGroupName"
        }

        $scope = (Invoke-AzCli -Arguments @('group', 'show', '--name', $resourceGroupName, '--query', 'id', '-o', 'tsv')).Trim()
        Write-Host "[$userAlias] Adding roles to scope: $scope"
        foreach ($role in $resolvedRoles) {
            $roleStates[$role] = Ensure-RoleAssignment -PrincipalObjectId $userObjectId -RoleName $role -Scope $scope
            Write-Host "[$userAlias] Role '$role' assignment status: $($roleStates[$role])"
        }

        $roleAssignmentsSummary = ($resolvedRoles | ForEach-Object { "$_=$($roleStates[$_])" }) -join '; '

        $results += [pscustomobject]@{
            User                = $userPrincipalName
            UserState           = $userState
            ResourceGroup       = $resourceGroupName
            ResourceGroupState  = $resourceGroupState
            RoleAssignments     = $roleAssignmentsSummary
            TemporaryPassword   = $generatedPassword
            Status              = 'ok'
            Error               = ''
        }

        Write-Host "[$userAlias] User creation finished"
    }
    catch {
        Write-Host "[$userAlias] User creation finished with failure"
        $results += [pscustomobject]@{
            User                = $userPrincipalName
            UserState           = $userState
            ResourceGroup       = $resourceGroupName
            ResourceGroupState  = $resourceGroupState
            RoleAssignments     = if ($roleStates.Count -gt 0) { ($resolvedRoles | ForEach-Object { "$_=$($roleStates[$_])" }) -join '; ' } else { 'n/a' }
            TemporaryPassword   = $generatedPassword
            Status              = 'failed'
            Error               = $_.Exception.Message
        }
    }
}

Write-Host ''
Write-Host 'Provisioning summary:'
$results | Select-Object User, UserState, ResourceGroup, ResourceGroupState, RoleAssignments, Status | Format-Table -AutoSize

$createdWithPasswords = @($results | Where-Object { -not [string]::IsNullOrWhiteSpace($_.TemporaryPassword) })
if ($createdWithPasswords.Count -gt 0) {
    Write-Host ''
    Write-Warning 'Temporary passwords (shown once):'
    $createdWithPasswords | Select-Object User, TemporaryPassword | Format-Table -AutoSize
}

$failedItems = @($results | Where-Object { $_.Status -eq 'failed' })
$failedCount = $failedItems.Count
if ($failedCount -gt 0) {
    Write-Host ''
    Write-Host 'Failed items:'
    $failedItems | Select-Object User, ResourceGroup, Error | Format-Table -AutoSize
    Write-Host ''
    Write-Error "Completed with $failedCount failed item(s). Review the Error column in the summary."
}

Write-Host ''
Write-Host 'Done.'