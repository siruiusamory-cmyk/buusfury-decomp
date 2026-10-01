# Documentation

This directory holds the project's technical documentation. Start with the entry
points below; the detailed per-subsystem write-ups are linked from them.

If you are new to the project, read [`ARCHITECTURE.md`](ARCHITECTURE.md) first,
then [`../CONTRIBUTING.md`](../CONTRIBUTING.md) if you want to help.

## Entry points

| Document | Read it for |
| --- | --- |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | how the project fits together: the image, the tooling, and the subsystems |
| [`PROGRESS.md`](PROGRESS.md) | what the progress figure means, and what does not count |
| [`BUILDING.md`](BUILDING.md) | toolchains, what builds, and what is blocked |
| [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | how to make a useful contribution |

## Subsystems

| Document | Subject |
| --- | --- |
| [`SCRIPT_VM.md`](SCRIPT_VM.md) | the script engine: dispatch, value stack, handlers, flags |
| [`IWRAM.md`](IWRAM.md) | the ARM code the game copies into IWRAM at boot, and its interrupt dispatch |
| [`ROM_MAP.md`](ROM_MAP.md) | generated: what every byte of the cartridge is |
| [`BUILD_REGIONS.md`](BUILD_REGIONS.md) | generated: how the build treats each byte |

## Procedure and methodology

| Document | Subject |
| --- | --- |
| [`LIFT_LOOP.md`](LIFT_LOOP.md) | the step-by-step reconstruction procedure |
| [`DECOMP_DEV.md`](DECOMP_DEV.md) | how progress is measured and published |
| [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) | what has actually been run and measured |
| [`COMPILER_PROBE.md`](COMPILER_PROBE.md) | the search for the original compiler's settings |

## Reference

| Document | Subject |
| --- | --- |
| [`DECOMP_BASELINE.md`](DECOMP_BASELINE.md) | the project's baseline: identity, map, build model, blockers |
| [`DEPENDENCIES.md`](DEPENDENCIES.md) | external tools, and what is optional |
| [`ADS12_SETUP.md`](ADS12_SETUP.md) | the commercial toolchain the matching work needs, if you have it |
| [`ROM_MAP_PROVENANCE.md`](ROM_MAP_PROVENANCE.md) | why each structural boundary is believed |
| [`REFERENCE_AUDIT.md`](REFERENCE_AUDIT.md) | the public disassembly of this game, and what may not be reused |
| [`COMPILER_PROBE_PROVENANCE.md`](COMPILER_PROBE_PROVENANCE.md) | where each compiler-probe claim comes from |

## Reconstruction write-ups

Each reconstructed unit has a write-up recording what it does, the evidence behind
it, and what is still unknown. They are grouped by subsystem in
[`SCRIPT_VM.md`](SCRIPT_VM.md) and [`IWRAM.md`](IWRAM.md), and are named
`LIFT_*.md`.

## Generated documents

`ROM_MAP.md` and `BUILD_REGIONS.md` are generated from committed evidence and
must not be edited by hand:

```powershell
python -m buusfury rommap --write config/rom_map.json --functions config/functions.json --docs docs/ROM_MAP.md
python -m buusfury map --write docs/BUILD_REGIONS.md
```
