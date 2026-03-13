from __future__ import annotations

import json
import stat
import sys
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from codex_loop.cli import main
from codex_loop.loop import LoopConfig, LoopRunner
from codex_loop.scaffold import CANONICAL_PROJECT_DOC_PATH, EN_DOCS_DIR, ORIGINAL_REQUIREMENTS_PATH


def _write_fake_codex(path: Path) -> None:
    script = """#!/usr/bin/env python3
import pathlib
import sys

args = sys.argv[1:]
output = pathlib.Path(args[args.index("-o") + 1])
output.write_text("fake final message\\n", encoding="utf-8")
print("fake stdout")
print("fake stderr", file=sys.stderr)
raise SystemExit(0)
"""
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


class RunTests(unittest.TestCase):
    def test_inspect_subcommand_without_args_uses_interactive_menu(self) -> None:
        with patch("builtins.input", side_effect=["."]):
            exit_code = main(["inspect"])

        self.assertEqual(exit_code, 0)

    def test_build_command_uses_search_and_on_failure(self) -> None:
        tmp_path = Path.cwd() / ".tmp-tests" / "build-command"
        if tmp_path.exists():
            shutil.rmtree(tmp_path)
        tmp_path.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, tmp_path, True)
        config = LoopConfig(
            codex_bin="codex",
            codex_command=None,
            workdir=tmp_path,
            prompt="Prompt",
            total_timeout_minutes=1,
            max_rounds=1,
            log_dir=tmp_path / "logs",
            skip_git_repo_check=False,
            sandbox_mode="workspace-write",
            approval_policy="on-failure",
            search_enabled=True,
            profile=None,
            model=None,
            extra_args=[],
        )
        runner = LoopRunner(config)
        command = runner._build_command(tmp_path / "final-message.txt")

        self.assertIn("--ask-for-approval", command)
        self.assertIn("on-failure", command)
        self.assertIn("--search", command)
        self.assertNotIn("--enable", command)

    def test_run_requires_canonical_project_doc(self) -> None:
        tmp_path = Path.cwd() / ".tmp-tests" / "run-missing-canonical"
        if tmp_path.exists():
            shutil.rmtree(tmp_path)
        tmp_path.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, tmp_path, True)
        workdir = tmp_path / "repo"
        workdir.mkdir()
        config = {
            "codex_bin": None,
            "codex_command": [sys.executable, "-c", "print('noop')"],
            "workdir": str(workdir),
            "prompt": "Prompt",
            "total_timeout_minutes": 1,
            "max_rounds": 1,
            "log_dir": str(tmp_path / "logs"),
            "skip_git_repo_check": False,
            "sandbox_mode": "workspace-write",
            "approval_policy": "on-request",
            "search_enabled": False,
            "profile": None,
            "model": None,
            "extra_args": [],
        }
        config_path = tmp_path / "codex-loop.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")

        with self.assertRaises(FileNotFoundError):
            main(["run", "--config", str(config_path)])

    def test_run_with_codex_command(self) -> None:
        tmp_path = Path.cwd() / ".tmp-tests" / "run-loop"
        if tmp_path.exists():
            shutil.rmtree(tmp_path)
        tmp_path.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, tmp_path, True)
        fake_codex = tmp_path / "fake_codex.py"
        _write_fake_codex(fake_codex)
        workdir = tmp_path / "repo"
        workdir.mkdir()
        docs_dir = workdir / EN_DOCS_DIR
        docs_dir.mkdir(parents=True)
        (workdir / ORIGINAL_REQUIREMENTS_PATH).parent.mkdir(parents=True, exist_ok=True)
        (workdir / ORIGINAL_REQUIREMENTS_PATH).write_text("# Original\n", encoding="utf-8")
        (workdir / CANONICAL_PROJECT_DOC_PATH).parent.mkdir(parents=True, exist_ok=True)
        (workdir / CANONICAL_PROJECT_DOC_PATH).write_text("# Canonical\n", encoding="utf-8")
        for name in [
            "AI-START-HERE.md",
            "AI-MASTER-PROMPT.md",
            "PROJECT-ROADMAP.md",
            "PROJECT-TODO.md",
            "PROJECT-STATUS.md",
            "PROJECT-HANDOFF.md",
            "PROJECT-DECISIONS.md",
            "PROJECT-ACCEPTANCE.md",
            "PROJECT-FILE-MAP.md",
            "PROJECT-CHANGELOG.md",
            "PROJECT-DESIGN.md",
            "PROJECT-TASK-BREAKDOWN.md",
        ]:
            (docs_dir / name).write_text(f"# {name}\n", encoding="utf-8")
        config = {
            "codex_bin": None,
            "codex_command": [sys.executable, str(fake_codex)],
            "workdir": str(workdir),
            "prompt": "Prompt",
            "total_timeout_minutes": 1,
            "max_rounds": 1,
            "log_dir": str(tmp_path / "logs"),
            "skip_git_repo_check": False,
            "sandbox_mode": "workspace-write",
            "approval_policy": "on-request",
            "search_enabled": False,
            "profile": None,
            "model": None,
            "extra_args": [],
        }
        config_path = tmp_path / "codex-loop.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")

        exit_code = main(["run", "--config", str(config_path)])

        self.assertEqual(exit_code, 0)
        final_messages = list((tmp_path / "logs").rglob("final-message.txt"))
        self.assertTrue(final_messages)
        self.assertIn("fake final message", final_messages[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
