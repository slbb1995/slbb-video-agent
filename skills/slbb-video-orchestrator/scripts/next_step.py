#!/usr/bin/env python3
"""Write and print the next workflow handoff card."""

from __future__ import annotations

import argparse
from pathlib import Path

from workflow_lib import (
    current_segment_for_stage,
    first_unfinished_stage,
    latest_validator_failure_anywhere,
    load_state,
    long_drama_s1_prerequisite_errors,
    save_state,
    stage_by_id,
    utc_now,
    write_handoff,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="AI 短剧生成过程文件目录")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    state = load_state(run_dir)
    stage = first_unfinished_stage(state)
    if stage is None:
        print("Workflow complete: S1-S8 are all completed.")
        return 0

    current = state["stages"][stage["id"]]
    state["current_stage"] = stage["id"]

    if state.get("mode") == "long_drama" and stage["id"] == "S1":
        prereq_errors = long_drama_s1_prerequisite_errors(run_dir, state)
        if prereq_errors:
            current["status"] = "blocked"
            current.setdefault("notes", []).append(
                {
                    "at": utc_now(),
                    "text": "Long-drama S1 preflight blocked: " + " | ".join(prereq_errors),
                }
            )
            save_state(run_dir, state)
            message = (
                "长剧 S1 暂停：素材证据还没准备好，不能直接进入 slbb-video-long-replica-script。\n\n"
                + "\n".join(f"- {error}" for error in prereq_errors)
                + "\n\n处理方式：\n"
                "- 本地视频/直链：先运行 slbb-video-doctor，再运行 slbb-video-ingest 生成 video_ingest 证据包。\n"
                "- 抖音/小红书/快手/B站链接：先按 START_HERE.md 下载成本地视频，再重新登记和 ingest。\n"
                "- 只有截图/字幕/口述：用 slbb-video-source --source-kind partial_material 登记，并接受低置信度人工确认。"
            )
            handoff = write_handoff(run_dir, stage_by_id(stage["id"], state.get("mode")), message)
            print(f"Blocked stage: {stage['id']} {stage['name']}")
            print(f"Skill: {stage['skill']}")
            print(f"Handoff: {handoff}")
            return 1
        if current["status"] == "blocked":
            current["status"] = "pending"

    if current["status"] == "pending":
        current["status"] = "in_progress"
    target_segment = current_segment_for_stage(state, stage["id"])
    if target_segment:
        current["segment_id"] = target_segment
    save_state(run_dir, state)

    if current["status"] == "ready_for_human":
        message = f"{stage['id']} 已准备好人工确认。确认后使用 advance_stage.py --status completed --human-confirmed。"
    elif current["status"] == "blocked":
        message = f"{stage['id']} 当前 blocked，请先处理 notes 中的问题。"
    elif target_segment:
        message = f"请执行 {stage['id']} 对应 Skill，仅处理目标片段 {target_segment}，不要批量处理其他片段。"
    else:
        message = f"请执行 {stage['id']} 对应 Skill，并生成 required outputs。"

    if state.get("mode") == "long_drama" and stage["id"] == "S1":
        source = state.get("source") or {}
        brief_rel = source.get("source_brief") or "artifacts/_source/source_brief.md"
        manifest_rel = source.get("source_manifest") or "artifacts/_source/source_manifest.json"
        source_kind = source.get("source_kind")
        message += (
            "\n\n长剧省 token 输入规则：S1 只读取 "
            f"`{brief_rel}`、`{manifest_rel}`"
        )
        if source_kind in {"local_video", "direct_video_url"}:
            message += " 和 `artifacts/_audit/video_ingest/` 证据包"
        message += "。不要把完整视频、录屏、长字幕或逐帧分析重新贴进聊天；如果 brief 为空，先补 brief 再跑 S1。"
        if source_kind == "partial_material":
            message += (
                "\n\n⚠️ 当前是 partial_material 降级路径：S1 必须明确写出“当前输入不是完整视频，"
                "只能做低置信度复刻分析；如需更高质量，请补充本地视频文件或录屏文件”。"
            )

    # If a previous validator run failed for any stage, surface it in
    # the handoff so the operator sees it before invoking the next skill.
    failure_anywhere = latest_validator_failure_anywhere(state)
    if failure_anywhere:
        failed_stage_id, failure_text = failure_anywhere
        message += f"\n\n⚠️ 最近一次 validator 失败（{failed_stage_id}）：\n" + failure_text

    # If this run was imported from a V2 handoff, add source context so the
    # next operator (or skill) sees what kind of benchmark was wired in.
    source = state.get("source") or {}
    if source.get("v2_video_url"):
        v2_lines = [
            "\n\n📦 V2 handoff 来源：",
            f"- 对标视频：{source['v2_video_url']}",
        ]
        if source.get("platform"):
            v2_lines.append(f"- 平台：{source['platform']}")
        if source.get("title"):
            v2_lines.append(f"- 标题：{source['title']}")
        rules = source.get("matched_rules") or []
        if rules:
            v2_lines.append(
                "- 命中规则：" + ", ".join(f"{r.get('id', '?')} {r.get('name', '')}".strip() for r in rules)
            )
        if source.get("manual_note"):
            v2_lines.append(f"- 人工备注：{source['manual_note']}")
        message += "\n".join(v2_lines)

    handoff = write_handoff(run_dir, stage_by_id(stage["id"], state.get("mode")), message, target_segment=target_segment)
    print(f"Next stage: {stage['id']} {stage['name']}")
    print(f"Skill: {stage['skill']}")
    print(f"Handoff: {handoff}")
    if failure_anywhere:
        print(f"Validator failure (from stage.notes, {failure_anywhere[0]}) surfaced in handoff.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
