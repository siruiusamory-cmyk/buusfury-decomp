# Upstream Audit

Audit date: 2026-08-19. Exact revisions are machine-pinned in `upstreams.lock`. License statements describe each inspected tree only; they are not a project-wide compatibility conclusion.

This project's own code is licensed under the Mozilla Public License 2.0, stated in the root `LICENSE`.

## DragonByteZ

### Repository

<https://github.com/spicybung/DragonByteZ>

### Commit

`b2691209fa873cc0c1d7aa9cdea7c1da4430afe4`

### License

MIT, stated in root `LICENSE`. `CONFIRMED`.

### Purpose

Current extraction and reverse-engineering reference for Webfoot's Dragon Ball Z GBA games.

### Relevant files

- `include/dragonbytez/rom.hpp`, `src/rom.cpp`: profiles, ROM loading, identity checks, pointer conversion.
- `src/analysis.cpp`: `MapEntry`, map/level/graphics/audio analysis and extractors.
- `src/compression.cpp`: Webfoot stored/custom decompression.
- `src/log1_runtime.cpp`: LoG1 runtime-assisted extraction.
- `CMakeLists.txt`, `build_windows.bat`: builds.

### ROM support

`CONFIRMED` from `src/rom.cpp`: LoG Europe revision 0 `ALGP`; LoG II Europe revision 0 `ALFP`; LoG II USA revision 0 `ALFE`; Buu's Fury USA revision 0 `BG3E`. Each must be 8 MiB with revision byte 0. No CRC, MD5, SHA-1, or SHA-256 whitelist exists, so recognition is not exact identity.

### Build requirements

C++17, CMake 3.16+, and Visual Studio 2022 C++ workload on Windows. The batch build produces x64 Release GUI and CLI variants. Linux CLI and `ctest` are documented; Win32 UI dependencies make the GUI Windows-specific.

### Useful research

`CONFIRMED`: `src/analysis.cpp`, `read_map_entries`, reads a `0x38` map record; Buu's profile reports 452 entries at `0x08E2E0`. `parse_level_record` follows graphics records and atlas data. Extraction covers compressed atlases, tilesets, map previews, and Buu music records. `src/compression.cpp` has stronger bounds checks than the historical Legacy JCALG1 ports.

### Limitations

Header/size identity is revision-risky. LoG1 extraction relies partly on an embedded runtime and explicitly does not reconstruct complete map records. Some layer semantics remain research. A profile field named `level_record_tileset_pointer_offset` differs from offsets directly read by `parse_level_record`; validate before reuse.

Optional local build validation did not complete: the PATH CMake exposed no Visual Studio generator, while native CMake 4.4.2 selected the Windows SDK but reported no C++ compiler in the non-developer-shell environment. Visual Studio Build Tools and `cl.exe` are installed, so this is a developer-environment/configuration limitation, not evidence of a DragonByteZ source failure.

### Confidence

Implementation behavior is `CONFIRMED` for this commit. Applicability to another hash is `UNKNOWN` until independently validated.

## Arefu/Legacy

### Repository

<https://github.com/Arefu/Legacy>

### Commit

`d22a556cd33dee56513d5b606b6ae8065ccc5752`

### License

No root license found. `DBZKit/Dependencies/JCALG1/LICENSE` is MIT for that dependency only. Repository-owned code, documents, images, and ROM-derived artifacts have unclear licensing. `UNKNOWN`.

### Purpose

Historical/community research spanning the trilogy: DBZKit, DrGero, opcodes, scripting, maps, graphics, and assorted research artifacts.

### Relevant files

- `OpCodes.csv`, `DBZKit/Legacy/Games/BYTECODE_VM.cs`: opcode names and VM research.
- `DBZKit/Bulma/GameDetector.cs`, `Dependencies/DBZLOG2/ALFE.json`: limited ROM detection/config.
- `DrGero/Types.cs`, `DrGero/ROM.cs`: older map and pointer interpretation.
- `DBZKit/Assets/Maps.cs`, `Sprites.cs`, `Items.cs`, `Dialog.cs`: extraction/research tools.
- `DBZKit/DBZKit/JCALG1.cs`, `DrGero/JCALG1.cs`: decompression ports.

### ROM support

Practical detector evidence is limited to `ALFE`, with no cryptographic hash, revision, or length verification. Other documents claim broader trilogy research but do not establish precise supported profiles. `CONFIRMED` detector behavior; broader compatibility `UNKNOWN`.

### Build requirements

Current projects target `.NET 10.0` and Windows variants; WinForms, WebView2, ScintillaNET, Antlr runtime, and a COM reference appear across projects. No verified end-to-end build procedure was found.

### Useful research

