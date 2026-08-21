# Challenge 4: Production Workflow

Time: about 20 minutes

## Objectives

Run the Python orchestration, keep the two agents persistent, create a `WorkflowAgentDefinition`, and invoke the workflow with embedded farm data.

## Workflow

```text
ensure_agents_deployed()
        |
        v
run_health_scan()       -- monitor agent and check_crop_health loop
        |
        v
run_advisor()           -- tool-free agricultural advice
        |
        v
print_farm_report()
```

The portal workflow uses the same two agent names but embeds the zone data in its first step. Workflow steps cannot execute the local Python function loop, so portal input must say to analyze the supplied readings directly.

## Run the Python workflow

```powershell
cd smart-farm\challenge-4-deploy
python deploy.py
```

The script includes the required functions `check_crop_health`, `ensure_agents_deployed`, `run_health_scan`, `run_advisor`, `run_smart_farm_workflow`, `print_farm_report`, `create_workflow_agent`, and `run_portal_workflow`. It uses `gpt-5.4` by default and reads `PROJECT_CONNECTION_STRING` and `MODEL_DEPLOYMENT_NAME` from `.env`.

## Portal verification

1. Open Foundry Build -> Agents and confirm `crop-health-monitor-agent` and `agricultural-advisor-agent`.
2. Confirm the created `smart-farm-health-workflow` workflow is listed.
3. Preview the workflow and ask it to analyze the embedded readings.
4. Inspect the run history and traces. The final response should call out ZONE-GAMMA as critical and explain why.
5. Set `WORKFLOW_AGENT_NAME` in `.env` if you want subsequent runs to invoke a portal-created workflow by a custom name.

## Success criteria

- [ ] Python orchestration completes monitor -> advisor -> report.
- [ ] Both named agents are persistent Foundry assets.
- [ ] A `WorkflowAgentDefinition` is created with embedded farm data.
- [ ] The portal workflow runs without waiting for a local function call.
- [ ] The final report identifies critical readings and actionable agronomic advice.
