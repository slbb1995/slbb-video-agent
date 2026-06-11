#!/usr/bin/env python3
"""Append an edit-fix item to S6 plan and checklist."""

from __future__ import annotations

import argparse
from pathlib import Path


VALID_TYPES = [
    "subtitle_cover",
    "caption_replace",
    "trim",
    "crop_or_mask",
    "audio_note",
    "rework_only",
    "accept_defer",
    "bridge_shot",
    "segment_regenerate",
    "continuity_trim",
]


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in text:
        return
    path.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


def append_to_section(path: Path, heading: str, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in text:
        return
    if heading not in text:
        append_once(path, marker, block)
        return
    start = text.index(heading) + len(heading)
    rest = text[start:]
    next_heading = rest.find("\n## ")
    insert_at = len(text) if next_heading < 0 else start + next_heading
    new_text = text[:insert_at].rstrip() + "\n\n" + block.strip() + "\n" + text[insert_at:]
    path.write_text(new_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    parser.add_argument("--fix-id", required=True)
    parser.add_argument("--type", required=True, choices=VALID_TYPES)
    parser.add_argument("--timestamp", required=True)
    parser.add_argument("--problem", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--acceptance", required=True)
    args = parser.parse_args()

    s6_dir = Path(args.run_dir).expanduser().resolve() / "artifacts" / "S6"
    s6_dir.mkdir(parents=True, exist_ok=True)
    plan = s6_dir / "edit_fix_plan.md"
    checklist = s6_dir / "edit_checklist.md"

    plan_block = f"""### {args.fix_id}

- 类型：{args.type}
- 时间段：{args.timestamp}
- 问题：{args.problem}
- 动作：{args.action}
- 验收：{args.acceptance}
"""
    checklist_block = f"""- [ ] `{args.fix_id}` `{args.type}` `{args.timestamp}`：人工执行：{args.action}。验收：{args.acceptance}
"""

    append_once(plan, f"### {args.fix_id}", plan_block)
    append_to_section(checklist, "## 修正项清单", f"`{args.fix_id}`", checklist_block)
    print(f"Appended S6 edit fix item: {args.fix_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
