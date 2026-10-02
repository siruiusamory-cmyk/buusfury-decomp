# Map layout editor verification

Editing existing map chunk layouts in the DragonByte Z Map Browser: the
verification findings and their resolutions, the independent re-measurements, and
the validation results on each revision.


## Second verification pass

The same verification pass re-inspected `e159de6ee94489afe5e0216250cf750eb787b5e9..ebdbd635f3fa3aa2414bc9d0aa769ff36fc6efd0` and reproduced each fix
independently: the null-cell revert at SDK level, through the real tab's Revert
slot, and through a full apply / leave-the-map / return / revert cycle ending in
`build() == source`; the render-failure state reset; and the re-selected map's
canvas matching the edited preview. It re-ran its Grand Kai proof, the no-op
identity check, the save-over-source refusals, the writer's cross-layer refusal
and every restriction-defeat attempt, and reported the focused set at 83 passed
with `tests/unit` at the same failure set as the base commit (six, all
environmental: five reproduced on pristine `b55701f0d0f53e1e687af7e24540e3029e7e7ab4`, plus one caused by `roms/`
being a directory junction in this worktree). **No blocking findings remain.**

Its six remaining notes and their dispositions:

| Note | Disposition |
| --- | --- |
| Review record untracked; its capture table listed a `10-*` screenshot that did not exist yet | **Fixed**: the record is committed and the re-selection capture now exists (`10-reselected-map-keeps-pending-edit.png`). |
| Read-only reason read "BG3 is the slot holds no layer" | **Fixed**: the absent-slot phrase is now "an empty slot holding no layer", and a test asserts every read-only phrase reads as a sentence after "BGn is". |
| The status bar said "EDIT LAYOUT … no changes yet" on a map the badge calls read-only | **Fixed**: the status now reads "EDIT LAYOUT · no editable layer on this map". |
| A session change left Edit Layout switched on with an empty explanation | **Fixed**: a new ROM resets to view mode and unchecks the toggle. |
| The worst-layer chunk pick is ~2.2 s because a pending edit re-renders the whole map | **Accepted as a limit.** Measured: typical editable maps preview in ~0.23 s (map:0040, after the character-block cache); the largest editable layer (map:0102 BG3, 20 chunks, 1280x1024) takes ~1.0-2.2 s. Removing it means a second, delta-based render path in the session, which this record's scope explicitly avoids. The public text says the swap "previews … immediately"; the measured spread is recorded here rather than smoothed over. |
| Unlink-before-emit on a user-confirmed target; `char_data` remains a trust-the-caller fast path; the record ledger is left to the closure pass | **Accepted deliberately**, with the reasons given above. |

## First verification pass

An independent verification pass with independent context, no part in the implementation, read the
whole `b55701f0d0f53e1e687af7e24540e3029e7e7ab4..e159de6ee94489afe5e0216250cf750eb787b5e9` diff and its surroundings and re-derived the evidence
independently (its own raw four-byte patch and its own accepted-reader render for
the Grand Kai proof; its own census; its own defeat attempts). It returned **BLOCK**
with three blocking findings and six non-blocking notes.

### Findings and resolutions

1. **[HIGH] A null-original revert raised, so "Revert cell" was dead on click.**
   `MapLayoutWriter.set_chunk_pointer` validated the replacement before noticing it
   equalled the cell's stored value, so restoring a cell whose canonical pointer is
   null raised `MapLayoutWriteError`. 104 of the 341 editable maps contain such a
   cell, and the GUI slot caught only `MapLayoutEditError`, so the exception escaped
   the slot.
   **Fixed in `ebdbd635f3fa3aa2414bc9d0aa769ff36fc6efd0`:** the writer refuses a non-int, then accepts
   `replacement == original` (a restore) before the replacement policy runs; the
   editor's revert paths translate writer and reader failures into
   `MapLayoutEditError`; the GUI's edit slots catch a named `_EDIT_ERRORS` tuple
   (`MapLayoutEditError`, `MapLayoutWriteError`, `MapBrowserError`, `WriteError`)
   with `OSError` on the save path. Tests added for a null-cell fill-then-revert at
   both the writer and the editor level, and for the sibling error family through
   Apply and Revert in the tab.

2. **[MEDIUM] `AttributeError` in a Qt slot after a render failure.**
   `_show_placeholder` left the previous map's layer/cell selection behind, so
   toggling Edit Layout on the emptied tab dereferenced a missing map.
   **Fixed in `ebdbd635f3fa3aa2414bc9d0aa769ff36fc6efd0`:** `_show_placeholder` forgets the per-map selection
   (target, slot, cell, draft, grid overlay, chooser) and re-syncs the panel, and
   the revert-button gate no longer dereferences a missing map. Regression test
   added.

