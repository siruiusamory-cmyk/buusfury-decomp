# Buu's Fury type-0 dialog runtime semantics

Measured against canonical `buus_fury_usa_rev0_01c1707f`, sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

TOOLKIT-019 proved that the 236 type-0 records behind table `0x0879B704` are
scripts for the VM the toolkit already models, and that the engine's own term
for them is **dialog**. It closed with player-visible meaning UNKNOWN.

This document resolves that: a type-0 dialog **renders text on screen**, and
the text comes from the **existing verified UTF-16 Buu text table**
`0x0806BCE8`, the same table TOOLKIT-004 tiled and TOOLKIT-014 proved the item
consumer reads.

## Headline

```
dialog  ->  native slot 178  ->  0x0802BFBC  ->  text table 0x0806BCE8
                                            ->  0x0802BECC  ->  OAM sprite text
```

Evidence class: **CONFIRMED_ROM**, with **VERIFIED_UPSTREAM** behavioural
corroboration for the specific strings involved.

This is a **new relation**, established through a new proven consumer chain, as
TOOLKIT-019 required. It does not reverse TOOLKIT-018: that ticket refuted
*map-event operands* as text ids for its three investigated families, and this
finding touches none of those families. See "Preserved refutations" below.

## Corpus census

All 236 supported type-0 dialogs were censused; nothing here is sampled.

- 236 dialogs, 10,263 code bytes, all decoding and re-encoding exactly
- 4,826 instructions total
- **107 distinct native slots** used across the corpus

### Opcode frequency

| Opcode | Name | Count | Dialogs |
|---:|---|---:|---:|
| `0x02` | `native_stack` | 1656 | 230 |
| `0x00` | `push_byte` | 1126 | 193 |
| `0x11` | `terminate` | 378 | 236 |
| `0x13` | `branch_if_zero` | 340 | 90 |
| `0x1D` | `push_many` | 305 | 100 |
| `0x03` | `native_pop` | 251 | 15 |
| `0x10` | `less_equal` | 197 | 5 |
| `0x04` | `logical_and` | 117 | 24 |
| `0x0A` | `divide_raw` | 97 | 3 |
| `0x0E` | `greater_equal` | 93 | 5 |
| `0x08` | `subtract` | 86 | 10 |
| `0x01` | `push_signed_magnitude` | 38 | 22 |
| `0x0B` | `equal` | 30 | 19 |
| `0x12` | `branch_forward` | 28 | 7 |
| `0x07` | `add` | 23 | 9 |
| `0x0C` | `not_equal` | 15 | 5 |
| `0x0F` | `less` | 13 | 2 |
| `0x05` | `logical_or` | 8 | 8 |
| `0x1B` | `transfer_to_alternate` | 6 | 6 |
| `0x1C` | `alternate_count_back` | 6 | 6 |
| `0x09` | `multiply` | 5 | 5 |
| `0x0D` | `greater` | 4 | 4 |
| `0x06` | `negate` | 3 | 2 |
| `0x15` | `native_post_15_raw` | 1 | 1 |

A dialog is overwhelmingly a sequence of native calls with pushed arguments.
`native_stack` alone is 1,656 of the 4,826 instructions, the single largest
opcode by a wide margin, and appears in 230 of 236 dialogs. So the native
table, not the arithmetic opcodes, is where dialog semantics live. That is
what selected the investigated families.

### Native slots by breadth

Ranked by how many distinct dialogs use them, not by raw call count: a
presentation primitive is one many dialogs reach.

| Slot | Dialogs | Calls | Native |
|---:|---:|---:|---|
| 29 | 54 | 54 | `0x080007E7` |
| 27 | 44 | 53 | `0x080007B7` |
| 48 | 37 | 37 | `0x08000AFD` |
| 83 | 35 | 53 | `0x080015BB` |
| 139 | 34 | 34 | `0x08002703` |
| 121 | 32 | 32 | `0x08002439` |
| 99 | 30 | 30 | `0x08001BC3` |
| 100 | 29 | 29 | `0x08001C1D` |
| 96 | 24 | 35 | `0x08001AB1` |
| 28 | 22 | 24 | `0x080007CD` |

