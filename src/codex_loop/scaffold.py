from __future__ import annotations

import json
import shutil
from pathlib import Path

from codex_loop.models import RepoInspection, RuntimeConfig, ScaffoldResult, SUPPORTED_APPROVAL_POLICIES, SUPPORTED_SANDBOX_MODES
from codex_loop.templates import get_template_bundle

CODEX_LOOP_DIR = Path(".codex-loop")
CODEX_LOOP_DOCS_DIR = CODEX_LOOP_DIR / "docs"
CODEX_LOOP_CONFIG_DIR = CODEX_LOOP_DIR / "config"
CODEX_LOOP_LOG_DIR = CODEX_LOOP_DIR / "log"
CANONICAL_PROJECT_DOC_PATH = CODEX_LOOP_DOCS_DIR / "CANONICAL-PROJECT-DOC.md"
USER_REQUIREMENTS_PATH = CODEX_LOOP_DOCS_DIR / "USER-REQUIREMENTS.md"
AI_START_HERE_PATH = CODEX_LOOP_DOCS_DIR / "AI-START-HERE.md"
AI_MASTER_PROMPT_PATH = CODEX_LOOP_DOCS_DIR / "AI-MASTER-PROMPT.md"
PROJECT_ROADMAP_PATH = CODEX_LOOP_DOCS_DIR / "PROJECT-ROADMAP.md"
PROJECT_TODO_PATH = CODEX_LOOP_DOCS_DIR / "PROJECT-TODO.md"
PROJECT_STATUS_PATH = CODEX_LOOP_DOCS_DIR / "PROJECT-STATUS.md"
PROJECT_HANDOFF_PATH = CODEX_LOOP_DOCS_DIR / "PROJECT-HANDOFF.md"
PROJECT_DECISIONS_PATH = CODEX_LOOP_DOCS_DIR / "PROJECT-DECISIONS.md"
PROJECT_ACCEPTANCE_PATH = CODEX_LOOP_DOCS_DIR / "PROJECT-ACCEPTANCE.md"
PROJECT_FILE_MAP_PATH = CODEX_LOOP_DOCS_DIR / "PROJECT-FILE-MAP.md"
PROJECT_CHANGELOG_PATH = CODEX_LOOP_DOCS_DIR / "PROJECT-CHANGELOG.md"
RUNTIME_CONFIG_PATH = CODEX_LOOP_CONFIG_DIR / "codex-loop.json"


def detect_scenario(repo: Path) -> str:
    docs_dir = repo / CODEX_LOOP_DIR
    if docs_dir.exists() and (repo / AI_START_HERE_PATH).exists():
        return "existing-docs"
    non_hidden = [path for path in repo.iterdir() if not path.name.startswith(".")]
    if not non_hidden:
        return "blank"
    substantive = []
    for path in non_hidden:
        if path.name in {"README.md", "README.zh-CN.md"}:
            continue
        substantive.append(path)
    return "blank" if not substantive else "existing-code"


def inspect_repo(repo: Path) -> RepoInspection:
    files_considered = sum(1 for _ in repo.rglob("*")) if repo.exists() else 0
    return RepoInspection(
        scenario=detect_scenario(repo),
        has_git=(repo / ".git").exists(),
        has_docs=(repo / CODEX_LOOP_DIR).exists(),
        has_requirements_doc=(repo / USER_REQUIREMENTS_PATH).exists(),
        files_considered=files_considered,
    )


def init_repo(
    *,
    repo: Path,
    scenario: str,
    requirements_doc: Path | None,
    canonical_doc: Path | None,
    ai_docs_language: str,
    sandbox_mode: str,
    approval_policy: str,
    search_enabled: bool,
    skip_git_repo_check: bool,
    force: bool,
) -> ScaffoldResult:
    _validate_runtime_options(sandbox_mode, approval_policy)
    bundle = get_template_bundle(ai_docs_language)
    created: list[Path] = []
    skipped: list[Path] = []
    docs = {
        repo / AI_START_HERE_PATH: bundle.ai_start_here,
        repo / AI_MASTER_PROMPT_PATH: bundle.ai_master_prompt,
        repo / PROJECT_ROADMAP_PATH: bundle.roadmap,
        repo / PROJECT_TODO_PATH: bundle.todo,
        repo / PROJECT_STATUS_PATH: bundle.status,
        repo / PROJECT_HANDOFF_PATH: bundle.handoff,
        repo / PROJECT_DECISIONS_PATH: bundle.decisions,
        repo / PROJECT_ACCEPTANCE_PATH: bundle.acceptance,
        repo / PROJECT_FILE_MAP_PATH: bundle.file_map,
        repo / PROJECT_CHANGELOG_PATH: bundle.changelog,
    }

    requirements_target = repo / USER_REQUIREMENTS_PATH
    canonical_target = repo / CANONICAL_PROJECT_DOC_PATH
    if requirements_doc:
        _copy_file(requirements_doc, requirements_target, force, created, skipped)
    elif not requirements_target.exists():
        raise FileNotFoundError(
            "Missing .codex-loop/docs/USER-REQUIREMENTS.md. "
            "Run `codex-loop plan-docs` first, or pass `--requirements-doc` to use an existing user document."
        )
    if canonical_doc:
        _copy_file(canonical_doc, canonical_target, force, created, skipped)
    else:
        _write_file(canonical_target, bundle.canonical_project_doc, force, created, skipped)

    for path, content in docs.items():
        _write_file(path, content, force, created, skipped)

    config = RuntimeConfig(
        codex_bin="codex",
        workdir=repo,
        prompt=bundle.runtime_prompt,
        total_timeout_minutes=300,
        log_dir=repo / CODEX_LOOP_LOG_DIR,
        skip_git_repo_check=skip_git_repo_check,
        sandbox_mode=sandbox_mode,
        approval_policy=approval_policy,
        search_enabled=search_enabled,
    )
    _write_file(repo / RUNTIME_CONFIG_PATH, json.dumps(runtime_config_to_dict(config), indent=2, ensure_ascii=False) + "\n", force, created, skipped)
    return ScaffoldResult(scenario=scenario, created=created, skipped=skipped)


