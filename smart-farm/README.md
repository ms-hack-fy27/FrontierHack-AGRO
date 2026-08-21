# GreenRise AgriTech Smart Farm Lab

Build, observe, evaluate, and orchestrate crop-health agents for GreenRise AgriTech, a five-zone demonstration farm. The lab uses Microsoft Foundry, Azure AI Projects, Application Insights, and a portal workflow.

## Scenario

GreenRise monitors five crop zones. Each zone reports soil moisture, temperature, humidity, and pH. The supplied snapshot intentionally contains exactly two warning zones, one critical zone, and two normal zones so you can test both routine and urgent recommendations.

The two agents are:

- `crop-health-monitor-agent`: has the `check_crop_health` function tool and returns structured threshold analysis.
- `agricultural-advisor-agent`: has no tools and turns the monitor output into evidence-based agronomic advice.

## Challenges

| # | Challenge | Outcome | Time |
|---|---|---|---|
| 0 | [Setup](./challenge-0-setup/README.md) | Provision Foundry, the model, and Application Insights | 20 min |
| 1 | [Build](./challenge-1-build/README.md) | Create and test both agents with farm data | 30 min |
| 2 | [Monitor](./challenge-2-monitor/README.md) | Capture GenAI traces and inspect telemetry | 20 min |
| 3 | [Evaluate](./challenge-3-evaluate/README.md) | Run a repeatable 10-case quality evaluation | 30 min |
| 4 | [Workflow](./challenge-4-deploy/README.md) | Run Python orchestration and deploy a portal workflow | 20 min |

Complete the challenges in order. Challenge 4 reuses agents created in Challenge 1 and demonstrates why local function loops and portal workflows need different inputs.

## Prerequisites

- Azure subscription with permission to provision resources
- Azure CLI, Azure Developer CLI (`azd`), Python 3.10+, and PowerShell
- Microsoft Foundry access with permission to create and run agents
- A signed-in Azure identity available to `DefaultAzureCredential`

## Quick start

```powershell
cd smart-farm
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
azd auth login
azd provision
```

The post-provision hook writes `smart-farm/.env`. Then follow the challenge links above. Run Python commands from the challenge directory shown in each guide.

## Data contract

`challenge-1-build/smart_farm_data.json` contains the farm timestamp, five unique zone IDs and names, crop names, status, inspection date, four readings, and minimum/maximum thresholds for every reading. The tool compares each value inclusively with its range and reports deviations as percentages from the violated boundary.

## Cleanup

When finished, remove the lab's Azure resources with `azd down` from `smart-farm`. This does not change any other scenario in the repository.
