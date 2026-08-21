#!/usr/bin/env python3
"""Turn a 3x3 chroma-key hand sheet into nine anchored 9:16 PNG sprites.

This is an optional production helper. It requires Pillow, but the published
browser demo itself remains dependency-free.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageFilter


CANVAS = (720, 1280)
ANCHOR = (315, 620)
SCALE = 1.42
VERTICAL_TIP_STATES = {0, 1, 2, 8}


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
