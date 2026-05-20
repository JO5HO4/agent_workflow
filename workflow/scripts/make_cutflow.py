from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def require_file(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Required input is missing: {candidate}")
    return candidate


def main() -> None:
    sample = snakemake.wildcards.sample
    selected_path = require_file(snakemake.input.selected)
    category_paths = [require_file(path) for path in snakemake.input.categories]
    csv_output = Path(snakemake.output.csv)
    json_output = Path(snakemake.output.json)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.parent.mkdir(parents=True, exist_ok=True)

    print(f"[make_cutflow] sample={sample} selected={selected_path}")
    rows = [{"stage": "selected", "region": "all", "events": len(pd.read_parquet(selected_path)), "status": "placeholder"}]
    for path in category_paths:
        region = path.stem
        events = len(pd.read_parquet(path))
        rows.append({"stage": "categorized", "region": region, "events": events, "status": "placeholder"})
        print(f"[make_cutflow] sample={sample} region={region} events={events}")

    df = pd.DataFrame(rows)
    df.to_csv(csv_output, index=False)
    json_output.write_text(json.dumps({"status": "placeholder", "sample": sample, "cutflow": rows}, indent=2) + "\n")
    print(f"[make_cutflow] wrote {csv_output} and {json_output}")


if __name__ == "__main__":
    main()
