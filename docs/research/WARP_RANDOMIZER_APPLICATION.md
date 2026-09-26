# WARPRAND-APP-001 - the standalone Buu's Fury Warp Randomizer application

STATUS: **CLOSED** (2026-09-26). v0.1.0 is built, packaged, independently
reviewed, and integrated. **The v0.1.0 executable was already shared publicly
before this integration completed** - that is recorded as history below, not
backdated.

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

Each row was measured per file with `pytest <file> -q`, no marker gate, no skips.
This table has been wrong twice: an earlier revision said 39/43, and the revision
after that said 48/51. Both were arithmetic guessed from a combined total instead
of measured, and the independent reviewer caught both. It now carries measured
values, and the five-file figure below is the measured sum, not a guess.

The whole randomizer surface - the predecessor's two files included - was run on
the frozen commit, each file on its own:

| File | Passed |
| --- | --- |
| `tests/unit/test_warp_randomizer.py` | 38 |
| `tests/unit/test_warp_randomizer_app.py` | 42 |
| `tests/unit/test_warp_randomizer_gui.py` | 50 |
| `tests/integration/test_warp_randomizer_rom.py` | 19 |
| `tests/integration/test_warp_randomizer_app_rom.py` | 16 |
| **total** | **165** |

(38 + 42 + 50 + 19 + 16 = 165. An earlier revision of this paragraph said 163;
a third review round measured 165 and was right - the aggregate had not been
re-measured when the per-file counts changed.)

The symlink refusal case lives in `tests/unit/test_warp_randomizer_app.py`
(`test_the_output_may_not_be_a_symlink_to_the_input`), not in the GUI file; both
files nevertheless run with zero skips on this machine.

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

`python -m pytest -m fast` on the final tip: **3,239 passed, 1 failed, 3 skipped**
(1,230 deselected - the `rom` axis).

**Recorded as: RUN ONCE, AGAINST THIS TICKET'S STANDING POLICY, NOT REPEATED.**
It was run once during implementation, before the closeout policy was stated, and
it is reported here because a run that happened is not made untrue by being
discouraged. Closeout itself ran no marker gate and no directory-wide selection;
the only test commands run during closeout were exact named files, and only where
a correction required them.

An earlier revision of this section said 3,229, the figure before the review
corrections added their tests; the stale-aggregate habit is why the number is
stated with its context rather than alone.

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

`scripts/package-warprand.ps1` stages **exactly two files** - the executable and
`README.txt` - and **fails closed** on proprietary
content: forbidden ROM/save/state extensions, the canonical image's exact hash,
and a byte-run probe that searches every staged file for 48 informative 48-byte
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
  selection now walks the whole image and takes 48 evenly spaced across it, and
  the script prints the **spanned-offset** figure (96.5% of offsets) - not a
  byte-coverage figure, which is 0.027%.

**What the probe still does not catch** is recorded in the script's header rather
than left implied, and the reviewer measured the real numbers so the claim is not
read as stronger than it is: the 48 needles search **2,304 bytes of 8,388,608 -
0.027% of the image** - even though their *offsets* span 96.5% of it. Round two
measured that; round three re-measured it and confirmed the corrected header,
including that a 1 MB carve at offset 4,000,000 **is** caught while a 48-byte
carve at offset 1,000 is not.
A carve is caught only if it contains one of those 48 exact windows. Blind spots,
stated: a carve from an unsampled region, an excerpt shorter than 48 bytes, a
*transformed* copy (compressed, base64, XORed, or a patch/delta), content inside a
nested container, and a header-stripped or trimmed copy. What it does catch - a
whole ROM under any name, a renamed copy that keeps its size, and a large carve -
is the shape a mistake in this build would actually take.

Result: `Buu-Fury-Warp-Randomizer-v0.1.0-win64.zip`, 35.1 MB, containing
**exactly two files** - `Buu-Fury-Warp-Randomizer.exe` and `README.txt` - so
"extract and run" is the whole procedure. **Proprietary content: NONE.**

The build is a **single file**, at the owner's direction. That is the form the
ticket allows ("single `.exe`"), and it is why the spec has no `COLLECT`: an
onedir build cannot be reduced to a lone executable, because the `.exe` needs its
runtime directory beside it, so a two-file archive required switching to one-file
packaging. The trade is stated rather than hidden:

* **startup costs ~4 s** - a one-file build unpacks its bundled runtime to a
  temporary directory on every launch. Measured on this machine: 4.44 s from
  `dist/`, 3.93 s from the extracted archive, against well under a second for the
  onedir build it replaced. The window appears and is responsive; it is simply
  slower to appear;
* a self-extracting executable is more likely to draw an anti-virus heuristic
  than a plain directory of DLLs, so the README tells the user what the
  "unknown publisher" prompt means;
