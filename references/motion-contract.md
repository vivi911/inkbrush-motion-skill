# Motion contract

The animation should feel caused by a physical brush. Motion is accepted only when the causal order remains visible frame by frame.

## Required causal order

```text
brush tip advances → active stroke appears → local diffusion blooms → label settles → final hold
```

- The active stroke must not appear ahead of the brush tip.
- Diffusion must lag the active stroke by 2–6 frames at 30 fps.
- Diffusion should remain local. A global opacity fade is not ink behavior.
- Pressure variation may change stroke width by roughly 15–35%; do not pulse mechanically.
- The final composition must hold for at least 30 frames.

## Default timing

| Phase | Time | Purpose |
|---|---:|---|
| Paper breath | 0.0–0.7 s | Establish stillness |
| First stroke | 0.7–3.0 s | Reveal the problem |
| Development | 3.0–6.0 s | Show the decision path |
| Resolve | 6.0–8.0 s | Complete the deliverable |
| Hold | 8.0–9.0 s | Let the viewer read |

Treat these as defaults, not an excuse to stretch weak content.

## Acceptable implementation lanes

- `svg-js`: SVG paths, masks, filters, and browser JavaScript.
- `gsap-svg`: SVG animated by GSAP when that dependency is deliberately approved and licensed.
- `remotion-svg`: frame-accurate React/SVG delivery in an approved Remotion project.
- `after-effects`: human-authored composition with evidence frames and renderer ownership recorded.

If no approved lane exists, return `RENDERER_REQUIRED`. Do not install a tool or spend generation credits silently.

## Evidence packet

For `MOTION_PROOF_READY`, record:

- the SHA-256 of the approved static artifact bundle, including any linked local PNG;
- renderer lane and reviewer names;
- duration, frame rate, dimensions, and final hold;
- three unique PNG evidence frames at start, middle, and end;
- frame index and SHA-256 for each evidence image.

The reviewer must be different from the renderer owner. The validator checks evidence structure; a human reviewer checks taste, causality, and readability.
