# Validation report - DECOMP-BASELINE-001 + DECOMP-BOOTSTRAP-001

Everything below was **executed on 2026-09-28** on the machine described in §1.
Nothing in this report is projected, estimated or assumed. Where a value is
derived rather than observed, it is labelled.

---

## 1. Environment

| | |
| --- | --- |
| Host OS | Windows |
| PowerShell | **5.1.26100.9444 (Desktop edition)** - *PowerShell 7 (`pwsh`) is NOT installed* |
| Python | 3.12.10 (`C:\Users\hears\AppData\Local\Programs\Python\Python312\python.exe`) |
| pytest | 9.1.1 |
| CMake | VS 2022 Build Tools bundled; **devkitPro's MinGW CMake cannot configure the JCALG1 tool** |
| MSVC | 14.44.35207, `vcvars32.bat` (x86, required by `jcalg1_static.lib`) |
| grit | 0.9.2 (`C:\devkitPro\tools\bin\grit.exe`) |
| **ADS 1.2** | **NOT INSTALLED** (`ADS12_ROOT` unset; no PATH entry; no registry entry; no install directory) |

**Consequence for the scripts:** everything is written for **Windows PowerShell
5.1 or later**, because 5.1 is present on every Windows machine and `pwsh` is
not installed here. `.cmd` shims are provided so the entry points do not depend
on knowing which PowerShell binary exists.

---

## 2. Input ROM verification - **PASS**

Command:

```powershell
python -m buusfury verify --rom 'C:\Dev\log1-remake\roms\Dragon Ball Z - Buu''s Fury (U).gba'
```

Output:

```
ROM identity: PASS
  path    : C:\Dev\log1-remake\roms\Dragon Ball Z - Buu's Fury (U).gba
  size    : 8388608 bytes
  sha1    : f1c4b07554d2a3b1ad2f325307051e775ce68087
  sha256  : 940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e
  crc32   : 01c1707f
  header  : title='DBZBUUSFURY' game_code='BG3E' maker='70' checksum=0x84 (valid)
```

Independently corroborated with `Get-FileHash` (SHA-1 / SHA-256 / MD5), which
returned the same SHA-1 and SHA-256, and MD5 `3a74fce97f1ea2b28c2a50ec3df0acee`.

The measured SHA-1 is **exactly** the ticket's expected canonical SHA-1.

Fail-closed behaviour was also exercised: the test suite covers a flipped byte, a
wrong game code, a wrong size, a broken header checksum, and a missing file, and
asserts that each is refused.

---

## 3. Region map - **PASS** (28 regions tile exactly)

Command:

```powershell
python -m buusfury map
```

Output:

```
REGION MAP: PASS (28 regions tile 0x000000-0x800000)

class           bytes     share  regions
incbin      8,268,480   98.568%  13
asset          26,112    0.311%  10
ads            94,016    1.121%   5
total       8,388,608  100.000%  28
```

Tiling was additionally verified element-by-element in a standalone script, and
the arithmetic was checked three ways:

- `8,268,480 + 26,112 + 94,016 = 8,388,608` - exact.
- The ten `build.bat` `incbin.bat` ranges sum to `8,268,168`; plus the three
  deliberately-opaque data regions (`rom_header` 192, `gbaram_data` 16,
  `dat_080561c4` 104) gives `8,268,480`.
- The four 64-byte corners plus the two 512-byte palettes end **flush** at
  `0x05672C`, where `color_transforms` begins.

---

## 4. Asset reproduction - **PASS** (10/10, 26,112 bytes byte-identical)

Command:

```powershell
python -m buusfury assets --rom <baserom> --reference <reference checkout>
```

Output:

```
region                   result        bytes  detail
asset_intro              IDENTICAL      2980  byte-identical
bmp_corner_top_left      IDENTICAL        64  byte-identical
bmp_corner_top_right     IDENTICAL        64  byte-identical
bmp_corner_bottom_left   IDENTICAL        64  byte-identical
bmp_corner_bottom_right  IDENTICAL        64  byte-identical
palette_bg               IDENTICAL       512  byte-identical
palette_sprite           IDENTICAL       512  byte-identical
asset_dialogbox          IDENTICAL       788  byte-identical
asset_dialogbox_small    IDENTICAL       548  byte-identical
asset_splash             IDENTICAL      20516  byte-identical

10/10 asset regions reproduced byte-identically
```

The JCALG1 front-end was built from source with the reference build's own
settings:

```
cmake -B <build> -S tools/compress -G "Visual Studio 17 2022" -A Win32 \
      -DCMAKE_EXE_LINKER_FLAGS="/SAFESEH:NO"
cmake --build <build> --config Debug
```

`compress.exe` was produced and used to regenerate the four compressed assets.
grit 0.9.2 produced the four 64-byte corners and the four raw image streams.

**Independent corroboration that these boundaries are not merely asserted:**

| Check | Result |
| --- | --- |
| grit's dialogbox output is 10,240 bytes; the ROM's JCALG1 stream at `0x071758` declares `0x2800` = 10,240 | match |
| grit's dialogbox_small output is 10,240 bytes; the stream at `0x071A6C` declares `0x2800` | match |
| grit's splash/intro output is 38,400 bytes; the streams declare `0x9600` | match |
| `build.bat` passes `788` as the dialogbox minimum size; the region is exactly 788 bytes | match |
| `build.bat` passes `20516` as the splash minimum size; the region is exactly 20,516 bytes | match |
| 4 corners x 64 + 2 palettes x 512 ends exactly at `0x05672C` | match |

---

## 5. Build reproduction

