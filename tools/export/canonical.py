"""Canonical readers for the accepted Buu's Fury resource graph.

ASSET-EXPORT-001. This module is the export-side, read-only view of the accepted
post-LOGX schemas. Every offset it publishes is the accepted schema in
`docs/research/LOGX_SYNTHESIS.md` (§3 map/world, §7 sprite definitions, §8
animation/frame/piece, §2.5 codec). Nothing here is derived from
`LOGExtractor`'s superseded readings, and the refuted model is not reachable from
this module:

* the superseded fixed 23-slot animation model is not used; the array is bounded
  by definition `+0x00`;
* the refuted 4-byte frame header and 16-byte piece stride are not used; the
  frame header is `0x08` bytes and pieces are `0x0C` bytes at `frame + 0x08`;
* the piece attribute pair is read at `+0x04` and the graphics word at `+0x08`,
  not at `+0x08`/`+0x0C`;
* tile-entry bits 12..15 are recorded raw and never explained;
* a layer `+0x00` word is a **Thumb handler entry**, never a numeric type tag.

**The map side reads through the SDK's format layer (CQA-04).** The map-entry
table, the layer records and their handler classification, the dominant chunk
grid, the selector stream, the screen-entry planes, the Map 19 terrain field, the
animated-tile records, the assembled character block and the engine-global
background palette are all read by
:mod:`tools.webfoot.formats.map_graphics`. This module keeps the export-facing
spelling of those readers so the exporter's call sites and their evidence labels
do not move, but there is no longer a second implementation behind them. That was
the finding: the export stack and the SDK renderer each decoded the same records,
nothing compared them, and they had already drifted.

**Why the export path asks for a stricter container.** The first justification
this module carried - that the shipping decoder clipped an over-long final match,
so the export needed its own strict reader - was repaired by
EVIDENCE-RISK-DEBT-001. What survives is the end-marker postcondition, which
`LOGX-CODEC-001` measured over the 4,322 packed containers reachable from the map
side and this exporter measured over its own wider 11,712: every one produces
exactly its declared size with the stream's own escape falling at that length. It
is a checkable postcondition, not the engine's rule, so it stays a policy of the
export path and is injected into the shared reader rather than asserted by it.

Offsets are read through :class:`Rom`, which bounds-checks every access against
the image, so a misread address fails loudly instead of wrapping.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import TYPE_CHECKING

from tools.webfoot.formats import map_entry as _me
from tools.webfoot.formats import map_graphics as _mg
from tools.webfoot.formats import text_tables as _tt

from . import profile_authority
from . import webfoot_strict as ws

if TYPE_CHECKING:  # pragma: no cover - typing only
    from tools.webfoot.profile import (
        AtlasIdentity,
        RomProfile,
        TextTableProfile,
    )

# --- accepted constants ------------------------------------------------------
#
# The map-side constants are the format layer's now: they are re-exported here so
# this module's callers keep one import site, and so a value cannot exist in two
# spellings. `buu_resource_export` reads several of them for its own curation
# decisions, which is exactly why the re-export rather than a second literal is
# the right shape.

#: The MapEntry record shape is the format's, owned by `webfoot.formats.map_entry`.
#: The TABLE address and its record COUNT are the profile's declarations and are
#: read through `Rom.map_entry_table_address()` / `Rom.map_entry_count()`; they are
#: deliberately not restated as module constants (CQA-15).
MAP_ENTRY_STRIDE = _me.MAP_ENTRY_SIZE

#: One pointer-table entry is one little-endian GBA address. The width is a
#: format fact and comes from the codec, so this module does not spell it "4".
TEXT_POINTER_SIZE = _tt.TEXT_POINTER_SIZE

#: MapEntry fields the accepted discovery route uses.
MAP_ENTRY_KEY_OFFSET = _mg.MAP_ENTRY_KEY_OFFSET
MAP_ENTRY_TEXT_OFFSET = _mg.MAP_ENTRY_TEXT_OFFSET
MAP_ENTRY_SOURCE_OFFSET = _mg.MAP_ENTRY_SOURCE_OFFSET

#: Map root (the load-time definition template) fields.
ROOT_LAYER_SLOTS = _mg.ROOT_LAYER_SLOTS
ROOT_BG_ADDEND_OFFSET = _mg.ROOT_BG_ADDEND_OFFSET
ROOT_EXTENT_X_OFFSET = _mg.ROOT_EXTENT_X_OFFSET
ROOT_EXTENT_Y_OFFSET = _mg.ROOT_EXTENT_Y_OFFSET
ROOT_SELECTOR_STREAM_OFFSET = _mg.ROOT_SELECTOR_STREAM_OFFSET
ROOT_BANK_TABLE_OFFSET = _mg.ROOT_BANK_TABLE_OFFSET
ROOT_CONNECTION_COUNT_OFFSET = _mg.ROOT_CONNECTION_COUNT_OFFSET
ROOT_CONNECTION_ARRAY_OFFSET = _mg.ROOT_CONNECTION_ARRAY_OFFSET
ROOT_BG_CONTROL_OFFSET = _mg.ROOT_BG_CONTROL_OFFSET
ROOT_ANIMATED_COUNT_OFFSET = _mg.ROOT_ANIMATED_COUNT_OFFSET
ROOT_ANIMATED_ARRAY_OFFSET = _mg.ROOT_ANIMATED_ARRAY_OFFSET

#: Layer-record fields for the dominant form.
LAYER_HANDLER_OFFSET = _mg.LAYER_HANDLER_OFFSET
LAYER_CHUNK_X_OFFSET = _mg.LAYER_CHUNK_X_OFFSET
LAYER_CHUNK_Y_OFFSET = _mg.LAYER_CHUNK_Y_OFFSET
LAYER_CHUNK_WINDOW_OFFSET = _mg.LAYER_CHUNK_WINDOW_OFFSET

#: The five accepted layer `+0x00` handler values, and the record-field mapping
#: for the two screen-entry handlers.
DOMINANT_LAYER_HANDLER = _mg.DOMINANT_LAYER_HANDLER
ABSENT_LAYER_HANDLER = _mg.ABSENT_LAYER_HANDLER
ABSENT_LAYER_RECORD = _mg.ABSENT_LAYER_RECORD
SCREENBLOCK_HANDLERS = _mg.SCREENBLOCK_HANDLERS
SCREENBLOCK_ENTRY_COUNT = _mg.SCREENBLOCK_ENTRY_COUNT
SCREENBLOCK_DECODED_BYTES = _mg.SCREENBLOCK_DECODED_BYTES
SCREENBLOCK_PIXELS = _mg.SCREENBLOCK_PIXELS

#: The Map 19 terrain-field layer form.
TERRAIN_FIELD_LAYER_HANDLER = _mg.TERRAIN_FIELD_LAYER_HANDLER
TERRAIN_FIELD_GRID_X_OFFSET = _mg.TERRAIN_FIELD_GRID_X_OFFSET
TERRAIN_FIELD_GRID_Y_OFFSET = _mg.TERRAIN_FIELD_GRID_Y_OFFSET
TERRAIN_FIELD_CONTAINER_OFFSET = _mg.TERRAIN_FIELD_CONTAINER_OFFSET
TERRAIN_FIELD_CELL_BYTES = _mg.TERRAIN_FIELD_CELL_BYTES
TERRAIN_FIELD_CELL_TILES = _mg.TERRAIN_FIELD_CELL_TILES
TERRAIN_FIELD_TILE_ORDINAL_MASK = _mg.TERRAIN_FIELD_TILE_ORDINAL_MASK
TERRAIN_FIELD_RESIDENT_SLOTS = _mg.TERRAIN_FIELD_RESIDENT_SLOTS

#: Chunk payload geometry.
CHUNK_SIDE_TILES = _mg.CHUNK_SIDE_TILES
CHUNK_ENTRY_COUNT = _mg.CHUNK_ENTRY_COUNT
CHUNK_DECODED_BYTES = _mg.CHUNK_DECODED_BYTES
TILE_PIXELS = _mg.TILE_PIXELS
CHUNK_PIXELS = _mg.CHUNK_PIXELS

#: Tile-entry bit fields the accepted corpus establishes.
TILE_ENTRY_ORDINAL_MASK = _mg.TILE_ENTRY_ORDINAL_MASK
TILE_ENTRY_BIT_10 = _mg.TILE_ENTRY_BIT_10
TILE_ENTRY_BIT_11 = _mg.TILE_ENTRY_BIT_11
TILE_ENTRY_HIGH_NIBBLE = _mg.TILE_ENTRY_HIGH_NIBBLE

#: Bank table: the accepted table's own length, and a bank's tile capacity.
#: The ADDRESS is read from the map root's `+0x4C` field by the shared reader;
#: `BANK_TABLE_ADDRESS` below is the canonical graph's own first root value, kept
#: as a provenance record for the bank catalogue rather than as a second
#: authority.
BANK_COUNT = _mg.BANK_COUNT
BANK_TILE_BYTES = _mg.BANK_TILE_BYTES
#: The canonical map root's bank-table value. The writer and the renderer both
#: read the field from their own root; this literal is what the bank catalogue
#: records as where the accepted graph was found, and is passed explicitly rather
#: than defaulted, so no caller can silently decode another image's table.
BANK_TABLE_ADDRESS = 0x08179764

#: The absent-layer placeholder's substitute container. It is a stored container
#: declaring zero bytes, so substituting it and skipping it both write no pixels.
DEFAULT_CHUNK_CONTAINER = 0x08070808

#: Engine-global background palette: 256 RGB888 triples, uncompressed. The
#: ENTRY COUNT and byte size are format facts; the ADDRESS is the profile's
#: (`tables.actor_sprites.bg_palette_address`), read through
#: `Rom.bg_palette_address()`, not restated here (CQA-15).
BG_PALETTE_ENTRIES = _mg.BG_PALETTE_ENTRIES
BG_PALETTE_BYTES = _mg.BG_PALETTE_BYTES

#: Sprite-definition pointer run: 297 entries, logical ids 10..306.
SPRITE_DEFINITION_COUNT = 297
SPRITE_ID_FLOOR = 10
SPRITE_DEFINITION_COUNT_OFFSET = 0x00
SPRITE_ANIMATION_ARRAY_OFFSET = 0x54
#: Ids below the floor take the party-slot branch instead of the run.
SPRITE_PARTY_ALIAS_IDS = tuple(range(SPRITE_ID_FLOOR))
PARTY_ALIAS_ACCESSOR = 0x08000158
PARTY_ALIAS_REENTRY = 0x0801713C
PARTY_ALIAS_INDEX_TABLE = 0x086B82EC
PARTY_ALIAS_INDEX_STRIDE = 24
PARTY_ALIAS_INDEX_ID_OFFSET = 0x0E

#: Animation object: u32 frame_count, then 4 cells per frame row.
ANIMATION_FRAME_COUNT_OFFSET = 0x00
ANIMATION_CELLS_OFFSET = 0x04
ANIMATION_ROW_BYTES = 16
ANIMATION_CELL_BYTES = 4
DIRECTION_COUNT = 4
ANIMATION_FRAME_COUNT_MIN = 1
ANIMATION_FRAME_COUNT_MAX = 16

#: Frame record: 8-byte header (piece count + rendered-frame bounding box),
#: then 12-byte pieces.
FRAME_HEADER_SIZE = 0x08
FRAME_PIECE_COUNT_OFFSET = 0x00
FRAME_MIN_X_OFFSET = 0x04          # s8
FRAME_MIN_Y_OFFSET = 0x05          # s8
FRAME_WIDTH_OFFSET = 0x06          # u8
FRAME_HEIGHT_OFFSET = 0x07         # u8
FRAME_MAX_PIECES = 16

#: Piece record: s8 x, s8 y, u8 dim_0, u8 dim_1, u32 attribute pair,
#: u32 graphics container.
PIECE_RECORD_SIZE = 0x0C
PIECE_X_OFFSET = 0x00
PIECE_Y_OFFSET = 0x01
PIECE_DIM_0_OFFSET = 0x02
PIECE_DIM_1_OFFSET = 0x03
PIECE_ATTRIBUTES_OFFSET = 0x04
PIECE_GRAPHICS_OFFSET = 0x08

#: GBA OBJ attribute bits the accepted piece word carries.
ATTR0_COLOUR_256 = 0x2000
ATTR0_SHAPE_SHIFT = 14
ATTR1_HORIZONTAL_FLIP = 0x1000
ATTR1_VERTICAL_FLIP = 0x2000
ATTR1_SIZE_SHIFT = 14

#: OAM shape/size -> pixel dimensions (GBATEK). Shape 3 is reserved and refused.
OBJECT_DIMENSIONS = (
    ((8, 8), (16, 16), (32, 32), (64, 64)),
    ((16, 8), (32, 8), (32, 16), (64, 32)),
    ((8, 16), (8, 32), (16, 32), (32, 64)),
)

#: Object palette entries: one 256-word palette is the OAM palette size, a
#: format fact. Its address is the profile's (`tables.actor_sprites.
#: object_palette_address`) and is read through `_profile()`, not restated.
OBJECT_PALETTE_ENTRIES = 256
OBJECT_PALETTE_BYTES = OBJECT_PALETTE_ENTRIES * 2

#: Appearance-definition table: 232 fixed records, stride 0x10. Each record
#: carries two text-table relationships and a sprite-definition selection.
APPEARANCE_COUNT = 232
APPEARANCE_STRIDE = 0x10
APPEARANCE_NAME_TEXT_OFFSET = 0x00   # u16 text index
APPEARANCE_DESCRIPTION_TEXT_OFFSET = 0x02
APPEARANCE_SPRITE_OFFSET = 0x04      # u32 logical sprite id
APPEARANCE_PORTRAIT_OFFSET = 0x08    # u32 index into the 0x086F393C array
APPEARANCE_STAT_OFFSET = 0x0C        # i32; negative values are skipped by the engine


# --- appearance side ---------------------------------------------------------

@dataclass(frozen=True, slots=True)
class AppearanceRecord:
    """One appearance definition: two text relationships and a sprite selection.

    The accepted synthesis describes these as "named appearance definitions with
    optional slot and stat indices". The `+0x00` and `+0x02` text relationships
    are `CONFIRMED`; calling the first a *name* and the second a *description* is
    `PARTIALLY CONFIRMED`, so both strings are carried as ROM text and the
    higher-level claim is not made anywhere. `+0x04` selects a sprite definition
    by logical id.
    """

    appearance_index: int
    address: int
    name_text_index: int | None
    description_text_index: int | None
    sprite_id: int
    portrait_index: int
    stat_index: int


def read_appearances(rom: Rom) -> tuple[AppearanceRecord, ...]:
    """Read all 232 appearance definitions at the accepted offsets."""
    records: list[AppearanceRecord] = []
    base = rom.appearance_table_address()
    for index in range(APPEARANCE_COUNT):
        address = base + index * APPEARANCE_STRIDE
        rom.span(address, APPEARANCE_STRIDE)
        name_index = rom.u16(address + APPEARANCE_NAME_TEXT_OFFSET)
        description_index = rom.u16(address + APPEARANCE_DESCRIPTION_TEXT_OFFSET)
        records.append(
            AppearanceRecord(
                appearance_index=index,
                address=address,
                name_text_index=name_index,
                description_text_index=description_index,
                sprite_id=rom.u32(address + APPEARANCE_SPRITE_OFFSET),
                portrait_index=rom.u32(address + APPEARANCE_PORTRAIT_OFFSET),
                stat_index=struct.unpack_from(
                    "<i", rom.data, rom.offset(address + APPEARANCE_STAT_OFFSET)
                )[0],
            )
        )
    return tuple(records)


def screenblock_container_offset(handler: int) -> int:
    """The record field a screen-entry layer's handler reads its container from.

    The mapping is the format layer's (`map_graphics.SCREENBLOCK_HANDLERS`); this
    is the export-facing spelling of the same lookup.
    """
    try:
        return _mg.screenblock_container_offset(handler)
    except _mg.MapGraphicsError as exc:
        raise CanonicalError(str(exc)) from exc


def read_screenblock_entries(rom: Rom, record_address: int) -> tuple[int, ...]:
    """Read the screen-entry plane a screen-entry layer's handler decompresses.

    Two handlers carry the same 32x32 plane and reach it by different code, so
    the container field is taken from the record's own `+0x00` word. Both reduce
    to 1024 little-endian screen entries, which is why the exporter renders both
    through the screen-entry renderer. Read by the shared map/graphics reader.
    """
    return _shared(lambda: _mg.read_screenblock_entries(rom.graphics_reader(), record_address))


def read_terrain_field_cells(rom: Rom, record_address: int) -> tuple[bytes, ...]:
    """Read a `0x080088BD` record's container payloads in its own raster order.

    The record states its cell grid at `+0x04`/`+0x05` and names `grid_x *
    grid_y` consecutive container pointers from `+0x08`. An empty grid (either
    dimension zero) is an empty field: the engine's own constructor skips the
    eager load when the product is not positive. Read by the shared reader.
    """
    return _shared(
        lambda: _mg.read_terrain_field_cells(rom.graphics_reader(), record_address)
    )


def read_terrain_field_containers(rom: Rom, record_address: int) -> tuple[int, ...]:
    """The container addresses a `0x080088BD` record names, in raster order."""
    return _shared(
        lambda: _mg.read_terrain_field_containers(
            rom.graphics_reader(), record_address
        )
    )


def read_terrain_field_probe(rom: Rom, record_address: int) -> dict[str, int]:
    """Structural facts about a `0x080088BD` record, for the audit only."""
    grid_x = rom.u8(record_address + TERRAIN_FIELD_GRID_X_OFFSET)
    grid_y = rom.u8(record_address + TERRAIN_FIELD_GRID_Y_OFFSET)
    targets: list[int] = []
    for index in range(grid_x * grid_y):
        address = rom.u32(
            record_address + TERRAIN_FIELD_CONTAINER_OFFSET + index * 4
        )
        if not rom.in_image(address):
            break
        targets.append(address)
    return {
        "grid_x": grid_x,
        "grid_y": grid_y,
        "grid_product": grid_x * grid_y,
        "chunk_targets": len(targets),
        "resident_slots": TERRAIN_FIELD_RESIDENT_SLOTS,
        "chunk_decoded_bytes": TERRAIN_FIELD_CELL_BYTES,
        "cell_tiles": TERRAIN_FIELD_CELL_TILES,
    }


class CanonicalError(ValueError):
    """Raised when the accepted graph cannot be read as the schema states."""


def signed_byte(value: int) -> int:
    """Interpret an unsigned byte as ``s8``."""
    return value - 256 if value > 127 else value


def to_file_offset(address: int, size: int) -> int:
    """GBA address -> file offset, refusing anything outside the image."""
    offset = address - ws.GBA_ROM_BASE
    if not 0 <= offset < size:
        raise CanonicalError(
            f"GBA address {address:#010x} (file {offset:#x}) is outside the "
            f"{size:#x}-byte image"
        )
    return offset


class Rom:
    """Bounds-checked little-endian reader over the immutable ROM bytes.

    The reader also carries the profile whose extents it resolves, so no table
    address or count is a module constant here. `profile_authority` supplies the
    packaged catalog's entry for the image this stack was verified against;
    every address and bound below is read from it, which is what makes the
    declaration the single owner of these facts instead of a literal beside it.
    """

    __slots__ = ("data", "size", "_profile", "_graphics")

    def __init__(self, data: bytes, *, profile: "RomProfile | None" = None) -> None:
        if not isinstance(data, (bytes, bytearray)):
            raise CanonicalError("ROM must be bytes")
        self.data = bytes(data)
        self.size = len(self.data)
        self._profile = profile
        self._graphics: "_mg.MapGraphicsReader | None" = None

    @property
    def profile(self) -> "RomProfile":
        """The profile this reader resolves addresses against."""
        if self._profile is None:
            self._profile = profile_authority.canonical_export_profile()
        return self._profile

    @property
    def identity(self) -> "AtlasIdentity":
        """The base image this reader's extents describe."""
        return self.profile.identity

    def graphics_reader(self) -> "_mg.MapGraphicsReader":
        """This image as the shared map/graphics reader, under this profile.

        The export path's container contract is the *strict* one - the packed
        stream's own end marker must fall at its declared size - so it is injected
        here rather than fixed in the shared reader. That is the one policy the
        two stacks still hold differently, and it is a check on the stream rather
        than a second reading of the map format.
        """
        if self._graphics is None:
            self._graphics = _mg.MapGraphicsReader(
                self.data, self.profile, decode=self._strict_decode
            )
        return self._graphics

    @staticmethod
    def _strict_decode(data: bytes, offset: int, *, expected: int | None = None):
        """Every container the export path reads must reach its own end marker."""
        container = ws.unpack(data, offset, require_end_marker=True)
        if expected is not None and len(container.data) != expected:
            raise CanonicalError(
                f"container at {offset:#x} decoded {len(container.data):#x} bytes, "
                f"expected {expected:#x}"
            )
        return container

    def map_entry_count(self) -> int:
        """This profile's declared MapEntry count: the live index bound."""
        table = self.profile.map_entries
        if table is None:
            raise CanonicalError(
                f"profile {self.profile.id!r} declares no map_entries table"
            )
        return table.count

    def map_entry_table_address(self) -> int:
        table = self.profile.map_entries
        if table is None:
            raise CanonicalError(
                f"profile {self.profile.id!r} declares no map_entries table"
            )
        return table.address.raw

    def map_entry_stride(self) -> int:
        table = self.profile.map_entries
        if table is None:
            raise CanonicalError(
                f"profile {self.profile.id!r} declares no map_entries table"
            )
        return table.record_size

    def text_table(self) -> "TextTableProfile":
        """This profile's declared text pointer table: address, count and pool."""
        table = self.profile.text_strings
        if table is None:
            raise CanonicalError(
                f"profile {self.profile.id!r} declares no text_strings table"
            )
        return table

    def object_palette_address(self) -> int:
        """The profile-declared OAM palette address."""
        sprites = self.profile.actor_sprites
        if sprites is None:
            raise CanonicalError(
                f"profile {self.profile.id!r} declares no actor_sprites palette"
            )
        return sprites.object_palette_address.raw

    def bg_palette_address(self) -> int:
        """The profile-declared engine-global background palette address."""
        sprites = self.profile.actor_sprites
        if sprites is None:
            raise CanonicalError(
                f"profile {self.profile.id!r} declares no actor_sprites palette"
            )
        return sprites.bg_palette_address.raw

    def sprite_definition_run_address(self) -> int:
        sprites = self.profile.actor_sprites
        if sprites is None:
            raise CanonicalError(
                f"profile {self.profile.id!r} declares no "
                f"actor_sprites.character_table_address"
            )
        return sprites.character_table_address.raw

    def appearance_table_address(self) -> int:
        table = self.profile.appearances
        if table is None:
            raise CanonicalError(
                f"profile {self.profile.id!r} declares no appearances.address"
            )
        return table.address.raw

    def offset(self, address: int) -> int:
        return to_file_offset(address, self.size)

    def span(self, address: int, length: int) -> int:
        offset = self.offset(address)
        if length < 0 or offset + length > self.size:
            raise CanonicalError(
                f"{length:#x} bytes at {address:#010x} run past the image"
            )
        return offset

    def u8(self, address: int) -> int:
        return self.data[self.offset(address)]

    def s8(self, address: int) -> int:
        return signed_byte(self.data[self.offset(address)])

    def u16(self, address: int) -> int:
        return struct.unpack_from("<H", self.data, self.span(address, 2))[0]

    def u32(self, address: int) -> int:
        return struct.unpack_from("<I", self.data, self.span(address, 4))[0]

    def bytes_at(self, address: int, length: int) -> bytes:
        offset = self.span(address, length)
        return self.data[offset : offset + length]

    def container(self, address: int) -> ws.Container:
        """Strictly decode the container at ``address``.

        The export path always requires the packed stream's own end marker to fall
        at its declared size. `LOGX-CODEC-001` measured that on every reachable
        canonical container it does, so the check costs nothing and turns "the
        decode produced the right number of bytes" into "the decode consumed the
        stream the header describes".
        """
        return ws.unpack(
            self.data, self.offset(address), require_end_marker=True
        )

    def container_payload(self, address: int) -> bytes:
        return self.container(address).data

    def in_image(self, address: int) -> bool:
        return ws.GBA_ROM_BASE <= address < ws.GBA_ROM_BASE + self.size

    def text(self, index: int) -> str | None:
        """The ROM string a text-table index resolves to, or ``None``.

        The pointer table and its UTF-16LE NUL-terminated pool are the accepted
        text structures; only the resolution is performed here, and an index
        that does not resolve returns ``None`` rather than being guessed at.

        The index bound and the table address are the profile's declaration, read
        by the shared reader rather than held as a module constant: that bound
        decides which indices a MapEntry label resolves through, so a stale copy
        of it would silently read the wrong slot or refuse a valid one.
        """
        return self.graphics_reader().text(index)


