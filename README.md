# Slbb Video Agent Workflow

> 🤖 **如果你是 AI Agent 接管这个包**：先读 [`START_HERE.md`](./START_HERE.md)，里面有完整接管流程。
> 👤 **如果你是团队成员**：从下面的"运行要求 + 推荐阅读顺序"开始。

这是「石榴爸爸 AI 短视频 / AI 短剧 / AI 长剧」团队交付版工作流包。

包内包含 **10 个本地 Agent skills**（短剧 8 个 + 长剧 1 个 + 总控 1 个）。Codex 可以安装成 skills；Claude Code、WorkBuddy 或其他 AI Agent 也可以直接读取 `skills/*/SKILL.md` 和本包 `bin/` 脚本来执行。

- `slbb-video-orchestrator`：总控，负责状态机、人工闸门、下一步 handoff。
- `slbb-video-research-script`：S1 短剧调研与剧情提取。
- `slbb-video-long-replica-script`：S1 长剧改编（多年龄段 / 二次创作）。
- `slbb-video-image-prompts`：S2 图片提示词（短剧/长剧双模式）。
- `slbb-video-motion-prompts`：S3 生视频提示词（含长剧反推 prompt）。
- `slbb-video-generation-log`：S4 视频生成记录。
- `slbb-video-qc`：S5 视频质检。
- `slbb-video-edit-fix`：S6 剪辑修正。
- `slbb-video-distribution-pack`：S7 分发包。
- `slbb-video-review`：S8 发布后复盘。

## 运行要求

- macOS / Linux：Terminal + Python 3.10+（运行 `python3 --version` 确认）。
- Windows 10/11：PowerShell 或 cmd + Python 3.10+（优先运行 `py -3 --version`，不行再试 `python --version`）。
- macOS / Linux 第一次使用可运行 `chmod +x bin/*`；Windows 不需要 `chmod`。
- 任意能读取本地文件并执行命令的 AI Agent 环境，例如 Codex、Claude Code、WorkBuddy 等。
- S1-S8 状态机脚本是纯 stdlib；长剧本地视频预处理需要 ffmpeg / ffprobe 和包内 `.venv` 的 `faster-whisper`。

首次处理本地视频前先运行：

```bash
./bin/slbb-video-doctor
```

Windows：

```powershell
.\bin\slbb-video-doctor.cmd
```

## 给学员的一句话安装提示词

```text
请帮我安装并接管这个项目：https://github.com/slbb1995/slbb-video-agent.git 。先 clone 到本地，阅读 START_HERE.md、README.md、QUICKSTART.md；如果你的环境支持本地 skills，就按对应方式安装 skills/slbb-video-*；如果不支持，就直接在项目目录里读取 skills/*/SKILL.md 并使用 bin/ 脚本运行。先执行 slbb-video-doctor 检查环境，缺什么先告诉我并问我是否安装。
```

## 两种使用方式

### 方式 A：直接在本包内运行脚本

不需要配置环境变量。macOS / Linux 用无后缀脚本：

```bash
./bin/slbb-video-init "./runs/demo" --title "测试短剧"
./bin/slbb-video-next "./runs/demo"
./bin/slbb-video-validate "./runs/demo"
```

Windows PowerShell / cmd 用 `.cmd` 脚本：

```powershell
.\bin\slbb-video-init.cmd ".\runs\demo" --title "测试短剧"
.\bin\slbb-video-next.cmd ".\runs\demo"
.\bin\slbb-video-validate.cmd ".\runs\demo"
```

如果 Windows 的 `.cmd` 被安全软件拦截，也可以直接用 Python 分发器：

```powershell
py -3 .\bin\slbb-video.py init ".\runs\demo" --title "测试短剧"
py -3 .\bin\slbb-video.py next ".\runs\demo"
py -3 .\bin\slbb-video.py validate ".\runs\demo"
```

后续 skill 文档里如果看到 `python3 "$CODEX_SKILLS_ROOT/..."`，Windows 电脑统一把开头的 `python3` 换成 `py -3`。

### 方式 B：安装到支持的本地 skill 目录（可选）

不是所有 AI Agent 都有本地 skill 目录。没有也没关系，直接使用方式 A，让 AI Agent 在本项目目录里读取 `skills/*/SKILL.md` 即可。

如果你用 Codex，可以安装到 Codex skills 目录：

macOS / Linux：

```bash
mkdir -p ~/.codex/skills
cp -R skills/slbb-video-* ~/.codex/skills/
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills"
Copy-Item -Recurse .\skills\slbb-video-* "$env:USERPROFILE\.codex\skills\"
```

安装后，在 Codex 里点名对应 skill 即可。Claude Code / WorkBuddy 等环境如果没有这个目录，不要强行创建，直接让 AI 读取项目内的 skill 文档。

单独安装 `skills/slbb-video-orchestrator` 时，这个 skill 自己也带了视频相关 wrapper：

