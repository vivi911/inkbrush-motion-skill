# Style contract

Use this contract before creating the static board. Its purpose is not to imitate a named living artist. It defines a reusable visual system built from broad ink-wash and calligraphic traditions.

## Native portrait composition

- Author at `720×1280` for review and `1080×1920` for final delivery.
- Keep required text and marks inside an 8% safe margin.
- Build a vertical reading path with one dominant journey from lower foreground to upper distance.
- Reserve at least 35% of the frame as breathing room. Empty paper is an active design element.
- Do not design landscape-first and crop later.

## Palette

| Role | Suggested value | Use |
|---|---|---|
| Xuan paper | `#EDE5D4` | Base field |
| Deep ink | `#171B18` | Active stroke and primary type |
| Gray wash | `#82918A` | Distant mountains and mist |
| Cinnabar | `#9B352C` | One seal, one accent, or one decision point |

Allow small value changes for contrast. Do not add neon, electric blue, chrome, or multicolor gradients.

## Recipe: shan-shui-scroll

- Best for 3–6 ordered beats.
- Use one river or mountain path as the knowledge sequence.
- Add mist to separate depth planes; it must never obscure required text.
- Use bamboo, bridge, rock, boat, or pavilion only when it carries meaning.

## Recipe: minimal-calligraphy

- Best for one thesis, contrast, or compact framework.
- Use one large code-native calligraphic title, one restrained active brush stroke, and generous paper.
- Avoid treating every word as expressive calligraphy. Supporting copy stays highly legible.

## Recipe: seal-diagram

- Best for taxonomies, systems, or repeatable processes.
- Use seal-like nodes connected by dry-brush paths.
- Keep the diagram editorial and asymmetrical; avoid a dashboard grid.

## Text integrity

- Render required words as SVG `<text>`, HTML, or licensed local font text.
- Keep source text selectable and reviewable.
- Never ask an image model to spell required text.
- Do not outline text until the wording is approved. If text is later converted to paths, preserve the editable source beside the final asset.

## Static approval gate

Return `STATIC_REVIEW_READY` only when:

1. the artifact is native 9:16;
2. all required text is exact and legible at 360×640;
3. hierarchy works with motion disabled;
4. source and license notes are complete; and
5. the exact artifact hash is recorded before motion begins.
