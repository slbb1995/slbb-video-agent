#!/usr/bin/env python3
"""Validate S3 motion prompt artifacts for the AI short-drama workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Validators live in slbb-video-<X>/scripts/ but import shared helpers
# (BASE_NOISE_MARKERS, section_text) from slbb-video-orchestrator/scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slbb-video-orchestrator" / "scripts"))

from workflow_lib import BASE_NOISE_MARKERS, section_text


PACK_HEADINGS = [
    "## 角色锁定",
    "## 场景锁定",
    "## 分镜提示词表",
]

COPY_HEADINGS = [
    "## 即梦复制版",
    "## 可灵复制版",
]

TABLE_HEADER = "| 时间 | 镜头 | 景别 | 运镜 | 画面内容 | 动作 | 微表情 | 台词口型 | 声音 | 时长 | 本镜头作用 | 平台优化标签 |"

REQUIRED_SIGNALS = [
    "角色锁定",
    "场景锁定",
    "台词：",
    "环境：",
    "SFX：",
    "平台优化标签",
    "9:16",
    "即梦",
]

UNFINISHED_MARKERS = ["TODO", "待填写", "待补充"]
NOISE_MARKERS = BASE_NOISE_MARKERS + [
    "## 使用说明",
    "## 合规与改写备注",
    "## 时长判断",
    "## 关键道具与文字风险",
]


def fail(errors: list[str]) -> int:
    print("S3 validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    s3_dir = run_dir / "artifacts" / "S3"
    pack = s3_dir / "motion_prompt_pack.md"
    copy_ready = s3_dir / "platform_copy_ready_prompts.md"
    errors: list[str] = []

    for path in [pack, copy_ready]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        return fail(errors)

    pack_text = pack.read_text(encoding="utf-8")
    copy_text = copy_ready.read_text(encoding="utf-8")
    combined = pack_text + "\n" + copy_text

    for heading in PACK_HEADINGS:
        if heading not in pack_text:
            errors.append(f"motion_prompt_pack.md missing heading: {heading}")
        elif not section_text(pack_text, heading):
            errors.append(f"motion_prompt_pack.md empty section: {heading}")

    for heading in COPY_HEADINGS:
        if heading not in copy_text:
            errors.append(f"platform_copy_ready_prompts.md missing heading: {heading}")
        elif not section_text(copy_text, heading):
            errors.append(f"platform_copy_ready_prompts.md empty section: {heading}")

    if TABLE_HEADER not in pack_text:
        errors.append("motion_prompt_pack.md missing required shot table header")

    # At least one real shot row should follow the header and separator.
    shot_rows = []
    for line in pack_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if stripped == TABLE_HEADER:
            continue
        if set(stripped.replace("|", "").replace(" ", "")) <= {"-"}:
            continue
        shot_rows.append(stripped)
    if not shot_rows:
        errors.append("motion_prompt_pack.md must contain at least one shot row")

    for signal in REQUIRED_SIGNALS:
        if signal not in combined:
            errors.append(f"S3 artifacts missing quality signal: {signal}")

    for marker in UNFINISHED_MARKERS:
        if marker in combined:
            errors.append(f"S3 artifacts contain unfinished marker: {marker}")

    for marker in NOISE_MARKERS:
        if marker in combined:
            errors.append(f"S3 artifacts contain process/noise marker: {marker}")

    if errors:
        return fail(errors)

    print("S3 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
