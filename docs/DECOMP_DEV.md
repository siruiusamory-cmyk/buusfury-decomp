# decomp.dev semantic progress

`INFRA-DECOMPDEV-001`. This document explains what the dashboard number means,
how it is produced, how to register the project with decomp.dev, and what every
future ticket must do so the number never needs editing by hand.

---

## 1. What the percentage means, exactly

> **This dashboard tracks semantically reconstructed original code bytes. It is
> not currently a byte-identical compiler-match percentage. Exact compiler
> matching is tracked separately and is presently blocked.**

The headline figure is

```
semantic code = original bytes of SEMANTIC PROVEN functions
                -------------------------------------------
                tracked mechanically identified executable bytes
```

and there is a second, smaller figure beside it:

```
semantic functions = SEMANTIC PROVEN functions / tracked functions
```

**A function is credited only when its committed lift report establishes
`SEMANTIC = PROVEN`.** Credit is never granted because

- a stub exists,
- the source compiles (`MODERN_BUILD = PASS`),
- a boundary is known,
- the function is mentioned in documentation,
- it has been disassembled but not reconstructed.

`ADS_MATCH = BLOCKED` is equally irrelevant in the other direction: it is the
state of every target and it neither grants nor withholds semantic credit.

### Byte weighting uses the ORIGINAL size

Credited bytes are the function's **original** byte extent, read from the lift
report's `functions[].original.size`. The modern GCC output size is recorded in
the same report and is deliberately never used: it is a different machine's
output for the same behaviour. A test pins this
(`test_original_size_is_used_and_not_the_modern_output_size`).

### What this number is not comparable to

It is not the informal "18-22% complete" project-maturity estimate. That estimate
mixed documentation, toolchain, harness and reconstruction maturity. This number
comes strictly from the mechanical denominator below and is authoritative **for
this dashboard**. It is also not comparable with a matching decomp's published
percentage, because it does not measure the same thing.

---

## 2. The denominator, and why it cannot be gamed

The denominator is the executable extent the project has already identified,
derived from committed provenance:

| source | what it contributes |
| --- | --- |
| `config/rom_map.json` | every region it classifies `code` / `code_candidate` with a known instruction set |
| `config/lift_iwramdispatch.json` | the code half of the runtime-copied IWRAM overlay, its extent and its function list |
| `config/functions.json` | **entry points and instruction sets only** |
| `config/lift_<id>.json` | each reconstructed function's original byte extent |

`config/functions.json` is used only for addresses and ISAs. Its `size` field is
`analysis.decode_run(..., limit=0x400).bytes_ok`, which overruns small functions
and overlaps its neighbours; `tools/buusfury/compiler_probe.py` already says so
in-tree. It is never used as an extent.

Within each tracked region the bytes are split between

- **function units**, one per mechanically discovered entry point, and
- **one unattributed remainder** carrying whatever is left (literal pools,
  undiscovered functions, data inside a code-classified span).

A function unit's tracked size is its committed original extent when a lift
report establishes one, and otherwise the distance to the next entry point in the
same region, clipped to that region's end. The remainder absorbs the difference,
so a region's units always sum to the region exactly.

**That is what makes the denominator stable.** Proving a function replaces an
upper-bound estimate with a measured extent and the freed bytes move into the
remainder: `total_code` cannot move as a side effect of reconstruction work. A
ticket cannot raise its percentage by removing unresolved work, and
`decompdev-inventory --write` refuses to record a smaller denominator unless it is
passed `--allow-denominator-decrease` and the change is explained in the ticket.

### What is deliberately NOT in the denominator

- Bytes the region map classifies as anything other than code. They are not
  tracked as executable work.
- The 110 candidate entry points that fall outside every tracked code region.
  They are counted in the inventory for transparency
  (`denominator.candidate_entries_outside_tracked_regions`) and contribute no
  bytes, because no extent of theirs has been classified as code.
- The overlay's 192-byte `.data` tail.

### Unattributed bytes are shown, not hidden

Roughly half of the tracked executable bytes are not yet enumerated as functions
at all. They appear as `unattributed/<region>` units in the report and in a
category whose name says so. The percentage is therefore conservative: bytes that
nobody has reconstructed cannot accidentally count as progress.

---

## 3. Local generation

No ROM, no compiler, no toolchain, no build. Everything is committed provenance.

```powershell
# the human-readable summary
python -m buusfury decompdev-report --summary

# write the artifact that decomp.dev ingests
python -m buusfury decompdev-report --out report.json

# verify everything and print the value to quote in a ticket report
python -m buusfury decompdev-report --check
```

`PYTHONPATH` must include `tools/` (as in `scripts/check.ps1`). The closeout
wrapper does that for you.

The report of record is `config/decompdev_report.json`; `--check` fails if it is
not byte-identical to a fresh generation.

### Refreshing the committed inventory

The inventory (`config/decompdev_inventory.json`) is the reviewed record of the
denominator. Regenerate it whenever reconstruction state changes:

```powershell
python -m buusfury decompdev-inventory --write
```

