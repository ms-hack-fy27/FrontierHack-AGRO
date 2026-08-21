# 🎉 Lab Complete — Claims Processing (ClaimSight Insurance)

Congratulations: you built, instrumented, evaluated, and deployed a production-ready multi-agent AI system from scratch. Here is what you accomplished.

---

## Recap

| # | Challenge | What you built |
|---|-----------|----------------|
| 0 | **Setup** | Provisioned a Microsoft Foundry resource, project, GPT model deployment, Log Analytics workspace, and Application Insights instance using `azd provision` |
| 1 | **Build agents** | Built a **Claims Triage Agent** (assesses document completeness, fraud risk, and policy coverage) and a **Claims Decision Agent** (recommends approval, acceleration, investigation, or denial with justification) |
| 2 | **Monitor** | Enabled OpenTelemetry GenAI tracing: every model call, tool invocation, and token count is captured as a distributed trace in Application Insights |
| 3 | **Evaluate** | Ran systematic LLM-as-a-judge evaluations across the claims dataset, producing repeatable coherence and fluency scores that can be tracked by version across prompt changes |
| 4 | **Production workflow** | Connected both agents in an orchestrated pipeline in the Foundry portal, creating a stable, testable endpoint with run history that regulators can inspect and audit |

### Skills Practiced

- Design system prompts for agents with clear role boundaries and constraints
- Ground agents in real claims data through tool calls (function calling)
- Distributed tracing for AI systems with OpenTelemetry
- LLM-as-a-judge evaluation using the Azure AI Evaluation SDK
- Multi-agent orchestration in the Foundry portal

---

## Next Steps

Want to take the ClaimSight system further? Here are some directions:

- **Add more agents**: a Document Extraction agent that analyzes uploaded PDFs or a Fraud Patterns agent that cross-references policyholder claims history
- **Connect real data**: replace the static `claims_data.json` with a live policy management system or a document storage query
- **Improve evaluation**: add task-specific evaluators (for example, "Did the agent correctly flag a claim with a fraud score above 0.7?") alongside the generic coherence scores
- **Configure CI/CD**: run your evaluation dataset automatically on every prompt change using GitHub Actions and fail the build if quality scores fall below a threshold
- **Explore fine-tuning**: use your tracked claims decisions as training data to fine-tune a smaller model for the initial triage step
- **Try another scenario**: the [Factory](../factory/README.md) and [Call Center](../callcenter/README.md) scenarios cover predictive maintenance and customer support using the same lifecycle

---

## Clean Up Azure Resources

> **Important:** resources deployed in Challenge 0 incur Azure charges while they exist. Delete them when you are finished.

### What Will Be Deleted

- O grupo de recursos `foundry-hackathon-rg-<suffix>` e tudo dentro dele:
  - Microsoft Foundry Resource + project
  - GPT model deployment
  - Log Analytics workspace
  - Application Insights instance

### Option 1 — azd down

From the **claims** folder (where the `azd` environment was initialized), run:

```bash
cd claims
azd down --purge
```

The command uses the `azd` environment created by `azd provision` to identify exactly which resource group to target. It asks for confirmation before deleting it.

### Option 2 — Azure portal

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for **Resource groups**
3. Find `foundry-hackathon-rg-<your-suffix>`
4. Click **Delete resource group** and confirm

### Option 3 — Azure CLI

```bash
# Replace <suffix> with the value shown in your .env file
az group delete --name foundry-hackathon-rg-<suffix> --yes --no-wait
```
