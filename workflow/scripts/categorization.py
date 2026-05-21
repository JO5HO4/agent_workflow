import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def region_name(region: dict[str, Any]) -> str:
    return str(region.get("region_name") or region.get("region_id") or "unnamed_region")


def main() -> None:
    analysis = json.loads(Path(snakemake.input.analysis_config).read_text())
    event_selection = json.loads(Path(snakemake.input.event_selection).read_text())

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

    payload = {
        "stage": "categorization",
        "status": "ok",
        "input_file_count": event_selection.get("input_file_count", 0),
        "signal_region_count": len(signal_regions),
        "control_region_count": len(control_regions),
        "category_count": len(categories),
        "categories": categories,
    }
    validation = {
        "stage": "categorization",
        "valid": len(categories) > 0,
        "checks": {
            "has_signal_regions": len(signal_regions) > 0,
            "has_control_regions": len(control_regions) > 0,
            "category_names_unique": len({item["name"] for item in categories}) == len(categories),
        },
    }

    write_json(snakemake.output.summary, payload)
    write_json(snakemake.output.validation, validation)


if __name__ == "__main__":
    main()
