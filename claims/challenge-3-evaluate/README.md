# Challenge 3: Evaluate

Tempo: ~30 minutos

## Objectives

By the end of this challenge, you will have:

- ✅ Run a systematic evaluation of your agents with a test dataset
- ✅ Use built-in evaluators (coherence, fluency) to measure quality
- ✅ Interpret evaluation metrics and identify areas for improvement
- ✅ Understand how to integrate evaluations into a CI/CD pipeline

![evaluate](./images/evaluate.png)

## Context

Monitoring tells you **what is happening** (latency, errors, token usage). Evaluation tells you **whether the decisions are actually correct**.

You have a dataset with 10 test cases, each containing claim metrics and the expected correct output (classification + recommended action). You will run your agents on these cases and measure performance using LLM-as-a-judge scoring.

## Why evaluate?

Monitoring tells you that your agents are *running*; evaluation tells you whether they are doing the *right thing*. These are fundamentally different questions.

Monitoring captures **operational signals**: latency, token counts, error rates, and availability. These show *how* the system behaves mechanically. Evaluation captures **quality signals**: are the agent's outputs correct, relevant, coherent, and consistent with expected results? These show *whether* the system is actually fulfilling its purpose.

Without systematic evaluation, you rely on spot checks: you read a few responses and judge them subjectively. This does not scale, is not repeatable, and does not detect regressions when you update a prompt or switch models. Evaluation provides a measurable baseline: a score you can track over time and compare across versions.

Evaluation also reveals problems that monitoring cannot see. An agent that always responds quickly and without errors, but consistently approves high-risk claims or flags legitimate claims for unnecessary investigation, looks perfectly healthy in monitoring. Evaluation detects this immediately.

For production AI, evaluations should run:

- **Before deployment**: establish a quality baseline and gate releases on minimum scores
- **After any change**: to system prompts, models, tools, or policy documents in the knowledge base
- **On a schedule**: to detect drift as fraud patterns evolve or new claim types emerge

For ClaimSight specifically: an agent that approves CLM-001 (fraud risk score 0.87, document completeness 45%) because it generated a coherent-sounding rationale is a direct financial risk. Monitoring sees a successful response. Only evaluation — comparing the output against the expected "investigate" decision — catches the mistake.

## The evaluation dataset

The dataset lives at [challenge-4-deploy/evaluation_dataset.json](../challenge-4-deploy/evaluation_dataset.json) — it contains:

- 10 claims covering normal, warning, and critical scenarios
- Each has an `input` (what you send to the agent)
- Each has an `expected_output` (the correct classification and action)

## About the evaluators

Microsoft Foundry uses an **LLM-as-a-judge** approach: a separate model reads each agent response alongside the input and reference answer, then assigns a score from 1 to 5. You will use two built-in evaluators:

- **Coherence**: measures whether the agent response is logically structured and internally consistent. A score of 5 means the output is clear, well organized, and flows naturally. A low score indicates a contradictory, confusing, or difficult-to-follow response. For a claims agent, this catches situations such as recommending approval while also flagging a high fraud risk score.

- **Fluency**: measures the grammatical and linguistic quality of the agent response. A score of 5 means the output is well written, natural, and easy to read. A low score indicates awkward phrasing, grammatical errors, or wording that is difficult to interpret, reducing confidence in the decision even when the underlying assessment is correct.

These two scores together give you a quick signal on output quality. When you see a low coherence score, look at the agent's system prompt structure. When you see a low fluency score, look at how the agent phrases its output and whether its system prompt encourages clear, well-formed responses.

## Getting started

The evaluation dataset has already been prepared for you as [eval_portal.jsonl](./eval_portal.jsonl) — 10 insurance claim scenarios ready to upload.

---

### Step 1: Open the evaluation tab

1. Go to the [Microsoft Foundry portal](https://ai.azure.com/nextgen) → your project
2. On the top bar → **Build** → **Evaluations** → **Create**

### Step 2: Configure the evaluation

3. Select **Agent** as the evaluation target
4. Choose `claims-triage-agent` from the dropdown
5. Select **Individual Turns** and then **Existing Dataset**
6. Click on **Upload new dataset**. 
You must enter a dataset name first — the upload stays disabled until you do. Type a name (e.g. `claims-eval`), then add the file located on `claims/challenge-3-evaluate/eval_portal.jsonl` and confirm the upload.
7. Leave the **Field Mapping** and **Configure Agents** fields as is.
8. In the **Criteria** step, keep only **Coherence** and **Fluency**. Remove every other evaluator — in particular **deselect Tool Call Accuracy**, since the agents can't execute the local tools during evaluation and will always score low on it. Trimming the evaluator list also makes the run significantly faster.
9. Leave the Evaluation Name as is or configure to your liking.
10. Submit your Evaluation. This will take some time to run.

### Step 3: View results

Results appear in the **Evaluate** tab within a few minutes. Click the run name to open the results.

There are two ways to read the results, and they answer different questions:

- **Aggregate metrics** — the average score for each evaluator across all 10 test cases (e.g. an overall Coherence of 4.2). This is your single-number quality baseline — the headline figure you track over time and compare across agent versions.
- **Per-row analysis** — the score for each individual test case, so you can see *which specific scenarios* dragged the average down. The aggregate tells you *if* there's a problem; the per-row view tells you *where* it is. Sort by the lowest scores to find the cases worth investigating.

---

## Success criteria

- [ ] The evaluation runs on all 10 test cases without errors
- [ ] You can see per-row coherence and fluency scores
- [ ] You identified at least one case where the agent can improve
- [ ] You understand the difference between aggregate metrics and per-row analysis
