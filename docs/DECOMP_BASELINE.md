# DECOMP-BASELINE-001 + DECOMP-BOOTSTRAP-001 - baseline

**Status:** baseline established. Identity gate, byte map, toolchain inventory and
the reproducible parts of the build are all in place and verified. Full source
reproduction is **blocked**, with the blocker measured and evidenced below.

**Date:** 2026-09-28
**Repository:** `C:\Dev\buusfury-decomp`
**ROM touched:** read-only, never modified.

---

## 1. Canonical ROM identity

| | |
| --- | --- |
| Game | Dragon Ball Z: Buu's Fury |
| Platform | Game Boy Advance |
| Region / revision | USA, rev0 |
| Size | 8,388,608 bytes |
| **SHA-1** | `f1c4b07554d2a3b1ad2f325307051e775ce68087` |
| SHA-256 | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| MD5 | `3a74fce97f1ea2b28c2a50ec3df0acee` |
| CRC-32 | `01C1707F` |
| Header title | `DBZBUUSFURY` (0x00A0) |
| Game code | `BG3E` (0x00AC) |
| Maker code | `70` (0x00B0) |
| Fixed value | `0x96` (0x00B2) |
| Header checksum | `0x84` (0x00BD), recomputed and validated |

**Input ROM verification: PASS.** The SHA-1 of the operator's local dump is
exactly the canonical SHA-1. It was measured with `Get-FileHash` and re-measured
independently by `tools/buusfury/identity.py`.

### One ROM, two names

The LOG1-REMAKE / Dragonbyte Z repository identifies the *same image* as profile
`buus_fury_usa_rev0_01c1707f` (by CRC-32). This is **not** a second revision.
`config/rom.json` records the alias so the two identifiers cannot drift apart.

A genuinely *different* Buu's Fury image also exists on this machine - a static
recompilation target with SHA-1 prefix `e65738e9`. Its file offsets are **not**
transferable to this ROM. It is recorded under `known_distinct_images` in
`config/rom.json` precisely so it can never be mistaken for the baserom.

### How identity is enforced

`tools/buusfury/identity.py` applies two independent checks and reports **every**
mismatch at once:

1. **Whole-file digests** - SHA-1 (canonical), SHA-256, MD5, CRC-32.
2. **GBA cartridge header** - title, game code, maker code, fixed value, main
   unit code, device type, software version, and a recomputed header checksum.

Check 2 is not redundant. Check 1 only refuses; check 2 *diagnoses* - it turns
"not the ROM you asked for" into "this is a different revision, here is its game
code". Every entry point (`verify`, `assets`, `build`, `status`) calls it first
and raises before touching anything else.

---

## 2. The public reference project

