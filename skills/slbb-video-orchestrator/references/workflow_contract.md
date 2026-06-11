# AI 视频 S1-S8 工作流契约

## 总原则

- 总控只负责流程推进，不负责生成每个阶段的专业内容。
- 工作流支持 `short_drama` 和 `long_drama` 两种 mode。没有 `mode` 的旧状态文件按 `short_drama` 处理。
- `long_drama` 不包含内容中台、选题池、热点监控或每日推送；它从已确定的对标视频/素材开始。
- `long_drama` 的原始视频、录屏、截图和字幕只作为证据来源；高频输入是 `artifacts/_source/source_brief.md`、`artifacts/_source/source_manifest.json` 和 `artifacts/_audit/video_ingest/`。
- 长剧本地视频/直链视频必须先运行 `slbb-video-ingest`；平台链接必须先下载或录屏成本地视频；缺素材时先补 brief 或走 `partial_material` 降级路径。
- 长剧 S1 不要重复读取完整视频、长字幕、逐帧分析或整包过程文件。
- 每个阶段必须先由对应 Skill 生成产物。
- 每个阶段必须经过校验和人工确认，才能进入下一阶段。
- 任何阶段失败，都回到该阶段或更上游阶段，不在总控里硬补内容。
- 主产物必须是干净交付：只保留下一阶段或人工执行会直接使用的内容。
- Workflow 原则、版本说明、输入来源、推导风险、校验依据、人工确认话术，放到 `artifacts/_meta/`、`artifacts/_audit/` 或 `artifacts/_handoff/`，不要混进 S1-S7 主产物。
- 下一阶段读取上一阶段的干净主产物，而不是读取整包过程文件。
- S1 必须先完成素材覆盖度审计和动态分集数量决策，写入 `artifacts/_meta/S1_segmentation_decision.md`；不能先固定 8/16/20 个 15 秒单元再倒推剧情。
- S1/S2 可以面向整条短剧准备剧情、人物和场景底座；S2 之后默认以单个 episode/clip 为最小推进单元。
- S3 默认只生成当前目标 episode/clip 的视频提示词，通常从 `001` 开始。不要因为 S2 包含全量人物和场景，就在 S3 一次生成所有 episode/clip。
- 单集闭环顺序是 `001: S3 -> S4 -> S5 -> S6 -> S7 -> S8`，该集复盘和人工确认后，再进入 `002: S3 -> S4 -> S5 -> S6 -> S7 -> S8`。
- S2 完成后，总控必须从 `artifacts/S1/story_segments.json` 初始化 `workflow_state.json.segment_state`，并把第一个未完成片段写入 `current_segment`。
- S8 完成当前片段后，总控必须把该片段的 S3-S8 产物归档到 `artifacts/_segments/<segment_id>/`，再重置 S3-S8 阶段状态并进入下一个片段。
- 只有用户明确要求批量覆盖时，才允许一次处理多个 episode/clip；此时必须把目标范围写进 `_handoff` 或 `_meta`，不要静默批量推进。

## 阶段表：short_drama

| 阶段 | Skill | 必须产物 | 人工闸门 |
| --- | --- | --- | --- |
| S1 | `slbb-video-research-script` | `artifacts/S1/story_extract.md`; `artifacts/S1/story_segments.json` | `human_confirm_story` |
| S2 | `slbb-video-image-prompts` | `artifacts/S2/image_prompt_pack.md` | `human_confirm_image_prompts` |
| S3 | `slbb-video-motion-prompts` | `artifacts/S3/motion_prompt_pack.md`; `artifacts/S3/platform_copy_ready_prompts.md` | `human_confirm_motion_prompts` |
| S4 | `slbb-video-generation-log` | `artifacts/S4/generation_run_log.md`; `artifacts/S4/generation_run_log.csv` | `human_select_video_version` |
| S5 | `slbb-video-qc` | `artifacts/S5/qc_report.md`; `artifacts/S5/qc_verdict.json`; `artifacts/S5/rework_suggestions.md` | `human_confirm_qc` |
| S6 | `slbb-video-edit-fix` | `artifacts/S6/edit_fix_plan.md`; `artifacts/S6/edit_checklist.md` | `human_confirm_edit` |
| S7 | `slbb-video-distribution-pack` | `artifacts/S7/distribution_pack.md`; `artifacts/S7/platform_copy.md`; `artifacts/S7/publish_checklist.md` | `human_confirm_publish_pack` |
| S8 | `slbb-video-review` | `artifacts/S8/review_report.md`; `artifacts/S8/next_iteration_plan.md` | `human_confirm_review` |

## 阶段表：long_drama

| 阶段 | Skill | 必须产物 | 人工闸门 |
| --- | --- | --- | --- |
| S1 | `slbb-video-long-replica-script` | `artifacts/S1/source_replica_description.md`; `artifacts/S1/second_creation_description.md`; `artifacts/S1/story_segments.json`; `artifacts/_meta/S1_replica_notes.md` | `human_confirm_replica_description` |
| S2 | `slbb-video-image-prompts` | `artifacts/S2/image_prompt_pack.md` | `human_confirm_image_prompts` |
| S3 | `slbb-video-motion-prompts` | `artifacts/S3/motion_prompt_pack.md`; `artifacts/S3/platform_copy_ready_prompts.md` | `human_confirm_motion_prompts` |
| S4 | `slbb-video-generation-log` | `artifacts/S4/generation_run_log.md`; `artifacts/S4/generation_run_log.csv` | `human_select_video_version` |
| S5 | `slbb-video-qc` | `artifacts/S5/qc_report.md`; `artifacts/S5/qc_verdict.json`; `artifacts/S5/rework_suggestions.md` | `human_confirm_qc` |
| S6 | `slbb-video-edit-fix` | `artifacts/S6/edit_fix_plan.md`; `artifacts/S6/edit_checklist.md` | `human_confirm_edit` |
| S7 | `slbb-video-distribution-pack` | `artifacts/S7/distribution_pack.md`; `artifacts/S7/platform_copy.md`; `artifacts/S7/publish_checklist.md` | `human_confirm_publish_pack` |
| S8 | `slbb-video-review` | `artifacts/S8/review_report.md`; `artifacts/S8/next_iteration_plan.md` | `human_confirm_review` |

