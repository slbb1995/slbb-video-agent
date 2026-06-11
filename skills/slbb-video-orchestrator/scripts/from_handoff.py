#!/usr/bin/env python3
"""Import a V2 handoff (ai-drama-monitor) into a new run directory.

The V2 monitor exports a Markdown handoff.md with sections 1-8 (see
builder.ts renderMarkdown). This script parses that Markdown, writes
workflow_state.json.source, and creates a low-token source packet so long-drama
S1 can read artifacts/_source/source_brief.md before touching raw evidence.

Usage:
    bin/slbb-video-from-handoff <handoff.md> <run_dir>

The run_dir is created if missing. Existing workflow_state.json is
overwritten (this is an init-style command).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from workflow_lib import MODE_VALUES, default_state, save_state, stages_for_mode, utc_now, write_handoff


HANDOFF_VERSION = 1
VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi"}
PLATFORM_DOMAINS = {
    "douyin.com",
    "iesdouyin.com",
    "xiaohongshu.com",
    "xhslink.com",
    "kuaishou.com",
    "kuaishouapp.com",
    "bilibili.com",
    "b23.tv",
}


def _source_kind(source_ref: str | None) -> str:
    if not source_ref:
        return "partial_material"
    parsed = urlparse(source_ref)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        suffix = Path(parsed.path).suffix.lower()
        if suffix in VIDEO_SUFFIXES:
            return "direct_video_url"
        host = parsed.netloc.lower()
        if any(host == domain or host.endswith("." + domain) for domain in PLATFORM_DOMAINS):
            return "platform_link"
        return "platform_link"
    if Path(source_ref).suffix.lower() in VIDEO_SUFFIXES:
        return "local_video"
    return "partial_material"


# --- markdown extractors ----------------------------------------------------

# Pull a single `- **key**：value` line. Returns "" if missing.
def _kv(text: str, key: str) -> str:
    pattern = re.compile(r"^[\s\-\*]*\*\*" + re.escape(key) + r"\*\*\s*[：:]\s*(.+?)\s*$", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


# Pull a section body bounded by `## heading` and the next `## `.
def _section(text: str, heading: str) -> str:
    pattern = re.compile(
        r"^[ \t]*##\s+" + re.escape(heading) + r"\s*$\n(.*?)(?=^[ \t]*##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


# Pull the body of a `> 项目文件夹：\`xxx\`` blockquote at the top of the doc.
def _project_folder(text: str) -> str:
    pattern = re.compile(r"^>\s*项目文件夹[：:]\s*`([^`]+)`", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


# Pull a numeric metric from a markdown table row: `| <label> | <value> | ...`.
def _metric(text: str, label: str) -> int | str:
    pattern = re.compile(r"^\|\s*" + re.escape(label) + r"\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return "unknown"
    raw = match.group(1).strip()
    if raw in {"未知", "未知 / 未采集", "-", ""}:
        return "unknown"
    if raw == "不可见":
        return "hidden"
    # Handle Chinese numbers like "1.2万" → 12000.
    if "万" in raw:
        try:
            return int(float(raw.replace("万", "")) * 10000)
        except ValueError:
            return "unknown"
    # Strip thousands separators and parse.
    try:
        return int(raw.replace(",", ""))
    except ValueError:
        return "unknown"


# Pull a list of matched rules from `## 3. 命中与排除` → `**命中的监控规则**` block.
def _matched_rules(text: str) -> list[dict[str, str]]:
    section = _section(text, "3. 命中与排除")
    pattern = re.compile(r"^-\s*\[([^\]]+)\]\s*(.+?)\s*$", re.MULTILINE)
    return [{"id": m.group(1).strip(), "name": m.group(2).strip()} for m in pattern.finditer(section)]


# --- public entry point -----------------------------------------------------

def parse_handoff(handoff_path: Path) -> dict:
    """Parse a V2 handoff.md into the template package's source schema.

    Missing fields fall back to safe defaults (null / "unknown" / []). Caller
    should treat `v2_video_url` as required and warn if empty.
    """
    if not handoff_path.exists():
        raise FileNotFoundError(f"handoff not found: {handoff_path}")

    text = handoff_path.read_text(encoding="utf-8")
    missing: list[str] = []

    title = _kv(text, "标题")
    if not title:
        missing.append("标题")
    platform = _kv(text, "平台")
    if not platform:
        missing.append("平台")
    video_url = _kv(text, "视频链接")
    if not video_url:
        missing.append("视频链接")

    selection_section = _section(text, "4. 推荐作为对标的原因")
    selection_reason = selection_section.split("\n", 1)[0].strip() if selection_section else ""
    if not selection_reason:
        missing.append("selection_reason")

    manual_section = _section(text, "5. 人工备注")
    manual_note = manual_section if manual_section else None

    rules = _matched_rules(text)
    if not rules:
        missing.append("matched_rules")

    project_folder = _project_folder(text)
    if not project_folder:
        missing.append("project_folder_name")

    return {
        "handoff_version": HANDOFF_VERSION,
        "v2_video_url": video_url or None,
        "v2_metrics": {
            "follower": _metric(text, "作者粉丝量"),
            "like": _metric(text, "点赞"),
            "comment": _metric(text, "评论"),
            "favorite": _metric(text, "收藏"),
            "share": _metric(text, "分享"),
            "recommend": _metric(text, "推荐"),
        },
        "matched_rules": rules,
        "manual_note": manual_note,
        "selection_reason": selection_reason or None,
        "project_folder_name": project_folder or None,
        "platform": platform or None,
        "title": title or None,
        "_missing_fields": missing,
    }


def write_source_packet(run_dir: Path, parsed: dict, mode: str) -> tuple[Path, Path]:
    source_dir = run_dir / "artifacts" / "_source"
    source_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = source_dir / "source_manifest.json"
    brief_path = source_dir / "source_brief.md"

    source_kind = _source_kind(parsed["v2_video_url"])
    evidence_quality = "blocked_needs_local_video" if source_kind == "platform_link" else "needs_ingest"
    manifest = {
        "created_at": utc_now(),
        "mode": mode,
        "source_kind": source_kind,
        "source_ref": parsed["v2_video_url"],
        "source_brief": "artifacts/_source/source_brief.md",
        "source_note": "artifacts/_source/source_note.md",
        "evidence_quality": evidence_quality,
        "video_ingest": None,
        "raw_material_policy": "Do not paste or re-read full raw video/transcript in later stages. S1 reads the concise source_brief and, for video sources, the video_ingest packet.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (source_dir / "source_note.md").write_text(
        f"""# V2 handoff 素材来源说明

