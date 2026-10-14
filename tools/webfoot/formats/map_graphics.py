"""The one production reader for the accepted map/graphics binary concepts.
CQA-04-DECODE-STACK-AUTHORITY-001. Before this module the same map and graphics
concepts were decoded twice in production - once by the export-side readers
(``tools/export/canonical.py`` and ``tools/export/render.py``) and once by the
SDK's own map renderer (``tools/webfoot/map_render.py`` and
``tools/webfoot/formats/bg_tilemap.py``) - with no shared code, no cross-import
and no test comparing them. The two copies had already drifted observably: one
read every tile bank at exactly ``0x4000`` bytes and the other at whatever the
container declared, and only one of them understood the map-side layer handlers
beyond the dominant chunk grid.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import Mapping, Protocol

from ..binary import GBA_ROM_BASE
from ..profile import MapEntryTableProfile, RomProfile
from . import bg_tilemap as _bg
from . import map_entry as _me
from . import sprite_graphics as _sg
from . import text_tables as _tt
from . import webfoot_lz as _lz

__all__ = [
    "MapGraphicsError",
    "ContainerDecoder",
    "MapGraphicsReader",
    "MapEntry",
    "LayerRecord",
    "SelectorStream",
    "AnimatedTileSource",
    "CharBlock",
    "Bank",
    "read_map_entries",
    "read_map_entry_table",
    "read_layer",
    "read_layers",
    "layer_record_size",
    "layer_record_header",
    "compose_layer_record",
    "root_layer_slot_address",
    "declared_extent_raw",
    "dominant_layer_geometry",
    "dominant_chunk_words",
    "stitch_dominant_entries",
    "decode_selector_stream",
    "selectors_from_payload",
    "read_screenblock_entries",
    "screenblock_container_offset",
    "read_terrain_field_containers",
    "read_terrain_field_cells",
    "read_animated_tiles",
    "assemble_char_block",
    "assemble_map_char_block",
    "read_banks",
    "decode_bg_palette",
    "read_tile_entry",
    "tile_entry_ordinal",
    "tile_entry_horizontal_flip",
    "tile_entry_vertical_flip",
]


class MapGraphicsError(ValueError):
    """Raised when a map/graphics record cannot be read as the accepted schema
    states.

    One class for the whole reader, for the reason the container codec gives: a
    caller either reads the record or refuses it, and a caller that needs to tell
    two refusals apart reads the message. Callers with their own public error
    family translate at their boundary.
    """



TILE_PIXELS = _sg.TILE_SIDE

TILE_BYTES = _sg.TILE_SIDE * _sg.TILE_SIDE

CHUNK_SIDE_TILES = _bg.SCREEN_CHUNK_SIDE
CHUNK_ENTRY_COUNT = CHUNK_SIDE_TILES * CHUNK_SIDE_TILES
CHUNK_ENTRY_BYTES = 2
CHUNK_DECODED_BYTES = CHUNK_ENTRY_COUNT * CHUNK_ENTRY_BYTES

CHUNK_PIXELS = CHUNK_SIDE_TILES * TILE_PIXELS

CHUNK_POINTER_BYTES = 4

CHUNK_CONTAINER_KIND = 1

#: little-endian screen entries = 0x800 decoded bytes = 32x32 tiles.
SCREENBLOCK_ENTRY_COUNT = CHUNK_ENTRY_COUNT
SCREENBLOCK_DECODED_BYTES = CHUNK_DECODED_BYTES
SCREENBLOCK_PIXELS = CHUNK_PIXELS

TILE_ENTRY_ORDINAL_MASK = _bg.TILE_ENTRY_ORDINAL_MASK
TILE_ENTRY_BIT_10 = _bg.TILE_ENTRY_BIT_10
TILE_ENTRY_BIT_11 = _bg.TILE_ENTRY_BIT_11
TILE_ENTRY_HIGH_NIBBLE = _bg.TILE_ENTRY_HIGH_NIBBLE

MAX_TILE_INDEX = TILE_ENTRY_ORDINAL_MASK

OBJECT_DIMENSIONS = _sg.OBJECT_DIMENSIONS

BG_PALETTE_ENTRIES = 256
BG_PALETTE_BYTES = BG_PALETTE_ENTRIES * 3

OBJECT_PALETTE_ENTRIES = _sg.PALETTE_ENTRIES
OBJECT_PALETTE_BYTES = _sg.PALETTE_BYTES

TEXT_POINTER_SIZE = _tt.TEXT_POINTER_SIZE



MAP_ENTRY_KEY_OFFSET = 0x00
MAP_ENTRY_TEXT_OFFSET = 0x0C
MAP_ENTRY_SOURCE_OFFSET = 0x2C

ROOT_LAYER_SLOTS = (0x14, 0x18, 0x1C, 0x20)
ROOT_BG_ADDEND_OFFSET = 0x04
ROOT_EXTENT_X_OFFSET = 0x08
ROOT_EXTENT_Y_OFFSET = 0x0A
ROOT_SELECTOR_STREAM_OFFSET = 0x48
ROOT_BANK_TABLE_OFFSET = 0x4C
ROOT_CONNECTION_COUNT_OFFSET = 0x40
ROOT_CONNECTION_ARRAY_OFFSET = 0x44
ROOT_BG_CONTROL_OFFSET = 0x3C
ROOT_ANIMATED_COUNT_OFFSET = 0x0C
ROOT_ANIMATED_ARRAY_OFFSET = 0x10

LAYER_HANDLER_OFFSET = 0x00
LAYER_CHUNK_X_OFFSET = 0x14
LAYER_CHUNK_Y_OFFSET = 0x15
LAYER_CHUNK_WINDOW_OFFSET = 0x18

#: dominant records, the record's size is exactly `0x18 + 4 * chunk_x * chunk_y`
#: header byte must be copied verbatim - the header's `+0x04`, `+0x08`, `+0x0C`,
#: `+0x10` and `+0x16` fields have no established semantics (LOGX-SYNTHESIS
LAYER_RECORD_HEADER_BYTES = LAYER_CHUNK_WINDOW_OFFSET

VIEWPORT_PIXELS_X = 240
VIEWPORT_PIXELS_Y = 160
MAX_LAYER_GRID_SIDE = 8

#: The five accepted layer `+0x00` handler values. A handler value is ROM content
DOMINANT_LAYER_HANDLER = 0x08008087
ABSENT_LAYER_HANDLER = 0x08007A41
ABSENT_LAYER_RECORD = 0x080707FC

#: 0x800 decoded bytes, the same form a dominant chunk carries, but they reach
#: * `0x08007B63` - tail-branch stub `0x08007B62` into constructor `0x08007A60`,
#:   which decompresses `record + 0x04` (and `record + 0x08`, the same container
#: * `0x0800897B` - constructor `0x0800897A` builds only a twelve-byte marker
#:   uploaded later by method 1 of that type's descriptor: `0x080088E6` reads
#:   `record + 0x1C`, decompresses it into a 0x800-byte buffer and copies it to
#:   `0x0600E000 + slot * 0x800`. Method 2 (`0x08008924`) then programs
#:   `BGxHOFS`/`BGxVOFS` at `0x04000010 + 4*slot` from the record's `+0x04`,
#:   `+0x0C`, `+0x10`, `+0x14`, `+0x18` and a viewport object.
SCREENBLOCK_HANDLERS: dict[int, int] = {
    0x08007B63: 0x04,
    0x0800897B: 0x1C,
}

#: Entry `0x080088BC` -> constructor `0x080080C0`: enables `REG_IE` bit 1
#: (`0x04000200 |= 2`, the HBlank interrupt - not `DISPSTAT`, which is
#: `0x04000004`) and clears `BG2PB`/`BG2PD`, then streams `record + 4` x
#: `record + 5` containers of `0x400` decoded bytes through a nine-slot resident
#: assignment destroys the correspondence. `record + 0x04` x `record + 0x05`
TERRAIN_FIELD_LAYER_HANDLER = 0x080088BD
TERRAIN_FIELD_GRID_X_OFFSET = 0x04
TERRAIN_FIELD_GRID_Y_OFFSET = 0x05
TERRAIN_FIELD_CONTAINER_OFFSET = 0x08
TERRAIN_FIELD_CELL_BYTES = 0x400
TERRAIN_FIELD_CELL_TILES = 32
TERRAIN_FIELD_TILE_ORDINAL_MASK = 0xFF
TERRAIN_FIELD_RESIDENT_SLOTS = 9

BANK_TILE_BYTES = TILE_BYTES
BANK_COUNT = 187



class ContainerDecoder(Protocol):

    def __call__(
        self, data: bytes, offset: int, *, expected: int | None = ...
    ) -> "_lz.Container":
        ...


def project_container_decoder(
    data: bytes, offset: int, *, expected: int | None = None
) -> "_lz.Container":
    container = _lz.unpack(data, offset)
    if expected is not None and len(container.data) != expected:
        raise MapGraphicsError(
            f"container at {offset:#x} decoded {len(container.data):#x} bytes, "
            f"expected {expected:#x}"
        )
    return container



class MapGraphicsReader:

    __slots__ = ("data", "size", "_profile", "_decode")

    def __init__(
        self,
        data: bytes,
        profile: RomProfile,
        *,
        decode: ContainerDecoder | None = None,
    ) -> None:
        if not isinstance(data, (bytes, bytearray)):
            raise MapGraphicsError("ROM must be bytes")
        if profile is None:
            raise MapGraphicsError(
                "a map/graphics reader needs the profile whose tables it resolves"
            )
        self.data = bytes(data)
        self.size = len(self.data)
        self._profile = profile
        self._decode = decode if decode is not None else project_container_decoder

    @property
    def profile(self) -> RomProfile:
        return self._profile


    def map_entry_table(self) -> MapEntryTableProfile:
        table = self._profile.map_entries
        if table is None:
            raise MapGraphicsError(
                f"profile {self._profile.id!r} declares no map_entries table"
            )
        return table

    def map_entry_count(self) -> int:
        return self.map_entry_table().count

    def map_entry_table_address(self) -> int:
        return self.map_entry_table().address.raw

    def map_entry_stride(self) -> int:
        return self.map_entry_table().record_size

    def bg_palette_address(self) -> int:
        sprites = self._profile.actor_sprites
        if sprites is None:
            raise MapGraphicsError(
                f"profile {self._profile.id!r} declares no actor_sprites palette; "
                "a background palette address cannot be defaulted"
            )
        return sprites.bg_palette_address.raw

    def object_palette_address(self) -> int:
        sprites = self._profile.actor_sprites
        if sprites is None:
            raise MapGraphicsError(
                f"profile {self._profile.id!r} declares no actor_sprites palette"
            )
        return sprites.object_palette_address.raw


    def offset(self, address: int) -> int:
        """GBA address -> file offset, refusing anything outside the image."""
        offset = address - GBA_ROM_BASE
        if not 0 <= offset < self.size:
            raise MapGraphicsError(
                f"ROM pointer {address:#010x} (file {offset:#x}) is outside the "
                f"{self.size:#x}-byte image"
            )
        return offset

    def span(self, address: int, length: int) -> int:
        offset = self.offset(address)
        if length < 0 or offset + length > self.size:
            raise MapGraphicsError(
                f"{length:#x} bytes at {address:#010x} run past the image"
            )
        return offset

    def in_image(self, address: int) -> bool:
        return GBA_ROM_BASE <= address < GBA_ROM_BASE + self.size

    def u8(self, address: int) -> int:
        return self.data[self.offset(address)]

    def s8(self, address: int) -> int:
        value = self.data[self.offset(address)]
        return value - 256 if value > 127 else value

    def u16(self, address: int) -> int:
        return struct.unpack_from("<H", self.data, self.span(address, 2))[0]

    def u32(self, address: int) -> int:
        return struct.unpack_from("<I", self.data, self.span(address, 4))[0]

    def bytes_at(self, address: int, length: int) -> bytes:
        offset = self.span(address, length)
        return self.data[offset : offset + length]

    def container(self, address: int, *, expected: int | None = None):
        """Decode the container at ``address`` with this reader's decoder."""
        return self._decode(self.data, self.offset(address), expected=expected)

    def container_payload(self, address: int, *, expected: int | None = None) -> bytes:
        return self.container(address, expected=expected).data

    def raw_stream(
        self, offset: int, expected: int, initial_literal_bits: int = 8
    ) -> bytes:
        """Decode a headerless packed stream of a record-proven size."""
        try:
            return _lz.unpack_raw_stream(
                self.data, offset, expected, initial_literal_bits=initial_literal_bits
            )
        except _lz.ContainerError as exc:
            raise MapGraphicsError(
                f"raw packed stream at {offset:#x} did not decode: {exc}"
            ) from exc


    def map_entry(self, index: int) -> "MapEntry":
        return read_map_entries(self)[index]

    def map_entries(self) -> tuple["MapEntry", ...]:
        return read_map_entries(self)

    def layers(self, root_address: int) -> tuple["LayerRecord", ...]:
        return read_layers(self, root_address)

    def layer(self, root_address: int, slot: int) -> "LayerRecord":
        return read_layer(self, root_address, slot)

    def char_block(self, root_address: int) -> "CharBlock":
        return assemble_map_char_block(self, root_address)[0]

    def text(self, index: int) -> str | None:
        table = self._profile.text_strings
        if table is None or not 0 <= index < table.count:
            return None
        pointer_address = table.pointer_table_address.raw + index * TEXT_POINTER_SIZE
        try:
            address = self.u32(pointer_address)
        except MapGraphicsError:
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



