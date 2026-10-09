"""The ROM destination's page: two views, one selection, one Go to address.

This page decides nothing about the image. Every classification, owner, extent,
change and search hit it shows is an answer from `romsurface`, and the page
renders it. That is what keeps one selection shared by both views and one
`Go to address` serving both: the selection is a file offset this widget holds,
and both views are rendered from it.

The ranges view lists the atlas's own coverage spans with the owners the range
index reports; the bytes view shows sixteen bytes per row with the canonical
bytes beside the current ones, the address and the file offset in the gutter and
the changed positions named. `Open bytes` is enabled only from an answer that
carries a proven extent, and a disabled one states the reason it was given.

No ROM semantics live here: no address arithmetic, no offset literal, no record
stride. `Go to address` calls the model's parser, and a write goes through the
shell's one confirmed raw-write path.
"""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from . import theme
from .romsurface import (
    BYTE_VIEW_ROWS,
    DEFAULT_SEARCH_HITS,
    SurfaceError,
    byte_rows,
    load_index,
    open_bytes,
    ownership,
    parse_pattern,
    parse_target,
    range_rows,
    search_bytes,
    selection_extent,
    surface_for,
    summary,
)
from .session import Session

#: The view names, in the order the switch offers them. The third appears only
#: after a search, so a view the user has not asked for is never an option.
RANGES_VIEW = "Ranges"
BYTES_VIEW = "Bytes"
SEARCH_VIEW = "Find results"

_RANGE_HEADERS = ("Address", "Size", "Classification", "Confidence", "Owner", "Preview")
_BYTE_HEADERS = (
    "Address",
    "File offset",
    "Bytes",
    "Canonical",
    "Changed",
    "ASCII",
)
_SEARCH_HEADERS = ("Address", "File offset", "Classification", "Confidence", "Owner")


class _RowsModel(QAbstractTableModel):
    """A read-only table over strings the page has already rendered.

    A model rather than one widget per row: the range view of the accepted image
    is 7,833 rows, and a widget each is the pattern `docs/desktop-ui.md` forbids.
    """

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


