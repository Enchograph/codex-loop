# Usage Guide

## Workflow

Codex Loop is intentionally split into explicit gated stages:

1. `plan-docs`: prepare and refine the canonical project document when needed.
2. `init`: create or normalize the formal relay documentation system.
3. `run`: start the supervised Codex loop after the docs are ready.

Users can choose which language is fed to AI through the full workflow with `--ai-doc-language en` or `--ai-doc-language zh-CN`.
If the user runs `codex-loop` without extra arguments, or runs a subcommand without any extra flags, the CLI opens an interactive terminal UI to collect the needed options.

## Canonical Project Document Rule

- Users should provide their own project document whenever available.
- A user-provided project document is only an input source.
- The direct baseline for relay-doc generation and autonomous execution is the canonical project document.
- During autonomous execution, the AI must still re-read the original user document at the start of every round.

## `plan-docs`

Use this for existing-code repositories before formal doc generation.

Examples:

```bash
codex-loop plan-docs --repo /path/to/repo --requirements-doc /path/to/original-user-doc.md
codex-loop plan-docs --repo /path/to/repo --input-doc /path/to/existing-project-doc.md
codex-loop plan-docs --repo /path/to/repo --requirements-doc /path/to/original-user-doc.md --input-doc /path/to/existing-project-doc.md
codex-loop plan-docs --repo /path/to/repo --ai-doc-language zh-CN
```

Behavior:

- Copies the original user document into `codex-loop-docs/requirements/USER-REQUIREMENTS.md` when provided
- Copies any user-provided project doc into `codex-loop-docs/project/USER-PROVIDED-PROJECT-DOC.md`
- Generates `codex-loop-docs/project/PROJECT-BRIEF.md` as the canonical project doc scaffold
- Generates planning guidance files for the Plan Mode clarification phase
- Does not start implementation or autonomous execution

## `init`

Examples:

```bash
codex-loop init blank --repo /path/to/repo --requirements-doc /path/to/requirements.md
codex-loop init existing-code --repo /path/to/repo --requirements-doc /path/to/requirements.md
codex-loop init existing-docs --repo /path/to/repo
codex-loop init --repo /path/to/repo
codex-loop init existing-code --repo /path/to/repo --ai-doc-language zh-CN
```

Behavior:

- Copies the provided requirements doc into `codex-loop-docs/requirements/USER-REQUIREMENTS.md`
- Requires the canonical project document for `existing-code`
- Generates the core relay docs in English under `codex-loop-docs/en/`
- Generates mirrored Chinese docs in `codex-loop-docs/zh-CN/`
- Writes `codex-loop.json` and `codex-loop.example.json`
- Does not start the loop automatically
- Allows choosing the default third-stage runtime permissions with `--sandbox-mode`, `--approval-policy`, `--search-enabled`, and `--skip-git-repo-check`

## `inspect`

```bash
codex-loop inspect --repo /path/to/repo
```

Returns the detected scenario as JSON.

## `run`

```bash
codex-loop run --config /path/to/repo/codex-loop.json
codex-loop run --config /path/to/repo/codex-loop.json --sandbox-mode workspace-write --approval-policy on-request
```

Behavior:

- Validates the Codex executable and workdir
- Creates per-round logs under `.codex/log/`
- Runs `codex exec` repeatedly until timeout, stop signal, or `max_rounds`
- Prints the final message for each round when present
- Lets the user override the configured runtime permissions right before stage 3 starts

## Config Notes

- Use `codex_bin` for a normal executable name such as `codex`.
- Use `codex_command` when the command must include a launcher or interpreter.
- `max_rounds` is optional and useful for tests or bounded sessions.
- Use `ai_docs_language` to decide whether AI reads the English or Chinese doc set through the workflow.
- Runtime permission values follow the current Codex CLI: `sandbox_mode` is `read-only`, `workspace-write`, or `danger-full-access`; `approval_policy` is `never`, `on-failure`, `on-request`, or `untrusted`.
