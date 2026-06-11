#!/usr/bin/env python3
"""Create the S4 artifact skeleton for an AI short-drama workflow run."""

from __future__ import annotations

import argparse
import csv
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

MD_TEMPLATE = """# S4 视频生成记录

## 平台执行摘要

## 生成版本记录

## 选中版本

## 失败与返工记录
"""

AUDIT_TEMPLATE = """# S4 过程备注

## 输入来源

## 人工确认备注
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    s4_dir = run_dir / "artifacts" / "S4"
    audit_dir = run_dir / "artifacts" / "_audit"
    s4_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    md_path = s4_dir / "generation_run_log.md"
    csv_path = s4_dir / "generation_run_log.csv"
    audit_path = audit_dir / "S4_attempt_notes.md"

    created = []
    if not md_path.exists():
        md_path.write_text(MD_TEMPLATE, encoding="utf-8")
        created.append(str(md_path))
    if not csv_path.exists():
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
            writer.writeheader()
        created.append(str(csv_path))
    if not audit_path.exists():
        audit_path.write_text(AUDIT_TEMPLATE, encoding="utf-8")
        created.append(str(audit_path))

    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    else:
        print(f"No files created; S4 skeleton already exists: {s4_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
