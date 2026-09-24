"""Canonical readers for the accepted Buu's Fury resource graph.

ASSET-EXPORT-001. This module is the export-side, read-only implementation of the
post-LOGX accepted schemas. It exists because the production readers in
`tools.webfoot` still carry the *refuted* sprite/frame layout that the
`LOGX-SYNTHESIS-001` closeout inventoried and explicitly deferred to the
`FIX-*` tickets, and because `map_render`'s assembly path fails closed on layer
records the export must classify rather than abandon.

**What is accepted, and where it comes from.** Every offset used here is the
accepted schema in `docs/research/LOGX_SYNTHESIS.md` (§3 map/world, §7 sprite
definitions, §8 animation/frame/piece, §2.5 codec). Nothing here is derived from
`LOGExtractor`'s superseded readings, and the refuted model is not reachable
from this module:

* the superseded fixed 23-slot animation model is not used; the array is bounded
  by definition `+0x00`;
* the refuted 4-byte frame header and 16-byte piece stride are not used; the
  frame header is `0x08` bytes and pieces are `0x0C` bytes at `frame + 0x08`;
* the piece attribute pair is read at `+0x04` and the graphics word at `+0x08`,
  not at `+0x08`/`+0x0C`;
* tile-entry bits 12..15 are recorded raw and never explained;
* a layer `+0x00` word is a **Thumb handler entry**, never a numeric type tag.

Offsets are read through :class:`Rom`, which bounds-checks every access against
the image, so a misread address fails loudly instead of wrapping.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import TYPE_CHECKING

from tools.webfoot.formats import map_entry as _me
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

#: The MapEntry record shape is the format's, owned by `webfoot.formats.map_entry`
#: and re-exported here so this module's callers keep one import site. The TABLE
#: address and its record COUNT are the profile's declarations and are read
#: through `Rom.map_entry_table_address()` / `Rom.map_entry_count()`; they are
#: deliberately not restated as module constants (CQA-15).
MAP_ENTRY_STRIDE = _me.MAP_ENTRY_SIZE

#: One pointer-table entry is one little-endian GBA address. The width is a
#: format fact and comes from the codec, so this module does not spell it "4".
TEXT_POINTER_SIZE = _tt.TEXT_POINTER_SIZE

#: MapEntry fields the accepted discovery route uses.
MAP_ENTRY_KEY_OFFSET = 0x00        # two ordered key bytes
MAP_ENTRY_TEXT_OFFSET = 0x0C       # u32; low half indexes the text pointer table
MAP_ENTRY_SOURCE_OFFSET = 0x2C     # u32; indexed-word source (selector 1 = word[0])

#: Map root (the load-time definition template) fields.
ROOT_LAYER_SLOTS = (0x14, 0x18, 0x1C, 0x20)
#: Four bytes the engine adds to `BG0CNT..BG3CNT`, one per slot. The arithmetic
#: is CONFIRMED; the per-slot assignment is PARTIALLY CONFIRMED, and the accepted
#: renderer uses the byte as a draw-order key. The exporter records it as the
#: addend rather than promoting it to a semantic "priority".
ROOT_BG_ADDEND_OFFSET = 0x04
ROOT_EXTENT_X_OFFSET = 0x08        # ldrh, extent stored as extent - 1
ROOT_EXTENT_Y_OFFSET = 0x0A
ROOT_SELECTOR_STREAM_OFFSET = 0x48
ROOT_BANK_TABLE_OFFSET = 0x4C
ROOT_CONNECTION_COUNT_OFFSET = 0x40
ROOT_CONNECTION_ARRAY_OFFSET = 0x44
ROOT_BG_CONTROL_OFFSET = 0x3C
ROOT_ANIMATED_COUNT_OFFSET = 0x0C
ROOT_ANIMATED_ARRAY_OFFSET = 0x10

#: Layer-record fields for the dominant form.
LAYER_HANDLER_OFFSET = 0x00
LAYER_CHUNK_X_OFFSET = 0x14        # unsigned chunk-grid X count
LAYER_CHUNK_Y_OFFSET = 0x15        # unsigned chunk-grid Y count
LAYER_CHUNK_WINDOW_OFFSET = 0x18   # chunk-pointer window, 4-byte elements

#: The five accepted layer `+0x00` handler values.
DOMINANT_LAYER_HANDLER = 0x08008087
ABSENT_LAYER_HANDLER = 0x08007A41
ABSENT_LAYER_RECORD = 0x080707FC

#: Handlers whose layer is a 32x32 screen-entry plane, mapped to the record field
#: that names its container. Both carry 1024 little-endian screen entries =
#: 0x800 decoded bytes, the same form a dominant chunk carries, but they reach
#: it by different code:
#:
#: * `0x08007B63` - tail-branch stub `0x08007B62` into constructor `0x08007A60`,
#:   which decompresses `record + 0x04` (and `record + 0x08`, the same container
#:   on the canonical record) into the object's own buffers.
#: * `0x0800897B` - constructor `0x0800897A` builds only a twelve-byte marker
#:   holding the type word, the slot byte and the record pointer. The plane is
#:   uploaded later by method 1 of that type's descriptor: `0x080088E6` reads
#:   `record + 0x1C`, decompresses it into a 0x800-byte buffer and copies it to
#:   `0x0600E000 + slot * 0x800`. Method 2 (`0x08008924`) then programs
#:   `BGxHOFS`/`BGxVOFS` at `0x04000010 + 4*slot` from the record's `+0x04`,
#:   `+0x0C`, `+0x10`, `+0x14`, `+0x18` and a viewport object.
#:
#: So neither handler is a marker without pixels: both name a screen-entry plane
#: and both are static graphical layers.
SCREENBLOCK_HANDLERS: dict[int, int] = {
    0x08007B63: 0x04,
    0x0800897B: 0x1C,
}
#: Same form as a dominant chunk: 1024 little-endian screen entries = 0x800
#: decoded bytes = 32x32 tiles = 256x256 pixels. Declared again here rather than
#: aliased so the constants block stays readable in one forward pass.
SCREENBLOCK_ENTRY_COUNT = 1024
SCREENBLOCK_DECODED_BYTES = 0x800
SCREENBLOCK_PIXELS = 256

#: Entry `0x080088BC` -> constructor `0x080080C0`: enables `REG_IE` bit 1
#: (`0x04000200 |= 2`, the HBlank interrupt - not `DISPSTAT`, which is
#: `0x04000004`) and clears `BG2PB`/`BG2PD`, then streams `record + 4` x
#: `record + 5` containers of `0x400` decoded bytes through a nine-slot resident
#: cache. ASSET-EXPORT-MAP19-001 recovered what those containers hold: a 32x32
#: plane of **8-bit tile ordinals** - 32 ordinals per raster row, one byte per
#: ordinal, 1024 ordinals per container - which the map's own assembled character
#: block resolves. The ordinal reading is established by the payload's semantics,
#: not by its shape: each ordinal consistently selects tiles of one kind, so
#: ordinal 2 selects a tile that is 100 % water, 43 and 119 green land, 137 sand,
#: 76/73 rock and 19 snow, while the same measurement over a permuted ordinal
#: assignment destroys the correspondence. `record + 0x04` x `record + 0x05`
#: containers lay out in raster order, container `y * grid_x + x` covering the
#: 32x32-tile cell at `(x * 32, y * 32)`.
TERRAIN_FIELD_LAYER_HANDLER = 0x080088BD
TERRAIN_FIELD_GRID_X_OFFSET = 0x04
TERRAIN_FIELD_GRID_Y_OFFSET = 0x05
TERRAIN_FIELD_CONTAINER_OFFSET = 0x08
TERRAIN_FIELD_CELL_BYTES = 0x400
TERRAIN_FIELD_CELL_TILES = 32
TERRAIN_FIELD_TILE_ORDINAL_MASK = 0xFF
TERRAIN_FIELD_RESIDENT_SLOTS = 9

#: Chunk payload: 32 x 32 little-endian u16 entries = 1024 entries = 2048 bytes.
CHUNK_SIDE_TILES = 32
CHUNK_ENTRY_COUNT = CHUNK_SIDE_TILES * CHUNK_SIDE_TILES
CHUNK_DECODED_BYTES = CHUNK_ENTRY_COUNT * 2

#: The tile unit is 8x8 pixels, so a chunk covers 256x256 pixels.
TILE_PIXELS = 8
CHUNK_PIXELS = CHUNK_SIDE_TILES * TILE_PIXELS

#: Tile-entry bit fields the accepted corpus establishes.
TILE_ENTRY_ORDINAL_MASK = 0x03FF   # bits 0..9
TILE_ENTRY_BIT_10 = 0x0400         # present and used; "horizontal flip" partial
TILE_ENTRY_BIT_11 = 0x0800         # as bit 10
TILE_ENTRY_HIGH_NIBBLE = 0xF000    # bits 12..15: reserved/constant in canonical data

#: Bank table: 187 consecutive aligned pointers, every one a container.
BANK_TABLE_ADDRESS = 0x08179764
BANK_COUNT = 187
#: A bank's addressed tile capacity under the selector's 8-bit tile field.
BANK_TILE_BYTES = 64

#: The absent-layer placeholder's substitute container. It is a stored container
#: declaring zero bytes, so substituting it and skipping it both write no pixels.
DEFAULT_CHUNK_CONTAINER = 0x08070808

#: Engine-global background palette: 256 RGB888 triples, uncompressed.
BG_PALETTE_ADDRESS = 0x080701B0
BG_PALETTE_ENTRIES = 256
BG_PALETTE_BYTES = BG_PALETTE_ENTRIES * 3

#: Sprite-definition pointer run: 297 entries, logical ids 10..306.
SPRITE_DEFINITION_RUN = 0x086B6BDC
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
APPEARANCE_TABLE_ADDRESS = 0x0874D380
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
    for index in range(APPEARANCE_COUNT):
        address = APPEARANCE_TABLE_ADDRESS + index * APPEARANCE_STRIDE
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
    """The record field a screen-entry layer's handler reads its container from."""
    try:
        return SCREENBLOCK_HANDLERS[handler]
    except KeyError:
        raise CanonicalError(
            f"handler {handler:#010x} is not a screen-entry layer handler"
        ) from None


