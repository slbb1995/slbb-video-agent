# Quickstart

以下命令假设你已经解压并进入本目录：

macOS / Linux：

```bash
cd AI短剧长剧工作流模版包6.10
chmod +x bin/slbb-video-{advance,doctor,from-handoff,ingest,init,next,setup,source,validate}  # 只给 macOS/Linux 入口加执行权限
./bin/slbb-video-doctor
```

Windows PowerShell：

```powershell
cd AI短剧长剧工作流模版包6.10
py -3 --version       # 确认 Python 3.10+ 可用；不行就试 python --version
.\bin\slbb-video-doctor.cmd
```

命令对照：

| 动作 | macOS / Linux | Windows PowerShell / cmd |
| --- | --- | --- |
| 环境检测 | `./bin/slbb-video-doctor` | `.\bin\slbb-video-doctor.cmd` |
| 安装视频依赖 | `./bin/slbb-video-setup --video` | `.\bin\slbb-video-setup.cmd --video` |
| 初始化 | `./bin/slbb-video-init` | `.\bin\slbb-video-init.cmd` |
| 登记长剧素材 | `./bin/slbb-video-source` | `.\bin\slbb-video-source.cmd` |
| 预处理本地视频 | `./bin/slbb-video-ingest` | `.\bin\slbb-video-ingest.cmd` |
| 从 handoff 导入 | `./bin/slbb-video-from-handoff` | `.\bin\slbb-video-from-handoff.cmd` |
| 查看下一步 | `./bin/slbb-video-next` | `.\bin\slbb-video-next.cmd` |
| 推进状态 | `./bin/slbb-video-advance` | `.\bin\slbb-video-advance.cmd` |
| 校验 | `./bin/slbb-video-validate` | `.\bin\slbb-video-validate.cmd` |

## 0. 5 分钟跑通 S1（最快路径）

如果你只是想"先跑通一条"，按下面 5 步走。下面先给 macOS / Linux 命令：

```bash
# 1. 初始化 run
./bin/slbb-video-init "./AI短剧工作流/first" --title "我的第一条"

# 2. 复制已填好的 source note
cp examples/sample-inputs/source-note-FILLED.md \
   "./AI短剧工作流/first/artifacts/S1/source_note.md"

# 3. 让当前 AI Agent 跑 S1（说"请按 skills/slbb-video-research-script/SKILL.md 处理 ./AI短剧工作流/first"）

# 4. 状态推进
./bin/slbb-video-advance "./AI短剧工作流/first" --stage S1 --status ready_for_human --note "等确认"
./bin/slbb-video-validate "./AI短剧工作流/first"

# 5. 确认后推进
./bin/slbb-video-advance "./AI短剧工作流/first" --stage S1 --status completed --human-confirmed --note "已确认"
./bin/slbb-video-next "./AI短剧工作流/first"    # 写下一步 handoff，进 S2
```

Windows PowerShell 对应命令：

```powershell
.\bin\slbb-video-init.cmd ".\AI短剧工作流\first" --title "我的第一条"
Copy-Item .\examples\sample-inputs\source-note-FILLED.md ".\AI短剧工作流\first\artifacts\S1\source_note.md"

# 然后对当前 AI Agent 说：请按 skills/slbb-video-research-script/SKILL.md 处理 .\AI短剧工作流\first

.\bin\slbb-video-advance.cmd ".\AI短剧工作流\first" --stage S1 --status ready_for_human --note "等确认"
.\bin\slbb-video-validate.cmd ".\AI短剧工作流\first"
.\bin\slbb-video-advance.cmd ".\AI短剧工作流\first" --stage S1 --status completed --human-confirmed --note "已确认"
.\bin\slbb-video-next.cmd ".\AI短剧工作流\first"
```

跑通后看 `docs/ONBOARDING.md` 拿更多细节。这个包不再引用未随包交付的 demo 目录，避免新人复制到不存在的路径。

## 从 V2 监控台 handoff 启动

如果对标素材来自 V2 监控台（ai-drama-monitor），用 `from-handoff` 命令：

```bash
./bin/slbb-video-from-handoff "/path/to/handoff.md" "./AI长剧工作流/long_drama_run"
```

