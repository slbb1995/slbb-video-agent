#!/usr/bin/env python3
"""Create the package-local video preprocessing Python environment."""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys

from video_env_lib import requirements_file, resolve_project_root, venv_python


def run(cmd: list[str]) -> int:
    print("+ " + " ".join(cmd))
    return subprocess.run(cmd, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Install video preprocessing Python dependencies into .venv")
    parser.add_argument("--video", action="store_true", help="Install the video preprocessing dependency set")
    parser.add_argument("--project-root", help="slbb-video-agent project root or standalone skill root")
    args = parser.parse_args()

    if not args.video:
        print("ERROR: use --video to confirm installing the video preprocessing dependency set.")
        return 2
    if sys.version_info < (3, 10):
        print(f"ERROR: Python 3.10+ is required, current is {sys.version.split()[0]}")
        return 1

    root = resolve_project_root(explicit_root=args.project_root)
    requirements = requirements_file(root)
    if not requirements:
        print(f"ERROR: missing requirements-video.txt near: {root}")
        return 1

    venv_dir = root / ".venv"
    py = venv_python(root)
    if not venv_dir.exists():
        code = run([sys.executable, "-m", "venv", str(venv_dir)])
        if code != 0:
            return code

    code = run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    if code != 0:
        return code
    code = run([str(py), "-m", "pip", "install", "-r", str(requirements)])
    if code != 0:
        return code

    print("\nPython 视频依赖已安装到包内 .venv。")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        system_name = platform.system().lower()
        print("\n仍需安装系统 ffmpeg / ffprobe：")
        if system_name == "darwin":
            print("- macOS: brew install ffmpeg")
        elif system_name == "windows":
            print("- Windows: winget install Gyan.FFmpeg")
            print("- 如果 winget 不可用，手动安装 ffmpeg 并把 bin 目录加入 PATH")
        else:
            print("- Linux: 使用系统包管理器安装 ffmpeg")
    print("\n下一步：重新运行 `./bin/slbb-video-doctor`。Windows 用 `.\\bin\\slbb-video-doctor.cmd`。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