## 状态推进

允许状态：

- `pending`
- `in_progress`
- `ready_for_human`
- `completed`
- `blocked`

正常顺序：

```text
pending -> in_progress -> ready_for_human -> completed
```

只有用户确认后，才能从 `ready_for_human` 进入 `completed`。

## 失败模式与兜底

| 触发条件 | 必须动作 | 禁止动作 |
| --- | --- | --- |
| 找不到 `workflow_state.json` | 先运行 `init_run.py` 或要求用户提供正确目录 | 不根据目录里的散文件脑补当前阶段 |
| 长剧请求包含内容中台/每日选题 | 说明内容中台是外部输入源，当前 S1-S8 从已选对标视频开始 | 不把选题池、热点监控塞进 S1 |
| 长剧请求粘贴完整视频分析/长字幕/逐帧拆解 | 先运行 `slbb-video-source` 和 `slbb-video-ingest`，要求把素材压成 source brief + video_ingest 证据包 | 不让总控或 S1 直接吞完整大素材 |
| 长剧素材是抖音/小红书等平台链接 | 先让用户下载/录屏成本地视频，再重新 source + ingest | 不让 S1 直接分析平台分享链接 |
| 长剧素材只有截图/字幕/口述 | 用 `partial_material` 登记，并在 S1 标低置信度 | 不伪装成完整视频拆解 |
| state JSON 损坏、缺 stage 或顺序异常 | 运行 `validate_orchestrator_state.py`，报告具体错误并停止推进 | 不手工猜测并改写阶段顺序 |
| 用户要求一次跑完 S1-S8 | 只返回下一步 handoff，并说明总控一次只推进一个阶段或一个 post-S2 片段 | 不在一个模型回复里生成全流程产物 |
| S1 分集数量被质疑，或原剧总集数与已抓素材边界不清 | 回到 S1，补/改 `S1_segmentation_decision.md`，重新校验；旧 S2/S3 产物必须归档或重跑 | 不继续沿用旧分集数量生成图片或视频提示词 |
| S2 后用户要求批量处理所有片段 | 要求用户明确 episode/clip 范围；没有范围时默认继续第一个未完成片段 | 不静默把所有剩余片段批量推进 |
| 必须产物缺失 | 保持当前阶段打开，回到该阶段 skill 补产物 | 不标记 `ready_for_human` 或 `completed` |
| 阶段 validator 失败 | 把 validator 输出写进 handoff/notes，状态不前进 | 不为了继续流程而跳过错误 |
| 缺少人工确认 | 保持 `gate_status=pending/waiting`，等待用户明确确认 | 不替用户追加 `--human-confirmed` |
| 主产物混入过程说明 | 移到 `_meta`、`_audit` 或 `_handoff` | 不把污染后的主产物交给下一阶段 |

## 防偷懒机制

- 阶段产物分文件保存。
- 校验脚本检查空骨架和缺字段。
- 总控状态文件记录当前阶段，不能一次跳过多个阶段。
- S1 校验必须覆盖 `S1_segmentation_decision.md`，并确认其中 `target_segment_count` 与 `story_segments.json` 的分集数量一致。
- S2 之后总控状态和 handoff 必须写清当前目标 episode/clip；没有目标片段时，默认选择 `story_segments.json` 中第一个未完成片段。
- S3-S8 主工作区只保存当前片段的活跃产物；已完成片段从 `artifacts/_segments/<segment_id>/` 读取。
- 人工闸门作为硬门槛，不靠模型自称完成。

## 干净输出规则

S1-S7 的主产物面向两个读者：下一阶段 Skill 和人工执行者。主产物里不要写给总控看的过程解释。

主产物允许：

- 剧情结构、人物、场景、分集、提示词、平台复制文案、生成记录、质检结论、剪辑动作、发布文案。
- 必要的执行字段，例如文件路径、平台、时长、画幅、标题、正文、标签、检查项。

主产物禁止：

- `Workflow` / `workflow` 原则说明。
- `V2 原则`、版本策略、为什么这样设计的长解释。
- `输入来源`、`路由模式`、`推导与风险备注`、`人工确认项` 这类过程字段。
- 面向 Codex 的下一步话术或人工闸门解释。

这些过程信息应放到：

```text
artifacts/_meta/S1_research_notes.md
artifacts/_meta/S2_prompt_notes.md
artifacts/_meta/S3_motion_design_notes.md
artifacts/_audit/S4_attempt_notes.md
artifacts/_audit/S5_review_notes.md
artifacts/_audit/S6_edit_log.md
artifacts/_meta/S7_distribution_notes.md
artifacts/_handoff/next_step.md
```
