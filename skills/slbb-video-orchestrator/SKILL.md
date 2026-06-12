---
name: slbb-video-orchestrator
description: AI 短剧 S1-S8 总控技能。用于按状态机推进 slbb-video 工作流，检查每阶段产物、运行阶段校验、维护 workflow_state.json、生成下一步 handoff，并强制人工闸门。当用户要求“AI短剧总控”“跑完整个短剧工作流”“S1-S8 串起来”“orchestrator”“状态机”或“下一步该跑哪个 Skill”时使用。总控只管流程，不代替 S1-S8 具体内容技能。
---

# AI 短剧总控：S1-S8

## 概览

这个技能用来协调 AI 短剧工作流，不把整套 SOP 压成一个大提示词。

总控只控制状态、闸门和交接。每个专业动作仍然属于对应阶段技能：S1 到 S8。

## 核心规则

```text
总控管流程，技能做专业动作，脚本查状态，人工闸门决定能不能进入下一步。
```

不要要求一次模型回复完成 S1-S8 全流程。

S1 进入 S2 之前，S1 必须包含来源覆盖审计和动态分集决策。除非 `artifacts/_meta/S1_segmentation_decision.md` 解释了来源覆盖和目标片段数，否则总控不能接受固定 8/16/20 这类模板化压缩数量。

对于 `long_drama`，S1 不能从原始平台链接直接开始。运行 `slbb-video-long-replica-script` 之前，run 必须有 `artifacts/_source/source_manifest.json`。如果来源是 `local_video` 或 `direct_video_url`，还必须有 `artifacts/_audit/video_ingest/ingest_report.md`、`shot_index.json` 和 `contact_sheet.jpg`。如果来源是 `platform_link`（抖音/小红书/快手/B站分享页），停止并要求用户先下载或录制本地视频。如果来源只有截图/字幕/笔记，标记为 `partial_material`，并保留低置信度警告。

S2 确认后，工作单元是一个分集/片段，不是整季。默认从第一个未完成片段开始，通常是 `001`，先让这个单片段跑完 S3-S8，再开始下一个片段。

S2 完成时，`workflow_state.json` 必须从 `artifacts/S1/story_segments.json` 初始化 `segment_state`。S3-S8 始终处理 `segment_state.current_segment`。S8 完成后，总控把该片段的 S3-S8 产物归档到 `artifacts/_segments/<segment_id>/`，重置 S3-S8，并推进到下一个未完成片段。

## 执行闸门

- 红色检查点：任何阶段标记为 `ready_for_human` 前，必需输出必须存在，且阶段 validator 必须通过。
- 红色检查点：S1 标记为 `ready_for_human` 前，确认 S1 validator 已检查 `artifacts/_meta/S1_segmentation_decision.md`，并且 `target_segment_count` 与 `story_segments.json` 匹配。
- 红色检查点：任何阶段标记为 `completed` 前，用户必须明确确认人工闸门，并且命令必须包含 `--human-confirmed`。
- 红色检查点：S2 之后任何批量覆盖前，用户必须给出准确分集/片段范围；否则继续处理第一个未完成单片段。
- 红色检查点：任何 S3-S8 交接前，`artifacts/_handoff/next_step.md` 必须写明当前目标片段。
- 停止：如果缺少 `workflow_state.json`，或它格式错误、顺序错误、早期阶段未完成但指向后续已完成阶段，停止并运行验证，不要推进。
- 停止：如果阶段产物缺失或 validator 失败，保持当前阶段打开，并把问题写入 handoff 说明。

## 工作流程

