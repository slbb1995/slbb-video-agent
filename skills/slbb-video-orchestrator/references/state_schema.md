# workflow_state.json 状态契约

## 顶层字段

```json
{
  "workflow_name": "ai-video-workflow",
  "version": "0.3",
  "mode": "short_drama",
  "title": "短剧/项目名",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp",
  "current_stage": "S1",
  "source": {
    "handoff_version": null,
    "v2_video_url": null,
    "v2_metrics": {},
    "matched_rules": [],
    "manual_note": null,
    "selection_reason": null,
    "project_folder_name": null,
    "platform": null,
    "title": null,
    "source_kind": null,
    "source_ref": null,
    "source_manifest": null,
    "source_brief": null,
    "source_note": null,
    "evidence_quality": null,
    "video_ingest": null,
    "shot_index": null
  },
  "segment_state": {
    "status": "not_started",
    "segment_ids": [],
    "current_segment": null,
    "completed_segments": [],
    "archived_segments": {},
    "notes": []
  },
  "stages": {
    "S1": {
      "name": "短剧调研与剧情提取",
      "skill": "slbb-video-research-script",
      "status": "pending",
      "gate": "human_confirm_story",
      "gate_status": "pending",
      "required_outputs": ["artifacts/S1/story_extract.md"],
      "notes": []
    }
  }
}
```

## 状态规则

- `current_stage` 必须指向第一个未完成阶段。
- `mode` 必须是 `short_drama` 或 `long_drama`；缺失时按 `short_drama` 兼容旧状态文件。
- `completed` 阶段必须有全部 required outputs。
- `completed` 阶段必须有 `gate_status=confirmed`。
- 后一阶段不能在前一阶段未完成时完成。
- 阶段校验失败时，状态不得进入 `completed`。
- S2 完成后，`segment_state.segment_ids` 必须来自 `artifacts/S1/story_segments.json`。
- S3-S8 只能处理 `segment_state.current_segment` 指向的单个片段。
- S8 完成一个片段后，该片段的 S3-S8 产物归档到 `artifacts/_segments/<segment_id>/`，再进入下一个片段。
- 所有片段完成后，`segment_state.status=complete`，`current_stage=complete`。

## source 字段：V2 handoff / 长剧素材索引入口

如果本 run 是从 V2 监控台（ai-drama-monitor）导出的 `handoff.md` 启动的，`source` 段会由 `from-handoff` 自动填写。

如果本 run 是从长剧本地视频、录屏或字幕启动的，先用 `slbb-video-source` 生成 `artifacts/_source/source_manifest.json` 和 `artifacts/_source/source_brief.md`。本地视频/直链视频必须再用 `slbb-video-ingest` 生成 `artifacts/_audit/video_ingest/`。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `handoff_version` | int | V2 handoff 格式版本，当前为 `1` |
| `v2_video_url` | string | V2 监控台导出的对标视频链接 |
| `v2_metrics` | object | 视频表现指标（`like` / `comment` / `favorite` / `share` / `recommend` / `follower`，值是数字或 `"unknown"` / `"hidden"`） |
| `matched_rules` | array | 命中的监控规则，每项 `{id, name}` |
| `manual_note` | string \| null | 人工备注原文 |
| `selection_reason` | string | V2 推荐作为对标的原因 |
| `project_folder_name` | string | V2 生成的项目文件夹名 slug |
| `platform` | string | 平台显示名（如 `抖音` / `视频号` / `小红书`），来自 V2 markdown 的“平台”字段 |
| `title` | string | 对标视频原始标题（显示用） |
| `source_kind` | string | `local_video` / `platform_link` / `direct_video_url` / `partial_material` |
| `source_ref` | string | 视频链接、本地路径、截图目录、字幕文件或说明文件的位置 |
| `source_manifest` | string | 固定为 `artifacts/_source/source_manifest.json` |
| `source_brief` | string | 固定为 `artifacts/_source/source_brief.md` |
| `source_note` | string | 固定为 `artifacts/_source/source_note.md` |
| `evidence_quality` | string | `needs_ingest` / `blocked_needs_local_video` / `complete` / `partial` |
| `video_ingest` | string | 完成预处理后指向 `artifacts/_audit/video_ingest/ingest_report.md` |
| `shot_index` | string | 完成预处理后指向 `artifacts/_audit/video_ingest/shot_index.json` |

状态规则：

- 如果使用 V2 入口启动，`source.v2_video_url` 必须非空，否则 S1 视为输入不完整并阻塞。
- 手工启动（`bin/slbb-video-init`）的 run，`source` 全部为 `null` / `{}` / `[]`。
- `platform_link` 不能直接进入长剧 S1；必须先下载/录屏成本地视频，或改走 `partial_material` 降级路径。
- `local_video` / `direct_video_url` 进入长剧 S1 前必须存在 `ingest_report.md`、`shot_index.json`、`contact_sheet.jpg`。
- `partial_material` 可以降级进入长剧 S1，但必须保留低置信度人工确认提示。
- 长剧本地素材启动时，`source.source_brief` 必须指向一份已人工补全的精简素材说明；S1 只读这份 brief、manifest 和 video_ingest 证据包，不重复读取完整视频或长字幕。
- `source` 字段参与长剧 S1 前置校验；S1 完成后，下游主要读取 S1 主产物。

## handoff 文件

`artifacts/_handoff/next_step.md` 用于跨对话继续执行，必须包含：

- 当前阶段
- 应使用的 Skill
- 必须生成的产物
- 人工闸门
- 推荐下一条命令
- S3-S8 阶段必须包含当前目标片段
- 来自 V2 入口的 run，推荐命令必须包含 `source.v2_video_url` 引用
