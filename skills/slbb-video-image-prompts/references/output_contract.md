# S2 Output Contract

S2 is a workflow node. It is not complete until the image prompt pack exists and validates.

`image_prompt_pack.md` is a clean prompt pack. It is read by humans and by S3, so it must contain only usable image prompts. Workflow principles, route choice, inference/risk notes, and human-gate notes belong in `artifacts/_meta/S2_prompt_notes.md`.

For `long_drama` mode, the same output file is used. The pack must support multiple age-stage character references when S1 identifies one person across childhood, youth, adult, or elderly stages. Keep the prompt pack clean; put continuity explanations or inferred-risk notes in `_meta/S2_prompt_notes.md`.

## Required Directory

```text
<run_dir>/
  artifacts/
    S2/
      image_prompt_pack.md
    _meta/
      S2_prompt_notes.md # optional
```

## image_prompt_pack.md

Must include these headings:

```markdown
# S2 图片提示词包

## 人物参考提示词
## 场景图提示词
## 首图提示词
```

## Required Quality Signals

The finished pack must contain:

- `白底三视图` in the character reference section.
- Character reference prompts must explicitly say each role is generated as one image/canvas/frame containing three full-body side-by-side views: `正面`, `侧面`, and `背面`.
- Character reference prompts must include `16:9 横向宽画布`; character sheets are reference assets and do not follow the final video frame ratio.
- Character reference prompts must match the reference-photo standard: left-to-right front / true side profile / back order, head-to-toe full body, same scale and height, neutral upright standing pose, and no crop.
- Character reference prompts must explicitly reject single-view output, e.g. `不是单张正面照` or `禁止只生成正面人物照`.
- `无人物` in the scene reference section.
- `短剧截图` or `短剧视频的开头首帧画面` in the first-frame section.
- Scene reference and first-frame prompts must include the mode-specific frame ratio:
  - `short_drama`: `9:16 竖屏`
  - `long_drama`: `16:9 横屏`
- `无文字`, `无水印`, and `无logo`.

For long-drama runs, the finished pack should also contain:

- separate prompts for each required age-stage character reference.
- continuity language when multiple age stages are the same person.
- first-frame prompts for segments that change age stage, scene, or emotional state.

The pack must not contain unfinished placeholders such as:

- `TODO`
- `待填写`
- `待补充`

The pack must not contain process/noise markers:

- `Workflow` / `workflow`
- `V2 原则`
- `输入来源`
- `路由模式`
- `推导与风险备注`
- `人工确认项`
- `风险备注`