1. 创建 AI 短剧生成过程文件目录：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-orchestrator/scripts/init_run.py" <AI短剧生成过程文件目录> --title "<短剧/项目名>"
   ```

   或把 V2 监控台（ai-drama-monitor）的 handoff 导入为来源：
   ```bash
   bin/slbb-video-from-handoff <handoff.md> <AI长剧生成过程文件目录>
   ```
   handoff 路径会填充 `workflow_state.json.source`（v2_video_url / matched_rules / v2_metrics 等）；S1 会把 `source.v2_video_url` 作为最高优先级输入读取。source 字段结构见 `references/state_schema.md`。

   对已选择的长剧本地视频或直链视频，S1 前先运行来源登记和 ingest：
   ```bash
   bin/slbb-video-source <AI长剧生成过程文件目录> --source-ref <本地视频路径或直链>
   bin/slbb-video-ingest --run-dir <AI长剧生成过程文件目录> --video <本地视频路径或直链>
   ```

   如果这个技能不是从完整项目根目录使用，而是作为独立本地技能安装，则从本技能目录运行 wrapper：
   ```bash
   ./bin/slbb-video-source <AI长剧生成过程文件目录> --source-ref <本地视频路径或直链>
   ./bin/slbb-video-ingest --run-dir <AI长剧生成过程文件目录> --video <本地视频路径或直链>
   ```
   ingest 脚本会按 `--transcript-python`、`SLBB_VIDEO_PYTHON`、`SLBB_VIDEO_VENV_PYTHON` 或最近的项目/技能 `.venv` 解析 `faster_whisper`。

   对平台分享链接，`slbb-video-source` 只记录链接并停止。用户必须先下载或录制视频；不要把第三方下载逻辑塞进这个技能。

2. 查询下一步：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-orchestrator/scripts/next_step.py" <AI短剧生成过程文件目录>
   ```
3. 运行 `artifacts/_handoff/next_step.md` 指定的阶段技能。
4. 红色检查点：当阶段产物可以审查时，标记为待人工确认：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-orchestrator/scripts/advance_stage.py" <AI短剧生成过程文件目录> --stage S1 --status ready_for_human --note "等待用户确认剧情"
   ```
5. 红色检查点：用户确认人工闸门后，完成该阶段：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-orchestrator/scripts/advance_stage.py" <AI短剧生成过程文件目录> --stage S1 --status completed --human-confirmed --note "用户确认剧情"
   ```
