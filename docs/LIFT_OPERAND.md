# DECOMP-LIFT-SCRIPT-SM7-001 - the variable-length operand reader

**Status:** primary dispatch slot 1 is lifted and its operand format is proven
from the instructions.
**Target:** `0x08003C8A`, the code entry behind primary table word `0x08003C8B` (slot 1), Thumb.
**Baseline:** `893baa99f8cea57c7ae7bf3bbdeab5de12d79a09`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, still independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | the decoding, sign handling and cursor mutation, checked by RUNNING them: 42 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | it compiles, links at `0x08003C8A` and emits bytes: 86 bytes |
| **ADS_MATCH** | **BLOCKED** | whether it reproduces the original compiler: `ADS12_LICENSE_UNAVAILABLE` |

No match is claimed. The comparison carries `is_a_match_claim: false`.

---

## 2. The derived boundary

| | |
| --- | --- |
| Extent | `0x08003C8A..0x08003CBE` |
| Size | **52 bytes** |
| Instructions | **26** |
| Terminators | **one**, at `0x08003CBC` (`bx lr`) |
| Gaps | none |
| Calls | **none** |
| Literal pool | **none** |
| Dispatch entry | primary slot 1, table word `0x08003C8B` |

Anchored twice over: the primary dispatch table holds it at slot 1, and the
chain-walk terminates cleanly. **No direct BL site anywhere in the image targets
it**, so it is reached only through the dispatch table.

Its end, `0x08003CBE`, is exactly the slot-2 handler's derived entry. Two
independently derived boundaries confirming each other.

**This is a leaf.** No calls and no literal loads, so it needed **no helper** and
no pool stubbing. `has_literal_pool` is reported as `false` - a fact about the
unit, not a measurement that failed.

**Pool / TU relationship: not established.** With no pool there is no pooling
evidence either way. The handler is contiguous with the slot-2 handler, which is
consistent with a shared original translation unit and is not proof of one. It is
reconstructed in its own file and registered as its own lift target; the slot-2
target is untouched, so its committed report still regenerates byte for byte.

---

## 3. The encoding, read off the instructions

```
acc = 0
loop:
  acc = acc << 7                    lsls r2,r2,#7        @ 0x08003C90
  b   = *cursor                     ldrb r3,[r4]         @ 0x08003C92
  cursor += 1                       adds r4,#1           @ 0x08003C94
  *cursor_slot = cursor             str  r4,[r1]         @ 0x08003C96
  acc += (b & 0x7F)                 lsls/lsrs/adds       @ 0x08003C98..9C
  if (b & 0x80) goto loop           lsls r3,r3,#0x18 ; bmi  @ 0x08003C9E..A0
then:
  if (acc & 1) value = -(acc >> 1)  lsls/bpl/asrs/rsbs  @ 0x08003CA2..A8
  else         value =  (acc >> 1)                       @ 0x08003CAC
push value onto the context's value stack
```

| Property | Value | Where it comes from |
| --- | --- | --- |
| Group width | **7 bits** | the shift pair by 25 at `0x08003C98`/`0x08003C9A` isolates the low 7 bits |
| Continuation flag | **bit 7**, set means another byte follows | a shift by 24 feeds the `bmi` at `0x08003CA0` |
| Group order | **most significant first** | the accumulator is shifted left *before* each group is added |
| Sign | **bit 0** of the accumulator | a shift by 31 feeds the `bpl` at `0x08003CA4` |
| Magnitude | the rest, by an **arithmetic** right shift | `asrs` at `0x08003CA6` and `0x08003CAC` |
| Bytes per iteration | 1 | one `ldrb` |
| Length limit | **none** | the only exit is the bit-7 test |

This is **big-endian base-128 sign-magnitude**. It is not two's complement, and
the sign is not a separate byte.

### Bytes consumed, and the reachable range

