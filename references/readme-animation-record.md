# Animated README demo record

This record identifies the animated preview shown at the top of `README.md`. The GIF is a direct capture of the repository's delivery demo, not a separately designed concept image.

## Source identity

- Source page: local build of `index.html?preview=once` from the release candidate.
- Source code identity: `index.html` SHA-256 `a70ed1a398a017c518730061193ea10eb0c80b60922c563d9dee92ee04d833e5`; `styles.css` SHA-256 `3d4cd52a499ae9c48311a98bc363422fad7264db96a7cc5388069fc33c061252`; `app.js` SHA-256 `66fa06127bfa951739364c8fa4552932eae628bb305a1320b30bee206b4d42cd`.
- Captured element: `.journey-frame`.
- Browser viewport: 390×800.
- Required text: code-native HTML text from `assets/demo-plan.json`.
- Image sources: disclosed `assets/ai-agent-knowledge-cleanplate.png` and the nine `assets/brush-poses-v2/pose-*.png` sprites; their exact hashes are in [`image-generation-record.md`](image-generation-record.md).

## Capture and conversion

- Capture date: 2026-08-21.
- Browser capture: headed Chrome; 103 ordered PNG frames, all 292×519.
- Frame rate: 10 fps.
- Final hold: the final 1.1 seconds are motionless; frames 092–102 share one content hash.
- Conversion: FFmpeg 7.1 palette generation and palette application; infinite GIF loop.

```bash
ffmpeg -framerate 10 \
  -i output/playwright/readme-gif-v2/frames/frame-%03d.png \
  -filter_complex "[0:v]split[a][b];[a]palettegen=max_colors=192:stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
  -loop 0 assets/inkbrush-motion-demo.gif
```

The local FFmpeg build reported GPL v2 or later because GPL components were enabled. FFmpeg and Playwright were capture tools only; they are not included in the public package and are not runtime dependencies.

## Published output identity

| Asset | Dimensions | Frames | Duration | SHA-256 |
|---|---:|---:|---:|---|
| `assets/inkbrush-motion-demo.gif` | 292×519 | 103 | 10.3 seconds | `996fca6cb98cbaa94bb8bb65d85cccb5b4b964e57276856f2f1abc2a90838194` |

The GIF contains the same AI-assisted background and human-directed code composition disclosed in `COPYRIGHT.md`; it adds no new generated imagery, font files, or third-party source code.