```bash
skills/slbb-video-orchestrator/bin/slbb-video-doctor
skills/slbb-video-orchestrator/bin/slbb-video-setup --video
skills/slbb-video-orchestrator/bin/slbb-video-source <run-dir> --source-ref <素材路径或链接>
skills/slbb-video-orchestrator/bin/slbb-video-ingest --run-dir <run-dir> --video <本地视频路径>
```

Windows 对应使用 `.cmd`：

```powershell
skills\slbb-video-orchestrator\bin\slbb-video-doctor.cmd
skills\slbb-video-orchestrator\bin\slbb-video-setup.cmd --video
skills\slbb-video-orchestrator\bin\slbb-video-source.cmd <run-dir> --source-ref <素材路径或链接>
skills\slbb-video-orchestrator\bin\slbb-video-ingest.cmd --run-dir <run-dir> --video <本地视频路径>
```

如果 AI Agent 只拿到了单独 skill 目录，没有完整项目根目录，也可以在该 skill 目录内运行 `bin/` wrapper。转写环境会优先查 `SLBB_VIDEO_PYTHON` / `SLBB_VIDEO_VENV_PYTHON`，再查项目或 skill 目录下的 `.venv`。

## V2 监控台衔接

如果你的 run 是从 V2 监控台（ai-drama-monitor）导出的 handoff.md 启动的，用 `slbb-video-from-handoff` 命令把交接包直接导入：

```bash
./bin/slbb-video-from-handoff "/path/to/handoff.md" "./AI长剧工作流/long_drama_run"
```

Windows：

```powershell
.\bin\slbb-video-from-handoff.cmd "C:\path\to\handoff.md" ".\AI长剧工作流\long_drama_run"
```

导入后 `workflow_state.json.source` 会写入 V2 对标信息，并同步生成 `artifacts/_source/source_manifest.json` 和 `artifacts/_source/source_brief.md`。长剧 S1 优先读 source brief，不需要再手填 source note，也不要重复读取完整视频或长字幕。

字段定义见 `skills/slbb-video-orchestrator/references/state_schema.md`。

## 长剧省 token 启动方式

长剧不要把完整视频分析、完整字幕、逐帧拆解直接粘进总控提示词。先登记素材，再把视频预处理成低 token 证据包。

macOS / Linux：

```bash
./bin/slbb-video-init "./AI长剧工作流/long_demo" --title "长剧测试" --mode long_drama
./bin/slbb-video-source "./AI长剧工作流/long_demo" --source-ref "/path/to/reference.mp4"
./bin/slbb-video-ingest --run-dir "./AI长剧工作流/long_demo" --video "/path/to/reference.mp4"
```

Windows：

```powershell
.\bin\slbb-video-init.cmd ".\AI长剧工作流\long_demo" --title "长剧测试" --mode long_drama
.\bin\slbb-video-source.cmd ".\AI长剧工作流\long_demo" --source-ref "C:\path\to\reference.mp4"
.\bin\slbb-video-ingest.cmd --run-dir ".\AI长剧工作流\long_demo" --video "C:\path\to\reference.mp4"
```

如果给的是抖音/小红书/快手/B站平台链接，先按 `START_HERE.md` 使用 `https://sv.bugpk.com/` 或录屏等方式拿到本地视频，再运行上面的 source + ingest。

然后只补 `artifacts/_source/source_brief.md`：6-10 条关键时间点、角色视觉锚点、关键台词和二创方向。S1 只读这份 brief、`source_manifest.json` 和 `artifacts/_audit/video_ingest/`，不反复读取原视频或长字幕。

可复制的低 token 提示词见：`examples/prompts/long-drama-low-token-orchestrator-prompt.md`。

## 核心规则

- 总控只推进流程，不替 S1-S8 写专业内容。
- 短剧 S1/S2 面向整条短剧打底；长剧 S1 先读 `artifacts/_source/source_brief.md` 和视频预处理证据包。
- 平台链接不能直接进入长剧 S1；必须先下载/录屏成本地视频，或走 `partial_material` 降级路径。
- S2 完成后，S3-S8 只处理一个目标片段，默认从 `001` 开始。
- 当前目标片段以 `workflow_state.json.segment_state.current_segment` 为准。
- 一个片段 S8 完成后，该片段 S3-S8 产物会归档到 `artifacts/_segments/<segment_id>/`。
- 每个阶段必须先通过 validator，再由人工确认，才能标记 `completed`。

## 推荐阅读顺序

1. `START_HERE.md`（**AI 接管入口**，人类也可以从这里开始）
2. `QUICKSTART.md`
3. `docs/ONBOARDING.md`（新人 5 分钟跑通 S1）
4. `docs/environment-setup.md`
5. `docs/video-source-guide.md`
6. `TEAM_SOP.md`
7. `docs/workflow-map.md`
8. `docs/artifact-contract.md`
9. `docs/human-gates.md`
10. `skills/slbb-video-orchestrator/references/state_schema.md`
