---
name: slbb-video-orchestrator
description: AI 短剧 S1-S8 总控 Skill。用于按状态机推进 slbb-video workflow，检查每阶段产物、运行阶段校验、维护 workflow_state.json、生成下一步 handoff，并强制人工闸门。Use when the user asks for “AI短剧总控”, “跑完整个短剧工作流”, “S1-S8 串起来”, “orchestrator”, “状态机”, or “下一步该跑哪个 Skill”. 总控只管流程，不代替 S1-S8 具体内容 Skill。
---

# AI 短剧总控：S1-S8 Orchestrator

## Overview

Use this skill to coordinate the AI short-drama workflow without turning the whole SOP into one large prompt.

The orchestrator controls state, gates, and handoff. Each professional action still belongs to one stage skill: S1 through S8.

## Core Rule

```text
总控管流程，Skill 做专业动作，脚本查状态，人工闸门决定能不能进入下一步。
```

Do not ask one model response to complete S1-S8 in one pass.

Before S1 can move to S2, S1 must include a source coverage audit and dynamic segmentation decision. The orchestrator must not accept a fixed 8/16/20-style compressed count unless `artifacts/_meta/S1_segmentation_decision.md` explains the source coverage and target segment count.

For `long_drama`, S1 cannot start from a raw platform link. Before running `slbb-video-long-replica-script`, the run must have `artifacts/_source/source_manifest.json`. If the source is `local_video` or `direct_video_url`, it must also have `artifacts/_audit/video_ingest/ingest_report.md`, `shot_index.json`, and `contact_sheet.jpg`. If the source is `platform_link` (Douyin/Xiaohongshu/Kuaishou/Bilibili share page), stop and ask the user to download or record a local video first. If the source is only screenshots/transcript/notes, mark it as `partial_material` and keep the low-confidence warning visible.

After S2 is confirmed, the workflow unit is one episode/clip, not the whole season. Default to the first unfinished segment, usually `001`, and run that single segment through S3-S8 before starting the next segment.
When S2 is completed, `workflow_state.json` must initialize `segment_state` from `artifacts/S1/story_segments.json`. S3-S8 always operate on `segment_state.current_segment`. When S8 completes, the orchestrator archives that segment's S3-S8 artifacts under `artifacts/_segments/<segment_id>/`, resets S3-S8, and advances to the next unfinished segment.

## Operating Gates

- 🔴 CHECKPOINT: before marking any stage `ready_for_human`, required outputs must exist and the stage validator must pass.
- 🔴 CHECKPOINT: before marking S1 `ready_for_human`, confirm the S1 validator has checked `artifacts/_meta/S1_segmentation_decision.md` and the `target_segment_count` matches `story_segments.json`.
- 🔴 CHECKPOINT: before marking any stage `completed`, the user must explicitly confirm the human gate and the command must include `--human-confirmed`.
- 🔴 CHECKPOINT: before any batch override after S2, the user must state the exact episode/clip range; otherwise continue the first unfinished single segment.
- 🔴 CHECKPOINT: before any S3-S8 handoff, `artifacts/_handoff/next_step.md` must name the current target segment.
- 🛑 STOP: if `workflow_state.json` is missing, malformed, out of order, or points to a completed later stage while an earlier stage is unfinished, stop and run validation instead of advancing.
- 🛑 STOP: if a stage artifact is missing or a validator fails, keep the current stage open and write the issue into the handoff note.

## Workflow

1. Create an AI 短剧生成过程文件目录:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-orchestrator/scripts/init_run.py" <AI短剧生成过程文件目录> --title "<短剧/项目名>"
   ```

   Or import a V2 monitor (ai-drama-monitor) handoff as the source:
   ```bash
   bin/slbb-video-from-handoff <handoff.md> <AI长剧生成过程文件目录>
   ```
   The handoff path populates `workflow_state.json.source` (v2_video_url / matched_rules / v2_metrics / etc.); S1 then reads `source.v2_video_url` as the highest-priority input. See `references/state_schema.md` for the source field shape.

   For a selected long-drama local video or direct video URL, run source registration and ingest before S1:
   ```bash
   bin/slbb-video-source <AI长剧生成过程文件目录> --source-ref <本地视频路径或直链>
   bin/slbb-video-ingest --run-dir <AI长剧生成过程文件目录> --video <本地视频路径或直链>
   ```

   For a platform share link, `slbb-video-source` records the link and stops. The user must download/record the video first; do not embed third-party download logic inside this skill.

2. Ask for the next step:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-orchestrator/scripts/next_step.py" <AI短剧生成过程文件目录>
   ```
3. Run the stage skill named in `artifacts/_handoff/next_step.md`.
4. 🔴 CHECKPOINT: when a stage artifact is ready for review, mark it ready:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-orchestrator/scripts/advance_stage.py" <AI短剧生成过程文件目录> --stage S1 --status ready_for_human --note "等待用户确认剧情"
   ```
5. 🔴 CHECKPOINT: after the user confirms the human gate, complete the stage:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-orchestrator/scripts/advance_stage.py" <AI短剧生成过程文件目录> --stage S1 --status completed --human-confirmed --note "用户确认剧情"
   ```
