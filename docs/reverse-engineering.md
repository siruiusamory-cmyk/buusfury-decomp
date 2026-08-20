# Reverse-Engineering Notes

All findings below are evidence scoped. They are research input for later tickets, not implemented formats in Phase 0.

## Confirmed across relevant sources

- `CONFIRMED`: DragonByteZ recognizes Buu's Fury USA revision 0 by 8 MiB size, `BG3E`, and revision byte 0, but performs no cryptographic whitelist check. Evidence: `spicybung/DragonByteZ@b2691209fa873cc0c1d7aa9cdea7c1da4430afe4`, `src/rom.cpp`, profile construction around line 79 and ROM validation in `Rom::load`.
- `CONFIRMED`: DragonByteZ treats GBA ROM pointers as values at or above `0x08000000`, subtracts that base, and bounds-checks against loaded size. Evidence: same commit, `src/rom.cpp`, `Rom::is_rom_pointer` and `Rom::pointer_to_offset`.
- `CONFIRMED`: DragonByteZ's current map research uses a `0x38`-byte `MapEntry`. Evidence: same commit, `src/analysis.cpp:462-624`, `MapEntry` and `read_map_entries`.
- `CONFIRMED`: in that implementation, byte fields occupy the beginning, pointer-bearing fields are read through `+0x10` to `+0x20`, music is at `+0x24`, and variation/entry/exit script references occupy `+0x28` through `+0x34`. This is upstream implementation evidence, not yet an independent byte-exact proof for every Buu profile.
- `CONFIRMED`: DragonByteZ's Buu profile uses a map table offset `0x08E2E0` with 452 entries and a global atlas table at `0x179764` with 187 records. Evidence: same commit, `src/rom.cpp`, Buu profile initialization. These addresses are not present in Phase 0 application configuration and must not transfer to another hash without validation.
- `CONFIRMED`: DragonByteZ implements stored and custom compressed containers in `src/compression.cpp`; `src/analysis.cpp` also contains a BIOS LZ77 decoder. Presence of the latter does not prove that a particular map asset uses BIOS LZ77.
- `CONFIRMED`: the pinned disassembly expects SHA-1 `f1c4b07554d2a3b1ad2f325307051e775ce68087`, matching the local ROM exactly. Evidence: `2genkidev/buusfury@cc53d0cd2d1c167e749419187e2d92017ac07468`, `README.md:6`, plus the reproducible local identification recorded in `docs/hash-investigation.md`.
- `CONFIRMED`: the pinned Buu recomp expects SHA-1 `e65738e9d67688309f09811a54f495523ec9aada`, which does not match the local ROM. Evidence: `mstan/DragonBallZBuusFuryRecomp@453a913a9f67916b9b358776da1c1229b09a6c80`, `baserom.md:13`.

## Legacy repository evidence

- `CONFIRMED`: `Arefu/Legacy@d22a556cd33dee56513d5b606b6ae8065ccc5752`, `DBZKit/Bulma/GameDetector.cs`, recognizes only `ALFE`; `Dependencies/DBZLOG2/ALFE.json` supplies a `mapEntries` address without hashes or a revision contract.
- `CONFIRMED`: `DrGero/Types.cs`, `MapEntry.Read`, contains an older `0x38` interpretation. `DrGero/ROM.cs`, `ReadPointer`, masks nonzero top bytes rather than enforcing the narrower ROM range used by DragonByteZ. Treat that pointer behavior as historical tooling, not a safe generic rule.
- `CONFIRMED`: `OpCodes.csv` and `DBZKit/Legacy/Games/BYTECODE_VM.cs` contain 145 opcode slots, many still named as unknown subroutines. Known labels are useful research leads; unresolved labels and operand questions remain unknown.
- `CONFIRMED`: `DBZKit/Assets/Dialog.cs` contains explicit TODOs and guessed handling for some compressed/jump modes. It is not authoritative proof for Buu's Fury.
- `UNKNOWN`: no machine-readable, source-linked character ID mapping was established from the repository's `Character IDs` images.
- `UNKNOWN`: no tracked textual Zenkai-specific evidence was found in the audited revision.

## Disassembly reconstruction boundary

- `CONFIRMED`: the disassembly retains large original byte ranges through `INCBIN`. Evidence: `build.bat:27-35`, `asm/buu.s`, `asm/GBARam.s`, and `asm/rest_of_the_game.s` at commit `cc53d0c...`.
- `CONFIRMED`: reconstructed pieces include startup/header assembly, a partial allocator, RAM reservations, `src/color_transforms.cpp`, and `src/strings.cpp`; large regions remain preserved binary.
- `INFERRED`: fixed scatter addresses and hard-sized compressed replacements indicate strong byte-layout constraints. A successful byte-identical build was not independently demonstrated in Phase 0.

## GBARecomp boundary

Generated C/C++ is behavioral evidence only. The pinned framework explicitly directs fixes into analyzer/emitter code followed by regeneration (`mstan/gbarecomp@6571cb39858af70d691914132f81b01a4558d815`, `README.md:248-250`). Useful future surfaces include TCP debug queries, snapshots, IO traces, reverse-debug rings, symbol mapping, and strict-static coverage. None is canonical editable game source for this project.

## Unresolved before ROM-002

- Whether every DragonByteZ `MapEntry` field interpretation is byte-exact for `buus_fury_usa_rev0_01c1707f`.
- Whether offsets and generated behavior from the `DCF23468` recomp profile transfer to `01C1707F`. They must currently be treated as incompatible.
- Semantics of unknown structure bytes and incomplete script opcodes.
- Portable compression integration and exact compatibility with Webfoot's streams.