def read_screenblock_entries(rom: Rom, record_address: int) -> tuple[int, ...]:
    """Read the screen-entry plane a screen-entry layer's handler decompresses.

    Two handlers carry the same 32x32 plane and reach it by different code, so
    the container field is taken from the record's own `+0x00` word:

    * `0x08007B63` - constructor `0x08007A60` decompresses `record + 0x04` into
      the object's first 0x800-byte buffer (`record + 0x08` into its second; on
      the canonical record the two name the same container).
    * `0x0800897B` - the constructor builds only a marker, and method 1 of the
      type's descriptor (`0x080088E6`) decompresses `record + 0x1C` into a
      0x800-byte buffer and copies it to `0x0600E000 + slot * 0x800`.

    The payload is 1024 little-endian screen entries either way, which is why the
    exporter renders both through the existing screen-entry renderer.
    """
    handler = rom.u32(record_address)
    offset = screenblock_container_offset(handler)
    container_address = rom.u32(record_address + offset)
    container = rom.container(container_address)
    if container.declared_size != SCREENBLOCK_DECODED_BYTES:
        raise CanonicalError(
            f"screen-entry layer at {record_address:#010x} (handler "
            f"{handler:#010x}, field +{offset:#04x}) names a container declaring "
            f"{container.declared_size} bytes, expected {SCREENBLOCK_DECODED_BYTES}"
        )
    return struct.unpack("<1024H", container.data)


