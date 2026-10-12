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
| `rom` | `tests/integration`, the ROM-gated suite | 1,503 | a canonical local ROM image, except one ROM-free member (see "The CI jobs") |
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

## App-wide Qt state: the adjacency run

`pytest` runs every test of one invocation in one process. That matters for the
shipping GUI, because `QApplication` is a **process-wide singleton**: a module
that names the application, sets its organisation, or applies the theme's style
sheet and palette is changing state that outlives it, and the next module in the
same process reads what it left behind. The concrete carriers here:

- `tools/webfoot/randomizer/gui.py:1294-1296` - `configure_application` sets
  `setOrganizationName`, `setApplicationName` and then calls
  `theme.apply_app_theme(app)`;
- `tools/webfoot/workbench/theme.py:430` - `apply_app_theme` ends in
  `app.setPalette(palette)` and `app.setStyleSheet(app_stylesheet())`;
- `tools/webfoot/workbench/theme.py:291` and
  `tools/webfoot/randomizer/gui.py:433,447` - `CONTROL_HEIGHT = 24`, the height
  the randomizer windows set on their controls, which is what
  `tests/unit/test_enemy_randomizer_gui.py:665` asserts.

`.\scripts\test.ps1` and the `test-sdk` CI job both distribute at **module**
granularity (`--dist loadfile`), so a module and its neighbour never share a
process there and that interaction is never exercised. The adjacency run is the
narrow, explicit gate that does exercise it:

```powershell
.venv\Scripts\python.exe -m scripts.adjacency_run -Order forward
.venv\Scripts\python.exe -m scripts.adjacency_run -Order reverse
```

One pytest process per order, no xdist, the whole fixed set in each. The set,
the order definitions and the fail-on-skip rule live in
`scripts/adjacency_run.py`, and `tests/unit/test_adjacency.py` pins them: the set
is exactly `REQUIRED_GUI_MODULES` plus the two randomizer modules, both orders
are exact reverses, and the `adjacency` CI job runs both. A change to
`REQUIRED_GUI_MODULES` fails that test on purpose, so the set is re-measured
rather than silently drifting.

The run fails rather than skips if any member cannot execute: a module that
collapses to a whole-file skip cannot say anything about adjacency, so a job
satisfied by skips would be a lie. The one member of the set that needs the
canonical image - `tests/unit/test_workbench_graphics.py:1010` - is excluded by
node id with that reason in the job log.

Measured 2026-10-12 in this worktree, PySide6 6.12.0, offscreen Qt:

| order | command | result | wall clock |
|---|---|---|---|
| forward | `python -m scripts.adjacency_run -Order forward` | 399 collected, 399 passed, 0 skipped, 0 failed | 52.6 s |
| reverse | `python -m scripts.adjacency_run -Order reverse` | 399 collected, 399 passed, 0 skipped, 0 failed | 35.3 s |

Same counts in either order, which is what "no order-dependent module in this
set" looks like as a measurement. What the set does carry across a module
boundary is measured separately: after
`tests/unit/test_warp_randomizer_gui.py` runs,
`QApplication.applicationName()` is still `"Buu's Fury Warp Randomizer"` for
every later module in the process, while the stylesheet and the palette are
restored by that module's own `finally` block.
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

### The interpreter, and cutting a worktree

`.\scripts\test.ps1` finds its own interpreter and says which one it chose, so a
ticket worktree needs no hand setup. It tries, in order:

1. the worktree's own `.venv\Scripts\python.exe`;
2. the shared test venv, the sibling directory
   `log1-remake-test-speed-003\build\test-speed-003\venv` (python 3.12.10,
   pytest 8.4.2, pytest-xdist 3.8.0, hypothesis, capstone), printing
   `test.ps1: interpreter <path> (the worktree .venv)` or `(the shared test venv)`
   so the chosen environment is never a guess.

The shared venv is named as that sibling path and searched for upward from the
checkout root rather than written as one machine's absolute path, because
`tools.quality.public_surface` forbids a machine-specific absolute path in
tracked text, and because worktrees here are cut at three depths: straight under
the checkout parent, one level deeper under a ticket directory, and nested under
`build\worktrees`. When nothing is found the script fails and names the sibling
to junction instead.

Measured 2026-10-12 in a scratch copy of the tree that mirrors the layout above:
with a `.venv` present the script printed its own path and `(the worktree .venv)`;
with the `.venv` removed it printed the shared venv path and `(the shared test
venv)`; with a `.venv` directory holding no `Scripts\python.exe` it printed the
shared path as well; and a copy nested three levels deep under `build\worktrees`
printed the shared path too. Every state was read off `-ResolveOnly`, which stops
after that line, so no gate was run to measure them. The primary checkout's venv
is deliberately not a candidate: it is read-only and has no pytest-xdist.

