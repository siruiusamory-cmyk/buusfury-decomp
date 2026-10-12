"""The OAM-to-PNG dumper: the hardware's own addressing, checked on synthetic entries.

The load-bearing tests are the two addressing ones. An 8bpp tile number indexes 32-byte slots with its low
bit IGNORED, and a 4bpp pixel's colour is `bank * 16 + nibble`; both were wrong in a sibling tool's VRAM
scan (a bank census that named the wrong banks), so each is pinned here rather than assumed.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.research import oam_sprites  # noqa: E402
from tools.webfoot.formats import indexed_png, sprite_graphics  # noqa: E402


def entry(attr0: int, attr1: int, attr2: int, *, index: int = 0) -> bytes:
    """One OAM entry set, every other entry DISABLED (mode 2).

    A zeroed entry is not an empty one: mode 0 draws an 8x8 sprite at (0,0), so a fixture that leaves the
    rest zeroed would paint 127 sprites the test never asked for.
    """
    oam = bytearray(oam_sprites.OAM_ENTRIES * oam_sprites.OAM_ENTRY_BYTES)
    for other in range(oam_sprites.OAM_ENTRIES):
        struct.pack_into("<H", oam, other * 8, 0x0200)
    struct.pack_into("<HHH", oam, index * 8, attr0, attr1, attr2)
    return bytes(oam)


def attr0(y: int, *, mode: int = 0, colour_256: bool = True, shape: int = 0) -> int:
    return y | (mode << 8) | (0x2000 if colour_256 else 0) | (shape << 14)


def attr1(x: int, *, size: int = 0, hflip: bool = False, vflip: bool = False) -> int:
    return (x & 0x1FF) | (0x1000 if hflip else 0) | (0x2000 if vflip else 0) | (size << 14)


def tile_8bpp(values: bytes) -> bytes:
    assert len(values) == 64
    return values


def test_an_8bpp_entry_draws_its_tile_at_the_oam_position() -> None:
    vram = bytearray(oam_sprites.OBJ_VRAM_BYTES)
    vram[0:64] = tile_8bpp(bytes(range(64)))
    composite = oam_sprites.compose(entry(attr0(20), attr1(10), 0), bytes(vram))
    assert composite.painted == 63, "the tile's own index 0 is transparent"
    assert composite.drawn[0].describe().startswith("entry   0 at (  10, 20) 8x8 8bpp tile 0 bank 0")
    at = (20 * 240 + 10)
    assert composite.canvas[at] == 0, "index 0 of the tile is transparent"
    assert composite.canvas[at + 1] == 1
    assert composite.canvas[at + 64] == 0, "only the 8x8 square is painted"
    assert composite.painted_banks() == [0, 1, 2, 3]


def test_an_8bpp_tile_number_ignores_its_low_bit() -> None:
    """Tile 1 and tile 0 are the same 64 bytes: the address is (tile & ~1) * 32."""
    vram = bytearray(oam_sprites.OBJ_VRAM_BYTES)
    vram[0:64] = tile_8bpp(bytes([7] * 64))
    odd = oam_sprites.compose(entry(attr0(0), attr1(0), 1), bytes(vram))
    even = oam_sprites.compose(entry(attr0(0), attr1(0), 0), bytes(vram))
    assert odd.canvas == even.canvas
    assert odd.canvas[0] == 7
    # And tile 2 is a different 64 bytes, 64 into the window, not 128.
    vram[64:128] = tile_8bpp(bytes([9] * 64))
    assert oam_sprites.compose(entry(attr0(0), attr1(0), 2), bytes(vram)).canvas[0] == 9


def test_a_4bpp_entry_paints_bank_times_sixteen_plus_the_nibble() -> None:
    vram = bytearray(oam_sprites.OBJ_VRAM_BYTES)
    vram[0:32] = bytes([0x21] * 32)  # low nibble 1, high nibble 2
    composite = oam_sprites.compose(entry(attr0(0, colour_256=False), attr1(0), 3 << 12),
                                    bytes(vram))
    assert composite.canvas[0] == 3 * 16 + 1
    assert composite.canvas[1] == 3 * 16 + 2
    assert composite.painted_banks() == [3]
    transparent = oam_sprites.compose(entry(attr0(0, colour_256=False), attr1(0), 3 << 12),
                                      bytes(bytearray(oam_sprites.OBJ_VRAM_BYTES)))
    assert transparent.painted == 0 and transparent.painted_banks() == []


def test_flips_move_the_pixels_not_the_palette() -> None:
    vram = bytearray(oam_sprites.OBJ_VRAM_BYTES)
    pixels = bytearray(64)
    pixels[0] = 5  # top-left only
    vram[0:64] = bytes(pixels)
    plain = oam_sprites.compose(entry(attr0(0), attr1(0), 0), bytes(vram))
    flipped = oam_sprites.compose(entry(attr0(0), attr1(0, hflip=True), 0), bytes(vram))
    assert plain.canvas[0] == 5 and flipped.canvas[7] == 5 and flipped.canvas[0] == 0
    both = oam_sprites.compose(entry(attr0(0), attr1(0, hflip=True, vflip=True), 0), bytes(vram))
    assert both.canvas[7 * 240 + 7] == 5


def test_a_disabled_entry_is_never_drawn_and_a_negative_x_is_clipped() -> None:
    vram = bytearray(oam_sprites.OBJ_VRAM_BYTES)
    vram[0:64] = bytes([4] * 64)
    disabled = oam_sprites.compose(entry(attr0(0, mode=2), attr1(0), 0), bytes(vram))
    assert disabled.painted == 0 and disabled.drawn == ()
    clipped = oam_sprites.compose(entry(attr0(0), attr1(0x1FC), 0), bytes(vram))  # x = -4
    assert clipped.painted == 4 * 8, "a 8x8 sprite at x=-4 paints its right four columns"
    assert clipped.canvas[0] == 4


def test_a_reserved_shape_is_reported_not_drawn() -> None:
    """Shape 3 is not a sprite the hardware draws, so it is skipped with a reason."""
    composite = oam_sprites.compose(entry(attr0(0, shape=3), attr1(0), 0),
                                    bytes(oam_sprites.OBJ_VRAM_BYTES))
    assert composite.painted == 0
    assert len(composite.skipped) == 1 and "reserved shape" in composite.skipped[0]
    assert composite.drawn == ()


def test_a_wrong_sized_dump_is_refused() -> None:
    with pytest.raises(oam_sprites.OamError, match="OAM dump is 8 bytes"):
        oam_sprites.compose(bytes(8), bytes(oam_sprites.OBJ_VRAM_BYTES))
    with pytest.raises(oam_sprites.OamError, match="OBJ VRAM window"):
        oam_sprites.compose(bytes(1024), bytes(16))
    with pytest.raises(oam_sprites.OamError, match="either 32768"):
        oam_sprites.vram_window(bytes(100))


def test_the_png_carries_the_indices_and_the_object_palette(tmp_path: Path) -> None:
    vram = bytearray(oam_sprites.OBJ_VRAM_BYTES)
    vram[0:64] = bytes([1] * 64)
    composite = oam_sprites.compose(entry(attr0(4), attr1(6), 0), bytes(vram))
    palette_words = [(index * 3) & 0x7FFF for index in range(256)]
    palette = struct.pack("<256H", *palette_words)
    colours = sprite_graphics.Palette(raw=tuple(palette_words)).rgb
    path = tmp_path / "oam.png"
    path.write_bytes(indexed_png.encode(composite.canvas, 240, 160, colours, transparent_index=0))

    pixels, width, height, read_colours, transparent = indexed_png.decode(path.read_bytes())
    assert (width, height, transparent) == (240, 160, 0)
    assert pixels == composite.canvas
    assert read_colours[1] == sprite_graphics.expand_bgr555(palette_words[1])
    assert len(oam_sprites.read_palette(palette)) == 512
