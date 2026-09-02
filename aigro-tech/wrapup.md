# 🎉 Lab complete

Congratulations — you built, observed, evaluated, and orchestrated a multi-agent crop-health system for GreenRise AgroTech, entirely from the Microsoft Foundry portal. Here is what you accomplished.

---

## Recap

| # | Challenge | What you built |
|---|-----------|----------------|
| 0 | **Setup** | Created a Microsoft Foundry resource, a project, a model deployment, and an Application Insights connection — all through the Azure and Foundry portals |
| 1 | **Build agents** | Created a tool-grounded **Classifier Agent** (OpenAPI tool over the farm API) and an **Advisor Agent** (Azure AI Search tool over the treatment knowledge base) |
| 2 | **Monitor** | Inspected traces, spans, tool calls, token usage, and cost in the Foundry **Tracing** and **Monitoring** views and in Application Insights |
| 3 | **Evaluate** | Ran a repeatable 10-case evaluation covering normal, warning, critical, single-metric, and multi-metric conditions, then reviewed coherence and fluency at aggregate and row level |
| 4 | **Orchestrate** | Wired both agents into a visual workflow that passes the Classifier's tool-grounded analysis to the Advisor for diagnosis and an action plan |

### Skills practiced

- Provision Microsoft Foundry resources through the Azure portal
- Design system prompts for agents with clear role boundaries and constraints
- Ground an agent in a live REST API using the **OpenAPI** tool
- Ground an agent in documents using the **Azure AI Search** tool (RAG)
- Read distributed traces for AI systems and find the slow or failing span
- Run LLM-as-judge evaluation in Microsoft Foundry
- Compose multiple agents visually with the Workflows designer

You also verified the expected farm snapshot: **ZONE-ALPHA** and **ZONE-EPSILON** are warnings, **ZONE-GAMMA** is critical, and the remaining two zones are normal.

---

## Next steps

You now have a working multi-agent system with observability and evaluation configured. Here are some directions for taking it further:

- **Deploy as a hosted agent endpoint**
Microsoft Foundry can host your agents as persistent, scalable API endpoints — with no infrastructure to manage. Once hosted, your farm platform can send zone readings directly to the Classifier Agent and receive health assessments in real time, replacing the manual morning review.

- **Connect live sensors**
Replace the static snapshot behind the farm API with a live telemetry path using Azure IoT Operations, Event Hubs, or your existing sensor gateway, so the agents classify current field conditions instead of a fixed dataset.

- **Add more tools to your agents**
This lab reads a demonstration dataset through the farm API. In production, you would add tools that call real systems:
  - A **weather forecast** tool that pulls rainfall and heat forecasts before recommending irrigation
  - A **work order** tool that assigns field tasks to the right crew when a zone turns critical
  - A **treatment history** tool that returns prior pest treatments so recommendations respect application intervals

- **Create a knowledge base**
Upload GreenRise's agronomy manuals, crop protocols, and approved pest-treatment guidance to a Microsoft Foundry knowledge base. Attach it to the Advisor Agent as a File Search tool so its recommendations are grounded in approved practice — rather than an invented version.

- **Schedule your evaluations**
Foundry can run an evaluation on a schedule against live traces. If the coherence score falls below a threshold (for example, 3.5 out of 5), you get an alert — so a prompt edit or a model update cannot silently reduce classification quality during the growing season.

- **Explore advanced agent patterns**
  - **Add confidence thresholds** — if the Classifier cannot separate irrigation stress from disease risk, flag the zone for agronomist review instead of assigning a cause
  - **Human in the loop** — always route critical zones such as ZONE-GAMMA to an agronomist, regardless of the agent's confidence level
  - **Add a third agent** to the workflow, for example a Reporter that formats the day's plan for the field crew

- **Tune for your domain**
Use evaluation results to identify systematic errors — metrics the agent consistently misreads or crops it serves poorly. Use these cases to refine system prompts or add targeted examples.

---

## Clean up Azure resources

> **Important:** the resources you created in Challenge 0 incur Azure charges while they exist. Delete them when you are finished.

### What will be deleted

- The resource group you created in Challenge 0 and everything in it, including:
  - The Microsoft Foundry resource and its project
  - The model deployment
  - Application Insights and its Log Analytics workspace

### Steps

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for **Resource groups** and open the one you created in Challenge 0
3. Review the resource list — confirm it contains only lab resources
4. Select **Delete resource group**, type the resource group name to confirm, and select **Delete**

> [!NOTE]
> Deleting the resource group also deletes your agents, workflows, traces, and evaluation runs. If you want to keep an evaluation result, export it from the **Evaluations** page first.
