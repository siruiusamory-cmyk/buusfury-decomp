# LOG1 Remake - Verified Project State

This file records current verified facts. Permanent rules live in [`../DEVELOPMENT.md`](../DEVELOPMENT.md). Detailed evidence lives in [`reverse-engineering.md`](reverse-engineering.md) and [`consumer-analysis.md`](consumer-analysis.md).
**Reading order** (each part targets a 240-line bound so records continue onward, though part 5 has since exceeded it): this file -> [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) -> [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) -> [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) -> [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) -> [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) -> [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) -> [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) -> [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) -> [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) -> [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>). **Part numbering is not a freshness key. The newest verified state is [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) - start there.** Parts have been appended out of order, so read the dated entries and not the number: part 5 also carries the recent 2026-09-19 entries PORTRAIT-COMPLETENESS-001, GRAPHICS-COVERAGE-001 and DRAGONBYTE-Z-MAP-BROWSER-001, which postdate part 10's newest baseline entry RESOURCE-LIBRARY-CURATION-001 (the ASSET-EXPORT stack is a separate, older section of [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>)). "Current Baseline" below is this part's newest entry, not the project's; earlier parts stay unchanged as history.
## Current Baseline
- **TOOLKIT-021 COMPLETE (2026-09-08)**, baseline `ebea207`: **the four map-reachable dialogs are save-state and scene-control logic - they do not present text, and they do not reach another dialog.** This is **Outcome B**, reached entirely on static evidence; **no runtime escalation was needed or used**. TOOLKIT-020 closed by stating plainly that `map -> placement -> event -> dialog -> text` did **not** close, because the four dialogs the verified map corpus reaches (`event_resource:0393/0506/0508/0509`, all type 0) are disjoint from the seven text-bearing ones. This ticket asked the ticket's own strongest question first - could a multi-hop `dialog A -> dialog B` connect the two proven halves - and the answer is **no, by measurement**. Each of the **13 native slots** the four dialogs call (0, 4, 5, 26, 29, 55, 100, 107, 119, 120, 138, 186, 187) was walked as a **whole call graph** - every `BL` followed, every PC-relative literal inspected - to **depth 10**, slot 119 alone expanding to **70 nodes**: **none reaches text table `0x0806BCE8` and none reaches dialog table `0x0879B704`**, unchanged at depths 4, 6, 8 and 10. **A negative is only worth the instrument that produced it**, so the same walker was pointed at the three known positives and reproduced all three - slot 178 `0x08003030 -> 0x0802BFBC -> literal@0x0802C06C` (text), slot 182 `0x080030F8 -> literal@0x080031C0` and slot 216 `0x0800327E -> literal@0x08003444` (dialog) - reusing the repo's own `analysis/thumb.py` helpers rather than a second BL decoder free to drift. A correctness note that mattered: **opcode 0 is `push_byte`, not a native call** (only opcodes 2 and 3 dispatch natively), so counting it would have invented slots out of pushed constants. **Three families investigated, the budget spent exactly.** (1) **Save flags resolved to all three operations**: `0x08004364` **ands = TEST**, `0x08004380` **orrs = SET**, `0x08004396` **bics = CLEAR**, sharing one bit-addressing shape on `[0x08054FBC + 0x14] + 0x50 + 5 + (bit >> 3)` with mask `1 << (bit & 7)` - SET and CLEAR are **byte-identical for eight halfwords and diverge at exactly one instruction**, so the classification is the operation, never a name. Slot 186 = TEST_FLAG_RANGE (pops count then base, packs results into a mask), slot 187 = WRITE_FLAG_RANGE (pops mask, count, base; SET or CLEAR per bit); **pop order was read from the handlers, never inferred from operand position**, and slot 29's already-proven single SET re-derives identically as the family's control. **OLD CLAIM** that `0x08004396` is "unreached by this corpus, so only SET is claimed" is **superseded**: slot 187, called by dialogs 506/508/509, reaches CLEAR at `0x08003358`, now recorded as a new `dialog_save_flag` contract entry kept **separate** from the event-level `save_flag`, because a different consumer proved it. (2) **Construct-and-queue** (slots 100, 107): allocate `0x0803D5B8`, install a vtable, append via tail walk `0x0801936A` to `[0x08054FBC + 0x1C]` - the same *shape* as TOOLKIT-019's `0x080030F8` and TOOLKIT-020's slot 83 but a **different destination, with no identity claimed**. (3) **Slot 119**, the dominant call in 508/509: pops **five**, matching `push_many(5, ...)` in both callers, stores the top two as halfwords (an X/Y pair passed by pointer), releases the current object through veneer `0x08046AA4`, stores 1 to state word `0x03002A58`, then calls worker `0x08008D44`; named structurally **transition/spawn with a coordinate pair** and **not** promoted to a gameplay verb. Flag effects proven: dialog 506 TESTs then WRITEs **flags 284-286**, dialogs 508/509 WRITE **flags 287-289** and SET one flag via slot 29 - **the operations are proven, the gameplay meanings of 284-289 stay UNKNOWN**. The **non-overlap rule is strengthened, not weakened**: previously the four merely did not *contain* the text base, and now their entire reachable call graph is known not to reach it. TOOLKIT-018's event->text refutation and TOOLKIT-020's slot-139 refutation both stand and are **not revived by context** - slot 139 does not appear in this corpus at all. **The non-type-0 escalation condition was never met** (no map-reachable dialog invokes any other dialog record), so the **286 refused records are untouched** and no subtype was opened; 236 type-0 ROUND_TRIP / 10,263 code bytes / 522 READ census, 31/31 VM handler identity, and the 15 refs / 4 records / 15 events / 4 maps / 47 placements ownership all unchanged. **No WRITE** (its precondition was not met and the ticket succeeds without it), no growth, relocation, subtype expansion, ID migration or AUTHOR_NEW. [Evidence](research/BUU_MAP_DIALOG_SEMANTICS.md); [ticket](tickets/PROJECT_<local-state-name>).
- **TOOLKIT-020 COMPLETE (2026-09-08)**, baseline `c9edc3f`: **a type-0 dialog renders text on screen, and the text is the existing verified UTF-16 Buu text table `0x0806BCE8`.** TOOLKIT-019 closed with player-visible meaning UNKNOWN; it is now **CONFIRMED_ROM**, entirely from static evidence - **no runtime escalation was needed or used**. Chain: `dialog -> native slot 178 -> 0x0802BFBC -> text table 0x0806BCE8`, and `-> 0x0802BECC -> OAM sprite text`. **The family was chosen by measurement, not by operands that looked like text ids** - the mistake TOOLKIT-018 already punished: each of the **107 native slots** the 236 type-0 dialogs use was asked whether its call graph reaches `0x0806BCE8`, and **exactly one answered yes** (slot 178, depth 1, 8 dialogs); the other 106 were excluded by that scan, which a test re-runs and which fails if a second slot ever qualifies. The ranking that produced the candidates **reproduces a known result at the top** - slot 29, TOOLKIT-018's proven save-flag SET - which is what makes it credible on unknown slots. Handler `0x08003030` **pops three, index deepest** (read from the handler at `0x0800303E/0x0800304C/0x0800305A`, never inferred from operand position); `0x0802BFC0` `ldr r1,=0x0806BCE8` then `0x0802BFC4` `lsls r0,#2` / `ldr r4,[r1,r0]` is **byte-for-byte the access shape TOOLKIT-014 proved at `0x0801F85E`** for the item consumer; `0x0803FFE8` walks that pointer as **UTF-16LE halfwords to NUL** summing per-glyph advance widths - the exact encoding TOOLKIT-004 verified - so the pointer is consumed *as text*, not merely as a table entry; `0x0802BFEC` emits **8-byte OAM entries** (8-bit Y, 9-bit X, 32-pixel step) and `0x0802BF8E` blits glyph tiles into `0x06010000`, the GBA OBJ VRAM base, while `0x0802BF5E` centres the string on the supplied X. **Seven dialogs carry literal indices**: 290..298 -> text 1525..1532 -> `"Match 2 Fight!"`..`"Match 9 Fight!"`, all at **X=120, the exact centre of the 240-pixel screen**, matching the centring code. The gaps in that dialog run (289, 293, 299) are **exactly the type-4 records TOOLKIT-019 declared UNSUPPORTED** - a consistency check that could have failed and did not. Dialog 516 calls the same slot twice with a **runtime-computed** index (Y=65 and 85, a 20px line step); it yields **no reference and stays UNKNOWN**, and refusing it is the point. **Families 2 and 3 investigated and REJECTED**: slot 139, the most common *terminal* call (27 dialogs) and so the strongest lifecycle candidate, is a **bitfield condition selector** - `0x08008AA0` filters a list through evaluator `0x08004784` and pushes passers, with no input poll, no UI write and no font routine, so **`wait_for_input` is refused as a context-guessed name**; slots 48/83 are **construct-and-queue**, slot 83 appending via `0x0801936A` (a linked-list tail walk) - the same *shape* as TOOLKIT-019's `0x080030F8` but a **different destination, with no identity claimed**. **Lifecycle: `construct -> queue` established** by three independent paths; **`wait` and `close` were NOT found and are NOT claimed** - no state machine was forced, and all 236 dialogs end in `terminate`. **The preferred milestone is NOT reached and this is stated rather than papered over**: `map -> placement -> event -> dialog -> text` **does NOT close** - the verified operand corpus reaches only dialogs 393/506/508/509, **none of which calls slot 178**, and the seven text-bearing dialogs have **zero** consuming events, placements or maps; both halves are proven, they do not meet, and a test pins that they must not overlap, so the reverse traversal is `text -> dialogs` and stops there. **TOOLKIT-018 is NOT reversed**: its refutation concerned three map-scene **event** consumer families, none of them slot 178; this is a **dialog** operand through a different opcode, native slot, handler and call graph, and a test pins that no event operand ever becomes a text reference. Compressed text `0x0879BF2C` **untouched** - the condition for inspecting it was never met. Save flags 266/267 SET, 31/31 dispatch handlers, 236 type-0 ROUND_TRIP / 10,263 code bytes / 286 refused all unchanged. Read-only `webfoot event dialog-refs` and `dialogs-for-text`; **no WRITE** (its precondition was not met and the ticket succeeds without it), no growth, relocation, subtype expansion or ID migration. Extraction determinism **7 byte-identical files across two runs**; no-op rebuild **0 of 8,388,608 bytes changed** with sha256 `940ad5f0...f059e` matching canonical; canonical ROM unchanged; unrelated work preserved. [Evidence](research/BUU_DIALOG_RUNTIME.md); [ticket](tickets/PROJECT_<local-state-name>).
- **TOOLKIT-019 COMPLETE (2026-09-08)**, baseline `c57873e`: the Buu `event_resource` records behind table **`0x0879B704`** are decoded, and they are **scripts for the VM the toolkit already models**. The engine's own term is **dialog**, read out of the shipped image rather than inferred: consumer `0x0800327E` reaches `0x08004098`, which fails an assertion carrying `"Expected dialog to start with a code block"` and the source path `T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp` line 60. That is a **naming** fact only - what a dialog does on screen stays UNKNOWN and nothing is claimed about it. The interpreter `0x08004038` dispatches through `0x080554C0`, whose **31 handlers (0..30, 17 absent)** are byte-for-byte the `_BUU_HANDLERS` tuple already in `script_specs.py`; opcode 1 is the same signed-magnitude varint and opcode 2 indexes the same native table `0x08055098`. **No second VM exists.** The two consumer families **do not** share a downstream worker - `0x080030F8` (slot 182, pops 2) reaches `0x08012588`, a generic constructor (allocs 8, vtable `0x08049D18`, queues `0x03002A58`), while `0x0800327E` (slot 216, pops 3) reaches `0x08004098` and runs the record: same record, different operation. **Two record fields promoted, because only two are read before branching**: `+0x00` a pointer the consumer dereferences (521 of 522 land in the pool), and dialog `+0x02` the type byte branched on at `0x080040BA..0x080040C2`. Type distribution **0:236 / 3:2 / 4:141 / 5:139 / 6:2 / 7:2**; type 0 runs a code block at dialog+0x03, type 4 expands via `0x08049120`, an ARM veneer to IWRAM `0x03000040`, so it is declared **UNSUPPORTED rather than guessed**. **No fixed record format**: two whole-corpus schemas were tested against all 522 records and both rejected rather than shipped - "pointer run then count word = n-1" holds for 190, "pointer run then NULL" for 463; the four reachable records agreeing was a coincidence. **Capability split, stated exactly**: the `0x0879B704` table is **READ** - 522 ascending pointers, extent `0x0879B704..0x0879BF2C`, pool `0x0877C5A4..0x0879B704` tiled **exhaustively at 127,328 bytes** with zero gap or overlap, sizes min 16 / max 3,168 / 166 distinct, all word-aligned - while only the **236 type-0 dialog records are ROUND_TRIP**; the remaining **286 are structurally classified by type byte and explicitly refused by the codec, never silently passed through**. "522 dialogs ROUND_TRIP" is NOT claimed. Extent is **walked, never searched**: every reachable path is followed, and record 393 proves a first-terminate rule wrong - its `branch_if_zero` at +4 targets +9, past a terminate at +7, so that rule would cut 12 bytes to 8. Four reachable records **`event_resource:0393/0506/0508/0509`** (48/56/824/88 bytes; code 12/38/56/54 bytes; 6/17/20/20 instructions) all type 0, all exact round-trip. Corpus-wide **all 236 type-0 records decode and re-encode exactly**, covering **10,263 code bytes**; the walker calls the VM's own `decode_instruction` rather than re-deriving operand widths, which is what makes that hold. **event->text NOT reopened** - TOOLKIT-018's refutation stands; none of the four dialogs contains text base `0x0806BCE8` and a test pins it, so any future `event_resource -> text` would be a new relation, not a reversal. TOOLKIT-018 counts hold (15 refs / 15 events / 4 records / 4 maps / 47 placements; save flags 266+267 SET only). Read-only `webfoot event resource-show`; no mutation verb, no WRITE, no growth, no relocation, no gameplay naming, no runtime escalation needed. **Stable identifiers remain `event_resource`** (`event_resource:NNNN`, `resource-show`, `resource_records()`) for compatibility; `dialog` is the verified engine classification carried in docs, docstrings and the typed `dialog_type`/`dialog_offset`/`dialog_code_block` fields, NOT an ID migration. Validation **1,268 passed / 1 failed / 1 skipped**; sole failure is the unchanged pre-existing packaged-wheel test. Extraction determinism **7,363 byte-identical files** across two runs; no-op rebuild **0 of 8,388,608 bytes changed**; canonical ROM hash/size/mtime unchanged; unrelated work preserved. [Evidence](research/BUU_EVENT_RESOURCE.md); [ticket](tickets/PROJECT_<local-state-name>).
- **TOOLKIT-017 COMPLETE (2026-09-07)**, baseline `24942bf`: production variable-length placement codec reaches **1,442 records / 240 maps / 240 runs**, preserving all **1,295 legacy IDs** and adding 147. Descriptor model has **82 shared records**; the owned `placement_descriptor_event` family exposes **57 placements / 10 maps / 25 roots / 202 instructions / 514 bytes**, including all three canonical 0x1C branches. Exclusions 7 unreached records / 76 unreferenced descriptors / 19 unowned roots remain excluded; no text consumer or gameplay-handler semantics promoted. Opaque slot accounting corrected to **108 arrays / 556 slots**, typed **35/89 unchanged**; legacy view retains 112/596. Shared common graph uses compact lossless project serialization; no growth, AUTHOR_NEW, allocator changes or semantic script WRITE. Final validation: **1,213 passed / 1 failed / 1 skipped**; portable **868 passed / 1 failed**. Sole failure is the unchanged pre-existing packaged-wheel test; isolated clean-source wheel build/install smoke passes. Two final extractions produced **7,363 byte-identical files**; both rebuilt all **8,388,608 bytes unchanged**. Legacy project rebuild and exact position edit at file **0x72908 (3C -> 4C)** pass. Canonical ROM hash/mtime/size unchanged; saves/states unused, unrelated work preserved. Owner accepted COMPLETE and authorized one narrow local commit; no push. Independent review has no remaining blocker. [Implementation and corrections](research/PLACEMENT_CODEC.md); [active ticket](tickets/PROJECT_<local-state-name>); [review](tickets/TOOLKIT-017-review.md).
- **TOOLKIT-014 COMPLETE for one bounded family (2026-09-07)**, baseline `f4f423f`. A **static Buu record is now proven to own a script**, closing the narrow question TOOLKIT-013 left open. All 29 interpreter call sites were censused by the instruction that last defines the cursor register `r1`: 3 static (the `static40` walker), **2 static-record**, 1 unreferenced dead proc, 23 runtime-object or caller-register. Selected site `0x0801E182`: proc `0x0801E164` gates on owner byte `+0x00` bit 1 then interprets `[r0+0x30]`, and both its callers form `r0` as `table + 52*index` over base **`0x083BD2F8`**, which is loaded from **twelve** independent literals ROM-wide; a thirteenth site `0x0801E1FE` reads `table + 52*index + 0x30` and tests it against zero to set a capability flag. **One deep investigation was spent, not two**: site `0x0800F67A` was inspected first and rejected because proc `0x0800F62C` has **zero inbound references of any kind**, so no owner exists to attach to. **No runtime instrumentation was used** - static tracing settled ownership. **Owner identity established by its own text, not an upstream name**: 83 item records of 52 bytes; text index `0x028E` decodes to `"Miso Soup"` and `0x0291` to its description. New family **`item_use`** reaches **ROUND_TRIP**: **23 roots** (of 83 owners; 60 have a null `+0x30`), all distinct and strictly ascending, **86 blocks, 351 instructions, 703 bytes** at `0x083BBBB0..0x083BBE6F`, **703/703 covered with 0 uncovered**, 0 failing roots, re-encode byte-identical and enforced inside `load_scripts`. **9 distinct opcodes** against static40's 5. **Branch contract promoted from handler-only to corpus-backed**: this corpus contains **42 branches** (21 x `0x12`, 21 x `0x13`). Round-trip still does not discriminate - both grammars decode and re-encode losslessly - but under LOGII's one-byte reading **all 42 branches have displacement 0 and jump to their own fallthrough** (65 blocks), while under Buu's two-byte big-endian reading **all 42 are real jumps** (86 blocks, 84 edges, 0 unknown targets, 0 off-boundary). **`0x1C` remains handler-derived only** - no supported corpus exercises it. **Text references promoted on proof**: `0x0801F818` loads the verified text pointer table `0x0806BCE8` and `0x0801F85E..0x0801F862` reads record `+0x02`, shifts left by two and indexes it - a real dereference. All 83 records carry four in-range decodable indices (332 total). **static40's `0x0266..0x028D` stay CANDIDATE** deliberately: item ids begin at `0x028E` immediately after them, and adjacency to a proven range is not a consumer. **Semantics stay UNKNOWN**: 8 native handlers resolve structurally, none named; `0x080007B7` does not occur here. Attachments exposed at **item level only** - no map, placement or placement-type attachment exists in this family and none is claimed. The two families are **declared separately, not merged**, because they are enumerated from different static owners; the profile loader now refuses overlapping pools. static40 unchanged and pinned (40/120/328/548/5 opcodes/0 attachments). Read-only `event` CLI gained `families | attachments | for-owner | owners-of`; no authoring command. TOOLKIT-011/012 stay closed; `MapEntry[+0x2C]` boundaries unaffected; protected generic core untouched with no game-name branching added. Validation **1,142 passed, 1 skipped, 0 failed** (baseline 1,115/1; +27 tests, no regressions; the skip is the pre-existing opt-in TOOLKIT-011 audit); an intermediate run carrying the toolkit changes but not the new test module reproduced the baseline exactly at 1,115/1/0, isolating the +27 as additions rather than churn. No-op whole-ROM rebuild **0 changed bytes** of 8,388,608; extraction determinism **7,362 byte-identical project files** across two runs; canonical counts hold (1,295 placements, 101 types, 215 maps, 95 enemy-linked types, 1,284 enemy-linked placements); canonical ROM/save/state inputs unchanged. [Evidence](research/BUU_SCRIPT_OWNERSHIP.md); [ticket](tickets/PROJECT_<local-state-name>).

