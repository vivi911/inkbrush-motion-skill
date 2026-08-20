# AI image generation record

This record identifies the AI-assisted source used by the live demo. It is provided for provenance and reproducibility review; it does not claim that the same prompt will produce the same pixels.

## Service and selection

- Service: OpenAI ImageGen, built-in generation tool. The session did not expose a more specific model identifier.
- Creation date: 2026-08-20.
- Human direction and selection: Vivi / GoAskVivi.
- Intended use: 9:16 visual proof for the public InkBrush Motion Skill and live demo.
- Required text: none in the generated image; all lesson wording is code-native HTML/SVG text.

## Input references

Both inputs were earlier AI-generated concept boards owned by the project. They are not redistributed in this public package.

| Reference | Role | SHA-256 |
|---|---|---|
| Reference A | Long-scroll landscape, winding river, quiet shanshui mood | `3b0c41b8ef3759a58fbcb6f40fc4ab7c22445e446ce0ccf6987fce858f04c374` |
| Reference B | Hand, brush, xuan-paper fibers, and active-ink direction | `eafa6368ac92995253bd069c2ded8fb03eb2c9686cb8e5a922cada24ac91c3ee` |

## Exact prompt

```text
Use case: stylized-concept
Asset type: vertical 9:16 visual proof for an open-source AI Skill README and live demo
Primary request: Create one cinematic mid-animation still that immediately communicates “knowledge is being painted by a real human hand.” A traditional Chinese calligraphy brush, held by a believable adult hand entering naturally from the lower-right edge, is actively laying down a wet black ink river on warm handmade xuan paper. The fresh stroke is darkest directly under the brush tip, with visible bristle pressure, dry-brush breaks, feathered wet edges, tiny ink bloom and delayed diffusion behind the tip. The river travels upward through a restrained Chinese shanshui landscape and visually connects three stages of thought.
Input images: Image 1 is the main reference for the long-scroll landscape, winding river composition and quiet shanshui mood. Image 2 is the reference for realistic hand, brush, paper fibres and live ink causality. Use their medium and emotional direction, but do not copy any existing text or labels.
Scene/backdrop: A genuine hand-painted Chinese ink landscape emerging from blank paper—distant mist mountains, a small bridge, sparse bamboo and one faint vermilion sun. Much of the lower paper remains quiet and unfinished so the viewer feels the painting is happening now.
Subject: Real human hand and traditional brush making the active stroke; the brush tip must physically touch the freshest ink edge. Three subtle unprinted rice-paper marker slips sit beside the river as future locations for code-native labels.
Style/medium: Museum-quality traditional Chinese ink wash and calligraphy on fibrous xuan paper, tactile, imperfect, restrained, poetic, handmade. Photographic realism only for the hand and brush; all scenery must feel painted in ink, never digital vector art.
Composition/framing: Native 9:16 portrait. The journey rises from lower foreground to distant upper mountains. Keep clear calm spaces beside the three markers for later code-native text. The brush and hand occupy no more than the lower-right quarter and do not cover the route.
Lighting/mood: Soft natural window light, warm off-white paper, quiet contemplative atmosphere, no dramatic spotlight.
Color palette: Warm rice paper, layered black and gray ink, one very restrained cinnabar-red sun/seal accent.
Materials/textures: Strong visible paper fibres, wet ink blooms, dry brush texture, bristle marks, uneven ink density.
Text: no text, no letters, no numerals, no calligraphy, no watermark.
Constraints: The brush must lead the stroke and the ink must not appear ahead of the tip. The image must look like a real person is painting knowledge, not like an AI infographic. Leave exact text to later HTML/SVG overlay.
Avoid: modern UI cards, dashboards, diagrams, icons, neon, gradients, particles, holograms, circuit patterns, glossy 3D, flat vector mountains, synthetic stock-photo polish, fake pseudo-Chinese characters, malformed hand, extra fingers, duplicated brush, detached brush tip, black plastic-looking river, heavy sepia filter.
```

The prompt describes the desired appearance. It must not be read as a claim that a human painted the resulting pixels.

## Output identity and edits

| Stage | SHA-256 | Note |
|---|---|---|
| Selected ImageGen output | `754e4c504481f48a7c4b2e4956c4b668bd6dad819a858c8d5a8f159c49be3b43` | Original generated output before repository post-processing |
| `assets/ai-agent-knowledge-journey.png` | `8e9c408d626ee75bb9f0cb0620d3db4440ae273240c32432e2fae8a765d5f110` | Resized to exactly 1080×1920; no required text baked into the image |

Exact lesson wording, card layout, path reveal, brush marker, timing, and replay behavior are implemented separately in repository code.

## Pre-stroke animation plate edit

- Service: OpenAI ImageGen, built-in image-editing tool. The session did not expose a more specific model identifier.
- Creation date: 2026-08-21.
- Input image: the selected journey composition published as `assets/ai-agent-knowledge-journey.png` (`8e9c408d626ee75bb9f0cb0620d3db4440ae273240c32432e2fae8a765d5f110`).
- Purpose: remove the completed dark river while preserving the approved composition, so the visible SVG stroke is created during playback instead of being uncovered from a finished image.

### Exact edit prompt

```text
Edit the supplied 9:16 Chinese ink-wash scene while preserving its approved composition and visual identity.

Primary edit: remove the completed dark black river/road that runs from the distant mountains down to the brush tip. Reconstruct that winding area as continuous warm fibrous xuan paper with only a very faint pale-gray ink guide, no solid white stripe and no dark finished stroke. The paper fibers and nearby landscape wash must continue naturally across the former river area.

Preserve exactly: the 9:16 framing; distant misty mountains; pale vermilion sun; pavilion; bridge; bamboo; three blank rice-paper marker slips; realistic lower-right adult hand; traditional brush; warm paper texture; restrained black/gray/vermilion palette; all object positions and proportions.

At the brush tip, leave only a tiny fresh dark ink touch no larger than the bristle contact area. Do not leave a long black trail.

Text: none. No letters, numerals, calligraphy, labels, watermark, logo, or pseudo-writing.

Avoid: pure white masking shape, opaque cream road, plastic-looking path, extra river, extra hand, extra brush, changed anatomy, altered marker slips, modern UI, neon, gradients, vector polish, heavy sepia, cropping, zooming, or re-composition.

This is a clean pre-stroke background plate for code-driven ink animation. The final visible dark river will be added later by SVG, so the background must not contain the completed river.
```

### Edit output identity

| Stage | SHA-256 | Note |
|---|---|---|
| Selected ImageGen edit output | `5da60c71f67d8453d5e0a35253abc351d87b929254c68ce08063df06b6f5e66a` | Original 941×1672 generated edit before repository post-processing |
| `assets/ai-agent-knowledge-prestroke.png` | `d4fda3d048c8bfde95290cd5289530cb09b43f43cd085e62e552243ddd0189cd` | Resized to exactly 1080×1920; no required text baked into the image |