def read_terrain_field_cells(rom: Rom, record_address: int) -> tuple[bytes, ...]:
    """Read a `0x080088BD` record's container payloads in its own raster order.

    The record states its cell grid at `+0x04`/`+0x05` and names
    `grid_x * grid_y` consecutive container pointers from `+0x08`. The pointer run
    is exactly that long on the canonical record, so a shorter run is a
    structural mismatch rather than something to silently pad.

    An empty grid (either dimension zero) is an empty field: the engine's own
    constructor skips the eager load when the product is not positive.
    """
    grid_x = rom.u8(record_address + TERRAIN_FIELD_GRID_X_OFFSET)
    grid_y = rom.u8(record_address + TERRAIN_FIELD_GRID_Y_OFFSET)
    cells = grid_x * grid_y
    if cells == 0:
        return ()
    payloads: list[bytes] = []
    for index in range(cells):
        address = rom.u32(
            record_address + TERRAIN_FIELD_CONTAINER_OFFSET + index * 4
        )
        if not rom.in_image(address):
            raise CanonicalError(
                f"terrain-field record at {record_address:#010x} names container "
                f"{index} at {address:#010x}, which is outside the image"
            )
        payloads.append(rom.container(address).data)
    return tuple(payloads)


def read_terrain_field_containers(rom: Rom, record_address: int) -> tuple[int, ...]:
    """The container addresses a `0x080088BD` record names, in raster order."""
    grid_x = rom.u8(record_address + TERRAIN_FIELD_GRID_X_OFFSET)
    grid_y = rom.u8(record_address + TERRAIN_FIELD_GRID_Y_OFFSET)
    targets: list[int] = []
    for index in range(grid_x * grid_y):
        address = rom.u32(
            record_address + TERRAIN_FIELD_CONTAINER_OFFSET + index * 4
        )
        if not rom.in_image(address):
            raise CanonicalError(
                f"terrain-field record at {record_address:#010x} names container "
                f"{index} at {address:#010x}, which is outside the image"
            )
        targets.append(address)
    return tuple(targets)


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

    __slots__ = ("data", "size", "_profile")

    def __init__(self, data: bytes, *, profile: "RomProfile | None" = None) -> None:
        if not isinstance(data, (bytes, bytearray)):
            raise CanonicalError("ROM must be bytes")
        self.data = bytes(data)
        self.size = len(self.data)
        self._profile = profile

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

        The index bound and the table address are the profile's declaration,
        read here rather than held as a module constant: this bound decides
        which indices a MapEntry label resolves through, so a stale copy of it
        would silently read the wrong slot or refuse a valid one.
        """
        table = self.text_table()
        if not 0 <= index < table.count:
            return None
        pointer_address = table.pointer_table_address.raw + index * TEXT_POINTER_SIZE
        try:
            address = self.u32(pointer_address)
        except CanonicalError:
            return None
        if not self.in_image(address):
            return None
        offset = self.offset(address)
        end = offset
        while end + 1 < self.size:
            if self.data[end] == 0 and self.data[end + 1] == 0:
                break
            end += 2
        else:
            return None
        try:
            return self.data[offset:end].decode("utf-16-le")
        except UnicodeDecodeError:
            return None


# --- map side ----------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class MapEntry:
    """One accepted MapEntry record."""

    index: int
    address: int
    key_high: int
    key_low: int
    text_index: int | None
    source_address: int
    root_address: int


@dataclass(frozen=True, slots=True)
class LayerRecord:
    """One layer record reached from a map root's four slots."""

    slot: int
    address: int
    handler: int
    chunk_x: int
    chunk_y: int
    chunk_addresses: tuple[int, ...]
    null_chunk_count: int
    #: The cell grid a terrain-field record states at its own `+0x04`/`+0x05`.
    #: Held separately from `chunk_x`/`chunk_y` because on this record form those
    #: two offsets carry unrelated bytes; see `read_layer`.
    terrain_x: int = 0
    terrain_y: int = 0

    @property
    def chunk_cells(self) -> int:
        return self.chunk_x * self.chunk_y

    @property
    def terrain_cells(self) -> int:
        return self.terrain_x * self.terrain_y

    @property
    def terrain_tiles_x(self) -> int:
        """Tile columns of a terrain-field record: `cell_tiles * grid_x`."""
        return self.terrain_x * TERRAIN_FIELD_CELL_TILES

    @property
    def terrain_tiles_y(self) -> int:
        """Tile rows of a terrain-field record: `cell_tiles * grid_y`."""
        return self.terrain_y * TERRAIN_FIELD_CELL_TILES

    @property
    def terrain_pixels_x(self) -> int:
        """Pixel width of a terrain-field record: `terrain_tiles_x * 8`."""
        return self.terrain_tiles_x * TILE_PIXELS

    @property
    def terrain_pixels_y(self) -> int:
        """Pixel height of a terrain-field record: `terrain_tiles_y * 8`."""
        return self.terrain_tiles_y * TILE_PIXELS

    @property
    def terrain_grid_x(self) -> int:
        """Cell-grid X count of a terrain-field record.

        A terrain-field record states its grid at `+0x04`/`+0x05`, not at the
        dominant form's `+0x14`/`+0x15`, so on this record form the dominant
        chunk-grid fields carry unrelated bytes and are not published as a grid.
        """
        return self.terrain_x

    @property
    def terrain_grid_y(self) -> int:
        """Cell-grid Y count of a terrain-field record; see `terrain_grid_x`."""
        return self.terrain_y

    @property
    def classification(self) -> str:
        """The structural class of this record, named by handler.

        The names are structural, not semantic. `dominant` is the accepted
        chunk-grid form and `absent_placeholder` is the shared zero-dimension
        record an unused slot points at. The three remaining handlers are
        classified by what their own code does, which ASSET-EXPORT-MAP-
        HANDLERS-001 established from the engine's instructions:

        * `static_graphical_screenblock` (`0x08007B63` and `0x0800897B`): both
          name a 0x800-byte container holding 1024 little-endian screen entries,
          the same 32x32 form a dominant chunk carries. `0x08007B63`'s
          constructor decompresses `record + 0x04` into the object's own buffer;
          `0x0800897B`'s constructor builds only a twelve-byte marker and the
          plane is uploaded by method 1 of its type's descriptor, `0x080088E6`,
          from `record + 0x1C` to `0x0600E000 + slot * 0x800`. Both are static
          graphical layers and both render as a 256x256 screen-entry plane.
        * `static_graphical_terrain_field` (`0x080088BD`): the constructor
          programs background registers and streams `record + 4` x `record + 5`
          containers of 0x400 decoded bytes each through a nine-slot resident
          cache. ASSET-EXPORT-MAP19-001 recovered what they hold, so the layer is
          renderable: each container is a 32x32 plane of 8-bit tile ordinals that
          resolve through the owning map's assembled character block, and the
          containers lay out in raster order.
        """
        if self.handler == DOMINANT_LAYER_HANDLER:
            if self.chunk_x == 0 and self.chunk_y == 0:
                return "dominant_zero_grid"
            if self.chunk_x == 0 or self.chunk_y == 0:
                return "dominant_partial_zero_grid"
            return "dominant"
        if self.handler == ABSENT_LAYER_HANDLER and self.address == ABSENT_LAYER_RECORD:
            return "absent_placeholder"
        if self.handler in SCREENBLOCK_HANDLERS:
            return "static_graphical_screenblock"
        if self.handler == TERRAIN_FIELD_LAYER_HANDLER:
            return "static_graphical_terrain_field"
        return "unclassified_handler"

    @property
    def renderable(self) -> bool:
        """Whether this exporter can render the slot to a deterministic image."""
        return self.classification in (
            "dominant",
            "static_graphical_screenblock",
            "static_graphical_terrain_field",
        )

    @property
    def resolved(self) -> bool:
        """Whether the record form this slot carries is established.

        A handler outside the ones the engine's own instructions account for, and
        a dominant record whose grid has a zero dimension, are classed but not
        understood. Their being unclassifiable is not evidence that the slot draws
        nothing, so a composite is refused for them rather than assembled from a
        record the exporter has not accounted for.
        """
        return self.classification not in (
            "unclassified_handler",
            "dominant_zero_grid",
            "dominant_partial_zero_grid",
        )

    @property
    def graphical(self) -> bool:
        """Whether the engine evidence establishes this slot draws pixels.

        `absent_placeholder` is the only class established as drawing nothing: it
        is a zero-dimension record with no payload. The dominant, screenblock and
        terrain-field classes all draw - the first two through a decompressed
        screen-entry plane, the last through background-register programming and a
        streaming terrain-field cache. An unclassified class establishes neither,
        so this is false for it without asserting that it draws nothing.
        """
        return self.classification in (
            "dominant",
            "static_graphical_screenblock",
            "static_graphical_terrain_field",
        )

    @property
    def blocks_composite(self) -> bool:
        """Whether this slot prevents a faithful static composite.

        A slot that draws nothing cannot make a composite unfaithful. A graphical
        slot whose pixels this exporter cannot assemble does. A slot whose record
        form is not established does too: unknown means unknown, so the composite
        is withheld rather than assembled from an unaccounted record.
        """
        return not self.resolved or (self.graphical and not self.renderable)