# --- map side ----------------------------------------------------------------
#
# The record TYPES are the format layer's. `MapEntry`, `LayerRecord`,
# `AnimatedTileSource`, `CharBlock` and `Bank` are aliases of
# `tools.webfoot.formats.map_graphics`'s dataclasses rather than second
# definitions of the same fields: a reader that returned a lookalike record would
# let a new field live in one copy only, which is the defect this ticket closed.
# The methods below are the export-facing spellings of the shared readers, kept
# so the exporter's call sites and their evidence labels do not move.

MapEntry = _mg.MapEntry
LayerRecord = _mg.LayerRecord
AnimatedTileSource = _mg.AnimatedTileSource
CharBlock = _mg.CharBlock
Bank = _mg.Bank


def _shared(operation):
    """Run a shared map/graphics read, re-raising a refusal in this family."""
    try:
        return operation()
    except _mg.MapGraphicsError as exc:
        raise CanonicalError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class SelectorStream:
    """The decoded selector stream, as the export path reports it."""

    address: int
    selectors: tuple[int, ...]


def read_map_entries(rom: Rom) -> tuple[MapEntry, ...]:
    """Read every MapEntry record this profile declares and resolve its root.

    The count, base address and stride all come from the profile through the
    reader, so a profile that declares a different table is enumerated at its
    own extent rather than at Buu's. The record read is the shared one
    (`map_graphics.read_map_entries`), which reads the fields through the
    physical layout `formats.map_entry` owns.
    """
    return _shared(lambda: _mg.read_map_entries(rom.graphics_reader()))


