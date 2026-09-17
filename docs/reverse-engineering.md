# Reverse-Engineering Notes

All findings below are evidence scoped. Structural facts and semantic interpretations are tracked separately.

## Confirmed across relevant sources

- `CONFIRMED`: DragonByteZ recognizes Buu's Fury USA revision 0 by 8 MiB size, `BG3E`, and revision byte 0, but performs no cryptographic whitelist check. Evidence: `spicybung/DragonByteZ@b2691209fa873cc0c1d7aa9cdea7c1da4430afe4`, `src/rom.cpp`, profile construction around line 79 and ROM validation in `Rom::load`.
- `CONFIRMED`: DragonByteZ treats GBA ROM pointers as values at or above `0x08000000`, subtracts that base, and bounds-checks against loaded size. Evidence: same commit, `src/rom.cpp`, `Rom::is_rom_pointer` and `Rom::pointer_to_offset`.
- `CONFIRMED`: DragonByteZ's current map research uses a `0x38`-byte `MapEntry`. Evidence: same commit, `src/analysis.cpp:462-624`, `MapEntry` and `read_map_entries`.
- `CONFIRMED`: in that implementation, byte fields occupy the beginning, pointer-bearing fields are read through `+0x10` to `+0x20`, music is at `+0x24`, and variation/entry/exit script references occupy `+0x28` through `+0x34`. This is upstream implementation evidence, not yet an independent byte-exact proof for every Buu profile.
- `CONFIRMED`: DragonByteZ's Buu profile uses a map table offset `0x08E2E0` with 452 entries and loads an atlas table from file offset `0x179764`. Evidence: same commit, `src/rom.cpp`, Buu profile initialization. The map table metadata is now configured only for `buus_fury_usa_rev0_01c1707f`; it must not transfer to another hash without validation. The upstream *"global atlas table at `0x179764`"* reading is **superseded** by [LOGX-TILE-001](#logx-tile-001-chunk-payloads-and-tile-entries) below: GBA address `0x08179764` is the value held at scene-descriptor `+0x4C` on all 452 selector-1 roots, and the 187 entries there are selector-bank containers, so `0x179764` is a descriptor field's value rather than a standalone global structure. The two statements agree on the location and the entry count and disagree only on ownership.
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
| `+0x40` | 4 | count in `1..14`; read together with `+0x44` by one `ldm r1,{r1,r2}` at `0x08009676` (base = `root + 0x40`), so no constant-offset load of either word exists |
| `+0x44` | 4 | aligned in-ROM pointer, null exactly when `+0x40` is null; points at an array of `+0x40` 4-byte ROM pointers whose targets are the transition records of [LOGX-CONNECTOR-001](#logx-connector-001-root-0x40-0x44-transition-records) |
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
recovered), and the meaning of `+0x30`,
`+0x50`..`+0x5C`. Selector use is partially confirmed: every examined selector
source resolves to `1`, yet 55 MapEntries expose multi-word source arrays, so a
wider valid range is possible and unresolved.

## LOGX-CONNECTOR-001 `root +0x40`/`+0x44` transition records

`root +0x44` points at an array of `root +0x40` 4-byte ROM pointers. The engine
reads the pair with a single `ldm` and walks the array once per map load. The
consumer was recorded as located by LOGX-MAP-RENDER-001; this ticket read it and
recovered the record layout
([`research/LOGX_CONNECTOR_PROVENANCE.md`](research/LOGX_CONNECTOR_PROVENANCE.md)).

The pair is consumed on the selector-1 map-load route:

```text
08008AB6  ldrb r1, [r7, #2]      ; request[+0x02] = the selector
08008AB8  ldr  r0, [r7, #4]      ; request[+0x04] = the MapEntry source array
08008ABA  bl   0x080089CC        ; the accepted "root + 4*(selector-1)" resolver
08008AC0  ldr  r0, [r5, #0xc]    ; the registry object
08008AC2  bl   0x08009670        ; register this root's records
08009672  adds r1, #0x40         ; base = root + 0x40
08009676  ldm  r1, {r1, r2}      ; r1 = count, r2 = pointer array   (one 8-byte read)
08009678  ldr  r0, [r0, #8]
0800967A  bl   0x08012664        ; walk
```

`0x08012664(registry, count, array)` is the walk. It indexes with
`lsls r0, r4, #2` (`0x0801266E`), loads `array[index]` (`0x08012670`), takes that
record's `+0x00` word as a function pointer (`ldr r1,[r0]` at `0x08012672`,
called through the `bx r1` trampoline `0x08046AA2`), and appends the returned
object at `registry + 4 + 4*n`. It iterates index `count-1` down to `0`.

A record's physical layout, at the access width the engine uses:

| offset | width | confirmed reading |
| --- | --- | --- |
| `+0x00` | 4 | the record's class/constructor function pointer, called by the walk at `0x08012672`. Two values in the canonical corpus: `0x08007675` (566 records) and `0x080072CD` (169). The meaning of the two classes is UNRESOLVED |
| `+0x04` | 4 | one value on all 735 records: `0x0800776D`. Meaning UNRESOLVED |
| `+0x08`, `+0x0A`, `+0x0C`, `+0x0E` | 2 each | four little-endian `u16` forming two ordered intervals: `A <= C` and `B <= D` on 735/735 records, no zero-area case. Axis names, units and signedness are UNRESOLVED. Every value is `0` or `8k+1` (24 exceptions at `8k+7`), maximum 977 |
| `+0x10` | 1 | `ldrb` at `0x0800729C`; `0..3` on 725 records, ten outliers |
| `+0x11` | 1 | destination key **high** byte, `ldrb` at `0x0800728E` |
| `+0x12` | 1 | destination key **low** byte, `ldrb` at `0x0800728C` |
| `+0x13` | 1 | a separate byte read at `0x08007282` and passed as a further argument; census `{0:561, 1:174}` |
| `+0x14` | 2 | `ldrh` read by the object the record feeds (`0x0800CDC6`), added to an animation counter |
| `+0x16`, `+0x17` | 1 each | bytes read by that object's constructor (`0x0800CB70`, `0x0800CF28`); `+0x16` is compared against `0x28` and `0x3C` |

The destination is **two independent key bytes**, not a halfword-typed field:
the producer reads them with two `ldrb` sites, the lookup at `0x080089FC`
compares the entry's two bytes with two separate `ldrb` loads and a byte
`cmp r3,r4`, and the warp routine at `0x08008D68`/`0x08008D6A` copies them into a
two-byte staging buffer with two `strb`. Taking `+0x11` as the high byte and
`+0x12` as the low byte resolves to an accepted `MapEntry +0x00` lookup key on
**735 of 735** records; no other content byte pair scores above 589.

Census across all 452 selector-1 roots: 104 roots have `+0x40 == 0` with
`+0x44 == 0`, 348 are non-null, the count sums to **735**, the maximum is
**14**, and `root + 0x44 == root - 4 * (root + 0x40)` on all 348 non-null roots.
All 735 array elements are distinct, 4-byte-aligned, in-ROM pointers, so
*references*, *unique records* and *shared records* are 735, 735 and 0 in this
image. Resolving every destination against the `MapEntry` key table gives 694
directed links, 674 reciprocal, 20 one-way and 3 self-links (maps 125, 126, 127),
with no unresolved destination.

Unresolved, and deliberately not promoted: the engine's own name for these
records; the meaning of the two `+0x00` classes; whether the four `u16` are
tested against a player or object position, and with which two coordinates; the
axis names, units and signedness of those intervals; the semantics of `+0x10`,
`+0x13`, `+0x14`, `+0x16` and `+0x17`; and LOGExtractor's viewer-side `X += 8`,
for which no engine counterpart was found.
## LOGX-LAYER-001 layer records

The four selector-1 root layer slots (`+0x14`, `+0x18`, `+0x1C`, `+0x20`) are
**all non-null in all 452 canonical roots**: 1808 references resolving to **1464
unique layer records** in `0x080707FC..0x082B8BC8`, 35 of which are shared
between maps. An unused layer is a zero-dimension record (`0x080707FC`,
referenced 249 times), never a null slot. Four root slots therefore mean four
layer instances, not four record types
([`research/LOGX_LAYER_PROVENANCE.md`](research/LOGX_LAYER_PROVENANCE.md)).

Physical layout of a record, at the access width the engine uses:

| offset | width | confirmed reading |
| --- | --- | --- |
| `+0x00` | 4 | an odd (Thumb-bit-set), non-4-byte-aligned word that is a valid Thumb code entry. Five distinct values occur; three of them are independently disassembled allocator/constructor routines. It is **not** the word the constructor writes into its object: that object field is an even data pointer (`0x08049410`, `0x08049548`, `0x080498B0`, `0x08049604`, one per family). Whether the record word is ever branched through is UNRESOLVED |
| `+0x04`, `+0x08` | 4 each | scalar words, read at `0x08007BBE`/`0x08007BC4` and copied to `object+0x3C`/`object+0x40`; meaning UNKNOWN |
| `+0x0C` .. `+0x13` | 4 + 4 | two 4-byte words, read whole by `ldm r0!,{r2}` at `0x08007BD0` and `ldr r0,[r0]` at `0x08007BD4`, copied to `object+0x44`/`object+0x48`. Nothing recovered consumes those object fields; signedness, units and any X/Y pairing are UNRESOLVED |
| `+0x14` | 1 | unsigned grid count in x: `ldrb` at `0x08007BDC`, used as the horizontal bound at `0x08007C66`/`0x08007C70` |
| `+0x15` | 1 | unsigned grid count in y: `ldrb` at `0x08007BDE`, used as the vertical bound at `0x08007C3C`/`0x08007C3E` |
| `+0x16` | 2 | signed halfword, `ldrsh` at `0x08007BB6`, copied to object `+0x0C`; 0 in all 1420 dominant-class records |
| `+0x18` | 4 x (`+0x14` * `+0x15`) | the chunk-pointer window. The constructor indexes it at `record + 0x18 + 4*i` (`lsls r1,r5,#2` at `0x08007BEE`, load at `0x08007BF2`) and decompresses each non-null entry through `0x0803D940` to a `0x800`-byte destination at `object + 0x4C + 0x800*i`. When the product exceeds four the loop is **skipped entirely** (`cmp r6,#4` / `bgt` at `0x08007BE2`/`0x08007BE4`) |

