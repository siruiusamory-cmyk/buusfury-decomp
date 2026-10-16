"""MAP-CHUNK-AUTHORING-001 - creating a chunk that did not exist before.

The production authority for *chunk creation*, and nothing else. MAP-TILE-PAINT-001
taught the editor to point a dominant layer's cell at a chunk **a dominant layer of
the same map already uses**, which is a fixed-width in-place write. This module owns the step
past that: a chunk body the canonical image does not contain, composed by the
author, materialized by the production allocator, and referenced by a map cell.

What one chunk is, measured rather than assumed
------------------------------------------------

Every fact below was measured over the canonical image's own chunk corpus - all
3,745 distinct bodies reachable from its 1,516 dominant layers - and the numbers
are stated here so a reader does not have to re-derive them:

* a chunk is a **Webfoot container** whose declared size is exactly
  :data:`~tools.webfoot.formats.map_graphics.CHUNK_DECODED_BYTES` (0x800);
* its payload is **1,024 little-endian 16-bit screen entries** - one 32x32 plane,
  256x256 pixels - and that is the whole object: there is no metadata outside the
  plane;
* the entry's fields are the hardware's: bits 0-9 tile ordinal (every entry in the
  corpus stays inside that mask), bit 10 horizontal flip, bit 11 vertical flip,
  and bits 12-15 the palette bank, which the corpus sets to zero in all 3,834,880
  entries because a tile at 8bpp indexes the full palette;
* every canonical chunk is container **kind 1**, so an authored chunk is emitted
  as kind 1 too (:func:`tools.webfoot.formats.map_graphics.pack_dominant_chunk`);
* a layer cell holds a **four-byte little-endian GBA address** naming that
  container, and nothing masks or truncates it;
* there is **no chunk catalog**. A chunk is discovered only from the layer window
  that points at it, which is why a template is named by the layer ordinal a
  person can see rather than by a table index that does not exist;
* chunks **are** shared - 165 of the 3,745 bodies are referenced by more than one
  cell and 160 of those are shared across different maps - which is why creating a
  chunk must never mutate its source.

Why an authored chunk is map-scoped
-----------------------------------

A chunk plane holds tile **ordinals**, and an ordinal only means anything resolved
through the assembled character block of the map whose layer points at it. Those
blocks are per map: an assembly over a 42-map sample produced 42 distinct blocks.
So an authored chunk is composed against one map's character block and may be
placed only in that map's layers. Cross-map reuse would need character-block
equality proved first; this module refuses rather than assumes it.

What this module will not do
----------------------------

It adds no graphic tiles, no palettes and no imported artwork. The vocabulary an
author composes from is exactly the screen entries the template's own layer
already displays, so an authored chunk is a new **arrangement** of graphics the
game already ships. Widening that vocabulary is graphics import, a later
capability.
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
from .map_layout_write import window_ordinals
from .packaged import packaged_profile
from .write import (
    ByteChange,
    ChunkEditProvenance,
    ChunkEntryProvenance,
    ChunkPlacementProvenance,
    GeneratedAllocationProvenance,
    GeneratedImage,
)

if TYPE_CHECKING:
    from .profile import RomProfile
    from .project.model import AuthoredChunk, AuthoredChunks


class ChunkAuthoringError(ValueError):
    """A chunk could not be created, composed, placed or materialized.

    One public failure type for the whole surface, for the reason the paint and
    layout surfaces give: the readers underneath raise several unrelated
    ``ValueError`` subclasses and a caller either authors a chunk or is refused.
    The message names the specific reason.
    """


#: The prefix of an authored chunk's durable identity. Lowercase and stable, so a
#: chunk exists before any build has chosen where its body will live.
CHUNK_IDENTITY_PREFIX = "chunk:"

#: The name an authored chunk identity may carry, matching the authored-placement
#: precedent so a project's two authored resource kinds read the same way.
_NAME = re.compile(r"[a-z][a-z0-9_-]{0,63}")

#: ``map:NNNN/layer:N/chunk:N`` - the canonical chunk a body started from, named
#: by the layer's own 1-based vocabulary ordinal. Resolved against the CANONICAL
#: image and never against the authored one, so painting a cell can never
#: re-point a template that names it.
_TEMPLATE = re.compile(r"^map:(\d{4})/layer:([0-3])/chunk:(\d+)$")

#: Chunk containers are 4-byte aligned in the canonical corpus - measured: every
#: one of the 3,745 addresses is a multiple of four, and the residues mod 16 are
#: evenly spread, so four is the format's requirement and sixteen is not.
CHUNK_ALIGNMENT = 4

#: The build-domain names recorded on this domain's provenance, kept distinct
#: from every canonical kind so a manifest reader can tell an authored chunk from
#: a canonical one without consulting the image.
OWNER_PREFIX = "chunk:"
DOMAIN = "map_chunk"


def chunk_identity(name: object) -> str:
    """The durable identity for an author-chosen chunk name, or refuse it."""
    if not isinstance(name, str):
        raise ChunkAuthoringError("a chunk name must be a string")
    text = name if name.startswith(CHUNK_IDENTITY_PREFIX) else CHUNK_IDENTITY_PREFIX + name
    if _NAME.fullmatch(text[len(CHUNK_IDENTITY_PREFIX):]) is None:
        raise ChunkAuthoringError(
            f"chunk name {name!r} must be 'chunk:<name>' where <name> starts with a "
            "lowercase letter and holds only a-z, 0-9, '_' and '-' (at most 64)"
        )
    return text


@dataclass(frozen=True, slots=True)
class ChunkTemplate:
    """The canonical chunk an authored body started from.

    Named by the layer's own **1-based vocabulary ordinal** - the same "Chunk N"
    the map editor shows and the same vocabulary ``maps/layout.toml`` stores -
    because that is the only handle the format has: there is no chunk catalog, so
    a chunk's identity is the layer that uses it.
    """

    map_index: int
    layer_slot: int
    ordinal: int

    def __post_init__(self) -> None:
        if type(self.map_index) is not int or self.map_index < 0:
            raise ChunkAuthoringError("a chunk template needs a map index")
        if type(self.layer_slot) is not int or not 0 <= self.layer_slot < 4:
            raise ChunkAuthoringError("a chunk template layer must be BG0..BG3")
        if type(self.ordinal) is not int or self.ordinal < 1:
            raise ChunkAuthoringError(
                "a chunk template ordinal is 1-based, so 0 is not a chunk"
            )

    @property
    def text(self) -> str:
        """The stored form: ``map:NNNN/layer:N/chunk:N``."""
        return f"map:{self.map_index:04d}/layer:{self.layer_slot}/chunk:{self.ordinal}"

    @classmethod
    def parse(cls, text: object) -> "ChunkTemplate":
        match = _TEMPLATE.match(text) if isinstance(text, str) else None
        if match is None:
            raise ChunkAuthoringError(
                f"chunk template {text!r} is not 'map:NNNN/layer:N/chunk:N'"
            )
        return cls(
            map_index=int(match.group(1), 10),
            layer_slot=int(match.group(2), 10),
            ordinal=int(match.group(3), 10),
        )


@dataclass(frozen=True, slots=True)
class ChunkEntryEdit:
    """One screen-entry cell the author changed, with what it replaced."""

    row: int
    column: int
    prior: int
    entry: int

    @property
    def cell(self) -> int:
        return self.row * mg.CHUNK_SIDE_TILES + self.column


@dataclass(frozen=True, slots=True)
class ResolvedAuthoredChunk:
    """An authored chunk resolved against the canonical image.

    Everything a build needs to materialize the body, and everything an audit
    needs to explain it, with nothing left to look up.
    """

    identity: str
    template: ChunkTemplate
    template_address: int
    #: The template's own 1,024 entries, before the authored delta.
    template_entries: tuple[int, ...]
    #: The authored body: the template with every edit applied.
    entries: tuple[int, ...]
    #: The authored cells, row-major, each carrying the entry it replaced.
    edits: tuple[ChunkEntryEdit, ...]
    #: The packed container a build writes, in the kind every canonical chunk is.
    container: bytes
    #: The layer whose vocabulary the body was composed from.
    vocabulary: tuple[int, ...]

    @property
    def body(self) -> bytes:
        """The 0x800 decoded screen-entry payload."""
        return mg.chunk_body_bytes(self.entries)

    @property
    def body_sha256(self) -> str:
        return hashlib.sha256(self.body).hexdigest()

    @property
    def map_index(self) -> int:
        """The map whose character block this body's ordinals are meaningful in."""
        return self.template.map_index


