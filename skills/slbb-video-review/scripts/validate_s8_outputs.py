#!/usr/bin/env python3
"""Validate S8 review artifacts for the AI short-drama workflow."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Validators live in slbb-video-<X>/scripts/ but import shared helpers
# (BASE_NOISE_MARKERS, section_text) from slbb-video-orchestrator/scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slbb-video-orchestrator" / "scripts"))

from workflow_lib import section_text


REVIEW_HEADINGS = [
    "## 输入来源",
    "## 发布数据",
    "## 平台表现对比",
    "## 评论与用户反馈",
    "## 问题归因",
    "## 上游反推",
    "## 结论",
]

PLAN_HEADINGS = [
    "## 下一轮选题建议",
    "## 剧情调整",
    "## 图片提示词调整",
    "## 视频提示词调整",
    "## 生成与质检调整",
    "## 剪辑与分发调整",
    "## 人工确认项",
]

METRIC_SIGNALS = ["播放", "点赞", "评论", "转发", "完播", "留存"]
UPSTREAM_SIGNALS = ["选题", "剧情", "图片提示词", "视频提示词", "生成", "质检", "剪辑", "发布"]
PLAN_SIGNALS = ["问题", "证据", "改动", "验证方式"]
UNFINISHED_MARKERS = ["TODO", "待填写", "待补充"]


def fail(errors: list[str]) -> int:
    print("S8 validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


def has_numeric_metric(text: str) -> bool:
    metric_section = section_text(text, "## 发布数据")
    return bool(re.search(r"\d", metric_section))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    s8_dir = Path(args.run_dir).expanduser().resolve() / "artifacts" / "S8"
    review = s8_dir / "review_report.md"
    plan = s8_dir / "next_iteration_plan.md"
    errors: list[str] = []

    for path in [review, plan]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        return fail(errors)

    review_text = review.read_text(encoding="utf-8")
    plan_text = plan.read_text(encoding="utf-8")
    combined = review_text + "\n" + plan_text

    if "# S8 复盘报告" not in review_text:
        errors.append("review_report.md missing title: # S8 复盘报告")
    if "# S8 下一轮迭代计划" not in plan_text:
        errors.append("next_iteration_plan.md missing title: # S8 下一轮迭代计划")

    for heading in REVIEW_HEADINGS:
        if heading not in review_text:
            errors.append(f"review_report.md missing heading: {heading}")
        elif not section_text(review_text, heading):
            errors.append(f"review_report.md empty section: {heading}")

    for heading in PLAN_HEADINGS:
        if heading not in plan_text:
            errors.append(f"next_iteration_plan.md missing heading: {heading}")
        elif not section_text(plan_text, heading):
            errors.append(f"next_iteration_plan.md empty section: {heading}")

    for signal in METRIC_SIGNALS:
        if signal not in review_text:
            errors.append(f"review_report.md missing metric signal: {signal}")
    if not has_numeric_metric(review_text):
        errors.append("review_report.md must include at least one numeric platform metric")

    upstream = section_text(review_text, "## 上游反推")
    for signal in UPSTREAM_SIGNALS:
        if signal not in upstream:
            errors.append(f"review_report.md upstream attribution missing: {signal}")

    for signal in PLAN_SIGNALS:
        if signal not in plan_text:
            errors.append(f"next_iteration_plan.md missing action-planning signal: {signal}")

    for marker in UNFINISHED_MARKERS:
        if marker in combined:
            errors.append(f"S8 artifacts contain unfinished marker: {marker}")

    if errors:
        return fail(errors)

    print("S8 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
