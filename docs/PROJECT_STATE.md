# LOG1 Remake - Verified Project State

This file records current verified facts. Permanent rules live in [`../DEVELOPMENT.md`](../DEVELOPMENT.md).
Detailed evidence lives in [`reverse-engineering.md`](reverse-engineering.md) and [`consumer-analysis.md`](consumer-analysis.md).

## Current Baseline
- **TOOLKIT-014 COMPLETE for one bounded family (2026-09-07)**, baseline `f4f423f`. A **static Buu record is now proven to own a script**, closing the narrow question TOOLKIT-013 left open. All 29 interpreter call sites were censused by the instruction that last defines the cursor register `r1`: 3 static (the `static40` walker), **2 static-record**, 1 unreferenced dead proc, 23 runtime-object or caller-register. Selected site `0x0801E182`: proc `0x0801E164` gates on owner byte `+0x00` bit 1 then interprets `[r0+0x30]`, and both its callers form `r0` as `table + 52*index` over base **`0x083BD2F8`**, which is loaded from **twelve** independent literals ROM-wide; a thirteenth site `0x0801E1FE` reads `table + 52*index + 0x30` and tests it against zero to set a capability flag. **One deep investigation was spent, not two**: site `0x0800F67A` was inspected first and rejected because proc `0x0800F62C` has **zero inbound references of any kind**, so no owner exists to attach to. **No runtime instrumentation was used** - static tracing settled ownership. **Owner identity established by its own text, not an upstream name**: 83 item records of 52 bytes; text index `0x028E` decodes to `"Miso Soup"` and `0x0291` to its description. New family **`item_use`** reaches **ROUND_TRIP**: **23 roots** (of 83 owners; 60 have a null `+0x30`), all distinct and strictly ascending, **86 blocks, 351 instructions, 703 bytes** at `0x083BBBB0..0x083BBE6F`, **703/703 covered with 0 uncovered**, 0 failing roots, re-encode byte-identical and enforced inside `load_scripts`. **9 distinct opcodes** against static40's 5. **Branch contract promoted from handler-only to corpus-backed**: this corpus contains **42 branches** (21 x `0x12`, 21 x `0x13`). Round-trip still does not discriminate - both grammars decode and re-encode losslessly - but under LOGII's one-byte reading **all 42 branches have displacement 0 and jump to their own fallthrough** (65 blocks), while under Buu's two-byte big-endian reading **all 42 are real jumps** (86 blocks, 84 edges, 0 unknown targets, 0 off-boundary). **`0x1C` remains handler-derived only** - no supported corpus exercises it. **Text references promoted on proof**: `0x0801F818` loads the verified text pointer table `0x0806BCE8` and `0x0801F85E..0x0801F862` reads record `+0x02`, shifts left by two and indexes it - a real dereference. All 83 records carry four in-range decodable indices (332 total). **static40's `0x0266..0x028D` stay CANDIDATE** deliberately: item ids begin at `0x028E` immediately after them, and adjacency to a proven range is not a consumer. **Semantics stay UNKNOWN**: 8 native handlers resolve structurally, none named; `0x080007B7` does not occur here. Attachments exposed at **item level only** - no map, placement or placement-type attachment exists in this family and none is claimed. The two families are **declared separately, not merged**, because they are enumerated from different static owners; the profile loader now refuses overlapping pools. static40 unchanged and pinned (40/120/328/548/5 opcodes/0 attachments). Read-only `event` CLI gained `families | attachments | for-owner | owners-of`; no authoring command. TOOLKIT-011/012 stay closed; `MapEntry[+0x2C]` boundaries unaffected; protected generic core untouched with no game-name branching added. Validation **1,142 passed, 1 skipped, 0 failed** (baseline 1,115/1; +27 tests, no regressions; the skip is the pre-existing opt-in TOOLKIT-011 audit); an intermediate run carrying the toolkit changes but not the new test module reproduced the baseline exactly at 1,115/1/0, isolating the +27 as additions rather than churn. No-op whole-ROM rebuild **0 changed bytes** of 8,388,608; extraction determinism **7,362 byte-identical project files** across two runs; canonical counts hold (1,295 placements, 101 types, 215 maps, 95 enemy-linked types, 1,284 enemy-linked placements); canonical ROM/save/state inputs unchanged. [Evidence](research/BUU_SCRIPT_OWNERSHIP.md); [ticket](tickets/PROJECT_<local-state-name>).
- **TOOLKIT-013 COMPLETE for one bounded family (2026-09-07)**, baseline `3ef10b6`. Buu's Fury **has a real bytecode script VM**: interpreter `0x08004038` fetches one opcode byte, indexes dispatch table `0x080554C0` and calls handlers through the `__call_via` veneer, terminating on the null slot `0x11`. The table holds **exactly 31 slots (0x00..0x1E)** because slot `0x1F` onward is UTF-16 text - a measured bound. A ROM-wide census of contiguous Thumb-pointer runs finds only **five** candidate dispatch tables; three belong to this VM, so Buu has one VM, not several. Same architecture as TOOLKIT-006's LOGII VM (abstractions reused) but **different encodings**, all 31 opcodes re-derived from Buu handler code with nothing transferred: branch displacements are **two-byte big-endian** (not one byte), measured from the **pre**-operand cursor (not post), `0x1C` **subtracts**, and slot `0x1E` is a real handler. Selected family **static40**: of 29 interpreter call sites, 28 take the cursor from a runtime object or caller argument and have no deterministic static enumeration; one walker (`0x080141EE`, table `0x08720564`, bound `cmp r6,#0x28`) yields **40 records / 120 roots**, all non-null, distinct and strictly ascending, over a **548-byte** pool at `0x08720340` ending exactly where the table begins. **ROUND_TRIP**: 328 instructions, 120 terminators, decode coverage **548/548 bytes with 0 uncovered**, 0 failing roots, re-encode byte-identical and enforced inside `load_scripts`. **Honest bound recorded, not glossed**: the corpus uses only opcodes whose widths are identical in both games, so LOGII's grammar also tiles and round-trips it; the round-trip proves boundedness and losslessness but does **not** discriminate the Buu branch contract - the handler disassembly does. An earlier draft claiming the tiling confirmed *every* operand width was measured, found wrong, and corrected in the evidence document and profile. **No attachment promoted**: no map, placement, placement-type, text, flag, item or enemy reference was proven, so none is exposed; opcode `02` occurs only with secondary byte 27 -> one shared native handler `0x080007B7`, meaning UNKNOWN; record `+0x02` halfwords fall inside the text table but stay **CANDIDATE, not text_ref**. Buu scripts as a whole are NOT ROUND_TRIP - one bounded family is. Read-only `webfoot event` CLI with no authoring command (free capacity is zero, so growth is absent by construction). TOOLKIT-011/012 stay closed; `0x08046AA4` remains the `__call_via_rN` veneer; no prior canonical count regressed; canonical ROM/save/state inputs unchanged. Validation **1,115 passed, 1 skipped, 0 failed** (baseline 1,082/1; +33 tests, no regressions; the skip is the pre-existing opt-in TOOLKIT-011 audit). No-op whole-ROM rebuild **0 changed bytes**; two independent extractions produced **7,362 byte-identical project files** and identical builds. Canonical counts hold: 452 maps, 1,295 placements, 101 placement types, 297/295 sprite entries, 10,959 frames, 7,355 payloads. [Evidence](research/BUU_SCRIPT_VM.md); [ticket](tickets/PROJECT_<local-state-name>).
- **TOOLKIT-012 BLOCKED (2026-09-07)** at environmental collision, baseline `5e4e9374b6525a1cb2ac0c220b1828370ba0750d`. No bounded static collision family reached verified movement-blocking semantics; no codec, rung or project representation was created. The 20-byte rectangle family (`0x0800742D`) has **zero** run starts referenced from the MapEntry table at three indirection levels; its subtype words are vtable getters returning IWRAM addresses, so class identity is built at load time; the one CONFIRMED rectangle is a transition receiver; and **no** walkability grid exists (0 low-entropy targets across 784 live MapEntry pointers). Structural finding retained: `MapEntry[+0x2C]` is live on all 452 entries (452 distinct targets, zero shared) addressing one heterogeneous factory-tagged stream `0x080728CC..0x0808E1E0` (112,916 bytes, 40 interleaved families). Correction recorded: `0x08046AA4` is a gcc `__call_via_rN` **veneer**, not a point query, and `+0x54` is a virtual method slot. [Evidence](research/COLLISION_FORMAT.md); [closure](tickets/archive/TOOLKIT-012.md).
- **TOOLKIT-011 BLOCKED (2026-09-06)** at free-region promotion, baseline `9366e080b60e4d4448fd27c1c70df6249c7099a6`; TOOLKIT-010 owner-closed and archived byte-for-byte. Pinned exact-match disassembly identifies candidate tail file `[0x7B89A8,0x800000)` (292,440 bytes), but INCBINs it rather than proving unused sections. Canonical bytes are FF; all-byte u32 audit finds **516 unresolved CANDIDATE references, 99 word-aligned sources**. Partial occupancy checks **16,977 known references**, zero known tail targets/overlaps, but leaves **5,199,061 bytes unannotated UNKNOWN**. No supported smaller independent boundary; no region promoted, verified capacity remains **0**, no graphics relocation or WRITE upgrade. Canonical ROM/save/state hashes, sizes and mtimes unchanged; unrelated work preserved; no runtime capture. Owner authorized one narrow local blocked-research closure commit after green validation. Portable baseline **830 passed**. Post-history-fix focused suite **88 passed, 0 failed (87 portable / 1 explicitly configured local-ROM)**. Earlier broad suite was interrupted at 87% and is not claimed passing. First completed closure run: **1,074 passed / 1 failed**, solely the 241-line state budget. Owner authorized moving the oldest COMPLETE entry verbatim to Part 2; primary/continuation now **240/213 lines**. Fresh final full suite: **1,075 passed, 0 failed, 0 skipped (838 portable / 237 local-ROM), 3 existing marker warnings, 794.40s**. Independent final review passed; ticket diff-check clean, global raw check retains unrelated CRLF warnings. [Evidence](research/FREE_SPACE_RELOCATION.md); [review](tickets/TOOLKIT-011-review.md).