def read_layer(rom: Rom, root_address: int, slot: int) -> LayerRecord:
    """Read one of a root's four layer slots at the accepted offsets.

    The dominant form states its chunk grid at `+0x14`/`+0x15` and its chunk
    window at `+0x18`. The terrain-field form states its cell grid at
    `+0x04`/`+0x05` and its container run at `+0x08`, so its grid is read from
    there and the dominant fields are left alone rather than filled with the
    unrelated bytes those offsets happen to hold. Both forms are read by the
    shared reader.
    """
    return _shared(
        lambda: _mg.read_layer(rom.graphics_reader(), root_address, slot)
    )


def read_layers(rom: Rom, root_address: int) -> tuple[LayerRecord, ...]:
    return _shared(lambda: _mg.read_layers(rom.graphics_reader(), root_address))


def read_chunk_entries(rom: Rom, address: int) -> tuple[int, ...]:
    """Decode a dominant chunk container into 1024 little-endian u16 entries."""
    return _shared(
        lambda: _mg.dominant_chunk_words(rom.graphics_reader(), address)
    )


def read_selector_stream(rom: Rom, root_address: int) -> tuple[int, ...]:
    """Decode ``root + 0x48`` into absolute ``bank:tile`` selectors.

    Entry zero is absolute; every later little-endian u16 is a delta from the
    preceding absolute selector, biased by one, wrapping to u16 exactly as the
    engine's own prefix-decode loop does.
    """
    stream = _shared(
        lambda: _mg.decode_selector_stream(rom.graphics_reader(), root_address)
    )
    return stream.selectors


