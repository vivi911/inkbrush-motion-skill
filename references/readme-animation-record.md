# Animated README demo record

This record identifies the animated preview shown at the top of `README.md`. It is a deterministic proof render of the repository's 9:16 delivery demo, using the same background, nine brush poses, route, timing, and exact English knowledge copy as the zero-dependency web animation.

## Source identity

- Source page: local build of `index.html?preview=once` from the release candidate.
- Source code identity: `index.html` SHA-256 `788a97feb32bedeadf5c52192242edc8aa458e50bc7c1ce6887f6f1e1d394e74`; `styles.css` SHA-256 `16ebbcae1feb1e8c27183177f4c0526654ffa8d4a983f85a8b69a7de503f0dda`; `motion-timing.js` SHA-256 `44ee0405a0bfd9d3c01b29f1fee4cc1d1ac387c1b3169af38ac3c17b24ba8389`; `app.js` SHA-256 `d759f5657437eee95ced784ac72ba365bce7d5406d17ac4a49531cd6c5fc3471`; `scripts/motion_timing.py` SHA-256 `708fb3198e6a01ceb529efdf21a333d7f2f2da5ccf5f8aeb5549db1eb32c4414`; `scripts/render_readme_gif.py` SHA-256 `5a20b0d23a8454c02172334acdc3ca13a9950815d205300ca240605ebfa1dad1`.
- Rendered composition: the `.journey-frame` contract at native 720×1280, reduced to 360×640 for GitHub README playback.
- Required text: code-native English text from `assets/demo-plan.json`; no generated text is used.
- Image sources: disclosed `assets/ai-agent-knowledge-cleanplate.png` and the nine photographic-looking `assets/brush-poses-v5/pose-*.png` sprites; their exact source, manifest, builder, and output hashes are in [`image-generation-record.md`](image-generation-record.md).

## Render and conversion

- Render date: 2026-08-23.
- Renderer: `scripts/render_readme_gif.py` with Pillow 11.3.0; 73 ordered timeline samples at approximately 7 fps, stored as 60 GIF frames after identical holds were duration-folded. Each frame uses its own 256-color palette without dithering to preserve the hand and paper while staying below the 16 MiB README limit.
- Opening proof: the shared machine-readable timing contract calculates web first ink at 0.506 seconds, GIF first ink at 0.56 seconds, hover / touch / press at 1.334 / 1.40 seconds, and Context at 2.419 / 2.38 seconds.
- Brush and ink behavior: each active v5 sprite preserves a complete photographic-looking ferrule and wet tuft from the disclosed source sheet; PRESS applies the recorded raster-only compression. The moving fresh core is a short warm ink black (`#2b2722`, 92% opacity) capped at 6 native pixels behind the tip; the muted wet fringe (`#50554d`, 22% opacity) diffuses after 5 frames; the unchanged older trail stays on the paper and dries after 12 frames into a pale, irregular fibre mark. No fixed wet circle follows the hand, and the full route is never darkened to compensate for the contact point.
- Final hold: timeline samples 064–072 are motionless for 1.26 seconds, with the pointed LEAVE bristles held 12 canvas pixels above the completed ink tail and no anchor jump.
- Runtime boundary: Pillow and the macOS fonts are maintainer-only render tools. The published web demo still has zero runtime dependencies.

```bash
python3 scripts/render_readme_gif.py
```

## Published output identity

| Asset | Dimensions | Frames | Duration | SHA-256 |
|---|---:|---:|---:|---|
| `assets/inkbrush-motion-demo.gif` | 360×640 | 60 | 10.22 seconds | `5a4a50381f3f21f5431affbd913cefd78813e9a216f9187302bbc37a9ba11a6f` |

The GIF contains the same disclosed AI-assisted background and brush sprites as the live delivery demo. It adds no font files, network runtime, or third-party source code.

## 12-second MP4 example

- Render date: 2026-08-23.
- Renderer identity: `scripts/render_12s_example.py` SHA-256 `4be3989f9a48a408cd3dc3995772a8335286b345da8a7c59d0b7767075a3beb3`.
- Tool identity: Pillow 11.3.0 and imageio-ffmpeg 0.6.0; the approved macOS arm64 executable reports FFmpeg 7.1, `--enable-gpl --enable-libx264`, and SHA-256 `6d175a4743ca50256e89a8cdd731100f9cee33bd79aeea46894d209410dc6617`. CI installs the same pinned package versions and requires FFmpeg 7.1 before validation. Source and license boundaries are in [`copyright-and-provenance.md`](copyright-and-provenance.md).
- Render recipe: Pillow 11.3.0 supplies the same 720×1280 source frames as the approved GIF renderer; frames are resized to 1080×1920 and piped to the pinned FFmpeg 7.1/libx264 tool at 30 fps, CRF 18, `yuv420p`, with no audio. The active lesson completes at 9.2 seconds and holds motionless through 12.0 seconds.
- Review times: 0.2 seconds (poise), 5.2 seconds (paint), and 11.5 seconds (resolve). The published contact sheet is generated from those exact composition times.
- Runtime boundary: the MP4 and contact sheet are static published assets. Pillow, imageio-ffmpeg, FFmpeg, libx264, and the macOS system fonts are maintainer-only build tools and are not vendored or loaded at runtime.

```bash
python3 scripts/render_12s_example.py
```

| Asset | Dimensions | Frames | Duration | SHA-256 |
|---|---:|---:|---:|---|
| `assets/inkbrush-ai-agent-12s.mp4` | 1080×1920 | 360 | 12.00 seconds | `a161f7ad71fec300cfa0bd097b234940ce2009d067437a3deb2af886844b9cfb` |
| `assets/inkbrush-ai-agent-12s-contact-sheet.png` | 1184×764 | 3 review times | static | `0da3df925f53b5c72d455ec6cd087fb7d53b7b7a1a99d01770586292fdcfe3cf` |