@dataclass(frozen=True, slots=True)
class MapEntry:

    index: int
    address: int
    key_high: int
    key_low: int
    text_index: int | None
    source_address: int
    root_address: int
    record: "_me.MapEntry"

    @property
    def output_raw(self) -> int:
        """The `+0x00` byte under the upstream name the project pins."""
        return self.record.output_raw

    @property
    def zone_raw(self) -> int:
        """The `+0x01` byte under the upstream name the project pins."""
        return self.record.zone_raw


@dataclass(frozen=True, slots=True)
class LayerRecord:
    """One layer record reached from a map root's four slots.
    ``chunk_x``/``chunk_y`` are the dominant form's own grid at `+0x14`/`+0x15`.
    ``terrain_x``/``terrain_y`` are the terrain-field form's grid at `+0x04`/
    `+0x05`. They are held separately on purpose: on a terrain-field record the
    dominant offsets carry unrelated bytes, and filling the grid fields from
    them would invent a grid the record does not state.
    """

    slot: int
    address: int
    handler: int
    chunk_x: int
    chunk_y: int
    chunk_addresses: tuple[int, ...]
    null_chunk_count: int
    terrain_x: int = 0
    terrain_y: int = 0

    @property
    def chunk_cells(self) -> int:
        return self.chunk_x * self.chunk_y

    @property
    def terrain_cells(self) -> int:
        return self.terrain_x * self.terrain_y

    @property
    def chunk_tiles_x(self) -> int:
        return self.chunk_x * CHUNK_SIDE_TILES

    @property
    def chunk_tiles_y(self) -> int:
        return self.chunk_y * CHUNK_SIDE_TILES

    @property
    def chunk_pixels_x(self) -> int:
        return self.chunk_tiles_x * TILE_PIXELS

    @property
    def chunk_pixels_y(self) -> int:
        return self.chunk_tiles_y * TILE_PIXELS

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
        return self.terrain_tiles_x * TILE_PIXELS

    @property
    def terrain_pixels_y(self) -> int:
        return self.terrain_tiles_y * TILE_PIXELS

    @property
    def terrain_grid_x(self) -> int:
        """Cell-grid X of a terrain-field record; see the class docstring."""
        return self.terrain_x

    @property
    def terrain_grid_y(self) -> int:
        return self.terrain_y

    @property
    def classification(self) -> str:
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
        """Whether a renderer that knows every accepted form could draw this."""
        return self.classification in (
            "dominant",
            "static_graphical_screenblock",
            "static_graphical_terrain_field",
        )

    @property
    def resolved(self) -> bool:
        return self.classification not in (
            "unclassified_handler",
            "dominant_zero_grid",
            "dominant_partial_zero_grid",
        )

    @property
    def graphical(self) -> bool:
        return self.renderable

    @property
    def blocks_composite(self) -> bool:
        return not self.resolved or (self.graphical and not self.renderable)


