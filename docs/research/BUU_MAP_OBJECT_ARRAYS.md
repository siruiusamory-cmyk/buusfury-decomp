# Buu map object arrays (TOOLKIT-025, TOOLKIT-026, TOOLKIT-027)

Canonical ROM `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
(`Dragon Ball Z - Buu's Fury (U).gba`, 8,388,608 bytes). Read-only; the image is an
input and is unchanged. Baseline `2673ec5`, parent `ffdf543`.

**COMPLETE ENGINE-COUNTED MAP ARRAY MODEL: YES.**
**AUTHORED MAP COUNT WRITE: YES.**
**PLACEMENT_REFERENCE_ARRAY RELOCATION: YES** (TOOLKIT-026).
**AUTHORED PLACEMENT BODY MATERIALIZATION: YES** (TOOLKIT-027).
**AUTHOR_NEW NEXT BLOCKER: declared free capacity / TOOLKIT-011** (TOOLKIT-027).

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

## Next blocker (TOOLKIT-025, superseded by TOOLKIT-026)

**Non-relocatable object-array anchor.**

The grown array no longer fits its canonical extent, so it must move. The
`placement_reference_array` anchor was published `relocatable=False` by
`entities.PlacementTypes.reference_document`, and `relocation.plan_relocation` refused a
non-relocatable anchor before any allocation was attempted. Verified independently of the
authored gate: map 10's anchor was `relocatable=False`, and **all 2,438 anchors** in the
production graph were non-relocatable.

The allocator was **not** reached. `InsufficientSpaceError` was not the outcome, and was
not forced to be.

**Is TOOLKIT-011 binding? NO.** The build did not reach verified-capacity failure.

TOOLKIT-026 resolved this blocker. What follows supersedes it.

## Scope held (TOOLKIT-025)

Not investigated, per the ticket's diminishing-returns guard: the seven new script
roots, sibling-family semantics, additional native handlers, collision, the free-space
tail, the 516 TOOLKIT-011 references, and unrelated relocation cases.

---

# TOOLKIT-026 - relocating one authored map object array

Same canonical ROM
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, read-only and
unchanged. Baseline `f808a67`.

**PLACEMENT_REFERENCE_ARRAY RELOCATION: YES.**

One question, answered for one representative array: *can the pointer array for an
authored placement expansion safely move?* It can.

## The selected array - map 10

Every value below was re-measured against the image for this ticket, not carried from
TOOLKIT-025's summary.

| Property | Measured |
| --- | --- |
| Map | 10 |
| MapEntry offset | file `0x08E510` |
| Canonical slot count (`MapEntry+0x04`) | **2** |
| Array pointer (`MapEntry+0x14`) raw | `0x0807293C` |
| Array start | file `0x07293C` |
| Array byte length | **8** (`count * 4`) |
| Slot 0 | src `0x07293C` -> `0x080728FC` (file `0x0728FC`), lead word `0x0800FD55` PLACEMENT |
| Slot 1 | src `0x072940` -> `0x0807291C` (file `0x07291C`), lead word `0x0800FD55` PLACEMENT |

## The owner pointer

| Property | Value |
| --- | --- |
| Owning field | `MapEntry+0x14` |
| Source ROM address | file `0x08E524` |
| Encoding | `ABSOLUTE_ROM_U32_LE` |
| Target delta | 0 |
| Evidence class | **CONFIRMED** |

The owner is rewrite-eligible under the existing reference rules: it is a CONFIRMED
absolute-u32 reference whose source lies outside the anchor, so `plan_relocation`
rewrites it as an ordinary `ByteChange`.

## Reverse-reference census - the selected array only

Complete and bounded: every 4-byte window at **every byte alignment** across all
8,388,608 bytes, tested against the array start and every interior byte of its
`count * 4` extent.

