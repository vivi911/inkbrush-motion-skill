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
    FRAME_FIELDS,
    MOTION_FIELDS,
    RENDERER_LANES,
    REQUIRED_FIELDS,
    STATES,
    STYLE_RECIPES,
    TOP_LEVEL_FIELDS,
    _reject_json_constant,
    validate,
)


ROOT = Path(__file__).resolve().parents[1]
README_GIF_SHA256 = "996fca6cb98cbaa94bb8bb65d85cccb5b4b964e57276856f2f1abc2a90838194"
README_SOURCE_SHA256 = {
    "index.html": "a70ed1a398a017c518730061193ea10eb0c80b60922c563d9dee92ee04d833e5",
    "styles.css": "3d4cd52a499ae9c48311a98bc363422fad7264db96a7cc5388069fc33c061252",
    "app.js": "66fa06127bfa951739364c8fa4552932eae628bb305a1320b30bee206b4d42cd",
}
BRUSH_ASSET_SHA256 = {
    "assets/brush-poses-v2/pose-01.png": "7cb1b6e47eab38f5294d08fb1b51ff256466a97667973a867ae616a6da0bb429",
    "assets/brush-poses-v2/pose-02.png": "700d83a95e5446753156b83d5d0cb5a4c035e11f5ee27628a447d39cc0248752",
    "assets/brush-poses-v2/pose-03.png": "a8141623bf31bd41a877094b19bc5ce259bd3603f60503ed9d111afb6a9a371a",
    "assets/brush-poses-v2/pose-04.png": "43c5c9df05d6f16e10b93c7ea7bef6eabf43296bd9a3c8687e6a73380b51bc31",
    "assets/brush-poses-v2/pose-05.png": "041a7542a138d679927ff8a17c4a89c2965f7ed55cfbe1e4fa8f0581f5e947e2",
    "assets/brush-poses-v2/pose-06.png": "e5f86d96a3162d775cd636adedd996af9ab48023813a3a30a52bd8b6990df259",
    "assets/brush-poses-v2/pose-07.png": "485711d794e1226b4998030146b369f399fc8a2c3cc8a69b28c5ae4a21fb1eaa",
    "assets/brush-poses-v2/pose-08.png": "7ccf6b02f089410fb140de231dc2535208ec432e15598ca2e3e240929dd92000",
    "assets/brush-poses-v2/pose-09.png": "8d7ae7052800f11be0acece156ea83e379d1135ca09a14fbaf90ffc7b71a1872",
}
FINAL_BRUSH_SHA256 = BRUSH_ASSET_SHA256["assets/brush-poses-v2/pose-09.png"]
CLEAN_PLATE_SHA256 = "37e16d24d69537bcdbb88dcee8307b78ae77a02c05fec79d82bc77a8a5f2e658"
REQUIRED = [
    ".gitignore", ".nojekyll", ".github/workflows/validate.yml",
    "SKILL.md", "README.md", "README.zh-TW.md", "LICENSE", "COPYRIGHT.md", "CONTRIBUTING.md",
    "SECURITY.md", "index.html", "styles.css", "app.js", "agents/openai.yaml",
    "assets/icon.svg", "assets/static-board.svg", "assets/social-preview.svg", "assets/social-preview.png", "assets/inkbrush-motion-demo.gif",
    "assets/ai-agent-knowledge-journey.png", "assets/ai-agent-knowledge-prestroke.png", "assets/ai-agent-knowledge-cleanplate.png",
    "assets/brush-pose-final.png", *BRUSH_ASSET_SHA256, "assets/demo-plan.json",
    "references/style-contract.md", "references/motion-contract.md", "references/qa-rubric.md",
    "references/copyright-and-provenance.md", "references/image-generation-record.md", "references/readme-animation-record.md", "references/open-source-notes.md", "references/storyboard.schema.json",
    "scripts/generate_social_preview.py", "scripts/test_validate_package.py", "scripts/test_validate_storyboard.py",
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
    for element_id in ["replay", "motion-status", "ink-stage", "river-path", "river-diffusion", "brush", "moving-brush"]:
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
            "`assets/inkbrush-motion-demo.gif`", "292×519", "103", "10.3 seconds", f"`{README_GIF_SHA256}`",
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
