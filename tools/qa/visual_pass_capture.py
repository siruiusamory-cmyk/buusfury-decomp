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
    python -m tools.qa.visual_pass_capture --list

`--list` prints the numbered states. `--states 20,21` captures only those.
States 1-19 are ONE chained suite - each builds on the session the previous one
left - so they are captured together or not at all; states 20+ are self-contained
and may be requested alone.

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
from tools.webfoot.map_chunk import ChunkTemplate  # noqa: E402
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

#: Every state this harness can capture, numbered. The numbers are the contract
#: `--states` speaks; the names are the PNGs written. 1-19 are one chained suite
#: (see the module docstring); 20-23 are MAP-CHUNK-AUTHORING-001's own states and
#: 40+ are MAP-RESIZE-AND-LAYERS-001's. Each of those builds its own session,
#: project and map from scratch.
STATES: tuple[tuple[int, str], ...] = (
    (1, "01-shell-no-rom"),
    (2, "02-maps-browse"),
    (3, "03-maps-layout"),
    (4, "04-maps-layout-cell"),
    (5, "05-maps-pending-pick"),
    (6, "06-maps-unsaved"),
    (7, "07-maps-derivative-read-only"),
    (8, "08-maps-read-only-map19"),
    (9, "09-maps-objects"),
    (10, "10-inspector-dialogue"),
    (11, "11-graphics-empty"),
    (12, "12-graphics-selected (+ g1-g8 graphics states)"),
    (13, "13-atlas-rom-open"),
    (14, "14-build-action (dialogue)"),
    (15, "15-run-configuration (dialogue)"),
    (16, "16-narrow-shell"),
    (17, "17-narrow-maps-browse"),
    (18, "18-narrow-shell-atlas"),
    (19, "19-scene-editor-empty"),
    (20, "20-chunk-editor-new"),
    (21, "21-chunk-editor-painted"),
    (22, "22-chunk-editor-narrow"),
    (23, "23-chunk-authored-placement-on-map"),
    (40, "40-retail-map-before-resize"),
    (41, "41-resize-form-opened"),
    (42, "42-resize-form-grown-dimensions"),
    (43, "43-resize-staged-initialized-cells"),
    (44, "44-resize-undo-retail-grid"),
    (45, "45-resize-redo-grown-grid"),
    (46, "46-resize-applied-project-grid (layer list before creation)"),
    (48, "48-new-layer-form"),
    (49, "49-layer-list-after-creation"),
    (50, "50-authored-layer-selected"),
    (51, "51-authored-layer-painted"),
    (52, "52-unrelated-mutation-keeps-staged-structure"),
    (53, "53-session-replacement-clears-staged-structure"),
    (54, "54-structural-surface-narrow"),
    (55, "55-resize-form-refuses-a-shrink"),
    (56, "56-validation-error-dialog"),
    (60, "60-warps-list-retail"),
    (61, "61-warps-selected-connection"),
    (62, "62-warps-staged-retarget"),
    (63, "63-warps-undo-retail"),
    (64, "64-warps-applied-saved"),
    (65, "65-warps-reverted-retail"),
    (66, "66-warps-class-169-read-only"),
    (67, "67-warps-retarget-refusal-status"),
    (68, "68-warps-narrow"),
    (69, "69-warps-map-with-no-connections"),
    (70, "70-warps-create-form-opened"),
    (71, "71-warps-create-name-authored"),
    (72, "72-warps-create-base-selected"),
    (73, "73-warps-create-staged-values"),
    (74, "74-warps-create-staged-row"),
    (75, "75-warps-create-applied-saved"),
    (76, "76-warps-create-reverted"),
    (77, "77-warps-create-undo-redo"),
    (78, "78-warps-create-duplicate-name-refused"),
    (79, "79-warps-create-no-base-on-this-map"),
    (80, "80-warps-create-shared-root-refused"),
    (81, "81-warps-create-narrow"),
    (90, "90-warp-canvas-regions"),
    (91, "91-warp-canvas-click-selects-row"),
    (92, "92-warp-canvas-selected-region"),
    (93, "93-warp-canvas-dragged-region"),
    (94, "94-warp-canvas-warps-row-after-drag"),
    (95, "95-warp-canvas-undo-retail"),
    (96, "96-warp-canvas-class-169-read-only"),
    (97, "97-warp-canvas-drag-refused"),
)

#: The last chained state; anything above it is self-contained.
LAST_CHAINED_STATE = 19

#: The first MAP-RESIZE-AND-LAYERS-001 state; 20..THIS-1 are chunk authoring's.
FIRST_STRUCTURAL_STATE = 40

#: The first MAP-WARP-WORKBENCH-001 state: the Maps editor's Warps mode.
FIRST_WARP_STATE = 60

#: The first MAP-WARP-CREATE-WORKBENCH-001 state: the Warps mode's Create action.
FIRST_WARP_CREATE_STATE = 70

#: The first MAP-WARP-CANVAS-001 state: connections on the Objects canvas.
FIRST_WARP_CANVAS_STATE = 90


class _NullHost:
    """A stand-in host for the action surfaces, which own no status line."""

    def status_label(self):
        return None


