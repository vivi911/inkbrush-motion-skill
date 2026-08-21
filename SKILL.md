---
name: inkbrush-motion-skill
description: Turn approved knowledge copy into a review-gated 9:16 Chinese ink-wash and calligraphy motion package. Use when the user asks for ink-wash animation, calligraphy motion, Chinese landscape storytelling, brush-and-paper knowledge visuals, static-first motion design, or a calm alternative to glossy AI-looking explainers.
---

# InkBrush Motion

Turn knowledge into a quiet visual journey built from brush, ink, paper, and deliberate motion instead of a glossy dashboard.

## Defaults

- Compose natively at `9:16`: preview `720×1280`; final contract `1080×1920`, `30 fps`, H.264.
- Use `shan-shui-scroll` unless the brief clearly needs `minimal-calligraphy` or `seal-diagram`.
- Keep every required mark inside an 8% safe margin.
- Lock exact wording before visual work. Render final text as code-native SVG or licensed font text, never image-model lettering.
- Keep the first proof silent unless audio is explicitly requested.
- When a visible hand is requested, use nine readable calligraphy actions in order: hover, touch, press, travel, turn, lift pressure, return tip, finish, and leave paper. A floating brush or one rigid sprite does not satisfy this contract.
- Default real-hand work to the `gray-linen-xuan` profile: an upright brush, a continuous sleeve entering from the right or lower-right, and ink that visibly dries into the paper instead of staying as a solid black ribbon.
- For a public repository showcase, prove the result above the fold: render the README loop at no less than `360×640`, show the first visible ink by `0.8 s`, reveal the first knowledge beat by `2.5 s`, and place labeled start / middle / end evidence directly below the preview.

## Workflow

1. Inventory the exact copy, audience, duration, visual assets, renderer, and rights status.
2. Reduce the knowledge into 3–6 ordered beats. Give each beat one idea and one landscape metaphor.
3. Read `references/style-contract.md` and build a native portrait static board.
4. Return `STATIC_REVIEW_READY`. Hash the exact static artifact bundle—including any linked local PNG—and wait for human visual approval before motion.
5. Read `references/motion-contract.md`. For visible-hand work, also read `references/real-brush-contract.md` and use its low-freedom hand, sleeve, and ink gates.
6. Build a 6–10 second proof in which the brush leads the ink and diffusion follows with a delay. For real-hand mode, prove all nine calligraphy actions, complete hover / touch / press in `1.2–1.4 s`, keep the sleeve connected to a frame edge, and hold the finished frame for at least `1.1 s`.
7. Export unique start, middle, and end evidence frames. Real-hand work also exports a hash-bound 3×3 action proof. Run `scripts/validate_storyboard.py` and inspect every proof at 360×640.
8. Return `MOTION_PROOF_READY` only after an independent visual review. If no approved renderer exists, return `RENDERER_REQUIRED`.

## Style recipes

| Style | Best for | Visual character |
|---|---|---|
| `shan-shui-scroll` | A journey with 3–6 knowledge beats | Mountains, mist, river, bridge, bamboo, warm xuan paper |
| `minimal-calligraphy` | One thesis or compact framework | Large calligraphy, restrained brushwork, generous empty space |
| `seal-diagram` | A process or taxonomy | Seal-like nodes, editorial rhythm, strong brush title |

Never blend styles unless the user explicitly asks for a hybrid.

## Readiness states

- `PLAN_ONLY`: beat plan exists; no static artifact exists.
- `STATIC_REVIEW_READY`: portrait board and exact text layer exist; human approval is pending.
- `MOTION_PROOF_READY`: the approved static artifact is hash-bound and a 6–10 second proof passed evidence checks.
- `RENDERER_REQUIRED`: the board is ready but no approved renderer is available.
- `HOLD`: wording, rights, source, or visual direction is unresolved.

## Validation

Run from this repository:

```bash
python3 scripts/validate_package.py
python3 scripts/validate_storyboard.py assets/demo-plan.json
python3 scripts/test_validate_storyboard.py
python3 scripts/test_validate_package.py
```

Read `references/qa-rubric.md` before calling any visual ready. The validators verify supplied evidence; they do not replace human taste review.

## Boundaries

- Do not call a static board an animation or a plan an MP4.
- Do not use wipes, rectangular masks, or opacity fades as the primary writing illusion.
- Do not call a floating brush, detached hand, pencil grip, or rigid single-pose translation a real-hand calligraphy animation.
- Do not let bare skin touch a frame boundary, let the brush fall outside 80–85°, or leave a uniform opaque trail after the brush has moved on.
- Do not publish, deploy, spend generation credits, or install third-party code without authorization.
- Read `COPYRIGHT.md` and `references/copyright-and-provenance.md` before adding external assets.
- This repository is MIT-licensed. Preserve the copyright and license notice in redistributed copies.
