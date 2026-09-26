# WARPRAND-APP-001 - the standalone Buu's Fury Warp Randomizer application

**This is not a roadmap ticket.** It occupies no phase and advances no
capability. It wraps the already-closed side hack recorded in
[`ROMHACK-WARP-RANDOMIZER-001.md`](ROMHACK-WARP-RANDOMIZER-001.md) as a small
Windows utility that other people can run against their own clean ROM.
`docs/PROJECT_<local-state-name>` stays `MAP-WARPS-AND-CONNECTIONS-001`, the Workbench
warp editor is **not** resumed by this pass, and `src/data/capabilities.json` is
**not touched**: DragonByte Z remains **19 / 24 - 79%**.

## Objective

Ship **Buu's Fury Warp Randomizer v0.1.0** - one window, one ROM check, one
seed, one output - as a standalone Windows executable that randomizes the
proven `reciprocal-door-pairs/3` transition family and reports exactly what it
did, without ever writing to the user's ROM.

## Product identity

| | |
| --- | --- |
| Product name | Buu's Fury Warp Randomizer |
| Version | 0.1.0 |
| Policy | `reciprocal-door-pairs/3` |
| Launch seed | `Goku` |
| Supported image | US Buu's Fury, `8,388,608` bytes, `940AD5F0…F059E` |
| Release artifact | `Buu-Fury-Warp-Randomizer-v0.1.0-win64.zip` |

## What was built

**Baseline: `d9f7e6d`** - current clean master, which by then already carried the
predecessor randomizer (`ticket/romhack-warp-randomizer-001` was merged into
master while this ticket ran). This pass adds exactly one commit on top of it and
modifies no file that was already there.

The architecture is the one the ticket asked for, outermost last:

```text
tools/webfoot/warp_randomizer.py            the algorithm - unchanged, reused
tools/webfoot/warprand/service.py           the application boundary (no Qt)
tools/webfoot/warprand/gui.py               one window over that boundary
Buu-Fury-Warp-Randomizer.spec.in            the tracked PyInstaller config
scripts/build-warprand.ps1                  generate the .spec and build
scripts/smoke-warprand-packaged.ps1         the packaged-executable gate
scripts/package-warprand.ps1                the release zip and content gate
```

**The algorithm was not reimplemented, and no core file was modified.** This
commit touches no file the predecessor shipped: `warp_randomizer.py` still
reports `POLICY_ID`, still draws its permutation from SHA-256, and still owns
every destination, arrival, facing and refusal decision. The boundary calls
`plan_warp_randomization` for the mapping and `webfoot.write.emit_image` for the
write - the one writer - and adds only what a *product* has to answer around them.

Because `.gitignore` files `*.spec` under "Generated builds" - the same convention
that leaves the existing `DragonByte Z.spec` untracked - the packaging
configuration is tracked as `Buu-Fury-Warp-Randomizer.spec.in`, and the `.spec`
PyInstaller consumes is generated from it by `scripts/build-warprand.ps1`. That
keeps the release reproducible from a fresh clone without contradicting the
repository's convention.

### The boundary

* `verify_rom` checks a selected file against the **packaged profile's own**
  size and SHA-256. The expected values are read from verified profile data, not
  restated in the app, so the refusal can never quote a stale hash. It returns a
  verdict rather than raising, because it is called the instant a file is chosen.
* `randomize_warps(source, output, seed, policy)` is the ticket's signature. It
  refuses an unknown policy rather than ignoring it - a policy argument that was
  silently dropped would produce a `/3` mapping under a caller's `/4` label.
* Output naming, seed sanitisation, collision policy and the manifest live here.
  The GUI holds none of them.

Two phases, in this order: the **write request** (seed, aliases, folder,
collision) and only then the **input image**. The cheap, total, path-level rules
come first, which is the ordering `webfoot.write.emit_image` already uses and for
the same reason - the input path also exists, so the alias check must run before
the overwrite policy or writing over the input raises the wrong rule.

### The window

One window: ROM row with an immediate verdict, seed row with **Random Seed**,
output row, one **Randomize** button, the progression disclaimer, a technical
status readout, **Open Folder** and **Copy Hash**. No tabs, no policy picker, no
configuration the randomizer does not support.

Work runs on one `QThread` with four outcomes (success, collision, refusal,
crash); the button is disabled and a **progress bar** shows. The bar is fed by
the boundary's own phase reports - `PROGRESS_STEPS`, reported immediately
*before* the work each names - so it can understate progress but never claim work
that has not happened. A core refusal arrives as a sentence; a programmer error
keeps its traceback behind "Show Details...".

