# 视频来源处理说明

长剧 S1 不直接读取完整视频和平台链接。先把素材变成低 token 证据包，再进入 S1。

## 来源类型

| 类型 | 说明 | 能否直接进 S1 |
| --- | --- | --- |
| `local_video` | 本地 `.mp4` / `.mov` / `.mkv` / `.webm` 文件 | 不能，必须先 ingest |
| `direct_video_url` | 直接指向视频文件的 URL | 不能，必须先 ingest |
| `platform_link` | 抖音 / 小红书 / 快手 / B 站分享页 | 不能，必须先下载或录屏成本地视频 |
| `partial_material` | 截图、字幕、台词、口述材料 | 可以降级进入，但必须标记低置信度 |

## 平台链接处理

如果用户提供抖音 / 小红书 / 快手 / B 站链接，先让用户下载成本地视频。

可选第三方工具：

```text
https://sv.bugpk.com/
```

失败时用：

- 录屏
- 平台自带保存
- 截图 + 字幕材料

注意：第三方工具不写进 skill 核心逻辑，只作为学员操作说明。

## 本地视频处理

```bash
./bin/slbb-video-source "./AI长剧工作流/项目名" --source-ref "/path/to/reference.mp4"
./bin/slbb-video-ingest --run-dir "./AI长剧工作流/项目名" --video "/path/to/reference.mp4"
```

Windows：

```powershell
.\bin\slbb-video-source.cmd ".\AI长剧工作流\项目名" --source-ref "C:\path\to\reference.mp4"
.\bin\slbb-video-ingest.cmd --run-dir ".\AI长剧工作流\项目名" --video "C:\path\to\reference.mp4"
```

## 预处理产物

```text
artifacts/_audit/video_ingest/video_meta.json
artifacts/_audit/video_ingest/contact_sheet.jpg
artifacts/_audit/video_ingest/keyframes/
artifacts/_audit/video_ingest/transcript.txt
artifacts/_audit/video_ingest/transcript.json
artifacts/_audit/video_ingest/shot_index.json
artifacts/_audit/video_ingest/ingest_report.md
```

S1 只读这些证据和 `source_brief.md`，不要重复读取完整视频。