| Class | Count | Sources |
| --- | --- | --- |
| CONFIRMED | **1** | `0x08E524` (`MapEntry+0x14`) |
| DECLARED | 0 | - |
| CANDIDATE | 0 | - |
| numeric coincidence / rejected | 0 | - |
| interior-address hits | 0 | - |
| unaligned hits | 0 | - |

**Positive control (ticket section 9).** The same loop that returns the negative result
finds the known owner reference at `0x08E524`. A census whose instrument could not
find the positive is not trusted, and this one does find it.

The graph agrees: `scan_pointer_candidates` over the MapEntry window returns nothing,
because the only numeric hit is already a declared reference source, and the production
document carries **zero** `CANDIDATE_REFERENCE` entries anywhere.

So the answer to *if this array moves, what existing ROM locations must be rewritten?*
is exactly one location: `0x08E524`.

## Relocation eligibility rule

Encoded in `layout.relocation_eligible`, applied as a post-pass over the assembled graph
in `entities.PlacementTypes.reference_document`. It is a statement about an anchor's
**measured references**, never about a map index or an address:

An anchor is relocatable when all of the following hold.

1. Its `kind` is in `RELOCATION_ELIGIBLE_KINDS` - today only
   `placement_reference_array`, because TOOLKIT-024 proved the engine reaches such an
   array through exactly two fields (`MapEntry+0x14` base, `MapEntry+0x04` count) with
   no sentinel, terminator or suffix, so the whole inbound surface is expressible as
   references. Every other kind stays fixed.
2. Every inbound reference is DECLARED or CONFIRMED. One CANDIDATE withdraws
   eligibility - the same refusal `plan_relocation` would raise, made at publication
   time so the flag stays honest.
3. Every inbound reference targets an offset inside the anchor, so none is stranded
   when the extent changes.
4. Every reference **sourced inside** the anchor is DECLARED or CONFIRMED and lies
   wholly within it, so the payload rewrite carries each source field along.
5. Something actually points at it. An unreferenced anchor has no proven owner to
   rewrite, so moving it would orphan whatever really reaches it.

Scope of the capability, measured on the production graph:

| Quantity | Value |
| --- | --- |
| Anchors in the graph | 2,438 |
| Now relocatable | **268** |
| Their kind | `placement_reference_array`, all of them |
| Other kinds made relocatable | **0** |
| `placement_reference_array` anchors NOT eligible | 0 |

All 268 arrays have exactly one CONFIRMED inbound reference at delta 0, and clean
interior slot sources, so the rule admits the whole class rather than a hand-picked
subset. That is a measured outcome of the rule, not a special case written into it.

## Synthetic verified-capacity result

Production machinery only - `relocation.plan_relocation` and `allocation.allocate`, with
one synthetic `FreeRegion(0x10000, 4096)`. No test-only relocation algorithm exists.

```text
map 10 canonical array (2 slots, 8 bytes)
-> append authored placement slot                  OK  (3 slots, 12 bytes)
-> relocation eligibility accepted                 OK  (was: refused at the flag)
-> allocator reached                               OK  <- previously never reached
-> expanded array allocated                        OK  file 0x010000, 12 bytes
-> expanded array written                          OK
-> owner pointer rewritten                         OK  0x08E524: 0x0807293C -> 0x08010000
-> canonical slot order preserved                  OK  0x080728FC, 0x0807291C
-> appended slot                                   0x00000000 (no anchor to point at)
-> repeated plan byte-identical                    OK
-> old extent left intact                          OK  (relocation retires, never scrubs)
-> base image unmodified by planning               OK
```

`MapEntry+0x04` stays `2` through relocation, correctly: a count field is neither a
reference source nor a relocated payload. The derived count write is a separate,
validated `ByteChange` (TOOLKIT-025), and both are available at the same time.

## Canonical Buu result

Same authored +1 build (`clone_placement` on map 10), through `build_project`, against
canonical Buu with its real zero free capacity.

Acceptance for TOOLKIT-026 is met: the build **no longer fails because the array anchor
is non-relocatable**. Production error, verbatim:

```text
map:0010/placement_references: valid authored placement content serialized;
proposed capacity request 108 bytes, alignment 4;
derived count write is AVAILABLE and validated (file 0x08E514: 2 -> 3);
array anchor IS relocatable and plan_relocation accepts it (2 -> 3 slots);
materialization blocked by unmodelled authored record bodies:
map:0010/authored:toolkit026 has no anchor and no array-slot reference in the
graph, and plan_relocation creates neither, so the appended slot would have
nothing to point at.
```

Deterministic across repeated runs; no output ROM and no manifest are produced; the
canonical image and its mtime are unchanged.

## The next blocker - measured, not predicted (resolved by TOOLKIT-027)

**Unmodelled authored record bodies.**

The relocator's contract is to move **existing** anchors and rewrite **existing**
references. It creates neither. Measured consequences for the map 10 +1 case:

* `plan_relocation` on the clone's identity raises
  `LayoutError: unknown anchor AnchorId(value='map:0010/authored:toolkit026')` - the
  authored body has no anchor to hold it;
* after the array relocates to 3 slots, only two reference sources exist inside the new
  extent (`0x10000`, `0x10004`), so the appended slot at `0x10008` stays `0x00000000`
  with nothing to point at.

This is reported **from production** rather than asserted: the gate reads the array
anchor's actual `relocatable` flag off the same document the build uses, and names the
authored records the graph is missing.

The gate message is not a prediction about what comes after that. Closing this blocker
means giving an authored record its own anchor and its own array-slot reference, which
is a graph-construction question, not a relocation one.

**Did production actually reach the allocator? YES**, under synthetic verified capacity
(allocated file `0x010000`, 12 bytes). Against canonical Buu the allocator is reached
and raises `InsufficientSpaceError`, because the profile declares zero free regions -
`plan_relocation(types.reference_document(), ...)` now fails at the capacity boundary,
not at an authority boundary. That is proven directly in
`test_capacity_is_still_necessary_and_relocation_now_reaches_the_allocator`.

**Is TOOLKIT-011 binding? NO.** The allocator is reached, which was TOOLKIT-011's
precondition, but it is not the *binding* blocker for AUTHOR_NEW: the authored-body
blocker above stops `build_project` before relocation is ever requested. Free-space work
becomes binding only once an authored record can be modelled in the graph. Buu free
capacity remains zero, and the candidate tail remains unused and uninspected.

## Superseded claims

**OLD CLAIM (TOOLKIT-025).** *All 2,438 anchors in the production graph are
non-relocatable*, and capacity never grants relocation authority.

**NEW EVIDENCE.** 268 `placement_reference_array` anchors satisfy the existing
relocation safety contract on their measured references, and `plan_relocation` moves
map 10's array through production machinery.

**RESOLUTION.** The blanket `relocatable=False` was a conservative default, not a
finding. It is replaced by an evidence-driven rule; every other anchor kind keeps the
default. The claim that *capacity does not override the fixed-anchor authority guard*
is retired for this kind: there is no longer a fixed-anchor guard to override here, and
what capacity still cannot grant is an anchor for a record absent from the base image.

## Scope held

Not investigated, per ticket section 8: the seven excluded script roots, sibling object
semantics, collision, dialog/native handlers, the TOOLKIT-011 tail, the 516 candidate
references, ROM expansion, and other placement runs beyond the 268-anchor eligibility
census used as the rule's own control.

---

# TOOLKIT-027 - materializing one authored placement body

Same canonical ROM
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, read-only and
unchanged. Baseline `28ae50b`.

**AUTHORED PLACEMENT BODY MATERIALIZATION: YES.**

One question, answered for the map 10 `+1` case: *can an authored placement body be
given a real anchor and a real array-slot reference, and be allocated by production
machinery?* It can, and the relocated array's third slot holds its address.

## Why the authored anchor cannot live in the base graph

This is the constraint that shapes the whole design, and it is measured, not assumed.