`.\scripts\new-ticket-worktree.ps1 -Ticket <id> -Branch <name>` cuts a worktree
in one command: it fetches `origin`, prints the frozen base SHA it read from
`origin/master`, adds `log1-remake-<id>` next to the checkout, junctions `.venv`
to the shared venv, and prints the ownership sweep, every sibling worktree with
its branch and its uncommitted file count plus up to eight of those paths, so a
writer can see which surface is already held before claiming it. `-Parent <dir>`
puts the worktree somewhere else. `-SiteGates` additionally runs `npm ci`, about
four minutes, because the site's own commands (`npm run check`, `npm run build`)
read `node_modules`; the `test-site` and `deploy-site` jobs in `.gitlab-ci.yml`
run it for the same reason, and the Python gates do not need it.

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

**Serial is the fallback when the parallel default runs out of room.** Each
worker is a separate Python process with this tree's modules imported, so the
default four workers hold four of those at once. A failure that disappears under
`-n 0` is a statement about worker processes rather than about the change, and
the serial run of the same node ids is what says which; report both counts before
concluding anything.

The `-n 0` check comes first and matches that exact spelling. Windows PowerShell
5.1 splits the pair before the script sees it, which is why the check looks for
two arguments rather than one string. `--%` does exist from PowerShell 3, and it
is deliberately not the mechanism here: measured on this machine's 5.1.26100, it
stops parsing where it appears, so a caller must place it before every argument,
and it still passes the shell's own redirection tokens through to the child as
literal arguments. A caller that passes its own `-n` or `--dist` in any other
form overrides the default rather than colliding with it, since the default pair
is written first and the caller's arguments are appended.

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

## Before merging: the stale-base gate

A merge-request pipeline runs on the branch's own commit, not on `master` as
`master` is when the merge lands. `scripts/pre-merge-check.ps1` is the cheap gate
for the one thing that leaves unmeasured - a path both master and the branch
changed - and it is the only local check in this document that is not a pytest
selection:

```powershell
.\scripts\pre-merge-check.ps1 -Ref <branch or SHA>
```

It fetches the target, prints the predicted merged tree, and exits 1 when the
target changed a path the candidate changed or when the merge conflicts. It
pushes and merges nothing, refuses the primary checkout structurally rather than
by name, and writes only what git writes: remote-tracking refs from the fetch and
tree/blob objects from `merge-tree`. Read its exit 1 as an instruction - rebase
onto live master, re-run the focused tests, re-request - not as a block.
`docs/git-workflow.md` carries the measured sample behind it, the one drifted
merge it would have stopped, and the reasons it is not a re-test. It is
deliberately not wired into `.\scripts\test.ps1`: it needs the network for its
one fetch, and the portable gate must not.

## The CI jobs

`.gitlab-ci.yml` runs four test-stage jobs and one deploy job, and each of them
names what it executes rather than trusting a filter to select it:

- **`test-sdk`** is the `fast` gate: `python -m pytest tests/unit` across xdist
  workers, then the tree-wide quality gates. It installs the `workbench` and
  `research` extras and sets a headless Qt platform, because fifteen GUI modules
  would otherwise collapse to one skip each and leave the job green over a surface
  it never ran. `tests/unit/test_ci_gui_surface.py` asserts that environment.
- **`test-integration`** runs
  `tests/integration/test_container_decode_synthetic.py` by name, and nothing
  else. That file is the `rom` gate's one ROM-free member: it decodes a committed
  synthetic container fixture and pins the fixture and both decoded members by
  sha256, so it needs no `roms/`, no emulator and no network, and it never skips.
  It stays under `tests/integration` because it is an integration-shaped decode of
  a whole container, and the directory is what gives the file the name the job
  selects. No new marker was added for it: a marker carrying one file would need a
  rule in `tests/gates.py`, an entry in `pyproject.toml` and a row in the table
  above, and the exception is stated here instead.

  Its install is `.[dev]`, measured rather than assumed. The selection's runtime
  import graph is `hashlib`, `json`, `pathlib`, `__future__` and
  `tools.webfoot.formats`, and that package imports nothing at all; `pytest` is
  the only non-stdlib need and it is the `dev` extra. `workbench` and `research`
  are deliberately absent - the job used to install a Qt wheel of about 100 MiB
  plus capstone for four tests that import neither.
  `tests/unit/test_ci_gui_surface.py` asserts both halves. `QT_QPA_PLATFORM`
  stays deliberately absent for the same reason the trim exists: the selection
  imports no Qt, so there is no platform plugin to select.
- **`adjacency`** runs `scripts/adjacency_run.py` twice, once per order, one
  pytest process each (see "App-wide Qt state: the adjacency run"). `test-sdk`'s
  `--dist loadfile` is what makes this a separate job rather than part of it.
- **`test-site`** validates the built progress site.
- **`deploy-site`** publishes it, and its non-optional `needs:` names every
  test-stage job, so a pipeline that excluded one of them by its rules fails to be
  created instead of publishing without it.

The rest of the `rom` gate needs the canonical image and is not collected in CI:
`-m rom` without `roms/` reports skips, and a job that collected the directory
would be green over exactly those skips. The named member above is the exception,
and selecting it by name is what keeps the exception from becoming the rule:

