# Project rules

Permanent rules for work in this repository. They continue in
[`docs/`](docs) as noted. Read
[`docs/DECOMP_BASELINE.md`](docs/DECOMP_BASELINE.md) first for the established
baseline before changing anything.

## Goal

A **matching decompilation** of Dragon Ball Z: Buu's Fury (GBA, USA rev0): source
that a compiler turns into the canonical ROM byte for byte. The end product is a
modern mod-build that Dragonbyte Z can target.

Matching means byte-identity of the produced ROM against
`f1c4b07554d2a3b1ad2f325307051e775ce68087`. A reconstruction that merely
*resembles* the original is not a result.

## Repository isolation - mandatory

- This is a **separate repository** at `C:\Dev\buusfury-decomp`. It shares no
  history with LOG1-REMAKE / Dragonbyte Z.
- **Never modify the LOG1-REMAKE checkout**, including its `extern/` directory.
  Read from it if useful; write nothing into it.
- Do not add this project as a submodule, subtree or worktree of LOG1-REMAKE.

## ROM safety - mandatory

- The user's ROM is read-only. Never overwrite, patch, truncate or rename it.
- Every write follows: `verified base -> working copy/generated output -> output`.
- `baserom.gba`, `roms/`, `*.gba`, `*.sav`, `*.ss*` are gitignored. So is
  `build/`. Never commit ROM data, extracted ROM blobs, saves or states.
- Every entry point verifies canonical identity **before** doing anything, and
  fails closed on any mismatch. Never continue past a mismatch.
- A derivative ROM may only be produced into `build/` (gitignored) or a path the
  operator explicitly names.

## Licence discipline - mandatory

- **`2genkidev/buusfury` has NO licence.** The GitHub API reports
  `"license": null`; there is no licence file. Under default copyright that means
  all rights reserved.
  - It is fetched into `reference/` (gitignored) for **reading** and for running
    its build path only.
  - **Never copy its source, assets or data into this repository.**
  - **Never commit it**, including its ROM-derived BMPs and its prebuilt
    third-party Windows binaries.
- **ARM Developer Suite 1.2 must never be committed.** It is commercial software.
  Install it locally and point `ADS12_ROOT` at it. No ADS binary, library or
  licence file may enter version control.
- Code written for this repository is original. If a licensing question is
  genuinely unclear, stop and ask rather than assume permission.

## Evidence discipline

- Label binary-format claims `CONFIRMED`, `INFERRED` or `UNKNOWN`. A passing
  test or an upstream's field name does not promote a claim.
- Cite `file:line` for any mechanism claim. Absent evidence, say so.
- **A hash match is not a decompilation result.** Reproducing a region by copying
  it out of the baserom proves the *map*, not the *source*. Every build report
  must label which bytes were actually rebuilt, and no report may describe a
  passthrough as a reconstruction.
- Measured numbers belong in the committed config, not in prose that drifts.
  `tests/test_regions.py` locks the coverage figures so documentation cannot go
  stale silently.

## The region map is load-bearing

- `config/regions.json` must tile `[0, 0x800000)` exactly: no gaps, no overlaps.
  `tools/buusfury/regions.py` enforces this on every run.
- Changing a region's class, extent, tool or sources requires re-running the
  asset gate and updating `docs/DECOMP_BASELINE.md`. Reclassifying an `incbin`
  region as `asset` or `ads` is only honest when the rebuild has actually been
  demonstrated byte-identical.

## Build discipline

- The build must be **command-driven** and repeatable. No manually edited
  generated files.
- No machine-specific absolute paths in tracked files. Use `ADS12_ROOT`,
  `BUUSFURY_ROM`, `BUUSFURY_REFERENCE`, `BUUSFURY_COMPRESS`, `GRIT`, `CMAKE`, or
  CLI arguments.
- `scripts/check.ps1` is the one-command gate. It must stay green.
- Portable tests must never require a baserom, a reference checkout, ADS, grit or
  the JCALG1 build. Anything needing those belongs in a CLI gate.

## Scope discipline

- Execute only the current ticket; stop at its stop condition.
- Do not begin bulk decompilation, convert functions to C/C++, stand up function-analysis workers, build a Ghidra database, start m2c automation, configure
  objdiff matching, or create the modern mod-build until a ticket says to.
- A measured blocker with evidence is a valid, reportable outcome. Do not work
  around a mismatch to make a number look better.

## Git discipline

- Never run `git reset --hard`, `git clean -fd`, or any destructive command
  against user work.
- Stage explicitly by path. Never `git add -A` / `git add .` in a dirty tree.
- Before any commit: inspect status, inspect the full diff, run the tests, and
  confirm no ROM, no reference checkout and no proprietary binary is staged.
- **Do not attribute a change to tooling** to commit messages, trailers,
  branch names, merge requests or release notes. Describe the change, not the
  process that produced it.

## Documentation discipline

- `docs/DECOMP_BASELINE.md` is the entry point for a new contributor.
- `docs/VALIDATION_REPORT.md` records what was actually run and measured, with
  commands and results. Never claim a run that did not happen.
- Keep `docs/ROM_MAP.md` generated: `python -m buusfury map --write docs/ROM_MAP.md`.
