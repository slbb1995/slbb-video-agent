---
name: slbb-video-long-replica-script
description: AI 长剧 S1 对标视频复刻描述、二创描述、角色形象提取和 3-15 秒片段拆分。Use when the user provides a selected reference video/link/recording/screenshots and asks for “长剧S1”, “复刻描述”, “二创描述”, “对标视频拆解”, “长剧片段拆分”, or S1 artifacts for long_drama mode in the slbb-video workflow.
---

# AI 长剧 S1：复刻描述与二创描述

## Overview

Use this skill after a long-drama topic/reference has already been selected. It turns a reference video, recording, screenshots, transcript, or user notes into production-ready S1 text assets for the `long_drama` workflow.

This skill does not do the content workbench. It does not find daily topics, monitor platforms, score hot videos, or create a topic pool.

## Core Rule

```text
S1 只交付复刻描述、二创描述、角色形象和片段结构。
S1 不生成视频提示词，不生成分镜提示词，不生成成片脚本。
```

## Inputs

Preferred workflow input:

- `artifacts/_source/source_brief.md`
- `artifacts/_source/source_manifest.json`
- For `local_video` / `direct_video_url`: `artifacts/_audit/video_ingest/ingest_report.md`, `shot_index.json`, `contact_sheet.jpg`, and `transcript.txt`

The raw reference video, recording, screenshots, transcript, subtitles, dialogue, or narration are evidence, not the high-frequency prompt input. Use the preprocessed evidence packet first; use raw material only to resolve a specific missing point after checking `source_brief.md`.

If `source_manifest.json.source_kind` is `platform_link`, stop. Ask the user to download/record the platform video as a local file first, then rerun `slbb-video-source` and `slbb-video-ingest`.

If the video cannot be inspected, do not invent visual facts. Ask the user to fill the missing part in `source_brief.md` with key screenshots, transcript excerpts, or timecoded notes.

## Workflow

1. Read `references/replica_description_sop.md` before writing S1 content.
2. Read `references/output_contract.md` for required file names and validation rules.
3. Read the source packet:
   - `artifacts/_source/source_brief.md`
   - `artifacts/_source/source_manifest.json`
   If `source_kind` is `local_video` or `direct_video_url`, also read `artifacts/_audit/video_ingest/ingest_report.md` and `shot_index.json`.
   If `source_brief.md` is empty or still a template, stop and ask the user to fill it. Do not analyze the full raw video as a substitute.
4. Create the S1 skeleton if writing to a run directory:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-long-replica-script/scripts/scaffold_s1_run.py" <run_dir>
   ```
5. Produce the source replica report:
   - video basics
   - fixed character descriptions
   - same-character age-stage descriptions, when present
   - 3-15 second segment overview
   - detailed visual replica descriptions
   - dialogue/subtitle/narration summary
   - source story summary
6. Produce the second-creation description only after the user has either supplied a specific second-creation direction or accepted the default light second-creation route.
7. Convert the approved second-creation description into `story_segments.json` for downstream S2/S3:
   - `characters` must include production-useful visual anchors.
   - `characters[].name` is the canonical character ID. Prefer the source/reference role name, such as `卖小鸡老人` or `拍摄女子`, unless the user explicitly asks to rename roles.
   - If second creation changes the role label, keep that in `role`, `appearance`, `relationship`, `visual_anchor`, or the segment descriptions. Do not silently create a second naming system.
   - `episodes` must represent one 3-15 second production unit each.
   - Every value in `episodes[].characters` must exactly match one top-level `characters[].name`.
   - Each episode must carry source and second-creation descriptions, not video prompts.
8. Put process notes, missing evidence, blocked items, and user confirmation notes in `_meta` or `_handoff`, not in S1 primary files.
9. Validate:
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-long-replica-script/scripts/validate_s1_outputs.py" <run_dir>
   ```
10. Stop at the human gate. Do not continue to S2 until the user confirms the replica/second-creation description and segment split.

## Required Outputs

```text
artifacts/S1/source_replica_description.md
artifacts/S1/second_creation_description.md
artifacts/S1/story_segments.json
artifacts/_meta/S1_replica_notes.md
```

## Primary Output Boundary

Primary S1 outputs may contain:

- source replica description
- second-creation direction and description
- character, age-stage, scene, action, expression, emotion, dialogue, camera, atmosphere, and segment details
- clean JSON consumed by S2/S3

Primary S1 outputs must not contain:

- content workbench notes
- topic pool or trend scoring
- video generation prompts
- storyboard prompts
- finished shooting scripts
- cover copy
- publishing plan
- workflow rationale
- human-gate prose

## Token Budget Rules

- Do not paste or re-read the full raw video analysis, full transcript, or all screenshots in the chat.
- For local/direct videos, read the `video_ingest` evidence packet instead of reprocessing the same video.
- `source_brief.md` should stay concise: normally 1500-2500 Chinese characters for a 30-60 second reference video.
- Use at most 12 key timecoded beats and at most 10 key dialogue/subtitle bullets unless the user explicitly approves a deeper pass.
- If the source is `partial_material`, clearly mark the S1 analysis as low-confidence and ask for human confirmation before proceeding.
- Downstream S2/S3 should read S1 clean outputs, not the raw source packet.

## Long-Drama Segment Rules

- Split by visual/story change, not by equal duration.
- Minimum segment duration is 3 seconds.
- Maximum segment duration is 15 seconds.
- A 2-minute long drama should normally become multiple 3-15 second production units.
- A segment must split when scene, character, emotion, dialogue stage, shot size, memory/real-world boundary, key prop, conflict, reversal, or ending beat changes.
- If the same character appears across age stages, list each age stage separately and record the continuity traits that should stay stable.
- Keep one canonical name system in `story_segments.json`. Do not use source names in top-level `characters` and second-creation names inside `episodes`, or the reverse.

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| `source_manifest.json` is missing | Stop and route back to `slbb-video-source` before writing S1. | Do not infer source type from chat history. |
| `source_kind` is `platform_link` | 🛑 STOP: ask the user to download or record the platform video, then rerun source registration and ingest. | Do not analyze a Douyin/Xiaohongshu/Kuaishou/Bilibili share page directly. |
| `local_video` or `direct_video_url` has no `video_ingest` packet | Run the environment doctor and ingest step with user approval. | Do not repeatedly read the full video in chat. |
| `source_brief.md` is empty or still a template | Ask the user to fill the brief with key time points, character anchors, and dialogue evidence. | Do not replace the brief by consuming the raw video end to end. |
| Input is screenshots, subtitles, notes, or oral description only | Mark the run as `partial_material`, write a low-confidence warning, and stop at the human gate. | Do not present the result as a full video breakdown. |
| Visual evidence is unclear or unavailable | Record the missing evidence in `artifacts/_meta/S1_replica_notes.md` and ask for screenshots or timecoded notes. | Do not invent character appearance, camera movement, props, or scene facts. |
| Character names diverge between source description and `story_segments.json` | Normalize to one canonical `characters[].name` system before validation. | Do not let downstream S2/S3 inherit mixed name systems. |
| Any segment is shorter than 3 seconds or longer than 15 seconds | Re-split by visual/story beat and rerun validation. | Do not keep an invalid segment just because the story reads smoothly. |
| Validator fails | Preserve the validator issue in `_handoff` or `_meta`, fix the owning S1 artifact, and rerun validation. | Do not move to S2 or mark S1 complete. |

## Anti-pattern Blacklist

- Do not use this skill for topic discovery, hot-video scoring, content workbench planning, or daily platform monitoring.
- Do not let S1 generate video prompts, storyboard prompts, finished shooting scripts, cover copy, or publishing plans.
- Do not paste full transcripts, full video analyses, all screenshots, or raw process dumps into primary S1 outputs.
- Do not reprocess the same local video after `artifacts/_audit/video_ingest/` already exists.
- Do not treat partial screenshots/subtitles/notes as complete source evidence.
- Do not invent visual facts, dialogue, camera language, character age stages, or scene props that are not supported by the source packet.
- Do not mix source role names and second-creation role names in `story_segments.json`.
- Do not continue to S2 until required S1 files exist, validation passes, and the user confirms the replica description, second-creation direction, and segment split.

## Completion Gate

S1 is complete only when all required artifacts exist, validation passes, and the user confirms the replica description, second-creation direction, and segment split.