@dataclass(frozen=True, slots=True)
class ChunkPlacement:
    """One map cell - or one build-materialized structure - an author pointed a
    chunk at.

    ``offset`` is the file offset of the four-byte pointer field this placement
    rewrites, and ``previous`` is what the canonical image holds there. A
    **structural** placement (MAP-RESIZE-AND-LAYERS-001) has neither: the field
    that will name the chunk lives inside a layer record the build materializes
    above canonical EOF, so there is no canonical site to rewrite and no previous
    value. Such a placement carries ``offset = -1`` and ``cell = -1``, exists so
    the chunk is materialized at all, and emits no cell write of its own - the
    structure's own record write is what carries the address, and it is owned by
    the structure's allocation.
    """

    map_index: int
    layer_slot: int
    cell: int
    #: File offset of the four-byte pointer field this placement rewrites, or -1
    #: for a structure-resident reference that has no canonical site.
    offset: int
    #: The pointer the canonical image holds at that cell; 0 when there is no site.
    previous: int
    identity: str
    #: ``"cell"`` for a canonical chunk-window cell, ``"structure"`` for a
    #: reference that only a build-materialized layer record carries.
    kind: str = "cell"

    @property
    def owner(self) -> str:
        if self.kind == "structure":
            return f"map:{self.map_index:04d} layer {self.layer_slot} structure"
        return f"map:{self.map_index:04d} layer {self.layer_slot} cell {self.cell}"

    @property
    def is_structural(self) -> bool:
        return self.kind == "structure"


@dataclass(frozen=True, slots=True)
class ChunkBuild:
    """One authored chunk, placed by the allocator, with its reference sites."""

    resolved: ResolvedAuthoredChunk
    allocation: Allocation
    placements: tuple[ChunkPlacement, ...]

    @property
    def identity(self) -> str:
        return self.resolved.identity

    @property
    def rom_address(self) -> int:
        return self.allocation.rom_address

    @property
    def expanded(self) -> bool:
        return self.allocation.is_expanded


@dataclass(frozen=True, slots=True)
class ChunkMaterialization:
    """Everything this domain contributes to one build's single write plan."""

    builds: tuple[ChunkBuild, ...]
    #: The appended bodies and the four-byte cell references, both attributed.
    changes: tuple[ByteChange, ...]
    generated_allocations: tuple[GeneratedAllocationProvenance, ...]
    #: The spans this domain took, for the build-scoped reservation set.
    reserved: tuple[RomRange, ...]
    #: The per-chunk audit record the manifest carries.
    provenance: tuple[ChunkEditProvenance, ...]
    #: The expansion policy this domain's spans imply, or None when every body
    #: fitted a declared canonical region. A build with more than one allocating
    #: domain merges these into the single policy the plan is validated against.
    generated_image: GeneratedImage | None = None


