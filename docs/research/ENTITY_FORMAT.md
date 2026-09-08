# Buu's Fury map-linked placement records

TOOLKIT-017 implementation and corrected full-corpus accounting:
[variable-length codec, descriptors, attachments and stable IDs](PLACEMENT_CODEC.md).
The TOOLKIT-008 measurements below retain their historical legacy-subset meaning.

TOOLKIT-008 evidence. Every count here was measured against the canonical Buu's
Fury image (SHA-256 `940ad5f0...f059e`) by reading it; none is inherited from a
prior ticket's summary or from an upstream project.

## Sources consulted before any new reverse engineering

| Source | What it gave | What it did not |
| --- | --- | --- |
| `docs/reverse-engineering.md` | The nine MapEntry pointer words, the full ROM-003 pointer census, the count/pointer correlation matrix | Any confirmed semantics; it records all nine as Category B/C, none Category A |
| `docs/research/MAP_FORMAT.md` | The `+0x04` correction, the typed/opaque split, the one CONFIRMED bounds structure | Anything about the other four count/pointer pairs |
| `docs/research/AUTO_RE_<local-state-name>` | Factory raws `0x08007675`/`0x080072CD`, the 24-byte rectangle-object family, descriptor field map, the reusable-actor-slot warning | A static placement record layout |
| `spicybung/DragonByteZ` (via the RE doc's pinned commit) | The upstream field names `items`/`objects`/`npcs` | Any dereference of those words; it follows only `+0x2C` |
| `2genkidev/buusfury` (pinned disassembly) | Table base, stride, count, byte accesses at `+0x00`/`+0x01` | No identified consumer loads any of the nine pointer words |

The upstream-labelled names were therefore treated as leads, not as structure.

## OLD CLAIM / NEW EVIDENCE / RESOLUTION: where the entity corpus lives

**OLD CLAIM.** The ticket's framing, inherited from the upstream labels: NPC,
object and item placements are reached through `npcs_pointer_raw` (`+0x20`),
`objects_pointer_raw` (`+0x1C`) and `items_pointer_raw` (`+0x18`), counted by
the bytes at `+0x08`, `+0x07` and `+0x06`.

**NEW EVIDENCE.** Measured across all 452 MapEntry records:

| Pair | count 0 / ptr NULL | count 0 / ptr live | count >0 / ptr NULL | count >0 / ptr live |
| --- | ---: | ---: | ---: | ---: |
| item / `items_pointer_raw` | 391 | 49 | 8 | **4** |
| object / `objects_pointer_raw` | 425 | 12 | 15 | **0** |
| npc / `npcs_pointer_raw` | 31 | 1 | 406 | **14** |
| script / `scripts_pointer_raw` | 122 | 277 | 14 | 39 |
| trigger / `triggers_pointer_raw` | 67 | 69 | 163 | 153 |

The declared entity families are nearly empty: 18 usable arrays in total, and
the object family has **zero**. 406 npc entries pair a positive count with a
NULL pointer. This reproduces the ROM-003 census already in
`docs/reverse-engineering.md`; it is not a new measurement, and it was checked
rather than assumed.

Separately, a scan for Thumb-shaped factory words found a much larger family:

| Factory raw | 4-aligned occurrences |
| --- | ---: |
| `0x0800FD55` | **1,571** |
| `0x08007675` (CONFIRMED, AUTO_RE_STATE) | 669 |
| `0x08017DA3` | 191 |
| `0x080072CD` (CONFIRMED, AUTO_RE_STATE) | 170 |

1,156 of the 1,571 `0x0800FD55` occurrences sit exactly 32 bytes from the next,
and 1,403 begin an eight-word record whose last three words are the constants
`{0x080555A0, 0x00000001, 0x080716EC}`.

**RESOLUTION.** The factory-led family is TOOLKIT-008's typed corpus. The
upstream-labelled fields are left in place, still named, still `INFERRED`, and
their bytes are unaffected. Nothing in this ticket renames a placement record to
"NPC", "object" or "item": no evidence establishes which of those it is.

## Entry point and ownership chain

```
MapEntry[+0x14]  ->  array of 32-bit pointers  ->  32-byte placement record
```

Measured: **215** of the 258 contiguous pointer arrays start exactly at a
`scripts_pointer_raw` target, and **zero** arrays start at any of the other eight
pointer fields. No MapEntry pointer field lands directly on a record.

Walking each map's `+0x14` array while every successive word points at a
well-formed record reaches:

| Quantity | Value |
| --- | ---: |
| Maps yielding at least one record | **215** |
| Records reached | **1,295** |
| Records claimed by more than one map | **0** |
| Pointer arrays overlapping each other | **0** |
| Unique byte extent | **41,440** |
| Well-formed records in the image that no map reaches | 108 |

The 108 unreached records are excluded rather than forced into a map's extent.

That the array hangs off the field upstream named "scripts" is an observation
about **where the pointer lives**, not a claim that these records are scripts.

## The declared count does not bound the array

| `script_count_raw` vs walked length | Maps |
| --- | ---: |
| equal | **2** |
| declared count smaller (usually zero) | **212** |
| declared count larger | **1** |

The extent is therefore resolved by walking and terminating on the first word
that is not a cartridge address reaching a well-formed record. What `+0x05`
counts is **UNKNOWN** and was not investigated.

## Record layout

Measured over the 1,295 reachable records:

| Offset | Width | Name | Observed | Status |
| ---: | ---: | --- | --- | --- |
| `+0x00` | 4 | `factory_raw` | always `0x0800FD55` | CONFIRMED constant |
| `+0x04` | 4 | `flags_raw` | 33 distinct values | UNKNOWN |
| `+0x08` | 4 | `type_raw` | 1..149, 101 distinct, high halfword always 0 | CONFIRMED table selector (TOOLKIT-009; see correction below) |
| `+0x0C` | 4 | `position_raw` | low 0..1982, high 0..930 | see below |
| `+0x10` | 4 | `id_raw` | 5..306, high halfword always 0 | UNKNOWN |
| `+0x14` | 4 | `tail0_raw` | always `0x080555A0` **in this corpus** | behavior-descriptor pointer - see correction |
| `+0x18` | 4 | `tail1_raw` | always `0x00000001` **in this corpus** | child count - see correction |
| `+0x1C` | 4 | `tail2_raw` | always `0x080716EC` **in this corpus** | `child_ptr[0]` - see correction |

Every field keeps a `_raw` suffix: the width and position are CONFIRMED, the
meaning is not.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: the record is variable-length

**OLD CLAIM.** The record is a fixed 32 bytes ending in the constant tail
`{0x080555A0, 0x00000001, 0x080716EC}`, and the 168 occurrences not carrying
that tail are non-conforming.

**NEW EVIDENCE** (TOOLKIT-016). `+0x18` is a **child count** and `+0x1C..` a
`count`-long **pointer array**, so a record occupies `0x1C + 4n` bytes. Over all
1,442 map-reached records the sizes are 32 (`n = 1`) x1,427, 36 x7, 40 x6 and
44 x2; **zero** record bodies collide with the next record and **zero**
pointer-array slots are shared, so the variable extent is self-consistent.
This is corroborated in code: `0x0800F6D2` does `adds r1, #0x18` and calls
`0x0800A93C`, which walks its argument as `{count, ptr[count]}` - that argument
is exactly this field pair.

`+0x14` points at a 2-word behavior descriptor `{handler, payload}`, and
`0x080555A0` is the shared **null-handler** descriptor: it holds `0x0800421D`
(`bx lr`), and it has 1,442 inbound references - one per map-reached record.

**RESOLUTION.** The three words are not a tail and are not constants of the
family; they read as constants here only because `n == 1` dominates the corpus.
Everything measured above stays valid **as the `n == 1` subset** - no count,
proof or edit path in this document is withdrawn - but that subset is not the
whole family. Reading `+0x18` as a count reaches 1,442 records including the
1,295 here, of which 57 name a script handler across 10 maps. This also answers
the "what the three tail constants are" entry under Remaining unknowns. Full
evidence: [`BUU_FD55_SCRIPT_OWNER.md`](BUU_FD55_SCRIPT_OWNER.md).

## `position_raw`: what is and is not established

**Established.** The word at `+0x0C` splits into two halfwords that vary
independently across the corpus, over ranges (0..1982 and 0..930) far wider than
one screen and consistent with map-space values.

**Suggestive, and explicitly not proof.**

* The packing matches the one CONFIRMED bounds structure in this project:
  `0x080755C0 +0x08` decodes as `(481, 121, 615, 271)` with the **low halfword
  holding X**.
* Within a map, the low halfword's spread exceeds the high halfword's in **130**
  maps against **52**, which is consistent with maps wider than they are tall.

**Not established.** 52 maps run the other way, and no consumer of this word has
been traced in code. The halfwords are therefore exposed as `position_low` and
`position_high` - named by position in the word, never by axis - and the edit
API takes keyword-only `low=`/`high=`. **No axis claim is made anywhere.**

Static evidence was exhausted first, per the ticket's escalation rule. Settling
the axis order requires the one narrow runtime question below, which was not
needed for the placement-edit milestone because the milestone is proven at the
byte level without naming an axis.

## OLD CLAIM / NEW EVIDENCE / RESOLUTION: 40 slot extents were not slots

**OLD CLAIM.** TOOLKIT-007: every MapEntry whose `trigger_count_raw` and
`triggers_pointer_raw` describe an in-bounds extent contributes a slot array -
**152 arrays, 873 slots, 6,984 bytes**.

**NEW EVIDENCE.** 40 of those 152 declared extents cover bytes that belong to
factory-led placement records - **57 records** in total. The two readings cannot
both be right, and the placement reading is the better-witnessed one:

* **33 of the 40** have their first record starting at byte **4 mod 8** within
  the declared extent - *mid slot*. A record straddling a slot boundary cannot
  be a slot array with a record after it.
* MapEntry 146 declares 12 slots whose extent walks through three complete
  records: `slots[2]` holds the factory word `0x0800FD55`, and `slots[5]` and
  `slots[6]` split one record's constant tail across a slot boundary.
* 46 declared extents contain a bare factory word inside them.
* **2** slots in the corpus were classified TYPED only because a record's tail
  constants happen to satisfy the `{type, source_ref}` shape test.

The placement reading rests on an eight-word record whose leading factory word
and three trailing constants all match, 1,295 times. The slot reading rests on a
count byte that `MAP_FORMAT.md` already records as UNKNOWN in meaning.

**RESOLUTION.** Those 40 extents are refused, exactly as MapEntry 451 already
was and for the same reason: a declared extent that provably is not slots is not
read as slots. The corrected corpus is **112 arrays, 596 slots, 4,768 bytes**.

The extents are refused rather than truncated, because 33 of the 40 cannot be
cut on a slot boundary at all, so a truncated extent would still emit fabricated
slots.

**The typed rung is unchanged at 35 arrays / 89 slots.** Every refused extent
was opaque, so TOOLKIT-007's typed corpus, its connection graph and its one
confirmed example all stand exactly as proven. `trigger_count_raw` remains
UNKNOWN; this narrows where it is trusted rather than reinterpreting it.

## Capability matrix

| Family | Rung | Note |
| --- | --- | --- |
| Factory-led placement records | **ROUND_TRIP + EDIT** | 1,295 records, 215 maps, 41,440 bytes; `position_raw` editable |
| `position_raw` as an (x, y) pair | **NOT ESTABLISHED** | halfwords exposed by position, never by axis |
| `flags_raw`, `type_raw`, `id_raw` | **READ** | preserved exactly; semantics UNKNOWN, not editable |
| Unreached factory-led records (108) | **DISCOVERED** | well-formed, but no map reaches them |
| Non-conforming `0x0800FD55` occurrences (168) | **DISCOVERED** | 1,571 occurrences minus 1,403 well-formed; bounded, never forced into the 32-byte codec |
| Other factory families (`0x08017DA3`, `0x0800A223`, ...) | **DISCOVERED** | counted only |
| MapEntry-declared item arrays | **READ** | 4 usable; names INFERRED upstream |
| MapEntry-declared npc arrays | **READ** | 14 usable; names INFERRED upstream |
| MapEntry-declared object arrays | **NOT PRESENT** | 0 entries with count > 0 and a live pointer |
| Entity type / template references | **NOT ESTABLISHED** | no field verified as a template reference |
| Script attachments | **DISCOVERED** | Buu profile declares no `scripts` capability |
| Dialogue attachments | **DISCOVERED** | no verified entity -> script -> text chain |
| NPC / enemy / item classification | **NOT ESTABLISHED** | no evidence names any record |
| Collision | **DISCOVERED** | untouched by this ticket |
| Sprite / animation | **DISCOVERED** | untouched by this ticket |
| AUTHOR_NEW | **NOT SUPPORTED** | no verified free space in any profile |

## Proofs

* **No-op**: extract -> build reproduces the canonical 8 MiB image with **0
  changed bytes**; repeated builds byte-identical; repeated extraction
  byte-identical.
* **Exhaustive round-trip**: all **1,295** records decoded and re-encoded
  byte-identically; `webfoot map validate-round-trip` reports 452 records, 112
  slot arrays, 596 slots, 1,295 placements, 0 failures.
* **Semantic move**: `map:0010/placement:0000` position low `60 -> 76` changes
  **exactly 1 byte**, at record base `+0x0C`, owner `map:0010/placement:0000`,
  reason `placement edit: position`. Every other record re-encodes unchanged.
* **Ownership**: no record is claimed by two maps; no slot extent overlaps a
  placement record (asserted, not merely described).
* **Fail-closed**: an out-of-range halfword, an unknown placement identity, and
  a cross-owner write overlap are each refused before any output is created.
* **Canonical inputs**: unchanged on every path.

## Remaining unknowns

* Which halfword of `position_raw` is X. Static evidence is suggestive
  (130 vs 52, plus the CONFIRMED bounds packing) and not conclusive.
* What `flags_raw`, `type_raw` and `id_raw` mean.
* What `script_count_raw` (`+0x05`) counts, given it does not bound this array.
* Why 108 well-formed records are unreachable from any map.
* ~~What the three tail constants are - a vtable, a shared callback, a template
  pointer, or something else.~~ **ANSWERED (TOOLKIT-016)**: `+0x14` is a
  behavior-descriptor pointer, `+0x18` a child count and `+0x1C` `child_ptr[0]`.
  See the variable-length correction above.
* Whether any record corresponds to an NPC, an enemy, a pickup or a generic
  object. Nothing here names one.
* The **168** factory occurrences that are not well-formed records (1,571
  occurrences minus 1,403 well-formed). Bounded and left alone: they are not
  forced into the 32-byte codec, and no fresh RE was opened on them.

## The one narrow runtime question, if it is ever needed

> Does the word at `+0x0C` of a `0x0800FD55` placement record become the spawned
> actor's world-space position, and in which halfword order?

Preferred escalation is `gbarecomp` instrumentation first, mGBA second, per the
ticket's ladder. It was **not** run: the placement-edit milestone is proven at
the byte level without an axis claim, so the question does not block closure.
Answering it is what would let `position_low` be renamed `x`.

## TOOLKIT-009 follow-up correction

The supported corpus has **101**, not 111, distinct type_raw selectors.
The factory now has a confirmed static consumer chain: placement +08 selects
08711274 + 28 * selector, passed to constructor 0800F68C. 95 selected targets
are existing enemy-stat records (1,284 placements); six targets (11 placements)
remain reference-only. Earlier UNKNOWN labels above are historical; see
[placement type evidence](PLACEMENT_TYPES.md) for the new evidence and limits.
No coordinate-axis or NPC/item/friendly taxonomy claim was added.
