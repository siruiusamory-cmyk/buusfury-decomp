"""The per-occurrence rename: the two names, one row per hit, one answer per hit.

A rename is a decision about an occurrence, not about a record, so the window shows
every occurrence of the spelling in Replace and what retail says at that offset. Each
row starts at the engine's own answer, `Default for undecided hits` answers the rest,
and the window returns the offsets the user accepted for the shell to apply as one
step.
"""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QPainter

from tools.webfoot import textedit

from . import theme
from .session import Hit, Session

#: The three answers, in the order the default control and the compact combo show them.
ANSWERS: tuple[tuple[str, str], ...] = (
    (textedit.UNCLEAR, "Ask"),
    (textedit.RENAME, "Rename"),
    (textedit.KEEP, "Keep"),
)
WORD = {textedit.RENAME: "Rename", textedit.KEEP: "Keep", textedit.UNCLEAR: "Ask"}

ROLE_CHOSEN = Qt.ItemDataRole.UserRole + 1

#: The order the Space key walks a row through.
CYCLE = (textedit.RENAME, textedit.KEEP, textedit.UNCLEAR)

DECISION_COLUMN = 3


class HitModel(QAbstractTableModel):
    """The engine's occurrences, with the answer each one currently carries."""

    HEADERS = ("Record", "Line", "Retail says", "Decision")

    #: The apply count changed, so the button's label has to be rebuilt.
    changed = Signal()

    def __init__(self, hits: tuple[Hit, ...], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.hits = hits
        self._chosen = [hit.decision for hit in hits]
        self.default = textedit.UNCLEAR

    def set_hits(self, hits: tuple[Hit, ...]) -> None:
        """Point the table at another spelling's occurrences, keeping the default.

        Every answer is the engine's own, so a refill starts from the engine again
        rather than carrying a decision onto an occurrence it was not made about.
        """
        self.beginResetModel()
        self.hits = hits
        self._chosen = [hit.decision for hit in hits]
        self.endResetModel()
        self.changed.emit()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.hits)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole) -> object:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.HEADERS[section]
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object:
        if not index.isValid():
            return None
        hit = self.hits[index.row()]
        column = index.column()
        if role == ROLE_CHOSEN:
            return self._chosen[index.row()]
        if role == Qt.ItemDataRole.ToolTipRole:
            return f"{hit.key} at {hit.at}" if hit.at >= 0 else \
                "the engine could not place this occurrence, so it stays as it is"
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return hit.key
            if column == 1:
                return hit.snippet
            if column == 2:
                return hit.retail
            if column == DECISION_COLUMN:
                return WORD[self.effective(index.row())]
            return ""
        if role == Qt.ItemDataRole.FontRole and column == 0:
            return theme.mono_font()
        return None

    def setData(self, index: QModelIndex, value: object,
                role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid() or role != ROLE_CHOSEN or index.column() != DECISION_COLUMN:
            return False
        if value not in WORD:
            return False
        self._chosen[index.row()] = value
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, ROLE_CHOSEN])
        self.changed.emit()
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = super().flags(index)
        if index.column() == DECISION_COLUMN and self.hits[index.row()].at >= 0:
            return flags | Qt.ItemFlag.ItemIsEditable
        return flags

    def effective(self, row: int) -> str:
        """What this row will do. Its own answer first, then the default control."""
        hit = self.hits[row]
        if hit.at < 0:
            return textedit.KEEP
        chosen = self._chosen[row]
        if chosen in (textedit.RENAME, textedit.KEEP):
            return chosen
        return self.default

    def set_default(self, decision: str) -> None:
        self.default = decision
        top = self.index(0, DECISION_COLUMN)
        bottom = self.index(len(self.hits) - 1, DECISION_COLUMN)
        if top.isValid() and bottom.isValid():
            self.dataChanged.emit(top, bottom, [Qt.ItemDataRole.DisplayRole])
        self.changed.emit()

    def cycle(self, row: int) -> None:
        """Walk one row through Rename, Keep and Ask."""
        current = self._chosen[row]
        following = textedit.RENAME if current not in CYCLE else \
            CYCLE[(CYCLE.index(current) + 1) % len(CYCLE)]
        self.setData(self.index(row, DECISION_COLUMN), following, ROLE_CHOSEN)

    def rename_count(self) -> int:
        """How many occurrences will actually change."""
        return sum(1 for row in range(len(self.hits))
                   if self.effective(row) == textedit.RENAME)

    def chosen(self) -> tuple[tuple[str, frozenset[int]], ...]:
        """The offsets to replace per record: one entry per record, never two steps."""
        picked: dict[str, set[int]] = {}
        for row, hit in enumerate(self.hits):
            if self.effective(row) == textedit.RENAME:
                picked.setdefault(hit.key, set()).add(hit.at)
        return tuple((key, frozenset(offsets)) for key, offsets in picked.items())


