"""The window: one header row, three panes, one status bar, one edit path.

Editors never connect to each other. Every surface that can change a line calls
`Shell.apply_edit`, so undo, the lists, the meter and the context pane all move
from one place.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTime, Qt, QUrl
from PySide6.QtGui import (
    QAction,
    QDesktopServices,
    QKeySequence,
    QPalette,
    QShortcut,
    QUndoCommand,
    QUndoStack,
)
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QUndoView,
    QVBoxLayout,
    QWidget,
)

from tools.webfoot import textedit

from . import contextpane, exportdialog, lineview, renamedialog, settings, theme
from .chipedit import EditorSections
from .identity import PACKAGE, PRODUCT_NAME, PRODUCT_VERSION
from .session import RECORD, SLOT, Session

LEFT_START, CENTRE_START, RIGHT_START = 330, 540, 350
LEFT_RANGE = (260, 470)
RIGHT_RANGE = (300, 480)
WINDOW_START = (1200, 760)

NO_IMAGE = f"No image open. Start with: python -m {PACKAGE} <image.gba>"


def pending_text(session: Session, key: str) -> str:
    """What the line will say: the engine's own pending text, else the loaded text."""
    line = session.line(key)
    if line is None:
        return ""
    edit = session.edits.get(key)
    return line.text if edit is None else edit.new


def span_detail(session: Session, key: str) -> str:
    """Where the line's span sits in the image, from the engine's own numbers.

    A record's own offset inside its container is the engine's arithmetic, so the
    status bar names the container's file offset and the record's start in it.
    """
    line = session.line(key)
    if line is None:
        return ""
    if line.kind == SLOT:
        try:
            slot = session.model.slots[int(key.split(":", 1)[1])]
        except (IndexError, ValueError):
            return key
        return f"{key}   string file offset 0x{slot.offset:06X}"
    selector, start, length = (int(part) for part in key.split(":"))
    container = session.model.layout.offsets.get(selector)
    where = "container offset unknown" if container is None else \
        f"container file offset 0x{container:06X}"
    return f"{key}   {where}   start {start} length {length} bytes"


class _EditCommand(QUndoCommand):
    """One user edit: the text before, the text after, one stack entry."""

    def __init__(self, shell: Shell, key: str, before: str, after: str) -> None:
        super().__init__(f"edit {key}")
        self._shell, self._key, self._before, self._after = shell, key, before, after

    def redo(self) -> None:
        self._shell.write(self._key, self._after, keep_editor=True)

    def undo(self) -> None:
        self._shell.write(self._key, self._before, keep_editor=False)


class _BatchCommand(QUndoCommand):
    """A whole rename batch as one step."""

    def __init__(self, shell: Shell, moves: list[tuple[str, str, str]]) -> None:
        super().__init__(f"rename {len(moves)} record(s)")
        self._shell, self._moves = shell, tuple(moves)

    def redo(self) -> None:
        for key, _before, after in self._moves:
            self._shell.write(key, after, keep_editor=False)

    def undo(self) -> None:
        for key, before, _after in self._moves:
            self._shell.write(key, before, keep_editor=False)


