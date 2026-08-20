# Reverse-Engineering Notes

All findings below are evidence scoped. Structural facts and semantic interpretations are tracked separately.

## Confirmed across relevant sources

- `CONFIRMED`: DragonByteZ recognizes Buu's Fury USA revision 0 by 8 MiB size, `BG3E`, and revision byte 0, but performs no cryptographic whitelist check. Evidence: `spicybung/DragonByteZ@b2691209fa873cc0c1d7aa9cdea7c1da4430afe4`, `src/rom.cpp`, profile construction around line 79 and ROM validation in `Rom::load`.
- `CONFIRMED`: DragonByteZ treats GBA ROM pointers as values at or above `0x08000000`, subtracts that base, and bounds-checks against loaded size. Evidence: same commit, `src/rom.cpp`, `Rom::is_rom_pointer` and `Rom::pointer_to_offset`.
- `CONFIRMED`: DragonByteZ's current map research uses a `0x38`-byte `MapEntry`. Evidence: same commit, `src/analysis.cpp:462-624`, `MapEntry` and `read_map_entries`.
- `CONFIRMED`: in that implementation, byte fields occupy the beginning, pointer-bearing fields are read through `+0x10` to `+0x20`, music is at `+0x24`, and variation/entry/exit script references occupy `+0x28` through `+0x34`. This is upstream implementation evidence, not yet an independent byte-exact proof for every Buu profile.
- `CONFIRMED`: DragonByteZ's Buu profile uses a map table offset `0x08E2E0` with 452 entries and a global atlas table at `0x179764` with 187 records. Evidence: same commit, `src/rom.cpp`, Buu profile initialization. The map table metadata is now configured only for `buus_fury_usa_rev0_01c1707f`; it must not transfer to another hash without validation.
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

## Buu's Fury MapEntry

ROM-002 targets only `buus_fury_usa_rev0_01c1707f`.

### Table structure

- `CONFIRMED`: table GBA address `0x0808E2E0`, file offset `0x0008E2E0`.
- `CONFIRMED`: 452 fixed records, no terminator, with stride and record size `0x38`.
- `CONFIRMED`: table range `[0x0008E2E0, 0x000945C0)` is within the 8 MiB target ROM.
- `CONFIRMED`: multi-byte values in the DragonByteZ interpretation are little-endian `u32` values.

Primary implementation evidence is `spicybung/DragonByteZ@b2691209fa873cc0c1d7aa9cdea7c1da4430afe4`: `src/rom.cpp:76-92` (`buus_fury_usa_rev0`), `src/rom.cpp:118-130` (`Rom::u16` and `Rom::u32`), and `src/analysis.cpp:578-622` (`read_map_entries`). Independent profile-scoped evidence comes from a read-only inspection of the verified local ROM: Thumb code at file offset `0x0089FC` loads literal `0x0808E2E0` from `0x008A58`, advances by `0x38`, and uses a helper at `0x0125E0` that returns `0x1C4`. The code is preserved by `extern/buusfury/asm/buu.s:6-11`; the table is inside the unresolved `INCBIN` range documented by `extern/buusfury/build.bat:28-38` and `asm/rest_of_the_game.s:8-12` at commit `cc53d0cd2d1c167e749419187e2d92017ac07468`.

The disassembly corroborates the table address, stride, count, and byte accesses at `+0x00` and `+0x01`. It does not independently establish the remaining field meanings. Names ending in `_raw` deliberately preserve that limitation.

### Physical record layout

