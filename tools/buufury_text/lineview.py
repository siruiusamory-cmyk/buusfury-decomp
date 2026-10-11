"""The left list: the shape, order and grouping controls, the table and its state cells.

The rows are whatever the session leaves after the search term, the tab, the filter
toggles, the speaker filter and the grouping. Every state is drawn as a marker shape,
an icon and the full word, so a reader who cannot separate the hues still reads the
row. Nothing here computes a ROM value: the shape, the order, the grouping, the
speaker label and the share all come from the session.
"""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QRect, Qt, Signal
from PySide6.QtGui import QFontMetrics, QPainter
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QTableView,
    QTabBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import settings
from . import status as status_words
from . import theme
from .session import (
    APPEARANCE,
    BY_PLACE,
    BY_SPEAKER,
    LINES,
    RECORDS,
    RECORD,
    SLOT,
    STORAGE,
    UNGROUPED,
    UNKNOWN_SPEAKER,
    UNPLACED,
    Group,
    Line,
    Session,
    State,
)

#: How a delegate finds the state, the row and the heading without rebuilding a Line.
ROLE_STATE = Qt.ItemDataRole.UserRole + 1
ROLE_LINE = Qt.ItemDataRole.UserRole + 2
ROLE_HEADING = Qt.ItemDataRole.UserRole + 3
#: Whether this image already differs from the original game, for the state cell.
ROLE_DIFFERS = Qt.ItemDataRole.UserRole + 4

IDENTITY_WIDTH = 54
STATUS_WIDTH = 116
#: The narrowest the speaker column may be; its real width follows the font.
SPEAKER_FLOOR = 96
MARKER_COLUMN = 7
#: The width the auxiliary marker takes inside the state cell when it applies.
AUX_GLYPH_WIDTH = 16

COLUMN_ID, COLUMN_TEXT, COLUMN_SPEAKER, COLUMN_STATUS = range(4)

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

#: Every word the controls say, in one place, so the menu, the tooltips and a test agree.
VIEW_TOOLTIP = ("Lines: one row per spoken line.\n"
                "Records: one row per handle, which is what the engine reads and writes.")
ORDER_TOOLTIPS = {
    APPEARANCE: "Ordered by the first handle site that names the line, which is an address "
                "order inside the game's script pool, not a proven route order.",
    STORAGE: "Ordered by the image's own layout: the container, then the offset inside it.",
}
GROUP_TOOLTIPS = {
    UNGROUPED: "One list, in the chosen order.",
    BY_SPEAKER: "One heading per displayed speaker name, and Unknown speaker last.",
    BY_PLACE: "No proven map or chapter link exists in this image, so every row falls in "
              "one group named Unplaced.",
}
SPEAKER_TOOLTIP = ("Show only the rows whose box draws this name or this gap. The record "
                   "stores a PORTRAIT operand, never a speaker field, so this is who is "
                   "drawn and not a proven speaker.")
SPEAKER_HEADER = "Speaker (by portrait)"
ALL_SPEAKERS = "All speakers"
NO_PLACE_LINK = "no proven map or chapter link exists in this image"

CLEAR_SEARCH = "Clear search"
CLEAR_FILTERS = "Clear filters"
SHOW_DIALOGUE = "Show dialogue"


def _one_of(value: object, allowed: tuple[str, ...], fallback: str) -> str:
    """A stored setting, or the default when the file holds anything else."""
    return value if value in allowed else fallback


def line_count(count: int) -> str:
    return f"{count} line" if count == 1 else f"{count} lines"