`document.RomDocument.validate` decodes **every** reference against the image the
document holds and refuses any whose decoded target is not exactly
`anchor.start + target_delta` (`malformed reference ... target mismatch`). For an
authored record:

* the body has no bytes in the verified base, so an anchor over its future span
  describes nothing that is there;
* the appended array slot does not exist in the base either - map 10's array anchor is
  8 bytes, exactly `count * 4` - so a reference sourced at the third slot would decode
  whatever those neighbouring bytes happen to be.

A second, independent guard points the same way: `RomDocument.from_bytes` refuses a
document whose anchors overlap a declared free region (`profile free region overlaps
existing content/reference`), and free space is precisely where an authored body goes.

So the authored anchor and its slot reference are created in the **same transaction
that creates the slot**, at their post-relocation addresses, rather than published onto
the verified base. That is `authored_placements.authoring_overlay`.

## The overlay - minimum reference relationship

Per authored record, exactly two objects are created, and nothing else:

| Object | Value for the map 10 case |
| --- | --- |
| Body anchor identity | `map:0010/authored:toolkit022` |
| Body anchor kind | `authored_placement_body` |
| Body anchor size | **32 bytes** - the production codec's own `consumed_length` |
| Slot reference source | relocated array start `+ 4 * slot_index` (slot **2**) |
| Slot reference target | the body anchor, delta **0** |
| Slot reference encoding | `ABSOLUTE_ROM_U32_LE` - identical to canonical slots |
| Slot reference class | `DECLARED_REFERENCE` |

The anchor ID is the project's own authored identity, which
`project.placements.AuthoredPlacement` already validates as a stable map-scoped name
(`map:NNNN/authored:<stable-name>`). It is **not** derived from any ROM address, so it
does not change when the allocator places the body somewhere else.

The body bytes are `PlannedPlacement.payload` - the output of
`PlacementRecord.with_position(...).to_bytes()`, the same production codec that
serializes canonical records. No parallel test-only body format exists anywhere; the
proof asserts the anchor's bytes decode back through `PlacementRecord.from_bytes` and
equal `template.with_position(123, 456)`.

`authored_placement_body` is deliberately a distinct kind from `placement`: a canonical
placement anchor describes bytes in the verified base, and this one describes bytes the
build is about to create. Keeping them separate is what lets
`RELOCATION_ELIGIBLE_KINDS` stay a statement about measured canonical structure.

## Two allocator calls, one answer - a real defect found and fixed

`plan_authored_materialization` allocates the bodies, and then `plan_relocation`
allocates the expanded array **itself**, deriving its own reserved set from the
document's anchors and profile (`relocation.py:73-79`). The first implementation left
those two calls ignorant of each other, and the measured result was:

```text
alloc map:0010/authored:toolkit022  0x7FF000  32 bytes
anchor(map:0010/placement_references).range.start = 0x7FF000   <- SAME BYTES
third slot pointer = 0x087FF000                                <- the array's own start
```

Both calls chose the same lowest first fit. The third slot was non-null and **wrong**:
it pointed at the array laid over the body. A pointer being non-zero is not the proof;
pointing at the body is.

The fix is subtraction, not a new allocator: the body spans are **withheld** from the
free regions offered to relocation (`_withhold`, which only ever splits or trims a
declared region and can never grow, merge or invent one). A body anchor could not do
the job, because of the free-region guard above. Measured after the fix:

```text
alloc map:0010/authored:toolkit022        0x7FF000  32 bytes
alloc map:0010/placement_references       0x7FF020  12 bytes
overlap                                   none
third slot pointer                        0x087FF000 -> file 0x7FF000 == body start
```

Pinned by `test_body_and_expanded_array_never_share_bytes` and
`test_withhold_only_ever_subtracts_capacity`.

## Synthetic verified-capacity result - canonical Buu bytes

Production machinery only: `allocation.allocate` for the body, `relocation.plan_relocation`
for the array, and the existing attributed write path for both. The only synthetic input
is one `FreeRegion(0x7FF000, 0x1000)` declared as capacity.