- VERTICAL-001 starting baseline: `478db31967ae0f0ba2d05f3bb51aab521e76d20c` (`docs: record blocked BSim calibration`).
- ROM-011 research baseline: `0d0c0e39c058b7cfba9abcdc30d95849c6310e10` (`feat: capture live spatial-object read`).
- TOOL-001 starting repository baseline: `931794cb5f03caa58431281c3f703a60b3ff5dba` (`feat: capture spatial transition action`).
- Latest completed research ticket: P-008 (normal melee variant selection). **P-006, P-007 and P-008 are RESOLVED**; their deferred unknowns are listed below and do not block closure. No ticket is in progress; P-009 is **NOT STARTED**.
- Latest completed tooling ticket: TOOL-001. TOOL-002 is **BLOCKED - independent related binary unavailable**; BSim remains **UNCALIBRATED** and no adoption decision was made.
- ROM-008 portable baseline: **192 passed, 0 failed, 0 skipped**. Current portable suite after workflow migration: **199 passed, 0 failed, 0 skipped**. Current portable suite after ROM-011: **250 passed, 0 failed, 0 skipped**. Current TOOL-001 portable suite: **293 passed, 0 failed, 0 skipped**. Current VERTICAL-001 portable suite: **280 passed, 0 failed, 0 skipped**. Current P-006B suite: **362 passed, 0 failed, 0 skipped**. Current P-006C suite: **371 passed, 0 failed, 0 skipped**.
- ROM-011, ROM-012, TOOL-001, blocked TOOL-002, VERTICAL-001, P-004, P-006,
  P-006A, P-006C, P-007, and P-008 are archived. `docs/PROJECT_<local-state-name>` is a
  stop-only placeholder; ROM-013 and P-009 remain unstarted.