def read_map_entries(rom: Rom) -> tuple[MapEntry, ...]:
    """Read every MapEntry record this profile declares and resolve its root.

    The count, base address and stride all come from the profile through the
    reader, so a profile that declares a different table is enumerated at its
    own extent rather than at Buu's.
    """
    entries: list[MapEntry] = []
    table_address = rom.map_entry_table_address()
    stride = rom.map_entry_stride()
    for index in range(rom.map_entry_count()):
        address = table_address + index * stride
        rom.span(address, stride)
        key_high = rom.u8(address + MAP_ENTRY_KEY_OFFSET)
        key_low = rom.u8(address + MAP_ENTRY_KEY_OFFSET + 1)
        text_word = rom.u32(address + MAP_ENTRY_TEXT_OFFSET)
        low = text_word & 0xFFFF
        text_index = low if text_word else None
        source = rom.u32(address + MAP_ENTRY_SOURCE_OFFSET)
        root = rom.u32(source)
        entries.append(
            MapEntry(
                index=index,
                address=address,
                key_high=key_high,
                key_low=key_low,
                text_index=text_index,
                source_address=source,
                root_address=root,
            )
        )
    return tuple(entries)


def read_layer(rom: Rom, root_address: int, slot: int) -> LayerRecord:
    """Read one of a root's four layer slots at the accepted offsets.

    The dominant form states its chunk grid at `+0x14`/`+0x15` and its chunk
    window at `+0x18`. The terrain-field form states its cell grid at
    `+0x04`/`+0x05` and its container run at `+0x08`, so its grid is read from
    there into `terrain_x`/`terrain_y` and the dominant fields are left alone
    rather than filled with the unrelated bytes those offsets happen to hold.
    """
    record = rom.u32(root_address + ROOT_LAYER_SLOTS[slot])
    handler = rom.u32(record)
    chunk_x = rom.u8(record + LAYER_CHUNK_X_OFFSET)
    chunk_y = rom.u8(record + LAYER_CHUNK_Y_OFFSET)
    terrain_x = terrain_y = 0
    addresses: list[int] = []
    nulls = 0
    if handler == TERRAIN_FIELD_LAYER_HANDLER:
        terrain_x = rom.u8(record + TERRAIN_FIELD_GRID_X_OFFSET)
        terrain_y = rom.u8(record + TERRAIN_FIELD_GRID_Y_OFFSET)
    if handler == DOMINANT_LAYER_HANDLER:
        for cell in range(chunk_x * chunk_y):
            address = rom.u32(record + LAYER_CHUNK_WINDOW_OFFSET + cell * 4)
            if address == 0:
                nulls += 1
            addresses.append(address)
    return LayerRecord(
        slot=slot,
        address=record,
        handler=handler,
        chunk_x=chunk_x,
        chunk_y=chunk_y,
        chunk_addresses=tuple(addresses),
        null_chunk_count=nulls,
        terrain_x=terrain_x,
        terrain_y=terrain_y,
    )


