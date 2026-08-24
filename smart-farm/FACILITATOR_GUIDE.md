# Facilitator Guide: GreenRise Smart Farm

## Audience and objective

This two-hour lab introduces a practical agent workflow for crop monitoring. Participants leave with two Foundry agents, application telemetry, an evaluation baseline, and a multi-agent workflow.

By the end, participants can explain how a function tool grounds threshold decisions, how traces expose agent behavior, how evaluation differs from monitoring, and how a portal workflow can pass embedded context between agents.

## Timing plan

| Time | Activity | Facilitator focus |
|---|---|---|
| 0:00-0:10 | Welcome and scenario | Explain the five zones and the intentional 2 warning / 1 critical / 2 normal mix. |
| 0:10-0:30 | Challenge 0: Setup | Confirm permissions, model deployment, and `.env` creation. |
| 0:30-1:00 | Challenge 1: Build | Pause after tool registration and again after the first critical result. |
| 1:00-1:20 | Challenge 2: Monitor | Show one trace and connect tool calls, tokens, and latency. |
| 1:20-1:50 | Challenge 3: Evaluate | Compare aggregate scores with individual rows. |
| 1:50-2:10 | Challenge 4: Workflow | Run the Python workflow, then show the portal workflow limitation. |
| 2:10-2:15 | Wrap-up | Collect one improvement idea per group. |

The schedule includes roughly 10 minutes of buffer for Azure provisioning and portal propagation.

## Objectives by challenge

- **Setup:** provision `smart-farm-project`, deploy `gpt-5.4`, and connect Application Insights.
- **Build:** use `check_health_monitor` as a deterministic grounding tool; create the monitor and advisor agents.
- **Monitor:** enable GenAI instrumentation before importing `azure.ai.projects`; find a conversation trace.
- **Evaluate:** upload the 10-line JSONL dataset and interpret coherence and fluency results.
- **Workflow:** run monitor -> advisor -> report in Python and create a `WorkflowAgentDefinition` asset.

## Reconvene points and answer cues

### After setup
Ask: "What is the difference between the project connection string and the model deployment name?" Cue: the connection string selects the Foundry project; the deployment name selects the model used by the agent.

### After the first tool call
Ask: "Why should the model call the tool instead of trusting the status field?" Cue: the tool computes the comparison from current values and thresholds, making the explanation auditable and reducing invented readings.

### After monitoring
Ask: "What can a trace tell us that a final answer cannot?" Cue: it shows the request, model turn, tool call, tool output, latency, and token usage.

### During evaluation
Ask: "Can a fast, error-free agent still be wrong?" Cue: yes. Monitoring measures operation; evaluation compares response quality with expected behavior.

### During workflow
Ask: "Why is the portal input embedded?" Cue: a visual workflow step cannot run the local Python function-call loop, so the data must be present in the message.

## Expected domain reasoning

- ZONE-ALPHA has low soil moisture and high temperature: irrigation stress is plausible.
- ZONE-GAMMA has four out-of-range metrics, including high humidity and low pH: treat as critical, escalate urgently, and investigate fungal or disease risk.
- ZONE-EPSILON has high humidity and low pH: increase airflow and investigate fungal or disease risk.
- Multiple critical readings should trigger urgent agronomist escalation, not routine monitoring.

## Common errors and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| `PROJECT_CONNECTION_STRING` is missing | Setup was not provisioned or the wrong directory is active | Run `azd provision` from `smart-farm`, then verify `.env`. |
| Permission error creating an agent | Missing Foundry data-plane role | Ask an administrator for the required Foundry project role. |
| Monitor script says tracing is disabled | Environment variables loaded too late or are missing | Set both tracing variables in `.env`; rerun from the lab directory. |
| Evaluation upload is disabled | Dataset name was not entered first | Enter a dataset name, then upload `eval_portal.jsonl`. |
| Tool Call Accuracy scores poorly in portal evaluation | Portal evaluation cannot execute the local function | Remove Tool Call Accuracy; keep Coherence and Fluency. |
| Portal workflow waits on a tool call | Local function execution is unavailable in workflow steps | Use the embedded-data input demonstrated in Challenge 4. |
| Agents are not visible immediately | Foundry portal propagation delay | Refresh the Agents page after a short wait. |

## Completion check

Ask each participant to show: the two agent names in Foundry, one trace containing a model response, the evaluation run with 10 rows, and the workflow output showing the critical strawberry zone.
