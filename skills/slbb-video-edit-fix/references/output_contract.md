# S6 Output Contract

S6 is a workflow node. It is not complete until the manual correction plan and checklist exist and validate.

S6 primary outputs are clean manual editing instructions. S6 does not edit, dub, render, export, or attach finished media. Capability limits, rejection logs, and operator notes belong in `artifacts/_audit/S6_edit_log.md`.

For `long_drama` mode, S6 can also describe segment-joining fixes such as `bridge_shot`, `segment_regenerate`, and `continuity_trim`, while keeping regenerate-required identity or story errors routed upstream.

## Required Directory

```text
<run_dir>/
  artifacts/
    S6/
      edit_fix_plan.md
      edit_checklist.md
    _audit/
      S6_edit_log.md # optional
```

## edit_fix_plan.md

Required headings:

```markdown
# S6 剪辑修正方案

## 修正结论
## 字幕遮挡方案
## 其他剪辑修正
## 不适合剪辑修正的问题
```

## edit_checklist.md

Required headings:

```markdown
# S6 人工剪辑修正清单

## 基础设置
## 修正项清单
## 人工交付检查
## 进入下一步条件
```

## Required Quality Signals

When `subtitle_cover` or `caption_replace` is present, the finished artifacts must include:

- `白底黑字`
- `黑体`
- `可商用`
- `遮住`
- At least one fix item id such as `fix-001`

If no subtitle cover is needed, the `## 字幕遮挡方案` section must explicitly say `不需要字幕遮挡`, then list another manual fix item or route back upstream with `rework_only`.

For audio, voiceover, narration, music, and sound problems, S6 must only output `audio_note` instructions for a human editor or route upstream. It must not produce or claim to produce audio files.

## Clean Output Guard

Primary Markdown outputs must not include:

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
