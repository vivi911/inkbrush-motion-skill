#!/usr/bin/env python3
"""Prove that the v5 source rebuilds the nine published sprite pixels exactly."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from PIL import Image

from build_calligraphy_brush_v5 import ACTIONS, OUTPUT_DIR, SOURCE, build, sha256_file, sha256_rgba


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_MANIFEST = OUTPUT_DIR / "manifest.json"


def main() -> None:
    published = json.loads(PUBLISHED_MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="inkbrush-v5-") as first_temp, tempfile.TemporaryDirectory(prefix="inkbrush-v5-") as second_temp:
        first = Path(first_temp)
        second = Path(second_temp)
        first_manifest = build(SOURCE, first / "poses", first / "manifest.json", first / "final.png")
        second_manifest = build(SOURCE, second / "poses", second / "manifest.json", second / "final.png")

        for index, action in enumerate(ACTIONS, start=1):
            name = f"pose-{index:02d}.png"
            first_path = first / "poses" / name
            second_path = second / "poses" / name
            published_path = OUTPUT_DIR / name
            first_hash = sha256_file(first_path)
            first_pixel_hash = sha256_rgba(Image.open(first_path))
            second_pixel_hash = sha256_rgba(Image.open(second_path))
            published_pixel_hash = sha256_rgba(Image.open(published_path))
            if first_path.read_bytes() != second_path.read_bytes():
                raise SystemExit(f"FAIL: {action} is not byte-deterministic across two rebuilds")
            if first_pixel_hash != second_pixel_hash or first_pixel_hash != published_pixel_hash:
                raise SystemExit(f"FAIL: {action} does not reproduce the published v5 pixels")
            if first_manifest["actions"][index - 1]["sha256"] != first_hash:
                raise SystemExit(f"FAIL: {action} rebuild manifest hash drift")
            if first_manifest["actions"][index - 1]["pixelSha256"] != first_pixel_hash:
                raise SystemExit(f"FAIL: {action} rebuild pixel hash drift")
            if published["actions"][index - 1]["sha256"] != sha256_file(published_path):
                raise SystemExit(f"FAIL: {action} published file hash drift")
            if published["actions"][index - 1]["pixelSha256"] != published_pixel_hash:
                raise SystemExit(f"FAIL: {action} published pixel hash drift")

        if sha256_rgba(Image.open(first / "final.png")) != sha256_rgba(Image.open(OUTPUT_DIR / "pose-09.png")):
            raise SystemExit("FAIL: rebuilt final copy does not reproduce LEAVE pixels")
        if (second / "final.png").read_bytes() != (first / "final.png").read_bytes():
            raise SystemExit("FAIL: final copy is not byte-deterministic")
        print("PASS: v5 source rebuilds all nine published sprites pixel-for-pixel")


if __name__ == "__main__":
    main()
