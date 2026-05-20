from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_parent(path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def main() -> None:
    cfg: dict[str, Any] = snakemake.config
    output = ensure_parent(snakemake.output[0])
    input_dir = Path(cfg["paths"]["input_dir"])
    samples = cfg["samples"]

    print(f"[build_file_manifest] input_dir={input_dir}")
    entries = []
    for sample, meta in samples.items():
        for rel_file in meta.get("files", []):
            path = input_dir / rel_file
            entries.append(
                {
                    "sample": sample,
                    "sample_type": meta["type"],
                    "path": str(path),
                    "exists": path.exists(),
                    "status": "placeholder",
                }
            )
            print(f"[build_file_manifest] sample={sample} file={path} exists={path.exists()}")

    payload = {
        "status": "placeholder",
        "analysis": cfg["analysis"]["name"],
        "input_dir": str(input_dir),
        "files": entries,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[build_file_manifest] wrote {output}")


if __name__ == "__main__":
    main()
