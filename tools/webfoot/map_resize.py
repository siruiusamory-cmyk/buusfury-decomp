"""MAP-RESIZE-AND-LAYERS-001: the production authority for map **structure**.

Phase 2C owns two operations that change a supported map's own shape rather than
the cells inside it:

**RESIZE** grows a supported dominant layer's chunk grid. The grid is stated by
two bytes on the layer record (``+0x14``/``+0x15``) and its chunk-pointer window
follows immediately at ``+0x18``, so a grid that grows does not fit where it was:
the record is `header + window` and nothing else, and the bytes right after the
window belong to the next structure. A resized layer's record is therefore
re-emitted whole and placed through the production allocator, and the map root's
own layer-slot pointer is repointed at it.

**LAYER AUTHORING** activates one of a map root's four layer slots with a new
supported layer record. The engine's layer count is fixed at four - a root
carries exactly four slot pointers, all non-null on all 452 canonical roots, and
an unused slot points at one shared zero-dimension placeholder - so "create a new
layer" means exactly what the engine can do: point an unused slot at a new
dominant record. No dynamic layer list the engine does not possess is invented
here.

**A CREATED LAYER CAN ALSO BE GROWN.** The two are independent facts about one
slot - "this record is the project's, created at this grid" and "its grid is this
one" - and the resize half of this capability applies to the layers the project
itself created, not only to retail ones. So one slot may carry both: a `[layer]`
entry declares the grid the layer was created at and a `[resize]` entry on the
same `map:NNNN/BGn` key declares the grid it is grown to. Then the resize's base
grid is the **authored** layer's, not the canonical slot's (which is the shared
zero-dimension placeholder): the authored layer's own cells keep their
coordinates in the grown grid, only the cells the growth adds take the resize's
initialization, and the emitted record's header still comes from the authored
layer's template. Two `[layer]` entries, or two `[resize]` entries, for one slot
stay refused - that is still a real double claim.

**What a resize is, stated exactly.** Growing a layer's plane does not by itself
put the new area on screen: the map root also declares a pixel **extent**
(``+0x08``/``+0x0A``, ``ldrh``) which the engine loads into its per-map camera
state as ``extent - 1`` and uses as the **maximum camera scroll** per axis - the
camera clamp at ``0x080094F0`` saturates the requested view origin to
``[0, extent - 1]``, and the in-play camera update at ``0x08009744`` re-reads the
same pair. A grow therefore also raises that word, to ``plane_pixels - viewport``
per axis, which is exactly the value at which the grown plane's far edge becomes
reachable, and never lowers it. The extent gates the camera and nothing else - no
actor-position code reads it - so it is the camera's reach, not the player's
walkable area, that a resize has to extend. An authored layer does NOT touch the
extent: it adds a visual layer inside the map the author already has, and changing
the camera's reach is not part of adding one.

**Everything is semantic until build.** The project stores the map identity, the
layer slot, the authored dimensions and the initialization chunk; physical
placement is resolved by the allocator during the build. Nothing here is a file
offset, an address or a byte.

**Fail closed.** Only the ordinary dominant form is supported. A slot whose
layer is a special handler, a zero-dimension record, or a form this ticket has
not established is refused with its own reason, and a map whose *root* is shared
with another map is refused outright - the root holds the slot pointers and the
extent, so editing one would silently change every map that shares it.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import TYPE_CHECKING, Iterable, Mapping

from .allocation import (
    Addressability,
    Allocation,
    AllocationKind,
    AllocationRequest,
    allocate,
)
from .binary import FileOffset
from .formats import map_graphics as mg
from .layout import AnchorId, OwnedRegion, RomRange
from .packaged import packaged_profile
from .write import (
    ByteChange,
    GeneratedAllocationProvenance,
    GeneratedImage,
    StructureEditProvenance,
    StructureExtentProvenance,
    StructureFillProvenance,
)

if TYPE_CHECKING:
    from .map_chunk import ChunkPlacement
    from .profile import RomProfile
    from .project.model import (
        AuthoredLayer,
        LayerResize,
        LayoutEdits,
        MapStructure,
    )


class MapStructureError(ValueError):
    """A structural map edit could not be authored, resolved or materialized.

    One public failure type for the whole surface, for the reason the paint and
    chunk surfaces give: the readers underneath raise several unrelated
    ``ValueError`` subclasses and a caller either authors the structure or is
    refused. The message names the specific reason.
    """


#: The `maps/structure.toml` table names, restated so a caller that persists does
#: not have to import the project package to spell them.
RESIZE_TABLE = "resize"
LAYER_TABLE = "layer"
#: The allocation domain name this surface records in provenance.
DOMAIN = "map_structure"

#: A resource identity prefix for the allocator's anchor. The owner string is the
#: durable project identity (`map:NNNN/BGn` or `layer:name`), so a manifest
#: answers which authored edit owns a span without a second lookup.
STRUCTURE_PREFIX = "structure:"

#: Layer records are four-byte aligned like every other dominant-layer structure
#: the engine reads; nothing measured requires 16.
LAYER_ALIGNMENT = 4

#: A project-authored layer's identity: lowercase, stable, address-free.
_LAYER_NAME = re.compile(r"[a-z][a-z0-9_-]{0,63}$")

_READ_ERRORS = (mg.MapGraphicsError,)

#: The classification of a root slot the engine has not been given a layer for.
_ABSENT = "absent_placeholder"


# --- the resolved structural view --------------------------------------------


@dataclass(frozen=True, slots=True)
class ChunkChoice:
    """One chunk a structural layer may be initialized or painted with.

    ``ordinal`` is the 1-based position in the layer's own first-appearance
    vocabulary - the same "Chunk N" a person reads in the map editor, and the same
    number `maps/layout.toml` stores. The address is published for renderers and
    is never persisted.
    """

    ordinal: int
    address: int
    cell_count: int

    @property
    def label(self) -> str:
        return f"Chunk {self.ordinal}"


@dataclass(frozen=True, slots=True)
class StructuralLayer:
    """One layer slot as the project's structure makes it.

    ``retail_columns``/``retail_rows`` are what the canonical record states;
    ``columns``/``rows`` are what the project authored. They differ for a resized
    layer and for an authored layer the retail image has no record for at all
    (``retail_columns == 0``).
    """

    slot: int
    #: The canonical record address, or 0 for a slot the canonical image leaves
    #: unused and the project activates.
    address: int
    handler: int
    classification: str
    retail_columns: int
    retail_rows: int
    columns: int
    rows: int
    #: The effective chunk window, row-major, in the authored grid. A cell whose
    #: chunk is a project-authored one that has no address before the build holds
    #: 0; ``authored_fill``/``authored_cells`` say so rather than pretending.
    cells: tuple[int, ...]
    vocabulary: tuple[ChunkChoice, ...]
    #: Set when the layer is a project-authored record, at its created grid or at
    #: the grid a resize on the same slot grew it to.
    identity: str | None = None
    #: Set when the layer's grid is a project-authored resize - of a retail layer,
    #: or of the project-authored layer ``identity`` names.
    resized: bool = False
    #: The initialization value's own spelling, as the project stores it: the
    #: authored layer's when ``identity`` is set, otherwise the resize's.
    fill: int | str | None = None
    #: Set when the initialization names a project-authored chunk.
    authored_fill: str | None = None
    #: Row-major: the identity of a project-authored chunk each cell holds, or
    #: None when the cell holds a canonical chunk. For a created layer that was
    #: grown this is the authored initialization inside the authored grid and the
    #: resize's initialization in the cells the growth adds.
    authored_cells: tuple[str | None, ...] = ()
    #: Why this slot cannot be authored, empty when it can.
    read_only_reason: str = ""

    @property
    def structural(self) -> bool:
        return self.identity is not None or self.resized

    @property
    def absent(self) -> bool:
        """Whether the canonical image leaves this slot unused."""
        return self.classification == _ABSENT

    @property
    def editable(self) -> bool:
        return not self.read_only_reason

    @property
    def cell_count(self) -> int:
        return self.columns * self.rows

    @property
    def retail_cell_count(self) -> int:
        return self.retail_columns * self.retail_rows

    @property
    def width(self) -> int:
        return self.columns * mg.CHUNK_PIXELS

    @property
    def height(self) -> int:
        return self.rows * mg.CHUNK_PIXELS

    @property
    def label(self) -> str:
        return f"BG{self.slot} · chunk grid {self.columns}×{self.rows}"

    def contains(self, cell: int) -> bool:
        return type(cell) is int and 0 <= cell < self.cell_count

    def column_of(self, cell: int) -> int:
        return cell % self.columns

    def row_of(self, cell: int) -> int:
        return cell // self.columns

    def chunk(self, ordinal: int) -> ChunkChoice | None:
        for choice in self.vocabulary:
            if choice.ordinal == ordinal:
                return choice
        return None

    def ordinal_of(self, address: int) -> int | None:
        for choice in self.vocabulary:
            if choice.address == address:
                return choice.ordinal
        return None

    def pointer(self, ordinal: int) -> int:
        choice = self.chunk(ordinal)
        if choice is None:
            raise MapStructureError(
                f"{self.label} has no chunk {ordinal}; the layer uses "
                f"{len(self.vocabulary)} distinct chunks"
            )
        return choice.address


@dataclass(frozen=True, slots=True)
class StructureTarget:
    """One map as a structural editing surface sees it."""

    map_index: int
    name: str | None
    root_address: int
    #: The root's declared extent, in pixels, as the engine's own arithmetic
    #: reads it (the stored word is ``extent - 1``).
    extent_x: int
    extent_y: int
    slots: tuple[StructuralLayer, ...]
    #: A root shared with another map cannot be edited: its slot pointers and its
    #: extent are shared state, so a resize would silently change every map that
    #: loads the same definition.
    shared_with: tuple[int, ...] = ()

    def layer(self, slot: int) -> StructuralLayer:
        for item in self.slots:
            if item.slot == slot:
                return item
        raise MapStructureError(f"map:{self.map_index:04d} has no layer slot {slot}")

    @property
    def editable_layers(self) -> tuple[StructuralLayer, ...]:
        return tuple(item for item in self.slots if item.editable)

    @property
    def editable(self) -> bool:
        return not self.shared_with and bool(self.editable_layers)

    @property
    def read_only_reason(self) -> str:
        if self.shared_with:
            others = ", ".join(f"map:{index:04d}" for index in self.shared_with)
            return (
                f"this map's definition is shared with {others}; its layer slots "
                "and its extent are shared state"
            )
        if not self.editable_layers:
            return "no layer slot on this map is a supported dominant chunk grid"
        return ""

    @property
    def free_slots(self) -> tuple[int, ...]:
        """Slots the canonical image leaves unused, ready to be activated."""
        return tuple(item.slot for item in self.slots if item.absent and not self.shared_with)


# --- building the view -------------------------------------------------------


class _StructuralView:
    """One reader plus the structural lookups a session repeats.

    The canonical image is immutable and the project document is immutable, so
    every derived answer - a layer's retail record, its vocabulary, the effective
    grid, the resolved root sharing - is a pure function of the two and is
    memoized here rather than re-derived at each call site.
    """

    __slots__ = (
        "image",
        "profile",
        "structure",
        "_reader",
        "_entries",
        "_layers",
        "_roots",
        "_vocab",
        "_effective",
    )

    def __init__(
        self,
        canonical: bytes,
        structure: "MapStructure | None" = None,
        profile: "RomProfile | None" = None,
    ) -> None:
        self.image = bytes(canonical)
        self.profile = profile if profile is not None else packaged_profile()
        self.structure = structure if structure is not None else _empty_structure()
        self._reader = mg.MapGraphicsReader(self.image, self.profile)
        self._entries = mg.read_map_entries(self._reader)
        self._layers: dict[tuple[int, int], mg.LayerRecord] = {}
        self._roots: dict[int, tuple[int, ...]] = {}
        self._vocab: dict[tuple[int, int], tuple[ChunkChoice, ...]] = {}
        self._effective: dict[tuple[int, int], StructuralLayer] = {}

    @property
    def reader(self) -> mg.MapGraphicsReader:
        return self._reader

    @property
    def map_entry_count(self) -> int:
        return self._reader.map_entry_count()

    def entry(self, map_index: int):
        if type(map_index) is not int or not 0 <= map_index < self.map_entry_count:
            raise MapStructureError(
                f"map index {map_index!r} is outside 0..{self.map_entry_count - 1}"
            )
        return self._entries[map_index]

    def canonical_layer(self, map_index: int, layer_slot: int) -> mg.LayerRecord:
        key = (map_index, layer_slot)
        cached = self._layers.get(key)
        if cached is not None:
            return cached
        entry = self.entry(map_index)
        if type(layer_slot) is not int or not 0 <= layer_slot < len(mg.ROOT_LAYER_SLOTS):
            raise MapStructureError(
                f"map:{map_index:04d} has no layer slot {layer_slot!r}; the engine's "
                f"regular-BG count is {len(mg.ROOT_LAYER_SLOTS)}"
            )
        try:
            record = mg.read_layer(self._reader, entry.root_address, layer_slot)
        except _READ_ERRORS as exc:
            raise MapStructureError(str(exc)) from exc
        self._layers[key] = record
        return record

    def shared_maps(self, map_index: int) -> tuple[int, ...]:
        """The other maps that load this map's own definition."""
        entry = self.entry(map_index)
        others = self._roots.get(entry.root_address)
        if others is None:
            others = tuple(
                item.index
                for item in self._entries
                if item.root_address == entry.root_address
            )
            self._roots[entry.root_address] = others
        return tuple(index for index in others if index != map_index)

    def extent(self, map_index: int) -> tuple[int, int]:
        entry = self.entry(map_index)
        return (
            self._reader.u16(entry.root_address + mg.ROOT_EXTENT_X_OFFSET) + 1,
            self._reader.u16(entry.root_address + mg.ROOT_EXTENT_Y_OFFSET) + 1,
        )

    def _dominant(self, record: mg.LayerRecord, map_index: int, layer_slot: int):
        if record.classification != "dominant":
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot} is "
                f"{record.classification}, not a supported dominant chunk grid"
            )
        return record

    def template_layer(
        self, map_index: int, layer_slot: int, template: str
    ) -> mg.LayerRecord:
        """The canonical layer a new record's header is copied from.

        Resolved against the **canonical image only**, so editing the authored
        layer can never re-point the template that named it - the same rule
        authored chunks already follow.
        """
        match = _MAP_LAYER.match(template)
        if match is None:
            raise MapStructureError(
                f"template {template!r} is not 'map:NNNN/BGn'"
            )
        template_map = int(match.group(1), 10)
        template_slot = int(match.group(2), 10)
        if template_map != map_index:
            raise MapStructureError(
                f"template {template!r} names another map; an authored layer's "
                "screen-entry ordinals resolve through its own map's assembled "
                "character block"
            )
        return self._dominant(
            self.canonical_layer(template_map, template_slot), template_map, template_slot
        )

    def vocabulary(
        self, map_index: int, layer_slot: int, template: str | None = None
    ) -> tuple[ChunkChoice, ...]:
        """The distinct chunks a structural layer may be composed from.

        For a resized layer that is the layer's own vocabulary; for an authored
        layer it is the **template** layer's, because the new record's screen-entry
        ordinals resolve through the same map's character block and the permitted
        vocabulary is exactly the entries a layer on this map already draws.
        """
        key = (map_index, layer_slot)
        cached = self._vocab.get(key)
        if cached is not None:
            return cached
        record = (
            self.template_layer(map_index, layer_slot, template)
            if template is not None
            else self._dominant(self.canonical_layer(map_index, layer_slot), map_index, layer_slot)
        )
        counts: dict[int, int] = {}
        for address in record.chunk_addresses:
            if address:
                counts[address] = counts.get(address, 0) + 1
        choices = tuple(
            ChunkChoice(ordinal=ordinal, address=address, cell_count=count)
            for ordinal, (address, count) in enumerate(counts.items(), start=1)
        )
        self._vocab[key] = choices
        return choices

    def structural_layer(self, map_index: int, layer_slot: int) -> StructuralLayer:
        key = (map_index, layer_slot)
        cached = self._effective.get(key)
        if cached is not None:
            return cached
        built = self._build_layer(map_index, layer_slot)
        self._effective[key] = built
        return built

    def _build_layer(self, map_index: int, layer_slot: int) -> StructuralLayer:
        record = self.canonical_layer(map_index, layer_slot)
        resize = self.structure.resize_for(map_index, layer_slot)
        authored = self.structure.layer_at(map_index, layer_slot)

        if authored is not None:
            # A created layer that was then grown is still the authored layer: the
            # template, the identity and the vocabulary are its own, and the resize
            # only states the grid it reaches.
            return self._authored_layer(authored, record, resize)
        if resize is not None:
            return self._resized_layer(resize, record)
        return self._retail_layer(record)

    def _retail_layer(self, record: mg.LayerRecord) -> StructuralLayer:
        if record.classification != "dominant":
            return StructuralLayer(
                slot=record.slot,
                address=record.address,
                handler=record.handler,
                classification=record.classification,
                retail_columns=record.chunk_x,
                retail_rows=record.chunk_y,
                columns=record.chunk_x,
                rows=record.chunk_y,
                cells=record.chunk_addresses,
                vocabulary=(),
                read_only_reason=_read_only_reason(record),
            )
        return StructuralLayer(
            slot=record.slot,
            address=record.address,
            handler=record.handler,
            classification=record.classification,
            retail_columns=record.chunk_x,
            retail_rows=record.chunk_y,
            columns=record.chunk_x,
            rows=record.chunk_y,
            cells=record.chunk_addresses,
            vocabulary=self._vocabulary_of(
                record.chunk_addresses
            ),
        )

    def _vocabulary_of(self, cells: Iterable[int]) -> tuple[ChunkChoice, ...]:
        counts: dict[int, int] = {}
        for address in cells:
            if address:
                counts[address] = counts.get(address, 0) + 1
        return tuple(
            ChunkChoice(ordinal=ordinal, address=address, cell_count=count)
            for ordinal, (address, count) in enumerate(counts.items(), start=1)
        )

    def _resized_layer(self, resize, record: mg.LayerRecord) -> StructuralLayer:
        self._dominant(record, resize.map_index, resize.layer_slot)
        vocabulary = self._vocabulary_of(record.chunk_addresses)
        fill_address, fill_identity = self._resolve_fill(resize.fill, vocabulary)
        cells: list[int] = []
        authored_cells: list[str | None] = []
        for row in range(resize.rows):
            for column in range(resize.columns):
                retail = _retail_cell(record, column, row)
                if retail is not None:
                    cells.append(retail)
                    authored_cells.append(None)
                else:
                    cells.append(fill_address)
                    authored_cells.append(fill_identity)
        return StructuralLayer(
            slot=resize.layer_slot,
            address=record.address,
            handler=record.handler,
            classification=record.classification,
            retail_columns=record.chunk_x,
            retail_rows=record.chunk_y,
            columns=resize.columns,
            rows=resize.rows,
            cells=tuple(cells),
            vocabulary=vocabulary,
            resized=True,
            fill=resize.fill,
            authored_fill=fill_identity,
            authored_cells=tuple(authored_cells),
        )

    def _authored_layer(
        self, authored, record: mg.LayerRecord, resize=None
    ) -> StructuralLayer:
        """A project-authored layer, at its created grid or at the grid it grew to.

        ``resize`` is the same slot's `[resize]` entry when there is one. The pair
        is resolved here rather than by a second code path because it IS one layer:
        the template, the header, the identity and the vocabulary are the authored
        layer's, and the resize only says which grid the record is emitted in. The
        authored grid's own cells keep their coordinates and only the cells the
        growth adds take the resize's initialization.
        """
        template = self.template_layer(
            authored.map_index, authored.layer_slot, authored.template
        )
        vocabulary = self._vocabulary_of(template.chunk_addresses)
        fill_address, fill_identity = self._resolve_fill(authored.fill, vocabulary)

        if resize is None:
            columns, rows = authored.columns, authored.rows
            cells = tuple(fill_address for _ in range(columns * rows))
            authored_cells: tuple[str | None, ...] = tuple(
                fill_identity for _ in range(columns * rows)
            )
        else:
            _require_growth(authored, resize)
            grown_address, grown_identity = self._resolve_fill(
                resize.fill, vocabulary
            )
            columns, rows = resize.columns, resize.rows
            cell_values: list[int] = []
            cell_identities: list[str | None] = []
            for row in range(rows):
                for column in range(columns):
                    if column < authored.columns and row < authored.rows:
                        cell_values.append(fill_address)
                        cell_identities.append(fill_identity)
                    else:
                        cell_values.append(grown_address)
                        cell_identities.append(grown_identity)
            cells = tuple(cell_values)
            authored_cells = tuple(cell_identities)

        return StructuralLayer(
            slot=authored.layer_slot,
            address=template.address,
            handler=template.handler,
            classification="dominant",
            retail_columns=record.chunk_x,
            retail_rows=record.chunk_y,
            columns=columns,
            rows=rows,
            cells=cells,
            vocabulary=vocabulary,
            identity=authored.identity,
            resized=resize is not None,
            fill=authored.fill,
            authored_fill=fill_identity,
            authored_cells=authored_cells,
        )

    def _resolve_fill(
        self, fill: int | str, vocabulary: tuple[ChunkChoice, ...]
    ) -> tuple[int, str | None]:
        """A fill value to ``(canonical address, authored identity)``.

        An ordinal resolves to an address in the canonical image; an authored
        chunk identity has no address before the build, so it resolves to 0 and
        its identity, and the build's chunk domain supplies the address.
        """
        if isinstance(fill, str):
            return 0, fill
        choice = next((item for item in vocabulary if item.ordinal == fill), None)
        if choice is None:
            raise MapStructureError(
                f"chunk {fill} is not one of the {len(vocabulary)} chunks this layer "
                "uses; the initialization must name a chunk the layer already draws "
                "or a project-authored chunk"
            )
        return choice.address, None


