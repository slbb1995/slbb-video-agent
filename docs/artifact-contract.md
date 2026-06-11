# Artifact Contract

## 主产物

主产物是下一阶段会直接读取或人工执行会直接使用的文件。

主产物不要写：

- workflow 原则。
- 版本策略。
- 输入来源长说明。
- 风险推导过程。
- 面向 AI Agent 的下一步话术。
- 人工确认话术。

## 过程信息位置

```text
artifacts/_meta/
artifacts/_audit/
artifacts/_handoff/
```

长剧视频预处理证据放在：

```text
artifacts/_source/source_manifest.json
artifacts/_source/source_brief.md
artifacts/_source/source_note.md
artifacts/_audit/video_ingest/
```

这些文件是 S1 前置证据，不是 S1-S7 主产物。S1 主产物仍然写入 `artifacts/S1/` 和 `artifacts/_meta/S1_replica_notes.md`。

## 片段归档

S2 后，活跃工作区只保存当前片段的 S3-S8 文件。

当前片段 S8 完成后，总控会归档：

```text
artifacts/_segments/<segment_id>/S3/
artifacts/_segments/<segment_id>/S4/
artifacts/_segments/<segment_id>/S5/
artifacts/_segments/<segment_id>/S6/
artifacts/_segments/<segment_id>/S7/
artifacts/_segments/<segment_id>/S8/
```

归档后，S3-S8 活跃目录会留给下一个片段重新生成。
