# MAP-WARPS-AND-CONNECTIONS-001 - editing map transitions

STATUS: **NOT STARTED.** Phase 2D. This ticket was displaced once by
`WEBFOOT-LZ-LITERAL-BASE-001`, which was executed, reviewed and merged first
(2026-09-26); its text was parked in `MAP-WARPS-AND-CONNECTIONS-001.md` for that
pass and is restored here verbatim.

**This file is not the roadmap.** The approved route to 24/24 and v1.0 lives in
[`../ROADMAP_TO_1_0.md`](../ROADMAP_TO_1_0.md); read its Phase 2 section and its
section 13 for this work rather than restating them here. The fixed capability
denominator and the open technical risks live in
[`../../src/data/capabilities.json`](../../src/data/capabilities.json) and
[`../research/PROJECT_CODE_QUALITY_AUDIT.md`](../research/PROJECT_CODE_QUALITY_AUDIT.md).

**Phase 2A (tile painting), 2B (chunk creation) and 2C (map resizing and layer
authoring) are COMPLETE and integrated.** Predecessor closures:
[`archive/MAP-TILE-PAINT-001-COMPLETE.md`](archive/MAP-TILE-PAINT-001-COMPLETE.md),
[`archive/MAP-CHUNK-AUTHORING-001-COMPLETE.md`](archive/MAP-CHUNK-AUTHORING-001-COMPLETE.md)
and
[`archive/MAP-RESIZE-AND-LAYERS-001-COMPLETE.md`](archive/MAP-RESIZE-AND-LAYERS-001-COMPLETE.md),
whose evidence records are [`MAP-TILE-PAINT-001.md`](MAP-TILE-PAINT-001.md),
[`MAP-CHUNK-AUTHORING-001.md`](MAP-CHUNK-AUTHORING-001.md) and
[`MAP-RESIZE-AND-LAYERS-001.md`](MAP-RESIZE-AND-LAYERS-001.md). **CQA-05** through
**CQA-09**, **CQA-12** and **CQA-15** are CLOSED and must not be reopened.
**CQA-10 remains PARTIAL / IMPROVED** and is not part of this ticket.

## Objective

Deliver Phase 2D: an author can create and edit a map's transitions - where one
area connects to another - and have the retail engine consume the edit. When it
ships, the product moves from **19 / 24** to **20 / 24**, and the `warps`
capability in the registry is the only authority for that count.

## Context delta

- The transition contract is already read, not guessed: all **735** transition
  records behind the 452 map roots parse with no anomalies, the record is a 24-byte
  block reached from a root's `+0x40`/`+0x44` count/array pair, and the destination
  is a two-byte map key at `+0x11`/`+0x12` resolved against the MapEntry key table.
  **Reading a transition is not editing one**: no surface writes a transition
  record, and the fields past the destination key are recorded with meanings still
  `UNRESOLVED`.
- Phase 2C established two facts this ticket will need and must reuse: a map root's
  pointer fields are full 32-bit GBA addresses the retail engine follows above the
  canonical EOF, and a map whose root is **shared** with another map cannot be
  edited in place - 11 canonical roots serve more than one map.
- The runtime methodology is unchanged and mandatory: a savestate restores the
  already-assembled background, so a capture is valid only after an observed
  leave-and-re-enter. **Runtime proof is human-operated** - no scripted player
  input, which is a permanent rule after Phase 2C's recorded process violation.
- Reuse the existing map view and model, the existing undo system, the identity and
  provenance rules, the production allocator and the one write plan. Do not add a
  second rendering, editing or allocation path.

## Required Work

1. Establish by measurement what a transition record actually is: which fields the
   engine reads, which of them are safe to author, and what the engine's own limits
   are - so an unsupported transition form is refused before it is planned.
2. Implement transition authoring through the production write path, persisting
   semantically and allocating only through declared free space plus generated
   expansion.
3. Make the result observable and revisable in the Workbench: transitions drawn and
   edited on the existing map surface, one undoable gesture, reopen reproducing the
   authored transition.
4. Prove it end to end: the project reopens, a built image contains the authored
   transition, the canonical input is still refused as a write target, and the
   retail engine consumes the transition after a genuine rebuild.
5. Add focused regressions with named failing nodes and one mutation that restores
   the old behaviour, keeping the change bounded to this capability.

## Scope Boundaries

