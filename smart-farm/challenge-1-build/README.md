# Challenge 1: Build agents

Time: ~30 minutes

## Objectives

By the end of this challenge, you will have:

- ✅ **Classification Agent** that analyzes call summaries and categorizes customer intent
- ✅ **Advisor Agent** that recommends optimal service strategies
- ✅ Both agents tested with real call center data

![build](./images/build.png)

## Context

NovaTel Communications receives hundreds of calls every day. Each call has a summary, the customer's history, and account context. Your agents need to:

1. **Classification**: analyze the call to determine what the customer needs (billing dispute, technical issue, cancellation risk, upsell opportunity, etc.)
2. **Advisory**: given a classified intent and the customer's context, recommend the best resolution path with scripts, routing decisions, and available offers

See [call_data.json](./call_data.json) for today's incoming calls.

## Portal or SDK?

Microsoft Foundry offers two ways to build agents. The **Foundry portal** ([ai.azure.com/nextgen](https://ai.azure.com/nextgen)) provides a visual, no-code interface where you can create agents, attach tools, and test them interactively in a playground — ideal for exploration and rapid prototyping. The **Azure AI Agents SDK** provides full programmatic control: you define agent behavior, tools, and orchestration logic in Python, making versioning, testing, and integration with automated pipelines easier.

![foundry](./images/foundry.png)

In this challenge, we use the **SDK**. The code in [agents.py](./agents.py) creates both agents, registers their tools, and runs them against each call in `call_data.json` — all from the terminal. After the script runs, both agents will also be visible in the portal under **Agents**, where you can inspect them, tune their instructions, and test them interactively without changing code.

## Agents and tools

### What is an agent?

An agent in Microsoft Foundry is a persistent, stateful AI assistant powered by a large language model. Unlike a simple API call — where you send a prompt and receive a single response — an agent maintains a **conversation thread**, can **invoke tools autonomously**, and **maintains context** across multiple interactions. You configure it with:

- A **name** and a **model** (for example, `gpt-5.4`)
- A **system prompt** — instructions that define its role, personality, and constraints
- One or more **tools** that it can call when it needs information or actions beyond its training data

Agents are managed resources in your Foundry project. They persist across runs, appear in the portal under **Agents**, and can be versioned, shared, and reused.

### What are tools?

Tools extend an agent's capabilities beyond language generation. When the model decides it needs information that is not in the context window, it emits a **tool call** — a structured JSON request specifying the tool name and its arguments. The SDK intercepts the request, executes the corresponding Python function, and returns the result to the model. This reasoning cycle continues until the agent produces a final response.

From the model's perspective, tools are described by a **JSON schema** (name, description, and parameters). The model reads these descriptions and autonomously decides when and how to call them — you never code the decision logic directly.

### Which tools can you add?

| Tool type | What it does | Best for |
|-----------|-------------|----------|
| **OpenAPI** | Calls a local Python function that you define | Any custom logic: database queries, APIs, and calculations |
| **Code Interpreter** | Lets the agent write and execute Python in a sandbox | Data analysis, chart generation, and file processing |
| **File Search** | Performs semantic search over a Microsoft Foundry knowledge base | Policy documents, manuals, and historical records |
| **Bing Search** | Searches the web in real time | Real-time information and news |
| **Azure AI Search** | Queries an Azure Search index | Grounded retrieval from your own data at scale |

#### Microsoft Foundry vector databases and knowledge bases

When your agent needs to answer questions grounded in a large collection of documents — policy manuals, product specifications, and historical records — you need a **vector database**. Unlike keyword search, a vector database converts text into numeric embeddings and finds semantically similar passages at query time. This lets the agent ask a natural-language question and retrieve the right content even when the exact words do not appear in the query.

**Microsoft Foundry** includes a built-in knowledge base backed by vector storage. You upload documents (PDFs, Word files, and plain text), and the service chunks them, generates embeddings, and builds the index automatically. When you attach this knowledge base to an agent as a **File Search** tool, the agent queries it during inference — bringing relevant passages into context before generating a response so its answers are grounded in your actual documents, not just the model's training data.

For the NovaTel call center, useful knowledge bases could include:

- **Customer service policy manual** — refund limits, routing rules, and retention-offer eligibility by plan tier
- **Product and plan documentation** — features by tier, billing cycles, device return windows, and roaming policies
- **Resolution scripts** — approved language for billing disputes, cancellation retention, and upsell conversations

With these resources, the **Resolution Advisor Agent** could answer “which retention offers apply to a Premium customer with more than 3 years of tenure who wants to cancel?” and retrieve the exact offer details from the manual — instead of inventing plausible but potentially incorrect policies.

In this challenge, the agents use **function tools**. The **Intent Classification Agent** uses `lookup_customer` to retrieve account history and customer tier before determining intent. Without this tool, the agent would have to guess based only on the call summary — with it, every classification is grounded in real account data.

## Get started

Open [agents.py](./agents.py) and review the implementation of both agents.


## Objectives

Create a tool-grounded `smart-farm-classifier-agent` and a tool-free `smart-farm-advisor-agent`. Run them against five realistic crop zones and inspect the structured status output.

## Data and tool

Open `smart_farm_data.json`. It contains exactly five zones and four metrics per zone: `soil_moisture`, `temperature`, `humidity`, and `ph_level`. Every metric has `min` and `max` thresholds. The snapshot has two warnings, one critical zone, and two normal zones.

`check_health_monitor(zone_id)` reads this file and returns JSON with every metric, its threshold, an inclusive range result, and an anomaly deviation. The monitor agent must call this tool for each requested zone.

## Agent responsibilities

- `smart-farm-classifier-agent` uses the function tool and reports zone ID, crop, status, all metrics, anomalies, and a next step.
- `smart-farm-advisor-agent` has no tools. It reasons from the monitor output using irrigation-stress, fungal/disease-risk, and urgent-escalation patterns.

## Run

```powershell
cd smart-farm\challenge-1-build
python agents.py
```

The script creates both hosted agent versions, checks all five zones, forwards the monitor output to the advisor, and deletes the temporary versions and conversations when it exits.

## Smart Farm data via API

The source dataset is `api-agro/data/smart_farm_data.json`. It contains a snapshot of five zones with crop details, inspection dates, observed issues, and these readings:

- `soil_moisture`
- `temperature`
- `humidity`
- `ph_level`
- `issues`

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

## TODO: CONFIG AGENTS - MANUALLY ON FOUNDRY

## Success criteria

- [ ] The tool returns threshold analysis for all four metrics.
- [ ] The monitor identifies two warning, one critical, and two normal zones.
- [ ] The advisor recommends irrigation action for irrigation stress.
- [ ] The advisor recommends fungal or disease investigation for high humidity plus low pH.
- [ ] Multiple critical readings produce urgent agronomist escalation.
