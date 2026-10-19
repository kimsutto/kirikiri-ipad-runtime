# Third-party code and provenance

Original build helpers, the neutral demo, publication checks and platform additions are MIT licensed. This repository does not claim authorship of its underlying engine or plugins. Existing source headers and license terms remain authoritative.

## Source layout

`upstream.json` pins Kirikiri SDL2 to commit `124bdf841f09e7ce02aa99b7b55791a0f7a900ff`. `tools/prepare.py` fetches that commit and the recursive submodule commits recorded by it, then copies the `overlay/` source files on top. The overlay contains complete modified source files, not binary patches. It does not contain game scripts or game assets.

| Files | Provenance / license |
|---|---|
| `overlay/CMakeLists.txt`, core engine files and bundle template | [Kirikiri SDL2](https://github.com/krkrsdl2/krkrsdl2/tree/124bdf841f09e7ce02aa99b7b55791a0f7a900ff), MIT; see `licenses/Kirikiri-SDL2.txt` |
| `overlay/external/krkrz/sound/` | [Kirikiri Z](https://github.com/krkrsdl2/krkrz/tree/b11c43a07543756fcb943a60ff0a949a7f470f10), BSD-style conditions and bundled component notices; see `licenses/Kirikiri-Z.txt` |
| Built-in KAG parser, ncbind, AlphaMovie and transition plugins | [KRKR-ns plugin sources](https://github.com/DrFlyingPig/krkr-ns/tree/929aecdbf6388b6100e4d79a78edbe5079b19721/krkrsdl2/src/plugins), adapted for this engine. Preserve `overlay/src/plugins/LICENSE.krkr-ns`, per-file upstream copyrights, and both `LICENSE.krkrsdl3` notices. Upstream-derived code keeps its original terms. |
| `RuntimePaths.mm`, `RuntimeVideo.*`, `RuntimeVorbisDecoder.cpp`, `AudioCompletions.h` and original tests | Original MIT-licensed platform additions; Vorbis decoding calls the existing FAudio stb_vorbis implementation |
| Demo font, obtained during preparation | Unmodified `DejaVuSansMono-Bold.ttf` from the pinned ANGLE submodule `f82b1b4dc548dc8325ec83c11cd2363f3656a894`; Bitstream/DejaVu/Arev terms in `licenses/DejaVu-Fonts.txt`, [official license](https://dejavu-fonts.github.io/License.html) |

The pinned source tree also contains SDL2, FAudio, simde, zlib, FreeType, libjpeg-turbo, libpng, libogg, Opus, opusfile, Oniguruma, jxrlib, ANGLE and their dependencies. They retain separate licenses in the fetched tree. The preparation script preserves these files and copies license notices into the bundled demo resources. Redistributing a compiled application requires preserving the notices for the components included in that build; the top-level MIT license does not replace them.

A one-line modern-Apple-SDK compatibility fix in `overlay/external/krkrz/external/freetype/src/gzip/zconf.h` retains its original zlib notice. FreeType notice: `licenses/FreeType.txt`; its embedded gzip code retains the zlib terms.

## Changes in this repository

- Static parser/transition/transparent-movie plugins and a Vorbis decoder.
- Audio completion dispatch moved out of the realtime callback; generation tracking rejects stale completions after a stream is reset.
- iOS AVPlayer overlay with real completion notification, and pause/resume on app activation changes.
- UIKit activation callbacks forwarded to the script runtime. The imported game's scripts remain responsible for what they save.
- Native `System.confirm` support. Existing games must call this API or supply an appropriate local compatibility adapter; Windows modal dialogs are not automatically rewritten.
- Generic `Documents/Game` and `Documents/Saves` paths, a configurable bundle identifier and a neutral demo.

Neither the engine projects nor game publishers are represented as endorsing this repository. No proprietary game-specific adapter is included. The license review is based on the pinned upstream notices; it is not a legal clearance for third-party games or modifications supplied by users.