### 5.1 Strict build - **BLOCKED** (correctly, with a precise report)

```powershell
scripts\build.cmd -Rom <baserom> -Reference <reference>      # exit 1
```

```
BUILD: BLOCKED [ADS12_UNAVAILABLE]
5 region(s), 94,016 bytes, can only be rebuilt with ARM Developer Suite 1.2,
which is not installed and whose source inputs are not available to this
repository.

Requirement 1 - a licensed ARM Developer Suite 1.2 installation.
  armasm: NOT FOUND
  armcpp: NOT FOUND
  armlink: NOT FOUND
  fromelf: NOT FOUND
Requirement 2 - independently authored sources for those regions.
  ...
Commands the reference build runs for these regions:
  armasm asm/buu.s -o build/buu.o
  armasm asm/GBARam.s -o build/GBARam.o
  armcpp -c src/color_transforms.cpp -o build/color_transforms.o
  armcpp -c src/strings.cpp -o build/strings.o
Link and convert steps:
  armlink ... -noremove -scatter scatter.ld -o build/buu.axf
  fromelf build/buu.axf -bin -o build/output
```

The build refuses rather than falling back. This is the documented, intended
outcome.

### 5.2 Passthrough build - **PASS** (byte-identical, provenance labelled)

```powershell
scripts\build.cmd -Rom <baserom> -Reference <reference> -AllowPassthrough
```

```
baserom SHA-1    : f1c4b07554d2a3b1ad2f325307051e775ce68087
output SHA-1     : f1c4b07554d2a3b1ad2f325307051e775ce68087
expected SHA-1   : f1c4b07554d2a3b1ad2f325307051e775ce68087
byte-identical   : PASS
provenance       : 26,112 bytes rebuilt (0.311%), 8,362,496 bytes passthrough
```

Verified a **second, independent** way - a raw byte comparison, not a hash:

```powershell
Compare-Object ([IO.File]::ReadAllBytes('build/buusfury.gba')) `
               ([IO.File]::ReadAllBytes(<baserom>)) -SyncWindow 0
