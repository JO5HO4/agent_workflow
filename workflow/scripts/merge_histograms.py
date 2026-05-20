from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def require_file(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Required input is missing: {candidate}")
    return candidate


def main() -> None:
    output = Path(snakemake.output[0])
    output.parent.mkdir(parents=True, exist_ok=True)
    region = snakemake.wildcards.region
    systematic = snakemake.wildcards.systematic
    variable = snakemake.wildcards.variable
    input_paths = [require_file(path) for path in snakemake.input]

    print(f"[merge_histograms] region={region} systematic={systematic} variable={variable} inputs={len(input_paths)}")
    merged_counts: np.ndarray | None = None
    bin_edges: list[float] | None = None
    components = []
    for path in input_paths:
        payload = json.loads(path.read_text())
        counts = np.asarray(payload["counts"], dtype=float)
        merged_counts = counts if merged_counts is None else merged_counts + counts
        bin_edges = payload["bin_edges"]
        components.append({"sample": payload["sample"], "path": str(path)})

    output.write_text(
        json.dumps(
            {
                "status": "placeholder",
                "region": region,
                "systematic": systematic,
                "variable": variable,
                "counts": [] if merged_counts is None else merged_counts.tolist(),
                "bin_edges": bin_edges or [],
                "components": components,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"[merge_histograms] wrote {output}")


if __name__ == "__main__":
    main()
