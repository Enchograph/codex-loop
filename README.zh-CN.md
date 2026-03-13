# Codex Loop

Codex Loop 是一个以 CLI 为核心的工具集，用于以 canonical 项目文档优先的方式运行 Codex 接力开发：

1. 准备或打磨 canonical 项目文档。
2. 生成正式的接力开发文档体系。
3. 在文档体系准备好之后，启动 supervised Codex 开发循环。

默认文档语言为英文，但用户可以自己选择全过程喂给 AI 的文档语言是 `en` 还是 `zh-CN`。完整中文镜像位于本文档和 `codex-loop-docs/zh-CN/` 目录中。

## 支持场景

- 空白仓库，从用户需求文档开始。
- 已有代码仓库，需要补齐 Codex 接力开发文档体系。
- 已具备接力文档的仓库，只需要校验、补缺和运行时配置。
- 通过 Python 3.11+ 支持 Windows、macOS 和 Linux。

## 重要规则

如果用户已经有自己的项目文档，应优先提供。但这个文档只是输入，不能直接作为执行基底。

真正最重要的开发基础，是在反复确认并消除歧义后形成的 canonical 项目文档。自动执行时，Codex 每轮开始仍必须回读用户原始文档，避免偏离方向。

## 安装

```bash
python -m pip install -e .[dev]
```

## 快速开始

为空仓库生成文档：

```bash
codex-loop init blank --repo /path/to/repo --requirements-doc /path/to/requirements.md
```

为已有代码仓库先准备 canonical 项目文档：

```bash
codex-loop plan-docs --repo /path/to/repo --requirements-doc /path/to/original-user-doc.md --input-doc /path/to/your-project-doc.md
codex-loop plan-docs --repo /path/to/repo --ai-doc-language zh-CN
```

确认 canonical 项目文档后，再为已有代码仓库生成正式文档组：

```bash
codex-loop init existing-code --repo /path/to/repo --ai-doc-language zh-CN
```

文档准备好后启动 supervised loop：

```bash
codex-loop run --config /path/to/repo/codex-loop.json
codex-loop run --config /path/to/repo/codex-loop.json --sandbox-mode danger-full-access --approval-policy never
```

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

## 项目文档

- [使用指南](codex-loop-docs/zh-CN/USAGE.md)
- [仓库结构](codex-loop-docs/zh-CN/REPOSITORY-STRUCTURE.md)
- [方法论](codex-loop-docs/zh-CN/METHODOLOGY.md)
- [贡献说明](codex-loop-docs/zh-CN/CONTRIBUTING.md)
