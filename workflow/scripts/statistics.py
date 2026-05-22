import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    analysis = json.loads(Path(snakemake.input.analysis_config).read_text())
    categorization = json.loads(Path(snakemake.input.categorization).read_text())

    objectives = analysis.get("analysis_objectives", [])
    fit_setups = analysis.get("fit_setup", [])
    reported_results = analysis.get("results", [])
    region_yields = categorization.get("region_yields", {})

    payload = {
        "stage": "statistics",
        "status": "ok",
        "category_count": categorization.get("category_count", 0),
        "objective_count": len(objectives),
        "fit_setup_count": len(fit_setups),
        "reported_result_count": len(reported_results),
        "region_yield_count": len(region_yields),
        "objectives": objectives,
        "fit_setups": fit_setups,
        "reported_results": reported_results,
    }
    validation = {
        "stage": "statistics",
        "valid": len(objectives) > 0 and len(fit_setups) > 0,
        "checks": {
            "has_objectives": len(objectives) > 0,
            "has_fit_setup": len(fit_setups) > 0,
            "has_categories": categorization.get("category_count", 0) > 0,
            "has_input_region_yields": bool(region_yields),
        },
    }
    validation["valid"] = validation["valid"] and bool(region_yields)

    write_json(snakemake.output.summary, payload)
    write_json(snakemake.output.validation, validation)


if __name__ == "__main__":
    main()
