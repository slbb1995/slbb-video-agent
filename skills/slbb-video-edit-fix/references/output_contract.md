# S6 输出契约

S6 是工作流节点。只有人工修正方案和检查清单都存在并验证通过，S6 才算完成。

S6 主输出是干净的人工剪辑说明。S6 不剪辑、不配音、不渲染、不导出、不附加成片媒体。能力边界、拒绝记录和操作者备注放到 `artifacts/_audit/S6_edit_log.md`。

在 `long_drama` 模式下，S6 也可以描述片段衔接修复，例如 `bridge_shot`、`segment_regenerate` 和 `continuity_trim`，但必须把身份或故事错误这类必须重生成的问题回到上游。

## 必需目录

```text
<run_dir>/
  artifacts/
    S6/
      edit_fix_plan.md
      edit_checklist.md
    _audit/
      S6_edit_log.md # 可选
```

## edit_fix_plan.md

必需标题：

```markdown
# S6 剪辑修正方案

## 修正结论
## 字幕遮挡方案
## 其他剪辑修正
## 不适合剪辑修正的问题
```

## edit_checklist.md

必需标题：

```markdown
# S6 人工剪辑修正清单

## 基础设置
## 修正项清单
## 人工交付检查
## 进入下一步条件
```

## 必需质量信号

当存在 `subtitle_cover` 或 `caption_replace` 时，最终产物必须包含：

- `白底黑字`
- `黑体`
- `可商用`
- `遮住`
- 至少一个修复项 ID，例如 `fix-001`

如果不需要字幕遮挡，`## 字幕遮挡方案` 章节必须明确写 `不需要字幕遮挡`，然后列出另一个人工修复项，或用 `rework_only` 回到上游。

对于音频、旁白、配音、音乐和声音问题，S6 只能输出给人工剪辑师的 `audio_note` 指令，或回到上游。它不得生成或声称生成音频文件。

## 干净输出保护

主 Markdown 输出不得包含：

- `Workflow` / `workflow`
- `V2 原则`
- `输入来源`
- `S6 能力边界`
- `人工确认项`
- `不能自动进入下一步`
- `自动剪辑产物路径`
- `draft_auto_edit`
- `已剪辑完成`
- `已配音完成`
- `我已完成剪辑`
- `我已完成配音`
