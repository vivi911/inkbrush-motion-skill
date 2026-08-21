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

## Clean animation plate edit

- Service: OpenAI ImageGen, built-in image-editing tool.
- Creation date: 2026-08-21.
- Input: `assets/ai-agent-knowledge-prestroke.png` (`d4fda3d048c8bfde95290cd5289530cb09b43f43cd085e62e552243ddd0189cd`).
- Purpose: remove the fixed photographed hand, sleeve, brush, and contact mark so the code-driven nine-pose hand is the only moving painter.

### Exact clean-plate prompt

```text
Use case: precise-object-edit
Asset type: clean 9:16 background plate for an animated Chinese ink-wash knowledge lesson
Input image: Image 1 is the edit target.
Primary request: Remove only the realistic human hand, black sleeve, calligraphy brush, and tiny fresh black ink touch from the lower-right foreground. Reconstruct the removed region as continuous warm fibrous xuan paper with the same faint pale-gray winding guide route already visible through the composition.
Preserve exactly: native 9:16 framing; every mountain, sun, pavilion, tree, bamboo stalk, bridge, blank rice-paper marker slip, paper fibre, shadow, color, object position, proportion, and the full pale-gray winding guide route. Do not crop, zoom, recompose, recolor, or add anything.
Style/medium: museum-quality traditional Chinese ink wash on tactile handmade xuan paper.
Constraints: the lower-right repair must be seamless at full resolution; no hand, fingers, skin, sleeve, brush, bristles, dark ink mark, text, logo, watermark, new objects, or finished black river anywhere. This is a clean animation plate only.
```

| Stage | SHA-256 | Note |
|---|---|---|
| Selected clean-plate ImageGen output | `2f5a3cb5ca7b0eb992c13ff7a24e71a9904538e710e0e5ac23df2f978bdd7999` | Original generated edit before repository post-processing |
| `assets/ai-agent-knowledge-cleanplate.png` | `37e16d24d69537bcdbb88dcee8307b78ae77a02c05fec79d82bc77a8a5f2e658` | Resized to exactly 1080×1920; used by the live demo and static board |

## Nine-action real-hand brush sprites

- Service: OpenAI ImageGen, built-in generation and image-editing tool.
- Creation date: 2026-08-21.
- Human direction and selection: Vivi / GoAskVivi. Vivi approved the gray-linen, xuan-paper art-direction sample before the nine poses were integrated.
- Approved visual reference source: `output/art-direction/recommended-a-ink-absorption-v2.png` SHA-256 `facc00ed79b46a52343ba46ef60714856aa2680866c3de6af6462e52c645fac1` (941×1672, local review source).
- Published visual reference: `assets/reference/real-brush-gray-linen.png` SHA-256 `49153b50a9a56539430099af1aa6475957b9bc7b9630075bdebc9927fcb6f85d` (720×1280).
- Action-layout reference: project-owned earlier nine-action proof SHA-256 `16204cb69a6f5f818fbc18255d9e2253a7d5ea001f7719613d67fef5a7d7c4f8`. It supplied action order and contact-sheet discipline only; no pixels from that sheet are published in v3.

### Production prompt record

```text
Create one production-ready 3×3 sprite sheet for a 9:16 Chinese ink-wash knowledge animation. Use the supplied nine-action contact sheet for action order and the approved gray-linen sample for the final hand, sleeve, brush, paper relationship, and quiet human realism.

Every cell must show the same believable adult right hand, the same traditional Chinese calligraphy brush, the same hand scale, the same gray natural-linen sleeve, and the same warm natural lighting. Keep the brush shaft nearly upright at 80–85 degrees and use a traditional calligraphy grip. The sleeve and forearm must continue naturally through the right edge; never cut bare skin at the frame boundary. No rings, jewelry, nail polish, logos, text, extra fingers, extra hands, extra brushes, or detached ink.

Arrange exactly nine equal cells in reading order: 01 HOVER with a visible paper gap; 02 TOUCH with first bristle contact; 03 PRESS with compressed bristles; 04 TRAVEL with attached moving bristles; 05 TURN with a controlled corner; 06 LIFT with pressure reduced but the tip still touching; 07 RETURN with a compact reverse hook; 08 FINISH with a tapered ending; 09 LEAVE with a clear gap between the lifted tip and completed ink.

Use one perfectly flat, uniform bright chroma-green background #00FF00 in every cell, edge to edge, with no paper, landscape, grid, labels, shadows, texture, gradient, watermark, or other object. Preserve clean complete hand and sleeve silhouettes for chroma keying. Output one 3×3 sheet only.
```

The prompt describes the intended production asset. It must not be read as a claim that an identified person performed the action.

### Published sprite identity

| Asset | SHA-256 |
|---|---|
| Generated 3×3 chroma source, 941×1672 | `05846c4ddab353b3ff888d852bb64c64b8702ebcf7910cccc72079c002c669ba` |
| 01 HOVER | `4bb53d10c827c59cf3542632e57d78a209a9d187e97047a04b7ae923b75eac92` |
| 02 TOUCH | `5e825a3eaf858603787417810a5d9d77178a6eb228059190e4ab32eea817829c` |
| 03 PRESS | `21535db0230d5d096921d2999d242175b4f66cee9c220ab4195d0eed26204cfc` |
| 04 TRAVEL | `a183c74c530a5a28c8ff2f9189e325d1ba9504f57c75f2fd9d26d307d7a2d823` |
| 05 TURN | `5927e49445362ea1a1e49ed743e8ee587ba3e072476996d37aa410401c3c7924` |
| 06 LIFT | `805812a945f34cb3db27e1b289cfcd1be7d27d7bbd5696794d908a28e121f9f5` |
| 07 RETURN | `3f7f1e077de59f5a84484ee39bb0338ef3a320b7b6fda980fe8c9e4206ad89cb` |
| 08 FINISH | `63dc0996a9ac75e4b0cb5a283249c1d3b5c00f2097b4aa6261c1e33b63eed311` |
| 09 LEAVE | `a9f8a713feffd92e911aa6d5e52b8716f641a48d34f7f73c32c2588bace68b00` |

`scripts/prepare_nine_action_sprites.py` crops the 3×3 sheet, removes the chroma background, suppresses green spill, locks every detected bristle tip to canvas coordinate (315,620), scales all subjects equally, extends only sleeve texture through the right frame boundary, and writes nine 720×1280 RGBA sprites. The generated chroma source is retained in ignored production output and is not distributed; the script and published sprites are included for review.

`assets/brush-pose-final.png` is byte-identical to approved v3 pose 09 (`a9f8a713feffd92e911aa6d5e52b8716f641a48d34f7f73c32c2588bace68b00`) so the static SVG evidence validator can bind the same lifted final hand used by motion.
