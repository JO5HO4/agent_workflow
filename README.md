# ATLAS Agent Workflow

This repository provides a small Snakemake harness for iterating on ATLAS analysis
scripts. Each iteration is split into an explicit Codex phase and Snakemake
phase. Successful Snakemake phases are checkpointed so the next Codex phase
continues with the next configured iteration. The current base workflow is
intentionally lightweight: it validates the analysis JSON, discovers input files,
builds region/category summaries, records statistical-analysis metadata, and
writes summary/validation artifacts.

## Layout

- `configs/workflow.json`: input directory, work directory, loop count, and Codex prompts.
- `configs/analysis/vlq.json`: analysis metadata and region/statistics definitions.
- `workflow/Snakefile`: stable Snakemake entrypoint.
- `workflow/rules/`: stage definitions and per-file fan-out rules.
- `workflow/scripts/`: editable stage implementations.
- `runs/iteration<N>/`: generated workflow copies, outputs, and logs.

## Run

Run Codex for the next iteration:

```bash
python run.py --codex
```

Then run Snakemake for that Codex-complete iteration:

```bash
python run.py --snakemake
```

After Snakemake succeeds, the next Codex call advances to the next iteration:

```bash
python run.py --codex
```

Dry-run Snakemake after one Codex script revision:

```bash
python run.py --snakemake --dry-run
```

Snakemake dry-runs do not checkpoint the iteration.

Running the phases out of order is a no-op: `--snakemake` does nothing until a
Codex phase has completed, and `--codex` does not advance past a Codex-complete
iteration until `--snakemake` checkpoints it.

Run a specific Snakemake target for the pending iteration:

```bash
python run.py --snakemake --target results/report/report.md
```

Iteration 0 uses `codex.prompt`; later iterations use `codex.revise` and copy the
scripts from the previous iteration before asking Codex to revise them. A Codex
phase records `.codex_complete.json`; a completed Snakemake phase records
`.run_complete.json`. Existing iteration directories created before checkpointing
are accepted as completed predecessors.

With the default work directory, each iteration is saved separately under:

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
- `results/yields/region_yields.csv`
- `results/plots/region_overview.pdf`
- `results/plots/region_overview.png`
- `results/report/report.md`
- `logs/*.log`

`run.py` sets the concrete work directory for each iteration. If the template
Snakefile is run directly with the base workflow config, it defaults to
`runs/iteration0/` instead of writing outputs into the `runs/` root.
