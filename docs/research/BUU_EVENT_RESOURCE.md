# Buu's Fury event-resource records

Measured against canonical `buus_fury_usa_rev0_01c1707f`, sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

TOOLKIT-018 proved that map-scene event operands select entries of table
`0x0879B704` and stopped there, with the records' internals UNKNOWN. This
document opens the records.

## Headline

The records are **scripts for the VM the toolkit already models**, and the
engine calls them **dialogs**.

Both names come from the shipped image, not from interpretation. Consumer
`0x0800327E` reaches `0x08004098`, which fails an assertion carrying two
developer-left strings:

- `"Expected dialog to start with a code block"` (UTF-16, `0x0805553C`)
- `T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp` (ASCII, `0x08004160`),
  line `0x3C` = 60

So "dialog", "code block" and "ByteCodeInterpreter" are Webfoot's own
vocabulary for this subsystem. That is a naming fact, **not** a gameplay
finding: what a dialog does on screen remains UNKNOWN, and this ticket claims
nothing about it.

## Table and pool boundaries

| Item | Value |
|---|---|
| Table base | `0x0879B704` |
| Pointer count | 522 |
| Table extent | `0x0879B704 .. 0x0879BF2C` (2,088 bytes) |
| Pool | `0x0877C5A4 .. 0x0879B704` |
| Pool size | 127,328 bytes |

Verified: the 522 **table** pointers are strictly ascending, all land inside
the pool, and the records tile it exhaustively with no gap or overlap. (The
*dialog* pointer stored inside each record is a separate thing; see the
census.) The pool ends exactly
where the table begins, the signature of every verified Buu table here.

`0x0879BF2C` is independently recorded by Data Crystal as the start of a
separate compressed-text region. That is corroboration only; the canonical
measurement stays primary.

## Record census

Record `i` spans `ptr[i] .. ptr[i+1]`; the last spans `ptr[521] .. 0x0879B704`.

- min 16, max 3,168, median 100 bytes
- 166 distinct sizes, all a multiple of 4
- 521 of 522 records begin with a pointer **into the pool**; record 0's first
  word (`0x0877C510`) resolves to a valid ROM offset that sits just *below*
  the pool, so it is reported as it measures rather than hidden

**No fixed record format exists.** Two candidate whole-corpus schemas were
tested and both failed, and neither is claimed:

| OLD CLAIM | NEW EVIDENCE | RESOLUTION |
|---|---|---|
| Record is a pointer run followed by a count word equal to `n-1` | Holds for only 190 of 522 records | Rejected. It was a coincidence of the four reachable records. |
| Record is a pointer run terminated by a NULL word | Holds for only 463 of 522 records | Rejected. Close, but a rule that fails 59 times is not a rule. |

Only the first word is a corpus-wide structural fact, because it is the only
field the consumer actually reads before branching.

## Consumer contracts

Both consumers pop their table index **last**, so it is the value pushed
**first**. Read from the handlers, never assumed from operand position.

### `0x080030F8`: native slot 182, pops 2

```
pop1 -> [0x03001030] -> object +0x00
pop2 -> table index; r0 = ptr[index]
        bl 0x08012588 (r0 = record pointer, r1 = runtime object)
```

`0x08012588` is a generic constructor: it allocates 8 bytes, stores vtable
`0x08049D18`, and queues into `0x03002A58`. The same routine is called from
`0x0800424F`. It is a shared constructor, not a dialog interpreter, and it
carries no text-table literal.

### `0x0800327E`: native slot 216, pops 3

```
pop1 -> [0x03001030] -> object +0x04
pop2 -> [0x03001030] -> object +0x00
pop3 -> table index; r1 = ptr[index]
        r0 = sp (0x6C scratch), r2 = runtime object
        bl 0x08004098
```

This is the discriminator. The two consumers **do not** share a downstream
worker: `0x080030F8` constructs and queues an object, while `0x0800327E` runs
the record immediately through `0x08004098`. Same record, different operation.

### `0x08004098`: the dialog entry point

```
if r0 == 0: r4 = alloc(0x6C)      ; dialog-runner object
r0 = [r6]                          ; dereference the record's +0x00
r1 = ldrb [r0, #2]                 ; DIALOG TYPE
  type 0 -> bl 0x08004038(r4, r0 + 3, arg)      ; run code at dialog+0x03
  type 4 -> alloc(4 << 9 = 0x800)
            bl 0x08049120(dest, dialog + 4)      ; expand
            bl 0x08004038(r4, dest, arg)         ; run the expansion
            free
  else   -> assert "Expected dialog to start with a code block"
```

`+0x02` is therefore the one record field this ticket promotes: it is read by
code and branched on. Everything else in a record stays opaque.

`0x08049120` is an ARM veneer to `0x03000040`, an IWRAM address. The expansion
routine is relocated at runtime, so **type 4 cannot be reproduced from ROM
bytes** and is declared unsupported rather than decoded on a guess.

### `0x08004038`: the interpreter loop

