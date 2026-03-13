from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent

REQUIRED_CORE_DOCS = [
    "AI-START-HERE.md",
    "AI-MASTER-PROMPT.md",
    "PROJECT-ROADMAP.md",
    "PROJECT-TODO.md",
    "PROJECT-STATUS.md",
    "PROJECT-HANDOFF.md",
    "PROJECT-DECISIONS.md",
    "PROJECT-ACCEPTANCE.md",
    "PROJECT-FILE-MAP.md",
    "PROJECT-CHANGELOG.md",
    "PROJECT-DESIGN.md",
    "PROJECT-TASK-BREAKDOWN.md",
]


@dataclass(frozen=True)
class TemplateContext:
    scenario: str
    project_name: str
    requirements_doc: str
    canonical_project_doc: str
    file_map: str
    current_state: str
    design_seed: str
    workflow_stage: str
    ai_docs_language: str


def ai_docs_dir(language: str) -> str:
    if language == "zh-CN":
        return "codex-loop-docs/zh-CN"
    return "codex-loop-docs/en"


def scenario_label(scenario: str, language: str) -> str:
    labels = {
        "en": {
            "blank": "Blank repository",
            "existing-code": "Existing code repository",
            "existing-docs": "Repository with an existing docs system",
        },
        "zh": {
            "blank": "空白仓库",
            "existing-code": "已有代码仓库",
            "existing-docs": "已具备文档体系的仓库",
        },
    }
    return labels[language][scenario]


def base_prompt(language: str) -> str:
    if language == "zh":
        return dedent(
            """
            在开始任何编码前，严格按以下顺序执行：
            1. 重读用户原始文档，避免偏离方向。
            2. 以 canonical 项目文档作为直接执行基底。
            3. 检查 git 状态、分支、远端和未提交改动。
            4. 依次读取 PROJECT-STATUS、PROJECT-HANDOFF、PROJECT-TODO、PROJECT-ROADMAP、PROJECT-DECISIONS、PROJECT-ACCEPTANCE。
            5. 只选择依赖已满足的最小任务项。
            6. 完成一个最小任务项后，先更新状态文档，再提交一次 git commit，commit message 必须包含任务 ID。
            7. 若缺少工具链，优先自行补齐；只有补齐失败时才将任务标记为 blocked。
            """
        ).strip()
    return dedent(
        """
        Before making code changes, follow this order:
        1. Re-read the original user document to avoid drift.
        2. Use the canonical project document as the direct execution baseline.
        3. Check git status, branch, remote, and uncommitted changes.
        4. Read PROJECT-STATUS, PROJECT-HANDOFF, PROJECT-TODO, PROJECT-ROADMAP, PROJECT-DECISIONS, and PROJECT-ACCEPTANCE.
        5. Select only the smallest task whose dependencies are already satisfied.
        6. After finishing one minimum task, update the status docs first and then create one git commit whose message includes the task ID.
        7. If the toolchain is missing, try to install or restore it before marking the task as blocked.
        """
    ).strip()


def render_doc(filename: str, language: str, ctx: TemplateContext) -> str:
    if language == "zh":
        return _render_zh(filename, ctx)
    return _render_en(filename, ctx)