Slot 29 is the already-proven save-flag SET from TOOLKIT-018, which is what
makes this ranking trustworthy: the method reproduces a known result at the top
before being used on unknowns.

## Family selection

The ticket budget is three deep investigations. Selection was made by asking
each of the 107 slots one objective question, does its call graph reach the
verified text pointer table `0x0806BCE8` within depth 4, rather than by
picking slots whose operands merely looked like text ids.

**Exactly one slot answered yes: slot 178, at depth 1, in 8 dialogs.**

That single hit is the reason this ticket resolves rather than guesses. The
other 106 slots were excluded by a measurement, not by an opinion.

Families investigated:

1. **Slot 178**: the content family. CONFIRMED.
2. **Slot 139**: the strongest lifecycle candidate (most common terminal call).
3. **Slot 48 / slot 83**: the queue-and-construct candidates.

---

## Family 1: slot 178, `0x08003031`: CONFIRMED text presentation

### Handler contract

`0x08003030` pops **three** values, innermost last:

```
0x08003032  ldr  r1,[r0]        ; VM stack pointer
0x0800303E  ldr  r1,[r1,#4]     ; pop 1 -> [sp+8]
0x0800304C  ldr  r1,[r1,#4]     ; pop 2 -> [sp+4]
0x0800305A  ldr  r0,[r0,#4]     ; pop 3 -> r0
0x0800305C  add  r1,sp,#4       ; r1 = &{pop2, pop1}
0x0800305E  bl   0x0802BFBC
0x08003068  bl   0x0801191A     ; push result back on the VM stack
```

So the **third** value popped (the one pushed **first**) is passed in `r0`,
and the other two are passed as a coordinate pair by pointer. The result is
pushed back onto the VM stack, so a dialog can keep a handle to the object it
just created.

This pop order is read from the handler, exactly as TOOLKIT-018 read the two
event-resource consumers. It is not inferred from operand position.

### The text-table access

`0x0802BFBC` is the proof:

```
0x0802BFC0  ldr  r1, =0x0806BCE8   ; the verified Buu text pointer table
0x0802BFC2  lsls r0, r0, #2        ; index * 4
0x0802BFC4  ldr  r4, [r1, r0]      ; r4 = string pointer
0x0802BFCA  ldr  r0, [r6,#4]       ; font object
0x0802BFCC  bl   0x0803FFE8        ; measure the string
0x0802BFD0  adds r0, #0x21
0x0802BFD2  lsrs r5, r0, #5        ; round up to whole 32px tiles
0x0802BFD4  lsls r5, r5, #5
0x0802BFDA  bl   0x8011732         ; reserve that much VRAM
0x0802BFE6  bl   0x0802BECC        ; build the text object
```

`ldr base; lsls #2; ldr [base, index]` is **byte-for-byte the access pattern
TOOLKIT-014 already proved** at `0x0801F85E` for the item consumer. The same
table, the same shift, the same indexing form. This is not a numeric
resemblance to a text id, it is the text table's own established consumer
shape, reached from a dialog.

### `0x0803FFE8` is a string-measuring routine, not a number cruncher

```
0x0803FFEA  ldrh r3,[r1]       ; read a UTF-16 code unit
0x0803FFEE  cmp  r3,#0         ; NUL terminates
0x0803FFF4  adds r1,#2         ; advance one halfword
0x0803FFF6  cmp  r3,#0xFF      ; wide/narrow glyph split
0x08040000  ldr  r4,[r0]       ; font metrics table
0x08040004  ldrh r3,[r4,r3]    ; per-glyph advance width
0x0804000C  adds r2,r3,r2      ; accumulate
```

It walks **UTF-16LE halfwords to a NUL terminator** and sums per-glyph advance
widths from a font metrics table. That is the exact encoding TOOLKIT-004
verified for this text pool (`utf16le_nul_terminated`). A routine that consumes
the pointer *as a UTF-16 string* is what upgrades this from "reads a table" to
"reads text".

