Revise the staged VLQ analysis scripts using the previous iteration's scripts,
results, validation summaries, and logs. Prioritize missing physics outputs:
ROOT event processing, per-region data and weighted-MC yields, merged region
yield comparisons, and report/validation evidence that those yields were made.
Preserve the existing Snakemake rule contracts and the per-file
`region_yields[region].data_yield_from_inputs` and `mc_yield_from_inputs`
merge contract.
