---
name: slbb-video-long-replica-script
description: AI 长剧 S1 对标视频复刻描述、二创描述、角色形象提取和 3-15 秒片段拆分。当用户已经提供选定的对标视频、录屏、截图、字幕或文字说明，并要求“长剧 S1”“复刻描述”“二创描述”“对标视频拆解”“长剧片段拆分”或生成 long_drama 模式的 S1 产物时使用。
---

# AI 长剧 S1：复刻描述与二创描述

## 概览

这个 skill 只在长剧选题或对标素材已经确定后使用。它把对标视频、录屏、截图、字幕、转写文本或用户笔记，整理成可交给后续 S2/S3 使用的 S1 文本资产。

这个 skill 不负责内容中台，不找每日选题，不监控平台，不给热视频打分，也不建立选题池。

## 核心规则

```text
S1 只交付复刻描述、二创描述、角色形象和片段结构。
S1 不生成视频提示词，不生成分镜提示词，不生成成片脚本。
```

## 输入

优先读取工作流已经准备好的输入：

- `artifacts/_source/source_brief.md`
- `artifacts/_source/source_manifest.json`
- 如果 `source_kind` 是 `local_video` 或 `direct_video_url`，还要读取 `artifacts/_audit/video_ingest/ingest_report.md`、`shot_index.json`、`contact_sheet.jpg` 和 `transcript.txt`

原始对标视频、录屏、截图、字幕、台词和旁白是证据，不是高频 prompt 输入。先用预处理证据包；只有在 `source_brief.md` 缺少关键点时，才回看原始材料补证据。

如果 `source_manifest.json.source_kind` 是 `platform_link`，立刻停止。要求用户先把平台视频下载或录屏成本地文件，再重新运行 `slbb-video-source` 和 `slbb-video-ingest`。

如果无法检查视频，不要编造画面事实。请用户用关键截图、字幕摘录或带时间码的笔记补齐 `source_brief.md` 的缺口。

## 工作流程

1. 写 S1 内容前，先阅读 `references/replica_description_sop.md`。
2. 阅读 `references/output_contract.md`，确认必需文件名和校验规则。
3. 读取素材包：
   - `artifacts/_source/source_brief.md`
   - `artifacts/_source/source_manifest.json`
   如果 `source_kind` 是 `local_video` 或 `direct_video_url`，还要读取 `artifacts/_audit/video_ingest/ingest_report.md` 和 `shot_index.json`。
   如果 `source_brief.md` 是空文件或仍是模板，停止并要求用户补充。不要用完整原始视频分析来替代 brief。
4. 如果要写入 run 目录，先创建 S1 骨架：
   ```bash
   python3 "skills/slbb-video-long-replica-script/scripts/scaffold_s1_run.py" <run_dir>
   ```
5. 生成原视频复刻描述报告：
   - 视频基础信息
   - 固定角色形象描述
   - 同一角色不同年龄段描述（如有）
   - 3-15 秒片段拆分总览
   - 分片段详细画面复刻描述
   - 台词 / 字幕 / 旁白汇总
   - 原视频剧情总结
6. 只有在用户提供明确二创方向，或接受默认轻二创路线后，才生成二创描述。
7. 把确认后的二创描述转成下游 S2/S3 可读的 `story_segments.json`：
   - `characters` 必须包含可用于生产的视觉锚点。
   - `characters[].name` 是标准角色 ID。除非用户明确要求改名，否则优先沿用对标素材里的角色称呼，例如 `参考人物A`、`拍摄者`、`旁观者A`。
   - 如果二创版本改变角色标签，把变化写进 `role`、`appearance`、`relationship`、`visual_anchor` 或片段描述，不要悄悄建立第二套命名系统。
   - `episodes` 中每一项代表一个 3-15 秒生产单元。
   - `episodes[].characters` 的每个值必须与顶层 `characters[].name` 完全一致。
   - 每个片段只写原视频复刻描述和二创描述，不写视频生成提示词。
8. 过程笔记、缺失证据、阻塞事项和用户确认记录放到 `_meta` 或 `_handoff`，不要写进 S1 主产物。
9. 运行校验：
   ```bash
   python3 "skills/slbb-video-long-replica-script/scripts/validate_s1_outputs.py" <run_dir>
   ```
10. 停在人工闸门。用户确认复刻描述、二创描述和片段拆分之前，不要进入 S2。

## 必需产物

```text
artifacts/S1/source_replica_description.md
artifacts/S1/second_creation_description.md
artifacts/S1/story_segments.json
artifacts/_meta/S1_replica_notes.md
```

## 主产物边界