### Appearance

The window is a **client of the one DragonByte Z theme**,
`tools/webfoot/workbench/theme.py` - the palette derived from Buu's own sprite -
and the published site carries the same tokens (`src/styles/global.css`:
`--pink-soft #f2ccdf`, `--pink-strong #a81560`, `--surface #fdfbfc`). The
utility holds **no colour of its own**: it names theme roles
(`dbzRole="primary"|"hint"|"fieldLabel"`), uses `theme.mono_font()` for the
technical readout, and
`test_the_app_module_holds_no_colour_of_its_own` fails if a hex literal ever
appears in `gui.py`'s executable code.

## Evidence

### Focused tests

| File | Gate | Result |
| --- | --- | --- |
| `tests/unit/test_warp_randomizer_app.py` | `fast` | 42 passed |
| `tests/unit/test_warp_randomizer_gui.py` | `fast` | 50 passed |
| `tests/integration/test_warp_randomizer_app_rom.py` | `rom` | 16 passed |

Each row was measured per file with `pytest <file> -q`, no marker gate, no skips
(the GUI row really runs the symlink case). This table has been wrong twice: an
earlier revision said 39/43, and the revision after that said 48/51. Both were
arithmetic guessed from a combined total instead of measured, and the independent
reviewer caught both. It now carries the measured values, and the combined figure
below is the sum of the three rows exactly (42 + 50 + 16 = 108 - the last
correction round added the GUI test for the cleared-field case).

The whole randomizer surface - the predecessor's two files included - was run on
the frozen commit in one pass: **163 passed** across
`tests/unit/test_warp_randomizer.py`, the two new `unit` files, and both
`tests/integration` ROM files.

The two new `unit` files use synthetic fixtures (a 4 KB image with a parseable
GBA header and its own profile), so the portable gate proves the boundary's
rules - wrong size, wrong hash, a file too short to carry a GBA header, missing
file, input==output including a **hard link**, collision, the canonical-copy
guard, "a refused overwrite destroys nothing", seed sanitisation versus seed
pass-through, policy refusal, friendly core errors - **without a commercial ROM
on the machine**. The new `rom` file proves what needs the real image: the
canonical counts, the golden hash, manifest content and byte-determinism across
two directories, source immutability, and the full progress sequence.

`tests/integration/test_warp_randomizer_rom.py` and
`tests/unit/test_warp_randomizer.py` are **unmodified**; the core's own proofs
still hold.

### The portable gate

`python -m pytest -m fast`: **3,229 passed, 1 failed, 3 skipped**.

The one failure is `test_capability_registry.py::test_the_built_page_renders_the_registry_list`,
and it is **pre-existing and environmental, not caused by this ticket**. It
compares the *generated site page* `dist/index.html` against
`src/data/capabilities.json`. That page is an untracked build artifact - `dist/`
is ignored - and on this machine it was written `2026-09-25 12:54`, six hours
*before* the registry it now contradicts (`2026-09-25 18:51`); the registry says
the `resize` capability shipped and the stale page renders it as planned. It
fails identically in isolation, it fails without any of this ticket's files, and
this ticket changed neither the registry nor the site. It is the same stale
`dist/index.html` the predecessor ticket recorded. Rebuilding the site is a
public-publishing action and is out of scope here (`public progress impact:
NONE`), so it is reported rather than papered over.

### The golden launch seed

```text
KNOWN LAUNCH SEED:            Goku
GOLDEN v0.1.0 OUTPUT SHA-256: ed167ca17944e4782cf19bf31245f772e5b7b9f5c66af317ddbedc8906c5abdc
supported 735 / randomized 496 / destinations moved 492 / skipped 239
```

Recorded from the **packaged executable**, and reproduced independently by the
ROM-gated test (which recomputes the 8 MB output and compares its digest) and by
the packaged `--smoke` run. An earlier revision of this document said "four
independent ways"; that was an overclaim the reviewer correctly measured - the GUI
test only carries the constant as a stand-in fixture's field and never computes
it, and the portable boundary test works on a 4 KB synthetic image and cannot
produce this digest at all. The ticket's warning was honoured: this is *not* the
older `0ff__white` hash.

### Packaged executable smoke

