"""The Scripts & Text destination's page: scripts, events, dialogue and strings.

Four modes over one centre table, and the two text modes are told apart in three
places at once, because the whole point of this destination is that they are not
interchangeable:

1. each row's own support column and identity column, where a string's identity is
   a pointer-table slot (``text:0000``) and a dialogue record's is a packed handle
   (``dialogue:0x02002641``);
2. the mode's own identity line above the table, which names the identity form, the
   storage and the offset of the system being shown;
3. the mode switch itself, whose two text modes are ``Spoken dialogue`` and
   ``String tables`` and never share a row.

**One edit path, and it is the shell's `apply_edit`.** A string edit commits under
the string-table target, and a spoken-dialogue replacement under the dialogue
target, so one ``Ctrl+Z`` returns whichever was edited and the ROM surface, which
reads the same journal, moves with it. Reads come from `textsurface`, which owns no
codec of its own.

`Open bytes` hands a proven extent to the ROM destination's one selection instead
of opening a second one here. A row with no proven extent states that reason rather
than carrying a button that would go nowhere.
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

from . import textsurface as ts, theme
from .inspector import SUPPORT_ROLES, InspectorContext
from .journal import EditKind
from .session import Session
from .tablemodel import RowsModel
from .textedits import TEXT_TARGET

#: The journal target the dialogue replacement document is committed under. The
#: journal's own registry owns the adapter; this is the name it is registered
#: under, and it is deliberately not the string-table target.
DIALOGUE_TARGET = "dialogues"

#: Mode id -> the label the switch shows, in the order the switch offers them.
MODES: tuple[tuple[str, str], ...] = tuple(
    (mode, ts.MODE_LABELS[mode]) for mode in ts.MODES
)

_ROOT_HEADERS = (
    "Root",
    "Family",
    "Owner",
    "File offset",
    "Size",
    "Instructions",
    "Support",
)
_EVENT_HEADERS = (
    "Resource",
    "File offset",
    "Size",
    "Type",
    "Text indices",
    "Code",
    "Support",
)
_DIALOGUE_HEADERS = (
    "System",
    "Identity",
    "Selector",
    "Decoded start",
    "Length",
    "Text",
    "Sites",
    "Event resources",
    "Authoring target",
    "Support",
)
_STRING_HEADERS = (
    "System",
    "Identity",
    "Slot",
    "Text",
    "File offset",
    "Allocation",
    "Support",
)

#: What each read-only mode says about itself, because no row on it can be edited.
_NO_SCRIPT_EDITOR = (
    "This build has no event editor and no authoring verb, so a script root is "
    "displayed and never offered for editing. The corpus is fixed-size, and the "
    "SDK's own evidence contract is what bounds it."
)
_NO_EVENT_EDITOR = (
    "The event resource corpus has no reader-based writer in this build, so every "
    "row here states what the image holds and offers no edit."
)

#: The one sentence the two text modes carry, so a reader who lands on either is
#: told what the other is and that an edit of one does not reach it.
_TWO_SYSTEMS = (
    "Two text systems live in this image and they are not interchangeable: editing "
    "one has exactly zero effect on the other."
)


def _support_cell(word: str) -> str:
    """A support state as glyph plus word, the form every surface renders."""
    return f"{theme.status_glyph(SUPPORT_ROLES[word])} {word}"


class TextPage(QWidget):
    """The Scripts & Text destination's centre page."""

    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("textPage")
        self._session = session
        #: The shell's one edit path, its one ROM-selection route and the one
        #: inspector. None until the shell wires them.
        self._edit_handler = None
        self._open_handler = None
        self._selection_handler = None
        self._surface: ts.TextSurface | None = None
        self._surface_for = None
        self._problem = ""
        self._rows: tuple = ()
        self._caret = ""
        self._mode = ts.SCRIPTS
        self._family = ""
        self._applying = False

        self._modes = QComboBox()
        self._modes.setObjectName("textModeSwitch")
        self._modes.addItems([label for _identifier, label in MODES])
        self._modes.setAccessibleName("Scripts and text view")

        self._families = QComboBox()
        self._families.setObjectName("textFamilySwitch")
        self._families.setAccessibleName("Script family")
        self._families.setMinimumWidth(theme.INSPECTOR_WIDTH)

        self._model = RowsModel(self)
        self._table = QTableView()
        self._table.setObjectName("textTable")
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.setWordWrap(False)

        #: The identity line: which text system this mode shows, and where that
        #: system's identity comes from. This is the page's own statement, drawn
        #: above the table for the two text modes and empty for the two script ones.
        self._identity_line = QLabel()
        self._identity_line.setObjectName("textIdentityLine")
        self._identity_line.setProperty("dbzRole", "hint")
        self._identity_line.setWordWrap(True)

        self._summary = QLabel()
        self._summary.setProperty("dbzRole", "hint")
        self._summary.setWordWrap(True)

        self._value = QLineEdit()
        self._value.setObjectName("textEditValue")
        self._value.setAccessibleName("Replacement text")
        self._apply = QPushButton("Apply")
        self._open = QPushButton("Open bytes")
        self._message = QLabel()
        self._message.setProperty("dbzRole", "hint")
        self._message.setWordWrap(True)
        self._editor = QWidget()
        self._editor.setObjectName("textFieldEditor")

        editor_row = QHBoxLayout(self._editor)
        editor_row.setContentsMargins(0, 0, 0, 0)
        editor_row.setSpacing(theme.SPACE_SM)
        editor_row.addWidget(QLabel("Text:"))
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
        top.addWidget(QLabel("Family:"))
        top.addWidget(self._families, 1)
        layout.addLayout(top)
        layout.addWidget(self._identity_line)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._editor)
        layout.addWidget(self._detail)
        layout.addWidget(self._message)

        self._modes.currentTextChanged.connect(self._on_mode_changed)
        self._families.currentIndexChanged.connect(self._on_family_changed)
        self._value.returnPressed.connect(self._on_apply)
        self._apply.clicked.connect(self._on_apply)
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
        """The byte effect of this destination's pending string edits.

        A dialogue replacement rewrites a decoded container, so its bytes are not
        a file range this surface can state; the manifest's own dialogue
        provenance carries that edit. The string table's in-place edits are a
        byte range, and they are what this provider contributes.
        """
        surface = self._surface
        if surface is None or self._session.project is None:
            return {}
        return surface.pending_bytes(self._session.project)

    # -- rendering ------------------------------------------------------------

    def refresh(self) -> None:
        """Re-render from the session. The shell calls this after every change."""
        if self._applying:
            return
        self._ensure_surface()
        if self._surface is None:
            self._render_unavailable()
            return
        self._render_families_switch()
        if self._mode == ts.STRINGS:
            self._render_strings()
        elif self._mode == ts.DIALOGUE:
            self._render_dialogue()
        elif self._mode == ts.EVENTS:
            self._render_events()
        else:
            self._render_scripts()

    def _render_families_switch(self) -> None:
        """Fill the family switch once per image, keeping the reader's own choice."""
        rows = self._surface.families
        labels = [row.family for row in rows]
        if self._families.count() != len(labels) or [
            self._families.itemText(at) for at in range(self._families.count())
        ] != labels:
            self._families.blockSignals(True)
            self._families.clear()
            self._families.addItems(labels)
            self._families.blockSignals(False)
        if labels and self._family not in labels:
            self._family = labels[0]
        position = self._families.findText(self._family)
        if position >= 0:
            self._families.blockSignals(True)
            self._families.setCurrentIndex(position)
            self._families.blockSignals(False)

    def _render_scripts(self) -> None:
        self._families.setVisible(True)
        rows = ()
        for family in [self._family] if self._family else []:
            rows += self._surface.script_roots(family)
        self._rows = rows
        self._model.set_rows(
            _ROOT_HEADERS, tuple(self._root_cells(row) for row in rows)
        )
        self._identity_line.clear()
        self._summary.setText(
            f"{ts.family_summary(self._surface.families)}; {len(rows)} root(s) in "
            f"family {self._family or 'none'}"
            + (f". {self._surface.family_problem}" if self._surface.family_problem else "")
        )
        self._message.setText(_NO_SCRIPT_EDITOR)
        self._editor.setVisible(False)
        self._select_caret()
        self._render_editor()

    def _render_events(self) -> None:
        self._families.setVisible(False)
        rows = self._surface.event_rows()
        self._rows = rows
        self._model.set_rows(
            _EVENT_HEADERS, tuple(self._event_cells(row) for row in rows)
        )
        self._identity_line.clear()
        self._summary.setText(
            ts.event_summary(rows)
            + (f". {self._surface.events_problem}" if self._surface.events_problem else "")
        )
        self._message.setText(
            _NO_EVENT_EDITOR if rows else self._surface.events_problem
        )
        self._editor.setVisible(False)
        self._select_caret()
        self._render_editor()

    def _render_dialogue(self) -> None:
        self._families.setVisible(False)
        rows = self._surface.dialogue_rows()
        self._rows = rows
        self._model.set_rows(
            _DIALOGUE_HEADERS, tuple(self._dialogue_cells(row) for row in rows)
        )
        self._identity_line.setText(
            f"System: {ts.SPOKEN_SYSTEM}. {ts.SPOKEN_IDENTITY_LINE} "
            f"{_TWO_SYSTEMS}"
        )
        self._summary.setText(ts.dialogue_summary(rows))
        self._message.setText(
            "Open a project to replace the one record with an authored target."
            if self._session.project is None
            else ""
        )
        self._editor.setVisible(True)
        self._select_caret()
        self._render_editor()

    def _render_strings(self) -> None:
        self._families.setVisible(False)
        rows = self._surface.string_rows()
        self._rows = rows
        self._model.set_rows(
            _STRING_HEADERS, tuple(self._string_cells(row) for row in rows)
        )
        self._identity_line.setText(
            f"System: {ts.STRING_SYSTEM}. {ts.STRING_IDENTITY_LINE} {_TWO_SYSTEMS}"
        )
        self._summary.setText(
            ts.string_summary(rows)
            + (f". {self._surface.strings_problem}" if self._surface.strings_problem else "")
        )
        self._message.setText(
            self._surface.strings_problem
            or (
                "Open a project to edit a string."
                if self._session.project is None
                else ""
            )
        )
        self._editor.setVisible(True)
        self._select_caret()
        self._render_editor()

    def _render_unavailable(self) -> None:
        self._families.setVisible(False)
        self._editor.setVisible(False)
        self._rows = ()
        self._model.set_rows(_ROOT_HEADERS, ())
        self._identity_line.clear()
        self._summary.setText("")
        self._detail.clear()
        self._open.setEnabled(False)
        self._apply.setEnabled(False)
        self._message.setText(
            self._problem or "Open a ROM image to see its scripts, events, dialogue and strings."
        )
        self._publish_selection(None)

    # -- cells ----------------------------------------------------------------

    def _root_cells(self, row: ts.ScriptRootRow) -> tuple[str, ...]:
        return (
            row.identity,
            row.family,
            row.owner or row.owner_kind or "no proven owner",
            f"0x{row.file_offset:06X}",
            f"{row.size}",
            f"{row.instructions}",
            _support_cell("Read-only"),
        )

    def _event_cells(self, row: ts.EventResourceRow) -> tuple[str, ...]:
        return (
            row.identity,
            f"0x{row.file_offset:06X}",
            f"{row.size}",
            row.dialog_type,
            ", ".join(f"text:{index:04d}" for index in row.text_indices) or "none proven",
            f"{row.code_size} byte(s), {row.instructions} instruction(s)"
            if row.code_file_offset is not None
            else "no readable code block",
            _support_cell("Read-only"),
        )

    def _dialogue_cells(self, row: ts.DialogueRow) -> tuple[str, ...]:
        return (
            row.system,
            f"{row.identity} ({row.identity_form})",
            f"{row.selector}",
            f"0x{row.decoded_start:04X}",
            f"{row.decoded_length}",
            row.text or row.note,
            f"{len(row.sites)}",
            ", ".join(f"{index:04d}" for index in row.event_resources) or "none",
            row.authoring_name or "none",
            _support_cell("Editable" if row.editable else "Read-only"),
        )

    def _string_cells(self, row: ts.StringRow) -> tuple[str, ...]:
        return (
            row.system,
            f"{row.identity} ({row.identity_form})",
            f"{row.index}",
            row.text,
            f"0x{row.file_offset:06X}",
            f"{row.allocation}",
            _support_cell("Editable"),
        )

    # -- the value editor -----------------------------------------------------

    def _caret_row(self):
        return next((row for row in self._rows if _key(row) == self._caret), None)

    def _render_editor(self) -> None:
        row = self._caret_row()
        if row is None:
            self._clear_editor()
            self._publish_selection(None)
            return
        if isinstance(row, ts.DialogueRow):
            self._render_dialogue_editor(row)
        elif isinstance(row, ts.StringRow):
            self._render_string_editor(row)
        elif isinstance(row, ts.EventResourceRow):
            self._render_event_editor(row)
        else:
            self._render_root_editor(row)

    def _render_dialogue_editor(self, row: ts.DialogueRow) -> None:
        self._editor.setVisible(True)
        editable = row.editable and self._session.project is not None
        if not editable:
            self._clear_value()
            self._apply.setEnabled(False)
            self._apply.setToolTip(
                f"{row.identity} has no authored target, so this build will not "
                "replace it."
                if not row.editable
                else "No project is open, so there is nothing to edit."
            )
        else:
            self._apply.setEnabled(True)
            self._apply.setToolTip(
                f"Replace the text of {row.authoring_name} ({row.identity})"
            )
            current = self._session.project.dialogues.get(row.authoring_name, "")
            self._value.setText(current or row.text)
        self._open.setEnabled(bool(row.sites))
        self._open.setToolTip(
            f"Show the handle field of {len(row.sites)} event-resource site(s), "
            "from 0x%06X" % row.sites[0]
            if row.sites
            else "This record has no proven event-resource site, so no byte extent "
            "of it is established and the ROM destination has nothing to open."
        )
        self._detail.setText(
            f"{row.identity} | system {row.system} | identity {row.identity_form} | "
            f"selector {row.selector} | decoded start 0x{row.decoded_start:04X} | "
            f"{row.decoded_length} bytes | {row.provenance} | authoring target "
            f"{row.authoring_name or 'none'}"
            + (f" | {row.note}" if row.note else "")
        )
        self._publish_selection(
            InspectorContext(
                friendly=row.authoring_name or row.identity,
                stable=row.identity,
                support="Editable" if row.editable else "Read-only",
                detail=f"{row.text or row.note}. {row.provenance}."
                + (f" {row.note}" if row.note else ""),
            )
        )

    def _render_string_editor(self, row: ts.StringRow) -> None:
        self._editor.setVisible(True)
        self._clear_value()
        editable = self._session.project is not None and self._surface.strings is not None
        self._apply.setEnabled(editable)
        self._apply.setToolTip(
            f"Replace {row.identity} ({row.allocation} bytes allocated)"
            if editable
            else self._surface.strings_problem or "No project is open, so there is nothing to edit."
        )
        if editable:
            authored = self._session.project.strings.get(
                _identity(row.identity), row.text
            )
            self._value.setText(authored)
        self._open.setEnabled(True)
        self._open.setToolTip(
            f"Show the {row.allocation} byte(s) at file offset 0x{row.file_offset:06X} "
            "in the ROM destination"
        )
        self._detail.setText(
            f"{row.identity} | system {row.system} | identity {row.identity_form} | "
            f"pointer-table slot {row.index} | file offset 0x{row.file_offset:06X} | "
            f"image 0x{row.address:08X} | {row.allocation} byte(s) allocated | the "
            "pool at file offset 0x05792C backs this slot"
        )
        self._publish_selection(
            InspectorContext(
                friendly=row.identity,
                stable=row.identity,
                support="Editable",
                detail=(
                    f"pointer-table slot {row.index} | {row.allocation} bytes | "
                    f"{row.text[:60]}"
                ),
            )
        )

    def _render_event_editor(self, row: ts.EventResourceRow) -> None:
        self._editor.setVisible(False)
        self._detail.setText(
            f"{row.identity} | slot 0x{row.slot_file_offset:06X} | record "
            f"0x{row.file_offset:06X}..0x{row.file_offset + row.size:06X} | "
            f"{row.dialog_type} at 0x{row.dialog_file_offset:06X} | code "
            f"{('0x%06X, %d instruction(s)' % (row.code_file_offset, row.instructions)) if row.code_file_offset is not None else 'not readable'} | "
            f"proven text indices "
            f"{', '.join(f'text:{index:04d}' for index in row.text_indices) or 'none'} | "
            f"{row.note}"
        )
        self._open.setEnabled(False)
        self._open.setToolTip(
            "This destination does not offer a byte extent for an event resource."
        )
        self._apply.setEnabled(False)
        self._publish_selection(
            InspectorContext(
                friendly=row.identity,
                stable=row.identity,
                support="Read-only",
                detail=f"{row.note} No edit is offered.",
            )
        )

    def _render_root_editor(self, row: ts.ScriptRootRow) -> None:
        self._editor.setVisible(False)
        extent = (
            "measured by the corpus segment"
            if row.measured_extent
            else "tiled to the next root in the pool"
        )
        self._detail.setText(
            f"{row.identity} | family {row.family} | owner "
            f"{row.owner or 'none proven'} ({row.owner_kind or 'none'}) | file offset "
            f"0x{row.file_offset:06X} | image 0x{row.address:08X} | {row.size} byte(s), "
            f"{extent} | {row.instructions} instruction(s) | {_NO_SCRIPT_EDITOR}"
        )
        self._open.setEnabled(True)
        self._open.setToolTip(
            f"Show the {row.size} byte(s) at file offset 0x{row.file_offset:06X} in "
            "the ROM destination"
        )
        self._apply.setEnabled(False)
        self._publish_selection(
            InspectorContext(
                friendly=row.identity,
                stable=row.identity,
                support="Read-only",
                detail=(
                    f"family {row.family} | owner {row.owner or 'none proven'} | "
                    f"{row.size} bytes | {_NO_SCRIPT_EDITOR}"
                ),
            )
        )

    def _clear_value(self) -> None:
        """Empty the field. It decides nothing about whether an edit is offered."""
        self._value.clear()

    def _clear_editor(self) -> None:
        self._clear_value()
        self._open.setEnabled(False)
        self._detail.clear()

    # -- selection ------------------------------------------------------------

    def _select_caret(self) -> None:
        if not self._rows:
            self._caret = ""
            self._render_editor()
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
        """Commit one text edit or one dialogue replacement, or state why not."""
        row = self._caret_row()
        if self._session.project is None:
            self._report("No project is open, so there is nothing to edit.")
            return
        if isinstance(row, ts.StringRow):
            self._apply_string(row)
        elif isinstance(row, ts.DialogueRow):
            self._apply_dialogue(row)
        else:
            self._report("This row has no edit.")

    def _apply_string(self, row: ts.StringRow) -> None:
        """Commit one string edit under the string-table target."""
        identity = _identity(row.identity)
        text = self._value.text()
        surface = self._surface
        problem = surface.string_problem(identity, text)
        if problem:
            self._report(problem)
            return
        if surface.strings.entry(identity).text == text:
            self._report(f"{row.identity} already reads that text.")
            return
        from dataclasses import replace

        from .textedits import read as read_text

        after = replace(
            read_text(self._session.project),
            strings={**self._session.project.strings, identity: text},
        )
        revision = self._session.journal.current_revision
        self._applying = True
        try:
            self._edit_handler(
                kind=EditKind.SEMANTIC,
                target=TEXT_TARGET,
                after=after,
                claimed=(surface.string_span(identity),),
                reason=f"{row.identity} edit: text",
            )
        finally:
            self._applying = False
        self.refresh()
        if self._session.journal.current_revision != revision:
            self._caret = row.identity
            self._select_caret()
            self._report(f"{row.identity} text replaced")

    def _apply_dialogue(self, row: ts.DialogueRow) -> None:
        """Commit one spoken-dialogue replacement, owned by its record identity."""
        if not row.editable:
            self._report(
                f"{row.identity} has no authored target, so this build will not "
                "replace it."
            )
            return
        target = next(
            (
                item
                for item in self._surface.authored_dialogue()
                if item.name == row.authoring_name
            ),
            None,
        )
        if target is None:
            self._report(f"{row.authoring_name} is not a target of this profile.")
            return
        text = self._value.text()
        problem = self._surface.dialogue_problem(target, text)
        if problem:
            self._report(problem)
            return
        if self._surface.dialogue_text(target) == text:
            self._report(f"{row.authoring_name} already reads that text.")
            return
        after = {**self._session.project.dialogues, row.authoring_name: text}
        revision = self._session.journal.current_revision
        self._applying = True
        try:
            self._edit_handler(
                kind=EditKind.SEMANTIC,
                target=DIALOGUE_TARGET,
                after=after,
                claimed=(ts.dialogue_span(row),),
                resources=(row.authoring_name,),
                reason=f"dialogue edit: {row.authoring_name}",
            )
        finally:
            self._applying = False
        self.refresh()
        if self._session.journal.current_revision != revision:
            self._caret = row.identity
            self._select_caret()
            self._report(f"{row.authoring_name} replaced")

    def _on_open(self) -> None:
        row = self._caret_row()
        if row is None or self._open_handler is None or not self._open.isEnabled():
            return
        if isinstance(row, ts.DialogueRow):
            if not row.sites:
                return
            self._open_handler(min(row.sites))
            return
        self._open_handler(row.file_offset)

    def _on_mode_changed(self, label: str) -> None:
        self._mode = next(
            (identifier for identifier, text in MODES if text == label), ts.SCRIPTS
        )
        self._caret = ""
        self.refresh()

    def _on_family_changed(self, _position: int) -> None:
        self._family = self._families.currentText()
        self._caret = ""
        self.refresh()

    def _report(self, text: str) -> None:
        self._message.setText(text)

    def _publish_selection(self, context: InspectorContext | None) -> None:
        if self._selection_handler is not None:
            self._selection_handler(context)

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
            self._surface = ts.load_text_surface(
                session.rom_path,
                session.catalog,
                session.identification,
                session.profile,
                session.base_image,
            )
        except ts.TextSurfaceError as exc:
            self._surface = None
            self._problem = str(exc)


def _key(row) -> str:
    """What one row is called while the caret survives a re-render."""
    return row.identity


def _identity(key: str):
    """The SDK's own `TextIdentity` for one row's stable key."""
    from tools.webfoot.formats.text_tables import TextIdentity

    return TextIdentity(int(key.split(":")[1]))