It is derived from committed provenance only, so it needs no ROM either.

---

## 4. CI artifact

`.github/workflows/report.yml` runs on **push to the default branch** and on
manual dispatch. It

1. checks out the repository,
2. installs nothing (the generator is pure standard-library Python),
3. refuses to run if a cartridge image is present or tracked,
4. generates and validates the report,
5. proves determinism by generating it twice and comparing, and that the file's
   first byte is `{`,
6. uploads exactly:

| artifact | file |
| --- | --- |
| `semantic_report` | `report.json` |

`semantic` is the report **version** string. decomp.dev's artifact-name rule is
the regex `^(?P<version>[A-z0-9_.\-]+)[_-]report(?:[_-].*)?$` and it displays the
captured version verbatim, so the dashboard labels this series `semantic`. Only
default-branch `push` runs are ingested; pull-request runs are not.

---

## 5. The GitHub repository

This project is published at
**<https://github.com/siruiusamory-cmyk/buusfury-decomp>**, a public repository,
with the remote named `github`:

```powershell
git remote -v
# github  https://github.com/siruiusamory-cmyk/buusfury-decomp.git (fetch)
# github  https://github.com/siruiusamory-cmyk/buusfury-decomp.git (push)

git push github main
```

decomp.dev ingests from GitHub, and only from the **default branch**, so the
report workflow must be on `main` for the dashboard to update. Pull-request runs
run the same checks but are not ingested.

No ROM, BIOS, proprietary compiler binary or extracted asset may be pushed.
`.gitignore` excludes `*.gba`, `roms/`, `baserom.gba*`, `build/` and saves; the
workflow additionally refuses to run if a cartridge image is present.

The workflow's first run on `main` produces the artifact decomp.dev reads. It can
be checked by hand in the repository's **Actions** tab: a successful
`progress report` run uploads `semantic_report` containing `report.json`.

## 5a. decomp.dev registration

Registration is a one-time action by a repository admin:

1. Sign in at <https://decomp.dev> with GitHub. You must be an **admin** of the
   repository.
2. Visit <https://decomp.dev/manage/new>, choose
   `siruiusamory-cmyk/buusfury-decomp`, and give it a game name - see the note
   below on wording - for example
   `Dragon Ball Z: Buu's Fury (Semantic Reconstruction)`.
3. Platform: **Game Boy Advance**.
4. Register. decomp.dev requires at least one completed default-branch push run
   with a parseable artifact, which the repository already has.

The dashboard headline is generated by decomp.dev as "N% decompiled" and that
label is not configurable. The levers that keep it honest are the ones this
integration uses:

- the report version `semantic`, displayed next to the series;
- every reconstructed category is named `... (semantic reconstruction)`;
- every unit is named `rom/sub_<address>` or `iwram/sub_<address>`, never a
  semantic name;
- `metadata.complete` is false everywhere, so the separate "fully linked" figure
  stays at zero instead of restating the claim in the language of linking;
- the project name and this document.

### Optional - the decomp.dev GitHub App

Once the repository is registered, install <https://github.com/apps/decomp-dev> on
the account or organisation that owns it, granting access to this repository. It
receives the `workflow_run` webhook and enqueues the refresh immediately instead
of waiting for a poll, and it is required if pull-request comments are ever
wanted. Without it decomp.dev still picks the report up on its own polling
schedule (every 30 minutes for a partial refresh, every 12 hours for a full one),
so a new report can appear up to half an hour late.

Whether the App is installed cannot be checked with an API token: GitHub refuses
user tokens on the installation endpoints. Confirm it in the repository's
**Settings → GitHub Apps**.

---

## 6. How future tickets update the dashboard

Zero manual percentage editing. When a lift ticket changes any of

- `config/lift_<id>.json` (a new or changed reconstruction verdict),
- `config/lift_targets.json` (a new registered target),
- `config/functions.json` or `config/rom_map.json` (the executable inventory),

the generator picks the change up from those files alone.

The closeout procedure for **every** ticket that changes reconstruction state is:

```powershell
python -m buusfury decompdev-inventory --write   # only if the inventory changed
scripts\check-progress.cmd
```

`scripts\check-progress.cmd` runs the targeted infrastructure check - not a test
suite - and prints the exact line to paste into the ticket report. Real example,
from the integration that landed the IWRAM transform families
(`INFRA-DECOMPDEV-INTEGRATE-001`):

```text
decomp.dev: semantic code 1.303% -> 1.670% (report check PASS)
```

or, when the ticket changed no semantic coverage:

```text
decomp.dev: unchanged (report check PASS)
```

The value is **emitted by the generator**, never calculated by hand.

If the inventory did not change, `python -m buusfury decompdev-report --check`
reports that the committed inventory is stale, which is the signal to run
`decompdev-inventory --write` and include it in the same commit.

### Regenerating over the committed report

`--out` writes the file first, so run the two together when refreshing the
artifact of record:

```powershell
python -m buusfury decompdev-report --out config/decompdev_report.json --check
```

