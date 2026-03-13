# Plan Mode Prompt

Use Codex Plan Mode to refine this repository into a complete, ambiguity-free project document before implementation.

- Scenario: `existing-docs`
- Target AI document language for the full workflow: `zh-CN`
- Read the codebase, `codex-loop-docs/requirements/USER-REQUIREMENTS.md`, and `codex-loop-docs/project/USER-PROVIDED-PROJECT-DOC.md` if present.
- Continuously question the user until `codex-loop-docs/project/PROJECT-BRIEF.md` is detailed enough to act as the canonical project document.
- Do not start automatic development during this phase.
- The project document is the most important development foundation.