The only public Buu's Fury disassembly is **`2genkidev/buusfury`**
(<https://github.com/2genkidev/buusfury>), pinned at
`cc53d0cd2d1c167e749419187e2d92017ac07468` (the tip of `master`, 2025-07-27).

It was studied read-only. It is treated as research material, **not** as a source
to copy. Full detail in [`REFERENCE_AUDIT.md`](REFERENCE_AUDIT.md).

### 2.1 What it actually is

It is **not a semantic decompilation**. It is a *repackaging harness*:

- `asm/rest_of_the_game.s` is **16 lines and is pure `INCBIN`** of baserom slices.
- `build.bat` extracts **ten** ranges straight out of `baserom.gba` with
  `tools/incbin.bat`, then `INCBIN`s them back into the image.
- **8,268,168 bytes - 98.56% of the ROM - are copied verbatim from the baserom**
  and are not disassembled in any form.

### 2.2 The ADS 1.2 build path

`build.bat` invokes exactly these proprietary tools:

```
armcpp  -c src/color_transforms.cpp -o build/color_transforms.o
armcpp  -c src/strings.cpp          -o build/strings.o
armasm  asm/buu.s     -o build/buu.o
armasm  asm/GBARam.s  -o build/GBARam.o
armasm  asm/ewram.s   -o build/ewram.o
armasm  asm/iwram.s   -o build/iwram.o
armasm  asm/rest_of_the_game.s -o build/rest_of_the_game.o
armlink build/GBARam.o build/color_transforms.o build/strings.o build/buu.o \
        build/rest_of_the_game.o build/ewram.o build/iwram.o \
        -noremove -scatter scatter.ld -o build/buu.axf
fromelf build/buu.axf -bin -o build/output
```

The README also names `tcpp` and the family `armasm`, `armcpp`, `tcpp`, `armlink`,
`fromelf`. The only surviving evidence of the **original** compiler flags is a
comment preserved in `asm/GBARam.s:5`:

```
; tcpp -S -c -cpu ARM7TDMI -O1 src/GBARam.c
; For now, just assembly because of alignment issues.
```

That line is the single most valuable input for `DECOMP-COMPILER-PROBE-001`: it
names the compiler (`tcpp`), the CPU (`ARM7TDMI`) and the optimisation level
(`-O1`) for the one function whose original C source was compiled.

### 2.3 Linker / scatter layout

`scatter.ld` places sections at **absolute addresses**:

| Region | Address | Contents |
| --- | --- | --- |
| `LOAD_ROM_2` | `0x02000000` | `ewram.o (+RW)` - 0x40000 of reserved EWRAM |
| `LOAD_ROM_3` | `0x03000000` | `iwram.o (+RW)` - 0x8000 of reserved IWRAM |
| `ROM_START` | `0x08000000` | `buu.o (GameStart, Head, Init)` |
| `MEMORY_START` | `0x0803D4D0` | `GBARam.o (GBARam)` |
| `UNUSED_GBARAM` | `0x0803D740` | `buu.o (UnusedGBARam)` |
| `AFTER_LIBS` | `0x08049114` | `buu.o (AfterLibs)` |
| `COLOR_TRANSFORMATIONS` | `0x0805672C` | `color_transforms.o (.constdata)` |
| `STRINGS` | `0x0805792C` | `strings.o (+RW +ZI)` |
| `EVERYTHING_ELSE` | `0x0806D4E0` | `rest_of_the_game.o (+Code)` |

The gaps between these fixed addresses are filled with the `INCBIN` blobs and
with linker padding. `-noremove` is **load-bearing**: without it `armlink`
discards the `SPACE`-reserved EWRAM/IWRAM sections that `ewram.s`/`iwram.s`
declare.

### 2.4 Extraction / incbin process

`tools/incbin.bat <file> <startHex> <endHex>` slices a byte range out of
`baserom.gba` into `baserom.gba_<start>_<end>.extracted` using Windows PowerShell
5.1 (`Get-Content -Encoding Byte`), which is why it needs `powershell.exe` and
not `pwsh`. The ten ranges it extracts are reproduced verbatim in
`config/regions.json`, and they are the source of every `class: "incbin"` region.

### 2.5 Generated files

| File | Produced by |
| --- | --- |
| `build/asset_{intro,splash,dialogbox,dialogbox_small}.img.bin` | grit |
| `build/corner_{top_left,top_right,bottom_left,bottom_right}.img.bin` | grit |
| `build/asset_*.compressed` | JCALG1 front-end (`tools/compress`) |
| `baserom.gba_0x*_0x*.extracted` ×10 | `tools/incbin.bat` - **written to the repo root**, not to `build/` |
| `build/*.o`, `build/buu.axf`, `build/output/ROM_START` → `image.gba` | armasm/armcpp/armlink/fromelf |

### 2.6 Semantic source vs opaque regions

In the reference project, source-backed content is only **1,436 bytes of real
executable code** plus data and assets:

| Content | Bytes | Kind |
| --- | ---: | --- |
| `asm/rom_header.s` | 192 | header data |
| `asm/crt0.s` | 152 | hand-written ARM asm |
| `asm/GBARam.s` | 232 + 16 | hand-transcribed Thumb asm + 4 data words |
| `asm/buu.s` `AfterLibs` | 12 | ARM veneer + literal |
| `src/color_transforms.cpp` | 4,608 | C++ - 18 × 256-byte colour-effect LUTs |
| `src/strings.cpp` | 89,012 | C++ - 1,534 `wchar_t` literals + pointer table |
| Assets (intro, splash, dialogbox ×2, corners, palettes) | 26,112 | BMP/palette source |

**Executable-code source is therefore ~5,020 bytes: 0.06% of the ROM.**
`src/strings.cpp` alone is 1.06% of the image, and it is data, not code.

### 2.7 Assumptions hardcoded into the reference build

These are real defects and portability hazards, found by reading the build rather
than by running it. Each is either fixed or explicitly documented here.

1. **The byte comparison is commented out.** `build.bat:62` has
   `::call fc /b "baserom.gba" "image.gba"`. The script only prints a SHA-1 and
   then `rmdir /S /Q build`. **It never fails on a mismatch** - the exact failure
   mode this project must not inherit.
2. **The baserom is never verified.** Nothing checks that `baserom.gba` is the
   canonical image before copying 98.6% of it into the output.
3. **Release/Debug inconsistency.** CMake is configured with
   `-DCMAKE_BUILD_TYPE=Release` but `build.bat` runs
   `tools/compress/build/Debug/compress.exe`. This works only because a Visual
   Studio generator is multi-config and ignores `CMAKE_BUILD_TYPE`, defaulting to
   `Debug`. With a single-config generator the path does not exist.
4. **The CMake must be a Visual Studio CMake.** The MSYS2/MinGW CMake that
   devkitPro puts on `PATH` fails with
   `Could not create named generator Visual Studio 17 2022`. Verified on this
   machine. The harness therefore locates the VS-bundled CMake explicitly.
5. **x86 is mandatory.** `-A Win32` and `jcalg1_static.lib` (a prebuilt 32-bit
   library) mean the 32-bit MSVC toolchain is required, not the default x64 one.
6. **`armcpp` is invoked with no optimisation flag at all**
   (`armcpp -c src/color_transforms.cpp`). The ADS 1.2 default applies. This is
   an open question for `DECOMP-COMPILER-PROBE-001`.
7. **`src/strings.cpp` silently depends on ADS `wchar_t` being 2 bytes.** On any
   compiler where `wchar_t` is 4 bytes the file encodes the pool as UTF-32 and
   the output is wrong. There is no assertion guarding this.
8. **`tools/incbin.bat` skips when the output already exists**
   (`if exist ... exit /b`), so a stale `.extracted` file from an earlier ROM is
   silently reused.
9. **The `.extracted` files are written to the repository root**, not into
   `build/`, and only removed indirectly by the final `rmdir`. They are caught by
   the `baserom.gba*` ignore rule, which is lucky rather than designed.
10. **`rmdir /S /Q build` makes the build non-incremental** and destroys evidence
    of what was produced.
11. **A filename is misspelled upstream:** `assets/cornet_top_left.bmp`. The
    build output is spelled `corner_top_left`. The misspelling is reproduced
    exactly by this project, because it is load-bearing.
12. **Absolute addresses in `scatter.ld`** rather than symbols derived from the
    map.
13. **No ADS version check.** README requires "Arm Developer Suite v1.2", but the
    scripts accept whatever `armasm` is on `PATH`. A different ADS/RVCT major
    version would produce different code and nothing would notice.
14. **The scatter relies on the linker's section ordering within `buu.o`**
    (`GameStart, Head, Init`), which depends on `INCLUDE` order inside
    `asm/buu.s`.
15. **`opaque_10` is labelled `<null bytes>` but is 0xFF-filled.** Verified:
    all 292,440 bytes are `0xFF`. The label is wrong.

### 2.8 Licence status - decisive

**`2genkidev/buusfury` has no licence.**

- The GitHub API for the repository reports `"license": null`.
- There is no `LICENSE`, `COPYING` or `NOTICE` file at the repository root.
- The only licence present is `tools/compress/jcalg1/LICENSE`, which belongs to
  the third-party JCALG1 submodule, not to the disassembly.

Under default copyright, that means **all rights reserved**. There is no grant to
copy, modify or redistribute its source, and none to create derivative works.

**Consequence for this project:** the reference project may be read, and its build
path may be run, but **none of its source may be imported into this repository**.
That is why:

- it is fetched into `reference/`, which is gitignored;
- no ADS input source (`crt0.s`, `GBARam.s`, `buu.s`, `color_transforms.cpp`,
  `strings.cpp`) exists in this repository;
- the 94,016 ADS-built bytes cannot be reproduced from this repository even if
  ADS 1.2 were installed.

The only content taken from the reference project is **procedural knowledge**:
which byte ranges are opaque, which tool builds which region, and the exact
command lines. Facts and offsets are not copyrightable; its expression is not
copied.

### 2.9 What prevents clean reproduction on our environment

| Requirement | Status |
| --- | --- |
| Canonical baserom | **available**, SHA-1 verified |
| Python 3.12 | available |
| grit 0.9.2 | available (`C:\devkitPro\tools\bin\grit.exe`) |
| Visual Studio CMake | available |
| MSVC x86 (vcvars32) | available |
| JCALG1 sources + prebuilt lib | available via the reference checkout |
| **ARM Developer Suite 1.2** | **ABSENT** |
| **Independently authored ADS sources** | **ABSENT** (and may not be imported - §2.8) |

---

## 3. The region map

`config/regions.json` partitions the canonical ROM into **28 regions** that tile
`[0x000000, 0x800000)` **exactly** - no gaps, no overlaps. Every run re-validates
this; a gap or overlap is a hard failure.

| class | meaning | bytes | share | regions |
| --- | --- | ---: | ---: | ---: |
| `incbin` | opaque; copied verbatim from the baserom | 8,268,480 | 98.568% | 13 |
| `asset` | rebuilt from a source asset (grit / JCALG1 / palette) | 26,112 | 0.311% | 10 |
| `ads` | rebuilt from source by ARM Developer Suite 1.2 | 94,016 | 1.121% | 5 |
| **total** | | **8,388,608** | **100.000%** | **28** |

Full per-region detail: [`BUILD_REGIONS.md`](BUILD_REGIONS.md) (generated from the
config). The independent structural map is a separate artefact: see
[`ROM_MAP.md`](ROM_MAP.md) and [`ROM_MAP_PROVENANCE.md`](ROM_MAP_PROVENANCE.md).

**Provenance of the map.** It is *derived* from the reference build script and
scatter file, not independently re-derived from the binary. That is an honest
limitation and is stated in the config itself. It is nonetheless factually
verified in three independent ways:

1. it tiles the image exactly;
2. **every `asset` region was rebuilt from its source and found byte-identical**;
3. every `ads` region is genuinely one the reference build feeds to `armasm` or
   `armcpp`.

The five `ads` regions, all blocked:

| region | extent | bytes | tool | content |
| --- | --- | ---: | --- | --- |
| `crt0` | `0x0000C0-0x000158` | 152 | armasm | CPU/mode/stack init, hardware init, tail branch |
| `gbaram_text` | `0x03D4D0-0x03D5B8` | 232 | armasm | hand-transcribed Thumb allocator |
| `afterlibs_thunk` | `0x049114-0x049120` | 12 | armasm | ARM veneer to `0x08046AED` |
| `color_transforms` | `0x05672C-0x05792C` | 4,608 | armcpp | 18 × 256-byte colour-effect LUTs |
| `strings` | `0x05792C-0x06D4E0` | 89,012 | armcpp | 1,534 UTF-16LE strings + pointer table |

Two regions are *trivially promotable* but deliberately left opaque for now,
because promoting them would mean committing ROM-derived bytes for no analytical
gain:

- `rom_header` (192 B) - 156 of its bytes are the mandated Nintendo logo.
- `gbaram_data` (16 B) and `dat_080561c4` (104 B) - pure address constants.

---

## 4. The build pipeline

### 4.1 Intended end state

```
baserom.gba
  -> extraction / generation
  -> ADS compile / assemble
  -> link (scatter.ld)
  -> fromelf -bin
  -> build/buusfury.gba
  -> SHA-1 comparison
```

### 4.2 What is implemented and proven

`python -m buusfury build` implements the pipeline in region-map terms and works
in two modes.

**Strict (default).** Verify the baserom, validate the map, then rebuild every
region the map says is reproducible and **fail closed** on anything else. It
never silently copies a region it was supposed to rebuild. On this machine it
stops with `ADS12_UNAVAILABLE` and prints the exact ARM commands and the exact
two missing prerequisites.

**`--allow-passthrough`.** Assembles a complete image anyway and writes
`build/build-report.json` labelling **every** region `rebuilt-asset`,
`rebuilt-ads` or `passthrough`. The result is byte-identical to the canonical
ROM - which proves the **map** is correct - but the report makes it impossible to
mistake that for a full source reproduction.

Measured on 2026-09-28:

```
baserom SHA-1  : f1c4b07554d2a3b1ad2f325307051e775ce68087
output SHA-1   : f1c4b07554d2a3b1ad2f325307051e775ce68087
byte-identical : PASS
provenance     : 26,112 bytes rebuilt (0.311%), 8,362,496 bytes passthrough
```

### 4.3 The asset leg - a real result

This is the part of the reference project's rebuild that does **not** need ADS,
and it has been independently reproduced here:

| region | source | pipeline | bytes | result |
| --- | --- | --- | ---: | --- |
| `asset_intro` | `assets/intro.bmp` | grit → JCALG1 | 2,980 | identical |
| `asset_dialogbox` | `assets/dialogbox.bmp` | grit → JCALG1 (min 788) | 788 | identical |
| `asset_dialogbox_small` | `assets/dialogbox_small.bmp` | grit → JCALG1 | 548 | identical |
| `asset_splash` | `assets/splash.bmp` | grit → JCALG1 (min 20516) | 20,516 | identical |
| `bmp_corner_top_left` | `assets/cornet_top_left.bmp` | grit | 64 | identical |
| `bmp_corner_top_right` | `assets/corner_top_right.bmp` | grit | 64 | identical |
| `bmp_corner_bottom_left` | `assets/corner_bottom_left.bmp` | grit | 64 | identical |
| `bmp_corner_bottom_right` | `assets/corner_bottom_right.bmp` | grit | 64 | identical |
| `palette_bg` | `assets/palettes/bg.pal` | copy | 512 | identical |
| `palette_sprite` | `assets/palettes/sprite.pal` | copy | 512 | identical |
| | | | **26,112** | **10/10** |

Independent corroboration that these boundaries are right, not merely asserted:

- grit's decompressed sizes (38,400 / 10,240) match the size fields in the
  JCALG1 stream headers in the ROM exactly.
- The four 64-byte corners plus the two 512-byte palettes end **flush** at
  `0x05672C`, or the map would not tile.
- `build.bat` passes `788` as the minimum size for `asset_dialogbox`, and 788 is
  exactly the uncompressed stream's own length.

### 4.4 Reported block on the ADS leg

`python -m buusfury build` (strict) reports:

```
BUILD: BLOCKED [ADS12_UNAVAILABLE]
5 region(s), 94,016 bytes, can only be rebuilt with ARM Developer Suite 1.2,
which is not installed and whose source inputs are not available to this
repository.
```

This is an accepted baseline outcome, not a failure of the ticket: the ticket
requires a *precise, evidence-based* blocker report over a workaround.

---

## 5. The blocker

Two independent conditions must both be met to reproduce the remaining 94,016
bytes. Neither is.

### Condition 1 - a licensed ARM Developer Suite 1.2 installation

ADS 1.2 is commercial software from ~2001. It is not installed and cannot be
redistributed into this repository.

Measured on 2026-09-28:

| probe | result |
| --- | --- |
| `armasm`, `armcpp`, `armlink`, `fromelf`, `tcc`, `tcpp` on `PATH` | **not found** |
| `$ADS12_ROOT` | unset |
| `C:\Program Files\ARM`, `C:\Program Files (x86)\ARM`, `C:\ARM` | do not exist |
| Registry uninstall entries matching ARM / ADS / RVCT / RealView / Keil | none |
| Start Menu shortcuts matching ARM / ADS / Developer Suite / RealView | none |

### Condition 2 - independently authored sources for those regions

Even with ADS 1.2 installed, this repository cannot build those regions: it
contains no input source for them, and none may be imported from the only public
copy because that copy carries **no licence** (§2.8).

Writing those sources *is* the decompilation work. It is the object of the
tickets that follow, not of this one.

### Consequence

> **Full source reproduction of the canonical ROM is not achievable on this
> machine at this time.** 26,112 bytes (0.311%) are independently reproduced and
> verified; 8,268,480 bytes (98.568%) are opaque in the public reference project
> too; 94,016 bytes (1.121%) require ADS 1.2 *and* sources that do not yet exist.

No workaround has been applied. The `--allow-passthrough` mode exists solely to
prove the map and is labelled as such in its report.

---

## 6. Validation gate

| # | Requirement | Result |
| --- | --- | --- |
| 1 | Input ROM SHA-1 is exactly canonical | **PASS** |
| 2 | Build reproducible from a clean checkout + local dependencies | **PARTIAL** - harness, map and asset leg reproduced from a clean checkout; the ADS leg is blocked (§5) |
| 3 | Produced ROM byte-identical to canonical, or inability precisely documented | **PASS** - byte-identical under `--allow-passthrough` (proves the map); inability to rebuild 94,016 bytes documented with evidence |
| 4 | No ROM tracked by Git | **PASS** |
| 5 | No proprietary toolchain binary tracked | **PASS** |
| 6 | Existing Dragonbyte Z files untouched | **PASS** |
| 7 | Build documented clearly enough for a new contributor | **PASS** - this document, `README.md`, `docs/DEVELOPMENT.md`, `DEPENDENCIES.md`, `ADS12_SETUP.md` |
| 8 | Current disassembly/source coverage inventoried | **PASS** - §3, `BUILD_REGIONS.md`, `REFERENCE_AUDIT.md` |
| 9 | No new gameplay function decompilation begun | **PASS** - no `src/` or `asm/` reconstruction exists |

86 portable tests pass. Exact commands and raw output:
[`VALIDATION_REPORT.md`](VALIDATION_REPORT.md).

---

## 7. Reproducing this baseline

```powershell
# 0. prerequisites: Python 3.11+, Git, and a legally dumped canonical ROM
#    (see DEPENDENCIES.md; ADS 1.2 optional and only needed for the ADS leg)

# 1. place the baserom outside Git tracking
Copy-Item 'D:\dumps\Dragon Ball Z - Buu''s Fury (U).gba' C:\Dev\buusfury-decomp\baserom.gba

# 2. verify identity, map, assets and tests in one command
pwsh -File scripts/check.ps1

# 3. fetch the reference checkout + source assets (gitignored), and build the
#    JCALG1 front-end
pwsh -File scripts/fetch-reference.ps1 -BuildTools

# 4. strict build - stops with the precise ADS blocker
pwsh -File scripts/build.ps1

# 5. assemble a byte-identical image with a labelled provenance report
pwsh -File scripts/build.ps1 -AllowPassthrough
python -m buusfury build --allow-passthrough --report build/build-report.json
```

Environment variables, all optional:

| Variable | Purpose |
| --- | --- |
| `BUUSFURY_ROM` | baserom path (overrides `./baserom.gba`) |
| `BUUSFURY_REFERENCE` | fetched reference checkout root |
| `BUUSFURY_COMPRESS` | JCALG1 front-end binary |
| `ADS12_ROOT` | ARM Developer Suite 1.2 root |
| `GRIT`, `CMAKE` | tool overrides |

No tracked file contains a machine-specific absolute path.

---

## 8. Recommended next tickets

> **EXTENDED (2026-09-29) by `DECOMP-ROM-MAP-001`.** Ticket 1 below ran; its
> structural map now lives in [`ROM_MAP.md`](ROM_MAP.md) with its evidence in
> [`ROM_MAP_PROVENANCE.md`](ROM_MAP_PROVENANCE.md). Two corrections to this
> document came out of that work:
>
> - The four compressed assets were called "JCALG1" here. That name is **not
>   supported**. Their 8-byte prologue is `kind = 1` at `+0x00` and
>   `declared_size` at `+0x04`, which is the engine's own container shape; the
>   bytes are proven by reproduction, the codec's name is not. The structural map
>   now says `compressed_asset` and names no codec.
> - The reset path's DMA3 source `0x087B79A4` is recorded here as referencing a
>   blob. Its transfer size is **unresolved** (`CNT_H = 0x8400`: a 16-bit
>   decrementing reading gives 2,050 bytes below that address; a 32-bit
>   incrementing reading gives 4,100 bytes above it, ending exactly at the `0xFF`
>   fill). The `codec_blob` region is bounded by CONTENT instead, which does not
>   depend on the answer.

1. **`DECOMP-ROM-MAP-001`** - replace the *derived* map with an independently
   re-derived one, and promote the three zero-toolchain regions
   (`rom_header`, `gbaram_data`, `dat_080561c4`) from `incbin` to `generated`.
2. **`DECOMP-COMPILER-PROBE-001`** - determine whether a free toolchain can
   reproduce the ADS code. The primary lead is `asm/GBARam.s:5`, which names
   `tcpp -S -c -cpu ARM7TDMI -O1`; the secondary is that `armcpp` is invoked with
   no optimisation flag at all. The two 4,608/89,012-byte `armcpp` regions and
   the 152-byte `crt0` are the only cheap experiments available before the
   opaque 8.27 MB is opened.

Only after those should any work begin on the 98.568% opaque region.
