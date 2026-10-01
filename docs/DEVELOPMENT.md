# Project rules

Development policy for this repository. Read
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the baseline before changing
anything, and [`CONTRIBUTING.md`](CONTRIBUTING.md) if you are new here. The
documentation index is [`docs/README.md`](docs/README.md).

## Goal

A **matching decompilation** of Dragon Ball Z: Buu's Fury (GBA, USA rev0): source
that a compiler turns into the canonical ROM byte for byte.

Matching means byte-identity of the produced ROM against
`f1c4b07554d2a3b1ad2f325307051e775ce68087`. A reconstruction that merely
*resembles* the original is not a result.

The original compiler is not available here, so byte-identity cannot be
demonstrated yet. What can be demonstrated - behaviour proven against the original
instructions - is tracked separately and never presented as matching.

## Repository independence

- This is a **standalone repository**. Do not add it as a submodule, subtree or
  worktree of another project, and do not link another checkout into it.
- Do not modify another checkout from here. Read from one if it is useful; write
  nothing into it.
- No tracked file may contain a machine-specific absolute path, including a path
  into another developer's checkout. `tests/test_rom_map.py` enforces this.

## ROM safety - mandatory

- The cartridge image is read-only. Never overwrite, patch, truncate or rename it.
- Every write follows `verified base -> working copy/generated output -> output`.
- `baserom.gba`, `roms/`, `*.gba`, `*.sav`, `*.ss*` are gitignored. So is
  `build/`. Never commit ROM data, extracted ROM blobs, saves or states.
- Every entry point verifies canonical identity **before** doing anything, and
  fails closed on any mismatch. Never continue past a mismatch.
- A derivative image may only be produced into `build/` (gitignored) or a path the
  operator explicitly names.

## Licence discipline - mandatory

- **`2genkidev/buusfury` has no licence.** The GitHub API reports
  `"license": null`; there is no licence file. Under default copyright that means
  all rights reserved.
  - It may be read, and its build path may be run, from a gitignored checkout.
  - **Never copy its source, assets or data into this repository.**
  - **Never commit it**, including its ROM-derived images and its prebuilt
    third-party Windows binaries.
- **ARM Developer Suite 1.2 must never be committed.** It is commercial software.
  Install it locally and point `ADS12_ROOT` at it. No ADS binary, library or
  licence file may enter version control.
- Code written for this repository is original. If a licensing question is
  genuinely unclear, stop and ask rather than assume permission.

## Evidence discipline

- Label binary-format claims `CONFIRMED`, `INFERRED` or `UNKNOWN`. A passing test
  or an upstream's field name does not promote a claim.
- Cite `file:line` for any mechanism claim. Absent evidence, say so.
- **A hash match is not a decompilation result.** Reproducing a region by copying
  it out of the baserom proves the *map*, not the *source*. Every build report must
  label which bytes were actually rebuilt, and no report may describe a
  passthrough as a reconstruction.
- Measured numbers belong in the committed config, not in prose that drifts.
  `tests/test_regions.py` locks the coverage figures, and the front-page progress
  table is generated and checked, so documentation cannot go stale silently.
- Records of what was actually run - `docs/VALIDATION_REPORT.md`,
  `docs/COMPILER_PROBE_PROVENANCE.md` - are dated evidence and are not rewritten
  to read better. Never claim a run that did not happen.

## The region map is load-bearing

- `config/regions.json` must tile `[0, 0x800000)` exactly: no gaps, no overlaps.
  `tools/buusfury/regions.py` enforces this on every run.
- Changing a region's class, extent, tool or sources requires re-running the asset
  gate and updating `docs/DECOMP_BASELINE.md`. Reclassifying an `incbin` region as
  `asset` or `ads` is only honest when the rebuild has actually been demonstrated
  byte-identical.

## Build discipline

- The build must be **command-driven** and repeatable. No manually edited
  generated files.
- No machine-specific absolute paths in tracked files. Use `ADS12_ROOT`,
  `BUUSFURY_ROM`, `BUUSFURY_REFERENCE`, `BUUSFURY_COMPRESS`, `DEVKITARM`, `GRIT`,
  `CMAKE`, or CLI arguments. Generated reports must be environment independent:
  relabel toolchain and checkout roots, and remove any remaining absolute path.