Windows：

```powershell
.\bin\slbb-video-from-handoff.cmd "C:\path\to\handoff.md" ".\AI长剧工作流\long_drama_run"
```

导入后：

```bash
./bin/slbb-video-validate "./AI长剧工作流/long_drama_run"
# 如果 handoff 是平台链接，validate/next 会提示先下载成本地视频并运行 ingest
```

V2 入口的 run 不需要 `source_note.md`，会自动生成 `artifacts/_source/source_brief.md`；长剧 S1 优先读这份 brief 和 `source_manifest.json`。

## 低 token 启动 AI 长剧

本地视频、录屏和长字幕不要直接粘进总控提示词。先登记素材位置，再填精简 brief。

macOS / Linux：

```bash
./bin/slbb-video-init "./AI长剧工作流/first_long" --title "我的第一条长剧" --mode long_drama
./bin/slbb-video-source "./AI长剧工作流/first_long" --source-ref "/path/to/reference.mp4"
./bin/slbb-video-ingest --run-dir "./AI长剧工作流/first_long" --video "/path/to/reference.mp4"
```

Windows：

```powershell
.\bin\slbb-video-init.cmd ".\AI长剧工作流\first_long" --title "我的第一条长剧" --mode long_drama
.\bin\slbb-video-source.cmd ".\AI长剧工作流\first_long" --source-ref "C:\path\to\reference.mp4"
.\bin\slbb-video-ingest.cmd --run-dir ".\AI长剧工作流\first_long" --video "C:\path\to\reference.mp4"
```

如果给的是抖音/小红书/快手/B站平台链接，先用 `https://sv.bugpk.com/` 或录屏等方式下载成本地视频，再运行上面的 source + ingest。

然后补 `AI长剧工作流/first_long/artifacts/_source/source_brief.md`。建议只写：

- 1 句话剧情/核心看点
- 2-4 个角色视觉锚点
- 6-10 条关键时间点
- 最关键的台词/字幕摘要
- 二创方向

填好后执行：

```bash
./bin/slbb-video-next "./AI长剧工作流/first_long"
```

S1 应使用 `slbb-video-long-replica-script`，并且只读取 `source_brief.md` 和 `source_manifest.json`。

本地视频/直链视频还必须有：

```text
artifacts/_audit/video_ingest/ingest_report.md
artifacts/_audit/video_ingest/shot_index.json
artifacts/_audit/video_ingest/contact_sheet.jpg
```

## 1. 初始化一个项目 run

```bash
./bin/slbb-video-init "./AI短剧工作流/my-first-video" --title "我的第一条 AI 短剧"
```

生成：

```text
AI短剧工作流/my-first-video/workflow_state.json
AI短剧工作流/my-first-video/artifacts/_handoff/next_step.md
```

## 2. 查看下一步

```bash
./bin/slbb-video-next "./AI短剧工作流/my-first-video"
```

打开：

```text
AI短剧工作流/my-first-video/artifacts/_handoff/next_step.md
```

里面会写明当前阶段、应该使用哪个 skill、必须产物和人工闸门。

## 3. 每个阶段的推进方式

当某个阶段产物已经写好，先标记等待人工确认：

```bash
./bin/slbb-video-advance "./AI短剧工作流/my-first-video" --stage S1 --status ready_for_human --note "等待确认剧情拆分"
```

人工确认后，再标记完成：

```bash
./bin/slbb-video-advance "./AI短剧工作流/my-first-video" --stage S1 --status completed --human-confirmed --note "剧情拆分已确认"
```

## 4. 验证状态

```bash
./bin/slbb-video-validate "./AI短剧工作流/my-first-video"
```

完整校验已完成阶段的产物：

```bash
./bin/slbb-video-validate "./AI短剧工作流/my-first-video" --run-stage-validators
```

## 5. S2 后的片段循环

S2 完成后，总控会从 `artifacts/S1/story_segments.json` 读取片段列表。

默认推进方式：

```text
001: S3 -> S4 -> S5 -> S6 -> S7 -> S8
002: S3 -> S4 -> S5 -> S6 -> S7 -> S8
...
```

不要一次把所有片段都批量推进，除非负责人明确给出目标范围。