# --- reading the canonical image ---------------------------------------------


class _CanonicalView:
    """One reader plus the lookups a chunk authoring session repeats.

    Layer vocabularies and layer pointer windows are read again for every chunk
    and every placement, and both are pure functions of the immutable image, so
    they are memoized here rather than re-derived at each call site.
    """

    __slots__ = ("image", "profile", "_reader", "_entries", "_vocab", "_pointers")

    def __init__(self, canonical: bytes, profile: "RomProfile | None" = None) -> None:
        self.image = bytes(canonical)
        self.profile = profile if profile is not None else packaged_profile()
        self._reader = mg.MapGraphicsReader(self.image, self.profile)
        self._entries = mg.read_map_entries(self._reader)
        self._vocab: dict[tuple[int, int], tuple[int, ...]] = {}
        self._pointers: dict[tuple[int, int], tuple[int, ...]] = {}

    @property
    def reader(self) -> mg.MapGraphicsReader:
        return self._reader

    @property
    def map_entry_count(self) -> int:
        return self._reader.map_entry_count()

    def layer(self, map_index: int, layer_slot: int) -> mg.LayerRecord:
        if type(map_index) is not int or not 0 <= map_index < self.map_entry_count:
            raise ChunkAuthoringError(
                f"map index {map_index!r} is outside this profile's 0.."
                f"{self.map_entry_count - 1} declared map-entry range"
            )
        if type(layer_slot) is not int or not 0 <= layer_slot < len(mg.ROOT_LAYER_SLOTS):
            raise ChunkAuthoringError(
                f"layer slot {layer_slot!r} is outside BG0..BG3"
            )
        try:
            record = mg.read_layer(
                self._reader, self._entries[map_index].root_address, layer_slot
            )
        except mg.MapGraphicsError as exc:
            raise ChunkAuthoringError(
                f"map:{map_index:04d} BG{layer_slot} could not be read: {exc}"
            ) from exc
        if record.handler != mg.DOMINANT_LAYER_HANDLER:
            raise ChunkAuthoringError(
                f"BG{layer_slot} of map:{map_index:04d} is {record.classification}, "
                "which has no chunk grid"
            )
        return record

    def pointers(self, map_index: int, layer_slot: int) -> tuple[int, ...]:
        """The layer's distinct non-null chunk pointers, in first-appearance order.

        This is one layer's own chunk vocabulary, which is the set a template ordinal
        resolves against: a chunk is authored by naming the layer that draws it.
        Since MAP-PAINT-ANY-CHUNK-001 it is NOT the numbering ``map_paint`` or a
        project's ``layout`` ordinals use - those count across every dominant layer of
        the map, so a borrowed chunk has a different number in each. Use
        ``LayoutSlot.template_target`` to cross between them.
        """
        key = (map_index, layer_slot)
        cached = self._pointers.get(key)
        if cached is None:
            record = self.layer(map_index, layer_slot)
            cached = tuple(window_ordinals(record.chunk_addresses))
            self._pointers[key] = cached
        return cached

    def vocabulary(self, map_index: int, layer_slot: int) -> tuple[int, ...]:
        """Every screen entry the layer's own chunks display, in first-appearance order.

        The permitted authoring vocabulary, and the reason an authored chunk adds
        no graphics: each value here is an entry some map of the shipping game
        already draws, so composing from it cannot introduce a tile, a palette or
        a flip combination the engine has not already been seen to accept.
        """
        key = (map_index, layer_slot)
        cached = self._vocab.get(key)
        if cached is None:
            seen: dict[int, None] = {}
            for address in self.pointers(map_index, layer_slot):
                for entry in mg.dominant_chunk_words(self._reader, address):
                    seen.setdefault(entry, None)
            cached = tuple(seen)
            self._vocab[key] = cached
        return cached


# --- resolving an authored chunk ---------------------------------------------


def resolve_template(
    view: _CanonicalView, template: ChunkTemplate
) -> tuple[int, tuple[int, ...]]:
    """The container address and entries a template names, or refuse it.

    The ordinal is resolved against the LAYER the template names and its own
    first-appearance vocabulary, because a chunk is authored by naming the layer that
    draws it. That is not the map-wide ordinal a project stores
    (``map_paint.PaintChunk.ordinal``), so a caller holding one of those must
    translate it first with ``LayoutSlot.template_target``. Resolving a map-wide
    ordinal here would refuse a legal chunk and report the layer's own count.
    """
    pointers = view.pointers(template.map_index, template.layer_slot)
    if template.ordinal > len(pointers):
        raise ChunkAuthoringError(
            f"template {template.text} names chunk {template.ordinal}, but "
            f"map:{template.map_index:04d} BG{template.layer_slot} uses only "
            f"{len(pointers)} distinct chunk(s)"
        )
    address = pointers[template.ordinal - 1]
    try:
        entries = mg.dominant_chunk_words(view.reader, address)
    except mg.MapGraphicsError as exc:
        raise ChunkAuthoringError(
            f"template {template.text} at {address:#010x} is not a dominant chunk: {exc}"
        ) from exc
    return address, entries


