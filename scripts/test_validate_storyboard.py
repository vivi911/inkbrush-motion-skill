#!/usr/bin/env python3
"""Dependency-free positive and negative tests for storyboard validation."""

from __future__ import annotations

import copy
import json
import struct
import tempfile
import zlib
from pathlib import Path

from artifact_checks import sha256_file
from validate_storyboard import validate


def write_png(path: Path, width: int, height: int, rgba: tuple[int, int, int, int]) -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    row = b"\x00" + bytes(rgba) * width
    raw = row * height
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(raw, 9))
    data += chunk(b"IEND", b"")
    path.write_bytes(data)


def base_plan() -> dict:
    return {
        "version": "1.0", "status": "STATIC_REVIEW_READY", "title": "Human AI",
        "summary": "A three-beat journey", "aspectRatio": "9:16", "width": 720, "height": 1280,
        "fps": 30, "previewSeconds": 9, "finalHoldFrames": 30, "safeMarginPercent": 8,
        "styleRecipe": "shan-shui-scroll", "textMode": "code-native", "staticArtifact": "board.svg",
        "beats": [
            {"id": "observe", "label": "Observe", "startSecond": 0.5, "endSecond": 3},
            {"id": "decide", "label": "Decide", "startSecond": 3, "endSecond": 6},
            {"id": "deliver", "label": "Deliver", "startSecond": 6, "endSecond": 8},
        ],
    }


def write_svg(path: Path, *, nested: bool = False, styled: bool = False) -> None:
    values = [("Human AI", 48), ("Observe", 40), ("Decide", 40), ("Deliver", 40)]
    nodes = ""
    for index, (text, size) in enumerate(values):
        class_attribute = ' class="label"' if styled and index == 0 else ""
        nodes += f'<text x="20" y="{80 + index * 60}" fill="#111" font-size="{size}"{class_attribute}>{text}</text>'
    if nested: nodes = f"<g>{nodes}</g>"
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280">{nodes}</svg>', encoding="utf-8")


