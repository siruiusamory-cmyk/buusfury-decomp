"""The left list: the two tabs, the filter chips, the shape controls and the table.

Every row, heading, label and state comes from `session.py`, and every colour, font
and metric comes from `theme.py`. Nothing here computes a ROM value.

A row is read without colour: the state cell carries a marker shape, an icon and the
whole word, and a selected row carries the accent indicator as well as the fill. The
text column is the one that gives ground, so the status word always shows in full.
"""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractTableModel,
    QItemSelection,
    QItemSelectionModel,
    QModelIndex,
    QRect,
    QSize,
    Qt,
    Signal,
)
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
    PLACE_EVIDENCE,
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

#: Identity, then the line, then the speaker, then the state the row ends with.
COLUMN_ID, COLUMN_TEXT, COLUMN_SPEAKER, COLUMN_STATUS = range(4)

#: The room the marker geometry takes at the left of the state cell, and the room
#: the auxiliary marker takes when this image already differs from the original.
MARKER_COLUMN = 12
AUX_GLYPH_WIDTH = 16
IDENTITY_FLOOR = 64
#: The room a name needs before the whole column stops being worth showing. It
#: elides, so this is small on purpose: the full label is the cell's tooltip.
SPEAKER_FLOOR = 88
#: The status column's own floor: the marker, the badge and a word that reads.
STATUS_FLOOR = 96
#: The room the text column keeps before any other column takes any. Below this the
#: row's own words stop being readable, which is the whole point of the list.
TEXT_FLOOR = 130
SPEAKER_CEILING = 168

#: The state filters, in the order the chips appear. Control units answer a
#: different question, so that chip is not a state.
FILTERS: tuple[tuple[str, frozenset[State]], ...] = (
    ("Edited", frozenset({State.EDITED})),
    ("Will move", frozenset({State.WILL_MOVE})),
    ("Refused", frozenset({State.REFUSED})),
)
CONTROL_FILTER = "Has control code"

#: The two lists. They are never merged.
TABS: tuple[tuple[str, str], ...] = (
    ("Dialogue", RECORD),
    ("Names && bios", SLOT),  # a doubled ampersand renders as one, not a mnemonic
)

#: Every word the controls say, in one place, so the menus, the tooltips and the
#: tests agree.
VIEW_TOOLTIP = ("Lines: one row per spoken line.\n"
                "Records: one row per handle, which is what the engine reads and writes.")
ORDER_TOOLTIPS = {
    APPEARANCE: "Ordered by the first handle site that names the line. That is an address "
                "order inside the game's script pool, not a proven route order.",
    STORAGE: "Ordered by the image's own layout: the container, then the offset inside it.",
}
GROUP_TOOLTIPS = {
    UNGROUPED: "One list, in the chosen order.",
    BY_SPEAKER: "One heading per displayed speaker name, and Unknown speaker last.",
    BY_PLACE: "One heading per map whose placements reach the line's record, then one "
              "Unplaced heading for the rest. The link is " + PLACE_EVIDENCE + ".",
}
SPEAKER_TOOLTIP = ("Show only the rows whose box draws this name or this gap. The record "
                   "stores a PORTRAIT operand, never a speaker field, so this is who is "
                   "drawn and not a proven speaker.")
SPEAKER_HEADER = "Speaker (by portrait)"
ALL_SPEAKERS = "All speakers"
#: What an Unplaced heading says the row is missing, when the route reaches no map.
NO_PLACE_LINK = "no placement route reaches this line"

CLEAR_SEARCH = "Clear search"
CLEAR_FILTERS = "Clear filters"
SHOW_DIALOGUE = "Show dialogue"


def _one_of(value: object, allowed: tuple[str, ...], fallback: str) -> str:
    """A stored setting, or the default when the file holds anything else."""
    return value if value in allowed else fallback


def line_count(count: int) -> str:
    return f"{count} line" if count == 1 else f"{count} lines"


def row_count(count: int, kind: str) -> str:
    """What the list holds, in the words that list uses."""
    if kind == SLOT:
        return f"{count} name" if count == 1 else f"{count} names"
    return line_count(count)