def compose_body(
    template_entries: tuple[int, ...],
    edits: Iterable[ChunkEntryEdit],
    vocabulary: tuple[int, ...],
) -> tuple[int, ...]:
    """Apply authored cell edits to a template plane, validating every one.

    Every refusal the format cares about happens here, before anything is planned
    or written: a coordinate outside the plane, a non-entry value, a prior that
    disagrees with the template the edit claims to be against, and an entry
    outside the permitted vocabulary. Each authored cell must also actually
    *change* something - a chunk whose only content is "the same as its template"
    is a byte-identical copy, not an authored chunk.
    """
    plane = list(template_entries)
    if len(plane) != mg.CHUNK_ENTRY_COUNT:
        raise ChunkAuthoringError(
            f"a template plane holds {mg.CHUNK_ENTRY_COUNT} entries, not {len(plane)}"
        )
    permitted = frozenset(vocabulary)
    seen: set[int] = set()
    for edit in edits:
        if not 0 <= edit.row < mg.CHUNK_SIDE_TILES or not 0 <= edit.column < mg.CHUNK_SIDE_TILES:
            raise ChunkAuthoringError(
                f"chunk cell ({edit.row}, {edit.column}) is outside the "
                f"{mg.CHUNK_SIDE_TILES}x{mg.CHUNK_SIDE_TILES} plane"
            )
        if edit.cell in seen:
            raise ChunkAuthoringError(
                f"chunk cell ({edit.row}, {edit.column}) is edited twice"
            )
        seen.add(edit.cell)
        for name, value in (("prior", edit.prior), ("entry", edit.entry)):
            if type(value) is not int or not 0 <= value <= 0xFFFF:
                raise ChunkAuthoringError(
                    f"chunk cell ({edit.row}, {edit.column}) has a {name} of "
                    f"{value!r}, which is not a 16-bit screen entry"
                )
        if plane[edit.cell] != edit.prior:
            raise ChunkAuthoringError(
                f"chunk cell ({edit.row}, {edit.column}) was authored against "
                f"{edit.prior:#06x}, but the template holds "
                f"{plane[edit.cell]:#06x}; the chunk was not composed from this "
                "template"
            )
        if edit.entry not in permitted:
            raise ChunkAuthoringError(
                f"chunk cell ({edit.row}, {edit.column}) would hold "
                f"{edit.entry:#06x}, which no chunk of the template's layer "
                "displays; authoring may only rearrange graphics the layer "
                "already uses"
            )
        plane[edit.cell] = edit.entry
    return tuple(plane)


def resolve_authored_chunk(
    canonical: bytes,
    chunk: "AuthoredChunk",
    *,
    profile: "RomProfile | None" = None,
    view: _CanonicalView | None = None,
) -> ResolvedAuthoredChunk:
    """Resolve a declared authored chunk against the canonical image.

    Fails closed on everything a hand-edited project could get wrong: an
    unparseable template, a template the layer does not offer, a stored prior that
    disagrees with the template, and an authored entry outside the layer's
    vocabulary.
    """
    from .project import ProjectError

    resolved_view = view if view is not None else _CanonicalView(canonical, profile)
    try:
        template = ChunkTemplate.parse(chunk.template)
        address, template_entries = resolve_template(resolved_view, template)
    except ProjectError as exc:  # pragma: no cover - defensive re-framing
        raise ChunkAuthoringError(str(exc)) from exc
    vocabulary = resolved_view.vocabulary(template.map_index, template.layer_slot)
    edits = tuple(
        ChunkEntryEdit(
            row=entry.row,
            column=entry.column,
            prior=entry.prior,
            entry=entry.entry,
        )
        for entry in chunk.entries
    )
    if not edits:
        raise ChunkAuthoringError(
            f"authored chunk {chunk.identity} edits no cell, so it would be a "
            "byte-identical copy of its template rather than a new chunk"
        )
    entries = compose_body(template_entries, edits, vocabulary)
    container = mg.pack_dominant_chunk(entries)
    return ResolvedAuthoredChunk(
        identity=chunk.identity,
        template=template,
        template_address=address,
        template_entries=template_entries,
        entries=entries,
        edits=tuple(sorted(edits, key=lambda e: (e.row, e.column))),
        container=container,
        vocabulary=vocabulary,
    )


# --- authoring: composing one chunk ------------------------------------------


def build_authored_chunk(
    canonical: bytes,
    identity: object,
    template: ChunkTemplate,
    entries: Mapping[tuple[int, int], int],
    *,
    profile: "RomProfile | None" = None,
    view: _CanonicalView | None = None,
) -> "AuthoredChunk":
    """Compose a new authored chunk from a template and a set of cell edits.

    This is the authoring entry point the Workbench calls: it takes the cells a
    person actually changed - ``{(row, column): entry}`` - resolves the template
    once, fills in each cell's prior value from that template, validates every
    entry against the layer's permitted vocabulary, and returns the value the
    project persists.

    Composing through here rather than through a hand-built document is what makes
    "the prior bytes are the template's" a property of the API rather than a
    promise: there is no way to state a prior that the template does not hold.
    """
    from .project import AuthoredChunk, AuthoredChunkEntry

    resolved_view = view if view is not None else _CanonicalView(canonical, profile)
    name = chunk_identity(identity)
    address, template_entries = resolve_template(resolved_view, template)
    del address
    vocabulary = resolved_view.vocabulary(template.map_index, template.layer_slot)
    authored: list[AuthoredChunkEntry] = []
    for (row, column), entry in sorted(entries.items()):
        if type(row) is not int or type(column) is not int:
            raise ChunkAuthoringError("a chunk cell coordinate must be an integer")
        if not 0 <= row < mg.CHUNK_SIDE_TILES or not 0 <= column < mg.CHUNK_SIDE_TILES:
            raise ChunkAuthoringError(
                f"chunk cell ({row}, {column}) is outside the "
                f"{mg.CHUNK_SIDE_TILES}x{mg.CHUNK_SIDE_TILES} plane"
            )
        if type(entry) is not int:
            raise ChunkAuthoringError("a screen entry must be an integer")
        prior = template_entries[row * mg.CHUNK_SIDE_TILES + column]
        if entry == prior:
            # A cell the author left at its template value is not an edit. It is
            # not an error either: a brush stroke re-enters cells it has already
            # painted, exactly as the map painter's does.
            continue
        if entry not in frozenset(vocabulary):
            raise ChunkAuthoringError(
                f"screen entry {entry:#06x} is not part of map:"
                f"{template.map_index:04d} BG{template.layer_slot}'s graphics "
                "vocabulary"
            )
        authored.append(
            AuthoredChunkEntry(row=row, column=column, prior=prior, entry=entry)
        )
    if not authored:
        raise ChunkAuthoringError(
            "a new chunk must differ from its template; every cell given is "
            "already at that value"
        )
    return AuthoredChunk(
        identity=name, template=template.text, entries=tuple(authored)
    )


