# What the materialised boolean controls (DECOMP-LIFT-SCRIPT-BOOLUSE-001)

**Status:** the materialised boolean's first concrete consequence is proven. The
chain `script byte -> push -> arithmetic -> consumer -> effect -> reader ->
materialised boolean -> bit selection` is closed.
**Targets:** `sub_080007B6` and `sub_080007CC`, Thumb, at `0x080007B6`.
**Baseline:** `75f766039c58a1e0ad2d70964ebb8248bf1f582a`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, still independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | the in-place replacement, the inverted variant, the unchanged counter and the empty-stack case, checked by RUNNING them: 17 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | they compile, link at `0x080007B6` and emit bytes: 72 bytes |
| **ADS_MATCH** | **BLOCKED** | whether they reproduce the original compiler: `ADS12_LICENSE_UNAVAILABLE` |

No match is claimed.

---

## 2. The destination slot, proven

The two sites the previous ticket found are the bodies of two adjacent routines:

| Routine | Extent | Size | Instructions | Terminator |
| --- | --- | --- | --- | --- |
| `sub_080007B6` | `0x080007B6..0x080007CC` | 22 B | 10 | `0x080007CA` |
| `sub_080007CC` | `0x080007CC..0x080007E6` | 26 B | 12 | `0x080007E4` |

Both compute their destination identically:

```
ldr  r1, [r0]        r1 = context+0x00, the COUNTER
lsls r1, r1, #2      r1 = count * 4
adds r4, r1, r0      r4 = context + count*4
```

and the value stack holds `values[i]` at `context + 4 + 4*i`, so

```
context + count*4  ==  context + 4 + 4*(count-1)  ==  values[count-1]
```

**Both sites write the SAME VM stack location: `values[count-1]`, the TOP of the
value stack.** It is not a separate word, and the two sites do not differ.

### It is an in-place replacement, not a pop

Neither routine stores to `context+0x00`, so the **counter is unchanged**. The
derivation asserts this by comparing the *base register* of every store against
the register the counter was loaded through, not merely the displacement: an
earlier revision counted the slot store `str r0,[r4]` as a counter write because
its displacement is also zero.

---

## 3. The two routines

```
0x080007B6  push {r4, lr}
0x080007B8  ldr  r1, [r0]           r1 = the counter
0x080007BA  lsls r1, r1, #2
0x080007BC  adds r4, r1, r0         r4 = context + count*4 = values[count-1]
0x080007BE  ldr  r0, [pc, #0x118]   r0 = 0x08054FBC
0x080007C0  ldr  r1, [r4]           r1 = *top
0x080007C2  ldr  r0, [r0, #0x14]    r0 = *(0x08054FBC + 0x14)
0x080007C4  bl   0x08004364         flag = test(r0, r1)
0x080007C8  str  r0, [r4]           *top = flag
0x080007CA  pop  {r4, pc}

0x080007CC  push {r4, lr}
0x080007CE  ldr  r1, [r0]
0x080007D0  lsls r1, r1, #2
0x080007D2  adds r4, r1, r0
0x080007D4  ldr  r0, [pc, #0x100]
0x080007D6  ldr  r1, [r4]
0x080007D8  ldr  r0, [r0, #0x14]
0x080007DA  bl   0x08004364         flag = test(r0, r1)
0x080007DE  movs r1, #1
0x080007E0  subs r0, r1, r0         r0 = 1 - flag
0x080007E2  str  r0, [r4]           *top = 1 - flag
0x080007E4  pop  {r4, pc}
```

So the first stores the flag and the second stores **its exact inverse**. Both
return what they stored, both make one call to the already-lifted reader
`sub_08004364`, and both load the same single literal. Neither reads `r1`.

### Empty stack: the counter word is the slot

With a counter of zero the address is `context + 0`, so `r4` points at the
**counter itself**: the word read is the counter and the store **replaces the
counter with the flag**. Nothing is popped, and there is no check. **No guard was
added.**

---

## 4. The first concrete engine consequence

The consumer lifted two tickets ago, `sub_080007E6`, **begins immediately after
these two** at `0x080007E6`. It pops `values[count-1]` and passes it to
`sub_08004380`, which sets bit `(value & 7)` of the byte at
`base + (value >> 3) + 0x55`.

Chained:

```
unary transform  ->  values[count-1] becomes the boolean 0 or 1
sub_080007E6     ->  pops it and passes it as sub_08004380's `value`
sub_08004380     ->  sets bit (value & 7) of byte base + (value >> 3) + 0x55
```

With a boolean input the index is 0 or 1, so:

```
THE BOOLEAN SELECTS WHICH BIT IS SET in the first byte of the flag array
    false  ->  bit 0
    true   ->  bit 1
```

**The materialised boolean is used as a BIT INDEX, not as a truth value, by the
first consumer downstream of it.** That is its first concrete engine behaviour,
and it is proven by composing three already-verified units rather than by reading
a new one.

---

## 5. Proven, and unresolved

### Proven

Everything in sections 2 to 4, plus: the two routines are adjacent with no gap;
their upper boundary is confirmed by the already-lifted consumer starting exactly
where they end; the two call sites this ticket derives are the same two the
`flagread` report derived from the other direction, so the two reports agree; the
second routine is the exact inverse of the first over all eight bit positions; no
input can leave anything but 0 or 1 in the slot.

### Unresolved

- **what either bit means.** No semantic name is assigned to bit 0, bit 1, the
  array, or the object, and nothing is imported from another title;
- whether callers rely on the counter being untouched;
- **what reads the array afterwards**;
- the array's size, so which values are in range is unknown.

---

## 6. The comparison

Artifact: `config/lift_booluse.json`.

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 48 | 72 |
| Differing bytes in the overlap | - | 42 |
| Instruction spans keyed on the original's boundaries | 22 | - |
| Spans byte-identical | - | 1 |
| Calls / literals per routine | 1 / 1 | 1 / 1 |

`is_a_match_claim` is false. The reader call is bound to its original address
`0x08004364`.

---

## 7. Regression status

- **all nine earlier reports byte-identical** - `git diff` on their report files
  is empty;
- no `--defsym`, no ARM veneers, correct Thumb symbol typing.

---

## 8. Limits

1. **The consequence is proven by composition**, through three already-verified
   units. No new downstream reader was opened.
2. **The meaning of either bit remains unknown** and is deliberately not guessed.
3. **`ADS_MATCH` remains BLOCKED.**
4. **The third call site of the reader, `0x080032EE`, is untouched**, as is the
   clearer at `0x08004396`.

---

## 9. Recommended next function

1. **The clearer at `0x08004396`** (22 bytes, `bics` + `strb`) would complete the
   accessor trio and is already bounded.
2. **The reader of the array's byte 0**, now known to hold two meaningful bits at
   positions 0 and 1. Finding what tests them would turn "bit 0 or bit 1 is set"
   into the engine behaviour they record - the last link.
3. **The third reader call site `0x080032EE`**, which already looks like a
   bit-gather loop and may reveal how the array is consumed in bulk.
4. **Native slot 178 at `0x08003030`.**
