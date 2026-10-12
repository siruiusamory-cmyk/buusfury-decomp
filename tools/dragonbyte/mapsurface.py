"""The Maps destination's model: layout cells, their chunks, and the warps.

Two editing worlds, one read of one immutable image. **Nothing here re-implements
an SDK codec or an SDK editing engine.** The authorities are the modules that own
the domains, and this module only asks them:

* the map table comes from `webfoot.maps`, exactly as the Data destination reads
  it, so a map identity is spelled once (`map:0012`);
* a layer, its cells and its chunk vocabulary come from
  `webfoot.map_paint.MapPainter`, which is the proven reader *and* the proven
  writer of a chunk cell (it verifies the image against the profile in its own
  constructor);
* the warps come from `webfoot.map_transitions`, which resolves a transition's
  destination through the engine's own two-byte lookup, and whose
  `MapTransitions.destination` is the only map-to-map edge this product may
  claim. `webfoot.maps.MapGraph` is read by nothing here: its own docstring says
  the destination is not derivable from verified data, so an edge taken from it
  would be an unproven relation.

What this module adds is the two things none of them has:

* a *view* that answers for one open image plus the open project, so a cell or a
  warp shows the value the project would build rather than the canonical one;
* a *change list*, staged through those same SDK authorities, which is where the
  owner-bearing `ByteChange` comes from: a layout cell's owner is the SDK's own
  `"map:NNNN layer N cell N"` and a warp's owner is the SDK's own
  `"map:NNNN/transition:NNNN"`, so "one edit produces one change owned by that
  row's identity" is a property passed through rather than stated.

A row that no evidence supports is not editable and carries the reason, which is
the only shape in which this surface reports a limit.

No Qt is imported: a test drives every answer with no window open.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import RomRange
from tools.webfoot.map_paint import (
    MapPaintError,
    MapPainter,
    PaintChunk,
    PaintLayer,
    PaintTarget,
)
from tools.webfoot.map_transitions import (
    MapTransitions,
    MapTransitionsError,
    TransitionEdit,
    TransitionIdentity,
    plan_transition_edits,
    read_map_transitions,
    transition_edits_to_requests,
)
from tools.webfoot.maps import (
    MapIdentity,
    Maps,
    load_maps,
)
from tools.webfoot.profile import RomProfile, RomProfileCatalog
from tools.webfoot.project import AuthoredTransition, LayoutEdits, TransitionEdits
from tools.webfoot.rom import RomIdentification
from tools.webfoot.write import ByteChange

from .datasurface import FieldValue
from .romsurface import image_address

#: The Maps destination's journal target. One target for the whole destination:
#: layout and warps are one authored subsystem, and a second target would give a
#: user two undos for one gesture. The map HEADER records are not here: they are
#: the Data destination's `data` target, and a second writer for them would be a
#: second authority over the same bytes.
MAPS_TARGET = "maps"

#: The layer a map's chunk cells live in, as `map_paint` classifies it.
DOMINANT = "dominant"


class MapSurfaceError(ValueError):
    """The open image's map domain could not be read; the message says why."""


@dataclass(frozen=True, slots=True)
class MapRow:
    """One map of the open image's table, as a list row."""

    index: int
    identity: str
    label: str
    file_offset: int
    size: int
    address: int
    warps: int


@dataclass(frozen=True, slots=True)
class LayerRow:
    """One of a map's four layer slots, with the vocabulary a cell may take.

    ``editable`` is false for a slot no evidence lets this product paint - an
    empty slot, a screen-entry layer, a terrain field, a one-chunk grid - and
    ``note`` then carries the SDK's own reason sentence rather than a new one.
    """

    map_index: int
    slot: int
    identity: str
    label: str
    classification: str
    columns: int
    rows: int
    cell_count: int
    chunks: tuple[PaintChunk, ...]
    editable: bool
    note: str

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)


