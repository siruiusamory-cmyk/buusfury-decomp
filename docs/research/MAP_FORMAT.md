# Buu's Fury map records, slot extents and connections

TOOLKIT-007 evidence. Every count here was measured against the canonical
Buu's Fury image (SHA-256 `940ad5f0...f059e`) by reading it; none is inherited
from a prior ticket's summary.

## MapEntry table

| Fact | Value | Status |
| --- | --- | --- |
| Table address | `0x0808E2E0` (file `0x0008E2E0`) | CONFIRMED |
| Record stride | `0x38` | CONFIRMED |
| Record count | 452 | CONFIRMED |
| Table extent | `0x0008E2E0..0x000945C0` | CONFIRMED |
| Full-corpus round-trip | 452/452 byte-identical | CONFIRMED |

Field layout is unchanged from `tools/webfoot/formats/map_entry.py`; TOOLKIT-007
added no field names and renamed none.

## The `+0x04` / `+0x10` pairing: corrected

Prior research (`AUTO_RE_<local-state-name>`, AUTO-012) established from a **single-entry
static decode** that `MapEntry[+0x10]` reaches 8-byte records counted by
`MapEntry[+0x04]`. Measured across all 452 records, that reading does not
generalise.

| State | Entries |
| --- | --- |
| count 0, pointer NULL | 136 |
| count 0, pointer in ROM | 69 |
| **count > 0, pointer NULL** | **163** |
| count > 0, pointer in ROM | 153 |

No entry points outside the cartridge window. No two arrays share a start.
Across the 153 readable extents, every declared count fits inside the gap to the
next array, 152 of 152 gaps are short, **none overruns**, so a declared extent
is safe to read even though the arrays do not tile.

Two independent witnesses against the general reading:

1. **Non-uniformity.** Only **35 of 153** arrays have every slot shaped like the
   confirmed `{type, source_ptr}` example. The other 118 contain words that are
   neither small type codes nor ROM pointers. (117 of those survived into the
   corpus as TOOLKIT-007 measured it; the 118th is MapEntry 451, refused by the
   next witness. TOOLKIT-008 refused 40 more, leaving **77** opaque arrays. The
   typed 35 are unaffected.)
2. **MapEntry 451** declares 4 records at `0x0008E2D0`, an extent covering the
   first 16 bytes of the MapEntry table at `0x0008E2E0`, the table indexing it.
   A count describing an array that consumes its own table is not describing an
   array. That entry's extent is therefore refused, leaving 152 readable at the
   time TOOLKIT-007 measured this. **TOOLKIT-008 refused 40 more by the same
   test; the supported corpus is 112.** See "Supported extents" below.

**What `+0x04` actually counts is UNKNOWN.** TOOLKIT-007 scope forbids fresh RE
on it; nothing here guesses.

## Supported extents

> **SUPERSEDED IN PART BY TOOLKIT-008.** 40 of the 152 extents below were
> measured to cover factory-led placement records and are now refused; the
> corpus is **112 arrays, 596 slots, 4,768 bytes**. The typed rung is unchanged.
> See [ENTITY_FORMAT.md](ENTITY_FORMAT.md) for the evidence and the correction.

| Rung | Extent | Status |
| --- | --- | --- |
| Opaque 8-byte slots | ~~152 arrays, 873 slots, 6,984 bytes~~ -> **112 arrays, 596 slots, 4,768 bytes** | ROUND_TRIP |
| Typed `{type, source_ref}` | 35 arrays, **89 slots, 712 bytes** | ROUND_TRIP |
| Referenced source structures | 89 distinct typed targets, located | READ |
| Source bounds semantics | 1 instance, reached from an **opaque** array | CONFIRMED (instance only) |
| Generic trigger-bound editing | - | NOT SUPPORTED (evidence) |

Note the gap this leaves deliberately open: the one structure whose layout is
verified is reached from MapEntry 39, which is *not* a typed array, so **no
typed reference's target layout is verified**. Typed references are located, not
interpreted. Closing that gap is fresh RE and outside TOOLKIT-007.

The opaque rung is not a lesser copy of the typed one: both reproduce the same
bytes exactly. The difference is only whether this toolkit will *name* the two
words in a slot.

### Classifier

A slot is typed when all three hold, each read off the confirmed example, none
inferred:

* word1 lands inside the cartridge window for the image being read;
* word1 is 4-aligned, as a struct pointer must be;
* word0's high halfword is below `0x0010`.

An array is TYPED only when **every** slot in it is. Uniformity is per-array,
because a mixed array is not evidence that the well-formed part means what the
example means.

`_TYPED_HIGH_HALFWORD_LIMIT = 0x0010` is an **explicit classifier heuristic and
nothing more**. The threshold is **hand-picked, not measured from ROM
semantics**, the confirmed example only ever shows `0x0002000X`, and no
evidence in this project establishes what the high halfword means or where its
real boundary lies.

