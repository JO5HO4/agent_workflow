rule categorization:
    input:
        f"{OUTDIR}/selected/{{sample}}.parquet"
    output:
        f"{OUTDIR}/categories/{{sample}}/{{region}}.parquet"
    log:
        "logs/categorization/{sample}_{region}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/categorization.py"

rule cutflow:
    input:
        selected=f"{OUTDIR}/selected/{{sample}}.parquet",
        categories=expand(f"{OUTDIR}/categories/{{sample}}/{{region}}.parquet", region=REGIONS)
    output:
        csv=f"{OUTDIR}/cutflows/{{sample}}.csv",
        json=f"{OUTDIR}/cutflows/{{sample}}.json"
    log:
        "logs/cutflow/{sample}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/make_cutflow.py"
