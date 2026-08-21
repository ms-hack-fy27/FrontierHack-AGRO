# 🎉 Lab complete — Call Center Triage (NovaTel Communications)

Congratulations — you built, instrumented, evaluated, and deployed a production-ready multi-agent AI system from scratch. Here is what you accomplished.

---

## Recap

| # | Challenge | What you built |
|---|-----------|----------------|
| 0 | **Setup** | Provisioned a Microsoft Foundry resource, project, GPT model deployment, Log Analytics workspace, and Application Insights instance using `azd provision` |
| 1 | **Build agents** | Built an **Intent Classification Agent** (classifies billing, technical, cancellation, upsell, and security intents with a `lookup_customer` tool) and a **Resolution Advisor Agent** (recommends retention offers and actions by customer tier) |
| 2 | **Monitor** | Enabled OpenTelemetry GenAI tracing — every model call, tool invocation, and token count is captured as a distributed trace in Application Insights |
| 3 | **Evaluate** | Ran systematic LLM-as-judge evaluations across the call set, producing repeatable coherence and fluency scores that can be tracked across prompt versions |
| 4 | **Production workflow** | Connected both agents in an orchestrated workflow in the Foundry portal — a stable, testable endpoint with run history supervisors can inspect |

### Skills practiced

- Design system prompts for agents with clear role boundaries and constraints
- Ground agents in real data through tool calls (function calling)
- Distributed tracing for AI systems with OpenTelemetry
- LLM-as-judge evaluation with the Azure AI Evaluation SDK
- Multi-agent orchestration in the Foundry portal

---

## Next steps

Want to take the NovaTel system further? Here are some directions:

- **Add more agents** — a Sentiment Analysis Agent that scores call tone or a Knowledge Base Agent that retrieves troubleshooting articles before the Resolution Advisor responds
- **Connect real data** — replace static `call_data.json` with a live CRM query or telephony webhook
- **Improve evaluation** — add task-specific evaluators (for example, "did the agent offer a retention discount to a Premium customer at risk of cancellation?") alongside generic coherence scores
- **Configure CI/CD** — run your evaluation set automatically on every prompt change using GitHub Actions and fail the build if quality scores fall below a threshold
- **Explore fine-tuning** — use your traced conversations as training data to fine-tune a smaller, less expensive model for intent classification
- **Try another scenario** — the [Factory](../factory/README.md) and [Claims](../claims/README.md) scenarios cover predictive maintenance and insurance claims processing using the same lifecycle

---

## Clean up Azure resources

> **Important:** resources deployed in Challenge 0 incur Azure charges while they exist. Delete them when you are finished.

### What will be deleted

- The `foundry-hackathon-rg-<suffix>` resource group and everything in it:
  - Microsoft Foundry Resource + project
  - GPT model deployment
  - Log Analytics workspace
  - Application Insights instance

### Option 1 — azd down

From the repository root (where the `azd` environment was initialized), run:

```bash
azd down --purge
```

The command uses the `azd` environment created by `azd provision` to know exactly which resource group to delete. It asks for confirmation before deletion.

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
