"""The Entities destination's page: placements, behaviours and object families.

Three modes over one centre table. `Placements` renders the selected map's
placement records, `Behaviours` the descriptors those placements name, and
`Object families` the four per-area families the census records, one modelled and
three shown as unknown structures. The page decides nothing: every identity,
extent, position, behaviour and support state arrives from `entitysurface`.

**One edit path, and it is the shell's `apply_edit`.** A placement edit is one
entry in the session's one journal, so one `Ctrl+Z` returns the project to what
it held and the ROM surface - which reads the same journal - moves with it. The
payload committed is the maps document the Data destination already owns
(`dataedits`), because a placement record lives in `maps/maps.toml`: a second
adapter writing that file would be a second authority over one document, and the
project model has exactly one writer for it.

`Open bytes` hands the record's proven extent to the ROM destination's one
selection instead of opening a second one here. It is offered only where an
extent is proven: a family row states that it has no reader rather than carrying
a button that would go nowhere.
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

from . import entitysurface as es, theme
from .dataedits import DATA_TARGET, read as read_data
from .inspector import SUPPORT_ROLES, InspectorContext
from .journal import EditKind
from .session import Session
from .tablemodel import RowsModel

#: Mode id -> the label the switch shows, in the order the switch offers them.
MODES: tuple[tuple[str, str], ...] = tuple(
    (mode, es.MODE_LABELS[mode]) for mode in es.MODES
)

_PLACEMENT_HEADERS = (
    "Placement",
    "Identity",
    "Address",
    "File offset",
    "Size",
    "Behaviour",
    "Attachment",
    "Support",
)
_BEHAVIOUR_HEADERS = (
    "Behaviour",
    "Handler",
    "Attachment",
    "Placements",
    "File offset",
    "Size",
    "Support",
)
_FAMILY_HEADERS = ("Family", "Pointer slot", "Stride", "Support")

#: What the family mode says, because no row on it can be edited or opened.
_NO_FAMILY_EDITOR = (
    "The unmodelled families have no reader and no writer in this build, so this "
    "mode shows each family's pointer slot and stride and offers no edit."
)


def _support_cell(word: str) -> str:
    """A support state as glyph plus word, the form every surface renders.

    The word is the one the inspector's own state table carries, so the two
    surfaces cannot name one state two ways.
    """
    return f"{theme.status_glyph(SUPPORT_ROLES[word])} {word}"


def _key(row) -> str:
    """What one row is called while the caret survives a re-render.

    A placement and a behaviour carry the SDK's stable identity; a family row has
    no identity to carry, because no family this build does not model has one, so
    it is keyed by its pointer slot, which is its whole address in this build.
    """
    return getattr(row, "identity", "") or row.pointer_slot


class EntityPage(QWidget):
    """The Entities destination's centre page."""

    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("entityPage")
        self._session = session
        #: The shell's one edit path, its one ROM-selection route and the one
        #: inspector. None until the shell wires them.
        self._edit_handler = None
        self._open_handler = None
        self._selection_handler = None
        #: The model for the open image, kept for as long as that image is open.
        self._surface: es.EntitySurface | None = None
        self._surface_for = None
        self._problem = ""
        self._rows: tuple = ()
        self._caret = ""
        self._mode = es.PLACEMENTS
        self._map_index = 0
        self._maps_for = None
        self._applying = False

        self._modes = QComboBox()
        self._modes.setObjectName("entityModeSwitch")
        self._modes.addItems([label for _identifier, label in MODES])
        self._modes.setAccessibleName("Entities view")

        self._maps = QComboBox()
        self._maps.setObjectName("entityMapSwitch")
        self._maps.setAccessibleName("Map")
        self._maps.setMinimumWidth(theme.INSPECTOR_WIDTH)

        self._model = RowsModel(self)
        self._table = QTableView()
        self._table.setObjectName("entityTable")
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.setWordWrap(False)

        self._summary = QLabel()
        self._summary.setProperty("dbzRole", "hint")
        self._summary.setWordWrap(True)

        self._field = QComboBox()
        self._field.setObjectName("entityFieldSwitch")
        self._field.setAccessibleName("Field")
        self._value = QLineEdit()
        self._value.setObjectName("entityFieldValue")
        self._value.setAccessibleName("Field value")
        self._apply = QPushButton("Apply")
        self._open = QPushButton("Open bytes")
        self._message = QLabel()
        self._message.setProperty("dbzRole", "hint")
        self._message.setWordWrap(True)
        self._editor = QWidget()
        self._editor.setObjectName("entityFieldEditor")

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
        top.addWidget(QLabel("Map:"))
        top.addWidget(self._maps, 1)
        layout.addLayout(top)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._editor)
        layout.addWidget(self._detail)
        layout.addWidget(self._message)

        self._modes.currentTextChanged.connect(self._on_mode_changed)
        self._maps.currentIndexChanged.connect(self._on_map_changed)
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

    def pending_bytes(self) -> dict[int, bytes]:
        """The byte effect of this destination's pending edits, for the ROM page.

        Asked on every ROM render, so it is a read of the journal-backed project
        rather than a cached value that could lag one undo behind. Where there is
        nothing to answer with, this returns nothing and `refresh` states the
        reason on the page: a silent empty answer is the shape of provider
        boundary this ticket was told not to add a fourth of.
        """
        surface = self._surface
        if surface is None or self._session.project is None:
            return {}
        return surface.pending_bytes(self._session.project)

    # -- rendering ------------------------------------------------------------

    def refresh(self) -> None:
        """Re-render from the session. The shell calls this after every change."""
        if self._applying:
            # An edit in flight: the shell's re-render would rebuild the field
            # editor from under the handler that is using it. The handler
            # re-renders once it is done instead.
            return
        self._ensure_surface()
        if self._surface is None:
            self._render_unavailable()
            return
        self._render_maps()
        if self._mode == es.FAMILIES:
            self._render_families()
        elif self._mode == es.BEHAVIOURS:
            self._render_behaviours()
        else:
            self._render_placements()

    def _render_maps(self) -> None:
        """Fill the map switch once per image, keeping the reader's own choice."""
        rows = self._surface.map_rows()
        if self._maps_for == self._session.rom_path and self._maps.count() == len(rows):
            self._select_combo(self._maps, self._map_index)
            return
        self._maps_for = self._session.rom_path
        self._maps.blockSignals(True)
        self._maps.clear()
        for row in rows:
            self._maps.addItem(f"{row.label} ({row.placements} placement(s))", row.index)
        self._maps.blockSignals(False)
        # A first visit lands on a map that owns a placement rather than on map 0,
        # so the destination opens on the family it is about. A map with none
        # stays selectable and states that it declares none.
        if not any(row.index == self._map_index and row.placements for row in rows):
            self._map_index = next(
                (row.index for row in rows if row.placements), self._map_index
            )
        self._select_combo(self._maps, self._map_index)

    def _render_placements(self) -> None:
        self._maps.setVisible(True)
        self._editor.setVisible(True)
        rows = self._surface.placements(self._map_index, self._session.project)
        self._rows = rows
        self._model.set_rows(
            _PLACEMENT_HEADERS, tuple(self._placement_cells(row) for row in rows)
        )
        self._summary.setText(
            f"{self._map_caption()}: {len(rows)} placement record(s)"
            + self._project_note()
            + self._behaviour_note()
        )
        self._message.setText(self._records_message(rows))
        self._select_caret()
        self._render_editor()

    def _render_behaviours(self) -> None:
        self._maps.setVisible(True)
        self._editor.setVisible(True)
        rows = self._surface.behaviours(self._map_index, self._session.project)
        self._rows = rows
        self._model.set_rows(
            _BEHAVIOUR_HEADERS, tuple(self._behaviour_cells(row) for row in rows)
        )
        self._summary.setText(
            f"{self._map_caption()}: {len(rows)} behaviour(s) reached from its "
            "placement records" + self._behaviour_note()
        )
        self._message.setText(
            self._surface.behaviour_problem
            or "A behaviour is chosen by authoring a placement clone; the "
            "records here state what the open image already carries."
        )
        self._select_caret()
        self._render_editor()

    def _render_families(self) -> None:
        self._maps.setVisible(False)
        self._editor.setVisible(False)
        rows = self._surface.families()
        self._rows = rows
        self._model.set_rows(
            _FAMILY_HEADERS, tuple(self._family_cells(row) for row in rows)
        )
        self._summary.setText(es.family_summary(rows))
        self._message.setText(_NO_FAMILY_EDITOR)
        self._select_caret()
        self._render_editor()

    def _render_unavailable(self) -> None:
        self._maps.setVisible(False)
        self._editor.setVisible(False)
        self._rows = ()
        self._model.set_rows(_PLACEMENT_HEADERS, ())
        self._summary.setText("")
        self._detail.clear()
        self._open.setEnabled(False)
        self._apply.setEnabled(False)
        self._message.setText(
            self._problem or "Open a ROM image to see its placement records."
        )
        self._publish_selection(None)

    # -- cells ----------------------------------------------------------------

    def _placement_cells(self, row: es.PlacementRow) -> tuple[str, ...]:
        return (
            row.label,
            row.identity,
            f"0x{row.address:08X}",
            f"0x{row.file_offset:06X}",
            f"{row.size}",
            row.behaviour or row.behaviour_note,
            row.attachment or "no script",
            _support_cell("Editable" if row.editable else "Read-only"),
        )

    def _behaviour_cells(self, row: es.BehaviourRow) -> tuple[str, ...]:
        return (
            row.identity,
            row.handler,
            row.attachment or "no script",
            f"{row.placements}",
            f"0x{row.file_offset:06X}",
            f"{row.size}",
            _support_cell("Read-only"),
        )

    def _family_cells(self, row: es.FamilyRow) -> tuple[str, ...]:
        return (
            row.label,
            row.pointer_slot,
            f"{row.stride}",
            _support_cell(row.support),
        )

    def _map_caption(self) -> str:
        return f"Map {self._map_index:04d}"

    def _project_note(self) -> str:
        if self._session.project is None:
            return ". Open a project to move one"
        return ""

    def _behaviour_note(self) -> str:
        problem = self._surface.behaviour_problem
        return f". {problem}" if problem else ""

    def _records_message(self, rows) -> str:
        if self._session.project is None:
            return "No project is open, so there is nothing to edit."
        if not rows:
            return f"{self._map_caption()} declares no placement record in this image."
        return ""

    # -- the field editor -----------------------------------------------------

    def _caret_row(self):
        return next((row for row in self._rows if _key(row) == self._caret), None)

    def _render_editor(self) -> None:
        row = self._caret_row()
        if row is None:
            self._clear_editor()
            self._publish_selection(None)
            return
        if isinstance(row, es.PlacementRow):
            self._render_placement_editor(row)
        elif isinstance(row, es.BehaviourRow):
            self._render_behaviour_editor(row)
        else:
            self._render_family_editor(row)

    def _render_placement_editor(self, row: es.PlacementRow) -> None:
        names = list(es.POSITION_FIELDS)
        chosen = self._field.currentText()
        self._field.blockSignals(True)
        self._field.clear()
        self._field.addItems(names)
        self._field.setCurrentText(chosen if chosen in names else names[0])
        self._field.blockSignals(False)
        self._apply.setEnabled(row.editable)
        self._apply.setToolTip(row.note or f"Move {row.identity}")
        self._open.setEnabled(True)
        self._open.setToolTip(
            f"Show the {row.size} byte(s) at file offset 0x{row.file_offset:06X} in "
            "the ROM destination"
        )
        self._detail.setText(
            f"{row.identity} | slot {row.slot_index} | file offset "
            f"0x{row.file_offset:06X} | image 0x{row.address:08X} | {row.size} bytes | "
            f"position low 0x{row.position_low:04X} high 0x{row.position_high:04X} | "
            f"type 0x{row.type_raw:02X} | id 0x{row.id_raw:02X} | "
            f"behaviour {row.behaviour or 'not read'} | attachment "
            f"{row.attachment or 'none'}"
            + (f" | {row.behaviour_note}" if row.behaviour_note else "")
            + (f" | {row.note}" if row.note else "")
        )
        self._publish_selection(
            InspectorContext(
                friendly=row.label,
                stable=row.identity,
                support="Editable" if row.editable else "Read-only",
                detail=(
                    f"({row.x}, {row.y}) | behaviour {row.behaviour or 'not read'} | "
                    f"attachment {row.attachment or 'none'}"
                    + (f". {row.note}" if row.note else "")
                ),
            )
        )
        self._on_field_changed()

    def _render_behaviour_editor(self, row: es.BehaviourRow) -> None:
        self._clear_field()
        self._open.setEnabled(True)
        self._open.setToolTip(
            f"Show the {row.size} byte(s) at file offset 0x{row.file_offset:06X} in "
            "the ROM destination"
        )
        self._detail.setText(
            f"{row.identity} | file offset 0x{row.file_offset:06X} | {row.size} bytes | "
            f"handler {row.handler} at 0x{row.handler_address:08X} | attachment "
            f"{row.attachment or 'none'} | {row.placements} placement(s) of this map"
            f" | {row.note}"
        )
        self._publish_selection(
            InspectorContext(
                friendly=row.identity,
                stable=row.identity,
                support="Read-only",
                detail=f"{row.note} Attachment: {row.attachment or 'none'}.",
            )
        )

    def _render_family_editor(self, row: es.FamilyRow) -> None:
        self._clear_field()
        self._open.setEnabled(False)
        self._open.setToolTip(
            "This family has no reader, so no byte extent of it is proven and the "
            "ROM destination has nothing to open."
        )
        self._detail.setText(
            f"{row.label} | pointer slot {row.pointer_slot} | stride {row.stride} | "
            f"{row.support} | {row.note} | {row.basis}"
        )
        self._publish_selection(
            InspectorContext(
                friendly=row.label,
                stable="",
                support=row.support,
                detail=(
                    f"pointer slot {row.pointer_slot}, stride {row.stride}. "
                    f"{row.note}. Evidence: {row.basis}. No stable identity exists "
                    "for a family this build does not model."
                ),
            )
        )

    def _clear_field(self) -> None:
        self._field.blockSignals(True)
        self._field.clear()
        self._field.blockSignals(False)
        self._value.clear()
        self._apply.setEnabled(False)

    def _clear_editor(self) -> None:
        self._clear_field()
        self._open.setEnabled(False)
        self._detail.clear()

    def _on_field_changed(self, _text: str = "") -> None:
        row = self._caret_row()
        if not isinstance(row, es.PlacementRow):
            return
        name = self._field.currentText()
        if name not in es.POSITION_FIELDS:
            return
        self._value.setText(str(getattr(row, name)))
        minimum, maximum = es.POSITION_RANGE
        self._value.setToolTip(f"{name}: {minimum}..{maximum}, signed map pixels")

    # -- selection ------------------------------------------------------------

    def _select_caret(self) -> None:
        if not self._rows:
            self._caret = ""
            return
        position = next(
            (at for at, row in enumerate(self._rows) if _key(row) == self._caret), 0
        )
        self._caret = _key(self._rows[position])
        self._select_row(position)

    def _select_row(self, position: int) -> None:
        """Point the table at a row without re-entering the selection handler."""
        selection = self._table.selectionModel()
        selection.blockSignals(True)
        self._table.selectRow(position)
        selection.blockSignals(False)

    def _on_row_changed(self, current, previous) -> None:
        if not current.isValid() or current.row() >= len(self._rows):
            return
        self._caret = _key(self._rows[current.row()])
        self._render_editor()

    # -- actions --------------------------------------------------------------

    def _on_apply(self) -> None:
        """Commit one placement move to the session's journal, or state why not."""
        row = self._caret_row()
        if not isinstance(row, es.PlacementRow) or self._surface is None:
            return
        if self._session.project is None:
            self._report("No project is open, so there is nothing to edit.")
            return
        if not row.editable:
            self._report(row.note or f"{row.identity} cannot be edited.")
            return
        name = self._field.currentText()
        if name not in es.POSITION_FIELDS:
            return
        try:
            value = int(self._value.text().strip(), 0)
        except ValueError:
            self._report(f"{name} must be a whole number.")
            return
        minimum, maximum = es.POSITION_RANGE
        if not minimum <= value <= maximum:
            self._report(
                f"{name}={value} is outside the supported range {minimum}..{maximum}."
            )
            return
        if value == getattr(row, name):
            self._report(f"{name} is already {value}.")
            return
        x, y = value, row.y
        if name == "y":
            x, y = row.x, value
        after = es.with_position(read_data(self._session.project), row, x, y)
        revision = self._session.journal.current_revision
        self._applying = True
        try:
            self._edit_handler(
                kind=EditKind.SEMANTIC,
                target=DATA_TARGET,
                after=after,
                claimed=(es.span(row),),
                reason=f"{row.identity} edit: position",
            )
        finally:
            self._applying = False
        self.refresh()
        if self._session.journal.current_revision != revision:
            self._caret = row.identity
            self._select_caret()
            self._render_editor()
            self._report(f"{row.identity} position = ({x}, {y})")

    def _on_open(self) -> None:
        row = self._caret_row()
        if row is None or self._open_handler is None:
            return
        self._open_handler(row.file_offset)

    def _on_mode_changed(self, label: str) -> None:
        self._mode = next(
            (identifier for identifier, text in MODES if text == label), es.PLACEMENTS
        )
        self._caret = ""
        self._field.clear()
        self.refresh()

    def _on_map_changed(self, _position: int) -> None:
        self._map_index = int(self._maps.currentData())
        self._caret = ""
        self.refresh()

    def _report(self, text: str) -> None:
        self._message.setText(text)

    def _publish_selection(self, context: InspectorContext | None) -> None:
        if self._selection_handler is not None:
            self._selection_handler(context)

    @staticmethod
    def _select_combo(combo: QComboBox, index: int) -> None:
        position = combo.findData(index)
        if position >= 0:
            combo.blockSignals(True)
            combo.setCurrentIndex(position)
            combo.blockSignals(False)

    # -- the open image -------------------------------------------------------

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
            self._surface = es.load_entity_surface(
                session.rom_path,
                session.catalog,
                session.identification,
                session.profile,
                session.base_image,
            )
        except es.EntitySurfaceError as exc:
            self._surface = None
            self._problem = str(exc)
