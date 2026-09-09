# Buu map object arrays (TOOLKIT-025)

Canonical ROM `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
(`Dragon Ball Z - Buu's Fury (U).gba`, 8,388,608 bytes). Read-only; the image is an
input and is unchanged. Baseline `2673ec5`, parent `ffdf543`.

**COMPLETE ENGINE-COUNTED MAP ARRAY MODEL: YES.**
**AUTHORED MAP COUNT WRITE: YES.**
**AUTHOR_NEW NEXT BLOCKER: non-relocatable `placement_reference_array` anchor.**

## Authoritative count semantics

TOOLKIT-024 proved the outer traversal by disassembly: the map loader at `0x08008B30`
runs a counted loop, reading `MapEntry+0x04` with `ldrb` at both the entry guard
(`0x08008CA2`) and the loop tail (`0x08008CD2`), and indexing the pointer array at
`MapEntry+0x14` by `index * 4`. There is no sentinel, no terminator and no suffix.

The engine never inspects a target's family before dereferencing it. The array is
therefore **heterogeneous**: placement-family records and sibling-family objects share
one counted sequence, and the order is canonical.

Per-record `child_count` at placement `+0x18` is the separate inner structure and is
unchanged by this ticket.

## Engine-owned slot census

Measured by walking `MapEntry+0x04` x 4-byte slots for all 452 map entries and
classifying every target by its leading word.

| Quantity | Measured |
| --- | --- |
| Maps with a non-zero count | **316** |
| Engine-owned object slots | **1,898** |
| Placement-family slots (`0x0800FD55`) | **1,559** |
| Sibling-family slots | **339** |
| UNKNOWN slots | **0** |
| Out-of-image slots | **0** |

### Sibling families

| Factory | Slots |
| --- | --- |
| `0x08017DA3` | 191 |
| `0x080111A9` | 148 |

Exactly three leading words occur across all 1,898 slots. No unknown family appears.
These are classified and preserved; **their payload semantics are not decoded**, and
this ticket does not authorize reverse engineering them.

### Placement-family census

| Quantity | Measured |
| --- | --- |
| Placement records | **1,559** |
| Distinct record offsets | 1,559 (zero double-claims) |
| Records reached by more than one map | 0 |
| Records decoding under the production codec | 1,559 (zero failures) |
| Total record bytes | 49,988 |
| `child_count` 1 / 2 / 3 / 4 | 1,544 / 7 / 6 / 2 |

## OLD CLAIM / NEW EVIDENCE / RESOLUTION - the census

**OLD CLAIM.** The SDK's 1,442-record placement census was complete, with only a small
discrepancy against the newly proven engine-count contract.

**NEW EVIDENCE.** The engine owns 1,898 pointer slots: 1,559 genuine `0x0800FD55`
placement records and 339 sibling-family objects. The existing SDK found 1,442. The
old census is a strict subset of the corrected one (verified set-inclusion), and the
old per-map sequence is an exact **prefix** of the new sequence in every contract map.

**RESOLUTION.** The 1,442 figure is the **pre-TOOLKIT-025 SDK census**, not the
canonical placement census, which is 1,559. The canonical map structure is a
heterogeneous engine-owned object-pointer array, and placement discovery must traverse
all `MapEntry+0x04` slots.

## OLD CLAIM / NEW EVIDENCE / RESOLUTION - the truncation mechanism

**OLD CLAIM.** The discrepancy was caused by runs truncating at sibling-family objects.

**NEW EVIDENCE.** Two independent defects in the frozen `contract['runs']` table, and
the live census read the frozen numbers rather than truncating at read time:

1. **Cause A - frozen truncated count.** The map is present in the contract, but its
   stored count came from a historical first-mismatch traversal. **1 map**, 2 records.
2. **Cause B - absent map entry.** The map is absent from the contract, and
   `maps.py` defaulted a missing entry to `(scripts_pointer_raw, 0)` - a count of
   zero. **28 maps**, 115 records.

**RESOLUTION.** The historical run contract is not authoritative for canonical
traversal. The confirmed `MapEntry` pointer/count contract drives the complete
heterogeneous object-array model, and a missing contract entry never means "empty map".

## Divergence figures - three distinct counts

