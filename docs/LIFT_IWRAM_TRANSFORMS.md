# The IWRAM block's byte-lane and Q-format transform families

Ticket: **DECOMP-IWRAM-TRANSFORMS-001**. Baseline `307186b1b1be41711d6a5cc8a6f2a3fbf4355f2a`.

This document records what two coherent mathematical families inside the
4100-byte runtime-installed IWRAM block are, proves each operation from the
cartridge, and says which parts are **not** proven. It is the third pass over
the same block: [`LIFT_IWRAM_RUNTIME.md`](LIFT_IWRAM_RUNTIME.md) established the
copy mechanism and lifted the four block-memory routines,
[`LIFT_IWRAM_DISPATCH.md`](LIFT_IWRAM_DISPATCH.md) lifted the interrupt
dispatcher and classified every function mechanically. This one lifts the two
families that classification put at the top of its own "next batch" list.

Every number here is regenerated on demand by `tools/buusfury/lift.py` and
carried, whole, inside `config/lift_iwrambl.json`,
`config/lift_iwramblsparse.json` and `config/lift_iwramqf.json`. Nothing is
hand-written prose that could drift from the image.

## 1. The address mapping, restated once

Unchanged from the previous two tickets:

    IWRAM X = ROM 0x087B79A4 + (X - 0x03000000)

because the reset routine programs DMA3 a second time with SAD `0x087B79A4`,
DAD `0x03000000` and CNT `0x84000401` - 1025 words, a verbatim copy. The code
half ends at `0x03000F44`; `0x03000F44..0x03001004` is a 192-byte data tail.

## 2. What this ticket lifted

| target | ROM | IWRAM | bytes | insns | verdict |
| --- | --- | --- | ---: | ---: | --- |
| `iwrambl` | `0x087B7C80..0x087B7CCC` | `0x030002DC` | 76 | 19 | SEMANTIC PROVEN, MODERN_BUILD PASS, ADS BLOCKED |
| `iwramblsparse` | `0x087B7CD4..0x087B7D2C` | `0x03000330` | 88 | 22 | SEMANTIC PROVEN, MODERN_BUILD PASS, ADS BLOCKED |
| `iwramqf` (member 1) | `0x087B7F04..0x087B80A4` | `0x03000560` | 416 | 104 | SEMANTIC PROVEN, MODERN_BUILD PASS, ADS BLOCKED |
| `iwramqf` (member 2) | `0x087B80A4..0x087B810C` | `0x03000700` | 104 | 26 | SEMANTIC PROVEN, MODERN_BUILD PASS, ADS BLOCKED |

Four addresses, but **not** four independent lifts: the ticket's question is what
reusable operations they represent, and the answer is one reduction idiom shared
by three of them plus one four-byte-stride lane idiom shared by two.

None of the five routines loads a literal, so no unit declares a pool and the
pool test is **not applicable** rather than failed.

## 3. The byte-lane family: two variants, not an inverse pair

### 3.1 `0x087B7C80` - the table transform

```
r0 = destination, r1 = source, r2 = 256-byte table, r3 = count IN BYTES
T(x) = (x == 0) ? 0 : table[x]                    # table[0] is NEVER read
out.lane k = T(in.lane k)   for k = 0..3, lane map the IDENTITY
stride 4 bytes; the `str` is unconditional, only the table reads are predicated
```

The lane mask is `mov ip, #0xff` (imm8 `0xFF`, no rotation). Each lane is
extracted with `ands rX, ip, rM, lsr #N` for N = 24, 16, 8 and the unshifted
form for lane 0, and the following `ldrbne` is **predicated on the Z flag that
`ands` just set**. So a zero lane does not read the table at all - not even
`table[0]`. That is a fact about the instruction sequence, not an optimisation:
it is why the routine is a *substitution with a fixed point at zero* rather than
a plain byte substitution.

**No table can turn this into `0x087B7CD4`'s inverse**, and the reason is worth
stating precisely because the obvious guess is that the two are a pair:

* the only composite identity is trivial - with `table[i] = i` for `i` in
  `1..255`, this routine is the identity word map, so running the other one over
  its output reproduces the source *because this one did nothing*;
* the other routine is **not injective**: its destination window is fixed by the
  byte count and not by the data, so distinct sources collapse to the same
  destination. Measured, not argued: eight different source words driven at a
  three-word count produce a repeated destination word.

