import csv
import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_region_table(path: str | Path, categories: list[dict[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "kind"])
        writer.writeheader()
        for category in categories:
            writer.writerow({"name": category["name"], "kind": category["kind"]})


def main() -> None:
    event_selection = json.loads(Path(snakemake.input.event_selection).read_text())
    categorization = json.loads(Path(snakemake.input.categorization).read_text())
    statistics = json.loads(Path(snakemake.input.statistics).read_text())
    categories = categorization.get("categories", [])

    plotting = {
        "stage": "plotting",
        "status": "ok",
        "artifacts": {
            "region_table": str(snakemake.output.region_table),
        },
        "plot_type": "csv_overview",
        "category_count": len(categories),
    }
    workflow_summary = {
        "status": "ok",
        "stages": {
            "event_selection": event_selection.get("status"),
            "categorization": categorization.get("status"),
            "statistics": statistics.get("status"),
            "plotting": plotting.get("status"),
        },
        "input_file_count": event_selection.get("input_file_count", 0),
        "category_count": categorization.get("category_count", 0),
        "objective_count": statistics.get("objective_count", 0),
        "reported_result_count": statistics.get("reported_result_count", 0),
    }
    validation = {
        "stage": "workflow",
        "valid": all(value == "ok" for value in workflow_summary["stages"].values()),
        "checks": {
            "event_selection_completed": event_selection.get("status") == "ok",
            "categorization_completed": categorization.get("status") == "ok",
            "statistics_completed": statistics.get("status") == "ok",
            "region_table_rows": len(categories),
        },
    }

    write_region_table(snakemake.output.region_table, categories)
    write_json(snakemake.output.summary, plotting)
    write_json(snakemake.output.workflow_summary, workflow_summary)
    write_json(snakemake.output.validation, validation)


if __name__ == "__main__":
    main()
