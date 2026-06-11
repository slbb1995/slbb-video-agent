#!/usr/bin/env python3
"""Validate S7 distribution-pack artifacts for the AI short-drama workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Validators live in slbb-video-<X>/scripts/ but import shared helpers
# (BASE_NOISE_MARKERS, section_text) from slbb-video-orchestrator/scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slbb-video-orchestrator" / "scripts"))

from workflow_lib import BASE_NOISE_MARKERS, section_text


DISTRIBUTION_HEADINGS = [
    "## 成片信息",
    "## 标题候选",
    "## 简介与看点",
    "## 封面建议",
    "## 发布时间建议",
]

PLATFORM_HEADINGS = ["## 抖音", "## 视频号", "## 小红书"]

CHECKLIST_HEADINGS = [
    "## 素材检查",
    "## 文案检查",
    "## 账号与平台检查",
    "## 手动发布状态",
    "## 进入下一步条件",
]

REQUIRED_SIGNALS = ["未发布", "不自动发布", "手动发布", "标题", "封面", "抖音", "视频号", "小红书"]
UNFINISHED_MARKERS = ["TODO", "待填写", "待补充"]
FALSE_COMPLETION_MARKERS = ["发布完成", "已自动发布", "已定时发布", "已上传平台"]
NOISE_MARKERS = BASE_NOISE_MARKERS + [
    "## 风险与人工确认",
    "人工确认：",
    "人工确认后",
]


def count_title_candidates(text: str) -> int:
    section = section_text(text, "## 标题候选")
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    candidate_lines = [line for line in lines if line.startswith(("-", "*")) or line[:2].rstrip(".、").isdigit()]
    return len(candidate_lines)


def fail(errors: list[str]) -> int:
    print("S7 validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    s7_dir = Path(args.run_dir).expanduser().resolve() / "artifacts" / "S7"
    distribution = s7_dir / "distribution_pack.md"
    platform_copy = s7_dir / "platform_copy.md"
    checklist = s7_dir / "publish_checklist.md"
    errors: list[str] = []

    for path in [distribution, platform_copy, checklist]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        return fail(errors)

    distribution_text = distribution.read_text(encoding="utf-8")
    platform_text = platform_copy.read_text(encoding="utf-8")
    checklist_text = checklist.read_text(encoding="utf-8")
    combined = "\n".join([distribution_text, platform_text, checklist_text])

    if "# S7 分发包" not in distribution_text:
        errors.append("distribution_pack.md missing title: # S7 分发包")
    if "# S7 平台文案" not in platform_text:
        errors.append("platform_copy.md missing title: # S7 平台文案")
    if "# S7 发布检查清单" not in checklist_text:
        errors.append("publish_checklist.md missing title: # S7 发布检查清单")

    for heading in DISTRIBUTION_HEADINGS:
        if heading not in distribution_text:
            errors.append(f"distribution_pack.md missing heading: {heading}")
        elif not section_text(distribution_text, heading):
            errors.append(f"distribution_pack.md empty section: {heading}")

    for heading in PLATFORM_HEADINGS:
        if heading not in platform_text:
            errors.append(f"platform_copy.md missing heading: {heading}")
            continue
        section = section_text(platform_text, heading)
        if not section:
            errors.append(f"platform_copy.md empty section: {heading}")
            continue
        for field in ["标题", "封面"]:
            if field not in section:
                errors.append(f"platform_copy.md {heading} missing field: {field}")
        if "正文" not in section and "caption" not in section.lower():
            errors.append(f"platform_copy.md {heading} missing body/caption")
        if "话题" not in section and "标签" not in section:
            errors.append(f"platform_copy.md {heading} missing topics/tags")

    for heading in CHECKLIST_HEADINGS:
        if heading not in checklist_text:
            errors.append(f"publish_checklist.md missing heading: {heading}")
        elif not section_text(checklist_text, heading):
            errors.append(f"publish_checklist.md empty section: {heading}")

    for signal in REQUIRED_SIGNALS:
        if signal not in combined:
            errors.append(f"S7 artifacts missing distribution signal: {signal}")

    if count_title_candidates(distribution_text) < 5:
        errors.append("distribution_pack.md must include at least 5 title candidates")

    for marker in UNFINISHED_MARKERS:
        if marker in combined:
            errors.append(f"S7 artifacts contain unfinished marker: {marker}")

    for marker in FALSE_COMPLETION_MARKERS:
        if marker in combined:
            errors.append(f"S7 artifacts falsely claim publishing completion: {marker}")

    for marker in NOISE_MARKERS:
        if marker in combined:
            errors.append(f"S7 artifacts contain process/noise marker: {marker}")

    if errors:
        return fail(errors)

    print("S7 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
