# Animated README demo record

This record identifies the animated preview shown at the top of `README.md`. It is a deterministic proof render of the repository's 9:16 delivery demo, using the same background, nine brush poses, route, timing, and exact English knowledge copy as the zero-dependency web animation.

## Source identity

- Source page: local build of `index.html?preview=once` from the release candidate.
- Source code identity: `index.html` SHA-256 `39ce27ddd8dfda291dbca376d0a0bcdca1b47d7e4ae999f11547454c3ec2666b`; `styles.css` SHA-256 `b1eb0c1a21338bacc65e596d92598f6eca0a24af4d5f237f006ae57b62ac9a54`; `app.js` SHA-256 `08b8f4d6bc04eed2824fdafe1e4ab014c58f3e2e071ab6811f5b0373317dd930`; `scripts/render_readme_gif.py` SHA-256 `e8b80773e601cae7a822b5dfcc729091456f271bce0909d84cc889966e574819`.
- Rendered composition: the `.journey-frame` contract at native 720×1280, reduced to 292×519 for GitHub README playback.
- Required text: code-native English text from `assets/demo-plan.json`; no generated text is used.
- Image sources: disclosed `assets/ai-agent-knowledge-cleanplate.png` and the nine `assets/brush-poses-v3/pose-*.png` sprites; their exact hashes are in [`image-generation-record.md`](image-generation-record.md).

## Render and conversion

- Render date: 2026-08-21.
- Renderer: `scripts/render_readme_gif.py` with Pillow 11.3.0; 103 ordered timeline samples at 10 fps, stored as 83 GIF frames after identical holds were duration-folded.
- Ink behavior: fresh dark core stays behind the tip; wet fringe diffuses after 5 frames; the trail dries after 12 frames into a pale, irregular fibre mark.
- Final hold: frames 092–102 are motionless, with the LEAVE pose lifted 42 canvas pixels above the completed ink tail.
- Runtime boundary: Pillow and the macOS fonts are maintainer-only render tools. The published web demo still has zero runtime dependencies.

```bash
python3 scripts/render_readme_gif.py
```

## Published output identity

| Asset | Dimensions | Frames | Duration | SHA-256 |
|---|---:|---:|---:|---|
| `assets/inkbrush-motion-demo.gif` | 292×519 | 83 | 10.3 seconds | `61f71b7c6185b76b67540956d79447f96e17dcd79727cc80c7b86dee933a48c5` |

The GIF contains the same disclosed AI-assisted background and brush sprites as the live delivery demo. It adds no font files, network runtime, or third-party source code.
