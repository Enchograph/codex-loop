# Codex Loop

<p align="center">中文 | <a href="./README.md">English</a></p>

Codex Loop 是一个简单的命令行项目，用于执行 Codex 的全自动循环接力开发。

项目分为三个部分：

1. （可选地）为现有仓库生成「基底需求文档」。或由 AI 辅助细化您自己写的详细项目需求文档。我们推荐您直接使用您详细的项目需求文档投入第二步。这一步的文档质量将决定最后的运行效果。
2. 基于「基底需求文档」生成文档组，为 Codex 会话提供多轮接力无缝开发能力。
3. 基于该文档组运行无人值守的 `codex exec` 全自动循环开发。

您如果只需要适用于 Codex 的自动循环脚本，参阅 `codex-loop-minimal/`即可。

项目要求 Python 3.11+，支持 Windows、macOS、Linux。

## 安装

```bash
python -m pip install -e .
```

## 命令

直接运行 `codex-loop` 会进入轻交互模式，让用户先选择语言，再逐项选择命令参数，默认把“当前终端所在目录”当成仓库。

```bash
cd /path/to/repo
codex-loop
```

亦可以使用 `--repo` 显式指定仓库路径。

### （可选）第一步，「基底需求文档」生成 ： plan-docs

用于为已有代码仓库生成「基底需求文档」。亦可以细化用户提供的文档作为「基底需求文档」。

我们更推荐您自己动手写一份详尽的「基底需求文档」直接投入第二阶段。您这一份「基底需求文档」的质量将决定最后的运行效果。

#### 为已有代码仓库从零生成文档：

```bash
cd /path/to/repo
codex-loop plan-docs
```

空仓库不应执行此命令。

#### 细化用户提供的文档：

```bash
cd /path/to/repo
codex-loop plan-docs --requirements-doc /path/to/original-user-doc.md
```

### 第二阶段，文档组生成：init

第二阶段：根据「基底需求文档」生成供 Codex 会话遵守的开发规则。

它要求「基底需求文档」必须存在。
如果您没有运行第一步：
则需要把您的文档放到 `.codex-loop/docs/USER-REQUIREMENTS.md`，
或者通过 `--requirements-doc` 显式指定「基底需求文档」位置。

#### `USER-REQUIREMENTS.md`（「基底需求文档」）已存在：

```bash
cd /path/to/repo
codex-loop init
```

#### 显式指定「基底需求文档」位置：

```bash
cd /path/to/repo
codex-loop init --requirements-doc /path/to/user-requirements.md
```

### 第三步，全自动循环运行：run

根据生成好的 `.codex-loop/config/codex-loop.json` 启动多轮 `codex exec` 自动开发循环。

```bash
cd /path/to/repo
codex-loop run
```
