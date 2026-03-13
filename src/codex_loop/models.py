from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


SUPPORTED_SANDBOX_MODES = {"read-only", "workspace-write", "danger-full-access"}
SUPPORTED_APPROVAL_POLICIES = {"untrusted", "on-request", "never"}


@dataclass
class RuntimeConfig:
    codex_bin: str
    workdir: Path
    prompt: str
    total_timeout_minutes: int
    log_dir: Path | None = None
    skip_git_repo_check: bool = False
    sandbox_mode: str = "workspace-write"
    approval_policy: str = "on-request"
    search_enabled: bool = True
    profile: str | None = None
    model: str | None = None
    extra_args: list[str] = field(default_factory=list)


@dataclass
class ScaffoldResult:
    scenario: str
    created: list[Path]
    skipped: list[Path]


@dataclass
class RepoInspection:
    scenario: str
    has_git: bool
    has_docs: bool
    has_requirements_doc: bool
    files_considered: int
