
from __future__ import annotations

from dataclasses import dataclass
import struct

from . import webfoot_lz


class SpriteFormatError(ValueError):
    """Raised when a sprite record is malformed or an edit cannot be honoured."""


OBJECT_DIMENSIONS: tuple[tuple[tuple[int, int], ...], ...] = (
    ((8, 8), (16, 16), (32, 32), (64, 64)),
    ((16, 8), (32, 8), (32, 16), (64, 32)),
    ((8, 16), (8, 32), (16, 32), (32, 64)),
)

ATTR0_COLOUR_256 = 0x2000
ATTR1_HORIZONTAL_FLIP = 0x1000
ATTR1_VERTICAL_FLIP = 0x2000

TILE_SIDE = 8

#: One piece record: ``s8 x``, ``s8 y``, two pixel-extent bytes, a packed OBJ
#: attribute pair and the graphics-container word. CONFIRMED as a stride across
#: all 11,005 reachable pieces, and fixed by the engine's own render-loop
#: arithmetic ``frame + 8 + 12 * index`` (`0x0800F3C0..0x0800F3CA`).
PIECE_SIZE = 12

FRAME_HEADER_SIZE = 8

FRAME_HEADER_MIN_X = 0x04
FRAME_HEADER_MIN_Y = 0x05
FRAME_HEADER_WIDTH = 0x06
FRAME_HEADER_HEIGHT = 0x07

#: Fields inside a piece record, relative to the piece's own start. Every offset
#: is an engine read site: ``x`` is the ``ldrsb`` at ``0x0800F204``, ``y`` the
#: ``ldrb`` at ``0x0800F22A``, the extents the ``ldrb`` pair at ``0x0800F206``
#: and ``0x0800F22E``, the attribute word the ``ldr`` at ``0x0800F1C2`` and
#: ``0x0800F24C``, and the container word the ``ldr r0, [r7, #8]`` at
#: ``0x0800F3CE``.
PIECE_X = 0x00
PIECE_Y = 0x01
PIECE_DIM_0 = 0x02
PIECE_DIM_1 = 0x03
PIECE_ATTRIBUTES = 0x04
PIECE_GRAPHICS = 0x08

DIRECTION_COUNT = 4

PALETTE_ENTRIES = 256
PALETTE_BYTES = PALETTE_ENTRIES * 2

TRANSPARENT_INDEX = 0

GRAPHICS_CONTAINER_KIND = 1



@dataclass(frozen=True)
class Palette:
    """Entry order is preserved exactly, never sorted and never deduplicated, because an index is the pixel value."""

    raw: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.raw) != PALETTE_ENTRIES:
            raise SpriteFormatError(
                f"palette has {len(self.raw)} entries, expected {PALETTE_ENTRIES}"
            )
        for index, word in enumerate(self.raw):
            if not 0 <= word <= 0xFFFF:
                raise SpriteFormatError(f"palette entry {index} is not a 16-bit word")

    @property
    def rgb(self) -> tuple[tuple[int, int, int], ...]:
        return tuple(expand_bgr555(word) for word in self.raw)


def expand_bgr555(word: int) -> tuple[int, int, int]:
    if not 0 <= word <= 0xFFFF or type(word) is not int:
        raise SpriteFormatError(f"palette word {word!r} is not a 16-bit word")

    def expand(part: int) -> int:
        return (part << 3) | (part >> 2)

    return (
        expand(word & 31),
        expand((word >> 5) & 31),
        expand((word >> 10) & 31),
    )


def expand_rgb888_channel(byte: int) -> int:
    if type(byte) is not int or not 0 <= byte <= 0xFF:
        raise SpriteFormatError(f"colour channel {byte!r} is not an 8-bit value")
    five = byte >> 3
    return (five << 3) | (five >> 2)


