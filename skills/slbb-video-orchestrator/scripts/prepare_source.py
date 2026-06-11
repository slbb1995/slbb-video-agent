#!/usr/bin/env python3
"""Create a source packet and classify long-drama reference material."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from workflow_lib import (
    MODE_VALUES,
    default_state,
    load_state,
    save_state,
    state_path,
    stages_for_mode,
    utc_now,
    write_handoff,
)


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
LEGACY_KIND_MAP = {
    "link": "platform_link",
    "recording": "local_video",
    "screenshots": "partial_material",
    "transcript": "partial_material",
    "notes": "partial_material",
}


SOURCE_BRIEF_TEMPLATE = """# 长剧 S1 精简素材说明

> 省 token 规则：S1 优先读取这份 brief。不要把完整视频、录屏、长字幕、逐帧分析重复贴进聊天。
> 建议总字数控制在 1500-2500 中文字内；30-60 秒视频通常写 6-10 条关键时间点就够。

## 对标素材定位

- 素材类型：{source_kind}
- 素材位置：{source_ref}
- 证据质量：{evidence_quality}
- 预处理证据包：{video_ingest}

## 一句话剧情/核心看点


## 角色与视觉锚点

- 角色 1：
- 角色 2：

## 关键时间点

- 00:00-00:03
- 00:03-00:08
- 00:08-00:15
- 00:15-00:25
- 00:25-00:35
- 00:35-00:42

## 台词/字幕要点

-

## 二创方向

- 默认轻二创：保留冲突结构、人物关系和情绪节奏，替换具体身份、场景和表达，避免照抄原视频。
"""


PLATFORM_DOWNLOAD_GUIDE = """# 平台链接下载提醒

你提供的是抖音 / 小红书 / 快手 / B 站等平台链接，不能直接进入长剧 S1。

请先把视频下载成本地 mp4 文件。

可选第三方工具：
https://sv.bugpk.com/

操作方式：
1. 复制平台视频分享链接。
2. 打开 https://sv.bugpk.com/。
3. 粘贴链接并解析。
4. 下载视频文件。
5. 把下载后的本地视频路径重新交给 Codex。
6. 再运行 `slbb-video-source` 和 `slbb-video-ingest`。

注意：
- 第三方解析网站可能失效、限流或解析失败。
- 如果解析失败，可以改用录屏、平台自带保存、截图+字幕材料。
- 请只处理你有权学习、分析或二创的素材。
- Codex 不直接解析抖音/小红书链接，必须先转换成本地视频文件。
"""


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def host(value: str) -> str:
    return (urlparse(value).netloc or "").lower()


def is_platform_link(value: str) -> bool:
    hostname = host(value)
    return any(hostname == domain or hostname.endswith("." + domain) for domain in PLATFORM_DOMAINS)


def is_direct_video_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and Path(parsed.path).suffix.lower() in VIDEO_SUFFIXES


def classify_source(source_ref: str, requested_kind: str) -> str:
    requested_kind = requested_kind.strip()
    if requested_kind in LEGACY_KIND_MAP:
        return LEGACY_KIND_MAP[requested_kind]
    if requested_kind in {"local_video", "platform_link", "direct_video_url", "partial_material"}:
        return requested_kind

    if is_url(source_ref):
        if is_direct_video_url(source_ref):
            return "direct_video_url"
        if is_platform_link(source_ref):
            return "platform_link"
        return "platform_link"

    suffix = Path(source_ref).suffix.lower()
    if suffix in VIDEO_SUFFIXES:
        return "local_video"
    return "partial_material"


def maybe_file_metadata(source_ref: str) -> dict:
    if is_url(source_ref):
        return {"file_exists": None, "url_host": host(source_ref)}
    path = Path(source_ref).expanduser()
    if not path.exists():
        return {"file_exists": False, "file_suffix": path.suffix}
    stat = path.stat()
    return {
        "file_exists": True,
        "file_name": path.name,
        "file_suffix": path.suffix,
        "file_size_bytes": stat.st_size,
    }


def ensure_run(run_dir: Path, title: str, mode: str) -> dict:
    run_dir.mkdir(parents=True, exist_ok=True)
    for stage_id in [s["id"] for s in stages_for_mode(mode)]:
        (run_dir / "artifacts" / stage_id).mkdir(parents=True, exist_ok=True)
    for support_dir in ("_meta", "_audit", "_handoff", "_source"):
        (run_dir / "artifacts" / support_dir).mkdir(parents=True, exist_ok=True)

    if state_path(run_dir).exists():
        return load_state(run_dir)

    state = default_state(title, mode=mode)
    save_state(run_dir, state)
    return state


def write_source_note(path: Path, source_kind: str, source_ref: str, evidence_quality: str) -> None:
    path.write_text(
        f"""# 素材来源说明

