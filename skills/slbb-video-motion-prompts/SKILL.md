---
name: slbb-video-motion-prompts
description: AI 短剧/长剧 S3 生视频提示词生成，把 S1 剧情分集或长剧复刻/二创片段描述，以及 S2 图片提示词/首帧/角色/场景参考，转换成即梦或可灵可复制的视频生成提示词。Use when the user asks for “生视频提示词”, “剧情生视频提示词”, “长剧反推提示词”, “即梦视频 prompt”, “可灵图生视频提示词”, “短剧镜头表”, “15秒短剧分镜”, “把剧情转成视频提示词”, or S3 motion prompt artifacts for the slbb-video workflow.
---

# AI 短剧 S3：生视频提示词

## Overview

Use this skill to convert approved story segments and image references into copy-ready video generation prompts for short-drama or long-drama tools such as 即梦 or 可灵.

S3 only produces motion/video prompts and platform-copy files. It does not call video APIs, upload images, select generated videos, or perform QC.

S3's default scope is exactly one target episode/clip. After S2 is approved, start with the first unfinished segment, usually `001`, and produce only that segment's video prompts. Do not generate prompts for every episode/clip in `story_segments.json` unless the user explicitly asks for a batch override.

## Operating Gates

- 🔴 CHECKPOINT: before writing any prompt, lock exactly one target episode/clip unless the user gives an explicit batch scope.
- 🔴 CHECKPOINT: before completing S3, preserve original dialogue order and confirm the prompt pack is ready for manual generation.
- 🔴 CHECKPOINT: before using readable text/phone UI/bank screens as a plot carrier, record the risk in `_meta/S3_motion_design_notes.md`.
- 🛑 STOP: if the user asks S3 to generate videos or choose the best generated version, route to S4/S5 instead.
- 🛑 STOP: if a 15-second prompt only repeats reaction shots, shorten or restructure before validation.

## Inputs

Prefer workflow artifacts:

```text
artifacts/S1/story_extract.md
artifacts/S1/source_replica_description.md
artifacts/S1/second_creation_description.md
artifacts/S1/story_segments.json
artifacts/S2/image_prompt_pack.md
```

If these are unavailable, use user-provided plot, image notes, role cards, scene cards, first frames, generated S2 reference sheets, storyboard/contact sheets, or target platform details, and clearly mark the output as not workflow-verified.

## Workflow

1. Inspect S1 and S2 artifacts if a run directory is provided.
2. Select one target episode/clip before writing anything:
   - Prefer the episode/clip named by the user or `_handoff/next_step.md`.
   - If no target is named, choose the first unfinished segment from `artifacts/S1/story_segments.json`, usually `001`.
   - Use S2's full character and scene prompt pack only as a reference library; copy only the references needed by the target episode/clip.
3. Decide target duration before writing shots. Do not default to 15 seconds without checking the episode information density.
4. Confirm target platform, duration, aspect ratio, and language. Defaults:
   - platform: 即梦
   - duration: choose from 5s / 10s / 10-12s / 15s based on the duration decision rules below
   - aspect ratio: `short_drama` uses `9:16 竖屏`; `long_drama` uses `16:9 横屏`; user override wins
   - style: 写实、电影质感、真实人物比例、浅景深、轻微手持、真实生活光影
   - mouth language: 中文
5. Run `scripts/scaffold_s3_run.py <run_dir>` when writing to a workflow run.
6. Read:
   - `references/motion_prompt_12_steps.md`
   - `references/long_drama_reverse_prompt.md` when `workflow_state.json.mode` is `long_drama`
   - `references/output_contract.md`
7. Write:
   - `artifacts/S3/motion_prompt_pack.md`
   - `artifacts/S3/platform_copy_ready_prompts.md`
   - optional process notes under `artifacts/_meta/S3_motion_design_notes.md`
8. Run `scripts/validate_s3_outputs.py <run_dir>`.
9. Stop at the human gate. Do not continue to S4 until the user confirms the prompts are ready for manual generation.

## Duration Decision Rules

Before writing the shot table, answer these questions internally or in `artifacts/_meta/S3_motion_design_notes.md`, not in the clean platform-copy prompt:

- How many effective information beats does this episode have?
- Is it a single visual hook, a small reversal, or a reversal plus next-episode hook?
- Does every 3 seconds add new information?
- If 3 seconds are removed, does the story lose a necessary beat?
- Does the ending need a new hook or only a reaction?

Use these defaults:

- `5s`: one visual hook only; no full story closure.
- `10s`: one complete mini-reversal with 2-3 core shots.
- `10-12s`: short-drama first-episode hook with humiliation, proof, reaction, and a next hook.
- `15s`: only when there are at least two effective reversals, or one reversal plus a new relationship/task setup.

If the episode has one core爽点, do not stretch it to 15s by repeating reaction shots or phone-confirmation shots.

## Non-Negotiable Rules

