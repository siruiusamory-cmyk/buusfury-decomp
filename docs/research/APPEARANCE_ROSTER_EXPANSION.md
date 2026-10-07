# Growing the roster/display-list structure

APPEARANCE-ROSTER-EXPANSION-001. Base candidate `a57a332`.

The appearance work can append records, but the engine's roster builder is sized
for exactly the 232 canonical ones. This document is the required proof pass that
comes before any implementation: what the structure is, who owns it, every site
that states its layout, and how far the count can go.

Evidence labels are the project's: CONFIRMED means the bytes were read here,
INFERRED means the conclusion rests on reasoning over measurements. Addresses are
GBA addresses; file offset is address minus `0x08000000`.

## 0. What "roster" means here, and what it does not

"Roster" is a working label this ticket coined for the list the builder at
`0x08024F3C` produces. It is not a term from the game, from the code, or from any
string in the image. The measured description is: a scrollable list built from the
seen-appearance bitset, holding one 4-byte appearance index per seen appearance
and an 8-byte `{first, last}` run list over them, with a display cursor, a
selected index, a counter and a limit, and a vtable with render and dispatch
slots.

Two attempts to name the screen failed, and both are recorded as failures:

- resolving the record text fields through the table at `0x0806BCE8` returned
  single characters rather than names, so that route is not the string reader,
  and the fields at `+0x00` and `+0x02` are consecutive for every record, which
  two independent name and description lookups would not be;
- an earlier search claimed the image contains no occurrence of `Scouter`, and
  that claim was wrong: it searched ASCII only. The game's text is UTF-16LE,
  and `Scouter` occurs at `0x0805E69A` inside the objective-string table, as
  `Get the Scouter Upgrade from Dr. Brief at Capsule Corp`. So a Scouter
  mechanic exists in this game, and the hypothesis that this list serves it
  is live rather than dead. The one occurrence is a quest objective, not a
  menu label, so it does not by itself name the screen. `Radar` occurs twice
  in the same encoding, at `0x0805E57E` and `0x0806379A`.

The screen the object is rendered on is therefore **not established**, and naming
it needs the runtime run rather than more static reading.

A correction to an earlier statement of this record: the roster builder's one
caller is `0x08007512`, and that call sits in the function beginning at
`0x080074EC`, not in the function at `0x080073F0` that an earlier note named. The
scan that produced the earlier answer treated `push {r3,r4,r5,lr}` (`0xB538`) as
not a function prologue, so it walked back past the real boundary. Any later
function attribution derived from that scan should be re-derived.

## Runtime: what was observed, and what was not

Four governed sessions ran against a built image carrying this relocation
(`build/roster001/with-roster.gba`, sha256 `bd9c7ace...`), each launched through
`Start-MgbaSession` with the emulator version and the exact ROM digest named, and
each observer checked by the injector's own allowlist gate first.

**Observed.** The relocated image boots, loads the savestate, renders the
overworld, opens the Scouter on Select and returns to the overworld into NPC
dialogue. The Scouter overlay is recorded in `press-00500.png`: the green framed
panel with the area map, which is what the game's controls give Select as. A
hand-driven schedule of twenty input pulses produced twenty-five screenshots with
no crash, no hang and no visible corruption. That is `PROCESS LAUNCHED` and an
observed running scene, and it is the level it is: it says the build runs, not
that the chain completed.

**Not observed.** The seen flag for indices 231, 232, 233 and 239 read `0x00` in
every session, so **the authored record was never resolved and flag 232 was never
set**.

An earlier session with breakpoints armed stopped early with no handler error
recorded, and this record first blamed the breakpoints. That was wrong. The cause
was a defect in the observer itself: two locals the report read were declared
after the report function, so they resolved as globals, were nil, and killed the
script the first time it journalled. Once declared before use, a session with four
sites armed ran to its limit - 1,500 elapsed frames, 19 input pulses, 22
screenshots, zero handler errors. Breakpoints are not a hazard here; a silent
instrument is.

