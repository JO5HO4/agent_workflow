"""Run the Codex and Snakemake analysis loop.

Each loop iteration has its own directory under ``workflow.work_dir``:

1. Copy a workflow into ``iteration<N>/workflow``.
2. Ask Codex to edit only that copied workflow's scripts.
3. Run Snakemake on the copied workflow and save outputs in the same iteration.

Iteration 0 starts from the repository's template workflow and uses
``codex.prompt``. Later iterations start from the previous iteration's edited
workflow and use ``codex.revise``.
"""

import argparse
import copy
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_ANALYSIS_CONFIG = "configs/analysis/vlq.json"
DEFAULT_TASK_PROMPT = "prompts/task.md"
DEFAULT_REVISE_PROMPT = "prompts/revise.md"
DEFAULT_WORKFLOW_CONFIG = "configs/workflow.json"
TEMPLATE_WORKFLOW_DIR = "workflow"

CODEX_GUARDRAILS = """
You are working in a staged Snakemake script directory.
Modify files in this directory only. Do not edit the staged Snakefile, rules, envs,
workflow config, analysis config, prompts, or template workflow files.
You may read parent directories when you need workflow context.
""".strip()


def parse_args() -> argparse.Namespace:
    """Read command-line options for one loop run."""
    parser = argparse.ArgumentParser(description="Run Codex edits followed by Snakemake.")
    parser.add_argument("--workflow-config", default=DEFAULT_WORKFLOW_CONFIG)
    parser.add_argument("--analysis-config", default=DEFAULT_ANALYSIS_CONFIG)
    parser.add_argument("--target", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-codex", action="store_true")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    """Load a JSON file and fail with a clear path if it is missing."""
    if not path.exists():
        raise FileNotFoundError(f"Missing config: {path}")
    return json.loads(path.read_text())


def require_iterations(workflow_config: dict[str, Any]) -> int:
    """Return the configured loop count after a small sanity check."""
    iterations = int(workflow_config.get("loop", {}).get("iterations", 1))
    if iterations < 1:
        raise ValueError("loop.iterations must be at least 1")
    return iterations


def resolve_config_path(repo_root: Path, configured_path: str) -> Path:
    """Resolve config and prompt paths relative to this checkout."""
    return (repo_root / configured_path).resolve()


def iteration_dir(repo_root: Path, workflow_config: dict[str, Any], index: int) -> Path:
    """Return ``workflow.work_dir/iteration<N>`` for one loop iteration."""
    work_dir = workflow_config.get("workflow", {}).get("work_dir")
    if not work_dir:
        raise ValueError("workflow.work_dir is required in the workflow config")
    return resolve_config_path(repo_root, str(work_dir)) / f"iteration{index}"


def stage_workflow(source_workflow: Path, iteration_dir: Path) -> Path:
    """Copy a workflow into an empty iteration directory."""
    if iteration_dir.exists():
        shutil.rmtree(iteration_dir)

    staged_workflow = iteration_dir / "workflow"
    iteration_dir.mkdir(parents=True)
    shutil.copytree(source_workflow, staged_workflow)
    return staged_workflow


def write_iteration_config(
    workflow_config: dict[str, Any], iteration_dir: Path
) -> Path:
    """Write the config Snakemake will use for one iteration.

    The repository config names the parent work directory, such as ``runs/``.
    The staged config points Snakemake at the concrete iteration directory so
    results and logs do not mix across iterations.
    """
    iteration_config = copy.deepcopy(workflow_config)
    iteration_config["workflow"]["work_dir"] = iteration_dir.as_posix()

    config_path = iteration_dir / "workflow.json"
    config_path.write_text(json.dumps(iteration_config, indent=2) + "\n")
    return config_path


def make_iteration_env(
    repo_root: Path, iteration_config: Path, analysis_config: Path
) -> dict[str, str]:
    """Build the environment expected by the staged Snakefile."""
    env = os.environ.copy()
    env["ATLAS_WORKFLOW_CONFIG"] = iteration_config.as_posix()
    env["ATLAS_ANALYSIS_CONFIG"] = analysis_config.as_posix()
    env.setdefault("XDG_CACHE_HOME", str((repo_root / ".snakemake/cache").resolve()))
    return env


def prompt_path_for_iteration(
    repo_root: Path, codex_config: dict[str, Any], index: int
) -> Path:
    """Use the task prompt once, then the revise prompt."""
    config_key = "prompt" if index == 0 else "revise"
    default_prompt = DEFAULT_TASK_PROMPT if index == 0 else DEFAULT_REVISE_PROMPT
    return resolve_config_path(repo_root, str(codex_config.get(config_key, default_prompt)))


def build_codex_prompt(
    prompt_path: Path, index: int, previous_iteration: Path | None
) -> str:
    """Add loop context and edit boundaries to a configured prompt file."""
    if not prompt_path.exists():
        raise FileNotFoundError(f"Missing Codex prompt: {prompt_path}")

    context = [f"This is iteration {index}."]
    if previous_iteration is not None:
        context.extend(
            [
                "The scripts in this directory were copied from the previous iteration.",
                f"Review previous results and logs under {previous_iteration.as_posix()} before revising.",
            ]
        )

    prompt_parts = [
        prompt_path.read_text().strip(),
        "\n".join(context),
        CODEX_GUARDRAILS,
    ]
    return "\n\n".join(prompt_parts) + "\n"


def build_codex_command(codex_config: dict[str, Any], scripts_dir: Path) -> list[str]:
    """Build ``codex exec`` from the small Codex config section."""
    command = ["codex", "exec", "--cd", scripts_dir.as_posix()]

    configured_flags = {
        "model": "--model",
        "sandbox": "--sandbox",
        "ask_for_approval": "--ask-for-approval",
    }
    for config_key, flag in configured_flags.items():
        if codex_config.get(config_key):
            command.extend([flag, str(codex_config[config_key])])

    if codex_config.get("reasoning_effort"):
        effort = codex_config["reasoning_effort"]
        command.extend(["--config", f'model_reasoning_effort="{effort}"'])

    # "-" tells Codex to read the prompt text from stdin.
    command.append("-")
    return command


def run_codex(
    repo_root: Path,
    codex_config: dict[str, Any],
    staged_workflow: Path,
    prompt: str,
    index: int,
    env: dict[str, str],
) -> int:
    """Let Codex edit one staged scripts directory."""
    scripts_dir = staged_workflow / "scripts"
    command = build_codex_command(codex_config, scripts_dir)
    print(f"Iteration {index} Codex: {shlex.join(command)}", flush=True)
    try:
        return subprocess.run(
            command,
            cwd=repo_root,
            env=env,
            input=prompt,
            text=True,
            check=False,
        ).returncode
    except FileNotFoundError:
        print("Cannot run Codex: `codex` is not on PATH.", file=sys.stderr)
        return 127


def build_snakemake_command(
    workflow_config: dict[str, Any], snakefile: Path, target: str | None, dry_run: bool
) -> list[str]:
    """Build the Snakemake command for one staged workflow."""
    snakemake_config = workflow_config.get("snakemake", {})
    command = [
        "snakemake",
        "--snakefile",
        snakefile.as_posix(),
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


def run_snakemake(
    repo_root: Path,
    workflow_config: dict[str, Any],
    staged_workflow: Path,
    target: str | None,
    dry_run: bool,
    index: int,
    env: dict[str, str],
) -> int:
    """Run Snakemake after Codex finishes one iteration."""
    command = build_snakemake_command(
        workflow_config, staged_workflow / "Snakefile", target, dry_run
    )
    print(f"Iteration {index} Snakemake: {shlex.join(command)}", flush=True)
    try:
        return subprocess.run(command, cwd=repo_root, env=env, check=False).returncode
    except FileNotFoundError:
        print("Cannot run Snakemake: `snakemake` is not on PATH.", file=sys.stderr)
        return 127


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent

    workflow_config_path = resolve_config_path(repo_root, args.workflow_config)
    analysis_config_path = resolve_config_path(repo_root, args.analysis_config)
    workflow_config = read_json(workflow_config_path)
    read_json(analysis_config_path)

    iterations = require_iterations(workflow_config)
    codex_config = workflow_config.get("codex", {})

    # These move forward after every successful iteration.
    # Iteration 0 starts from the template; later iterations copy the edited copy.
    source_workflow = repo_root / TEMPLATE_WORKFLOW_DIR
    previous_iteration: Path | None = None

    for index in range(iterations):
        current_iteration = iteration_dir(repo_root, workflow_config, index)
        staged_workflow = stage_workflow(source_workflow, current_iteration)
        iteration_config = write_iteration_config(workflow_config, current_iteration)
        env = make_iteration_env(repo_root, iteration_config, analysis_config_path)

        if not args.skip_codex:
            prompt_path = prompt_path_for_iteration(repo_root, codex_config, index)
            prompt = build_codex_prompt(prompt_path, index, previous_iteration)
            returncode = run_codex(
                repo_root, codex_config, staged_workflow, prompt, index, env
            )
            if returncode != 0:
                return returncode

        returncode = run_snakemake(
            repo_root,
            workflow_config,
            staged_workflow,
            args.target,
            args.dry_run,
            index,
            env,
        )
        if returncode != 0:
            return returncode

        previous_iteration = current_iteration
        source_workflow = staged_workflow

    return 0


if __name__ == "__main__":
    sys.exit(main())