- 素材类型：{source_kind}
- 素材位置：{parsed["v2_video_url"]}
- 证据质量：{evidence_quality}

如果这是抖音/小红书等平台链接，必须先下载成本地视频并运行 `slbb-video-ingest`，再进入长剧 S1。
""",
        encoding="utf-8",
    )

    if not brief_path.exists():
        title = parsed.get("title") or parsed.get("project_folder_name") or "未命名对标素材"
        rules = parsed.get("matched_rules") or []
        rules_text = "\n".join(f"- {rule.get('id', '?')} {rule.get('name', '')}".strip() for rule in rules) or "- 无"
        manual_note = parsed.get("manual_note") or "无"
        selection_reason = parsed.get("selection_reason") or "无"
        brief = f"""# 长剧 S1 精简素材说明

> 省 token 规则：S1 优先读取这份 brief。不要把完整视频、长字幕、逐帧分析重复贴进聊天。

## 对标素材定位

- 标题：{title}
- 平台：{parsed.get("platform") or "未知"}
- 链接：{parsed["v2_video_url"]}
- 来源方式：V2 handoff

## 一句话剧情/核心看点

{selection_reason}

## 角色与视觉锚点

- 待人工补充：角色身份、年龄段、脸型发型、服装、气质、关键道具。

## 关键时间点

