---
name: slbb-video-generation-log
description: AI 短剧 S4 视频生成执行记录。Use when the user manually generates short-drama videos in 即梦, 可灵, or another platform and needs to log the platform, prompt, image assets, generation attempts, generated files/URLs, failures, selected version, and handoff to S5 QC. Trigger for “视频生成记录”, “生成日志”, “记录即梦/可灵生成结果”, “选择哪版视频”, “人工生成视频后登记”, or S4 artifacts in the slbb-video workflow.
---

# AI 短剧 S4：视频生成记录

## Overview

Use this skill to record manual video generation attempts after S3. S4 does not call 即梦, 可灵, or any video-generation API.

The purpose is to make generation observable: which prompt was used, which image assets were uploaded, what versions were generated, which one was selected, and why failures happened.

## Operating Gates

- 🔴 CHECKPOINT: before appending a success row, require a real output path, URL, platform id, or explicit human note.
- 🔴 CHECKPOINT: before S4 completion, at least one record must be selected for S5 QC.
- 🔴 CHECKPOINT: before moving to S5, the selected video/version must be confirmed by the user.
- 🛑 STOP: if no usable generated video exists, keep S4 incomplete and route back to S2/S3 or platform retry.
- 🛑 STOP: if the user asks S4 to call 即梦/可灵 APIs, keep the task manual and record only what the human generated.

## Inputs

Prefer workflow artifacts:

```text
artifacts/S2/image_prompt_pack.md
artifacts/S3/motion_prompt_pack.md
artifacts/S3/platform_copy_ready_prompts.md
```

Also accept manual data:

- Platform: 即梦 / 可灵 / other
- Generation mode: text-to-video / image-to-video
- Prompt ID or copied prompt
- Reference image path or URL
- Generated video file path or URL
- Failure reason
- Selected version

## Workflow

1. Create the S4 skeleton:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-generation-log/scripts/scaffold_s4_run.py" <run_dir>
   ```
2. Ask the human operator to manually generate video on the target platform.
3. Append each generated version or failed attempt:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-generation-log/scripts/append_generation_record.py" <run_dir> --clip-id clip-001 --platform 即梦 --generation-mode image-to-video --prompt-ref artifacts/S3/platform_copy_ready_prompts.md --reference-assets "artifacts/S2/image_prompt_pack.md" --output-ref "/path/or/url/to/video.mp4" --status success --selected-for-qc yes --notes "selected version"
   ```
4. Update `artifacts/S4/generation_run_log.md` with a concise summary and selected version.
   - Keep the Markdown summary clean: platform, settings, generated versions, selected version, and failure/retry notes.
   - Put operator reasoning or handoff notes in `artifacts/_audit/S4_attempt_notes.md` if needed.
5. Validate:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-generation-log/scripts/validate_s4_outputs.py" <run_dir>
   ```
6. Stop at the human gate. Do not continue to S5 until the selected video is confirmed.

If `CODEX_SKILLS_ROOT` is not set, replace it with the local skills root.

## Rules

- Do not claim that a video has been generated unless there is a file path, URL, or explicit human note.
- Do not call platform APIs in this first version.
- Keep failed attempts. They are useful for S5 and future prompt fixes.
- Record the exact prompt reference used for each attempt.
- Record reference assets used for image-to-video.
- At least one row must be selected for QC before S4 can be marked complete.
- If no generated video is usable, S4 remains incomplete and should route back to S2/S3 or platform retry.

## Required Outputs

```text
artifacts/S4/generation_run_log.md
artifacts/S4/generation_run_log.csv
```

See `references/generation_log_schema.md` for required columns and Markdown sections.

Primary S4 outputs must not include workflow principles, artificial confirmation sections, or long process explanations. They are logs for S5, not training notes.

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| User has not generated a video yet | Ask the human to generate manually and record S4 as incomplete. | Do not fabricate a success row. |
| Attempt failed | Record the failed row with `failure_reason`. | Do not delete failed attempts. |
| Multiple versions exist | Mark exactly which version is selected for QC. | Do not leave S5 to guess the selected version. |
| Selected row lacks output path or URL | Treat S4 as incomplete until evidence exists. | Do not mark selected without a usable reference. |
| CSV shape fails validation | Fix the log schema before handoff. | Do not continue with an ad hoc table. |
| User asks to evaluate video quality | Route quality judgment to S5. | Do not perform QC inside S4. |

## Anti-pattern Blacklist

- Do not call video-generation APIs in this skill.
- Do not claim generation succeeded without a path, URL, platform id, or explicit human note.
- Do not overwrite failed attempts to make the log look clean.
- Do not select more than one version for QC without a clear reason in notes.
- Do not put workflow principles or human-gate prose in `generation_run_log.md`.
- Do not continue to S5 without a selected version.

## Completion Gate

S4 is complete only when the Markdown log and CSV log exist, validation passes, and at least one generated video/version is marked as selected for S5 QC.