`+0x14` and `+0x15` are **separate byte fields** read by two distinct `ldrb`
instructions and multiplied at `0x08007BE0`; they are never loaded as a
halfword. The streaming consumer computes the chunk index as
`y * (record+0x14) + x` at `0x08007C86`, which independently fixes `+0x14` as
the x-count and `+0x15` as the y-count.

`+0x00` vocabulary over the 1464 unique records (references in brackets):
`0x08008087` 1420 [1516], `0x0800897B` 41 [41], `0x08007A41` 1 [249],
`0x08007B63` 1 [1], `0x080088BD` 1 [1].

The LOGExtractor readings of `+0x14`, `+0x15` and `+0x18` are independently
**confirmed**. Its `+0x0D` and `+0x11` X/Y readings are **refuted at the value
level**: those bytes are zero on 1458 and 1453 of 1464 records respectively and
neither is among the fields the one recovered record consumer reads. A stronger
"no consumer exists" claim is **not** made - the region's instruction census is
incomplete (2,035 undecodable halfwords in `0x08007000..0x08010000`), so no
absence claim rests on it. Layer **positioning remains UNRESOLVED** - no signed
coordinate transform was found, and none is imported.

The layer record's `+0x18` window is a **4-byte-element** pointer array. The
`0x18`-byte element stride established elsewhere in this project is
**CONFIRMED for root `+0x24`/`+0x28`** (`0x08009452..0x08009458`); the MapEntry
`+0x18` array examined here uses a 4-byte stride, so it is **not** a second
`0x18`-byte site.

## LOGX-TILE-001 chunk payloads and tile entries

For the dominant layer handler `0x08008087`, every `+0x18` array element
resolves **directly to a Webfoot container**: the constructor loads it with
`ldr r0,[r0,#0x18]` at `0x08007BF2` and passes that same value to the
decompressor `0x0803D940` at `0x08007C04`, with no second dereference. Measured
over the canonical image: 1516 dominant references enumerate 4274 grid cells,
156 of them null, 4118 aligned in-ROM, 0 malformed; those 4118 references
resolve to **3745 unique targets**, 165 of which are shared, the most-referenced
being used 10 times. All 3745 targets are kind-1 containers declaring exactly
`0x800` bytes, and all 3745 decode to 2048 bytes
([`research/LOGX_TILE_PROVENANCE.md`](research/LOGX_TILE_PROVENANCE.md)).

**A chunk is 0x800 decoded bytes consumed as 1024 little-endian 16-bit entries
laid out 32 columns by 32 rows.** The engine states neither dimension as data;
both come from its own accesses: the query method `0x0800800A` computes
`(tile_row & 31) * 64` (`lsls r4,r5,#0x1B` / `lsrs r4,r4,#0x15` at
`0x0800806A`) and `(tile_col & 31) * 2` (`0x0800806E`/`0x08008070`) and reads a
halfword with `ldrh r1,[r3,r1]` at `0x08008074`; the VRAM blit `0x08007D98`
`memcpy`s whole 64-byte rows unchanged. The entry width is therefore 2 bytes,
the row stride 64 bytes, the element stride 2 bytes, and the byte order
little-endian. No packing, no transformation and no second entry access exist:
the engine's only test on an entry value is `cmp r1,#0` at `0x08008076`.

Tile entry bits, over the union of all 3745 unique decoded payloads
(3,834,880 entries):

| bits | measurement | status |
| --- | --- | --- |
| 0-9 | integer field; maximum 895; 896 distinct values, `0..895` | **CONFIRMED** as an integer field |
| 0-9 | the tile ordinal the engine's own loaders populate | **CONFIRMED** |
| 10 | set on 46,034 entries | **CONFIRMED** to exist, be used, and lie outside the index field |
| 11 | set on 15,668 entries (both 10 and 11 on 5,239) | **CONFIRMED** likewise |
| 12-15 | zero on all 3,834,880 entries | **RESERVED / CONSTANT IN CANONICAL DATA**; unused by any known consumer; semantic role UNRESOLVED |

The bits 0-9 reading is not inferred from the hardware format: expanding every
nonzero entry of every dominant payload **that a map references** (1,241,888
entries, a per-map expansion of shared payloads) and comparing the field against
the map's own two tile sources leaves **0 exceptions** - 1,218,581 entries fall
inside the `root+0x48` selector stream's ordinals and 23,307 inside an
animated-tile destination range on 178 maps. (Aggregating over *unique* payloads
instead gives 1,107,699 nonzero entries and is a different unit.) Bit 10 and
bit 11 are not documented here as "horizontal" and "vertical": no payload
consumer reads either bit, and the direction assignment rests on the platform BG
entry layout applied to bytes the engine copies verbatim into a screenblock whose
control word it writes as 8bpp with character base 0. That assignment is
**PARTIALLY CONFIRMED**.

Bits 12-15 are **not** to be documented as "unused by the format": the
all-zero census is a property of canonical data, no `0x0000F000` or
`0x00000FFF` mask exists anywhere in the image, and the engine's occupancy test
treats any nonzero entry as occupied. The four bits are separately classified as
reserved/constant and as unread by any known payload consumer. Bits 10 and 11
are individually **CONFIRMED** to exist, to be used and to lie outside the
tile-index field; the up/down and left/right *direction* assignment is
**PARTIALLY CONFIRMED** only, because no engine consumer of a payload reads
either bit. That negative is scoped deliberately: it rests on an image-wide
adjacent `lsls`/`lsrs` mask scan plus an aligned-constant search, and
shift-then-branch carry tests, `movs`+`lsls` mask builds and non-adjacent
`lsls`/`lsrs` pairs were **not** scanned. Every such site sampled in the
map/layer region reads an object field, never a payload word.

