---
name: slbb-video-qc
description: AI 短剧/长剧 S5 视频质检与问题归因。Use when the user has generated video clips from 即梦, 可灵, or another platform and needs to inspect characters, deformation, action, lighting, expression, camera stability, subtitles/text glitches, story fidelity, long-drama character continuity, platform artifacts, and infer whether problems come from S1 story split/replica description, S2 image prompts, S3 motion prompts, S4 generation settings/platform, or should move to S6 editing. Trigger for “视频质检”, “视频审查”, “长剧连续性质检”, “质检表”, “Gemini质检”, “抽帧检查”, “人物变形”, “动作不合适”, “光线问题”, “字幕乱码”, “反推提示词问题”, or S5 artifacts in the slbb-video workflow.
---

# AI 短剧 S5：视频质检

## Overview

Use this skill to turn a generated video, frame observations, human notes, or vision-model notes into a QC report, machine-readable verdict, and rework suggestions.

S5 does not pick a permanent video-understanding model in the first version. It can use human review, extracted frames, Gemini, or any available vision/video model, but it must record the review method and model used.

## Operating Gates

- 🔴 CHECKPOINT: before QC begins, identify the selected S4 generated video/version or mark `blocked_no_video`.
- 🔴 CHECKPOINT: before sending anything to S6, decide whether each important issue is `edit_safe`, `edit_precise_only`, `regenerate_required`, or `accept_or_defer`.
- 🔴 CHECKPOINT: before completing S5, the user must confirm the verdict: pass to S6, route upstream, or stop.
- 🛑 STOP: if no video/frame/user evidence exists, output `blocked_no_video` instead of guessing.
- 🛑 STOP: if a core prop/story issue would look fake after editing, route back to S2/S3/S4 instead of forcing S6.

## Inputs

Prefer workflow artifacts:

```text
artifacts/S1/story_extract.md
artifacts/S1/source_replica_description.md
artifacts/S1/second_creation_description.md
artifacts/S2/image_prompt_pack.md
artifacts/S3/motion_prompt_pack.md
artifacts/S4/generation_run_log.md
artifacts/S4/generation_run_log.csv
```

Also accept:

- Video file path or URL
- Extracted frame folder
- Human issue notes
- Gemini/vision-model review text
- Selected generation record from S4

## Workflow

1. Create S5 skeleton:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-qc/scripts/scaffold_s5_run.py" <run_dir>
   ```
2. Inspect S4 and identify the selected generated video/version.
3. Review the video using the best available method:
   - Human observation
   - Extracted key frames
   - Gemini or another video-capable model
   - Existing user-provided QC notes
4. Add issues using:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-qc/scripts/add_qc_issue.py" <run_dir> --category character_consistency --severity high --timestamp "0:04-0:06" --observation "人物脸变形" --likely-source-step S2 --recommendation "重做人物参考图并锁定角色"
   ```
5. Write `qc_report.md`, `qc_verdict.json`, and `rework_suggestions.md`.
   - Keep primary S5 files actionable: conclusion, issue evidence, attribution, editability, and rework action.
   - Put review-method details, model notes, long frame observations, and human-gate wording in `artifacts/_audit/S5_review_notes.md` if needed.
6. Validate:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-qc/scripts/validate_s5_outputs.py" <run_dir>
   ```
7. Stop at the human gate. Do not continue to S6 until the user confirms the QC verdict.

If `CODEX_SKILLS_ROOT` is not set, replace it with the local skills root.

## QC Categories

Use `references/qc_standard.md`.

Required checks:

- Character consistency
- Face/body deformation
- Action correctness
- Expression and emotion
- Lighting and color
- Camera stability
- Scene and prop consistency
- Dialogue/lip-sync/story fidelity
- Subtitle/text glitches
- Platform artifacts
- Compliance and safety

For `long_drama` mode, also check:

- Same-person identity continuity across segments and age stages
- Whether age-stage changes are intentional and visually plausible
- Clothing, prop, and scene continuity inside the current story section
- Emotional continuity between the current segment and adjacent segments
- Whether the selected generated clip can be edited into the larger 2-minute story without breaking rhythm

## Attribution Rules

Every issue must be mapped to one likely source:

- `S1`: story split, character relation, scene logic, or episode rhythm problem
- `S1_long_replica`: long-drama source replica, second-creation description, role age-stage, or segment split problem
- `S2`: image prompt, character reference, scene reference, first-frame problem
- `S3`: motion prompt, shot table, action, sound, dialogue, platform prompt problem
- `S4`: platform setting, generation attempt, selected version, upload/reference mismatch
- `S6`: only editing/subtitle/covering/cut can fix it
- `platform`: model artifact that requires regeneration
- `unknown`: not enough evidence; ask for more frames/video

Do not write vague feedback. Use this shape:

```text
问题 -> 证据 -> 可能来源 -> 建议返工环节
```

## S6 Editability Gate

S5 must decide whether each issue is actually suitable for S6. Do not send every problem to editing just because an editing tool exists.

Use one of these labels for important issues:

- `edit_safe`: editing can fix it naturally, e.g. trim, audio level, simple subtitle cover.
- `edit_precise_only`: only careful manual/precision editing may work; rough automatic repair likely looks worse.
- `regenerate_required`: the issue must return to S2/S3/S4, e.g. fake core prop, broken action logic, face/identity failure, unreadable plot-critical UI.
- `accept_or_defer`: visible issue exists but can be accepted for this test because fixing it costs more or makes it worse.

For plot-critical props such as phone payment screens, bank numbers, cash, bills, contracts, and identity documents, S5 must explicitly answer:

- Is this core爽点 still understandable?
- Would S6 repair look more fake than the original?
- Is the minimum acceptable fix audio/trim only?
- Should this go back to generation instead of editing?

## Required Outputs

```text
artifacts/S5/qc_report.md
artifacts/S5/qc_verdict.json
artifacts/S5/rework_suggestions.md
```

See `references/output_contract.md` for schemas.

Primary S5 outputs must not read like a workflow memo. They should answer: usable or not, what is wrong, why it happened, where to return, and whether S6 can safely fix it.

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| No selected video/version | Set verdict to `blocked_no_video` and route back to S4. | Do not QC an unspecified video. |
| Only screenshots/frames are available | Record method and confidence, then limit conclusions to visible evidence. | Do not infer invisible motion or audio. |
| Core prop is fake or unreadable | Decide whether the story still works; if not, route to S2/S3/S4. | Do not send every prop issue to S6. |
| Face/identity/action logic fails | Mark `regenerate_required` unless editing can naturally fix it. | Do not cover conceptual generation failure with edits. |
| Review method/model is unknown | Record `notes_only` or ask for method details. | Do not hide review uncertainty. |
| Validator fails | Fix report, JSON, or rework output before human confirmation. | Do not continue to S6 with invalid verdict data. |

## Anti-pattern Blacklist

- Do not treat S5 as a polishing checklist; it must decide pass/rework/reject/blocked.
- Do not send every issue to S6 because editing tools exist.
- Do not invent timestamps, scores, model names, or evidence references.
- Do not bury review method, confidence, or missing data.
- Do not put long frame notes or human-gate prose in primary S5 outputs.
- Do not mark `pass` when unresolved critical/high issues remain.

## Completion Gate

S5 is complete only when all three required files exist, validation passes, and the user confirms the verdict: pass to S6, route back to S2/S3/S4, or stop.
