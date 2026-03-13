# Project Decisions

- Primary workflow: `plan-docs` to refine the canonical project document, `init` to generate relay docs, and `run` to start the supervised Codex loop.
- Original user document: `codex-loop-docs/requirements/USER-REQUIREMENTS.md`
- Canonical project document: `codex-loop-docs/project/PROJECT-BRIEF.md`
- User-provided project doc input: `codex-loop-docs/project/USER-PROVIDED-PROJECT-DOC.md`
- AI document language: `en`
- Scenario type: Repository with an existing docs system
- Default rule: Re-read the original user document at the start of every round.
- Direct execution baseline: always use the canonical project document, never the raw uploaded document.
- Commit rule: One minimum task per commit, and the commit message must include the task ID.
- Toolchain rule: Attempt self-repair or installation before declaring a blocker.
