# 🎉 Lab complete — Smart Farm Crop Health (GreenRise AgroTech)

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

Want to take the GreenRise system further? Here are some directions:

- **Connect live sensors** — replace the static farm snapshot with an IoT ingestion path using Azure IoT Operations, Event Hubs, or another telemetry source
- **Add specialist agents** — introduce weather, irrigation-planning, pest-management, or crop-disease agents and route findings to the right specialist
- **Persist recommendations** — store monitor results, recommended actions, and operator decisions so changes can be tracked by zone over time
- **Improve evaluation** — add task-specific evaluators for threshold accuracy, evidence grounding, escalation behavior, and agronomic action quality
- **Configure CI/CD** — run your evaluation set automatically on every prompt change using GitHub Actions and fail the build if quality scores fall below a threshold
- **Add notifications** — send urgent critical-zone alerts to a farm operations dashboard, email, or Microsoft Teams
- **Test changing conditions** — replay time-series readings to verify that the system detects recovery, deterioration, and repeated anomalies

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