def _retail_cell(record: mg.LayerRecord, column: int, row: int) -> int | None:
    """The canonical chunk at the authored coordinate, or None outside the grid.

    The one statement of the resize transform: **top-left anchored**, so an old
    cell ``(x, y)`` lands at new cell ``(x, y)`` and a cell the growth adds has no
    canonical source. A sequential copy of the window is only the same thing when
    the column count does not change, and a wrong stride or a wrong anchor is
    exactly what this replaces - the boundary and corner tests pin it.
    """
    if not 0 <= column < record.chunk_x or not 0 <= row < record.chunk_y:
        return None
    address = record.chunk_addresses[row * record.chunk_x + column]
    return address or None


def _require_growth(authored, resize) -> None:
    """A resize of a project-authored layer must actually grow it.

    The `[layer]` entry declares the grid the layer was CREATED at and the
    `[resize]` entry the grid it is GROWN to, so a resize that is smaller on
    either axis - or that changes nothing - would silently drop the cells the
    authored grid holds, the same loss the retail shrink refusal exists to
    prevent. The authored grid is therefore the shrink floor.
    """
    if (
        resize.columns < authored.columns
        or resize.rows < authored.rows
        or (resize.columns, resize.rows) == (authored.columns, authored.rows)
    ):
        raise MapStructureError(
            f"{authored.owner}: the project-authored layer is "
            f"{authored.columns}x{authored.rows} and the resize states "
            f"{resize.columns}x{resize.rows}; a resize on an authored layer states "
            "the grid it is grown to, so it must be larger on at least one axis "
            "and smaller on neither"
        )


