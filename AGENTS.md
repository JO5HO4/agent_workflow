# Agent Operating Guide

This repository uses Codex to revise staged analysis scripts while Snakemake
remains the execution harness.

## Editable Surface

During `python run.py`, Codex is started inside:

```text
runs/iteration<N>/workflow/scripts/
```

Edit staged scripts in that directory only.

Agents may read the staged workflow context, analysis config, previous iteration
results, validation summaries, and logs.

Do not edit the Snakefile, rules, envs, prompts, workflow config, or template
workflow during a staged Codex iteration.

## Workflow Shape

The runner creates a fresh directory for each iteration, copies the previous
iteration's workflow forward, runs Codex, then runs Snakemake.

Event selection and categorization fan out per input file:

```text
input file -> event_selection[file_id] -> categorization[file_id]
```

Merged summaries feed statistics, plotting, and reporting.

Keep per-file script outputs compatible with the staged rules and preserve the
summary and validation products expected by downstream stages.

## Expected Loop

1. Iteration 0 starts from `workflow/` and uses `prompts/task.md`.
2. Later iterations copy the prior staged workflow and use `prompts/revise.md`.
3. After each Codex edit, Snakemake writes separate scripts, results, validation,
   reports, and logs under that iteration directory.
4. Revisions should use previous iteration outputs and logs as evidence.
