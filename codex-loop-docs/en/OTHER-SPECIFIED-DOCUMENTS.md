## Other Specified Documents

## Generated Documents

The formal documentation generation stage generates or normalizes the following documents:

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
- Chinese mirrored documents under `codex-loop-docs/zh-CN/`

## Commands

- `codex-loop plan-docs`
- `codex-loop init [blank|existing-code|existing-docs|auto]`
- `codex-loop inspect`
- `codex-loop run`

For `existing-code`, if the canonical project document is missing, `init` stops and provides a clear prompt.

## Runtime Configuration

The generated `codex-loop.json` remains compatible with the earlier shell-based workflow while adding a more flexible `codex_command` field.

Important fields:

- `ai_docs_language`: the document language fed to AI through the whole workflow, supporting `en` and `zh-CN`
- `codex_bin`: a simple executable name, such as `codex`
- `codex_command`: an optional array form, suitable for a complete startup command
- `workdir`: the target repository root directory
- `prompt`: the prompt passed to `codex exec`
- `total_timeout_minutes`: the total time budget for the whole loop
- `max_rounds`: an optional round limit, suitable for testing or controlled runs
- `log_dir`: an optional log directory, defaulting to `workdir/.codex/log`
- `sandbox_mode`: the runtime sandbox mode, corresponding to the permission options from the original script
- `approval_policy`: the runtime approval mode, corresponding to the permission options from the original script
- `search_enabled`: whether web search is enabled during the loop
- `skip_git_repo_check`: whether to skip Codex's initial git repository check

## Permission Selection Before the Third Stage

Before starting the third stage, the user can choose the Codex runtime permission combination just like in the original script:

- `sandbox_mode`: `read-only`, `workspace-write`, `danger-full-access`
- `approval_policy`: `never`, `on-failure`, `on-request`, `untrusted`
- `search_enabled`
- `skip_git_repo_check`

These values can be written as defaults during `init`, or temporarily overridden right before running `run`.

## Cross-Platform Entry Points

The [`scripts/`](scripts) directory provides wrapper scripts:

- `scripts/codex-loop.sh`
- `scripts/codex-loop.ps1`
- `scripts/codex-loop.bat`

The recommended main entry point is still the installed `codex-loop` command.
