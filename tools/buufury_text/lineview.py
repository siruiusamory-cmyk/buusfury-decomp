"""The left list: one table over ``Session.matching``, its status cell and its toggles.

The rows are whatever the session leaves after the search term, the tab and the
filter toggles. Every state is drawn as a marker shape, an icon and the full
word, so a reader who cannot separate the hues still reads the row.
"""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QRect, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QStyle,
    QStyledItemDelegate,
    QTableView,
    QTabBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import status as status_words
from . import theme
from .session import RECORD, SLOT, Line, Session, State

#: How a delegate finds the state and the row without rebuilding a Line.
ROLE_STATE = Qt.ItemDataRole.UserRole + 1
ROLE_LINE = Qt.ItemDataRole.UserRole + 2

IDENTITY_WIDTH = 54
STATUS_WIDTH = 116
AUX_WIDTH = 26
MARKER_COLUMN = 7

#: The state filters, in the order the toggles appear. Control units answer a
#: different question, so that toggle is not a state.
FILTERS: tuple[tuple[str, frozenset[State]], ...] = (
    ("Edited", frozenset({State.EDITED})),
    ("Will move", frozenset({State.WILL_MOVE})),
    ("Refused", frozenset({State.REFUSED})),
)
CONTROL_FILTER = "Has control code"

#: The two system lists. They are never merged.
TABS: tuple[tuple[str, str], ...] = (
    ("Dialogue", RECORD),
    ("Names && bios", SLOT),  # a doubled ampersand renders as one, not a mnemonic
)


class LineModel(QAbstractTableModel):
    """The rows one list shows. It answers from the session and stores no rule."""

    HEADERS = ("ID", "Text", "Status", "Differs")

    def __init__(self, session: Session | None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self._rows: tuple[Line, ...] = ()

    def rows(self) -> tuple[Line, ...]:
        return self._rows

    def shows_auxiliary(self) -> bool:
        """Whether the retail marker column has anything to say."""
        return any(line.shows_retail for line in self._rows)

    def refresh(self, kind: str, term: str = "", states: frozenset[State] = frozenset(),
                locked: bool | None = None) -> None:
        self.beginResetModel()
        self._rows = () if self._session is None else self._session.matching(
            term, kind=kind, states=states, locked=locked)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole) -> object:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.HEADERS[section]
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object:
        if not index.isValid() or self._session is None:
            return None
        line = self._rows[index.row()]
        column = index.column()
        if role == ROLE_LINE:
            return line
        if role == ROLE_STATE:
            return self._session.state(line.key)
        if role == Qt.ItemDataRole.ToolTipRole:
            if column == 3:
                return status_words.auxiliary_label()
            if column == 2:
                return status_words.label(self._session.state(line.key))
            return line.key
        if role == Qt.ItemDataRole.FontRole and column == 0:
            return theme.mono_font()
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return line.key
            if column == 1:
                return line.text
            if column == 3 and self._session.differs_from_retail(line.key):
                return status_words.AUXILIARY.glyph
            return ""
        return None


def paint_item_background(painter: QPainter, option, theme_) -> None:
    """One row's own background: selection first, hover only when it is not selected."""
    if option.state & QStyle.StateFlag.State_Selected:
        painter.fillRect(option.rect, theme.color(theme_, "selection"))
    elif option.state & QStyle.StateFlag.State_MouseOver:
        painter.fillRect(option.rect, theme.color(theme_, "surface_raised"))


