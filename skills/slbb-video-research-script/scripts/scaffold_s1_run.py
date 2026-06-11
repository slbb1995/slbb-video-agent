#!/usr/bin/env python3
"""Create the S1 artifact skeleton for an AI short-drama workflow run."""

from __future__ import annotations

import argparse
from pathlib import Path


STORY_EXTRACT = """# S1 剧情提取结果

## 一句话简介

## 核心人物

## 核心场景

## 分集列表

## 下一阶段输入
"""

STORY_META = """# S1 过程备注

## 输入来源

## 调研边界

## 改写与版权风险

## 人工确认备注
"""

SEGMENTATION_DECISION = """# S1 分集数量决策

source_type:
original_episode_count:
collected_source_count:
material_types:
coverage_level:
target_segment_count:
decision_basis:
boundary:
"""

STORY_SEGMENTS = """{
  "characters": [],
  "episodes": []
}
"""

CONFIRMATION_CARD = """# S1 人工确认卡

## 本轮产物

- `artifacts/S1/story_extract.md`
- `artifacts/S1/story_segments.json`
- `artifacts/_meta/S1_segmentation_decision.md`

## 需要你确认

- 剧情提取是否完整。
- 分集数量是否由素材覆盖度和剧情密度支撑。
- 人物关系是否准确。
- 15 秒拆分是否能继续进入 S2。
- 哪些内容属于已验证，哪些内容只是合理推导。
- 哪些内容需要先改写，避免后续提示词太贴近原作。

## 不能自动进入下一步的原因

S2 会根据 S1 结果生成图片提示词；如果 S1 的人物、场景、冲突或版权风险没确认，后续会放大错误。

## 确认后下一步

进入 S2：图片提示词生成。
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

    created = []
    files = {
        s1_dir / "story_extract.md": STORY_EXTRACT,
        s1_dir / "story_segments.json": STORY_SEGMENTS,
        meta_dir / "S1_segmentation_decision.md": SEGMENTATION_DECISION,
        meta_dir / "S1_research_notes.md": STORY_META,
        handoff_dir / "S1_human_confirmation_card.md": CONFIRMATION_CARD,
    }
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