* the byte-run content probe is **narrower** than it was for a directory of loose
  files, because the payload is now a compressed archive and only uncompressed
  content is searchable. What carries the weight instead is that the build has no
  ROM as an input at all - the only data file bundled is the profile catalog, a
  table of addresses and hashes - and the extension and exact-hash checks still
  run. Recorded in the script's header.

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

pwsh scripts/build-warprand.ps1 -Clean        # dist/Buu-Fury-Warp-Randomizer.exe
pwsh scripts/smoke-warprand-packaged.ps1      # the golden hash gate
pwsh scripts/package-warprand.ps1             # the release zip + content gate
```

To run the utility from a checkout instead of the executable:

```powershell
python -m tools.webfoot.warprand
```

## Independent review

Every review round is recorded in full in
[`WARPRAND-APP-001-review.md`](WARPRAND-APP-001-review.md), including each
round's verdict, findings and dispositions. The number is deliberately not
stated here: an earlier revision said "two rounds" while the file already held
three, which is the same stale-count mistake the rounds themselves kept catching.

**The mandated channel was attempted on every round, and failed every time.**
`the local reviewer` returned
`You've hit your session limit · resets 10:40am (America/Los_Angeles)` - jobs
`cl-20260926-151346-c84856` and `cl-20260926-153558-0ebd29`, both recorded
`status: failed, session: (none)`. That is an **account usage limit**, not a
candidate defect. Cloud was **not** run: `the reviewer readback probe` reports
`cloud_attach UNAVAILABLE` ("attaching to an existing cloud session is not enabled
for this account"), so a cloud verdict would not be readable here - the ticket's
own stated condition.

Every round then ran through a **fresh-context reviewer** that did not implement
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

### Round 3 - narrow verification of the corrections, PASS

Two of the round-2 fixes changed **production code** after a PASS, so a third,
narrow round verified that correction diff. It re-measured every test file on its
own, then verified the fixes **by measurement rather than by reading**:

* it clicked the ROM field's real clear button on the real window and confirmed
  no verdict and no enabled Randomize survive, then loaded the **pre-fix** `gui.py`
  side by side and reproduced the defect on the same click - proving the fix is
  operative and the new test genuinely fails on the old code (three of its five
  assertions fail there);
* it fuzzed **200 mutation sequences** over the ROM/output/seed controls against
  the invariants "a cached OK verdict must belong to the current text" and "no
  `None` verdict beside a Verified label", and found **zero** violations;
* it reimplemented the release script's needle selection read-only and confirmed
  both header numbers exactly, including that a 1 MB carve at offset 4,000,000 is
  caught while a 48-byte carve at offset 1,000 is not.

Its three findings were all documentation residuals of the same class round 2 had
raised, surviving in sentences round 2's own fix had added - the five-file
aggregate said 163 (measured **165**), the known-limits bullet still said the probe
"spans all of it" with "four" blind spots, and the brief still counted commits.
All three are fixed above. Full record:
[`WARPRAND-APP-001-review.md`](WARPRAND-APP-001-review.md).

**One gap the implementer found while the review ran:** the bundle ships Qt and
CPython with no notices for them. `docs/warprand/THIRD-PARTY-NOTICES.txt` now
names every bundled component and licence and states plainly that the LGPL
licence *texts* are still not bundled. At the owner's later direction the release
archive was cut back to the executable plus a brief README, so that notice no
longer ships either - which makes the gap larger, not smaller, and it is recorded
as an owner decision before any public distribution rather than glossed over.

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

### public progress impact: NONE

A side utility that ships an offline artefact adds no DragonByte Z capability and
moves no capability count, so the public capability story is unchanged:
`src/data/capabilities.json`, `src/data/project.ts` and the published site are all
untouched by this diff, warp/connection *editing* is not marked shipped, and no
cosmetic site edit was made to say otherwise.

## Known limits, stated rather than implied

- Randomization is verified against **one** image. Another region, revision or a
  pre-patched dump is refused; there is no "continue anyway".
- The progress bar is phase-based, so it steps rather than sweeps. The phases are
  unevenly expensive and the caption, not the percentage, is what tells a user
  where the run is.
- `--smoke` is a **release-verification hook**, not product configuration: it
  cannot change what the randomizer does, and with no arguments the window is
  unchanged.
- Windows x64 only. Nothing was verified on another platform. The build follows
  this repository's PyInstaller conventions in every respect **except** the
  packaging mode: `DragonByte Z.spec` is an onedir `COLLECT` build, and this
  artifact is one file, at the owner's direction - the trade is measured in the
  spec's own docstring and above in this document.
- The ROM-content probe samples the image and its needle offsets span 96.5% of it,
  but it is a strong check, not a proof of absence: **48 needles of 48 bytes search
  2,304 bytes of 8,388,608 (0.027%)**, so a carve is only caught if it contains one
  of those 48 exact windows. Its known blind spots are listed in
  `scripts/package-warprand.ps1`'s header, which is the single place that states
  them - no count is repeated here, because switching to one-file packaging
  changed the list and left this sentence quoting the old length.
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
- **The release archive ships no licence or third-party-notice files**, at the
  owner's direction: it holds the executable and a brief README and nothing else.
  `docs/warprand/THIRD-PARTY-NOTICES.txt` still exists in the repository and its
  "Known gap" section still stands - the LGPL licence *texts* for Qt are not
  bundled anywhere, which is an owner decision before any public distribution.
  What is not in the archive cannot be read by whoever downloads it.

## Closeout

### The product, as shipped

| | |
| --- | --- |
| App | Buu's Fury Warp Randomizer |
| Version | 0.1.0 |
| Policy | `reciprocal-door-pairs/3` |
| Default seed | `Goku` |
| Golden Goku output | `ed167ca17944e4782cf19bf31245f772e5b7b9f5c66af317ddbedc8906c5abdc` |
| Core counts | 735 supported / 496 randomized / 492 destinations moved / 239 skipped |
| Form | standalone Windows x64 executable - **no Python, no install, no terminal** |
| Progression guarantee | **NO** |
| Canonical ROM | **immutable and unchanged** - `940ad5f0…f059e` before and after every run |
| DragonByte Z | **19 / 24 - 79%, unchanged**; `capabilities.json` untouched |

### First public distribution - recorded as history, not backdated

**v0.1.0 was shared publicly before this repository integration completed.** The
repository did not produce that distribution, does not date it, and does not
claim the merge preceded it; `git log` on this branch shows the integration
commits, and the public share came first.

This matters for one honest reason: the artifact shared publicly was built from
the same application code but **before** the packaging was cut to a single file,
so its *archive* differs from the one recorded below. What did **not** differ is
what the tool produces: the randomized image is decided by the image, the seed,
the policy and the tool version, all of which are unchanged, so any v0.1.0 build
yields the same `Goku` output hash. The published artifact's own digest is not
recorded here because the repository never held it.

### Release evidence (current artifact, measured locally)

```text
Buu-Fury-Warp-Randomizer.exe
  bytes  37109070
  sha256 c9bd61258a1a9ec13252c506e0e79450a8d4b0c7df37ccce837ec619aed3fb23

Buu-Fury-Warp-Randomizer-v0.1.0-win64.zip   (contains only the .exe and README.txt)
  bytes  36765976
  sha256 38c6730686f97749cdc4d8e80bfed84126e04a262bbeca818573168cc09565e4
```

Both live in the ignored `dist/` tree, so they are release artifacts and not
source history - rebuilding from the frozen source reproduces them by procedure,
not byte-for-byte (PyInstaller embeds build metadata).

### What was verified at closeout, by inspection rather than by another test run

- **Scope:** the branch is **17 additions and zero modifications** against
  `origin/master`; the core algorithm, the capability registry,
  `src/data/project.ts`, `PROJECT_<local-state-name>`, `PROJECT_<local-state-name>` and the whole Workbench
  tree are untouched, and no ROM, save, savestate, runtime capture, image or
  archive is tracked anywhere in the diff.
- **Thin client:** no shuffle, pairing, arrival, facing or policy decision exists
  in `tools/webfoot/warprand/`; it imports `POLICY_ID` and calls
  `plan_warp_randomization`, `emit_image`, `normalize_seed` and
  `packaged_profile`. The only `reciprocal-door-pairs` text in the app layer is a
  docstring.
- **Product surface:** one `QMainWindow` with no tab or stacked-page widget, and
  the ROM picker, canonical verification, `Goku` default, Random Seed, output
  path, Randomize, progress, status, success summary, source immutability,
  deterministic manifest and progression disclaimer all present in source.

### Why `docs/PROJECT_<local-state-name>` was not edited

The predecessor side ticket (`ROMHACK-WARP-RANDOMIZER-001`) was likewise never
`PROJECT_<local-state-name>` and is likewise **not** recorded in `docs/PROJECT_<local-state-name>`; it sits
at the tickets root, as this one does. `docs/README.md`'s archive step is
part of the *replace `PROJECT_<local-state-name>`* workflow, which never applied here, and this
ticket advances no capability to record. Keeping the closeout in this document
therefore follows the convention its predecessor set and leaves the roadmap,
`PROJECT_<local-state-name>` and the capability registry untouched, as instructed. If the owner
wants a side-tool line in the project state anyway, that is a deliberate addition
rather than a closeout omission.

## Stop

Stop when the application exists, is packaged, is proved by the packaged smoke,
and has been independently reviewed. Do not resume the Workbench warp editor, do
not open a new research line, and do not begin `MAP-WARPS-AND-CONNECTIONS-001`'s
Required Work 3 or 4 from here.

**Reached.** The application exists and is packaged; the packaged-executable
smoke passes on the real binary with the pinned golden hash; the independent
review gate returned PASS with no blocking findings outstanding. The ticket is
CLOSED. Do not begin v0.1.1 work, do not redesign the packaging, and do not change
the randomizer algorithm under this ticket.
