# S5 质检标准

来源：白板 S5 节点和项目计划。关联的 `质检表格` 是飞书表格，但 2026-05-23 当前访问权限无法读取内容。第一版使用已可见的白板要求。

## 审查方法

记录使用的方法：

- `human`：用户或操作者人工观看视频
- `frames`：审查抽帧或截图
- `gemini`：Gemini 或其他支持视频的模型审查视频
- `vision_model`：其他模型审查帧/视频
- `notes_only`：用户只提供问题笔记，没有视频访问

不要隐藏审查方法。如果没有视频/帧证据，置信度要标低。

## 类别

| 类别 | 检查内容 | 可能上游来源 |
| --- | --- | --- |
| character_consistency | 脸漂移、身体漂移、服装漂移、随机新增人物 | S2 / platform |
| deformation | 脸/身体/手变形，结构错误，不自然的眼睛或嘴 | S2 / S3 / platform |
| action_correctness | 动作不匹配提示词，顺序错误，关键动作缺失 | S3 / platform |
| expression_emotion | 表情不匹配冲突或台词 | S1 / S3 / platform |
| lighting_color | 过暗、光线不一致、氛围错误 | S2 / S3 / platform |
| camera_stability | 抖动、变焦异常、构图问题、主体丢失 | S3 / platform |
| scene_prop_consistency | 场景错误、道具缺失、道具变化、背景冲突 | S2 / S3 / platform |
| dialogue_lipsync_story | 台词不匹配、口型不匹配、故事含义改变 | S1 / S3 / platform |
| subtitle_text_glitch | 乱码文字、多余字幕、类似水印的文字 | S3 / platform / S6 |
| platform_artifact | 生成噪点、闪烁、形变、不可能运动 | platform / S4 |
| compliance_safety | 不安全视觉表达或高风险场景 | S1 / S3 |
| long_drama_continuity | 跨年龄阶段同一人物身份漂移、年龄变化不合理、相邻长剧片段情绪连续性断裂 | S1_long_replica / S2 / S3 / platform |

## 严重程度

- `critical`：不能发布或继续，必须返工。
- `high`：伤害故事或观众信任，进入剪辑前应返工。
- `medium`：可见问题，可根据成本选择返工或剪辑。
- `low`：轻微润色问题，可继续。

## 结论

- `pass`：可以继续到 S6。
- `needs_rework`：回到 S2、S3 或 S4。
- `reject`：不能使用这个生成版本。
- `blocked_no_video`：没有视频/帧证据，无法质检。

## 归因启发

- 如果角色脸/衣服从首帧就不稳定，可能来自 S2 或平台。
- 如果首帧正确但动作错误，可能来自 S3 或平台。
- 如果动作顺序错误，可能来自 S3 分镜表。
- 如果场景或道具错误，检查 S2 场景参考和 S3 场景锁定。
- 如果字幕乱码但画面可用，转到 S6 剪辑修复。
- 如果问题只出现在一个生成版本，可能是 S4 平台尝试或平台随机性。
- 如果所有版本都有同一概念性问题，回到上游 S1/S2/S3。
