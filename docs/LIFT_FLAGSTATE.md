# DECOMP-LIFT-FLAGSTATE-001 - the first decompiled flag-state cluster

**Status:** the accessor trio is complete, the gather loop is proven, and the
array is bounded honestly.
**Functions lifted:** `sub_08004396` (clear) and `sub_080032C2` (gather), Thumb.
**Baseline:** `20a3b1bb3e9494e32a26d9c0650dc868476a54cf`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. The accessor trio, complete

| Member | Entry | Extent | Size | Instructions | Combining instruction |
| --- | --- | --- | --- | --- | --- |
| test | `0x08004364` | `0x08004364..0x08004380` | 28 B | 14 | `ands` |
| set | `0x08004380` | `0x08004380..0x08004396` | 22 B | 10 | `orrs` |
| **clear** | `0x08004396` | `0x08004396..0x080043AC` | 22 B | 11 | **`bics`** |

The three **tile contiguously** `0x08004364..0x080043AC`, so their boundaries
confirm one another. The clearer was **derived on its own evidence**: the single
instruction that decides its behaviour is `bics`, where the setter has `orrs`.

### The shared contract, from all three routines' own instructions

| Property | Value |
| --- | --- |
| byte index | `value >> 3`, **arithmetic** shift |
| bit index | `value & 7` (the `lsls`/`lsrs #0x1d` pair) |
| object offset | `+0x50` |
| field offset | `+5`, so storage begins at **`base + 0x55`** |
| entry size | 1 byte |
| read-modify-write | the test's is a read only; set and clear are read-modify-write |
| bounds check | **none in any of the three** |

### The clearer
`bics` computes `byte & ~(1 << (value & 7))`, a **bit clear**, so the other seven
bits of that byte survive. Exactly **one byte** is modified. Clearing an
already-clear bit is a no-op, and clearing a bit twice equals clearing it once.

**The return value is not defined.** The routine ends with `bx lr` with `r0` still
holding the computed field address, not a status or a boolean, so the
reconstruction returns `void` rather than inventing a result.

---

## 2. The gather loop: `sub_080032C2`

`0x080032C2..0x08003310`, **78 bytes, 38 instructions**, one terminator at
`0x0800330E`, one call to the already-lifted reader, one literal. No `BL` caller
targets it, so it is reached by VM dispatch; it is the function the `flagread`
report recorded as the reader's third call site `0x080032EE`.

### What it does

It is a **two-into-one reduction over the flag array** rather than over its two
operands:

1. **POP the bound** from the top;
2. **POP the bit offset** from beneath it;
3. for `n = 0 .. bound-1`, test the array bit at **`offset + n`** and set bit `n`
   of an accumulator when that flag is set;
4. **PUSH the mask** as a new stack value.

Net counter movement **-1**: two consumed, one produced. The result stays in the
VM.

### The detail that fixes the second operand's meaning

The value passed to the reader is **`offset + n`, not `n`** (`adds r1, r0, r4`).
The reader then splits it as `(offset+n) >> 3` and `(offset+n) & 7`, so successive
iterations test successive **bits**. The offset is therefore a **BIT NUMBER** in
the array, not a byte index and not a pointer.

### Loop bounds

| Bound | Behaviour |
| --- | --- |
| positive | gathers exactly that many bits |
| **zero or less** | skipped entirely by the `ble`, which compares the bound as **signed**; mask is `0` and the reader is **not called at all** |
| above 32 | **wraps.** The mask bit is built by a Thumb `lsls` on a 32-bit register, so the shift amount is taken modulo 32 and bits already set are re-set. The machine's behaviour, reproduced rather than corrected |

### The resulting mask and where it goes

```
bit n of the mask  ==  the flag array bit at (offset + n)
```

so the mask is the packed run of flags from the caller's offset, `bound` bits
wide. Its **destination is the VM stack itself**: the routine increments the
counter and stores the mask at `values[count]`, so **the mask becomes the new
stack top**, to be consumed by whatever pops it next. The mask does not leave the
VM here, and that is as far as this ticket follows it.

### No bounds check, no NULL check, no size knowledge

Neither the offset nor the bound is compared against any size, and **the array
size is not reachable from this routine at all**: both are runtime values. No
guard was added.

---

## 3. Array extent: proven lower bound, no derivable upper bound

| | |
| --- | --- |
| **Proven lower bound** | **1 byte, 8 bits** |
| Evidence | the trio's index arithmetic addresses exactly one byte at `base + 0x55`, and the boolean transforms only ever produce indices 0 and 1, so **bits 0 and 1 of that byte are reachable and used** |
| **Upper bound** | **none derivable** |
| Reason | no instruction anywhere compares an index or an offset against a size, and the gather loop's offset and bound are runtime values |
| Classification | **bounded only below** |

This is reported as a bound pair rather than a guessed size: the honest answer is
that the code has no size knowledge to recover.

---

## 4. The comparison

| Target | Original | Modern | Differing bytes | Spans (identical/total) | Calls | Literals |
| --- | ---: | ---: | ---: | --- | --- | --- |
| clear | 22 B, 11 i | 36 B, 18 i | 20 | 1 / 10 | 0 / 0 | 0 / 0 |
| gather | 78 B, 38 i | 120 B, 59 i | 70 | 1 / 37 | 1 / 1 | 1 / 3 |

`is_a_match_claim` is false for both. The gather's reader call is bound to its
original address `0x08004364`. The modern literal count is not asserted equal for
the gather, for the reason established two tickets ago: GCC places its pool inside
the function body and decoding those words as code invents literal loads.

Verdicts remain independent for both targets: **SEMANTIC PROVEN**,
**MODERN_BUILD PASS**, **ADS_MATCH BLOCKED**.

---

## 5. Proven, and unresolved

### Proven

Everything in sections 1 to 4, plus: the trio tiles contiguously; the clearer is a
read-modify-write that touches one byte; the gather's call site is the one the
`flagread` report recorded from the other direction; the mask is `(1<<bound)-1`
when every gathered bit is set, for bound 1..32; a bound above 32 wraps.

### Unresolved

- **what any bit means.** No semantic name is assigned to the bits, the array, the
  object or the gathered mask, and nothing is imported from another title;
- **the array's size**, reported as a lower bound only;
- **what pops the mask** the gather pushes;
- whether the gather's offset is ever negative at runtime, though the code permits
  it.

---

## 6. Regression status

- **all ten earlier reports byte-identical** - `git diff` on their report files is
  empty;
- no `--defsym`, no ARM veneers, correct Thumb symbol typing.

---

## 7. Limits

1. **Two functions lifted**, both required by the ticket; no unrelated flag
   consumer was opened.
2. **The mask's consumer is not followed**, so the gather is proven to *produce*
   the mask and not to *cause* its effect.
3. **`ADS_MATCH` remains BLOCKED.**
4. **The array extent is bounded, not measured.**

---

## 8. Recommended next subsystem batch

1. **The popper of the gathered mask.** The gather pushes a packed run of flags;
   finding what pops it would turn "a mask is produced" into the engine behaviour
   it drives, and it is the natural next link.
2. **The array's size**, by finding a reader that indexes it with a bound, or by
   finding the object's allocation. That would settle whether the gather's
   unbounded offset is reachable at runtime.
3. **The remaining 50 non-write-back value consumers**, already bounded by the
   earlier scan.
4. **Native slot 178 at `0x08003030`**, the one native routine with an independent
   runtime anchor from a 2026 capture.
