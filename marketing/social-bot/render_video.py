"""Render short Ken Burns MP4 clips from still PNGs (ffmpeg)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def ffmpeg_bin() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def has_ffmpeg() -> bool:
    if shutil.which("ffmpeg"):
        return True
    try:
        import imageio_ffmpeg

        return bool(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        return False


def ken_burns(
    png_path: Path,
    mp4_path: Path,
    *,
    width: int,
    height: int,
    duration: float = 10.0,
    fps: int = 30,
) -> Path:
    """Slow zoom-in Ken Burns — readable text, no shake."""
    png_path = Path(png_path)
    mp4_path = Path(mp4_path)
    mp4_path.parent.mkdir(parents=True, exist_ok=True)

    frames = max(int(duration * fps), fps)
    # Mild zoom: end ~1.12x so type stays legible
    z_expr = f"min(1+0.12*on/{frames},1.12)"
    vf = (
        f"scale={width * 2}:{height * 2}:force_original_aspect_ratio=increase,"
        f"crop={width * 2}:{height * 2},"
        f"zoompan=z='{z_expr}':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={width}x{height}:fps={fps},"
        f"format=yuv420p"
    )

    cmd = [
        ffmpeg_bin(),
        "-y",
        "-loop",
        "1",
        "-i",
        str(png_path),
        "-vf",
        vf,
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-an",
        str(mp4_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return mp4_path


def render_feed_clip(png_path: Path, mp4_path: Path, duration: float = 10.0) -> Path:
    return ken_burns(png_path, mp4_path, width=1080, height=1080, duration=duration)


def render_stories_clip(png_path: Path, mp4_path: Path, duration: float = 10.0) -> Path:
    return ken_burns(png_path, mp4_path, width=1080, height=1920, duration=duration)


def render_reels_video_with_audio_and_subs(
    png_path: Path,
    audio_path: Path,
    srt_path: Path,
    mp4_path: Path,
    duration: float,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
) -> Path:
    """Combine static PNG, voiceover audio, and burn styled subtitles into 9:16 Reels video."""
    png_path = Path(png_path)
    audio_path = Path(audio_path)
    srt_path = Path(srt_path)
    mp4_path = Path(mp4_path)
    mp4_path.parent.mkdir(parents=True, exist_ok=True)

    png_abs = png_path.resolve()
    audio_abs = audio_path.resolve()
    srt_abs = srt_path.resolve()
    mp4_abs = mp4_path.resolve()

    srt_parent = srt_abs.parent
    srt_filename = srt_abs.name

    frames = max(int(duration * fps), fps)
    z_expr = f"min(1+0.12*on/{frames},1.12)"

    # Modern readable Tahoma subtitles, bold white text with thick black outline, positioned nicely
    style = (
        "FontName=Tahoma,FontSize=14,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=40,Bold=1"
    )

    vf = (
        f"scale={width * 2}:{height * 2}:force_original_aspect_ratio=increase,"
        f"crop={width * 2}:{height * 2},"
        f"zoompan=z='{z_expr}':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={width}x{height}:fps={fps},"
        f"subtitles={srt_filename}:force_style='{style}',"
        f"format=yuv420p"
    )

    cmd = [
        ffmpeg_bin(),
        "-y",
        "-loop",
        "1",
        "-i",
        str(png_abs),
        "-i",
        str(audio_abs),
        "-vf",
        vf,
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(mp4_abs),
    ]

    subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
        cwd=str(srt_parent),
    )
    return mp4_path
