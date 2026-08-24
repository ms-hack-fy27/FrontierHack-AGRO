# Challenge 1: Build Agents

Time: about 30 minutes

## Objectives

Create a tool-grounded `smart-farm-monitor-agent` and a tool-free `smart-farm-advisor-agent`. Run them against five realistic crop zones and inspect the structured status output.

## Data and tool

Open `smart_farm_data.json`. It contains exactly five zones and four metrics per zone: `soil_moisture`, `temperature`, `humidity`, and `ph_level`. Every metric has `min` and `max` thresholds. The snapshot has two warnings, one critical zone, and two normal zones.

`check_health_monitor(zone_id)` reads this file and returns JSON with every metric, its threshold, an inclusive range result, and an anomaly deviation. The monitor agent must call this tool for each requested zone.

## Agent responsibilities

- `smart-farm-monitor-agent` uses the function tool and reports zone ID, crop, status, all metrics, anomalies, and a next step.
- `smart-farm-advisor-agent` has no tools. It reasons from the monitor output using irrigation-stress, fungal/disease-risk, and urgent-escalation patterns.

## Run

```powershell
cd smart-farm\challenge-1-build
python agents.py
```

The script creates both hosted agent versions, checks all five zones, forwards the monitor output to the advisor, and deletes the temporary versions and conversations when it exits.

## What to inspect

1. Find the `FunctionTool` schema and compare its name with `check_health_monitor`.
2. Follow the `responses.create()` loop and observe how each `FunctionCallOutput` is returned to the model.
3. Confirm that ZONE-GAMMA is critical and that ZONE-ALPHA and ZONE-EPSILON are warnings.
4. Open Foundry Build -> Agents and inspect both agents.

## Success criteria

- [ ] The tool returns threshold analysis for all four metrics.
- [ ] The monitor identifies two warning, one critical, and two normal zones.
- [ ] The advisor recommends irrigation action for irrigation stress.
- [ ] The advisor recommends fungal or disease investigation for high humidity plus low pH.
- [ ] Multiple critical readings produce urgent agronomist escalation.
