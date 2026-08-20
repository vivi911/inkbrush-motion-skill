# Copyright, license, and provenance

## Copyright notice

Copyright © 2026 Vivi (GoAskVivi).

## License scope

The repository's source code, `SKILL.md`, documentation, schemas, tests, code-authored SVG/CSS/JavaScript visuals, the published `assets/social-preview.png` rendition, and the selected AI-assisted demo backgrounds (`assets/ai-agent-knowledge-journey.png` and `assets/ai-agent-knowledge-prestroke.png`) are licensed under the MIT License in `LICENSE`, to the extent those materials are copyrightable and controlled by the publisher.

The MIT License allows commercial use, copying, modification, distribution, sublicensing, and sale. Copies or substantial portions must retain the copyright and license notice. The work is provided without warranty.

## AI-assistance disclosure

This project was developed with AI-assisted research, image generation, and coding under human direction, selection, editing, integration, and testing by Vivi / GoAskVivi.

`assets/ai-agent-knowledge-journey.png` was generated with OpenAI ImageGen on 2026-08-20 from a human-authored art direction and two earlier project-owned AI-generated reference boards. A second ImageGen edit on 2026-08-21 produced `assets/ai-agent-knowledge-prestroke.png`, which removes the completed river so the code-driven ink stroke can visibly create it. Vivi selected the composition and approved its visual direction; both published files were resized to native 1080×1920, then combined with original HTML, SVG, CSS, JavaScript animation, and exact English knowledge copy. No reference image contained a third-party library, dataset, logo, font file, or identified artist style. The exact prompts, input-reference hashes, selected-output hashes, and published-asset hashes are recorded in [`references/image-generation-record.md`](references/image-generation-record.md).

Under the applicable [OpenAI Terms of Use](https://openai.com/policies/terms-of-use/), output rights are assigned to the user to the extent permitted by law. Output may not be unique, and the publisher remains responsible for lawful use and human review.

No claim is made that purely machine-generated material receives copyright protection in every jurisdiction. To the extent a component is not copyrightable, the MIT permission still states the publisher's intent not to restrict reuse of that component.

## Social-preview build provenance

`assets/social-preview.png` is a flattened rendition produced by `scripts/generate_social_preview.py` from a human-directed layout, exact code-rendered text, and the disclosed `assets/ai-agent-knowledge-journey.png` background. The legacy `assets/social-preview.svg` remains a safe code-authored reference, but it is not the source of the current PNG.

The maintainer-only generator uses [Pillow](https://github.com/python-pillow/Pillow), which is available under the [HPND License](https://github.com/python-pillow/Pillow/blob/main/LICENSE). Pillow is not vendored and is not required to run the website or Skill.

The current local rendition used macOS-provided Georgia, Arial, and Songti typefaces. Their font software is not copied or distributed in this repository, and the MIT License does not relicense that software. Contributors regenerating the PNG are responsible for having lawful access to their chosen fonts; they may substitute licensed fonts without changing the runtime package.

## Third-party material

No third-party library, font file, stroke dataset, or repository source code is vendored in this release. The build-tool and system-font disclosures above do not add runtime dependencies. `references/open-source-notes.md` is otherwise a research list only. If a contributor adds a dependency or asset, its source, license, and redistribution terms must be recorded before merge.

## Names and endorsement

The MIT License covers the repository materials, not a right to imply endorsement. The names `GoAskVivi` and `Vivi`, associated logos, and brand identity may not be used to suggest sponsorship or endorsement without separate written permission. Factual attribution is allowed.

## Contributions

Unless a pull request states otherwise before acceptance, contributions are submitted under the repository's MIT License.

This file explains the repository's intended rights boundary; it is not legal advice and local law may differ.