class LineModel(QAbstractTableModel):
    """The rows one list shows. It answers from the session and stores no rule."""

    HEADERS = ("ID", "Text", SPEAKER_HEADER, "Status")

    def __init__(self, session: Session | None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self._rows: tuple[Line, ...] = ()
        self._entries: tuple[Line | Group, ...] = ()

    def rows(self) -> tuple[Line, ...]:
        return self._rows

    def entries(self) -> tuple[Line | Group, ...]:
        """One heading or one row per table line, in the order the table shows them."""
        return self._entries

    def key_at(self, entry_row: int) -> str:
        """The line key of one table line, or nothing for a heading."""
        entry = self._entries[entry_row]
        return entry.key if isinstance(entry, Line) else ""

    def refresh(self, kind: str, term: str = "", states: frozenset[State] = frozenset(),
                locked: bool | None = None, speaker: str | None = None,
                by: str = UNGROUPED) -> None:
        self.beginResetModel()
        session = self._session
        found = () if session is None else session.matching(
            term, kind=kind, states=states, locked=locked, speaker=speaker)
        # The grouping sees the rows the filters left, so no heading hides an excluded row.
        groups = () if session is None else session.grouped(by=by, rows=found)
        entries: list[Line | Group] = []
        for group in groups:
            if group.label:
                entries.append(group)
            entries.extend(group.rows)
        self._rows = tuple(found)
        self._entries = tuple(entries)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._entries)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole) -> object:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.HEADERS[section]
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """A heading is a label, not a row, so it is never selectable."""
        if index.isValid() and isinstance(self._entries[index.row()], Group):
            return Qt.ItemFlag.NoItemFlags
        return super().flags(index)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object:
        if not index.isValid() or self._session is None:
            return None
        entry = self._entries[index.row()]
        column = index.column()
        if isinstance(entry, Group):
            return self._heading(entry, column, role)
        line = entry
        if role == ROLE_LINE:
            return line
        if role == ROLE_STATE:
            return self._session.state(line.key)
        if role == ROLE_DIFFERS:
            return bool(self._session.differs_from_retail(line.key))
        if role == Qt.ItemDataRole.ToolTipRole:
            if column == COLUMN_STATUS:
                if self._session.differs_from_retail(line.key):
                    return (f"{status_words.label(self._session.state(line.key))}\n"
                            f"{status_words.auxiliary_label()}")
                return status_words.label(self._session.state(line.key))
            if column == COLUMN_SPEAKER:
                return line.speaker_label
            return line.key
        if role == Qt.ItemDataRole.FontRole and column == COLUMN_ID:
            return theme.mono_font()
        if role == Qt.ItemDataRole.ForegroundRole and column == COLUMN_SPEAKER \
                and not line.speaker:
            # The absence is carried by the word and by brightness, never by a hue.
            return theme.color(theme.active_theme(), "text_secondary")
        if role == Qt.ItemDataRole.DisplayRole:
            if column == COLUMN_ID:
                return line.key
            if column == COLUMN_TEXT:
                return line.text
            if column == COLUMN_SPEAKER:
                return line.speaker_label
            return ""
        return None

    @staticmethod
    def _heading(group: Group, column: int, role: int) -> object:
        """A heading's label, its row count and the note a group with no link carries."""
        if role == ROLE_HEADING and column == COLUMN_ID:
            note = NO_PLACE_LINK if group.label == UNPLACED else ""
            return (f"{group.label} ({len(group.rows)})", note)
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
        left = option.rect.left() + MARKER_COLUMN
        if index.data(ROLE_DIFFERS):
            # The auxiliary marker belongs with the state, as the owning decision
            # document puts it: it "appears before it", not in a column of its own.
            glyph_rect = QRect(left, option.rect.top(), AUX_GLYPH_WIDTH, option.rect.height())
            painter.setPen(theme.color(self._theme, "text_secondary"))
            painter.drawText(glyph_rect, Qt.AlignmentFlag.AlignCenter,
                             status_words.AUXILIARY.glyph)
            painter.setPen(Qt.PenStyle.NoPen)
            left = glyph_rect.right() + 2
        badge = QRect(left, option.rect.top() + 2,
                      max(0, option.rect.right() - left - 4), option.rect.height() - 4)
        painter.setBrush(fill)
        painter.drawRoundedRect(badge, 3, 3)
        icon_rect = QRect(badge.left() + 4, badge.top() + (badge.height() - 16) // 2, 16, 16)
        theme.icon(word.icon, ink.name()).paint(painter, icon_rect)
        text_rect = QRect(icon_rect.right() + 4, badge.top(),
                          max(0, badge.right() - icon_rect.right() - 4), badge.height())
        painter.setPen(ink)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         painter.fontMetrics().elidedText(word.word, Qt.TextElideMode.ElideRight,
                                                          text_rect.width()))
        painter.restore()


