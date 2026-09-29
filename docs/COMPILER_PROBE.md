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
capped at 1024 bytes. Measured against this unit, it records 620 bytes for
`0x0803D4D0` where the boundary is 24, and 388 bytes for `0x0803D5B8` where the
boundary is 132; both spans run to `0x0803D73C`, straight through neighbouring
functions and into the literal pool, and both carry the same contaminated callee
list (`0x0803D4E8`, `0x0803D520`, `0x0803D56A`) because those are the
neighbours' calls. Six of the eight probes carry an inventory size that overruns
the measured boundary; those disagreements are recorded in
`config/compiler_probes.json` under `inventory_size_disagreements` rather than
smoothed over.

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
| `--verify-manifest` | re-derive `config/compiler_probes.json` and compare the WHOLE document; FAIL on any disagreement |
| `--verify-matrix` | re-derive `config/compiler_matrix.json` and compare the whole document |
| `--write-manifest` | regenerate the manifest from the ROM |
| `--write-matrix` | regenerate `config/compiler_matrix.json` |
| `--plan` | print the exact command sequence and the linker layout; execute nothing |
| `--matrix` | run every configuration in the matrix |
| `--diagnostic-control` | exercise the harness with devkitARM GCC; NEVER evidence |
| `--json` | machine-readable output |

The modes are mutually exclusive, so a combined invocation is a usage error
rather than silently running only one of them.

Exit codes:

| code | meaning |
| --- | --- |
| `0` | a verdict was produced, or the requested check passed (`--plan` and `--verify-*` always exit 0 on success because they execute nothing failing) |
| `1` | no verdict could be obtained, or a check failed. **`--json` does not change this**: a blocked probe exits non-zero with or without `--json` |
| `2` | usage error |

`--matrix` exits 0 **only if at least one configuration actually compared
bytes**. A matrix in which every configuration is blocked is a failure to obtain
a verdict, not a pass. When some configurations ran and some did not, the
document says `COMPILER PROBE: PARTIAL (N of M configurations compared)` rather
than `COMPLETE`, because the configurations that did not run may include exactly
the negative controls the claim depends on.

Gate 6 in `scripts/check.ps1` reads that JSON and branches on the document's own
**top-level** `code` and `comparisons_run` fields, never on a substring of the
document text. That distinction is load-bearing: in a `PARTIAL` matrix the
blocked *rows* still carry `"code": "ADS12_UNAVAILABLE"`, so a substring test
would report a run that did compare bytes as `BLOCKED`. The gate also parses
stdout only, because a warning on stderr merged into the stream would break the
JSON and turn a working probe into a false `FAIL`. Both hazards have tests.

Every comparison reports target size, candidate size, identical bytes, first
differing offset with its ROM address, number of differing bytes, the target's
instruction count, the number of those instructions whose encoding differs, and
an exact-match boolean. Instruction counts are keyed on the **target's**
instruction boundaries, never on a positional walk of both streams: capstone
renders distinct Thumb encodings as the same text (127 colliding
`(mnemonic, op_str)` pairs exist among the 65,536 halfwords, for example
`0x4280` and `0x4500` both being `cmp r0, r0`), so a text comparison can report
zero differing instructions for bytes that are not equal.

The guarantee "unequal bytes imply a differing instruction" is scoped to a
target that **decodes fully**, which every real probe does and a test asserts.
When the target's own bytes do not decode to a single instruction there is
nothing to compare instruction-wise: those bytes are published as
`undecoded_target_bytes` rather than folded into the instruction count, and
`matching_instructions` is clamped at zero so it can never be negative. Assembly
is compared as decoded instructions in addition to raw bytes, never as text
alone.

`no_compiler_result_claimed` means **no setting was identified**, that is, no
claim reached `PROVEN` or `STRONGLY_SUPPORTED`. It does not mean nothing was
learned: a run whose lead matched nothing is a real result and is reported
separately in `refuted_claims`.

### Identifying the toolchain

