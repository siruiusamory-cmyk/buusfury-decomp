# Contributing

Thanks for wanting to help. This project reconstructs the executable code of
*Dragon Ball Z: Buu's Fury* (GBA, USA rev0) as readable source, and there is more
to do than any one person can get through.

You do not need to know anything about how the project is organised internally to
contribute. Pick something from the list below, follow the evidence rules, and
open a pull request.

## Ground rules

Two rules matter more than any others.

1. **Never commit game data.** The ROM, extracted graphics, audio, text, level
   data and anything else derived from the cartridge must not enter the
   repository. `.gitignore` covers the obvious cases, but the rule is the point,
   not the file patterns.
2. **Never claim a match you cannot demonstrate.** Reconstructed source is
   credited only when its behaviour has been proven against the original code. A
   reconstruction that compiles, or that looks right, or that has the same size,
   is not yet a result.

Two more that follow from those:

3. **Prefer evidence to assertion.** Every non-obvious claim should cite
   something checkable: an address, an instruction, a measurement, a test.
4. **Label what you do not know.** `confirmed`, `inferred` and `unknown` are all
   useful outcomes. Silence about a gap is not.

## Ways to contribute

| Kind of work | What it looks like |
| --- | --- |
| Reconstruct a function | write it in `src/`, prove its behaviour with a host self-check |
| Verify existing work | re-derive a boundary, improve a self-check, attack a claim |
| Extend the map | identify a region of the image the structural map leaves as `unknown` |
| Tooling | analysis, comparison, reporting, or build improvements in `tools/` |
| Documentation | explain a subsystem, or fix something that has drifted |

If you are unsure where to start, open an issue describing what you are
interested in and what evidence you have found.

## Setting up

```powershell
git clone https://github.com/siruiusamory-cmyk/buusfury-decomp
cd buusfury-decomp
$env:BUUSFURY_ROM = 'D:\dumps\Dragon Ball Z - Buu''s Fury (U).gba'
pwsh -File scripts/check.ps1
```

Python 3.11+ and Git are the only requirements for the analysis, test and
progress tooling: it is pure standard-library Python. Some gates need toolchains
that may not be present on your machine (an ARM cross-compiler, the original
commercial compiler, `grit`). Those gates report **BLOCKED** rather than failing,
and nothing in the repository installs anything for you.

You need your own legally obtained copy of the game to run the gates that compare
against the original image. Nothing else requires it.

## Picking a function

Good candidates share a few properties:

- their boundaries are already established, so you are not guessing where the
  function starts and ends;
- they are leaf functions, or call only functions that are already understood;
- their behaviour can be exercised on the host without an emulator.

The structural map (`docs/ROM_MAP.md`, generated) and the function inventory
(`config/functions.json`) show what has been identified. `config/lift_targets.json`
lists what has already been reconstructed, so you can see what is left and what
pattern the existing work follows.

Do not start from a name. If you do not know what a function is called, that is
normal and fine - the convention is to call it `sub_<address>`.

## The reconstruction procedure

The full procedure is in [`docs/LIFT_LOOP.md`](docs/LIFT_LOOP.md). In outline:

1. **Derive the boundaries from the image.** Never write function start and end
   addresses by hand. If the existing evidence does not establish them, deriving
   them is part of the work.
2. **Read the original instructions.** Record, from the machine code, what the
   function actually does: access widths, offsets, call targets, return shape.
3. **Write the C in `src/<family>.c`.** Name each function `sub_<address>`. Do not
   invent semantic names, and do not import meaning from another game.
4. **Prove the behaviour by running it.** Add a host self-check that compiles the
   reconstruction for your machine, executes it, and asserts the results -
   including the awkward cases: zero sizes, negative values, unbounded loops,
   underflow. Reproduce the original's behaviour, including behaviour that looks
   like a bug. Do not add guards the original does not have.
5. **Build it with a modern ARM toolchain.** This shows the source is real,
   buildable C for the target. It is a separate question from whether the
   original compiler would have produced the same bytes, and it never counts as a
   match.
6. **Record the evidence** in the committed report for that unit, and add focused
   tests.

If the unit calls code it does not contain, its calls are bound to the original
addresses rather than replaced with stubs, so that no extra bytes enter the
comparison.

## Evidence standard

Three questions are asked of every reconstruction, and the answer to one is never
used as the answer to another:

| Verdict | Question | Status |
| --- | --- | --- |
| semantic | does it behave like the original? | provable today, by running it |
| modern build | does it compile and emit bytes? | a modern ARM toolchain |
| original match | does it reproduce the original compiler? | blocked: needs the original compiler |

Report each separately. A passing modern build says nothing about the original
compiler; a passing behavioural run only removes one class of error. When
something cannot be checked, say so and record the exact command that would check
it.

## Source style

- One file per translation unit in `src/`; `src/probes/` holds only a shim that
  includes it plus the self-check, never an implementation.
- `sub_<address>` naming, always. The comparison tooling pairs original and
  reconstructed functions by symbol name.
- A short header comment per file: what the unit is, what the surviving evidence
  says about it, and what is unknown.
- Match the original's machine model. A unit that holds addresses in 32-bit
  fields must be built 32-bit; do not widen types to silence a warning.
- Reproduce what the code does, not what it should have done. If the original
  loop has no bounds check, the reconstruction has no bounds check either - and
  the self-check should demonstrate the consequence.

## Focused validation

Run the checks that cover what you changed, not the whole suite:

```powershell
$env:PYTHONPATH = "$PWD\tools"
python -m pytest tests/test_lift_<your_unit>.py tests/test_lift.py -q
scripts\check-progress.cmd
```

`scripts\check-progress.cmd` is the one project-wide check that matters for a
reconstruction change: it re-derives the progress figure from committed evidence
and verifies the published report. It needs no ROM.

## Progress regeneration

The progress figure and the table on the front page are generated. Never edit a
percentage by hand. After your change:

```powershell
python -m buusfury decompdev-inventory --write     # the denominator changed
python -m buusfury decompdev-report --out config/decompdev_report.json --sync-readme
scripts\check-progress.cmd                         # must pass
```

See [`docs/PROGRESS.md`](docs/PROGRESS.md) for what the figure means and
[`docs/DECOMP_DEV.md`](docs/DECOMP_DEV.md) for how it is published.

## Pull requests

A good pull request is focused: one family, or one clear fix. It should say

- what you reconstructed or changed, and for which addresses;
- what evidence backs it - instructions read, measurements taken;
- which checks you ran and what they printed;
- what remains unknown or unverified.

If a change cannot be validated on your machine because a toolchain is missing,
say so. A documented blocker is a valid outcome; an unverified claim is not.

## Legal

You must own the game. Do not submit or request ROMs, extracted assets,
disassembly of retail assets, or material from any proprietary toolchain. Code
and documentation you contribute must be your own work; do not copy from another
project's source, including any public disassembly of this or another game. Facts
and addresses read out of the image are not copyrightable; someone else's
expression is.