class _MapsAccessor:
    """Drives the current shell's Maps editor modes and reports its pending work.

    `MapsEditor.set_mode` returns silently for a mode it does not have, so this
    checks the landing state instead of trusting the call: a capture that asked
    for one mode and photographed another is worse than a failed capture.
    """

    def __init__(self, editor) -> None:
        self._editor = editor

    def set_mode(self, key: str) -> None:
        buttons = self._editor.mode_buttons()
        if key not in buttons:
            raise SystemExit(
                f"unknown Maps mode {key!r}; this shell has {sorted(buttons)}"
            )
        self._editor.set_mode(key)
        landed = self._editor.mode()
        if landed != key or not buttons[key].isChecked():
            raise SystemExit(
                f"Maps mode {key!r} did not become the shown mode "
                f"(editor reports {landed!r})"
            )

    def mode(self) -> str:
        return self._editor.mode()

    def unsaved_edit_count(self) -> int:
        counter = getattr(self._editor, "unsaved_edit_count", None)
        return counter() if callable(counter) else 0

    @property
    def browser(self):
        """The Maps editor's layout browser, which owns the map list and paints."""
        return self._editor.browser

    @property
    def warps(self):
        """The Maps editor's Warps surface."""
        return self._editor.warps

    @property
    def workspace(self):
        """The Maps editor's Objects canvas."""
        return self._editor.workspace

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

    def editors(self) -> tuple[str, ...]:
        """Every editor this shell actually has, in strip order."""
        return tuple(self.window._hosts)

    def editor(self, name: str):
        """The live editor widget for an editor name, or a refusal.

        Resolution goes through the shell's own host registry, the authority the
        product navigates with. An unknown name is an error here rather than a
        silently substituted surface: this harness exists to photograph one named
        editor, and capturing a different one would misrepresent the shell.
        """
        hosts = getattr(self.window, "_hosts", None)
        if not hosts:
            raise SystemExit(
                "this window has no editor host registry; the capture harness "
                "targets the current editor-strip shell only"
            )
        if name not in hosts:
            raise SystemExit(
                f"unknown editor {name!r}; this shell has {sorted(hosts)}"
            )
        return hosts[name].signal_source()

    # -- navigation ---------------------------------------------------------

    def show_editor(self, name: str) -> None:
        """Show one editor through the shell's own selection API, or refuse.

        `MainWindow.show_editor` returns silently for a name it does not have, so
        the name is checked here first: a silent no-op would leave the previous
        editor on screen and the capture would be of the wrong surface.
        """
        if name in ("Build", "Launch"):
            # These are project-action surfaces now, not destinations. They are
            # shown as the shell's stage for the capture, exactly the widget the
            # action's dialog re-parents. The shell's status line is cleared rather
            # than pointed at one of them: they own no status of their own and the
            # permanent zone still carries the project state.
            for host in self.window._hosts.values():
                host.setVisible(False)
            self.window._build.setVisible(name == "Build")
            self.window._launcher.setVisible(name == "Launch")
            if hasattr(self.window, "_active_host"):
                self.window._active_host = None
                self.window._status_context.setText("")
            self.pump()
            return
        self.editor(name)  # refuses an editor this shell does not have
        self.window.show_editor(name)
        self.pump()
        if not self.window._hosts[name].isVisible():
            raise SystemExit(f"editor {name!r} did not become the shown editor")

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
        """The current shell's Maps editor, driven by mode.

        Resolution goes through `editor`, so a shell without a Maps editor is a
        refusal rather than a substituted surface.
        """
        return _MapsAccessor(self.editor("Maps"))

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
    harness.show_editor("Maps")
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


def _extracted_project(harness: Harness, workspace: Path) -> Path:
    """Extract a real project from the canonical ROM, so every write is real."""
    from tools.webfoot.build import extract_project

    project = workspace / "workbench-capture-project"
    if project.is_dir():
        return project
    extract_project(ROM, project, harness.catalog, graphics=False)
    return project


def _dialogue_project(harness: Harness, workspace: Path) -> Path:
    """The same extracted project; kept as the name the dialogue state calls."""
    return _extracted_project(harness, workspace)


def capture_all(harness: Harness, workspace: Path, states: set[int] | None = None) -> None:
    """Capture the requested states, or the whole set when none is named.

    States 1-19 are one chained suite: each leaves the session, the project or the
    window geometry the next one reads, so they are captured as a unit. States 20+
    are self-contained and may be requested on their own, which is what makes a
    focused re-capture of one surface cheap.
    """
    chain = states is None or any(1 <= number <= LAST_CHAINED_STATE for number in states)
    chunk = states is None or any(
        LAST_CHAINED_STATE < number < FIRST_STRUCTURAL_STATE for number in states
    )
    structural = states is None or any(
        FIRST_STRUCTURAL_STATE <= number < FIRST_WARP_STATE for number in states
    )
    warp = states is None or any(
        FIRST_WARP_STATE <= number < FIRST_WARP_CREATE_STATE for number in states
    )
    warp_create = states is None or any(
        FIRST_WARP_CREATE_STATE <= number < FIRST_WARP_CANVAS_STATE for number in states
    )
    warp_canvas = states is None or any(
        number >= FIRST_WARP_CANVAS_STATE for number in states
    )
    if chain:
        if states is not None:
            print("note: states 1-19 are one chained suite; capturing all of them")
        _capture_chain(harness, workspace)
    if chunk:
        chunk_authoring_qa(harness, workspace, states)
    if structural:
        structural_qa(harness, workspace, states)
    if warp:
        warp_qa(harness, workspace, states)
    if warp_create:
        warp_create_qa(harness, workspace, states)
    if warp_canvas:
        warp_canvas_qa(harness, workspace, states)
    total = len(list(harness.out.glob("*.png")))
    print(f"\nwrote {total} PNG(s) to {harness.out}")


def _capture_chain(harness: Harness, workspace: Path) -> None:
    """Drive every required BEFORE/AFTER state through the real widgets.

    The correction's own required list is covered explicitly: the application
    shell, Graphics with and without a selection, the Maps editor in its browse
    and layout modes, the Maps editor's Objects mode, the shell and the Maps
    editor at a narrow width, and the Build action's report surface.
    """
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

    # 19. the Scene editor. It is not a strip destination, so the review set can
    # only reach it through a placement, and without a capture of its own the
    # shared-language claim had no evidence. Driven the way a user reaches it:
    # Objects mode enables View -> Detailed Editor, which opens this editor.
    #
    # The capture name says "empty" on purpose. View -> Detailed Editor is DISABLED
    # until a project is open, so this is the defensive no-project state, reached
    # here by enabling the action explicitly. It is the state that drew a status
    # sentence twice before the correction, which is why it is worth a capture.
    print("[19] scene editor (empty state)")
    harness.show_editor("Maps")
    harness.maps.set_mode("objects")
    harness.select_map(PROOF_MAP)
    harness.pump(6)
    harness.window._scene_action.setEnabled(True)
    harness.window._scene_action.trigger()
    harness.pump(8)
    harness.grab("19-scene-editor-empty")


