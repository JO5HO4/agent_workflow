from pathlib import Path

OUTDIR = config["paths"]["output_dir"]
SAMPLES = sorted(config["samples"].keys())
REGIONS = sorted(config["regions"].keys())
VARIABLES = sorted(config["variables"].keys())
SYSTEMATICS = sorted(config["systematics"].keys())
NOMINAL = config["defaults"].get("nominal_systematic", "nominal")
SMOKE = config["defaults"]["smoke"]

MERGED_HISTS = expand(
    f"{OUTDIR}/histograms/merged/{{region}}/{{systematic}}/{{variable}}.json",
    region=REGIONS,
    systematic=SYSTEMATICS,
    variable=VARIABLES,
)
CUTFLOW_CSVS = expand(f"{OUTDIR}/cutflows/{{sample}}.csv", sample=SAMPLES)
SUMMARY_PLOTS = expand(
    f"{OUTDIR}/plots/{{region}}/{{variable}}.png",
    region=REGIONS,
    variable=VARIABLES,
)

rule all:
    input:
        f"{OUTDIR}/report/analysis_report.md",
        f"{OUTDIR}/stats/statistical_summary.json",
        MERGED_HISTS,
        CUTFLOW_CSVS,
        SUMMARY_PLOTS

rule smoke:
    input:
        f"{OUTDIR}/report/smoke_report.md",
        f"{OUTDIR}/stats/{SMOKE['region']}/{SMOKE['systematic']}/statistical_summary.json",
        f"{OUTDIR}/histograms/per_sample/{SMOKE['sample']}/{SMOKE['region']}/{SMOKE['systematic']}/{SMOKE['variable']}.json",
        f"{OUTDIR}/cutflows/{SMOKE['sample']}.csv",
        f"{OUTDIR}/plots/smoke/{SMOKE['sample']}/{SMOKE['region']}/{SMOKE['variable']}.png"
