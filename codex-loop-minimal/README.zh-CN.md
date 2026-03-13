# Codex Loop Minimal

<p align="center">中文 | <a href="./README.md">English</a></p>

## 项目介绍

Codex Loop Minimal 是 Codex 循环执行器的最小版本。

它保留了原有的核心能力：

1. 读取本地 JSON 配置文件。
2. 用固定提示词运行 `codex exec`。
3. 当前轮结束后自动开始下一轮。
4. 一直循环，直到总超时到达或用户主动停止。

这个文件夹适合只想要“固定提示词自动开对话循环”功能的用户，不需要主项目里更完整的文档生成工作流。

## 支持平台

- Linux：`codex_supervised_loop.sh`
- macOS：`codex_supervised_loop_macos.command`
- Windows PowerShell：`codex_supervised_loop.ps1`
- Windows 命令提示符：`codex_supervised_loop.bat`

## 配置

默认配置文件为 `codex_supervised_loop.json`。

关键字段：

- `codex_bin`
- `workdir`
- `prompt`
- `total_timeout_minutes`
- `log_dir`
- `skip_git_repo_check`
- `sandbox_mode`
- `approval_policy`
- `search_enabled`
- `profile`
- `model`
- `extra_args`

## 运行权限选项

脚本支持当前 Codex CLI 的运行权限模型：

- `sandbox_mode`：`read-only`、`workspace-write`、`danger-full-access`
- `approval_policy`：`never`、`on-failure`、`on-request`、`untrusted`
- `search_enabled`
- `skip_git_repo_check`

## 快速开始

### Linux

```bash
SCRIPT_DIR="/path/to/codex-loop-minimal"
cd "$SCRIPT_DIR"
chmod +x ./codex_supervised_loop.sh
./codex_supervised_loop.sh
```

### macOS

```bash
SCRIPT_DIR="/path/to/codex-loop-minimal"
cd "$SCRIPT_DIR"
chmod +x ./codex_supervised_loop_macos.command ./codex_supervised_loop.sh
./codex_supervised_loop_macos.command
```

### Windows PowerShell

```powershell
$ScriptDir = "D:\path\to\codex-loop-minimal"
Set-Location $ScriptDir
.\codex_supervised_loop.ps1
```

### Windows 命令提示符

```bat
set SCRIPT_DIR=D:\path\to\codex-loop-minimal
cd /d %SCRIPT_DIR%
codex_supervised_loop.bat
```

## 包含文件

- `codex_supervised_loop.sh`：兼容 Linux 的循环执行脚本
- `codex_supervised_loop_macos.command`：macOS 启动器
- `codex_supervised_loop.ps1`：Windows PowerShell 执行脚本
- `codex_supervised_loop.bat`：Windows batch 启动器
- `codex_supervised_loop.desktop`：Linux 桌面启动器示例
- `codex_supervised_loop.json`：最小版示例配置
- `codex-loop.example.json`：另一份示例配置
- `Codex-接力开发文档编写指南.md`：参考方法论文档
