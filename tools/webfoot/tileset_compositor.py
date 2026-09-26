"""Infer a human-readable authoring atlas from proven map usage.

TILESET-COMPOSITOR-001. A bank container is 16,384 decoded bytes = 256 tiles of
8x8 pixels in *storage order*. Storage order carries no meaning: related art is
scattered through the bank, which is why a raw sheet reads as a jigsaw even after
the packed-container decode is correct (``docs/research/BUU_MAP_GRAPHICS_DIAG.md``
section 6 establishes that the sheet's jigsaw appearance is the storage order of
the art and not a format layer).

This module recovers the missing structure from evidence the ROM already
contains: every decoded map layer is a regular-BG screen-entry plane, so the
engine has already told us which tiles appear next to which, thousands of times
over. The compositor censuses that usage and lays each bank's tiles out so that
strongly related tiles sit together.

**What this is not.** It is a *view*. It invents no tile, no palette entry and no
ROM layout, and it never writes to an image. Every displayed cell resolves back
to a real source tile through the map's own char-block assembly.

**Three linked views per bank.**

``raw``
    The bank exactly as the container stores it: 16 tiles per row, storage order.
    This is the before picture and the control.
``observed``
    The distinct 32x32 screen-entry chunks that reference this bank, rendered
    through the owning map's own assembled character block by the production
    renderer. It is a *reference view and regression oracle*: its pixels must
    stay identical to the runtime-proven renderer, so it is rendered by calling
    that renderer rather than by reimplementing it.
``inferred``
    The inferred atlas: motif components of strongly related tiles, deterministically
    packed onto a tile-cell canvas with gutters between components.

**Provenance.** The census key is a source tile, because that is the ROM identity
the atlas displays. A screen entry names a *char-block ordinal*; the map's own
selector stream resolves that ordinal to a ``bank:tile`` source. So one display
cell can carry two different identities, and this module keeps both:

* :class:`DisplayIdentity` - ``(bank, tile, palette_bank, hflip, vflip)`` - the
  exact presentation one screen-entry occurrence asked for; and
* :class:`TileIdentity` - ``(bank, tile)`` - the canonical unflipped identity,
  which is what grouping, adjacency and motifs are computed on, because a flip
  is presentation and not a different tile.

**Determinism.** Nothing here reads a clock, a filesystem, a random source or a
set's iteration order. Every aggregate that reaches output is sorted by an
explicit key, every ratio is an exact integer (parts per million, never a float),
and every digest is taken over a fixed-width encoding. Same bytes in, byte-identical
manifest and pixel-identical images out.

One scope qualifier, measured rather than assumed: the ordering that reaches
output is the order of the **plane sequence the caller supplies**. Every derived
structure - components, cells, the canvas, and the adjacency and motif tables'
use - is order-invariant, but a per-tile occurrence *digest* and its quoted
samples follow the order occurrences were walked in, so reordering ``planes``
reorders them. The ROM entry point supplies a fixed order (maps by index, then
layer slots, then cells in raster order), which is what makes that path
reproducible; a caller assembling planes itself must fix its own order to get
the same digests.

**No machine learning, no image similarity.** Frequency, adjacency and layout are
the whole algorithm, and every placement states the evidence that produced it.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import hashlib
import json
import struct
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .formats import bg_tilemap as _bg
from .formats import indexed_png as _png
from .formats import map_graphics as _mg
from .formats import sprite_graphics as _sg

__all__ = [
    "TilesetCompositorError",
    "TileIdentity",
    "DisplayIdentity",
    "Occurrence",
    "ObservedChunk",
    "BankSpec",
    "PlaneInput",
    "CensusParameters",
    "InferenceParameters",
    "Census",
    "BankUsage",
    "TileUsage",
    "CensusFailure",
    "Constraint",
    "Conflict",
    "Evidence",
    "Placement",
    "Component",
    "AtlasCell",
    "InferredAtlas",
    "PackedCanvas",
    "PackedPlacement",
    "RenderedView",
    "read_bank_table",
    "census_planes",
    "census_image",
    "infer_bank",
    "pack_components",
    "atlas_document",
    "run_document",
    "render_raw_bank",
    "render_inferred_atlas",
    "observed_chunk_planes",
    "render_observed_view",
    "tile_pixels",
    "prepare_output_root",
    "write_bundle",
]


class TilesetCompositorError(ValueError):
    """Raised when a census, inference or output request cannot be honoured."""


# --- platform and policy constants -------------------------------------------

#: One tile is 8x8 pixels. The compositor's canvas is measured in these.
TILE_PIXELS = _sg.TILE_SIDE

#: The four cardinal neighbours, in a fixed order so every ranking tie-break is
#: reproducible. ``(+1, 0)`` is the neighbour one tile to the right in the
#: plane's own row-major order, ``(0, +1)`` one tile down.
CARDINAL_OFFSETS: tuple[tuple[int, int], ...] = ((1, 0), (-1, 0), (0, 1), (0, -1))

#: A bank's addressed tile capacity under the selector's 8-bit tile field.
TILES_PER_BANK = 256

#: The raw view lays a bank out 16 tiles per row, which is the shape the
#: compiled resource library's own sheets use - so a raw sheet and the artifact
#: the user already looks at are directly comparable.
RAW_COLUMNS = 16

#: The cell grid a dominant chunk and a screen-entry plane both carry.
CHUNK_SIDE = _mg.CHUNK_SIDE_TILES

#: Names for the three layer forms the census reads. They are structural, never
#: semantic: nothing here says what a tile depicts.
LAYER_KIND_DOMINANT = "dominant_chunk"
LAYER_KIND_SCREENBLOCK = "static_graphical_screenblock"
LAYER_KIND_TERRAIN = "static_graphical_terrain_field"

#: Layer classifications this census draws usage from. The remaining accepted
#: classifications (an absent placeholder, a zero-dimension grid, an
#: unclassified handler) name no screen entries, so they contribute nothing and
#: are counted as skipped with their own reason rather than silently ignored.
CENSUSED_CLASSIFICATIONS = (
    "dominant",
    "static_graphical_screenblock",
    "static_graphical_terrain_field",
)

#: The plane kinds :func:`census_planes` accepts. They are the layer *kinds* the
#: census records, not the reader's classification strings, and the two are not
#: the same vocabulary - a mismatch here silently censuses nothing.
CENSUSED_KINDS = (
    LAYER_KIND_DOMINANT,
    LAYER_KIND_SCREENBLOCK,
    LAYER_KIND_TERRAIN,
)

#: Bits of one occurrence record in the per-tile occurrence digest. Fixed width
#: so the digest is a function of the occurrence stream and nothing else.
_OCCURRENCE_STRUCT = struct.Struct("<HBBIHHH")

#: The layer-kind codes that stream contributes, so a digest distinguishes a
#: dominant chunk from a screen-entry plane without encoding a string.
_LAYER_KIND_CODES = {
    LAYER_KIND_DOMINANT: 1,
    LAYER_KIND_SCREENBLOCK: 2,
    LAYER_KIND_TERRAIN: 3,
}


# --- identities ---------------------------------------------------------------

@dataclass(frozen=True, order=True, slots=True)
class TileIdentity:
    """The canonical unflipped identity of one ROM tile: ``(bank, tile)``.

    This is the identity the atlas groups, scores and places on. A flip is a
    property of a *use*, not of the tile, so folding it into this key would
    split one tile's evidence across four keys and weaken every relationship
    the compositor is trying to measure.
    """

    bank: int
    tile: int

    def __str__(self) -> str:
        return f"{self.bank:03d}:{self.tile:03d}"

    def to_document(self) -> dict[str, object]:
        return {"bank": self.bank, "tile": self.tile}

    @property
    def packed(self) -> int:
        """``bank << 8 | tile`` - the integer the census inner loops key on."""
        return (self.bank << 8) | self.tile


@dataclass(frozen=True, order=True, slots=True)
class DisplayIdentity:
    """One screen entry's full presentation identity.

    ``palette_bank`` is decoded even though the canonical corpus is 8bpp and
    leaves bits 12..15 zero everywhere: the field is real, a 4bpp caller would
    use it, and dropping it would make this identity a claim about the corpus
    rather than a statement about the entry.
    """

    bank: int
    tile: int
    palette_bank: int
    hflip: bool
    vflip: bool

    @property
    def canonical(self) -> TileIdentity:
        return TileIdentity(self.bank, self.tile)

    def to_document(self) -> dict[str, object]:
        return {
            "bank": self.bank,
            "tile": self.tile,
            "palette_bank": self.palette_bank,
            "hflip": self.hflip,
            "vflip": self.vflip,
        }


@dataclass(frozen=True, slots=True)
class Occurrence:
    """One screen-entry occurrence of one tile, with its full provenance.

    ``raw_word`` is the 16-bit screen entry exactly as the plane stores it, so a
    reader can re-derive the ordinal, both flip bits and the palette bank
    without trusting this module's decode. ``chunk_index``/``chunk_address``
    name the container the entry came from for every layer form that has one
    (a dominant chunk cell, a screen-entry plane, a terrain-field cell), which
    is what makes an atlas cell traceable to *where* the map used it.
    """

    map_index: int
    layer_slot: int
    layer_kind: str
    layer_address: int
    plane_x: int
    plane_y: int
    chunk_index: int | None
    chunk_address: int | None
    raw_word: int
    ordinal: int
    display: DisplayIdentity

    def to_document(self) -> dict[str, object]:
        return {
            "map": f"map:{self.map_index:04d}",
            "map_index": self.map_index,
            "layer_slot": self.layer_slot,
            "layer_kind": self.layer_kind,
            "layer_address": f"{self.layer_address:#010x}",
            "plane_x": self.plane_x,
            "plane_y": self.plane_y,
            "chunk_index": self.chunk_index,
            "chunk_address": (
                None if self.chunk_address is None else f"{self.chunk_address:#010x}"
            ),
            "raw_word": f"{self.raw_word:#06x}",
            "ordinal": self.ordinal,
            "display": self.display.to_document(),
        }

    def digest_bytes(self) -> bytes:
        """The fixed-width encoding the per-tile occurrence digest consumes."""
        return _OCCURRENCE_STRUCT.pack(
            self.map_index,
            self.layer_slot,
            _LAYER_KIND_CODES[self.layer_kind],
            self.chunk_address or 0,
            self.plane_x,
            self.plane_y,
            self.raw_word,
        )


@dataclass(frozen=True, order=True, slots=True)
class ObservedChunk:
    """One 32x32 screen-entry plane observed using a bank, and where it lives."""

    map_index: int
    layer_slot: int
    layer_kind: str
    layer_address: int
    chunk_index: int
    chunk_address: int


# --- parameters ---------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class CensusParameters:
    """Everything the census' output depends on besides the ROM bytes."""

    #: How many exact occurrences are quoted per tile in the manifest. The
    #: digest over the *complete* occurrence stream is recorded regardless, so a
    #: sample is provably drawn from a complete list rather than replacing it.
    occurrence_samples: int = 4

    def to_document(self) -> dict[str, object]:
        return {"occurrence_samples": self.occurrence_samples}


