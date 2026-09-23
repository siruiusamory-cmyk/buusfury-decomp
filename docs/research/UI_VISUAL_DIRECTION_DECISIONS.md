# DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001 review

```text
CODE REVIEW

Verdict: APPROVE WITH NON-BLOCKING NOTES

Scope reviewed:
- frozen candidate 13d2ab207f92f7df547651d38433a2bac592302a against parent
  ad3c0226eea902be1c983922274fffbca9794f9c (35 files, +7912/-598)
- all 13 workbench modules in the diff, the 4 changed/new tests, the 6 UI
  research documents, the 12 new tools/qa harnesses
- all 24 final captures in <temp>\dbz-visual-pass\light (plus a labelled
  status-bar sheet rebuilt from all 24), palette-comparison-buu.png,
  comparison-light\ and three of its sheets
- ROM/provenance/SDK paths outside the diff, and the canonical ROM hash

Blocking findings:
- none

Non-blocking findings:
- [NONBLOCKING] tools/webfoot/workbench/atlas_browser.py:61,131 - Atlas still
  draws its own status row inside its body while the shell mirrors the identical
  string, so one sentence renders twice on one screen. This contradicts the
  candidate's own claim of "one physical status bar", UI_FUNCTIONAL_DIFF.md and
  UI_REFERENCE_FIDELITY_MATRIX.md ("No second status row"), and the accepted
  "one physical status bar" direction.
  Evidence: `_load_status` is parented to AtlasBrowserTab, is in that tab's
  layout, and reports hidden=False / visible=True; it reads "No ROM loaded." in
  01-shell-no-rom.png at y=83 and y=881, and "profile buus_fury_usa_rev0_01c1707f"
  in 13-atlas-rom-open.png and 18-narrow-shell-atlas.png at both rows. There is
  exactly one QStatusBar, so the second row is the editor's, not a second bar.
  Impact: a redundant status row on one editor; no functional effect, no other
  editor is affected.
  Required fix: hide `_load_status` as the Graphics, Maps, Scene and Inspector
  labels already are (the shell owns the one status line).

- [NONBLOCKING] tools/webfoot/workbench/graphics_tab.py:203-209 - the new
  index-0 transparency pass in `indexed_pixmap` is a pure-Python per-pixel loop,
  measured at 2.5 Mpx/s against the parent's C++ `copy()`. map:0019's composite
  (3584x2560, 9.2 Mpx) costs 3.17 s versus 0.017 s in the parent, roughly 190x
  slower; ten maps exceed 1 Mpx. `map_tab.py:638` calls this helper for the
  Objects-mode canvas, so switching to a large map blocks the UI thread for
  seconds. Correctness is unaffected and the transparency decision itself is
  right (it matches the SDK's own `mb.rgba` index-0 convention, and a spatial
  check found no isolated interior index-0 pixels in five real maps), but
  UI_FUNCTIONAL_DIFF.md claims map rendering is untouched.
  Impact: a responsiveness regression introduced by this pass, on the largest
  maps only.
  Required fix: replace the per-pixel loop with a QImage colour-table or
  mask-based conversion.

- [NONBLOCKING] docs/research/UI_BUU_SPRITE_COLOR_SOURCE.md:110,120,150,168 - the
  document disagrees with the code it is cited as sourcing. `accent_pressed` is
  documented `#7d0f41` but ships `#6d0c3c`; `grid`/`marker_retail` are documented
  `#a81560` but ship `#b81f6b`; `preview` is given as `#e2dce0` in one place and
  `#e8dae1` in its own table row; and the `accent_ink on accent` ratio is stated
  as 6.09:1 (white on the previous accent) where the shipped pair computes
  7.14:1. Nineteen of the twenty documented contrast ratios reproduce exactly.
  Impact: the provenance document is the evidence for the palette, so stale
  values in it undermine the audit trail rather than the product.
  Required fix: correct the four values and the one ratio.

- [NONBLOCKING] docs/research/UI_BUU_SPRITE_COLOR_SOURCE.md:171-178 and
  tools/webfoot/workbench/theme.py:178 - `research: #6b3fa0` is described as
  coming from "the sprite's cape violet" and as needing "no exception either",
  but the reproduced 24-entry sprite palette contains no violet and the value is
  55 degrees from the nearest sprite hue. It is a second undocumented exception
  beside the honestly documented green.
  Impact: provenance accuracy only.
  Required fix: list `research` as a second documented exception.