# -> $null
```

```
BYTE-IDENTICAL: 8,388,608 bytes, 0 differences
```

Provenance from `build/build-report.json`:

| provenance | regions | bytes |
| --- | ---: | ---: |
| `rebuilt-asset` | 10 | 26,112 |
| `passthrough` | 18 | 8,362,496 |

**This result proves the region map is correct. It does not prove the 8,362,496
passthrough bytes were reconstructed, and the report says so per region.**

---

## 6. Portable regression tests - **PASS** (88 passed)

```powershell
python -m pytest tests -q
# 88 passed in 13.89s
```

Coverage:

| File | Focus |
| --- | --- |
| `tests/test_identity.py` | header offsets, checksum algorithm, every mismatch kind, fail-closed `verify`, baserom resolution |
| `tests/test_regions.py` | exact tiling, gap/overlap/short-map rejection, **coverage totals locked**, per-region lengths, markdown rendering, LF stability, committed map matches a fresh render |
| `tests/test_build.py` | strict-mode blocker and its contents, passthrough provenance labelling, byte accounting, wrong-ROM refusal |
| `tests/test_toolchain.py` | manifest integrity, no invented paths, `ADS12_ROOT` lookup order, honest absence reporting |

The tests need no baserom, no reference checkout, no ADS, no grit and no JCALG1
build, so they run on a bare clone.

**A portability fix was required and made.** pytest's stock `tmp_path` roots
itself at `%TEMP%\pytest-of-<user>`, which exists on this machine with broken
ACLs; every test using it aborted at collection with
`PermissionError: [WinError 5] ... pytest-of-hears`. `tests/conftest.py` now
redefines `tmp_path` / `tmp_path_factory` under `build/`, and `pytest.ini`
redirects the cache there. The suite is therefore reproducible on any machine
instead of depending on an environment variable and a special command line.

**A reproducibility bug was found and fixed.** Python's text mode translates
`\n` to `os.linesep` on Windows, so the generated `docs/BUILD_REGIONS.md` was written
CRLF and `git diff --check` flagged every line. `--write` and the build report
now open files with `newline="\n"`, `.gitattributes` normalises all text to LF,
and two tests lock the guarantee (LF-only output, and a fresh render equal to the
committed file).

---

## 7. Safety verification

### 7.1 No ROM is tracked - **PASS**

```
$ git ls-files --others --exclude-standard | grep -E '\.(gba|sav|ss[0-9]|sps)$'
(no matches)
```

`.gitignore` was exercised directly:

| Path | Ignored |
| --- | --- |
| `baserom.gba` | yes |
| `roms/x.gba` | yes |
| `build/buusfury.gba` | yes |
| `build/build-report.json` | yes |
| `reference/buusfury/README.md` | yes |
| `toolchain/armasm.exe` | yes |

### 7.2 No proprietary toolchain binary is tracked - **PASS**

A scan of every staged path for `.exe`, `.dll`, `.lib`, `.obj`, `.axf`, `.elf`,
`armasm`, `armlink`, `armcpp`, `armcc`, `fromelf`, `tcpp`, `jcalg1` and `JCALG1`
returned no matches. The 36 staged files are `.md`, `.json`, `.py`, `.ps1`,
`.cmd`, `.ini`, `.gitignore`, `.gitattributes` only.

ADS 1.2 is not installed at all, so there was nothing to accidentally stage.

### 7.3 The source ROM was never modified - **PASS**

| | Before | After |
| --- | --- | --- |
| Size | 8,388,608 | 8,388,608 |
| SHA-1 | `F1C4B075…8087` | `F1C4B075…8087` |
| mtime (UTC) | `2026-08-20T01:10:12.3295721Z` | `2026-08-20T01:10:12.3295721Z` |

The file was opened for reading only, throughout. Its save and state siblings
(`.sav`, `.ss1`, `.ss2`) were likewise untouched, with unchanged sizes and
mtimes.

### 7.4 Existing Dragonbyte Z work is untouched - **PASS**

`C:\Dev\log1-remake` was read from but never written to.

| | Start of session | End of session |
| --- | --- | --- |
| HEAD | `7f01251b290075a564af857090cde68b0f06fbba` | `7f01251b290075a564af857090cde68b0f06fbba` |
| `git status --porcelain` | ` M docs/DEVELOPMENT.md` | ` M docs/DEVELOPMENT.md` |

`docs/DEVELOPMENT.md` was already modified before this work began and is the operator's
unrelated change; it was neither touched nor included in any commit. No file
inside `C:\Dev\log1-remake` was created, modified or deleted. In particular the
reference checkout at `extern/buusfury` was **read only**: the JCALG1 front-end
was built and run from a copy staged into this repository's gitignored `build/`,
precisely so that no artifact would appear inside the LOG1-REMAKE tree.

---

## 8. Validation gate

| # | Requirement | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Input ROM SHA-1 is exactly canonical | **PASS** | §2 |
| 2 | Reproducible from a clean checkout + local dependencies | **PARTIAL** | §3, §4, §6 reproduce from a bare clone; the ADS leg cannot (§5.1) |
| 3 | Output byte-identical, or inability precisely documented | **PASS** | §5.2 byte-identical; §5.1 precise blocker |
| 4 | No ROM tracked by Git | **PASS** | §7.1 |
| 5 | No proprietary toolchain binary tracked | **PASS** | §7.2 |
| 6 | Existing Dragonbyte Z files untouched | **PASS** | §7.4 |
| 7 | Documented clearly enough for a new contributor | **PASS** | `docs/DECOMP_BASELINE.md`, `docs/DEPENDENCIES.md`, `docs/ADS12_SETUP.md`, `docs/REFERENCE_AUDIT.md`, `docs/DEVELOPMENT.md`, `README.md` |
| 8 | Disassembly/source coverage inventoried | **PASS** | `docs/BUILD_REGIONS.md`, `docs/REFERENCE_AUDIT.md` §2 |
| 9 | No new gameplay function decompilation begun | **PASS** | `src/`, `asm/`, `data/`, `include/` contain only a README |

Requirement 2 is the only partial, and it is partial for one reason that is
documented with evidence rather than worked around.

---

## 9. One-command entry point

```powershell
scripts\check.cmd -Rom <baserom> -Reference <reference>
```

```
[1/4] canonical baserom identity            PASS
[2/4] region map tiles the ROM exactly      PASS  28 regions
[3/4] asset regions reproduced              PASS  10/10, 26,112 bytes identical
[4/4] full source reproduction              BLOCKED 94,016 bytes need ADS 1.2
portable regression tests                   88 passed
OVERALL: PASS
```

Exit code `0`. Gate 4 is reported `BLOCKED`, not `FAIL`: the baseline's contract
is that the blocker is **measured and documented**, not that it is absent.
Conflating the two would either hide a real defect or train the operator to
ignore a red build.

Run with no baserom present, the same command exits `1` and explains where it
looked and that the repository never tracks ROM data - verified.

---

## 10. Known limitations

1. **The region map is derived, not independently re-derived.** It comes from the
   reference project's `build.bat` and `scatter.ld`. It tiles exactly and every
   asset region is verified to rebuild identically, but the *classification* of
   each `incbin` range has not been re-derived from the binary. That is
   `DECOMP-ROM-MAP-001`.
2. **94,016 bytes (1.121%) cannot be reproduced here** - see §5.1.
3. **grit 0.9.2 is what was verified.** The reference README points at a
   different grit distribution; the two were not compared.
4. **No ADS version fingerprinting.** `ADS12_ROOT` resolves whatever `armasm` is
   there. A different ADS/RVCT major release would produce different code and
   nothing would notice. Capturing the exact banner into `config/toolchain.json`
   should happen as soon as a matching build is demonstrated.
5. **`config/regions.json` is hand-maintained.** Only the tiling and the asset
   coverage are machine-checked; the prose in each `note` is not.
6. **The 26,112 "reproduced" asset bytes depend on the reference checkout**
   (gitignored, unlicensed, containing ROM-derived BMPs). They are reproducible
   on this machine but the source assets are not redistributable.

---

# Validation report - `DECOMP-ROM-MAP-001` (2026-09-29)

See [`ROM_MAP.md`](ROM_MAP.md) and [`ROM_MAP_PROVENANCE.md`](ROM_MAP_PROVENANCE.md).
The ten map invariants hold, `config/rom_map.json` tiles 8,388,608 bytes exactly,
and 177 tests passed at that ticket's closure (the 88 above plus the ROM-map
suite).

---

# Validation report - `DECOMP-COMPILER-PROBE-001` (2026-09-29)

Result: **`COMPILER PROBE: BLOCKED - ADS12_UNAVAILABLE`**. No compiler setting
was proven, supported or refuted. Read [`COMPILER_PROBE.md`](COMPILER_PROBE.md).

## Commands run, and their measured results

```text
python -m buusfury compiler-probe --verify-manifest
# PROBE MANIFEST: PASS (8 probes, 8 thumb / 0 arm, 6 leaf / 2 non-leaf)

