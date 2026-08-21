# 🏭 Scenario: Predictive Maintenance — TireForge Industries

## Context

![scenario](./images/scenario.png)

**TireForge Industries** operates a tire factory with 5 critical machines:

- **MX-001** (Mixer) — Mixes raw rubber compounds
- **EX-002** (Extruder) — Shapes rubber into tread profiles
- **CP-003** (Curing Press) — Vulcanizes tires under heat and pressure
- **CU-004** (Cooling Unit) — Gradually cools cured tires
- **IS-005** (Inspection Station) — Performs quality assurance through vibration analysis

Each machine emits real-time sensor data: temperature, pressure, vibration, and RPM.



## Your Mission

![agentic-orchestration](./images/agentic-orchestration.png)

Create an AI agent system that:

1. **Detects anomalies** — Compare sensor readings with thresholds
2. **Diagnoses faults** — Reason about root causes from anomaly patterns
3. **Reports health** — Produce a consolidated factory health report

## Challenges

| # | Challenge | What you will do | Time |
|---|-----------|---------------|------|
| 0 | [Setup](./challenge-0-setup/README.md) | Provision the Microsoft Foundry infrastructure | 20 min |
| 1 | [Build Agents](./challenge-1-build/README.md) | Build Anomaly Detection + Fault Diagnosis agents | 30 min |
| 2 | [Monitor](./challenge-2-monitor/README.md) | Enable GenAI tracing with Application Insights | 20 min |
| 3 | [Evaluate](./challenge-3-evaluate/README.md) | Run systematic quality evaluations | 30 min |
| 4 | [Production Workflow](./challenge-4-deploy/README.md) | Multi-agent orchestration + portal workflow | 20 min |

## Why the Challenges Are in This Order

**Build first.** An agent with a vague system prompt or no tools will produce plausible but fabricated diagnoses. In a tire factory, that is not an academic problem — it means maintenance teams chasing nonexistent faults or failing to detect real faults until a machine stops mid-shift. The `check_thresholds` tool grounds the Anomaly Agent in the machines' actual specifications, rather than the LLM's general knowledge of what "normal" extruder vibration looks like.

**Monitor next.** When the Fault Diagnosis Agent recommends taking CP-003 offline, did it actually examine the sensor readings you supplied? Was `check_thresholds` called, or did the agent reason only from context? Application Insights traces answer that question. Without them, the only signal you have is a machine failure that should have been detected earlier.

**Evaluate next.** Tracing tells you that the agent ran. Evaluation tells you whether it ran correctly. The selected test set provides a repeatable score for comparison before and after any prompt change or model swap, helping detect regressions before they reach the factory floor.

**Deploy next.** The portal workflow turns what you built in scripts into something the maintenance team can actually use: a stable endpoint, a shift-by-shift factory health report, and a trace history for every diagnosis. That is the difference between a demo and a tool someone will trust before scheduling an unplanned maintenance window.


## Architecture

![architecture](./images/architecture.png)


## Next Steps

After completing these challenges, you will have a functional multi-agent system with observability and evaluation configured. Here are some ways to take it further:

**Deploy as a hosted agent endpoint**
Microsoft Foundry can host your agents as persistent, scalable API endpoints with no infrastructure to manage. Once hosted, any system (a SCADA dashboard, a maintenance mobile app, or a Slack bot) can send a machine ID and receive a real-time diagnosis instead of manually running a Python script.

**Add more tools to your agents**
This lab's `check_thresholds` function uses local simulated data. In production, you would replace it with tools that call real systems:
- A `fetch_maintenance_history` tool that queries your CMMS (such as SAP PM or IBM Maximo) for previous faults on that machine
- A `lookup_spare_parts` tool that checks inventory availability before recommending a replacement
- A `create_work_order` tool that automatically opens a ServiceNow ticket when the Fault Diagnosis Agent flags a critical issue

**Create a knowledge base**
Upload TireForge machine manuals, vendor specification sheets, and historical incident reports to a Microsoft Foundry knowledge base. Attach it to the Fault Diagnosis Agent as a File Search tool so its recommendations are based on documented procedures rather than the LLM's general knowledge.

**Integrate evaluations into CI/CD**
Run your evaluation set automatically on every pull request or deployment. If the coherence or relevance score falls below a threshold (for example, 3.5 out of 5), block the release. This prevents a system prompt edit or model update from silently degrading diagnostic quality in production.

**Explore advanced agent patterns**
- **Parallelize** anomaly checks across all 5 machines simultaneously instead of sequentially
- **Add confidence thresholds** — if the Anomaly Detection Agent is uncertain, route the case to a human operator instead of automatically passing it to Fault Diagnosis
- **Human in the loop** — for critical faults, require a maintenance engineer to approve the recommended action before it triggers a work order

**Fine-tune for your domain**
Use evaluation results to identify systematic errors — machines the agent repeatedly misclassifies or fault types it handles poorly. Use these cases to refine system prompts, add targeted few-shot examples, or fine-tune the underlying model with TireForge-specific sensor patterns.
