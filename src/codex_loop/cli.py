from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from codex_loop.codex import launch_interactive_codex
from codex_loop.i18n import get_messages, resolve_language
from codex_loop.interactive import choose_option, prompt_bool, prompt_text
from codex_loop.runtime import LoopRunner, load_config
from codex_loop.scaffold import (
    CANONICAL_PROJECT_DOC_PATH,
    CODEX_LOOP_CONFIG_DIR,
    CODEX_LOOP_DIR,
    USER_REQUIREMENTS_PATH,
    detect_scenario,
    generate_init_prompt,
    generate_plan_prompt,
    init_repo,
    inspect_repo,
    plan_docs,
    validate_run_readiness,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-loop",
        description="Generate Codex relay docs and run supervised Codex development loops.",
    )
    parser.add_argument("--language", default=None, help="CLI language, for example en or zh-CN.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Print detected repository scenario as JSON.")
    inspect_parser.add_argument("--repo", default=".", help="Repository path.")

    plan_parser = subparsers.add_parser("plan-docs", help="Prepare base requirements docs and launch interactive Codex.")
    _add_repo_args(plan_parser)
    plan_parser.add_argument("scenario", nargs="?", choices=["existing-code", "auto"], default="auto")
    plan_parser.add_argument("--requirements-doc", help="Path to the original user requirements document.")
    plan_parser.add_argument("--ai-doc-language", default=None, help="Output language for generated documents.")
    plan_parser.add_argument("--codex-bin", default="codex", help="Codex binary name or path.")
    plan_parser.add_argument("--model", default=None, help="Optional Codex model override.")
    plan_parser.add_argument("--profile", default=None, help="Optional Codex profile override.")
    plan_parser.add_argument("--no-search", action="store_true", help="Disable web search during interactive planning.")
    plan_parser.add_argument("--force", action="store_true", help="Overwrite generated files if they already exist.")

    init_parser = subparsers.add_parser("init", help="Generate relay docs and runtime config, then launch interactive Codex.")
    _add_repo_args(init_parser)
    init_parser.add_argument("--requirements-doc", help="Path to the finalized base requirements document.")
    init_parser.add_argument("--ai-doc-language", default=None, help="Output language for generated documents.")
    init_parser.add_argument("--codex-bin", default="codex", help="Codex binary name or path.")
    init_parser.add_argument("--model", default=None, help="Optional Codex model override.")
    init_parser.add_argument("--profile", default=None, help="Optional Codex profile override.")
    init_parser.add_argument("--sandbox-mode", default="workspace-write", choices=["read-only", "workspace-write", "danger-full-access"])
    init_parser.add_argument("--approval-policy", default="on-request", choices=["untrusted", "on-request", "never"])
    init_parser.add_argument("--no-search", action="store_true", help="Disable web search during init.")
    init_parser.add_argument("--skip-git-repo-check", action="store_true")
    init_parser.add_argument("--force", action="store_true", help="Overwrite generated files if they already exist.")

    run_parser = subparsers.add_parser("run", help="Run unattended Codex exec rounds from JSON config.")
    run_parser.add_argument("--config", default=CODEX_LOOP_CONFIG_DIR.joinpath("codex-loop.json").as_posix(), help="Runtime config path.")
    run_parser.add_argument("--sandbox-mode", choices=["read-only", "workspace-write", "danger-full-access"])
    run_parser.add_argument("--approval-policy", choices=["untrusted", "on-request", "never"])
    run_parser.add_argument("--search-enabled", dest="search_enabled", action="store_true", default=None)
    run_parser.add_argument("--no-search-enabled", dest="search_enabled", action="store_false")
    run_parser.add_argument("--skip-git-repo-check", dest="skip_git_repo_check", action="store_true", default=None)
    run_parser.add_argument("--no-skip-git-repo-check", dest="skip_git_repo_check", action="store_false")
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = _expand_interactive_argv(argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    cli_language = resolve_language(getattr(args, "language", None))

    if args.command == "inspect":
        repo = Path(args.repo).resolve()
        payload = inspect_repo(repo)
        print(json.dumps(payload.__dict__, indent=2, ensure_ascii=False))
        return 0

    if args.command == "plan-docs":
        repo = Path(args.repo).resolve()
        scenario = detect_scenario(repo) if args.scenario == "auto" else args.scenario
        doc_language = resolve_language(args.ai_doc_language or cli_language)
        result = plan_docs(
            repo=repo,
            scenario=scenario,
            requirements_doc=Path(args.requirements_doc).resolve() if args.requirements_doc else None,
            canonical_doc=None,
            ai_docs_language=doc_language,
            force=args.force,
        )
        prompt = generate_plan_prompt(repo, doc_language, scenario)
        exit_code = launch_interactive_codex(
            prompt=prompt,
            cwd=repo,
            codex_bin=args.codex_bin,
            search_enabled=not args.no_search,
            model=args.model,
            profile=args.profile,
        )
        print(json.dumps(_scaffold_payload(repo, result), indent=2, ensure_ascii=False))
        return exit_code

    if args.command == "init":
        repo = Path(args.repo).resolve()
        scenario = detect_scenario(repo)
        doc_language = resolve_language(args.ai_doc_language or cli_language)
        result = init_repo(
            repo=repo,
            scenario=scenario,
            requirements_doc=Path(args.requirements_doc).resolve() if args.requirements_doc else None,
            canonical_doc=None,
            ai_docs_language=doc_language,
            sandbox_mode=args.sandbox_mode,
            approval_policy=args.approval_policy,
            search_enabled=not args.no_search,
            skip_git_repo_check=args.skip_git_repo_check,
            force=args.force,
        )
        prompt = generate_init_prompt(repo, doc_language, scenario)
        exit_code = launch_interactive_codex(
            prompt=prompt,
            cwd=repo,
            codex_bin=args.codex_bin,
            search_enabled=not args.no_search,
            sandbox_mode=args.sandbox_mode,
            approval_policy=args.approval_policy,
            model=args.model,
            profile=args.profile,
        )
        print(json.dumps(_scaffold_payload(repo, result), indent=2, ensure_ascii=False))
        return exit_code

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
    return LoopRunner(config).run()


def _add_repo_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", default=".", help="Repository path.")


def _scaffold_payload(repo: Path, result: object) -> dict[str, object]:
    return {
        "scenario": getattr(result, "scenario"),
        "created": [str(path.relative_to(repo)) for path in getattr(result, "created")],
        "skipped": [str(path.relative_to(repo)) for path in getattr(result, "skipped")],
        "requirements_doc": USER_REQUIREMENTS_PATH.as_posix(),
        "canonical_doc": CANONICAL_PROJECT_DOC_PATH.as_posix(),
    }


def _expand_interactive_argv(argv: list[str] | None) -> list[str]:
    raw = list(sys.argv[1:] if argv is None else argv)
    if raw:
        return raw

    repo = str(Path.cwd())
    cli_language = choose_option("Language / 语言", ["en", "zh-CN"], default_index=0)
    messages = get_messages(cli_language)
    print(messages.interactive_title)
    print(f"{messages.using_current_repo}: {repo}")
    command = choose_option(messages.choose_command, ["inspect", "plan-docs", "init", "run"], language=cli_language)
    if command == "inspect":
        return ["--language", cli_language, "inspect", "--repo", repo]
    if command == "plan-docs":
        scenario = choose_option("Scenario", ["auto", "existing-code"], language=cli_language)
        requirements_doc = prompt_text("Requirements doc", "")
        ai_language = prompt_text(messages.prompt_language, cli_language)
        use_search = prompt_bool("Enable web search", True, language=cli_language)
        force = prompt_bool("Overwrite existing generated files", False, language=cli_language)
        args = ["--language", cli_language, "plan-docs", scenario, "--repo", repo, "--ai-doc-language", ai_language]
        if requirements_doc:
            args.extend(["--requirements-doc", requirements_doc])
        if not use_search:
            args.append("--no-search")
        if force:
            args.append("--force")
        return args
    if command == "init":
        requirements_doc = prompt_text("Requirements doc", "")
        ai_language = prompt_text(messages.prompt_language, cli_language)
        sandbox_mode = choose_option("Sandbox mode", ["read-only", "workspace-write", "danger-full-access"], default_index=1, language=cli_language)
        approval_policy = choose_option("Approval policy", ["untrusted", "on-request", "never"], default_index=1, language=cli_language)
        use_search = prompt_bool("Enable web search", True, language=cli_language)
        skip_git_repo_check = prompt_bool("Skip git repo check in runtime config", False, language=cli_language)
        force = prompt_bool("Overwrite existing generated files", False, language=cli_language)
        args = [
            "--language",
            cli_language,
            "init",
            "--repo",
            repo,
            "--ai-doc-language",
            ai_language,
            "--sandbox-mode",
            sandbox_mode,
            "--approval-policy",
            approval_policy,
        ]
        if requirements_doc:
            args.extend(["--requirements-doc", requirements_doc])
        if not use_search:
            args.append("--no-search")
        if skip_git_repo_check:
            args.append("--skip-git-repo-check")
        if force:
            args.append("--force")
        return args
    config = prompt_text("Runtime config path", CODEX_LOOP_CONFIG_DIR.joinpath("codex-loop.json").as_posix())
    args = ["--language", cli_language, "run", "--config", config]
    sandbox_override = choose_option("Sandbox override", ["keep-config", "read-only", "workspace-write", "danger-full-access"], language=cli_language)
    approval_override = choose_option("Approval override", ["keep-config", "untrusted", "on-request", "never"], language=cli_language)
    search_override = choose_option("Search override", ["keep-config", "enabled", "disabled"], language=cli_language)
    git_override = choose_option("Git check override", ["keep-config", "skip", "require"], language=cli_language)
    if sandbox_override != "keep-config":
        args.extend(["--sandbox-mode", sandbox_override])
    if approval_override != "keep-config":
        args.extend(["--approval-policy", approval_override])
    if search_override == "enabled":
        args.append("--search-enabled")
    elif search_override == "disabled":
        args.append("--no-search-enabled")
    if git_override == "skip":
        args.append("--skip-git-repo-check")
    elif git_override == "require":
        args.append("--no-skip-git-repo-check")
    return args
