from __future__ import annotations

from pathlib import Path


def require_file(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Required input is missing: {candidate}")
    return candidate


def main() -> None:
    output = Path(snakemake.output[0])
    output.parent.mkdir(parents=True, exist_ok=True)
    cfg = snakemake.config
    analysis = cfg["analysis"]["name"]
    stats = require_file(snakemake.input.stats)
    cutflow_inputs = getattr(snakemake.input, "cutflows", [])
    single_cutflow = getattr(snakemake.input, "cutflow", None)
    plot_inputs = getattr(snakemake.input, "plots", [])
    single_plot = getattr(snakemake.input, "plot", None)
    cutflows = [require_file(path) for path in cutflow_inputs]
    if single_cutflow is not None:
        cutflows.append(require_file(single_cutflow))
    plots = [require_file(path) for path in plot_inputs]
    if single_plot is not None:
        plots.append(require_file(single_plot))

    print(f"[make_report] analysis={analysis} stats={stats} output={output}")
    lines = [
        f"# {analysis}",
        "",
        "**Status:** placeholder",
        "",
        "This report is generated to validate the Snakemake DAG and file plumbing. It does not contain real physics results.",
        "",
        "## Statistical Summary",
        "",
        f"- `{stats}`",
        "",
        "## Cutflows",
        "",
    ]
    lines.extend(f"- `{path}`" for path in cutflows)
    lines.extend(["", "## Plots", ""])
    lines.extend(f"- `{path}`" for path in plots)
    lines.append("")
    output.write_text("\n".join(lines))
    print(f"[make_report] wrote {output}")


if __name__ == "__main__":
    main()