| Bytes | Accumulator bits | Value range |
| --- | --- | --- |
| 1 | 0..6 | **-63 .. +63** |
| 2 | 0..13 | **-8191 .. +8191** |
| 3 | 0..20 | **-1048575 .. +1048575** |
| 4 | 0..27 | **-134217727 .. +134217727** |
| 5+ | 0..31 | beyond this the artifact below applies |

Each extreme was simulated from the derived group width, not tabulated, and the
test recomputes it from the same width.

### The encoding is not canonical

Leading zero groups are accepted, so one value has many spellings: `0x02` and
`0x80 0x02` both decode to **+1**. Nothing trims them. The byte count carries no
information the value does not already have.

There are also **two encodings for zero**: `0x00` is positive zero and `0x01` is
a *negative* zero, because bit 0 is the sign and the magnitude is 0. Both decode
to 0.

### There is no length limit and no validation

The loop's only exit is a byte with bit 7 clear. Nothing counts iterations,
compares the cursor against a bound, or caps the read. A run of bytes with bit 7
set is followed indefinitely, so malformed input walks the cursor forward until it
happens to meet a byte with bit 7 clear. The self-check drives 40 and then 63
continuation bytes and confirms all are consumed.

**No length check has been added.** The original performs none, and inventing one
would change the behaviour being reconstructed.

### The high-accumulator artifact

The magnitude is extracted with an **arithmetic** shift of the full 32-bit
accumulator. While bit 31 is clear the result is exactly sign-magnitude. Once bit
31 is set the shift replicates the sign bit, and the two branches stop meaning
what they say:

| Accumulator | Nominal branch | Result |
| --- | --- | --- |
| `0x7FFFFFFE` | positive | +1073741823 (exact) |
| `0x7FFFFFFF` | negative | -1073741823 (exact) |
| `0x80000000` | positive | **-1073741824** (negative!) |
| `0x80000001` | negative | **+1073741824** (positive!) |
| `0xFFFFFFFF` | negative | **+1** |

The maximal all-ones five-group sequence `0xFF 0xFF 0xFF 0xFF 0x7F` builds
accumulator `0xFFFFFFFF`, takes the negative branch, shifts arithmetically to
`0xFFFFFFFF` (= -1), and negates that to produce **+1**. A naive sign-magnitude
model would predict -2147483647 and be wrong.

**This is recorded as the code's actual behaviour and reproduced exactly.** It is
not corrected, and the reconstruction contains no guard against it.

---

## 4. The cursor contract

The interpreter's contract holds unchanged: entry **r0 = context**,
**r1 = the address of the cursor slot**.

- every byte read advances the cursor by one and writes it **straight back into
  the slot**, before the continuation test - so the terminating byte has already
  been consumed when the loop exits, and the cursor ends one past it;
- **the handler makes no calls**, so there is no ordering question between a
  cursor update and a call. That is the whole answer for this handler;
- the decoded value is **pushed** onto a stack in the context: `context+0x00` is
  a counter, incremented by one, and the value goes to
  `context + 4 + 4*old_counter`.

### A cross-ticket consequence

This handler proves `context+0x00` is a **counter** - something the interpreter's
own translation unit used but could not name. In `sub_08004038` the store of zero
at `0x0800405C` now reads as *emptying this stack*, not as an anonymous field
clear. The field is named `count` in the new source on that evidence.

`src/ByteCodeInterpreter.c` is deliberately **not** edited by this ticket, so that
its committed report stays byte-for-byte reproducible. Renaming its `field_00`
would be correct and is left to a future ticket that can re-verify that target.

---

## 5. The name "sm7"

**"sm7" does not appear anywhere in the ROM.** It is not ASCII, not UTF-16, not a
symbol string. It is a project nickname, and it is recorded in the source and the
report as a **candidate alias only**, never as an established name.

The encoding above is described from the instructions themselves and needs no
nickname. No operand meaning has been imported from another LoG title; a test
asserts the source names none of them and contains no `case` label.