@dataclass(frozen=True, slots=True)
class SelectorStream:

    address: int
    selectors: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class AnimatedTileSource:
    """One animated-tile record reached from ``root + 0x10``.
    """

    index: int
    address: int
    frame_count: int
    tile_count: int
    destination_tile: int
    first_frame_address: int
    first_frame_bytes: bytes


@dataclass(frozen=True, slots=True)
class CharBlock:

    data: bytes
    tile_count: int
    selector_count: int
    animated_tile_count: int
    missing_tile_indices: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class Bank:

    index: int
    pointer_field_address: int
    container_address: int
    declared_size: int
    packed_bytes: int
    tile_count: int
    payload: bytes



def read_map_entry_table(reader: MapGraphicsReader) -> MapEntryTableProfile:
    table = reader.map_entry_table()
    if table.record_size != _me.MAP_ENTRY_SIZE:
        raise MapGraphicsError(
            f"configured map-entry size must be 0x{_me.MAP_ENTRY_SIZE:X}; "
            f"got 0x{table.record_size:X}"
        )
    return table


def read_map_entries(reader: MapGraphicsReader) -> tuple[MapEntry, ...]:
    table = read_map_entry_table(reader)
    entries: list[MapEntry] = []
    for index in range(table.count):
        address = table.address.raw + index * table.record_size
        record = _me.MapEntry.from_bytes(
            reader.bytes_at(address, table.record_size)
        )
        text_word = record.unknown_0c
        low = text_word & 0xFFFF
        source = record.variation_array_pointer_raw
        entries.append(
            MapEntry(
                index=index,
                address=address,
                key_high=record.output_raw,
                key_low=record.zone_raw,
                text_index=low if text_word else None,
                source_address=source,
                root_address=reader.u32(source),
                record=record,
            )
        )
    return tuple(entries)