The change line is computed from the measures the committed report had **before**
that command wrote over it, so this still reports real movement instead of
comparing the fresh document with itself.

### The line every ticket report carries

Every completed decomp ticket's final report includes exactly one line, copied
from the generator's output:

```text
decomp.dev: semantic code X% -> Y% (report check PASS)
```

A ticket that changes no semantic coverage writes:

```text
decomp.dev: unchanged (report check PASS)
```

Nothing else in the report should restate the percentage, and the number is never
typed in by hand. This is the whole of the manual effort the dashboard costs: one
line, produced by `scripts\check-progress.cmd`.

---

## 7. What the check verifies

`python -m buusfury decompdev-report --check` fails on any of:

| invariant | why it matters |
| --- | --- |
| the committed report is not byte-identical to a fresh one | the artifact of record must be the artifact |
| two generations differ | the dashboard must be reproducible |
| report version != 2 | objdiff's `Report::migrate()` **rejects** anything else |
| a field that is not in `report.proto` | objdiff's deserialiser is generated from the proto |
| a `uint64` field is not a JSON string | that is how objdiff serialises them |
| duplicate unit names or duplicate function addresses | the unit table is corrupt |
| overlapping units | two units claim the same original bytes |
| a region's units do not sum to the region | bytes were created or lost |
| aggregate measures != the sum of the units | the headline would not describe what is displayed |
| category measures != the sum of their member units | ditto, per category |
| a semantic-complete unit has no evidence, target, source or instruction count | credit without a receipt |
| a lift-report function that is not a tracked unit (orphan) | reconstruction outside the denominator |
| a registered target with no report, or a report outside the registry | the two records disagree |
| the denominator shrank | unresolved work must stay in the denominator |
| a `config/lift_*.json`, `functions.json`, `rom_map.json` or `lift_targets.json` changed since the inventory was generated | the snapshot is stale |
| an absolute local path in the artifact | artifacts are world-readable |
| any string that the generator cannot produce | a smuggled payload or a leak |
| the file does not start with `{` | objdiff would try to decode protobuf |

`scripts\check-progress.cmd` adds a second, independent generation through the
CLI and compares SHA-256 hashes, so determinism is proven end to end.

---

## 8. Validated against the upstream implementation

Beyond these tests, the committed report was parsed by the real parser:

```text
objdiff-cli v3.8.2 (windows-x86_64)
  objdiff-cli report changes config/decompdev_report.json <variant>.json
```

- the document parses as an objdiff Report version 2;
- every measure round-trips exactly (`total_code 186346`, `matched_code 3112`,
  `matched_code_percent 1.670012`, `total_functions 266`, `matched_functions 39`,
  `total_units 295`);
- objdiff names the changed unit, its function, its `metadata.demangled_name`,
  its `metadata.virtual_address` and its `progress_categories`, which proves the
  unit, item and metadata layers are decoded rather than ignored.

Re-measured after `INFRA-DECOMPDEV-INTEGRATE-001` regenerated the report from the
IWRAM transform evidence, so the figures above are the current ones. The binary
was downloaded into `build/tools/` (gitignored) for this check and is not
committed.

---

## 9. Troubleshooting a stale report

| symptom | cause | fix |
| --- | --- | --- |
| `DECOMPDEV INVENTORY: STALE` | a lift report, `functions.json`, `rom_map.json` or `lift_targets.json` changed after the inventory was generated | `python -m buusfury decompdev-inventory --write`, then commit the snapshot with the change |
| `decompdev_report.json is stale` | the report of record was not regenerated | `python -m buusfury decompdev-report --out config/decompdev_report.json` |
| `DENOMINATOR SHRANK` | unresolved work was removed from the inventory | restore it, or if the executable inventory legitimately changed, re-run with `--allow-denominator-decrease` and explain the change in the ticket |
| decomp.dev still shows the old numbers | the run was not on the default branch, or the artifact expired, or polling has not reached it yet | check the Actions tab for a successful `semantic_report` upload; without the GitHub App a refresh can take up to 30 minutes |
| the dashboard says "0% decompiled" | the report was uploaded before any function was `SEMANTIC PROVEN`, or the artifact's first byte is not `{` | run `decompdev-report --check` locally; it fails on both |
| decomp.dev crashes on the artifact | the file was not an objdiff Report version 2, or a field name is not in the proto | `decompdev-report --check` validates both |

---

## 10. Files this integration owns

| path | role |
| --- | --- |
| `tools/buusfury/decompdev.py` | inventory derivation, the objdiff Report v2 generator, and every invariant |
| `config/decompdev_inventory.json` | the committed denominator: one unit per function plus one remainder per region |
| `config/decompdev_report.json` | the committed objdiff Report v2 artifact of record |
| `.github/workflows/report.yml` | the CI job that produces and uploads `semantic_report` |
| `scripts/check-progress.cmd` / `.ps1` | the closeout check |
| `tests/test_decompdev.py` | the focused tests for all of the above |
| `docs/DECOMP_DEV.md` | this document |

Nothing here reads the cartridge, and nothing here can publish its contents.
