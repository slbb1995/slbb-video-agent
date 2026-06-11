---
name: slbb-video-edit-fix
description: AI 短剧/长剧 S6 剪辑修正方案，基于 S5 质检结果生成可人工执行的剪辑修正清单，重点处理即梦/可灵生成视频中不稳定出现的字幕、乱码字幕、错误文字、水印样文字，也支持长剧补镜头、重生片段、段落衔接和节奏修正。Use when the user asks for “剪辑修正”, “长剧段落衔接”, “补镜头”, “重生片段”, “字幕遮挡”, “遮住乱码字幕”, “白底黑字”, “黑体”, “剪映遮字幕”, “视频修正清单”, or S6 edit-fix artifacts in the slbb-video workflow.
---

# AI 短剧 S6：剪辑修正

## Overview

Use this skill to convert S5 QC conclusions into an edit-fix plan and an execution checklist.

S6 first version is intentionally narrow. It does not promise publish-ready automatic video editing. It gives a human editor clear steps, especially for audio, trim, simple masks, and covering unwanted AI-generated subtitles/text.

For `long_drama` mode, S6 also gives segment-joining decisions: whether to trim, add a transition, regenerate the current segment, request a bridging shot, or route upstream because continuity cannot be repaired in editing.

## Operating Gates

- 🔴 CHECKPOINT: before writing an edit plan, read S5 verdict and only include issues S5 marked edit-safe or explicitly accepted for S6.
- 🔴 CHECKPOINT: before calling any edit result final, require a user-provided edited file or explicit human confirmation.
- 🔴 CHECKPOINT: before moving to S7, confirm the human editing plan or edited video.
- 🛑 STOP: if the issue is `regenerate_required`, route back to S2/S3/S4 instead of creating a fake edit fix.
- 🛑 STOP: if an automatic/script-generated edit exists, label it `draft` until human review.

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
4. Add each fix item:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-edit-fix/scripts/add_edit_fix_item.py" <run_dir> --fix-id fix-001 --type subtitle_cover --timestamp "0:00-0:15" --problem "即梦生成乱码字幕" --action "白底遮罩覆盖原字幕，黑体重打正确字幕" --acceptance "原乱码不可见，新字幕清晰可读"
   ```
5. Write or update:
   - `artifacts/S6/edit_fix_plan.md`
   - `artifacts/S6/edit_checklist.md`
   - optional process notes under `artifacts/_audit/S6_edit_log.md`
6. Validate:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-edit-fix/scripts/validate_s6_outputs.py" <run_dir>
   ```
7. Stop at the human gate. Do not continue to S7 until the user confirms the edit plan.

If `CODEX_SKILLS_ROOT` is not set, replace it with the local skills root.

## Rules

- Do not claim the video was edited unless the user provides an edited file or confirms the edit.
- Use white background and black text for subtitle cover by default.
- Use a commercially usable bold sans-serif font; prefer 黑体 / 思源黑体 / Noto Sans CJK style.
- The cover block must fully hide the unwanted original subtitle/text.
- Preserve story meaning. Do not rewrite dialogue unless the user explicitly approves.
- If the issue is not fixable by editing, route back to S2/S3/S4 instead of forcing S6.
- If S5 says the video should be rejected, do not create a publish-ready edit plan; create a rework-only plan.
- Automatic or script-generated edits must be labeled `draft` until a human reviews them. Do not name an auto edit `final`.
- Do not use rough white panels, fake UI overlays, or pasted digits to repair plot-critical phone screens, bank balances, cash, bills, contracts, or other core爽点 unless the user explicitly accepts that visual tradeoff.
- S6 can remove/attenuate bad audio, trim dead time, add simple masks, and create human editing checklists. S6 should not claim it can make a broken core prop look like original footage.
- If a local fix looks more fake than the original issue, stop and route back to S2/S3/S4 or mark the defect as accepted/deferred.

## Fix Types

- `subtitle_cover`: cover garbled/generated subtitles or wrong text
- `caption_replace`: replace visible subtitle with correct text
- `trim`: remove unusable leading/trailing seconds
- `crop_or_mask`: hide edge artifacts or unwanted text
- `audio_note`: record sound/music fix for the human editor
- `rework_only`: not fixable in edit; go back upstream
- `draft_auto_edit`: automatic edit output for review only, not final
- `accept_defer`: known defect accepted for the current test, not repaired
- `bridge_shot`: add or request a short bridging shot between long-drama segments
- `segment_regenerate`: current segment should be regenerated before assembly
- `continuity_trim`: trim or rearrange segment edges to preserve rhythm and emotion

## Long-Drama Mode

When `workflow_state.json.mode` is `long_drama`, S6 must explicitly decide whether the current segment can connect to adjacent segments:

- Use S5 long-drama continuity findings as the input.
- Keep edit-safe fixes separate from regenerate-required issues.
- If identity, age stage, or story logic is broken, route back to S2/S3/S4 instead of hiding it with a transition.
- If the segment is usable but the join is rough, create a `bridge_shot`, `continuity_trim`, or audio-transition instruction.
- Do not claim the 2-minute film is assembled unless the user provides the edited file or confirms assembly.

## Required Outputs

```text
artifacts/S6/edit_fix_plan.md
artifacts/S6/edit_checklist.md
```

See `references/output_contract.md`.

Primary S6 outputs should be clean editing instructions. Capability limits, draft/rejection logs, and human-gate notes belong in `_audit`, not in the editing plan itself.

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| S5 verdict is reject or regenerate_required | Create a rework-only plan and route upstream. | Do not produce a publish-ready edit checklist. |
| User asks to fix a broken core prop with overlays | Explain visual tradeoff and require explicit acceptance. | Do not paste fake UI/digits as if it restores original footage. |
| Automatic edit output was generated | Mark it `draft_auto_edit` and require human review. | Do not call it `final`. |
| Subtitle cover leaks original text | Expand cover area and recheck timestamps. | Do not accept partially visible garbled text. |
| Editing would look worse than original | Stop, route upstream, or mark accept/defer. | Do not force a local patch. |
| Validator fails | Fix plan/checklist before human gate. | Do not continue to S7 with invalid S6 outputs. |

## Anti-pattern Blacklist

- Do not claim the video was edited without an edited file or user confirmation.
- Do not turn S6 into regeneration, QC, or platform publishing.
- Do not rewrite dialogue meaning while replacing subtitles.
- Do not use rough masks, fake UI, or pasted numbers for plot-critical props unless explicitly accepted.
- Do not put capability limits, draft logs, or human-gate prose in primary edit instructions.
- Do not call a draft/script edit final.

## Completion Gate

S6 is complete only when the plan and checklist exist, validation passes, and the user confirms the human editing plan or provides the edited video.