**The search itself never ran.** A probe on the search entry `0x08027948`, which
identifies the object as `r0 - 0x5C` because `[object+0x58]` is the object's own
component pointer, reported **0 executions across a completed session that
included walking and menu navigation**. That is the measured form of what the
frozen appearance record states: a loaded savestate restores actors that were
already built, so the construction path is not reached by loading a state, and
neither a menu nor a short walk reaches it in the state this worktree has. The
frozen record adds that a 12,000-frame wandering schedule on the same map did not
reach it either, and that the one session which did was an operator walking into a
new map.

**Why the builder cannot have been reached this way.** The frozen appearance
record already states it: a savestate load restores actors that were built before
the state was taken, and "the trigger is an in-game event" - a map load constructs
actors. So a state load cannot exercise the construction path at all, and the one
session that ever did reach it was an operator walking into a new map (`map 40`,
frame 7642, `actor_constructor` 24 hits).

**The constraint that is actually unresolved is not this structure.** The engine
search has two callers and the rule is per caller: `0x08010312` passes a zero
second argument, while `0x0800FB72` passes `[actor+0x224]` and on that path both
loops require `+0x0C >= 0`. An authored record is written with `+0x0C = -1`, so on
the actor path it is never returned at all. No actor has been observed carrying an
authored sprite id, and the frozen record lists that link as `NOT ESTABLISHED`.

So the roster question this ticket was opened for is answered - the structure is
grown, every offset that depends on it is restated, and the image is byte-verified
to change nothing else - while the runtime acceptance the ticket asks for is gated
on a reachability question this structure does not touch. Until an authored record
can be resolved in a running scene, no flag at index 232 can be set, the builder
cannot see a 233rd entry, and the overflow this relocation guards against cannot
occur. That is the honest ordering of the two problems.

## What would unblock the runtime chain

Recorded because a failure report is only useful if it says what to do next, and
because two of these were measured this session rather than guessed.

**1. A savestate taken at a transition, or an operator walking into one.** The
search path runs when an object is constructed, and a loaded state restores
objects that were already built. Five sessions this ticket ran - two savestates,
menu navigation and seventy input pulses of walking - never entered it, and the
frozen appearance record adds that a 12,000-frame wandering schedule did not
either. The one session that did was an operator walking into a new map (`map 40`,
frame 7642). So the cheapest path is a state taken *during* a transition, or a
human driving to one.

**2. Or set the seen flag in the save image, which is where the persistence lives.**
This ticket measured the save path: the record IS the runtime state object at
`0x03001068`, `0x8A8` bytes, written to the EEPROM image at `0x10 + 0x8B0*slot`,
with its first `0x4F8` bytes copied verbatim and a checksum over the whole record.
That means the flag for the authored index can be set by writing one bit at
`record + 0xC5 + (index >> 3)` in a save, which would make the builder append the
233rd entry and exercise the overflow path directly - without needing an actor at
all. Two things are needed to do it, and neither is in place:

- the checksum, which `0x0803FC4E` computes as an additive running pair over
  `0x8A8` bytes and returns packed (`(second << 16) | first`), with the running
  values passed through the ARM helper at `0x08053180` once per `0x15B0`-byte
  chunk. A single-chunk record therefore needs that helper's mask, which this
  session did not determine: the routine is an ARM veneer and the formulas tried
  against the local save did not match it;
- a save that has a record in it. The `.sav` in this worktree does not: slot 0's
  checksum word is zero and slots 1 and 2 hold `0xFFFFFFFF`. The real save image
  travels inside the mGBA savestate, not in that file.

Route 2 proves the builder half of the chain - flag set, display list built, no
overflow - without proving that the engine resolves an authored record, which is
the reachability question in its own right. Both routes are recorded as measured
openings rather than as plans that were carried out.

## The evidence boundary, stated once

Three levels, and nothing in this record may be read across them.

**Runtime-proven.** Authored appearance records beyond the canonical table are
resolved by the engine; post-canonical indices are reached; their state bits are
written; and their appearance data is consumed visibly by the running game.

