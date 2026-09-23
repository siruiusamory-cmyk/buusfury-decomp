"""DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001 QA harness: drive the real app and capture.

This is QA tooling, not production code. It launches the SHIPPED `MainWindow`
against the real canonical ROM, drives a named set of representative states
through the tabs' own public widget API, and writes one PNG per state.

It fabricates nothing: every map, name, dialogue string and layout change in the
captures comes out of the open image through the SDK. The one authored artifact
it creates is a real DragonByte Z layout derivative (a Save As of one cell),
produced by the real `MapLayoutEditor.save`, so the derivative-reopen state is a
genuine provenance acceptance rather than a mock.

Run:

    python -m tools.qa.visual_pass_capture --out <dir> [--states 1,2,3]

`--list` prints the state names. Offscreen Qt is set before PySide6 is imported,
so each capture is deterministic and does not steal the desktop.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from PySide6.QtCore import QSize, Qt, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QLabel, QWidget  # noqa: E402

from tools.webfoot.cli import load_catalog  # noqa: E402
from tools.webfoot import atlas as atlas_sdk  # noqa: E402
from tools.webfoot import dialogue as dialogue_sdk  # noqa: E402
from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402
from tools.webfoot.workbench.graphics_tab import _IDENTITY_ROLE  # noqa: E402

try:  # The baseline revision has no theme module; the candidate does.
    from tools.webfoot.workbench import theme as app_theme  # noqa: E402
except ImportError:  # pragma: no cover - baseline capture only
    app_theme = None

#: The canonical Buu's Fury USA rev0 image, and the assembled Atlas artifact the
#: Session expects. Both live OUTSIDE this worktree by default (they are ignored
#: local inputs), so they are overridable rather than copied in - a junction
#: inside the worktree is reported by git as a link it will not resolve, which
#: `tests/unit/test_project_safety.py` correctly refuses.
ROM = Path(
    os.environ.get(
        "DBZ_QA_ROM",
        r"<checkout>\roms\Dragon Ball Z - Buu's Fury (U).gba",
    )
)
ATLAS_DIR = Path(
    os.environ.get("DBZ_QA_ATLAS_DIR", r"<checkout>\build\atlas")
)
CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: The Grand Kai proof case used by the accepted layout-editor record: map 64's
#: first editable layer, cell 0.
PROOF_MAP = 0x40
PROOF_CELL = 0

#: A map whose layout form is not the proven dominant chunk grid (terrain field).
READ_ONLY_MAP = 19

#: Legacy tab indices are gone; navigation is by editor name. These remain for
#: the probes that still speak in indices.
TAB_ATLAS, TAB_INSPECTOR, TAB_MAPS, TAB_MAP, TAB_BROWSER, TAB_GRAPHICS, TAB_BUILD, TAB_LAUNCH = range(8)


class _NullHost:
    """A stand-in host for the action surfaces, which own no status line."""

    def status_label(self):
        return None


class _LegacyMaps:
    """Drives the three map tabs of the pre-correction shell as one editor.

    The baseline had `Maps` (Scene), `Map` (placements) and `Map Browser` as three
    destinations. This presents the same three workflows through the mode names the
    corrected shell uses, so one harness can capture both revisions and the pair is
    a real comparison rather than two different tools' output.
    """

    def __init__(self, harness: "Harness") -> None:
        self._harness = harness
        self._mode = "browse"

    @property
    def browser(self):
        return self._harness.editor("Maps")

    @property
    def workspace(self):
        return self._harness.tab(self._LEGACY_MAP_INDEX)

    _LEGACY_MAP_INDEX = 3  # the pre-correction "Map" tab

    def set_mode(self, key: str) -> None:
        """Show the baseline destination that performed this mode's workflow."""
        self._mode = key
        if key == "objects":
            self._harness.show_editor("Map")
            return
        self._harness.show_editor("Maps")
        toggle = getattr(self.browser, "_edit_toggle", None)
        if toggle is not None:
            toggle.setChecked(key == "layout")
        self._harness.pump(4)

    def mode(self) -> str:
        return self._mode

    def unsaved_edit_count(self) -> int:
        counter = getattr(self.browser, "unsaved_edit_count", None)
        if callable(counter):
            return counter()
        unsaved = getattr(self.browser, "_unsaved_count", None)
        return unsaved() if callable(unsaved) else 0

