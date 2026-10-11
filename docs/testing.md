# Testing: focused validation gates

`docs/DEVELOPMENT.md` states the policy: the full suite is an expensive
integration gate (about 90 minutes here), never an iterative loop and never a
reflex after a fix. This file is the operational half of that rule: how to run
the *small* scope that validates a change, by name, without reconstructing a
path list from memory.

Every test carries at least one gate. The gates are assigned from a single
registry, [`tests/gates.py`](../tests/gates.py), applied to the collection by
[`tests/conftest.py`](../tests/conftest.py), and checked against the pytest
marker registry by `tests/unit/test_test_gates.py`.

## The gates

| gate | selects | collected | needs |
|---|---|---|---|
| `fast` | `tests/unit`, the portable suite | 4,337 | nothing beyond the dev extra, except the six members listed below |
| `rom` | `tests/integration`, the ROM-gated suite | 1,503 | a canonical local ROM image |
| `workbench` | DragonByte Z UI, session and editor regressions | 611 | PySide6 (skips without it; must not skip in CI) |
| `writer` | authored images, provenance, allocation and output safety | 1,306 | nothing extra |
| `map` | map reading, placement, rendering and layout | 1,251 | a ROM for its integration members |
| `research` | research and runtime tooling (atlas, mGBA, logx, disassembly) | 1,119 | a ROM for its integration members |

`fast` and `rom` are the axis: every test is in exactly one of them, decided by
which directory it lives in, and the two collected counts sum to the whole tree.
The four subsystem gates cut across that axis, so a map-layout write test is
`rom`, `map` *and* `writer` at once. Counts above are what the collection
reported on 2026-10-08 in this checkout; they move as tests are added, and they
are not a maintained fact.

## Running a gate

The whole of each gate, on its own:

```bash
python -m pytest -m fast          # the portable suite; about 7 minutes here
python -m pytest -m workbench     # DragonByte Z UI and editor regressions
python -m pytest -m writer        # write-path safety
python -m pytest -m map           # map reading, placement, rendering, layout
python -m pytest -m research      # research and runtime tooling
python -m pytest -m rom           # ROM-gated; skips without a ROM
```

Compose them when the change crosses a boundary:

```bash
python -m pytest -m "fast and writer"     # one subsystem, portable only
python -m pytest -m "writer or map"       # a typical subsystem cross-check
python -m pytest -m "fast and research"
```

Add the directory when you already know which one it is: `pytest -m` still
collects the whole tree first (a few seconds here) before deselecting, so
`python -m pytest tests/unit -m "fast and writer"` finishes sooner.

