#!/usr/bin/env python3
"""Advance a workflow stage with artifact and human-gate checks."""

from __future__ import annotations

import argparse
from pathlib import Path

from workflow_lib import (
    STATUS_VALUES,
    STAGES,
    complete_current_segment,
    current_segment_for_stage,
    first_unfinished_stage,
    initialize_segments_from_story,
    latest_validator_failure,
    load_state,
    missing_outputs,
    previous_stages_completed,
    record_validator_failure,
    run_stage_validator,
    save_state,
    stage_by_id,
    utc_now,
    write_handoff,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="AI 短剧生成过程文件目录")
    parser.add_argument("--stage", required=True, choices=[stage["id"] for stage in STAGES])
    parser.add_argument("--status", required=True, choices=sorted(STATUS_VALUES))
    parser.add_argument("--note", default="")
    parser.add_argument("--human-confirmed", action="store_true")
    parser.add_argument("--skip-validator", action="store_true")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    state = load_state(run_dir)
    stage = stage_by_id(args.stage, state.get("mode"))
    stage_state = state["stages"][args.stage]
    target_segment = current_segment_for_stage(state, args.stage)
    if target_segment:
        stage_state["segment_id"] = target_segment

    if args.status in {"ready_for_human", "completed"}:
        missing = missing_outputs(run_dir, stage)
        if missing:
            print(f"{args.stage} cannot be marked {args.status}; missing outputs:")
            for rel in missing:
                print(f"- {rel}")
            return 1
        if not args.skip_validator:
            code, output = run_stage_validator(run_dir, stage)
            if output:
                print(output)
            if code != 0:
                # Record the failure so next_step can surface it in the handoff.
                record_validator_failure(state, args.stage, output)
                save_state(run_dir, state)
                print(f"{args.stage} validator failed; status not advanced.")
                return code

    if args.status == "completed":
        if not previous_stages_completed(state, args.stage):
            print(f"{args.stage} cannot be completed before previous stages are completed.")
            return 1
        if not args.human_confirmed:
            print(f"{args.stage} requires --human-confirmed before completion.")
            return 1
        stage_state["gate_status"] = "confirmed"
        stage_state["completed_at"] = utc_now()
    elif args.status == "ready_for_human":
        stage_state["gate_status"] = "waiting"

    stage_state["status"] = args.status
    if args.note:
        stage_state.setdefault("notes", []).append({"at": utc_now(), "text": args.note})

    if args.stage == "S2" and args.status == "completed":
        initialize_segments_from_story(run_dir, state)

    if args.stage == "S8" and args.status == "completed":
        complete_current_segment(run_dir, state)

    next_stage = first_unfinished_stage(state)
    if next_stage is None:
        state["current_stage"] = "complete"
        save_state(run_dir, state)
        print("Workflow complete: S1-S8 are all completed.")
        return 0

    state["current_stage"] = next_stage["id"]
    next_state = state["stages"][next_stage["id"]]
    if next_state["status"] == "pending":
        next_state["status"] = "in_progress"
    next_segment = current_segment_for_stage(state, next_stage["id"])
    if next_segment:
        next_state["segment_id"] = next_segment

    save_state(run_dir, state)
    segment_note = f"，目标片段 {next_segment}" if next_segment else ""
    handoff = write_handoff(
        run_dir,
        next_stage,
        f"{args.stage} 已更新为 {args.status}。下一步处理 {next_stage['id']}{segment_note}。",
        target_segment=next_segment,
    )
    print(f"Updated {args.stage}: {args.status}")
    print(f"Current stage: {next_stage['id']}")
    print(f"Handoff: {handoff}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