# --- placement legality ------------------------------------------------------


def validate_authored_placement(
    chunk_map: int, map_index: int, layer_slot: int
) -> None:
    """Whether an authored chunk may be placed in this map and layer.

    A chunk's plane holds tile ordinals, and an ordinal is only meaningful inside
    the assembled character block of the map it was composed against, so the one
    hard rule is that the placement's map is the template's map. The layer is free
    - every layer of a map shares that map's character block - and the layer's own
    form is checked by the caller, which already reads it.
    """
    if map_index != chunk_map:
        raise ChunkAuthoringError(
            f"an authored chunk composed against map:{chunk_map:04d} cannot be "
            f"placed in map:{map_index:04d}: a chunk plane holds tile ordinals, "
            "which only resolve through the character block of the map it was "
            "composed against"
        )
    if type(layer_slot) is not int or not 0 <= layer_slot < len(mg.ROOT_LAYER_SLOTS):
        raise ChunkAuthoringError(f"layer slot {layer_slot!r} is outside BG0..BG3")


def placements_for(
    canonical: bytes,
    chunks: Mapping[str, "AuthoredChunk"],
    edits: Mapping[tuple[int, int, int], str],
    *,
    profile: "RomProfile | None" = None,
    view: _CanonicalView | None = None,
) -> tuple[ChunkPlacement, ...]:
    """Resolve authored chunk-cell references into their exact pointer fields.

    Every refusal happens here, before a build plans anything: an identity no
    document declares, a map/layer that is not a dominant chunk grid, a cell
    outside that layer's own grid, and a chunk whose character-block scope does
    not include the map it is being placed in.
    """
    from .map_layout_write import MapLayoutWriteError, MapLayoutWriter

    resolved_view = view if view is not None else _CanonicalView(canonical, profile)
    try:
        writer = MapLayoutWriter(resolved_view.image, profile=resolved_view.profile)
    except MapLayoutWriteError as exc:
        raise ChunkAuthoringError(str(exc)) from exc
    placements: list[ChunkPlacement] = []
    for (map_index, layer_slot, cell), identity in sorted(edits.items()):
        chunk = chunks.get(identity)
        if chunk is None:
            raise ChunkAuthoringError(
                f"map:{map_index:04d} BG{layer_slot} cell {cell} names authored "
                f"chunk {identity!r}, which this project does not declare"
            )
        template = ChunkTemplate.parse(chunk.template)
        validate_authored_placement(template.map_index, map_index, layer_slot)
        record = resolved_view.layer(map_index, layer_slot)
        if type(cell) is not int or not 0 <= cell < len(record.chunk_addresses):
            raise ChunkAuthoringError(
                f"chunk cell {cell!r} is outside BG{layer_slot}'s "
                f"{record.chunk_x}x{record.chunk_y} grid"
            )
        try:
            offset = writer.chunk_pointer_offset(map_index, layer_slot, cell)
        except MapLayoutWriteError as exc:  # pragma: no cover - grid already checked
            raise ChunkAuthoringError(str(exc)) from exc
        placements.append(
            ChunkPlacement(
                map_index=map_index,
                layer_slot=layer_slot,
                cell=cell,
                offset=offset,
                previous=record.chunk_addresses[cell],
                identity=identity,
            )
        )
    duplicate = len({(p.map_index, p.layer_slot, p.cell) for p in placements})
    if duplicate != len(placements):
        raise ChunkAuthoringError("an authored placement names one cell twice")
    return tuple(placements)


# --- materialization ---------------------------------------------------------


