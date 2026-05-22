import json
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    summaries = [read_json(path) for path in snakemake.input.summaries]
    validations = [read_json(path) for path in snakemake.input.validations]
    input_files = [
        input_file
        for summary in summaries
        for input_file in summary.get("input_files", [])
    ]

    payload = {
        "stage": "event_selection",
        "status": "ok",
        "input_file_count": len(input_files),
        "input_files": input_files,
        "file_summaries": [str(path) for path in snakemake.input.summaries],
    }
    validation = {
        "stage": "event_selection",
        "valid": all(item.get("valid", False) for item in validations),
        "checks": {
            "per_file_jobs": len(summaries),
            "per_file_validations": len(validations),
            "input_files_processed": len(input_files),
        },
    }

    write_json(snakemake.output.summary, payload)
    write_json(snakemake.output.validation, validation)


if __name__ == "__main__":
    main()
