"""One read-only table model, shared by every destination that shows rows.

A model rather than one widget per row: an assembled range index covers a whole
image in thousands of spans, and a record table covers hundreds of records, so a
widget each is the pattern `docs/desktop-ui.md` forbids. The rows arrive already
rendered as strings, because what a cell says is the page's statement and not
the model's.
"""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QWidget


class RowsModel(QAbstractTableModel):
    """A read-only table over strings a page has already rendered."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._headers: tuple[str, ...] = ()
        self._rows: tuple[tuple[str, ...], ...] = ()

    def set_rows(
        self, headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]
    ) -> None:
        self.beginResetModel()
        self._headers = tuple(headers)
        self._rows = tuple(rows)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        return self._rows[index.row()][index.column()]

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation != Qt.Orientation.Horizontal:
            return None
        return self._headers[section]
