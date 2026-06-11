#!/usr/bin/env python3
"""Create the S2 artifact skeleton for an AI short-drama workflow run."""

from __future__ import annotations

import argparse
from pathlib import Path


IMAGE_PROMPT_PACK = """# S2 图片提示词包

## 人物参考提示词

## 场景图提示词

## 首图提示词
"""

PROMPT_NOTES = """# S2 过程备注

## 输入来源

## 路由模式

full_pack

## 推导与风险备注

## 人工确认备注
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    s2_dir = run_dir / "artifacts" / "S2"
    meta_dir = run_dir / "artifacts" / "_meta"
    s2_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)
    target = s2_dir / "image_prompt_pack.md"
    notes = meta_dir / "S2_prompt_notes.md"

    created = []
    if not target.exists():
        target.write_text(IMAGE_PROMPT_PACK, encoding="utf-8")
        created.append(str(target))
    if not notes.exists():
        notes.write_text(PROMPT_NOTES, encoding="utf-8")
        created.append(str(notes))
    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    else:
        print(f"No files created; already exists: {s2_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
