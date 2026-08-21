#!/usr/bin/env python3
"""Render the dependency-free README GIF and nine-action proof from local assets."""

from __future__ import annotations

import bisect
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from motion_timing import load_motion_timing, stroke_progress


ROOT = Path(__file__).resolve().parents[1]
TIMING = load_motion_timing(ROOT / "motion-timing.js")
WIDTH, HEIGHT = 720, 1280
GIF_SIZE = (TIMING["gif"]["width"], TIMING["gif"]["height"])
GIF_TIMELINE_SAMPLES = TIMING["gif"]["timelineSamples"]
GIF_ACTIVE_LAST_INDEX = TIMING["gif"]["activeLastIndex"]
GIF_FRAME_DURATION_MS = TIMING["gif"]["frameDurationMs"]
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"
ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
ACTIONS = ["HOVER", "TOUCH", "PRESS", "TRAVEL", "TURN", "LIFT", "RETURN", "FINISH", "LEAVE"]
BREAKS = TIMING["breaks"]
ACTION_PROGRESS = TIMING["actionProgress"]
KNOWLEDGE_THRESHOLDS = TIMING["knowledgeThresholds"]


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def cubic(p0, p1, p2, p3, t: float) -> tuple[float, float]:
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
    )


def build_path() -> tuple[list[tuple[float, float]], list[float]]:
    segments = [
        ((318, 304), (295, 326), (278, 350), (300, 392)),
        ((300, 392), (325, 439), (391, 445), (355, 497)),
        ((355, 497), (326, 540), (259, 554), (317, 620)),
        ((317, 620), (365, 675), (492, 679), (494, 748)),
        ((494, 748), (496, 813), (424, 817), (383, 867)),
        ((383, 867), (342, 918), (390, 958), (456, 1000)),
    ]
    points: list[tuple[float, float]] = []
    for segment_index, segment in enumerate(segments):
        for step in range(81):
            if segment_index and step == 0:
                continue
            points.append(cubic(*segment, step / 80))
    distances = [0.0]
    for previous, current in zip(points, points[1:]):
        distances.append(distances[-1] + math.dist(previous, current))
    return points, distances


PATH_POINTS, PATH_DISTANCES = build_path()
PATH_LENGTH = PATH_DISTANCES[-1]


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def pose_index(progress: float) -> int:
    return next((index for index, threshold in enumerate(BREAKS) if progress < threshold), 8)


def point_at(fraction: float) -> tuple[float, float]:
    target = max(0.0, min(1.0, fraction)) * PATH_LENGTH
    index = bisect.bisect_left(PATH_DISTANCES, target)
    if index <= 0:
        return PATH_POINTS[0]
    if index >= len(PATH_POINTS):
        return PATH_POINTS[-1]
    before, after = PATH_DISTANCES[index - 1], PATH_DISTANCES[index]
    weight = 0 if after == before else (target - before) / (after - before)
    left, right = PATH_POINTS[index - 1], PATH_POINTS[index]
    return left[0] + (right[0] - left[0]) * weight, left[1] + (right[1] - left[1]) * weight


def points_between(start: float, end: float) -> list[tuple[int, int]]:
    start_distance = max(0.0, min(1.0, start)) * PATH_LENGTH
    end_distance = max(0.0, min(1.0, end)) * PATH_LENGTH
    first = bisect.bisect_left(PATH_DISTANCES, start_distance)
    last = bisect.bisect_right(PATH_DISTANCES, end_distance)
    points = [point_at(start), *PATH_POINTS[first:last], point_at(end)]
    return [(round(x), round(y)) for x, y in points]


def draw_dry_trail(layer: Image.Image, progress: float) -> None:
    points = points_between(0, progress)
    if len(points) < 2:
        return
    draw = ImageDraw.Draw(layer)
    # A dry xuan-paper mark is never an opaque dashed vector. Build it from a
    # faint body, uneven fibres, and tiny losses where the brush ran out of ink.
    body = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ImageDraw.Draw(body).line(points, fill=(72, 79, 71, 34), width=24, joint="curve")
    layer.alpha_composite(body.filter(ImageFilter.GaussianBlur(3.2)))

    for index, (start, end) in enumerate(zip(points, points[1:])):
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        # Short losses occur irregularly, never as a repeating dash pattern.
        loss = math.sin(index * 0.71) + math.sin(index * 0.19 + 1.7)
        if loss > 1.42:
            continue
        width = max(5, round(10 + 3.3 * math.sin(index * 0.43) + 1.7 * math.sin(index * 0.17)))
        alpha = max(38, round(67 + 17 * math.sin(index * 0.29 + 0.8)))
        draw.line((start, end), fill=(66, 73, 66, alpha), width=width)

        # Side fibres split away from the core as pressure falls.
        nx, ny = -dy / length, dx / length
        for fibre in (-1, 1):
            offset = fibre * (4 + 3 * abs(math.sin(index * 0.37 + fibre)))
            if math.sin(index * 0.53 + fibre) < -0.15:
                continue
            p0 = (round(start[0] + nx * offset), round(start[1] + ny * offset))
            p1 = (round(end[0] + nx * offset * 1.18), round(end[1] + ny * offset * 1.18))
            draw.line((p0, p1), fill=(75, 81, 73, 22), width=1)

        # Sparse capillary dots dissolve the hard vector edge into paper grain.
        if index % 3 == 0:
            offset = 7 * math.sin(index * 1.37)
            cx = round((start[0] + end[0]) / 2 + nx * offset)
            cy = round((start[1] + end[1]) / 2 + ny * offset)
            radius = 1 + index % 2
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(73, 80, 72, 25))


