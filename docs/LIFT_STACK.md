# DECOMP-LIFT-SCRIPT-STACK-001 - the first value-stack consumer

**Status:** the first consumer of the ByteCodeInterpreter value stack is found,
bounded, lifted and run.
**Target:** primary dispatch slot 7, entry `0x08003D3E`, Thumb.
**Baseline:** `12580af33a55f7609aaf10707830feb673b6fec1`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, still independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | pop, operand slots, result placement, counter timing and underflow, checked by RUNNING them: 34 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | it compiles, links at `0x08003D3E` and emits bytes: 20 bytes |
| **ADS_MATCH** | **BLOCKED** | whether it reproduces the original compiler: `ADS12_LICENSE_UNAVAILABLE` |

No match is claimed.

---

## 2. How the consumer was found, and why this one

The search was mechanical, not a guess. Every entry in both proven dispatch
tables - 31 primary handlers and 266 native routines - was walked and scanned for
access to `context+0x00` and `context+0x04+4*i`, tracking the context register
through simple aliases.

The **pop idiom** turned out to be a six-instruction inline sequence:

```
ldr  rX, [ctx]        rX = count
subs rX, #1           rX = count - 1
str  rX, [ctx]        count = count - 1        (pre-decrement)
lsls rX, rX, #2       rX = (count-1) * 4
adds rX, rX, ctx      rX = ctx + (count-1)*4
ldr  rX, [rX, #4]     rX = values[count-1]     (the old top)
```

A first detector looking for a base+index memory operand found **nothing**,
because the code computes the address into a register first. Matching the
six-instruction sequence instead found **84 functions containing it, 111 pops in
total** - 69 native and 15 primary.

Ranking by the ticket's criteria:

| Criterion | Result |
| --- | --- |
| direct stack read/pop | all 84 |
| known interpreter/native caller | all, via the two proven dispatch tables |
| smallest isolated function | **`0x08003D3E`, 20 bytes, 10 instructions** |
| simplest observable semantics | one pop, one combining instruction, no calls, no branches |

The three smallest are primary slots **7, 8 and 9**, at 20 bytes each, differing
in exactly one instruction - the value-stack arithmetic trio. Slot 7 is the
smallest and the simplest, and it is directly dispatachable from the interpreter,
so it is the one lifted.

**Slots 8 and 9 are not lifted.** They are read only far enough to establish the
operand-order convention that this commutative handler cannot show by itself.

---

## 3. The derived boundary

| | |
| --- | --- |
| Extent | `0x08003D3E..0x08003D52` |
| Size | **20 bytes** |
| Instructions | **10** |
| Terminators | **one**, at `0x08003D50` (`bx lr`) |
| Branches | none: straight-line |
| Calls | **none** |
| Literal pool | **none** |
| Dispatch entry | primary slot 7, table word `0x08003D3F` |

Anchored by the dispatch table and by the chain-walk; no direct BL site anywhere
in the image targets it.

---

## 4. The handler, all ten instructions

```
0x08003D3E  ldr  r1, [r0]        r1 = context+0x00, the counter
0x08003D40  subs r1, #1          r1 = count - 1
0x08003D42  str  r1, [r0]        context+0x00 = count - 1
0x08003D44  lsls r1, r1, #2      r1 = (count-1) * 4
0x08003D46  adds r0, r1, r0      r0 = context + (count-1)*4
0x08003D48  ldr  r1, [r0, #4]    r1 = values[count-1]   <- the OLD TOP
0x08003D4A  ldr  r2, [r0]        r2 = values[count-2]   <- the NEW TOP
0x08003D4C  adds r1, r2, r1      r1 = values[count-2] + values[count-1]
0x08003D4E  str  r1, [r0]        values[count-2] = the sum
0x08003D50  bx   lr              the single exit
```

---

## 5. Exact stack semantics

| Property | Proven behaviour |
| --- | --- |
| peek or pop | **pop**: the counter decreases by exactly one |
| values consumed | **2** - `values[count-1]` and `values[count-2]` |
| values produced | **1**, written back in place |
| net counter delta | **-1** |
| operand order | `values[count-2] <op> values[count-1]`, i.e. the **deeper** value is the left operand |
| result placement | the **LOWER** slot, `values[count-2]` |
| upper slot | **abandoned**, not cleared - the old top is left above the new counter |
| counter mutation timing | written back **before** either operand is read, so both addresses come from the **new** count |
| context fields touched | `+0x00` (counter) and the two operand slots only |
| cursor slot (`r1` in) | **never read** - the first instruction overwrites `r1` before any read |
| calls | none |
| operation | 32-bit addition, wrapping, with no signed saturation |

### Operand order

Addition is commutative, so **this handler cannot show the operand order by
itself**, and the report says so rather than asserting an order it cannot see.

The convention is established by the sibling at **primary slot 8 (`0x08003D52`)**,
which shares this handler's first eight instructions verbatim and then performs:

```
0x08003D60  subs r1, r2, r1      r1 = r2 - r1
```

Thumb renders a two-source ALU op as `op Rd, Rn, Rm`, and `Rn` is the left
operand. The register loaded from the lower slot is `r2` and the one loaded from
the top is `r1`, so slot 8 computes **`values[count-2] - values[count-1]`**: the
**deeper value is the left operand**. Slot 9 (`0x08003D66`) multiplies, which is
again commutative.

