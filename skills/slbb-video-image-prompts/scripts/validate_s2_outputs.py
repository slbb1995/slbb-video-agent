#!/usr/bin/env python3
"""Validate S2 image prompt artifacts for the AI short-drama workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Validators live in slbb-video-<X>/scripts/ but import shared helpers
# (BASE_NOISE_MARKERS, section_text) from slbb-video-orchestrator/scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slbb-video-orchestrator" / "scripts"))

from workflow_lib import BASE_NOISE_MARKERS, section_text


REQUIRED_HEADINGS = [
    "## 人物参考提示词",
    "## 场景图提示词",
    "## 首图提示词",
]

REQUIRED_SIGNALS = [
    "无人物",
    "无文字",
    "无水印",
    "无logo",
]

CHARACTER_REFERENCE_SIGNALS = [
    "白底三视图",
    "正面",
    "侧面",
    "背面",
    "完整全身",
    "并排",
]

ONE_CANVAS_SIGNALS = ["同一张图片", "同一张图", "同一张画布", "同一画面", "one image", "one canvas", "one frame"]
ORDER_SIGNALS = ["从左到右", "左到右", "左中右", "left-to-right"]
SIDE_PROFILE_SIGNALS = ["纯 90 度侧面", "90度侧面", "90-degree side", "true 90-degree side", "标准侧面"]
FULL_BODY_UNCROPPED_SIGNALS = ["头到脚完整", "不裁切", "no crop", "head-to-toe"]
SAME_SCALE_SIGNALS = ["等比例", "同等比例", "same scale", "等高度", "same height"]
NEUTRAL_STANCE_SIGNALS = ["中性直立站姿", "直立站姿", "neutral upright", "standing pose", "自然站姿"]
SINGLE_VIEW_REJECTION_SIGNALS = ["不是单张正面照", "禁止只生成正面人物照", "禁止单张正面照", "不是单视图"]

FIRST_FRAME_SIGNALS = ["短剧截图", "短剧视频的开头首帧画面"]
UNFINISHED_MARKERS = ["TODO", "待填写", "待补充"]
NOISE_MARKERS = BASE_NOISE_MARKERS + [
    "## 路由模式",
    "## 推导与风险备注",
    "风险备注",
]


def fail(errors: list[str]) -> int:
    print("S2 validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    pack = run_dir / "artifacts" / "S2" / "image_prompt_pack.md"
    errors: list[str] = []

    if not pack.exists():
        return fail([f"missing required file: {pack}"])

    text = pack.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"image_prompt_pack.md missing heading: {heading}")
        elif not section_text(text, heading):
            errors.append(f"image_prompt_pack.md empty section: {heading}")

    for signal in REQUIRED_SIGNALS:
        if signal not in text:
            errors.append(f"image_prompt_pack.md missing quality signal: {signal}")

    character_section = section_text(text, "## 人物参考提示词")
    for signal in CHARACTER_REFERENCE_SIGNALS:
        if signal not in character_section:
            errors.append(f"人物参考提示词 missing three-view signal: {signal}")
    if not any(signal in character_section for signal in ONE_CANVAS_SIGNALS):
        errors.append("人物参考提示词 must say the three views are in one image/canvas/frame")
    if not any(signal in character_section for signal in ORDER_SIGNALS):
        errors.append("人物参考提示词 must specify left-to-right front/side/back order")
    if not any(signal in character_section for signal in SIDE_PROFILE_SIGNALS):
        errors.append("人物参考提示词 must specify a true 90-degree side profile")
    if not any(signal in character_section for signal in FULL_BODY_UNCROPPED_SIGNALS):
        errors.append("人物参考提示词 must specify head-to-toe full body with no crop")
    if not any(signal in character_section for signal in SAME_SCALE_SIGNALS):
        errors.append("人物参考提示词 must specify same scale or same height across views")
    if not any(signal in character_section for signal in NEUTRAL_STANCE_SIGNALS):
        errors.append("人物参考提示词 must specify neutral upright standing pose")
    if not any(signal in character_section for signal in SINGLE_VIEW_REJECTION_SIGNALS):
        errors.append("人物参考提示词 must explicitly reject single-front-view output")

    if not any(signal in text for signal in FIRST_FRAME_SIGNALS):
        errors.append("image_prompt_pack.md missing first-frame signal: 短剧截图 or 短剧视频的开头首帧画面")

    for marker in UNFINISHED_MARKERS:
        if marker in text:
            errors.append(f"image_prompt_pack.md contains unfinished marker: {marker}")

    for marker in NOISE_MARKERS:
        if marker in text:
            errors.append(f"image_prompt_pack.md contains process/noise marker: {marker}")

    if errors:
        return fail(errors)

    print("S2 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
