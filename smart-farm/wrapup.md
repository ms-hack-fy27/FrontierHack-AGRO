# 🎉 Lab complete 

Congratulations — you built, observed, evaluated, and orchestrated a multi-agent crop-health system for GreenRise AgroTech. Here is what you accomplished.

---

## Recap

| # | Challenge | What you built |
|---|-----------|----------------|
| 0 | **Setup** | Provisioned the `smart-farm-project` Microsoft Foundry project, a `gpt-5.4` model deployment, and Application Insights using `azd provision` |
| 1 | **Build agents** | Built a tool-grounded **Crop Health Monitor** and a tool-free **Agronomic Advisor** that analyze five growing zones and turn threshold violations into practical recommendations |
| 2 | **Monitor** | Enabled OpenTelemetry GenAI tracing and inspected model input, output, latency, token usage, and errors in Microsoft Foundry and Application Insights |
| 3 | **Evaluate** | Ran a repeatable 10-case evaluation covering normal, warning, critical, single-metric, and multi-metric conditions, then reviewed coherence and fluency at aggregate and row level |
| 4 | **Orchestrate** | Ran an interactive two-agent workflow that passes the Health Monitor's tool-grounded analysis to the Agronomic Advisor for diagnosis and an action plan |

### Skills practiced

- Design system prompts for agents with clear role boundaries and constraints
- Ground an agent in farm telemetry through the `check_health_monitor` function tool
- Compare soil moisture, temperature, humidity, and pH readings with configured thresholds
- Pass structured context between specialized agents
- Distributed tracing for AI systems with OpenTelemetry
- LLM-as-judge evaluation in Microsoft Foundry
- Interactive multi-agent orchestration with Azure AI Projects

You also verified the expected farm snapshot: **ZONE-ALPHA** and **ZONE-EPSILON** are warnings, **ZONE-GAMMA** is critical, and the remaining two zones are normal.

---

## Next steps

After completing these challenges, you will have a working multi-agent system with observability and evaluation configured. Here are some directions for taking it further:

- **Deploy as a hosted agent endpoint**
Microsoft Foundry can host your agents as persistent, scalable API endpoints — with no infrastructure to manage. Once hosted, your farm platform can send zone readings directly to the Classification Agent and receive health assessments in real time, replacing the manual morning review.

- **Connect live sensors**
Replace the static snapshot with a live telemetry path using Azure IoT Operations, Event Hubs, or your existing sensor gateway, so the agents classify current field conditions instead of a checked-in JSON file.

- **Add more tools to your agents**
This lab reads a local dataset through the `api-agro` service. In production, you would add tools that call real systems:
  - A `fetch_weather_forecast` tool that pulls rainfall and heat forecasts before recommending irrigation
  - An `open_work_order` tool that assigns field tasks to the right crew when a zone turns critical
  - A `check_treatment_history` tool that returns prior pest treatments so recommendations respect application intervals

- **Create a knowledge base**
Upload GreenRise's agronomy manuals, crop protocols, and approved pest-treatment guidance to a Microsoft Foundry knowledge base. Attach it to the Advisory Agent as a File Search tool so its recommendations are grounded in approved practice — rather than an invented version.

- **Integrate evaluations into CI/CD**
Run your evaluation set automatically on every pull request or deployment. If the coherence or relevance score falls below a threshold (for example, 3.5 out of 5), block the release. This prevents a system prompt edit or model update from silently reducing classification accuracy during the growing season.

- **Explore advanced agent patterns**
  - **Parallelize** classification across all 5 zones simultaneously instead of sequentially
  - **Add confidence thresholds** — if the Classification Agent cannot separate irrigation stress from disease risk, flag the zone for agronomist review instead of assigning a cause
  - **Human in the loop** — always route critical zones such as ZONE-GAMMA to an agronomist, regardless of the agent's confidence level

- **Tune for your domain**
Use evaluation results to identify systematic errors — metrics the agent consistently misreads or crops it serves poorly. Use these cases to refine system prompts, add targeted few-shot examples, or fine-tune the underlying model with GreenRise field records.

---

## Clean up Azure resources

> **Important:** resources deployed in Challenge 0 incur Azure charges while they exist. Delete them when you are finished.

### What will be deleted

- The resource group created by the current `azd` environment and everything in it, including:
  - Microsoft Foundry Resource + project
  - `gpt-5.4` model deployment
  - Application Insights and supporting monitoring resources

### Option 1 — azd down

From the same directory and `azd` environment used to provision the lab, run:

```bash
azd down --purge
```

The command uses the environment created by `azd provision` to identify the deployed resources. It asks for confirmation before deletion.

### Option 2 — Azure portal

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for **Resource groups**
3. Open the resource group created by your lab deployment
4. Select **Delete resource group** and confirm

### Option 3 — Azure CLI

```bash
# Replace <resource-group-name> with the group created by azd provision
az group delete --name <resource-group-name> --yes --no-wait
```
