# The first surviving-value consumer (DECOMP-LIFT-SCRIPT-USE-001)

**Status:** the chain `encoded value -> push -> arithmetic -> surviving value ->
actual use` is closed. The first routine that consumes a stack value for a
non-stack side effect is found, bounded, lifted and run.
**Target:** native dispatch entry 29, code address `0x080007E6`, Thumb.
**Baseline:** `ef01f7996a6854b9323e580aee622224c2f33f0a`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, still independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | the pop, the absence of a write-back, both call arguments and the ordering, checked by RUNNING it: 32 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | it compiles, links at `0x080007E6` and emits bytes: 40 bytes |
| **ADS_MATCH** | **BLOCKED** | whether it reproduces the original compiler: `ADS12_LICENSE_UNAVAILABLE` |

No match is claimed.

---

## 2. Why this candidate

The scan walked both proven dispatch tables and scored every function that
touches `context+0x00` or `context+0x04+4*i`, then **excluded pure stack
transforms**: pushes, and binary reductions that write a result back into a stack
slot. That left **52 functions that read a stack value and write nothing back**.

Ranked by the ticket's criteria:

| Criterion | Result |
| --- | --- |
| reads top/deeper value | yes, one value |
| no replacement written back | **yes** |
| reachable through a proven dispatch table | native entry 29, via interpreter -> primary slot 2 |
| small bounded control flow | **24 bytes, 11 instructions, no branches** |
| observable side effect | **one call, receiving the value** |

`0x080007E6` is the **smallest** of the 52, and it is the only one at that size
whose side effect is a call taking the value as an argument - the fully
observable case. Three other 24-byte candidates exist and are near-identical in
shape (native entries 30, 37, 38, 54, 138, 148, 194); this is the first in table
order and the one lifted.

---

## 3. The boundary

| | |
| --- | --- |
| Extent | `0x080007E6..0x080007FE` |
| Size | **24 bytes** |
| Instructions | **11** |
| Terminators | **one**, at `0x080007FC` (`pop {r3, pc}`) |
| Branches | none |
| Calls | **one**, `0x08004380` |
| Literal pool | one word at `0x080008D8` (**not** adjacent: `0xDA` bytes past the code) |
| Dispatch | native table entry 29, word `0x080007E7` |

Exactly one native entry points here. The caller chain is the proven one:
interpreter `0x08004038` dispatches primary slot 2 `0x08003CBE`, which indexes the
native table.

---

## 4. The routine, all eleven instructions

```
0x080007E6  push {r3, lr}
0x080007E8  ldr  r1, [r0]        r1 = context+0x00, the counter
0x080007EA  subs r1, #1          r1 = count - 1
0x080007EC  str  r1, [r0]        context+0x00 = count - 1
0x080007EE  lsls r1, r1, #2      r1 = (count-1) * 4
0x080007F0  adds r0, r1, r0      r0 = context + (count-1)*4
0x080007F2  ldr  r1, [r0, #4]    r1 = values[count-1]   <- the popped value
0x080007F4  ldr  r0, [pc, #0xe0] r0 = 0x08054FBC, a global base
0x080007F6  ldr  r0, [r0, #0x14] r0 = *(0x08054FBC + 0x14)
0x080007F8  bl   0x08004380      sub_08004380(r0, r1)
0x080007FC  pop  {r3, pc}        the single exit
```

---

## 5. Stack behaviour

| Property | Proven behaviour |
| --- | --- |
| pop or peek | **pop**: the counter is decremented by exactly one and written back |
| values read | **1**, `values[count-1]` - the old top |
| values produced | **0** |
| written back to the stack | **nothing.** There is no store whose base is the slot register computed at `0x080007F0` |
| counter mutation timing | written back **before** the value is read, which is before the call |
| effect on surviving values | none: the consumed slot keeps its old value and is simply abandoned |
| cursor slot (`r1` in) | **never read** - the first instruction overwrites `r1` |
| underflow check | **none** |

That **absence of a write-back** is what distinguishes this routine from the
arithmetic family, which always writes its result into the lower operand slot.
The difference is derived, not assumed: the matcher looks for a store based on
the slot register and reports `writes_back_to_the_stack: false`
with the evidence.

---

## 6. The non-stack side effect

**One call, `sub_08004380`, whose arguments are:**

| Register | Value |
| --- | --- |
| `r0` | `*(u32*)(0x08054FBC + 0x14)` - the `+0x14` field of the object at the routine's only literal |
| `r1` | **the popped stack value** |

So the surviving value leaves the interpreter and enters the engine as the
**second argument** of an ordinary call. That is the observable use the target
chain was looking for.