`.\scripts\test.ps1` (the repository's single test entry point) runs the portable
gate, `-m fast`, by default and passes every extra argument through to pytest
after that selection. So `.\scripts\test.ps1 tests/unit/test_relocation.py` runs
that file inside the default gate, and a narrower `-k`, `--maxfail` or path
argument composes with it. A second `-m` replaces the default rather than
composing with it, because pytest keeps the last one. The entry point also runs
`-n 4 --dist loadfile` by default, and `-n 0` is the explicit serial opt-out:
`.\scripts\test.ps1 -n 0` runs the same gate in one process (see "Parallel
runs").

To run the whole tree through the entry point, replace the selection with the
expression that covers every gate, rather than trying to clear it: an empty `-m`
does not work here, because Windows PowerShell 5.1 (the requirement `README.md`
names) drops an empty string argument and pytest then exits with
`argument -m: expected one argument`.

```powershell
.\scripts\test.ps1 -m "fast or rom or workbench or writer or map or research"
```

That expression is exhaustive rather than a guess: measured 2026-10-11, those six
markers are the complete set in `pyproject.toml`, the expression collects the same
6,781 tests as no `-m` at all, and its complement
(`-m "not (fast or rom or workbench or writer or map or research)"`) collects zero.
Every test carries at least one of them.

### Parallel runs

The entry point and the `test-sdk` CI job both run the gate across pytest-xdist
worker processes, at module granularity (`--dist loadfile`), because the
slowest modules here are dominated by per-module setup rather than by the tests
themselves. Each worker is a separate process, so worker-local caches, module
level fixtures and monkeypatched module attributes are per-worker rather than
shared, and the counts must not change.

Opt out with `-n 0`, which real pytest reads as "no workers" and runs
everything in one process:

```powershell
.\scripts\test.ps1 -n 0                                        # serial
.\scripts\test.ps1 tests\unit\test_relocation.py -n 0          # serial, one file
```

The `-n 0` check comes first and matches that exact spelling, because the
requirement `README.md` names is Windows PowerShell 5.1, which has no `--%`
stop-parsing token. A caller that passes its own `-n` or `--dist` in any other
form overrides the default rather than colliding with it, since the default
pair is written first and the caller's arguments are appended.

**Same counts, either mode.** A serial and a parallel run of the same commit
must report identical collected, passed, skipped and failed counts. A test that
passes serially and fails in parallel is a finding about test isolation, not a
flake to retry, and it is reported with the differing node ids rather than
worked around.

**Which worker a failure came from.** Each worker stamps its own id on the
failure's header line, so a failure reads:

```text
================================== FAILURES ===================================
_______________________________ test_this_fails _______________________________
[gw0] win32 -- Python 3.12.10 <the interpreter that ran it>
```

`--dist loadfile` sends a whole module to one worker, so that `gw0` is the
process that ran the failing module. The last line before the assertion, the one
naming the file and line, is the test; the `[gwN]` above it is the worker to
search the job log for, because the summary's `FAILED ...` line carries the node
id but not the worker.

**Re-run one failure alone, serially.** Prefix the node id with the opt-out so
the failing test runs in a single process with no distribution in the way:

```powershell
.\scripts\test.ps1 -n 0 tests\unit\test_relocation.py::test_the_guard_refuses_a_stale_cursor
```

A gate is a *selection*, not a promise: `-m rom` on a machine with no ROM
reports skips, and `-m fast` includes members that need the canonical image or a
local artifact and skip without them. Measured 2026-10-08, six of the portable
gate's members read the canonical image - four in
`tests/unit/test_workbench_session.py`, one in `tests/unit/test_workbench_graphics.py`,
and `tests/unit/test_map_render.py:test_map40_renders_from_vram_capture`, which
also needs a captured map40 VRAM dump - and further members skip when the
assembled atlas, a built site or the VRAM oracle is absent. Read the summary
line, not just the exit code.

`tests/unit/test_write_invariants_property.py` is property-based: it explores
generated edit sets and images with Hypothesis, derandomized so the gate is
reproducible run to run. Raise the search depth for a deeper sweep with
`WEBFOOT_PROPERTY_EXAMPLES=500`; a failure always prints the falsifying example
and the seed that produced it.

## What a normal change runs

The smallest scope that bounds the change, then the portable gate if the
change is shared:

- changed surface: the test files next to the code you touched;
- relevant domain: `python -m pytest -m <gate>` for the subsystem;
- cross-domain safety: `python -m pytest -m fast` before freezing.

The full-suite rules in `docs/DEVELOPMENT.md` still govern when a broad
integration run
is genuinely warranted.

## Environment requirements

- **Run from the repository root.** Tests read `config/`, `upstreams.lock` and
  `roms/` relatively. The session header says so when the working directory is
  not the root.
- **The temporary root must be outside the repository tree.** The output-safety
  tests that expect an accepted output fail by design when `tmp_path` resolves
  inside the repository, because the generated-output guards refuse paths
  inside version control. Measured 2026-09-20 with the temp root at
  `<checkout>/build/`: exactly five tests, four in
  `test_asset_export_output_safety.py` plus
  `test_mgba_capture.py::test_capture_output_is_restricted_to_ignored_build_tree`.
  The mGBA check is location-dependent because `build/` is an accepted capture
  tree, so an in-repository root elsewhere costs four rather than five; the
  four output-safety failures happen wherever the root sits inside the work
  tree.
  Pass `--basetemp` outside the work tree, or rely on the default: when
  pytest's own temp root cannot be read, the conftest redirects the process
  temp root to an isolated one under the system temp directory and says so in
  the header. Redirecting rather than pinning `--basetemp` keeps pytest's own
  numbered basetemps, its `tmp_path_retention_count` pruning and its
  cleanup-after-a-green-run, and keeps two concurrent runs in one checkout from
  deleting each other's temporary directories. A `--basetemp` inside the
  repository is honoured, with a warning.
- **PySide6** is needed for the `workbench` gate. Without it those modules
  skip cleanly rather than erroring; install `.[workbench]` to run them. CI
  installs `.[dev,workbench,research]` and sets `QT_QPA_PLATFORM=offscreen`,
  because the runner has no display while several of those modules construct a
  real `QApplication` and real widgets.
- **capstone** is needed by the three `research` modules that sweep the Thumb
  decoder with it (`test_thumb_caller_census.py`,
  `test_thumb_disasm_field_extraction.py`, `test_ui_graphics_probe.py`); without
  it they skip as a whole file. It is research tooling rather than a shipping
  dependency, so it is the separate `research` extra: install `.[research]`.
- **A required GUI module must not collapse to a whole-file skip in CI.** The
  shipping Workbench modules are named in `REQUIRED_GUI_MODULES` in
  `tests/gates.py`. When a run collects one of them and it contributes no test,
  `tests/conftest.py` names it and its skip reason at session end, and under CI
  (`GITLAB_CI` or `CI`) that report is a session FAILURE rather than a skip
  count. Locally it is a warning only, so a developer without PySide6 can still
  run the portable suite; set `WEBFOOT_REQUIRE_GUI_TESTS=1` to make it fail
  locally as well, which is how the guard is mutation-tested. A targeted run is
  unaffected - a module the run never collected is never reported, so
  `pytest tests/unit/test_map_render.py` stays quiet.
  `tests/unit/test_ci_gui_surface.py` checks the CI half of the contract: the
  installed extras, the headless Qt platform, the module-level dependency guards
  and the regressions the change names.
- **A canonical ROM** is needed for the `rom` gate. It is read only; the
  canonical image is never written. The header reports which image, if any,
  the session found. The default location is
  `roms/Dragon Ball Z - Buu's Fury (U).gba`; `WEBFOOT_BUU_ROM` and
  `LOGX_CANONICAL_ROM` override it. Keep any local `roms/` a real ignored
  directory: a directory junction there is covered by `.gitignore` only
  because of the bare `roms` rule, and `git check-ignore` refuses to answer
  about a path *beyond* a link.

## How a test gets its gates

Gates come from the file's path and name, through the rules in
`tests/gates.py`:

- `tests/unit/...` is `fast`; `tests/integration/...` is `rom`;
- a name that states a concern joins that subsystem's gate, so
  `test_stat_write_rom.py` is `writer` and `test_logx_codec_rom.py` is
  `research`.

Those domain rules are filename heuristics, not a semantic analysis: a file
whose name does not state its concern carries only its axis gate, and a
concern spelled a new way needs a new rule. That is deliberate - the mapping
stays readable and reviewable - but it means a domain gate is "everything
named like this subsystem", not "everything that touches this subsystem". When
a change spans subsystems, run the axis gate (`-m fast`) rather than trusting
one domain name.

Adding an ordinary test file needs no registry edit: a new
`tests/unit/test_thing.py` is `fast`, and a new
`tests/integration/test_thing_rom.py` is `rom`. A genuinely new *concern*
gets a new rule in `tests/gates.py`, a marker in `pyproject.toml`, a row in
the table above, and a line in the doc. `test_test_gates.py` fails until all
of those agree, and it also fails if a rule stops matching any test file.

One further registry edit is not about gates: a new *shipping GUI* module also
belongs in `REQUIRED_GUI_MODULES` in `tests/gates.py`, the list CI fails over
when a whole Workbench module skips (see "Environment requirements"). A GUI
module left out of that list still runs; its silent collapse is just not caught.

## Measured baselines

Earlier measurement, 2026-09-20, `pytest 8.4.2` on Windows from the repository
root, with PySide6, capstone and hypothesis installed, and a local `roms/` link
present:

| command | result |
|---|---|
| `-m fast` | 2,057 passed, 9 skipped, 0 failed, ~138 s |
| `-m "fast and workbench"` | 129 passed, 3 skipped, ~22 s |
| `-m "fast and writer"` | 443 passed, ~24 s |
| `-m "fast and map"` | 297 passed, 1 skipped, ~13 s |
| `-m "fast and research"` | 648 passed, 1 skipped, ~73 s |
| `tests/integration/test_map_render_rom.py` | 3 passed, 2 skipped, ~5 s |

Most recent measurement, 2026-10-08, same machine and the same installed extras,
with the canonical image staged so the ROM-dependent portable members ran rather
than skipped:

| command | result |
|---|---|
| `python -m pytest tests/unit` (the `fast` gate) | 4,300 passed, 37 skipped, 0 failed, ~406 s |
| `python -m pytest --collect-only` (the whole tree) | 5,840 collected |

The portable gate is the row measured as a run; the whole-tree row is a
collection, not a run, because the full `rom` gate is the expensive integration
gate the policy forbids running by reflex. The whole-tree run skips the
ROM-gated half because no canonical image is configured for it, so the 90-minute
figure for the full `rom` gate remains a statement about the ROM-gated suite
rather than something this table measured.

The full `rom` gate was not run: it is the expensive integration gate the
policy forbids running by reflex. The single ROM-gated file above is a
representative sample that the axis works end to end.
