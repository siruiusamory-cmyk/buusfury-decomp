# Reverse-Engineering Research Ledger

Durable brain of the Webfoot reverse-engineering programme
(`OX-AUTO-RE`). Read this file first every loop iteration. Keep it compact;
detailed evidence lives in `docs/reverse-engineering.md`,
`docs/consumer-analysis.md`, and `docs/research/SUBSYSTEM_MAP.md`.

Rules of the lane: static-first, bounded units, evidence labels
`CONFIRMED` / `INFERRED` / `UNKNOWN`, runtime levels 0-4, never modify the
canonical ROM or user saves/states, narrow commits only, never commit
proprietary artifacts.

## Current Objective

AUTO-002: recover the containing functions behind the five verified point-query
callsites (`0x08006E4E`, `0x08021DFE`, `0x08021E06`, `0x08012AEC`,
`0x08022142`) in the calibrated Ghidra project by seeding those call
instructions, then decompile and conservatively name each containing caller.
Answers a recorded PROJECT_STATE unresolved question (who schedules spatial
queries).

## Research Queue

| ID | Subsystem | Question | Why useful | Known evidence | Suggested next method | Status |
|---|---|---|---|---|---|---|
| AUTO-001 | spatial-descriptors | What descriptors exist in the count-2 array at `0x08294960`, and does a sibling cover the ROM-012 doorway? | Directly targets the recorded smallest blocker of VERTICAL-001 C; extends descriptor format knowledge | Array base/count from ROM-007 runtime (`field_40_raw=2`, `field_44_raw=0x08294960`); descriptor `0x08294948` fully characterized | Read-only byte reads at file offsets `0x00294960..68` + both descriptors; decode factory/bounds fields; cross-check with `webfoot variation-arrays find-first-word` | RESOLVED |
| AUTO-002 | spatial-registry-callers | Which containing functions call point-query entries (`0x08006E4E -> 0x080126D4`, `0x08021DFE/08021E06 -> 0x080126D4`, `0x08012AEC -> 0x080127AE`, `0x08022142 -> 0x08012846`)? | Names the scheduler layer that decides when spatial queries run; open PROJECT_STATE unresolved question | Callsite instructions CONFIRMED by independent BL decode (ROM-008); Ghidra did not recover containing functions | Seed callsite instructions in calibrated Ghidra project; recover boundaries; decompile callers; conservative names | READY |
| AUTO-003 | transition-action | What does action `0x080125E8 -> downstream 0x080075AC` actually do (map reload? dialogue start?)? | Would explain transition mechanism and likely close VERTICAL-001 C mechanism question | Runtime: action executed and reached `0x080075AC`; trace hit `0x080077EC`, `0x08009744`, `0x080094B8`; no return within 512 steps | Ghidra: seed `0x080125E8`, `0x080075AC`, `0x080077EC`, `0x08009744`, `0x080094B8`; decompile; enumerate callees; look for MapEntry-load flow entry (`0x08008B30`) and registry reset (`0x08048488`) | READY |
| AUTO-004 | object-vtables | What methods live in dispatch tables `0x0804A09C`, `0x0804A0AC`, `0x0804E444`? | Defines the rectangle-object class hierarchy; every spatial object routes through these | Cleanup slot raw/fetch `0x080510A1/080510A0`; filter vtable[2] `0x08007769`; receiver base `0x0804A0AC` vtable[1]/[2] used | Ghidra data-word dump of each table; follow each raw target; classify per-slot semantics conservatively | READY |
| AUTO-005 | registry-manager | Complete function graph of registry manager around `0x03002A64` (`0x08012628`, `0x08012664`, `0x0801268A`, `0x080126D4`, `0x080127AE`, `0x08012846`, `0x08012900`, neighbors to `0x080128F2+`) | One coherent subsystem map for the best-understood engine area | Individual behaviors established in ROM-006/008/011/012 | Ghidra seeding + decompilation sweep over `0x08012600..0x08012A00` | READY |
| AUTO-006 | descriptor-format | What is the minimal extent/field map of a source descriptor such that parsing is lossless? | Recorded parser-readiness blocker across ROM-008..ROM-012 | Consumers read `+0x00` (factory), `+0x04` (callback producer), `+0x08/+0x0C` (bounds) | Static census of all descriptor accesses from all factories reached via variation arrays; adjacency analysis in ROM | READY |
| AUTO-007 | script-vm | How does the Buu bytecode VM relate to Legacy repo's 145-opcode LoG1 VM inventory? | Dialogue/quest scripting is a whole engine subsystem | `extern/Legacy/OpCodes.csv`, `DBZKit/Legacy/Games/BYTECODE_VM.cs` (LoG1 lineage, INFERRED transferability) | Locate Buu bytecode consumers from MapEntry script pointers; compare opcode dispatch shape | DEFERRED |
| AUTO-008 | bsim | Calibrate BSim against an independent related binary | TOOL-002 closed BLOCKED: no independent related binary locally | TOOL-002 archive | Needs a new local binary (e.g., another-region dump) before any work | BLOCKED |
| AUTO-009 | external-knowledge | Data Crystal / community addresses for Buu's Fury or LoG1/LoGII worth validating? | Cheap candidate anchors if any exist | None imported so far (deliberate) | Web search; record EXTERNAL CLAIM then validate against canonical profile before use | DEFERRED |

## Recent Discoveries

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

If AUTO-002 completes: AUTO-003 (static characterization of action
`0x080125E8 -> 0x080075AC`), reusing the same Ghidra session; AUTO-004 table
dumps can share that session's data-word queries but get recorded separately.
