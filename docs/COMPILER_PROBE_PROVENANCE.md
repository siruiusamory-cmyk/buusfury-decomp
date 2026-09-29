# Compiler probe provenance: DECOMP-COMPILER-PROBE-001

Companion to `docs/COMPILER_PROBE.md`. That document states the result and the
method; this one records where every claim came from, what was measured rather
than read, and what was deliberately not done. It exists so that a later reader
can re-derive or falsify each step instead of trusting it.

## 1. Identity and scope

| item | value |
| --- | --- |
| repository | `C:\Dev\buusfury-decomp` |
| starting commit | `53fba714b4b4fe041e8223f27faed7151983ffe8` |
| canonical ROM SHA-1 | `f1c4b07554d2a3b1ad2f325307051e775ce68087` |
| ROM size | 8,388,608 bytes |
| ROM path used | resolved through `tools/buusfury/identity.py`; never hardcoded in code |
| previous tickets | DECOMP-BASELINE-001, DECOMP-BOOTSTRAP-001, DECOMP-ROM-MAP-001 |
| bulk decompilation | not started, by the ticket's stop condition |
| other repository | `C:\Dev\log1-remake` (LOG1-REMAKE / Dragonbyte Z) not modified |

The ROM was opened read-only for every measurement. No test or tool writes to
it; `tests/test_compiler_probe.py` asserts both its SHA-1 and its `mtime_ns` are
unchanged around the probe's read path.

## 2. Toolchain inventory, measured 2026-09-29

### Present

| tool | version / path | used for |
| --- | --- | --- |
| Python | 3.12 (`python`) | the whole harness |
| capstone | 5.0.7 (`CS_ARCH_ARM`, `CS_MODE_ARM` / `CS_MODE_THUMB`) | all disassembly and comparison |
| numpy | 2.4.6 | inherited from the ROM-map tooling |
| `arm-none-eabi-gcc` | `C:\devkitPro\devkitARM\bin` | **plumbing control only** |

### Absent

`ADS12_ROOT` unset. None of `armcc`, `armcpp`, `tcc`, `tcpp`, `armasm`,
`armlink`, `fromelf`, `armsd`, `axd` is on `PATH`, in any plausible install root,
or behind any registry entry or Start Menu shortcut. Only one fixed drive exists.

`C:\devkitPro\devkitARM` is a modern GNU toolchain and is not ARM Developer
Suite. It was used in exactly one place, the `--diagnostic-control` path, whose
output is tagged `DIAGNOSTIC_CONTROL_NOT_EVIDENCE`; no result from it is
reported anywhere in this ticket as a finding.

### Search performed