- 素材类型：{source_kind}
- 素材位置：{source_ref}
- 证据质量：{evidence_quality}

本文件是过程说明，不是 S1 主输入。S1 高频输入仍然是 `source_brief.md` 和预处理证据包。
""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and register long-drama source material")
    parser.add_argument("run_dir", help="Workflow run directory")
    parser.add_argument("--title", default="AI长剧工作流")
    parser.add_argument("--mode", default="long_drama", choices=sorted(MODE_VALUES))
    parser.add_argument(
        "--source-kind",
        default="auto",
        choices=[
            "auto",
            "local_video",
            "platform_link",
            "direct_video_url",
            "partial_material",
            "link",
            "recording",
            "screenshots",
            "transcript",
            "notes",
        ],
        help="Source type. Use auto unless you need to force partial_material.",
    )
    parser.add_argument("--source-ref", required=True, help="Video path, platform link, direct URL, or notes path")
    parser.add_argument("--overwrite-brief", action="store_true", help="Overwrite an existing source_brief.md")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    state = ensure_run(run_dir, args.title, args.mode)
    mode = state.get("mode") or args.mode
    source_kind = classify_source(args.source_ref, args.source_kind)
    evidence_quality = "partial" if source_kind == "partial_material" else "needs_ingest"
    if source_kind == "platform_link":
        evidence_quality = "blocked_needs_local_video"

    source_dir = run_dir / "artifacts" / "_source"
    manifest_path = source_dir / "source_manifest.json"
    brief_path = source_dir / "source_brief.md"
    note_path = source_dir / "source_note.md"

    manifest = {
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "mode": mode,
        "source_kind": source_kind,
        "source_ref": args.source_ref,
        "source_brief": "artifacts/_source/source_brief.md",
        "source_note": "artifacts/_source/source_note.md",
        "evidence_quality": evidence_quality,
        "video_ingest": None,
        "raw_material_policy": (
            "Keep raw video/transcript as evidence only. S1 reads the concise source_brief and, "
            "for video sources, the video_ingest packet. Do not paste full raw material into chat."
        ),
        "file_metadata": maybe_file_metadata(args.source_ref),
    }
    if source_kind == "platform_link":
        guide_path = source_dir / "platform_link_download_guide.md"
        guide_path.write_text(PLATFORM_DOWNLOAD_GUIDE, encoding="utf-8")
        manifest["platform_download_guide"] = "artifacts/_source/platform_link_download_guide.md"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.overwrite_brief or not brief_path.exists():
        video_ingest = "运行 slbb-video-ingest 后自动写入" if source_kind in {"local_video", "direct_video_url"} else "不适用"
        brief_path.write_text(
            SOURCE_BRIEF_TEMPLATE.format(
                source_kind=source_kind,
                source_ref=args.source_ref,
                evidence_quality=evidence_quality,
                video_ingest=video_ingest,
            ),
            encoding="utf-8",
        )
    write_source_note(note_path, source_kind, args.source_ref, evidence_quality)

    source = state.setdefault("source", {})
    source["source_kind"] = source_kind
    source["source_ref"] = args.source_ref
    source["source_manifest"] = "artifacts/_source/source_manifest.json"
    source["source_brief"] = "artifacts/_source/source_brief.md"
    source["source_note"] = "artifacts/_source/source_note.md"
    source["evidence_quality"] = evidence_quality
    save_state(run_dir, state)

    stage = stages_for_mode(mode)[0]
    if source_kind == "platform_link":
        note = (
            "已识别为平台链接，不能直接进入长剧 S1。请先用 START_HERE.md 推荐方式把视频下载成本地 mp4，"
            "或提供录屏/截图+字幕材料；下载后重新运行 slbb-video-source 和 slbb-video-ingest。"
        )
    elif source_kind in {"local_video", "direct_video_url"}:
        note = (
            "素材索引已创建。下一步先运行 slbb-video-doctor；环境通过后运行 slbb-video-ingest 生成 "
            "`artifacts/_audit/video_ingest/` 证据包，再补全 `artifacts/_source/source_brief.md`。"
        )
    else:
        note = (
            "已按 partial_material 降级路径登记。S1 可以继续，但必须明确标记低置信度："
            "没有完整视频证据，爆款复刻可信度较低，需要人工确认。"
        )
    handoff = write_handoff(run_dir, stage, note)

    print(f"Source kind: {source_kind}")
    print(f"Evidence quality: {evidence_quality}")
    print(f"Updated source manifest: {manifest_path}")
    print(f"Source brief: {brief_path}")
    print(f"Source note: {note_path}")
    if source_kind == "platform_link":
        print(f"Download guide: {source_dir / 'platform_link_download_guide.md'}")
    print(f"Handoff: {handoff}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
