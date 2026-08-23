# Webfoot Engine Subsystem Map (Buu's Fury, canonical profile)

Target: `buus_fury_usa_rev0_01c1707f` only. Every claim carries its evidence
class; do not transfer addresses across profiles. This file is a navigation
aid: "where does X live?" without re-doing archaeology.

## 1. Map data and loading

| Item | Address | Evidence | Notes |
|---|---|---|---|
| MapEntry table | `0x0808E2E0`, 452 x 0x38 | CONFIRMED | Layout in reverse-engineering.md; semantics mostly INFERRED |
| MapEntry lookup fn | `0x080089FC` (Thumb) | CONFIRMED (static + structure) | Compares `+0x00/+0x01`, stride 0x38; BL sites `0x08004A82`, `0x08008D2A`, `0x08008D6C`, `0x08008E94`, `0x08009056` |
| Variation-word resolver | `0x080089CC` | CONFIRMED L3 | `MapEntry[+0x2C] + 4*(selector-1)`; callers `0x08008ABA`, `0x08008BC4`, `0x0800906A` |
| Selector default helper | `0x080089A0` | STRONG_STATIC | Returns supplied selector; 0 -> 1 when MapEntry `+0x28` null (always true in this ROM) |
| Map load flow | `0x08008B30` region (`0x08008D2A..0x08009078`) | STRONG_STATIC | Resolves variation word, retains at struct `+0x8C` via `0x0800953E`; alt path `0x08008AA0 -> 0x08009670` |

## 2. Spatial-object registry (best understood subsystem)

Global manager at IWRAM `0x03002A64` (count + slot array). Reset clears count
at `0x08048488`.

| Function | Role | Evidence |
|---|---|---|
| `0x08009670` | population adapter: selected value `+0x40`=count, `+0x44`=descriptor array -> `0x08012664` | L3 runtime (ROM-007) |
| `0x08012664` | descriptor-array iteration (backward), indirect factory dispatch via `0x08046AA2 BX r1`, registry append | L3 runtime |
| `0x0801268A..0x080126CE` | removal by pointer, compaction, cleanup dispatch | static + runtime lifecycle (ROM-008) |
| `0x080126D4..0x080127AD` | point query: signed half-open AABB vs `+0x04..+0x0B`, first-accept exit; two-stage callback dispatch | L3 (ROM-011/ROM-012) |
| `0x080127AE..0x08012844` | second AABB query routine | static entries; callers below |
| `0x08012846..` | third query routine | static entry |
| `0x08012900` | prune path (mode-dependent) | STRONG_STATIC |
| `0x08012628` | destroy/prune helper (mode-dependent) | STRONG_STATIC |

Point-query callsites -> containing functions (AUTO-002; callsite
relationships CONFIRMED via independent BL decode, boundaries are Ghidra
candidates):
- `candidate_caller_08006E3C` (`0x08006E3C..0x08006FDF`) -> `0x080126D4`
  at `0x08006E4E`. Global-driven frame handler; button-bit tests; message
  family heavy. Player-interaction candidate.
- `candidate_caller_08021CC0` (`..0x08021EAD`) -> two point queries
  (`0x08021DFE/08021E06`). Periodic dual-point sensor, animation ids
  `0x6f..0x73`.
- `candidate_caller_08012A24` (`..0x08012B5D`) -> `aabb_query_080127AE`
  at `0x08012AEC`. Entity method; flag gate; table-indexed text calls;
  `+0x16` gate. Examine/interact candidate.
- `candidate_caller_080220D8` (`..0x08022149`) -> `aabb_query_08012846`
  at `0x08022142`. Factory: allocates 0x200 via `FUN_0803d5b8`, registers a
  child, immediately area-queries it.
Callers-of-these: UNKNOWN.

## 3a. Candidate dialogue/message family (CANDIDATE roles)

`FUN_0801191a`, `FUN_08011944`, `FUN_08011a1e`, `FUN_08011c0c`,
`FUN_08011c70`, `FUN_08011db4`, `FUN_08011e0e`, `FUN_08011e94` - recurring
attach/post/remove-shaped calls around interaction paths. Also allocator
`0x0803D5B8` (shared with spatial factory), release-ish `0x0803D8A0`,
resource-by-id getter `FUN_0802bfbc(id,table)`.

## 3. Rectangle runtime object family

- Size 0x18; dispatch base installed at `+0x00`; bounds halfwords
  `+0x04/+0x06/+0x08/+0x0A`; callback receiver reference `+0x0C`;
  retained source descriptor `+0x14`; bytes `+0x10/+0x11` initialized.
- Known factory: raw `0x08007675` / fetch `0x08007674` (allocates 0x18,
  initializer `0x08009AEC`). Second observed factory raw/fetch
  `0x080072CD/0x080072CC` - role UNKNOWN.
- Dispatch tables (data): object family `0x0804A09C` (cleanup slot ->
  `0x080510A1/0x080510A0` -> release `0x0803D63C`); receiver table
  `0x0804A0AC` with vtable[1] action, vtable[2] filter slots used by the
  point-query accept path.
- Accept chain (CONFIRMED L3/L4): containment -> vtable[2] filter
  `0x08007768` (returns 1) -> vtable[1] action `0x080125E8` -> concrete
  downstream `0x080075AC`. Action semantics: **map-transition executor**
  (AUTO-003, STRONG_STATIC / semantics CANDIDATE) - calls `FUN_08008d44`
  (map-load flow) with zone/area/variation-shaped bytes, gets a new map
  context, carries the retained variation word into new-context `+0x8C`, and
  dispatches the new context's `+0x28` population method.
- Example source descriptor `0x08294948`: factory raw `0x08007675`,
  `+0x08=(592,136)`, `+0x0C=(601,241)`; bounds copied to object by common
  initializer `0x08009AEC`; `+0x04` drives callback-reference production.
- MapEntry 39 descriptor array `0x08294960 = [0x08294930, 0x08294948]`
  (AUTO-001, CONFIRMED). Sibling `0x08294930`: factory raw `0x080072CD`,
  bounds `(96,0)-(257,17)`. Pair spacing supports `INFERRED` descriptor stride
  0x18: layout candidate
  `{+00 factory_raw, +04 code_ptr_raw, +08..+0F four signed bound halfwords,
  +10/+11 bytes, +12..+17 unknown}`. Extent not yet globally proven.
- ROM-wide (AUTO-004, CONFIRMED): 839 shape-plausible descriptors match the
  two confirmed factory words; ownership chains resolve through
  `descriptor <- ptr array <- selected value S (word0 000C10xx, +40 count,
  +44 array) <- variation source <- MapEntry`. Bounds are map-local.
  byte10/byte11 clustering leads recorded in AUTO_RE_<local-state-name>.

## 4. Runtime observation infrastructure

- Instrumented SDL mGBA build (pinned commit `26b7884b...`) with one-shot
  EWRAM read probe + accepted-containment gate; tracked patch in
  `tools/mgba_probe/`. No Lua needed.
- Legacy Lua-injection route scripts under `tools/runtime/` (ROM-006..010).
- Ghidra calibrated project under ignored `build/ghidra/`; headless report
  wrapper `tools/ghidra/run-calibration.ps1`. Blind discovery POOR; seed
  entries explicitly.

## 5. Not yet mapped (frontier)

Main loop / scheduler, player entity update, movement/collision resolution,
enemy AI, combat/damage, script VM + dialogue, inventory/stats, save format,
graphics/animation/audio loaders, compression usage. Anchors into these exist
only where noted above (e.g., query entity `0x0202E4D0` strongly supported as
player-controlled in ROM-012).