| Figure | Meaning |
| --- | --- |
| **5** | contract maps whose stored count differs from `MapEntry+0x04` (17, 96, 151, 258, 450) |
| **29** | maps where the SDK lost placement records (Cause A + Cause B) |
| **81** | maps where the SDK count differs from the engine **slot** count (includes maps whose slots are entirely sibling-family, where the SDK correctly found 0 placements and lost nothing) |

Of the 5 contract maps that disagree with the engine count, 4 stored the engine
**placement-family** count (correctly skipping siblings, losing nothing). Only map 17
stored a genuinely truncated count.

## The 29 maps that lost records

`+0x04` = engine count; `old` = frozen contract count (0 = absent); `first sib` = index
of the first sibling-family slot.

| map | +0x04 | slots | placement | sibling | old | lost | first sib | cause |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | 4 | 4 | 3 | 1 | 1 | 2 | 1 | A frozen count |
| 40 | 4 | 4 | 2 | 2 | 0 | 2 | 0 | B absent |
| 41 | 6 | 6 | 3 | 3 | 0 | 3 | 0 | B absent |
| 42 | 8 | 8 | 4 | 4 | 0 | 4 | 0 | B absent |
| 43 | 2 | 2 | 1 | 1 | 0 | 1 | 0 | B absent |
| 46 | 18 | 18 | 2 | 16 | 0 | 2 | 0 | B absent |
| 80 | 3 | 3 | 2 | 1 | 0 | 2 | 0 | B absent |
| 81 | 13 | 13 | 3 | 10 | 0 | 3 | 0 | B absent |
| 82 | 15 | 15 | 5 | 10 | 0 | 5 | 0 | B absent |
| 83 | 21 | 21 | 9 | 12 | 0 | 9 | 0 | B absent |
| 91 | 2 | 2 | 1 | 1 | 0 | 1 | 0 | B absent |
| 116 | 8 | 8 | 1 | 7 | 0 | 1 | 0 | B absent |
| 124 | 6 | 6 | 4 | 2 | 0 | 4 | 0 | B absent |
| 138 | 21 | 21 | 19 | 2 | 0 | 19 | 0 | B absent |
| 166 | 5 | 5 | 1 | 4 | 0 | 1 | 0 | B absent |
| 179 | 4 | 4 | 1 | 3 | 0 | 1 | 0 | B absent |
| 207 | 5 | 5 | 1 | 4 | 0 | 1 | 0 | B absent |
| 221 | 9 | 9 | 4 | 5 | 0 | 4 | 0 | B absent |
| 225 | 8 | 8 | 4 | 4 | 0 | 4 | 0 | B absent |
| 257 | 5 | 5 | 4 | 1 | 0 | 4 | 0 | B absent |
| 281 | 15 | 15 | 11 | 4 | 0 | 11 | 0 | B absent |
| 335 | 14 | 14 | 8 | 6 | 0 | 8 | 0 | B absent |
| 339 | 7 | 7 | 6 | 1 | 0 | 6 | 0 | B absent |
| 343 | 10 | 10 | 9 | 1 | 0 | 9 | 0 | B absent |
| 402 | 8 | 8 | 4 | 4 | 0 | 4 | 0 | B absent |
| 416 | 9 | 9 | 3 | 6 | 0 | 3 | 0 | B absent |
| 443 | 3 | 3 | 1 | 2 | 0 | 1 | 0 | B absent |
| 445 | 2 | 2 | 1 | 1 | 0 | 1 | 0 | B absent |
| 447 | 2 | 2 | 1 | 1 | 0 | 1 | 0 | B absent |

Total recovered: **2 + 115 = 117**.

### Map 17 - the frozen-count discriminator

The only map whose truncation happens mid-array, and the only Cause A instance.

| Slot | Source | Pointer | Family | Kind |
| --- | --- | --- | --- | --- |
| 0 | `0x08072A34` | `0x080729BC` | `0x0800FD55` | PLACEMENT |
| 1 | `0x08072A38` | `0x080729DC` | `0x080111A9` | sibling |
| 2 | `0x08072A3C` | `0x080729F4` | `0x0800FD55` | PLACEMENT |
| 3 | `0x08072A40` | `0x08072A14` | `0x0800FD55` | PLACEMENT |

`MapEntry+0x04` = 4; the contract stored 1. The walk stopped at slot 1 and lost the two
placement records behind it.

