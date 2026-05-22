Implement the VLQ analysis in the staged Snakemake scripts using the input ROOT
files. Do real event processing: read needed branches, apply VLQ region
selections per file, compute region-level data and weighted-MC yields, and keep
the per-file rule contracts and merged summaries intact.

The merged outputs and report must compare each VLQ region's input-derived yields
with the observed-data and expected-background values in the analysis JSON. Do
not treat metadata-only summaries as a valid analysis. Per-file categorization
summaries should expose `region_yields[region].data_yield_from_inputs` and
`region_yields[region].mc_yield_from_inputs` for merging.
