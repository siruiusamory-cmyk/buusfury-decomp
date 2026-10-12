# RETRO-QT-SHUTDOWN-001: the suite's exit-time native crash

Owner order (Cale, 2026-10-12, relayed by the coordinator): complete the retro
items ASAP. This is the Product Studio item, C7: the shutdown segfault recorded
in section 5.3 of the Product Studio retro for 2026-10-12, with
`QT_FATAL_WARNINGS=1` named there as the next instrument. Its own ticket, in a
worktree from live master.

## 1. Publication changes: none (D1)

Nothing in this ticket reaches `src/data/capabilities.json`, `src/data/project.ts`
or the public site. It adds one document under `docs/research/`; the probes and
logs it cites stay in `build/retro-qt-shutdown-001/`, which is ignored, and are
named in the review request rather than committed. No capability or progress
statement changes, so no owner-approved publication edit is requested.

## 2. Baseline

The baseline is the live master tip, `3dfa7226ca3ae5539f4469a32e353afe6c338ec7`
(the merge of `ticket/retro-guards-render-followup-001`), read from
`git ls-remote origin refs/heads/master` on 2026-10-12. One local fact is worth
recording because it cost this ticket a mistaken baseline: in this clone
`git fetch origin` reported `up to date` and left `origin/master` at the stale
`933827a`, three commits behind, while `git ls-remote` showed `3dfa7226`. The
worktree was cut from the stale ref first and then reset onto the live tip, and
every number below is measured on the live tip. A lane that takes its baseline
from `origin/master` here should confirm it against `git ls-remote` first.

## 3. The recorded failure

Section 5.3 of the retro is the primary record: a `test-sdk` job that reports
every test passing and then dies in native Qt teardown during interpreter
finalization. **Four** pipelines in this repository carry that signature, read
back from the GitLab API on 2026-10-12:

| Pipeline | Ref | Job | SHA | Result |
| --- | --- | --- | --- | --- |
| 2936670905 | `ticket/text-tool-ui-001` | 17098101523 | `9bd16c89` | `1 failed, 5241 passed, 293 skipped`, then the crash |
| 2936750156 | `ticket/text-tool-ui-001` | 17098594988 | `245d0336` | exit 139 |
| 2936757492 | merge request 224 | 17098637198 | `245d0336` | exit 134 |
| 2936888158 | merge request 224 | 17099385133 | `04e3fc2d` | exit 139 |

The first three rows are the clean shape this ticket is about: a green run whose
job is red only because of the crash. The fourth, `2936670905`, is the same crash
on the same line, but its job was **already red** from a real failure before the
crash happened: `1 failed, 5241 passed, 293 skipped`, the failure being
`test_the_public_surface_is_clean`, which had found an unregistered launch site.
It is counted here because the crash is the same and equally real, and it is
called out separately because it is not evidence that a green run turns red: that
job would have failed without the crash. The reviewer of the first version of this
document found it and the count was corrected from three to four.

The three crash-only rows each report `5242 passed, 293 skipped` and then, after
the summary:

```text
QObject: shared QObject was deleted directly. The program is malformed and may crash.
Fatal Python error: Segmentation fault
Current thread 0x000079b03abcc340 (most recent call first):
  <no Python frame>
Extension modules: yaml._yaml, shiboken6.Shiboken, PySide6.QtCore, PySide6.QtGui,
PySide6.QtWidgets, PySide6.QtTest, PySide6.QtSvg (total: 7)
```

The 134 pipeline is the same warning followed by `pure virtual method called` and
`terminate called without an active exception`, which is the same teardown fault
reaching a different abort. So the crash is not one signature but a family, and in
all four it happens after the last test result has been reported.

All four are on the text-tool line. A scan of every failed `test-sdk` job in the
100 most recent pipelines found the signature in exactly these four and in no
other pipeline, and every other failure in that window is an ordinary test failure
(`exit code 1`, with a failing test named above it). `2936670905` is the one of
the four that was already red on its own merits, so it is not evidence that a
green run turns red; the other three are.

## 4. Master does not reproduce it, measured

**The authority for the clean-master claim is CI, not this machine.** The `master`
pipeline for this baseline (pipeline 2939644504, at `3dfa7226`, job 17120014534)
is green, with `5152 passed, 305 skipped in 188.12s`, and every `master` pipeline
in the hundred most recent is green. The four crash pipelines in section 3 are CI
traces too, read the same way, so both sides of the comparison come from the same
instrument.

**A rule breach is recorded here rather than hidden.** The owner standing rule is
that the full suite is never run locally: CI is the full gate, and no budget or
context allowance lifts that. The full unit suite was run locally during this
ticket, twice, and both runs are breaches. They are kept in the record as breach
measurements and are NOT the evidence for the clean-master claim above; the CI
traces are. Both commands are named so the breach is not repeated by accident.
The suites below are the ones a local run is allowed to make.

- **BREACH: the full unit suite locally, one process, no xdist.** Command:
  `python -m pytest tests/unit -q -p no:cacheprovider`, with
  `QT_QPA_PLATFORM=offscreen`. Result:
  **`5360 passed, 97 skipped in 841.61s (0:14:01)`**, process exit 0, no warning
  of any kind, and zero matches in the log for `QObject: shared QObject`,
  `Fatal Python error`, `Segmentation fault` or `pure virtual`
  (`build/retro-qt-shutdown-001/unit-serial-livetip.log`, SHA-256
  `EB37160142C19C590B659293AB5A614F0D46C8986CB867D5E0CF5D512E48116B`).
