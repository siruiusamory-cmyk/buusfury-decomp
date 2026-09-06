# LOG1 Remake - Verified Project State

This file records current verified facts. Permanent rules live in [`../DEVELOPMENT.md`](../DEVELOPMENT.md).
Detailed evidence lives in [`reverse-engineering.md`](reverse-engineering.md) and [`consumer-analysis.md`](consumer-analysis.md).

## Current Baseline

- **TOOLKIT-003 COMPLETE (2026-09-05)**, independently reviewed; owner accepted and authorized a narrow local commit; no TOOLKIT-004. Implementation baseline `f66007b34d81c7f7c5aac0d1bf8cbf796918a07e`; unrelated work preserved. First post-activation run **497 passed, 2 failed** (obsolete ticket assertions, fixed); post-staging worktree suite **555 passed, 0 failed, 0 skipped**: **494 portable unit**, **61 local-ROM integration**, including **56 synthetic relocation cases**, with three pre-existing marker warnings. Isolated staged relevant suite **109 passed**; staged packaging retry **1 passed**. Broad staged unit run: **418 passed, 4 failed** (three excluded untracked runtime-script dependencies; one wheel subprocess error resolved by the packaging retry). [Closure and file inventory](tickets/TOOLKIT-003-review.md); older baselines below are historical.
- Anchors, classified/reverse references, profile-only free space, deterministic allocation, atomic batch relocation and provenance proven synthetically (`0x100/8 -> 0x208/39`); old bytes preserved, candidates block. Canonical stat/build guarantees pass; ROM SHA-256 remains `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, ROM/save/state hashes and mtimes unchanged. Canonical relocation omitted: no verified free region declared; no new research/runtime capture. Raw diff-check has pre-existing CRLF whitespace; `core.whitespace=cr-at-eol` passes. [Design/limits](relocation.md).

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

Result records for ROM-011, ROM-012, and VERTICAL-001 live in
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
