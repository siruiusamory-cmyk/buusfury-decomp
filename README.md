# Buu's Fury - matching decompilation

A from-scratch matching decompilation of **Dragon Ball Z: Buu's Fury** (GBA, USA
rev0), intended as a deterministic foundation for a modern mod-build that
DragonByte Z can target.

This repository is deliberately **separate** from the LOG1-REMAKE / Dragonbyte Z
checkout. It shares no Git history with it and never modifies it.

## Target

| | |
| --- | --- |
| Game | Dragon Ball Z: Buu's Fury |
| Platform | Game Boy Advance |
| Region / revision | USA, rev0 |
| Size | 8,388,608 bytes (8 MiB) |
| Game code | `BG3E` |
| **Canonical SHA-1** | `f1c4b07554d2a3b1ad2f325307051e775ce68087` |
| SHA-256 | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| CRC-32 | `01C1707F` |

The identical image is known to the LOG1-REMAKE project as profile
`buus_fury_usa_rev0_01c1707f`. One ROM, two naming conventions - **not** two
revisions.

## The baserom is never tracked

You must supply your own legally dumped copy. Nothing in this repository
contains ROM data, and `.gitignore` is written so that a stray `git add -A`
cannot publish one.

```powershell
# any one of these works
Copy-Item 'D:\dumps\Dragon Ball Z - Buu''s Fury (U).gba' .\baserom.gba
$env:BUUSFURY_ROM = 'D:\dumps\Dragon Ball Z - Buu''s Fury (U).gba'
pwsh -File scripts/check.ps1 -Rom 'D:\dumps\...gba'
```

The pipeline fails closed on any mismatch. It will not run on a wrong revision,
a wrong region, a truncated file, or a single flipped byte.

## Quick start

```powershell
pwsh -File scripts/check.ps1                 # every achievable gate, one summary
pwsh -File scripts/fetch-reference.ps1 -BuildTools   # source assets for the asset gate
pwsh -File scripts/build.ps1                 # strict build; stops with a precise blocker
pwsh -File scripts/build.ps1 -AllowPassthrough       # byte-identical image + provenance report
```

## Where the project stands

See [`docs/DECOMP_BASELINE.md`](docs/DECOMP_BASELINE.md) for the full baseline,
[`docs/VALIDATION_REPORT.md`](docs/VALIDATION_REPORT.md) for the measured
results, [`docs/ROM_MAP.md`](docs/ROM_MAP.md) for the independent structural ROM
map, [`docs/ROM_MAP_PROVENANCE.md`](docs/ROM_MAP_PROVENANCE.md) for why each of
its boundaries is believed, and [`docs/BUILD_REGIONS.md`](docs/BUILD_REGIONS.md)
for what the build does with each byte.

Two models, deliberately kept apart: `BUILD_REGIONS.md` answers *who builds the
bytes*, `ROM_MAP.md` answers *what the bytes are*.

### Structural coverage (DECOMP-ROM-MAP-001, measured 2026-09-29)

| Classification | Bytes | Share |
| --- | ---: | ---: |
| `unknown` | 4,554,062 | 54.289% |
| `compressed_asset` | 3,060,696 | 36.486% |
| `padding` | 292,442 | 3.486% |
| `pointer_table` | 166,260 | 1.982% |
| `code` | 104,796 | 1.249% |
| `strings` | 82,874 | 0.988% |
| `code_candidate` | 81,742 | 0.974% |
| `lookup_table` | 42,366 | 0.505% |
| `library_data` | 2,050 | 0.024% |
| `palette` | 1,024 | 0.012% |
| `header` + `structured_data` | 296 | 0.004% |

Executable bytes: **9,684 `confirmed`** (a lower bound, from recursive
reachability) plus 168,662 `probable`. Candidate functions: **341** (3 confirmed
ARM, 1 probable ARM, 5 confirmed Thumb, 332 probable Thumb).

The 54% `unknown` is a measured property of the cartridge, not a gap in effort:
this engine's Thumb data decodes at roughly 94%, so a UTF-16LE text pool or a
pointer table decodes end to end exactly like code. The map refuses to guess
rather than over-claim; see
[`ROM_MAP_PROVENANCE.md`](docs/ROM_MAP_PROVENANCE.md) section 3.

