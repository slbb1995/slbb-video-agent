#!/usr/bin/env python3
"""Append one issue to S5 qc_verdict.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


VALID_CATEGORIES = [
    "character_consistency",
    "deformation",
    "action_correctness",
    "expression_emotion",
    "lighting_color",
    "camera_stability",
    "scene_prop_consistency",
    "dialogue_lipsync_story",
    "subtitle_text_glitch",
    "platform_artifact",
    "compliance_safety",
]

VALID_SEVERITIES = ["critical", "high", "medium", "low"]
VALID_SOURCE_STEPS = ["S1", "S1_long_replica", "S2", "S3", "S4", "S6", "platform", "unknown"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    parser.add_argument("--issue-id", default="")
    parser.add_argument("--category", required=True, choices=VALID_CATEGORIES)
    parser.add_argument("--severity", required=True, choices=VALID_SEVERITIES)
    parser.add_argument("--timestamp", default="")
    parser.add_argument("--observation", required=True)
    parser.add_argument("--evidence-ref", default="")
    parser.add_argument("--likely-source-step", required=True, choices=VALID_SOURCE_STEPS)
    parser.add_argument("--recommendation", required=True)
    args = parser.parse_args()

    verdict_path = Path(args.run_dir).expanduser().resolve() / "artifacts" / "S5" / "qc_verdict.json"
    verdict_path.parent.mkdir(parents=True, exist_ok=True)
    if verdict_path.exists():
        data = json.loads(verdict_path.read_text(encoding="utf-8"))
    else:
        data = {"issues": []}
    issues = data.setdefault("issues", [])
    issue_id = args.issue_id or f"qc-{len(issues) + 1:03d}"
    issues.append(
        {
            "issue_id": issue_id,
            "category": args.category,
            "severity": args.severity,
            "timestamp": args.timestamp,
            "observation": args.observation,
            "evidence_ref": args.evidence_ref,
            "likely_source_step": args.likely_source_step,
            "recommendation": args.recommendation,
        }
    )
    verdict_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Appended QC issue: {issue_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
