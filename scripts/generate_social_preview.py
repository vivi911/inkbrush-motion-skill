#!/usr/bin/env python3
"""Render the 1280x640 launch card from the approved 9:16 demo art."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1280, 640
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEORGIA_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
SONGTI = "/System/Library/Fonts/Supplemental/Songti.ttc"


def font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size, index=index)


def paper_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    random.seed(27)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            t = (x / WIDTH) * .22 + (y / HEIGHT) * .78
            base = (246*(1-t) + 224*t, 240*(1-t) + 211*t, 225*(1-t) + 187*t)
            grain = random.choice((-2, -1, 0, 0, 0, 1, 2))
            pixels[x, y] = tuple(max(0, min(255, int(channel + grain))) for channel in base)
    return image


def main() -> None:
    image = paper_background()
    draw = ImageDraw.Draw(image)

    art = Image.open(ROOT / "assets/ai-agent-knowledge-journey.png").convert("RGB")
    art.thumbnail((360, 640), Image.Resampling.LANCZOS)
    art_x = 874

    shadow = Image.new("RGBA", (art.width + 50, HEIGHT), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle((24, 2, 24 + art.width, HEIGHT - 2), fill=(35, 27, 18, 95))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    image.paste(shadow, (art_x - 24, 0), shadow)
    image.paste(art, (art_x, 0))

    wash = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    wash_draw = ImageDraw.Draw(wash)
    for x in range(760, 940):
        alpha = int(230 * (x - 760) / 180)
        wash_draw.line((x, 0, x, HEIGHT), fill=(232, 220, 196, alpha))
    image = Image.alpha_composite(image.convert("RGBA"), wash)
    draw = ImageDraw.Draw(image)

    draw.line((50, 86, 805, 86), fill=(64, 56, 44, 90), width=1)
    draw.line((50, 562, 805, 562), fill=(64, 56, 44, 90), width=1)
    draw.rectangle((54, 48, 114, 108), fill="#98372f")
    draw.text((68, 55), "墨", font=font(SONGTI, 36), fill="#f5efdf")
    draw.text((136, 65), "INKBRUSH MOTION", font=font(ARIAL, 18), fill="#202620")

    draw.text((54, 153), "LIVE 9:16 OUTPUT · OPEN-SOURCE AI SKILL", font=font(ARIAL, 13), fill="#98372f")
    draw.text((50, 200), "AI knowledge,", font=font(GEORGIA, 70), fill="#171b18")
    draw.text((50, 278), "brushed", font=font(GEORGIA_ITALIC, 70), fill="#98372f")
    draw.text((312, 278), "in ink.", font=font(GEORGIA, 70), fill="#171b18")
    draw.text((55, 397), "CONTEXT  →  ACTION  →  EVIDENCE", font=font(ARIAL, 20), fill="#3f4943")
    draw.text((55, 438), "A reliable AI-agent loop, revealed one stroke at a time.", font=font(ARIAL, 18), fill="#59635d")
    draw.text((55, 582), "VIVI911 / GOASKVIVI · MIT · 2026", font=font(ARIAL, 13), fill="#68716b")

    output = ROOT / "assets/social-preview.png"
    image.convert("RGB").save(output, format="PNG", optimize=True)
    print(f"wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
