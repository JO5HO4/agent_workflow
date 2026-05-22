# ATLAS Agent Workflow

This repository provides a small Snakemake harness for iterating on ATLAS analysis
scripts. The current base workflow is intentionally lightweight: it validates the
analysis JSON, discovers input files, builds region/category summaries, records
statistical-analysis metadata, and writes summary/validation artifacts.

## Layout

- `configs/workflow.json`: workflow preset, input directory, work directory, and Snakemake options.
- `configs/analysis/vlq.json`: analysis metadata and region/statistics definitions.
- `workflow/Snakefile`: stable Snakemake entrypoint.
- `workflow/rules/`: stage definitions.
- `workflow/scripts/`: editable stage implementations.
- `runs/<family>/<preset>/`: generated outputs and logs.

## Run

Dry-run the DAG:

```bash
python run.py --dry-run
```

Run the workflow:

```bash
python run.py
```

Equivalent direct Snakemake invocation:

```bash
XDG_CACHE_HOME=$PWD/.snakemake/cache snakemake --snakefile workflow/Snakefile --cores 1 --use-conda all
```

## Outputs

For the default config, outputs are written under `runs/vlq/full/`:

- `results/summary/workflow_summary.json`
- `results/validation/workflow_validation.json`
- `results/plots/region_overview.csv`
- `results/plots/region_overview.pdf`
- `results/plots/region_overview.png`
- `results/report/report.md`
- `logs/*.log`
