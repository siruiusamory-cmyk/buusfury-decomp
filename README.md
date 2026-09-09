# Legacy of Goku Remake Toolchain

This project is a modding SDK and reproducible reverse-engineering laboratory for
Webfoot's Dragon Ball Z GBA trilogy: inspect, extract, decode, edit, validate and
rebuild. The long-term target is a Legacy of Goku campaign rebuilt on the Buu's
Fury engine, guided by Legacy of Goku II gameplay.

Editing is real but deliberately narrow. Every write goes verified base image ->
generated output, the canonical ROM is never modified in place, and an unchanged
project rebuilds the entire ROM byte-identically. Anything not proven against the
canonical image is refused rather than approximated.

## Public progress website

The repository includes a one-page Astro site that explains the SDK's current
authoring frontier. Almost every public status update belongs in one typed data
file: `src/data/project.ts`.

Install and run it with npm:

```powershell
npm install
npm run dev
npm run build
npm run preview
```

The public site is deployed at
<https://siruiusamory.gitlab.io/log1-remake/>. GitLab Pages builds it from the
repository's default branch with `.gitlab-ci.yml`; the pipeline runs the focused
site checks, builds Astro, and publishes `dist/` without committing generated
output. GitLab's Pages settings show the active deployment URL and are also
where a future custom domain would be configured.

In `src/data/project.ts`, edit `overallProgress` and `overallProgressLabel` to
change the explicitly approximate headline. Update the blocker fields to move
the current frontier, change a milestone's `status` to `complete`, `current`,
`next`, or `target`, and append a typed item to `breakthroughs` for a new log
entry. Breakthrough `date` and `commit` fields are optional; omit them when the
project has no verified value. Footer links are also optional and disappear
when their `url` is absent.

At ticket closure, classify the measured result as
`public progress impact: UPDATED` or `public progress impact: NONE`. `UPDATED`
means the result changes public capability, the blocker/frontier, the
capability-based AUTHOR_NEW questline, a completed capability's wording, a
meaningful outside-facing breakthrough, or the acceptance-target story. Update
`src/data/project.ts`, then run `npm run check` and `npm run build`; normally the
status change belongs in the capability's ticket commit. `NONE` requires a
one-sentence reason and no cosmetic website edit.

The overall percentage is a directional product estimate, never a calculation
from ticket count. Change it only when the maintainer reviews it explicitly or a broader
roadmap review finds a material shift. Milestones are authoritative. Questline
entries represent capabilities rather than ticket numbers, and breakthroughs
are reserved for results useful to outside visitors. Never invent dates.

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

Find every MapEntry whose already-bounded first-word observation matches one exact value:

```powershell
webfoot variation-arrays find-first-word ".\roms\Dragon Ball Z - Buu's Fury (U).gba" 0x0822CC08
```

The lookup reports indices, variation-array source addresses, and raw MapEntry metadata. It still reads only target `+0x00` and never follows the matched value.

## Graphics

Inspect the verified actor sprite corpus. Extraction into a project remains the
authoring workflow; these commands are for looking, not editing.

```powershell
webfoot graphics summary ".\roms\Dragon Ball Z - Buu's Fury (U).gba"
webfoot graphics list ".\roms\Dragon Ball Z - Buu's Fury (U).gba" --shared-only
webfoot graphics export ".\roms\Dragon Ball Z - Buu's Fury (U).gba" "<profile>/graphic:0768" --out buu.png
```

Before changing anything, ask who else uses it. Most payloads are shared, so an
edit is usually not local:

```powershell
webfoot graphics consumers ".\roms\Dragon Ball Z - Buu's Fury (U).gba" "<profile>/graphic:1652"
webfoot graphics palette ".\roms\Dragon Ball Z - Buu's Fury (U).gba" --index 40
```

The verified pointers join the common reference graph - 7,652 anchors and 11,254
confirmed references - rather than living in a private index:

```powershell
webfoot graphics references ".\roms\Dragon Ball Z - Buu's Fury (U).gba"
```

Assets are named by stable profile-qualified identity, never by ROM address, so a
name survives a rebuild. See
[`docs/research/GRAPHICS_FORMAT.md`](docs/research/GRAPHICS_FORMAT.md) for the
format evidence, the corpus counts, and the capability matrix.

## Tests

```powershell
.\scripts\test.ps1
```

Committed fixtures use synthetic bytes only. When the user's exact local ROM is present, one runtime integration test validates its complete MapEntry table; otherwise that test skips. No ROM-derived fixture is committed.

## the tool Research Workflow

- Permanent project rules: [`docs/DEVELOPMENT.md`](<local-state-name>)
- Current verified state: [`docs/PROJECT_<local-state-name>`](docs/PROJECT_<local-state-name>)
- Current research ticket: [`docs/PROJECT_<local-state-name>`](docs/PROJECT_<local-state-name>)
- Detailed evidence: [`docs/reverse-engineering.md`](docs/reverse-engineering.md) and [`docs/consumer-analysis.md`](docs/consumer-analysis.md)

Inspect the handoff without launching the tool:

```powershell
.\scripts\run-current.ps1 -DryRun
```

Launch the current ticket from any working directory:

```powershell
<checkout>\scripts\run-current.ps1
```

From the repository root, use `.\scripts\run-current.ps1`. Completed-ticket
archival and replacement are documented in
[`docs/README.md`](docs/README.md).

## Emulator

Phase 0 found mGBA at `C:\Program Files\mGBA\mGBA.exe`. Bounded read-only
runtime research may use the verified local ROM with ignored working copies of
private saves and states. Never let emulator automation modify the original ROM;
future write experiments must target generated output only.

## Current scope

Implemented: streaming hashes, GBA header parsing, exact ROM profiles and
conservative matching, profile-declared capabilities, CLI packaging, pinned
upstream setup, deterministic project extract / validate / build with an exact
whole-ROM no-op rebuild, and transactional attributed writes. Byte-exact
round-trips exist for enemy and character stats, Buu's Fury text, Legacy of Goku
II UI/map text and its bounded script VM, MapEntry records, map placements,
placement types, and actor sprite graphics.

Graphics (TOOLKIT-010) cover the Buu's Fury actor sprite family: 7,355 payloads
across 295 characters decompress, decode and re-encode exactly, extract as
indexed PNGs with the ROM palette and index identity preserved, and report the
consumers a shared asset would affect. **Palette editing is the supported visual
write path** - uncompressed, fixed-size, and exactly in place. Pixel editing
decodes and re-encodes to a valid stream but is capacity-blocked for most assets,
because payloads are packed with no slack and no free space is declared;
[`docs/research/GRAPHICS_FORMAT.md`](docs/research/GRAPHICS_FORMAT.md) records
that measurement rather than an aspiration.

TOOLKIT-022 adds explicit named placement clones to projects, production-codec
serialization and proposed capacity requests. ROM materialization remains blocked
by the placement-run ownership contract, including with synthetic free space;
canonical Buu also has zero verified capacity. See
[`AUTHORED_PLACEMENTS.md`](docs/research/AUTHORED_PLACEMENTS.md) for commands,
the precise blocker and the distinction between representation and materialization.

Not implemented: materializing newly authored assets (AUTHOR_NEW), free-space
discovery, ROM expansion, relocation beyond the verified path, map tilesets and
every other graphics family, audio, gameplay, engine patches, a GUI, Tiled
integration, or remake content. Enemy-to-graphics linkage was probed across all
141 enemy records and has no static path.

See `docs/PROJECT_<local-state-name>` for the current verified baseline and
`docs/PROJECT_<local-state-name>` for the next bounded research task.
