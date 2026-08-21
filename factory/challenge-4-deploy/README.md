# Challenge 4: Production Workflow

Time: ~20 minutes

Create a multi-agent orchestration workflow for TireForge Industries and take it to production.

## Scenario

The individual agents you built in Challenge 1 are valuable, but in production agents need to work
**together** as an automated pipeline. In this challenge, you will connect the two agents into a
factory health workflow, run it from code, and then create and test it visually in the Foundry portal.

![deploy](./images/deploy.png)

## Learning Objectives

- Deploy persistent production agents (create once and reuse)
- Orchestrate multiple agents step by step in a Python workflow
- Create the same workflow visually in the Foundry portal
- Invoke the portal workflow from Python with live streaming
- View run history and traces in the portal

## The Workflow

```
ensure_agents_deployed()
        |
        v
run_anomaly_scan()          <-- Anomaly Detection Agent checks all 5 machines
        |
        v (for each machine with anomalies)
run_fault_diagnosis()       <-- Fault Diagnosis Agent diagnoses root cause
        |
        v
print_factory_report()      <-- Consolidated Health Report
```

---

## Part 1 — SDK: Build and Run the Python Workflow

### Step 1: Examine the implementation

Open [deploy.py](./deploy.py) and examine:

- **`ensure_agents_deployed()`** — lists existing agents and creates `anomaly-detection-agent` and `fault-diagnosis-agent` if they are not present
- **`run_anomaly_scan()`** — calls the anomaly agent and handles the `check_thresholds` function-call loop
- **`run_fault_diagnosis()`** — calls the diagnosis agent for each affected machine
- **`run_factory_health_workflow()`** — orchestrates all steps and returns the consolidated report

### Step 2: Run the workflow

```bash
cd factory/challenge-4-deploy
python deploy.py
```

Expected output:
```
=== Step 1: Ensure Agents Are Deployed ===
  Found existing: anomaly-detection-agent
  Found existing: fault-diagnosis-agent

=== Step 2a: Anomaly Scan ===
  CP-003 CRITICAL: vibration 143% above max, pressure 13.8% above max, temperature 10.3% above max
  MX-001 WARNING: vibration 6.7% above max, temperature 2.6% above max
  IS-005 WARNING: vibration 30% above max
  ...

=== Step 2b: Fault Diagnosis ===
  Diagnosing CP-003...
  Diagnosing MX-001...
  Diagnosing IS-005...

TIREFORGE FACTORY HEALTH REPORT
  Machines checked   : 5
  Machines affected  : 2
  ...
```

---

## Part 2 — Portal: Create and Test the Visual Workflow

### Step 3: Verify that agents are deployed in the portal

