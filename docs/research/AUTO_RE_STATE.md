# Reverse-Engineering Research Ledger

Durable brain of the Webfoot reverse-engineering programme
(`OX-AUTO-RE`). Read this file first every loop iteration. Keep it compact;
detailed evidence lives in `docs/reverse-engineering.md`,
`docs/consumer-analysis.md`, and `docs/research/SUBSYSTEM_MAP.md`.

Rules of the lane: static-first, bounded units, evidence labels
`CONFIRMED` / `INFERRED` / `UNKNOWN`, runtime levels 0-4, never modify the
canonical ROM or user saves/states, narrow commits only, never commit
proprietary artifacts.

## Priority Steering (2026-08-23, user)

1. Finish the transition thread cleanly (AUTO-012 first). The causal target:
   WHY did VERTICAL-001 still transition after MapEntry 39's only
   descriptor-owned doorway rectangle was emptied? Strongest remaining
   candidate chain: non-descriptor registry population -> append site
   `candidate_registry_writer_08009172` -> caller path `0x080026FC`. Answer:
   what object is appended, where its bounds originate, whether it exists on
   MapEntry 39, whether it accepts the doorway query, what action it
   dispatches, and whether it reaches `downstream_080075AC`. If explained,
   mark VERTICAL-001 C RESOLVED with the full chain; do NOT enumerate every
   remaining transition subtype. If not explained after bounded work,
   document why and move on.
2. One concise transition-pipeline synthesis in SUBSYSTEM_MAP.md
   (CONFIRMED / STRONGLY SUPPORTED / INFERRED / UNKNOWN separated). Close the
   frontier; do not keep polishing it.
3. Then PIVOT HARD to player/combat as top priority: player entity ->
   update root -> minimum runtime structure (position/velocity/facing/
   animation/HP/ki/attack state/i-frames) -> input->movement rules with
   numbers -> melee initiation/state progression (startup/active/recovery)
   -> one complete damage event (hit detection -> damage calc -> HP mutation
   -> reaction/knockback/i-frames -> death) -> one simple enemy's update loop.
4. Produce BEHAVIORAL SPECIFICATIONS, not field lists (with evidence labels;
   no invented semantics).
5. Use LoG1/LoGII material as differential evidence (manual structural
   comparison; RELATED_IMPLEMENTATION_CANDIDATE until validated).
6. Recover usable gameplay constants: value / unit-representation / where
   used / evidence / game-version.
7. At synthesis passes: audit older claims against new evidence; record
   OLD CLAIM / NEW EVIDENCE / RESOLUTION; archive stays historical.
8. Stay discovery-dominated; synthesis must be cheaper than the units it
   summarizes. Prefer subsystem roots, closed causal chains, state machines,
   formulas/timings, eliminated hypotheses; ignore anonymous leaves.
9. Next-major-checkpoint report must attempt: player update location,
   movement computation, melee initiation, hit->HP-loss chain, knockback,
   enemy update location, recovered constants, LoGII-vs-Buu deltas.

## Current Objective

P-002 (movement): trace directional input to entity movement and recover the
movement behavioral spec (input representation, cardinal/diagonal speed,
normalization, facing rules, state gates). Anchors: input halfwords read at
`*(global)+4` in frame handlers; positions are `>>8` fixed-point words
(`entity+0xA0/+0xA4` pattern seen in `candidate_caller_08012A24`);
per-state data blobs (UTF-16-labelled) hold packed per-state parameters.

## Research Queue