- `scripts/check.ps1` is the one-command gate. It must stay green.
- Portable tests must never require a baserom, a reference checkout, ADS, a modern
  ARM toolchain, grit or the compression front-end build. Anything needing those
  belongs in a CLI gate, and skips rather than fails when the tool is absent.

## Reconstruction rules

- Reconstruction lives in `src/<family>.c`. `src/probes/` holds only shims and
  self-checks; an implementation there is a bug.
- **One source of truth.** A probe entry point is a shim that `#include`s the real
  file. Verify it by compiling both and comparing disassembly, never by assuming.
- **Never name a function semantically.** Use `sub_<ROM address>`: the disassembly
  fixes offsets and access widths, not the names the game used. The comparison
  tooling pairs original and reconstructed functions by symbol name, so the
  convention is load bearing.
- **Run the reconstruction on the host before spending a compiler run.** A wrong
  translation unit cannot match under any compiler.
- **Three verdicts, three vocabularies, never inferred from one another:**
  `SEMANTIC` (behaviour, measured by running it), `MODERN_BUILD` (does it compile
  and emit bytes), `ADS_MATCH` (does it reproduce the original compiler). A passing
  modern build says nothing about the original compiler.
- **Never report a modern build as a match.** The comparison carries
  `is_a_match_claim: false` and a note saying so. Report the measurement; do not
  read it as agreement or as disagreement.
- **Compare at translation-unit scope, keyed on the target's instruction
  boundaries.** A function with a PC-relative literal load has no meaning
  standalone, and a positional text diff of two disassemblies can report zero
  differences for unequal bytes.
- **Derive boundaries by aligned chain-walk, and re-derive on every run.** A linear
  sweep from a region's first byte desyncs whenever that byte is not an instruction
  boundary and then silently misses real branches. It under-counted the callers of
  `0x08004038` as 2 when an aligned walk found 13. A wrong derived boundary must
  raise, not be absorbed.
- **Prove a table's extent by what follows it.** A function-pointer table has no
  length field; the dispatch table at `0x080554C0` is 31 entries because slot 30
  ends where the assertion string begins.
- **Build a 32-bit machine model 32-bit.** A reconstruction that holds pointers in
  `u32` fields must use the 32-bit host toolchain; at 64-bit every stored address
  loses its high half and faults. Record the width per target; never widen a
  typedef to silence the truncation.
- **Bind declared-not-reconstructed calls to their original addresses.** Read the
  unit's own BL targets from the ROM and declare each `sub_<address>` symbol with
  `.thumb_func` before `.set`, so call displacements stay right and no stub bytes
  enter the compared window. **Never use `--defsym`:** it creates an absolute
  symbol with no Thumb marking regardless of bit 0, so the linker wraps every
  external call in a Thumb-to-ARM interworking veneer (`bx pc` then an ARM branch,
  entering Thumb code in ARM state) and adds eight bytes per call.
- **Prove a table's extent from both sides where possible.** The native table is
  266 entries because the one-byte index needs 256 and the next table's base caps
  it; a claimed 283 was refuted by arithmetic, not by preference. An existing count
  claim is a hypothesis to re-measure, not a fact to repeat.
- **A single-byte index makes an out-of-bounds read unreachable** when the table is
  at least 256 entries. Say that as a property of the encodings, not as an absent
  check.
- **Never add validation the original lacks.** If the loop has no length limit,
  reconstruct it without one and test the unbounded behaviour. Inventing a guard
  changes the thing being reconstructed.
- **A project nickname is not a ROM fact.** If a name is not a string in the image,
  record it as a candidate alias and describe the mechanism from the instructions
  instead.
- **Cross-check every derived table against the executable test.** A group-width
  error in the derivation once made the report claim -31 where the self-check
  proved -63. Assert the two agree.
- **Reproduce artifacts, do not repair them.** When arithmetic produces a value the
  encoding "should not" give, reconstruct it exactly and record it; the binary is
  the ground truth.
- **Equal size is not a match.** The modern build of the value-stack consumer is
  the same 20 bytes and 10 instructions as the original and still differs in nine
  bytes. Never let a size coincidence read as identity; assert `byte_identical` is
  false.
- **Do not add an underflow guard.** The consumer decrements its counter with no
  test, so a zero counter walks the slot address below the context object and
  corrupts it. Reproduce that, give the host test real storage below the context so
  the walk is observable and bounded, and never write a guard.