def read_layer(
    reader: MapGraphicsReader, root_address: int, slot: int
) -> LayerRecord:
    """Read one of a root's four layer slots at the accepted offsets.
    The dominant form states its chunk grid at `+0x14`/`+0x15` and its chunk
    window at `+0x18`. The terrain-field form states its cell grid at
    `+0x04`/`+0x05` and its container run at `+0x08`, so its grid is read from
    there into ``terrain_x``/``terrain_y`` and the dominant fields are left alone
    rather than filled with the unrelated bytes those offsets happen to hold.
    """
    if not 0 <= slot < len(ROOT_LAYER_SLOTS):
        raise MapGraphicsError(f"layer slot {slot!r} is outside 0..3")
    record = reader.u32(root_address + ROOT_LAYER_SLOTS[slot])
    handler = reader.u32(record)
    chunk_x = reader.u8(record + LAYER_CHUNK_X_OFFSET)
    chunk_y = reader.u8(record + LAYER_CHUNK_Y_OFFSET)
    terrain_x = terrain_y = 0
    addresses: list[int] = []
    nulls = 0
    if handler == TERRAIN_FIELD_LAYER_HANDLER:
        terrain_x = reader.u8(record + TERRAIN_FIELD_GRID_X_OFFSET)
        terrain_y = reader.u8(record + TERRAIN_FIELD_GRID_Y_OFFSET)
    if handler == DOMINANT_LAYER_HANDLER:
        for cell in range(chunk_x * chunk_y):
            address = reader.u32(record + LAYER_CHUNK_WINDOW_OFFSET + cell * 4)
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


def read_layers(reader: MapGraphicsReader, root_address: int) -> tuple[LayerRecord, ...]:
    return tuple(read_layer(reader, root_address, slot) for slot in range(4))


def layer_record_size(columns: int, rows: int) -> int:
    """A dominant layer record's exact byte size: ``0x18 + 4 * columns * rows``.
    """
    if not isinstance(columns, int) or not isinstance(rows, int):
        raise MapGraphicsError("a layer grid is stated in whole columns and rows")
    if columns <= 0 or rows <= 0:
        raise MapGraphicsError(
            f"a layer grid must be positive on both axes; got {columns}x{rows}"
        )
    return LAYER_RECORD_HEADER_BYTES + CHUNK_POINTER_BYTES * columns * rows


