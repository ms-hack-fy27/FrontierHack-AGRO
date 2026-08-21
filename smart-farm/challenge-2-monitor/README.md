# Challenge 2: Monitor

Time: about 20 minutes

## Objectives

Enable GenAI tracing, make a traced agent call, and inspect the resulting conversation in Microsoft Foundry and Application Insights.

## Prerequisites

Verify these values exist in `.env`:

```text
AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

## Run

```powershell
cd smart-farm\challenge-2-monitor
python monitor.py
```

The script loads environment variables first, imports and instruments `AIProjectInstrumentor`, configures Azure Monitor, and only then imports `azure.ai.projects` inside the traced call. It creates a temporary `smart-farm-tracing-agent`, runs one conversation, deletes the conversation and agent, and closes the client.

## Inspect the trace

In Foundry, open Build -> Agents -> `smart-farm-tracing-agent` or the Traces view. In Azure Portal, open the smart farm Application Insights resource and use Transaction search with a recent time range.

Look for the input, model response, duration, token usage, and any errors. A trace is useful for proving which prompt and model call produced a result; it does not by itself prove that the recommendation was correct.

## Success criteria

- [ ] The script completes with tracing enabled.
- [ ] A recent conversation trace is visible.
- [ ] You can identify latency and token information.
- [ ] You can explain how monitoring differs from evaluation.
