from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from codex_loop.models import RuntimeConfig


def ensure_codex_available(codex_bin: str = "codex") -> str:
    resolved = shutil.which(codex_bin)
    if not resolved:
        raise FileNotFoundError(f"Codex binary not found: {codex_bin}")
    return resolved


def launch_interactive_codex(
    *,
    prompt: str,
    cwd: Path,
    codex_bin: str = "codex",
    search_enabled: bool = True,
    sandbox_mode: str | None = None,
    approval_policy: str | None = None,
    model: str | None = None,
    profile: str | None = None,
) -> int:
    ensure_codex_available(codex_bin)
    command = [codex_bin]
    if sandbox_mode:
        command.extend(["--sandbox", sandbox_mode])
    if approval_policy:
        command.extend(["--ask-for-approval", approval_policy])
    if search_enabled:
        command.append("--search")
    if model:
        command.extend(["--model", model])
    if profile:
        command.extend(["--profile", profile])
    command.extend(["--cd", str(cwd), prompt])
    completed = subprocess.run(command, cwd=cwd, check=False)
    return completed.returncode


def build_exec_command(config: RuntimeConfig) -> list[str]:
    ensure_codex_available(config.codex_bin)
    command = [config.codex_bin, "exec", "--cd", str(config.workdir)]
    if config.skip_git_repo_check:
        command.append("--skip-git-repo-check")
    if config.approval_policy == "never" and config.sandbox_mode == "danger-full-access":
        command.append("--dangerously-bypass-approvals-and-sandbox")
    else:
        command.extend(["--sandbox", config.sandbox_mode, "--ask-for-approval", config.approval_policy])
    if config.search_enabled:
        command.append("--search")
    if config.profile:
        command.extend(["--profile", config.profile])
    if config.model:
        command.extend(["--model", config.model])
    command.extend(config.extra_args)
    return command
