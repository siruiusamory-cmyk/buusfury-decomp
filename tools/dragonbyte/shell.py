"""The window: five regions, one session, one wiring point.

The shell is the single place the regions are wired together. It owns no ROM
knowledge - no constant, no address, no record stride - and it renders what the
session, the destination registry and the diagnostics module already hold.

Five regions, in order: the menu bar, the action bar, the destination strip, a
splitter holding the centre pages and the one inspector, and the status bar.

Every destination's centre page is a statement rather than an editor: this step
builds the foundation, and a page that implied editing worked would be a false
claim. The four global actions are present, disabled and each carries the reason
it is not available; a control that cannot act says so instead of pretending.
Save, Undo and Redo are real actions, and what they can do is the session's
answer rather than a decision taken here: this window renders the availability of
edits and never computes one.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from tools.webfoot.release_identity import release_identity

from . import diagnostics, theme
from .destination import DESTINATIONS, ROM, Destination, destination
from .inspector import InspectorPane, support_state_text
from .journal import EditKind
from .session import Session, SessionError
from .settings import Settings

#: The window's starting size. A narrower window is allowed; this is what a user
#: sees first, with the centre editor and the inspector both usable.
START_WIDTH = 1280
START_HEIGHT = 800

#: What each global action would do, and why it cannot do it yet. One sentence
#: each, in the same product language as a destination's foundation summary.
GLOBAL_ACTIONS: tuple[tuple[str, str], ...] = (
    (
        "Validate",
        "Not available in the foundation build: validation arrives with the "
        "project and edit steps.",
    ),
    (
        "Build",
        "Not available in the foundation build: building arrives with the "
        "project and edit steps.",
    ),
    (
        "Run",
        "Not available in the foundation build: running arrives with the build "
        "step.",
    ),
    (
        "Export patch",
        "Not available in the foundation build: patch export arrives with the "
        "release step.",
    ),
)

#: The edit actions, in the order they sit in the action bar. They are real
#: actions rather than placeholders: what they can do is the session's answer,
#: never a decision taken here.
EDIT_ACTIONS: tuple[str, ...] = ("Save", "Undo", "Redo")


class _FoundationPage(QWidget):
    """One destination's centre page: what it is, and what is not built yet."""

    #: The one constant line every foundation page carries. A page that cannot
    #: change the image says so, rather than showing a control that implies it can.
    NOTE = (
        "No editor surface is available yet, so nothing on this page can change "
        "the image."
    )

    def __init__(self, dest: Destination, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(f"foundationPage_{dest.id}")
        title = QLabel(dest.label)
        title.setProperty("dbzRole", "panelHeader")
        summary = QLabel(dest.foundation_summary)
        summary.setWordWrap(True)
        note = QLabel(self.NOTE)
        note.setProperty("dbzRole", "hint")
        note.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD
        )
        layout.setSpacing(theme.SPACE_SM)
        layout.addWidget(title)
        layout.addWidget(summary)
        layout.addWidget(note)
        layout.addStretch(1)


