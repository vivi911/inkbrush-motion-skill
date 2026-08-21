#!/usr/bin/env python3
"""Dependency-free positive and negative tests for storyboard validation."""

from __future__ import annotations

import copy
import json
import struct
import tempfile
import zlib
from pathlib import Path

from artifact_checks import sha256_file, sha256_static_artifact
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
        "fps": 30, "previewSeconds": 9, "finalHoldFrames": 33, "safeMarginPercent": 8,
        "styleRecipe": "shan-shui-scroll", "textMode": "code-native", "brushMode": "none", "staticArtifact": "board.svg",
        "beats": [
            {"id": "observe", "label": "Observe", "copy": "See the whole task.", "startSecond": 0.5, "endSecond": 3},
            {"id": "decide", "label": "Decide", "copy": "Choose one next step.", "startSecond": 3, "endSecond": 6},
            {"id": "deliver", "label": "Deliver", "copy": "Check the evidence.", "startSecond": 6, "endSecond": 8},
        ],
    }


def write_svg(path: Path, *, nested: bool = False, styled: bool = False) -> None:
    values = [
        ("Human AI", 48), ("Observe", 40), ("Decide", 40), ("Deliver", 40),
        ("See the whole task.", 24), ("Choose one next step.", 24), ("Check the evidence.", 24),
    ]
    nodes = ""
    for index, (text, size) in enumerate(values):
        class_attribute = ' class="label"' if styled and index == 0 else ""
        nodes += f'<text x="80" y="{160 + index * 60}" fill="#111" font-size="{size}"{class_attribute}>{text}</text>'
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
        plan["staticArtifactSha256"] = sha256_static_artifact(root / "board.svg")
        expect("valid static evidence", validate(plan, root) == [])
        for too_short in (30, 32):
            bad = copy.deepcopy(plan); bad["finalHoldFrames"] = too_short
            expect(f"reject {too_short}-frame final hold", any("at least 33" in error for error in validate(bad, root)))
        expect("artifact states fail closed without base_dir", any("base_dir" in error for error in validate(plan, None)))

        unsafe_margin = root / "unsafe-margin.svg"
        unsafe_margin.write_text((root / "board.svg").read_text(encoding="utf-8").replace('x="80"', 'x="20"', 1), encoding="utf-8")
        bad = copy.deepcopy(plan); bad["staticArtifact"] = "unsafe-margin.svg"; bad["staticArtifactSha256"] = sha256_static_artifact(unsafe_margin)
        expect("reject text outside declared safe margin", any("safe margin" in error for error in validate(bad, root)))

        bad = copy.deepcopy(plan); bad["aspectRatio"] = "16:9"
        expect("reject non-portrait ratio", any("aspectRatio" in error for error in validate(bad, root)))
        bad = copy.deepcopy(plan); bad["textMode"] = "image-model"
        expect("reject image-model text", any("textMode" in error for error in validate(bad, root)))
        bad = copy.deepcopy(plan); bad["brushMode"] = "floating-marker"
        expect("reject unknown brush mode", any("brushMode" in error for error in validate(bad, root)))
        bad = copy.deepcopy(plan); bad["brushMode"] = "real-hand-nine-action"
        expect("reject real hand without hard profile", any("realHandProfile" in error for error in validate(bad, root)))

        real_hand = copy.deepcopy(plan)
        real_hand["brushMode"] = "real-hand-nine-action"
        real_hand["realHandProfile"] = {
            "profile": "gray-linen-xuan", "brushAngleRange": [80, 85], "armEntry": "lower-right",
            "cropBoundary": "fabric-only", "sleeveStyle": "gray-linen",
            "actions": ["hover", "touch", "press", "travel", "turn", "lift", "return", "finish", "leave"],
            "inkPhysics": {
                "paper": "xuan", "freshCoreOpacity": 0.78, "wetEdgeOpacity": 0.2,
                "dryTrailOpacity": 0.42, "dryBrushGapPercent": 20,
                "dryingDelayFrames": 12, "diffusionDelayFrames": 5,
            },
        }
        expect("accept gray-linen xuan real-hand profile", validate(real_hand, root) == [])
        bad = copy.deepcopy(real_hand); bad["realHandProfile"]["brushAngleRange"] = [72, 85]
        expect("reject non-calligraphic brush angle", any("brushAngleRange" in error for error in validate(bad, root)))
        bad = copy.deepcopy(real_hand); bad["realHandProfile"]["cropBoundary"] = "bare-skin"
        expect("reject bare-skin frame crop", any("cropBoundary" in error for error in validate(bad, root)))
        bad = copy.deepcopy(real_hand); bad["realHandProfile"]["inkPhysics"]["dryTrailOpacity"] = 0.9
        expect("reject opaque undried trail profile", any("dryTrailOpacity" in error for error in validate(bad, root)))
        bad = copy.deepcopy(plan); del bad["beats"][0]["copy"]
        expect("reject missing beat copy", any("copy must be non-empty" in error for error in validate(bad, root)))
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
            "external-image.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><image href="https://example.com/a.png"/><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "sibling PNG filename"),
            "traversal-image.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280"><image href="../a.png"/><text x="20" y="80" fill="#111" font-size="48">Human AI</text></svg>', "sibling PNG filename"),
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

        write_png(root / "linked.png", 720, 1280, (236, 226, 207, 255))
        linked_board = root / "linked-board.svg"
        linked_board.write_text((root / "board.svg").read_text(encoding="utf-8").replace(">", '><image href="linked.png" x="0" y="0" width="720" height="1280"/>', 1), encoding="utf-8")
        linked = copy.deepcopy(plan); linked["staticArtifact"] = "linked-board.svg"; linked["staticArtifactSha256"] = sha256_static_artifact(linked_board)
        expect("valid hash-bound local PNG static evidence", validate(linked, root) == [])
        write_png(root / "linked.png", 720, 1280, (220, 210, 191, 255))
        expect("reject changed linked PNG after static approval", any("static artifact bundle" in error for error in validate(linked, root)))

        bad = copy.deepcopy(plan); bad["status"] = "MOTION_PROOF_READY"
        expect("reject motion state without approval evidence", any("motionEvidence" in error for error in validate(bad, root)))

        for index, color in enumerate([(31, 36, 32, 255), (98, 105, 98, 255), (151, 52, 45, 255)]):
            write_png(root / f"frame-{index}.png", 720, 1280, color)
        motion = copy.deepcopy(plan); motion["status"] = "MOTION_PROOF_READY"
        motion["motionEvidence"] = {
            "rendererLane": "svg-js", "rendererOwner": "Maker", "reviewer": "Reviewer",
            "staticApprovalSha256": sha256_static_artifact(root / "board.svg"),
            "frames": [
                {"role": role, "frame": frame, "path": f"frame-{index}.png", "sha256": sha256_file(root / f"frame-{index}.png")}
                for index, (role, frame) in enumerate([("start", 0), ("middle", 120), ("end", 270)])
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
        bad = copy.deepcopy(motion); bad["motionEvidence"]["frames"][2]["frame"] = 269
        expect("reject end evidence before final hold", any("animation end" in error for error in validate(bad, root)))
        bad = copy.deepcopy(motion); bad["motionEvidence"]["frames"][2]["frame"] = 303
        expect("reject evidence frame beyond final hold", any("between 0 and" in error for error in validate(bad, root)))

        fake_png = root / "fake.png"
        fake_png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
        bad = copy.deepcopy(motion)
        bad["motionEvidence"]["frames"][0]["path"] = "fake.png"
        bad["motionEvidence"]["frames"][0]["sha256"] = sha256_file(fake_png)
        expect("reject header-only fake PNG evidence", any("complete PNG" in error for error in validate(bad, root)))

        write_png(root / "nine-actions.png", 1080, 1920, (236, 226, 207, 255))
        real_motion = copy.deepcopy(real_hand); real_motion["status"] = "MOTION_PROOF_READY"
        real_motion["motionEvidence"] = copy.deepcopy(motion["motionEvidence"])
        real_motion["motionEvidence"]["nineActionProof"] = "nine-actions.png"
        real_motion["motionEvidence"]["nineActionProofSha256"] = sha256_file(root / "nine-actions.png")
        expect("accept hash-bound nine-action proof", validate(real_motion, root) == [])
        bad = copy.deepcopy(real_motion); del bad["motionEvidence"]["nineActionProof"]
        expect("reject real-hand motion without nine-action proof", any("nineActionProof" in error for error in validate(bad, root)))
        bad = copy.deepcopy(real_motion); bad["motionEvidence"]["nineActionProofSha256"] = "0" * 64
        expect("reject changed nine-action proof", any("nineActionProofSha256" in error for error in validate(bad, root)))

        print("PASS: all storyboard validator tests")


if __name__ == "__main__":
    main()