### Build coverage (DECOMP-BASELINE-001, measured 2026-09-28)

| class | bytes | share | regions | status |
| --- | ---: | ---: | ---: | --- |
| `incbin` - opaque, copied from the baserom | 8,268,480 | 98.568% | 13 | not yet decompiled |
| `asset` - grit / JCALG1 / palette | 26,112 | 0.311% | 10 | **reproduced byte-identically** |
| `ads` - ARM Developer Suite 1.2 | 94,016 | 1.121% | 5 | **blocked**, see below |
| **total** | **8,388,608** | **100.000%** | **28** | |

The single blocker to a full source reproduction is **ARM Developer Suite 1.2**:
it is commercial software, it is not installed, it cannot be redistributed, and
the only public source for the 94,016 bytes it produces carries no licence and
therefore cannot be imported. See
[`docs/ADS12_SETUP.md`](docs/ADS12_SETUP.md) and
[`docs/DECOMP_BASELINE.md`](docs/DECOMP_BASELINE.md#the-blocker).

### Value-stack arithmetic (DECOMP-LIFT-SCRIPT-ARITH-001, measured 2026-09-29)

Slots **8** (`0x08003D52`) and **9** (`0x08003D66`) complete the arithmetic family
begun by slot 7, source at
[`src/ByteCodeInterpreter_arith.c`](src/ByteCodeInterpreter_arith.c). 20 bytes and
10 instructions each.

| Verdict | Result | Question it answers |
| --- | --- | --- |
| `SEMANTIC` | **PROVEN** | do they pop correctly? 45 assertions, 0 failures |
| `MODERN_BUILD` | **PASS** | do they compile, link at `0x08003D52` and emit bytes? 40 bytes |
| `ADS_MATCH` | **BLOCKED** | does it reproduce the original compiler? `ADS12_LICENSE_UNAVAILABLE` |

The three members tile `0x08003D3E..0x08003D7A` and differ in one instruction:
`adds r1,r2,r1`, `subs r1,r2,r1`, `muls r2,r1,r2`. **Operand order is now proven
directly** rather than by sibling inference: subtraction is not commutative, and
`subs r1, r2, r1` shows the deeper value is the **first** source and the top the
**second**. The shared contract - pop two, produce one, delta count -1, result in
the **lower** slot, counter written before the reads, **no underflow check** - is
derived from the ROM for all three. Slot 7's report is **byte-identical** to
before this ticket. See [`docs/LIFT_ARITH.md`](docs/LIFT_ARITH.md).

### Value-stack consumer (DECOMP-LIFT-SCRIPT-STACK-001, measured 2026-09-29)

The first **consumer** of the interpreter's value stack: primary dispatch slot 7 at
`0x08003D3E`, 20 bytes and 10 instructions, source at
[`src/ByteCodeInterpreter_stack.c`](src/ByteCodeInterpreter_stack.c).

| Verdict | Result | Question it answers |
| --- | --- | --- |
| `SEMANTIC` | **PROVEN** | does it pop correctly? 34 assertions, 0 failures |
| `MODERN_BUILD` | **PASS** | does it compile, link at `0x08003D3E` and emit bytes? 20 bytes |
| `ADS_MATCH` | **BLOCKED** | does it reproduce the original compiler? `ADS12_LICENSE_UNAVAILABLE` |

The consumer was found **mechanically**: a scan of both proven dispatch tables for
the value-stack pop idiom found **84 functions holding it, 111 pops in total**.
This one is the smallest. It **pops** the top value, adds it to the new top in
place, and leaves the sum in the **lower** slot; the counter is written back
before the operand reads. There is **no underflow check**: a zero counter becomes
`0xFFFFFFFF`, the slot address becomes `context-4`, and the handler decrements the
word immediately below the context object, walking four bytes further down each
time. That is reproduced exactly, with no guard added.

The modern build is the **same size** as the original for the first time - 20
bytes and 10 instructions - but 9 bytes still differ, so this is a size
coincidence and **not a match**; a test asserts that. See
[`docs/LIFT_STACK.md`](docs/LIFT_STACK.md).

### Operand reader (DECOMP-LIFT-SCRIPT-SM7-001, measured 2026-09-29)

Primary dispatch slot 1 at `0x08003C8A`, 52 bytes and 26 instructions, source at
[`src/ByteCodeInterpreter_operand.c`](src/ByteCodeInterpreter_operand.c). It reads
a variable-length operand from the cursor and pushes it onto the context's value
stack. A **leaf**: no calls and no literal pool, so it needed no helper lifted with
it.

| Verdict | Result | Question it answers |
| --- | --- | --- |
| `SEMANTIC` | **PROVEN** | does it decode correctly? 42 assertions, 0 failures, exhaustive over every 1- and 2-byte input |
| `MODERN_BUILD` | **PASS** | does it compile, link at `0x08003C8A` and emit bytes? 86 bytes |
| `ADS_MATCH` | **BLOCKED** | does it reproduce the original compiler? `ADS12_LICENSE_UNAVAILABLE` |

The format, read off the instructions: **big-endian base-128 sign-magnitude**.
Bit 7 of each byte continues the sequence, bit 0 of the accumulator is the sign,
and the magnitude is extracted with an **arithmetic** shift. 1 byte reaches Â±63,
2 Â±8191, 3 Â±1048575, 4 Â±134217727. The encoding is **not canonical** (`0x02` and
`0x80 0x02` are both +1) and there are **two zeros**. There is **no length limit
and no validation**; the reconstruction adds none.

The arithmetic shift means the sign inverts once accumulator bit 31 is set, so the
maximal five-group sequence `FF FF FF FF 7F` decodes to **+1**, not -2147483647.
That is the code's actual behaviour, reproduced exactly rather than corrected.

**"sm7" is not a ROM string.** It is a project nickname, recorded as a candidate
alias only. See [`docs/LIFT_OPERAND.md`](docs/LIFT_OPERAND.md).

### Script engine handler (DECOMP-LIFT-SCRIPT-HANDLER-001, measured 2026-09-29)

The first opcode handler is lifted: **primary dispatch slot 2** at `0x08003CBE`,
22 bytes and 10 instructions, source at
[`src/ByteCodeInterpreter_handlers.c`](src/ByteCodeInterpreter_handlers.c). It is
the handler that reaches the native dispatch table at `0x08055098`.

| Verdict | Result | Question it answers |
| --- | --- | --- |
| `SEMANTIC` | **PROVEN** | does it behave correctly? 23 assertions, 0 failures, measured by RUNNING it |
| `MODERN_BUILD` | **PASS** | does it compile, link at `0x08003CBE` and emit bytes? 40 bytes |
| `ADS_MATCH` | **BLOCKED** | does it reproduce the original compiler? `ADS12_LICENSE_UNAVAILABLE` |

It consumes a **one-byte** native index, advances the cursor by one, and calls
`native[index]` through the `bx r1` thunk with `r0` untouched. It never writes
`r0`, so the context passes through unchanged.

**The native table has 266 entries, not 283.** The count is bounded on both sides:
the one-byte index needs at least 256, and the primary dispatch table's base at
`0x080554C0` caps it at exactly 266. A 283-entry table would run through the
primary table. Independently, the project's 2026 runtime capture recorded slot 178
dispatching to `0x08003030`, and reading index 178 statically gives `0x08003031`,
masking to the same address. See [`docs/LIFT_HANDLER2.md`](docs/LIFT_HANDLER2.md).

### Script engine (DECOMP-LIFT-SCRIPT-001, measured 2026-09-29)

The first real engine subsystem is lifted: the **ByteCodeInterpreter**, three Thumb
functions at `0x08004038..0x08004160`, source at
[`src/ByteCodeInterpreter.c`](src/ByteCodeInterpreter.c). The ROM preserves the
original source path, which is why the file exists under that name:
`T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp`.

| Verdict | Result | Question it answers |
| --- | --- | --- |
| `SEMANTIC` | **PROVEN** | does it behave correctly? 70 assertions, 0 failures, measured by RUNNING it |
| `MODERN_BUILD` | **PASS** | does it compile, link at `0x08004038` and emit bytes? 486 bytes |
| `ADS_MATCH` | **BLOCKED** | does it reproduce the original compiler? `ADS12_LICENSE_UNAVAILABLE` |

Its boundary is **derived from the ROM on every run** and raises on disagreement, and
the 31-entry dispatch table's extent is proved by the assertion string that follows it
rather than by a remembered number. The comparison: 284 of 296 bytes differ and the
modern build is 64% larger, while the **call counts and return structure match
exactly**. No opcode is decoded; unknown semantics are named by offset and said to be
unknown. See [`docs/LIFT_SCRIPT.md`](docs/LIFT_SCRIPT.md).

### Lifting loop (DECOMP-LIFT-PILOT-001, measured 2026-09-29)

The first function family is decompiled and the loop that produced it is reusable:
the **GBARam allocator**, eight Thumb functions at `0x03D4D0..0x03D740`, source at
[`src/GBARam.c`](src/GBARam.c).

| Verdict | Result | Question it answers |
| --- | --- | --- |
| `SEMANTIC` | **PROVEN** | does it behave correctly? 230 assertions, 0 failures, measured by RUNNING it |
| `MODERN_BUILD` | **PASS** | does it compile, link at its original address and emit bytes? 772 bytes |
| `ADS_MATCH` | **BLOCKED** | does it reproduce the original compiler? `ADS12_LICENSE_UNAVAILABLE` |

The three are independent and none is evidence for another. A modern GCC build is
**not** a match and is never reported as one: the comparison is a measurement, with
`is_a_match_claim: false`.

What the comparison found: 595 of 624 bytes differ and the modern build is 23.7%
larger, while the **structure** agrees exactly - identical call counts and identical
literal-slot counts for all eight functions. The sharpest divergence is the literal
pool: the original keeps **one** shared pool reached by seven of eight functions
(which is itself the evidence that the region was a single translation unit), the
modern build keeps seven. See [`docs/LIFT_PILOT.md`](docs/LIFT_PILOT.md); add the next
family with [`docs/LIFT_LOOP.md`](docs/LIFT_LOOP.md).

## Layout

```
config/     ROM identity, region map, toolchain manifest, lift targets + reports
docs/       baseline, dependencies, ADS 1.2 setup, reference audit, ROM map, lift
src/        the reconstruction      (src/GBARam.c is the first lifted family)
asm/        assembly reconstruction (empty)
data/       extracted/derived data  (fixed regions, boot logo)
include/    shared headers          (empty)
tools/      the harness (pure stdlib Python)
scripts/    one-command entry points
tests/      portable regression tests
build/      all output; gitignored
reference/  fetched upstream; gitignored
```

## The harness

No third-party Python dependencies.

```powershell
$env:PYTHONPATH = "$PWD\tools"
python -m buusfury status    # every achievable gate, one summary
python -m buusfury verify    # canonical ROM identity, fail closed
python -m buusfury map       # region-map tiling and coverage
python -m buusfury doctor    # toolchain availability
python -m buusfury assets    # rebuild asset regions, compare to the ROM
python -m buusfury build     # assemble a ROM, with per-region provenance
python -m buusfury lift      # semantic lifting loop: build + compare one family
python -m buusfury rommap    # independent structural ROM map + function inventory
python -m buusfury fixed     # generate the zero-toolchain fixed regions
python -m pytest tests -q    # 467 tests
```

## Scope

This repository is at **DECOMP-LIFT-SCRIPT-ARITH-001**. It carries the identity
gate, the build model, the independent ROM map and the compiler probe, plus six
lifted units - the GBARam allocator, the ByteCodeInterpreter dispatch loop, its
primary dispatch slots 2 and 1, its first value-stack consumer, and the rest of
the value-stack arithmetic family - and the reusable loop that produced all six.

`ADS_MATCH` remains blocked: the ADS 1.2 installed on this machine is unlicensed, and
nothing here reduces that. The next work continues outward from the script engine; see
[`docs/LIFT_STACK.md`](docs/LIFT_STACK.md#10-recommended-next-work),
[`docs/LIFT_OPERAND.md`](docs/LIFT_OPERAND.md#10-recommended-next-work),
[`docs/LIFT_HANDLER2.md`](docs/LIFT_HANDLER2.md#9-recommended-next-work),
[`docs/LIFT_SCRIPT.md`](docs/LIFT_SCRIPT.md#8-recommended-next-bytecodeinterpreter-work)
and
[`docs/LIFT_PILOT.md`](docs/LIFT_PILOT.md#7-next-recommended-function-family).
