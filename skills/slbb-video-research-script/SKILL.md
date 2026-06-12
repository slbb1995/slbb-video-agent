---
name: slbb-video-research-script
description: AI 短剧/长剧 S1 调研、剧情提取、剧情拆分、15 秒短视频分集拆解、人物关系整理和版权/改写风险提示。当用户提供短剧名称、平台、原始故事、剧本、梗概、飞书/Markdown 素材，或要求“短剧调研”“剧情提取”“拆分剧情”“生剧情提示词”“版权筛查”“改写成 AI 短视频剧情”，以及为 slbb-video 工作流准备 S1 产物时使用。
---

# AI 短剧 S1：调研与剧情提取拆分

## 概览

这个技能用来把短剧名称、平台、原始剧情、剧本或调研笔记，转换成 S1 工作流产物，供后续图片提示词和视频提示词技能使用。

S1 不做下游 S2/S3 的工作。S1 只产出干净的故事结构和 15 秒分集片段，供 S2 使用。调研笔记、改写/版权风险、确认说明要放在 `_meta` 或 `_handoff`，不要放进 S1 主输出。

## 执行闸门

- 红色检查点：写 S1 主输出之前，先把来源标记为 `researched`、`provided` 或 `inferred`。
- 红色检查点：决定 15 秒片段数量之前，必须完成来源覆盖审计，并写入 `artifacts/_meta/S1_segmentation_decision.md`。
- 红色检查点：S1 完成前，每个核心角色都必须有可用于 S2 三视图参考图的外貌锚点。
- 红色检查点：进入 S2 前，必须由用户确认剧情提取和分集拆分。
- 停止：如果素材太薄，无法识别核心人物、核心场景和至少一集内容，写阻塞 handoff，不要编造完整故事。
- 停止：如果要压缩整季短剧，但来源覆盖不足以支撑整季拆分，把输出标记为“推断样本”或要求补充素材，不要随手选一个固定集数。
- 停止：如果基于有版权的来源素材，主输出不要放长段原文或台词，只在 `_meta` 记录改写风险。

## 工作流程

1. 确认输入类型：
   - **V2 handoff（最高优先级）**：如果 `workflow_state.json.source.v2_video_url` 非空，说明这个 run 是通过 `bin/slbb-video-from-handoff` 导入的。把 handoff 当作主来源读取。`source.title` 是原始对标视频标题；`source.matched_rules` 是监控规则；`source.manual_note` 是人工上下文；`source.v2_metrics` 只作参考。
   - 短剧名称 + 平台：如果工具可用就做调研，并把缺少证据支撑的细节标记为 inferred。
   - 原始故事/剧本/梗概：把用户提供文本作为主来源。
   - 已存在的 S1 run 目录：编辑前先检查现有产物。
2. 拆分前先做来源覆盖审计：
   - 原剧总集数，如果已知。
   - 已收集素材数量和素材类型：官方梗概、分集列表、完整字幕、平台片段、用户笔记，或只有搜索摘要。
   - 已验证剧情覆盖范围与推断/重构范围。
   - 素材里已经找到的主要叙事弧和有效短视频钩子。
   - 动态目标片段数，以及为什么这个数量适合当前素材。
3. 写文件时，先运行 `scripts/scaffold_s1_run.py` 创建 S1 产物骨架。
4. 只读取必要参考：
   - `references/research_prompt.md`：已验证的飞书调研提示词。
   - `references/decomposition_framework.md`：标准剧情拆解模板。
   - `references/output_contract.md`：必需文件名和验证规则。
5. 产出这些必需文件：
   - `artifacts/S1/story_extract.md`
   - `artifacts/S1/story_segments.json`
   - `artifacts/_meta/S1_segmentation_decision.md`
   - 可选过程记录：`artifacts/_meta/S1_research_notes.md` 或 `artifacts/_handoff/S1_human_confirmation_card.md`
6. 声称 S1 完成前，运行 `scripts/validate_s1_outputs.py <run_dir>`。
7. 停在人工闸门。用户确认剧情提取和拆分之前，不要继续进入 S2。

## 产物规则

- 产物写入 run 目录，不要写进 skill 目录。
- 优先使用用户提供的 run 目录。没有提供时，使用当前工作目录。
- 不要在生成的技能逻辑里写死用户专属绝对路径。
- 清晰区分已验证事实、推断细节和为改写而原创的内容。
- 不要按习惯或模板决定压缩片段数。要根据来源覆盖、原始集数、剧情密度、叙事弧数量和可用 15 秒钩子决定，并记录到 `_meta/S1_segmentation_decision.md`。
- S1 要为 S2 准备视觉锚点：每个核心人物都应包含足够稳定的外貌细节，供生成“一张图三视图”角色参考图，包括脸、发型、体型、服装、鞋、配饰和整体视觉气质。
- 对已知版权作品，不要复现长段原剧情或台词。要总结、转化，并创作原创 15 秒改编片段。
- 分集脚本里把原角色名替换成中性名称，例如 `小美`、`小刚`、`小秦`；原名只保留在人物调研章节里。
- 主输出必须干净。不要把工作流原则、版本说明、风险分析或人工确认话术写进 `story_extract.md` 或 `story_segments.json`。

