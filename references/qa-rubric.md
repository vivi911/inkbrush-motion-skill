# Visual QA rubric

Inspect the static board and evidence frames at full size and at a 360×640 mobile viewport. A validator pass is necessary but not sufficient.

## Static board — all must pass

- Native 9:16 composition; no crop-dependent hierarchy.
- Required text is exact, selectable, and legible on mobile.
- One dominant brush journey is visible before animation.
- Empty space supports reading rather than feeling unfinished.
- Red is restrained to a seal or one semantic accent.
- No synthetic AI visual shorthand: neon glow, circuitry, floating UI cards, holograms, or particle fields.
- No unlicensed font, logo, stock art, or copied artist-specific composition.

## Motion proof — all must pass

- Brush tip visibly leads the active stroke.
- Ink diffusion follows locally with a believable delay.
- Start, middle, and end frames are materially different.
- Labels enter after their associated stroke reaches them.
- There is no rectangular wipe pretending to be handwriting.
- Camera movement, if any, does not fight the brush direction.
- The last frame holds long enough to read.

## Truthfulness gate

| State | Minimum evidence |
|---|---|
| `PLAN_ONLY` | Structured beats only |
| `STATIC_REVIEW_READY` | Existing portrait SVG and exact text |
| `MOTION_PROOF_READY` | Static approval hash, motion metadata, three unique frames, independent reviewer |
| `RENDERER_REQUIRED` | Approved static board but no authorized renderer |
| `HOLD` | Explicit unresolved wording, rights, source, or direction |

Never use “finished animation” for a static SVG, mockup, prompt, or unverified renderer claim.
