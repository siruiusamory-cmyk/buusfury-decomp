# Dependencies and local setup

Everything the baseline needs, what is required versus optional, and how each is
located. Nothing proprietary is ever committed.

---

## Summary

| Dependency | Required? | Redistributable? | Found via |
| --- | --- | --- | --- |
| A legally dumped canonical ROM | **required** | **no** | `--rom`, `$BUUSFURY_ROM`, `./baserom.gba` |
| Python 3.11+ | **required** | yes | `PATH` |
| Git | **required** | yes | `PATH` |
| pytest | for the test gate | yes | `PATH` |
| `2genkidev/buusfury` checkout | for the asset gate | **no licence** | `--reference`, `$BUUSFURY_REFERENCE`, `reference/buusfury` |
| grit | for BMP assets | yes | `PATH`, `$GRIT`, `$DEVKITPRO/tools/bin` |
| CMake (Visual Studio) | to build the JCALG1 front-end | yes | VS install, `$CMAKE` |
| MSVC x86 (vcvars32) | to build the JCALG1 front-end | yes | Visual Studio Build Tools |
| ARM Developer Suite 1.2 | **for the 1.12% ADS leg** | **no** | `$ADS12_ROOT`, `PATH` |

The harness itself has **no third-party Python packages**. It runs on a stock
CPython.

---

## Required

### A legally dumped canonical ROM

You must own and dump your own copy. It is never tracked, never copied into the
repository, and never modified.

```
SHA-1  f1c4b07554d2a3b1ad2f325307051e775ce68087
size   8388608 bytes
```

Place it at `<repo>/baserom.gba`, or point at it:

```powershell
$env:BUUSFURY_ROM = 'D:\dumps\Dragon Ball Z - Buu''s Fury (U).gba'
```

`scripts/check.ps1` and every CLI subcommand verify it and **fail closed** on any
mismatch - wrong revision, wrong region, wrong size, a single flipped byte. There
is no override flag.

### Python 3.11 or newer

Verified on 3.12.10. `config/rom.json` and `config/regions.json` are parsed with
the standard library only.

### Git

For the checkout, and because `scripts/fetch-reference.ps1` asserts that
`reference/` is ignored before it will proceed.

---

## Optional, but needed for specific gates

### pytest - the portable test gate

```powershell
python -m pytest tests -q      # 86 tests
```

`tests/conftest.py` deliberately overrides pytest's `tmp_path` and
`tmp_path_factory` to live under `build/` rather than `%TEMP%`. On this machine
`%TEMP%\pytest-of-hears` exists with broken ACLs and would otherwise abort every
test with `PermissionError: [WinError 5]`. The override makes the suite
reproducible anywhere instead of depending on a machine-specific environment
variable. `pytest.ini` also redirects the cache to `build/`.

### The reference checkout - the asset gate

```powershell
pwsh -File scripts/fetch-reference.ps1            # clone + submodules
pwsh -File scripts/fetch-reference.ps1 -BuildTools # and build compress.exe
```

- **No licence.** Fetched into `reference/`, which `.gitignore` excludes. Read it
  and run its build path; never copy its source into this repository.
- It contains ROM-derived BMPs and prebuilt third-party Windows binaries. Neither
  may be committed.
- Probe alternative: `$BUUSFURY_REFERENCE`.

If it is absent, the asset gate reports *why* each region failed rather than
crashing, and `--allow-passthrough` still produces a byte-identical image with a
report marking those regions `passthrough`.

### grit - BMP to GBA image data

```powershell
python -m buusfury doctor        # shows the resolved path
```

discovery order: `$GRIT` → `PATH` → `$DEVKITPRO/tools/bin/grit.exe` →
`C:\devkitPro\tools\bin\grit.exe`.

devkitPro ships grit in `tools/bin` but does **not** add that directory to `PATH`,
so a naive `which grit` misses a working installation. The harness checks there
explicitly.

**Verified version: 0.9.2.** The reference README points at DylanGraham's grit
instead. Both were not compared; 0.9.2 is what was measured to reproduce the
ROM's asset bytes exactly, and that is what the baseline records.

### A Visual Studio CMake and the x86 MSVC toolchain