## Verified ROM
Canonical local profile:

| Property | Value |
|---|---|
| Profile ID | `buus_fury_usa_rev0_01c1707f` |
| Size | 8,388,608 bytes |
| CRC32 | `01C1707F` |
| MD5 | `3a74fce97f1ea2b28c2a50ec3df0acee` |
| SHA-1 | `f1c4b07554d2a3b1ad2f325307051e775ce68087` |
| SHA-256 | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| GBA title | `DBZBUUSFURY` |
| Game code | `BG3E` |
| Maker | `70` |
| Revision | `0` |
| Header checksum | `0x84`, valid |
| Status | `VERIFIED` |

The separate Buu's Fury recomp image with SHA-1 beginning `e65738e9` is a
different profile. Its offsets are not transferable without independent
validation.

## Established MapEntry Format

For the trusted profile:

- GBA table address: `0x0808E2E0`.
- File offset: `0x0008E2E0`.
- Record size and stride: `0x38`.
- Record count: 452.
- Exclusive end: `0x000945C0`.
- Iteration is fixed-count, with no sentinel.
- All 452 records parse and serialize byte-exactly.
- The physical layout is implemented and documented.
- Uncertain field meanings remain raw.

## Established Pointer and Variation Findings

ROM-003 observed nine pointer-labelled words across all 452 entries:

