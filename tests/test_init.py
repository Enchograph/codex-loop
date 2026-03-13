from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from codex_loop.cli import main
from codex_loop.scaffold import CANONICAL_PROJECT_DOC_PATH, EN_DOCS_DIR, detect_scenario


def workspace_temp_dir(name: str) -> Path:
    root = Path.cwd() / ".tmp-tests"
    root.mkdir(exist_ok=True)
    target = root / name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    return target


class InitTests(unittest.TestCase):
    def test_detect_blank_repo(self) -> None:
        tmp_path = workspace_temp_dir("init-detect-blank")
        self.addCleanup(shutil.rmtree, tmp_path, True)
        self.assertEqual(detect_scenario(tmp_path), "blank")

    def test_init_blank_repo_generates_docs(self) -> None:
        tmp_path = workspace_temp_dir("init-blank")
        self.addCleanup(shutil.rmtree, tmp_path, True)
        requirements = tmp_path / "requirements.md"
        requirements.write_text("# Requirements\n", encoding="utf-8")

        exit_code = main(
            [
                "init",
                "blank",
                "--repo",
                str(tmp_path),
                "--requirements-doc",
                str(requirements),
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertTrue((tmp_path / EN_DOCS_DIR / "AI-START-HERE.md").exists())
        self.assertTrue((tmp_path / "codex-loop-docs" / "zh-CN" / "AI-START-HERE.md").exists())
        self.assertTrue((tmp_path / "codex-loop-docs" / "requirements" / "USER-REQUIREMENTS.md").exists())
        config = json.loads((tmp_path / "codex-loop.json").read_text(encoding="utf-8"))
        self.assertEqual(config["workdir"], str(tmp_path.resolve()))

    def test_init_existing_docs_adds_validation_report(self) -> None:
        tmp_path = workspace_temp_dir("init-existing-docs")
        self.addCleanup(shutil.rmtree, tmp_path, True)
        docs_dir = tmp_path / EN_DOCS_DIR
        docs_dir.mkdir(parents=True)
        (docs_dir / "AI-START-HERE.md").write_text("x", encoding="utf-8")

        exit_code = main(["init", "existing-docs", "--repo", str(tmp_path)])

        self.assertEqual(exit_code, 0)
        self.assertTrue((tmp_path / EN_DOCS_DIR / "DOCS-VALIDATION-REPORT.md").exists())

    def test_plan_docs_creates_canonical_project_doc(self) -> None:
        tmp_path = workspace_temp_dir("plan-docs")
        self.addCleanup(shutil.rmtree, tmp_path, True)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("print('x')\n", encoding="utf-8")
        project_doc = tmp_path / "input-project-doc.md"
        project_doc.write_text("# Existing Project Doc\n", encoding="utf-8")

        exit_code = main(
            [
                "plan-docs",
                "--repo",
                str(tmp_path),
                "--input-doc",
                str(project_doc),
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertTrue((tmp_path / CANONICAL_PROJECT_DOC_PATH).exists())
        self.assertTrue((tmp_path / "codex-loop-docs" / "project" / "USER-PROVIDED-PROJECT-DOC.md").exists())

    def test_init_can_select_zh_cn_as_ai_doc_language(self) -> None:
        tmp_path = workspace_temp_dir("init-zh-ai-language")
        self.addCleanup(shutil.rmtree, tmp_path, True)
        requirements = tmp_path / "requirements.md"
        requirements.write_text("# Requirements\n", encoding="utf-8")

        exit_code = main(
            [
                "init",
                "blank",
                "--repo",
                str(tmp_path),
                "--requirements-doc",
                str(requirements),
                "--ai-doc-language",
                "zh-CN",
            ]
        )

        self.assertEqual(exit_code, 0)
        config = json.loads((tmp_path / "codex-loop.json").read_text(encoding="utf-8"))
        self.assertEqual(config["ai_docs_language"], "zh-CN")
        self.assertIn("codex-loop-docs\\zh-CN\\AI-MASTER-PROMPT.md", config["prompt"])

    def test_init_can_write_runtime_permission_defaults(self) -> None:
        tmp_path = workspace_temp_dir("init-runtime-permissions")
        self.addCleanup(shutil.rmtree, tmp_path, True)
        requirements = tmp_path / "requirements.md"
        requirements.write_text("# Requirements\n", encoding="utf-8")

        exit_code = main(
            [
                "init",
                "blank",
                "--repo",
                str(tmp_path),
                "--requirements-doc",
                str(requirements),
                "--sandbox-mode",
                "danger-full-access",
                "--approval-policy",
                "never",
                "--no-search-enabled",
                "--skip-git-repo-check",
            ]
        )

        self.assertEqual(exit_code, 0)
        config = json.loads((tmp_path / "codex-loop.json").read_text(encoding="utf-8"))
        self.assertEqual(config["sandbox_mode"], "danger-full-access")
        self.assertEqual(config["approval_policy"], "never")
        self.assertFalse(config["search_enabled"])
        self.assertTrue(config["skip_git_repo_check"])

    def test_init_accepts_on_failure_approval_policy(self) -> None:
        tmp_path = workspace_temp_dir("init-on-failure-policy")
        self.addCleanup(shutil.rmtree, tmp_path, True)
        requirements = tmp_path / "requirements.md"
        requirements.write_text("# Requirements\n", encoding="utf-8")

        exit_code = main(
            [
                "init",
                "blank",
                "--repo",
                str(tmp_path),
                "--requirements-doc",
                str(requirements),
                "--approval-policy",
                "on-failure",
            ]
        )

        self.assertEqual(exit_code, 0)
        config = json.loads((tmp_path / "codex-loop.json").read_text(encoding="utf-8"))
        self.assertEqual(config["approval_policy"], "on-failure")

    def test_init_existing_code_requires_canonical_doc(self) -> None:
        tmp_path = workspace_temp_dir("init-existing-code-missing-canonical")
        self.addCleanup(shutil.rmtree, tmp_path, True)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("print('x')\n", encoding="utf-8")

        with self.assertRaises(FileNotFoundError):
            main(["init", "existing-code", "--repo", str(tmp_path)])


if __name__ == "__main__":
    unittest.main()