#: Desktop and narrow window sizes. 1440x900 is the size the accepted public
#: captures use; 1100x720 is the narrow state.
DESKTOP = QSize(1440, 900)
NARROW = QSize(1100, 720)

#: Qt no longer ships fonts and the offscreen platform finds none on Windows, so
#: every glyph would render as a box. Registering real system faces is what makes
#: an offscreen capture legible enough to review.
_FONT_FILES = (
    "segoeui.ttf",
    "segoeuib.ttf",
    "segoeuii.ttf",
    "consola.ttf",
    "consolab.ttf",
)


def _load_system_fonts() -> None:
    from PySide6.QtGui import QFontDatabase

    root = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in _FONT_FILES:
        candidate = root / name
        if candidate.is_file():
            QFontDatabase.addApplicationFont(str(candidate))


def _point_at_local_inputs() -> None:
    """Tell the SDK where the ignored local Atlas artifact actually lives.

    The worktree holds no `build/` of its own (it is generated and ignored), so
    the QA harness redirects the CLI's default atlas directory to the configured
    one instead of creating a junction git will refuse to resolve. Both importers
    are patched: `Session` binds the helper into its own namespace at import.
    """
    from tools.webfoot import cli
    from tools.webfoot.workbench import session as workbench_session

    resolver = lambda: ATLAS_DIR  # noqa: E731 - a one-line stand-in
    cli._default_atlas_directory = resolver
    workbench_session._default_atlas_directory = resolver


