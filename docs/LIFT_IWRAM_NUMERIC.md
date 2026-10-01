# The IWRAM block's numeric and data-processing families

`DECOMP-IWRAM-NUMERIC-001`. The 4100 bytes at ROM `0x087B79A4..0x087B89A8` are
the image of IWRAM `0x03000000..0x03001004`, installed by the reset code's own
DMA3 program, so IWRAM `X` = ROM `0x087B79A4 + (X - 0x03000000)` byte-exactly.
`docs/LIFT_IWRAM_RUNTIME.md` establishes the copy; `docs/LIFT_IWRAM_DISPATCH.md`
establishes who reaches it. This document covers the two routines the ticket
names, plus the census that settles whether either has a sibling.

| | IWRAM | ROM | size | instructions | source |
|---|---|---|---|---|---|
| Q18.14 sampler | `0x03000868` | `0x087B820C` | 484 B | 121 | [`src/IwramQ1814.c`](../src/IwramQ1814.c) |
| field clamp | `0x03000A4C` | `0x087B83F0` | 148 B | 37 | [`src/IwramFieldClamp.c`](../src/IwramFieldClamp.c) |

They are **adjacent** - the sampler's last instruction ends exactly where the
clamp's prologue begins - and they are still **two translation units**, because
adjacency is not a reason to put two unrelated operations in one unit and the
census found no semantic reason to join them.

---

## 1. `0x03000868` - a Q18.14 fractional-position signed-byte sampler

### 1.1 The equations

```
address_i = (C + floor((A + i*B) / 2^14)) mod 2^32
out[i]    = (out[i] + D * (int8_t)mem[address_i]) mod 2^32
```

`s8` is `ldrsb`, the `floor` is what an arithmetic right shift of a
two's-complement value computes, and every operand is 32-bit. `A` and `B` are
Q18.14 byte quantities (14 fractional bits per byte); `C` is an integer byte base;
`D` is a 32-bit multiplier.

**The mechanism is that the 64-bit phase's HIGH WORD IS THE POINTER:**

```
hi = C + (A asr 14)          r3, dereferenced by every ldrsb
lo = A lsl 18                r7, the sub-byte fraction at 2^18 per byte
adds lo, lo, (B lsl 18)
adc  hi, hi, (B asr 14)
```

so the pair is one 64-bit accumulator holding `(A + i*B) * 2^18 + C * 2^32`, and
`hi` is its high word. `lsl #18` with `asr #14` is the 32-14 split, which is why
the low word is scaled by eighteen and the high word by fourteen.

### 1.2 The whole extent, and why a first-terminator rule is wrong

The routine has **two** `bx lr` epilogues - at IWRAM `0x0300098C` and
`0x03000A48` - because the odd-count path leaves early. A walk that stops at the
first terminator reports **292 bytes** instead of 484. The extent is closed from
both sides: 121 instructions ending at `0x03000A4C`, which is exactly where the
next entry begins.

### 1.3 The conditional writeback, which is the sharpest detail in the ticket

When `B asr 14` is zero the compiler replaces the `adc` with

```
adds    r7, r7, r8          the fractional add, setting carry
ldrsbhs r0, [r3, #1]!       HS = carry set; PRE-indexed, with writeback
```

`ldrsbhs` is `ldrsb` under condition **HS** (carry set). When the carry is set it
loads from `r3+1` and leaves `r3 = r3+1`. **When the carry is clear the
instruction has no effect at all**: no load, no memory access, and no base
writeback. It is the 64-bit carry rendered as one predicated instruction, and a
reconstruction that reads `[r3, #1]!` as an unconditional post-increment gets
every non-carrying element wrong.

The selector is `cmp r4, #0` with `r4 = B asr 14`, i.e. **`0 <= B <= 16383`** -
**not** `|B| < 2^14`, because a negative `B` has an all-ones arithmetic shift and
takes the general path.

#### The retained sample, which is observable

