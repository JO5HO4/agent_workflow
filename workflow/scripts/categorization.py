from __future__ import annotations

from pathlib import Path
from typing import Any

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
    cfg: dict[str, Any] = snakemake.config
    selection = cfg["regions"][region]["selection"]

    print(f"[categorization] sample={sample} region={region} selection={selection!r}")
    df = pd.read_parquet(input_path)
    try:
        categorized = df.query(selection).copy()
    except Exception as exc:
        raise RuntimeError(f"Failed to evaluate selection for region={region}: {selection}") from exc

    categorized["region"] = region
    categorized["status"] = "placeholder"
    categorized.to_parquet(output, index=False)
    print(f"[categorization] sample={sample} region={region} rows={len(categorized)} output={output}")


if __name__ == "__main__":
    main()
