# Real-brush contract

Read this contract only when a visible hand appears. It turns the fragile parts of real-hand calligraphy into low-freedom acceptance rules.

## Default profile: `gray-linen-xuan`

- Use the approved gray-linen reference in `assets/reference/real-brush-gray-linen.png` for hand scale, sleeve weight, paper warmth, and ink absorption—not as a fixed composition to copy.
- Keep one adult right hand, five-finger anatomy, one brush, one grip, one sleeve, and one scale across all nine actions.
- Hold the brush shaft at 80–85° from horizontal. Path direction may bend the bristles but must not turn the shaft into a pencil grip.
- Enter from the right or lower-right. The frame may cut continuous sleeve fabric; it must never cut bare skin.
- Keep the hand, sleeve, and brush at least 16 SVG pixels away from visible knowledge text.

## Xuan-paper ink model

Model one stroke as three local layers:

1. `fresh core`: darkest only at the touching brush tip, 70–85% opacity, default 6 native SVG pixels and never longer than 18 pixels behind the bristle anchor;
2. `wet fringe`: 1.6–2.2× the core width, 15–25% opacity, delayed by 2–6 frames; and
3. `dry trail`: warm charcoal, 35–50% opacity, with 15–35% paper-fibre gaps.

Begin visible drying 12–24 frames after the tip passes. Do not apply one global blur or one uniform opacity to the full route. The oldest trail must be lighter and more broken than the newest contact area. The fresh core may move with the bristles; wet fringe and dry trail pixels must remain fixed on the paper. A rigid black tail translating with the hand is an automatic failure.

## Nine-action proof

Export a 3×3 proof in row-major order: hover, touch, press, travel, turn, lift, return, finish, leave. The proof must use the same pixels or render states as the animation, not a separate illustration.

Fail the proof when any cell shows:

- bare skin touching a frame boundary;
- a shaft angle outside 80–85°;
- ink ahead of the bristle tip;
- a moving fresh core longer than 18 native SVG pixels, or any rigid black tail that translates with the hand;
- a detached hand, extra finger, duplicated brush, or floating tip;
- a uniform black or gray ribbon without fibre gaps; or
- no paper gap between the lifted final bristles and completed ink.

The validator can bind dimensions, fields, paths, and hashes. A reviewer must still inspect anatomy, angle, crop continuity, text clearance, and ink material.
