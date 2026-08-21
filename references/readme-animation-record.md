# Animated README demo record

This record identifies the animated preview shown at the top of `README.md`. It is a deterministic proof render of the repository's 9:16 delivery demo, using the same background, nine brush poses, route, timing, and exact English knowledge copy as the zero-dependency web animation.

## Source identity

- Source page: local build of `index.html?preview=once` from the release candidate.
- Source code identity: `index.html` SHA-256 `1a1ce030606fe4202690d5456555e5709ed4a5434cff15deecf87e1d083f2512`; `styles.css` SHA-256 `b1eb0c1a21338bacc65e596d92598f6eca0a24af4d5f237f006ae57b62ac9a54`; `motion-timing.js` SHA-256 `f94ca2241f70ea2136c69a959f4b6d445f0b8e45c556e867f7cc37aaf3937e67`; `app.js` SHA-256 `a825eb56fbd811caded2eb0f7bc46dab1232a0ccf356c2719e14fb80a1b49ff0`; `scripts/motion_timing.py` SHA-256 `66875a9090f0c787fb2af4bb0ced7f04d984db066f5466e098d4e2fb786ea5a8`; `scripts/render_readme_gif.py` SHA-256 `46ce6f7ec083881867304e9ace8e45e2b5fab2e52b0746f56dff6a2327fbae03`.
- Rendered composition: the `.journey-frame` contract at native 720×1280, reduced to 360×640 for GitHub README playback.
- Required text: code-native English text from `assets/demo-plan.json`; no generated text is used.
- Image sources: disclosed `assets/ai-agent-knowledge-cleanplate.png` and the nine `assets/brush-poses-v3/pose-*.png` sprites; their exact hashes are in [`image-generation-record.md`](image-generation-record.md).

## Render and conversion

- Render date: 2026-08-22.
- Renderer: `scripts/render_readme_gif.py` with Pillow 11.3.0; 73 ordered timeline samples at approximately 7 fps, stored as 60 GIF frames after identical holds were duration-folded. Each frame uses its own 256-color palette without dithering to preserve the hand and paper while staying below the 16 MiB README limit.
- Opening proof: the shared machine-readable timing contract calculates web first ink at 0.506 seconds, GIF first ink at 0.56 seconds, hover / touch / press at 1.334 / 1.40 seconds, and Context at 2.419 / 2.38 seconds.
- Ink behavior: fresh dark core stays behind the tip; wet fringe diffuses after 5 frames; the trail dries after 12 frames into a pale, irregular fibre mark.
- Final hold: timeline samples 064–072 are motionless for 1.26 seconds, with the LEAVE pose lifted 42 canvas pixels above the completed ink tail.
- Runtime boundary: Pillow and the macOS fonts are maintainer-only render tools. The published web demo still has zero runtime dependencies.

```bash
python3 scripts/render_readme_gif.py
```

## Published output identity

| Asset | Dimensions | Frames | Duration | SHA-256 |
|---|---:|---:|---:|---|
| `assets/inkbrush-motion-demo.gif` | 360×640 | 60 | 10.22 seconds | `134f5de0ea0b0912ccb446143f309dd815e33a5825ab81790e1ede86738080db` |

The GIF contains the same disclosed AI-assisted background and brush sprites as the live delivery demo. It adds no font files, network runtime, or third-party source code.