class Harness:
    """One live application instance plus the directories a state may need."""

    def __init__(self, out: Path, workspace: Path) -> None:
        self.out = out
        self.workspace = workspace
        _load_system_fonts()
        _point_at_local_inputs()
        self.catalog = load_catalog(None)
        self.session = Session()
        self.window = MainWindow(self.session, self.catalog)
        # The window must be *shown* for a resize to reach the layout: an unshown
        # QWidget keeps its initial geometry, so a capture taken from a hidden
        # window is a capture of the wrong size. The offscreen platform maps it
        # without stealing the desktop.
        self.window.show()
        self.window.resize(DESKTOP)
        self.pump()

    # -- process ------------------------------------------------------------

    def pump(self, rounds: int = 6) -> None:
        """Run the event loop briefly so deferred work (icon drains) lands."""
        for _ in range(rounds):
            QApplication.processEvents()

    def grab(self, name: str, *, size: QSize | None = None) -> Path:
        if size is not None:
            self.window.resize(size)
        self.pump()
        # Qt delivers a resize asynchronously; give the layout its pass before
        # grabbing, or the pixmap is of the previous geometry.
        QApplication.processEvents()
        self.pump(4)
        path = self.out / f"{name}.png"
        pixmap = self.window.grab()
        pixmap.save(str(path), "PNG")
        print(
            f"  captured {path.name}  ({self.window.width()}x{self.window.height()}, "
            f"minimum {self.window.minimumSizeHint().width()}x"
            f"{self.window.minimumSizeHint().height()})"
        )
        return path

    @property
    def tabs(self):
        """Kept for older probes: the shell no longer has a tab strip."""
        return None

    def tab(self, index: int):
        """Kept for older probes: resolve a legacy tab index to its editor."""
        legacy = {
            0: "Atlas", 1: "Inspector", 2: "Scene", 3: "Maps", 4: "Maps",
            5: "Graphics", 6: "Build", 7: "Launch",
        }
        return self.editor(legacy[index])

    def editor(self, name: str):
        """The live editor widget for an editor name.

        Resolves against the current editor-strip shell, and falls back to the
        pre-correction tab shell so the same harness can capture the baseline and
        the candidate: a before/after pair must be taken by the same tool or it is
        not a comparison.
        """
        hosts = getattr(self.window, "_hosts", None)
        if hosts and name in hosts:
            return hosts[name].signal_source()
        legacy = {
            "Atlas": 0, "Inspector": 1, "Scene": 2, "Map": 3, "Maps": 4,
            "Graphics": 5, "Build": 6, "Launch": 7,
        }
        tabs = getattr(self.window, "_tabs", None)
        if tabs is not None and name in legacy:
            widget = tabs.widget(legacy[name])
            unwrap = getattr(widget, "content", None)
            return unwrap() if callable(unwrap) else widget
        if name == "Build":
            return self.window._build
        if name == "Launch":
            return self.window._launcher
        raise SystemExit(f"unknown editor {name!r}")

    # -- navigation ---------------------------------------------------------

    def show_editor(self, name: str) -> None:
        """Show one editor, on either the current or the pre-correction shell."""
        if name in ("Build", "Launch"):
            # These are project-action surfaces now, not destinations. They are
            # shown as the shell's stage for the capture, exactly the widget the
            # action's dialog re-parents. The shell's status line is cleared rather
            # than pointed at one of them: they own no status of their own and the
            # permanent zone still carries the project state.
            for host in getattr(self.window, "_hosts", {}).values():
                host.setVisible(False)
            self.window._build.setVisible(name == "Build")
            self.window._launcher.setVisible(name == "Launch")
            if hasattr(self.window, "_active_host"):
                self.window._active_host = None
                self.window._status_context.setText("")
            self.pump()
            return
        if hasattr(self.window, "show_editor"):
            self.window.show_editor(name)
            self.pump()
            return
        legacy = {"Atlas": 0, "Inspector": 1, "Scene": 2, "Map": 3, "Maps": 4,
                  "Graphics": 5}[name]
        self.window._tabs.setCurrentIndex(legacy)
        self.pump()

    def show_project_action(self, name: str, shot_name: str):
        """Capture a project-action surface AS A DIALOGUE.

        Build and Run are actions, so their configuration is a content-sized
        dialogue rather than an editor page. Capturing them as pages would show a
        shape the product no longer has - and would be exactly the "action looks
        like an editor switch" confusion the review named. This opens the real
        dialogue, grabs it, and closes it, so the capture is of the shipping
        surface and nothing is left behind.
        """
        window = self.window
        captured: list[Path] = []

        def grab_live_dialog():
            """Grab whatever modal dialogue the action opened, then close it.

            The REAL `_show_surface_dialog` is used, not a stand-in: a stand-in
            would capture the harness's idea of the dialogue rather than the one
            that ships. `open_build_report` runs a nested event loop, so the grab
            is scheduled as a zero-delay timer that fires inside that loop.
            """
            from PySide6.QtWidgets import QApplication, QDialog

            dialog = QApplication.activeModalWidget()
            if not isinstance(dialog, QDialog):
                dialog = QApplication.activeWindow()
            if not isinstance(dialog, QDialog):
                print(f"  (no dialogue appeared for {name})")
                return
            # The dialogue's own layout has to settle before the grab. An immediate
            # capture records the geometry from before the surface was laid out, and
            # comes back with the caption alone.
            self.pump(20)
            path = self.out / f"{shot_name}.png"
            dialog.grab().save(str(path), "PNG")
            print(
                f"  captured {path.name}  ({dialog.width()}x{dialog.height()}, "
                f"content asks {dialog.sizeHint().width()}x{dialog.sizeHint().height()})"
            )
            captured.append(path)
            dialog.close()

        QTimer.singleShot(250, grab_live_dialog)
        if name == "Build":
            window.open_build_report()
        else:
            window.open_run_configuration()
        return captured[0] if captured else None

    @property
    def maps(self):
        """The Maps editor, or the layout browser on the pre-correction shell."""
        return getattr(self.window, "_maps", None) or self.editor("Maps")

    def close_project(self) -> None:
        """Return the session to ROM-only: no project open.

        There is no `close_project` on the session because the application never
        needs one, so this performs exactly the two things selecting a different
        project source does - drop the directory and invalidate the results tied to
        the old source - without inventing an API the product does not have. The
        shell then recomputes its status from that state.
        """
        self.session.project_dir = None
        self.session.project_mutated()
        self.window._refresh_identity()
        self.window._refresh_action_state()
        self.pump(4)

    def show_tab(self, index: int) -> None:
        """Kept for older probes: a legacy tab index names an editor."""
        self.show_editor(self.tab_name(index))

    @staticmethod
    def tab_name(index: int) -> str:
        return {
            0: "Atlas", 1: "Inspector", 2: "Scene", 3: "Maps", 4: "Maps",
            5: "Graphics", 6: "Build", 7: "Launch",
        }[index]

    # -- session ------------------------------------------------------------
    def open_canonical(self) -> None:
        import hashlib

        digest = hashlib.sha256(ROM.read_bytes()).hexdigest()
        if digest != CANONICAL_SHA256:
            raise SystemExit(f"canonical ROM hash mismatch: {digest}")
        self.session.open_rom(ROM, self.catalog)
        # The Atlas editor owns the "Open ROM" click; emit what it would emit so
        # the shell reacts exactly as a real open does.
        self.editor("Atlas").romOpened.emit()
        self.pump()

    # -- map editor ---------------------------------------------------------

    @property
    def maps(self):
        """The Maps editor, or a stub on the pre-correction shell.

        On the baseline the three map destinations are three separate tabs, so
        "switch mode" is "select the tab" and there is no mode strip to drive.
        """
        return getattr(self.window, "_maps", None) or _LegacyMaps(self)

    @property
    def browser(self):
        return self.maps.browser

    def select_map(self, index: int) -> None:
        tab = self.browser
        for row in range(tab._list.count()):
            if tab._list.item(row).data(Qt.ItemDataRole.UserRole) == index:
                tab._list.setCurrentRow(row)
                self.pump()
                return
        raise SystemExit(f"map:{index:04d} is not in the browser list")

    def enter_edit_mode(self) -> None:
        self.browser._edit_toggle.setChecked(True)
        self.pump()

    def choose_chunk_row(self, row: int) -> None:
        self.browser._chooser.setCurrentRow(row)
        self.pump()

    def apply_draft(self) -> None:
        self.browser._apply_draft()
        self.pump()