`sub_08004380` is **declared, not reconstructed**, and it is bound at its original
address `0x08004380` through `render_external_symbols`, so the call displacement
is right and **no stub bytes** enter the compared window.

**Ordering**, proven by the self-check reading the counter from *inside* the
callee: the counter store precedes the value read, which precedes the call.

---

## 7. Underflow

No check, as everywhere else in this VM. With a counter of zero:

```
count = 0xFFFFFFFF
base  = context + 0xFFFFFFFF*4 = context - 4
value = *(context - 4 + 4) = *(context) = 0xFFFFFFFF   <- the new counter
```

**Unlike the arithmetic family, this underflow is harmless to memory.** Because
the routine has **no store to the slot**, nothing below the context object is
written; the `[slot+4]` read lands exactly on the counter, so the callee receives
`0xFFFFFFFF`. A second underflow walks the base four bytes further down and reads
whatever is there - still without writing.

The self-check asserts all of this against a context that carries real storage
below it, so the walk is observable and bounded. **No guard was added.**

---

## 8. The comparison

Artifact: `config/lift_use.json`, regenerated and compared key by key.

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 24 | 40 |
| Differing bytes in the overlap | - | 16 |
| Instruction spans keyed on the original's boundaries | 11 | - |
| Spans byte-identical | - | 1 |
| Calls / literals / returns | 1 / 1 / 1 | 1 / 1 / 1 |

The call count, literal count and return structure all agree while no byte does.
`is_a_match_claim` is false.

---

## 9. A defect this ticket found in its own report

The first version of this target **reused the arithmetic shape matcher**. That
matcher is written for a *write-back* reduction, so on a routine defined by not
writing back it failed its later steps and still **published derived fields**:
`operation: ldr r0, [pc, #0xe0]`, `consumes: 2`, `produces: 1`, and a
`result_slot` - every one of them false for this code.

That is the same defect class the project has hit before: a **field asserting what
the derivation did not prove**. It was fixed by adding `derive_value_use`, a
matcher for the consumer shape that reports `consumes: 1`, `produces: 0`,
`writes_back_to_the_stack: false` and the evidence for it, and by wiring this unit
to that matcher instead. A test now asserts the report carries `value_use` and
**not** `stack_access`, and that `produces == 0`.

A second, smaller defect was found in the same matcher: it did not account for the
routine's leading `push {r3, lr}`, so every reported step address named the
instruction *before* the one that actually matched. The offset is now applied to
the recorded address as well as to the match, and a test pins the first and last
step addresses.

---

## 10. Proven, and unresolved

### Proven

Everything in sections 4 to 7, plus: exactly one native entry points here; the
call target is derived from the ROM; 52 routines read a stack value without
writing back, and this is the smallest.

### Unresolved

- **what `sub_08004380` does with the value.** It is declared, not reconstructed,
  so the chain ends here by design;
- **what the object at `0x08054FBC` is.** Its `+0x14` field is passed; the object
  is not named and no meaning is imported from another title;
- **which native index this is at runtime** beyond the table entry that points
  here. No opcode table is reconstructed and no index is given a name;
- whether any caller relies on the underflow behaviour;
- whether the other 51 non-write-back readers are variants of this one. They are
  not examined beyond the scan.

---

## 11. Regression status

- **previous reports byte-identical** - `git diff` on all six earlier report files
  is empty;
- **no `--defsym`** - this unit's single external call goes through
  `render_external_symbols`, which emits `.thumb_func` before `.set`;
- **correct Thumb symbol typing**, asserted by the generated source;
- **no ARM veneers**, asserted by scanning every built ELF for `from_thumb` /
  `from_arm`;
- all **seven** reports regenerate identically.

---

## 12. Limits

1. **One consumer of 52 non-write-back readers.**
2. **The callee is a black box**, so the use is proven as "passed as an argument",
   not as "causes effect X".
3. **`ADS_MATCH` remains BLOCKED.** Every number in section 8 describes a modern
   compiler.
4. **The scan is a lower bound**: it matches the pop idiom, so a consumer reaching
   the stack through a different register path would not be found.

---

## 13. Recommended next VM function

1. **`sub_08004380` at `0x08004380`**, the callee, is now the single most valuable
   next target: it is the routine that actually *uses* the value this ticket
   delivers, and its caller's argument contract is already proven. Following it
   would turn "passed as an argument" into "causes this effect".
2. **The other 24-byte readers** (native entries 30, 37, 38, 54, 138, 148, 194),
   which the scan already bounded. They are the same size and shape, so they would
   go quickly and would show whether this pattern is a family.
3. **The thunk block `0x080046AA0..0x080046AA6`**, still unlifted.
4. **Native slot 178 at `0x08003030`**, the one native routine with an independent
   runtime anchor from a 2026 capture.
