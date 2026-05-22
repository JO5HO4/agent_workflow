import csv
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


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


def definition_value(category: dict[str, Any], key: str) -> Any:
    return category.get("definition", {}).get(key)


def write_region_yield_table(
    path: str | Path, categories: list[dict[str, Any]], region_yields: dict[str, Any]
) -> int:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "region",
        "kind",
        "observed_data_spec",
        "expected_background_spec",
        "data_yield_from_inputs",
        "mc_yield_from_inputs",
    ]
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        rows = 0
        for category in categories:
            region = category["name"]
            expected = definition_value(category, "expected_total_background") or {}
            computed = region_yields.get(region, {})
            writer.writerow(
                {
                    "region": region,
                    "kind": category["kind"],
                    "observed_data_spec": definition_value(category, "observed_data_yield"),
                    "expected_background_spec": expected.get("value"),
                    "data_yield_from_inputs": computed.get("data_yield_from_inputs"),
                    "mc_yield_from_inputs": computed.get("mc_yield_from_inputs"),
                }
            )
            rows += 1
    return rows


def write_region_plot(pdf_path: str | Path, png_path: str | Path, categories: list[dict[str, Any]]) -> None:
    kind_counts: dict[str, int] = {}
    for category in categories:
        kind = str(category["kind"])
        kind_counts[kind] = kind_counts.get(kind, 0) + 1

    output_paths = [Path(pdf_path), Path(png_path)]
    for output in output_paths:
        output.parent.mkdir(parents=True, exist_ok=True)

    labels = list(kind_counts) or ["none"]
    counts = [kind_counts[label] for label in labels] or [0]
    figure, axis = plt.subplots(figsize=(6.4, 4.2))
    bars = axis.bar(labels, counts, color=["#386cb0", "#fdb462"][: len(labels)])
    axis.set_title("Analysis region overview")
    axis.set_xlabel("Region kind")
    axis.set_ylabel("Region count")
    axis.set_ylim(0, max(counts + [1]) * 1.2)
    axis.bar_label(bars, padding=3)
    figure.tight_layout()
    figure.savefig(output_paths[0])
    figure.savefig(output_paths[1], dpi=160)
    plt.close(figure)


def main() -> None:
    event_selection = json.loads(Path(snakemake.input.event_selection).read_text())
    categorization = json.loads(Path(snakemake.input.categorization).read_text())
    statistics = json.loads(Path(snakemake.input.statistics).read_text())
    categories = categorization.get("categories", [])
    region_yields = categorization.get("region_yields", {})

    plotting = {
        "stage": "plotting",
        "status": "ok",
        "artifacts": {
            "region_table": str(snakemake.output.region_table),
            "region_yield_table": str(snakemake.output.region_yield_table),
            "region_plot_pdf": str(snakemake.output.region_plot_pdf),
            "region_plot_png": str(snakemake.output.region_plot_png),
        },
        "plot_type": "region_kind_overview",
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
            "root_events_read": event_selection.get("events_read", 0),
            "input_region_yield_rows": len(region_yields),
        },
    }

    write_region_table(snakemake.output.region_table, categories)
    yield_rows = write_region_yield_table(
        snakemake.output.region_yield_table, categories, region_yields
    )
    validation["checks"]["region_yield_table_rows"] = yield_rows
    validation["valid"] = (
        validation["valid"]
        and event_selection.get("events_read", 0) > 0
        and bool(region_yields)
        and yield_rows > 0
    )
    write_region_plot(
        snakemake.output.region_plot_pdf,
        snakemake.output.region_plot_png,
        categories,
    )
    write_json(snakemake.output.summary, plotting)
    write_json(snakemake.output.workflow_summary, workflow_summary)
    write_json(snakemake.output.validation, validation)


if __name__ == "__main__":
    main()
