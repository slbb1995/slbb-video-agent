# 视频预处理环境安装说明

本包默认先检测环境，再由用户确认是否安装。AI Agent 不要静默安装任何依赖。

## 必需环境

- Python 3.10+
- ffmpeg
- ffprobe
- 包内 `.venv`
- `.venv` 里的 `faster-whisper`

## 第一步：检测

macOS / Linux：

```bash
./bin/slbb-video-doctor
```

Windows：

```powershell
.\bin\slbb-video-doctor.cmd
```

如果检测失败，把缺失项展示给用户，等用户确认后再安装。

## 第二步：安装 Python 视频依赖

macOS / Linux：

```bash
./bin/slbb-video-setup --video
```

Windows：

```powershell
.\bin\slbb-video-setup.cmd --video
```

依赖安装到包内 `.venv`，不污染全局 Python。

如果 AI Agent 只安装了单独的 `slbb-video-orchestrator` skill，没有完整项目根目录，也在该 skill 目录运行同样命令：

macOS / Linux：

```bash
./bin/slbb-video-setup --video
```

Windows：

```powershell
.\bin\slbb-video-setup.cmd --video
```

脚本会在当前项目或当前 skill 目录创建 `.venv`，并安装旁边的 `requirements-video.txt`。

## 第三步：安装 ffmpeg / ffprobe

macOS：

```bash
brew install ffmpeg
```

Windows：

```powershell
winget install Gyan.FFmpeg
```

如果 Windows 没有 winget，手动安装 ffmpeg，并把 ffmpeg 的 `bin` 目录加入 PATH。

## 第四步：复查

安装后重新运行：

```bash
./bin/slbb-video-doctor
```

Windows：

```powershell
.\bin\slbb-video-doctor.cmd
```

只有 doctor 通过后，才进入 `slbb-video-ingest`。

注意：第一次运行 `slbb-video-ingest --model small` 时，`faster-whisper` 可能需要下载模型文件，耗时取决于网络。后续同一电脑会复用缓存。

## 转写环境查找顺序

`slbb-video-ingest` 默认按这个顺序寻找能导入 `faster_whisper` 的 Python：

1. `--transcript-python` 参数指定的 Python。
2. `SLBB_VIDEO_PYTHON` 环境变量。
3. `SLBB_VIDEO_VENV_PYTHON` 环境变量。
4. 当前项目根目录或单独 skill 目录下的 `.venv`。
5. 当前正在运行脚本的 Python。

如果找不到，会停在转写前并输出修复建议。此时可以先运行 `slbb-video-setup --video`，或者临时加 `--skip-transcript` 只生成抽帧、contact sheet 和 shot index。
