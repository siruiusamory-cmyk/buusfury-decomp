# The value-stack arithmetic family (DECOMP-LIFT-SCRIPT-ARITH-001)

**Status:** the arithmetic family is complete. Slots 8 and 9 are lifted, and
together with slot 7 they establish the VM's binary arithmetic stack contract.
**Targets:** primary dispatch slot 8 at `0x08003D52` and slot 9 at `0x08003D66`, Thumb.
**Baseline:** `7baa3bfa8a2e74cf8a29b24e555511b13befa03e`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, still independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | both handlers' pop, operands, result slot, wrap and underflow, checked by RUNNING them: 45 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | they compile, link at `0x08003D52` and emit bytes: 40 bytes |
| **ADS_MATCH** | **BLOCKED** | whether they reproduce the original compiler: `ADS12_LICENSE_UNAVAILABLE` |

No match is claimed.

---

## 2. The boundaries, re-derived

Both were re-derived from the ROM by aligned chain-walk rather than taken from
the previously observed sibling relationship.

| Slot | Extent | Size | Instructions | Terminator | Calls | Literals |
| --- | --- | --- | ---: | --- | --- | --- |
| 8 | `0x08003D52..0x08003D66` | 20 B | 10 | `0x08003D64` | none | none |
| 9 | `0x08003D66..0x08003D7A` | 20 B | 10 | `0x08003D78` | none | none |

Zero gaps in each. **No direct BL site anywhere in the image targets either
entry**, so both are reached only through the primary dispatch table, at slots 8
(table word `0x08003D53`) and 9 (word `0x08003D67`). Both are leaves with **no
literal pool**: every instruction is register-only.

The three members tile `0x08003D3E..0x08003D7A` contiguously, twenty bytes each.

---

## 3. The family, derived from the ROM

The derivation re-reads **all three** members regardless of which unit they live
in, so the shared contract comes from the image rather than from the sibling
relationship being asserted.

| Slot | Entry | Operation | Consumes | Produces | Δcount | Reads `r1` | Underflow check |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 7 | `0x08003D3E` | `adds r1, r2, r1` | 2 | 1 | -1 | no | **no** |
| 8 | `0x08003D52` | `subs r1, r2, r1` | 2 | 1 | -1 | no | **no** |
| 9 | `0x08003D66` | `muls r2, r1, r2` | 2 | 1 | -1 | no | **no** |

Slot 7 is carried in the table as the reference member; it is reconstructed in a
separate unit and **its committed report is byte-identical to before this
ticket**, verified by `git diff` on `config/lift_stack.json`.

### The shared stack contract

```
context+0x00          a COUNTER
context+4+4*i         the values, index i in 0..count-1

1. the counter is read, decremented by one, and written back;
2. the operands are the TOP TWO slots: values[count-1] via [slot+4] (the old top)
   and values[count-2] via [slot];
3. one ALU instruction combines them;
4. the result is written to the LOWER slot, values[count-2], and the upper slot
   is left ABANDONED above the new counter, not cleared.
```

So every member consumes two values, produces one, and moves the counter by
exactly **-1**. The counter is written back **before** the operand reads, which
the underflow behaviour proves.

### Operand order, now proven directly

Slot 7 could not show the order because addition is commutative, and slot 9
cannot either. **Slot 8 can.** Thumb renders a two-source ALU op as
`op Rd, Rn, Rm` and computes `Rn <op> Rm`, so `subs r1, r2, r1` computes
`r2 - r1`. The register loaded from the **lower** slot is `r2`, and the one
loaded from the **top** is `r1`. Therefore:

```
result = values[count-2] - values[count-1] = DEEPER - TOP
```

and the structural contract for the whole family is:

```
deeper stack value = FIRST source operand
top stack value    = SECOND source operand
```

The derivation **finds** the non-commutative member by mnemonic rather than
naming slot 8, and reports which members are commutative (`[7, 9]`) instead of
implying that every member proves the order.

### One structural difference in slot 9

Slots 7 and 8 leave the result in `r1` and store `str r1, [r0]`. Slot 9's
`muls r2, r1, r2` writes `r2`, so slot 9 stores `str r2, [r0]` at `0x08003D76`.
The result register differs; the slot written and the contract do not.

### Overflow and wrap

All three are plain 32-bit operations with **no saturation and no overflow
branch**. `adds` and `subs` wrap modulo 2^32, and `muls` keeps only the **low 32
bits** of the product - `0x10000 * 0x10000` is `0`, and `0xFFFF * 0xFFFF` is
`0xFFFE0001`.

### Underflow: no check, in any member