- Do not change the canonical ROM, and do not commit ROM-derived fixtures or
  runtime captures. Do not lower a real assertion to make a gate green.
- Do not implement new maps, graphics import, collision editing, sprite or
  appearance authoring - those are Phase 3 and later.
- Do not re-open Phase 2A, 2B or 2C's accepted limits, and do not weaken the
  fail-closed refusal list.
- Do not weaken `tools/webfoot/profile.py`, the identity checks, output and source
  separation, allocation authorization or provenance.
- Do not touch CQA-10, and do not reopen CQA-01 through CQA-09, CQA-12 or CQA-15.

## Ticket-Specific Validation

- The transition operation, demonstrated on a real map with a real rebuild.
- A named regression that fails on the pre-edit shape, with the failing node
  recorded, plus the mutation that restores the old shape.
- The reopen, build and identity-refusal proof named in Required Work.
- Focused named-file tests only, `git diff --check`, and the gates for the changed
  surface. Broad validation belongs to CI.

## Required Review

Independent code-review gate per [`../../docs/DEVELOPMENT.md`](../../docs/DEVELOPMENT.md) using
[`REVIEW.md`](REVIEW.md), with a fresh-context reviewer given the
ticket, the START SHA, the frozen SHA and the frozen worktree. A review is launched
only when its verdict can be read.

## Completion Criteria

- A supported map's transitions can be authored, materialized, reopened and
  consumed by the retail engine, and the addressability the feature needs is proven
  rather than assumed.
- Because every write must use the flow
  `verified base -> working copy/generated output -> patch/output ROM`, the
  canonical input is still refused as a write target and the canonical ROM is
  unchanged.
- Reopen reproduces the authored transition byte-exactly, and the build is
  deterministic.
- Focused tests pass, the independent review returns a verdict with no unresolved
  blocking finding, and the `warps` capability is marked shipped only after the
  work is done and reviewed.

## Stop

Stop when transition authoring is implemented, proved and reviewed.

Do not begin MAP-NEW-MAPS-001 or any later capability in this pass. Do not
implement new maps, graphics import, or sprite or appearance authoring, and do not
reorder the roadmap's phases.

No capability count may be advanced before the work is done and reviewed: the
capability registry is the authority, and reaching 20 / 24 happens only when the
capability actually ships.

WORKBENCH-006 remains untouched and needs owner direction before it resumes. It is
not part of this ticket.

## Completed

- **MAP-RESIZE-AND-LAYERS-001** - CLOSED and reviewed (2026-09-26); Phase 2C map
  growth and supported layer authoring shipped, DragonByte Z **19 / 24 (79%)**;
  closeout
  [`archive/MAP-RESIZE-AND-LAYERS-001-COMPLETE.md`](archive/MAP-RESIZE-AND-LAYERS-001-COMPLETE.md).
- **MAP-CHUNK-AUTHORING-001** - CLOSED and integrated (2026-09-25); Phase 2B chunk
  creation shipped, DragonByte Z **18 / 24 (75%)**; closeout
  [`archive/MAP-CHUNK-AUTHORING-001-COMPLETE.md`](archive/MAP-CHUNK-AUTHORING-001-COMPLETE.md).
- **MAP-TILE-PAINT-001** - CLOSED and integrated (2026-09-25); Phase 2A tile
  painting shipped, DragonByte Z **17 / 24 (71%)**; closeout
  [`archive/MAP-TILE-PAINT-001-COMPLETE.md`](archive/MAP-TILE-PAINT-001-COMPLETE.md).
- **CQA-07-08-WORKBENCH-PERF-AND-CI-001** - CLOSED and integrated (2026-09-25);
  closeout [`archive/CQA-07-08-WORKBENCH-PERF-AND-CI-001-COMPLETE.md`](archive/CQA-07-08-WORKBENCH-PERF-AND-CI-001-COMPLETE.md).
- **CQA-05-06-WORKBENCH-STATE-AND-ERRORS-001** - CLOSED and integrated.
- **CQA-04-DECODE-STACK-AUTHORITY-001** - CLOSED and integrated.
- **CQA-03-15-IDENTITY-AND-EXTENTS-001**,
  **CQA-02-PACKED-STREAM-TERMINATION-001** and
  **CQA-01-OUTPUT-SAFETY-001** - CLOSED and integrated (2026-09-23).
