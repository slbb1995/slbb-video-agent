#!/usr/bin/env python3
"""Create a low-token evidence packet from a local/direct video source."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from workflow_lib import load_state, save_state, utc_now
from video_env_lib import resolve_project_root, resolve_python_with_module


VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi"}
PLATFORM_DOMAINS = {
    "douyin.com",
    "iesdouyin.com",
    "xiaohongshu.com",
    "xhslink.com",
    "kuaishou.com",
    "kuaishouapp.com",
    "bilibili.com",
    "b23.tv",
}


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def hostname(value: str) -> str:
    return (urlparse(value).netloc or "").lower()


def is_platform_link(value: str) -> bool:
    host = hostname(value)
    return any(host == domain or host.endswith("." + domain) for domain in PLATFORM_DOMAINS)


def is_direct_video_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and Path(parsed.path).suffix.lower() in VIDEO_SUFFIXES


def run_capture(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return result.returncode, result.stdout, result.stderr


def require_binary(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise RuntimeError(f"missing {name}; run slbb-video-doctor and install ffmpeg first")
    return found


def ffprobe_json(ffprobe: str, video: str) -> dict:
    code, stdout, stderr = run_capture(
        [ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", video]
    )
    if code != 0:
        raise RuntimeError(stderr.strip() or f"ffprobe failed for {video}")
    return json.loads(stdout)


def duration_seconds(meta: dict) -> float:
    raw = (meta.get("format") or {}).get("duration")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def has_audio(meta: dict) -> bool:
    return any(stream.get("codec_type") == "audio" for stream in meta.get("streams", []))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def transcribe_audio(audio_path: Path, json_out: Path, txt_out: Path, model_name: str) -> int:
    from faster_whisper import WhisperModel  # type: ignore

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(audio_path), vad_filter=True)
    rows: list[dict] = []
    lines: list[str] = []
    for segment in segments:
        text = segment.text.strip()
        row = {
            "start": round(float(segment.start), 3),
            "end": round(float(segment.end), 3),
            "text": text,
        }
        rows.append(row)
        lines.append(f"[{row['start']:0.3f}-{row['end']:0.3f}] {text}")
    write_json(
        json_out,
        {
            "created_at": utc_now(),
            "model": model_name,
            "language": getattr(info, "language", None),
            "language_probability": getattr(info, "language_probability", None),
            "segments": rows,
        },
    )
    txt_out.write_text("\n".join(lines).strip() + ("\n" if lines else ""), encoding="utf-8")
    return 0


def run_transcription(
    run_dir: Path,
    audio_path: Path,
    json_out: Path,
    txt_out: Path,
    model_name: str,
    project_root: Path,
    transcript_python: str | None,
) -> int:
    py, notes = resolve_python_with_module(
        "faster_whisper",
        run_dir=run_dir,
        explicit_root=str(project_root),
        explicit_python=transcript_python,
    )
    if not py:
        print("ERROR: cannot find a Python environment that can import faster_whisper.")
        print("Checked candidates:")
        for note in notes:
            print(f"- {note}")
        print("\nFix:")
        print("- From the slbb-video-agent project root, run `./bin/slbb-video-setup --video`.")
        print("- Windows: run `.\\bin\\slbb-video-setup.cmd --video`.")
        print("- If using a standalone skill copy, run `python scripts/setup_video_env.py --video --project-root <skill-or-project-root>`.")
        print("- Or set SLBB_VIDEO_PYTHON to the Python executable inside the correct .venv.")
        return 127
    cmd = [str(py), str(Path(__file__).resolve()), "_transcribe_audio", str(audio_path), str(json_out), str(txt_out), model_name]
    return subprocess.run(cmd, check=False).returncode


def build_shot_index(video: str, duration: float, interval: float, frame_paths: list[Path], out_dir: Path) -> dict:
    frames = []
    for index, frame in enumerate(frame_paths, start=1):
        start = round((index - 1) * interval, 3)
        frames.append(
            {
                "id": f"frame_{index:04d}",
                "time_seconds": start,
                "path": str(frame.relative_to(out_dir.parent.parent.parent)),
            }
        )
    last_time = frames[-1]["time_seconds"] if frames else 0.0
    coverage = 1.0 if duration <= 0 else min((last_time + interval) / duration, 1.0)
    return {
        "created_at": utc_now(),
        "source_video": video,
        "duration_seconds": duration,
        "interval_seconds": interval,
        "frame_count": len(frames),
        "coverage_ratio": round(coverage, 4),
        "frames": frames,
    }


def update_source_files(run_dir: Path, video: str, source_kind: str, ingest_rel: str, shot_rel: str) -> None:
    source_dir = run_dir / "artifacts" / "_source"
    source_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = source_dir / "source_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "created_at": utc_now(),
            "mode": "long_drama",
            "source_ref": video,
            "source_brief": "artifacts/_source/source_brief.md",
        }
    manifest["updated_at"] = utc_now()
    manifest["source_kind"] = source_kind
    manifest["source_ref"] = video
    manifest["evidence_quality"] = "complete"
    manifest["video_ingest"] = ingest_rel
    manifest["shot_index"] = shot_rel
    manifest["raw_material_policy"] = (
        "S1 reads the concise source brief plus video_ingest evidence packet. "
        "Do not paste the full video, full transcript, or all frame files into chat."
    )
    write_json(manifest_path, manifest)

    note_path = source_dir / "source_note.md"
    note_path.write_text(
        f"""# 视频素材来源说明

