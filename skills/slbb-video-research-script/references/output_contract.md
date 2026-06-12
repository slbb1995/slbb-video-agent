# S1 输出契约

S1 是工作流节点。只有所有必需产物都存在并验证通过，S1 才算完成。

S1 主输出是给 S2 使用的干净输入。不要把工作流原则、调研限制、版权分析、版本说明或人工闸门话术写进主文件。那些内容应放在 `artifacts/_meta/` 或 `artifacts/_handoff/`。

S1 标记为待人工审查前，必须存在 `artifacts/_meta/S1_segmentation_decision.md`。它记录为什么把来源短剧压缩成 `story_segments.json` 中对应数量的 15 秒单元。

## 必需目录

```text
<run_dir>/
  artifacts/
    S1/
      story_extract.md
      story_segments.json
    _meta/
      S1_segmentation_decision.md # 必需
      S1_research_notes.md        # 可选
    _handoff/
      S1_human_confirmation_card.md # 可选
```

## story_extract.md

必须包含这些 Markdown 标题：

```markdown
# S1 剧情提取结果

## 一句话简介
## 核心人物
## 核心场景
## 分集列表
## 下一阶段输入
```

`## 核心人物` 和 `## 下一阶段输入` 必须给 S2 足够的视觉锚点，能生成“一张图三视图”角色参考图。每个核心角色都要包含稳定外貌细节，例如脸、头发、体型、服装、鞋、配饰和视觉气质。如果某个细节是推断而非来源事实，要保持生产可用，并把推断说明记录到 `_meta/S1_research_notes.md`。

## story_segments.json

必须是合法 JSON：

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

必须包含：

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

规则：

- `target_segment_count` 必须与 `story_segments.json` 中的 `episodes` 数量一致。
- 如果覆盖度低，`boundary` 不得声称是整季重构。
- 数量必须来自来源覆盖、剧情密度、叙事弧数量和可用 15 秒钩子，不能来自固定模板。

## 干净输出保护

`story_extract.md` 和 `story_segments.json` 不得包含：

- `Workflow` / `workflow`
- `V2 原则`
- `输入与来源`
- `版权与改写风险提示`
- `人工确认项`
- `不能自动进入下一步`