- VERTICAL-001 starting baseline: `478db31967ae0f0ba2d05f3bb51aab521e76d20c` (`docs: record blocked BSim calibration`).
- ROM-011 research baseline: `0d0c0e39c058b7cfba9abcdc30d95849c6310e10` (`feat: capture live spatial-object read`).
- TOOL-001 starting repository baseline: `931794cb5f03caa58431281c3f703a60b3ff5dba` (`feat: capture spatial transition action`).
- Latest completed research ticket: P-008 (normal melee variant selection). **P-006, P-007 and P-008 are RESOLVED**; their deferred unknowns are listed below and do not block closure. No ticket is in progress; P-009 is **NOT STARTED**.
- Latest completed tooling ticket: TOOL-001. TOOL-002 is **BLOCKED - independent related binary unavailable**; BSim remains **UNCALIBRATED** and no adoption decision was made.
- ROM-008 portable baseline: **192 passed, 0 failed, 0 skipped**. Current portable suite after workflow migration: **199 passed, 0 failed, 0 skipped**. Current portable suite after ROM-011: **250 passed, 0 failed, 0 skipped**. Current TOOL-001 portable suite: **293 passed, 0 failed, 0 skipped**. Current VERTICAL-001 portable suite: **280 passed, 0 failed, 0 skipped**. Current P-006B suite: **362 passed, 0 failed, 0 skipped**. Current P-006C suite: **371 passed, 0 failed, 0 skipped**.
- Persistent the tool workflow migration is installed.
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
