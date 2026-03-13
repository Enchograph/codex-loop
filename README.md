# Codex Loop

Codex Loop is a CLI-first toolkit for running Codex relay development with a canonical project-document workflow:

1. Prepare or refine the canonical project document.
2. Generate the formal relay documentation system.
3. Start a supervised Codex development loop after the documentation system is ready.

English is the default documentation language, but the user can choose whether the full AI-fed workflow should use `en` or `zh-CN`. A full Chinese mirror is available in [README.zh-CN.md](README.zh-CN.md).

## What It Supports

- Blank repositories where the user starts from a requirements document.
- Existing code repositories that need a Codex handoff documentation system.
- Repositories that already have relay docs and only need validation, normalization, and runtime setup.
- Cross-platform usage on Windows, macOS, and Linux through Python 3.11+.

## Important Rule

Users should provide their own project document whenever they have one. That document is an input, not the direct execution baseline.

The most important development foundation is the canonical project document generated or refined by Codex after repeated clarification. During autonomous execution, Codex must still re-read the user's original source document at the start of every round to avoid drift.

## Install

```bash
python -m pip install -e .[dev]
```

## Quick Start

Generate docs for an empty repository:

```bash
codex-loop init blank --repo /path/to/repo --requirements-doc /path/to/requirements.md
```

Prepare the canonical project doc for an existing code repository:

```bash
codex-loop plan-docs --repo /path/to/repo --requirements-doc /path/to/original-user-doc.md --input-doc /path/to/your-project-doc.md
codex-loop plan-docs --repo /path/to/repo --ai-doc-language zh-CN
```

Generate formal relay docs for an existing code repository after the canonical project doc is confirmed:

```bash
codex-loop init existing-code --repo /path/to/repo --ai-doc-language zh-CN
```

Start the supervised loop after the docs are ready:

```bash
codex-loop run --config /path/to/repo/codex-loop.json
codex-loop run --config /path/to/repo/codex-loop.json --sandbox-mode danger-full-access --approval-policy never
```

## Generated Documents

The formal relay-doc step generates or normalizes:

- `codex-loop-docs/en/AI-START-HERE.md`
- `codex-loop-docs/en/AI-MASTER-PROMPT.md`
- `codex-loop-docs/en/PROJECT-ROADMAP.md`
- `codex-loop-docs/en/PROJECT-TODO.md`
- `codex-loop-docs/en/PROJECT-STATUS.md`
- `codex-loop-docs/en/PROJECT-HANDOFF.md`
- `codex-loop-docs/en/PROJECT-DECISIONS.md`
- `codex-loop-docs/en/PROJECT-ACCEPTANCE.md`
- `codex-loop-docs/en/PROJECT-FILE-MAP.md`
- `codex-loop-docs/en/PROJECT-CHANGELOG.md`
- `codex-loop-docs/en/PROJECT-DESIGN.md`
- `codex-loop-docs/en/PROJECT-TASK-BREAKDOWN.md`
- `codex-loop-docs/requirements/USER-REQUIREMENTS.md`
- `codex-loop-docs/project/PROJECT-BRIEF.md`
- `codex-loop-docs/project/PLAN-MODE-PROMPT.md`
- `codex-loop-docs/project/PROJECT-DOC-QUESTIONS.md`
- `codex-loop-docs/project/PROJECT-DOC-STATUS.md`
- mirrored Chinese docs under `codex-loop-docs/zh-CN/`

## Commands

- `codex-loop plan-docs`
- `codex-loop init [blank|existing-code|existing-docs|auto]`
- `codex-loop inspect`
- `codex-loop run`

For `existing-code`, `init` will stop with guidance if the canonical project document is missing.

## Runtime Config

The generated `codex-loop.json` keeps compatibility with the earlier shell-based loop while adding a more flexible `codex_command` field.

Important fields:

- `ai_docs_language`: which document language is fed to AI through the workflow, `en` or `zh-CN`
- `codex_bin`: simple executable name, for example `codex`
- `codex_command`: optional array form when you need a full launcher command
- `workdir`: target repository root
- `prompt`: prompt passed to `codex exec`
- `total_timeout_minutes`: total wall-clock budget for the loop
- `max_rounds`: optional hard cap for testing or controlled sessions
- `log_dir`: optional override, defaults to `workdir/.codex/log`
- `sandbox_mode`: runtime sandbox choice, matching the original supervised-loop options
- `approval_policy`: runtime approval mode, matching the original supervised-loop options
- `search_enabled`: whether web search is enabled in the runtime loop
- `skip_git_repo_check`: whether Codex skips its initial git repo check

## Runtime Permission Selection

Before starting the third stage, the user can choose the Codex runtime permission model through the same core options used by the original script:

- `sandbox_mode`: `read-only`, `workspace-write`, `danger-full-access`
- `approval_policy`: `never`, `on-failure`, `on-request`, `untrusted`
- `search_enabled`
- `skip_git_repo_check`

You can set defaults during `init`, and you can still override them right before `run`.

## Cross-Platform Entry Points

Wrapper scripts are provided in [`scripts/`](scripts):

- `scripts/codex-loop.sh`
- `scripts/codex-loop.ps1`
- `scripts/codex-loop.bat`

The recommended interface remains the Python-installed `codex-loop` command.

## Project Docs

- [Usage Guide](codex-loop-docs/en/USAGE.md)
- [Repository Structure](codex-loop-docs/en/REPOSITORY-STRUCTURE.md)
- [Methodology](codex-loop-docs/en/METHODOLOGY.md)
- [Contributing](codex-loop-docs/en/CONTRIBUTING.md)
