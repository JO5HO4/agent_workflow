# Snakemake HEP Analysis Workflow

This repository is a local-first scaffold for a reproducible high-energy physics analysis workflow. It models the file plumbing and DAG shape for a typical analysis, while every generated artifact is clearly marked with `status: placeholder` until real analysis code is added.

## Directory Structure

- `config/config.yaml`: analysis settings, luminosity, paths, regions, variables, systematics, and binning.
- `config/samples.yaml`: sample metadata, sample type, input files, cross sections, and generated event counts.
- `workflow/Snakefile`: short entry point that loads configuration and includes modular rule files.
- `workflow/rules/`: Snakemake rule modules for each analysis stage.
- `workflow/scripts/`: Python scripts called by Snakemake rules.
- `workflow/envs/analysis.yaml`: conda environment for local execution.
- `input-data/`: local input ROOT files. This directory is ignored by git.
- `results/`: generated workflow outputs. This directory is ignored by git.
- `logs/`: rule logs. This directory is ignored by git.

## Analysis Stages

1. `build_file_manifest`: records configured input ROOT files and whether they exist.
2. `validate_inputs`: validates the manifest. The placeholder implementation records missing files but does not fail.
3. `preselection`: creates placeholder skimmed per-sample Parquet files.
4. `event_selection`: applies placeholder event selection and feature construction.
5. `categorization`: writes one categorized Parquet file per sample and region.
6. `cutflow`: writes CSV and JSON cutflow tables per sample.
7. `make_histograms`: produces per-sample histogram JSON files for each region, systematic, and variable.
8. `merge_histograms`: merges per-sample histograms into analysis histograms.
9. `build_stat_inputs`: builds placeholder statistical-input JSON files.
10. `statistical_analysis`: writes placeholder fit/limit/significance JSON outputs.
11. `make_plots`: makes PNG and PDF summary plots from merged nominal histograms.
12. `report`: writes a Markdown analysis report.

## Add Samples

Edit `config/samples.yaml`:

```yaml
samples:
  ttbar:
    type: background
    files:
      - mc/ttbar.root
    cross_section_pb: 831.76
    generated_events: 1000000
```

Place the corresponding files under the configured `paths.input_dir`, currently `input-data/`.

## Add Regions

Edit `config/config.yaml` under `regions`. Region names become the `{region}` wildcard:

```yaml
regions:
  two_lepton_sr:
    description: Two-lepton signal region.
    selection: "n_leptons >= 2 and met > 80"
```

The placeholder categorization script evaluates the `selection` with `pandas.DataFrame.query`.

## Add Variables

Edit `config/config.yaml` under `variables`. Variable names become the `{variable}` wildcard:

```yaml
variables:
  jet_pt:
    expression: "jet_pt"
    label: "Leading jet pT"
    unit: GeV
    binning:
      bins: 25
      low: 0.0
      high: 500.0
```

For real analysis code, update `workflow/scripts/event_selection.py` or upstream scripts to create the requested column.

## Add Systematics

Edit `config/config.yaml` under `systematics`. Systematic names become the `{systematic}` wildcard. The placeholder histogram script only treats `weight_up` and `weight_down` specially.

## Run

Dry run from the repository root:

```bash
snakemake -n --cores 1
```

Run the full workflow with conda environments:

```bash
snakemake --cores 4 --use-conda
```

Run the minimal smoke target:

```bash
snakemake smoke --cores 1 --use-conda
```

Draw the DAG:

```bash
snakemake --dag | dot -Tpdf > dag.pdf
```

Clean generated outputs:

```bash
rm -rf results logs .snakemake
```

## Notes

- The workflow is intentionally local-first. Snakemake profiles for batch systems can be added later without changing the rule layout.
- Placeholder outputs are for testing reproducibility, path conventions, wildcard expansion, and DAG wiring only.
- Replace the placeholder scripts stage by stage with real ROOT reading, event selections, histogramming, and statistical modeling.