def chunk_authoring_qa(
    harness: Harness, workspace: Path, states: set[int] | None = None
) -> list[Path]:
    """MAP-CHUNK-AUTHORING-001's states: create, paint, apply and place a chunk.

    Every step goes through the SHIPPED surface and the SHIPPED SDK: the real
    `ChunkAuthor` over the canonical image, the real `set_authored_chunk` write
    into a real extracted project in a temporary directory, and the real map
    preview that renders the authored plane through the layer's own character
    block. Nothing is mocked; the only thing the harness supplies is the chunk's
    NAME, because a `QInputDialog` cannot be typed into offscreen.
    """
    from PySide6.QtWidgets import QInputDialog

    written: list[Path] = []

    def shot(number: int, name: str, size: QSize | None = None) -> None:
        if states is None or number in states:
            written.append(harness.grab(name, size=size))

    project = _extracted_project(harness, workspace)
    harness.open_canonical()
    harness.session.set_project(project)
    harness.editor("Atlas").romOpened.emit()
    harness.show_editor("Maps")
    harness.maps.set_mode("layout")
    harness.select_map(PROOF_MAP)
    tab = harness.browser
    harness.choose_chunk_row(0)
    template = ChunkTemplate(PROOF_MAP, tab._slot.slot, tab._brush_ordinal)
    print(
        f"  template: {template.text}  vocabulary: "
        f"{len(tab.chunk_author().vocabulary(PROOF_MAP, tab._slot.slot))} entries"
    )

    # The action itself, with the name the harness supplies for the dialog.
    QInputDialog.getText = staticmethod(lambda *a, **k: ("qa-cave-floor", True))
    tab.create_chunk()
    harness.pump(12)
    print(f"  opened the chunk editor on {tab._chunk_identity}")
    shot(20, "20-chunk-editor-new")

    # A drag along a run of screen entries: the same gesture shape the map paint
    # surface uses, staging every changed cell as one history entry.
    vocabulary = tab.chunk_author().vocabulary(PROOF_MAP, tab._slot.slot)
    tab.set_chunk_brush(next(entry for entry in vocabulary if entry != tab.chunk_plane_entries()[0]))
    tab.begin_chunk_stroke()
    for row, column in ((4, 4), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6), (6, 6)):
        tab.paint_chunk_cell(row * 32 + column)
    tab.end_chunk_stroke()
    harness.pump(8)
    print(
        f"  staged {len(tab._edited_chunk_cells())} cell(s); "
        f"unsaved {tab.unsaved_edit_count()}"
    )
    shot(21, "21-chunk-editor-painted")
    shot(22, "22-chunk-editor-narrow", size=NARROW)
    harness.window.resize(DESKTOP)
    harness.pump()

    # Apply the chunk to the project (a real write into the extracted project),
    # then take it back to the map as the paint value and place one cell.
    print(f"  apply chunk -> {tab.apply_chunk()}")
    harness.pump(8)
    tab.use_chunk_as_brush()
    harness.pump(8)
    tab._on_cell_clicked(0)
    harness.pump(12)
    print(
        f"  brush: {tab._brush_authored}  staged placement: {tab._authored_cells}  "
        f"unsaved {tab.unsaved_edit_count()}"
    )
    shot(23, "23-chunk-authored-placement-on-map")
    return written


def _find_structural_map(harness: Harness) -> tuple[int, int, int, tuple | None]:
    """A map that gives a resizable dominant grid AND an unused slot, via the SDK.

    ``(map_index, layer_slot, free_slot, writer)`` where ``writer`` is a
    ``(map, layer, cell, ordinal)`` a *canonical* layer can legally take, for the
    unrelated project mutation the CQA-05 state needs. Read through
    `MapResizer` rather than by walking the browser list: selecting a map renders
    it, so probing 452 maps through the widget would be minutes of drawing for one
    answer.

    The resizable layer must be one the LAYOUT EDITOR offers (`MapLayoutEditor`
    marks a dominant grid of a single chunk read-only, because there is no legal
    substitute for it), or the Layer row would not list it and the states below
    could not be driven.
    """
    from tools.webfoot.formats.map_graphics import MapGraphicsError
    from tools.webfoot.map_resize import MapResizer, MapStructureError, read_map_structure

    def substitute(map_index: int, layers, excluded: int | None) -> tuple | None:
        """A canonical cell a real layout write can change, on another layer."""
        for other in layers:
            if other.slot == excluded or len(other.vocabulary) < 2:
                continue
            target_address = other.vocabulary[1].address
            cell = next(
                (
                    index
                    for index in range(other.cell_count)
                    if other.cells[index] != target_address
                ),
                0,
            )
            return (map_index, other.slot, cell, other.vocabulary[1].ordinal)
        return None

    project = harness.session.project_dir
    resizer = MapResizer(
        harness.session.map_image,
        structure=read_map_structure(project) if project is not None else None,
        profile=harness.session.profile,
    )
    fallback: tuple | None = None
    for index in range(resizer.map_entry_count):
        try:
            target = resizer.target(index)
        except (MapStructureError, MapGraphicsError, OSError):
            # A map whose structure cannot be read is a state, not a stop: the
            # search is for one that can be, and every other map is skipped.
            continue
        if target.shared_with:
            continue
        if fallback is None:
            fallback = substitute(index, target.editable_layers, None)
        if not target.free_slots:
            continue
        for layer in target.editable_layers:
            if layer.columns and layer.rows and layer.columns < 8 and len(
                layer.vocabulary
            ) >= 2:
                return (
                    index,
                    layer.slot,
                    target.free_slots[0],
                    substitute(index, target.editable_layers, layer.slot) or fallback,
                )
    raise SystemExit("no map gives both a resizable dominant grid and an unused slot")


def _shot_widget(harness: Harness, widget, path: Path) -> Path:
    """Grab one non-modal widget (a form) after its layout has settled."""
    widget.show()
    harness.pump(12)
    widget.grab().save(str(path), "PNG")
    print(f"  captured {path.name}  ({widget.width()}x{widget.height()})")
    return path


def _close_active_dialog(harness: Harness, out: Path | None) -> None:
    """Grab the modal dialogue an action opened, then close it.

    A refused resize opens the REAL `QMessageBox`, which runs a nested event loop:
    a zero-delay timer inside that loop is the only place a capture can be taken.
    The dialogue is always closed, whether or not its picture was wanted, or the
    action would never return.
    """
    from PySide6.QtWidgets import QApplication, QDialog

    dialog = QApplication.activeModalWidget()
    if not isinstance(dialog, QDialog):
        print("  (no modal dialogue appeared)")
        return
    harness.pump(16)
    if out is not None:
        dialog.grab().save(str(out), "PNG")
        print(f"  captured {out.name}  ({dialog.width()}x{dialog.height()})")
    dialog.close()


