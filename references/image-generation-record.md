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

### Historical v2 per-action sprite identity

Before the consolidated 3×3 sheet, nine ImageGen edits were produced from the
same project-owned references using a shared full-frame prompt and one named
action addition per pose. The shared requirements locked the same synthetic
adult right hand, five-finger anatomy, 80–85° traditional grip, brush, scale,
lighting, chroma-green background, and right-edge forearm continuation. The
per-pose additions were HOVER, TOUCH DOWN, PRESS, TRAVEL, TURN, LIFT PRESSURE,
RETURN TIP, FINISH, and LEAVE PAPER. No third-party pixels, font files, logos,
or identified human performer were supplied.

#### Exact shared v2 production prompt

```text
Use case: precise-object-edit
Asset type: full-frame animation sprite on native 9:16 portrait.
Input Image 1 is the exact composition and identity base. Input Image 2 is the approved nine-action reference.
Preserve exactly from Image 1: canvas, uniform #00ff00 background, same adult East Asian woman's right hand, five fingers, skin, nails, 80–85° upright traditional three-finger grip, same brush, subject position, hand scale, lighting, and forearm extending through the right frame edge.
Change only the brush-contact action described below. Keep the entire hand and wrist identical. No background shadow, texture, text, labels, grid, logo, watermark, extra hand, extra brush, stray mark, or green on the subject.
```

Pose 01 used the same requirements directly as a full prompt. Poses 02–09
used the shared prompt plus their named action addition.

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

The nine published files were resized to 720×1280 with Lanczos filtering and
converted to RGBA with a local chroma-key/despill helper. Pose 09 additionally
received a targeted ImageGen edit that removed one detached ink fleck while
preserving the lifted-tip gap. These v2 files remain only as disclosed version
history and are not loaded by the active demo.

#### Exact v2 pose-09 cleanup prompt

```text
Create a clean chroma-key production version of this same asset. Preserve the same adult right hand, five-finger anatomy, upright traditional Chinese calligraphy brush, grip, proportions, lighting, scale, and placement. The brush must remain visibly lifted. Remove the small detached dark comma-shaped ink fleck below the bristle tip completely. There must be a clear empty gap below the intact bristles. Replace every transparent/checkerboard/background area with one perfectly flat uniform bright chroma green #00FF00, edge to edge, with no texture, gradient, shadow, checkerboard, paper, or other object. No text, no ink marks, no extra fingers, no extra brush. Output one vertical sprite image.
```

### Historical v3 sprite identity

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

These v3 sprites remain in the repository only as version history. They are not used by the active demo because the long lateral hair shapes could read as a black cord moving with the hand.

## Compact-bristle v4 correction

- Service: OpenAI ImageGen, built-in image-editing tool.
- Correction date: 2026-08-22.
- Input: the v3 generated 3×3 chroma source (`05846c4ddab353b3ff888d852bb64c64b8702ebcf7910cccc72079c002c669ba`).
- Purpose: preserve the approved hand, grip, sleeve, and action order while replacing rope-like black hair extensions with compact calligraphy bristles.

### First exact edit prompt

```text
Use case: precise-object-edit
Asset type: production 3×3 chroma-key sprite sheet for a Chinese calligraphy animation
Input image: edit target and exact layout reference.
Primary request: edit only the black brush-hair tuft below the black ferrule in each of the nine cells. Remove every long L-shaped, rope-like or hose-like black extension. Replace it with a physically believable compact Chinese calligraphy brush tuft: the dark hair from ferrule to tip is about 38–46 pixels long in this 941×1672 sheet; most of the tuft stays aligned with the rigid upright wooden shaft, while only the final 10–16 pixels compress or flex for the action. Keep nine distinct actions in reading order: hover with pointed dry tuft and a gap; touch with first contact; press with short compressed rounded tuft; travel with a compact backward flex only at the tip; turn with compact sideways flex only at the tip; lift with reduced compact contact; return with a tiny reverse hook only at the last hairs; finish with a short tapered ending; leave with pointed tuft and a clear gap.
Preserve exactly: same one adult right hand, five fingers, same grip, anatomy, hand scale, skin, gray linen sleeve, rigid upright wooden handle, lighting, cell positions, 3×3 layout, and crop. Sleeve remains continuous through the right edge of each cell.
Background: preserve one perfectly flat uniform chroma green #00FF00 edge to edge in every cell.
Constraints: no ink trail, no black stroke beyond the hair tuft, no paper, no shadows on green, no grid, no labels, no text, no watermark, no extra fingers, no extra hands, no extra brushes, no detached tips. Change only the brush hairs below each ferrule.
```

