# First-Frame Prompt

Source: whiteboard prompt registry nodes `z3:65` and `z3:67`.

Use this route when the user needs a short-drama opening frame or a first image for video generation.

## Input Form

```text
输入：首帧画面描述

请填写首帧画面信息，不用写完整剧情，只写画面：

1. 场景：
2. 人物：
3. 人物站位：
4. 表情/情绪：
5. 动作前状态：
6. 镜头方式：
7. 画幅比例：

选填：
8. 时间/光线：
9. 服装/年代：
10. 关键道具：
11. 画面气质：
```

## Prompt Template

```text
请生成一张短剧视频的开头首帧画面，画幅比例为{画幅比例}，不要生成海报感，不要字幕，不要水印，不要logo，不要拼贴，不要多余人物。画面要像真实短剧截图，重点固定人物站位、场景背景、空间关系和镜头视角，停在动作发生前一刻，静中有势。

场景：{场景}
人物：{人物}
人物站位：{人物站位}
表情/情绪：{表情/情绪}
动作前状态：{动作前状态}
镜头方式：{镜头方式}
画幅比例：{画幅比例}
时间/光线：{时间/光线}
服装/年代：{服装/年代}
关键道具：{关键道具}
画面气质：{画面气质}

要求：影视写实风，人物关系清楚，主体明确，背景稳定，构图自然，符合短剧开场第一帧。
```

## Output Rules

- Produce one prompt per key episode or user-selected scene.
- The first frame should stop before the action peaks.
- Keep it image-only; do not include video movement instructions.
- Include the correct mode ratio in every first-frame prompt: short_drama uses `9:16 竖屏`; long_drama uses `16:9 横屏`.
- Always include no subtitles, no watermark, no logo, and no poster style.
