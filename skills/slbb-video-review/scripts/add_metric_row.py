#!/usr/bin/env python3
"""Append one platform metric row to S8 review_report.md."""

from __future__ import annotations

import argparse
from pathlib import Path


REPORT_TEMPLATE = """# S8 复盘报告

## 输入来源

## 发布数据

## 平台表现对比

## 评论与用户反馈

## 问题归因

## 上游反推

## 结论
"""


TABLE_HEADER = "| 平台 | 发布时间 | 播放 | 点赞 | 评论 | 转发 | 收藏 | 完播率 | 留存 | 用户反馈 |\n| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |"


def section_bounds(text: str, heading: str) -> tuple[int, int]:
    start = text.find(heading)
    if start < 0:
        return -1, -1
    content_start = start + len(heading)
    next_start = text.find("\n## ", content_start)
    if next_start < 0:
        next_start = len(text)
    return content_start, next_start


def add_row(text: str, row: str) -> str:
    heading = "## 发布数据"
    if heading not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += f"\n{heading}\n\n"
    start, end = section_bounds(text, heading)
    section = text[start:end].strip()
    if TABLE_HEADER.splitlines()[0] not in section:
        new_section = f"\n\n{TABLE_HEADER}\n{row}\n"
    else:
        new_section = text[start:end].rstrip() + f"\n{row}\n"
    return text[:start] + new_section + text[end:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    parser.add_argument("--platform", required=True)
    parser.add_argument("--publish-time", default="缺失")
    parser.add_argument("--views", required=True, type=int)
    parser.add_argument("--likes", required=True, type=int)
    parser.add_argument("--comments", required=True, type=int)
    parser.add_argument("--shares", required=True, type=int)
    parser.add_argument("--saves", default=0, type=int)
    parser.add_argument("--completion-rate", required=True)
    parser.add_argument("--retention", required=True)
    parser.add_argument("--feedback", required=True)
    args = parser.parse_args()

    path = Path(args.run_dir).expanduser().resolve() / "artifacts" / "S8" / "review_report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.exists() else REPORT_TEMPLATE
    row = (
        f"| {args.platform} | {args.publish_time} | {args.views} | {args.likes} | "
        f"{args.comments} | {args.shares} | {args.saves} | {args.completion_rate} | "
        f"{args.retention} | {args.feedback} |"
    )
    path.write_text(add_row(text, row), encoding="utf-8")
    print(f"Updated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
