# 低 token 版：AI 长剧工作流启动提示词

```text
/slbb-video-orchestrator

使用 slbb-video-orchestrator 启动 AI 长剧工作流。

workflow mode：
long_drama

AI 长剧生成过程文件目录：
./AI长剧工作流/<填写项目文件夹名>

已确定的对标素材：
<只写视频链接或本地视频路径；如果是抖音/小红书等平台链接，先下载成本地视频；不要粘贴完整视频分析、完整字幕、逐帧拆解>

要求：
1. 先运行环境检测，不要静默安装：
   macOS / Linux：./bin/slbb-video-doctor
   Windows：.\bin\slbb-video-doctor.cmd
2. 如果缺 ffmpeg / ffprobe / .venv / faster-whisper，先把缺失项告诉我，问我是否安装；不要直接继续。
3. 先检查该目录是否已有 workflow_state.json；没有就初始化：
   macOS / Linux：./bin/slbb-video-init "./AI长剧工作流/<项目名>" --title "<项目名>" --mode long_drama
   Windows：.\bin\slbb-video-init.cmd ".\AI长剧工作流\<项目名>" --title "<项目名>" --mode long_drama
4. 使用 slbb-video-source 判断素材类型，不直接分析完整视频：
   macOS / Linux：./bin/slbb-video-source "./AI长剧工作流/<项目名>" --source-ref "<本地视频路径或链接>"
   Windows：.\bin\slbb-video-source.cmd ".\AI长剧工作流\<项目名>" --source-ref "<本地视频路径或链接>"
5. 如果识别为 platform_link（抖音/小红书/快手/B站等），停止，提醒我先用 https://sv.bugpk.com/ 或录屏等方式下载成本地视频，再继续。
6. 如果识别为 local_video 或 direct_video_url，先运行 slbb-video-ingest：
   macOS / Linux：./bin/slbb-video-ingest --run-dir "./AI长剧工作流/<项目名>" --video "<本地视频路径或直链>"
   Windows：.\bin\slbb-video-ingest.cmd --run-dir ".\AI长剧工作流\<项目名>" --video "<本地视频路径或直链>"
7. 让我补全 artifacts/_source/source_brief.md，或你只根据我提供的 6-10 条关键时间点补 brief。
8. 生成并读取 artifacts/_handoff/next_step.md。
9. 当前只执行 S1，并且 S1 必须调用 slbb-video-long-replica-script。
10. S1 只读取 artifacts/_source/source_brief.md、artifacts/_source/source_manifest.json 和 artifacts/_audit/video_ingest/ 证据包；不要重复读取完整视频、录屏、长字幕或整包过程文件。
11. S1 只做原视频复刻描述、二创描述、角色形象提取和 3-15 秒片段拆分。
12. S1 不生成视频提示词、不生成分镜提示词、不生成成片脚本、不生成封面文案。
13. S1 产物必须真实保存到 artifacts/S1 和 artifacts/_meta，不要只在聊天里展示。
14. S1 必须通过校验，并停在人工确认门；不要进入 S2。
```

## 为什么这样写

- 平台链接不能直接进 S1；必须先下载/录屏成本地视频，或走截图/字幕降级路径。
- 本地视频必须先被 `slbb-video-ingest` 处理成低 token 证据包。
- `source_brief.md` 和 `video_ingest` 是高频读取输入，后续 S1/S2/S3 都不该反复读取原始大素材。
- 42 秒视频一般只需要 6-10 条时间点、2-4 个角色视觉锚点、关键台词摘要。