def structural_qa(
    harness: Harness, workspace: Path, states: set[int] | None = None
) -> list[Path]:
    """MAP-RESIZE-AND-LAYERS-001's states: resize a map, author a layer, paint it.

    Every step goes through the SHIPPED surface and the SHIPPED SDK: the real
    `MapResizer`/`MapPainter` over the canonical image, the real
    `set_layer_resize`/`set_authored_layer`/`set_layout_cells` writes into a real
    extracted project in a temporary directory, and the real map editor's own
    widgets and forms. Nothing is mocked; the harness supplies only what a mouse
    and a keyboard would.
    """
    from PySide6.QtCore import QTimer

    from tools.webfoot.map_paint import set_layout_cells

    written: list[Path] = []

    def shot(number: int, name: str, size: QSize | None = None) -> None:
        if states is None or number in states:
            written.append(harness.grab(name, size=size))

    def form(number: int, name: str, widget) -> None:
        if states is None or number in states:
            written.append(_shot_widget(harness, widget, harness.out / f"{name}.png"))

    project = _extracted_project(harness, workspace)
    harness.open_canonical()
    harness.session.set_project(project)
    harness.editor("Atlas").romOpened.emit()
    harness.show_editor("Maps")

    index, slot, free_slot, writer = _find_structural_map(harness)
    print(
        f"  structural target: map:{index:04d} BG{slot} resizable, BG{free_slot} "
        f"unused, unrelated writer {writer}"
    )
    harness.select_map(index)
    harness.pump(8)
    harness.maps.set_mode("layout")
    harness.pump(8)
    tab = harness.browser
    target = tab.structure_target()
    if target is None:
        raise SystemExit(f"map:{index:04d} has no structural view in the surface")
    layer = target.layer(slot)
    row = tab._layer_combo.findData(slot)
    if row < 0:
        raise SystemExit(f"BG{slot} is not offered in the Layer row")
    tab._layer_combo.setCurrentIndex(row)
    harness.pump(8)
    if tab._slot is None or tab._slot.slot != slot:
        raise SystemExit(f"the editor did not select BG{slot}")

    # 40. the retail map, before anything is staged.
    print("[40] retail map, before the resize")
    shot(40, "40-retail-map-before-resize")

    # 41. the resize form as it opens: the current grid, and a no-op rather than
    #     a refusal.
    print("[41] resize form, opened")
    dialog = tab.build_resize_dialog()
    if dialog is None:
        raise SystemExit("the resize form could not be offered")
    form(41, "41-resize-form-opened", dialog)

    # 42. the dimensions changed, and the preview naming the new cells' chunk.
    grown_columns = min(8, layer.columns + 1)
    grown_rows = layer.rows
    dialog._columns.setValue(grown_columns)
    dialog._rows.setValue(grown_rows)
    harness.pump(8)
    fill = dialog._fill.currentData()
    print(f"  resize form: {grown_columns}x{grown_rows} fill {fill} -> {dialog.summary_text()}")
    form(42, "42-resize-form-grown-dimensions", dialog)
    dialog.reject()
    harness.pump(6)

    # 43. the staged resize: the canvas draws the grown plane and the cells the
    #     growth added, initialized to the chosen chunk.
    print(f"[43] stage the resize -> {tab.apply_resize(grown_columns, grown_rows, fill)}")
    harness.pump(12)
    print(
        f"  staged: {sorted(tab._staged_resizes)}  dirty {tab.unsaved_edit_count()}  "
        f"grid {tab.structure_target().layer(slot).columns}x"
        f"{tab.structure_target().layer(slot).rows}"
    )
    shot(43, "43-resize-staged-initialized-cells")

    # 44/45. undo restores the retail grid; redo the authored one.
    print("[44] undo the resize")
    tab._undo_stack.undo()
    harness.pump(12)
    print(
        f"  after undo: staged {sorted(tab._staged_resizes)}  grid "
        f"{tab.structure_target().layer(slot).columns}x"
        f"{tab.structure_target().layer(slot).rows}"
    )
    shot(44, "44-resize-undo-retail-grid")

    print("[45] redo the resize")
    tab._undo_stack.redo()
    harness.pump(12)
    print(
        f"  after redo: staged {sorted(tab._staged_resizes)}  grid "
        f"{tab.structure_target().layer(slot).columns}x"
        f"{tab.structure_target().layer(slot).rows}"
    )
    shot(45, "45-resize-redo-grown-grid")

    # 46. Apply: the one SDK write, and the surface now reads the project's grid.
    #     This is also the "layer list before creation" state: nothing between here
    #     and the new-layer form changes a pixel, so a capture of its own would be
    #     the same picture under a second name.
    print(f"[46] apply the resize -> {tab.apply_to_project()}")
    harness.pump(12)
    committed = tab.structural_layer(index, slot)
    print(f"  project grid: {committed.columns}x{committed.rows} resized {committed.resized}")
    shot(46, "46-resize-applied-project-grid")

    # 48. the new-layer form: the unused slot, the template, the dimensions.
    print("[48] new-layer form")
    new_form = tab.build_new_layer_dialog()
    if new_form is None:
        raise SystemExit("the new-layer form could not be offered")
    # The template is named explicitly: the form defaults to the first supported
    # dominant layer, which on some maps is a grid of a single chunk - and an
    # authored layer copied from one would be read-only, so the painting states
    # below could not be driven. `slot` is a layer this harness measured as using
    # more than one chunk.
    template_row = new_form._template.findData(slot)
    if template_row < 0:
        raise SystemExit(f"BG{slot} is not offered as a template")
    new_form._template.setCurrentIndex(template_row)
    new_form._columns.setValue(2)
    new_form._rows.setValue(2)
    harness.pump(8)
    request = new_form.request()
    print(f"  new-layer form: {request} -> {new_form.summary_text()}")
    form(48, "48-new-layer-form", new_form)
    new_form.reject()
    harness.pump(6)

    # 49. created: the layer list and the Layer row both carry the authored layer.
    print(f"[49] create the layer -> {tab.apply_new_layer(*request)}")
    harness.pump(12)
    authored = tab.structural_layer(index, request[1])
    print(
        f"  authored {authored.identity} {authored.columns}x{authored.rows}  "
        f"dirty {tab.unsaved_edit_count()}"
    )
    shot(49, "49-layer-list-after-creation")

    # 50. the authored layer selected in the existing map editor.
    print("[50] select the authored layer")
    tab._layer_combo.setCurrentIndex(tab._layer_combo.findData(request[1]))
    harness.pump(12)
    slot_view = tab._slot
    print(
        f"  editor slot BG{slot_view.slot} grid "
        f"{slot_view.grid.columns}x{slot_view.grid.rows} choices "
        f"{len(slot_view.choices)} offsets "
        f"{sorted({cell.offset for cell in slot_view.cells})}"
    )
    shot(50, "50-authored-layer-selected")

    # 51. painted: a stroke over the authored grid, one command per gesture.
    print("[51] paint the authored layer")
    vocabulary = tab.structural_layer(index, request[1]).vocabulary
    brush = next(
        (choice.ordinal for choice in vocabulary if choice.ordinal != request[5]), None
    )
    if brush is not None:
        tab.set_brush_ordinal(brush)
    cells = [
        cell
        for cell in (0, 1, slot_view.grid.columns, slot_view.grid.columns + 1)
        if cell < slot_view.grid.cell_count
    ]
    tab.begin_paint_stroke()
    for cell in cells:
        tab.paint_cell(cell)
    tab.end_paint_stroke()
    harness.pump(12)
    print(
        f"  brush {brush} staged cells {tab._structural_cells}  "
        f"commands {tab._undo_stack.count()}  dirty {tab.unsaved_edit_count()}"
    )
    shot(51, "51-authored-layer-painted")

    # 52. an unrelated project mutation, made through the SDK and broadcast by the
    #     shell exactly as another editor's write would be.
    print("[52] unrelated project mutation with a staged structural edit")
    mutated = False
    if writer is not None:
        write_map, write_slot, write_cell, write_ordinal = writer
        mutated = set_layout_cells(
            project,
            harness.session.profile,
            harness.session.map_image,
            {(write_map, write_slot, write_cell): write_ordinal},
        )
        print(
            f"  unrelated SDK write map:{write_map:04d} BG{write_slot} cell "
            f"{write_cell} -> ordinal {write_ordinal}: {mutated}"
        )
    harness.window._on_project_changed()
    harness.pump(12)
    print(
        f"  after the mutation: staged layer {list(tab._staged_layers)} "
        f"staged cells {len(tab._structural_cells)} "
        f"dirty {tab.unsaved_edit_count()}"
    )
    shot(52, "52-unrelated-mutation-keeps-staged-structure")

    # 53. a genuine session/image replacement, through the shell's own open path.
    print("[53] session replacement")
    harness.session.open_rom(ROM, harness.catalog)
    harness.editor("Atlas").romOpened.emit()
    harness.show_editor("Maps")
    harness.pump(10)
    print(
        f"  after the replacement: staged resizes {len(tab._staged_resizes)} "
        f"staged layers {len(tab._staged_layers)} "
        f"staged cells {len(tab._structural_cells)} "
        f"dirty {tab.unsaved_edit_count()}"
    )
    harness.select_map(index)
    harness.pump(8)
    # A session change drops the edit mode with the staging (a new ROM starts in
    # view mode), so the surface is put back into Layout the way a person would,
    # or the capture would be of the browse text rather than of the structural
    # section stating what survived.
    harness.maps.set_mode("layout")
    harness.pump(10)
    shot(53, "53-session-replacement-clears-staged-structure")

    # 54. the structural surface at the narrow width.
    print("[54] narrow window")
    shot(54, "54-structural-surface-narrow", size=NARROW)
    harness.window.resize(DESKTOP)
    harness.pump(8)

    # 55/56. the validation states: a shrink refused in the form, and the same
    #        refusal as the SDK's own error dialogue.
    print("[55] the resize form refuses a shrink")
    tab._layer_combo.setCurrentIndex(tab._layer_combo.findData(slot))
    harness.pump(8)
    shrink = tab.build_resize_dialog()
    if shrink is None:
        raise SystemExit("the resize form could not be offered for the refusal")
    shrink._columns.setValue(max(1, committed.columns - 1))
    harness.pump(8)
    print(f"  refusal: {shrink.summary_text()}")
    form(55, "55-resize-form-refuses-a-shrink", shrink)
    shrink.reject()
    harness.pump(6)

    print("[56] the refusal as the SDK's own error dialogue")
    wanted = states is None or 56 in states
    out = harness.out / "56-validation-error-dialog.png" if wanted else None
    QTimer.singleShot(250, lambda: _close_active_dialog(harness, out))
    refused = tab.apply_resize(max(1, committed.columns - 1), committed.rows, fill)
    harness.pump(10)
    print(f"  apply_resize refused -> {refused}")
    if out is not None and out.is_file():
        written.append(out)
    return written


