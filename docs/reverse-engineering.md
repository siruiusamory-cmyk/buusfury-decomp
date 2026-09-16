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

## ROM-009 clean gameplay trace

The newer ignored `.ss1` and `.sav` were identified as 72,775 bytes /
`ea500f3a774d42032202d9c3d7bfb437478417ba37e4b72c634993d7d701ac82`
and 8,192 bytes /
`9bbd7cb67b724fbe1263d9b5b7cedf0a6c935a2ff6448befd0a0348b7607f46a`.
Dynamic runtime discovery reproduced MapEntry 39, descriptor `0x08294948`, raw
factory `0x08007675`, X `0x0203DE7C`, slot `0x03002A68`, and bounds
`(592,136)..(601,241)` in load epoch 1.

No verified query entry, direct caller, query-capable caller entry, internal
guard, exact AABB, or callback executed after X became live. Point-query context
slot `0x03001C34` was raw zero at insertion. Primary classification is
**D. ENVIRONMENT BLOCKED** for this supplied state/route; the causal mechanism
and dialogue hypothesis remain `UNKNOWN` / **UNRESOLVED**. Evidence stays Level
3. Structural parser readiness remains **NO** because descriptor extent/boundary
and a complete lossless field map are not established. Full private-runtime and
safety evidence is in
[consumer-analysis.md](consumer-analysis.md#rom-009-clean-gameplay-exact-object-callback-trace).

## ROM-010 harness and replay result

ROM-010 reproduced the clean replay with machine-detected success through input
verification, one mGBA launch, allowlisted Lua completion, GDB attachment,
breakpoint installation, runtime load, and exact X insertion. The exact runtime
identity matched ROM-009. No known caller entry, query entry, callsite, guard,
AABB, or callback executed after X became live. The earlier state produced the
same post-live boundary in a separate bounded replay.

ROM-010 has **NO VALID A/B/C/D RESULT**: infrastructure succeeds, A/B do not
occur, no rejecting guard supports C, and the ticket forbids D when execution
succeeds. Available inputs do not schedule a known query-capable caller after X
is live. Dialogue remains **UNRESOLVED**, evidence stays Level 3, and parser
readiness remains **NO** because source-descriptor extent/boundary is not
independently established. Full pipeline, runtime, and safety evidence is in
[consumer-analysis.md](consumer-analysis.md#rom-010-runtime-harness-reliability-and-clean-state-replay).

## ROM-011 native mGBA read probe

Stock mGBA 0.10.5 GDB read watchpoints failed the playability gate: the stub
ignored the requested range length, byte coverage required approximately 16
watchpoints, and the generic memory-debugger shim scanned them on ordinary
emulated accesses, reducing gameplay below 1 FPS. This remains negative tooling
evidence, not ROM behavior evidence.

A separate SDL mGBA executable was built from exact upstream commit
`26b7884bc25a5933960f3cdcd98bac1ae14d42e2`; the installed stock executable and
commercial ROM were not changed. The tracked patch adds a dedicated probe state
to `struct GBA`, observes CPU EWRAM loads in `GBALoad8/16/32` plus the direct
load-multiple path, and overlaps mGBA's bus-aligned physical access span with
`[X+0x04,X+0x10)` and `[X+0x14,X+0x18)`, while retaining the instruction's
logical address and width. Disarmed reads pay one predicted branch. The armed hot path
does no allocation, logging, formatting, socket work, or generic watchpoint-list
scan. First match records the original address/width, overlap, PC, CPSR, r0-r15,
externally supplied identity, and event ID, then disarms before a controlled
debugger pause. Control and deferred event serialization use four custom GDB
query packets; numeric control fields are lowercase because the pinned stub's
hex parser does not accept uppercase `A-F`.

The standalone Windows SDL frontend also exposed an upstream initialization
gap: `SocketSubsystemInit` existed but no mGBA caller invoked it. Qt incidentally
initialized Winsock elsewhere. The patch balances socket subsystem setup and
teardown in the GDB stub, allowing command-driven SDL `--gdb --savestate`
startup without Lua or Windows UI automation.

The human capture used the pre-review patch/executable hashes `a18e6f9a...` /
`6d67481b...`. Final ROM-011 review corrected generic unaligned 16/32-bit
physical-span overlap and bound launch verification to the tracked patch hash,
producing ROM-011 completion hashes `8863b2e2...` / `cdd871ae...`. The captured
aligned 16-bit `X+0x04` read is unaffected by that correction. ROM-012 later
extended this patch with an exact accepted-containment mode.

Ignored performance gate `build/rom011/performance-gate-13` used the same
verified ROM/state/save copies and direct GBA VCOUNT rollover counting over GDB,
without memory watchpoints or injected input. Five-second results were stock
59.890, instrumented-disarmed 59.129, and instrumented-armed 59.727 observed
VCOUNT rollovers per second. These are near-real-time lower-bound observations,
not a valid throughput ratio: some sampling gaps exceed one frame, and stock Qt
versus instrumented SDL is not an uncapped like-for-like comparison. Originals
remained unchanged. A corrected human run retired discovery breakpoints after
arming and retained only reset/removal lifecycle breakpoints; the user reported
normal performance, completing the qualitative playability gate.

Corrected run `build/rom011/human-native-02` dynamically established the exact
load-epoch-1 X `0x0203DE7C` and captured the first qualifying CPU read before
immediate disarm. PC `0x08012748` performed a signed 16-bit read at
`0x0203DE80` (`X+0x04`) inside point-query routine `0x080126D4`. The captured
query coordinate was 172 and X's loaded lower bound was 592. The next compare
therefore implies the first lower-bound rejection path, before the remaining
bounds or callback. The user separately reported that Goku had entered his
idle sit-down animation when execution stopped; this is timing context, not
proof that X caused that animation.

ROM-011 result is **C - IDLE/NORMAL PROCESSING READ CAPTURED**. Exact-X
consumption at PC `0x08012748` inside point-query `0x080126D4` is **CONFIRMED,
Level 3**. The specific region subtype and dialogue hypothesis remain
unresolved, and parser readiness remains **NO** because descriptor
extent/boundary is still unknown.

## ROM-012 exact target action capture

A user-created post-transition state allowed post-load reconstruction without
replaying the factory/allocation/insertion chain. Runtime enumeration validated
the complete identity chain from live registry slot `0x03002A68`, through X
`0x0203DE6C` and retained descriptor `0x08294948`, to descriptor raw factory
`0x08007675`. X had half-open bounds `x=[592,601), y=[136,241)` and callback
receiver `0x0300195C`. Query entity `0x0202E4D0` tracked the user's movement,
strongly supporting player correlation.

The ROM-012 tracked patch/executable SHA-256 values were `8ee9d92d...` and
`0698a847...`, built from the same pinned mGBA commit as ROM-011. The new mode
requires exact PC `0x0801277A` plus a read overlapping `X+0x0C..X+0x10`.

The native exact gate captured PC `0x0801277A` reading `X+0x0C` when the query
was `(592,218)`. Receiver dispatch base `0x0804A0AC` resolved vtable[2] raw/fetch
`0x08007769/0x08007768`; it returned 1. Vtable[1] raw/fetch
`0x080125E9/0x080125E8` then executed and re-dispatched through X to concrete
target `0x080075AC`. The retained bounded trace reached descriptor-driven and
spatial-position update paths but did not return to the point query within 512
steps.

Human observation is separate: entering X moved the player to the next area
and began dialogue. The exact containment/filter/action chain is **CONFIRMED,
Level 3**; a transition-initiating spatial action is **STRONGLY SUPPORTED,
Level 4** by the controlled trace plus immediate observation. Dialogue gating,
collision semantics, and a final subtype remain unresolved. ROM-012 result is
**B - EXACT TARGET ACTION CAPTURED**. Parser readiness remains **NO** because
source-descriptor extent/boundary and a complete lossless field map remain
unestablished.

## GBARecomp boundary

Generated C/C++ is behavioral evidence only. The pinned framework explicitly directs fixes into analyzer/emitter code followed by regeneration (`mstan/gbarecomp@6571cb39858af70d691914132f81b01a4558d815`, `README.md:248-250`). Useful future surfaces include TCP debug queries, snapshots, IO traces, reverse-debug rings, symbol mapping, and strict-static coverage. None is canonical editable game source for this project.

## LOGX-MAP-RENDER-001 selected map root

The selector route confirmed by LOGX-MAP-RECORD-001
(`MapEntry[+0x2C] + 4 * (selector - 1)`, Thumb `0x080089CC`) resolves, at
selector `1`, a per-map ROM-resident **load-time definition template**. Thumb
`0x0800953E`, reached from the MapEntry load flows `0x08008BD0` and
`0x08009078`, copies its scalar fields into the RAM map-state structure and
hands its pointer fields to the graphics, layer, and object loaders
(**CONFIRMED**, static instruction and decompilation evidence; full detail and
the read-only Ghidra report procedure are in
[`research/LOGX_MAP_RENDER_PROVENANCE.md`](research/LOGX_MAP_RENDER_PROVENANCE.md)).

All 452 canonical records resolve a non-null, 4-byte aligned, in-ROM selector-1
root (`0x0817B1B0..0x082B8C38`, 421 distinct). Exactly 453 word-aligned ROM words
hold one of those root values: the 452 `MapEntry+0x2C` selector-1 slots plus one
stray hold at `0x0837F900` (value `0x08250A24`). A resynchronising full-image
Thumb and ARM scan found no **code** that loads or computes a root address by
PC-relative constant, so the intended access route is `MapEntry+0x2C`. (Root
range values do appear as data inside the root region itself; an earlier claim
of "zero literal loads in the image" was wrong and is recorded as refuted in the
provenance document.)

Confirmed physical layout of the selected root. Widths are the access width the
engine uses, not an assumed schema:

| offset | width | confirmed reading |
| --- | --- | --- |
| `+0x00` | 2 | halfword, loaded whole at `0x08009630` |
| `+0x02`, `+0x03` | 1 each | bytes at `0x08009634`/`0x08009638` |
| `+0x04`..`+0x07` | 1 each | four bytes at `0x0800961E`..`0x0800962E`, added to `BG0CNT`..`BG3CNT` at `0x080093E0`..`0x08009406` |
| `+0x08`, `+0x0A` | 2 each | `ldrh` at `0x0800958A`/`0x08009592`; horizontal and vertical map extent in pixels, stored as `extent - 1`; maximum camera scroll is `extent - 1 + 239` / `+ 159` |
| `+0x0C` | 4 | count |
| `+0x10` | 4 | aligned in-ROM pointer, null exactly when `+0x0C` is null |
| `+0x14`, `+0x18`, `+0x1C`, `+0x20` | 4 each | aligned in-ROM pointers to layer records; target `+0x00` is a Thumb handler (`0x08008087` dominant, also `0x08007A41`, `0x0800897B`, `0x08007B63`, `0x080088BD`), `+0x14`/`+0x15` are chunk width/height bytes, `+0x18` is a container-pointer array |
| `+0x24` | 4 | count |
| `+0x28` | 4 | aligned in-ROM pointer, null exactly when `+0x24` is null; `0x08009420` walks it at a 0x18-byte element stride |
| `+0x34`, `+0x38` | 4 each | aligned in-ROM pointers decompressed by `0x0803D940` into 0x2000-byte buffers at `0x080095AE`/`0x080095B6` |
| `+0x3C` | 4 | word (`0` in 451 roots, `1` in map 19), selects an engine table row for the BG control values |
| `+0x40` | 4 | count in `1..14` |
| `+0x44` | 4 | aligned in-ROM pointer, null exactly when `+0x40` is null; `0x08009670` loads exactly this pair and forwards it to registry routine `0x08012664` |
| `+0x48` | 4 | aligned in-ROM pointer to a Webfoot-LZ container whose decoded payload is a delta-coded u16 selector stream (`0x08009BE6`..`0x08009C12`) |
| `+0x4C` | 4 | the single word `0x08179764` on all 452 roots; engine-global, not per-map |

All three count/pointer pairs (`+0x0C`/`+0x10`, `+0x24`/`+0x28`,
`+0x40`/`+0x44`) are null-coupled: no root has a count without a pointer or the
reverse.

Provisional or unresolved, and deliberately not promoted: the semantic names
"width"/"height" (the pixel-extent reading is confirmed, the tile-vs-pixel unit
name is not), the BG0-BG3 slot assignment (slot order is consumed by the BG
control programming but the per-slot assignment is not directly proven), the
animated-tile identity of `+0x0C`/`+0x10` (the record loader and VRAM target are
established, but the instruction that reads the pair out of the root was not
recovered), the record layout of `+0x44`, and the meaning of `+0x30`,
`+0x50`..`+0x5C`. Selector use is partially confirmed: every examined selector
source resolves to `1`, yet 55 MapEntries expose multi-word source arrays, so a
wider valid range is possible and unresolved.

## Unresolved after ROM-002

- Semantic meaning of every `_raw` field above, especially `output`, `zone`, `area`, `variation`, counts, flags, `music_id`, and pointer target types.
- Whether offsets and generated behavior from the `DCF23468` recomp profile transfer to `01C1707F`. They must currently be treated as incompatible.
- Semantics of unknown structure bytes and incomplete script opcodes.
- Portable compression integration and exact compatibility with Webfoot's streams.