```bash
python -m pytest tests/integration/test_container_decode_synthetic.py -q
```

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
- **When pytest cannot use its own `pytest-of-<user>` root.** The failure to look
  for is `PermissionError: [WinError 5] Access is denied` on the directory
  pytest builds under the process temp root. The escape hatch is
  `PYTEST_DEBUG_TEMPROOT`, which pytest 8.4.2 reads as the temp root itself
  rather than as a debug flag (`_pytest/tmpdir.py:155`, `temproot =
  Path(from_env or tempfile.gettempdir()).resolve()`, with the
  `pytest-of-<user>` basetemp created under it). Point it at a directory you own
  outside the repository and the session header prints that root:
  `$env:PYTEST_DEBUG_TEMPROOT = '<a directory you own>'`. Measured 2026-10-12:
  the default root under this machine's temp directory already carries ACEs for
  several sandbox SIDs (`Caleputer\CodexSandboxUsers` among them), yet a shell in
  this session created and removed a directory inside it without error, so the
  denial is a property of the process, or of a root another process left behind,
  not a permanent state of the directory. The conftest redirect above covers the
  case where the variable is not set.
- **PySide6** is needed for the `workbench` gate. Without it those modules
  skip cleanly rather than erroring; `.\scripts\setup.ps1` installs it, and
  `uv sync --locked --extra workbench` adds it to an existing environment. CI
  installs `.[dev,workbench,research]` and sets `QT_QPA_PLATFORM=offscreen`,
  because the runner has no display while several of those modules construct a
  real `QApplication` and real widgets.
- **capstone** is needed by the three `research` modules that sweep the Thumb
  decoder with it (`test_thumb_caller_census.py`,
  `test_thumb_disasm_field_extraction.py`, `test_ui_graphics_probe.py`); without
  it they skip as a whole file. It is research tooling rather than a shipping
  dependency, so it is the separate `research` extra: `.\scripts\setup.ps1`
  installs it, and `uv sync --locked --extra research` adds it to an existing
  environment.
- **`scripts/setup.ps1` installs `dev`, `workbench` and `research`**, the same
  three extras CI installs, so the one command the project tells a contributor
  to run produces an environment that runs every portable gate instead of one
  that skips the workbench and research halves. Its `-Extra` parameter replaces
  the set, for example `-Extra dev` for a deliberately minimal environment.
  `packaging` (PyInstaller) is not installed: cutting a release is an owner-run
  step and `.\scripts\build-*.ps1` documents how to get it.
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
  `LOGX_CANONICAL_ROM` override it. `tests/rom_support.py:28` is the shared
  reader, trying `WEBFOOT_BUU_ROM` first and `LOGX_CANONICAL_ROM` second, and
  accepting a value only when it is a file. Measured 2026-10-12 in this tree:
  both names appear in `tests/rom_support.py:28`, the module that owns that lookup
  order, and in the ROM-gated files under `tests/integration/`, where each file's
  own guard reads one or both of them before it skips. The per-file list is
  deliberately not written down: it moves with every ROM-gated file added or
  removed, and a recorded list or count is a second copy of what one search
  already answers. Enumerate it instead:

  ```bash
  git grep -l LOGX_CANONICAL_ROM -- tests
  git grep -l WEBFOOT_BUU_ROM -- tests
  ```

  - The one `tests/unit` file that names either variable is
    `tests/unit/test_ticket_worktree_setup.py`, a documentation guard asserting
    that this section still names both. It opens no image: that occurrence is the
    guard matching this file's text, so no `tests/unit` file resolves either
    variable at run time.

  Keep any local `roms/` a real ignored directory: a directory junction there is
  covered by `.gitignore` only because of the bare `roms` rule, and
  `git check-ignore` refuses to answer about a path *beyond* a link.
- **Running a ROM-gated file with no local `roms/`.** Point the variable at a
  byte-identical scratch copy outside the work tree, never at the canonical
  input, and check the digest on both sides: the copy must hash to
  `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
  (`tests/rom_support.py:30`), a file that does not is skipped
  (`canonical_rom_bytes`), and a test that could have written re-hashes the input
  afterwards (`assert_canonical_unchanged`). `mutable_rom_copy` is the only write
  path, and it proves the copy is a distinct file from every protected
  repository input before handing it over. `docs/ROM_SAFETY.md` states the same
  rule: preserve the original read-only and experiment on an ignored copy.

  ```powershell
  $copy = "$env:TEMP\buu-scratch.gba"
  Copy-Item 'roms\Dragon Ball Z - Buu''s Fury (U).gba' $copy
  (Get-FileHash $copy -Algorithm SHA256).Hash.ToLower()   # 940ad5f0...
  $env:WEBFOOT_BUU_ROM = $copy
  python -m pytest -m rom tests\integration\test_map_render_rom.py -q
  (Get-FileHash $copy -Algorithm SHA256).Hash.ToLower()   # unchanged
  ```

## How a test gets its gates

Gates come from the file's path and name, through the rules in
`tests/gates.py`:

- `tests/unit/...` is `fast`; `tests/integration/...` is `rom`, with one stated
  exception: the ROM-free member named under "The CI jobs" carries `rom` from the
  directory but reads no image;
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