def _probe() -> int:
    app = QApplication.instance() or QApplication([])
    harness = Harness(Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()))
    harness.open_canonical()
    harness.show_tab(TAB_BROWSER)
    tab = harness.browser
    for row in range(tab._list.count()):
        item = tab._list.item(row)
        if item.data(Qt.ItemDataRole.UserRole) in (PROOF_MAP, READ_ONLY_MAP):
            print(item.text())
    harness.select_map(PROOF_MAP)
    print("target        :", tab._target.editable, tab._target.read_only_kind)
    print("editable slots:", [s.label for s in tab._target.editable_slots])
    if tab._layer_combo.count():
        tab._layer_combo.setCurrentIndex(0)
        harness.pump()
        slot = tab._slot
        print(
            "slot",
            slot.slot,
            "grid",
            f"{slot.grid.columns}x{slot.grid.rows}",
            "choices",
            len(slot.choices),
        )
    harness.select_map(READ_ONLY_MAP)
    print(
        "map 19 target :",
        tab._target.editable,
        tab._target.read_only_kind,
        "|",
        tab._target.read_only_reason if tab._target else None,
    )
    del app
    return 0


def make_derivative(workspace: Path) -> Path:
    """Author one real layout change and Save As a real derivative ROM.

    Uses the shipped `MapLayoutEditor` and its real provenance manifest, so the
    derivative-reopen capture exercises genuine acceptance rather than a stub.
    """
    from tools.webfoot.map_layout_edit import MapLayoutEditor

    editor = MapLayoutEditor(ROM.read_bytes())
    target = editor.target(PROOF_MAP)
    slot = target.editable_slots[0]
    original = slot.cells[PROOF_CELL].pointer
    replacement = next(choice for choice in slot.choices if choice != original)
    editor.set_cell(PROOF_MAP, slot.slot, PROOF_CELL, replacement)
    output = workspace / f"{ROM.stem} - Edited.gba"
    saved = editor.save(output, source_path=ROM, profile_id="buus_fury_usa_rev0_01c1707f")
    print(
        f"  derivative: {saved.output_path.name}  "
        f"{len(saved.changes)} change(s)  {len(saved.changed_offsets)} byte(s)"
    )
    return saved.output_path


