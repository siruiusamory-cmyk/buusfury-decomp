# TOOLKIT-028 - Verified canonical Buu capacity

## Result: one bounded region VERIFIED and declared

`[0x007EA400, 0x007EA500)` - **256 bytes** - is verified writable for authored
allocation in canonical Buu, under the constraints recorded below, and is declared
in the production profile as a `CONFIRMED` free region.

Canonical identity: `buus_fury_usa_rev0_01c1707f`, 8,388,608 bytes,
SHA-256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
Baseline: `ffd0eb1bac4df6575c153e37a8c159cc97cd6277` (`feat: materialize authored Buu placements`).

This is **not** a claim that the surrounding tail is free. TOOLKIT-011 refused the
whole `[0x007B89A8, 0x00800000)` region and that refusal stands unchanged. This is a
carve of that region chosen to contain none of the evidence that blocked it.

## 1. Exact canonical allocation demand

Measured from the production transaction itself, by instrumenting
`allocation.allocate` while `plan_authored_materialization` ran the existing map 10
authored `+1` case against canonical Buu bytes. Not taken from any prior estimate.

| Order | Anchor | Owner | Size | Alignment |
|---|---|---|---|---|
| 1 | `map:0010/authored:toolkit022` | `map:0010/placement_references` | 32 | 4 |
| 2 | `map:0010/placement_references` | `map:0010/placement_references` | 12 | 4 |

* two separate `allocate` calls, in that order, not one combined request;
* **total allocated: 44 bytes**; span actually occupied under the allocator: **44 bytes**
  (the two are adjacent, body then array, with no alignment loss);
* ordering constraint: the body must be allocated **first**, because the array payload
  has to contain the body's address before the array can be written
  (`authored_placements.plan_authored_materialization`);
* the second call is issued by `relocation.plan_relocation`, which runs the allocator
  itself against free regions with the body's span already withheld (`_withhold`).

**OLD CLAIM:** the authored planner reported a proposed capacity request of 108 bytes.
**NEW EVIDENCE:** `AuthoredRun.allocation_request` is a single-block *proposal* - 3
pointer slots plus all 3 whole bodies - and the build never issues it. The transaction
issues 44 bytes, because the two canonical bodies are not rewritten, only re-pointed.
**RESOLUTION:** 44 bytes is the demand. The 108-byte proposal is retained and pinned by
test so it cannot quietly become the sizing rule; it is not what production requests.

## 2. TOOLKIT-011 evidence reused

The prior audit was **not** rerun wholesale. Its preserved record
(`build/toolkit011/occupancy.json`, UTF-16LE) and its implementation were read first,
and `free_space_audit.build_model` - the same annotation and reference model that
produced its positives - is imported rather than reimplemented, so this ticket's
negatives are directly comparable with its positives.

| TOOLKIT-011 finding | Status now |
|---|---|
| Tail `[0x007B89A8, 0x00800000)`, 292,440 bytes, entirely `FF` | Reproduced; unchanged |
| 516 candidate references, 99 word-aligned sources | Reproduced exactly; **all still blocking** |
| 475 distinct candidate target offsets | Reproduced exactly |
| Zero known inbound references into the tail | Reproduced |
| Zero known owned overlaps in the tail | Reproduced |
| Whole tail is CANDIDATE, promotion REJECTED | **Still rejected.** Not revisited |

### Treatment of the 516 historical candidates

None are resolved, whitelisted, downgraded or explained away. Every one remains
blocking for the bytes it addresses, and candidate-reference policy is unchanged
globally: `profile._free_regions` still refuses any status but `CONFIRMED`, and
`relocation` still refuses to move an anchor with a candidate in its inbound set.

What changed is only the *question asked*. TOOLKIT-011 asked whether the whole tail
is allocatable; 516 unresolved candidates land inside it, so the answer was correctly
NO. This ticket asks whether one bounded window contains none of them. Their target
offsets span `0x7B8E2C`..`0x7FFDFF` but do not tile the tail: 474 candidate-free
intervals exist between consecutive targets, the largest being
`[0x7E9D4C, 0x7EB000)` at 4,788 bytes. The declared window sits inside that interval.

Separately measured and worth recording: **zero** of the 516 observations are *sourced*
inside the tail. Every source is elsewhere in the image.

## 3. The verification, check by check

`tools/research/capacity_proof.py` decides one window and fails closed on any failure.
It promotes nothing; a reviewed profile entry does. Measured for
`[0x007EA400, 0x007EA500)`:

| Check | Requirement | Measured |
|---|---|---|
| `bounds` | inside the image, above the declared header (`0x158`) | PASS |
| `fill` | every byte is the tail's `FF` fill | PASS - histogram is `{0xFF: 256}` |
| `known_overlap` | no modelled anchor or declared table overlaps it | PASS - 0 |
| `known_inbound` | no CONFIRMED/DECLARED reference targets it | PASS - 0 |
| `candidate_target` | no candidate targets any byte, interior included, any alignment | PASS - 0 |
| `candidate_source` | no candidate is sourced inside it | PASS - 0 |
| `margin` | ≥ 1,024 bytes clear of the nearest candidate target each side | PASS - 1,717 below, 2,816 above |

Accounting for the factors the ticket named: modelled anchors and declared tables are
the `known_overlap` input; confirmed and declared references are `known_inbound`;
candidate and interior references are `candidate_target`, which tests every byte of
the window rather than only its start; known data structures enter through the same
annotation model; ROM and header boundaries are `bounds`; alignment is satisfied
because both requests are alignment 4 and `0x7EA400` is 4-aligned (it is in fact
2,048-aligned). Whether the bytes are *read or addressed by known engine structures*
is exactly what `known_inbound` and `known_overlap` measure against the production
graph - and its known limit is stated below.

