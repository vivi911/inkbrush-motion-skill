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
- For xuan paper, the newest contact stays darkest while older ink becomes warmer, lighter, and visibly broken by paper fibres. Read `real-brush-contract.md` for the numeric profile.
- The final composition must hold for at least 30 frames.

## Nine-action real-hand sequence

When the delivery shows a hand, the motion must use these ordered states. The hand keeps five-finger anatomy, a credible upright three-finger calligraphy grip, one consistent identity and scale, and a sleeved forearm that exits the right or lower-right frame edge. Bare skin must never meet the frame boundary.

| State | Visible proof |
|---|---|
| 01 HOVER | Pointed bristles remain off paper; no ink exists yet |
| 02 TOUCH | The tip barely contacts and creates one tiny point |
| 03 PRESS | Bristles compress and spread under pressure |
| 04 TRAVEL | The hand advances while ink appears only behind the tip |
| 05 TURN | Wrist rotation and bristle bend carry the route through a corner |
| 06 LIFT | Pressure reduces; the touching stroke visibly narrows |
| 07 RETURN | A controlled reverse rotation folds the tip into a compact return |
| 08 FINISH | The tapered terminal mark completes under a poised pause |
| 09 LEAVE | The bristles lift clear of the finished ink; no diffusion or stroke follows the lifted tip |

The final LEAVE frame must show paper between the bristle tip and the completed ink tail. Reusing one rigid pose for every state, moving a detached brush, or letting a fixed hand sit behind a marker fails this contract.

## Default timing

| Phase | Time | Purpose |
|---|---:|---|
| Paper breath | 0.0–0.7 s | Establish stillness |
| First stroke | 0.7–3.0 s | Reveal the problem |
| Development | 3.0–6.0 s | Show the decision path |
| Resolve | 6.0–8.0 s | Complete the deliverable |
| Hold | 8.0–9.0 s | Let the viewer read |

Treat these as defaults, not an excuse to stretch weak content.

### Public-repository preview override

When the motion is the repository's first visual proof, use a faster opening without deleting any brush state:

- show the first visible ink by `0.8 s`;
- complete hover, touch, and press in `1.2–1.4 s`;
- reveal the first knowledge beat by `2.5 s`;
- retain all nine ordered actions; and
- hold the complete frame without motion for at least `1.1 s`.

The README preview must be at least `360×640`. Directly below it, show labeled start, middle, and end crops so a visitor can verify `Tip leads → Ink absorbs → Evidence holds` without opening the live site.

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
- for `real-hand-nine-action`, one 1080×1920 PNG proof containing all nine ordered action states;
- frame index and SHA-256 for each evidence image.

The reviewer must be different from the renderer owner. The validator checks evidence structure; a human reviewer checks taste, causality, and readability.
