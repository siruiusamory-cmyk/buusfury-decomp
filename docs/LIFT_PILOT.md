# DECOMP-LIFT-PILOT-001 - the first semantic lifting loop

**Status:** the loop is proven end to end on one function family.
**Target:** the GBARam allocator at file `0x03D4D0..0x03D740`.
**Baseline:** `f729b44ccf98dd352376ac2f503bb96769eadb38`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, deliberately independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | whether the reconstructed C behaves correctly, by RUNNING it: 230 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | whether the source compiles, links at its original address and emits bytes: 772 bytes |
| **ADS_MATCH** | **BLOCKED** | whether it reproduces the original compiler's output: `ADS12_LICENSE_UNAVAILABLE` |

None of these is evidence for another, and the harness enforces that:

- A passing modern build says **nothing** about the original compiler. GCC 16.1.0 is
  not ADS 1.2 `tcpp`, and the report records `is_the_original_compiler: false`.
- A passing semantic run removes **one class of error** (wrong C) and nothing else.
- `ADS_MATCH` is never promoted from either of the other two. The comparison
  document carries `is_a_match_claim: false` and a `match_claim_note` saying so, and
  a test asserts both.

The modern-vs-original byte comparison *is* published, as a measurement. It must not
be read as a match claim in either direction.

---

## 2. Toolchain

Detected, never installed. `python -m buusfury lift --target gbaram`.

| | |
| --- | --- |
| Family | GNU Arm Embedded (devkitARM) |
| Compiler | `arm-none-eabi-gcc.exe (devkitARM) 16.1.0` |
| Target triple | `arm-none-eabi` |
| Binutils | `GNU objdump (GNU Binutils) 2.46.0.20260210` |
| Root | `C:\devkitPro\devkitARM` (reported as `<DEVKITARM>`), overridable with `$DEVKITARM` or `--toolchain-root` |
| Configuration | `-mcpu=arm7tdmi -mthumb -O1 -ffreestanding -fno-common -fno-builtin -fomit-frame-pointer -mno-unaligned-access` |

Support for the target is not taken from a version banner. `probe_target_support`
compiles, links and **disassembles** a two-line function and requires the result to
contain a write to `r0` and a return; the report stores the disassembly it saw
(`adds r0, #1`, `bx lr`).

An **explicit** toolchain root is authoritative: if it does not hold a complete
toolchain the answer is "no toolchain", never a silent fallback to a different one.
A partial installation is likewise reported absent, so a build can never half-run.

### 2.1 The ADS 1.2 situation, unchanged and not worked around

The ARM Developer Suite 1.2 binaries **are present** on this machine
(`armcc`, `armcpp`, `armasm`, `armlink`, `fromelf`, `tcc`, `tcpp`). The licence file
that ships with them licenses `Win32_CWIDE_Unlimited` - the CodeWarrior IDE - and
carries no compiler/armasm/armlink feature, so FLEXlm refuses the tools. That is
`ADS12_LICENSE_UNAVAILABLE`, which is a different thing from "ADS is not installed"
and is the only correct code here.

This ticket did not attempt a workaround, did not modify the existing
`DECOMP-COMPILER-PROBE-001` work, and does not weaken its result. Gate 6 still reports
BLOCKED.

---

## 3. What was lifted

`src/GBARam.c` - the reconstruction promoted into the real decomp source tree, at the
path the surviving original build command names (`tcpp -S -c -cpu ARM7TDMI -O1
src/GBARam.c`). Eight Thumb functions, 608 bytes of code plus a 16-byte literal pool:

| Function | Role | Original | Modern | same extent |
| --- | --- | ---: | ---: | --- |
| `sub_0803D4D0` | list head and node-0 pool initialiser | 24 B / 12 i | 40 B / 19 i | no |
| `sub_0803D4E8` | unlink a node and mark it busy | 56 B / 28 i | 80 B / 40 i | no |
| `sub_0803D520` | insert a node at the free-list head | 40 B / 20 i | 44 B / 22 i | no |
| `sub_0803D548` | merge a node with its successor | 34 B / 17 i | 34 B / 17 i | no |
| `sub_0803D56A` | merge a node with its predecessor | 78 B / 39 i | 106 B / 53 i | no |
| `sub_0803D5B8` | allocate: best-fit search | 132 B / 64 i | 160 B / 76 i | no |
| `sub_0803D63C` | free: return a node and coalesce | 214 B / 101 i | 264 B / 126 i | no |
| `sub_0803D712` | total free bytes | 30 B / 15 i | 44 B / 22 i | no |

**The promotion changed no code.** `src/probes/GBARam.c` is now a one-line shim that
`#include`s the real file, so the probe path compiles the same token stream; that is
verified by compiling both entry points and comparing their disassembly
(identical sha1 `c2481b78...`, 367 instructions each). The semantic fixes the previous
ticket found by running the allocator - signed locals, testing the 16-bit index before
converting it, merge direction, the `0x7FFFFFFF` best-fit sentinel, and the recorded
absence of an out-of-memory path - are all preserved, and a test asserts each.

---

## 4. The comparison

Artifact: `config/lift_gbaram.json` (committed, regenerated and compared key by key by
gate 7). Working files: `build/lift/gbaram/` (gitignored).

### 4.1 Translation unit

