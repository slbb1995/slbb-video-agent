# S1 Output Contract

S1 is a workflow node. It is not complete until all required artifacts exist and validate.

S1 primary outputs are clean inputs for S2. Do not put workflow principles, research caveats, copyright analysis, version notes, or human-gate copy into the primary files. Put that material under `artifacts/_meta/` or `artifacts/_handoff/`.

`artifacts/_meta/S1_segmentation_decision.md` is required before S1 can be marked ready for human review. It records why the source drama was compressed into the exact number of 15-second units used in `story_segments.json`.

## Required Directory

```text
<run_dir>/
  artifacts/
    S1/
      story_extract.md
      story_segments.json
    _meta/
      S1_segmentation_decision.md # required
      S1_research_notes.md        # optional
    _handoff/
      S1_human_confirmation_card.md # optional
```

## story_extract.md

Must include these Markdown headings:

```markdown
# S1 剧情提取结果

## 一句话简介
## 核心人物
## 核心场景
## 分集列表
## 下一阶段输入
```

`## 核心人物` and `## 下一阶段输入` must give S2 enough visual anchors to produce one-image three-view character reference sheets. For each core character, include stable appearance details such as face, hair, body shape, costume, shoes, accessories, and visual temperament. If a detail is inferred rather than sourced, keep it production-useful and record inference notes in `_meta/S1_research_notes.md`.

## story_segments.json

Must be valid JSON:

```json
{
  "characters": [
    {
      "name": "",
      "role": "",
      "appearance": "",
      "relationship": "",
      "visual_anchor": {
        "face": "",
        "hair": "",
        "body": "",
        "costume": "",
        "shoes": "",
        "accessories": "",
        "temperament": ""
      }
    }
  ],
  "episodes": [
    {
      "episode_id": "001",
      "episode_name": "",
      "scene": {
        "type": "",
        "location": "",
        "time_light": "",
        "environment": ""
      },
      "characters": [
        {
          "name": "",
          "psychology": "",
          "costume": "",
          "action_habit": ""
        }
      ],
      "props": [],
      "timeline": {
        "0-2s": {
          "camera": "",
          "action": "",
          "dialogue_or_sound": ""
        },
        "3-10s": {
          "camera": "",
          "action": "",
          "dialogue_or_sound": ""
        },
        "11-15s": {
          "camera": "",
          "action": "",
          "dialogue_or_sound": ""
        }
      },
      "review": {
        "opening_hook": "",
        "middle_hook": "",
        "ending_hook": ""
      }
    }
  ]
}
```

## S1_segmentation_decision.md

Must include:

```markdown
# S1 分集数量决策

source_type:
original_episode_count:
collected_source_count:
material_types:
coverage_level:
target_segment_count:
decision_basis:
boundary:
```

Rules:

- `target_segment_count` must match the number of `episodes` in `story_segments.json`.
- If coverage is low, `boundary` must not claim full-series reconstruction.
- The count must come from source coverage, plot density, narrative arc count, and usable 15-second hooks, not a fixed template.

## Clean Output Guard

`story_extract.md` and `story_segments.json` must not include:

- `Workflow` / `workflow`
- `V2 原则`
- `输入与来源`
- `版权与改写风险提示`
- `人工确认项`
- `不能自动进入下一步`