def _read_only_reason(record: mg.LayerRecord) -> str:
    if record.handler == mg.TERRAIN_FIELD_LAYER_HANDLER:
        return (
            "this slot is the terrain-field form Map 19 uses; its grid is a run of "
            "8-bit ordinal containers, not a chunk window"
        )
    if record.handler in mg.SCREENBLOCK_HANDLERS:
        return (
            "this slot is a single screen-entry plane reached by its own handler; it "
            "has no chunk grid to resize"
        )
    if record.classification == "absent_placeholder":
        return (
            "the canonical image leaves this slot unused; author a layer to activate it"
        )
    if record.classification in ("dominant_zero_grid", "dominant_partial_zero_grid"):
        return (
            f"this dominant record's own grid is {record.chunk_x}x{record.chunk_y}, "
            "which states no chunk window"
        )
    return f"this slot's layer form is {record.classification}"


def _empty_structure() -> "MapStructure":
    from .project.model import MapStructure

    return MapStructure()


_MAP_LAYER = re.compile(r"^map:(\d{4})/BG([0-3])$")


def layer_identity(name: object) -> str:
    """``name`` as a project-authored layer's durable identity."""
    if not isinstance(name, str):
        raise MapStructureError("a layer identity must be a string")
    text = name if name.startswith("layer:") else f"layer:{name}"
    if _LAYER_NAME.match(text[len("layer:"):]) is None:
        raise MapStructureError(
            f"{name!r} is not a usable layer name; expected a lowercase letter "
            "followed by up to 63 of a-z, 0-9, '_' or '-'"
        )
    return text


