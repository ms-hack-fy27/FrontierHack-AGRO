# Challenge 4: Production workflow

Time: ~20 minutes

Create a multi-agent orchestration workflow for NovaTel Communications and take it to production.

## Scenario

The individual agents you created in Challenge 1 are valuable — but in production, agents need to work
**together** as an automated pipeline. In this challenge, you will connect the two agents into a complete
call center triage workflow, run the workflow from code, and then create and test it visually in the Foundry portal.

![deploy](./images/deploy.png)

## Learning objectives

- Deploy persistent production agents (create once and reuse indefinitely)
- Orchestrate multiple agents step by step in a Python workflow
- Visually create the same workflow in the Foundry portal
- Invoke the portal workflow from Python with live streaming
- View run history and traces in the portal

## The workflow

```
ensure_agents_deployed()
        |
        v
run_intent_classification()     <-- Intent Agent classifies all 7 calls
        |
        v (for each high-priority call)
run_resolution_advisory()       <-- Resolution Agent recommends actions
        |
        v
print_shift_report()            <-- Consolidated Shift Report
```

---

## Part 1 — SDK: create and run the Python workflow

### Step 1: Review the implementation

Open [deploy.py](./deploy.py) and review:

- **`ensure_agents_deployed()`** — lists existing agents and creates `call-center-intent-classifier-agent` and `call-center-advisor-agent` if they are not present
- **`run_intent_classification()`** — calls the intent agent and handles the `lookup_customer` function-call loop
- **`run_resolution_advisory()`** — calls the resolution agent for each high-priority call
- **`run_call_center_workflow()`** — orchestrates all steps and returns the consolidated report

### Step 2: Run the workflow

```bash
cd callcenter/challenge-4-deploy
python deploy.py
```

Expected output:
```
=== Step 1: Ensure Agents Are Deployed ===
  Found existing: call-center-intent-classifier-agent
  Found existing: call-center-advisor-agent

=== Step 2a: Intent Classification ===
  CALL-001: billing_dispute (HIGH) — frustrated, retention risk HIGH
  CALL-002: technical_issue (HIGH) — frustrated, retention risk MEDIUM
  CALL-003: cancellation (HIGH) — neutral, retention risk HIGH
  CALL-004: upsell_opportunity (MEDIUM) — positive, retention risk LOW
  CALL-005: account_support (LOW) — frustrated, retention risk LOW
  CALL-006: billing_dispute (HIGH) — frustrated, retention risk MEDIUM
  CALL-007: security_concern (CRITICAL) — anxious, retention risk MEDIUM

=== Step 2b: Resolution Advisory (High-Priority Calls) ===
  Resolving CALL-007 (security_concern)...
  Resolving CALL-001 (billing_dispute)...
  Resolving CALL-003 (cancellation)...

NOVATEL CALL CENTER — SHIFT REPORT
  Total calls processed  : 7
  Critical priority      : 1
  High priority          : 2
  ...
```

---

## Part 2 — Portal: create and test the visual workflow

### Step 3: Verify that the agents are deployed in the portal

