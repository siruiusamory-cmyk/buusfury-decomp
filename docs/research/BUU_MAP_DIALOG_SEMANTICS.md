# Buu map-reachable dialog semantics (TOOLKIT-021)

Baseline `e41ac22c82874f1b0a16e2ab97a290225773bdd8`. Static evidence only; no runtime escalation was performed,
and none was needed to classify the behavior below.

## Result, stated first

**The four map-reachable dialogs are save-state and scene-control logic. They
do not present text, and they do not reach another dialog.**

This is TOOLKIT-021 **Outcome B**. The preferred Outcome A -
`map -> placement -> event -> dialog -> text` - **does not close**, and the
multi-hop route through a second dialog that section 7 of the ticket asked
about **does not exist either**. Both are reported as measured negatives, not
as open questions.

```
map -> placement -> event -> dialog      SUPPORTED  (TOOLKIT-018/019)
dialog -> text                           SUPPORTED  (TOOLKIT-020, slot-178 subset)
map-reachable dialog -> text             REFUTED    (this ticket, measured)
map-reachable dialog -> dialog           REFUTED    (this ticket, measured)
map-reachable dialog -> save_flag        CONFIRMED_ROM (this ticket)
```

## 1. The frozen corpus

Four records, all dialog type 0, all exact round-trip. Identities are table
indices, never addresses - a record's bytes and its dialog's code are different
regions (TOOLKIT-019).

| Dialog | Record offset | Size | Dialog offset | Type | Code offset | Code | Instrs | Events | Placements | Maps |
|---|---|---|---|---|---|---|---|---|---|---|
| `event_resource:0393` | 7,938,672 | 48 | 7,938,584 | 0 | 0x79221B | 12 | 6 | 3 | 7 | `map:0325` |
| `event_resource:0506` | 7,972,544 | 56 | 7,972,500 | 0 | 0x79A697 | 38 | 17 | 2 | 30 | `map:0021`, `map:0022` |
| `event_resource:0508` | 7,973,388 | 824 | 7,972,608 | 0 | 0x79A703 | 56 | 20 | 5 | 5 | `map:0019` |
| `event_resource:0509` | 7,974,212 | 88 | 7,973,432 | 0 | 0x79AA3B | 54 | 20 | 5 | 5 | `map:0019` |

Totals reconcile with the preserved TOOLKIT-018/019 counts: **15 dialog
references, 4 distinct dialog records, 15 events, 4 maps, 47 consuming
placements**, plus the 2 save-flag references (266, 267) for a 17-reference
event corpus.

Dialogs 508 and 509 are near-identical programs differing only in operands;
they share `map:0019` and split its placements 5/5.

## 2. Instruction traces

Decoded by the toolkit's own VM (`stack_be16_buu_v1`), not re-derived.

**Read the opcodes correctly**: opcode `0` is `push_byte`, **not** a native
call. Native calls are only opcode `2` (`native_stack`) and opcode `3`
(`native_pop`), with the slot in `operands[0]`. Treating opcode 0 as a call
inflates the slot census with values that are really pushed constants.

### `event_resource:0393` - 6 instructions

```
  +0  native_stack     4          ; push context word
  +2  native_stack     55         ; push mapped object
  +4  branch_if_zero   -> +9
  +7  terminate
  +9  push_byte        2
 +11  terminate
```

The `branch_if_zero` at +4 targets +9, jumping **over** the terminate at +7 -
the case that proved a first-terminate extent rule wrong in TOOLKIT-019. The
terminate at +7 is reached only by fall-through that never happens, so the
disassembler marks it opaque and exact re-encode is the guarantee.

### `event_resource:0506` - 17 instructions

```
  +0  push_many        (2, 284, 3)     ; base 284, count 3
  +5  native_stack     186             ; TEST_FLAG_RANGE  -> packed mask
  +7  push_byte        1
  +9  subtract
 +10  native_pop       0
 +12  push_many        (2, 284, 3)     ; base 284, count 3
 +17  native_stack     0               ; push context word (mask source)
 +19  native_stack     187             ; WRITE_FLAG_RANGE (SET/CLEAR per bit)
 +21  native_stack     0
 +23  push_byte        0
 +25  equal
 +26  branch_if_zero   -> +37
 +29  native_stack     4
 +31  native_stack     100             ; construct + queue
 +33  native_stack     5
 +35  native_stack     138
 +37  terminate
```

