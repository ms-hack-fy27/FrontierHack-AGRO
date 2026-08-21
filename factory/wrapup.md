# 🎉 Lab Complete — Predictive Maintenance (TireForge Industries)

Congratulations — you built, instrumented, evaluated, and deployed a production-ready multi-agent AI system from scratch. Here is what you accomplished.

---

## Recap

| # | Challenge | What you built |
|---|-----------|----------------|
| 0 | **Setup** | Provisioned a Microsoft Foundry resource and project, a GPT model deployment, a Log Analytics workspace, and an Application Insights instance using `azd provision` |
| 1 | **Build Agents** | Created an **Anomaly Detection Agent** (reads live sensor telemetry — temperature, vibration, and pressure — and identifies machines operating outside safe limits) and a **Fault Diagnosis Agent** (determines root cause and recommends maintenance actions by machine type) |
| 2 | **Monitor** | Enabled OpenTelemetry GenAI tracing — every model call, tool invocation, and token count is captured as a distributed trace in Application Insights |
| 3 | **Evaluate** | Ran systematic LLM-as-a-judge evaluations across the sensor dataset, producing repeatable coherence and fluency scores that can be tracked by version across prompt changes |
| 4 | **Production Workflow** | Connected the two agents in an orchestrated Foundry portal pipeline — a stable, testable endpoint with run history that factory operators can inspect |

### Skills Practiced

- Designing agent system prompts with clear role boundaries and constraints
- Grounding agents in real sensor telemetry through tool calls (function calling)
- Distributed tracing for AI systems with OpenTelemetry
- LLM-as-a-judge evaluation using the Azure AI Evaluation SDK
- Multi-agent orchestration in the Foundry portal

---

## Next Steps

Want to take the TireForge system further? Here are some options:

- **Add more agents** — a Parts Inventory agent that checks whether replacement components are in stock before recommending maintenance, or a Scheduling agent that finds the earliest maintenance window with the least production impact
- **Connect real data** — replace the static `sensor_data.json` with a live stream from IoT Hub or Azure Event Hub
- **Improve evaluation** — add task-specific evaluators (for example, “did the agent correctly identify a Curing Press fault from the combination of elevated temperature and abnormal pressure?”) alongside generic coherence scores
- **Configure CI/CD** — automatically run your evaluation set after every prompt change using GitHub Actions and fail the build if quality scores fall below a threshold
- **Explore fine-tuning** — use your traced fault diagnoses as training data to fine-tune a smaller, less expensive model for the initial anomaly detection step
- **Try another scenario** — the [Claims](../claims/README.md) and [Call Center](../callcenter/README.md) scenarios cover insurance processing and customer support using the same lifecycle

---

## Clean Up Azure Resources

> **Important:** Resources deployed in Challenge 0 incur Azure costs while they exist. Delete them when you are finished.

### What Will Be Deleted

- The `foundry-hackathon-rg-<suffix>` resource group and everything in it:
  - Microsoft Foundry resource and project
  - GPT model deployment
  - Log Analytics workspace
  - Application Insights instance

### Option 1 — azd down

In the **factory** folder (where the `azd` environment was initialized), run:

```bash
cd factory
azd down --purge
```

The command uses the `azd` environment created by `azd provision` to know exactly which resource group to target. It asks for confirmation before deleting it.

### Option 2 — Azure portal

1. Open [portal.azure.com](https://portal.azure.com)
2. Search for **Resource groups**
3. Find `foundry-hackathon-rg-<your-suffix>`
4. Select **Delete resource group** and confirm

### Option 3 — Azure CLI

```bash
# Replace <suffix> with the value shown in your .env file
az group delete --name foundry-hackathon-rg-<suffix> --yes --no-wait
```