The three call sites all pass the **same** 256-byte ROM table at `0x0805672C`,
which occurs exactly once in the whole image as a word (at `0x08030F30`, the
literal slot the `0x08030EBC` call site loads):

| call site | veneer | arguments |
| --- | --- | --- |
| `0x08030EBC` | `0x0804918C` | r0 = r1 = a stack address, r2 = `0x0805672C`, r3 = a rectangle product |
| `0x0803D99C` | `0x0804918C` | r0 = r1 = a record's field, r2 = `0x0805672C`, r3 = another field |
| `0x0803F9FA` | `0x0804918C` | r0 = r1 = a row base, r2 = `0x0805672C`, r3 = a width |

`r0 == r1` at all three, so the operation is performed **in place**. The table
is not the identity, and it is not a bijection either: three of its 256 entries
hold `0xFF`. **What the table means is UNKNOWN**: no compression, container or
opcode meaning is imported from another title, and the table's own structure has
not been proven. It is recorded as a 256-byte byte map at `0x0805672C` and
nothing more.

### 3.2 `0x087B7CD4` - the sparse masked store

```
r0 = context record: +0x24 = destination BYTE ADDRESS, +0x30 = byte count (SIGNED)
r1 = source
if the word is zero: store nothing        # `cmp r3, #0` / `beq`
otherwise: for k in 0..3, if lane k is non-zero, destination[k] = lane k
destination += 4 PER SOURCE WORD, whether or not anything was written
```

The destination is decremented by four **before** the loop and incremented by
four at the top of every pass, so the first word it writes lands exactly on the
address the record names. The advance is unconditional, which is what makes this
a *sparse masked store* and not a compaction: reading "sparse" as "compacting"
is the obvious wrong reading and is refuted by the `add r0, r0, #4` that
precedes the zero test.

Two boundary behaviours are **reproduced, not repaired**:

* the count test is **signed**. `subs r2, r2, #4` followed by `bmi` (word
  `0x4A00000C`, condition field `0100` = MI) is an **N** test, not a C test. The
  decrement happens once *before* the loop and once at the end of each pass, so
  a count at or above four yields exactly `count/4` passes and a count below four
  yields **none**. A count of five or six does **not** round up;
* the wrap boundary is `0x80000004`, not the sign bit: `0x80000004 - 4` is
  negative after the pre-loop `subs` and the routine does nothing, while
  `0x80000000 - 4 = 0x7FFFFFFC` is positive.

An earlier reading of `0x087B7C80` had the counter decremented to zero with the
exit at the top of the body, which would have made its pass count `r3` rather
than `r3/4`. The instruction order settles it: the body is 14 instructions, the
`subs` is the last but two, and the `bne` targets the load at `+0x8`.

### 3.3 The relationship, proven

They are **variants of one four-byte-stride byte-lane transform**. Not inverses,
not a pack/unpack pair, not byte permutations. What they share is mechanical and
exact:

* a four-byte stride and a `0xFF` lane mask applied by `ands`;
* the same "byte 0 is special" idiom - `ands` sets Z and the very next
  instruction is predicated on it, one skipping the table **read** and the other
  skipping the **store**;
* all lane extractions are LSR or the unshifted form: **no ASR, no ROR** anywhere
  in either body, so neither sign-extends and neither rotates;
* both lane maps are the **identity**, so neither permutes bytes.

### 3.4 The extents, and a correction the ticket's own brief needed

`0x087B7C80` is **76 bytes and 19 instructions**, ending at the `bx lr` at IWRAM
`0x03000324`. The brief called the entry-to-next-entry window 84 bytes / 21
instructions. That is wrong, and it is wrong in exactly the way
[`LIFT_LOOP.md`](LIFT_LOOP.md) forbids: the eight bytes at IWRAM
`0x03000328`/`0x0300032C` (`0x000037FF`, `0x0000027F`) are a literal pool, and
they belong to the routine **preceding** this one. Exactly two instructions in
the whole block read them:

```
0x03000230  E59F80F0  ldr r8, [pc, #0xf0]   -> 0x087B7CCC = 0x03000328
0x03000240  E59F80E4  ldr r8, [pc, #0xe4]   -> 0x087B7CD0 = 0x0300032C
```

and both lie inside the 149-word routine at `0x03000040`. Decoded as code the two
words read `strdeq r3,r4,[r0],-pc` and `andeq r0,r0,pc,ror r2`. So the block's
layout is

    [0x03000040 .. 0x030002D8][pool 0x03000328..0x03000330][0x03000330 .. 0x03000388]

