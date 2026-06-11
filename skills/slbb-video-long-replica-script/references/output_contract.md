# Long Drama S1 Output Contract

S1 turns one selected reference video or user-provided reference package into clean replica and second-creation descriptions. It is not a topic workbench and it is not a prompt-generation stage.

## Required Directory

```text
<run_dir>/
  artifacts/
    S1/
      source_replica_description.md
      second_creation_description.md
      story_segments.json
    _meta/
      S1_replica_notes.md
```

## source_replica_description.md

Must use this structure:

```markdown
# AI短视频复刻描述提取报告

## 1. 视频基础信息
## 2. 固定角色形象描述
## 3. 视频片段拆分总览
## 4. 分片段详细画面描述
## 5. 台词 / 字幕 / 旁白汇总
## 6. 原视频剧情总结
```

This file describes the source reference video. It must not include second-creation execution notes, workflow notes, or video-generation prompts.

## second_creation_description.md

Must use this structure:

```markdown
# 二次创作版复刻描述

## 1. 本次二创方向
## 2. 二创后角色形象描述
## 3. 二创后片段拆分总览
## 4. 二创后分片段详细画面描述
```

This file keeps the source structure but performs originalizing adjustments inside the approved boundary.

## story_segments.json

Top-level object:

```json
{
  "characters": [],
  "episodes": []
}
```

Each character must include:

- `name`
- `role`
- `appearance`
- `relationship`
- `visual_anchor`

`visual_anchor` must include:

- `face`
- `hair`
- `body`
- `costume`
- `shoes`
- `accessories`
- `temperament`

Recommended long-drama character fields:

- `age_stage`
- `same_person_group`
- `continuity_anchor`
- `production_alias`

`name` is the canonical character ID used by downstream S2/S3. Prefer source/reference role names unless the user explicitly asks to rename roles. If the second-creation version changes the role label, use `production_alias`, `role`, `appearance`, or segment descriptions; do not change naming systems between top-level characters and episodes.

Each episode must include:

- `episode_id`
- `episode_name`
- `source_time_range`
- `duration_seconds`
- `scene`
- `characters`
- `props`
- `replica_description`
- `second_creation_description`
- `timeline`
- `review`

`timeline` must be a non-empty object. Each beat should include:

- `camera`
- `action`
- `dialogue_or_sound`

Every value in `episodes[].characters` must exactly match one top-level `characters[].name`. If an episode needs a group such as `小鸡群`, `路人`, or `学生群体`, add it as a top-level character/group entry with a visual anchor, or move it to `props` / scene description instead of `characters`.

## Clean Output Rules

Primary S1 files must not contain:

- content workbench or topic-pool notes
- trend scoring
- video generation prompts
- storyboard prompts
- finished shooting scripts
- cover copy
- publishing plan
- workflow rationale
- human confirmation text

Put source limits, missing evidence, user confirmation notes, and blocked items in `artifacts/_meta/S1_replica_notes.md`.
