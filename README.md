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
python -m pytest tests -q    # 304 tests
```

## Scope

This repository is at **DECOMP-LIFT-PILOT-001**. It carries the identity gate, the
build model, the independent ROM map and the compiler probe, plus one lifted
function family (the GBARam allocator) and the reusable loop that produced it.

`ADS_MATCH` remains blocked: the ADS 1.2 installed on this machine is unlicensed, and
nothing here reduces that. The next tickets work outward from the pilot - see
[`docs/LIFT_PILOT.md`](docs/LIFT_PILOT.md#7-next-recommended-function-family) for the
recommended next function families.
