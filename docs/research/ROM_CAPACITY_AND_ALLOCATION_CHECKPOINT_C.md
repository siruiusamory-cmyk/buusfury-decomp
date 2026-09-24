# ROM-CAPACITY-AND-ALLOCATION-001 - Checkpoint C

**The one production allocator authority, proved synthetically.** Checkpoint A
(`d7d5ca548adb3753b580b0144f6f02d38b5cfeea`) and Checkpoint B
(`9b0c4889f275d9066e984e9f4c5ddced5deb9e24`, record head `6d96593`) are frozen and
were accepted by the owner; neither is reopened here.

This checkpoint is headless SDK infrastructure. It is **not** the real-ROM runtime
proof - that is Checkpoint D - and it is **not** wired into any GUI.

## 1. One authority, extended not duplicated

`tools/webfoot/allocation.py` remains the only allocator. No `allocation2.py`,
`new_allocator.py` or `production_allocator.py` exists, and
`test_there_is_exactly_one_allocator_module` asserts that literally. The module
was extended in place; `withhold` is unchanged and still the one subtraction
primitive every allocating domain threads its reservation set through.

| Before | After |
|---|---|
| `AllocationRequest(anchor, owner, size, alignment)` | the same four positional fields, plus a **required keyword-only** `kind`, plus `addressability`, `evidence` and `constraints` |
| `Allocation(request, range, free_region_evidence)` | plus `storage_class`, `source_region`, `canonical_size`, `image_size`, `order`, `policy` |
| `allocate(profile, requests, *, occupied, capacity_regions, image_size)` | `allocate(profile, requests, *, storage, occupied)` |
| free regions came from `profile.free_regions` plus an ad-hoc `capacity_regions` argument | a `StorageModel`: canonical `VERIFIED_FREE` plus the profile's **explicitly declared** `PADDING_EXPANDED` |

The three production call sites now state their semantic kind explicitly:
`compressed_dialogue` (packed stream, expanded-permitted), `authored_placements`
(placement body; and the whole-map proposal), `relocation` (placement reference
array, text string, or the conservative generic relocated payload).

## 2. The input contract

The allocator's whole input is declarations. It does not read image bytes, does
not scan for `FF`/`00`, does not open a file, and does not import the structural
atlas or the Phase A research model - all four are asserted structurally in
`test_the_allocator_does_not_read_image_bytes`.

```text
resolved RomProfile identity and size
+ StorageModel: declared regions, each with a class and an evidence string
+ existing reservations (OwnedRegion spans)
+ AllocationRequest: identity, kind, size, alignment, addressability, evidence
-> tuple[Allocation]
```

`StorageModel.from_profile` is the only production construction, and it takes the
expanded region from `profile.generated_expansion` alone. A generated image that
is merely larger produces no model entry, which is what "a bigger file authorizes
nothing" means in code.

## 3. Region-class safety

`ALLOCATABLE_REGION_CLASSES = {VERIFIED_FREE, PADDING_EXPANDED}` is the single
decision point. `OWNED`, `REFERENCED` and `UNKNOWN` are exclusion evidence:

* a model whose allocatable region overlaps an exclusion region is **refused at
  construction** (`RegionClassError`), not resolved by precedence;
* a model offering only `OWNED`, `REFERENCED` or `UNKNOWN` yields
  `InsufficientSpaceError`.

`UNKNOWN` is the class the project's own measurements could not classify, so it is
the one that matters most, and it is the mutation M3 target.

**Candidate free space was not promoted.** The 115 promotable runs and 23,595
candidate bytes from Phase A are unreachable from `allocation.py` by construction -
it never sees a candidate, a fill run or an image. The canonical profile still
declares the single 256-byte TOOLKIT-028 window, and that is still all it can
allocate.

## 4. Expanded storage and addressability

An expanded region enters a model only through the profile's declaration, only an
`EXPANDED_PERMITTED` request may use one, and
`Allocation.generated_allocation_provenance(...)` is what converts the placement
into the write-layer authorization. It **refuses** for a canonical allocation,
because minting expansion provenance for canonical bytes would authorize a span
outside the declared expansion.

Addressability is applied in exactly one place (`_candidate_regions`): a
canonical-only request never sees the expanded region. From the Phase A
addressability matrix - 16 domains inventoried, 1 engine-proven above EOF, 13
unproven - `DEFAULT_ADDRESSABILITY` marks only `PACKED_STREAM` as
expanded-permitted. Every other kind defaults to canonical-only, so a domain that
has not been proven capable cannot silently receive an expanded address.

## 5. Deterministic policy