In the carry-only body the sample is **retained** in `r0` when the address does
not move, and the code depends on that. A group reads its destination words into
registers, accumulates, and only then stores, so the retention is invisible
*within* a group - but across groups the previous group's `stm` has rewritten a
byte the general body would read again:

```
B = 0, count = 8, C = the address of out[0], out[0] = 0x40, D = 0x102
  the first group writes out[0] = 0x40C0, so the byte at C is now 0xC0
  the second group still uses the RETAINED 0x40  ->  out[4] = 0x4080
  a re-reading implementation would use 0xC0     ->  out[4] = 0xC180
```

`src/probes/iwramq1814_selftest.c` asserts `0x4080` and asserts it is **not**
`0xC180`; the discrimination was proved by temporarily re-reading in the source
and watching that single assertion fail. The two bodies are therefore kept
separate on purpose and must not be "tidied" into one loop.

### 1.4 The count dispatch, and the two unguarded edges

```
if (n & 1) { 1 element; n -= 1; if (n == 0) return; }
if (n & 2) { 2 elements; n -= 2; if (n == 0) return; }
if (n & 4) { 4 elements; } else { 4 elements; 4 elements; }
for (;;) { before = n; n = before - 8; if (!(before >= 8 && n != 0)) break;
           4 elements; 4 elements; }
```

The `tst r2,#4` test **skips** the first 4-element group when bit 2 is set while
the following `subs r2,r2,#8` still subtracts **eight**, so the count is not
consumed in whole groups for every residue. Measured element counts, by executing
the ROM's own bytes:

| count | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 12 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| elements written | **8** | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 12 | 20 |

A count of **zero** writes **eight** words: there is no pre-test, the first
`subs` borrows, and the body has already run twice. The count is used unsigned -
it is only ever tested for equality with zero - so `0xFFFFFFFF` asks for 2^32 - 1
elements. Both are reproduced, neither is guarded.

### 1.5 Callers and purpose (branch D, 27/27 checks)

| route | measurement |
|---|---|
| direct branches to IWRAM `0x03000868` | **none** - it is IWRAM, no ROM branch reaches it |
| 32-bit sites in the whole 8 MiB holding the address | **exactly one: ROM `0x0803E36C`** |
| its PC-relative readers | **exactly one: Thumb `ldr r2,[pc,#0x278]` at `0x0803E0F2`** |
| the Thumb-bit form `0x03000869` | zero sites |
| the thirteen Thumb-to-ARM veneers | none targets it |
| invocation sites | **eight**, all in the routine at `0x0803E152`, through a generic `bx r3` thunk |

The address is **installed into a record field** (`record+0x18`), not called
directly, and the invocation is `ldr r3,[r4,#0x18]` + `bl 0x08046AA6` with
`r0 = &record`, `r1 = the caller's buffer`, `r2 = the count`. The four input words
are the record's own header, and their provenance is measured:

* `+0x00` phase, Q18.14 - reset to zero by the reader and advanced to
  `record[0] + count*record[1]` by the invoker;
* `+0x04` step, Q18.14 - **computed** as
  `(((record[0x14] * record[0x30]) >> 14) * 4195 + 2047) >> 12` with the sign taken
  from bit 2 of `record[0x11]`; the `+2047` is a round-to-nearest at the `>>12`;
* `+0x08` the signed-byte source base, copied from a **pointer-chased
  descriptor** (`record[0x28]` dereferenced);
* `+0x0C` the gain word, written as **two halfwords** and read back as **one
  word** by `ldm r0,{r3,r4,r5,r6}` - the multiplier is the concatenation, which is
  an encoding fact and not a typo.

**Neutral structural role:** a fractional-position signed-byte sampler with a
per-record gain - structurally a **resampling / mixing step** over a byte buffer,
whose position advances by a Q18.14 step. What the samples, the gain or the mode
bits *mean* is UNKNOWN and is not assigned here.

---

## 2. `0x03000A4C` - a ten-bit signed field clamp and de-interleave

### 2.1 The bit transformation

