# START HERE — AI 接管这个工作流包

> 你的客户拿到这个压缩包后，会把这个文件告诉你。**你就是 AI Agent**。
> 看到 `START_HERE.md` 意味着：客户已经把 AI 短剧 / 长剧工作流包交给你接管。
> 第一件事不是跑 S1，而是先检查电脑环境和素材类型。

---

## 第 0 步：正式开始前必做环境检测

先不要急着跑长剧 workflow。先在包根目录运行环境检测。

macOS / Linux：

```bash
chmod +x bin/slbb-video-{advance,doctor,from-handoff,ingest,init,next,setup,source,validate}
./bin/slbb-video-doctor
```

Windows PowerShell / cmd：

```powershell
.\bin\slbb-video-doctor.cmd
```

`doctor` 会检查：

- Python 是否可用，且是否为 3.10+。
- ffmpeg 是否可用。
- ffprobe 是否可用。
- 包内 `.venv` 是否存在。
- `.venv` 里是否已安装 `faster-whisper`。
- 是否能正常创建 artifacts 目录。
- 当前系统是 macOS、Windows 还是 Linux。
- 当前路径是否包含中文或空格，并给出兼容提醒。

如果检测到缺环境，**不要静默安装，也不要继续 S1**。先把缺失项告诉客户，让客户决定是否安装。

推荐话术：

```text
检测到你的电脑缺少以下环境：

- ffmpeg：未安装
- ffprobe：未安装
- faster-whisper：未安装

是否现在安装？
1. 安装后继续视频预处理
2. 暂不安装，只使用截图/字幕/文字材料降级分析
```

用户确认安装后：

macOS / Linux：

```bash
./bin/slbb-video-setup --video
```

Windows：

```powershell
.\bin\slbb-video-setup.cmd --video
```

系统 ffmpeg 需要单独安装：

- macOS：`brew install ffmpeg`
- Windows：`winget install Gyan.FFmpeg`
- Windows 没有 winget 时：手动安装 ffmpeg，并把 ffmpeg 的 `bin` 目录加入 PATH。

安装完必须重新运行 `slbb-video-doctor`，通过后再继续。

如果你不是在完整项目根目录，而是只安装了单独的 `slbb-video-orchestrator` skill，请在该 skill 目录里运行：

macOS / Linux：

```bash
./bin/slbb-video-doctor
./bin/slbb-video-setup --video
```

Windows：

```powershell
.\bin\slbb-video-doctor.cmd
.\bin\slbb-video-setup.cmd --video
```

转写时会优先使用 `SLBB_VIDEO_PYTHON` 或 `SLBB_VIDEO_VENV_PYTHON` 指定的 Python；没有指定时，自动查当前项目或 skill 目录下的 `.venv`。

---

## 第 1 步：摸清包和入口

按顺序读这 5 份文件：

1. `README.md` — 包是什么、能跑什么。
2. `QUICKSTART.md` — 完整命令清单。
3. `TEAM_SOP.md` — 角色分工 + 每日交接规则。
4. `docs/ONBOARDING.md` — 5 分钟跑通指南。
5. `skills/slbb-video-orchestrator/SKILL.md` — 总控 skill 的完整规则。

摸清后告诉客户：

- 包里有 10 个 `slbb-video-*` skill。
- `bin/` 里有 9 个 macOS/Linux 脚本 + 9 个 Windows `.cmd` 脚本 + `slbb-video.py` 分发器。
- 长剧模式必须先做素材来源判断和视频预处理，不能直接让 S1 读取完整视频或平台链接。

---

## 第 2 步：判断客户给的是什么素材

问客户：你现在给的是哪一种？

1. 本地视频文件：`.mp4` / `.mov` / `.mkv` / `.webm`
2. 抖音 / 小红书 / 快手 / B 站等平台分享链接
3. 直接指向视频文件的 URL
4. 录屏文件
5. 截图、字幕、台词、口述材料
6. V2 监控台导出的 `handoff.md`

不要自己猜。先登记素材：

macOS / Linux：

