---
name: slbb-video-review
description: AI 短剧 S8 发布后复盘。读取抖音、视频号、小红书等平台的播放、点赞、评论、转发、收藏、完播、留存和用户反馈，输出复盘报告、问题归因、下一轮选题建议和提示词/生成/剪辑/分发调整计划。当用户要求“短剧复盘”“发布后数据分析”“播放点赞转发留存复盘”“下一轮怎么改”，或要求 slbb-video 工作流中的 S8 复盘产物时使用。
---

# AI 短剧 S8：发布后复盘

## 概览

这个技能用来把发布后的表现数据转换成具体的下一轮迭代计划。

当前稳定输入模式：`screenshot_csv`。

这一版 S8 不登录平台后台，不操作 Chrome，也不自动抓取抖音、视频号、小红书后台。用户提供平台截图、CSV 导出、评论样本或手动录入的数据。技能解析这些已提供素材，记录证据，再写复盘。

S8 不是泛泛总结。它必须把数据反接回上游工作流决策：选题、剧情、图片提示词、生视频提示词、生成、质检、剪辑和分发。

## 执行闸门

- 红色检查点：写 S8 前，确认视频已经人工发布，或用户提供了发布后数据。
- 红色检查点：做结论前，至少附上一类证据：数据行、截图/CSV 路径、评论样本，或 S1-S7 产物引用。
- 红色检查点：开始下一轮 run 前，用户必须确认下一轮选题方向或具体修改清单。
- 停止：如果没有平台数据、截图、CSV、评论样本或手动数据，写阻塞版复盘 handoff，不要写表现复盘。
- 停止：如果用户要求后台抓取或登录态后台截图，转到未来的 `browser_assisted` 工作，并先要求提供截图/CSV。

## 输入

优先使用工作流产物：

```text
artifacts/S1/story_extract.md
artifacts/S2/image_prompt_pack.md
artifacts/S3/motion_prompt_pack.md
artifacts/S4/generation_run_log.md
artifacts/S5/qc_report.md
artifacts/S6/edit_fix_plan.md
artifacts/S7/distribution_pack.md
artifacts/S7/platform_copy.md
artifacts/S7/publish_checklist.md
```

也可以接受：

- 平台数据：播放、点赞、评论、转发、收藏、完播率、留存、发布时间
- 平台截图或 CSV 导出
- 评论样本和用户反馈
- 标题、封面、账号、发布时间、流量来源等人工说明

稳定模式契约：

- `screenshot_csv`：用户提供截图和/或 CSV 导出。默认使用，也是当前唯一生产支持的 S8 模式。
- `browser_assisted`：尚未启用。不要在本技能中打开登录态平台后台，也不要声称已经自动抓取后台。

## 工作流程

1. 创建 S8 骨架：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-review/scripts/scaffold_s8_run.py" <run_dir>
   ```
2. 记录平台数据。可以添加一行数据：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-review/scripts/add_metric_row.py" <run_dir> --platform 抖音 --views 1200 --likes 80 --comments 12 --shares 5 --saves 9 --completion-rate 23.5 --retention "3s=61%, 5s=43%" --feedback "开头能看懂，但反转不够强"
   ```
   或导入 CSV：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-review/scripts/ingest_metric_csv.py" <run_dir> <csv_path> --source "抖音后台导出"
   ```
3. 读取 S1-S7 产物，把数据和每个上游决策对照。
4. 如果提供截图，把截图保存或引用到 `artifacts/S8/evidence/` 下，并写一条简短证据说明，列出每张截图、可读数据、评论样本和置信度。除非确实能从截图中读出，不要 OCR 或推断不可见数据。
5. 写入：
   - `artifacts/S8/review_report.md`
   - `artifacts/S8/next_iteration_plan.md`
6. 验证：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-review/scripts/validate_s8_outputs.py" <run_dir>
   ```
7. 停在人工闸门。用户确认下一轮选题方向和具体修改后，再开始下一轮。

如果没有设置 `CODEX_SKILLS_ROOT`，把它替换成本地 skills 根目录。

## 规则

- 不要写模糊复盘话术。每个结论都要有数据点、评论样本或工作流产物作为证据。
- 数据缺失就标记缺失并降低置信度。不要编造指标。
- 始终区分平台表现问题和生产流程问题。
- 始终包含上游归因：选题、剧情、图片提示词、视频提示词、生成、质检、剪辑、发布。
- 下一轮计划必须明确写出改什么，以及如何验证。
- 不要把单条视频当成统计证明。样本少的结论要标为暂定。
- 用户确认下一轮方向之前，不要进入新的 S1 run。
- 这一版不要使用用户长期浏览器登录态做 S8。如果用户要求后台截图，先要求截图/CSV，或明确转到未来 `browser_assisted` 升级。
- 对截图，始终记录什么能直接看见，什么看不见。如果某个指标被裁掉、模糊、隐藏或不可读，标记为缺失。
- 对 CSV 导出，在报告里保留原始 CSV 路径，并把指标规范化到 S8 复盘表。

## 复盘维度

写报告时读取 `references/review_standard.md`。

最小维度：

- 平台数据：播放、点赞、评论、转发、收藏、完播、留存
- 用户反馈：评论主题、反对点、看不懂的地方、情绪反应
- 内容诊断：钩子、冲突、反转、角色清晰度、节奏
- 工作流诊断：提示词质量、生成失败、质检遗漏、剪辑问题、分发包装
- 下一轮修改：选题、剧情、图片提示词、生视频提示词、生成设置、剪辑、平台文案

## 失败模式

| 触发情况 | 必须动作 | 禁止的偷懒做法 |
| --- | --- | --- |
| 有 S7 分发包，但没有发布证据 | 停止并要求人工发布确认或平台侧证据。 | 把未发布包当作已发布内容复盘。 |
| 指标缺失或被裁切 | 把字段标为 `缺失` 并降低置信度。 | 推断隐藏数值。 |
| 只有一条低样本视频 | 标记结论为暂定。 | 把一个样本说成统计证明。 |
| 用户要求自动后台抓取 | 要求截图/CSV，或转到未来 `browser_assisted`。 | 在 S8 使用登录态浏览器。 |
| 没有评论 | 把用户反馈缺失和平台数据分开。 | 编造评论主题。 |
| 下一轮计划缺少证据或验证方法 | 改写成“问题/证据/修改/验证”格式。 | 输出泛泛的“继续优化”。 |

## 反模式黑名单

- 不要编造播放、点赞、评论、转发、完播、留存或用户反馈。
- 不要在没有证据时，把表现过度归因到某一个上游环节。
- 不要隐藏缺失数据或置信度。
- 不要在 S8 未经用户确认就开启新的 S1 run。
- 这一版不要登录平台后台或抓取后台数据。
- 不要输出没有数据、评论或产物证据的模糊复盘话术。

## 必需输出

```text
artifacts/S8/review_report.md
artifacts/S8/next_iteration_plan.md
```

见 `references/output_contract.md`。

## 完成闸门

只有复盘报告和下一轮计划都存在、验证通过，并且用户确认下一轮选题方向或修改清单时，S8 才算完成。