and **no single contiguous translation unit contains both byte-lane
transforms**. That is why they are two targets and not one.

The four bytes `0x0300032C..0x03000330` are alignment padding between the pool
and the next entry, so the pool-provenance correction does not by itself move any
boundary: the unit's extent is its own last instruction, and the padding is
reported rather than declared.

## 4. The Q-format family: one reduction, two different computations

### 4.1 The reduction, and a claim this ticket got wrong three times

Both `0x087B7F04` and `0x087B80A4` accumulate signed 32x32 products into 64 bits
with `smull`/`smlal` and then reduce with

```
lsr rD, RO, #10            low word of the sum, LOGICAL right shift
add rD, rD, RH, lsl #22    high word, shifted up by 22
```

For **every** 64-bit pattern this is exactly `(u32)(((u64)sum) >> 10)`: the high
word contributes its low 22 bits at result bits 22..43, of which 32..43 are
truncated, and bits 10..31 of the low word land at result bits 0..21. That is an
identity, not an approximation, and the self-check now asserts it as one.

It is **also** identical to an arithmetic shift truncated the same way,
`(u32)(((s64)sum) >> 10)`, because an `asr` differs from an `lsr` only in the
bits it shifts *in* at the top, and after truncation to 32 bits those are all
above bit 31. **This ticket asserted a difference between the two forms three
times - in a source comment, in the JSON notes and in the self-check - and was
wrong every time.** The source comment claiming `lsr` was "load-bearing" has
been corrected, because a wrong reason is as bad as a wrong value. What survives
is the contract: the reduction **discards ten bits**, with no rounding term (no
`+0x200` anywhere in either routine) and no saturation instruction.

The idiom appears in two spellings and **both must be recognised** or a pattern
scan under-counts the family:

| spelling | form | where |
| --- | --- | --- |
| standalone | `lsr rD, RO, #10` then `add rD, rD, RH, lsl #22` | `0x087B7F04` x9 |
| folded | `add rD, ACC, RO, lsr #10` then `add rD, rD, RH, lsl #22` | `0x087B7F04` x3, `0x087B80A4` x3 |

A scan keyed on the folded form alone finds 3 of `0x087B7F04`'s 12 reductions.
The nine standalone ones are at `+0xA4/+0x108` groups; the three folded ones are
its **last** group only, at `0x030006C8`/`0x030006CC`/`0x030006D0` with their
`lsl #22` partners at `0x030006D4`/`D8`/`DC`.

### 4.2 The two routines are **not** the same operation

This is the question the ticket exists to settle, and the answer is measured.

**`0x087B80A4`** - three-term product, reduced once:

```
r0 = destination (3 words, `stm r0, {r4,r5,r6}`, NO writeback)
r1 = three vector words
r2 = twelve words: a 3x3 matrix at +0..+0x23, then the bias vector at +0x24
a[k] = r1[4k]; M[k][j] = r2[12k+4j] row-major; b[j] = r2[36+4j]
out[j] = b[j] + (u32)(((s64)a0*M0j + (s64)a1*M1j + (s64)a2*M2j) >> 10)
```

The intermediate is a genuine 64-bit sum (3 `smull` + 6 `smlal`), so it **cannot
wrap**: `|S| <= 3*2^62 < 2^64`.

**`0x087B7F04`** - twelve terms over three lanes, each lane reduced separately:

```
r0 = destination (6 words, two `stm r0!, {r4,r5,r6}` blocks)
r1 = twelve coefficient words, walked with `ldr r3, [r1], #4`
r2 = the first three sample words, RELOADED before every group (`mov lr, r2`)
for groups 1..3:  r[lane] += (u32)(((s64)c[3g+lane] * three-sample-sum) >> 10)
last group:       r[3+lane]  = (u32)(((s64)c[9+lane] * three-sample-sum) >> 10)
```

The three reduced 32-bit lane values are then added into one accumulator per
lane, **with 32-bit wraparound**. That is a different computation and not a
rearrangement: the bits discarded from one product cannot carry into another.

The instruction-level difference is the last group's third lane, which folds the
shift into the accumulator (`add r6, r6, fp, lsr #10`) where the earlier three
read (`lsr r6, fp, #10`) and add separately. Six of `0x087B7F04`'s last-group
reduction words are **byte-identical** to `0x087B80A4`'s
(`E0844527/E0855529/E086652B/E0844B08/E0855B0A/E0866B0C`), which is what makes
the shared element the *reduction* rather than the whole routine.

