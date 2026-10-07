# Appearance table growth (APPEARANCE-AUTHORING-GATE-001)

Phase A of the ticket. The question is narrow and was answered by measurement
rather than by argument:

> Can the retail engine safely consume an appearance table containing a
> genuinely new record, with every relevant bound and reference updated or
> otherwise proven compatible?

**Gate result: GATE A, GROWTH PROVEN.** The table can be grown by re-emitting it
in expanded storage, repointing the five literal-pool words that name it and
patching the three compiled loop bounds. Growth in place is impossible and is
recorded as such. The runtime claim (that this engine follows the repointed word
for *this* table) is a Phase B obligation and is listed under open items.

Measurement baseline: branch `ticket/appearance-authoring-gate-001`, candidate
commit `9360379df45b2b928c0321d76c54226799b8235a`, canonical image
`Dragon Ball Z - Buu's Fury (U).gba`, profile `buus_fury_usa_rev0_01c1707f`,
8,388,608 bytes, sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, file sha256
re-checked unchanged after every pass. Table bytes
`file 0x74D380..0x74E1FF` hash
`0663af35a42c202df5411b2888b431f250c52830a5381dc3a073afdf7a1bfb8f`.

The census below was produced by four independent read-only measurement passes
and re-measured by the ticket owner. Where a delegated number disagreed with a
direct measurement the direct measurement is used and the disagreement is
recorded in section 11.

## 1. Storage contract

| item | value | status |
| --- | --- | --- |
| GBA address / file offset | `0x0874D380` / `0x74D380` | CONFIRMED |
| stride | `0x10` | CONFIRMED |
| accepted count | 232 | CONFIRMED |
| extent | file `0x74D380..0x74E1FF` (`0xE80` bytes) | CONFIRMED |
| first byte past the extent | file `0x74E200` | CONFIRMED |
| count representation | three compiled `cmp rN,#0xE8` loop bounds; no count word, no terminator | CONFIRMED |

Record layout, measured over all 232 records. The 16 bytes are fully covered by
these five fields; no byte lies outside them.

| offset | type | observed range | readers |
| --- | --- | --- | --- |
| `+0x00` | `u16` | 986..1310, 154 distinct | `0x08024FAC`, `0x080251BC` |
| `+0x02` | `u16` | 987..1311, 154 distinct, `== +0x00 + 1` on 232 of 232 | `0x080252E6`, `0x0802539E`, `0x08025EC2` |
| `+0x04` | `u32` | 12..306, 198 distinct | `0x080273B2`, `0x08027968` |
| `+0x08` | `u32` | 0 or 8..162, 98 zero | `0x080250CA` |
| `+0x0C` | `i32` | -9..149, 88 negative | `0x08027974`, `0x080279AA` |

`+0x00` and `+0x02` are indices into the verified text pointer table at
`0x0806BCE8`, scaled by four. `+0x04` is the value handed to the sprite
accessor `0x08000158` (ids `10..306` are the 297-entry run at `0x086B6BDC`).
`+0x08` is the slot handed to the portrait accessor `0x08011F20` (the 155-slot
run at `0x086F393C`). `+0x0C` is a signed index into `0x08711274` at `0x1C`
stride, tested with `blt` and skipped when negative. `+0x06`, `+0x0A` and
`+0x0E` are the high halves of the three `u32` fields and carry no independent
bit in the canonical image.

## 2. Consumer census

Every PC-relative literal load over the whole image was decoded and its pool
word read: exactly eight sites load `0x0874D380`, from exactly five pool words,
in six functions. A raw four-byte search at every byte offset returns the same
five words and nothing else, so there is no second encoding, no folded base and
no ARM-pool occurrence.