def materialize_authored_chunks(
    canonical: bytes,
    chunks: Mapping[str, "AuthoredChunk"],
    edits: Mapping[tuple[int, int, int], str],
    *,
    profile: "RomProfile | None" = None,
    reserved: Iterable[RomRange] = (),
    structural: Iterable[ChunkPlacement] = (),
) -> ChunkMaterialization:
    """Allocate, encode and reference every authored chunk a build must place.

    Only chunks a cell actually references are materialized. A chunk body exists
    in an image because something points at it: an unreferenced body would be
    dead weight, and the allocation record's ``pointer_offset`` is precisely the
    field that references the span, which an unplaced chunk does not have. A
    declared-but-unplaced chunk is still a durable project resource - it keeps its
    identity, its body and its edits across a reopen - and materializes as soon as
    a cell names it.

    ``structural`` carries references a layer record the build itself materializes
    will hold - a structural edit's initialization chunk, or a cell of a
    project-authored layer. They have no canonical site to rewrite (the record
    does not exist in the canonical image), so they materialize the body and emit
    no write of their own: the structure domain's own record write carries the
    address, and that write is owned by the structure domain's allocation.

    The bodies are placed by the production allocator, one request per chunk,
    against the caller's reservation set, in the order of the chunks' own
    identities, so the same project produces the same addresses on every machine.
    """
    resolved_profile = profile if profile is not None else packaged_profile()
    view = _CanonicalView(canonical, resolved_profile)
    placements = placements_for(
        canonical, chunks, edits, profile=resolved_profile, view=view
    )
    placements = placements + tuple(structural)
    if not placements:
        return ChunkMaterialization((), (), (), (), ())
    for placement in placements:
        if placement.identity not in chunks:
            raise ChunkAuthoringError(
                f"map:{placement.map_index:04d} BG{placement.layer_slot} names "
                f"authored chunk {placement.identity!r}, which this project does "
                "not declare"
            )
    # A structural reference carries no cell of its own (cell = -1): the field that
    # will name it lives inside a record the build materializes, and one slot's
    # record may name more than one authored body - a created layer that was then
    # grown initializes some cells from its own initialization and the rest from
    # the resize's. What distinguishes those is the chunk each one names, so the
    # identity joins the key for structural placements only; a canonical cell is
    # still one cell and still claimed once.
    site_keys = [
        (
            p.map_index,
            p.layer_slot,
            p.cell,
            p.kind,
            p.identity if p.is_structural else "",
        )
        for p in placements
    ]
    if len(set(site_keys)) != len(site_keys):
        raise ChunkAuthoringError("an authored placement names one cell twice")

    by_identity: dict[str, list[ChunkPlacement]] = {}
    for placement in placements:
        by_identity.setdefault(placement.identity, []).append(placement)

    referenced = sorted(by_identity)
    # The allocator's reservation set is typed `OwnedRegion`; a bare span is not
    # enough, because an owner is what makes an overlapping reservation set an
    # error the allocator can report rather than a union it silently accepts.
    taken: list[OwnedRegion] = [
        OwnedRegion(span, "build reservation") for span in tuple(reserved)
    ]

    builds: list[ChunkBuild] = []
    changes: list[ByteChange] = []
    generated: list[GeneratedAllocationProvenance] = []
    provenance: list[ChunkEditProvenance] = []

    expansion = resolved_profile.generated_expansion
    for identity in referenced:
        chunk = chunks[identity]
        resolved = resolve_authored_chunk(
            canonical, chunk, profile=resolved_profile, view=view
        )
        sites = by_identity[identity]
        request = AllocationRequest(
            AnchorId(f"{OWNER_PREFIX}{identity}"),
            f"{OWNER_PREFIX}{identity}",
            len(resolved.container),
            CHUNK_ALIGNMENT,
            kind=AllocationKind.CHUNK_BODY,
            addressability=Addressability.EXPANDED_PERMITTED,
            evidence=(
                "a dominant layer's chunk cell is a full 32-bit little-endian GBA "
                "address (MAP-CHUNK-AUTHORING-001), and the canonical image "
                "declares no VERIFIED_FREE region large enough for a chunk body"
            ),
        )
        allocation = allocate(
            resolved_profile, [request], occupied=taken
        )[0]
        taken.append(OwnedRegion(allocation.range, f"{OWNER_PREFIX}{identity}"))
        address = allocation.rom_address
        destination = allocation.range.start.value
        previous_bytes = (
            canonical[destination:destination + len(resolved.container)]
            if destination < len(canonical)
            else bytes([expansion.padding_byte]) * len(resolved.container)
            if expansion is not None
            else b""
        )
        if len(previous_bytes) != len(resolved.container):  # pragma: no cover
            raise ChunkAuthoringError(
                f"{identity}: allocated span at {destination:#x} cannot carry the "
                "authored body"
            )
        changes.append(
            ByteChange(
                offset=destination,
                old=previous_bytes,
                new=resolved.container,
                owner=f"{OWNER_PREFIX}{identity}",
                reason="authored dominant chunk body",
            )
        )
        for site in sites:
            if site.is_structural:
                # The field that will name this chunk lives inside a record the
                # build materializes; there is nothing canonical to rewrite.
                continue
            changes.append(
                ByteChange(
                    offset=site.offset,
                    old=site.previous.to_bytes(4, "little"),
                    new=address.to_bytes(4, "little"),
                    owner=site.owner,
                    reason=f"map cell references authored chunk {identity}",
                )
            )
        cell_sites = tuple(site for site in sites if not site.is_structural)
        if allocation.is_expanded:
            generated.append(
                allocation.generated_allocation_provenance(
                    domain=DOMAIN,
                    resource=identity,
                    pointer_offset=(
                        cell_sites[0].offset if cell_sites else None
                    ),
                    source_range=RomRange(
                        FileOffset(resolved.template_address - 0x08000000),
                        len(resolved.container),
                    ),
                )
            )
        builds.append(
            ChunkBuild(resolved=resolved, allocation=allocation, placements=tuple(sites))
        )
        provenance.append(
            ChunkEditProvenance(
                resource=identity,
                owner=f"{OWNER_PREFIX}{identity}",
                template=resolved.template.text,
                template_address=resolved.template_address,
                body_sha256=resolved.body_sha256,
                container_size=len(resolved.container),
                allocation_file_offset=destination,
                allocation_size=allocation.range.size,
                rom_address=address,
                expanded=allocation.is_expanded,
                expansion_evidence=allocation.free_region_evidence,
                edits=tuple(
                    ChunkEntryProvenance(
                        row=edit.row,
                        column=edit.column,
                        prior=edit.prior,
                        entry=edit.entry,
                    )
                    for edit in resolved.edits
                ),
                placements=tuple(
                    ChunkPlacementProvenance(
                        map_index=site.map_index,
                        layer_slot=site.layer_slot,
                        cell=site.cell,
                        previous=site.previous,
                        offset=site.offset,
                        chunk=identity,
                    )
                    for site in cell_sites
                ),
            )
        )

    spans = tuple(region.range for region in taken[len(tuple(reserved)):])
    image: GeneratedImage | None = None
    if generated and expansion is not None:
        image = expansion.generated_image(
            resolved_profile.size, tuple(item.allocated_range for item in generated)
        )
    return ChunkMaterialization(
        builds=tuple(builds),
        changes=tuple(changes),
        generated_allocations=tuple(generated),
        reserved=spans,
        provenance=tuple(provenance),
        generated_image=image,
    )


