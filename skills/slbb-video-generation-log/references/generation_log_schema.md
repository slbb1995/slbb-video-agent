# S4 Generation Log Schema

S4 records manual platform execution. It does not generate videos.

## Required Files

```text
<run_dir>/
  artifacts/
    S4/
      generation_run_log.md
      generation_run_log.csv
```

## generation_run_log.md

Required headings:

```markdown
# S4 视频生成记录

## 平台执行摘要
## 生成版本记录
## 选中版本
## 失败与返工记录
```

## generation_run_log.csv

Required columns:

```csv
record_id,clip_id,episode_id,platform,generation_mode,prompt_ref,reference_assets,settings,output_ref,status,selected_for_qc,failure_reason,created_at,operator_notes
```

Column meaning:

- `record_id`: unique attempt id, for example `s4-001`
- `clip_id`: clip or prompt group id, for example `clip-001`
- `episode_id`: source episode id from S1/S3
- `platform`: 即梦, 可灵, or other
- `generation_mode`: text-to-video, image-to-video, video-to-video, or other
- `prompt_ref`: file path, prompt id, or copied prompt reference
- `reference_assets`: image/video asset paths or URLs used by the platform
- `settings`: platform settings such as duration, aspect ratio, model, seed, style
- `output_ref`: generated video path, URL, platform id, or explicit failure note
- `status`: success, failed, selected, rejected, retry_needed
- `selected_for_qc`: yes/no
- `failure_reason`: required when status is failed or retry_needed
- `created_at`: timestamp or manual date
- `operator_notes`: human notes

## Completion Rule

At least one CSV row must have:

```text
selected_for_qc = yes
```

or:

```text
status = selected
```

Without a selected video/version, S4 can be useful as a log, but it is not complete for the workflow.

## Clean Output Guard

`generation_run_log.md` must not include:

- `Workflow` / `workflow`
- `V2 原则`
- `输入来源`
- `人工确认项`
- `不能自动进入下一步`