def layer_record_header(reader: MapGraphicsReader, layer: LayerRecord) -> bytes:
    """The dominant record's own ``0x18``-byte header, byte for byte.
    The header's ``+0x04``, ``+0x08``, ``+0x0C``, ``+0x10`` and ``+0x16`` fields
    have no established semantics, so a relocated record carries them rather than
    reconstructing them. Copying is the only operation that cannot invent a value.
    """
    if layer.classification not in ("dominant", "dominant_zero_grid",
                                    "dominant_partial_zero_grid"):
        raise MapGraphicsError(
            f"layer at {layer.address:#010x} is {layer.classification}, not a "
            "dominant record, so it has no chunk-grid header"
        )
    return reader.bytes_at(layer.address, LAYER_RECORD_HEADER_BYTES)


def compose_layer_record(
    header: bytes, columns: int, rows: int, window: Sequence[int]
) -> bytes:
    if len(header) != LAYER_RECORD_HEADER_BYTES:
        raise MapGraphicsError(
            f"a dominant layer header is {LAYER_RECORD_HEADER_BYTES} bytes; got "
            f"{len(header)}"
        )
    if not isinstance(columns, int) or not isinstance(rows, int):
        raise MapGraphicsError("a layer grid is stated in whole columns and rows")
    if not 0 < columns <= MAX_LAYER_GRID_SIDE or not 0 < rows <= MAX_LAYER_GRID_SIDE:
        raise MapGraphicsError(
            f"layer grid {columns}x{rows} is outside the supported 1.."
            f"{MAX_LAYER_GRID_SIDE} per axis"
        )
    cells = columns * rows
    if len(window) != cells:
        raise MapGraphicsError(
            f"a {columns}x{rows} grid holds {cells} cells; got {len(window)} addresses"
        )
    record = bytearray(header)
    record.extend(bytes(CHUNK_POINTER_BYTES * cells))
    record[LAYER_CHUNK_X_OFFSET] = columns
    record[LAYER_CHUNK_Y_OFFSET] = rows
    for index, address in enumerate(window):
        if not isinstance(address, int) or address == 0:
            raise MapGraphicsError(
                f"chunk cell {index} of a {columns}x{rows} grid names no chunk"
            )
        struct.pack_into("<I", record, LAYER_CHUNK_WINDOW_OFFSET + 4 * index, address)
    return bytes(record)


def root_layer_slot_address(root_address: int, slot: int) -> int:
    """The address of a map root's layer-slot pointer for ``slot``."""
    if not 0 <= slot < len(ROOT_LAYER_SLOTS):
        raise MapGraphicsError(f"layer slot {slot!r} is outside 0..3")
    return root_address + ROOT_LAYER_SLOTS[slot]


def declared_extent_raw(pixels: int, viewport: int) -> int:
    """The root extent field's stored value that makes ``pixels`` reachable.
    The engine loads the selector-1 root into its per-map camera state as
    ``dest+0x9C = (root + 0x08) - 1`` and ``dest+0x9E = (root + 0x0A) - 1``
    (``ldrh`` at ``0x0800958A``/``0x08009592``, ``subs #1``, stored at
    ``0x0800958E``/``0x08009596``), and the camera clamp at ``0x080094F0``
    saturates the requested view origin to ``[0, dest+0x9C]`` per axis - the same
    pair is re-read by the in-play camera clamp at ``0x08009744``. So the stored
    value is the map's **maximum camera scroll**, and the camera can show a plane
    ``P`` pixels wide only when ``stored + viewport >= P``.
    """
    if not isinstance(pixels, int) or not isinstance(viewport, int):
        raise MapGraphicsError("an extent is stated in whole pixels")
    if pixels <= 0 or viewport <= 0:
        raise MapGraphicsError(f"extent {pixels} px at viewport {viewport} px")
    return max(1, pixels - viewport)


def dominant_layer_geometry(
    reader: MapGraphicsReader,
    layer: LayerRecord,
    *,
    addresses: tuple[int, ...] | None = None,
) -> tuple[int, int, int, int]:
    """``(tile_columns, tile_rows, pixel_width, pixel_height)`` of a dominant layer.
    The one statement of a dominant layer's extent: the grid is the record's own
    ``+0x14``/``+0x15`` counts of 32x32-entry chunks. Reading it here rather than
    multiplying at each call site is what kept the two stacks from disagreeing
    about what a 2x3 grid covers.
    """
    del reader, addresses
    return (
        layer.chunk_tiles_x,
        layer.chunk_tiles_y,
        layer.chunk_pixels_x,
        layer.chunk_pixels_y,
    )


def dominant_chunk_words(
    reader: MapGraphicsReader, address: int
) -> tuple[int, ...]:
    container = reader.container(address, expected=CHUNK_DECODED_BYTES)
    if container.declared_size != CHUNK_DECODED_BYTES:
        raise MapGraphicsError(
            f"chunk at {address:#010x} declares {container.declared_size} bytes, "
            f"expected {CHUNK_DECODED_BYTES}"
        )
    return struct.unpack("<1024H", container.data)


