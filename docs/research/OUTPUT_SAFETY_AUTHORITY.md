# CQA-01-OUTPUT-SAFETY-001 - shared output-safety authority and graphics export data-loss fix

STATUS: **IMPLEMENTATION COMPLETE, FOCUSED VALIDATION GREEN, FROZEN FOR
INDEPENDENT REVIEW.** Not merged.

Ticket class: CRITICAL REMEDIATION. Primary finding **CQA-01 [CRITICAL]**, with
only the output-safety ownership needed to close it durably from **CQA-10
[MEDIUM]**.

## Baseline

| Fact | Value |
| --- | --- |
| Repository authority | `origin/master` |
| START SHA | `d96796eb8c59f2fce664afce387f96893059c6aa` |
| Worktree | `<temp>\log1-remake-cqa-01-output-safety-001` (detached at START SHA) |
| Dirty `workbench-006` checkout | **not** read as the baseline and **not** touched |

The working `<checkout>` checkout is on `workbench-006` (`b4b13c9`) with
89 files of pure CRLF-vs-LF ending churn against its own `HEAD`. That is
pre-existing unrelated local state; per [`../line-endings.md`](../line-endings.md)
it was reported rather than committed or "fixed", and all ticket work moved to a
clean detached worktree at the START SHA.

## 1. The defect, reproduced before any code changed (RED)

The audit's phrasing named `--rom`, which the command does not have: the ROM is a
positional argument. The real invocation is
`webfoot graphics export <rom> <identity> --out <path>`, and that is what was
driven.

**CLI.** Probe `<temp>\cqa01-probe\probe_cli_export_alias.py` calls the real
`main()` with one synthetic 8,192-byte image named as both the ROM and `--out`,
with only the read-only `load_actor_sprites` call stubbed (a synthetic profile
can never pass `capability.require`, which re-checks extents against the
*packaged* catalogue - the same limitation the audit's own probe recorded).

| | before | after |
| --- | --- | --- |
| size | 8,192 | 864 |
| SHA-256 | `d47eca594d9e2705af0b16cac052e2d169100aaaa3769188245d2d6c6a815131` | `d8cb7f9d5b6ce7a954e1da0e4bcf5f660a7af05e01a12513c952ca1a82ff9a48` |
| head | `00000000` | `89504e470d0a1a0a` (PNG signature) |
| result | - | `exit code 0`, result JSON printed the clobbered path |

**Workbench.** Probe `<temp>\cqa01-probe\probe_workbench_export_alias.py` drives
the real `GraphicsTab._on_export` slot with the open ROM's own path chosen in the
save dialog. A synthetic 2,048-byte file became an 864-byte PNG, `QMessageBox`
list was **empty**, and the status line read
`Exported sprite 0 to ...\open_rom.gba` - a silent destructive success.

**Affected call paths, exactly:**

- `tools/webfoot/cli.py:1543-1555` (`_run_graphics`, `elif command == "export":`,
  write at `:1554`).
- `tools/webfoot/workbench/graphics_tab.py:930-956` (`GraphicsTab._on_export`,
  write at `:952`).

Neither path contained any source-alias predicate. Canonical ROM safety: no
reproduction touched the canonical image; every destructive run used a synthetic
file inside the probe's own scratch directory.

## 2. One shared SDK output-safety authority

Ownership is `tools/webfoot/write.py`, which already owned the equivalent rule for
ROM writers (`emit_image`) and is named the owner by the audit's own CQA-10
remediation note. It is now explicit:

| Name | Role |
| --- | --- |
| `write.paths_are_the_same_file(source, destination)` | The rule: does this destination denote the same file as this source? |
| `write.ensure_not_source_alias(source, destination)` | The **source-alias safety** policy. Raises `OutputPathError`. |
| `write.ensure_new_destination(destination)` | The **overwrite** policy. Raises `OutputPathError`. Separate on purpose. |
| `write.OutputPathError` | `WriteError` (and therefore `ValueError`), so every existing CLI and GUI boundary already reports it. |

Filesystem awareness is two halves, because neither alone is sufficient:

- `os.path.samefile` compares the operating system's own file identity (device +
  inode on POSIX; volume serial + file index on Windows). This is the **only**
  comparison that catches a **hard link**, where two genuinely different names
  share one file and no path normalisation can help.