6. 验证状态：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-orchestrator/scripts/validate_orchestrator_state.py" <AI短剧生成过程文件目录>
   ```

如果没有设置 `CODEX_SKILLS_ROOT`，把它替换成本地 skills 根目录。

## 阶段地图

完整契约见 `references/workflow_contract.md`。
干净输出边界见 `references/clean_output_contract.md`：S1-S7 主输出是下一阶段输入，过程记录放在 `_meta`、`_audit` 或 `_handoff`。

- S1 `slbb-video-research-script`：短剧调研与剧情提取
- S2 `slbb-video-image-prompts`：图片提示词
- S3 `slbb-video-motion-prompts`：生视频提示词
- S4 `slbb-video-generation-log`：视频生成记录
- S5 `slbb-video-qc`：视频质检
- S6 `slbb-video-edit-fix`：剪辑修正
- S7 `slbb-video-distribution-pack`：分发包
- S8 `slbb-video-review`：发布后复盘

## 失败模式

| 触发情况 | 必须动作 | 禁止的偷懒做法 |
| --- | --- | --- |
| `workflow_state.json` 不存在 | 运行 `init_run.py`，或要求提供正确过程目录。 | 根据附近文件推断状态。 |
| `workflow_state.json` 不是合法 JSON 或缺少阶段 | 运行 `validate_orchestrator_state.py`，报告准确错误并停止。 | 手工猜测阶段顺序。 |
| 用户要求一次跑完 S1-S8 | 说明总控一次只推进一个阶段，或 S2 后一个片段，然后运行 `next_step.py`。 | 一次回复产出所有阶段产物。 |
| 用户要求 S2 后批量跑所有分集 | 要求给出明确分集/片段范围；没有范围就继续第一个未完成片段，通常是 `001`。 | 静默生成或推进所有剩余片段。 |
| S1 拆分数量被质疑或来源覆盖不清 | 回到 S1，修订来源覆盖审计和拆分决策，再使依赖旧数量的下游 S2/S3 产物失效。 | 继续沿用旧图片/视频提示词推进。 |
| 必需输出缺失 | 保持阶段打开，并回到 handoff 里列出的阶段技能。 | 标记 `ready_for_human` 或 `completed`。 |
| 长剧来源是平台链接 | 要求用户下载/录制本地视频，再重新运行 `slbb-video-source` 和 `slbb-video-ingest`。 | 让 S1 直接分析抖音/小红书分享链接。 |
| 长剧本地/直链视频缺少 `video_ingest` 包 | 运行 `slbb-video-doctor`，经用户批准安装缺失环境，再运行 `slbb-video-ingest`。 | 在聊天里反复读完整视频。 |
| 长剧来源只有截图/字幕/笔记 | 登记为 `partial_material`，并要求低置信度人工确认。 | 把它说成完整视频拆解。 |
| 阶段 validator 失败 | 把 validator 输出保留在 handoff 说明里，状态不变。 | 除非用户明确接受风险，否则不要用 `--skip-validator`。 |
| 缺少人工确认 | 保持 `gate_status` 为 `waiting` 或 `pending`，并要求确认。 | 替用户传入 `--human-confirmed`。 |
| 阶段内容需要重写 | 转给对应 S1-S8 技能，总控只管状态、闸门和交接。 | 让总控重写阶段内容。 |
| 主输出包含过程记录 | 把过程记录移到 `_meta`、`_audit` 或 `_handoff`，保持主产物干净。 | 把污染过的主输出喂给下一阶段。 |

## 规则

- 没有必需产物和明确人工确认，绝不把阶段标记为 `completed`。
- 除非用户明确要求覆盖工作流，否则不要跳阶段。
- 不要让总控重写阶段内容。内容工作要回到对应阶段技能。
- 除非 S1 来源覆盖审计和拆分决策存在并验证通过，否则不要把看似合理的 S1 分集数量当成已确认。
- S2 之后，不要在一次阶段调用里生成或推进所有剩余分集/片段。正常循环是 `001: S3 -> S4 -> S5 -> S6 -> S7 -> S8`，用户确认下一个片段后，再走 `002: S3 -> S4 -> ...`。
- S2 可以包含所有角色和场景参考，但 S3 必须只选择当前目标分集/片段需要的参考，除非用户明确要求批量覆盖。
- validator 失败时，保持当前阶段打开，并写清楚 handoff 说明。
- `workflow_state.json` 是一个 AI 短剧生成过程文件目录的本地真相源。
- S2 之后，`workflow_state.json.segment_state.current_segment` 是当前活跃分集/片段的本地真相源。
- `artifacts/_handoff/next_step.md` 是下一次 agent 对话的下一步执行卡。
- 总完成需要 S1-S8 都完成、所有闸门确认、状态验证通过。

## 反模式黑名单

- 不要把总控当成 S1-S8 的内容生成器。
- 决定下一步时，不要绕过 `next_step.py`。
- 不要因为模型说输出看起来可以，就把阶段标记为 `completed`。
- 早期阶段未 `completed` 时，不要推进后续阶段。
- 不要把 S1 结构验证通过当成来源边界或压缩片段数正确的证明。
- S2 之后，没有明确用户覆盖和书面目标范围，不要批量跑分集/片段。
- 不要把工作流理由、路由说明、风险说明或人工闸门文字放进 S1-S7 主输出。
- 不要把 `--skip-validator` 当作便利开关；只有用户明确接受风险后才能用。
- 不要在总控里修缺失阶段产物；把工作交回拥有该产物的阶段技能。

## 必需文件

每个 AI 短剧生成过程文件目录应有：

```text
workflow_state.json
artifacts/_handoff/next_step.md
```

状态文件结构见 `references/state_schema.md`。