def warp_qa(
    harness: Harness, workspace: Path, states: set[int] | None = None
) -> list[Path]:
    """MAP-WARP-WORKBENCH-001's states: the Maps editor's Warps mode.

    Every step goes through the SHIPPED surface and the SHIPPED SDK: the real
    transition authority over the canonical image, the real
    `set_transition_edits`/`remove_transition_edit` writes into a real extracted
    project in a temporary directory, and the mode's own widgets. The map with a
    retargetable connection, the map with a 169-class connection and the
    destination with no connection back are all *found* through the authority, not
    hard-coded, so the capture follows whatever the open image actually holds.
    """
    from tools.webfoot import map_transitions as map_transitions_sdk
    from tools.webfoot.maps import MapIdentity

    written: list[Path] = []

    def shot(number: int, name: str, size: QSize | None = None) -> None:
        if states is None or number in states:
            written.append(harness.grab(name, size=size))

    project = _extracted_project(harness, workspace)
    harness.open_canonical()
    harness.session.set_project(project)
    harness.editor("Atlas").romOpened.emit()
    harness.show_editor("Maps")
    harness.maps.set_mode("warps")
    harness.pump(10)
    tab = harness.maps.warps

    corpus = map_transitions_sdk.read_map_transitions(
        harness.session.map_image, harness.session.profile
    )
    retargetable = next(
        entry for entry in corpus.entries() if entry.record.has_raw_arrival_pair
    )
    refused = next(
        entry for entry in corpus.entries() if not entry.record.has_raw_arrival_pair
    )
    source = retargetable.identity.source
    # A connection whose retarget the surface ACCEPTS and which is a real change:
    # a destination other than the one the record already leads to, that has its
    # own connection back to the source (so an arrival can be derived), and whose
    # derived point lands inside that destination's walkable extent. All of that
    # is the surface's own judgement, so the harness asks the product and takes
    # the first pair it agrees to - it does not decide any of it itself.
    #
    # `doors_back[source][destination]` is the number of records in `destination`
    # that lead to `source`, computed in ONE pass over the corpus rather than one
    # `reciprocal_doors` call per candidate (which would be 452 rescans per
    # connection).
    doors_back: dict[int, dict[int, int]] = {}
    for other in corpus.entries():
        try:
            towards = corpus.destination(other.identity)
        except map_transitions_sdk.MapTransitionsError:
            continue
        doors_back.setdefault(towards.index, {})
        from_source = other.identity.source.index
        doors_back[towards.index][from_source] = (
            doors_back[towards.index].get(from_source, 0) + 1
        )

    target = None
    chosen = None
    tried = 0
    for entry in corpus.entries():
        if not entry.record.has_raw_arrival_pair:
            continue
        source_index = entry.identity.source.index
        try:
            retail_destination = corpus.destination(entry.identity)
        except map_transitions_sdk.MapTransitionsError:
            continue
        candidates = [
            index
            for index in sorted(doors_back.get(source_index, {}))
            if index != source_index and index != retail_destination.index
        ]
        if not candidates:
            continue
        mark = tab.undo_stack().index()
        tab.select_source_map(source_index)
        tab.select_row(entry.identity.index)
        harness.pump(2)
        for index in candidates:
            tried += 1
            if tab.stage_destination(index):
                target = MapIdentity(index)
                chosen = entry
                break
        if chosen is None:
            continue
        retargetable = chosen
        source = chosen.identity.source
        # `index()`, not `count()`: count() is the stack's depth and does not fall
        # as commands are undone, so a count-based loop never ends.
        while tab.undo_stack().index() > mark:
            tab.undo_stack().undo()  # back to retail for the first captures
        harness.pump(6)
        break
    if chosen is None:
        raise SystemExit(
            f"no destination this surface accepts was found ({tried} tried)"
        )
    # A destination with NO connection back: the retarget the toolkit refuses.
    underivable = None
    for index in range(corpus.map_count):
        candidate = MapIdentity(index)
        if candidate in (source, target):
            continue
        if not corpus.reciprocal_doors(source, candidate):
            underivable = candidate
            break

    print(
        f"  connections: {retargetable.identity} -> map:{target.index:04d}; "
        f"169-class {refused.identity}; underivable "
        + (f"map:{underivable.index:04d}" if underivable is not None else "none")
    )
    tab.select_source_map(source.index)
    tab.select_row(retargetable.identity.index)
    harness.pump(8)

    shot(60, "60-warps-list-retail")
    shot(61, "61-warps-selected-connection")

    print(f"  stage retarget -> map:{target.index:04d}: {tab.stage_destination(target.index)}")
    harness.pump(8)
    shot(62, "62-warps-staged-retarget")

    print(f"  undo -> {tab.undo_stack().count()} command(s)")
    tab.undo_stack().undo()
    harness.pump(8)
    shot(63, "63-warps-undo-retail")
    tab.undo_stack().redo()
    harness.pump(8)

    print(f"  apply -> {tab.apply_to_project()}")
    harness.pump(10)
    shot(64, "64-warps-applied-saved")

    print(f"  revert -> {tab.revert_selected()}")
    harness.pump(10)
    shot(65, "65-warps-reverted-retail")

    print(f"  169-class read-only: {refused.identity}")
    tab.select_source_map(refused.identity.source.index)
    tab.select_row(refused.identity.index)
    harness.pump(8)
    print(
        f"    editable={tab.selected_editable()} reason={tab.edit_refusal()!r}"
    )
    shot(66, "66-warps-class-169-read-only")

    if underivable is not None:
        print(f"  retarget with no connection back -> map:{underivable.index:04d}")
        tab.select_source_map(source.index)
        tab.select_row(0)
        harness.pump(6)
        print(f"    staged={tab.stage_destination(underivable.index)}")
        harness.pump(8)
    shot(67, "67-warps-retarget-refusal-status")

    shot(68, "68-warps-narrow", size=NARROW)
    harness.window.resize(DESKTOP)
    harness.pump(6)

    # The empty state: a map this image gives no connections at all.
    connections_per_map: dict[int, int] = {}
    for other in corpus.entries():
        index = other.identity.source.index
        connections_per_map[index] = connections_per_map.get(index, 0) + 1
    empty = next(
        (index for index in range(corpus.map_count) if not connections_per_map.get(index)),
        0,
    )
    print(f"  map with no connections: map:{empty:04d}")
    tab.select_source_map(empty)
    harness.pump(8)
    shot(69, "69-warps-map-with-no-connections")
    return written


