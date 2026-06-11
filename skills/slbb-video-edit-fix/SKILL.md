---
name: slbb-video-edit-fix
description: AI 短剧/长剧 S6 人工剪辑修正方案，基于 S5 质检结果生成给人工编辑执行的修正清单和返工建议；AI 不剪辑视频、不生成配音、不导出成片。Use when the user asks for “剪辑修正方案”, “人工修正清单”, “长剧段落衔接”, “补镜头建议”, “重生片段建议”, “字幕遮挡方案”, “遮住乱码字幕”, “剪映操作清单”, “视频修正清单”, or S6 edit-fix artifacts in the slbb-video workflow.
---

# AI 短剧 S6：剪辑修正

## Overview

Use this skill to convert S5 QC conclusions into an edit-fix plan and a human execution checklist.

S6 is a planning stage, not a media editing stage. It does not edit, render, dub, generate voiceover, replace audio, or export a finished video. It gives a human editor clear repair instructions, especially for trim notes, simple mask instructions, subtitle/text cover plans, audio problem notes, and upstream regeneration decisions.

For `long_drama` mode, S6 also gives segment-joining decisions: whether to trim, add a transition, regenerate the current segment, request a bridging shot, or route upstream because continuity cannot be repaired in editing.

## Operating Gates

- 🔴 CHECKPOINT: before writing an edit plan, read S5 verdict and only include issues S5 marked edit-safe or explicitly accepted for S6.
- 🔴 CHECKPOINT: before writing S6, state that this stage only creates a human edit-fix plan; it does not edit video or create voiceover.
- 🔴 CHECKPOINT: before moving to S7, require user confirmation of the plan or a user-provided edited file.
- 🛑 STOP: if the issue is `regenerate_required`, route back to S2/S3/S4 instead of creating a fake edit fix.
- 🛑 STOP: if the user asks S6 to cut video, dub voice, synthesize narration, render, or export final media, refuse that action and provide only the manual correction plan.

## Inputs

Prefer workflow artifacts:

```text
artifacts/S4/generation_run_log.md
artifacts/S4/generation_run_log.csv
artifacts/S5/qc_report.md
artifacts/S5/qc_verdict.json
artifacts/S5/rework_suggestions.md
```

Also accept:

- Video file path or platform URL
- Timestamp ranges with unwanted subtitles/text
- Human notes from editor
- Screenshots/frames showing text glitches

## Workflow

1. Create S6 skeleton:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-edit-fix/scripts/scaffold_s6_run.py" <run_dir>
   ```
2. Read S5 artifacts and identify issues that can be fixed by editing.
3. For subtitle/text glitches, follow `references/subtitle_cover_standard.md`.
4. Add each manual fix item:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-edit-fix/scripts/add_edit_fix_item.py" <run_dir> --fix-id fix-001 --type subtitle_cover --timestamp "0:00-0:15" --problem "即梦生成乱码字幕" --action "人工在剪映添加白底遮罩覆盖原字幕，黑体重打正确字幕" --acceptance "人工预览确认原乱码不可见，新字幕清晰可读"
   ```
5. Write or update:
   - `artifacts/S6/edit_fix_plan.md`
   - `artifacts/S6/edit_checklist.md`
   - optional process notes under `artifacts/_audit/S6_edit_log.md`