def _dialogue_project(harness: Harness, workspace: Path) -> Path:
    """Extract a real project from the canonical ROM so dialogue editing is live."""
    from tools.webfoot.build import extract_project

    project = workspace / "workbench-capture-project"
    if project.is_dir():
        return project
    extract_project(ROM, project, harness.catalog, graphics=False)
    return project


def capture_all(harness: Harness, workspace: Path) -> None:
    """Drive every required BEFORE/AFTER state through the real widgets.

    The correction's own required list is covered explicitly: the application
    shell, Graphics with and without a selection, the Maps editor in its browse
    and layout modes, the Maps editor's Objects mode, the shell and the Maps
    editor at a narrow width, and the Build action's report surface.
    """
    out = harness.out

    # 1. the shell itself, before a ROM. This is the capture that answers the
    #    "menu bar -> one strip -> workspace" requirement.
    print("[1] shell")
    harness.show_editor("Atlas")
    harness.grab("01-shell-no-rom")

    # 2. the Maps editor, Browse mode
    print("[2] maps / browse")
    harness.open_canonical()
    harness.show_editor("Maps")
    harness.maps.set_mode("browse")
    harness.select_map(PROOF_MAP)
    harness.grab("02-maps-browse")

    # 3. the Maps editor, Layout mode with an editable map selected
    print("[3] maps / layout")
    harness.select_map(PROOF_MAP)
    harness.maps.set_mode("layout")
    harness.grab("03-maps-layout")

    # 4. a chunk cell selected in Layout mode
    print("[4] maps / layout, cell selected")
    harness.browser._on_cell_clicked(PROOF_CELL)
    harness.pump()
    harness.grab("04-maps-layout-cell")

    # 5. a pending, unapplied chunk replacement
    print("[5] maps / pending pick")
    tab = harness.browser
    current = tab._chooser_row_for(tab._working_pointer(tab._slot.slot, PROOF_CELL))
    harness.choose_chunk_row(1 if current == 0 else 0)
    harness.grab("05-maps-pending-pick")

    # 6. the applied, unwritten edit
    print("[6] maps / unsaved")
    harness.apply_draft()
    harness.grab("06-maps-unsaved")

    # 7. a real Save As derivative, reopened and read-only
    print("[7] maps / derivative reopen")
    derivative = make_derivative(workspace)
    harness.session.open_rom(derivative, harness.catalog)
    harness.editor("Atlas").romOpened.emit()
    harness.show_editor("Maps")
    harness.maps.set_mode("layout")
    harness.select_map(PROOF_MAP)
    harness.grab("07-maps-derivative-read-only")

    # 8. an unsupported map: the reason is named, the map stays browsable
    print("[8] maps / unsupported map")
    harness.session.open_rom(ROM, harness.catalog)
    harness.editor("Atlas").romOpened.emit()
    harness.show_editor("Maps")
    harness.maps.set_mode("layout")
    harness.select_map(READ_ONLY_MAP)
    harness.grab("08-maps-read-only-map19")

    # 9. the Maps editor, Objects mode: the placement-authoring surface
    print("[9] maps / objects")
    harness.maps.set_mode("objects")
    harness.pump(10)
    harness.grab("09-maps-objects")

    # 10. dialogue editing (Inspector over a real, authorable dialog record)
    print("[10] inspector / dialogue")
    project = _dialogue_project(harness, workspace)
    harness.session.set_project(project)
    harness.editor("Atlas").romOpened.emit()
    _show_dialogue(harness)
    harness.show_editor("Inspector")
    harness.grab("10-inspector-dialogue")

    # 11. Graphics with NOTHING selected: the corrected empty state
    print("[11] graphics / no selection")
    harness.show_editor("Graphics")
    harness.pump(24)
    harness.grab("11-graphics-empty")

    # 12. Graphics with a sprite selected: the contextual inspector populated
    print("[12] graphics / sprite selected")
    harness.editor("Graphics")._grid.setCurrentRow(0)
    harness.pump(24)
    harness.grab("12-graphics-selected")
    print("[G1-G8] graphics states")
    graphics_qa(harness)

    # 13. the Atlas editor with a ROM open and NO project.
    #
    # The project opened at step 10 is still open here, which made this capture a
    # genuine "project open, never validated" state while its name claimed
    # ROM-only - the disagreement the human review found between this capture and
    # Maps Browse. The project is closed again first, so the state matches the
    # claim and the ROM-only row reads the same in every editor and at every width.
    print("[13] atlas (ROM only)")
    harness.close_project()
    harness.show_editor("Atlas")
    harness.grab("13-atlas-rom-open")

    # 14. the Build action's surface, captured as the DIALOGUE it now is
    print("[14] build action")
    harness.show_project_action("Build", "14-build-action")

    # 15. the Run action's configuration surface, likewise a dialogue
    print("[15] run action")
    harness.show_project_action("Run", "15-run-configuration")

    # 16. the whole shell at the narrow width, on the primary editing surface
    print("[16] narrow shell")
    harness.show_editor("Maps")
    harness.maps.set_mode("layout")
    harness.select_map(PROOF_MAP)
    harness.grab("16-narrow-shell", size=NARROW)
    harness.window.resize(DESKTOP)
    harness.pump()

    # 17. the Maps editor at the narrow width, Browse mode (ROM only)
    print("[17] narrow maps / browse (ROM only)")
    harness.maps.set_mode("browse")
    harness.select_map(READ_ONLY_MAP)
    harness.grab("17-narrow-maps-browse", size=NARROW)
    harness.window.resize(DESKTOP)
    harness.pump()

    # 18. the narrow shell on the Atlas editor (ROM only)
    print("[18] narrow shell / atlas (ROM only)")
    harness.show_editor("Atlas")
    harness.grab("18-narrow-shell-atlas", size=NARROW)
    harness.window.resize(DESKTOP)
    harness.pump()

    print(f"\nwrote {len(list(out.glob('*.png')))} PNG(s) to {out}")