The tile unit is **8x8 pixels**, which the engine proves rather than inherits:
the query method shifts pixels to tiles with `asrs #3` on both axes
(`0x0800805C`/`0x0800805E`), the character-data writer copies exactly 64 bytes
per destination tile (`0x08009C6A`/`0x08009C78`), and the chunk index is a pixel
coordinate shifted by 8 (`0x08008022`), i.e. 256x256 pixels per chunk. The
engine's own `REG_BG0CNT..REG_BG3CNT` values come from one of two records at
`0x080716D8`, selected by `root+0x3C`: **451 roots select index 0**
(`0x1C80 0x1D80 0x1E80 0x1F80`) and one - map 19, root `0x082AD8BC` - selects
index 1 (`0x1C80 0x1D80 0xBE80 0x1F80`). Both are 8bpp with character base 0 and
screen bases 28..31, matching the blit destination `0x0600E000 + slot*0x800`;
they differ only in map 19's BG2, whose `0xBE80` makes that one screenblock
512x256 rather than 256x256.

`root+0x48` is a Webfoot container whose decoded `u16` array the engine prefix-
decodes in place at `0x08009C02`..`0x08009C12` as
`absolute[i] = (raw[i] + absolute[i-1] + 1) & 0xFFFF`, with `absolute[0] = raw[0]`
and the container's declared size as the terminator. All 452 canonical roots
decode; sizes are 4..1784 bytes (2..892 selectors). Each decoded value is a
packed pair: `value >> 8` is a bank index and `value & 0xFF` selects a 64-byte
tile inside that bank's `0x4000`-byte payload (`0x08009C6E`). The engine loads
`root+0x4C` as a **pointer to a `u32` array of bank container addresses**
(`0x08009C54` loads the field, `0x08009C56` indexes the array it points at), so
one selector contributes one 8x8 tile to character memory at
`0x06000000 + 64*ordinal`.

File offset `0x179764` is not an independent global graphics structure: the GBA
address `0x08179764` is the value stored at `root+0x4C` on all 452 roots, and it
points at a **187-entry array of Webfoot containers**, 186 declaring `0x4000`
bytes and one declaring `0x3C40`. The largest `value >> 8` bank index used by any
canonical selector stream is 186, exactly the last table entry. The "128x128 /
256-tile source block" is that bank's `0x4000 / 64` capacity under an 8-bit tile
field - **PARTIALLY CONFIRMED** as an engine resource unit, not a stored
dimension and not universal.

Applicability is bounded: only handler `0x08008087` is covered. `0x08007A41` is
the zero-dimension absent-layer placeholder (`0x08007A40` allocates 8 bytes, no
payload); `0x08007B63` and `0x080088BD` are singletons whose dimension bytes
cannot be a chunk grid; `0x0800897B` fails the dominant reading on 29 of 41
records. No dominant-form decoding is applied to those records.

This section resolves LOGX-LAYER-001's open question about the four-slot install
cap: `cmp r6,#4` / `bgt` at `0x08007BE2`/`0x08007BE4` bounds only the
constructor's warm-up. The streaming method `0x08007C12` recomputes a 2x2
viewport window and decompresses whichever chunk of the record is missing into a
four-entry resident cache (`0x08007D04`..`0x08007D60`), so a record with
`x*y > 4` loses nothing.

Layer **positioning remains UNRESOLVED**, unchanged from LOGX-LAYER-001.

## LOGX-CODEC-001 Webfoot container and packed-stream semantics

Full evidence: [`research/LOGX_CODEC_PROVENANCE.md`](research/LOGX_CODEC_PROVENANCE.md).

**The wrapper is the engine's, not an inference from a decoder.** `0x0803D940`
is a Thumb dispatcher taking exactly two arguments - `r0` = container address,
`r1` = destination - because its first instruction is `adds r2, r0, #0`, which
discards its incoming third argument. It reads `container[+0x00]` and branches:

| `container[+0x00]` | Engine action |
| --- | --- |
| `0` | `memcpy(dst, container + 8, container[+0x04])` at `0x0803D95E`/`0x0803D960` |
| `1` or `2` | the packed decoder, via the Thumb->ARM veneer at `0x08049120` |
| anything else | return with the destination untouched (`0x0803D956 bne`) |

So the eight-byte wrapper is `u32` form, `u32` declared decoded size, then
payload at `+0x08`; and a **zero first word selects a raw copy of
`container[+0x04]` bytes** - it is neither "empty" nor a sentinel. The engine's
own dominant-layer constructor installs `0x08070808` (form 0, declared 0,
followed by `0x800` zero bytes) as its default, so the zero-length case is
engine-observed as well as engine-supported.

`0x0803D966` is a **second dispatcher entry that does test its third argument**.
It has no `BL` caller in the image and none of the accepted call sites use it.
The wrapper has 57 `BL` callers, including `0x08007C04` and `0x08007D4C`
(dominant chunks), `0x08009BF6` (`root+0x48`) and `0x08009C5A` (`root+0x4C`).