def paint_marker(painter: QPainter, rect: QRect, marker: str, pen) -> None:
    """The shape channel: the same state reads without any colour at all."""
    height = rect.height() - 6
    if height <= 0:
        return
    left, top = rect.left() + 2, rect.top() + 3
    if marker == "none":
        return
    if marker == "block":
        painter.fillRect(QRect(left, top, 8, 8), pen.color())
        return
    if marker == "double":
        painter.fillRect(QRect(left, top, 2, height), pen.color())
        painter.fillRect(QRect(left + 4, top, 2, height), pen.color())
        return
    if marker == "dashed":
        third = max(2, height // 3)
        painter.fillRect(QRect(left, top, 3, third), pen.color())
        painter.fillRect(QRect(left, top + height - third, 3, third), pen.color())
        return
    painter.fillRect(QRect(left, top, 3, height), pen.color())


class StatusDelegate(QStyledItemDelegate):
    """Draws the marker, the icon and the full state word for one row."""

    def __init__(self, theme_, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme_

    def paint(self, painter: QPainter, option, index: QModelIndex) -> None:
        state = index.data(ROLE_STATE)
        if state is None:
            super().paint(painter, option, index)
            return
        word = status_words.presentation(state)
        fill, ink = theme.state_colors(self._theme, state)
        painter.save()
        paint_item_background(painter, option, self._theme)
        if option.state & QStyle.StateFlag.State_Selected and \
                option.state & QStyle.StateFlag.State_HasFocus:
            painter.fillRect(QRect(option.rect.left(), option.rect.bottom() - 1,
                                   option.rect.width(), 2),
                             theme.color(self._theme, "focus"))
        paint_marker(painter, option.rect, word.marker, theme.state_marker(self._theme, state))
        badge = QRect(option.rect.left() + MARKER_COLUMN, option.rect.top() + 2,
                      max(0, option.rect.width() - MARKER_COLUMN - 4), option.rect.height() - 4)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill)
        painter.drawRoundedRect(badge, 3, 3)
        icon_rect = QRect(badge.left() + 4, badge.top() + (badge.height() - 16) // 2, 16, 16)
        theme.icon(word.icon).paint(painter, icon_rect)
        text_rect = QRect(icon_rect.right() + 4, badge.top(),
                          max(0, badge.right() - icon_rect.right() - 4), badge.height())
        painter.setPen(ink)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         painter.fontMetrics().elidedText(word.word, Qt.TextElideMode.ElideRight,
                                                          text_rect.width()))
        painter.restore()


class AuxDelegate(QStyledItemDelegate):
    """The 'this image already differs from the original game' marker."""

    def __init__(self, theme_, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme_

    def paint(self, painter: QPainter, option, index: QModelIndex) -> None:
        glyph = index.data(Qt.ItemDataRole.DisplayRole)
        painter.save()
        paint_item_background(painter, option, self._theme)
        if glyph:
            painter.setPen(theme.color(self._theme, "text_secondary"))
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, str(glyph))
        painter.restore()


class LineTable(QTableView):
    """The one table. Enter is the documented route into the editor."""

    entered = Signal()

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.entered.emit()
            return
        super().keyPressEvent(event)


class LinePane(QWidget):
    """The left pane: the two system tabs, the filter toggles and the table."""

    line_chosen = Signal(str)
    line_entered = Signal(str)

    def __init__(self, session: Session | None, metrics, theme_,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self._theme = theme_
        self._term = ""
        self._kind = RECORD
        self._selected = ""
        self._chip_height = metrics.chip_height
        self._model = LineModel(session, self)
        self.tabs = QTabBar()
        self.tabs.setExpanding(False)
        for title, _kind in TABS:
            self.tabs.addTab(title)
        self.counters = QLabel()
        self.chips = [self._chip(name) for name, _states in FILTERS]
        self.control_chip = self._chip(CONTROL_FILTER)
        self.table = LineTable()
        self._build(metrics)
        self.tabs.currentChanged.connect(self._tab_changed)
        self.refresh()

    # --- construction --------------------------------------------------------

    def _chip(self, name: str) -> QToolButton:
        chip = QToolButton()
        chip.setText(name)
        chip.setCheckable(True)
        chip.setProperty("filterChip", True)
        chip.setMinimumHeight(self._chip_height)
        chip.toggled.connect(self.refresh)
        return chip

    def _build(self, metrics) -> None:
        self.table.setModel(self._model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setWordWrap(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(metrics.row_height)
        header = self.table.horizontalHeader()
        header.setFixedHeight(metrics.header_height)
        for column in (0, 2, 3):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, IDENTITY_WIDTH)
        self.table.setColumnWidth(2, STATUS_WIDTH)
        self.table.setColumnWidth(3, AUX_WIDTH)
        self.table.setItemDelegateForColumn(2, StatusDelegate(self._theme, self.table))
        self.table.setItemDelegateForColumn(3, AuxDelegate(self._theme, self.table))
        self.table.selectionModel().currentRowChanged.connect(self._row_changed)
        self.table.entered.connect(self._row_entered)
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(metrics.gap)
        toggle_row.addWidget(self.tabs)
        toggle_row.addWidget(self.counters)
        toggle_row.addStretch(1)
        chips_row = QHBoxLayout()
        chips_row.setSpacing(metrics.gap)
        for chip in [*self.chips, self.control_chip]:
            chips_row.addWidget(chip)
        chips_row.addStretch(1)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(metrics.gap)
        column.addLayout(toggle_row)
        column.addLayout(chips_row)
        column.addWidget(self.table, 1)

    # --- what the list shows -------------------------------------------------

    def kind(self) -> str:
        return self._kind

    def next_tab(self) -> None:
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count())

    def set_kind(self, kind: str) -> None:
        for index, (_title, tab_kind) in enumerate(TABS):
            if tab_kind == kind:
                self.tabs.setCurrentIndex(index)
                return

    def set_term(self, term: str) -> None:
        if term != self._term:
            self._term = term
            self.refresh()

    def clear_filters(self) -> None:
        """Uncheck every toggle, so a jump to a record is not hidden by a filter."""
        for chip in [*self.chips, self.control_chip]:
            chip.setChecked(False)

    def filters(self) -> tuple[frozenset[State], bool | None]:
        """The states the checked toggles ask for, and whether control units are asked for."""
        states: frozenset[State] = frozenset()
        for chip, (_name, chip_states) in zip(self.chips, FILTERS):
            if chip.isChecked():
                states = states | chip_states
        return states, True if self.control_chip.isChecked() else None

    def rows(self) -> tuple[Line, ...]:
        return self._model.rows()

    def selected(self) -> str:
        return self._selected

    def select_key(self, key: str) -> bool:
        """Select a row the list already holds, without re-running the search."""
        for row, line in enumerate(self._model.rows()):
            if line.key == key:
                self.table.setCurrentIndex(self._model.index(row, 0))
                return True
        return False

    def select_first(self, keys) -> bool:
        """Select the first of ``keys`` this list holds, if it holds any."""
        for key in keys:
            if self.select_key(key):
                return True
        return False

    def refresh(self, keep: str | None = None) -> None:
        """Re-run the search and the filters, keeping one row selected when asked."""
        states, locked = self.filters()
        self._model.refresh(self._kind, self._term, states, locked)
        self.table.setColumnHidden(3, not self._model.shows_auxiliary())
        self._update_chips()
        self._update_counters()
        if keep is not None:
            self._selected = keep
            self.select_key(keep)
            return
        rows = self._model.rows()
        if rows and not self.table.currentIndex().isValid():
            self.table.setCurrentIndex(self._model.index(0, 0))

    # --- signals out ---------------------------------------------------------

    def _tab_changed(self, index: int) -> None:
        self._kind = TABS[index][1]
        self._selected = ""
        self.table.setCurrentIndex(QModelIndex())
        self.refresh()

    def _row_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        key = "" if not current.isValid() else self._model.rows()[current.row()].key
        if key == self._selected:
            return
        self._selected = key
        if key:
            self.line_chosen.emit(key)

    def _row_entered(self) -> None:
        if self._selected:
            self.line_entered.emit(self._selected)

    # --- the small print -----------------------------------------------------

    def _update_chips(self) -> None:
        for chip, (name, _states) in zip(self.chips, FILTERS):
            chip.setText(f"\u2713 {name}" if chip.isChecked() else name)
        self.control_chip.setText(
            f"\u2713 {CONTROL_FILTER}" if self.control_chip.isChecked() else CONTROL_FILTER)

    def _update_counters(self) -> None:
        if self._session is None:
            self.counters.setText("")
            return
        counts = self._session.counts(self._kind)
        self.counters.setText("   ".join(
            f"{counts[state]} {status_words.presentation(state).word.lower()}"
            for state in (State.EDITED, State.WILL_MOVE, State.REFUSED)))
