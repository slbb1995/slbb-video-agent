---
name: slbb-video-review
description: AI 短剧 S8 发布后复盘。读取抖音、视频号、小红书等平台的播放、点赞、评论、转发、收藏、完播、留存和用户反馈，输出复盘报告、问题归因、下一轮选题建议和提示词/生成/剪辑/分发调整计划。Use when the user asks for “短剧复盘”, “发布后数据分析”, “播放点赞转发留存复盘”, “下一轮怎么改”, or S8 review artifacts in the slbb-video workflow.
---

# AI 短剧 S8：发布后复盘

## Overview

Use this skill to convert post-publishing performance data into a concrete next-iteration plan.

Current stable input mode: `screenshot_csv`.

In this version, S8 does not log in to platform backends, does not operate Chrome, and does not scrape Douyin/视频号/小红书 dashboards automatically. The user provides platform screenshots, CSV exports, comment samples, or manually typed metrics. The skill parses those provided materials, records evidence, then writes the review.

S8 is not a generic summary. It must connect data back to upstream workflow decisions: topic, story, image prompts, motion prompts, generation, QC, edit, and distribution.

## Operating Gates

- 🔴 CHECKPOINT: before writing S8, confirm the video was manually published or that the user provided post-publishing data.
- 🔴 CHECKPOINT: before making a conclusion, attach at least one evidence type: metric row, screenshot/CSV path, comment sample, or S1-S7 artifact reference.
- 🔴 CHECKPOINT: before starting the next run, the user must confirm the next topic direction or concrete change list.
- 🛑 STOP: if there is no platform data, screenshot, CSV, comment sample, or manual metric, write a blocked review handoff instead of a performance review.
- 🛑 STOP: if the user asks for backend scraping or logged-in dashboard capture, route to future `browser_assisted` work and ask for screenshots/CSV first.

## Inputs

Prefer workflow artifacts:

```text
artifacts/S1/story_extract.md
artifacts/S2/image_prompt_pack.md
artifacts/S3/motion_prompt_pack.md
artifacts/S4/generation_run_log.md
artifacts/S5/qc_report.md
artifacts/S6/edit_fix_plan.md
artifacts/S7/distribution_pack.md
artifacts/S7/platform_copy.md
artifacts/S7/publish_checklist.md
```

Also accept:

- Platform metrics: views, likes, comments, shares, saves, completion rate, retention, publish time
- Platform screenshots or CSV exports
- Comment samples and user feedback
- Manual notes about title, cover, account, publish timing, and traffic source

Stable mode contract:

- `screenshot_csv`: user provides screenshots and/or CSV exports. Use this as the default and only production-supported S8 mode.
- `browser_assisted`: not active yet. Do not open logged-in platform backends or claim automatic dashboard capture as part of this skill.

## Workflow

1. Create S8 skeleton:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-review/scripts/scaffold_s8_run.py" <run_dir>
   ```
2. Record platform metrics. You can add one metric row:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-review/scripts/add_metric_row.py" <run_dir> --platform 抖音 --views 1200 --likes 80 --comments 12 --shares 5 --saves 9 --completion-rate 23.5 --retention "3s=61%, 5s=43%" --feedback "开头能看懂，但反转不够强"
   ```
   Or ingest a CSV export:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-review/scripts/ingest_metric_csv.py" <run_dir> <csv_path> --source "抖音后台导出"
   ```
3. Read S1-S7 artifacts and compare data against each upstream decision.
4. If screenshots are provided, save or reference them under `artifacts/S8/evidence/` and write a short evidence note that names each screenshot, extracted metrics, comment samples, and confidence. Do not OCR or infer invisible data unless you can actually read it from the screenshot.
5. Write:
   - `artifacts/S8/review_report.md`
   - `artifacts/S8/next_iteration_plan.md`
6. Validate:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-review/scripts/validate_s8_outputs.py" <run_dir>
   ```
7. Stop at the human gate. The user confirms the next topic direction and concrete changes before the next run.

If `CODEX_SKILLS_ROOT` is not set, replace it with the local skills root.

## Rules

- Do not produce vague review language. Every conclusion needs a data point, comment sample, or workflow artifact as evidence.
- If data is missing, mark it as missing and lower confidence. Do not invent metrics.
- Always separate platform performance from production-process issues.
- Always include upstream attribution: 选题、剧情、图片提示词、视频提示词、生成、质检、剪辑、发布.
- The next iteration plan must say exactly what to change and how to verify the change.
- Do not treat a single video as statistical proof. Label low-sample conclusions as tentative.
- Do not enter a new S1 run until the user confirms the next-iteration direction.
- Do not use the user's long-lived browser login state for S8 in this version. If the user asks for dashboard capture, ask for screenshots/CSV first or explicitly route to a future `browser_assisted` upgrade.
- For screenshots, always record what was directly visible and what was not visible. If a metric is cropped, blurred, hidden, or unreadable, mark it as missing.
- For CSV exports, preserve the original CSV path in the report and normalize metrics into the S8 review table.

## Review Dimensions

Read `references/review_standard.md` when writing the report.

Minimum dimensions:

- Platform data: playback, likes, comments, shares, saves, completion, retention
- User feedback: comment themes, objections, confusion points, emotional reactions
- Content diagnosis: hook, conflict, reversal, character clarity, pacing
- Workflow diagnosis: prompt quality, generation failure, QC miss, edit issue, distribution packaging
- Next changes: topic, story, image prompts, motion prompts, generation settings, edit, platform copy

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| S7 package exists but no publishing evidence | Stop and ask for manual publish confirmation or platform-side evidence. | Do not review an unpublished package as if it performed. |
| Metrics are missing or cropped | Mark fields as `缺失` and lower confidence. | Do not infer hidden values. |
| Only one low-sample video exists | Label conclusions tentative. | Do not present one sample as statistical proof. |
| User requests automatic dashboard capture | Ask for screenshots/CSV or route to future `browser_assisted`. | Do not use logged-in browser state in S8. |
| Comments are unavailable | Separate missing user feedback from platform metrics. | Do not invent comment themes. |
| Next plan lacks evidence or verification method | Rewrite it into problem/evidence/change/verification format. | Do not output generic “继续优化”. |

## Anti-pattern Blacklist

- Do not fabricate views, likes, comments, shares, completion, retention, or user feedback.
- Do not over-attribute performance to one upstream step without evidence.
- Do not hide missing data or confidence level.
- Do not start a new S1 run from S8 without user confirmation.
- Do not log in to platform backends or scrape dashboards in this version.
- Do not output vague review language without data, comment, or artifact evidence.

## Required Outputs

```text
artifacts/S8/review_report.md
artifacts/S8/next_iteration_plan.md
```

See `references/output_contract.md`.

## Completion Gate

S8 is complete only when the review report and next-iteration plan exist, validation passes, and the user confirms the next topic direction or change list.