- 4,068 total observations.
- 2,827 null.
- 1,241 valid in-ROM.
- 0 out of range.

`variation_array_pointer_raw` is valid, unique, and 4-byte aligned in all 452
entries. ROM-004 read exactly one little-endian `u32` from each validated target:

- 452 attempted and 452 successful.
- 0 bounds failures.
- Every `first_word_raw` is nonzero, ROM-address-shaped, and 4-byte aligned.
- Its global semantic meaning remains `UNKNOWN`.

## Established Executable Flow

Thumb fetch `0x080089CC` resolves:

```text
MapEntry[+0x2C] + 4 * (selector - 1)
```

Selector `1` therefore selects `first_word_raw` at target `+0x00`.

ROM-006 verified this at runtime on the trusted ROM:

| MapEntry | Expected | Observed |
|---:|---:|---:|
| 1 | `0x082B5FA0` | `0x082B5FA0` |
| 4 | `0x082B5B2C` | `0x082B5B2C` |

This is Level 3 evidence.

## Established Population Flow

Thumb function `0x08009670` receives a selected value, reads words at
`selected +0x40/+0x44`, and calls `0x08012664`.

`0x08012664` receives manager, count, and pointer-array base; iterates
descriptors; loads each descriptor's factory pointer; dispatches indirectly; and
stores returned runtime objects in an IWRAM registry. One observed runtime tuple
had `field_40_raw = 0x00000002`, `field_44_raw = 0x08294960`, and manager
`0x03002A64`. This path is not graphics evidence.

