# Challenge 2: Monitor with Application Insights

Time: ~20 minutes

## Objectives

By the end of this challenge, you will have:

- ✅ GenAI tracing enabled for your Foundry agents
- ✅ Agent interactions visible as traces in Application Insights
- ✅ An understanding of how to debug agent behavior in production

![monitor](./images/monitor.png)

## Context

Your agents work — but how do you know whether they are working **well**? What if an agent incorrectly classifies a security concern as a billing dispute? What if resolution recommendations take too long to generate during peak hours?

**Application Insights** with **GenAI tracing** provides:

- A complete trace of every agent interaction (user message → model call → tool calls → response)
- Token usage per request
- Latency breakdown (network, model inference, and tool execution)
- Error tracking and alerts

## Why monitor?

AI agents behave differently from traditional software. A conventional API returns the correct data or throws an error — you can test it deterministically. An agent's output is probabilistic: the same input can produce subtly different responses on each run, tool calls can succeed and still return unexpected data, and failures can be silent (the agent responds confidently but incorrectly). Without observability, these problems remain invisible until a user reports them.

Monitoring serves three critical functions for AI agents:

- **Reliability** — Detect when agents stop working (failed tool calls, timeouts, and empty responses) before users do
- **Performance** — Track latency and token usage over time, detect regressions when updating a system prompt, and size deployments correctly for cost efficiency
- **Debugging** — When something goes wrong, distributed traces provide a complete record of the model's reasoning, the tools called, what they returned, and exactly where the chain stopped

For AI systems in production, monitoring is the foundation that makes improvement possible. You cannot fix what you cannot see.

Specifically for the NovaTel call center: a security concern classified incorrectly (CALL-007) and routed to the billing queue means a compromised account could go unattended for hours. A latency spike during the morning rush means agents may not keep up with the call queue. Without traces, you would never know which tool call or model reasoning step caused the problem — or even that it occurred.

## Portal or SDK?

