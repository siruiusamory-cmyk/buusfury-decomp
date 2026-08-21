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

## ROM-004 variation-array first-word analysis

ROM-004 performs one deliberately bounded dereference for `buus_fury_usa_rev0_01c1707f`. For every MapEntry it validates `variation_array_pointer_raw`, converts it through `GbaRomAddress`, requires `file_offset + 4 <= ROM size`, reads exactly `target[0x00:0x04]`, and decodes one explicit little-endian unsigned word named `first_word_raw`. It does not read a second word, inspect neighboring bytes, infer a record size, or follow the observed value.

### Evidence and confidence

At `spicybung/DragonByteZ@b2691209fa873cc0c1d7aa9cdea7c1da4430afe4`, `src/analysis.cpp:578-621` function `read_map_entries` validates the raw `+0x2C` value, converts it to a file offset, requires four in-bounds bytes, and calls `Rom::u32` once at target `+0x00`. `src/rom.cpp:124-130` proves that `Rom::u32` decodes four bytes little-endian; `src/rom.cpp:138-147` establishes its ROM-address check and conversion. DragonByteZ then calls the result `graphics_pointer` and attempts a level-record parse in `src/analysis.cpp:687-719`. That downstream name and target interpretation are upstream behavior, not independently proven game semantics.

The pinned disassembly `2genkidev/buusfury@cc53d0cd2d1c167e749419187e2d92017ac07468` preserves both relevant executable and target regions as unresolved `INCBIN` data (`asm/buu.s:6-11`, `asm/rest_of_the_game.s:8-12`, and `build.bat:28-38`). No identified consumer independently corroborates a MapEntry `+0x2C` load followed by target `+0x00`. There is no conflicting evidence.

- Source-pointer confidence: **INFERRED, strongly behaviorally supported**. All 452 values are unique, aligned, and valid in-ROM, and DragonByteZ validates and uses them.
- First-word structural confidence: **CONFIRMED as an evidence-backed tool access**. The exact four-byte read, bounds rule, and little-endian width are explicit in DragonByteZ and reproduced safely here. Runtime game consumption remains independently unconfirmed.
- First-word semantic confidence: **UNKNOWN**. `first_word_raw` is deliberately not called a graphics pointer, ID, flags word, or record reference.

### Complete first-word census

All 452 source values were valid in-ROM addresses, none were null or out of range, and all 452 were unique. Exactly 452 four-byte reads succeeded with zero bounds failures.

| Measure | Result |
|---|---:|
| Zero first words | 0 |
| Nonzero first words | 452 |
| Unique raw values | 421 |
| Duplicate references | 31 |
| Distinct repeated values | 11 |
| Minimum raw value | `0x0817B1B0` |
| Maximum raw value | `0x082B8C38` |
| ROM-address-shaped | 452 |
| Non-ROM values | 0 |
| Odd nonzero values | 0 |
| 2-byte aligned nonzero values | 452 |
| 4-byte aligned nonzero values | 452 |

`ROM-address-shaped` is a numeric classification only. It does not promote any of the 452 words to a confirmed pointer. The most frequent raw values are `0x0822CC08` (10 observations), `0x0829C2D8` (5), `0x0822DBC4` (4), `0x0822DF88` (4), and `0x08228290` (3).

### Source-address ordering and spacing

The 452 source variation-array addresses are strictly increasing by MapEntry index: 451 increases, zero decreases, and zero equal neighbors. Positive deltas range from `0x4` to `0xD08`. The most common signed deltas are `+0x4` (48), `+0x70` (17), `+0x4C` (12), `+0x94` (12), and `+0xDC` (11). These spacings are observations only and do not establish an array or record length.

### Raw metadata correlations

The 11 duplicated `first_word_raw` groups were compared with four raw MapEntry bytes. `Same` means every observation in a duplicated first-word group had one metadata value; `Vary` means at least two metadata values occurred.

| Raw field | Duplicate groups | Same | Vary | Unique `(first word, metadata)` pairs |
|---|---:|---:|---:|---:|
| `output_raw` | 11 | 11 | 0 | 421 |
| `zone_raw` | 11 | 0 | 11 | 452 |
| `area_raw` | 11 | 11 | 0 | 421 |
| `variation_raw` | 11 | 10 | 1 | 422 |

These correlations do not establish what either side means. In particular, they do not prove that `first_word_raw` is a map variation ID or that repeated values identify a shared structure.

### Unresolved

The runtime consumer, semantic type, reason every value is ROM-address-shaped, target alignment contract, second and later words, array length, and any formal relationship to MapEntry raw metadata remain unknown. ROM-004 intentionally gathers no adjacent target data to answer them.

## Executable Consumer Analysis

ROM-005 identified Thumb resolver `0x080089CC` in the verified ROM. It loads MapEntry `+0x2C`, indexes a word at `source + 4 * (selector - 1)`, and therefore consumes `first_word_raw` when selector is `1`. ROM-006 raises that result to Level 3 with frame-synchronized mGBA routes from reset and two exact runtime captures:

| MapEntry | Source | Expected/observed `first_word_raw` | Resolver caller |
|---:|---:|---:|---:|
| 1 | `0x080728D4` | `0x082B5FA0` | `0x0800906A` |
| 4 | `0x080728E0` | `0x082B5B2C` | `0x0800906A` |

At `0x080089D4`, both captures had scaled `r1 = 4`, proving original selector `1`; one single-step placed the predicted value in `r0`. The verified ROM hash, size, and mtime were unchanged.

Static ownership analysis shows `0x08009670` loads selected value `+0x40/+0x44`, passes them as count/pointer-array inputs to `0x08012664`, invokes descriptor factories, and appends returned objects to IWRAM registry `0x03002A64`. Neighboring rectangle/bounds queries strongly support a map-load spatial-object/region registry. There is no direct VRAM, palette, OAM, DMA, decompression, or graphics-copy behavior in this path. Exact collision/trigger/activation subtype remains unknown, and the deterministic runtime routes did not hit `0x08009670`, so Level 4 is not claimed.

The field remains `first_word_raw`. Full selector provenance, exact commands, registers, automation-source evidence, subsystem call graph, safety results, and unresolved questions are in [consumer-analysis.md](consumer-analysis.md).

## ROM-007 concrete spatial-object factory

User-provided Higher Plane state starts with runtime MapEntry pointer `0x0808EB30` (index 38). Deterministic 120-frame south input transitions through MapEntry 39 and reproduces full verified chain:

```text
MapEntry 39 / selector 1
  -> variation source 080753F0
  -> first_word_raw 08294968 (runtime = Webfoot)
  -> 08009670: field_40_raw=2, field_44_raw=08294960
  -> 08012664
  -> descriptor 08294948
  -> raw factory 08007675, Thumb fetch 08007674
  -> returned object 0203DEBC
  -> registry slot 03002A68
```

Static instructions show factory `0x08007674` allocates `0x18` bytes and initializes exact signed halfword bounds later consumed by registry AABB queries. Classification is **STRONGLY SUPPORTED: rectangle-aware runtime object**. Collision, trigger, activation, event, and transition semantics remain unknown because bounded spatial callback hit belonged to a different object.

Same count-2 population pass used a second distinct factory (`0x080072CD`, Thumb fetch `0x080072CC`) and inserted a second object at `0x03002A6C`; construction paths are therefore heterogeneous for this active load. Evidence remains Level 3, `first_word_raw` remains unchanged, and no target/descriptor/object parser was added. Full commands, registers, factory initialization, callback blocker, and safety rules are in [consumer-analysis.md](consumer-analysis.md#rom-007-higher-plane-factory-capture).

## ROM-008 exact-object trace

Three bounded Higher Plane replays rediscovered descriptor `0x08294948`, raw factory `0x08007675`, current return `0x0203DEBC`, slot `0x03002A68`, and executable-initialized bounds `(592,136)..(601,241)`. Identity tracking uses a verified probe load epoch, not an assumed internal generation counter. Committed reset at `0x08048488`, committed removal through `0x080126AC`, or a new verified load epoch invalidates the pointer.

No after-guard AABB candidate or callback was captured for that exact object. Static correction established actual query entries `0x080126D4`, `0x080127AE`, and `0x08012846`; addresses `0x080127AC` and `0x08012844` are endpoints, not entries. Direct verified callers are `0x08006E4E`, `0x08021DFE`, `0x08021E06`, `0x08012AEC`, and `0x08022142`. The entry-level replay needed to identify the rejecting guard was blocked when the environment rejected further mGBA launches at its approval quota.

Semantic classification therefore stays **STRONGLY SUPPORTED: 24-byte rectangle-aware runtime object**, at Level 3. Parser readiness is **NO**; one exact current-load-epoch AABB/callback and downstream consequence remains required. The runtime helper adds fail-closed identity/timeline validation only and introduces no ROM structure parser. Full evidence and safety details are in [consumer-analysis.md](consumer-analysis.md#rom-008-exact-object-behavior-trace).

## GBARecomp boundary

Generated C/C++ is behavioral evidence only. The pinned framework explicitly directs fixes into analyzer/emitter code followed by regeneration (`mstan/gbarecomp@6571cb39858af70d691914132f81b01a4558d815`, `README.md:248-250`). Useful future surfaces include TCP debug queries, snapshots, IO traces, reverse-debug rings, symbol mapping, and strict-static coverage. None is canonical editable game source for this project.

## Unresolved after ROM-002

- Semantic meaning of every `_raw` field above, especially `output`, `zone`, `area`, `variation`, counts, flags, `music_id`, and pointer target types.
- Whether offsets and generated behavior from the `DCF23468` recomp profile transfer to `01C1707F`. They must currently be treated as incompatible.
- Semantics of unknown structure bytes and incomplete script opcodes.
- Portable compression integration and exact compatibility with Webfoot's streams.
