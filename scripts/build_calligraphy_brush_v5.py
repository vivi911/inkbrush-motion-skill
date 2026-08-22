#!/usr/bin/env python3
"""Build the active v5 photographic-looking nine-action brush sprites.

The public source is a disclosed 3x3 ImageGen sheet. Each cell keeps its own
hand, wrist, shaft, ferrule, and wet bristles. PRESS alone receives a small,
deterministic raster deformation so axial compression remains legible at the
360x640 GitHub preview size. No vector or code-drawn bristle is composited.

Pillow is a maintainer-only build dependency; the published browser demo has
no runtime dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/reference/brush-hand-sheet-v5.png"
OUTPUT_DIR = ROOT / "assets/brush-poses-v5"
MANIFEST = OUTPUT_DIR / "manifest.json"
FINAL_COPY = ROOT / "assets/brush-pose-final.png"

CANVAS = (720, 1280)
ANCHOR = (315, 620)
SHEET_SIZE = (941, 1672)
SCALE = 1.42
SOURCE_SHA256 = "569fb216f3510dcff04813ad451e96d09d458a6ca61bb942d2d57558fce9f6d9"
ACTIONS = ["hover", "touch", "press", "travel", "turn", "lift", "return", "finish", "leave"]
VERTICAL_TIP_STATES = {0, 1, 2, 3, 5, 6, 7, 8}
PRESS_TRANSFORM = {
    "kind": "photographic-raster-axial-pressure",
    "terminalCrop": [282, 452, 354, 624],
    "ferruleHeight": 42,
    "hairHeight": 60,
    "maxWidth": 27,
    "bendPx": 0.0,
    "tipWidth": 3,
    "shaftOverlapPx": 4,
}
PIXEL_HASH_ALGORITHM = "sha256(be32-width || be32-height || rgba8-straight-row-major-top-left)"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_rgba(image: Image.Image) -> str:
    """Hash decoded RGBA pixels independently of platform PNG compression."""

    rgba = image.convert("RGBA")
    digest = hashlib.sha256()
    digest.update(struct.pack(">II", *rgba.size))
    digest.update(rgba.tobytes())
    return digest.hexdigest()


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
            luminance = (red * 299 + green * 587 + blue * 114) / 1000
            if alpha >= 150 and luminance < 82:
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
    bbox = canvas.getchannel("A").getbbox()
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


def prepare_cell(sheet: Image.Image, state: int) -> Image.Image:
    row, column = divmod(state, 3)
    left, right = cell_bounds(sheet.width, column)
    top, bottom = cell_bounds(sheet.height, row)
    keyed = chroma_key(sheet.crop((left, top, right, bottom)), clear_left=column > 0)
    tip_x, tip_y = dark_tip(keyed, state)
    resized = keyed.resize(
        (round(keyed.width * SCALE), round(keyed.height * SCALE)),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    canvas.alpha_composite(
        resized,
        (ANCHOR[0] - round(tip_x * SCALE), ANCHOR[1] - round(tip_y * SCALE)),
    )
    extend_sleeve_to_edge(canvas)
    return canvas


def photographic_press_state(source: Image.Image) -> Image.Image:
    """Compress photographed PRESS pixels without drawing a replacement nib."""

    left, top, right, bottom = PRESS_TRANSFORM["terminalCrop"]
    ferrule_height = PRESS_TRANSFORM["ferruleHeight"]
    hair_height = PRESS_TRANSFORM["hairHeight"]
    max_width = PRESS_TRANSFORM["maxWidth"]
    tip_width = PRESS_TRANSFORM["tipWidth"]
    terminal = source.crop((left, top, right, bottom))
    output_height = ferrule_height + hair_height
    warped = Image.new("RGBA", (terminal.width * 2, output_height), (0, 0, 0, 0))
    center = warped.width // 2
    source_center = terminal.width / 2

    for dest_y in range(output_height):
        if dest_y < ferrule_height:
            source_y = dest_y
            t = 0.0
        else:
            t = (dest_y - ferrule_height) / max(1, hair_height - 1)
            source_y = ferrule_height + round(t * (terminal.height - ferrule_height - 1))
        row = terminal.crop((0, source_y, terminal.width, source_y + 1))
        bbox = row.getchannel("A").getbbox()
        if bbox is None:
            continue
        visible = row.crop((bbox[0], 0, bbox[2], 1))
        row_width = visible.width
        if dest_y >= ferrule_height:
            if t < 0.52:
                target_width = row_width
            elif t < 0.82:
                spread = (t - 0.52) / 0.30
                smooth = spread * spread * (3 - 2 * spread)
                target_width = round(row_width + (max_width - row_width) * smooth)
            elif t < 0.94:
                taper = (t - 0.82) / 0.12
                shoulder = max(tip_width + 4, round(max_width * 0.74))
                target_width = round(max_width + (shoulder - max_width) * taper)
            else:
                taper = (t - 0.94) / 0.06
                shoulder = max(tip_width + 4, round(max_width * 0.74))
                target_width = round(shoulder + (tip_width - shoulder) * taper)
            row_width = max(2, target_width)
            visible = visible.resize((row_width, 1), Image.Resampling.LANCZOS)
        original_center = (bbox[0] + bbox[2]) / 2
        center_offset = original_center - source_center
        if dest_y >= ferrule_height:
            center_offset *= max(0.0, 1.0 - t)
        paste_center = round(center + center_offset)
        warped.alpha_composite(visible, (paste_center - row_width // 2, dest_y))

    occupied_rows = [
        y for y in range(warped.height)
        if warped.getchannel("A").crop((0, y, warped.width, y + 1)).getbbox()
    ]
    if occupied_rows:
        gaps = {
            y for y in range(occupied_rows[0], occupied_rows[-1] + 1)
            if not warped.getchannel("A").crop((0, y, warped.width, y + 1)).getbbox()
        }
        if gaps:
            compact = Image.new("RGBA", (warped.width, warped.height - len(gaps)), (0, 0, 0, 0))
            target_y = 0
            for source_y in range(warped.height):
                if source_y in gaps:
                    continue
                compact.alpha_composite(warped.crop((0, source_y, warped.width, source_y + 1)), (0, target_y))
                target_y += 1
            warped = compact

    result = source.copy()
    erase_box = (238, top - 4, 392, bottom + 6)
    erase_source = result.crop(erase_box)
    local_mask = Image.new("L", erase_source.size, 0)
    local_pixels = local_mask.load()
    for y in range(erase_source.height):
        for x in range(erase_source.width):
            red, green, blue, alpha = erase_source.getpixel((x, y))
            if alpha > 12 and red < 145 and green < 105 and blue < 88:
                local_pixels[x, y] = 255
    local_mask = local_mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(0.8))
    erase = Image.new("L", CANVAS, 0)
    erase.paste(local_mask, erase_box[:2])
    result.putalpha(ImageChops.subtract(result.getchannel("A"), erase))
    paste_x = round((left + right) / 2 - center)
    result.alpha_composite(warped, (paste_x, top - PRESS_TRANSFORM["shaftOverlapPx"]))

    brush_alpha = result.getchannel("A").crop((270, 400, 365, 700))
    brush_bbox = brush_alpha.getbbox()
    if brush_bbox is None:
        raise ValueError("warped PRESS brush is empty")
    tip_y = 400 + brush_bbox[3] - 1
    result_alpha = result.getchannel("A")
    tip_pixels = [
        x
        for y in range(max(400, tip_y - 2), tip_y + 1)
        for x in range(270, 365)
        if result_alpha.getpixel((x, y)) > 20
    ]
    if not tip_pixels:
        raise ValueError("warped PRESS tip anchor is empty")
    tip_x = round(sum(tip_pixels) / len(tip_pixels))
    shifted = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    shifted.alpha_composite(result, (ANCHOR[0] - tip_x, ANCHOR[1] - tip_y))
    return shifted


def build(source_path: Path, output_dir: Path, manifest_path: Path, final_copy: Path) -> dict:
    if sha256_file(source_path) != SOURCE_SHA256:
        raise ValueError("v5 source sheet SHA-256 does not match the approved source")
    sheet = Image.open(source_path).convert("RGB")
    if sheet.size != SHEET_SIZE:
        raise ValueError(f"v5 source sheet must be {SHEET_SIZE[0]}x{SHEET_SIZE[1]}")
    poses = [prepare_cell(sheet, state) for state in range(9)]
    poses[2] = photographic_press_state(poses[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for state, (action, pose) in enumerate(zip(ACTIONS, poses), start=1):
        output_path = output_dir / f"pose-{state:02d}.png"
        pose.save(output_path, optimize=True)
        records.append({
            "index": state,
            "action": action,
            "sourceCell": state,
            "transform": PRESS_TRANSFORM if state == 3 else {"kind": "source-photographic"},
            "anchor": list(ANCHOR),
            "output": output_path.relative_to(ROOT).as_posix() if output_path.is_relative_to(ROOT) else output_path.name,
            "sha256": sha256_file(output_path),
            "pixelSha256": sha256_rgba(pose),
        })

    final_copy.parent.mkdir(parents=True, exist_ok=True)
    final_copy.write_bytes((output_dir / "pose-09.png").read_bytes())
    manifest = {
        "schemaVersion": 2,
        "assetVersion": "v5",
        "description": "AI-assisted photographic-looking hand, brush, ferrule, and wet-bristle sprites",
        "pixelHashAlgorithm": PIXEL_HASH_ALGORITHM,
        "source": source_path.relative_to(ROOT).as_posix() if source_path.is_relative_to(ROOT) else source_path.name,
        "sourceSha256": SOURCE_SHA256,
        "sourceSize": list(SHEET_SIZE),
        "canvas": list(CANVAS),
        "anchor": list(ANCHOR),
        "actions": records,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--final-copy", type=Path, default=FINAL_COPY)
    args = parser.parse_args()
    manifest = build(args.source, args.output_dir, args.manifest, args.final_copy)
    for record in manifest["actions"]:
        print(f"{record['action']:>6} {record['output']} {record['sha256']}")


if __name__ == "__main__":
    main()