So the trio is a binary arithmetic family over the top two slots, and the
convention is `deeper <op> top`.

### Underflow: no check, and what actually happens

**There is no underflow check.** The counter is decremented with no test and no
branch. With a counter of zero:

```
count_new = 0xFFFFFFFF
base      = context + 0xFFFFFFFF*4 = context - 4      (32-bit wrap)
top       = base[1] = *(context-4+4) = *context       = 0xFFFFFFFF, the new count
deeper    = base[0] = the word immediately BELOW the context object
base[0]   = deeper + 0xFFFFFFFF                        = deeper - 1
```

So an underflowing pop:

- sets the counter to `0xFFFFFFFF`;
- **decrements the word immediately below the context object by one**;
- leaves **every value slot untouched**.

And each successive underflow walks the base another four bytes down: the second
reads and writes `context-8`, the third `context-12`, and so on. The self-check
gives the context four words of real storage below it and asserts exactly this
for the first three underflows.

That result is also the proof of the **ordering**: `top` can only be
`0xFFFFFFFF`, the brand-new counter, if the counter store landed before the
operand reads. Had the reads come first, `top` would have been `0`.

**Nothing has been added to prevent any of this.** The original performs no check,
and a guard would change the behaviour being reconstructed.

---

## 6. The comparison

Artifact: `config/lift_stack.json`, regenerated and compared key by key.

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 20 | **20** |
| Instructions | 10 | **10** |
| Differing bytes in the overlap | - | 9 |
| Instruction spans keyed on the original's boundaries | 10 | - |
| Spans byte-identical | - | 1 |
| Calls | 0 | 0 |
| Literal slots | 0 | 0 |
| Return points | 1 | 1 |

This is the first target whose modern build is the **same size** as the original,
with the same instruction count and one instruction encoding identically. That is
a size coincidence, **not a match**: nine bytes still differ and the report
records `byte_identical: false` and `is_a_match_claim: false`. A test asserts
exactly that, so equal size can never be read as identity.

---

## 7. Proven, and unresolved

### Proven

Everything in section 5, plus the family:

- 84 functions in the image contain the pop idiom, 111 pops in total;
- this one is the smallest, at 20 bytes;
- its neighbours 8 and 9 share the shape and differ in one instruction.

Coverage: an exhaustive sweep of all 65,536 operand pairs in `0..255` against the
wrapped 32-bit sum, plus hand-written expectations for the result placement, the
counter timing, the wraparound cases, the abandoned slot, the cursor slot, the
chained reduction, and three successive underflows.

### Unresolved

- **what consumes the surviving value.** This handler leaves it on the stack and
  returns; the reader is another handler, not reconstructed here;
- **the meaning of an opcode index.** Slot 7's operation is proven to be addition
  from its own instruction; the slot *number* is a dispatch detail. **No opcode
  table is reconstructed and no opcode index is named**;
- whether any caller relies on the underflow behaviour;
- why the family is split between native and primary dispatch at all. 69 of the
  84 are native routines, which is consistent with the primary slots being mostly
  control flow, but the split is not explained here.

---

## 8. Regression status

Preserved and re-verified:

- **no `--defsym` external-call bindings** - this unit has no external calls at
  all, and `render_external_symbols` still emits `.thumb_func` before `.set`;
- **Thumb externals keep Thumb symbol typing**, asserted by the generated source;
- **no linker-generated ARM veneers**, asserted by scanning every built ELF for
  `from_thumb` / `from_arm`.

All five lift reports regenerate **identically**:

```
LIFT gbaram   REPORT: PASS
LIFT bci      REPORT: PASS
LIFT handler2 REPORT: PASS
LIFT operand  REPORT: PASS
LIFT stack    REPORT: PASS
```

---

## 9. Limits

1. **One consumer of a family of 84.** The rest are unexamined beyond the
   mechanical scan.
2. **No reader of the surviving value is reconstructed**, so the expression
   system still has no observable end.
3. **`ADS_MATCH` remains BLOCKED.** Every number in section 6 describes a modern
   compiler.
4. **The operand order rests on sibling evidence**, not on the lifted function's
   own behaviour, for the reason given in section 5.
5. **The 84-function count comes from a pattern match**, so it is a lower bound:
   a consumer that reaches the stack through a different register path would not
   match the idiom.

---

## 10. Recommended next work

1. **Primary slot 8 at `0x08003D52` and slot 9 at `0x08003D66`.** They are 20
   bytes each, already bounded, already carried in this report as siblings, and
   they complete the arithmetic trio. They would also turn the operand-order
   convention from sibling evidence into directly proven behaviour, because
   subtraction is not commutative.
2. **A consumer that reads the surviving value** rather than combining two. That
   is what would close the loop from push to pop to use and make the stack
   observable end to end.
3. **The thunk block `0x080046AA0..0x080046AA6`**, still unlifted, which closes
   the call path from the interpreter through to a handler.
4. **Native slot 178 at `0x08003030`**, the one native routine with an
   independent runtime anchor from a 2026 capture.