def graphics_qa(harness: Harness, out: Path | None = None) -> list[Path]:
    """The Graphics-workspace states the human correction asked for by name.

    Every one is driven through the real widget: a static sprite, an animated one,
    a specific animation, playback on, a selected swatch, a pending recolour and
    the narrow window. Nothing here invents a state the editor cannot reach.
    """
    written: list[Path] = []
    graphics = harness.editor("Graphics")
    row0 = graphics._grid.item(0)

    def shot(name: str, size=None) -> None:
        written.append(harness.grab(name, size=size))

    # A sprite that has no animation reaches no character, so it has no stepper.
    # Every sprite in the canonical image reaches a character, so the static case
    # is driven explicitly: the stepper is asked to show the sprite itself, which
    # is the code path a genuinely static asset takes.
    static_row = _first_static_row(graphics)
    print("[G2] graphics / static sprite")
    graphics._grid.setCurrentRow(static_row if static_row is not None else 0)
    harness.pump(20)
    graphics._load_character_animations(None)
    harness.pump(6)
    shot("g2-graphics-static-sprite")
    if static_row is None:
        print("  (no character-less sprite in this image; drove the static path directly)")

    # An animated sprite: the stepper exists and the one preview shows its frame.
    animated_row = _first_animated_row(graphics)
    if animated_row is not None:
        print("[G3] graphics / animated sprite")
        graphics._grid.setCurrentRow(animated_row)
        harness.pump(24)
        shot("g3-graphics-animated-sprite")

        # A second animation, when the character has more than one.
        if graphics._anim_select.count() > 1:
            print("[G4] graphics / second animation")
            graphics._anim_select.setCurrentRow(1)
            harness.pump(16)
            shot("g4-graphics-second-animation")
            graphics._anim_select.setCurrentRow(0)
            harness.pump(10)

        # Playback on. Presentation only; the frame label still says which frame
        # is shown, so the capture proves the timer advanced rather than a claim.
        print("[G5] graphics / playing")
        graphics._play.setChecked(True)
        harness.pump(40)
        shot("g5-graphics-playing")
        graphics._play.setChecked(False)
        harness.pump(6)

    # A selected palette swatch: the one detail line names it.
    print("[G6] graphics / swatch selected")
    order = sorted(graphics._swatches)
    if order:
        graphics._pick_colour = _no_dialog_pick(graphics)
        graphics._swatches[order[0]].mousePressEvent(None)
        harness.pump(6)
        shot("g6-graphics-swatch-selected")

    # A pending, unapplied recolour: previewed on the swatch and stated in words.
    print("[G7] graphics / pending recolour")
    if order:
        index = order[0]
        graphics._palette_pending[index] = (250, 180, 60)
        swatch = graphics._swatches.get(index)
        if swatch is not None:
            r, g, b = graphics._palette_pending[index]
            graphics._paint_swatch(swatch, r, g, b)
        graphics._refresh_pending_ui()
        harness.pump(6)
        shot("g7-graphics-pending-recolour")
        graphics._palette_pending.clear()
        graphics._refresh_pending_ui()
        harness.pump(4)

    # The narrow window on this editor.
    print("[G8] graphics / narrow")
    shot("g8-graphics-narrow", size=NARROW)
    harness.window.resize(DESKTOP)
    harness.pump()
    return written