def read_layers(rom: Rom, root_address: int) -> tuple[LayerRecord, ...]:
    return tuple(read_layer(rom, root_address, slot) for slot in range(4))


def read_chunk_entries(rom: Rom, address: int) -> tuple[int, ...]:
    """Decode a dominant chunk container into 1024 little-endian u16 entries."""
    container = rom.container(address)
    if container.declared_size != CHUNK_DECODED_BYTES:
        raise CanonicalError(
            f"chunk at {address:#010x} declares {container.declared_size} bytes, "
            f"expected {CHUNK_DECODED_BYTES}"
        )
    return struct.unpack("<1024H", container.data)


def read_selector_stream(rom: Rom, root_address: int) -> tuple[int, ...]:
    """Decode ``root + 0x48`` into absolute ``bank:tile`` selectors.

    Entry zero is absolute; every later little-endian u16 is a delta from the
    preceding absolute selector, biased by one, wrapping to u16 exactly as the
    engine's own prefix-decode loop does.
    """
    address = rom.u32(root_address + ROOT_SELECTOR_STREAM_OFFSET)
    payload = rom.container_payload(address)
    if not payload or len(payload) % 2:
        raise CanonicalError(
            f"selector stream at {address:#010x} has non-even decoded size "
            f"{len(payload)}"
        )
    selectors = list(struct.unpack(f"<{len(payload) // 2}H", payload))
    for index in range(1, len(selectors)):
        selectors[index] = (selectors[index] + selectors[index - 1] + 1) & 0xFFFF
    return tuple(selectors)