@dataclass(frozen=True, slots=True)
class InferenceParameters:
    """The thresholds that turn usage into a layout.

    Every one is a stated policy, not a measurement, and each is recorded in the
    manifest so a reader can reproduce a sheet from the census alone.
    """

    #: A directional relationship needs at least this many observations.
    min_adjacency_support: int = 2
    #: ...and must hold for at least this fraction of the source tile's
    #: neighbour observations in that direction, in parts per million. This is
    #: what stops a common filler tile - which borders everything and so
    #: predicts nothing - from dominating the layout.
    min_adjacency_confidence_ppm: int = 400_000
    #: A repeated 2x2 motif needs this many observations to count as evidence.
    min_motif_2x2_support: int = 3
    #: A repeated 3x3 motif needs this many.
    min_motif_3x3_support: int = 3
    #: The canvas starts this many tiles wide and widens only to fit a component
    #: that does not fit. The user's stated preference: a sensible fixed
    #: starting width, expanded deterministically when needed.
    pack_start_width: int = 16
    #: Blank tiles between two components, on both axes.
    pack_gutter: int = 1
    #: How many times one ROM tile may be *presented* on the sheet. A tile that
    #: takes part in several strong arrangements legitimately earns more than
    #: one instance, but a highly repetitive texture earns hundreds of equally
    #: valid ones and a sheet of those is noise, not an atlas. Instances past
    #: this budget are counted, never silently created.
    max_instances_per_tile: int = 3
    #: How many conflicts are enumerated in the manifest. Every conflict is
    #: counted and digested regardless, so the cap bounds the document without
    #: weakening the claim that nothing was dropped.
    max_recorded_conflicts: int = 64

    def to_document(self) -> dict[str, object]:
        return {
            "min_adjacency_support": self.min_adjacency_support,
            "min_adjacency_confidence_ppm": self.min_adjacency_confidence_ppm,
            "min_motif_2x2_support": self.min_motif_2x2_support,
            "min_motif_3x3_support": self.min_motif_3x3_support,
            "pack_start_width": self.pack_start_width,
            "pack_gutter": self.pack_gutter,
            "max_instances_per_tile": self.max_instances_per_tile,
            "max_recorded_conflicts": self.max_recorded_conflicts,
        }


# --- census aggregates --------------------------------------------------------

@dataclass(slots=True)
class TileUsage:
    """Everything the census learned about one source tile."""

    occurrences: int = 0
    display: Counter = field(default_factory=Counter)
    maps: set = field(default_factory=set)
    layer_kinds: Counter = field(default_factory=Counter)
    chunks: Counter = field(default_factory=Counter)
    raw_words: Counter = field(default_factory=Counter)
    samples: list = field(default_factory=list)
    digest: object = field(default_factory=hashlib.sha256)

    def to_document(self, tile: TileIdentity, samples: int) -> dict[str, object]:
        return {
            "tile": tile.tile,
            "bank": tile.bank,
            "occurrence_count": self.occurrences,
            "occurrences_sha256": self.digest.hexdigest(),
            "maps": sorted(self.maps),
            "layer_kinds": {key: self.layer_kinds[key] for key in sorted(self.layer_kinds)},
            "chunks": {
                f"{address:#010x}": self.chunks[address]
                for address in sorted(self.chunks)
            },
            "raw_words": {
                f"{word:#06x}": self.raw_words[word] for word in sorted(self.raw_words)
            },
            "display_identities": [
                dict(identity.to_document(), count=count)
                for identity, count in sorted(
                    self.display.items(),
                    key=lambda item: (
                        item[0].palette_bank,
                        item[0].hflip,
                        item[0].vflip,
                    ),
                )
            ],
            "occurrence_samples": [
                occurrence.to_document() for occurrence in self.samples[:samples]
            ],
        }


@dataclass(slots=True)
class BankUsage:
    """Everything the census learned about one bank."""

    bank: int
    container_address: int
    declared_size: int
    tile_count: int
    tiles: dict = field(default_factory=dict)
    observed_chunks: dict = field(default_factory=dict)
    occurrences: int = 0

    def tile_usage(self, tile: int) -> TileUsage:
        usage = self.tiles.get(tile)
        if usage is None:
            usage = TileUsage()
            self.tiles[tile] = usage
        return usage

    @property
    def used_tiles(self) -> tuple[int, ...]:
        return tuple(sorted(self.tiles))

    def to_document(self, *, samples: int) -> dict[str, object]:
        return {
            "bank": self.bank,
            "tileset": self.bank + 1,
            "container_address": f"{self.container_address:#010x}",
            "declared_size": self.declared_size,
            "tile_count": self.tile_count,
            "occurrence_total": self.occurrences,
            "tiles_used": len(self.tiles),
            "observed_chunk_count": len(self.observed_chunks),
            "tiles": [
                self.tiles[tile].to_document(TileIdentity(self.bank, tile), samples)
                for tile in self.used_tiles
            ],
        }


@dataclass(frozen=True, slots=True)
class CensusFailure:
    """A map or layer the census could not read, recorded rather than dropped."""

    map_index: int
    layer_slot: int | None
    reason: str

    def to_document(self) -> dict[str, object]:
        return {
            "map": f"map:{self.map_index:04d}",
            "map_index": self.map_index,
            "layer_slot": self.layer_slot,
            "reason": self.reason,
        }


@dataclass(slots=True)
class Census:
    """A whole-corpus census, partitioned by bank.

    The adjacency and motif tables are keyed by the bank of the **left/top
    anchor** tile of the observation, which is what lets one global pass serve
    every bank's sheet without a second pass per bank. The user's stated design:
    one census over all 452 maps, indexed by bank, each bank's sheet drawn only
    from observations whose tiles are in that bank.
    """

    profile_id: str
    map_count: int
    bank_table_address: int
    parameters: CensusParameters
    banks: dict
    adjacency: dict
    motifs_2x2: dict
    motifs_3x3: dict
    failures: tuple
    occurrences: dict
    skipped: Counter
    cells_censused: int = 0
    maps_censused: int = 0

    def bank_usage(self, bank: int) -> BankUsage:
        try:
            return self.banks[bank]
        except KeyError:
            raise TilesetCompositorError(
                f"bank {bank} is outside this census' {len(self.banks)} banks"
            ) from None

    def to_document(self) -> dict[str, object]:
        return {
            "profile": self.profile_id,
            "maps": self.map_count,
            "maps_censused": self.maps_censused,
            "cells_censused": self.cells_censused,
            "bank_table_address": f"{self.bank_table_address:#010x}",
            "banks": len(self.banks),
            "skipped": {key: self.skipped[key] for key in sorted(self.skipped)},
            "failures": [failure.to_document() for failure in self.failures],
            "parameters": self.parameters.to_document(),
        }


# --- reading ------------------------------------------------------------------

def read_bank_table(reader: _mg.MapGraphicsReader) -> tuple[int, tuple[int, ...]]:
    """The one bank table every map root names, and its container addresses.

    The table address is ``root + 0x4C``; measured over the canonical image all
    452 roots name the same table, and this refuses a corpus where they do not
    rather than silently censusing one map's banks under another map's usage.
    """
    entries = _mg.read_map_entries(reader)
    if not entries:
        raise TilesetCompositorError("the image declares no map entries")
    addresses = {
        reader.u32(entry.root_address + _mg.ROOT_BANK_TABLE_OFFSET)
        for entry in entries
    }
    if len(addresses) != 1:
        raise TilesetCompositorError(
            "map roots disagree about the bank table: "
            + ", ".join(f"{address:#010x}" for address in sorted(addresses))
        )
    table = addresses.pop()
    containers = tuple(
        reader.u32(table + index * 4) for index in range(_mg.BANK_COUNT)
    )
    return table, containers


@dataclass(frozen=True, slots=True)
class BankSpec:
    """One bank as the census needs it: identity, extent, no payload.

    The census never needs tile pixels, only how many tiles a bank declares, so
    it takes the extent rather than a decoded payload. That is what lets the
    whole census run against a synthetic bank set with no ROM at all.
    """

    bank: int
    container_address: int
    declared_size: int
    tile_count: int


@dataclass(frozen=True, slots=True)
class PlaneInput:
    """One screen-entry plane, reduced to the one shape the census walks.

    A caller supplies the plane's own words plus the two facts that only the
    owning map knows: its selector stream (which resolves a char-block ordinal
    to a ``bank:tile`` source) and the ordinals an animated-tile record
    overlays. Nothing else about a map reaches the census, which is why
    :func:`census_planes` is a pure function over this record.
    """

    map_index: int
    slot: int
    kind: str
    address: int
    width_tiles: int
    height_tiles: int
    words: tuple
    chunk_grid: tuple | None
    chunk_addresses: tuple
    selectors: tuple
    animated_tiles: frozenset


