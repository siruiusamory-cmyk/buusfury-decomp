"""MAP-WARP-WORKBENCH-001 - the Maps editor's Warps mode.

A **thin client** over the transition authority (`tools.webfoot.map_transitions`),
which is the already-merged, runtime-proven path: the same `TransitionIdentity`,
the same `set_destination`/`set_arrival`/`set_facing`, the same
`maps/transitions.toml` document and the same production build. Nothing here
serializes a record, writes a ROM, computes a file offset or masks a byte; every
value on screen comes out of the SDK, and every edit goes back through it.

What it does: pick a map, see its existing connections, select one, and retarget
it - where it leads, where the player arrives, and which way they face - then
Apply, which is one semantic project write. The normal Validate -> Build path
consumes it exactly as it consumes any other authored content.

What it deliberately will not do:

* **No new transitions.** The surface edits records the corpus already holds; the
  array, its count and its pointer are never touched (`MapTransitions.changes`
  yields records only, and the count and pointer are not this module's to write).
* **No 169-class retarget.** A 169-class record stores its arrival as a
  scene-relative delta rather than a point, so the toolkit cannot state where the
  player lands on a different map. The whole record is read-only, with the reason
  on screen, rather than a destination edit that leaves a delta pointing into the
  old scene.
* **No raw field.** The facing control offers Unchanged / South / North / West /
  East - never `+0x10` and never its gate bits. "Unchanged" means "author no
  facing", which is the authority's own no-override state; a record whose low bits
  are `0x02` therefore reads Unchanged, not West.

The one rule that matters most (WORKBENCH-001): every slot that calls the SDK
catches the SDK exception **family parent** - `MapTransitionsError` for the
authority, `MapTransitionError` for the codec - plus `ProjectError` and `OSError`
for the project read and write underneath, and `MapBrowserError` /
`MapGraphicsError` for the map labels. A leaf-only `except` would let a real
refusal escape to a console the GUI does not have, and the click would simply
look dead.

Project I/O is bounded on purpose (CQA-07): the corpus and the map labels are read
once per session, the project's authored edits once per project mutation, and
selecting a map, a row or a field reads nothing at all.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QUndoCommand, QUndoStack
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from tools.webfoot import map_transitions as mt
from tools.webfoot import map_view as mv
from tools.webfoot.formats.map_graphics import MapGraphicsError
from tools.webfoot.formats.map_transitions import (
    ARRIVAL_UNSET_MINIMUM,
    FACING_NAMES,
    MapTransitionError,
    TransitionArrival,
    TransitionFacing,
    TransitionRegion,
)
from tools.webfoot.maps import MapIdentity
from tools.webfoot.project import ProjectError

from . import theme
from .session import Session
from .widgets import PanelHeader, StateChip, TechnicalLabel

#: Every failure family a slot on this surface can meet. `MapTransitionsError` is
#: the authority's parent (`TransitionFieldError`, `UnknownTransitionError`,
#: `TransitionProfileError`), `MapTransitionError` is the codec's, and the rest are
#: the project, filesystem and map-label families underneath them - none of which
#: shares a parent with the others, so each is named.
_WARP_ERRORS = (
    mt.MapTransitionsError,
    MapTransitionError,
    ProjectError,
    mv.MapBrowserError,
    MapGraphicsError,
    OSError,
)

#: What reading the *session's* image can add on top of that. The corpus reader
#: resolves the profile's own tables by attribute, so a profile object that is not
#: a `RomProfile` surfaces as `AttributeError`/`TypeError` rather than as a refusal.
#: At a session boundary that is a read-only state like any other ("this profile
#: cannot describe its connections") and is stated on screen; the command slots keep
#: the narrower tuple above, so a programming error in a slot is still loud rather
#: than dressed up as an SDK refusal - the same split `map_browser_tab` makes
#: between `_STRUCTURE_ERRORS` and `_STRUCTURE_VIEW_ERRORS`.
_WARP_SESSION_ERRORS = _WARP_ERRORS + (AttributeError, TypeError)

#: The columns of the connection list, named so nothing indexes by a bare integer.
_COLUMNS = ("#", "Leads to", "Trigger region", "Arrival", "Facing", "State")

#: The row states. "Saved" is the project's committed edit, "Staged" is this
#: session's uncommitted one, "Read-only" is a record the authority will not
#: retarget (or a surface with no project to author into).
_STATE_RETAIL = "Retail"
_STATE_SAVED = "Saved"
_STATE_STAGED = "Staged"
_STATE_READ_ONLY = "Read-only"

#: Each state's colour-and-glyph role. Read-only is a state, not an error, so it
#: takes the muted `readonly` role rather than the danger one, and the two
#: unedited states stay neutral: the chip's emphasis is spent on work in progress.
_STATE_ROLES = {
    _STATE_RETAIL: "neutral",
    _STATE_SAVED: "saved",
    _STATE_STAGED: "pending",
    _STATE_READ_ONLY: "readonly",
}

#: The facing control's "author no facing" choice. It is NOT a direction: a zero
#: high nibble means the record states no arrival facing at all (`TransitionFacing`),
#: and the low bits are the door gate, which this surface never shows or edits.
_UNCHANGED = "Unchanged"

#: Why a 169-class record cannot be retargeted, in product wording. The measured
#: reason is `formats.map_transitions.TransitionRecord.has_raw_arrival_pair`: the
#: 169 class reads `+0x14`/`+0x16` as a delta from its own region and adds the scene
#: origin, so the pair is not an arrival point and no project value can state one.
_NOT_RETARGETABLE = (
    "169-class connection: its stored arrival is a scene-relative delta rather "
    "than a point, so the toolkit cannot safely retarget it. Read-only in this pass."
)

_UNRESOLVED_DESTINATION = (
    "This record's destination key resolves to no map in this image, so the "
    "toolkit will not retarget it."
)

_NO_PROJECT = (
    "Open a Webfoot project to author a connection; a transition edit is stored "
    "in maps/transitions.toml, never in a ROM."
)

_NO_IMAGE = "Open a game image to read its connections."


class StageTransitionCommand(QUndoCommand):
    """One staged transition edit: the whole draft before and after.

    Staging is the gesture, so one command covers a destination, an arrival, a
    facing, or any combination the form produced in one step - which is what makes
    a combined retarget one undo entry rather than three. `redo()` re-applies the
    after-state, so the widget's own change and the command cannot drift.
    """

    def __init__(self, tab: "WarpTab", identity, before, after) -> None:
        super().__init__(_command_text(identity, before, after))
        self._tab = tab
        self._identity = identity
        self._before = before
        self._after = after

    def undo(self) -> None:  # noqa: D102 - Qt naming
        self._tab._restore_draft(self._identity, self._before)

    def redo(self) -> None:  # noqa: D102 - Qt naming
        self._tab._restore_draft(self._identity, self._after)


def _draft_fields(before, after) -> tuple[str, ...]:
    """Which fields a draft changed, named the way the product names them."""
    names: list[str] = []
    for name in ("destination", "arrival", "facing"):
        old = getattr(before, name, None) if before is not None else None
        new = getattr(after, name, None) if after is not None else None
        if old != new:
            names.append(name)
    return tuple(names)


def _command_text(identity, before, after) -> str:
    """A one-line undo label naming what changed, in product language."""
    if after is None:
        return f"Discard the staged edit on {identity}"
    names = _draft_fields(before, after)
    if not names:
        return f"Edit {identity}"
    if len(names) == 1:
        return f"Change the {names[0]} of {identity}"
    return f"Retarget {identity} ({', '.join(names)})"


def _facing_direction(raw: "int | None") -> "int | None":
    """The arrival direction a stored ``+0x10`` byte states, through the codec.

    The whole byte is decoded by `TransitionFacing`, so the shift and the
    "a non-zero high nibble only" rule live in one place - the codec - and this
    surface never reads a facing out of the low bits.
    """
    if raw is None:
        return None
    return TransitionFacing(raw=raw).arrival_direction


def _field_label(caption: str) -> QLabel:
    label = QLabel(caption)
    label.setProperty("dbzRole", "fieldLabel")
    label.setWordWrap(False)
    return label


class WarpTab(QWidget):
    """The Maps editor's Warps mode: this map's connections, and their edits."""

    #: A semantic project edit landed; the shell re-arms validation and build.
    projectChanged = Signal()
    #: The compact one-line status, forwarded to the shell's status bar.
    statusChanged = Signal(str)
    #: The staged-edit count changed; kept for symmetry with the other modes.
    dirtyChanged = Signal()

    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session

        # -- the source-map context ------------------------------------------
        self._map_select = QComboBox()
        self._map_select.setAccessibleName("Map")
        self._map_select.setToolTip("Which map's connections to edit")
        self._map_select.currentIndexChanged.connect(self._on_source_map_changed)
        self._map_support = QLabel()
        self._map_support.setProperty("dbzRole", "hint")
        self._map_support.setWordWrap(True)

        # -- the connection list ---------------------------------------------
        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(theme.ROW_HEIGHT)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.itemSelectionChanged.connect(self._on_row_selected)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        # -- the selected connection's editor ---------------------------------
        self._identity = TechnicalLabel("Select a connection to edit it.")
        self._destination = QComboBox()
        self._destination.setAccessibleName("Destination map")
        self._destination.setToolTip("Where this connection leads")
        self._destination.currentIndexChanged.connect(self._on_destination_changed)
        self._arrival_x = QSpinBox()
        self._arrival_x.setAccessibleName("Arrival X")
        self._arrival_y = QSpinBox()
        self._arrival_y.setAccessibleName("Arrival Y")
        for spin in (self._arrival_x, self._arrival_y):
            # The coordinate domain is the arrival codec's own: everything below
            # the measured "no authored arrival" sentinel. A point outside the
            # destination's walkable extent is refused by the authority with its
            # own message rather than clamped here.
            spin.setRange(0, ARRIVAL_UNSET_MINIMUM - 1)
            spin.setKeyboardTracking(False)
            spin.editingFinished.connect(self._on_arrival_changed)
        self._arrival_hint = QLabel()
        self._arrival_hint.setProperty("dbzRole", "hint")
        self._arrival_hint.setWordWrap(True)
        arrival_row = QHBoxLayout()
        arrival_row.setContentsMargins(0, 0, 0, 0)
        arrival_row.setSpacing(theme.SPACE_SM)
        arrival_row.addWidget(QLabel("X"))
        arrival_row.addWidget(self._arrival_x)
        arrival_row.addWidget(QLabel("Y"))
        arrival_row.addWidget(self._arrival_y)
        arrival_row.addWidget(self._arrival_hint, 1)
        arrival_widget = QWidget()
        arrival_widget.setLayout(arrival_row)

        self._facing = QComboBox()
        self._facing.setAccessibleName("Facing")
        self._facing.setToolTip(
            "The direction the player is turned on arrival. Unchanged authors no "
            "facing, so the record keeps its own."
        )
        self._facing.addItem(_UNCHANGED, None)
        for direction, name in sorted(FACING_NAMES.items()):
            self._facing.addItem(name, direction)
        self._facing.currentIndexChanged.connect(self._on_facing_changed)
        self._facing_hint = QLabel()
        self._facing_hint.setProperty("dbzRole", "hint")
        self._facing_hint.setWordWrap(True)
        facing_row = QHBoxLayout()
        facing_row.setContentsMargins(0, 0, 0, 0)
        facing_row.setSpacing(theme.SPACE_SM)
        facing_row.addWidget(self._facing)
        facing_row.addWidget(self._facing_hint, 1)
        facing_widget = QWidget()
        facing_widget.setLayout(facing_row)

        self._region_label = QLabel("\u2014")
        self._region_label.setProperty("dbzRole", "hint")
        self._region_label.setWordWrap(True)
        self._state_chip = StateChip("No connection selected", "neutral", plain=True)
        self._reason = QLabel()
        self._reason.setProperty("dbzRole", "hint")
        self._reason.setWordWrap(True)

        self._apply_button = QPushButton("Apply to project")
        self._apply_button.setProperty("dbzRole", "primary")
        self._apply_button.setToolTip(
            "Write every staged connection edit into the project's "
            "maps/transitions.toml. The source ROM is never modified; Validate and "
            "Build then consume the edit like any other authored content."
        )
        self._apply_button.clicked.connect(self.apply_to_project)
        self._revert_button = QPushButton("Revert")
        self._revert_button.setToolTip(
            "Discard this connection's staged change. With nothing staged, remove "
            "its saved project edit so the retail connection applies again."
        )
        self._revert_button.clicked.connect(self.revert_selected)
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(theme.SPACE_SM)
        actions.addWidget(self._apply_button)
        actions.addWidget(self._revert_button)
        actions.addStretch(1)

        form = QFormLayout()
        form.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM
        )
        form.setHorizontalSpacing(theme.SPACE_MD)
        form.setVerticalSpacing(theme.SPACE_XS)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.addRow(self._identity)
        form.addRow(_field_label("Leads to"), self._destination)
        form.addRow(_field_label("Arrival"), arrival_widget)
        form.addRow(_field_label("Facing"), facing_widget)
        form.addRow(_field_label("Trigger region"), self._region_label)
        form.addRow(_field_label("State"), self._state_chip)
        form.addRow(self._reason)
        form.addRow(actions)
        form_box = QWidget()
        form_box.setLayout(form)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(PanelHeader("Connections"))
        left_layout.addWidget(self._table, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(PanelHeader("Selected connection"))
        right_layout.addWidget(form_box)
        right_layout.addStretch(1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setCollapsible(0, False)
        splitter.setSizes([640, 420])
        self._splitter = splitter

        top = QWidget()
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_XS, theme.SPACE_SM, theme.SPACE_XS
        )
        top_layout.setSpacing(theme.SPACE_SM)
        top_layout.addWidget(_field_label("Map"))
        top_layout.addWidget(self._map_select)
        top_layout.addWidget(self._map_support, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(theme.SPACE_XS)
        layout.addWidget(top)
        layout.addWidget(splitter, 1)
        # This editor's one status line is held here and mirrored into the shell's
        # single status bar; drawing it here as well would state it twice.
        self._status = QLabel()
        self._status.setProperty("dbzRole", "status")
        self._status.setWordWrap(True)
        self._status.setVisible(False)

        # -- state ------------------------------------------------------------
        #: The whole-image corpus, loaded once per session (CQA-07). Selecting a
        #: map, a row or a field never re-reads it.
        self._corpus: "mt.MapTransitions | None" = None
        #: Why the corpus could not be read, when it could not.
        self._corpus_error: str | None = None
        #: Why the project's own connection document could not be read.
        self._project_error: str | None = None
        #: Source map index -> how many connections it holds. Derived in one pass
        #: over the corpus, so a label never rescans it (CQA-07).
        self._counts: dict[int, int] = {}
        #: The project's authored edits, in the SDK's own types, re-read once per
        #: project mutation - never per control.
        self._committed: dict = {}
        #: This session's uncommitted edits, keyed by identity. The undo stack is
        #: their history.
        self._staged: dict = {}
        #: Map index -> ROM-derived label, resolved once per session.
        self._labels: dict[int, str] = {}
        self._source_index: int | None = None
        self._selected = None
        #: True while the widgets are being repopulated, so a programmatic change
        #: is never mistaken for a gesture.
        self._suppress = False
        self._undo_stack = QUndoStack(self)

        self._populate_after_session_change()

    # -- public surface (used by the mode strip, the shell, tests and QA) ------

    def on_session_changed(self) -> None:
        """A different image: drop everything image-bound and re-read.

        CQA-05, second half. Staged edits, the undo history, the corpus and the
        map labels all describe the image that was open, so a true session
        replacement clears them; no project mutation does.
        """
        self._corpus = None
        self._corpus_error = None
        self._committed = {}
        self._staged = {}
        self._labels = {}
        self._selected = None
        self._source_index = None
        self._undo_stack.clear()
        self._populate_after_session_change()
        self.dirtyChanged.emit()

    def on_project_mutated(self) -> None:
        """A project mutation: re-read what the project holds, keep what is staged.

        CQA-05, first half. Another editor's Apply, a Save As or this tab's own
        Apply all arrive here. The staged edits are in-memory intents the project
        still has a place for, so they survive; only the committed picture is
        re-read - once, not per row or per control (CQA-07).
        """
        self._reload_committed()
        self._populate_rows()
        self._populate_source_labels()
        self._publish_status(self._summary_text())

    def refresh(self) -> None:
        """Re-assert the surface when the mode becomes visible."""
        if self._corpus is None and self._corpus_error is None:
            self._populate_after_session_change()
            return
        self._populate_rows()
        self._refresh_map_support()
        self._publish_status(self._summary_text())

    def restate_status(self) -> None:
        """Republish this mode's own line when the shell switches to it."""
        self._publish_status(self._summary_text())

    def status_line(self) -> str:
        return self._status.text()

    def unsaved_edit_count(self) -> int:
        """This session's uncommitted transition edits."""
        return len(self._staged)

    def undo_stack(self) -> QUndoStack:
        return self._undo_stack

    def source_map_index(self) -> int | None:
        return self._source_index

    def select_source_map(self, index: int) -> bool:
        """Show one map's connections, by map index."""
        row = self._map_select.findData(index)
        if row < 0:
            return False
        self._map_select.setCurrentIndex(row)
        return self._source_index == index

    def row_count(self) -> int:
        return self._table.rowCount()

    def row_values(self, row: int) -> tuple[str, ...]:
        """One row's displayed cells, left to right."""
        if not 0 <= row < self._table.rowCount():
            raise IndexError(f"no connection row {row}")
        return tuple(
            self._table.item(row, column).text() for column in range(len(_COLUMNS))
        )

    def select_row(self, row: int) -> bool:
        if not 0 <= row < self._table.rowCount():
            return False
        self._table.selectRow(row)
        self._table.setCurrentCell(row, 0)
        return self.selected_identity() is not None

    def selected_identity(self) -> str | None:
        return self._selected.key if self._selected is not None else None

    def selected_editable(self) -> bool:
        return self._selected is not None and self.edit_refusal() is None

    def edit_refusal(self) -> str | None:
        """Why the selected connection cannot be edited, or None."""
        return self._edit_refusal()

    def destination_choices(self) -> tuple[tuple[str, int], ...]:
        """The destination selector's vocabulary: ``(label, map index)``."""
        return tuple(
            (self._destination.itemText(row), self._destination.itemData(row))
            for row in range(self._destination.count())
        )

    def facing_choices(self) -> tuple[tuple[str, int | None], ...]:
        """The facing control's whole vocabulary: Unchanged, then the directions."""
        return tuple(
            (self._facing.itemText(row), self._facing.itemData(row))
            for row in range(self._facing.count())
        )

    def facing_choice(self) -> int | None:
        return self._facing.currentData()

    def form_state(self) -> dict:
        """The editor's current state, for tests and QA probes."""
        return {
            "identity": self.selected_identity(),
            "destination": self._destination.currentData(),
            "arrival": (self._arrival_x.value(), self._arrival_y.value()),
            "facing": self._facing.currentData(),
            "state": self._state_chip.accessibleName(),
            "reason": self.edit_refusal(),
            "editable": self.selected_editable(),
        }

    def staged_edit(self, key: str):
        """The staged draft for one ``map:NNNN/transition:NNNN`` identity, or None."""
        for identity, draft in self._staged.items():
            if identity.key == key:
                return draft
        return None

    # -- staging (the gestures) ----------------------------------------------

    def stage_destination(self, map_index: int) -> bool:
        """Point the selected connection at another map, with a safe arrival."""
        identity = self._selected
        if identity is None or self._edit_refusal() is not None:
            return False
        try:
            destination = MapIdentity(int(map_index))
        except (mt.MapTransitionsError, ValueError) as exc:
            self._refuse_stage(str(exc), identity)
            return False
        base_destination, _base_arrival, _base_facing = self._base(identity)
        facing = self.facing_choice()
        if destination == base_destination:
            # Back to where the retail record already points: the arrival returns
            # to the record's own point, and nothing is authored unless the other
            # controls ask for it.
            arrival = self._form_arrival()
            if arrival is None:
                return False
            seed = self._seed_arrival(identity, destination)
            draft = self._compose(
                identity,
                destination,
                arrival,
                facing,
                arrival_touched=seed is None or arrival != seed,
            )
            return self._stage(identity, draft)
        # A retarget always states where the player lands, and the authority's own
        # derivation is preferred over the previous destination's point.
        derived = self._derive_arrival(identity, destination)
        if derived is None:
            self._refuse_stage(
                f"{destination} has no connection back to {identity.source}, so no "
                "safe arrival can be derived. This toolkit refuses a retarget whose "
                "arrival would belong to the old destination; state the arrival "
                "explicitly, then choose the destination.",
                identity,
            )
            return False
        if facing is None:
            # The SDK's documented authoring default (not engine law): face away
            # from the nearest edge of the destination. It is chosen here and shown
            # in the control, so it is a stated default rather than a silent one.
            facing = self._default_facing(destination, derived)
        draft = self._compose(
            identity, destination, derived, facing, arrival_touched=True
        )
        return self._stage(identity, draft)

    def stage_arrival(self, x: int, y: int) -> bool:
        """Set the point the selected connection places the player at."""
        identity = self._selected
        if identity is None or self._edit_refusal() is not None:
            return False
        try:
            arrival = TransitionArrival(x=int(x), y=int(y))
        except (MapTransitionError, TypeError, ValueError) as exc:
            self._refuse_stage(str(exc), identity)
            return False
        destination = self._form_destination()
        if destination is None:
            return False
        seed = self._seed_arrival(identity, destination)
        draft = self._compose(
            identity,
            destination,
            arrival,
            self.facing_choice(),
            arrival_touched=seed is None or arrival != seed,
        )
        return self._stage(identity, draft)

    def stage_facing(self, direction: int | None) -> bool:
        """Author the direction the player is turned on arrival, or author none."""
        identity = self._selected
        if identity is None or self._edit_refusal() is not None:
            return False
        destination = self._form_destination()
        if destination is None:
            return False
        arrival = self._form_arrival()
        if arrival is None:
            return False
        seed = self._seed_arrival(identity, destination)
        draft = self._compose(
            identity,
            destination,
            arrival,
            direction,
            arrival_touched=seed is None or arrival != seed,
        )
        return self._stage(identity, draft)

    # -- apply / revert -------------------------------------------------------

    def apply_to_project(self) -> bool:
        """Commit every staged edit in one semantic project write.

        The authority validates the whole batch against the canonical image before
        anything is written (`set_transition_edits`), so a batch with one illegal
        entry writes nothing at all. A batch the project already holds is reported
        as exactly that and changes no file.
        """
        if not self._staged:
            self._publish_status("There is no staged connection edit to apply.")
            return False
        project = self._session.project_dir
        image = self._session.map_image
        profile = self._session.profile
        if project is None:
            self._report_error("Apply connection edit", _NO_PROJECT)
            return False
        if image is None or profile is None:
            self._report_error("Apply connection edit", _NO_IMAGE)
            return False
        try:
            changed = mt.set_transition_edits(project, profile, image, dict(self._staged))
        except _WARP_ERRORS as exc:
            self._report_error("Apply connection edit", str(exc))
            return False
        self._staged.clear()
        self._undo_stack.clear()
        self._reload_committed()
        self._populate_rows()
        self._populate_source_labels()
        if changed:
            self._session.project_mutated()
            self.projectChanged.emit()
            self._publish_status(
                "Applied the connection edit to maps/transitions.toml. Validate and "
                "build to consume it."
            )
        else:
            self._publish_status("The project already held exactly this connection.")
        self.dirtyChanged.emit()
        return changed

    def revert_selected(self) -> bool:
        """Put the selected connection back: un-stage, else un-author.

        With a staged edit this is the un-stage gesture, and it is itself undoable
        like any other. With nothing staged it removes the project's saved edit, so
        the retail connection applies again - the way back from an applied retarget
        without editing the project by hand.
        """
        identity = self._selected
        if identity is None:
            self._publish_status("Select a connection first.")
            return False
        if self._edit_refusal() is not None:
            self._publish_status(self._edit_refusal())
            self._refresh_form()
            return False
        if identity in self._staged:
            self._push(identity, None)
            self._publish_status(f"Discarded the staged edit on {identity}.")
            return True
        if identity not in self._committed:
            self._refresh_form()
            self._publish_status(f"{identity} has no staged or saved edit to revert.")
            return False
        project = self._session.project_dir
        if project is None:
            self._report_error("Revert connection edit", _NO_PROJECT)
            return False
        try:
            removed = mt.remove_transition_edit(project, identity)
        except _WARP_ERRORS as exc:
            self._report_error("Revert connection edit", str(exc))
            return False
        if not removed:
            self._publish_status(f"{identity} had no saved edit after all.")
            self._refresh_form()
            return False
        self._reload_committed()
        self._populate_rows()
        self._populate_source_labels()
        self._session.project_mutated()
        self.projectChanged.emit()
        self._publish_status(
            f"Removed the project's edit on {identity}; the retail connection "
            "applies again. Apply to author it once more."
        )
        self.dirtyChanged.emit()
        return True

    # -- population -----------------------------------------------------------

    def _populate_after_session_change(self) -> None:
        """Rebuild every session-bound cache and put a real map on screen."""
        self._load_corpus()
        self._load_labels()
        self._reload_committed()
        self._populate_source_maps()
        self._populate_destination_maps()
        self._populate_rows()
        self._publish_status(self._summary_text())

    def _load_corpus(self) -> None:
        image = self._session.map_image
        profile = self._session.profile
        self._corpus = None
        self._corpus_error = None
        self._counts = {}
        if image is None or profile is None:
            return
        try:
            self._corpus = mt.read_map_transitions(image, profile)
        except _WARP_SESSION_ERRORS as exc:
            self._corpus = None
            self._corpus_error = str(exc)
            return
        counts: dict[int, int] = {}
        for entry in self._corpus.entries():
            index = entry.identity.source.index
            counts[index] = counts.get(index, 0) + 1
        self._counts = counts

    def _load_labels(self) -> None:
        """The ROM-derived map labels, resolved once per session.

        A map that publishes no text keeps its ``map:NNNN`` identity, which is what
        `map_view` and the Map Browser already do; nothing is invented for it.
        """
        self._labels = {}
        image = self._session.map_image
        profile = self._session.profile
        if image is None or profile is None:
            return
        try:
            for entry in mv.read_map_index(image, profile):
                if entry.name:
                    self._labels[entry.index] = entry.name
        except _WARP_SESSION_ERRORS:
            self._labels = {}

    def _reload_committed(self) -> None:
        """Re-read the project's authored edits, once (CQA-07).

        `read_project_transition_requests` is the SDK's own conversion of the
        authored document into `AuthoredTransitionEdit` values, so this widget
        never parses a project key, a point pair or a facing byte. A document that
        cannot be read at all is a state: nothing is authorable against it until it
        is fixed, and the reason is what the surface says.
        """
        self._committed = {}
        self._project_error = None
        project = self._session.project_dir
        if project is None:
            return
        try:
            self._committed = dict(mt.read_project_transition_requests(project))
        except _WARP_ERRORS as exc:
            self._committed = {}
            self._project_error = f"The project's connection edits could not be read: {exc}"

    def _populate_source_maps(self) -> None:
        self._suppress = True
        try:
            self._map_select.clear()
            if self._corpus is None:
                self._source_index = None
                return
            for index in range(self._corpus.map_count):
                self._map_select.addItem(self._source_item_text(index), index)
            wanted = self._default_source_index()
            row = self._map_select.findData(wanted)
            self._map_select.setCurrentIndex(row if row >= 0 else 0)
            self._source_index = self._map_select.currentData()
        finally:
            self._suppress = False

    def _populate_source_labels(self) -> None:
        """Restate the source selector's per-map connection counts, in place."""
        if self._corpus is None:
            return
        self._suppress = True
        try:
            for row in range(self._map_select.count()):
                index = self._map_select.itemData(row)
                self._map_select.setItemText(row, self._source_item_text(index))
        finally:
            self._suppress = False
        self._refresh_map_support()

    def _source_item_text(self, index: int) -> str:
        count = self._counts.get(index, 0)
        suffix = (
            f"{count} connection{'s' if count != 1 else ''}"
            if count
            else "no connections"
        )
        return f"{self._map_label(index)} \u00b7 {suffix}"

    def _default_source_index(self) -> int:
        """The map the session already points at, else the first with a connection.

        Opening on a map with nothing to show would make the whole surface look
        empty when it is not, so a map that has connections is preferred.
        """
        if self._corpus is None:
            return 0
        selected = self._session.selected_map
        if selected and selected.startswith("map:"):
            try:
                index = int(selected[4:], 10)
            except ValueError:
                index = -1
            if 0 <= index < self._corpus.map_count:
                return index
        for entry in self._corpus.entries():
            return entry.identity.source.index
        return 0

    def _populate_destination_maps(self) -> None:
        self._suppress = True
        try:
            self._destination.clear()
            if self._corpus is None:
                return
            for index in range(self._corpus.map_count):
                self._destination.addItem(self._map_label(index), index)
        finally:
            self._suppress = False

    def _populate_rows(self) -> None:
        """The selected map's connections, one row each, from the authority."""
        self._suppress = True
        try:
            self._table.clearContents()
            identities = self._identities()
            self._table.setRowCount(len(identities))
            for row, identity in enumerate(identities):
                self._fill_row(row, identity)
            self._reconcile_selection(identities)
        finally:
            self._suppress = False
        self._refresh_form()

    def _identities(self) -> tuple:
        if self._source_index is None:
            return ()
        return self._identities_for(self._source_index)

    def _identities_for(self, index: int) -> tuple:
        if self._corpus is None:
            return ()
        try:
            entries = self._corpus.for_map(MapIdentity(index))
        except _WARP_ERRORS:
            return ()
        return tuple(entry.identity for entry in entries)

    def _fill_row(self, row: int, identity) -> None:
        destination, arrival, facing = self._effective(identity)
        refusal = self._refusal_for(identity)
        state = self._state_for(identity, refusal)
        cells = (
            f"{identity.index:04d}",
            self._map_text(destination),
            self._region_text(identity),
            "\u2014" if refusal else self._arrival_text(arrival),
            "\u2014" if refusal else self._facing_text(facing),
            state,
        )
        for column, text in enumerate(cells):
            item = QTableWidgetItem(text)
            item.setToolTip(
                f"{identity}\n"
                f"Trigger region: {cells[2]}\n"
                f"Leads to: {cells[1]}\n"
                f"Arrival: {cells[3]}\n"
                f"Facing: {cells[4]}\n"
                f"State: {state}"
            )
            if column == 0:
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
            self._table.setItem(row, column, item)

    def _reconcile_selection(self, identities: tuple) -> None:
        """Keep the same connection selected across a repopulation when it exists."""
        if self._selected in identities:
            row = identities.index(self._selected)
        elif identities:
            row = 0
            self._selected = identities[0]
        else:
            self._selected = None
            return
        self._table.setCurrentCell(row, 0)
        self._table.selectRow(row)

    # -- the values a row and the form show -----------------------------------

    def _retail(self, identity) -> tuple:
        """``(destination, arrival, facing)`` exactly as the record stores them."""
        if self._corpus is None:
            return (None, None, None)
        entry = self._corpus.entry(identity)
        try:
            destination = self._corpus.destination(identity)
        except _WARP_ERRORS:
            destination = None
        record = entry.record
        if not record.has_raw_arrival_pair:
            # A 169-class pair is a scene-relative delta, so this surface shows no
            # point for it at all rather than presenting the delta as one.
            return (destination, None, None)
        return (destination, record.arrival, record.facing.arrival_direction)

    def _base(self, identity) -> tuple:
        """``(destination, arrival, facing)`` as the project leaves them."""
        destination, arrival, facing = self._retail(identity)
        committed = self._committed.get(identity)
        if committed is None:
            return (destination, arrival, facing)
        if committed.destination is not None:
            destination = committed.destination
        if committed.arrival_authored:
            arrival = committed.arrival
        if committed.facing_authored:
            facing = _facing_direction(committed.facing_raw)
        return (destination, arrival, facing)

    def _effective(self, identity) -> tuple:
        """The base overlaid by this session's staged edit - what a row shows."""
        destination, arrival, facing = self._base(identity)
        staged = self._staged.get(identity)
        if staged is None:
            return (destination, arrival, facing)
        if staged.destination is not None:
            destination = staged.destination
        if staged.arrival is not None:
            arrival = staged.arrival
        if staged.facing is not None:
            facing = staged.facing
        return (destination, arrival, facing)

    def _state_for(self, identity, refusal: str | None) -> str:
        if refusal is not None:
            return _STATE_READ_ONLY
        if identity in self._staged:
            return _STATE_STAGED
        if identity in self._committed:
            return _STATE_SAVED
        return _STATE_RETAIL

    def _seed_arrival(self, identity, destination) -> "TransitionArrival | None":
        """What the arrival control shows before the author states one.

        The project's or the record's own point where there is one; otherwise, for
        a destination the authority can derive one for, the point it derives.
        """
        base_destination, base_arrival, _ = self._base(identity)
        if destination == base_destination:
            if base_arrival is not None:
                return base_arrival
            return self._derive_arrival(identity, destination)
        derived = self._derive_arrival(identity, destination)
        return derived if derived is not None else base_arrival

    def _derive_arrival(self, identity, destination) -> "TransitionArrival | None":
        """The authority's safe arrival for this link, or None when it refuses."""
        if self._corpus is None:
            return None
        try:
            return self._corpus.derive_arrival(identity, destination)
        except _WARP_ERRORS:
            return None

    def _default_facing(self, destination, arrival) -> int | None:
        if self._corpus is None:
            return None
        try:
            return self._corpus.default_facing(destination, arrival)
        except _WARP_ERRORS:
            return None

    def _compose(self, identity, destination, arrival, facing, *, arrival_touched: bool):
        """The draft the form's current state asks for, or None when it asks nothing.

        A draft names only what it changes: a field left at the value the base
        already holds is not authored at all, which is what makes an untouched form
        a true no-op rather than a pretend edit. A retarget always states the
        arrival, because the previous destination's point belongs to the previous
        destination's geometry.
        """
        base_destination, _base_arrival, base_facing = self._base(identity)
        destination_part = None if destination == base_destination else destination
        if destination_part is not None or arrival_touched:
            arrival_part = arrival
        else:
            arrival_part = None
        facing_part = facing if facing != base_facing else None
        if destination_part is None and arrival_part is None and facing_part is None:
            return None
        return mt.TransitionEdit(
            destination=destination_part, arrival=arrival_part, facing=facing_part
        )

    # -- the gestures' shared machinery ---------------------------------------

    def _stage(self, identity, draft) -> bool:
        """Validate and record one gesture, as one undo entry.

        The draft is checked through the authority itself (`check_edit`), so the
        rule that decides what may be staged is the same rule the build applies -
        including the 169-class refusal and the destination's walkable extent.
        """
        if draft is None:
            if identity not in self._staged:
                self._refresh_form()
                self._publish_status(f"{identity} already holds these values.")
                return False
            self._push(identity, None)
            self._publish_status(f"Discarded the staged edit on {identity}.")
            return True
        if self._corpus is not None:
            try:
                self._corpus.check_edit(identity, draft)
            except _WARP_ERRORS as exc:
                self._refuse_stage(str(exc), identity)
                return False
        if not self._push(identity, draft):
            self._refresh_form()
            self._publish_status(f"{identity} already holds these values.")
            return False
        self._publish_status(self._gesture_text(identity, draft))
        return True

    def _push(self, identity, draft) -> bool:
        """Record a staged draft as one undo entry; False when it changes nothing."""
        before = self._staged.get(identity)
        if before == draft:
            return False
        self._undo_stack.push(StageTransitionCommand(self, identity, before, draft))
        return True

    def _restore_draft(self, identity, draft) -> None:
        """The one place a staged draft changes; undo and redo both come here."""
        if draft is None:
            self._staged.pop(identity, None)
        else:
            self._staged[identity] = draft
        self._populate_rows()
        self._populate_source_labels()
        self._publish_status(self._summary_text())
        self.dirtyChanged.emit()

    def _refuse_stage(self, message: str, identity) -> None:
        """An expected refusal: stated on screen, and nothing staged."""
        self._reason.setText(message)
        self._publish_status(f"{identity}: {message}")

    def _report_error(self, title: str, message: str) -> None:
        """An expected SDK refusal on an action the user pressed."""
        self._publish_status(message)
        QMessageBox.warning(self, title, message)

    def _gesture_text(self, identity, draft) -> str:
        if draft.destination is not None:
            facing_text = (
                self._facing_text(draft.facing)
                if draft.facing is not None
                else _UNCHANGED
            )
            return (
                f"{identity} now leads to {self._map_text(draft.destination)}, "
                f"arriving at {self._arrival_text(draft.arrival)}, facing "
                f"{facing_text}. Apply to write it to the project."
            )
        fields = _draft_fields(None, draft)
        if fields:
            return (
                f"{identity} staged ({', '.join(fields)}). Apply to write it to the "
                "project."
            )
        return f"{identity} staged."

    # -- widgets --------------------------------------------------------------

    def _on_source_map_changed(self, _row: int) -> None:
        if self._suppress:
            return
        self._source_index = self._map_select.currentData()
        self._selected = None
        self._table.clearSelection()
        self._populate_rows()
        self._refresh_map_support()
        self._publish_status(self._summary_text())

    def _on_row_selected(self) -> None:
        if self._suppress:
            return
        row = self._table.currentRow()
        identities = self._identities()
        if 0 <= row < len(identities):
            self._selected = identities[row]
        self._refresh_form()

    def _on_destination_changed(self, _row: int) -> None:
        if self._suppress or self._selected is None:
            return
        destination = self._destination.currentData()
        if destination is None:
            return
        self.stage_destination(int(destination))

    def _on_arrival_changed(self) -> None:
        if self._suppress or self._selected is None:
            return
        self.stage_arrival(self._arrival_x.value(), self._arrival_y.value())

    def _on_facing_changed(self, _row: int) -> None:
        if self._suppress or self._selected is None:
            return
        self.stage_facing(self._facing.currentData())

    def _refresh_form(self) -> None:
        """Render the selected connection: the form, the chip and the reason."""
        identity = self._selected
        self._suppress = True
        try:
            refusal = self._edit_refusal()
            if identity is None:
                # Nothing is selected, so nothing of a PREVIOUS selection may stay
                # on screen: a stale destination and arrival beside "no connection
                # selected" reads as if some connection still had those values.
                self._identity.setText("Select a connection to edit it.")
                self._state_chip.set_state("No connection selected", "neutral")
                if self._corpus_error is not None:
                    self._reason.setText(self._corpus_error)
                elif self._corpus is None:
                    self._reason.setText(_NO_IMAGE)
                elif self._project_error is not None:
                    self._reason.setText(self._project_error)
                else:
                    self._reason.setText("This map has no connections to edit.")
                self._show_destination(None)
                self._arrival_x.setValue(0)
                self._arrival_y.setValue(0)
                self._show_facing(None)
                self._arrival_hint.setText("")
                self._facing_hint.setText("")
                self._region_label.setText("\u2014")
                self._set_controls_enabled(False)
                return
            destination, arrival, facing = self._effective(identity)
            self._identity.setText(str(identity))
            self._region_label.setText(self._region_text(identity))
            self._show_destination(destination)
            shown = arrival if arrival is not None else self._seed_arrival(
                identity, destination
            )
            self._arrival_x.setValue(shown.x if shown is not None else 0)
            self._arrival_y.setValue(shown.y if shown is not None else 0)
            self._show_facing(facing if facing is not None else None)
            self._reason.setText(refusal or "")
            state = self._state_for(identity, refusal)
            self._state_chip.set_state(state, _STATE_ROLES.get(state, "neutral"))
            self._set_controls_enabled(refusal is None)
            self._refresh_hints(identity, destination, arrival, shown)
        finally:
            self._suppress = False
        self._refresh_buttons()

    def _show_destination(self, destination) -> None:
        """Point the destination control at the record's map, or at nothing.

        A record whose key resolves to no map gets no fabricated selection: the
        control is left unselected so the surface never claims the connection leads
        somewhere it does not.
        """
        if destination is None:
            self._destination.setCurrentIndex(-1)
            return
        row = self._destination.findData(destination.index)
        self._destination.setCurrentIndex(row if row >= 0 else -1)

    def _show_facing(self, facing: "int | None") -> None:
        row = self._facing.findData(facing)
        self._facing.setCurrentIndex(row if row >= 0 else 0)

    def _refresh_hints(self, identity, destination, arrival, shown) -> None:
        """State what the record does today, in words, next to each control.

        A record the authority will not retarget gets NO hint: the reason line
        states why, and a hint that told the author to type a point would be an
        instruction the disabled controls make impossible to follow.
        """
        if not self._editable(identity):
            self._arrival_hint.setText("")
            self._facing_hint.setText("")
            return
        _dest, _base_arrival, base_facing = self._base(identity)
        staged = self._staged.get(identity)
        committed = self._committed.get(identity)
        if destination is None:
            self._arrival_hint.setText(_UNRESOLVED_DESTINATION)
        elif staged is not None and staged.arrival is not None:
            self._arrival_hint.setText("Staged arrival; not applied yet.")
        elif committed is not None and committed.arrival_authored:
            self._arrival_hint.setText("The project's authored arrival point.")
        elif arrival is not None:
            self._arrival_hint.setText("The record's own arrival point.")
        elif shown is not None:
            self._arrival_hint.setText(
                "The record states no arrival; the point shown is derived from the "
                "destination's connection back. Editing it authors an arrival."
            )
        else:
            self._arrival_hint.setText(
                "The record states no arrival, and none can be derived. Type the "
                "point the player should arrive at."
            )
        if staged is not None and staged.facing is not None:
            self._facing_hint.setText(
                f"Will author: {self._facing_text(staged.facing)}."
            )
        elif base_facing is not None:
            self._facing_hint.setText(
                f"The record states: {self._facing_text(base_facing)}."
            )
        else:
            self._facing_hint.setText(
                "The record states no facing; the actor keeps its own direction."
            )

    def _set_controls_enabled(self, enabled: bool) -> None:
        for widget in (
            self._destination,
            self._arrival_x,
            self._arrival_y,
            self._facing,
        ):
            widget.setEnabled(enabled)
        self._refresh_buttons()

    def _refresh_buttons(self) -> None:
        identity = self._selected
        staged = identity is not None and identity in self._staged
        committed = identity is not None and identity in self._committed
        self._apply_button.setEnabled(bool(self._staged))
        self._revert_button.setEnabled(
            staged
            or (
                committed
                and self._session.project_dir is not None
                and self._edit_refusal() is None
            )
        )

    def _refresh_map_support(self) -> None:
        """The map bar's second half: only what the combo does not already say.

        The combo's own text carries each map's connection count, so repeating the
        count here said the same fact twice on one line. This states the *edit*
        state instead, and nothing at all when there is none to state.
        """
        if self._corpus_error is not None:
            self._map_support.setText(f"Connections could not be read: {self._corpus_error}")
            return
        if self._corpus is None:
            self._map_support.setText(_NO_IMAGE)
            return
        if self._source_index is None:
            self._map_support.setText("No map selected.")
            return
        identities = self._identities()
        if not identities:
            self._map_support.setText("This map has no connections to edit.")
            return
        staged = sum(1 for identity in identities if identity in self._staged)
        saved = sum(1 for identity in identities if identity in self._committed)
        parts: list[str] = []
        if staged:
            parts.append(f"{staged} staged, not applied")
        if saved:
            parts.append(f"{saved} saved to the project")
        if self._session.project_dir is None:
            parts.append(_NO_PROJECT)
        self._map_support.setText(" \u00b7 ".join(parts))

    # -- labels and text ------------------------------------------------------

    def _edit_refusal(self) -> str | None:
        if self._selected is None:
            return None
        if self._corpus_error is not None:
            return self._corpus_error
        if self._corpus is None:
            return _NO_IMAGE
        if self._project_error is not None:
            return self._project_error
        if self._session.project_dir is None:
            return _NO_PROJECT
        return self._refusal_for(self._selected)

    def _refusal_for(self, identity) -> str | None:
        """Why this record cannot be retargeted, or None."""
        if self._corpus_error is not None:
            return self._corpus_error
        if self._corpus is None:
            return _NO_IMAGE
        if self._project_error is not None:
            return self._project_error
        if not self._editable(identity):
            return _NOT_RETARGETABLE
        if self._retail(identity)[0] is None:
            return _UNRESOLVED_DESTINATION
        if self._session.project_dir is None:
            return _NO_PROJECT
        return None

    def _editable(self, identity) -> bool:
        """Whether the authority can safely express a retarget of this record.

        `has_raw_arrival_pair` is the measured class split: true exactly for the
        566-class record whose stored pair IS the arrival.
        """
        if self._corpus is None:
            return False
        try:
            return self._corpus.entry(identity).record.has_raw_arrival_pair
        except _WARP_ERRORS:
            return False

    def _form_destination(self) -> "MapIdentity | None":
        index = self._destination.currentData()
        if index is None:
            return None
        try:
            return MapIdentity(int(index))
        except (mt.MapTransitionsError, ValueError):
            return None

    def _form_arrival(self) -> "TransitionArrival | None":
        try:
            return TransitionArrival(self._arrival_x.value(), self._arrival_y.value())
        except (MapTransitionError, ValueError):
            return None

    def _map_label(self, index: int) -> str:
        name = self._labels.get(index)
        return f"map:{index:04d} \u00b7 {name}" if name else f"map:{index:04d}"

    def _map_text(self, identity: "MapIdentity | None") -> str:
        if identity is None:
            return "unresolved"
        return self._map_label(identity.index)

    def _region_text(self, identity) -> str:
        if self._corpus is None:
            return "\u2014"
        try:
            region: TransitionRegion = self._corpus.entry(identity).record.region
        except _WARP_ERRORS:
            return "\u2014"
        # Positional, exactly as the codec names them: which interval is which is
        # UNRESOLVED, so no axis name is invented here either.
        return (
            f"first {region.first[0]}\u2013{region.first[1]} \u00b7 "
            f"second {region.second[0]}\u2013{region.second[1]}"
        )

    def _arrival_text(self, arrival) -> str:
        if arrival is None:
            return "not stated"
        return f"{arrival.x}, {arrival.y}"

    def _facing_text(self, facing: "int | None") -> str:
        if facing is None:
            return _UNCHANGED
        return FACING_NAMES.get(facing, _UNCHANGED)

    def _summary_text(self) -> str:
        if self._corpus_error is not None:
            return f"Connections could not be read: {self._corpus_error}"
        if self._corpus is None:
            return _NO_IMAGE
        if self._project_error is not None:
            return self._project_error
        if self._source_index is None:
            return "No map selected."
        name = self._map_label(self._source_index)
        identities = self._identities()
        if not identities:
            return f"{name}: no connections to edit."
        staged = sum(1 for i in identities if i in self._staged)
        saved = sum(1 for i in identities if i in self._committed)
        parts = [f"{name}: {len(identities)} connection{'s' if len(identities) != 1 else ''}"]
        if saved:
            parts.append(f"{saved} saved")
        if staged:
            parts.append(f"{staged} staged, not applied")
        if self._session.project_dir is None:
            parts.append(_NO_PROJECT)
        return " \u00b7 ".join(parts)

    def _publish_status(self, text: str) -> None:
        self._status.setText(text)
        self.statusChanged.emit(text)


__all__ = ["StageTransitionCommand", "WarpTab"]