The decoder itself does not run from ROM: `0x08049120` is a Thumb->ARM
interworking veneer (`bx pc` / `nop` / `ldr pc,[pc,#-4]` / `.word 0x03000040`)
and the code executes from IWRAM. The copied blob's ROM base is `0x087B79A4`
(**INFERRED** from the library table at `0x087B7970` and the region's
self-consistent internal `BL` offsets); its literal pool holds the length-bias
thresholds `0x37FF` (`0x087B7CCC`) and `0x027F` (`0x087B7CD0`).

**No engine-side destination bound exists.** The packed decoder receives no
length and stores without any comparison. What makes the canonical callers safe
is that each sizes its buffer from the same constant the container declares:
`0x800` per dominant chunk (`0x08007BFE`) and `0x4000` per selector bank.

**Packed grammar** (CONFIRMED against the whole reachable corpus, not from the
disassembly alone): MSB-first bits over little-endian `u32` words; prefix `1` =
literal of `literal_bits` added to `literal_base`; `0 1` = long match with the
field order *distance-code gamma, low distance bits, count gamma*, the match
length biased by distance (`>= 0x10000 +3`, `>= 0x37FF +2`, `>= 0x027F +1`,
`<= 0x007F +4`); `0 0 0` = seven-bit short/control field (non-zero = short match,
zero = distance-width control or, with a second zero, the end marker);
`0 0 1` = four-bit code at `b3..b6` (1 = write `base`, 2..15 = one-byte copy from
`code - 1`, 0 = the literal-width/base escape, which then reads a two-bit field:
non-zero selects 8-bit literals with no base read, zero keeps 7-bit literals and
reads a base byte).

**The third prefix bit is a discriminator and its polarity matters.** Bit 2
**clear** is the seven-bit form and bit 2 **set** is the four-bit form; every one
of the 4,322 reachable packed containers opens on the four-bit escape with prefix
`0 0 1`. Inverting that reading desynchronises most of the corpus.

**CENSUS over the accepted resource graphs** (421 distinct selector-1 roots):
4,520 references, 4,324 unique containers, 4,324 unique payload digests, 4,322
packed and 2 stored, and **2 zero-header containers**. Every one of the 4,322
packed containers decodes byte-identically under two implementations, produces
exactly its declared size, and reaches its own end marker at that same length.
There are no malformed candidates and no digest collisions. Declared sizes run
4..16,384 bytes; packed sources consume 12..8,708 bytes each.

**CORRECTED.** The phrase "all Buu data is JCALG1-compressed" is not supported.
What is supported is narrower: *these Webfoot container forms, carrying these
declared sizes and reached through `0x0803D940`, use this packed grammar.* The
codec's identity as JCALG1 is **PARTIALLY CONFIRMED** at best (JCALG1-like /
derived, engine-consistent); the name is not promoted.

**KNOWN ROBUSTNESS GAP, host-side only.** `webfoot_lz` does not enforce that a
packed stream produces exactly its declared size: an over-long final match is
silently clipped and the decode is reported as successful, so a caller can
receive a truncated payload with no error
(`01000000040000000558d020000000c0` -> accepts, returns 4 bytes). The engine has
no length comparison either, so this is not an engine-contract violation, and the
case never arises on the canonical corpus. It is recorded, pinned by a test, and
its fix belongs to a follow-up implementation ticket.

**REFUTED.** `mainant/LOGExtractor`'s `UnknownHeader` path is not a container
form the engine can be handed: the dispatcher knows only `{0, 1, 2}` at `+0x08`,
and there is no engine path that skips four bytes and then decodes. Four-byte
prefixes belong to engine *records*, not to the codec. The ~64 KiB temporary
buffer is host-tool convenience, **not** an engine limit; the largest declared
size in the reachable corpus is `0x4000` and no engine instruction compares
against 65,536.

## LOGX-CHAR-001 character-definition records

Full evidence: [`research/LOGX_CHAR_PROVENANCE.md`](research/LOGX_CHAR_PROVENANCE.md).

A table of **232 sixteen-byte records** begins at file offset `0x74D380`
(GBA `0x0874D380`), and the engine addresses it directly: `0x08027948` and
`0x08024F3C` compute `record = 0x0874D380 + (index << 4)` and bound their loops
with `cmp rN,#0xE8` (`0x08027998`, `0x080279CC`, `0x08024F92`), each incrementing
its counter before the comparison so `0xE8` is an exclusive bound. `0x08027948`
returns `-1` when its scans exhaust (`0x080279D0`/`0x080279D2`);
`0x08024F3C` does not - its only `mvns` (`0x08024FFC`) builds a `-1` it stores at
`[object + 0x14]`, and its loop simply falls through. Eight sites in all apply
the `index << 4` scale, one per literal load: `0x08027964`, `0x080279A2`,
`0x08024FA8` inside the two walks, and `0x08025088`, `0x080251B8`, `0x08025382`,
`0x08025E92`, `0x080273AE` for single-record lookups.