```
for each pair of source words (w0, w1):
    src[0] = 0; src[1] = 0;             the source pair is DESTROYED
    dst0[k] = sat8(s10(w0[15:6]))  | sat8(s10(w1[15:6]))  << 8
    dst1[k] = sat8(s10(w0[31:22])) | sat8(s10(w1[31:22])) << 8
```

Each 32-bit source word carries **two ten-bit SIGNED fields**, at bits `31..22`
and at bits `15..6`. Bits `21..16` and `5..0` - twelve of thirty-two - are never
read by any instruction. Each field is saturated to signed 8-bit `[-128, 127]`
and emitted as one byte; two consecutive words' fields of the same half form one
destination halfword. It is a **de-interleave** of a two-channel interleaved
stream, not a conversion of one stream, and the source is consumed destructively.

### 2.2 All eight shift sites, and the brief's "sum 38"

The ticket's brief described this routine as an "unresolved shift/pack routine
with 8 shift sites summing to 38". Measured from the encoding:

| # | ROM | IWRAM | word | form | shift | role |
|---|---|---|---|---|---|---|
| 1 | `0x087B8404` | `0x03000A60` | `E1A05B44` | standalone | `asr #22` | field C = `s10(w0[31:22])` |
| 2 | `0x087B8408` | `0x03000A64` | `E1A07B46` | standalone | `asr #22` | field D = `s10(w1[31:22])` |
| 3 | `0x087B840C` | `0x03000A68` | `E1A04804` | standalone | `lsl #16` | first half of the low-field extraction |
| 4 | `0x087B8410` | `0x03000A6C` | `E1A06806` | standalone | `lsl #16` | the same, for the second word |
| 5 | `0x087B8414` | `0x03000A70` | `E1A04B44` | standalone | `asr #22` | second half: `s10(w0[15:6])` |
| 6 | `0x087B8418` | `0x03000A74` | `E1A06B46` | standalone | `asr #22` | the same, for the second word |
| 7 | `0x087B8460` | `0x03000ABC` | `E1844406` | folded into `orr` | `lsl #8` | packs the second low byte into place |
| 8 | `0x087B8468` | `0x03000AC4` | `E1855407` | folded into `orr` | `lsl #8` | the same for the second stream |

The amounts are **22, 22, 16, 16, 22, 22, 8, 8 and their sum is 136**, not 38 -
eight non-zero amounts of at least 8 cannot total 38. The 38 is a **two-site pair
sum**, and the previous census's own field names it: its
`same_register_opposite_shift` entry printed
`amount(nearest opposite-direction shift on the same source register) +
amount(this site)`, which for the low-field extractor is `lsl #16` + `asr #22 =
38`, printed at **six of the eight** sites. That pairing rule is a *fixed-point*
test - "the two halves of one 64-bit value, summing to 32" - and it simply does
not apply here; the 38 is 32 + 6, where 6 is the field's low bit index.

The pair is also **not a net `>> 6`**: the intermediate 32-bit **logical** shift
discards bits `31..16` first, so the arithmetic shift sign-extends from bit 15
and the result is a ten-bit field rather than a six-bit one.
`src/IwramFieldClamp.c` expresses both offsets with the single form
`(w << (32-10-shift)) >>s (32-10)`, which is the instruction pair written once.

### 2.3 Saturation, masks and the halfword store

```
cmp r4, #0x7F ; movgt r4, #0x7F     if (v >  127) v =  127
cmn r4, #0x80 ; mvnlt r4, #0x7F     if (v < -128) v = -128
```

`cmn r4,#0x80` is `r4 + 128`; `mvnlt r4,#0x7F` is `r4 = ~0x7F = -128`. ARMv4T has
no `ssat`/`usat`, so a saturation can only be a conditional move, and the
sixteen-byte pattern occurs **exactly once in the whole 8 MiB image** - which is
what proves this routine is the overlay's only clamp.

The two **low**-field values are explicitly masked with `and #0xFF` before the
`orr`; the two **high**-field values are not, because the consuming `strh` keeps
only the low 16 bits. The missing mask is a property of the store width.

