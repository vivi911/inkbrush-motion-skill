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
from motion_timing import (
    load_motion_timing,
    minimum_final_hold_frames,
    preview_metrics,
    validate_motion_timing,
)
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
README_GIF_SHA256 = "a3160d3d094dc5473fe73c13d67e067300c5d08641946045424524f9f7ad7929"
README_SOURCE_SHA256 = {
    "index.html": "0e8b475da0708e7c136791dc461ffc7844e1d4745a12884e95f929af261b740a",
    "styles.css": "efdcff1009fde42b6670791333082ad808434e2c11a4b99ab308455aa9e668d7",
    "motion-timing.js": "b2db8b094527aaacdc3febf9f004b2ffc23f3b72ff3f8462f1e76f6b441cc6aa",
    "app.js": "71804469abd11aa52b45e7b8cc391b426b1f63f7f09ca2ee97ffb3fa6f32d1cf",
    "scripts/motion_timing.py": "6417a4b90b29dff1ab584e6c0930fde04a93a0472526a9451f9d915541154700",
    "scripts/render_readme_gif.py": "91d94c2a0b38547a6326da2a7f7a22ab40f0cdd250b68cb2dbae030f7a89b5bd",
}
HERO_EVIDENCE_SHA256 = {
    "assets/evidence/hero-start.png": "135d924707022680d773158d93e383aa1681a58fdcfeec5fb62694b8aacf28fb",
    "assets/evidence/hero-middle.png": "4f4d2736a61e16d3e83664af77e47a8c61b20d3653c67c8c4a5166fe969e32e3",
    "assets/evidence/hero-end.png": "d0468aa84929c405a7c9c410b968b863a4211ac33fadb991eb3b9bcb982a3332",
}
BRUSH_ASSET_SHA256 = {
    "assets/brush-poses-v5/pose-01.png": "0395742b0478962b0dcd09ccc292db797a5e3d9e0f8eec8b26a0f8c1ce91396f",
    "assets/brush-poses-v5/pose-02.png": "3b7d85a04a7a694685d5c6f1944972936d8bf422e544c9841e2dd91a28a176ad",
    "assets/brush-poses-v5/pose-03.png": "3b0f97e63d0b4d355d43c6568d538a29e15e70528bbed2c7dca115bc3c2922cb",
    "assets/brush-poses-v5/pose-04.png": "dfafed3c777090a411e2e84f4854b1e288255f1f235dd527235399f7bbfafe5c",
    "assets/brush-poses-v5/pose-05.png": "d379bc9a2e4c367763d377039ea720a61f11fd8e54f292940625f3b796f58a74",
    "assets/brush-poses-v5/pose-06.png": "45c4296951793fb2f3190fb1b5be67be813d0d2dcf9dda3a69df0b66484d7217",
    "assets/brush-poses-v5/pose-07.png": "b14c6d6b0135fab607d8929dbfdee1ad9a572a4f38d1b7bb4b3459d60d8a9225",
    "assets/brush-poses-v5/pose-08.png": "fe02935133e310ab47198111eca3c5b52f3ca944d43f82facc186fe45104beff",
    "assets/brush-poses-v5/pose-09.png": "a18e3f4c1424688e0134163caf4e8b896acb25379b84dc36bebe4537a4b77681",
}
HISTORICAL_BRUSH_ASSET_SHA256 = {
    "assets/brush-poses-v2/pose-01.png": "7cb1b6e47eab38f5294d08fb1b51ff256466a97667973a867ae616a6da0bb429",
    "assets/brush-poses-v2/pose-02.png": "700d83a95e5446753156b83d5d0cb5a4c035e11f5ee27628a447d39cc0248752",
    "assets/brush-poses-v2/pose-03.png": "a8141623bf31bd41a877094b19bc5ce259bd3603f60503ed9d111afb6a9a371a",
    "assets/brush-poses-v2/pose-04.png": "43c5c9df05d6f16e10b93c7ea7bef6eabf43296bd9a3c8687e6a73380b51bc31",
    "assets/brush-poses-v2/pose-05.png": "041a7542a138d679927ff8a17c4a89c2965f7ed55cfbe1e4fa8f0581f5e947e2",
    "assets/brush-poses-v2/pose-06.png": "e5f86d96a3162d775cd636adedd996af9ab48023813a3a30a52bd8b6990df259",
    "assets/brush-poses-v2/pose-07.png": "485711d794e1226b4998030146b369f399fc8a2c3cc8a69b28c5ae4a21fb1eaa",
    "assets/brush-poses-v2/pose-08.png": "7ccf6b02f089410fb140de231dc2535208ec432e15598ca2e3e240929dd92000",
    "assets/brush-poses-v2/pose-09.png": "8d7ae7052800f11be0acece156ea83e379d1135ca09a14fbaf90ffc7b71a1872",
    "assets/brush-poses-v3/pose-01.png": "4bb53d10c827c59cf3542632e57d78a209a9d187e97047a04b7ae923b75eac92",
    "assets/brush-poses-v3/pose-02.png": "5e825a3eaf858603787417810a5d9d77178a6eb228059190e4ab32eea817829c",
    "assets/brush-poses-v3/pose-03.png": "21535db0230d5d096921d2999d242175b4f66cee9c220ab4195d0eed26204cfc",
    "assets/brush-poses-v3/pose-04.png": "a183c74c530a5a28c8ff2f9189e325d1ba9504f57c75f2fd9d26d307d7a2d823",
    "assets/brush-poses-v3/pose-05.png": "5927e49445362ea1a1e49ed743e8ee587ba3e072476996d37aa410401c3c7924",
    "assets/brush-poses-v3/pose-06.png": "805812a945f34cb3db27e1b289cfcd1be7d27d7bbd5696794d908a28e121f9f5",
    "assets/brush-poses-v3/pose-07.png": "3f7f1e077de59f5a84484ee39bb0338ef3a320b7b6fda980fe8c9e4206ad89cb",
    "assets/brush-poses-v3/pose-08.png": "63dc0996a9ac75e4b0cb5a283249c1d3b5c00f2097b4aa6261c1e33b63eed311",
    "assets/brush-poses-v3/pose-09.png": "a9f8a713feffd92e911aa6d5e52b8716f641a48d34f7f73c32c2588bace68b00",
    "assets/brush-poses-v4/pose-01.png": "142ca1b8d1b8ef3eea85a432fce5aa7f17641a5c3be84865158231c0c845589a",
    "assets/brush-poses-v4/pose-02.png": "d009180e4687c586c89b6700eec255fa2f487cde5093699dc42391169dd95c8e",
    "assets/brush-poses-v4/pose-03.png": "4937512b84b0144d4c4aecb5fa07859d13a123817cfff0f57a510e78e41436f0",
    "assets/brush-poses-v4/pose-04.png": "b0a6b592427f419880a6bfe8952e961f423b422cbe9d736d8aa6c6fbfcd4c213",
    "assets/brush-poses-v4/pose-05.png": "31b51a36e37cc13251b78454c67fe78f18f22a93dd74fe006e9322ec9523b649",
    "assets/brush-poses-v4/pose-06.png": "2570c9d48f093e7648ebf1eeedbf34855e976dcf655a1919cf8b0d03fecb9ee9",
    "assets/brush-poses-v4/pose-07.png": "7511f86429b2eb677f9c9219c918f1a3d9f87cf9e0d7b96d5f279dad01c75a63",
    "assets/brush-poses-v4/pose-08.png": "96b02f554de2800e8722114f1b47f5bf221145ef67eb91828596810c4077dd88",
    "assets/brush-poses-v4/pose-09.png": "a0fd8190962e75cd24b7f8e0ed5a9659c36450512ae867f78925dff54729a3d2",
}
FINAL_BRUSH_SHA256 = BRUSH_ASSET_SHA256["assets/brush-poses-v5/pose-09.png"]
V5_SOURCE_SHA256 = "569fb216f3510dcff04813ad451e96d09d458a6ca61bb942d2d57558fce9f6d9"
V5_BUILDER_SHA256 = "6ddf2f0561ab0f3f5bd8081d91b0f865515134d4b776c0d4a1d2fddc885c617c"
V5_MANIFEST_SHA256 = "573fb65d5a10fd22eabfc05e0bf0fa5a0bfe81a97b431a6ab780e7e4fec2e7b5"
CLEAN_PLATE_SHA256 = "37e16d24d69537bcdbb88dcee8307b78ae77a02c05fec79d82bc77a8a5f2e658"
REAL_BRUSH_REFERENCE_SHA256 = "49153b50a9a56539430099af1aa6475957b9bc7b9630075bdebc9927fcb6f85d"
NINE_ACTION_PROOF_SHA256 = "b9e6d42f916c3bba43ac44c5ec76dc1e1daccb7f065ed002b42854a641e9dfe7"
REQUIRED = [
    ".gitignore", ".nojekyll", ".github/workflows/validate.yml",
    "SKILL.md", "README.md", "README.zh-TW.md", "LICENSE", "COPYRIGHT.md", "CONTRIBUTING.md",
    "SECURITY.md", "index.html", "styles.css", "motion-timing.js", "app.js", "agents/openai.yaml",
    "assets/icon.svg", "assets/static-board.svg", "assets/social-preview.svg", "assets/social-preview.png", "assets/inkbrush-motion-demo.gif",
    "assets/ai-agent-knowledge-journey.png", "assets/ai-agent-knowledge-prestroke.png", "assets/ai-agent-knowledge-cleanplate.png",
    "assets/brush-pose-final.png", *BRUSH_ASSET_SHA256, *HISTORICAL_BRUSH_ASSET_SHA256, "assets/reference/real-brush-gray-linen.png",
    "assets/reference/brush-hand-sheet-v5.png", "assets/brush-poses-v5/manifest.json",
    "assets/nine-action-proof.png", "assets/evidence/start.png", "assets/evidence/middle.png", "assets/evidence/end.png", *HERO_EVIDENCE_SHA256, "assets/demo-plan.json",
    "references/style-contract.md", "references/motion-contract.md", "references/qa-rubric.md",
    "references/real-brush-contract.md", "references/copyright-and-provenance.md", "references/image-generation-record.md", "references/readme-animation-record.md", "references/open-source-notes.md", "references/storyboard.schema.json",
    "scripts/build_calligraphy_brush_v5.py", "scripts/generate_social_preview.py", "scripts/motion_timing.py", "scripts/prepare_nine_action_sprites.py", "scripts/render_readme_gif.py", "scripts/test_build_calligraphy_brush_v5.py", "scripts/test_validate_package.py", "scripts/test_validate_storyboard.py",
]
FORBIDDEN_PUBLIC_BUNDLES = [".agents", "skills-lock.json"]


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
                if values["src"] not in {"motion-timing.js", "app.js"}: self.errors.append("index.html only allows the local timing and app runtimes")
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
    for relative in FORBIDDEN_PUBLIC_BUNDLES:
        if (ROOT / relative).exists():
            errors.append(f"forbidden third-party tooling bundle in public package: {relative}")
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
    if '<img src="assets/inkbrush-motion-demo.gif"' not in readme or 'width="360"' not in readme.split("</a>", 1)[0]:
        errors.append("README.md must lead with the 360-pixel animated delivery demo")
    if "Tip leads → Ink absorbs → Evidence holds" not in readme:
        errors.append("README.md must state the three-part first-screen proof")
    for relative in HERO_EVIDENCE_SHA256:
        if f'src="{relative}"' not in readme:
            errors.append(f"README.md is missing first-screen evidence: {relative}")

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for element_id in ["replay", "motion-status", "ink-stage", "river-path", "river-diffusion", "river-dry", "river-dry-mask", "brush", "moving-brush"]:
        if f'id="{element_id}"' not in html: errors.append(f"index.html missing required id: {element_id}")
    errors.extend(audit_html_runtime(html))
    if html.find('src="motion-timing.js"') > html.find('src="app.js"') or html.find('src="motion-timing.js"') < 0:
        errors.append("index.html must load motion-timing.js before app.js")
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    if re.search(r"@import\b|url\(\s*[\"']?(?:https?:)?//", css, re.IGNORECASE): errors.append("styles.css must not import external runtime resources")
    javascript = (ROOT / "app.js").read_text(encoding="utf-8")
    if re.search(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\b|navigator\.sendBeacon|import\s*\(\s*[\"'](?:https?:)?//", javascript): errors.append("app.js must not make runtime network requests")
    renderer_source = (ROOT / "scripts/render_readme_gif.py").read_text(encoding="utf-8")
    if "assets/brush-poses-v5/pose-" not in renderer_source:
        errors.append("README renderer must consume the active v5 brush sprites")
    if re.search(r"assets/brush-poses-v[234]/pose-", javascript + html + renderer_source):
        errors.append("active demo consumers must not load historical brush sprites")
    try:
        timing = load_motion_timing(ROOT / "motion-timing.js")
        errors.extend(validate_motion_timing(timing))
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
        timing = None
    for timing_key in ["context", "action", "evidence", "result"]:
        if f'data-threshold-key="{timing_key}"' not in html:
            errors.append(f"index.html is missing semantic timing key: {timing_key}")
    for relative in BRUSH_ASSET_SHA256:
        if relative not in javascript: errors.append(f"app.js is missing the nine-action brush asset: {relative}")
    if 'href="assets/brush-poses-v5/pose-01.png"' not in html:
        errors.append("index.html initial brush must use the active v5 HOVER pose")
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
        if timing is not None and schema_properties.get("finalHoldFrames", {}).get("minimum") != minimum_final_hold_frames(timing): errors.append("schema final hold minimum drifts from the motion timing contract")
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
        plan_ink = plan.get("realHandProfile", {}).get("inkPhysics", {})
        if timing is not None and (
            plan_ink.get("diffusionDelayFrames") != timing["inkDelays"]["diffusionFrames"]
            or plan_ink.get("dryingDelayFrames") != timing["inkDelays"]["dryingFrames"]
        ):
            errors.append("demo-plan ink delays drift from the shared motion timing contract")
        for beat in plan.get("beats", []):
            for field in ("label", "copy"):
                exact_text = beat.get(field)
                if isinstance(exact_text, str) and exact_text not in html:
                    errors.append(f"index.html is missing exact demo-plan beat {field}: {exact_text!r}")
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(f"invalid JSON: {exc}")

    try:
        manifest_path = ROOT / "assets/brush-poses-v5/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"), parse_constant=_reject_json_constant)
        manifest_fields = {"schemaVersion", "assetVersion", "description", "source", "sourceSha256", "sourceSize", "canvas", "anchor", "actions"}
        if not isinstance(manifest, dict) or set(manifest) != manifest_fields:
            errors.append("v5 brush manifest top-level fields drift")
        elif (
            manifest.get("schemaVersion") != 1
            or manifest.get("assetVersion") != "v5"
            or manifest.get("source") != "assets/reference/brush-hand-sheet-v5.png"
            or manifest.get("sourceSha256") != V5_SOURCE_SHA256
            or manifest.get("sourceSize") != [941, 1672]
            or manifest.get("canvas") != [720, 1280]
            or manifest.get("anchor") != [315, 620]
        ):
            errors.append("v5 brush manifest identity or dimensions drift")
        actions = manifest.get("actions") if isinstance(manifest, dict) else None
        action_fields = {"index", "action", "sourceCell", "transform", "anchor", "output", "sha256"}
        if not isinstance(actions, list) or len(actions) != 9:
            errors.append("v5 brush manifest must contain nine actions")
        else:
            for index, record in enumerate(actions, start=1):
                relative = f"assets/brush-poses-v5/pose-{index:02d}.png"
                expected_transform = {
                    "kind": "photographic-raster-axial-pressure",
                    "terminalCrop": [282, 452, 354, 624],
                    "ferruleHeight": 42,
                    "hairHeight": 60,
                    "maxWidth": 27,
                    "bendPx": 0.0,
                    "tipWidth": 3,
                    "shaftOverlapPx": 4,
                } if index == 3 else {"kind": "source-photographic"}
                if not isinstance(record, dict) or set(record) != action_fields:
                    errors.append(f"v5 brush manifest action {index:02d} fields drift")
                    continue
                if (
                    record.get("index") != index
                    or record.get("action") != NINE_ACTIONS[index - 1]
                    or record.get("sourceCell") != index
                    or record.get("transform") != expected_transform
                    or record.get("anchor") != [315, 620]
                    or record.get("output") != relative
                    or record.get("sha256") != BRUSH_ASSET_SHA256[relative]
                ):
                    errors.append(f"v5 brush manifest action {index:02d} identity or transform drift")
        if sha256_file(manifest_path) != V5_MANIFEST_SHA256:
            errors.append("v5 brush manifest does not match the approved provenance hash")
        if sha256_file(ROOT / "scripts/build_calligraphy_brush_v5.py") != V5_BUILDER_SHA256:
            errors.append("v5 brush builder does not match the approved provenance hash")
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(f"invalid v5 brush manifest: {exc}")

    try:
        if png_dimensions(ROOT / "assets/social-preview.png") != (1280, 640): errors.append("assets/social-preview.png must be 1280x640")
        if png_dimensions(ROOT / "assets/ai-agent-knowledge-journey.png") != (1080, 1920): errors.append("assets/ai-agent-knowledge-journey.png must be 1080x1920")
        if png_dimensions(ROOT / "assets/ai-agent-knowledge-prestroke.png") != (1080, 1920): errors.append("assets/ai-agent-knowledge-prestroke.png must be 1080x1920")
        clean_plate = ROOT / "assets/ai-agent-knowledge-cleanplate.png"
        if png_dimensions(clean_plate) != (1080, 1920): errors.append("assets/ai-agent-knowledge-cleanplate.png must be 1080x1920")
        if sha256_file(clean_plate) != CLEAN_PLATE_SHA256: errors.append("assets/ai-agent-knowledge-cleanplate.png does not match the approved provenance hash")
        v5_source = ROOT / "assets/reference/brush-hand-sheet-v5.png"
        if png_dimensions(v5_source) != (941, 1672): errors.append("assets/reference/brush-hand-sheet-v5.png must be 941x1672")
        if sha256_file(v5_source) != V5_SOURCE_SHA256: errors.append("assets/reference/brush-hand-sheet-v5.png does not match the approved provenance hash")
        final_brush = ROOT / "assets/brush-pose-final.png"
        if png_dimensions(final_brush) != (720, 1280): errors.append("assets/brush-pose-final.png must be 720x1280")
        if sha256_file(final_brush) != FINAL_BRUSH_SHA256: errors.append("assets/brush-pose-final.png must be byte-identical to the approved LEAVE pose")
        for relative, expected_hash in BRUSH_ASSET_SHA256.items():
            brush_asset = ROOT / relative
            if png_dimensions(brush_asset) != (720, 1280): errors.append(f"{relative} must be 720x1280")
            if sha256_file(brush_asset) != expected_hash: errors.append(f"{relative} does not match the approved provenance hash")
        for relative, expected_hash in HISTORICAL_BRUSH_ASSET_SHA256.items():
            brush_asset = ROOT / relative
            if png_dimensions(brush_asset) != (720, 1280): errors.append(f"{relative} must be 720x1280")
            if sha256_file(brush_asset) != expected_hash: errors.append(f"{relative} does not match the disclosed historical provenance hash")
        real_brush_reference = ROOT / "assets/reference/real-brush-gray-linen.png"
        if png_dimensions(real_brush_reference) != (720, 1280): errors.append("assets/reference/real-brush-gray-linen.png must be 720x1280")
        if sha256_file(real_brush_reference) != REAL_BRUSH_REFERENCE_SHA256: errors.append("assets/reference/real-brush-gray-linen.png does not match the approved provenance hash")
        nine_action_proof = ROOT / "assets/nine-action-proof.png"
        if png_dimensions(nine_action_proof) != (1080, 1920): errors.append("assets/nine-action-proof.png must be 1080x1920")
        if sha256_file(nine_action_proof) != NINE_ACTION_PROOF_SHA256: errors.append("assets/nine-action-proof.png does not match the approved provenance hash")
        for relative, expected_hash in HERO_EVIDENCE_SHA256.items():
            hero_evidence = ROOT / relative
            if png_dimensions(hero_evidence) != (360, 240): errors.append(f"{relative} must be 360x240")
            if sha256_file(hero_evidence) != expected_hash: errors.append(f"{relative} does not match the approved provenance hash")
        # The exact approved hash below binds the compressed pixels. Structural parsing
        # stays fast in repeated negative suites; full LZW decoding is covered directly
        # by artifact_checks tests and the published capture record.
        gif_width, gif_height, gif_frames, gif_duration_ms = gif_metadata(ROOT / "assets/inkbrush-motion-demo.gif", validate_lzw=False)
        if timing is None:
            raise ValueError("motion timing contract is unavailable")
        expected_gif = timing["gif"]
        if (gif_width, gif_height) != (expected_gif["width"], expected_gif["height"]): errors.append("assets/inkbrush-motion-demo.gif dimensions drift from the motion timing contract")
        if gif_frames < 55: errors.append("assets/inkbrush-motion-demo.gif must contain at least 55 animation frames")
        expected_duration_ms = round(preview_metrics(timing)["gifDurationMs"])
        if gif_duration_ms != expected_duration_ms: errors.append("assets/inkbrush-motion-demo.gif duration drifts from the motion timing contract")
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
            "`assets/inkbrush-motion-demo.gif`", "360×640", "60", "10.22 seconds", f"`{README_GIF_SHA256}`",
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
