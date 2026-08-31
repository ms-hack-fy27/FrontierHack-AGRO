# 🌱 Scenario: Smart Farm Crop Health — GreenRise AgroTech

## Context

**GreenRise AgroTech** runs the Salinas Valley Demonstration Farm, where five growing zones are monitored for soil moisture, temperature, humidity, and pH. Each zone has its own crop and its own safe thresholds, so the same reading can be normal in one zone and an emergency in another. Today's snapshot covers 5 zones:

- **ZONE-ALPHA** — North Lettuce Beds (romaine lettuce)
- **ZONE-BETA** — East Tomato Greenhouse (heirloom tomatoes) 
- **ZONE-GAMMA** — South Strawberry Rows (strawberries) 
- **ZONE-DELTA** — West Bell Pepper Block (bell peppers) 
- **ZONE-EPSILON** — Central Herb Garden (basil and cilantro) 

## Your mission

Build an AI agent system that:

1. **Classifies zone health** — Compares every reading with that zone's thresholds and marks each metric critical, warning, or normal
2. **Recommends agronomic actions** — Turns threshold violations into practical irrigation, disease, and escalation guidance
3. **Prioritizes the day** — Produces a zone-by-zone summary the farm team can act on, with the critical zone first

## Challenges

| # | Challenge | What you'll do | Time |
|---|-----------|---------------|------|
| 0 | [Setup](./challenge-0-setup/README.md) | Deploy the Microsoft Foundry infrastructure | 20 min |
| 1 | [Build agents](./challenge-1-build/README.md) | Build the Classification and Advisory agents | 30 min |
| 2 | [Monitor](./challenge-2-monitor/README.md) | Enable GenAI tracing with Application Insights | 20 min |
| 3 | [Evaluate](./challenge-3-evaluate/README.md) | Run systematic quality evaluations | 30 min |
| 4 | [Orchestrate](./challenge-4-workflow/README.md) | Interactive two-agent orchestration | 20 min |

When you are done, see the [wrap up](./wrapup.md) for a recap and cleanup steps.

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
