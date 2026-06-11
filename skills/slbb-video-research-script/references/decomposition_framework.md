# Standard Decomposition Framework

Source: Feishu wiki document titled `拆解剧情标准化框架`, fetched on 2026-05-23.

Use this when the user provides raw plot text or an already researched drama and needs S1 story extraction and segmentation.

## Character Research

| 字段 | 说明 | 输出要求 |
| --- | --- | --- |
| 原角色名称 | 短剧中角色原名，用于调研 | 保留原名 |
| 角色类型 | 主角/配角/群像 | 明确主次 |
| 性别 | 男/女/未知 | 不确定就写未知 |
| 年龄段/身份 | 大致年龄或职业身份 | 必须服务视觉生成 |
| 性格特点 | 核心性格标签 | 避免抽象，写可表演特征 |
| 穿着/喜好 | 常穿服饰、风格偏好 | 服务后续角色参考图 |
| 行为/习惯 | 典型行为动作 | 写动作、表情、口头禅 |
| 心理活动 | 心情、想法 | 写当前驱动力 |
| 出现频率/重要性 | 高/中/低或主线/配角/群像 | 标明重要程度 |
| 角色目标/动机 | 人物行为背后的心理动机 | 写欲望和冲突 |
| 情绪曲线 | 角色在剧情中情绪变化 | 用箭头连接 |
| 角色关系 | 与其他角色关系 | 写利益、感情、冲突 |

## Main Plot Overview

Rules:

- Divide the story by complete narrative movement. Use 起承转合 when suitable.
- Every phase must include overview, core conflict, emotional turn, major event, rhythm, and reproducible visual image.
- Phase count can vary by story length.
- Keep logic continuous so S2/S3 can convert the output into image and video prompts.

| 阶段 | 概述 | 核心冲突 | 爽点/转折 | 重大事件 | 节奏 | 亮点/可复刻画面 |
| --- | --- | --- | --- | --- | --- | --- |
| 起 |  |  |  |  |  |  |
| 承 |  |  |  |  |  |  |
| 转 |  |  |  |  |  |  |
| 合 |  |  |  |  |  |  |

## One-Sentence Summary

```text
一句话简介：
```

The sentence should include role contrast, conflict, emotional hook, and suspense.

## Dynamic 15-Second Segmentation

Before writing any 15-second episode, decide the segment count from source coverage. Do not choose a fixed count first.

Write the decision to `artifacts/_meta/S1_segmentation_decision.md` with:

- `source_type`: researched / provided / inferred.
- `original_episode_count`: known source episode count, if available.
- `collected_source_count`: number of usable collected source items.
- `material_types`: full transcript, episode synopsis, official synopsis, platform clips, user notes, search snippets, etc.
- `coverage_level`: high / medium / low.
- `target_segment_count`: exact number of compressed 15-second units.
- `decision_basis`: why this count fits the drama.
- `boundary`: full-series reconstruction, compressed adaptation, sample-only inferred segmentation, or blocked.

Flexible judgment rules:

- If full episode-level story coverage exists, compress by story arcs and effective hooks, not by a fixed ratio.
- If only official synopsis and scattered clips exist, output a sample/inferred segmentation and say so in `_meta`; do not claim it is full-series coverage.
- For a long short drama such as 40-80 source episodes, the final 15-second unit count may plausibly be 12, 18, 24, or more depending on plot density, but the number must come from the source audit.
- A segment exists only when it can carry a clear hook, conflict escalation, and ending hook. Do not add filler segments to hit a target count.
- If source materials show more arcs than the chosen count can hold, increase the count or mark the compression as a sample.
- If source coverage is too thin to justify the count, block for more source material instead of inventing a full season.

Rules:

1. Each short video episode is 15 seconds.
2. Opening 2 seconds must contain a visual hook or strong action.
3. Middle 5-10 seconds must contain a second conflict or unexpected escalation.
4. Ending 3 seconds must contain a suspense hook.
5. Episodes are dynamic; do not force a fixed count.
6. Each episode must include scene, people, psychology, action, dialogue, props, environment, and audio-visual rhythm.
7. Use replacement character names in episodes. Keep original names only in research.
8. If the last episode is shorter in story content, still write a complete 15-second dramatic unit.

Episode template:

```markdown
分集编号：
分集名称：

场景：
- 类型：
- 具体位置：
- 时间/光线：
- 环境元素：

人物：
- 角色名称（替换名称）：
- 心理活动：
- 穿着：
- 行为动作：

重点物料：

剧情（完整文字化叙述）：
- 开头2秒抓眼球：
- 中间5-10秒二次爆点：
- 结尾3秒钩子：

爆点：
- 开头：
- 中间：

钩子：
```

## Rewrite And Copyright Risk Notes

Add a section that separates:

- Directly sourced plot facts.
- Inferred or reconstructed details.
- Original rewritten details.
- Lines or scenes that are too close to the source and should be rewritten before downstream prompting.