### The output is on-screen sprite text

`0x0802BECC` builds the object; `0x0802BFEC` emits it:

```
0x0802BFFA  ldr  r7, =0x80002000   ; OBJ attribute template
0x0802C000  ldr  r4,[r0,#0x14]     ; Y
0x0802C004  lsls r4,r4,#0x17
0x0802C006  lsrs r4,r4,#7          ; Y masked to 8 bits  (OAM attr0)
0x0802C01A  ldrh r4,[r0,#0xC]      ; X
0x0802C020  lsls r4,r4,#0x16
0x0802C026  lsrs r4,r4,#0x16       ; X masked to 9 bits  (OAM attr1)
0x0802C030  adds r2,#8             ; 8 bytes per OAM entry
0x0802C032  adds r3,#0x20          ; 32 pixels per sprite
```

8-byte entries, an 8-bit Y field, a 9/10-bit X field, stepping 32 pixels, this
is the GBA OAM sprite-attribute layout. The sibling routine at `0x0802BF8E`
blits glyph tiles into `0x06010000`, the GBA OBJ VRAM base.

The string is also horizontally centred on the supplied coordinate:

```
0x0802BF5E  ldr  r0,[r4,#0x10]   ; total pixel width
0x0802BF66  asrs r0,r0,#1        ; width / 2
0x0802BF68  subs r0,r1,r0        ; x - width/2
0x0802BF6A  str  r0,[r4,#0x14]
```

**Player-visible classification: text drawn as hardware sprites, positioned by
the dialog, centred on the given X.** Observed from code, not interpreted.

### Operand provenance

Seven dialogs supply the text index as a literal, and the shape is identical in
all seven:

| Dialog | Instruction | Text id | X | Y | String |
|---:|---|---:|---:|---:|---|
| 290 | `push_many 3,1525,120,65` | 1525 | 120 | 65 | `Match 2 Fight!` |
| 291 | `push_many 3,1526,120,65` | 1526 | 120 | 65 | `Match 3 Fight!` |
| 292 | `push_many 3,1527,120,65` | 1527 | 120 | 65 | `Match 4 Fight!` |
| 295 | `push_many 3,1529,120,65` | 1529 | 120 | 65 | `Match 6 Fight!` |
| 296 | `push_many 3,1530,120,65` | 1530 | 120 | 65 | `Match 7 Fight!` |
| 297 | `push_many 3,1531,120,65` | 1531 | 120 | 65 | `Match 8 Fight!` |
| 298 | `push_many 3,1532,120,65` | 1532 | 120 | 65 | `Match 9 Fight!` |

`push_many` pushes n values in order, so the **first** listed is the bottom of
the three and is therefore the **third** popped, precisely the value the
handler routes to `r0` and into the table index. Operand order and pop order
agree independently.

X = 120 is exactly the centre of the 240-pixel GBA screen, which is what the
centring code above expects. Y = 65 is the same for all seven.

### Why these strings settle it

The text ids are sequential across sequential dialog indices, and the strings
they resolve to are themselves a sequence:

```
1524 'Match 1 Fight!'   1529 'Match 6 Fight!'
1525 'Match 2 Fight!'   1530 'Match 7 Fight!'
1526 'Match 3 Fight!'   1531 'Match 8 Fight!'
1527 'Match 4 Fight!'   1532 'Match 9 Fight!'
1528 'Match 5 Fight!'   1533 'Match 10 Fight!'
```

Dialog 290 -> "Match 2", 291 -> "Match 3", ... 298 -> "Match 9". Structural
position and semantic content agree with no gaps in the mapping.

The apparent gaps in the *dialog* run are explained by the codec boundary
rather than by a defect: dialogs 289, 293 and 299 are **type 4**, which
TOOLKIT-019 declared UNSUPPORTED because its expansion routine is relocated to
IWRAM. The dialogs that go missing are exactly the ones this toolkit cannot
read, and the ones it can read are exactly the ones that fit the sequence. That
is a strong consistency check the hypothesis could have failed and did not.