def read_selector_stream_record(rom: Rom, root_address: int) -> SelectorStream:
    """The selector stream with the container address that carried it."""
    stream = _shared(
        lambda: _mg.decode_selector_stream(rom.graphics_reader(), root_address)
    )
    return SelectorStream(address=stream.address, selectors=stream.selectors)


def read_animated_tiles(rom: Rom, root_address: int) -> tuple[AnimatedTileSource, ...]:
    """Read the animated-tile records and decode their first frame.

    The accepted root pair at `+0x0C`/`+0x10` is a count and a null-coupled
    pointer; the record layout below the count and the headerless packed frame
    are read by the shared reader, so the export no longer restates a shape the
    SDK renderer also decodes.
    """
    return _shared(
        lambda: _mg.read_animated_tiles(rom.graphics_reader(), root_address)
    )


def assemble_char_block(
    rom: Rom,
    selectors: tuple[int, ...],
    animated: tuple[AnimatedTileSource, ...],
    bank_table_address: int,
) -> CharBlock:
    """Assemble character data: selector ordinal -> tile, animated tiles overlaid.

    A selector writes exactly one 8x8 tile to character memory at
    `64 * ordinal`; an animated-tile record writes `tile_count` tiles starting at
    its own destination ordinal. Both come from the engine's own loaders.
    ``bank_table_address`` is the value stored at `root + 0x4C` - the table of
    bank *container pointers*, so a bank index is dereferenced through it before
    the container is decoded. The assembly itself is the shared one; the exporter
    does not pass ``require_referenced``, because reporting uncovered ordinals is
    the renderer's refusal, not an export requirement.
    """
    return _shared(
        lambda: _mg.assemble_char_block(
            rom.graphics_reader(), selectors, animated, bank_table_address
        )
    )