S1 主产物可以包含：

- 原视频复刻描述
- 二创方向和二创描述
- 角色、年龄段、场景、动作、表情、情绪、台词、镜头、氛围和片段细节
- 可被 S2/S3 读取的干净 JSON

S1 主产物不得包含：

- 内容中台笔记
- 选题池或趋势评分
- 视频生成提示词
- 分镜提示词
- 成片拍摄脚本
- 封面文案
- 发布计划
- 工作流解释
- 人工闸门说明

## Token 预算规则

- 不要在聊天里粘贴或反复读取完整原始视频分析、完整转写文本或全部截图。
- 对本地视频或直链视频，读取 `video_ingest` 证据包，不要重复处理同一个视频。
- `source_brief.md` 要保持精简：30-60 秒对标视频通常控制在 1500-2500 个中文字。
- 除非用户明确同意深拆，最多使用 12 条关键时间点和 10 条关键台词 / 字幕摘要。
- 如果素材是 `partial_material`，必须把 S1 分析标为低置信度，并在继续前要求人工确认。
- 下游 S2/S3 应读取 S1 干净产物，不读取原始素材包。

## 长剧片段规则

- 按画面和剧情变化拆分，不按平均时长硬切。
- 单个片段最短 3 秒。
- 单个片段最长 15 秒。
- 2 分钟长剧通常要拆成多个 3-15 秒生产单元。
- 场景、角色、情绪、台词阶段、景别、回忆/现实边界、关键道具、冲突、反转或收尾节拍变化时，必须拆分。
- 如果同一角色跨年龄段出现，要分别列出各年龄段，并记录必须保持一致的连续性特征。
- `story_segments.json` 必须只有一套标准命名系统。不要顶层 `characters` 用原角色名，`episodes` 里又用二创角色名，反过来也不行。

## 失败模式

| 触发条件 | 必须动作 | 禁止捷径 |
| --- | --- | --- |
| 缺少 `source_manifest.json` | 写 S1 前停止，退回 `slbb-video-source`。 | 不要从聊天历史里猜素材类型。 |
| `source_kind` 是 `platform_link` | 停止，要求用户下载或录屏平台视频，再重新登记素材并 ingest。 | 不要直接分析抖音 / 小红书 / 快手 / B 站分享页。 |
| `local_video` 或 `direct_video_url` 没有 `video_ingest` 证据包 | 经用户同意后运行环境检测和 ingest。 | 不要在聊天里反复读取完整视频。 |
| `source_brief.md` 为空或仍是模板 | 要求用户补充关键时间点、角色锚点和台词证据。 | 不要用端到端读取原始视频来替代 brief。 |
| 输入只有截图、字幕、笔记或口述 | 标记为 `partial_material`，写低置信度提醒，并停在人工闸门。 | 不要把结果说成完整视频拆解。 |
| 画面证据不清楚或不可用 | 在 `artifacts/_meta/S1_replica_notes.md` 记录缺失证据，并要求补截图或时间码笔记。 | 不要编造人物外貌、镜头运动、道具或场景事实。 |
| 复刻描述和 `story_segments.json` 的角色命名不一致 | 校验前统一成一套 `characters[].name` 命名系统。 | 不要让下游 S2/S3 继承混乱命名。 |
| 任意片段短于 3 秒或长于 15 秒 | 按画面 / 剧情节拍重新拆分并重新校验。 | 不要因为故事读起来顺就保留非法片段。 |
| 校验失败 | 把校验问题保留在 `_handoff` 或 `_meta`，修复归属 S1 的产物，并重新校验。 | 不要进入 S2 或标记 S1 完成。 |

## 反模式黑名单

- 不要用这个 skill 做选题发现、热视频评分、内容中台规划或每日平台监控。
- 不要让 S1 生成视频提示词、分镜提示词、成片拍摄脚本、封面文案或发布计划。
- 不要把完整转写文本、完整视频分析、全部截图或原始过程 dump 塞进 S1 主产物。
- `artifacts/_audit/video_ingest/` 已存在时，不要重复处理同一个本地视频。
- 不要把部分截图 / 字幕 / 笔记当成完整素材证据。
- 不要编造素材包不支持的画面事实、台词、镜头语言、角色年龄段或场景道具。
- 不要在 `story_segments.json` 里混用原角色名和二创角色名。
- 必需 S1 文件存在、校验通过、且用户确认复刻描述、二创方向和片段拆分之前，不要进入 S2。

## 完成闸门

只有当所有必需产物存在、校验通过、且用户确认复刻描述、二创方向和片段拆分后，S1 才算完成。