@dataclass(frozen=True, slots=True)
class CellRow:
    """One chunk-window cell of one paintable layer.

    ``ordinal`` is the chunk's 1-based position in the map's accepted set - the
    value a project
    stores and the SDK resolves - or None for a cell whose pointer is the null
    pointer, which is the one cell state with no chunk to name.
    """

    map_index: int
    slot: int
    cell: int
    identity: str
    column: int
    row: int
    pointer: int
    ordinal: int | None
    offset: int
    editable: bool
    note: str

    @property
    def field(self) -> FieldValue:
        """The one editable field: this cell's chunk.

        0 is the honest spelling of "this cell carries no authored chunk", and it
        is offered only where there is something to remove. On a cell the open
        project does not author there is no such edit: the SDK refuses ordinal 0,
        and storing the removal anyway would claim a change with no bytes behind
        it.
        """
        return FieldValue(
            name="chunk",
            value=0 if self.ordinal is None else self.ordinal,
            minimum=0 if self.revertable else 1,
            maximum=self.maximum,
        )

    #: How many chunks the cell's layer offers, filled in by the surface so the
    #: row can state its own range without carrying the whole vocabulary again.
    maximum: int = 0
    #: Whether the open project authors a value for this cell, which is what
    #: makes 0 a real revert rather than an edit with nothing behind it.
    revertable: bool = False


@dataclass(frozen=True, slots=True)
class WarpRow:
    """One transition record of the open image, as the Warps list row."""

    identity: str
    source: int
    index: int
    label: str
    file_offset: int
    size: int
    destination: int | None
    destination_text: str
    region_text: str
    editable: bool
    note: str
    #: How many maps the destination field may name, for the field's own range.
    destinations: int = 0

    @property
    def field(self) -> FieldValue:
        """The one editable field: the map this warp leads to."""
        return FieldValue(
            name="destination",
            value=-1 if self.destination is None else self.destination,
            minimum=0,
            maximum=self.destinations - 1,
        )


