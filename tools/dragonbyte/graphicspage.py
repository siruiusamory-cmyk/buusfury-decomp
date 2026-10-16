"""The Graphics destination's page: sprites, payloads, appearances and the palette.

Five modes over one centre table, and the one editable relation on any of them is
an object-palette entry. Everything else states what the image holds and offers no
edit, with its reason, because a row that implies an edit the product cannot make
is worse than a row that is absent.

**One edit path, and it is the shell's `apply_edit`.** A recolour commits under the
graphics target, so one ``Ctrl+Z`` returns it and the ROM surface, which reads the
same journal, moves with it. The page states the shared-consumer disclosure for the
entry it is about to change BEFORE the change: the palette is one global table, so
the consumers are the whole risk.

**The palette counts have a corpus and the page says which.** A consumer count read
off `ActorSprites.palette_users` covers the decoded actor-sprite graphics only; map
tilesets, portraits, UI, HUD and font tiles are not in it. A row therefore reads
"0 of N decoded actor-sprite graphics; consumers outside ... are not counted and
not excluded", never a bare zero.

**No per-sprite palette and no bank label.** Which palette bank a sprite uses is
not decoded anywhere in this project, so the page shows one table and names no bank.

**The read costs seconds, so it happens once, on a worker.** Building the corpus is
the expensive half of this destination; the page keeps the event loop and states
that it is loading until the answer lands.
"""

from __future__ import annotations

import re

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal
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

from . import graphicsurface as gs, theme
from .graphicsedits import GRAPHICS_TARGET, read as read_palette
from .inspector import SUPPORT_ROLES, InspectorContext
from .journal import EditKind
from .romsurface import PendingBytes
from .session import Session
from .tablemodel import RowsModel

#: Mode id -> the label the switch shows, in the order the switch offers them.
MODES: tuple[tuple[str, str], ...] = tuple(
    (mode, gs.MODE_LABELS[mode]) for mode in gs.MODES
)

_SPRITE_HEADERS = (
    "Identity",
    "Slot",
    "Animations",
    "Payloads",
    "File offset",
    "Support",
)
_PAYLOAD_HEADERS = (
    "Identity",
    "Size",
    "Depth",
    "Packed",
    "Frames",
    "Characters",
    "Support",
)
_APPEARANCE_HEADERS = (
    "Index",
    "Text index",
    "Description",
    "Sprite id",
    "Portrait slot",
    "Stat index",
    "File offset",
    "Support",
)
_PALETTE_HEADERS = (
    "Entry",
    "Canonical",
    "Raw word",
    "Authored",
    "Consumers",
    "Support",
)
_OTHER_HEADERS = ("System", "Status", "Reason", "Evidence")

#: What the palette mode says when it cannot offer the edit, one sentence per case.
_NO_PROJECT = "Open a project to recolour an object-palette entry."
_PALETTE_TRANSPARENT = (
    "Entry 0 is the SDK's declared transparent index, so a recolour of it cannot "
    "change a colour any actor sprite draws. It is shown and not offered."
)

#: The one sentence the payload mode carries about why a pixel edit is not here,
#: in the SDK's own measured terms rather than as a policy statement.
_NO_PIXEL_EDITOR = (
    "A pixel edit is not offered here. The SDK's own write path for a visible "
    "change is the palette entry: a payload re-encode has to re-compress and "
    "usually cannot fit its original container, while a recolour is an exact "
    "two-byte write. An authored payload is a PNG in the project's asset tree "
    "rather than a project document, so it is not a payload the one journal writes."
)


def _support_cell(word: str) -> str:
    """A support state as glyph plus word, the form every surface renders."""
    return f"{theme.status_glyph(SUPPORT_ROLES[word])} {word}"


def _parse_rgb(text: str) -> tuple[int, int, int] | None:
    """One RGB triple as a person types it: ``r, g, b``, each channel 0..255.

    Deliberately one form. A hex colour, a percentage or a packed GBA word would
    each be a second way to say the same thing, and the SDK owns the word.
    """
    parts = [part for part in re.split(r"[,\s]+", text.strip()) if part]
    if len(parts) != 3:
        return None
    channels: list[int] = []
    for part in parts:
        if not part.isdigit():
            return None
        value = int(part, 10)
        if not 0 <= value <= 255:
            return None
        channels.append(value)
    return (channels[0], channels[1], channels[2])


