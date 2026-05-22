# ATLAS Agent Workflow

This repository provides a small Snakemake harness for iterating on ATLAS analysis
scripts. The runner stages a workflow copy for each configured iteration, lets
Codex edit the staged scripts, and then runs Snakemake on that iteration before
starting the next one. The current base workflow is intentionally lightweight:
it validates the analysis JSON, discovers input files, builds region/category
summaries, records statistical-analysis metadata, and writes summary/validation
artifacts.

## Layout

- `configs/workflow.json`: input directory, work directory, loop count, and Codex prompts.
- `configs/analysis/vlq.json`: analysis metadata and region/statistics definitions.
- `workflow/Snakefile`: stable Snakemake entrypoint.
- `workflow/rules/`: stage definitions.
- `workflow/scripts/`: editable stage implementations.
- `runs/iteration<N>/`: generated workflow copies, outputs, and logs.

## Run

Run the Codex and Snakemake loop:

```bash
python run.py
```

Dry-run Snakemake after each Codex script revision:

```bash
python run.py --dry-run
```

Run staged Snakemake iterations without invoking Codex:

```bash
python run.py --skip-codex
```

Iteration 0 uses `codex.prompt`; later iterations use `codex.revise` and copy the
scripts from the previous iteration before asking Codex to revise them. With the
default work directory, each iteration is saved separately under:

- `runs/iteration0/workflow/scripts/` and `runs/iteration0/results/`
- `runs/iteration1/workflow/scripts/` and `runs/iteration1/results/`
- `runs/iteration2/workflow/scripts/` and `runs/iteration2/results/`

## Outputs

For each iteration, outputs are written under its iteration directory:

- `results/summary/workflow_summary.json`
- `results/validation/workflow_validation.json`
- `results/plots/region_overview.csv`
- `results/plots/region_overview.pdf`
- `results/plots/region_overview.png`
- `results/report/report.md`
- `logs/*.log`
