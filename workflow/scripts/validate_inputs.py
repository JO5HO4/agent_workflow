from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def require_file(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Required input is missing: {candidate}")
    return candidate


def main() -> None:
    manifest_path = require_file(snakemake.input.manifest)
    output = Path(snakemake.output[0])
    output.parent.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = json.loads(manifest_path.read_text())
    missing = [entry for entry in manifest["files"] if not entry["exists"]]
    print(f"[validate_inputs] manifest={manifest_path} missing_files={len(missing)}")

    payload = {
        "status": "placeholder",
        "valid": True,
        "strict_validation": False,
        "missing_files": missing,
        "message": "Placeholder validation records missing files but does not fail until real input policy is enabled.",
    }
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[validate_inputs] wrote {output}")


if __name__ == "__main__":
    main()
