#!/usr/bin/env python3
"""Validate S1 artifacts for the AI short-drama workflow."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Validators live in slbb-video-<X>/scripts/ but import shared helpers
# (BASE_NOISE_MARKERS, section_text) from slbb-video-orchestrator/scripts/.
# Adjust sys.path so the import below resolves regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slbb-video-orchestrator" / "scripts"))

from workflow_lib import BASE_NOISE_MARKERS


REQUIRED_HEADINGS = [
    "## 一句话简介",
    "## 核心人物",
    "## 核心场景",
    "## 分集列表",
    "## 下一阶段输入",
]

# S1-specific noise markers (in addition to BASE_NOISE_MARKERS):
# "## 输入与来源" is the S1-specific variant of "## 输入来源" (S2-S7 use the latter).
NOISE_MARKERS = BASE_NOISE_MARKERS + [
    "## 输入与来源",
    "## 版权与改写风险提示",
    "不能自动进入下一步",
]

REQUIRED_TIMELINE_KEYS = ["0-2s", "3-10s", "11-15s"]
REQUIRED_BEAT_KEYS = ["camera", "action", "dialogue_or_sound"]
REQUIRED_CHARACTER_KEYS = ["name", "role", "appearance", "relationship"]
VISUAL_ANCHOR_KEYS = ["face", "hair", "body", "costume", "shoes", "accessories", "temperament"]
SEGMENTATION_DECISION_MARKERS = [
    "source_type:",
    "original_episode_count:",
    "collected_source_count:",
    "material_types:",
    "coverage_level:",
    "target_segment_count:",
    "decision_basis:",
    "boundary:",
]


def fail(errors: list[str]) -> int:
    print("S1 validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    s1_dir = run_dir / "artifacts" / "S1"
    meta_dir = run_dir / "artifacts" / "_meta"
    story_extract = s1_dir / "story_extract.md"
    story_segments = s1_dir / "story_segments.json"
    segmentation_decision = meta_dir / "S1_segmentation_decision.md"

    errors: list[str] = []
    for path in [story_extract, story_segments, segmentation_decision]:
        if not path.exists():
            errors.append(f"missing required file: {path}")

    if errors:
        return fail(errors)

    story_text = story_extract.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if heading not in story_text:
            errors.append(f"story_extract.md missing heading: {heading}")
    for marker in NOISE_MARKERS:
        if marker in story_text:
            errors.append(f"story_extract.md contains process/noise marker: {marker}")

    decision_text = segmentation_decision.read_text(encoding="utf-8")
    for marker in SEGMENTATION_DECISION_MARKERS:
        if marker not in decision_text:
            errors.append(f"S1_segmentation_decision.md missing marker: {marker}")
    target_match = re.search(r"target_segment_count\s*[:：]\s*(\d+)", decision_text)
    target_segment_count = int(target_match.group(1)) if target_match else None
    if target_segment_count is None:
        errors.append("S1_segmentation_decision.md missing numeric target_segment_count")
    coverage_low = re.search(r"coverage_level\s*[:：]\s*low\b", decision_text, re.IGNORECASE)
    full_boundary = re.search(r"boundary\s*[:：].*full-series", decision_text, re.IGNORECASE)
    if coverage_low and full_boundary:
        errors.append("S1_segmentation_decision.md cannot claim full-series reconstruction when coverage_level is low")

    try:
        segment_text = story_segments.read_text(encoding="utf-8")
        for marker in NOISE_MARKERS:
            if marker in segment_text:
                errors.append(f"story_segments.json contains process/noise marker: {marker}")
        data = json.loads(segment_text)
    except json.JSONDecodeError as exc:
        errors.append(f"story_segments.json invalid JSON: {exc}")
        data = None

    if isinstance(data, dict):
        characters = data.get("characters")
        if not isinstance(characters, list):
            errors.append("story_segments.json missing array: characters")
        elif not characters:
            errors.append("story_segments.json characters must contain at least one core character before S2")
        else:
            for index, character in enumerate(characters, start=1):
                prefix = f"characters[{index}]"
                for key in REQUIRED_CHARACTER_KEYS:
                    if not str(character.get(key, "")).strip():
                        errors.append(f"{prefix} missing non-empty {key}")
                visual_anchor = character.get("visual_anchor")
                if isinstance(visual_anchor, dict):
                    missing_visual = [key for key in VISUAL_ANCHOR_KEYS if not str(visual_anchor.get(key, "")).strip()]
                    if missing_visual:
                        errors.append(f"{prefix}.visual_anchor missing non-empty fields: {', '.join(missing_visual)}")
                else:
                    errors.append(f"{prefix} missing object: visual_anchor")
        episodes = data.get("episodes")
        if not isinstance(episodes, list):
            errors.append("story_segments.json missing array: episodes")
        elif not episodes:
            errors.append("story_segments.json episodes must contain at least one episode before S1 can be marked complete")
        elif episodes:
            if target_segment_count is not None and len(episodes) != target_segment_count:
                errors.append(
                    "S1_segmentation_decision.md target_segment_count "
                    f"{target_segment_count} does not match story_segments.json episodes count {len(episodes)}"
                )
            for index, episode in enumerate(episodes, start=1):
                prefix = f"episodes[{index}]"
                for key in ["episode_id", "episode_name", "scene", "characters", "props", "timeline", "review"]:
                    if key not in episode:
                        errors.append(f"{prefix} missing key: {key}")
                timeline = episode.get("timeline", {})
                if isinstance(timeline, dict):
                    for beat_key in REQUIRED_TIMELINE_KEYS:
                        beat = timeline.get(beat_key)
                        if not isinstance(beat, dict):
                            errors.append(f"{prefix}.timeline missing beat: {beat_key}")
                            continue
                        for field in REQUIRED_BEAT_KEYS:
                            if not str(beat.get(field, "")).strip():
                                errors.append(f"{prefix}.timeline.{beat_key} missing non-empty {field}")
                else:
                    errors.append(f"{prefix}.timeline must be an object")
    elif data is not None:
        errors.append("story_segments.json top-level value must be an object")

    if errors:
        return fail(errors)

    print("S1 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
