"""Buu's Fury actor sprite graphics: tiles, palette, pieces, frames, animations.

TOOLKIT-010. A pure codec over ``bytes``: no filesystem, no addresses beyond the
file offsets its caller supplies, no game-name branching. The semantic layer
that turns these records into named project assets is `webfoot.graphics`.

**The chain**, verified against the canonical image (see
`docs/research/GRAPHICS_FORMAT.md` for how each count was measured):

    character pointer table   297 entries, all valid, strictly ascending
      -> character structure  variable size; animation pointers follow a header
        -> animation record   u32 frame_count, then frame_count * 4 pointers
          -> frame record     u32 piece_count, then 16-byte piece records
            -> piece record   OAM-style attributes + a graphics container pointer
              -> container    `webfoot.formats.webfoot_lz`, decoding to raw tiles

**The layers are kept apart on purpose.** A packed payload, the tile bytes it
decodes to, the pixel indices those tiles unswizzle into, the palette that gives
them colour, the piece that places them, the frame that groups pieces and the
animation that orders frames are six different things. The ROM does not collapse
them and neither does this module: there is no ``Sprite`` class here, because
the corpus does not contain one.

**Sharing is the normal case, not an edge case.** 10,959 distinct frame records
reference only 7,355 distinct containers: 2,986 payloads are reached by more
than one frame and 2,644 are used by more than one character. Anything that
treats a piece as *owning* its pixels will silently edit several characters at
once. Callers get container offsets and resolve ownership themselves;
`webfoot.graphics` exposes the consumer and character lists.

**One piece per frame, measured - not assumed.** Across all 10,959 distinct
frames in the canonical image, every single one declares exactly one piece. The
record format clearly permits more (the count is a full word, and the plausibility
bound accepts up to 16), so the decoder handles the general case; but no
multi-piece frame exists in this corpus, and no code here may assume that a frame
and its single piece are interchangeable.

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
end to end: zero overlaps, and 4,014 of 7,354 consecutive pairs are exactly
adjacent. There is no slack anywhere and no profile declares free space, so
:func:`plan_graphic_payload` refuses any re-encoding that does not fit the
original packed extent rather than trusting that the bytes after a container are
spare.

That refusal is the common case, not the exception. `webfoot_lz.pack` emits
valid streams but averages 1.06x the size Webfoot's own compressor achieved, so
roughly one payload in two hundred re-encodes small enough to fit. Pixel editing
therefore reaches EDIT but not WRITE for most assets. **Palette editing is the
supported route to a visible change**: the object palette is uncompressed and
fixed-size, so a recolour is an exact in-place write with no capacity question
at all. Both are reported separately in the capability matrix; neither is
described as the other.
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

#: One piece record. CONFIRMED as a stride across all 13,588 reachable pieces.
PIECE_SIZE = 16

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
        def expand(part: int) -> int:
            return (part << 3) | (part >> 2)

        return tuple(
            (expand(word & 31), expand((word >> 5) & 31), expand((word >> 10) & 31))
            for word in self.raw
        )


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
    the corpus; the ROM-gated suite asserts that over all 7,355 containers
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
    """One 16-byte OBJ placement record.

    Only the fields whose meaning is established get names. ``unknown_raw``
    carries bytes +0x02..+0x07 verbatim and is re-emitted unchanged on write,
    following the same rule as every other codec in this project: a field that
    has not been explained is preserved, not dropped and not guessed at. Those
    six bytes are non-zero in the corpus and their purpose is UNKNOWN.
    """

    offset: int
    x: int
    y: int
    unknown_raw: bytes
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


def decode_piece(data: bytes, offset: int) -> Piece:
    """Read the 16-byte piece record at ``offset``."""
    if offset < 0 or offset + PIECE_SIZE > len(data):
        raise SpriteFormatError(f"piece record at {offset:#x} is outside the image")
    x, y = struct.unpack_from("<bb", data, offset)
    attributes, pointer = struct.unpack_from("<II", data, offset + 8)
    return Piece(
        offset=offset,
        x=x,
        y=y,
        unknown_raw=data[offset + 2 : offset + 8],
        attributes=attributes,
        graphics_pointer=pointer,
    )


def encode_piece(piece: Piece) -> bytes:
    """Serialise a piece back to its exact 16 bytes, unknowns included."""
    if len(piece.unknown_raw) != 6:
        raise SpriteFormatError("piece unknown_raw must be exactly 6 bytes")
    return (
        struct.pack("<bb", piece.x, piece.y)
        + piece.unknown_raw
        + struct.pack("<II", piece.attributes, piece.graphics_pointer)
    )


# --- frames and animations ---------------------------------------------------

@dataclass(frozen=True)
class Frame:
    """A frame: a piece count followed by that many piece records."""

    offset: int
    pieces: tuple[Piece, ...]


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
    """Read the frame record at ``offset``."""
    if offset < 0 or offset + 4 > len(data):
        raise SpriteFormatError(f"frame record at {offset:#x} is outside the image")
    count = struct.unpack_from("<I", data, offset)[0]
    if count == 0 or count > maximum_pieces:
        raise SpriteFormatError(
            f"frame at {offset:#x} declares {count} pieces, outside 1..{maximum_pieces}"
        )
    if offset + 4 + count * PIECE_SIZE > len(data):
        raise SpriteFormatError(f"frame at {offset:#x} runs past the image")
    pieces = tuple(
        decode_piece(data, offset + 4 + index * PIECE_SIZE) for index in range(count)
    )
    return Frame(offset=offset, pieces=pieces)


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
    the piece's OAM dimensions are recorded independently in the ROM, so
    requiring them to agree turns a decode from "produced plausible bytes" into
    a structural verification. Across the canonical corpus it holds for all
    7,355 containers.
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
    no slack - containers sit end to end, 4,014 pairs of them exactly adjacent -
    so a payload that does not fit its original extent has nowhere to go that is
    not another asset's bytes. No profile declares free space, and this function
    will not go looking for any.

    **Expect this to refuse.** The replacement is re-encoded with
    `webfoot_lz.pack`, which produces a valid stream but not a competitive one -
    a median 1.06x the original packed size, so about one payload in two hundred
    fits. That is a measured property of the encoder, stated rather than papered
    over, and it is why palette editing is this subsystem's supported route to a
    visible change. Refusal is the honest answer; writing past a container's end
    is not an alternative.

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