| site | function | pool | field read | how the index is bounded | class |
| --- | --- | --- | --- | --- | --- |
| `0x08024FA0` | `0x08024F3C` roster/display-list builder | file `0x25310` | `+0x00` | `cmp r0,#0xE8` / `blt` at `0x08024F92`, counter 0..231 | COMPILED CONSTANT |
| `0x08025086` | `0x08025056` record panel | file `0x25310` | `+0x08`, `+0x02` | `-1` selector test only, no ceiling | SENTINEL |
| `0x080251B6` | `0x08025056` record panel | file `0x25310` | `+0x00` | same element, same `-1` test | SENTINEL |
| `0x08025380` | `0x08025354` line-list render | file `0x256B8` | `+0x02` | none: the index arrives in a register | UNKNOWN |
| `0x08025E94` | `0x08025E50` record link and flag writer | file `0x2618C` | `+0x02` | none: the index is an argument | UNKNOWN |
| `0x080273AC` | `0x08027390` actor constructor | file `0x27474` | `+0x04` | none: the index is `*(u32*)arg` | UNKNOWN |
| `0x08027962` | `0x08027948` id search, loop 1 | file `0x279D8` | `+0x04`, `+0x0C` | `cmp r4,#0xE8` / `blt` at `0x08027998` | COMPILED CONSTANT |
| `0x080279A0` | `0x08027948` id search, loop 2 | file `0x279D8` | `+0x0C`, `+0x04` | `cmp r4,#0xE8` / `blt` at `0x080279CC` | COMPILED CONSTANT |

The three sites that carry no bound are not walkers. `0x08025354`,
`0x08025E50` and `0x08027390` each receive one index and address one record, so
there is no bound to update and no way for them to skip the new record once the
count is raised. `0x08027948` returns the record index or `-1` and its two
callers (`0x0800FB72`, `0x08010312`) test `-1` and substitute a default rather
than clamping the incoming id.

The two walkers and their bounds:

* `0x08024F3C`, reached from exactly one `bl` at `0x08007512`. It walks
  `0..231` against the runtime flag array and appends each set index to a list,
  collapsing adjacent equal `+0x00` values into a display list.
* `0x08027948`, reached from exactly two `bl` sites, `0x0800FB72` and
  `0x08010312`, both of which pass an actor's `+0x58` as the id. Two scans, the
  second for the stat-record path.

## 3. Duplicated count constants

A scan of `cmp`/`movs`/`adds`/`subs` immediates over the code banks and a
literal-pool value census of the whole image were run for 232 (`0xE8`), 231
(`0xE7`), 233 (`0xE9`), `0x1D0`, `0xE80`, `0xE70`, `0xE90`, `0x3A0` and
`0x3B4`.

* Exactly three real `cmp rN,#0xE8` instructions exist, all three in the table's
  own consumers: `0x08024F92`, `0x08027998`, `0x080279CC`.
* Three further halfword matches (`0x08029974`, `0x08047D00`, `0x08048650`) sit
  on the same 32-bit word `0x03002FE8` inside IWRAM pointer-initialiser stubs.
  They are data, not instructions, and are excluded.
* No `cmp rN,#0xE7` and no `cmp rN,#0xE9` exists anywhere in the image.
* No literal-pool word in the code region holds `0xE8`, `0xE7`, `0xE9`, `0x1D0`
  or `0xE80`. The count is not reloadable: there is no stored count, no
  count-versus-count comparison and no terminator test anywhere in the six
  functions.
* The only table-internal `0xE8`-family values are record fields: `+0x04` is 231
  in record 162 and 233 in record 164. A future scan must exclude the table body.

## 4. Reference census

| target | occurrences | class |
| --- | --- | --- |
| table base `0x0874D380` | 5 words, 8 consuming `ldr` sites | PATCHABLE AND OWNED |
| table end `0x0874E200` | 1 word, 1 consuming site (`0x08050FB2`) | DOES NOT REQUIRE CHANGE for a move; the reason growth in place is impossible |
| count `0xE8` | 3 instruction halfwords | PATCHABLE AND OWNED for growth, not for a move |
| individual records | zero direct references | n/a: every read is `base + (index << 4)` |

Zero unresolved load-bearing references. No word equals `0x0874D380 + i*0x10`
for any `i` in `1..231`, so a moved table strands nothing at record level. The
thirteen literal values in `[base-0x1000, base)` were inspected; none is used
with a sixteen-byte stride plus an index, so no folded base reaches the table.

The eight sites follow the relocated base automatically: each loads the base
into a register and then indexes it. Only the five words that supply that
register need to change.

## 5. The runtime flag array

The roster walk tests bit `(i & 7)` of the byte at `[block + 8] + 0xC5 + (i >> 3)`.
The reader loads its block from file `0x2530C` (`0x087319CC`); the writer loads a
different block, file `0x26188` (`0x08732374`). Both blocks hold `0x03001068` at
their `+0x08` word, measured directly, so both address the same array. Index `i`
therefore uses IWRAM `0x0300112D + (i >> 3)`.