| Offset | Width | Internal name | Interpretation | Layout | Semantics | Evidence |
|---:|---:|---|---|---|---|---|
| `0x00` | 1 | `output_raw` | DragonByteZ `output` label | `CONFIRMED` | `INFERRED` | `read_map_entries`; raw code accesses byte `+0x00` |
| `0x01` | 1 | `zone_raw` | DragonByteZ `zone` label | `CONFIRMED` | `INFERRED` | `read_map_entries`; raw code accesses byte `+0x01` |
| `0x02` | 1 | `area_raw` | DragonByteZ `area` label | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x03` | 1 | `variation_raw` | DragonByteZ `variation` label | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x04` | 1 | `trigger_count_raw` | Upstream-labelled count | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x05` | 1 | `script_count_raw` | Upstream-labelled count | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x06` | 1 | `item_count_raw` | Upstream-labelled count | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x07` | 1 | `object_count_raw` | Upstream-labelled count | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x08` | 1 | `npc_count_raw` | Upstream-labelled count | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x09` | 1 | `flags_raw` | Upstream-labelled flags byte | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x0A` | 1 | `unknown_0a` | Unknown byte | `CONFIRMED` | `UNKNOWN` | `read_map_entries` |
| `0x0B` | 1 | `unknown_0b` | Unknown byte | `CONFIRMED` | `UNKNOWN` | `read_map_entries` |
| `0x0C` | 4 | `unknown_0c` | Unknown little-endian word | `CONFIRMED` | `UNKNOWN` | `read_map_entries`, `Rom::u32` |
| `0x10` | 4 | `triggers_pointer_raw` | Upstream-labelled raw pointer word | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x14` | 4 | `scripts_pointer_raw` | Upstream-labelled raw pointer word | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x18` | 4 | `items_pointer_raw` | Upstream-labelled raw pointer word | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x1C` | 4 | `objects_pointer_raw` | Upstream-labelled raw pointer word | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x20` | 4 | `npcs_pointer_raw` | Upstream-labelled raw pointer word | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x24` | 4 | `music_id_raw` | Upstream-labelled music identifier | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x28` | 4 | `variation_script_pointer_raw` | Upstream-labelled raw pointer word | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x2C` | 4 | `variation_array_pointer_raw` | Raw word dereferenced by DragonByteZ as a ROM pointer | `CONFIRMED` | `INFERRED` array meaning | `read_map_entries:610-618` |
| `0x30` | 4 | `entry_script_pointer_raw` | Upstream-labelled raw pointer word | `CONFIRMED` | `INFERRED` | `read_map_entries` |
| `0x34` | 4 | `exit_script_pointer_raw` | Upstream-labelled raw pointer word | `CONFIRMED` | `INFERRED` | `read_map_entries` |

`graphics_pointer` in DragonByteZ is derived by following the word at `+0x2C`; it is not a byte field in the `0x38` record and is not serialized. ROM-002 follows none of these raw pointer words.

## ROM-003 pointer-field census

ROM-003 observes the nine 32-bit pointer-labelled words in every MapEntry for `buus_fury_usa_rev0_01c1707f`. It does not read any target byte. A raw value is `NULL` only when zero, `VALID_ROM_ADDRESS` when the existing checked `GbaRomAddress` converts it to an offset in `[0, 0x800000)`, and `OUT_OF_RANGE` otherwise. Alignment is measured separately and never changes classification. Duplicate references are `valid references - unique valid targets`. Numeric clustering uses 64 KiB file-offset buckets without semantic region names.

### Upstream behavior and confidence

At `spicybung/DragonByteZ@b2691209fa873cc0c1d7aa9cdea7c1da4430afe4`, `src/analysis.cpp:578-622` reads all nine words. Only `variation_array_pointer` is bounds-checked and dereferenced, at `src/analysis.cpp:613-618`, to read one little-endian word. DragonByteZ does not follow the other eight words, combine the five paired counts with them, establish target record sizes, or impose alignment. Its heuristic scanner treats the words as optional ROM-pointer candidates at `src/analysis.cpp:1807-1840`; this is plausibility logic rather than target-format proof.

The pinned Buu disassembly independently confirms only the table base, stride, count, and byte accesses at entry `+0x00/+0x01`. No identified consumer in that evidence loads the nine candidate words. Confidence therefore remains:

- Category B, strongly supported pointer: `variation_array_pointer_raw` only. The pointer behavior is supported by DragonByteZ; the array label and extent remain inferred.
- Category C, upstream-labelled candidate: the other eight fields. Their address distributions support pointer-like shape, not semantic target names.
- Category A, independently confirmed ROM pointer: none.

### Complete census

All 452 entries and nine fields were analyzed: 4,068 observations, comprising 2,827 null values, 1,241 valid in-ROM values, and zero out-of-range values.

| Field | Null | Valid | OOR | Aligned 2 | Aligned 4 | Unique | Duplicate refs | Minimum GBA | Maximum GBA |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `triggers_pointer_raw` | 230 | 222 | 0 | 222 | 222 | 222 | 0 | `0x08072998` | `0x0808E2D0` |
| `scripts_pointer_raw` | 136 | 316 | 0 | 316 | 316 | 316 | 0 | `0x0807293C` | `0x0808E294` |
| `items_pointer_raw` | 399 | 53 | 0 | 53 | 53 | 53 | 0 | `0x08075ADC` | `0x0808DBE0` |
| `objects_pointer_raw` | 440 | 12 | 0 | 12 | 12 | 12 | 0 | `0x08078C98` | `0x0808BE1C` |
| `npcs_pointer_raw` | 437 | 15 | 0 | 15 | 15 | 15 | 0 | `0x08075A44` | `0x0808D434` |
| `variation_script_pointer_raw` | 452 | 0 | 0 | 0 | 0 | 0 | 0 | - | - |
| `variation_array_pointer_raw` | 0 | 452 | 0 | 452 | 452 | 452 | 0 | `0x080728CC` | `0x0808E1E0` |
| `entry_script_pointer_raw` | 285 | 167 | 0 | 166 | 166 | 132 | 35 | `0x08072974` | `0x0808E13C` |
| `exit_script_pointer_raw` | 448 | 4 | 0 | 1 | 1 | 3 | 1 | `0x0807853D` | `0x0807B3C7` |

### Count/pointer correlation

The five pairings remain statistical hypotheses. `0/non` combines valid and out-of-range nonzero words; this ROM has no out-of-range observations.

| Pair | Count 0 / null | Count 0 / non-null | Count >0 / null | Count >0 / valid | Count >0 / OOR |
|---|---:|---:|---:|---:|---:|
| trigger / `triggers_pointer_raw` | 67 | 69 | 163 | 153 | 0 |
| script / `scripts_pointer_raw` | 122 | 277 | 14 | 39 | 0 |
| item / `items_pointer_raw` | 391 | 49 | 8 | 4 | 0 |
| object / `objects_pointer_raw` | 425 | 12 | 15 | 0 | 0 |
| NPC / `npcs_pointer_raw` | 31 | 1 | 406 | 14 | 0 |

These matrices do not support a simple invariant that zero count means null pointer or positive count means non-null pointer. This is an observed contradiction to that simple pairing model, not evidence that the upstream field names are wrong.

### Ranges, clusters, duplicates, and anomalies

- Every valid target falls in the 64 KiB file-offset buckets beginning at `0x070000` or `0x080000`; collectively the observed range is `0x0728CC..0x08E2D0`.
- Six fields with valid observations have no duplicate targets: triggers, scripts, items, objects, NPCs, and variation arrays. `entry_script_pointer_raw` has 167 valid references to 132 unique values; `0x08083E00` occurs 24 times, while `0x0807C4BC` and `0x0807C6B4` occur six times each.
- `exit_script_pointer_raw` has four valid references to three unique values. `0x0807B3C7` occurs twice.
- Four valid values are not 2-byte aligned and are retained unchanged: entry 81 `entry_script_pointer_raw = 0x08076C3F`; entry 103 `exit_script_pointer_raw = 0x0807853D`; entries 146 and 310 `exit_script_pointer_raw = 0x0807B3C7`.
- `variation_script_pointer_raw` is null in all 452 records. `variation_array_pointer_raw` is valid and 4-byte aligned in all 452, with 452 unique targets. Neither observation proves target semantics.
- No address bit is masked, cleared, aligned, or normalized by the census.

## GBARecomp boundary

Generated C/C++ is behavioral evidence only. The pinned framework explicitly directs fixes into analyzer/emitter code followed by regeneration (`mstan/gbarecomp@6571cb39858af70d691914132f81b01a4558d815`, `README.md:248-250`). Useful future surfaces include TCP debug queries, snapshots, IO traces, reverse-debug rings, symbol mapping, and strict-static coverage. None is canonical editable game source for this project.

## Unresolved after ROM-002

- Semantic meaning of every `_raw` field above, especially `output`, `zone`, `area`, `variation`, counts, flags, `music_id`, and pointer target types.
- Whether offsets and generated behavior from the `DCF23468` recomp profile transfer to `01C1707F`. They must currently be treated as incompatible.
- Semantics of unknown structure bytes and incomplete script opcodes.
- Portable compression integration and exact compatibility with Webfoot's streams.
