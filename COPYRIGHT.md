# Copyright, license, and provenance

## Copyright notice

Copyright © 2026 Vivi (GoAskVivi).

## License scope

The repository's source code, `SKILL.md`, documentation, schemas, tests, code-authored SVG/CSS/JavaScript visuals, the published preview renditions (`assets/social-preview.png`, `assets/inkbrush-motion-demo.gif`, `assets/inkbrush-ai-agent-12s.mp4`, `assets/inkbrush-ai-agent-12s-contact-sheet.png`, `assets/nine-action-proof.png`, and all `assets/evidence/*.png` frames and crops), the selected AI-assisted demo backgrounds (`assets/ai-agent-knowledge-journey.png`, `assets/ai-agent-knowledge-prestroke.png`, and `assets/ai-agent-knowledge-cleanplate.png`), the approved real-brush reference (`assets/reference/real-brush-gray-linen.png`), the active v5 ImageGen source sheet (`assets/reference/brush-hand-sheet-v5.png`), the active photographic-looking v5 sprites (`assets/brush-poses-v5/pose-01.png` through `pose-09.png` plus the byte-identical static-evidence copy `assets/brush-pose-final.png`), and the historical v2–v4 brush sprites are licensed under the MIT License in `LICENSE`, to the extent those materials are copyrightable and controlled by the publisher.

The MIT License allows commercial use, copying, modification, distribution, sublicensing, and sale. Copies or substantial portions must retain the copyright and license notice. The work is provided without warranty.

## AI-assistance disclosure

This project was developed with AI-assisted research, image generation, and coding under human direction, selection, editing, integration, and testing by Vivi / GoAskVivi.

`assets/ai-agent-knowledge-journey.png` was generated with OpenAI ImageGen on 2026-08-20 from a human-authored art direction and two earlier project-owned AI-generated reference boards. ImageGen edits on 2026-08-21 produced `assets/ai-agent-knowledge-prestroke.png`, which removes the completed river, and `assets/ai-agent-knowledge-cleanplate.png`, which removes the fixed hand and brush so the code-driven stroke and nine-pose painter can visibly create the journey. The active v5 brush source sheet was generated with ImageGen from human-authored nine-action requirements, then selected, chroma-keyed, aligned, and converted into deterministic full-frame sprites. Eight states preserve their source photographic-looking bristles; PRESS uses a disclosed raster-only axial compression of the photographed pixels so the lower-third splay remains readable at GitHub size. No vector or code-drawn nib is pasted into v5. The hand is synthetic visual media, not a claim that an identified real person performed or painted the lesson. Exact English knowledge copy remains code-native. No reference image contained a third-party library, dataset, logo, font file, or identified artist style. Generation records, selected-output hashes, published-asset hashes, and local post-processing steps are recorded in [`references/image-generation-record.md`](references/image-generation-record.md).

Under the applicable [OpenAI Terms of Use](https://openai.com/policies/terms-of-use/), output rights are assigned to the user to the extent permitted by law. Output may not be unique, and the publisher remains responsible for lawful use and human review.

No claim is made that purely machine-generated material receives copyright protection in every jurisdiction. To the extent a component is not copyrightable, the MIT permission still states the publisher's intent not to restrict reuse of that component.

## Social-preview build provenance

`assets/social-preview.png` is a flattened rendition produced by `scripts/generate_social_preview.py` from a human-directed layout, exact code-rendered text, and the disclosed `assets/ai-agent-knowledge-journey.png` background. The legacy `assets/social-preview.svg` remains a safe code-authored reference, but it is not the source of the current PNG.

The maintainer-only generator uses [Pillow 11.3.0](https://github.com/python-pillow/Pillow/tree/11.3.0), which is available under the [MIT-CMU License](https://github.com/python-pillow/Pillow/blob/11.3.0/LICENSE). Pillow is not vendored and is not required to run the website or Skill.

The current local rendition used macOS-provided Georgia, Arial, and Songti typefaces. Their font software is not copied or distributed in this repository, and the MIT License does not relicense that software. Contributors regenerating the PNG are responsible for having lawful access to their chosen fonts; they may substitute licensed fonts without changing the runtime package.

## Animated README preview provenance

`assets/inkbrush-motion-demo.gif` is a deterministic proof render of the repository's live 9:16 demo contract. It contains the disclosed AI-assisted clean plate and nine-action hand/brush sprites, exact code-native English knowledge text, and the same route and timing used by the SVG/CSS/JavaScript motion shown on GitHub Pages. The source-file hashes, frame count, dimensions, output hash, and render recipe are recorded in [`references/readme-animation-record.md`](references/readme-animation-record.md).

The maintainer-only proof renderer used [Pillow 11.3.0](https://github.com/python-pillow/Pillow/tree/11.3.0). Pillow and the macOS system fonts used to flatten the English text are not included in the repository and are not required to view or reuse the GIF.

## 12-second MP4 example provenance

`assets/inkbrush-ai-agent-12s.mp4` is a 1080×1920, 30 fps, silent H.264 delivery example rendered from the same disclosed clean plate, v5 sprites, route, ink behavior, and code-native English knowledge copy. `assets/inkbrush-ai-agent-12s-contact-sheet.png` contains three exact review times from that composition. The source identity, render recipe, dimensions, duration, and hashes are recorded in [`references/readme-animation-record.md`](references/readme-animation-record.md).

The maintainer-only renderer `scripts/render_12s_example.py` uses Pillow 11.3.0 and the FFmpeg 7.1 executable supplied by imageio-ffmpeg 0.6.0. The exact local executable was built with `--enable-gpl --enable-libx264`, so that combined tool is governed by GPL version 2 or later; libx264's source is GPL version 2. imageio-ffmpeg's Python wrapper is BSD-2-Clause. The [FFmpeg legal page](https://ffmpeg.org/legal.html), [FFmpeg 7.1 source](https://ffmpeg.org/releases/ffmpeg-7.1.tar.xz), [x264 source and COPYING file](https://code.videolan.org/videolan/x264/-/blob/master/COPYING), and the exact package/tool identity are recorded in [`references/copyright-and-provenance.md`](references/copyright-and-provenance.md). Those build tools, binaries, and the macOS system fonts used to flatten the text are not included and are not runtime dependencies of the website or Skill.

The GPL applies to the external encoder executable, not as a relicensing claim over the separately encoded MP4 content. H.264 implementation or distribution can also involve patent obligations in some jurisdictions; this repository does not grant a patent license. Contributors are responsible for the rules that apply to their own use and distribution.

## Third-party material

No third-party library, executable, font file, stroke dataset, or repository source code is vendored in this release. The pinned maintainer requirements download external build tools separately; their source and license records appear below and do not add browser or Skill runtime dependencies. `references/open-source-notes.md` is otherwise a research list only. If a contributor adds a dependency or asset, its source, license, and redistribution terms must be recorded before merge.

## Names and endorsement

The MIT License covers the repository materials, not a right to imply endorsement. The names `GoAskVivi` and `Vivi`, associated logos, and brand identity may not be used to suggest sponsorship or endorsement without separate written permission. Factual attribution is allowed.

## Contributions

Unless a pull request states otherwise before acceptance, contributions are submitted under the repository's MIT License.

This file explains the repository's intended rights boundary; it is not legal advice and local law may differ.
