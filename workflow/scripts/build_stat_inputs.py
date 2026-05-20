from __future__ import annotations

import json
from pathlib import Path


def require_file(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Required input is missing: {candidate}")
    return candidate


def main() -> None:
    output = Path(snakemake.output[0])
    output.parent.mkdir(parents=True, exist_ok=True)
    variable = snakemake.wildcards.variable
    input_paths = [require_file(path) for path in snakemake.input]

    print(f"[build_stat_inputs] variable={variable} inputs={len(input_paths)}")
    channels = []
    for path in input_paths:
        hist = json.loads(path.read_text())
        channels.append(
            {
                "region": hist["region"],
                "systematic": hist["systematic"],
                "variable": hist["variable"],
                "histogram": str(path),
                "status": "placeholder",
            }
        )

    payload = {
        "status": "placeholder",
        "variable": variable,
        "format": "analysis-placeholder-json",
        "channels": channels,
        "message": "Replace with pyhf/HistFactory/datacard construction for real fits.",
    }
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[build_stat_inputs] wrote {output}")


if __name__ == "__main__":
    main()
