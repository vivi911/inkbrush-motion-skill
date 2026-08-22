#!/usr/bin/env python3
"""Prove that the v5 source rebuilds the nine published sprites byte-for-byte."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_calligraphy_brush_v5 import ACTIONS, OUTPUT_DIR, SOURCE, build, sha256_file


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
            if first_path.read_bytes() != second_path.read_bytes():
                raise SystemExit(f"FAIL: {action} is not byte-deterministic across two rebuilds")
            if first_path.read_bytes() != published_path.read_bytes():
                raise SystemExit(f"FAIL: {action} does not reproduce the published v5 pose")
            if first_manifest["actions"][index - 1]["sha256"] != first_hash:
                raise SystemExit(f"FAIL: {action} rebuild manifest hash drift")
            if published["actions"][index - 1]["sha256"] != first_hash:
                raise SystemExit(f"FAIL: {action} published manifest hash drift")

        if (first / "final.png").read_bytes() != (OUTPUT_DIR / "pose-09.png").read_bytes():
            raise SystemExit("FAIL: rebuilt final copy is not byte-identical to LEAVE")
        if (second / "final.png").read_bytes() != (first / "final.png").read_bytes():
            raise SystemExit("FAIL: final copy is not byte-deterministic")
        print("PASS: v5 source rebuilds all nine published sprites byte-for-byte")


if __name__ == "__main__":
    main()
