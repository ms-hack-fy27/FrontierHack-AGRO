# 🌱 Scenario: Smart Farm — GreenRise AgroTech

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