### Map 138 - the missing-contract discriminator

Absent from `contract['runs']` entirely. `MapEntry+0x04` = 21, of which 19 are
placement-family and 2 are sibling-family. The old census reported **0** placements,
because slot 0 holds a `0x080111A9` sibling and the missing entry defaulted to a count
of zero. This is a second, independent defect from map 17's.

## Heterogeneous model

`formats/map_placements.ObjectSlot` / `iter_object_slots` walk one engine-counted array
and classify each target, preserving for every physical slot:

* array index, slot source offset, pointer value, target offset
* family (`PLACEMENT`, `SIBLING_<factory>`, `UNKNOWN`, `OUT_OF_IMAGE`)

`iter_placement_offsets` remains the placement-only projection for existing consumers.
Sibling targets are preserved and classified, never decoded.

`PlacementEntry.slot_index` records a record's position in the engine array. It is
distinct from `identity.placement_index` and is not defaulted: emitting a placement
reference at `placement_index * 4` wrote a placement pointer over a sibling's slot
wherever the two interleaved, which surfaced as a layout target mismatch at map 17's
slot `0x00072A38`.

## Stable identities

* All **1,442** previously known placement IDs are preserved.
* The old per-map sequence is an exact **prefix** of the new sequence in every contract
  map, so no existing `(map_index, placement_index)` is renumbered.
* The **117** additions take indices after existing ones, or occupy maps that
  previously modelled none. The allocation rule is array order itself - a placement's
  index is its ordinal among placement-family slots in the engine array - so identity
  follows canonical layout rather than physical address.

## Downstream census refresh

Recomputed mechanically over the corrected census with existing classifiers only. No
new semantic RE.

| Classification | Pre-TOOLKIT-025 | Corrected |
| --- | --- | --- |
| Placement records | 1,442 | **1,559** |
| Maps with placements | 240 | **268** |
| Record bytes | 46,244 | **49,988** |
| Legacy fixed-tail subset | 1,295 | **1,330** |
| Canonical descriptors reached | 82 | **131** |
| Shared null descriptor `0x080555A0` | 1,361 | **1,429** |
| Private descriptors | 81 | **130** |
| Distinct type selectors | 111 | **125** |
| Enemy-linked types | 105 | **118** |
| Enemy-linked placements | 1,420 | **1,534** |
| Enemy stat bytes round-tripped | 2,940 | **3,304** |
| Opaque+typed slot arrays | 108 / 556 slots | **105 / 518 slots** |
| Typed slot arrays | 35 / 89 slots | **35 / 89 slots** (unchanged) |

The slot-array totals **fall** because a declared slot extent is refused whole wherever
it covers a placement record, and 117 further records are now visible. The typed subset
is unchanged; only contested opaque extents were shed.

## Verified event corpus - deliberately unchanged

| Quantity | Value |
| --- | --- |
| Verified event descriptors | **82** |
| Verified roots | **25** |
| Decoded event-bearing placements | **57** |
| Maps owning them | **10** |
| Raw `0x0800421F` structural fan-in | **64** |
| Script-dispatching but outside the verified corpus | **7** |

### OLD CLAIM / NEW EVIDENCE / RESOLUTION - the descriptor contract

**OLD CLAIM.** The 82-descriptor event contract equalled the complete descriptor set
reachable from canonical placements.

**NEW EVIDENCE.** The corrected census reaches 131 descriptors. The additional 49 all
use already-verified handlers - 42 `0x0800424F` and 7 `0x0800421F` - so no unknown
handler family appears. The seven `0x0800421F` descriptors point at seven roots whose
extents are not part of the verified event corpus.

**RESOLUTION.** The 82-descriptor contract is a verified event-model **subset** of the
larger canonical descriptor universe, not an exhaustive descriptor census.

The seven are recorded accurately as: *canonical placements whose descriptors use the
already-confirmed `0x0800421F` script-dispatch handler and whose payloads point at seven
previously uncensused script roots; event attachment/decoding is not promoted because
root extents have not been established under the existing VM evidence contract.* Their
structural relationship is real; their decoded event membership is not established.
Their roots are `0x0807CDAC`, `0x0807FA04`, `0x080819E4`, `0x08083D88`, `0x0808DF28`,
`0x0808DFE4`, `0x0808E09C`, in maps 166, 225, 257, 281, 443, 445, 447.

