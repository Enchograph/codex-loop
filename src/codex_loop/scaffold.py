from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from codex_loop.templates import REQUIRED_CORE_DOCS, TemplateContext, render_doc

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    "codex-loop-docs",
}

DOCS_ROOT = Path("codex-loop-docs")
EN_DOCS_DIR = DOCS_ROOT / "en"
ZH_DOCS_DIR = DOCS_ROOT / "zh-CN"
PROJECT_DOCS_DIR = DOCS_ROOT / "project"
REQUIREMENTS_DOCS_DIR = DOCS_ROOT / "requirements"
SUPPORTED_AI_DOC_LANGUAGES = {"en": EN_DOCS_DIR, "zh-CN": ZH_DOCS_DIR}
SUPPORTED_SANDBOX_MODES = {"read-only", "workspace-write", "danger-full-access"}
SUPPORTED_APPROVAL_POLICIES = {"never", "on-failure", "on-request", "untrusted"}

ORIGINAL_REQUIREMENTS_PATH = REQUIREMENTS_DOCS_DIR / "USER-REQUIREMENTS.md"
CANONICAL_PROJECT_DOC_PATH = PROJECT_DOCS_DIR / "PROJECT-BRIEF.md"
PROJECT_DOC_QUESTIONS_PATH = PROJECT_DOCS_DIR / "PROJECT-DOC-QUESTIONS.md"
PROJECT_DOC_STATUS_PATH = PROJECT_DOCS_DIR / "PROJECT-DOC-STATUS.md"
PLAN_MODE_PROMPT_PATH = PROJECT_DOCS_DIR / "PLAN-MODE-PROMPT.md"
WORKFLOW_STATE_PATH = PROJECT_DOCS_DIR / "WORKFLOW-STATE.json"


@dataclass
class InitResult:
    created: list[Path]
    skipped: list[Path]
    scenario: str


@dataclass
class PlanDocsResult:
    created: list[Path]
    skipped: list[Path]
    scenario: str