def _render_en(filename: str, ctx: TemplateContext) -> str:
    scenario_name = scenario_label(ctx.scenario, "en")
    selected_dir = ai_docs_dir(ctx.ai_docs_language)
    docs = {
        "AI-START-HERE.md": dedent(
            f"""
            # AI Start Here

            This is the single entry point for any new Codex session working on **{ctx.project_name}**.

            ## Read Order

            1. `{ctx.requirements_doc}`
            2. `{ctx.canonical_project_doc}`
            3. `{selected_dir}/AI-MASTER-PROMPT.md`
            4. `{selected_dir}/PROJECT-STATUS.md`
            5. `{selected_dir}/PROJECT-HANDOFF.md`
            6. `{selected_dir}/PROJECT-TODO.md`
            7. `{selected_dir}/PROJECT-ROADMAP.md`
            8. `{selected_dir}/PROJECT-DECISIONS.md`
            9. `{selected_dir}/PROJECT-ACCEPTANCE.md`
            10. `{selected_dir}/PROJECT-FILE-MAP.md`
            11. `{selected_dir}/PROJECT-DESIGN.md`
            12. `{selected_dir}/PROJECT-TASK-BREAKDOWN.md`

            ## Mandatory Checks Before Work

            - Confirm the repository scenario: **{scenario_name}**
            - The selected AI document language for the full workflow is: `{ctx.ai_docs_language}`
            - Re-read the original user document: `{ctx.requirements_doc}`
            - Use the canonical project document as the direct execution baseline: `{ctx.canonical_project_doc}`
            - Run a git status check before selecting work
            - Verify the current phase and next single priority task
            - Do not guess around recorded decisions
            """
        ).strip()
        + "\n",
        "AI-MASTER-PROMPT.md": f"# AI Master Prompt\n\n{base_prompt('en')}\n",
        "PROJECT-ROADMAP.md": dedent(
            f"""
            # Project Roadmap

            Project: **{ctx.project_name}**
            Scenario: **{scenario_name}**

            | Phase | Goal | Entry Criteria | Exit Criteria |
            | --- | --- | --- | --- |
            | 1. Discovery | Lock source requirements and architecture direction | Requirements document exists | Design baseline, decisions, and file map are recorded |
            | 2. Foundation | Establish shell, tooling, and project skeleton | Discovery outputs are complete | Core infrastructure and bootstrapping tasks are done |
            | 3. Implementation | Deliver prioritized functional slices | Foundation tasks are complete | Main product flows are implemented and verified |
            | 4. Hardening | Close gaps, test, and reduce risk | Core flows exist | Acceptance checks pass |
            | 5. Release Readiness | Prepare for handoff or release | Hardening outputs are stable | Final docs, changelog, and release notes are ready |

            ## Notes

            - Organize work by real dependency order, not by UI page names.
            - Update this roadmap only when the architecture or milestone model changes.
            - For existing-code repositories, do not enter implementation until the canonical project document is ambiguity-free.
            """
        ).strip()
        + "\n",
        "PROJECT-TODO.md": dedent(
            """
            # Project TODO

            Use one section per minimum shippable task.

            ## Task Template

            - Task ID:
            - Title:
            - Phase:
            - Depends On:
            - Status:
            - Goal:
            - Implementation Notes:
            - Done When:
            - Verification:
            - Files Expected:

            ## Initial Seed Tasks

            - Task ID: DISC-001
            - Title: Validate the source requirements and freeze the initial scope
            - Phase: Discovery
            - Depends On: None
            - Status: Pending
            - Goal: Confirm the requirements document and identify any unresolved assumptions.
            - Implementation Notes: Review source docs and update PROJECT-DECISIONS.md.
            - Done When: The source of truth and scope boundaries are recorded.
            - Verification: Requirements path and scope notes are present in the docs.
            - Files Expected: {selected_dir}/PROJECT-DECISIONS.md, {selected_dir}/PROJECT-STATUS.md
            """
        ).strip()
        + "\n",
        "PROJECT-STATUS.md": dedent(
            f"""
            # Project Status

            - Current phase: Discovery
            - Current milestone: Documentation bootstrap
            - Workflow stage: {ctx.workflow_stage}
            - Completed task IDs: None
            - In-progress task ID: DISC-001
            - Next single priority task: DISC-001
            - Current blockers: None recorded
            - Latest verification: Documentation scaffold generated by codex-loop

            ## Current State Summary

            {ctx.current_state}

            ## Risks and Drift

            - Architecture details still require project-specific confirmation.
            - TODO items are placeholders until discovery is completed.
            """
        ).strip()
        + "\n",
        "PROJECT-HANDOFF.md": dedent(
            """
            # Project Handoff

            - Round goal: Bootstrap the relay documentation system.
            - Completed in this round: Generated the initial docs set and runtime config.
            - Not completed in this round: Final user confirmation and ambiguity removal in the canonical project document.
            - Current blockers: None.
            - Updated files: Initial docs scaffold.
            - Recommended next action: Re-read the original user document, refine the canonical project document, and only then continue implementation planning.
            - Notes for the next Codex: Re-read the original user document every round before making assumptions.
            """
        ).strip()
        + "\n",
        "PROJECT-DECISIONS.md": dedent(
            f"""
            # Project Decisions

            - Primary workflow: `plan-docs` to refine the canonical project document, `init` to generate relay docs, and `run` to start the supervised Codex loop.
            - Original user document: `{ctx.requirements_doc}`
            - Canonical project document: `{ctx.canonical_project_doc}`
            - AI document language: `{ctx.ai_docs_language}`
            - Scenario type: {scenario_name}
            - Default rule: Re-read the original user document at the start of every round.
            - Direct execution baseline: always use the canonical project document, never the raw uploaded document.
            - Commit rule: One minimum task per commit, and the commit message must include the task ID.
            - Toolchain rule: Attempt self-repair or installation before declaring a blocker.
            """
        ).strip()
        + "\n",
        "PROJECT-ACCEPTANCE.md": dedent(
            """
            # Project Acceptance

            ## Global Done Definition

            - The delivered implementation maps back to the original user document.
            - The canonical project document is complete enough to remove material ambiguity.
            - The roadmap, TODO, status, and handoff docs reflect reality.
            - The repo can be handed to a new Codex session without additional human context.

            ## Milestone Acceptance

            - Discovery: requirements and architecture constraints are documented.
            - Foundation: toolchain and shell are reproducible.
            - Implementation: main functional flows meet the agreed scope.
            - Hardening: critical tests and verifications pass.
            - Release Readiness: final docs and handoff are complete.
            """
        ).strip()
        + "\n",
        "PROJECT-FILE-MAP.md": dedent(
            f"""
            # Project File Map

            ## Initial Repository Map

            {ctx.file_map}

            ## Usage Notes

            - Update this file when directories or critical ownership boundaries change.
            - Keep the map concise and focused on decision-relevant paths.
            - Include the canonical project document and original user document in future updates.
            """
        ).strip()
        + "\n",
        "PROJECT-CHANGELOG.md": dedent(
            """
            # Project Changelog

            ## 2026-03-13

            - Bootstrapped the Codex relay documentation system.
            - Added the initial roadmap, TODO, status, handoff, decisions, and acceptance docs.
            """
        ).strip()
        + "\n",
        "PROJECT-DESIGN.md": dedent(
            f"""
            # Project Design

            ## Design Seed

            {ctx.design_seed}

            ## Source Baseline

            - Canonical project document: `{ctx.canonical_project_doc}`
            - Original user document: `{ctx.requirements_doc}`

            ## Sections To Complete

            - System context
            - Primary user flows
            - Architecture layers and boundaries
            - Data contracts and integration points
            - Error handling and fallback behavior
            """
        ).strip()
        + "\n",
        "PROJECT-TASK-BREAKDOWN.md": dedent(
            """
            # Project Task Breakdown

            Convert the roadmap into minimum independently verifiable tasks.

            ## Expected Structure

            - Discovery tasks
            - Foundation tasks
            - Implementation tasks
            - Hardening tasks
            - Release readiness tasks

            ## Rule

            Every task must be small enough to complete, verify, document, and commit in one round.
            Do not create implementation tasks until the canonical project document is detailed enough to remove material ambiguity.
            """
        ).strip()
        + "\n",
    }
    return docs[filename]


