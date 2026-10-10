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
carries a proven extent, and a disabled one states the reason it was given. A raw
write is offered only while the range index is loaded, and the page says in the
one visible place that the write it makes is saved with the project and shown in
this surface, and is applied by no build path yet.

The range index is a large artifact, so it is parsed on a worker thread: this page
never blocks its own event loop for it, and it says what it is doing while the
parse runs.

No ROM semantics live here: no address arithmetic, no offset literal, no record
stride. `Go to address` calls the model's parser, and a write goes through the
shell's one confirmed raw-write path.
"""

from __future__ import annotations

from PySide6.QtCore import (
    QModelIndex,
    QObject,
    QRunnable,
    Qt,
    QThreadPool,
    Signal,
)
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
from .inspector import InspectorContext
from .romsurface import (
    BYTE_VIEW_ROWS,
    DEFAULT_SEARCH_HITS,
    SEARCH_SCOPE,
    SurfaceError,
    byte_rows,
    declared_tables,
    load_index,
    open_bytes,
    ownership,
    parse_pattern,
    parse_target,
    range_rows,
    range_selection_context,
    search_bytes,
    selection_context,
    selection_extent,
    surface_for,
    summary,
    write_gate,
)
from .session import Session
from .tablemodel import RowsModel

#: The view names, in the order the switch offers them. The third appears only
#: after a search, so a view the user has not asked for is never an option.
RANGES_VIEW = "Ranges"
BYTES_VIEW = "Bytes"
SEARCH_VIEW = "Find results"

_RANGE_HEADERS = (
    "Address",
    "File offset",
    "Size",
    "Classification",
    "Confidence",
    "Owner",
    "Preview (bytes)",
)
_BYTE_HEADERS = (
    "Address",
    "File offset",
    "Bytes",
    "Canonical",
    "Changed",
    "ASCII",
)
_SEARCH_HEADERS = ("Address", "File offset", "Classification", "Confidence", "Owner")

#: Column widths per view, so a technical identity is not squeezed by the columns
#: that carry a fixed number of digits. `Classification` and `Owner` carry the
#: atlas's own words, which are the longest in the row and the ones a reader
#: compares; the last column takes whatever is left, and a window too narrow to
#: hold them scrolls rather than eliding the identity away.
_COLUMN_WIDTHS = {
    RANGES_VIEW: (88, 88, 76, 190, 96, 170),
    BYTES_VIEW: (88, 88, 264, 264, 88),
    SEARCH_VIEW: (88, 88, 170, 90),
}

#: Said where the user writes, because it is the one thing a write here does not
#: do: no build path reads the project's raw byte document, so the write is not
#: in any image yet and must not be described as if it were.
JOURNAL_LOCAL = (
    "A raw write is saved with the project and shown in this surface. No build "
    "path applies it to an image yet."
)

#: The destination's own exception, in the product's words: a raw address is the
#: primary label here rather than a diagnostic, which is why the image address
#: leads every row and the file offset follows it.
ADDRESS_FIRST = (
    "This surface is address-first: the image address leads and the file offset "
    "follows it."
)


class _IndexSignals(QObject):
    """The worker's one answer, delivered on the thread that owns the page.

    The request token travels with it: the parse takes seconds, an image can be
    replaced while it runs, and an answer for the previous image must never be
    installed over the current one.
    """

    finished = Signal(int, object, str)


class _IndexTask(QRunnable):
    """Parse the range index away from the UI thread.

    The atlas artifact is tens of megabytes, so the parse belongs off the event
    loop: `docs/desktop-ui.md` forbids blocking the UI thread for indexing and
    gives a 400 ms feedback budget. The result crosses back through a queued
    signal, and a failure becomes the stated reason rather than a silent thread
    death that would leave the page loading forever.

    The one failure with nobody left to tell is a parse that answers after the
    page that owns the signal source has been destroyed. That is caught here
    rather than allowed to escape: an unhandled exception on a pool thread is
    what this boundary exists to prevent, and there is no page left to state a
    reason to.
    """

    def __init__(self, profile, directory, token: int, signals) -> None:
        super().__init__()
        self.signals = signals
        self._profile = profile
        self._directory = directory
        self._token = token

    def run(self) -> None:
        try:
            index, problem = load_index(self._profile, self._directory)
        except Exception as exc:  # a worker boundary: report, never die silently
            index, problem = None, f"the range index could not be loaded: {exc}"
        try:
            self.signals.finished.emit(self._token, index, problem)
        except RuntimeError:
            # The page was destroyed while this parse ran, so the signal source
            # and the widgets that would render the answer are gone. Nothing is
            # installed and nobody is left to report to.
            pass


class RomPage(QWidget):
    """The ROM destination's centre page."""

    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("romPage")
        self._session = session
        #: The shell's one confirmed raw-write path, so a write from this page is
        #: the same write as a write from anywhere else.
        self._write_handler = None
        #: The shell's one inspector, told what this page has selected. None until
        #: the shell wires it.
        self._selection_handler = None
        #: Asked for the byte effect of the project's semantic edits. None until
        #: the shell wires the destination that owns them.
        self._pending_provider = None
        #: The range index and the one attempt to load it. It is expensive and
        #: immutable per image, so it is loaded once, on a worker, and never per
        #: repaint or per status refresh.
        self._index = None
        self._index_problem = ""
        self._index_loading = False
        self._index_attempted = False
        self._index_for = None
        #: The one token an index answer must carry to be installed: it moves
        #: every time a parse starts, so a late answer for another image cannot.
        self._index_request = 0
        #: The signal source and the running parses, both owned by the page
        #: rather than by a task: a parse can outlive the request that started
        #: it, and a worker whose signal object has been collected dies at its
        #: own emit. The parses are keyed by the token that started them and the
        #: entry is dropped when that token answers, so the map holds one entry
        #: per outstanding parse rather than one per parse ever started.
        self._index_signals = _IndexSignals(self)
        self._index_tasks: dict[int, _IndexTask] = {}
        self._pool = QThreadPool.globalInstance()
        self._surface = None
        self._mode = RANGES_VIEW
        #: The view the column widths were last set for, so a reader's own width
        #: survives a re-render and is only reset when the view changes.
        self._columns_for = None
        self._range_rows: tuple = ()
        self._byte_rows: tuple = ()
        self._hits: tuple = ()
        self._hits_truncated = False
        #: The one selection both views share, as a file offset.
        self._caret = 0
        #: True while this page is pointing the table at a row itself, so the
        #: row-change handler does not overwrite the caret it was given.
        self._selecting = False
        #: What the caret is, and the extent something has proven for it.
        self._what = "the ROM surface"
        self._extent = None

        self._views = QComboBox()
        self._views.setObjectName("romViewSwitch")
        self._views.addItems([RANGES_VIEW, BYTES_VIEW])
        self._views.setAccessibleName("ROM view")

        self._goto = QLineEdit()
        self._goto.setObjectName("romGoToAddress")
        self._goto.setPlaceholderText("address or offset")
        self._goto.setToolTip(
            "An image address (0x08xxxxxx) or a file offset (0x0xxxxx)."
        )
        self._goto.setAccessibleName("Go to address")
        self._goto_button = QPushButton("Go")

        #: The declared-table jump list: the range index's own declared spans, so
        #: a table the jump offers and a table a write is refused by are one list.
        self._jump = QComboBox()
        self._jump.setObjectName("romJumpList")
        self._jump.setAccessibleName("Jump to a declared table")

        self._find = QLineEdit()
        self._find.setObjectName("romFindBytes")
        self._find.setPlaceholderText("hex bytes")
        self._find.setToolTip(SEARCH_SCOPE)
        self._find.setAccessibleName("Find bytes")
        self._find_button = QPushButton("Find")
        self._find_button.setToolTip(SEARCH_SCOPE)

        self._model = RowsModel(self)
        self._table = QTableView()
        self._table.setObjectName("romTable")
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.setFont(theme.mono_font())
        self._table.verticalHeader().setVisible(False)
        self._table.setWordWrap(False)
        # The elide is in the middle: a truncated owner keeps its head and its
        # tail, so `function:func.08001304` never reads as `function:func.08001340`.
        self._table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        # Whatever width is left over belongs to the last column, which at a wide
        # window is the byte preview and at a narrow one is the scrollbar's.
        self._table.horizontalHeader().setStretchLastSection(True)

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
        self._write_note = QLabel(JOURNAL_LOCAL)
        self._write_note.setProperty("dbzRole", "hint")
        self._write_note.setWordWrap(True)
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

        # The jump list gets its own row rather than sharing one: a declared table
        # name is long, and at the 960x640 minimum a shared row truncated both the
        # name and the address field.
        jump = QHBoxLayout()
        jump.setSpacing(theme.SPACE_SM)
        jump.addWidget(QLabel("Jump to:"))
        jump.addWidget(self._jump, 1)
        jump.addSpacing(theme.SPACE_LG)
        jump.addWidget(QLabel("Find bytes:"))
        jump.addWidget(self._find, 1)
        jump.addWidget(self._find_button)

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
        layout.addLayout(jump)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._empty)
        layout.addWidget(self._summary)
        layout.addWidget(self._strip)
        layout.addLayout(write)
        layout.addWidget(self._write_note)

    def _connect(self) -> None:
        self._views.currentTextChanged.connect(self._on_view_changed)
        self._goto_button.clicked.connect(self._on_go)
        self._goto.returnPressed.connect(self._on_go)
        self._find_button.clicked.connect(self._on_find)
        self._find.returnPressed.connect(self._on_find)
        self._jump.activated.connect(self._on_jump)
        self._open_button.clicked.connect(self._on_open_bytes)
        self._write_button.clicked.connect(self._on_write)
        self._index_signals.finished.connect(self._index_ready)
        self._table.selectionModel().currentRowChanged.connect(self._on_row_changed)

    def set_write_handler(self, handler) -> None:
        """The shell's one write path: this page never writes bytes itself."""
        self._write_handler = handler

    def set_selection_handler(self, handler) -> None:
        """The shell's one inspector, told what this page has selected."""
        self._selection_handler = handler

    def set_pending_provider(self, provider) -> None:
        """What the project's semantic edits amount to, asked on every render.

        The destinations own those edits and their codecs; this page renders
        whatever the provider answers - the bytes it could state, and its reason
        for any it could not - so a stat edit appears here as a changed value
        without this page knowing what a stat is, and an incomplete answer is
        never shown as the image's own.
        """
        self._pending_provider = provider

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
            for widget in (self._write_hex, self._write_button):
                widget.setToolTip("Open a ROM first.")
            self._write_note.setText("Open a ROM first.")
            self._jump.setToolTip("Open a ROM first.")
            for widget in (
                self._views,
                self._goto,
                self._goto_button,
                self._find,
                self._find_button,
                self._jump,
                self._write_hex,
                self._write_button,
            ):
                widget.setEnabled(False)
            self._publish_nothing()
            return
        self._table.setVisible(True)
        self._empty.setVisible(False)
        for widget in (
            self._views,
            self._goto,
            self._goto_button,
            self._find,
            self._find_button,
        ):
            widget.setEnabled(True)
        self._refresh_write_controls()
        self._render_jump_list()
        if not 0 <= self._caret < self._surface.image_size:
            self._caret = 0
        self._summary.setText(f"{summary(self._surface)} {ADDRESS_FIRST}")
        self._render()

    def _render_jump_list(self) -> None:
        """The declared-table jump list, from the range index's own declared layer.

        One list, and it is the index's: the same spans the raw byte authority
        refuses a write against, so a table a jump offers and a table a write is
        refused by cannot disagree. No second index and no second vocabulary are
        built here - the page names what the model already holds, and a jump
        selects the atlas coverage row that contains the table's first byte.

        A jump needs rows to land on, so it is offered only while the range index
        is loaded, and it states that reason when it is not.
        """
        rows = [
            (span, owner)
            for span, owner in declared_tables(self._surface)
            # A declared table that begins past the open image has no coverage row
            # to land on, so it is not offered as a jump.
            if span.start.value < self._surface.image_size
        ]
        labels = [f"{owner} (0x{span.start.value:06X})" for span, owner in rows]
        if [self._jump.itemText(at) for at in range(self._jump.count())] != labels:
            self._jump.blockSignals(True)
            self._jump.clear()
            for (span, _owner), label in zip(rows, labels):
                self._jump.addItem(label, span.start.value)
            self._jump.blockSignals(False)
        available = bool(rows) and self._surface.index is not None
        self._jump.setEnabled(available)
        self._jump.setToolTip(
            ""
            if available
            else "A declared table is a range, so a jump needs the range index: "
            + (self._surface.index_problem or "the index is not loaded")
        )

    def _refresh_write_controls(self) -> None:
        """Render the model's raw-write gate on the two write controls.

        The same shape as `Open bytes`: a control that cannot act is disabled and
        states the reason it was given, and a disabled one cannot be clicked into
        a write the surface would have to refuse later.
        """
        gate = write_gate(self._surface)
        for widget in (self._write_hex, self._write_button):
            widget.setEnabled(gate.available)
            widget.setToolTip(gate.reason)
        self._write_button.setAccessibleName(f"Write. {gate.reason}")
        # A control that cannot act states its reason where the control is, not
        # only in the summary line at the foot of the page.
        self._write_note.setText(JOURNAL_LOCAL if gate.available else gate.reason)

    def _build_surface(self):
        session = self._session
        if session.base_image is None or session.profile is None:
            return None
        self._ensure_index()
        extra = self._pending_provider() if self._pending_provider is not None else None
        return surface_for(
            session.base_image,
            session.profile,
            session.journal,
            index=self._index,
            index_problem=self._index_problem,
            extra_pending=extra.mapping if extra is not None else None,
            pending_problem=extra.problem if extra is not None else "",
        )

    def _ensure_index(self) -> None:
        """Start the one parse of the range index for this image, on a worker.

        Nothing here blocks: the parse is tens of megabytes and the event loop
        keeps running while it happens, which is the budget `docs/desktop-ui.md`
        sets for indexing. The page renders what it has until the answer lands.
        """
        if self._index_attempted and self._index_for == self._session.rom_path:
            return
        self._index_attempted = True
        self._index_for = self._session.rom_path
        self._index_request += 1
        self._index = None
        self._index_problem = "the range index is still loading"
        self._index_loading = True
        self._reset_search()
        task = _IndexTask(
            self._session.profile, None, self._index_request, self._index_signals
        )
        self._index_tasks[self._index_request] = task
        self._pool.start(task)

    def _index_ready(self, token: int, index, problem: str) -> None:
        """The worker's answer, if it is still the answer for the open image.

        A parse that started for another image is dropped here rather than
        installed: its owners, its classification and its bytes are all claims
        about bytes that are not open any more, and accepting them would bind
        every owner the strip shows and every claimed-bytes refusal to the wrong
        evidence.

        The entry is dropped for a stale token as well as for the current one:
        the answer names which parse just finished, so that is when the page
        stops holding it.
        """
        self._index_tasks.pop(token, None)
        if token != self._index_request:
            return
        self._index = index
        self._index_problem = problem
        self._index_loading = False
        self.refresh()

    def _reset_search(self) -> None:
        """Another image invalidates every hit: each one names an offset in this one."""
        self._hits = ()
        self._hits_truncated = False
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
        self._apply_columns()
        self._describe_caret()

    def _apply_columns(self) -> None:
        """Give this view's columns their widths once, when the view changes.

        Once per view rather than once per render: a reader who widened a column
        to read a long identity keeps that width until the view changes.
        """
        if self._columns_for == self._mode:
            return
        self._columns_for = self._mode
        for column, width in enumerate(_COLUMN_WIDTHS[self._mode]):
            self._table.setColumnWidth(column, width)

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
                    f"0x{row.span.start.value:06X}",
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
        """Make the row holding `offset` the table's current row.

        The row becomes the table's current row rather than only being selected:
        the caret, the status line and the inspector all describe the current row,
        and a highlight with no current row is a row nothing is selected in. The
        caret itself is NOT moved to the row's start. `Go to address` names a
        byte, a raw write goes at the caret, and a range that covers 0x400 starts
        at 0x200: snapping the caret would silently move the write. The guard
        replaces the blocked-signal shortcut, which stopped the row from becoming
        current at all and left the inspector empty.
        """
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
        self._selecting = True
        try:
            self._table.setCurrentIndex(self._model.index(index, 0))
            self._table.selectRow(index)
        finally:
            self._selecting = False

    def _on_row_changed(self, current: QModelIndex, previous: QModelIndex) -> None:
        if self._selecting or not current.isValid() or self._surface is None:
            # A row this page pointed at is already the selection: its caret was
            # set by the caller, and `_render` describes it after this returns.
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
        inventing a name for it. The same selection is published to the shell's
        one inspector, so the highlighted row and the pane can never disagree:
        either a row is selected and the pane carries its identity, or nothing is
        highlighted and the pane says nothing is selected.
        """
        if self._surface is None:
            return
        if self._mode == RANGES_VIEW:
            row = self._range_row_at(self._caret)
            if row is not None:
                self._what = ", ".join(row.owners) or "this range"
                self._extent = row.span
                self._show_selection()
                self._publish(range_selection_context(self._surface, row))
                return
        if self._mode == SEARCH_VIEW:
            hit = next(
                (item for item in self._hits if item.offset == self._caret), None
            )
            if hit is not None:
                self._what = ", ".join(hit.owners) or "this hit"
                self._extent = selection_extent(self._surface, self._caret)
                self._show_selection()
                self._publish(selection_context(self._surface, self._caret))
                return
        if not 0 <= self._caret < self._surface.image_size:
            return
        self._what = "this byte"
        self._extent = selection_extent(self._surface, self._caret)
        self._show_selection()
        self._publish(selection_context(self._surface, self._caret))

    def _publish(self, answer) -> None:
        """Hand one model answer to the shared inspector, in its own vocabulary."""
        if self._selection_handler is None:
            return
        self._selection_handler(
            InspectorContext(
                friendly=answer.friendly,
                stable=answer.stable,
                support=answer.support,
                detail=answer.detail,
            )
        )

    def _publish_nothing(self) -> None:
        """No selection: the pane's own empty state, never a stale context."""
        if self._selection_handler is not None:
            self._selection_handler(None)

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

    def _on_jump(self, _position: int) -> None:
        """Jump to a declared table's first byte, through the one selection."""
        if self._surface is None:
            return
        start = self._jump.currentData()
        if start is None:
            return
        name = self._jump.currentText()
        self._caret = int(start)
        if self._mode != RANGES_VIEW:
            self._views.setCurrentText(RANGES_VIEW)
        else:
            self._render()
        self._message.setText(
            f"Jump to {name}: file offset 0x{self._caret:06X} selected"
        )

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
            # One more than will be shown, so a full page of hits can say whether
            # it is the whole answer or the first of more.
            found = search_bytes(
                self._surface, self._find.text(), limit=DEFAULT_SEARCH_HITS + 1
            )
        except SurfaceError as exc:
            self._report(str(exc))
            return
        self._hits_truncated = len(found) > DEFAULT_SEARCH_HITS
        self._hits = found[:DEFAULT_SEARCH_HITS]
        if not self._hits:
            self._message.setText("No raw byte hit for that pattern.")
            return
        if self._views.count() == 2:
            self._views.addItem(SEARCH_VIEW)
        self._message.setText(
            f"{len(self._hits)} raw byte hit(s)"
            + (", the first of more" if self._hits_truncated else "")
            + ". "
            + SEARCH_SCOPE
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

    def focus_offset(self, offset: int) -> None:
        """Point the one selection at `offset` and show the bytes there.

        The route another destination takes to hand this surface a selection.
        The offset is a file offset, which is the spelling the one selection
        already uses, so no conversion happens here and none is needed.
        """
        if self._surface is None:
            return
        if not 0 <= offset < self._surface.image_size:
            self._report(
                f"file offset 0x{offset:06X} is outside the "
                f"{self._surface.image_size}-byte open image."
            )
            return
        self._caret = offset
        self._message.setText(
            f"Go to address: file offset 0x{offset:06X} selected from the Data "
            "destination"
        )
        if self._views.currentText() != BYTES_VIEW:
            self._views.setCurrentText(BYTES_VIEW)
        else:
            self._render()

    def _on_write(self) -> None:
        """Ask the model whether a write is offered, then hand it to the shell."""
        if self._surface is None or self._write_handler is None:
            return
        gate = write_gate(self._surface)
        if not gate.available:
            # The control is disabled for this reason; refuse here too, so a
            # signal that arrives anyway cannot write into bytes nobody checked.
            self._report(gate.reason)
            return
        try:
            new = parse_pattern(self._write_hex.text())
        except SurfaceError as exc:
            self._report(str(exc))
            return
        self._write_handler(self._caret, new, atlas=self._surface.index.atlas)

    def _report(self, reason: str) -> None:
        self._message.setText(reason)