### `event_resource:0508` - 20 instructions

```
  +0  push_byte        30
  +2  native_stack     120
  +4  native_stack     4
  +6  native_stack     29              ; save-flag SET (single)
  +8  native_stack     4
 +10  push_signed_magnitude 388
 +13  subtract
 +14  native_pop       4
 +16  push_many        (2, 287, 3)     ; base 287, count 3
 +21  native_stack     4
 +23  native_stack     187             ; WRITE_FLAG_RANGE
 +25  push_many        (5, 0, 55, 0, 369, 158)
 +34  native_stack     119             ; transition/spawn with coord pair
 +36  push_many        (3, 240, 183, 500)
 +44  native_stack     107             ; construct + queue
 +46  push_byte        75
 +48  native_stack     26              ; fixed-point scale
 +50  branch_if_zero   -> +55
 +53  push_byte        5
 +55  terminate
```

### `event_resource:0509` - 20 instructions

Same program shape as 508. Differences are operands only:
`push_signed_magnitude 393` (vs 388), `push_many(5, 0, 52, 0, 87, 47)` (vs
`(5, 0, 55, 0, 369, 158)`) and `push_many(3, 80, 60, 500)` (vs
`(3, 240, 183, 500)`).

## 3. Native-slot census

Thirteen distinct slots across the four dialogs. Handler addresses are
`native_table 0x08055098 + 4 * slot`, Thumb bit cleared.

| Slot | Handler | Uses | Dialogs | Classification | Status |
|---|---|---|---|---|---|
| 0 | `0x08000206` | 3 | 506 | push word from `[0x03001058]` | context getter |
| 4 | `0x0800026E` | 10 | all four | push word from `[[0x03001030]]` | context getter |
| 5 | `0x0800028A` | 1 | 506 | push word from `[[0x03001030]+4]` | context getter |
| 26 | `0x08000738` | 2 | 508, 509 | multiply by `0x00028F5D`, `asr #8`, `0x0803FADE` | fixed-point scale |
| 29 | `0x080007E6` | 2 | 508, 509 | save-flag **SET**, single bit | **proven, TOOLKIT-018** |
| 55 | `0x08000C4E` | 1 | 393 | guarded object lookup via `0x08011CCA` | structural |
| 100 | `0x08001C1C` | 1 | 506 | construct + queue | **family 2** |
| 107 | `0x08001E6E` | 2 | 508, 509 | construct + queue | **family 2** |
| 119 | `0x08002390` | 2 | 508, 509 | transition/spawn, coord pair | **family 3** |
| 120 | `0x08002404` | 2 | 508, 509 | `0x08050714` then `0x0803D8A0` | structural |
| 138 | `0x080026EA` | 1 | 506 | pops 1 into `0x08009172` | structural |
| 186 | `0x080032C2` | 1 | 506 | save-flag **TEST range** | **family 1** |
| 187 | `0x08003310` | 3 | 506, 508, 509 | save-flag **SET/CLEAR range** | **family 1** |

**Slot 178 is absent.** So is every slot TOOLKIT-018 refuted.

## 4. The central negative, and the control that makes it trustworthy

Section 7 of the ticket asks the strongest question first: does any
map-reachable dialog reach another dialog, or reach slot 178 indirectly?

Every one of the 13 slots was walked as a **whole call graph** - not a single
path - following every `BL` and inspecting every PC-relative literal, to
**depth 10**. Slot 119 alone expands to 70 distinct nodes.

**No slot reaches text table `0x0806BCE8`. No slot reaches dialog table
`0x0879B704`.** The result is unchanged at depths 4, 6, 8 and 10.

A negative is only worth as much as the instrument that produced it, so the
same walker was pointed at the three known positives:

| Control | Expected | Measured path |
|---|---|---|
| slot 178 | text table | `0x08003030 -> 0x0802BFBC -> literal@0x0802C06C` |
| slot 182 | dialog table | `0x080030F8 -> literal@0x080031C0` |
| slot 216 | dialog table | `0x0800327E -> literal@0x08003444` |