### 2.4 The count is a signed do-while over word pairs

```
subs r3, r3, #2 ; bgt
```

`bgt` is the **signed** greater-than test on the value *before* the subtraction,
so the body runs at least once for *any* count, and one iteration consumes **two**
source words however small the count is. Measured: counts `0,1,2` run once,
`3,4` twice, `5,6` three times. A count of `3` therefore reads and zeroes four
words while only three were asked for, and there is no bound on the source
pointer. Reproduced, not repaired.

### 2.5 Callers (branch D, 27/27 checks)

The entry is the literal of the Thumb-to-ARM veneer at `0x080491B4`
(`bx pc` / `nop` / `ldr pc,[pc,#-4]` / `0x03000A4C`), and **exactly six Thumb `BL`
sites** reach it, all inside one routine at **`0x0803F296`**. Zero ARM branches
and zero stored pointers reach it. The six sites split one run at fixed plane
boundaries and pass:

| argument | measured at the call sites |
|---|---|
| `r0`, `r1` | two of the four EWRAM bases `0x02000000` / `0x02000200` / `0x02000400` / `0x02000600`, optionally shifted by `r4` |
| `r2` | a fixed-offset buffer **inside the caller-supplied context object** at `context + 0x9C4`, plus a boundary-relative byte offset |
| `r3` | the distance to the next `0x400`/`0x200` boundary |

**Neutral structural role:** a **packed-field conversion** - a saturated
de-interleave of 10-bit signed fields into two 8-bit streams. What the fields
represent is UNKNOWN.

---

## 3. Family census: neither anchor has a sibling

`build/recon/IWRAM_N/C/census.py` re-derives the whole code half from the image
and reports 48 checks / 0 failures over 20 functions and 966 owned words.

* **Q18.14:** exactly **two** `lsl #18` / `asr #14` pairs in the entire code half,
  both in `0x03000868`, and **zero unpaired** occurrences of either amount. The
  `Q22.10` dot products of `src/IwramQFormat.c` use `smull`/`smlal` where this
  uses `adds`/`adc` and `mla` - a different mechanism, deliberately not one
  family. The sampler's 24-byte prologue is **unique in the whole 8 MiB image**.
* **Clamp:** exactly **four** clamp quads, all in `0x03000A4C`, and the pattern is
  unique in the image. It is also the only routine in the block that writes
  **post-indexed** halfwords to two cursor registers. "Two halfword destination
  bases" is *not* the fingerprint - the IRQ dispatcher also has two, and neither of
  its stores advances - so the post-indexed store shape is the discriminator.
* `0x030002DC` shares the `orr ...,lsl #8` packing tail but has no clamp, no sign
  extension, one stream and a 1:1 ratio: a shared sub-structure, not a relative.
  Its true relative is `0x03000330`, in the byte-lane family.

Negative results are recorded with the register paths each cannot see - a shift
amount held in a register (**four such sites are measured**, so the blind path
provably exists), an amount materialised separately, and a scale applied through a
pool-loaded coefficient, which is invisible in principle.

### The next high-value subsystem batch

| # | batch | bytes |
|---|---|---|
| 1 | the LZ bit-buffer decompressor pair and their two byte-identical nested refill helpers: `0x03000040`, `0x03000CA0`, `0x0300028C`, `0x03000EF4` | **1344** |
| 2 | the strided two-row block gather: `0x03000388`, `0x030004C0`, `0x03000414` (`0x03000414` is `0x030004C0` plus one destination stream) | 472 |
| 3 | the IRQ installer and clear stub: `0x03000AE0`, `0x03000000` | 188 |

Batch 1 is recommended: it is the largest uncharacterised subsystem left, and it
is the only one whose evidence chain is fully internal - nine `BL`s per caller to
a helper that is byte-identical between the two callers, and two near-duplicate
members that cross-check each other's derivation.

### A disagreement with the committed callgraph, recorded and NOT acted on

