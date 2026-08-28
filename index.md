# Microsoft Frontier Hackathon

## Microsoft Foundry: Build, scale, observe, and secure your AI agents

Welcome to the **Microsoft Frontier Hackathon** hands-on lab, where ideas become real solutions.

Throughout Frontier Hack, you explored how AI is transforming organizations. Here, you will put that knowledge into practice.

In this lab, you will **build, monitor, evaluate, and orchestrate AI agents** using the Microsoft Foundry SDK, following a guided, scenario-based experience designed to take you from concept to a functional, enterprise-ready multi-agent system.

By the end, you will not just understand how agents work: you will have built an agent that can be **traced, evaluated, and deployed**.

## Choose your LAB

The scenarios use the same five-challenge structure. Choose the industry that best matches your interests.

| Scenario | Domain | What you will build |
|----------|--------|----------------|
| [📞 Call center](./callcenter/README.md) | Customer support | Intent classification and resolution guidance agents |
| [🌱 Smart Farm](./smart-farm/README.md) | Precision agriculture | Crop health monitoring and agricultural advisory agents |

## Challenge structure

All scenarios follow the same five challenges:

| # | Challenge | Duration |
|---|-----------|----------|
| 0 | **Setup** — Deploy the Azure AI Foundry infrastructure | 20 min |
| 1 | **Build agents** — Build two AI agents with tools | 30 min |
| 2 | **Monitor** — Enable GenAI tracing with Application Insights | 20 min |
| 3 | **Evaluate** — Run systematic quality evaluations | 30 min |
| 4 | **Workflow** — Orchestrate multiple agents in the Foundry portal | 20 min |

## Prerequisites

- Azure subscription with Contributor access
- Python 3.10 or later
- Azure CLI (`az`) installed and authenticated (`az login`)
- Azure Developer CLI (`azd`) installed
- A terminal (bash, PowerShell, or WSL)

## Getting started

1. Clone this repository and authenticate with `az login` and `azd auth login`.
2. To provision the default call center scenario, run `azd up` from the repository root.
3. For a specific scenario, enter `callcenter/` or `smart-farm/` and run `azd up`.
4. Complete challenges 1–4 in order; each one builds on the previous challenge.
5. The `agents.py` and `deploy.py` scripts are ready to run. Read the README in each challenge folder for instructions.
