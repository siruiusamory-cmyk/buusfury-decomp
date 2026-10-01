# The reader of the flag array (DECOMP-LIFT-SCRIPT-FLAGREAD-001)

**Status:** the first reader is found, bounded, and its first consequence proven.
The chain `encoded value -> push -> arithmetic -> consumer -> effect -> reader ->
consequence` is closed.
**Target:** `sub_08004364` at `0x08004364`, Thumb.
**Baseline:** `e6a7206cf23181d315cf00e9149f19a3ddac9849`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, still independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | the index split, the boolean result and the fact that nothing is written, checked by RUNNING them: 17 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | it compiles, links at `0x08004364` and emits bytes: 38 bytes |
| **ADS_MATCH** | **BLOCKED** | whether it reproduces the original compiler: `ADS12_LICENSE_UNAVAILABLE` |

No match is claimed.

---

## 2. How it was found

A scan walked every reachable function and looked for the signature of this
storage region: an `adds rX, #0x50` followed within a few instructions by a byte
access through `rX`. It found **four hits**, and they turned out to be a
contiguous **accessor trio**:

| Entry | Size | First byte access | Role |
| --- | --- | --- | --- |
| `0x08004364` | 28 B | `ldrb` | **test** - returns a boolean |
| `0x08004380` | 22 B | `ldrb` + `strb` (`orrs`) | set - lifted previously |
| `0x08004396` | 22 B | `ldrb` + `strb` (`bics`) | clear |
| `0x0803F110` | 74 B | `strb` at displacement 15 | a different offset, not this array |

The three tile `0x08004364..0x080043AC` exactly, so their boundaries confirm one
another. Only the **test** is lifted here.

---

## 3. The reader

| | |
| --- | --- |
| Extent | `0x08004364..0x08004380` |
| Size | **28 bytes** |
| Instructions | **14** |
| Terminators | **two**, at `0x0800437A` and `0x0800437E` (both `bx lr`) |
| Branches | one, `beq` on the masked bit |
| Calls | **none** |
| Literal pool | **none** |
| Callers | `0x080007C4`, `0x080007DA`, `0x080032EE` - re-derived from the ROM |

```
0x08004364  asrs r2, r1, #3        r2 = value >> 3      (ARITHMETIC)
0x08004366  adds r0, r2, r0        r0 = base + (value >> 3)
0x08004368  lsls r2, r1, #0x1d     r2 = value << 29
0x0800436A  adds r0, #0x50         r0 = base + (value >> 3) + 0x50
0x0800436C  ldrb r0, [r0, #5]      r0 = the byte at +5
0x0800436E  lsrs r2, r2, #0x1d     r2 = value & 7
0x08004370  movs r1, #1
0x08004372  lsls r1, r2            r1 = 1 << (value & 7)
0x08004374  ands r0, r1            r0 = byte & mask
0x08004376  beq  0x0800437C        when the masked bit is zero...
0x08004378  movs r0, #1            ...otherwise return 1
0x0800437A  bx   lr
0x0800437C  movs r0, #0            return 0
0x0800437E  bx   lr
```

---

## 4. Bit-index calculation, and the test semantics

The **index split is identical to the setter's**: `asrs #3` selects the byte and
the `lsls/lsrs #0x1d` pair isolates the low three bits. So it reads the **same
byte** the setter writes - `base + (value >> 3) + 0x55`.

| Property | Proven behaviour |
| --- | --- |
| index input | `value`, the same argument the setter takes |
| byte | `value >> 3`, **arithmetic** shift, so a value with bit 31 set indexes **before** the base |
| bit | `value & 7` |
| shift kind | **arithmetic**, matching the setter |
| set or clear | it **tests for SET**: `ands` masks with `1 << (value & 7)` and branches on zero |
| return value | a **normalised boolean**, `0` or `1` - never the masked byte, so a caller cannot see which bit was masked |
| writes | **nothing.** There is no store anywhere in the routine |
| bounds | **none** |
| NULL | **no check** |

The **absence of any store** is what makes this a reader rather than the setter or
the clearer, and the self-check asserts the byte is unchanged across 64 reads.

---

## 5. The first observable consequence

All three call sites consume the boolean, and all three show the bit being used as
a **predicate**:

| Site | What happens to the boolean | Proof |
| --- | --- | --- |
| `0x080007C4` | **materialised** into a word slot | `bl sub_08004364` then `str r0, [r4]` |
| `0x080007DA` | materialised **inverted** | `bl` then `movs r1,#1 ; subs r0, r1, r0 ; str r0, [r4]` |
| `0x080032EE` | **gates a bit-gather** | `bl` then `cmp r0,#0 ; beq ... ; movs r0,#1 ; lsls r0,r4 ; orrs r6,r0` |

So the bit's first concrete consequence is that it becomes a **0/1 value in an
engine slot**, and one caller deliberately inverts it - which is what makes it a
boolean rather than a count. At the third site the boolean gates setting a bit in
a packed local word: a **gather loop that copies set bits out of the array**.

The call sites are **re-derived from the ROM on every run** rather than
remembered, so the consequence is measured.

---

## 6. Proven, and unresolved

### Proven

Everything in sections 3 to 5, plus: the reader, setter and clearer tile
contiguously; the reader makes no calls and loads no literals; a sweep over every
value in `0..511` reads exactly the bit its index arithmetic predicts, both set and
clear; the result is always `0` or `1`.

### Unresolved

- **what the bit MEANS.** No semantic name is assigned to the flag, the array or
  the object, and nothing is imported from another title;
- **how large the array is**, so which values are in range cannot be stated;
- **what reads the materialised word** afterwards. This ticket follows the
  consequence exactly one step;
- whether the callers pass the same object every time.

---

## 7. The comparison

Artifact: `config/lift_flagread.json`, regenerated and compared key by key.

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 28 | 38 |
| Differing bytes in the overlap | - | 25 |
| Instruction spans keyed on the original's boundaries | 14 | - |
| Spans byte-identical | - | 1 |
| Calls / literals / returns | 0 / 0 / 2 | 0 / 0 / 2 |

`is_a_match_claim` is false.

---

## 8. Regression status

- **all eight earlier reports byte-identical** - `git diff` on their report files
  is empty;
- no `--defsym`, no ARM veneers, correct Thumb symbol typing.

---

## 9. Limits

1. **One reader**, and only one step of its consequence.
2. **The flag's meaning is unknown** and is deliberately not guessed.
3. **`ADS_MATCH` remains BLOCKED.**
4. **The clearer at `0x08004396` is not lifted**, though it is bounded by the same
   scan and sits in the same trio.

---

## 10. Recommended next function

1. **The clearer at `0x08004396`** (22 bytes, `bics` + `strb`) would complete the
   accessor trio, and it is already bounded and drawn in this report.
2. **The reader of the materialised word** - the slot written at `0x080007C4` and
   `0x080007DA`. That would turn "the bit becomes a 0/1 value" into "the bit
   controls this engine behaviour", which is the last link left.
3. **How large the array is**, which would settle whether the negative-index cases
   are reachable at runtime.
4. **Native slot 178 at `0x08003030`**, the one native routine with an independent
   runtime anchor from a 2026 capture.