Microsoft Foundry offers two ways to monitor agents. The **Foundry portal** ([ai.azure.com/nextgen](https://ai.azure.com/nextgen)) has an integrated **Tracing** view where you can browse agent interactions, inspect individual spans, and view token usage and latency — without writing code. **Application Insights** (through the Azure portal) provides deeper analysis: Kusto queries, custom dashboards, and alert rules.

In this challenge, we use the **SDK** — `monitor.py` instruments your agents so every interaction is automatically captured as a distributed trace. After the script runs, you will explore these traces using both portal options and see how each presents the same data differently.

## Prerequisites

Make sure your `.env` contains:
```
AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;...
```

## Connect Application Insights to the portal

The deployment script automatically links Application Insights to your Foundry project. To confirm it worked, open the [Microsoft Foundry portal](https://ai.azure.com/nextgen), navigate to your project, and click **Tracing** in the left sidebar — you should see the Application Insights resource already connected.

If you see a **"Create or connect an App Insights resource to get started"** banner, automatic connection was blocked by a tenant policy. Fix it with one click: click **Connect**, select the `foundry-hack-insights-<suffix>` resource from the dropdown, and confirm. You only need to do this once.

## Get started

Open [monitor.py](./monitor.py) and review the tracing configuration.

```bash
cd callcenter/challenge-2-monitor
python monitor.py
```

When the script finishes, your traces will be active. Explore them in the Azure portal.

---

### Step 1: Microsoft Foundry portal

1. Open the [Microsoft Foundry Portal](https://ai.azure.com/nextgen) → open your project
2. Click `resolution-advisor-agent` -> **Traces**

   - **Traces panel** — The **Conversations** tab lists each agent run as a row, showing the conversation ID, trace ID, response ID, status, creation time, duration, input/output tokens, estimated cost, evaluation results, and agent version. Use the search box and **Status**, **Duration**, **Tokens**, and **Estimated Cost** filters (along with the date-range selector) to narrow the results, switch to the **Responses** tab to view individual model responses, or click **Create dataset** to turn these traces into an evaluation dataset.

   ![traces](./images/traces.png)

3. You will see a list of recent traces — click any row to open it

   ![traces2](./images/traces2.png)

4. Within a trace, you can see:
   - Each **agent turn** as a span (input → output)
   - **Tool calls** (`lookup_customer`, etc.) as child spans with inputs/outputs
   - **Token usage** and **latency** per span
   - The model's full prompt and completion when `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true`
5. Use the **timeline view** to find slow spans and the **details panel** to inspect individual messages
6. Click `resolution-advisor-agent` -> **Monitor**

   - **Monitor panel** — The **Overview** tab provides a quick health summary with **Operational metrics** (estimated cost and total token usage), **Evaluations**, **Scheduled evaluations**, and **Scheduled red teaming run issues** cards. Below, the **Operational metrics** charts show **Agent runs** (how often the agent was called) and **Runs and token metrics** (calls versus tokens consumed) for the selected range. Use the **Tools** tab, date filters, **Settings**, or **Open in Azure Monitor** for deeper analysis.

   ![monitor2](./images/monitor2.png)

### Step 2 - Application Insights

1. Open [portal.azure.com](https://portal.azure.com) → search for **Application Insights** → open `foundry-hack-insights-<suffix>`
2. Left sidebar → **Investigate** → **Search**

![Application Insights Search](./images/screen22.png)

3. Set the time range to **Last 30 minutes** and click **Search** — you will see individual trace events
4. Look for traces where your agents were invoked.
   You can inspect the timestamp, operation ID, and message payload to confirm that the calls reached the model.
5. Click the `Resolution Advisor Agent` instance.
You will see the **end-to-end transaction trace**, showing:
   - The complete agent conversation (user input with call summaries → agent response with resolution recommendations)
   - Nested spans for each model call with a latency breakdown (for example, `gpt-5.4-2026-03-05` taking 5.1 seconds)
   - The exact system prompt and generated reasoning the agent used to reach its conclusion
   - Resource details (AKS cluster and region) where the agent ran
   - Any content-filter blocks that violated Responsible AI standards
   - This view lets you inspect exactly what the agent "saw" and "reasoned about" to understand incorrect classifications or performance issues
6. In the left sidebar → **Investigate** → **Agents (preview)** to open the agent-focused operational dashboard.
![alt text](./images/agentspane.png)
    - Use the **Time range** and **Agent** filters at the top to narrow the view, switch between the **Dashboard** and **All agents** tabs, or click **Explore in Grafana** for deeper analysis.
    - **Agent operational metrics**:
       - **Agent Runs** — total invocations broken down by agent (for example, `resolution-advisor-agent`, `intent-classification-agent`). Click **View Traces with Agent Runs** to access the underlying traces.
       - **Gen AI Errors** — shows traces with GenAI errors in the selected window; a green check means none were found.
       - **Tool Calls** — a table of each tool (for example, `multi_tool_use.parallel`) with its error count, average duration, and number of calls, so you can identify slow or failing tools.
       - **Models** — a breakdown by model (for example, `gpt-5.4-2026-03-05`, `gpt-5.4`) showing errors, average duration, and call count.
    - **Token consumption**:
       - **Token Consumption by Model** — total tokens consumed by model (for example, ~22.1K for `gpt-5.4-2026-03-05`).
       - **Input vs Output Tokens** — total input versus output tokens over time (for example, 17K input versus 5.1K output), useful for tracking cost drivers.

---

## Success criteria

- [ ] GenAI tracing is enabled and `monitor.py` ran successfully
- [ ] You can browse agent traces in the Foundry portal's **Traces** view and open a conversation
- [ ] You can read the **Monitor** panel (agent runs, token usage, and estimated cost)
- [ ] You can see at least one agent trace in Application Insights and open its end-to-end transaction trace
- [ ] You can use the **Agents (preview)** dashboard to view agent runs, tool calls, models, and token consumption
- [ ] You understand where to look when an agent behaves poorly
