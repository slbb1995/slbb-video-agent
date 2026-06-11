#!/usr/bin/env python3
"""Create the S8 artifact skeleton for an AI short-drama workflow run."""

from __future__ import annotations

import argparse
from pathlib import Path


REVIEW_REPORT = """# S8 复盘报告

## 输入来源

## 发布数据

## 平台表现对比

## 评论与用户反馈

## 问题归因

## 上游反推

## 结论
"""

NEXT_PLAN = """# S8 下一轮迭代计划

## 下一轮选题建议

## 剧情调整

## 图片提示词调整

## 视频提示词调整

## 生成与质检调整

## 剪辑与分发调整

## 人工确认项
"""


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    s8_dir = run_dir / "artifacts" / "S8"
    s8_dir.mkdir(parents=True, exist_ok=True)

    created = []
    for name, content in {
        "review_report.md": REVIEW_REPORT,
        "next_iteration_plan.md": NEXT_PLAN,
    }.items():
        path = s8_dir / name
        if write_if_missing(path, content):
            created.append(str(path))

    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    else:
        print(f"No files created; S8 skeleton already exists: {s8_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