6. Validate:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-edit-fix/scripts/validate_s6_outputs.py" <run_dir>
   ```
7. Stop at the human gate. Do not continue to S7 until the user confirms the manual edit plan or provides a revised video file.

If `CODEX_SKILLS_ROOT` is not set, replace it with the local skills root.

## Rules

- Do not edit video, generate voiceover, replace audio, render, export, or claim media work was completed.
- Do not claim the video was edited unless the user provides an edited file or confirms the edit was done outside this skill.
- Use white background and black text for subtitle cover by default.
- Use a commercially usable bold sans-serif font; prefer 黑体 / 思源黑体 / Noto Sans CJK style.
- The cover block must fully hide the unwanted original subtitle/text.
- Preserve story meaning. Do not rewrite dialogue unless the user explicitly approves.
- If the issue is not fixable by editing, route back to S2/S3/S4 instead of forcing S6.
- If S5 says the video should be rejected, do not create a publish-ready edit plan; create a rework-only plan.
- S6 output is a plan only. If a user provides an externally edited draft, label the plan review status as human-review-needed until the user confirms.
- Do not use rough white panels, fake UI overlays, or pasted digits to repair plot-critical phone screens, bank balances, cash, bills, contracts, or other core爽点 unless the user explicitly accepts that visual tradeoff.
- S6 can describe how a human should lower bad audio, trim dead time, add simple masks, or request replacement audio. S6 must not generate, mix, dub, or replace audio itself.
- If a local fix looks more fake than the original issue, stop and route back to S2/S3/S4 or mark the defect as accepted/deferred.

## Fix Types

- `subtitle_cover`: cover garbled/generated subtitles or wrong text
- `caption_replace`: replace visible subtitle with correct text
- `trim`: instruct a human editor to remove unusable leading/trailing seconds
- `crop_or_mask`: instruct a human editor to hide edge artifacts or unwanted text
- `audio_note`: record music, sound, narration, or voiceover fix instructions for the human editor
- `rework_only`: not fixable in edit; go back upstream
- `accept_defer`: known defect accepted for the current test, not repaired
- `bridge_shot`: add or request a short bridging shot between long-drama segments
- `segment_regenerate`: current segment should be regenerated before assembly
- `continuity_trim`: instruct a human editor to trim or rearrange segment edges to preserve rhythm and emotion

## Long-Drama Mode

When `workflow_state.json.mode` is `long_drama`, S6 must explicitly decide whether the current segment can connect to adjacent segments:

- Use S5 long-drama continuity findings as the input.
- Keep edit-safe fixes separate from regenerate-required issues.
- If identity, age stage, or story logic is broken, route back to S2/S3/S4 instead of hiding it with a transition.
- If the segment is usable but the join is rough, create a `bridge_shot`, `continuity_trim`, or human audio-transition instruction.
- Do not claim the 2-minute film is assembled unless the user provides the edited file or confirms assembly.

## Required Outputs

```text
artifacts/S6/edit_fix_plan.md
artifacts/S6/edit_checklist.md
```

See `references/output_contract.md`.

Primary S6 outputs should be clean manual editing instructions. Capability limits, rejection logs, and human-gate notes belong in `_audit`, not in the editing plan itself.

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| S5 verdict is reject or regenerate_required | Create a rework-only plan and route upstream. | Do not produce a publish-ready edit checklist. |
| User asks S6 to cut, dub, render, or export video | Refuse media execution and provide a manual edit-fix plan only. | Do not create or modify video/audio files. |
| User asks to fix a broken core prop with overlays | Explain visual tradeoff and require explicit acceptance. | Do not paste fake UI/digits as if it restores original footage. |
| User asks S6 to generate or replace voiceover | Write an `audio_note` for the human editor or route upstream for regeneration. | Do not synthesize voice, mix audio, or claim配音完成. |
| Subtitle cover leaks original text | Expand cover area and recheck timestamps. | Do not accept partially visible garbled text. |
| Editing would look worse than original | Stop, route upstream, or mark accept/defer. | Do not force a local patch. |
| Validator fails | Fix plan/checklist before human gate. | Do not continue to S7 with invalid S6 outputs. |

## Anti-pattern Blacklist

- Do not claim the video was edited without an edited file or user confirmation.
- Do not cut, crop, mask, dub, synthesize voiceover, mix audio, render, export, or attach finished media from S6.
- Do not turn S6 into regeneration, QC, or platform publishing.
- Do not rewrite dialogue meaning while replacing subtitles.
- Do not use rough masks, fake UI, or pasted numbers for plot-critical props unless explicitly accepted.
- Do not put capability limits, draft logs, or human-gate prose in primary edit instructions.
- Do not call any plan, script output, or unreviewed media `final`.

## Completion Gate

S6 is complete only when the manual plan and checklist exist, validation passes, and the user confirms the plan or provides an externally edited video.