class Shell(QMainWindow):
    """The single wiring point, and the only place an edit is pushed."""

    def __init__(self, session: Session | None, theme_=None,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        application = QApplication.instance()
        self.session = session
        self.theme = theme_ if theme_ is not None else theme.active_theme()
        self.metrics = theme.metrics(application)
        self.stack = QUndoStack(self)
        self._key = ""
        self._exported_path: Path | None = None
        self.last_export: exportdialog.ExportDialog | None = None
        self.resize(*WINDOW_START)
        self._build_header()
        self._build_panes()
        self._build_status()
        self._build_menu()
        self._connect()
        self._update_header()
        if session is not None and self.pane.selected():
            self.show_line(self.pane.selected())

    # --- construction --------------------------------------------------------

    def _build_header(self) -> None:
        self.rom_label = QLabel()
        self.layout_label = QLabel()
        self.layout_label.setFont(theme.mono_font())
        self.project_label = QLabel()
        self.unsaved_label = QLabel("unsaved changes")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search lines")
        self.search.setMaximumWidth(320)
        self.search.setMinimumHeight(self.metrics.field_height)
        self.search.addAction(theme.icon("search"), QLineEdit.ActionPosition.LeadingPosition)
        row = QHBoxLayout()
        row.setContentsMargins(self.metrics.pad, self.metrics.pad, self.metrics.pad, 0)
        row.setSpacing(self.metrics.gap)
        for widget in (self.rom_label, self.layout_label, self.project_label,
                       self.unsaved_label):
            row.addWidget(widget)
        row.addStretch(1)
        row.addWidget(self.search)
        self.header = QWidget()
        header_column = QVBoxLayout(self.header)
        header_column.setContentsMargins(0, 0, 0, 0)
        header_column.setSpacing(self.metrics.gap)
        header_column.addLayout(row)
        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setFrameShadow(QFrame.Shadow.Plain)
        header_column.addWidget(rule)

    def _build_panes(self) -> None:
        self.pane = lineview.LinePane(self.session, self.metrics, self.theme, self)
        self.pane.setMinimumWidth(LEFT_RANGE[0])
        self.pane.setMaximumWidth(LEFT_RANGE[1])
        self.editor = EditorSections(self.theme, self.metrics, self)
        self.empty = QLabel(NO_IMAGE if self.session is None else "")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty.setWordWrap(True)
        self.centre = QStackedWidget()
        self.centre.addWidget(self.editor)
        self.centre.addWidget(self.empty)
        self.centre.setCurrentWidget(self.editor if self.session is not None else self.empty)
        self.context = contextpane.ContextPane(self.theme, self.metrics, self)
        self.context.setMinimumWidth(RIGHT_RANGE[0])
        self.context.setMaximumWidth(RIGHT_RANGE[1])
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        for widget in (self.pane, self.centre, self.context):
            self.splitter.addWidget(widget)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes(self._stored_sizes())
        central = QWidget()
        column = QVBoxLayout(central)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(self.header)
        column.addWidget(self.splitter, 1)
        self.setCentralWidget(central)

    def _stored_sizes(self) -> list[int]:
        stored = settings.load().get("splitter")
        if isinstance(stored, list) and len(stored) == 3 and all(
                isinstance(size, int) and size > 0 for size in stored):
            return list(stored)
        return [LEFT_START, CENTRE_START, RIGHT_START]

    def _build_status(self) -> None:
        status_bar = self.statusBar()
        status_bar.setMinimumHeight(self.metrics.status_height)
        self.offset_label = QLabel()
        self.offset_label.setFont(theme.mono_font())
        self.export_label = QLabel()
        self.export_label.setFont(theme.mono_font())
        palette = self.export_label.palette()
        palette.setColor(QPalette.ColorRole.WindowText,
                         theme.color(self.theme, "text_secondary"))
        self.export_label.setPalette(palette)
        self.export_button = QPushButton("Export")
        self.export_button.setMinimumHeight(self.metrics.field_height)
        button_palette = self.export_button.palette()
        button_palette.setColor(QPalette.ColorRole.Button, theme.color(self.theme, "accent"))
        button_palette.setColor(QPalette.ColorRole.ButtonText,
                                theme.color(self.theme, "surface"))
        self.export_button.setPalette(button_palette)
        self.export_button.setAutoFillBackground(True)
        for widget in (self.offset_label, self.export_label, self.export_button):
            status_bar.addPermanentWidget(widget)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        self.export_action = QAction("&Export image...", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_action.triggered.connect(self.prompt_export)
        self.emulator_action = QAction("Open in &emulator", self)
        self.emulator_action.setEnabled(False)
        self.emulator_action.triggered.connect(self.open_in_emulator)
        close_action = QAction("&Close", self)
        close_action.setShortcut(QKeySequence("Ctrl+W"))
        close_action.triggered.connect(self.close)
        file_menu.addAction(self.export_action)
        file_menu.addAction(self.emulator_action)
        file_menu.addSeparator()
        file_menu.addAction(close_action)

        edit_menu = self.menuBar().addMenu("&Edit")
        self.undo_action = self.stack.createUndoAction(self, "&Undo")
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.redo_action = self.stack.createRedoAction(self, "&Redo")
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.rename_action = QAction("&Rename occurrences...", self)
        self.rename_action.triggered.connect(self.prompt_rename)
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.rename_action)

        view_menu = self.menuBar().addMenu("&View")
        self.dialogue_action = QAction("&Dialogue list", self)
        self.dialogue_action.triggered.connect(lambda: self.pane.set_kind(RECORD))
        self.names_action = QAction("&Names and bios", self)
        self.names_action.triggered.connect(lambda: self.pane.set_kind(SLOT))
        self.search_action = QAction("&Find line", self)
        self.search_action.setShortcut(QKeySequence("Ctrl+F"))
        self.search_action.triggered.connect(self.focus_search)
        self.next_list_action = QAction("&Next list", self)
        self.next_list_action.setShortcut(QKeySequence("Ctrl+Tab"))
        self.next_list_action.triggered.connect(self.pane.next_tab)
        self.next_pane_action = QAction("Next &pane", self)
        self.next_pane_action.setShortcut(QKeySequence("F6"))
        self.next_pane_action.triggered.connect(self.cycle_focus)
        self.history = QUndoView(self.stack)
        self.history_dock = QDockWidget("Undo history", self)
        self.history_dock.setWidget(self.history)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.history_dock)
        self.history_dock.hide()
        for action in (self.dialogue_action, self.names_action):
            view_menu.addAction(action)
        view_menu.addSeparator()
        for action in (self.search_action, self.next_list_action, self.next_pane_action):
            view_menu.addAction(action)
        view_menu.addAction(self.history_dock.toggleViewAction())

        help_menu = self.menuBar().addMenu("&Help")
        about_action = QAction(f"&About {PRODUCT_NAME}", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _connect(self) -> None:
        self.pane.line_chosen.connect(self.show_line)
        self.pane.line_entered.connect(self.focus_new)
        self.editor.edited.connect(self._editor_edited)
        self.editor.notice.records_requested.connect(self.select_records)
        self.search.textChanged.connect(self.pane.set_term)
        self.search.returnPressed.connect(self.focus_list)
        self.export_button.clicked.connect(self.prompt_export)
        self.stack.cleanChanged.connect(self._clean_changed)
        self.escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self.search)
        self.escape.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.escape.activated.connect(self._escape_search)

    # --- what a line looks like ---------------------------------------------

    def show_line(self, key: str, keep_editor: bool = False) -> None:
        """Show one line everywhere it appears, from the session's own answers."""
        if self.session is None or self.session.line(key) is None:
            return
        self._key = key
        detail = span_detail(self.session, key)
        text = pending_text(self.session, key)
        self.editor.show_line(self.session, key, text, keep_editor)
        self.context.show_line(self.session, key, text, detail)
        self.offset_label.setText(detail)

    def panes(self) -> tuple[tuple[str, QWidget], ...]:
        return (("list", self.pane), ("editor", self.centre), ("context", self.context))

    def walk_panes(self) -> tuple[str, ...]:
        """Touch every pane, so a smoke run proves each one built and answers."""
        touched = []
        for name, pane in self.panes():
            pane.sizeHint()
            pane.isVisibleTo(self)
            touched.append(name)
        self.pane.table.model().rowCount()
        self.editor.new.serialized()
        self.context.preview.is_approximate()
        return tuple(touched)

    # --- the one edit path ---------------------------------------------------

    def apply_edit(self, key: str, new: str) -> None:
        """The one way a line changes: one user action, one undo step."""
        if self.session is None or self.session.line(key) is None:
            return
        before = pending_text(self.session, key)
        if new == before:
            return
        self.stack.push(_EditCommand(self, key, before, new))

    def write(self, key: str, text: str, keep_editor: bool = True) -> None:
        """Write one line's pending text and redraw. It never pushes a command."""
        line = self.session.line(key)
        if line is None:
            return
        try:
            if text == line.text:
                self.session.clear_edit(key)
            else:
                self.session.set_edit(key, text)
        except textedit.TextEditError as error:
            self.statusBar().showMessage(str(error))
            return
        self.pane.refresh(self._key)
        if self._key:
            self.show_line(self._key, keep_editor)
        self._update_header()

    def apply_rename(self, old: str, new: str, renamed: dict[str, frozenset[int]]) -> None:
        """One undo step for a whole rename batch."""
        if self.session is None:
            return
        moves = []
        for key, offsets in sorted(renamed.items()):
            line = self.session.line(key)
            if line is None:
                continue
            after = self.session.rename_text(key, old, new, offsets)
            if after != line.text:
                moves.append((key, line.text, after))
        if not moves:
            return
        self.stack.push(_BatchCommand(self, moves))

    def _editor_edited(self, text: str) -> None:
        if self._key:
            self.apply_edit(self._key, text)

    # --- export and the emulator --------------------------------------------

    def prompt_export(self) -> None:
        if self.session is None:
            return
        note = self._refusal_note()
        if note:
            self.statusBar().showMessage(note)
            return
        if self.session.plan() is None:
            self.statusBar().showMessage("There is nothing to export: the edit list is empty.")
            return
        source = Path(self.session.model.path)
        chosen, _filters = QFileDialog.getSaveFileName(
            self, "Export image", str(source.with_name(f"{source.stem}-edited.gba")),
            "GBA image (*.gba)")
        if chosen:
            self.export_to(chosen)

    def export_to(self, path) -> dict | None:
        """Run the engine's own export, and surface its refusal message verbatim."""
        if self.session is None:
            return None
        dialog = exportdialog.ExportDialog(self)
        self.last_export = dialog
        try:
            report = self.session.export(path)
        except textedit.TextEditError as error:
            dialog.show_error(str(error))
            dialog.show()
            return None
        dialog.show_report(report, Path(path))
        dialog.show()
        self._exported_path = Path(path)
        self.emulator_action.setEnabled(True)
        self.stack.setClean()
        self.export_label.setText(
            f"Last export {QTime.currentTime().toString('HH:mm:ss')}"
            f"   SHA-256 {str(report.get('output_sha256', ''))[:12]}")
        return report

    def _refusal_note(self) -> str:
        """Why an export cannot happen, in the engine's own words, or nothing."""
        if self.session is None:
            return ""
        refusals = self.session.refusals()
        if not refusals:
            return ""
        first = refusals[0]
        more = "" if len(refusals) == 1 else f" (and {len(refusals) - 1} more)"
        return (f"Export is impossible while a refusal stands: {first.target}: "
                f"{first.reason}{more}")

    def open_in_emulator(self) -> None:
        """Hand the exported image to whatever the system has registered."""
        if self._exported_path is None:
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._exported_path))):
            self.statusBar().showMessage("No emulator is registered for .gba on this machine.")

    # --- rename ---------------------------------------------------------------

    def prompt_rename(self) -> None:
        if self.session is None:
            return
        old, accepted = QInputDialog.getText(self, "Rename occurrences", "Text to replace:")
        if not accepted or not old:
            return
        new, accepted = QInputDialog.getText(self, "Rename occurrences",
                                            f"Replace {old} with:")
        if not accepted or not new:
            return
        dialog = renamedialog.RenameDialog(self.session, old, new, self.metrics, self.theme, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.apply_rename(old, new, dialog.renamed())

    def select_records(self, covering) -> None:
        """Show the records that contain the selected line."""
        self.pane.set_kind(RECORD)
        self.search.clear()
        self.pane.clear_filters()
        self.pane.refresh()
        if not self.pane.select_first(covering):
            self.statusBar().showMessage(
                "The records that contain this line are not in the loaded image.")

    # --- focus and the small print -------------------------------------------

    def focus_search(self) -> None:
        self.search.setFocus(Qt.FocusReason.ShortcutFocusReason)
        self.search.selectAll()

    def focus_list(self) -> None:
        self.pane.table.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def focus_new(self, _key: str = "") -> None:
        self.editor.new.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _escape_search(self) -> None:
        if self.search.text():
            self.search.clear()
        else:
            self.focus_list()

    def cycle_focus(self) -> None:
        """F6 walks the lists, the editor, the context pane and the status bar."""
        order = [self.pane.table, self.editor.new, self.context, self.statusBar()]
        current = QApplication.focusWidget()
        index = order.index(current) if current in order else len(order) - 1
        order[(index + 1) % len(order)].setFocus(Qt.FocusReason.TabFocusReason)

    def show_about(self) -> None:
        QMessageBox.about(self, PRODUCT_NAME, f"{PRODUCT_NAME} {PRODUCT_VERSION}")

    def _clean_changed(self, clean: bool) -> None:
        self.unsaved_label.setVisible(not clean)
        name = "no image" if self.session is None else Path(self.session.model.path).name
        self.setWindowTitle(f"{'* ' if not clean else ''}{name} - {PRODUCT_NAME}")

    def _update_header(self) -> None:
        session = self.session
        if session is None:
            self.rom_label.setText("No image open")
            self.layout_label.setText("")
            self.project_label.setText("")
        else:
            self.rom_label.setText(Path(session.model.path).name)
            self.layout_label.setText(session.model.layout.profile.key)
            edits = len(session.edits)
            state = f"{edits} edit" if edits == 1 else f"{edits} edits"
            if session.unmatched:
                state += f", {len(session.unmatched)} unmatched"
            if session.base_changed:
                state = f"base changed, {state}"
            self.project_label.setText(f"project: {state}")
        note = self._refusal_note()
        self.export_button.setToolTip(note)
        self._clean_changed(self.stack.isClean())

    def closeEvent(self, event) -> None:
        settings.save({"splitter": list(self.splitter.sizes())})
        super().closeEvent(event)
