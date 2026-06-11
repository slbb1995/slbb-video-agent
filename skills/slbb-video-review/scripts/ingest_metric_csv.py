#!/usr/bin/env python3
"""Ingest a user-provided platform metrics CSV into S8 evidence files.

This script intentionally does not open browser sessions or scrape platforms.
It only parses a CSV file supplied by the user and records the source path.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path


FIELD_ALIASES = {
    "platform": ["platform", "平台", "渠道"],
    "publish_time": ["publish_time", "发布时间", "发布日期", "time", "date"],
    "views": ["views", "播放", "播放量", "观看", "曝光播放"],
    "likes": ["likes", "点赞", "赞"],
    "comments": ["comments", "评论", "评论数"],
    "shares": ["shares", "转发", "分享", "分享数"],
    "saves": ["saves", "收藏", "收藏数"],
    "completion_rate": ["completion_rate", "完播率", "完播", "完成率"],
    "retention": ["retention", "留存", "留存率", "3秒留存", "5秒留存"],
    "feedback": ["feedback", "用户反馈", "评论摘要", "备注"],
}


TABLE_HEADER = (
    "| 平台 | 发布时间 | 播放 | 点赞 | 评论 | 转发 | 收藏 | 完播率 | 留存 | 用户反馈 |\n"
    "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |"
)


def canonical_header_map(headers: list[str]) -> dict[str, str]:
    normalized = {header.strip().lower(): header for header in headers}
    result: dict[str, str] = {}
    for canonical, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            key = alias.strip().lower()
            if key in normalized:
                result[canonical] = normalized[key]
                break
    return result


def value(row: dict[str, str], header_map: dict[str, str], canonical: str, default: str = "缺失") -> str:
    header = header_map.get(canonical)
    if not header:
        return default
    raw = row.get(header, "").strip()
    return raw if raw else default


def read_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise SystemExit(f"CSV has no header row: {csv_path}")
        header_map = canonical_header_map(reader.fieldnames)
        required = ["platform", "views", "likes", "comments", "shares"]
        missing = [field for field in required if field not in header_map]
        if missing:
            raise SystemExit(
                "CSV missing required columns or aliases: "
                + ", ".join(missing)
                + "\nAccepted aliases are documented in FIELD_ALIASES."
            )
        rows = []
        for row in reader:
            rows.append(
                {
                    "platform": value(row, header_map, "platform"),
                    "publish_time": value(row, header_map, "publish_time"),
                    "views": value(row, header_map, "views", "0"),
                    "likes": value(row, header_map, "likes", "0"),
                    "comments": value(row, header_map, "comments", "0"),
                    "shares": value(row, header_map, "shares", "0"),
                    "saves": value(row, header_map, "saves", "0"),
                    "completion_rate": value(row, header_map, "completion_rate"),
                    "retention": value(row, header_map, "retention"),
                    "feedback": value(row, header_map, "feedback"),
                }
            )
    return rows


def section_bounds(text: str, heading: str) -> tuple[int, int]:
    start = text.find(heading)
    if start < 0:
        return -1, -1
    content_start = start + len(heading)
    next_start = text.find("\n## ", content_start)
    if next_start < 0:
        next_start = len(text)
    return content_start, next_start


def row_to_markdown(row: dict[str, str]) -> str:
    return (
        f"| {row['platform']} | {row['publish_time']} | {row['views']} | {row['likes']} | "
        f"{row['comments']} | {row['shares']} | {row['saves']} | {row['completion_rate']} | "
        f"{row['retention']} | {row['feedback']} |"
    )


def update_review_table(review_path: Path, rows: list[dict[str, str]]) -> None:
    if review_path.exists():
        text = review_path.read_text(encoding="utf-8")
    else:
        text = "# S8 复盘报告\n\n## 发布数据\n\n"

    heading = "## 发布数据"
    if heading not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += f"\n{heading}\n\n"

    start, end = section_bounds(text, heading)
    row_text = "\n".join(row_to_markdown(row) for row in rows)
    new_section = f"\n\n{TABLE_HEADER}\n{row_text}\n"
    review_path.write_text(text[:start] + new_section + text[end:], encoding="utf-8")


def write_evidence(evidence_dir: Path, csv_path: Path, rows: list[dict[str, str]], source: str) -> Path:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    copied = evidence_dir / f"source_metrics_{csv_path.name}"
    if csv_path.resolve() != copied.resolve():
        shutil.copy2(csv_path, copied)

    out = evidence_dir / "metrics_from_csv.md"
    lines = [
        "# S8 CSV 指标解析记录",
        "",
        f"解析时间：{datetime.now().isoformat(timespec='seconds')}",
        f"来源说明：{source}",
        f"原始 CSV：`{csv_path}`",
        f"留证副本：`{copied}`",
        "",
        TABLE_HEADER,
        *[row_to_markdown(row) for row in rows],
        "",
        "说明：本文件只解析用户提供的 CSV，不自动登录后台，不自动抓取平台页面。",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest user-provided S8 platform metric CSV.")
    parser.add_argument("run_dir", help="Workflow run directory")
    parser.add_argument("csv_path", type=Path, help="User-provided CSV export path")
    parser.add_argument("--source", default="用户提供 CSV")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    csv_path = args.csv_path.expanduser().resolve()
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    rows = read_rows(csv_path)
    if not rows:
        raise SystemExit(f"CSV contains no data rows: {csv_path}")

    s8_dir = run_dir / "artifacts" / "S8"
    s8_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = write_evidence(s8_dir / "evidence", csv_path, rows, args.source)
    update_review_table(s8_dir / "review_report.md", rows)
    print(f"Rows ingested: {len(rows)}")
    print(f"Evidence: {evidence_path}")
    print(f"Updated: {s8_dir / 'review_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
