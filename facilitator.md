# Facilitator - Preparing Hackthon environment

## Scripts

The scripts under `scripts/` perform tenant and subscription administration separately from `azd`:

- [`hackthon-setup.ps1`](scripts/hackthon-setup.ps1) creates `hack-dev-001`, `hack-dev-002`, and subsequent Microsoft Entra users, creates matching `rg-hack-dev-001`, `rg-hack-dev-002`, and subsequent resource groups, and assigns each user the `Contributor` and `Foundry User` roles on their matching resource group by default.
- The setup script does **not** run `azd` or deploy `infra/main.bicep` into those resource groups. Each participant or facilitator must perform the actual lab deployment separately.
- The current setup implementation assigns the fixed temporary password `P@$$w0rd`, forces a password change at first sign-in, and prints newly assigned temporary passwords in its final output. Treat that output as sensitive and replace the fixed-password implementation before using the script outside a controlled workshop.
- [`hackthon-cleanup.ps1`](scripts/hackthon-cleanup.ps1) deletes Microsoft Entra users and resource groups by name prefix. Its defaults match `hack-dev*` users and `rg-hack-dev*` resource groups. Resource-group deletion is asynchronous by default (`-NoWait $true`). Review the prefixes and active subscription before running it because deletion is destructive.

Running these scripts requires permissions to create and delete Microsoft Entra users, create and delete resource groups, and assign Azure roles. Supplying `-SubscriptionId` changes the active Azure CLI subscription before resource-group operations.

## Identity and security

The Foundry account and project use system-assigned managed identities. The current template also sets:

- `publicNetworkAccess: 'Enabled'` on the Foundry account.
- `disableLocalAuth: false`, so local authentication remains enabled.
- Application Insights connection credentials in the Foundry connection.
- GenAI message-content capture to `true` in the generated local `.env` file.

These settings are suitable for a short-lived workshop, but they are not a production security baseline. A production deployment should evaluate private networking, restricted ingress, Microsoft Entra ID-only authentication where supported, least-privilege role assignments, secret rotation, telemetry content redaction, and policy controls. Do not print or commit generated connection strings, keys, temporary passwords, or captured prompt content.

## Observability path

The Application Insights resource is workspace-based and uses the Log Analytics workspace created by the same template. Challenge 2 enables GenAI tracing from the local Python agents using the generated connection string. Traces can then be inspected in Application Insights and the Microsoft Foundry portal, including model calls, latency, errors, and token usage.