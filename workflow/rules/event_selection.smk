rule event_selection:
    input:
        f"{OUTDIR}/preselection/{{sample}}.parquet"
    output:
        f"{OUTDIR}/selected/{{sample}}.parquet"
    log:
        "logs/event_selection/{sample}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/event_selection.py"
