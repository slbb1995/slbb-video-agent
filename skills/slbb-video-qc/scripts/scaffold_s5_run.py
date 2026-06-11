#!/usr/bin/env python3
"""Create the S5 artifact skeleton for an AI short-drama workflow run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


QC_REPORT = """# S5 视频质检报告

## 质检结论

## 问题清单

## 问题归因

## S6 可修性判定

| 问题 | 处理标签 | 是否允许进 S6 | 最小可接受修正 | 不允许的修法 | 需要回到的环节 |
| --- | --- | --- | --- | --- | --- |

处理标签：`edit_safe` / `edit_precise_only` / `regenerate_required` / `accept_or_defer`

"""

REWORK = """# S5 返工建议

## 总结

## 按问题返工

## 建议回到哪个环节

## 进入下一步条件
"""

REVIEW_NOTES = """# S5 过程备注

## 输入来源

## 审查方法

## 模型或人工观察原始记录

## 人工确认备注
"""

VERDICT = {
    "source": {
        "video_ref": "",
        "generation_record_id": "",
        "review_method": "",
        "model_used": "",
        "confidence": "",
    },
    "verdict": "",
    "next_step": "",
    "scores": {
        "character_consistency": 0,
        "deformation": 0,
        "action_correctness": 0,
        "lighting_color": 0,
        "camera_stability": 0,
        "story_fidelity": 0,
    },
    "issues": [],
    "editability": {
        "summary": "",
        "s6_allowed": False,
        "risk": "",
        "minimum_fix": "",
        "do_not_fix_by": "",
    },
}


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Workflow run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    s5_dir = run_dir / "artifacts" / "S5"
    audit_dir = run_dir / "artifacts" / "_audit"
    s5_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    created = []
    files = {
        s5_dir / "qc_report.md": QC_REPORT,
        s5_dir / "rework_suggestions.md": REWORK,
        s5_dir / "qc_verdict.json": json.dumps(VERDICT, ensure_ascii=False, indent=2) + "\n",
        audit_dir / "S5_review_notes.md": REVIEW_NOTES,
    }
    for path, content in files.items():
        if write_if_missing(path, content):
            created.append(str(path))

    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    else:
        print(f"No files created; S5 skeleton already exists: {s5_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