`placement_events.py` now requires the declared contract to be a subset of canonical
discovery rather than equal to it. The check stays exact in the direction carrying the
evidence: a declared descriptor that disappears, moves, changes handler, or stops
dispatching its declared root still fails. Decoded-event queries return only the
verified 57/25 corpus.

## TOOLKIT-023 re-run over all 1,559

Mandatory re-check, because the missing 117 could have contained a reuse candidate.

| Class | Count |
| --- | --- |
| `LIVE_MAP_OWNED` | **1,559** |
| `LIVE_REFERENCED` | 0 |
| `SHARED` | 0 |
| `ORPHAN_STATIC` | 0 |
| `UNKNOWN` | 0 |
| `REPURPOSABLE_CANDIDATE` | 0 |
| `REPURPOSABLE_CONFIRMED` | 0 |
| **Total** | **1,559** |

Every one of the 117 newly exposed records is reached from a map object array, decodes
cleanly under the production codec, and is claimed by exactly one map.

**`SAFE EXISTING PLACEMENT REUSE PATH: NO` survives the corrected census.**

TOOLKIT-023's finding is superseded only in scope, not in substance: its conclusion held
for the 1,442 it could see, and re-running the same liveness logic over all 1,559
reaches the same result.

## MapEntry+0x04 count write contract

A narrow, derived write. Users cannot edit a count: `maps.MAP_FIELDS` still refuses
every `*_count_raw` byte, and no project field supplies one.

`AuthoredRun.derive_count_change(image)` returns an attributed `ByteChange`, not a
`ReferenceRewrite`, recording map, old count, new count, exact ROM address, old byte,
new byte, and the reason `derived from authored object-array expansion`.

Invariants, each failing closed:

| Condition | Behaviour |
| --- | --- |
| Canonical no-op | returns `None`; no count write emitted |
| Authored +1 | derives exactly `old_count + 1` |
| Modelled canonical count disagrees with the image's `MapEntry+0x04` | refused |
| Modelled slot count disagrees with the modelled engine count | refused |
| Authored array shorter than canonical (deletion) | refused |
| Derived count above 255 | refused - the engine reads one `ldrb` byte |
| No map-entry provenance | refused; a count write must name its byte |

## Authored +1 expansion - canonical Buu

One TOOLKIT-022 authored clone on map 10, through the production build.

| Property | Value |
| --- | --- |
| Map | 10 |
| MapEntry offset | file `0x08E510` |
| Count byte address | file `0x08E514` |
| Old count | **2** |
| New count | **3** |
| Canonical slots | 2 (both placement-family) |
| Authored additions | 1 |
| Pointer array | 8 bytes -> 12 bytes |
| Clone body | 32 bytes |
| Allocation request | 108 bytes, alignment 4 |
| Proposed write set | one `ByteChange` at `0x08E514`, `02` -> `03`, owner `map:0010/object_array_count` |

Progression reached:

```
complete canonical heterogeneous array
-> append one authored placement
-> derive N+1 slots                       OK  (2 -> 3)
-> MapEntry+0x04 count write permitted    OK  (0x08E514: 02 -> 03)
-> relocation machinery                   BLOCKED
```

## Next blocker

**Non-relocatable object-array anchor.**

The grown array no longer fits its canonical extent, so it must move. The
`placement_reference_array` anchor is published `relocatable=False` by
`entities.PlacementTypes.reference_document`, and `relocation.plan_relocation` refuses a
non-relocatable anchor before any allocation is attempted. Verified independently of the
authored gate: map 10's anchor is `relocatable=False`, and **all 2,438 anchors** in the
production graph are non-relocatable.

The allocator was **not** reached. `InsufficientSpaceError` was not the outcome, and was
not forced to be.

**Is TOOLKIT-011 binding? NO.** The build does not reach verified-capacity failure, so
free-space work remains downstream. Buu free capacity remains zero and the candidate
tail remains unused and uninspected.

## Scope held

Not investigated, per the ticket's diminishing-returns guard: the seven new script
roots, sibling-family semantics, additional native handlers, collision, the free-space
tail, the 516 TOOLKIT-011 references, and unrelated relocation cases.