- [NONBLOCKING] docs/research/UI_HUMAN_REVIEW_INDEX.md:3,16-18,28-36,101-108 -
  the committed index describes a superseded capture set. It says "Not frozen,
  not staged, not committed" (it is in the frozen commit); it points at
  after-contact-sheet.png, after\ and comparison\ rather than the final light\
  (24 PNGs) and comparison-light\ (17 sheets); it names 14-build-surface, which
  no longer exists (the state is 14-build-action, which is also why there is no
  compare-14 sheet); and it calls a deviation a "black band" that is mauve in the
  final 09 capture.
  Impact: reviewer-facing documentation does not describe the frozen artifact.
  Required fix: re-point the index at the final capture set.

- [NONBLOCKING] docs/research/UI_FUNCTIONAL_DIFF.md:10-11,38,102 - stale against
  the frozen revision: "Candidate uncommitted" (it is committed), `_anim_preview`
  listed as present (removed), "Map rendering ... untouched" (see the timing
  finding), and the index-0 transparency change is absent from its behaviour list.
  Impact: same as above.
  Required fix: update to the frozen revision.

- [NONBLOCKING] Test gap: no test exercises `_show_surface_dialog`,
  `open_build_report` or `open_run_configuration`, so the re-parenting that moved
  Build and Run out of the editor stage has no automated guard.
  Impact: a future regression in the action-surface wiring would not be caught.
  Required fix: add a focused test asserting a dialog parent, the expected
  controls, and that the active editor and status are unchanged after opening.

- [NONBLOCKING] tools/webfoot/workbench/map_browser_tab.py:122-124,1781 -
  comments still describe the edit state as "gold" while
  `_MODE_COLORS["edit"]` is `accent`.
  Impact: stale comment from the superseded colour direction.

Notes:
- [NOTE] app.py defines `current_editor_name` twice with identical bodies; the
  first is dead code.
- [NOTE] `_show_surface_dialog` re-parents the surface out of `_stage_layout`
  (measured layout count 7 -> 5 after the first open). Both surfaces are hidden
  outside a dialogue and none of the visible editors is affected, so there is no
  visible defect, but the stage permanently loses those pages.
- [NOTE] The claimed 720x560 dialogue ceiling is a preference, not a cap: Qt will
  not shrink a dialogue below its content minimum (measured 788x340 offscreen).
- [NOTE] `_release_status` disconnects `host` and `host.status_label()` but not
  `host.signal_source()`, so stale `statusChanged` connections accumulate across
  editor switches. The `_status_emitters` identity check keeps behaviour correct.
- [NOTE] Beyond presentation the pass adds newly *reported* facts (canvas hover
  readout, per-map dirty glyph, unsaved count in the title, map name in the
  status line). These are disclosed in UI_FUNCTIONAL_DIFF.md and move no
  capability-registry state.
- [NOTE] tools/qa/overlap_probe.py lays the Build and Run surfaces out as stage
  pages for its states 14 and 15, so its "0 problems across 16 states" does not
  cover the shipped dialogue geometry.
- [NOTE] tools/qa/visual_pass_capture.py hardcodes a machine-local default ROM and
  atlas path (both environment-overridable) and the canonical SHA-256; the ROM is
  hash-verified before use and never written, and all QA output goes to temp dirs.
- [NOTE] docs/research/UI_GAME_COLOR_SOURCE.md has a typo (`\theme.py`). The file
  is correctly banner-marked SUPERSEDED.
- [NOTE] The docs/DEVELOPMENT.md `public progress impact` classification is a closure-time
  item and is not recorded in the candidate. The underlying facts are verified:
  src/data/capabilities.json and project.ts are byte-unchanged.

Report-claim spot-check (the review tested three specific claims rather than
accepting the ticket report):

1. "One physical status bar, no editor draws its own duplicate status row" -
   NOT SUPPORTED as worded. There is exactly one QStatusBar and the Graphics,
   Maps, Scene and Inspector labels are correctly hidden, but the Atlas editor's
   own row renders the identical string. See the first non-blocking finding.
2. "ROM-only status reads no project at every width and in every editor" -
   SUPPORTED for the captures. A labelled sheet of the bottom 24 px of all 24
   PNGs was rebuilt and read: 13 (1440x900), 16, 17 and 18 (1100x720) all read
   `no project`; 01 reads `no ROM`; the captures taken with the project open
   (10, 11, 12, g2-g8) read `not validated | not built`, which matches the state
   sequence the capture script drives. Residual gap: no ROM-only capture exists
   for Graphics or Inspector.