`scripts/smoke-warprand-packaged.ps1` drives the real release binary. The frozen
build is windowed and has no console, so it is asked for a machine-readable
report through its own `--smoke` entry, which goes through the same
`set_rom_path` the Browse button calls and the same `start_randomization` the
Randomize button calls. Result: **PASS** - output written, manifest written,
second run of `Goku` byte-identical, source ROM still canonical, and the golden
constant re-checked against the recorded value.

A genuine interactive launch of the same binary was also performed: the process
starts, holds a visible window titled `Buu's Fury Warp Randomizer v0.1.0`, stays
responsive, and closes cleanly.

### Visual QA

The real window was launched, driven through every state, and the captures were
opened and inspected (`build/warprand-app-001-qa/*.png`): launch with no ROM,
verified ROM, unsupported ROM, in-flight progress, success, refusal, long output
path, minimum width, and both dialogs. Three defects were found and fixed:

1. the two-line ROM refusal drew **on top of** the Seed row - a wrapping `QLabel`
   in a grid does not reliably grow its row when its text is replaced after the
   first layout pass, so the row now reserves three lines up front;
2. the status readout **clipped** a long refusal behind a horizontal scrollbar at
   the minimum width - it now wraps at the viewport;
3. the progression disclaimer, the policy line and the ROM verdict were painted
   in `palette(mid)` and measured as **near-invisible on this machine's dark
   theme** - the one limitation the window is required to state was effectively
   hidden. The stylesheet was removed in favour of the theme's own roles, and the
   verdict now carries its colour *and* a check/cross glyph.

### Release package

`scripts/package-warprand.ps1` stages the build, adds `README.txt`,
`THIRD-PARTY-NOTICES.txt` and `LICENSE`, and **fails closed** on proprietary
content: forbidden ROM/save/state extensions, the canonical image's exact hash,
and a byte-run probe that searches every packaged file for 48 informative 48-byte
runs whose offsets span the image. The probe enforces a **positive
control** - a file containing a needle at a non-zero offset, among unrelated
bytes, is pushed through the same per-file scan the real pass uses, because a
probe that never fires proves nothing.

Two earlier defects in this probe were found and fixed, both by measurement:

* its first version reported "ROM data" in `python312.dll`, because its needles
  were runs of `0x00`/`0xFF` padding that occur in every large binary. Bucketing
  by byte diversity fixed it;
* its second version claimed to sample "across the whole image" while actually
  covering the **first 197 KB** - 2.35% of the bytes, none of the graphics or
  text it was meant to catch. The independent reviewer measured that; the needle
  selection now walks the whole image and prints its measured coverage.

**What the probe still does not catch** is recorded in the script's header rather
than left implied, and a second review round measured the real numbers so the
claim is not read as stronger than it is: the 48 needles search **2,304 bytes of
8,388,608 - 0.027% of the image** - even though their *offsets* span 96.5% of it.
A carve is caught only if it contains one of those 48 exact windows. Blind spots,
stated: a carve from an unsampled region, an excerpt shorter than 48 bytes, a
*transformed* copy (compressed, base64, XORed, or a patch/delta), content inside a
nested container, and a header-stripped or trimmed copy. What it does catch - a
whole ROM under any name, a renamed copy that keeps its size, and a large carve -
is the shape a mistake in this build would actually take.

Result: `Buu-Fury-Warp-Randomizer-v0.1.0-win64.zip`, 35.4 MB -
`Buu-Fury-Warp-Randomizer.exe`, `README.txt`, `THIRD-PARTY-NOTICES.txt`,
`LICENSE` and the PyInstaller runtime directory (`_internal/`, including
`tools/webfoot/data/roms.yaml`, the profile catalog the frozen build reads).
**Proprietary content: NONE.**

The build is **onedir**, not one-file: one-file unpacks Qt to a temporary
directory on every launch, which costs seconds of startup and is the shape most
likely to be quarantined by an anti-virus heuristic. The ticket allows either.
~35 MB of QtQml/QtQuick/QtPdf/QtVirtualKeyboard/translations that a QtWidgets
application never loads were excluded; `opengl32sw.dll` was deliberately **kept**
because it is what renders the window on a machine with no usable GL driver.

## Reproducing the release

From the repository root, with a canonical ROM at
`roms/Dragon Ball Z - Buu's Fury (U).gba` (or `LOGX_CANONICAL_ROM` pointing at
one):

```powershell
python -m pytest tests/unit/test_warp_randomizer.py `
    tests/unit/test_warp_randomizer_app.py `
    tests/unit/test_warp_randomizer_gui.py -q
python -m pytest tests/integration/test_warp_randomizer_rom.py `
    tests/integration/test_warp_randomizer_app_rom.py -q

