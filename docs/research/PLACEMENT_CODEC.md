# TOOLKIT-017 placement codec and attachment implementation

Binary interpretation remains CONFIRMED by TOOLKIT-016, not by passing codec
tests. See [ownership evidence](BUU_FD55_SCRIPT_OWNER.md) and the constructor
`0800F6D2 -> 0800A93C`. No ownership or constructor-chain archaeology was reopened.

## Production contract

`formats/map_placements.py` reads exactly `0x1C + 4 * child_count` bytes:

| Offset | Representation |
|---|---|
| +00 | factory_raw |
| +04 | flags_raw |
| +08 | type_raw |
| +0C | `position_raw`: low halfword is signed map/world X pixels; high halfword is signed map/world Y pixels. Preserve each stored halfword losslessly as unsigned raw bits. |
| +10 | id_raw |
| +14 | descriptor_pointer_raw |
| +18 | child_count |
| +1C | ordered child_pointers_raw[count] |

Supported counts are 1..4, a measured corpus bound, not an engine maximum.
Consumed extent derives from count. Serialization preserves every represented
word, child order and unknown value without padding normalization. Normal edits
remain limited to the two position halfwords; no child/descriptor/script growth,
substitution, insertion, relocation, AUTHOR_NEW or semantic script WRITE exists.

Trusted profile metadata in `data/placement_contracts.py` declares 240 runs,
descriptor provenance, 57 owned descriptors and 25 independently verified root
extents. It contains numeric metadata only, no commercial byte fixtures. Normal
loading checks the exact profile/hash before access, reads declared runs rather
than scanning the ROM, and rejects truncation, unsupported counts, duplicate
claims, record/run overlaps and descriptor/attachment provenance mismatches.

## Census and historical corrections

| Measurement | Full supported path | Legacy TOOLKIT-008 view |
|---|---:|---:|
| Maps containing placements / pointer runs | 240 / 240 | 215 / 215 |
| Placements | 1,442 | 1,295 |
| Placement bytes | 46,244 | 41,440 |
| Placement types | 111 | 101 |
| Enemy-linked types / placements | 105 / 1,420 | 95 / 1,284 |
| Readable slot arrays / slots / bytes | 108 / 556 / 4,448 | 112 / 596 / 4,768 |
| Typed slot arrays / slots | 35 / 89 | 35 / 89 |

Child counts 1/2/3/4 occur 1,427/7/6/2 times, giving sizes 32/36/40/44.
Zero double claims, record-body overlap, overlapping run slots, lost legacy
placements, or malformed canonical records. All 147 additions use normal loading.

**OLD CLAIM:** production supported 1,295 fixed 32-byte records.
**NEW EVIDENCE:** full variable-length runs reach 1,442 and retain every old ID.
**RESOLUTION:** 1,295 remains the exact legacy supported subset; 1,442 supersedes
the production ceiling. Old supported prefixes end at the first fixed-tail
mismatch; testing every record for the old tail would not reconstruct that subset.

**OLD CLAIM:** 112 readable slot arrays / 596 slots survived TOOLKIT-008 overlap
checks. **NEW EVIDENCE:** three more opaque extents overlap newly exposed
placements, and map 418's opaque file extent `[0x8D228,0x8D250)` overlaps the
descriptor at `0x8D24C` owned by map 419. **RESOLUTION:** refuse all four opaque
extents whole under the existing rule. No typed extent changes. Legacy projects
validate against their historical view; production builds use corrected ownership.

**OLD CLAIM:** placement +18/+1C was a shared vtable pair.
**NEW EVIDENCE:** these are count and ordered children.
**RESOLUTION:** constant-tail terminology is historical only. `0800421F` is a
function pointer, never a factory tag. The separately refuted fixed minus-12
script adjacency hypothesis remains false; attachment is by stored pointers.

## Identity, descriptors and script ownership

Placement IDs remain `(map index, array ordinal)`. The original supported runs
were prefixes, so every old ordinal survives unchanged; newly exposed suffix
records take their actual subsequent ordinals, and newly visible maps begin at
zero. No address becomes a public ID.

Descriptors are represented once, keyed by their first placement consumer's ID
plus `/descriptor`, in sorted semantic-consumer order. There are 82 distinct
descriptors: one shared by 1,361 placements, and 81 with one consumer each.
The two stored words remain handler_pointer_raw and payload_raw. Three structural
handler identities are exposed, with no gameplay-semantic names:

| Handler | Placements | Maps |
|---|---:|---:|
| 0800421D | 1,361 | 226 |
| 0800421F (script dispatch) | 57 | 10 |
| 0800424F | 24 | 16 |

Events are represented once per shared root, using the first descriptor
consumer's semantic ID plus `/event`. The family `placement_descriptor_event`
uses the existing Buu VM: 25 roots, 42 blocks, 202 instructions, 514 unique bytes,
exact re-encode and all three canonical 0x1C branches. Its physical segments are
explicit; the combined IR uses virtual offsets and has no contiguous ROM base.
Every root is decoded inside its own verified extent before combination.

Seven unreached records, 76 unreferenced descriptors and 19 unowned roots remain
excluded; zero root sharing crosses that boundary. Non-script handlers acquire
no event. The map-to-event convenience query derives the real stored chain:
map -> pointer array -> placement -> descriptor -> event.

The existing `RomDocument` graph contains shared descriptor/event anchors and
confirmed pointer edges. Native opcodes 02/03 have confirmed byte-index edges to
dispatch slots and onward raw Thumb pointers, with separate normalized fetch
addresses. Consumer proof: BUU_SCRIPT_VM.md:49,64-65. Native meanings remain
UNKNOWN. No text consumer is proven for this family, so no event/placement/map
text edge is invented. Candidate edges remain non-rewriteable.

## Project compatibility and queries

New map TOML entries retain raw bytes and position halfwords and add descriptor
ID, child count, ordered raw child pointers and record size. The read-only
`events/placement_descriptors.json` catalog stores shared descriptors/events and
the common graph. Its labelled tables intern repeated IDs and provenance once;
table indices are serialization references, not replacement public identities.
Unknown payloads and complete script bytes round-trip.
Structural fields must match the canonical base; malformed child arrays and
catalog changes fail validation before output.

Format version remains 1 with an explicit additive surface. Projects lacking the
new catalog and structural fields validate against the exact legacy view, including
the old slot and placement-type catalogs. Partial new structures are rejected.
The compatibility path never lowers the normal production enumeration ceiling.

Existing `map placement`, `entity references` and `event --family` inspection
surfaces include the new representation. `event for-map` and `event for-placement`
provide read-only derived queries; `event owners-of` retains descriptor ownership.

Placement ROUND_TRIP now covers all 1,442 records. Descriptor READ/ROUND_TRIP and
owned event READ/DECODE/ROUND_TRIP attachment are supported. Other handler semantics,
constructor runtime destination, text consumption and all growth remain unpromoted.
Production free capacity stays zero; allocator, collision and graphics unchanged.
