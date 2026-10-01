# Building and validation

What builds here, what does not, and how to check either claim yourself.

Everything is command-driven and repeatable. No generated file is edited by hand,
and no entry point installs a toolchain or downloads a ROM.

## Requirements

| Requirement | Needed for | Status on a fresh machine |
| --- | --- | --- |
| Python 3.11+ | all analysis, comparison, test and progress tooling | required |
| Git | the repository | required |
| A legally obtained copy of the ROM | every gate that compares against the original image | required, and never tracked |
| A modern ARM cross-toolchain | compiling and linking reconstructions | optional; the gate reports BLOCKED without it |
| `grit` and a C++ build of the compression front-end | rebuilding the compressed asset regions | optional; the gate reports BLOCKED without them |
| ARM Developer Suite 1.2 | reproducing the original compiler's output | **commercial, not redistributable, and not licensed here** |

The analysis, test and progress tooling is pure standard-library Python. There is
nothing to `pip install`.

## The one-command gate

```powershell
$env:BUUSFURY_ROM = 'D:\dumps\Dragon Ball Z - Buu''s Fury (U).gba'
pwsh -File scripts/check.ps1
```

It runs every gate that can run on the machine and prints one summary. Two of the
gates depend on the unavailable commercial compiler: they report **BLOCKED**, not
FAIL, because the project's contract is that a blocker is measured and documented
rather than absent. Everything else is a real pass or fail.

`scripts/check-progress.cmd` is the narrower check that matters after a
reconstruction change: it re-derives the progress figures from committed evidence
and validates the published report. It needs no ROM.

## Individual commands

```powershell
$env:PYTHONPATH = "$PWD\tools"

python -m buusfury verify                    # ROM identity, fails closed
python -m buusfury map                       # how the build treats each byte
python -m buusfury rommap                    # what each byte is
python -m buusfury fixed                     # the toolchain-free generated regions
python -m buusfury assets                    # rebuild the asset regions and compare
python -m buusfury build                     # assemble an image, with provenance
python -m buusfury lift --target <unit>      # one reconstruction: build, run, compare
python -m buusfury doctor                    # which toolchains are present
python -m pytest tests -q                    # the portable test suite
```

`python -m buusfury build` fails closed: it rebuilds every region the map says is
reproducible and stops with a precise blocker on anything else. It never silently
copies a region it was supposed to rebuild.

`python -m buusfury build --allow-passthrough` assembles a complete image anyway
and writes a per-region provenance report labelling every byte as rebuilt or
passed through. The result is byte-identical to the cartridge, which proves the
**map** is right - it is not evidence that the source was reconstructed, and the
report says so.

## Toolchains

Paths are never hardcoded. Each tool is located through the environment or a CLI
argument:

| Variable | Tool |
| --- | --- |
| `BUUSFURY_ROM` | the cartridge image |
| `BUUSFURY_REFERENCE` | a read-only reference checkout, if you have one |
| `BUUSFURY_COMPRESS` | the compression front-end used by the asset gate |
| `DEVKITARM` | a modern ARM cross-toolchain |
| `GRIT` | the GBA graphics tool |
| `CMAKE` | CMake, for building the compression front-end |
| `ADS12_ROOT` | ARM Developer Suite 1.2, if you have a licensed copy |

Toolchain selection is authoritative: if you point the tooling at a specific
toolchain it uses that one or fails, rather than silently falling back to a
different compiler.

See [`DEPENDENCIES.md`](DEPENDENCIES.md) for details and
[`ADS12_SETUP.md`](ADS12_SETUP.md) for the commercial toolchain.

## What is blocked

| Blocked | Why |
| --- | --- |
| reproducing the original compiler's output | ARM Developer Suite 1.2 is commercial, unlicensed here, and its sources cannot be redistributed |
| rebuilding 94,016 bytes of `ads`-classed regions | same toolchain, and independent sources for those regions do not exist yet |
| auditing the regions the structural map leaves unclassified | no source; this is the object of future work |

The repository reports these as blocked, with the exact command that would run
them, and never works around them. In particular, an unlicensed installation is
reported as a licensing failure, which is a different condition from the tool
being absent.

## Continuous integration

`.github/workflows/report.yml` runs on every push to the default branch with **no
ROM, no compiler and no build output present**: it regenerates the progress
figures from committed evidence, validates them, and uploads the report that
[decomp.dev](https://decomp.dev) reads. That is also the clearest demonstration
that the reporting path depends on nothing proprietary.