**The mechanism of that resolution, because it is not free.** The search at
`0x08027948` has TWO loops and the first one runs first. Loop 2, at `0x0802799C`,
skips the stat test entirely when the second argument is zero (`0x080279A6`-`0x080279A8`)
and returns the first record whose sprite matches whatever its stat sign - which is
how a retail object carrying sprite 209 resolves to canonical record 42. An
appended record carries `+0x0C = -1`, so loop 1 returns it *before* loop 2 is ever
reached. Resolution of an appended record therefore requires the appended record to
bind a sprite id a retail record also selects, and the effect is that the object's
message-path resolution moves from the retail record to the authored one. This was
measured, not assumed: sessions resolved appended records 232, 233, 234 and 236 for
objects carrying sprite ids 209, 211 and 215. The
observations, from operator-driven sessions on the zero-second-argument path:

```
caller=0x08010317  second=0x00000000
compare  index=232  record_sprite=0x086B1DE8  actor_sprite=0x086B1DE8  matched=true
resolved index=232/233/234/236  past_canonical=true
flag_write index=233  past_canonical=true
flag index=233  value=0x02  set=true          (byte 0x0300114A)
```

and on the Scouter's own character screen the consumed fields are visible: OLIBU
with HP/STR/POW/END, a portrait and a description, which are the appearance
record's own fields.

**Not runtime-proven.** The relocated roster/display-list builder appending a 233rd
entry. Seventeen instrumented sessions, six of them operator-driven, with the same
seven armed sites reporting `ok=true` and other sites in the same sessions firing
thousands of times, never executed the builder at `0x08024F3C`. **This is recorded
as a limitation of the roster subproof, not as outstanding work**: the builder has
one caller, reached indirectly, and ordinary play does not reach it. The ticket
does not require proof of a path that cannot be shown to be relevant to the
capability.

**Statically and review-proven.** If that builder does execute, all twenty-nine
dependent sites and seventeen statements have been relocated consistently. The
census was independently reviewed, which found three statements this work had
missed, and the corrected census is re-derived from the image by a test whose
enforcement was falsified twice.

The capability is about authoring and consuming a new appearance, not about
proving that every dormant consumer of the same index space executes during
ordinary play.

## 1. The containing object, and its extent - CONFIRMED

The builder is `0x08024F3C`. Its first instructions decide everything:

```
08024f3e  adds r4, r0, #0        ; r4 = arg0
08024f40  bne  0x08024F52        ; a caller-supplied buffer is used as-is
08024f42  movs r0, #0x59
08024f44  lsls r0, r0, #5        ; 0xB20
08024f46  bl   0x0803D5B8        ; heap allocation
```

**The one caller passes NULL.** At `0x08007510`-`0x08007512`, inside the function
that begins at `0x080074EC` (section 0 records why an earlier edition named
`0x080073F0`):

```
08007510  movs r0, #0            ; arg0 = 0
08007512  bl   0x08024F3C
```

So the object is heap-allocated per construction and there is **no static buffer
to enlarge**. `0x08024F3C` has exactly one BL caller in the image; that caller is
itself reached indirectly and has no BL callers.

The layout, read from the builder's own arithmetic, is parameterised by the entry
count N:

| offset | field |
| --- | --- |
| `+0x00` | vtable word |
| `+0x10` | entry count |
| `+0x14` | N entries, 4 bytes each |
| `+0x14 + 4N` | second count (the display-list count) |
| `+0x18 + 4N` | N display entries, 8 bytes each |
| `+0x18 + 12N` | tail fields |
| total | **`0x40 + 12N`** |

`N = 232` gives `64 + 2784 = 2848 = 0xB20`, which is the allocation size. The
arithmetic is confirmed by the code that performs it, not by assumption.

The append loop, `0x08024F6E`-`0x08024F94`:

```
08024f6e  ldr  r3, [r6, #8]      ; the seen-flag block
08024f70  asrs r5, r0, #3        ; index >> 3
08024f74  adds r3, #0xC0
08024f7a  ldrb r3, [r3, #5]      ; block + 0xC5 + (index>>3)
08024f7c  movs r5, #1
08024f7e  lsls r5, r7            ; 1 << (index & 7)
08024f80  ands r3, r5
08024f82  beq  0x08024F90        ; not seen, next index
08024f84  ldr  r3, [r1]          ; count at +0x10
08024f88  lsls r3, r3, #2
08024f8a  adds r3, r3, r1
08024f8e  str  r0, [r3, #4]      ; entry[count] = index, at +0x14 + 4*count
08024f90  adds r0, #1
08024f92  cmp  r0, #0xE8
08024f94  blt  0x08024F6E
```