1. Open the [Microsoft Foundry portal](https://ai.azure.com/nextgen)
2. Select your project
3. Select **Build** → **Agents** in the top bar
4. Confirm that both agents appear:
   - `anomaly-detection-agent`
   - `fault-diagnosis-agent`


### Step 4: Create the workflow in the portal designer

1. Select **Build** → **Agents** → **Workflows**
2. Notice that the workflow created with the SDK in Part 1 is listed. Create a new workflow by selecting **Build** → **Blank workflow**

![Create workflow](./images/create-workflow.png)

3. In the visual designer, in the **Add a flow node** dialog, choose **Agent**

   ![add agent](./images/add-agent.png)

4. In the **Select an agent** picker, select `anomaly-detection-agent`

   ![select agent](./images/select-agent.png)

5. In the **Next node** picker, select **Agent** and select the **Done** button
   \
    ![next node agent](./images/next-node-agent.png)

6. Select the new agent node on the canvas and, in the **Select an agent** picker, select `fault-diagnosis-agent`

   ![select agent 2](./images/select-agent-2.png) 

7. In the **Next node** picker, select **End** and select the **Done** button

    ![end node](./images/end-node.png) 

8. Select **Save** and name it `factory-health-workflow-portal`

![Save agent](./images/save-agent.png) 

### Step 5: Test the workflow in the portal playground

> **Why you should include sensor data in the message**
>
> The agents use a `check_thresholds` tool that reads a local Python file.
> The portal playground **cannot execute Python functions**; if you send a
> generic prompt, the agent will try to call the tool and wait for a result that never
> arrives. Paste the sensor readings directly into the message so the agents
> can work without the tool.

1. On the **factory-health-workflow-portal** workflow screen, select **Preview**

![Preview Agent](./images/preview-agent.png) 

2. Paste the following message (the data is already included, so no tool calls are needed):

   ```
   All sensor readings for today are below — analyse them directly, do not call check_thresholds.

   MX-001 (mixer) — status: warning
     temperature: 92.3°C  [normal 60–90]  ⚠️ ABOVE MAX
     pressure:     3.1 bar [normal 2.0–4.0]
     vibration:    4.8 mm/s [normal 0–4.5]  ⚠️ ABOVE MAX
     rpm:          58 rpm  [normal 40–65]

   EX-002 (extruder) — status: normal
     temperature: 115.0°C [normal 100–130]
     pressure:    12.5 bar [normal 10.0–15.0]
     vibration:    2.1 mm/s [normal 0–3.5]
     rpm:          30 rpm  [normal 20–40]

   CP-003 (curing_press) — status: critical
     temperature: 198.5°C [normal 140–180]  🔴 ABOVE MAX
     pressure:    18.2 bar [normal 12.0–16.0]  🔴 ABOVE MAX
     vibration:    7.3 mm/s [normal 0–3.0]  🔴 ABOVE MAX
     rpm:           0 rpm  [normal 0]

   CU-004 (cooling_unit) — status: normal
     temperature: 35.2°C  [normal 20–45]
     pressure:     1.0 bar [normal 0.8–1.5]
     vibration:    0.8 mm/s [normal 0–2.0]
     rpm:         120 rpm  [normal 80–150]

   IS-005 (inspection_station) — status: warning
     temperature: 28.0°C  [normal 18–30]
     pressure:     1.0 bar [normal 0.8–1.2]
     vibration:    5.2 mm/s [normal 0–4.0]  ⚠️ ABOVE MAX
     rpm:        1800 rpm  [normal 1500–2200]

   Detect all anomalies, then diagnose root causes and recommend remediation for affected machines.
   ```

3. Watch the steps run in sequence: first the anomaly scan, then fault diagnosis
4. Examine the final consolidated report


### Step 6: View run history and traces

1. In the **factory-health-workflow-portal** workflow, select **Traces**

![Workflow Traces](./images/workflow-traces.png) 

2. Select the most recent run to view the timeline, each step, duration, and output


---

## Success Criteria

- [ ] The Python workflow runs end to end: anomaly scan → diagnosis → factory health report
- [ ] Both agents are visible in the Foundry portal as persistent assets
- [ ] The visual workflow was created in the portal and tested in its playground

---

## Beyond the Lab: Production Deployment Options

You built and tested your agents locally. Here is how to take them to production:

### Option 1: Hosted Agents (what you already have)

Your agents created with `agents.create_version()` are already production-ready hosted agents. They remain in Foundry indefinitely; any client can invoke them by name using the Responses API. There is no infrastructure to manage: Foundry handles scaling, versioning, and availability.

- **Versioning**: Each `create_version()` produces an immutable version. Roll back by referencing an earlier version.
- **Multi-tenant**: Multiple users/apps can call the same agent simultaneously.
- **Portal visibility**: Agents appear under Build → Agents with a playground, run history, and tracing.

### Option 2: Foundry Workflows (Visual Orchestration)

What you created in Part 2: connect multiple hosted agents in a DAG using the portal designer. The workflow becomes a deployable agent invoked through the same Responses API.

- Step sequencing with automatic output passing
- `workflow_action` event streaming showing progress
- Run history with time per step

### Option 3: Azure App Service / Container Apps

Wrap your Python workflow in a FastAPI/Flask application for custom middleware, authentication, or business logic:

```python
# Example: FastAPI endpoint that calls your Foundry agents
@app.post("/factory-health-check")
async def health_check():
    report = run_factory_health_workflow(anomaly_agent, diagnosis_agent)
    return report
```

Deploy to **App Service** (managed PaaS) or **Container Apps** (automatically scaling containers).

### Option 4: Azure Functions (Event-Driven)

Trigger agent workflows from events:

- **Timer trigger**: Run the factory health check every hour
- **Service Bus trigger**: Process each anomaly alert as soon as it arrives from IoT Hub
- **HTTP trigger**: On-demand endpoint for maintenance teams

Pay per execution, scaling to zero when idle.

### Option 5: CI/CD Quality Gates

Integrate evaluation into your deployment pipeline:

- Run `evaluate.py` on every PR; block the merge if quality falls below the threshold
- Promote agent versions: `v1-dev` → `v1-staging` → `v1-prod` after evaluation passes
- Blue/green: deploy the new version to 10% of traffic, compare metrics, then promote it

### Summary

| Pattern | Best for |
|---------|----------|
| Hosted agents | Always on, name-based invocation, and no infrastructure management |
| Foundry workflows | No-code multi-agent orchestration |
| App Service / Containers | Custom authentication, middleware, and webhooks |
| Azure Functions | Event-driven, pay-per-use, and IoT integration |
| CI/CD gates | Automated quality assurance before promotion |
