"""MAP-WARP-WORKBENCH-001 - the Maps editor's Warps mode.
MAP-WARP-CREATE-WORKBENCH-001 - its Create Transition action.

A **thin client** over the transition authority (`tools.webfoot.map_transitions`),
which is the already-merged, runtime-proven path: the same `TransitionIdentity`,
the same `set_destination`/`set_arrival`/`set_facing`, the same
`CreatedTransitionIdentity`, the same `maps/transitions.toml` and
`maps/transition_creations.toml` documents and the same production build. Nothing
here serializes a record, writes a ROM, computes a file offset or masks a byte;
every value on screen comes out of the SDK, and every edit goes back through it.

What it does: pick a map, see its existing connections, select one and retarget it
- where it leads, where the player arrives, and which way they face - then Apply,
which is one semantic project write. It also **creates** a transition the image
does not contain: `Create transition` opens a compact form that collects a durable
authored name, the existing same-map connection the new one is based on, its
trigger region, its destination, its arrival pair and its facing override, and
stages a semantic creation through the authority. The normal Validate -> Build path
consumes both exactly as it consumes any other authored content.

What it deliberately will not do:

* **No 169-class retarget, and no 169-class base.** A 169-class record stores its
  arrival as a scene-relative delta rather than a point, so the toolkit cannot state
  where the player lands on a different map, and cannot state an arrival for a new
  record over one. The record is read-only, with the reason on screen, and the
  `Based on` control is built from the authority's own `creation_templates`, which
  yields the measured 566 class alone.
* **No raw field, and no address anywhere.** The facing control offers Unchanged /
  South / North / West / East - never `+0x10` and never its gate bits. "Unchanged"
  means "author no facing", which is the authority's own no-override state; a record
  whose low bits are `0x02` therefore reads Unchanged, not West. A creation's
  identity is `map:NNNN/transition:<name>`; no array index, offset, pointer or count
  is shown, typed or computed here, and the trigger region keeps the codec's own
  positional naming (`first`/`second`).
* **No derivation for a creation.** A new transition's arrival is authored, not
  derived from its destination, because there is no existing link to derive it from.

The one rule that matters most (WORKBENCH-001): every slot that calls the SDK
catches the SDK exception **family parent** - `MapTransitionsError` for the
authority, `MapTransitionError` for the codec - plus `ProjectError` and `OSError`
for the project read and write underneath, and `MapBrowserError` /
`MapGraphicsError` for the map labels. A leaf-only `except` would let a real
refusal escape to a console the GUI does not have, and the click would simply
look dead.

Project I/O is bounded on purpose (CQA-07): the corpus and the map labels are read
once per session, the project once per project mutation (one parse for both of its
transition documents), and selecting a map, a row, a field or a creation gesture
reads nothing at all. A creation gesture is checked against the corpus already in
memory, never re-read from the image.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QUndoCommand, QUndoStack
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStackedWidget,
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
    BOUND_MAXIMUM,
    BOUND_MINIMUM,
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
#: The first column carries each row's own identity part - a canonical record's
#: `IIII`, or a created transition's authored name - because those are the two
#: spellings a transition's durable identity has, and neither is an address.
_COLUMNS = ("Connection", "Leads to", "Trigger region", "Arrival", "Facing", "State")

#: The row states. "Saved" is the project's committed edit, "Staged" is this
#: session's uncommitted one, "Read-only" is a record the authority will not
#: retarget (or a surface with no project to author into). The two `New` states are
#: a transition the project CREATES rather than edits, which is why they say so:
#: such a row has no canonical bytes behind it at all.
_STATE_RETAIL = "Retail"
_STATE_SAVED = "Saved"
_STATE_STAGED = "Staged"
_STATE_READ_ONLY = "Read-only"
_STATE_NEW_STAGED = "New (staged)"
_STATE_NEW_SAVED = "New (saved)"

#: Each state's colour-and-glyph role. Read-only is a state, not an error, so it
#: takes the muted `readonly` role rather than the danger one, and the two
#: unedited states stay neutral: the chip's emphasis is spent on work in progress.
_STATE_ROLES = {
    _STATE_RETAIL: "neutral",
    _STATE_SAVED: "saved",
    _STATE_STAGED: "pending",
    _STATE_READ_ONLY: "readonly",
    _STATE_NEW_STAGED: "pending",
    _STATE_NEW_SAVED: "saved",
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

#: Why a created transition needs a project, worded so the document it lands in is
#: named rather than implied - the two transition documents are separate on purpose.
_NO_CREATE_PROJECT = (
    "Open a Webfoot project to create a transition; a creation is stored in "
    "maps/transition_creations.toml, never in a ROM."
)

_NO_IMAGE = "Open a game image to read its connections."

#: The arrival hint on a creation form. It states the ticket's rule in product
#: wording: the point is authored, and the toolkit does not infer one from the
#: destination the way a retarget of an existing link can.
_ARRIVAL_REQUIRED = (
    "Where the player lands in the destination. Required: a new transition has no "
    "existing link to derive an arrival from."
)

#: The `Based on` hint when nothing is selected yet.
_BASED_ON_REQUIRED = (
    "Choose the existing connection this new one starts from; its class word, its "
    "engine-read byte and the low bits of its direction byte are carried over."
)


def _no_base_text(label: str) -> str:
    """Why a creation cannot start on this map, in product wording."""
    return (
        f"{label} has no 566-class connection, and only that class carries the "
        "arrival bytes a new transition starts from, so the toolkit will not create "
        "one on this map."
    )


def _shared_root_text(label: str, sharers: tuple[str, ...]) -> str:
    """Why a map on a shared connection root cannot gain one.

    The fact is the authority's own (`MapTransitions.shared_root_maps`); stating it
    before the form opens is what keeps an author from filling a form in and only
    then being told the count and the array pointer belong to another map too.
    """
    return (
        f"{label}'s connection root is shared with {' and '.join(sharers)}, so a "
        "transition created here would appear on those maps as well; the toolkit "
        "will not create one."
    )


@dataclass(frozen=True, slots=True)
class CreationDraft:
    """Everything the Create Transition form states, as semantic SDK values.

    The form's widgets are a view of this and nothing else, so an undo entry's
    before/after values are the authored values themselves rather than a snapshot of
    widget state. Every field is either an SDK type or a plain pair of integers in
    the codec's own domain; no address, offset, index or raw byte appears here.

    ``region`` is ``((low, high), (low, high))`` and ``arrival`` is ``(x, y)``: the
    form has to hold values the codec may refuse (an unordered interval, an off-map
    point) so it can show the refusal beside the field that caused it, which is why
    the intervals are held as stated rather than as a validated
    :class:`TransitionRegion`.
    """

    source: MapIdentity
    name: str = ""
    template: "mt.TransitionIdentity | None" = None
    region: tuple[tuple[int, int], tuple[int, int]] = ((0, 1), (0, 1))
    destination: "MapIdentity | None" = None
    arrival: tuple[int, int] = (0, 0)
    facing: "int | None" = None

    def identity(self) -> "mt.CreatedTransitionIdentity | None":
        """``map:NNNN/transition:<name>``, or None while the name is not one.

        The name is validated by the production model itself
        (`CreatedTransitionIdentity`), so the rule the form enforces is the rule the
        project document and the build enforce, and its wording is theirs.
        """
        try:
            return mt.CreatedTransitionIdentity(self.source, self.name)
        except mt.MapTransitionsError:
            return None

    def replaced(self, **fields) -> "CreationDraft":
        """A copy with some fields changed, which is how a gesture states itself."""
        return replace(self, **fields)


def _draft_from_creation(creation: "mt.TransitionCreation") -> CreationDraft:
    """The form state an authored creation states, for reopening or reverting to."""
    region = creation.region
    return CreationDraft(
        creation.identity.source,
        name=creation.identity.name,
        template=creation.template,
        region=(region.first, region.second),
        destination=creation.destination,
        arrival=(creation.arrival.x, creation.arrival.y),
        facing=creation.facing,
    )


#: The form fields a creation gesture can change, named the way the product names
#: them. Used for the undo label only; the values themselves are the draft's.
_CREATION_FIELDS = (
    ("name", "name"),
    ("template", "base connection"),
    ("region", "trigger region"),
    ("destination", "destination"),
    ("arrival", "arrival"),
    ("facing", "facing"),
)


def _creation_fields(before: "CreationDraft | None", after: "CreationDraft | None") -> tuple[str, ...]:
    """Which fields a creation gesture changed, in product language."""
    names: list[str] = []
    for attribute, label in _CREATION_FIELDS:
        old = getattr(before, attribute, None) if before is not None else None
        new = getattr(after, attribute, None) if after is not None else None
        if old != new:
            names.append(label)
    return tuple(names)


def _creation_command_text(
    before: "CreationDraft | None", after: "CreationDraft | None"
) -> str:
    """A one-line undo label naming what a creation gesture did."""
    if after is None:
        return "Discard the new transition"
    identity = after.identity()
    subject = str(identity) if identity is not None else "the new transition"
    names = _creation_fields(before, after)
    if not names:
        return f"Edit {subject}"
    if len(names) == 1:
        return f"Set the {names[0]} of {subject}"
    return f"Author {subject} ({', '.join(names)})"


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


@dataclass(frozen=True, slots=True)
class CreationState:
    """The whole creation surface, as one value: the draft and what it stages.

    An undo entry stores two of these instead of two drafts, which is what lets
    `undo()`/`redo()` install a state without reading, validating or raising - the
    properties Qt's undo stack requires of a command, because a Python exception
    crossing `QUndoCommand.redo` leaves the C++ stack in a state Python cannot see.
    """

    draft: "CreationDraft | None" = None
    #: The staged creations, as ``((identity, creation), ...)`` in identity order.
    staged: tuple = ()
    #: The identity the draft is currently staged under, or None.
    open_key: object = None
    #: Why the draft is not staged, in the authority's own words where it refused.
    reason: str | None = None


def _staged_snapshot(staged) -> tuple:
    """A staged-creations mapping as an ordered, hashable snapshot."""
    return tuple(sorted(staged.items(), key=lambda item: item[0]))


class StageCreationCommand(QUndoCommand):
    """One authored creation gesture: the whole creation state before and after.

    The same shape :class:`StageTransitionCommand` has, for the same reason: the
    gesture is what the author did, so one name, one base selection, one region, one
    destination, one arrival or one facing is one entry. Both states are fully
    resolved before this command is pushed, so `undo()`/`redo()` only install them.
    """

    def __init__(self, tab: "WarpTab", before, after) -> None:
        super().__init__(_creation_command_text(before.draft, after.draft))
        self._tab = tab
        self._before = before
        self._after = after

    def undo(self) -> None:  # noqa: D102 - Qt naming
        self._tab._install_creation_state(self._before)

    def redo(self) -> None:  # noqa: D102 - Qt naming
        self._tab._install_creation_state(self._after)


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

        connections_page = QWidget()
        connections_layout = QVBoxLayout(connections_page)
        connections_layout.setContentsMargins(0, 0, 0, 0)
        connections_layout.setSpacing(0)
        connections_layout.addWidget(PanelHeader("Selected connection"))
        connections_layout.addWidget(form_box)
        connections_layout.addStretch(1)

        self._create_button = QPushButton("Create transition\u2026")
        self._create_button.setAccessibleName("Create transition")
        self._create_button.setToolTip(
            "Author a transition this image does not contain, stored in the "
            "project's maps/transition_creations.toml and materialized by the normal "
            "build. The source ROM is never modified."
        )
        self._create_button.clicked.connect(self.open_creation)
        creation_page = self._build_creation_page()

        self._pages = QStackedWidget()
        self._pages.addWidget(connections_page)
        self._pages.addWidget(creation_page)

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
        right_layout.addWidget(self._pages, 1)

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
        top_layout.addWidget(self._create_button)

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
        #: project mutation - never per control. One project parse supplies both
        #: this and `_committed_creations`.
        self._committed: dict = {}
        #: This session's uncommitted edits, keyed by identity. The undo stack is
        #: their history.
        self._staged: dict = {}
        #: The project's authored CREATIONS, as the authority's own request type.
        self._committed_creations: dict = {}
        #: This session's uncommitted creations, keyed by their durable identity.
        self._staged_creations: dict = {}
        #: The creation form's open draft, or None when the form is closed.
        self._creation: "CreationDraft | None" = None
        #: The identity the open draft is currently STAGED under, or None when it is
        #: not staged. It is what lets a rename or a revert drop the entry the form
        #: held without touching a creation another draft staged.
        self._open_creation_key = None
        #: Why the open creation is not staged right now, in the authority's own
        #: words where the authority refused it. Rendered beside the form.
        self._creation_refusal_text: str | None = None
        #: Why the Create Transition action itself was refused on this map. Held
        #: until the map or the selection changes, so the pane the author is looking
        #: at states the reason instead of only the elided status line.
        self._creation_action_refusal: str | None = None
        #: Map index -> ROM-derived label, resolved once per session.
        self._labels: dict[int, str] = {}
        self._source_index: int | None = None
        self._selected = None
        #: True while the widgets are being repopulated, so a programmatic change
        #: is never mistaken for a gesture.
        self._suppress = False
        self._undo_stack = QUndoStack(self)

        self._populate_after_session_change()

    # -- the Create Transition form -------------------------------------------

    def _build_creation_page(self) -> QWidget:
        """The compact creation surface: name, base, region, destination, arrival.

        Every control states a semantic value the authority owns. The one place the
        form is stricter than the authority is that nothing here shows an address,
        an offset, an array index, a count or a raw byte - the identity is
        ``map:NNNN/transition:<name>``, the region keeps the codec's positional
        naming, and the facing offers the five product choices.
        """
        self._creation_identity = TechnicalLabel("Author a name to create a transition.")
        self._creation_identity.setAccessibleName("Created transition identity")

        self._creation_name = QLineEdit()
        self._creation_name.setAccessibleName("New transition name")
        self._creation_name.setPlaceholderText("e.g. kai-shop-door")
        self._creation_name.setToolTip(
            "The durable authored name. The identity becomes "
            "map:NNNN/transition:<name>; lowercase, starting with a letter, letters, "
            "digits, '_' and '-' only."
        )
        self._creation_name.editingFinished.connect(self._on_creation_name_edited)
        self._creation_name_hint = QLabel(
            "Lowercase, starts with a letter, letters, digits, '_' and '-' only."
        )
        self._creation_name_hint.setProperty("dbzRole", "hint")
        self._creation_name_hint.setWordWrap(True)

        self._creation_template = QComboBox()
        self._creation_template.setAccessibleName("Based on")
        self._creation_template.setToolTip(
            "The existing connection of this map the new one starts from. Only a "
            "566-class connection may be used, because only its stored arrival is a "
            "point."
        )
        self._creation_template.currentIndexChanged.connect(
            self._on_creation_template_changed
        )
        self._creation_template_hint = QLabel()
        self._creation_template_hint.setProperty("dbzRole", "hint")
        self._creation_template_hint.setWordWrap(True)

        # The trigger region, in the codec's own positional vocabulary: two ordered
        # intervals, one row each, so the control stays narrow enough for the pane.
        self._creation_region_spins: list[QSpinBox] = []
        region_rows = QVBoxLayout()
        region_rows.setContentsMargins(0, 0, 0, 0)
        region_rows.setSpacing(theme.SPACE_XS)
        for caption in ("first", "second"):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(theme.SPACE_SM)
            low = self._creation_spin(f"{caption} lower bound")
            high = self._creation_spin(f"{caption} upper bound")
            self._creation_region_spins.extend((low, high))
            row.addWidget(_field_label(caption))
            row.addWidget(low)
            row.addWidget(QLabel("\u2013"))
            row.addWidget(high)
            row.addStretch(1)
            region_rows.addLayout(row)
        for spin in self._creation_region_spins:
            spin.editingFinished.connect(self._on_creation_region_changed)
        region_widget = QWidget()
        region_widget.setLayout(region_rows)

        self._creation_destination = QComboBox()
        self._creation_destination.setAccessibleName("Destination map")
        self._creation_destination.setToolTip("Where the new connection leads")
        self._creation_destination.currentIndexChanged.connect(
            self._on_creation_destination_changed
        )

        self._creation_arrival_x = self._creation_spin("Arrival X", arrival=True)
        self._creation_arrival_y = self._creation_spin("Arrival Y", arrival=True)
        arrival_row = QHBoxLayout()
        arrival_row.setContentsMargins(0, 0, 0, 0)
        arrival_row.setSpacing(theme.SPACE_SM)
        arrival_row.addWidget(QLabel("X"))
        arrival_row.addWidget(self._creation_arrival_x)
        arrival_row.addWidget(QLabel("Y"))
        arrival_row.addWidget(self._creation_arrival_y)
        arrival_row.addStretch(1)
        arrival_widget = QWidget()
        arrival_widget.setLayout(arrival_row)

        self._creation_facing = QComboBox()
        self._creation_facing.setAccessibleName("Arrival facing")
        self._creation_facing.setToolTip(
            "The direction the player is turned on arrival. Unchanged authors no "
            "facing, which is the engine's own 'keep walking' state."
        )
        self._creation_facing.addItem(_UNCHANGED, None)
        for direction, name in sorted(FACING_NAMES.items()):
            self._creation_facing.addItem(name, direction)
        self._creation_facing.currentIndexChanged.connect(
            self._on_creation_facing_changed
        )

        self._creation_chip = StateChip("Not staged", "neutral", plain=True)
        self._creation_reason = QLabel()
        self._creation_reason.setProperty("dbzRole", "hint")
        self._creation_reason.setWordWrap(True)
        self._creation_reason.setAccessibleName("Why the new transition is not staged")

        self._create_apply_button = QPushButton("Apply to project")
        self._create_apply_button.setProperty("dbzRole", "primary")
        self._create_apply_button.setToolTip(
            "Write every staged new transition into the project's "
            "maps/transition_creations.toml. The normal build allocates the record "
            "and its expanded pointer array; the source ROM is never modified."
        )
        self._create_apply_button.clicked.connect(self.apply_creations)
        self._create_revert_button = QPushButton("Revert")
        self._create_revert_button.setToolTip(
            "Return this creation to the last saved state: a staged creation is "
            "discarded, and a saved one is restored to the values the project holds."
        )
        self._create_revert_button.clicked.connect(self.revert_creation)
        self._create_close_button = QPushButton("Close")
        self._create_close_button.setToolTip(
            "Leave the creation form. Anything already staged stays in the list and "
            "is written by Apply."
        )
        self._create_close_button.clicked.connect(self.close_creation)
        create_actions = QHBoxLayout()
        create_actions.setContentsMargins(0, 0, 0, 0)
        create_actions.setSpacing(theme.SPACE_SM)
        create_actions.addWidget(self._create_apply_button)
        create_actions.addWidget(self._create_revert_button)
        create_actions.addWidget(self._create_close_button)
        create_actions.addStretch(1)

        form = QFormLayout()
        form.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM
        )
        form.setHorizontalSpacing(theme.SPACE_MD)
        form.setVerticalSpacing(theme.SPACE_XS)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.addRow(self._creation_identity)
        form.addRow(_field_label("Name"), self._creation_name)
        form.addRow("", self._creation_name_hint)
        form.addRow(_field_label("Based on"), self._creation_template)
        form.addRow("", self._creation_template_hint)
        form.addRow(_field_label("Trigger region"), region_widget)
        form.addRow(_field_label("Leads to"), self._creation_destination)
        form.addRow(_field_label("Arrival"), arrival_widget)
        form.addRow("", self._arrival_hint_for_creation())
        form.addRow(_field_label("Facing"), self._creation_facing)
        form.addRow(_field_label("State"), self._creation_chip)
        form.addRow(self._creation_reason)
        form.addRow(create_actions)
        form_box = QWidget()
        form_box.setLayout(form)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(PanelHeader("New transition"))
        layout.addWidget(form_box)
        layout.addStretch(1)
        return page

    def _creation_spin(self, name: str, *, arrival: bool = False) -> QSpinBox:
        """One numeric field, in the codec's own domain for the field it states."""
        spin = QSpinBox()
        spin.setAccessibleName(name)
        spin.setKeyboardTracking(False)
        if arrival:
            # Everything below the measured "no authored arrival" sentinel, exactly
            # as the existing-connection editor states it. A point outside the
            # destination's walkable extent is refused by the authority rather than
            # clamped here.
            spin.setRange(0, ARRIVAL_UNSET_MINIMUM - 1)
        else:
            spin.setRange(BOUND_MINIMUM, BOUND_MAXIMUM)
        spin.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return spin

    def _arrival_hint_for_creation(self) -> QLabel:
        self._creation_arrival_hint = QLabel(_ARRIVAL_REQUIRED)
        self._creation_arrival_hint.setProperty("dbzRole", "hint")
        self._creation_arrival_hint.setWordWrap(True)
        return self._creation_arrival_hint

    # -- public surface (used by the mode strip, the shell, tests and QA) ------

    def on_session_changed(self) -> None:
        """A different image: drop everything image-bound and re-read.

        CQA-05, second half. Staged edits, staged creations, the open creation form,
        the undo history, the corpus and the map labels all describe the image that
        was open, so a true session replacement clears them; no project mutation
        does.
        """
        self._corpus = None
        self._corpus_error = None
        self._committed = {}
        self._staged = {}
        self._committed_creations = {}
        self._staged_creations = {}
        self._creation = None
        self._open_creation_key = None
        self._labels = {}
        self._selected = None
        self._source_index = None
        self._undo_stack.clear()
        self._populate_after_session_change()
        self.dirtyChanged.emit()

    def on_project_mutated(self) -> None:
        """A project mutation: re-read what the project holds, keep what is staged.

        CQA-05, first half. Another editor's Apply, a Save As or this tab's own
        Apply all arrive here. The staged edits and the staged creations are
        in-memory intents the project still has a place for, so they survive - as
        does the creation form's open draft, which is what makes an unrelated
        mutation unable to discard work in progress. Only the committed picture is
        re-read - once, not per row or per control (CQA-07).
        """
        self._reload_committed()
        # The form's own draft is re-derived against what the project now holds -
        # the one thing a mutation can change about it - without touching the undo
        # history or the drafted values.
        self._reapply_creation()
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
        """This session's uncommitted work: staged edits and staged creations."""
        return len(self._staged) + len(self._staged_creations)

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
        """Select one list row, exactly as a click on it would.

        The row handler is invoked explicitly as well as by Qt's signal, because
        selecting the row that is ALREADY current emits nothing - and a created row
        opens the creation form, so "click the row you are on" has to work.
        """
        if not 0 <= row < self._table.rowCount():
            return False
        self._table.selectRow(row)
        self._table.setCurrentCell(row, 0)
        self._on_row_selected()
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

    # -- the creation surface (public, for tests and QA) -----------------------

    def create_action_enabled(self) -> bool:
        """Whether the Create Transition action can be pressed at all."""
        return self._create_button.isEnabled()

    def creation_refusal(self) -> str | None:
        """Why no transition can be created on the selected map, or None.

        This is the surface's fail-closed gate, and every branch of it is a fact the
        authority owns: no image, no project, a project document that cannot be read,
        a connection root shared with another map (`shared_root_maps`), or no
        566-class record to base a creation on (`creation_templates`). It gates the
        ACTION, so an author is told before filling a form in, and the same rules are
        enforced again - by the authority itself - on every gesture.
        """
        if self._corpus_error is not None:
            return self._corpus_error
        if self._corpus is None:
            return _NO_IMAGE
        if self._project_error is not None:
            return self._project_error
        if self._source_index is None:
            return "Select a map first."
        if self._session.project_dir is None:
            return _NO_CREATE_PROJECT
        index = self._source_index
        try:
            sharers = self._corpus.shared_root_maps(MapIdentity(index))
        except _WARP_ERRORS as exc:
            return str(exc)
        if sharers:
            return _shared_root_text(
                self._map_label(index),
                tuple(self._map_label(other.index) for other in sharers),
            )
        if not self._template_entries():
            return _no_base_text(self._map_label(index))
        return None

    def creation_templates(self) -> tuple[tuple[str, object], ...]:
        """The `Based on` vocabulary: ``(description, TransitionIdentity)``.

        Straight from the authority's `creation_templates`, so a 169-class record
        cannot appear here even if a future corpus is full of them.
        """
        return tuple(
            (self._template_text(entry.identity), entry.identity)
            for entry in self._template_entries()
        )

    def creation_open(self) -> bool:
        return self._creation is not None

    def open_creation(self) -> bool:
        """The Create Transition action: open a form for a new transition.

        Fails closed: with no image, no project, no 566-class base or a shared
        connection root, nothing is opened and the reason is stated on screen and in
        the status line. Opening the form is not a gesture, so it enters no history.
        """
        refusal = self.creation_refusal()
        if refusal is not None:
            # The action is refused. The form is not opened, and the reason is kept
            # on the surface itself - not only in the status line, which is one line
            # wide and elides a long explanation - so the pane the author is looking
            # at states why nothing happened.
            self._creation = None
            self._open_creation_key = None
            self._creation_refusal_text = None
            self._creation_action_refusal = refusal
            self._pages.setCurrentIndex(0)
            self._publish_status(refusal)
            self._refresh_pages()
            self._refresh_map_support()
            return False
        self._creation_action_refusal = None
        source = MapIdentity(self._source_index)
        if self._creation is None or self._creation.source != source:
            # A fresh form is derived and installed, not pushed: opening it is not a
            # gesture, so it enters no history. The list selection is dropped with
            # it, so the highlight cannot name a row this form is not editing.
            self._selected = None
            draft = self._fresh_creation_draft(source)
            self._creation = draft
            self._open_creation_key = None
            self._install_creation_state(self._resolve_creation_state(draft, None))
            return True
        self._pages.setCurrentIndex(1)
        self._refresh_pages()
        self._publish_status(self._summary_text())
        return True

    def close_creation(self) -> bool:
        """Leave the creation form. Anything staged stays staged and stays listed."""
        if self._creation is None:
            return False
        self._creation = None
        self._open_creation_key = None
        self._creation_refusal_text = None
        self._pages.setCurrentIndex(0)
        self._refresh_pages()
        self._publish_status(self._summary_text())
        return True

    def creation_draft(self) -> "CreationDraft | None":
        return self._creation

    def creation_identity(self) -> str | None:
        """The identity the open form states, or None while the name is not one."""
        identity = self._creation.identity() if self._creation is not None else None
        return str(identity) if identity is not None else None

    def creation_reason(self) -> str | None:
        """Why the open creation is not staged, or None when it is."""
        return self._creation_refusal_text

    def creation_form_state(self) -> dict:
        """The creation form's current state, for tests and QA probes."""
        return {
            "open": self._creation is not None,
            "source": self._creation.source.index if self._creation else None,
            "name": self._creation.name if self._creation else None,
            "identity": self.creation_identity(),
            "template": (
                str(self._creation.template.key)
                if self._creation is not None and self._creation.template is not None
                else None
            ),
            "region": self._creation.region if self._creation else None,
            "destination": (
                self._creation.destination.index
                if self._creation is not None
                and self._creation.destination is not None
                else None
            ),
            "arrival": self._creation.arrival if self._creation else None,
            "facing": self._creation.facing if self._creation else None,
            "staged": self._open_creation_key is not None,
            "state": self._creation_chip.accessibleName(),
            "reason": self._creation_refusal_text,
            "refusal": self.creation_refusal(),
            "name_editable": self._creation_name.isEnabled(),
            "apply_enabled": self._create_apply_button.isEnabled(),
        }

    def staged_creation_count(self) -> int:
        return len(self._staged_creations)

    def staged_creation(self, key: str):
        """The staged creation with one ``map:NNNN/transition:<name>`` key, or None."""
        for identity, creation in self._staged_creations.items():
            if identity.key == key:
                return creation
        return None

    def saved_creation(self, key: str):
        """The project's saved creation with one identity key, or None."""
        for identity, authored in self._committed_creations.items():
            if identity.key == key:
                return authored.creation
        return None

    def creation_row_keys(self) -> tuple[str, ...]:
        """This map's created transitions, in the order the list shows them."""
        if self._source_index is None:
            return ()
        return tuple(
            identity.key
            for identity in self._creation_identities_for(self._source_index)
        )

    def row_kind(self, row: int) -> str | None:
        """Whether one list row is a canonical connection or a created transition."""
        keys = self._row_keys()
        if not 0 <= row < len(keys):
            return None
        return (
            "created"
            if isinstance(keys[row], mt.CreatedTransitionIdentity)
            else "connection"
        )

    # -- the creation gestures -------------------------------------------------

    def stage_creation_name(self, name: str) -> bool:
        """Author the new transition's durable name."""
        return self._creation_gesture(lambda draft: draft.replaced(name=str(name)))

    def stage_creation_template(self, template) -> bool:
        """Base the new transition on an existing 566-class connection."""
        if not isinstance(template, mt.TransitionIdentity):
            return False
        return self._creation_gesture(
            lambda draft: draft.replaced(template=template)
        )

    def stage_creation_region(self, first, second) -> bool:
        """Author the new transition's source trigger region, positionally."""
        return self._creation_gesture(
            lambda draft: draft.replaced(
                region=(tuple(first), tuple(second))
            )
        )

    def stage_creation_destination(self, map_index: int) -> bool:
        """Point the new transition at a map."""
        try:
            destination = MapIdentity(int(map_index))
        except (TypeError, ValueError):
            return False
        return self._creation_gesture(
            lambda draft: draft.replaced(destination=destination)
        )

    def stage_creation_arrival(self, x: int, y: int) -> bool:
        """Author the point the new transition places the player at."""
        try:
            arrival = (int(x), int(y))
        except (TypeError, ValueError):
            return False
        return self._creation_gesture(lambda draft: draft.replaced(arrival=arrival))

    def stage_creation_facing(self, direction: int | None) -> bool:
        """Author the direction the player is turned on arrival, or author none."""
        return self._creation_gesture(
            lambda draft: draft.replaced(facing=direction)
        )

    def apply_creations(self) -> bool:
        """Commit every staged creation in ONE semantic project write.

        The authority validates the whole batch against the canonical image before
        anything is written (`set_transition_creations`), so a batch with one illegal
        entry writes nothing at all, and a batch the project already holds is
        reported as exactly that and changes no file.
        """
        if not self._staged_creations:
            self._publish_status("There is no staged new transition to apply.")
            return False
        project = self._session.project_dir
        image = self._session.map_image
        profile = self._session.profile
        if project is None:
            self._report_error("Apply new transition", _NO_CREATE_PROJECT)
            return False
        if image is None or profile is None:
            self._report_error("Apply new transition", _NO_IMAGE)
            return False
        try:
            changed = mt.set_transition_creations(
                project, profile, image, dict(self._staged_creations)
            )
        except _WARP_ERRORS as exc:
            self._report_error("Apply new transition", str(exc))
            return False
        # The write is committed, so what was staged is now the project's; the
        # authority is re-read once and the form re-derived against it.
        self._staged_creations.clear()
        self._open_creation_key = None
        self._undo_stack.clear()
        self._reload_committed()
        self._reapply_creation()
        if changed:
            self._session.project_mutated()
            self.projectChanged.emit()
            self._publish_status(
                "Applied the new transition to maps/transition_creations.toml. "
                "Validate and build to materialize it."
            )
        else:
            self._publish_status(
                "The project already held exactly this new transition; no file "
                "changed."
            )
        self.dirtyChanged.emit()
        return changed

    def revert_creation(self) -> bool:
        """Return the open creation to the last saved state, without any write.

        A staged creation is discarded - which is what makes a not-yet-saved
        creation cancellable with no project residue - and a saved creation is
        restored to the values the project holds. Either way the gesture is one undo
        entry, so Revert is itself reversible. Nothing here removes a creation from
        a project, and no canonical record is touched.
        """
        before = self._creation_state()
        draft = before.draft
        if draft is None:
            self._publish_status("Open Create transition to author a new connection.")
            return False
        identity = draft.identity()
        target = self._saved_draft(identity) if identity is not None else None
        if target is None:
            target = self._fresh_creation_draft(draft.source)
        if target == draft:
            self._publish_status(
                "The creation form already states the last saved values."
            )
            self._refresh_pages()
            return False
        after = self._resolve_creation_state(target, before.open_key)
        # Whether anything was staged is read from the state captured BEFORE the
        # command ran: `redo()` has already replaced the live staged set.
        was_staged = before.open_key is not None and before.open_key in dict(before.staged)
        self._undo_stack.push(StageCreationCommand(self, before, after))
        if was_staged:
            self._publish_status(
                "Discarded the staged new transition; nothing was written to the "
                "project. Undo brings it back."
            )
        else:
            self._publish_status(
                "The creation form is back at the values the project holds."
            )
        return True

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

    # -- the creation form's machinery ----------------------------------------

    def _fresh_creation_draft(self, source: MapIdentity) -> CreationDraft:
        """What a newly opened form starts from, stated rather than implied.

        The name is deliberately empty - the author supplies it, and the production
        model validates it. Everything else is seeded from the base the form shows:
        the base's own region, destination and arrival are visible starting values
        the author edits, and the facing starts at Unchanged because the SDK
        deliberately does NOT inherit the base's override (it was a decision about a
        different door).
        """
        entries = self._template_entries()
        if not entries:
            return CreationDraft(source)
        entry = entries[0]
        record = entry.record
        destination = None
        try:
            destination = self._corpus.destination(entry.identity)
        except _WARP_ERRORS:
            destination = None
        # The stored pair is read only where it IS a point: a record whose class
        # stores a scene-relative delta never reaches this branch through
        # `creation_templates`, and asking it for an arrival would be a claim about
        # a different structure's geometry.
        arrival = record.arrival if record.has_raw_arrival_pair else None
        return CreationDraft(
            source,
            template=entry.identity,
            region=(record.region.first, record.region.second),
            destination=destination,
            arrival=(arrival.x, arrival.y) if arrival is not None else (0, 0),
            facing=None,
        )

    def _saved_draft(self, identity) -> "CreationDraft | None":
        """The values the project holds for one created identity, or None."""
        authored = self._committed_creations.get(identity)
        if authored is None:
            return None
        return _draft_from_creation(authored.creation)

    def _template_entries(self) -> tuple:
        """The map's valid creation bases, from the authority's own rule."""
        if self._corpus is None or self._source_index is None:
            return ()
        try:
            return mt.creation_templates(
                self._corpus, MapIdentity(self._source_index)
            )
        except _WARP_ERRORS:
            return ()

    def _template_text(self, identity) -> str:
        """One existing connection described the way the list describes it."""
        destination = None
        if self._corpus is not None:
            try:
                destination = self._corpus.destination(identity)
            except _WARP_ERRORS:
                destination = None
        return (
            f"transition {identity.index:04d} \u00b7 leads to "
            f"{self._map_text(destination)}"
        )

    def _template_detail(self, identity) -> str:
        """The full description of a base, for the hint beside the control."""
        if self._corpus is None or identity is None:
            return _BASED_ON_REQUIRED
        try:
            record = self._corpus.entry(identity).record
        except _WARP_ERRORS:
            return _BASED_ON_REQUIRED
        region = self._region_values_text(record.region)
        if not record.has_raw_arrival_pair:
            # A 169-class record is never offered as a base (`creation_templates`
            # returns the measured 566 class alone); it can only reach the form
            # through a hand-edited document, and its stored pair is a delta rather
            # than a point, so no arrival is stated for it here.
            return f"{region} \u00b7 its stored pair is a scene-relative delta"
        return f"{region} \u00b7 arrives at {self._arrival_text(record.arrival)}"

    def _creation_from_draft(
        self, draft: "CreationDraft"
    ) -> tuple["mt.TransitionCreation | None", str | None]:
        """The creation a draft states, or the reason it does not state one yet."""
        if draft.template is None:
            return None, _BASED_ON_REQUIRED
        identity = draft.identity()
        if identity is None:
            if not draft.name:
                return None, "Author a name for the new transition."
            try:
                mt.CreatedTransitionIdentity(draft.source, draft.name)
            except mt.MapTransitionsError as exc:
                return None, str(exc)
            return None, "Author a name for the new transition."
        if draft.destination is None:
            return None, "Choose the map this transition leads to."
        try:
            region = TransitionRegion(first=draft.region[0], second=draft.region[1])
        except MapTransitionError as exc:
            return None, str(exc)
        try:
            arrival = TransitionArrival(x=draft.arrival[0], y=draft.arrival[1])
        except MapTransitionError as exc:
            return None, str(exc)
        try:
            creation = mt.TransitionCreation(
                identity=identity,
                template=draft.template,
                destination=draft.destination,
                region=region,
                arrival=arrival,
                facing=draft.facing,
            )
        except _WARP_ERRORS as exc:
            return None, str(exc)
        return creation, None

    def _check_creation(self, creation) -> str | None:
        """What the authority says about one creation, or None when it accepts it.

        The corpus is the one already loaded for this session, so a check on every
        gesture reads nothing (CQA-07), and the rules are the build's own.
        """
        if self._corpus is None:
            return self._corpus_error or _NO_IMAGE
        try:
            mt.check_transition_creation(self._corpus, creation)
        except _WARP_ERRORS as exc:
            return str(exc)
        return None

    def _creation_gesture(self, change) -> bool:
        """Record one authored creation gesture as one undo entry.

        Everything the gesture means - the draft it produces, the staged entry that
        draft asks for, and the authority's answer about it - is resolved HERE, as
        this method's own work. `QUndoCommand.redo` runs inside Qt's C++ undo stack,
        and a Python exception crossing a virtual override leaves that stack in a
        state Python cannot see (the command is on the stack and its redo never
        completed), so the command carries two fully resolved states and installing
        them reads and validates nothing.

        A gesture that asks for the values the form already states changes nothing
        and enters no history. An unexpected failure from the authority surfaces
        here, loudly, before any history exists.
        """
        before = self._creation_state()
        if before.draft is None:
            return False
        after_draft = change(before.draft)
        if after_draft == before.draft:
            self._publish_status("The new transition already holds these values.")
            self._refresh_pages()
            return False
        after = self._resolve_creation_state(after_draft, self._open_creation_key)
        self._undo_stack.push(StageCreationCommand(self, before, after))
        return True

    def _creation_state(self) -> "CreationState":
        """The whole creation surface's state, as an undo entry stores it."""
        return CreationState(
            draft=self._creation,
            staged=_staged_snapshot(self._staged_creations),
            open_key=self._open_creation_key,
            reason=self._creation_refusal_text,
        )

    def _resolve_creation_state(
        self, draft: "CreationDraft | None", previous
    ) -> "CreationState":
        """The state a draft produces: compose it, consult the authority, stage it.

        Staging is DERIVED from the form rather than remembered beside it, so a draft
        that stops being a creation - or that is renamed - cannot leave an entry
        behind under an identity the form no longer states. ``previous`` is the
        identity the open form was bound to before this change: its entry is dropped
        first and re-derived below, while a creation ANOTHER draft staged under the
        same identity survives and is reported as the conflict it is.

        A durable identity may be claimed by ONE creation. A name the project
        already creates is therefore refused for a form that is not bound to it -
        `previous != identity` - because "author a second transition with this name"
        and "re-author the one that exists" are different intentions and only the
        second may overwrite a document entry.
        """
        staged = dict(self._staged_creations)
        if previous is not None:
            staged.pop(previous, None)
        if draft is None:
            return CreationState(
                draft=None,
                staged=_staged_snapshot(staged),
                open_key=None,
                reason=None,
            )
        creation, reason = self._creation_from_draft(draft)
        if creation is None:
            return CreationState(draft, _staged_snapshot(staged), None, reason)
        identity = creation.identity
        saved = self._committed_creations.get(identity)
        if saved is not None and previous != identity:
            return CreationState(
                draft,
                _staged_snapshot(staged),
                None,
                f"{identity} is already a transition this project creates. A "
                "transition's identity is durable, so a second one cannot take it: "
                "open its row to re-author it, or author a different name.",
            )
        existing = staged.get(identity)
        if existing is not None and existing != creation:
            # A different draft already stages this durable identity. The project
            # document is keyed by it, so one of the two would silently win.
            return CreationState(
                draft,
                _staged_snapshot(staged),
                None,
                f"{identity} is already staged as a new transition with different "
                "values. Apply it, revert it, or author a different name.",
            )
        if saved is not None and saved.creation == creation:
            staged.pop(identity, None)
            return CreationState(
                draft,
                _staged_snapshot(staged),
                identity,
                f"The project already holds exactly this transition ({identity}); "
                "nothing is staged.",
            )
        refusal = self._check_creation(creation)
        if refusal is not None:
            staged.pop(identity, None)
            return CreationState(draft, _staged_snapshot(staged), identity, refusal)
        staged[identity] = creation
        return CreationState(draft, _staged_snapshot(staged), identity, None)

    def _install_creation_state(self, state: "CreationState") -> None:
        """Install a resolved state. The one place the creation surface changes.

        Nothing is read and nothing is validated here: this is what `redo()` and
        `undo()` call, so it must be total. Callers that need a state derived from
        the current project or corpus resolve one and install it.
        """
        self._creation = state.draft
        self._staged_creations = dict(state.staged)
        self._open_creation_key = state.open_key
        self._creation_refusal_text = state.reason
        self._creation_action_refusal = None
        self._populate_rows()
        self._populate_source_labels()
        # A refusal is what the author needs to read; the summary is what they need
        # when there is nothing wrong.
        self._publish_status(state.reason or self._summary_text())
        self.dirtyChanged.emit()

    def _reapply_creation(self) -> None:
        """Re-derive the open form against what the project now holds.

        A project mutation or a successful Apply changes what is committed, so the
        staged entry the form asks for can change with it - without disturbing the
        undo history, which describes the author's gestures rather than the file. The
        form stays bound to the identity it already states, which is what lets an
        applied creation be re-authored in place after Apply instead of reading as a
        second transition claiming a taken name.
        """
        bound = self._open_creation_key
        if bound is None and self._creation is not None:
            bound = self._creation.identity()
        self._install_creation_state(self._resolve_creation_state(self._creation, bound))

    def _creation_values(self, identity) -> "mt.TransitionCreation | None":
        """What a created row shows: this session's draft, else the project's."""
        staged = self._staged_creations.get(identity)
        if staged is not None:
            return staged
        authored = self._committed_creations.get(identity)
        return authored.creation if authored is not None else None

    def _creation_identities_for(self, index: int) -> tuple:
        """This map's created transitions, staged and saved, in name order.

        Name order is not decoration: it is the order a build appends them in
        (`materialize_transition_creations` sorts each map's creations by name), so
        the list reads the way the array grows.
        """
        source = MapIdentity(index)
        keys = {key for key in self._staged_creations if key.source == source}
        keys |= {key for key in self._committed_creations if key.source == source}
        return tuple(sorted(keys))

    def _open_creation_row(self, identity) -> bool:
        """Show a created row in the creation form, read-write."""
        creation = self._creation_values(identity)
        if creation is None:
            return False
        self._creation = _draft_from_creation(creation)
        # The draft IS the entry this row shows, so it is re-derived rather than
        # treated as a second creation of the same identity.
        self._install_creation_state(self._resolve_creation_state(self._creation, identity))
        return True

    def _sync_creation_widgets(self) -> None:
        """Render the draft into the widgets, and the authority's answer beside it."""
        draft = self._creation
        self._suppress = True
        try:
            if draft is None:
                self._pages.setCurrentIndex(0)
                return
            identity = draft.identity()
            self._creation_identity.setText(
                str(identity)
                if identity is not None
                else f"{draft.source.key}/transition:\u2026"
            )
            if self._creation_name.text() != draft.name:
                self._creation_name.setText(draft.name)
            self._show_creation_template(draft.template)
            for spin, value in zip(
                self._creation_region_spins,
                (
                    draft.region[0][0],
                    draft.region[0][1],
                    draft.region[1][0],
                    draft.region[1][1],
                ),
            ):
                if spin.value() != value:
                    spin.setValue(value)
            self._show_creation_destination(draft.destination)
            if self._creation_arrival_x.value() != draft.arrival[0]:
                self._creation_arrival_x.setValue(draft.arrival[0])
            if self._creation_arrival_y.value() != draft.arrival[1]:
                self._creation_arrival_y.setValue(draft.arrival[1])
            row = self._creation_facing.findData(draft.facing)
            if row >= 0 and self._creation_facing.currentIndex() != row:
                self._creation_facing.setCurrentIndex(row)
            elif row < 0:
                self._creation_facing.setCurrentIndex(0)
            self._creation_template_hint.setText(self._template_detail(draft.template))
            self._pages.setCurrentIndex(1)
        finally:
            self._suppress = False

    def _refresh_creation_form(self) -> None:
        """State the form's own condition: the chip, the reason and the buttons."""
        draft = self._creation
        refusal = self.creation_refusal()
        # The STAGED dict decides whether there is anything pending, not the binding:
        # a form that states exactly what the project holds is bound to that identity
        # and has nothing staged.
        staged = (
            self._open_creation_key is not None
            and self._open_creation_key in self._staged_creations
        )
        state, role = self._creation_display_state()
        saved_equal = state == _STATE_NEW_SAVED
        identity = draft.identity() if draft is not None else None
        # The name is durable once the form is BOUND to a saved creation - opened
        # from its row (a re-author in progress) or stating exactly what the project
        # holds. A form that merely collides with a saved name stays editable, because
        # its own refusal tells the author to author a different one.
        bound_to_saved = (
            identity is not None
            and identity in self._committed_creations
            and (self._open_creation_key == identity or saved_equal)
        )
        name_editable = refusal is None and draft is not None and not bound_to_saved
        if draft is None:
            self._creation_reason.setText("")
        else:
            self._creation_chip.set_state(state, role)
            self._creation_reason.setText(
                self._creation_refusal_text
                or ("" if staged else f"{identity} is saved in the project.")
            )
        self._set_creation_enabled(refusal is None and draft is not None)
        self._creation_name.setEnabled(name_editable)
        if not name_editable:
            # A field disabled while focused keeps its selection, which reads as an
            # edit in progress on a value that can no longer be edited.
            self._creation_name.deselect()
        if saved_equal:
            self._creation_name.setToolTip(
                "This transition is saved in the project, so its identity is fixed "
                "here. Its other values may still be re-authored and applied."
            )
        self._create_apply_button.setEnabled(bool(self._staged_creations))
        self._create_revert_button.setEnabled(
            draft is not None and (staged or self._creation_revertible())
        )
        self._create_close_button.setEnabled(draft is not None)

    def _creation_display_state(self) -> tuple[str, str]:
        """The chip's state and role: the same words the list row uses.

        A creation the project holds is **New (saved)** even though there is nothing
        left to stage - reporting "Not staged" there contradicted the row beside it.
        A gap or a refusal is the one state that is not a creation at all.
        """
        draft = self._creation
        if draft is None:
            return "Not staged", "neutral"
        if (
            self._open_creation_key is not None
            and self._open_creation_key in self._staged_creations
        ):
            return _STATE_NEW_STAGED, "pending"
        identity = draft.identity()
        if identity is not None:
            saved = self._committed_creations.get(identity)
            creation, _reason = self._creation_from_draft(draft)
            if saved is not None and creation is not None and saved.creation == creation:
                return _STATE_NEW_SAVED, "saved"
        if self._creation_refusal_text is not None:
            return "Not staged", "readonly"
        return "Not staged", "neutral"

    def _creation_revertible(self) -> bool:
        """Whether Revert has anything to do: a staged draft, or a saved departure."""
        draft = self._creation
        if draft is None:
            return False
        identity = draft.identity()
        saved = self._saved_draft(identity) if identity is not None else None
        return saved is not None and saved != draft

    def _set_creation_enabled(self, enabled: bool) -> None:
        for widget in (
            self._creation_template,
            self._creation_destination,
            self._creation_facing,
            self._creation_arrival_x,
            self._creation_arrival_y,
            *self._creation_region_spins,
        ):
            widget.setEnabled(enabled)

    def _show_creation_template(self, template) -> None:
        """Point the `Based on` control at the draft's base, or at nothing.

        The rows are matched by comparing the item data with the identity itself
        rather than by `findData`, because the data is an SDK value and the two are
        not guaranteed to be compared the same way by a QVariant.
        """
        row = -1
        if template is not None:
            for index in range(self._creation_template.count()):
                if self._creation_template.itemData(index) == template:
                    row = index
                    break
        self._creation_template.setCurrentIndex(row)

    def _populate_creation_templates(self) -> None:
        """Fill the `Based on` control from the authority's own template rule.

        `creation_templates` is what decides which existing connections may be a
        base, so a 169-class record cannot appear here however the corpus changes.
        Repopulating is not a gesture: the draft's own selection is re-applied under
        `_suppress`.
        """
        self._suppress = True
        try:
            self._creation_template.clear()
            for label, identity in self.creation_templates():
                self._creation_template.addItem(label, identity)
            if self._creation is not None:
                self._show_creation_template(self._creation.template)
        finally:
            self._suppress = False

    def _show_creation_destination(self, destination) -> None:
        if destination is None:
            self._creation_destination.setCurrentIndex(-1)
            return
        row = self._creation_destination.findData(destination.index)
        self._creation_destination.setCurrentIndex(row if row >= 0 else -1)

    # -- population -----------------------------------------------------------

    def _populate_after_session_change(self) -> None:
        """Rebuild every session-bound cache and put a real map on screen."""
        self._load_corpus()
        self._load_labels()
        self._reload_committed()
        self._populate_source_maps()
        self._populate_destination_maps()
        self._creation = None
        self._open_creation_key = None
        self._creation_refusal_text = None
        self._creation_action_refusal = None
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
        """Re-read the project's authored transitions, once (CQA-07).

        ONE project parse supplies both documents - the edits and the creations -
        because they are two tables of one project and re-reading it twice per
        mutation would be exactly the growth CQA-07 forbids. The conversions are the
        SDK's own (`transition_edits_to_requests`,
        `transition_creations_to_requests`), so this widget never parses a project
        key, a point pair or a facing byte. A document that cannot be read at all is
        a state: nothing is authorable against it until it is fixed, and the reason
        is what the surface says.
        """
        self._committed = {}
        self._committed_creations = {}
        self._project_error = None
        project = self._session.project_dir
        if project is None:
            return
        try:
            from tools.webfoot.project import read_project

            document = read_project(project)
            self._committed = dict(
                mt.transition_edits_to_requests(document.transitions)
            )
            self._committed_creations = dict(
                mt.transition_creations_to_requests(document.transition_creations)
            )
        except _WARP_ERRORS as exc:
            self._committed = {}
            self._committed_creations = {}
            self._project_error = (
                f"The project's transition documents could not be read: {exc}"
            )

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
        self._populate_creation_templates()

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
            self._creation_destination.clear()
            if self._corpus is None:
                return
            for index in range(self._corpus.map_count):
                label = self._map_label(index)
                self._destination.addItem(label, index)
                self._creation_destination.addItem(label, index)
        finally:
            self._suppress = False

    def _populate_rows(self) -> None:
        """The selected map's connections and created transitions, one row each.

        Canonical records come first, in array order, then the map's created
        transitions in the order a build appends them - so the list reads the way the
        image and the project actually are, and a new transition is visible the
        moment it is staged.
        """
        self._suppress = True
        try:
            self._table.clearContents()
            keys = self._row_keys()
            self._table.setRowCount(len(keys))
            for row, key in enumerate(keys):
                if isinstance(key, mt.CreatedTransitionIdentity):
                    self._fill_creation_row(row, key)
                else:
                    self._fill_row(row, key)
            self._reconcile_selection(keys)
        finally:
            self._suppress = False
        self._refresh_pages()

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

    def _row_keys(self) -> tuple:
        """Every visible row's selection key: records first, then creations."""
        if self._source_index is None:
            return ()
        return self._identities() + self._creation_identities_for(self._source_index)

    def _fill_creation_row(self, row: int, identity) -> None:
        """One row for a transition the PROJECT creates rather than the image holds.

        The first cell carries the authored name, because that is the second half of
        this transition's identity - a canonical row carries its own `IIII` there -
        and no array index exists for a record a build has not appended yet.
        """
        creation = self._creation_values(identity)
        if creation is None:  # pragma: no cover - a row only exists with a value
            return
        state = (
            _STATE_NEW_STAGED
            if identity in self._staged_creations
            else _STATE_NEW_SAVED
        )
        cells = (
            identity.name,
            self._map_text(creation.destination),
            self._region_values_text(creation.region),
            self._arrival_text(creation.arrival),
            self._facing_text(creation.facing),
            state,
        )
        for column, text in enumerate(cells):
            item = QTableWidgetItem(text)
            item.setToolTip(
                f"{identity}\n"
                f"Based on: {creation.template}\n"
                f"Trigger region: {cells[2]}\n"
                f"Leads to: {cells[1]}\n"
                f"Arrival: {cells[3]}\n"
                f"Facing: {cells[4]}\n"
                f"State: {state}"
            )
            self._table.setItem(row, column, item)

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
        # A refusal belongs to the map it was asked about.
        self._creation_action_refusal = None
        if self._creation is not None:
            # A creation belongs to ONE source map and its base must be a record of
            # that map, so the form follows the map bar by closing: an already staged
            # creation stays staged and stays listed under the map it belongs to -
            # clicking its row reopens it there - while a draft that never validated
            # is discarded, exactly as selecting another connection discards it.
            self._creation = None
            self._open_creation_key = None
            self._creation_refusal_text = None
        self._populate_creation_templates()
        self._populate_rows()
        self._refresh_map_support()
        self._publish_status(self._summary_text())

    def _on_row_selected(self) -> None:
        if self._suppress:
            return
        row = self._table.currentRow()
        keys = self._row_keys()
        if 0 <= row < len(keys):
            self._selected = keys[row]
        if isinstance(self._selected, mt.CreatedTransitionIdentity):
            self._open_creation_row(self._selected)
        else:
            self._creation = None
            self._open_creation_key = None
            self._creation_refusal_text = None
        self._refresh_pages()

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

    # -- the creation form's widgets ------------------------------------------

    def _on_creation_name_edited(self) -> None:
        if self._suppress or self._creation is None:
            return
        self.stage_creation_name(self._creation_name.text())

    def _on_creation_template_changed(self, _row: int) -> None:
        if self._suppress or self._creation is None:
            return
        template = self._creation_template.currentData()
        if template is None:
            return
        self.stage_creation_template(template)

    def _on_creation_region_changed(self) -> None:
        if self._suppress or self._creation is None:
            return
        low, high, low2, high2 = (
            spin.value() for spin in self._creation_region_spins
        )
        self.stage_creation_region((low, high), (low2, high2))

    def _on_creation_destination_changed(self, _row: int) -> None:
        if self._suppress or self._creation is None:
            return
        destination = self._creation_destination.currentData()
        if destination is None:
            return
        self.stage_creation_destination(int(destination))

    def _on_creation_arrival_changed(self) -> None:
        if self._suppress or self._creation is None:
            return
        self.stage_creation_arrival(
            self._creation_arrival_x.value(), self._creation_arrival_y.value()
        )

    def _on_creation_facing_changed(self, _row: int) -> None:
        if self._suppress or self._creation is None:
            return
        self.stage_creation_facing(self._creation_facing.currentData())

    def _refresh_pages(self) -> None:
        """Show the page the open creation implies, and render both pages.

        The creation form is a page rather than a dialog on purpose: a staged
        creation is visible in the list WHILE it is being authored, which is what
        makes "the new row appears immediately" true rather than a claim.
        """
        self._sync_creation_widgets()
        self._refresh_form()
        self._refresh_creation_form()

    def _refresh_form(self) -> None:
        """Render the selected connection: the form, the chip and the reason."""
        identity = self._selected
        if isinstance(identity, mt.CreatedTransitionIdentity):
            # A created transition is authored in the creation form, so this pane
            # states nothing about it rather than describing it as a record the
            # authority will not retarget.
            self._show_no_selection()
            return
        self._suppress = True
        try:
            refusal = self._edit_refusal()
            if identity is None:
                self._show_no_selection()
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

    def _show_no_selection(self) -> None:
        """Nothing of a PREVIOUS selection may stay on screen.

        A stale destination and arrival beside "no connection selected" reads as if
        some connection still had those values.
        """
        self._suppress = True
        try:
            self._identity.setText("Select a connection to edit it.")
            self._state_chip.set_state("No connection selected", "neutral")
            if self._creation_action_refusal is not None:
                # The Create action was refused on this map: that reason is the one
                # the author just asked for, so it outranks the generic empty state.
                self._reason.setText(self._creation_action_refusal)
            elif self._corpus_error is not None:
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
        if self._creation_action_refusal is not None:
            # The button that lives on this line was just refused: the reason belongs
            # beside it, where it wraps, rather than only in the status bar.
            self._map_support.setText(self._creation_action_refusal)
            return
        if self._corpus is None:
            self._map_support.setText(_NO_IMAGE)
            return
        if self._source_index is None:
            self._map_support.setText("No map selected.")
            return
        identities = self._identities()
        creations = self._creation_identities_for(self._source_index)
        if not identities and not creations:
            self._map_support.setText("This map has no connections to edit.")
            return
        staged = sum(1 for identity in identities if identity in self._staged)
        saved = sum(1 for identity in identities if identity in self._committed)
        new_staged = sum(1 for key in creations if key in self._staged_creations)
        new_saved = len(creations) - new_staged
        parts: list[str] = []
        if staged:
            parts.append(f"{staged} staged, not applied")
        if saved:
            parts.append(f"{saved} saved to the project")
        if new_staged:
            parts.append(f"{new_staged} new, staged")
        if new_saved:
            parts.append(f"{new_saved} new, saved")
        if self._session.project_dir is None:
            parts.append(_NO_PROJECT)
        self._map_support.setText(" \u00b7 ".join(parts))

    # -- labels and text ------------------------------------------------------

    def _edit_refusal(self) -> str | None:
        if self._selected is None:
            return None
        if isinstance(self._selected, mt.CreatedTransitionIdentity):
            # A created transition is not a record to retarget: it is authored in the
            # creation form, where it may be edited or reverted.
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
        return self._region_values_text(region)

    def _region_values_text(self, region) -> str:
        """Two intervals, named positionally exactly as the codec names them.

        Which interval is which is UNRESOLVED, so no axis name is invented here -
        for a record the corpus holds, or for one a project creates.
        """
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
        creations = self._creation_identities_for(self._source_index)
        staged = sum(1 for i in identities if i in self._staged)
        saved = sum(1 for i in identities if i in self._committed)
        new_staged = sum(1 for key in creations if key in self._staged_creations)
        new_saved = len(creations) - new_staged
        if not identities and not creations:
            return f"{name}: no connections to edit."
        parts = [
            f"{name}: {len(identities)} connection"
            f"{'s' if len(identities) != 1 else ''}"
        ]
        if saved:
            parts.append(f"{saved} saved")
        if staged:
            parts.append(f"{staged} staged, not applied")
        if new_saved:
            parts.append(f"{new_saved} new, saved")
        if new_staged:
            parts.append(f"{new_staged} new, staged")
        if self._session.project_dir is None:
            parts.append(_NO_PROJECT)
        return " \u00b7 ".join(parts)

    def _publish_status(self, text: str) -> None:
        self._status.setText(text)
        self.statusChanged.emit(text)


__all__ = ["CreationDraft", "StageCreationCommand", "StageTransitionCommand", "WarpTab"]
