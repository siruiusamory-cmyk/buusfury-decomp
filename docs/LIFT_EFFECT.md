# DECOMP-LIFT-SCRIPT-EFFECT-001 - what the popped VM value does

**Status:** the effect is established. The chain `encoded value -> push ->
arithmetic -> surviving value -> call -> concrete effect` is closed.
**Target:** `sub_08004380` at `0x08004380`, Thumb.
**Baseline:** `98a8e985f837163d8ede4d4afaec03277679e1c1`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, still independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | the bit arithmetic, the byte address, the read-modify-write and the negative-index case, checked by RUNNING them: 19 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | it compiles, links at `0x08004380` and emits bytes: 36 bytes |
| **ADS_MATCH** | **BLOCKED** | whether it reproduces the original compiler: `ADS12_LICENSE_UNAVAILABLE` |

No match is claimed.

---

## 2. The function

| | |
| --- | --- |
| Extent | `0x08004380..0x08004396` |
| Size | **22 bytes** |
| Instructions | **11** |
| Terminators | **one**, at `0x08004394` (`bx lr`) |
| Branches | none |
| Calls | **none** |
| Literal pool | **none** |
| Callers | `sub_080007E6` at `0x080007F8` (native dispatch entry 29) |

**A leaf.** No calls and no literal pool, so **no helper had to be followed** and
the effect below is established by this routine alone. Its only caller is the
routine the previous ticket lifted.

```
0x08004380  asrs r2, r1, #3        r2 = value >> 3      (ARITHMETIC)
0x08004382  adds r0, r2, r0        r0 = base + (value >> 3)
0x08004384  lsls r3, r1, #0x1d     r3 = value << 29
0x08004386  adds r0, #0x50         r0 = base + (value >> 3) + 0x50
0x08004388  ldrb r2, [r0, #5]      r2 = the byte at +5 from there
0x0800438A  lsrs r3, r3, #0x1d     r3 = value & 7
0x0800438C  movs r1, #1
0x0800438E  lsls r1, r3            r1 = 1 << (value & 7)
0x08004390  orrs r1, r2            r1 = that bit | the byte
0x08004392  strb r1, [r0, #5]      the byte at +5 := r1
0x08004394  bx   lr                the single exit
```

---

## 3. The exact argument flow

Proven in the previous ticket from the caller, and carried into this report as
`boundary_evidence.called_from`:

| Register | Value |
| --- | --- |
| `r0` | `*(u32*)(0x08054FBC + 0x14)` - the `+0x14` field of the object at the caller's only literal |
| `r1` | **the value popped from the ByteCodeInterpreter stack**, `values[count-1]` |

The routine never touches the VM stack itself: it receives the value in `r1` and
has no stack access at all.

---

## 4. The concrete effect

```
SETS BIT (value & 7) OF THE BYTE AT  base + (value >> 3) + 0x55
```

and changes nothing else.

The two shifts are the standard **bit-array split**: the value's low three bits
select the bit within the byte (`lsls #0x1d` then `lsrs #0x1d` isolates them) and
the remaining bits select which byte (`asrs #3`). The byte is read with `ldrb`,
one bit is OR-ed in with `orrs`, and the byte is written back with `strb`, so the
other seven bits are preserved. That is a **single-bit set** - a flag or membership
mark inside an object - and it is the first externally observable effect of the VM
value.

Every constant above is taken from the instruction stream by the derivation
(`byte_index_shift: 3`, `bit_index_mask_bits: 3`, `object_offset: 0x50`,
`field_offset_from_object_offset: 5`, `read_modify_write: true`), so a change to
any instruction changes the report.

---

## 5. The byte-index shift is ARITHMETIC, and that matters

`asrs r2, r1, #3` replicates the sign bit. A value with **bit 31 set** therefore
gives a *negative* byte index and the write lands **before** the base:

| Value | `value >> 3` | `value & 7` | Byte written |
| --- | --- | --- | --- |
| `0` | `0` | 0 | `base + 0x55`, bit 0 |
| `7` | `0` | 7 | `base + 0x55`, bit 7 |
| `8` | `1` | 0 | `base + 0x56`, bit 0 |
| `0xFFFFFFFF` | `0xFFFFFFFF` | 7 | **`base + 0x54`**, bit 7 |
| `0x80000000` | `0xF0000000` | 0 | `base + 0xF0000055` |

A **logical** shift would have placed the last two at `base + 0x1FFFFFFF + 0x55`
and `base + 0x10000055` - far *above* the base. The reconstruction **models the
arithmetic shift explicitly** (`arithmetic_shift_right_3`, replicating the top
three bits) rather than leaving it to the compiler, because C's right shift of a
negative signed value is implementation-defined.

---

## 6. No bounds check, and no NULL check

There is **no compare against a size and no conditional branch anywhere** in the
routine. Every value selects a byte and that byte is written, however far outside
the object it lies - `0x80000000` writes to `base + 0xF0000055`. **No guard was
added.**

The self-check therefore asserts the far cases **by pointer arithmetic only and
does not execute them**: performing that write would fault, and that is precisely
the behaviour being recorded. For the in-range-but-outside-the-body case the test
gives the object a large enough arena to observe the out-of-body write rather than
crash on it.

---

## 7. The comparison

Artifact: `config/lift_effect.json`, regenerated and compared key by key.

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 22 | 36 |
| Differing bytes in the overlap | - | 20 |
| Instruction spans keyed on the original's boundaries | 11 | - |
| Spans byte-identical | - | 1 |
| Calls / literals / returns | 0 / 0 / 1 | 0 / 0 / 1 |

`is_a_match_claim` is false.

---

## 8. Proven, and unresolved

### Proven

Everything in sections 2 to 6, plus: the caller contract, carried from the
previous ticket and re-asserted here (the caller's own report still binds its
callee to `0x08004380`); the routine is a leaf, so nothing else was needed.

### Unresolved

- **what the bit MEANS.** It is a bit in a byte array inside an object reachable
  from `0x08054FBC + 0x14`. **No name is assigned to the object, the array, or the
  bit**, and nothing is imported from another title;
- **how large that byte array is**, so which values are in range cannot be stated
  from this routine alone;
- **what reads the bit afterwards**;
- whether the caller's `+0x14` field is always the same object.

---

## 9. Regression status

- **all seven earlier reports byte-identical** - `git diff` on their seven report
  files is empty;
- **no `--defsym`**, Thumb externals keep Thumb typing, **no ARM veneers**;
- all **eight** reports regenerate identically.

---

## 10. Limits

1. **The effect is proven as a memory write**, not as a gameplay consequence: the
   bit is set, and what consumes it is unknown.
2. **`ADS_MATCH` remains BLOCKED.** Every number in section 7 describes a modern
   compiler.
3. **Out-of-range writes are asserted by pointer arithmetic, not executed**, for
   the reason in section 6.
4. **Only this one callee was followed**; no other value consumer was touched.

---

## 11. Recommended next function

1. **The reader of the bit array.** The array base is `base + 0x50` with the byte
   field at `+5`, and `base` is `*(0x08054FBC + 0x14)`. Finding the routine that
   *reads* that byte would close the loop from VM value to game state, which is the
   last link this chain is missing.
2. **How large the array is**, which would settle which VM values are in range and
   whether the negative-index case is reachable at runtime.
3. **The other 51 non-write-back value consumers** from the previous ticket's scan
   (entries 30, 37, 38, 54, 138, 148, 194 and the rest), which are already bounded.
4. **Native slot 178 at `0x08003030`**, the one native routine with an independent
   runtime anchor from a 2026 capture.
