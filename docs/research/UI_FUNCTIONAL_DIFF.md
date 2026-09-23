# Functional diff, DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001

The question this answers: **what behaviour changed besides presentation?**

Method: `git diff` over the ten changed production modules, read line by line for
any line that reads state, chooses a path, calls the SDK, or writes anything -
as opposed to a line that sets a colour, a metric, a metric's policy, a tooltip,
an accessible name, or a widget's visibility.

Baseline `ad3c0226eea902be1c983922274fffbca9794f9c`. Candidate uncommitted in
`<temp>\log1-remake-dbz-visual-001`.

## PRESENTATION CHANGES (the overwhelming majority)

Everything below changes only how an existing decision is *drawn*:

- One application-wide theme (`theme.apply_app_theme`) replaces the Map Browser's
  scoped style sheet and the literal hex strings in a handful of labels. No widget
  gained or lost a decision; they gained one palette.
- Menu bar, global toolbar and one status bar added to the shell. Their actions
  call the **existing** slots: `AtlasBrowserTab.open_rom_dialog` (extracted from
  `_on_open_rom` with its body unchanged), `BuildPanelTab.open_project_dialog`
  (extracted from `_on_open_project` with its body unchanged),
  `BuildPanelTab.validate_project` / `build_project`, and
  `LauncherTab.launch_built_rom`.
- Panel headers, tool strips, disclosure rows, state chips and scroll panes
  replace `QGroupBox` frames and bare label rows across all eight tabs.
- Row heights, margins, spacing, radii, borders, selection fills, disabled
  treatment, focus rings, table header styling, splitter handles and scrollbars.
- The Map Browser's layout was re-arranged: map collection left, dominant canvas
  centre, one tabbed inspector right, chunk palette under the canvas, one status
  line. Every widget the old layout held is still held and still wired to the same
  slots.
- The layer visibility controls moved from a row of labelled check boxes into a
  menu owned by one `QToolButton`. The **controls themselves are the same
  `QCheckBox` objects**, still in `_layer_checks` keyed by layer slot, still
  connected to `_show_composite`; only their parent changed.
- `GraphicsTab._preview` / `_anim_preview` lost their `StyledPanel` frame.
- The Graphics browser/inspector splitter was given explicit initial sizes.
- New: panel headers say "MAPS", "INSPECTOR", "CELL CHUNKS", "OUTPUT" etc. where
  before there was an untitled frame or a `QGroupBox` title.

## BEHAVIOR CHANGES

There are **six**, all small, all deliberate, and none of them in the domain
layer. Each is listed with what it does and why.

1. **The window's minimum size is now 820×560 instead of ~1090×1246.**
   *Was:* the shell inherited the deepest control's minimum, so the window could
   not be resized below a tall monitor's work area. *Now:* each tab's content
   keeps its own minimum inside a scroll pane, and the shell declares a floor of
   820×560. *Why:* tiling the application beside anything was impossible.
   *Evidence:* the baseline forces its captures to 1172×1608 at a requested
   1440×900; the candidate honours the request.

2. **Each scroll pane enforces its content's minimum height.**
   *Was:* a tab compressed its own children when the window was short, which made
   the Graphics tab's animation preview and status line occupy the same pixels.
   *Now:* `ScrollPane` sets the content's hard minimum and its own, so the pane
   scrolls instead of deforming. *Why:* overlapping widgets are a defect, not a
   compact layout.

3. **The Map Browser keeps a fitted map fitted on resize.**
   *Was:* `fitInView` ran once; a later resize left the map at a stale zoom.
   *Now:* `MapCanvasView.resizeEvent` refits **only while the view is in its
   fitted state**, and a manual zoom (`zoom_in`/`zoom_out`/wheel) clears that
   state so a chosen zoom is never overridden. *Why:* a fit computed before the
   viewport reached its final size is wrong, and the baseline showed the map as a
   small patch in a large canvas.

4. **The Map Browser's chunk palette collapses to its header when the open map
   has no editable layer.** *Was:* the palette stayed open and empty. *Now:* the
   header remains (so the control does not move and stays discoverable) and its
   body is hidden. *Why:* an empty palette was dead space that repeated the
   inspector's own explanation.