python -m buusfury compiler-probe
# COMPILER PROBE - DECOMP-COMPILER-PROBE-001
# canonical ROM : f1c4b07554d2a3b1ad2f325307051e775ce68087
# ADS 1.2       : ABSENT
# probe corpus  : 8 functions in 1 translation unit (8 Thumb / 0 ARM, 6 leaf / 2 non-leaf)
# COMPILER PROBE: BLOCKED - ADS12_UNAVAILABLE

python -m buusfury compiler-probe --plan
# exit 0. Prints the four-command ADS pipeline, the scatter file, and the
# ORIGIN_ASSUMPTION. Executes nothing.

python -m buusfury compiler-probe --matrix
# exit 1. Six configurations, all status=BLOCKED, all exact_match=false.
# no_compiler_result_claimed: true. Fingerprint: all claims UNTESTED.

python -m buusfury compiler-probe --diagnostic-control
# exit 0. Compiled src/probes/GBARam.c with devkitARM GCC and compared.
# target_size 624, candidate_size 760, identical_bytes 27, first_difference 0x0
#   (address 0x0803D4D0), differing_bytes 733, target_instructions 301,
#   differing_instructions 298, matching_instructions 3, exact_match False.
# classification: DIAGNOSTIC_CONTROL_NOT_EVIDENCE. Not a compiler finding.

