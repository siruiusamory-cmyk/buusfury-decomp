# Legacy of Goku Remake Toolchain

This project is a reproducible reverse-engineering laboratory for Webfoot's Dragon Ball Z GBA trilogy. The long-term target is a Legacy of Goku campaign rebuilt on the Buu's Fury engine, guided by Legacy of Goku II gameplay. No remake content or ROM editing exists yet.

## Legal boundary

This repository does not distribute ROMs, BIOS images, extracted game assets, or other proprietary game data. Supply only ROMs you legally obtained. `roms/`, generated ROMs, extracted data, dumps, build output, and upstream clones are Git-ignored.

## Requirements

- Windows PowerShell
- Git
- `uv` 0.11 or newer; setup uses `uv.lock` and installs Python 3.12 when needed
- Optional for upstream experiments: CMake and Visual Studio 2022 C++ Build Tools
- mGBA for later manual emulator checks

ARM Developer Suite 1.2 is required by the historical Buu's Fury disassembly build, but is not required for Phase 0 and is not installed by this project.

## Setup

```powershell
cd <checkout>
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
```

The process-scoped execution-policy change lasts only for the current PowerShell process. It is needed when Windows reports the default effective policy as Restricted; the setup does not change machine or user policy.

`setup.ps1` creates or repairs `.venv`, synchronizes the exact dependency set in `uv.lock`, installs this project in editable mode, and clones/checks out the exact commits in `upstreams.lock`. Existing clone origins are verified before fetch. Use `-SkipUpstreams` to install only the Python project.

Manual equivalent:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

The manual pip command is supported but resolves declared dependency constraints; use `setup.ps1` for the locked reproducible environment.

## ROM identification

Leave your own ROM at its existing path beneath `roms\`; do not rename it for this tool.

```powershell
webfoot identify ".\roms\Dragon Ball Z - Buu's Fury (U).gba"
python -m tools.webfoot identify ".\roms\Dragon Ball Z - Buu's Fury (U).gba"
```

The command streams CRC32, MD5, SHA-1, and SHA-256; parses minimal GBA header metadata; and compares exact SHA-256 identity plus configured corroborating metadata against `config\roms.yaml`. Built packages carry the same default catalog as package data. Exit code `0` means `VERIFIED`, `1` means `UNKNOWN`, and `2` means malformed input, profile conflict, or ambiguity. Game code, size, revision, MD5, or SHA-1 alone never yields `VERIFIED`.

Validate every MapEntry in the exact supported Buu's Fury profile without writing the ROM:

```powershell
webfoot validate-map-entries ".\roms\Dragon Ball Z - Buu's Fury (U).gba"
```

The command reads all 452 configured `0x38`-byte records, parses and serializes each in memory, and fails if any serialized byte differs. ROM-002 also enforces the fixed target SHA-256 and canonical table tuple, so an alternate catalog cannot relabel another ROM or redirect validation. It does not follow record pointers or expose an editing operation.

Run the read-only pointer-field census without dereferencing targets:

```powershell
webfoot map-entries pointer-census ".\roms\Dragon Ball Z - Buu's Fury (U).gba"
```

The census classifies all 4,068 raw candidate observations as null, valid in-ROM, or out of range; reports alignment, duplicates, numeric target ranges, and count/pointer correlations; and never reads pointed-to data.

Read exactly the first little-endian word at each validated variation-array target:

```powershell
webfoot variation-arrays first-word-census ".\roms\Dragon Ball Z - Buu's Fury (U).gba"
```

This read-only command requires the canonical packaged ROM identity, bounds-checks every four-byte access, and does not read a second word or follow the observed raw value.

## Tests

```powershell
.\scripts\test.ps1
```

Committed fixtures use synthetic bytes only. When the user's exact local ROM is present, one runtime integration test validates its complete MapEntry table; otherwise that test skips. No ROM-derived fixture is committed.

## Emulator

Phase 0 found mGBA at `C:\Program Files\mGBA\mGBA.exe`. A later ticket may invoke it explicitly against generated ROM output. Emulator automation is intentionally not implemented yet; never point an automated modification workflow at an original file beneath `roms\`.

## Current scope

Implemented: streaming hashes, GBA header parsing, exact ROM profiles, conservative matching, CLI packaging, pinned upstream setup, research audit, byte-exact read-only Buu's Fury MapEntry round-trip validation, a non-dereferencing pointer-field census, and an exact-width variation-array first-word census.

Not implemented: ROM modification, pointer following, semantic MapEntry editing, map editing, Tiled integration, allocation, relocation, compression integration, scripts, graphics, audio, gameplay, or remake content.

The next ticket will be selected after ROM-002 review; it is not implemented here.
