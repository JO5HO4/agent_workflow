# Agent Operating Guide

This repository is designed so an AI/Codex agent can iterate on analysis code while Snakemake remains the stable execution harness.
The role of an agent is to develop analysis scripts, leaving execution for the user via Snakemake

## Editable Surface

Agents may edit:

- `runs/<analysis>/<workflow>/scripts/` during a run

Agents may read:
- analyis json
- snakefile
- rules
- scripts
- envs

## Expected Loop

1. The agent inspects all scripts/files it is allowed to read `workflow/scripts/`
2. The agent modifies analysis scripts.
3. The user runs the full workflow locally or on batch.
4. The agent reviews the staged outputs in the work directory, `results/summary/`, `results/validation/`, `logs/`, and the edited code, then proposes or makes the next iteration.