| | Original | Modern |
| --- | ---: | ---: |
| Bytes emitted | 624 | 772 |
| Differing bytes in the overlap | - | 595 of 624 |
| Instruction spans keyed on the original's boundaries | 296 | - |
| Spans byte-identical | - | 3 |
| Spans differing | - | 293 |
| Bytes not covered by an original instruction | - | 16 (the literal pool) |

The modern build is **148 bytes larger (+23.7%)** and does not fit the original
footprint. That is reported, not worked around.

Instruction granularity is keyed on the **original's own instruction starts**, not on
the modern output. Capstone renders distinct Thumb encodings identically (`0x4280` and
`0x4500` are both `cmp r0, r0`), so a positional text comparison can report zero
differences for unequal bytes and can exceed the instruction count. An earlier
revision of this module did exactly that - it reported 0 differing instructions for 595
differing bytes - which is why the spans now come from the target.

### 4.2 What actually agrees

The byte differences are large, but the **structural** correspondence is exact:

| | Agreement across all 8 functions |
| --- | --- |
| Call counts | identical (0,0,0,0,0,1,3,0) |
| Literal-slot counts | identical (3,1,1,0,1,2,1,1) |
| Leaf/non-leaf | identical (7 leaf, 1 non-leaf) |

`sub_0803D548` is even the same size and same instruction count (34 B / 17 i), though
not the same bytes. The reconstruction's *shape* is right; the code generator differs.

### 4.3 The literal pool - the sharpest divergence

| | Original | Modern |
| --- | --- | --- |
| Distinct literal slots | 4 | 10 |
| Contiguous runs | **1** | **7** |
| Shared pool | **yes** | no |
| Functions reaching a pool | 7 of 8 | 7 of 8 |

The original places **one** pool at `0x0803D730..0x0803D740` and seven of the eight
functions reach back into it. That is itself the evidence that the region was a single
translation unit, and it is why the comparison cannot be done per function: a function
containing a PC-relative literal load has a displacement that depends on where the pool
sits. A modern compiler pools per function or per basic block. This is a consequence of
the compiler, not a defect in the reconstruction.

### 4.4 Register and ABI facts

Recorded per function for both sides: callee-saved registers pushed, frame size,
registers written, return-shaped terminations, leaf-ness. Example from
`sub_0803D5B8`:

| | Original | Modern |
| --- | --- | --- |
| callee-saved pushed | `r4 r5 r6 r7` | `r4 r5 r6` |
| frame size | 0 | 0 |
| written | `r0..r7` | `r0..r6, r8` |

"Return-shaped" counts both `bx lr` and GCC's `pop {rN}; bx rN`, so the metric stays
comparable across the two compilers; it is documented as return-shaped rather than
proven returns, because a register-form `bx` is a computed jump in principle.

---

## 5. Reproducing it

```powershell
python -m buusfury lift --list-targets
python -m buusfury lift --target gbaram --rom <baserom>          # full loop
python -m buusfury lift --target gbaram --rom <baserom> --verify # regenerate + compare
pwsh -File scripts/check.ps1                                     # gate 7 runs --verify
```

The report is committed and **environment independent**: the toolchain root is
`<DEVKITARM>`, the checkout root is `<REPO>`, remaining absolute paths are `<path>`,
there are no timestamps, and the file is LF-only. A test asserts none of them leak.

---

## 6. Limits, stated plainly

1. **This is one function family.** The loop is proven; the coverage is 608 bytes of a
   8,388,608-byte cartridge.
2. **`ADS_MATCH` remains BLOCKED** and no part of this ticket reduces that. Every number
   in section 4 describes a *modern* compiler.
3. **The modern build does not fit the original footprint** (772 > 624 bytes), so even
   as a structural template it would need work before it could occupy the region.
4. **Field names in `src/GBARam.c` are still placeholders.** The disassembly fixes each
   offset and access width; it does not say what the game called the field. The one
   previously unknown store at `absorbed+0x04` is now behaviourally consistent with
   `+0x00`/`+0x04` being the coalescing neighbour links across 230 checks, which is
   consistency, not proof.
5. **The semantic self-check runs on the host** with MSVC, not on ARM. It falsifies
   wrong C; it cannot validate code generation.

---

## 7. Next recommended function family

From `config/functions.json` and `config/compiler_probes.json`, in the order the
evidence supports:

1. **The script bytecode interpreter at `0x08004038`** (Thumb). It is reachable, it is
   named by the LOG1-REMAKE corpus with quoted source paths (`T:\Source\
   ByteCodeInterpreter\ByteCodeInterpreter.cpp` survives in the ROM), and it is
   non-leaf with known callers - so it exercises the loop's call-graph and multi-function
   paths in a way a single leaf does not. Its boundary is a region anchor, not a guess.
2. **The container dispatcher at `0x0803D940`** (Thumb, 57 callers). It sits in the same
   `0x0803D...` cluster as GBARam, is independently located, and its kind-0 path is a
   plain `memcpy` that a reconstruction can be checked against byte-wise.
3. **The map-entry lookup at `0x080089FC`** (Thumb). Small, single-purpose, and it is the
   only code site that takes the MapEntry table address as a literal, so its literal
   handling is a clean test of the pool comparison.

Only after those should anything larger be attempted.