```text
authored placement description (map:0010/authored:toolkit022)
-> real authored placement anchor            OK  stable semantic ID, 32 bytes
-> serialize production placement body       OK  PlacementRecord codec, round-trips
-> allocate body under synthetic capacity    OK  file 0x7FF000, 32 bytes, align 4
-> allocate expanded array                   OK  file 0x7FF020, 12 bytes, align 4
-> body and array disjoint                   OK
-> canonical slots preserved exactly         OK  fc280708 1c290708 (bytes unchanged)
-> create new array-slot reference           OK  src 0x7FF028 -> body, delta 0, ABSOLUTE_ROM_U32_LE
-> third slot contains body pointer          OK  0x087FF000, NOT 0x00000000
-> body payload applies to the image         OK  final bytes == codec payload
-> repeated planning byte-identical          OK
-> base image unmodified by planning         OK
```

The two canonical map 10 slots are carried over **byte for byte** (`fc280708`,
`1c290708`); an authored record can only ever append, which
`AuthoredRun.derive_count_change` independently refuses to violate.

## Canonical Buu result

Same authored +1 build through `build_project`, against canonical Buu with its real
zero free capacity. `require_materialization_contract` no longer asserts a boundary at
all - it **runs** the materialization and reports whatever production refuses.
Production error, verbatim:

```text
map:0010/placement_references: valid authored placement content serialized;
proposed capacity request 108 bytes, alignment 4;
derived count write is AVAILABLE and validated (file 0x08E514: 2 -> 3);
array anchor IS relocatable and plan_relocation accepts it (2 -> 3 slots);
authored record bodies are MODELLED (map:0010/authored:toolkit022) with an anchor
and an array-slot reference each; materialization blocked by InsufficientSpaceError:
insufficient declared free space for map:0010/authored:toolkit022 (32 bytes, alignment 4)
```

Deterministic across repeated runs; no output ROM and no manifest are produced; the
canonical image and its mtime are unchanged (asserted in the test's `finally`).

## The next blocker - measured, not predicted

**Declared free capacity.**

The chain now runs end to end and stops where the ROM genuinely has nothing to give:
`allocation.allocate` raises `InsufficientSpaceError` for the 32-byte authored body,
because the canonical Buu profile declares **zero** free regions
(`document.profile.free_regions == ()`, asserted directly).

This is the first time the authored-placement path has been blocked by *capacity alone*
with every structural prerequisite satisfied - the count write, the array relocation,
the body anchor and the slot reference all exist and validate.

**Did production reach the allocator? YES.** It is reached and it is the thing that
refuses.

**Is TOOLKIT-011 binding? YES.** This is the change from TOOLKIT-026. Free-space work is
no longer waiting on a graph-construction prerequisite: nothing structural remains
between an authored placement description and a written body except declared bytes to
put it in. Buu free capacity remains zero, and the candidate tail remains uninspected -
per this ticket's scope, free space was not investigated here.

## Superseded claims

**OLD CLAIM (TOOLKIT-026).** *An authored clone has no anchor to hold its body and no
reference source to fill the new array slot, so the expanded array's appended slot has
nothing to point at*, and *plan_relocation creates neither*.

**NEW EVIDENCE.** `plan_relocation` still creates neither - that half stands, and is
unchanged. `authoring_overlay` creates both, outside the relocator, and the relocated
map 10 array's third slot holds `0x087FF000`, the authored body's allocated address.

**RESOLUTION.** The blocker was a missing graph-construction step, not a limit of the
relocator. The correction to the TOOLKIT-026 write-up is narrow: "the appended slot
would have nothing to point at" was true of the machinery as it stood, not a property
of the format.

## Scope held

Not investigated, per the ticket: free space (including the TOOLKIT-011 tail and the
516 candidate references), scripts, sibling object semantics, collision, and unrelated
map structures. No engine behaviour is claimed for a materialized body - this ticket
proves the SDK can construct and place one, not that the game runs it.
