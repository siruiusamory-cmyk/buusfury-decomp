# The third region's population path (DECOMP-LIFT-COLLECTION-INSERT3-001)

**Status:** lifted and validated. The third region's shape is proven, and **the
population path does not exist in the reachable code** - a result that is stated
plainly rather than papered over.
**Target:** `sub_0801157E` at `0x0801157E`, Thumb.
**Baseline:** `e9f92202478f893ced638f7bbde8fb77af03c80d`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. The third region's exact layout

Proven from `sub_0801157E`'s **own instructions**, not from spacing:

| Property | Value | Evidence |
| --- | --- | --- |
| count offset | **`object + 0x208`** | `movs r0,#0x41` / `lsls r0,r0,#3` / `adds r5,r4,r0`, then `ldr r4,[r5]` |
| element array | **`object + 0x20C + 4*i`** | `ldr r0,[r0,#4]` after indexing from `r5` |
| count width | 32 bits | a word load and a word store |
| element width | **32 bits** | `lsls r0,r4,#2` scaling |
| element type | **pointer to a virtual object** | `ldr r1,[r0]` then `ldr r2,[r1,#0x14]` |
| traversal | **BACKWARD**, `count-1` down to `0` | decrement then `bpl` |
| method slot | **`table + 0x14`** | `ldr r2,[r1,#0x14]` |

**The offset is never a literal and never an immediate displacement** - it is built
from a shift pair every time. That single fact defeats any displacement-based search
and is why the earlier tickets' region was invisible to one.

**The method slot is +0x14, which is NOT shared** with the first collection's
destructor (+0x04), the second's (+0x04), or the reader's search predicate (+0x24).
So the slot belongs to this region's identity.

Note the layout is the same shape as the other two if the base is taken as
`object + 0x204` (count at base+4, elements at base+8).

---

## 2. The selected routine

| | |
| --- | --- |
| Range | `0x0801157E..0x080115B0` |
| Size | **50 bytes**, **23 instructions** |
| Terminator | one, at `0x080115AE` |
| Literal | `0x08072824` |
| Callees | `sub_0803DA62`, and the `bx r1` thunk for the element method |
| Callers | **one**: `0x0802E88C` in `sub_0802E83C` |

```
for i = third.count-1 DOWN TO 0:
    third.elements[i]->table[+0x14](third.elements[i])
third.count = 0
```

**It is a DRAIN, not a population path.** It never writes an element and never
increments a count. `sub_08011732` contains the **identical** drain-and-zero inline,
so this is a routine concept rather than incidental cleanup.

---

## 3. The population path does not exist - the negative proof

Four independent searches, all reproducible as tests:

1. **No immediate displacement access.** No instruction in the reachable code
   accesses the region by a displacement; the address is always computed.
2. **EIGHT sites build the constant `0x208`**, found by scanning **every byte of the
   image** for the `movs`/`lsls` pair in all its register forms and all its
   decompositions - not just the reachable set. **Exactly three** are in the
   collection cluster and use it as `object + 0x208`: this routine (`0x0801158A`),
   `sub_08011732` (`0x080117CA`) and `sub_08011B04` (`0x08011B7A`). **All three write
   ZERO to the count and none writes an element.** The other five - `0x080344CC`,
   `0x08034A6A`, `0x0804843E`, `0x0804E9AE`, `0x08054492` - are in unrelated routines
   using the same numeric offset for other structures, and **none of the eight
   performs the append shape**.

   *An earlier revision of this document claimed only three routines compute `0x208`.
   That was wrong; the test written to pin it is what caught it.*
3. **No stored pointer to the region exists.** Searching the whole image for the
   words `0x03001E50` (`object+0x204`), `0x03001E54` (`object+0x208`) and
   `0x03001E58` (`object+0x20C`) finds **zero occurrences**. So no code can reach the
   region through a pointer either, and the generic append could not be aimed at it.
4. `sub_08011B04` **bulk-fills the array** at `object + 0x20C`, and CALLS THE
   IWRAM-INSTALLED ROUTINE AT `0x030007A8`. **This item was WRONG when this
   document was written and is corrected here** (see section 8). It claimed the
   trampoline "jumps to whatever is stored at `0x030007A8`", which would make the
   argument order unresolvable. The instruction is `ldr pc,[pc,#-4]`: the stub's
   own literal IS the destination, `0x030007A8`, and that address is filled by
   the reset code's DMA3 with a verbatim copy of ROM `0x087B79A4..0x087B89A8`.
   The call is a WORD FILL - `r0` destination, `r1` a 32-bit value replicated and
   never masked, `r2` size in bytes - and it is fully statically resolvable.

**Consequence:** the count is zero on every readable path, which makes the drain
**defensive and normally a no-op**. The bulk fills DO write the element slots, but
with sentinel values (`0x03002A4C` over the first three arrays, `0x03001C44` over
the fourth) rather than with appended elements, so no element is ever readable.