- 素材类型：{source_kind}
- 素材位置：{video}
- 证据质量：complete
- 预处理报告：{ingest_rel}
- 镜头索引：{shot_rel}

S1 只能读取精简 brief 和预处理证据包，不要重新吞完整视频。
""",
        encoding="utf-8",
    )

    try:
        state = load_state(run_dir)
    except Exception:
        return
    source = state.setdefault("source", {})
    source["source_kind"] = source_kind
    source["source_ref"] = video
    source["source_manifest"] = "artifacts/_source/source_manifest.json"
    source["source_note"] = "artifacts/_source/source_note.md"
    source["video_ingest"] = ingest_rel
    source["shot_index"] = shot_rel
    source["evidence_quality"] = "complete"
    s1 = state.get("stages", {}).get("S1")
    if s1 and s1.get("status") == "blocked":
        s1["status"] = "pending"
        s1.setdefault("notes", []).append({"at": utc_now(), "text": "Video ingest completed; S1 prerequisites can be checked again."})
    save_state(run_dir, state)


def write_report(
    path: Path,
    video: str,
    duration: float,
    frame_count: int,
    contact_sheet_rel: str,
    transcript_status: str,
    coverage_ratio: float,
) -> None:
    path.write_text(
        f"""# 视频预处理报告

## 输入

- 视频来源：{video}
- 时长秒数：{duration:.3f}

## 已生成证据

- 关键帧数量：{frame_count}
- 接触图：{contact_sheet_rel}
- 转写状态：{transcript_status}
- 画面覆盖率：{coverage_ratio:.2%}

## S1 使用规则

