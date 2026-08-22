# Animated README demo record

This record identifies the animated preview shown at the top of `README.md`. It is a deterministic proof render of the repository's 9:16 delivery demo, using the same background, nine brush poses, route, timing, and exact English knowledge copy as the zero-dependency web animation.

## Source identity

- Source page: local build of `index.html?preview=once` from the release candidate.
- Source code identity: `index.html` SHA-256 `ef92e770080ea40036143cb59313c5d8fcfb6c763cadc7f60ff4f84f615c3cfe`; `styles.css` SHA-256 `b1eb0c1a21338bacc65e596d92598f6eca0a24af4d5f237f006ae57b62ac9a54`; `motion-timing.js` SHA-256 `b2db8b094527aaacdc3febf9f004b2ffc23f3b72ff3f8462f1e76f6b441cc6aa`; `app.js` SHA-256 `05c73dc6368abf66b31bb4083fa9a8a87b755da93325122d1e89595d7fc3b7ae`; `scripts/motion_timing.py` SHA-256 `6417a4b90b29dff1ab584e6c0930fde04a93a0472526a9451f9d915541154700`; `scripts/render_readme_gif.py` SHA-256 `185604e7b51af31a00a5e20a6e29cf5e8bee33c8a638c73de9029582a57ea4a8`.
- Rendered composition: the `.journey-frame` contract at native 720×1280, reduced to 360×640 for GitHub README playback.
- Required text: code-native English text from `assets/demo-plan.json`; no generated text is used.
- Image sources: disclosed `assets/ai-agent-knowledge-cleanplate.png` and the nine compact-bristle `assets/brush-poses-v4/pose-*.png` sprites; their exact hashes are in [`image-generation-record.md`](image-generation-record.md).

## Render and conversion

- Render date: 2026-08-22.
- Renderer: `scripts/render_readme_gif.py` with Pillow 11.3.0; 73 ordered timeline samples at approximately 7 fps, stored as 60 GIF frames after identical holds were duration-folded. Each frame uses its own 256-color palette without dithering to preserve the hand and paper while staying below the 16 MiB README limit.
- Opening proof: the shared machine-readable timing contract calculates web first ink at 0.506 seconds, GIF first ink at 0.56 seconds, hover / touch / press at 1.334 / 1.40 seconds, and Context at 2.419 / 2.38 seconds.
- Brush and ink behavior: each active v4 sprite uses the deterministic soft-hair reconstruction recorded in `image-generation-record.md`; the moving fresh dark core is capped at 6 native pixels behind the tip; wet fringe diffuses after 5 frames; the trail stays on the paper and dries after 12 frames into a pale, irregular fibre mark.
- Final hold: timeline samples 064–072 are motionless for 1.26 seconds, with the LEAVE pose lifted 42 canvas pixels above the completed ink tail.
- Runtime boundary: Pillow and the macOS fonts are maintainer-only render tools. The published web demo still has zero runtime dependencies.

```bash
python3 scripts/render_readme_gif.py
```

## Published output identity

| Asset | Dimensions | Frames | Duration | SHA-256 |
|---|---:|---:|---:|---|
| `assets/inkbrush-motion-demo.gif` | 360×640 | 60 | 10.22 seconds | `8b9166cbac1522ffab69a1c0494b1124ce1a4ce8351fbf15c91c8952d6f123e9` |

The GIF contains the same disclosed AI-assisted background and brush sprites as the live delivery demo. It adds no font files, network runtime, or third-party source code.