def chunk_body_bytes(entries: object) -> bytes:
    """Encode one dominant chunk's screen-entry plane as its 0x800-byte payload.
    """
    if isinstance(entries, (str, bytes, bytearray)) or not hasattr(entries, "__len__"):
        raise MapGraphicsError(
            "a dominant chunk plane must be a sequence of screen entries"
        )
    values = tuple(entries)
    if len(values) != CHUNK_ENTRY_COUNT:
        raise MapGraphicsError(
            f"a dominant chunk plane holds {CHUNK_ENTRY_COUNT} screen entries, "
            f"not {len(values)}"
        )
    for index, value in enumerate(values):
        if type(value) is not int or not 0 <= value <= 0xFFFF:
            raise MapGraphicsError(
                f"screen entry {index} is {value!r}, which is not a 16-bit entry"
            )
    return struct.pack(f"<{CHUNK_ENTRY_COUNT}H", *values)


def pack_dominant_chunk(entries: object) -> bytes:
    return _lz.pack(chunk_body_bytes(entries), kind=CHUNK_CONTAINER_KIND)


def stitch_dominant_entries(
    reader: MapGraphicsReader,
    layer: LayerRecord,
    addresses: tuple[int, ...] | None = None,
    *,
    cache: dict[int, tuple[int, ...]] | None = None,
    entries_by_cell: Mapping[int, tuple[int, ...]] | None = None,
) -> tuple[int, ...]:
    """Stitch a dominant layer's chunk grid into one logical entry array.
    The accepted loader order, which the engine's own indexing at
    `0x08007C82..0x08007C90` establishes and both surfaces already implement:
    for every chunk row, for every local row, for every chunk in that row, that
    local row's 32 entries. A null chunk pointer contributes entry 0, the value
    the engine's own occupancy test treats as unoccupied.
    """
    side = CHUNK_SIDE_TILES
    if addresses is None:
        addresses = layer.chunk_addresses
    elif len(addresses) != len(layer.chunk_addresses):
        raise MapGraphicsError(
            "a dominant-layer override set must cover the layer's whole grid"
        )
    if len(addresses) != layer.chunk_cells:
        raise MapGraphicsError(
            f"layer states a {layer.chunk_x}x{layer.chunk_y} grid "
            f"({layer.chunk_cells} cells) but holds {len(addresses)} pointers"
        )
    if entries_by_cell:
        for cell, plane in entries_by_cell.items():
            if type(cell) is not int or not 0 <= cell < layer.chunk_cells:
                raise MapGraphicsError(
                    f"substituted chunk cell {cell!r} is outside this layer's grid"
                )
            if len(plane) != side * side:
                raise MapGraphicsError(
                    f"substituted chunk cell {cell} holds {len(plane)} entries, "
                    f"not {side * side}"
                )
    blanks = (0,) * (side * side)
    chunks: list[tuple[int, ...]] = []
    for cell, address in enumerate(addresses):
        if entries_by_cell and cell in entries_by_cell:
            chunks.append(entries_by_cell[cell])
            continue
        if address == 0:
            chunks.append(blanks)
            continue
        if cache is not None and address in cache:
            chunks.append(cache[address])
            continue
        entries = dominant_chunk_words(reader, address)
        if cache is not None:
            cache[address] = entries
        chunks.append(entries)
    out: list[int] = []
    for block_y in range(layer.chunk_y):
        for local_y in range(side):
            for block_x in range(layer.chunk_x):
                chunk = chunks[block_y * layer.chunk_x + block_x]
                start = local_y * side
                out.extend(chunk[start : start + side])
    return tuple(out)



def selectors_from_payload(payload: bytes, address: int) -> tuple[int, ...]:
    """Delta-decode an already-decoded selector payload.
    Entry zero is absolute; every later little-endian u16 is a delta from the
    preceding absolute selector, biased by one, wrapping to u16 exactly as the
    engine's own prefix-decode loop does (``ldrh/add/strh`` at
    ``0x08009C02..0x08009C12``).
    """
    if not payload or len(payload) % 2:
        raise MapGraphicsError(
            f"selector stream at {address:#010x} has non-even decoded size "
            f"{len(payload)}"
        )
    selectors = list(struct.unpack(f"<{len(payload) // 2}H", payload))
    for index in range(1, len(selectors)):
        selectors[index] = (selectors[index] + selectors[index - 1] + 1) & 0xFFFF
    return tuple(selectors)


def decode_selector_stream(
    reader: MapGraphicsReader, root_address: int
) -> SelectorStream:
    """Decode ``root + 0x48``'s container into absolute ``bank:tile`` selectors."""
    address = reader.u32(root_address + ROOT_SELECTOR_STREAM_OFFSET)
    payload = reader.container_payload(address)
    return SelectorStream(
        address=address, selectors=selectors_from_payload(payload, address)
    )



def screenblock_container_offset(handler: int) -> int:
    """The record field a screen-entry layer's handler reads its container from."""
    try:
        return SCREENBLOCK_HANDLERS[handler]
    except KeyError:
        raise MapGraphicsError(
            f"handler {handler:#010x} is not a screen-entry layer handler"
        ) from None


