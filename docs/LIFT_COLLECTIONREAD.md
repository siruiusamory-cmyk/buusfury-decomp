# The collection reader (DECOMP-LIFT-COLLECTION-READ-001)

**Status:** lifted and validated. The first concrete reader of the collection the
append routine fills is found, and an element's first non-collection use is proven.
**Target:** `sub_08011C70` at `0x08011C70`, Thumb.
**Baseline:** `cefdb2d5189a33569999c5db459d3508a6157ce4`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. How it was found

The object is **not reachable as a literal**: a search for the address `0x03001C4C`
as a load literal in reachable code found **nothing**. It is reached **through the
table**, as `*(0x08054FBC + 0x18)`. Following that route produced a census of **21
functions** that reach the object; the strongest reader was selected from it.

## 2. The function

| | |
| --- | --- |
| Range | `0x08011C70..0x08011CCA` |
| Size | **90 bytes** |
| Instructions | **44** |
| Terminator | one, at `0x08011CC8` |
| Caller | called **with the object in `r0`**, from `0x08001E1E` among others |
| Callee | the virtual method, reached through the `bx r3` thunk at `0x08046AA6` |

## 3. The concrete effect: a virtual-dispatch search

```
for i = count-1 DOWN TO 0:
    element = *(collection + 8 + 4*i)
    table   = *(u32*)element          the element's FIRST WORD
    method  = table + table[9]        table + 0x24
    if method(a, b) != 0:  return that value
return 0
```

Then the **same search over a second collection**.

## 4. Traversal semantics

| Property | Proven |
| --- | --- |
| count interpretation | `u32` count at `collection + 0x04` |
| traversal order | **BACKWARD**, from `count-1` down to 0 - the **most recently appended element is tested first** |
| element width | **32-bit pointers** |
| elements | each is a **pointer to a virtual object** whose **first word** points at a dispatch table |
| method | at **`table + 0x24`** |
| transformed? | no - the two incoming arguments are **forwarded unchanged** |
| stop rule | the **first non-zero** result is returned **immediately** |
| count changes | **none** - the count is read only |
| count 0 | the index goes to `-1` and the `bmi` **skips the loop**, so **no call at all** |

## 5. Object-relative accesses and capacity evidence

The collection layout is now proven a **third time, from different instructions**:
count at `+0x04`, elements from `+0x08`.

**Capacity evidence, found here and NOT inferred from adjacency:** the routine
searches a **SECOND collection of the same shape at `object + 0x408`** - its count is
at `object + 0x40C` and its elements from `object + 0x410`, because the routine adds
`0x40C` to the object base and then reads the count from that address.

**The object therefore carries TWO collections, `0x408` bytes apart.**

**`+0x00` is not touched** by this reader.

## 6. The virtual call

The original reaches the method through the **`bx r3` thunk at `0x08046AA6`**, a
trampoline the original toolchain emitted for an indirect call. The reconstruction
expresses the same operation as a plain call through a function pointer - which is
what the trampoline achieves - so **no external symbol is introduced**.

**No bounds check** on the count and **no null check** on an element. None was added.

## 7. The comparison

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 90 | 108 |
| Differing bytes in the overlap | - | 86 |
| Spans byte-identical | - | 1 |

`is_a_match_claim` is false. Verdicts independent: **SEMANTIC PROVEN** (23
assertions), **MODERN_BUILD PASS**, **ADS_MATCH BLOCKED**.

---

## 8. Proven, and unresolved

### Proven
Everything above, plus the count-is-read-only fact and the empty-collection skip.

### Unresolved
- what the collection holds, and what the element type or the method is;
- how large either collection may grow - nothing bounds either;
- what the object's `+0x00` field is. **No semantic name is assigned** to the
  collection, the element type or the method, and nothing is imported.

---

## 9. A test bug worth recording

The first revision of the host check tracked **call order** and silently treated it
as the **element index**, which made two traversal assertions wrong. It was rewritten
so each fake element carries **its own method**, making element identity observable
rather than inferred. The same revision also set a collection's **count without
placing its elements**, so the search dereferenced a null element and crashed; both
the code shape and the test now state that a count must have elements behind it.

---

## 10. Recommended next collection/object family

1. **The second collection's writer.** The reader proves two collections exist; the
   append routine only writes the first, so what fills `object + 0x408` is unknown
   and is the natural next target.
2. **The element type.** Elements are virtual objects; mapping the table's other
   offsets would identify the method called at `+0x24` and its siblings.
3. **The object's `+0x00` field**, still untouched by every routine lifted so far.
4. **A capacity limit**, if one exists: neither collection is bounded by anything
   seen, so if a limit exists it belongs to the owner.