| check | result |
| --- | --- |
| `$env:ADS12_ROOT` | unset |
| `shutil.which` for the nine ADS tool names | all `None` |
| install roots (`Program Files\ARM`, `Program Files (x86)\ARM`, `C:\ARM`, `C:\ADS`, `C:\ADS12`, `Keil`, `ADSv1_2`, `RVCT`) | none exists |
| uninstall registry (HKLM, WOW6432Node, HKCU) matching ARM/ADS/Developer Suite/RVCT/RealView/Keil | only Windows SDK arm64 components |
| ARM vendor registry keys | none |
| Start Menu shortcuts matching ARM/ADS/Developer Suite/RealView/AXD | none |
| bounded filesystem scan of `C:\Dev`, `C:\Tools`, `C:\opt`, `D:\`, `E:\`, `F:\`, Downloads, Desktop, Documents, `AppData\Local\Programs` | no ADS executable |

No system configuration was mutated. ADS 1.2 was not downloaded: it is
commercial software, its licence prohibits redistribution, and the ticket
forbids unofficial, abandonware and warez sources. No proprietary binary,
licence file or registry entry was created.

## 3. Why each function was selected

Selection ran in two stages: a scored candidate list, then a final set.

### Stage 1: scored candidates

| candidate | bounded? | small? | simple? | calls | literals | decision |
| --- | --- | --- | --- | --- | --- | --- |
| `gbaram_tu` functions | yes, chain walk, zero gaps | 24 to 214 B | yes, one loop total | 0 to 3 | 0 to 3 | **selected** |
| `0x0800419C` | yes, from the reset path | 116 B | no, 9 callees | 9 | 2 | deferred |
| `code_reachable_02E1C0` | no, 4096-byte window | 1022 B first function | no, 20 callees | 20 | many | deferred |
| `code_reachable_055324` | n/a | n/a | n/a | n/a | n/a | rejected: data |
| `code_candidate_span_6_048F14` | n/a | n/a | n/a | n/a | n/a | rejected: not ARM |
| `code_candidate_span_5_03D2D0` | no, mixed with data | n/a | n/a | n/a | n/a | rejected |
| `0x080000C0` reset | yes | 116 B | yes | 0 | 9 | control, excluded by ticket |
| `0x087B79A4` codec | yes (region bounds) | 1024 B | no | 1 | many | control, excluded by ticket |
| `0x08049114` veneer | yes | 248 B | yes | 0 | many | control: library |

Each "deferred" candidate is real code that failed on probe quality (size,
control-flow complexity, relocation count), not on authenticity. They are
recorded so a later ticket can revisit them once a TU-level harness exists.

### Stage 2: final set, and why it is one translation unit

The eight `gbaram_tu` functions are the only candidates in the image whose
boundaries are established by an argument rather than by a window, and they are
also the only set that can be compared at all once the shared literal pool is
taken into account. Selecting a subset across several unverified regions would
have produced a corpus that cannot be compiled into the original layout.

## 4. Measurements taken, and how

| claim | method | strength |
| --- | --- | --- |
| the eight boundaries | chain-walk recursive descent, all paths terminated, zero gaps, zero undecodable bytes | `CONFIRMED` |
| the shared literal pool and its four words | decoded the `ldr rX, [pc, #N]` loads and read the slots; independently matches DECOMP-ROM-MAP-001's `gbaram_literals` | `CONFIRMED` |
| the internal call graph | read the `bl` sites in the disassembly; the calls are at `0x0803D5D6`, `0x0803D600`, `0x0803D670`, `0x0803D69A`, `0x0803D6C4`, `0x0803D6D4`, `0x0803D6DC`, `0x0803D702` | `CONFIRMED` |
| index arithmetic `(u16 << 2) + 0x02000000` and `(ptr + 0xFE000000) >> 2` | the emitted instructions themselves | `CONFIRMED` |
| field offsets and widths | the emitted `ldrh` / `strh` / `ldrb` / `strb` offsets | `CONFIRMED` |
| field **names** | placeholder only | `UNKNOWN` |
| the `0x7FFFFFFF` guard semantics | not resolved; a `ldrh`-loaded value cannot reach it | `UNRESOLVED` |
| the `[0x04]` store in `sub_0803D56A` | not resolved | `UNRESOLVED` |
| that the original file is `src/GBARam.c` | the surviving command line plus the region's role as an allocator | `INFERRED` |
| that `tcpp` implies Thumb + C++ | published ADS driver naming | `INFERRED` |
| any compiler setting | not measured | `UNTESTED` |

### The inventory's `size` field is not a boundary

`config/functions.json` derives `size` from
`analysis.decode_run(limit=0x400).bytes_ok`. That is a decode extent capped at
1024 bytes, not a function boundary. Measured against this unit:

| address | inventory size | measured boundary | overrun |
| --- | --- | --- | --- |
| `0x0803D4D0` | 620 | 24 | 596 bytes |
| `0x0803D4E8` | 596 | 56 | 540 bytes |
| `0x0803D5B8` | 388 | 132 | 256 bytes |
| `0x0803D63C` | 256 | 214 | 42 bytes |

Both of the larger spans end at `0x0803D73C`, running through neighbouring
functions and into the literal pool, and both carry the same contaminated callee
list (`0x0803D4E8`, `0x0803D520`, `0x0803D56A`) because those are the
neighbours' calls. Six of the eight probes carry an overrun; all six are in
`config/compiler_probes.json` under `inventory_size_disagreements`, each with the
recorded value and the measured one side by side.

An earlier revision of this document attached the 620 figure to
`0x0803D5B8`. The independent review measured both entries and caught it; the
manifest now records both pairs explicitly and a test asserts them.

### Two functions missing from the inventory

`sub_0803D548` and `sub_0803D712` are absent from `config/functions.json`. Neither
is the target of any `BL`/`BLX` in the image and neither is a literal-pool code
pointer, so a branch-target inventory could not have found them. They are
recorded under `inventory_gaps` with their independent evidence rather than
dropped, because they are real and their bytes must be in the comparison.

## 5. Regions that must not be promoted to evidence

`code_reachable_055324` (`0x055324`, map: `code`, `high`, executable
`confirmed`) **is data**. It disassembles as a repeating `cmp rX, #imm` /
`lsrs r0, r0, #0x20` pair, i.e. a table of halfwords followed by `0x0808`.
`code_candidate_span_6_048F14` (`0x048F14`, map: `medium`, ARM) does not decode
as ARM at all: the first word is an NV-condition word. Both are recorded in
`config/compiler_probes.json` under `rejections`.

The general lesson, already measured in DECOMP-ROM-MAP-001 and re-confirmed
here, is that on this cartridge Thumb data is indistinguishable from Thumb code,
so a `high` classification describes a window and never authorizes a probe. Only
recursive reachability plus a terminating chain walk produced boundaries this
ticket was willing to build on.

## 6. Every compiler configuration considered

The matrix is committed in `config/compiler_matrix.json`. On this machine every
row is `status: BLOCKED`, `code: ADS12_UNAVAILABLE`, `exact_match: false`, with
`no_compiler_result_claimed: true`.

| configuration | status | exact | purpose |
| --- | --- | --- | --- |
| `tcpp -cpu ARM7TDMI -O1` | `BLOCKED` | no | the historical lead |
| `tcpp -cpu ARM7TDMI -O0` | `BLOCKED` | no | control: optimisation off |
| `tcpp -cpu ARM7TDMI -O2` | `BLOCKED` | no | control: more optimisation |
| `tcc -cpu ARM7TDMI -O1` | `BLOCKED` | no | control: C rather than C++ |
| `armcpp -cpu ARM7TDMI -O1` | `BLOCKED` | no | control: ARM, C++ |
| `armcc -cpu ARM7TDMI -O1` | `BLOCKED` | no | control: ARM, C |

Also considered and deliberately excluded from the committed matrix: `-O3`,
`-Ospace` and `-Otime`. ADS 1.2 does expose size/time optimization variants, but
the exact spelling and its interaction with `-O1` must come from the installed
compiler's own help, and the ticket forbids blind brute force of undocumented
flags. Adding them once documented is a one-line change to `MATRIX_CONFIGS`.

Two claims have **no** discriminator in this matrix and are structurally capped
rather than promoted: the CPU target (every configuration is ARM7TDMI) and ABI
characteristics (no ABI-affecting flag is varied). `fingerprint()` says so in
its evidence block instead of reporting them at the same strength as the claims
that do have competing settings.

Exact matches: **none**. Near matches: **none**. Ambiguous or non-discriminating
functions: **not established**, because no probe has been run. Failed
hypotheses: **none yet**, for the same reason; the hypotheses that have been
recorded as unresolved are the two semantic questions listed in section 4.

The committed `config/compiler_matrix.json` is deliberately
**environment-independent**: it carries a stable blocker statement rather than
this machine's tool listing, so it reproduces byte-identically on any machine
without ADS and `--verify-matrix` is meaningful. On a machine with an identified
ADS 1.2 the matrix must be regenerated, and `--verify-matrix` fails until it is.

## 7. Provenance of the harness itself

The probe harness is a new module, `tools/buusfury/compiler_probe.py`, plus a
`compiler-probe` subcommand in `tools/buusfury/cli.py`. It reuses, rather than
reinvents:

- `identity.py` for canonical ROM resolution and fail-closed verification,
- `gba.py` for the ROM base and address-space conversion,
- `capstone` through its own handle pair, matching `analysis.py`'s configuration.

It does **not** import `analysis.decode_run` for boundaries; the chain walk is
its own algorithm and is the thing that makes this corpus new.

The ADS command pipeline is faithful to the surviving lead: `tcpp -S` emits
assembly (which is why the reference build has a checked-in `GBARam.s` carrying
the command in its header), `armasm` assembles it, `armlink` places it through a
scatter file, and `fromelf` extracts the bytes.

### What has been exercised, and what has not

| path | exercised? | how |
| --- | --- | --- |
| manifest derivation and verification | yes | `--write-manifest`, `--verify-manifest`, and tests that tamper with each field in turn |
| matrix derivation and verification | yes | `--write-matrix`, `--verify-matrix`, and a tampering test |
| byte comparison, including length mismatch and instruction counting | yes | portable tests plus a real compile |
| command construction and scatter generation | yes | `--plan`, and tests that assert the exact argument order |
| blocked reporting, including the aggregate | yes | `--matrix` on this machine, plus a test that every configuration blocked still yields BLOCKED rather than COMPLETE |
| toolchain identification by banner | partly | the rejection paths are tested against a real non-ADS executable and against the Tiny C Compiler's banner; no real ADS banner has been seen |
| compiler invocation and object extraction with GCC | yes | `--diagnostic-control`, tagged not-evidence |
| compiler invocation, linking and extraction with ADS 1.2 | **no** | no installation exists |

The ADS leg is therefore **unexercised**. The one assumption in it that could
silently corrupt a result is stated in every report as `ORIGIN_ASSUMPTION`: that
`fromelf -bin` on a single-load-region scatter emits from that region's address.
Confirming it from real toolchain output is the first step after installation.

## 8b. Independent review

The implementation was frozen at `c6882ae` and reviewed adversarially by a
reviewer whose brief was to falsify it and whose method was independent: an
exhaustive `BL`/`BLX` halfword-pattern census over all 8,388,608 bytes, a
from-scratch reachability fixpoint, and in-memory reconstruction of the manifest
and matrix. It confirmed the eight boundaries, the exact 608-byte tiling, the
absence of a ninth function, the shared four-word pool, the two inventory gaps
and the call graph, and found one blocker and nine major defects.
`docs/COMPILER_PROBE.md` section 17 lists them. Its verdict was
`SOUND WITH FIXES`.

A second verification round against the fixed revision re-confirmed the measured
core independently (eight boundaries, every `problems` tuple empty, 608 bytes,
`consistency_problems` empty), confirmed the blocker and seven of the nine
majors resolved, and then found two defects that the first round of fixes had
itself introduced:

- a claim could be published as `PROVEN` when its competing configuration never
  ran, because a missing competitor was treated as a differing one. This is the
  same class of failure as the original blocker and is reachable as soon as a
  partially installed toolchain runs only some configurations. Fixed by capping
  any claim whose competitor did not compare, and by recording the cap.
- gate 6's PASS branch was unreachable: it matched the literal string
  `comparisons_run` against the human-readable matrix rendering, which does not
  contain it, so a probe that actually worked would have failed the gate. Fixed
  by reading the matrix as JSON and checking the count.

It also reduced the remainder to documented NITs, each addressed here: the
manifest note about `role` strings was untrue and is corrected to say they are
semantic hypotheses; the target's uncovered bytes are now published as
`undecoded_target_bytes`; the toolchain-identification limits are published as
`toolchain_identification`; a partly blocked matrix now headlines `PARTIAL`
instead of `COMPLETE`; manifest comparison is type-strict so `"schema": true`
cannot pass for `1`, and a valid-JSON non-object manifest is reported rather
than crashing; the ARM optimization claim is `UNTESTED` instead of borrowing the
frontend comparison; and the tests that only grepped prose were replaced with
behavioural ones, including a real CLI invocation for the exit codes.

A third round verified that revision and found three further narrow defects of
the same class, all fixed here:

- the gate's BLOCKED branch was still decided by searching the whole document
  text for `ADS12_UNAVAILABLE`. In a `PARTIAL` matrix the blocked rows carry
  that code, so a run that did compare bytes was reported `BLOCKED`. The gate
  now branches on the document's own top-level `code` and `comparisons_run`,
  and a test pins the trap by asserting that a partial document keeps
  `code: null` while the string is still present in it.
- the gate merged stderr into the JSON it parsed, so a warning line broke the
  parse and turned a working probe into a false `FAIL`. It now parses stdout
  only, verified by replaying both forms.
- folding uncovered target bytes into the instruction count made
  `matching_instructions` negative for an undecodable target, contradicting the
  documented guarantee. Those bytes are now reported only in
  `undecoded_target_bytes`, the property is clamped at zero, and a property test
  covers adversarial pairs including undecodable targets.

That round's verdict was again `SOUND WITH FIXES`, with all three items
described as narrow and none able to produce a false PASS or an unjustified
`PROVEN`.

## 8. Reproducing this ticket

From a bare checkout with a legally dumped canonical ROM:

    set BUUSFURY_ROM=<path to the canonical ROM>      REM or place baserom.gba at the repo root
    python -m buusfury compiler-probe --verify-manifest
    python -m buusfury compiler-probe
    python -m buusfury compiler-probe --write-manifest   REM must reproduce the committed file
    python -m pytest tests -q
    scripts\check.cmd

`--verify-manifest` regenerates every measured field, including all eight
boundaries, the two inventory gaps, the six size disagreements and the four
literal words, and fails on any disagreement with the committed file. The
committed manifest is therefore a claim that is re-tested rather than trusted.

## 9. Tests, gates and repository state

| item | result |
| --- | --- |
| `tests/test_compiler_probe.py` | 86 passed |
| full suite | 263 passed (measured) |
| `scripts/check.cmd` | PASS, exit 0; gates 5 and 6 are reported `BLOCKED`, not `FAIL` |
| canonical ROM | unchanged (SHA-1 and mtime) |
| proprietary artefacts | none created, downloaded or tracked; Git refuses every ADS tool and licence name |
| `C:\Dev\log1-remake` | not modified |

## 10. Blocker, precisely

    COMPILER PROBE: BLOCKED - ADS12_UNAVAILABLE

Two conditions, of which the first is decisive on this machine:

1. ARM Developer Suite 1.2 is not installed. It is commercial software whose
   licence does not permit redistribution, so this repository can never supply
   it, and the ticket forbids unofficial sources.
2. Even with a compiler, the reconstruction in `src/probes/GBARam.c` is a first
   hypothesis that will need iteration against the real compiler before three
   discriminating exact matches can be expected.

The honest next action is to install ADS 1.2 locally, set `ADS12_ROOT`, and run
`python -m buusfury compiler-probe --plan` followed by `--matrix`.
