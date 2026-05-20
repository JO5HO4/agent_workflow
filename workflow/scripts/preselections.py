from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def require_file(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Required input is missing: {candidate}")
    return candidate


def main() -> None:
    validation_path = require_file(snakemake.input.validation)
    output = Path(snakemake.output[0])
    output.parent.mkdir(parents=True, exist_ok=True)
    sample = snakemake.wildcards.sample
    cfg: dict[str, Any] = snakemake.config
    sample_meta = cfg["samples"][sample]

    print(f"[preselection] sample={sample} validation={validation_path}")
    validation = json.loads(validation_path.read_text())
    if not validation.get("valid", False):
        raise RuntimeError(f"Input validation failed for sample={sample}: {validation}")

    df = pd.DataFrame(
        [
            {
                "event": idx,
                "sample": sample,
                "sample_type": sample_meta["type"],
                "weight": 1.0,
                "n_leptons": idx % 3,
                "met": 25.0 + 20.0 * idx,
                "mass": 40.0 + 15.0 * idx,
                "status": "placeholder",
            }
            for idx in range(10)
        ]
    )
    df.to_parquet(output, index=False)
    print(f"[preselection] wrote {len(df)} placeholder rows to {output}")


if __name__ == "__main__":
    main()
