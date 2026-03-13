# Codex Loop Minimal

<p align="center">English | <a href="./README.zh-CN.md">中文</a></p>

## Project Introduction

Codex Loop Minimal is the minimal version of the Codex loop runner.

It keeps the original core behavior:

1. Read a local JSON config file.
2. Run `codex exec` with a fixed prompt.
3. Start the next round automatically after the current round finishes.
4. Keep looping until the total timeout is reached or the user stops the process.

This folder is for users who only want the fixed-prompt automatic conversation loop and do not need the larger documentation-generation workflow from the main project.

## Supported Platforms

- Linux: `linux/`
- macOS: `macos/`
- Windows: `windows/`

## Configuration

Each platform folder includes its own `codex_supervised_loop.json`.

Important fields:

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

## Runtime Permission Options

The scripts support the current Codex CLI runtime permission model:

- `sandbox_mode`: `read-only`, `workspace-write`, `danger-full-access`
- `approval_policy`: `never`, `on-failure`, `on-request`, `untrusted`
- `search_enabled`
- `skip_git_repo_check`

## Quick Start

### Linux

```bash
SCRIPT_DIR="/path/to/codex-loop-minimal/linux"
cd "$SCRIPT_DIR"
chmod +x ./codex_supervised_loop.sh
./codex_supervised_loop.sh
```

### macOS

```bash
SCRIPT_DIR="/path/to/codex-loop-minimal/macos"
cd "$SCRIPT_DIR"
chmod +x ./codex_supervised_loop_macos.command ./codex_supervised_loop.sh
./codex_supervised_loop_macos.command
```

### Windows PowerShell

```powershell
$ScriptDir = "D:\path\to\codex-loop-minimal\windows"
Set-Location $ScriptDir
.\codex_supervised_loop.ps1
```

### Windows Command Prompt

```bat
set SCRIPT_DIR=D:\path\to\codex-loop-minimal\windows
cd /d %SCRIPT_DIR%
codex_supervised_loop.bat
```

## Included Files

- `linux/codex_supervised_loop.sh`: Linux-compatible loop runner
- `linux/codex_supervised_loop.desktop`: Linux desktop launcher example
- `linux/codex_supervised_loop.json`: Linux example config
- `macos/codex_supervised_loop_macos.command`: macOS launcher
- `macos/codex_supervised_loop.sh`: shell runner used on macOS
- `macos/codex_supervised_loop.json`: macOS example config
- `windows/codex_supervised_loop.ps1`: Windows PowerShell runner
- `windows/codex_supervised_loop.bat`: Windows batch launcher
- `windows/codex_supervised_loop.json`: Windows example config
- `codex-loop.example.json`: alternate example config
- `codex-loop.json`: alternate example config
- `Codex-接力开发文档编写指南.md`: reference methodology document
