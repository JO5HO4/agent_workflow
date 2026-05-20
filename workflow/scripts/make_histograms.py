from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def require_file(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Required input is missing: {candidate}")
    return candidate


def main() -> None:
    input_path = require_file(snakemake.input[0])
    output = Path(snakemake.output[0])
    output.parent.mkdir(parents=True, exist_ok=True)
    sample = snakemake.wildcards.sample
    region = snakemake.wildcards.region
    systematic = snakemake.wildcards.systematic
    variable = snakemake.wildcards.variable
    cfg: dict[str, Any] = snakemake.config
    variable_cfg = cfg["variables"][variable]
    binning = variable_cfg["binning"]

    print(f"[make_histograms] sample={sample} region={region} systematic={systematic} variable={variable}")
    df = pd.read_parquet(input_path)
    if variable not in df.columns:
        raise KeyError(f"Variable {variable!r} not found in {input_path}. Available columns: {list(df.columns)}")

    weights = df["weight"].to_numpy(dtype=float) if "weight" in df else np.ones(len(df))
    if systematic == "weight_up":
        weights = weights * 1.05
    elif systematic == "weight_down":
        weights = weights * 0.95

    counts, edges = np.histogram(
        df[variable].to_numpy(dtype=float),
        bins=int(binning["bins"]),
        range=(float(binning["low"]), float(binning["high"])),
        weights=weights,
    )
    payload = {
        "status": "placeholder",
        "sample": sample,
        "region": region,
        "systematic": systematic,
        "variable": variable,
        "counts": counts.tolist(),
        "bin_edges": edges.tolist(),
        "entries": int(len(df)),
    }
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[make_histograms] wrote {output}")


if __name__ == "__main__":
    main()
