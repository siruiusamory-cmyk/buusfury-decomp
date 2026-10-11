"""The window: one header row, one splitter, one status bar, one edit path.

The shell is the only place the surfaces are connected to each other. Editors
never talk to each other: `line_chosen` drives the editor and the context pane,
`committed` comes back through `apply_edit`, and one undo stack carries the list.

This package is not `tools.dragonbyte`, so a QUndoStack is the right undo here:
one user action, one step, and the step is the edit list's own history.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from PySide6.QtCore import Qt, QTime, QUrl
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QDesktopServices,
    QKeySequence,
    QPalette,
    QShortcut,
    QUndoCommand,
    QUndoStack,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from tools.webfoot import textedit

from . import contextpane, exportdialog, lineview, renamedialog, settings, status, theme
from . import project as project_file
from .chipedit import EditorSections
from .identity import PACKAGE, PRODUCT_NAME, PRODUCT_VERSION
from .session import (
    APPEARANCE,
    BY_PLACE,
    BY_SPEAKER,
    LINES,
    RECORD,
    RECORDS,
    SLOT,
    STORAGE,
    UNGROUPED,
    Session,
    State,
    open_image,
)

#: The panes start here, and no side pane may collapse into an unreadable column.
#: The first-open pane sizes, and they must add up to the window's content width.
#: Measured: the three values summed to 1320 against 1230 px of content, so the
#: splitter clamped and the list landed on its own floor at 368 rather than at 420,
#: which cost the text column 52 px and the slot list its identity column.
DEFAULT_SPLIT = (420, 470, 340)
#: Pane floors. The list's is the sum of its three column floors plus the frame, so
#: the text column can never be starved: the status needs about 130 px for its whole
#: word, the speaker column will not go below 108, and the text keeps 130. The
#: adopted spec's range for this pane is 260 to 470 with a nominal 330, and the
#: owner's speaker column and four state chips are what push the floor above the
#: spec's number; the default of 420 sits inside the spec's own range.
LEFT_MIN, CENTRE_MIN, RIGHT_MIN = 368, 360, 280
WINDOW_START = (1240, 780)

#: The three panes the View menu shows and hides.
PANE_LABELS = (("list", "&List pane"), ("editor", "&Editor pane"),
               ("context", "&Context pane"))

NO_IMAGE = (
    "No image open.\n\n"
    "Open the image you want to edit: File > Open image (Ctrl+O), or start with\n"
    f"    python -m {PACKAGE} <image.gba>"
)
NO_IMAGE_TIP = "Open an image first."
EXPORT_TIP = "Write every pending edit to a new image."
EXPORT_EMPTY = "There is nothing to export: the edit list is empty."


def project_state(session: Session | None) -> State:
    """The header's word for the whole edit list, from the session's own row states."""
    if session is None:
        return State.UNCHANGED
    if session.base_changed:
        return State.BASE_CHANGED
    states = {session.state(key) for key in session.edited_keys()}
    for worst in (State.REFUSED, State.BASE_CHANGED, State.WILL_MOVE, State.EDITED):
        if worst in states:
            return worst
    return State.UNCHANGED


def project_text(session: Session | None) -> str:
    """The project state as a word and a glyph, plus the counts that qualify it."""
    if session is None:
        return ""
    mark = status.presentation(project_state(session))
    text = f"{mark.glyph} {mark.word}"
    edits = len(session.edited_keys())
    if edits:
        text += f" \u00b7 {edits} edit" + ("" if edits == 1 else "s")
    if session.unmatched:
        text += f", {len(session.unmatched)} unmatched"
    return text


def export_reason(session: Session | None, key: str = "") -> str:
    """Why Export cannot run, in the engine's own words, or "" when it can.

    The selected row's own refusal is the most useful sentence, so it wins; the
    plan's refusal list answers for every other row.
    """
    if session is None:
        return NO_IMAGE_TIP
    if key:
        reason = session.refusal_reason(key)
        if reason:
            return f"{key}: {reason}"
    refusals = session.refusals()
    if refusals:
        first = refusals[0]
        more = "" if len(refusals) == 1 else f" (and {len(refusals) - 1} more)"
        return (f"Export is impossible while a refusal stands: {first.target}: "
                f"{first.reason}{more}")
    if not session.edited_keys():
        return EXPORT_EMPTY
    return ""


def span_detail(session: Session, key: str) -> str:
    """Where the row sits in the image, from the engine's own numbers.

    A record's offset inside its container is the engine's arithmetic, so the
    status bar names the container's file offset and the row's own span in bytes.
    """
    line = session.line(key)
    if line is None:
        return ""
    if line.kind == SLOT:
        slot = next((item for item in session.model.slots if item.key == key), None)
        return key if slot is None else f"{key}   string file offset 0x{slot.offset:06X}"
    selector, _start, length = (int(part) for part in key.split(":"))
    container = session.model.layout.offsets.get(selector)
    where = "container offset unknown" if container is None else f"container 0x{container:06X}"
    return f"{key}   {where}   span {length} bytes"


class _EditCommand(QUndoCommand):
    """One user edit: the target's whole text before and after, one stack entry.

    Both sides are the record's own text, which is the only state this session keeps for
    it, so undo restores exactly what the record held and cannot be refused.
    """

    def __init__(self, shell: Shell, key: str, before, after,
                 label: str | None = None) -> None:
        super().__init__(label or f"edit {key}")
        self._shell, self._key, self._before, self._after = shell, key, before, after

    def redo(self) -> None:
        self._shell.restore(self._key, self._after)

    def undo(self) -> None:
        self._shell.restore(self._key, self._before)


class Shell(QMainWindow):
    """The single wiring point, and the only place an edit is pushed."""

    def __init__(self, session: Session | None = None, applied_theme=None,
                 mode: str = theme.MODE_SYSTEM, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.theme = applied_theme if applied_theme is not None else theme.active_theme()
        self.metrics = theme.metrics(QApplication.instance())
        self.mode = mode
        self.session: Session | None = None
        self.stack = QUndoStack(self)
        self.last_export: exportdialog.ExportDialog | None = None
        self._key = ""
        self._editor_key = ""
        self._exported: Path | None = None
        self._canonical: Path | None = None
        self._shown = dict.fromkeys((name for name, _label in PANE_LABELS), True)
        # A closed window's own undo stack still emits as it is torn down, and no
        # widget is left to answer it.
        self._closing = False
        self.resize(*WINDOW_START)
        self._build_header()
        self._build_status()
        self._build_menu()
        central = QWidget()
        self.column = QVBoxLayout(central)
        self.column.setContentsMargins(0, 0, 0, 0)
        self.column.setSpacing(0)
        self.column.addWidget(self.header)
        self.body: QWidget = QWidget()
        self.column.addWidget(self.body, 1)
        self.setCentralWidget(central)
        self._install(session)

    # --- construction --------------------------------------------------------

    def _build_header(self) -> None:
        """One line: the product, the image, the profile, the state, the search."""
        self.product_label = QLabel(PRODUCT_NAME)
        self.product_label.setProperty("role", "heading")
        self.image_label = QLabel()
        self.profile_label = QLabel()
        self.profile_label.setFont(theme.mono_font())
        self.state_label = QLabel()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search lines")
        self.search.setFixedHeight(self.metrics.field_height)
        self.search.addAction(theme.icon("search"), QLineEdit.ActionPosition.LeadingPosition)
        line = QHBoxLayout()
        line.setContentsMargins(self.metrics.pad_md, self.metrics.pad_sm,
                                self.metrics.pad_md, self.metrics.pad_sm)
        line.setSpacing(self.metrics.gap)
        for widget in (self.product_label, self.image_label, self.profile_label,
                       self.state_label):
            line.addWidget(widget)
        line.addWidget(self.search, 1)
        self.header = QWidget()
        self.header.setLayout(line)
        self.search.textChanged.connect(self._set_term)
        self.escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self.search)
        self.escape.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.escape.activated.connect(self.clear_search)

    def _build_status(self) -> None:
        """The selected row's identity and span, the last export, and Export."""
        status_bar = self.statusBar()
        status_bar.setMinimumHeight(self.metrics.status_height)
        self.detail_label = QLabel()
        self.detail_label.setFont(theme.mono_font())
        self.export_label = QLabel("no export yet")
        self.export_label.setFont(theme.mono_font())
        ink = self.export_label.palette()
        ink.setColor(QPalette.ColorRole.WindowText, theme.color(self.theme, "text_secondary"))
        self.export_label.setPalette(ink)
        self.export_button = QPushButton("Export")
        self.export_button.setMinimumHeight(self.metrics.field_height)
        # The one accent-filled control in the window, from the theme's own rule.
        self.export_button.setProperty("role", "primary")
        self.export_button.clicked.connect(self.prompt_export)
        status_bar.addWidget(self.detail_label)
        status_bar.addPermanentWidget(self.export_label)
        status_bar.addPermanentWidget(self.export_button)

    def _build_menu(self) -> None:
        """File, Edit, View and Help, every item with the shortcut it really has."""
        file_menu = self.menuBar().addMenu("&File")
        self.open_action = self._add(file_menu, "&Open image...", "Ctrl+O", self.prompt_open)
        self.open_project_action = self._add(file_menu, "Open edit &list...", "",
                                             self.prompt_open_project)
        self.save_action = self._add(file_menu, "&Save edit list...", "Ctrl+S",
                                     self.prompt_save_project)
        self.export_action = self._add(file_menu, "&Export image...", "Ctrl+E",
                                       self.prompt_export)
        file_menu.addSeparator()
        self._add(file_menu, "&Quit", "", self.close)

        edit_menu = self.menuBar().addMenu("&Edit")
        self.undo_action = self.stack.createUndoAction(self, "&Undo")
        self.undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        self.redo_action = self.stack.createRedoAction(self, "&Redo")
        self.redo_action.setShortcut(QKeySequence("Ctrl+Y"))
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        self.rename_action = self._add(edit_menu, "&Rename occurrences...", "",
                                       self.prompt_rename)
        edit_menu.addSeparator()
        self.clear_action = self._add(edit_menu, "Clear this &edit", "", self.clear_edit)
        self.clear_all_action = self._add(edit_menu, "Clear &all edits", "",
                                          self.clear_all_edits)

        view_menu = self.menuBar().addMenu("&View")
        self.find_action = self._add(view_menu, "&Find line", "Ctrl+F", self.focus_search)
        self.next_pane_action = self._add(view_menu, "Next &pane", "F6", self.cycle_focus)
        view_menu.addSeparator()
        self.view_actions = self._choice_actions(
            view_menu, ((LINES, "&Lines"), (RECORDS, "&Records")), "view")
        self.order_actions = self._choice_actions(
            view_menu, ((APPEARANCE, "&Appearance"), (STORAGE, "&Storage")), "order")
        self.group_actions = self._choice_actions(
            view_menu, ((UNGROUPED, "&No grouping"), (BY_SPEAKER, "Group by &speaker"),
                        (BY_PLACE, "Group by &place")), "group")
        view_menu.addSeparator()
        self.pane_actions: dict[str, QAction] = {}
        for name, label in PANE_LABELS:
            action = view_menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(True)
            action.triggered.connect(lambda shown, pane=name: self.show_pane(pane, shown))
            self.pane_actions[name] = action

        help_menu = self.menuBar().addMenu("&Help")
        self._add(help_menu, f"&About {PRODUCT_NAME}", "", self.show_about)

        self._needs_image = (
            self.open_project_action, self.save_action, self.export_action,
            self.rename_action, self.clear_action, self.clear_all_action,
            self.find_action,
            *self.view_actions.actions(), *self.order_actions.actions(),
            *self.group_actions.actions(), *self.pane_actions.values(),
        )
        # A bound method, so Qt drops the connection with this window instead of
        # leaving a context-free lambda to fire at a QAction that is already gone.
        self.stack.cleanChanged.connect(self._update)

    def _add(self, menu, label: str, shortcut: str, slot) -> QAction:
        """One menu item, with its real shortcut written beside it."""
        action = QAction(label, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _choice_actions(self, menu, pairs, shape: str) -> QActionGroup:
        """One checkable single-choice group, wired to the pane's own control."""
        group = QActionGroup(self)
        for value, label in pairs:
            action = menu.addAction(label)
            action.setCheckable(True)
            action.setActionGroup(group)
            action.setData(value)
            action.triggered.connect(
                lambda _checked=False, v=value, s=shape: self.set_shape(s, v))
        return group

    # --- the session, the panes and their wiring ------------------------------

    def _install(self, session: Session | None) -> None:
        """The panes over `session`, or the empty state when there is no image."""
        shape = self.shape() or self._stored_shape()
        self.session = session
        self._key = ""
        self._editor_key = ""
        self._exported = None
        self.stack.clear()
        if session is not None and self._canonical is None:
            self._canonical = session.model.retail_path
        previous = self.body
        self.body = self._build_body()
        self.column.replaceWidget(previous, self.body)
        previous.deleteLater()
        if session is not None:
            self._apply_shape(shape)
            # The pane selects its first row while it is being built, which is before
            # this window can hear about it, so the editor and the context pane used to
            # open empty beside a highlighted row until the reader clicked a DIFFERENT
            # row. Replaying the selection once costs one call and closes that gap.
            selected = self.pane.selected()
            if selected:
                self.show_line(selected)
        self._update()

    def _build_body(self) -> QWidget:
        if self.session is None:
            self.empty = QLabel(NO_IMAGE)
            self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.empty.setWordWrap(True)
            self.empty.setProperty("role", "hint")
            return self.empty
        self.pane = lineview.LinePane(self.session, self.metrics, self.theme, self)
        # The floor is the constant OR whatever the pane's own controls need, whichever
        # is larger. Measured at 150 and 200 percent Windows text, the list pane's own
        # minimum grows to 475 and 603 while a fixed floor holds it at 368, so the chips
        # and the counters line elide. Letting the window grow instead is the honest
        # answer, and Qt already derives the window's minimum from its layout.
        self.pane.setMinimumWidth(max(LEFT_MIN, self.pane.minimumSizeHint().width()))
        self.editor = EditorSections(self.theme, self.metrics, self)
        self.editor.setMinimumWidth(CENTRE_MIN)
        self.context = contextpane.ContextPane(self.theme, self.metrics, self)
        self.context.setMinimumWidth(RIGHT_MIN)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        for widget in (self.pane, self.editor, self.context):
            self.splitter.addWidget(widget)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes(self._stored_sizes())
        self.pane.line_chosen.connect(self.show_line)
        self.pane.line_entered.connect(self.focus_new)
        self.editor.committed.connect(self.apply_edit)
        # A refused edit in NEW says why, in the same status line as every other
        # refusal in this window, instead of leaving the text silently unchanged.
        self.editor.refused.connect(self.statusBar().showMessage)
        # The move notice's one action selects the records that carry the row, so a
        # reader can act on what it just said without hunting in the list.
        self.editor.notice.records_requested.connect(self.show_records)
        for box, name in ((self.pane.shape_box, "view"), (self.pane.order_box, "order"),
                          (self.pane.group_box, "group")):
            box.currentIndexChanged.connect(
                lambda _index, s=name: self._sync(self._group_for(s), s))
        for name, widget in self.panes():
            widget.setVisible(self._shown.get(name, True))
        return self.splitter

    def panes(self) -> tuple[tuple[str, QWidget], ...]:
        """The three panes, or the one empty state when no image is open."""
        if self.session is None:
            return (("empty", self.empty),)
        return (("list", self.pane), ("editor", self.editor), ("context", self.context))

    def walk_panes(self) -> tuple[str, ...]:
        """Touch every pane, so a smoke run proves each one built and answers."""
        touched = []
        for name, pane in self.panes():
            pane.sizeHint()
            pane.isVisibleTo(self)
            touched.append(name)
        if self.session is not None:
            rows = self.pane.rows()
            self.pane.selected()
            self.pane.kind()
            self.pane.filters()
            self.shape()
            self.editor.new_text()
            self.editor.has_focus()
            if rows:
                self.pane.select_key(rows[0].key)
                self.show_line(rows[0].key)
        return tuple(touched)

    # --- what a row shows ----------------------------------------------------

    def show_records(self, keys: tuple[str, ...]) -> None:
        """Select the records a row is carried by, in the list, and say how many.

        This is the move notice's only action. A carrying record is a dialogue
        record, so the list is put on that tab and on the shape that lists records:
        a button that silently did nothing would be worse than no button.
        """
        if self.session is None or not keys:
            return
        if self.pane.kind() != RECORD:
            self.pane.set_kind(RECORD)
        if self.pane.view() != RECORDS:
            self.pane.set_view(RECORDS)
        found = self.pane.select_rows(keys)
        self.statusBar().showMessage(f"selected {found} of {len(keys)} carrying record(s)")

    def show_line(self, key: str) -> None:
        """Show one row everywhere it appears, from the session's own answers."""
        if self.session is None:
            return
        line = self.session.line(key)
        if line is None:
            return
        # A message belongs to the action that raised it and hides the row's own
        # identity while it stands, so landing on another row releases it.
        self.statusBar().clearMessage()
        self._key = key
        text = self.session.pending_text(key)
        state = self.session.state(key)
        # A row with no pending edit still shows its budget: the meter's own purpose is
        # to say how much room is left BEFORE the writer types, so the untouched state
        # is zeros against the same limit the edit will be measured against.
        meter = self.session.meter(key) or self.session.headroom(key)
        differs = self.session.differs_from_retail(key)
        reason = self.session.refusal_reason(key)
        name = span_detail(self.session, key)
        self.detail_label.setText(name)
        self.context.set_line(self.session, line)
        self.context.set_address(name)
        # The preview draws the RECORD, not the row, because that is what the box holds:
        # a record split by the game's own line break is one page of up to four lines,
        # and showing one row of it would show a fraction of what the reader will see.
        # The record's pending text carries every row's edit in it. A string slot names
        # no record, so the pane is told the row has no box rather than shown an empty
        # one, which is a box the engine never draws for it.
        self.context.set_preview_state(
            "" if line.view == SLOT
            else self.session.pending_text(line.target) if line.target else "")
        if self._editor_key != key:
            self._editor_key = key
            self.editor.set_line(line, state, meter, differs, reason,
                                 self.session.covering(key), self.session.sites(key),
                                 line.proven)
        else:
            self.editor.set_state(state, meter, differs, reason)
        # `set_pending` is what decides whether the caret in NEW wins, so it is
        # asked on every refresh rather than the shell deciding for it.
        self.editor.set_pending(text)
        self._update()

    def shape(self) -> dict[str, str]:
        """The list's shape, which is the part of the settings that lives in the pane."""
        if self.session is None:
            return {}
        return {"view": self.pane.view(), "order": self.pane.order(),
                "group": self.pane.group()}

    def set_shape(self, name: str, value: str) -> None:
        """One shape control, from the menu or from the pane's own combo."""
        if self.session is not None:
            getattr(self.pane, f"set_{name}")(value)

    def _group_for(self, name: str) -> QActionGroup:
        return {"view": self.view_actions, "order": self.order_actions,
                "group": self.group_actions}[name]

    def _sync(self, group: QActionGroup, name: str) -> None:
        """Check the menu action whose value the pane's own control now holds."""
        current = self.shape().get(name)
        for action in group.actions():
            if action.data() == current:
                action.setChecked(True)
                return

    def _apply_shape(self, values: Mapping[str, object]) -> None:
        """Put one shape on the pane, ignoring a value this build does not know."""
        view, order, group = (values.get("view"), values.get("order"), values.get("group"))
        if view in (LINES, RECORDS):
            self.pane.set_view(view)
        if order in (APPEARANCE, STORAGE):
            self.pane.set_order(order)
        if group in (UNGROUPED, BY_SPEAKER, BY_PLACE):
            self.pane.set_group(group)
        for name in ("view", "order", "group"):
            self._sync(self._group_for(name), name)

    def _stored_shape(self) -> dict[str, object]:
        """What the last session left, as the three keys this window owns."""
        stored = settings.load()
        return {key: stored.get(key) for key in ("view", "order", "group")}

    def _stored_sizes(self) -> list[int]:
        """The remembered pane sizes, floored so a stored file cannot starve a pane.

        A settings file written by an earlier build, or edited by hand, can hold a
        left pane narrower than the list needs. Measured: at 330 px the speaker and
        status columns left the text column 32 px, which draws as an ellipsis, so a
        stale size is a defect the user cannot see the cause of.
        """
        stored = settings.load().get("splitter")
        if isinstance(stored, list) and len(stored) == 3 and all(
                isinstance(size, int) and size > 0 for size in stored):
            floors = (LEFT_MIN, CENTRE_MIN, RIGHT_MIN)
            return [max(size, floor) for size, floor in zip(stored, floors)]
        return list(DEFAULT_SPLIT)

    # --- the one edit path ---------------------------------------------------

    def apply_edit(self, key: str, new: str) -> None:
        """The one way a line changes: one user action, one undo step.

        The edit is applied first and both sides are recorded as SNAPSHOTS of what the
        record held, so an undo restores exactly what was there. A refused combination
        leaves the record as it was and pushes nothing.
        """
        if self.session is None:
            return
        line = self.session.line(key)
        if line is None or not line.text:
            self.statusBar().showMessage(f"{key} has no text for an edit to replace.")
            return
        before = self.session.snapshot(key)
        self.write(key, new)
        after = self.session.snapshot(key)
        if after == before:
            return
        self.stack.push(_EditCommand(self, key, before, after))

    def write(self, key: str, text: str) -> None:
        """Write one row's pending text and redraw. It never pushes a command."""
        if self.session is None:
            return
        try:
            self.session.set_edit(key, text)
        except (textedit.TextEditError, KeyError) as error:
            self.statusBar().showMessage(str(error))
            return
        if self._key:
            self.pane.refresh(self._key)
            self.show_line(self._key)
        self._update()

    def restore(self, key: str, entries) -> None:
        """Put a record back to a snapshot. It never pushes a command."""
        if self.session is None:
            return
        self.session.restore(key, entries)
        if self._key:
            self.pane.refresh(self._key)
            self.show_line(self._key)
        self._update()

    def clear_edit(self) -> None:
        """Clear the selected row's own edit, as one step.

        It calls the session's own clear rather than writing the row's text back. Under the
        derived model a row already shows the text the export writes, so writing it back
        changed nothing and the edit stayed: measured, clearing a row left its record
        edited and an undo that restored it was the only way back.
        """
        if self.session is None or not self._key:
            return
        before = self.session.snapshot(self._key)
        try:
            self.session.clear_edit(self._key)
        except (textedit.TextEditError, KeyError) as error:
            self.statusBar().showMessage(str(error))
            return
        after = self.session.snapshot(self._key)
        if after != before:
            self.stack.push(_EditCommand(self, self._key, before, after,
                                         f"clear {self._key}"))
        if self._key:
            self.pane.refresh(self._key)
            self.show_line(self._key)
        self._update()

    def clear_all_edits(self) -> None:
        """Every pending edit, as one step.

        An edit no row of this image carries has no text to restore, so it is
        dropped outright rather than restored by an undo step.
        """
        if self.session is None or not self.session.edited_keys():
            return
        carried = [key for key in self.session.edited_keys()
                   if self.session.line(key) is not None]
        self.stack.beginMacro(f"clear {len(carried)} edit(s)")
        for key in carried:
            before = self.session.snapshot(key)
            try:
                self.session.clear_edit(key)
            except (textedit.TextEditError, KeyError) as error:
                self.statusBar().showMessage(str(error))
                continue
            after = self.session.snapshot(key)
            if after != before:
                self.stack.push(_EditCommand(self, key, before, after, f"clear {key}"))
        self.stack.endMacro()
        if len(carried) != len(self.session.edited_keys()):
            self.session.clear_all()
        self._update()

    def apply_rename(self, old: str, new: str,
                     chosen: tuple[tuple[str, frozenset[int]], ...]) -> int:
        """One undo step for a whole rename batch, through the same edit path.

        Each move is applied to the record's OWN text, which is the only thing this
        session stores per record, so two batches touching one record compose instead of
        the second replacing the first, and an offset that no longer reads what the dialog
        showed is reported rather than applied or dropped quietly.
        """
        if self.session is None:
            return 0
        moves = [(key, offsets) for key, offsets in chosen
                 if self.session.line(key) is not None and offsets]
        if not moves:
            return 0
        self.stack.beginMacro(f"rename {len(moves)} record(s)")
        applied = 0
        skipped: list[str] = []
        for key, offsets in moves:
            before = self.session.snapshot(key)
            skipped.extend(self.session.set_rename(key, old, new, offsets))
            after = self.session.snapshot(key)
            if after != before:
                self.stack.push(_EditCommand(self, key, before, after,
                                             f"rename in {key}"))
                applied += 1
        self.stack.endMacro()
        if skipped:
            self.statusBar().showMessage("; ".join(skipped))
        return applied

    # --- open, save and export -----------------------------------------------

    def prompt_open(self) -> None:
        if not self._may_discard():
            return
        chosen, _filters = QFileDialog.getOpenFileName(self, "Open image", "",
                                                      "GBA image (*.gba)")
        if chosen:
            self.load_image(chosen)

    def load_image(self, path: str | Path, project=None) -> bool:
        """Open an image read-only. A refusal is the engine's own sentence."""
        try:
            session = open_image(path, canonical=self._canonical, project=project)
        except (textedit.TextEditError, OSError) as error:
            QMessageBox.critical(self, PRODUCT_NAME, str(error))
            return False
        self._install(session)
        return True

    def prompt_open_project(self) -> None:
        if not self._need_image() or not self._may_discard():
            return
        chosen, _filters = QFileDialog.getOpenFileName(
            self, "Open edit list", "", f"Edit list (*{project_file.SUFFIX})")
        if not chosen:
            return
        try:
            saved = project_file.load(chosen)
        except (project_file.ProjectFileError, OSError) as error:
            QMessageBox.critical(self, PRODUCT_NAME, str(error))
            return
        self.load_image(self.session.model.path, project=saved)

    def prompt_save_project(self) -> None:
        """Save the edit list. The image itself is never written here."""
        if not self._need_image():
            return
        source = Path(self.session.model.path)
        chosen, _filters = QFileDialog.getSaveFileName(
            self, "Save edit list", str(source.with_suffix(project_file.SUFFIX)),
            f"Edit list (*{project_file.SUFFIX})")
        if not chosen:
            return
        try:
            project_file.save(self.session.project(), chosen)
        except (project_file.ProjectFileError, OSError) as error:
            QMessageBox.critical(self, PRODUCT_NAME, str(error))

    def prompt_export(self) -> None:
        if not self._need_image():
            return
        reason = export_reason(self.session, self._key)
        if reason:
            self.statusBar().showMessage(reason)
            return
        source = Path(self.session.model.path)
        chosen, _filters = QFileDialog.getSaveFileName(
            self, "Export image", str(source.with_name(f"{source.stem}-edited.gba")),
            "GBA image (*.gba)")
        if chosen:
            self.export_to(chosen)

    def export_to(self, path: str | Path) -> dict | None:
        """Always a new file, through the engine, with its refusal shown verbatim."""
        if not self._need_image():
            return None
        try:
            report = self.session.export(path)
        except (textedit.TextEditError, OSError) as error:
            self.surface_error(str(error))
            return None
        self._exported = Path(path)
        digest = str(report.get("output_sha256", ""))
        self.export_label.setText(
            f"exported {QTime.currentTime().toString('HH:mm:ss')}   {digest[:12]}")
        self.stack.setClean()
        dialog = exportdialog.ExportDialog(report, self._exported, self)
        self.last_export = dialog
        dialog.finished.connect(lambda _code: self.offer_open())
        dialog.show()
        self._update()
        return report

    def surface_error(self, message: str) -> None:
        """The engine writes these sentences for a user, so show one verbatim."""
        QMessageBox.warning(self, PRODUCT_NAME, message)
        self.statusBar().showMessage(message)

    def offer_open(self) -> None:
        """Offer the exported image once its summary is closed."""
        if self._exported is None:
            return
        answer = QMessageBox.question(self, PRODUCT_NAME, f"Open {self._exported.name} now?")
        if answer == QMessageBox.StandardButton.Yes:
            self.open_exported()

    def open_exported(self) -> bool:
        """Hand the exported file to whatever the system registered for it."""
        if self._exported is None:
            return False
        if QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._exported))):
            return True
        suffix = self._exported.suffix.lstrip(".")
        self.statusBar().showMessage(
            f"No application is registered to open .{suffix} on this machine.")
        return False

    # --- rename --------------------------------------------------------------

    def prompt_rename(self) -> None:
        """The rename surface, from the Edit menu: the dialog collects both names.

        A rename is one action, so the two names are typed in the dialog that also
        answers every occurrence; asking for half of it in a modal prompt first
        would be a second action.
        """
        if not self._need_image():
            return
        dialog = renamedialog.RenameDialog(self.session, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.apply_rename(dialog.old_edit.text(), dialog.new_edit.text(),
                              dialog.chosen())

    # --- focus, and the small print ------------------------------------------

    def focus_search(self) -> None:
        self.search.setFocus(Qt.FocusReason.ShortcutFocusReason)
        self.search.selectAll()

    def _set_term(self, term: str) -> None:
        if self.session is not None:
            self.pane.set_term(term)

    def clear_search(self) -> None:
        """Esc in the search field: an empty field hands the focus to the list."""
        if self.search.text():
            self.search.clear()
        elif self.session is not None:
            self.pane.table.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def focus_new(self, _key: str = "") -> None:
        self.editor.focus_new()

    def cycle_focus(self) -> None:
        """F6 walks the list, the editor and the context pane."""
        if self.session is None:
            return
        current = QApplication.focusWidget()
        if current is self.pane.table:
            self.editor.focus_new()
        elif current is self.editor or self.editor.has_focus():
            self.context.setFocus(Qt.FocusReason.ShortcutFocusReason)
        else:
            self.pane.table.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def show_pane(self, name: str, shown: bool) -> None:
        """Show or hide one pane. The choice survives a new image."""
        self._shown[name] = shown
        for pane_name, widget in self.panes():
            if pane_name == name:
                widget.setVisible(shown)

    def show_about(self) -> None:
        QMessageBox.about(self, PRODUCT_NAME, f"{PRODUCT_NAME} {PRODUCT_VERSION}")

    # --- the header, the title and what is enabled ---------------------------

    def _need_image(self) -> bool:
        if self.session is None:
            self.statusBar().showMessage(NO_IMAGE_TIP)
            return False
        return True

    def _may_discard(self) -> bool:
        """Ask before an action that would drop pending edits. True to go on."""
        if self.session is None or self.stack.isClean():
            return True
        edits = len(self.session.edited_keys())
        answer = QMessageBox.question(
            self, PRODUCT_NAME,
            f"Discard {edits} pending edit" + ("" if edits == 1 else "s")
            + " without exporting?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)
        return answer == QMessageBox.StandardButton.Discard

    def _update(self) -> None:
        if self._closing:
            return
        self._update_header()
        self._update_actions()
        self._update_title()

    def _update_header(self) -> None:
        """The header's pairs. A self-describing value drops its label."""
        if self.session is None:
            self.image_label.setText("no image")
            self.image_label.setToolTip(NO_IMAGE)
            self.profile_label.setText("")
            self.profile_label.setToolTip("")
            self.state_label.setText(status.label(State.UNCHANGED))
            return
        path = Path(self.session.model.path)
        self.image_label.setText(path.name)
        self.image_label.setToolTip(str(path))
        self.profile_label.setText(self.session.model.layout.profile.key)
        self.profile_label.setToolTip("Detected profile")
        self.state_label.setText(project_text(self.session))

    def _update_actions(self) -> None:
        """Enable what the session can do now, and say why when it cannot."""
        loaded = self.session is not None
        for action in self._needs_image:
            action.setEnabled(loaded)
            action.setToolTip("" if loaded else NO_IMAGE_TIP)
        self.export_button.setEnabled(loaded)
        self.export_button.setToolTip("" if loaded else NO_IMAGE_TIP)
        if not loaded:
            return
        reason = export_reason(self.session, self._key)
        for target in (self.export_action, self.export_button):
            target.setEnabled(not reason)
            target.setToolTip(reason or EXPORT_TIP)
        edits = bool(self.session.edited_keys())
        self.clear_all_action.setEnabled(edits)
        self.clear_all_action.setToolTip("" if edits else "There are no pending edits.")
        pending = edits and bool(self._key) and \
            self.session.state(self._key) is not State.UNCHANGED
        self.clear_action.setEnabled(bool(pending))
        self.clear_action.setToolTip(
            "" if pending else "Select a line that has a pending edit.")

    def _update_title(self) -> None:
        name = "no image" if self.session is None else Path(self.session.model.path).name
        self.setWindowTitle(f"{'' if self.stack.isClean() else '* '}{name} - {PRODUCT_NAME}")

    # --- the settings --------------------------------------------------------

    def _save_settings(self) -> None:
        """One write: the theme it ran under, the splitter, and the list's shape."""
        values: dict[str, object] = {"theme": self.mode}
        if self.session is not None:
            values["splitter"] = list(self.splitter.sizes())
        values.update(self.shape())
        settings.save(values)

    def closeEvent(self, event) -> None:
        self._save_settings()
        self._closing = True
        super().closeEvent(event)