pwsh scripts/build-warprand.ps1 -Clean        # dist/Buu-Fury-Warp-Randomizer/
pwsh scripts/smoke-warprand-packaged.ps1      # the golden hash gate
pwsh scripts/package-warprand.ps1             # the release zip + content gate
```

To run the utility from a checkout instead of the executable:

```powershell
python -m tools.webfoot.warprand
```

## Independent review

Two rounds, both recorded in full in
[`WARPRAND-APP-001-review.md`](WARPRAND-APP-001-review.md).

**The mandated channel was attempted first, on both rounds, and failed on both.**
`the local reviewer` returned
`You've hit your session limit · resets 10:40am (America/Los_Angeles)` - jobs
`cl-20260926-151346-c84856` and `cl-20260926-153558-0ebd29`, both recorded
`status: failed, session: (none)`. That is an **account usage limit**, not a
candidate defect. Cloud was **not** run: `the reviewer readback probe` reports
`cloud_attach UNAVAILABLE` ("attaching to an existing cloud session is not enabled
for this account"), so a cloud verdict would not be readable here - the ticket's
own stated condition.

Both rounds then ran through a **fresh-context reviewer** that did not implement
the work, so the repository's independent-review gate was satisfied rather than
skipped.

### Round 1 - BLOCKED, one blocking finding

The reviewer confirmed scope independently (15 added files, 0 modified;
`capabilities.json`, `project.ts`, `PROJECT_<local-state-name>`, `PROJECT_<local-state-name>` untouched; no
ROM/save/state artefact), re-ran the permitted tests, reproduced the golden hash
and verified the canonical ROM unchanged before and after.

**B1.** `verify_rom` documented "Never raises" and did not honour it.
`tools.webfoot.rom.identify_rom` raises `GbaHeaderError` - a `ValueError` - for
any file under 192 bytes or with a non-ASCII header field, and `_identify` caught
only `RomReadError`/`OSError`. The consequence was worse than an ugly traceback:
`verify_selected_rom` assigned the cached verdict only *after* the call returned,
so selecting a good ROM and then a 24-byte file left the **good ROM's** "Verified
supported ROM ✓" on screen with **Randomize enabled** - a false verified state for
a file that is not a ROM - and pressing it produced the "unexpected problem"
defect dialog. Reachable through the file dialog's own "All files" filter.

Reproduced here before fixing (`24-byte file -> RAISED GbaHeaderError`). Fixed by
catching `GbaHeaderError` explicitly - not as a bare `ValueError`, so a real
programmer error still escapes - and reporting it as
`The selected file is not a Game Boy Advance ROM: …`; and by clearing the cached
verdict *before* anything can go wrong, with a defensive red "could not be
checked" state that keeps Randomize disabled if the boundary ever breaks its
contract again. Both halves are pinned by new tests.

### Round 2 - PASS, no blocking findings

On the correction commit `9402381`. Beyond re-running the permitted files, the
reviewer verified the blocking fix **end to end rather than by tests**: it drove
the real service through the real window, confirmed the exact round-1 scenario now
yields `Unsupported ROM ✗ … GBA header requires at least 192 bytes; got 24` with
Randomize disabled and no bug dialog, could construct **no** input that still makes
`verify_rom` raise, and proved the new service tests are genuine regression tests
by running them against a verbatim reproduction of the pre-fix method body. It
also confirmed the overwrite reordering introduced no new defect, that the
canonical-copy refusal still fires with `overwrite=True`, that the probe's
positive control now exercises the real per-file scan, and that the progress bar
can never reach 4/4 before the work is done.

It then raised four non-blocking findings and three notes **about the honesty of
this document and of the release claim** - two of them catching round-1 entries
that had been marked "Fixed" without being fixed. Those are exactly the findings
worth having, and all seven were addressed:

| | Round-2 finding | Resolution |
| --- | --- | --- |
| F1 | The per-file test counts in this document were wrong *again* (48/51; measured 42/49) | **Fixed**; the table is now measured per file, and the document says plainly that it has been wrong twice and why |
| F2 | Residual stale-verdict state of B1's class: the ROM field's own clear button left a verified verdict and an enabled Randomize over an **empty** path; `set_rom_path(..., verify=False)` had the same shape and was dead in production | **Fixed.** `rom_edit.textChanged` now invalidates the cached verdict immediately and shows a neutral "Not checked yet."; the dead parameter is gone. Pinned by a new GUI test |
| F3 | The probe's header still claimed it catches "a carved blob of 48+ contiguous bytes from anywhere in the image"; its needles actually search 2,304 of 8,388,608 bytes (0.027%), and a 48-byte carve at offset 1,000 is missed | **Fixed.** The header now states the measured byte coverage, adds "a carve from an unsampled region" to the blind-spot list, and says what it *does* catch. This document no longer calls the spanned-offset figure "measured coverage" |
| F4 | The committed brief still said "exactly one commit" and pinned `7bbd985`, a superseded candidate | **Fixed**; the brief now reads its SHAs from the repository |
| F5 | This document linked `WARPRAND-APP-001-review.md`, committed nowhere | **Fixed**; that file is the record |
| F6 | A GUI test's docstring claimed to pin B1 while passing on the pre-fix code | **Fixed**; the docstring now says what it actually proves and names the tests that do pin it |
| F7 | `gui.py` held a fallback output-name literal while this document claims the GUI owns no output naming | **Fixed**; the fallback uses the service's own template and seed sanitiser |

`SourceChangedError` remains the one declared test gap; the reviewer agreed it
cannot be arranged honestly in a portable test and it is recorded in the known
limits below.

**One gap the implementer found while the review ran and fixed in the same
correction commit:** the release bundle ships Qt and CPython with no notices for
them. A `THIRD-PARTY-NOTICES.txt` naming every bundled component and licence now
travels in the package, and its own "Known gap" section states plainly that the
LGPL licence *texts* are still not bundled and that this needs the owner's
decision before any public distribution - reported rather than papered over.

Two things are worth stating plainly rather than burying: **two round-1 entries
marked "Fixed" were not actually fixed**, and only the second round caught it -
the lesson, recorded in the review record, is that a correction to a *claim* needs
the claim re-measured rather than rewritten. And the release-content probe's
coverage is genuinely much weaker than the first version of this document implied;
what it does catch is now stated exactly.

## Scope boundaries observed

- **No capability count change.** `src/data/capabilities.json` untouched;
  DragonByte Z stays 19 / 24 - 79%. Warp/connection *editing* is not marked
  shipped because a standalone randomizer exists.
- **No Workbench surface**, no new tab, no editor. The Workbench is not resumed.
- **No new reverse engineering**: every fact used was already measured and is
  carried by `map_transitions` and the transition authority.
- **No progression guarantee.** The window states it; the manifest records it;
  the README repeats it.
- **No ROM distribution, and no ROM committed.** No `.gba`, save, state or
  runtime capture is staged; `dist/` and `build/` stay ignored.
- `public progress impact: NONE` - a side utility adds no published capability.

## Known limits, stated rather than implied

- Randomization is verified against **one** image. Another region, revision or a
  pre-patched dump is refused; there is no "continue anyway".
- The progress bar is phase-based, so it steps rather than sweeps. The phases are
  unevenly expensive and the caption, not the percentage, is what tells a user
  where the run is.
- `--smoke` is a **release-verification hook**, not product configuration: it
  cannot change what the randomizer does, and with no arguments the window is
  unchanged.
- Windows x64 only. Nothing was verified on another platform, and the release
  artifact is built by the repository's own `DragonByte Z.spec` conventions.
- The ROM-content probe samples the image and now spans all of it, but it is a
  strong check, not a proof of absence; its four known blind spots are listed in
  `scripts/package-warprand.ps1`'s header.
- **`SourceChangedError` is implemented but pinned by no test.** It fires only when
  the input image changes between the pre-run and post-run identification, which a
  portable test cannot arrange honestly. If the source becomes unparseable during
  a run, `_identify` now returns no identification and the same error is raised
  rather than a `GbaHeaderError`. Recorded as a test gap, not as a known defect.
- A confirmed overwrite deletes the old output only once the mapping is planned,
  so a bad input or an unplannable image can no longer destroy it. A failure in the
  remaining window - the write itself, or the source changing underneath the run -
  can still leave the user without the previous file. That is the irreducible cost
  of `emit_image` refusing to write over an existing destination.
- The shipped archive does not yet contain the LGPL licence *texts* for Qt; see
  `docs/warprand/THIRD-PARTY-NOTICES.txt`, "Known gap". Owner decision required
  before any public distribution.

## Stop

Stop when the application exists, is packaged, is proved by the packaged smoke,
and has been independently reviewed. Do not resume the Workbench warp editor, do
not open a new research line, and do not begin `MAP-WARPS-AND-CONNECTIONS-001`'s
Required Work 3 or 4 from here.
