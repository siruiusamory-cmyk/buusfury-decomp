# DECOMP-LIFT-NATIVE178-001 - native dispatch slot 178

**Status:** lifted and validated. Static derivation and an independent runtime
capture agree on the identity, the boundary is proven, and the first concrete
engine effect is established.
**Target:** `0x08003030`, Thumb, native dispatch slot 178.
**Baseline:** `cdc0bb6d29cbe5da7cff3a29dee0e9992ce75b9e`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Identity, cross-validated static and runtime

| | |
| --- | --- |
| Native table | `0x08055098`, 266 entries |
| Slot | **178** |
| Table address of the entry | `0x08055360` |
| **Raw table word** | **`0x08003031`** |
| Thumb bit | set |
| Thumb-normalized address | **`0x08003030`** |
| **Runtime capture address** | **`0x08003030`** |
| Agreement | **yes** |
| Entries pointing here | **exactly one (178)** |

**The runtime capture is used ONLY as identity evidence.** It establishes *where*
the slot points and nothing about what the routine does, and no semantic claim here
rests on it.

---

## 2. The function

| | |
| --- | --- |
| Range | `0x08003030..0x08003070` |
| Size | **64 bytes** |
| Instructions | **30** |
| Terminator | one, at `0x0800306E` (`pop {pc}`) |
| Calls | **two**, `sub_0802BFBC` and `sub_0801191A` |
| Literal | one word at `0x080031B4` |

```
0x08003032  ldr r1,[r0]          the counter
... three times: counter-- ; ldr [slot+4]
0x08003040  str r1,[sp,#8]       local[1] = values[count-1]
0x0800304E  str r1,[sp,#4]       local[0] = values[count-2]
0x0800305A  ldr r0,[r0,#4]       r0 = values[count-3]
0x0800305C  add r1, sp, #4       r1 = &local[0]
0x0800305E  bl  0x0802BFBC       sub_0802BFBC(values[count-3], local)
0x08003064  ldr r0,[pc,#0x14c]   0x08054FBC
0x08003066  ldr r0,[r0,#0x18]    r0 = *(0x08054FBC + 0x18)
0x08003068  bl  0x0801191A       sub_0801191A(that word, the result)
0x0800306E  pop {pc}
```

---

## 3. The native entry contract

| Register | What slot 178 actually does with it |
| --- | --- |
| `r0` | **the interpreter context.** Used as the base of the value stack, reading the counter at `+0x00` and the values at `+4+4*i`, exactly as the other lifted handlers do |
| `r1` | **never read.** The first instruction is `ldr r1,[r0]`, which overwrites it before it can be read |

The dispatcher evidence says `r1` holds the routine's own address incidentally.
**This routine ignores it entirely, and no argument meaning is assigned to it.**

---

## 4. VM stack behaviour

| Property | Proven |
| --- | --- |
| pops | **three** |
| pushes | **none** |
| counter | moves by exactly **−3** |
| read order | top first: `values[count-1]`, `values[count-2]`, `values[count-3]` |
| value slots written | **none** - the consumed slots are abandoned, not cleared |
| context fields | `+0x00` counter, `+0x04+4*i` values |

**The local array is built on the routine's own frame, not on the VM stack:**
`local[1] = values[count-1]` and `local[0] = values[count-2]`, so the pair is handed
to the callee **deepest-of-the-two first** - the *reverse* of VM stack order.

### There is no stack guard
No comparison of the counter against zero or three exists anywhere. A counter below
three wraps and the reads **walk below the context object**. Reproduced, not guarded.
The self-check pins the exact walk: at a count of 1, POP 2's `+1` **wraps onto the
counter itself**, and POP 3 lands on the **word immediately below the context** -
and nothing below the context is written.

---

## 5. The first concrete non-stack effect

The handler makes **two calls and returns nothing to the VM**:

```
result = sub_0802BFBC(values[count-3], { values[count-2], values[count-1] })
sub_0801191A(*(0x08054FBC + 0x18), result)
```

**The second call is the observable engine effect**: it hands the first call's
result to an engine routine together with the object named by the table word at
`0x08054FBC + 0x18`, which is the IWRAM address **`0x03001C4C`** - the entry the
static-layout ticket recorded as the most heavily referenced object in the table.

Both callees are **declared, not reconstructed**, and are bound at their original
addresses, so nothing was lifted beyond this handler.

---

## 6. The comparison

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 64 | **64** |
| Instructions | 30 | **30** |
| Differing bytes in the overlap | - | 62 |
| Instruction spans byte-identical | - | **0** |

**The size and instruction count agree exactly, and that is still not a match** -
62 of the bytes differ, `byte_identical` is false, and a test asserts that the
equal sizes are not presented as a match.

Verdicts independent: **SEMANTIC PROVEN** (22 assertions, 0 failures),
**MODERN_BUILD PASS**, **ADS_MATCH BLOCKED**.

---

## 7. Proven, and unresolved

### Proven
Everything in sections 1 to 5.

### Unresolved
- what `sub_0802BFBC` computes from the three values;
- what `sub_0801191A` does with the object and the result;
- what the object at `0x03001C4C` is. **No semantic name is assigned** to it, to the
  handler, or to any operand, and nothing is imported from another title.

---

## 8. Regression status

All **thirteen** earlier reports are byte-identical; no `--defsym`; no ARM veneers;
correct Thumb symbol typing.

---

## 9. Limits

1. **One handler**, with both callees left black-box.
2. **`ADS_MATCH` remains BLOCKED.**
3. **The runtime capture is identity evidence only** and is scoped as such in the
   artifact and in the source.
4. **No name is invented** for the object, the handler or the operands.

---

## 10. Recommended next native-function family

1. **`sub_0801191A`**, the engine routine this handler drives with the `+0x18`
   object. Its caller's argument contract is now proven, so following it converts
   "drives the object" into "causes this effect" - the same step that paid off for
   the value consumer in the flag chain.
2. **`sub_0802BFBC`**, the three-value transform, whose arguments are now known
   exactly (a value plus a reversed two-element pair).
3. **The other native handlers that touch `+0x18`**, since that object is the most
   referenced in the table and this handler is a proven consumer of it.
4. **The remaining native entries with proven table slots**, lifting them one at a
   time against the same identity discipline used here.
