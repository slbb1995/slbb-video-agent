# S4 视频生成日志结构

S4 记录人工平台执行结果。它不生成视频。

## 必需文件

```text
<run_dir>/
  artifacts/
    S4/
      generation_run_log.md
      generation_run_log.csv
```

## generation_run_log.md

必需标题：

```markdown
# S4 视频生成记录

## 平台执行摘要
## 生成版本记录
## 选中版本
## 失败与返工记录
```

## generation_run_log.csv

必需列：

```csv
record_id,clip_id,episode_id,platform,generation_mode,prompt_ref,reference_assets,settings,output_ref,status,selected_for_qc,failure_reason,created_at,operator_notes
```

列含义：

- `record_id`：唯一尝试 ID，例如 `s4-001`
- `clip_id`：片段或提示词组 ID，例如 `clip-001`
- `episode_id`：来自 S1/S3 的来源分集 ID
- `platform`：即梦、可灵或其他
- `generation_mode`：text-to-video、image-to-video、video-to-video 或 other
- `prompt_ref`：文件路径、提示词 ID 或复制版提示词引用
- `reference_assets`：平台使用的图片/视频资产路径或 URL
- `settings`：平台设置，例如时长、画幅、模型、seed、风格
- `output_ref`：生成视频路径、URL、平台 ID 或明确失败说明
- `status`：success、failed、selected、rejected、retry_needed
- `selected_for_qc`：yes/no
- `failure_reason`：当 status 为 failed 或 retry_needed 时必填
- `created_at`：时间戳或人工日期
- `operator_notes`：人工备注

## 完成规则

至少一行 CSV 必须包含：

```text
selected_for_qc = yes
```

或：

```text
status = selected
```

没有选中的视频/版本时，S4 日志仍有价值，但对工作流来说还未完成。

## 干净输出保护

`generation_run_log.md` 不得包含：

- `Workflow` / `workflow`
- `V2 原则`
- `输入来源`
- `人工确认项`
- `不能自动进入下一步`