- 待人工补充：按 `00:00-00:03 发生了什么` 写，最多 12 条。

## 台词/字幕要点

- 待人工补充：只保留影响剧情和情绪的关键台词，最多 10 条。

## 二创方向

{manual_note}

## 命中规则

{rules_text}
"""
        brief_path.write_text(brief, encoding="utf-8")

    return manifest_path, brief_path


def init_run_from_handoff(handoff_path: Path, run_dir: Path, mode: str) -> int:
    """Create run_dir, init state with source populated, write first handoff."""
    parsed = parse_handoff(handoff_path)

    if not parsed["v2_video_url"]:
        print("ERROR: handoff missing 视频链接 (v2_video_url). S1 will block without it.")
        print("Hint: re-export from V2 monitor with a real video link.")
        return 2

    run_dir.mkdir(parents=True, exist_ok=True)
    stages = stages_for_mode(mode)
    for stage_id in [s["id"] for s in stages]:
        (run_dir / "artifacts" / stage_id).mkdir(parents=True, exist_ok=True)
    for support_dir in ("_meta", "_audit", "_handoff", "_source"):
        (run_dir / "artifacts" / support_dir).mkdir(parents=True, exist_ok=True)

    title = parsed["title"] or parsed["project_folder_name"] or "AI长剧工作流"
    state = default_state(title, mode=mode)
    manifest_path, brief_path = write_source_packet(run_dir, parsed, mode)
    parsed["source_kind"] = _source_kind(parsed["v2_video_url"])
    parsed["source_ref"] = parsed["v2_video_url"]
    parsed["source_manifest"] = str(manifest_path.relative_to(run_dir))
    parsed["source_brief"] = str(brief_path.relative_to(run_dir))
    parsed["source_note"] = "artifacts/_source/source_note.md"
    parsed["evidence_quality"] = "blocked_needs_local_video" if parsed["source_kind"] == "platform_link" else "needs_ingest"
    # Replace the empty default source with our parsed values (keep the same shape).
    state["source"] = {k: v for k, v in parsed.items() if not k.startswith("_")}
    state["current_stage"] = "S1"
    save_state(run_dir, state)

    missing = parsed["_missing_fields"]
    note = f"V2 handoff 已导入：{title}，mode={mode}。S1 应优先读取 `artifacts/_source/source_brief.md` 和 video_ingest 证据包，只把 source.v2_video_url 当作证据定位，不要重复吞完整素材。"
    if parsed["source_kind"] == "platform_link":
        note += "\n\n⚠️ 当前 handoff 是平台链接，不能直接进入 S1。请先下载/录屏成本地视频，再运行 slbb-video-source 和 slbb-video-ingest。"
    if missing:
        note += f"\n\n⚠️ 以下字段在 handoff 中缺失（已用默认值占位，可后续人工补全）：{', '.join(missing)}"
    write_handoff(run_dir, stages[0], note, target_segment=None)

    print(f"Created: {run_dir / 'workflow_state.json'}")
    print(f"Created: {run_dir / 'artifacts' / '_handoff' / 'next_step.md'}")
    print(f"Source handoff_version: {HANDOFF_VERSION}")
    print(f"Source v2_video_url: {parsed['v2_video_url']}")
    print(f"Source matched_rules: {len(parsed['matched_rules'])} items")
    print(f"Source brief: {brief_path}")
    if missing:
        print(f"⚠️  Missing fields: {', '.join(missing)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a V2 handoff into a new run directory")
    parser.add_argument("handoff_md", help="Path to V2 handoff.md")
    parser.add_argument("run_dir", help="AI 长剧生成过程文件目录 (will be created if missing)")
    parser.add_argument("--mode", default="long_drama", choices=sorted(MODE_VALUES))
    args = parser.parse_args()

    handoff_path = Path(args.handoff_md).expanduser().resolve()
    run_dir = Path(args.run_dir).expanduser().resolve()
    try:
        return init_run_from_handoff(handoff_path, run_dir, args.mode)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