def assemble_map_char_block(
    rom: Rom, root_address: int
) -> tuple[CharBlock, tuple[int, ...], tuple[AnimatedTileSource, ...]]:
    """Assemble a map's character block from its own root."""
    block, stream, animated = _shared(
        lambda: _mg.assemble_map_char_block(rom.graphics_reader(), root_address)
    )
    return block, stream.selectors, animated


def read_banks(
    rom: Rom,
    table_address: int = BANK_TABLE_ADDRESS,
    count: int = BANK_COUNT,
) -> tuple[Bank, ...]:
    """Read the bank table and decode every bank container.

    ``table_address`` defaults to the canonical graph's own root value so this
    catalogue keeps one call shape; every other caller reads the field from the
    root it is walking.
    """
    return _shared(
        lambda: _mg.read_banks(rom.graphics_reader(), table_address, count)
    )


# --- sprite side -------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class SpriteDefinition:
    """One sprite-definition object and its count-bounded animation array."""

    sprite_id: int
    run_index: int
    address: int
    animation_count: int
    animation_pointers: tuple[int, ...]
    extent_end: int

    @property
    def slots(self) -> int:
        return len(self.animation_pointers)

    @property
    def non_null_slots(self) -> int:
        return sum(1 for pointer in self.animation_pointers if pointer)


