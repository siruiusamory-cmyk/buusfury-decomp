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
`\n` to `os.linesep` on Windows, so the generated `docs/ROM_MAP.md` was written
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
| 8 | Disassembly/source coverage inventoried | **PASS** | `docs/ROM_MAP.md`, `docs/REFERENCE_AUDIT.md` §2 |
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