- `resolve()` + `normcase()` handles the case where the destination does not
  exist yet - the ordinary export - folding relative spellings, `.`/`..`,
  junctions and symlinks in existing components, and on Windows case and
  separator variation.

Both existing proven alias implementations are now routed through it rather than
keeping private comparisons: `emit_image` (was `source.resolve() ==
destination.resolve()` plus `destination.exists()`, and missed a hard-link alias
of its own input), and `workbench/build_panel.is_safe_output_path` (was a second
`resolve()` comparison of the same rule, deliberately not delegated; it is now a
named GUI-facing wrapper over `paths_are_the_same_file`, so `build_panel` and
`map_browser_tab` inherit the stronger rule).

**No architecture expansion.** `write.py` was not rewritten; no writer was
replaced; `emit_image`, `emit_plan`, the staged-publish primitive and
`authored_image` are otherwise untouched. `authored_image.refuse_source_alias`
was left alone: it is a *multi-path* refusal for a transaction that also derives
and stages paths, not a re-derivation of single-destination identity.

## 3. The two callers

- **CLI** (`cli.py`): `ensure_not_source_alias(args.rom, Path(args.out))` runs
  **before** `out.parent.mkdir(...)` and before `out.write_bytes(...)`. An unsafe
  `--out` now exits non-zero (`2`) with the reason on stderr and the source
  untouched. The encode no longer runs either, because the refusal precedes it.
- **Workbench** (`graphics_tab.py`): a thin `_refuse_source_alias(path)` wrapper
  supplies `session.rom_path` to the same SDK rule and nothing else; the slot's
  existing `_SDK_ERRORS + OSError` boundary now includes `OutputPathError`, so the
  refusal becomes the established `QMessageBox.critical` with the status line
  left alone - no dead click, no traceback. A safe distinct PNG export is
  unchanged.

## 4. Bounded caller audit (the CQA-01 defect class)

Search over every direct write site in `tools/webfoot/**` (`write_bytes`,
`open("w")`, `write_text`, `os.replace`, `shutil.copy`) for an exporter that
accepts **both** an input/source path and a caller-selected output path:

| Candidate | Verdict |
| --- | --- |
| `cli.py` `graphics export --out` | **CQA-01 path - now guarded.** |
| `graphics_tab.py` PNG export | **CQA-01 path - now guarded.** |
| ROM writers (`stats set`, `text set`, `build`, `relocate`, `atlas build`) | All route through `write.emit_image`, already guarded. |
| `atlas_build.write_atlas` / `write_conflicts` | Non-atomic in-place truncation to a caller path, but **no source ROM argument** and no ROM overwrite: they cannot alias the verified input because the input is never a parameter. Recorded follow-up **CQA-13**, untouched. |
| `build._extract_graphics`, graphics-manifest writes | Destinations are constructed inside the project directory from fixed relative names, not caller-selected. |
| `project/**`, `atlas_producers/**`, `workbench/settings.py` | Project/settings documents, not ROM-scoped artefacts. |

**No other immediately equivalent CQA-01 path exists.** Scope was not widened;
the audit's other output-policy findings (atlas atomic publication, export
directory policy, overwrite-policy unification, repository-output rules, the
remaining ~24 write sites) were left for their own tickets.

## 5. Tests

- `tests/unit/test_output_safety.py` (**new**, 18 tests, `writer` gate): the
  predicate and both policies. Identical path; relative-resolved spelling;
  case/separator variation asserted against the *platform's own* answer (not a
  lowercased comparison); distinct path; non-existent destination; **hard-link
  alias**; **file symlink alias**; **directory symlink/junction alias**;
  both-policies-independent; every refusal is a `WriteError`; and an
  anti-regression pin that `emit_image` itself refuses a hard-link alias of its
  input (a re-introduced `resolve() == resolve()` fails it). Each alias form
  **skips explicitly, naming what the host could not provide** - none degrades
  into a weaker passing assertion. No canonical ROM, no ROM bytes: all synthetic,
  all inside `tmp_path`.
- `tests/unit/test_graphics_cli.py` (+3 tests): the real `main()` argument
  vector, asserting non-zero exit, the refusal text, **source byte-identical by
  SHA-256**, no PNG replacement and no success document; a relative spelling of
  the same input; and a positive control that a distinct destination still
  produces a decodable 2x2 PNG and creates its parent directory.