6. Validate state:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-orchestrator/scripts/validate_orchestrator_state.py" <AI短剧生成过程文件目录>
   ```

If `CODEX_SKILLS_ROOT` is not set, replace it with the local skills root.

## Stage Map

Read `references/workflow_contract.md` for the full contract.
Read `references/clean_output_contract.md` for the clean-output boundary: S1-S7 primary outputs are next-stage inputs, while process notes live in `_meta`, `_audit`, or `_handoff`.

- S1 `slbb-video-research-script`: 短剧调研与剧情提取
- S2 `slbb-video-image-prompts`: 图片提示词
- S3 `slbb-video-motion-prompts`: 生视频提示词
- S4 `slbb-video-generation-log`: 视频生成记录
- S5 `slbb-video-qc`: 视频质检
- S6 `slbb-video-edit-fix`: 剪辑修正
- S7 `slbb-video-distribution-pack`: 分发包
- S8 `slbb-video-review`: 发布后复盘

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| `workflow_state.json` does not exist | Run `init_run.py` or ask for the correct process directory. | Do not infer a state from nearby files. |
| `workflow_state.json` is invalid JSON or missing a stage | Run `validate_orchestrator_state.py`, report the exact error, and stop. | Do not hand-edit a guessed stage order. |
| User asks to run S1-S8 in one pass | Explain that the orchestrator only advances one stage or one post-S2 segment at a time, then run `next_step.py`. | Do not produce all stage outputs in one response. |
| User asks to batch all episodes after S2 | Ask for an explicit episode/clip range; if absent, continue the first unfinished segment, usually `001`. | Do not silently generate or advance every remaining segment. |
| S1 segmentation count is challenged or source coverage is unclear | Return to S1, revise the source coverage audit and segmentation decision, then invalidate downstream S2/S3 artifacts that depended on the old count. | Do not keep advancing with the old image/video prompts. |
| Required outputs are missing | Keep the stage open and route back to the stage skill listed in the handoff. | Do not mark `ready_for_human` or `completed`. |
| Long-drama source is a platform link | Ask the user to download/record a local video, then rerun `slbb-video-source` and `slbb-video-ingest`. | Do not let S1 analyze a Douyin/Xiaohongshu share link directly. |
| Long-drama local/direct video has no `video_ingest` packet | Run `slbb-video-doctor`, install missing environment with user approval, then run `slbb-video-ingest`. | Do not repeatedly read the full video in chat. |
| Long-drama source is screenshots/subtitles/notes only | Register `partial_material` and require low-confidence human confirmation. | Do not present it as a full video breakdown. |
| Stage validator fails | Preserve the validator output in the handoff note and leave the status unchanged. | Do not use `--skip-validator` unless the user explicitly accepts the risk. |
| Human confirmation is missing | Keep `gate_status` as `waiting` or `pending` and ask for confirmation. | Do not pass `--human-confirmed` on the user's behalf. |
| Stage content needs rewriting | Route to the owning S1-S8 skill and keep orchestrator scope to state, gates, and handoff. | Do not let the orchestrator rewrite stage content. |
| Primary output contains process notes | Move process notes to `_meta`, `_audit`, or `_handoff` and keep the primary artifact clean. | Do not feed polluted primary outputs into the next stage. |

## Rules

- Never mark a stage `completed` without required artifacts and explicit human confirmation.
- Never skip a stage unless the user explicitly says to override the workflow.
- Never let the orchestrator rewrite stage content. Route content work back to the stage skill.
- Never treat a plausible S1 episode count as confirmed unless the S1 source coverage audit and segmentation decision are present and validated.
- After S2, never generate or advance all remaining episodes/clips in one stage call. The normal loop is `001: S3 -> S4 -> S5 -> S6 -> S7 -> S8`, then `002: S3 -> S4 -> ...` after the user confirms the next segment.
- S2 can contain all character and scene references, but S3 must select only the references needed for the current target episode/clip unless the user explicitly asks for a batch override.
- If a validator fails, keep the current stage open and write a clear handoff note.
- `workflow_state.json` is the local truth source for one AI 短剧生成过程文件目录.
- After S2, `workflow_state.json.segment_state.current_segment` is the local truth source for the active episode/clip.
- `artifacts/_handoff/next_step.md` is the next-action note for the next Codex conversation.
- Total completion requires S1-S8 completed, all gates confirmed, and state validation passing.

## Anti-pattern Blacklist

- Do not use the orchestrator as a content generator for S1-S8.
- Do not bypass `next_step.py` when deciding what to run next.
- Do not mark a stage `completed` only because the model says the output looks ready.
- Do not advance a later stage while any earlier stage is not `completed`.
- Do not treat S1 structural validation alone as proof that the source boundary or compressed segment count is correct.
- Do not batch episodes/clips after S2 without an explicit user override and a written target range.
- Do not put workflow rationale, route notes, risk notes, or human-gate text into S1-S7 primary outputs.
- Do not use `--skip-validator` as a convenience flag; use it only after the user explicitly accepts the risk.
- Do not repair missing stage artifacts inside the orchestrator; send the work back to the stage skill that owns the artifact.

## Required Files

Each AI 短剧生成过程文件目录 should have:

```text
workflow_state.json
artifacts/_handoff/next_step.md
```

See `references/state_schema.md` for the state file shape.