# --- authoring: the session a surface drives ---------------------------------


@dataclass(frozen=True, slots=True)
class ChunkTemplateChoice:
    """One canonical chunk a surface may offer as a starting point."""

    ordinal: int
    address: int
    #: How many cells of the layer currently reference this chunk.
    cell_count: int


class ChunkAuthor:
    """Read-and-compose authority over one immutable canonical image.

    The public surface a chunk editor drives, so a GUI never reaches into the
    private reader the build uses. It answers the questions a chunk authoring
    surface has to ask and nothing else:

    * which canonical chunks a layer offers as a starting point;
    * which screen entries that layer's graphics may be composed from;
    * what a starting chunk's plane currently holds;
    * and what a composed chunk resolves to, so the surface can preview it.

    Everything it returns is a pure function of the immutable image, so the same
    call answers the same way for the whole session and a surface may cache freely.
    """

    __slots__ = ("_view",)

    def __init__(self, canonical_bytes: bytes, *, profile: "RomProfile | None" = None) -> None:
        self._view = _CanonicalView(canonical_bytes, profile)

    @property
    def image(self) -> bytes:
        return self._view.image

    @property
    def profile(self) -> "RomProfile":
        return self._view.profile

    @property
    def map_entry_count(self) -> int:
        return self._view.map_entry_count

    def layer_label(self, map_index: int, layer_slot: int) -> str:
        """The layer's own description, so a surface cannot invent a second one."""
        record = self._view.layer(map_index, layer_slot)
        return f"BG{layer_slot} · chunk grid {record.chunk_x}×{record.chunk_y}"

    def templates(self, map_index: int, layer_slot: int) -> tuple[ChunkTemplateChoice, ...]:
        """The canonical chunks this layer uses, in its own 1-based order.

        This is the layer-scoped order a template ordinal resolves against. Since
        MAP-PAINT-ANY-CHUNK-001 it is NOT the numbering a project's ``layout``
        ordinals use: those count across every dominant layer of the map, so a chunk
        borrowed from a sibling has a different number in each. Use
        ``LayoutSlot.template_target`` to cross between the two.
        """
        record = self._view.layer(map_index, layer_slot)
        choices: list[ChunkTemplateChoice] = []
        for ordinal, address in enumerate(
            self._view.pointers(map_index, layer_slot), start=1
        ):
            choices.append(
                ChunkTemplateChoice(
                    ordinal=ordinal,
                    address=address,
                    cell_count=sum(
                        1 for pointer in record.chunk_addresses if pointer == address
                    ),
                )
            )
        return tuple(choices)

    def template_text(self, map_index: int, layer_slot: int, ordinal: int) -> str:
        """The stored template identity for one of :meth:`templates`."""
        return ChunkTemplate(map_index, layer_slot, ordinal).text

    def vocabulary(self, map_index: int, layer_slot: int) -> tuple[int, ...]:
        """Every screen entry this layer's own chunks display."""
        return self._view.vocabulary(map_index, layer_slot)

    def plane(self, template: ChunkTemplate) -> tuple[int, ...]:
        """A template's current 32x32 screen-entry plane, read from the image."""
        _address, entries = resolve_template(self._view, template)
        return entries

    def create(
        self,
        identity: object,
        template: ChunkTemplate,
        entries: Mapping[tuple[int, int], int],
    ) -> "AuthoredChunk":
        """Compose a new authored chunk from a template and changed cells."""
        return build_authored_chunk(
            self._view.image, identity, template, entries, view=self._view
        )

    def resolve(self, chunk: "AuthoredChunk") -> ResolvedAuthoredChunk:
        """Resolve a declared chunk fully, or refuse it."""
        return resolve_authored_chunk(
            self._view.image, chunk, profile=self._view.profile, view=self._view
        )

    def entry_label(self, entry: int) -> str:
        """A human label for one screen entry, naming the fields the format has.

        The ordinals are the hardware's fields, so the label states the tile and
        the two flip selectors, and reports the palette bank only when it is
        non-zero - which the canonical corpus never is, because a tile at 8bpp
        indexes the full palette.
        """
        tile = entry & mg.TILE_ENTRY_ORDINAL_MASK
        flips = ""
        if entry & mg.TILE_ENTRY_BIT_10:
            flips += "H"
        if entry & mg.TILE_ENTRY_BIT_11:
            flips += "V"
        bank = (entry >> 12) & 0xF
        parts = [f"tile {tile}"]
        if flips:
            parts.append(f"flip {flips}")
        if bank:
            parts.append(f"bank {bank}")
        return " · ".join(parts)


# --- authoring: project persistence ------------------------------------------
#
# The one authority through which an authored chunk and its placement reach the
# project. Shaped like `map_paint.set_layout_cells` on purpose: validate the whole
# batch against the canonical image first, load the project ONCE, apply on top of
# what is committed, and write only when the result actually differs - which is
# what makes an edit that changes nothing a no-op and what keeps a Workbench
# apply from creating a project revision.


