rule build_stat_inputs:
    input:
        expand(
            f"{OUTDIR}/histograms/merged/{{region}}/{{systematic}}/{{variable}}.json",
            region=REGIONS,
            systematic=SYSTEMATICS,
            allow_missing=True,
        )
    output:
        f"{OUTDIR}/stat_inputs/{{variable}}.json"
    log:
        "logs/build_stat_inputs/{variable}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/build_stat_inputs.py"

rule statistical_analysis:
    input:
        f"{OUTDIR}/stat_inputs/{{variable}}.json"
    output:
        f"{OUTDIR}/stats/by_variable/{{variable}}.json"
    log:
        "logs/statistical_analysis/{variable}.log"
    conda:
        "../envs/analysis.yaml"
    script:
        "../scripts/statistical_analysis.py"

rule statistical_summary:
    input:
        expand(f"{OUTDIR}/stats/by_variable/{{variable}}.json", variable=VARIABLES)
    output:
        f"{OUTDIR}/stats/statistical_summary.json"
    log:
        "logs/statistical_summary/summary.log"
    run:
        import json
        from pathlib import Path
        Path(output[0]).parent.mkdir(parents=True, exist_ok=True)
        Path(log[0]).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "status": "placeholder",
            "analysis": config["analysis"]["name"],
            "inputs": list(input),
            "message": "Combined statistical summary placeholder; replace with analysis-specific combination.",
        }
        Path(output[0]).write_text(json.dumps(payload, indent=2) + "\n")
        Path(log[0]).write_text(f"Wrote {output[0]}\n")

rule smoke_statistical_summary:
    input:
        f"{OUTDIR}/histograms/per_sample/{SMOKE['sample']}/{SMOKE['region']}/{SMOKE['systematic']}/{SMOKE['variable']}.json"
    output:
        f"{OUTDIR}/stats/{SMOKE['region']}/{SMOKE['systematic']}/statistical_summary.json"
    log:
        "logs/smoke_statistical_summary/summary.log"
    run:
        import json
        from pathlib import Path
        Path(output[0]).parent.mkdir(parents=True, exist_ok=True)
        Path(log[0]).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "status": "placeholder",
            "scope": "smoke",
            "sample": SMOKE["sample"],
            "region": SMOKE["region"],
            "systematic": SMOKE["systematic"],
            "variable": SMOKE["variable"],
            "input": input[0],
        }
        Path(output[0]).write_text(json.dumps(payload, indent=2) + "\n")
        Path(log[0]).write_text(f"Wrote {output[0]}\n")