---

## 6. The comparison

Artifact: `config/lift_operand.json`, regenerated and compared key by key.

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 52 | 86 |
| Differing bytes in the overlap | - | 50 |
| Instruction spans keyed on the original's boundaries | 26 | - |
| Spans byte-identical | - | 0 |
| Calls | 0 | 0 |
| Literal slots | 0 | 0 |
| Return points | 1 | 1 |

The modern build is **34 bytes larger** and no byte matches. The **call count,
literal count and return structure all agree** - the shape is right, the code
generation is not.

---

## 7. Proven, and unresolved

### Proven, each instruction-backed or run

- the full algorithm in section 3, including the 7-bit groups, the bit ordering,
  the continuation rule, the sign bit and the arithmetic magnitude shift;
- the value range per byte count, simulated from the derived width;
- the non-canonical encodings and both spellings of zero;
- the high-accumulator artifact, including that the maximal five-group sequence
  decodes to `+1`;
- the absence of a length limit;
- the cursor advancing one byte per group and ending one past the terminating
  byte;
- the push onto `context+0x00` / `context+4+4*i`;
- the entry contract, by passing a second context and observing the push land on
  it.

Coverage: **exhaustive** over every 1-byte input (256) and every valid
terminating 2-byte input (16,384), each compared against a reference that folds
the groups with a different expression. Plus hand-written expectations for the
shortest encodings, the extremes, both zeros and the artifact.

### Unresolved

- **What consumes the pushed value.** Nothing in this handler calls anything, so
  nothing here observes it;
- whether any caller relies on the non-canonical spellings, which cannot be
  answered without lifting a consumer;
- what the surrounding handlers do with the same value stack;
- **whether this handler shared a translation unit with slot 2.** No pool, so no
  evidence.

---

## 8. Regression status

The previous ticket's linker fix is preserved and re-verified:

- **no `--defsym` external-call bindings** - `derive_external_calls` found none
  here, and `render_external_symbols` still emits `.thumb_func` before `.set` for
  any unit that has them;
- **Thumb externals keep Thumb symbol typing**, asserted by the generated source;
- **no linker-generated ARM veneers** in any compared image, asserted by scanning
  every built ELF for `from_thumb` / `from_arm` symbols.

All four lift reports regenerate **identically**:

```
LIFT gbaram   REPORT: PASS (the whole document regenerated identically)
LIFT bci      REPORT: PASS (the whole document regenerated identically)
LIFT handler2 REPORT: PASS (the whole document regenerated identically)
LIFT operand  REPORT: PASS (the whole document regenerated identically)
```

---

## 9. Limits

1. **One handler of thirty-one.** The operand it reads still has no observable
   effect until a consumer is lifted.
2. **No consumer is reconstructed**, so the pushed value's meaning is unknown.
3. **`ADS_MATCH` remains BLOCKED.** Every number in section 6 describes a modern
   compiler.
4. **The TU relationship with slot 2 is unresolved**, for the reason in section 2.
5. The artifact is recorded, not explained: the original likely never feeds this
   reader an accumulator with bit 31 set, but nothing here proves that.

---

## 10. Recommended next work

1. **The consumer of the value stack.** `context+0x00` is now proven to be a
   counter, so the natural next question is which handler or native routine reads
   `context+4+4*i`. Finding it turns this reader from a decoder into a proven part
   of an expression system, and it is the single largest step available.
2. **Primary slot 21 at `0x08003E84`**, sharing the slot-2 handler's pool at
   `0x08003F40`. It would settle whether that pool defines a translation unit, and
   it may also touch the same value stack.
3. **The thunk block `0x080046AA0..0x080046AA6`** as one small unit, closing the
   call path from the interpreter through to a handler.
4. **Native slot 178 at `0x08003030`**, the one native routine with an independent
   runtime anchor, so its behaviour could be checked against an observation rather
   than only against statically read code.
