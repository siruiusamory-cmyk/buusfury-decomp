# Architecture

How this project is put together, and where to look for the detail.

## The goal, and the shape of the problem

The target is a single 8 MB Game Boy Advance cartridge containing ARM7TDMI code -
a little ARM, most of it Thumb - plus graphics, audio, text and compressed data.
The goal is source code that reproduces the executable part of that image.

The project is structured around one constraint: **the original compiler is not
available.** ARM Developer Suite 1.2 is commercial software, is not licensed
here, and its input sources cannot be redistributed. Byte-for-byte matching
therefore cannot be demonstrated today, and the project does not pretend
otherwise. What it can do is recover the code's structure and behaviour, prove
that behaviour against the original instructions, and keep the compiler question
strictly separate.

That produces the project's central distinction, used everywhere:

| Question | Verdict | Can it be answered today? |
| --- | --- | --- |
| Does the reconstruction behave like the original? | semantic | yes - run it and assert the results |
| Does it compile for the target and emit bytes? | modern build | yes - with a modern ARM toolchain |
| Does it reproduce the original compiler's output? | original match | no - blocked on the original compiler |

No verdict is ever inferred from another. See
[`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) for the measurements and
[`COMPILER_PROBE.md`](COMPILER_PROBE.md) for the compiler question.

## What the tooling knows about the image

Two independent models of the cartridge are maintained, and they answer different
questions:

- [`BUILD_REGIONS.md`](BUILD_REGIONS.md) - **how the build treats each byte**:
  28 regions in `config/regions.json` that tile the image exactly, classified as
  fully reproduced from source (`asset`), needing the original toolchain (`ads`),
  or copied verbatim (`incbin`).
- [`ROM_MAP.md`](ROM_MAP.md) - **what each byte is**: an independent structural
  model derived from the image itself, 249 regions, each with a confidence and
  recorded evidence. Roughly half the image resists classification, which is a
  measured property of the cartridge: the engine's Thumb data decodes at about
  94%, so a text pool or a pointer table can decode end to end exactly like code.
  The map refuses to guess rather than over-claim
  ([`ROM_MAP_PROVENANCE.md`](ROM_MAP_PROVENANCE.md)).

`config/functions.json` is a candidate function inventory for the executable
regions: entry points and instruction sets. A candidate is not proof that a
function starts there, and the entry list is a lower bound. Function *extents* for
reconstructed units come from the committed reconstruction evidence, never from
that inventory.

## The tooling

`tools/buusfury/` is a pure standard-library Python package - no third-party
dependencies - driven by a single command:

| Command | Purpose |
| --- | --- |
| `status` | every achievable gate, one summary |
| `verify` | canonical ROM identity, fails closed |
| `map`, `rommap` | the two byte models above |
| `fixed` | regenerate the toolchain-free fixed regions |
| `assets` | rebuild the asset regions and compare to the image |
| `build` | assemble an image, with per-region provenance labels |
| `lift` | the reconstruction loop: build, run, compare |
| `compiler-probe` | the search for the original compiler's settings |
| `decompdev-inventory`, `decompdev-report` | the progress figures |

Everything that reads the cartridge goes through the identity gate first and
stops on any mismatch. Nothing installs a toolchain or downloads a ROM.

## Subsystems

### Script engine

The game's dialogue, events and much of its logic run on a bytecode interpreter.
The image even preserves the original source path for it. The engine has a
dispatch loop, a primary handler table, a native handler table, a value stack and
a family of bit-array flag accessors.

Start at [`SCRIPT_VM.md`](SCRIPT_VM.md).

### Runtime-copied IWRAM code

At boot the game copies 4,100 bytes of ARM code and data from ROM into IWRAM, and
runs it from there: block memory routines, byte-lane transforms, fixed-point
maths, and the machine's interrupt entry point with its 14-entry vector table.

Start at [`IWRAM.md`](IWRAM.md).

### Small-block allocator

A Thumb heap allocator whose original translation unit is identified by a build
command preserved in the public disassembly of this game
(`tcpp -S -c -cpu ARM7TDMI -O1 src/GBARam.c`). It was the project's first
reconstruction and is the unit whose boundaries are most tightly established.
See [`LIFT_PILOT.md`](LIFT_PILOT.md).

### Assets and fixed data

Ten regions - compressed images, palettes and corners, 26,112 bytes - are rebuilt
byte-identically from source assets, which is what proves the region boundaries
are right. Three further regions are generated from data derived from the image
itself. The build classifies every byte it emits, so a passthrough can never be
mistaken for a reconstruction.

## Repository layout

| Path | Purpose |
| --- | --- |
| `src/` | reconstructed source, one file per translation unit |
| `src/probes/` | probe shims and the host self-checks |
| `include/` | shared declarations and types |
| `config/` | ROM identity, region map, function inventory, reconstruction evidence |
| `tools/buusfury/` | the tooling described above |
| `tests/` | portable tests |
| `docs/` | this documentation |
| `scripts/` | one-command entry points |
| `data/` | generated fixed regions |
| `.github/workflows/` | CI: the progress report |

## What is blocked, and why

| Blocked | Reason |
| --- | --- |
| byte-identical builds | ARM Developer Suite 1.2 is commercial and unlicensed here; see [`ADS12_SETUP.md`](ADS12_SETUP.md) |
| auditing the remaining opaque regions | the same missing toolchain for the `ads` regions, and no source for the 98% of the image that is data |
| matching the original compiler's flags | the same; [`COMPILER_PROBE.md`](COMPILER_PROBE.md) records the prepared experiment |

A documented blocker with evidence is a result. The project reports these as
blocked, with the exact command that would run them, rather than working around
them.
