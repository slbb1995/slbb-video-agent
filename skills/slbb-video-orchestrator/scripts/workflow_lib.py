#!/usr/bin/env python3
"""Shared workflow definitions for the slbb video orchestrator."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_VALUES = {"pending", "in_progress", "ready_for_human", "completed", "blocked"}
MODE_VALUES = {"short_drama", "long_drama"}
LOOP_STAGE_IDS = {"S3", "S4", "S5", "S6", "S7", "S8"}

# Shared markers + helpers used by all 9 stage validators.
# BASE_NOISE_MARKERS are the common "this is process text, not a clean output" markers.
# Each stage validator imports BASE_NOISE_MARKERS and appends its own stage-specific
# markers (e.g. "## 时长判断" for S3, "## S6 能力边界" for S6).
BASE_NOISE_MARKERS: list[str] = [
    "Workflow",
    "workflow",
    "V2 原则",
    "## 输入来源",
    "## 人工确认项",
]

# V2 handoff source schema (canonical shape). The from-handoff script writes into
# workflow_state.json.source using these keys. See bin/slbb-video-from-handoff.
SOURCE_FIELDS: list[str] = [
    "handoff_version",
    "v2_video_url",
    "v2_metrics",
    "matched_rules",
    "manual_note",
    "selection_reason",
    "project_folder_name",
    "platform",
    "title",
]


def section_text(text: str, heading: str) -> str:
    """Return the body of `heading` section in `text`, or "" if not found.

    A section is bounded by `heading` and the next `\\n## ` heading at the same level.
    Used by S1-S8 validators to extract a sub-section's body for further checks.
    """
    start = text.find(heading)
    if start < 0:
        return ""
    rest = text[start + len(heading):]
    next_heading = rest.find("\n## ")
    if next_heading >= 0:
        rest = rest[:next_heading]
    return rest.strip()

SHORT_S1_STAGE: dict[str, Any] = {
    "id": "S1",
    "name": "短剧调研与剧情提取",
    "skill": "slbb-video-research-script",
    "outputs": [
        "artifacts/S1/story_extract.md",
        "artifacts/S1/story_segments.json",
    ],
    "gate": "human_confirm_story",
    "validator": "slbb-video-research-script/scripts/validate_s1_outputs.py",
}

LONG_S1_STAGE: dict[str, Any] = {
    "id": "S1",
    "name": "长剧复刻描述与二创描述",
    "skill": "slbb-video-long-replica-script",
    "outputs": [
        "artifacts/S1/source_replica_description.md",
        "artifacts/S1/second_creation_description.md",
        "artifacts/S1/story_segments.json",
        "artifacts/_meta/S1_replica_notes.md",
    ],
    "gate": "human_confirm_replica_description",
    "validator": "slbb-video-long-replica-script/scripts/validate_s1_outputs.py",
}

COMMON_STAGES: list[dict[str, Any]] = [
    {
        "id": "S2",
        "name": "图片提示词",
        "skill": "slbb-video-image-prompts",
        "outputs": ["artifacts/S2/image_prompt_pack.md"],
        "gate": "human_confirm_image_prompts",
        "validator": "slbb-video-image-prompts/scripts/validate_s2_outputs.py",
    },
    {
        "id": "S3",
        "name": "生视频提示词",
        "skill": "slbb-video-motion-prompts",
        "outputs": [
            "artifacts/S3/motion_prompt_pack.md",
            "artifacts/S3/platform_copy_ready_prompts.md",
        ],
        "gate": "human_confirm_motion_prompts",
        "validator": "slbb-video-motion-prompts/scripts/validate_s3_outputs.py",
    },
    {
        "id": "S4",
        "name": "视频生成记录",
        "skill": "slbb-video-generation-log",
        "outputs": [
            "artifacts/S4/generation_run_log.md",
            "artifacts/S4/generation_run_log.csv",
        ],
        "gate": "human_select_video_version",
        "validator": "slbb-video-generation-log/scripts/validate_s4_outputs.py",
    },
    {
        "id": "S5",
        "name": "视频质检",
        "skill": "slbb-video-qc",
        "outputs": [
            "artifacts/S5/qc_report.md",
            "artifacts/S5/qc_verdict.json",
            "artifacts/S5/rework_suggestions.md",
        ],
        "gate": "human_confirm_qc",
        "validator": "slbb-video-qc/scripts/validate_s5_outputs.py",
    },
    {
        "id": "S6",
        "name": "剪辑修正",
        "skill": "slbb-video-edit-fix",
        "outputs": [
            "artifacts/S6/edit_fix_plan.md",
            "artifacts/S6/edit_checklist.md",
        ],
        "gate": "human_confirm_edit",
        "validator": "slbb-video-edit-fix/scripts/validate_s6_outputs.py",
    },
    {
        "id": "S7",
        "name": "分发包",
        "skill": "slbb-video-distribution-pack",
        "outputs": [
            "artifacts/S7/distribution_pack.md",
            "artifacts/S7/platform_copy.md",
            "artifacts/S7/publish_checklist.md",
        ],
        "gate": "human_confirm_publish_pack",
        "validator": "slbb-video-distribution-pack/scripts/validate_s7_outputs.py",
    },
    {
        "id": "S8",
        "name": "发布后复盘",
        "skill": "slbb-video-review",
        "outputs": [
            "artifacts/S8/review_report.md",
            "artifacts/S8/next_iteration_plan.md",
        ],
        "gate": "human_confirm_review",
        "validator": "slbb-video-review/scripts/validate_s8_outputs.py",
    },
]

STAGES_BY_MODE: dict[str, list[dict[str, Any]]] = {
    "short_drama": [SHORT_S1_STAGE, *COMMON_STAGES],
    "long_drama": [LONG_S1_STAGE, *COMMON_STAGES],
}

# Backward-compatible default for old scripts/imports that expect STAGES.
STAGES: list[dict[str, Any]] = STAGES_BY_MODE["short_drama"]


def normalize_mode(mode: str | None) -> str:
    if mode in MODE_VALUES:
        return str(mode)
    return "short_drama"


def stages_for_mode(mode: str | None) -> list[dict[str, Any]]:
    return STAGES_BY_MODE[normalize_mode(mode)]


def workflow_mode(state: dict[str, Any]) -> str:
    return normalize_mode(state.get("mode"))


def stages_for_state(state: dict[str, Any]) -> list[dict[str, Any]]:
    return stages_for_mode(workflow_mode(state))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def skills_root() -> Path:
    env_root = os.environ.get("CODEX_SKILLS_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def state_path(run_dir: Path) -> Path:
    return run_dir / "workflow_state.json"


def stage_by_id(stage_id: str, mode: str | None = None) -> dict[str, Any]:
    for stage in stages_for_mode(mode):
        if stage["id"] == stage_id:
            return stage
    raise KeyError(f"unknown stage: {stage_id}")


def default_state(title: str, mode: str = "short_drama") -> dict[str, Any]:
    mode = normalize_mode(mode)
    stages = stages_for_mode(mode)
    return {
        "workflow_name": "slbb-video-workflow",
        "version": "0.3",
        "mode": mode,
        "title": title,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "current_stage": "S1",
        "source": {
            "handoff_version": None,
            "v2_video_url": None,
            "v2_metrics": {},
            "matched_rules": [],
            "manual_note": None,
            "selection_reason": None,
            "project_folder_name": None,
            "platform": None,
            "title": None,
            "source_kind": None,
            "source_ref": None,
            "source_manifest": None,
            "source_brief": None,
            "source_note": None,
            "evidence_quality": None,
            "video_ingest": None,
            "shot_index": None,
        },
        "segment_state": {
            "status": "not_started",
            "segment_ids": [],
            "current_segment": None,
            "completed_segments": [],
            "archived_segments": {},
            "notes": [],
        },
        "stages": {
            stage["id"]: {
                "name": stage["name"],
                "skill": stage["skill"],
                "status": "pending",
                "gate": stage["gate"],
                "gate_status": "pending",
                "required_outputs": stage["outputs"],
                "notes": [],
            }
            for stage in stages
        },
    }


def ensure_stage_states(state: dict[str, Any]) -> None:
    state["mode"] = workflow_mode(state)
    stage_states = state.setdefault("stages", {})
    for stage in stages_for_state(state):
        stage_state = stage_states.setdefault(stage["id"], {})
        stage_state["name"] = stage["name"]
        stage_state["skill"] = stage["skill"]
        stage_state["gate"] = stage["gate"]
        stage_state["required_outputs"] = stage["outputs"]
        stage_state.setdefault("status", "pending")
        stage_state.setdefault("gate_status", "pending")
        stage_state.setdefault("notes", [])


def load_state(run_dir: Path) -> dict[str, Any]:
    path = state_path(run_dir)
    if not path.exists():
        raise FileNotFoundError(f"missing workflow_state.json: {path}")
    state = json.loads(path.read_text(encoding="utf-8"))
    state.setdefault("mode", "short_drama")
    source = state.setdefault("source", {})
    source.setdefault("source_kind", None)
    source.setdefault("source_ref", None)
    source.setdefault("source_manifest", None)
    source.setdefault("source_brief", None)
    source.setdefault("source_note", None)
    source.setdefault("evidence_quality", None)
    source.setdefault("video_ingest", None)
    source.setdefault("shot_index", None)
    ensure_segment_state(state)
    ensure_stage_states(state)
    return state


def long_drama_s1_prerequisite_errors(run_dir: Path, state: dict[str, Any]) -> list[str]:
    """Return blockers that must be resolved before long-drama S1 starts."""
    if workflow_mode(state) != "long_drama":
        return []

    source = state.get("source") or {}
    manifest_rel = source.get("source_manifest") or "artifacts/_source/source_manifest.json"
    manifest_path = run_dir / manifest_rel
    if not manifest_path.exists():
        return [
            "missing source manifest: artifacts/_source/source_manifest.json "
            "(run slbb-video-source before long-drama S1)"
        ]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid source manifest JSON: {exc}"]

    source_kind = manifest.get("source_kind") or source.get("source_kind")
    source_ref = manifest.get("source_ref") or source.get("source_ref") or ""
    evidence_quality = manifest.get("evidence_quality") or source.get("evidence_quality")

    if source_kind in {None, "", "link"}:
        return ["source_kind is not classified; rerun slbb-video-source with --source-ref"]

    if source_kind == "platform_link":
        return [
            "source is a platform link and cannot enter S1 directly. "
            "Download/record it as a local video first, then rerun slbb-video-source and slbb-video-ingest. "
            f"source_ref={source_ref}"
        ]

    if source_kind in {"local_video", "direct_video_url"}:
        required = [
            "artifacts/_audit/video_ingest/ingest_report.md",
            "artifacts/_audit/video_ingest/shot_index.json",
            "artifacts/_audit/video_ingest/contact_sheet.jpg",
        ]
        missing = [rel for rel in required if not (run_dir / rel).exists()]
        if missing:
            return [
                "video source is registered but preprocessing evidence is missing; run slbb-video-ingest first",
                *[f"missing video ingest artifact: {rel}" for rel in missing],
            ]
        return []

    if source_kind == "partial_material":
        if evidence_quality != "partial":
            return ["partial_material must set evidence_quality=partial in source_manifest.json"]
        return []

    return [f"unknown source_kind: {source_kind}"]


def save_state(run_dir: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = utc_now()
    state_path(run_dir).write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def missing_outputs(run_dir: Path, stage: dict[str, Any]) -> list[str]:
    return [rel for rel in stage["outputs"] if not (run_dir / rel).exists()]


def ensure_segment_state(state: dict[str, Any]) -> dict[str, Any]:
    segment_state = state.setdefault("segment_state", {})
    segment_state.setdefault("status", "not_started")
    segment_state.setdefault("segment_ids", [])
    segment_state.setdefault("current_segment", None)
    segment_state.setdefault("completed_segments", [])
    segment_state.setdefault("archived_segments", {})
    segment_state.setdefault("notes", [])
    return segment_state


def story_segment_ids(run_dir: Path) -> list[str]:
    path = run_dir / "artifacts" / "S1" / "story_segments.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    episodes = data.get("episodes", [])
    ids: list[str] = []
    for index, episode in enumerate(episodes, start=1):
        episode_id = str(episode.get("episode_id", "")).strip()
        ids.append(episode_id or f"{index:03d}")
    return ids


def initialize_segments_from_story(run_dir: Path, state: dict[str, Any]) -> dict[str, Any]:
    segment_state = ensure_segment_state(state)
    if segment_state["segment_ids"]:
        return segment_state

    segment_ids = story_segment_ids(run_dir)
    segment_state["segment_ids"] = segment_ids
    if segment_ids:
        segment_state["current_segment"] = segment_ids[0]
        segment_state["status"] = "active"
        segment_state["notes"].append(
            {"at": utc_now(), "text": f"S2 completed; locked first target segment: {segment_ids[0]}"}
        )
    else:
        segment_state["status"] = "not_started"
        segment_state["notes"].append(
            {"at": utc_now(), "text": "S2 completed but no segment ids were found in story_segments.json"}
        )
    return segment_state


def current_segment_for_stage(state: dict[str, Any], stage_id: str) -> str | None:
    if stage_id not in LOOP_STAGE_IDS:
        return None
    segment_state = ensure_segment_state(state)
    current = segment_state.get("current_segment")
    return str(current) if current else None


def reset_loop_stages(state: dict[str, Any], next_segment: str) -> None:
    for stage in stages_for_state(state):
        if stage["id"] not in LOOP_STAGE_IDS:
            continue
        stage_state = state["stages"][stage["id"]]
        stage_state["status"] = "pending"
        stage_state["gate_status"] = "pending"
        stage_state["notes"] = [{"at": utc_now(), "text": f"Reset for target segment {next_segment}"}]
        stage_state["segment_id"] = next_segment
        stage_state.pop("completed_at", None)


def archive_current_segment_artifacts(run_dir: Path, segment_id: str) -> Path:
    # Use a single ISO8601 compact suffix (YYYYMMDDTHHMMSSZ) when a same-named
    # archive already exists, instead of mutating the timestamp with `.replace(':')`
    # which produced awkward strings like `2026-06-10T15:48:00Z00:00`.
    archive_root = run_dir / "artifacts" / "_segments" / segment_id
    if archive_root.exists():
        suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive_root = run_dir / "artifacts" / "_segments" / f"{segment_id}-{suffix}"
    archive_root.mkdir(parents=True, exist_ok=True)

    for stage_id in sorted(LOOP_STAGE_IDS):
        source = run_dir / "artifacts" / stage_id
        if source.exists():
            shutil.move(str(source), str(archive_root / stage_id))

    for support_dir in ["_meta", "_audit", "_handoff"]:
        source_dir = run_dir / "artifacts" / support_dir
        if not source_dir.exists():
            continue
        target_dir = archive_root / support_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        for path in list(source_dir.iterdir()):
            if path.name == "next_step.md":
                continue
            if not path.name.startswith(tuple(LOOP_STAGE_IDS)):
                continue
            shutil.move(str(path), str(target_dir / path.name))

    return archive_root


def complete_current_segment(run_dir: Path, state: dict[str, Any]) -> str | None:
    segment_state = ensure_segment_state(state)
    current = segment_state.get("current_segment")
    if not current:
        return None

    completed = segment_state["completed_segments"]
    if current not in completed:
        completed.append(current)
    archive_path = archive_current_segment_artifacts(run_dir, current)
    segment_state["archived_segments"][current] = str(archive_path.relative_to(run_dir))

    next_segment = next((segment_id for segment_id in segment_state["segment_ids"] if segment_id not in completed), None)
    if next_segment:
        segment_state["current_segment"] = next_segment
        segment_state["status"] = "active"
        segment_state["notes"].append(
            {"at": utc_now(), "text": f"Segment {current} completed; next target segment: {next_segment}"}
        )
        reset_loop_stages(state, next_segment)
        return next_segment

    segment_state["current_segment"] = None
    segment_state["status"] = "complete"
    segment_state["notes"].append({"at": utc_now(), "text": f"Segment {current} completed; all segments complete"})
    return None


def first_unfinished_stage(state: dict[str, Any]) -> dict[str, Any] | None:
    for stage in stages_for_state(state):
        if state["stages"][stage["id"]]["status"] != "completed":
            return stage
    return None


def previous_stages_completed(state: dict[str, Any], stage_id: str) -> bool:
    for stage in stages_for_state(state):
        if stage["id"] == stage_id:
            return True
        if state["stages"][stage["id"]]["status"] != "completed":
            return False
    return False


def run_stage_validator(run_dir: Path, stage: dict[str, Any]) -> tuple[int, str]:
    validator = skills_root() / stage["validator"]
    if not validator.exists():
        return 0, f"validator not found, skipped: {validator}"
    result = subprocess.run(
        [sys.executable, str(validator), str(run_dir)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode, result.stdout.strip()


def record_validator_failure(state: dict[str, Any], stage_id: str, output: str) -> None:
    """Append a structured validator-failure note to the stage so next_step can surface it.

    The note is kept short (first 3 non-empty lines of the validator output) to avoid
    polluting the state file. Caller is responsible for `save_state` afterwards.
    """
    if not output.strip():
        return
    lines = [line.strip() for line in output.strip().splitlines() if line.strip()]
    summary = "\n".join(lines[:3])
    state["stages"][stage_id].setdefault("notes", []).append(
        {"at": utc_now(), "text": f"validator_failed: {summary}", "kind": "validator_failure"}
    )


def latest_validator_failure(state: dict[str, Any], stage_id: str) -> str | None:
    """Return the most recent validator-failure summary for a stage, or None."""
    notes = state.get("stages", {}).get(stage_id, {}).get("notes", [])
    for note in reversed(notes):
        if isinstance(note, dict) and note.get("kind") == "validator_failure":
            return note.get("text", "")
    return None


def latest_validator_failure_anywhere(state: dict[str, Any]) -> tuple[str, str] | None:
    """Return (stage_id, summary) of the most recent validator failure across all stages.

    Used by next_step so the operator sees a recent failure even if it was on the
    previous stage (the one that just completed and the next skill builds on).
    """
    most_recent: tuple[str, str, str] | None = None  # (at, stage_id, text)
    for stage_id, stage_state in state.get("stages", {}).items():
        for note in stage_state.get("notes", []):
            if isinstance(note, dict) and note.get("kind") == "validator_failure":
                at = note.get("at", "")
                if most_recent is None or at > most_recent[0]:
                    most_recent = (at, stage_id, note.get("text", ""))
    if most_recent is None:
        return None
    return (most_recent[1], most_recent[2])


def write_handoff(run_dir: Path, stage: dict[str, Any], message: str, target_segment: str | None = None) -> Path:
    handoff_dir = run_dir / "artifacts" / "_handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    output_lines = "\n".join(f"- `{rel}`" for rel in stage["outputs"])
    segment_block = ""
    if stage["id"] in LOOP_STAGE_IDS:
        segment_block = f"""
## 当前目标片段

`{target_segment or "未锁定"}`

"""
    content = f"""# 下一步执行卡

## 当前阶段

{stage["id"]}：{stage["name"]}

{segment_block}## 应使用的 Skill

`{stage["skill"]}`

## 必须产物

{output_lines}

## 人工闸门

`{stage["gate"]}`

## 状态说明

{message}

## 推荐命令

macOS / Linux:

```bash
python3 "$CODEX_SKILLS_ROOT/{stage["skill"]}/scripts/scaffold_{stage["id"].lower()}_run.py" <AI短剧生成过程文件目录>
```

Windows PowerShell:

```powershell
py -3 "$env:CODEX_SKILLS_ROOT/{stage["skill"]}/scripts/scaffold_{stage["id"].lower()}_run.py" <AI短剧生成过程文件目录>
```
"""
    path = handoff_dir / "next_step.md"
    path.write_text(content, encoding="utf-8")
    return path