## S1 最小输出

`story_extract.md` 必须包含：

- 一句话总结
- 核心人物
- 核心场景
- 分集列表
- 给 S2 的下一阶段输入

S2 输入章节必须说明哪些人物需要“一张图三视图”参考图，哪些场景需要空场景参考图。

`artifacts/_meta/S1_segmentation_decision.md` 必须包含：

- source_type：`researched`、`provided` 或 `inferred`
- original_episode_count：原始集数，如果已知
- collected_source_count：已收集素材数量和类型
- coverage_level：high / medium / low
- target_segment_count：`story_segments.json` 中 15 秒单元的准确数量
- decision_basis：为什么这个数量适合当前来源覆盖和剧情密度
- boundary：整季重构、压缩改编、样本级推断拆分，或 blocked

`story_segments.json` 必须包含顶层 `characters` 数组。每个角色必须包含：

- `name`
- `role`
- `appearance`
- `relationship`
- `visual_anchor`

`visual_anchor` 必须包含脸、发型、体型、服装、鞋、配饰和气质，用于 S2 三视图角色参考图生成。

`story_segments.json` 必须包含顶层 `episodes` 数组。每集必须包含：

- `episode_id`
- `episode_name`
- `scene`
- `characters`
- `props`
- `timeline`
- `review`

`timeline` 必须包含三个节拍：

- `0-2s`
- `3-10s`
- `11-15s`

每个节拍都必须包含镜头语言、身体动作和台词/声音。不要把台词/声音留空。

人工确认说明可以写到 `artifacts/_handoff/S1_human_confirmation_card.md`，但这个文件只是过程辅助，不是 S1 主输出。

## 失败模式

| 触发情况 | 必须动作 | 禁止的偷懒做法 |
| --- | --- | --- |
| 短剧名称/平台无法调研 | 把缺失事实标为 `inferred`，并要求补充来源素材或用户确认。 | 把推断剧情说成已验证来源。 |
| 已知原始集数，但来源覆盖很薄 | 写覆盖审计，选择样本级拆分，或阻塞等待更多素材。 | 因为 8、16、20 看起来合理就直接选。 |
| 用户质疑压缩片段数 | 回到 S1，修订 `S1_segmentation_decision.md`，再更新 `story_segments.json`。 | 继续沿用依赖旧拆分的 S2/S3 产物。 |
| 原始故事缺少角色外貌 | 只补生产所需的视觉锚点，并在 `_meta/S1_research_notes.md` 记录为推断。 | 让 S2 缺少脸、头发、体型、服装、鞋、配饰和气质锚点。 |
| 来源有版权或过于接近现有短剧 | 总结、转化、改名，并把风险说明放出主输出之外。 | 复制长段剧情或台词原文。 |
| 分集无法支撑 15 秒 | 在 `_meta` 标记 blocked，或说明拆分/合并原因。 | 强行写三个空时间节拍。 |
| `story_segments.json` 验证失败 | 先修 JSON 结构，再请求人工确认。 | 带着无效 JSON 继续进入 S2。 |
| 用户要求直接跳到图片/视频提示词 | 先完成 S1 产物和人工闸门。 | 在 S1 里直接调用 S2/S3。 |

## 反模式黑名单

- 不要隐藏细节是已验证、推断，还是为了改编原创。
- 不要在没有来源覆盖审计的情况下，把长剧压缩成固定数量的 15 秒单元。
- 不要把结构验证通过当作来源覆盖和拆分数量正确的证明。
- 不要把版权分析、来源限制或人工闸门话术写进 `story_extract.md` 或 `story_segments.json`。
- 不要让任何核心角色缺少给 S2 使用的视觉锚点。
- 需要改编中性名时，不要在分集脚本里保留原角色名。
- 不要在 S1 里产出 S2 图片提示词或 S3 生视频提示词。
- 不要因为故事听起来合理就标记 S1 完成；必须通过验证并取得用户确认。
- 不要创建空的 `dialogue_or_sound` 节拍。

## 命令

创建 run 骨架：

```bash
python3 "$CODEX_SKILLS_ROOT/slbb-video-research-script/scripts/scaffold_s1_run.py" <run_dir>
```

如果没有设置 `CODEX_SKILLS_ROOT`，把它替换成本地 skills 根目录。

验证输出：

```bash
python3 "$CODEX_SKILLS_ROOT/slbb-video-research-script/scripts/validate_s1_outputs.py" <run_dir>
```

## 完成闸门

只有两个必需的干净产物都存在、验证通过，并且用户确认剧情闸门时，S1 才算完成。S1 放行是人工决策，不是模型自动决策。
