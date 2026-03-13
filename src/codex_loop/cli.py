from __future__ import annotations

import argparse
import json
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
        "--input-doc",
        help="Optional path to user-provided project documentation. It will be copied and then refined, not used directly as final truth.",
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
        input_doc = Path(args.input_doc).resolve() if args.input_doc else None
        canonical_doc = Path(args.canonical_doc).resolve() if args.canonical_doc else None
        result = plan_docs(
            repo=repo,
            scenario="existing-code" if scenario == "auto" else scenario,
            requirements_doc=requirements_doc,
            input_doc=input_doc,
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