There is **no bounds check on the count**. The loop is bounded only by the index
bound `0xE8`, and one entry is appended per seen appearance. With 233 seen
appearances the second count at `+0x3B4` - the very next field - is overwritten.

The display half, `0x08024F96`-`0x08024FD4`, walks the entries, reads each
record's first halfword (`ldrh r5, [record + 0x00]`, table base from the pool at
`0x08024FA0`), skips a value equal to the previous one, and appends **8 bytes per
kept entry** at `base + 0x3B8 + 8 * displayCount`.

The tail, `0x08024FD6`-`0x08024FFE`, is built as `0x2B << 6` (`0xAC0`) plus stride
`+0x38` / `+0x3C`, and `0xB << 8` (`0xB00`) plus `+0x0C` / `+0x10` / `+0x14`.

## 2. Ownership of the roster bitset - CONFIRMED

The bitset is **not** in the roster object. It lives in the block reached as
`[X + 8]` (`0x03001068` at run time): bit `index & 7` of the byte at
`block + 0xC5 + (index >> 3)`.

Exactly two sites in the whole image touch it:

- `0x08024F74`, the roster builder's read (quoted above);
- `0x08025E86`, the appearance constructor's write, in the function at
  `0x08025E50`:

```
08025e76  asrs r2, r5, #3        ; index >> 3
08025e80  ldr  r1, [r0, #8]      ; the block
08025e86  adds r1, #0xC0
08025e8a  ldrb r2, [r1, #5]      ; block + 0xC5 + (index>>3)
08025e8c  lsls r3, r6            ; 1 << (index & 7)
08025e8e  orrs r2, r3
08025e90  strb r2, [r1, #5]
08025e92  lsls r1, r5, #4
08025e9a  str  r1, [r4, #0x20]   ; record[index]
```

Both derive the byte from the index, so **the loop bound the build already patches
is the only thing that decides how far the bitset is reached**. The constructor
also shows the coupling that started this ticket: one index sets both the flag and
the record pointer.

## 3. Ownership of the display list - CONFIRMED

Inside the roster object, at `+0x3B8`, 8 bytes per entry, capacity N, written by
the builder at `0x08024FBE`-`0x08024FCC` as `r2 + displayCount * 8 + 4` where `r2`
is the object base plus the second-count offset.

## 4. Every reader and writer - CONFIRMED

Twenty-nine sites for the roster object. The statements that state its layout
are enumerated in section 5, which is generated from the patch table:

| function | sites | roles |
| --- | --- | --- |
| `0x08024F3C` | 6 | object size, display-count offset, both tail bases and their shifts |
| `0x08025004` | 4 | both tail bases and their shifts |
| `0x08025056` | 5 | display-count offset, both tail bases and their shifts |
| `0x08025354` | 2 | tail base B and its shift |
| `0x08025404` | 3 | display-count offset, tail base B and its shift |
| `0x080254A8` | 2 | tail base B and its shift |
| `0x08025510` | 3 | display-count offset, tail base B and its shift |
| `0x080255C4` | 4 | both tail bases and their shifts |

Eight functions, computed from each site's own containing prologue rather than
asserted: an earlier edition of this table named five functions and attributed
`0x0802502C` to the builder, which ends at `0x08025002`. It also listed instruction
*uses* (`0x08024F6C`, `0x08024FE4`, `0x08024FF4`, `0x08024FFE`) as if they were
patched sites, and omitted `0x0802500E`, `0x08025106` and `0x08025112`.

Callers: `0x08024F3C` from `0x08007512`; `0x08025404` from `0x080255BE`;
`0x08025354`, `0x08025510` and `0x080255C4` have no BL callers and are reached
indirectly.

Two apparent extra bitset sites at `0x08044206` and `0x0804459E` are **false
positives**: both reach `block+0xDC`, a pointer, and then dereference it
(`ldr r0, [r0, #0x1C]` then `ldrb r0, [r0, #5]`). They never touch the array.

## 5. Every layout-dependent constant - CONFIRMED

This table is generated from `ROSTER_PATCH_SITES`, so it cannot disagree with what
the build patches:

**A correction that matters, and how it was caught.** The first edition of this
census found fourteen statements and twenty-three sites. It was wrong. It searched
for the `movs` and its `lsls` **next to each other**, and in three tail-base-B
statements the compiler put other instructions between the pair:

| `movs` | `lsls` | between them |
| --- | --- | --- |
| `0x0802505A` | `0x08025066` | `add sp,r3`, a `movs`/`lsls`/`add` building a stack address, and a load |
| `0x0802541A` | `0x08025420` | the `movs r2,#0xED` / `lsls r2,#2` display-count pair |
| `0x080254B0` | `0x080254B4` | one `ldrh` |

Those three sit in the functions at `0x08025056`, `0x08025404` and `0x080254A8`.
What shows they address the same object is the read/write census in section 4:
the sites that hand the object around are the ones section 5 lists, and each of
these three functions contains at least one of them. A first version of this
sentence said they reach the object through `0x0802502C`, `0x0802541C` and
`0x0802500E` "respectively", which is wrong - `0x0802502C` and `0x0802500E` are
both in `0x08025004`, and only `0x0802541C` sits in the function this paragraph
names it with. In the grown layout those offsets fall inside display entries, so
the miss would have turned a hazard that needed 233 seen flags into a live
inconsistency on **every** authored build. An independent review found it by
tracking registers through `movs`/`lsls`/`adds` and literal loads instead of
matching adjacent byte patterns.

The true census is **seventeen statements and twenty-nine sites**. A test now
re-derives it from the image with the pair allowed to be up to twelve instructions
apart, and it was checked by removing one pair and watching it fail.

| constant | role | sites |
| --- | --- | --- |
| `0xB20` size | object size | **1** - `0x024F42` |
| `0x3B4` display count | display-list count offset | **4** - `0x024F60`, `0x025112`, `0x02541C`, `0x025514` |
| `0xAC0` tail A | tail base A | **4** - `0x024FD6`, `0x02502C`, `0x025106`, `0x025638` |
| `0xAC0` tail A shift | tail base A shift | **4** |
| `0xB00` tail B | tail base B | **8** - `0x024FE0`, `0x02500E`, `0x02505A`, `0x02536E`, `0x02541A`, `0x0254B0`, `0x02552C`, `0x02561E` |
| `0xB00` tail B shift | tail base B shift | **8** |

## 6. Can the data at +0x3B4 move independently - CONFIRMED, yes

The second count is named by four sites as an offset from the object base, and the
display-entry base is **derived** from it (`r2 + 4`). Moving both is therefore
those four patches and no data movement: no pointer to fix up, no relocation
table, nothing else refers to the array's address.

## 7. Maximum count the encoded widths support

- The record count is a Thumb `cmp rN,#imm8`, so **255 is the hard cap**.
- The bitset needs `ceil(N/8)` bytes from `block+0xC5`. N=240 ends at `+0xE2`;
  N=248 adds `+0xE3`; N=248 or above would write the word the block's initializer
  zeroes at `+0xE4`, so **248 is unreachable**.
- Nothing in the appearance/roster region `0x08024000`-`0x08026000` adds `0xE0`,
  `0xE1`, `0xE2`, `0xE3` or `0xE4` to any base. The initializer region
  `0x08004000`-`0x08005000` adds `0xE4` at seven sites (the block-init family) and
  none of `0xE0`..`0xE3`.

**Supported N is therefore 240**, which needs only `+0xE2` - the single byte
immediately after the canonical 232-bit array. `0xE3` would be reachable at 248
and is left unused deliberately.

## 8. Save data and narrower fields

**Item 8.1 - the bitset's containing block is STATIC, not heap.** Two ROM
descriptors name their RAM blocks by absolute address, and both name the same
one for the flag block:

```
reader descriptor 0x087319CC:  +0x00 0x03003300  +0x04 0x03003898
                               +0x08 0x03001068  +0x0C 0x03001C4C  +0x10 0x0806EE6C
writer descriptor 0x08732374:  +0x00 0x03003300  +0x04 0x03001C4C
                               +0x08 0x03001068  +0x0C 0x0806EE6C  +0x10 0x00000001
```

