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
    "## 导出检查",
    "## 进入下一步条件",
]

REQUIRED_SIGNALS = ["白底黑字", "黑体", "可商用", "遮住"]
NOISE_MARKERS = BASE_NOISE_MARKERS + [
    "## S6 能力边界",
    "不能自动进入下一步",
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

    for signal in REQUIRED_SIGNALS:
        if signal not in combined:
            errors.append(f"S6 artifacts missing quality signal: {signal}")

    if "fix-001" not in combined and "rework_only" not in combined:
        errors.append("S6 artifacts must include at least one fix item such as fix-001, or a rework_only item")

    if "TODO" in combined or "待填写" in combined or "待补充" in combined:
        errors.append("S6 artifacts contain unfinished placeholder")

    if errors:
        return fail(errors)

    print("S6 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
