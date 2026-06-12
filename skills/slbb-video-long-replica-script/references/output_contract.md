# 长剧 S1 输出契约

S1 把一个已选定的对标视频或用户提供的素材包，整理成干净的复刻描述和二创描述。S1 不是选题工作台，也不是提示词生成阶段。

## 必需目录

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

必须使用以下结构：

```markdown
# AI短视频复刻描述提取报告

## 1. 视频基础信息
## 2. 固定角色形象描述
## 3. 视频片段拆分总览
## 4. 分片段详细画面描述
## 5. 台词 / 字幕 / 旁白汇总
## 6. 原视频剧情总结
```

这个文件只描述原始对标素材。不得包含二创执行笔记、工作流笔记或视频生成提示词。

## second_creation_description.md

必须使用以下结构：

```markdown
# 二次创作版复刻描述

## 1. 本次二创方向
## 2. 二创后角色形象描述
## 3. 二创后片段拆分总览
## 4. 二创后分片段详细画面描述
```

这个文件保留原始结构，但在已确认边界内做原创化调整。

## story_segments.json

顶层对象：

```json
{
  "characters": [],
  "episodes": []
}
```

每个角色必须包含：

- `name`
- `role`
- `appearance`
- `relationship`
- `visual_anchor`

`visual_anchor` 必须包含：

- `face`
- `hair`
- `body`
- `costume`
- `shoes`
- `accessories`
- `temperament`

推荐补充的长剧角色字段：

- `age_stage`
- `same_person_group`
- `continuity_anchor`
- `production_alias`

`name` 是下游 S2/S3 使用的标准角色 ID。除非用户明确要求改名，否则优先使用对标素材里的角色称呼。若二创版本改变了角色标签，把变化写入 `production_alias`、`role`、`appearance` 或片段描述；不要让顶层角色和片段角色使用两套命名系统。

每个片段必须包含：

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

`timeline` 必须是非空对象。每个节拍建议包含：

- `camera`
- `action`
- `dialogue_or_sound`

`episodes[].characters` 的每个值必须与顶层 `characters[].name` 完全一致。如果某个片段需要群体角色，例如 `路人群体`、`学生群体` 或 `工作人员群体`，要把它作为顶层角色 / 群体条目并补充视觉锚点；也可以把它移到 `props` 或场景描述里，不要塞进 `characters` 后破坏校验。

## 干净输出规则

S1 主产物不得包含：

- 内容中台或选题池笔记
- 趋势评分
- 视频生成提示词
- 分镜提示词
- 成片拍摄脚本
- 封面文案
- 发布计划
- 工作流解释
- 人工确认文字

素材限制、缺失证据、用户确认记录和阻塞事项统一放入 `artifacts/_meta/S1_replica_notes.md`。
