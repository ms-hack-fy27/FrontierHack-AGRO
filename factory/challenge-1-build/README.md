# Challenge 1: Build Agents

Time: ~30 minutes

## Objectives

By the end of this challenge, you will have:

- ✅ An **Anomaly Detection Agent** that monitors sensor data and flags abnormal readings
- ✅ A **Fault Diagnosis Agent** that analyzes flagged anomalies and recommends maintenance actions
- ✅ Both agents tested with real factory-floor sensor data

![build](./images/build.png)

## Context

TireForge Industries has 5 machines on the factory floor. Each machine emits sensor data, including temperature, pressure, vibration, and RPM. Your agents need to:

1. **Anomaly Detection**: Compare current readings with known thresholds and flag machines outside specifications
2. **Fault Diagnosis**: Given an anomaly, reason about what may be wrong and recommend an action

See [sensor_data.json](./sensor_data.json) for the current state of all machines.

## Portal or SDK?

Microsoft Foundry offers two ways to build agents. The **Foundry portal** ([ai.azure.com/nextgen](https://ai.azure.com/nextgen)) provides a no-code visual interface where you can create agents, attach tools, and test them interactively in a playground, which is ideal for exploration and rapid prototyping. The **Azure AI Agents SDK** provides full programmatic control: you define agent behavior, tools, and orchestration logic in Python, making versioning, testing, and integration with automated pipelines easier.

![foundry](./images/foundry.png)

In this challenge, we use the **SDK**. The code in [agents.py](./agents.py) creates both agents, registers their tools, and runs them for each machine in `sensor_data.json`, all from the terminal. After the script runs, both agents will also be visible in the portal under **Agents**, where you can inspect them, adjust their instructions, and test them interactively without touching the code.

## Agents and Tools

### What is an agent?

An agent in Microsoft Foundry is a persistent, stateful AI assistant powered by a large language model. Unlike a simple API call, where you send a prompt and receive one response, an agent maintains a **conversation thread**, can **invoke tools autonomously**, and **retains context** across multiple interactions. You configure it with:

- A **name** and a **model** (for example, `gpt-5.4`)
- A **system prompt** — instructions that define its role, personality, and constraints
- One or more **tools** it can call when it needs information or actions beyond its training data

Agents are managed resources in your Foundry project. They persist across runs, appear in the portal under **Agents**, and can be versioned, shared, and reused.

### What are tools?

Tools extend an agent's capabilities beyond language generation. When the model decides it needs information that is not in the context window, it emits a **tool call**, a structured JSON request specifying the tool name and arguments. The SDK intercepts the call, executes the corresponding Python function, and returns the result to the model. This reasoning cycle continues until the agent produces a final response.

From the model's perspective, tools are described by a **JSON schema** (name, description, and parameters). The model reads these descriptions and autonomously decides when and how to call them; you never encode the decision logic directly.

### What tools can you add?

| Tool type | What it does | Best for |
|-----------|-------------|----------|
| **Function** | Calls a local Python function you define | Any custom logic: database queries, APIs, and calculations |
| **Code Interpreter** | Lets the agent write and execute Python in a sandbox | Data analysis, chart generation, and file processing |
| **File Search** | Performs semantic search over a Microsoft Foundry knowledge base | Policy documents, manuals, and historical records |
| **Bing Search** | Searches the web in real time | Real-time information and news |
| **Azure AI Search** | Queries an Azure Search index | Grounded retrieval from your data at scale |

#### Vector databases and Microsoft Foundry knowledge bases

When your agent needs to answer questions grounded in a large collection of documents, such as policy manuals, product specifications, and historical records, you need a **vector database**. Unlike keyword search, a vector database converts text into numerical embeddings and finds semantically similar passages at query time. This lets the agent ask a natural-language question and retrieve the right content even when the exact words do not appear in the query.

**Microsoft Foundry** includes a built-in knowledge base backed by vector storage. You upload documents (PDFs, Word files, and plain text), and the service chunks them, generates embeddings, and builds the index automatically. When you attach this knowledge base to an agent as a **File Search** tool, the agent queries it during inference and brings relevant passages into context before generating a response. This grounds answers in your actual documents rather than only the model's training data.

For TireForge Industries, useful knowledge bases might include:

- **Machine maintenance manuals** — repair procedures, lubrication schedules, torque specifications, and replacement part numbers for each machine
- **Historical incident reports** — previous faults, their root causes, and the corrective actions that resolved them
- **Vendor specification sheets** — acceptable operating tolerances, warranty conditions, and recommended sensor limits by machine model

With this in place, the **Fault Diagnosis Agent** could ask, “what are the known failure modes for the CP-003 curing press when vibration exceeds 9.0 mm/s?” and retrieve relevant maintenance history, grounding its recommendation in documented precedents rather than the LLM's general knowledge.

In this challenge, the agents use **function tools**. The **Anomaly Detection Agent** uses `check_thresholds` to look up each machine's acceptable operating ranges and compare them with live sensor readings. Without this tool, the agent would have to reason from memory alone; with it, every threshold check is grounded in real machine specification data.

## Start Here

Open [agents.py](./agents.py) and examine the implementation of both agents.

```bash
cd factory/challenge-1-build
python agents.py
```

While the script runs, watch the terminal: you will see each agent being created, followed by each machine from `sensor_data.json` passing first through the **Anomaly Detection Agent**, with its output forwarded to the **Fault Diagnosis Agent**. The agents' raw responses will be printed for each machine, giving you a live view of how the two agents collaborate. When it finishes, open the [Microsoft Foundry portal](https://ai.azure.com/nextgen), open your project, and navigate to **Agents** in the left sidebar. Select **Refresh** if the agents do not appear immediately; newly created agents may take a few seconds to show up in the portal.

## Success Criteria

- [ ] The Anomaly Detection Agent correctly identifies the 2 warning machines and the 1 critical machine
- [ ] The Fault Diagnosis Agent provides reasonable maintenance recommendations
- [ ] Both agents respond coherently when given a machine's sensor readings