The census measures four committed extents in `config/lift_iwramdispatch.json` as
*windows to the next entry* rather than instruction counts - `0x03000040`
167 -> 149, `0x030007FC` 23 -> 22, `0x03000B6C` 75 -> 73, `0x03000CA0` 169 -> 151 -
and its `functions` array omits the two nested helpers (16 entries against 20
functions). Its `unreachable_code_runs` **does** match. No committed report was
changed: this ticket owns two new targets and does not own its siblings' prose.

### A stale sentence left in place on purpose

The `iwramqf` registry note ends "...It remains unlifted and is the recommended
next cluster", referring to `0x03000868`. **That sentence is now stale** - this
ticket lifts it - and it was deliberately **not** edited, because a registry
`notes` string feeds that target's committed report and this ticket does not own
its sibling's prose. `config/lift_iwramqf.json` is therefore byte-identical to
what it was, `tests/test_lift_iwramnumeric.py` pins the sentence in place, and a
future ticket that owns `iwramqf` can refresh it.

---

## 4. Verification

Three independent channels, in increasing strength:

| channel | what it compares | result |
|---|---|---|
| host self-check (`src/probes/*_selftest.c`) | the reconstruction against a **closed-form reference computed in the self-check**, plus edge and aliasing cases | `iwramq1814` 20,644 assertions / 0 failures; `iwramfieldclamp` 69,424 / 0 |
| instruction differential (`build/recon/IWRAM_N/diff_rom.py`) | a Python model of the equations against the **ROM's own bytes executed by an ARM interpreter** | 1,914 cases / 0 mismatches |
| C-versus-ROM differential (`build/recon/IWRAM_N/cdiff.py`) | **the reconstructed C** against the ROM's own bytes on a shared deterministic case stream, one quarter of the sampler cases with the destination aliasing the sampled bytes | 12,000 cases / 0 mismatches |

The third is the one that matters: it removes the possibility that the
reconstruction and its reference share a misreading. It found and confirmed the
retained-sample behaviour, and the aliasing family is what makes that checkable.

Two self-check defects were found by running it and fixed: a reference that read a
sample byte before the test had written it, and a reference saturation boundary
compared as a signed value against an unsigned return. Both were test bugs; the
reconstruction was right.

### The verdicts, which are independent

| | `iwramq1814` | `iwramfieldclamp` |
|---|---|---|
| SEMANTIC | **PROVEN** (20,644) | **PROVEN** (69,424) |
| MODERN_BUILD | **PASS** - 484 B original -> 1,008 B linked at `0x087B820C` | **PASS** - 148 B original -> 196 B linked at `0x087B83F0` |
| ADS_MATCH | **BLOCKED** (`ADS12_LICENSE_UNAVAILABLE`) | **BLOCKED** |

The modern comparison is a **measurement, not a match claim**:
`is_a_match_claim` is false, `byte_identical` is false, and 0 of 121 (respectively
37) instruction spans are identical. `MODERN_BUILD = PASS` says the source
compiles and emits bytes; it says nothing about the original compiler, and
`ADS_MATCH` stays blocked because the ADS 1.2 installation on this machine is
unlicensed - which is a different condition from "not installed".

### The method traps this ticket paid for

* **capstone's ARM condition enum is offset by one** (`EQ = 1` ... `AL = 15`). An
  interpreter written with the ARM ARM's numbering branches the opposite way
  everywhere and still produces plausible output.
* **A post-indexed transfer reports `mem.disp == 0` and puts the offset in a third
  operand; a pre-indexed one reports `disp == 1` with two operands.** Reading
  `mem.disp` silently drops the writeback - which is exactly the behaviour this
  ticket exists to prove.
* **`MLA Rd, Rm, Rs, Rn`**: the multiplier is the *lowest* nibble, not bits 11..8.
* **`ldm`/`stm` base registers are plain `ARM_OP_REG` operands**, not `ARM_OP_MEM`,
  so a memory-base helper that only looks for `ARM_OP_MEM` sees no base at all for
  the whole block-copy idiom.
* PowerShell `>` writes UTF-16LE, so redirected check output is not byte-comparable
  with a fresh run.
