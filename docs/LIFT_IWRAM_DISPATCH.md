# The IWRAM block's dispatch and IRQ architecture

Ticket: DECOMP-IWRAM-DISPATCH-001. Baseline `b3097339dd0399d1730004a87f94147d198d2522`.

This document records what the 4100-byte block's entry, dispatch and interrupt
architecture is, and what is still unknown. It is the second half of the picture
[`LIFT_IWRAM_RUNTIME.md`](LIFT_IWRAM_RUNTIME.md) starts: that document established
that the block exists, where it comes from and how the ROM reaches the four
block-memory routines. This one answers how the ROM reaches *everything else* in
the block, what the interrupt dispatcher does, and what the internal callgraph
looks like.

[`LIFT_IWRAM_TRANSFORMS.md`](LIFT_IWRAM_TRANSFORMS.md) is the third pass over the
same block. It lifts the byte-lane and Q10 families this document ranked first
and second, and it **corrects one row of the family table below**: the third
member of the "fixed point" family does not carry the idiom that family was keyed
on, so the table now splits Q10 from Q18.14. No count in this document changes.

Every number here is regenerated on demand by
`tools/buusfury/lift.py`'s `derive_iwram_dispatch` and carried, whole, inside
`config/lift_iwramdispatch.json`. Nothing in it is hand-written prose that could
drift from the image.

## 1. The address mapping

Unchanged from the previous ticket and restated only because everything below
depends on it. The reset routine programs DMA3 with SAD `0x087B79A4`, DAD
`0x03000000` and CNT `0x84000401`, so:

    IWRAM X = ROM 0x087B79A4 + (X - 0x03000000)

and the block is `0x03000000..0x03001004`. The code half ends at `0x03000F44`;
`0x03000F44..0x03001004` is a 192-byte data tail.

## 2. There are sixteen ways in, not thirteen

The veneer family carries thirteen of them. The other three are **stored
pointers**, and each is a plain literal-pool word in ordinary ROM code:

| ROM slot | value | read at | installed into |
|---|---|---|---|
| `0x0803E36C` | `0x03000868` | `0x0803E0F2` | a sound-channel record, `+0x18` |
| `0x0803F3BC` | `0x03000AE0` | `0x0803F21A` | **IRQ vector slot 10**, `0x03000FD8` |
| `0x0803F434` | `0x03000B6C` | `0x0803F3DA` | **the BIOS IRQ vector pointer**, `0x03007FFC` |

Each of the three ROM words occurs exactly once in the whole 8 MiB image at every
alignment, and nothing else in the image names those IWRAM addresses.

The census that finds them has to be run at **every 2-byte-aligned offset**. A
4-byte-aligned sweep gives 129 distinct values over 257 windows; the same image
gives 225 over 533 at two-byte alignment. The 96 extra values all occur at odd
offsets only. The previous report's `words_naming_the_block_anywhere_in_it`
section stated the aligned figure and did not say it was a lower bound; that is
corrected here and in that report.

Storing an address is not the same as being an entry, so the derivation asks the
question that decides it: **does an instruction load it?** Readers inside the game
code half count; readers above `0x08060000` are in the asset half, where four bytes
spell a plausible IWRAM address by chance. Filtering the 32 values that have *any*
reader by that boundary leaves 17 in the code half - the thirteen veneer
destinations, the three stored pointers, and one more that is a data reference, not
an entry: `0x08043CC8` holds `0x030000F0` and real code at `0x0804391E` byte-compares
the ROM multiboot signature at `0x087B7734` against the block's own code half and
sums 90 halfwords from `0x03000000`. That routine treats the block as **data**; it
is a multiboot self-check that cannot be live in a cartridge build, and whether it
is ever called is UNKNOWN.

Nine further values have readers and lie in the block's own data tail
(`0x03000F4C`, `0x03000F50`, `0x03000F60`, `0x03000F78`, `0x03000F90`, `0x03000FB0`,
`0x03000FF0`, `0x03000FFC`, `0x03001000`). They are data slots the ROM code
dereferences, not entries. `0x03000F90` is the most-referenced address in the block.

## 3. The five functions with no caller inside the block, and the two that nothing reaches

A recursive descent from the sixteen entries reaches **904 words**. The words it
does not reach are exactly:

* the two complete functions `0x03000330..0x03000388` and `0x03000414..0x030004C0`,
  both `push`..`bx lr`, both internally well formed;
* the dispatcher's Thumb interworking halfword at `0x03000C98`;
* literal-pool words the walk never executes.