`OpCodes.csv` enumerates 145 slots with many unknown `sub_*` entries. DBZKit contains map, asset, dialog, script, and JCALG1 experiments. `ROM Code/String_DASM.asm` documents decompressor code recovered from RAM. Hard-coded addresses provide research leads for their apparent profile, not portable constants.

### Limitations

Many TODOs, guesses, incomplete configs, images without machine-readable ID provenance, and unsafe pointer masking. LoG II findings must not be promoted to Buu's Fury facts. No verified Zenkai-specific textual source was found. Public availability does not resolve the absent license.

### Confidence

Tool behavior and file contents are `CONFIRMED`; game/revision scope and incomplete semantic claims remain `INFERRED` or `UNKNOWN`.

## 2genkidev/buusfury

### Repository

<https://github.com/2genkidev/buusfury>

### Commit

`cc53d0cd2d1c167e749419187e2d92017ac07468`

### License

No root license found. The pinned JCALG1 submodule has its own MIT license; that does not license the whole repository. `UNKNOWN`.

### Purpose

Partial Buu's Fury disassembly/build research and source of historical compression/graphics tooling.

### Relevant files

- `README.md`: base SHA-1 and proprietary tool requirements.
- `build.bat`, `scatter.ld`: extraction, fixed layout, link/build flow.
- `asm/rom_header.s`: title/code/maker/revision/header checksum.
- `asm/buu.s`, `asm/GBARam.s`, `asm/rest_of_the_game.s`: reconstructed code mixed with `INCBIN` ranges.
- `tools/compress/CMakeLists.txt`, `tools/compress/main.cpp`: JCALG1 wrapper.

### ROM support

Expected base SHA-1: `f1c4b07554d2a3b1ad2f325307051e775ce68087`. Build layout consumes 8 MiB. Reconstructed header specifies `DBZBUUSFURY`, `BG3E`, maker `70`, revision 0, checksum `0x84`. The local ROM matches this SHA-1 exactly.

### Build requirements

ARM Developer Suite 1.2 (`armasm`, `armcpp`, `armlink`, `fromelf`, and documented `tcpp`), `grit`, CMake, and a matching user-supplied base ROM. ARM Developer Suite is proprietary and was not installed. `grit` was not found locally.

### Useful research

Fixed ROM/RAM scatter layout, selected reconstructed source, named preserved regions, graphics conversion flow, and a JCALG1 compression wrapper. `build.bat` extracts nine original ranges; very large areas remain untouched binary.

### Limitations

No verified full build in Phase 0. The compression target links a prebuilt Win32 x86 JCALG1 library and did not configure with the available x64-only environment. Build configuration mixes Release generation with a Debug executable path. Large `INCBIN` regions are not source reconstruction. Output byte identity is not enforced because the comparison step is commented out.

### Confidence

Base contract and build behavior are `CONFIRMED`. Byte-identical build success and provenance of the base image remain `UNKNOWN`.

## mstan/gbarecomp

### Repository

<https://github.com/mstan/gbarecomp>

### Commit

`6571cb39858af70d691914132f81b01a4558d815`

### License

PolyForm Noncommercial 1.0.0, root `LICENSE`. `CONFIRMED`. Commercial reuse is restricted; obtain legal review before integrating code.

### Purpose

Experimental GBA static recompilation, hardware runtime, differential/debug tooling, and generated native code.

### Relevant files

- `src/armv4t/`: decode, IR, analysis, interpretation, and emission.
- `src/gba/`: hardware model.
- `src/runtime/`: dispatch and healing cache.
- `src/debug/`, `TCP.md`: TCP debugger, traces, snapshots, reverse debug.
- `docs/ARCHITECTURE.md`, `README.md`: architecture and generated-code policy.

### ROM support

Framework support is configuration-driven. Game repositories below establish exact targets; the framework does not make those ROMs redistributable.

### Build requirements

CMake/Ninja and a modern C++ toolchain. Audited game projects document MSYS2 MinGW64 and SDL2 for their native builds.

### Useful research

TCP queries, snapshots, IO traces, reverse-debug call/store/block rings, symbols, dispatch-miss reporting, differential workflows, and `GBARECOMP_STRICT_STATIC=1` coverage checks.

### Limitations

Experimental and not exhaustively tested. Generated C/C++ is evidence, not editable canonical source. `README.md:248-250` directs fixes into analysis/emission followed by regeneration.

### Confidence

Architecture and documented tooling are `CONFIRMED`; fidelity for any untested game path remains `UNKNOWN`.

## Legacy of Goku recomp

### Repository

<https://github.com/mstan/DragonBallZLegacyOfGokuRecomp>

### Commit

