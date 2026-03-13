# Codex Loop

<p align="center">中文 | <a href="./README.md">English</a></p>

## 项目介绍

Codex Loop 是一份简单的脚本项目，旨在为 Codex 提供全自动循环开发的功能。

项目分三部分：

1. （如果需要的话）根据用户需求生成一份基底项目需求文档
2. 根据前一步生成的或用户自行添加的基底项目需求文档生成一系列完整的文档组，供后续的复数个空白 Codex 会话无缝接续接力开发。
3. 自动化脚本， 在 Codex 完成一项任务后开启新会话自动开始下一部分任务，以达到无人值守全自动循环开发的效果。提供语言、 Codex 权限、循环时间等参数设置。

项目支持从零开始的空项目开发，与已有代码的中途项目开发。

项目支持 Windows、macOS 和 Linux 等系统，需求 Python 3.11 以上环境

## 命令

### 安装

```bash
python -m pip install -e .[dev]
```

### 基底项目需求文档生成（可选）


为已有代码仓库先准备基底项目文档：

```bash
PROJECT_DIR="/path/to/repo"
ORIGINAL_USER_DOC="/path/to/original-user-doc.md"

codex-loop plan-docs --repo "$PROJECT_DIR" --requirements-doc "$ORIGINAL_USER_DOC"
```

### 根据 用户基底项目需求文档 生成 AI 开发文档组

#### 空项目，有 用户基底文档 提供

```bash
PROJECT_DIR="/path/to/repo"
BASE_REQUIREMENTS_DOC="/path/to/requirements.md"

codex-loop init blank --repo "$PROJECT_DIR" --requirements-doc "$BASE_REQUIREMENTS_DOC"
```

#### 已有项目，无 用户基底文档 提供

经由上一步生成 用户基底项目需求文档 后，基于此文档生成 AI 开发文档组

```bash
PROJECT_DIR="/path/to/repo"

codex-loop init existing-code --repo "$PROJECT_DIR" --ai-doc-language zh-CN
```

#### 已有项目，有 用户原始需求文档 提供

```bash
PROJECT_DIR="/path/to/repo"
ORIGINAL_USER_DOC="/path/to/original-user-doc.md"

codex-loop plan-docs --repo "$PROJECT_DIR" --requirements-doc "$ORIGINAL_USER_DOC"
codex-loop init existing-code --repo "$PROJECT_DIR" --ai-doc-language zh-CN
```

### Codex 自动化脚本启动

文档组准备好后启动 Codex 自动循环，**注意对 Codex 的权限授权！**

> 建议的方式是在空虚拟机里赋予 Codex 无需请求的权限，以实现全自动不中断开发。

```bash
PROJECT_DIR="/path/to/repo"
CONFIG_PATH="$PROJECT_DIR/codex-loop.json"

codex-loop run --config "$CONFIG_PATH"
codex-loop run --config "$CONFIG_PATH" --sandbox-mode danger-full-access --approval-policy never
```

## 如果只是需要自动循环功能……

如果你只是想要 Codex 固定提示词自动开对话循环功能，请参阅 /codex-loop-minimal 文件夹。


## 项目文档

- [其他说明文档](codex-loop-docs/zh-CN/OTHER-SPECIFIED-DOCUMENTS.md)
- [使用指南](codex-loop-docs/zh-CN/USAGE.md)
- [仓库结构](codex-loop-docs/zh-CN/REPOSITORY-STRUCTURE.md)
- [方法论](codex-loop-docs/zh-CN/METHODOLOGY.md)
- [贡献说明](codex-loop-docs/zh-CN/CONTRIBUTING.md)