```text
ALLOCATION_POLICY = "lowest-aligned-first-fit/v2: requests ordered by anchor
identity (total, no ties); each takes the lowest aligned address that fits in the
first allocatable region, by ascending region start, clear of every reservation"
```

Ordering is by `AnchorId`, which is a total order, and duplicate identities are
refused - so the ordering has **no ties to break**, which is stated rather than
left implicit. Every `Allocation` records the policy string and its `order` index.
Nothing consults dict, set or filesystem order. Proven by permuting the request
list and the region list independently and asserting byte-identical results.

## 6. Collisions, alignment and fail-closed

* Every completed placement joins the reservation set before the next request is
  placed, so a batch cannot overlap itself.
* Overlapping reservations are **refused**, not merged: two owners claiming one
  span means at least one is wrong.
* Alignment `1, 2, 4, 8, 16, 256` is proved. Padding may not escape its source
  region, and a padded request that no longer fits is refused rather than shrunk.
* Invalid alignment (`0`, `-1`, `3`, `6`, `True`) fails clearly.
* An impossible request raises `InsufficientSpaceError` naming the size,
  alignment and kind. **A request is never truncated**, and a batch is
  all-or-nothing: one impossible member places nothing.

## 7. Provenance, reopen and write authorization

No second sidecar format. The expanded allocation converts into the existing
`write.GeneratedAllocationProvenance`, which is the record `write.plan_changes`
already demands before it will accept an appended write. `allocate ->
provenance -> WriteManifest.dumps() -> json.loads -> reservations_from_manifest ->
allocate again` is proved, and the discriminating half is asserted with it: with
the reservations removed the allocator **does** hand back the same span, so the
reopened reservation is what prevents reuse - not the span happening to be
unreachable. Relocation destinations (`new_range`) round-trip the same way.

## 8. Mutations

Each ran in its own `robocopy` copy, so the reviewed tree was never modified and
reversion is byte-exact by construction. Only the exact detecting node was run.

| Mutation | Hostile edit | Detecting test | Result |
|---|---|---|---|
| **M1** collision | `_place` ignores `reserved` | `test_allocation_authority.py::test_an_existing_reservation_is_stepped_over` | **1 failed** |
| **M2** alignment | `_place` drops the alignment adjustment | `::test_every_supported_alignment_is_honoured` | **5 failed, 1 passed** (only alignment 1, which needs no padding) |
| **M3** UNKNOWN-as-free | `ALLOCATABLE_REGION_CLASSES` gains `UNKNOWN` | `::test_a_non_allocatable_class_is_never_allocated` | **1 failed, 2 passed** (only the `UNKNOWN` case; `OWNED`/`REFERENCED` still refused) |
| **M5** expanded authorization | `write.plan_changes` no longer requires matching provenance | `test_allocation_provenance.py::test_an_expanded_write_is_accepted_only_with_its_own_allocation_record` | **1 failed** |

M3's 2 passing siblings are the point: the mutation makes exactly one class
allocatable, and exactly that class's test fails.

## 9. Not done here, deliberately

| Out of scope | State |
|---|---|
| Real-ROM runtime / above-8-MiB engine proof | Checkpoint D |
| Workbench allocator integration | **not started**; CQA-05/06/07/08 remain deferred |
| Promoting candidate free space | not done; not promoted |
| `ROM-CAPACITY-ATLAS-SEED-OVERLAY-001` | **OPEN**, untouched - `seed.py` was not modified, and the allocator does not depend on it |
| Re-doing Phase A capacity research, probing 32 MiB, re-measuring runtime pools | not done |
| Checkpoints A and B | frozen; CQA-09's straddle regression and CQA-12's provenance-by-default behaviour are preserved and exercised by the focused set |

## 10. Validation

Focused file-scoped tests only; no broad suite and no ROM-backed corpus test was
run for confidence.

```text
tests/unit/test_allocation_authority.py
tests/unit/test_allocation_provenance.py
tests/unit/test_relocation.py
tests/unit/test_rom_expansion.py
tests/unit/test_authored_placements.py
tests/unit/test_text_relocation.py
tests/unit/test_text_growth.py
tests/unit/test_authored_materialization_policy.py
tests/unit/test_authored_image.py
tests/unit/test_write_invariants_property.py
tests/unit/test_compressed_dialogue_write_guard.py
tests/unit/test_capacity_model.py          (Checkpoint A contract)
tests/unit/test_build_manifest_default.py  (Checkpoint B contract)
tests/unit/test_test_gates.py
    -> 342 passed

collection check only (not executed) on the ROM-gated files whose allocator calls
were updated: test_placement_run_relocation_rom.py, test_authored_placements_rom.py,
test_combined_allocation_rom.py, test_text_rom.py
    -> 75 tests collected
```