232 indices occupy bytes `0x0300112D..0x03001149`, 29 bytes. Index 232 uses byte
`0x0300114A`, one byte past that. The writer has no bound, no mask and no
sentinel on the index, so the engine will write that bit.

Byte `0x0300114A` is interior to the block. The block's initialiser is reached
from the only literal load of `0x03001068`: `0x0804819A` is `ldr r0,[pc,#8]`,
whose pool word sits at `0x080481A4` and holds `0x03001068`. (An earlier revision
cited `0x08004AE4` as that pool; that address is four kilobytes away from the load,
which a Thumb literal load cannot reach, and it holds `0x000008A8`, the allocation
size used below.) The initialiser writes `+0xE4`, `+0x4F8` and `+0x8A0` and calls
`0x08046FF4` with the base at `+0x4F8`, the base at `+0x8A0` and a length of `0x68`,
so the object extends at least to offset `0x908`. The allocating branch of the same
routine uses size `0x8A8`. Offset `0xE2` is interior under either number, and that
interiority is what the bound argument rests on - not a claim that those bytes are
unused, which this document cannot support and does not. The width of the array is
therefore a consequence of the loop bound and not a separate capacity: raising
the bound raises the addressable range into bytes that already belong to the
block.

**Measured engine capacity, distinct from the above.** The roster builder
allocates `0xB20` bytes (`0x08024F42` `movs r0,#0x59` / `0x08024F44`
`lsls r0,r0,#5`) with a count at `+0x10` and four-byte entries from `+0x14`
holding one entry per set flag; its display list begins at `+0x3B4`.
`(0x3B4 - 0x14) / 4` is exactly 232. That array is dimensioned for the retail
maximum of set flags, and a 233rd record raises the theoretical maximum by one.
It is reached only when every flag is simultaneously set, which requires every
appearance to be present at once; the retail flag is per-encountered
appearance. This is recorded as a limit of the capability rather than as a bound
the build can patch, because the array is heap-allocated by retail code from a
compiled size.

**Correction, and it is a blocking one.** An earlier revision of this section
argued that "ordinary play does not approach" the limit, and that is an
assumption, not a measurement. Three things are true at once: the builder appends
one entry per set flag with no bound check of its own, its array is sized for
exactly 232 entries, and this document records flag initialisation and persistence
as UNKNOWN. Under `docs/ROM_SAFETY.md` a grown structure has to be checked against
the engine's own bounds rather than argued past, so the honest statement is that
**appending any record can overflow the roster array if its flag is ever set**, and
that nothing in this build prevents it. The count ceiling bounds what the
authoring surface may write; it does not bound a retail array the engine owns.

That makes the capability unsafe to claim until either the roster array grows with
the table and its display list is relocated, or the flag array's reachable maximum
is shown to stay at 232. Neither has been done here.

## 6. End-of-table neighbourhood

The 16 bytes immediately after the extent are live, multiply-named data, so a
233rd record cannot be written in place:

```
74E200 03001C4C 030019A4 00000000 000002A0
74E210 00000000 FFFFFD60 FFFFFD60 00000000
74E220 000002A0 00000000 03003898 03001C4C
```

`0x0874E200` is named by one literal load (`0x08050FB2`), `0x0874E208` by three,
`0x0874E228` by one, `0x0874E234` by five and `0x0874E614` by two: ten literal
load sites own the region. Slack after the table is zero. Slack before the table
is also zero: a four-byte table at `0x0874D35C` and an eight-entry pointer table
at `0x0874D360` end exactly where the appearance table begins.

Growth in place is therefore REFUTED twice over, and the relocation route is the
only one.

## 7. Gate decision

| requirement | finding |
| --- | --- |
| ownership known | five pool words, eight sites, byte-aligned whole-image census, no folded base, no duplicate table |
| record layout known | five fields, every reader instruction cited, every value range measured |
| every load-bearing consumer accounted for | six functions, eight sites, three compiled bounds, three unbounded single-index consumers |
| every required update identified | five literal words and three instruction halfwords |
| values fit their encoded widths | `cmp` immediate is `imm8`, so the ENCODING reaches 255, but the seen-flag array bounds a build to 240 records; index registers and index fields are 32-bit; the address carrier is a full 32-bit word |
| allocation and relocation supported | existing allocator and write path; the naming seams are listed in section 8 |
| no consumer can silently exclude or misindex | **FALSIFIED for the roster consumer.** All three bounds are patchable and named, and the flag byte for the new index is interior to the block, but the roster display-list builder appends one entry per set flag into an array sized for exactly 232 and checks nothing, so a raised count can overflow it. See section 5's correction; the flag byte for the new index is interior; the unbounded consumers take one index each and follow the base register |
| project reopen can represent it | not yet: the project format has no appearance representation, which is Phase B work |
| deterministic build plan exists | yes: allocate above EOF, emit the grown block, rewrite the five words, patch the three halfwords |