- `tests/unit/test_workbench_graphics.py` (+5 tests): the real
  `GraphicsTab._on_export` slot through the real dialog seam. Refusal of the open
  ROM, of an equivalent spelling, and of a **hard-link alias** (visible message,
  source byte-identical, no PNG bytes); a positive control that a distinct
  destination writes a valid PNG, leaves the ROM unchanged and reports in the
  status line; and a no-ROM-open control proving the guard is a no-op before a ROM
  is chosen.
- `tests/helpers.py` gained a synthetic sprite-declaring ROM, its `tables`
  mapping and a shared catalog writer - the fixture the CLI export tests need,
  because a synthetic profile can never satisfy the packaged-catalogue check.
- `tests/integration/test_graphics_rom.py` (+2 ROM-gated tests) closes the one
  gap the portable tests necessarily leave: they stub the corpus load, so these
  run the **whole** path against the canonical image - the real
  `load_actor_sprites`, the real identity parse, the real encoder. One asserts
  the canonical ROM named as its own `--out` is refused (`read-only` on stderr,
  exit non-zero, SHA-256 unchanged); the other is the positive control that a
  safe destination still produces a PNG whose decoded pixels and dimensions
  equal the source graphic, with the ROM hash unchanged. Read-only: the refusal
  never writes and the safe case writes only into `tmp_path`.

## 6. Mutation check

Two temporary, bounded mutations in an **isolated scratch worktree**
(`<temp>\dsh-cqa01-mutation`), never in the ticket worktree, each reverted
byte-for-byte and SHA-verified afterwards.

| Mutation | Result |
| --- | --- |
| **M1** `cli.py` export branch calls `out.write_bytes(blob)` without `ensure_not_source_alias(args.rom, out)` | **detected** - `test_export_refuses_to_write_over_its_own_input_rom`, `test_export_refuses_a_relative_spelling_of_the_input_rom` fail (2 failed / 77 passed / 1 skipped) |
| **M2** `graphics_tab._refuse_source_alias` returns immediately | **detected** - 3 Workbench refusal tests fail, including the hard-link case (3 failed / 76 passed / 1 skipped) |

Both paths are covered by tests that exercise the real command/slot, not the
helper in isolation. Sensitivity in depth: `tests/integration/test_graphics_rom.py`
covers the same CLI branch with the **real** corpus load against the canonical
image, so the M1 bypass would be caught on the real path as well - a guard that
only worked under the stubbed corpus could not pass both.

## 7. Existing-destination semantics (recorded, deliberately unchanged)

Measured after the fix, on the same synthetic profile:

- `graphics export --out <existing file>` **silently replaces** it - a
  20-byte pre-existing file became an 864-byte PNG, `exit 0`.
- `GraphicsTab._on_export` likewise overwrites whatever the save dialog returns
  (that is how the CQA-01 reproduction clobbered the ROM in the first place).
- The ROM writers **refuse** an existing destination (`emit_image`, and the
  `--output ... (must not exist)` help text on every ROM-writing command).

CLI and GUI agree with each other and differ from the ROM writers. This ticket
does **not** change it: `ensure_new_destination` exists, is tested, and is
deliberately **not** applied to the PNG export. Changing that would be a
behaviour change belonging to the overwrite-policy finding, and the required
invariant here - *the source can never be the destination or an alias of it* - is
enforced either way.

## 8. Canonical ROM safety

`<checkout>\roms\Dragon Ball Z - Buu's Fury (U).gba`, **read only**:

```text
sha256 before : 940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e
sha256 after  : 940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e
```

Positive safety validation (`<temp>\cqa01-probe\canonical_positive.py`) confirms
the shared rule recognises the canonical ROM, a case-varied spelling, a relative
spelling, a **symlink alias** and a **hard-link alias**, refuses each, accepts a
distinct destination, and leaves the ROM byte-identical. The destructive
reproductions used synthetic files only.

## 9. Finding closure

### CQA-01: **CLOSED**

Both destructive call paths refuse before any write, the source stays
byte-identical, the CLI reports non-zero with a readable reason, the GUI reports
visibly rather than silently, safe exports still work, tests drive the real paths
and are sensitive to the guard's removal, and no other equivalent path exists.

### CQA-10: **PARTIAL / IMPROVED**

Resolved by this ticket: the **source-alias invariant now has one SDK owner**
(`write.py`), and the two writers that had no policy at all
(`cli.py:1554`, `graphics_tab.py:952`) now apply it; the deliberate GUI duplicate
`build_panel.is_safe_output_path` no longer re-derives the rule.