The `margin` requirement exists because a candidate, if real, means some structure
*begins* at its target with unknown length. Keeping 1 KiB of clearance means such a
structure would have to run over a kilobyte to reach the declared window.

## 4. Positive controls

A negative result without a working positive control is not evidence, so the same
verifier is run against windows this project independently models as used. All four
are REJECTED, each failing the specific check it was chosen to exercise:

| Control | Window | Fails on |
|---|---|---|
| `header_startup` | `[0x000000, 0x000100)` | `bounds`, `fill` |
| `declared_table:text_pool` | `[0x05792C, 0x057A2C)` | `known_overlap` (also `fill`, `known_inbound`) |
| `referenced_target:0x00FD55` | `[0x00FD55, 0x00FD59)` | `known_inbound` (also `fill`, `known_overlap`) |
| `candidate_target:0x7B8E2C` | `[0x7B8E2C, 0x7B8E30)` | `candidate_target` |

The last is the decisive one. It is `FF` fill inside the *same tail* as the verified
window, so it cannot be rejected for holding live bytes - `candidate_target` is the
only thing separating it from a verified window. That is what makes absence of
detection evidence of absence for this specific check, rather than a blind scan.
`tests/unit/test_capacity_proof.py` additionally pins that a deliberately blinded
scanner fails this control, and that a control failing for the *wrong* reason does
not count as a control.

## 5. Production integration

`config/roms.yaml` and `tools/webfoot/data/roms.yaml` (identical catalogs) gain one
`free_regions` entry on the canonical Buu profile, `status: CONFIRMED`, carrying the
evidence above. It is a general SDK capacity declaration: the allocator is unchanged,
nothing special-cases map 10, and no test-only region was added to production config.

Every other profile still declares zero capacity.

## 6. Canonical materialization

The existing authored map 10 `+1` operation, run against canonical Buu through
`build_project`, now completes:

```text
body modeled            -> authored_placement_body anchor, 32 bytes
slot reference modeled  -> ABSOLUTE_ROM_U32_LE from appended slot, delta 0
allocator succeeds      -> from the declared region, evidence TOOLKIT-028
body allocated          -> file 0x7EA400, 32 bytes, alignment 4
array allocated         -> file 0x7EA420, 12 bytes, alignment 4
no overlap              -> body [0x7EA400,0x7EA420), array [0x7EA420,0x7EA42C)
new slot points to body -> slot 2 = 0x087EA400
owner pointer rewritten -> MapEntry+0x14 at 0x08E524: 0x0807293C -> 0x087EA420
derived count 2 -> 3    -> MapEntry+0x04 at 0x08E514: 0x02 -> 0x03
output ROM produced     -> 8,388,608 bytes
```

Exactly **48 bytes** differ from the canonical image, in three runs:

| Offset | Size | Before | After |
|---|---|---|---|
| `0x08E514` | 1 | `02` | `03` |
| `0x08E524` | 3 | `3c2907` | `20a47e` |
| `0x7EA400` | 44 | `FF`... | body (32) + expanded array (12) |

The two canonical map 10 slots are carried over byte-for-byte (`fc280708`,
`1c290708`) and the third slot holds `00a47e08` = `0x087EA400`, the body's address.
Nothing outside the declared window and that one MapEntry record changed.

Built output SHA-256 `ac7caf10c7d08e3d7cb7ab3637ddad51205e1668294ee6061e987529fee3a57c`.
Repeated builds are byte-identical, ROM and manifest alike. The canonical no-op build
remains byte-identical to the base. The canonical ROM's SHA-256 and mtime are
unchanged; output is a separate file.

### One defect found and fixed rather than worked around

Emitting the expansion surfaced a real conflict the merged write plan caught:
`Maps.changes()` re-encodes every MapEntry record and every object array, so for an
authored map it re-encoded the record at its *canonical* count and owner pointer, and
the array at its *canonical* home - both contradicting the expansion, and both raising
`OverlappingChangeError`. `Maps.changes` now takes `authored_maps` and yields both
structures for those maps to the expansion, which emits the MapEntry as one
record-wide change with the relocated pointer and derived count folded in. The
MapEntry therefore has a single writer, `MAP_FIELDS` still refuses `*_count_raw` as
directly editable, and any map not in that set is encoded exactly as before.

## 7. Limits, and what this does not establish

* **Structural, not runtime.** The ROM contains the new placement. Whether the engine
  behaves correctly with it in-game is a different proof and is not claimed.
* The occupancy model behind `known_inbound`/`known_overlap` is the same **partial**
  model TOOLKIT-011 recorded: 16,977 known references and 5,199,061 bytes with no
  known annotation. Absence of a known reference is not proof of absence of all use.
  The window's safety rests on the conjunction of all seven checks plus the margin,
  not on the annotation model alone.
* Computed references, unknown compressed extents and checksum/signature uses remain
  unruled-out in general, exactly as before.
* 256 bytes is the declared capacity. It is not a claim about the rest of the tail,
  and it is not large: the next authoring case may need a further verified window.

## Reproducing

```powershell
.venv/Scripts/python.exe -m tools.research.capacity_proof `
  "roms/Dragon Ball Z - Buu's Fury (U).gba" --start 0x7EA400 --size 0x100
```

Regressions: `tests/unit/test_capacity_proof.py` (portable policy),
`tests/integration/test_capacity_proof_rom.py` (canonical evidence),
`tests/integration/test_authored_placements_rom.py` (canonical materialization).