def round_rect(draw: ImageDraw.ImageDraw, box, fill, radius=7) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def add_text_and_cards(frame: Image.Image, stroke: float, progress: float) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    draw.text((36, 45), "AI KNOWLEDGE · 01", font=font(ARIAL_BOLD, 14), fill=(151, 52, 45, 255))
    draw.text((36, 78), "How Reliable", font=font(GEORGIA, 42), fill=(25, 29, 25, 255))
    draw.text((36, 119), "AI Agents Work", font=font(GEORGIA, 42), fill=(25, 29, 25, 255))
    draw.text((38, 173), "ONE DECISION AT A TIME", font=font(ARIAL_BOLD, 12), fill=(77, 87, 80, 255))

    cards = [
        (KNOWLEDGE_THRESHOLDS["context"], (72, 397, 217, 468), "01", "Context"),
        (KNOWLEDGE_THRESHOLDS["action"], (238, 608, 383, 679), "02", "Action"),
        (KNOWLEDGE_THRESHOLDS["evidence"], (505, 506, 684, 577), "03", "Evidence"),
    ]
    for threshold, box, number, label in cards:
        if stroke < threshold:
            continue
        round_rect(draw, box, (244, 236, 218, 226), 5)
        draw.rectangle((box[0], box[1], box[0] + 6, box[3]), fill=(155, 53, 44, 255))
        draw.text((box[0] + 18, box[1] + 11), number, font=font(ARIAL_BOLD, 13), fill=(155, 53, 44, 255))
        draw.text((box[0] + 18, box[1] + 33), label, font=font(GEORGIA, 23), fill=(28, 33, 29, 255))

    captions = [
        (KNOWLEDGE_THRESHOLDS["context"], KNOWLEDGE_THRESHOLDS["action"], "CONTEXT", "Give the goal, audience, and boundaries."),
        (KNOWLEDGE_THRESHOLDS["action"], KNOWLEDGE_THRESHOLDS["evidence"], "ACTION", "Ask for one clear next step."),
        (KNOWLEDGE_THRESHOLDS["evidence"], KNOWLEDGE_THRESHOLDS["result"], "EVIDENCE", "Check the result before calling it done."),
    ]
    for start, end, label, copy in captions:
        if not start <= stroke < end:
            continue
        round_rect(draw, (58, 940, 492, 1038), (27, 33, 29, 224), 4)
        draw.text((78, 958), label, font=font(ARIAL_BOLD, 12), fill=(207, 118, 107, 255))
        draw.text((78, 984), copy, font=font(ARIAL_BOLD, 15), fill=(244, 238, 222, 255))
    if stroke >= KNOWLEDGE_THRESHOLDS["result"]:
        round_rect(draw, (58, 1085, 430, 1177), (27, 33, 29, 228), 4)
        draw.text((78, 1103), "RELIABLE AI", font=font(ARIAL_BOLD, 12), fill=(207, 118, 107, 255))
        draw.text((78, 1134), "Context + Action + Evidence", font=font(GEORGIA, 20), fill=(244, 238, 222, 255))


