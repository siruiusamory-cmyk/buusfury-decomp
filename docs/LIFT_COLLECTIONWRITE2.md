# The second collection's writer (DECOMP-LIFT-COLLECTION-WRITE2-001)

**Status:** lifted and validated. The second collection's **write** path is proven;
its **insertion** path is not, and that is stated rather than glossed.
**Target:** `sub_080119BC` at `0x080119BC`, Thumb.
**Baseline:** `66f29cdc1e54382161ce0d81bc9fbd093dbb479f`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. The function

| | |
| --- | --- |
| Range | `0x080119BC..0x08011A1E` |
| Size | **98 bytes** |
| Instructions | **48** |
| Terminator | one, at `0x080119E8` |
| Callee | **`sub_0804FE54`** - the removal helper, bound at its original address |
| Literal | one, `0x0000040C` |

It sits **immediately after** the first-collection append `sub_0801191A`, but the two
are **separate routines**, not one routine at two offsets.

---

## 2. The exact write contract

```
sub_080119BC(object, key, value):
    i = find the element EQUAL TO key in the FIRST collection     (FORWARD from 0)
    if i >= 0:
        first.elements[i] = value            REPLACE in place, NO count change
    else:
        j = find the element EQUAL TO key in the SECOND collection (object + 0x40C)
        if j >= 0:
            sub_0804FE54(object + 0x408, j)  REMOVE from the second
        append value to the FIRST collection  and increment the FIRST count
```

| Question | Answer |
| --- | --- |
| count read/write | the **first** count is read and, on the append path only, incremented; the **second** count is read and **never** incremented here |
| element address | `collection + 0x08 + 4*i` for the first; `object + 0x410 + 4*i` for the second |
| insertion order | the value is appended at index `count` of the **first** collection |
| stored verbatim | **yes**, no transformation |
| capacity check | **none** |
| unchecked behaviour | a large count writes past any sane array end, as in the append routine |

**It is a KEYED MOVE ACROSS THE TWO COLLECTIONS.** The second collection is a writer
target **only through that removal**.

### The second collection is reached by a computed base, not a displacement

The `0x40C` literal is loaded into a register and then added with
**`adds r0, r0, r2`** - not an immediate add. Every access afterwards goes through
that register. **That is exactly why an image-wide search for stores at a
displacement near `0x40C` finds nothing.** It also explains the counts: `object +
0x40C` for the second count and `object + 0x410 + 4*i` for its elements, the shape
the reader `sub_08011C70` proved.

### Scan direction

Both scans run **FORWARD** from index 0, so the **first** element equal to the key
wins - the **opposite** direction from the reader's backward search.

---

## 3. Comparison with `sub_0801191A` - measured, not assumed

The two are adjacent, and **they are NOT structurally equivalent at different
offsets**. The difference was established from the *callers*, not from the symmetry:

| | `sub_0801191A` | `sub_080119BC` |
| --- | --- | --- |
| shape | **generic append** | **object-specific keyed move** |
| base | any collection base | hardcodes `0x40C`, knows **both** collections |
| callers' bases | **many different** - `*(r5+4)`, `*(r5)`, `*(r7+0xc)`, and the object | n/a |
| appends to the second | never | never |
| increments the second count | never | never |

The generic test **measures** this: it walks the reachable call graph, finds every
`BL` targeting `0x0801191A`, and asserts that the callers use **more than one
distinct base displacement**. If every caller passed the same object, the routine
would not be generic and the claim would be withdrawn.

**They are two members of ONE API FAMILY with DIFFERENT roles.**

---

## 4. The comparison

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 98 | 116 |
| Differing bytes in the overlap | - | 94 |
| Spans byte-identical | - | 0 |

`is_a_match_claim` is false. Verdicts independent: **SEMANTIC PROVEN** (21
assertions), **MODERN_BUILD PASS**, **ADS_MATCH BLOCKED**.

---

## 5. Proven, and unresolved

### Proven
Everything in section 2, plus the removal helper's identity and the callers' bases.

### Unresolved
- what the elements mean;
- what `sub_0804FE54` does beyond removing an entry, and whether it compacts;
- **what appends to the SECOND collection.** This routine only *removes* from it, so
  its **insertion path is still unfound** and is the next lead;
- the object's `+0x00` field, which this routine does **not** touch.

---

## 6. Two defects found and fixed during this ticket

1. **The derivation was wrong about the fold.** `second_collection_offset_folded_
   into_the_base` was computed by looking for an **immediate** add of `0x40C`, but
   the machine adds a **register** holding that literal, so the field reported
   `False` for something plainly true. The detector now follows the register.
2. **The prose describing that instruction was inaccurate**, claiming
   `adds r0, r0, #0x40C` where the code has `adds r0, r0, r2`. Corrected.

A third item is process rather than code: an earlier revision of the pytest wrapper
was **withdrawn rather than committed failing**, because four of its assertions did
not match the derivation's wording. It has since been rewritten against the strings
the derivation actually produces, and it passes - the fix was to read the real
values, not to weaken the checks.

---

## 7. Recommended next collection/object-family ticket

1. **The second collection's INSERTION path.** Nothing lifted so far appends to it,
   yet the reader searches it backward and this routine removes from it, so something
   must fill it. This is the single most valuable remaining question.
2. **`sub_0804FE54`**, the removal helper: does it compact, and does it touch either
   count beyond the second?
3. **The object's `+0x00` field**, untouched by every routine lifted so far.
4. **A capacity limit**, if one exists - nothing seen bounds either collection.
