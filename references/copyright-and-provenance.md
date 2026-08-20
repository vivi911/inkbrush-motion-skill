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
| `assets/social-preview.png` | Flattened output of `scripts/generate_social_preview.py` using exact code-rendered text and the disclosed AI-assisted journey background | MIT for the human-directed composition and published rendition to the extent controlled and copyrightable, subject to the image and font boundaries in `COPYRIGHT.md` | Included |
| Pillow 11.3.0 | [python-pillow/Pillow](https://github.com/python-pillow/Pillow) | [HPND License](https://github.com/python-pillow/Pillow/blob/main/LICENSE); maintainer build tool only | Not included |
| Georgia, Arial, Songti | macOS system typefaces | Governed by the applicable [Apple software license agreement](https://www.apple.com/legal/sla/); used only to render the flattened preview | Font software not included |

Snapshot date: 2026-08-21.
