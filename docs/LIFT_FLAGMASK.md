# The first consumer of the gathered mask (DECOMP-LIFT-FLAGMASK-001)

**Status:** the mask's first concrete use is proven. The chain now runs from a
script byte all the way to a **write back into the flag array**.
**Target:** `sub_08003310` at `0x08003310`, Thumb, native dispatch entry 187.
**Baseline:** `fc72c09377cc2eb9d05ee584825a087104b3f55f`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | the per-bit set/clear, both clamps, the width-32 case and the width-0 skip, checked by RUNNING them: 22 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | it compiles, links at `0x08003310` and emits bytes: 144 bytes |
| **ADS_MATCH** | **BLOCKED** | `ADS12_LICENSE_UNAVAILABLE` |

No match is claimed.

---

## 2. How it was found, and why it is the one

It begins **exactly where the gather ends**: the gather's extent is
`0x080032C2..0x08003310` and this is `0x08003310..0x08003366`. A routine that
starts where the producer stops, and which **pops** rather than pushes a
stack-only transform, is the first consumer by construction.

It is **native dispatch entry 187** (table word `0x08003311`), with **no BL caller
anywhere**, so it is reached by VM dispatch.

---

## 3. The routine

| | |
| --- | --- |
| Extent | `0x08003310..0x08003366` |
| Size | **86 bytes** |
| Instructions | **41** |
| Terminator | one, at `0x08003364` |
| Callees | **`sub_08004380` (SET)** and **`sub_08004396` (CLEAR)**, both already lifted |
| Literal | one, `0x08054FBC` |

```
0x08003312  ldr r1,[r0] ; subs r1,#1 ; str r1,[r0] ; ... ldr r4,[r2,#4]   POP -> MASK
0x0800331E  ... ldr r6,[r2,#4]                                            POP -> WIDTH
0x08003328  ... ldr r7,[r0,#4]                                            POP -> OFFSET
0x08003332  cmp r4,#0 ; bge   mask < 0 (SIGNED)  ->  mask = 0
0x08003338  movs r0,#1 ; lsls r0,r6
0x0800333C  cmp r0,r4 ; bgt   (1 << width) > mask -> keep
0x08003340  subs r4,r0,#1     else  mask = (1 << width) - 1
0x08003342  loop i = 0 .. width-1:
0x0800334A      adds r1,r7,r5          r1 = offset + i
0x0800334C      lsls r2,r4,#0x1f       mask bit 0 into bit 31
0x08003350      beq  clear             bit 0 clear -> CLEAR(base, offset+i)
0x08003352      bl   0x08004380        bit 0 set   -> SET(base, offset+i)
0x08003358      bl   0x08004396
0x0800335C      asrs r4,r4,#1          mask >>= 1
0x08003364  pop {r3-r7, pc}
```

---

## 4. Stack behaviour

| Property | Proven |
| --- | --- |
| pop or peek | **three pops** |
| order | **mask** (the stack top), then **width**, then **bit offset** |
| pushes | **none** |
| counter | moves by exactly **−3** |
| mask written back to the stack | **no** |
| ordering | **all three pops complete before the first flag is touched**; the offset is added to the loop index immediately before each call |

The three pop sites are found in the instruction stream at `0x0800331C`,
`0x08003326`, `0x08003330`.

---

## 5. Mask interpretation, and the consequence

The mask is **not compared, not stored, and not merely tested**. It is **applied
per bit**:

```
for i = 0 .. width-1:
    if mask bit i is SET  ->  SET   the flag at (offset + i)
    else                  ->  CLEAR the flag at (offset + i)
```

**EACH BIT OF THE MASK BECOMES THE STATE OF THE CORRESPONDING FLAG.** The bit
under test is always mask bit 0, because `lsls r2, r4, #0x1f` moves it into bit 31
for the `beq`, and `asrs r4, r4, #1` then brings the next bit down.

