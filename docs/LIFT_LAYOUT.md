# The flag array's extent (DECOMP-FLAGSTATE-LAYOUT-001)

**Result: option B, honest bounds.** The array's start is proven, a lower bound is
proven, and **no upper bound is derivable** from code evidence.
**Baseline:** `0117178985ef4fe05b9b38ed54dcaa8fb022c88a`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

**No routine was lifted and no lift report was added or changed.** The evidence
comes from the five routines already lifted plus an image-wide search for the
object's constructor. All thirteen reports are byte-identical.

---

## 1. Array start: PROVEN, `base + 0x55`

| Routine | Entry | Size | Computes the index arithmetic? | Reaches the array through |
| --- | --- | --- | --- | --- |
| test | `0x08004364` | 28 B | **yes** | own arithmetic |
| set | `0x08004380` | 22 B | **yes** | own arithmetic |
| clear | `0x08004396` | 22 B | **yes** | own arithmetic |
| gather | `0x080032C2` | 78 B | no | `sub_08004364` |
| apply-mask | `0x08003310` | 86 B | no | `sub_08004380` / `sub_08004396` |

The **three accessors independently compute** `base + (value >> 3) + 0x50` and then
use field displacement `+5`, so all three agree the first byte is at `base + 0x55`.
The gather and the apply-mask routine do **no** index arithmetic of their own; they
reach the array only *through* the accessors, so they add no independent evidence
of the start.

| Property | Value |
| --- | --- |
| Entry size | **1 byte** |
| Byte index | `value >> 3`, **arithmetic** |
| Bit index | `value & 7` |
| Bits per byte | 8 |
| **Alignment** | **byte-aligned; `+0x55` is an ODD offset, so the array is NOT word-aligned** |

### Neighbouring offsets

| Side | Offset | Status |
| --- | --- | --- |
| below | `base + 0x54` | reached only when a value with bit 31 set sign-extends the byte index to `-1`; the code does **not** treat it as part of the array |
| above | **none identified** | nothing establishes where the array ends |

---

## 2. Bounds

| | Value | Evidence |
| --- | --- | --- |
| **Lower bound** | **1 byte / 8 bits** | bits 0 and 1 are demonstrably **both used**: the two boolean-transforming routines store the reader's result (0 or 1), and the apply-mask routine then SETs or CLEARs the flag at that same index, so byte 0 is written with bit 0 and bit 1 as live values |
| **Upper bound** | **not derivable** | no instruction in any of the five routines compares an index, an offset or a width against a size, so nothing in the code establishes the array's end |
| **Object minimum size** | **0x56 bytes** | the array's first byte is at `base + 0x55` |

---

## 3. The index-range question: NO constraint is proven

The five routines have **no runtime bounds check**, and that absence does **not**
rest on a proven externally constrained index range:

- the **test, set and clear** accessors pass the index straight into the shift;
- the **gather** takes its `offset` and `bound` from the VM stack and clamps
  neither;
- the **apply-mask** routine clamps the **mask** to the width, but that is a clamp
  on the *data*, **not** on `offset + width` against the array.

**No constraint was found, and none should be inferred.**

---

## 4. Constructor search: none found

The object is `*(0x08054FBC + 0x14)`. An image-wide search for any code that
**stores** that pointer used the shape

```
ldr rX, [pc, #N]        ; literal == 0x08054FBC
<within 3 instructions> ldr/str ... [rX, #0x14]
```

| Result | Count |
| --- | --- |
| readers of `+0x14` found | **60** |
| **writers of `+0x14` found** | **0** |

**The allocation size is therefore not recoverable from this evidence.** The object
may be constructed by a path this shape does not match, for example one that keeps
the global base in a register across the store, or one reached only from startup.

No initialisation loop, copy loop or serialisation code over the object was found
either.

---

## 5. The exact missing evidence

1. the object's **allocation**, which would fix an upper bound directly;
2. a **memset or copy length** over the object;
3. a **reader** that indexes the array with a constant or with a bounded loop;
4. any **comparison** of an index or width against an array length.

---

## 6. Regression status

- **no lift report changed** - this ticket adds no target, so all thirteen reports
  regenerate byte-identically;
- the `clear` report's embedded gather derivation was **not** refactored, as the
  ticket directed;
- no `--defsym`, no ARM veneers, correct Thumb symbol typing.

---

## 7. Limits

1. **Bounds, not a size.** The upper bound is not merely unproven, it is not
   derivable from the evidence gathered here.
2. **One search shape** for the constructor. A second shape was not tried.
3. **The object's semantic name is deliberately not guessed.**
4. **Adjacent fields inside `base + 0x00 .. base + 0x54` were not mapped.** The
   accessors only ever name `+0x50` and `+5`; surrounding offsets would need the
   object's other users, which this ticket did not chase.

---

## 8. Recommended next subsystem batch

1. **The object's other users.** 60 sites read `*(0x08054FBC + 0x14)`; mapping the
   offsets they touch would give the neighbouring fields and a true object size,
   and would likely find the constructor by a second route.
2. **A bounded reader of the array**, if one exists, which would fix the upper
   bound directly.
3. **The object's allocation** by searching for a second constructor shape, in
   particular one where the global base stays in a register.
4. **Native slot 178 at `0x08003030`.**