3. **[MEDIUM] Re-selecting a map lost its pending edits on the canvas.**
   The selection path restored the cached unedited render while the change list,
   the chooser tags and the saved ROM all carried the edits, contradicting the
   public claim that the swap previews immediately.
   **Fixed in `ebdbd635f3fa3aa2414bc9d0aa769ff36fc6efd0`:** the selection path ends in `_refresh_preview()`, so a
   map with pending edits re-renders from the session. Regression test added, and a
   re-selection step was added to the visual QA walkthrough.

### Notes and dispositions

- The chooser's error guard did not cover thumbnail expansion (`mb.rgba`).
  **Fixed**: thumbnail expansion is inside the same guarded block.
- `char_data` is a public parameter trusted on `isinstance(bytes)` alone.
  **Kept, documented**: it is the preview/chooser fast path, the editor is its only
  supplier, and the docstrings now state that it must be the block for the same map.
- `render_chunk_images` re-decoded the character block on every call (measured
  1.26 s to refill a 20-chunk layer, cold pick ~2.5 s).
  **Fixed**: `MapLayoutEditor.character_block` is public and the chooser passes the
  session's cached block through `render_chunk_images(..., char_data=...)`.
- `#010X` versus the repository's `#010x`.
  **Fixed** in the three sites.
- An existing output is unlinked before the emit, so a failed emit leaves neither
  file. **Kept, accepted as a limit**: this is the established
  `build_panel.py` convention (its overwrite flow deletes then rebuilds), and
  `emit_image`'s refuse-to-overwrite property is what makes a second save fail
  closed at SDK level.
- No record-ledger update and no UI-QA record in the frozen tree.
  **Partly addressed**: this record carries the UI-QA result. `docs/records/the working queue`
  and the archive closeout are deliberately left to the human's closure pass, which
  owns the record lifecycle in this repository.

## What the verification pass confirmed independently (not taken on trust)

- Census: 452 maps readable, 341 with an editable layer, 111 read-only.
- The Grand Kai proof case: `map:0040` dominant layer 1 cell 0
  `0x082928DC` -> `0x08292A54` at file `0x00292CA0`; only bytes `0x292CA0-1`
  changed; 29,208 changed pixels, all inside that cell's 256x256 region, 0 in the
  other three chunk regions of the layer, and BG0/BG2/BG3 pixel-identical.
- No-op save byte-identical (bytes and SHA-256) and structurally guaranteed.
- Save over the source ROM refused via absolute path, relative path and a file
  symlink; a second save to one output refused with the first file intact;
  hard-linking the source cannot modify it.
- All restriction-defeat attempts refused: cross-layer, null, boolean, negative,
  over-32-bit, out-of-range cell, non-editable layer, Map 19 (both its dominant and
  its terrain slots), map index 452, a non-canonical image, and an override aimed at
  a terrain layer.
- Canonical ROM unchanged (8,388,608 bytes, SHA-256 `940ad5f0…f059e`, size and
  mtime identical before and after).
- `git diff --check` clean; added lines bare-LF; no ROM, save, state, generated ROM
  or generated PNG in the diff; no CLI path exposes the write.

## Visual and interaction QA

Run on the real windows platform plugin (the offscreen plugin has no font database
here, so every label renders as tofu boxes and its screenshots are worthless for
judging text). The harness drives the real `MainWindow`, opens the real canonical
ROM through the real Atlas tab, and walks the workflow with real clicks
(`QTest.mouseClick` on the chunk grid). Screenshots are captured under the ignored
`build/qa/map-layout-editor/` and were opened and inspected:

| Capture | State |
| --- | --- |
| `00-empty-no-rom.png` | no ROM open (empty state) |
| `01-normal-read-only-browser.png` | normal read-only browser |
| `02-layout-edit-mode.png` | edit mode with the chunk grid over the map |
| `03-selected-chunk-cell.png` | a chunk cell selected by a real click |
| `04-chunk-chooser.png`, `04-chunk-chooser-panel.png` | chunk chooser with thumbnails |
| `05-live-replacement-preview.png` | live in-memory replacement preview |
| `06-unsaved-change-state.png`, `06b-unsaved-two-changes.png` | unsaved-change state |
| `06c-narrow-window.png` | resized narrow |
| `07-map19-read-only.png` | Map 19 read-only state |
| `08-save-as-result.png`, `08b-save-as-dialog.png` | successful Save As |
| `09a`/`09b` | the emitted file's own bytes re-rendered, canonical versus edited |
| `10-reselected-map-keeps-pending-edit.png` | a map re-selected with pending edits still shows them |

Defects the pass found and fixed before the freeze:

1. The chooser elided the `current`/`original` state tag: a `QListWidget` in IconMode
   with uniform item sizes is sized from the first item, so an item whose text grew a
   second line was clipped. Fixed with per-item size hints derived from the real font
   and non-uniform item sizes.