# --- authoring ---------------------------------------------------------------


class MapResizer:
    """The public facade a Workbench surface drives.

    It answers what a map's structural editing surface may offer, validates an
    authored resize or authored layer against the canonical image, and resolves
    either into the record the build will emit. It never writes a file, never
    allocates and never touches an image.
    """

    __slots__ = ("_view",)

    def __init__(
        self,
        canonical_bytes: bytes,
        *,
        structure: "MapStructure | None" = None,
        profile: "RomProfile | None" = None,
    ) -> None:
        self._view = _StructuralView(canonical_bytes, structure, profile)

    @property
    def image(self) -> bytes:
        return self._view.image

    @property
    def profile(self):
        return self._view.profile

    @property
    def structure(self) -> "MapStructure":
        return self._view.structure

    @property
    def map_entry_count(self) -> int:
        return self._view.map_entry_count

    def layer_label(self, map_index: int, layer_slot: int) -> str:
        return self._view.structural_layer(map_index, layer_slot).label

    def vocabulary(self, map_index: int, layer_slot: int) -> tuple[ChunkChoice, ...]:
        return self._view.structural_layer(map_index, layer_slot).vocabulary

    def target(self, map_index: int) -> StructureTarget:
        entry = self._view.entry(map_index)
        name = self._view.reader.text(entry.text_index) if entry.text_index else None
        extent_x, extent_y = self._view.extent(map_index)
        return StructureTarget(
            map_index=map_index,
            name=name,
            root_address=entry.root_address,
            extent_x=extent_x,
            extent_y=extent_y,
            slots=tuple(
                self._view.structural_layer(map_index, slot)
                for slot in range(len(mg.ROOT_LAYER_SLOTS))
            ),
            shared_with=self._view.shared_maps(map_index),
        )

    def chunk_label(self, ordinal: int) -> str:
        return ChunkChoice(ordinal, 0, 0).label

    def resize(
        self,
        map_index: int,
        layer_slot: int,
        columns: int,
        rows: int,
        fill: int | str,
    ) -> "LayerResize":
        """Validate a resize and return the value the project persists.

        Growth only, and the reason is stated rather than implied: a shrink would
        orphan authored content whose references this ticket has not established -
        placements, triggers and the map's own connections are stated in map
        coordinates that a smaller extent need not contain - so it is refused
        instead of silently dropping cells.

        A slot that already holds a project-authored layer is accepted: the layer
        was created at its own declared grid, so **that** grid is the shrink floor
        rather than the canonical slot's zero-dimension placeholder, and the pair
        is what "grow a layer the project itself created" means.
        """
        from .project.model import LayerResize

        target = self.target(map_index)
        if target.shared_with:
            raise MapStructureError(
                f"map:{map_index:04d}: {target.read_only_reason}"
            )
        layer = target.layer(layer_slot)
        if layer.read_only_reason:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot}: {layer.read_only_reason}"
            )
        # The shrink floor is the layer's CURRENT grid: the authored layer's own
        # declared grid when it carries no resize yet, and the grid it has already
        # been grown to when it does. Either way an authored cell is never removed.
        retail_columns, retail_rows = layer.columns, layer.rows
        columns = _grid_side(columns, "columns")
        rows = _grid_side(rows, "rows")
        if columns < retail_columns or rows < retail_rows:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot} is {retail_columns}x{retail_rows}; "
                f"shrinking to {columns}x{rows} is not supported because the cells it "
                "would remove have not been shown to be unreferenced"
            )
        if columns == retail_columns and rows == retail_rows:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot} is already "
                f"{columns}x{rows}; a resize must change the grid"
            )
        self._resolve_fill_for(layer, fill)
        return LayerResize(
            map_index=map_index,
            layer_slot=layer_slot,
            columns=columns,
            rows=rows,
            fill=fill,
        )

    def authored_layer(
        self,
        identity: object,
        map_index: int,
        layer_slot: int,
        template: str,
        columns: int,
        rows: int,
        fill: int | str,
    ) -> "AuthoredLayer":
        """Validate a new supported layer and return the value to persist."""
        from .project.model import AuthoredLayer

        identity = layer_identity(identity)
        target = self.target(map_index)
        if target.shared_with:
            raise MapStructureError(
                f"map:{map_index:04d}: {target.read_only_reason}"
            )
        layer = target.layer(layer_slot)
        if not layer.absent:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot} is {layer.classification}; an "
                "authored layer can only activate a slot the canonical image leaves "
                "unused, because the engine's layer count is fixed at "
                f"{len(mg.ROOT_LAYER_SLOTS)}"
            )
        # Name the two template mistakes before resolving anything: a template that
        # names this slot would copy the record it is replacing, and a malformed
        # template is a project-file problem rather than a layer-form one.
        match = _MAP_LAYER.match(template) if isinstance(template, str) else None
        if match is None:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot}: template {template!r} is not "
                "'map:NNNN/BGn'"
            )
        if int(match.group(1), 10) != map_index:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot}: template {template!r} names "
                "another map; an authored layer's screen-entry ordinals resolve "
                "through its own map's assembled character block"
            )
        if int(match.group(2), 10) == layer_slot:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot}: template {template!r} is the "
                "slot it would activate"
            )
        template_record = self._view.template_layer(map_index, layer_slot, template)
        if self._view.structure.layer_at(map_index, layer_slot) is not None:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot} is already a project-authored layer"
            )
        columns = _grid_side(columns, "columns")
        rows = _grid_side(rows, "rows")
        # A slot may already carry a resize. That is the pair, not a second claim -
        # but only when this layer really is the grid that resize grows FROM, so a
        # case that would silently drop this layer's own cells is refused here
        # rather than at the build.
        existing = self._view.structure.resize_for(map_index, layer_slot)
        if existing is not None and (
            existing.columns < columns
            or existing.rows < rows
            or (existing.columns, existing.rows) == (columns, rows)
        ):
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot} already carries the resize to "
                f"{existing.columns}x{existing.rows}; an authored layer on that slot "
                "is the grid the resize grows from, so its own grid must be smaller "
                "on at least one axis and larger on neither"
            )
        vocabulary = self._vocabulary_of(template_record.chunk_addresses)
        self._resolve_fill_value(fill, vocabulary, f"map:{map_index:04d} BG{layer_slot}")
        return AuthoredLayer(
            identity=identity,
            map_index=map_index,
            layer_slot=layer_slot,
            template=template,
            columns=columns,
            rows=rows,
            fill=fill,
        )

    def describe(self, edit) -> str:
        """One readable line for a persisted structural edit."""
        if hasattr(edit, "identity"):
            return (
                f"{edit.identity}: new BG{edit.layer_slot} on map:{edit.map_index:04d} "
                f"· {edit.columns}×{edit.rows} from {edit.template}"
            )
        return (
            f"map:{edit.map_index:04d} BG{edit.layer_slot} resize → "
            f"{edit.columns}×{edit.rows}"
        )

    def _resolve_fill_for(self, layer: StructuralLayer, fill: int | str) -> None:
        self._resolve_fill_value(fill, layer.vocabulary, layer.label)

    def _resolve_fill_value(self, fill, vocabulary, label: str) -> None:
        if isinstance(fill, str):
            if not fill.startswith("chunk:"):
                raise MapStructureError(
                    f"{label}: initialization {fill!r} is neither a chunk ordinal nor "
                    "a 'chunk:<name>' authored chunk"
                )
            return
        if type(fill) is not int or fill < 1:
            raise MapStructureError(
                f"{label}: initialization must be a 1-based chunk ordinal or an "
                f"authored chunk identity, got {fill!r}"
            )
        if all(choice.ordinal != fill for choice in vocabulary):
            raise MapStructureError(
                f"{label}: chunk {fill} is not one of the {len(vocabulary)} chunks "
                "this layer uses"
            )

    def _vocabulary_of(self, cells: Iterable[int]) -> tuple[ChunkChoice, ...]:
        return self._view._vocabulary_of(cells)