A zero counter becomes `0xFFFFFFFF`, the slot address becomes `context-4`, and
the arithmetic runs against the word immediately **below** the context object:

| Slot | `top` | `deeper` | Result written to `context-4` |
| --- | --- | --- | --- |
| 7 | `*context` = `0xFFFFFFFF` | word below | `deeper - 1` |
| 8 | `*context` = `0xFFFFFFFF` | word below | `deeper + 1` |
| 9 | `*context` = `0xFFFFFFFF` | word below | `-deeper` |

No member touches a value slot, and successive underflows walk the base four
bytes further down each time. **Reproduced exactly; no guard was added.**

That `top` is exactly `0xFFFFFFFF` is also the proof of the ordering: it can only
be the brand-new counter if the store landed before the reads.

---

## 4. The comparison

Artifact: `config/lift_arith.json`, regenerated and compared key by key.

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 40 | **40** |
| Instructions | 20 | **20** |
| Differing bytes in the overlap | - | 18 |
| Instruction spans keyed on the original's boundaries | 20 | - |
| Spans byte-identical | - | 2 |
| Calls / literals / returns | 0 / 0 / 1 each | 0 / 0 / 1 each |

Both members pair by name over **exactly their own extent** (`same_extent` true
for each) at 20 bytes and 10 instructions. Equal size is still **not a match**:
18 bytes differ, `byte_identical` is false, and a test asserts that.

---

## 5. Proven, and unresolved

### Proven

Everything in section 3, plus:

- both extents, terminators, zero gaps, no calls, no pool;
- the family's three operations, each from its own instruction;
- the operand order, directly, from the non-commutative member;
- an **antisymmetry sweep** over 4096 operand pairs, `sub(a,b) == -sub(b,a)`,
  which no commutative operation could satisfy;
- exhaustive sweeps of all 65,536 operand pairs in `0..255` for both handlers.

### Unresolved

- **what consumes the surviving value.** Both handlers leave it on the stack and
  return;
- **the meaning of an opcode index.** Slot 8 is proven to subtract and slot 9 to
  multiply, from their own instructions; the slot *numbers* are dispatch details.
  **No opcode table is reconstructed and no opcode index is given a name** beyond
  the operation the ARM instruction performs;
- whether any caller relies on the underflow behaviour;
- why the pop family is split between native and primary dispatch at all.

---

## 6. Regression status

- **no `--defsym` external-call bindings** - neither unit has external calls, and
  `render_external_symbols` still emits `.thumb_func` before `.set`;
- **Thumb externals keep Thumb symbol typing**, asserted by the generated source;
- **no linker-generated ARM veneers**, asserted by scanning every built ELF.

All six lift reports regenerate **identically**, and `git diff` on the five
earlier report files is **empty**, including `config/lift_stack.json` for slot 7:

```
LIFT gbaram   REPORT: PASS
LIFT bci      REPORT: PASS
LIFT handler2 REPORT: PASS
LIFT operand  REPORT: PASS
LIFT stack    REPORT: PASS      <- slot 7, byte-identical
LIFT arith    REPORT: PASS
```

One note on that: slot 7's registry `notes` text feeds its report, and an early
revision of this ticket changed one clause in it from "Slots 8 and 9 are NOT
lifted." to "... NOT lifted here.". That flowed into the report. The exact
earlier wording was restored so the report is byte-identical, and a test now pins
that wording so a later ticket cannot silently restate it.

---

## 7. Limits

1. **Three arithmetic members only.** No comparison, shift, bitwise or unary
   handler is reconstructed, and the family of 84 pop sites is untouched beyond
   the mechanical scan.
2. **No reader of the surviving value is reconstructed**, so the expression
   system still has no observable end.
3. **`ADS_MATCH` remains BLOCKED.** Every number in section 4 describes a modern
   compiler.
4. **Slot 9's order is unobservable**, like slot 7's; only slot 8 proves it.

---

## 8. Recommended next stack consumer

1. **A consumer that READS the surviving value** rather than combining two. That
   is what would close the loop from push to pop to use and make the stack
   observable end to end. The mechanical scan already knows where the 111 pop
   sites are; the interesting ones are those whose result is not written back to
   a stack slot.
2. **The remaining 81 pop sites**, ranked by the same criteria used to pick the
   first three - smallest, fewest calls, simplest observable result.
3. **The thunk block `0x080046AA0..0x080046AA6`**, still unlifted, which closes
   the call path from the interpreter through to a handler.
4. **Native slot 178 at `0x08003030`**, the one native routine with an independent
   runtime anchor from a 2026 capture.
