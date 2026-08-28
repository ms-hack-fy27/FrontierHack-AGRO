<img width="990" height="150" alt="Microsoft Agent-a-thon_banner_WEB_990x150" src="https://github.com/user-attachments/assets/5f550061-077d-421c-bba2-4a5820e72fad" />

# Microsoft Frontier Hackathon
## Microsoft Foundry: Build, scale, observe, and secure your AI agents
 
Welcome to the hands-on lab experience where ideas become real, enterprise-ready solutions. This is the most advanced of the three agent-building tracks. While the Explorer track creates your first no-code agent and the Maker track automates tasks with low-code tools, this track is designed for developers, engineers, and architects who want full control over models, orchestration, and operations.

In this lab, you will build, monitor, evaluate, and orchestrate AI agents using the Microsoft Foundry SDK. You will follow a guided, scenario-based experience designed to help turn a concept into a functional, enterprise-ready multi-agent system.
 
By the end, you will not just understand how agents work: you will have built an agent that can be traced, evaluated, and deployed.

## What you will learn

This lab guides you through the full lifecycle of building production-ready AI agents with [Microsoft Foundry](https://learn.microsoft.com/azure/ai-foundry/):

- **Agent design** — Build specialized agents with system prompts, tools, and domain-specific data
- **Observability** — Instrument agents with OpenTelemetry-based GenAI tracing through Application Insights
- **Quality evaluation** — Run LLM-as-a-judge evaluations to systematically measure agent output quality
- **Multi-agent orchestration** — Connect agents to automated workflows using the Python SDK and the Foundry portal

This is a **code-first hackathon**: you will write and run Python throughout the experience. However, several challenges also require interaction with the **Microsoft Foundry portal** to deploy models, explore traces, review evaluations, and create workflows visually. Expect to switch regularly between your IDE and the portal.


## Choose your scenario

All tracks teach the same Foundry concepts. Choose the one that best matches your interests:

| Scenario | Description | Start here |
|----------|-------------|------------|
| 📞 **Call center** | Classify call intents and guide resolutions at NovaTel Communications | [Call center lab](./callcenter/README.md) |
| 🌱 **Smart Farm** | Monitor crop health and recommend actions at GreenRise AgriTech | [Smart Farm lab](./smart-farm/README.md) |

All scenarios follow the same five-challenge structure:

| # | Challenge | Duration | What you will learn |
|---|-----------|----------|-------------------|
| 0 | **Setup** | 20 min | Provision Microsoft Foundry, deploy a model, and verify authentication |
| 1 | **Build agents** | 35 min | Build two agents with tools and system prompts |
| 2 | **Monitor** | 20 min | Enable GenAI tracing with Application Insights |
| 3 | **Evaluate** | 25 min | Run LLM-as-a-judge evaluations on test datasets |
| 4 | **Workflow** | 20 min | Orchestrate agents in a multi-step pipeline |

## Prerequisites

- **Azure subscription** with **Contributor** and **Foundry User** access
- A **GitHub account**
- **Python 3.10 or later** installed locally (pre-installed when using Codespaces)
- **Azure CLI** (`az`) installed (pre-installed when using Codespaces)
- **Azure Developer CLI** (`azd`) installed (pre-installed when using Codespaces)

## Deploy from the repository root

The root `azd` project provisions the call center scenario. After authenticating with Azure, run:

```bash
az login
azd auth login
azd up
```

The command creates resources in the `azd` environment's resource group and generates the `.env` file in the repository root. To change the environment or subscription, use `azd env set` before running `azd up`.

## Ready to go further?

### 1. Dive deeper with the documentation

- [What is Microsoft Foundry?](https://learn.microsoft.com/azure/foundry/what-is-foundry)
- [Foundry Agent Service overview](https://learn.microsoft.com/azure/foundry/agents/overview)
- [Trace your agents with Microsoft Foundry](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup)
- [Evaluate agentic workflows](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent)
- [azure-ai-projects SDK reference](https://learn.microsoft.com/python/api/azure-ai-projects/)

### 2. Keep learning with Microsoft Learn

- [Develop an AI agent with Foundry Agent Service](https://learn.microsoft.com/training/modules/develop-ai-agent-azure/) — 55-minute module
- [Build agentic workflows with Microsoft Foundry](https://learn.microsoft.com/training/modules/build-agent-workflows-microsoft-foundry/) — 1-hour module
- [Trace and debug your generative AI app](https://learn.microsoft.com/training/modules/tracing-generative-ai-app/) — 1-hour module
- [Evaluate generative AI performance in the Microsoft Foundry portal](https://learn.microsoft.com/training/modules/evaluate-models-azure-ai-studio/) — 38-minute module
- [Monitor your generative AI app](https://learn.microsoft.com/training/modules/monitor-generative-ai-app/) — 1-hour module
- [Develop generative AI apps on Azure](https://learn.microsoft.com/training/paths/develop-generative-ai-apps/) — learning path
- [Monitor AI workloads on Azure](https://learn.microsoft.com/training/paths/monitor-ai-workloads-on-azure/) — learning path
- [Operationalize AI responsibly with Azure AI Foundry](https://learn.microsoft.com/training/paths/operationalize-ai-responsibly/) — learning path