All three reproduce exactly, reusing the repo's own
`tools/webfoot/analysis/thumb.py` helpers (`scan_bl`, `ldr_literal_address`,
`is_pop_with_pc`) rather than a second BL decoder that could drift. The
instrument finds the links that exist; it reports none here because there are
none.

## 5. Family 1 - save flags: TEST, SET and CLEAR resolved

Three primitives share one bit-addressing shape and differ **only** in the
bitwise operation. That is what classifies them, rather than any naming guess:

```
byte  = saveobj + 0x50 + 5 + (bit >> 3)
mask  = 1 << (bit & 7)

0x08004364   ands  ->  TEST   (returns 1/0)
0x08004380   orrs  ->  SET
0x08004396   bics  ->  CLEAR
```

The save object is `[0x08054FBC + 0x14]` in every caller.

- **Slot 29** pops one bit index and calls SET. This is TOOLKIT-018's already
  proven result, and it re-derives identically here. It is the control for
  this family.
- **Slot 186 = TEST_FLAG_RANGE.** Pops 2. `r7` (top) is the **count**, the
  second pop is the **base**. Loops `i < count` calling TEST on `base + i` and
  packs each result into a bitmask (`movs r0,#1` / `lsls r0,r4` / `orrs r6,r0`),
  then pushes the packed mask.
- **Slot 187 = WRITE_FLAG_RANGE.** Pops 3 (mask, count, base). Loops
  `i < count`; per bit it tests the mask's low bit (`lsls r2,r4,#0x1f` / `beq`)
  and calls **SET** `0x08004380` when 1, **CLEAR** `0x08004396` when 0, then
  `asrs r4,#1`.

Pop order was read from the handler, never inferred from operand position -
the discipline TOOLKIT-018 established.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION

**OLD CLAIM** (`placement_contracts.py`): "`0x08004396` is the matching clear;
unreached by this corpus, so only SET is claimed."

**NEW EVIDENCE**: slot 187, reached by dialogs 506, 508 and 509, calls
`0x08004396` directly at `0x08003358`.

**RESOLUTION**: CLEAR is now reached, through the **range** consumer rather
than a single-bit one. `save_flag consumers {29: 'set'}` describes the *event*
corpus and stays correct for it; the dialog corpus adds slots 186 (test) and
187 (set/clear). The two are recorded separately rather than merged, because
they were proven by different consumers.

### Flag operands

The flag indices the four dialogs act on come from `push_many`, resolved with
the pop order above:

| Dialog | Slot | Base | Count | Flags | Operation |
|---|---|---|---|---|---|
| 506 | 186 | 284 | 3 | 284, 285, 286 | TEST -> mask |
| 506 | 187 | 284 | 3 | 284, 285, 286 | SET/CLEAR per bit |
| 508 | 187 | 287 | 3 | 287, 288, 289 | SET/CLEAR per bit |
| 509 | 187 | 287 | 3 | 287, 288, 289 | SET/CLEAR per bit |

Individual gameplay meanings of flags 284-289 remain **UNKNOWN**. They are
distinct from the event-level flags 266/267, which are unchanged.

## 6. Family 2 - construct and queue (slots 100, 107)

Both allocate through `0x0803D5B8`, install a vtable, and append to a list by
the tail walk `0x0801936A`.

- **Slot 100**: allocates `0xC`, installs vtable literal `0x0804DEB4`, writes
  `1` at `+8`, appends to the queue head `[0x08054FBC + 0x1C]`.
- **Slot 107**: pops 3, builds through `0x08021174`, appends to the same
  `[0x08054FBC + 0x1C]`.

This is the same **shape** as TOOLKIT-019's `0x080030F8` and TOOLKIT-020's
slot 83, but a **different destination**. No identity is claimed between them,
and the scheduler behind the queue was not reverse-engineered - the ticket
scopes that out and nothing here needed it.

## 7. Family 3 - slot 119, the dominant call in 508 and 509

`0x08002390`, 116 bytes, 70-node call graph. It pops **five**, which matches
`push_many(5, ...)` in both dialogs exactly.

