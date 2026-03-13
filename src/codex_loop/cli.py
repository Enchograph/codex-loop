from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from codex_loop.loop import LoopRunner, load_config
from codex_loop.scaffold import (
    CANONICAL_PROJECT_DOC_PATH,
    SUPPORTED_APPROVAL_POLICIES,
    SUPPORTED_AI_DOC_LANGUAGES,
    SUPPORTED_SANDBOX_MODES,
    detect_scenario,
    init_repo,
    plan_docs,
    validate_run_readiness,
)

INTERACTIVE_COMMANDS = {"init", "plan-docs", "run", "inspect"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-loop",
        description="Generate Codex relay docs and run supervised Codex development loops.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Generate or normalize the relay documentation system.")
    init_parser.add_argument(
        "scenario",
        nargs="?",
        choices=["blank", "existing-code", "existing-docs", "auto"],
        default="auto",
        help="Repository scenario to initialize. Defaults to automatic detection.",
    )
    init_parser.add_argument("--repo", default=".", help="Repository path. Defaults to the current directory.")
    init_parser.add_argument(
        "--requirements-doc",
        help="Optional path to the source requirements document that will be copied into docs/requirements/USER-REQUIREMENTS.md.",
    )
    init_parser.add_argument(
        "--canonical-doc",
        help=f"Optional canonical project document path. Defaults to {CANONICAL_PROJECT_DOC_PATH.as_posix()}.",
    )
    init_parser.add_argument(
        "--ai-doc-language",
        choices=sorted(SUPPORTED_AI_DOC_LANGUAGES.keys()),
        default=None,
        help="Language of the document set that will be fed to AI through the full workflow.",
    )
    init_parser.add_argument(
        "--sandbox-mode",
        choices=sorted(SUPPORTED_SANDBOX_MODES),
        default="workspace-write",
        help="Default Codex sandbox mode for the third-stage runtime.",
    )
    init_parser.add_argument(
        "--approval-policy",
        choices=sorted(SUPPORTED_APPROVAL_POLICIES),
        default="on-request",
        help="Default Codex approval policy for the third-stage runtime.",
    )
    init_parser.add_argument(
        "--search-enabled",
        dest="search_enabled",
        action="store_true",
        default=True,
        help="Enable web search during the runtime loop.",
    )
    init_parser.add_argument(
        "--no-search-enabled",
        dest="search_enabled",
        action="store_false",
        help="Disable web search during the runtime loop.",
    )
    init_parser.add_argument(
        "--skip-git-repo-check",
        action="store_true",
        help="Write the runtime config so Codex skips the initial git repo check.",
    )
    init_parser.add_argument("--force", action="store_true", help="Overwrite generated files if they already exist.")

    plan_parser = subparsers.add_parser(
        "plan-docs",
        help="Prepare the canonical project-document workflow before formal relay-doc generation.",
    )
    plan_parser.add_argument("scenario", nargs="?", choices=["existing-code", "auto"], default="auto")
    plan_parser.add_argument("--repo", default=".", help="Repository path. Defaults to the current directory.")
    plan_parser.add_argument(
        "--requirements-doc",
        help="Optional path to the user's original project or requirements document.",
    )
    plan_parser.add_argument(
        "--canonical-doc",
        help=f"Optional canonical project document path. Defaults to {CANONICAL_PROJECT_DOC_PATH.as_posix()}.",
    )
    plan_parser.add_argument(
        "--ai-doc-language",
        choices=sorted(SUPPORTED_AI_DOC_LANGUAGES.keys()),
        default="en",
        help="Language of the document set that will be fed to AI through the full workflow.",
    )
    plan_parser.add_argument("--force", action="store_true", help="Overwrite generated files if they already exist.")

    run_parser = subparsers.add_parser("run", help="Start the supervised Codex development loop.")
    run_parser.add_argument("--config", default="codex-loop.json", help="Path to the runtime JSON config.")
    run_parser.add_argument(
        "--sandbox-mode",
        choices=sorted(SUPPORTED_SANDBOX_MODES),
        help="Override the configured sandbox mode for this run.",
    )
    run_parser.add_argument(
        "--approval-policy",
        choices=sorted(SUPPORTED_APPROVAL_POLICIES),
        help="Override the configured approval policy for this run.",
    )
    run_parser.add_argument(
        "--search-enabled",
        dest="search_enabled",
        action="store_true",
        default=None,
        help="Override and enable web search for this run.",
    )
    run_parser.add_argument(
        "--no-search-enabled",
        dest="search_enabled",
        action="store_false",
        help="Override and disable web search for this run.",
    )
    run_parser.add_argument(
        "--skip-git-repo-check",
        dest="skip_git_repo_check",
        action="store_true",
        default=None,
        help="Override and make Codex skip the git repo check for this run.",
    )
    run_parser.add_argument(
        "--no-skip-git-repo-check",
        dest="skip_git_repo_check",
        action="store_false",
        help="Override and require the git repo check for this run.",
    )

    inspect_parser = subparsers.add_parser("inspect", help="Print the detected repository scenario as JSON.")
    inspect_parser.add_argument("--repo", default=".", help="Repository path. Defaults to the current directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = _expand_interactive_argv(argv)
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        repo = Path(args.repo).resolve()
        scenario = detect_scenario(repo) if args.scenario == "auto" else args.scenario
        requirements_doc = Path(args.requirements_doc).resolve() if args.requirements_doc else None
        canonical_doc = Path(args.canonical_doc).resolve() if args.canonical_doc else None
        result = init_repo(
            repo=repo,
            scenario=scenario,
            requirements_doc=requirements_doc,
            canonical_doc=canonical_doc,
            ai_docs_language=args.ai_doc_language,
            sandbox_mode=args.sandbox_mode,
            approval_policy=args.approval_policy,
            search_enabled=args.search_enabled,
            skip_git_repo_check=args.skip_git_repo_check,
            force=args.force,
        )
        payload = {
            "scenario": result.scenario,
            "created": [str(path.relative_to(repo)) for path in result.created],
            "skipped": [str(path.relative_to(repo)) for path in result.skipped],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "plan-docs":
        repo = Path(args.repo).resolve()
        scenario = detect_scenario(repo) if args.scenario == "auto" else args.scenario
        requirements_doc = Path(args.requirements_doc).resolve() if args.requirements_doc else None
        canonical_doc = Path(args.canonical_doc).resolve() if args.canonical_doc else None
        result = plan_docs(
            repo=repo,
            scenario="existing-code" if scenario == "auto" else scenario,
            requirements_doc=requirements_doc,
            canonical_doc=canonical_doc,
            ai_docs_language=args.ai_doc_language,
            force=args.force,
        )
        payload = {
            "scenario": result.scenario,
            "created": [str(path.relative_to(repo)) for path in result.created],
            "skipped": [str(path.relative_to(repo)) for path in result.skipped],
            "next_step": "Refine the canonical project document with the user in Plan Mode until no material ambiguity remains, then run `codex-loop init existing-code`.",
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "inspect":
        repo = Path(args.repo).resolve()
        print(json.dumps({"scenario": detect_scenario(repo)}, ensure_ascii=False))
        return 0

    config = load_config(Path(args.config).resolve())
    if args.sandbox_mode is not None:
        config.sandbox_mode = args.sandbox_mode
    if args.approval_policy is not None:
        config.approval_policy = args.approval_policy
    if args.search_enabled is not None:
        config.search_enabled = args.search_enabled
    if args.skip_git_repo_check is not None:
        config.skip_git_repo_check = args.skip_git_repo_check
    validate_run_readiness(config.workdir)
    runner = LoopRunner(config)
    return runner.run()


def _expand_interactive_argv(argv: list[str] | None) -> list[str]:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    if not raw_argv:
        return _interactive_root_menu()
    if len(raw_argv) == 1 and raw_argv[0] in INTERACTIVE_COMMANDS:
        return _interactive_command_menu(raw_argv[0])
    return raw_argv


def _interactive_root_menu() -> list[str]:
    print("Codex Loop interactive mode")
    command = _choose_option(
        "Choose a command",
        ["init", "plan-docs", "run", "inspect"],
        default_index=0,
    )
    return _interactive_command_menu(command)


def _interactive_command_menu(command: str) -> list[str]:
    if command == "init":
        return _interactive_init_args()
    if command == "plan-docs":
        return _interactive_plan_docs_args()
    if command == "run":
        return _interactive_run_args()
    return _interactive_inspect_args()


def _interactive_init_args() -> list[str]:
    repo = _prompt_text("Repository path", ".")
    scenario = _choose_option("Scenario", ["auto", "blank", "existing-code", "existing-docs"], 0)
    requirements_doc = _prompt_text("Requirements document path (optional)", "")
    canonical_doc = _prompt_text("Canonical project document path (optional)", "")
    ai_doc_language = _choose_option("AI document language", sorted(SUPPORTED_AI_DOC_LANGUAGES.keys()), 0)
    sandbox_mode = _choose_option("Sandbox mode", sorted(SUPPORTED_SANDBOX_MODES), 2)
    approval_policy = _choose_option("Approval policy", sorted(SUPPORTED_APPROVAL_POLICIES), 2)
    search_enabled = _choose_bool("Enable web search", True)
    skip_git_repo_check = _choose_bool("Skip git repo check", False)
    force = _choose_bool("Overwrite generated files if they exist", False)

    args = ["init", scenario, "--repo", repo, "--ai-doc-language", ai_doc_language, "--sandbox-mode", sandbox_mode, "--approval-policy", approval_policy]
    if requirements_doc:
        args.extend(["--requirements-doc", requirements_doc])
    if canonical_doc:
        args.extend(["--canonical-doc", canonical_doc])
    args.append("--search-enabled" if search_enabled else "--no-search-enabled")
    if skip_git_repo_check:
        args.append("--skip-git-repo-check")
    if force:
        args.append("--force")
    return args


def _interactive_plan_docs_args() -> list[str]:
    repo = _prompt_text("Repository path", ".")
    scenario = _choose_option("Scenario", ["auto", "existing-code"], 0)
    requirements_doc = _prompt_text("Original user document path (optional)", "")
    canonical_doc = _prompt_text("Canonical project document path (optional)", "")
    ai_doc_language = _choose_option("AI document language", sorted(SUPPORTED_AI_DOC_LANGUAGES.keys()), 0)
    force = _choose_bool("Overwrite generated files if they exist", False)

    args = ["plan-docs", scenario, "--repo", repo, "--ai-doc-language", ai_doc_language]
    if requirements_doc:
        args.extend(["--requirements-doc", requirements_doc])
    if canonical_doc:
        args.extend(["--canonical-doc", canonical_doc])
    if force:
        args.append("--force")
    return args


def _interactive_run_args() -> list[str]:
    config = _prompt_text("Runtime config path", "codex-loop.json")
    sandbox_mode = _choose_option(
        "Sandbox mode override",
        ["keep-config"] + sorted(SUPPORTED_SANDBOX_MODES),
        0,
    )
    approval_policy = _choose_option(
        "Approval policy override",
        ["keep-config"] + sorted(SUPPORTED_APPROVAL_POLICIES),
        0,
    )
    search_mode = _choose_option("Search override", ["keep-config", "enabled", "disabled"], 0)
    git_check_mode = _choose_option("Git repo check override", ["keep-config", "skip", "require"], 0)

    args = ["run", "--config", config]
    if sandbox_mode != "keep-config":
        args.extend(["--sandbox-mode", sandbox_mode])
    if approval_policy != "keep-config":
        args.extend(["--approval-policy", approval_policy])
    if search_mode == "enabled":
        args.append("--search-enabled")
    elif search_mode == "disabled":
        args.append("--no-search-enabled")
    if git_check_mode == "skip":
        args.append("--skip-git-repo-check")
    elif git_check_mode == "require":
        args.append("--no-skip-git-repo-check")
    return args


def _interactive_inspect_args() -> list[str]:
    repo = _prompt_text("Repository path", ".")
    return ["inspect", "--repo", repo]


def _choose_option(prompt: str, options: list[str], default_index: int) -> str:
    print(f"{prompt}:")
    for index, option in enumerate(options, start=1):
        marker = " (default)" if index - 1 == default_index else ""
        print(f"  {index}. {option}{marker}")
    while True:
        raw = input("> ").strip()
        if not raw:
            return options[default_index]
        if raw.isdigit():
            index = int(raw) - 1
            if 0 <= index < len(options):
                return options[index]
        print("Enter the number of one of the listed options, or press Enter for the default.")


def _choose_bool(prompt: str, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} [{suffix}]: ").strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Enter y or n, or press Enter for the default.")


def _prompt_text(prompt: str, default: str) -> str:
    label = f"{prompt} [{default}]" if default else f"{prompt} [leave empty to skip]"
    raw = input(f"{label}: ").strip()
    if not raw:
        return default
    return raw
