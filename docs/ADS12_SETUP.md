# ARM Developer Suite 1.2 - installation and configuration

**Status on this machine: NOT INSTALLED.** Nothing in this document was executed
here; it records what is required and how the pipeline expects to find it.

---

## Why ADS 1.2 at all

Buu's Fury was built in ~2004 with **ARM Developer Suite 1.2**. Matching
decompilation requires emitting the *same machine code*, which in general means
the same compiler, the same optimisation level and the same linker. The evidence
that ADS 1.2 is the right family:

- `2genkidev/buusfury`'s `build.bat` invokes `armcpp`, `armasm`, `armlink`,
  `fromelf` and its README names `tcpp`.
- `asm/GBARam.s:5` preserves the original command line:
  `tcpp -S -c -cpu ARM7TDMI -O1 src/GBARam.c`.

## Licence - read first

ADS 1.2 is **commercial software**. Its licence does **not** permit
redistribution.

- **Never commit an ADS binary, library or licence file to this repository.**
  `.gitignore` blocks the known executables, but the rule is the rule.
- Install it wherever you like **outside** the repository and point `ADS12_ROOT`
  at it.
- A licensed copy is required. This project cannot supply one, and will not
  accept one obtained by other means.
- If no licensed copy is available, the ADS-dependent regions cannot be
  reproduced by this route at all - see
  [`DECOMP_BASELINE.md`](DECOMP_BASELINE.md#5-the-blocker). That is a legitimate
  and *expected* baseline outcome, and `DECOMP-COMPILER-PROBE-001` exists to
  determine whether a free toolchain can close the gap instead.

## What must be present

| Tool | Purpose | Needed by |
| --- | --- | --- |
| `armasm` | assemble `crt0.s`, `GBARam.s`, `buu.s` | `crt0`, `gbaram_text`, `afterlibs_thunk` |
| `armcpp` | compile `color_transforms.cpp`, `strings.cpp` | `color_transforms`, `strings` |
| `armlink` | link with `-noremove -scatter scatter.ld` | the whole image |
| `fromelf` | `-bin` conversion of the linked `.axf` | the whole image |
| `tcc` | ARM C compiler | not yet invoked; recorded for the compiler probe |
| `tcpp` | Thumb C compiler / preprocessor | not yet invoked; the original compiler for `GBARam` |

`armasm` must be able to assemble ARM **and** Thumb (`CODE32` / `CODE16`,
`PROC`/`ENDP`), which is ADS's syntax rather than GNU `as` syntax.

## How the pipeline locates it

`tools/buusfury/toolchain.py` searches, in order, for each tool:

1. `$ADS12_ROOT/Bin/<tool>.exe`
2. `$ADS12_ROOT/bin/<tool>.exe`
3. `$ADS12_ROOT/<tool>.exe`
4. `PATH`

`ADS12_ROOT` is the only configuration knob. No tracked file hardcodes an install
path.

```powershell
# current session
$env:ADS12_ROOT = 'C:\ARM\ADSv1_2'

# or permanently, for the user
[Environment]::SetEnvironmentVariable('ADS12_ROOT', 'C:\ARM\ADSv1_2', 'User')
```

Then confirm the pipeline sees it:

```powershell
python -m buusfury doctor
```

A correctly configured machine shows `available` for `armasm`, `armcpp`,
`armlink` and `fromelf`, and the `doctor` output stops listing them as blocking.

## Expected installation shape

ADS 1.2 typically installs to a path such as `C:\ARM\ADSv1_2` with this layout:

```
<ADS12_ROOT>\
  Bin\
    armasm.exe
    armcc.exe
    armcpp.exe
    armlink.exe
    fromelf.exe
    tcc.exe
    tcpp.exe
    armsd.exe
  Include\
  Lib\
  ...
```

`armsd` (the debugger) is not needed.

## Configuring the JCALG1 front-end (not ADS, but part of the image)

The asset regions do **not** need ADS, but they do need the JCALG1 front-end
built. This has two non-obvious requirements, both verified on this machine and
both recorded because the reference build gets them wrong:

1. **A Visual Studio CMake.** The MSYS2/MinGW CMake that devkitPro installs
   cannot name a Visual Studio generator:
   `CMake Error: Could not create named generator Visual Studio 17 2022`.
   Use the CMake bundled with Visual Studio, or set `CMAKE` to it.
2. **The 32-bit MSVC toolchain.** `jcalg1_static.lib` is a prebuilt x86 library
   and the reference build passes `-A Win32`.

```powershell
pwsh -File scripts/fetch-reference.ps1 -BuildTools
python -m buusfury doctor
```

`scripts/fetch-reference.ps1 -BuildTools` builds `build/tools/compress.exe`.

## What is still missing after ADS 1.2 is installed

Installing ADS does **not** by itself make the build complete. This repository
contains no input source for the five `ads` regions, and none may be imported
from the only public copy, because that copy carries no licence
(see [`REFERENCE_AUDIT.md`](REFERENCE_AUDIT.md#2-licence--decisive)).

Writing those sources is the decompilation work itself:

| Region | Bytes | What has to be written |
| --- | ---: | --- |
| `crt0` | 152 | ARM start-up: mode/stack setup, hardware init, tail branch |
| `gbaram_text` | 232 | Thumb allocator, hand-transcribed today |
| `afterlibs_thunk` | 12 | an ARM veneer to `0x080046AED` |
| `color_transforms` | 4,608 | 18 × 256-byte colour-effect LUTs |
| `strings` | 89,012 | 1,534 UTF-16LE strings + the pointer table |

## Version discipline

The reference scripts accept any `armasm` on `PATH` and never check its version.
`armasm` from a different ADS/RVCT major release will not produce identical code.

The baseline records the expected family (ADS 1.2) but does **not** yet
fingerprint a specific build. Adding a version assertion is a sensible early
follow-up: once a matching build is demonstrated, the exact `armasm` banner
should be captured into `config/toolchain.json` and enforced, so that a
subsequent build cannot silently drift to another toolchain.
