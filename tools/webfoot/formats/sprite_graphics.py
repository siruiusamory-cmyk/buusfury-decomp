"""Buu's Fury actor sprite graphics: tiles, palette, pieces, frames, animations.

TOOLKIT-010. A pure codec over ``bytes``: no filesystem, no addresses beyond the
file offsets its caller supplies, no game-name branching. The semantic layer
that turns these records into named project assets is `webfoot.graphics`.

**The chain**, verified against the canonical image (see
`docs/research/GRAPHICS_FORMAT.md` for how each count was measured):

    character pointer table   297 entries, all valid, strictly ascending
      -> character structure  variable size; animation pointers follow a header
        -> animation record   u32 frame_count, then frame_count * 4 pointers
          -> frame record     8-byte header, then 12-byte piece records
            -> piece record   x at +0x00, y at +0x01, two pixel extents at
                              +0x02/+0x03, a packed OBJ attribute pair at +0x04
                              and a graphics-container pointer at +0x08
              -> container    `webfoot.formats.webfoot_lz`, decoding to raw tiles

Frame record fields, at the engine's own widths: `u32 piece_count` then the
frame's bounding box over its pieces - `s8 min_x`, `s8 min_y`, `u8 width`,
`u8 height`. The render loop computes `frame + 8 + 12 * index`, and the header's
four bytes reproduce the pieces' bounding box on all 10,980 canonical frames.

**The layers are kept apart on purpose.** A packed payload, the tile bytes it
decodes to, the pixel indices those tiles unswizzle into, the palette that gives
them colour, the piece that places them, the frame that groups pieces and the
animation that orders frames are seven different things. The ROM does not collapse
them and neither does this module: there is no ``Sprite`` class here, because
the corpus does not contain one.

**Populations, and which of them is a total.** The canonical corpus reaches
**7,390** distinct graphics-container offsets through pieces. **7,355** is exactly
the subset reached by single-piece frames - a population, never the total. The
frame population is 10,980 distinct frame records holding 11,005 pieces, of which
21 frames are multi-piece (19 hold two pieces and 2 hold four).

**The layout this module used to model, and why it changed.** Until
EVIDENCE-RISK-DEBT-001 it read the refuted 4-byte frame header and 16-byte piece
records, with the attribute pair at `+0x08`, the graphics pointer at `+0x0C` and a
six-byte "unknown" span at `+0x02..+0x07`. LOGX-FRAME-001 refuted that reading: the
piece stride is `0x0C`, the attribute pair is at `+0x04`, the container pointer is
at `+0x08`, and the two bytes the old model buried in `unknown_raw` are the piece's
own pixel extents. The old walk rejected every multi-piece frame on its
size/geometry test, which is exactly why the corpus appeared to hold 10,959
single-piece frames and 7,355 containers.

**Sharing is the normal case, not an edge case.** 10,980 distinct frame records
reference only 7,390 distinct containers. Anything that treats a piece as *owning*
its pixels will silently edit several characters at once. Callers get container
offsets and resolve ownership themselves; `webfoot.graphics` exposes the measured
consumer and character lists.

**Multi-piece frames exist, and the decoder is exercised on them.** 21 of the
10,980 canonical frames hold more than one piece - 19 hold two and 2 hold four -
so the general case is the one the corpus actually contains, not a hypothetical.
The count is a full word and the plausibility bound accepts up to 16; nothing here
may assume a frame and its single piece are interchangeable.

**Depth is uniformly 8bpp, measured.** Every piece in the corpus sets attribute0
bit 13. The 4bpp path is implemented because the attribute defines it and the
GBA hardware supports it (gbadoc: 32 bytes per tile at 4bpp against 64 at 8bpp),
but it is exercised only by synthetic fixtures. A 4bpp piece appearing in a
future profile would decode; one appearing *here* would mean the reading is
wrong, so the decoder reports depth rather than hiding it.

**Transparency is index 0, and that is evidence rather than convention.** GBA
palette index 0 being transparent for objects is a platform norm, which is
exactly why it needed checking instead of assuming: in a decoded 32x32 frame
from character 0, index 0 accounts for 60.2% of pixels and forms the connected
surround, while the body occupies a tight 114..119 ramp. Rendering with index 0
opaque produces a solid block, which is what a wrong convention would look like.

**Palette.** One global 256-entry object palette at a profile-declared offset,
not a per-character one. The character structure header holds no palette
pointer: across 297 structures, ROM pointers appear only at +0x00 (4 of them),
+0x04 (65) and +0x50 (10), none of which resolves to a palette. The declared
object palette has 16 inbound word-aligned references against the background
palette's 1, and decodes as a plain ramp - black, black, white, red, orange,
yellow, green, cyan.

**Capacity, and the honest limit of pixel editing.** The containers are packed
end to end: zero overlaps, and 4,034 of 7,389 consecutive pairs are exactly
adjacent. There is no slack anywhere and no profile declares free space, so
:func:`plan_graphic_payload` refuses any re-encoding that does not fit the
original packed extent rather than trusting that the bytes after a container are
spare.

That refusal is the common case, not the exception. `webfoot_lz.pack` emits valid,
self-terminating streams - it writes the retail decoder's own escape after the
final token - but averages 1.06x the size Webfoot's own compressor achieved, so
roughly one payload in two hundred re-encodes small enough to fit. The size the
fit rule compares is the **final** encoded length, escape and final padding
included; there is no pre-marker figure to fall back on. The bound it is compared
against stays the conservative one - the original container's declared-size
extent, which does not credit it with an escape word that may belong to the next
container - so a correct payload can be refused for being one word larger than
that, and :func:`plan_graphic_payload` says so. Pixel editing therefore reaches
EDIT but not WRITE for most assets. **Palette editing is the supported route to a
visible change**: the object palette is uncompressed and fixed-size, so a recolour
is an exact in-place write with no capacity question at all. Both are reported
separately in the capability matrix; neither is described as the other.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct

from . import webfoot_lz


class SpriteFormatError(ValueError):
    """Raised when a sprite record is malformed or an edit cannot be honoured."""


#: OAM shape/size -> pixel dimensions. Shape is attribute0 bits 14-15, size is
#: attribute1 bits 14-15; GBATEK gives exactly this 3x4 table and shape 3 is
#: "not used", which is why a shape of 3 is a rejection rather than a lookup.
OBJECT_DIMENSIONS: tuple[tuple[tuple[int, int], ...], ...] = (
    ((8, 8), (16, 16), (32, 32), (64, 64)),      # square
    ((16, 8), (32, 8), (32, 16), (64, 32)),      # horizontal
    ((8, 16), (8, 32), (16, 32), (32, 64)),      # vertical
)

#: Attribute bits this project reads. Named so the call sites do not carry bare
#: hex, and so a future profile that disagrees fails visibly at one place.
ATTR0_COLOUR_256 = 0x2000
ATTR1_HORIZONTAL_FLIP = 0x1000
ATTR1_VERTICAL_FLIP = 0x2000

#: Tiles are 8x8 on this hardware, always.
TILE_SIDE = 8

#: One piece record: ``s8 x``, ``s8 y``, two pixel-extent bytes, a packed OBJ
#: attribute pair and the graphics-container word. CONFIRMED as a stride across
#: all 11,005 reachable pieces, and fixed by the engine's own render-loop
#: arithmetic ``frame + 8 + 12 * index`` (`0x0800F3C0..0x0800F3CA`).
PIECE_SIZE = 12

#: Bytes of a frame record before its first piece: ``u32 piece_count`` then the
#: frame's bounding box, ``s8 min_x``, ``s8 min_y``, ``u8 width``, ``u8 height``.
FRAME_HEADER_SIZE = 8

#: Fields inside a frame record's 8-byte header.
FRAME_HEADER_MIN_X = 0x04   # s8, the minimum piece x
FRAME_HEADER_MIN_Y = 0x05   # s8, the minimum piece y
FRAME_HEADER_WIDTH = 0x06   # u8, the width of the pieces' union
FRAME_HEADER_HEIGHT = 0x07  # u8, the height of the pieces' union

#: Fields inside a piece record, relative to the piece's own start. Every offset
#: is an engine read site: ``x`` is the ``ldrsb`` at ``0x0800F204``, ``y`` the
#: ``ldrb`` at ``0x0800F22A``, the extents the ``ldrb`` pair at ``0x0800F206``
#: and ``0x0800F22E``, the attribute word the ``ldr`` at ``0x0800F1C2`` and
#: ``0x0800F24C``, and the container word the ``ldr r0, [r7, #8]`` at
#: ``0x0800F3CE``.
PIECE_X = 0x00           # s8
PIECE_Y = 0x01           # s8
PIECE_DIM_0 = 0x02       # u8, the piece's horizontal pixel extent
PIECE_DIM_1 = 0x03       # u8, the piece's vertical pixel extent
PIECE_ATTRIBUTES = 0x04  # u32 packed OBJ attribute pair
PIECE_GRAPHICS = 0x08    # u32 container pointer

#: A frame's four direction slots. The animation record stores frame_count * 4
#: pointers and the corpus never departs from that, but note what is NOT claimed:
#: that slot 0 is "down" or slot 2 is "left". Direction *names* are gameplay
#: semantics and nothing in the ROM labels them, so they stay numbered.
DIRECTION_COUNT = 4

#: Palette entries in the object palette, and the bytes they occupy.
PALETTE_ENTRIES = 256
PALETTE_BYTES = PALETTE_ENTRIES * 2

#: The transparent index for this family. See the module docstring: measured,
#: not assumed from platform convention.
TRANSPARENT_INDEX = 0


# --- palette -----------------------------------------------------------------

@dataclass(frozen=True)
class Palette:
    """A 256-entry object palette, kept in BOTH representations.

    ``raw`` holds the original little-endian 16-bit words and is what
    :func:`encode_palette` writes back; ``rgb`` is the expanded display colour
    and is derived. Keeping the raw word is the whole point: GBA colour is
    5 bits per channel, so an 8-bit RGB triple cannot round-trip to a unique
    word, and a palette edited through RGB alone would quietly re-quantise.
    Entry order is preserved exactly - never sorted, never deduplicated - because
    the index *is* the identity that every pixel byte refers to.
    """

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
        """Display colours, 8 bits per channel.

        The 5-to-8 bit expansion replicates the high bits into the low ones
        (``v << 3 | v >> 2``) so that 31 maps to 255 rather than 248; a plain
        shift would make white slightly grey.
        """
        return tuple(expand_bgr555(word) for word in self.raw)


def expand_bgr555(word: int) -> tuple[int, int, int]:
    """One little-endian GBA palette halfword as 8-bit display RGB.

    The ONE implementation of the hardware's 5-to-8 bit expansion: the object
    palette's :attr:`Palette.rgb`, the exporter's object-palette decode and the
    engine-global background palette's RGB888 requantisation all reduce to it, so
    a fixed channel cannot be expanded two different ways by two readers.
    """
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
    """One 8-bit RGB channel requantised to the hardware's 5 bits and back.

    The background palette is stored as RGB888 but the display keeps 5 bits per
    channel, so the faithful value is the 5-bit quantisation re-expanded. One
    implementation, for the same reason as :func:`expand_bgr555`.
    """
    if type(byte) is not int or not 0 <= byte <= 0xFF:
        raise SpriteFormatError(f"colour channel {byte!r} is not an 8-bit value")
    five = byte >> 3
    return (five << 3) | (five >> 2)


def _to5(channel: int) -> int:
    """One 8-bit channel to the nearest 5-bit step, clamped to 0..31.

    Inverts the decode's ``v << 3 | v >> 2`` expansion: every representable
    value sits exactly on a step so it round-trips, and a free value snaps to
    the closest step instead of truncating down.
    """
    return min(31, (channel * 31 + 127) // 255)


def pack_gba_colour(red: int, green: int, blue: int) -> int:
    """Pack an 8-bit RGB triple into a GBA 15-bit palette word.

    The inverse of :attr:`Palette.rgb`'s 5-bit-per-channel decode: that property
    expands ``word & 31`` etc. up to 8 bits (``v << 3 | v >> 2``), so this maps
    each 8-bit channel to the NEAREST 5-bit step (round, not truncate) and
    repacks ``r | g << 5 | b << 10``. Bit 15 is unused on this hardware and
    stays clear.

    Rounding to nearest keeps two properties: any triple already produced by
    :attr:`Palette.rgb` packs back to the word it came from (idempotent for
    representable colours, since those sit exactly on a step), AND a triple
    picked freely maps to the closest representable colour rather than always
    rounding down - so a channel like 250 becomes 31 (nearest) not 30 (trunc).
    """
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


# --- tiles -------------------------------------------------------------------

def unswizzle_tiles(tiles: bytes, width: int, height: int, *, colour_256: bool) -> bytes:
    """Tiled 8x8 blocks -> a linear ``width * height`` block of palette indices.

    GBA graphics are stored one 8x8 tile at a time, left to right then top to
    bottom, and this is the only function that knows it. Everything above this
    point works in linear pixel indices, which is what makes an ordinary image
    editor a usable authoring tool.
    """
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
                        # 4bpp packs two pixels per byte, low nibble first.
                        out[row + x] = packed & 0x0F
                        out[row + x + 1] = packed >> 4
    return bytes(out)


def swizzle_tiles(pixels: bytes, width: int, height: int, *, colour_256: bool) -> bytes:
    """The exact inverse of :func:`unswizzle_tiles`.

    Round-tripping through this pair must be the identity on every payload in
    the corpus; the ROM-gated suite asserts that over all 7,390 containers
    rather than over a sample, because a swizzle bug that only affects unusual
    dimensions is precisely the kind that a sample would miss.
    """
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
    """Apply the horizontal and vertical flip to a linear square 8x8 tile.

    H-flip mirrors the 8 columns of each row; V-flip mirrors the 8 rows. This is
    the ONE implementation of that transform: the 8x8 tiled-background renderer
    (`bg_tilemap`) and the exporter both call it rather than each carrying a copy
    that could disagree about which axis is which.
    """
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


# --- pieces ------------------------------------------------------------------

@dataclass(frozen=True)
class Piece:
    """One 12-byte piece record, read only at offsets the engine is seen to use.

    ``x`` and ``y`` are signed placement offsets. ``dim_0``/``dim_1`` are the
    piece's own stored pixel extents, and they are *stored fields*, not a guess:
    the engine halves ``dim_0`` to centre an OBJ horizontally and multiplies the
    pair to size the composite buffer. ``attributes`` is the packed OBJ attribute
    pair ``(attribute_1 << 16) | attribute_0`` the engine loads and merges into the
    outgoing OAM word, and whose decoded shape/size reproduces the stored extents
    on every canonical piece. ``graphics_pointer`` is the container word.
    """

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
        """The extents the record stores, independent of the attribute decode.

        The two agree on all 11,005 canonical pieces, which is what makes the
        attribute reading evidence rather than a restatement.
        """
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


# --- frames and animations ---------------------------------------------------

@dataclass(frozen=True)
class Frame:
    """A frame: an 8-byte header and ``piece_count`` 12-byte piece records.

    The header holds the piece count and the frame's own bounding box over those
    pieces - signed minimum x and y, then unsigned width and height. On all 10,980
    canonical frames that box equals the pieces' own union, which is what makes it
    a bounding box rather than four raw bytes; this module records it and does not
    require the equality, so a future profile that disagrees still reads.
    """

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
    """An animation: a frame count and ``frame_count * 4`` frame pointers.

    ``frame_pointers`` is stored flat and in file order. It is deliberately not
    reshaped into a per-direction structure here, because doing so would bake in
    the claim that the four slots are directions in a particular arrangement.
    :meth:`pointer_for` states the indexing without naming the slots.
    """

    offset: int
    frame_count: int
    frame_pointers: tuple[int, ...]

    def pointer_for(self, frame_index: int, direction: int) -> int:
        """The pointer for one (frame, direction slot) pair.

        Direction-major within each frame: slot ``d`` of frame ``f`` lives at
        flat index ``f * 4 + d``.
        """
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


# --- decoded graphics --------------------------------------------------------

@dataclass(frozen=True)
class Graphic:
    """One decoded graphics payload: linear palette indices plus its extent.

    ``packed_end`` and ``packed_size`` come from the container and are what a
    later edit is measured against. ``width``/``height`` come from the *piece*
    that referenced the payload, not from the payload itself - which is why
    decoding cross-checks the two and why that cross-check is meaningful.
    """

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
    """Decode the container at ``offset`` into linear palette indices.

    The size check is the load-bearing line. The container's declared size and
    the piece's stored extents are recorded independently in the ROM, so
    requiring them to agree turns a decode from "produced plausible bytes" into
    a structural verification. Across the canonical corpus it holds for all
    7,390 containers - and for all 11,005 piece references, because a container
    several frames share is checked by each of them.
    """
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
    """A re-encoded payload plus the exact region it replaces."""

    offset: int
    original_size: int
    payload: bytes

    @property
    def padding(self) -> int:
        return self.original_size - len(self.payload)


def plan_graphic_payload(data: bytes, graphic: Graphic, pixels: bytes) -> PayloadPlan:
    """Re-encode ``pixels`` into the space the original payload occupied.

    This is where the capacity rule lives, and it fails closed. The corpus has
    no slack - containers sit end to end, 4,034 pairs of them exactly adjacent -
    so a payload that does not fit its original extent has nowhere to go that is
    not another asset's bytes. No profile declares free space, and this function
    will not go looking for any.

    **Expect this to refuse.** The replacement is re-encoded with
    `webfoot_lz.pack`, which produces a valid, self-terminating stream but not a
    competitive one - a median 1.06x the original packed size, so about one
    payload in two hundred fits. That is a measured property of the encoder,
    stated rather than papered over, and it is why palette editing is this
    subsystem's supported route to a visible change. Refusal is the honest
    answer; writing past a container's end is not an alternative.

    The fit comparison uses the final encoded length, which already includes the
    retail decoder's escape and the final word's padding; nothing here subtracts
    the terminator to make an old allocation appear to fit. The payload is also
    re-decoded to the retail engine's own termination rule before the comparison
    is made, so a stream that is not provably self-terminating never reaches a
    plan.

    One asymmetry is deliberate and worth stating. The bound is the *original*
    container's declared-size-terminated extent (``Graphic.packed_size``), which
    does not credit that container with an escape beginning a fresh word: the
    following bytes may be the next container's, and this module already refuses
    to assume otherwise. For a container whose own escape did begin a fresh word,
    a corrected payload carrying its own escape is one word larger than that bound
    and is refused. The refusal is the honest answer - the alternative is a write
    that reaches into a neighbour - and it is why a re-encode is only guaranteed to
    fit when its escape lands inside the final word.

    Bytes between the new payload and the end of the original extent are left
    for the caller to preserve verbatim; see `webfoot.graphics`. They are not
    zero-filled, because nothing establishes that trailing allocation bytes are
    disposable and a container's tail may be another record's head.
    """
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
    payload = webfoot_lz.pack(tiles)
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
