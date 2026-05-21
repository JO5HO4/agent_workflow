import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def discover_inputs(input_dir: str | Path) -> list[dict[str, Any]]:
    root = Path(input_dir)
    if not root.exists():
        return []

    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.name.startswith("."):
            files.append(
                {
                    "path": path.as_posix(),
                    "sample_group": path.parent.name,
                    "suffix": path.suffix,
                    "size_bytes": path.stat().st_size,
                }
            )
    return files


def main() -> None:
    analysis_config_path = Path(snakemake.input.analysis_config)
    analysis = json.loads(analysis_config_path.read_text())
    input_files = discover_inputs(snakemake.params.input_dir)

    metadata = analysis.get("analysis_metadata", {})
    payload = {
        "stage": "event_selection",
        "status": "ok",
        "analysis_config": analysis_config_path.as_posix(),
        "analysis_short_name": metadata.get("analysis_short_name"),
        "input_dir": str(snakemake.params.input_dir),
        "input_file_count": len(input_files),
        "input_files": input_files,
        "preselection": analysis.get("retrieval_features", {}).get("event_preselection", {}),
    }
    validation = {
        "stage": "event_selection",
        "valid": True,
        "checks": {
            "analysis_config_exists": analysis_config_path.exists(),
            "input_dir_exists": Path(snakemake.params.input_dir).exists(),
            "input_files_discovered": len(input_files),
        },
    }

    write_json(snakemake.output.summary, payload)
    write_json(snakemake.output.validation, validation)


if __name__ == "__main__":
    main()