class MapSurface:
    """One open image's map domain, plus whichever project is open with it.

    The painter and the transition corpus are read once and cached: both verify
    the image against the profile as they are built, and both answer the same way
    for the whole session, so a second read would only be a second identity gate.
    """

    def __init__(
        self,
        *,
        identification: RomIdentification,
        profile: RomProfile,
        image: bytes,
        maps: Maps,
        transitions: MapTransitions | None = None,
        transitions_problem: str = "",
    ) -> None:
        self.identification = identification
        self.profile = profile
        self.image = image
        self.maps = maps
        self.transitions = transitions
        self.transitions_problem = transitions_problem
        self._painter: MapPainter | None = None
        self._layers: dict[int, tuple[LayerRow, ...]] = {}
        self._warp_cache: tuple[object, tuple[ByteChange, ...]] | None = None

    # -- reading: the map list ------------------------------------------------

    def map_rows(self) -> tuple[MapRow, ...]:
        """Every map the open image's table declares, in table order."""
        warps = self._warps_per_map()
        rows: list[MapRow] = []
        for entry in self.maps.entries():
            index = entry.identity.index
            rows.append(
                MapRow(
                    index=index,
                    identity=entry.identity.key,
                    label=f"Map {index:04d}",
                    file_offset=entry.file_offset,
                    size=len(entry.original_bytes),
                    address=image_address(entry.file_offset, len(self.image)),
                    warps=warps.get(index, 0),
                )
            )
        return tuple(rows)

    def map_name(self, map_index: int) -> str:
        """The map's own published text, or an empty string where it has none.

        Read through the painter for the ONE selected map: the read costs a
        text decode per map, which is why the list carries identities only.
        """
        try:
            return self.painter().target(map_index).name or ""
        except MapPaintError:
            return ""

    # -- reading: layout ------------------------------------------------------

    def painter(self) -> MapPainter:
        if self._painter is None:
            self._painter = MapPainter(self.image, profile=self.profile)
        return self._painter

    def target(self, map_index: int) -> PaintTarget:
        """One map's layers, or raise `MapPaintError` naming the reason."""
        return self.painter().target(map_index)

    def layers(self, map_index: int) -> tuple[LayerRow, ...]:
        """One map's four layer slots, with their own read-only reasons."""
        cached = self._layers.get(map_index)
        if cached is not None:
            return cached
        try:
            target = self.target(map_index)
        except MapPaintError as exc:
            row = LayerRow(
                map_index=map_index,
                slot=-1,
                identity=f"map:{map_index:04d}",
                label="Layers",
                classification="",
                columns=0,
                rows=0,
                cell_count=0,
                chunks=(),
                editable=False,
                note=str(exc),
            )
            self._layers[map_index] = (row,)
            return (row,)
        rows = tuple(self._layer_row(map_index, layer) for layer in target.slots)
        self._layers[map_index] = rows
        return rows

    def _layer_row(self, map_index: int, layer: PaintLayer) -> LayerRow:
        return LayerRow(
            map_index=map_index,
            slot=layer.slot,
            identity=f"map:{map_index:04d} layer {layer.slot}",
            label=layer.label,
            classification=layer.classification,
            columns=layer.columns,
            rows=layer.rows,
            cell_count=layer.cell_count,
            chunks=layer.vocabulary,
            editable=layer.editable,
            note=layer.read_only_reason,
        )

    def layer(self, map_index: int, slot: int) -> LayerRow | None:
        return next(
            (row for row in self.layers(map_index) if row.slot == slot), None
        )

    def cells(
        self, map_index: int, slot: int, project: Any | None = None
    ) -> tuple[CellRow, ...]:
        """One layer's cells, showing the value the open project would build."""
        try:
            target = self.target(map_index)
        except MapPaintError:
            return ()
        layer = next((item for item in target.slots if item.slot == slot), None)
        if layer is None or not layer.editable:
            return ()
        authored = self._authored_layout(project)
        maximum = len(layer.vocabulary)
        rows: list[CellRow] = []
        for cell in layer.cells:
            value = authored.get((map_index, slot, cell.cell))
            ordinal = (
                layer.ordinal_of(cell.pointer) if cell.pointer else None
            )
            if type(value) is int:
                ordinal = value
            rows.append(
                CellRow(
                    map_index=map_index,
                    slot=slot,
                    cell=cell.cell,
                    identity=f"map:{map_index:04d} layer {slot} cell {cell.cell}",
                    column=cell.column,
                    row=cell.row,
                    pointer=cell.pointer,
                    ordinal=ordinal,
                    offset=cell.offset,
                    editable=True,
                    note=(
                        ""
                        if value is None
                        else f"this project paints chunk {value} here"
                    ),
                    maximum=maximum,
                    revertable=value is not None,
                )
            )
        return tuple(rows)

    # -- reading: warps -------------------------------------------------------

    def warps(
        self, project: Any | None = None, map_index: int | None = None
    ) -> tuple[WarpRow, ...]:
        """Every transition of this image, or one map's own, in array order."""
        if self.transitions is None:
            return ()
        rows: list[WarpRow] = []
        for entry in self.transitions.entries():
            identity = entry.identity
            if map_index is not None and identity.source.index != map_index:
                continue
            rows.append(self._warp_row(entry, project))
        return tuple(rows)

    def _warp_row(self, entry: Any, project: Any | None) -> WarpRow:
        identity = entry.identity
        record = entry.record
        authored = self._authored_warps(project).get(
            (identity.source.index, identity.index)
        )
        destination: int | None
        note = ""
        try:
            destination = self.transitions.destination(identity).index
        except MapTransitionsError as exc:
            destination = None
            note = str(exc)
        if authored is not None and authored.destination is not None:
            destination = int(authored.destination[4:], 10)
            note = f"this project sends it to map {destination:04d}"
        elif authored is not None and authored.destination is None:
            note = "this project authors this transition without a destination"
        return WarpRow(
            identity=str(identity),
            source=identity.source.index,
            index=identity.index,
            label=f"Transition {identity.index:04d}",
            file_offset=entry.file_offset,
            size=len(entry.original_bytes),
            destination=destination,
            destination_text=(
                "unresolved"
                if destination is None
                else f"Map {destination:04d}"
            ),
            region_text=_region_text(record.region),
            editable=destination is not None,
            note=note or ("" if destination is not None else "its destination resolves to no map"),
            destinations=self.transitions.map_count,
        )

    # -- planning -------------------------------------------------------------

    def changes(self, project: Any | None) -> tuple[ByteChange, ...]:
        """Every pending map edit, as the SDK's own owner-bearing changes."""
        if project is None:
            return ()
        return self._layout_changes(project) + self._warp_changes(project)

    def pending_bytes(self, project: Any | None) -> dict[int, bytes]:
        """The byte effect of every pending map edit, keyed by file offset.

        This is what the ROM surface materializes as its current bytes. Both
        changes here are fixed-width in-place rewrites - a four-byte chunk
        pointer, one 24-byte transition record - so an offset maps to its bytes
        without this module knowing anything about allocation.
        """
        return {change.offset: change.new for change in self.changes(project)}

    def _layout_changes(self, project: Any) -> tuple[ByteChange, ...]:
        edits = {
            key: value
            for key, value in self._authored_layout(project).items()
            if type(value) is int
        }
        if not edits:
            return ()
        return tuple(
            change
            for change in self.painter().changes(edits)
            if change.old != change.new
        )

    def _warp_changes(self, project: Any) -> tuple[ByteChange, ...]:
        requests = transition_edits_to_requests(project.transitions)
        if not requests or self.transitions is None:
            return ()
        # Keyed on the authored document's own identity: the authority re-decodes
        # the whole 735-record corpus per call, measured at 160 ms, and the ROM
        # surface asks for the project's byte effect on every render. A document
        # mutated in place rather than replaced would answer stale; nothing here
        # mutates one, and the journal replaces it on every commit, undo and redo.
        cached = self._warp_cache
        if cached is not None and cached[0] is project.transitions:
            return cached[1]
        application = plan_transition_edits(
            self.image, requests, profile=self.profile
        )
        changes = tuple(
            change for change in application.changes if change.old != change.new
        )
        self._warp_cache = (project.transitions, changes)
        return changes

    # -- the open project's own documents -------------------------------------

    @staticmethod
    def _authored_layout(project: Any | None) -> Mapping[tuple[int, int, int], Any]:
        if project is None:
            return {}
        return project.layout.cells()

    @staticmethod
    def _authored_warps(project: Any | None) -> Mapping[tuple[int, int], Any]:
        if project is None:
            return {}
        return project.transitions.edits()

    def _warps_per_map(self) -> dict[int, int]:
        if self.transitions is None:
            return {}
        counts: dict[int, int] = {}
        for entry in self.transitions.entries():
            counts[entry.identity.source.index] = (
                counts.get(entry.identity.source.index, 0) + 1
            )
        return counts


