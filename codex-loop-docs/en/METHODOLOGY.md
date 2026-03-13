# Methodology

Codex Loop follows a relay-development model:

- The original requirements document always has the highest priority.
- The canonical project document is the direct baseline for relay-doc generation and autonomous execution.
- A user-provided project document is only an input and must be refined before it becomes canonical.
- The system separates roadmap, TODO, status, handoff, decisions, and acceptance.
- Work is organized by dependency order instead of page-by-page sequencing.
- A new Codex session must be able to recover project state from repository docs alone.
- The loop should not depend on conversational memory.
- Runtime permission settings should match the current Codex CLI rather than stale wrapper assumptions.

This repository turns that methodology into a reusable CLI and document scaffold.