def _rgb_text(rgb: tuple[int, int, int]) -> str:
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"


class _SurfaceSignals(QObject):
    """The worker's one answer, delivered on the thread that owns the page."""

    finished = Signal(int, object, str)


class _SurfaceTask(QRunnable):
    """Read this image's graphics records off the UI thread.

    `docs/desktop-ui.md` forbids blocking the UI thread for a bulk decode, and the
    actor-sprite corpus is seconds of work. A failure becomes the stated reason
    rather than a silent thread death that would leave the page loading forever.
    """

    def __init__(self, identification, profile, image: bytes, token: int, signals):
        super().__init__()
        self.signals = signals
        self._identification = identification
        self._profile = profile
        self._image = image
        self._token = token

    def run(self) -> None:
        try:
            surface = gs.load_graphics_surface(
                self._identification, self._profile, self._image
            )
            problem = ""
        except Exception as exc:  # a worker boundary: report, never die silently
            surface, problem = None, f"these graphics records could not be read: {exc}"
        try:
            self.signals.finished.emit(self._token, surface, problem)
        except RuntimeError:
            # The page was destroyed while this read ran.
            pass


class GraphicsPage(QWidget):
    """The Graphics destination's centre page."""

    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("graphicsPage")
        self._session = session
        self._edit_handler = None
        self._open_handler = None
        self._selection_handler = None
        self._surface: gs.GraphicsSurface | None = None
        self._surface_for = None
        self._problem = ""
        self._surface_requested = False
        self._surface_loading = False
        self._surface_request = 0
        self._surface_signals = _SurfaceSignals(self)
        self._surface_tasks: dict[int, _SurfaceTask] = {}
        self._pool = QThreadPool.globalInstance()
        self._rows: tuple = ()
        self._caret = ""
        self._mode = gs.SPRITES
        self._applying = False

        self._modes = QComboBox()
        self._modes.setObjectName("graphicsModeSwitch")
        self._modes.addItems([label for _identifier, label in MODES])
        self._modes.setAccessibleName("Graphics view")

        self._model = RowsModel(self)
        self._table = QTableView()
        self._table.setObjectName("graphicsTable")
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.setWordWrap(False)

        self._identity_line = QLabel()
        self._identity_line.setObjectName("graphicsIdentityLine")
        self._identity_line.setProperty("dbzRole", "hint")
        self._identity_line.setWordWrap(True)

        self._summary = QLabel()
        self._summary.setProperty("dbzRole", "hint")
        self._summary.setWordWrap(True)

        #: The palette editor: the entry it would change, the colour as typed, and
        #: the one Apply. It is the only editable control on this page.
        self._entry = QLabel()
        self._entry.setObjectName("graphicsPaletteEntry")
        self._entry.setAccessibleName("Palette entry")
        self._swatch = QLabel()
        self._swatch.setObjectName("graphicsPaletteSwatch")
        self._value = QLineEdit()
        self._value.setObjectName("graphicsPaletteValue")
        self._value.setAccessibleName("Palette colour, red green blue")
        self._value.setPlaceholderText("r, g, b")
        self._apply = QPushButton("Apply")
        self._open = QPushButton("Open bytes")
        self._message = QLabel()
        self._message.setProperty("dbzRole", "hint")
        self._message.setWordWrap(True)
        self._editor = QWidget()
        self._editor.setObjectName("graphicsPaletteEditor")

        editor_row = QHBoxLayout(self._editor)
        editor_row.setContentsMargins(0, 0, 0, 0)
        editor_row.setSpacing(theme.SPACE_SM)
        editor_row.addWidget(QLabel("Entry:"))
        editor_row.addWidget(self._entry)
        editor_row.addWidget(self._swatch)
        editor_row.addWidget(QLabel("Colour:"))
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
        layout.addWidget(self._identity_line)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._editor)
        layout.addWidget(self._detail)
        layout.addWidget(self._message)

        self._modes.currentTextChanged.connect(self._on_mode_changed)
        self._value.returnPressed.connect(self._on_apply)
        self._apply.clicked.connect(self._on_apply)
        self._open.clicked.connect(self._on_open)
        self._table.selectionModel().currentRowChanged.connect(self._on_row_changed)
        self._surface_signals.finished.connect(self._surface_ready)

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
        """The byte effect of this destination's pending palette edits.

        The shared `PendingBytes` contract rather than a bare mapping, because the
        ROM surface has one question and a partial answer must travel with the
        reason it is partial. A recolour is an exact two-byte write at the entry's
        own offset, so the mapping is a real file range; with no project, or with
        the corpus still being read, the reason is stated and the mapping is empty.
        """
        if self._session.project is None:
            return PendingBytes()
        surface = self._surface
        if surface is None:
            return PendingBytes(
                problem=self._problem or "the graphics records have not been read yet"
            )
        try:
            return PendingBytes(surface.pending_bytes(self._session.project))
        except Exception as exc:  # noqa: BLE001 - the reason is kept, not dropped
            return PendingBytes(
                problem=f"the pending palette bytes could not be stated: {exc}"
            )

    # -- rendering ------------------------------------------------------------

    def refresh(self) -> None:
        """Re-render from the session. The shell calls this after every change."""
        if self._applying:
            return
        self._ensure_surface()
        if self._surface is None:
            self._render_unavailable()
            return
        if self._mode == gs.PAYLOADS:
            self._render_payloads()
        elif self._mode == gs.APPEARANCES:
            self._render_appearances()
        elif self._mode == gs.PALETTE:
            self._render_palette()
        elif self._mode == gs.OTHER:
            self._render_other()
        else:
            self._render_sprites()

    def _ensure_surface(self) -> None:
        """Start the one read of this image's graphics records, on a worker."""
        session = self._session
        if (
            session.base_image is None
            or session.profile is None
            or session.identification is None
        ):
            self._surface = None
            self._surface_for = None
            self._problem = ""
            return
        if self._surface_requested and self._surface_for == session.identification:
            return
        self._surface_requested = True
        self._surface_for = session.identification
        self._surface_request += 1
        self._surface = None
        self._problem = "the graphics records are still loading"
        self._surface_loading = True
        task = _SurfaceTask(
            session.identification,
            session.profile,
            session.base_image,
            self._surface_request,
            self._surface_signals,
        )
        self._surface_tasks[self._surface_request] = task
        self._pool.start(task)

    def _surface_ready(self, token: int, surface, problem: str) -> None:
        """The worker's answer, if it is still the answer for the open image."""
        self._surface_tasks.pop(token, None)
        if token != self._surface_request:
            return
        self._surface = surface
        self._problem = problem
        self._surface_loading = False
        self.refresh()

    # -- the five modes -------------------------------------------------------

    def _render_sprites(self) -> None:
        rows = self._surface.character_rows()
        self._rows = rows
        self._model.set_rows(
            _SPRITE_HEADERS, tuple(self._sprite_cells(row) for row in rows)
        )
        self._identity_line.setText(gs.VIEW_LINES[gs.SPRITES])
        self._summary.setText(self._surface.sprite_summary())
        self._message.setText(self._surface.sprites_problem)
        self._editor.setVisible(False)
        self._select_caret()
        self._render_editor()

    def _render_payloads(self) -> None:
        rows = self._surface.payload_rows()
        self._rows = rows
        self._model.set_rows(
            _PAYLOAD_HEADERS, tuple(self._payload_cells(row) for row in rows)
        )
        self._identity_line.setText(gs.VIEW_LINES[gs.PAYLOADS])
        self._summary.setText(self._surface.payload_summary())
        self._message.setText(
            self._surface.sprites_problem or _NO_PIXEL_EDITOR
        )
        self._editor.setVisible(False)
        self._select_caret()
        self._render_editor()

    def _render_appearances(self) -> None:
        rows = self._surface.appearance_rows()
        self._rows = rows
        self._model.set_rows(
            _APPEARANCE_HEADERS, tuple(self._appearance_cells(row) for row in rows)
        )
        self._identity_line.setText(gs.VIEW_LINES[gs.APPEARANCES])
        self._summary.setText(self._surface.appearance_summary())
        self._message.setText(self._surface.appearances_problem)
        self._editor.setVisible(False)
        self._select_caret()
        self._render_editor()

    def _render_palette(self) -> None:
        rows = self._surface.palette_rows()
        self._rows = rows
        self._model.set_rows(
            _PALETTE_HEADERS, tuple(self._palette_cells(row) for row in rows)
        )
        self._identity_line.setText(
            f"{gs.VIEW_LINES[gs.PALETTE]} {self._surface.palette_identity_line()}"
        )
        self._summary.setText(
            self._surface.palette_summary(self._session.project)
        )
        self._message.setText(
            self._surface.sprites_problem
            or (
                _NO_PROJECT
                if self._session.project is None
                else ""
            )
        )
        self._editor.setVisible(True)
        self._select_caret()
        self._render_editor()

    def _render_other(self) -> None:
        rows = self._surface.other_rows()
        self._rows = rows
        self._model.set_rows(
            _OTHER_HEADERS, tuple(self._other_cells(row) for row in rows)
        )
        self._identity_line.setText(gs.VIEW_LINES[gs.OTHER])
        self._summary.setText(
            f"Other graphics systems: {len(rows)} with no editor in this build"
        )
        self._message.setText("")
        self._editor.setVisible(False)
        self._select_caret()
        self._render_editor()

    def _render_unavailable(self) -> None:
        """Nothing to show: the page says which of the two reasons it is."""
        self._rows = ()
        self._model.set_rows(_SPRITE_HEADERS, ())
        self._identity_line.clear()
        self._summary.setText("")
        self._detail.clear()
        self._entry.clear()
        self._swatch.clear()
        self._open.setEnabled(False)
        self._apply.setEnabled(False)
        self._editor.setVisible(False)
        if self._surface_loading:
            self._message.setText(self._problem)
        else:
            self._message.setText(
                self._problem
                or "Open a ROM image to see its sprites, payloads, appearances and "
                "object palette."
            )
        self._publish_selection(None)

    # -- cells ----------------------------------------------------------------

    def _sprite_cells(self, row: gs.CharacterRow) -> tuple[str, ...]:
        return (
            row.identity,
            f"{row.index:04d}",
            f"{row.animations}",
            f"{row.payloads}",
            f"0x{row.file_offset:06X}",
            _support_cell("Read-only"),
        )

    def _payload_cells(self, row: gs.PayloadRow) -> tuple[str, ...]:
        return (
            row.identity,
            f"{row.width}x{row.height}",
            f"{row.bit_depth}bpp",
            f"{row.packed_size}",
            f"{len(row.frames)}",
            f"{len(row.characters)}",
            _support_cell("Read-only"),
        )

    def _appearance_cells(self, row: gs.AppearanceRow) -> tuple[str, ...]:
        return (
            f"{row.index:03d}",
            f"text:{row.text_index:04d}",
            f"text:{row.description_index:04d}",
            f"{row.sprite_id}",
            f"{row.portrait_slot}",
            f"{row.stat_index}",
            f"0x{row.file_offset:06X}",
            _support_cell("Read-only"),
        )

    def _palette_cells(self, row: gs.PaletteRow) -> tuple[str, ...]:
        authored = self._authored_rgb(row.index)
        return (
            f"{row.index:03d}",
            _rgb_text(row.rgb),
            f"0x{row.raw:04X}",
            _rgb_text(authored) if authored is not None else "not authored",
            row.consumer_text,
            _support_cell("Editable" if row.editable else "Not supported yet"),
        )

    def _other_cells(self, row: gs.OtherRow) -> tuple[str, ...]:
        return (row.name, row.status, row.reason, row.evidence)

    def _authored_rgb(self, index: int) -> tuple[int, int, int] | None:
        """The colour the open project authors for one entry, if it authors one."""
        project = self._session.project
        if project is None:
            return None
        return project.graphics_overrides.palette.get(index)

    # -- the editor -----------------------------------------------------------

    def _render_editor(self) -> None:
        row = self._caret_row()
        if isinstance(row, gs.PaletteRow):
            self._render_palette_editor(row)
        else:
            self._clear_editor()
            self._publish_selection(self._context(row))

    def _render_palette_editor(self, row: gs.PaletteRow) -> None:
        """The one editor, and the disclosure that must precede its edit.

        This row's own state is the LAST word on both the message and the enabled
        state, after everything that could set either. The defect this closes was
        measured: moving the caret from the unsupported entry to an editable one
        left the previous row's refusal on the page, so the reason shown belonged
        to a row nobody had selected.
        """
        self._editor.setVisible(True)
        self._clear_value()
        authored = self._authored_rgb(row.index)
        effective = authored if authored is not None else row.rgb
        self._entry.setText(f"{row.index:03d}")
        self._swatch.setText(
            f"canonical {_rgb_text(row.rgb)}"
            + (f" | authored {_rgb_text(authored)}" if authored is not None else "")
        )
        self._value.setToolTip(
            f"Object palette entry {row.index:03d}, currently {_rgb_text(effective)}. "
            "Type three channels, 0..255."
        )
        self._open.setEnabled(True)
        self._open.setToolTip(
            f"Show the two bytes of palette entry {row.index:03d} at file offset "
            f"0x{self._palette_offset(row.index):06X} in the ROM destination"
        )
        disclosure = self._surface.palette_disclosure(row.index)
        owners = self._surface.owners_of(row.index)
        self._detail.setText(
            f"{self._surface.palette_identity_line()} | entry {row.index:03d} | raw "
            f"word 0x{row.raw:04X} | {disclosure}"
            + (
                " Characters affected, through those graphics: "
                + ", ".join(owners[:8])
                + (f" and {len(owners) - 8} more" if len(owners) > 8 else "")
                if owners
                else ""
            )
        )
        self._publish_selection(self._context(row))

        if self._surface.sprites_problem:
            self._apply.setEnabled(False)
            self._value.setEnabled(False)
            self._report(self._surface.sprites_problem)
            return
        if not row.editable:
            self._apply.setEnabled(False)
            self._apply.setToolTip(row.unsupported_reason)
            self._value.setEnabled(False)
            self._value.setPlaceholderText(row.unsupported_reason)
            self._report(_PALETTE_TRANSPARENT)
            return
        self._value.setEnabled(True)
        self._value.setPlaceholderText("r, g, b")
        self._value.setText(_rgb_channels(effective))
        project = self._session.project
        self._apply.setEnabled(project is not None)
        self._apply.setToolTip(
            f"Recolour entry {row.index:03d} for every graphic that uses it"
            if project is not None
            else _NO_PROJECT
        )
        self._report("" if project is not None else _NO_PROJECT)

    def _clear_value(self) -> None:
        """Empty the field. It decides nothing about whether an edit is offered."""
        self._value.clear()

    def _clear_editor(self) -> None:
        """No row is selected, so nothing here is offered: no field, no buttons."""
        self._clear_value()
        self._entry.clear()
        self._swatch.clear()
        self._apply.setEnabled(False)
        self._open.setEnabled(False)
        self._detail.clear()

    # -- selection ------------------------------------------------------------

    def _select_caret(self) -> None:
        if not self._rows:
            self._caret = ""
            return
        keys = [_key(row) for row in self._rows]
        if self._caret not in keys:
            self._caret = keys[0]
        position = keys.index(self._caret)
        self._select_row(position)

    def _select_row(self, position: int) -> None:
        selection = self._table.selectionModel()
        selection.blockSignals(True)
        self._table.selectRow(position)
        selection.setCurrentIndex(
            self._model.index(position, 0),
            selection.SelectionFlag.ClearAndSelect
            | selection.SelectionFlag.Rows,
        )
        selection.blockSignals(False)

    def _on_row_changed(self, current, _previous) -> None:
        if not current.isValid():
            return
        row = self._rows[current.row()]
        self._caret = _key(row)
        self._render_editor()

    def _caret_row(self):
        for row in self._rows:
            if _key(row) == self._caret:
                return row
        return None

    def _palette_offset(self, index: int) -> int:
        return self._surface.palette_address + index * 2

    def _context(self, row) -> InspectorContext | None:
        """What the shared inspector says about one row, in its three tiers."""
        if isinstance(row, gs.CharacterRow):
            return InspectorContext(
                friendly=f"Character slot {row.index:04d}",
                stable=row.identity,
                support="Read-only",
                detail=f"{row.animations} animation(s), {row.payloads} payload(s). "
                f"{row.note}.",
            )
        if isinstance(row, gs.PayloadRow):
            return InspectorContext(
                friendly=f"Payload {row.index:04d}",
                stable=row.identity,
                support="Read-only",
                detail=f"{row.width}x{row.height} at {row.bit_depth}bpp, "
                f"{row.packed_size} packed bytes. {row.disclosure}. {row.note}.",
            )
        if isinstance(row, gs.AppearanceRow):
            return InspectorContext(
                friendly=f"Appearance {row.index:03d}",
                stable=f"appearance:{row.index:03d}",
                support="Read-only",
                detail=f"text {row.text_index}, sprite id {row.sprite_id}, stat "
                f"{row.stat_index}. {row.note}.",
            )
        if isinstance(row, gs.PaletteRow):
            return InspectorContext(
                friendly=f"Palette entry {row.index:03d}",
                stable=f"palette_entry:{row.index:03d}",
                support="Editable" if row.editable else "Not supported yet",
                detail=f"{row.consumer_text}. "
                + (row.unsupported_reason + "." if row.unsupported_reason else ""),
            )
        if isinstance(row, gs.OtherRow):
            return InspectorContext(
                friendly=row.name,
                stable=row.name,
                support="Not supported yet",
                detail=f"{row.status}. {row.reason} ({row.evidence})",
            )
        return None

    # -- actions --------------------------------------------------------------

    def _on_apply(self) -> None:
        row = self._caret_row()
        if not isinstance(row, gs.PaletteRow):
            self._report("This row has no edit.")
            return
        if self._session.project is None:
            self._report(_NO_PROJECT)
            return
        if not row.editable:
            self._report(row.unsupported_reason)
            return
        rgb = _parse_rgb(self._value.text())
        if rgb is None:
            self._report(
                "A colour is three channels, 0..255, as in 31, 0, 0."
            )
            return
        problem, changes, claimed = self._surface.plan(row.index, rgb)
        if problem:
            self._report(problem)
            return
        if not changes:
            self._report(f"Entry {row.index:03d} is already that colour.")
            return
        after = read_palette(self._session.project)
        revision = self._session.journal.current_revision
        self._applying = True
        try:
            self._edit_handler(
                kind=EditKind.SEMANTIC,
                target=GRAPHICS_TARGET,
                after=_with_palette(after, row.index, rgb),
                claimed=claimed,
                reason=f"palette edit: entry {row.index:03d}",
            )
        finally:
            self._applying = False
        self.refresh()
        if self._session.journal.current_revision != revision:
            self._caret = _key(row)
            self._select_caret()
            self._report(f"Entry {row.index:03d} recoloured to {_rgb_text(rgb)}")

    def _on_open(self) -> None:
        row = self._caret_row()
        if row is None or self._open_handler is None or not self._open.isEnabled():
            return
        if isinstance(row, gs.PaletteRow):
            self._open_handler(self._palette_offset(row.index))
            return
        if isinstance(row, (gs.PayloadRow, gs.AppearanceRow)):
            self._open_handler(row.file_offset)

    def _on_mode_changed(self, label: str) -> None:
        self._mode = next(
            (identifier for identifier, text in MODES if text == label), gs.SPRITES
        )
        self._caret = ""
        self.refresh()

    def _report(self, text: str) -> None:
        self._message.setText(text)

    def _publish_selection(self, context: InspectorContext | None) -> None:
        if self._selection_handler is not None:
            self._selection_handler(context)


def _with_palette(payload, index: int, rgb: tuple[int, int, int]):
    """The adapter payload with one entry authored, leaving every other alone."""
    from dataclasses import replace

    return replace(payload, palette={**payload.palette, index: rgb})


def _rgb_channels(rgb: tuple[int, int, int]) -> str:
    return f"{rgb[0]}, {rgb[1]}, {rgb[2]}"


def _key(row) -> str:
    """What one row is called while the caret survives a re-render."""
    if isinstance(row, gs.PaletteRow):
        return f"palette:{row.index:03d}"
    if isinstance(row, gs.AppearanceRow):
        return f"appearance:{row.index:03d}"
    if isinstance(row, gs.OtherRow):
        return row.name
    return row.identity