```bash
./bin/slbb-video-source "./AI长剧工作流/项目名" --source-ref "<客户给的路径或链接>"
```

Windows：

```powershell
.\bin\slbb-video-source.cmd ".\AI长剧工作流\项目名" --source-ref "<客户给的路径或链接>"
```

`slbb-video-source` 会自动写入：

```text
artifacts/_source/source_manifest.json
artifacts/_source/source_brief.md
artifacts/_source/source_note.md
```

素材类型只允许这 4 类：

```text
local_video
platform_link
direct_video_url
partial_material
```

---

## 第 3 步：平台链接必须先下载成本地视频

如果客户给的是抖音 / 小红书 / 快手 / B 站等平台链接，**不能直接进入 S1**。

请先把视频下载成本地 mp4 文件。

可选第三方工具：

```text
https://sv.bugpk.com/
```

操作方式：

1. 复制平台视频分享链接。
2. 打开 `https://sv.bugpk.com/`。
3. 粘贴链接并解析。
4. 下载视频文件。
5. 把下载后的本地视频路径重新交给当前 AI Agent。
6. 再运行 `slbb-video-source` 和 `slbb-video-ingest`。

注意：

- 第三方解析网站可能失效、限流或解析失败。
- 如果解析失败，可以改用录屏、平台自带保存、截图+字幕材料。
- 请只处理你有权学习、分析或二创的素材。
- AI Agent 不直接解析抖音/小红书链接，必须先转换成本地视频文件。
- 这个网站只写在 `START_HERE.md` 作为学员操作说明，不写进 skill 核心逻辑。

---

## 第 4 步：本地视频 / 直链视频必须先预处理

环境检测通过、素材是本地视频或直链视频后，运行预处理。

macOS / Linux：

```bash
./bin/slbb-video-ingest \
  --run-dir "./AI长剧工作流/项目名" \
  --video "/path/to/reference.mp4" \
  --interval 1.5 \
  --model small
```

Windows：

```powershell
.\bin\slbb-video-ingest.cmd `
  --run-dir ".\AI长剧工作流\项目名" `
  --video "C:\path\to\reference.mp4" `
  --interval 1.5 `
  --model small
```

它会生成：

```text
artifacts/_audit/video_ingest/video_meta.json
artifacts/_audit/video_ingest/contact_sheet.jpg
artifacts/_audit/video_ingest/keyframes/
artifacts/_audit/video_ingest/transcript.txt
artifacts/_audit/video_ingest/transcript.json
artifacts/_audit/video_ingest/shot_index.json
artifacts/_audit/video_ingest/ingest_report.md
```

后续长剧 S1 只读取：

```text
artifacts/_source/source_brief.md
artifacts/_source/source_manifest.json
artifacts/_audit/video_ingest/ingest_report.md
artifacts/_audit/video_ingest/shot_index.json
artifacts/_audit/video_ingest/contact_sheet.jpg
artifacts/_audit/video_ingest/transcript.txt
```

不要在聊天里粘贴完整视频分析、完整字幕、逐帧拆解或整包过程文件。

---

## 第 5 步：只有截图 / 字幕 / 口述时走降级路径

如果客户无法下载视频，只能提供截图、字幕或口述材料，可以继续，但必须登记为降级输入：

```bash
./bin/slbb-video-source "./AI长剧工作流/项目名" --source-kind partial_material --source-ref "/path/to/materials"
```

Windows：

```powershell
.\bin\slbb-video-source.cmd ".\AI长剧工作流\项目名" --source-kind partial_material --source-ref "C:\path\to\materials"
```

S1 输出必须提醒：

```text
当前输入不是完整视频，只能做低置信度复刻分析。
如需更高质量，请补充本地视频文件或录屏文件。
```

降级路径不能伪装成完整视频拆解。

---

## 第 6 步：选择启动方式

### 方式 A — 短剧手工启动

macOS / Linux：

```bash
./bin/slbb-video-init "./AI短剧工作流/项目名" --title "短剧标题"
cp examples/sample-inputs/source-note-template.md \
   "./AI短剧工作流/项目名/artifacts/S1/source_note.md"
```