## 8. Required updates, exactly

1. Re-emit the whole table in expanded storage with `232 + n` records, where `n`
   is the number of authored appearances, preserving the existing 232 records
   byte-for-byte.
2. Rewrite the five literal-pool words at file `0x25310`, `0x256B8`, `0x2618C`,
   `0x27474` and `0x279D8` to the new GBA address. Each word must still hold
   `0x0874D380` before the rewrite, or the build refuses.
3. Patch the low byte of the three `cmp rN,#0xE8` halfwords at `0x08024F92`,
   `0x08027998` and `0x080279CC` from `0xE8` to `0xE8 + n`. These are CODE, not
   reference fields, so they are ordinary byte changes with their own note.
4. Fail closed when `232 + n` exceeds 240, the flag array's extent, and when the
   aligned block cannot be placed in expanded storage.

The two naming seams that do not exist yet, and their measured shape:

* an `AllocationKind` member for the appearance record table, with
  `DEFAULT_ADDRESSABILITY` `EXPANDED_ONLY`, because the canonical image declares
  one 256-byte free region against 3,712 bytes for the table alone;
* an anchor kind for the table in `layout.RELOCATION_ELIGIBLE_KINDS` and in
  `relocation._ALLOCATION_KIND`, plus a reference document that publishes the
  five words as `CONFIRMED_REFERENCE` / `ABSOLUTE_ROM_U32_LE` / delta 0.

## 9. Limits and open items

* **Runtime claim, OPEN.** No run has yet shown the retail engine following a
  repointed word into expanded storage for this table. The mechanism is proven
  on this engine for three other domains (a created warp array, a relocated
  graphics container and the relocated actor-sprite registry), and the
  appearance carrier is the same plain 32-bit literal word, but the appearance
  table itself is unproven above EOF. Phase B owns that run.
* **Roster index-array capacity, recorded limit.** See section 5. The array holds
  exactly 232 entries, and the authored record raises the theoretical maximum of
  set flags by one.
* **Entry path of `0x08025354`, UNKNOWN.** It has no `bl`, no branch target and
  no word equal to its address in the image. It is entered indirectly. It is not
  a walker, so this does not affect growth, and it is recorded rather than
  smoothed.
* **Flag-array initialisation and save persistence, UNKNOWN.** How the 29 bytes
  reach a defined state at boot, and whether they are persisted, was not
  established. Both are runtime state written by the engine, so neither is a
  bound the build has to update.
* **Old table bytes are left in place.** The move retires the canonical span
  without reclaiming it, so any undiscovered reference keeps pointing at intact
  original data rather than at freed storage.

## 10. Method and blind spots

Methods used: whole-image Thumb `ldr Rt,[pc,#imm]` decode at every even offset
with the pool word read from the image; raw four-byte value search at every byte
offset; whole-image Thumb `bl`/`blx` and `b`/`b.w` target decode; `cmp`/`movs`/
`adds`/`subs` immediate census over the code banks; literal-pool value census;
capstone Thumb disassembly of every consumer function and its callees; and
corpus statistics over all 232 records.

What none of these can see: a base computed at run time, a table reached by
offset from another base, a RAM-resident copy of the pointer, a `blx rN` with a
computed target, an address built from a base in a jump table, and a bound held
in a register loaded from a data `u16` rather than a pool word. No emulator run
was made for the static census; every runtime statement in this document is
labelled as an open item.

## 11. Corrections made during synthesis

* One measurement pass placed the flag array at `0x03003300 + 0xC5` by using the
  block's first word instead of its `+0x08` word. Direct measurement gives
  `[0x087319D4] = 0x03001068` for the reader and `[0x0873237C] = 0x03001068`
  for the writer, so the array is at `0x0300112D`. Section 5 uses the direct
  measurement.
* One measurement pass carried an initial premise that the character base-stat
  `+0x0A` field indexes this table. The measured `person` bytes are `2..45` and
  do not; a second pass independently refuted the same premise. It is not
  carried into the ticket.
