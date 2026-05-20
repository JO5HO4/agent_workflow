rule build_file_manifest:
    output:
        f"{OUTDIR}/manifest/file_manifest.json"
    log:
        "logs/build_file_manifest/file_manifest.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/build_file_manifest.py"

rule validate_inputs:
    input:
        manifest=f"{OUTDIR}/manifest/file_manifest.json"
    output:
        f"{OUTDIR}/manifest/input_validation.json"
    log:
        "logs/validate_inputs/input_validation.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/validate_inputs.py"

rule preselection:
    input:
        validation=f"{OUTDIR}/manifest/input_validation.json"
    output:
        f"{OUTDIR}/preselection/{{sample}}.parquet"
    log:
        "logs/preselection/{sample}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/preselections.py"
