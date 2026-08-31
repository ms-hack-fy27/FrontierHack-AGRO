# GreenRise AgriTech Smart Farm

This folder contains a smart-farm dataset and read-only API plus examples for creating, tracing, evaluating, and orchestrating agents with Microsoft Foundry. This README describes the current implementation; some challenge guides describe intended behavior that is not wired into the code yet.

## What is implemented

| Component | Current behavior |
|---|---|
| Infrastructure | The repository-level `azure.yaml` and `infra/main.bicep` provision a Foundry resource and project, a `gpt-5.4` deployment, Bing Custom Search, Log Analytics, and Application Insights. |
| Smart Farm API | `api-agro/main.py` exposes the farm snapshot, zones, readings, and crops through a read-only FastAPI application. It is not currently called by the agent scripts. |
| Challenge 0 | Provisions the shared repository infrastructure. The post-provision hook writes `.env` at the repository root. |
| Challenge 1 | Creates `smart-farm-classifier-agent` and `smart-farm-advisor-agent`, then runs only the classifier against two zones embedded in the prompt. It does not register a function or OpenAPI tool, load the farm dataset, invoke the advisor, or delete the created agent versions. |
| Challenge 2 | Creates a temporary `smart-farm-tracing-agent`, sends one prompt containing five hard-coded zone statuses, exports telemetry to Application Insights, and then deletes the conversation and agent version. |
| Challenge 3 | Provides `eval_portal.jsonl` with 10 cases for a manual Foundry portal evaluation. There is no local evaluation runner or `evaluation_dataset.json`. |
| Challenge 4 | Contains an interactive two-agent orchestration script. The script expects `challenge-1-build/smart_farm_data.json`, which does not exist, and creates a `FunctionTool` definition without attaching it to the classifier. The local health-monitor function is therefore not wired end to end. |

## Farm data and API

The source dataset is `api-agro/data/smart_farm_data.json`. It contains a snapshot of five zones with crop details, inspection dates, observed issues, and these readings:

- `soil_moisture`
- `temperature`
- `humidity`
- `ph_level`

Each metric has a zone-specific minimum and maximum threshold. The stored statuses are two `warning` zones, one `critical` zone, and two `normal` zones.

The API serves that dataset through:

| Method | Route | Result |
|---|---|---|
| GET | `/farm` | Full farm snapshot |
| GET | `/zones` | All zones; accepts optional `zone_id` |
| GET | `/zones/{zone_id}` | One zone, matched case-insensitively |
| GET | `/zones/{zone_id}/readings` | All metric readings; accepts optional `metric` |
| GET | `/crops` | Crop summaries; accepts a case-insensitive partial `crop` filter |
| GET | `/swagger` | Swagger UI |

Run the API separately from the agent lab:

```powershell
cd smart-farm\api-agro
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000/swagger`. Static OpenAPI documents are checked in as `api-agro/openapi.json` and `api-agro/openapi.yaml`.

## Agent lab setup

### Prerequisites

- Azure subscription with permission to provision resources
- Microsoft Foundry access with permission to create and run agents
- Azure CLI, Azure Developer CLI (`azd`), Python 3.10+, and PowerShell
- An Azure identity available to `DefaultAzureCredential`

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r smart-farm\requirements.txt
az login
azd auth login
azd provision
```

The `postprovision` hook runs `scripts/write-env.ps1` and writes the variables consumed by the Python scripts to the repository-root `.env`, including `PROJECT_CONNECTION_STRING`, `MODEL_DEPLOYMENT_NAME`, and `APPLICATIONINSIGHTS_CONNECTION_STRING`.

## Challenges

| # | Guide | What can be run now |
|---|---|---|
| 0 | [Setup](./challenge-0-setup/README.md) | Provision the repository infrastructure and generate `.env`. |
| 1 | [Build](./challenge-1-build/README.md) | Create both hosted agent versions and run the classifier's hard-coded two-zone example. |
| 2 | [Monitor](./challenge-2-monitor/README.md) | Send one traced model call and export telemetry. |
| 3 | [Evaluate](./challenge-3-evaluate/README.md) | Upload the 10-case JSONL dataset and run an evaluation manually in Foundry. |
| 4 | [Workflow](./challenge-4-workflow/README.md) | Inspect the intended interactive handoff; code and data paths must be fixed before the documented tool-grounded flow works. |

Run each Python command from the directory specified by its guide. The challenge guides may still refer to the intended end state; use the implementation notes above when behavior differs.

## Cleanup

From the repository root, remove the resources provisioned by this repository:

```powershell
azd down
```

Because `azure.yaml` is shared at the repository root, this removes the shared deployment rather than resources scoped only to `smart-farm`.