The self-check measures that difference on a case chosen to show it. A case with
**equal** coefficients does **not** show it - multiplying by three commutes with
the shift - and the first attempt at that check used exactly such a case and
failed. The working case is lane coefficients 1000 / 2000 / 3000 against samples
1000 / 2000 / 3000: the separated-lane sum is `0x19BF9` where the single
reduction of the combined 64-bit sum is `0x8954`.

### 4.3 The scale: Q10 is INFERRED, and `0x400` is not in the code

`0x400` occurs **nowhere** in either routine - no immediate, no literal pool, and
neither routine has *any* pc-relative load. The shift amount 10 is the only scale
evidence, and a shift of ten discards ten fractional bits whatever the input
scale is. So the code licenses a **relative** scale: any
`s_a * s_M / 2^10 = s_out` fits, and "Q10" as a name for the data is
**INFERRED** from the call sites, not proven by the function. There is no `0x400`
constant in either routine and no Q10 claim is made for the *values*.

### 4.4 The callers

Each entry is the literal of a ROM-side Thumb-to-ARM veneer, and each veneer has
exactly **one** Thumb BL caller in the image:

| entry | veneer | Thumb BL caller |
| --- | --- | --- |
| `0x03000560` | `0x08049174` | `0x0802EFD0` |
| `0x03000700` | `0x08049180` | `0x0802F1DC` |

Neither call site resolves all four register arguments inside a readable window,
so the register roles above come from the routines' own instructions and **not**
from the call sites. That is stated rather than glossed over. The word
`0x03000700` also appears twice more in the image (`0x082DAA72`, `0x08799F68`),
both in the asset half and both coincidences.

## 5. `0x03000868` is NOT part of this family, and the brief was the outlier

The ticket's premise was that `0x03000700`, `0x03000560` and `0x03000868` share
one Q10 primitive. The first two do share the reduction. The third does not:

* **zero** `smull` and **zero** `smlal` in its 121 instructions; it uses `mla`,
  a 32-bit wrapping multiply-accumulate;
* **no** `lsr #10` and **no** `lsl #22` anywhere; its shift pair is `lsl #18`
  with `asr #14`, which is an 18.14 phase accumulator, not a product reduction;
* 21 `mla` and 22 `ldrsb`, with a 64-bit *position* accumulator maintained by
  `adds`/`adc` pairs and a pre-indexed conditional writeback
  (`ldrsbhs r0, [r3, #1]!`) that performs the carry propagation of the 64-bit
  increment. When the condition is false the instruction has **no effect at
  all** - no load *and* no base update - so the same source byte is reused for
  that output slot.

The committed `docs/LIFT_IWRAM_DISPATCH.md` already recorded 18.14 as a guess
from a fingerprint; this ticket's independent measurement confirms it and
refutes the brief's grouping. The existing document's word "fixed point" for the
family was not wrong, but "Q10" for the third member was. `0x03000868` remains
**unlifted** and is the recommended next cluster; its equations are recorded in
section 8 so the next ticket does not have to re-derive them.

## 6. Reachability

`0x030002DC`, `0x03000560` and `0x03000700` are reachable: each through its own
veneer, with 3, 1 and 1 Thumb BL callers respectively. `0x03000868` is reachable
as a **stored pointer**: the ROM literal word `0x0803E36C` holds `0x03000868`
and is read by the Thumb instruction at `0x0803E0F2`, which stores it into a
sound-channel record at `+0x18` as a callback.

**`0x03000330` is reachable by nothing**, and this is a measured negative, not an
absence of search:

* its IWRAM address `0x03000330` occurs **zero** times in the whole 8 MiB image at
  every byte alignment, in both the even (ARM) and the odd (Thumb) forms;
* no in-block BL, branch or literal-pool word in the walk-reached set names it;
* fall-through is impossible: `0x087B7C80` ends in an unconditional `bx lr` with a
  third routine's pool between them.

Its status is **INFERRED DEAD/UNREACHABLE, not proven dead**. The one route this
census cannot see is a pointer assembled at run time from two registers, which
only PC sampling could settle. No guard, no dead-code marker and no semantic name
is invented for it.