def read_authored_chunks(project_dir) -> "AuthoredChunks":
    """The committed authored chunks for a project, in one load."""
    from .project import read_project

    return read_project(project_dir).chunks


def set_authored_chunk(
    project_dir,
    canonical_bytes: bytes,
    chunk: "AuthoredChunk",
    *,
    profile: "RomProfile | None" = None,
) -> bool:
    """Validate and persist one authored chunk. Returns whether the source changed.

    The chunk is fully resolved against the canonical image first - template,
    priors and every authored entry - so a chunk that cannot be built cannot be
    saved either, and the project never holds a resource the build would refuse.
    """
    from .project import AuthoredChunks, read_project, write_authored_chunks

    resolve_authored_chunk(canonical_bytes, chunk, profile=profile)
    committed = read_project(project_dir).chunks
    document = dict(committed.chunks)
    document[chunk.identity] = chunk
    updated = AuthoredChunks(chunks=dict(sorted(document.items())))
    if updated.chunks == committed.chunks:
        return False
    write_authored_chunks(project_dir, updated)
    return True


def remove_authored_chunk(project_dir, identity: str) -> bool:
    """Delete one authored chunk. Returns whether the project source changed.

    Refuses while any map cell still references the chunk: removing a referenced
    resource would leave a project whose layout names a chunk nobody declares,
    which `read_project` refuses - so the refusal happens here, where the message
    can name the cells, rather than at the next load.
    """
    from .project import AuthoredChunks, read_project, write_authored_chunks

    project = read_project(project_dir)
    if identity not in project.chunks.chunks:
        return False
    holders = sorted(
        key for key, value in project.layout.cells().items() if value == identity
    )
    if holders:
        listed = ", ".join(
            f"map:{m:04d} BG{layer} cell {cell}" for m, layer, cell in holders[:5]
        )
        raise ChunkAuthoringError(
            f"{identity} is still referenced by {len(holders)} map cell(s) "
            f"({listed}); remove those placements before deleting the chunk"
        )
    document = dict(project.chunks.chunks)
    document.pop(identity, None)
    write_authored_chunks(project_dir, AuthoredChunks(chunks=document))
    return True


def set_layout_authored_cells(
    project_dir,
    canonical_bytes: bytes,
    edits: Mapping[tuple[int, int, int], str | None],
    *,
    profile: "RomProfile | None" = None,
) -> bool:
    """Validate and persist authored-chunk cell placements in ONE write.

    ``edits`` maps ``(map index, layer slot, cell)`` to an authored chunk identity,
    or to ``None`` meaning "this cell carries no authored placement". The mirror of
    ``map_paint.set_layout_cells`` for the other value form a layout cell may
    hold: the whole batch is validated against the canonical image first through
    the same authority a build uses, the project is loaded once, and the document
    is rewritten only when the resulting set differs.
    """
    from .project import LayoutEdits, read_project, write_layout_edits

    view = _CanonicalView(canonical_bytes, profile)
    project = read_project(project_dir)
    if not edits:
        return False

    # 1. Validate the whole batch before touching the project.
    for key, identity in edits.items():
        map_index, layer_slot, cell = _placement_key(key)
        record = view.layer(map_index, layer_slot)
        if type(cell) is not int or not 0 <= cell < len(record.chunk_addresses):
            raise ChunkAuthoringError(
                f"chunk cell {cell!r} is outside BG{layer_slot}'s "
                f"{record.chunk_x}x{record.chunk_y} grid"
            )
        if identity is None:
            continue
        chunk = project.chunks.get(identity)
        if chunk is None:
            raise ChunkAuthoringError(
                f"{identity!r} is not an authored chunk of this project"
            )
        template = ChunkTemplate.parse(chunk.template)
        validate_authored_placement(template.map_index, map_index, layer_slot)

    # 2. Apply on top of what is committed, then write only if it differs.
    document: dict[str, dict[int, dict[int, int | str]]] = {
        key: {slot: dict(cells) for slot, cells in layers.items()}
        for key, layers in project.layout.maps.items()
    }
    for key, identity in edits.items():
        map_index, layer_slot, cell = _placement_key(key)
        map_key = LayoutEdits.key_for(map_index)
        if identity is None:
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
        document.setdefault(map_key, {}).setdefault(layer_slot, {})[cell] = identity

    updated = LayoutEdits(maps=document)
    if updated.maps == project.layout.maps:
        return False
    write_layout_edits(project_dir, updated)
    return True


def clear_layout_authored_cell(
    project_dir,
    canonical_bytes: bytes,
    map_index: int,
    layer_slot: int,
    cell: int,
    *,
    profile: "RomProfile | None" = None,
) -> bool:
    """Remove one authored placement, restoring the canonical chunk for that cell."""
    return set_layout_authored_cells(
        project_dir,
        canonical_bytes,
        {(map_index, layer_slot, cell): None},
        profile=profile,
    )


def _placement_key(key: object) -> tuple[int, int, int]:
    """Destructure one ``(map, layer, cell)`` placement key, or refuse it.

    A malformed key is a :class:`ChunkAuthoringError` like any other bad edit
    rather than a ``TypeError`` out of argument unpacking, which would be outside
    the family a GUI boundary catches - the documented dead-click failure mode.
    """
    if not isinstance(key, tuple) or len(key) != 3:
        raise ChunkAuthoringError(
            "an authored placement key must be a (map index, layer slot, cell) triple"
        )
    map_index, layer_slot, cell = key
    for name, value in (
        ("map index", map_index),
        ("layer slot", layer_slot),
        ("cell", cell),
    ):
        if type(value) is not int:
            raise ChunkAuthoringError(f"an authored placement's {name} must be an integer")
    return map_index, layer_slot, cell