python -m pytest tests -q
# 267 passed in 31.80s        (177 before this ticket; +90 in tests/test_compiler_probe.py)
```

The diagnostic-control run is reported here for one reason only: it proves the
harness's extraction, compilation, byte comparison and reporting paths work
end to end, and that `src/probes/GBARam.c` at least compiles. Its numeric output
say nothing about the original Webfoot compiler and must never be cited as
though it did.

## What was proven, and at what strength

| claim | strength |
| --- | --- |
| the eight `gbaram_tu` function boundaries | `CONFIRMED` (chain walk, all paths terminated, zero gaps) |
| the shared 16-byte literal pool and its four words | `CONFIRMED` (independently matches `data/fixed_regions.json`) |
| the internal call graph of the unit | `CONFIRMED` |
| `code_reachable_055324` is data, not code | `CONFIRMED` (decodes only as `cmp`/`lsrs` pairs over `0x0808` halfwords) |
| `code_candidate_span_6_048F14` does not decode as ARM | `CONFIRMED` |
| two real functions are missing from the inventory | `CONFIRMED` (recorded in `inventory_gaps`) |
| the inventory's `size` overruns six of eight probes | `CONFIRMED` (recorded in `inventory_size_disagreements`) |
| that the original file is `src/GBARam.c` | `INFERRED` |
| that `tcpp` implies Thumb and C++ | `INFERRED` (published ADS driver naming) |
| any compiler setting | `UNTESTED` |

## `scripts/check.cmd`

Six gates. Gates 5 and 6 are `BLOCKED`, not `FAIL`. The result is recorded in
the ticket's final report, and the gate was added by this ticket; the probe
manifest must regenerate from the canonical ROM for gate 6 to reach its
`BLOCKED` branch, so a manifest that has drifted fails the build rather than
hiding behind the blocker.

## Safety

- Canonical ROM SHA-1 `f1c4b07554d2a3b1ad2f325307051e775ce68087` and its
  `mtime_ns` are asserted unchanged by `tests/test_compiler_probe.py` around the
  probe read path, and again by a dedicated test in `tests/test_rom_map.py`.
- No ADS binary, licence file or ROM-derived blob is tracked; Git itself refuses
  every ADS tool name and licence filename, and a test walks the repository tree
  looking for any of them.
- Automatic harness output goes under `build/probes/`, which is gitignored. The
  only writes outside it are the two committed results, and only when
  `--write-manifest` or `--write-matrix` is passed explicitly. A test runs the
  whole blocked harness and asserts the working tree is unchanged.
- `C:\Dev\log1-remake` was not modified. See the ticket's final report for the
  proof.

## Independent review of this ticket

The implementation was frozen at `c6882ae` and reviewed adversarially, with an
independent method (an exhaustive `BL`/`BLX` census over all 8,388,608 bytes plus
a from-scratch reachability fixpoint, and in-memory reconstruction of both
committed documents). The review **confirmed the measured core** - the eight
exact boundaries, the 608-byte tiling, no ninth function, the shared four-word
pool, the two inventory gaps, and the call graph - and found one blocker and nine
major defects, all fixed in the revision that follows. The blocker was that a
discovered-but-useless toolchain could be reported as `COMPLETE` with a
`REFUTED` fingerprint and exit code 0; the factual errors were the "620 bytes
for `sub_0803D5B8`" claim (620 belongs to `sub_0803D4D0`) and "three confirmed
ARM regions" (there are two). Its verdict was `SOUND WITH FIXES`. See
[`COMPILER_PROBE.md`](COMPILER_PROBE.md) section 17 for the full list.

After the fixes the probe suite is 90 tests and the full suite is 267, measured.

A second verification round re-confirmed the measured core independently and
confirmed the original blocker and seven of the nine majors resolved, but found
that the first round of fixes had introduced two defects of its own: a claim
could be published as `PROVEN` when its competing configuration never ran, and
gate 6's PASS branch was unreachable because it matched the literal string
`comparisons_run` against human-readable output that does not contain it.

A third round confirmed both of those fixed - no row set reaches `PROVEN` or
`STRONGLY_SUPPORTED` without a competitor that ran and differed - and found three
further narrow defects of the same class, all now fixed: the gate's BLOCKED
branch was still decided by a whole-document substring, so a `PARTIAL` matrix
whose blocked rows carry `ADS12_UNAVAILABLE` was misreported as `BLOCKED`; stderr
merged into the gate's JSON stream could break the parse and turn a working probe
into a false `FAIL`; and folding uncovered target bytes into the instruction
count made `matching_instructions` negative for an undecodable target. Each has a
test, including one that pins the `PARTIAL`/row-code trap itself, and the gate's
branches were replayed against complete, partial and blocked documents. See
[`COMPILER_PROBE.md`](COMPILER_PROBE.md) section 17.

A fourth round returned **CLOSURE-READY** with two non-blocking one-liners, both
taken here: `thumb_cpu_target` published `REFUTED` for a row that `_claim`
elsewhere treats as unusable evidence, and gate 6 tested the blocker code before
the comparison count, so a hand-tampered document carrying both a top-level
`ADS12_UNAVAILABLE` code and `comparisons_run > 0` would have read `BLOCKED`. The
blocker branch now also requires `comparisons_run == 0`, so a comparison always
wins, and a test pins the invariant that makes that ordering total for emitted
documents. Across four rounds no reviewer finding could produce a false PASS or
an unjustified `PROVEN`.

## ADS execution pass, attempted 2026-09-29: BLOCKED

An execution pass was opened against `a0cbeb7` on the expectation that ADS 1.2
had been installed locally. It had not. The preflight was repeated independently
and returns the same absence by six checks: `ADS12_ROOT` unset in the process
environment and empty in both registry scopes, no ADS tool on `PATH`, no
plausible install root, no registry uninstall entry or vendor key, no Start Menu
shortcut, and only one volume with no unextracted installer or archive anywhere
searched. The harness was then run in that state and failed closed: `--plan`
reported `BLOCKED [ADS12_UNAVAILABLE]` with every required tool `MISSING`, and
`--matrix --json` reported `comparisons_run: 0`, `conclusion: UNTESTED`,
`no_compiler_result_claimed: true`, `promoted_claims: []` and exit 1.

Neither `ORIGIN_ASSUMPTION` nor `BANNER_ASSUMPTION` could be exercised, so
neither is confirmed or refuted. No compiler configuration was tested, no exact
match was obtained, and no compiler verdict is claimed.

Two ways the harness could itself have produced a *false* `ADS12_UNAVAILABLE`
were closed while waiting, both precautionary rather than observed: the banner
markers now include the Thumb-specific driver wordings (`ARM Thumb C Compiler`,
`ARM Thumb C++ Compiler`) and the `ADS1.2` version strings, because the surviving
command line names the Thumb drivers; and the root lookup searches one level
down for a versioned product directory, because ADS 1.2 installs as one and an
operator may point `ADS12_ROOT` at either the version directory or its parent.
Tests cover the accept and reject sets, and one asserts the deeper search stops
after a single level so no path is invented.

`scripts\check.cmd` after these changes: **OVERALL PASS**, exit 0, gates 5 and 6
reported `BLOCKED`. Full suite 267 passed.

## Semantic self-check of the probe source, 2026-09-29

Running the reconstruction on the host found four defects that reading had not,
none of which could ever have matched the ROM. `src/probes/gbaram_selftest.c`
compiles `GBARam.c` for x86 and executes the allocator, checking payload bounds,
non-overlap, free-list integrity and the conservation of free bytes across 230
checks. This is **not compiler evidence**; it is the one check a compiler can
perform here that the ROM cannot.

| defect | how it surfaced |
| --- | --- |
| the search loop advanced without testing the neighbour word, so index 0 became a valid-looking pointer instead of terminating | the self-check **hung** |
| `0x7FFFFFFF` was read as a dead size guard; it is the search's initial best-size sentinel, and `r3` is reassigned at `0x0803D5E6` | re-reading the loop with that reassignment in view |
| three of six coalesce cases merged into the wrong neighbour and one passed `sub_0803D56A` its arguments reversed | free total collapsed to 172 bytes instead of 260,088 |
| the source was unsigned where the ROM emits `asrs` and `bge` | reading the signedness of the emitted shift and branches |

Two semantic consequences are now recorded: the search is **best-fit** (the
smallest block strictly larger than the request, with an exact-size shortcut),
and the allocator has **no out-of-memory path** (`best` is dereferenced
unconditionally). The previously unresolved `sub_0803D56A` store at
`absorbed+0x04` is behaviourally consistent with neighbour links used for
coalescing, though the field's name remains unknown and consistency is not proof.

Full suite 268 passed. `scripts\check.cmd` still **OVERALL PASS**, exit 0, with
gates 5 and 6 `BLOCKED`.

## ADS 1.2 installation and licence audit, 2026-09-29

ADS 1.2 Build 805 was installed at `C:\Program Files (x86)\ARM\ADSv1_2`, with all
seven required tools present in `Bin\` and the directory added to the machine
`PATH`. Real banners were captured, which validates `BANNER_ASSUMPTION` and
**corrects** it: the Thumb drivers print `Thumb C++ Compiler` / `Thumb C Compiler`
with **no `ARM` prefix**, whereas the precautionary markers had guessed
"ARM Thumb C++ Compiler". The installation was identified only because `ADS1.2`
was also in the marker list. That `tcpp` is the *Thumb C++ Compiler* upgrades the
section 2 inference from `INFERRED` to `CONFIRMED` for this installation.

**The tools cannot run.** FLEXlm refuses every build tool: `tcpp` gives
`C3397E: Cannot obtain license for compiler ... No such feature exists`, `armasm`
gives `A1439E` for feature `armasm`, and `armlink` gives `L6579E ... License does
not match configuration file`. A bare invocation does not show this, because ADS
prints its banner before the licence check; asking `tcpp` to compile one line
does, and it produces no object file.

A content-based scan of the installation (2,822 files) and the installer media
(1,189 files) found exactly two FLEXlm licence files plus their identical media
copies, all containing a single feature: `Win32_CWIDE_Unlimited`, vendor
`metrowks` - the bundled Metrowerks CodeWarrior IDE licence. **No file anywhere
contains a `compiler`, `armasm` or `armlink` feature**, and `C:\ADS12_INSTALL`
does not exist. No `ARMLMD_LICENSE_FILE`, `LM_LICENSE_FILE` or
`ARM_LICENSE_FILE` is set at any scope, so ADS falls back to its default path,
`...\ADSv1_2\licenses\license.dat`, which is that one-feature file.

    NO INCLUDED LICENSE COVERS THE REQUIRED BUILD TOOLS

Two harness defects were exposed by this state, which is distinct from "not
installed", and both are fixed: the CLI's default report judged the probe ready
from the mere presence of an identified toolchain, so it exited 0 while nothing
was usable; and gate 6 branched on the literal `ADS12_UNAVAILABLE`, so a licence
blocker would have failed the gate rather than being reported. Both now key on
the blocker code itself, and the new `ADS12_LICENSE_UNAVAILABLE` code carries the
FLEXlm evidence. Full suite 269 passed; `scripts\check.cmd` **OVERALL PASS**,
exit 0, gate 6 `BLOCKED (ADS12_LICENSE_UNAVAILABLE)`.

---

# Validation report - `DECOMP-RUNTIME-IWRAM-001` (2026-09-29)

**Focused validation only, as the ticket directed. The full suite was NOT run.**
The canonical ROM was re-verified before and after: SHA-1
`F1C4B07554D2A3B1AD2F325307051E775CE68087`, mtime `2026-08-19T18:10:12` -
unchanged.

## Commands run, and their measured results

```
# focused tests: the lift loop, the neighbouring collection/object work, the maps
python -m pytest tests/test_lift.py tests/test_lift_iwramblock.py \
    tests/test_lift_collectionflush3.py tests/test_lift_collectioninsert2.py \
    tests/test_lift_collectionwrite2.py tests/test_lift_collectionread.py \
    tests/test_lift_append.py tests/test_lift_native178.py tests/test_ewram_layout.py \
    tests/test_object_layout.py tests/test_object_constructor.py tests/test_regions.py \
    tests/test_rom_map.py tests/test_identity.py tests/test_fixed_regions.py \
    -q -p no:cacheprovider
