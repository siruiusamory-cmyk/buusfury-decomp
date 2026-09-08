# TOOLKIT-024 - Placement-run traversal contract and relocation

## Result

**PLACEMENT-RUN TRAVERSAL CONTRACT: CONFIRMED.**
**PLACEMENT-RUN RELOCATION: NO** - blocked on an unwritable engine count field.

Canonical identity `buus_fury_usa_rev0_01c1707f`, 8,388,608 bytes, SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`. The ROM is
read-only and untouched. Baseline `ffdf543`.

The TOOLKIT-022 blocker is **resolved as stated and replaced by a narrower one**.
The engine's outer traversal count/termination rule is no longer UNKNOWN: it is a
counted loop over `MapEntry+0x04`, proven by disassembly of the map loader. There
is no sentinel, no terminator and no suffix, so a run owns exactly `count * 4`
array bytes and nothing more - which is precisely what the graph already models.

What blocks materialization now is not evidence but expressive power: expanding a
run requires writing a **new count byte**, and no production write path can emit a
count change. That is a structural finding about the toolkit, not a ROM UNKNOWN.

## Selected run

Map 10, the TOOLKIT-022 canonical example. Verified against the selection criteria
rather than assumed: physically contiguous bodies, no interior hole, smallest
useful record count, every `child_count == 1`, and `MapEntry+0x04` exactly equal to
the declared count (so the run carries no census ambiguity of its own).

| Property | Value |
|---|---|
| Map index | 10 |
| MapEntry base | file `0x08E510` |
| `MapEntry+0x04` (engine count) | **2** |
| `MapEntry+0x05` (`script_count_raw`) | 0 |
| `MapEntry+0x14` (array pointer) | `0x0807293C` |
| Pointer array extent | file `0x07293C..0x072944`, 8 bytes |
| Record bodies extent | file `0x0728FC..0x07293C`, 64 bytes |
| Records | 2, both 32 bytes, both `child_count` 1 |
| Placement IDs | `0x0000002B`, `0x0000001C` |
| Types | `0x0000001C`, `0x00000019` |
| Descriptor | `0x080555A0` (shared null handler) for both |
| Total encoded bytes | 72 (64 body + 8 pointer) |

## Canonical record sequence

Enumerated with the production codec (`formats/map_placements.read_placement_record`),
not a re-derived walk.

| Slot | Slot address | Body address | File offset | Size | `child_count` | Next body |
|---|---|---|---|---|---|---|
| 0 | `0x0807293C` | `0x080728FC` | `0x0728FC` | 32 | 1 | `0x07291C` |
| 1 | `0x08072940` | `0x0807291C` | `0x07291C` | 32 | 1 | `0x07293C` |

The identity `record[i+1] == record[i] + (0x1C + 4*child_count[i])` **does hold**
for this run, and the array begins exactly where the last body ends.

**This is a layout observation, not the traversal mechanism.** The run is an array
of pointers; the engine never adds a record size to reach the next record. It
computes `array_base + index*4` and dereferences. Contiguity is a property of how
the canonical image was laid out and carries no information about termination. It
is recorded here only so a relocation plan knows what physically moves, and it is
**not** used anywhere as evidence of the run's bound.

## Owner

| Question | Answer |
|---|---|
| Source structure | `MapEntry` record 10 |
| Field | `+0x14`, upstream-inferred name `scripts_pointer_raw` |
| Source file offset | `0x08E524` |
| Encoding | `ABSOLUTE_ROM_U32_LE` |
| Target | `map:0010/placement_references` anchor at file `0x07293C`, 8 bytes |
| Classification | **CONFIRMED_REFERENCE** |

Classification is read off the implemented rule, not asserted: `entities.py`
`PlacementTypes.reference_document` emits every placement-graph reference with
`ReferenceClass.CONFIRMED_REFERENCE`, and the anchor is published with
`relocatable=False`.

**The owner reference is not rewrite-eligible as published.** `plan_relocation`
rejects a non-relocatable anchor before allocating, and this ticket did not flip
that flag - doing so would be weakening evidence to pass a gate.

## Traversal contract - PROVEN

The consuming code is the map loader `0x08008B30`, which has exactly three BL
callers - `0x08008D38`, `0x08008D7A`, `0x08008EA4` - each of which first resolves a
MapEntry through the by-(zone,area) lookup `0x080089FC` and passes the resulting
pointer in. The loader reads it from the runtime map context at `[r4+0x04]`.

`0x080089FC` is the **only** code site in the image that takes the MapEntry table
address `0x0808E2E0` as a literal (one word-aligned occurrence, file `0x008A58`),
and it has 5 BL callers. So every path that reaches a MapEntry at all reaches it
through that lookup, and the loop below is the only code that consumes `+0x14`.

The outer traversal is this loop, verbatim:

```
0x08008C9E: 6860   ldr  r0,[r4,#0x04]   ; r4+0x04 = current MapEntry pointer
0x08008CA0: 2500   mov  r5,#0           ; index = 0
0x08008CA2: 7900   ldrb r0,[r0,#0x04]   ; MapEntry+0x04 -> unsigned byte COUNT
0x08008CA4: 2800   cmp  r0,#0
0x08008CA6: DD17   ble  0x08008CD8      ; count <= 0: consume nothing
0x08008CA8: 6860   ldr  r0,[r4,#0x04]   ; loop head
0x08008CAA: 00A9   lsl  r1,r5,#2        ; index * 4
0x08008CAC: 6940   ldr  r0,[r0,#0x14]   ; MapEntry+0x14 -> pointer array base
0x08008CAE: 5846   ldr  r6,[r0,r1]      ; array[index] -> record body
0x08008CB0: 6870   ldr  r0,[r6,#0x04]   ; body+0x04 (flags) -> predicate
0x08008CB2: F7FB FD67  bl 0x08004784
0x08008CB6: 2800   cmp  r0,#0
0x08008CB8: D009   beq  0x08008CCE      ; predicate false: skip this record
0x08008CBA: 1C29   add  r1,r5,#0
0x08008CBC: 1C30   add  r0,r6,#0
0x08008CBE: 6832   ldr  r2,[r6,#0x00]   ; body+0x00 = factory pointer
0x08008CC0: F03D FEF0  bl 0x08046AA4
...
0x08008CCE: 6860   ldr  r0,[r4,#0x04]   ; loop tail
0x08008CD0: 3501   add  r5,#1           ; index += 1
0x08008CD2: 7900   ldrb r0,[r0,#0x04]   ; re-read the SAME count byte
0x08008CD4: 42A8   cmp  r0,r5
0x08008CD6: DCE7   bgt  0x08008CA8      ; index < count: continue
0x08008CD8: ...                          ; fall through: run consumed
```

**The bound is `MapEntry+0x04`, read as an unsigned byte by `ldrb`, at two sites
(`0x08008CA2` entry guard and `0x08008CD2` loop tail).** The array base is
`MapEntry+0x14`, indexed by `index*4`.

Three negative facts follow directly from the instruction sequence and matter for
relocation:

* **No sentinel.** Nothing in the loop compares a loaded word against a terminator
  value. The word after the array is never read. This independently explains the
  measured heterogeneity of the word following each array end (top values
  `0x08007675` x27, `0x0800742D` x17, `0x00000000` x13): there is no terminator to
  be uniform, because the engine never looks there.
* **No suffix.** The loop reads `count*4` bytes of array and nothing beyond, so a
  run's array ownership is exactly `count * 4` bytes. The existing graph already
  models exactly this (`entities.py` sizes the anchor `len(placements)*4`), so the
  TOOLKIT-022 "suffix ownership is UNKNOWN" caveat is discharged, not worked around.
* **Nothing else bounds it.** `+0x05`, the descriptor, the body sizes and the next
  run's address play no part in the loop.

### Outer traversal is proven independently of `child_count`

Stated explicitly, because conflating them would invalidate the result. The
per-placement `child_count` at body `+0x18`, consumed by `0x0800A93C` via the
constructor path `0x0800FD54 -> 0x0800F68C -> (0x0800F6D2 adds r1,#0x18) -> 0x0800A93C`,
is the **inner** loop over one record's child pointers. It executes only after a
record has already been selected, and only inside the factory call at `0x08046AA4`,
which the outer loop reaches at `0x08008CC0`.

The outer loop above **never reads body `+0x18`**. Its only body access is `[r6,#0x04]`
(flags, for the skip predicate) and `[r6,#0x00]` (the factory pointer). The two
loops were traced separately and neither was used as evidence for the other.

Note also that `0x0800FD54` has **zero** BL callers in the image: placements are
constructed by dereferencing the factory pointer stored at each body `+0x00`. That
is why the array can hold heterogeneous record families at all - see below.

## The `+0x04` correlation: confirmed, and the 5 exceptions explained

The session opened with a numeric correlation - `MapEntry+0x04` equals the declared
placement count in 235 of 240 runs - flagged as *hypothesis only*, because
`MAP_FORMAT.md` records `+0x04` as UNKNOWN and AUTO-012 was previously burned by
over-generalizing a `+0x04`/`+0x10` pairing from one decode.

The correlation is now **confirmed by the consuming code, not by the correlation**.
The code was read first and agrees with it. Had they disagreed, the code would win.

The 5 exceptions (maps 17, 96, 151, 258, 450) are not noise and are not tolerated
over-count. Every one is explained by the same mechanism, measured slot by slot:

| Map | Declared count | `+0x04` | What the extra slots hold |
|---|---|---|---|
| 17 | 1 | 4 | slot1 `0x080729DC`, slot2/slot3 **are `0x0800FD55` placements** |
| 96 | 3 | 4 | slot3 `0x08077D94` |
| 151 | 14 | 16 | slot14 `0x0807BD74`, slot15 `0x0807BD90` |
| 258 | 3 | 4 | slot3 `0x08081BB4` |
| 450 | 1 | 2 | slot1 `0x0808E188` |

Each extra slot points at a well-formed record whose `+0x00` factory word is
`0x080111A9` or `0x08017DA3` instead of `0x0800FD55`. Both are genuine Thumb
function entries (`0x080111A8: B5F3 push {r0,r1,r4,r5,r6,r7,lr}`;
`0x08017DA2: B530 push {r4,r5,lr}`), and `0x080111A8` calls `0x0800FD74` and
`0x0800A93C` exactly as the placement constructor does - the same record family
idiom with a different factory.

**So `MapEntry+0x04` is the true engine count and the declared census count is the
artifact.** The census `runs` table derives from `iter_placement_offsets`, whose
unbounded mode stops at the first non-`0x0800FD55` pointer. In these 5 maps the
array interleaves sibling-family records, so the census truncated early.

Map 17 is decisive: `+0x04` is 4, slot1 is a sibling record, and slots 2 and 3 are
**ordinary `0x0800FD55` placements**. The engine loads all four. The census stopped
at slot 1 and lost two live placement records. This is the same prefix-truncation
failure mode TOOLKIT-023 documented for the legacy 32-byte tail codec, recurring one
level up at the pointer array.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION - what `MapEntry+0x04` counts

**OLD CLAIM** (`MAP_FORMAT.md`, carried from AUTO-012). What `MapEntry[+0x04]`
counts is UNKNOWN. A single-entry decode suggested it counts the 8-byte records
reached through `MapEntry[+0x10]`; measured across all 452 entries that pairing did
not generalize, and the meaning was left explicitly unresolved.

**NEW EVIDENCE.** The map loader at `0x08008C9E..0x08008CD6` reads `+0x04` with
`ldrb` at two sites as the entry guard and loop bound of a counted loop whose body
indexes the array at `+0x14` by `index*4`. The `+0x10` slot array is bounded by a
*different* loop; `+0x10` and `+0x14` are consumed by separate loops in the same
function. Across the 240 declared runs `+0x04` equals the declared count in 235,
and all 5 remainders are census truncation at a sibling-family pointer, verified
slot by slot.

**RESOLUTION.** `MapEntry+0x04` is the **placement-run record count**. The
AUTO-012 `+0x04`/`+0x10` pairing stays **refuted** - this result does not revive
it, it identifies the field's real consumer. The codec field name
`trigger_count_raw` is now known to be misleading and is annotated in
`formats/map_entry.py` rather than renamed, because project files and tests pin it.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION - expanded-run termination

**OLD CLAIM** (TOOLKIT-022, `AUTHORED_PLACEMENTS.md`). "Expanded-run engine
count/termination and suffix ownership are UNKNOWN (MapEntry+0x05 is not a verified
count)." Materialization was refused on that UNKNOWN.

**NEW EVIDENCE.** Termination is a count, the count is `+0x04` (not `+0x05`, which
this ticket confirms plays no part in the loop and is 0 for the selected run), and
there is no suffix: the loop reads exactly `count*4` array bytes and never touches
the word past the array end.

**RESOLUTION.** The UNKNOWN is **discharged**. The gate message in
`authored_placements.require_materialization_contract` was factually stale in two
ways - it cited the wrong field and an UNKNOWN that no longer holds - and is
corrected to state the real remaining blocker. The gate still refuses, on narrower
and now-accurate grounds.

## Reverse-reference census (bounded to this run)

Scanned every 4-aligned word in the image against the run start, both record
starts, and every interior address that would move.

| Target | Inbound word-aligned references | Source |
|---|---|---|
| Array start `0x0807293C` | **1** | file `0x08E524` = MapEntry 10 `+0x14` |
| Record 0 `0x080728FC` | **1** | file `0x07293C` = array slot 0 |
| Record 1 `0x0807291C` | **1** | file `0x072940` = array slot 1 |
| Any interior non-start address | **0** | - |

No structure outside the run points into it. The only inbound references are the
owner and the run's own array slots.

**Pointer direction resolved.** Every ROM pointer stored *inside* the run points
**out** of it: `0x0800FD55` (factory), `0x080555A0` (shared descriptor),
`0x080716EC` (child pointer), in both records. These survive a move unchanged. The
only pointers *into* the run are the two array slots, which the relocator already
rewrites as CONFIRMED references.

### Positive controls

* **PC1.** The traversal enumeration reproduces the known run start `0x0807293C`,
  both canonical records, and the known end `0x072944`, using the production codec.
* **PC2.** The reference instrument found the known owner reference - MapEntry 10
  `+0x14` at file `0x08E524` - as a positive, and found both array slots. The zero
  external-reference result is therefore a measurement, not an instrument failure.

## Hypothetical +1

Canonical run plus one `AUTHORED_CLONE` of `map:0010/placement:0000` at position
(123, 456), through the TOOLKIT-022 representation:

| Quantity | Canonical | +1 | Delta |
|---|---|---|---|
| Records | 2 | 3 | +1 |
| Body bytes | 64 | 96 | +32 |
| Pointer slot bytes | 8 | 12 | +4 |
| Total | 72 | 108 | **+36** |

The 108-byte allocation request reproduces the TOOLKIT-022 figure exactly, measured
independently here.

**Required owner metadata changes**, now fully enumerated because the contract is
proven:

1. `MapEntry+0x04`: `2 -> 3`. One byte at file `0x08E514`. **Required** - without
   it the engine consumes 2 of 3 records and the clone never spawns.
2. `MapEntry+0x14`: `0x0807293C -> <new array address>`. One word at file `0x08E524`.
3. New 12-byte array: 3 pointer slots at the new address.
4. Slot 2: pointer to the clone body's new address.
5. No terminator, no suffix, no padding word. Proven, not assumed.

Items 2-4 are exactly what the existing graph and relocator model. **Item 1 is not
modelled anywhere.**

## Synthetic relocation - the blocker

Attempted through production machinery only (`allocation.allocate`,
`relocation.plan_relocation`), against a synthetic profile declaring one free
region at file `0x10000`. No parallel relocator was written and no production
free-space declaration was added.

| Step | Result |
|---|---|
| 108-byte request against canonical profile | `InsufficientSpaceError` (zero free regions) |
| 108-byte request against synthetic profile | allocated at `0x10000`, deterministic |
| `plan_relocation` on the published graph | `LayoutError: non-relocatable anchor: map:0010/placement_references` |

The published anchor is `relocatable=False`. This ticket did **not** flip it.

To locate the *next* gate rather than stop at a flag, an in-memory probe replaced
that one boolean and re-ran the real relocator. The probe wrote nothing and is
recorded as a measurement, not as a capability:

* `plan_relocation` **succeeded** for the 12-byte expanded array.
* It rewrote `MapEntry+0x14` from `0x0807293C` to `0x08010000` - the owner
  reference rewrite works.
* It preserved slots 0 and 1 as CONFIRMED references to the two canonical records.
* Slot 2 remained `0x00000000`: no anchor exists for the clone body, and the
  relocator's own contract does not create anchors or append new reference sources.
* **`MapEntry+0x04` remained 2.**

That last line is the finding. `plan_relocation` composes its change set from
exactly two sources - reference-source rewrites and relocated payload bytes. A
count field is neither, so there is no path by which it could emit the `2 -> 3`
byte change. Independently, `maps.MAP_FIELDS` exposes only
`zone / area / variation / flags / music_id` as editable and explicitly refuses
every `*_count_raw` byte, on the reasoning that slot extents are resolved *by* the
count so an edit would change what a later read decodes.

**A run whose count cannot be rewritten cannot be expanded, regardless of capacity
or of how well the traversal contract is understood.** Per this ticket's own
instruction, that is reported as a finding rather than worked around: expressing it
would require new graph declarations (a clone anchor, an appended reference source,
and a count-field write contract), which is design work this ticket did not
authorize itself to do.

Reparse verification (section 8 of the brief) is therefore **N/A**: no synthetic
materialization was produced to reparse.

## Canonical Buu

`webfoot placement clone` accepted the authored placement, and the build failed
before allocation with, verbatim:

```text
map:0010/placement_references: valid authored placement content serialized; proposed capacity request 108 bytes, alignment 4; materialization blocked by an unwritable engine count: the outer traversal bound is CONFIRMED as MapEntry+0x04 (counted loop at 0x08008C9E indexing the MapEntry+0x14 array), but no production path can rewrite a count field - the relocator emits only reference and payload changes, and every *_count_raw byte is refused as non-editable. Verified capacity alone does not authorize this rewrite.
```

**CANONICAL AUTHOR_NEW BLOCKER: OTHER (unwritable `MapEntry+0x04` count field).**
Not capacity. No output ROM and no manifest were published. No free space was
declared and the candidate tail was not consulted.

## Required rewrite set for a future ticket

For map 10, complete and now fully enumerated:

| # | Target | Change | Modelled today |
|---|---|---|---|
| 1 | file `0x08E514` (`MapEntry+0x04`) | `2 -> 3` | **No** |
| 2 | file `0x08E524` (`MapEntry+0x14`) | new array address | Yes (CONFIRMED ref) |
| 3 | new array, 12 bytes | 3 pointer slots | Yes (anchor payload) |
| 4 | array slot 2 | pointer to clone body | **No** (no clone anchor) |
| 5 | clone body, 32 bytes | allocated | **No** (no clone anchor) |
| 6 | anything else | **nothing** - no terminator, no suffix | Proven |

Row 6 is the ticket's positive contribution to future work: the rewrite set is
*closed*, and it is closed because the traversal contract is proven rather than
assumed.

## Generalization

Not claimed beyond what was measured. The loop at `0x08008C9E` is reached for every
map through a single loader, and `0x080089FC` is the only literal consumer of the
MapEntry table, so the mechanism is structurally shared by all 240 runs. That is
reported as evidence, not as a proof that all 240 are relocatable - each run's
external-reference census and hole structure is its own question, and 26 runs carry
interior holes this ticket did not examine.

## Remaining UNKNOWNs

* The gameplay semantics of the sibling factories `0x080111A9` and `0x08017DA3`.
  Their records are shown live and shown to occupy declared array slots; neither is
  decoded, and neither is modelled by the production codec.
* The `runs` census table under-counts 5 maps relative to the engine's `+0x04`.
  Correcting it would change the 1,442-record census and is deliberately **not**
  done here - it is a codec and census change, not a traversal question, and
  TOOLKIT-023's numbers are preserved unchanged.
* The predicate at `0x08004784` applied to body `+0x04` (flags) decides whether a
  record spawns. Its semantics are UNKNOWN; it does not affect the run's bound.
* Whether `MapEntry+0x04` may be safely written at all, given `_resolve_slot_extent`
  also reads it. This ticket proves what the engine does with it, not that the
  toolkit's own readers tolerate a change.
