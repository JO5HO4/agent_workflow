from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


def require_file(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Required input is missing: {candidate}")
    return candidate


def main() -> None:
    input_path = require_file(snakemake.input[0])
    png_output = Path(snakemake.output.png)
    pdf_output = Path(snakemake.output.pdf)
    png_output.parent.mkdir(parents=True, exist_ok=True)
    pdf_output.parent.mkdir(parents=True, exist_ok=True)
    hist = json.loads(input_path.read_text())
    region = getattr(snakemake.wildcards, "region", hist.get("region", "unknown_region"))
    variable = getattr(snakemake.wildcards, "variable", hist.get("variable", "unknown_variable"))
    print(f"[make_plots] region={region} variable={variable} input={input_path}")
    edges = hist["bin_edges"]
    counts = hist["counts"]
    centers = [(low + high) / 2.0 for low, high in zip(edges[:-1], edges[1:])]
    widths = [high - low for low, high in zip(edges[:-1], edges[1:])]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(centers, counts, align="center", width=widths, edgecolor="black", linewidth=0.8)
    ax.set_title(f"{region} - {variable} (placeholder)")
    ax.set_xlabel(variable)
    ax.set_ylabel("Weighted events")
    ax.text(0.02, 0.95, "status: placeholder", transform=ax.transAxes, va="top")
    fig.tight_layout()
    fig.savefig(png_output)
    fig.savefig(pdf_output)
    plt.close(fig)
    print(f"[make_plots] wrote {png_output} and {pdf_output}")


if __name__ == "__main__":
    main()