def _no_dialog_pick(graphics):
    """Freeze the colour dialogue's callback so QA can select a swatch only.

    QA must not open a modal colour dialogue, and it must not *write* anything:
    this returns a call that records the selection exactly as the real handler
    does before the dialogue appears, and stops there.
    """

    def pick(index: int) -> None:
        graphics._selected_palette_index = index
        graphics._refresh_palette_detail()

    return pick


def _first_animated_row(graphics) -> int | None:
    """The first grid row whose sprite reaches a character with animations."""
    for row in range(min(graphics._grid.count(), 400)):
        identity = graphics._grid.item(row).data(_IDENTITY_ROLE)
        if _animations_for(graphics, identity):
            return row
    return None


def _first_static_row(graphics) -> int | None:
    """The first grid row whose sprite reaches no animated character."""
    for row in range(min(graphics._grid.count(), 400)):
        identity = graphics._grid.item(row).data(_IDENTITY_ROLE)
        if _animations_for(graphics, identity) is None:
            return row
    return None


def _animations_for(graphics, identity):
    """The decoded animations for a sprite identity, or None when it has none."""
    if identity is None:
        return None
    sprites = graphics._sprites()
    if sprites is None:
        return None
    try:
        graphic = sprites.graphic(identity)
        if not graphic.characters:
            return None
        return sprites.get_actor_animations(graphic.characters[0]) or None
    except Exception:  # noqa: BLE001 - a QA probe, never a production path
        return None


def _show_dialogue(harness: Harness) -> None:
    """Drive the one REAL dialogue record the Inspector can author.

    The public dialogue-authoring API registers exactly one target for this
    profile, so the capture searches for the phrase that reaches it
    (``goku-greeting``, packed handle ``0x02002641``) instead of picking an
    arbitrary match, which would leave the Inspector in its
    "editing not available" state.
    """
    session = harness.session
    for phrase in ("Goku", "Kakarot", "Saiyan"):
        result = atlas_sdk.search_text(
            session.atlas, phrase, session.decoded_text, rom_image=session.rom_image
        )
        for decoded in result["decoded"]:
            if dialogue_sdk.resolve_dialogue_target(decoded, session.profile) is None:
                continue
            harness.editor("Atlas").resultActivated.emit({**decoded, "_mode": "decoded"})
            harness.pump()
            print(f"  Inspector target: {phrase!r} -> {decoded.get('text', '')[:48]!r}")
            return
    print("  (no resoluble dialogue result; Inspector stays in its empty state)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="directory to write PNGs into")
    parser.add_argument("--probe", action="store_true", help="print real map facts")
    args = parser.parse_args(argv)
    if args.probe:
        return _probe()
    if args.out is None:
        parser.error("--out is required")
    args.out.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="dbz-visual-qa-"))
    app = QApplication.instance() or QApplication([])
    app.setOrganizationName("Webfoot")
    app.setApplicationName("Workbench")
    # The application-wide theme is applied by the real entry point, so the capture
    # must apply it too: without it the shell is stock light Qt, which is precisely
    # the "black headers pasted on stock panels" defect the review must be able to
    # see or not see. The baseline revision has no theme module.
    if app_theme is not None:
        app_theme.apply_app_theme(app)
    harness = Harness(args.out, workspace)
    try:
        capture_all(harness, workspace)
    finally:
        harness.window.close()
        shutil.rmtree(workspace, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
