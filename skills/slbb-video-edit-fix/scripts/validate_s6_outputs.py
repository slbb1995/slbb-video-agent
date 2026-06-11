#!/usr/bin/env python3
"""Validate S6 edit-fix artifacts for the AI short-drama workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Validators live in slbb-video-<X>/scripts/ but import shared helpers
# (BASE_NOISE_MARKERS, section_text) from slbb-video-orchestrator/scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slbb-video-orchestrator" / "scripts"))

from workflow_lib import BASE_NOISE_MARKERS, section_text


PLAN_HEADINGS = [
    "## 修正结论",
    "## 字幕遮挡方案",
    "## 其他剪辑修正",
    "## 不适合剪辑修正的问题",
]

CHECKLIST_HEADINGS = [
    "## 基础设置",
    "## 修正项清单",
    "## 人工交付检查",
    "## 进入下一步条件",
]

SUBTITLE_SIGNALS = ["白底黑字", "黑体", "可商用", "遮住"]
SUBTITLE_MARKERS = ["subtitle_cover", "caption_replace", "乱码字幕", "错误字幕", "错误文字", "水印样文字"]
NO_SUBTITLE_MARKERS = ["不需要字幕遮挡", "无需字幕遮挡", "无字幕遮挡问题"]
NOISE_MARKERS = BASE_NOISE_MARKERS + [
    "## S6 能力边界",
    "不能自动进入下一步",
    "自动剪辑产物路径",
    "draft_auto_edit",
    "已剪辑完成",
    "已配音完成",
    "我已完成剪辑",
    "我已完成配音",
]


def fail(errors: list[str]) -> int:
    print("S6 validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    s6_dir = Path(args.run_dir).expanduser().resolve() / "artifacts" / "S6"
    plan = s6_dir / "edit_fix_plan.md"
    checklist = s6_dir / "edit_checklist.md"
    errors: list[str] = []

    for path in [plan, checklist]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        return fail(errors)

    plan_text = plan.read_text(encoding="utf-8")
    checklist_text = checklist.read_text(encoding="utf-8")
    combined = plan_text + "\n" + checklist_text

    for heading in PLAN_HEADINGS:
        if heading not in plan_text:
            errors.append(f"edit_fix_plan.md missing heading: {heading}")
        elif not section_text(plan_text, heading):
            errors.append(f"edit_fix_plan.md empty section: {heading}")
    for marker in NOISE_MARKERS:
        if marker in plan_text:
            errors.append(f"edit_fix_plan.md contains process/noise marker: {marker}")

    for heading in CHECKLIST_HEADINGS:
        if heading not in checklist_text:
            errors.append(f"edit_checklist.md missing heading: {heading}")
        elif not section_text(checklist_text, heading):
            errors.append(f"edit_checklist.md empty section: {heading}")
    for marker in NOISE_MARKERS:
        if marker in checklist_text:
            errors.append(f"edit_checklist.md contains process/noise marker: {marker}")

    subtitle_section = section_text(plan_text, "## 字幕遮挡方案")
    subtitle_fix_present = any(marker in combined for marker in SUBTITLE_MARKERS)
    no_subtitle_needed = any(marker in subtitle_section for marker in NO_SUBTITLE_MARKERS)
    if subtitle_fix_present and not no_subtitle_needed:
        for signal in SUBTITLE_SIGNALS:
            if signal not in combined:
                errors.append(f"S6 subtitle fix missing quality signal: {signal}")
    elif not subtitle_fix_present and not no_subtitle_needed:
        errors.append("S6 subtitle section must either define subtitle cover details or explicitly say 不需要字幕遮挡")

    if "fix-001" not in combined and "rework_only" not in combined:
        errors.append("S6 artifacts must include at least one fix item such as fix-001, or a rework_only item")

    if "audio_note" in combined and ("配音完成" in combined or "已生成配音" in combined or "已替换音频" in combined):
        errors.append("S6 audio_note must describe human audio instructions, not claim generated/replaced audio")

    if "TODO" in combined or "待填写" in combined or "待补充" in combined:
        errors.append("S6 artifacts contain unfinished placeholder")

    if errors:
        return fail(errors)

    print("S6 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
