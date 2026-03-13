from __future__ import annotations

from dataclasses import dataclass

from codex_loop.i18n import BUILTIN_LANGUAGES


@dataclass(frozen=True)
class TemplateBundle:
    ai_start_here: str
    ai_master_prompt: str
    roadmap: str
    todo: str
    status: str
    handoff: str
    decisions: str
    acceptance: str
    file_map: str
    changelog: str
    runtime_prompt: str
    base_requirements: str
    canonical_project_doc: str


def _language_note(language: str) -> str:
    if language in BUILTIN_LANGUAGES:
        return language
    return f"{language} (fallback structure generated from English templates)"


def get_template_bundle(language: str) -> TemplateBundle:
    target = _language_note(language)
    if language == "zh-CN":
        return TemplateBundle(
            ai_start_here=f"""# AI-START-HERE

本项目的 AI 接力开发入口。

## 阅读顺序
1. `.codex-loop/docs/USER-REQUIREMENTS.md`
2. `.codex-loop/docs/CANONICAL-PROJECT-DOC.md`
3. `.codex-loop/docs/AI-MASTER-PROMPT.md`
4. `.codex-loop/docs/PROJECT-STATUS.md`
5. `.codex-loop/docs/PROJECT-HANDOFF.md`
6. `.codex-loop/docs/PROJECT-TODO.md`
7. `.codex-loop/docs/PROJECT-ROADMAP.md`
8. `.codex-loop/docs/PROJECT-DECISIONS.md`
9. `.codex-loop/docs/PROJECT-ACCEPTANCE.md`
10. `.codex-loop/docs/PROJECT-FILE-MAP.md`

所有新增或更新内容都应使用目标语言：`{target}`。
""",
            ai_master_prompt=f"""# AI-MASTER-PROMPT

你正在接手一个 Codex 接力开发项目。

规则：
- 每轮开始前先重读 `.codex-loop/docs/USER-REQUIREMENTS.md`
- 然后读取 `.codex-loop/docs/CANONICAL-PROJECT-DOC.md`
- 再读取状态、交接、TODO、路线、决策、验收文档
- 只做依赖已满足的最小任务项
- 完成最小任务项后更新状态文档
- 如被阻塞，先记录阻塞，再收敛到最小下一步
- 所有接力文档默认使用 `{target}`
""",
            roadmap=_roadmap_zh(),
            todo=_todo_zh(),
            status=_status_zh(),
            handoff=_handoff_zh(),
            decisions=_decisions_zh(),
            acceptance=_acceptance_zh(),
            file_map=_file_map_zh(),
            changelog="# PROJECT-CHANGELOG\n\n- 初始化文档系统。\n",
            runtime_prompt="阅读 .codex-loop/docs/AI-MASTER-PROMPT.md，严格按照其要求接手之前的成果继续完整开发。",
            base_requirements=f"# USER-REQUIREMENTS\n\n请用 `{target}` 补全项目原始需求、目标用户、边界、不做项和验收重点。\n",
            canonical_project_doc=f"# CANONICAL-PROJECT-DOC\n\n请用 `{target}` 基于仓库现状整理完整项目说明、现状、约束、阶段目标与实施准则。\n",
        )
    return TemplateBundle(
        ai_start_here=f"""# AI-START-HERE

This is the entrypoint for Codex relay development.

## Read order
1. `.codex-loop/docs/USER-REQUIREMENTS.md`
2. `.codex-loop/docs/CANONICAL-PROJECT-DOC.md`
3. `.codex-loop/docs/AI-MASTER-PROMPT.md`
4. `.codex-loop/docs/PROJECT-STATUS.md`
5. `.codex-loop/docs/PROJECT-HANDOFF.md`
6. `.codex-loop/docs/PROJECT-TODO.md`
7. `.codex-loop/docs/PROJECT-ROADMAP.md`
8. `.codex-loop/docs/PROJECT-DECISIONS.md`
9. `.codex-loop/docs/PROJECT-ACCEPTANCE.md`
10. `.codex-loop/docs/PROJECT-FILE-MAP.md`

All generated relay docs should use target language `{target}`.
""",
        ai_master_prompt=f"""# AI-MASTER-PROMPT

You are continuing a Codex relay-development repository.

Rules:
- Re-read `.codex-loop/docs/USER-REQUIREMENTS.md` before each round
- Then read `.codex-loop/docs/CANONICAL-PROJECT-DOC.md`
- Then read status, handoff, todo, roadmap, decisions, and acceptance docs
- Only pick the smallest unblocked task
- Update status docs after each completed task
- Record blockers explicitly before pausing
- Write relay docs in `{target}`
""",
        roadmap=_roadmap_en(),
        todo=_todo_en(),
        status=_status_en(),
        handoff=_handoff_en(),
        decisions=_decisions_en(),
        acceptance=_acceptance_en(),
        file_map=_file_map_en(),
        changelog="# PROJECT-CHANGELOG\n\n- Initialized the relay-document system.\n",
        runtime_prompt="Read .codex-loop/docs/AI-MASTER-PROMPT.md and continue the project strictly according to its instructions.",
        base_requirements=f"# USER-REQUIREMENTS\n\nWrite the original product requirements, audience, constraints, non-goals, and acceptance priorities in `{target}`.\n",
        canonical_project_doc=f"# CANONICAL-PROJECT-DOC\n\nWrite the canonical project document from the current repository state in `{target}`.\n",
    )