def warp_create_qa(
    harness: Harness, workspace: Path, states: set[int] | None = None
) -> list[Path]:
    """MAP-WARP-CREATE-WORKBENCH-001's states: the Warps mode's Create action.

    Every step goes through the SHIPPED surface and the SHIPPED SDK: the real
    transition authority over the canonical image, the real
    `check_transition_creation` validation on each gesture, the real
    `set_transition_creations` write into a real extracted project in a temporary
    directory, and the mode's own widgets. The map with a usable base, the map with
    none and the map on a shared connection root are all FOUND through the
    authority, not hard-coded, so the capture follows whatever the open image holds.
    """
    from tools.webfoot import map_transitions as map_transitions_sdk
    from tools.webfoot.maps import MapIdentity

    written: list[Path] = []

    def shot(number: int, name: str, size: QSize | None = None) -> None:
        if states is None or number in states:
            written.append(harness.grab(name, size=size))

    project = _extracted_project(harness, workspace)
    harness.open_canonical()
    harness.session.set_project(project)
    harness.editor("Atlas").romOpened.emit()
    harness.show_editor("Maps")
    harness.maps.set_mode("warps")
    harness.pump(10)
    tab = harness.maps.warps

    corpus = map_transitions_sdk.read_map_transitions(
        harness.session.map_image, harness.session.profile
    )
    bases: dict[int, tuple] = {}
    for entry in corpus.entries():
        if entry.record.class_raw == map_transitions_sdk.CREATED_CLASS_RAW:
            bases.setdefault(entry.identity.source.index, []).append(entry)

    # A map with a usable base AND at least one existing connection, so the list has
    # context beside the new row.
    connections: dict[int, int] = {}
    for entry in corpus.entries():
        index = entry.identity.source.index
        connections[index] = connections.get(index, 0) + 1

    source_index = next(
        (
            index
            for index, entries in sorted(bases.items())
            if connections.get(index) and not corpus.shared_root_maps(MapIdentity(index))
        ),
        None,
    )
    if source_index is None:
        raise SystemExit("no map with a usable 566-class base was found")
    base = bases[source_index][0]
    base_record = base.record
    print(
        f"  base map: map:{source_index:04d} ({len(bases[source_index])} usable "
        f"base(s) of {connections.get(source_index, 0)} connection(s)); base "
        f"{base.identity}"
    )

    # A map whose only records are 169-class, or which has none at all.
    no_base = next(
        (
            index
            for index in range(corpus.map_count)
            if not bases.get(index) and not corpus.shared_root_maps(MapIdentity(index))
        ),
        None,
    )
    # A map whose selector-1 root another map shares.
    shared = next(
        (
            index
            for index in range(corpus.map_count)
            if corpus.shared_root_maps(MapIdentity(index))
        ),
        None,
    )

    tab.select_source_map(source_index)
    harness.pump(8)

    print(f"  create action: enabled={tab.create_action_enabled()} refusal={tab.creation_refusal()!r}")
    print(f"  open create form: {tab.open_creation()}")
    harness.pump(8)
    shot(70, "70-warps-create-form-opened")

    print(f"  author name: {tab.stage_creation_name('qa-new-door')}")
    harness.pump(8)
    print(f"    identity={tab.creation_identity()} reason={tab.creation_reason()!r}")
    shot(71, "71-warps-create-name-authored")

    offered = tab.creation_templates()
    print(f"  bases offered: {[label for label, _identity in offered]}")
    harness.pump(6)
    shot(72, "72-warps-create-base-selected")

    # A region that differs from the base's, stated positionally, plus a facing:
    # both are authored through the surface, so the staged creation is the author's.
    region = (
        (base_record.region.first[0], min(0xFFFF, base_record.region.first[1] + 16)),
        base_record.region.second,
    )
    print(f"  author region {region}: {tab.stage_creation_region(*region)}")
    print(f"  author facing East: {tab.stage_creation_facing(3)}")
    harness.pump(8)
    print(
        f"    staged={tab.staged_creation_count()} state="
        f"{tab.creation_form_state()['state']!r} reason={tab.creation_reason()!r}"
    )
    shot(73, "73-warps-create-staged-values")

    print(f"  select the created row: {tab.select_row(tab.row_count() - 1)}")
    harness.pump(8)
    shot(74, "74-warps-create-staged-row")

    print(f"  apply: {tab.apply_creations()}")
    harness.pump(10)
    print(f"    rows: {[tab.row_values(row) for row in range(tab.row_count())]}")
    shot(75, "75-warps-create-applied-saved")

    # Revert: a second, never-saved creation is discarded with no project residue.
    name = "qa-reverted-door"
    print(f"  author a second creation {name!r}")
    print(f"    close={tab.close_creation()} open={tab.open_creation()}")
    tab.stage_creation_name(name)
    tab.stage_creation_region(*region)
    tab.stage_creation_facing(3)
    harness.pump(8)
    print(f"    staged={tab.staged_creation_count()}")
    print(f"  revert: {tab.revert_creation()}")
    harness.pump(10)
    print(
        f"    staged={tab.staged_creation_count()} "
        f"file={(project / 'maps' / 'transition_creations.toml').is_file()}"
    )
    shot(76, "76-warps-create-reverted")

    print(f"  undo the revert: {tab.undo_stack().canUndo()}")
    tab.undo_stack().undo()
    harness.pump(8)
    print(f"    staged={tab.staged_creation_count()}")
    tab.undo_stack().redo()
    harness.pump(8)
    shot(77, "77-warps-create-undo-redo")

    # A duplicate of a name the project already creates.
    print(f"  duplicate name: close={tab.close_creation()} open={tab.open_creation()}")
    tab.stage_creation_name("qa-new-door")
    harness.pump(8)
    print(f"    reason={tab.creation_reason()!r} staged={tab.staged_creation_count()}")
    shot(78, "78-warps-create-duplicate-name-refused")

    if no_base is not None:
        print(f"  map with no usable base: map:{no_base:04d}")
        tab.select_source_map(no_base)
        harness.pump(8)
        print(f"    refusal={tab.creation_refusal()!r} open={tab.open_creation()}")
        harness.pump(8)
        # Inside the guard: a capture named for a refusal must not be written when
        # the corpus offered no map to refuse.
        shot(79, "79-warps-create-no-base-on-this-map")

    if shared is not None:
        print(f"  map on a shared connection root: map:{shared:04d}")
        tab.select_source_map(shared)
        harness.pump(8)
        print(f"    refusal={tab.creation_refusal()!r} open={tab.open_creation()}")
        harness.pump(8)
        shot(80, "80-warps-create-shared-root-refused")

    # The narrow window, with a form open and its values authored.
    print(f"  narrow: back to map:{source_index:04d} with the form open")
    tab.select_source_map(source_index)
    tab.open_creation()
    tab.stage_creation_name("qa-narrow-door")
    tab.stage_creation_region(*region)
    tab.stage_creation_facing(2)
    harness.pump(10)
    shot(81, "81-warps-create-narrow", size=NARROW)
    harness.window.resize(DESKTOP)
    harness.pump(6)
    return written


