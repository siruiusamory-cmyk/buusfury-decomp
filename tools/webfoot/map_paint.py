"""MAP-TILE-PAINT-001 - painting an existing map's chunk-cell layout.

The production authority for the *painting* capability, and nothing else. It
answers the questions a paint surface has to ask, against the immutable canonical
image, without inventing a representation the map format does not have:

* what one editable cell of a map actually is;
* which existing chunk values the selected layer offers as a brush;
* what a set of authored cell replacements serializes to, as attributed
  :class:`tools.webfoot.write.ByteChange` records for the one shared write plan.

The unit it paints is the engine's own. A supported (dominant) layer record is a
``chunk_x x chunk_y`` grid of **four-byte chunk pointers** at ``record + 0x18``;
each pointer names a 32x32 plane of 16-bit screen entries, i.e. a 256x256-pixel
chunk. The innermost unit the format lets an author *choose between* is therefore
the chunk, not the 8x8 hardware tile: a chunk plane is a shared container that
many cells point at, so writing an individual tile into a pointer's container
would silently rewrite every other cell that uses the same chunk. This module
paints chunk cells because that is what the format has, and it refuses to present
a finer brush than the format supports.

The replacement rule is the one MAP-LAYOUT-WRITE-001 proved, DRAGONBYTE-Z-MAP-
LAYOUT-EDITOR-001 shipped and MAP-PAINT-ANY-CHUNK-001 widened: a cell may only be
given a **non-null chunk pointer that already occurs in a dominant layer of the
same map**. That is why the legal
brush vocabulary is the map's existing chunks and why this module cannot
allocate, relocate, create a chunk, or resize a layer. Creating a brand-new chunk
is a different capability (Phase 2B) and is deliberately absent here.

Nothing in this module writes a file. It plans changes and it resolves authored
ordinals; :mod:`tools.webfoot.build` merges the plan into the one write plan and
:mod:`tools.webfoot.project` owns the authored text.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping

from .formats import map_graphics as mg
from .map_layout_write import (
    MapLayoutWriteError,
    MapLayoutWriter,
    validate_chunk_replacement,
)
from .packaged import packaged_profile
from .write import ByteChange

if TYPE_CHECKING:
    from .profile import RomProfile
    from .project.model import MapStructure


class MapPaintError(ValueError):
    """A paint target, brush value or authored edit could not be accepted.

    One public failure type for the whole surface, for the reason the map
    layout session gives: the readers below raise several unrelated
    ``ValueError`` subclasses, and a caller either paints or is refused. The
    message names the specific reason.
    """


#: Every failure family the readers under this module raise. Named explicitly
#: because they share no parent narrower than ``ValueError``; a caller that
#: catches one leaf would let its siblings escape.
_READ_ERRORS = (mg.MapGraphicsError, MapLayoutWriteError)

#: The engine's own chunk geometry, re-exported from the format layer so a
#: surface that draws a cell and a surface that plans one cannot disagree.
CHUNK_PIXELS = mg.CHUNK_PIXELS
CHUNK_SIDE_TILES = mg.CHUNK_SIDE_TILES


@dataclass(frozen=True, slots=True)
class PaintChunk:
    """One selectable brush value: a chunk a dominant layer of this map uses.

    ``ordinal`` is the 1-based position in this map's brush vocabulary, and it is
    the value an authored project stores - not ``pointer``. The pointer is
    published because a renderer needs it and because it is the honest identity
    of the value; the ordinal is published because it is the only form that
    survives being written into a project file.
    """

    ordinal: int
    pointer: int
    #: How many cells of this layer currently reference this chunk; 0 when the
    #: chunk comes from a sibling layer and this one holds it nowhere.
    cell_count: int
    #: The layer slot this chunk was first seen in. None means the edited layer
    #: itself; a slot number means the brush came from that sibling record, which
    #: is what the label has to say so a user is not choosing blind.
    source_slot: int | None = None
    #: This chunk's 1-based position inside the window of the layer that draws it.
    #: Chunk authoring names a chunk that way, so creating a chunk from a borrowed
    #: brush needs this and not ``ordinal``, which counts across the whole map.
    owner_ordinal: int = 0

    @property
    def label(self) -> str:
        if self.source_slot is None:
            return f"Chunk {self.ordinal}"
        return f"Chunk {self.ordinal} \u00b7 BG{self.source_slot}"


@dataclass(frozen=True, slots=True)
class PaintCell:
    """One row-major cell of an editable layer."""

    cell: int
    column: int
    row: int
    #: The chunk pointer the canonical image stores here; 0 is the null pointer
    #: the engine's own occupancy test reads as unoccupied.
    pointer: int
    #: File offset of the four-byte field a paint of this cell rewrites, or -1 for
    #: a cell that exists only in an authored grid: the record holding it is
    #: materialized by the build, so there is no canonical field to rewrite.
    offset: int


@dataclass(frozen=True, slots=True)
class PaintLayer:
    """One of a root's four layer slots, resolved for painting."""

    slot: int
    classification: str
    handler: int
    columns: int
    rows: int
    cells: tuple[PaintCell, ...]
    #: The legal brush values, in first-appearance order, numbered from 1.
    vocabulary: tuple[PaintChunk, ...]
    #: Non-empty when the slot cannot be painted, and why. A read-only state,
    #: not an error.
    read_only_reason: str
    #: MAP-RESIZE-AND-LAYERS-001. Set when this grid is the project's own - a
    #: resized layer or an authored layer - rather than the canonical record's.
    #: Its cells are still paintable and its vocabulary is still the accepted
    #: brush set, but a paint of it is a **semantic** edit the build materializes,
    #: not a four-byte in-place write, so no cell carries a canonical offset.
    structural: bool = False

    @property
    def editable(self) -> bool:
        return not self.read_only_reason

    @property
    def paintable(self) -> bool:
        """Whether a brush may be applied at all."""
        return self.editable

    @property
    def cell_count(self) -> int:
        return len(self.cells)

    @property
    def width(self) -> int:
        return self.columns * CHUNK_PIXELS

    @property
    def height(self) -> int:
        return self.rows * CHUNK_PIXELS

    @property
    def label(self) -> str:
        if self.classification == _DOMINANT:
            return f"BG{self.slot} · chunk grid {self.columns}×{self.rows}"
        return f"BG{self.slot} · {self.classification}"

    def contains(self, cell: object) -> bool:
        return type(cell) is int and 0 <= cell < len(self.cells)

    def cell_rect(self, cell: int) -> tuple[int, int, int, int]:
        """``(x, y, width, height)`` of one cell in the layer's own pixels."""
        column, row = self.column_of(cell), self.row_of(cell)
        return (
            column * CHUNK_PIXELS,
            row * CHUNK_PIXELS,
            CHUNK_PIXELS,
            CHUNK_PIXELS,
        )

    def column_of(self, cell: int) -> int:
        if not self.contains(cell):
            raise MapPaintError(f"chunk cell {cell!r} is outside BG{self.slot}")
        return cell % self.columns

    def row_of(self, cell: int) -> int:
        if not self.contains(cell):
            raise MapPaintError(f"chunk cell {cell!r} is outside BG{self.slot}")
        return cell // self.columns

    def cell_at(self, x: int, y: int) -> int | None:
        """The cell covering one pixel of this layer, or None outside it.

        The one place map pixels become a cell, so a drag gesture and a click
        cannot disagree about which cell the pointer is over.
        """
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return None
        return (y // CHUNK_PIXELS) * self.columns + (x // CHUNK_PIXELS)

    def chunk(self, ordinal: int) -> PaintChunk | None:
        """The vocabulary entry with this 1-based ordinal, or None."""
        if type(ordinal) is not int or not 1 <= ordinal <= len(self.vocabulary):
            return None
        return self.vocabulary[ordinal - 1]

    def ordinal_of(self, pointer: int) -> int | None:
        """The 1-based ordinal of a pointer in this map's vocabulary."""
        for entry in self.vocabulary:
            if entry.pointer == pointer:
                return entry.ordinal
        return None

    def pointer(self, ordinal: int) -> int | None:
        entry = self.chunk(ordinal)
        return None if entry is None else entry.pointer


@dataclass(frozen=True, slots=True)
class PaintTarget:
    """Everything one map offers a paint surface, and nothing it does not."""

    map_index: int
    #: The ROM-derived label, or None where the map publishes no text.
    name: str | None
    slots: tuple[PaintLayer, ...]

    @property
    def editable_layers(self) -> tuple[PaintLayer, ...]:
        return tuple(layer for layer in self.slots if layer.editable)

    @property
    def editable(self) -> bool:
        return bool(self.editable_layers)

    @property
    def read_only_reason(self) -> str:
        if self.editable:
            return ""
        details = "; ".join(
            f"BG{layer.slot} is {layer.read_only_reason}" for layer in self.slots
        )
        return f"no paintable dominant layer ({details})"

    @property
    def read_only_kind(self) -> str:
        """``unsupported``, ``no_alternative``, ``mixed`` or ``""``.

        The same three-state vocabulary the shipped layout editor publishes, so
        the map browser does not grow a second one.
        """
        if self.editable:
            return ""
        kinds = {
            "no_alternative" if layer.classification == _DOMINANT else "unsupported"
            for layer in self.slots
        }
        if kinds == {"no_alternative"}:
            return "no_alternative"
        if kinds == {"unsupported"}:
            return "unsupported"
        return "mixed"

    def layer(self, slot: int) -> PaintLayer:
        if type(slot) is not int or not 0 <= slot < len(self.slots):
            raise MapPaintError(f"layer slot {slot!r} is out of range")
        return self.slots[slot]


@dataclass(frozen=True, slots=True)
class PaintEdit:
    """One resolved authored replacement, and the exact bytes it rewrites."""

    map_index: int
    layer_slot: int
    cell: int
    ordinal: int
    #: The chunk pointer the canonical image holds at this cell.
    original: int
    #: The chunk pointer the authorized vocabulary resolves the ordinal to.
    replacement: int
    #: File offset of the four-byte field.
    offset: int

    @property
    def is_effective(self) -> bool:
        return self.original != self.replacement

    @property
    def owner(self) -> str:
        return f"map:{self.map_index:04d} layer {self.layer_slot} cell {self.cell}"

    def to_change(self, image: bytes) -> ByteChange:
        if self.offset < 0:
            raise MapPaintError(
                f"{self.owner} exists only in a grid the build materializes, so it "
                "has no canonical four-byte field to rewrite; a structural paint is "
                "persisted semantically and emitted by the structure domain"
            )
        return ByteChange(
            offset=self.offset,
            old=image[self.offset : self.offset + 4],
            new=self.replacement.to_bytes(4, "little"),
            owner=self.owner,
            reason=_REASON,
        )


#: The one reason string every layout paint records, so the build manifest and
#: the derivative provenance document name the same operation the same way.
_REASON = "authored chunk-cell paint"

_DOMINANT = "dominant"
_EDITABLE_CLASSIFICATION = _DOMINANT

#: Human names for the forms painting may not touch. Each completes "BGn is ...".
_READ_ONLY_FORMS = {
    "absent_placeholder": "an empty slot holding no layer",
    "static_graphical_screenblock": "a screen-entry layer, not the dominant chunk grid",
    "static_graphical_terrain_field": (
        "a terrain-field layer, the special graphical form Map 19 uses"
    ),
    "dominant_zero_grid": "a dominant record whose chunk grid has a zero dimension",
    "dominant_partial_zero_grid": (
        "a dominant record whose chunk grid has a zero dimension"
    ),
    "unclassified_handler": "an unclassified layer handler",
}


def _vocabulary(
    record: mg.LayerRecord,
    records: tuple[mg.LayerRecord, ...],
    cells: tuple[PaintCell, ...],
    lead: tuple[int, ...] | None = None,
) -> tuple[PaintChunk, ...]:
    """The brush vocabulary for one layer: its own chunks first, then its siblings'.

    ``lead`` overrides the layer's own window with the structural authority's fill
    vocabulary, so an ordinal a project already stored keeps resolving to the chunk
    it named. Otherwise the layer's own non-null pointers in first-appearance order
    lead, which is what keeps the ordinals of every existing project stable. A
    chunk's ``source_slot`` is the record it was first seen in, and ``owner_ordinal``
    is its 1-based position inside that record's window, which is the number chunk
    authoring resolves a template against.
    """
    groups: list[tuple[int, tuple[int, ...]]] = [
        (record.slot, lead if lead is not None else record.chunk_addresses)
    ]
    groups.extend(
        (sibling.slot, sibling.chunk_addresses)
        for sibling in records
        if sibling.slot != record.slot
    )
    source: dict[int, int] = {}
    order: list[int] = []
    owned: dict[int, int] = {}
    for group_slot, window in groups:
        position = 0
        for pointer in window:
            if not pointer:
                continue
            position += 1
            if pointer not in source:
                source[pointer] = group_slot
                order.append(pointer)
            owned.setdefault(pointer, position)
    return tuple(
        PaintChunk(
            ordinal=ordinal,
            pointer=pointer,
            cell_count=sum(1 for cell in cells if cell.pointer == pointer),
            source_slot=source[pointer] if source[pointer] != record.slot else None,
            owner_ordinal=owned[pointer],
        )
        for ordinal, pointer in enumerate(order, start=1)
    )


class MapPainter:
    """Read-only paint authority over one immutable canonical image.

    One reader and one writer are built for the session: the writer is the
    proven fixed-width cell writer, and its constructor is what verifies the
    image against the profile, so nothing here re-implements the identity gate.
    """

    def __init__(
        self,
        canonical_bytes: bytes,
        *,
        profile: "RomProfile | None" = None,
        structure: "MapStructure | None" = None,
    ) -> None:
        self._base = bytes(canonical_bytes)
        resolved = profile if profile is not None else packaged_profile()
        try:
            self._writer = MapLayoutWriter(self._base, profile=resolved)
            self._reader = mg.MapGraphicsReader(self._base, resolved)
            self._entries = mg.read_map_entries(self._reader)
        except _READ_ERRORS as exc:
            raise MapPaintError(str(exc)) from exc
        self._targets: dict[int, PaintTarget] = {}
        # MAP-RESIZE-AND-LAYERS-001. A project that authored a resize or an
        # authored layer has a grid the canonical record does not state, so the
        # paint surface must read it from the project and not from the ROM. The
        # document is optional and a canonical session passes none, which leaves
        # every existing behaviour byte-identical.
        self._structure = structure
        self._structural_slots = (
            structure.structural_slots() if structure is not None else frozenset()
        )

    @property
    def map_entry_count(self) -> int:
        """The profile's declared MapEntry count: the live index bound."""
        return self._reader.map_entry_count()

    @property
    def image(self) -> bytes:
        return self._base

    # -- what may be painted -----------------------------------------------

    def target(self, map_index: int) -> PaintTarget:
        """Read (and cache) one map's layer slots, resolved for painting."""
        count = self.map_entry_count
        if type(map_index) is not int or not 0 <= map_index < count:
            raise MapPaintError(
                f"map index {map_index!r} is outside this profile's 0..{count - 1} "
                "declared map-entry range"
            )
        cached = self._targets.get(map_index)
        if cached is None:
            try:
                cached = self._build_target(map_index)
            except _READ_ERRORS as exc:
                raise MapPaintError(f"map:{map_index:04d} could not be read: {exc}") from exc
            self._targets[map_index] = cached
        return cached

    def _build_target(self, map_index: int) -> PaintTarget:
        entry = self._entries[map_index]
        name = None
        if entry.text_index is not None:
            name = self._reader.text(entry.text_index) or None
        records = mg.read_layers(self._reader, entry.root_address)
        slots: list[PaintLayer] = []
        for record in records:
            slots.append(self._build_layer(map_index, record, records))
        return PaintTarget(map_index=map_index, name=name, slots=tuple(slots))

    def _build_layer(
        self,
        map_index: int,
        record: mg.LayerRecord,
        records: tuple[mg.LayerRecord, ...],
    ) -> PaintLayer:
        if (map_index, record.slot) in self._structural_slots:
            return self._structural_layer(map_index, record, records)
        if record.classification != _EDITABLE_CLASSIFICATION:
            return PaintLayer(
                slot=record.slot,
                classification=record.classification,
                handler=record.handler,
                columns=0,
                rows=0,
                cells=(),
                vocabulary=(),
                read_only_reason=_READ_ONLY_FORMS.get(
                    record.classification, "an unclassified layer handler"
                ),
            )
        cells = tuple(
            PaintCell(
                cell=index,
                column=index % record.chunk_x,
                row=index // record.chunk_x,
                pointer=pointer,
                offset=self._writer.chunk_pointer_offset(map_index, record.slot, index),
            )
            for index, pointer in enumerate(record.chunk_addresses)
        )
        # The brush vocabulary is this layer's own non-null pointers in
        # first-appearance order, then whatever its sibling records add: the one
        # accepted replacement set for this map, with the layer's own chunks
        # keeping their familiar low ordinals.
        vocabulary = _vocabulary(record, records, cells)
        return PaintLayer(
            slot=record.slot,
            classification=record.classification,
            handler=record.handler,
            columns=record.chunk_x,
            rows=record.chunk_y,
            cells=cells,
            vocabulary=vocabulary,
            read_only_reason=self._read_only_reason(
                record.chunk_x, record.chunk_y, vocabulary
            ),
        )

    def _structural_layer(
        self,
        map_index: int,
        record: mg.LayerRecord,
        records: tuple[mg.LayerRecord, ...],
    ) -> PaintLayer:
        """A grid the project authored, read through the structural authority.

        The geometry, the effective cell pointers and the fill vocabulary come from
        ``map_resize``, so a resize and a paint of it cannot disagree about how many
        cells the layer has. The *brush* vocabulary is the map's accepted
        replacement set, the same one :meth:`_build_layer` offers, so a grid the
        project authored is paintable with the same chunks a canonical grid is.
        Only cells that also exist in the canonical record carry an offset; the
        rest exist solely in the record the build materializes, and a paint of them
        is persisted semantically rather than written in place.
        """
        from .map_resize import MapStructureError, MapResizer

        try:
            resizer = MapResizer(
                self._base, structure=self._structure, profile=self._writer.profile
            )
            layer = resizer.target(map_index).layer(record.slot)
        except MapStructureError as exc:
            raise MapPaintError(f"map:{map_index:04d} BG{record.slot}: {exc}") from exc
        retail_cells = len(record.chunk_addresses)
        cell_offsets: list[int] = []
        for index in range(layer.cell_count):
            column, row = index % layer.columns, index // layer.columns
            # A new cell has a canonical four-byte field only when its own
            # coordinate is inside the retail grid, and then it is the RETAIL
            # cell's field: the transform is top-left anchored, so a new index
            # does not address a canonical cell while the column count differs.
            if (
                retail_cells
                and column < record.chunk_x
                and row < record.chunk_y
            ):
                cell_offsets.append(
                    self._writer.chunk_pointer_offset(
                        map_index, record.slot, row * record.chunk_x + column
                    )
                )
            else:
                cell_offsets.append(-1)
        cells = tuple(
            PaintCell(
                cell=index,
                column=index % layer.columns,
                row=index // layer.columns,
                pointer=layer.cells[index],
                offset=cell_offsets[index],
            )
            for index in range(layer.cell_count)
        )
        # The structural grid's own fill vocabulary leads, so an ordinal already
        # stored in a project keeps resolving to the chunk it named.
        own = tuple(choice.address for choice in layer.vocabulary)
        vocabulary = _vocabulary(record, records, cells, lead=own)
        return PaintLayer(
            slot=record.slot,
            classification=_DOMINANT,
            handler=record.handler,
            columns=layer.columns,
            rows=layer.rows,
            cells=cells,
            vocabulary=vocabulary,
            read_only_reason=self._read_only_reason(
                layer.columns, layer.rows, vocabulary
            ),
            structural=True,
        )

    @staticmethod
    def _read_only_reason(
        columns: int, rows: int, vocabulary: tuple[PaintChunk, ...]
    ) -> str:
        """Why a dominant slot has no brush, or "" when it has.

        A cell may only be given a chunk some dominant layer of the same map
        already uses, so a map whose dominant layers between them hold one chunk
        has nothing to paint with: a 1x1 grid holds one cell, and a larger grid
        repeating one chunk has no second value to place. That is a read-only
        state, not a failure. A layer with a single chunk of its own whose
        sibling records hold others is NOT read-only: the brush vocabulary is the
        map's set, so it has something to place.
        """
        if not columns * rows:
            return "a dominant record whose chunk grid has a zero dimension"
        if len(vocabulary) < 2:
            return (
                f"a grid of {columns * rows} cell(s) using a single chunk, so it "
                "has no other chunk to paint with"
            )
        return ""

    def layer(self, map_index: int, layer_slot: int) -> PaintLayer:
        return self.target(map_index).layer(layer_slot)

    # -- resolving authored edits ------------------------------------------

    def resolve(self, map_index: int, layer_slot: int, cell: int, ordinal: int) -> PaintEdit:
        """Resolve one authored replacement into the exact bytes it rewrites.

        Every refusal the write side cares about happens here, before anything
        is planned: an unsupported layer, a cell outside the layer's own grid, a
        non-integer or out-of-range ordinal, and a pointer no dominant layer of
        this map already uses.

        A replacement that resolves to the value the cell already holds is NOT a
        refusal - see the note at the end of the method - so callers that need
        "did anything actually change?" read :attr:`PaintEdit.is_effective`.
        """
        layer = self.layer(map_index, layer_slot)
        if not layer.editable:
            raise MapPaintError(
                f"BG{layer_slot} of map:{map_index:04d} is not editable: "
                f"{layer.read_only_reason}"
            )
        if not layer.contains(cell):
            raise MapPaintError(
                f"chunk cell {cell!r} is outside BG{layer_slot}'s "
                f"{layer.columns}×{layer.rows} grid"
            )
        if type(ordinal) is not int:
            raise MapPaintError("a chunk ordinal must be an integer")
        entry = layer.chunk(ordinal)
        if entry is None:
            raise MapPaintError(
                f"chunk ordinal {ordinal!r} is outside BG{layer_slot}'s "
                f"{len(layer.vocabulary)} existing chunk(s)"
            )
        original = layer.cells[cell].pointer
        try:
            # The accepted replacement rule is "a chunk a dominant layer of this
            # map already uses", and the vocabulary IS that set - the layer's own
            # chunks first, then its siblings'. A structural layer's cells are
            # mostly one initialization value, so the layer does not yet *hold*
            # the rest of its vocabulary, but `layer.chunk(ordinal)` has already
            # refused anything outside it.
            validate_chunk_replacement(
                tuple(chunk.pointer for chunk in layer.vocabulary), entry.pointer
            )
            mg.dominant_chunk_words(self._reader, entry.pointer)
        except _READ_ERRORS as exc:
            raise MapPaintError(str(exc)) from exc
        # A paint of the value the cell already holds is NOT an error. It is
        # frequently unavoidable rather than accidental: a drag re-enters cells
        # it has already painted, a merged gesture replays its own work, and an
        # author may re-issue the same gesture at any time. The resolved edit is
        # returned with `is_effective` false, and the planner and the project
        # writer both treat that as "nothing to do" rather than as a refusal -
        # which is what keeps a no-op paint from creating project mutation or a
        # meaningless byte change.
        return PaintEdit(
            map_index=map_index,
            layer_slot=layer_slot,
            cell=cell,
            ordinal=ordinal,
            original=original,
            replacement=entry.pointer,
            offset=layer.cells[cell].offset,
        )

    def changes(self, edits: Mapping[tuple[int, int, int], int]) -> tuple[ByteChange, ...]:
        """Plan authored ``(map, layer, cell) -> ordinal`` edits as byte changes.

        The one place an authored layout becomes a write. Every edit is resolved
        first and the whole set is returned only when all of them are legal, so a
        batch containing one bad entry writes nothing rather than part of itself.

        An edit whose resolved pointer already occupies the cell is a no-op and
        contributes nothing: it is not an error, because the canonical image may
        already agree with the author, and ``plan_changes`` would drop it anyway.
        """
        if not edits:
            return ()
        resolved: list[PaintEdit] = []
        for (map_index, layer_slot, cell), ordinal in sorted(edits.items()):
            edit = self.resolve(map_index, layer_slot, cell, ordinal)
            if edit.is_effective:
                resolved.append(edit)
        return tuple(edit.to_change(self._base) for edit in resolved)
    def overrides(self, edits: Mapping[tuple[int, int, int], int | str]) -> dict[int, dict[int, int]]:
        """Authored edits for one map as ``{layer slot: {cell: pointer}}``.

        The form the accepted renderer's ``chunk_overrides`` takes, so a preview
        of authored content goes through the same pipeline that draws the retail
        layout rather than through a second renderer.

        A value that is a ``str`` is a project-authored chunk identity
        (MAP-CHUNK-AUTHORING-001) - the *other* value form an authored layout cell
        may hold. It is not an ordinal and this module cannot resolve one, so it is
        skipped here and resolved by :mod:`tools.webfoot.map_chunk`; a caller that
        wants both merges the two. Skipping is deliberate rather than refusing:
        this method is what a map surface calls to build a preview, and a project
        that places an authored chunk must not make that preview unreadable.
        """
        result: dict[int, dict[int, int]] = {}
        for (map_index, layer_slot, cell), ordinal in sorted(edits.items()):
            if type(ordinal) is not int:
                continue
            edit = self.resolve(map_index, layer_slot, cell, ordinal)
            result.setdefault(edit.map_index, {}).setdefault(edit.layer_slot, {})[
                edit.cell
            ] = edit.replacement
        return result

    def overrides_for(
        self, map_index: int, edits: Mapping[tuple[int, int, int], int | str]
    ) -> dict[tuple[int, int], int]:
        """:meth:`overrides` for one map, keyed ``(layer slot, cell)``."""
        return {
            (slot, cell): pointer
            for slot, cells in self.overrides(edits).get(map_index, {}).items()
            for cell, pointer in cells.items()
        }

    def pointer_edits(
        self, edits: Mapping[tuple[int, int, int], int | str]
    ) -> dict[tuple[int, int, int], int]:
        """Authored ordinals resolved to pointers, keyed by the full triple.

        The form a layout *session's* committed layer takes: it needs the map as
        well as the layer and cell, because one session covers every map of the
        image. Every ordinal is resolved through the same authority a build uses,
        so a session can never hold a pointer the build would refuse.

        An authored-chunk identity is skipped for the reason :meth:`overrides`
        gives; ``MapLayoutEditor.set_floor`` is the caller, and its floor is the
        canonical-ordinal layer.
        """
        resolved: dict[tuple[int, int, int], int] = {}
        for (map_index, layer_slot, cell), ordinal in sorted(edits.items()):
            if type(ordinal) is not int:
                continue
            edit = self.resolve(map_index, layer_slot, cell, ordinal)
            resolved[(edit.map_index, edit.layer_slot, edit.cell)] = edit.replacement
        return resolved


def paint_target(
    canonical_bytes: bytes, map_index: int, *, profile: "RomProfile | None" = None
) -> PaintTarget:
    """One map's paintable layers, read from the canonical image."""
    return MapPainter(canonical_bytes, profile=profile).target(map_index)


def plan_layout_cells(
    canonical_bytes: bytes,
    edits: Mapping[tuple[int, int, int], int],
    *,
    profile: "RomProfile | None" = None,
) -> tuple[ByteChange, ...]:
    """Plan authored chunk-cell paints as attributed byte changes.

    The build-side entry point: it turns the persisted semantic edits into the
    exact four-byte in-place writes the proven writer authorizes, and raises
    :class:`MapPaintError` naming the offending map/layer/cell for anything else.
    """
    return MapPainter(canonical_bytes, profile=profile).changes(edits)


# --- authoring: project persistence ------------------------------------------
#
# The one authority through which a paint reaches the project. It is shaped like
# `graphics.set_palette_overrides` on purpose: validate the WHOLE batch, load the
# project ONCE, apply the batch on top of what is committed, and write only when
# the result actually differs. That is what makes a stroke of many cells one
# write, an undo of a cell that was never authored a removal, and a re-paint that
# changes nothing a no-op.


def read_layout_edits(project_dir) -> "LayoutEdits":
    """The committed authored layout edits for a project, in one load.

    Reads the project's own document only. It does not consult an image, so a
    caller that only wants to know what is authored can ask without one.
    """
    from .project import read_project

    return read_project(project_dir).layout


def set_layout_cells(
    project_dir,
    profile: "RomProfile",
    canonical_bytes: bytes,
    edits: Mapping[tuple[int, int, int], int | None],
) -> bool:
    """Validate and persist a whole batch of chunk-cell paints in ONE write.

    ``edits`` maps ``(map index, layer slot, cell)`` to the 1-based ordinal of a
    chunk a dominant layer of the same map uses, or to ``None`` meaning "this cell carries no
    authored paint" (which is how an undo of a cell that was never painted
    reverses, and how the palette batch spells a removal).

    Semantics, in order:

    * the WHOLE batch is validated against the canonical image first, through the
      same :class:`MapPainter` the build uses, so a batch containing one illegal
      entry writes nothing at all rather than half of itself, and "what may be
      painted" and "what may be built" cannot drift apart;
    * then the project is loaded ONCE, the batch is applied on top of the
      committed edits, and the document is rewritten only when the resulting set
      differs from the one that was loaded;
    * a resulting set that is empty REMOVES the document rather than writing an
      invalid empty table, and the return value says whether project source
      actually changed - which is what an undo stack needs to know and what keeps
      a no-op paint from creating a project revision.

    A removal is validated too, but only for the cell's identity: an ordinal is
    not needed to un-paint a cell, and requiring the canonical layer to still
    offer it would make an undo fail after an unrelated ROM change.
    """
    from .project import LayoutEdits, write_layout_edits

    # 2. Load once, so both the painter and the merge see the same committed
    # state. MAP-RESIZE-AND-LAYERS-001: the painter is given the project's own
    # structural document, so a cell of a resized layer - or of a project-authored
    # layer - is validated against the grid the project declares rather than
    # against the canonical record it replaced, and the paint surface and the
    # build cannot disagree about how many cells the layer has.
    from .project import read_project

    project = read_project(project_dir)
    painter = MapPainter(
        canonical_bytes, profile=profile, structure=project.structure
    )

    # 1. Validate the whole batch before touching the project.
    for key, ordinal in edits.items():
        map_index, layer_slot, cell = _paint_key(key)
        if ordinal is None:
            layer = painter.layer(map_index, layer_slot)
            if not layer.contains(cell):
                raise MapPaintError(
                    f"chunk cell {cell!r} is outside BG{layer_slot}'s "
                    f"{layer.columns}×{layer.rows} grid"
                )
            continue
        painter.resolve(map_index, layer_slot, cell, ordinal)

    # 2. Apply on top of what is committed.
    committed = project.layout
    document: dict[str, dict[int, dict[int, int]]] = {
        key: {slot: dict(cells) for slot, cells in layers.items()}
        for key, layers in committed.maps.items()
    }
    for key, ordinal in edits.items():
        map_index, layer_slot, cell = _paint_key(key)
        map_key = LayoutEdits.key_for(map_index)
        if ordinal is None:
            layers = document.get(map_key)
            if layers is None:
                continue
            cells = layers.get(layer_slot)
            if cells is None:
                continue
            cells.pop(cell, None)
            if not cells:
                layers.pop(layer_slot, None)
            if not layers:
                document.pop(map_key, None)
            continue
        document.setdefault(map_key, {}).setdefault(layer_slot, {})[cell] = ordinal

    updated = LayoutEdits(maps=document)
    if updated.maps == committed.maps:
        return False
    write_layout_edits(project_dir, updated)
    return True


def set_layout_cell(
    project_dir,
    profile: "RomProfile",
    canonical_bytes: bytes,
    map_index: int,
    layer_slot: int,
    cell: int,
    ordinal: int,
) -> bool:
    """The one-cell spelling of :func:`set_layout_cells`."""
    return set_layout_cells(
        project_dir, profile, canonical_bytes, {(map_index, layer_slot, cell): ordinal}
    )


def clear_layout_cell(
    project_dir,
    profile: "RomProfile",
    canonical_bytes: bytes,
    map_index: int,
    layer_slot: int,
    cell: int,
) -> bool:
    """Remove one authored paint, restoring the canonical value for that cell."""
    return set_layout_cells(
        project_dir, profile, canonical_bytes, {(map_index, layer_slot, cell): None}
    )


def _paint_key(key: object) -> tuple[int, int, int]:
    """Destructure one ``(map, layer, cell)`` batch key, or refuse it.

    A malformed key is a ``MapPaintError`` like any other bad edit rather than a
    ``TypeError`` or ``ValueError`` out of argument unpacking, which would be
    outside the family a GUI boundary catches - the documented dead-click
    failure mode.
    """
    if not isinstance(key, tuple) or len(key) != 3:
        raise MapPaintError(
            "a layout edit key must be a (map index, layer slot, cell) triple"
        )
    map_index, layer_slot, cell = key
    for name, value in (
        ("map index", map_index),
        ("layer slot", layer_slot),
        ("cell", cell),
    ):
        if type(value) is not int:
            raise MapPaintError(f"a layout edit's {name} must be an integer")
    return map_index, layer_slot, cell
