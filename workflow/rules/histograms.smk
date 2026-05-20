rule make_histograms:
    input:
        f"{OUTDIR}/categories/{{sample}}/{{region}}.parquet"
    output:
        f"{OUTDIR}/histograms/per_sample/{{sample}}/{{region}}/{{systematic}}/{{variable}}.json"
    log:
        "logs/make_histograms/{sample}_{region}_{systematic}_{variable}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/make_histograms.py"

rule merge_histograms:
    input:
        expand(
            f"{OUTDIR}/histograms/per_sample/{{sample}}/{{region}}/{{systematic}}/{{variable}}.json",
            sample=SAMPLES,
            allow_missing=True,
        )
    output:
        f"{OUTDIR}/histograms/merged/{{region}}/{{systematic}}/{{variable}}.json"
    log:
        "logs/merge_histograms/{region}_{systematic}_{variable}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/merge_histograms.py"
