# Challenge 3: Evaluate

Time: about 30 minutes

## Objectives

Run a repeatable evaluation against 10 crop-health cases and interpret coherence and fluency scores. The cases include normal, warning, critical, single-metric, and multi-metric patterns.

## Dataset

`eval_portal.jsonl` is a 10-line JSONL dataset for portal upload. The same cases, with explicit IDs and JSON expected outputs, are in `../challenge-4-workflow/evaluation_dataset.json` for scripted or future CI use.

The portal dataset embeds values and thresholds in each query. This is intentional: portal evaluations cannot execute the local Python `check_health_monitor` function.

## Run in Foundry

1. Open the [Microsoft Foundry portal](https://ai.azure.com/nextgen) and select `smart-farm-project`.
2. Open Build -> Evaluations -> Create and choose Agent.
3. Select `smart-farm-classifier-agent`, Individual turns, and Existing dataset.
4. Enter a dataset name before selecting Upload new dataset. Upload `eval_portal.jsonl`.
5. Keep field mapping unchanged.
6. Keep Coherence and Fluency. Remove Tool Call Accuracy because the uploaded test turns do not run the local function.
7. Submit the evaluation and inspect aggregate and row-level results.

## Discussion prompts

- Which cases test the irrigation-stress pattern?
- Which case should produce urgent agronomist escalation?
- Does a coherent answer necessarily contain correct threshold reasoning?
- Which row would you use as a regression test after changing the system prompt?

## Success criteria

- [ ] All 10 cases run without upload or execution errors.
- [ ] Coherence and Fluency results are visible.
- [ ] At least one row-level improvement opportunity is identified.
- [ ] You can explain why monitoring and evaluation answer different questions.