def _grid_side(value: object, axis: str) -> int:
    if type(value) is not int:
        raise MapStructureError(f"a grid {axis} count must be a whole number")
    if not 1 <= value <= mg.MAX_LAYER_GRID_SIDE:
        raise MapStructureError(
            f"{axis} = {value} chunks is outside the supported 1.."
            f"{mg.MAX_LAYER_GRID_SIDE}"
        )
    return value


# --- persistence -------------------------------------------------------------


def read_map_structure(project_dir) -> "MapStructure":
    """One load of the project's structural document."""
    from .project.model import read_project

    return read_project(project_dir).structure


def _project_structure(project_dir) -> "MapStructure":
    from .project.model import MapStructure, read_project

    return read_project(project_dir).structure


def set_layer_resize(
    project_dir,
    canonical_bytes: bytes,
    resize: "LayerResize",
    *,
    profile: "RomProfile | None" = None,
) -> bool:
    """Persist one resize into `maps/structure.toml`. Returns whether it changed."""
    from .project.model import MapStructure
    from .project.model import write_map_structure as _write

    resizer = MapResizer(
        canonical_bytes, structure=_project_structure(project_dir), profile=profile
    )
    accepted = resizer.resize(
        resize.map_index,
        resize.layer_slot,
        resize.columns,
        resize.rows,
        resize.fill,
    )
    document = dict(resizer.structure.resizes)
    document[accepted.key] = accepted
    updated = MapStructure(
        resizes=dict(sorted(document.items())), layers=dict(resizer.structure.layers)
    )
    if updated == resizer.structure:
        return False
    _write(project_dir, updated)
    return True


def clear_layer_resize(
    project_dir,
    canonical_bytes: bytes,
    map_index: int,
    layer_slot: int,
    *,
    profile: "RomProfile | None" = None,
) -> bool:
    """Remove one resize. Returns whether it was declared."""
    from .project.model import LayerResize, MapStructure
    from .project.model import write_map_structure as _write

    del canonical_bytes, profile
    structure = _project_structure(project_dir)
    key = LayerResize.key_for(map_index, layer_slot)
    if key not in structure.resizes:
        return False
    document = dict(structure.resizes)
    del document[key]
    _write(
        project_dir,
        MapStructure(resizes=dict(sorted(document.items())), layers=dict(structure.layers)),
    )
    return True


def set_authored_layer(
    project_dir,
    canonical_bytes: bytes,
    layer: "AuthoredLayer",
    *,
    profile: "RomProfile | None" = None,
) -> bool:
    """Persist one authored layer into `maps/structure.toml`."""
    from .project.model import MapStructure
    from .project.model import write_map_structure as _write

    resizer = MapResizer(
        canonical_bytes, structure=_project_structure(project_dir), profile=profile
    )
    accepted = resizer.authored_layer(
        layer.identity,
        layer.map_index,
        layer.layer_slot,
        layer.template,
        layer.columns,
        layer.rows,
        layer.fill,
    )
    # Copy independence: the template is resolved against the canonical image and
    # only this record is created, so the source layer's record, grid and metadata
    # are untouched by construction. A resize already on this slot is the pair -
    # the created layer and the grid it is grown to - and `authored_layer` has
    # already refused it unless this layer really is the grid that resize grows
    # from, so nothing here has to choose between the two.
    document = dict(resizer.structure.layers)
    document[accepted.identity] = accepted
    updated = MapStructure(
        resizes=dict(resizer.structure.resizes), layers=dict(sorted(document.items()))
    )
    if updated == resizer.structure:
        return False
    _write(project_dir, updated)
    return True


def remove_authored_layer(project_dir, identity: str) -> bool:
    """Remove one authored layer, refusing while its cells are still authored.

    A layer that still carries authored cell content is not removed silently: the
    cells would become edits on a slot the project no longer declares, which is
    exactly the "authored but not applied" failure the project format refuses.
    """
    from .project.model import MapStructure
    from .project.model import write_map_structure as _write
    from .project.model import read_project as _read

    project = _read(project_dir)
    structure = project.structure
    if identity not in structure.layers:
        return False
    layer = structure.layers[identity]
    holders = sorted(
        cell
        for (map_index, slot, cell) in project.layout.cells()
        if (map_index, slot) == (layer.map_index, layer.layer_slot)
    )
    if holders:
        shown = ", ".join(str(cell) for cell in holders[:5])
        more = "" if len(holders) <= 5 else f" and {len(holders) - 5} more"
        raise MapStructureError(
            f"{identity} still holds authored cell content at {shown}{more}; clear "
            "those cells before removing the layer"
        )
    document = dict(structure.layers)
    del document[identity]
    _write(
        project_dir,
        MapStructure(resizes=dict(structure.resizes), layers=dict(sorted(document.items()))),
    )
    return True


