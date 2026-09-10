# Webfoot SDK

Webfoot SDK is a safe, deterministic modding toolkit for Webfoot's three
Dragon Ball Z games on Game Boy Advance:

- *Dragon Ball Z: The Legacy of Goku*
- *Dragon Ball Z: The Legacy of Goku II*
- *Dragon Ball Z: Buu's Fury*

The SDK turns a verified local ROM into an inspectable, versionable project,
then validates and builds that project into a new ROM image. The original ROM
is always read-only.

The product goal is not a standalone remake. The acceptance target is authored
Legacy of Goku content running inside the actual Legacy of Goku II/Buu's Fury
engine. Buu's Fury currently leads the implementation because it is the primary
measurement target, but the architecture is intended for all three games.

> [!IMPORTANT]
> This is pre-release reverse-engineering software. Supported operations are
> deliberately narrower than the final goal, and unverified inputs or unsafe
> writes fail closed.

## What works today

- exact ROM identification against profile hashes and corroborating GBA header
  metadata;
- deterministic `extract`, `validate`, and `build` project lifecycle;
- byte-identical no-op rebuilds from the canonical supported input;
- attributed, transactional writes to a new output image;
- editing for verified enemy and character stats, text, and selected fixed-size
  visual data;
- lossless codecs and read-only inspection for verified map, placement, script,
  event, dialog, reference, and actor-sprite structures;
- indexed-PNG extraction for the supported Buu's Fury actor-sprite family;
- synthetic relocation proofs and explicit refusal when real free capacity or
  reference coverage has not been established.

The largest missing capability is materializing newly authored content. The
canonical Buu's Fury profile has no verified free region, so growth and broad
relocation remain blocked rather than borrowing space speculatively. Map
tilesets, most graphics families, audio, executable patches, a GUI, and a
complete LoG-to-Buu authoring path are not yet implemented.

See [project state](docs/PROJECT_<local-state-name>) for current verified facts and the
[public progress site](https://webfoot-sdk.siruiusamory.workers.dev/) for a
shorter capability overview.

## Requirements

- Windows PowerShell
- Git
- [`uv`](https://docs.astral.sh/uv/) 0.11 or newer
- Python 3.12 (installed by the setup script when needed)
- mGBA for optional runtime research and manual emulator checks

Some historical upstream experiments require additional tools, but they are not
needed to install or use the Python SDK.

## Setup

```powershell
git clone <repository-url>
cd log1-remake
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
```

The execution-policy change applies only to the current PowerShell process.
`setup.ps1` creates or repairs `.venv`, synchronizes `uv.lock`, installs the SDK
in editable mode, and verifies the pinned upstream sources. Use
`-SkipUpstreams` when only the Python project is needed.

## Quick start

Keep a legally obtained ROM under the ignored `roms\` directory or at another
local path. Do not add it to Git.

```powershell
# Verify the exact ROM profile before parsing it.
webfoot identify ".\roms\Dragon Ball Z - Buu's Fury (U).gba"

# Extract an authored project. Omit --no-graphics to include supported sprites.
webfoot extract ".\roms\Dragon Ball Z - Buu's Fury (U).gba" ".\work\my-mod" --no-graphics

# Validate without writing a ROM.
webfoot validate ".\work\my-mod" --rom ".\roms\Dragon Ball Z - Buu's Fury (U).gba"

# Build a new image. The output path must not already exist.
webfoot build ".\work\my-mod" `
  --rom ".\roms\Dragon Ball Z - Buu's Fury (U).gba" `
  --output ".\build\my-mod.gba" `
  --manifest ".\build\my-mod.json"
```

The project format stores semantic values and stable identities rather than ROM
addresses. Given the same verified base ROM, project state, and SDK version, a
build is deterministic. See the [project format](docs/project-format.md) for
the authored files, guarantees, and current editing limits.

Run `webfoot --help` or `webfoot <command> --help` for the full command tree.

## Repository map

| Path | Purpose |
| --- | --- |
| `tools/webfoot/` | Shipping SDK, codecs, project model, build system, and CLI |
| `config/roms.yaml` | Exact supported ROM profiles and measured layout data |
| `tests/` | Portable synthetic tests and opt-in local-ROM integration tests |
| `docs/` | Architecture, formats, evidence, contributor workflow, and project state |
| `tools/runtime/` | Reusable mGBA instrumentation for LoG-family research |
| `tools/ghidra/` | Static-analysis helpers used to reproduce SDK evidence |
| `src/` | Source for the public progress website |

ROMs, saves, states, dumps, extracted assets, generated ROMs, build output, and
checked-out upstream repositories are local artifacts and must remain ignored.

## Safety and legal boundary

Every write follows this path:

```text
verified base ROM -> generated working output -> patch/output ROM
```

The SDK refuses to overwrite its input or an existing output. Profile-specific
access requires exact identity, and addresses are not transferred between game
revisions without independent evidence.

This repository does not provide commercial ROMs, BIOS images, saves, states,
memory dumps, or extracted proprietary game assets. Supply only game images you
are legally entitled to use. No license has yet been selected for the project
code; do not assume redistribution rights until that release decision is made.

## Testing

```powershell
.\scripts\test.ps1
```

Portable tests use synthetic byte fixtures. Local-ROM integration tests are
opt-in and never turn ROM-derived data into committed fixtures. The full suite
is an integration gate; focused tests are preferred while iterating on a narrow
change.

## Contributing and evidence

Start with:

- [architecture](docs/architecture.md)
- [verified project state](docs/PROJECT_<local-state-name>)
- [current ticket](docs/PROJECT_<local-state-name>)
- [ticket workflow](docs/README.md)
- [reverse-engineering evidence](docs/reverse-engineering.md)

Binary claims are labelled `CONFIRMED`, `INFERRED`, or `UNKNOWN`. Round-trip
tests prove representation, not semantics; runtime and executable claims need
direct evidence. Product work should remove a concrete authoring blocker rather
than grow research infrastructure for its own sake.

Nontrivial code-bearing changes require independent review of the actual diff,
surrounding code, tests, architecture, and evidence before closure. Substantial
changes should use a feature branch and GitLab merge request through the
authenticated `glab` workflow. See the [review gate](docs/DEVELOPMENT.md) and reusable
[review template](docs/REVIEW.md).
