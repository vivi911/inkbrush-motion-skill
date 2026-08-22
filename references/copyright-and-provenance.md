# Copyright and provenance checklist

Complete this checklist before adding any external asset, dependency, font, dataset, or generated media.

## Record for every external item

- Human-readable asset name.
- Original creator or organization.
- Direct source URL, not a search result page.
- License name and direct license URL.
- Date accessed.
- Whether modification and redistribution are allowed.
- Whether attribution or notice files are required.
- Where that attribution appears in the delivery.

## Stop conditions

Return `HOLD` if any required item has:

- no discoverable license;
- a noncommercial restriction that conflicts with the intended use;
- a no-derivatives term but the delivery modifies it;
- an unclear font embedding right;
- identifiable private data or a real person's likeness without authorization; or
- a request to imitate a named living artist's signature style.

## Generated media

Record the model or service, creation date, human-authored inputs, human selection and editing, and the service terms used at the time. Do not promise that purely machine-generated material is copyrightable in every jurisdiction.

The repository-wide public statement is in [`COPYRIGHT.md`](../COPYRIGHT.md).

## Current public-package record

| Item | Source | Rights note | Redistribution |
|---|---|---|---|
| HTML/SVG/CSS/JavaScript demo | Original code-authored composition in this repository | MIT, copyright notice in `LICENSE` | Included |
| `assets/ai-agent-knowledge-journey.png` | OpenAI ImageGen output created 2026-08-20 from human-authored direction and two project-owned AI-generated reference boards; exact prompt and hashes in [`image-generation-record.md`](image-generation-record.md); selected and integrated by Vivi / GoAskVivi | OpenAI assigns output rights to the user to the extent permitted by law; MIT permission expresses the publisher's reuse intent, without promising copyrightability or uniqueness | Included |
| `assets/ai-agent-knowledge-prestroke.png` | OpenAI ImageGen edit created 2026-08-21 from the selected journey image; the completed river was removed to create a pre-stroke animation plate; exact edit prompt and hashes in [`image-generation-record.md`](image-generation-record.md) | Same rights boundary as the selected journey image; MIT permission expresses the publisher's reuse intent without promising copyrightability or uniqueness | Included |
| `assets/ai-agent-knowledge-cleanplate.png` | OpenAI ImageGen edit created 2026-08-21 from the pre-stroke plate; the fixed photographed hand and brush were removed for the live nine-action painter; exact prompt and hashes in [`image-generation-record.md`](image-generation-record.md) | Same rights boundary as the selected journey image; MIT permission expresses the publisher's reuse intent without promising copyrightability, uniqueness, or human authorship of generated pixels | Included |
| `assets/reference/real-brush-gray-linen.png` | OpenAI ImageGen output created 2026-08-21 from the approved art direction; selected by Vivi as the gray-linen, xuan-paper reference gate | Same rights boundary as the selected journey image; the synthetic hand is not presented as an identified real contributor | Included |
| `assets/reference/brush-hand-sheet-v5.png` | OpenAI ImageGen 3×3 source selected 2026-08-22 from a human-authored nine-action brief; exact source hash and disclosure in [`image-generation-record.md`](image-generation-record.md) | OpenAI assigns output rights to the user to the extent permitted by law; the source sheet is published under MIT to the extent controlled and copyrightable, without claiming the synthetic hand is a real performer | Included |
| `assets/brush-poses-v5/pose-01.png` through `pose-09.png` | Deterministically cropped, chroma-keyed, anchored photographic-looking raster states built from the disclosed v5 sheet by `scripts/build_calligraphy_brush_v5.py`; PRESS alone applies a documented raster deformation to the photographed tuft pixels | Same rights boundary as the v5 source sheet; the selected sprites and human-directed compilation are published under MIT to the extent controlled and copyrightable | Included, active |
| `assets/brush-poses-v4/pose-01.png` through `pose-09.png` | Historical OpenAI ImageGen action sprites with deterministic code-authored soft-hair reconstruction; no longer used by the active demo | Same MIT grant to the extent controlled and copyrightable; synthetic-hand disclosure still applies | Included, inactive |
| `assets/brush-poses-v3/pose-01.png` through `pose-09.png` | Historical OpenAI ImageGen action sprites retained for version history; no longer used by the active demo | Same MIT grant to the extent controlled and copyrightable; synthetic-hand disclosure still applies | Included, inactive |
| `assets/brush-poses-v2/pose-01.png` through `pose-09.png` | Historical OpenAI ImageGen per-action sprites created 2026-08-21 from the exact shared and per-pose prompt recorded in [`image-generation-record.md`](image-generation-record.md), then resized and chroma-keyed locally; no longer used by the active demo | Same MIT grant to the extent controlled and copyrightable; synthetic-hand disclosure still applies | Included, inactive |
| `assets/brush-pose-final.png` | Byte-identical evidence copy of the approved `pose-09.png`, used only by the static SVG review board | Same rights boundary as the nine-action sprites | Included |
| `assets/nine-action-proof.png` and `assets/evidence/*.png` | Deterministic local compositions rendered from the disclosed clean plate, active v5 sprites, route, and code-native English copy | MIT for the human-directed composition to the extent controlled and copyrightable, subject to the source-image and font boundaries in `COPYRIGHT.md` | Included |
| `assets/social-preview.png` | Flattened output of `scripts/generate_social_preview.py` using exact code-rendered text and the disclosed AI-assisted journey background | MIT for the human-directed composition and published rendition to the extent controlled and copyrightable, subject to the image and font boundaries in `COPYRIGHT.md` | Included |
| `assets/inkbrush-motion-demo.gif` | Deterministic proof render of the live demo contract; exact source-file hashes, render recipe, frame count, duration, and output hash are in [`readme-animation-record.md`](readme-animation-record.md) | MIT for the human-directed composition and rendered rendition to the extent controlled and copyrightable, subject to the source-image boundaries in `COPYRIGHT.md` | Included |
| Pillow 11.3.0 | [python-pillow/Pillow 11.3.0](https://github.com/python-pillow/Pillow/tree/11.3.0) | [MIT-CMU License](https://github.com/python-pillow/Pillow/blob/11.3.0/LICENSE); maintainer build tool only | Not included |
| Georgia, Arial, Songti | macOS system typefaces | Governed by the applicable [Apple software license agreement](https://www.apple.com/legal/sla/); used only to render the flattened preview | Font software not included |

Snapshot date: 2026-08-22.
