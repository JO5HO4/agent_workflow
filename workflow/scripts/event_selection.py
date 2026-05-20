from __future__ import annotations

from pathlib import Path

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

    print(f"[event_selection] sample={sample} input={input_path}")
    df = pd.read_parquet(input_path)
    selected = df[df["met"] >= 30.0].copy()
    selected["feature_placeholder"] = selected["mass"] / selected["met"].clip(lower=1.0)
    selected["status"] = "placeholder"
    selected.to_parquet(output, index=False)
    print(f"[event_selection] sample={sample} selected_rows={len(selected)} output={output}")


if __name__ == "__main__":
    main()