def _to5(channel: int) -> int:
    return min(31, (channel * 31 + 127) // 255)


def pack_gba_colour(red: int, green: int, blue: int) -> int:
    for name, channel in (("red", red), ("green", green), ("blue", blue)):
        if type(channel) is not int or not 0 <= channel <= 255:
            raise SpriteFormatError(f"{name} channel {channel!r} is not an 8-bit value")
    return _to5(red) | (_to5(green) << 5) | (_to5(blue) << 10)


def decode_palette(data: bytes, offset: int) -> Palette:
    """Read a 256-entry object palette at ``offset``."""
    if offset < 0 or offset + PALETTE_BYTES > len(data):
        raise SpriteFormatError(f"palette at {offset:#x} is outside the image")
    words = struct.unpack_from(f"<{PALETTE_ENTRIES}H", data, offset)
    return Palette(raw=words)


def encode_palette(palette: Palette) -> bytes:
    """Serialise a palette back to its exact source words."""
    return struct.pack(f"<{PALETTE_ENTRIES}H", *palette.raw)



def unswizzle_tiles(tiles: bytes, width: int, height: int, *, colour_256: bool) -> bytes:
    _check_dimensions(width, height)
    expected = tile_byte_count(width, height, colour_256=colour_256)
    if len(tiles) != expected:
        raise SpriteFormatError(
            f"{width}x{height} at {8 if colour_256 else 4}bpp needs {expected} "
            f"bytes of tile data, got {len(tiles)}"
        )

    out = bytearray(width * height)
    source = 0
    for tile_y in range(0, height, TILE_SIDE):
        for tile_x in range(0, width, TILE_SIDE):
            for y in range(TILE_SIDE):
                row = (tile_y + y) * width + tile_x
                if colour_256:
                    out[row : row + TILE_SIDE] = tiles[source : source + TILE_SIDE]
                    source += TILE_SIDE
                else:
                    for x in range(0, TILE_SIDE, 2):
                        packed = tiles[source]
                        source += 1
                        out[row + x] = packed & 0x0F
                        out[row + x + 1] = packed >> 4
    return bytes(out)


def swizzle_tiles(pixels: bytes, width: int, height: int, *, colour_256: bool) -> bytes:
    _check_dimensions(width, height)
    if len(pixels) != width * height:
        raise SpriteFormatError(
            f"{width}x{height} needs {width * height} pixels, got {len(pixels)}"
        )

    out = bytearray()
    for tile_y in range(0, height, TILE_SIDE):
        for tile_x in range(0, width, TILE_SIDE):
            for y in range(TILE_SIDE):
                row = (tile_y + y) * width + tile_x
                if colour_256:
                    out += pixels[row : row + TILE_SIDE]
                else:
                    for x in range(0, TILE_SIDE, 2):
                        low, high = pixels[row + x], pixels[row + x + 1]
                        if low > 0x0F or high > 0x0F:
                            raise SpriteFormatError(
                                f"pixel index {max(low, high)} exceeds 15 at 4bpp"
                            )
                        out.append((high << 4) | low)
    return bytes(out)


def flip_tile(tile: bytes, horizontal: bool, vertical: bool) -> bytes:
    if len(tile) != TILE_SIDE * TILE_SIDE:
        raise SpriteFormatError(
            f"a tile is {TILE_SIDE * TILE_SIDE} pixels, got {len(tile)}"
        )
    if not horizontal and not vertical:
        return tile
    rows = [tile[y * TILE_SIDE : (y + 1) * TILE_SIDE] for y in range(TILE_SIDE)]
    if horizontal:
        rows = [row[::-1] for row in rows]
    if vertical:
        rows = rows[::-1]
    return b"".join(rows)


def tile_byte_count(width: int, height: int, *, colour_256: bool) -> int:
    """Bytes of tile data a ``width`` x ``height`` image occupies."""
    pixels = width * height
    return pixels if colour_256 else pixels // 2


def _check_dimensions(width: int, height: int) -> None:
    if width <= 0 or height <= 0:
        raise SpriteFormatError(f"dimensions must be positive, got {width}x{height}")
    if width % TILE_SIDE or height % TILE_SIDE:
        raise SpriteFormatError(
            f"dimensions must be whole tiles, got {width}x{height}"
        )



@dataclass(frozen=True)
class Piece:
    """One 12-byte piece record, read only at offsets the engine is seen to use."""

    offset: int
    x: int
    y: int
    dim_0: int
    dim_1: int
    attributes: int
    graphics_pointer: int

    @property
    def shape(self) -> int:
        return (self.attributes & 0xFFFF) >> 14 & 3

    @property
    def size(self) -> int:
        return (self.attributes >> 16) >> 14 & 3

    @property
    def colour_256(self) -> bool:
        return bool(self.attributes & ATTR0_COLOUR_256)

    @property
    def horizontal_flip(self) -> bool:
        return bool((self.attributes >> 16) & ATTR1_HORIZONTAL_FLIP)

    @property
    def vertical_flip(self) -> bool:
        return bool((self.attributes >> 16) & ATTR1_VERTICAL_FLIP)

    @property
    def dimensions(self) -> tuple[int, int]:
        if self.shape >= len(OBJECT_DIMENSIONS):
            raise SpriteFormatError(
                f"piece at {self.offset:#x} uses reserved OAM shape {self.shape}"
            )
        return OBJECT_DIMENSIONS[self.shape][self.size]

    @property
    def stored_dimensions(self) -> tuple[int, int]:
        return self.dim_0, self.dim_1


def decode_piece(data: bytes, offset: int) -> Piece:
    """Read the 12-byte piece record at ``offset``."""
    if offset < 0 or offset + PIECE_SIZE > len(data):
        raise SpriteFormatError(f"piece record at {offset:#x} is outside the image")
    x, y, dim_0, dim_1 = struct.unpack_from("<bbBB", data, offset)
    attributes, pointer = struct.unpack_from("<II", data, offset + PIECE_ATTRIBUTES)
    return Piece(
        offset=offset,
        x=x,
        y=y,
        dim_0=dim_0,
        dim_1=dim_1,
        attributes=attributes,
        graphics_pointer=pointer,
    )


def encode_piece(piece: Piece) -> bytes:
    """Serialise a piece back to its exact 12 bytes."""
    return (
        struct.pack("<bbBB", piece.x, piece.y, piece.dim_0, piece.dim_1)
        + struct.pack("<II", piece.attributes, piece.graphics_pointer)
    )



@dataclass(frozen=True)
class Frame:

    offset: int
    pieces: tuple[Piece, ...]
    min_x: int
    min_y: int
    width: int
    height: int

    @property
    def piece_count(self) -> int:
        return len(self.pieces)

    @property
    def piece_bounds(self) -> tuple[int, int, int, int]:
        """``(min_x, min_y, width, height)`` computed from the pieces themselves."""
        min_x = min(piece.x for piece in self.pieces)
        min_y = min(piece.y for piece in self.pieces)
        max_x = max(piece.x + piece.dim_0 for piece in self.pieces)
        max_y = max(piece.y + piece.dim_1 for piece in self.pieces)
        return min_x, min_y, max_x - min_x, max_y - min_y

    @property
    def header_bounds(self) -> tuple[int, int, int, int]:
        return self.min_x, self.min_y, self.width, self.height


@dataclass(frozen=True)
class Animation:

    offset: int
    frame_count: int
    frame_pointers: tuple[int, ...]

    def pointer_for(self, frame_index: int, direction: int) -> int:
        if not 0 <= frame_index < self.frame_count:
            raise SpriteFormatError(f"frame {frame_index} out of range")
        if not 0 <= direction < DIRECTION_COUNT:
            raise SpriteFormatError(f"direction slot {direction} out of range")
        return self.frame_pointers[frame_index * DIRECTION_COUNT + direction]


def decode_frame(data: bytes, offset: int, *, maximum_pieces: int = 16) -> Frame:
    """Read the frame record at ``offset``: an 8-byte header, then 12-byte pieces."""
    if offset < 0 or offset + FRAME_HEADER_SIZE > len(data):
        raise SpriteFormatError(f"frame record at {offset:#x} is outside the image")
    count = struct.unpack_from("<I", data, offset)[0]
    if count == 0 or count > maximum_pieces:
        raise SpriteFormatError(
            f"frame at {offset:#x} declares {count} pieces, outside 1..{maximum_pieces}"
        )
    if offset + FRAME_HEADER_SIZE + count * PIECE_SIZE > len(data):
        raise SpriteFormatError(f"frame at {offset:#x} runs past the image")
    pieces = tuple(
        decode_piece(data, offset + FRAME_HEADER_SIZE + index * PIECE_SIZE)
        for index in range(count)
    )
    min_x, min_y, width, height = struct.unpack_from(
        "<bbBB", data, offset + FRAME_HEADER_MIN_X
    )
    return Frame(
        offset=offset,
        pieces=pieces,
        min_x=min_x,
        min_y=min_y,
        width=width,
        height=height,
    )


def decode_animation(data: bytes, offset: int, *, maximum_frames: int = 64) -> Animation:
    """Read the animation record at ``offset``."""
    if offset < 0 or offset + 4 > len(data):
        raise SpriteFormatError(f"animation record at {offset:#x} is outside the image")
    count = struct.unpack_from("<I", data, offset)[0]
    if count == 0 or count > maximum_frames:
        raise SpriteFormatError(
            f"animation at {offset:#x} declares {count} frames, outside "
            f"1..{maximum_frames}"
        )
    total = count * DIRECTION_COUNT
    if offset + 4 + total * 4 > len(data):
        raise SpriteFormatError(f"animation at {offset:#x} runs past the image")
    pointers = struct.unpack_from(f"<{total}I", data, offset + 4)
    return Animation(offset=offset, frame_count=count, frame_pointers=pointers)



@dataclass(frozen=True)
class Graphic:

    offset: int
    width: int
    height: int
    colour_256: bool
    pixels: bytes
    packed_end: int

    @property
    def packed_size(self) -> int:
        return self.packed_end - self.offset


def decode_graphic(data: bytes, offset: int, width: int, height: int, *,
                   colour_256: bool) -> Graphic:
    container = webfoot_lz.unpack(data, offset)
    expected = tile_byte_count(width, height, colour_256=colour_256)
    if container.declared_size != expected:
        raise SpriteFormatError(
            f"container at {offset:#x} holds {container.declared_size} bytes but "
            f"its piece declares {width}x{height} at "
            f"{8 if colour_256 else 4}bpp ({expected} bytes)"
        )
    return Graphic(
        offset=offset,
        width=width,
        height=height,
        colour_256=colour_256,
        pixels=unswizzle_tiles(container.data, width, height, colour_256=colour_256),
        packed_end=container.packed_end,
    )


@dataclass(frozen=True)
class PayloadPlan:

    offset: int
    original_size: int
    payload: bytes

    @property
    def padding(self) -> int:
        return self.original_size - len(self.payload)


def encode_graphic_payload(graphic: Graphic, pixels: bytes, *, kind: int) -> bytes:
    """Re-encode ``pixels`` into a retail-terminating container stream."""
    if len(pixels) != graphic.width * graphic.height:
        raise SpriteFormatError(
            f"expected {graphic.width * graphic.height} pixels for a "
            f"{graphic.width}x{graphic.height} graphic, got {len(pixels)}"
        )
    limit = 255 if graphic.colour_256 else 15
    for index, value in enumerate(pixels):
        if value > limit:
            raise SpriteFormatError(
                f"pixel {index} has index {value}, above the {limit} a "
                f"{8 if graphic.colour_256 else 4}bpp graphic can address"
            )

    tiles = swizzle_tiles(
        pixels, graphic.width, graphic.height, colour_256=graphic.colour_256
    )
    payload = webfoot_lz.pack(tiles, kind=kind)
    # The same production postcondition the dialogue write path applies, and the
    # same one place that owns it: a planned payload must reach the retail
    # decoder's own escape at its declared length rather than depending on the
    # bytes that follow it. Refusing here keeps an invalid stream out of the plan
    # before the allocation question is even asked.
    try:
        webfoot_lz.validate_retail_termination(payload)
    except webfoot_lz.ContainerError as exc:
        raise SpriteFormatError(
            f"re-encoded graphic at {graphic.offset:#x} does not satisfy the "
            f"retail termination contract: {exc}"
        ) from exc
    return payload


def graphics_container_kind(data: bytes, offset: int) -> int:
    kind, _declared = webfoot_lz.read_header(data, offset)
    if kind != GRAPHICS_CONTAINER_KIND:
        raise SpriteFormatError(
            f"graphic at {offset:#x} is a kind-{kind} container, but every "
            f"graphics container in the verified corpus is kind "
            f"{GRAPHICS_CONTAINER_KIND}; re-encoding it in an unproven container "
            "form is refused rather than guessed"
        )
    return kind


def plan_graphic_payload(data: bytes, graphic: Graphic, pixels: bytes) -> PayloadPlan:
    """Re-encode into the original's extent; growth is refused rather than written past the allocation."""
    payload = encode_graphic_payload(
        graphic, pixels, kind=graphics_container_kind(data, graphic.offset)
    )
    original = graphic.packed_size
    if len(payload) > original:
        raise SpriteFormatError(
            f"re-encoded graphic at {graphic.offset:#x} needs {len(payload)} bytes "
            f"but its original allocation is {original}; growth is refused because "
            "no free space is declared for this profile and the following bytes "
            "belong to another asset. Edit the palette instead, which is "
            "uncompressed and writes in place"
        )
    return PayloadPlan(offset=graphic.offset, original_size=original, payload=payload)
