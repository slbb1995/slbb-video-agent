#!/usr/bin/env python3
"""Preflight checks for local video preprocessing."""

from __future__ import annotations

import argparse
import platform
import shutil
import sys
import tempfile
from pathlib import Path

from video_env_lib import python_can_import, resolve_project_root, venv_python


def has_non_ascii(text: str) -> bool:
    return any(ord(ch) > 127 for ch in text)


def check_artifacts_write(root: Path) -> tuple[bool, str]:
    try:
        with tempfile.TemporaryDirectory(prefix=".doctor_artifacts_", dir=root) as tmp:
            probe = Path(tmp) / "artifacts" / "_audit"
            probe.mkdir(parents=True, exist_ok=True)
            (probe / "write_test.txt").write_text("ok\n", encoding="utf-8")
        return True, "can create artifacts directory"
    except Exception as exc:  # noqa: BLE001 - preflight should surface exact reason
        return False, str(exc)


def print_install_hint(system_name: str, missing: list[str]) -> None:
    if not missing:
        return
    print("\n安装建议：")
    lower = system_name.lower()
    if "ffmpeg" in missing or "ffprobe" in missing:
        if lower == "darwin":
            print("- macOS: 先让用户确认，然后运行 `brew install ffmpeg`")
        elif lower == "windows":
            print("- Windows: 先让用户确认，然后运行 `winget install Gyan.FFmpeg`")
            print("- 如果 winget 不可用：手动安装 ffmpeg，并把 ffmpeg 的 bin 目录加入 PATH")
        else:
            print("- Linux: 使用系统包管理器安装 ffmpeg，例如 `sudo apt install ffmpeg`")
    if ".venv" in missing or "faster-whisper" in missing:
        print("- Python 依赖：先让用户确认，然后运行 `./bin/slbb-video-setup --video`")
        print("- Windows 对应：`.\\bin\\slbb-video-setup.cmd --video`")
    print("\n规则：检测出缺失项后，不要静默安装；必须先询问用户是否安装。")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check video workflow prerequisites")
    parser.add_argument("--project-root", help="slbb-video-agent project root or standalone skill root")
    args = parser.parse_args()

    root = resolve_project_root(explicit_root=args.project_root)
    system_name = platform.system() or "unknown"
    required_missing: list[str] = []
    warnings: list[str] = []

    print("SLBB video environment doctor")
    print(f"Environment root: {root}")
    print(f"System: {system_name} {platform.release()}")

    python_ok = sys.version_info >= (3, 10)
    print(f"{'OK' if python_ok else 'MISSING'} Python: {sys.version.split()[0]} (need 3.10+)")
    if not python_ok:
        required_missing.append("Python 3.10+")

    for binary in ("ffmpeg", "ffprobe"):
        found = shutil.which(binary)
        print(f"{'OK' if found else 'MISSING'} {binary}: {found or 'not found in PATH'}")
        if not found:
            required_missing.append(binary)

    venv_dir = root / ".venv"
    venv_ok = venv_dir.exists()
    print(f"{'OK' if venv_ok else 'MISSING'} .venv: {venv_dir}")
    if not venv_ok:
        required_missing.append(".venv")

    fw_ok = False
    fw_detail = "skipped because .venv is missing"
    if venv_ok:
        fw_ok, fw_detail = python_can_import(venv_python(root), "faster_whisper")
    print(f"{'OK' if fw_ok else 'MISSING'} faster-whisper: {fw_detail}")
    if not fw_ok:
        required_missing.append("faster-whisper")

    artifacts_ok, artifacts_detail = check_artifacts_write(root)
    print(f"{'OK' if artifacts_ok else 'MISSING'} artifacts write: {artifacts_detail}")
    if not artifacts_ok:
        required_missing.append("artifacts write permission")

    root_text = str(root)
    if " " in root_text:
        warnings.append("当前包路径包含空格；脚本已做引号兼容，但复制命令时必须保留引号。")
    if has_non_ascii(root_text):
        warnings.append("当前包路径包含中文或非 ASCII 字符；macOS 通常可用，Windows 上建议保留引号并避免手动拆路径。")

    if warnings:
        print("\n路径提醒：")
        for warning in warnings:
            print(f"- {warning}")

    if required_missing:
        print("\n检测到缺失项：")
        for item in required_missing:
            print(f"- {item}")
        print_install_hint(system_name, required_missing)
        return 1

    print("\n环境检测通过，可以继续视频预处理。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
