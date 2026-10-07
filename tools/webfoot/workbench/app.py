"""WORKBENCH-001 GUI shell; visual direction and information architecture
DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001.

`MainWindow` is a thin ``QMainWindow`` holding the shared `Session` and the ROM
profile catalog by constructor injection (no global state) and handing them to
whatever editor is mounted.

Structure, and the correction it answers
(``docs/research/UI_REFERENCE_MATRIX.md`` and
``docs/research/UI_FIDELITY_MATRIX.md``): a menu bar carrying
File / Edit / View / Tools / Help, one compact editor strip naming
[Atlas] [Inspector] [Maps] [Graphics] and the project actions, the active editor's
own workspace beneath it, and one status bar carrying the active editor's line
plus project state on the right.

This is the ROM-hacking editor model the human correction named - **menu bar ->
compact toolbar -> active editor workspace -> editor-local modes** - and not a
global tab strip listing every implementation panel. What changed from the
previous revision:

- **The eight-tab strip is gone.** The four primary editors are named on one
  compact strip; Build, Launch and the Scene editor are no longer permanent
  destinations because they are not editors a user works in continuously. Build
  and Run are project actions and live in the strip and the menus; the Scene
  editor is reached from the placement it belongs to.
- **Maps, Map and Map Browser are one Maps editor** (:class:`~.editors.MapsEditor`)
  with Browse / Layout / Objects modes, the way Porymap keeps Map / Events /
  Header / Connections inside one window.
- **Build and Launch became dialogs**, so their configuration is preserved
  without keeping two permanent workspaces alive for it.
- **Undo and Redo are real menu actions** routed to whichever editor owns a
  history, instead of being duplicated per panel.

Deliberately NOT built, per the reference set: a docking system, editor layout
profiles, LDtk's zen mode, or any control this product cannot actually drive.

This shell holds no ROM-format knowledge - no offsets, masks or record
constants; that all lives behind the SDK the Session calls.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..profile import RomProfileCatalog
from . import theme
from .atlas_browser import AtlasBrowserTab
from .build_panel import BuildPanelTab
from .editors import EditorHost, MapsEditor
from .graphics_tab import GraphicsTab
from .inspector import InspectorTab
from .launcher import LauncherTab
from .scene_tab import SceneTab
from .session import OPEN_ROM_FAILURES, Session

#: The primary editor destinations, in the order the strip shows them. Only these
#: are editors: a place where a user works on content.
_EDITORS = ("Atlas", "Inspector", "Maps", "Graphics")

#: Editors reachable from another editor rather than from the strip, kept as
#: stack pages. The Scene editor is opened from the placement that owns it.
_SECONDARY = ("Scene",)


class MainWindow(QMainWindow):
    def __init__(self, session: Session, catalog: RomProfileCatalog) -> None:
        super().__init__()
        self._session = session
        self._catalog = catalog

        self.setWindowTitle("DragonByte Z")

        self._atlas = AtlasBrowserTab(session, catalog)
        self._inspector = InspectorTab(session)
        self._maps = MapsEditor(session)
        self._graphics = GraphicsTab(session)
        # Not destinations: reached from an editor or from a project action.
        self._scene = SceneTab(session)
        self._build = BuildPanelTab(session, catalog)
        self._launcher = LauncherTab(session)

        #: Editor name -> host, so the strip and the switcher share one map.
        self._hosts: dict[str, EditorHost] = {}
        self._active_host: EditorHost | None = None
        # A QStackedWidget reports the *largest* minimum among all its pages, so one
        # tall editor would set the window's floor for the whole application. Plain
        # sibling widgets with explicit visibility avoid that: only the editor on
        # screen contributes a minimum.
        self._stage = QWidget()
        self._stage_layout = QVBoxLayout(self._stage)
        self._stage_layout.setContentsMargins(0, 0, 0, 0)
        self._stage_layout.setSpacing(0)
        self._editor_buttons: dict[str, QToolButton] = {}
        for title, widget in (
            ("Atlas", self._atlas),
            ("Inspector", self._inspector),
            ("Graphics", self._graphics),
        ):
            host = EditorHost(title)
            host.add_surface(widget)
            self._hosts[title] = host
            self._stage_layout.addWidget(host)
        # The Maps editor IS its own host: it owns internal modes, so wrapping a
        # host around it would put its status line one level too deep to find.
        self._hosts["Maps"] = self._maps
        self._stage_layout.addWidget(self._maps)
        for title, widget in (("Scene", self._scene),):
            host = EditorHost(title)
            host.add_surface(widget)
            self._hosts[title] = host
            self._stage_layout.addWidget(host)
        self._build_host = self._build
        self._launcher_host = self._launcher
        self._stage_layout.addWidget(self._build)
        self._stage_layout.addWidget(self._launcher)

        # Each primary editor declares the label it maintains as its own status
        # line; the shell draws that one while the editor is active.
        self._hosts["Atlas"].set_status_label(self._atlas._load_status)
        self._hosts["Graphics"].set_status_label(self._graphics._status)
        self._hosts["Scene"].set_status_label(self._scene._status)
        self._inspector_status = QLabel("No record selected.")
        self._inspector_status.setObjectName("dbzStatusLine")
        self._inspector_status.setProperty("dbzRole", "status")
        self._inspector._authoring_status.stateChanged.connect(
            self._inspector_status.setText
        )
        self._hosts["Inspector"].set_status_label(self._inspector_status)

        self._wire_editors()
        self.setCentralWidget(self._stage)
        # A window that cannot be made smaller than a tall monitor's work area
        # cannot be tiled beside anything. This is the floor; each editor's content
        # scrolls rather than clips below it.
        self.setMinimumSize(820, 560)
        self._build_actions()
        self._build_strip()
        self._build_menus()
        self._build_status_bar()
        self.show_editor("Atlas")
        self._refresh_identity()
        self._refresh_action_state()

    # -- wiring ---------------------------------------------------------------

    def _wire_editors(self) -> None:
        self._atlas.romOpened.connect(self._on_rom_opened)
        self._atlas.resultActivated.connect(self._on_result_activated)
        self._inspector.projectChanged.connect(self._on_project_changed)
        self._maps.projectChanged.connect(self._on_project_changed)
        self._maps.openSceneRequested.connect(self._open_scene_placement)
        self._maps.buildRunRequested.connect(self._build_and_run)
        self._maps.dirtyChanged.connect(self._refresh_identity)
        # A mode switch changes WHICH surface's history Edit -> Undo reaches, so the
        # two actions are re-enabled from the newly active stack.
        self._maps.modeChanged.connect(lambda _mode: self._refresh_undo_actions())
        self._graphics.projectChanged.connect(self._on_project_changed)
        self._scene.projectChanged.connect(self._on_project_changed)
        self._build.projectChanged.connect(self._on_project_changed)
        self._build.buildFinished.connect(self._on_build_finished)
        # Run availability lives with the ROM field that owns it, so a manually
        # chosen ROM arms Ctrl+R exactly as a build's output does.
        self._launcher.romChanged.connect(self._refresh_action_state)

    def _on_rom_opened(self) -> None:
        """A new image is open: EVERY surface re-reads it, one failure contained.

        CQA-06, second half. This is a session transition, so a single expected
        SDK failure while one panel re-reads the image must not stop the panels
        after it: a half-refreshed window shows the previous image's content
        beside the new one, which is exactly the session inconsistency the
        finding is about. Each peer is therefore refreshed through
        `_refresh_after_open`, which contains an expected failure and lets the
        rest proceed.

        Containment has to be here rather than only around `romOpened.emit()`:
        an exception raised inside a slot reached through a signal is printed by
        PySide and swallowed, so the emitting `try` never sees it and the window
        is left half-refreshed with no message. This is the observed behaviour,
        not a guess - it is what the CQA-06 slot test proved when it drove a peer
        failure through the signal.
        """
        failures: list[tuple[str, Exception]] = []
        for name, editor in (
            ("Atlas", self._atlas),
            ("Scene", self._scene),
            ("Graphics", self._graphics),
            ("Inspector", self._inspector),
            ("Maps", self._maps),
            ("Build", self._build),
            ("Launch", self._launcher),
        ):
            self._refresh_after_open(name, editor, failures)
        self._refresh_identity()
        self._refresh_action_state()
        if failures:
            self._report_refresh_failures(failures)

    def _refresh_after_open(self, name: str, editor, failures: list) -> None:
        """Re-read the open image into one peer, containing an expected failure."""
        try:
            editor.on_session_changed()
        except OPEN_ROM_FAILURES as exc:
            failures.append((name, exc))

    def _report_refresh_failures(self, failures: list) -> None:
        """Say which panels could not re-read an image that DID open.

        The image is open and the session holds it, so claiming a failed open
        would be false; the message names the panels, the reason, and what is
        still true.
        """
        names = ", ".join(name for name, _ in failures)
        first = failures[0][1]
        self._status_context.setText(f"Opened, but {names} could not refresh: {first}")
        QMessageBox.warning(
            self,
            "Open ROM",
            f"The image opened, but these panels could not re-read it: {names}.\n\n"
            f"{first}\n\nThe image is open and the session holds it. Open it again "
            "to retry the re-read.",
        )

    def _on_project_changed(self) -> None:
        """Any editor mutated the project: re-arm the shell and every peer.

        This is NOT the ROM/session event. Every editor's `projectChanged`
        arrives here - a dialogue Apply, a palette Apply or Undo, a Scene NPC
        add, a placement drag, a Save As - and none of them replaces the open
        image. So each peer is asked to re-read what a project can change
        (`on_project_mutated`) rather than to re-read a *session*
        (`on_session_changed`), because the session entry point is where staged
        in-memory authoring state is legitimately dropped. CQA-05 was exactly
        this conflation: one callback answering two different events, so a
        mutation in any editor silently discarded the Map Browser's staged
        layout edits, the placement undo history and the mode strip's
        truthfulness.
        """
        self._inspector.on_project_mutated()
        self._launcher.on_project_mutated()
        self._scene.on_project_mutated()
        self._maps.on_project_mutated()
        self._graphics.on_project_mutated()
        self._build.on_project_mutated()
        self._refresh_identity()
        self._refresh_action_state()

    def _on_build_finished(self) -> None:
        self._launcher.on_session_changed()
        self._refresh_identity()
        self._refresh_action_state()

    def _on_result_activated(self, result: dict) -> None:
        self._session.selected_result = result
        self._inspector.show_result(result)
        self.show_editor("Inspector")

    def _open_scene_placement(self, map_id: str, placement_identity: str) -> None:
        """Follow a semantic map selection into the Scene editor.

        The Scene editor is not a destination on the strip: it belongs to the
        placement that was selected, so it is opened from there.
        """
        self._scene.select_placement(map_id, placement_identity)
        self._show_host(self._hosts["Scene"])

    # -- actions --------------------------------------------------------------

    def _build_actions(self) -> None:
        """Every project action, defined once and shared by menu, strip and dialog."""
        self._action_open_rom = QAction("Open ROM\u2026", self)
        self._action_open_rom.setShortcut(QKeySequence("Ctrl+O"))
        self._action_open_rom.setStatusTip("Identify and open a game image")
        self._action_open_rom.triggered.connect(self._open_rom)

        self._action_open_project = QAction("Open Project\u2026", self)
        self._action_open_project.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self._action_open_project.setStatusTip("Open an extracted Webfoot project")
        self._action_open_project.triggered.connect(self._build.open_project_dialog)

        self._action_extract_project = QAction("Extract Project\u2026", self)
        self._action_extract_project.setStatusTip(
            "Write a project from the open ROM, which is never modified"
        )
        self._action_extract_project.triggered.connect(self._build.extract_project_dialog)

        self._action_output_dir = QAction("Output Directory\u2026", self)
        self._action_output_dir.setStatusTip("Where a built ROM is written")
        self._action_output_dir.triggered.connect(self._build.choose_output_dialog)

        self._action_validate = QAction("Validate", self)
        self._action_validate.setShortcut(QKeySequence("Ctrl+Shift+V"))
        self._action_validate.setStatusTip("Validate the open project against the open ROM")
        self._action_validate.triggered.connect(self._validate_project)

        self._action_build = QAction("Build", self)
        self._action_build.setShortcut(QKeySequence("Ctrl+B"))
        self._action_build.setStatusTip("Build the validated project into a new ROM")
        self._action_build.triggered.connect(self._build_project)

        self._action_run = QAction("Run", self)
        self._action_run.setShortcut(QKeySequence("Ctrl+R"))
        self._action_run.setStatusTip("Launch the last built ROM in mGBA")
        self._action_run.triggered.connect(self._launcher.launch_built_rom)

        self._action_undo = QAction("Undo", self)
        self._action_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self._action_undo.setStatusTip("Undo the active editor's last change")
        self._action_undo.triggered.connect(self._undo)

        self._action_redo = QAction("Redo", self)
        self._action_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self._action_redo.setStatusTip("Redo the active editor's last undone change")
        self._action_redo.triggered.connect(self._redo)

        self._action_quit = QAction("Quit", self)
        self._action_quit.setShortcut(QKeySequence.StandardKey.Quit)
        self._action_quit.triggered.connect(self.close)

    def _build_strip(self) -> None:
        """One compact strip: the editors, then the project actions.

        The ROM-editor model puts workspace selection and project actions on the
        same thin line above the workspace. Nothing is represented twice: an action
        that lives here does not also get a permanent workspace.
        """
        bar = QToolBar("Editor")
        bar.setObjectName("dbzEditorStrip")
        bar.setMovable(False)
        bar.setFloatable(False)
        bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)

        picker = QWidget()
        picker_row = QHBoxLayout(picker)
        picker_row.setContentsMargins(0, 0, 0, 0)
        picker_row.setSpacing(2)
        for title in _EDITORS:
            button = QToolButton()
            button.setText(title)
            button.setCheckable(True)
            button.setAutoRaise(True)
            button.setToolTip(f"Work in the {title} editor")
            button.setAccessibleName(f"{title} editor")
            button.clicked.connect(lambda _checked=False, name=title: self.show_editor(name))
            self._editor_buttons[title] = button
            picker_row.addWidget(button)
        bar.addWidget(picker)
        bar.addSeparator()

        for widget in (self._action_open_rom, self._action_open_project):
            bar.addAction(widget)
        bar.addSeparator()
        for widget in (self._action_validate, self._action_build, self._action_run):
            bar.addAction(widget)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bar.addWidget(spacer)
        self._strip = bar
        self.addToolBar(bar)

    def _build_menus(self) -> None:
        """Global commands only, in the ROM-editor order the correction named."""
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self._action_open_rom)
        file_menu.addAction(self._action_open_project)
        file_menu.addAction(self._action_extract_project)
        file_menu.addSeparator()
        file_menu.addAction(self._action_output_dir)
        file_menu.addSeparator()
        file_menu.addAction(self._action_quit)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(self._action_undo)
        edit_menu.addAction(self._action_redo)

        view_menu = self.menuBar().addMenu("&View")
        for title in _EDITORS:
            action = QAction(title, self)
            action.setShortcut(QKeySequence(f"Ctrl+{_EDITORS.index(title) + 1}"))
            action.triggered.connect(
                lambda _checked=False, name=title: self.show_editor(name)
            )
            view_menu.addAction(action)
        view_menu.addSeparator()
        self._scene_action = QAction("Detailed Editor", self)
        self._scene_action.setStatusTip(
            "Show the placement currently selected in the Maps editor's Objects mode"
        )
        self._scene_action.triggered.connect(
            lambda: self._show_host(self._hosts["Scene"])
        )
        view_menu.addAction(self._scene_action)
        view_menu.addSeparator()
        self._action_compact = QAction("Compact Strip", self)
        self._action_compact.setCheckable(True)
        self._action_compact.setStatusTip(
            "Hide the editor strip to give the workspace the full window"
        )
        self._action_compact.toggled.connect(self._on_compact_toggled)
        view_menu.addAction(self._action_compact)

        tools_menu = self.menuBar().addMenu("&Tools")
        tools_menu.addAction(self._action_validate)
        tools_menu.addAction(self._action_build)
        tools_menu.addAction(self._action_run)
        tools_menu.addSeparator()
        self._action_build_report = QAction("Build and Validation Report\u2026", self)
        self._action_build_report.setStatusTip(
            "Open the report surface: stage, output directory and the last result"
        )
        self._action_build_report.triggered.connect(self.open_build_report)
        tools_menu.addAction(self._action_build_report)
        self._action_run_settings = QAction("Run Configuration\u2026", self)
        self._action_run_settings.setStatusTip(
            "Choose the ROM to launch and the mGBA executable"
        )
        self._action_run_settings.triggered.connect(self.open_run_configuration)
        tools_menu.addAction(self._action_run_settings)

        help_menu = self.menuBar().addMenu("&Help")
        about = QAction("About DragonByte Z", self)
        about.triggered.connect(self._show_about)
        help_menu.addAction(about)

    def _build_status_bar(self) -> None:
        """ONE compact native status line.

        Left: what the active editor is showing. Right: project state, in the
        permanent zone so a transient message cannot hide it. The shell owns this
        one label and copies each editor's own status line into it, so a fact is
        never on screen twice and the bar's contents never depend on mount order.
        """
        self._status_context = QLabel("Open a game image to begin.")
        self._status_context.setProperty("dbzRole", "status")
        self._status_context.setMinimumWidth(0)
        self._status_context.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._status_project = QLabel("")
        self._status_project.setProperty("dbzRole", "status")
        self._status_source: EditorHost | None = None
        #: The objects currently wired to the status bar, so a delivery can be
        #: attributed to the editor on screen rather than to a hidden one.
        self._status_emitters: list = []
        status = self.statusBar()
        status.addWidget(self._status_context, 1)
        # An explicit spacer rather than stylesheet padding: a QStatusBar lays its
        # items out itself and a `padding` rule on a label does not widen the gap
        # between items, which left two labels reading as one run-on string.
        gap = QWidget()
        gap.setFixedWidth(theme.SPACE_XL)
        gap.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        status.addPermanentWidget(gap)
        status.addPermanentWidget(self._status_project)

    # -- editor switching -----------------------------------------------------

    def show_editor(self, name: str) -> None:
        """Show a primary editor. Never changes what that editor can do."""
        if name not in self._hosts:
            return
        if name not in _EDITORS:
            self._show_host(self._hosts[name])
            return
        for title, button in self._editor_buttons.items():
            button.setChecked(title == name)
        self._show_host(self._hosts[name])
        self._sync_scene_action()

    def _show_host(self, host: EditorHost) -> None:
        """Show one editor and hide the rest, so only it contributes a minimum."""
        for candidate in self._hosts.values():
            candidate.setVisible(candidate is host)
        self._build.setVisible(host is self._build_host)
        self._launcher.setVisible(host is self._launcher_host)
        self._active_host = host
        self._mount_editor_status(host)
        self._refresh_undo_actions()

    def current_editor_name(self) -> str:
        """The active editor, tracked explicitly.

        Read from an attribute rather than from visibility, because a widget that
        has never been shown reports ``isVisible() is False`` in a headless test -
        the window itself may not be mapped - which would make "which editor is
        active" indistinguishable from "no editor is active".
        """
        for title, candidate in self._hosts.items():
            if candidate is self._active_host:
                return title
        return ""

    def _mount_editor_status(self, host: EditorHost) -> None:
        """Point the shell's one status label at the active editor's own line.

        The shell owns the label and copies text into it; every editor keeps
        maintaining its own status line exactly as before, which is also the text
        its own tests read. Re-parenting those labels into the bar instead made its
        contents depend on mount order, and copying once at mount time missed every
        later change - so the active editor's status is *tracked* while it is on
        screen and released when another editor takes over.
        """
        previous = self._status_source
        if previous is not None and previous is not host:
            self._release_status(previous)
        self._status_source = host
        line = getattr(host, "status_line", None)
        self._status_context.setText(line() if callable(line) else "")
        # Start a fresh list per mount: keeping the previous host's emitters would
        # let a hidden editor still be recognised as an acceptable source.
        self._status_emitters = []
        self._track_status_carriers(host)

    #: The signals a status carrier may publish on. A plain QLabel has no such
    #: signal of its own; the editors that keep a live line publish `statusChanged`
    #: and the chips `stateChanged`.
    _STATUS_SIGNALS = ("textChanged", "stateChanged", "statusChanged")

    def _track_status_carriers(self, host: EditorHost) -> None:
        """Follow every signal the active editor publishes its status on.

        A Qt signal's ``sender()`` is the object that *emits*, which for
        ``GraphicsTab.statusChanged`` is the tab rather than the host wrapper or its
        label. Comparing against the stored signal objects does not work in PySide
        either - each attribute access returns a fresh bound-signal wrapper, so
        object identity fails and a real update is rejected. The emitting *object*
        is remembered instead, and it is a stable identity.

        The editor the host wraps is included, because for a plain host that is
        where the line actually lives.
        """
        carriers = [host, host.status_label(), host.signal_source()]
        for carrier in carriers:
            if carrier is None:
                continue
            if carrier is not host:
                label = carrier if isinstance(carrier, QLabel) else None
                if label is not None:
                    label.setObjectName("dbzStatusLine")
            for name in self._STATUS_SIGNALS:
                signal = getattr(carrier, name, None)
                if signal is None:
                    continue
                self._connect(signal, self._on_status_published)
                self._status_emitters.append(carrier)

    def _release_status(self, host: EditorHost) -> None:
        """Stop tracking an editor's status once it is no longer on screen."""
        carriers = [host, host.status_label()]
        for carrier in carriers:
            if carrier is None:
                continue
            for name in self._STATUS_SIGNALS:
                signal = getattr(carrier, name, None)
                if signal is None:
                    continue
                try:
                    signal.disconnect(self._on_status_published)
                except (RuntimeError, TypeError):
                    # Never connected, or already gone: neither is an error.
                    pass
        self._status_emitters = []

    @staticmethod
    def _connect(signal, slot) -> None:
        """Connect a signal, tolerating one that cannot take this slot."""
        try:
            signal.connect(slot)
        except (RuntimeError, TypeError):
            pass

    def _on_status_published(self, *_args) -> None:
        """Mirror the active editor's own status line into the shell's label.

        Accepts a message only from a carrier belonging to the editor on screen, so
        a hidden editor finishing work in the background cannot overwrite the line
        for the one the user is looking at. The line is always *re-read from the
        editor* rather than taken from the signal's argument, because the two modes
        of the Maps editor publish on the same signal with different labels and the
        label that counts is the one the editor currently declares.
        """
        if self._status_source is None:
            return
        source = self.sender()
        if source is None or any(
            source is carrier for carrier in self._status_emitters
        ):
            self._status_context.setText(self._status_source.status_line())

    def current_editor_name(self) -> str:
        """The active editor, tracked explicitly.

        Read from an attribute rather than from visibility, because a widget that
        has never been shown reports ``isVisible() is False`` in a headless test -
        the window itself may not be mapped - which would make "which editor is
        active" indistinguishable from "no editor is active".
        """
        for title, candidate in self._hosts.items():
            if candidate is self._active_host:
                return title
        return ""

    def _sync_scene_action(self) -> None:
        self._scene_action.setEnabled(self._maps.mode() == "objects")

    def _on_compact_toggled(self, compact: bool) -> None:
        self._strip.setVisible(not compact)

    # -- project actions ------------------------------------------------------

    def _undo(self) -> None:
        stack = self._active_undo_stack()
        if stack is not None and stack.canUndo():
            stack.undo()

    def _redo(self) -> None:
        stack = self._active_undo_stack()
        if stack is not None and stack.canRedo():
            stack.redo()

    def _active_undo_stack(self):
        host = self._active_host
        if host is not None:
            stack = host.undo_stack()
            if stack is not None:
                return stack
        for widget in (self._build, self._launcher):
            if widget.isVisible():
                return getattr(widget, "_undo_stack", None)
        return None

    def _refresh_undo_actions(self) -> None:
        stack = self._active_undo_stack()
        try:
            can_undo = stack is not None and stack.canUndo()
            can_redo = stack is not None and stack.canRedo()
        except RuntimeError:
            # The stack's C++ object is already gone. That happens when a stack
            # emits its last canUndo/canRedo change while its window is being torn
            # down, which a headless suite does between tests. "There is no history
            # to offer" is the honest answer there, and it is not a user-visible
            # failure, so the two actions are simply disabled.
            self._action_undo.setEnabled(False)
            self._action_redo.setEnabled(False)
            return
        self._action_undo.setEnabled(can_undo)
        self._action_redo.setEnabled(can_redo)
        if stack is None:
            return
        # Every stack the active editor has offered is wired once and kept wired,
        # because switching modes switches stacks: a single "already wired" flag
        # would leave the second and later stacks unable to update these actions.
        wired = getattr(self, "_undo_wired", None)
        if wired is None:
            wired = self._undo_wired = set()
        key = id(stack)
        if key in wired:
            return
        wired.add(key)
        stack.canUndoChanged.connect(lambda _ok: self._refresh_undo_actions())
        stack.canRedoChanged.connect(lambda _ok: self._refresh_undo_actions())

    def _validate_project(self) -> None:
        self._build.validate_project()
        self._refresh_identity()
        self._refresh_action_state()

    def _build_project(self) -> None:
        self._build.build_project()
        self._refresh_identity()
        self._refresh_action_state()

    def _build_and_run(self) -> None:
        """Preserve Validate -> Build -> Launch; the Maps editor owns no build logic."""
        self._build.validate_project()
        if not self._session.validation_current:
            self._refresh_identity()
            self._refresh_action_state()
            return
        self._build.build_project()
        if not self._session.build_current:
            self._refresh_identity()
            self._refresh_action_state()
            return
        self._launcher.launch_built_rom()
        self._refresh_identity()
        self._refresh_action_state()

    def open_build_report(self) -> None:
        """Show the Build surface and its configuration.

        Build is a project action, not a permanent editor. Its report and its
        configuration live in one conversation opened from the action that uses
        them, so nothing it holds was discarded and no workspace is kept alive for
        a panel nobody is reading.
        """
        self._show_surface_dialog(
            "Build and validation",
            self._build,
            "Validate and Build write a NEW ROM from the open project. The base ROM "
            "is never modified.",
        )

    def open_run_configuration(self) -> None:
        """Show the Run surface and its configuration."""
        self._show_surface_dialog(
            "Run configuration",
            self._launcher,
            "Run starts mGBA on a ROM that already exists. This application never "
            "writes a ROM from here.",
        )

    def _show_surface_dialog(self, title: str, surface: QWidget, blurb: str) -> None:
        """Open one project-action surface as a CONTENT-SIZED desktop dialogue.

        These are configuration and result surfaces, not workspaces. Sized by
        preference to the content they hold, they open as a compact sheet; the
        minimum keeps the dialogue usable, and the report area inside them is the
        one part allowed to grow when a real build produces a lot of output.

        The surface is a dialogue and never a stage page, so a project action can
        no longer look like an editor switch happening underneath an active editor.
        """
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setSizeGripEnabled(True)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(
            theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD
        )
        layout.setSpacing(theme.SPACE_SM)
        caption = QLabel(blurb)
        caption.setProperty("dbzRole", "hint")
        caption.setWordWrap(True)
        layout.addWidget(caption)
        # The surface is re-parented, not copied: one implementation, one owner.
        # It is also explicitly re-shown. `_show_host` hides whichever action
        # surface is not the active one, and a hidden widget stays hidden when it is
        # re-parented - so without this the dialogue opened with its caption and
        # nothing else.
        previous_parent = surface.parentWidget()
        surface.setParent(dialog)
        surface.setVisible(True)
        layout.addWidget(surface, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        # Prefer the content's own size, with a floor that keeps the controls
        # reachable and a ceiling so a long report cannot run off the screen.
        hint = dialog.sizeHint()
        dialog.resize(
            min(max(hint.width(), 480), 720),
            min(max(hint.height(), 260), 560),
        )
        try:
            dialog.exec()
        finally:
            surface.setParent(previous_parent)

    def _show_about(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "About DragonByte Z",
            "DragonByte Z\n\n"
            "A desktop authoring client for the Webfoot Dragon Ball Z GBA games.\n"
            "It presents the Webfoot SDK; it holds no ROM-format knowledge of its own.\n\n"
            "The original commercial ROM is never modified. Every write produces a "
            "new file beside a provenance record.",
        )

    # -- staged-work guard ----------------------------------------------------

    def _open_rom(self) -> None:
        """Open a game image, confirming first when staged edits would be lost.

        The open image is the base every pending layout edit points into, so
        replacing it cannot preserve them. That makes this the "reload" case the
        dirty-state contract requires to ASK rather than discard, and it is
        asked before the file dialog is shown, so cancelling changes nothing.
        The dialog itself stays the one implementation of "load an image"
        (`AtlasBrowserTab.open_rom_dialog`); this only decides whether it opens.
        """
        if not self._confirm_discard_staged_edits("Opening another image"):
            return
        self._atlas.open_rom_dialog()

    def _confirm_discard_staged_edits(self, action: str) -> bool:
        """Ask before an operation that cannot preserve staged layout edits.

        The count is `MapsEditor.unsaved_edit_count()`, the same authority the
        window title and the status bar already report as unsaved work, so the
        prompt can never disagree with the number on screen.

        Other editors also stage values - unapplied palette colours, unapplied
        dialogue text - but those describe the *outgoing* image and have no
        meaning across it, so a session change clears them by design. Only
        layout edits are authored work that a ROM change would silently destroy,
        which is why the guard is derived from that one count.
        """
        pending = self._maps.unsaved_edit_count()
        if not pending:
            return True
        answer = QMessageBox.question(
            self,
            action,
            f"{pending} unsaved layout edit(s) have not been written to a ROM.\n\n"
            f"{action} discards them; the Map Browser's Save As writes them to a "
            "new ROM first.\n\nDiscard them and continue?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return answer == QMessageBox.StandardButton.Discard

    def closeEvent(self, event) -> None:
        """Refuse to close silently while layout edits are unwritten.

        Closing is the other irreversible case: the process ends, so nothing
        staged can be recovered afterwards. Cancelling leaves the window open
        with its staged work exactly as it was.
        """
        if self._confirm_discard_staged_edits("Closing DragonByte Z"):
            event.accept()
        else:
            event.ignore()

    # -- shell state ----------------------------------------------------------

    def _refresh_identity(self) -> None:
        """Project identity in the window title; project state in the status bar.

        Identity is global, so the title carries it. Godot puts its ``(*)`` marker
        *first* so the OS task bar always shows it; DragonByte Z names the count in
        words as well, because the pending work here is a pending layout-edit list
        rather than an open document.

        The status bar's permanent zone carries the three project states that are
        otherwise invisible and that every editor needs: validation, build and
        unsaved layout edits.
        """
        rom = self._session.rom_path
        profile = self._session.profile
        project = self._session.project_dir
        title = "DragonByte Z"
        if rom is not None:
            suffix = f" \u00b7 {profile.id}" if profile is not None else ""
            kind = " \u00b7 derivative" if self._session.authored is not None else ""
            title = f"DragonByte Z \u2014 {rom.name}{suffix}{kind}"
        if project is not None:
            title = f"{title} \u00b7 {project.name}"
        pending = self._maps.unsaved_edit_count()
        if pending:
            title = f"{theme.TITLE_DIRTY} {title} \u2014 {pending} unsaved"
        self.setWindowTitle(title)
        self._status_project.setText(self._project_state_text(rom, project, pending))

    def _project_state_text(self, rom, project, pending: int) -> str:
        """The project states that are actually applicable, each with a glyph.

        "Stale" is used only where it is true: a result was produced and a later
        change invalidated it. A project that has never been validated is "not
        validated", not "stale" - the two are different facts, and reporting the
        second when the first holds is what made this bar read as noise. Nothing is
        invented here: `validation_revision` and `build_revision` are the session's
        own record of whether a result ever existed.
        """
        parts: list[str] = []
        if rom is None:
            parts.append("no ROM")
        elif project is None:
            parts.append("no project")
        else:
            validated = self._session.validation_revision is not None
            if validated:
                parts.append(
                    "validation current"
                    if self._session.validation_current
                    else f"{theme.status_glyph('pending')} validation stale"
                )
            else:
                parts.append("not validated")
            built = self._session.last_build is not None
            if built:
                parts.append(
                    "build current"
                    if self._session.build_current
                    else f"{theme.status_glyph('pending')} build stale"
                )
            else:
                parts.append("not built")
        if pending:
            parts.append(f"{theme.TITLE_DIRTY} {pending} unsaved layout edit(s)")
        return "   \u2502   ".join(parts)

    def _refresh_action_state(self) -> None:
        """Enable each project action by the state its own contract needs.

        Mirrors ``BuildPanelTab._refresh`` exactly - this shell must not become a
        second, disagreeing authority on when an action is available.
        """
        rom_open = self._session.rom_path is not None
        has_project = self._session.project_dir is not None
        self._action_extract_project.setEnabled(rom_open and not has_project)
        self._action_open_project.setEnabled(True)
        self._action_output_dir.setEnabled(True)
        self._action_validate.setEnabled(rom_open and has_project)
        self._action_build.setEnabled(self._session.validation_current)
        self._action_run.setEnabled(self._launcher.rom_is_runnable())
        self._refresh_undo_actions()

    def refresh_shell(self) -> None:
        """Re-read session state into the shell chrome. Safe to call any time."""
        self._refresh_identity()
        self._refresh_action_state()