## 7. Overlay-wide pattern census

The census is over the block's code half, `0x03000000..0x03000F44`, whose entries
were re-derived rather than repeated: **16 entries** (13 Thumb-to-ARM veneers at
`0x08049120..0x080491C0` plus 3 stored ROM words at `0x0803E36C`, `0x0803F3BC`,
`0x0803F434`). The image-wide value census reproduces the previous ticket's
figures exactly: 225 distinct in-block values over 533 two-byte-aligned sites
against 129 over 257 at four-byte alignment.

| idiom | exact matches | close variants | out of family |
| --- | --- | --- | --- |
| byte-lane (`ands` + `0xFF` + predicated lane op) | **8 sites, 2 functions** (`0x087B7C80` x4, `0x087B7CD4` x4) | **0** | - |
| Q10 reduction (`smull`/`smlal` + `lsr #10`/`lsl #22`) | **15 sites, 2 functions** (`0x087B7F04` x12, `0x087B80A4` x3) | **0** in the family | 21 |
| Q18.14 (`lsl #18`/`asr #14`, `mla`, `ldrsb`) | - | `0x03000868` is the **only** member | - |

The finger-print corrections that mattered, and both are counting hazards:

* a byte-lane rule requiring `lsr #N` finds **3 of 4 lanes** per function,
  because lane 0's term is unshifted. The mask census is the reliable form: every
  reached `ands` whose mask register is a local `mov` immediate is `0xFF`, eight
  sites, no other mask exists;
* a Q10 rule keyed on the **folded** spelling finds **3 of 12** reductions in
  `0x087B7F04`.

A pattern scan is a **lower bound**. A function reaching the same effect through
a different register path would not match, and the blind paths are named: the
byte-lane scan cannot see a mask materialised other than by a local `mov`
immediate, and the Q10 scan cannot see a reduction whose low half is computed by
a path that never touches the product's low word.

**The next cluster**, ranked by evidence per byte from the census rather than from
adjacency:

1. **`0x03000868`, Q18.14** (484 bytes, 121 instructions, the largest pool-free
   leaf in the block). Its contract is derived from the image but is **not
   lifted by this ticket**; its blockers are its size and the `adds`/`adc`
   carry modelling, both of which this ticket's `ldrsbhs` finding resolves. It is
   the only function in the block with a 64-bit *adder* and no 64-bit
   *multiplier*, which is the easiest thing to get wrong about it.
2. **`0x03000A4C`, the signed-byte clamp/packer** (148 bytes, 6 callers). The
   census flags it as the sharpest small open question: its eight shift sites sum
   to 38 rather than 32, so it is not a byte-packer in the ordinary sense and the
   first reading of it is undecided.
3. **The strided gather family** `0x03000388`, `0x030004C0`, `0x03000414`
   (472 bytes). Reachable except `0x03000414`, but the contract lives in an
   uncharacterised context record.

## 8. What is NOT proven

* **What the 256-byte table at `0x0805672C` means.** No compression, container or
  opcode meaning is imported from another title.
* **The Q10 scale of the fixed-point operands.** The shift is proven; the input
  scale is INFERRED from the call sites.
* **Whether `0x03000330` ever executes.** INFERRED dead, not proven.
* **The context record fields beyond `+0x24` and `+0x30`**, and what the record
  at `r2` is for either fixed-point routine.
* **Whether the block was authored as C or as assembly**, and no ADS 1.2 codegen
  match (ADS_MATCH stays BLOCKED - the installation is present but the licence
  it ships covers a different product, so no compile has been attempted).
* **The `bias` reading of `0x087B80A4`'s `r2+36`.** It is a 32-bit addend added
  after the reduction at the one call site found; whether it is a bias rather
  than a previous output is INFERRED from that one site.

## 9. Corrections carried

Each is a factual error found by measurement, not a rewording.

1. **The entry-to-next-entry reading of `0x087B7C80` (84 bytes / 21 instructions)
   was wrong.** It is 76 bytes / 19 instructions, and the eight bytes the window
   absorbed are a *third* routine's literal pool. Carried in this document, in
   `src/IwramByteLanePair.c` and in the `iwrambl` target's notes.
2. **`0x03000868` is not Q10.** Zero `smull`/`smlal`, zero `lsr #10`/`lsl #22`;
   it is Q18.14 with `mla`. Carried in section 5 and in the `iwramqf` notes.