def _region_text(region: Any) -> str:
    if region is None:
        return ""
    first, second = region.first, region.second
    return f"[{first[0]}..{first[1]}] [{second[0]}..{second[1]}]"


# --- the one write path, in memory -------------------------------------------


def layout_span(row: CellRow) -> RomRange:
    """The four bytes one cell's chunk pointer occupies, as the ROM surface unit."""
    return RomRange(FileOffset(row.offset), 4)


def with_layout_cell(payload: Any, row: CellRow, ordinal: int) -> Any:
    """The authored project with one cell set to one chunk, mutating nothing.

    `ordinal` 0 means "this cell carries no authored chunk", which is the
    document's own removal - the same meaning `map_paint.set_layout_cells` gives
    ``None``. The cell's legality is not judged here: the caller plans the batch
    through the SDK's own painter before committing it.
    """
    flat = dict(payload.layout.cells())
    if ordinal:
        flat[(row.map_index, row.slot, row.cell)] = ordinal
    else:
        flat.pop((row.map_index, row.slot, row.cell), None)
    return replace(payload, layout=layout_from_cells(flat))


def layout_from_cells(
    cells: Mapping[tuple[int, int, int], int | str]
) -> LayoutEdits:
    """The document form of a flat cell map: the one place the key is regrouped."""
    maps: dict[str, dict[int, dict[int, int | str]]] = {}
    for (map_index, slot, cell), value in cells.items():
        maps.setdefault(LayoutEdits.key_for(map_index), {}).setdefault(slot, {})[
            cell
        ] = value
    return LayoutEdits(maps)


