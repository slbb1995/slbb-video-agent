from __future__ import annotations

import ast
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISPATCHER = ROOT / "bin" / "slbb-video.py"


def utf8_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DISPATCHER), *args],
        cwd=ROOT,
        env=utf8_env(),
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class RepositoryHealthTests(unittest.TestCase):
    def test_every_python_file_parses(self) -> None:
        python_files = sorted(ROOT.rglob("*.py"))
        self.assertGreaterEqual(len(python_files), 30)
        for path in python_files:
            with self.subTest(path=path.relative_to(ROOT)):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_every_skill_script_exposes_help(self) -> None:
        scripts = sorted((ROOT / "skills").glob("*/scripts/*.py"))
        self.assertGreaterEqual(len(scripts), 30)
        for path in scripts:
            with self.subTest(path=path.relative_to(ROOT)):
                result = subprocess.run(
                    [sys.executable, str(path), "--help"],
                    cwd=ROOT,
                    env=utf8_env(),
                    encoding="utf-8",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_short_drama_workflow_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="slbb-video-smoke-") as tmp:
            run_dir = Path(tmp) / "run"

            initialized = run_cli(
                "init",
                str(run_dir),
                "--title",
                "CI smoke test",
                "--mode",
                "short_drama",
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            self.assertTrue((run_dir / "workflow_state.json").is_file())

            next_step = run_cli("next", str(run_dir))
            self.assertEqual(next_step.returncode, 0, next_step.stderr)
            self.assertIn("S1", next_step.stdout)

            validated = run_cli("validate", str(run_dir))
            self.assertEqual(validated.returncode, 0, validated.stderr)
            self.assertIn("validation passed", validated.stdout)

    def test_unknown_dispatcher_command_fails_closed(self) -> None:
        result = run_cli("not-a-command")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown command", result.stdout)

    def test_video_dependency_is_exactly_pinned(self) -> None:
        requirement = (ROOT / "requirements-video.txt").read_text(encoding="utf-8").strip()
        self.assertEqual(requirement, "faster-whisper==1.2.1")

    @unittest.skipIf(os.name == "nt", "POSIX executable bits are not meaningful on Windows")
    def test_windows_wrappers_are_not_executable(self) -> None:
        wrappers = sorted((ROOT / "bin").glob("*.cmd"))
        self.assertGreater(len(wrappers), 0)
        for path in wrappers:
            with self.subTest(path=path.relative_to(ROOT)):
                mode = path.stat().st_mode
                self.assertFalse(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))

    def test_docs_do_not_dirty_windows_wrappers(self) -> None:
        docs = [
            ROOT / "README.md",
            ROOT / "START_HERE.md",
            ROOT / "QUICKSTART.md",
            ROOT / "docs" / "ONBOARDING.md",
        ]
        for path in docs:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("chmod +x bin/*", text)

    def test_windows_wrappers_enable_utf8(self) -> None:
        wrappers = sorted(ROOT.glob("bin/*.cmd"))
        wrappers.extend(sorted(ROOT.glob("skills/*/bin/*.cmd")))
        self.assertGreater(len(wrappers), 0)
        for path in wrappers:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertIn('set "PYTHONUTF8=1"', text)
                self.assertIn('set "PYTHONIOENCODING=utf-8"', text)


if __name__ == "__main__":
    unittest.main()
