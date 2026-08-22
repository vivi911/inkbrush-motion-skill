# Animated README demo record

This record identifies the animated preview shown at the top of `README.md`. It is a deterministic proof render of the repository's 9:16 delivery demo, using the same background, nine brush poses, route, timing, and exact English knowledge copy as the zero-dependency web animation.

## Source identity

- Source page: local build of `index.html?preview=once` from the release candidate.
- Source code identity: `index.html` SHA-256 `0e8b475da0708e7c136791dc461ffc7844e1d4745a12884e95f929af261b740a`; `styles.css` SHA-256 `efdcff1009fde42b6670791333082ad808434e2c11a4b99ab308455aa9e668d7`; `motion-timing.js` SHA-256 `b2db8b094527aaacdc3febf9f004b2ffc23f3b72ff3f8462f1e76f6b441cc6aa`; `app.js` SHA-256 `71804469abd11aa52b45e7b8cc391b426b1f63f7f09ca2ee97ffb3fa6f32d1cf`; `scripts/motion_timing.py` SHA-256 `6417a4b90b29dff1ab584e6c0930fde04a93a0472526a9451f9d915541154700`; `scripts/render_readme_gif.py` SHA-256 `91d94c2a0b38547a6326da2a7f7a22ab40f0cdd250b68cb2dbae030f7a89b5bd`.
- Rendered composition: the `.journey-frame` contract at native 720×1280, reduced to 360×640 for GitHub README playback.
- Required text: code-native English text from `assets/demo-plan.json`; no generated text is used.
- Image sources: disclosed `assets/ai-agent-knowledge-cleanplate.png` and the nine photographic-looking `assets/brush-poses-v5/pose-*.png` sprites; their exact source, manifest, builder, and output hashes are in [`image-generation-record.md`](image-generation-record.md).

## Render and conversion

- Render date: 2026-08-22.
- Renderer: `scripts/render_readme_gif.py` with Pillow 11.3.0; 73 ordered timeline samples at approximately 7 fps, stored as 60 GIF frames after identical holds were duration-folded. Each frame uses its own 256-color palette without dithering to preserve the hand and paper while staying below the 16 MiB README limit.
- Opening proof: the shared machine-readable timing contract calculates web first ink at 0.506 seconds, GIF first ink at 0.56 seconds, hover / touch / press at 1.334 / 1.40 seconds, and Context at 2.419 / 2.38 seconds.
- Brush and ink behavior: each active v5 sprite preserves a complete photographic-looking ferrule and wet tuft from the disclosed source sheet; PRESS applies the recorded raster-only compression. The moving fresh dark core is capped at 6 native pixels behind the tip; wet fringe diffuses after 5 frames; the trail stays on the paper and dries after 12 frames into a pale, irregular fibre mark. No fixed wet circle follows the hand.
- Final hold: timeline samples 064–072 are motionless for 1.26 seconds, with the pointed LEAVE bristles held 12 canvas pixels above the completed ink tail and no anchor jump.
- Runtime boundary: Pillow and the macOS fonts are maintainer-only render tools. The published web demo still has zero runtime dependencies.

```bash
python3 scripts/render_readme_gif.py
```

## Published output identity

| Asset | Dimensions | Frames | Duration | SHA-256 |
|---|---:|---:|---:|---|
| `assets/inkbrush-motion-demo.gif` | 360×640 | 60 | 10.22 seconds | `a3160d3d094dc5473fe73c13d67e067300c5d08641946045424524f9f7ad7929` |

The GIF contains the same disclosed AI-assisted background and brush sprites as the live delivery demo. It adds no font files, network runtime, or third-party source code.
