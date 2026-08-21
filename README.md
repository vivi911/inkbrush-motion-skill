<div align="center">
  <a href="https://vivi911.github.io/inkbrush-motion-skill/">
    <img src="assets/inkbrush-motion-demo.gif" alt="Animated Chinese ink-wash lesson showing Context, Action, and Evidence" width="292">
  </a>
  <h1>InkBrush Motion</h1>
  <p><strong>An open-source AI Skill for calm, brush-led 9:16 knowledge animation.</strong></p>
  <p><em>The animation above is the actual zero-dependency delivery demo. Click it for the full-size replay.</em></p>
  <p>
    <a href="https://vivi911.github.io/inkbrush-motion-skill/">Live demo</a> ·
    <a href="SKILL.md">Use the Skill</a> ·
    <a href="README.zh-TW.md">繁體中文</a>
  </p>
  <p>
    <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-7c2f2f">
    <img alt="No runtime dependencies" src="https://img.shields.io/badge/runtime-0%20dependencies-27352f">
    <img alt="Native 9:16" src="https://img.shields.io/badge/canvas-9%3A16-c6a15b">
  </p>
</div>

Most AI explainers look like AI: neon gradients, floating cards, synthetic particles, and generic motion. InkBrush Motion takes the opposite direction. The live demo teaches one reliable AI-agent loop—**Context → Action → Evidence**—as a calligraphy brush completes a Chinese ink-wash journey. Give AI the right context, ask for one clear next step, and check the result before you trust it. Exact knowledge text stays code-native while the AI-assisted scene carries the feeling.

The repository includes both the reusable Skill and a zero-dependency SVG/CSS/JavaScript delivery demo. The README preview is a direct capture of that same live animation, not a separate concept still.

## What you get

| Deliverable | What it proves |
|---|---|
| Native 9:16 static board | The composition works before motion hides layout problems |
| 6–10 second motion proof | The brush leads the active stroke; ink never appears ahead of it |
| Start / middle / end evidence | Reviewers can inspect causality, diffusion, exact text, and final hold |
| Rights packet | Sources, licenses, and authorship boundaries stay explicit |

## Try the delivery demo

```bash
git clone https://github.com/vivi911/inkbrush-motion-skill.git
cd inkbrush-motion-skill
python3 -m http.server 8000
```

Open `http://localhost:8000` and select **Replay the brush**. No npm install, canvas library, image model, or external font is required.

## Use it as an AI Skill

Clone the repository into your Codex skills directory:

```bash
git clone https://github.com/vivi911/inkbrush-motion-skill.git \
  ~/.codex/skills/inkbrush-motion-skill
```

Then ask:

```text
Use $inkbrush-motion-skill to turn this AI knowledge into a static-first
9:16 Chinese ink-wash motion package: [paste your approved copy]
```

You can also point another coding agent directly at `SKILL.md`. Do not assume compatibility with a product-specific skill loader unless that product documents it.

## Design contract

- Warm xuan paper, near-black ink, gray wash, and one restrained vermilion seal.
- Native portrait composition—never a mechanical crop of a landscape board.
- Code-native text for exact glyphs and wording.
- Brush-tip tracking, pressure variation, delayed local diffusion, and a final hold.
- No neon, circuitry, holograms, glossy UI cards, or fake handwriting wipes.
- Human visual approval before motion.

See [`references/style-contract.md`](references/style-contract.md), [`references/motion-contract.md`](references/motion-contract.md), and [`references/qa-rubric.md`](references/qa-rubric.md).

## Why this project can own a category

Ink libraries exist. Stroke-order libraries exist. Motion tools exist. What is still missing is a small, reviewable workflow that joins them into a knowledge-video delivery contract. InkBrush Motion focuses on that missing layer: art direction, state gates, evidence, and truthful handoff.

If that direction is useful, **star the repository**. Stars help more makers discover a calmer visual language for AI knowledge.

## Validation

```bash
python3 scripts/validate_package.py
python3 scripts/validate_storyboard.py assets/demo-plan.json
python3 scripts/test_validate_storyboard.py
python3 scripts/test_validate_package.py
```

The demo is intentionally dependency-free. The references list optional open-source building blocks, but none are vendored into this repository.

## Copyright and license

Copyright © 2026 Vivi (GoAskVivi).

The source code, Skill instructions, documentation, code-authored SVG/CSS/JavaScript visuals, published social-preview PNG and animated README GIF, and the selected AI-assisted demo backgrounds in this repository are available under the [MIT License](LICENSE) to the extent those materials are copyrightable and controlled by the publisher, subject to the detailed boundaries in [COPYRIGHT.md](COPYRIGHT.md). Keep the copyright and license notice with copies or substantial portions.

The names **GoAskVivi** and its brand identity are not licensed for implied endorsement. See [COPYRIGHT.md](COPYRIGHT.md) for the human direction, AI-assistance, third-party, and trademark boundaries.

## Contributing

Small, visual, evidence-backed pull requests are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md). Good first contributions include new code-authored paper textures, renderer adapters, verified text-path support, and additional motion evidence checks.
