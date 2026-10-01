# Progress

What the progress figure means, how it is produced, and what it deliberately does
not count.

The live figure is published on
[decomp.dev](https://decomp.dev/siruiusamory-cmyk/buusfury-decomp). The generated
table on the front page and that dashboard are produced from the same committed
evidence by the same command, so they cannot disagree.

## The two figures

| Figure | Meaning |
| --- | --- |
| Semantically reconstructed functions | reconstructed functions whose behaviour has been proven, over the functions the project tracks |
| Reconstructed executable bytes | the **original** byte size of those functions, over the executable bytes the project tracks |

Byte weighting uses the function's original size in the cartridge - the bytes that
are actually being reproduced - not the size of the output produced by a modern
compiler from the reconstruction.

## What earns credit

A function is credited when its committed reconstruction evidence establishes
that its behaviour has been **proven** against the original instructions: the
reconstruction was executed and its results asserted, including the awkward
cases.

Credit is never granted because:

- a function has been identified, or its boundaries are known;
- a placeholder or stub exists;
- the source compiles, or a modern toolchain emits bytes for it;
- the function is described in documentation;
- the original-compiler question is unanswered.

The original-compiler question is separate and currently blocked. That is why the
published dashboard shows a figure for semantic coverage and **no** figure for
fully-matched, byte-identical output: the second number is honestly zero and the
project does not restate the first number as if it meant the second.

## The denominator

Progress is measured against the executable bytes the project has been able to
identify, not against the whole 8 MB cartridge. The denominator is derived from
committed evidence:

- every region of the structural image map classified as code or a code
  candidate, plus
- the code half of the block the game copies into IWRAM at boot.

Within each region, the bytes are divided between the functions the project has
enumerated and a single unattributed remainder, so a region's parts always add up
to the region. A function's tracked size is its committed original size when the
reconstruction establishes one, and otherwise a bound derived from its
neighbours.

This has a deliberate consequence: **proving more work never shrinks the
denominator.** Replacing a bound with a measured extent moves bytes into the
remainder instead of removing them, so the percentage can only move because real
progress was made - never because unresolved work was deleted. The same guard
refuses to record a smaller denominator without an explicit, reviewed change.

## Why the figure looks small

It is conservative on purpose:

- every function that has not been reconstructed, including those nobody has even
  enumerated yet, stays in the denominator at zero;
- bytes that the map identifies as executable but that have not been attributed
  to a function are counted, and shown separately;
- no partial credit is given for a reconstruction that is not proven.

The figure is therefore a floor on understanding, not an estimate of effort, and
it is not comparable with a byte-matching decompilation project's percentage,
because it does not measure the same thing.

## Regenerating it

The figures are generated. Never edit a percentage by hand.

```powershell
python -m buusfury decompdev-report --summary          # what the dashboard shows
python -m buusfury decompdev-report --check            # verify everything
python -m buusfury decompdev-report --out config/decompdev_report.json --sync-readme
python -m buusfury decompdev-inventory --write         # when the denominator changed
```

None of these needs the ROM, a compiler or a build. `--check` fails if the
committed report or the front-page table is stale, if any invariant is broken, or
if the generator stops being reproducible.

## Where it is published

The figure is uploaded from CI as an artifact that
[decomp.dev](https://decomp.dev) reads, and it is checked against the committed
report on every push. See [`DECOMP_DEV.md`](DECOMP_DEV.md) for the mechanism and
for what the dashboard's own wording does and does not claim.