def _roadmap_en() -> str:
    return """# PROJECT-ROADMAP

## Phase 1: Shell and project structure
- Establish entrypoints, packaging, and basic runtime conventions.

## Phase 2: Domain and workflow rules
- Finalize document responsibilities, state transitions, and task sequencing.

## Phase 3: Infrastructure and execution
- Implement Codex launchers, runtime config, logging, and safety checks.

## Phase 4: Presentation and UX
- Improve CLI/TUI prompts, localization, and onboarding.

## Phase 5: QA and release
- Verify scenarios, tests, and acceptance mapping.
"""


def _todo_en() -> str:
    return """# PROJECT-TODO

| Task ID | Phase | Status | Goal | Done When |
| --- | --- | --- | --- | --- |
| T-001 | Phase 1 | pending | Define the next smallest unblocked task. | The task is specific, implementable, and verifiable. |
"""


def _status_en() -> str:
    return """# PROJECT-STATUS

- Current phase: Phase 1
- Current milestone: Bootstrap
- Completed tasks:
- In progress:
- Next priority task: T-001
- Blockers:
- Latest verification:
- Summary: Relay-document system initialized.
"""


def _handoff_en() -> str:
    return """# PROJECT-HANDOFF

- Goal of this round: Initialize the relay-document system.
- Completed this round: Generated initial docs and runtime config.
- Not completed: Project-specific task planning.
- Current blockers: None recorded.
- Next recommended action: Read the requirements docs and replace placeholders with project-specific content.
"""


def _decisions_en() -> str:
    return """# PROJECT-DECISIONS

- The original user requirements document has highest priority.
- AI state must live in repository docs, not only in prompts.
- Roadmap, todo, status, and handoff are separate documents.
- Tasks must be split into the smallest independently completable units.
"""


def _acceptance_en() -> str:
    return """# PROJECT-ACCEPTANCE

- Relay docs reflect the original requirements.
- Status and handoff clearly identify the next task.
- The runtime loop can start from the generated prompt/config without manual reconstruction.
"""


def _file_map_en() -> str:
    return """# PROJECT-FILE-MAP

- `.codex-loop/docs/AI-START-HERE.md`: entrypoint for new Codex sessions.
- `.codex-loop/docs/AI-MASTER-PROMPT.md`: fixed execution rules.
- `.codex-loop/docs/USER-REQUIREMENTS.md`: authoritative user requirements document.
- `.codex-loop/docs/CANONICAL-PROJECT-DOC.md`: canonical project document.
- `.codex-loop/docs/PROJECT-*.md`: roadmap, todo, status, handoff, decisions, acceptance, file map, changelog.
- `.codex-loop/config/codex-loop.json`: runtime configuration.
- `.codex-loop/log/`: runtime logs.
"""


def _roadmap_zh() -> str:
    return """# PROJECT-ROADMAP

## Phase 1：应用壳层与项目结构
- 建立入口、打包方式和基础运行约定。

## Phase 2：领域与流程规则
- 固化文档职责、状态流转和任务顺序。

## Phase 3：基础设施与执行
- 实现 Codex 启动器、运行配置、日志与安全校验。

## Phase 4：表现层与交互
- 完善 CLI/TUI 提示、本地化与引导流程。

## Phase 5：QA 与发布
- 验证场景、测试与验收映射。
"""


def _todo_zh() -> str:
    return """# PROJECT-TODO

| Task ID | Phase | Status | Goal | Done When |
| --- | --- | --- | --- | --- |
| T-001 | Phase 1 | pending | 定义下一个最小且无阻塞的任务。 | 任务足够具体，可实施且可验证。 |
"""


def _status_zh() -> str:
    return """# PROJECT-STATUS

- 当前阶段：Phase 1
- 当前里程碑：Bootstrap
- 已完成任务：
- 正在进行：
- 下一个唯一优先任务：T-001
- 当前阻塞：
- 最近验证：
- 摘要：接力文档系统已初始化。
"""


def _handoff_zh() -> str:
    return """# PROJECT-HANDOFF

- 本轮目标：初始化接力文档系统。
- 本轮完成：已生成初始文档和运行配置。
- 未完成：项目专属任务拆解。
- 当前阻塞：暂无记录。
- 下一步推荐动作：阅读需求文档并将占位内容替换为项目真实内容。
"""


def _decisions_zh() -> str:
    return """# PROJECT-DECISIONS

- 用户原始需求文档优先级最高。
- AI 状态必须落在仓库文档中，而不是只存在于提示词里。
- 路线、TODO、状态、交接必须分离。
- 任务必须拆分到可独立完成和提交的最小粒度。
"""


def _acceptance_zh() -> str:
    return """# PROJECT-ACCEPTANCE

- 接力文档能覆盖原始需求。
- 状态与交接文档能明确指出下一个任务。
- 运行循环可直接基于生成的提示词和配置启动，无需手工重建。
"""


def _file_map_zh() -> str:
    return """# PROJECT-FILE-MAP

- `.codex-loop/docs/AI-START-HERE.md`：新 Codex 会话入口。
- `.codex-loop/docs/AI-MASTER-PROMPT.md`：固定执行规则。
- `.codex-loop/docs/USER-REQUIREMENTS.md`：唯一用户需求文档。
- `.codex-loop/docs/CANONICAL-PROJECT-DOC.md`：规范项目文档。
- `.codex-loop/docs/PROJECT-*.md`：路线、TODO、状态、交接、决策、验收、文件地图、变更日志。
- `.codex-loop/config/codex-loop.json`：运行配置。
- `.codex-loop/log/`：运行日志。
"""