So `sub_08003310` is the **exact counterpart of the gather**: where the gather
reads a run of flag bits into a mask, this writes a mask into a run of flag bits.
Together they are a save/restore pair, and this is the first concrete engine
consequence of the gathered mask.

### Two clamps, both signed

1. a mask that is **negative when read as signed** is replaced by `0` entirely;
2. a mask where `(1 << width)` is **not greater** is truncated to `(1 << width) - 1`.

### Width 32 is a real edge case, reproduced not corrected

**ARM `LSL` by a register yields ZERO for an amount of 32 or more.** So at a width
of 32 the width clamp computes `0 - 1`, which is `0xFFFFFFFF` **even for a mask of
0**; `asrs` then keeps it all ones, so **all 32 flags are SET**.

**The Thumb shift is modelled explicitly** (`flagmask_thumb_lsls_1`) rather than
left to C: `1u << 32` is *undefined* in C, and MSVC on x86 masks the amount to five
bits and yields `1` - the exact opposite of the machine. Leaving it to the
language would have made the host test disagree with the ROM.

A width of **zero or less is skipped entirely** by the `ble`, though the three
values are still consumed.

---

## 6. The carried-over discrepancy, now discharged

While building the width-32 case this ticket established that the **gather loop's
shift explanation was wrong**: it claimed the Thumb `lsls` amount was taken
*modulo 32*, whereas ARM `LSL` by a register yields **zero** for an amount of 32 or
more, and its reconstruction left `1u << n` undefined in C for `n >= 32`.

This ticket could not fix it, because its regression requirement was that all
twelve earlier reports regenerate byte-identically, and correcting the gather
changes that report.

**It was fixed by the immediately following ticket,
`DECOMP-FLAGSTATE-SHIFT-FIX-001`**, which owns that report change: the gather now
models the architectural rule in an explicit helper, its report carries
`shift_is_register_controlled` and `shift_amount_at_or_above_32_yields_zero` in
place of the removed `shift_amount_is_modulo_32`, and its self-check covers shift
amounts 0, 1, 31, 32, 33 and 255 directly.

---

## 7. The comparison

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 86 | 144 |
| Differing bytes in the overlap | - | 77 |
| Instruction spans keyed on the original's boundaries | 41 | - |
| Spans byte-identical | - | 1 |
| Calls / literals | 2 / 1 | 2 / 1 |

`is_a_match_claim` is false. Both callees are bound to their original addresses
`0x08004380` and `0x08004396`.

---

## 8. Proven, and unresolved

### Proven

Everything in sections 3 to 5: the extent and its contiguity with the gather, the
dispatch entry, the three pops in order with no push, the absence of any
write-back to the stack, the per-bit application, both signed clamps, the
width-32 overflow and the width-0 skip; a sweep over all sixteen single-bit masks
and a multi-bit mask; the ordering.

### Unresolved

- **what any flag means.** No semantic name is assigned to the mask, the flags, the
  array or the object, and nothing is imported from another title;
- **the array's size**; there is no bounds check here either, so a large offset or
  width writes wherever the index arithmetic points;
- whether the mask applied here is the one the gather produced at any given
  runtime moment. The **contiguity and the stack discipline** make it the first
  consumer, but data flow through the dispatch loop is not traced dynamically.

---

## 9. Limits

1. **One consumer**, followed one step.
2. **`ADS_MATCH` remains BLOCKED.**
3. **The gather's shift defect is recorded, not fixed**, for the reason in
   section 6.

---

## 10. Recommended next subsystem batch

1. **Fix the gather's shift model** (section 6). It is a small, well-understood
   correction to one helper and one report field, and it removes a known-wrong
   explanation from the tree.
2. **The size of the flag array.** Neither the accessors, the gather nor this
   routine bounds it, so finding an allocation or a bounded reader would settle
   whether the unbounded offsets are reachable.
3. **The other consumers of the mask's producer.** The gather's result is a plain
   stack value, so any handler may pop it; the arithmetic family is the obvious
   place to look for a mask combined with a constant.
4. **Native slot 178 at `0x08003030`.**