class Shell(QMainWindow):
    """The one window: one session, one inspector, one history."""

    def __init__(self, session: Session, config_directory: Path) -> None:
        super().__init__()
        self._session = session
        self._config_directory = Path(config_directory)
        self._settings = Settings.load(self._config_directory)
        identity = release_identity()
        self.setWindowTitle(identity.display)
        # A restored geometry is the user's own size and wins over the default;
        # resizing after the restore would silently discard it.
        if self._settings.geometry:
            self.restoreGeometry(
                QByteArray.fromBase64(self._settings.geometry.encode("ascii"))
            )
        else:
            self.resize(START_WIDTH, START_HEIGHT)
        #: The last message this window showed. A refusal puts the reason here,
        #: never a bare word, because the reason is the part that helps.
        self._status_text = ""

        self._pages: dict[str, QWidget] = {}
        self._page_stack = QStackedWidget()
        for candidate in DESTINATIONS:
            page = _FoundationPage(candidate)
            self._pages[candidate.id] = page
            self._page_stack.addWidget(page)

        self._inspector = InspectorPane()
        self._inspector.setMinimumWidth(theme.INSPECTOR_MIN_WIDTH)
        centre = QSplitter(Qt.Orientation.Horizontal)
        centre.addWidget(self._page_stack)
        centre.addWidget(self._inspector)
        # The inspector keeps its width while the centre grows.
        centre.setStretchFactor(0, 1)
        centre.setStretchFactor(1, 0)
        centre.setSizes([START_WIDTH - theme.INSPECTOR_WIDTH, theme.INSPECTOR_WIDTH])
        self._centre = centre
        self.setCentralWidget(centre)

        self._destination_buttons: dict[str, QToolButton] = {}
        self._build_actions()
        self._build_menus()
        self._build_action_bar()
        self._build_destination_strip()
        self._build_status_bar()
        self._refresh_identity()
        self.show_destination(DESTINATIONS[0].id)

    # -- construction ---------------------------------------------------------

    def _build_actions(self) -> None:
        """Every action once, in one place, so none is defined twice."""
        self._action_open_rom = QAction("Open ROM\u2026", self)
        self._action_open_rom.setShortcut(QKeySequence("Ctrl+O"))
        self._action_open_rom.setStatusTip("Identify and open a game image")
        self._action_open_rom.triggered.connect(self.open_rom)

        self._action_open_project = QAction("Open Project\u2026", self)
        self._action_open_project.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self._action_open_project.setStatusTip("Open an authored project directory")
        self._action_open_project.triggered.connect(self.open_project)

        self._action_exit = QAction("Exit", self)
        self._action_exit.setShortcut(QKeySequence("Ctrl+Q"))
        self._action_exit.triggered.connect(self.close)

        self._action_back = QAction("Back", self)
        self._action_back.setShortcut(QKeySequence("Alt+Left"))
        self._action_back.setStatusTip("Return to the previous destination")
        self._action_back.triggered.connect(self.go_back)

        self._action_forward = QAction("Forward", self)
        self._action_forward.setShortcut(QKeySequence("Alt+Right"))
        self._action_forward.setStatusTip("Return to the next destination")
        self._action_forward.triggered.connect(self.go_forward)

        self._action_about = QAction("About DragonByte Z", self)
        self._action_about.triggered.connect(self.show_about)

        self._global_actions: dict[str, QAction] = {}
        for label, reason in GLOBAL_ACTIONS:
            action = QAction(label, self)
            action.setEnabled(False)
            action.setToolTip(reason)
            action.setStatusTip(reason)
            self._global_actions[label] = action

        # The platform's own standard keys, so a menu-less action still answers
        # the combination a user already knows.
        shortcuts = {
            "Save": QKeySequence.StandardKey.Save,
            "Undo": QKeySequence.StandardKey.Undo,
            "Redo": QKeySequence.StandardKey.Redo,
        }
        slots = {
            "Save": self.save_project,
            "Undo": self.undo_edit,
            "Redo": self.redo_edit,
        }
        self._edit_actions: dict[str, QAction] = {}
        for label in EDIT_ACTIONS:
            action = QAction(label, self)
            action.setShortcut(shortcuts[label])
            action.triggered.connect(slots[label])
            self._edit_actions[label] = action

    def _build_menus(self) -> None:
        """File, View and Help. The four global actions are not repeated here."""
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self._action_open_rom)
        file_menu.addAction(self._action_open_project)
        file_menu.addSeparator()
        file_menu.addAction(self._action_exit)

        view_menu = self.menuBar().addMenu("&View")
        for number, candidate in enumerate(DESTINATIONS, start=1):
            action = QAction(candidate.label.replace("&", "&&"), self)
            action.setShortcut(QKeySequence(f"Ctrl+{number}"))
            action.triggered.connect(
                lambda _checked=False, identifier=candidate.id: self.show_destination(
                    identifier
                )
            )
            view_menu.addAction(action)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self._action_about)

    def _build_action_bar(self) -> None:
        """Identity on the left, the four global actions on the right."""
        bar = QToolBar("Actions", self)
        bar.setObjectName("actionBar")
        bar.setMovable(False)
        bar.setFloatable(False)
        bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self._identity_label = QLabel()
        self._identity_label.setProperty("dbzRole", "technical")
        bar.addWidget(self._identity_label)
        bar.addWidget(self._spacer())
        for label, reason in GLOBAL_ACTIONS:
            self._place_action(bar, self._global_actions[label], label, reason)
        # The edit actions share the row group with the global ones: the same
        # treatment, so a disabled control states its reason here too.
        for label in EDIT_ACTIONS:
            self._place_action(bar, self._edit_actions[label], label, "")
        self._action_bar = bar
        self.addToolBar(bar)

    def _place_action(
        self, bar: QToolBar, action: QAction, label: str, reason: str
    ) -> None:
        """Add one action to a bar and let its button carry the reason."""
        bar.addAction(action)
        button = bar.widgetForAction(action)
        if button is not None:
            # The reason travels with the control as well as with the action,
            # so a keyboard or screen-reader user gets it from the control.
            button.setToolTip(reason)
            button.setAccessibleName(f"{label}. {reason}" if reason else label)

    def _build_destination_strip(self) -> None:
        """Six destinations, one rule between the groups, then history."""
        strip = QToolBar("Destinations", self)
        strip.setObjectName("destinationStrip")
        strip.setMovable(False)
        strip.setFloatable(False)
        strip.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        for candidate in DESTINATIONS:
            if candidate.group == ROM:
                strip.addSeparator()
            button = QToolButton()
            # An ampersand in a button's text is a mnemonic unless it is doubled,
            # so the destination's own name would lose it on screen.
            button.setText(candidate.label.replace("&", "&&"))
            # The style sheet's padding and border are a pixel wider than the
            # button's own size hint allows for, so the longest label elides in a
            # strip that has room to spare.
            button.setMinimumWidth(button.sizeHint().width() + 2 * theme.SPACE_SM)
            button.setCheckable(True)
            button.setAutoRaise(True)
            button.setToolTip(f"Show the {candidate.label} destination")
            button.setAccessibleName(f"{candidate.label} destination")
            button.clicked.connect(
                lambda _checked=False, identifier=candidate.id: self.show_destination(
                    identifier
                )
            )
            strip.addWidget(button)
            self._destination_buttons[candidate.id] = button
        strip.addWidget(self._spacer())
        strip.addAction(self._action_back)
        strip.addAction(self._action_forward)
        self._strip = strip
        # The two bands are separate regions in the approved window: the action
        # bar above, the destination strip below it. Without the break they share
        # one row, which squeezes the strip until its labels elide and Back and
        # Forward fall behind the overflow chevron.
        self.addToolBarBreak()
        self.addToolBar(strip)

    @staticmethod
    def _spacer() -> QWidget:
        """An expanding gap between two groups of controls in a toolbar."""
        spacer = QWidget()
        spacer.setObjectName("toolbarSpacer")
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        return spacer

    def _build_status_bar(self) -> None:
        """The active destination and what is open on one side, the last message
        on the other, so a transient refusal cannot hide the other two."""
        self._status_state = QLabel()
        self._status_state.setProperty("dbzRole", "status")
        self._status_message = QLabel()
        self._status_message.setProperty("dbzRole", "status")
        status = self.statusBar()
        status.addWidget(self._status_state, 1)
        status.addPermanentWidget(self._status_message)

    # -- wiring ---------------------------------------------------------------

    def show_destination(self, destination_id: str, *, record: bool = True) -> None:
        """Show one destination and clear the inspector to its empty state."""
        target = destination(destination_id)
        if record:
            self._session.navigation.push(target.id)
        self._page_stack.setCurrentWidget(self._pages[target.id])
        for identifier, button in self._destination_buttons.items():
            button.setChecked(identifier == target.id)
        self._inspector.set_destination(target)
        self._inspector.set_context(None)
        self._refresh_navigation()
        self._refresh_status()

    def go_back(self) -> None:
        """Move back one history entry; never creates one."""
        entry = self._session.navigation.back()
        if entry is not None:
            self.show_destination(entry.destination, record=False)
        else:
            self._refresh_navigation()

    def go_forward(self) -> None:
        """Move forward one history entry; never creates one."""
        entry = self._session.navigation.forward()
        if entry is not None:
            self.show_destination(entry.destination, record=False)
        else:
            self._refresh_navigation()

    def open_rom(self) -> None:
        """Ask for an image and open it. A refusal changes nothing."""
        chosen, _ = QFileDialog.getOpenFileName(
            self,
            "Open ROM",
            self._settings.last_directory,
            "Game Boy Advance image (*.gba);;All files (*)",
        )
        if not chosen:
            return
        path = Path(chosen)
        try:
            self._session.open_rom(path)
        except SessionError as exc:
            self._report_failure("Open ROM", str(exc))
            return
        self._settings.last_directory = str(path.parent)
        self._refresh_identity()
        self._refresh_status()

    def open_project(self) -> None:
        """Ask for a project directory and open it. A refusal changes nothing."""
        chosen = QFileDialog.getExistingDirectory(
            self, "Open Project", self._settings.last_directory
        )
        if not chosen:
            return
        directory = Path(chosen)
        if not self._settle_unsaved_changes():
            return
        try:
            self._session.open_project(directory, discard_unsaved=True)
        except SessionError as exc:
            self._report_failure("Open Project", str(exc))
            return
        self._settings.last_directory = str(directory)
        self._refresh_identity()
        self._refresh_status()

    def save_project(self) -> None:
        """Write the unsaved edits. A refusal or a failure changes nothing."""
        try:
            self._session.save_project()
        except SessionError as exc:
            self._report_failure("Save", str(exc))
            return
        self._refresh_status()

    def undo_edit(self) -> None:
        """Step the project back one edit. A refusal changes nothing."""
        try:
            self._session.undo_edit()
        except SessionError as exc:
            self._report_failure("Undo", str(exc))
            return
        self._refresh_status()

    def redo_edit(self) -> None:
        """Step the project forward one edit. A refusal changes nothing."""
        try:
            self._session.redo_edit()
        except SessionError as exc:
            self._report_failure("Redo", str(exc))
            return
        self._refresh_status()

    def apply_edit(
        self,
        *,
        kind: EditKind,
        target: str,
        after: object,
        resources: tuple[str, ...] = (),
        reason: str = "",
        coalesce_key: str = "",
    ) -> None:
        """Commit one edit to the session's project and re-render the window.

        The one entry point an editing surface calls, so the status line, the
        unsaved indicator and the three action states can never be left behind
        by an edit: refreshing here rather than at the caller is what makes the
        display follow the model instead of a discipline.
        """
        try:
            self._session.apply_edit(
                kind=kind,
                target=target,
                after=after,
                resources=resources,
                reason=reason,
                coalesce_key=coalesce_key,
            )
        except SessionError as exc:
            self._report_failure("Edit", str(exc))
            return
        self._refresh_status()

    def _unsaved_changes_question(self) -> str:
        """What an unsaved-changes question says, and nothing it cannot measure.

        The count and the affected documents are what the journal holds. The byte
        ranges the product spec also asks for are owed when the range index exists
        (S4); they are left out rather than guessed, because a count a user cannot
        trust is worse than a shorter question.
        """
        journal = self._session.journal
        edits = journal.edits()
        targets = ", ".join(sorted({entry.target for entry in edits}))
        return (
            f"{journal.depth} unsaved edit(s) to {targets} would be lost.\n\n"
            "Discard replaces the project's authored files and the edits they "
            "carry with the project as it was last read from disk."
        )

    def _settle_unsaved_changes(self) -> bool:
        """Ask about unsaved edits. Returns False when the caller must stop.

        One question for both callers - closing the window and replacing the
        project - so the destructive step cannot be reached two different ways.
        """
        if not self._session.journal.is_dirty:
            return True
        answer = QMessageBox.warning(
            self,
            "Unsaved changes",
            self._unsaved_changes_question(),
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            return False
        if answer == QMessageBox.StandardButton.Discard:
            return True
        try:
            self._session.save_project()
        except SessionError as exc:
            self._report_failure("Save", str(exc))
            return False
        self._refresh_status()
        return True

    def show_about(self) -> None:
        """The window's state and the state rules, from their one authority."""
        text = diagnostics.diagnostics_text(
            self._session, self._active_destination(), self._status_text
        )
        QMessageBox.about(
            self,
            f"About {release_identity().product_name}",
            f"{text}\n\nSupport states:\n{support_state_text()}",
        )

    def closeEvent(self, event) -> None:
        """Ask about unsaved edits, then persist the window and close.

        A declined save keeps the window open: closing on a failed write would
        destroy the edits the write existed to keep.
        """
        if not self._settle_unsaved_changes():
            event.ignore()
            return
        self._settings.geometry = bytes(self.saveGeometry().toBase64()).decode("ascii")
        self._settings.save(self._config_directory)
        event.accept()

    # -- rendering ------------------------------------------------------------

    def _active_destination(self) -> Destination | None:
        """The destination the history's cursor is on, or None before one is shown."""
        entry = self._session.navigation.current
        return destination(entry.destination) if entry is not None else None

    def _refresh_navigation(self) -> None:
        self._action_back.setEnabled(self._session.navigation.can_go_back)
        self._action_forward.setEnabled(self._session.navigation.can_go_forward)

    def _refresh_status(self) -> None:
        active = self._active_destination()
        label = active.label if active is not None else "no destination"
        rom = "ROM open" if self._session.has_rom else "no ROM"
        project = "project open" if self._session.has_project else "no project"
        if self._session.has_project and self._session.journal.is_dirty:
            project = "project open, unsaved changes"
        self._status_state.setText(f"{label}   |   {rom}   |   {project}")
        self._status_message.setText(self._status_text)
        self._refresh_edit_actions()

    def _refresh_edit_actions(self) -> None:
        """Render the session's answer about Save, Undo and Redo.

        The enabled state and the reason both come from `edit_availability`, so a
        button and its action can never disagree with the session or with each
        other - and nothing here decides either one.
        """
        availability = self._session.edit_availability()
        for label in EDIT_ACTIONS:
            enabled, reason = availability[label]
            action = self._edit_actions[label]
            action.setEnabled(enabled)
            action.setToolTip(reason)
            action.setStatusTip(reason)
            button = self._action_bar.widgetForAction(action)
            if button is not None:
                button.setToolTip(reason)
                button.setAccessibleName(f"{label}. {reason}")

    def _refresh_identity(self) -> None:
        self._identity_label.setText(
            f"{self._session.rom_identity}   |   {self._session.project_identity}"
        )

    def _report_failure(self, operation: str, reason: str) -> None:
        """Show a refusal's reason in the status line and in a message box."""
        self._status_text = f"{operation}: {reason}"
        self._refresh_status()
        QMessageBox.warning(self, operation, reason)
