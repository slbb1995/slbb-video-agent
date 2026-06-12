# 干净输出契约

本契约适用于 `slbb-video` 工作流中 S1-S7 的主输出。

## 为什么需要这个契约

这个工作流有三类读者：

- 下一阶段技能需要紧凑、准确的输入。
- 人工操作者需要可复制提示词、日志、质检结论、剪辑动作或发布文案。
- 总控需要过程状态、闸门、记录和验证证据。

不要把三类读者都塞进同一个 Markdown 文件。阶段主输出只服务前两类读者。过程状态应放在 `_meta`、`_audit` 或 `_handoff`。

## 目录规则

```text
artifacts/S1..S7/      干净主交付物
artifacts/_meta/       设计记录、来源记录、风险记录、路由决策
artifacts/_audit/      执行日志、质检证据、剪辑日志
artifacts/_handoff/    下一步执行卡和人工闸门卡
workflow_state.json    状态真相源
```

## 主输出规则

主文件应能被下一阶段或人工操作者直接使用。

允许包含：

- 故事总结、人物、场景、分集节拍。
- 图片提示词、视频提示词、平台复制版提示词。
- 生成记录和选中视频路径。
- 质检结论、问题证据、归因、返工动作。
- 剪辑方案、剪辑清单、发布包、平台文案。

S1-S7 主文件禁止包含：

- `Workflow` / `workflow` 原则。
- `V2 原则`、版本策略或长篇设计理由。
- `输入来源`、`路由模式`、`推导与风险备注`、`人工确认项`。
- `使用说明`、`合规与改写备注`、`时长判断`、`关键道具与文字风险`。
- 人工闸门解释，例如 `不能自动进入下一步`。

## 阶段映射

| 阶段 | 干净主输出 | 过程/元数据输出 |
| --- | --- | --- |
| S1 | `artifacts/S1/story_extract.md`; `artifacts/S1/story_segments.json` | `_meta/S1_research_notes.md`; `_handoff/S1_human_confirmation_card.md` |
| S2 | `artifacts/S2/image_prompt_pack.md` | `_meta/S2_prompt_notes.md` |
| S3 | `artifacts/S3/motion_prompt_pack.md`; `artifacts/S3/platform_copy_ready_prompts.md` | `_meta/S3_motion_design_notes.md` |
| S4 | `artifacts/S4/generation_run_log.md`; `artifacts/S4/generation_run_log.csv` | `_audit/S4_attempt_notes.md` |
| S5 | `artifacts/S5/qc_report.md`; `artifacts/S5/qc_verdict.json`; `artifacts/S5/rework_suggestions.md` | `_audit/S5_review_notes.md` |
| S6 | `artifacts/S6/edit_fix_plan.md`; `artifacts/S6/edit_checklist.md` | `_audit/S6_edit_log.md` |
| S7 | `artifacts/S7/distribution_pack.md`; `artifacts/S7/platform_copy.md`; `artifacts/S7/publish_checklist.md` | `_meta/S7_distribution_notes.md` |

## 链路规则

每个阶段应优先读取上一阶段的干净主输出。

示例：

- S2 读取 S1 的 `story_extract.md` 和 `story_segments.json`，不读取 S1 调研笔记。
- S3 读取 S2 的 `image_prompt_pack.md`，不读取 S2 路由/风险记录。
- S4 使用 S3 的 `platform_copy_ready_prompts.md` 和选中的参考图。
- S5 读取 S4 选中的视频记录。
- S6 读取 S5 的问题和返工输出。
- S7 读取 S6 已接受的最终/剪辑输出和 S5 结论。

`_meta` / `_audit` 文件可以帮助 agent 判断，但它们不是默认的下一阶段输入。