class DecisionDelegate(QStyledItemDelegate):
    """Every cell of the table, and the one compact combo the decision cell opens.

    One delegate draws the row chrome for all four columns, so the divider, the
    selection fill and the accent indicator cannot be applied twice or missed.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._shape = theme.active_metrics()

    def sizeHint(self, option, index: QModelIndex) -> QSize:
        return QSize(option.rect.width(), self._shape.row_height)

    def paint(self, painter: QPainter, option, index: QModelIndex) -> None:
        applied = theme.active_theme()
        theme.paint_row_background(painter, option, applied)
        painter.save()
        painter.setFont(theme.mono_font() if index.column() == 0 else theme.fonts().body)
        painter.setPen(theme.color(applied, "text_primary"))
        rect = option.rect.adjusted(self._shape.pad_md, 0, -self._shape.pad_md, 0)
        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         painter.fontMetrics().elidedText(
                             text, Qt.TextElideMode.ElideRight, max(0, rect.width())))
        theme.paint_divider(painter, option.rect, applied)
        if option.state & QStyle.StateFlag.State_Selected \
                and option.state & QStyle.StateFlag.State_HasFocus:
            theme.paint_focus_edge(painter, option.rect, applied)
        painter.restore()

    def createEditor(self, parent: QWidget, _option, index: QModelIndex) -> QWidget | None:
        if index.column() != DECISION_COLUMN:
            return None
        combo = QComboBox(parent)
        for value, label in ANSWERS:
            combo.addItem(label, value)
        return combo

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:
        editor.setCurrentIndex(max(0, editor.findData(index.data(ROLE_CHOSEN))))

    def setModelData(self, editor: QComboBox, model, index: QModelIndex) -> None:
        model.setData(index, editor.currentData(), ROLE_CHOSEN)


class HitTable(QTableView):
    """Space cycles the row's answer, which is the documented keyboard route."""

    def keyPressEvent(self, event) -> None:
        model = self.model()
        if event.key() == Qt.Key.Key_Space and self.currentIndex().isValid() \
                and isinstance(model, HitModel):
            model.cycle(self.currentIndex().row())
            return
        super().keyPressEvent(event)


