rule make_plots:
    input:
        f"{OUTDIR}/histograms/merged/{{region}}/{NOMINAL}/{{variable}}.json"
    output:
        png=f"{OUTDIR}/plots/{{region}}/{{variable}}.png",
        pdf=f"{OUTDIR}/plots/{{region}}/{{variable}}.pdf"
    log:
        "logs/make_plots/{region}_{variable}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/make_plots.py"

rule smoke_plot:
    input:
        f"{OUTDIR}/histograms/per_sample/{SMOKE['sample']}/{SMOKE['region']}/{SMOKE['systematic']}/{SMOKE['variable']}.json"
    output:
        png=f"{OUTDIR}/plots/smoke/{SMOKE['sample']}/{SMOKE['region']}/{SMOKE['variable']}.png",
        pdf=f"{OUTDIR}/plots/smoke/{SMOKE['sample']}/{SMOKE['region']}/{SMOKE['variable']}.pdf"
    log:
        f"logs/smoke_plot/{SMOKE['sample']}_{SMOKE['region']}_{SMOKE['variable']}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/make_plots.py"

rule report:
    input:
        stats=f"{OUTDIR}/stats/statistical_summary.json",
        cutflows=CUTFLOW_CSVS,
        plots=SUMMARY_PLOTS
    output:
        f"{OUTDIR}/report/analysis_report.md"
    log:
        "logs/report/analysis_report.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/make_report.py"

rule smoke_report:
    input:
        stats=f"{OUTDIR}/stats/{SMOKE['region']}/{SMOKE['systematic']}/statistical_summary.json",
        cutflow=f"{OUTDIR}/cutflows/{SMOKE['sample']}.csv",
        plot=f"{OUTDIR}/plots/smoke/{SMOKE['sample']}/{SMOKE['region']}/{SMOKE['variable']}.png"
    output:
        f"{OUTDIR}/report/smoke_report.md"
    log:
        "logs/report/smoke_report.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/make_report.py"
