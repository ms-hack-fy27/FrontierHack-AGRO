# Challenge 5: Interactive Multi-Agent Orchestration

Estimated time: ~20 minutes

## Objectives

Run a simple two-agent orchestration using the latest version of the **Microsoft Agent Framework** in Python (`azure-ai-projects`).

1. Request a prompt from the user interactively.
2. Send the prompt to **Agent 1** (`smart-farm-classifier-agent`), which checks crop metrics through the `check_health_monitor` tool.
3. Pass Agent 1's response context directly to **Agent 2** (`smart-farm-advisor-agent`), which analyzes the data and generates an agronomic assessment.
4. Display each transition step and the advisor's final response graphically in the terminal.

---

## Orchestration Flow

```text
 ┌───────────────────────────────────┐
 │        👤  USER (PROMPT)           │
 └─────────────────┬─────────────────┘
                   │
                   │  1. User Prompt
                   ▼
 ┌───────────────────────────────────┐
 │  🤖 AGENT 1: HEALTH MONITOR       │
 │   (smart-farm-classifier-agent)      │
 └─────────────────┬─────────────────┘
                   │
                   │  2. Analysis Context / Anomalies
                   ▼
 ┌───────────────────────────────────┐
 │  🤖 AGENT 2: AGRONOMIC ADVISOR    │
 │   (smart-farm-advisor-agent)      │
 └─────────────────┬─────────────────┘
                   │
                   │  3. Diagnosis and Final Assessment
                   ▼
 ┌───────────────────────────────────┐
 │      📄 FINAL RESPONSE DISPLAYED  │
 └───────────────────────────────────┘
```

---

## How to Run

Open a terminal in the challenge directory and run the Python script:

```powershell
cd smart-farm\challenge-5
python orchestrate.py
```

### What the script does:

1. **Verifies that the agents exist**: Connects to Azure AI Projects / Microsoft Foundry and reuses the agents `smart-farm-classifier-agent` and `smart-farm-advisor-agent`. If either agent is missing, the script raises an error and does not create it.
2. **Collects a prompt**: Interactively asks which query you want to run for the farm.
3. **Runs Agent 1**: Sends the prompt to the Health Monitor, which invokes `check_health_monitor` and generates the analysis report.
4. **Passes context**: Takes Agent 1's output and sends it as context to Agent 2 (the Agronomic Advisor).
5. **Provides a graphical view**: Displays terminal banners showing the message transition from User -> Agent 1 -> Agent 2 -> Final Response.

---

## Success Criteria

- [ ] The Python script runs without errors on the latest version of the Agentic Framework (`azure-ai-projects`).
- [ ] The user's prompt is captured through the CLI.
- [ ] Agent 1 (`smart-farm-classifier-agent`) processes the request and runs the monitoring tool.
- [ ] Agent 1's response is passed as context to Agent 2 (`smart-farm-advisor-agent`).
- [ ] The interface visually displays the message handoff and Agent 2's final response in the terminal.
