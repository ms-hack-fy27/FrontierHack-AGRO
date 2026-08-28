# Challenge 0: Setup and authentication

Tempo: ~20 minutos

## Objectives

By the end of this challenge, you will have:

- ✅ A fully provisioned Microsoft Foundry project with a deployed model
- ✅ Application Insights provisioned with its connection string available
- ✅ Local machine authentication to Foundry verified
- ✅ Confirmation that your agent endpoint is working

![setup](./images/setup.png)

## Comece agora

> [!NOTE]
> Before you start, make sure you have:
> - An **Azure subscription** where you have the **Contributor** role (to deploy infrastructure) and the **Foundry User** role (to create, evaluate, and run agents in Challenges 1–4).
> - A **GitHub account** to fork this repository and run it in GitHub Codespaces.
>
> **Owner** (or Contributor) permissions on the subscription alone are **not** sufficient. They provide control-plane access to create and manage resources, but creating and running agents are data-plane operations that require the separate **Foundry User** role assigned on the Foundry account. An Owner can assign it to themselves; a Contributor must ask an administrator to assign it after deployment.

There are two ways to get started — choose one:

> **First step for either option:** [fork this repository](https://github.com/ms-hack-fy27/FrontierHack-AGRO//fork) to your own GitHub account.

### Option A: GitHub Codespaces (recommended)

No local installation is required. Everything runs in a cloud development environment.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ms-hack-fy27/FrontierHack-AGRO)

1. Click the badge above (select your fork if applicable)
2. Wait for the Codespace to be created (~2 min)
3. In the terminal, sign in to Azure:

```bash
az login
```

4. Continue to **Deploy infrastructure** below.

---

### Option B: Local environment

Run everything on your own machine. Requires Python 3.10+ and the Azure CLI.

```bash
# 1. Clone this repo
git clone https://github.com/ms-hack-fy27/FrontierHack-AGRO/.git
cd FrontierWeekHack

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Log in to Azure
az login
```

4. Continue to **Deploy infrastructure** below.

## Deploy infrastructure

From the **callcenter** folder, initialize the `azd` environment and provision the infrastructure:

```bash
cd callcenter
azd auth login
azd provision
```

This provisions all resources and automatically writes your `.env` file to the **callcenter** folder. Deployment takes a few minutes. To change the region or names, use `azd env set` before running `azd provision`.

## Verify resource creation

Open the [Azure portal](https://portal.azure.com/) and find your resource group, which should now contain resources like these:

![Azure Portal Resources](./images/azure-portal-resources.png)

> [!NOTE]
> Resource name prefixes vary by scenario, and suffixes are unique to each deployment.

Open the [Microsoft Foundry portal](https://ai.azure.com/nextgen) and verify that you can access the Foundry project.

![Foundry Project](./images/foundry-project.png)

Select **Build** in the top navigation, then **Models**, and verify that the **gpt-5.4** model is deployed.

>[!NOTE]
> In some versions of the Foundry portal, the **Models** tab is named **Deployments**, but both serve the same purpose.

![Foundry Model](./images/foundry-model.png)

Select **gpt-5.4**, enter a test message in the model playground, and verify that you receive a response.

![Foundry Model Playground](./images/foundry-model-playground.png)


## Success criteria

- [ ] You can see your Microsoft Foundry project in the Azure portal
- [ ] A gpt-5.4 model deployment shows the status "Succeeded"
- [ ] You can send a test message in the Foundry Model Playground
