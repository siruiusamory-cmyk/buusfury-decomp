# TOOLKIT-022 - Authored placement representation

Outcome B: semantic AUTHOR_NEW representation and production-codec serialization
are implemented. Materialization is refused on a specific ownership invariant,
including with synthetic verified capacity. This is not Outcome A and does not
establish a playable new ROM placement.

## Project schema and identity

Project version remains **1**. The additive `authored_placements` map table is
unambiguous: existing `placements` remains the extracted canonical collection;
the new collection contains `AuthoredPlacement` models with explicit
`AUTHORED_CLONE` provenance. Earlier readers reject the unknown map field rather
than silently dropping additions. Existing projects need no migration, normal
extraction emits no additions, and unsupported future versions still fail.

Example inside `maps/maps.toml`:

```toml
[map."map:0010".authored_placements."map:0010/authored:extra-wolf"]
provenance = "AUTHORED_CLONE"
clone_from = "map:0010/placement:0000"
position_low = 123
position_high = 456
```

Use the CLI instead of writing opaque internals:

```powershell
webfoot placement clone PROJECT --map map:0010 --source map:0010/placement:0000 --name extra-wolf --position-low 123 --position-high 456
webfoot placement plan PROJECT --rom BASE.gba
```

The Python surface is `project.placements.clone_placement`; planning is
`build.authored_capacity_plan`. The explicit name is stable project identity,
map-scoped and disjoint from `placement:NNNN`. It never depends on ROM allocation
or filesystem order. It is not an engine `id_raw`. Future modified-ROM extraction
will need to retain project provenance to recover names; that work is not claimed.

A clone is a new serialized record, not an alias to the source's address.
Structure comes from verified canonical template bytes, not position edits to
the source project row. Only the two position halfwords can be overridden.
Type, descriptor, ordered children, `id_raw`, flags and every unknown word are
copied exactly. No type/child/descriptor fabrication, deletion or retyping API
was added. A source may be another represented map's canonical placement.

Canonical rows must still reconcile exactly to base identities and bytes.
Missing rows, duplicate indices, unsupported structural changes and unexplained
identity drift fail. Canonical order is retained; authored IDs sort after it.
The old count equality guard remains exclusively on the extracted collection;
explicit additions increase only the planned target count.

## Serialization and proposed capacity

Both existing rows and clones use `PlacementRecord.with_position().to_bytes()`.
Synthetic tests exercise all supported child counts 1..4 and exact sizes
`0x1C + 4*n`; bytes outside the allowed position word remain exact.

An `AuthoredRun` retains each record's semantic ID, provenance, clone source,
serialized bytes and owning map. Its existing `AllocationRequest` proposes a
contiguous packing of all record bodies plus one pointer slot per target record.
This is explicitly **PROPOSED_NOT_APPROVED_ROM_LAYOUT**: no engine terminator,
suffix or count field is invented. The size is exact for that proposal, not a
confirmed complete runtime array footprint. Planning JSON omits commercial bytes.
It reports no allocated address or rewritten references because neither exists.
Failed builds publish neither output ROM nor success manifest.

## Exact ownership blocker

> **SUPERSEDED IN PART BY TOOLKIT-024.** The "UNKNOWN engine consumption" bullet
> below is resolved: the outer traversal is a counted loop over `MapEntry+0x04`
> at `0x08008C9E`, with no sentinel and no suffix, so a run owns exactly
> `count * 4` array bytes. The blocker is now narrower - a run cannot grow
> because no production write path can rewrite a count field. The `+0x05`
> reference below was the wrong field. See
> [placement-run relocation](BUU_PLACEMENT_RUN_RELOCATION.md).

These are existing evidence/code facts, not new reverse engineering:

- **CONFIRMED representation:** map `+0x14` points at the placement reference
  array; each slot points at a separate variable-length body. The graph declares
  these refs CONFIRMED, but every corresponding anchor is non-relocatable
  (`tools/webfoot/entities.py:181`, `:185`, `:200`).
- **UNKNOWN engine consumption:** production uses trusted census run counts;
  `MapEntry+0x05` is explicitly not a verified placement count
  (`tools/webfoot/maps.py:324`). The count-free helper's non-family stopping rule
  is for synthetic/legacy traversal, not proof of the engine's rule
  (`tools/webfoot/formats/map_placements.py:146`).
