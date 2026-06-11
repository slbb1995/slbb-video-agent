---
name: slbb-video-image-prompts
description: AI 短剧/长剧 S2 图片提示词生成。Use when the user has S1 story extraction/replica artifacts, short drama plot text, long drama second-creation descriptions, episode segments, character notes, scene notes, or asks to generate “生图片参考提示词”, “首图提示词”, “人物参考图”, “白底三视图”, “场景图”, “短剧角色定妆照”, “长剧多年龄段角色图”, “短剧场景空镜”, or S2 image prompt pack for the slbb-video workflow.
---

# AI 短剧 S2：图片提示词

## Overview

Use this skill to turn S1 story outputs into image-generation prompts for short-drama or long-drama production.

S2 only handles static image prompts. It does not generate motion/video prompts, call image/video APIs, edit images, or publish content.

## Operating Gates

- 🔴 CHECKPOINT: before generating prompts from a workflow run, verify S1 artifacts exist and contain character visual anchors.
- 🔴 CHECKPOINT: before completing S2, confirm the human can use the prompt pack for image generation.
- 🔴 CHECKPOINT: before S3 reads S2, keep route notes, critical-prop risks, and inferred details in `_meta/S2_prompt_notes.md`, not in `image_prompt_pack.md`.
- 🛑 STOP: if S1 lacks stable character appearance details, route back to S1 or record inferred anchors before writing final prompts.
- 🛑 STOP: if a requested route would create motion/video instructions, stop and route that work to S3.

## Routing

Choose one route from the user request or workflow state:

- `full_pack`: generate character reference, scene reference, and first-frame prompts.
- `character_reference`: generate white-background three-view character prompts.
- `scene_reference`: generate empty-scene reference prompts.
- `first_frame`: generate opening first-frame prompts.

Default to `full_pack` when S2 is called by the workflow and no specific route is requested.

## Workflow

1. Inspect S1 artifacts if a run directory is provided:
   - `artifacts/S1/story_extract.md`
   - `artifacts/S1/source_replica_description.md`
   - `artifacts/S1/second_creation_description.md`
   - `artifacts/S1/story_segments.json`
2. If S1 artifacts are unavailable, use the user-provided plot or episode text and clearly mark that the output is not workflow-verified.
3. Run `scripts/scaffold_s2_run.py <run_dir>` when writing to a workflow run.
4. Read only the needed references:
   - `references/character_reference_prompt.md`
   - `references/scene_reference_prompt.md`
   - `references/first_frame_prompt.md`
   - `references/output_contract.md`
5. Write `artifacts/S2/image_prompt_pack.md`.
   - This primary file must contain only image prompts that can be copied into an image generator or read by S3.
   - Put route choice, inference notes, critical-prop risk, and human-gate notes in `artifacts/_meta/S2_prompt_notes.md`.
6. Run `scripts/validate_s2_outputs.py <run_dir>`.
7. Stop at the human gate. Do not continue to S3 until the user confirms image prompt usability.

## Prompt Rules

- Reuse the validated prompt structures in `references/`.
- Keep character, scene, and first-frame prompts separated.
- Character reference prompts must produce one full-body white-background three-view character sheet per character.
- Each character reference prompt must explicitly say the three views are in one image/canvas/frame: front view, side view, and back view arranged side by side. Do not output a single front portrait, a single-angle full-body photo, or three separate image prompts.
- Character reference prompts must use a `16:9 横向宽画布` by default. Character sheets are reference assets, not final video frames, so this ratio does not change between short-drama and long-drama runs.
- The required three-view standard is a clean reference photo sheet: left-to-right front view, true 90-degree side profile, and back view; head-to-toe full body; same scale and height; neutral upright standing pose; plain white studio background; no crop.
- Scene reference prompts must not contain people, shadows, silhouettes, body parts, or backs.
- First-frame prompts must look like real short-drama screenshots, not posters.
- Scene reference and first-frame prompts must explicitly include the production frame ratio:
  - `short_drama`: `9:16 竖屏`
  - `long_drama`: `16:9 横屏`
- All image prompts must include no text, no watermark, and no logo.
- For critical props such as cash, phone screens, bills, contracts, bank slips, or UI panels, prioritize natural realism over readable fake text. Do not ask for oversized pasted digits or poster-like prop labels unless the user explicitly chooses that tradeoff.
- If a later plot point depends on readable numbers or UI text, record it as a risk note for S3/S4/S5 instead of forcing S2 to generate artificial-looking text.
- Do not invent a stable character look if S1 provides explicit appearance details; use S1 first.
- If S1 lacks appearance details, fill only production-useful details and label them as inferred.
- Do not produce video motion instructions here. Save motion for S3.

## Long-Drama Mode

When `workflow_state.json.mode` is `long_drama`, S2 must treat S1 as a replica/second-creation description package:

- Use `second_creation_description.md` as the production story source.
- Use `source_replica_description.md` only to preserve visual logic and reference structure.
- Generate separate character reference prompts for each meaningful age stage, such as childhood, youth, adult, or elderly versions.
- If multiple age stages belong to the same person, preserve stable facial/temperament continuity while allowing age, costume, posture, and context to change.
- Generate first-frame prompts per target segment when the segment changes age stage, scene, or emotional state.
- Do not collapse all age stages into one generic character prompt.
- Do not generate video movement, shot tables, or platform copy here.

## Required Output

Write one Markdown pack:

```text
artifacts/S2/image_prompt_pack.md
```

It must include:

- Character reference prompts
- Scene reference prompts
- First-frame prompts

It must not include:

- Workflow/V2 principles
- Input source sections
- Route-mode sections
- Risk-note sections
- Human confirmation sections
- Long explanation of why the prompts were designed

Process notes can go to:

```text
artifacts/_meta/S2_prompt_notes.md
```

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| S1 visual anchors are missing | Return to S1 or add clearly labeled inferred anchors in `_meta`. | Do not invent a character look without marking it. |
| User asks for one portrait instead of three-view reference | Generate one image/canvas with front, true side, and back full-body views. | Do not output only a single front portrait. |
| Scene prompt includes people or shadows | Rewrite as an empty scene reference. | Do not leave people, silhouettes, body parts, or backs in scene prompts. |
| Critical prop requires readable text | Record the risk for S3/S4/S5 and prefer natural prop realism. | Do not force oversized fake digits or poster labels. |
| User asks for motion, camera movement, or video generation | Route to S3. | Do not produce video motion instructions in S2. |
| Validator fails on prompt pack | Fix the primary prompt pack before the human gate. | Do not continue to S3 with invalid S2 output. |

## Anti-pattern Blacklist

- Do not put route mode, inference notes, risk notes, or human-gate prose in `image_prompt_pack.md`.
- Do not call image APIs or claim images were generated.
- Do not output separate prompts for front/side/back when the requirement is one canvas containing three views.
- Do not add text, logo, watermark, or poster design into image prompts.
- Do not make first frames look like posters instead of real short-drama screenshots.
- Do not silently override explicit S1 appearance details.

## Commands

Create S2 skeleton:

```bash
python3 "$CODEX_SKILLS_ROOT/slbb-video-image-prompts/scripts/scaffold_s2_run.py" <run_dir>
```

Validate S2 outputs:

```bash
python3 "$CODEX_SKILLS_ROOT/slbb-video-image-prompts/scripts/validate_s2_outputs.py" <run_dir>
```

If `CODEX_SKILLS_ROOT` is not set, replace it with the local skills root.

## Completion Gate

S2 is complete only when `image_prompt_pack.md` exists, validation passes, and the user has confirmed the prompts can be used for image generation. S2 approval is a human decision.
