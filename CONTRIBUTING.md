# Contributing

Thanks for helping build a calmer visual language for knowledge.

## Before opening a pull request

1. Keep the static-first approval gate intact.
2. Record the source and license of every added dependency, font, dataset, or visual asset.
3. Keep exact text code-native and keep the brush ahead of the ink.
4. Run all four validation commands from `README.md`.
5. Include a screenshot or three-frame evidence packet for visual changes.

Good first contributions include code-authored paper textures, verified renderer adapters, accessibility improvements, new negative tests, and documentation translations.

By submitting a contribution, you agree that it may be distributed under this repository's MIT License.

The website has no runtime dependencies. Maintainers who intentionally regenerate `assets/social-preview.png`, the README GIF, or the v5 brush sprites need Pillow 11.3.0 and lawful access to any fonts named in `COPYRIGHT.md`; Pillow and font files are not vendored here.

Rebuild and verify the disclosed v5 brush sprites with:

```bash
python3 scripts/build_calligraphy_brush_v5.py
python3 scripts/test_build_calligraphy_brush_v5.py
```
