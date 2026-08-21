# Challenge 3: Evaluate

Time: ~30 minutes

## Objectives

By the end of this challenge, you will have:

- ✅ Run a systematic evaluation of your agents with a test dataset
- ✅ Use built-in evaluators (coherence and fluency) to measure quality
- ✅ Interpret evaluation metrics and identify areas for improvement
- ✅ Understand how to integrate evaluations into a CI/CD pipeline

![evaluate](./images/evaluate.png)

## Context

Monitoring tells you **what is happening** (latency, errors, and token usage). Evaluation tells you **whether classifications are actually correct**.

You have a dataset with 10 test cases — each with a call scenario and the expected correct classification (intent, priority, sentiment, and recommended action). You will run your agents against these test cases and measure performance using LLM-as-judge scoring.

## Why evaluate?

Monitoring tells you that your agents are *running* — evaluation tells you whether they are doing the *right thing*. These are fundamentally different questions.

Monitoring captures **operational signals**: latency, token count, error rates, and availability. These tell you *how* the system behaves mechanically. Evaluation captures **quality signals**: are the agent outputs correct, relevant, coherent, and consistent with the expected results? These tell you *whether* the system is actually fulfilling its purpose.

Without systematic evaluation, you rely on spot checks — reading a few responses and judging them subjectively. This does not scale, is not repeatable, and does not detect regressions when you update a prompt or switch models. Evaluation provides a measurable baseline: a score that can be tracked over time and compared across versions.

Evaluation also reveals problems that monitoring cannot detect. An agent that always responds quickly and without errors, but classifies intents incorrectly or provides scripted resolutions that do not match the customer's actual situation, looks perfectly healthy to monitoring. Evaluation catches this immediately.

For AI in production, evaluations should run:

- **Before deployment** — establish a quality baseline and gate versions with minimum scores
- **After any change** — to system prompts, models, tools, or retrieval data
- **On a schedule** — detect drift as the underlying model is updated or call patterns change

Specifically for the NovaTel call center: an agent that classifies CALL-007 (suspected account breach) as a billing dispute is dangerous — this is a security incident that must be routed immediately. Monitoring sees a successful, low-latency response. Only evaluation — comparing the output with the expected classification — detects the error.

## The evaluation dataset

The dataset is at [challenge-4-deploy/evaluation_dataset.json](../challenge-4-deploy/evaluation_dataset.json) — it contains:

- 10 call scenarios covering the 6 intent types
- Each has an `input` (the call summary sent to the agent)
- Each has an `expected_output` (the correct classification and action)

## About the evaluators

Microsoft Foundry uses an **LLM-as-judge** approach — a separate model reads each agent response along with the input and reference truth, then assigns a score from 1 to 5. You will use two built-in evaluators:

- **Coherence** — measures whether the agent response is logically structured and internally consistent. A score of 5 means the output is clear, well organized, and flows naturally. A low score means the response is contradictory, confusing, or difficult to follow. For a call center agent, this catches situations such as recommending an upsell while simultaneously classifying the intent as cancellation risk.

- **Fluency** — measures the grammatical and linguistic quality of the agent response. A score of 5 means the output is well written, natural, and easy to read. A low score means the response is awkwardly phrased, has grammatical issues, or is difficult to interpret — reducing confidence in the classification even when the underlying decision is correct.

Together, these two scores provide a quick signal of output quality. When you see a low coherence score, examine the structure of the agent's system prompt. When you see a low fluency score, look at how the agent phrases its output and whether the system prompt encourages clear, well-structured responses.

## Get started

The evaluation dataset has already been prepared for you at [eval_portal.jsonl](./eval_portal.jsonl) — 10 call scenarios ready for upload.

---

### Step 1: Open the evaluation tab

1. Open the [Microsoft Foundry portal](https://ai.azure.com/nextgen) → your project
2. In the top bar → **Build** → **Evaluations** → **Create**

### Step 2: Configure the evaluation

3. Select **Agent** as the evaluation target
4. Choose `intent-classification-agent` from the dropdown
5. Select **Individual Turns** and then **Existing Dataset**
6. Click **Upload new dataset**. First, you need to enter a name for the dataset — upload will remain disabled until you do so. Enter a name (for example, `callcenter-eval`), then add the file located at `callcenter/challenge-3-evaluate/eval_portal.jsonl` and confirm the upload.
7. Leave **Field Mapping** and **Configure Agents** as they are.
8. In the **Criteria** step, keep only **Coherence** and **Fluency**. Remove all other evaluators — especially **uncheck Tool Call Accuracy**, because the agents cannot execute local tools during evaluation and will always score poorly on this item. Reducing the evaluator list also makes the run significantly faster.
9. Keep the evaluation name as is or configure it as you prefer.
10. Submit your evaluation. The run will take some time.

### Step 3: View the results

Results appear in the **Evaluate** tab within a few minutes. Click the run name to open the results.

There are two ways to read the results, and they answer different questions:

- **Aggregate metrics** — the average score for each evaluator across the 10 test cases (for example, an overall Coherence score of 4.2). This is your quality baseline in a single number — the primary indicator you track over time and compare across agent versions.
- **Per-row analysis** — the score for each individual test case, so you can see *which specific scenarios* pulled down the average. The aggregate tells you *whether* a problem exists; the per-row view tells you *where* it is. Sort by the lowest scores to find the cases that deserve investigation.

---

## Success criteria

- [ ] The evaluation runs on all 10 test cases without errors
- [ ] You can view per-row coherence and fluency scores
- [ ] You identified at least one case where the agent can improve
- [ ] You understand the difference between aggregate metrics and per-row analysis
