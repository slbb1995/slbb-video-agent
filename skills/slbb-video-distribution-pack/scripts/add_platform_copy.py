#!/usr/bin/env python3
"""Insert or replace one platform copy block in S7 platform_copy.md."""

from __future__ import annotations

import argparse
from pathlib import Path


PLATFORMS = ["抖音", "视频号", "小红书"]


def replace_section(text: str, heading: str, content: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        if not text.endswith("\n"):
            text += "\n"
        return f"{text}\n{marker}\n\n{content.strip()}\n"

    section_start = start + len(marker)
    next_start = text.find("\n## ", section_start)
    replacement = f"{marker}\n\n{content.strip()}\n"
    if next_start < 0:
        return text[:start] + replacement
    return text[:start] + replacement + text[next_start:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    parser.add_argument("--platform", required=True, choices=PLATFORMS)
    parser.add_argument("--title", required=True)
    parser.add_argument("--caption", required=True)
    parser.add_argument("--hashtags", required=True)
    parser.add_argument("--cover", required=True)
    parser.add_argument("--publish-time", required=True)
    args = parser.parse_args()

    path = Path(args.run_dir).expanduser().resolve() / "artifacts" / "S7" / "platform_copy.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = "# S7 平台文案\n\n发布状态：未发布。本 Skill 不自动发布，后续由人工手动发布。\n"

    block = f"""- 标题：{args.title}
- 正文：{args.caption}
- 话题 / 标签：{args.hashtags}
- 封面建议：{args.cover}
- 发布时间建议：{args.publish_time}"""

    path.write_text(replace_section(text, args.platform, block), encoding="utf-8")
    print(f"Updated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