def expect(label: str, condition: bool) -> None:
    if not condition: raise AssertionError(label)
    print(f"PASS: {label}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="inkbrush-tests-") as temp:
        root = Path(temp)
        plan = base_plan()
        write_svg(root / "board.svg")
        expect("valid static evidence", validate(plan, root) == [])
        expect("artifact states fail closed without base_dir", any("base_dir" in error for error in validate(plan, None)))

        bad = copy.deepcopy(plan); bad["aspectRatio"] = "16:9"
        expect("reject non-portrait ratio", any("aspectRatio" in error for error in validate(bad, root)))
        bad = copy.deepcopy(plan); bad["textMode"] = "image-model"
        expect("reject image-model text", any("textMode" in error for error in validate(bad, root)))
        bad = copy.deepcopy(plan); bad["staticArtifact"] = "missing.svg"
        expect("reject missing artifact", any("does not exist" in error for error in validate(bad, root)))

        write_svg(root / "nested.svg", nested=True)
        bad = copy.deepcopy(plan); bad["staticArtifact"] = "nested.svg"
        expect("reject nested review text", any("direct children" in error for error in validate(bad, root)))
        write_svg(root / "styled.svg", styled=True)
        bad = copy.deepcopy(plan); bad["staticArtifact"] = "styled.svg"
        expect("reject CSS-dependent review text", any("CSS hooks" in error or "forbidden" in error for error in validate(bad, root)))

        raw_cases = {
            "hidden-tspan.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><text x="20" y="80" fill="#111" font-size="48">Human <tspan display="none">AI</tspan></text></svg>', "tspan"),
            "transparent-root.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280" opacity="0"><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "transparent SVG root"),
            "no-fill.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><text x="20" y="80" fill="none" font-size="48">Human AI</text></svg>', "opaque hex fill"),
            "off-canvas.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><text x="-999" y="80" fill="#111" font-size="48">Human AI</text></svg>', "off-canvas"),
            "active-content.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><script>alert(1)</script><image href="https://example.com/a.png"/><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "<script>"),
            "event-handler.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280" onload="alert(1)"><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "event attributes"),
            "root-transform.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280" transform="translate(9999 0)"><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "transform or clip"),
            "root-clip.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280" clip-path="url(#empty)"><defs><clipPath id="empty"/></defs><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "transform or clip"),
            "root-fill-opacity.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280" fill-opacity="0"><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "transparent SVG root"),
            "root-collapse.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280" visibility="collapse"><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "hidden SVG root"),
            "animate.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><animate attributeName="opacity" to="0"/><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "<animate>"),
            "external-filter.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><path filter="url(https://example.com/a.svg#f)"/><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "external URL"),
            "xml-stylesheet.svg": ('<?xml-stylesheet href="https://example.com/a.css"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "stylesheets"),
            "transparent-gradient.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><defs><linearGradient id="gone"><stop stop-opacity="0"/></linearGradient></defs><text x="20" y="80" fill="url(#gone)" font-size="48">Human AI</text></svg>', "opaque hex fill"),
            "nan-font-size.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><text x="20" y="80" fill="#111" font-size="NaN">Human AI</text></svg>', "finite font-size"),
            "not-svg-root.svg": ('<not-svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><text x="20" y="80" fill="#111" font-size="48">Human AI</text></not-svg>', "root element must be <svg>"),
        }
        for filename, (content, expected_error) in raw_cases.items():
            content = content.replace('viewBox="0 0 720 1280"', 'width="720" height="1280" viewBox="0 0 720 1280"')
            (root / filename).write_text(content, encoding="utf-8")
            bad = copy.deepcopy(plan); bad["staticArtifact"] = filename
            expect(f"reject hostile SVG evidence: {filename}", any(expected_error in error for error in validate(bad, root)))

        bad = copy.deepcopy(plan); bad["unexpected"] = True
        expect("reject unknown top-level fields", any("unknown top-level" in error for error in validate(bad, root)))
        bad = copy.deepcopy(plan); bad["beats"][0]["unexpected"] = True
        expect("reject unknown beat fields", any("unknown fields" in error for error in validate(bad, root)))
        bad = copy.deepcopy(plan); bad["beats"][0]["startSecond"] = float("nan")
        expect("reject non-finite beat time", any("finite" in error for error in validate(bad, root)))
        bad = copy.deepcopy(plan); bad["status"] = "PLAN_ONLY"
        expect("reject PLAN_ONLY claiming a static artifact", any("must not claim" in error for error in validate(bad, root)))

        bad = copy.deepcopy(plan); bad["status"] = "MOTION_PROOF_READY"
        expect("reject motion state without approval evidence", any("motionEvidence" in error for error in validate(bad, root)))

        for index, color in enumerate([(31, 36, 32, 255), (98, 105, 98, 255), (151, 52, 45, 255)]):
            write_png(root / f"frame-{index}.png", 720, 1280, color)
        motion = copy.deepcopy(plan); motion["status"] = "MOTION_PROOF_READY"
        motion["motionEvidence"] = {
            "rendererLane": "svg-js", "rendererOwner": "Maker", "reviewer": "Reviewer",
            "staticApprovalSha256": sha256_file(root / "board.svg"),
            "frames": [
                {"role": role, "frame": frame, "path": f"frame-{index}.png", "sha256": sha256_file(root / f"frame-{index}.png")}
                for index, (role, frame) in enumerate([("start", 0), ("middle", 120), ("end", 240)])
            ],
        }
        expect("valid motion evidence", validate(motion, root) == [])
        bad = copy.deepcopy(motion); bad["motionEvidence"]["unexpected"] = True
        expect("reject unknown motion evidence fields", any("unknown fields" in error for error in validate(bad, root)))
        bad = copy.deepcopy(motion); bad["motionEvidence"]["frames"][0]["unexpected"] = True
        expect("reject unknown frame fields", any("unknown fields" in error for error in validate(bad, root)))
        bad = copy.deepcopy(motion); bad["motionEvidence"]["staticApprovalSha256"] = "0" * 64
        expect("reject mismatched approval hash", any("does not match" in error for error in validate(bad, root)))
        bad = copy.deepcopy(motion); bad["motionEvidence"]["frames"][2] = copy.deepcopy(bad["motionEvidence"]["frames"][1]); bad["motionEvidence"]["frames"][2]["role"] = "end"
        expect("reject duplicate frame evidence", any("unique" in error for error in validate(bad, root)))

        fake_png = root / "fake.png"
        fake_png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
        bad = copy.deepcopy(motion)
        bad["motionEvidence"]["frames"][0]["path"] = "fake.png"
        bad["motionEvidence"]["frames"][0]["sha256"] = sha256_file(fake_png)
        expect("reject header-only fake PNG evidence", any("complete PNG" in error for error in validate(bad, root)))

        print("PASS: all storyboard validator tests")


if __name__ == "__main__":
    main()