def render_frame(background: Image.Image, sprites: list[Image.Image], progress: float) -> Image.Image:
    frame = background.copy().convert("RGBA")
    stroke = stroke_progress(progress, TIMING)
    total_frames = TIMING["durationMs"] / 1000 * TIMING["fps"]
    diffusion_frames = TIMING["inkDelays"]["diffusionFrames"]
    drying_frames = TIMING["inkDelays"]["dryingFrames"]
    diffusion_progress = max(0.0, (stroke - diffusion_frames / total_frames) / (1 - diffusion_frames / total_frames))
    dry_progress = max(0.0, (stroke - drying_frames / total_frames) / (1 - drying_frames / total_frames))

    diffusion = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    diffusion_points = points_between(0, ease(diffusion_progress))
    if len(diffusion_points) >= 2:
        ImageDraw.Draw(diffusion).line(diffusion_points, fill=(86, 96, 87, 51), width=36, joint="curve")
        diffusion = diffusion.filter(ImageFilter.GaussianBlur(5))
        frame = Image.alpha_composite(frame, diffusion)

    dry = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_dry_trail(dry, ease(dry_progress))
    frame = Image.alpha_composite(frame, dry)

    active_span = 0.075
    active_start = max(0.0, stroke - active_span)
    active = points_between(active_start, stroke)
    if len(active) >= 2 and stroke > 0:
        opacity = 198 if progress < BREAKS[-1] else round(198 * max(0, 1 - (progress - BREAKS[-1]) / (1 - BREAKS[-1])))
        pose = pose_index(progress)
        widths = [6, 7, 15, 12, 14, 9, 10, 7, 0]
        if opacity and widths[pose]:
            active_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            ImageDraw.Draw(active_layer).line(active, fill=(45, 53, 47, opacity), width=widths[pose], joint="curve")
            frame = Image.alpha_composite(frame, active_layer)

    index = pose_index(progress)
    point = point_at(stroke)
    if index != 8:
        wet = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        wet_draw = ImageDraw.Draw(wet)
        wet_draw.ellipse((point[0] - 13, point[1] - 13, point[0] + 13, point[1] + 13), fill=(48, 55, 48, 46))
        frame = Image.alpha_composite(frame, wet.filter(ImageFilter.GaussianBlur(5)))

    sprite = sprites[index]
    anchor_y = 662 if index == 8 else 620
    frame.alpha_composite(sprite, (round(point[0] - 315), round(point[1] - anchor_y)))
    add_text_and_cards(frame, stroke, progress)
    return frame.convert("RGB")


def main() -> None:
    background = Image.open(ROOT / "assets/ai-agent-knowledge-cleanplate.png").convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    sprites = [Image.open(ROOT / f"assets/brush-poses-v3/pose-{index:02d}.png").convert("RGBA") for index in range(1, 10)]
    output_dir = ROOT / "output/visual-gate-v3"
    evidence_dir = ROOT / "assets/evidence"
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    gif_rgb_frames: list[Image.Image] = []
    for index in range(GIF_TIMELINE_SAMPLES):
        progress = min(1.0, index / GIF_ACTIVE_LAST_INDEX)
        rendered = render_frame(background, sprites, progress)
        gif_rgb_frames.append(rendered.resize(GIF_SIZE, Image.Resampling.LANCZOS))
    # Each frame gets its own restrained palette. This avoids the coarse skin
    # blocks of one global palette while keeping the 360x640 proof below 16 MiB.
    gif_frames = [
        frame.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        for frame in gif_rgb_frames
    ]
    gif_path = ROOT / "assets/inkbrush-motion-demo.gif"
    gif_frames[0].save(gif_path, save_all=True, append_images=gif_frames[1:], duration=GIF_FRAME_DURATION_MS, loop=0, disposal=2, optimize=True)

    proof = Image.new("RGB", (1080, 1920), (237, 229, 214))
    proof_draw = ImageDraw.Draw(proof, "RGBA")
    for index, progress in enumerate(ACTION_PROGRESS):
        frame = render_frame(background, sprites, progress).resize((360, 640), Image.Resampling.LANCZOS)
        x, y = index % 3 * 360, index // 3 * 640
        proof.paste(frame, (x, y))
        proof_draw.rectangle((x, y, x + 360, y + 34), fill=(26, 31, 27, 220))
        proof_draw.text((x + 12, y + 8), f"{index + 1:02d} · {ACTIONS[index]}", font=font(ARIAL_BOLD, 14), fill=(245, 238, 222, 255))
    proof_path = ROOT / "assets/nine-action-proof.png"
    proof.save(proof_path, optimize=True)

    # Evidence uses exact composition progress, independent of README sampling.
    # The storyboard records the equivalent 30 fps frames (9, 165, 276).
    total_frames = TIMING["durationMs"] / 1000 * TIMING["fps"]
    evidence_frames = {
        "start": render_frame(background, sprites, 9 / total_frames),
        "middle": render_frame(background, sprites, 165 / total_frames),
        "end": render_frame(background, sprites, 1.0),
    }
    for label, frame in evidence_frames.items():
        frame.save(output_dir / f"{label}.png", optimize=True)
        frame.save(evidence_dir / f"{label}.png", optimize=True)
    hero_crops = {
        "hero-start": (render_frame(background, sprites, 21 / total_frames), (160, 220, 520, 460)),
        "hero-middle": (evidence_frames["middle"], (230, 560, 590, 800)),
        "hero-end": (evidence_frames["end"], (360, 360, 720, 600)),
    }
    for label, (frame, box) in hero_crops.items():
        frame.crop(box).save(evidence_dir / f"{label}.png", optimize=True)
    with Image.open(gif_path) as rendered_gif:
        stored_frames = rendered_gif.n_frames
    print(f"wrote {gif_path} ({len(gif_frames)} timeline samples, {stored_frames} stored frames)")
    print(f"wrote {proof_path} (1080x1920)")


if __name__ == "__main__":
    main()
