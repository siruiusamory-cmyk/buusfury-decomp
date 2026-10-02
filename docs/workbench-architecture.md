# Workbench architecture

DragonByte Z is the desktop editor shipped from `tools/webfoot/workbench/`. Run
it with `python -m tools.webfoot.workbench` (`workbench/__main__.py`). It is a
second client of the Webfoot SDK the CLI uses, not a separate implementation of
anything the SDK already owns.

This is the architecture contract for that package: the thin-client boundary,
the shared state model and its signals, the editor composition, the error
handling rule with the catch lists that implement it, the authoring discipline,
and how the package is accepted. For the Maps editor's Layout mode and for
reopening a ROM this editor wrote, see [workbench.md](workbench.md); neither is
repeated here.

## The thin-client boundary

The Workbench computes no ROM-format values. It holds paths and the values the
SDK returns, and calls public SDK functions for everything about ROM semantics.

- `session.py` states the rule for the shared model: no bitfield masks, no
  offset literals, no record-type constants. A ROM is identified by SHA-256
  through `rom.identify_rom` (`session.py:246`), the same path the CLI uses.
- `atlas_browser.py` hands phrases and offsets to `atlas.search_text`,
  `atlas.addr` and `atlas_build.parse_offset` and renders what they return.
- `inspector.py` keeps dialogue resolution, validation, persistence and retail
  decoding behind `tools/webfoot/dialogue.py`.
- `build_panel.py` keeps every ROM-format decision behind
  `build.extract_project`, `build.validate_project` and `build.build_project`,
  and renders the `ValidationReport` / `BuildResult` those return.
- `launcher.py` has no ROM-format knowledge: the built image path comes from
  `session.last_build.output_path`, the emulator path from `shutil.which` or a
  saved override.

**Rule.** If a widget is about to compute a ROM value, that logic belongs in the
SDK behind a public function. Add it there and call it from the widget.

**Corollary.** Call a public Python API; never shell out to the CLI and parse
its stdout. `tools/webfoot/dialogue.py` is the pattern for exposing a domain
capability to a GUI: semantic identity in (`resolve_dialogue_target`,
`get_dialogue_original`, `get_dialogue_replacement`,
`validate_dialogue_replacement`, `set_dialogue_replacement`,
`remove_dialogue_replacement`), and no handles, compression, container offsets
or project TOML at the call site.

## Session and shared state

`Session` (`session.py:80`) is one plain dataclass that every editor reads and
writes. `MainWindow.__init__` builds exactly one `Session` and one
`RomProfileCatalog` and passes both to each editor by constructor
(`app.py:78-127`). There are no module globals and no singleton accessor.

The fields worth knowing before adding state:

- the open image: `rom_image`, `profile`, `identification`, `authored`,
  `provenance_error`;
- the SDK domains loaded from it: `atlas`, `decoded_text`, `maps`,
  `text_strings`, and the lazily built `sprites` corpus behind the `sprites`
  property (`session.py:121-140`);
- what the user is working on: `selected_map`, `selected_result`, `project_dir`,
  `output_dir`;
- the authoring counters: `project_revision`, `validation_revision`,
  `build_revision`, `last_build`.

Opening an image goes through `Session.open_rom` (`session.py:205-241`), which
is **total** over the SDK's declared failure families: every expected failure
leaves as `SessionError` or its subclass `RomNotRecognizedError`, so a surface
catches one type at the click. A non-canonical image is accepted only as a
verified DragonByte Z-authored derivative (`Session._verify_derivative`,
`session.py:353-358`), and `map_image` then returns the reconstructed canonical
bytes that every reader runs against, so a derivative is never parsed as if it
were canonical.

## Editor composition

The shipped window (`app.py`) is a `QMainWindow` holding a menu bar, one compact
editor strip, the active editor's own workspace, and one status bar. The primary
editors, in strip order, are Atlas, Inspector, Maps and Graphics
(`app.py:70` `_EDITORS`). The Scene editor is secondary (`app.py:74`
`_SECONDARY`): it is opened from the placement that owns it, not from the strip.
Build and Launch are project actions that open as dialogs, not permanent
workspaces.

- Atlas, Inspector, Graphics and Scene are wrapped in an `EditorHost`
  (`editors.py:68`). The Maps editor is its own host because it owns internal
  modes (`editors.py:176` `MapsEditor`, plus `map_browser_tab.py`, `map_tab.py`
  and `warp_tab.py`).
- Editors never connect to each other. `MainWindow._wire_editors`
  (`app.py:158-172`) is the single place their signals are connected, and a
  signal announces an event rather than pushing data at a sibling.
- Two different events must stay two different callbacks:
  - `on_session_changed`: a new image is open, so editors drop staged
    in-memory authoring state and re-read the image.
  - `on_project_mutated`: a project mutation happened without replacing the
    image, so staged work is preserved and only project-derived facts are
    re-read.

  `MainWindow._on_project_changed` (`app.py:233-255`) fans the second out to
  every peer; `MainWindow._on_rom_opened` (`app.py:174-207`) drives the first
  one peer at a time so one panel's expected failure cannot leave the window
  half-refreshed.