It is acceptable only because **corpus classification is invariant across the
tested `0x0003`-`0x0100` range**: every limit in that range yields the identical
35 arrays / 89 slots. Only removing the constraint entirely moves the result (to
40 / 112). **The current test guards that invariant**
(`test_the_typed_corpus_is_insensitive_to_the_threshold`).

**If that invariant ever fails, the classifier requires new evidence rather than
threshold tweaking.** Retuning the number to restore a preferred corpus size
would be fitting the constant to a desired answer.

`0x0010` is **not** CONFIRMED and carries no semantic status. It must not be
promoted to either, and no claim about the ROM may rest on it.

## The one verified instance

`AUTO_RE_<local-state-name>` records MapEntry 39 slot[1] as type `0x00020006` reaching
source `0x080755C0` with bounds `(481,121)..(615,271)`. That reproduces here
byte-for-byte: the halfwords at that source `+0x08` are `481, 121, 615, 271`.
Kept as a regression fixture in `tests/integration/test_local_maps_rom.py`.

MapEntry 39 is **not** one of the typed 35. Its declared count of 11 runs past
its four well-formed records into data of another shape, so the array as
declared is not uniform. The example is real; the generalisation was not.

## Connection graph

Built only from typed slots: **89 connections** across 35 maps, deterministic
for a given image (asserted by re-loading and comparing).

**Every destination is explicitly UNKNOWN.** Resolving one would mean reading a
destination out of the referenced structure, whose layout is verified for a
single instance. `MapConnection.destination` is therefore always `None`, and
`webfoot map connections` prints `destination UNKNOWN` rather than omitting the
field, an absent column reads as "no destination", which is a different and
false claim.

The graph preserves the solved VERTICAL-001 lesson: a MapEntry participates in
more than one spatial mechanism, and descriptor-backed objects and slot records
are distinct. Nothing here collapses them.

## Editing

Editable fields, all fixed-width and self-contained:
`zone`, `area`, `variation`, `flags`, `music_id`.

Refused, each for a stated reason:

* the five `*_pointer_raw` words, editing one moves a target this toolkit does
  not own; that is relocation, and no verified profile declares free space;
* the five `*_count_raw` bytes, slot extents are resolved *by* the trigger
  count, so an edit would change what a later read decodes;
* `output_raw`, `unknown_0a`, `unknown_0b`, `unknown_0c`, UNKNOWN semantics.

### Proofs

* **No-op**: extract -> build reproduces the canonical 8 MiB image with
  **0 changed bytes**; repeated builds byte-identical; repeated extraction
  byte-identical.
* **Edit**: `map:0039 music_id 15 -> 14` changes **exactly 1 byte**, at record
  base `+0x24`, owner `map:0039`, reason `map edit: music_id`.
* **Cross-subsystem**: a map, stat and text edit coexist in one merged plan with
  three distinct owners; a second owner claiming a map record's span is refused
  with `OverlappingChangeError`.
* **Canonical inputs**: unchanged on every path.

## Capability matrix

| Target family | Rung | Note |
| --- | --- | --- |
| MapEntry records | **ROUND_TRIP** | 452/452, editable fields above |
| Map-linked 8-byte extents | **ROUND_TRIP** | 112 arrays, 596 slots, opaque-exact (corrected by TOOLKIT-008) |
| Typed slot arrays | **ROUND_TRIP** | 35 arrays, 89 slots |
| Source references | **READ** | 89 targets located; no layout claimed |
| Source bounds | **READ** | one instance, from an opaque array, not a typed one |
| Transitions / connections | **DECODE** | 89 edges, destinations UNKNOWN |
| Generic trigger semantics | **NOT ESTABLISHED** | `+0x04` meaning UNKNOWN |
| Collision | **DISCOVERED** | not decoded; no verified representation |
| NPC targets | **DISCOVERED** | pointer + count fields only |
| Object targets | **DISCOVERED** | pointer + count fields only |
| Item targets | **DISCOVERED** | pointer + count fields only |
| Script attachments | **DISCOVERED** | Buu profile declares no script capability |

Script references stay DISCOVERED because TOOLKIT-006's structural script
identities are for the **Legacy of Goku II** static43 corpus; the Buu profile
declares no `scripts` capability, so there is nothing verified to reference.
Promoting Buu's four script-pointer MapEntry fields would mean asserting a
correspondence across games that no evidence supports.

## Remaining unknowns

* What `MapEntry[+0x04]` counts.
* Why 163 entries carry a positive count with a NULL pointer, and 69 the reverse.
* The layout of all **89** typed source targets. The one verified structure
  (`0x080755C0`) is reached from MapEntry 39, whose array is opaque, so it is
  not among them, no typed target's layout is verified.
* Every slot word in the 117 opaque arrays.
* Whether any map has a canonical display name.
* Collision representation.
