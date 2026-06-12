# S5 输出契约

S5 是工作流节点。只有所有必需产物都存在并验证通过，S5 才算完成。

S5 主输出是给 S6 或上游返工使用的干净质检交付物。长审查笔记和人工闸门话术放到 `artifacts/_audit/S5_review_notes.md`。

## 必需目录

```text
<run_dir>/
  artifacts/
    S5/
      qc_report.md
      qc_verdict.json
      rework_suggestions.md
    _audit/
      S5_review_notes.md # 可选
```

## qc_report.md

必需标题：

```markdown
# S5 视频质检报告

## 质检结论
## 问题清单
## 问题归因
## S6 可修性判定
```

## qc_verdict.json

必需结构：

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

如果 `verdict` 为 `needs_rework` 或 `reject`，至少需要一个问题。

## rework_suggestions.md

必需标题：

```markdown
# S5 返工建议

## 总结
## 按问题返工
## 建议回到哪个环节
## 进入下一步条件
```

## 干净输出保护

主 Markdown 输出不得包含：

- `Workflow` / `workflow`
- `V2 原则`
- `输入来源`
- `审查方法`
- `人工确认项`
- `不能自动进入下一步`