```
pops 5: top two stored as HALFWORDS to sp+0xe and sp+0xc  (an X/Y pair,
        passed on as r3 = sp+0xc, a pointer to the pair)
        remaining three into r4, r5, r6

if [0x03001C34] non-null:
        load its vtable, call the method at vtable+0x28 through the
        __call_via veneer 0x08046AA4          ; releases the current object

store 1 to [0x03002A58]                       ; the same state word
                                              ; TOOLKIT-019 observed at 0x08012588

call 0x08008D44 with r0=[0x08054FBC+0xC], r1=r6, r2=r5,
                     r3=sp+0xc (the coord pair), stack args r4 and 0
```

Worker `0x08008D44` writes two bytes into the object, allocates via
`0x0803D5B8`, builds vtable-bearing objects and pushes them through
`0x08021094` and `0x0801191A`.

Structural name: **transition/spawn with a coordinate pair**. It is *not*
promoted to a gameplay verb. The coordinate-pair operands in 508
(`0, 55, 0, 369, 158`) and 509 (`0, 52, 0, 87, 47`) are consistent with
per-placement positioning, but position semantics are not proven statically
and no runtime observation was taken.

## 8. Behavior summaries

Only proven edges are included.

```
event_resource:0393:
  push context (slot 4), push mapped object (slot 55)
  -> branch_if_zero over the fall-through terminate
  -> terminate
  No flag, resource or presentation effect proven.

event_resource:0506:
  TEST flags 284..286 (slot 186)          -> packed mask
  -> arithmetic, native_pop 0
  -> WRITE flags 284..286 (slot 187)       SET or CLEAR per mask bit
  -> if the compared value is zero, terminate
     else construct+queue (slot 100) and slots 5/138
  -> terminate

event_resource:0508:
  SET single save flag (slot 29)
  -> WRITE flags 287..289 (slot 187)
  -> transition/spawn with coord pair (slot 119, operands 0,55,0,369,158)
  -> construct+queue (slot 107, operands 240,183,500)
  -> fixed-point scale (slot 26)
  -> terminate

event_resource:0509:
  identical structure to 0508; operands differ
  (magnitude 393; coord pair 0,52,0,87,47; queue 80,60,500)
```

## 9. Rejected interpretations

| Rejected | Why |
|---|---|
| The four dialogs render text | No slot in the four reaches `0x0806BCE8` at any depth to 10, while the same walker finds it for slot 178 |
| A map-reachable dialog invokes another dialog | No slot in the four reaches `0x0879B704` at any depth to 10, while the same walker finds it for slots 182 and 216 |
| Slot 119 is a dialog-close or wait primitive | It reaches no font routine, no text table and polls no input; it releases one object and calls a spawn worker with a coordinate pair |
| Slot 186/187 operands are text ids | They index the save bitfield through the proven TEST/SET/CLEAR primitives; the TOOLKIT-018 mistake is not repeated |
| Flags 284-289 have known gameplay meaning | Nothing proves it. The operation is proven; the meaning is not |
| Opcode 0 is a native call | Opcode 0 is `push_byte`; only opcodes 2 and 3 dispatch natively |

## 10. Preserved results

TOOLKIT-018's refutation of event -> text stands, and is untouched: it
concerned three map-scene **event** consumer families, none of them slots 186,
187 or 119. TOOLKIT-020's slot-178 text chain stands. The non-overlap between
the four map-reachable dialogs and the seven text-bearing dialogs stands, and
this ticket **strengthens** it: previously the four merely did not contain the
text base, and now their entire call graph is known not to reach it.

TOOLKIT-020's refutation of slot 139 as `wait_for_input` is not revived by
context; slot 139 does not appear in this corpus at all.

## 11. Remaining UNKNOWNs

- Gameplay meaning of save flags 284-289.
- What the queue at `[0x08054FBC + 0x1C]` eventually executes.
- Whether slot 119's coordinate pair is a screen position, a map position or a
  spawn origin.
- Slot 138's effect beyond its single pop into `0x08009172`.
- The non-type-0 subtypes stay unopened: section 10's escalation condition was
  never met, because no map-reachable dialog invokes any other dialog record.
