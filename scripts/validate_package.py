#!/usr/bin/env python3
"""Validate the public InkBrush Motion repository package."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from artifact_checks import gif_metadata, png_dimensions, sha256_file, validate_svg_safety
from validate_storyboard import (
    BEAT_FIELDS,
    BRUSH_MODES,
    FRAME_FIELDS,
    INK_PHYSICS_FIELDS,
    MOTION_FIELDS,
    NINE_ACTIONS,
    REAL_HAND_FIELDS,
    RENDERER_LANES,
    REQUIRED_FIELDS,
    STATES,
    STYLE_RECIPES,
    TOP_LEVEL_FIELDS,
    _reject_json_constant,
    validate,
)


ROOT = Path(__file__).resolve().parents[1]
README_GIF_SHA256 = "61f71b7c6185b76b67540956d79447f96e17dcd79727cc80c7b86dee933a48c5"
README_SOURCE_SHA256 = {
    "index.html": "39ce27ddd8dfda291dbca376d0a0bcdca1b47d7e4ae999f11547454c3ec2666b",
    "styles.css": "b1eb0c1a21338bacc65e596d92598f6eca0a24af4d5f237f006ae57b62ac9a54",
    "app.js": "08b8f4d6bc04eed2824fdafe1e4ab014c58f3e2e071ab6811f5b0373317dd930",
    "scripts/render_readme_gif.py": "e8b80773e601cae7a822b5dfcc729091456f271bce0909d84cc889966e574819",
}
BRUSH_ASSET_SHA256 = {
    "assets/brush-poses-v3/pose-01.png": "4bb53d10c827c59cf3542632e57d78a209a9d187e97047a04b7ae923b75eac92",
    "assets/brush-poses-v3/pose-02.png": "5e825a3eaf858603787417810a5d9d77178a6eb228059190e4ab32eea817829c",
    "assets/brush-poses-v3/pose-03.png": "21535db0230d5d096921d2999d242175b4f66cee9c220ab4195d0eed26204cfc",
    "assets/brush-poses-v3/pose-04.png": "a183c74c530a5a28c8ff2f9189e325d1ba9504f57c75f2fd9d26d307d7a2d823",
    "assets/brush-poses-v3/pose-05.png": "5927e49445362ea1a1e49ed743e8ee587ba3e072476996d37aa410401c3c7924",
    "assets/brush-poses-v3/pose-06.png": "805812a945f34cb3db27e1b289cfcd1be7d27d7bbd5696794d908a28e121f9f5",
    "assets/brush-poses-v3/pose-07.png": "3f7f1e077de59f5a84484ee39bb0338ef3a320b7b6fda980fe8c9e4206ad89cb",
    "assets/brush-poses-v3/pose-08.png": "63dc0996a9ac75e4b0cb5a283249c1d3b5c00f2097b4aa6261c1e33b63eed311",
    "assets/brush-poses-v3/pose-09.png": "a9f8a713feffd92e911aa6d5e52b8716f641a48d34f7f73c32c2588bace68b00",
}
FINAL_BRUSH_SHA256 = BRUSH_ASSET_SHA256["assets/brush-poses-v3/pose-09.png"]
CLEAN_PLATE_SHA256 = "37e16d24d69537bcdbb88dcee8307b78ae77a02c05fec79d82bc77a8a5f2e658"
REAL_BRUSH_REFERENCE_SHA256 = "49153b50a9a56539430099af1aa6475957b9bc7b9630075bdebc9927fcb6f85d"
NINE_ACTION_PROOF_SHA256 = "912ee31fec01566df0fec8eb0b60c86487e11803b2cfc1da17f2feaa5819b6de"
REQUIRED = [
    ".gitignore", ".nojekyll", ".github/workflows/validate.yml",
    "SKILL.md", "README.md", "README.zh-TW.md", "LICENSE", "COPYRIGHT.md", "CONTRIBUTING.md",
    "SECURITY.md", "index.html", "styles.css", "app.js", "agents/openai.yaml",
    "assets/icon.svg", "assets/static-board.svg", "assets/social-preview.svg", "assets/social-preview.png", "assets/inkbrush-motion-demo.gif",
    "assets/ai-agent-knowledge-journey.png", "assets/ai-agent-knowledge-prestroke.png", "assets/ai-agent-knowledge-cleanplate.png",
    "assets/brush-pose-final.png", *BRUSH_ASSET_SHA256, "assets/reference/real-brush-gray-linen.png",
    "assets/nine-action-proof.png", "assets/evidence/start.png", "assets/evidence/middle.png", "assets/evidence/end.png", "assets/demo-plan.json",
    "references/style-contract.md", "references/motion-contract.md", "references/qa-rubric.md",
    "references/real-brush-contract.md", "references/copyright-and-provenance.md", "references/image-generation-record.md", "references/readme-animation-record.md", "references/open-source-notes.md", "references/storyboard.schema.json",
    "scripts/generate_social_preview.py", "scripts/prepare_nine_action_sprites.py", "scripts/render_readme_gif.py", "scripts/test_validate_package.py", "scripts/test_validate_storyboard.py",
]


def _external_or_active_url(value: str) -> bool:
    compact = value.strip().lower()
    return compact.startswith(("http://", "https://", "//", "javascript:", "vbscript:"))


def _safe_local_runtime_path(value: str) -> bool:
    """Accept only an existing package-relative file path for active HTML resources."""
    compact = value.strip()
    if not compact or "\\" in compact:
        return False
    decoded = compact
    for _ in range(3):
        expanded = unquote(decoded)
        if expanded == decoded:
            break
        decoded = expanded
    parsed = urlsplit(decoded)
    if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
        return False
    relative = Path(parsed.path)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        return False
    candidate = (ROOT / relative).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return candidate.is_file()


class RuntimeHTMLAudit(HTMLParser):
    """Reject active or external runtime content while allowing JSON-LD and outbound anchors."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.errors: list[str] = []
        self.json_ld: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attribute_names = [name.lower() for name, _ in attrs]
        if len(attribute_names) != len(set(attribute_names)):
            self.errors.append(f"index.html forbids duplicate attributes on <{tag}>")
        values = {name.lower(): value or "" for name, value in attrs}
        if tag == "base": self.errors.append("index.html forbids <base>")
        if tag in {"animate", "animatemotion", "animatetransform", "embed", "foreignobject", "iframe", "object", "set", "style"}:
            self.errors.append(f"index.html forbids active <{tag}> content")
        if any(name.startswith("on") for name in values): self.errors.append(f"index.html forbids event attributes on <{tag}>")
        if "style" in values: self.errors.append(f"index.html forbids inline style attributes on <{tag}>")
        if any(name.split(":")[-1] == "href" and _external_or_active_url(value) and value.strip().lower().startswith(("javascript:", "vbscript:")) for name, value in values.items()):
            self.errors.append(f"index.html forbids active href values on <{tag}>")

        runtime_attributes = {
            "script": ("src",), "link": ("href",), "img": ("src",), "image": ("href",),
            "use": ("href",), "source": ("src",), "video": ("src", "poster"), "audio": ("src",),
        }
        for attribute in runtime_attributes.get(tag, ()):
            if attribute in values:
                if _external_or_active_url(values[attribute]):
                    self.errors.append(f"index.html forbids external runtime URL on <{tag}>")
                elif not _safe_local_runtime_path(values[attribute]):
                    self.errors.append(f"index.html requires a safe package-relative runtime path on <{tag}>")
        if "srcset" in values:
            urls = [candidate.strip().split()[0] for candidate in values["srcset"].split(",") if candidate.strip()]
            if any(_external_or_active_url(url) for url in urls): self.errors.append(f"index.html forbids external srcset on <{tag}>")

        if tag == "script":
            if values.get("src"):
                if values["src"] != "app.js": self.errors.append("index.html only allows the local app.js runtime")
            elif values.get("type", "").lower() == "application/ld+json":
                if self.json_ld is not None: self.errors.append("nested JSON-LD scripts are invalid")
                self.json_ld = []
            else:
                self.errors.append("index.html forbids inline executable scripts")

    def handle_data(self, data: str) -> None:
        if self.json_ld is not None: self.json_ld.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.json_ld is not None:
            try:
                json.loads("".join(self.json_ld), parse_constant=_reject_json_constant)
            except (json.JSONDecodeError, ValueError) as exc:
                self.errors.append(f"index.html contains invalid JSON-LD: {exc}")
            self.json_ld = None

    def close(self) -> None:
        super().close()
        if self.json_ld is not None: self.errors.append("index.html contains an unclosed JSON-LD script")


