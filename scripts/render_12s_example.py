#!/usr/bin/env python3
"""Render the approved InkBrush v5 lesson as a deterministic 12-second MP4."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from artifact_checks import ffmpeg_executable


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RENDERER = ROOT / "scripts" / "render_readme_gif.py"
FPS = 30
ACTIVE_SECONDS = 9.2
TOTAL_SECONDS = 12.0
OUTPUT_SIZE = (1080, 1920)
CONTACT_TIMES = (0.2, 5.2, 11.5)


def load_renderer():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("inkbrush_readme_renderer", SOURCE_RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load source renderer: {SOURCE_RENDERER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frame_at(renderer, background: Image.Image, sprites: list[Image.Image], seconds: float) -> Image.Image:
    progress = min(1.0, max(0.0, seconds / ACTIVE_SECONDS))
    native = renderer.render_frame(background, sprites, progress)
    return native.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)


def render_contact_sheet(renderer, background: Image.Image, sprites: list[Image.Image], output: Path) -> None:
    thumb_size = (360, 640)
    gutter = 26
    label_height = 72
    sheet = Image.new(
        "RGB",
        (thumb_size[0] * 3 + gutter * 4, thumb_size[1] + label_height + gutter * 2),
        "#171715",
    )
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(renderer.ARIAL_BOLD, 22)
    sub_font = ImageFont.truetype(renderer.ARIAL, 15)
    labels = ("POISE · 0.2s", "PAINT · 5.2s", "RESOLVE · 11.5s")

    for index, (seconds, label) in enumerate(zip(CONTACT_TIMES, labels)):
        frame = frame_at(renderer, background, sprites, seconds).resize(thumb_size, Image.Resampling.LANCZOS)
        x = gutter + index * (thumb_size[0] + gutter)
        y = gutter + label_height
        sheet.paste(frame, (x, y))
        draw.text((x, gutter), label, font=label_font, fill="#f3ead8")
        draw.text((x, gutter + 31), "1080×1920 · silent proof", font=sub_font, fill="#a99f90")

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)


def render_video(renderer, background: Image.Image, sprites: list[Image.Image], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    total_frames = int(round(TOTAL_SECONDS * FPS))
    command = [
        ffmpeg_executable(),
        "-y",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-pixel_format",
        "rgb24",
        "-video_size",
        f"{OUTPUT_SIZE[0]}x{OUTPUT_SIZE[1]}",
        "-framerate",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    if process.stdin is None:
        raise RuntimeError("ffmpeg stdin is unavailable")

    try:
        for frame_index in range(total_frames):
            seconds = frame_index / FPS
            process.stdin.write(frame_at(renderer, background, sprites, seconds).tobytes())
    finally:
        process.stdin.close()

    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {return_code}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "assets" / "inkbrush-ai-agent-12s.mp4")
    parser.add_argument(
        "--contact-sheet",
        type=Path,
        default=ROOT / "assets" / "inkbrush-ai-agent-12s-contact-sheet.png",
    )
    parser.add_argument("--contact-sheet-only", action="store_true")
    args = parser.parse_args()

    renderer = load_renderer()
    background = Image.open(ROOT / "assets" / "ai-agent-knowledge-cleanplate.png").convert("RGB")
    background = background.resize((renderer.WIDTH, renderer.HEIGHT), Image.Resampling.LANCZOS)
    sprites = [
        Image.open(ROOT / "assets" / "brush-poses-v5" / f"pose-{index:02d}.png").convert("RGBA")
        for index in range(1, 10)
    ]

    render_contact_sheet(renderer, background, sprites, args.contact_sheet)
    if not args.contact_sheet_only:
        render_video(renderer, background, sprites, args.output)
        print(f"video={args.output}")
        print(f"video_sha256={sha256(args.output)}")
    print(f"contact_sheet={args.contact_sheet}")
    print(f"contact_sheet_sha256={sha256(args.contact_sheet)}")


if __name__ == "__main__":
    main()