3. "Build and Run open content-sized dialogs and Atlas is not replaced" -
   SUPPORTED. 14 is a 542x350 dialogue and 15 a 480x326 dialogue, both grabbed
   from the live modal dialogue. Independently, each was opened twice through
   `open_build_report`/`open_run_configuration`: the parent is a QDialog, all
   Build (5) and Run (3) controls are present and correctly enabled, the second
   open is identical, the active editor is Atlas before and after, and the shell
   status text is unchanged. `_show_surface_dialog` never calls `show_editor`
   or `_show_host`.

Correctness:
- PASS. The accepted IA, action ownership and state model are implemented as
  described, with the two presentation caveats above.

Architecture/product alignment:
- PASS. No new capability, no registry movement, no IA change beyond the
  accepted consolidation.

ROM/data safety:
- PASS. Canonical ROM SHA-256 940ad5f0...059e matches the harness constant and
  its mtime predates the work; the harness hash-checks before opening; derivative
  and extracted outputs are written under tempfile.mkdtemp and removed; no
  source-ROM write path exists in the diff; session.py, authored_image.py and
  map_layout_provenance.py are untouched.

Determinism:
- PASS. Status text, palette resolution and capture states are pure functions of
  session and window state.

Tests/evidence:
- PASS with the coverage gap noted. Project-status tests call the real
  `_project_state_text` with a real Session and do not re-implement production
  logic; the three modified visual tests were re-pointed for genuinely removed
  widgets (second preview, tab strip) and each replacement is at least as
  strong, with none weakened to hide a failure.

Compatibility:
- PASS. No dependency, format or CLI change; no generated imagery dependency added.

Maintainability:
- PASS. Theme roles are centralized (no `#rrggbb` literal outside theme.py; every
  role lookup resolves). Duplicate function and stale comments noted.

Public-release hygiene:
- PASS. No src/, site or capability data in the candidate; no generated imagery
  committed (captures live under C:\tmp); the em-dash and markdown-fence
  violations raised by the repository's pre-commit scan were corrected before
  the freeze rather than bypassed.

Reviewer validation performed:
- git diff --stat / show --name-status / diff --check (clean, exit 0); single
  commit 13d2ab2; worktree clean.
- pytest tests/unit/test_workbench_project_status.py -q -> 14 passed.
- pytest -m "fast and workbench" -q -> 148 passed, 3 skipped, 3051 deselected.
- pytest test_workbench_graphics.py test_workbench_map_tab.py
  test_workbench_map_browser.py test_workbench_smoke.py -q -> 87 passed, 1 skipped.
- pytest test_project_safety.py test_workbench_session.py -q -> 9 passed,
  2 skipped.
- python -m compileall -q tools/webfoot/workbench tools/qa -> exit 0.
- python -m tools.qa.buu_sprite_palette -> graphic:903 top-ranked, 24-entry
  palette matching the document.
- python -m tools.qa.overlap_probe -> 0 problems across 16 states, reproduced.
- Custom probes: theme role-name resolution; WCAG ratios (19 of 20 documented
  figures exact); hue provenance against the sprite palette; shell status-row
  ownership; `_project_state_text` across six states; Build/Run dialogue
  round-trip twice; `indexed_pixmap` timing on three real map geometries;
  composite index-0 spatial analysis on five real maps; a survey of all 452 maps.

Remaining uncertainty:
- The full suite was not run; it is the CI gate.
- The on-screen result of the index-0 change for the largest map cannot be
  checked against a capture, because no Objects-mode capture of map:0019 exists;
  that conclusion rests on SDK-level pixel analysis plus the timing measurement.
- Per-layer render cost in the Objects workspace was not measured end to end.
- Dialogue geometry has no overlap/clipping probe coverage; it was verified by
  control inventory rather than pixel inspection.
- Three of the seventeen comparison sheets were opened; the rest were not.
- The external upstream references cited in UI_REFERENCE_MATRIX.md were not
  re-verified against those projects' sources.
```

Reviewed frozen candidate `13d2ab2`. Verdict: **APPROVE WITH NON-BLOCKING NOTES**;
no blocking findings, so the candidate stands as frozen. The non-blocking list is
led by two items worth a follow-up: the Atlas duplicate status row (a stated
acceptance criterion that is not fully met) and the `indexed_pixmap` timing
regression on the largest maps. Neither invalidates the accepted visual
direction, and neither was corrected here, because the reviewer must not edit a
frozen candidate.