5. **The Map Browser reports five facts it did not report before**, each of which
   is new information rather than new behaviour: the open map's **name** in the
   status line; a **live hover readout** (`X, Y px · cell n of m (col, row) ·
   Chunk k`) driven by `MapCanvasView.mouseMoveEvent`/`leaveEvent`; a **glyph on
   the map list row** of a map that has pending edits; a **pending-edit count in
   the window title**; and a `dirtyChanged` signal the shell reads. It
   simultaneously **stopped** reporting the map's pixel dimensions and graphical
   layer count in the status line, because the Map inspector already states both.
   *Why:* the ticket requires pending/unsaved state to be visible through more
   than colour, and requires the same fact not to appear twice on one screen.

6. **`AtlasBrowserTab` grew an `on_session_changed` method** that re-reads
   `session.rom_path`/`profile`/`authored` into its identity chip, and the shell
   connects it to `romOpened`. *Was:* the chip was written only by this tab's own
   file dialog, so a ROM opened any other way left it reading "No image open"
   while the status line said the ROM was loaded, a contradiction visible in the
   review captures. *Why:* the chip is the one thing on that surface that states
   which image is open.

## NOT CHANGED, verified, not assumed

| Concern | Position |
|---|---|
| ROM source selection | `Session.open_rom` untouched. `identify_rom`, the SHA-256 catalog match, the atlas load and the derivative path are byte-for-byte the baseline. |
| Map selection | `_on_selection` / `_load_map` / `_on_map_changed` bodies untouched. |
| Map rendering | `mb.render_map`, `mb.compose`, `mb.rgba`, `mb.render_chunk_images` call sites and their arguments untouched, including `chunk_overrides` and `char_data`. The render cache and its bound are untouched. |
| Edit-layout entry/exit | `_on_edit_mode_toggled`, `_show_edit_groups`, `_install_grid_item` logic untouched; the mode still starts off and a session change still leaves it. |
| Chunk-cell selection | `_on_cell_clicked`, `_move_cell_selection`, `_on_canvas_key` untouched; arrow-key navigation, Enter and Escape behave identically. |
| Chunk replacement | `_apply_draft`, `_working_pointer`, `_preview_overrides`, `_refresh_preview` untouched; `MapLayoutEditor.set_cell` is called with the same arguments. |
| Pending edit state | `_unsaved_count`, `_saved` bookkeeping and `MapLayoutEditor.edits()` untouched. |
| Revert / reset | `_revert_cell`, `_reset_edits` untouched; their status wording is unchanged. |
| **Save As** | `_on_save_as` body untouched, including `is_safe_output_path(chosen, self._session.rom_path)`, the `_apply_draft()` before emit, the `MapLayoutEditor.save(chosen, source_path=…, profile_id=…)` call, and the refusal dialog's wording. |
| Output-path selection | `_default_output_path` untouched. |
| Provenance | `tools/webfoot/authored_image.py` and `map_layout_provenance.py` are not in the diff at all. |
| Derivative reopening | `Session._verify_derivative`, `AuthoredRom`, `layout_overrides` untouched; a derivative still renders the reconstructed canonical bytes and stays read-only. |
| Validation / build | `BuildPanelTab._refresh`'s four `setEnabled` calls are unchanged in condition; the new stage chip only *reads* the same three predicates. `validate_project` / `build_project` untouched. |
| Launch | `LauncherTab._launch` untouched; `subprocess`, the mGBA field and the built-ROM field are unchanged. `on_session_changed` gained a label update and an enable rule that reads the same `last_build`/field text it already read. |
| Session state | `session.py` is **not in the diff**. |
| Read-only gating | `MapLayoutEditor.target(...).editable` and `read_only_kind` drive the same badge/detail/button states; the strings are byte-identical. |

## Position

**BEHAVIOUR CHANGES: the six above.** Five are presentation-adjacent (window
floor, scroll-pane minimum, refit-on-resize, palette collapse, Atlas identity
refresh). One adds new *reported* state without changing any decision.

**No change to** capability states, map-edit semantics, provenance, Save As,
derivative trust, source immutability, ROM writes, supported map counts, or
authoring limits. `public API`, `capabilities.json` and `project.ts` are
untouched.

**No functional regression was found by the test suites that could be run** (see
`FUNCTIONAL_DIFF.md`'s companion in the review index for the focused results and
the two suites that could not be run in this worktree).
