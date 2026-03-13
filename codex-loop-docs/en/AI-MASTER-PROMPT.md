# AI Master Prompt

Before making code changes, follow this order:
1. Re-read the original user document to avoid drift.
2. Use the canonical project document as the direct execution baseline.
3. Check git status, branch, remote, and uncommitted changes.
4. Read PROJECT-STATUS, PROJECT-HANDOFF, PROJECT-TODO, PROJECT-ROADMAP, PROJECT-DECISIONS, and PROJECT-ACCEPTANCE.
5. Select only the smallest task whose dependencies are already satisfied.
6. After finishing one minimum task, update the status docs first and then create one git commit whose message includes the task ID.
7. If the toolchain is missing, try to install or restore it before marking the task as blocked.