- The shell publishes exactly one status line: the active editor's. A hidden
  editor finishing work cannot overwrite it (`app.py:582-598`).

## Revision counters and the authoring discipline

`Session` derives currentness from the three counters rather than tracking a
dirty flag by hand:

- `project_revision` is bumped by every project mutation
  (`Session.project_mutated`, `session.py:177-182`).
- `validation_revision` and `build_revision` record the `project_revision` at
  which validation passed and a build succeeded.
- `validation_current` is `validation_revision == project_revision`;
  `build_current` additionally requires `last_build is not None`
  (`session.py:164-170`).
- `project_mutated()` clears `validation_revision`, `build_revision` and
  `last_build`, so any edit makes the prior validation and build unusable.
  `record_build` refuses to run against a stale validation
  (`session.py:199-203`), and `scene_mutated` routes through `project_mutated`
  rather than adding a second invalidation path (`session.py:184-191`).

Every authoring surface must commit through `session.project_mutated()` and then
emit `projectChanged`, so Validate, Build and Launch re-arm. The Inspector is
the worked example (`inspector.py:409-410`, `424-425`).

Four steps, deliberately kept separate:

1. **Typing does not mutate the project.** The editor's `textChanged` only
   re-validates through the SDK and toggles the Apply button
   (`inspector.py:364-390`); a `_loading_editor` guard suppresses it during
   programmatic fills (`inspector.py:359-362`).
2. **Apply commits.** It re-validates, persists the replacement through the
   SDK, then calls `project_mutated()` and refreshes
   (`inspector.py:392-411`).
3. **Build is separate from Apply.** It is enabled only while
   `validation_current`, and `BuildPanelTab._on_build` re-checks that condition
   at click time (`build_panel.py:287-293`).
4. **Launch is separate from Build.** It reads the built path from
   `session.last_build` or a manual pick (`launcher.py:189-217`).

Two safety rules hold across all four:

- **The canonical ROM is immutable.** `is_safe_output_path`
  (`build_panel.py:48-59`) refuses an output that resolves to the source image.
  It is a module-level, Qt-free function so it is unit-testable, and it
  delegates the comparison to the SDK's own `write.paths_are_the_same_file`
  rather than deriving a second, weaker one. The check runs before
  `build_project` and again before the one irreversible delete
  (`build_panel.py:299-307`, `323-331`).
- **Fail closed.** An authoring target the SDK cannot resolve stays read-only
  with no raw-address or source-text fallback (`inspector.py:314-317`).

## Error handling: catch the family parent

A Qt slot has no console in front of the user. An uncaught exception escapes to
stderr, the GUI does nothing, and the click looks dead. Because an exception
raised inside a slot reached through a signal is printed and swallowed by the
binding, a `try` around the emitting call does not see it either
(`app.py:184-191`, `atlas_browser.py:179-183`).

**The rule: catch the SDK exception family parent, not one leaf subclass.**
Catching one child leaves its siblings uncaught, and a family that is not under
the same base as its neighbour needs its own `except`. Prefer naming the parent
once in a named tuple at module level and catching that tuple, as the shipped
code does; the tuple is the reviewable list.

### The SDK family parents

| Family parent | Defined in | Leaves seen in the tree |
| --- | --- | --- |
| `SessionError` | `workbench/session.py:39` | `RomNotRecognizedError` |
| `ProjectError` | `tools/webfoot/project/model.py:199` | `ProjectLoadError`, `ProjectValidationError` |
| `BuildError` | `tools/webfoot/build.py:93` | `ProjectRomMismatchError` |
| `WriteError` | `tools/webfoot/write.py:61` | `OutputPathError`, `ChangeValidationError`, `OverlappingChangeError` |
| `DialogueAuthoringError` | `tools/webfoot/dialogue.py:55` | none |

`WriteError` is not a `BuildError` or `ProjectError` subclass. That is exactly
the shape that escaped once before: a build slot caught the build and project
families, a directory-level failure raised `WriteError`, and the click looked
dead. It therefore has its own branch (`build_panel.py:314-331`).

### The shipped catch lists

