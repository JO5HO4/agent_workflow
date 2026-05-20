from __future__ import annotations

import json
from pathlib import Path


def require_file(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Required input is missing: {candidate}")
    return candidate


def main() -> None:
    input_path = require_file(snakemake.input[0])
    output = Path(snakemake.output[0])
    output.parent.mkdir(parents=True, exist_ok=True)
    variable = snakemake.wildcards.variable

    print(f"[statistical_analysis] variable={variable} input={input_path}")
    stat_input = json.loads(input_path.read_text())
    payload = {
        "status": "placeholder",
        "variable": variable,
        "input": str(input_path),
        "n_channels": len(stat_input.get("channels", [])),
        "limits": None,
        "significance": None,
        "message": "No physics fit has been performed. This placeholder only validates workflow plumbing.",
    }
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[statistical_analysis] wrote {output}")


if __name__ == "__main__":
    main()
