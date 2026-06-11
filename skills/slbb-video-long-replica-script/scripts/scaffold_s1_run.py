#!/usr/bin/env python3
"""Create the S1 artifact skeleton for a long-drama workflow run."""

from __future__ import annotations

import argparse
from pathlib import Path


SOURCE_REPLICA = """# AI短视频复刻描述提取报告

## 1. 视频基础信息

## 2. 固定角色形象描述

## 3. 视频片段拆分总览

## 4. 分片段详细画面描述

## 5. 台词 / 字幕 / 旁白汇总

## 6. 原视频剧情总结
"""

SECOND_CREATION = """# 二次创作版复刻描述

## 1. 本次二创方向

## 2. 二创后角色形象描述

## 3. 二创后片段拆分总览

## 4. 二创后分片段详细画面描述
"""

STORY_SEGMENTS = """{
  "characters": [],
  "episodes": []
}
"""

REPLICA_NOTES = """# S1 长剧复刻过程备注

## 素材边界

## 缺失信息

## 二创确认

## 进入 S2 前备注
"""

CONFIRMATION_CARD = """# S1 人工确认卡

## 本轮产物

- `artifacts/S1/source_replica_description.md`
- `artifacts/S1/second_creation_description.md`
- `artifacts/S1/story_segments.json`
- `artifacts/_meta/S1_replica_notes.md`

## 需要你确认

- 原视频复刻描述是否准确。
- 二创方向是否符合你的要求。
- 角色形象和多年龄段拆分是否准确。
- 3-15 秒片段拆分是否可以进入 S2。
- 是否需要补视频、录屏、截图、台词或字幕。
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
    s1_dir = run_dir / "artifacts" / "S1"
    meta_dir = run_dir / "artifacts" / "_meta"
    handoff_dir = run_dir / "artifacts" / "_handoff"
    s1_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)
    handoff_dir.mkdir(parents=True, exist_ok=True)

    files = {
        s1_dir / "source_replica_description.md": SOURCE_REPLICA,
        s1_dir / "second_creation_description.md": SECOND_CREATION,
        s1_dir / "story_segments.json": STORY_SEGMENTS,
        meta_dir / "S1_replica_notes.md": REPLICA_NOTES,
        handoff_dir / "S1_human_confirmation_card.md": CONFIRMATION_CARD,
    }
    created = []
    for path, content in files.items():
        if write_if_missing(path, content):
            created.append(str(path))

    print(f"S1 directory: {s1_dir}")
    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    else:
        print("No files created; skeleton already exists.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
