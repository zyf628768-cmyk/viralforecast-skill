"""FFmpeg media processing. No remote calls or inferred visual semantics."""
import importlib
import os
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageStat

from .common import ForecastError, number, read_json


def binary(name):
    explicit = os.environ.get(name.upper())
    if explicit:
        found = shutil.which(explicit)
        if found:
            return found
        raise ForecastError(f"{name.upper()} points to a missing executable: {explicit}")
    found = shutil.which(name)
    if found:
        return found
    if name == "ffmpeg":
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except (ImportError, RuntimeError):
            pass
    raise ForecastError(f"Missing {name}. Install FFmpeg + FFprobe and set {name.upper()} to its executable.")


def run(args, timeout=180):
    try:
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ForecastError(f"Media process failed: {exc}") from exc
    if p.returncode:
        raise ForecastError(f"{Path(args[0]).name} failed: {p.stderr[-2000:]}")
    return p


def local_file(path):
    p = Path(path)
    if not p.is_file() or not p.stat().st_size:
        raise ForecastError(f"Missing or empty local file: {path}")
    return p.resolve()


def transcript(path=None, adapter=None, audio=None, duration=None):
    if path and adapter:
        raise ForecastError("Choose transcript JSON or local transcriber, not both")
    data = None
    if path:
        data = read_json(path)
    elif adapter:
        if audio is None:
            raise ForecastError("Transcription requires an audio track")
        try:
            module, func = adapter.split(":")
            data = getattr(importlib.import_module(module), func)(str(audio))
        except Exception as exc:
            raise ForecastError(f"Local transcription adapter failed: {exc}") from exc
    if data is None:
        return {"status": "not_run", "segments": []}
    if not isinstance(data, dict) or not isinstance(data.get("segments"), list):
        raise ForecastError("Transcript must contain a segments array")
    last = 0.0
    for s in data["segments"]:
        if not isinstance(s, dict) or not isinstance(s.get("text"), str):
            raise ForecastError("Each transcript segment needs text, start and end")
        start = number(s.get("start"), "segment.start")
        end = number(s.get("end"), "segment.end")
        if start < last or end <= start or (duration is not None and end > duration + 0.1):
            raise ForecastError("Transcript segments must be ordered, non-overlapping and inside video")
        last = end
    return {"status": "imported" if path else "local_adapter", "segments": data["segments"]}


def inspect_video(path, output, transcript_path=None, adapter=None, cover=None):
    import json
    source = local_file(path)
    ffmpeg, ffprobe = binary("ffmpeg"), binary("ffprobe")
    meta = json.loads(run([ffprobe, "-v", "error", "-protocol_whitelist", "file,pipe,crypto,data", "-show_format", "-show_streams", "-of", "json", str(source)]).stdout)
    video = next((s for s in meta.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video:
        raise ForecastError("Input has no video stream")
    duration = number(meta.get("format", {}).get("duration", video.get("duration")), "duration", 0.01, 7200)
    dest = Path(output).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    # Restrict protocols even for media containing playlist or network references.
    base = [ffmpeg, "-nostdin", "-y", "-protocol_whitelist", "file,pipe,crypto,data", "-i", str(source)]
    scenes = run(base + ["-an", "-vf", "scale=160:-2,select='gt(scene,0.30)',showinfo", "-f", "null", "-"])
    cuts = [float(v) for v in re.findall(r"pts_time:([\d.]+)", scenes.stderr)]
    frames = []
    for i, t in enumerate(sorted(set([0, min(1, duration / 3), min(3, duration / 2), duration * .75]))):
        target = dest / f"frame-{i:02}.jpg"
        run([ffmpeg, "-nostdin", "-y", "-protocol_whitelist", "file,pipe,crypto,data", "-ss", str(t), "-i", str(source), "-frames:v", "1", "-vf", "scale=320:-2", str(target)])
        frames.append({"time": t, "path": str(target)})
    audio = None
    if any(s.get("codec_type") == "audio" for s in meta["streams"]):
        audio = dest / "audio.wav"
        run(base + ["-vn", "-ac", "1", "-ar", "16000", str(audio)])
    tr = transcript(transcript_path, adapter, audio, duration)
    cover_metrics = None
    if cover:
        p = local_file(cover)
        try:
            with Image.open(p) as im:
                im.thumbnail((512, 512))
                gray = im.convert("L")
                stat = ImageStat.Stat(gray)
                cover_metrics = {"path": str(p), "sample_width": im.width, "sample_height": im.height,
                                 "brightness": stat.mean[0] / 255, "contrast": stat.stddev[0] / 255,
                                 "semantics": "not_implemented"}
        except (OSError, ValueError) as exc:
            raise ForecastError(f"Invalid cover image: {exc}") from exc
    return {"duration_seconds": duration, "width": video["width"], "height": video["height"],
            "codec": video.get("codec_name"), "frame_rate": video.get("avg_frame_rate"),
            "scene_times": cuts, "scene_count": len(cuts), "first_3s_cuts": sum(t < 3 for t in cuts),
            "cut_rate": len(cuts) / duration, "keyframes": frames, "audio_path": str(audio) if audio else None,
            "transcript": tr, "cover": cover_metrics,
            "visual_semantics": "not_implemented", "analysis_scope": "metadata, pixel scene changes, cover brightness/contrast and optional supplied transcription"}