The address `0x0874D380` is loaded from eight `ldr Rt,[pc,#imm]` sites
(`0x08024FA0`, `0x08025086`, `0x080251B6`, `0x08025380`, `0x08025E94`,
`0x080273AC`, `0x08027962`, `0x080279A0`). No 16-bit `adr` or ARM `pc`-relative
form reaches it, no folded base for it exists in the 0x100 bytes below it, and
the only literals in that range are the two neighbouring structures below. The
table is preceded by a 4-byte table at `0x0874D35C` (indexed `& 3` at
`0x0802734C`) and an eight-entry `u32` pointer table at `0x0874D360` (indexed
`& 7` at `0x08027494`); the eight-entry table ends exactly at the character
table's first byte. The first candidate record past the count (`0x0874E200`)
reads `+0x00 = 7244` (outside the 1,534-entry text table), `+0x02 = 768` (not
`+0x00 + 1`) and `+0x04 = 0x030019A4` (an IWRAM address), so it fails three of
the four invariants that hold on all 232 records and the limit is a real edge.

Field layout, physical only:

| Offset | Physical field | Read by |
| --- | --- | --- |
| `+0x00` | `u16` little-endian | `ldrh` at `0x08024FAC`, `0x080251BC` |
| `+0x02` | `u16` little-endian | `ldrh` at `0x080252E6`, `0x0802539E`, `0x08025EC2` |
| `+0x04` | `u32` little-endian | `ldr` at `0x080273B2`, `0x08027968` |
| `+0x08` | `u32` little-endian | `ldr` at `0x080250CA` |
| `+0x0C` | `i32` little-endian, sign-tested with `blt` | `ldr` at `0x08027974`, `0x080279AA` |

**`+0x00` and `+0x02` are indices into the verified text pointer table
`0x0806BCE8`.** Both are loaded as halfwords, scaled by four (`lsls r0,r0,#2` at
`0x080251C0`, `0x080252EA`, `0x080253A2`, `0x08025EC6`) and then loaded with
`ldr r1,[r1,r0]` (`0x080251C2`) or `ldr r0,[r1,r0]` (`0x080253A4`,
`0x08025EC8`); the four table loads read three pool words (`0x08025328` twice,
`0x080256C0`, `0x08026190`) and all of them hold `0x0806BCE8`. Over all 232
records `+0x00` is in `986..1310` and `+0x02`
in `987..1311`, so every record's text resolves; there are no invalid, empty or
sentinel text references, and `+0x02 == +0x00 + 1` on 232 of 232 records. 154
distinct `+0x00` indices resolve to **152** distinct strings (three slots hold
`"Super Buu"`), and 154 distinct `+0x02` indices resolve to **104**. `+0x00` is
drawn once (`0x0803DADA` at `0x080251C8`) and `+0x02` through a line-wrapping draw
(`0x0803DE6A`, looped over a line counter at `0x080253B6..0x080253BC`), but no
engine instruction names or derives either field, so they are documented as text
indices, not as "name" and "description".

**`+0x04` is a `u32` index into a 4-byte-entry pointer array** and is range
`12..306` over the canonical records with no zero. The accessor is `0x08000158`:
for `id >= 10` it returns `u32 at 0x086B6BDC + 4*id - 0x28` (`0x0800015E` loads
the literal `0x086B6BDC` from pool `0x080003C0`; `0x08000164 subs r0,#0x40` and
`0x08000166 ldr r0,[r0,#0x18]` carry the folded `-0x28`), i.e. the arithmetic
base is `0x086B6BB4`. Ids `0..9` take a party-slot branch and never read the
array. The project's accepted entry run is the contiguous 297 valid, strictly
ascending pointers starting at `0x086B6BDC` and terminated by the non-ROM word
`0x03001068` at `0x086B7080`; the ten words at `0x086B6BB4` are **four** ascending
valid pointers interleaved with **six** nulls. **Which byte is the array's first
entry is UNRESOLVED** and LOGExtractor's `0x6B6BB4` is recorded as the folded
base; resolving it belongs to LOGX-SPRITE-001. *(Resolved by LOGX-SPRITE-001 -
see "LOGX-SPRITE-001 sprite-definition objects and animation tables" below: the
ten words are the last definition object's own inline array, and the run's first
entry is id 10. The paragraph above is left as LOGX-CHAR-001 wrote it.)*

**`+0x08` is a `u32` index into the pointer array at `0x086F393C`**, which is the
accessor's own literal (`0x08011F52`, pool `0x08012194`). `0x08011F20` returns
`0` for slots `0` and `7` without reading the array, takes a party-record path for
slots `1..6`, and otherwise returns `u32 at 0x086F393C + 4*slot`. The canonical
records use `0` plus a 110-element **subset** of `8..162` - 111 distinct values,
exactly one of them zero, carried by 98 records, none in `1..7` - and the array
itself holds 163 slots of which `0..7` are zero, `8..162` are 155 valid ascending
ROM pointers (`0x086B880C..0x086F3360`), and slot 163 is the non-ROM word
`0x0011E502`. Whether an entry is portrait graphics is **PARTIALLY CONFIRMED**:
the consumer passes the pointer to the container dispatcher `0x0803D940`, and no
pixel-format claim is made here.