| ID | Subsystem | Question | Why useful | Known evidence | Suggested next method | Status |
|---|---|---|---|---|---|---|
| AUTO-001 | spatial-descriptors | What descriptors exist in the count-2 array at `0x08294960`, and does a sibling cover the ROM-012 doorway? | Directly targets the recorded smallest blocker of VERTICAL-001 C; extends descriptor format knowledge | Array base/count from ROM-007 runtime (`field_40_raw=2`, `field_44_raw=0x08294960`); descriptor `0x08294948` fully characterized | Read-only byte reads at file offsets `0x00294960..68` + both descriptors; decode factory/bounds fields; cross-check with `webfoot variation-arrays find-first-word` | RESOLVED |
| AUTO-002 | spatial-registry-callers | Which containing functions call point-query entries (`0x08006E4E -> 0x080126D4`, `0x08021DFE/08021E06 -> 0x080126D4`, `0x08012AEC -> 0x080127AE`, `0x08022142 -> 0x08012846`)? | Names the scheduler layer that decides when spatial queries run; open PROJECT_STATE unresolved question | Callsite instructions CONFIRMED by independent BL decode (ROM-008); Ghidra did not recover containing functions | Seed callsite instructions in calibrated Ghidra project; recover boundaries; decompile callers; conservative names | RESOLVED |
| AUTO-003 | transition-action | What does action `0x080125E8 -> downstream 0x080075AC` actually do (map reload? dialogue start?)? | Would explain transition mechanism and likely close VERTICAL-001 C mechanism question | Runtime: action executed and reached `0x080075AC`; trace hit `0x080077EC`, `0x08009744`, `0x080094B8`; no return within 512 steps | Ghidra: seed `0x080125E8`, `0x080075AC`, `0x080077EC`, `0x08009744`, `0x080094B8`; decompile; enumerate callees; look for MapEntry-load flow entry (`0x08008B30`) and registry reset (`0x08048488`) | RESOLVED |
| AUTO-004 | doorway-descriptor-census | Which candidate descriptors ROM-wide overlap the ROM-012 doorway, and which map owns them? | Identifies or eliminates descriptor-driven explanations for VERTICAL-001 C; builds global descriptor corpus | Factory raw words `0x08007675`/`0x080072CD`; half-open AABB semantics; per-map coordinate caveat | 4-aligned scan for factory words, decode bounds, reverse-reference ownership chain (descriptor <- pointer array <- selected value <- variation source <- MapEntry) | RESOLVED |
| AUTO-005 | object-vtables | What methods live in dispatch tables `0x0804A09C`, `0x0804A0AC`, `0x0804E444`? | Defines the rectangle-object class hierarchy; every spatial object routes through these | Cleanup slot raw/fetch `0x080510A1/080510A0`; filter vtable[2] `0x08007769`; receiver base `0x0804A0AC` vtable[1]/[2] used; AUTO-003 added vtable+0x34/+0x84/+0x28 uses | Ghidra data-word dump of each table; follow each raw target; classify per-slot semantics conservatively | READY |
| AUTO-005 | registry-manager | Complete function graph of registry manager around `0x03002A64` (`0x08012628`, `0x08012664`, `0x0801268A`, `0x080126D4`, `0x080127AE`, `0x08012846`, `0x08012900`, neighbors to `0x080128F2+`) | One coherent subsystem map for the best-understood engine area | Individual behaviors established in ROM-006/008/011/012 | Ghidra seeding + decompilation sweep over `0x08012600..0x08012A00` | READY |
| AUTO-006 | descriptor-format | What is the minimal extent/field map of a source descriptor such that parsing is lossless? | Recorded parser-readiness blocker across ROM-008..ROM-012 | Consumers read `+0x00` (factory), `+0x04` (callback producer), `+0x08/+0x0C` (bounds) | Static census of all descriptor accesses from all factories reached via variation arrays; adjacency analysis in ROM | READY |
| AUTO-010 | map-loader | Does `FUN_08008d44` resolve a MapEntry via `0x080089FC` from zone/area/variation bytes, and what are its argument/return contracts? | Completes the transition mechanism chain end-to-end; needed for any future map-warp tooling | AUTO-003: called by `downstream_080075AC` with `(ctx, byte, byte, ptr, byte, 1)`, returns new context | Ghidra: seed + decompile `0x08008d44`; check for `0x080089FC` call and literal use | RESOLVED |
| AUTO-011 | registry-population | Do MapEntry objects/npcs pointer-driven spawns add spatial registry members beyond the variation-array path? | Tests the remaining descriptor-free explanation for VERTICAL-001 C | ROM-007: registry construction is heterogeneous; objects/npcs pointers exist in MapEntry (+0x1C/+0x20) | Enumerate callers of `registry_populate_08012664`; census manager-global xrefs; classify write sites | RESOLVED (refined) |
| AUTO-012 | registry-population | Which load path drives second append site `candidate_registry_writer_08009172` via callsite `0x080026FC`, and what do the `FUN_0800d30e`/`FUN_08017f5a` manager writes do? | Completes the registry-mutation map; candidate VERTICAL-001 C mechanism | AUTO-011: append site appends vtable[0]-dispatch results from an 8-byte-stride record table; caller `0x080026FC` unrecovered | Ghidra: recover containing function of `0x080026FC` (backward seeding), decompile writers | RESOLVED (VERTICAL-001 C explained; FUN_0800d30e/FUN_08017f5a write classification deferred as low-value) |
| P-001 | player-entity | Which runtime entity is the player and where is its update root/dispatcher? | Root anchor for all player/combat research | ROM-012: query entity `0x0202E4D0` tracked human movement; `candidate_caller_08006E3C` frame handler queries at a tracked entity; map loader spawns via 0x18-stride table + `FUN_080109aa/080104f2` | Static: decompile loader spawn path (`FUN_0801713c`, `FUN_080109aa`) to find the player-class factory + its update dispatch entry; then find per-frame update root | RESOLVED |
| P-002 | player-movement | How does directional input become movement (speed, normalization, facing, inhibition)? | Core behavioral spec for remake | P-001 dependency | Trace input bits from `candidate_caller_08006E3C` button tests into entity velocity/position fields | BLOCKED by P-001 |
| P-003 | melee | Where does basic melee begin and what is its state progression (startup/active/recovery/hitbox query)? | Core combat spec | none yet | From player update root, follow attack-button branch to melee state machine | BLOCKED by P-001 |
| P-004 | damage | One complete damage event: hit detection -> damage calc -> HP mutation -> reaction/knockback/i-frames -> death | Closes the combat loop end-to-end | none yet | Follow melee hitbox accept into enemy entity HP mutation | BLOCKED by P-003 |
| P-005 | enemy-ai | One simple enemy's update loop (idle/detect/approach/attack/receive-damage/death) | Enemy behavioral spec | `candidate_caller_08021CC0` periodic dual-point sensor candidate | From entity spawn table, pick simplest enemy class and trace update | BLOCKED by P-001 |
| P-006 | differential | Compare recovered Buu player/combat functions against LoGII/LoG1 material (manual structural comparison only) | Answers what combat feel is shared vs changed | recomp repos lack generated code; Legacy repo has LoG1 tooling/VM data | After P-002/P-003 produce constants/state machines, compare shapes/constants with Legacy repo data | DEFERRED until P-003 |
| AUTO-007 | script-vm | How does the Buu bytecode VM relate to Legacy repo's 145-opcode LoG1 VM inventory? | Dialogue/quest scripting is a whole engine subsystem | `extern/Legacy/OpCodes.csv`, `DBZKit/Legacy/Games/BYTECODE_VM.cs` (LoG1 lineage, INFERRED transferability) | Locate Buu bytecode consumers from MapEntry script pointers; compare opcode dispatch shape | DEFERRED |
| AUTO-008 | bsim | Calibrate BSim against an independent related binary | TOOL-002 closed BLOCKED: no independent related binary locally | TOOL-002 archive | Needs a new local binary (e.g., another-region dump) before any work | BLOCKED |
| AUTO-009 | external-knowledge | Data Crystal / community addresses for Buu's Fury or LoG1/LoGII worth validating? | Cheap candidate anchors if any exist | None imported so far (deliberate) | Web search; record EXTERNAL CLAIM then validate against canonical profile before use | DEFERRED |