### What `sub_08011B04` is
A **reset/destructor**, not a populator. It calls `table[+4]` destructors on the first
and second collections and `table[+8]` on a fourth collection at `object + 0x610`,
bulk-fills arrays, and then zeroes the counts at `+4`, `+0x208`, `+0x40C` and `+0x610`
in one run of four stores. `sub_0802E83C` calls it, then `sub_080115B0`, then the
drain - a teardown sequence.

---

## 4. Relationship to the verdict-driven scan

`sub_08011732`'s inline block and this routine are the same operation. Because the
count is only ever written as zero, that block does nothing in practice - so the
"third collection is flushed" transition recorded in the previous ticket is real but
**normally vacuous**. Its presence implies the code's author expected the count to be
non-zero at some point, and RESOLVED 2026-09-29 by `DECOMP-RUNTIME-IWRAM-001`: the
bulk fill does not close that gap either, because it writes the element slots with
sentinel WORDS and the counts are zeroed immediately afterwards by the same routine.

---

## 5. Comparison

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 50 | 84 |
| Differing bytes in the overlap | - | 44 |
| Spans byte-identical | - | 0 |

`is_a_match_claim` is false. **SEMANTIC PROVEN** (16 assertions),
**MODERN_BUILD PASS**, **ADS_MATCH BLOCKED**.

---

## 6. Answers to the ticket's questions

| Question | Answer |
| --- | --- |
| duplicate handling | **not applicable** - nothing inserts |
| capacity checks | **none** |
| overflow behaviour | **not applicable** to this routine |
| cross-collection transition | **none**: it does not touch the first or second collection |
| `+0x00` | **not touched BY THIS ROUTINE**. Corrected 2026-09-29: `sub_08011B04` DOES write `+0x00 = 0` and `+0x01 = 1` as bytes at `0x08011C02`/`0x08011C06`, so the earlier wording "untouched by every routine lifted so far" was true only of the routines lifted BEFORE it. |
| why `sub_08011732` flushes it | because it is a shared drain concept; the count is zero on every readable path, so the flush is defensive |
| verdicts 1/2 | **not advanced** by this routine - it calls only `table+0x14` |
| capacity | **no evidence** of any limit |

## 7. Recommended next subsystem ticket

**RAN.** Item 1 below became `DECOMP-RUNTIME-IWRAM-001`; its result is
[`LIFT_IWRAM_RUNTIME.md`](LIFT_IWRAM_RUNTIME.md). The slot at `0x030007A8` is the
first word of a block FILL at ROM `0x087B814C`, installed by the reset code's DMA3.

1. ~~**Resolve the IWRAM-installed callee at `0x030007A8`**~~ - **DONE**. It was not
   a function pointer at all: the trampoline jumps straight to `0x030007A8`.
2. **What `table+0x14` means** for these elements.
3. **The fourth region at `object + 0x610`**, zeroed in the same reset and never
   examined - its layout is now proven contiguous (`count +0x610`, array
   `+0x614..+0x694`, 32 slots) but its USE is still open.
4. **`sub_0804FE54`** - does it compact?
5. **The object's `+0x00` field**: written `0` and `+0x01` written `1` by
   `sub_08011B04` (corrected above); what the pair means is still open.

---

## 8. Correction carried by `DECOMP-RUNTIME-IWRAM-001` (2026-09-29)

Section 3 item 4, section 4 and section 6's `+0x00` row stated things that later
evidence refutes. All three are corrected in place above, and the correction also
changed the committed `config/lift_collectionflush3.json` (its `target.notes` field)
and `src/ByteCodeInterpreter_collectionflush3.c`'s comment. Nothing else in that
report moved: only `/target/notes` differs from the previous revision. This was a
deliberate deviation from "existing reports stay byte-identical", taken because the
artifact asserted something false and the evidence is the veneer's own instruction.

What was wrong:

| Claim | Status | Evidence |
| --- | --- | --- |
| the trampoline at `0x0804912C` "jumps to whatever is stored at `0x030007A8`" | **REFUTED** | `0xE51FF004` is `ldr pc,[pc,#-4]`; it loads the stub's own literal into PC, so `0x030007A8` is the destination |
| the call's argument order is "NOT statically resolvable" | **REFUTED** | the destination resolves to ROM `0x087B814C`, a word fill: `r0` dest, `r1` value, `r2` bytes |
| whether the bulk fill writes elements "is NOT established" | **RESOLVED** | it writes the sentinel WORDS `0x03002A4C` / `0x03001C44` into the slots, then the routine zeroes all four counts |
| `object + 0x00` is untouched | **REFUTED for this routine** | `0x08011C02 strb r0,[r4]` sets it to 0 and `0x08011C06 strb r0,[r4,#1]` sets `+0x01` to 1 |
