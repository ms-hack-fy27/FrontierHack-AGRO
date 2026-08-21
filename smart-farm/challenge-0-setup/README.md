# Challenge 0: Setup

Time: about 20 minutes

## Objectives

Provision a Microsoft Foundry resource, the `smart-farm-project` project, a `gpt-5.4` deployment, and Application Insights. The post-provision hook writes the environment variables used by later challenges.

## Prerequisites

Use an Azure subscription where you can provision resources and a signed-in identity that can create and run Foundry agents. Install Python 3.10+, Azure CLI, `azd`, and PowerShell.

## Steps

1. From the repository root, create a virtual environment and install dependencies:

```powershell
cd smart-farm
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
az login
azd auth login
```

2. Provision the lab:

```powershell
azd provision
```

3. Confirm that `.env` was created and contains `PROJECT_CONNECTION_STRING` and `MODEL_DEPLOYMENT_NAME=gpt-5.4`.
4. Open the [Microsoft Foundry portal](https://ai.azure.com/nextgen), select the project, and confirm that the model deployment is ready.
5. Send a test message in the model playground.

## Success criteria

- [ ] `smart-farm-project` is available in Foundry.
- [ ] The `gpt-5.4` deployment is ready.
- [ ] Application Insights is connected or available to connect.
- [ ] `smart-farm/.env` contains the required environment variables.