The selected intermediate edit is SHA-256 `7e2823b629cae666bb667fbc870d3af4b5b4e72f618c8d20f4375e129d0b9c6f`.

### Second exact edit prompt

```text
Keep this exact 3×3 chroma-green sprite sheet, the same hand, sleeve, grip, rigid handle, scale, framing, lighting, and compact 38–46 pixel brush-hair length. Make one targeted change only: make the nine brush-hair tip shapes clearly distinguish the calligraphy actions without ever becoming a long curved rope.
Reading order: 01 hover = narrow pointed tuft; 02 touch = point just beginning to flatten; 03 press = visibly short, wider, rounded compressed tuft; 04 travel = compact tuft with only the final 10–14 pixels flexing backward; 05 turn = compact tuft with only the final 10–14 pixels flexing sideways; 06 lift = narrow reduced-pressure contact; 07 return = tiny reverse hook confined to the last 8–10 pixels; 08 finish = short fine taper; 09 leave = narrow pointed tuft. Keep all nine tips local to the ferrule and no black line or ink trail anywhere.
Preserve perfectly flat uniform #00FF00 background and all other pixels/composition. No text, grid, paper, shadows on green, watermark, extra fingers, extra hands, extra brushes, detached tips, L-shapes, hose shapes, or long black strokes.
```

### Historical v4 sprite identity with deterministic soft-hair reconstruction

After chroma keying and alignment, `scripts/prepare_nine_action_sprites.py`
removes the generated compact tuft and rebuilds the visible hairs from a
code-authored pressure model. This preserves the selected synthetic hand,
grip, shaft, sleeve, and lighting while making the hair states inspectable and
repeatable: pointed at rest, rounded on first touch, visibly fanned under
pressure, tapered at finish, and separated from the paper on leave. The
post-processing script SHA-256 is
`6d36f2138613f408b8fec4fd64ced472620e88209bc13d9b36287d2c1d5060c7`.

| Asset | SHA-256 |
|---|---|
| Selected compact-bristle 3×3 chroma source, 941×1672 | `8b14692b15f74c4d2bc6e1a38f56a698ab7ca98aaa927f234c34ff487b37c4c0` |
| 01 HOVER | `142ca1b8d1b8ef3eea85a432fce5aa7f17641a5c3be84865158231c0c845589a` |
| 02 TOUCH | `d009180e4687c586c89b6700eec255fa2f487cde5093699dc42391169dd95c8e` |
| 03 PRESS | `4937512b84b0144d4c4aecb5fa07859d13a123817cfff0f57a510e78e41436f0` |
| 04 TRAVEL | `b0a6b592427f419880a6bfe8952e961f423b422cbe9d736d8aa6c6fbfcd4c213` |
| 05 TURN | `31b51a36e37cc13251b78454c67fe78f18f22a93dd74fe006e9322ec9523b649` |
| 06 LIFT | `2570c9d48f093e7648ebf1eeedbf34855e976dcf655a1919cf8b0d03fecb9ee9` |
| 07 RETURN | `7511f86429b2eb677f9c9219c918f1a3d9f87cf9e0d7b96d5f279dad01c75a63` |
| 08 FINISH | `96b02f554de2800e8722114f1b47f5bf221145ef67eb91828596810c4077dd88` |
| 09 LEAVE | `a0fd8190962e75cd24b7f8e0ed5a9659c36450512ae867f78925dff54729a3d2` |

`scripts/prepare_nine_action_sprites.py` turns the selected v4 sheet into nine 720×1280 RGBA sprites and applies the disclosed deterministic soft-hair reconstruction. These files remain as inactive version history and are not loaded by the active demo.

## Photographic-looking v5 source and active sprites

- Service: OpenAI ImageGen, built-in image generation tool. The session did not expose a more specific model identifier.
- Creation and selection date: 2026-08-22.
- Human direction, selection, and review: Vivi / GoAskVivi.
- Intended use: synthetic hand-and-brush motion sprites for this open-source 9:16 knowledge-animation Skill.
- Public source: `assets/reference/brush-hand-sheet-v5.png`, 941×1672, SHA-256 `569fb216f3510dcff04813ad451e96d09d458a6ca61bb942d2d57558fce9f6d9`.
- Identity boundary: the depicted hand is AI-assisted synthetic media. It is not an identified performer and is not evidence that a person painted the pixels.

### Production brief supplied to ImageGen

