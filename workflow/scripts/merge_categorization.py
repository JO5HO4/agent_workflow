import json
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def region_name(region: dict[str, Any]) -> str:
    return str(region.get("region_name") or region.get("region_id") or "unnamed_region")


def analysis_categories(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    signal_regions = analysis.get("signal_regions", [])
    control_regions = analysis.get("control_regions", [])
    categories = [
        {"name": region_name(region), "kind": "signal", "definition": region}
        for region in signal_regions
    ]
    categories.extend(
        {"name": region_name(region), "kind": "control", "definition": region}
        for region in control_regions
    )
    return categories


def merge_region_yields(summaries: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    merged: dict[str, dict[str, float]] = {}
    for summary in summaries:
        for region, yields in summary.get("region_yields", {}).items():
            target = merged.setdefault(
                str(region),
                {"data_yield_from_inputs": 0.0, "mc_yield_from_inputs": 0.0},
            )
            for key in target:
                target[key] += float(yields.get(key, 0.0))
    return merged


def main() -> None:
    analysis = read_json(snakemake.input.analysis_config)
    summaries = [read_json(path) for path in snakemake.input.summaries]
    validations = [read_json(path) for path in snakemake.input.validations]
    categories = analysis_categories(analysis)
    region_yields = merge_region_yields(summaries)
    signal_region_count = sum(category["kind"] == "signal" for category in categories)
    control_region_count = sum(category["kind"] == "control" for category in categories)

    payload = {
        "stage": "categorization",
        "status": "ok",
        "input_file_count": sum(item.get("input_file_count", 0) for item in summaries),
        "signal_region_count": signal_region_count,
        "control_region_count": control_region_count,
        "category_count": len(categories),
        "categories": categories,
        "region_yields": region_yields,
        "file_summaries": [str(path) for path in snakemake.input.summaries],
    }
    validation = {
        "stage": "categorization",
        "valid": len(categories) > 0 and all(item.get("valid", False) for item in validations),
        "checks": {
            "per_file_jobs": len(summaries),
            "per_file_validations": len(validations),
            "has_categories": len(categories) > 0,
            "has_input_region_yields": bool(region_yields),
            "category_names_unique": len({item["name"] for item in categories}) == len(categories),
        },
    }
    validation["valid"] = validation["valid"] and bool(region_yields)

    write_json(snakemake.output.summary, payload)
    write_json(snakemake.output.validation, validation)


if __name__ == "__main__":
    main()
