# The second collection's insertion path (DECOMP-LIFT-COLLECTION-INSERT2-001)

**Status:** lifted and validated. **How elements get into the second collection is
now proven.**
**Target:** `sub_08011732` at `0x08011732`, Thumb.
**Baseline:** `70a4f56b7edb09a6cb9ffab0c640d8a2a5dfd08f`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. The function

| | |
| --- | --- |
| Range | `0x08011732..0x0801180A` |
| Size | **216 bytes** |
| Instructions | **97** |
| Terminator | one, at `0x08011808` |
| Literals | `0x0000040C`, `0x08072824` |
| Callees | `sub_080116FC`, `sub_080115B0`, `sub_0803DA62`, `sub_0804FE54`, and three indirect calls through the element's table |

## 2. The exact insertion contract

```
slot = second.count
second.count = slot + 1
second.elements[slot] = element        <-- the OLD count is the index
```

at `0x0801177E..0x0801178A`:

```
0x0801177E  ldr  r0, [sp, #8]     object + 0x40C, the second count slot
0x08011780  ldr  r1, [r0]         r1 = count2
0x08011782  adds r2, r1, #1
0x08011784  str  r2, [r0]         count2 = count2 + 1
0x08011786  lsls r1, r1, #2       r1 = OLD count2 * 4
0x08011788  adds r0, r1, r0
0x0801178A  str  r5, [r0, #4]     second.elements[old count2] = element
```

## 3. How it is reached - a verdict-driven migration

```
while (sub_080116FC(object) < arg2):
    for i = first.count-1 DOWN TO 0:
        verdict = element->table[+0x18](element, pass)
        if verdict == 1:  element->table[+0x04](element); REMOVE i from the FIRST
        if verdict == 2:  element->table[+0x1C](element)
                          APPEND to the SECOND       <-- the insertion
                          REMOVE i from the FIRST
        otherwise: leave it
    pass++
sub_080115B0(object); read the global; sub_0803DA62(...)
for each element of the THIRD collection: element->table[+0x14](element)
third.count = 0                       <-- the third collection is FLUSHED
```

**The second collection is filled by a migration out of the first, and the element is
MOVED, not copied**: the removal at `0x0801178C..0x08011790` uses the same index the
loop is on, so the element exists in exactly one of the two collections afterwards.

## 4. Answers to the ticket's questions

| Question | Answer |
| --- | --- |
| insertion / replace / move | **move**: insert into the second **and** remove from the first |
| count semantics | the second count is read, incremented, and the **old** value used as the index |
| element width | 32-bit pointers to virtual objects |
| stored verbatim | **yes** |
| is the first collection consulted | **yes, it is the source** - it is scanned and the element is taken from it |
| ordering | the inner loop runs **BACKWARD**; the append goes to the **tail** of the second |
| duplicate handling | **NONE**. No comparison against the second collection's contents exists, so the same element can be appended twice and duplicates are **not** prevented here |
| capacity checks | **none** |
| wrap/overflow | an arbitrarily large second count writes past any sane array end, as in the first append |

## 5. Interaction with the first collection

Proven sequence for a verdict of 2:

1. `element = first.elements[i]`
2. `element->table[+0x1C](element)`
3. `slot = second.count`; `second.count = slot + 1`; `second.elements[slot] = element`
4. `sub_0804FE54(first.count_slot, i)`

**This is the exact inverse of `sub_080119BC`**, which moves an element from the
second collection to the first when a key is found. Together they are the two
directions of one migration.

## 6. The removal helper's argument - and a correction to an earlier note

`sub_0804FE54` receives a pointer to the **COUNT SLOT**, not the collection base.
This routine proves it: it passes `r7`, which it set to `object + 4`, for the first
collection whose base is `object + 0`.

By the same convention the call in `sub_080119BC` is
**`sub_0804FE54(object + 0x40C, index)`**. An earlier note of ours said
`object + 0x408`; that was **wrong** and is corrected in
[lift_targets.json](../config/lift_targets.json).

**This is the one previous report that intentionally changes** -
[lift_collectionwrite2.json](../config/lift_collectionwrite2.json) - because its
embedded note carried that error. The other sixteen are byte-identical.

## 7. Capacity, `+0x00`, and a third collection

- **Capacity evidence:** none. Nothing compares the second count against a limit.
- **`+0x00`:** **not touched** by this routine either.
- **A THIRD COLLECTION EXISTS AT `object + 0x208`**: its count is at `+0x208` and its
  elements from `+0x20C`. This routine calls `table[+0x14]` on each of its elements
  and then **sets its count to zero**, so it is flushed rather than migrated.

## 8. The comparison

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 216 | 296 |
| Differing bytes in the overlap | - | 212 |
| Spans byte-identical | - | 0 |

`is_a_match_claim` is false. Verdicts independent: **SEMANTIC PROVEN** (27
assertions), **MODERN_BUILD PASS**, **ADS_MATCH BLOCKED**.

## 9. Defects found while lifting this

1. **The removal mock was wrong**, adding 4 to the pointer it received. Because this
   routine passes the **count slot**, the mock wrote into the elements area and made
   the routine dereference a garbage element pointer. Fixing the mock is what proved
   the argument convention and exposed the earlier note's error.
2. **The host redirect macro was never defined** by the self-check, so the routine
   still dereferenced the unmapped ROM address `0x08072824`. The crash took several
   probes to locate and is now guarded by an explicit `#define`.
3. **The virtual-call helpers used pointer arithmetic.** The table offsets in this
   image are large negative values, so `(u8 *)table + offset` was pointer-overflow;
   the add is now expressed in the same 32-bit wrapping arithmetic the instruction
   performs.

## 10. Recommended next collection-family ticket

1. **What fills the THIRD collection at `object + 0x208`.** It is flushed here and
   nothing lifted so far appends to it.
2. **What verdicts 1 and 2 mean** beyond their effect, and what `sub_080116FC`
   returns - it gates the entire scan.
3. **`sub_0804FE54`** itself: does it compact?
4. **The object's `+0x00` field**, still untouched by every routine lifted so far.
5. **A capacity limit**, if one exists - nothing seen bounds any of the three
   collections.