The ticket's premise that all five callerless functions are reached through the
three stored pointers is **refuted for two of them**. `0x03000330`'s address occurs
**zero times in the whole image at any byte offset**, and `0x03000414`'s occurs once,
at `0x082E4264`, inside asset data with no reader. No BL reaches either; no
literal-pool slot in the reached set names either; the block's one computed jump
(`add pc, pc, r3, lsl #2` at `0x030007FC`) cannot leave its own function; all four
indirect transfers in the block are resolved (`bx lr`, the dispatcher's `bx r0`,
`0x03000AE0`'s `bx r1` = `0x0803F297`, and the two `bxne r4` returns). The
conclusion is **INFERRED dead code**: two complete routines the linker kept and
nothing references. The one route that would be invisible to every sweep here is a
pointer built at runtime out of two registers, and only PC sampling could settle it.

The 904-word reachable set is two words larger than an
entry-only walk gives, because this derivation follows `add rD, pc, #imm` as a code
successor. Those two words are the dispatcher's own return path
(`0x03000C7C..0x03000C84`), which is reachable only through the Thumb halfword.

## 4. The second dispatch path is an installation protocol, not one API

The three stored pointers are not three variants of one interface:

* `0x03000868` is a **callback field**. The reader at `0x0803E0F2` picks it in one
  arm of a two-way select and stores it at `r0+0x18` of a 64-byte sound-channel
  record; the other arm stores the Thumb no-op `0x0803E0B5`. It is invoked as
  `ldr r3,[r4,#0x18]; bl 0x08046AA6`, and `0x08046AA6` is the two-halfword
  `bx r3` thumb-call thunk.
* `0x03000AE0` is an **interrupt callback**: it is written into vector slot 10 at
  `0x0803F220` while the same routine enables `REG_IE` bit 10.
* `0x03000B6C` is an **exception entry**, installed into the BIOS vector.

What groups them is one link unit - one 4100-byte DMA3-copied image - not one
calling convention. Their register contracts differ accordingly: `0x03000868` takes
`r0` = channel record, `r1` = mix buffer, `r2` = word count plus mode bits and
returns through `lr`; `0x03000AE0` takes `r0`/`r3` state and **returns through `r4`**,
never touching `lr`; `0x03000B6C` is entered by the hardware.

## 5. The IRQ dispatcher

`0x03000B6C`, ARM, 75 instructions, `0x087B8510..0x087B863C` in ROM.

```
read REG_IE (0x04000200) as one 32-bit word  -> (IF << 16) | IE
read REG_IME (0x04000208) as a halfword
push spsr, IME, IE|IF, 0x04000200, r4, r5, lr
REG_IME = 1
r1 = IE & IF
scan r1 in a FIXED PRIORITY ORDER (below); r4 = the chosen vector byte offset
  if nothing is pending, jump to the restore path
clear the served bit in IE's half, set it in IF's half, ONE 32-bit store   <- BEFORE the handler
OR the served mask into a 16-bit software word at 0x03000FE8
switch to system mode (ip = 0x9F for the first test, 0x1F for every later one)
lr = 0x03000C99 (ODD), r4 = 0x03000C7C, r0 = vector_table[offset/4]
bx r0
  ... handler returns in Thumb state into the halfword 0x4720 at 0x03000C98,
      which is `bx r4`, landing back at 0x03000C7C
restore CPSR, pop everything back, REG_IE = the saved value, REG_IME = the saved value,
msr spsr_fsxc, bx lr
```

**The priority order is all fourteen GBA interrupt bits**, not a subset:
bit 10, 7, 6, 0, 1, 2, 3, 4, 5, 8, 9, 11, 12, 13. Reading those masks requires the
ARM immediate rotation: `ands r0, r1, #64, #28` is `ror(0x40, 28) = 0x400`, i.e.
**bit 10** - and capstone prints the two halves as two operands, so a derivation
that reads the last operand gets 28 and reports bit 4. This exact mistake was made
in this ticket's own brief and corrected against the encoding.

Three asymmetries are reproduced rather than repaired:

* The first test (bit 10) settles on the `orr` and therefore **skips the IE clear**;
  every other test enters at the `bic`. That is the only difference between the
  first test and the rest, and it is the reason `ip` is `0x9F` for that test alone.
* The last test (bit 13) is a `beq` to the exit, so its *settled* path is the
  fallthrough - which is a `b` to its own address. **A pending bit 13 spins forever**,
  and the slot its offset would select is never entered. Thirteen of the fourteen
  tests can reach a slot.
* Bit 12 and bit 13 share the byte offset `0x30`, so the final slot is unreachable
  even by offset arithmetic.

### The vector table

Fourteen 32-bit words at IWRAM `0x03000FB0`. The extent is proved from what follows
it rather than from a round number: the dispatcher reads a halfword at
`base + 0x38`, so the table ends exactly where that word begins.

In the ROM **every entry is `0x0803F3D9`** - the Thumb stub whose entire body is
`bx lr` at `0x0803F3D8`. The routine at `0x0803F3DA` is a *different* function that
merely follows the stub.

The table is **populated at run time**, and finding that requires a two-step
derivation, because the base is never a literal in the installing code: ROM
`0x0803F218` loads the *data word* `0x087B6EDC`, the data word holds `0x03000FB0`,
and the next instruction dereferences the register. The derivation finds every
instruction that loads the address of a word holding the table base, follows the
register through one dereference, and reports every store through it. It finds, among
others, `0x0803F220` writing `0x03000AE0` into **slot 10** at `0x03000FD8` - and
slot 10 is exactly the slot the priority chain selects for bit 10, which is exactly
the bit that same routine enables in `REG_IE`. The two halves of the install agree.

### The software pending word is a producer/consumer semaphore

`0x03000FE8`, immediately after the table, receives `OR served_mask` **before the
handler runs**. Its consumer is a ROM routine, not part of the block: the waiter
`0x0803F3F4` takes the table base in `r0` and an awaited mask in `r1`, and

```
0x0803F420  strh r0, [r4, #0x38]   ; clear the pending word
0x0803F422  svc  #2                ; halt until an interrupt
0x0803F426  ldrsh r0, [r4, r2]     ; the dispatcher has ORed the served mask in
0x0803F428  ands r0, r5            ; is anything we are waiting for set?
0x0803F42A  beq  0x0803F422        ; no: halt again
0x0803F42E  bics r0, r5            ; yes: consume those bits
0x0803F430  strh r0, [r4, #0x38]
```

So it is a **bitmap the dispatcher produces and a waiter consumes**, not a nest
counter: nothing increments it, the waiter clears it before waiting and bics the
bits it consumed afterwards. An earlier revision of this document called its
purpose UNKNOWN; the consumer was simply outside the block being analysed.

The waiter also writes `0x03000FEC` (`+0x3C`), once with a constant `100` at
`0x0803F406` and otherwise with a value computed from `VCOUNT` at `0x0803F41C`,
so that word is a scanline-derived timing value rather than part of the vector
table. The waiter has five callers, all passing `0x03000FB0` in `r0`.

### The bit-13 hang is armed at run time

The install routine sets `REG_IE = 0x2000`, which is **exactly bit 13** - the one
bit whose settled path is the self-branch - and its caller then ORs in bit 0
(VBlank), leaving `REG_IE = 0x2001`. So the latent hang is not dead configuration:
a pending Game Pak interrupt would spin the machine with `IME` already set to 1.
This is recorded, not repaired.

### The install path

`0x03007FFC`, the BIOS IRQ vector pointer, is stored by the 26-byte Thumb routine at
ROM `0x0803F3DA`:

```
ldr r0, [pc, #0x58]   -> 0x03000B6C
ldr r1, [pc, #0x58]   -> 0x03007FC0
str r0, [r1, #0x3c]   -> 0x03007FC0 + 0x3C = 0x03007FFC
ldr r0, [pc, #0x58]   -> 0x04000200
REG_IE = 0x2000 ; REG_IME = 1 ; REG_DISPSTAT = 0x18
```

**The literal `0x03007FFC` occurs zero times in the whole image.** A literal search
for the BIOS vector therefore finds nothing and concludes the vector is never
installed; the address is computed. This is the single most reusable fact in the
ticket.

### The routine that does it is reached by a call, not by a pointer

The same trap has a second half. The installer's own address is named by **no
stored word anywhere in the image** - the 4-byte value `0x0803F3DA` occurs zero
times at every alignment - so a pointer search reports that the installer is never
called either. It is called: `0x0803D7CC` is a Thumb `bl 0x0803F3DA`, through the
system-init path that also loads the IWRAM system-pointer table at `0x087B5B80`,
writes handler `0x0803D785` into vector slot 0, calls `0x0803F1B8` (which installs
`0x03000AE0` into slot 10 and enables `REG_IE` bit 10), and enables interrupts.

A Thumb `bl` is a 32-bit instruction, so it has to be decoded as a **pair**.
Decoding one halfword at a time reports the whole instruction as undecodable and
loses the edge - which is the likeliest reason an independent sweep of this image
concluded the installer was unreachable. The subsystem is **live**: the BIOS IRQ
vector is written, the vector table is populated, and the dispatcher runs.

## 6. The internal callgraph

Sixteen functions are reachable from the sixteen entries, ranging from 4 to 169
instructions. Every function is a leaf or calls exactly one thing; the graph is
acyclic; no function has more than one caller; and no word is reached from two
different starts. There are no tail branches between functions and no
cross-function fallthrough. Two functions end through a register other than `lr`
(both `bxne r4`, in `0x03000AE0`), and one ends in a tail branch (`bx r1`).

The block is **not purely assembly with no literal pools**: nine pool words sit
inside the code half. Two of the entries have their main body and their epilogue
separated by an embedded helper, so extents come from the walk and never from
"next entry minus this entry".

### Families

Classified from each function's own instructions, not from names:

| family | members | mechanical reason |
|---|---|---|
| IRQ / IO | `0x03000B6C`, `0x03000000` | read or write `0x04000200`/`0x04000208`; `0x03000000` is the reset routine's own entry |
| IRQ-handler protocol | `0x03000AE0` | `mrs`/`bic #0x80`/`msr cpsr_c`, two `bxne r4` returns, tail branch to Thumb `0x0803F296` |
| dispatch | `0x030007FC`, `0x03000B6C`, `0x03000AE0` | a register- or table-indexed branch |
| block memory | `0x03000768`, `0x030007A8`, `0x030007FC`, `0x03000858` | already lifted as `src/IwramBlock.c` |
| bit-stream | `0x03000040`, `0x03000CA0` (+ two byte-identical helpers) | bit-cursor refill loops; both share the thresholds `0x37FF`/`0x027F` |
| byte-lane transforms | `0x030002DC`, `0x03000330` | `0xff` masks and repeated `ands`; **LIFTED** by DECOMP-IWRAM-TRANSFORMS-001 as `iwrambl` and `iwramblsparse` |
| fixed point, Q10 | `0x03000560`, `0x03000700` | `smull`/`smlal` plus the `lsr #10` / `lsl #22` reduction; **LIFTED** by DECOMP-IWRAM-TRANSFORMS-001 as `iwramqf` |
| fixed point, Q18.14 | `0x03000868` | `mla` + `ldrsb`, `lsl #18`/`asr #14`, 64-bit `adds`/`adc` position accumulation; **no** `smull`/`smlal` at all. The "fixed point" grouping is right and a "Q10" reading of this member is not: see `LIFT_IWRAM_TRANSFORMS.md` section 5 |
| clamp / pack | `0x03000A4C` | signed-byte clamp and two-byte packing, destructively zeroing its source |
| strided gather | `0x03000388`, `0x03000414`, `0x030004C0` | `mla` addressing with a pitch taken from the context record |
| graphics / DMA | **empty** | no resolved effective address lands in `0x040000B0..0xDF` or `0x06000000`, and no pool word holds one |

The graphics/DMA family being empty is a **measured negative**, not an omission.

**The fixed-point row above was one row in this ticket's classification and is two
families.** The third member has none of the two instructions the classification
was keyed on, so the table now splits it out. The correction is a change to this
table and not to any measurement this document carries: every count in sections 2
to 6 below is unchanged and was re-derived when the split was made.

## 7. What this ticket lifted

`iwramdispatch`, unit `iwram_dispatch_tu`, ARM, `src/IwramDispatch.c`: the
dispatcher itself, `0x087B8510..0x087B863C`, plus its single literal at
`0x087B8640`.

The unit's boundary needs one extra rule that every other unit does not: the
return path is reachable only through the handler's Thumb trampoline, so the walk
follows `add rD, pc, #imm` as a code successor. That rule is opt-in per unit
(`pc_add_successors`), because in a Thumb unit the same idiom almost always points
at a literal. With it, the walk covers all 75 instructions with no gap and ends
exactly at the Thumb halfword.

**Three things are not expressible in C** and are modelled as environment calls
rather than omitted: the SPSR read and write, the CPSR mode switch, and the
ARM-to-Thumb-to-ARM return. Everything memory-visible - which bit is acknowledged,
in what order, which slot is called, what is pushed and restored, and the infinite
spin on bit 13 - is reconstructed exactly. No guard the original lacks was added.

## 8. Corrections this ticket made to existing claims

Each is a factual error found by measurement, not a rewording.

1. **"the 16-bit reading ... leaves eight of the thirteen veneer destinations
   outside the copied block"** was wrong in three places
   (`docs/LIFT_IWRAM_RUNTIME.md`, `docs/ROM_MAP_PROVENANCE.md`, and the generator's
   own docstring and report field). The measured count is **three**:
   `0x03000858`, `0x03000A4C`, `0x03000CA0`. The report now **derives** the count
   from the destination list instead of restating it.
2. **"Eight of the thirteen destination addresses - including all four
   block-memory slots - occur exactly once"** was self-contradictory: `0x030007FC`
   occurs twice (`0x0804914C`, its own veneer literal, and `0x0830E231`) and is
   listed in the same sentence among the five that do not. The count of eight is
   correct; "all four" is now "three of the four".
3. **"every four-byte-aligned offset ... This finds LITERALS only"** understated
   its own scope. The 2-byte-aligned census gives 225 values over 533 windows
   against 129 over 257, so the aligned figure is a lower bound. The report now
   says so and gives both numbers.
4. **The priority-order list** in this ticket's own brief (bit 14, 7, 6, ..., 18, 19)
   was wrong: the real masks are bits 0-13. The masks are now decoded from the
   instruction words with the rotation applied, so the claim can be re-checked
   mechanically.
5. **"13 in-block veneer destinations"** is right, but "the entry set is thirteen"
   is not: it is sixteen.

## 9. Unknown

* The identity of whatever reaches `0x03000330` and `0x03000414`, if anything does.
  Still open after `LIFT_IWRAM_TRANSFORMS.md`: both are reported as INFERRED
  DEAD/UNREACHABLE, and `0x03000330`'s address occurs zero times in the image.
* The meaning of the 256-byte table at `0x0805672C` that `0x030002DC` indexes.
* The consumer of the software pending word `0x03000FE8`.
* The purpose of the guard-adjacent spin on bit 13 - whether it is a deliberate
  park or a defect in the original.
* The LZ bit format behind the `0x37FF`/`0x027F` thresholds.
* The plane/rectangle convention of the strided gathers.
* What the IWRAM object at `0x03003898` is, which `0x03000AE0` reads.
* Whether the multiboot self-check at `0x0804391C` is ever called.

## 10. The next subsystem-sized batch

Ranked by evidence per byte, from the callgraph rather than from adjacency. Items
1 and 2 were **taken** by DECOMP-IWRAM-TRANSFORMS-001, and the note under each
says what that ticket found; the ranking below is left as it stood so the two
documents can be read against each other.

1. **The byte-lane transforms**, `0x030002DC` (76 bytes, all arguments in registers,
   no callees, no pool) and then `0x03000330` (88 bytes, reference-free, so lifting
   is its only route to a contract). Both are exhaustively testable on the host.
   *DONE: lifted as `iwrambl` and `iwramblsparse`. The 76 is confirmed and the
   entry-to-next-entry reading of 84 is refuted; `0x03000330` remains INFERRED
   DEAD; the two are variants of one transform, not an inverse pair, and
   `0x030002DC`'s table is a single 256-byte ROM map at `0x0805672C`.*
2. **The Q10 fixed-point family**, `0x03000700` first (104 bytes, nine
   `smull`/`smlal` and an unambiguous `lsr #10`/`lsl #22` idiom), which pins the
   idiom that `0x03000560` and `0x03000868` repeat.
   *DONE for the first two, lifted as `iwramqf`. `0x03000868` does NOT repeat the
   idiom - it has zero `smull`/`smlal` and zero `lsr #10`/`lsl #22` - so it is not
   Q10 and is the recommended next batch instead.*
3. **The two orphan functions**, which are complete and well formed and whose only
   blocker is the unresolved question of whether anything calls them.
4. **`0x03000868`** (484 bytes, 21 `mla`, 22 `ldrsb`, Q18.14), the largest
   pool-free leaf in the block and the only function in it with a 64-bit adder
   and no 64-bit multiplier.
5. **`0x03000A4C`** (148 bytes, 6 callers), whose eight shift sites sum to 38
   rather than 32 and whose first reading is therefore undecided.
6. **The strided gather family** `0x03000388`, `0x030004C0`, `0x03000414`
   (472 bytes), whose contract lives in an uncharacterised context record.
