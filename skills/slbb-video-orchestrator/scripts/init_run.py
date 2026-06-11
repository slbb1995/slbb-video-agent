#!/usr/bin/env python3
"""Initialize an AI video workflow process directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from workflow_lib import MODE_VALUES, default_state, save_state, stages_for_mode, write_handoff


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="AI 视频生成过程文件目录")
    parser.add_argument("--title", default="AI视频工作流")
    parser.add_argument(
        "--mode",
        default="short_drama",
        choices=sorted(MODE_VALUES),
        help="Workflow mode: short_drama or long_drama",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing workflow_state.json")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    # Pre-create stage directories so users can drop source notes / partial artifacts in
    # before invoking the corresponding skill.
    stages = stages_for_mode(args.mode)
    for stage_id in [s["id"] for s in stages]:
        (run_dir / "artifacts" / stage_id).mkdir(parents=True, exist_ok=True)
    for support_dir in ("_meta", "_audit", "_handoff", "_source"):
        (run_dir / "artifacts" / support_dir).mkdir(parents=True, exist_ok=True)

    state_file = run_dir / "workflow_state.json"
    if state_file.exists() and not args.overwrite:
        print(f"workflow_state.json already exists: {state_file}")
        return 1

    state = default_state(args.title, mode=args.mode)
    save_state(run_dir, state)
    note = f"新的 AI 视频生成过程文件目录已创建，mode={args.mode}。请从 S1 开始，不要跳阶段。"
    if args.mode == "long_drama":
        note += "\n\n长剧省 token 规则：先用 `slbb-video-source` 判断素材类型；本地视频/直链必须再跑 `slbb-video-ingest` 生成 `artifacts/_audit/video_ingest/`，平台链接必须先下载/录屏成本地视频。S1 只读取 source brief、manifest 和预处理证据包，不直接吞完整视频、录屏或长字幕。"
    handoff = write_handoff(run_dir, stages[0], note)
    print(f"Created: {state_file}")
    print(f"Created: {handoff}")
    print(f"Mode: {args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
