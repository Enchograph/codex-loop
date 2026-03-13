## 其他说明文档

## 生成的文档

正式文档生成阶段会生成或规范化以下文档：

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
- `codex-loop-docs/zh-CN/` 下的中文镜像

## 命令

- `codex-loop plan-docs`
- `codex-loop init [blank|existing-code|existing-docs|auto]`
- `codex-loop inspect`
- `codex-loop run`

对于 `existing-code`，如果 canonical 项目文档缺失，`init` 会停止并给出明确提示。

## 运行配置

生成的 `codex-loop.json` 在兼容旧 shell 方案的同时，新增了更灵活的 `codex_command` 字段。

关键字段：

- `ai_docs_language`：全过程喂给 AI 的文档语言，支持 `en` 和 `zh-CN`
- `codex_bin`：简单可执行名，例如 `codex`
- `codex_command`：可选数组形式，适用于完整启动命令
- `workdir`：目标仓库根目录
- `prompt`：传给 `codex exec` 的提示词
- `total_timeout_minutes`：整轮总时长预算
- `max_rounds`：可选轮次数上限，适合测试或受控运行
- `log_dir`：可选日志目录，默认 `workdir/.codex/log`
- `sandbox_mode`：运行时沙箱模式，对应最初脚本的权限选项
- `approval_policy`：运行时审批模式，对应最初脚本的权限选项
- `search_enabled`：运行循环中是否开启网页搜索
- `skip_git_repo_check`：是否跳过 Codex 的初始 git 仓库检查

## 第三阶段前的权限选择

在开始第三阶段前，用户可以像最初脚本一样选择 Codex 的运行权限组合：

- `sandbox_mode`：`read-only`、`workspace-write`、`danger-full-access`
- `approval_policy`：`never`、`on-failure`、`on-request`、`untrusted`
- `search_enabled`
- `skip_git_repo_check`

这些值可以在 `init` 时写成默认配置，也可以在真正执行 `run` 之前临时覆盖。

## 跨平台入口

[`scripts/`](scripts) 目录提供了包装脚本：

- `scripts/codex-loop.sh`
- `scripts/codex-loop.ps1`
- `scripts/codex-loop.bat`

推荐的主入口仍然是安装后的 `codex-loop` 命令。