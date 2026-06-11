# Workflow Map

```text
S0  长剧视频来源与预处理（仅 long_drama）
    commands:
    - slbb-video-doctor
    - slbb-video-source
    - slbb-video-ingest
    outputs:
    - artifacts/_source/source_manifest.json
    - artifacts/_source/source_brief.md
    - artifacts/_audit/video_ingest/ingest_report.md
    - artifacts/_audit/video_ingest/shot_index.json
    - artifacts/_audit/video_ingest/contact_sheet.jpg

S1  调研与剧情提取
    outputs:
    - artifacts/S1/story_extract.md
    - artifacts/S1/story_segments.json
    - artifacts/_meta/S1_segmentation_decision.md

S2  图片提示词
    outputs:
    - artifacts/S2/image_prompt_pack.md

S2 完成后：
    workflow_state.json.segment_state.current_segment = 第一个未完成片段

片段循环：
    S3  生视频提示词
    S4  视频生成记录
    S5  视频质检
    S6  剪辑修正
    S7  分发包
    S8  发布后复盘

一个片段 S8 完成后：
    artifacts/S3-S8 -> artifacts/_segments/<segment_id>/
    current_segment -> 下一个未完成片段
    current_stage -> S3
```

`S0` 不是 S1-S8 阶段状态的一部分。它只负责让长剧 S1 拿到低 token 证据包，避免直接吞完整视频或平台链接。

## 状态真相源

```text
workflow_state.json
```

## 下一步交接卡

```text
artifacts/_handoff/next_step.md
```