@dataclass(frozen=True, slots=True)
class AnimatedTileSource:
    """One animated-tile record reached from ``root + 0x10``."""

    index: int
    address: int
    frame_count: int
    tile_count: int
    destination_tile: int
    first_frame_address: int
    first_frame_bytes: bytes


def read_animated_tiles(rom: Rom, root_address: int) -> tuple[AnimatedTileSource, ...]:
    """Read the animated-tile records and decode their first frame.

    The accepted root pair at `+0x0C`/`+0x10` is a count and a null-coupled
    pointer; the record layout below the count and the headerless packed frame
    are the shape `map_render` reconstructs, restated here so the export does not
    depend on the production renderer.
    """
    count = rom.u32(root_address + ROOT_ANIMATED_COUNT_OFFSET)
    if count == 0:
        return ()
    array = rom.u32(root_address + ROOT_ANIMATED_ARRAY_OFFSET)
    if array == 0:
        raise CanonicalError(
            f"root at {root_address:#010x} declares {count} animated tiles and a "
            "null array"
        )
    sources: list[AnimatedTileSource] = []
    for index in range(count):
        address = rom.u32(array + index * 4)
        offset = rom.offset(address)
        frame_count = rom.u8(address)
        tile_count = rom.u8(address + 1)
        destination = rom.u16(address + 2)
        if not frame_count or not tile_count:
            raise CanonicalError(
                f"animated-tile record at {address:#010x} has a zero extent"
            )
        first_frame = rom.u32(address + 4)
        expected = tile_count * BANK_TILE_BYTES
        data, _end, _marker = ws.decode_packed(
            rom.data,
            first_frame - ws.GBA_ROM_BASE + 4,
            expected,
            8,
            require_end_marker=True,
        )
        sources.append(
            AnimatedTileSource(
                index=index,
                address=address,
                frame_count=frame_count,
                tile_count=tile_count,
                destination_tile=destination,
                first_frame_address=first_frame,
                first_frame_bytes=data,
            )
        )
        del offset
    return tuple(sources)


