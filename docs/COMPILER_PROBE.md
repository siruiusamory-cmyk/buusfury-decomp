# Compiler probe: DECOMP-COMPILER-PROBE-001

    COMPILER PROBE: BLOCKED - ADS12_UNAVAILABLE

No compiler result is claimed by this ticket. What is claimed, and proven from
the canonical ROM alone, is the *probe corpus*: eight ordinary Thumb engine
functions with exact boundaries, a reconstruction hypothesis for their original
translation unit, a compiler configuration matrix, and a deterministic
compile/compare harness that fails closed. Every piece is in place for the first
run to produce an answer the moment ARM Developer Suite 1.2 is available.

- Repository: `C:\Dev\buusfury-decomp`
- Starting commit: `53fba714b4b4fe041e8223f27faed7151983ffe8`
- Canonical ROM SHA-1: `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged)
- Machine-readable results: `config/compiler_probes.json`, `config/compiler_matrix.json`

## 1. The question

    Which ADS 1.2 compiler invocation reproduces the original Webfoot machine code
    of ordinary Buu's Fury engine functions?

The strongest external clue was, and remains, a single preserved command line.
The reference project's `asm/GBARam.s` carries it in a header comment:

    tcpp -S -c -cpu ARM7TDMI -O1 src/GBARam.c

That is a lead about one file, not proof about the corpus. This ticket's job was
to convert it into a test.

## 2. What the tool name already implies (INFERRED, not proven)

In ARM Developer Suite 1.x the compiler drivers are named by instruction set and
by front end:

| driver | instruction set | front end |
| --- | --- | --- |
| `armcc` | ARM | C |
| `armcpp` | ARM | C++ |
| `tcc` | Thumb | C |
| `tcpp` | Thumb | C++ |

If that naming holds for the installation that produced this cartridge, then the
lead is not merely "some C compiler at `-O1`": `tcpp` already means **Thumb** and
**C++**. That is consistent with the independent observation that this region is
Thumb, and it is why `tcpp` is the front end tested first and why `tcc` is its
negative control.

This is `INFERRED`. The mapping must be confirmed against the installed
compiler's own documentation before it is used as reasoning, and the matrix
tests both front ends precisely because the inference is not proof.

## 3. The probe corpus

One translation unit, eight functions, all Thumb, all with exact boundaries:

| probe | rom address | file offset | bytes | insn | returns | leaf | literal loads |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `sub_0803D4D0` | `0x0803D4D0` | `0x03D4D0` | 24 | 12 | 1 | yes | 3 |
| `sub_0803D4E8` | `0x0803D4E8` | `0x03D4E8` | 56 | 28 | 1 | yes | 1 |
| `sub_0803D520` | `0x0803D520` | `0x03D520` | 40 | 20 | 1 | yes | 1 |
| `sub_0803D548` | `0x0803D548` | `0x03D548` | 34 | 17 | 1 | yes | 0 |
| `sub_0803D56A` | `0x0803D56A` | `0x03D56A` | 78 | 39 | 1 | yes | 1 |
| `sub_0803D5B8` | `0x0803D5B8` | `0x03D5B8` | 132 | 64 | 3 | no (1 callee) | 2 |
| `sub_0803D63C` | `0x0803D63C` | `0x03D63C` | 214 | 101 | 9 | no (3 callees) | 1 |
| `sub_0803D712` | `0x0803D712` | `0x03D712` | 30 | 15 | 1 | yes | 1 |

Totals: 608 bytes of code, 8 Thumb / 0 ARM, 6 leaf / 2 non-leaf, 7 of 8 with a
PC-relative literal load. The control-flow spread is deliberate: straight-line
code, forward conditional branches, a backward loop, early returns, and two
functions that call into the unit.

### Why this region

1. `config/rom_map.json` classifies `0x03D4D0..0x03D730` as `gbaram_code`,
   confidence `high`, executable `confirmed`.
2. The surviving command line names `src/GBARam.c`, and the reference build
   reproduces a checked-in `GBARam.s` from it: this region is that file's
   compiled output.
3. The region ends in a **single shared literal pool** at `0x03D730..0x03D740`
   holding `0x02000800`, `0x03003488`, `0x0000FDFE`, `0x7FFFFFFF`. Those are
   exactly the four values DECOMP-ROM-MAP-001 independently proved as the fixed
   region `gbaram_literals`, each loaded by the allocator's own PC-relative
   loads.
4. An independent chain walk recovers eight functions with zero gaps and zero
   undecodable bytes, so every boundary is evidence rather than a heuristic
   window.

### The allocator, as read

The evidence fixes the header layout but not the original field names:

    +0x00 u16    +0x02 u16 (size, in 4-byte words)    +0x04 u16
    +0x06 u8 (busy)    +0x08 u16    +0x0A u16

Index to pointer is `(u16 << 2) + 0x02000000`; the inverse is emitted as
`(ptr + 0xFE000000) >> 2`, an arithmetic shift, because `0x7F << 25` is
`-0x02000000`. An allocation is returned as `block + 8`. After unlink and
coalesce, the call graph is: `0x0803D5B8` calls `0x0803D4E8`;
`0x0803D63C` calls `0x0803D4E8`, `0x0803D56A`, `0x0803D520`. The other five
functions are leaves. `0x0803D5B8` has hundreds of external callers in
identified engine code, which is what makes this ordinary engine code rather
than a decoder artefact.

## 4. Boundary method

`config/functions.json` was **not** used for boundaries, and could not be. Its
`size` field is `analysis.decode_run(limit=0x400).bytes_ok`: a decode extent
capped at 1024 bytes. For `sub_0803D5B8` it runs 620 bytes, straight through
three neighbouring functions, and attributes their calls to it. Six of the eight
probes carry an inventory size that overruns the measured boundary; those
disagreements are recorded in `config/compiler_probes.json` under
`inventory_size_disagreements` rather than smoothed over.

The boundary method used instead is a **chain walk**: a recursive descent in the
unit's own instruction set that

- follows conditional branches and unconditional branches that stay inside the
  unit,
- treats a call as fall-through,
- terminates a path at `bx lr`, at `pop {..., pc}`, or at a tail branch leaving
  the unit,
- ends a function at the highest-address terminator it reached, and
- starts the next function immediately after, because every path of the
  previous one already terminated.

That last property is what makes the result evidence. A function that decoded
off the end of the image, or hit a byte that is not an instruction, or never
terminated, would be reported as a `problem` on its boundary instead of quietly
producing a plausible function list, and `derive_manifest()` would record it in
`consistency_problems`.

Two further cross-checks hold: the boundaries tile the code body exactly with no
gaps and no overlaps, and the literal pool begins precisely where the code body
ends.

## 5. Candidate source

`src/probes/GBARam.c` is the first reconstruction hypothesis. It is explicitly
**not validated**: no ADS 1.2 installation exists on the authoring machine, so
it has never been compiled by the tool it targets. It is written to be
structurally faithful to the disassembly and it compiles cleanly under a modern
GCC (used only as a plumbing control), but matching instruction-for-instruction
is the iteration the matrix exists to perform.

Assumptions are recorded in the file header rather than buried. Two are
genuinely unresolved and are called out:

- the `0x7FFFFFFF` guard in `sub_0803D5B8` is compared against a value read with
  `ldrh`, so it can never be taken. Either the original field is wider than 16
  bits, or the guard is a sentinel test whose emitted form is not obvious.
- in `sub_0803D56A` both list-neighbour updates store the word read from
  `block[1] + 0x04`, which does not read as a plain unlink.

Neither is hidden from the harness: both are in the source, and both are
candidates for the first thing a real compiler run will correct.

## 6. Compiler configuration matrix

The first row is the historical lead and is tried first. The rest are the
negative controls, without which a match would identify nothing.

| frontend | ISA | CPU | opt | why |
| --- | --- | --- | --- | --- |
| `tcpp` | Thumb | `ARM7TDMI` | `-O1` | the historical lead, verbatim |
| `tcpp` | Thumb | `ARM7TDMI` | `-O0` | negative control: optimisation off |
| `tcpp` | Thumb | `ARM7TDMI` | `-O2` | negative control: more optimisation |
| `tcc` | Thumb | `ARM7TDMI` | `-O1` | C front end instead of C++ |
| `armcpp` | ARM | `ARM7TDMI` | `-O1` | ARM front end, C++ |
| `armcc` | ARM | `ARM7TDMI` | `-O1` | ARM front end, C |

`-Ospace` and `-Otime` are documented ADS 1.2 variants on the optimization
axis. They are deliberately **not** in the committed matrix: the exact spelling
and interaction must come from the installed compiler's own help output, and the
ticket forbids blind brute force of undocumented flags. The `--plan` output
prints the configuration in use, so adding them once documented is a
one-line change.

## 7. The harness

    python -m buusfury compiler-probe [--rom ROM] [--ads12-root DIR]

| flag | effect |
| --- | --- |
| (none) | report the probe corpus and the blocked/tooled state |
| `--verify-manifest` | re-derive `config/compiler_probes.json` from the ROM and compare; FAIL on any disagreement |
| `--write-manifest` | regenerate the manifest from the ROM |
| `--write-matrix` | regenerate `config/compiler_matrix.json` |
| `--plan` | print the exact command sequence and the linker layout; execute nothing |
| `--matrix` | run every configuration in the matrix |
| `--diagnostic-control` | exercise the harness with devkitARM GCC; NEVER evidence |
| `--json` | machine-readable output |

Exit codes: `0` when a verdict was produced, `1` when no verdict could be
obtained (the blocked case, which fails closed), `2` on usage error.

Every comparison reports target size, candidate size, identical bytes, first
differing offset, number of differing bytes, number of differing instructions,
and an exact-match boolean. Assembly is compared as decoded instructions in
addition to raw bytes, never as text.

## 8. Relocation methodology

This is the part of the probe that is easiest to get wrong, so it is stated
explicitly rather than assumed.

**A function with a PC-relative literal load cannot be byte-compared on its
own.** Its `ldr rX, [pc, #N]` encodes a displacement to a literal pool.
Compiling that function alone puts the pool somewhere else, changes N, and
produces a mismatch for source that is perfectly correct. Seven of the eight
probes load a literal; only `sub_0803D548` is byte-comparable in isolation.

The chosen methodology is therefore **translation-unit scoped**:

1. compile the whole unit from `src/probes/GBARam.c` with
   `tcpp -S -c -cpu ARM7TDMI -O1` to assembly,
2. assemble it with `armasm`,
3. link it with `armlink -noremove -scatter probe.scatter`, where the scatter
   file places the unit's read-only region at its **original ROM address**
   `0x0803D4D0` so that every literal displacement and call offset is
   reproduced,
4. extract raw bytes with `fromelf probe.axf -bin -o probe.bin`, and
5. compare the full 624-byte span `0x0803D4D0..0x0803D740`, code plus literal
   pool, against the ROM.

Per-probe results are slices of that single build rather than separate
compilations, which is what keeps them comparable.

One assumption in step 4 cannot be exercised on this machine and is therefore
printed in every report as `ORIGIN_ASSUMPTION`: `fromelf -bin` on a scatter file
whose only load region is at the unit's ROM address is taken to emit from that
address. It is the first thing to confirm from real toolchain output.

Unresolved relocations are never allowed to masquerade as a compiler mismatch:
where a candidate object carries relocations, the link step resolves them
against the known original address before any comparison runs, and a failure to
produce a binary is reported as `TOOLCHAIN_BLOCKED` rather than as a difference.

## 9. Does translation-unit context matter?

Yes, necessarily, for anything with a literal load, and the harness is built to
measure rather than assume it. The observed layout is itself the evidence: seven
of eight functions share **one** pool at the end of the region, not one pool
each. That means the original was compiled as one translation unit, so the
comparison must be one too.

The `--plan` and `--matrix` paths make the alternative explicit: a
single-function standalone build would place the pool immediately after that
function and change every displacement in it. `sub_0803D548` is the control for
this: it has no literal load, so it should compare identically whether compiled
alone or in the unit. If it does not, the harness itself is wrong.

## 10. Repeated evidence and the success criterion

A compiler configuration is not proven because one tiny function matches. The
ticket's preferred criterion, implemented in `fingerprint()`:

- `PLAUSIBLE` on one exact match,
- `STRONGLY_SUPPORTED` on three or more,
- `PROVEN` on multiple *discriminating* exact matches, and
- `REFUTED` on repeated mismatches despite semantically correct source.

A two-instruction getter that compiles identically at `-O0`, `-O1` and `-O2` is
non-discriminating and cannot prove an optimization level; that is why the
corpus spans straight-line code, conditional branches, loops, early returns and
calls, and why the negative controls exist.

**Result on this machine: all seven claims are `UNTESTED`**, because the
toolchain is unavailable. See section 12.

## 11. Controls and rejected candidates

### Regions that may not be used as evidence

| id | rom address | ISA | why it is a control and not evidence |
| --- | --- | --- | --- |
| `reset_crt` | `0x080000C0` | ARM | startup/CRT code. The cartridge header branches here and it hands off to the ADS C runtime. |
| `crt_veneer` | `0x08049114` | ARM | the ADS C runtime static-initialiser veneer; library code, not engine code. |
| `codec_blob` | `0x087B79A4` | ARM | may be hand-written or library/codec assembly; not representative. |

### Candidates examined and rejected, with the measurement that rejected them

| candidate | map claim | rejected because |
| --- | --- | --- |
| `code_reachable_055324` | code, `high`, executable `confirmed` | **it is data.** It decodes only as a repeating `cmp rX, #imm` / `lsrs r0, r0, #0x20` pair, i.e. a table of halfwords followed by `0x0808`. |
| `code_candidate_span_6_048F14` | code_candidate, `medium`, ARM | does not decode as ARM at all; the first word is an NV-condition word, the signature of data. No ARM probe can be built here. |
| `code_candidate_span_5_03D2D0` | code_candidate, `medium`, Thumb | the chain walk reaches an impossible "40 bytes / 137 instructions" entry and two functions with no terminator, so the span mixes inline data with code. |
| `code_reachable_02E1C0` | code, `high`, executable `confirmed` | real and reachable, but not independently bounded: the first function is 1022 bytes with 20 callees. Deferred, not refuted. |
| `sub_0803D5B8` entry in `config/functions.json` | `size=620` | the size is a decode extent; it overruns three functions and attributes their calls to it. Used as a cross-check only. |

The first two matter more than their length suggests. `code_reachable_055324`
carries the map's strongest code vocabulary and **is not code**. This is because
on this cartridge Thumb data is indistinguishable from Thumb code (a result
DECOMP-ROM-MAP-001 measured: about 94 percent of arbitrary halfwords are valid
Thumb), so a `high` classification is a statement about a window, never a
licence to build a probe on it.

### Why there is no ARM probe

The three confirmed ARM regions are the reset/CRT at `0x080000C0` (excluded by
the ticket), the C runtime veneer at `0x08049114` (library), and `codec_blob` at
`0x087B79A4` (excluded by the ticket as primary evidence). The one ARM
`code_candidate` does not decode. An ARM probe would have to be forced, and the
ticket explicitly permits the honest answer:

    ARM startup:      hand-written assembly          - NOT APPLICABLE
    ARM library/codec: tool origin unresolved

### Inventory gaps

`sub_0803D548` and `sub_0803D712` are **absent** from `config/functions.json`.
Neither is the target of a `BL`/`BLX` anywhere in the image and neither is a
literal-pool code pointer, so a branch-target inventory could not have found
them. They are nonetheless real: they decode completely, they terminate on
every path, and they sit inside a proven code region. They are recorded as a
measured gap in `inventory_gaps`, with the intermediate finding that the
previous ticket's inventory is incomplete for this region, rather than being
deleted to make a test pass.

## 12. Compiler fingerprint

| claim | state |
| --- | --- |
| Thumb front end (C vs C++) | `UNTESTED` |
| Thumb optimization | `UNTESTED` |
| Thumb CPU target | `UNTESTED` |
| ARM front end | `UNTESTED` |
| ARM optimization | `UNTESTED` |
| C vs C++ | `UNTESTED` |
| ABI characteristics | `UNTESTED` |

`UNTESTED` is defined as "toolchain unavailable". It is not a weak positive and
must not be read as one.

### What is NOT claimed

- No compiler setting has been proven, supported, or refuted.
- `tcpp -cpu ARM7TDMI -O1` remains a **lead**. The new Thumb/C++ reading of the
  driver name in section 2 is `INFERRED` from published tool naming, not measured.
- No modern compiler result is evidence about the original build. The GCC run in
  section 7 exists to prove the plumbing works and is tagged
  `DIAGNOSTIC_CONTROL_NOT_EVIDENCE` everywhere it appears.
- The candidate source is a hypothesis. It has not been validated.

## 13. Toolchain preflight

ADS 1.2 is **absent**. Established by six independent checks, none of which was
allowed to invent a path:

1. `ADS12_ROOT` is unset.
2. `shutil.which` finds none of `armcc`, `armcpp`, `tcc`, `tcpp`, `armasm`,
   `armlink`, `fromelf`, `armsd`, `axd`.
3. None of the plausible install roots exists (`C:\Program Files\ARM`,
   `C:\Program Files (x86)\ARM`, `C:\ARM`, `C:\ADS`, `C:\ADS12`, `C:\Keil`,
   `C:\Program Files (x86)\Keil`, and the `ADSv1_2` / `RVCT` variants).
4. No registry uninstall entry and no vendor key matches ARM / ADS / Developer
   Suite / RVCT / RealView / Keil. The only `ARM` matches are Windows SDK arm64
   components.
5. No Start Menu shortcut matches ARM / ADS / AXD / Multi-ICE.
6. Only one fixed drive exists (`C:`); a bounded scan of `C:\Dev`, `C:\Tools`,
   `C:\opt`, `D:\`, `E:\`, `F:\`, `Downloads`, `Desktop`, `Documents` and
   `AppData\Local\Programs` finds no ADS executable.

`C:\devkitPro\devkitARM` is present and is **not** ADS. It provides a modern GNU
toolchain that this ticket uses only as a labelled plumbing control.

ADS 1.2 was deliberately not downloaded. It is commercial software whose licence
does not permit redistribution, and the ticket forbids unofficial, abandonware
and warez sources. No proprietary binary, licence file or registry entry was
created or modified by this ticket.

## 14. Exact command required once ADS is supplied

    set ADS12_ROOT=<installation root>
    python -m buusfury compiler-probe --plan      # review the commands first
    python -m buusfury compiler-probe --matrix    # run the matrix

The plan resolves to this pipeline, with `<root>` substituted for the real
installation:

    <root>\Bin\tcpp.exe    -S -c -cpu ARM7TDMI -O1 -o probe.s   src\probes\GBARam.c
    <root>\Bin\armasm.exe  -cpu ARM7TDMI          -o probe.o    probe.s
    <root>\Bin\armlink.exe -noremove -scatter probe.scatter -o probe.axf probe.o
    <root>\Bin\fromelf.exe probe.axf -bin -o probe.bin

### Expected `ADS12_ROOT` layout

    <ADS12_ROOT>\
        Bin\
            armcc.exe    armcpp.exe    tcc.exe     tcpp.exe
            armasm.exe   armlink.exe   fromelf.exe
        Include\
        Lib\
        ...

The harness looks for `<root>/Bin/<tool>.exe`, then `<root>/<tool>.exe`, then
`PATH`, and never invents a path. Everything it writes goes under
`build/probes/`, which is gitignored.

## 15. Tests

`tests/test_compiler_probe.py`, 53 tests, all passing. Portable and ROM-gated
tests are deliberately separated; a missing ADS installation is a *passing*
state for the suite because the ticket's contract is that the blocker is
measured, not that it is absent.

Covered, per the ticket's list: probe manifest validity; probe addresses present
in `config/functions.json` or recorded as a measured gap; ISA consistency;
target-byte extraction against per-probe SHA-1 digests; complete decoding of
each declared span; no overlapping probe ranges and exact tiling of the code
body; deterministic comparison; a wrong ROM refused before any probe runs; the
canonical ROM unmutated by probe reads (digest and mtime); toolchain absence
producing `BLOCKED` and never a false PASS or an `exact_match`; no proprietary
binary or licence tracked and every ADS tool name gitignored; and no write path
into the other checkout.

## 16. Next ticket

If ADS 1.2 is supplied and three or more discriminating probe functions match
byte-for-byte under one configuration, the next ticket is
`DECOMP-MATCH-LOOP-001`, which turns the proven recipe into the permanent
per-function compile/diff workflow.

If three exact discriminating matches cannot be obtained, the correct result is
`INCONCLUSIVE` with the per-configuration differences preserved, not a forced
conclusion. `config/compiler_matrix.json` already records every configuration in
machine-readable form for exactly that outcome.