## Spatial Object Research

ROM-007 and ROM-008 established this factory family:

| Property | Value |
|---|---|
| Raw factory target | `0x08007675` |
| Thumb fetch | `0x08007674` |
| Example descriptor | `0x08294948` |
| Allocation size | `0x18` bytes |
| Dispatch-table base | `0x0804A09C` |
| Runtime bounds | signed halfwords at `+0x04/+0x06/+0x08/+0x0A` |
| Retained descriptor | object `+0x14` |
| Callback-like reference | object `+0x0C` |

The factory creates a 24-byte rectangle-aware runtime object, which the
population manager then registers; construction paths in the observed registry
are heterogeneous. **STRONGLY SUPPORTED: generic 24-byte rectangle-aware
runtime object.** Not proven: collision, trigger, activation, transition,
event, or interaction.

## Earlier Runtime Results

ROM-008 established exact object lifecycle attribution and query entries
`0x080126D4`, `0x080127AE`, and `0x08012846`, but no exact callback. ROM-009's
clean state reached the same live family without scheduling a verified query and
ended environment-blocked. ROM-010 confirmed its one-launch harness worked but
the available bounded inputs still scheduled no known post-live query. Detailed
inputs, negative evidence, and safety records remain in the research documents.

## Completed Ticket Results

Result records for TOOLKIT-003/006, ROM-011, ROM-012, and VERTICAL-001 live in
[`PROJECT_<local-state-name>`](PROJECT_<local-state-name>), together with two implementation
specs. **P-007 wolf combat**: acquisition at `dist_sq <= 10000` (r 100), attack
at `dist_sq <= 524` (r ~22.9), a 35-tick attack state, a 36-tick minimum
observed cadence, and no disengagement. **P-008 normal melee**: the three punch
clips are presentation variants selected uniformly at random, each lasting 16
ticks with indistinguishable damage, and there is no deterministic combo.