- **BREACH: the full unit suite locally in the shape CI runs it.** Command:
  `python -m pytest tests/unit -q -n auto --dist loadfile -p no:cacheprovider`,
  through the shared test venv because the worktree junction has no xdist.
  Result: **`5360 passed, 97 skipped in 254.97s (0:04:14)`**, process exit 0, no
  crash (`build/retro-qt-shutdown-001/unit-xdist-livetip.log`, SHA-256
  `A9160DAE8F2C5508F8CC5733406A123B7C07E55AB38F968B3CECAE4E0FCB88D2`).
- **The `workbench` gate, the GUI-heavy subset, serially.** Command:
  `python -m pytest -m workbench -q -p no:cacheprovider`. Result:
  `610 passed, 9 skipped, 6379 deselected in 75.03s`, exit 0, no warning. This is
  the subset most likely to leave Qt state behind, and it does not.
- **Where the candidate mechanism lives, and that it is not here.** The one place
  in this repository that hands a `QStyleFactory` style to something else that
  owns it is the text tool's theme, `tools/buufury_text/theme.py`. That file, the
  whole `tools/buufury_text/` package and its tests are absent from master: they
  live on the parked `ticket/text-tool-ui-001` branch (125 files differ between
  master and that branch). A search of master's `tests/` for `buufury_text`,
  `apply_theme`, `setBaseStyle` or `QStyleFactory` matches nothing, and master's
  `tools/` holds no PySide6 GUI surface at all.

The crash therefore belongs to the text-tool line. It is owned debt about a
parked branch, not a defect reachable from master, and this ticket does not
pretend to have fixed it.

## 5. The instrument

`QT_FATAL_WARNINGS=1` was named by the retro as the cheapest next instrument. It
works on this machine, with one measured caution that has to travel with it.

- A trivial PySide6 process that calls `qWarning` once exits `0xC0000409`
  (`-1073740791`) with `QT_FATAL_WARNINGS=1`, and exits 0 without it. The
  instrument turns a warning into an abort, as intended.
- The **first** warning a Qt process with a widget or a style emits here is not a
  repository warning:

  ```text
  QFontDatabase: Cannot find font directory
  .../PySide6/lib/fonts. Note that Qt no longer ships fonts. Deploy some ...
  ```

  Under `QT_FATAL_WARNINGS=1` that environment warning aborts the process before
  any repository warning can be seen, so the instrument has to be combined with
  `QT_LOGGING_RULES="qt.qpa.fonts.warning=false"` (or the font directory deployed)
  before it can name a repository warning. A minimal application with no widget
  never reaches the font database and stays at exit 0 with the instrument on,
  which is why the caution is about widgets and styles rather than about Qt.
- A warning therefore reaches a file rather than the void: a message handler that
  writes each Qt message as it arrives captured the font warning from a process
  that then aborted under the instrument, which is the evidence that the
  instrument is usable for this question at all.
- **The two candidate mechanisms were probed directly**, three runs each, in
  `build/retro-qt-shutdown-001/probe_style_ownership.py`: pattern A,
  `QProxyStyle()` with `proxy.setBaseStyle(QStyleFactory.create("Fusion"))`, and
  pattern B, `QProxyStyle("Fusion")` naming the base instead. Plain, both patterns
  exit 0 in every run. The probe does not distinguish them, which is the same
  result the 2026-10-11 probe in `04e3fc2d` recorded, so the ownership question
  stays open rather than settled.

## 6. Debt, owned, with its reproduction

**Debt.** The exit-time native crash on the text-tool line is unfixed, and it is
mitigated rather than fixed on the parked branch. The mitigation is commit
`9e888911` on `ticket/text-tool-ui-001`: under CI the suite leaves through
`os._exit` before the interpreter tears down the Qt extensions, with
`WEBFOOT_KEEP_INTERPRETER_EXIT=1` keeping the ordinary exit path so the crash can
still be observed. That commit is not in master and, per the owner, the text tool
stays parked.

**Who owns it.** Whoever resumes merge request 224. The rule for that head is the
standing two-clean-run rule, and a clean run is exactly what the guard buys; the
crash has to be re-measured on the head being driven to merge, not inferred from a
green pipeline.

**The reproduction, as commands.** On a Linux container with the CI image, on the
text-tool line at `04e3fc2d` or earlier (before the `os._exit` guard and its
fault-handler predecessor):

```bash
python -m pip install -e ".[dev,workbench,research]"
QT_QPA_PLATFORM=offscreen python -m pytest tests/unit -q --junitxml=report.xml
```

The run reports `5242 passed, 293 skipped` and then the warning and the segfault
above. To name a repository warning instead of the environment one, add
`QT_FATAL_WARNINGS=1 QT_LOGGING_RULES="qt.qpa.fonts.warning=false"`.

## 7. Why no code change

The cause is not in master, and the fix is not on master to make: the candidate
mechanism lives in a parked branch, and the mitigation that exists is already
committed there. A change made here would be an unmeasured guess at a native
teardown fault, which is the shape of change this repository's evidence rules
exist to refuse. The instrument is proven and recorded instead, so the next
session that touches the text-tool line can name a warning rather than a
`<no Python frame>`.

There is no revert evidence to offer for this ticket: it changes no executable
behaviour and adds no test, so there is no new guard to drive to failure. What a
reviewer can falsify instead is named in the review request: the CI traces in
section 3, and the instrument probe repeated as the commands in section 5.
