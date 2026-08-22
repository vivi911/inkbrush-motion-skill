#!/usr/bin/env python3
"""Prove that public-package checks fail closed for external runtime and schema drift."""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from artifact_checks import gif_metadata
from motion_timing import PREFIX, load_motion_timing


ROOT = Path(__file__).resolve().parents[1]


def run_validator(candidate: Path) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
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
        approved_app_hash = "05c73dc6368abf66b31bb4083fa9a8a87b755da93325122d1e89595d7fc3b7ae"
        source_record_text = source_record_path.read_text(encoding="utf-8").replace(
            f"`app.js` SHA-256 `{approved_app_hash}`",
            f"`app.js` SHA-256 `{'0' * 64}`",
            1,
        )
        source_record_text += f"\n<!-- `app.js` SHA-256 `{approved_app_hash}` -->\n"
        source_record_path.write_text(source_record_text, encoding="utf-8")
        result = run_validator(source_record_case)
        expect("reject capture-source hash hidden outside its provenance field", result.returncode == 1 and "exact capture source identity line" in result.stdout)

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

        clean_plate_case = clone_candidate(parent, "changed-clean-plate")
        shutil.copyfile(
            clean_plate_case / "assets/ai-agent-knowledge-prestroke.png",
            clean_plate_case / "assets/ai-agent-knowledge-cleanplate.png",
        )
        result = run_validator(clean_plate_case)
        expect("reject changed clean-plate provenance hash", result.returncode == 1 and "cleanplate.png does not match" in result.stdout)

        brush_pose_case = clone_candidate(parent, "changed-brush-pose")
        shutil.copyfile(
            brush_pose_case / "assets/brush-poses-v4/pose-02.png",
            brush_pose_case / "assets/brush-poses-v4/pose-01.png",
        )
        result = run_validator(brush_pose_case)
        expect("reject changed nine-action brush pose", result.returncode == 1 and "pose-01.png does not match" in result.stdout)

        historical_brush_case = clone_candidate(parent, "changed-historical-brush-pose")
        shutil.copyfile(
            historical_brush_case / "assets/brush-poses-v2/pose-02.png",
            historical_brush_case / "assets/brush-poses-v2/pose-01.png",
        )
        result = run_validator(historical_brush_case)
        expect("reject changed historical brush pose", result.returncode == 1 and "disclosed historical provenance hash" in result.stdout)

        final_brush_case = clone_candidate(parent, "changed-final-brush")
        shutil.copyfile(
            final_brush_case / "assets/brush-poses-v4/pose-08.png",
            final_brush_case / "assets/brush-pose-final.png",
        )
        result = run_validator(final_brush_case)
        expect("reject static board bound to the wrong final pose", result.returncode == 1 and "byte-identical" in result.stdout)

        record_case = clone_candidate(parent, "misbound-gif-record")
        record_path = record_case / "references/readme-animation-record.md"
        record_text = record_path.read_text(encoding="utf-8")
        record_text = record_text.replace(
            "`8b9166cbac1522ffab69a1c0494b1124ce1a4ce8351fbf15c91c8952d6f123e9` |",
            f"`{'0' * 64}` |",
            1,
        )
        record_text += "\n<!-- 8b9166cbac1522ffab69a1c0494b1124ce1a4ce8351fbf15c91c8952d6f123e9 -->\n"
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
        for relative in [".nojekyll", ".github/workflows/validate.yml", "motion-timing.js", "scripts/test_validate_storyboard.py", "assets/ai-agent-knowledge-journey.png", "assets/ai-agent-knowledge-prestroke.png", "assets/ai-agent-knowledge-cleanplate.png", "assets/brush-pose-final.png", "assets/brush-poses-v2/pose-09.png", "assets/brush-poses-v4/pose-09.png", "assets/reference/real-brush-gray-linen.png", "assets/nine-action-proof.png", "assets/evidence/middle.png", "assets/evidence/hero-middle.png", "assets/inkbrush-motion-demo.gif", "references/real-brush-contract.md", "references/image-generation-record.md", "references/readme-animation-record.md"]:
            (manifest_case / relative).unlink()
        result = run_validator(manifest_case)
        expect("reject missing CI/Pages/test/art/provenance manifest", result.returncode == 1 and result.stdout.count("missing required file") >= 15)

        print("PASS: all public-package negative tests")


if __name__ == "__main__":
    main()
