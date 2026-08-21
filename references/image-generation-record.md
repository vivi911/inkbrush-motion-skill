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
- Human direction and selection: Vivi / GoAskVivi; the nine-action direction was approved before production integration.
- Identity reference: approved 3×3 art-direction proof SHA-256 `16204cb69a6f5f818fbc18255d9e2253a7d5ea001f7719613d67fef5a7d7c4f8`.
- Workflow reference: project-owned Vivi Whiteboard v3 nine-pose proof SHA-256 `2a01c9b4c87b3b87cb9d1054137acc8628dc3dacc675f3ae7bf01a6119f16be2`; it supplied contact-sheet discipline only, not shipped pixels, text, or marker graphics.
- Visual reference: `assets/ai-agent-knowledge-prestroke.png` SHA-256 `d4fda3d048c8bfde95290cd5289530cb09b43f43cd085e62e552243ddd0189cd`.

### Shared production prompt

```text
Use case: precise-object-edit
Asset type: full-frame animation sprite on native 9:16 portrait.
Input Image 1 is the exact composition and identity base. Input Image 2 is the approved nine-action reference.
Preserve exactly from Image 1: canvas, uniform #00ff00 background, same adult East Asian woman's right hand, five fingers, skin, nails, 80–85° upright traditional three-finger grip, same brush, subject position, hand scale, lighting, and forearm extending through the right frame edge.
Change only the brush-contact action described below. Keep the entire hand and wrist identical. No background shadow, texture, text, labels, grid, logo, watermark, extra hand, extra brush, stray mark, or green on the subject.
```

The per-pose additions were: HOVER (clean gap, no ink), TOUCH DOWN (tiny contact point), PRESS (compressed spread), TRAVEL (short attached trail), TURN (compact attached corner), LIFT PRESSURE (narrow taper while touching), RETURN TIP (compact reverse hook), FINISH (paused tapered end), and LEAVE PAPER (clear lifted gap). Pose 01 used the same requirements directly as a full prompt; poses 02–09 used the shared prompt plus their named addition.

### Published sprite identity

| Pose | Generated chroma source SHA-256 | Published RGBA SHA-256 |
|---|---|---|
| 01 HOVER | `3dc41c13a30220a8d6a78271135307cea0dfc35daf47e3176e93e9d2cecab122` | `7cb1b6e47eab38f5294d08fb1b51ff256466a97667973a867ae616a6da0bb429` |
| 02 TOUCH DOWN | `6a70d611609ec20663766c1a18ac1f7e55ad1c5da2dc767a96e03bb3391f9fe0` | `700d83a95e5446753156b83d5d0cb5a4c035e11f5ee27628a447d39cc0248752` |
| 03 PRESS | `5210e55c4fae9d610203a9a947d2b3c6f420e43cd76a6831a1e581ab29018881` | `a8141623bf31bd41a877094b19bc5ce259bd3603f60503ed9d111afb6a9a371a` |
| 04 TRAVEL | `7c2fa6c420229cfcf12601603a4655d0e8eca7bfb2bea8ad7f54ea0c330cf490` | `43c5c9df05d6f16e10b93c7ea7bef6eabf43296bd9a3c8687e6a73380b51bc31` |
| 05 TURN | `0c8da34f98409227c13073dfd44346463d406208d538cf5569126010840036ad` | `041a7542a138d679927ff8a17c4a89c2965f7ed55cfbe1e4fa8f0581f5e947e2` |
| 06 LIFT PRESSURE | `a80f4ed700e064cf8a57e34baffb7d04fadd7e67073bbb0758b9102d5e6b1650` | `e5f86d96a3162d775cd636adedd996af9ab48023813a3a30a52bd8b6990df259` |
| 07 RETURN TIP | `18afb008d47a0df59c51359b5c88feecb1e646155f2427ca85155dd26893a2c8` | `485711d794e1226b4998030146b369f399fc8a2c3cc8a69b28c5ae4a21fb1eaa` |
| 08 FINISH | `12de1d603b0051bfdb6f58887680383ad7d40bf11480a9078e2d09da499147b1` | `7ccf6b02f089410fb140de231dc2535208ec432e15598ca2e3e240929dd92000` |
| 09 LEAVE PAPER, cleaned | `0ed045d4e3f9b67efb217c9224bc1391e63d17f061f06c9750c5d79d3f0defe1` | `8d7ae7052800f11be0acece156ea83e379d1135ca09a14fbaf90ffc7b71a1872` |

Poses 01–08 were resized to 720×1280 with Lanczos filtering, then converted to RGBA with the repository-used ImageGen chroma-key helper (`--auto-key border --soft-matte --transparent-threshold 12 --opaque-threshold 220 --despill`). Pose 09 was re-edited to remove a detached ink fleck, resized to 720×1280, then converted with the same helper using `#00ff00`, soft matte thresholds 24/112, edge feather 0.4, and spill cleanup. Its exact cleanup prompt was:

```text
Create a clean chroma-key production version of this same asset. Preserve the same adult right hand, five-finger anatomy, upright traditional Chinese calligraphy brush, grip, proportions, lighting, scale, and placement. The brush must remain visibly lifted. Remove the small detached dark comma-shaped ink fleck below the bristle tip completely. There must be a clear empty gap below the intact bristles. Replace every transparent/checkerboard/background area with one perfectly flat uniform bright chroma green #00FF00, edge to edge, with no texture, gradient, shadow, checkerboard, paper, or other object. No text, no ink marks, no extra fingers, no extra brush. Output one vertical sprite image.
```

`assets/brush-pose-final.png` is a byte-identical copy of the approved pose 09 (`8d7ae7052800f11be0acece156ea83e379d1135ca09a14fbaf90ffc7b71a1872`) placed beside `static-board.svg` so the fail-closed SVG evidence validator can keep local image references sibling-only.
