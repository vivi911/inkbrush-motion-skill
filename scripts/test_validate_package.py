#!/usr/bin/env python3
"""Prove that public-package checks fail closed for external runtime and schema drift."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


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

        manifest_case = clone_candidate(parent, "missing-manifest")
        for relative in [".nojekyll", ".github/workflows/validate.yml", "scripts/test_validate_storyboard.py"]:
            (manifest_case / relative).unlink()
        result = run_validator(manifest_case)
        expect("reject missing CI/Pages/test manifest", result.returncode == 1 and result.stdout.count("missing required file") >= 3)

        print("PASS: all public-package negative tests")


if __name__ == "__main__":
    main()
