#!/usr/bin/env python3
"""Validate S1 artifacts for the AI long-drama workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SOURCE_HEADINGS = [
    "## 1. 视频基础信息",
    "## 2. 固定角色形象描述",
    "## 3. 视频片段拆分总览",
    "## 4. 分片段详细画面描述",
    "## 5. 台词 / 字幕 / 旁白汇总",
    "## 6. 原视频剧情总结",
]

SECOND_CREATION_HEADINGS = [
    "## 1. 本次二创方向",
    "## 2. 二创后角色形象描述",
    "## 3. 二创后片段拆分总览",
    "## 4. 二创后分片段详细画面描述",
]

NOISE_MARKERS = [
    "内容中台",
    "选题池",
    "爆款选题",
    "趋势评分",
    "视频生成提示词",
    "分镜提示词",
    "成片脚本",
    "封面文案",
    "发布方案",
    "Workflow",
    "workflow",
    "V2 原则",
    "## 人工确认项",
]

UNFINISHED_MARKERS = ["TODO", "待填写", "待补充"]
REQUIRED_CHARACTER_KEYS = ["name", "role", "appearance", "relationship"]
VISUAL_ANCHOR_KEYS = ["face", "hair", "body", "costume", "shoes", "accessories", "temperament"]
REQUIRED_EPISODE_KEYS = [
    "episode_id",
    "episode_name",
    "source_time_range",
    "duration_seconds",
    "scene",
    "characters",
    "props",
    "replica_description",
    "second_creation_description",
    "timeline",
    "review",
]
REQUIRED_BEAT_KEYS = ["camera", "action", "dialogue_or_sound"]
SOURCE_BRIEF_MAX_CHARS = 3500
SOURCE_BRIEF_HEADINGS = [
    "## 对标素材定位",
    "## 一句话剧情/核心看点",
    "## 角色与视觉锚点",
    "## 关键时间点",
    "## 台词/字幕要点",
    "## 二创方向",
]


def section_text(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    rest = text[start + len(heading):]
    next_heading = rest.find("\n## ")
    if next_heading >= 0:
        rest = rest[:next_heading]
    return rest.strip()


def fail(errors: list[str]) -> int:
    print("Long-drama S1 validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


def check_markdown(path: Path, headings: list[str], label: str, errors: list[str]) -> str:
    text = path.read_text(encoding="utf-8")
    for heading in headings:
        if heading not in text:
            errors.append(f"{label} missing heading: {heading}")
        elif not section_text(text, heading):
            errors.append(f"{label} empty section: {heading}")
    for marker in NOISE_MARKERS:
        if marker in text:
            errors.append(f"{label} contains forbidden marker: {marker}")
    for marker in UNFINISHED_MARKERS:
        if marker in text:
            errors.append(f"{label} contains unfinished marker: {marker}")
    return text


def check_source_brief(run_dir: Path, errors: list[str]) -> None:
    brief = run_dir / "artifacts" / "_source" / "source_brief.md"
    manifest = run_dir / "artifacts" / "_source" / "source_manifest.json"
    if not brief.exists():
        errors.append("missing source brief: artifacts/_source/source_brief.md (run slbb-video-source first)")
        return
    if not manifest.exists():
        errors.append("missing source manifest: artifacts/_source/source_manifest.json (run slbb-video-source first)")
        return

    try:
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"source_manifest.json invalid JSON: {exc}")
        manifest_data = {}
    source_kind = manifest_data.get("source_kind")
    evidence_quality = manifest_data.get("evidence_quality")
    if source_kind == "platform_link":
        errors.append(
            "source_manifest.json is platform_link; download/record the video as a local file before long-drama S1"
        )
    if source_kind in {"local_video", "direct_video_url"}:
        for rel in [
            "artifacts/_audit/video_ingest/ingest_report.md",
            "artifacts/_audit/video_ingest/shot_index.json",
            "artifacts/_audit/video_ingest/contact_sheet.jpg",
        ]:
            if not (run_dir / rel).exists():
                errors.append(f"missing video ingest artifact for {source_kind}: {rel}")
    if source_kind == "partial_material" and evidence_quality != "partial":
        errors.append("partial_material source must set evidence_quality=partial")

    text = brief.read_text(encoding="utf-8")
    if len(text) > SOURCE_BRIEF_MAX_CHARS:
        errors.append(
            f"source_brief.md is too long ({len(text)} chars); keep it under {SOURCE_BRIEF_MAX_CHARS} chars"
        )
    for heading in SOURCE_BRIEF_HEADINGS:
        body = section_text(text, heading)
        if not body:
            errors.append(f"source_brief.md empty section: {heading}")
    for marker in UNFINISHED_MARKERS:
        if marker in text:
            errors.append(f"source_brief.md contains unfinished marker: {marker}")

    key_time_section = section_text(text, "## 关键时间点")
    key_time_bullets = [line for line in key_time_section.splitlines() if line.strip().startswith("-")]
    if len(key_time_bullets) > 12:
        errors.append("source_brief.md should keep ## 关键时间点 to 12 bullets or fewer")

    dialogue_section = section_text(text, "## 台词/字幕要点")
    dialogue_bullets = [line for line in dialogue_section.splitlines() if line.strip().startswith("-")]
    if len(dialogue_bullets) > 10:
        errors.append("source_brief.md should keep ## 台词/字幕要点 to 10 bullets or fewer")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    s1_dir = run_dir / "artifacts" / "S1"
    meta_dir = run_dir / "artifacts" / "_meta"
    source = s1_dir / "source_replica_description.md"
    second = s1_dir / "second_creation_description.md"
    segments = s1_dir / "story_segments.json"
    notes = meta_dir / "S1_replica_notes.md"

    errors: list[str] = []
    check_source_brief(run_dir, errors)
    for path in [source, second, segments, notes]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        return fail(errors)

    check_markdown(source, SOURCE_HEADINGS, "source_replica_description.md", errors)
    check_markdown(second, SECOND_CREATION_HEADINGS, "second_creation_description.md", errors)

    try:
        segment_text = segments.read_text(encoding="utf-8")
        for marker in NOISE_MARKERS:
            if marker in segment_text:
                errors.append(f"story_segments.json contains forbidden marker: {marker}")
        for marker in UNFINISHED_MARKERS:
            if marker in segment_text:
                errors.append(f"story_segments.json contains unfinished marker: {marker}")
        data = json.loads(segment_text)
    except json.JSONDecodeError as exc:
        errors.append(f"story_segments.json invalid JSON: {exc}")
        data = None

    if isinstance(data, dict):
        characters = data.get("characters")
        character_names: set[str] = set()
        if not isinstance(characters, list):
            errors.append("story_segments.json missing array: characters")
        elif not characters:
            errors.append("story_segments.json characters must contain at least one core character")
        else:
            for index, character in enumerate(characters, start=1):
                prefix = f"characters[{index}]"
                name = str(character.get("name", "")).strip()
                if name:
                    if name in character_names:
                        errors.append(f"{prefix} duplicate character name: {name}")
                    character_names.add(name)
                for key in REQUIRED_CHARACTER_KEYS:
                    if not str(character.get(key, "")).strip():
                        errors.append(f"{prefix} missing non-empty {key}")
                visual_anchor = character.get("visual_anchor")
                if not isinstance(visual_anchor, dict):
                    errors.append(f"{prefix} missing object: visual_anchor")
                else:
                    missing_visual = [key for key in VISUAL_ANCHOR_KEYS if not str(visual_anchor.get(key, "")).strip()]
                    if missing_visual:
                        errors.append(f"{prefix}.visual_anchor missing non-empty fields: {', '.join(missing_visual)}")

        episodes = data.get("episodes")
        if not isinstance(episodes, list):
            errors.append("story_segments.json missing array: episodes")
        elif not episodes:
            errors.append("story_segments.json episodes must contain at least one segment")
        else:
            for index, episode in enumerate(episodes, start=1):
                prefix = f"episodes[{index}]"
                for key in REQUIRED_EPISODE_KEYS:
                    if key not in episode:
                        errors.append(f"{prefix} missing key: {key}")
                duration = episode.get("duration_seconds")
                if isinstance(duration, (int, float)):
                    if duration < 3 or duration > 15:
                        errors.append(f"{prefix}.duration_seconds must be between 3 and 15")
                else:
                    errors.append(f"{prefix}.duration_seconds must be numeric")
                for text_key in ["replica_description", "second_creation_description"]:
                    if not str(episode.get(text_key, "")).strip():
                        errors.append(f"{prefix} missing non-empty {text_key}")
                episode_characters = episode.get("characters")
                if not isinstance(episode_characters, list) or not episode_characters:
                    errors.append(f"{prefix}.characters must be a non-empty array")
                elif characters:
                    for character_name in episode_characters:
                        if not isinstance(character_name, str) or not character_name.strip():
                            errors.append(f"{prefix}.characters contains a non-string or empty character name")
                            continue
                        if character_name.strip() not in character_names:
                            errors.append(
                                f"{prefix}.characters references unknown character: {character_name.strip()}"
                            )
                timeline = episode.get("timeline")
                if not isinstance(timeline, dict) or not timeline:
                    errors.append(f"{prefix}.timeline must be a non-empty object")
                elif isinstance(timeline, dict):
                    for beat_key, beat in timeline.items():
                        if not isinstance(beat, dict):
                            errors.append(f"{prefix}.timeline.{beat_key} must be an object")
                            continue
                        for field in REQUIRED_BEAT_KEYS:
                            if not str(beat.get(field, "")).strip():
                                errors.append(f"{prefix}.timeline.{beat_key} missing non-empty {field}")
    elif data is not None:
        errors.append("story_segments.json top-level value must be an object")

    if errors:
        return fail(errors)

    print("Long-drama S1 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
