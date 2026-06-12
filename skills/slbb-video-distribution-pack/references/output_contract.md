# S7 输出契约

S7 主输出是干净的发布材料。工作流推理、来源记录、风险分析和人工闸门说明应放到 `artifacts/_meta/S7_distribution_notes.md` 或发布检查清单里。

## 必须输出

```text
artifacts/S7/distribution_pack.md
artifacts/S7/platform_copy.md
artifacts/S7/publish_checklist.md
artifacts/_meta/S7_distribution_notes.md # optional
```

## distribution_pack.md

必须包含：

- `# S7 分发包`
- `## 成片信息`
- `## 标题候选`
- `## 简介与看点`
- `## 封面建议`
- `## 发布时间建议`

必须写明：

- 最终视频路径或草稿链接
- S5/S6 是否通过人工确认
- 至少 5 个标题候选
- 发布状态：未发布 / 手动发布 / 不自动发布

## platform_copy.md

必须包含：

- `# S7 平台文案`
- `## 抖音`
- `## 视频号`
- `## 小红书`

每个平台必须包含：

- 标题
- 正文或 caption
- 话题 / 标签
- 封面建议
- 发布时间建议
- 未发布状态

## publish_checklist.md

必须包含：

- `# S7 发布检查清单`
- `## 素材检查`
- `## 文案检查`
- `## 账号与平台检查`
- `## 手动发布状态`
- `## 进入下一步条件`

必须写明：

- 视频文件是否确认
- 封面是否确认
- 标题和平台文案是否确认
- 账号是否由人工检查
- 当前未发布，不自动发布
- 人工发布或修改后的下一步

## 禁止

- 不允许用“发布完成”代替“分发包完成”。
- 不允许没有人工确认就进入复盘。
- 不允许出现 `TODO`、`待填写`、`待补充`。
- 主输出不允许出现 `输入来源`、`风险与人工确认`、`人工确认`、`Workflow`、`V2 原则`。