# 392 passed in 99.12s      (232 before this ticket; +160 with the new target)

# the rest of the lift loop and the harness it shares, added so that nothing the
# derivation and the registry touch is left unmeasured
python -m pytest tests/test_compiler_probe.py tests/test_lift_arith.py \
    tests/test_lift_booluse.py tests/test_lift_effect.py tests/test_lift_flagmask.py \
    tests/test_lift_flagread.py tests/test_lift_flagstate.py tests/test_lift_handler2.py \
    tests/test_lift_layout.py tests/test_lift_operand.py tests/test_lift_script.py \
    tests/test_lift_stack.py tests/test_lift_use.py tests/test_stackflow_tracker.py \
    tests/test_toolchain.py -q -p no:cacheprovider
# 460 passed in 150.85s

# deterministic report regeneration, the same command gate 7 runs
python -m buusfury lift --target all --verify
# 20/20 REPORT: PASS, exit 0

# the new target's own loop
python -m buusfury lift --target iwramblock --write config/lift_iwramblock.json
# SEMANTIC      PROVEN   165 behavioural assertions, 0 failures (minimum 160)
# MODERN_BUILD  PASS     arm-none-eabi-gcc 16.1.0, linked at 0x087B810C, 552 bytes
# ADS_MATCH     BLOCKED  ADS12_LICENSE_UNAVAILABLE

# ROM integrity, before and after every write
Get-FileHash -Algorithm SHA1 'C:\Dev\log1-remake\roms\Dragon Ball Z - Buu''s Fury (U).gba'
# F1C4B07554D2A3B1AD2F325307051E775CE68087
```

`scripts/check.ps1` was deliberately **not** run: its pytest gate is
`pytest tests -q`, i.e. the whole suite, which this ticket's validation section
forbids. Gate 7's own command was run directly instead, and it is byte for byte
the command the gate executes.

**852 tests passed** across the 30 test files that this ticket can affect. The two
files not run are `tests/test_build.py` (the asset/JCALG1 leg) and
`tests/test_gba.py`; neither reads the lift registry, the lift derivation or the
region map, and neither was touched.

The modern toolchain is ARM-capable and was proven so rather than assumed: a
two-line function compiled with `arm-none-eabi-gcc -mcpu=arm7tdmi -marm -O1` and
disassembled to three ARM instructions (`add r1,r1,r1,lsl #1` / `add r0,r1,r0` /
`bx lr`). This is the first lift target in the project in **ARM** state; every
earlier one is Thumb.

## Report regression

**19 of the 20 committed reports are byte-identical to the previous revision.**
`git diff --stat -- config` reports exactly two changed files, and one of them is
the registry:

