#!/usr/bin/env python3
"""Render the code-authored 1280x640 social preview. Requires Pillow for maintainers only."""

from __future__ import annotations

import math
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


def cubic(p0, p1, p2, p3, steps=90):
    points = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
        points.append((x, y))
    return points


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    random.seed(19)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            t = (x / WIDTH) * .35 + (y / HEIGHT) * .65
            base = (245*(1-t) + 216*t, 239*(1-t) + 203*t, 223*(1-t) + 179*t)
            grain = random.choice((-2, -1, 0, 0, 0, 1, 2))
            pixels[x, y] = tuple(max(0, min(255, int(channel + grain))) for channel in base)

    draw = ImageDraw.Draw(image)
    draw.line((46, 88, 830, 88), fill=(65, 59, 48, 42), width=1)
    draw.line((46, 563, 830, 563), fill=(65, 59, 48, 42), width=1)
    draw.rectangle((54, 56, 112, 114), fill="#98372f")
    draw.text((68, 61), "墨", font=font(SONGTI, 35), fill="#f5efdf")
    draw.text((132, 72), "INKBRUSH MOTION", font=font(ARIAL, 18), fill="#202620", stroke_width=0)
    draw.text((56, 178), "OPEN-SOURCE AI SKILL · NATIVE 9:16", font=font(ARIAL, 13), fill="#98372f")
    draw.text((52, 218), "Knowledge,", font=font(GEORGIA, 73), fill="#171b18")
    draw.text((52, 297), "painted", font=font(GEORGIA_ITALIC, 73), fill="#98372f")
    draw.text((337, 297), "at", font=font(GEORGIA, 73), fill="#171b18")
    draw.text((52, 376), "human speed.", font=font(GEORGIA, 73), fill="#171b18")
    draw.text((56, 482), "Static-first · Exact text · Brush-led motion · MIT", font=font(ARIAL, 19), fill="#4f5953")
    draw.text((56, 580), "VIVI911 / GOASKVIVI · 2026", font=font(ARIAL, 13), fill="#68716b")

    scroll = Image.new("RGBA", (344, 588), (0, 0, 0, 0))
    scene = Image.new("RGBA", (320, 568), "#eee5d2")
    scene_draw = ImageDraw.Draw(scene)
    scene_draw.polygon([(-23,279),(44,186),(97,250),(157,154),(210,258),(255,197),(299,262),(349,178),(387,262),(387,350),(-23,350)], fill=(111,123,116,48))
    scene_draw.polygon([(-19,319),(48,254),(107,304),(157,229),(216,311),(269,243),(312,305),(369,241),(405,305),(405,370),(-19,370)], fill=(52,66,59,68))
    mist = Image.new("RGBA", (320, 568), (0,0,0,0))
    mist_draw = ImageDraw.Draw(mist)
    mist_draw.line([(-28,300),(65,277),(143,306),(209,285),(278,276),(348,298)], fill=(255,253,244,125), width=26)
    mist_draw.line([(-25,344),(62,324),(140,350),(220,331),(285,321),(346,342)], fill=(255,253,244,115), width=24)
    scene.alpha_composite(mist.filter(ImageFilter.GaussianBlur(10)))
    scene_draw = ImageDraw.Draw(scene)
    river = cubic((57,530),(62,448),(131,442),(124,391)) + cubic((124,391),(142,335),(104,316),(147,276)) + cubic((147,276),(183,242),(208,263),(239,202)) + cubic((239,202),(213,161),(272,110),(295,82))
    bloom = Image.new("RGBA", (320,568), (0,0,0,0))
    ImageDraw.Draw(bloom).line(river, fill=(29,41,37,58), width=30, joint="curve")
    scene.alpha_composite(bloom.filter(ImageFilter.GaussianBlur(10)))
    scene_draw.line(river, fill="#19211d", width=13, joint="curve")
    for x, y in [(116,431),(148,275),(245,210)]: scene_draw.ellipse((x-4,y-4,x+4,y+4), fill="#98372f")
    scene_draw.text((39, 28), "AI Collaboration", font=font(GEORGIA, 25), fill="#171b18")
    scene_draw.text((136, 412), "Observe", font=font(GEORGIA, 20), fill="#171b18")
    scene_draw.text((166, 264), "Decide", font=font(GEORGIA, 20), fill="#171b18")
    scene_draw.text((170, 194), "Deliver", font=font(GEORGIA, 20), fill="#171b18")
    scene_draw.text((251, 460), "知", font=font(SONGTI, 45), fill="#202823")
    scene_draw.text((251, 508), "行", font=font(SONGTI, 45), fill=(32,40,35,140))
    scene_draw.line(((309,18),(300,60)), fill="#704b2d", width=10)
    scene_draw.line(((300,60),(297,75)), fill="#b59864", width=14)
    scene_draw.polygon([(295,82),(292,61),(304,64)], fill="#151b18")
    scroll.alpha_composite(scene, (12, 10))
    scroll_draw = ImageDraw.Draw(scroll)
    scroll_draw.rectangle((0,0,344,15), fill="#8e765d", outline="#45392d")
    scroll_draw.rectangle((0,573,344,587), fill="#8e765d", outline="#45392d")
    scroll_draw.rectangle((12,10,332,578), outline=(83,73,54,90), width=2)
    image.paste(scroll, (863, 30), scroll)

    output = ROOT / "assets/social-preview.png"
    image.save(output, format="PNG", optimize=True)
    print(f"wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