- The graph owns exactly `count*4` pointer bytes; it neither retains a terminator
  nor establishes suffix ownership (`tools/webfoot/entities.py:203`,
  `tools/webfoot/maps.py:770`). Rewriting `+0x14` alone cannot establish safe
  consumption of an expanded array.
- The existing relocator rejects fixed anchors before allocating
  (`tools/webfoot/relocation.py:63`). Moving bodies would additionally encounter
  the read-only indexed type reference (`tools/webfoot/entities.py:210`,
  `tools/webfoot/layout.py:147`). Its existing-anchor move contract does not
  create clone anchors or newly appended reference sources
  (`tools/webfoot/relocation.py:69`, `:77`, `:84`).

Therefore the new build gate refuses materialization before allocation. No
reference evidence is promoted, no `relocatable` flags are flipped, no pointer
is fabricated, and no allocator/relocator/profile data was changed.

Minimum prerequisite: establish the engine-consumed placement array extent and
growth/count/termination rule, including ownership of its suffix. Then implement
new clone/ref-source graph declarations under that contract. TOOLKIT-011 capacity
work alone does not remove this prerequisite. No new RE ticket was opened.

## Measured canonical and synthetic results

Canonical example: `map:0010`, source `map:0010/placement:0000`, authored identity
`map:0010/authored:toolkit022`, position `(123,456)`. Two 32-byte canonical records
plus one 32-byte clone serialize to **96 bytes**; three proposed pointer slots
add **12 bytes**, for a deterministic **108-byte**, 4-aligned capacity request.
Project parsing, semantic validation and authored-ID resolution pass.

> **SUPERSEDED by TOOLKIT-026 (relocation) and TOOLKIT-025 (count).** The two
> reasons quoted in the TOOLKIT-022 error below are both resolved. The engine
> count is `MapEntry+0x04`, proven by disassembly (TOOLKIT-024) and now written
> as a derived, validated `ByteChange`; `MapEntry+0x05` was never the count. The
> `placement_reference_array` anchor is no longer published `relocatable=False`:
> its measured reference set satisfies the relocation safety contract, and
> `plan_relocation` moves it and rewrites the `MapEntry+0x14` owner pointer. The
> current blocker is unmodelled authored record bodies. See
> [BUU_MAP_OBJECT_ARRAYS.md](BUU_MAP_OBJECT_ARRAYS.md).

Production **build** raises `LayoutError` (TOOLKIT-022 form, superseded):

```text
map:0010/placement_references: valid authored placement content serialized; proposed capacity request 108 bytes, alignment 4; materialization blocked by non-relocatable placement_reference_array: MapEntry+0x14 reference is CONFIRMED, but expanded-run engine count/termination and suffix ownership are UNKNOWN (MapEntry+0x05 is not a verified count). Verified capacity alone does not authorize this rewrite.
```

A separately labelled **capacity feasibility check** submits that same request
to the existing allocator and raises `InsufficientSpaceError`:

```text
insufficient declared free space for map:0010/placement_references (108 bytes, alignment 4)
```

This is not a claim that production build reached allocation. Production Buu
still has zero verified free regions; no candidate tail was consulted.

Synthetic verified space accepts the equivalent 108-byte request deterministically
at file offset **0x10000**. The existing relocator then rejects the actual
synthetic placement graph's fixed run anchor. **No relocation, owner rewrite,
output ROM or materialized authored address is claimed.** Capacity is necessary
but demonstrably insufficient under the existing ownership contract.

Two canonical extractions without graphics produced **7 byte-identical files**.
No-op build reproduced **8,388,608 bytes** exactly. Two authored build attempts
failed identically without output. Canonical SHA-256 and mtime remained unchanged:
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
No emulator, save/state, runtime or playable-behavior test was performed.

## Capability and closure answers

| Capability | Result |
|---|---|
| Existing placement READ / ROUND_TRIP / supported position WRITE | Preserved |
| Describe a placement absent from canonical ROM | YES |
| Serialize it through the real placement codec | YES |
| Materialize with verified capacity | NO - ownership contract blocks |
| Canonical Buu AUTHOR_NEW placement | NO - ownership gate, also zero capacity |
| Old placement-count mismatch removed as authored-addition blocker | YES |
| TOOLKIT-011 is the next sole actual blocker | NO - ownership prerequisite first |

Validation/review/commit details are recorded in the active ticket and the bounded
PROJECT_STATE_3 entry after the integration gate completes.