def warp_canvas_qa(
    harness: Harness, workspace: Path, states: set[int] | None = None
) -> list[Path]:
    """MAP-WARP-CANVAS-001's states: connections drawn on the Objects canvas.

    Every step goes through the SHIPPED surfaces and the SHIPPED SDK: the real
    `map_render` over the canonical image, the real transition authority, the real
    `set_transition_edits` write into a real extracted project in a temporary
    directory, and the Maps editor's own mode strip, canvas and connection list. The
    map with a region this canvas accepts, and the map whose records the authority
    refuses to retarget, are FOUND through the authority rather than hard-coded, so
    the capture follows whatever the open image actually holds.
    """
    from tools.webfoot import map_transitions as map_transitions_sdk
    from tools.webfoot.maps import MapIdentity

    written: list[Path] = []

    def shot(number: int, name: str, size: QSize | None = None) -> None:
        if states is None or number in states:
            written.append(harness.grab(name, size=size))

    project = _extracted_project(harness, workspace)
    harness.open_canonical()
    harness.session.set_project(project)
    harness.editor("Atlas").romOpened.emit()
    harness.show_editor("Maps")
    harness.pump(10)
    canvas = harness.maps.workspace
    warps = harness.maps.warps

    corpus = map_transitions_sdk.read_map_transitions(
        harness.session.map_image, harness.session.profile
    )
    per_map: dict[int, list] = {}
    for entry in corpus.entries():
        per_map.setdefault(entry.identity.source.index, []).append(entry)

    # One map carries every canvas state, on purpose: a map that holds BOTH a
    # connection the canvas may move and one the authority refuses shows the two
    # overlay states side by side on ONE render, and it keeps the capture from
    # rendering a second map (the canonical corpus holds maps whose render is
    # minutes long, which is not what this state is about). Both facts are asked of
    # the authority, never decided here.
    chosen = None
    for index, entries in sorted(per_map.items()):
        if corpus.shared_root_maps(MapIdentity(index)) or len(entries) > 4:
            continue
        editable = [entry for entry in entries if entry.record.has_raw_arrival_pair]
        refused = [entry for entry in entries if not entry.record.has_raw_arrival_pair]
        if not editable:
            continue
        if chosen is None:
            chosen = (index, editable[0], refused[0] if refused else None)
        if refused:
            chosen = (index, editable[0], refused[0])
            break
    if chosen is None:
        raise SystemExit("no map with an editable connection was found for the canvas")
    source_index, target, refused_entry = chosen

    def show_map(index: int) -> bool:
        """Show one map on the canvas the way the map list does."""
        for row in range(canvas._maps.count()):
            entry = canvas._maps.item(row).data(Qt.ItemDataRole.UserRole)
            if entry["identity"] == f"map:{index:04d}":
                canvas._maps.setCurrentRow(row)
                harness.pump(10)
                return True
        return False

    harness.maps.set_mode("objects")
    if not show_map(source_index):
        raise SystemExit(f"map:{source_index:04d} is not in the canvas's map list")
    print(
        f"  canvas map: map:{source_index:04d}; connections "
        f"{[entry.identity.key for entry in per_map[source_index]]}"
    )
    print(f"  drawn regions: { {k: (v.first, v.second) for k, v in canvas.transition_overlays().items()} }")
    shot(90, "90-warp-canvas-regions")

    print(f"  click the region of {target.identity}: switches to the Warps mode")
    canvas._on_overlay_clicked(target.identity)
    harness.pump(10)
    print(
        f"    mode={harness.maps.mode()} row={warps.selected_identity()} "
        f"region={warps.row_values(warps._table.currentRow())[2]!r}"
    )
    shot(91, "91-warp-canvas-click-selects-row")

    harness.maps.set_mode("objects")
    canvas._canvas.zoom_in()
    canvas._canvas.zoom_in()
    harness.pump(10)
    print(f"    the canvas marks the same connection: {canvas.selected_transition()}")
    shot(92, "92-warp-canvas-selected-region")

    region_before = canvas.transition_overlays()[target.identity.key]
    state = canvas._transition_overlays[target.identity.key].state
    before = (region_before.first[0], region_before.second[0])
    after = (before[0] + 24, before[1] + 18)
    print(f"  drag the region by {after[0] - before[0]}, {after[1] - before[1]}: {canvas._on_overlay_drag(state, before, after)}")
    harness.pump(10)
    print(f"    drawn now: {canvas.transition_overlays()[target.identity.key]}")
    shot(93, "93-warp-canvas-dragged-region")

    harness.maps.set_mode("warps")
    harness.pump(10)
    print(
        f"    the connection list states: {warps.row_values(warps._table.currentRow())}"
    )
    shot(94, "94-warp-canvas-warps-row-after-drag")

    harness.maps.set_mode("objects")
    print(f"  undo: {canvas._undo_stack.canUndo()}")
    canvas._undo_stack.undo()
    harness.pump(10)
    print(f"    drawn after undo: {canvas.transition_overlays()[target.identity.key]}")
    shot(95, "95-warp-canvas-undo-retail")

    # A connection the authority refuses to retarget: drawn, dashed, and refused on
    # a drag with the surface's own reason. It lives on the SAME canvas the states
    # above used, so no second map is rendered.
    if refused_entry is None:
        print("  (this image gives no map holding both classes; the read-only canvas "
              "state is not captured)")
        return written
    key = refused_entry.identity.key
    print(f"  169-class connection on the same map: {key}")
    print(f"    drawn: {canvas.transition_overlays().get(key)}")
    # Frame it: the read-only region can sit at a map edge, and a capture of half a
    # rectangle would not show the dashed edge the state exists to show.
    canvas._canvas.centerOn(canvas._transition_overlays[key])
    harness.pump(10)
    shot(96, "96-warp-canvas-class-169-read-only")
    wanted = states is None or 97 in states
    out = harness.out / "97-warp-canvas-drag-refused.png" if wanted else None
    state = canvas._transition_overlays[key].state
    region = state.region
    point = (region.first[0], region.second[0])
    QTimer.singleShot(250, lambda: _close_active_dialog(harness, out))
    print(f"    refusal: {canvas._on_overlay_drag(state, point, (point[0] + 20, point[1] + 20))}")
    harness.pump(10)
    if out is not None and out.is_file():
        print(f"  captured {out.name}")
        written.append(out)
    return written


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


