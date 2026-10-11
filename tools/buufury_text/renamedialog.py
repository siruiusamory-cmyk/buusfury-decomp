"""The per-occurrence rename: a normal resizable window over the engine's hits.

Rows start at the engine's own decision, so an occurrence retail already settled
is not asked about. 'Default for undecided hits' answers the rest, and the
window returns one set of offsets per record for the shell to apply as one step.
"""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QStyledItemDelegate,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from tools.webfoot import textedit

from . import theme
from .session import Hit, Session

#: The three answers, in the order the default control and the cycling use.
ANSWERS: tuple[tuple[str, str], ...] = (
    (textedit.UNCLEAR, "Ask"),
    (textedit.RENAME, "Rename"),
    (textedit.KEEP, "Keep"),
)
WORD = {textedit.RENAME: "RENAME", textedit.KEEP: "KEEP", textedit.UNCLEAR: "ASK"}

ROLE_CHOSEN = Qt.ItemDataRole.UserRole + 1

#: The order the Space key and the cycle walk through.
CYCLE = (textedit.RENAME, textedit.KEEP, textedit.UNCLEAR)

DECISION_COLUMN = 3


class HitModel(QAbstractTableModel):
    """The engine's occurrences, with the answer each one currently carries."""

    HEADERS = ("Record", "Snippet", "Retail says", "Decision")

    #: The Apply count changed, so the button's label has to be rebuilt.
    changed = Signal()

    def __init__(self, hits: tuple[Hit, ...], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.hits = hits
        self._chosen = [hit.decision for hit in hits]
        self.default = textedit.UNCLEAR

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
        if role == Qt.ItemDataRole.FontRole and column in (0, DECISION_COLUMN):
            return theme.mono_font()
        return None

    def setData(self, index: QModelIndex, value: object,
                role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid() or role != ROLE_CHOSEN or index.column() != DECISION_COLUMN:
            return False
        if value not in WORD:
            return False
        self._chosen[index.row()] = value
        self.dataChanged.emit(index, index,
                              [Qt.ItemDataRole.DisplayRole, ROLE_CHOSEN])
        self.changed.emit()
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = super().flags(index)
        if index.column() == DECISION_COLUMN and self.hits[index.row()].at >= 0:
            return flags | Qt.ItemFlag.ItemIsEditable
        return flags

    def effective(self, row: int) -> str:
        """What this row will do. An undecided row follows the default control."""
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
        index = self.index(row, DECISION_COLUMN)
        current = self._chosen[row]
        following = textedit.RENAME if current not in CYCLE else \
            CYCLE[(CYCLE.index(current) + 1) % len(CYCLE)]
        self.setData(index, following, ROLE_CHOSEN)

    def rename_count(self) -> int:
        return sum(1 for row in range(len(self.hits)) if self.effective(row) == textedit.RENAME)

    def renamed(self) -> dict[str, frozenset[int]]:
        """The offsets to replace per record: one entry per record, never two steps."""
        chosen: dict[str, set[int]] = {}
        for row, hit in enumerate(self.hits):
            if self.effective(row) == textedit.RENAME:
                chosen.setdefault(hit.key, set()).add(hit.at)
        return {key: frozenset(offsets) for key, offsets in chosen.items()}


class DecisionDelegate(QStyledItemDelegate):
    """One cell, one compact combo on activation: never a widget per row."""

    def createEditor(self, parent: QWidget, _option, _index: QModelIndex) -> QWidget:
        combo = QComboBox(parent)
        for value, label in ANSWERS:
            combo.addItem(label, value)
        return combo

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:
        editor.setCurrentIndex(max(0, editor.findData(index.data(ROLE_CHOSEN))))

    def setModelData(self, editor: QComboBox, model, index: QModelIndex) -> None:
        model.setData(index, editor.currentData(), ROLE_CHOSEN)


class HitTable(QTableView):
    """Space cycles the row's answer, the documented keyboard route."""

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Space and self.currentIndex().isValid():
            self.model().cycle(self.currentIndex().row())
            return
        super().keyPressEvent(event)


class RenameDialog(QDialog):
    """Where the user answers each occurrence, and where Apply returns the batch."""

    def __init__(self, session: Session, old: str, new: str, metrics,
                 theme_, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Rename {old} to {new}")
        self.resize(920, 560)
        self.setMinimumSize(720, 420)
        self.model = HitModel(session.rename_hits(old), self)
        self.model.set_default(textedit.UNCLEAR)
        self.sentence = QLabel(
            f"This replaces {old} with {new} in the dialogue occurrences below.")
        self.sentence.setWordWrap(True)
        default_label = QLabel("Default for undecided hits:")
        self.default_box = QComboBox()
        for value, label in ANSWERS:
            self.default_box.addItem(label, value)
        self.default_box.currentIndexChanged.connect(
            lambda _index: self.model.set_default(self.default_box.currentData()))
        self.table = HitTable()
        self.table.setModel(self.model)
        self.table.setItemDelegateForColumn(DECISION_COLUMN, DecisionDelegate(self.table))
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableView.EditTrigger.DoubleClicked
                                   | QTableView.EditTrigger.EditKeyPressed)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(metrics.row_height)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setFixedHeight(metrics.header_height)
        self.apply_button = QPushButton()
        self.apply_button.setDefault(True)
        self.apply_button.clicked.connect(self.accept)
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.buttons.addButton(self.apply_button, QDialogButtonBox.ButtonRole.AcceptRole)
        self.buttons.rejected.connect(self.reject)
        self.model.changed.connect(self.update_count)
        default_row = QHBoxLayout()
        default_row.addWidget(default_label)
        default_row.addWidget(self.default_box)
        default_row.addStretch(1)
        column = QVBoxLayout(self)
        column.setContentsMargins(12, 12, 12, 12)
        column.setSpacing(metrics.gap)
        column.addWidget(self.sentence)
        column.addLayout(default_row)
        column.addWidget(self.table, 1)
        column.addWidget(self.buttons)
        self.update_count()

    def update_count(self) -> None:
        self.apply_button.setText(f"Apply {self.model.rename_count()} decisions")

    def renamed(self) -> dict[str, frozenset[int]]:
        """The offsets per record the user accepted, empty when nothing changes."""
        return self.model.renamed()

    def choose_default(self, label: str) -> None:
        """Pick the default by its visible word, for the keyboard and for a test."""
        for index in range(self.default_box.count()):
            if self.default_box.itemText(index) == label:
                self.default_box.setCurrentIndex(index)
                return