### External corroboration (VERIFIED_UPSTREAM, behaviour only)

Buu's Fury contains a 25th World Martial Arts Tournament chapter in which,
per published walkthroughs, the player must "defeat ten fighters in a row to
become champion". Ten sequential matches is exactly the shape of the ten
strings 1524..1533.

That corroborates **what these particular strings are for**. It is recorded as
an external observation and is not load-bearing: the mechanism above is proven
from ROM alone. No upstream name was imported.

Sources:
- [GameFAQs guide index](https://gamefaqs.gamespot.com/gba/920530-dragon-ball-z-buus-fury/faqs/40657)
- [CheatCodes walkthrough](http://www.cheatcodes.com/guide/walkthrough-dragon-ball-z-buus-fury-gba-66184/)
- [Dragon Ball Wiki](https://dragonball.fandom.com/wiki/Dragon_Ball_Z:_Buu's_Fury)

No source describes the on-screen presentation format, so no source was used to
name it. "Textbox", "speech bubble" and "dialogue window" are **not** claimed.

### Dialog 516: the same call with a runtime index

```
+16  push_many 2,120,65      ; only X,Y are literal
+22  native_stack 178
+26  push_many 2,120,85
+32  native_stack 178
```

Here the index is whatever `native_stack 4` / `native_stack 5` left on the
stack, so it is computed at runtime and **cannot** be resolved statically. The
two calls sit at Y = 65 and Y = 85, a 20-pixel line step, which is consistent
with two stacked lines of text.

This dialog is recorded as structurally identical but with **UNKNOWN** content,
and no text edge is emitted for it. Only the seven literal-operand dialogs get
a proven `dialog -> text` relation.

---

## Family 2: slot 139, `0x08002703`: condition selector, NOT presentation

Slot 139 is the most common **terminal** call (27 dialogs end with it), which
made it the strongest lifecycle candidate. It is not one.

```
0x08002706  ldr  r1,[r0,#0x28]
0x0800270A  ldr  r1,[r1,#0xC]      ; test a state field
0x0800271A  bl   0x08008AA0
```

`0x08008AA0` walks a table of entries and, for each, calls `0x08004784`, a
bitfield condition evaluator (it decodes a group/bit pair and tests it against
a flag block at `+0x50`), then pushes the entries that pass:

```
0x08008AD8  bl   0x8004784        ; evaluate condition
0x08008ADC  cmp  r0,#0
0x08008ADE  beq  <skip>           ; failed -> not offered
0x08008AF6  str  r0,[r1,#4]       ; passed -> appended to a list
```

**Classification: game-state-conditional selection.** It filters a set of
options by save/progress flags. It writes no UI structure, touches no font
routine, and reaches no text table.

**Rejected**: "slot 139 is the wait-for-input / dialog-close primitive." Its
call graph contains no input polling and no presentation object; it is a
predicate filter over a list. Naming it `wait_for_input` would have been
exactly the context-guessed opcode name the ticket forbids.

---

## Family 3: slots 48 and 83: construct/queue, not content

Slot 48 (`0x08000AFD`) is the most common **opening** call (34 dialogs):

```
0x08004766  ldrb r1,[r0,#1]
0x08004768  lsls r2,r1,#0x1E
0x0800476C  beq  <skip>
0x08004770  bics r1,r2          ; clear bit 1
0x0800477E  bl   0x8011C70       ; state transition
```

It clears a status bit and calls a state routine. No content source.

Slot 83 (`0x080015BB`) pops two values, allocates a 12-byte object with vtable
`0x0804DEC8`, transforms the second popped value through `0x080001C6` (an actor
/ handle resolver, with special cases for negative values, 0 and 9 reading
IWRAM globals `0x03001C34` and `0x03001BAC`), then calls `0x0801936A`.

`0x0801936A` is a **linked-list append**:

```
0x08019388  ldr  r2,[r2]
0x0801938A  adds r2,#4
0x0801938C  ldr  r3,[r2]
0x0801938E  cmp  r3,#0
0x08019390  bne  0x8019388      ; walk to tail
0x08019392  str  r1,[r2]        ; append
```

**Classification: queue insertion of a constructed object.** This is the same
*shape* as the `0x080030F8` construct-and-queue consumer TOOLKIT-019 found one
level up, and it corroborates that a dialog's normal mode of operation is to
build objects and enqueue them rather than to block.

It is **not** claimed to be the same queue: `0x080030F8` queues into
`0x03002A58` via `0x08012588`, while slot 83 appends through `0x0801936A`.
Those are different destinations and no identity between them is asserted.

---

## Lifecycle

Partially established, and deliberately not forced into a state machine.

What the code supports:

```
construct  ->  queue
```

Slot 178 constructs a text object and pushes the handle back onto the VM stack
(`0x08003068 -> 0x0801191A`, which appends to a VM-side array). Slot 83
constructs an object and appends it to a list. TOOLKIT-019's `0x080030F8`
constructs and queues. Three independent construct-then-queue paths.

What the code does **not** support, and is therefore not claimed:

- no `wait` stage was found, no investigated family polls input
- no `close` / teardown primitive was identified
- no evidence that dialog execution blocks

A type-0 dialog, as measured, **runs to completion**: every one of the 236 ends
in `terminate`, and the interpreter loop at `0x08004038` returns on a null
dispatch slot. Presentation objects outlive the script by being queued. That is
consistent with TOOLKIT-019's two consumers being construct-vs-run rather than
begin-vs-end of a blocking sequence, but "consistent with" is as far as the
evidence goes.

---

## Content-source classification

| Source | Status |
|---|---|
| Existing Buu UTF-16 text (`0x0806BCE8`) | **CONFIRMED_ROM** for slot 178 in 7 dialogs |
| Compressed text at `0x0879BF2C` | **NOT REACHED**: see below |
| Separate text corpus | Not observed |
| Generated/formatted content | Not observed |
| UI-only resource | Not observed |
| Graphics/portrait resource | Not observed (glyph tiles are produced from the font, not a portrait resource) |
| Audio resource | Not observed |
| Game-state-only behaviour | **CONFIRMED_ROM** for slots 139, 48 |
| Dialog 516 slot-178 content | **UNKNOWN** (runtime index) |

### The compressed-text region was not investigated

`0x0879BF2C` was left alone, per the ticket's condition. No investigated dialog
consumer reaches it or a decoder owning it: the one slot that reaches a text
store reaches `0x0806BCE8`, the already-verified UTF-16 table. The region
remains untouched and unclaimed.

---

## Rejected interpretations

| OLD CLAIM | NEW EVIDENCE | RESOLUTION |
|---|---|---|
| Dialogs cannot reach text, since none of the four map-reachable dialogs contains `0x0806BCE8` | The four reachable dialogs use slots 4, 55, 186, 187, 0, 100, 5, 138, 120, 29, 119, 107, 26, none is 178. The corpus-wide scan found slot 178 in a *different* 8 dialogs | **Superseded, not contradicted.** TOOLKIT-019's test was about those four dialogs and remains true of them. Text is reached by dialogs outside the map-reachable subset. |
| Slot 139 is the presentation/wait primitive because it terminates 27 dialogs | Its call graph is a bitfield-predicate filter over a list; no input poll, no UI write, no font routine | Rejected. Terminal position is not evidence of presentation. |
| Slot 83's queue is TOOLKIT-019's `0x03002A58` dialog queue | Slot 83 appends via `0x0801936A`; `0x080030F8` queues via `0x08012588` into `0x03002A58` | Rejected. Same shape, different destination; no identity claimed. |
| The map chain `map -> placement -> event -> dialog -> text` closes | The 7 text-bearing dialogs have 0 consuming events, placements and maps in the verified corpus | **Rejected.** See below. |

### The full map chain does NOT close

This is the ticket's preferred milestone and it is **not** achieved. Stated
plainly rather than papered over.

The verified operand-reference corpus reaches exactly four dialogs, 393, 506,
508 and 509, and none of them calls slot 178. The seven text-bearing dialogs
(290, 291, 292, 295, 296, 297, 298) have **no** verified consuming event,
placement or map.

So this ticket establishes:

```
dialog -> text                                    CONFIRMED_ROM
map -> placement -> event -> dialog               CONFIRMED (TOOLKIT-018/019)
map -> placement -> event -> dialog -> text       NOT ESTABLISHED
```

The two halves are each proven; they do not currently meet, because no single
dialog is known to be in both sets. Composing them anyway would assert an
ownership edge that no code supports. The reverse traversal below is therefore
`text -> dialogs` only, and stops there rather than fabricating the rest.

---

## Reverse consumers

Provable today:

```
text 1525 -> dialog 290
text 1526 -> dialog 291
text 1527 -> dialog 292
text 1529 -> dialog 295
text 1530 -> dialog 296
text 1531 -> dialog 297
text 1532 -> dialog 298
```

This coexists with, and is kept distinct from, TOOLKIT-014's `item -> text`
consumers. Both reach `0x0806BCE8`; they are separate provenance paths and are
not merged.

---

## Preserved refutations and findings

TOOLKIT-018's `event -> text` refutation **stands untouched**. That refutation
concerned three specific *map-event* consumer families whose operands were
candidate text ids; all three were traced to their consumers and refuted. None
of those families is slot 178, and none of the three is revisited here.

The distinction that matters: TOOLKIT-018 refuted *event operands* being text
ids. This ticket proves a *dialog operand* is a text id, through a different
opcode, a different native slot, a different handler and a different call
graph, verified by reaching the text table's own established consumer shape.

Also preserved unchanged:

- `388..397` are runtime arguments, not text ids
- save flags 266 / 267, SET only (slot 29 was re-observed at the top of the
  breadth ranking and its semantics were not re-opened)
- TOOLKIT-014 does not establish generic script-operand -> text
- `0x0800421F` is a handler, not a factory tag
- operand identity resolves by physical position, not decoded value
- 31/31 dispatch handlers match `_BUU_HANDLERS`; no second VM
- 236 type-0 ROUND_TRIP, 10,263 code bytes, 286 refused

## Runtime evidence

**None used.** Runtime escalation was authorised for one final semantic link,
and no such link remained: the content source, its encoding, its consumer and
its on-screen output are all resolved statically from ROM bytes. No emulator
was launched, and no CONFIRMED_RUNTIME claim is made anywhere in this document.

## Capability boundary

| Layer | Status |
|---|---|
| Type-0 dialog corpus census (opcodes, natives) | **CONFIRMED_ROM**, deterministic |
| Slot 178 -> text table `0x0806BCE8` | **CONFIRMED_ROM** |
| Slot 178 text encoding is UTF-16LE NUL-terminated | **CONFIRMED_ROM** |
| Slot 178 output is OAM sprite text, centred on X | **CONFIRMED_ROM** |
| `dialog -> text` for 7 dialogs with literal operands | **CONFIRMED_ROM** |
| `text -> dialog` reverse traversal | **CONFIRMED_ROM** |
| Slots 139, 48, 83 semantics | **CONFIRMED_ROM** (structural) |
| Dialog lifecycle: construct -> queue | **CONFIRMED_ROM** |
| Dialog lifecycle: wait / close | **UNKNOWN**: not found, not claimed |
| Dialog 516 text content | **UNKNOWN** (runtime index) |
| `map -> placement -> event -> dialog -> text` | **NOT ESTABLISHED** |
| Compressed text `0x0879BF2C` | **UNTOUCHED** |
| Type-4 and the other 286 records | **UNSUPPORTED** (unchanged) |
| Semantic WRITE / AUTHOR_NEW / growth | **ABSENT** |