def _decode_layer_plane(
    reader: _mg.MapGraphicsReader,
    layer: _mg.LayerRecord,
    *,
    map_index: int,
    selectors: tuple,
    animated_tiles: frozenset,
) -> PlaneInput | None:
    """Reduce one layer record to its screen-entry plane, or ``None``."""
    if layer.classification == "dominant":
        words = _mg.stitch_dominant_entries(reader, layer)
        return PlaneInput(
            map_index=map_index,
            slot=layer.slot,
            kind=LAYER_KIND_DOMINANT,
            address=layer.address,
            width_tiles=layer.chunk_tiles_x,
            height_tiles=layer.chunk_tiles_y,
            words=words,
            chunk_grid=(layer.chunk_x, layer.chunk_y),
            chunk_addresses=tuple(layer.chunk_addresses),
            selectors=selectors,
            animated_tiles=animated_tiles,
        )
    if layer.classification == "static_graphical_screenblock":
        words = _mg.read_screenblock_entries(reader, layer.address)
        offset = _mg.screenblock_container_offset(reader.u32(layer.address))
        container = reader.u32(layer.address + offset)
        return PlaneInput(
            map_index=map_index,
            slot=layer.slot,
            kind=LAYER_KIND_SCREENBLOCK,
            address=layer.address,
            width_tiles=CHUNK_SIDE,
            height_tiles=CHUNK_SIDE,
            words=words,
            chunk_grid=None,
            chunk_addresses=(container,),
            selectors=selectors,
            animated_tiles=animated_tiles,
        )
    if layer.classification == "static_graphical_terrain_field":
        containers = _mg.read_terrain_field_cells(reader, layer.address)
        width, height, plane = _mg.stitch_terrain_field_plane(
            containers,
            layer.terrain_grid_x,
            layer.terrain_grid_y,
        )
        mask = _mg.TERRAIN_FIELD_TILE_ORDINAL_MASK
        return PlaneInput(
            map_index=map_index,
            slot=layer.slot,
            kind=LAYER_KIND_TERRAIN,
            address=layer.address,
            width_tiles=width,
            height_tiles=height,
            words=tuple(value & mask for value in plane),
            chunk_grid=(layer.terrain_grid_x, layer.terrain_grid_y),
            chunk_addresses=tuple(
                _mg.read_terrain_field_containers(reader, layer.address)
            ),
            selectors=selectors,
            animated_tiles=animated_tiles,
        )
    return None