# --- resolution and materialization ------------------------------------------


@dataclass(frozen=True, slots=True)
class ResolvedLayerRecord:
    """One structural edit resolved to the exact record a build will emit.

    ``authored_layer`` is set when the slot carries a project-authored layer -
    either because the edit IS one, or because it is a resize OF one. That is what
    tells a retail-layer resize from an authored-layer resize, and
    ``authored_columns``/``authored_rows`` are the grid the layer was created at,
    which is the grid a resize of it grows from.
    """

    owner: str
    kind: str
    map_index: int
    layer_slot: int
    columns: int
    rows: int
    retail_columns: int
    retail_rows: int
    template_address: int
    record: bytes
    #: Entry ``(cell, chunk address, canonical ordinal, authored identity)`` for
    #: every window cell, in row-major order. ``ordinal`` is set when the cell's
    #: chunk is a canonical one named by the layer's own vocabulary; ``identity``
    #: is set, and ``address`` is the address the chunk domain placed that body at,
    #: when the cell names a project-authored chunk.
    window: tuple[tuple[int, int, int | None, str | None], ...]
    extent_changes: tuple[tuple[str, int, int], ...]
    #: The ``layer:name`` identity of the project-authored layer this record is,
    #: or "" when the record is a retail layer's own resize.
    authored_layer: str = ""
    #: The grid the authored layer was created at - the grid a resize of it grows
    #: FROM - or 0/0 when the record is not a project-authored layer's.
    authored_columns: int = 0
    authored_rows: int = 0

    @property
    def record_sha256(self) -> str:
        return hashlib.sha256(self.record).hexdigest()

    @property
    def expanded_columns(self) -> int:
        return self.retail_columns * self.retail_rows


@dataclass(frozen=True, slots=True)
class StructureBuild:
    """One structural edit, placed by the allocator, with its reference sites."""

    resolved: ResolvedLayerRecord
    allocation: Allocation
    #: File offset of the map root's own four-byte layer-slot field.
    slot_offset: int
    previous_record_address: int
    placement: tuple[int, int] | None
    #: ``(window cell file offset, chunk identity)`` for every cell that holds a
    #: project-authored chunk.
    authored_cells: tuple[tuple[int, str], ...]

    @property
    def owner(self) -> str:
        return self.resolved.owner

    @property
    def record_address(self) -> int:
        return self.allocation.rom_address

    @property
    def expanded(self) -> bool:
        return self.allocation.is_expanded


@dataclass(frozen=True, slots=True)
class StructureMaterialization:
    """Everything this domain contributes to one build's single write plan."""

    builds: tuple[StructureBuild, ...]
    changes: tuple[ByteChange, ...]
    generated_allocations: tuple[GeneratedAllocationProvenance, ...]
    reserved: tuple[RomRange, ...]
    provenance: tuple[StructureEditProvenance, ...]
    generated_image: GeneratedImage | None = None


def resolve_layer_record(
    canonical: bytes,
    edit,
    *,
    view: _StructuralView | None = None,
    structure: "MapStructure | None" = None,
    layout: "LayoutEdits | None" = None,
    chunk_addresses: Mapping[str, int] | None = None,
    profile: "RomProfile | None" = None,
) -> ResolvedLayerRecord:
    """Resolve one persisted structural edit into the record bytes it implies.

    The record is the template's own ``0x18``-byte header copied verbatim - its
    ``+0x04``, ``+0x08``, ``+0x0C``, ``+0x10`` and ``+0x16`` fields have no
    established semantics, so they are carried rather than reconstructed - with
    the two grid bytes and the chunk window replaced.

    ``chunk_addresses`` supplies the addresses the build's chunk domain placed
    project-authored chunk bodies at. A cell that names an authored chunk but has
    no address is refused rather than written as a null pointer.

    A ``[resize]`` whose slot also carries a ``[layer]`` is resolved against the
    **authored** layer, which the document has to be in hand to see: the
    argument is a resize, the template is the authored layer's, and the base grid
    is the authored layer's own declared grid. Pass the document as ``structure``
    (or inside ``view``) for that case; a caller that supplies neither gets the
    retail reading, which for a slot the canonical image leaves unused is refused
    by the dominance check rather than silently resolved against a placeholder.
    """
    resolved_view = (
        view if view is not None else _StructuralView(canonical, structure, profile)
    )
    addresses = dict(chunk_addresses or {})
    resize = not hasattr(edit, "identity")
    authored_layer = ""
    authored_columns = 0
    authored_rows = 0

    if resize:
        authored = resolved_view.structure.layer_at(edit.map_index, edit.layer_slot)
        if authored is not None:
            # A created layer that was then grown. The base grid is the AUTHORED
            # layer's: the canonical slot holds the shared zero-dimension
            # placeholder, so there is no retail grid to map cells from, and the
            # record's header - the unknown fields this transform carries rather
            # than reconstructs - comes from the authored layer's template record.
            _require_growth(authored, edit)
            record = resolved_view.template_layer(
                edit.map_index, edit.layer_slot, authored.template
            )
            template_address = record.address
            columns, rows = edit.columns, edit.rows
            vocabulary = resolved_view._vocabulary_of(record.chunk_addresses)
            created_address, created_identity = resolved_view._resolve_fill(
                authored.fill, vocabulary
            )
            grown_address, grown_identity = resolved_view._resolve_fill(
                edit.fill, vocabulary
            )
            created_ordinal = (
                authored.fill if isinstance(authored.fill, int) else None
            )
            grown_ordinal = edit.fill if isinstance(edit.fill, int) else None
            base_cells: list[tuple[int | None, str | None, int | None]] = []
            for row in range(rows):
                for column in range(columns):
                    if column < authored.columns and row < authored.rows:
                        base_cells.append(
                            (created_address, created_identity, created_ordinal)
                        )
                    else:
                        base_cells.append(
                            (grown_address, grown_identity, grown_ordinal)
                        )
            slot_record = resolved_view.canonical_layer(
                edit.map_index, edit.layer_slot
            )
            retail_columns, retail_rows = slot_record.chunk_x, slot_record.chunk_y
            # ONE owner for the pair: the record IS the project-authored layer, so
            # every change of it - the record, the root slot pointer and the extent
            # words - is attributed to the layer the author named.
            owner = authored.identity
            kind = "resize"
            authored_layer = authored.identity
            authored_columns = authored.columns
            authored_rows = authored.rows
        else:
            record = resolved_view._dominant(
                resolved_view.canonical_layer(edit.map_index, edit.layer_slot),
                edit.map_index,
                edit.layer_slot,
            )
            template_address = record.address
            columns, rows = edit.columns, edit.rows
            fill = edit.fill
            fill_ordinal = fill if isinstance(fill, int) else None
            vocabulary = resolved_view._vocabulary_of(record.chunk_addresses)
            retail_columns, retail_rows = record.chunk_x, record.chunk_y
            base_cells = []
            for row in range(rows):
                for column in range(columns):
                    retail = _retail_cell(record, column, row)
                    if retail is not None:
                        base_cells.append((retail, None, None))
                    else:
                        address, identity = resolved_view._resolve_fill(
                            fill, vocabulary
                        )
                        base_cells.append((address, identity, fill_ordinal))
            owner = edit.key
            kind = "resize"
    else:
        record = resolved_view.template_layer(
            edit.map_index, edit.layer_slot, edit.template
        )
        template_address = record.address
        columns, rows = edit.columns, edit.rows
        vocabulary = resolved_view._vocabulary_of(record.chunk_addresses)
        fill_resolved = resolved_view._resolve_fill(edit.fill, vocabulary)
        fill_ordinal = edit.fill if isinstance(edit.fill, int) else None
        base_cells = [
            (fill_resolved[0], fill_resolved[1], fill_ordinal)
            for _ in range(columns * rows)
        ]
        retail_columns, retail_rows = 0, 0
        owner = edit.identity
        kind = "layer"

    # Authored cell content overrides the structural default. Each resolution
    # carries the canonical ordinal when there is one, so provenance can state
    # which chunk of the layer's own vocabulary a cell holds rather than making a
    # reader recover it from the address.
    overrides = (layout or _empty_layout()).for_map(edit.map_index).get(
        edit.layer_slot, {}
    )
    cell_resolutions: list[tuple[int, int, int | None, str | None]] = []
    window: list[int] = []
    for cell in range(columns * rows):
        address, identity, ordinal = base_cells[cell]
        value = overrides.get(cell)
        if value is not None:
            if isinstance(value, str):
                address, identity, ordinal = addresses.get(value, 0), value, None
            else:
                choice = next((c for c in vocabulary if c.ordinal == value), None)
                if choice is None:
                    raise MapStructureError(
                        f"{owner}: cell {cell} names chunk {value}, which is not one "
                        f"of the {len(vocabulary)} chunks this layer uses"
                    )
                address, identity, ordinal = choice.address, None, choice.ordinal
        elif identity is not None:
            # A cell initialized from (or overridden by) a project-authored chunk
            # has no address until the chunk domain has placed that body; resolving
            # it here is what lets the window state the address the emitted record
            # really names rather than the 0 the view carries before a build.
            address = addresses.get(identity, 0)
        if not address:
            raise MapStructureError(
                f"{owner}: cell {cell} names "
                + (f"authored chunk {identity}" if identity else "no chunk")
                + ", which this build did not place"
            )
        cell_resolutions.append((cell, address, ordinal, identity))
        window.append(address)

    header = mg.layer_record_header(resolved_view.reader, record)
    emitted = mg.compose_layer_record(header, columns, rows, window)

    extent_changes: list[tuple[str, int, int]] = []
    if resize:
        entry = resolved_view.entry(edit.map_index)
        for axis, offset, viewport, plane in (
            ("x", mg.ROOT_EXTENT_X_OFFSET, mg.VIEWPORT_PIXELS_X,
             columns * mg.CHUNK_PIXELS),
            ("y", mg.ROOT_EXTENT_Y_OFFSET, mg.VIEWPORT_PIXELS_Y,
             rows * mg.CHUNK_PIXELS),
        ):
            field = entry.root_address + offset
            previous = resolved_view.reader.u16(field)
            required = mg.declared_extent_raw(plane, viewport)
            if required > previous:
                extent_changes.append((axis, field, required))

    return ResolvedLayerRecord(
        owner=owner,
        kind=kind,
        map_index=edit.map_index,
        layer_slot=edit.layer_slot,
        columns=columns,
        rows=rows,
        retail_columns=retail_columns,
        retail_rows=retail_rows,
        template_address=template_address,
        record=emitted,
        window=tuple(cell_resolutions),
        extent_changes=tuple(extent_changes),
        authored_layer=authored_layer,
        authored_columns=authored_columns,
        authored_rows=authored_rows,
    )