def init_repo(
    repo: Path,
    scenario: str,
    requirements_doc: Path | None,
    canonical_doc: Path | None,
    ai_docs_language: str | None,
    sandbox_mode: str,
    approval_policy: str,
    search_enabled: bool,
    skip_git_repo_check: bool,
    force: bool,
) -> InitResult:
    repo = repo.resolve()
    docs_dir = repo / EN_DOCS_DIR
    zh_dir = repo / ZH_DOCS_DIR
    req_dir = repo / REQUIREMENTS_DOCS_DIR
    created: list[Path] = []
    skipped: list[Path] = []

    docs_dir.mkdir(parents=True, exist_ok=True)
    zh_dir.mkdir(parents=True, exist_ok=True)
    req_dir.mkdir(parents=True, exist_ok=True)

    req_target = repo / ORIGINAL_REQUIREMENTS_PATH
    if requirements_doc is not None:
        _copy_if_needed(requirements_doc, req_target, force, created, skipped)
    elif not req_target.exists():
        req_target.write_text(
            "# User Requirements\n\nAdd or copy the source requirements document here.\n",
            encoding="utf-8",
        )
        created.append(req_target)

    canonical_target = canonical_doc.resolve() if canonical_doc is not None else repo / CANONICAL_PROJECT_DOC_PATH
    if scenario == "existing-code":
        _ensure_existing_code_ready(repo, canonical_target)

    workflow_state = load_workflow_state(repo)
    selected_ai_docs_language = ai_docs_language or str(workflow_state.get("ai_docs_language", "en"))
    ctx = TemplateContext(
        scenario=scenario,
        project_name=repo.name,
        requirements_doc=_rel(repo, req_target),
        canonical_project_doc=_rel(repo, canonical_target),
        file_map=build_file_map(repo),
        current_state=build_current_state(repo, scenario),
        design_seed=build_design_seed(scenario),
        workflow_stage=str(workflow_state.get("stage", "unknown")),
        ai_docs_language=selected_ai_docs_language,
    )

    for filename in REQUIRED_CORE_DOCS:
        _write_text(docs_dir / filename, render_doc(filename, "en", ctx), force, created, skipped)
        _write_text(zh_dir / filename, render_doc(filename, "zh", ctx), force, created, skipped)

    _write_text(
        docs_dir / "SCENARIO.md",
        f"# Repository Scenario\n\nThis repository is currently treated as `{scenario}`.\n",
        force,
        created,
        skipped,
    )
    _write_text(
        zh_dir / "SCENARIO.md",
        f"# 仓库场景\n\n当前仓库被视为 `{scenario}` 场景。\n",
        force,
        created,
        skipped,
    )

    config_text = (
        json.dumps(
            build_runtime_config(
                repo,
                selected_ai_docs_language,
                sandbox_mode=sandbox_mode,
                approval_policy=approval_policy,
                search_enabled=search_enabled,
                skip_git_repo_check=skip_git_repo_check,
            ),
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    _write_text(repo / "codex-loop.json", config_text, force, created, skipped)
    _write_text(repo / "codex-loop.example.json", config_text, force, created, skipped)

    if scenario == "existing-docs":
        report = validate_existing_docs(repo)
        _write_text(docs_dir / "DOCS-VALIDATION-REPORT.md", report, force, created, skipped)
        _write_text(zh_dir / "DOCS-VALIDATION-REPORT.md", report, force, created, skipped)

    set_workflow_state(repo, stage="relay_docs_generated", ai_docs_language=selected_ai_docs_language)
    return InitResult(created=created, skipped=skipped, scenario=scenario)


def build_runtime_config(
    repo: Path,
    ai_docs_language: str,
    sandbox_mode: str,
    approval_policy: str,
    search_enabled: bool,
    skip_git_repo_check: bool,
) -> dict[str, object]:
    ai_docs_dir = SUPPORTED_AI_DOC_LANGUAGES[ai_docs_language]
    return {
        "codex_bin": "codex",
        "codex_command": None,
        "workdir": str(repo),
        "ai_docs_language": ai_docs_language,
        "prompt": (
            f"Read {repo / ai_docs_dir / 'AI-MASTER-PROMPT.md'}, "
            f"then read {repo / CANONICAL_PROJECT_DOC_PATH} as the canonical project document, "
            f"and re-read {repo / ORIGINAL_REQUIREMENTS_PATH} at the start of this round before continuing."
        ),
        "total_timeout_minutes": 300,
        "max_rounds": None,
        "log_dir": None,
        "skip_git_repo_check": skip_git_repo_check,
        "sandbox_mode": sandbox_mode,
        "approval_policy": approval_policy,
        "search_enabled": search_enabled,
        "profile": None,
        "model": None,
        "extra_args": [],
    }


def plan_docs(
    repo: Path,
    scenario: str,
    requirements_doc: Path | None,
    canonical_doc: Path | None,
    ai_docs_language: str,
    force: bool,
) -> PlanDocsResult:
    repo = repo.resolve()
    created: list[Path] = []
    skipped: list[Path] = []

    (repo / PROJECT_DOCS_DIR).mkdir(parents=True, exist_ok=True)
    (repo / REQUIREMENTS_DOCS_DIR).mkdir(parents=True, exist_ok=True)

    req_target = repo / ORIGINAL_REQUIREMENTS_PATH
    if requirements_doc is not None:
        _copy_if_needed(requirements_doc, req_target, force, created, skipped)
    elif not req_target.exists():
        _write_text(
            req_target,
            "# User Requirements\n\nAdd the user's original project request or source requirements document here.\n",
            force,
            created,
            skipped,
        )

    canonical_target = canonical_doc.resolve() if canonical_doc is not None else repo / CANONICAL_PROJECT_DOC_PATH
    canonical_content = build_canonical_project_doc(repo, scenario, req_target)
    _write_text(canonical_target, canonical_content, force, created, skipped)
    _write_text(
        repo / PROJECT_DOC_QUESTIONS_PATH,
        build_project_questions(repo, scenario),
        force,
        created,
        skipped,
    )
    _write_text(
        repo / PROJECT_DOC_STATUS_PATH,
        build_project_doc_status(repo, scenario),
        force,
        created,
        skipped,
    )
    _write_text(
        repo / PLAN_MODE_PROMPT_PATH,
        build_plan_mode_prompt(repo, scenario, canonical_target, ai_docs_language),
        force,
        created,
        skipped,
    )
    set_workflow_state(repo, stage="project_doc_in_refinement", ai_docs_language=ai_docs_language)
    return PlanDocsResult(created=created, skipped=skipped, scenario=scenario)


def detect_scenario(repo: Path) -> str:
    docs_dir = repo / EN_DOCS_DIR
    required = [docs_dir / name for name in REQUIRED_CORE_DOCS]
    if docs_dir.exists() and any(path.exists() for path in required):
        return "existing-docs"
    non_doc_files = [
        path
        for path in repo.iterdir()
        if path.name not in {".git", DOCS_ROOT.name, "docs"} and path.name != ".DS_Store"
    ]
    if any(path.is_dir() or path.suffix not in {".md", ".txt"} for path in non_doc_files):
        return "existing-code"
    if any(path.name not in {"README.md", "README.zh-CN.md"} for path in non_doc_files):
        return "existing-code"
    return "blank"


def build_file_map(repo: Path, limit: int = 60) -> str:
    lines: list[str] = []
    count = 0
    for path in sorted(repo.rglob("*")):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        rel = path.relative_to(repo)
        if path.is_dir():
            continue
        lines.append(f"- `{rel.as_posix()}`")
        count += 1
        if count >= limit:
            lines.append("- `...`")
            break
    return "\n".join(lines) if lines else "- Repository contents have not been created yet."


def build_current_state(repo: Path, scenario: str) -> str:
    if scenario == "blank":
        return "The repository is treated as blank. No implementation baseline has been confirmed yet."
    if scenario == "existing-docs":
        return "A documentation system already exists. Review and normalize it before starting new implementation work."
    file_count = len([path for path in repo.rglob("*") if path.is_file() and ".git" not in path.parts])
    return (
        f"The repository already contains code or assets. Initial scan found {file_count} files outside ignored internals. "
        "Automatic development must not start until the canonical project document has been refined with the user until no material ambiguity remains."
    )


def build_design_seed(scenario: str) -> str:
    if scenario == "blank":
        return "Start from the user requirements and define the first stable architecture baseline."
    if scenario == "existing-docs":
        return "Preserve the current documentation system and only fill missing decisions or mismatches."
    return "Inspect the current codebase first, then document the actual architecture rather than rewriting it from scratch."


def validate_existing_docs(repo: Path) -> str:
    docs_dir = repo / EN_DOCS_DIR
    missing = [name for name in REQUIRED_CORE_DOCS if not (docs_dir / name).exists()]
    if not missing:
        return "# Docs Validation Report\n\nAll required core docs were present during initialization.\n"
    bullet_list = "\n".join(f"- {name}" for name in missing)
    return f"# Docs Validation Report\n\nMissing core docs were generated:\n{bullet_list}\n"


def validate_run_readiness(repo: Path) -> None:
    workflow_state = load_workflow_state(repo)
    ai_docs_language = str(workflow_state.get("ai_docs_language", "en"))
    ai_docs_dir = SUPPORTED_AI_DOC_LANGUAGES.get(ai_docs_language, EN_DOCS_DIR)
    canonical_doc = repo / CANONICAL_PROJECT_DOC_PATH
    original_doc = repo / ORIGINAL_REQUIREMENTS_PATH
    if not canonical_doc.exists():
        raise FileNotFoundError(
            "Canonical project document missing. This is the most important development foundation. "
            "Run `codex-loop plan-docs` first and refine it with the user."
        )
    if not original_doc.exists():
        raise FileNotFoundError(
            "Original user project document missing. The autonomous loop must re-read it at the start of every round."
        )
    missing = [name for name in REQUIRED_CORE_DOCS if not (repo / ai_docs_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Relay docs are incomplete. Run `codex-loop init` after the canonical project document is ready. "
            f"Missing files: {', '.join(missing)}"
        )


def load_workflow_state(repo: Path) -> dict[str, object]:
    path = repo / WORKFLOW_STATE_PATH
    if not path.exists():
        return {"stage": "project_doc_missing", "ai_docs_language": "en"}
    return json.loads(path.read_text(encoding="utf-8"))


def set_workflow_state(repo: Path, stage: str, ai_docs_language: str) -> None:
    path = repo / WORKFLOW_STATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "stage": stage,
        "ai_docs_language": ai_docs_language,
        "canonical_project_doc": str(CANONICAL_PROJECT_DOC_PATH).replace("\\", "/"),
        "original_requirements_doc": str(ORIGINAL_REQUIREMENTS_PATH).replace("\\", "/"),
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_canonical_project_doc(repo: Path, scenario: str, requirements_doc: Path) -> str:
    return (
        "# Canonical Project Document\n\n"
        "This file is the direct baseline for generating the relay documentation set and for autonomous execution.\n"
        "It must be refined with the user until there is no material ambiguity left.\n\n"
        "## Source Inputs\n\n"
        f"- Original user document: `{_rel(repo, requirements_doc)}`\n"
        "## Completion Rule\n\n"
        "- Do not use this file as final truth until all important ambiguities have been resolved with the user.\n"
        "- During autonomous execution, the AI must still re-read the original user document at the start of every round.\n\n"
        "## Sections To Fill\n\n"
        "- Project goal and target users\n"
        "- In-scope and out-of-scope behaviors\n"
        "- Current codebase state and architecture\n"
        "- Confirmed constraints and decisions\n"
        "- Open questions that must be resolved before implementation\n"
        "- Acceptance criteria\n"
    )


def build_project_questions(repo: Path, scenario: str) -> str:
    return (
        "# Project Document Questions\n\n"
        "Use this file to track unresolved items while refining the canonical project document.\n\n"
        f"- Scenario: `{scenario}`\n"
        "- Which behaviors are already implemented and must be preserved?\n"
        "- Which parts of the current codebase are incomplete, experimental, or obsolete?\n"
        "- What exact outcomes define success for this project?\n"
        "- Which constraints are architectural, business, platform, or delivery constraints?\n"
        "- Which ambiguities still block safe autonomous development?\n"
    )


def build_project_doc_status(repo: Path, scenario: str) -> str:
    return (
        "# Project Document Status\n\n"
        f"- Scenario: `{scenario}`\n"
        "- Current state: project-doc in refinement\n"
        "- Rule: do not generate the final relay docs or start autonomous development until the canonical project document is ambiguity-free.\n"
        "- User guidance: provide the original requirements document and keep it as the permanent source of truth.\n"
    )


def build_plan_mode_prompt(repo: Path, scenario: str, canonical_doc: Path, ai_docs_language: str) -> str:
    return (
        "# Plan Mode Prompt\n\n"
        "Use Codex Plan Mode to refine this repository into a complete, ambiguity-free project document before implementation.\n\n"
        f"- Scenario: `{scenario}`\n"
        f"- Target AI document language for the full workflow: `{ai_docs_language}`\n"
        f"- Read the codebase and `{ORIGINAL_REQUIREMENTS_PATH.as_posix()}`.\n"
        f"- Continuously question the user until `{_rel(repo, canonical_doc)}` is detailed enough to act as the canonical project document.\n"
        "- Do not start automatic development during this phase.\n"
        "- The project document is the most important development foundation.\n"
    )


def _ensure_existing_code_ready(repo: Path, canonical_doc: Path) -> None:
    if not canonical_doc.exists():
        raise FileNotFoundError(
            "Canonical project document missing for existing-code workflow. "
            "This project document is the most important development foundation. "
            "Run `codex-loop plan-docs --repo <path>` "
            "before `codex-loop init existing-code`."
        )
    workflow_state = load_workflow_state(repo)
    set_workflow_state(repo, stage="project_doc_canonicalized", ai_docs_language=str(workflow_state.get("ai_docs_language", "en")))


def _copy_if_needed(source: Path, target: Path, force: bool, created: list[Path], skipped: list[Path]) -> None:
    if target.exists() and not force:
        skipped.append(target)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    created.append(target)


def _write_text(
    path: Path,
    content: str,
    force: bool,
    created: list[Path],
    skipped: list[Path],
) -> None:
    if path.exists() and not force:
        skipped.append(path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(path)


def _rel(repo: Path, path: Path) -> str:
    return path.resolve().relative_to(repo.resolve()).as_posix()
