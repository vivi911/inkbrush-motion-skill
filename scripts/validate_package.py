#!/usr/bin/env python3
"""Validate the public InkBrush Motion repository package."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from artifact_checks import png_dimensions, validate_svg_safety
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
REQUIRED = [
    ".gitignore", ".nojekyll", ".github/workflows/validate.yml",
    "SKILL.md", "README.md", "README.zh-TW.md", "LICENSE", "COPYRIGHT.md", "CONTRIBUTING.md",
    "SECURITY.md", "index.html", "styles.css", "app.js", "agents/openai.yaml",
    "assets/icon.svg", "assets/static-board.svg", "assets/social-preview.svg", "assets/social-preview.png",
    "assets/ai-agent-knowledge-journey.png", "assets/ai-agent-knowledge-prestroke.png", "assets/demo-plan.json",
    "references/style-contract.md", "references/motion-contract.md", "references/qa-rubric.md",
    "references/copyright-and-provenance.md", "references/image-generation-record.md", "references/open-source-notes.md", "references/storyboard.schema.json",
    "scripts/generate_social_preview.py", "scripts/test_validate_package.py", "scripts/test_validate_storyboard.py",
]


def _external_or_active_url(value: str) -> bool:
    compact = value.strip().lower()
    return compact.startswith(("http://", "https://", "//", "javascript:", "vbscript:"))


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
            if attribute in values and _external_or_active_url(values[attribute]):
                self.errors.append(f"index.html forbids external runtime URL on <{tag}>")
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

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for element_id in ["replay", "motion-status", "ink-stage", "river-path", "river-diffusion", "brush"]:
        if f'id="{element_id}"' not in html: errors.append(f"index.html missing required id: {element_id}")
    errors.extend(audit_html_runtime(html))
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    if re.search(r"@import\b|url\(\s*[\"']?(?:https?:)?//", css, re.IGNORECASE): errors.append("styles.css must not import external runtime resources")
    javascript = (ROOT / "app.js").read_text(encoding="utf-8")
    if re.search(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\b|navigator\.sendBeacon|import\s*\(\s*[\"'](?:https?:)?//", javascript): errors.append("app.js must not make runtime network requests")
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