class RenameDialog(QDialog):
    """Where the two names are collected, each occurrence is answered, and Apply returns.

    The two names may be passed in, or typed here: a rename is one action, and asking
    for half of it in a second modal prompt would be a second action.
    """

    def __init__(self, session: Session, old: str = "", new: str = "",
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.session = session
        self.resize(920, 560)
        self.setMinimumSize(720, 420)
        self.setModal(True)
        shape = theme.active_metrics()
        self.replace_label = QLabel("Replace")
        self.replace_label.setProperty("role", "caption")
        self.with_label = QLabel("with")
        self.with_label.setProperty("role", "caption")
        self.old_edit = QLineEdit(old)
        self.new_edit = QLineEdit(new)
        for field in (self.old_edit, self.new_edit):
            # The body face, not the data face: these hold prose words, not ids.
            field.setFont(theme.fonts().body)
            field.setMinimumHeight(shape.field_height)
        self.old_edit.setAccessibleName("Replace")
        self.new_edit.setAccessibleName("The name to put in its place")
        self.sentence = QLabel()
        self.sentence.setWordWrap(True)
        self.notice = QLabel()
        self.notice.setWordWrap(True)
        self.notice.setProperty("role", "caption")
        self.default_label = QLabel("Default for undecided hits")
        self.default_box = QComboBox()
        for value, label in ANSWERS:
            self.default_box.addItem(label, value)
        self.default_box.currentIndexChanged.connect(
            lambda _index: self.model.set_default(self.default_box.currentData()))
        self.table = HitTable()
        self.model = HitModel((), self)
        self.table.setModel(self.model)
        self.table.setItemDelegate(DecisionDelegate(self.table))
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableView.EditTrigger.DoubleClicked
                                   | QTableView.EditTrigger.EditKeyPressed)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(shape.row_height)
        header = self.table.horizontalHeader()
        header.setFont(theme.fonts().label)
        header.setFixedHeight(shape.header_height)
        header.setTextElideMode(Qt.TextElideMode.ElideRight)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.apply_button = QPushButton()
        self.apply_button.setDefault(True)
        self.apply_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.model.changed.connect(self.update_count)
        fields_row = QHBoxLayout()
        fields_row.setSpacing(shape.gap)
        fields_row.addWidget(self.replace_label)
        fields_row.addWidget(self.old_edit, 1)
        fields_row.addWidget(self.with_label)
        fields_row.addWidget(self.new_edit, 1)
        default_row = QHBoxLayout()
        default_row.setSpacing(shape.gap)
        default_row.addWidget(self.default_label)
        default_row.addWidget(self.default_box)
        default_row.addStretch(1)
        buttons = QHBoxLayout()
        buttons.setSpacing(shape.gap)
        buttons.addStretch(1)
        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.apply_button)
        column = QVBoxLayout(self)
        column.setContentsMargins(shape.pad_lg, shape.pad_lg, shape.pad_lg, shape.pad_lg)
        column.setSpacing(shape.gap)
        column.addLayout(fields_row)
        column.addWidget(self.sentence)
        column.addLayout(default_row)
        column.addWidget(self.notice)
        column.addWidget(self.table, 1)
        column.addLayout(buttons)
        # Connected after the fields are seeded, so the first refill is the only one
        # that runs before the window is usable.
        self.old_edit.textChanged.connect(self.reload)
        self.new_edit.textChanged.connect(self.reload)
        self.reload()

    def showEvent(self, event) -> None:
        """First focus belongs on the table, never on the button that closes."""
        super().showEvent(event)
        self.table.setFocus()

    def reload(self) -> None:
        """Re-query the engine for the spelling in Replace and refill the table.

        A spelling shorter than two characters is not a rename, so nothing is asked
        of the engine and the table says what it is waiting for instead.
        """
        old = self.old_edit.text()
        self.model.set_hits(self.session.rename_hits(old) if len(old) > 1 else ())
        old, new = self.old_edit.text(), self.new_edit.text()
        self.setWindowTitle(f"Rename {old} to {new}" if old and new else "Rename")
        self.sentence.setText(self._sentence(old, new))
        notice = self._notice(old)
        self.notice.setText(notice)
        self.notice.setVisible(bool(notice))
        self.update_count()

    @staticmethod
    def _sentence(old: str, new: str) -> str:
        if old and new:
            return (f"This replaces {old} with {new} in the occurrences below. Each row is "
                    "one occurrence, so a decision applies to that occurrence alone.")
        return ("A rename replaces one spelling with another in the occurrences below. Each "
                "row is one occurrence, so a decision applies to that occurrence alone.")

    def _notice(self, old: str) -> str:
        if not old:
            return "Type the name to replace, then the name to put in its place."
        if len(old) < 2:
            return f"A rename needs at least two characters, and {old!r} is one."
        if not self.model.hits:
            return f"No dialogue occurrence of {old!r} can be decided from retail."
        return ""

    def update_count(self) -> None:
        """The count is what will change; the button waits for a name to change it to."""
        count = self.model.rename_count()
        ready = bool(count) and bool(self.new_edit.text())
        self.apply_button.setText(f"Apply {count} decisions")
        self.apply_button.setEnabled(ready)
        if ready:
            self.apply_button.setToolTip("")
        elif count:
            self.apply_button.setToolTip("Type the name to put in its place")
        else:
            self.apply_button.setToolTip("No occurrence changes yet")

    def default_choice(self) -> str:
        return self.default_box.currentData()

    def chosen(self) -> tuple[tuple[str, frozenset[int]], ...]:
        """The records and offsets the user accepted for the spelling in Replace."""
        return self.model.chosen()