- Preserve user-provided original dialogue exactly. Do not rewrite, omit, merge, reorder, or change speakers.
- If original dialogue is long, add shots or split the same sentence across continuous shots while preserving order.
- If original dialogue is risky, keep the original in the main table and add safety alternatives in notes; do not silently replace it.
- If no dialogue exists, write `台词：无`; optional lines must be labeled as optional.
- Convert abstract emotions into body action, micro-expression, camera movement, sound, and environment changes.
- Every shot must include time, shot number, shot size, camera movement, visual content, action, micro-expression, lip-sync dialogue, sound, duration, shot purpose, and platform optimization tags.
- Every shot must have sound in this format: `台词：...；环境：...；SFX：...`.
- Do not use split-screen, grids, numeric overlays, decorative watermarks, meaningless empty shots, random face changes, or random costume changes.
- If the user provides a storyboard/contact sheet with panel numbers or grid borders, treat those numbers and borders as reference IDs only. Do not reproduce panel labels, grids, borders, or contact-sheet layout in the video prompt.
- Do not rely on platform-generated readable phone UI, bank screens, bills, contracts, or long text as the only way viewers understand the plot. If readable text is necessary, keep it short, record the risk, and make character action/reaction carry the story.
- For key money props, prefer natural prop realism and clear action over fake-looking oversized digits.
- Do not turn all S1 episodes/clips into prompts in one S3 run. One S3 run means one target episode/clip, unless the user explicitly overrides with a batch scope.
- Treat platform/API execution as S4, not S3.

## Long-Drama Mode

When `workflow_state.json.mode` is `long_drama`, S3 must consume the detailed S1 replica/second-creation descriptions instead of a compressed plot sentence:

- Prefer `story_segments.json` episode fields `second_creation_description`, `replica_description`, `source_time_range`, and `duration_seconds`.
- Use `second_creation_description.md` as the production truth source.
- Use `source_replica_description.md` only to preserve reference visual structure.
- Read `references/long_drama_reverse_prompt.md` and follow its emphasis on detailed image, action, expression, dialogue, camera, light, and atmosphere.
- Generate prompts for exactly one target segment unless the user gives an explicit batch scope.
- Preserve the chosen character age stage and S2 character reference for that segment.
- Use `16:9 横屏` by default unless the user explicitly requests another final frame ratio.
- If S2 generated images are provided, use the character/scene reference sheet to lock appearance and environment, and use the target storyboard panel only as a visual reference for that segment.
- For image-to-video execution, require one clean first-frame image for the selected segment. Do not ask the user to feed a full contact sheet into the video tool unless the tool explicitly supports reference contact sheets.
- Do not create or alter S1 replica descriptions here.

## Required Output

`motion_prompt_pack.md` must include:

- Target episode/clip ID and title
- Character lock
- Scene lock
- Shot table

`platform_copy_ready_prompts.md` must include only copy-ready prompts for the selected episode/clip, grouped by platform, ready for manual paste into 即梦/可灵.

Primary S3 files must not include:

- Workflow/V2 principles
- Input source sections
- Usage instructions
- Compliance notes
- Duration-analysis notes
- Critical-prop risk analysis
- Human confirmation sections

Put those notes in:

```text
artifacts/_meta/S3_motion_design_notes.md
```

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| Target episode/clip is not specified | Use the first unfinished segment, usually `001`, and state that target in both outputs. | Do not generate all segments by default. |
| User requests batch generation | Require an explicit target range and label it as a batch override. | Do not silently process every episode. |
| Original dialogue is long | Split across continuous shots while preserving words and speaker order. | Do not summarize or rewrite dialogue. |
| Plot depends on readable UI/text | Shift understanding to action/reaction and record text risk in `_meta`. | Do not trust platform-generated readable UI as the only story proof. |
| Duration exceeds information density | Reduce to 5s/10s/10-12s according to the duration rules. | Do not stretch to 15s with filler reactions. |
| S3 validator fails | Fix prompt structure before human approval. | Do not continue to S4 with invalid prompt files. |

## Anti-pattern Blacklist

- Do not call video APIs, upload assets, or claim generation happened.
- Do not select generated videos or perform QC in S3.
- Do not rewrite, omit, merge, reorder, or change speakers for original dialogue.
- Do not use split-screen, grids, decorative watermarks, random face/costume changes, or empty filler shots.
- Do not reproduce S2 storyboard panel numbers, grid borders, labels, or contact-sheet layouts in video prompts.
- Do not put duration analysis, risk notes, source notes, or human-gate prose into primary S3 outputs.
- Do not include more than one target episode/clip unless the user explicitly gave a batch scope.

## Commands

Create S3 skeleton:

```bash
python3 "$CODEX_SKILLS_ROOT/slbb-video-motion-prompts/scripts/scaffold_s3_run.py" <run_dir>
```

Validate S3 outputs:

```bash
python3 "$CODEX_SKILLS_ROOT/slbb-video-motion-prompts/scripts/validate_s3_outputs.py" <run_dir>
```

If `CODEX_SKILLS_ROOT` is not set, replace it with the local skills root.

## Completion Gate

S3 is complete only when both required files exist for the selected episode/clip, validation passes, and the user has confirmed the prompts can be used for manual generation. S3 approval is a human decision.