1. Open the [Microsoft Foundry portal](https://ai.azure.com/nextgen)
2. Select your project
3. Select **Build** → **Agents** in the top bar
4. Confirm that both agents appear:
   - `call-center-intent-classifier-agent`
   - `call-center-advisor-agent`


### Step 4: Create the workflow in the portal designer

1. Select **Build** → **Agents** → **Workflows**
2. Notice that the workflow created using the SDK in Part 1 is listed. Create a new workflow by selecting **Create** → **Blank workflow**

![Create workflow](./images/create-workflow.png)

3. In the visual designer, in the **Add a workflow node** dialog, choose **Agent**

   ![add agent](./images/add-agent.png)

4. In the **Select an agent** selector, select `call-center-intent-classifier-agent`

   ![select agent](./images/select-agent.png)

5. In the **Next node** selector, select **Agent** and click the **Done** button
   \
    ![next node agent](./images/next-node-agent.png)

6. Select the new agent node on the canvas and, in the **Select and agent** selector, select `call-center-advisor-agent`

   ![select agent 2](./images/select-agent-2.png) 

7. In the **Next node** selector, select **End** and click the **Done** button

    ![end node](./images/end-node.png) 

8. Select **Save** and name it `callcenter-triage-workflow-portal`

![Save agent](./images/save-agent.png) 

### Step 5: Test the workflow in the portal playground

> **Why you need to include the call data in the message**
>
> The agents use a `lookup_customer` tool that reads data from a local Python file.
> The portal playground **cannot execute Python functions** — if you send a
> generic prompt, the agent will try to call the tool and remain stuck waiting for a result that
> never arrives. Paste the call data directly into the message so the agents can
> work without the tool.

1. Open **callcenter-triage-workflow-portal** → **Preview**

![Preview Agent](./images/preview-agent.png) 

2. Paste the following message (the data is already embedded, so no tool calls are needed):

   ```
   All call data for today is below — analyse it directly, do not call lookup_customer.

   CALL-001 | Maria Gonzalez | premium | 36 months
   Unexpected $47.99 charge for sports add-on she never subscribed to. Wants refund, threatening to cancel.

   CALL-002 | James Liu | basic | 4 months
   Internet dropping every 20-30 minutes since yesterday. Works from home, presentation tomorrow. 1 open ticket.

   CALL-003 | Priya Sharma | premium | 18 months
   Moving to city without NovaTel coverage, wants to cancel. Asking about ETF and final bill.

   CALL-004 | Robert Chen | business | 24 months
   Wants to expand from 5 to 12 lines for new hires. Asking about bulk pricing and number porting.

   CALL-005 | Sarah Mitchell | basic | 60 months
   Confused by new app UI — cannot find billing or data usage pages. 2 open tickets.

   CALL-006 | David Park | premium | 12 months
   Charged $899 for a device returned 3 weeks ago (has FedEx proof of delivery). 1 open ticket.

   CALL-007 | Emma Wilson | basic | 8 months
   Suspected account breach — unsolicited SMS verification codes, unfamiliar device on account.

   Classify each call by intent, priority, sentiment, and retention risk.
   Then recommend resolution strategies for high-priority and security calls.
   ```

3. Watch the steps run in sequence — classification first, followed by resolution advisory
4. Review the final consolidated report

### Step 6: View run history and traces

1. In the **callcenter-triage-workflow-portal** workflow, click **Traces**

![Workflow Traces](./images/workflow-traces.png) 

2. Click the most recent run to view the timeline — each step, duration, and output

---

## Success criteria

- [ ] The Python workflow runs end to end: classification → resolution → shift report
- [ ] Both agents are visible in the Foundry portal as persistent assets
- [ ] The visual workflow was created in the portal and tested in its playground

---

## Beyond the lab: production deployment options

You created and tested your agents locally. Here is how to take them to production:

### Option 1: Hosted agents (what you already have)

Your agents created with `agents.create_version()` are already production-ready hosted agents. They remain in Foundry indefinitely — any client can invoke them by name using the Responses API. There is no infrastructure to manage; Foundry handles scaling, versioning, and availability.

- **Versioning**: Each `create_version()` produces an immutable version. Roll back by referencing an earlier version.
- **Multi-tenant**: Multiple users/applications can call the same agent simultaneously.
- **Portal visibility**: agents appear under Build → Agents with a playground, run history, and tracing.

### Option 2: Foundry workflows (visual orchestration)

What you created in Part 2 — connect multiple hosted agents in a DAG using the portal designer. The workflow becomes a deployable agent, invoked through the same Responses API.

- Step sequencing with automatic output passing
- `workflow_action` event streaming showing progress
- Run history with time per step

### Option 3: Azure App Service / Container Apps

Wrap your Python workflow in a FastAPI/Flask application for custom middleware, authentication, or business logic:

```python
# Example: FastAPI endpoint that calls your Foundry agents
@app.post("/triage-calls")
async def triage_calls():
    report = run_call_center_workflow(intent_agent, resolution_agent)
    return report
```

Deploy to **App Service** (managed PaaS) or **Container Apps** (containers with automatic scaling).

### Option 4: Azure Functions (event-driven)

Trigger agent workflows from events:

- **Service Bus trigger**: classify and resolve each call when it enters the queue
- **Timer trigger**: generate shift reports every hour during business hours
- **HTTP trigger**: on-demand endpoint for supervisors to request triage updates

Pay per execution, with scale-to-zero when idle.

### Option 5: CI/CD quality gates

Integrate evaluation into your deployment pipeline:

- Run `evaluate.py` on every PR — block the merge if quality falls below the threshold
- Promote agent versions: `v1-dev` → `v1-staging` → `v1-prod` after evaluation passes
- Blue/green: deploy the new version to 10% of traffic, compare metrics, and then promote it

### Summary

| Pattern | Best for |
|---------|----------|
| Hosted agents | Always-on agents, name-based invocation, and no infrastructure management |
| Foundry workflows | No-code multi-agent orchestration |
| App Service / Containers | Custom authentication, middleware, and webhooks |
| Azure Functions | Event-driven, pay-per-use, and queue processing |
| CI/CD gates | Automated quality assurance before promotion |