A tool is accepted only if it **identifies as ARM ADS/RVCT from its own banner**.
The executable name alone is not enough: `tcc` is also the name of the Tiny C
Compiler, so accepting any executable called `tcc.exe` would let an unrelated
compiler's mismatches be published as a finding about the original build. When
`ADS12_ROOT` is set, the lookup is confined to it and `PATH` is not consulted,
so an unrelated same-named binary cannot be substituted for the requested
installation. An unidentifiable tool is treated as absent, and the exact banner
and version of an identified one are recorded in the matrix.

Two limits on this are published in the matrix as `toolchain_identification`:
only the compiler is required to identify, and the no-argument banner probe
itself is unexercised against a real ADS 1.2 installation. A genuine install
whose compiler prints nothing on a bare invocation would be reported absent, and
the whole `-S`/`armasm`/`armlink`/`fromelf` pipeline has never been run here.

The marker list deliberately includes the instruction-set-specific Thumb
wordings, `ARM Thumb C Compiler` and `ARM Thumb C++ Compiler`, because the
surviving command line names the Thumb drivers `tcpp`. Without them a correctly
installed ADS 1.2 could be reported absent, which is a false negative in the
fail-closed direction. That wording has **not** been observed from real ADS
output; it is a precaution, and every phrase added is ARM-branded, so the Tiny C
Compiler's banner is still rejected.

Lookup order, which is bounded and never invents a path: `$ADS12_ROOT/Bin/<tool>.exe`,
`$ADS12_ROOT/<tool>.exe`, then one level down at
`$ADS12_ROOT/<product>/Bin/<tool>.exe` because ADS 1.2 installs as a versioned
product directory and an operator may reasonably point `ADS12_ROOT` at either
the version directory or its parent. `PATH` is consulted **only** when
`ADS12_ROOT` itself is unset. A tool two or more levels down is not found.

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

- `REFUTED` when the favoured configuration matched none of the eight probe
  functions,
- `PLAUSIBLE` when it matched but the competing setting produced **identical**
  results, or when no competing setting ran at all, or when only one function
  matched,
- `STRONGLY_SUPPORTED` on two or more discriminating function matches,
- `PROVEN` when all eight match AND a competing setting that actually ran
  differs, and
- `UNTESTED` when the configurations never compared bytes at all.

Each claim is scored from **its own** two discriminating configurations, not
from one pooled set of evidence:

| claim | discriminated by |
| --- | --- |
| Thumb front end | `tcpp -O1` against `tcc -O1` |
| Thumb optimization | `tcpp -O1` against `tcpp -O0` and `-O2` |
| C vs C++ | `tcpp -O1` against `tcc -O1` |
| ARM front end | `armcpp -O1` against `armcc -O1` |
| Thumb CPU target | **nothing**: the CPU is ARM7TDMI in every configuration, so this claim is structurally capped at `PLAUSIBLE` |
| ARM optimization | **nothing**: no ARM row varies `-O`, and there is no ARM probe corpus to optimize, so `UNTESTED` |
| ABI | **nothing**: no ABI-affecting flag is varied, so `UNTESTED` |

**A competitor that never ran cannot promote a claim.** If the favoured
configuration compared bytes but its competing configuration was blocked or
absent, the claim is capped at `PLAUSIBLE`, and the cap is recorded in
`_evidence.claims_capped_for_a_missing_competitor`. Treating "the competitor did
not run" as "the competitor differs" would publish `PROVEN` for a setting with
no discriminating evidence at all, and that becomes reachable the moment a
partially installed toolchain runs only some configurations.

The score counts matching probe **functions** under one shared configuration,
and `PROVEN` additionally requires all eight of them. Counting matching
configurations would invert the meaning: `-O0`, `-O1` and `-O2` all matching is
exactly the non-discriminating case, not three independent confirmations. A
single matching function is `PLAUSIBLE`, not `STRONGLY_SUPPORTED`, because the
ticket's bar is three. That is also why the corpus spans straight-line code,
conditional branches, loops, early returns and calls, and why the negative
controls exist.