class HeadingDelegate(QStyledItemDelegate):
    """One group heading: a bold label and its muted note, on a raised row."""

    def __init__(self, theme_, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme_

    def paint(self, painter: QPainter, option, index: QModelIndex) -> None:
        heading = index.data(ROLE_HEADING)
        if heading is None:
            super().paint(painter, option, index)
            return
        label, note = heading
        painter.save()
        painter.fillRect(option.rect, theme.color(self._theme, "surface_raised"))
        rect = option.rect.adjusted(6, 0, -6, 0)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(theme.color(self._theme, "text_primary"))
        label = painter.fontMetrics().elidedText(label, Qt.TextElideMode.ElideRight, rect.width())
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label)
        if note:
            font.setBold(False)
            painter.setFont(font)
            painter.setPen(theme.color(self._theme, "text_secondary"))
            left = rect.left() + painter.fontMetrics().horizontalAdvance(label) + 12
            wide = max(0, rect.right() - left)
            painter.drawText(QRect(left, rect.top(), wide, rect.height()),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             painter.fontMetrics().elidedText(
                                 note, Qt.TextElideMode.ElideRight, wide))
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
    """The left pane: the two system tabs, the controls, the toggles and the table."""

    line_chosen = Signal(str)
    line_entered = Signal(str)
    search_cleared = Signal()

    def __init__(self, session: Session | None, metrics, theme_,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self._theme = theme_
        self._metrics = metrics
        self._term = ""
        self._kind = RECORD
        self._selected = ""
        self._empty_action = ""
        self._chip_height = metrics.chip_height
        # The window remembers the shape, the order and the grouping between runs.
        stored = settings.load()
        self._view = _one_of(stored.get("view"), (LINES, RECORDS), LINES)
        self._order = _one_of(stored.get("order"), (APPEARANCE, STORAGE), APPEARANCE)
        self._by = _one_of(stored.get("group"), (UNGROUPED, BY_SPEAKER, BY_PLACE), UNGROUPED)
        if session is not None:
            session.set_view(self._view)
            session.set_order(self._order)
        self._model = LineModel(session, self)
        self.tabs = QTabBar()
        self.tabs.setExpanding(False)
        for title, _kind in TABS:
            self.tabs.addTab(title)
        self.counters = QLabel()
        self.view_box = self._combo(((LINES, "Lines"), (RECORDS, "Records")), VIEW_TOOLTIP,
                                    {LINES: VIEW_TOOLTIP, RECORDS: VIEW_TOOLTIP})
        self.order_box = self._combo(((APPEARANCE, "Appearance"), (STORAGE, "Storage")),
                                     ORDER_TOOLTIPS[APPEARANCE], ORDER_TOOLTIPS)
        self.group_box = self._combo(((UNGROUPED, "None"), (BY_SPEAKER, "Speaker"),
                                      (BY_PLACE, "Place")), GROUP_TOOLTIPS[UNGROUPED],
                                     GROUP_TOOLTIPS)
        self.speaker_box = self._combo(self._speaker_pairs(), SPEAKER_TOOLTIP)
        self.speaker_box.setAccessibleName(SPEAKER_HEADER)
        self.speaker_caption = QLabel(SPEAKER_HEADER)
        self.speaker_caption.setProperty("role", "hint")
        self.chips = [self._chip(name) for name, _states in FILTERS]
        self.control_chip = self._chip(CONTROL_FILTER)
        self.table = LineTable()
        self.empty_label = QLabel()
        self.empty_label.setWordWrap(True)
        self.empty_label.setProperty("role", "hint")
        self.empty_button = QPushButton()
        self.empty_state = QWidget()
        self._build(metrics)
        self.tabs.currentChanged.connect(self._tab_changed)
        self.view_box.currentIndexChanged.connect(self._view_changed)
        self.order_box.currentIndexChanged.connect(self._order_changed)
        self.group_box.currentIndexChanged.connect(self._group_changed)
        self.speaker_box.currentIndexChanged.connect(self._speaker_changed)
        self.empty_button.clicked.connect(self._fix_empty)
        self.refresh()

    # --- construction --------------------------------------------------------

    def _combo(self, pairs, tooltip: str, item_tooltips=None) -> QComboBox:
        box = QComboBox()
        for value, label in pairs:
            box.addItem(label, value)
            if item_tooltips:
                box.setItemData(box.count() - 1, item_tooltips.get(value, ""),
                                Qt.ItemDataRole.ToolTipRole)
        box.setToolTip(tooltip)
        box.setMinimumHeight(self._metrics.field_height)
        return box

    def _speaker_pairs(self) -> list[tuple[str, str]]:
        """All speakers, then the unknown count, then every name the session resolved."""
        counts = self._session.speaker_counts() if self._session is not None else {}
        unknown = counts.get(UNKNOWN_SPEAKER, 0)
        label = UNKNOWN_SPEAKER if not unknown else f"{UNKNOWN_SPEAKER} ({line_count(unknown)})"
        pairs = [("", ALL_SPEAKERS), (UNKNOWN_SPEAKER, label)]
        pairs += [(name, name) for name in sorted(counts, key=str.casefold)
                  if name != UNKNOWN_SPEAKER]
        return pairs

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
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(metrics.row_height)
        header = self.table.horizontalHeader()
        header.setFixedHeight(metrics.header_height)
        for column in (COLUMN_ID, COLUMN_SPEAKER, COLUMN_STATUS):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(COLUMN_TEXT, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(COLUMN_ID, IDENTITY_WIDTH)
        self.table.setColumnWidth(COLUMN_SPEAKER, self._speaker_width())
        self.table.setColumnWidth(COLUMN_STATUS, STATUS_WIDTH)
        self.table.setItemDelegateForColumn(COLUMN_ID, HeadingDelegate(self._theme, self.table))
        self.table.setItemDelegateForColumn(COLUMN_STATUS, StatusDelegate(self._theme, self.table))
        self.table.selectionModel().currentRowChanged.connect(self._row_changed)
        self.table.entered.connect(self._row_entered)
        self.tabs.setFixedHeight(metrics.row_height)
        self.view_box.setCurrentIndex(self.view_box.findData(self._view))
        self.order_box.setCurrentIndex(self.order_box.findData(self._order))
        self.group_box.setCurrentIndex(self.group_box.findData(self._by))
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(metrics.gap)
        toggle_row.addWidget(self.tabs)
        toggle_row.addWidget(self.counters)
        toggle_row.addStretch(1)
        shape_row = QHBoxLayout()
        shape_row.setSpacing(metrics.gap)
        for box in (self.view_box, self.order_box, self.group_box):
            shape_row.addWidget(box)
        shape_row.addStretch(1)
        chips_row = QHBoxLayout()
        chips_row.setSpacing(metrics.gap)
        for chip in [*self.chips, self.control_chip]:
            chips_row.addWidget(chip)
        chips_row.addStretch(1)
        speaker_row = QHBoxLayout()
        speaker_row.setSpacing(metrics.gap)
        speaker_row.addWidget(self.speaker_caption)
        speaker_row.addWidget(self.speaker_box, 1)
        empty_row = QHBoxLayout(self.empty_state)
        empty_row.setContentsMargins(0, 0, 0, 0)
        empty_row.setSpacing(metrics.gap)
        empty_row.addWidget(self.empty_label, 1)
        empty_row.addWidget(self.empty_button)
        self.empty_state.setVisible(False)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(metrics.gap)
        column.addLayout(toggle_row)
        column.addLayout(shape_row)
        column.addLayout(chips_row)
        column.addLayout(speaker_row)
        column.addWidget(self.empty_state)
        column.addWidget(self.table, 1)

    def _speaker_width(self) -> int:
        """Wide enough for the unknown label, from the font, capped for a narrow pane.

        The text column is the one that gives ground, and the cell elides rather than
        pushing the status cell out of the row.
        """
        metrics = QFontMetrics(self.table.font())
        return min(128, max(SPEAKER_FLOOR, metrics.horizontalAdvance(UNKNOWN_SPEAKER) + 16))

    # --- what the list shows -------------------------------------------------

    def kind(self) -> str:
        return self._kind

    def view(self) -> str:
        return self._view

    def order(self) -> str:
        return self._order

    def group(self) -> str:
        return self._by

    def speaker(self) -> str | None:
        """The selected speaker name, or None for every speaker."""
        return self.speaker_box.currentData() or None

    def next_tab(self) -> None:
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count())

    def set_kind(self, kind: str) -> None:
        for index, (_title, tab_kind) in enumerate(TABS):
            if tab_kind == kind:
                self.tabs.setCurrentIndex(index)
                return

    def set_view(self, view: str) -> None:
        index = self.view_box.findData(view)
        if index >= 0:
            self.view_box.setCurrentIndex(index)

    def set_order(self, order: str) -> None:
        index = self.order_box.findData(order)
        if index >= 0:
            self.order_box.setCurrentIndex(index)

    def set_group(self, by: str) -> None:
        index = self.group_box.findData(by)
        if index >= 0:
            self.group_box.setCurrentIndex(index)

    def set_term(self, term: str) -> None:
        if term != self._term:
            self._term = term
            self.refresh()

    def clear_filters(self) -> None:
        """Uncheck every toggle and the speaker filter, so a jump is not hidden."""
        for chip in [*self.chips, self.control_chip]:
            chip.setChecked(False)
        if self.speaker_box.currentIndex() != 0:
            self.speaker_box.setCurrentIndex(0)

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
        for entry_row, entry in enumerate(self._model.entries()):
            if isinstance(entry, Line) and entry.key == key:
                self.table.setCurrentIndex(self._model.index(entry_row, 0))
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
        self._model.refresh(self._kind, self._term, states, locked, self.speaker(),
                            self._by if self._kind == RECORD else UNGROUPED)
        self.table.clearSpans()
        for entry_row, entry in enumerate(self._model.entries()):
            if isinstance(entry, Group):
                # One heading spans the row, so its label and note are read as one line.
                self.table.setSpan(entry_row, 0, 1, self._model.columnCount())
        self.table.setColumnHidden(COLUMN_SPEAKER, self._kind != RECORD)
        # The identity column is a diagnostic, and the spec puts diagnostics one
        # disclosure away rather than in the primary reading position. In the line
        # list it is also the width the text column needs most: the key is on the
        # status bar and in the context pane's carrier table either way.
        self.table.setColumnHidden(
            COLUMN_ID, self._kind != SLOT and self._view == LINES)
        self._sync_controls()
        self._update_chips()
        self._update_counters()
        self._update_empty()
        if keep:
            self._selected = keep
            if not self.select_key(keep):
                self._selected = ""
        if not self.table.currentIndex().isValid() and self._model.rows():
            self.table.setCurrentIndex(self._first_row())

    def _first_row(self) -> QModelIndex:
        """The first table line that is a row, never a heading."""
        for entry_row, entry in enumerate(self._model.entries()):
            if isinstance(entry, Line):
                return self._model.index(entry_row, 0)
        return QModelIndex()

    def _sync_controls(self) -> None:
        """The dialogue-only controls answer nothing in the Names and bios list."""
        dialogue = self._session is not None and self._kind == RECORD
        for box in (self.view_box, self.speaker_box, self.group_box):
            box.setEnabled(dialogue)
        self.order_box.setEnabled(self._session is not None)

    # --- signals out ---------------------------------------------------------

    def _tab_changed(self, index: int) -> None:
        self._kind = TABS[index][1]
        self._selected = ""
        self.table.setCurrentIndex(QModelIndex())
        self.refresh()

    def _view_changed(self, _index: int) -> None:
        self._view = self.view_box.currentData()
        if self._session is not None:
            self._session.set_view(self._view)
        settings.save({"view": self._view})
        self.refresh(self._selected or None)

    def _order_changed(self, _index: int) -> None:
        self._order = self.order_box.currentData()
        if self._session is not None:
            self._session.set_order(self._order)
        settings.save({"order": self._order})
        self.refresh(self._selected or None)

    def _group_changed(self, _index: int) -> None:
        self._by = self.group_box.currentData()
        settings.save({"group": self._by})
        self.refresh(self._selected or None)

    def _speaker_changed(self, _index: int) -> None:
        self.refresh(self._selected or None)

    def _row_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        key = "" if not current.isValid() else self._model.key_at(current.row())
        if key == self._selected:
            return
        self._selected = key
        if key:
            self.line_chosen.emit(key)

    def _row_entered(self) -> None:
        if self._selected:
            self.line_entered.emit(self._selected)

    # --- the small print -----------------------------------------------------

    def _empty_state(self) -> tuple[str, str]:
        """What to say above an empty table, and the one action that fixes it.

        A term or a filter the reader set is fixable, so it gets a button. A gap in
        the image is labelled and gets none: a button there would be a lie.
        """
        name = "line" if self._kind == RECORD else "name or bio row"
        if self._kind == SLOT and self._term and \
                self._session.matching(self._term, kind=RECORD):
            # The term is not wrong, it is on the other list.
            return (f'No {name} matches "{self._term}". The dialogue list does have '
                    "matches for it.", SHOW_DIALOGUE)
        if self._term:
            return (f'No {name} matches "{self._term}". Clear the search to see the list '
                    "again.", CLEAR_SEARCH)
        if self._kind == RECORD and self.speaker() is not None:
            return (f"No line in this image is spoken by {self.speaker()}. Choose "
                    f"{ALL_SPEAKERS} to see every line.", ALL_SPEAKERS)
        if any(chip.isChecked() for chip in [*self.chips, self.control_chip]):
            return ("The checked filters hide every row here. Clear them to see the list "
                    "again.", CLEAR_FILTERS)
        return (f"This image carries no {name}.", "")

    def _update_empty(self) -> None:
        note, action = "", ""
        if self._session is not None and not self._model.rows():
            note, action = self._empty_state()
        self._empty_action = action
        self.empty_label.setText(note)
        self.empty_button.setText(action)
        self.empty_button.setVisible(bool(action))
        self.empty_state.setVisible(bool(note))

    def _fix_empty(self) -> None:
        action = self._empty_action
        if action == CLEAR_SEARCH:
            self.set_term("")
            self.search_cleared.emit()
        elif action == CLEAR_FILTERS:
            self.clear_filters()
        elif action == SHOW_DIALOGUE:
            self.set_kind(RECORD)
        elif action == ALL_SPEAKERS:
            self.speaker_box.setCurrentIndex(0)

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
