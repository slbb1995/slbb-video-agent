#!/usr/bin/env python3
"""Validate S4 generation log artifacts for the AI short-drama workflow."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

# Validators live in slbb-video-<X>/scripts/ but import shared helpers
# (BASE_NOISE_MARKERS, section_text) from slbb-video-orchestrator/scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slbb-video-orchestrator" / "scripts"))

from workflow_lib import BASE_NOISE_MARKERS, section_text


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

MD_HEADINGS = [
    "## 平台执行摘要",
    "## 生成版本记录",
    "## 选中版本",
    "## 失败与返工记录",
]

VALID_STATUSES = {"success", "failed", "selected", "rejected", "retry_needed"}
NOISE_MARKERS = BASE_NOISE_MARKERS + [
    "不能自动进入下一步",
]


def fail(errors: list[str]) -> int:
    print("S4 validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    s4_dir = run_dir / "artifacts" / "S4"
    md_path = s4_dir / "generation_run_log.md"
    csv_path = s4_dir / "generation_run_log.csv"
    errors: list[str] = []

    for path in [md_path, csv_path]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        return fail(errors)

    md_text = md_path.read_text(encoding="utf-8")
    for heading in MD_HEADINGS:
        if heading not in md_text:
            errors.append(f"generation_run_log.md missing heading: {heading}")
        elif not section_text(md_text, heading):
            errors.append(f"generation_run_log.md empty section: {heading}")
    for marker in NOISE_MARKERS:
        if marker in md_text:
            errors.append(f"generation_run_log.md contains process/noise marker: {marker}")

    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        missing_columns = [column for column in CSV_COLUMNS if column not in fieldnames]
        if missing_columns:
            errors.append(f"generation_run_log.csv missing columns: {', '.join(missing_columns)}")
        rows = list(reader)

    if not rows:
        errors.append("generation_run_log.csv must contain at least one generation record")
    else:
        has_selected = False
        for index, row in enumerate(rows, start=1):
            prefix = f"row {index}"
            for column in ["record_id", "clip_id", "platform", "generation_mode", "prompt_ref", "output_ref", "status", "selected_for_qc"]:
                if not str(row.get(column, "")).strip():
                    errors.append(f"{prefix} missing required value: {column}")
            status = row.get("status", "")
            if status and status not in VALID_STATUSES:
                errors.append(f"{prefix} invalid status: {status}")
            if status in {"failed", "retry_needed"} and not str(row.get("failure_reason", "")).strip():
                errors.append(f"{prefix} status {status} requires failure_reason")
            selected = str(row.get("selected_for_qc", "")).strip().lower()
            if selected == "yes" or status == "selected":
                has_selected = True
        if not has_selected:
            errors.append("at least one generation record must be selected for S5 QC")

    if errors:
        return fail(errors)

    print("S4 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