2. A long `READ ONLY` reason clipped instead of wrapping in the badge. Fixed by
   keeping the badge to a short state and moving the explanation into a separate
   wrapped, recessive label.
3. An empty layer combo box was shown for a map with nothing editable. Fixed by
   hiding the row.
4. Ghost layer checkboxes from the previous map painted over the new ones: removing a
   widget from a layout does not unparent it, so a `deleteLater` widget still paints
   at its stale geometry until the deferred delete runs. Fixed with `setParent(None)`.
5. The status line did not mention an unapplied chooser pick. Fixed: it now reads
   "previewing an unapplied choice".

Known UI limits, not fixed because they are pre-existing shell behaviour or outside
this record's scope: the window's minimum height is 1264 px on this machine, which is
identical on the reviewed base commit (it comes from other tabs, not this feature);
at very narrow widths the map list is squeezed by the canvas toolbar; only the
accepted renderer's transparency (index 0) is shown as canvas checkerboard.

Interaction QA is the automated suite in `tests/unit/test_workbench_map_browser.py`
(real widget tree, duck-typed edit session) plus the ROM-gated
`tests/integration/test_map_layout_editor_rom.py`.

## Validation on revision `ebdbd635f3fa3aa2414bc9d0aa769ff36fc6efd0`

- Focused map and workbench set: **90 passed, 2 skipped** (both skips are the
  MAP-VIS-001 VRAM oracle, unconfigured locally).
- Full `pytest tests` gate on `ebdbd635f3fa3aa2414bc9d0aa769ff36fc6efd0` (the state this run imported; measured, not
  derived): **6 failed, 2953 passed, 19 skipped in 5126 s (1:25:26)**. The six
  failures are all environmental and are not caused by this change: five
  (`test_asset_export_output_safety.py` x4 and
  `test_mgba_capture.py::test_capture_output_is_restricted_to_ignored_build_tree`)
  reproduce identically on the pristine base commit `b55701f0d0f53e1e687af7e24540e3029e7e7ab4` in a separate
  worktree, and the sixth
  (`test_project_safety.py::test_proprietary_and_generated_paths_are_git_ignored`)
  fails only because `roms/` is a directory junction in this worktree, so
  `git check-ignore` exits 128 with "pathspec is beyond a symbolic link";
  `.gitignore` and `roms/` are untouched by the diff. The 19 skips are the
  documented ROM-oracle, capstone-presence and curation-basetemp conditions,
  including the two MAP-VIS-001 VRAM oracle skips.

## Validation on revision `34da3c938e093ee99e9ba07f7f16bd1aff92f70c`

The polish delta is three local state changes, each covered by its own test:
**63 passed** across the four unit files `tests/unit/test_map_layout_edit.py`,
`tests/unit/test_workbench_map_browser.py`, `tests/unit/test_map_browser.py` and
`tests/unit/test_workbench_smoke.py`; and **89 passed** across those four plus
`tests/unit/test_workbench_session.py` and the three ROM-gated files
`tests/integration/test_map_layout_editor_rom.py`,
`tests/integration/test_map_layout_write_rom.py` and
`tests/integration/test_map_browser_rom.py`. The verification pass reproduced both numbers
itself and bounded the blast radius independently (`_READ_ONLY_FORMS` is referenced
only by the session module and the two unit test files; `_reset_editor` has one call
site; `_update_status` and `_show_edit_groups` are tab-internal), which is why the
long suite gate was not rerun for that delta. The gate below ran against `ebdbd635f3fa3aa2414bc9d0aa769ff36fc6efd0`.
- Pre-existing environment failures, reproduced on the pristine base commit
  `b55701f0d0f53e1e687af7e24540e3029e7e7ab4` in a separate worktree, are unrelated to this change:
  `tests/unit/test_asset_export_output_safety.py` (4) and
  `tests/unit/test_mgba_capture.py::test_capture_output_is_restricted_to_ignored_build_tree`.
  A sixth failure appears only in a worktree where `roms/` is a directory junction
  (`git check-ignore` refuses a path beyond a link), so it is a worktree artefact,
  not a code defect.
- `npm run check`: 0 errors, 0 warnings, 0 hints. `npm run build`: passed, and the
  built page carries the new capability text.

## Product-safety correction

Human acceptance accepted the implementation except for two product-level issues,
fixed in `15dcb1bbd70b62b9480bed9b15b100fda22b988b` and `0ed03a406eb479faf0364db10b57dc1bf00efb5b` and `4e42c901060b41aa7fbf358406c2d0d8642bbc67` on the same branch:

1. **DragonByte Z could not reopen its own output.** The Map Browser renders the
   canonical image only, so an emitted derivative was refused. Save As now writes a
   provenance manifest beside the image (the project's existing write-manifest
   document shape), and the Atlas open accepts a modified image only when that
   provenance proves it is the canonical image plus declared, policy-legal layout
   edits: canonical base SHA-256 and the profile *of that image*, the file matching
   the declared output digest and byte count, every declared change being a
   four-byte dominant-layer field named by its own `map:NNNN layer S cell C` owner
   whose replacement the layer already uses elsewhere, and - the decisive check -
   restoring the declared old values reproducing the canonical image by SHA-256,
   which bounds an accepted derivative to the canonical image plus exactly its
   declared fields and needs no copy of the canonical file. An accepted derivative
   renders its edited layout from the reconstructed canonical bytes with the
   verified edits applied through the same override path the editor previews with,
   and stays read-only. The canonical image is still accepted by identity before any
   manifest is consulted; an image with no manifest, a mismatching manifest, or a
   manifest declaring anything outside those rules is refused with the reason
   stated.
2. **Save As could destroy an existing destination.** The image and its manifest are
   now built at temporary sibling paths, verified there, and only then moved onto
   the requested destinations, so a failed emit, a failed verification or a failed
   publish leaves whatever existed at that path byte-for-byte intact and no
   temporary file behind. Every path a save touches - the requested output, the
   manifest, and both staging names - is resolved and refused against the source
   before anything is deleted or emitted.

### Correction verification

A fresh verification pass inspected only the correction: provenance-aware reopening,
arbitrary-modified-ROM rejection, existing-destination failure safety, canonical-path
regression and the exact changed surface.

- **First pass: BLOCK**, one HIGH finding - `save()` guarded only the requested
  output against the source, so a source file named after a derived path (the
  manifest name, or either staging name) could be replaced or deleted by a save.
  Reproduced with two concrete collisions. Fixed in `0ed03a406eb479faf0364db10b57dc1bf00efb5b`; the verification pass then
  reproduced both collisions as refused with the source byte-identical, and added
  its own symlink and directory-junction alias attempts, all refused.
- Its six non-blocking notes were also cleared in `0ed03a406eb479faf0364db10b57dc1bf00efb5b`: the manifest's base
  profile must now be the profile of the canonical image (a canonical base naming
  Legacy of Goku's profile was previously accepted and relabelled the image in the
  Atlas tab); the schema version must be an integer; the declared changed-byte count
  must match the manifest's own changes; the field offset comes from
  `MapLayoutWriter` rather than a second copy of the format arithmetic; a failed
  manifest publish is reported as an image written without provenance; a refused
  open states the identification reason before the provenance reason.
- **Second pass: APPROVE WITH NON-BLOCKING NOTES**, with two new LOW items from the
  fix delta itself, both cleared in `4e42c901060b41aa7fbf358406c2d0d8642bbc67`: a failed final publish left the
  staging files behind, and the verifier hashed the whole image once per declared
  edit (now one writer per check: verification of a 20-edit derivative measured at
  175 ms instead of about 1.4 s).
- **Final delta confirmation: APPROVE WITH NON-BLOCKING NOTES**, no blockers, and
  the verification pass's own re-runs (85/0 and 38/0 harness checks, focused set 107 passed,
  remaining ROM-gated set 81 passed/3 skipped, `pytest tests/unit` at the same six
  environmental failures as before and none new).

### End-to-end QA (real application, real platform plugin)

`build/research/qa_closeout.py` drove the required user flow on the real Windows
platform plugin and its captures were opened and inspected: open the canonical ROM,
map:0040, Edit Layout, change the proven cell, Save As, leave the source image, open
the emitted ROM through the normal Atlas open flow, select map:0040 and see the
edited layout (confirmed programmatically as differing from the canonical render),
with the source ROM hash unchanged throughout. The refusals were driven through the
same open flow and each captured: a one-byte-mutated canonical image with no
provenance, a derivative whose bytes no longer match its manifest, a manifest
claiming a terrain-field edit, an untouched canonical image accepted again
afterwards, and a failed Save As over an existing destination with the destination
preserved and no staging file left behind.

### Carried notes (not fixed, none blocking)

- `verify_authored_rom` returns an `AuthoredRom` whose `profile_id` could contradict
  its `canonical_sha256`; the binding is enforced in `Session`, its single consumer,
  and documented by the field. Enforcing it in the verifier too would be defence in
  depth.
- No committed test drives the manifest-rename failure specifically; the
  image-rename case is covered by a test and the manifest case was verified by
  probe.
- The editor can hold two semantic pending edits for one physical field when two map
  indices share one dominant layer record; Save As then refuses through its
  byte-plan cross-check. The provenance format cannot express that state, so it
  fails closed rather than writing.
- A derivative has no scene or text domain of its own, so the Maps, Map and Scene
  tabs show nothing for it; the Map Browser renders it, which is what this record
  requires.