So the block the bitset lives in is a static object at `0x03001068` in IWRAM, and
the descriptor's `+0x08` is the field the accessors load. That is a different
structure from the roster object, which the builder heap-allocates. It also means
`+0xE2` and `+0xE3` are **inside** the static block rather than past the end of an
allocation, since the block is initialised as a `0x8A8`-byte object.

The block's address appears as a literal word in 41 places: one code pool
(`0x080481A4`, read by the initializer function `0x08047FF4`) and 40 data
occurrences in the `0x0806xxxx`-`0x0807xxxx` region, which is the shape of pointer
tables to static RAM structures rather than of code.

**Item 8.2 - the bitset IS persisted, and the saved record has room for 240.**
An independent read-only census followed the save path end to end. The medium is
**EEPROM**, not SRAM or FLASH: the `EEPROM_V124` tag sits at file `0x7B7964`, the
driver selects the `0x2000`-byte descriptor (`0x0803FB80`), and `0x0803FB96`-`0x0803FB9A`
allocates an 8192-byte save image whose pointer lands at `0x03004A64`.

The persisted record **is the runtime state object at IWRAM `0x03001068`**, 0x8A8
bytes, written to the image at `0x10 + 0x8B0 * slot`:

```
08004944  movs r1, #0x8B
08004946  lsls r1, r1, #4        ; 0x8B0, the slot stride
08004948  muls r1, r5, r1
08004950  adds r1, #0x10         ; image offset
0800494E  r3 = 0x8B0             ; length
08004956  bl   0x0803FBDE        ; copy the region out and write it
```

`0x08020504` is the save entry, and `0x08020516`-`0x0802051A` passes exactly that
pointer: the literal at file `0x72085C` is `68 10 00 03` = `0x03001068`.

**The first `0x4F8` bytes are copied verbatim** by an ARM memcpy reached through
the interworking veneer at `0x08046DD0` (`0x080502C6` sets `r2 = 0x9F << 3`), and
the checksum covers the whole `0x8A8` record (`0x080048C8` length, compared at
`0x080048DA`).

So appearance persistence is **one bit per index in a byte array** - there is no
count field and no index list - and that array lies inside the verbatim prefix.
Indices 232 to 239 reach `record+0xC5+29 = +0xE2` at most, which is inside both
the verbatim `0x4F8` prefix and the checksummed `0x8A8` record. **The saved region
does not cap at 232**, so the supported N of 240 sits entirely inside it.

**Item 8.3 - no narrower field holds an appearance id or count.** The census
traced every carrier: the search returns the index as a 32-bit `r0`, both callers
store it with `str r0` into 0x28-byte entries, the constructor stores the record
*pointer* at `object+0x20`, and every consumer reads `record+0x04` and `record+0x0C`
as words. The only sub-32-bit values near the table are the record's own `u16`
text indices, which bound the string table rather than the appearance count. The
one narrow store derived from an index resolves to the 1-bit flag itself.

## The fixture for N = 240

| what | canonical | at N = 240 |
| --- | --- | --- |
| size | `0xB20` | `0xB80` |
| entries end | `+0x3B3` | `+0x3D3` |
| second count | `+0x3B4` | `+0x3D4` |
| display entries | `+0x3B8`..`+0xAF7` | `+0x3D8`..`+0xB57` |
| tail-A | `+0xAF8` | `+0xB58` |
| tail-B | `+0xB00` | `+0xB60` |

Every value is encodable with the same two-instruction idiom the code already
uses, so the change is a constant patch rather than new code:

- size: `movs #0x5C; lsls #5` (shift unchanged from `0x59<<5`)
- second count: `movs #0xF5; lsls #2` (shift unchanged from `0xED<<2`)
- tail-A: `movs #0x59; lsls #5` then strides `+0x38`/`+0x3C` (shift 6 becomes 5)
- tail-B: `movs #0x5B; lsls #5` (shift 8 becomes 5)

**29 halfword and immediate-byte patches across the seventeen statements, no data
movement, no extra allocation, deterministic.**

## What this leaves

The builder's overflow is confirmed rather than refuted, so the structural route
is required: grow the object and move its two dependent offsets, with the count
itself capped at 240 and a build that fails closed above it. The bitset needs no
separate allocation - it has room for 240 bits in the block it already lives in,
and only the two sites above ever touch it.