class RomPage(QWidget):
    """The ROM destination's centre page."""

    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("romPage")
        self._session = session
        #: The shell's one confirmed raw-write path, so a write from this page is
        #: the same write as a write from anywhere else.
        self._write_handler = None
        #: The range index and the one attempt to load it. It is expensive and
        #: immutable per image, so it is loaded once and never per repaint.
        self._index = None
        self._index_problem = ""
        self._index_attempted = False
        self._index_for = None
        self._surface = None
        self._mode = RANGES_VIEW
        self._range_rows: tuple = ()
        self._byte_rows: tuple = ()
        self._hits: tuple = ()
        #: The one selection both views share, as a file offset.
        self._caret = 0
        #: What the caret is, and the extent something has proven for it.
        self._what = "the ROM surface"
        self._extent = None

        self._views = QComboBox()
        self._views.setObjectName("romViewSwitch")
        self._views.addItems([RANGES_VIEW, BYTES_VIEW])
        self._views.setAccessibleName("ROM view")

        self._goto = QLineEdit()
        self._goto.setObjectName("romGoToAddress")
        self._goto.setPlaceholderText("image address or file offset")
        self._goto.setAccessibleName("Go to address")
        self._goto_button = QPushButton("Go")

        self._find = QLineEdit()
        self._find.setObjectName("romFindBytes")
        self._find.setPlaceholderText("hex bytes, for example DE AD BE EF")
        self._find.setAccessibleName("Find bytes")
        self._find_button = QPushButton("Find")

        self._model = _RowsModel(self)
        self._table = QTableView()
        self._table.setObjectName("romTable")
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.setFont(theme.mono_font())
        self._table.verticalHeader().setVisible(False)
        self._table.setWordWrap(False)

        self._empty = QLabel(
            "Open a ROM image to see its ranges, its ownership and its bytes."
        )
        self._empty.setProperty("dbzRole", "hint")
        self._empty.setWordWrap(True)
        self._empty.setObjectName("romEmptyState")

        self._summary = QLabel()
        self._summary.setProperty("dbzRole", "hint")
        self._summary.setWordWrap(True)

        self._strip = QLabel()
        self._strip.setProperty("dbzRole", "technical")
        self._strip.setWordWrap(True)
        self._strip.setTextInteractionFlags(
            self._strip.textInteractionFlags()
            | Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._strip.setText("Nothing is selected.")

        self._open_button = QPushButton("Open bytes")
        self._write_hex = QLineEdit()
        self._write_hex.setMaximumWidth(160)
        self._write_hex.setPlaceholderText("new bytes (hex)")
        self._write_hex.setAccessibleName("New bytes for the raw write")
        self._write_button = QPushButton("Write")
        self._message = QLabel()
        self._message.setProperty("dbzRole", "hint")
        self._message.setWordWrap(True)

        self._build_layout()
        self._connect()
        self.refresh()

    # -- construction ---------------------------------------------------------

    def _build_layout(self) -> None:
        tools = QHBoxLayout()
        tools.setSpacing(theme.SPACE_SM)
        tools.addWidget(self._views)
        tools.addWidget(QLabel("Go to address:"))
        tools.addWidget(self._goto, 1)
        tools.addWidget(self._goto_button)
        tools.addSpacing(theme.SPACE_LG)
        tools.addWidget(QLabel("Find bytes:"))
        tools.addWidget(self._find, 1)
        tools.addWidget(self._find_button)

        write = QHBoxLayout()
        write.setSpacing(theme.SPACE_SM)
        write.addWidget(self._open_button)
        write.addSpacing(theme.SPACE_LG)
        write.addWidget(QLabel("Write at the selection:"))
        write.addWidget(self._write_hex)
        write.addWidget(self._write_button)
        write.addWidget(self._message, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD
        )
        layout.setSpacing(theme.SPACE_SM)
        layout.addLayout(tools)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._empty)
        layout.addWidget(self._summary)
        layout.addWidget(self._strip)
        layout.addLayout(write)

    def _connect(self) -> None:
        self._views.currentTextChanged.connect(self._on_view_changed)
        self._goto_button.clicked.connect(self._on_go)
        self._goto.returnPressed.connect(self._on_go)
        self._find_button.clicked.connect(self._on_find)
        self._find.returnPressed.connect(self._on_find)
        self._open_button.clicked.connect(self._on_open_bytes)
        self._write_button.clicked.connect(self._on_write)
        self._table.selectionModel().currentRowChanged.connect(self._on_row_changed)

    def set_write_handler(self, handler) -> None:
        """The shell's one write path: this page never writes bytes itself."""
        self._write_handler = handler

    # -- rendering ------------------------------------------------------------

    def refresh(self) -> None:
        """Re-render from the session. The shell calls this after every change."""
        self._surface = self._build_surface()
        if self._surface is None:
            self._table.setVisible(False)
            self._empty.setVisible(True)
            self._summary.setText("")
            self._strip.setText(
                "No ROM is open, so there is no address space, no owner and no byte."
            )
            self._open_button.setEnabled(False)
            self._open_button.setToolTip("Open a ROM first.")
            for widget in (
                self._views,
                self._goto,
                self._goto_button,
                self._find,
                self._find_button,
                self._write_hex,
                self._write_button,
            ):
                widget.setEnabled(False)
            return
        self._table.setVisible(True)
        self._empty.setVisible(False)
        for widget in (
            self._views,
            self._goto,
            self._goto_button,
            self._find,
            self._find_button,
            self._write_hex,
            self._write_button,
        ):
            widget.setEnabled(True)
        if not 0 <= self._caret < self._surface.image_size:
            self._caret = 0
        self._summary.setText(summary(self._surface))
        self._render()

    def _build_surface(self):
        session = self._session
        if session.base_image is None or session.profile is None:
            return None
        self._ensure_index()
        return surface_for(
            session.base_image,
            session.profile,
            session.journal,
            index=self._index,
            index_problem=self._index_problem,
        )

    def _ensure_index(self) -> None:
        """Load the range index once per image, through the SDK's own artifact."""
        if self._index_attempted and self._index_for == self._session.rom_path:
            return
        # The assembled 56 MB atlas is parsed on this thread the first time the
        # ROM destination is shown, measured at 4 s. Move it to a worker or a
        # chained QTimer drain if that wait ever lands on a user.
        self._index, self._index_problem = load_index(self._session.profile)
        self._index_attempted = True
        self._index_for = self._session.rom_path
        self._reset_search()

    def _reset_search(self) -> None:
        """Another image invalidates every hit: each one names an offset in this one."""
        self._hits = ()
        self._mode = RANGES_VIEW
        if self._views.currentText() != RANGES_VIEW:
            self._views.blockSignals(True)
            self._views.setCurrentText(RANGES_VIEW)
            self._views.blockSignals(False)

    def _render(self) -> None:
        if self._mode == BYTES_VIEW:
            self._render_bytes()
        elif self._mode == SEARCH_VIEW and self._hits:
            self._render_search()
        else:
            self._render_ranges()
        self._describe_caret()

    def _range_row_at(self, offset: int):
        return next(
            (
                row
                for row in self._range_rows
                if row.span.start.value <= offset < row.span.end
            ),
            None,
        )

    def _render_ranges(self) -> None:
        self._mode = RANGES_VIEW
        rows = range_rows(self._surface)
        self._range_rows = rows
        self._model.set_rows(
            _RANGE_HEADERS,
            tuple(
                (
                    f"0x{row.address:08X}",
                    f"0x{row.span.size:06X}",
                    row.classification,
                    row.confidence.value,
                    row.owner_text,
                    row.preview.hex(),
                )
                for row in rows
            ),
        )
        self._select_row_at(self._caret)

    def _render_bytes(self) -> None:
        self._mode = BYTES_VIEW
        rows = byte_rows(self._surface, self._caret, rows=BYTE_VIEW_ROWS)
        self._byte_rows = rows
        self._model.set_rows(
            _BYTE_HEADERS,
            tuple(
                (
                    f"0x{row.address:08X}",
                    f"0x{row.offset:06X}",
                    row.current_hex(),
                    row.canonical_hex(),
                    " ".join(f"+{position:02X}" for position in row.changed) or "-",
                    row.ascii,
                )
                for row in rows
            ),
        )
        self._select_row_at(self._caret)

    def _render_search(self) -> None:
        self._mode = SEARCH_VIEW
        self._model.set_rows(
            _SEARCH_HEADERS,
            tuple(
                (
                    f"0x{hit.address:08X}",
                    f"0x{hit.offset:06X}",
                    hit.classification or "unclassified",
                    hit.confidence.value if hit.confidence else "UNKNOWN",
                    hit.owner_text,
                )
                for hit in self._hits
            ),
        )
        if self._hits:
            self._caret = self._hits[0].offset
        self._select_row_at(self._caret)

    # -- selection ------------------------------------------------------------

    def _select_row_at(self, offset: int) -> None:
        """Point the table at the row holding `offset`, without re-entering."""
        if self._mode == BYTES_VIEW:
            index = next(
                (
                    at
                    for at, item in enumerate(self._byte_rows)
                    if item.offset <= offset < item.offset + len(item.canonical)
                ),
                None,
            )
        elif self._mode == RANGES_VIEW:
            index = next(
                (
                    at
                    for at, item in enumerate(self._range_rows)
                    if item.span.start.value <= offset < item.span.end
                ),
                None,
            )
        else:
            index = next(
                (
                    at
                    for at, item in enumerate(self._hits)
                    if item.offset == offset
                ),
                None,
            )
        if index is None:
            return
        selection = self._table.selectionModel()
        selection.blockSignals(True)
        self._table.selectRow(index)
        selection.blockSignals(False)

    def _on_row_changed(self, current: QModelIndex, previous: QModelIndex) -> None:
        if not current.isValid() or self._surface is None:
            return
        row = current.row()
        if self._mode == BYTES_VIEW:
            if row >= len(self._byte_rows):
                return
            self._caret = self._byte_rows[row].offset
        elif self._mode == RANGES_VIEW:
            if row >= len(self._range_rows):
                return
            self._caret = self._range_rows[row].span.start.value
        else:
            if row >= len(self._hits):
                return
            self._caret = self._hits[row].offset
        self._describe_caret()

    def _describe_caret(self) -> None:
        """What the selected row proves, in the model's own answers.

        A range row proves its whole coverage span; a byte row and a search hit
        prove the one byte they name. The `what` is the owner where the index
        reports one, so `Open bytes` can say what it would open without this page
        inventing a name for it.
        """
        if self._surface is None:
            return
        if self._mode == RANGES_VIEW:
            row = self._range_row_at(self._caret)
            if row is not None:
                self._what = ", ".join(row.owners) or "this range"
                self._extent = row.span
                self._show_selection()
                return
        if self._mode == SEARCH_VIEW:
            hit = next(
                (item for item in self._hits if item.offset == self._caret), None
            )
            if hit is not None:
                self._what = ", ".join(hit.owners) or "this hit"
                self._extent = selection_extent(self._surface, self._caret)
                self._show_selection()
                return
        if not 0 <= self._caret < self._surface.image_size:
            return
        self._what = "this byte"
        self._extent = selection_extent(self._surface, self._caret)
        self._show_selection()

    def _show_selection(self) -> None:
        """The ownership strip and the Open bytes state, both from the model."""
        if self._surface is None:
            return
        self._strip.setText(ownership(self._surface, self._caret).text())
        opened = open_bytes(self._surface, self._what, extent=self._extent)
        self._open_button.setEnabled(opened.available)
        self._open_button.setToolTip(opened.status())
        self._open_button.setAccessibleName(
            f"Open bytes. {opened.status()}"
        )

    # -- actions --------------------------------------------------------------

    def _on_view_changed(self, view: str) -> None:
        self._mode = view
        self._render()

    def _on_go(self) -> None:
        if self._surface is None:
            return
        try:
            target = parse_target(self._goto.text(), self._surface.image_size)
        except SurfaceError as exc:
            self._report(str(exc))
            return
        self._caret = target.file_offset
        self._message.setText(f"Go to address: {target.text()}")
        if self._views.currentText() == SEARCH_VIEW:
            # The hit list is not an address-space view, so a jump leaves it for
            # the ranges view; the two real views keep whichever one is showing.
            self._views.setCurrentText(RANGES_VIEW)
        else:
            self._render()

    def _on_find(self) -> None:
        if self._surface is None:
            return
        try:
            self._hits = search_bytes(self._surface, self._find.text())
        except SurfaceError as exc:
            self._report(str(exc))
            return
        if not self._hits:
            self._message.setText("No raw byte hit for that pattern.")
            return
        if self._views.count() == 2:
            self._views.addItem(SEARCH_VIEW)
        stopped = len(self._hits) == DEFAULT_SEARCH_HITS
        self._message.setText(
            f"{len(self._hits)} raw byte hit(s)"
            + (f", the first {DEFAULT_SEARCH_HITS} of more" if stopped else "")
            + "."
        )
        if self._views.currentText() == SEARCH_VIEW:
            self._render()
        else:
            self._views.setCurrentText(SEARCH_VIEW)

    def _on_open_bytes(self) -> None:
        """Open the proven extent: move the byte view to its first byte."""
        if self._surface is None or self._extent is None:
            return
        self._caret = self._extent.start.value
        if self._views.currentText() != BYTES_VIEW:
            self._views.setCurrentText(BYTES_VIEW)
        else:
            self._render()

    def _on_write(self) -> None:
        if self._surface is None or self._write_handler is None:
            return
        try:
            new = parse_pattern(self._write_hex.text())
        except SurfaceError as exc:
            self._report(str(exc))
            return
        atlas = self._surface.index.atlas if self._surface.index else None
        self._write_handler(self._caret, new, atlas=atlas)

    def _report(self, reason: str) -> None:
        self._message.setText(reason)