def _empty_layout() -> "LayoutEdits":
    from .project.model import LayoutEdits

    return LayoutEdits()


def structural_placements(
    canonical: bytes,
    structure: "MapStructure",
    layout: "LayoutEdits",
    *,
    profile: "RomProfile | None" = None,
) -> tuple["ChunkPlacement", ...]:
    """The authoured-chunk references a structural edit carries.

    Two sources, both of which a build must materialize the chunk body for: the
    initialization value of a resize or authored layer when it names a
    project-authored chunk, and any authored cell content on a structural layer.
    They are returned as site-less :class:`map_chunk.ChunkPlacement` values because
    the field that will name them lives inside a record the build materializes.

    A slot is visited **once**, so a created layer that was then grown contributes
    its own initialization and its resize's initialization - one reference each,
    both of which the emitted record's window names - rather than the slot being
    counted once per document entry.
    """
    from .map_chunk import ChunkPlacement

    view = _StructuralView(canonical, structure, profile)
    placements: list[ChunkPlacement] = []
    for map_index, layer_slot in sorted(structure.structural_slots()):
        structural = view.structural_layer(map_index, layer_slot)
        # The resolved layer states, cell by cell, which project-authored chunk
        # body each cell needs. Taking the distinct identities in first-appearance
        # order covers the layer's initialization, the resize's initialization of
        # the cells the growth adds, and any authored cell content - all three are
        # in this one tuple, so none of them can be missed.
        for identity in dict.fromkeys(
            item for item in structural.authored_cells if item
        ):
            placements.append(
                ChunkPlacement(
                    map_index=map_index,
                    layer_slot=layer_slot,
                    cell=-1,
                    offset=-1,
                    previous=0,
                    identity=identity,
                    kind="structure",
                )
            )
        for cell, cells in layout.for_map(map_index).get(layer_slot, {}).items():
            if isinstance(cells, str):
                placements.append(
                    ChunkPlacement(
                        map_index=map_index,
                        layer_slot=layer_slot,
                        cell=cell,
                        offset=-1,
                        previous=0,
                        identity=cells,
                        kind="structure",
                    )
                )
    # A structural reference has no cell of its own: what distinguishes two of
    # them on one slot is the chunk each names, so two different initializations
    # are two references rather than one cell claimed twice.
    keys = [
        (
            p.map_index,
            p.layer_slot,
            p.cell,
            p.identity if p.is_structural else None,
        )
        for p in placements
    ]
    if len(set(keys)) != len(keys):
        raise MapStructureError("a structural layer names one cell twice")
    return tuple(placements)


def _effective_edits(structure: "MapStructure") -> tuple[tuple[str, object], ...]:
    """``(owner, edit)`` for every slot this document owns, sorted by owner.

    One entry per **slot**, not per document entry: a slot that carries a created
    layer and a resize of it is one edit, and the resize is what resolves it (the
    authored layer is found from the same document, so the pair comes out as one
    grown record). Ordering by the resolved owner - the ``layer:name`` for the
    pair - is what makes the allocator's placement deterministic.
    """
    by_slot: dict[tuple[int, int], tuple[str, object]] = {}
    for layer in structure.layers.values():
        slot = (layer.map_index, layer.layer_slot)
        resize = structure.resize_for(*slot)
        by_slot[slot] = (layer.identity, resize if resize is not None else layer)
    for resize in structure.resizes.values():
        slot = (resize.map_index, resize.layer_slot)
        if slot not in by_slot:
            by_slot[slot] = (resize.key, resize)
    return tuple(sorted(by_slot.values(), key=lambda item: item[0]))


