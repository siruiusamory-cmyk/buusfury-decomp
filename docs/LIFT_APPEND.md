# DECOMP-LIFT-NATIVE178-EFFECT-001 - the object append

**Status:** lifted and validated. The first concrete effect of the chain that starts
at native slot 178 is established.
**Target:** `sub_0801191A` at `0x0801191A`, Thumb.
**Baseline:** `5b101dbadc8aa89d0d729750f184b87462b6fca1`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. The function

| | |
| --- | --- |
| Range | `0x0801191A..0x0801192C` |
| Size | **18 bytes** |
| Instructions | **9** |
| Terminator | one, at `0x0801192A` (`bx lr`) |
| Calls | **none** |
| Literal pool | **none** |
| Caller | **native dispatch slot 178** at `0x08003068` |

**A leaf**: no calls and no literal pool, so **no helper had to be followed** and the
effect is established by this routine alone.

```
0x0801191A  adds r0, #4        r0 = object + 4
0x0801191C  adds r2, r1, #0    r2 = the incoming value
0x0801191E  ldr  r1, [r0]      r1 = *(object + 4)      <- THE COUNT
0x08011920  adds r3, r1, #1
0x08011922  str  r3, [r0]      *(object + 4) = count + 1
0x08011924  lsls r1, r1, #2    r1 = count * 4
0x08011926  adds r0, r1, r0    r0 = (object + 4) + count*4
0x08011928  str  r2, [r0, #4]  *(object + 8 + 4*count) = value
0x0801192A  bx   lr
```

---

## 2. The concrete effect

The object carries a **32-bit COUNT at `+0x04`** and an **array of 32-bit values
beginning at `+0x08`**. The routine

> **APPENDS the incoming value at index `count`, then increments that count.**

```
((u32 *)object)[1] = ((u32 *)object)[1] + 1;        the count at +0x04
*(u32 *)(object + 8 + 4*count) = value;             the element at +0x08+4*i
```

The count is **read before** it is incremented, so element `count` is written, not
element `count+1`.

**This is the first concrete effect of the chain from native slot 178:** that handler
pops three VM values, computes one from them, and hands it here, where it is
**appended** to the object's array. The object is a **growable-by-write collection**
rather than a scalar, and slot 178 is a producer for it.

---

## 3. Object-relative accesses, all of them

| Offset | Width | Access |
| --- | --- | --- |
| `+0x04` | 32 | **read** - the count |
| `+0x04` | 32 | **written** - the count, incremented |
| `+0x08 + 4*count` | 32 | **written** - the appended element |
| `+0x00` | - | **NOT TOUCHED.** Neither read nor written |

There is no other access in the routine.

**Order:** the count is loaded first, stored back incremented second, and only then
is the element written; both complete before the routine returns and nothing
interrupts them.

### There is no capacity check
Nothing compares the count against a limit, and no capacity is reachable from this
routine. A large count writes far past any sane array end. **Reproduced, not
guarded.** The self-check pins the extreme: at a count of `0xFFFFFFFF` the element
address **wraps onto the count slot itself**, so the appended value overwrites the
count.

### The return value is not defined
The routine ends with `bx lr` with `r0` holding the address of the element it just
wrote - not a status and not a boolean - so the reconstruction returns `void` rather
than inventing a result.

---

## 4. The incoming contract, re-proven from the caller

Native slot 178 calls this at `0x08003068` with

```
r0 = *(0x08054FBC + 0x18)  ->  0x03001C4C   (the static layout's most referenced object)
r1 = the value returned by sub_0802BFBC
```

which is exactly how this routine reads them.

---

## 5. The comparison

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 18 | 14 |
| Differing bytes in the overlap | - | 13 |
| Spans byte-identical | - | 0 |
| Calls / literals | 0 / 0 | 0 / 0 |

`is_a_match_claim` is false. Verdicts independent: **SEMANTIC PROVEN** (15 assertions,
0 failures), **MODERN_BUILD PASS**, **ADS_MATCH BLOCKED**.

---

## 6. Proven, and unresolved

### Proven
Everything in sections 1 to 4.

### Unresolved
- what the object at `0x03001C4C` is, and what its `+0x00` field means;
- what the appended values are used for, and who reads them;
- whether a capacity limit exists elsewhere. **No semantic name is assigned** to the
  object, the array or the count, and nothing is imported from another title.

---

## 7. Regression status

All **fourteen** earlier reports are byte-identical; no `--defsym`; no ARM veneers;
correct Thumb symbol typing.

---

## 8. A build bug worth recording

The first revision of the source **nested `/* +0x04 */` inside a `/* ... */` block
comment**, which closed the comment early and produced a wall of syntax errors in the
host build. Replaced with plain text, and a test now asserts the file's leading block
comment contains exactly one `/*` so the mistake cannot recur silently.

---

## 9. Recommended next `0x03001C4C` object family

1. **The reader of the array.** The count at `+0x04` and values from `+0x08` are
   written here; finding what consumes them converts "values are appended" into what
   the collection is *for*.
2. **The object's `+0x00` field**, which this routine never touches - it is the
   object's other half and the natural next field to map.
3. **A capacity limit**, if one exists elsewhere; nothing here enforces one, so if a
   bound exists it is the readers' or the object's owner's responsibility.
4. **`sub_0802BFBC`**, the three-value transform that produces what gets appended.
