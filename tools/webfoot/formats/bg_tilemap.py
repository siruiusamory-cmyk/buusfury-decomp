"""GBA Mode 0 regular tiled background: screen entries, screenblocks, layer render.

MAP-VIS-001 Phase 3. A pure codec over ``bytes``: no filesystem, no addresses
beyond the block indices its caller supplies, no game-name branching - the same
discipline as `webfoot.formats.sprite_graphics`. It reuses that module's tile
unswizzle rather than re-deriving GBA tile layout.

**The chain**, straight from GBATEK (verified against the MAP-VIS-001 map 40 VRAM
dump manifest, which supplies the block numbers as runtime inputs):

    DISPCNT mode 0            up to four REGULAR tiled BG layers
      -> BGxCNT               char base block, screen base block, size, colour mode
        -> screenblock        2 KiB = 32x32 u16 screen entries (one 256x256 map)
          -> screen entry     tile index + H/V flip + palette bank
            -> charblock       16 KiB of tile graphics; tile N is 64 (8bpp) or
                               32 (4bpp) bytes from the charblock base
              -> tile          8x8 palette indices, unswizzled and flipped

**Blocks are addressed by number, never hardcoded.** A charblock is 0x4000 bytes
and a screenblock is 0x800 bytes from the VRAM base; both this module and its
callers work in block indices so the same code renders any layer of any dump.
The manifest block numbers (28/29/30/31 for map 40) are runtime inputs, not
constants here.

**Palette bank is decoded but unused at 8bpp.** The screen entry carries a
4-bit palette bank in bits 12-15; at 8bpp a tile indexes the full 256-colour
table and the bank is ignored (GBATEK). The field is decoded so a 4bpp caller
can use it, and left untouched by the 8bpp render path rather than silently
dropped.

**A tile index is not clamped to one charblock.** The screen entry's tile index
is 10 bits (0..1023) and the hardware fetches ``char_base + index * tile_bytes``
without stopping at the 16 KiB base block - an 8bpp index past 255 simply reads
into the following VRAM. Map 40 relies on this (its indices reach ~890). So the
render bound is VRAM extent, not one charblock.

**Fail closed.** A tile whose bytes run past VRAM, or a block number that runs
past VRAM, is a `BgTilemapError`, not a wrap-around read - a garbled layer must
surface as an error, not as plausible-looking wrong pixels.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct

from . import sprite_graphics


class BgTilemapError(ValueError):
    """Raised when a screen entry, block, or tile reference is out of range."""


#: A charblock of tile graphics is 16 KiB from the VRAM base (GBATEK).
CHAR_BLOCK_BYTES = 0x4000

#: A screenblock is 2 KiB = 32x32 u16 screen entries (GBATEK).
SCREEN_BLOCK_BYTES = 0x800

#: Screen entries per screenblock (a 32x32 tile map).
SCREEN_ENTRIES = SCREEN_BLOCK_BYTES // 2

#: The side of one screen-entry plane, in tiles. One screenblock is a 32x32
#: tile map, and a dominant map chunk carries exactly the same 32x32 plane, so
#: this is the one statement of that side.
SCREEN_CHUNK_SIDE = 32

#: Tiles are 8x8 on this hardware, always.
TILE_SIDE = sprite_graphics.TILE_SIDE

#: A single 8x8 tile: 64 bytes at 8bpp, 32 bytes at 4bpp.
TILE_BYTES_8BPP = TILE_SIDE * TILE_SIDE
TILE_BYTES_4BPP = TILE_BYTES_8BPP // 2

#: The screen entry's bit fields. These are the ONE statement of which bit is
#: which; `ScreenEntry.decode` reads them, and every other module that needs to
#: inspect a raw entry word (the map-side format reader, the exporter) reads
#: them from here rather than re-testing a literal.
#:
#: Bits 10 and 11 are the platform's horizontal and vertical flip selectors for a
#: regular tiled background. The accepted work marks the *direction* assignment
#: `PARTIALLY CONFIRMED`; the hardware flips the tile and both renderers apply
#: it. Bits 12..15 are decoded as the palette bank, which at 8bpp is ignored.
TILE_ENTRY_ORDINAL_MASK = 0x03FF   # bits 0..9
TILE_ENTRY_HORIZONTAL_FLIP = 0x0400
TILE_ENTRY_VERTICAL_FLIP = 0x0800
TILE_ENTRY_PALETTE_BANK_SHIFT = 12
TILE_ENTRY_PALETTE_BANK_MASK = 0xF
#: Bits 12..15 read as a whole. Reserved/constant in the canonical map corpus,
#: but a meaningful palette bank for a 4bpp caller, so it is never dropped.
TILE_ENTRY_HIGH_NIBBLE = 0xF000
#: The aliases the map-side format reader and the exporter use, kept so both
#: spellings resolve to this one pair of bits rather than to their own copy.
TILE_ENTRY_BIT_10 = TILE_ENTRY_HORIZONTAL_FLIP
TILE_ENTRY_BIT_11 = TILE_ENTRY_VERTICAL_FLIP


@dataclass(frozen=True)
class ScreenEntry:
    """One 16-bit BG screen (map) entry.

    ``palette_bank`` is decoded for completeness; it is ignored by the 8bpp
    render path (an 8bpp tile uses the full 256-colour palette - GBATEK).
    """

    tile_index: int
    h_flip: bool
    v_flip: bool
    palette_bank: int

    @classmethod
    def decode(cls, word: int) -> "ScreenEntry":
        if not 0 <= word <= 0xFFFF:
            raise BgTilemapError(f"screen entry {word!r} is not a 16-bit word")
        return cls(
            tile_index=word & TILE_ENTRY_ORDINAL_MASK,
            h_flip=bool(word & TILE_ENTRY_HORIZONTAL_FLIP),
            v_flip=bool(word & TILE_ENTRY_VERTICAL_FLIP),
            palette_bank=(word >> TILE_ENTRY_PALETTE_BANK_SHIFT)
            & TILE_ENTRY_PALETTE_BANK_MASK,
        )


def encode_screen_entry(entry: ScreenEntry) -> int:
    """The exact 16-bit word :meth:`ScreenEntry.decode` reads.

    The inverse of the decode, so a caller that has a decoded entry can put it
    back into the plane it came from without a second statement of the bit
    positions. Rendered output never needs this; a test oracle comparing a
    logical layout against a live VRAM screenblock does.
    """
    return (
        entry.tile_index
        | (int(entry.h_flip) << 10)
        | (int(entry.v_flip) << 11)
        | (entry.palette_bank << TILE_ENTRY_PALETTE_BANK_SHIFT)
    )


def decode_screenblock(data: bytes, offset: int) -> tuple[ScreenEntry, ...]:
    """Decode a 2 KiB screenblock at ``offset`` into 1024 screen entries."""
    if offset < 0 or offset + SCREEN_BLOCK_BYTES > len(data):
        raise BgTilemapError(f"screenblock at {offset:#x} is outside VRAM")
    words = struct.unpack_from(f"<{SCREEN_ENTRIES}H", data, offset)
    return tuple(ScreenEntry.decode(word) for word in words)


def _flip_tile(tile: bytes, h_flip: bool, v_flip: bool) -> bytes:
    """Apply H/V flip to a linear 8x8 block of indices.

    Delegates to the format layer's one flip: this module's screen-entry renderer
    is its only caller here, and the exporter's tile path calls the same
    function, so the two cannot mirror different axes.
    """
    return sprite_graphics.flip_tile(tile, h_flip, v_flip)


def render_layer(
    vram: bytes,
    *,
    char_base_block: int,
    screen_base_block: int,
    map_width_tiles: int,
    map_height_tiles: int,
    color_256: bool,
) -> tuple[bytes, int, int]:
    """Render one regular tiled BG layer to linear 8bpp palette indices.

    Returns ``(pixels, width, height)`` where ``width = map_width_tiles * 8`` and
    likewise for height. Each screen entry's tile is fetched from the charblock,
    unswizzled to 8x8 indices via `sprite_graphics.unswizzle_tiles`, flipped, and
    blitted into the layer buffer.

    Fails closed on any block or tile reference that runs past VRAM or past the
    charblock.
    """
    if map_width_tiles <= 0 or map_height_tiles <= 0:
        raise BgTilemapError(
            f"map dimensions must be positive, got "
            f"{map_width_tiles}x{map_height_tiles} tiles"
        )

    char_base = char_base_block * CHAR_BLOCK_BYTES
    if char_base < 0 or char_base + CHAR_BLOCK_BYTES > len(vram):
        raise BgTilemapError(
            f"char base block {char_base_block} ({char_base:#x}) is outside VRAM"
        )

    tile_bytes = TILE_BYTES_8BPP if color_256 else TILE_BYTES_4BPP

    screen_base = screen_base_block * SCREEN_BLOCK_BYTES
    entries = decode_screenblock(vram, screen_base)
    needed = map_width_tiles * map_height_tiles
    if needed > len(entries):
        raise BgTilemapError(
            f"a {map_width_tiles}x{map_height_tiles} map needs {needed} screen "
            f"entries but one screenblock holds only {len(entries)}"
        )

    try:
        return render_entries(
            vram,
            entries[:needed],
            map_width_tiles=map_width_tiles,
            map_height_tiles=map_height_tiles,
            color_256=color_256,
            char_offset=char_base,
        )
    except BgTilemapError as exc:
        # Preserve this hardware-facing API's established diagnostic wording.
        raise BgTilemapError(str(exc).replace("character data", "VRAM")) from exc


def entry_tile(
    char_data: bytes,
    word: int,
    *,
    colour_256: bool = True,
) -> bytes:
    """The 8x8 linear tile one screen-entry word names, with its stored flips.

    One tile's worth of :func:`render_entry_words`, exposed because a caller that
    needs a single tile (a sheet builder, a piece preview) must not reach into the
    tile bytes with its own ordinals-and-flips arithmetic and become a second
    implementation of the same decode.
    """
    entry = ScreenEntry.decode(word)
    tile_bytes = TILE_BYTES_8BPP if colour_256 else TILE_BYTES_4BPP
    src = entry.tile_index * tile_bytes
    if src + tile_bytes > len(char_data):
        raise BgTilemapError(
            f"screen entry references tile {entry.tile_index} at {src:#x}, whose "
            f"{tile_bytes} bytes run past character data ({len(char_data):#x})"
        )
    raw = char_data[src : src + tile_bytes]
    unswizzled = sprite_graphics.unswizzle_tiles(
        raw, TILE_SIDE, TILE_SIDE, colour_256=colour_256
    )
    return _flip_tile(unswizzled, entry.h_flip, entry.v_flip)


def render_entries(
    char_data: bytes,
    entries: tuple[ScreenEntry, ...],
    *,
    map_width_tiles: int,
    map_height_tiles: int,
    color_256: bool,
    char_offset: int = 0,
) -> tuple[bytes, int, int]:
    """Render a logical regular-BG layout from already-decoded screen entries.

    Unlike :func:`render_layer`, this accepts a complete logical entry array,
    so maps larger than the engine's camera-relative 32x32 hardware window do
    not need to be forced through a synthetic screenblock.

    A caller holding the raw 16-bit words the plane stores - which is what a
    ROM-backed map reader has - calls :func:`render_entry_words` instead, which
    shares this function's whole tile path and differs only in how it reaches
    the entry's ordinal and flip bits.
    """
    def entry_at(index: int) -> ScreenEntry:
        try:
            return entries[index]
        except IndexError:
            raise BgTilemapError(
                f"logical layout has {len(entries)} entries, expected "
                f"{map_width_tiles * map_height_tiles}"
            ) from None

    return _render_tiles(
        char_data,
        entry_at,
        count=map_width_tiles * map_height_tiles,
        map_width_tiles=map_width_tiles,
        map_height_tiles=map_height_tiles,
        color_256=color_256,
        char_offset=char_offset,
    )


def render_entry_words(
    char_data: bytes,
    words: tuple[int, ...] | list[int],
    *,
    map_width_tiles: int,
    map_height_tiles: int,
    color_256: bool,
    char_offset: int = 0,
) -> tuple[bytes, int, int]:
    """Render raw 16-bit screen-entry words into a linear index image.

    The word form of :func:`render_entries`, and the entry point a ROM-backed
    reader uses: a dominant chunk and a screen-entry plane both decode to tuples
    of little-endian u16 words, so a caller never has to build a second decoded
    representation of the same plane. Bits 0..9 are the ordinal, bits 10 and 11
    the flips; the palette bank is ignored at 8bpp, exactly as GBATEK states.
    """
    if len(words) != map_width_tiles * map_height_tiles:
        raise BgTilemapError(
            f"logical layout has {len(words)} entries, expected "
            f"{map_width_tiles * map_height_tiles}"
        )

    def entry_at(index: int) -> ScreenEntry:
        return ScreenEntry.decode(words[index])

    return _render_tiles(
        char_data,
        entry_at,
        count=len(words),
        map_width_tiles=map_width_tiles,
        map_height_tiles=map_height_tiles,
        color_256=color_256,
        char_offset=char_offset,
    )


def _render_tiles(
    char_data: bytes,
    entry_at,
    *,
    count: int,
    map_width_tiles: int,
    map_height_tiles: int,
    color_256: bool,
    char_offset: int = 0,
) -> tuple[bytes, int, int]:
    """The one tile-blitting core both entry forms render through."""
    if map_width_tiles <= 0 or map_height_tiles <= 0:
        raise BgTilemapError(
            f"map dimensions must be positive, got "
            f"{map_width_tiles}x{map_height_tiles} tiles"
        )
    if count != map_width_tiles * map_height_tiles:
        raise BgTilemapError(
            f"logical layout has {count} entries, expected "
            f"{map_width_tiles * map_height_tiles}"
        )
    if char_offset < 0 or char_offset > len(char_data):
        raise BgTilemapError(f"character offset {char_offset:#x} is outside data")

    tile_bytes = TILE_BYTES_8BPP if color_256 else TILE_BYTES_4BPP
    width = map_width_tiles * TILE_SIDE
    height = map_height_tiles * TILE_SIDE
    out = bytearray(width * height)

    # One fetch, unswizzle and flip per distinct entry: a map repeats entries
    # heavily (a flat field is one entry 1024 times), and the flip bits are part
    # of the identity, so keying on the decoded entry is exact.
    cache: dict[ScreenEntry, bytes] = {}
    for index in range(count):
        entry = entry_at(index)
        tile = cache.get(entry)
        if tile is None:
            src = char_offset + entry.tile_index * tile_bytes
            if src + tile_bytes > len(char_data):
                tile_x, tile_y = index % map_width_tiles, index // map_width_tiles
                raise BgTilemapError(
                    f"screen entry at tile ({tile_x},{tile_y}) references tile "
                    f"{entry.tile_index} at {src:#x}, whose {tile_bytes} bytes run "
                    f"past character data ({len(char_data):#x})"
                )
            raw = char_data[src : src + tile_bytes]
            unswizzled = sprite_graphics.unswizzle_tiles(
                raw, TILE_SIDE, TILE_SIDE, colour_256=color_256
            )
            tile = _flip_tile(unswizzled, entry.h_flip, entry.v_flip)
            cache[entry] = tile
        base = (index // map_width_tiles) * TILE_SIDE * width + (
            index % map_width_tiles
        ) * TILE_SIDE
        for y in range(TILE_SIDE):
            dst = base + y * width
            out[dst : dst + TILE_SIDE] = tile[y * TILE_SIDE : (y + 1) * TILE_SIDE]

    return bytes(out), width, height