| file | change |
| --- | --- |
| `config/lift_iwramblock.json` | **new** (the target's report) |
| `config/lift_targets.json` | the new entry, plus one corrected note |
| `config/lift_collectionflush3.json` | **one field only**: `/target/notes` |

The `collectionflush3` report changed because new evidence refutes a claim that
note made, and per this project's own rule a known error is corrected and the
deviation declared rather than frozen to satisfy a byte-identity check. A
key-by-key comparison against `HEAD` reports exactly one difference:

```
DIFF at /target/notes
```

Nothing else in that report moved: not a verdict, not a comparison count, not a
function row. The other eighteen reports were not rewritten at all.

## What the new target measures

| | original | modern |
| --- | ---: | ---: |
| bytes | 256 | 552 |
| code bytes (no literal pool) | 256 | 552 |
| instructions in the four functions | 16 / 21 / 23 / 4 | 47 / 45 / 39 / 7 |
| differing bytes in the overlap | - | 226 |
| matching instruction spans | - | **0** of 64 |
| `byte_identical` | - | **false** |
| `is_a_match_claim` | - | **false** |

No match is claimed. The structural agreement that does hold is the one the loop
exists to expose: every function is paired by name, all four are leaves on both
sides (0 calls, 0 literal slots), the unit has no literal pool on either side, and
the 64 instruction spans keyed on the **original's** boundaries account for 256 of
the 256 original bytes with no uncovered remainder.

The three verdicts are independent and were read separately:
**SEMANTIC PROVEN** (the reconstruction was run and 165 assertions passed),
**MODERN_BUILD PASS** (it compiles and emits ARM bytes), **ADS_MATCH BLOCKED**
(never compiled by the tool it targets; no byte-match claim is made).

## The behaviours the semantic check pins

Sixteen sizes through each of the four routines, with the expected written-byte
counts computed **by hand from the ARM instructions** rather than from the C: the
32-byte and 16-byte fast paths, the round-up tails (5 -> 8, 7 -> 8, 17 -> 18,
33 -> 34), the fact that a **zero-size call still stores one unit**, that the fill
writes the **whole 32-bit word** (`0xDEADBEEF` must not become `0xEFEFEFEF`), and
that the 2-byte copy's computed-jump entry always starts at source offset 0. Two
defects were caught this way before any compiler run: the same table asserted
`0x030007FC` occurs exactly once in the image when it occurs once *aligned* and
once more at an odd offset, and an earlier draft of the derivation reused the loop
variable `address` after the veneer walk and silently truncated the reported
family extent by one stub - the derivation now fails closed on that invariant
(`the veneer family's end does not follow its last stub`).

## Corrections carried, and their evidence

| artifact | claim | status |
| --- | --- | --- |
| `src/ByteCodeInterpreter_collectionflush3.c`, `docs/LIFT_COLLECTIONFLUSH3.md`, `config/lift_targets.json` | the trampoline at `0x0804912C` "jumps to whatever is stored at `0x030007A8`", so the call is "NOT statically resolvable" | **REFUTED** by `0xE51FF004` = `ldr pc,[pc,#-4]`; the literal is the destination |
| `docs/ROM_MAP_PROVENANCE.md` section 2 | the DMA3 transfer size is unresolved; `CNT_H = 0x8400` read as 16-bit gives 2,050 bytes | **RESOLVED** at 4,100 bytes by the block tiling both ends exactly |
| `docs/LIFT_COLLECTIONFLUSH3.md`, `LIFT_APPEND.md`, `LIFT_NATIVE178.md` | `object + 0x00` is untouched | **REFUTED for `sub_08011B04`**: `0x08011C02` writes 0 and `0x08011C06` writes 1 |
| `tests/test_lift_collectionflush3.py` | pinned the refuted sentence | repointed at the correction |

## Safety

No ROM was written, patched, truncated or renamed. The canonical ROM was
read-only throughout and its SHA-1 and mtime are unchanged. No ROM data, no
extracted blob and no proprietary binary is tracked: the new files are source, a
self-check, a test, a document and a report. `C:\Dev\log1-remake` was read (its
`roms/` copy of the canonical dump) and never written. No `--defsym` appears in
any report, no ARM interworking veneer symbol appears in any build, and the
reconstruction's instruction set is declared `arm` on the target and `arm` on the
unit rather than being inferred.

---

# Validation report - `DECOMP-IWRAM-DISPATCH-001` (2026-09-30)

**Focused validation only, as the ticket directed. The full suite was NOT run.**
The canonical working copy `build/buusfury.gba` was re-verified before and after:
SHA-1 `F1C4B07554D2A3B1AD2F325307051E775CE68087`, mtime `2026-09-28T14:43:13` -
unchanged. `C:\Dev\log1-remake` stayed at `511ba74` with only its pre-existing
` M docs/DEVELOPMENT.md`, untouched by this ticket.

## Commands run, and their measured results

```
# the focused set: the lift loop, the IWRAM work on both halves of the block,
# the neighbouring collection/object/region/identity work, the shared harness
python -m pytest tests/test_lift.py tests/test_lift_iwramdispatch.py \
    tests/test_lift_iwramblock.py tests/test_lift_collectionflush3.py \
    tests/test_lift_collectioninsert2.py tests/test_lift_collectionwrite2.py \
    tests/test_lift_collectionread.py tests/test_lift_append.py \
    tests/test_lift_native178.py tests/test_ewram_layout.py \
    tests/test_object_layout.py tests/test_object_constructor.py \
    tests/test_regions.py tests/test_rom_map.py tests/test_identity.py \
    tests/test_fixed_regions.py tests/test_compiler_probe.py \
    tests/test_lift_arith.py tests/test_lift_booluse.py tests/test_lift_effect.py \
    tests/test_lift_flagmask.py tests/test_lift_flagread.py \
    tests/test_lift_flagstate.py tests/test_lift_handler2.py tests/test_lift_layout.py \
    tests/test_lift_operand.py tests/test_lift_script.py tests/test_lift_stack.py \
    tests/test_lift_use.py tests/test_stackflow_tracker.py tests/test_toolchain.py \
    -q -p no:cacheprovider
# 880 passed in 495.35s

# the new target's own file, on its own
python -m pytest tests/test_lift_iwramdispatch.py -q -p no:cacheprovider
# 29 passed in 10.78s

# deterministic report regeneration, key by key, the command gate 7 runs
python -m buusfury lift --target all --rom build/buusfury.gba --verify
# 21/21 REPORT: PASS (the whole document regenerated identically), exit 0

# the new target's own loop
python -m buusfury lift --target iwramdispatch --rom build/buusfury.gba
# SEMANTIC      PROVEN   277 behavioural assertions, 0 failures (minimum 90)
# MODERN_BUILD  PASS     arm-none-eabi-gcc 16.1.0, linked at 0x087B8510, 472 bytes
# ADS_MATCH     BLOCKED  ADS12_LICENSE_UNAVAILABLE
# comparison    308 original vs 472 modern, 257 differing bytes,
#               0 of 75 instruction spans identical, byte_identical FALSE,
#               is_a_match_claim FALSE
```

`scripts/check.ps1` was deliberately **not** run: its pytest gate is
`pytest tests -q`, i.e. the whole suite, which this ticket's validation section
forbids. Gate 7's own command was run directly and is the command the gate
executes; its ticket list was extended to name `DECOMP-IWRAM-DISPATCH-001`.

The modern toolchain was exercised in **ARM** state again and produced 472 bytes
from a 300-byte original. **A modern build is not a match.** The reconstruction is
larger because C cannot express the SPSR access, the CPSR mode switch or the
ARM-to-Thumb-to-ARM return, so those are environment calls rather than inline
instructions. The comparison asserts `byte_identical` is false.

## Report regression

**Every report regenerates identically except the one this ticket intends to
change.** `config/lift_iwramdispatch.json` is new. `config/lift_iwramblock.json`
changed, and a key-by-key diff against `HEAD` reports **exactly three
differences**, every one of them a measured correction declared in
[`LIFT_IWRAM_DISPATCH.md`](LIFT_IWRAM_DISPATCH.md) section 8:

| key | change |
| --- | --- |
| `/boundary_evidence/iwram_runtime/installed_block/transfer_width_decided_by` | "leaves eight of the thirteen veneer destinations outside the copied block" -> the count is **derived** and reads `3`, with the three destinations named |
| `/boundary_evidence/iwram_runtime/installed_block/veneer_destinations_outside_the_16_bit_reading` | **added**: the derived evidence the score above rests on |
| `/boundary_evidence/iwram_runtime/words_naming_the_block_anywhere_in_it/method` | the 4-byte-aligned census is now declared a **LOWER BOUND**, with both measurements (129 values / 257 windows against 225 / 533) |

`tests/test_lift_iwramblock.py` was updated for the first of those: it used to
assert the prose `"the 16-bit reading leaves eight"` and now pins the derivation,
so the number cannot drift back. Its `test_it_is_the_first_arm_target_and_the_only_one`
was **widened deliberately**, which is what that test's own docstring instructs
when a second ARM target appears; the list is still exact, so a third cannot
appear unnoticed.

## Corrections carried, and their evidence

| artifact | claim | status |
| --- | --- | --- |
| `docs/LIFT_IWRAM_RUNTIME.md`, `docs/ROM_MAP_PROVENANCE.md`, `lift.py` docstring | "the 16-bit reading ... leaves **eight** of the thirteen veneer destinations outside the copied block" | **CORRECTED to three** (`0x03000858`, `0x03000A4C`, `0x03000CA0`); the count is now derived from the destination list rather than restated |
| `docs/LIFT_IWRAM_RUNTIME.md` | "**all four** block-memory slots ... occur exactly once" | **CORRECTED**: `0x030007FC` occurs twice, and the same sentence lists it among the five that do not |
| `config/lift_iwramblock.json` method note | the census "finds LITERALS only", stated of a 4-byte-aligned scan | **CORRECTED**: it is a lower bound; 2-byte alignment adds 96 values over 276 windows |
| this ticket's own recon brief | priority order "bit14, bit7, bit6, ..., bit18, bit19" | **REFUTED** and corrected inside the derivation: the masks are bits 0-13, and the trap was reading capstone's second immediate operand instead of applying the ARM rotation |
| this ticket's own recon brief | "the five functions reached only through the three ROM-stored pointers" | **REFUTED for two**: `0x03000330` occurs nowhere in the image at any byte offset, and `0x03000414` occurs once inside asset data with no reader |

## Safety

No ROM was written, patched, truncated or renamed. No `.gba`, save or state is
tracked. The new tracked files are two C sources, a shim, a self-check, a test, a
document and a report. `src/IwramDispatch.c` carries no `--defsym`, declares its
instruction set as `arm` on the target and on the unit, and adds one guarded
weak default definition per environment hook so that the translation unit links
on its own for the modern-build verdict; the host self-check defines
`IWRAMDISPATCH_HOST_TEST` and supplies its own, so the defaults are never
executed by the behavioural check.

**Housekeeping, disclosed rather than hidden:** `C:\Dev\buusfury-decomp\reference\tools\`
holds an mGBA 0.10.5 win64 build downloaded before it was established that the
project's runtime tooling already exists in `C:\Dev\log1-remake\tools\runtime\`
and that mGBA 0.10.5 and 0.11.0 are both already installed. It is untracked and
gitignored, it was not used, and it is a delete-on-request duplicate.