def _chunk_for(plane: PlaneInput, x: int, y: int) -> tuple[int, int | None]:
    """``(chunk_index, chunk_address)`` for a plane cell, or a null address.

    A dominant layer's window may hold a null pointer, which the engine's own
    occupancy test reads as an unoccupied cell and which
    :func:`map_graphics.stitch_dominant_entries` fills with a blank plane. It is
    a real state, not a chunk at address zero, so it names no container here.
    """
    if plane.kind in (LAYER_KIND_DOMINANT, LAYER_KIND_TERRAIN):
        grid_x = plane.chunk_grid[0]
        index = (y // CHUNK_SIDE) * grid_x + (x // CHUNK_SIDE)
        address = plane.chunk_addresses[index]
        return index, (address if address else None)
    address = plane.chunk_addresses[0]
    return 0, (address if address else None)


def census_planes(
    planes: Sequence[PlaneInput],
    banks: Sequence[BankSpec],
    *,
    parameters: CensusParameters | None = None,
    profile_id: str = "synthetic",
    map_count: int | None = None,
    maps_censused: int | None = None,
    bank_table_address: int = 0,
    retain_occurrences_for: Iterable[int] | None = None,
    failures: Sequence[CensusFailure] = (),
    skipped: Mapping[str, int] | None = None,
) -> Census:
    """Census a corpus of already-decoded screen-entry planes.

    This is the whole census as a pure function: no reader, no ROM, no
    filesystem. :func:`census_image` decodes the map/graphics records into
    :class:`PlaneInput` records and calls this, and a test can build the planes
    it wants to reason about directly.

    ``planes`` is consumed **in the order given**. The aggregate tables this
    builds do not depend on that order, but a tile's `occurrences_sha256` and
    its quoted samples do, so a caller that wants two runs to agree must supply
    its planes in a fixed order. :func:`census_image` does.

    Cells that cannot be attributed are never silently dropped: an ordinal past
    the selector stream, an ordinal an animated-tile record overlays, and a tile
    outside its bank's declared extent each land in :attr:`Census.skipped` under
    their own name.
    """
    parameters = parameters or CensusParameters()
    retained = (
        None
        if retain_occurrences_for is None
        else {int(bank) for bank in retain_occurrences_for}
    )

    usage: dict[int, BankUsage] = {}
    for spec in banks:
        if spec.declared_size % _mg.TILE_BYTES:
            raise TilesetCompositorError(
                f"bank {spec.bank} at {spec.container_address:#010x} declares "
                f"{spec.declared_size} bytes, not a whole number of tiles"
            )
        if spec.tile_count != spec.declared_size // _mg.TILE_BYTES:
            raise TilesetCompositorError(
                f"bank {spec.bank} states {spec.tile_count} tiles for "
                f"{spec.declared_size} bytes"
            )
        usage[spec.bank] = BankUsage(
            bank=spec.bank,
            container_address=spec.container_address,
            declared_size=spec.declared_size,
            tile_count=spec.tile_count,
        )

    adjacency: dict = {}
    motifs_2x2: dict = {}
    motifs_3x3: dict = {}
    occurrences: dict = {} if retained is not None else {}
    counters: Counter = Counter(skipped or {})
    cells = 0

    for plane in planes:
        if plane.kind not in CENSUSED_KINDS:
            counters[f"layer:{plane.kind}"] += 1
            continue
        if not plane.width_tiles or not plane.height_tiles:
            counters["layer:empty"] += 1
            continue
        cells += _census_plane(
            plane=plane,
            banks=usage,
            adjacency=adjacency,
            motifs_2x2=motifs_2x2,
            motifs_3x3=motifs_3x3,
            occurrences=occurrences,
            retained=retained,
            skipped=counters,
            samples=parameters.occurrence_samples,
        )

    return Census(
        profile_id=profile_id,
        map_count=map_count if map_count is not None else len(
            {plane.map_index for plane in planes}
        ),
        bank_table_address=bank_table_address,
        parameters=parameters,
        banks=usage,
        adjacency=adjacency,
        motifs_2x2=motifs_2x2,
        motifs_3x3=motifs_3x3,
        failures=tuple(failures),
        occurrences=occurrences,
        skipped=counters,
        cells_censused=cells,
        maps_censused=(
            maps_censused
            if maps_censused is not None
            else len({plane.map_index for plane in planes})
        ),
    )


def census_image(
    reader: _mg.MapGraphicsReader,
    *,
    parameters: CensusParameters | None = None,
    maps: Iterable[int] | None = None,
    retain_occurrences_for: Iterable[int] | None = None,
    strict: bool = False,
    bank_table: tuple[int, tuple[int, ...]] | None = None,
) -> Census:
    """Census every screen-entry occurrence that resolves to a ROM bank tile.

    One pass over every requested map's every layer. For each cell the plane
    stores, the entry's char-block ordinal is resolved through *that map's own*
    selector stream to a ``bank:tile`` source; the occurrence is then counted
    into its bank's usage, into the directional adjacency table and into the
    repeated-motif counts.

    This function is the ROM walk; the census itself is
    :func:`census_planes`, so the aggregate rules have one owner and a synthetic
    corpus can exercise them without an image.

    ``retain_occurrences_for`` keeps the exact :class:`Occurrence` records for
    the named banks, which is what a full per-occurrence provenance dump needs;
    the aggregate digest over the same stream is always computed, so a run that
    does not retain them can still prove the sample came from a complete list.
    """
    if bank_table is None:
        bank_table = read_bank_table(reader)
    table_address, containers = bank_table

    banks = []
    for index, container_address in enumerate(containers):
        container = reader.container(container_address)
        if container.declared_size % _mg.TILE_BYTES:
            raise TilesetCompositorError(
                f"bank {index} at {container_address:#010x} declares "
                f"{container.declared_size} bytes, not a whole number of tiles"
            )
        banks.append(
            BankSpec(
                bank=index,
                container_address=container_address,
                declared_size=container.declared_size,
                tile_count=container.declared_size // _mg.TILE_BYTES,
            )
        )

    wanted = None if maps is None else {int(index) for index in maps}
    entries = _mg.read_map_entries(reader)
    planes: list[PlaneInput] = []
    failures: list[CensusFailure] = []
    skipped: Counter = Counter()

    for entry in entries:
        map_index = entry.index
        if wanted is not None and map_index not in wanted:
            continue
        root = entry.root_address
        try:
            selectors = _mg.decode_selector_stream(reader, root).selectors
            animated = _mg.read_animated_tiles(reader, root)
        except (_mg.MapGraphicsError, ValueError) as exc:
            failures.append(CensusFailure(map_index, None, str(exc)))
            if strict:
                raise TilesetCompositorError(
                    f"map:{map_index:04d} could not be censused: {exc}"
                ) from exc
            continue

        animated_tiles = frozenset(
            ordinal
            for source in animated
            for ordinal in range(
                source.destination_tile,
                source.destination_tile + source.tile_count,
            )
        )

        try:
            layers = _mg.read_layers(reader, root)
        except (_mg.MapGraphicsError, ValueError) as exc:
            failures.append(CensusFailure(map_index, None, str(exc)))
            if strict:
                raise TilesetCompositorError(
                    f"map:{map_index:04d} layers could not be read: {exc}"
                ) from exc
            continue

        for layer in layers:
            if layer.classification not in CENSUSED_CLASSIFICATIONS:
                skipped[f"layer:{layer.classification}"] += 1
                continue
            try:
                plane = _decode_layer_plane(
                    reader,
                    layer,
                    map_index=map_index,
                    selectors=selectors,
                    animated_tiles=animated_tiles,
                )
            except (_mg.MapGraphicsError, ValueError) as exc:
                failures.append(CensusFailure(map_index, layer.slot, str(exc)))
                if strict:
                    raise TilesetCompositorError(
                        f"map:{map_index:04d} slot {layer.slot} could not be read: {exc}"
                    ) from exc
                continue
            if plane is None:
                skipped["layer:empty"] += 1
                continue
            planes.append(plane)

    return census_planes(
        planes,
        banks,
        parameters=parameters,
        profile_id=reader.profile.id,
        map_count=len(entries),
        maps_censused=sum(
            1 for entry in entries if wanted is None or entry.index in wanted
        ),
        bank_table_address=table_address,
        retain_occurrences_for=retain_occurrences_for,
        failures=failures,
        skipped=skipped,
    )


def _census_plane(
    *,
    plane: PlaneInput,
    banks: dict,
    adjacency: dict,
    motifs_2x2: dict,
    motifs_3x3: dict,
    occurrences: dict,
    retained: set | None,
    skipped: Counter,
    samples: int,
) -> int:
    """Census one layer plane. Returns the number of cells examined."""
    width = plane.width_tiles
    height = plane.height_tiles
    words = plane.words
    selectors = plane.selectors
    animated_tiles = plane.animated_tiles
    count = width * height
    if len(words) != count:
        raise TilesetCompositorError(
            f"layer at {plane.address:#010x} states a {width}x{height} plane but "
            f"holds {len(words)} entries"
        )

    # Resolve each cell once. ``ids[i]`` is the packed canonical identity, or
    # -1 for a cell that contributes no bank usage.
    ids: list[int] = [-1] * count
    for index in range(count):
        word = words[index]
        ordinal = word & _mg.TILE_ENTRY_ORDINAL_MASK
        if ordinal >= len(selectors):
            skipped["ordinal_past_selector_stream"] += 1
            continue
        if ordinal in animated_tiles:
            skipped["ordinal_overlaid_by_animation"] += 1
            continue
        selector = selectors[ordinal]
        bank = selector >> 8
        tile = selector & 0xFF
        bank_usage = banks.get(bank)
        if bank_usage is None or tile >= bank_usage.tile_count:
            skipped["tile_outside_bank_extent"] += 1
            continue
        ids[index] = (bank << 8) | tile

        x, y = index % width, index // width
        chunk_index, chunk_address = _chunk_for(plane, x, y)
        display = DisplayIdentity(
            bank=bank,
            tile=tile,
            palette_bank=(word >> _bg.TILE_ENTRY_PALETTE_BANK_SHIFT)
            & _bg.TILE_ENTRY_PALETTE_BANK_MASK,
            hflip=bool(word & _bg.TILE_ENTRY_HORIZONTAL_FLIP),
            vflip=bool(word & _bg.TILE_ENTRY_VERTICAL_FLIP),
        )
        occurrence = Occurrence(
            map_index=plane.map_index,
            layer_slot=plane.slot,
            layer_kind=plane.kind,
            layer_address=plane.address,
            plane_x=x,
            plane_y=y,
            chunk_index=chunk_index,
            chunk_address=chunk_address,
            raw_word=word,
            ordinal=ordinal,
            display=display,
        )
        tile_usage = bank_usage.tile_usage(tile)
        tile_usage.occurrences += 1
        tile_usage.display[display] += 1
        tile_usage.maps.add(plane.map_index)
        tile_usage.layer_kinds[plane.kind] += 1
        if chunk_address is not None:
            tile_usage.chunks[chunk_address] += 1
        tile_usage.raw_words[word] += 1
        tile_usage.digest.update(occurrence.digest_bytes())
        if len(tile_usage.samples) < samples:
            tile_usage.samples.append(occurrence)
        bank_usage.occurrences += 1
        if chunk_address is not None:
            key = (plane.map_index, chunk_address)
            if key not in bank_usage.observed_chunks:
                bank_usage.observed_chunks[key] = ObservedChunk(
                    map_index=plane.map_index,
                    layer_slot=plane.slot,
                    layer_kind=plane.kind,
                    layer_address=plane.address,
                    chunk_index=chunk_index if chunk_index is not None else 0,
                    chunk_address=chunk_address,
                )
        if retained is not None and bank in retained:
            occurrences.setdefault(bank, []).append(occurrence)

    _census_adjacency(
        ids=ids,
        width=width,
        height=height,
        adjacency=adjacency,
    )
    _census_motifs(
        ids=ids,
        width=width,
        height=height,
        motifs_2x2=motifs_2x2,
        motifs_3x3=motifs_3x3,
    )
    return count


def _census_adjacency(
    *, ids: list, width: int, height: int, adjacency: dict
) -> None:
    """Count directional neighbour relationships inside one plane."""
    for index, source in enumerate(ids):
        if source < 0:
            continue
        x, y = index % width, index // width
        for direction, (dx, dy) in enumerate(CARDINAL_OFFSETS):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            target = ids[ny * width + nx]
            key = (source, direction)
            bucket = adjacency.get(key)
            if bucket is None:
                bucket = Counter()
                adjacency[key] = bucket
            bucket[target] += 1


def _census_motifs(
    *, ids: list, width: int, height: int, motifs_2x2: dict, motifs_3x3: dict
) -> None:
    """Count repeated 2x2 and 3x3 motifs, keyed by their anchor tile's bank.

    A motif with an unattributable cell is not counted at all: a motif is a
    claim about a whole neighbourhood, and a partially-known neighbourhood is
    not evidence for the part that is known.
    """
    for y in range(height - 1):
        row = y * width
        for x in range(width - 1):
            a = ids[row + x]
            b = ids[row + x + 1]
            c = ids[row + width + x]
            d = ids[row + width + x + 1]
            if a < 0 or b < 0 or c < 0 or d < 0:
                continue
            key = (a << 48) | (b << 32) | (c << 16) | d
            bucket = motifs_2x2.get(a >> 8)
            if bucket is None:
                bucket = Counter()
                motifs_2x2[a >> 8] = bucket
            bucket[key] += 1

    for y in range(height - 2):
        row = y * width
        for x in range(width - 2):
            cells = (
                ids[row + x], ids[row + x + 1], ids[row + x + 2],
                ids[row + width + x], ids[row + width + x + 1], ids[row + width + x + 2],
                ids[row + 2 * width + x], ids[row + 2 * width + x + 1],
                ids[row + 2 * width + x + 2],
            )
            if any(cell < 0 for cell in cells):
                continue
            key = 0
            for cell in cells:
                key = (key << 16) | cell
            bucket = motifs_3x3.get(cells[0] >> 8)
            if bucket is None:
                bucket = Counter()
                motifs_3x3[cells[0] >> 8] = bucket
            bucket[key] += 1


# --- constraints --------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Constraint:
    """One accepted "B sits immediately this way from A" relationship.

    ``out_degree`` is every neighbour observation of A in that direction -
    **including the cells the census could not attribute** - so the confidence
    is never inflated by discarding negative evidence. ``support`` is the count
    of the specific pair. The two motif fields are the number of *repeated*
    2x2/3x3 motifs that place the pair at that same relative offset.
    """

    source: TileIdentity
    direction: tuple[int, int]
    target: TileIdentity
    support: int
    out_degree: int
    motif_support_2x2: int
    motif_support_3x3: int

    @property
    def confidence_ppm(self) -> int:
        """``support / out_degree`` in exact integer parts per million."""
        if self.out_degree <= 0:
            return 0
        return self.support * 1_000_000 // self.out_degree

    @property
    def motif_support(self) -> int:
        return self.motif_support_2x2 + self.motif_support_3x3

    @property
    def rank(self) -> tuple:
        """The deterministic ranking key: motifs first, then count, then id."""
        return (-self.motif_support, -self.support, self.target.tile)

    def to_document(self) -> dict[str, object]:
        return {
            "source": self.source.to_document(),
            "direction": {"dx": self.direction[0], "dy": self.direction[1]},
            "target": self.target.to_document(),
            "support": self.support,
            "out_degree": self.out_degree,
            "confidence_ppm": self.confidence_ppm,
            "motif_support_2x2": self.motif_support_2x2,
            "motif_support_3x3": self.motif_support_3x3,
        }


@dataclass(frozen=True, slots=True)
class Conflict:
    """A relationship the compositor deliberately did **not** force.

    Nothing here is discarded silently: every conflict is named, carries its
    counts, and reaches the manifest, so an ambiguous corpus reads as ambiguous
    instead of as a confident wrong layout.
    """

    kind: str
    detail: str
    source: TileIdentity | None = None
    direction: tuple[int, int] | None = None
    target: TileIdentity | None = None
    occupant: TileIdentity | None = None
    support: int = 0
    rival_support: int = 0

    def to_document(self) -> dict[str, object]:
        document: dict[str, object] = {"kind": self.kind, "detail": self.detail}
        if self.source is not None:
            document["source"] = self.source.to_document()
        if self.direction is not None:
            document["direction"] = {
                "dx": self.direction[0],
                "dy": self.direction[1],
            }
        if self.target is not None:
            document["target"] = self.target.to_document()
        if self.occupant is not None:
            document["occupant"] = self.occupant.to_document()
        if self.support or self.rival_support:
            document["support"] = self.support
            document["rival_support"] = self.rival_support
        return document


@dataclass(frozen=True, slots=True)
class Evidence:
    """Why one tile sits where it sits. Every placement carries exactly one.

    Three kinds exist and they are never blended: a ``motif`` placement rests on
    a repeated arrangement, an ``adjacency`` placement on a single directional
    relationship, and ``no_constraint`` states plainly that the census offered
    nothing and the tile was kept rather than placed on a guess.
    """

    kind: str
    detail: str
    motif_size: int | None = None
    motif_support: int = 0
    constraint: Constraint | None = None

    def to_document(self) -> dict[str, object]:
        document: dict[str, object] = {"kind": self.kind, "detail": self.detail}
        if self.motif_size is not None:
            document["motif_size"] = self.motif_size
            document["motif_support"] = self.motif_support
        if self.constraint is not None:
            document["constraint"] = self.constraint.to_document()
        return document


@dataclass(frozen=True, slots=True)
class Placement:
    """One tile's position inside its component, and what put it there."""

    tile: TileIdentity
    x: int
    y: int
    role: str
    evidence: Evidence

    def to_document(self) -> dict[str, object]:
        return {
            "tile": self.tile.to_document(),
            "x": self.x,
            "y": self.y,
            "role": self.role,
            "evidence": self.evidence.to_document(),
        }


@dataclass(frozen=True, slots=True)
class Component:
    """A connected group of strongly related tiles, with its relative layout."""

    index: int
    root: TileIdentity
    placements: tuple
    width: int
    height: int
    support: int

    @property
    def tile_count(self) -> int:
        return len(self.placements)

    @property
    def area(self) -> int:
        return self.width * self.height

    def to_document(self) -> dict[str, object]:
        return {
            "index": self.index,
            "root": self.root.to_document(),
            "width": self.width,
            "height": self.height,
            "tile_count": self.tile_count,
            "support": self.support,
            "placements": [placement.to_document() for placement in self.placements],
        }


# --- inference ----------------------------------------------------------------

def _motif_pair_support(census: Census, bank: int, parameters: InferenceParameters):
    """Sum repeated motif support per ``(source, direction, target)`` triple.

    A motif is indexed under the bank of its **top-left** cell, so this measures
    the windows this bank anchors. The rule is stated in the manifest rather
    than left implicit: the adjacency table, which is the primary signal, is
    exact for every source tile, and only this booster is anchor-scoped.
    """
    pairs_2x2: Counter = Counter()
    pairs_3x3: Counter = Counter()

    for key, count in census.motifs_2x2.get(bank, {}).items():
        if count < parameters.min_motif_2x2_support:
            continue
        cells = {
            (0, 0): (key >> 48) & 0xFFFF,
            (1, 0): (key >> 32) & 0xFFFF,
            (0, 1): (key >> 16) & 0xFFFF,
            (1, 1): key & 0xFFFF,
        }
        for (x, y), source in cells.items():
            for direction, (dx, dy) in enumerate(CARDINAL_OFFSETS):
                target = cells.get((x + dx, y + dy))
                if target is None:
                    continue
                pairs_2x2[(source, direction, target)] += count

    for key, count in census.motifs_3x3.get(bank, {}).items():
        if count < parameters.min_motif_3x3_support:
            continue
        cells = {}
        for position in range(9):
            shift = 16 * (8 - position)
            cells[(position % 3, position // 3)] = (key >> shift) & 0xFFFF
        for (x, y), source in cells.items():
            for direction, (dx, dy) in enumerate(CARDINAL_OFFSETS):
                target = cells.get((x + dx, y + dy))
                if target is None:
                    continue
                pairs_3x3[(source, direction, target)] += count

    return pairs_2x2, pairs_3x3


def _select_constraints(
    census: Census, bank: int, parameters: InferenceParameters
) -> tuple[tuple[Constraint, ...], tuple[Conflict, ...]]:
    """Pick at most one successor per ``(tile, direction)``, refusing ties.

    A tie is a genuine ambiguity - two different tiles follow this one equally
    often - and the compositor records it instead of picking one. That single
    rule is what keeps a conflict from ever being forced: the accepted set is
    per-direction unique by construction, and everything the rule declined to
    choose is named in the conflicts.
    """
    usage = census.bank_usage(bank)
    pairs_2x2, pairs_3x3 = _motif_pair_support(census, bank, parameters)
    accepted: list[Constraint] = []
    conflicts: list[Conflict] = []

    for tile in usage.used_tiles:
        packed = (bank << 8) | tile
        source = TileIdentity(bank, tile)
        for direction, (dx, dy) in enumerate(CARDINAL_OFFSETS):
            bucket = census.adjacency.get((packed, direction))
            if not bucket:
                continue
            out_degree = sum(bucket.values())
            ranked = []
            for target_packed, count in bucket.items():
                if target_packed < 0 or (target_packed >> 8) != bank:
                    continue
                ranked.append(
                    (
                        pairs_2x2.get((packed, direction, target_packed), 0),
                        pairs_3x3.get((packed, direction, target_packed), 0),
                        count,
                        target_packed,
                    )
                )
            if not ranked:
                continue
            ranked.sort(key=lambda row: (-(row[0] + row[1]), -row[2], row[3]))
            best = ranked[0]
            if len(ranked) > 1:
                runner_up = ranked[1]
                if (runner_up[0], runner_up[1], runner_up[2]) == (
                    best[0],
                    best[1],
                    best[2],
                ):
                    conflicts.append(
                        Conflict(
                            kind="ambiguous_successor",
                            detail=(
                                "two tiles follow this one equally often in this "
                                "direction with equal motif support, so neither is "
                                "asserted"
                            ),
                            source=source,
                            direction=(dx, dy),
                            target=TileIdentity(bank, best[3] & 0xFF),
                            occupant=TileIdentity(bank, runner_up[3] & 0xFF),
                            support=best[2],
                            rival_support=runner_up[2],
                        )
                    )
                    continue

            motif_2x2, motif_3x3, count, target_packed = best
            target = TileIdentity(bank, target_packed & 0xFF)
            constraint = Constraint(
                source=source,
                direction=(dx, dy),
                target=target,
                support=count,
                out_degree=out_degree,
                motif_support_2x2=motif_2x2,
                motif_support_3x3=motif_3x3,
            )
            # The confidence floor is a floor for every accepted relationship.
            # Motif support raises a pair's *rank* - so a repeated arrangement
            # beats a merely frequent one - but it cannot admit a relationship
            # the confidence floor refused. Otherwise a filler tile that borders
            # eight tiles equally would still earn a successor from whichever
            # arrangement happened to repeat, which is precisely the dominance
            # the ticket asks the confidence term to prevent.
            if (
                count >= parameters.min_adjacency_support
                and constraint.confidence_ppm >= parameters.min_adjacency_confidence_ppm
            ):
                accepted.append(constraint)

    accepted.sort(
        key=lambda item: (
            item.source.tile,
            DIRECTIONS_INDEX[item.direction],
            item.target.tile,
        )
    )
    return tuple(accepted), tuple(conflicts)


#: Direction -> its index in :data:`CARDINAL_OFFSETS`, for stable sorting.
DIRECTIONS_INDEX = {offset: index for index, offset in enumerate(CARDINAL_OFFSETS)}


def _decode_motif(key: int, size: int) -> dict:
    """Decode a packed motif key into ``{(x, y): packed tile id}``."""
    cells = {}
    total = size * size
    for position in range(total):
        shift = 16 * (total - 1 - position)
        cells[(position % size, position // size)] = (key >> shift) & 0xFFFF
    return cells


def _repeated_motifs(
    census: Census, bank: int, parameters: InferenceParameters
) -> list:
    """Repeated 2x2 and 3x3 motifs this bank anchors, strongest first.

    A motif whose cells are **all the same tile** is dropped from layout: it
    says the tile tiles, which is true of nearly every ground tile and is no
    evidence at all for where anything belongs. It is still counted - the
    manifest reports how much self-tiling each tile showed - but it cannot
    arrange a sheet.

    The sort key is ``(-support, -size, key)``, so the strongest and largest
    evidence merges first and the result never depends on dict order.
    """
    found = []
    for size, minimum, table in (
        (2, parameters.min_motif_2x2_support, census.motifs_2x2),
        (3, parameters.min_motif_3x3_support, census.motifs_3x3),
    ):
        for key, count in table.get(bank, {}).items():
            if count < minimum:
                continue
            cells = _decode_motif(key, size)
            if len(set(cells.values())) < 2:
                continue
            found.append((count, size, key, cells))
    found.sort(key=lambda row: (-row[0], -row[1], row[2]))
    return found


def _build_components(
    census: Census,
    bank: int,
    parameters: InferenceParameters,
    constraints: tuple,
) -> tuple:
    """Grow motif components from repeated motifs, then attach loose tiles.

    The repeated motif is the strongest structure the corpus offers: it is an
    exact arrangement observed at least ``min_motif_*_support`` times, with no
    ranking or threshold judgement inside it. Components are therefore grown by
    merging motifs that agree, which is what produces real 2D blocks rather than
    chains.

    A motif that fits an existing component in exactly one place is merged; one
    that fits nowhere starts a component; one that fits in **more than one**
    place is recorded as a conflict and merged nowhere, because choosing among
    its alignments would be exactly the silent forcing this ticket forbids.

    Tiles no motif reaches are then attached through their strongest accepted
    adjacency constraint wherever a matching free cell exists. Whatever is still
    unplaced is reported as ``unconstrained`` or ``unused``, never dropped.
    """
    usage = census.bank_usage(bank)
    conflicts: list = []
    motifs = _repeated_motifs(census, bank, parameters)

    #: component index -> {(x, y): packed tile id}
    layouts: list = []
    #: component index -> {(x, y): Evidence}
    evidence: list = []
    #: packed tile id -> component indices that contain it (duplicates allowed)
    members: dict = {}
    #: component index -> the packed tile at its top-left-most placement
    roots: list = []
    #: packed tile id -> how many times it is already presented on the sheet
    instances: Counter = Counter()
    #: how many motifs were declined because a tile had spent its budget
    budget_refusals = 0

    def remember(component_index: int, tile: int) -> None:
        members.setdefault(tile, set()).add(component_index)
        instances[tile] += 1

    def affordable(motif: dict) -> bool:
        """Whether presenting this motif stays inside the instance budget."""
        needed: Counter = Counter(motif.values())
        return all(
            instances[tile] + count <= parameters.max_instances_per_tile
            for tile, count in needed.items()
        )

    for support, size, key, motif in motifs:
        anchor = motif[(0, 0)]
        candidates = []
        for component_index in sorted(members.get(anchor, ())):
            layout = layouts[component_index]
            for (x, y), tile in sorted(layout.items()):
                if tile != anchor:
                    continue
                if all(
                    layout.get((mx + x, my + y), tile_id) == tile_id
                    for (mx, my), tile_id in motif.items()
                ):
                    candidates.append((component_index, x, y))
        if len(candidates) > 1:
            # Every candidate is *compatible* with the layout already inferred -
            # that is what the test above proves - so the choice is between
            # equally valid anchors, not between conflicting placements. It is
            # taken deterministically and the ambiguity is recorded.
            conflicts.append(
                Conflict(
                    kind="ambiguous_motif_anchor",
                    detail=(
                        f"a {size}x{size} arrangement observed {support} times "
                        f"fits the inferred layout at {len(candidates)} places; "
                        "the first by component and offset is used and the "
                        "alternatives are recorded here"
                    ),
                    source=TileIdentity(bank, anchor & 0xFF),
                    support=support,
                    rival_support=len(candidates),
                )
            )
        if candidates:
            component_index, ox, oy = candidates[0]
            if not affordable(motif):
                budget_refusals += 1
                continue
            layout = layouts[component_index]
            for (mx, my), tile in sorted(motif.items()):
                spot = (mx + ox, my + oy)
                if spot not in layout:
                    layout[spot] = tile
                    evidence[component_index][spot] = Evidence(
                        kind="motif",
                        detail=(
                            f"a {size}x{size} arrangement observed {support} times "
                            "in decoded map layers places this tile here"
                        ),
                        motif_size=size,
                        motif_support=support,
                    )
                    remember(component_index, tile)
            continue
        if not affordable(motif):
            budget_refusals += 1
            continue
        component_index = len(layouts)
        layouts.append({})
        evidence.append({})
        roots.append(anchor)
        for (mx, my), tile in sorted(motif.items()):
            layouts[component_index][(mx, my)] = tile
            evidence[component_index][(mx, my)] = Evidence(
                kind="motif",
                detail=(
                    f"a {size}x{size} arrangement observed {support} times in "
                    "decoded map layers founded this component"
                ),
                motif_size=size,
                motif_support=support,
            )
            remember(component_index, tile)

    ordered = sorted(
        constraints,
        key=lambda item: (
            -item.support,
            -item.confidence_ppm,
            item.source.tile,
            item.target.tile,
        ),
    )
    for _pass in range(usage.tile_count + 1):
        progressed = False
        for constraint in ordered:
            source = constraint.source.packed
            target = constraint.target.packed
            dx, dy = constraint.direction
            if (source in members) == (target in members):
                continue
            if source in members:
                moved, placed = source, target
                sign = 1
            else:
                moved, placed = target, source
                sign = -1
            if instances[placed] >= parameters.max_instances_per_tile:
                budget_refusals += 1
                continue
            for component_index in sorted(members[moved]):
                layout = layouts[component_index]
                spot = None
                for (x, y), tile in sorted(layout.items()):
                    if tile != moved:
                        continue
                    candidate = (x + sign * dx, y + sign * dy)
                    if candidate not in layout:
                        spot = candidate
                        break
                if spot is None:
                    continue
                layout[spot] = placed
                evidence[component_index][spot] = Evidence(
                    kind="adjacency",
                    detail=(
                        "no repeated arrangement reached this tile, so it is "
                        "placed by its strongest directional relationship"
                    ),
                    constraint=constraint,
                )
                remember(component_index, placed)
                progressed = True
                break
        if not progressed:
            break

    components: list = []
    for component_index, layout in enumerate(layouts):
        if not layout:
            continue
        min_x = min(x for x, _y in layout)
        min_y = min(y for _x, y in layout)
        placements = []
        for (x, y), tile in sorted(layout.items(), key=lambda item: (item[0][1], item[0][0])):
            item = evidence[component_index][(x, y)]
            placements.append(
                Placement(
                    tile=TileIdentity(bank, tile & 0xFF),
                    x=x - min_x,
                    y=y - min_y,
                    role=(
                        "root"
                        if tile == roots[component_index]
                        else ("edge" if item.kind == "adjacency" else "motif")
                    ),
                    evidence=item,
                )
            )
        width = max(placement.x for placement in placements) + 1
        height = max(placement.y for placement in placements) + 1
        support = max(
            item.motif_support
            for item in evidence[component_index].values()
        )
        components.append(
            Component(
                index=len(components),
                root=TileIdentity(bank, roots[component_index] & 0xFF),
                placements=tuple(placements),
                width=width,
                height=height,
                support=support,
            )
        )

    claimed = {
        placement.tile.tile
        for component in components
        for placement in component.placements
    }
    leftovers = [tile for tile in range(usage.tile_count) if tile not in claimed]
    leftover_evidence = Evidence(
        kind="no_constraint",
        detail=(
            "the census accepted no relationship strong enough to place this "
            "tile, so it is kept in storage order rather than placed on a guess"
        ),
    )
    for start in range(0, len(leftovers), parameters.pack_start_width):
        block = leftovers[start:start + parameters.pack_start_width]
        components.append(
            Component(
                index=len(components),
                root=TileIdentity(bank, block[0]),
                placements=tuple(
                    Placement(
                        tile=TileIdentity(bank, tile),
                        x=offset,
                        y=0,
                        role="unused" if tile not in usage.tiles else "unconstrained",
                        evidence=leftover_evidence,
                    )
                    for offset, tile in enumerate(block)
                ),
                width=len(block),
                height=1,
                support=0,
            )
        )
    if budget_refusals:
        conflicts.append(
            Conflict(
                kind="instance_budget_reached",
                detail=(
                    f"{budget_refusals} further arrangements were declined because "
                    "a tile they would present had already spent its duplicate "
                    "instance budget; they are counted here rather than silently "
                    "presented"
                ),
                source=TileIdentity(bank, 0),
                support=budget_refusals,
            )
        )
    return tuple(components), tuple(conflicts)


def infer_bank(
    census: Census, bank: int, *, parameters: InferenceParameters | None = None
) -> InferredAtlas:
    """Infer one bank's authoring atlas from the census.

    Every tile the bank declares is placed at least once. A ROM tile may be
    placed more than once when it takes part in more than one strong
    arrangement: the atlas is a view over the bank, not a relocation of it, so a
    duplicate presentation instance is legitimate and is labelled as one.
    """
    parameters = parameters or InferenceParameters()
    constraints, conflicts = _select_constraints(census, bank, parameters)
    components, layout_conflicts = _build_components(
        census, bank, parameters, constraints
    )
    every_conflict = tuple(
        sorted(conflicts + layout_conflicts, key=_conflict_sort_key)
    )
    conflict_digest = hashlib.sha256()
    for conflict in every_conflict:
        conflict_digest.update(
            json.dumps(conflict.to_document(), sort_keys=True).encode("utf-8")
        )
    recorded = every_conflict[: parameters.max_recorded_conflicts]
    canvas = pack_components(components, parameters=parameters)
    cells = tuple(
        AtlasCell(
            column=placed.column,
            row=placed.row,
            tile=placed.tile,
            component=placed.component,
            role=placed.role,
            evidence=placed.evidence,
        )
        for placed in canvas.placements
    )
    return InferredAtlas(
        bank=bank,
        parameters=parameters,
        components=components,
        canvas=canvas,
        cells=cells,
        constraints=constraints,
        conflicts=recorded,
        conflict_total=len(every_conflict),
        conflicts_sha256=conflict_digest.hexdigest(),
    )


def _conflict_sort_key(conflict: Conflict) -> tuple:
    """A total, content-derived order over conflicts, for a stable digest."""

    def tile_key(tile) -> tuple:
        return (0, 0) if tile is None else (1, tile.tile)

    return (
        conflict.kind,
        tile_key(conflict.source),
        tile_key(conflict.target),
        tile_key(conflict.occupant),
        conflict.direction or (0, 0),
        -conflict.support,
        -conflict.rival_support,
        conflict.detail,
    )


# --- packing ------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class PackedPlacement:
    """One tile's absolute cell on the packed canvas."""

    component: int
    tile: TileIdentity
    column: int
    row: int
    role: str
    evidence: Evidence


@dataclass(frozen=True, slots=True)
class PackedCanvas:
    """A deterministic tile-cell canvas: components in shelves, gutters between.

    Empty cells are **kept**, not cropped: the canvas is a full rectangle, the
    count is reported and a digest over the exact coordinates makes the padding
    verifiable rather than merely claimed.
    """

    columns: int
    rows: int
    gutter: int
    placements: tuple
    empty_cells: tuple
    empty_cell_sha256: str

    def to_document(self) -> dict[str, object]:
        return {
            "columns": self.columns,
            "rows": self.rows,
            "gutter": self.gutter,
            "pixel_width": self.columns * TILE_PIXELS,
            "pixel_height": self.rows * TILE_PIXELS,
            "placed_cells": len(self.placements),
            "empty_cell_count": len(self.empty_cells),
            "empty_cell_sha256": self.empty_cell_sha256,
        }


def pack_components(
    components: Sequence[Component],
    *,
    parameters: InferenceParameters | None = None,
) -> PackedCanvas:
    """Shelf-pack components onto a tile-cell canvas with gutters.

    Ordering is by descending area, then descending tile count, then the root
    tile - so the biggest and best-evidenced motif blocks land first and read as
    blocks, and the order never depends on a set's iteration order.

    The canvas starts ``pack_start_width`` tiles wide and widens to a roughly
    square sheet - the smallest multiple of the starting width whose square
    holds everything placed - and then further only if a single component does
    not fit. "Expanding deterministically when needed" is exactly this: a pure
    function of the components, with no search over orderings and no clock.
    """
    parameters = parameters or InferenceParameters()
    gutter = parameters.pack_gutter
    if gutter < 1:
        raise TilesetCompositorError(
            f"packing needs at least a one-tile gutter; got {gutter}"
        )

    ordered = sorted(
        components,
        key=lambda component: (
            -component.area,
            -component.tile_count,
            -component.support,
            component.root.tile,
        ),
    )
    total_area = sum(component.area for component in ordered)
    total_area += 2 * gutter * (len(ordered) + 1)
    side = 1
    while side * side < total_area:
        side += 1
    step = max(1, parameters.pack_start_width)
    columns = max(step, ((side + step - 1) // step) * step)
    columns = max(columns, max((component.width for component in ordered), default=1))

    placements: list[PackedPlacement] = []
    occupied: set = set()
    cursor_x = 0
    cursor_y = 0
    shelf_height = 0
    for component in ordered:
        if cursor_x and cursor_x + component.width > columns:
            cursor_y += shelf_height + gutter
            cursor_x = 0
            shelf_height = 0
        for placement in component.placements:
            column = cursor_x + placement.x
            row = cursor_y + placement.y
            placements.append(
                PackedPlacement(
                    component=component.index,
                    tile=placement.tile,
                    column=column,
                    row=row,
                    role=placement.role,
                    evidence=placement.evidence,
                )
            )
            occupied.add((column, row))
        cursor_x += component.width + gutter
        shelf_height = max(shelf_height, component.height)

    rows = cursor_y + shelf_height
    empty = tuple(
        (column, row)
        for row in range(rows)
        for column in range(columns)
        if (column, row) not in occupied
    )
    digest = hashlib.sha256()
    for column, row in empty:
        digest.update(struct.pack("<II", column, row))

    placements.sort(key=lambda placed: (placed.row, placed.column, placed.tile.tile))
    return PackedCanvas(
        columns=columns,
        rows=rows,
        gutter=gutter,
        placements=tuple(placements),
        empty_cells=empty,
        empty_cell_sha256=digest.hexdigest(),
    )


# --- inferred atlas -----------------------------------------------------------

@dataclass(frozen=True, slots=True)
class AtlasCell:
    """One displayed atlas cell: where it is, what it is, why it is there.

    The evidence is carried per cell rather than looked up later, so a
    duplicate presentation instance of one ROM tile can state the *different*
    reason each instance earned its place.
    """

    column: int
    row: int
    tile: TileIdentity
    component: int
    role: str
    evidence: Evidence

    def to_document(self) -> dict[str, object]:
        return {
            "column": self.column,
            "row": self.row,
            "bank": self.tile.bank,
            "tile": self.tile.tile,
            "component": self.component,
            "role": self.role,
            "evidence": self.evidence.to_document(),
        }


@dataclass(frozen=True, slots=True)
class InferredAtlas:
    """One bank's inferred atlas: components, canvas, cells and evidence."""

    bank: int
    parameters: InferenceParameters
    components: tuple
    canvas: PackedCanvas
    cells: tuple
    constraints: tuple
    #: The conflicts *enumerated* in the manifest, capped by policy.
    conflicts: tuple
    #: How many conflicts the inference actually produced, and a digest over
    #: every one of them in a canonical order. The cap bounds the document; it
    #: never weakens the claim that nothing was dropped.
    conflict_total: int
    conflicts_sha256: str

    @property
    def used_components(self) -> tuple:
        return tuple(c for c in self.components if c.support > 0)

    def to_document(self) -> dict[str, object]:
        return {
            "bank": self.bank,
            "tileset": self.bank + 1,
            "parameters": self.parameters.to_document(),
            "canvas": self.canvas.to_document(),
            "component_count": len(self.components),
            "motif_component_count": len(self.used_components),
            "conflict_count": self.conflict_total,
            "recorded_conflict_count": len(self.conflicts),
            "conflicts_sha256": self.conflicts_sha256,
            "conflicts": [conflict.to_document() for conflict in self.conflicts],
        }


# --- rendering ----------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class RenderedView:
    """One 8bpp index image plus the padding it deliberately kept."""

    name: str
    width: int
    height: int
    pixels: bytes
    empty_cell_count: int = 0
    detail: dict = field(default_factory=dict)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.pixels).hexdigest()


def tile_pixels(payload: bytes, tile: int) -> bytes:
    """One tile's 8x8 linear palette indices, unswizzled from a bank payload.

    A bank payload stores tiles swizzled, exactly as the assembled character
    block does, so this is the same unswizzle the production renderer performs -
    there is no second reading of the tile layout.
    """
    start = tile * _mg.TILE_BYTES
    if tile < 0 or start + _mg.TILE_BYTES > len(payload):
        raise TilesetCompositorError(
            f"tile {tile} needs bytes {start:#x}..{start + _mg.TILE_BYTES:#x} "
            f"but the bank holds {len(payload)}"
        )
    return _sg.unswizzle_tiles(
        payload[start:start + _mg.TILE_BYTES],
        TILE_PIXELS,
        TILE_PIXELS,
        colour_256=True,
    )


def _blit(
    canvas: bytearray,
    canvas_width: int,
    tile: bytes,
    column: int,
    row: int,
) -> None:
    """Draw one 8x8 tile at a tile-cell position."""
    for line in range(TILE_PIXELS):
        target = (row * TILE_PIXELS + line) * canvas_width + column * TILE_PIXELS
        canvas[target:target + TILE_PIXELS] = tile[
            line * TILE_PIXELS:(line + 1) * TILE_PIXELS
        ]


def render_raw_bank(
    payload: bytes, *, columns: int = RAW_COLUMNS
) -> RenderedView:
    """The bank exactly as its container stores it: storage order, 16 per row.

    The trailing cells of the last row are kept and counted. They are not
    tiles, and cropping them silently would make a 241-tile bank and a 256-tile
    bank produce the same image.
    """
    if columns <= 0:
        raise TilesetCompositorError(f"raw columns must be positive; got {columns}")
    tiles = len(payload) // _mg.TILE_BYTES
    if tiles <= 0:
        raise TilesetCompositorError("a raw sheet needs at least one tile")
    rows = (tiles + columns - 1) // columns
    width = columns * TILE_PIXELS
    canvas = bytearray(width * rows * TILE_PIXELS)
    for index in range(tiles):
        _blit(
            canvas,
            width,
            tile_pixels(payload, index),
            index % columns,
            index // columns,
        )
    padding = rows * columns - tiles
    return RenderedView(
        name="raw",
        width=width,
        height=rows * TILE_PIXELS,
        pixels=bytes(canvas),
        empty_cell_count=padding,
        detail={"columns": columns, "rows": rows, "tiles": tiles, "padding_cells": padding},
    )


def render_inferred_atlas(atlas: InferredAtlas, payload: bytes) -> RenderedView:
    """The inferred atlas as pixels: one source tile per placed cell.

    No scaling, no resampling and no invented pixel: a cell is either a real
    tile's own 8x8 indices or it is the transparent index the empty cells keep.
    """
    canvas_spec = atlas.canvas
    width = canvas_spec.columns * TILE_PIXELS
    canvas = bytearray(width * canvas_spec.rows * TILE_PIXELS)
    for cell in atlas.cells:
        _blit(canvas, width, tile_pixels(payload, cell.tile.tile), cell.column, cell.row)
    return RenderedView(
        name="inferred",
        width=width,
        height=canvas_spec.rows * TILE_PIXELS,
        pixels=bytes(canvas),
        empty_cell_count=len(canvas_spec.empty_cells),
        detail={
            "columns": canvas_spec.columns,
            "rows": canvas_spec.rows,
            "cells": len(atlas.cells),
            "components": len(atlas.components),
        },
    )


#: The layer forms whose observed view is a genuine 32x32 screen-entry plane.
#: A terrain field is a plane of 8-bit ordinals, not screen entries, so it is
#: censused for usage but has no screen-entry chunk to show.
OBSERVED_KINDS = (LAYER_KIND_DOMINANT, LAYER_KIND_SCREENBLOCK)


def observed_chunk_planes(
    reader: _mg.MapGraphicsReader,
    census: Census,
    bank: int,
    *,
    limit: int | None = None,
) -> tuple:
    """The observed 32x32 screen-entry planes that use this bank.

    Returns ``(planes, total)`` where each plane is
    ``(ObservedChunk, char_data, words)``. ``char_data`` is the owning map's own
    assembled character block, because a chunk holds char-block *ordinals* that
    only mean anything through the map that uses them.

    The planes are ordered by ``(map index, chunk address)``, so a limit keeps
    the earliest maps deterministically rather than whatever a directory walk
    happened to produce.
    """
    usage = census.bank_usage(bank)
    refs = sorted(
        (
            ref
            for ref in usage.observed_chunks.values()
            if ref.layer_kind in OBSERVED_KINDS
        ),
        key=lambda ref: (ref.map_index, ref.chunk_address),
    )
    total = len(refs)
    if limit is not None:
        refs = refs[:limit]

    entries = _mg.read_map_entries(reader)
    blocks: dict = {}
    planes: list = []
    for ref in refs:
        if ref.map_index not in blocks:
            block, _stream, _animated = _mg.assemble_map_char_block(
                reader, entries[ref.map_index].root_address
            )
            blocks[ref.map_index] = block.data
        if ref.layer_kind == LAYER_KIND_DOMINANT:
            words = _mg.dominant_chunk_words(reader, ref.chunk_address)
        else:
            words = _mg.read_screenblock_entries(reader, ref.layer_address)
        planes.append((ref, blocks[ref.map_index], words))
    return tuple(planes), total


def render_observed_view(
    planes: Sequence,
    *,
    columns: int = 8,
    gutter: int = 1,
) -> RenderedView:
    """Compose observed chunks into one reference image.

    Each chunk is rendered by the production regular-BG renderer over its own
    map's character block. This function adds no tile logic of its own, which is
    what keeps the reference view pixel-equivalent to the runtime-proven
    renderer rather than a second opinion about it.
    """
    if columns <= 0:
        raise TilesetCompositorError(f"observed columns must be positive; got {columns}")
    if gutter < 0:
        raise TilesetCompositorError(f"a gutter cannot be negative; got {gutter}")
    chunk_pixels = _mg.CHUNK_PIXELS
    step = chunk_pixels + gutter * TILE_PIXELS
    if not planes:
        return RenderedView(
            name="observed",
            width=0,
            height=0,
            pixels=b"",
            empty_cell_count=0,
            detail={"chunks": 0, "columns": columns},
        )

    rows = (len(planes) + columns - 1) // columns
    width = columns * step - gutter * TILE_PIXELS
    height = rows * step - gutter * TILE_PIXELS
    canvas = bytearray(width * height)
    for index, (reference, char_data, words) in enumerate(planes):
        pixels, _w, _h = _bg.render_entry_words(
            char_data,
            words,
            map_width_tiles=CHUNK_SIDE,
            map_height_tiles=CHUNK_SIDE,
            color_256=True,
        )
        origin_x = (index % columns) * step
        origin_y = (index // columns) * step
        for line in range(chunk_pixels):
            source = line * chunk_pixels
            target = (origin_y + line) * width + origin_x
            canvas[target:target + chunk_pixels] = pixels[source:source + chunk_pixels]
    empty = rows * columns - len(planes)
    return RenderedView(
        name="observed",
        width=width,
        height=height,
        pixels=bytes(canvas),
        empty_cell_count=empty,
        detail={"chunks": len(planes), "columns": columns, "gutter": gutter},
    )


# --- documents ----------------------------------------------------------------

#: Stated in every atlas document so the motif booster's scope is never a
#: surprise to someone reading a placement.
MOTIF_ANCHOR_RULE = (
    "a motif is indexed under the bank of its top-left cell, so motif pair "
    "support measures the windows this bank anchors; the adjacency table, the "
    "primary signal, is exact for every source tile in the bank"
)


def _cells_digest(atlas: InferredAtlas) -> str:
    digest = hashlib.sha256()
    for cell in atlas.cells:
        digest.update(
            struct.pack(
                "<HHHHH",
                cell.tile.bank,
                cell.tile.tile,
                cell.column,
                cell.row,
                cell.component,
            )
        )
        digest.update(cell.role.encode("ascii"))
    return digest.hexdigest()


def atlas_document(
    census: Census, atlas: InferredAtlas, *, samples: int | None = None
) -> dict[str, object]:
    """The deterministic per-bank atlas manifest.

    Every displayed cell names its tile, and every displayed tile carries the
    census' complete usage record for it: the maps that use it, the layer forms
    they use it in, the chunk containers it appears in, the raw 16-bit screen
    entries it was reached by, every palette-bank and flip state it was ever
    presented with, the occurrence count, a digest over the *complete*
    occurrence stream, and exact samples drawn from that stream.
    """
    samples = census.parameters.occurrence_samples if samples is None else samples
    usage = census.bank_usage(atlas.bank)
    displayed = sorted({cell.tile.tile for cell in atlas.cells})
    return {
        "schema": 1,
        "kind": "tileset-compositor/bank-atlas",
        "bank": atlas.bank,
        "tileset": atlas.bank + 1,
        "container_address": f"{usage.container_address:#010x}",
        "declared_size": usage.declared_size,
        "tile_count": usage.tile_count,
        "profile": census.profile_id,
        "motif_anchor_rule": MOTIF_ANCHOR_RULE,
        "census": census.to_document(),
        "parameters": atlas.parameters.to_document(),
        "usage": {
            "occurrence_total": usage.occurrences,
            "tiles_used": len(usage.tiles),
            "tiles_declared": usage.tile_count,
            "observed_chunk_count": len(usage.observed_chunks),
        },
        "canvas": atlas.canvas.to_document(),
        "component_count": len(atlas.components),
        "conflict_count": atlas.conflict_total,
        "recorded_conflict_count": len(atlas.conflicts),
        "conflicts_sha256": atlas.conflicts_sha256,
        "components": [component.to_document() for component in atlas.components],
        "constraints": [constraint.to_document() for constraint in atlas.constraints],
        "conflicts": [conflict.to_document() for conflict in atlas.conflicts],
        "tiles": [
            (
                usage.tiles[tile] if tile in usage.tiles else TileUsage()
            ).to_document(TileIdentity(atlas.bank, tile), samples)
            for tile in displayed
        ],
        "cells": [cell.to_document() for cell in atlas.cells],
        "cells_sha256": _cells_digest(atlas),
    }


def run_document(
    census: Census,
    summaries: Sequence[Mapping],
    artifacts: Sequence[Mapping],
    *,
    inference: InferenceParameters,
) -> dict[str, object]:
    """The run-level manifest: the census, the parameters, and every artifact."""
    return {
        "schema": 1,
        "kind": "tileset-compositor/run",
        "profile": census.profile_id,
        "motif_anchor_rule": MOTIF_ANCHOR_RULE,
        "census": census.to_document(),
        "inference_parameters": inference.to_document(),
        "banks": list(summaries),
        "artifacts": list(artifacts),
    }


def _json_bytes(document: Mapping) -> bytes:
    """Canonical JSON: sorted keys, fixed indent, one trailing newline."""
    text = json.dumps(document, sort_keys=True, indent=2)
    return (text + "\n").encode("utf-8")


# --- output -------------------------------------------------------------------

def _repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def prepare_output_root(path: str | Path) -> Path:
    """Refuse a generated-output location that would escape the ignored tree.

    Generated proprietary artwork must stay local and ignored. Everything this
    module writes is derived from the canonical ROM, so it is refused inside the
    repository unless it is under ``build/`` - which is the one directory the
    repository already ignores - and refused outright at a path that is an
    existing file, the repository root, or an ancestor of it.
    """
    resolved = Path(path).resolve()
    root = _repository_root()
    if resolved == root:
        raise TilesetCompositorError(
            f"{resolved} is the repository root; generated output belongs in a "
            "directory of its own"
        )
    if root in resolved.parents:
        build = root / "build"
        if resolved != build and build not in resolved.parents:
            raise TilesetCompositorError(
                f"generated output inside the repository must stay under "
                f"{build}, not {resolved}"
            )
    if resolved.exists():
        if not resolved.is_dir():
            raise TilesetCompositorError(f"{resolved} exists and is not a directory")
        if any(resolved.iterdir()):
            raise TilesetCompositorError(
                f"{resolved} is not empty; a run writes a fresh directory so its "
                "outputs cannot be confused with a previous run's"
            )
    return resolved


def _write(path: Path, data: bytes) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def write_bundle(
    reader: _mg.MapGraphicsReader,
    census: Census,
    banks: Sequence[int],
    output_root: str | Path,
    *,
    inference: InferenceParameters | None = None,
    palette: Sequence[tuple[int, int, int]] | None = None,
    observed_columns: int = 8,
    observed_limit: int | None = 64,
    raw_columns: int = RAW_COLUMNS,
    write_observed: bool = True,
) -> dict[str, object]:
    """Write one run's Raw, Observed and Inferred set plus its manifests.

    Deterministic: the same ROM bytes and the same parameters produce the same
    file set, the same file names and byte-identical file contents. Nothing here
    reads the clock or the environment, and every image is an 8-bit indexed PNG
    whose palette entry 0 is the transparent index the platform uses.
    """
    inference = inference or InferenceParameters()
    root = prepare_output_root(output_root)
    palette = tuple(palette) if palette is not None else _mg.decode_bg_palette(reader)
    if len(palette) < 2:
        raise TilesetCompositorError("an indexed atlas needs at least two palette entries")

    artifacts: list[dict] = []
    summaries: list[dict] = []

    for bank in sorted({int(value) for value in banks}):
        usage = census.bank_usage(bank)
        payload = reader.container(usage.container_address).data
        if len(payload) % _mg.TILE_BYTES:
            raise TilesetCompositorError(
                f"bank {bank} decodes to {len(payload)} bytes, not whole tiles"
            )
        atlas = infer_bank(census, bank, parameters=inference)
        directory = root / f"bank-{bank:03d}"

        raw = render_raw_bank(payload, columns=raw_columns)
        inferred = render_inferred_atlas(atlas, payload)

        written: dict[str, object] = {}
        images = [("raw.png", raw), ("inferred.png", inferred)]
        if write_observed:
            planes, total = observed_chunk_planes(
                reader, census, bank, limit=observed_limit
            )
            observed = render_observed_view(
                planes, columns=observed_columns, gutter=inference.pack_gutter
            )
            images.append(("observed.png", observed))

        for name, view in images:
            data = _png.encode(
                view.pixels, view.width, view.height, palette, transparent_index=0
            )
            info = _write(directory / name, data)
            artifacts.append({"path": f"bank-{bank:03d}/{name}", **info})
            written[name] = info

        document = atlas_document(census, atlas)
        document["images"] = {
            "raw": raw.detail,
            "inferred": inferred.detail,
        }
        if write_observed:
            document["images"]["observed"] = {
                **observed.detail,
                "observed_total": total,
                "observed_shown": len(planes),
            }
        document["image_pixels_sha256"] = {
            "raw": raw.digest,
            "inferred": inferred.digest,
        }
        if write_observed:
            document["image_pixels_sha256"]["observed"] = observed.digest
        atlas_bytes = _json_bytes(document)
        info = _write(directory / "atlas.json", atlas_bytes)
        artifacts.append({"path": f"bank-{bank:03d}/atlas.json", **info})

        summaries.append(
            {
                "bank": bank,
                "tileset": bank + 1,
                "container_address": f"{usage.container_address:#010x}",
                "tile_count": usage.tile_count,
                "tiles_used": len(usage.tiles),
                "occurrence_total": usage.occurrences,
                "observed_chunk_count": len(usage.observed_chunks),
                "canvas": atlas.canvas.to_document(),
                "component_count": len(atlas.components),
                "motif_component_count": len(atlas.used_components),
                "conflict_count": atlas.conflict_total,
                "conflicts_sha256": atlas.conflicts_sha256,
                "cells_sha256": document["cells_sha256"],
                "atlas_path": f"bank-{bank:03d}/atlas.json",
            }
        )

    document = run_document(
        census, summaries, artifacts, inference=inference
    )
    info = _write(root / "manifest.json", _json_bytes(document))
    artifacts.append({"path": "manifest.json", **info})
    return {"root": str(root), "manifest": document, "artifacts": artifacts}
