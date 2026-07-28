# 新人 Onboarding：5 分钟跑通第一条 S1

> 本文档写给"今天第一次拿到这个包"的团队成员。跟着走一遍 5 分钟，你应该能把 S1 跑通并停在人工闸门。
> 完成 5 步即达标，第 6 步是可选项。

## 1. 拿到包后 30 秒检查

macOS / Linux：

```bash
cd /path/to/AI短剧工作流模版包
ls bin/                  # 应该有 9 个无后缀脚本 + 9 个 Windows .cmd + slbb-video.py
chmod +x bin/slbb-video-{advance,doctor,from-handoff,ingest,init,next,setup,source,validate}  # 只修改 macOS/Linux 入口
./bin/slbb-video-doctor  # 视频预处理前必须先检查环境
ls skills/               # 应该有 10 个 slbb-video-* 目录
python3 --version        # 需要 Python 3.10+
```

Windows PowerShell：

```powershell
cd C:\path\to\AI短剧工作流模版包
Get-ChildItem .\bin       # 应该能看到 slbb-video-init.cmd / slbb-video-ingest.cmd 等 9 个 .cmd
.\bin\slbb-video-doctor.cmd
Get-ChildItem .\skills    # 应该有 10 个 slbb-video-* 目录
py -3 --version           # 需要 Python 3.10+；不行就试 python --version
```

环境要求（任一不满足就先解决）：

- macOS / Linux Terminal，或 Windows PowerShell / cmd
- Python 3.10+
- 长剧本地视频预处理需要 ffmpeg / ffprobe / faster-whisper
- 不要 `sudo` 执行任何命令

## 2. 启动你的第一个 run（1 分钟）

跑通 init 命令，把 run 目录创建出来。

```bash
./bin/slbb-video-init "./AI短剧工作流/onboard_demo" --title "我的第一个测试"
```

Windows：

```powershell
.\bin\slbb-video-init.cmd ".\AI短剧工作流\onboard_demo" --title "我的第一个测试"
```

应当看到：

```text
Created: .../AI短剧工作流/onboard_demo/workflow_state.json
Created: .../AI短剧工作流/onboard_demo/artifacts/_handoff/next_step.md
```

## 3. 复制一份已填好的 source note（30 秒）

从 `examples/sample-inputs/source-note-FILLED.md` 复制到你的 run 目录 S1 输入位置：

```bash
cp examples/sample-inputs/source-note-FILLED.md \
   "./AI短剧工作流/onboard_demo/artifacts/S1/source_note.md"
```

Windows：

```powershell
Copy-Item .\examples\sample-inputs\source-note-FILLED.md ".\AI短剧工作流\onboard_demo\artifacts\S1\source_note.md"
```

> **如果你从 V2 监控台（ai-drama-monitor）导出了 handoff.md**：跳过本步，改用 `slbb-video-from-handoff`，source 字段会自动写入。
> **如果你做 AI 长剧并且素材是本地视频/录屏/字幕**：不要复制 `source-note-FILLED.md`，改用 `slbb-video-source` 登记素材，再用 `slbb-video-ingest` 生成 `artifacts/_audit/video_ingest/` 后再跑长剧 S1。
> **如果素材是抖音/小红书等平台链接**：先按 `START_HERE.md` 下载或录屏成本地视频，不要直接进 S1。

## 4. 让当前 AI Agent 跑 S1（2 分钟）

让当前 AI Agent 按 `skills/slbb-video-research-script/SKILL.md` 执行：

```text
请按 skills/slbb-video-research-script/SKILL.md，处理 ./AI短剧工作流/onboard_demo
```

Skill 完成后会写两个文件：

```text
artifacts/S1/story_extract.md
artifacts/S1/story_segments.json
artifacts/_meta/S1_segmentation_decision.md
```

S1 会**自己停在人工闸门**，不会自动跑 S2。

## 5. 推进状态 + 验证（1 分钟）

回到 shell 跑这两条：

```bash
./bin/slbb-video-advance "./AI短剧工作流/onboard_demo" \
    --stage S1 --status ready_for_human \
    --note "等待确认剧情拆分"

./bin/slbb-video-validate "./AI短剧工作流/onboard_demo"
```

Windows：

```powershell
.\bin\slbb-video-advance.cmd ".\AI短剧工作流\onboard_demo" --stage S1 --status ready_for_human --note "等待确认剧情拆分"
.\bin\slbb-video-validate.cmd ".\AI短剧工作流\onboard_demo"
```

如果看到 `Orchestrator validation passed.`，S1 就跑通了。

人工确认后：

```bash
./bin/slbb-video-advance "./AI短剧工作流/onboard_demo" \
    --stage S1 --status completed --human-confirmed \
    --note "剧情拆分已确认"
```

跑 `./bin/slbb-video-next "./AI短剧工作流/onboard_demo"`，会推进到 S2。

## 6.（可选项）从 V2 handoff 启动

如果你手里有 V2 监控台导出的 `handoff.md`，可以不复制 `source_note.md`，直接这样启动：

```bash
./bin/slbb-video-from-handoff "/path/to/handoff.md" "./AI长剧工作流/from_v2_demo"
./bin/slbb-video-validate "./AI长剧工作流/from_v2_demo"
```

Windows：

```powershell
.\bin\slbb-video-from-handoff.cmd "C:\path\to\handoff.md" ".\AI长剧工作流\from_v2_demo"
.\bin\slbb-video-validate.cmd ".\AI长剧工作流\from_v2_demo"
```

## 7. 接下来看哪些文档

- 完整命令清单：`QUICKSTART.md`
- 角色分工 + 每日交接：`TEAM_SOP.md`
- 视频环境安装：`docs/environment-setup.md`
- 视频来源处理：`docs/video-source-guide.md`
- 8 步工作流地图：`docs/workflow-map.md`
- 产物契约：`docs/artifact-contract.md`
- 人工闸门规则：`docs/human-gates.md`
- 状态文件 schema：`skills/slbb-video-orchestrator/references/state_schema.md`

## 常见卡点

| 卡点 | 解决方式 |
| --- | --- |
| `chmod: cannot access 'bin/*': No such file or directory` | 先确认自己在包根目录；Windows 不需要 `chmod` |
| `python3: command not found` | macOS 装 Python 3.10+（可用 `brew install python@3.11`）；Windows 用 `py -3 --version` 或重新安装 Python 并勾选 Add to PATH |
| Windows 提示 `'.\bin\slbb-video-init.cmd' 不是内部或外部命令` | 先 `Get-ChildItem .\bin`，确认在包根目录；也可以改用 `py -3 .\bin\slbb-video.py init ...` |
| `ModuleNotFoundError: No module named 'workflow_lib'` | 不要直接跑某个 validator 文件；macOS / Linux 用 `./bin/slbb-video-validate`，Windows 用 `.\bin\slbb-video-validate.cmd` |
| V2 handoff 报"missing 视频链接" | handoff.md 第 1 节必须有 `**视频链接**：<url>`，V2 导出会自带；如果手写 fixture 漏了 |
| S1 validator 报"missing array: episodes" | `story_segments.json` 顶层必须有 `episodes: [...]`；S1 拆分决策没生效时常见 |
| S2 后不知道下一步 | 跑 `./bin/slbb-video-next "./AI短剧工作流/onboard_demo"`，Windows 跑 `.\bin\slbb-video-next.cmd ".\AI短剧工作流\onboard_demo"`，看 `artifacts/_handoff/next_step.md` 顶部 |