def plan_docs(
    *,
    repo: Path,
    scenario: str,
    requirements_doc: Path | None,
    canonical_doc: Path | None,
    ai_docs_language: str,
    force: bool,
) -> ScaffoldResult:
    created: list[Path] = []
    skipped: list[Path] = []
    bundle = get_template_bundle(ai_docs_language)

    requirements_target = repo / USER_REQUIREMENTS_PATH
    if requirements_doc:
        _copy_file(requirements_doc, requirements_target, force, created, skipped)
    else:
        _write_file(requirements_target, bundle.base_requirements, force, created, skipped)
    return ScaffoldResult(scenario=scenario, created=created, skipped=skipped)


def generate_plan_prompt(repo: Path, language: str, scenario: str) -> str:
    return f"""You are preparing the base project documents for repository `{repo}`.

Requirements:
- Analyze the repository state first
- Follow the methodology in `codex-loop-minimal/Codex-接力开发文档编写指南.md`
- Ask the user follow-up questions when the requirements are incomplete or ambiguous
- Produce a single authoritative requirements document at `.codex-loop/docs/USER-REQUIREMENTS.md`
- Do not create a second user-requirements variant elsewhere
- The result of this stage becomes the only user requirements document used by the next stage
- Write the resulting document in `{language}`
- Current scenario: `{scenario}`
"""


def generate_init_prompt(repo: Path, language: str, scenario: str) -> str:
    return f"""You are initializing the Codex relay-development document set for repository `{repo}`.

Requirements:
- Follow `codex-loop-minimal/Codex-接力开发文档编写指南.md`
- Read the single authoritative requirements document at `.codex-loop/docs/USER-REQUIREMENTS.md` first
- Treat `.codex-loop/docs/USER-REQUIREMENTS.md` as fixed input for this stage; do not rewrite or regenerate it
- Then refine `.codex-loop/docs/CANONICAL-PROJECT-DOC.md` and the generated relay docs until they are ready for handoff
- Use follow-up questions only to refine the stage-two document set
- Ask the user about any unresolved ambiguity instead of guessing
- Write the relay documents in `{language}`
- Current scenario: `{scenario}`
"""


def runtime_config_to_dict(config: RuntimeConfig) -> dict[str, object]:
    payload: dict[str, object] = {
        "codex_bin": config.codex_bin,
        "workdir": str(config.workdir),
        "prompt": config.prompt,
        "total_timeout_minutes": config.total_timeout_minutes,
        "skip_git_repo_check": config.skip_git_repo_check,
        "sandbox_mode": config.sandbox_mode,
        "approval_policy": config.approval_policy,
        "search_enabled": config.search_enabled,
        "profile": config.profile,
        "model": config.model,
        "extra_args": config.extra_args,
        "log_dir": str(config.log_dir) if config.log_dir else None,
    }
    return payload


def validate_run_readiness(repo: Path) -> None:
    required = [
        repo / AI_MASTER_PROMPT_PATH,
        repo / USER_REQUIREMENTS_PATH,
        repo / CANONICAL_PROJECT_DOC_PATH,
        repo / RUNTIME_CONFIG_PATH,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required generated files:\n" + "\n".join(missing))


def _validate_runtime_options(sandbox_mode: str, approval_policy: str) -> None:
    if sandbox_mode not in SUPPORTED_SANDBOX_MODES:
        raise ValueError(f"Unsupported sandbox mode: {sandbox_mode}")
    if approval_policy not in SUPPORTED_APPROVAL_POLICIES:
        raise ValueError(f"Unsupported approval policy: {approval_policy}")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_file(path: Path, content: str, force: bool, created: list[Path], skipped: list[Path]) -> None:
    _ensure_parent(path)
    if path.exists() and not force:
        skipped.append(path)
        return
    path.write_text(content, encoding="utf-8")
    created.append(path)


def _copy_file(source: Path, target: Path, force: bool, created: list[Path], skipped: list[Path]) -> None:
    _ensure_parent(target)
    if target.exists() and not force:
        skipped.append(target)
        return
    shutil.copyfile(source, target)
    created.append(target)