Per-function results are slices of the one translation-unit build, reported as
`probe_matches` on each configuration, because the ticket's criterion is stated
per function ("at least three unrelated ordinary engine functions match
byte-for-byte under the same compiler configuration"). They are not independent
builds: the shared literal pool is what makes one build the only comparable
thing.

**Result on this machine: every claim is `UNTESTED`**, because no configuration
compared bytes. See section 12.

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
| `sub_0803D4D0` entry | `size=620` | the size is a decode extent; 620 bytes runs to `0x0803D73C`, spanning the whole unit plus 12 bytes of its pool, and its callee list is its neighbours' calls. The measured boundary is 24 bytes with no calls. |
| `sub_0803D5B8` entry | `size=388` | the same defect: 388 bytes runs to `0x0803D73C`, through `0x0803D63C` and `0x0803D712` and into the pool. The measured boundary is 132 bytes with one distinct callee. |

The first two matter more than their length suggests. `code_reachable_055324`
carries the map's strongest code vocabulary and **is not code**. This is because
on this cartridge Thumb data is indistinguishable from Thumb code (a result
DECOMP-ROM-MAP-001 measured: about 94 percent of arbitrary halfwords are valid
Thumb), so a `high` classification is a statement about a window, never a
licence to build a probe on it.

### Why there is no ARM probe

Measured from `config/rom_map.json`, exactly **two** regions are `isa=arm` with
`executable=confirmed`: the reset/CRT at `0x080000C0` (excluded by the ticket)
and `codec_blob` at `0x087B79A4` (excluded by the ticket as primary evidence).
The ARM veneer at `0x08049114` is not a region start at all: it lies inside
`code_candidate_span_6_048F14` (`0x08048F14..0x08049324`, `code_candidate`,
`medium`, executable `probable`), which is also the only ARM candidate in the
image and the one that does not decode as ARM. An ARM probe would have to be
forced, and the ticket explicitly permits the honest answer:

    ARM startup:       hand-written assembly          - NOT APPLICABLE
    ARM library/codec: tool origin unresolved

`tests/test_compiler_probe.py` asserts this count against the map, so if a third
ARM region were ever confirmed as ordinary code the empty ARM corpus would fail
loudly instead of being inherited silently.

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
| ARM optimization | `UNTESTED` (structurally untestable by this matrix) |
| C vs C++ | `UNTESTED` |
| ABI characteristics | `UNTESTED` (no ABI-affecting flag is varied) |

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

**Re-checked 2026-09-29 for the ADS execution pass, after ADS 1.2 was expected to
be installed. It is still absent.** The second preflight is independent of the
first and reaches the same result by six checks, none of which may invent a path:

1. `ADS12_ROOT` is unset in the process environment, and empty for both the User
   and the Machine scopes in the registry.
2. `shutil.which` finds none of `armcc`, `armcpp`, `tcc`, `tcpp`, `armasm`,
   `armlink`, `fromelf`, `armsd`, `axd`.
3. None of the plausible install roots exists (`C:\Program Files\ARM`,
   `C:\Program Files (x86)\ARM`, `C:\ARM`, `C:\ADS`, `C:\ADS12`, `C:\Keil`,
   `C:\Dev\ADS`, `C:\Tools\ADS`, and the `ADSv1_2` / `RVCT` variants).
4. No registry uninstall entry and no vendor key matches ARM / ADS / Developer
   Suite / RVCT / RealView / Keil. A search for the ARM-specific file names at
   depth 5 under `Program Files`, `Program Files (x86)`, `C:\Dev`, `C:\Tools`,
   `Downloads`, `Desktop`, `Documents` and `C:\opt` returns nothing.
5. No Start Menu shortcut matches ARM / ADS / AXD / Multi-ICE.
6. Only **one** volume exists (`C:`, label `Acer`, 475 GB), and a search for an
   unextracted installer or archive (`*ADS*`, `*ARM*Developer*`, `*RVCT*`,
   `*ads1*`, `*armcc*`, `*armasm*` and `.iso` variants) under `Downloads`,
   `Desktop`, `Documents`, `C:\Dev`, `C:\Temp` and `%TEMP%` finds no such file.

The harness was then run in that state and behaved correctly: `--plan` reported
`BLOCKED [ADS12_UNAVAILABLE]` with every required tool `MISSING`, and
`--matrix --json` reported `result: COMPILER PROBE: BLOCKED - ADS12_UNAVAILABLE`,
`code: ADS12_UNAVAILABLE`, `comparisons_run: 0`, `conclusion: UNTESTED`,
`no_compiler_result_claimed: true`, `promoted_claims: []` and exit 1. No compiler
result was produced or claimed, and neither assumption could be exercised.

### What the first preflight found

The earlier preflight established the same absence, and its detail is retained
below because it is the baseline this second pass confirms rather than replaces.

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

Because the installation could not be found, the two ways the harness could
itself have produced a *false* `ADS12_UNAVAILABLE` were closed, without
weakening anything: the banner markers now include the Thumb-specific driver
wordings, and the root lookup searches one level down for a versioned product
directory. Both are precautionary rather than observed, both are labelled as
such, and both have tests, including one asserting that the deeper search does
**not** wander further than one level so no path can be invented.

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

The harness looks for `<root>/Bin/<tool>.exe`, then `<root>/<tool>.exe`, and
never invents a path. When `ADS12_ROOT` is supplied, `PATH` is not consulted.
What it writes automatically goes under `build/probes/`, which is gitignored;
the only writes outside it are the two committed results, and those happen only
when `--write-manifest` or `--write-matrix` is passed explicitly, because a
generated config file must be a deliberate act. A test runs the whole blocked
harness and asserts the working tree is unchanged.

## 15. Verifying the committed results

`--verify-manifest` regenerates the entire manifest and compares **every** field,
not a hand-picked subset, so a document whose `controls`, `rejections`,
`method`, `notes`, `schema` or `generated_by` had been rewritten would be
rejected. Tests tamper with each of those fields in turn and assert the
tampering is caught.

Because the manifest embeds three fields derived from `config/functions.json`,
that inventory is pinned inside the manifest by SHA-1, and a changed inventory is
reported as `INVENTORY DRIFT` explicitly distinguished from ROM drift, rather
than blaming the ROM for a difference the ROM did not cause.

`--verify-matrix` does the same for `config/compiler_matrix.json`, which
previously had no drift check at all. The committed matrix is written to be
environment-independent, so its blocked state is reproducible on any machine
without ADS; on a machine **with** an identified ADS 1.2 the matrix must be
regenerated, and `--verify-matrix` will say so.

## 16. Tests

`tests/test_compiler_probe.py`, 88 tests, all passing. Portable and ROM-gated
tests are deliberately separated; a missing ADS installation is a *passing*
state for the suite because the ticket's contract is that the blocker is
measured, not that it is absent. A further test asserts that running the whole
blocked harness leaves the working tree byte-for-byte unchanged.

Covered, per the ticket's list: probe manifest validity; probe addresses present
in `config/functions.json` or recorded as a measured gap; ISA consistency;
target-byte extraction against per-probe SHA-1 digests; complete decoding of
each declared span; no overlapping probe ranges and exact tiling of the code
body; deterministic comparison; a wrong ROM refused before any probe runs; the
canonical ROM unmutated by probe reads (digest and mtime); toolchain absence
producing `BLOCKED` and never a false PASS or an `exact_match`; no proprietary
binary or licence tracked and every ADS tool name refused by Git itself; and no
write path into the other checkout.

Beyond the ticket's list, and directly from the independent review:

- a blocked toolchain can never produce a `COMPLETE` document, a `REFUTED`
  claim, or exit code 0, and a winner whose competing configuration never ran
  cannot be promoted above `PLAUSIBLE`;
- a `PARTIAL` matrix keeps `code: null` at the top level while its blocked rows
  carry `ADS12_UNAVAILABLE`, which is the trap a substring-reading gate would
  fall into; and stderr noise cannot break the gate's JSON parse;
- the fingerprint is per claim, counts matching functions rather than matching
  configurations, cannot promote the CPU, ARM-optimization or ABI claims, and
  cannot reach `PROVEN` on a single function;
- tampering with any field of the manifest or the matrix is detected, including
  type-substituted values such as `true` for `1`, and a valid-JSON non-object
  manifest is reported rather than crashing;
- inventory drift is reported separately from ROM drift;
- `compare_bytes` cannot report zero differing instructions for unequal bytes
  when the target decodes fully, and `matching_instructions` is clamped at zero
  for every input including an undecodable target;
- an executable named `tcpp.exe` is not accepted as ARM's compiler, the Tiny C
  Compiler's banner is rejected, and an explicit `ADS12_ROOT` never falls back
  to `PATH`;
- every control names a region that exists in `config/rom_map.json` with the
  declared ISA, confidence and executable state, and exactly two regions are
  ARM and confirmed;
- the probe files this ticket adds are ASCII, LF-only and BOM-free;
- the CLI's exit codes are checked by running it, not by reading its source.

## 17. Independent review

The implementation was frozen at commit `c6882ae` and put through an independent
adversarial review whose method was its own, not this ticket's. It re-derived
the eight boundaries by exhaustive halfword-pattern `BL`/`BLX` census over all
8,388,608 bytes plus a from-scratch reachability fixpoint, and it reconstructed
the manifest and matrix in memory.

It **confirmed the measured core**: 296 instruction starts over 304 halfword
slots, the eight closures tiling `0x0803D4D0..0x0803D730` exactly, zero
undecodable bytes, zero escapes, every closure's reachable maximum equal to its
declared end, no ninth function, no aligned pointer into the region, all ten
PC-relative loads resolving into the same four-word pool, and the return and
instruction counts matching the manifest. It also confirmed the two inventory
gaps, the internal call graph, and the absence of any hardcoded path into the
other checkout.

It found, and this revision fixes, one blocker and nine major defects. The
blocker is the one worth naming: a toolchain that was discovered but useless
could be reported as `COMPLETE` with a `REFUTED` fingerprint and exit code 0,
because the matrix aggregated nothing and the fingerprint counted configurations
rather than functions. Also fixed: the manifest was compared only field by field
over six of its keys; a correct manifest could be rejected when the unpinned
inventory differed, with the message blaming the ROM; the "620 bytes for
`sub_0803D5B8`" claim was wrong (620 belongs to `sub_0803D4D0`, `sub_0803D5B8`
is 388); "three confirmed ARM regions" was wrong (there are two); instruction
comparison could report zero differing instructions for different bytes and a
negative matching count; gate 6 in `scripts/check.ps1` printed PASS for a run
that compared nothing; `--json` exited 0 on a blocked probe; and any
same-named executable was accepted as ADS.