def read_sprite_definitions(rom: Rom) -> tuple[SpriteDefinition, ...]:
    """Read the 297-entry pointer run as logical sprite ids 10..306.

    The array is bounded by the definition's own `+0x00` low byte. The superseded
    fixed 23-slot model is not reachable from this function: the superseded walk
    form is replaced by `[+0x54, +0x54 + 4 * count)` and nothing else.
    """
    definitions: list[SpriteDefinition] = []
    base = rom.sprite_definition_run_address()
    for run_index in range(SPRITE_DEFINITION_COUNT):
        address = rom.u32(base + run_index * 4)
        count = rom.u8(address + SPRITE_DEFINITION_COUNT_OFFSET)
        high = rom.u8(address + SPRITE_DEFINITION_COUNT_OFFSET + 1)
        if high != 0:
            raise CanonicalError(
                f"definition at {address:#010x} has a non-zero count high byte "
                f"{high:#04x}"
            )
        pointers = tuple(
            rom.u32(address + SPRITE_ANIMATION_ARRAY_OFFSET + index * 4)
            for index in range(count)
        )
        definitions.append(
            SpriteDefinition(
                sprite_id=SPRITE_ID_FLOOR + run_index,
                run_index=run_index,
                address=address,
                animation_count=count,
                animation_pointers=pointers,
                extent_end=address + SPRITE_ANIMATION_ARRAY_OFFSET + count * 4,
            )
        )
    return tuple(definitions)