3. **The reduction's `lsr` is not "load-bearing".** The two-instruction form is
   algebraically identical to a truncated arithmetic shift as well as to a
   truncated 64-bit logical shift. The source comment asserting otherwise was
   corrected and the self-check now asserts the identity. This ticket made the
   wrong claim three times before measuring it.
4. **`0x03000328`'s two words are a pool but not this routine's**, and the unit
   that owns them precedes it. An earlier classification counted them as part of
   the byte-lane function's extent.
5. **A "rounding-up" count law for `0x087B7CD4` was wrong.** The pre-loop
   decrement means a count of five or six yields **one** pass, not two, and the
   wrap boundary is `0x80000004`, not the sign bit.
6. **The estimate of the block's non-code words.** The previous ticket recorded
   8; the census accounts for 11, of which 7 are pool words and 4 are
   reached-but-not-owned (a `nop`, the dispatcher's register-return path and the
   Thumb halfword). Reconciled to the word: 966 owned + 3 = 969 function words
   and 901 + 3 = 904 reachable, which **confirms** both of the previous document's
   figures once the units are identified.

## 10. The three verdicts

Independent, and never inferred from one another:

| target | SEMANTIC | MODERN_BUILD | ADS_MATCH |
| --- | --- | --- | --- |
| `iwrambl` | PROVEN, 10726 assertions, 0 failures | PASS, 128 bytes at `0x087B7C80` | BLOCKED (`ADS12_LICENSE_UNAVAILABLE`) |
| `iwramblsparse` | PROVEN, 10726 assertions, 0 failures | PASS, 128 bytes at `0x087B7CD4` | BLOCKED |
| `iwramqf` | PROVEN, 340029 assertions, 0 failures | PASS, 800 bytes at `0x087B7F04` | BLOCKED |

The SEMANTIC numbers are shared between the first two because one self-check
covers both byte-lane routines; the harness compares the count against each
target's own `semantic_minimum_checks`.

### The host self-checks

`src/probes/iwrambl_selftest.c` (10726 checks) runs explicit ARM models against
the reconstruction:

* **exhaustive** over all 256 table entries x all 256 lane values x all four
  lanes, and over every word-granularity count in `[0, 64]`, comparing the whole
  destination window rather than a sample;
* all 16 `(source lane, destination lane)` placements, to prove the lane map is
  the identity rather than a permutation;
* `table[0]` is proven **never read**, by filling it with a byte no correct
  result can contain;
* the count-0 and non-multiple-of-4 wraparound are **modelled and asserted as
  arithmetic**, never executed: a count of 0 is 2^30 passes and a count that is
  not a multiple of 4 never terminates. Neither is guarded.
* 8000 randomized differential cases per routine.

`src/probes/iwramqformat_selftest.c` (340029 checks) compares both routines
against an independent 64-bit model: 200000 random 64-bit reductions, an
**exhaustive** sweep of all 2^22 high-word values and all 2^22 low-word
quotients the reduction reads, exhaustive truncation below 2^10, the
sign-combination and 64-bit-overflow cases, and 60000 + 80000 randomized
32-bit differential cases per routine.

Both were written before the first compiler run and **both found real defects in
the tests themselves** - a wrong discriminating constant, a wrong pass-count
model, a wrong destination window and a reading-order error about the
accumulators - each of which would have looked like a defect in the
reconstruction.

### The modern build comparisons, as measurements

`is_a_match_claim` is **false** in all three reports; a modern compiler is not
the original compiler.

| target | original | modern | differing bytes | instruction spans |
| --- | ---: | ---: | ---: | --- |
| `iwrambl` | 76 code + 8 padding | 128 | 80 of 84 | 0 of 19 match |
| `iwramblsparse` | 88 | 128 | 73 of 88 | 0 of 22 match |
| `iwramqf` | 520 | 800 | 463 of 520 | 1 of 130 match |

The differences are structural and worth naming rather than hiding: GCC hoists
the loop count test of `0x087B7C80` to the top and keeps the loop body at 32
instructions against the original's 19; for `0x087B80A4` GCC expands each signed
64-bit product into `umull` plus a `mul`/`mla` sign correction (about 15
instructions per lane) where the original uses one `smull` or `smlal`, and
places the unit's two functions in the **opposite order** to the image. None of
that is a defect in the reconstruction - the SEMANTIC verdict is measured by
running it - and none of it is evidence about ADS 1.2.