Windows：

```powershell
.\bin\slbb-video-init.cmd ".\AI短剧工作流\项目名" --title "短剧标题"
Copy-Item .\examples\sample-inputs\source-note-template.md ".\AI短剧工作流\项目名\artifacts\S1\source_note.md"
```

让客户填好 `source_note.md` 后，让当前 AI Agent 按 `skills/slbb-video-research-script/SKILL.md` 执行 S1。

### 方式 B — V2 handoff 启动

macOS / Linux：

```bash
./bin/slbb-video-from-handoff "/path/to/handoff.md" "./AI长剧工作流/项目名"
```

Windows：

```powershell
.\bin\slbb-video-from-handoff.cmd "C:\path\to\handoff.md" ".\AI长剧工作流\项目名"
```

如果 handoff 里是平台链接，仍然要先下载成本地视频并运行 ingest，不能直接进 S1。

### 方式 C — 低 token 长剧启动

macOS / Linux：

```bash
./bin/slbb-video-init "./AI长剧工作流/项目名" --title "项目名" --mode long_drama
./bin/slbb-video-source "./AI长剧工作流/项目名" --source-ref "/path/to/reference.mp4"
./bin/slbb-video-ingest --run-dir "./AI长剧工作流/项目名" --video "/path/to/reference.mp4"
```

Windows：

```powershell
.\bin\slbb-video-init.cmd ".\AI长剧工作流\项目名" --title "项目名" --mode long_drama
.\bin\slbb-video-source.cmd ".\AI长剧工作流\项目名" --source-ref "C:\path\to\reference.mp4"
.\bin\slbb-video-ingest.cmd --run-dir ".\AI长剧工作流\项目名" --video "C:\path\to\reference.mp4"
```

然后让客户补 `artifacts/_source/source_brief.md`，或只根据客户提供的 6-10 条关键时间点补 brief。

---

## 第 7 步：阶段执行规则

- 每次只跑 `./bin/slbb-video-next` 指向的那一个阶段，不要一次跑完 S1-S8。
- 长剧 S1 必须调用 `slbb-video-long-replica-script`。
- 长剧 S1 不生成视频提示词、不生成分镜提示词、不生成成片脚本、不生成封面文案。
- S2 完成后只处理 `current_segment` 指向的单片段，默认 `001`。
- 阶段要标 `completed` 之前必须停下来等客户确认。
- 绝对不要替客户加 `--human-confirmed`。
- validator 失败时把失败原因原样贴出，不要自己跳。
- 跨对话继续时，先读 `artifacts/_handoff/next_step.md`。

---

## 工具清单速查

| 路径 | 用途 |
|------|------|
| `bin/slbb-video-doctor` / `bin/slbb-video-doctor.cmd` | 检测视频预处理环境 |
| `bin/slbb-video-setup` / `bin/slbb-video-setup.cmd` | 安装包内 Python 视频依赖 |
| `bin/slbb-video-init` / `bin/slbb-video-init.cmd` | 手工初始化 run |
| `bin/slbb-video-source` / `bin/slbb-video-source.cmd` | 判断并登记长剧素材 |
| `bin/slbb-video-ingest` / `bin/slbb-video-ingest.cmd` | 生成低 token 视频证据包 |
| `bin/slbb-video-from-handoff` / `bin/slbb-video-from-handoff.cmd` | 从 V2 handoff 初始化 run |
| `bin/slbb-video-next` / `bin/slbb-video-next.cmd` | 写 handoff 推进到下一阶段 |
| `bin/slbb-video-advance` / `bin/slbb-video-advance.cmd` | 改阶段状态 |
| `bin/slbb-video-validate` / `bin/slbb-video-validate.cmd` | 校验 state + 阶段产物 |
| `bin/slbb-video.py` | 跨平台 Python 分发器 |
| `skills/` | 10 个 slbb-video-* skill |
| `docs/` | Onboarding、环境安装、视频来源、产物契约、人工闸门等文档 |

看到 `next_step.md` 说什么就做什么。不明白就问客户，不要猜。
