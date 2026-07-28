#!/usr/bin/env python3
"""Cross-platform command dispatcher for the slbb video workflow package."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


COMMANDS = {
    "doctor": "doctor.py",
    "setup": "setup_video_env.py",
    "init": "init_run.py",
    "from-handoff": "from_handoff.py",
    "next": "next_step.py",
    "advance": "advance_stage.py",
    "validate": "validate_orchestrator_state.py",
    "source": "prepare_source.py",
    "ingest": "ingest_video.py",
}


def usage() -> str:
    commands = " | ".join(COMMANDS)
    return (
        "Usage:\n"
        f"  python bin/slbb-video.py <{commands}> [args...]\n\n"
        "Examples:\n"
        "  python bin/slbb-video.py doctor\n"
        "  python bin/slbb-video.py setup --video\n"
        '  python bin/slbb-video.py init ./runs/demo --title "测试短剧"\n'
        '  python bin/slbb-video.py source ./runs/demo --source-ref "/path/video.mp4"\n'
        '  python bin/slbb-video.py ingest --run-dir ./runs/demo --video "/path/video.mp4"\n'
        "  python bin/slbb-video.py validate ./runs/demo\n"
    )


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print(usage())
        return 0 if len(sys.argv) >= 2 else 2

    command = sys.argv[1]
    if command not in COMMANDS:
        print(f"Unknown command: {command}\n")
        print(usage())
        return 2

    bin_dir = Path(__file__).resolve().parent
    package_root = bin_dir.parent
    skills_root = package_root / "skills"
    script = skills_root / "slbb-video-orchestrator" / "scripts" / COMMANDS[command]
    if not script.exists():
        print(f"ERROR: command script not found: {script}")
        return 1

    env = os.environ.copy()
    env["CODEX_SKILLS_ROOT"] = str(skills_root)
    # Windows runners and older Windows consoles may default to cp1252, which
    # cannot represent the Chinese workflow output. Child commands are the
    # actual user-facing processes, so force UTF-8 at interpreter startup.
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run([sys.executable, str(script), *sys.argv[2:]], env=env, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