Still open, and **not** addressed here:

- **Overwrite-policy divergence** between writers (refuse / silent replace /
  delete-then-rebuild) - CQA-11, plus the PNG-export behaviour recorded in
  section 7 above.
- **Repository/raw-input-root output policy**: the exporters under
  `tools/export/**` keep their own "outside a git work tree" rule, still not
  shared with the ROM writers, and the eight near-identical copied helpers
  (`sha256_bytes`, `is_repository_root`, `find_repository_root`,
  `ensure_outside_repository`, `audit_root_for`, `_has_files`,
  `_empty_directory`, `clear_generated`) are unchanged.
- **Atomic publication for the atlas** (`atlas_build.write_atlas` truncates in
  place) - CQA-13.
- `.gitignore` coverage for stray exported `*.png` / provenance manifests.
- The remaining unguarded write sites across the wider repository.

## 10. Scope boundaries observed

CQA-02 was not started. No allocation/expansion work. No `write.py` rewrite, no
`emit_image` replacement, no `authored_image` redesign, no generalized VFS, no
exporter-wide refactor. CQA-11, CQA-13 and the repository-output policy were
recorded, not fixed. WORKBENCH-006 was not touched: its branch, worktree and
uncommitted state are exactly as found.

## 11. Focused validation

Measured in the ticket worktree (`<temp>\log1-remake-cqa-01-output-safety-001`),
with the canonical image reachable through an untracked `roms` junction pointing
at the read-only main-checkout copy.

| Scope | Result |
| --- | --- |
| `pytest tests/unit -m fast` (portable gate), canonical image reachable | **2244 passed, 10 skipped** (171s) |
| `pytest tests/unit -m fast`, before the junction above | **2242 passed, 12 skipped** (207s) |
| `pytest tests/unit -m writer` | **461 passed** |
| `pytest tests/unit -m workbench` | **176 passed, 5 skipped** |
| New shared-rule file `tests/unit/test_output_safety.py` | **18 passed** |
| `tests/unit/test_graphics_cli.py` | **13 passed** |
| `tests/unit/test_workbench_graphics.py` | **44 passed, 1 skipped** |
| `tests/unit/test_build_panel_guard.py` | **4 passed** |
| Existing project/ROM/asset-export safety files | **72 passed**, 41 skipped (ROM-gated, no image in that run) |
| ROM-gated `test_stat_write_rom.py`, `test_cross_profile_invariants.py` against the canonical image | **42 passed** |
| ROM-gated `test_graphics_rom.py -k export_refuses_the_canonical or export_writes_a_real_png` | **2 passed** |
| `python -m compileall` on every touched Python file | clean |
| `git diff --check` | clean |

The two fast-gate counts differ only in what the environment exposed: with the
read-only `roms` junction present, two previously-skipped Workbench tests ran
against the canonical image (they need the assembled `atlas.jsonl`, which only
exists beside that image). Nothing was collected or skipped differently by the
ticket's own change.

The skips are all environmental and named in the output (no canonical image on
that path, no assembled `atlas.jsonl`, no site build, `capstone`). No test was
deleted, relaxed or skipped to reach a green result.

**This run caught a real regression and it was fixed, not waived:** three
existing ROM-gated tests (`test_emit_refuses_to_write_over_the_input`,
`test_a_build_refuses_to_overwrite_the_base_rom[buus_fury]`,
`...[legacy_of_goku_ii]`) match on the *wording* of `emit_image`'s refusal
(`"read-only"`, `"over the input image"`). Consolidating that guard into the
shared policy rewrote the message and broke all three. Rather than weaken those
assertions, the shared policy now emits a message carrying **both** the original
phrasing and the new consequence text, so every prior regression assertion still
matches. This is why the ROM-gated suite was run at all: a `-m fast` gate cannot
see it.

No manual full-suite run: the change is a guarded boundary plus tests; the blast
radius is bounded by the `writer` gate, the `workbench` gate and the fast
portable gate, and `docs/DEVELOPMENT.md`'s evidence-proportional policy makes a manual
15+ minute integration run unnecessary here. CI runs the portable suite after MR
creation.

## 12. Independent review

See the final report for the reviewer verdict and any findings.

## Stop

Do not merge. Return for integration/closeout. The next remediation after this
ticket is **CQA-02 PACKED-STREAM TERMINATION EVIDENCE RESOLUTION**.