@dataclass(frozen=True, slots=True)
class AnimationRecord:
    """One animation object: a frame count and four cells per frame row."""

    address: int
    frame_count: int
    cell_addresses: tuple[int, ...]

    @property
    def direction_cells(self) -> int:
        return len(self.cell_addresses)

    def cell_address(self, frame_index: int, direction_index: int) -> int:
        if not 0 <= frame_index < self.frame_count:
            raise CanonicalError(f"frame index {frame_index} is out of range")
        if not 0 <= direction_index < DIRECTION_COUNT:
            raise CanonicalError(f"direction index {direction_index} is out of range")
        return self.cell_addresses[frame_index * DIRECTION_COUNT + direction_index]


def read_animation(rom: Rom, address: int) -> AnimationRecord:
    """Read an animation object at the accepted cell layout."""
    frame_count = rom.u32(address + ANIMATION_FRAME_COUNT_OFFSET)
    if not ANIMATION_FRAME_COUNT_MIN <= frame_count <= ANIMATION_FRAME_COUNT_MAX:
        raise CanonicalError(
            f"animation at {address:#010x} declares {frame_count} frames, outside "
            f"{ANIMATION_FRAME_COUNT_MIN}..{ANIMATION_FRAME_COUNT_MAX}"
        )
    cells = tuple(
        rom.u32(
            address
            + ANIMATION_CELLS_OFFSET
            + frame * ANIMATION_ROW_BYTES
            + direction * ANIMATION_CELL_BYTES
        )
        for frame in range(frame_count)
        for direction in range(DIRECTION_COUNT)
    )
    if any(cell == 0 for cell in cells):
        raise CanonicalError(f"animation at {address:#010x} has a null cell")
    return AnimationRecord(address=address, frame_count=frame_count, cell_addresses=cells)


