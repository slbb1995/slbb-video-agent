#!/usr/bin/env python3
"""Create the S3 artifact skeleton for an AI short-drama workflow run."""

from __future__ import annotations

import argparse
from pathlib import Path


MOTION_PROMPT_PACK = """# S3 生视频提示词包

## 角色锁定

## 场景锁定

## 分镜提示词表

| 时间 | 镜头 | 景别 | 运镜 | 画面内容 | 动作 | 微表情 | 台词口型 | 声音 | 时长 | 本镜头作用 | 平台优化标签 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""

COPY_READY = """# S3 平台复制版提示词

## 即梦复制版

## 可灵复制版
"""

MOTION_NOTES = """# S3 过程备注

## 输入来源

## 平台设置

- 平台：
- 时长：
- 画幅：9:16
- 风格：

## 时长判断

- 有效信息点：
- 是否需要结尾钩子：
- 每 3 秒是否有新信息：
- 推荐时长：
- 不选更长时长的理由：

## 合规与改写备注

## 关键道具与文字风险

## 人工确认备注
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
    s3_dir = run_dir / "artifacts" / "S3"
    meta_dir = run_dir / "artifacts" / "_meta"
    s3_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    created = []
    for name, content in {
        "motion_prompt_pack.md": MOTION_PROMPT_PACK,
        "platform_copy_ready_prompts.md": COPY_READY,
    }.items():
        path = s3_dir / name
        if write_if_missing(path, content):
            created.append(str(path))
    notes = meta_dir / "S3_motion_design_notes.md"
    if write_if_missing(notes, MOTION_NOTES):
        created.append(str(notes))

    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    else:
        print(f"No files created; S3 skeleton already exists: {s3_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