[`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) continues from there. **P-009
critical hits (PARTIAL)**: HP and damage are fixed-point scaled by 1024, so the
displayed number is `(raw + 1023) >> 10` and earlier "~50,000 per hit" figures
were raw units; criticals are discriminated by damage `record+0x10` and multiply
damage by **exactly 1.5**, contradicting the documented 2. The critical roll,
its RNG, and the STR probability formula are **blocked**, not merely unfinished.
**P-010 enemy death and rewards (RESOLVED)**: EXP is awarded exactly one
gameplay tick after lethal damage, from a reward object's destructor; the
amount is fixed at kill time with the equipment bonus already applied, while
the recipient is resolved at payout, which is why the save-point
character-switch glitch works. Wolf base EXP is 225, qualifying equipment adds
+23 per item additively, and zeni denominations are 5, 25, 50 and 100. The EXP
bonus arithmetic site and the drop roll remain bounded unknowns with named
anchors.

## Ghidra Static-Analysis Calibration

TOOL-001 calibrated Ghidra 12.1.2, Temurin 21.0.11+10, and `pudii/gba-ghidra-loader` commit `9bfb2d1fe891aa78bab7093a328feb3a52318ab7`; all local tools, ROM copies, projects, caches, and reports remain ignored under `build/ghidra/`. The verified ROM imported as `ARM:LE:32:v4t:default` with ROM at `0x08000000`, mapped GBA regions, a parsed header, and an ARM entry at `0x080000C0`. Bounded default analysis timed out at 900 seconds but saved the project. Blind analysis missed all five target functions and chose the wrong ARM/Thumb context for four; established entry/callsite seeds then yielded matching point-query, factory, and callback bodies, but not the indirect action path to `0x080075AC`. Outcome: **B - ADOPT WITH REQUIRED CORRECTIONS**. Use Ghidra as the default static database only with explicit Thumb checks, conservative labels, and corroboration of boundaries and indirect targets. Headless reporting is verified; [`ghidra-workflow.md`](ghidra-workflow.md) has full details. No Ghidra MCP work, broad BSim transfer, Data Crystal import, or ROM-013 research occurred.

## Unresolved Questions

- Which higher-level caller invokes point-query `0x080126D4` during the ROM-011 idle/normal-processing path?
- What is the complete call tree after ROM-012 action target `0x080125E8`, which did not return within 512 steps?
- Is the `0x08007675` source descriptor bounded well enough for a future lossless read-only parser?
- Which semantic subtype, if any, is justified for this rectangle-aware family?
- Which additional object or mechanism causes the remaining VERTICAL-001 transition after descriptor `0x08294948` is empty?

## P-006A/P-006B Corrected Damage and Reaction

- P-006A confirmed signed current HP at `target+0x28C`, incoming damage at
  `record+0x18`, writer `0x0800FA50`, and death threshold `HP <= 0`.
- `0x080101C6` and `target+0x04` are position-derived, not HP. All HP, healing,
  damage, and re-hit claims derived from them are **SUPERSEDED**.
- Controlled punch run `20260827-154856-842990b7` entered reaction node
  `0x08706BA8` at tick 320 and wrote HP at tick 323, so HURT preceded damage by
  3 ticks. Controller state is rooted at `target+0x238`.
- Writer-only mash run `20260827-211421-4e307ab8` recorded post-ki HP writes at
  ticks 673, 976, and 992, giving intervals of 303 and 16 ticks; the latter
  ended in the death path. Neither establishes an immunity timer.

## P-006C Behavior Controller, Reaction and Attack Timing

State-machine primitives: `0x0800AA9C` push (guards `depth < 5`), `0x0800AA4A`
replace, `0x0800AAD8` pop, `0x0800AB0C` update, each taking a controller pointer
and selector index. A controller holds depth at `+0x04` and 8-byte
`{node, table_slot}` entries at `+0x08`; **state-table base is `0x0870F514`**,
stride 8. Nodes: `{entry, update, exit, param, child, sibling}`.

**Correction:** `0x0801920F` is a generic clip-entry handler shared by ~170
selectors, so executing `0x0801920E`/`0x0801920F` alone does **not** establish
HURT semantics; any earlier claim resting on that PC alone is superseded. Wolf
selector 436 has primary node `0x08706BC4` with reaction node `0x08706BA8` as
its child; wolf selectors are contiguous 434-439. Reading `wolf+0x238` per frame
reproduced these selectors with zero stops, confirming the table at **Level 3**.

**Correction:** the player has **no** behavior controller. A structural probe
over every 4-byte offset of each actor matched only `wolf+0x238`. Any
interpretation assuming a player controller is superseded.

Run `20260827-231643-47eeb42a` measured landed hits without breakpoints. A hit
pushes a reaction state (depth 1 to 2), coinciding with authoritative HP
decreases and not observed on unrelated events: push 708/pop 732 and push
1241/pop 1265, both **24 ticks**, the canonical low-perturbation duration. The
earlier 28-tick observation is retained as historical evidence from the
three-breakpoint run, and is **superseded and explained** by that
instrumentation's pacing perturbation.

`T_ATTACK_ACCEPT` is player object `+0x04C`, the current animation-clip pointer.
`0x0851C618` is idle; `0x0851C680`, `0x0851C6C0`, and `0x0851C6A0` are punch
clips observed only with A held. An accepted punch is idle to punch clip with A
held; `+0x050` and `+0x014` move with it. Run `20260828-004513-27dae1f8`
recorded 154 accepted punches: minimum interval **20 ticks**, median 26, against
330 raw A edges at minimum 8. Raw A assertion is therefore not equivalent to an
accepted punch, and 20 ticks is the minimum observed acceptance cadence for this
capture and configuration. The three clips occurred at roughly similar counts;
combo semantics must **not** be inferred from that observation alone.

Rejected anchors, non-authoritative unless future evidence explicitly
rehabilitates them: `0x080342A8`, `0x08034298`, `0x080342AE`, `0x08029FFE`, and
the attack-object `+0x08` phase watch.

### P-006 final status: RESOLVED

Implementation-useful results: accepted-punch anchor is the `player+0x04C` clip
transition, minimum cadence 20 ticks and median 26, with raw input faster and
not equivalent; a landed damaging physical hit pushes a reaction state of 24
ticks. From P-006A: current HP `target+0x28C` signed 32-bit, incoming damage
`record+0x18`, authoritative writer `0x0800FA50`, death `HP <= 0`.

Open, not blocking closure: separate invulnerability **UNKNOWN**; reaction/HURT
exit condition **UNKNOWN**; authoritative world position **DEFERRED**; knockback
kinematics **DEFERRED**; possible three-clip combo cycle **OBSERVED PATTERN /
DEFERRED**.

## Upstream Pins
