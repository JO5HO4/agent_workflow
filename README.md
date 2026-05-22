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
- `workflow/rules/`: stage definitions and per-file fan-out rules.
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

## Parallel Stages

Snakemake discovers visible files below `workflow.input_dir` and assigns each one
a deterministic `file_id`. Event selection and categorization run once per file,
so Snakemake can schedule those jobs across the available cores:

```text
input file -> event selection -> categorization
```

The per-file categorization summaries are merged before statistics:

```text
per-file categorizations -> merged categorization -> statistics -> plotting -> report
```

Merged event-selection and categorization summaries keep the same downstream
summary paths used by statistics, plotting, and reporting.

The default workflow config sets `snakemake.cores` to `6`. Keep that number low
enough for the memory used by the per-file event-selection jobs on the machine
running the workflow.

## Outputs

For each iteration, outputs are written under its iteration directory:

- `results/summary/workflow_summary.json`
- `results/validation/workflow_validation.json`
- `results/plots/region_overview.csv`
- `results/plots/region_overview.pdf`
- `results/plots/region_overview.png`
- `results/report/report.md`
- `logs/*.log`

`run.py` sets the concrete work directory for each iteration. If the template
Snakefile is run directly with the base workflow config, it defaults to
`runs/iteration0/` instead of writing outputs into the `runs/` root.