Needed only to build `tools/compress.exe`, the JCALG1 front-end. Two traps, both
verified here:

1. **The MinGW CMake on `PATH` cannot do it.** devkitPro's CMake fails with
   `Could not create named generator Visual Studio 17 2022`. The harness looks for
   the CMake bundled with Visual Studio and prefers it.
2. **32-bit is mandatory.** `jcalg1_static.lib` is a prebuilt x86 library, and the
   reference build passes `-A Win32`. The harness locates `vcvars32.bat`.

MSVC 14.44 (Visual Studio 2022 Build Tools) works.

Built by `scripts/fetch-reference.ps1 -BuildTools`, landing at
`build/tools/compress.exe`. Override with `$BUUSFURY_COMPRESS`.

### ARM Developer Suite 1.2 - the ADS leg

An ADS 1.2 installation **is present** on this machine
(`armcc`, `armcpp`, `armasm`, `armlink`, `fromelf`, `tcc`, `tcpp`), but the licence
file it ships licenses `Win32_CWIDE_Unlimited` (the CodeWarrior IDE) and carries no
compiler/armasm/armlink feature, so FLEXlm refuses the tools. The correct code is
`ADS12_LICENSE_UNAVAILABLE`, which is a different condition from "ADS is not
installed" and is why gates 5 and 6 report BLOCKED rather than FAIL.

Not redistributable, and not sufficient on its own: the ADS input sources do not
exist in this repository and cannot be imported. See
[`ADS12_SETUP.md`](ADS12_SETUP.md).

### The modern ARM toolchain - the lifting loop

Needed by gate 7 and by `python -m buusfury lift`. **Never installed by this
repository**; it is detected and reported.

| | |
| --- | --- |
| Family | GNU Arm Embedded (devkitARM) |
| Verified version | `arm-none-eabi-gcc.exe (devkitARM) 16.1.0`, binutils 2.46.0.20260210 |
| Target triple | `arm-none-eabi` |
| Default root | `C:\devkitPro\devkitARM` (reported as `<DEVKITARM>`) |
| Discovery | `--toolchain-root`, then `$DEVKITARM`, then the default |

Required tools: `arm-none-eabi-{gcc,ld,objcopy,objdump,nm}`. **All** must be present;
a partial installation is reported absent rather than used, so a build can never
half-run. An **explicit** root is authoritative: if it does not hold a complete
toolchain the answer is "no toolchain", never a silent fallback to a different one.

This toolchain is **not the original compiler** and its output can never be a
finding about ADS 1.2. It exists so the reconstruction can be built and its shape
compared. See [`LIFT_PILOT.md`](LIFT_PILOT.md) and [`LIFT_LOOP.md`](LIFT_LOOP.md).

If it is missing, gate 7 reports **BLOCKED** - an environment problem, not a defect
in the repository - and the portable test suite still passes.

---

## Environment variables

All optional. No tracked file contains a machine-specific absolute path.

| Variable | Overrides |
| --- | --- |
| `BUUSFURY_ROM` | baserom location |
| `BUUSFURY_REFERENCE` | fetched reference checkout |
| `BUUSFURY_COMPRESS` | JCALG1 front-end binary |
| `ADS12_ROOT` | ARM Developer Suite 1.2 root |
| `DEVKITARM` | modern ARM cross toolchain root (for the lifting loop) |
| `GRIT` | grit binary |
| `CMAKE` | CMake binary (must name a VS generator) |

---

## Verifying a machine

```powershell
python -m buusfury doctor          # tool-by-tool availability and versions
python -m buusfury verify          # ROM identity only
pwsh -File scripts/check.ps1       # every achievable gate, one summary
```

`doctor` distinguishes *available* from *blocking*: it lists the tools that are
missing **and** whose absence prevents full source reproduction, so a partially
configured machine reports exactly what is missing and why it matters.

## A note on why `check.ps1` still exits 0 without ADS

Gate 5 (full source reproduction) is reported as `BLOCKED`, not `FAIL`. The
baseline's contract is that the blocker is **measured and precisely documented**,
not that it is absent. Conflating the two would either hide a real defect or train
the operator to ignore a red build - both worse than an explicit `BLOCKED`.
