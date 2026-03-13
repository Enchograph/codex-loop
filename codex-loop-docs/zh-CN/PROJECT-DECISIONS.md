# 项目决策

- 主工作流：先用 `plan-docs` 打磨 canonical 项目文档，再用 `init` 生成正式文档组，最后用 `run` 启动 supervised Codex loop。
- 用户原始文档：`codex-loop-docs/requirements/USER-REQUIREMENTS.md`
- Canonical 项目文档：`codex-loop-docs/project/PROJECT-BRIEF.md`
- 用户提供的项目文档输入：`codex-loop-docs/project/USER-PROVIDED-PROJECT-DOC.md`
- AI 文档语言：`en`
- 场景类型：已具备文档体系的仓库
- 默认规则：每轮开始前必须重读用户原始文档。
- 直接执行基底：永远使用 canonical 项目文档，不能直接使用用户上传原件。
- 提交规则：每个最小任务一条 commit，且 commit message 必须包含任务 ID。
- 工具链规则：只有在自行补齐失败后才允许标记为 blocked。
