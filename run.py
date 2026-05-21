import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing config: {path}")
    return json.loads(path.read_text())


def build_command(workflow_config: dict[str, Any], target: str | None, dry_run: bool) -> list[str]:
    snakemake_config = workflow_config.get("snakemake", {})
    command = [
        "snakemake",
        "--snakefile",
        "workflow/Snakefile",
        "--cores",
        str(snakemake_config.get("cores", 1)),
    ]

    if snakemake_config.get("use_conda", False):
        command.append("--use-conda")
    if dry_run or snakemake_config.get("dry_run", False):
        command.append("--dry-run")

    command.extend(str(item) for item in snakemake_config.get("config", []))
    command.append(target or workflow_config.get("loop", {}).get("target", "all"))
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the ATLAS analysis Snakemake workflow.")
    parser.add_argument("--workflow-config", default="configs/workflow.json")
    parser.add_argument("--analysis-config", default="configs/analysis/vlq.json")
    parser.add_argument("--target", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workflow_config_path = Path(args.workflow_config)
    analysis_config_path = Path(args.analysis_config)
    workflow_config = load_json(workflow_config_path)
    load_json(analysis_config_path)

    env = os.environ.copy()
    env["ATLAS_WORKFLOW_CONFIG"] = workflow_config_path.as_posix()
    env["ATLAS_ANALYSIS_CONFIG"] = analysis_config_path.as_posix()
    env.setdefault("XDG_CACHE_HOME", str(Path(".snakemake/cache").resolve()))

    command = build_command(workflow_config, args.target, args.dry_run)
    print(" ".join(command))
    return subprocess.run(command, env=env, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