@dataclass(frozen=True, slots=True)
class CharBlock:
    """The assembled 8bpp character data a map's layers index into."""

    data: bytes
    tile_count: int
    selector_count: int
    animated_tile_count: int


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
    ``bank_table_address`` is the value stored at `root + 0x4C` - the 187-entry
    table of bank *container pointers*, so a bank index is dereferenced through it
    before the container is decoded. Bank containers are decoded once per bank and
    cached, because a map's selector stream names a bank many times over.
    """
    tiles: list[bytes] = []
    cache: dict[int, bytes] = {}
    for selector in selectors:
        bank, source_tile = selector >> 8, selector & 0xFF
        if bank not in cache:
            cache[bank] = rom.container_payload(rom.u32(bank_table_address + bank * 4))
        bank_bytes = cache[bank]
        start = source_tile * BANK_TILE_BYTES
        if start + BANK_TILE_BYTES > len(bank_bytes):
            raise CanonicalError(
                f"selector {selector:#06x} reads tile {source_tile} past bank "
                f"{bank} ({len(bank_bytes)} bytes)"
            )
        tiles.append(bank_bytes[start : start + BANK_TILE_BYTES])

    highest = len(tiles) - 1
    for source in animated:
        highest = max(highest, source.destination_tile + source.tile_count - 1)
    block = bytearray((highest + 1) * BANK_TILE_BYTES)
    for ordinal, tile in enumerate(tiles):
        block[ordinal * BANK_TILE_BYTES : (ordinal + 1) * BANK_TILE_BYTES] = tile
    for source in animated:
        start = source.destination_tile * BANK_TILE_BYTES
        block[start : start + len(source.first_frame_bytes)] = source.first_frame_bytes

    return CharBlock(
        data=bytes(block),
        tile_count=highest + 1,
        selector_count=len(selectors),
        animated_tile_count=len(animated),
    )


def assemble_map_char_block(
    rom: Rom, root_address: int
) -> tuple[CharBlock, tuple[int, ...], tuple[AnimatedTileSource, ...]]:
    """Assemble a map's character block from its own root."""
    selectors = read_selector_stream(rom, root_address)
    animated = read_animated_tiles(rom, root_address)
    bank_table_address = rom.u32(root_address + ROOT_BANK_TABLE_OFFSET)
    block = assemble_char_block(rom, selectors, animated, bank_table_address)
    return block, selectors, animated