def read_screenblock_entries(
    reader: MapGraphicsReader, record_address: int
) -> tuple[int, ...]:
    """Read the screen-entry plane a screen-entry layer's handler decompresses.
    Two handlers carry the same 32x32 plane and reach it by different code, so
    the container field is taken from the record's own `+0x00` word. The payload
    is 1024 little-endian screen entries either way.
    """
    handler = reader.u32(record_address)
    offset = screenblock_container_offset(handler)
    container_address = reader.u32(record_address + offset)
    container = reader.container(container_address, expected=SCREENBLOCK_DECODED_BYTES)
    if container.declared_size != SCREENBLOCK_DECODED_BYTES:
        raise MapGraphicsError(
            f"screen-entry layer at {record_address:#010x} (handler "
            f"{handler:#010x}, field +{offset:#04x}) names a container declaring "
            f"{container.declared_size} bytes, expected {SCREENBLOCK_DECODED_BYTES}"
        )
    return struct.unpack("<1024H", container.data)



def read_terrain_field_containers(
    reader: MapGraphicsReader, record_address: int
) -> tuple[int, ...]:
    """The container addresses a terrain-field record names, in raster order.
    The record states its cell grid at `+0x04`/`+0x05` and names `grid_x *
    grid_y` consecutive container pointers from `+0x08`. A pointer outside the
    image is a structural mismatch rather than something to skip.
    """
    grid_x = reader.u8(record_address + TERRAIN_FIELD_GRID_X_OFFSET)
    grid_y = reader.u8(record_address + TERRAIN_FIELD_GRID_Y_OFFSET)
    targets: list[int] = []
    for index in range(grid_x * grid_y):
        address = reader.u32(
            record_address + TERRAIN_FIELD_CONTAINER_OFFSET + index * 4
        )
        if not reader.in_image(address):
            raise MapGraphicsError(
                f"terrain-field record at {record_address:#010x} names container "
                f"{index} at {address:#010x}, which is outside the image"
            )
        targets.append(address)
    return tuple(targets)


def read_terrain_field_cells(
    reader: MapGraphicsReader, record_address: int
) -> tuple[bytes, ...]:
    grid_x = reader.u8(record_address + TERRAIN_FIELD_GRID_X_OFFSET)
    grid_y = reader.u8(record_address + TERRAIN_FIELD_GRID_Y_OFFSET)
    if grid_x * grid_y == 0:
        return ()
    return tuple(
        reader.container_payload(address)
        for address in read_terrain_field_containers(reader, record_address)
    )


