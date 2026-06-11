---
name: slbb-video-distribution-pack
description: AI 短剧 S7 分发包生成。基于 S1-S6 的剧情、成片、质检和剪辑修正结果，生成手动发布所需的标题候选、简介、抖音/视频号/小红书平台文案、封面建议、发布时间建议和发布检查清单。Use when the user asks for “矩阵分发”, “分发包”, “平台文案”, “发布清单”, “抖音/视频号/小红书文案”, or S7 distribution artifacts in the slbb-video workflow. 第一版只准备分发材料，不自动发布。
---

# AI 短剧 S7：分发包

## Overview

Use this skill to turn a confirmed short-drama video into a manual publishing package.

S7 first version is intentionally conservative: it prepares the materials for 抖音、视频号、小红书, but it does not log in, upload, schedule, or publish anything.

## Operating Gates

- 🔴 CHECKPOINT: before writing a normal distribution pack, confirm S5/S6 status. If S5/S6 has blocking issues, write a `not ready to publish` package and route back to the blocking stage.
- 🔴 CHECKPOINT: before any wording says `手动发布`, the final video path or platform draft link must be present and human-confirmed.
- 🔴 CHECKPOINT: before entering S8 review, the user must confirm that manual publishing actually happened or provide platform-side evidence.
- 🛑 STOP: if the final video path is missing, S7 may only produce a blocked publish checklist; do not create platform copy as if the video is ready.
- 🛑 STOP: if the user asks this skill to upload, schedule, scrape dashboards, or mark metrics, stop and route to manual publishing or S8 after evidence exists.

## Inputs

Prefer workflow artifacts:

```text
artifacts/S1/story_extract.md
artifacts/S3/motion_prompt_pack.md
artifacts/S4/generation_run_log.md
artifacts/S5/qc_report.md
artifacts/S5/qc_verdict.json
artifacts/S6/edit_fix_plan.md
artifacts/S6/edit_checklist.md
```

Also accept:

- Final video file path or platform draft link
- Cover frame or screenshot
- User notes about target account, target audience, and publish timing
- Platform list, defaulting to 抖音、视频号、小红书

## Workflow

1. Create S7 skeleton:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-distribution-pack/scripts/scaffold_s7_run.py" <run_dir>
   ```
2. Read the confirmed S1-S6 artifacts and identify the final video, story hook, target audience, QC status, and remaining risk notes.
3. Follow `references/platform_pack_standard.md` to write platform-specific copy.
4. Write or update:
   - `artifacts/S7/distribution_pack.md`
   - `artifacts/S7/platform_copy.md`
   - `artifacts/S7/publish_checklist.md`
   - optional process notes under `artifacts/_meta/S7_distribution_notes.md`
5. Insert one platform block when needed:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-distribution-pack/scripts/add_platform_copy.py" <run_dir> --platform 抖音 --title "标题候选" --caption "正文文案" --hashtags "#短剧 #AI" --cover "封面建议" --publish-time "今晚 20:00-22:00"
   ```
6. Validate:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-distribution-pack/scripts/validate_s7_outputs.py" <run_dir>
   ```
7. Stop at the human gate. Do not claim the video has been published.

If `CODEX_SKILLS_ROOT` is not set, replace it with the local skills root.

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| Final video path or draft link is missing | Write a blocked `publish_checklist.md` and ask for the final video/draft link. | Do not invent a video path or produce copy that implies the video is ready. |
| S5 verdict is reject/blocking | Mark `暂不建议发布` and route back to S5/S6. | Do not polish the package into a publish-ready version. |
| S6 fix plan exists but edited video is not confirmed | Keep status as `未发布 / 待人工修正确认`. | Do not say the edited version is final. |
| User asks for automatic upload/schedule/publish | State that S7 only prepares manual publishing materials. | Do not log in, upload, schedule, or claim platform actions. |
| User asks to enter S8 immediately | Require manual publish evidence or explicit user confirmation. | Do not create review outputs from an unpublished package. |
| Platform copy changes story facts | Restore the S1-S6 plot, relationship, and ending. | Do not rewrite the story to chase clicks. |
| Account permission, audit status, or traffic forecast is unknown | Mark it as `人工检查`. | Do not fabricate algorithm, permission, audit, or performance claims. |
| Primary output contains workflow/process notes | Move notes to `publish_checklist.md` or `_meta/S7_distribution_notes.md`. | Do not put route reasoning or human-gate prose inside platform copy. |

## Rules

- S7 produces a distribution pack only. It never performs automatic publishing in the first version.
- Always mark the publishing state as `未发布 / 手动发布 / 不自动发布`.
- Do not say “已发布”, “已上传”, or “已定时发布” unless the user provides platform-side confirmation.
- Do not invent platform performance data, algorithm rules, account permissions, or compliance conclusions.
- If S5/S6 still has blocking issues, create a “not ready to publish” package and route back to S5/S6.
- Keep title candidates concrete and story-driven. Avoid generic AI tutorial wording.
- Make platform copy meaning-preserving: do not change the plot, character relationship, or ending to chase clicks.
- Each platform block must include title, caption/body, hashtags/topics, cover suggestion, and publish-time suggestion.
- Put risk notes and human review notes in `publish_checklist.md` or `_meta`, not inside platform copy.

## Anti-pattern Blacklist

- Do not say `已发布`, `已上传`, `已定时发布`, or `发布完成` unless the user provides platform-side confirmation.
- Do not treat `S7 分发包完成` as equal to `平台发布完成`.
- Do not continue to S8 review without actual publishing evidence.
- Do not use S7 to repair S5/S6 blocking problems; route back instead.
- Do not invent final video paths, account permissions, platform审核结果, traffic forecasts, or comment data.
- Do not put `TODO`, `待填写`, or `待补充` in final S7 artifacts.
- Do not include workflow rationale, input-source blocks, or artificial human-confirmation prose in `platform_copy.md`.
- Do not change plot facts, character relationships, or ending details for clickbait.

## Platform Scope

First-version default platforms:

- 抖音：强钩子、短标题、短正文、话题标签、封面标题。
- 视频号：更直接、更像真实转述，强调故事冲突和评论引导。
- 小红书：笔记感标题、封面字、正文分段、标签。

For detailed requirements, read `references/platform_pack_standard.md`.

## Required Outputs

```text
artifacts/S7/distribution_pack.md
artifacts/S7/platform_copy.md
artifacts/S7/publish_checklist.md
```

See `references/output_contract.md`.

Primary S7 outputs are client-facing publishing materials. They should not contain workflow reasoning, input-source blocks, or artificial human-confirmation prose.

## Completion Gate

S7 is complete only when all three required outputs exist, validation passes, and the user confirms whether to manually publish or revise the package. It is not equivalent to publishing.