def place_tooltip(session: Session | None) -> str:
    """The Place tooltip, with the coverage this image actually has.

    Most lines have no map, so the number is the honest part of the sentence and
    the evidence is the session's own wording rather than a retyped claim.
    """
    if session is None:
        return GROUP_TOOLTIPS[BY_PLACE]
    placed, total = session.place_coverage()
    return (f"Grouped by the map whose placements reach the line's record. {placed} of "
            f"{total} lines have one; the rest are Unplaced. The link is "
            f"{PLACE_EVIDENCE}.")


def status_width() -> int:
    """Wide enough for the longest state word, its icon and both markers."""
    shape = theme.active_metrics()
    widest = max((status_words.presentation(state).word for state in State), key=len)
    advance = QFontMetrics(theme.fonts().strong).horizontalAdvance(widest)
    frame = MARKER_COLUMN + AUX_GLYPH_WIDTH + shape.pad_xs + 4 * shape.pad_sm
    return frame + advance


class LineModel(QAbstractTableModel):
    """The rows one list shows. It answers from the session and stores no rule."""

    HEADERS = ("ID", "Text", SPEAKER_HEADER, "Status")

    def __init__(self, session: Session | None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self._rows: tuple[Line, ...] = ()
        self._entries: tuple[Line | Group, ...] = ()

    def rows(self) -> tuple[Line, ...]:
        """The rows themselves, without the headings."""
        return self._rows

    def entries(self) -> tuple[Line | Group, ...]:
        """One heading or one row per table line, in the order the table shows them."""
        return self._entries

    def row_rows(self) -> tuple[int, ...]:
        """The table lines that hold a row, which is every line no heading occupies."""
        return tuple(index for index, entry in enumerate(self._entries)
                     if isinstance(entry, Line))

    def key_at(self, entry_row: int) -> str:
        """The line key of one table line, or nothing for a heading."""
        entry = self._entries[entry_row]
        return entry.key if isinstance(entry, Line) else ""

    def row_at(self, entry_row: int) -> Line | None:
        entry = self._entries[entry_row] if 0 <= entry_row < len(self._entries) else None
        return entry if isinstance(entry, Line) else None

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
        """A heading is a label, not a row, so it is never selected or focused."""
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
            return self._tooltip(line, column)
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

    def _tooltip(self, line: Line, column: int) -> str:
        """The cell's own tooltip: the whole text on the row, the words on the rest."""
        if column == COLUMN_TEXT:
            return line.text
        if column == COLUMN_STATUS:
            state = self._session.state(line.key)
            note = status_words.label(state)
            return f"{note}\n{status_words.auxiliary_label()}" \
                if self._session.differs_from_retail(line.key) else note
        if column == COLUMN_SPEAKER:
            return line.speaker_label
        return line.key

    @staticmethod
    def _heading(group: Group, column: int, role: int) -> object:
        """A heading's label, its row count and the reason an Unplaced row is there.

        The heading answers on every column, because the table skips a hidden column
        when it measures a row, and the first column is hidden in the line list.
        """
        if role == ROLE_HEADING:
            note = NO_PLACE_LINK if group.label == UNPLACED else ""
            return (f"{group.label} ({len(group.rows)})", note)
        return None


class LineDelegate(QStyledItemDelegate):
    """Every cell of every row, and the heading band, in one delegate.

    One delegate means one paint pass per cell: the divider, the selection fill and
    the accent indicator come from `theme`, so a row cannot be drawn two ways.
    """

    def __init__(self, applied_theme, metrics, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = applied_theme
        self._metrics = metrics
        fonts = theme.fonts()
        self._body = fonts.body
        self._mono = theme.mono_font()
        self._note_height = QFontMetrics(fonts.caption).height()

    def heading_height(self, note: bool) -> int:
        """A heading is one row, plus one more line when it has to say why."""
        return self._metrics.row_height + (self._note_height if note else 0)

    def sizeHint(self, option, index: QModelIndex) -> QSize:
        heading = index.data(ROLE_HEADING)
        if heading is not None:
            return QSize(option.rect.width(), self.heading_height(bool(heading[1])))
        return QSize(option.rect.width(), self._metrics.row_height)

    def paint(self, painter: QPainter, option, index: QModelIndex) -> None:
        heading = index.data(ROLE_HEADING)
        if heading is not None:
            self._paint_heading(painter, option, heading)
            return
        theme.paint_row_background(painter, option, self._theme)
        painter.save()
        if index.column() == COLUMN_STATUS:
            self._paint_status(painter, option, index)
        else:
            self._paint_text(painter, option, index)
        theme.paint_divider(painter, option.rect, self._theme)
        state = QStyle.StateFlag
        if option.state & state.State_Selected and option.state & state.State_HasFocus:
            theme.paint_focus_edge(painter, option.rect, self._theme)
        painter.restore()

    def _paint_text(self, painter: QPainter, option, index: QModelIndex) -> None:
        column = index.column()
        painter.setFont(self._mono if column == COLUMN_ID else self._body)
        ink = index.data(Qt.ItemDataRole.ForegroundRole)
        painter.setPen(ink if ink is not None
                       else theme.color(self._theme, "text_primary"))
        rect = option.rect.adjusted(self._metrics.pad_lg, 0, -self._metrics.pad_md, 0)
        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         painter.fontMetrics().elidedText(
                             text, Qt.TextElideMode.ElideRight, max(0, rect.width())))

    def _paint_status(self, painter: QPainter, option, index: QModelIndex) -> None:
        state = index.data(ROLE_STATE)
        if state is None:
            return
        entry = status_words.presentation(state)
        rect = option.rect
        theme.paint_marker(painter, rect, entry.marker,
                           theme.state_marker(self._theme, state))
        left = rect.left() + MARKER_COLUMN
        if index.data(ROLE_DIFFERS):
            # The owning decision puts the auxiliary marker "before" the state, not in
            # a column of its own, so it is drawn inside this cell.
            glyph = QRect(left, rect.top(), AUX_GLYPH_WIDTH, rect.height())
            painter.setFont(self._body)
            painter.setPen(theme.color(self._theme, "text_secondary"))
            painter.drawText(glyph, Qt.AlignmentFlag.AlignCenter, status_words.AUXILIARY.glyph)
            left = glyph.right() + self._metrics.pad_xs
        fill, ink = theme.state_colors(self._theme, state)
        badge = QRect(left, rect.top() + self._metrics.pad_xs,
                      max(0, rect.right() - left - self._metrics.pad_sm),
                      max(0, rect.height() - self._metrics.pad_xs * 2))
        theme.paint_badge(painter, badge, fill, ink, entry.icon, entry.word)

    def _paint_heading(self, painter: QPainter, option, heading) -> None:
        label, note = heading
        fonts = theme.fonts()
        painter.save()
        painter.fillRect(option.rect, theme.color(self._theme, "surface_raised"))
        rect = option.rect.adjusted(self._metrics.pad_lg, self._metrics.pad_md,
                                    -self._metrics.pad_md, -self._metrics.pad_xs)
        if note:
            rect.setHeight(max(0, rect.height() - self._note_height))
        painter.setFont(fonts.strong)
        painter.setPen(theme.color(self._theme, "text_primary"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         painter.fontMetrics().elidedText(
                             str(label), Qt.TextElideMode.ElideRight, max(0, rect.width())))
        if note:
            below = QRect(rect.left(), rect.bottom() + 1, rect.width(), self._note_height)
            painter.setFont(fonts.caption)
            painter.setPen(theme.color(self._theme, "text_secondary"))
            painter.drawText(below, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                             painter.fontMetrics().elidedText(
                                 str(note), Qt.TextElideMode.ElideRight,
                                 max(0, below.width())))
        theme.paint_divider(painter, option.rect, self._theme)
        painter.restore()


class LineTable(QTableView):
    """The one table. Enter opens the row, Home and End the row ends."""

    entered = Signal()

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.entered.emit()
            return
        # A table's own Home and End move between columns; this list is one column of
        # prose, so they move to the first and last row the design note names.
        if key in (Qt.Key.Key_Home, Qt.Key.Key_End) \
                and event.modifiers() == Qt.KeyboardModifier.NoModifier:
            self._jump_to_end(first=key == Qt.Key.Key_Home)
            return
        super().keyPressEvent(event)

    def cursor_column(self) -> int:
        """A current cell in a hidden column cannot move, so name a visible one."""
        return COLUMN_ID if not self.isColumnHidden(COLUMN_ID) else COLUMN_TEXT

    def _jump_to_end(self, first: bool) -> None:
        model = self.model()
        if not isinstance(model, LineModel):
            return
        rows = model.row_rows()
        if not rows:
            return
        index = model.index(rows[0] if first else rows[-1], self.cursor_column())
        self.setCurrentIndex(index)
        self.scrollTo(index)


class LinePane(QWidget):
    """The left pane: the two tabs, the filters, the shape controls and the table."""

    line_chosen = Signal(str)
    line_entered = Signal(str)
    #: The shell owns the search field, so the pane asks for it instead of reaching
    #: into another widget: focus it, or empty it.
    search_requested = Signal()
    search_cleared = Signal()

    def __init__(self, session: Session | None, metrics, applied_theme,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self._theme = applied_theme
        self._metrics = metrics
        self._term = ""
        self._kind = RECORD
        self._selected = ""
        self._empty_action = ""
        # The window remembers the shape, the order and the grouping between runs.
        stored = settings.load()
        self._view = _one_of(stored.get("view"), (LINES, RECORDS), LINES)
        self._order = _one_of(stored.get("order"), (APPEARANCE, STORAGE), APPEARANCE)
        self._by = _one_of(stored.get("group"), (UNGROUPED, BY_SPEAKER, BY_PLACE), UNGROUPED)
        if session is not None:
            session.set_view(self._view)
            session.set_order(self._order)
        self._model = LineModel(session, self)
        self._delegate = LineDelegate(applied_theme, metrics, self)
        self.status_width = status_width()
        self.tabs = QTabBar()
        self.tabs.setExpanding(False)
        # Both lists must stay reachable at any pane width. Qt's default is to add
        # scroll arrows and push a tab out of sight, which hides a whole surface.
        self.tabs.setUsesScrollButtons(False)
        self.tabs.setElideMode(Qt.TextElideMode.ElideRight)
        self.tabs.setAccessibleName("List")
        for title, _kind in TABS:
            self.tabs.addTab(title)
        self.counters = QLabel()
        self.counters.setProperty("role", "caption")
        self.shape_box = self._combo(((LINES, "Lines"), (RECORDS, "Records")), VIEW_TOOLTIP)
        self.order_box = self._combo(((APPEARANCE, "Appearance"), (STORAGE, "Storage")),
                                     ORDER_TOOLTIPS[APPEARANCE], ORDER_TOOLTIPS)
        self.group_box = self._combo(((UNGROUPED, "None"), (BY_SPEAKER, "Speaker"),
                                      (BY_PLACE, "Place")), GROUP_TOOLTIPS[UNGROUPED],
                                     GROUP_TOOLTIPS)
        self.speaker_box = self._combo(self._speaker_pairs(), SPEAKER_TOOLTIP)
        self.speaker_box.setAccessibleName(SPEAKER_HEADER)
        self.speaker_caption = QLabel(SPEAKER_HEADER)
        self.speaker_caption.setProperty("role", "caption")
        self.chips = [self._chip(name) for name, _states in FILTERS]
        self.control_chip = self._chip(CONTROL_FILTER)
        self.table = LineTable()
        self.empty_label = QLabel()
        self.empty_label.setWordWrap(True)
        self.empty_label.setProperty("role", "caption")
        self.empty_action = QPushButton()
        self.empty_state = QWidget()
        self._build(metrics)
        self.tabs.currentChanged.connect(self._tab_changed)
        self.shape_box.currentIndexChanged.connect(self._view_changed)
        self.order_box.currentIndexChanged.connect(self._order_changed)
        self.group_box.currentIndexChanged.connect(self._group_changed)
        self.speaker_box.currentIndexChanged.connect(self._speaker_changed)
        self.empty_action.clicked.connect(self._fix_empty)
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
        """All speakers, then the unknown count, then every name the session resolved.

        The control has to reach every speaker again, so the list leads with the one
        that filters nothing.
        """
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
        chip.setMinimumHeight(self._metrics.chip_height)
        chip.toggled.connect(self.refresh)
        return chip

    def _build(self, metrics) -> None:
        self.table.setModel(self._model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setItemDelegate(self._delegate)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(metrics.row_height)
        header = self.table.horizontalHeader()
        header.setFont(theme.fonts().label)
        header.setFixedHeight(metrics.header_height)
        header.setTextElideMode(Qt.TextElideMode.ElideRight)
        for column in (COLUMN_ID, COLUMN_SPEAKER, COLUMN_STATUS):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(COLUMN_TEXT, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(COLUMN_ID, IDENTITY_FLOOR)
        self.table.setColumnWidth(COLUMN_SPEAKER, self._speaker_width())
        self.table.setColumnWidth(COLUMN_STATUS, self.status_width)
        self.table.selectionModel().currentRowChanged.connect(self._row_changed)
        self.table.entered.connect(self._row_entered)
        self.tabs.setFixedHeight(metrics.tab_height)
        self.shape_box.setCurrentIndex(self.shape_box.findData(self._view))
        self.order_box.setCurrentIndex(self.order_box.findData(self._order))
        self.group_box.setCurrentIndex(self.group_box.findData(self._by))
        tab_row = QHBoxLayout()
        tab_row.setSpacing(metrics.gap)
        tab_row.addWidget(self.tabs)
        tab_row.addWidget(self.counters)
        tab_row.addStretch(1)
        chips_row = QHBoxLayout()
        chips_row.setSpacing(metrics.gap)
        for chip in [*self.chips, self.control_chip]:
            chips_row.addWidget(chip)
        chips_row.addStretch(1)
        shape_row = QHBoxLayout()
        shape_row.setSpacing(metrics.gap)
        for box in (self.shape_box, self.order_box, self.group_box):
            shape_row.addWidget(box)
        shape_row.addStretch(1)
        speaker_row = QHBoxLayout()
        speaker_row.setSpacing(metrics.gap)
        speaker_row.addWidget(self.speaker_caption)
        speaker_row.addWidget(self.speaker_box, 1)
        empty_row = QHBoxLayout(self.empty_state)
        empty_row.setContentsMargins(0, 0, 0, 0)
        empty_row.setSpacing(metrics.gap)
        empty_row.addWidget(self.empty_label, 1)
        empty_row.addWidget(self.empty_action)
        self.empty_state.setVisible(False)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(metrics.gap)
        column.addLayout(tab_row)
        column.addLayout(chips_row)
        column.addLayout(shape_row)
        column.addLayout(speaker_row)
        column.addWidget(self.empty_state)
        column.addWidget(self.table, 1)

    def _speaker_width(self) -> int:
        """Wide enough for the gap words, from the font, capped for a narrow pane."""
        metrics = QFontMetrics(self.table.font())
        widest = max([UNKNOWN_SPEAKER, *(self._session.speaker_counts() if self._session
                                         else {})], key=len)
        return min(SPEAKER_CEILING,
                   max(SPEAKER_FLOOR, metrics.horizontalAdvance(widest) + self._metrics.pad_xl))

    def _fit_columns(self) -> None:
        """Keep the text column readable, and drop the diagnostic column before it.

        Measured on the shipping font at the pane's default width: the status column
        needs about 133 px to show `BASE CHANGED` whole, the speaker column wanted
        168 px for the longest label, and those two left the text column 32 px, which
        draws as an ellipsis. Who gives ground is the design note's order: the status
        keeps its whole word, the text keeps a readable floor, the speaker elides
        because its cell carries the full label as a tooltip, and the identity column
        goes entirely, because the key is on the status bar and in the context pane.
        """
        width = self.table.viewport().width()
        if width <= 0:
            return
        wants_identity = self._id_by_view()
        fits = width >= SPEAKER_FLOOR + self.status_width + TEXT_FLOOR + IDENTITY_FLOOR
        self.table.setColumnHidden(COLUMN_ID, not wants_identity or not fits)
        identity = 0 if self.table.isColumnHidden(COLUMN_ID) \
            else self.table.columnWidth(COLUMN_ID)
        status = min(self.status_width, max(STATUS_FLOOR, width - TEXT_FLOOR))
        room = width - identity - status
        speaker = 0 if self.table.isColumnHidden(COLUMN_SPEAKER) \
            else min(self._speaker_width(), max(SPEAKER_FLOOR, room - TEXT_FLOOR))
        self.table.setColumnWidth(COLUMN_STATUS, status)
        if not self.table.isColumnHidden(COLUMN_SPEAKER):
            self.table.setColumnWidth(COLUMN_SPEAKER, speaker)

    def _id_by_view(self) -> bool:
        """Whether the current list wants an identity column at all."""
        return self._kind == SLOT or self._view == RECORDS

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._fit_columns()

    # --- what the list shows -------------------------------------------------

    def kind(self) -> str:
        """Which list is showing: the dialogue records, or the string slots."""
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

    def rows(self) -> tuple[Line, ...]:
        return self._model.rows()

    def selected(self) -> str:
        return self._selected

    def filters(self) -> tuple[frozenset[State], bool | None]:
        """The states the checked chips ask for, and whether control units are asked for."""
        states: frozenset[State] = frozenset()
        for chip, (_name, chip_states) in zip(self.chips, FILTERS):
            if chip.isChecked():
                states = states | chip_states
        return states, True if self.control_chip.isChecked() else None

    def next_tab(self) -> None:
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count())

    def focus_search(self) -> None:
        """Ask the window to put the caret in its search field."""
        self.search_requested.emit()

    def set_kind(self, kind: str) -> None:
        for index, (_title, tab_kind) in enumerate(TABS):
            if tab_kind == kind:
                self.tabs.setCurrentIndex(index)
                return

    def set_view(self, view: str) -> None:
        index = self.shape_box.findData(view)
        if index >= 0:
            self.shape_box.setCurrentIndex(index)

    def set_order(self, order: str) -> None:
        index = self.order_box.findData(order)
        if index >= 0:
            self.order_box.setCurrentIndex(index)

    def set_group(self, by: str) -> None:
        index = self.group_box.findData(by)
        if index >= 0:
            self.group_box.setCurrentIndex(index)

    def set_speaker(self, name: str | None) -> None:
        index = self.speaker_box.findData(name or "")
        if index >= 0:
            self.speaker_box.setCurrentIndex(index)

    def set_term(self, term: str) -> None:
        if term != self._term:
            self._term = term
            self.refresh()

    def clear_filters(self) -> None:
        """Uncheck every chip and the speaker filter, so a jump is not hidden."""
        for chip in [*self.chips, self.control_chip]:
            chip.setChecked(False)
        if self.speaker_box.currentIndex() != 0:
            self.speaker_box.setCurrentIndex(0)

    def refresh(self, keep: str | None = None) -> None:
        """Re-run the search and the filters, keeping one row selected when asked."""
        states, locked = self.filters()
        self._model.refresh(self._kind, self._term, states, locked, self.speaker(),
                            self._by if self._kind == RECORD else UNGROUPED)
        entries = self._model.entries()
        self.table.clearSpans()
        for entry_row, entry in enumerate(entries):
            if isinstance(entry, Group):
                # One heading spans the row, so its label and its reason read as one line.
                self.table.setSpan(entry_row, 0, 1, self._model.columnCount())
        # Which columns show, and how wide, is one decision: `_fit_columns` owns the
        # identity column, because it is a diagnostic that goes before the text does.
        self.table.setColumnHidden(COLUMN_SPEAKER, self._kind != RECORD)
        self._fit_columns()
        if any(isinstance(entry, Group) for entry in entries):
            self.table.resizeRowsToContents()
        self._sync_controls()
        self._update_tabs()
        self._update_chips()
        self._update_counters()
        self._update_empty()
        rows = self._model.rows()
        if keep:
            self._selected = keep if self.select_key(keep) else ""
        if not self.table.currentIndex().isValid() and rows:
            self.select_key(rows[0].key)

    # --- selection -----------------------------------------------------------

    def _entry_row(self, key: str) -> int | None:
        for entry_row, entry in enumerate(self._model.entries()):
            if isinstance(entry, Line) and entry.key == key:
                return entry_row
        return None

    def select_key(self, key: str) -> bool:
        """Select one row the list already holds, without re-running the search."""
        entry_row = self._entry_row(key)
        if entry_row is None:
            return False
        index = self._model.index(entry_row, self.table.cursor_column())
        self.table.selectionModel().setCurrentIndex(
            index, QItemSelectionModel.SelectionFlag.ClearAndSelect
            | QItemSelectionModel.SelectionFlag.Rows)
        self.table.scrollTo(index)
        return True

    def select_first(self, keys) -> bool:
        """Select the first of ``keys`` this list holds, if it holds any."""
        for key in keys:
            if self.select_key(key):
                return True
        return False

    def select_rows(self, keys) -> int:
        """Select every one of ``keys`` this list holds, and say how many that was."""
        entry_rows = [row for row in (self._entry_row(key) for key in keys) if row is not None]
        if not entry_rows:
            return 0
        last = self._model.columnCount() - 1
        selection = QItemSelection()
        for entry_row in entry_rows:
            selection.select(self._model.index(entry_row, 0),
                             self._model.index(entry_row, last))
        self.table.selectionModel().select(selection,
                                           QItemSelectionModel.SelectionFlag.ClearAndSelect)
        self.table.setCurrentIndex(self._model.index(entry_rows[0], self.table.cursor_column()))
        return len(entry_rows)

    # --- the controls --------------------------------------------------------

    def _sync_controls(self) -> None:
        """The dialogue-only controls answer nothing in the Names and bios list."""
        dialogue = self._session is not None and self._kind == RECORD
        for box in (self.shape_box, self.speaker_box, self.group_box):
            box.setEnabled(dialogue)
        self.order_box.setEnabled(self._session is not None)
        self.group_box.setItemData(self.group_box.findData(BY_PLACE),
                                   place_tooltip(self._session), Qt.ItemDataRole.ToolTipRole)

    def _tab_changed(self, index: int) -> None:
        self._kind = TABS[index][1]
        self._selected = ""
        self.table.setCurrentIndex(QModelIndex())
        self.refresh()

    def _view_changed(self, _index: int) -> None:
        self._view = self.shape_box.currentData()
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

    # --- the empty state -----------------------------------------------------

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
        self.empty_action.setText(action)
        self.empty_action.setVisible(bool(action))
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
            self.set_speaker(None)

    # --- the small print -----------------------------------------------------

    def _update_tabs(self) -> None:
        """The tab names only, with each list's count beside them on the counters line.

        Measured at the pane's default width: `Dialogue (3024)` and `Names && bios
        (1534)` together needed more than the pane had, so Qt elided the counts away
        and neither list said how much it held. The count belongs beside the tab,
        which is where the counters line is.
        """
        for index, (title, kind) in enumerate(TABS):
            total = 0 if self._session is None else self._session.total(kind)
            self.tabs.setTabText(index, title)
            self.tabs.setTabToolTip(index, row_count(total, kind))

    def _update_chips(self) -> None:
        """A checked chip carries the check glyph, so the state reads without the fill."""
        for chip, (name, _states) in zip(self.chips, FILTERS):
            chip.setText(f"\u2713 {name}" if chip.isChecked() else name)
        self.control_chip.setText(
            f"\u2713 {CONTROL_FILTER}" if self.control_chip.isChecked() else CONTROL_FILTER)

    def _update_counters(self) -> None:
        """The three state counts, which are the actionable numbers.

        Measured at the pane's default width: this line plus the two tab names
        together want 399 px inside 350, so one of the two elides. A list's own total
        is on its tab tooltip instead, which leaves both names whole and the counts
        readable.
        """
        if self._session is None:
            self.counters.setText("")
            return
        counts = self._session.counts(self._kind)
        self.counters.setText("   ".join(
            f"{counts[state]} {status_words.presentation(state).word.lower()}"
            for state in (State.EDITED, State.WILL_MOVE, State.REFUSED)))
