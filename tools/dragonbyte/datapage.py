"""The Data destination's page: three record tables and the Coverage view.

Four modes over one centre table. `Enemies`, `Characters` and `Map headers`
render the model's rows; `Coverage` renders the census view. The page decides
nothing: a record's fields, its supported range, its byte extent and its
support state all arrive from `datasurface`, and the coverage counts arrive from
`coverage`, which recomputes them from the census rows.

The one edit path is the shell's own `apply_edit`, so a data edit is one entry
in the session's one journal, one `Ctrl+Z` returns the project to what it held,
and the ROM surface - which reads the same journal - moves with it. `Open bytes`
hands the record's proven extent to the ROM destination's one selection instead
of opening a second one here.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
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

from . import coverage, datasurface as ds, theme
from .dataedits import DATA_TARGET, read as read_data
from .inspector import SUPPORT_ROLES, InspectorContext
from .journal import EditKind
from .romsurface import PendingBytes
from .session import Session
from .tablemodel import RowsModel

#: The coverage mode's own id. It is not a record kind, so it is not in
#: `datasurface.KINDS`; the mode list below is the one place the two meet.
COVERAGE_MODE = "coverage"

#: Mode id -> the label the switch shows, in the order the switch offers them.
MODES: tuple[tuple[str, str], ...] = tuple(
    (kind, ds.KIND_LABELS[kind]) for kind in ds.KINDS
) + ((COVERAGE_MODE, "Coverage"),)

_RECORD_HEADERS = ("Record", "Identity", "Address", "File offset", "Size", "Support")
_COVERAGE_HEADERS = ("Row", "Area", "Support", "Basis", "Engine knowledge", "Confidence")

#: What a coverage row says where the census has no evidence word for a cell.
_NO_EDITOR = (
    "Coverage is a view over the census: no record on this page can be edited "
    "and no count here is stored, every one is recomputed from the census rows."
)


def _support_cell(editable: bool) -> str:
    """A support state as glyph plus word, the form every surface renders.

    The word is the one the inspector's own state table carries, so the two
    surfaces cannot name one state two ways.
    """
    word = "Editable" if editable else "Read-only"
    return f"{theme.status_glyph(SUPPORT_ROLES[word])} {word}"


class DataPage(QWidget):
    """The Data destination's centre page."""

    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dataPage")
        self._session = session
        #: The shell's one edit path, its one ROM-selection route and the one
        #: inspector. None until the shell wires them.
        self._edit_handler = None
        self._open_handler = None
        self._selection_handler = None
        #: The model for the open image, kept for as long as that image is open.
        self._surface: ds.DataSurface | None = None
        self._surface_for = None
        self._problem = ""
        self._rows: tuple[ds.RecordRow, ...] = ()
        self._caret = ""
        self._mode = ds.ENEMY
        self._applying = False
        self._census_document: dict | None = None
        self._census_problem = ""
        self._census_loaded = False
        self._coverage: coverage.CoverageView | None = None

        self._modes = QComboBox()
        self._modes.setObjectName("dataModeSwitch")
        self._modes.addItems([label for _identifier, label in MODES])
        self._modes.setAccessibleName("Data view")

        self._model = RowsModel(self)
        self._table = QTableView()
        self._table.setObjectName("dataTable")
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.setWordWrap(False)

        self._summary = QLabel()
        self._summary.setProperty("dbzRole", "hint")
        self._summary.setWordWrap(True)

        self._field = QComboBox()
        self._field.setObjectName("dataFieldSwitch")
        self._field.setAccessibleName("Field")
        self._value = QLineEdit()
        self._value.setObjectName("dataFieldValue")
        self._value.setAccessibleName("Field value")
        self._apply = QPushButton("Apply")
        self._open = QPushButton("Open bytes")
        self._message = QLabel()
        self._message.setProperty("dbzRole", "hint")
        self._message.setWordWrap(True)
        self._editor = QWidget()
        self._editor.setObjectName("dataFieldEditor")

        editor_row = QHBoxLayout(self._editor)
        editor_row.setContentsMargins(0, 0, 0, 0)
        editor_row.setSpacing(theme.SPACE_SM)
        editor_row.addWidget(QLabel("Field:"))
        editor_row.addWidget(self._field)
        editor_row.addWidget(QLabel("Value:"))
        editor_row.addWidget(self._value, 1)
        editor_row.addWidget(self._apply)
        editor_row.addSpacing(theme.SPACE_LG)
        editor_row.addWidget(self._open)

        self._detail = QLabel()
        self._detail.setProperty("dbzRole", "technical")
        self._detail.setWordWrap(True)
        self._detail.setTextInteractionFlags(
            self._detail.textInteractionFlags()
            | Qt.TextInteractionFlag.TextSelectableByMouse
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD
        )
        layout.setSpacing(theme.SPACE_SM)
        top = QHBoxLayout()
        top.setSpacing(theme.SPACE_SM)
        top.addWidget(QLabel("View:"))
        top.addWidget(self._modes)
        top.addStretch(1)
        layout.addLayout(top)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._editor)
        layout.addWidget(self._detail)
        layout.addWidget(self._message)

        self._modes.currentTextChanged.connect(self._on_mode_changed)
        self._field.currentTextChanged.connect(self._on_field_changed)
        self._apply.clicked.connect(self._on_apply)
        self._value.returnPressed.connect(self._on_apply)
        self._open.clicked.connect(self._on_open)
        self._table.selectionModel().currentRowChanged.connect(self._on_row_changed)

        self.refresh()

    # -- wiring ---------------------------------------------------------------

    def set_edit_handler(self, handler) -> None:
        """The shell's one edit path: this page never commits an edit itself."""
        self._edit_handler = handler

    def set_open_bytes_handler(self, handler) -> None:
        """The shell's one route into the ROM surface's selection."""
        self._open_handler = handler

    def set_selection_handler(self, handler) -> None:
        """The shell's one inspector, told what this page has selected."""
        self._selection_handler = handler

    # -- the ROM surface's question -------------------------------------------

    def pending_bytes(self) -> PendingBytes:
        """The byte effect of this destination's pending edits, for the ROM page.

        Asked on every ROM render, so it is a read of the journal-backed project
        rather than a cached value that could lag one undo behind. A destination
        that has not read this image, and one whose surface cannot encode the
        edits, both state why instead of answering with nothing; no project open
        is the one case with nothing to state.
        """
        surface = self._surface
        if self._session.project is None:
            return PendingBytes()
        if surface is None:
            return PendingBytes(
                problem=self._problem or "the records have not been read yet"
            )
        try:
            return PendingBytes(surface.pending_bytes(self._session.project))
        except Exception as exc:  # noqa: BLE001 - the exception text is the report
            return PendingBytes(problem=f"the pending bytes could not be stated: {exc}")

    # -- rendering ------------------------------------------------------------

    def refresh(self) -> None:
        """Re-render from the session. The shell calls this after every change."""
        if self._applying:
            # An edit in flight: the shell's re-render would rebuild the field
            # editor from under the handler that is using it. The handler
            # re-renders once it is done instead.
            return
        self._ensure_surface()
        if self._mode == COVERAGE_MODE:
            self._render_coverage()
        elif self._surface is None:
            self._render_unavailable()
        else:
            self._render_records()

    def _render_records(self) -> None:
        self._editor.setVisible(True)
        self._summary.setVisible(True)
        rows = self._surface.rows(self._mode, self._session.project)
        self._rows = rows
        self._model.set_rows(
            _RECORD_HEADERS, tuple(self._row_cells(row) for row in rows)
        )
        self._summary.setText(self._records_summary(rows))
        self._select_caret()
        self._render_editor()

    def _records_summary(self, rows: tuple[ds.RecordRow, ...]) -> str:
        editable = sum(1 for row in rows if row.editable)
        note = f"{len(rows)} record(s), {editable} editable through the open project"
        if self._mode == ds.MAP_HEADER and self._surface.maps_problem:
            return f"{note}. {self._surface.maps_problem}"
        if self._session.project is None:
            return f"{note}. Open a project to edit these records."
        return note

    def _row_cells(self, row: ds.RecordRow) -> tuple[str, ...]:
        return (
            row.label,
            row.identity,
            f"0x{row.address:08X}",
            f"0x{row.file_offset:06X}",
            f"{row.size}",
            _support_cell(row.editable),
        )

    def _render_unavailable(self) -> None:
        self._editor.setVisible(False)
        self._rows = ()
        self._model.set_rows(_RECORD_HEADERS, ())
        self._summary.setText("")
        self._detail.clear()
        self._message.setText(
            self._problem or "Open a ROM image to see its data records."
        )
        self._open.setEnabled(False)
        self._publish_selection(None)

    def _render_coverage(self) -> None:
        self._editor.setVisible(False)
        document, problem = self._census()
        self._coverage = None
        if document is None or self._session.profile is None:
            self._rows = ()
            self._model.set_rows(_COVERAGE_HEADERS, ())
            self._summary.setText("")
            self._detail.clear()
            self._message.setText(problem or "Open a ROM image to see its coverage.")
            self._publish_selection(None)
            return
        try:
            view = coverage.coverage_view(document, self._session.profile.id)
        except coverage.CoverageError as exc:
            self._rows = ()
            self._model.set_rows(_COVERAGE_HEADERS, ())
            self._summary.setText("")
            self._message.setText(str(exc))
            self._publish_selection(None)
            return
        self._coverage = view
        self._model.set_rows(
            _COVERAGE_HEADERS,
            tuple(
                (
                    row.name,
                    row.area,
                    f"{theme.status_glyph(SUPPORT_ROLES.get(row.word, 'neutral'))} "
                    f"{row.word}",
                    row.basis,
                    row.engine_knowledge,
                    row.confidence,
                )
                for row in view.rows
            ),
        )
        self._summary.setText(
            "\n".join(
                [view.summary()]
                + [
                    f"{theme.status_glyph(SUPPORT_ROLES.get(group.word, 'neutral'))} "
                    f"{group.word}: {group.cells}"
                    for group in view.groups
                ]
            )
        )
        self._message.setText(_NO_EDITOR)
        self._detail.clear()
        if view.rows:
            self._select_row(0)

    def _render_coverage_detail(self, position: int) -> None:
        view = self._coverage
        if view is None or not 0 <= position < len(view.rows):
            self._detail.clear()
            return
        row = view.rows[position]
        self._detail.setText(
            f"{row.row_id} | census state {row.state} | {row.basis} | "
            f"{row.engine_knowledge} / {row.confidence} | {row.evidence}"
        )
        self._publish_selection(
            InspectorContext(
                friendly=row.name,
                stable=row.row_id,
                support=row.word,
                detail=f"{row.area} | {row.basis} | {row.state}",
            )
        )

    # -- the field editor -----------------------------------------------------

    def _caret_row(self) -> ds.RecordRow | None:
        return next((row for row in self._rows if row.identity == self._caret), None)

    def _render_editor(self) -> None:
        row = self._caret_row()
        if row is None:
            self._field.blockSignals(True)
            self._field.clear()
            self._field.blockSignals(False)
            self._value.clear()
            self._apply.setEnabled(False)
            self._open.setEnabled(False)
            self._detail.clear()
            self._publish_selection(None)
            return
        names = [field.name for field in row.fields]
        chosen = self._field.currentText()
        self._field.blockSignals(True)
        self._field.clear()
        self._field.addItems(names)
        self._field.setCurrentText(chosen if chosen in names else names[0])
        self._field.blockSignals(False)
        self._apply.setEnabled(row.editable)
        self._apply.setToolTip(
            row.note or f"Set {self._field.currentText()} on {row.identity}"
        )
        self._open.setEnabled(True)
        self._open.setToolTip(
            f"Show the {row.size} byte(s) at file offset 0x{row.file_offset:06X} in "
            "the ROM destination"
        )
        self._detail.setText(
            f"{row.identity} | file offset 0x{row.file_offset:06X} | "
            f"image 0x{row.address:08X} | {row.size} bytes | "
            f"{'Editable' if row.editable else 'Read-only'}"
            + (f" | {row.note}" if row.note else "")
        )
        self._publish_selection(
            InspectorContext(
                friendly=row.label,
                stable=row.identity,
                support="Editable" if row.editable else "Read-only",
                detail=(
                    f"file offset 0x{row.file_offset:06X}, {row.size} bytes"
                    + (f". {row.note}" if row.note else "")
                ),
            )
        )
        self._on_field_changed()

    def _on_field_changed(self, _text: str = "") -> None:
        row = self._caret_row()
        if row is None:
            return
        field = row.field(self._field.currentText())
        if field is None:
            return
        self._value.setText(str(field.value))
        self._value.setToolTip(f"{field.name}: {field.range_text}")

    def _on_mode_changed(self, label: str) -> None:
        self._mode = next(
            (identifier for identifier, text in MODES if text == label), ds.ENEMY
        )
        self._caret = ""
        self.refresh()

    def _select_caret(self) -> None:
        if not self._rows:
            return
        position = next(
            (at for at, row in enumerate(self._rows) if row.identity == self._caret), 0
        )
        self._caret = self._rows[position].identity
        self._select_row(position)

    def _select_row(self, position: int) -> None:
        """Point the table at a row without re-entering the selection handler."""
        selection = self._table.selectionModel()
        selection.blockSignals(True)
        self._table.selectRow(position)
        selection.blockSignals(False)

    def _on_row_changed(self, current, previous) -> None:
        if self._mode == COVERAGE_MODE:
            if current.isValid():
                self._render_coverage_detail(current.row())
            return
        if not current.isValid() or current.row() >= len(self._rows):
            return
        self._caret = self._rows[current.row()].identity
        self._render_editor()

    # -- actions --------------------------------------------------------------

    def _on_apply(self) -> None:
        """Commit one field edit to the session's journal, or state why not."""
        row = self._caret_row()
        if row is None or self._surface is None:
            return
        if self._session.project is None:
            self._report("No project is open, so there is nothing to edit.")
            return
        if not row.editable:
            self._report(row.note or f"{row.identity} cannot be edited.")
            return
        name = self._field.currentText()
        field = row.field(name)
        if field is None:
            return
        try:
            value = int(self._value.text().strip(), 0)
        except ValueError:
            self._report(f"{name} must be a whole number.")
            return
        if value < field.minimum or (
            field.maximum is not None and value > field.maximum
        ):
            self._report(f"{name}={value} is outside the supported range {field.range_text}.")
            return
        if value == field.value:
            self._report(f"{name} is already {value}.")
            return
        after = ds.with_field(read_data(self._session.project), row, name, value)
        revision = self._session.journal.current_revision
        self._applying = True
        try:
            self._edit_handler(
                kind=EditKind.SEMANTIC,
                target=DATA_TARGET,
                after=after,
                claimed=(ds.span(row),),
                reason=f"{row.identity} edit: {name}",
            )
        finally:
            self._applying = False
        self.refresh()
        if self._session.journal.current_revision != revision:
            self._caret = row.identity
            self._select_caret()
            self._render_editor()
            self._report(f"{row.identity} {name} = {value}")

    def _on_open(self) -> None:
        row = self._caret_row()
        if row is None or self._open_handler is None:
            return
        self._open_handler(row.file_offset)

    def _report(self, text: str) -> None:
        self._message.setText(text)

    def _publish_selection(self, context: InspectorContext | None) -> None:
        if self._selection_handler is not None:
            self._selection_handler(context)

    # -- the open image and the census ----------------------------------------

    def _ensure_surface(self) -> None:
        session = self._session
        if (
            session.base_image is None
            or session.profile is None
            or session.identification is None
            or session.rom_path is None
            or session.catalog is None
        ):
            self._surface = None
            self._surface_for = None
            self._problem = ""
            return
        if self._surface_for == session.rom_path and self._surface is not None:
            return
        self._surface_for = session.rom_path
        try:
            self._surface = ds.load_data_surface(
                session.rom_path,
                session.catalog,
                session.identification,
                session.profile,
                session.base_image,
            )
            self._problem = ""
        except ds.DataSurfaceError as exc:
            self._surface = None
            self._problem = str(exc)

    def _census(self) -> tuple[dict | None, str]:
        if not self._census_loaded:
            self._census_loaded = True
            try:
                self._census_document = coverage.load_census()
            except coverage.CoverageError as exc:
                self._census_problem = str(exc)
        return self._census_document, self._census_problem