def _render_zh(filename: str, ctx: TemplateContext) -> str:
    scenario_name = scenario_label(ctx.scenario, "zh")
    selected_dir = ai_docs_dir(ctx.ai_docs_language)
    docs = {
        "AI-START-HERE.md": dedent(
            f"""
            # AI 从这里开始

            这是任何新 Codex 会话接手 **{ctx.project_name}** 时的唯一入口。

            ## 阅读顺序

            1. `{ctx.requirements_doc}`
            2. `{ctx.canonical_project_doc}`
            3. `{selected_dir}/AI-MASTER-PROMPT.md`
            4. `{selected_dir}/PROJECT-STATUS.md`
            5. `{selected_dir}/PROJECT-HANDOFF.md`
            6. `{selected_dir}/PROJECT-TODO.md`
            7. `{selected_dir}/PROJECT-ROADMAP.md`
            8. `{selected_dir}/PROJECT-DECISIONS.md`
            9. `{selected_dir}/PROJECT-ACCEPTANCE.md`
            10. `{selected_dir}/PROJECT-FILE-MAP.md`
            11. `{selected_dir}/PROJECT-DESIGN.md`
            12. `{selected_dir}/PROJECT-TASK-BREAKDOWN.md`

            ## 开始前强制检查

            - 确认仓库场景：**{scenario_name}**
            - 全流程喂给 AI 的文档语言：`{ctx.ai_docs_language}`
            - 重读用户原始文档：`{ctx.requirements_doc}`
            - 以 canonical 项目文档作为直接执行基底：`{ctx.canonical_project_doc}`
            - 选择任务前先检查 git 状态
            - 确认当前阶段和下一项唯一优先任务
            - 不要重新猜测已经记录过的决策
            """
        ).strip()
        + "\n",
        "AI-MASTER-PROMPT.md": f"# AI 固定提示词\n\n{base_prompt('zh')}\n",
        "PROJECT-ROADMAP.md": dedent(
            f"""
            # 项目路线图

            项目：**{ctx.project_name}**
            场景：**{scenario_name}**

            | 阶段 | 目标 | 进入条件 | 退出条件 |
            | --- | --- | --- | --- |
            | 1. Discovery | 锁定需求来源与架构方向 | 原始需求文档已存在 | 设计基线、决策和文件地图已记录 |
            | 2. Foundation | 建立壳层、工具链和项目骨架 | Discovery 产物已完整 | 核心基础设施与启动骨架完成 |
            | 3. Implementation | 交付优先级最高的功能切片 | Foundation 完成 | 主流程实现并验证 |
            | 4. Hardening | 补齐缺口、测试和降风险 | 主流程已存在 | 验收检查通过 |
            | 5. Release Readiness | 准备交接或发布 | Hardening 稳定 | 最终文档、变更记录与发布说明就绪 |

            ## 说明

            - 工作顺序必须按真实依赖组织，而不是按页面名称组织。
            - 只有在架构或里程碑模型变化时才更新此文档。
            - 对已有代码仓库，只有在 canonical 项目文档消除关键歧义后才允许进入实现。
            """
        ).strip()
        + "\n",
        "PROJECT-TODO.md": dedent(
            """
            # 项目 TODO

            每个最小可交付任务使用一个独立区块。

            ## 任务模板

            - Task ID:
            - Title:
            - Phase:
            - Depends On:
            - Status:
            - Goal:
            - Implementation Notes:
            - Done When:
            - Verification:
            - Files Expected:

            ## 初始种子任务

            - Task ID: DISC-001
            - Title: 校验需求来源并冻结初始范围
            - Phase: Discovery
            - Depends On: None
            - Status: Pending
            - Goal: 确认需求文档并识别所有未决假设。
            - Implementation Notes: 阅读源文档并更新 PROJECT-DECISIONS.md。
            - Done When: 已记录唯一可信需求来源与范围边界。
            - Verification: 文档中已写明需求路径与范围说明。
            - Files Expected: {selected_dir}/PROJECT-DECISIONS.md, {selected_dir}/PROJECT-STATUS.md
            """
        ).strip()
        + "\n",
        "PROJECT-STATUS.md": dedent(
            f"""
            # 项目状态

            - 当前阶段：Discovery
            - 当前里程碑：文档体系初始化
            - 工作流阶段：{ctx.workflow_stage}
            - 已完成任务 ID：无
            - 正在进行任务 ID：DISC-001
            - 下一项唯一优先任务：DISC-001
            - 当前阻塞：无
            - 最近验证：由 codex-loop 生成初始文档脚手架

            ## 当前状态摘要

            {ctx.current_state}

            ## 风险与偏差

            - 架构细节仍需根据项目事实补全。
            - TODO 仍是占位版本，需在完成 discovery 后细化。
            """
        ).strip()
        + "\n",
        "PROJECT-HANDOFF.md": dedent(
            """
            # 项目交接

            - 本轮目标：建立接力开发文档体系。
            - 本轮完成：生成初始文档集合与运行配置。
            - 本轮未完成：与用户反复确认并消除 canonical 项目文档中的关键歧义。
            - 当前阻塞：无。
            - 已更新文件：初始文档脚手架。
            - 下一步唯一推荐动作：重读用户原始文档，完善 canonical 项目文档，确认无歧义后再继续。
            - 接手 Codex 注意事项：每轮开始前先重读用户原始文档。
            """
        ).strip()
        + "\n",
        "PROJECT-DECISIONS.md": dedent(
            f"""
            # 项目决策

            - 主工作流：先用 `plan-docs` 打磨 canonical 项目文档，再用 `init` 生成正式文档组，最后用 `run` 启动 supervised Codex loop。
            - 用户原始文档：`{ctx.requirements_doc}`
            - Canonical 项目文档：`{ctx.canonical_project_doc}`
            - AI 文档语言：`{ctx.ai_docs_language}`
            - 场景类型：{scenario_name}
            - 默认规则：每轮开始前必须重读用户原始文档。
            - 直接执行基底：永远使用 canonical 项目文档，不能直接使用用户上传原件。
            - 提交规则：每个最小任务一条 commit，且 commit message 必须包含任务 ID。
            - 工具链规则：只有在自行补齐失败后才允许标记为 blocked。
            """
        ).strip()
        + "\n",
        "PROJECT-ACCEPTANCE.md": dedent(
            """
            # 项目验收

            ## 全局完成定义

            - 最终实现能映射回用户原始文档。
            - canonical 项目文档已经详尽到不存在关键歧义。
            - 路线图、TODO、状态和交接文档与真实状态一致。
            - 仓库可以在无需额外人工说明的情况下交给新的 Codex 会话接手。

            ## 里程碑验收

            - Discovery：需求与架构约束已文档化。
            - Foundation：工具链与项目壳层可复现。
            - Implementation：主功能流程满足已确认范围。
            - Hardening：关键测试与验证通过。
            - Release Readiness：最终文档与交接完整。
            """
        ).strip()
        + "\n",
        "PROJECT-FILE-MAP.md": dedent(
            f"""
            # 项目文件地图

            ## 初始仓库地图

            {ctx.file_map}

            ## 使用说明

            - 目录结构或关键职责边界变化时更新此文件。
            - 保持简洁，只记录影响判断的关键路径。
            - 后续更新时应包含 canonical 项目文档与用户原始文档。
            """
        ).strip()
        + "\n",
        "PROJECT-CHANGELOG.md": dedent(
            """
            # 项目变更记录

            ## 2026-03-13

            - 初始化 Codex 接力开发文档体系。
            - 添加路线图、TODO、状态、交接、决策和验收文档。
            """
        ).strip()
        + "\n",
        "PROJECT-DESIGN.md": dedent(
            f"""
            # 项目设计

            ## 设计种子

            {ctx.design_seed}

            ## 直接基底

            - Canonical 项目文档：`{ctx.canonical_project_doc}`
            - 用户原始文档：`{ctx.requirements_doc}`

            ## 待补全章节

            - 系统上下文
            - 核心用户流程
            - 架构层次与边界
            - 数据契约与集成点
            - 错误处理与回退策略
            """
        ).strip()
        + "\n",
        "PROJECT-TASK-BREAKDOWN.md": dedent(
            """
            # 项目任务拆解

            将路线图拆成可独立验证的最小任务。

            ## 期望结构

            - Discovery 任务
            - Foundation 任务
            - Implementation 任务
            - Hardening 任务
            - Release Readiness 任务

            ## 规则

            每个任务都必须小到能在一轮内完成、验证、更新文档并提交。
            只有在 canonical 项目文档已经消除关键歧义后，才允许继续生成实现任务。
            """
        ).strip()
        + "\n",
    }
    return docs[filename]
