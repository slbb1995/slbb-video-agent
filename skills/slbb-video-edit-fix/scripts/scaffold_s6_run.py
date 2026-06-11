#!/usr/bin/env python3
"""Create the S6 artifact skeleton for an AI short-drama workflow run."""

from __future__ import annotations

import argparse
from pathlib import Path


PLAN = """# S6 剪辑修正方案

## 修正结论

本阶段只输出给人工编辑执行的修正方案，不剪辑视频、不生成配音、不导出成片。

## 字幕遮挡方案

如存在乱码字幕、错误文字或水印样文字，默认规则：白底黑字，黑体或等价可商用黑体风格字体，遮住原始乱码字幕。

如无字幕遮挡问题，写明：不需要字幕遮挡。

## 其他剪辑修正

只记录人工剪辑、人工配音/音乐处理、补镜头或上游重生建议。

## 不适合剪辑修正的问题

| 问题 | 原因 | 返回环节 | 是否可接受暂不修 |
| --- | --- | --- | --- |
"""

CHECKLIST = """# S6 人工剪辑修正清单

## 基础设置

- 执行者：人工编辑
- S6 只提供修正方案，不剪辑视频、不生成配音、不导出成片。
- 如需字幕遮挡：白底黑字，黑体或等价可商用黑体风格字体，完全遮住原始乱码字幕。

## 修正项清单

## 人工交付检查

- 人工编辑已按每个 fix item 处理。
- 如有字幕遮挡：原乱码字幕不可见，新字幕清晰可读，没有遮住关键人物、动作、道具。
- 如有配音/音乐问题：人工编辑已按 `audio_note` 处理，并完成听感复核。
- 如需上游重生：已明确返回 S2/S3/S4，不进入 S7。

## 进入下一步条件

- 用户确认人工修正方案，或提供人工修正后的视频文件。
- 未确认前不得进入 S7 分发包。
"""

EDIT_LOG = """# S6 过程备注

## 输入来源

## S6 能力边界

- 可做：人工音频处理建议、裁切建议、简单遮挡建议、字幕替换建议、发布前人工剪辑清单。
- 谨慎：手机屏幕、金额、账单、合同、纸币等核心道具的局部修复。
- 不承诺：把失败的核心道具或 UI 修成原生拍摄质感。
- 不执行：AI 不剪辑视频、不生成配音、不替换音频、不导出成片。

## 人工剪辑状态

- 人工修正后视频路径：
- 状态：plan_only / human_confirmed / rejected
- 人工检查证据：抽帧 / contact sheet / 听感备注

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
    s6_dir = run_dir / "artifacts" / "S6"
    audit_dir = run_dir / "artifacts" / "_audit"
    s6_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    created = []
    for name, content in {
        "edit_fix_plan.md": PLAN,
        "edit_checklist.md": CHECKLIST,
    }.items():
        path = s6_dir / name
        if write_if_missing(path, content):
            created.append(str(path))
    edit_log = audit_dir / "S6_edit_log.md"
    if write_if_missing(edit_log, EDIT_LOG):
        created.append(str(edit_log))

    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    else:
        print(f"No files created; S6 skeleton already exists: {s6_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