## Recent Discoveries

Synthesis pass after units 1-5 (2026-08-23):
- No contradictory field interpretations found; `+0x8C` variation-word
  retention (ROM-005) is now linked to `downstream_080075AC` carrying it
  across transitions (AUTO-003).
- Ghidra markup updated: `FUN_080089fc -> map_entry_lookup_080089FC`,
  `FUN_08009670 -> population_adapter_08009670`.
- Queue reconciled: AUTO-001/002/003/004/010 RESOLVED; BSim stays BLOCKED;
  script VM and external-knowledge stay DEFERRED; next research objective is
  AUTO-011.
- Naming consistency rule going forward: new DB names use
  `<role>_0XXXXXXXXX` lowercase-hex suffix form.

(Inherited anchors are summarized in SUBSYSTEM_MAP.md; this section records new
research-lane findings only.)

- **AUTO-001 (2026-08-23), read-only static, canonical profile:**
  - `CONFIRMED`: MapEntry-39 selected value `0x08294968` is unique among all
    452 variation first-words (webfoot find-first-word).
  - `CONFIRMED`: descriptor array at `0x08294960` = `[0x08294930, 0x08294948]`.
  - `CONFIRMED` bytes of sibling descriptor `0x08294930`: factory raw
    `0x080072CD` (matches ROM-007's second runtime factory), `+0x04` raw code
    pointer `0x0800776D`, bounds `(96,0)-(257,17)`, bytes `+0x10/+0x11`
    `01 01`.
  - Negative result: sibling bounds `(96,0)-(257,17)` do not overlap the
    ROM-012 doorway `(592,136)-(601,241)`. Under the CONFIRMED containment
    semantics, VERTICAL-001 result-C's persisting transition is NOT caused by
    this array's sibling. The remaining source lies elsewhere in the registry
    population or another mechanism.
  - `INFERRED` (strong): descriptor stride/extent `0x18` for this pair -
    adjacent, both array-referenced, both start with plausible raw factory
    words, one value (`0x08007675`) independently runtime-confirmed. Not yet
    proven as a global rule (feeds AUTO-006).
  - Both sibling descriptors share `+0x04 = 0x0800776D` (Thumb fetch
    `0x0800776C`, four bytes after filter `0x08007768`). Function role
    UNKNOWN; Ghidra seeding candidate.
  - Literal `0x08179764` observed at `0x082949B4` inside the variation-record
    neighborhood. Matches DragonByteZ's upstream claim of a global atlas table
    at file offset `0x179764`; independent consumer proof pending.
    Classification: EXTERNAL CLAIM corroborated by byte presence only.

- **AUTO-002 (2026-08-23), Ghidra static, calibrated project:**
  - All five verified query callsites are now attributed to recovered
    containing functions; every containment check CONTAINS:
    - `candidate_caller_08006E3C` (body `0x08006E3C..0x08006FDF`) contains
      point-query callsite `0x08006E4E`.
    - `candidate_caller_08012A24` (body `..0x08012B5D`) contains
      `0x08012AEC -> aabb_query_080127AE`.
    - `candidate_caller_08021CC0` (body `..0x08021EAD`) contains both
      `0x08021DFE/08021E06 -> point_query`.
    - `candidate_caller_080220D8` (body `..0x08022149`) contains
      `0x08022142 -> aabb_query_08012846`.
  - New DB entries: `aabb_query_080127AE`, `aabb_query_08012846`
    (`STRONG_STATIC`; entries from ROM-008 independent BL decode).
  - Cross-validation: post-seed entry references for all three query entries
    list exactly the ROM-008 callsites with resolved source functions.
  - Static shape classifications (CANDIDATE semantics, boundaries candidate):
    - `candidate_caller_08006E3C`: parameterless global-driven frame handler;
      button bits (halfword at `*ctx+4` bit0/bit1), point query at a tracked
      entity, heavy use of message family `FUN_08011xxx`.
    - `candidate_caller_08012A24`: entity method; flag gate on global `+0xC`;
      table-indexed text/message calls (`FUN_08052fd4` +
      `FUN_08011c0c/08011c70`); the known `+0x16` halfword gate; sound-like
      `FUN_0800797c(0xf,0x4b)`. Entity position words at `+0xA0/+0xA4`
      (`>>8` fixed point).
    - `candidate_caller_08021CC0`: periodic dual-point spatial sensor with
      60-frame counters, animation-id getter `FUN_0802bfbc(0x6f..0x73,...)`,
      two dispatched objects' `+0x16` gates.
    - `candidate_caller_080220D8`: factory allocating 0x200 via shared
      allocator `FUN_0803d5b8`, installs table `_DAT_080222d8`, registers a
      child into the message family, then immediately runs
      `aabb_query_08012846` - area-effect/hitbox-spawner shape.
  - New subsystem anchors: allocator `0x0803D5B8`, resource-by-id getter
    `FUN_0802bfbc`, message/dialogue family `FUN_0801191a / 08011944 /
    08011a1e / 08011c0c / 08011c70 / 08011db4 / 08011e0e / 08011e94`
    (CANDIDATE roles).

- **AUTO-003 (2026-08-23), Ghidra static, calibrated project:**
  - `downstream_080075AC` (body `0x080075AC..0x08007673`) is a **map-transition
    executor** (STRONG_STATIC, semantics CANDIDATE):
    - gates on object vtable`+0x84` dispatch result halfword `+2` vs receiver
      byte `+0x11`;
    - invokes the object's vtable`+0x34` method with arg `2`, remembering the
      result;
    - calls `FUN_08008d44(global_ctx, byte[ctx+0x11], byte[ctx+0x12],
      ptr=ctx+0x14, byte[ctx+0x13], 1)` -> returns a NEW map-context pointer.
      `FUN_08008d44` sits inside the established map-load flow between the
      confirmed MapEntry-lookup BL sites `0x08008D2A/0x08008D6C`. Three bytes +
      pointer args match MapEntry's zone/area/variation byte shape.
    - transfers spawn-position byte (`ctx+0x10`, nibble logic) into new
      context `+0x10`;
    - when the vtable method returned nonzero: stores the pre-transition saved
      word at **new context `+0x8C`** - exactly where consumer-analysis placed
      the retained selected variation word - then dispatches the new context's
      table`+0x28` method (population-shaped);
    - else allocates a 0xC-byte pending marker object via `FUN_0803d5b8`.
  - Trace-site functions recovered and named:
    `candidate_trace_site_080077EC` (`..0x08007853`, calls `08009744`),
    `candidate_trace_site_08009744` (`..0x080097A5`, calls `080094B8`,
    callers also `08007916`, `080211fa`),
    `candidate_trace_site_080094B8` (`..0x080094EF`, copy-shaped).
  - Interpretation (INFERRED): accepted spatial actions of this family execute
    area transitions; VERTICAL-001's persisting transition therefore likely
    came from another accepted containment on some other descriptor-driven
    object or another mechanism feeding the same loader.

- **AUTO-004 (2026-08-23), read-only static census, canonical profile:**
  - `CONFIRMED`: 839 four-aligned words match confirmed factory raw values
    (`669 x 0x08007675`, `170 x 0x080072CD`); ALL decode as shape-plausible
    descriptors (odd Thumb-shaped `+0x04`, ordered signed bounds). Nearly all
    share `+0x04 = 0x0800776D`; an earlier data region uses `0x080077DF`.
    Strong global support for the descriptor field map (extent still
    unproven; feeds AUTO-006).
  - `CONFIRMED`: exactly ONE candidate besides `0x08294948` overlaps the
    doorway rectangle: `0x081BE1B8`, bounds `(600,176)..(609,201)`.
  - `CONFIRMED` ownership chain for that candidate:
    descriptor <- array `0x081BE260[7]` of 14 pointers <- selected value
    `S=0x081BE298` (`+0x40`=14, `+0x44`=array; word0 `0x000C1041`) <-
    variation source `0x0808AEBC[0]` <- **MapEntry 377**
    (out=15, zone=19, area=1, variation=5). Different map: its map-local
    bounds cannot fire at MapEntry-39's doorway.
  - `CONFIRMED`: MapEntry 39's variation source `0x080753F0` contains exactly
    one selected-value-shaped structure (`source[0] = S39`); no selector!=1
    alternative population exists statically there.
  - Consequence (INFERRED, strong): after the VERTICAL-001 patch, NO
    descriptor-driven registry member of MapEntry 39 could accept containment
    at the doorway. The persisting transition must come from non-descriptor
    registry members (heterogeneous population, e.g., entity-spawned) or a
    non-registry mechanism. New queue items AUTO-010/AUTO-011 target these.
  - INFERRED leads (unproven): descriptor byte10 clusters by rectangle shape
    (`00` interior/bottom strips, `01` top strips, `02` left strips,
    `03` right strips); byte11 clusters by map group (MapEntry-39 pair has
    `01`, MapEntry-377 set has `0F`). Descriptors also carry unknown halfword
    fields at `+0x12/+0x14`.

- **AUTO-010 (2026-08-23), Ghidra static, calibrated project:**
  - `candidate_map_loader_08008d44` (body `0x08008D44..0x08008E6F`) is the
    map-transition loader (STRONG_STATIC):
    - writes its zone/area byte args into context `+0/+1`;
    - adjusts spawn coordinates by `-0x70, -0x4C`;
    - calls **`FUN_080089fc`** (the CONFIRMED MapEntry lookup) and feeds the
      result plus adjusted spawn into **`FUN_08008b30`** (the established
      map-load flow);
    - spawns entities through an 0x18-stride per-type table
      (`FUN_0801713c`, `FUN_080109aa`/`FUN_080104f2`, allocator wrappers,
      list-add `FUN_08021094`, message attach `FUN_0801191a`);
    - compares `FUN_08008a36(ctx+4)` music id against ctx `+8` and attaches a
      change object on difference (map BGM switch).
  - Additional direct callers of the loader: `FUN_080022e6`, `FUN_08002390`,
    `FUN_08005abe` - candidate non-door warp sources (scripts/NPCs).
  - Transition chain now end-to-end statically: containment -> filter ->
    `spatial_action_080125E8` -> `downstream_080075AC` ->
    `candidate_map_loader_08008d44` -> MapEntry lookup + load flow.

- **AUTO-011 (2026-08-23), Ghidra static + xref census:**
  - `CONFIRMED` (static): `registry_populate_08012664` has exactly ONE
    caller - `population_adapter_08009670`. The descriptor-array path is the
    only feeder of that primitive.
  - `CONFIRMED` (static): a SECOND independent registry-append site exists at
    `candidate_registry_writer_08009172` (body `..0x08009195`): reads an
    object pointer from `*(arg+4)+0x10 + idx*8 + 4` (8-byte-stride record
    table), dispatches vtable[0] via `FUN_08046aa2`, appends result to the
    manager reached through literal `DAT_080091fc+0x10`. Its only recovered
    callsite is `0x080026FC` (containing function unrecovered).
  - Manager-global `0x03002A64` xref census (25 refs): known sites plus
    direct READ/WRITE accessors `FUN_0800d30e` (`0x0800D4C0/C4`),
    `FUN_08017f5a` (`0x0801804A/E`), `FUN_08018078`, `FUN_08018346`,
    `FUN_0803643c`, `FUN_0803656c` (x3), `FUN_08036914`, `FUN_08002862`,
    and DATA references at `0x08070190`, `0x080707B4/E0/E4`. The reset at
    `0x08048488` did not appear in recovered xrefs (likely unrecovered
    literal flow; not evidence of absence).
  - Consequence (INFERRED): the spatial registry has multiple mutation sites;
    non-descriptor members (e.g., entity-spawned) remain a live candidate for
    VERTICAL-001 C. Refined into AUTO-012.

- **AUTO-012 (2026-08-23), Ghidra static + byte decode - VERTICAL-001
  RESOLVED:**
  - `CONFIRMED` (static): containing function of callsite `0x080026FC` is
    `candidate_registry_spawn_080026EA` (`..0x08002701`): pops an index from a
    `{count, elems[]}` stack-array and calls the writer with the map-context
    global **`0x0300197C`** (literal chain `0x08002954 -> 0x08054FBC+0xC`).
    Reached via function-pointer table entry `0x080552C0 -> 0x080026EB`
    (dense engine dispatch table region `~0x08055284..`).
  - `CONFIRMED` (static): `candidate_registry_writer_08009172` iterates
    **`MapEntry[+0x10] triggers_pointer_raw` as 8-byte records** (count =
    MapEntry `+0x04`), reads each record's `+4` pointer, and dispatches its
    vtable[0] to construct the registry member.
  - `CONFIRMED` (static): handler `candidate_trigger_handler_0800742C`
    allocates the SAME 24-byte rectangle object and runs the SAME common
    initializer `FUN_08009AEC`; source field roles identical to spatial
    descriptors (`+04` callback producer, `+08/+0C` bounds); installs family
    vtable base `0x08049BD4`; copies source `+0x10` word to object `+0x14`.
    Trigger objects are first-class rectangle members of the same registry.
  - MapEntry 39 has 11 trigger records; record[1] type `0x00020006` ->
    source `0x080755C0`: producer `0x08007791`, bounds **`(481,121)..(615,271)`
    - CONTAINING the entire doorway rectangle `(592,136)..(601,241)`**
    (`producer candidate_trigger_producer_08007790` builds an 8-byte receiver
    `{table 0x0804ACE0, 0}`).
  - CAUSAL CHAIN for VERTICAL-001 result C (STRONGLY SUPPORTED, Level 2/3
    boundary): after descriptor `0x08294948` was emptied, the player still
    stood inside trigger[1]'s rectangle; the generic point query accepted it;
    ITS action path executed; the transition persisted. The exact concrete
    action target behind receiver table `0x0804ACE0` is UNKNOWN (computed
    dispatch; no static refs beyond producer). Per steering rule this does
    not change the resolution.
  - OLD CLAIM / NEW EVIDENCE / RESOLUTION:
    - OLD: "The remaining transition source is not established" (VERTICAL-001,
      PROJECT_STATE unresolved list).
    - NEW: trigger-array population path + containing rectangle identified.
    - RESOLUTION: descriptor-driven doorway was one of at least two overlapping
      accept regions on MapEntry 39; the trigger-family member persists.

- **P-001 progress (2026-08-23), Ghidra static - player entity anchors:**
  - `CONFIRMED` (static): `candidate_entity_ctor_a_080109AA` allocates a
    **0x240-byte entity**, base-initializes via `FUN_0800e6b8`, installs table
    base (literal `0x08010b68`), and stores the entity into global
    **`0x03001C34`** (write at `0x080109e6`; literal `0x08010b6c`). It then
    attaches a per-type component chosen through a `0x68`-stride record array
    (`FUN_0801714a`) and dispatches its vtable[0].
  - `STRONG_STATIC`: the stored `0x03001C34` entity is the player-controlled
    entity candidate: ROM-009 identified that slot as the point-query context;
    ROM-012's query entity tracked human movement; frame handler
    `candidate_caller_08006E3C` queries at this slot's value.
  - `CONFIRMED` (static): wrapper ctor `candidate_entity_ctor_b_080104F2`
    (0x240 alloc, calls ctor_a with flag 1, overrides vtable, attaches a
    0x10-byte sub-object via `FUN_0800ed18`, `FUN_0800ecda(ent,0xf)`); called
    by the map loader in its alternate branch.
  - `CONFIRMED` (static): `candidate_entity_dispatch_08013914(entity, arg)` is
    an **entity state-machine tick**:
    - gate: halfword `entity+0x16 != 0` (the ubiquitous +0x16 gate);
    - state-group byte at `+0x14` indexes a 0x18-stride table
      (`DAT_08013b9c`);
    - current/next state halfwords at `+0x16/+0x18` (+ copies to `+0x1A/
      +0x1C`) advance on timer expiry (`FUN_080135d2` reads `+0x24` timer;
      threshold from table; advance via `FUN_08013678`; sound wrappers
      `FUN_0800f53c/f558` around `FUN_0801064c`);
    - nibbles of `entity+0x02` select two 0x68-stride per-character records
      at `DAT_08013ba0+0x4f8` (recursion over both; `FUN_0801375e` on
      transition).
  - Update-root candidate: `FUN_080043d8` (sole non-recursive caller of the
    tick) - NEXT decompile target.
  - `CONFIRMED` (static): `candidate_frame_update_080043D8` is a thin adapter:
    `tick(base + base[0]*0x68 + 0x4f8)` - i.e., it runs the entity state
    machine for the ACTIVE record of the recurring 0x68-stride per-character
    array (leading byte = active index). Its caller is `FUN_080033d2`
    (next link toward the frame scheduler).
  - `CONFIRMED` (static): scheduler chain completed -
    `candidate_game_tick_080033D2(tasklist)` pops a task (`count--`, element
    `[count]`) and ticks it with base = `[0x08054FBC]+0x14` = IWRAM
    **`0x03001068`** (reached via function pointer; no direct BL callers).
  - `CONFIRMED` (byte-level): game-state block at IWRAM `0x03001068`
    (`+0x00` active character byte; character records begin at `+0x4F8`);
    record array base in ROM at **`0x086B7578`** (`DAT_08013ba0=0x086B7080`
    literal pool + 0x4F8). The tick's `DAT_08013ba4` is literally
    **`0x03001C34`** - the state machine directly drives the player-entity
    slot.
  - Observation: character records embed UTF-16 dev labels (record[0]
    begins `'state data "'`) followed by packed parameter groups pairing ROM
    data pointers (`0x086B75DC/61C/65C/69C...`) with consecutive IWRAM words
    (`0x03002B88..0x03002B94`). Layout semantics UNKNOWN; likely per-state
    definitions. P-002 will decode as needed.
  - P-001 answer summary: player entity = object stored at `0x03001C34`;
    update path = task stack -> `candidate_game_tick_080033D2` ->
    `candidate_frame_update_080043D8` -> `candidate_entity_dispatch_08013914`
    (state machine) over active character record.

- **P-002 progress (2026-08-23), static - input/position anchors:**
  - `CONFIRMED` (byte-level): ROM table `0x08070180` is a master global
    directory: `[0]=0x03003300` (system/input ctx), `[1]=0x03003898`,
    `[2]=0x030019A4`, `[3]=0x03001068` (character block),
    `[4]=0x03002A64` (spatial registry manager), `[5]=0x03001C4C`.
    Only two literal-pool references exist to the directory
    (`0x08006FE0` frame-handler pool; `0x0804FDB0`).
  - Behavioral fact (raw): button state is read as
    `*(u16*)(*(0x08070180)+4)` = `*(u16*)(0x03003300+4)`; masks observed:
    `& 0xF3` (text entry gate), `& 0xF0` (interact toggle). Bit meanings and
    the +4 writer are UNKNOWN (no KEYINPUT literal anywhere in ROM -> IRQ or
    computed-address copy).
  - Behavioral fact (raw): positions are 32-bit fixed-point words whose
    map-pixel value is obtained with `>>8` (integer part in upper bits;
    "32-bit fixed-point with 8 fractional bits", not 8.8). Seen as
    `param+0xA0/+0xA4` in `candidate_caller_08012A24`; point query compares
    `>>8` values against descriptor bounds; projectile stepper integrates
    `pos += vel` on the same representation.
  - Behavioral fact (raw): `candidate_input_acc_b_0802C564` writes entity
    `+0x1A0/+0x1A4` from stored coords before dispatching vtable[+0x28] on
    both entities - warp/respawn-position shape (INFERRED purpose).
  - Behavioral fact (raw): linear-animator pattern in
    `candidate_input_acc_c_0802D940`: per-tick `field+0x20 += field+0x40`,
    `+0x24 += +0x44`, frame counter `+0x48` wraps at 24 ticks, row stride
    0xC into `+0x4C` table (sprite/frame stepper candidate; INFERRED).
  - Next P-002 step: identify the `0x03003300+4` writer (IRQ/main-loop key
    copy), then follow direction-bit consumers into entity velocity writes;
    recover cardinal/diagonal speeds.

- **P-002 progress 2 (2026-08-23), static - dev labels + first combat
  quantities:**
  - `CONFIRMED` (byte-level): UTF-16 developer diagnostics embedded before
    the character-record region:
    - `0x086B7400`: "Energy attack level set for attack which doesn't exist
      for player!"
    - `0x086B748C`: "Energy attack level requested for attack which doesn't
      exist for player!"
    - `0x086B7524`: "Unable to find sprite index in character state data"
    Literal-pool refs: `0x08013BC8` and `0x08013E20` - an energy-attack
    accessor cluster immediately after the state-machine tick (P-003 lead).
    INTERNAL DEVELOPER EVIDENCE only; semantics to be validated against
    executable behavior before naming.
  - Record-region layout note: record[0] is a `'state data "'` header;
    subsequent 0x68-stride slots are heterogeneous (pointers like
    `0x086B7CCC`, packed bytes) - the uniform-record model needs revision;
    treat 0x68 indexing as into a mixed state-data blob until decoded.
  - `CONFIRMED` (static): `candidate_player_update_080247BE` (body
    `..0x080248DB`) is a projectile/effect stepper, NOT the walking player.
    Behavioral spec captured anyway (first concrete combat quantities):
    - integration per tick: `pos+0x20 += vel+0x48`; `pos+0x24 += vel+0x4C`
      (32-bit words, 8 fractional bits);
    - animation counter `+0x50++`; anim byte `+0x44 = counter>>2`;
      frames table at `+0x54` stride 0xC; after counter>>2 >= 5 the object
      detaches via message-family remove (`FUN_08011944`);
    - hitbox: rect `(pos>>8 -8) .. (pos>>8 +8)` on both axes = 16x16 pixels,
      tested against target bounds by AABB helper `FUN_0800fe78`
      (`iStack_* < ...` overlap form);
    - on hit: attach to target (`FUN_0800e9d8`), dispatch target vtable
      `+0x5C`, then vtable[+0x34] with id 0x17, and on nonzero vtable[+0x28];
      sets self flag `+0x40=1`;
    - a timer clamp compares two globals' `+4` fields and raises the lower
      to the higher (cooldown-style; roles UNKNOWN).
  - Next P-002 step unchanged (buffered-input consumers -> walk speed);
    P-004 anchors now include projectile integration + hitbox + hit dispatch.

## Function Knowledge

See `SUBSYSTEM_MAP.md` for the consolidated table. Confidence vocabulary:
`CONFIRMED` (runtime or byte-exact), `STRONG_STATIC` (static executable
behavior, multiple corroborations), `CANDIDATE` (single static observation).

## Structures

- `MapEntry` 0x38 bytes, 452 records at `0x0808E2E0` - CONFIRMED layout,
  field semantics mostly INFERRED/UNKNOWN (see reverse-engineering.md).
- Runtime rectangle object 0x18 bytes - bounds `+0x04..+0x0B` signed halfwords
  (CONFIRMED), callback reference `+0x0C`, retained descriptor `+0x14`,
  dispatch-table base `+0x00`.
- Source spatial descriptor - `+0x00` raw factory, `+0x04` unknown
  (callback-producer input), `+0x08/+0x0C` bound pairs; extent UNKNOWN.

## Blockers

- BSim uncalibrated: no genuinely distinct locally ingestible binary.
- Recomp repos ship no generated C++ (`generated/` empty), so no recomp symbol
  transfer surface exists.
- mGBA GUI-launch approval quotas historically flaky; native SDL probe path
  (ROM-011+) avoids Lua injection.

## Next Candidate

P-001 (player entity + update root) - top of the player/combat pivot.
Transition frontier is CLOSED; do not spend further units on transition
taxonomy (AUTO-005 vtable dump remains READY but demoted below P-series).
