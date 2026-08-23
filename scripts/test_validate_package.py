#!/usr/bin/env python3
"""Prove that public-package checks fail closed for external runtime and schema drift."""

from __future__ import annotations

import copy
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from artifact_checks import ffmpeg_executable, gif_metadata
from motion_timing import PREFIX, load_motion_timing


ROOT = Path(__file__).resolve().parents[1]


def run_validator(candidate: Path, environment_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.update(environment_overrides or {})
    return subprocess.run(
        [sys.executable, "scripts/validate_package.py"],
        cwd=candidate,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def expect(label: str, condition: bool) -> None:
    if not condition: raise AssertionError(label)
    print(f"PASS: {label}")


def clone_candidate(parent: Path, name: str) -> Path:
    destination = parent / name
    shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(".git", "output", "__pycache__"))
    return destination


def write_timing(path: Path, timing: dict) -> None:
    payload = json.dumps(timing, separators=(",", ":"), ensure_ascii=False)
    path.write_text(f"{PREFIX}{payload};\n", encoding="utf-8")


def write_video_fixture(
    path: Path,
    *,
    size: str = "32x32",
    fps: int = 30,
    duration: float = 1.0,
    codec: str = "libx264",
    audio: bool = False,
) -> None:
    command = [
        ffmpeg_executable(),
        "-y",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        f"color=c=black:s={size}:r={fps}:d={duration}",
    ]
    if audio:
        command.extend(["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono:d={duration}"])
    command.extend(["-c:v", codec, "-pix_fmt", "yuv420p"])
    if audio:
        command.extend(["-c:a", "aac", "-shortest"])
    else:
        command.append("-an")
    command.append(str(path))
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="inkbrush-package-tests-") as temp:
        parent = Path(temp)
        baseline = clone_candidate(parent, "baseline")
        expect("baseline public package passes", run_validator(baseline).returncode == 0)

        agents_case = clone_candidate(parent, "vendored-agent-skill")
        (agents_case / ".agents/skills/motion-graphics").mkdir(parents=True)
        (agents_case / ".agents/skills/motion-graphics/SKILL.md").write_text("third-party tooling\n", encoding="utf-8")
        result = run_validator(agents_case)
        expect("reject vendored agent tooling bundle", result.returncode == 1 and "forbidden third-party tooling bundle" in result.stdout)

        lock_case = clone_candidate(parent, "vendored-skill-lock")
        (lock_case / "skills-lock.json").write_text("{}\n", encoding="utf-8")
        result = run_validator(lock_case)
        expect("reject skill installer lock bundle", result.returncode == 1 and "forbidden third-party tooling bundle" in result.stdout)

        requirements_case = clone_candidate(parent, "drifted-maintainer-requirements")
        requirements_path = requirements_case / "requirements-dev.txt"
        requirements_path.write_text(requirements_path.read_text(encoding="utf-8").replace("imageio-ffmpeg==0.6.0", "imageio-ffmpeg==0.6.1"), encoding="utf-8")
        result = run_validator(requirements_case)
        expect("reject unpinned maintainer video tool drift", result.returncode == 1 and "approved Pillow and imageio-ffmpeg" in result.stdout)

        workflow_tool_case = clone_candidate(parent, "missing-ci-video-tool-gate")
        workflow_path = workflow_tool_case / ".github/workflows/validate.yml"
        workflow_path.write_text(workflow_path.read_text(encoding="utf-8").replace("7.0.2-static", "7.2-static"), encoding="utf-8")
        result = run_validator(workflow_tool_case)
        expect("reject CI without pinned Linux FFmpeg gate", result.returncode == 1 and "exact Linux FFmpeg 7.0.2-static" in result.stdout)

        prefixed_tool_case = clone_candidate(parent, "prefixed-fake-ffmpeg-version")
        fake_tool = parent / "fake-ffmpeg"
        expected_prefix = "7.0.2-static" if platform.system() == "Linux" else "7.1"
        fake_tool.write_text(f"#!/bin/sh\nprintf 'ffmpeg version {expected_prefix}-evil Copyright fake\\n'\n", encoding="utf-8")
        fake_tool.chmod(0o755)
        result = run_validator(prefixed_tool_case, {"INKBRUSH_FFMPEG": str(fake_tool)})
        expect("reject FFmpeg version that only matches the approved prefix", result.returncode == 1 and "pinned FFmpeg" in result.stdout)

        html_case = clone_candidate(parent, "external-html")
        (html_case / "index.html").write_text((html_case / "index.html").read_text(encoding="utf-8") + '\n<script src="//example.com/track.js"></script>\n', encoding="utf-8")
        result = run_validator(html_case)
        expect("reject protocol-relative HTML runtime", result.returncode == 1 and "external runtime" in result.stdout)

        inline_case = clone_candidate(parent, "inline-script")
        (inline_case / "index.html").write_text((inline_case / "index.html").read_text(encoding="utf-8") + "\n<script>alert(1)</script>\n", encoding="utf-8")
        result = run_validator(inline_case)
        expect("reject inline executable script", result.returncode == 1 and "inline executable" in result.stdout)

        base_case = clone_candidate(parent, "external-base")
        (base_case / "index.html").write_text((base_case / "index.html").read_text(encoding="utf-8").replace("<head>", '<head><base href="https://example.com/">'), encoding="utf-8")
        result = run_validator(base_case)
        expect("reject external base URL", result.returncode == 1 and "forbids <base>" in result.stdout)

        srcset_case = clone_candidate(parent, "external-srcset")
        (srcset_case / "index.html").write_text((srcset_case / "index.html").read_text(encoding="utf-8") + '\n<img src="assets/social-preview.png" srcset="//example.com/a.png 2x">\n', encoding="utf-8")
        result = run_validator(srcset_case)
        expect("reject external srcset", result.returncode == 1 and "external srcset" in result.stdout)

        unquoted_case = clone_candidate(parent, "unquoted-src")
        (unquoted_case / "index.html").write_text((unquoted_case / "index.html").read_text(encoding="utf-8") + "\n<script src=//example.com/a.js></script>\n", encoding="utf-8")
        result = run_validator(unquoted_case)
        expect("reject unquoted external src", result.returncode == 1 and "external runtime" in result.stdout)

        style_case = clone_candidate(parent, "inline-style")
        (style_case / "index.html").write_text((style_case / "index.html").read_text(encoding="utf-8") + '\n<div style="background:url(https://example.com/a.png)"></div>\n', encoding="utf-8")
        result = run_validator(style_case)
        expect("reject inline style URL", result.returncode == 1 and "inline style attributes" in result.stdout)

        active_anchor_case = clone_candidate(parent, "active-anchor")
        (active_anchor_case / "index.html").write_text((active_anchor_case / "index.html").read_text(encoding="utf-8") + '\n<a href="javascript:alert(1)">bad</a>\n', encoding="utf-8")
        result = run_validator(active_anchor_case)
        expect("reject active anchor href", result.returncode == 1 and "active href" in result.stdout)

        duplicate_case = clone_candidate(parent, "duplicate-attribute")
        (duplicate_case / "index.html").write_text((duplicate_case / "index.html").read_text(encoding="utf-8") + '\n<script src="//example.com/first.js" src="app.js"></script>\n', encoding="utf-8")
        result = run_validator(duplicate_case)
        expect("reject duplicate runtime attributes", result.returncode == 1 and "duplicate attributes" in result.stdout)

        css_case = clone_candidate(parent, "external-css")
        (css_case / "styles.css").write_text('@import url("//example.com/theme.css");\n' + (css_case / "styles.css").read_text(encoding="utf-8"), encoding="utf-8")
        result = run_validator(css_case)
        expect("reject external CSS import", result.returncode == 1 and "external runtime" in result.stdout)

        js_case = clone_candidate(parent, "network-js")
        (js_case / "app.js").write_text((js_case / "app.js").read_text(encoding="utf-8") + '\nfetch("https://example.com/pixel");\n', encoding="utf-8")
        result = run_validator(js_case)
        expect("reject JavaScript network call", result.returncode == 1 and "network requests" in result.stdout)

        timing_case = clone_candidate(parent, "late-first-ink")
        timing_path = timing_case / "motion-timing.js"
        timing = load_motion_timing(timing_path)
        timing["breaks"][0] = 0.09; timing["strokeSegments"][0][0] = 0.09
        write_timing(timing_path, timing)
        result = run_validator(timing_case)
        expect("reject first ink after 0.8 seconds", result.returncode == 1 and "first visible ink" in result.stdout)

        timing_case = clone_candidate(parent, "late-first-three")
        timing_path = timing_case / "motion-timing.js"
        timing = load_motion_timing(timing_path)
        timing["breaks"][2] = 0.16; timing["strokeSegments"][1][1] = 0.16; timing["strokeSegments"][2][0] = 0.16
        write_timing(timing_path, timing)
        result = run_validator(timing_case)
        expect("reject hover-touch-press after 1.4 seconds", result.returncode == 1 and "hover-touch-press" in result.stdout)

        timing_case = clone_candidate(parent, "rushed-first-three")
        timing_path = timing_case / "motion-timing.js"
        timing = load_motion_timing(timing_path)
        timing["breaks"][2] = 0.12; timing["strokeSegments"][1][1] = 0.12; timing["strokeSegments"][2][0] = 0.12
        write_timing(timing_path, timing)
        result = run_validator(timing_case)
        expect("reject hover-touch-press before 1.2 seconds", result.returncode == 1 and "hover-touch-press" in result.stdout)

        timing_case = clone_candidate(parent, "late-context")
        timing_path = timing_case / "motion-timing.js"
        timing = load_motion_timing(timing_path)
        timing["knowledgeThresholds"]["context"] = 0.25
        write_timing(timing_path, timing)
        result = run_validator(timing_case)
        expect("reject Context after 2.5 seconds", result.returncode == 1 and "Context reveal" in result.stdout)

        timing_case = clone_candidate(parent, "short-gif-hold")
        timing_path = timing_case / "motion-timing.js"
        timing = load_motion_timing(timing_path)
        timing["gif"]["frameDurationMs"] = 120
        write_timing(timing_path, timing)
        result = run_validator(timing_case)
        expect("reject GIF final hold under 1.1 seconds", result.returncode == 1 and "GIF final hold" in result.stdout)

        timing_case = clone_candidate(parent, "moving-black-tail")
        timing_path = timing_case / "motion-timing.js"
        timing = load_motion_timing(timing_path)
        timing["inkContact"]["activeCoreMaxPixels"] = 40
        write_timing(timing_path, timing)
        result = run_validator(timing_case)
        expect("reject a long black core that travels with the brush", result.returncode == 1 and "active ink core" in result.stdout)

        timing_case = clone_candidate(parent, "seven-pixel-demo-core")
        timing_path = timing_case / "motion-timing.js"
        timing = load_motion_timing(timing_path)
        timing["inkContact"]["activeCoreMaxPixels"] = 7
        write_timing(timing_path, timing)
        result = run_validator(timing_case)
        expect("reject demo core drift from exact six pixels", result.returncode == 1 and "exactly 6 pixels" in result.stdout)

        timing_case = clone_candidate(parent, "pale-fresh-core")
        timing_path = timing_case / "motion-timing.js"
        timing = load_motion_timing(timing_path)
        timing["inkTone"]["freshCoreOpacity"] = 0.7
        write_timing(timing_path, timing)
        result = run_validator(timing_case)
        expect("reject a pale fresh core", result.returncode == 1 and "fresh core opacity" in result.stdout)

        timing_case = clone_candidate(parent, "invalid-fresh-core-color")
        timing_path = timing_case / "motion-timing.js"
        timing = load_motion_timing(timing_path)
        timing["inkTone"]["freshCoreColor"] = "black"
        write_timing(timing_path, timing)
        result = run_validator(timing_case)
        expect("reject an unbound fresh-core color", result.returncode == 1 and "freshCoreColor" in result.stdout)

        tone_case = clone_candidate(parent, "drifted-plan-ink-tone")
        plan_path = tone_case / "assets/demo-plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["realHandProfile"]["inkPhysics"]["wetEdgeOpacity"] = 0.18
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = run_validator(tone_case)
        expect("reject demo-plan ink tone drift", result.returncode == 1 and "ink tone drifts" in result.stdout)

        ink_delay_case = clone_candidate(parent, "drifted-ink-delay")
        plan_path = ink_delay_case / "assets/demo-plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["realHandProfile"]["inkPhysics"]["diffusionDelayFrames"] = 6
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = run_validator(ink_delay_case)
        expect("reject demo-plan ink delay drift", result.returncode == 1 and "ink delays drift" in result.stdout)

        proof_case = clone_candidate(parent, "missing-first-screen-proof")
        proof_path = proof_case / "README.md"
        proof_path.write_text(proof_path.read_text(encoding="utf-8").replace("Tip leads → Ink absorbs → Evidence holds", "Tip leads", 1), encoding="utf-8")
        result = run_validator(proof_case)
        expect("reject README without three-part first-screen proof", result.returncode == 1 and "three-part first-screen proof" in result.stdout)

        example_link_case = clone_candidate(parent, "missing-12-second-example-link")
        example_readme_path = example_link_case / "README.md"
        example_readme_path.write_text(
            example_readme_path.read_text(encoding="utf-8").replace('href="assets/inkbrush-ai-agent-12s.mp4"', 'href="assets/missing.mp4"'),
            encoding="utf-8",
        )
        result = run_validator(example_link_case)
        expect("reject README without approved 12-second MP4 link", result.returncode == 1 and "12-second MP4 and contact sheet" in result.stdout)

        hero_hash_case = clone_candidate(parent, "changed-first-screen-evidence")
        shutil.copyfile(hero_hash_case / "assets/evidence/hero-end.png", hero_hash_case / "assets/evidence/hero-start.png")
        result = run_validator(hero_hash_case)
        expect("reject changed first-screen evidence hash", result.returncode == 1 and "hero-start.png does not match" in result.stdout)

        source_hash_case = clone_candidate(parent, "changed-readme-capture-source")
        (source_hash_case / "app.js").write_text((source_hash_case / "app.js").read_text(encoding="utf-8") + "\n// harmless source drift\n", encoding="utf-8")
        result = run_validator(source_hash_case)
        expect("reject README GIF after capture-source drift", result.returncode == 1 and "capture source hash" in result.stdout)

        source_record_case = clone_candidate(parent, "misbound-readme-capture-source")
        source_record_path = source_record_case / "references/readme-animation-record.md"
        approved_app_hash = "d759f5657437eee95ced784ac72ba365bce7d5406d17ac4a49531cd6c5fc3471"
        source_record_text = source_record_path.read_text(encoding="utf-8").replace(
            f"`app.js` SHA-256 `{approved_app_hash}`",
            f"`app.js` SHA-256 `{'0' * 64}`",
            1,
        )
        source_record_text += f"\n<!-- `app.js` SHA-256 `{approved_app_hash}` -->\n"
        source_record_path.write_text(source_record_text, encoding="utf-8")
        result = run_validator(source_record_case)
        expect("reject capture-source hash hidden outside its provenance field", result.returncode == 1 and "exact capture source identity line" in result.stdout)

        behavior_record_case = clone_candidate(parent, "drifted-ink-behavior-record")
        behavior_record_path = behavior_record_case / "references/readme-animation-record.md"
        behavior_record_path.write_text(behavior_record_path.read_text(encoding="utf-8").replace("`#2b2722`, 92% opacity", "`#2c2722`, 92% opacity", 1), encoding="utf-8")
        result = run_validator(behavior_record_case)
        expect("reject drifted ink behavior record", result.returncode == 1 and "exact ink behavior line" in result.stdout)

        tool_record_case = clone_candidate(parent, "drifted-video-tool-record")
        tool_record_path = tool_record_case / "references/readme-animation-record.md"
        tool_record_path.write_text(tool_record_path.read_text(encoding="utf-8").replace("imageio-ffmpeg 0.6.0;", "imageio-ffmpeg 0.6.1;", 1), encoding="utf-8")
        result = run_validator(tool_record_case)
        expect("reject drifted video tool identity record", result.returncode == 1 and "exact 12-second tool identity line" in result.stdout)

        source_comment_case = clone_candidate(parent, "comment-hidden-capture-source")
        source_comment_path = source_comment_case / "references/readme-animation-record.md"
        source_comment_text = source_comment_path.read_text(encoding="utf-8")
        source_identity_line = next(line for line in source_comment_text.splitlines() if line.startswith("- Source code identity:"))
        source_comment_path.write_text(source_comment_text.replace(source_identity_line, f"<!--\n{source_identity_line}\n-->", 1), encoding="utf-8")
        result = run_validator(source_comment_case)
        expect("reject source identity hidden in multiline HTML comment", result.returncode == 1 and "forbids HTML comments" in result.stdout)

        clean_plate_src = 'src="assets/ai-agent-knowledge-cleanplate.png"'
        for name, unsafe_src in [
            ("traversal", "../outside/cleanplate.png"),
            ("encoded-traversal", "%2e%2e/outside/cleanplate.png"),
            ("absolute", "/tmp/outside/cleanplate.png"),
            ("backslash", "assets\\cleanplate.png"),
        ]:
            path_case = clone_candidate(parent, f"unsafe-html-path-{name}")
            html_path = path_case / "index.html"
            html_path.write_text(html_path.read_text(encoding="utf-8").replace(clean_plate_src, f'src="{unsafe_src}"', 1), encoding="utf-8")
            result = run_validator(path_case)
            expect(f"reject {name} HTML runtime path", result.returncode == 1 and "safe package-relative runtime path" in result.stdout)

        schema_case = clone_candidate(parent, "schema-drift")
        schema_path = schema_case / "references/storyboard.schema.json"
        schema_text = schema_path.read_text(encoding="utf-8").replace('"$schema": {"type": "string"}', '"$schema": {"type": "string"}, "unexpected": {"type": "string"}')
        schema_path.write_text(schema_text, encoding="utf-8")
        result = run_validator(schema_case)
        expect("reject schema field drift", result.returncode == 1 and "schema top-level fields drift" in result.stdout)

        schema_version_case = clone_candidate(parent, "schema-version-drift")
        schema_path = schema_version_case / "references/storyboard.schema.json"
        schema_path.write_text(schema_path.read_text(encoding="utf-8").replace('"version": {"const": "2.0"}', '"version": {"const": "1.0"}', 1), encoding="utf-8")
        result = run_validator(schema_version_case)
        expect("reject storyboard schema version drift", result.returncode == 1 and "storyboard version drifts" in result.stdout)

        schema_range_case = clone_candidate(parent, "schema-fresh-core-range-drift")
        schema_path = schema_range_case / "references/storyboard.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        ink_properties = schema["properties"]["realHandProfile"]["properties"]["inkPhysics"]["properties"]
        ink_properties["freshCoreOpacity"]["minimum"] = 0.7
        schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = run_validator(schema_range_case)
        expect("reject fresh-core schema range drift", result.returncode == 1 and "freshCoreOpacity range drifts" in result.stdout)

        schema_beat_case = clone_candidate(parent, "schema-required-beat-drift")
        schema_path = schema_beat_case / "references/storyboard.schema.json"
        schema_path.write_text(schema_path.read_text(encoding="utf-8").replace('"required": ["id", "label", "copy", "startSecond", "endSecond"]', '"required": ["id", "label", "startSecond", "endSecond"]', 1), encoding="utf-8")
        result = run_validator(schema_beat_case)
        expect("reject schema required beat drift", result.returncode == 1 and "required beat fields drift" in result.stdout)

        schema_hand_case = clone_candidate(parent, "schema-real-hand-drift")
        schema_path = schema_hand_case / "references/storyboard.schema.json"
        schema_path.write_text(schema_path.read_text(encoding="utf-8").replace('"sleeveStyle": {"enum": ["gray-linen", "project-defined"]}', '"sleeveStyle": {"enum": ["gray-linen", "project-defined"]}, "unexpected": {"type": "string"}', 1), encoding="utf-8")
        result = run_validator(schema_hand_case)
        expect("reject real-hand schema drift", result.returncode == 1 and "realHandProfile fields drift" in result.stdout)

        schema_gate_case = clone_candidate(parent, "schema-gate-drift")
        schema_path = schema_gate_case / "references/storyboard.schema.json"
        schema_path.write_text(schema_path.read_text(encoding="utf-8").replace('{"const": 1280}', '{"const": 1920}', 1), encoding="utf-8")
        result = run_validator(schema_gate_case)
        expect("reject schema state/dimension gate drift", result.returncode == 1 and "state and dimension gates drift" in result.stdout)

        schema_hold_case = clone_candidate(parent, "schema-final-hold-drift")
        schema_path = schema_hold_case / "references/storyboard.schema.json"
        schema_path.write_text(schema_path.read_text(encoding="utf-8").replace('"finalHoldFrames": {"type": "integer", "minimum": 33}', '"finalHoldFrames": {"type": "integer", "minimum": 30}', 1), encoding="utf-8")
        result = run_validator(schema_hold_case)
        expect("reject schema final hold below 33 frames", result.returncode == 1 and "final hold minimum" in result.stdout)

        icon_case = clone_candidate(parent, "active-icon")
        icon_path = icon_case / "assets/icon.svg"
        icon_path.write_text(icon_path.read_text(encoding="utf-8").replace("</svg>", "<script>alert(1)</script></svg>"), encoding="utf-8")
        result = run_validator(icon_case)
        expect("reject active content in shipped SVG", result.returncode == 1 and "forbids <script>" in result.stdout)

        def gif_error(name: str, payload: bytes) -> str:
            gif_path = parent / name
            gif_path.write_bytes(payload)
            try:
                gif_metadata(gif_path)
            except ValueError as exc:
                return str(exc)
            return ""

        real_gif = ROOT / "assets/inkbrush-motion-demo.gif"
        expect("fully decode approved animated README demo", gif_metadata(real_gif) == (360, 640, 60, 10_220))
        expect("reject truncated animated README demo", "GIF" in gif_error("truncated.gif", real_gif.read_bytes()[:40]))

        empty_gif = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff"
        frame = b"\x21\xf9\x04\x00\x0a\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00"
        expect("reject empty GIF LZW frame data", "cannot be empty" in gif_error("empty-lzw.gif", empty_gif + frame * 80 + b"\x3b"))

        oversized = bytearray(empty_gif + frame + b"\x3b")
        descriptor = oversized.index(b"\x2c")
        oversized[descriptor + 5:descriptor + 9] = b"\xff\xff\xff\xff"
        expect("reject GIF frame outside logical screen", "frame rectangle" in gif_error("oversized-frame.gif", oversized))

        invalid_code_size = bytearray(empty_gif + frame + b"\x3b")
        image_descriptor = invalid_code_size.index(b"\x2c")
        invalid_code_size[image_descriptor + 10] = 1
        expect("reject invalid GIF LZW code size", "minimum code size" in gif_error("bad-code-size.gif", invalid_code_size))

        valid_one_pixel_data = b"\x02\x02\x44\x01\x00"
        valid_frame = frame[:-2] + valid_one_pixel_data
        expect("reject excessive GIF frame count", "300-frame" in gif_error("excessive-frames.gif", empty_gif + valid_frame * 301 + b"\x3b"))

        hash_case = clone_candidate(parent, "changed-gif-provenance")
        gif_path = hash_case / "assets/inkbrush-motion-demo.gif"
        gif_data = gif_path.read_bytes()
        gif_path.write_bytes(gif_data[:-1] + b"\x21\xfe\x03abc\x00" + gif_data[-1:])
        result = run_validator(hash_case)
        expect("reject changed GIF provenance hash", result.returncode == 1 and "provenance hash" in result.stdout)

        mp4_hash_case = clone_candidate(parent, "changed-12-second-mp4-provenance")
        mp4_path = mp4_hash_case / "assets/inkbrush-ai-agent-12s.mp4"
        mp4_data = bytearray(mp4_path.read_bytes())
        mp4_data[-1] ^= 1
        mp4_path.write_bytes(mp4_data)
        result = run_validator(mp4_hash_case)
        expect("reject changed 12-second MP4 provenance hash", result.returncode == 1 and "12s.mp4 does not match" in result.stdout)

        for label, settings, expected_error in [
            ("dimensions", {"size": "32x32"}, "dimensions must be 1080x1920"),
            ("frame-rate", {"fps": 24}, "frame rate must be 30 fps"),
            ("duration", {"duration": 1.0}, "exactly 360 frames and 12.00 seconds"),
            ("codec", {"codec": "mpeg4"}, "codec must be H.264"),
            ("audio", {"audio": True}, "must not contain audio streams"),
        ]:
            structure_case = clone_candidate(parent, f"changed-12-second-{label}")
            structure_path = structure_case / "assets/inkbrush-ai-agent-12s.mp4"
            write_video_fixture(structure_path, **settings)
            result = run_validator(structure_case)
            expect(f"reject 12-second MP4 {label} drift", result.returncode == 1 and expected_error in result.stdout)

        decode_case = clone_candidate(parent, "truncated-12-second-mp4")
        decode_path = decode_case / "assets/inkbrush-ai-agent-12s.mp4"
        decode_path.write_bytes(decode_path.read_bytes()[: decode_path.stat().st_size // 2])
        result = run_validator(decode_case)
        expect("reject MP4 that does not fully decode", result.returncode == 1 and "cannot be fully decoded" in result.stdout)

        missing_tool_case = clone_candidate(parent, "missing-ffmpeg-tool")
        result = run_validator(missing_tool_case, {"INKBRUSH_FFMPEG": "/definitely/missing/ffmpeg"})
        expect("reject missing pinned FFmpeg tool", result.returncode == 1 and "missing or not executable" in result.stdout)

        contact_hash_case = clone_candidate(parent, "changed-12-second-contact-sheet-provenance")
        contact_path = contact_hash_case / "assets/inkbrush-ai-agent-12s-contact-sheet.png"
        contact_data = bytearray(contact_path.read_bytes())
        contact_data[-1] ^= 1
        contact_path.write_bytes(contact_data)
        result = run_validator(contact_hash_case)
        expect("reject changed 12-second contact-sheet provenance hash", result.returncode == 1 and "contact-sheet" in result.stdout)

        clean_plate_case = clone_candidate(parent, "changed-clean-plate")
        shutil.copyfile(
            clean_plate_case / "assets/ai-agent-knowledge-prestroke.png",
            clean_plate_case / "assets/ai-agent-knowledge-cleanplate.png",
        )
        result = run_validator(clean_plate_case)
        expect("reject changed clean-plate provenance hash", result.returncode == 1 and "cleanplate.png does not match" in result.stdout)

        brush_pose_case = clone_candidate(parent, "changed-brush-pose")
        shutil.copyfile(
            brush_pose_case / "assets/brush-poses-v5/pose-02.png",
            brush_pose_case / "assets/brush-poses-v5/pose-01.png",
        )
        result = run_validator(brush_pose_case)
        expect("reject changed nine-action brush pose", result.returncode == 1 and "pose-01.png does not match" in result.stdout)

        v5_source_case = clone_candidate(parent, "changed-v5-source")
        source_path = v5_source_case / "assets/reference/brush-hand-sheet-v5.png"
        shutil.copyfile(v5_source_case / "assets/reference/real-brush-gray-linen.png", source_path)
        result = run_validator(v5_source_case)
        expect("reject changed v5 photographic source", result.returncode == 1 and "brush-hand-sheet-v5.png does not match" in result.stdout)

        manifest_unknown_case = clone_candidate(parent, "v5-manifest-unknown")
        manifest_path = manifest_unknown_case / "assets/brush-poses-v5/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["unexpected"] = True
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = run_validator(manifest_unknown_case)
        expect("reject unknown v5 manifest field", result.returncode == 1 and "top-level fields drift" in result.stdout)

        manifest_schema_case = clone_candidate(parent, "v5-manifest-schema-drift")
        manifest_path = manifest_schema_case / "assets/brush-poses-v5/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["schemaVersion"] = 1
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = run_validator(manifest_schema_case)
        expect("reject v1 shape after v2 pixel contract", result.returncode == 1 and "schemaVersion must be 2" in result.stdout)

        manifest_algorithm_case = clone_candidate(parent, "v5-manifest-pixel-algorithm-drift")
        manifest_path = manifest_algorithm_case / "assets/brush-poses-v5/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["pixelHashAlgorithm"] = "sha256(rgba8-only)"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = run_validator(manifest_algorithm_case)
        expect("reject v5 pixel hash algorithm drift", result.returncode == 1 and "pixel hash algorithm drift" in result.stdout)

        manifest_nan_case = clone_candidate(parent, "v5-manifest-nan")
        manifest_path = manifest_nan_case / "assets/brush-poses-v5/manifest.json"
        manifest_text = manifest_path.read_text(encoding="utf-8").replace('"hairHeight": 60', '"hairHeight": NaN', 1)
        manifest_path.write_text(manifest_text, encoding="utf-8")
        result = run_validator(manifest_nan_case)
        expect("reject NaN v5 manifest value", result.returncode == 1 and "invalid v5 brush manifest" in result.stdout)

        manifest_duplicate_case = clone_candidate(parent, "v5-manifest-duplicate-action")
        manifest_path = manifest_duplicate_case / "assets/brush-poses-v5/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["actions"][4]["action"] = manifest["actions"][3]["action"]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = run_validator(manifest_duplicate_case)
        expect("reject duplicate v5 action", result.returncode == 1 and "action 05 identity" in result.stdout)

        app_consumer_case = clone_candidate(parent, "v5-app-consumer-drift")
        app_path = app_consumer_case / "app.js"
        app_path.write_text(app_path.read_text(encoding="utf-8").replace("brush-poses-v5", "brush-poses-v4", 1), encoding="utf-8")
        result = run_validator(app_consumer_case)
        expect("reject app consumer drift from v5", result.returncode == 1 and "historical brush sprites" in result.stdout)

        index_consumer_case = clone_candidate(parent, "v5-index-consumer-drift")
        index_path = index_consumer_case / "index.html"
        index_path.write_text(index_path.read_text(encoding="utf-8").replace("brush-poses-v5", "brush-poses-v4", 1), encoding="utf-8")
        result = run_validator(index_consumer_case)
        expect("reject index consumer drift from v5", result.returncode == 1 and "historical brush sprites" in result.stdout)

        renderer_consumer_case = clone_candidate(parent, "v5-renderer-consumer-drift")
        renderer_path = renderer_consumer_case / "scripts/render_readme_gif.py"
        renderer_path.write_text(renderer_path.read_text(encoding="utf-8").replace("brush-poses-v5", "brush-poses-v4", 1), encoding="utf-8")
        result = run_validator(renderer_consumer_case)
        expect("reject README renderer drift from v5", result.returncode == 1 and "historical brush sprites" in result.stdout)

        historical_brush_case = clone_candidate(parent, "changed-historical-brush-pose")
        shutil.copyfile(
            historical_brush_case / "assets/brush-poses-v2/pose-02.png",
            historical_brush_case / "assets/brush-poses-v2/pose-01.png",
        )
        result = run_validator(historical_brush_case)
        expect("reject changed historical brush pose", result.returncode == 1 and "disclosed historical provenance hash" in result.stdout)

        final_brush_case = clone_candidate(parent, "changed-final-brush")
        shutil.copyfile(
            final_brush_case / "assets/brush-poses-v5/pose-08.png",
            final_brush_case / "assets/brush-pose-final.png",
        )
        result = run_validator(final_brush_case)
        expect("reject static board bound to the wrong final pose", result.returncode == 1 and "byte-identical" in result.stdout)

        record_case = clone_candidate(parent, "misbound-gif-record")
        record_path = record_case / "references/readme-animation-record.md"
        record_text = record_path.read_text(encoding="utf-8")
        record_text = record_text.replace(
            "`5a4a50381f3f21f5431affbd913cefd78813e9a216f9187302bbc37a9ba11a6f` |",
            f"`{'0' * 64}` |",
            1,
        )
        record_text += "\n<!-- 5a4a50381f3f21f5431affbd913cefd78813e9a216f9187302bbc37a9ba11a6f -->\n"
        record_path.write_text(record_text, encoding="utf-8")
        result = run_validator(record_case)
        expect("reject GIF hash hidden outside provenance table row", result.returncode == 1 and "exact approved GIF table row" in result.stdout)

        gif_comment_case = clone_candidate(parent, "comment-hidden-gif-row")
        gif_comment_path = gif_comment_case / "references/readme-animation-record.md"
        gif_comment_text = gif_comment_path.read_text(encoding="utf-8")
        gif_row = next(line for line in gif_comment_text.splitlines() if line.startswith("| `assets/inkbrush-motion-demo.gif` |"))
        gif_comment_path.write_text(gif_comment_text.replace(gif_row, f"<!--\n{gif_row}\n-->", 1), encoding="utf-8")
        result = run_validator(gif_comment_case)
        expect("reject GIF provenance row hidden in multiline HTML comment", result.returncode == 1 and "forbids HTML comments" in result.stdout)

        gif_path = parent / "oversized-file.gif"
        with gif_path.open("wb") as handle:
            handle.seek(16 * 1024 * 1024)
            handle.write(b"x")
        try:
            gif_metadata(gif_path)
            oversized_error = ""
        except ValueError as exc:
            oversized_error = str(exc)
        expect("reject oversized GIF before parsing", "16 MiB" in oversized_error)

        manifest_case = clone_candidate(parent, "missing-manifest")
        for relative in [".nojekyll", ".github/workflows/validate.yml", "requirements-dev.txt", "motion-timing.js", "scripts/test_validate_storyboard.py", "scripts/test_build_calligraphy_brush_v5.py", "scripts/render_12s_example.py", "assets/ai-agent-knowledge-journey.png", "assets/ai-agent-knowledge-prestroke.png", "assets/ai-agent-knowledge-cleanplate.png", "assets/brush-pose-final.png", "assets/brush-poses-v2/pose-09.png", "assets/brush-poses-v5/pose-09.png", "assets/brush-poses-v5/manifest.json", "assets/reference/real-brush-gray-linen.png", "assets/reference/brush-hand-sheet-v5.png", "assets/nine-action-proof.png", "assets/evidence/middle.png", "assets/evidence/hero-middle.png", "assets/inkbrush-motion-demo.gif", "assets/inkbrush-ai-agent-12s.mp4", "assets/inkbrush-ai-agent-12s-contact-sheet.png", "references/real-brush-contract.md", "references/image-generation-record.md", "references/readme-animation-record.md"]:
            (manifest_case / relative).unlink()
        result = run_validator(manifest_case)
        expect("reject missing CI/Pages/test/art/provenance manifest", result.returncode == 1 and result.stdout.count("missing required file") >= 15)

        print("PASS: all public-package negative tests")


if __name__ == "__main__":
    main()
