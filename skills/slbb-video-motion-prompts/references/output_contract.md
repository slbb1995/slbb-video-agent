# S3 Output Contract

S3 is a workflow node. It is not complete until both required artifacts exist and validate.

S3 primary outputs are clean execution prompts. `motion_prompt_pack.md` is the compact shot/prompt design for downstream use. `platform_copy_ready_prompts.md` is the direct paste surface for 即梦/可灵. Process notes belong in `artifacts/_meta/S3_motion_design_notes.md`.

Default scope: one S3 run covers one target episode/clip only. If the user has not named a target, use the first unfinished segment, usually `001`. Do not include multiple episode/clip prompt blocks in one S3 output unless the user explicitly asked for a batch override.

For `long_drama` mode, S3 still outputs the same two files. The difference is input priority: consume the selected S1 segment's detailed `second_creation_description` and `replica_description`, plus S2 character/scene/first-frame references, instead of rewriting from a short plot sentence. The long-drama reverse-prompt reference belongs in prompt design notes and execution behavior, not as a process explanation inside the primary outputs.

Frame ratio is mode-specific:

- `short_drama`: `9:16 竖屏`
- `long_drama`: `16:9 横屏`

If generated S2 reference sheets or storyboard/contact sheets are provided, use them only to lock visual consistency. Do not reproduce panel labels, grids, numeric overlays, borders, or contact-sheet layouts inside the video prompt.

## Required Directory

```text
<run_dir>/
  artifacts/
    S3/
      motion_prompt_pack.md
      platform_copy_ready_prompts.md
    _meta/
      S3_motion_design_notes.md # optional
```

## motion_prompt_pack.md

Must include:

```markdown
# S3 生视频提示词包

## 目标片段
## 角色锁定
## 场景锁定
## 分镜提示词表
```

The shot table must include this header:

```markdown
| 时间 | 镜头 | 景别 | 运镜 | 画面内容 | 动作 | 微表情 | 台词口型 | 声音 | 时长 | 本镜头作用 | 平台优化标签 |
```

## platform_copy_ready_prompts.md

Must include:

```markdown
# S3 平台复制版提示词

## 目标片段
## 即梦复制版
## 可灵复制版
```

## Required Quality Signals

The finished artifacts must include:

- `角色锁定`
- `场景锁定`
- `台词：`
- `环境：`
- `SFX：`
- `平台优化标签`
- the mode-specific frame ratio: `9:16 竖屏` for `short_drama`, or `16:9 横屏` for `long_drama`
- `即梦`

They must identify exactly one target episode/clip, such as `001` or the user-provided clip ID.

They must not contain unfinished placeholders:

- `TODO`
- `待填写`
- `待补充`

They must not contain process/noise markers:

- `Workflow` / `workflow`
- `V2 原则`
- `输入来源`
- `使用说明`
- `合规与改写备注`
- `时长判断`
- `关键道具与文字风险`
- `人工确认项`
