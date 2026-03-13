# Codex Loop

<p align="center">中文 | <a href="./README.md">English</a> 

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
codex-loop plan-docs --repo /path/to/repo --requirements-doc /path/to/original-user-doc.md --input-doc /path/to/your-project-doc.md
codex-loop plan-docs --repo /path/to/repo --ai-doc-language zh-CN
```

### 根据 用户基底项目需求文档 生成 AI 开发文档组

#### 空项目，有 用户基底文档 提供

```bash
codex-loop init blank --repo /path/to/repo --requirements-doc /path/to/requirements.md
```

#### 已有项目，无 用户基底文档 提供

经由上一步生成 用户基底项目需求文档 后，基于此文档生成 AI 开发文档组

```bash
codex-loop init existing-code --repo /path/to/repo --ai-doc-language zh-CN
```

#### 已有项目，有 用户基底文档 提供

```bash
```

### Codex 自动化脚本启动

文档组准备好后启动 Codex 自动循环：

```bash
codex-loop run --config /path/to/repo/codex-loop.json
codex-loop run --config /path/to/repo/codex-loop.json --sandbox-mode danger-full-access --approval-policy never
```


## 项目文档

- [其他说明文档](codex-loop-docs/zh-CN/OTHER-SPECIFIED-DOCUMENTS.md)
- [使用指南](codex-loop-docs/zh-CN/USAGE.md)
- [仓库结构](codex-loop-docs/zh-CN/REPOSITORY-STRUCTURE.md)
- [方法论](codex-loop-docs/zh-CN/METHODOLOGY.md)
- [贡献说明](codex-loop-docs/zh-CN/CONTRIBUTING.md)
