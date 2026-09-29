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
  `BUUSFURY_ROM`, `BUUSFURY_REFERENCE`, `BUUSFURY_COMPRESS`, `DEVKITARM`, `GRIT`,
  `CMAKE`, or CLI arguments. Generated reports must be environment independent:
  relabel toolchain and checkout roots, and scrub any remaining absolute path.
- `scripts/check.ps1` is the one-command gate. It must stay green.
- Portable tests must never require a baserom, a reference checkout, ADS, a modern
  ARM toolchain, grit or the JCALG1 build. Anything needing those belongs in a CLI
  gate, and skips rather than fails when the tool is absent.

## The lifting loop

- Reconstruction lives in `src/<family>.c`. `src/probes/` holds only shims and
  self-checks; an implementation there is a bug.
- **One source of truth.** A probe entry point is a shim that `#include`s the real
  file. Verify it by compiling both and comparing disassembly, never by assuming.
- **Never name a function semantically.** Use `sub_<ROM address>`: the disassembly
  fixes offsets and access widths, not the names the game used. The lift harness
  pairs original and modern functions by symbol name, so the convention is load
  bearing.
- **Run the reconstruction on the host before spending a compiler run.** A wrong
  translation unit cannot match under any compiler.
- **Three verdicts, three vocabularies, never inferred from one another:**
  `SEMANTIC` (behaviour, measured by running it), `MODERN_BUILD` (does it compile
  and emit bytes), `ADS_MATCH` (does it reproduce the original compiler). A passing
  modern build says nothing about ADS 1.2.
- **Never report a modern build as a match.** The comparison carries
  `is_a_match_claim: false` and a note saying so. Report the measurement; do not
  read it as agreement or as disagreement.
- **Compare at translation-unit scope, keyed on the target's instruction
  boundaries.** A function with a PC-relative literal load has no meaning
  standalone, and a positional text diff of two disassemblies can report zero
  differences for unequal bytes.
- **Derive boundaries by aligned chain-walk, and re-derive on every run.** A
  linear sweep from a region's first byte desyncs whenever that byte is not an
  instruction boundary and then silently misses real branches. It under-counted
  the callers of `0x08004038` as 2 when an aligned walk found 13. A wrong
  derived boundary must raise, not be absorbed.
- **Prove a table's extent by what follows it.** A function-pointer table has no
  length field; the dispatch table at `0x080554C0` is 31 entries because slot 30
  ends where the assertion string begins.
- **Build a 32-bit machine model 32-bit.** A reconstruction that holds pointers
  in `u32` fields must use the 32-bit host toolchain; at 64-bit every stored
  address loses its high half and faults. Record the width per target; never
  widen a typedef to silence the truncation.
- **Bind declared-not-reconstructed calls to their original addresses.** Read
  the unit's own BL targets from the ROM and `--defsym` each `sub_<address>`
  symbol, so call displacements stay right and no stub bytes enter the compared
  window.
- **Name context fields by offset and say what is unknown.** No opcode meaning
  may be imported from another LoG title, and a reconstruction should contain no
  `switch` over opcodes until one is proven.
- Adding a family is a config entry plus source: `config/lift_targets.json`,
  boundaries derived in `config/compiler_probes.json` or re-derived in
  `tools/buusfury/lift.py`, tested via `tests/test_lift*.py`. No one-off
  scripts. See [`docs/LIFT_LOOP.md`](docs/LIFT_LOOP.md).

## Scope discipline

- Execute only the current ticket; stop at its stop condition.
- Do not begin bulk decompilation, stand up function-analysis workers, build a Ghidra
  database, start m2c automation, configure objdiff matching, or create the modern
  mod-build until a ticket says to.
- A measured blocker with evidence is a valid, reportable outcome. Do not work
  around a mismatch to make a number look better. In particular, never weaken the
  ADS blocker: an unlicensed installation stays `ADS12_LICENSE_UNAVAILABLE`, which
  is a different condition from "not installed".

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
- Keep the two maps generated and distinct: `docs/BUILD_REGIONS.md` describes what
  the build does with each byte (`python -m buusfury map --write docs/BUILD_REGIONS.md`);
  `docs/ROM_MAP.md` is the independent structural model of the ROM
  (`python -m buusfury rommap --docs docs/ROM_MAP.md`). Never conflate them.