`fbe502a3d44256402262cd3f5baeb072a7235932`

### License

No root license found. Its pinned `gbarecomp` submodule is PolyForm Noncommercial, but that does not establish a license for repository-owned integration files. `UNKNOWN`.

### Purpose

Behavioral/native recompilation research for Dragon Ball Z: The Legacy of Goku.

### Relevant files

`baserom.md`, `game.toml`, `tools/regen.ps1`, `CMakeLists.txt`, `README.md`, and ignored `generated/` output contract.

### ROM support

USA `ALGE`, 8,388,608 bytes, CRC32 `D47CCFF4`, SHA-1 `a3c8c76742f11fc6a3f6e3fcca20992458cac0b5`, SHA-256 `3ba9919e26704b0f5fdc2bfabc7f7a0404c71413761d38abcd94224c3bd4b1b9`. Phase 0 did not establish the header revision byte.

### Build requirements

Pinned GBARecomp/recomp-ui submodules, CMake, Ninja, MSYS2 MinGW64, SDL2, matching ROM, and retail BIOS expected by the project configuration.

### Useful research

Behavioral execution, TCP debug port 19887, snapshots and adaptive-view experiments. Generated output can support observation only.

### Limitations

Experimental preview; ROM/BIOS absent; no root license; revision metadata unresolved; generated code not canonical.

### Confidence

Published hash/config requirements are `CONFIRMED`; full-game behavior is not exhaustively validated.

## Legacy of Goku II recomp

### Repository

<https://github.com/mstan/DragonBallZLegacyofGokuIIRecomp>

### Commit

`add98b5d76fb2b822be870f29fa27b22c9a95631`

### License

No root license found. Pinned framework license does not automatically cover repository-owned files. `UNKNOWN`.

### Purpose

Behavioral/native recompilation research for Dragon Ball Z: The Legacy of Goku II.

### Relevant files

`baserom.md`, `game.toml`, `tools/regen.ps1`, `CMakeLists.txt`, `README.md`.

### ROM support

USA revision 0 `ALFE`, 8,388,608 bytes, CRC32 `204142E1`, MD5 `4e1565aa1f0627c2bf5e51019440cb70`, SHA-1 `18e0715dec419f3501c301511530d2edcd590f8b`, SHA-256 `6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75`.

### Build requirements

Same GBARecomp/SDL2/MSYS2/CMake/Ninja family as above, exact ROM, and configured retail BIOS.

### Useful research

TCP debug port 19888 and strict-static/traversal validation claims can support later behavioral study.

### Limitations

Experimental, not exhaustively tested, no root license, and generated output is not canonical source.

### Confidence

Published identity/config is `CONFIRMED`; wider compatibility is `UNKNOWN`.

## Buu's Fury recomp

### Repository

<https://github.com/mstan/DragonBallZBuusFuryRecomp>

### Commit

`453a913a9f67916b9b358776da1c1229b09a6c80`

### License

PolyForm Noncommercial 1.0.0, root `LICENSE`. `CONFIRMED`.

### Purpose

Behavioral/native recompilation research for Buu's Fury and the principal source of the alternate hash claim.

### Relevant files

- `baserom.md`, `game.toml`: exact identity and recompiler configuration.
- `tools/regen.ps1`: SHA-1 validation and generation.
- `src/buus_fury_extended_view.cpp`, `src/mods/buus_fury_adaptive_view_plugin.cpp`: authored extended-view behavior.
- `CMakeLists.txt`, `README.md`, `TCP.md` through the framework.

### ROM support

USA revision 0 `BG3E`, 8,388,608 bytes, CRC32 `DCF23468`, MD5 `808eda67b17c901e9052f47bdc419e2f`, SHA-1 `e65738e9d67688309f09811a54f495523ec9aada`, SHA-256 `15df2fbbe072cc5d28a699ae9af9c56657e290cdb47c92e57d6ce14a01be4b64`. This does not match the local ROM.

### Build requirements

Pinned GBARecomp/recomp-ui, CMake, Ninja, MSYS2 MinGW64, SDL2, exact ROM, and configured retail BIOS. `tools/regen.ps1` checks SHA-1 before generation.

### Useful research

TCP debug port 19889, strict-static validation, snapshots, IO/reverse-debug instrumentation, and authored visibility/field-streaming modifications.

### Limitations

Hash mismatch blocks transfer of addresses or generated behavior to the local profile without validation. Experimental status, incomplete whole-game testing, noncommercial license, and generated-code boundary all apply.

### Confidence

Exact upstream base requirement is `CONFIRMED`; compatibility with `buus_fury_usa_rev0_01c1707f` is `UNKNOWN` and must not be assumed.
