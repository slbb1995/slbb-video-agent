---
name: slbb-video-generation-log
description: AI 短剧 S4 视频生成执行记录。当用户在即梦、可灵或其他平台手动生成短剧视频，需要登记平台、提示词、图片资产、生成尝试、生成文件/URL、失败原因、选中版本，并交接给 S5 质检时使用。触发词包括“视频生成记录”“生成日志”“记录即梦/可灵生成结果”“选择哪版视频”“人工生成视频后登记”，以及 slbb-video 工作流中的 S4 产物。
---

# AI 短剧 S4：视频生成记录

## 概览

这个技能用来记录 S3 之后的人工视频生成尝试。S4 不调用即梦、可灵或任何视频生成 API。

它的目的，是让生成过程可追踪：用了哪个提示词、上传了哪些图片资产、生成了哪些版本、选中了哪一版、失败原因是什么。

## 执行闸门

- 红色检查点：追加成功记录前，必须有真实输出路径、URL、平台 ID，或明确人工说明。
- 红色检查点：S4 完成前，至少有一条记录被选中用于 S5 质检。
- 红色检查点：进入 S5 前，所选视频/版本必须由用户确认。
- 停止：如果没有可用生成视频，S4 保持未完成，并回到 S2/S3 或平台重试。
- 停止：如果用户要求 S4 调用即梦/可灵 API，保持人工流程，只记录人工生成结果。

## 输入

优先使用工作流产物：

```text
artifacts/S2/image_prompt_pack.md
artifacts/S3/motion_prompt_pack.md
artifacts/S3/platform_copy_ready_prompts.md
```

也可以接受人工数据：

- 平台：即梦 / 可灵 / 其他
- 生成模式：文生视频 / 图生视频
- 提示词 ID 或复制版提示词
- 参考图片路径或 URL
- 生成视频文件路径或 URL
- 失败原因
- 选中版本

## 工作流程

1. 创建 S4 骨架：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-generation-log/scripts/scaffold_s4_run.py" <run_dir>
   ```
2. 让人工操作者在目标平台手动生成视频。
3. 追加每个生成版本或失败尝试：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-generation-log/scripts/append_generation_record.py" <run_dir> --clip-id clip-001 --platform 即梦 --generation-mode image-to-video --prompt-ref artifacts/S3/platform_copy_ready_prompts.md --reference-assets "artifacts/S2/image_prompt_pack.md" --output-ref "/path/or/url/to/video.mp4" --status success --selected-for-qc yes --notes "selected version"
   ```
4. 更新 `artifacts/S4/generation_run_log.md`，写入简洁总结和选中版本。
   - Markdown 总结保持干净：平台、设置、生成版本、选中版本、失败/重试记录。
   - 如有需要，把操作者判断或交接说明放到 `artifacts/_audit/S4_attempt_notes.md`。
5. 验证：
   ```bash
   python3 "$CODEX_SKILLS_ROOT/slbb-video-generation-log/scripts/validate_s4_outputs.py" <run_dir>
   ```
6. 停在人工闸门。所选视频确认之前，不要继续进入 S5。

如果没有设置 `CODEX_SKILLS_ROOT`，把它替换成本地 skills 根目录。

## 规则

- 除非有文件路径、URL 或明确人工说明，否则不要声称已经生成视频。
- 第一版不调用平台 API。
- 保留失败尝试。它们对 S5 和后续提示词修正有价值。
- 记录每次尝试使用的准确提示词引用。
- 记录图生视频使用的参考资产。
- S4 标记完成前，至少一行必须被选中用于质检。
- 如果没有可用生成视频，S4 保持未完成，并应回到 S2/S3 或平台重试。

## 必需输出

```text
artifacts/S4/generation_run_log.md
artifacts/S4/generation_run_log.csv
```

必需列和 Markdown 章节见 `references/generation_log_schema.md`。

S4 主输出不得包含工作流原则、人造确认章节或长篇过程解释。它们是给 S5 用的日志，不是培训笔记。

## 失败模式

| 触发情况 | 必须动作 | 禁止的偷懒做法 |
| --- | --- | --- |
| 用户还没有生成视频 | 请人工先手动生成，并把 S4 记录为未完成。 | 编造成功记录。 |
| 某次尝试失败 | 记录失败行，并填写 `failure_reason`。 | 删除失败尝试。 |
| 存在多个版本 | 明确标记哪一版被选中用于质检。 | 让 S5 猜测选中版本。 |
| 选中行缺少输出路径或 URL | 在证据存在前，把 S4 视为未完成。 | 没有可用引用也标记 selected。 |
| CSV 结构验证失败 | 先修日志结构，再交接。 | 使用随意表格继续推进。 |
| 用户要求评估视频质量 | 把质量判断转给 S5。 | 在 S4 内做质检。 |

## 反模式黑名单

- 不要在这个技能里调用视频生成 API。
- 不要在没有路径、URL、平台 ID 或明确人工说明时声称生成成功。
- 不要为了让日志好看而覆盖失败尝试。
- 不要在没有清楚原因的情况下选择多个版本用于质检。
- 不要把工作流原则或人工闸门话术写进 `generation_run_log.md`。
- 没有选中版本时，不要继续进入 S5。

## 完成闸门

只有 Markdown 日志和 CSV 日志都存在、验证通过，并且至少一个生成视频/版本被标记为选中用于 S5 质检时，S4 才算完成。
