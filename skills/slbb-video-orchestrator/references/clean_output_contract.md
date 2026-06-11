# Clean Output Contract

This contract applies to S1-S7 primary outputs in the `slbb-video` workflow.

## Why This Exists

The workflow has three different readers:

- Next-stage skills need compact, accurate inputs.
- Humans need copy-ready prompts, logs, QC verdicts, edit actions, or publishing copy.
- The orchestrator needs process state, gates, notes, and validation evidence.

Do not serve all three readers from one Markdown file. Primary stage outputs are for the first two readers only. Process state belongs in `_meta`, `_audit`, or `_handoff`.

## Directory Rule

```text
artifacts/S1..S7/      clean primary deliverables
artifacts/_meta/       design notes, source notes, risk notes, route decisions
artifacts/_audit/      execution logs, QC evidence, edit logs
artifacts/_handoff/    next-step cards and human-gate cards
workflow_state.json    state truth source
```

## Primary Output Rules

Primary files should be directly usable by the next stage or by a human operator.

Allowed:

- Story summary, characters, scenes, episode beats.
- Image prompts, video prompts, platform-copy prompts.
- Generation records and selected video path.
- QC verdict, issue evidence, attribution, rework action.
- Edit plan, edit checklist, publish package, platform copy.

Forbidden in S1-S7 primary files:

- `Workflow` / `workflow` principles.
- `V2 原则`, version strategies, or long design rationale.
- `输入来源`, `路由模式`, `推导与风险备注`, `人工确认项`.
- `使用说明`, `合规与改写备注`, `时长判断`, `关键道具与文字风险`.
- Human-gate explanations such as `不能自动进入下一步`.

## Stage Mapping

| Stage | Clean primary outputs | Process/meta outputs |
| --- | --- | --- |
| S1 | `artifacts/S1/story_extract.md`; `artifacts/S1/story_segments.json` | `_meta/S1_research_notes.md`; `_handoff/S1_human_confirmation_card.md` |
| S2 | `artifacts/S2/image_prompt_pack.md` | `_meta/S2_prompt_notes.md` |
| S3 | `artifacts/S3/motion_prompt_pack.md`; `artifacts/S3/platform_copy_ready_prompts.md` | `_meta/S3_motion_design_notes.md` |
| S4 | `artifacts/S4/generation_run_log.md`; `artifacts/S4/generation_run_log.csv` | `_audit/S4_attempt_notes.md` |
| S5 | `artifacts/S5/qc_report.md`; `artifacts/S5/qc_verdict.json`; `artifacts/S5/rework_suggestions.md` | `_audit/S5_review_notes.md` |
| S6 | `artifacts/S6/edit_fix_plan.md`; `artifacts/S6/edit_checklist.md` | `_audit/S6_edit_log.md` |
| S7 | `artifacts/S7/distribution_pack.md`; `artifacts/S7/platform_copy.md`; `artifacts/S7/publish_checklist.md` | `_meta/S7_distribution_notes.md` |

## Chain Rule

Each stage should consume the previous stage's clean primary outputs first.

Examples:

- S2 reads S1 `story_extract.md` and `story_segments.json`, not S1 research notes.
- S3 reads S2 `image_prompt_pack.md`, not S2 route/risk notes.
- S4 uses S3 `platform_copy_ready_prompts.md` and selected reference images.
- S5 reads S4 selected video records.
- S6 reads S5 issue/rework outputs.
- S7 reads S6 accepted final/edit outputs and S5 verdict.

Meta/audit files can inform the agent, but they are not the default next-stage input.