```
r1 = &cursor
op = ldrb [cursor]; cursor += 1
handler = [0x080554C0 + op * 4]
if handler == 0: return
call handler(state, &cursor)
repeat
```

The dispatch table at `0x080554C0` holds **31 handlers, indices 0..30 with 17
absent**, and index 31 onward is the assertion string, which bounds the table.
Those 31 addresses are byte-for-byte the `_BUU_HANDLERS` tuple already in
`tools/webfoot/data/script_specs.py`.

**This is the same VM.** Opcode 1 decodes a big-endian signed-magnitude varint
with a continuation bit and the sign in bit 0 (`stack_be16_buu_v1`'s `sm7`),
and opcode 2 indexes native table `0x08055098`, the profile's existing
`native_table`. No new VM was invented for dialogs.

## Dialog type distribution

| Type | Records | Status |
|---|---|---|
| 0 | 236 | Supported; code block at dialog+0x03 |
| 4 | 141 | Real, engine-handled; expansion lives in IWRAM, unsupported |
| 5 | 139 | Hits the engine's own assertion; unsupported |
| 3, 6, 7 | 2 each | Unsupported |

## Code-block extent

The extent is walked, never searched. Every reachable path is followed one
instruction at a time from `dialog+0x03`, and the block ends at the furthest
byte any path reaches.

A first-terminate rule is **wrong**, and record 393 proves it: its
`branch_if_zero` at +4 targets +9, jumping over a terminate at +7. Stopping at
the first terminate would cut a 12-byte block to 8 and silently lose real code.

Unreachable-but-exact bytes are tolerated in a dialog, unlike in the map-scene
corpus, precisely because of that branch-over pattern. Exact re-encode remains
the guarantee: a byte that did not re-encode still fails.

## The four reachable records

| ID | Slot | Record | End | Size | Type | Code | Bytes | Instrs |
|---|---|---|---|---|---|---|---|---|
| `event_resource:0393` | `0x0879BD28` | `0x08792270` | `0x087922A0` | 48 | 0 | `0x0879221B` | 12 | 6 |
| `event_resource:0506` | `0x0879BEEC` | `0x0879A6C0` | `0x0879A6F8` | 56 | 0 | `0x0879A697` | 38 | 17 |
| `event_resource:0508` | `0x0879BEF4` | `0x0879AA0C` | `0x0879AD44` | 824 | 0 | `0x0879A703` | 56 | 20 |
| `event_resource:0509` | `0x0879BEF8` | `0x0879AD44` | `0x0879AD9C` | 88 | 0 | `0x0879AA3B` | 54 | 20 |

All four are type 0, all four decode and re-encode exactly. Consumers are
unchanged from TOOLKIT-018: 15 references, 15 events, 4 maps (19, 21, 22, 325),
47 consuming placements.

Note that a record's own bytes and its dialog's bytes are **different regions**.
Record 508 spans 824 bytes but its code block sits at `0x0879A703`, outside the
record entirely. The record holds a pointer array; identity is the table index,
never the address.

## Capability boundary

| Layer | Status |
|---|---|
| Table `0x0879B704`, whole-resource census | **READ**: 522 entries, ascending, exact bounded tiling |
| Record extents | DECODE (exact, gap-free) |
| Record `+0x00` pointer | CONFIRMED (consumer dereferences it) |
| Dialog `+0x02` type | CONFIRMED (consumer branches on it) |
| **236 type-0 dialog records** | **ROUND_TRIP**: 236/236 exact, 10,263 code bytes, existing Buu VM |
| **286 non-type-0 records** | **STRUCTURALLY CLASSIFIED / UNSUPPORTED BY CODEC**: type byte observed, explicitly refused, never silently passed through |
| Type-4 expansion | UNSUPPORTED (routine relocated to IWRAM) |
| Remaining record bytes | OPAQUE |
| Dialog player-visible meaning | UNKNOWN |
| Semantic WRITE / AUTHOR_NEW / growth | ABSENT |

The table is **READ**, not ROUND_TRIP. Only the 236 type-0 dialog records
round-trip. Nothing here may be read as "522 dialogs ROUND_TRIP" or
"event_resource table ROUND_TRIP"; establishing that would take a later ticket
actually supporting the remaining 286.

**All 236** type-0 records decode and re-encode exactly, covering 10,263 code
bytes. An earlier draft of this work reported 231 with 5 refusals; that was a
defect in a hand-rolled instruction walker, not a property of the data.

| OLD CLAIM | NEW EVIDENCE | RESOLUTION |
|---|---|---|
| 5 type-0 records cannot be decoded | Those 5 were mis-walked by a private copy of the operand-width and branch rules, which got `count_back`'s sign backwards | Rejected. The walker now calls `decode_instruction`, the VM's own decoder, and all 236 round-trip. Duplicating VM rules was the bug. |

## Rejected interpretations

- **Fixed record format**: rejected, see the census table above.
- **Common downstream worker**: rejected. `0x080030F8` and `0x0800327E` diverge
  immediately into `0x08012588` and `0x08004098` respectively.
- **event → text**: NOT reopened. TOOLKIT-018 refuted it for the map-scene
  families and this ticket does not disturb that. A dialog is a script for the
  already-modelled VM, so it could only reach text through a proven text
  consumer; none of the four reachable dialogs even contains the text-table base
  `0x0806BCE8`, and a test pins that. A future `event_resource → text` relation
  would need a resource field proven to reach the verified text pointer table
  through a text consumer. That would be a **new relation**, not a reversal.
- **Gameplay naming**: not attempted. "Dialog" is the engine's structural term
  for the record, taken from its own assertion string. It is not a claim that
  these drive on-screen conversation.

## Preserved corrections

- `388..397` are runtime arguments, not text ids
- 266/267 are save-flag indices, SET only
- TOOLKIT-014 does not establish generic script-operand → text
- `0x0800421F` is a handler, not a factory tag
- operand identity resolves by physical position, not decoded value

## Addendum 2026-09-21 - type-4 packed payload recovery, and corpus completeness

Source: HUMAN-4-USAGE-CLOSURE-001 (recorded by HUMAN-4-RESEARCH-CAPTURE-001).
Read-only static work on the canonical image; no runtime capture, no code change.

### The failure was the acceptance rule, not the data

Ten type-4 records sat outside every decode performed before that ticket:
`event_resource` **0, 171, 185, 193, 199, 208, 239, 256, 347, 450**. They are valid
**headerless Webfoot bitstreams beginning at `dialog + 0x04`**. The earlier rule
demanded a size whose decode round-tripped as a VM script with **no** opaque byte
and a packed end inside the record; these blocks legitimately contain
unreachable-but-exact bytes, which this page already tolerates for a dialog (the
branch-over-terminate precedent at `event_resource:0393` above). Refusing them was
a property of the rule, not of the bytes.

### Accepted bounded recovery rule

`_unpack_stream` raises when a stream terminates before the requested size, so the
**natural decoded length is the maximal valid decode boundary** - the largest size
that still decodes. Control: `event_resource:0342` peaks at exactly **103**, the
length the strict rule independently established, so the two rules agree on a block
they can both read. Applying the natural-length rule to the ten:

| `event_resource` | natural size | packed end | opaque bytes | round-trip |
|---|---|---|---|---|
| 0 | 46 | `0x77C538` | 3 | exact |
| 171 | 96 | `0x7852B0` | 1 | exact |
| 185 | 253 | `0x7857E0` | 20 | exact |
| 193 | 78 | `0x786688` | 5 | exact |
| 199 | 107 | `0x786A00` | 6 | exact |
| 208 | 50 | `0x786EB0` | 2 | exact |
| 239 | 82 | `0x78A4DC` | 3 | exact |
| 256 | 63 | `0x78A730` | 3 | exact |
| 347 | 185 | `0x790F30` | 12 | exact |
| 450 | 196 | `0x7938F0` | 1 | exact |

**All ten recovered, all round-trip.** Their native-slot vocabulary matches the
accepted corpus (the slot 27/28 dialog and flag primitives, 43, 48, 55, 77, 93,
113, 114, 120, 127, 146, 149, 186); **none of the ten contains an actor-spawn site
(native slot 53) and none contains the literal `101`**. The remaining 145 records
(139 type 5, 2 each of types 3, 6, 7) yield **no** recoverable bitstream at any size
4..2048 or literal width 1..8, so the script-bearing corpus is now **complete:
377 / 377 decoded** (236 type-0 + 141 type-4).

### Scope of this result

Measured for the **522-record event-resource population only**. It is not
generalised to other script families (their own pages hold their own counts) and it
does not decode `0x08049120`, the runtime expansion routine this page already
records. The engine-side statement above is unchanged: the runtime path reaches
`0x08049120`, an ARM veneer to IWRAM `0x03000040`, and that routine was not
disassembled here.

The decoder identity is therefore **INFERRED**, carried by three independent
cross-checks rather than by the expansion routine: (1) the maximal-length rule
yields one unique boundary per record and agrees with the strict rule on the
control; (2) type-4 `event_resource:0293` decodes to `push_many(3, 1528, 120, ..)`
→ `"Match 5 Fight!"`, continuing the 1525..1532 series whose other members are
type-0 and already CONFIRMED in TOOLKIT-020 - a check that could have failed; and
(3) the actor-spawn operand invariant (first pushed value ≤ 305 or a party slot
1..5, the other two being coordinates up to 600) reproduces independently across
**201 type-4 spawn sites**, exactly as in the 25 type-0 sites.

**Capability boundary, refined not overturned.** "Type 4 is UNSUPPORTED" above
remains true of the *runtime expansion*; what changes is that the packed payload
**is present in ROM and reads**, with the project's existing headerless bitstream
grammar, to a byte-exact round-tripping VM instruction stream. Nothing here
authorises a type-4 WRITE, and no gameplay meaning is claimed.