def materialize_map_structure(
    canonical: bytes,
    structure: "MapStructure",
    layout: "LayoutEdits | None" = None,
    *,
    profile: "RomProfile | None" = None,
    reserved: Iterable[RomRange] = (),
    chunk_addresses: Mapping[str, int] | None = None,
) -> StructureMaterialization:
    """Allocate, emit and reference every structural edit a build must place.

    **One request per owned slot**, ordered by the slot's own durable owner,
    against the caller's reservation set, so the same project produces the same
    addresses on every machine. A slot that carries a created layer AND a resize
    of it is ONE edit - the grown record - because two records for one slot would
    be two root-slot writes to the same field and two records nothing could tell
    apart. Each request is EXPANDED_ONLY: a layer record grows with the authored
    grid and the canonical image declares one 256-byte free region, so the
    domain's aggregate demand cannot be served canonically - which is also exactly
    the above-EOF addressability this capability has to prove.
    """
    resolved_profile = profile if profile is not None else packaged_profile()
    view = _StructuralView(canonical, structure, resolved_profile)
    edits = _effective_edits(structure)
    if not edits:
        return StructureMaterialization((), (), (), (), ())

    taken: list[OwnedRegion] = [
        OwnedRegion(span, "build reservation") for span in tuple(reserved)
    ]
    expansion = resolved_profile.generated_expansion

    builds: list[StructureBuild] = []
    changes: list[ByteChange] = []
    generated: list[GeneratedAllocationProvenance] = []
    provenance: list[StructureEditProvenance] = []

    for _owner, edit in edits:
        resolved = resolve_layer_record(
            canonical,
            edit,
            view=view,
            layout=layout,
            chunk_addresses=chunk_addresses,
            profile=resolved_profile,
        )
        anchor = f"{STRUCTURE_PREFIX}{resolved.owner}"
        request = AllocationRequest(
            AnchorId(anchor),
            resolved.owner,
            len(resolved.record),
            LAYER_ALIGNMENT,
            kind=AllocationKind.LAYER_RECORD,
            addressability=Addressability.EXPANDED_ONLY,
            evidence=(
                "a map root's layer-slot field is a full 32-bit little-endian GBA "
                "address (MAP-RESIZE-AND-LAYERS-001), the canonical image declares "
                "one 256-byte VERIFIED_FREE region, and a dominant record is "
                "0x18 + 4*columns*rows bytes"
            ),
        )
        allocation = allocate(resolved_profile, [request], occupied=taken)[0]
        taken.append(OwnedRegion(allocation.range, resolved.owner))
        destination = allocation.range.start.value
        previous_bytes = (
            canonical[destination:destination + len(resolved.record)]
            if destination < len(canonical)
            else bytes([expansion.padding_byte]) * len(resolved.record)
            if expansion is not None
            else b""
        )
        if len(previous_bytes) != len(resolved.record):  # pragma: no cover
            raise MapStructureError(
                f"{resolved.owner}: allocated span at {destination:#x} cannot carry "
                "the layer record"
            )
        changes.append(
            ByteChange(
                offset=destination,
                old=previous_bytes,
                new=resolved.record,
                owner=resolved.owner,
                reason=(
                    "authored dominant layer record" if resolved.kind == "layer"
                    else "resized dominant layer record"
                ),
            )
        )

        entry = view.entry(resolved.map_index)
        slot_field = mg.root_layer_slot_address(entry.root_address, resolved.layer_slot)
        slot_offset = view.reader.offset(slot_field)
        previous_record = view.reader.u32(slot_field)
        if previous_record == allocation.rom_address:  # pragma: no cover
            raise MapStructureError(
                f"{resolved.owner}: the root already names the authored record"
            )
        changes.append(
            ByteChange(
                offset=slot_offset,
                old=previous_record.to_bytes(4, "little"),
                new=allocation.rom_address.to_bytes(4, "little"),
                owner=resolved.owner,
                reason=f"map root layer slot BG{resolved.layer_slot} references the "
                       "authored record",
            )
        )

        extents: list[StructureExtentProvenance] = []
        for axis, field, authored in resolved.extent_changes:
            previous = view.reader.u16(field)
            changes.append(
                ByteChange(
                    offset=view.reader.offset(field),
                    old=previous.to_bytes(2, "little"),
                    new=authored.to_bytes(2, "little"),
                    owner=resolved.owner,
                    reason=f"map extent {axis} covers the resized layer grid",
                )
            )
            extents.append(
                StructureExtentProvenance(
                    axis=axis,
                    offset=view.reader.offset(field),
                    previous=previous,
                    authored=authored,
                )
            )

        authored_cells = tuple(
            (destination + mg.LAYER_CHUNK_WINDOW_OFFSET + 4 * cell, identity)
            for cell, _address, _ordinal, identity in resolved.window
            if identity is not None
        )
        fills: dict[str, tuple[int | None, tuple[int, ...]]] = {}
        for cell, _address, ordinal, identity in resolved.window:
            if identity is None:
                continue
            offset = destination + mg.LAYER_CHUNK_WINDOW_OFFSET + 4 * cell
            current = fills.setdefault(identity, (ordinal, ()))
            fills[identity] = (current[0], current[1] + (offset,))

        if allocation.is_expanded:
            generated.append(
                allocation.generated_allocation_provenance(
                    domain=DOMAIN,
                    resource=resolved.owner,
                    pointer_offset=slot_offset,
                    source_range=RomRange(FileOffset(previous_record - 0x08000000), 4),
                )
            )

        builds.append(
            StructureBuild(
                resolved=resolved,
                allocation=allocation,
                slot_offset=slot_offset,
                previous_record_address=previous_record,
                placement=None,
                authored_cells=authored_cells,
            )
        )
        provenance.append(
            StructureEditProvenance(
                kind=resolved.kind,
                owner=resolved.owner,
                map_index=resolved.map_index,
                layer_slot=resolved.layer_slot,
                template_address=resolved.template_address,
                retail_columns=resolved.retail_columns,
                retail_rows=resolved.retail_rows,
                columns=resolved.columns,
                rows=resolved.rows,
                slot_offset=slot_offset,
                previous_record_address=previous_record,
                record_address=allocation.rom_address,
                record_size=len(resolved.record),
                allocation_file_offset=destination,
                allocation_size=allocation.range.size,
                expanded=allocation.is_expanded,
                expansion_evidence=allocation.free_region_evidence,
                record_sha256=resolved.record_sha256,
                fills=tuple(
                    StructureFillProvenance(
                        chunk=identity,
                        ordinal=ordinal,
                        address=(chunk_addresses or {}).get(identity, 0),
                        offsets=offsets,
                    )
                    for identity, (ordinal, offsets) in sorted(fills.items())
                ),
                extents=tuple(extents),
                cell_entries=sum(
                    1
                    for cell in (layout or _empty_layout())
                    .for_map(resolved.map_index)
                    .get(resolved.layer_slot, {})
                ),
                authored_layer=resolved.authored_layer,
                authored_columns=resolved.authored_columns,
                authored_rows=resolved.authored_rows,
            )
        )

    spans = tuple(region.range for region in taken[len(tuple(reserved)):])
    image: GeneratedImage | None = None
    if generated and expansion is not None:
        image = expansion.generated_image(
            resolved_profile.size, tuple(item.allocated_range for item in generated)
        )
    return StructureMaterialization(
        builds=tuple(builds),
        changes=tuple(changes),
        generated_allocations=tuple(generated),
        reserved=spans,
        provenance=tuple(provenance),
        generated_image=image,
    )


# --- reopen ------------------------------------------------------------------


def structural_layers(
    canonical: bytes,
    structure: "MapStructure",
    *,
    profile: "RomProfile | None" = None,
) -> tuple[StructuralLayer, ...]:
    """Every slot this structure authors, resolved against the canonical image."""
    view = _StructuralView(canonical, structure, profile)
    return tuple(
        view.structural_layer(map_index, slot)
        for map_index, slot in sorted(structure.structural_slots())
    )
