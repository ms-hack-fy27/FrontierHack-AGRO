# Challenge 3: Evaluate

Time: ~30 minutes

## Objectives

By the end of this challenge, you will have:

- ✅ Run a systematic evaluation of your agents with a test set
- ✅ Use built-in evaluators (coherence and fluency) to measure quality
- ✅ Interpret evaluation metrics and identify areas for improvement
- ✅ Understand how to integrate evaluations into a CI/CD pipeline

![evaluate](./images/evaluate.png)

## Context

Monitoring tells you **what is happening** (latency, errors, and token usage). Evaluation tells you **whether the responses are actually good**.

You have a dataset with 10 test cases, each containing a snapshot of sensor readings and the expected correct output (classification + recommended action). You will run your agents on these cases and measure performance using LLM-as-a-judge scoring.

## Why Evaluate?

Monitoring tells you that your agents are *running*; evaluation tells you whether they are doing the *right thing*. These are fundamentally different questions.

Monitoring captures **operational signals**: latency, token counts, error rates, and availability. These tell you *how* the system behaves mechanically. Evaluation captures **quality signals**: are agent outputs correct, relevant, coherent, and consistent with expected results? These signals tell you *whether* the system is actually fulfilling its purpose.

Without systematic evaluation, you rely on spot checks: you read a few responses and judge them subjectively. This does not scale, is not repeatable, and does not detect regressions when you update a prompt or change models. Evaluation provides a measurable baseline: a score you can track over time and compare across versions.

Evaluation also reveals problems that monitoring cannot see. An agent that always responds quickly and without errors but repeatedly misdiagnoses fault conditions, or recommends “schedule routine maintenance” for a machine that needs to be shut down immediately, looks perfectly healthy to monitoring. Evaluation catches this immediately.

For production AI, evaluations should run:

- **Before deployment** — establish a quality baseline and gate releases with minimum scores
- **After any change** — to system prompts, models, tools, or threshold data
- **On a schedule** — detect drift as machine configurations or operating conditions evolve

For TireForge specifically: an agent that confidently diagnoses a CP-003 anomaly as “normal vibration” when thresholds have been exceeded could delay critical maintenance action for hours. Monitoring sees a fast, error-free response. Only evaluation, comparing the output with the known correct classification, reveals the problem.

## The Evaluation Dataset

The dataset is in [challenge-4-deploy/evaluation_dataset.json](../challenge-4-deploy/evaluation_dataset.json) and contains:

- 10 scenarios covering normal, warning, and critical machines
- Each has an `input` (what you send to the agent)
- Each has an `expected_output` (the correct classification and action)

## About the Evaluators

Microsoft Foundry uses an **LLM-as-a-judge** approach: a separate model reads each agent response along with the input and reference truth and assigns a score from 1 to 5. You will use two built-in evaluators:

- **Coherence** — measures whether the agent response is logically structured and internally consistent. A score of 5 means the output is clear, well organized, and flows naturally. A low score means the response is contradictory, confusing, or difficult to follow. For a factory agent, this catches situations such as recommending “no action” while listing critical anomalies.

- **Fluency** — measures the grammatical and linguistic quality of the agent response. A score of 5 means the output is well written, natural, and easy to read. A low score means the response has awkward phrasing, grammatical errors, or is difficult to interpret, reducing confidence in the classification even when the underlying diagnosis is correct.

Together, these two scores provide a quick signal of output quality. When you see a low coherence score, examine the agent's system prompt structure. When you see a low fluency score, examine how the agent phrases its output and whether the system prompt encourages clear, well-formed responses.

## Start Here

The evaluation dataset is already prepared for you in [eval_portal.jsonl](./eval_portal.jsonl): 10 machine sensor scenarios ready for upload.

---

### Step 1: Open the evaluation tab

1. Open the [Microsoft Foundry portal](https://ai.azure.com/nextgen) → your project
2. In the top bar → **Build** → **Evaluations** → **Create**

### Step 2: Configure the evaluation

3. Select **Agent** as the evaluation target
4. Choose `anomaly-detection-agent` from the dropdown
5. Select **Individual turns**, then **Existing dataset**
6. Select **Upload new dataset**.
First, you must enter a dataset name; upload remains disabled until you do. Enter a name (for example, `factory-eval`), add the file at `factory/challenge-3-evaluate/eval_portal.jsonl`, and confirm the upload.
7. Leave **Field mapping** and **Configure agents** unchanged.
8. In the **Criteria** step, keep only **Coherence** and **Fluency**. Remove all other evaluators, especially **uncheck Tool Call Accuracy**, because the agents cannot execute local tools during evaluation and will always score poorly on that item. Reducing the evaluator list also makes the run significantly faster.
9. Keep the evaluation name as is or configure it as you prefer.
10. Submit your evaluation. The run will take some time.

### Step 3: View the results

Results appear in the **Evaluate** tab after a few minutes. Select the run name to open the results.

There are two ways to read the results, and they answer different questions:

- **Aggregate metrics** — the average score for each evaluator across the 10 test cases (for example, an overall Coherence score of 4.2). This is your one-number quality baseline, the primary value you track over time and compare across agent versions.
- **Row-level analysis** — the score for each individual test case, so you can see *which specific scenarios* lowered the average. The aggregate tells you *whether* there is a problem; the row view tells you *where* it is. Sort by the lowest scores to find cases that deserve investigation.

---

## Success Criteria

- [ ] The evaluation runs on all 10 test cases without errors
- [ ] You can see row-level coherence and fluency scores
- [ ] You identified at least one case where the agent could improve
- [ ] You understand the difference between aggregate metrics and row-level analysis