| Surface | Catch list | Where |
| --- | --- | --- |
| ROM open, and the re-read after it | `OPEN_ROM_FAILURES` = `SessionError`, `RomReadError`, `OSError`, `MapError`, `CapabilityError`, `AtlasError`, `AtlasBuildError`, `TextTableError` | `session.py:60-77`, `atlas_browser.py:170-189` |
| Every peer's re-read after an open | `OPEN_ROM_FAILURES` | `app.py:208-213` |
| Extract, Validate | `(build_sdk.BuildError, ProjectError, OSError)` | `build_panel.py:227`, `258` |
| Build | `(build_sdk.BuildError, ProjectError)`, plus a separate `WriteError` branch | `build_panel.py:311-331` |
| Dialogue Apply, Revert, read | `(dialogue_sdk.DialogueAuthoringError, ProjectError, OSError)` | `inspector.py:284`, `322`, `345`, `406`, `420` |
| Launch (`subprocess.Popen`) | `OSError` | `launcher.py:200-203` |
| Graphics tab | `_SDK_ERRORS` = `GraphicsError`, `SpriteFormatError`, `PngError`, `OutputPathError` | `graphics_tab.py:77` |
| Maps editor edits | `_EDIT_ERRORS` = `MapLayoutEditError`, `MapLayoutWriteError`, `MapPaintError`, `ChunkAuthoringError`, `mv.MapBrowserError`, `WriteError` | `map_browser_tab.py:216-223` |
| Maps editor project read | `_PROJECT_READ_ERRORS` = `ProjectError`, `ChunkAuthoringError`, `OSError` | `map_browser_tab.py:230` |
| Maps editor project write | `_EDIT_AND_PROJECT_ERRORS` = `_EDIT_ERRORS` + `ProjectError`, `OSError` | `map_browser_tab.py:234` |
| Canonical-image chunk read | `_CHUNK_READ_ERRORS` = `ChunkAuthoringError`, `MapGraphicsError`, `mv.MapBrowserError`, `ProjectError`, `OSError` | `map_browser_tab.py:240-246` |
| Structural edits, structural view | `_STRUCTURE_ERRORS`, `_STRUCTURE_VIEW_ERRORS` | `map_browser_tab.py:257-265` |
| Map transitions, and their session read | `_TRANSITION_ERRORS`, `_TRANSITION_SESSION_ERRORS` | `map_tab.py:80-96` |
| Warp edits, and their session read | `_WARP_ERRORS`, `_WARP_SESSION_ERRORS` | `warp_tab.py:117-134` |

Note the deliberate split between a command slot and a session-boundary slot.
The command tuple names only SDK families, so a programming error in a slot
stays loud. The session tuple adds `AttributeError` and `TypeError`, because at
a boundary a profile object that is not the expected type is a read-only state
to report rather than a traceback inside a widget (`map_tab.py:89-96`,
`warp_tab.py:126-134`).

One catch is deliberately wider than a family: `atlas_browser.py:277-281`
catches `ValueError` around `atlas_build.parse_offset`, because that call raises
the SDK's `AtlasBuildError` and a bare `ValueError` from the integer parse. The
comment records the reason; do not generalise it to other slots.

### Rules for a new slot

1. List every SDK function the slot calls. For each, name the exception family
   parent it can raise. Add `OSError` when it touches the filesystem.
2. Catch those parents and turn the exception into a `QMessageBox`, and
   optionally status text. Never let it reach stderr.
3. A type that is not under the same base as its neighbour needs its own
   `except`; do not assume one family covers a sibling.
4. Do not branch on exception message text. Branch on a checkable condition: the
   overwrite offer is gated on the output file actually existing, never on the
   message (`build_panel.py:314-322`).

## Acceptance testing

Headless tests do not exercise the real click, SDK call and error path. Two
error-handling defects in the original Workbench escaped every headless test and
surfaced only in a live click-through. Treat the layers below as
complementary, and the last one as mandatory.

1. **Qt-free logic is unit-tested without a GUI.** Keep safety-critical
   functions Qt-free so they are testable headless; `is_safe_output_path` is
   covered by `tests/unit/test_build_panel_guard.py` and
   `tests/unit/test_build_panel_overwrite.py`. Session revision logic and the
   SDK facades are covered the same way.
2. **Real SDK integration, ROM-gated.** `tests/integration/` proves the public
   path end to end, including `test_workbench_rom_safety.py`,
   `test_workbench_scene_rom.py` and `test_workbench_workspace_rom.py`.
3. **GUI module tests.** They construct a real `QApplication` and real widgets
   (`tests/unit/test_workbench_smoke.py`, `test_workbench_state_and_errors.py`),
   which is why CI sets `QT_QPA_PLATFORM=offscreen`. Run the gate with
   `python -m pytest -m workbench`; [testing.md](testing.md) defines it and the
   `REQUIRED_GUI_MODULES` list in `tests/gates.py` that stops a shipping GUI
   module from collapsing to a whole-file skip. A green run is necessary, not
   sufficient: the modules skip cleanly when PySide6 is absent.
4. **The mandatory live walkthrough.** Before a Workbench task is called
   complete, run `python -m tools.webfoot.workbench`, populate it with
   representative real data, and click every new or changed path, including the
   error paths: bad input, a missing file, an unsupported authoring target, a
   stale validation. Each must produce a `QMessageBox` and a status line, never
   a dead click. Confirm the canonical image is unchanged in size and SHA-256
   after a build. The visual and interaction review for a visible change is in
   [desktop-ui.md](desktop-ui.md).

## Where the detail lives

- [workbench.md](workbench.md): the Maps editor Layout mode and derivative
  reopen.
- [architecture.md](architecture.md): the SDK layering the Workbench calls into.
- [testing.md](testing.md): gates, markers and environment requirements.
- [desktop-ui.md](desktop-ui.md): how an editor surface should look and behave.
