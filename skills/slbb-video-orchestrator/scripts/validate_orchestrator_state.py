#!/usr/bin/env python3
"""Validate workflow_state.json ordering, gates, and completed-stage artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from workflow_lib import (
    LOOP_STAGE_IDS,
    STATUS_VALUES,
    ensure_segment_state,
    first_unfinished_stage,
    load_state,
    long_drama_s1_prerequisite_errors,
    missing_outputs,
    record_validator_failure,
    run_stage_validator,
    save_state,
    stages_for_state,
)


def fail(errors: list[str]) -> int:
    print("Orchestrator validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="AI 短剧生成过程文件目录")
    parser.add_argument("--run-stage-validators", action="store_true")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    errors: list[str] = []
    try:
        state = load_state(run_dir)
    except Exception as exc:  # noqa: BLE001 - command-line validator should surface the exact issue
        return fail([str(exc)])

    if state.get("workflow_name") != "slbb-video-workflow":
        errors.append("workflow_name must be slbb-video-workflow")

    if state.get("mode") == "long_drama" and state.get("stages", {}).get("S1", {}).get("status") != "completed":
        for error in long_drama_s1_prerequisite_errors(run_dir, state):
            errors.append(f"long_drama S1 preflight: {error}")

    segment_state = ensure_segment_state(state)
    s2_completed = state.get("stages", {}).get("S2", {}).get("status") == "completed"
    if s2_completed:
        if not segment_state.get("segment_ids"):
            errors.append("S2 is completed but segment_state.segment_ids is empty")
        if segment_state.get("status") not in {"active", "complete"}:
            errors.append("S2 is completed but segment_state.status is not active or complete")
        for segment_id in segment_state.get("completed_segments", []):
            archive_rel = segment_state.get("archived_segments", {}).get(segment_id)
            if not archive_rel:
                errors.append(f"segment {segment_id} is completed but missing archived_segments entry")
            elif not (run_dir / archive_rel).exists():
                errors.append(f"segment {segment_id} archive path does not exist: {archive_rel}")
        if segment_state.get("status") == "complete":
            for segment_id in segment_state.get("segment_ids", []):
                archive_rel = segment_state.get("archived_segments", {}).get(segment_id)
                if not archive_rel:
                    errors.append(f"segment {segment_id} is complete but missing archived_segments entry")
                elif not (run_dir / archive_rel).exists():
                    errors.append(f"segment {segment_id} archive path does not exist: {archive_rel}")

    seen_unfinished = False
    for stage in stages_for_state(state):
        stage_state = state.get("stages", {}).get(stage["id"])
        if not stage_state:
            errors.append(f"missing stage state: {stage['id']}")
            continue
        status = stage_state.get("status")
        if status not in STATUS_VALUES:
            errors.append(f"{stage['id']} invalid status: {status}")
            continue
        if s2_completed and stage["id"] in LOOP_STAGE_IDS and segment_state.get("status") == "active":
            current_segment = segment_state.get("current_segment")
            if not current_segment:
                errors.append(f"{stage['id']} requires segment_state.current_segment after S2 completion")
            stage_segment = stage_state.get("segment_id")
            if status in {"in_progress", "ready_for_human", "completed"} and stage_segment and stage_segment != current_segment:
                errors.append(
                    f"{stage['id']} segment_id {stage_segment} does not match current_segment {current_segment}"
                )
        if seen_unfinished and status == "completed":
            errors.append(f"{stage['id']} is completed before an earlier stage is completed")
        if status != "completed":
            seen_unfinished = True
            continue
        if stage_state.get("gate_status") != "confirmed":
            errors.append(f"{stage['id']} completed without confirmed gate")
        missing = missing_outputs(run_dir, stage)
        if missing and stage["id"] in LOOP_STAGE_IDS and segment_state.get("status") == "complete":
            missing = []
        for rel in missing:
            errors.append(f"{stage['id']} completed but missing output: {rel}")
        if args.run_stage_validators and not missing:
            code, output = run_stage_validator(run_dir, stage)
            if code != 0:
                errors.append(f"{stage['id']} validator failed: {output}")
                # Persist the failure to stage.notes so next_step can surface it in handoff.
                record_validator_failure(state, stage["id"], output)

    expected = first_unfinished_stage(state)
    expected_current = expected["id"] if expected else "complete"

    # handoff presence check: while a stage is in_progress or ready_for_human,
    # artifacts/_handoff/next_step.md should exist and point to the next step.
    if expected_current != "complete":
        handoff_path = run_dir / "artifacts" / "_handoff" / "next_step.md"
        if not handoff_path.exists():
            errors.append(f"missing handoff file: {handoff_path} (current_stage={expected_current})")

    if args.run_stage_validators:
        # Persist any failure notes recorded above so subsequent next_step calls see them.
        save_state(run_dir, state)

    if state.get("current_stage") != expected_current:
        errors.append(f"current_stage should be {expected_current}, got {state.get('current_stage')}")

    if errors:
        return fail(errors)

    print("Orchestrator validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
