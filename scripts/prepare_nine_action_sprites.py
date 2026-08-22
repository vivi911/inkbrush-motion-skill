#!/usr/bin/env python3
"""Turn a 3x3 chroma-key hand sheet into nine anchored 9:16 PNG sprites.

This is an optional production helper. It requires Pillow, but the published
browser demo itself remains dependency-free.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


CANVAS = (720, 1280)
ANCHOR = (315, 620)
SCALE = 1.42
# The compact-hair sheet keeps every terminal tip vertically anchored except
# TURN, whose last hairs deliberately flex sideways at contact.
VERTICAL_TIP_STATES = {0, 1, 2, 3, 5, 6, 7, 8}

# The selected ImageGen sheet supplies the hand, grip, shaft, light and sleeve.
# Its compact tufts are replaced deterministically so every published pose uses
# the same approved soft-hair language as the contact proof: pointed at rest,
# rounded on touch, visibly fanned under pressure, tapered on exit.
BRISTLE_ROOTS = [
    (329, 516),
    (327, 516),
    (328, 516),
    (329, 516),
    (352, 544),
    (332, 526),
    (324, 516),
    (336, 516),
    (336, 516),
]
BRISTLE_PRESSURE = [0.0, 0.42, 0.91, 0.72, 0.84, 0.38, 0.52, 0.25, 0.0]
BRISTLE_BEND = [-1.0, 0.5, 7.0, 8.0, 18.0, 3.0, -4.0, 2.0, -1.0]
CONTACT_STATES = {1, 2, 3, 4, 5, 6, 7}


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return min(upper, max(lower, value))


def smoothstep(value: float) -> float:
    value = clamp(value)
    return value * value * (3 - 2 * value)


def cubic_points(p0, p1, p2, p3, steps: int = 18):
    points = []
    for index in range(1, steps + 1):
        t = index / steps
        u = 1 - t
        points.append((
            u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
        ))
    return points


def quadratic_points(p0, p1, p2, steps: int = 8):
    points = []
    for index in range(1, steps + 1):
        t = index / steps
        u = 1 - t
        points.append((
            u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
        ))
    return points


def color_at(stops, progress: float) -> tuple[int, int, int, int]:
    progress = clamp(progress)
    for (left_at, left), (right_at, right) in zip(stops, stops[1:]):
        if progress <= right_at:
            local = 0 if right_at == left_at else (progress - left_at) / (right_at - left_at)
            return tuple(round(a + (b - a) * local) for a, b in zip(left, right))
    return stops[-1][1]


def bristle_outline(state: int) -> tuple[list[tuple[float, float]], float, float, float]:
    root_x, root_y = BRISTLE_ROOTS[state]
    root_dx = root_x - ANCHOR[0]
    length = ANCHOR[1] - root_y
    scale_y = length / 93
    pressure = BRISTLE_PRESSURE[state]
    contact = state in CONTACT_STATES
    press_fan = smoothstep((pressure - 0.46) / 0.42) if contact else 0
    splay = pressure * 5 + press_fan * 18
    bend = BRISTLE_BEND[state]
    tip_half = 0.7 + pressure * 2.5 + press_fan * 9 if contact else 0

    def point(x: float, y: float) -> tuple[float, float]:
        return ANCHOR[0] + x, ANCHOR[1] + y * scale_y

    start = point(root_dx - 4.8, -93)
    outline = [start]
    lower_left = point(root_dx * 0.52 - 4.8 - splay * 0.1 + bend * 0.35, -38)
    outline.extend(cubic_points(
        start,
        point(root_dx - 6.4, -73),
        point(root_dx * 0.72 - 5.5 + bend * 0.15, -54),
        lower_left,
    ))
    left_tip = point(-tip_half, -1 if contact else 0)
    outline.extend(cubic_points(
        lower_left,
        point(-4.6 - splay * 0.42 + bend * 0.72, -29),
        point(-tip_half - splay * 0.18 + bend * 0.25, -10),
        left_tip,
    ))
    if contact:
        first = point(-tip_half * 0.25, 0.9)
        second = point(tip_half * 0.34, 1.0)
        right_tip = point(tip_half, 0.2)
        outline.extend(quadratic_points(left_tip, point(-tip_half * 0.72, 1.7), first))
        outline.extend(quadratic_points(first, point(tip_half * 0.04, 2.5), second))
        outline.extend(quadratic_points(second, point(tip_half * 0.72, 1.9), right_tip))
    else:
        right_tip = point(tip_half, 0)
        outline.append(right_tip)
    lower_right = point(root_dx * 0.52 + 4.8 + splay * 0.1 + bend * 0.35, -38)
    outline.extend(cubic_points(
        right_tip,
        point(tip_half + splay * 0.15 + bend * 0.22, -10),
        point(5 + splay * 0.44 + bend * 0.72, -28),
        lower_right,
    ))
    outline.extend(cubic_points(
        lower_right,
        point(root_dx * 0.72 + 5.5 + bend * 0.15, -54),
        point(root_dx + 6.4, -73),
        point(root_dx + 4.8, -93),
    ))
    return outline, tip_half, bend, scale_y


def rebuild_bristles(canvas: Image.Image, state: int) -> None:
    root = BRISTLE_ROOTS[state]
    tip = ANCHOR

    # Remove only the generated source tuft. The replacement overlaps the last
    # shaft pixels so no square seam or detached second brush can survive.
    erase = Image.new("L", CANVAS, 0)
    erase_draw = ImageDraw.Draw(erase)
    erase_draw.line((root, tip), fill=255, width=48)
    erase_draw.ellipse((tip[0] - 27, tip[1] - 25, tip[0] + 31, tip[1] + 23), fill=255)
    if state == 4:
        # TURN was anchored from the leftmost contact hair in the generated
        # sheet, so its obsolete tuft also extended below the anchor. Remove
        # that entire local tail before drawing the compact replacement.
        erase_draw.rectangle((tip[0] - 66, root[1] + 16, tip[0] + 100, tip[1] + 112), fill=255)
    erase = erase.filter(ImageFilter.GaussianBlur(0.35))
    canvas.putalpha(ImageChops.subtract(canvas.getchannel("A"), erase))

    outline, tip_half, bend, scale_y = bristle_outline(state)
    margin = 8
    left = max(0, int(min(x for x, _y in outline)) - margin)
    top = max(0, int(min(y for _x, y in outline)) - margin)
    right = min(CANVAS[0], int(max(x for x, _y in outline)) + margin + 1)
    bottom = min(CANVAS[1], int(max(y for _x, y in outline)) + margin + 1)
    supersample = 4
    size = ((right - left) * supersample, (bottom - top) * supersample)
    to_local = lambda p: ((p[0] - left) * supersample, (p[1] - top) * supersample)

    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon([to_local(point) for point in outline], fill=255)

    gradient = Image.new("RGBA", size, (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)
    root_y = BRISTLE_ROOTS[state][1]
    tip_y = ANCHOR[1] + 3
    stops = [
        (0.0, (47, 27, 21, 255)),
        (0.30, (89, 53, 40, 255)),
        (0.68, (67, 42, 33, 255)),
        (1.0, (53, 35, 29, 255)),
    ]
    for row in range(size[1]):
        canvas_y = top + row / supersample
        progress = (canvas_y - root_y) / max(1, tip_y - root_y)
        gradient_draw.line((0, row, size[0], row), fill=color_at(stops, progress))
    gradient.putalpha(mask)

    # Short, uneven terminal fibres make pressure read as living hair, not a
    # flat triangular nib. They deliberately stop at different paper points.
    contact = state in CONTACT_STATES
    terminal = Image.new("RGBA", size, (0, 0, 0, 0))
    terminal_draw = ImageDraw.Draw(terminal)
    ends = ([-1, -0.76, -0.49, -0.17, 0.11, 0.39, 0.67, 0.91] if contact else [-0.55, 0, 0.68])
    end_y = [0.4, 1.2, 0.2, 1.5, 0.7, 1.4, 0.3, 0.9]
    root_dx = BRISTLE_ROOTS[state][0] - ANCHOR[0]

    def center_at(local_y: float) -> float:
        root_mix = clamp(-local_y / 93)
        return root_dx * root_mix + bend * (1 - root_mix) * 0.66

    for index, value in enumerate(ends):
        end_x = value * tip_half
        spread_index = index - (len(ends) - 1) / 2
        start_local_y = -18 - (index % 3) * 2.2
        start_x = center_at(start_local_y) + spread_index * 1.35
        p0 = (ANCHOR[0] + start_x, ANCHOR[1] + start_local_y * scale_y)
        p1 = (
            ANCHOR[0] + end_x * 0.68 + bend * 0.08 + (-0.7 if index % 2 == 0 else 0.55),
            ANCHOR[1] + (-5.2 - (index % 2) * 1.1) * scale_y,
        )
        p2 = (
            ANCHOR[0] + end_x,
            ANCHOR[1] + ((end_y[index] if contact else (0.4 if index == 1 else 0)) * scale_y),
        )
        strand = quadratic_points(p0, p1, p2, 12)
        color = (128, 73, 48, 110) if index % 3 == 1 else (27, 18, 15, 155)
        width = 4 if contact and index % 2 else 3
        terminal_draw.line([to_local(p0), *[to_local(p) for p in strand]], fill=color, width=width, joint="curve")

    merged = Image.alpha_composite(gradient, terminal)
    merged = merged.resize((right - left, bottom - top), Image.Resampling.LANCZOS)
    canvas.alpha_composite(merged, (left, top))


def cell_bounds(length: int, index: int) -> tuple[int, int]:
    return round(length * index / 3), round(length * (index + 1) / 3)


def chroma_key(cell: Image.Image, clear_left: bool) -> Image.Image:
    rgba = cell.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            red, green, blue, _alpha = pixels[x, y]
            greenness = green - max(red, blue)
            if greenness >= 54:
                alpha = 0
            elif greenness <= 22:
                alpha = 255
            else:
                alpha = round(255 * (54 - greenness) / 32)
            if clear_left and x < 58:
                alpha = 0
            if alpha:
                # Undo the green-screen contribution before compositing the
                # antialiased edge over warm paper. This removes the yellow-
                # green rim that otherwise makes the hand read as a sticker.
                coverage = alpha / 255
                if coverage < 1:
                    red = min(255, round(red / coverage))
                    green = max(0, min(255, round((green - (1 - coverage) * 255) / coverage)))
                    blue = min(255, round(blue / coverage))
                green = min(green, max(red, blue))
            pixels[x, y] = red, green, blue, alpha
    alpha = rgba.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.35))
    rgba.putalpha(alpha)
    return rgba


def dark_tip(image: Image.Image, state: int) -> tuple[int, int]:
    pixels = image.load()
    candidates: list[tuple[int, int]] = []
    for y in range(round(image.height * 0.35), image.height):
        for x in range(round(image.width * 0.68)):
            red, green, blue, alpha = pixels[x, y]
            if alpha >= 150 and (red * 299 + green * 587 + blue * 114) / 1000 < 82:
                candidates.append((x, y))
    if not candidates:
        raise ValueError(f"cannot locate dark bristle tip for state {state + 1:02d}")
    if state in VERTICAL_TIP_STATES:
        edge = max(y for _x, y in candidates)
        band = sorted(x for x, y in candidates if y >= edge - 4)
        return band[len(band) // 2], edge
    edge = min(x for x, _y in candidates)
    band = sorted(y for x, y in candidates if x <= edge + 4)
    return edge, band[len(band) // 2]


def extend_sleeve_to_edge(canvas: Image.Image) -> None:
    alpha = canvas.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError("sprite is empty after chroma key")
    right = bbox[2]
    if right >= CANVAS[0]:
        return
    strip_left = max(0, right - 34)
    strip = canvas.crop((strip_left, 0, right, CANVAS[1]))
    extension = strip.resize((CANVAS[0] - strip_left, CANVAS[1]), Image.Resampling.BICUBIC)
    mask = extension.getchannel("A").filter(ImageFilter.GaussianBlur(0.7))
    canvas.paste(extension, (strip_left, 0), mask)


def prepare(source: Path, output_dir: Path, final_copy: Path | None = None) -> None:
    sheet = Image.open(source).convert("RGB")
    output_dir.mkdir(parents=True, exist_ok=True)
    for state in range(9):
        row, column = divmod(state, 3)
        left, right = cell_bounds(sheet.width, column)
        top, bottom = cell_bounds(sheet.height, row)
        keyed = chroma_key(sheet.crop((left, top, right, bottom)), clear_left=column > 0)
        tip_x, tip_y = dark_tip(keyed, state)
        resized = keyed.resize(
            (round(keyed.width * SCALE), round(keyed.height * SCALE)),
            Image.Resampling.LANCZOS,
        )
        tip_x = round(tip_x * SCALE)
        tip_y = round(tip_y * SCALE)
        canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        paste_at = (ANCHOR[0] - tip_x, ANCHOR[1] - tip_y)
        canvas.alpha_composite(resized, paste_at)
        extend_sleeve_to_edge(canvas)
        rebuild_bristles(canvas, state)
        pose_path = output_dir / f"pose-{state + 1:02d}.png"
        canvas.save(pose_path, optimize=True)
        if state == 8 and final_copy is not None:
            final_copy.parent.mkdir(parents=True, exist_ok=True)
            canvas.save(final_copy, optimize=True)
        print(f"pose-{state + 1:02d}.png anchor={ANCHOR[0]},{ANCHOR[1]}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--final-copy", type=Path)
    args = parser.parse_args()
    prepare(args.source, args.output_dir, args.final_copy)


if __name__ == "__main__":
    main()
