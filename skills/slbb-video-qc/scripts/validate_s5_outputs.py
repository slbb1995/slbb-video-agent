#!/usr/bin/env python3
"""Validate S5 QC artifacts for the AI short-drama workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Validators live in slbb-video-<X>/scripts/ but import shared helpers
# (BASE_NOISE_MARKERS, section_text) from slbb-video-orchestrator/scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slbb-video-orchestrator" / "scripts"))

from workflow_lib import BASE_NOISE_MARKERS, section_text


REPORT_HEADINGS = [
    "## 质检结论",
    "## 问题清单",
    "## 问题归因",
    "## S6 可修性判定",
]

REWORK_HEADINGS = [
    "## 总结",
    "## 按问题返工",
    "## 建议回到哪个环节",
    "## 进入下一步条件",
]

VALID_METHODS = {"human", "frames", "gemini", "vision_model", "notes_only"}
VALID_CONFIDENCE = {"low", "medium", "high"}
VALID_VERDICTS = {"pass", "needs_rework", "reject", "blocked_no_video"}
VALID_NEXT_STEPS = {"S6", "S2", "S3", "S4", "stop"}
VALID_SEVERITIES = {"critical", "high", "medium", "low"}
VALID_SOURCE_STEPS = {"S1", "S2", "S3", "S4", "S6", "platform", "unknown"}
REQUIRED_SCORE_KEYS = [
    "character_consistency",
    "deformation",
    "action_correctness",
    "lighting_color",
    "camera_stability",
    "story_fidelity",
]
NOISE_MARKERS = BASE_NOISE_MARKERS + [
    "## 审查方法",
    "不能自动进入下一步",
]


def fail(errors: list[str]) -> int:
    print("S5 validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    s5_dir = Path(args.run_dir).expanduser().resolve() / "artifacts" / "S5"
    report = s5_dir / "qc_report.md"
    verdict = s5_dir / "qc_verdict.json"
    rework = s5_dir / "rework_suggestions.md"
    errors: list[str] = []

    for path in [report, verdict, rework]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        return fail(errors)

    report_text = report.read_text(encoding="utf-8")
    for heading in REPORT_HEADINGS:
        if heading not in report_text:
            errors.append(f"qc_report.md missing heading: {heading}")
        elif not section_text(report_text, heading):
            errors.append(f"qc_report.md empty section: {heading}")
    for marker in NOISE_MARKERS:
        if marker in report_text:
            errors.append(f"qc_report.md contains process/noise marker: {marker}")

    rework_text = rework.read_text(encoding="utf-8")
    for heading in REWORK_HEADINGS:
        if heading not in rework_text:
            errors.append(f"rework_suggestions.md missing heading: {heading}")
        elif not section_text(rework_text, heading):
            errors.append(f"rework_suggestions.md empty section: {heading}")
    for marker in NOISE_MARKERS:
        if marker in rework_text:
            errors.append(f"rework_suggestions.md contains process/noise marker: {marker}")

    try:
        data = json.loads(verdict.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"qc_verdict.json invalid JSON: {exc}")
        data = {}

    source = data.get("source")
    if not isinstance(source, dict):
        errors.append("qc_verdict.json missing object: source")
        source = {}
    else:
        if not str(source.get("video_ref", "")).strip() and data.get("verdict") != "blocked_no_video":
            errors.append("source.video_ref is required unless verdict is blocked_no_video")
        method = source.get("review_method", "")
        if method not in VALID_METHODS:
            errors.append(f"source.review_method must be one of: {', '.join(sorted(VALID_METHODS))}")
        confidence = source.get("confidence", "")
        if confidence not in VALID_CONFIDENCE:
            errors.append(f"source.confidence must be one of: {', '.join(sorted(VALID_CONFIDENCE))}")

    verdict_value = data.get("verdict", "")
    if verdict_value not in VALID_VERDICTS:
        errors.append(f"verdict must be one of: {', '.join(sorted(VALID_VERDICTS))}")
    next_step = data.get("next_step", "")
    if next_step not in VALID_NEXT_STEPS:
        errors.append(f"next_step must be one of: {', '.join(sorted(VALID_NEXT_STEPS))}")

    scores = data.get("scores")
    if not isinstance(scores, dict):
        errors.append("qc_verdict.json missing object: scores")
    else:
        for key in REQUIRED_SCORE_KEYS:
            value = scores.get(key)
            if not isinstance(value, int) or value < 0 or value > 5:
                errors.append(f"scores.{key} must be integer 0-5")

    issues = data.get("issues")
    if not isinstance(issues, list):
        errors.append("qc_verdict.json missing array: issues")
        issues = []
    if verdict_value in {"needs_rework", "reject"} and not issues:
        errors.append(f"verdict {verdict_value} requires at least one issue")

    for index, issue in enumerate(issues, start=1):
        prefix = f"issues[{index}]"
        for key in ["issue_id", "category", "severity", "observation", "likely_source_step", "recommendation"]:
            if not str(issue.get(key, "")).strip():
                errors.append(f"{prefix} missing required value: {key}")
        if issue.get("severity") not in VALID_SEVERITIES:
            errors.append(f"{prefix}.severity invalid")
        if issue.get("likely_source_step") not in VALID_SOURCE_STEPS:
            errors.append(f"{prefix}.likely_source_step invalid")

    if errors:
        return fail(errors)

    print("S5 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
