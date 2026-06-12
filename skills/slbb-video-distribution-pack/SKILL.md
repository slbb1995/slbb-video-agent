---
name: slbb-video-distribution-pack
description: AI 短剧 S7 分发包生成。基于 S1-S6 的剧情、成片、质检和剪辑修正结果，生成手动发布所需的标题候选、简介、抖音/视频号/小红书平台文案、封面建议、发布时间建议和发布检查清单。当用户要求“矩阵分发”“分发包”“平台文案”“发布清单”“抖音/视频号/小红书文案”，或要求 本视频工作流中的 S7 分发产物时使用。第一版只准备分发材料，不自动发布。
---

# AI 短剧 S7：分发包

## 概览

这个技能用来把确认后的短剧视频转换成手动发布包。

S7 第一版刻意保守：它只准备抖音、视频号、小红书发布材料，不登录、不上传、不定时发布，也不发布任何内容。

## 执行闸门

- 红色检查点：写正常分发包前，先确认 S5/S6 状态。如果 S5/S6 仍有阻塞问题，写 `not ready to publish` 包，并回到阻塞阶段。
- 红色检查点：任何文字要写 `手动发布` 前，必须有最终视频路径或平台草稿链接，并由人工确认。
- 红色检查点：进入 S8 复盘前，用户必须确认人工发布已经发生，或提供平台侧证据。
- 停止：如果缺少最终视频路径，S7 只能产出阻塞版发布检查清单；不要像视频已准备好一样生成平台文案。
- 停止：如果用户要求这个技能上传、定时、抓后台或标记数据，停止并转为人工发布；有发布证据后再进 S8。

## 输入

优先使用工作流产物：

```text
artifacts/S1/story_extract.md
artifacts/S3/motion_prompt_pack.md
artifacts/S4/generation_run_log.md
artifacts/S5/qc_report.md
artifacts/S5/qc_verdict.json
artifacts/S6/edit_fix_plan.md
artifacts/S6/edit_checklist.md
```

也可以接受：

- 最终视频文件路径或平台草稿链接
- 封面帧或截图
- 用户关于目标账号、目标受众和发布时间的说明
- 平台列表，默认抖音、视频号、小红书

## 工作流程

1. 创建 S7 骨架：
   ```bash
   python3 "skills/slbb-video-distribution-pack/scripts/scaffold_s7_run.py" <run_dir>
   ```
2. 读取已确认的 S1-S6 产物，识别最终视频、故事钩子、目标受众、质检状态和剩余风险说明。
3. 按 `references/platform_pack_standard.md` 写各平台文案。
4. 写入或更新：
   - `artifacts/S7/distribution_pack.md`
   - `artifacts/S7/platform_copy.md`
   - `artifacts/S7/publish_checklist.md`
   - 可选过程记录：`artifacts/_meta/S7_distribution_notes.md`
5. 需要时插入一个平台文案块：
   ```bash
   python3 "skills/slbb-video-distribution-pack/scripts/add_platform_copy.py" <run_dir> --platform 抖音 --title "标题候选" --caption "正文文案" --hashtags "#短剧 #AI" --cover "封面建议" --publish-time "今晚 20:00-22:00"
   ```
6. 验证：
   ```bash
   python3 "skills/slbb-video-distribution-pack/scripts/validate_s7_outputs.py" <run_dir>
   ```
7. 停在人工闸门。不要声称视频已经发布。

从包根目录运行上述命令；如果只拿到了单独 skill 目录，则改用该 skill 目录内的相对脚本路径。

## 失败模式

| 触发情况 | 必须动作 | 禁止的偷懒做法 |
| --- | --- | --- |
| 缺少最终视频路径或草稿链接 | 写阻塞版 `publish_checklist.md`，并要求提供最终视频/草稿链接。 | 编造视频路径，或产出暗示视频已准备好的文案。 |
| S5 结论为 reject/blocking | 标记 `暂不建议发布`，并回到 S5/S6。 | 把包润色成可发布版本。 |
| 有 S6 修正方案，但未确认已剪辑视频 | 保持状态为 `未发布 / 待人工修正确认`。 | 声称修正版已经是最终版。 |
| 用户要求自动上传/定时/发布 | 说明 S7 只准备手动发布材料。 | 登录、上传、定时或声称平台动作已完成。 |
| 用户要求立刻进入 S8 | 要求手动发布证据或明确用户确认。 | 从未发布包生成复盘输出。 |
| 平台文案改变剧情事实 | 恢复 S1-S6 的剧情、关系和结尾。 | 为了追点击改写故事。 |
| 账号权限、审核状态或流量预测未知 | 标为 `人工检查`。 | 编造算法、权限、审核或表现结论。 |
| 主输出包含工作流/过程说明 | 把说明移到 `publish_checklist.md` 或 `_meta/S7_distribution_notes.md`。 | 把路线判断或人工闸门话术放进平台文案。 |

## 规则

- S7 只产出分发包。第一版绝不自动发布。
- 始终把发布状态标为 `未发布 / 手动发布 / 不自动发布`。
- 除非用户提供平台侧确认，否则不要说“已发布”“已上传”或“已定时发布”。
- 不要编造平台表现数据、算法规则、账号权限或合规结论。
- 如果 S5/S6 仍有阻塞问题，创建“暂不建议发布”包，并回到 S5/S6。
- 标题候选要具体、围绕故事，不要写成泛泛的 AI 教程味。
- 平台文案要保留含义：不要为了追点击改变剧情、人物关系或结尾。
- 每个平台块都必须包含标题、正文/说明、话题标签、封面建议和发布时间建议。
- 风险说明和人工审查说明放到 `publish_checklist.md` 或 `_meta`，不要放进平台文案。

## 反模式黑名单

- 除非用户提供平台侧确认，否则不要说 `已发布`、`已上传`、`已定时发布` 或 `发布完成`。
- 不要把 `S7 分发包完成` 等同于 `平台发布完成`。
- 没有实际发布证据，不要继续进入 S8 复盘。
- 不要用 S7 修复 S5/S6 的阻塞问题；要回到对应阶段。
- 不要编造最终视频路径、账号权限、平台审核结果、流量预测或评论数据。
- 最终 S7 产物不要包含 `TODO`、`待填写` 或 `待补充`。
- 不要在 `platform_copy.md` 里包含工作流理由、输入来源块或人造人工确认话术。
- 不要为标题党改变剧情事实、人物关系或结尾细节。

## 平台范围

第一版默认平台：

- 抖音：强钩子、短标题、短正文、话题标签、封面标题。
- 视频号：更直接、更像真实转述，强调故事冲突和评论引导。
- 小红书：笔记感标题、封面字、正文分段、标签。

详细要求见 `references/platform_pack_standard.md`。

## 必需输出

```text
artifacts/S7/distribution_pack.md
artifacts/S7/platform_copy.md
artifacts/S7/publish_checklist.md
```

见 `references/output_contract.md`。

S7 主输出是给客户看的发布材料，不应包含工作流推理、输入来源块或人造人工确认话术。

## 完成闸门

只有三个必需输出都存在、验证通过，并且用户确认手动发布或修订分发包时，S7 才算完成。它不等于已经发布。