The review's own verdict was **SOUND WITH FIXES**, with the boundary corpus
described as reliable as committed. A second verification round then confirmed
that blocker and seven of the nine majors resolved, and found that the first
revision of the fixes had introduced two new defects of its own: a claim could
be published as `PROVEN` when its competing configuration never ran, and gate 6's
PASS branch was unreachable because it matched a JSON field name against
human-readable output.

A third round confirmed both of those fixed - no row set reaches `PROVEN` or
`STRONGLY_SUPPORTED` without a competitor that ran and differed - and found
three narrow defects of the same class, all fixed here: the gate's BLOCKED
branch was still decided by a whole-document substring, so a `PARTIAL` matrix
whose rows carry `ADS12_UNAVAILABLE` was misreported as `BLOCKED`; stderr merged
into the gate's JSON stream could turn a working probe into a false `FAIL`; and
folding uncovered target bytes into the instruction count made
`matching_instructions` negative for an undecodable target. Each now has a test,
including one that pins the `PARTIAL`/row-code trap itself.

A fourth round returned **CLOSURE-READY** with two non-blocking one-liners, both
taken. The CPU claim published `REFUTED` for a row that the rest of the module
treats as unusable evidence, and the gate's blocker test preceded its comparison
test, so a hand-tampered document carrying both would have read `BLOCKED`. The
gate now requires `comparisons_run == 0` for the blocker branch, so a comparison
always wins, and a test pins the underlying invariant that `build_matrix` never
emits a non-null top-level `code` alongside a non-zero `comparisons_run`. Across
four rounds none of the findings could produce a false PASS or an unjustified
`PROVEN`.

## 18. Next ticket

If ADS 1.2 is supplied and three or more discriminating probe functions match
byte-for-byte under one configuration, the next ticket is
`DECOMP-MATCH-LOOP-001`, which turns the proven recipe into the permanent
per-function compile/diff workflow.

If three exact discriminating matches cannot be obtained, the correct result is
`INCONCLUSIVE` with the per-configuration differences preserved, not a forced
conclusion. `config/compiler_matrix.json` already records every configuration in
machine-readable form for exactly that outcome.