def audit_html_runtime(html: str) -> list[str]:
    audit = RuntimeHTMLAudit()
    audit.feed(html)
    audit.close()
    return audit.errors


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file(): errors.append(f"missing required file: {relative}")

    if errors:
        for error in errors: print(f"- {error}")
        return 1

    text_files = [path for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".html", ".css", ".js", ".json", ".yaml", ".yml", ".py", ".svg"} and ".git" not in path.parts]
    placeholder_pattern = r"\b(" + "|".join(["TO" + "DO", "TB" + "D", "FIX" + "ME"]) + r")\b"
    for path in text_files:
        content = path.read_text(encoding="utf-8")
        if re.search(placeholder_pattern, content, re.IGNORECASE): errors.append(f"placeholder marker in {path.relative_to(ROOT)}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\nname: inkbrush-motion-skill\n"): errors.append("SKILL.md frontmatter name is missing or incorrect")
    if "9:16" not in skill or "STATIC_REVIEW_READY" not in skill: errors.append("SKILL.md is missing the portrait/static-first contract")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "MIT License" not in license_text or "2026 Vivi (GoAskVivi)" not in license_text: errors.append("LICENSE is not the expected MIT notice")
    copyright_text = (ROOT / "COPYRIGHT.md").read_text(encoding="utf-8")
    for marker in ["AI-assistance disclosure", "Third-party material", "Names and endorsement"]:
        if marker not in copyright_text: errors.append(f"COPYRIGHT.md missing section: {marker}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if '<img src="assets/inkbrush-motion-demo.gif"' not in readme:
        errors.append("README.md must lead with the animated delivery demo")

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for element_id in ["replay", "motion-status", "ink-stage", "river-path", "river-diffusion", "river-dry", "river-dry-mask", "brush", "moving-brush"]:
        if f'id="{element_id}"' not in html: errors.append(f"index.html missing required id: {element_id}")
    errors.extend(audit_html_runtime(html))
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    if re.search(r"@import\b|url\(\s*[\"']?(?:https?:)?//", css, re.IGNORECASE): errors.append("styles.css must not import external runtime resources")
    javascript = (ROOT / "app.js").read_text(encoding="utf-8")
    if re.search(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\b|navigator\.sendBeacon|import\s*\(\s*[\"'](?:https?:)?//", javascript): errors.append("app.js must not make runtime network requests")
    for relative in BRUSH_ASSET_SHA256:
        if relative not in javascript: errors.append(f"app.js is missing the nine-action brush asset: {relative}")
    for svg_name in ["assets/icon.svg", "assets/social-preview.svg", "assets/static-board.svg"]:
        try:
            validate_svg_safety(ROOT / svg_name, allow_local_png=svg_name == "assets/static-board.svg")
        except ValueError as exc:
            errors.append(str(exc))

    try:
        schema = json.loads((ROOT / "references/storyboard.schema.json").read_text(encoding="utf-8"), parse_constant=_reject_json_constant)
        if schema.get("title") != "InkBrush Motion Storyboard": errors.append("storyboard schema title is incorrect")
        schema_properties = schema.get("properties", {})
        if schema.get("additionalProperties") is not False or set(schema_properties) != TOP_LEVEL_FIELDS: errors.append("schema top-level fields drift from the Python validator")
        if set(schema.get("required", [])) != REQUIRED_FIELDS: errors.append("schema required fields drift from the Python validator")
        if set(schema_properties.get("status", {}).get("enum", [])) != STATES: errors.append("schema status enum drifts from the Python validator")
        if set(schema_properties.get("styleRecipe", {}).get("enum", [])) != STYLE_RECIPES: errors.append("schema styleRecipe enum drifts from the Python validator")
        if set(schema_properties.get("brushMode", {}).get("enum", [])) != BRUSH_MODES: errors.append("schema brushMode enum drifts from the Python validator")
        hand_schema = schema_properties.get("realHandProfile", {})
        if hand_schema.get("additionalProperties") is not False or set(hand_schema.get("properties", {})) != REAL_HAND_FIELDS: errors.append("schema realHandProfile fields drift from the Python validator")
        if set(hand_schema.get("required", [])) != REAL_HAND_FIELDS: errors.append("schema required realHandProfile fields drift from the Python validator")
        if hand_schema.get("properties", {}).get("actions", {}).get("const") != NINE_ACTIONS: errors.append("schema nine-action sequence drifts from the Python validator")
        ink_schema = hand_schema.get("properties", {}).get("inkPhysics", {})
        if ink_schema.get("additionalProperties") is not False or set(ink_schema.get("properties", {})) != INK_PHYSICS_FIELDS: errors.append("schema inkPhysics fields drift from the Python validator")
        if set(ink_schema.get("required", [])) != INK_PHYSICS_FIELDS: errors.append("schema required inkPhysics fields drift from the Python validator")
        beat_schema = schema_properties.get("beats", {}).get("items", {})
        if beat_schema.get("additionalProperties") is not False or set(beat_schema.get("properties", {})) != BEAT_FIELDS: errors.append("schema beat fields drift from the Python validator")
        if set(beat_schema.get("required", [])) != {"id", "label", "copy", "startSecond", "endSecond"}: errors.append("schema required beat fields drift from the Python validator")
        motion_schema = schema_properties.get("motionEvidence", {})
        if motion_schema.get("additionalProperties") is not False or set(motion_schema.get("properties", {})) != MOTION_FIELDS: errors.append("schema motionEvidence fields drift from the Python validator")
        if set(motion_schema.get("properties", {}).get("rendererLane", {}).get("enum", [])) != RENDERER_LANES: errors.append("schema rendererLane enum drifts from the Python validator")
        frame_schema = motion_schema.get("properties", {}).get("frames", {}).get("items", {})
        if frame_schema.get("additionalProperties") is not False or set(frame_schema.get("properties", {})) != FRAME_FIELDS: errors.append("schema frame fields drift from the Python validator")
        expected_schema_gates = [
            {"oneOf": [
                {"properties": {"width": {"const": 720}, "height": {"const": 1280}}},
                {"properties": {"width": {"const": 1080}, "height": {"const": 1920}}},
            ]},
            {"if": {"properties": {"status": {"enum": sorted(["STATIC_REVIEW_READY", "MOTION_PROOF_READY", "RENDERER_REQUIRED"])}}}, "then": {"required": ["staticArtifact", "staticArtifactSha256"]}},
            {"if": {"properties": {"status": {"const": "MOTION_PROOF_READY"}}}, "then": {"required": ["motionEvidence"]}, "else": {"not": {"required": ["motionEvidence"]}}},
            {"if": {"properties": {"status": {"const": "PLAN_ONLY"}}}, "then": {"not": {"anyOf": [{"required": ["staticArtifact"]}, {"required": ["staticArtifactSha256"]}]}}},
            {"if": {"properties": {"brushMode": {"const": "real-hand-nine-action"}}, "required": ["brushMode"]}, "then": {"required": ["realHandProfile"]}, "else": {"not": {"required": ["realHandProfile"]}}},
            {"if": {"properties": {"status": {"const": "MOTION_PROOF_READY"}, "brushMode": {"const": "real-hand-nine-action"}}, "required": ["status", "brushMode"]}, "then": {"properties": {"motionEvidence": {"required": ["nineActionProof", "nineActionProofSha256"]}}}},
        ]
        if schema.get("allOf") != expected_schema_gates: errors.append("schema state and dimension gates drift from the Python validator")
        plan = json.loads((ROOT / "assets/demo-plan.json").read_text(encoding="utf-8"), parse_constant=_reject_json_constant)
        errors.extend(f"demo-plan: {error}" for error in validate(plan, ROOT))
        for beat in plan.get("beats", []):
            for field in ("label", "copy"):
                exact_text = beat.get(field)
                if isinstance(exact_text, str) and exact_text not in html:
                    errors.append(f"index.html is missing exact demo-plan beat {field}: {exact_text!r}")
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(f"invalid JSON: {exc}")

    try:
        if png_dimensions(ROOT / "assets/social-preview.png") != (1280, 640): errors.append("assets/social-preview.png must be 1280x640")
        if png_dimensions(ROOT / "assets/ai-agent-knowledge-journey.png") != (1080, 1920): errors.append("assets/ai-agent-knowledge-journey.png must be 1080x1920")
        if png_dimensions(ROOT / "assets/ai-agent-knowledge-prestroke.png") != (1080, 1920): errors.append("assets/ai-agent-knowledge-prestroke.png must be 1080x1920")
        clean_plate = ROOT / "assets/ai-agent-knowledge-cleanplate.png"
        if png_dimensions(clean_plate) != (1080, 1920): errors.append("assets/ai-agent-knowledge-cleanplate.png must be 1080x1920")
        if sha256_file(clean_plate) != CLEAN_PLATE_SHA256: errors.append("assets/ai-agent-knowledge-cleanplate.png does not match the approved provenance hash")
        final_brush = ROOT / "assets/brush-pose-final.png"
        if png_dimensions(final_brush) != (720, 1280): errors.append("assets/brush-pose-final.png must be 720x1280")
        if sha256_file(final_brush) != FINAL_BRUSH_SHA256: errors.append("assets/brush-pose-final.png must be byte-identical to the approved LEAVE pose")
        for relative, expected_hash in BRUSH_ASSET_SHA256.items():
            brush_asset = ROOT / relative
            if png_dimensions(brush_asset) != (720, 1280): errors.append(f"{relative} must be 720x1280")
            if sha256_file(brush_asset) != expected_hash: errors.append(f"{relative} does not match the approved provenance hash")
        real_brush_reference = ROOT / "assets/reference/real-brush-gray-linen.png"
        if png_dimensions(real_brush_reference) != (720, 1280): errors.append("assets/reference/real-brush-gray-linen.png must be 720x1280")
        if sha256_file(real_brush_reference) != REAL_BRUSH_REFERENCE_SHA256: errors.append("assets/reference/real-brush-gray-linen.png does not match the approved provenance hash")
        nine_action_proof = ROOT / "assets/nine-action-proof.png"
        if png_dimensions(nine_action_proof) != (1080, 1920): errors.append("assets/nine-action-proof.png must be 1080x1920")
        if sha256_file(nine_action_proof) != NINE_ACTION_PROOF_SHA256: errors.append("assets/nine-action-proof.png does not match the approved provenance hash")
        # The exact approved hash below binds the compressed pixels. Structural parsing
        # stays fast in repeated negative suites; full LZW decoding is covered directly
        # by artifact_checks tests and the published capture record.
        gif_width, gif_height, gif_frames, gif_duration_ms = gif_metadata(ROOT / "assets/inkbrush-motion-demo.gif", validate_lzw=False)
        if abs(gif_width * 16 - gif_height * 9) > 16: errors.append("assets/inkbrush-motion-demo.gif must be native 9:16")
        if gif_frames < 80: errors.append("assets/inkbrush-motion-demo.gif must contain at least 80 animation frames")
        if not 9_000 <= gif_duration_ms <= 12_000: errors.append("assets/inkbrush-motion-demo.gif must run for 9 to 12 seconds")
        actual_gif_hash = sha256_file(ROOT / "assets/inkbrush-motion-demo.gif")
        if actual_gif_hash != README_GIF_SHA256: errors.append("assets/inkbrush-motion-demo.gif does not match the approved provenance hash")
        animation_record = (ROOT / "references/readme-animation-record.md").read_text(encoding="utf-8")
        if "<!--" in animation_record or "-->" in animation_record:
            errors.append("readme animation record forbids HTML comments that can hide provenance")
        for relative, expected_hash in README_SOURCE_SHA256.items():
            if sha256_file(ROOT / relative) != expected_hash:
                errors.append(f"{relative} does not match the approved README capture source hash")
        expected_source_line = "- Source code identity: " + "; ".join(
            f"`{relative}` SHA-256 `{expected_hash}`" for relative, expected_hash in README_SOURCE_SHA256.items()
        ) + "."
        source_lines = [line for line in animation_record.splitlines() if line.startswith("- Source code identity:")]
        if source_lines != [expected_source_line]:
            errors.append("readme animation record must contain one exact capture source identity line")
        gif_rows = [line for line in animation_record.splitlines() if line.startswith("| `assets/inkbrush-motion-demo.gif` |")]
        expected_gif_row = [
            "`assets/inkbrush-motion-demo.gif`", "292×519", "83", "10.3 seconds", f"`{README_GIF_SHA256}`",
        ]
        parsed_gif_row = [cell.strip() for cell in gif_rows[0].strip().strip("|").split("|")] if len(gif_rows) == 1 else []
        if parsed_gif_row != expected_gif_row:
            errors.append("readme animation record must contain one exact approved GIF table row")
    except ValueError as exc:
        errors.append(str(exc))

    if errors:
        print("FAIL: package validation")
        for error in errors: print(f"- {error}")
        return 1
    print(f"PASS: public package contains {len(REQUIRED)} required artifacts and a verified static demo plan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