@dataclass(frozen=True, slots=True)
class Bank:
    """One entry of the 187-entry bank table."""

    index: int
    pointer_field_address: int
    container_address: int
    declared_size: int
    packed_bytes: int
    tile_count: int
    payload: bytes


def read_banks(rom: Rom, table_address: int = BANK_TABLE_ADDRESS,
               count: int = BANK_COUNT) -> tuple[Bank, ...]:
    """Read the bank table and decode every bank container."""
    banks: list[Bank] = []
    for index in range(count):
        field = table_address + index * 4
        container_address = rom.u32(field)
        container = rom.container(container_address)
        if container.declared_size % BANK_TILE_BYTES:
            raise CanonicalError(
                f"bank {index} at {container_address:#010x} declares "
                f"{container.declared_size} bytes, not a whole number of tiles"
            )
        banks.append(
            Bank(
                index=index,
                pointer_field_address=field,
                container_address=container_address,
                declared_size=container.declared_size,
                packed_bytes=container.packed_end - container.offset,
                tile_count=container.declared_size // BANK_TILE_BYTES,
                payload=container.data,
            )
        )
    return tuple(banks)


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
    for run_index in range(SPRITE_DEFINITION_COUNT):
        address = rom.u32(SPRITE_DEFINITION_RUN + run_index * 4)
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
