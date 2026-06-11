#!/usr/bin/env python3
"""Environment discovery helpers for slbb video preprocessing scripts."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path


def _unique(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        result.append(resolved)
    return result


def _ancestors(path: Path) -> list[Path]:
    path = path.expanduser().resolve()
    if path.is_file():
        path = path.parent
    return [path, *path.parents]


def script_skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_project_root(path: Path) -> bool:
    return (
        (path / "requirements-video.txt").exists()
        or (path / "bin" / "slbb-video.py").exists()
        or (path / "skills" / "slbb-video-orchestrator" / "SKILL.md").exists()
        or ((path / "SKILL.md").exists() and (path / "scripts" / "ingest_video.py").exists())
    )


def candidate_roots(run_dir: Path | None = None, explicit_root: str | None = None) -> list[Path]:
    paths: list[Path] = []
    env_root = os.environ.get("SLBB_VIDEO_AGENT_ROOT") or os.environ.get("SLBB_VIDEO_PROJECT_ROOT")
    if env_root:
        paths.append(Path(env_root))
    if explicit_root:
        paths.append(Path(explicit_root))
    paths.extend(_ancestors(Path.cwd()))
    if run_dir:
        paths.extend(_ancestors(run_dir))
    paths.extend(_ancestors(Path(__file__)))
    paths.append(script_skill_root())
    return _unique(paths)


def resolve_project_root(run_dir: Path | None = None, explicit_root: str | None = None) -> Path:
    for root in candidate_roots(run_dir=run_dir, explicit_root=explicit_root):
        if is_project_root(root):
            return root
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    return Path.cwd().resolve()


def venv_python(root: Path) -> Path:
    if platform.system().lower().startswith("win"):
        return root / ".venv" / "Scripts" / "python.exe"
    return root / ".venv" / "bin" / "python"


def python_can_import(python_path: Path, module: str) -> tuple[bool, str]:
    if not python_path.exists():
        return False, f"python not found: {python_path}"
    result = subprocess.run(
        [str(python_path), "-c", f"import {module}; print('ok')"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    if result.returncode == 0:
        return True, f"{module} import ok"
    detail = (result.stderr or result.stdout).strip().splitlines()
    return False, detail[-1] if detail else f"{module} import failed"


def resolve_python_with_module(
    module: str,
    run_dir: Path | None = None,
    explicit_root: str | None = None,
    explicit_python: str | None = None,
) -> tuple[Path | None, list[str]]:
    candidates: list[Path] = []
    if explicit_python:
        candidates.append(Path(explicit_python))
    env_python = os.environ.get("SLBB_VIDEO_PYTHON") or os.environ.get("SLBB_VIDEO_VENV_PYTHON")
    if env_python:
        candidates.append(Path(env_python))
    for root in candidate_roots(run_dir=run_dir, explicit_root=explicit_root):
        candidates.append(venv_python(root))
    candidates.append(Path(sys.executable))

    notes: list[str] = []
    for python_path in _unique(candidates):
        ok, detail = python_can_import(python_path, module)
        notes.append(f"{python_path}: {detail}")
        if ok:
            return python_path, notes
    return None, notes


def requirements_file(root: Path) -> Path | None:
    candidates = [
        root / "requirements-video.txt",
        script_skill_root() / "requirements-video.txt",
        script_skill_root().parent.parent / "requirements-video.txt",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None
