# Legacy of Goku Remake Toolchain

Phase 0 builds a reproducible reverse-engineering laboratory for Webfoot's Dragon Ball Z GBA trilogy. The long-term target is a Legacy of Goku campaign rebuilt on the Buu's Fury engine, guided by Legacy of Goku II gameplay. No remake content or ROM editing exists yet.

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

## Tests

```powershell
.\scripts\test.ps1
```

Tests use synthetic bytes only. No ROM-derived fixture is committed.

## Emulator

Phase 0 found mGBA at `C:\Program Files\mGBA\mGBA.exe`. A later ticket may invoke it explicitly against generated ROM output. Emulator automation is intentionally not implemented yet; never point an automated modification workflow at an original file beneath `roms\`.

## Current scope

Implemented: streaming hashes, GBA header parsing, exact ROM profiles, conservative matching, CLI packaging, pinned upstream setup, research audit, and synthetic tests.

Not implemented: parsing or serializing `MapEntry`, ROM modification, map editing, Tiled integration, allocation, relocation, compression integration, scripts, graphics, audio, gameplay, or remake content.

Next ticket: `ROM-002 - byte-exact Buu's Fury MapEntry parser/serializer`.
