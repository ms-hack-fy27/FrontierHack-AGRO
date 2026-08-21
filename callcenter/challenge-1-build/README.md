# Challenge 1: Build agents

Time: ~30 minutes

## Objectives

By the end of this challenge, you will have:

- ✅ An **Intent Classification Agent** that analyzes call summaries and categorizes customer intent
- ✅ A **Resolution Advisor Agent** that recommends optimal service strategies
- ✅ Both agents tested with real call center data

![build](./images/build.png)

## Context

NovaTel Communications receives hundreds of calls every day. Each call has a summary, the customer's history, and account context. Your agents need to:

1. **Intent classification**: analyze the call to determine what the customer needs (billing dispute, technical issue, cancellation risk, upsell opportunity, etc.)
2. **Resolution advisory**: given a classified intent and the customer's context, recommend the best resolution path with scripts, routing decisions, and available offers

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
| **Function** | Calls a local Python function that you define | Any custom logic: database queries, APIs, and calculations |
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

```bash
cd callcenter/challenge-1-build
python agents.py
```

While the script runs, watch the terminal closely — you will see each agent being created, followed by each call from `call_data.json` passing first through the **Intent Classification Agent**, with its output forwarded to the **Resolution Advisor Agent**. The agents' raw responses will be displayed for each call, giving you a live view of how they collaborate. When it finishes, open the [Microsoft Foundry portal](https://ai.azure.com/nextgen), open your project, and navigate to **Agents** in the left sidebar — click **Refresh** if the agents do not appear immediately, as new agents may take a few seconds to show up in the portal.


## Success criteria

- [ ] The Intent Classification Agent correctly identifies the 6 intent types across the 7 calls
- [ ] The Resolution Advisor provides actionable recommendations with scripts and routing decisions
- [ ] Security concerns are always routed appropriately; billing disputes offer suitable credits
