# Animated README demo record

This record identifies the animated preview shown at the top of `README.md`. The GIF is a direct capture of the repository's delivery demo, not a separately designed concept image.

## Source identity

- Source repository commit: `d795bf817dcad6359f3428a53f4d43a223e15495`.
- Source page: local build of `index.html?preview=once` from that commit.
- Captured element: `.journey-frame`.
- Browser viewport: 390×800.
- Required text: code-native HTML text from `assets/demo-plan.json`.
- Image source: disclosed `assets/ai-agent-knowledge-prestroke.png`.

## Capture and conversion

- Capture date: 2026-08-21.
- Browser capture: headed Chromium driven by Playwright; 103 ordered PNG frames.
- Frame rate: 10 fps.
- Final hold: included in the 10.3-second sequence.
- Conversion: FFmpeg 7.1 palette generation and palette application; infinite GIF loop.

```bash
ffmpeg -framerate 10 \
  -i output/playwright/readme-gif/frames/frame-%03d.png \
  -filter_complex "[0:v]split[a][b];[a]palettegen=max_colors=192:stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
  -loop 0 assets/inkbrush-motion-demo.gif
```

The local FFmpeg build reported GPL v2 or later because GPL components were enabled. FFmpeg and Playwright were capture tools only; they are not included in the public package and are not runtime dependencies.

## Published output identity

| Asset | Dimensions | Frames | Duration | SHA-256 |
|---|---:|---:|---:|---|
| `assets/inkbrush-motion-demo.gif` | 292×519 | 103 | 10.3 seconds | `282149ab0beae16c291f7a08fbcce0b2ae57d2e8e6ba01509ff438ca75f153a7` |

The GIF contains the same AI-assisted background and human-directed code composition disclosed in `COPYRIGHT.md`; it adds no new generated imagery, font files, or third-party source code.
