#!/usr/bin/env python3
"""Prove that public-package checks fail closed for external runtime and schema drift."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from artifact_checks import gif_metadata


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


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="inkbrush-package-tests-") as temp:
        parent = Path(temp)
        baseline = clone_candidate(parent, "baseline")
        expect("baseline public package passes", run_validator(baseline).returncode == 0)

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

        schema_gate_case = clone_candidate(parent, "schema-gate-drift")
        schema_path = schema_gate_case / "references/storyboard.schema.json"
        schema_path.write_text(schema_path.read_text(encoding="utf-8").replace('{"const": 1280}', '{"const": 1920}', 1), encoding="utf-8")
        result = run_validator(schema_gate_case)
        expect("reject schema state/dimension gate drift", result.returncode == 1 and "state and dimension gates drift" in result.stdout)

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
        expect("fully decode approved animated README demo", gif_metadata(real_gif) == (292, 519, 103, 10_300))
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

        record_case = clone_candidate(parent, "misbound-gif-record")
        record_path = record_case / "references/readme-animation-record.md"
        record_text = record_path.read_text(encoding="utf-8")
        record_text = record_text.replace(
            "`282149ab0beae16c291f7a08fbcce0b2ae57d2e8e6ba01509ff438ca75f153a7` |",
            f"`{'0' * 64}` |",
            1,
        )
        record_text += "\n<!-- 282149ab0beae16c291f7a08fbcce0b2ae57d2e8e6ba01509ff438ca75f153a7 -->\n"
        record_path.write_text(record_text, encoding="utf-8")
        result = run_validator(record_case)
        expect("reject GIF hash hidden outside provenance table row", result.returncode == 1 and "exact approved GIF table row" in result.stdout)

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
        for relative in [".nojekyll", ".github/workflows/validate.yml", "scripts/test_validate_storyboard.py", "assets/ai-agent-knowledge-journey.png", "assets/ai-agent-knowledge-prestroke.png", "assets/inkbrush-motion-demo.gif", "references/image-generation-record.md", "references/readme-animation-record.md"]:
            (manifest_case / relative).unlink()
        result = run_validator(manifest_case)
        expect("reject missing CI/Pages/test/art/provenance manifest", result.returncode == 1 and result.stdout.count("missing required file") >= 8)

        print("PASS: all public-package negative tests")


if __name__ == "__main__":
    main()
