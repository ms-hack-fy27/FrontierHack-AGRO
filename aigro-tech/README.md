# 🚜 Scenario: AIgro Tech — GreenRise AgroTech (no-code)

> **No code required.** Every step in this lab is done in the browser, in the [Microsoft Foundry portal](https://ai.azure.com/nextgen). There is nothing to clone, install, or run from a terminal.

## Context

**GreenRise AgroTech** runs the Smart Farm Demonstration, where five growing zones are monitored for soil moisture, temperature, humidity, and pH. Each zone has its own crop and its own safe thresholds, so the same reading can be normal in one zone and an emergency in another. Today's snapshot covers 5 zones:

- **ZONE-ALPHA** — North Lettuce Beds (romaine lettuce)
- **ZONE-BETA** — East Tomato Greenhouse (heirloom tomatoes)
- **ZONE-GAMMA** — South Strawberry Rows (strawberries)
- **ZONE-DELTA** — West Bell Pepper Block (bell peppers)
- **ZONE-EPSILON** — Central Herb Garden (basil and cilantro)

Each zone reports four metrics, each with its own zone-specific `min` and `max` threshold:

| Metric | Meaning | Typical default range |
|---|---|---|
| `soil_moisture` | Water available to the roots (%) | 30.0 – 65.0 |
| `temperature` | Air temperature (°C) | 12.0 – 30.0 |
| `humidity` | Relative humidity (%) | 45.0 – 80.0 |
| `ph_level` | Soil acidity (pH) | 6.0 – 7.0 |

Zones also record **issues** — for example a pest observation such as *Ácaro-branco (Polyphagotarsonemus latus)*.

## Your mission

Build an AI agent system that:

1. **Classifies zone health** — Compares every reading with that zone's thresholds and marks each metric critical, warning, or normal
2. **Recommends agronomic actions** — Turns threshold violations into practical irrigation, disease, and escalation guidance
3. **Prioritizes the day** — Produces a zone-by-zone summary the farm team can act on, with the critical zone first

## Challenges

| # | Challenge | What you'll do | Time |
|---|-----------|---------------|------|
| 0 | [Setup](./challenge-0-setup/README.md) | Create the Foundry resource, project, and model — all in the portal | 25 min |
| 1 | [Build agents](./challenge-1-build/README.md) | Create the Classifier and Advisor agents and attach their tools | 40 min |
| 2 | [Monitor](./challenge-2-monitor/README.md) | Read traces and the monitoring dashboard | 20 min |
| 3 | [Evaluate](./challenge-3-evaluate/README.md) | Run a quality evaluation on an uploaded dataset | 30 min |
| 4 | [Orchestrate](./challenge-4-workflow/README.md) | Connect both agents in the visual Workflows designer | 25 min |

## Prerequisites

- A modern web browser
- An Azure subscription where you have the **Contributor** and **Azure AI User** roles
- Nothing else — no Python, no Azure CLI, no `git`

> [!TIP]
> This lab is the click-through twin of the [Smart Farm](../smart-farm/README.md) lab. Same scenario, same data, same agent prompts — only the delivery differs. If you prefer Python and the SDK, do that one instead.

When you are done, see the [wrap up](./wrapup.md) for a recap and cleanup steps.