def stitch_terrain_field_plane(
    containers: tuple[bytes, ...],
    grid_x: int,
    grid_y: int,
) -> tuple[int, int, bytes]:
    """Lay a terrain field's containers out as one plane of tile ordinals.
    ASSET-EXPORT-MAP19-001 recovered this record form from the engine's own code
    and its payload's semantics: the `0x080088BD` constructor streams
    `grid_x * grid_y` containers of :data:`TERRAIN_FIELD_CELL_BYTES` decoded
    bytes through a nine-slot resident cache, and each container is a 32x32 plane
    of 8-bit tile ordinals. Container ``y * grid_x + x`` covers the cell at
    ``(x * 32, y * 32)``, so the whole field is ``32 * grid_x`` by ``32 * grid_y``
    ordinals.
    """
    if grid_x <= 0 or grid_y <= 0:
        raise MapGraphicsError(
            f"a terrain field needs a positive grid, got {grid_x}x{grid_y}"
        )
    expected = grid_x * grid_y
    if len(containers) != expected:
        raise MapGraphicsError(
            f"a {grid_x}x{grid_y} terrain field needs {expected} containers, "
            f"got {len(containers)}"
        )
    cell = TERRAIN_FIELD_CELL_TILES
    row_bytes = TERRAIN_FIELD_CELL_BYTES // cell
    width, height = grid_x * cell, grid_y * cell
    plane = bytearray(width * height)
    for index, data in enumerate(containers):
        if len(data) != TERRAIN_FIELD_CELL_BYTES:
            raise MapGraphicsError(
                f"terrain-field container {index} holds {len(data)} bytes, "
                f"expected {TERRAIN_FIELD_CELL_BYTES}"
            )
        at_x = (index % grid_x) * cell
        at_y = (index // grid_x) * cell
        for y in range(cell):
            target = (at_y + y) * width + at_x
            source = y * row_bytes
            plane[target : target + cell] = data[source : source + row_bytes]
    return width, height, bytes(plane)



def read_animated_tiles(
    reader: MapGraphicsReader, root_address: int
) -> tuple[AnimatedTileSource, ...]:
    """Read the animated-tile records and decode each one's first packed frame.
    The accepted root pair at `+0x0C`/`+0x10` is a count and a null-coupled
    pointer. The record is `u8 frame_count`, `u8 tile_count`, `u16 destination`,
    then a pointer to the first packed frame; the frame is a *headerless* stream
    whose size the record's tile count gives, which is why it is decoded through
    the raw-stream entry point rather than the container one.
    """
    count = reader.u32(root_address + ROOT_ANIMATED_COUNT_OFFSET)
    if count == 0:
        return ()
    array = reader.u32(root_address + ROOT_ANIMATED_ARRAY_OFFSET)
    if array == 0:
        raise MapGraphicsError(
            f"root at {root_address:#010x} declares {count} animated tiles and a "
            "null array"
        )
    sources: list[AnimatedTileSource] = []
    for index in range(count):
        address = reader.u32(array + index * 4)
        frame_count = reader.u8(address)
        tile_count = reader.u8(address + 1)
        destination = reader.u16(address + 2)
        if not frame_count or not tile_count:
            raise MapGraphicsError(
                f"animated-tile record at {address:#010x} has a zero extent"
            )
        first_frame = reader.u32(address + 4)
        data = reader.raw_stream(
            reader.offset(first_frame) + 4,
            tile_count * BANK_TILE_BYTES,
            initial_literal_bits=8,
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
    return tuple(sources)



def assemble_char_block(
    reader: MapGraphicsReader,
    selectors: tuple[int, ...],
    animated: tuple[AnimatedTileSource, ...],
    bank_table_address: int,
    *,
    require_referenced: tuple[int, ...] | None = None,
) -> CharBlock:
    """Assemble character data: selector ordinal -> tile, animated tiles overlaid.
    A selector writes exactly one 8x8 tile to character memory at
    ``64 * ordinal``; an animated-tile record writes ``tile_count`` tiles starting
    at its own destination ordinal. Both come from the engine's own loaders.
    ``bank_table_address`` is the value stored at `root + 0x4C` - the table of
    bank *container pointers* - so a bank index is dereferenced through it before
    the container is decoded. Bank containers are decoded once per bank and
    cached, because a map's selector stream names a bank many times over.
    """
    tiles: list[bytes] = []
    cache: dict[int, bytes] = {}
    for selector in selectors:
        bank, source_tile = selector >> 8, selector & 0xFF
        if bank not in cache:
            cache[bank] = reader.container(
                reader.u32(bank_table_address + bank * 4)
            ).data
        bank_bytes = cache[bank]
        start = source_tile * BANK_TILE_BYTES
        if start + BANK_TILE_BYTES > len(bank_bytes):
            raise MapGraphicsError(
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

    missing: tuple[int, ...] = ()
    if require_referenced is not None:
        covered = set(range(len(tiles)))
        for source in animated:
            covered.update(
                range(
                    source.destination_tile,
                    source.destination_tile + source.tile_count,
                )
            )
        missing = tuple(sorted(set(require_referenced) - covered))

    return CharBlock(
        data=bytes(block),
        tile_count=highest + 1,
        selector_count=len(selectors),
        animated_tile_count=len(animated),
        missing_tile_indices=missing,
    )


def assemble_map_char_block(
    reader: MapGraphicsReader,
    root_address: int,
    *,
    require_referenced: tuple[int, ...] | None = None,
) -> tuple[CharBlock, SelectorStream, tuple[AnimatedTileSource, ...]]:
    """Assemble a map's character block from its own root."""
    stream = decode_selector_stream(reader, root_address)
    animated = read_animated_tiles(reader, root_address)
    bank_table_address = reader.u32(root_address + ROOT_BANK_TABLE_OFFSET)
    block = assemble_char_block(
        reader,
        stream.selectors,
        animated,
        bank_table_address,
        require_referenced=require_referenced,
    )
    return block, stream, animated



def read_banks(
    reader: MapGraphicsReader,
    table_address: int,
    count: int = BANK_COUNT,
) -> tuple[Bank, ...]:
    """Read a bank table and decode every bank container.
    ``table_address`` is a map root's ``+0x4C`` field, which is where the
    accepted graph stores it. It is required rather than defaulted so a caller
    cannot silently decode a table belonging to another image.
    """
    banks: list[Bank] = []
    for index in range(count):
        field = table_address + index * 4
        container_address = reader.u32(field)
        container = reader.container(container_address)
        if container.declared_size % BANK_TILE_BYTES:
            raise MapGraphicsError(
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



def decode_bg_palette(
    reader: MapGraphicsReader,
) -> tuple[tuple[int, int, int], ...]:
    address = reader.bg_palette_address()
    offset = reader.span(address, BG_PALETTE_BYTES)
    raw = reader.data[offset : offset + BG_PALETTE_BYTES]

    def display(byte: int) -> int:
        five = byte >> 3
        return (five << 3) | (five >> 2)

    return tuple(
        (
            display(raw[index * 3]),
            display(raw[index * 3 + 1]),
            display(raw[index * 3 + 2]),
        )
        for index in range(BG_PALETTE_ENTRIES)
    )



def read_tile_entry(word: int) -> "_bg.ScreenEntry":
    """Decode one 16-bit tile entry with the format layer's own decoder."""
    return _bg.ScreenEntry.decode(word)


def tile_entry_ordinal(word: int) -> int:
    """The tile ordinal a screen entry names: bits 0..9."""
    return word & TILE_ENTRY_ORDINAL_MASK


def tile_entry_horizontal_flip(word: int) -> bool:
    return bool(word & TILE_ENTRY_BIT_10)


def tile_entry_vertical_flip(word: int) -> bool:
    """Whether the entry sets bit 11, the platform's vertical flip selector."""
    return bool(word & TILE_ENTRY_BIT_11)