**`+0x0C` is one signed `i32` used as an index into the accepted stat table**
`0x08711274` at its own `0x1C` stride: `0x08027948` computes
`0x08711274 + 28 * +0x0C` (`0x080279B0 lsls r3,r1,#3`, `0x080279B2 subs r1,r3,r1`,
`0x080279B4 lsls r1,r1,#2`, `0x080279B6 adds r1,r1,r6`) and compares it with a
live pointer. `88` records carry a negative value (`-1..-9`) that the engine
**skips** with `blt` at `0x080279AE`, forming no address; the `144` others use
`0..149` over 123 distinct values, and the eight records whose value is
`142, 143, 145, 146, 147, 148, 149` lie past the 141-record extent TOOLKIT-009
validated (`141` and `144` are unused), so they are recorded as an anomaly rather
than promoted. The field's semantic is **PARTIALLY CONFIRMED** only: the index
arithmetic and the signed test are engine-established, and nothing in this ticket
establishes what the target record means.

**Runtime arrival.** Both `BL` callers of `0x08027948` - `0x0800FB72` and
`0x08010312` - pass a live object's `+0x58` as the appearance id, and the first
also passes `[object + 0x224]`, a pointer into the stat table's address space. So
the engine's route is `runtime object -> (appearance id, stat record pointer) ->
0x08027948 -> 0-based record index`, or `-1`. `0x08027948` maps both its argument
and the record's `+0x04` through the same accessor before comparing, and
substitutes `f(0x92)` for `f(0x95)` first; the meaning of both constants is
**UNKNOWN**.

**Semantic scope.** The table is a superset of whatever the roster bitmap can
set: the roster code `0x08024F3C` intersects it with a 232-bit runtime bitmap
(`bit (i & 7)` of byte `(i >> 3)` at `base + 0xC5`) rather than enumerating it.
The 152 distinct labels span named fighters, story characters, generic enemies,
machinery and body parts, which refutes "playable roster" and "enemy table"; it
does **not** establish that the table is a complete registry, and the attributes
are not universal - 98 records have `+0x08 == 0` (no slot) and 88 have
`+0x0C < 0` (no stat record). It is documented as a table of **named appearance
definitions with optional slot and stat-record indices**. Sharing is normal: 232
records resolve to 198 distinct `+0x04` ids, 110 distinct non-zero `+0x08` slots
and 123 distinct `+0x0C` values, and exactly one pair of records (80, 81) is
byte-identical in all five fields. No engine code groups or orders the variant
families, so what a family means is **UNKNOWN**.

## LOGX-SPRITE-001 sprite-definition objects and animation tables

Full evidence: [`research/LOGX_SPRITE_PROVENANCE.md`](research/LOGX_SPRITE_PROVENANCE.md).

The pointer run LOGX-CHAR-001 accepted is the array the appearance table's
`+0x04` accessor indexes. It holds **297 entries** at `0x086B6BDC`, ids `10..306`
(`index = id - 10`), all word-aligned ROM pointers, strictly ascending, with
**297 unique targets** and no duplicates; the word after the last entry is the
non-ROM `0x03001068` at `0x086B7080`. The accessor's literal `0x086B6BDC` is
reached by exactly two `ldr Rt,[pc,#imm]` sites in the whole image
(`0x0800015E` from pool `0x080003C0`, `0x0801713E` from pool `0x0801715C`).

**The folded base `0x086B6BB4` is not a run prefix.** The accessor computes
`0x086B6BB4 + 4*id` for `id >= 10`, so for `id` in `0..9` it would read the ten
words `0x086B6BB4..0x086B6BD8`. Those words are the inline animation array of the
definition object at `0x086B6B60` - the run's own last entry, id 306 - whose
count is `10` and whose array therefore occupies `0x086B6B60 + 0x54` through
`0x086B6BDC`: exactly the ten words, ending exactly where the run starts. Ids
`0..9` never reach them, because `0x08000158` branches at `cmp r0,#0xa` into a
party-slot path that resolves a party slot through a 24-byte-record table at
`0x086B82EC` and re-enters the array through `0x0801713C`, which applies the same
arithmetic from a record's `u16 +0x0E`. **The run's first entry is id 10 and
index 0 carries no special meaning.**

**Definition object.** Physical layout, all offsets in bytes:

| Offset | Physical field | Engine read |
| --- | --- | --- |
| `+0x00` | `u16` LE; low byte is the inline array's element count, high byte always `0` | `ldrb` at `0x08013046`, `0x08013088`, `0x080131DA`, `0x0802736C`, `0x0802A28E` |
| `+0x02` | `u16` LE, a byte size | `ldrh` at `0x0800EB7C`, `0x0800EC00` |
| `+0x04` | `u32` LE | `ldr` at `0x0800EBF6` |
| `+0x08` | four individual bytes | `ldrb` at `0x0800EF74` (byte 0), `0x0800EC0A`/`0x0800EC0C` (bytes 2 and 3) |
| `+0x0C` | `u32` LE | none found |
| `+0x10..+0x4F` | four 16-byte records of four `s32` LE | none found |
| `+0x50` | `u32` LE | `ldr` at `0x0800EBB6`; indexed by animation index at `0x0800ECE4`, `0x0800ED08` |
| `+0x54` | `count` x `u32` LE inline array | `ldr` at `0x0800EBD0`; indexed at `0x0800ECE0`, `0x0800ED50` |

**`definition + 0x00`, low byte, is the inline array's element count -
CONFIRMED.** The object's extent is `0x54 + 4*count`: 232 of the 296 consecutive
run pairs place the next definition exactly at `+0x54 + 4*count`, the last
object's computed end is exactly the run start, and the 65 exceptions are
separated by exactly `0x100` - the 256-byte remap block below. Five engine sites
then use the byte as an index bound, comparing it with the index of the element
they are about to load and skipping the load when the count is not greater than
that index:

```text
0x08013046  ldrb r1, [r0]       0x08013048  cmp r1, #7      0x0801304C  ldr r0, [r0, #0x70]
0x08013088  ldrb r1, [r0]       0x0801308A  cmp r1, #8      0x0801308E  ldr r0, [r0, #0x74]
0x080131DA  ldrb r1, [r0]       0x080131DC  cmp r1, #7      0x080131E0  ldr r0, [r0, #0x70]
0x0802736C  ldrb r2, [r1]       0x0802736E  cmp r2, #1      0x08027372  ldr r1, [r1, #0x58]
0x0802A28E  ldrb r1, [r0]       0x0802A290  cmp r1, #6      0x0802A294  ldr r2, [r0, #0x6c]
```

`+0x54 + 4*index` is `+0x58`, `+0x6C`, `+0x70`, `+0x74` for indices 1, 6, 7, 8,
which is exactly what those five sites load. A raw scan of every decodable
instruction boundary in `0x08000000..0x08060000` for the whole pattern finds
these five sites and no others.

**`definition + 0x54` begins an inline array of `count` 32-bit ROM pointers -
CONFIRMED.** The elements point at **animation records**. The model is
**count-bounded and sparse**, not fixed: over the 4,070 slots the 297 counts
describe, **1,721 are non-null and 2,349 are null**; index 0 is non-null in 297
of 297 definitions and index 1 in 262 of the 285 that have it. No object carries
an index at or above its own count.

**Animation record.** `u32 frame_count` at `+0x00` (values `1..16`), then
`4 * frame_count` 32-bit ROM pointers; frame `f`, direction slot `d` is at byte
offset `+0x04 + 16*f + 4*d`. Over the canonical image: **1,017 unique animation
records** reached by 1,721 slots, **13,660 frame-pointer slots** with zero
malformed, and **10,980 unique frame records**. Two trailing words follow the
pointer array; their meaning is unknown.

**Animation selection.** `0x0800ECDA(obj, index)` assigns
`*(u32*)(definition + 0x54 + 4*index)` to `obj+0x50`, and also
`definition[0x50][index]` to `obj+0x4C` when `definition + 0x50` is non-null. It
has **no range check** and 159 of its 162 direct `BL` call sites pass a constant
in `0..21`. `0x0800ECF0(obj, state)` and `0x0800ED3E(obj, state, row)` first
translate the state through a 25-byte table at `0x08072670`; that table is
`0..15` identity, `16..22 -> 17..23`, and states `23`/`24` both alias indices
`10`/`11`, so the mapping is a translation and not an identity. `0x0800ED3E`
also writes `obj+0x11`, the second index. `0x0800EF38` then computes
`*(u32*)(obj+0x50 + 16*obj[0x11] + 4*obj[0x10] + 4)` into `obj+0x54`; that is
the current frame record, whose `+0x04` and `+0x05` are read as signed byte
offsets and `+0x06`/`+0x07` as additive extents by the constructor at
`0x080273F0..0x08027414`. Everything below the frame record's `piece_count`
belongs to LOGX-FRAME-001.

**Semantic scope.** Positional slots are comparable across definitions, and the
engine consults the count to decide whether indices 1, 6, 7 and 8 exist, but no
engine instruction names an animation. "Stand", "walk", "run", "attack",
"block" and the rest are **LOGExtractor conventions, not engine facts**, and are
not written here; LOGExtractor's 23-slot numbering is not adopted, and no code
adds one to an animation index. **Fixed positional slots: CONFIRMED
structurally. Individual semantic slot names: mostly UNRESOLVED.** An animation
element may legitimately be null and no selector tests for it, so a sprite may
have no animation at a given index.

**Known disagreement with the accepted graphics corpus.** `GRAPHICS_FORMAT.md`
and `tools/webfoot/graphics.py::_animations_in` resolve a structure's animation
pointers by walking from `+0x54` to the next structure, on the stated ground
that no header field bounds the list, and they filter the walk's words to ROM
pointers. That ground is refuted: the `+0x00` byte bounds the list and the engine
uses it. The walk scans 8,230 slots where the count model scans 4,070; its 4,160
extra slots are all nonzero and none is a ROM pointer, so its corpus figures stay
right for the wrong reason, but its 1,562 "animation references" is a
per-structure deduplicated count rather than a slot count (the slot count is
1,721) and its 1,013 unique animation records exclude the 4 that fail its art
filter (1,017 raw; `13660 - 64 = 13596` direction slots). The accepted document
and reader are **not** modified here; the correction is handed to synthesis.

## Unresolved after ROM-002

- Semantic meaning of every `_raw` field above, especially `output`, `zone`, `area`, `variation`, counts, flags, `music_id`, and pointer target types.
- Whether offsets and generated behavior from the `DCF23468` recomp profile transfer to `01C1707F`. They must currently be treated as incompatible.
- Semantics of unknown structure bytes and incomplete script opcodes.
- Portable compression **encoding**: the packed grammar is understood well enough
  to decode and to state an encoder's obligations (LOGX-CODEC-001, PARTIAL), but
  reproducing Webfoot's compressor bit-for-bit is not established.
