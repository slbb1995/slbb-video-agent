#!/usr/bin/env python3
"""Create the S7 artifact skeleton for an AI short-drama workflow run."""

from __future__ import annotations

import argparse
from pathlib import Path


DISTRIBUTION_PACK = """# S7 分发包

发布状态：未发布。本 Skill 不自动发布，后续由人工手动发布。

## 成片信息

## 标题候选

## 简介与看点

## 封面建议

## 发布时间建议
"""

PLATFORM_COPY = """# S7 平台文案

发布状态：未发布。本 Skill 不自动发布，后续由人工手动发布。

## 抖音

## 视频号

## 小红书
"""

PUBLISH_CHECKLIST = """# S7 发布检查清单

发布状态：未发布。本 Skill 不自动发布，后续由人工手动发布。

## 素材检查

## 文案检查

## 账号与平台检查

## 手动发布状态

## 进入下一步条件
"""

DISTRIBUTION_NOTES = """# S7 过程备注

## 输入来源

## 风险与人工确认

## 平台发布备注
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
    s7_dir = run_dir / "artifacts" / "S7"
    meta_dir = run_dir / "artifacts" / "_meta"
    s7_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    created = []
    for name, content in {
        "distribution_pack.md": DISTRIBUTION_PACK,
        "platform_copy.md": PLATFORM_COPY,
        "publish_checklist.md": PUBLISH_CHECKLIST,
    }.items():
        path = s7_dir / name
        if write_if_missing(path, content):
            created.append(str(path))
    notes = meta_dir / "S7_distribution_notes.md"
    if write_if_missing(notes, DISTRIBUTION_NOTES):
        created.append(str(notes))

    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    else:
        print(f"No files created; S7 skeleton already exists: {s7_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
