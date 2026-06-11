# Human Gates

| 阶段 | 人工闸门 | 确认内容 |
| --- | --- | --- |
| S1 | `human_confirm_story` | 剧情提取、分集数量、人物视觉锚点可用 |
| S2 | `human_confirm_image_prompts` | 图片提示词可用于生成参考图 |
| S3 | `human_confirm_motion_prompts` | 当前片段的视频提示词可复制到平台 |
| S4 | `human_select_video_version` | 已选中进入质检的视频版本 |
| S5 | `human_confirm_qc` | 质检结论确认：通过、返工、拒绝或阻塞 |
| S6 | `human_confirm_edit` | 剪辑修正方案或成片确认 |
| S7 | `human_confirm_publish_pack` | 分发包确认，但不等于已经发布 |
| S8 | `human_confirm_review` | 复盘结论和下一轮调整方向确认 |

## 完成阶段命令

```bash
./bin/slbb-video-advance "./AI短剧工作流/onboard_demo" --stage S1 --status completed --human-confirmed --note "人工确认说明"
```

Windows：

```powershell
.\bin\slbb-video-advance.cmd ".\AI短剧工作流\onboard_demo" --stage S1 --status completed --human-confirmed --note "人工确认说明"
```

没有人工确认时，不要加 `--human-confirmed`。

## S5 质检 verdict → next_step 映射

S5（质检）的人工确认不仅要确认结论本身，还要确认 next_step。`qc_verdict.json` 必须包含 `verdict` 和 `next_step` 字段，组合如下：

| verdict | 含义 | next_step 默认 | 操作 |
| --- | --- | --- | --- |
| `pass` | 质检通过 | `S6` | 直接推进到 S6 剪辑修正 |
| `needs_rework` | 需要返工 | `S2` / `S3` / `S4` | 按 `rework_suggestions.md` 回到对应环节，**清空目标片段 S3-S7 产物**后重跑 |
| `reject` | 拒绝当前片段 | `S2` | 回到 S2 重做（通常是人物或场景锚点问题） |
| `blocked_no_video` | 无视频可检 | `S4` | 回到 S4 补生成记录 |

人工确认时**必须**同时确认 verdict 和 next_step，否则 next_step 默认值可能不准确（例如 needs_rework 但 next_step=stop 就会卡住流程）。

S5 validator 校验这 4 个值在合法集合内（`pass` / `needs_rework` / `reject` / `blocked_no_video`）。