- S1 先读 `artifacts/_source/source_brief.md`。
- 需要核画面时读 `artifacts/_audit/video_ingest/contact_sheet.jpg` 和 `shot_index.json`。
- 需要核台词时读 `artifacts/_audit/video_ingest/transcript.txt`。
- 不要把完整视频、完整字幕、全部关键帧重复贴进聊天。
""",
        encoding="utf-8",
    )


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "_transcribe_audio":
        return transcribe_audio(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5])

    parser = argparse.ArgumentParser(description="Create video evidence packet for long-drama S1")
    parser.add_argument("--run-dir", required=True, help="Workflow run directory")
    parser.add_argument("--video", required=True, help="Local video path or direct video URL")
    parser.add_argument("--interval", type=float, default=1.5, help="Keyframe interval in seconds")
    parser.add_argument("--model", default="small", help="faster-whisper model name")
    parser.add_argument("--max-keyframes", type=int, default=120)
    parser.add_argument("--skip-transcript", action="store_true", help="Skip faster-whisper transcription")
    parser.add_argument("--project-root", help="slbb-video-agent project root or standalone skill root")
    parser.add_argument("--transcript-python", help="Python executable that can import faster_whisper")
    args = parser.parse_args()

    video = args.video
    if is_platform_link(video) and not is_direct_video_url(video):
        print("ERROR: platform links cannot be ingested directly.")
        print("请先用 START_HERE.md 里的方式下载成本地视频，或提供录屏/截图+字幕材料。")
        return 2
    if not is_url(video):
        local_video = Path(video).expanduser()
        if not local_video.exists():
            print(f"ERROR: local video not found: {local_video}")
            return 1
        video = str(local_video.resolve())

    run_dir = Path(args.run_dir).expanduser().resolve()
    project_root = resolve_project_root(run_dir=run_dir, explicit_root=args.project_root)
    out_dir = run_dir / "artifacts" / "_audit" / "video_ingest"
    keyframes_dir = out_dir / "keyframes"
    out_dir.mkdir(parents=True, exist_ok=True)
    keyframes_dir.mkdir(parents=True, exist_ok=True)

    try:
        ffmpeg = require_binary("ffmpeg")
        ffprobe = require_binary("ffprobe")
        meta = ffprobe_json(ffprobe, video)
    except Exception as exc:  # noqa: BLE001 - CLI should print the exact blocker
        print(f"ERROR: {exc}")
        return 1

    video_meta_path = out_dir / "video_meta.json"
    write_json(video_meta_path, meta)
    duration = duration_seconds(meta)

    for old in keyframes_dir.glob("frame_*.jpg"):
        old.unlink()
    vf = f"fps=1/{args.interval},scale=640:-1"
    code, _stdout, stderr = run_capture(
        [
            ffmpeg,
            "-y",
            "-i",
            video,
            "-vf",
            vf,
            "-frames:v",
            str(args.max_keyframes),
            str(keyframes_dir / "frame_%04d.jpg"),
        ]
    )
    if code != 0:
        print("ERROR: ffmpeg keyframe extraction failed")
        print(stderr.strip())
        return code

    frame_paths = sorted(keyframes_dir.glob("frame_*.jpg"))
    contact_sheet = out_dir / "contact_sheet.jpg"
    if frame_paths:
        cols = 5
        rows = max(1, math.ceil(len(frame_paths) / cols))
        code, _stdout, stderr = run_capture(
            [
                ffmpeg,
                "-y",
                "-framerate",
                "1",
                "-i",
                str(keyframes_dir / "frame_%04d.jpg"),
                "-vf",
                f"scale=320:-1,tile={cols}x{rows}:padding=8:margin=8",
                "-frames:v",
                "1",
                str(contact_sheet),
            ]
        )
        if code != 0:
            print("ERROR: ffmpeg contact sheet generation failed")
            print(stderr.strip())
            return code
    else:
        print("ERROR: no keyframes were extracted")
        return 1

    transcript_json = out_dir / "transcript.json"
    transcript_txt = out_dir / "transcript.txt"
    transcript_status = "skipped"
    if args.skip_transcript:
        write_json(transcript_json, {"created_at": utc_now(), "segments": [], "note": "transcription skipped"})
        transcript_txt.write_text("", encoding="utf-8")
    elif not has_audio(meta):
        transcript_status = "no audio stream"
        write_json(transcript_json, {"created_at": utc_now(), "segments": [], "note": "no audio stream detected"})
        transcript_txt.write_text("", encoding="utf-8")
    else:
        with tempfile.TemporaryDirectory(prefix="slbb_audio_") as tmp:
            audio_path = Path(tmp) / "audio.wav"
            code, _stdout, stderr = run_capture(
                [ffmpeg, "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", str(audio_path)]
            )
            if code != 0:
                print("ERROR: ffmpeg audio extraction failed")
                print(stderr.strip())
                return code
            code = run_transcription(
                run_dir,
                audio_path,
                transcript_json,
                transcript_txt,
                args.model,
                project_root,
                args.transcript_python,
            )
            if code != 0:
                print("ERROR: faster-whisper transcription failed")
                return code
            transcript_status = f"ok ({args.model})"

    shot_index_path = out_dir / "shot_index.json"
    shot_index = build_shot_index(video, duration, args.interval, frame_paths, out_dir)
    write_json(shot_index_path, shot_index)

    report_path = out_dir / "ingest_report.md"
    contact_rel = str(contact_sheet.relative_to(run_dir))
    report_rel = str(report_path.relative_to(run_dir))
    shot_rel = str(shot_index_path.relative_to(run_dir))
    write_report(
        report_path,
        video,
        duration,
        len(frame_paths),
        contact_rel,
        transcript_status,
        float(shot_index.get("coverage_ratio") or 0),
    )

    source_kind = "direct_video_url" if is_direct_video_url(video) else "local_video"
    update_source_files(run_dir, video, source_kind, report_rel, shot_rel)

    print(f"Video metadata: {video_meta_path}")
    print(f"Keyframes: {keyframes_dir}")
    print(f"Contact sheet: {contact_sheet}")
    print(f"Transcript: {transcript_txt}")
    print(f"Shot index: {shot_index_path}")
    print(f"Ingest report: {report_path}")
    print("Next: fill/confirm artifacts/_source/source_brief.md, then run slbb-video-next.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
