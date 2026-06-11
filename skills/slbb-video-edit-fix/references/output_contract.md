# S6 Output Contract

S6 is a workflow node. It is not complete until the plan and checklist exist and validate.

S6 primary outputs are clean editing instructions. Capability limits, draft/rejection logs, and operator notes belong in `artifacts/_audit/S6_edit_log.md`.

For `long_drama` mode, S6 can also describe segment-joining fixes such as `bridge_shot`, `segment_regenerate`, and `continuity_trim`, while keeping regenerate-required identity or story errors routed upstream.

## Required Directory

```text
<run_dir>/
  artifacts/
    S6/
      edit_fix_plan.md
      edit_checklist.md
    _audit/
      S6_edit_log.md # optional
```

## edit_fix_plan.md

Required headings:

```markdown
# S6 剪辑修正方案

## 修正结论
## 字幕遮挡方案
## 其他剪辑修正
## 不适合剪辑修正的问题
```

## edit_checklist.md

Required headings:

```markdown
# S6 剪辑执行清单

## 基础设置
## 修正项清单
## 导出检查
## 进入下一步条件
```

## Required Quality Signals

The finished artifacts must include:

- `白底黑字`
- `黑体`
- `可商用`
- `遮住`
- At least one fix item id such as `fix-001`

If no subtitle cover is needed, the plan must explicitly say why and list another fix or route back upstream.

## Clean Output Guard

Primary Markdown outputs must not include:

- `Workflow` / `workflow`
- `V2 原则`
- `输入来源`
- `S6 能力边界`
- `人工确认项`
- `不能自动进入下一步`
