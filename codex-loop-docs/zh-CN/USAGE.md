# 使用指南

## 工作流

Codex Loop 刻意拆成带门禁的几个阶段：

1. `plan-docs`：在需要时准备并打磨 canonical 项目文档。
2. `init`：创建或规范化正式的接力开发文档体系。
3. `run`：在文档准备好之后启动 supervised Codex loop。

用户可以通过 `--ai-doc-language en` 或 `--ai-doc-language zh-CN` 选择全过程喂给 AI 的文档语言。

## Canonical 项目文档规则

- 如果用户已有自己的项目文档，应优先提供。
- 用户提供的项目文档只是输入来源。
- 正式文档生成和自动执行的直接基底，是 canonical 项目文档。
- 自动执行时，AI 每轮开始都仍然必须回读用户原始文档。

## `plan-docs`

对于已有代码仓库，应先使用这个命令，再进入正式文档生成。

示例：

```bash
codex-loop plan-docs --repo /path/to/repo --requirements-doc /path/to/original-user-doc.md
codex-loop plan-docs --repo /path/to/repo --input-doc /path/to/existing-project-doc.md
codex-loop plan-docs --repo /path/to/repo --requirements-doc /path/to/original-user-doc.md --input-doc /path/to/existing-project-doc.md
codex-loop plan-docs --repo /path/to/repo --ai-doc-language zh-CN
```

行为：

- 如果提供了用户原始文档，则复制到 `codex-loop-docs/requirements/USER-REQUIREMENTS.md`
- 如果提供了用户项目文档，则复制到 `codex-loop-docs/project/USER-PROVIDED-PROJECT-DOC.md`
- 生成 `codex-loop-docs/project/PROJECT-BRIEF.md` 作为 canonical 项目文档脚手架
- 生成进入 Plan Mode 追问澄清所需的提示和辅助文件
- 不会启动实现或自动执行

## `init`

示例：

```bash
codex-loop init blank --repo /path/to/repo --requirements-doc /path/to/requirements.md
codex-loop init existing-code --repo /path/to/repo --requirements-doc /path/to/requirements.md
codex-loop init existing-docs --repo /path/to/repo
codex-loop init --repo /path/to/repo
codex-loop init existing-code --repo /path/to/repo --ai-doc-language zh-CN
```

行为：

- 将需求文档复制到 `codex-loop-docs/requirements/USER-REQUIREMENTS.md`
- 对 `existing-code` 强制要求 canonical 项目文档
- 在 `codex-loop-docs/en/` 中生成英文核心接力文档
- 在 `codex-loop-docs/zh-CN/` 中生成中文镜像
- 写入 `codex-loop.json` 与 `codex-loop.example.json`
- 不会自动启动 loop
- 允许通过 `--sandbox-mode`、`--approval-policy`、`--search-enabled`、`--skip-git-repo-check` 预先设定第三阶段的默认运行权限

## `inspect`

```bash
codex-loop inspect --repo /path/to/repo
```

返回 JSON 格式的场景识别结果。

## `run`

```bash
codex-loop run --config /path/to/repo/codex-loop.json
codex-loop run --config /path/to/repo/codex-loop.json --sandbox-mode workspace-write --approval-policy on-request
```

行为：

- 校验 Codex 可执行文件和工作目录
- 在 `.codex/log/` 下创建每轮日志
- 持续运行 `codex exec`，直到超时、收到停止信号或达到 `max_rounds`
- 若存在 final message，则在每轮结束后打印
- 允许用户在第三阶段真正开始前临时覆盖运行权限设置

## 配置说明

- 普通可执行名使用 `codex_bin`，例如 `codex`。
- 需要完整启动命令时使用 `codex_command`。
- `max_rounds` 是可选项，适合测试或受控运行。
- 使用 `ai_docs_language` 决定全过程喂给 AI 的是英文还是中文文档。
- 运行权限取值跟随当前 Codex CLI：`sandbox_mode` 支持 `read-only`、`workspace-write`、`danger-full-access`；`approval_policy` 支持 `never`、`on-failure`、`on-request`、`untrusted`。