The generation requested one 3×3 chroma-green production sheet with a single
consistent adult right hand, gray linen sleeve, upright traditional Chinese
calligraphy brush, photographic lighting, and nine states in row-major order:
HOVER, TOUCH, PRESS, TRAVEL, TURN, LIFT, RETURN, FINISH, and LEAVE. The brief
required five-finger anatomy, one brush, a continuous sleeve reaching the
right edge, complete ferrule and wet bristles, no ink trail, no paper, no text,
no grid labels, no extra hand or brush, and a flat green background suitable
for deterministic chroma keying. It explicitly rejected a hard polygon nib,
detached bristles, a square ferrule seam, a long rope-like black tail, and bare
skin touching the canvas edge.

The exact verbatim ImageGen request was not retained by the generation tool in
the repository session. This section therefore records the human-authored
production requirements without presenting a reconstructed paragraph as an
exact quote. The selected source pixels, source hash, deterministic builder,
machine-readable action manifest, and every published output hash are included
so the released asset identity remains auditable.

### Deterministic post-processing

`scripts/build_calligraphy_brush_v5.py` crops the nine source cells, removes and
despills chroma green, anchors every bristle tip to `(315,620)`, preserves each
cell's photographic-looking hand, wrist, shaft, ferrule, and wet tuft, and
extends only sleeve fabric to the right frame edge. PRESS alone applies a
raster-only axial compression to the photographed terminal pixels: hair height
60 px, maximum contact width 27 px, 3 px terminal width, 42 px ferrule region,
and 4 px shaft overlap. No vector or code-drawn nib is composited into v5.

The builder SHA-256 is `917650614f976083703c4cac5b6011b446fb1faa723e82d12a8d43bfcb144211`.
The machine-readable parameters and hashes are also stored in
`assets/brush-poses-v5/manifest.json` (SHA-256
`5ccf96475ab88e7c695f1e713b269dfe2554b81d73749a9219f5561c835331be`).

| Active v5 asset | Published PNG SHA-256 | Decoded RGBA pixel SHA-256 |
|---|---|---|
| 01 HOVER | `0395742b0478962b0dcd09ccc292db797a5e3d9e0f8eec8b26a0f8c1ce91396f` | `9b20b32cc7faa52279aad3f1875c2a4ecaf28a184bd0a72199ee6f152f9a4d32` |
| 02 TOUCH | `3b7d85a04a7a694685d5c6f1944972936d8bf422e544c9841e2dd91a28a176ad` | `22bef1b8a23e9b3540f7f0ea136e4c08e1691c5d81c8b4a9872ff0eeff64612e` |
| 03 PRESS | `3b0f97e63d0b4d355d43c6568d538a29e15e70528bbed2c7dca115bc3c2922cb` | `7a592d7a4ffa786a87ce7baefa5e059607a7159ddc599298a7618eb52ccb0282` |
| 04 TRAVEL | `dfafed3c777090a411e2e84f4854b1e288255f1f235dd527235399f7bbfafe5c` | `db1352632674e7789b469c8f6debe0a6a2499f55e46fd8f1c9600cfc8964cb00` |
| 05 TURN | `d379bc9a2e4c367763d377039ea720a61f11fd8e54f292940625f3b796f58a74` | `86c28eea71b46d271ed2fafe7a85a1c6c6601677f50a18a41fa8ecacffa7ad0c` |
| 06 LIFT | `45c4296951793fb2f3190fb1b5be67be813d0d2dcf9dda3a69df0b66484d7217` | `19ac93ae0bdf30b89c5cba5ae25006e8ce8c0a809b2db724a30d5ec1db0ce1ac` |
| 07 RETURN | `b14c6d6b0135fab607d8929dbfdee1ad9a572a4f38d1b7bb4b3459d60d8a9225` | `08197037ead8a848b6727af480cdfedef9f99b7315c2ae86577d8801f8866886` |
| 08 FINISH | `fe02935133e310ab47198111eca3c5b52f3ca944d43f82facc186fe45104beff` | `92f2c8a68e8c129c2502fbdd3c057edaf5583f44f05ddf6e912bd9d027ca5f8a` |
| 09 LEAVE | `a18e3f4c1424688e0134163caf4e8b896acb25379b84dc36bebe4537a4b77681` | `3b35defb30d79fd71208c978da2660bb0719c06f37713eeb3d996564f98eba45` |

`assets/brush-pose-final.png` is byte-identical to active v5 pose 09. Two
independent rebuilds under Pillow 11.3.0 reproduce all nine decoded RGBA images
pixel-for-pixel via `scripts/test_build_calligraphy_brush_v5.py`; the test also
checks byte stability within one environment. Published PNG byte hashes remain
separate because zlib compression bytes can differ across platforms without
changing decoded pixels.
