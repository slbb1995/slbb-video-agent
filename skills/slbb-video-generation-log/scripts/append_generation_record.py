#!/usr/bin/env python3
"""Append one manual video generation attempt to S4 CSV log."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path


CSV_COLUMNS = [
    "record_id",
    "clip_id",
    "episode_id",
    "platform",
    "generation_mode",
    "prompt_ref",
    "reference_assets",
    "settings",
    "output_ref",
    "status",
    "selected_for_qc",
    "failure_reason",
    "created_at",
    "operator_notes",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    parser.add_argument("--record-id", default="", help="Unique attempt id; auto-filled if omitted")
    parser.add_argument("--clip-id", required=True)
    parser.add_argument("--episode-id", default="")
    parser.add_argument("--platform", required=True)
    parser.add_argument("--generation-mode", required=True)
    parser.add_argument("--prompt-ref", required=True)
    parser.add_argument("--reference-assets", default="")
    parser.add_argument("--settings", default="")
    parser.add_argument("--output-ref", required=True)
    parser.add_argument("--status", required=True, choices=["success", "failed", "selected", "rejected", "retry_needed"])
    parser.add_argument("--selected-for-qc", default="no", choices=["yes", "no"])
    parser.add_argument("--failure-reason", default="")
    parser.add_argument("--created-at", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    csv_path = run_dir / "artifacts" / "S4" / "generation_run_log.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
    else:
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
            writer.writeheader()

    record_id = args.record_id or f"s4-{len(rows) + 1:03d}"
    row = {
        "record_id": record_id,
        "clip_id": args.clip_id,
        "episode_id": args.episode_id,
        "platform": args.platform,
        "generation_mode": args.generation_mode,
        "prompt_ref": args.prompt_ref,
        "reference_assets": args.reference_assets,
        "settings": args.settings,
        "output_ref": args.output_ref,
        "status": args.status,
        "selected_for_qc": args.selected_for_qc,
        "failure_reason": args.failure_reason,
        "created_at": args.created_at or datetime.now().isoformat(timespec="seconds"),
        "operator_notes": args.notes,
    }

    with csv_path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writerow(row)

    print(f"Appended S4 generation record: {record_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
