import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def describe_input(path: Path) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "sample_group": path.parent.name,
        "suffix": path.suffix,
        "size_bytes": path.stat().st_size,
    }


def main() -> None:
    analysis_config_path = Path(snakemake.input.analysis_config)
    data_path = Path(snakemake.input.data)
    analysis = json.loads(analysis_config_path.read_text())

    metadata = analysis.get("analysis_metadata", {})
    payload = {
        "stage": "event_selection",
        "status": "ok",
        "file_id": str(snakemake.params.file_id),
        "analysis_config": analysis_config_path.as_posix(),
        "analysis_short_name": metadata.get("analysis_short_name"),
        "input_file_count": 1,
        "input_files": [describe_input(data_path)],
        "preselection": analysis.get("retrieval_features", {}).get("event_preselection", {}),
    }
    validation = {
        "stage": "event_selection",
        "valid": True,
        "checks": {
            "analysis_config_exists": analysis_config_path.exists(),
            "input_file_exists": data_path.exists(),
            "input_files_processed": 1,
        },
    }

    write_json(snakemake.output.summary, payload)
    write_json(snakemake.output.validation, validation)


if __name__ == "__main__":
    main()
