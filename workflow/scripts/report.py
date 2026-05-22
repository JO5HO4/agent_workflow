import csv
import json
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def artifact_row(path: str | Path) -> str:
    artifact = Path(path)
    return f"| `{artifact.name}` | `{artifact.as_posix()}` |"


def count_region_rows(path: str | Path) -> int:
    with Path(path).open(newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> None:
    event_selection = read_json(snakemake.input.event_selection_summary)
    event_selection_validation = read_json(snakemake.input.event_selection_validation)
    categorization = read_json(snakemake.input.categorization_summary)
    categorization_validation = read_json(snakemake.input.categorization_validation)
    statistics = read_json(snakemake.input.statistics_summary)
    statistics_validation = read_json(snakemake.input.statistics_validation)
    plotting = read_json(snakemake.input.plotting_summary)
    workflow_summary = read_json(snakemake.input.workflow_summary)
    workflow_validation = read_json(snakemake.input.workflow_validation)

    stage_rows = [
        ("Event selection", event_selection, event_selection_validation),
        ("Categorization", categorization, categorization_validation),
        ("Statistics", statistics, statistics_validation),
        ("Plotting", plotting, workflow_validation),
    ]
    lines = [
        "# Analysis Workflow Report",
        "",
        "## Workflow Summary",
        "",
        f"- Status: `{workflow_summary.get('status', 'unknown')}`",
        f"- Input files discovered: {workflow_summary.get('input_file_count', 0)}",
        f"- Categories: {workflow_summary.get('category_count', 0)}",
        f"- Analysis objectives: {workflow_summary.get('objective_count', 0)}",
        f"- Reported results: {workflow_summary.get('reported_result_count', 0)}",
        f"- Region table rows: {count_region_rows(snakemake.input.region_table)}",
        f"- Region yield rows: {count_region_rows(snakemake.input.region_yield_table)}",
        "",
        "## Stage Status",
        "",
        "| Stage | Status | Validation |",
        "| --- | --- | --- |",
    ]
    lines.extend(
        f"| {name} | `{summary.get('status', 'unknown')}` | `{validation.get('valid', False)}` |"
        for name, summary, validation in stage_rows
    )
    lines.extend(
        [
            "",
            "## Region Yield Comparison",
            "",
            f"- Yield table: `{snakemake.input.region_yield_table}`",
            f"- Input-derived region yields present: `{bool(categorization.get('region_yields'))}`",
        ]
    )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "| Artifact | Path |",
            "| --- | --- |",
        ]
    )
    lines.extend(artifact_row(path) for path in snakemake.input)

    output = Path(snakemake.output.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