@dataclass(frozen=True, slots=True)
class PieceRecord:
    """One 12-byte piece record."""

    index: int
    address: int
    x: int
    y: int
    dim_0: int
    dim_1: int
    attributes: int
    graphics_address: int

    @property
    def colour_256(self) -> bool:
        return bool(self.attributes & ATTR0_COLOUR_256)

    @property
    def shape(self) -> int:
        return (self.attributes & 0xFFFF) >> ATTR0_SHAPE_SHIFT & 3

    @property
    def size(self) -> int:
        return (self.attributes >> 16) >> ATTR1_SIZE_SHIFT & 3

    @property
    def horizontal_flip(self) -> bool:
        return bool((self.attributes >> 16) & ATTR1_HORIZONTAL_FLIP)

    @property
    def vertical_flip(self) -> bool:
        return bool((self.attributes >> 16) & ATTR1_VERTICAL_FLIP)

    @property
    def oam_dimensions(self) -> tuple[int, int]:
        if self.shape >= len(OBJECT_DIMENSIONS):
            raise CanonicalError(
                f"piece at {self.address:#010x} uses reserved OAM shape {self.shape}"
            )
        return OBJECT_DIMENSIONS[self.shape][self.size]


@dataclass(frozen=True, slots=True)
class FrameRecord:
    """One frame record: an 8-byte header and its pieces."""

    address: int
    piece_count: int
    min_x: int
    min_y: int
    width: int
    height: int
    pieces: tuple[PieceRecord, ...]


def read_frame(rom: Rom, address: int) -> FrameRecord:
    """Read a frame record at the accepted layout."""
    count = rom.u32(address + FRAME_PIECE_COUNT_OFFSET)
    if not 1 <= count <= FRAME_MAX_PIECES:
        raise CanonicalError(
            f"frame at {address:#010x} declares {count} pieces, outside "
            f"1..{FRAME_MAX_PIECES}"
        )
    rom.span(address, FRAME_HEADER_SIZE + count * PIECE_RECORD_SIZE)
    pieces: list[PieceRecord] = []
    for index in range(count):
        base = address + FRAME_HEADER_SIZE + index * PIECE_RECORD_SIZE
        pieces.append(
            PieceRecord(
                index=index,
                address=base,
                x=rom.s8(base + PIECE_X_OFFSET),
                y=rom.s8(base + PIECE_Y_OFFSET),
                dim_0=rom.u8(base + PIECE_DIM_0_OFFSET),
                dim_1=rom.u8(base + PIECE_DIM_1_OFFSET),
                attributes=rom.u32(base + PIECE_ATTRIBUTES_OFFSET),
                graphics_address=rom.u32(base + PIECE_GRAPHICS_OFFSET),
            )
        )
    return FrameRecord(
        address=address,
        piece_count=count,
        min_x=rom.s8(address + FRAME_MIN_X_OFFSET),
        min_y=rom.s8(address + FRAME_MIN_Y_OFFSET),
        width=rom.u8(address + FRAME_WIDTH_OFFSET),
        height=rom.u8(address + FRAME_HEIGHT_OFFSET),
        pieces=tuple(pieces),
    )


@dataclass(frozen=True, slots=True)
class GraphicContainer:
    """One structured sprite-graphics container."""

    address: int
    declared_size: int
    packed_bytes: int
    width: int
    height: int
    colour_256: bool
    payload: bytes


def read_graphic(rom: Rom, address: int, width: int, height: int,
                 colour_256: bool) -> GraphicContainer:
    """Decode a graphics container and verify it against the piece's extents.

    The declared decoded length and the piece's independently stored extents
    agreeing is the structural verification that makes the word a graphics
    reference rather than a coincidence; it holds on all 11,005 canonical
    pieces, so a mismatch here is an error and never a silent substitution.
    """
    container = rom.container(address)
    expected = width * height if colour_256 else (width * height) // 2
    if container.declared_size != expected:
        raise CanonicalError(
            f"graphics container at {address:#010x} declares "
            f"{container.declared_size} bytes but its piece declares "
            f"{width}x{height} at {8 if colour_256 else 4}bpp ({expected} bytes)"
        )
    return GraphicContainer(
        address=address,
        declared_size=container.declared_size,
        packed_bytes=container.packed_end - container.offset,
        width=width,
        height=height,
        colour_256=colour_256,
        payload=container.data,
    )