def with_warp_destination(
    payload: Any, corpus: MapTransitions, row: WarpRow, destination: int
) -> Any:
    """The authored project with one transition retargeted, mutating nothing.

    The stored prior is read from the canonical record through the SDK's own
    `MapTransitions.destination` - the same resolution the engine's two-byte
    lookup performs - and the authored value is the durable ``map:NNNN`` key, so
    the document proves the base it was authored against exactly as
    `set_transition_edits` writes it. Setting the destination back to the value
    the image already holds removes the pair rather than recording a pretend
    edit, which is that writer's own rule.
    """
    identity = TransitionIdentity(MapIdentity(row.source), row.index)
    target = MapIdentity(destination)
    before = corpus.destination(identity)
    key = (row.source, row.index)
    entry = payload.transitions.edits().get(key)
    flat = dict(payload.transitions.edits())
    if target == before:
        if entry is None:
            return payload
        if _authored_beyond_destination(entry):
            flat[key] = replace(
                entry, prior_destination=None, destination=None
            )
        else:
            flat.pop(key, None)
    else:
        flat[key] = replace(
            entry
            or AuthoredTransition(
                prior_destination=before.key, destination=target.key
            ),
            prior_destination=before.key,
            destination=target.key,
        )
    return replace(payload, transitions=TransitionEdits.from_edits(flat))


def _authored_beyond_destination(entry: AuthoredTransition) -> bool:
    """Whether this entry still authors something a destination-only edit cannot."""
    return (
        entry.region is not None
        or entry.arrival_authored
        or entry.facing_authored
    )


def check_transition(
    corpus: MapTransitions, row: WarpRow, destination: int
) -> None:
    """Refuse a retarget the SDK's own authority would refuse, or return.

    `MapTransitions.check_edit` stages the request through the same path the
    build uses and records nothing, so the surface cannot offer an edit the
    build would reject.
    """
    corpus.check_edit(
        TransitionIdentity(MapIdentity(row.source), row.index),
        TransitionEdit(destination=MapIdentity(destination)),
    )


def load_map_surface(
    rom_path: str,
    catalog: RomProfileCatalog,
    identification: RomIdentification,
    profile: RomProfile,
    image: bytes,
) -> MapSurface:
    """Read the map table and the transition corpus from one identified image.

    The map table is loaded through `webfoot.maps.load_maps` for the reason the
    Data surface does: it has no from-image entry point, and the profile it
    reports is compared against the open image's own, so a table read against
    another profile is a stated absence rather than a silently wrong extent. A
    profile that declares no map-entry table - Legacy of Goku II declares none
    against this codec - is that same stated absence: the Maps destination then
    says why it has nothing, and the ROM surface still works.

    The transition corpus is read from the bytes already in hand rather than
    re-opened, because the image is identified and its hash already checked.
    """
    try:
        maps = load_maps(rom_path, catalog)
    except (ValueError, OSError) as exc:
        raise MapSurfaceError(str(exc)) from exc
    if maps.profile.id != profile.id:
        raise MapSurfaceError(
            f"the map table was read against profile {maps.profile.id!r}, not the "
            f"open image's {profile.id!r}"
        )

    transitions: MapTransitions | None = None
    problem = ""
    try:
        transitions = read_map_transitions(image, profile)
    except MapTransitionsError as exc:
        problem = str(exc)

    return MapSurface(
        identification=identification,
        profile=profile,
        image=image,
        maps=maps,
        transitions=transitions,
        transitions_problem=problem,
    )