- **A pattern scan is a lower bound.** 84 functions matched the pop idiom; a
  consumer reaching the same stack through a different register path would not
  match, so report the count as a floor.
- **When a claim rests on sibling evidence, say so.** Addition is commutative, so
  the lifted consumer cannot show operand order; the convention comes from the
  sibling's subtract, and the report names the sibling rather than asserting the
  order as if it had been observed.
- **Adding a target must not restate an earlier one.** A registry `notes` string
  feeds that target's committed report, so editing it changes the report even
  though no measurement moved. Restore the previous wording byte-for-byte and pin
  it with a test; a change that adds a family member does not own its sibling's
  prose.
- **Derive a family across units, not just within one.** The arithmetic derivation
  re-reads all three members from the ROM even though they live in two translation
  units, so the shared contract comes from the image rather than from the siblings
  being assumed alike.
- **Name context fields by offset and say what is unknown.** No opcode meaning may
  be imported from another title, and a reconstruction should contain no `switch`
  over opcodes until one is proven.
- Adding a family is a config entry plus source: `config/lift_targets.json`,
  boundaries derived in `config/compiler_probes.json` or re-derived in
  `tools/buusfury/lift.py`, tested via `tests/test_lift*.py`. No one-off scripts.
  See [`docs/LIFT_LOOP.md`](docs/LIFT_LOOP.md).

## Progress reporting

- The public progress number is **semantic reconstruction coverage**, never a
  compiler match. A function is credited only when its committed evidence proves
  its behaviour; a modern build earns nothing and the blocked original-compiler
  question costs nothing. See [`docs/PROGRESS.md`](docs/PROGRESS.md).
- **Never edit a percentage by hand.** The figures are generated from committed
  evidence, and the front-page table between the `progress` markers is generated
  too. Regenerate both with
  `python -m buusfury decompdev-report --out config/decompdev_report.json --sync-readme`;
  if the tracked set of functions changed, run `decompdev-inventory --write` in the
  same commit. The check fails when either is stale.
- **Do not delete unresolved work to raise the number.** The denominator refuses to
  shrink silently, and every unreconstructed function stays in it at zero.
- After a reconstruction change, run `scripts\check-progress.cmd`. It is a targeted
  infrastructure check, not a test suite, and it needs no ROM. Quote its line
  verbatim in the pull request: `decomp.dev: semantic code X% -> Y% (report check
  PASS)`, or `decomp.dev: unchanged (report check PASS)`.

## Scope discipline

- Do one change at a time and stop at its stop condition.
- Do not begin bulk decompilation, build a Ghidra database, start m2c automation,
  configure byte-matching comparison, or create a modern mod-build until a change
  explicitly calls for it. The semantic progress report is **not** compiler
  matching: it never claims a byte match, and the original-compiler verdict stays
  blocked.
- A measured blocker with evidence is a valid, reportable outcome. Do not work
  around a mismatch to make a number look better. In particular, never weaken the
  toolchain blocker: an unlicensed installation stays `ADS12_LICENSE_UNAVAILABLE`,
  which is a different condition from "not installed".

## Git discipline

- Never run `git reset --hard`, `git clean -fd`, or any destructive command
  against someone else's work.
- Stage explicitly by path. Never `git add -A` / `git add .` in a dirty tree.
- Before any commit: inspect status, inspect the full diff, run the focused tests,
  and confirm no ROM, no reference checkout and no proprietary binary is staged.
- **Do not attribute a change to tooling.** Describe the change, not the process
  that produced it: no tool or product names, and no generated-by trailers, in
  commit messages, branch names, pull requests or release notes.

## Documentation discipline

- [`docs/README.md`](docs/README.md) is the entry point for a new contributor;
  [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) explains the project's shape.
- `docs/VALIDATION_REPORT.md` records what was actually run and measured, with
  commands and results. Never claim a run that did not happen.
- Keep the two maps generated and distinct: `docs/BUILD_REGIONS.md` describes what
  the build does with each byte (`python -m buusfury map --write docs/BUILD_REGIONS.md`);
  `docs/ROM_MAP.md` is the independent structural model of the ROM
  (`python -m buusfury rommap --write config/rom_map.json --docs docs/ROM_MAP.md`).
  Never conflate them.
- Public documentation is written for someone who has just found the project. Keep
  research detail in `docs/`, keep the front page short, and prefer describing a
  subject to narrating how the work was organised.
