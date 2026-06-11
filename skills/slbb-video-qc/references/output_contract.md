# S5 Output Contract

S5 is a workflow node. It is not complete until all required artifacts exist and validate.

S5 primary outputs are clean QC deliverables for S6 or upstream rework. Long review notes and human-gate wording belong in `artifacts/_audit/S5_review_notes.md`.

## Required Directory

```text
<run_dir>/
  artifacts/
    S5/
      qc_report.md
      qc_verdict.json
      rework_suggestions.md
    _audit/
      S5_review_notes.md # optional
```

## qc_report.md

Required headings:

```markdown
# S5 视频质检报告

## 质检结论
## 问题清单
## 问题归因
## S6 可修性判定
```

## qc_verdict.json

Required shape:

```json
{
  "source": {
    "video_ref": "",
    "generation_record_id": "",
    "review_method": "human|frames|gemini|vision_model|notes_only",
    "model_used": "",
    "confidence": "low|medium|high"
  },
  "verdict": "pass|needs_rework|reject|blocked_no_video",
  "next_step": "S6|S2|S3|S4|stop",
  "scores": {
    "character_consistency": 0,
    "deformation": 0,
    "action_correctness": 0,
    "lighting_color": 0,
    "camera_stability": 0,
    "story_fidelity": 0
  },
  "issues": [
    {
      "issue_id": "qc-001",
      "category": "character_consistency",
      "severity": "high",
      "timestamp": "0:04-0:06",
      "observation": "",
      "evidence_ref": "",
      "likely_source_step": "S1|S1_long_replica|S2|S3|S4|S6|platform|unknown",
      "recommendation": ""
    }
  ],
  "editability": {
    "summary": "",
    "s6_allowed": false,
    "risk": "",
    "minimum_fix": "",
    "do_not_fix_by": ""
  }
}
```

If `verdict` is `needs_rework` or `reject`, at least one issue is required.

## rework_suggestions.md

Required headings:

```markdown
# S5 返工建议

## 总结
## 按问题返工
## 建议回到哪个环节
## 进入下一步条件
```

## Clean Output Guard

Primary Markdown outputs must not include:

- `Workflow` / `workflow`
- `V2 原则`
- `输入来源`
- `审查方法`
- `人工确认项`
- `不能自动进入下一步`