def _parse_states(text: str) -> set[int]:
    """Parse `--states` into the set of state numbers it names."""
    wanted: set[int] = set()
    for chunk in text.replace(" ", "").split(","):
        if not chunk:
            continue
        if "-" in chunk:
            first, _, last = chunk.partition("-")
            wanted.update(range(int(first), int(last) + 1))
            continue
        wanted.add(int(chunk))
    known = {number for number, _name in STATES}
    unknown = sorted(wanted - known)
    if unknown:
        raise SystemExit(
            f"unknown state number(s) {unknown}; known states are "
            f"{sorted(known)}"
        )
    return wanted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="directory to write PNGs into")
    parser.add_argument("--probe", action="store_true", help="print real map facts")
    parser.add_argument(
        "--list", action="store_true", help="list the numbered capture states"
    )
    parser.add_argument(
        "--states",
        help="comma/range list of state numbers to capture (e.g. 20,21 or 1-6)",
    )
    args = parser.parse_args(argv)
    if args.list:
        for number, name in STATES:
            print(f"{number:>3}  {name}")
        return 0
    if args.probe:
        return _probe()
    if args.out is None:
        parser.error("--out is required")
    states = _parse_states(args.states) if args.states else None
    args.out.mkdir(parents=True, exist_ok=True)
    # The product's own wording carries "·", "×" and "→"; a cp1252 console would
    # otherwise end the run on the first one a state prints.
    sys.stdout.reconfigure(errors="replace")
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
        capture_all(harness, workspace, states)
    finally:
        harness.window.close()
        shutil.rmtree(workspace, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
