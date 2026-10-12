"""The 4bpp converter's rules, proven with no ROM.

Packing, the bank choice, the local-index mapping and the piece-word bank bits are all pure functions, so the
test drives them with hand-built bytes and asserts the arithmetic that a wrong nibble order or a wrong shift
would break.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.research import cell_4bpp as convert  # noqa: E402


def palette_of(entries: list[tuple[int, int, int]]) -> bytes:
    out = bytearray(512)
    for slot, (red, green, blue) in enumerate(entries):
        value = ((red * 31 + 127) // 255) | (((green * 31 + 127) // 255) << 5) | \
                (((blue * 31 + 127) // 255) << 10)
        struct.pack_into("<H", out, 2 * slot, value)
    return bytes(out)


def test_the_packing_is_tile_order_with_the_low_nibble_first() -> None:
    # A 16x8 piece: two tiles side by side, the left one all index 1 and the right one all index 2.
    pixels = bytes([1] * 8 + [2] * 8) * 8
    packed = convert.pack_4bpp(pixels, 16, 8, {1: 1, 2: 2})
    assert len(packed) == 64, "16x8 at 4bpp is 64 bytes"
    assert packed[0:32] == bytes([0x11] * 32), "the left tile is all local index 1"
    assert packed[32:64] == bytes([0x22] * 32), "the right tile is all local index 2"


def test_two_pixels_share_a_byte_with_the_first_pixel_in_the_low_nibble() -> None:
    pixels = bytes([3, 4] + [0] * 6) * 8
    packed = convert.pack_4bpp(pixels, 8, 8, {3: 0xA, 4: 0xB})
    assert packed[0] == 0xBA, "the first pixel is the low nibble, the second the high"


def test_the_bank_choice_maps_index_zero_to_transparent_local_zero() -> None:
    source = palette_of([(0, 0, 0), (255, 0, 0)] + [(0, 0, 0)] * 254)
    bank = palette_of([(0, 0, 0)] + [(0, 0, 0)] * 7 + [(255, 0, 0)] + [(0, 0, 0)] * 7)
    result = convert.choose_bank(bytes([0, 1]), bank + bytes(7 * 512), source)
    assert result["mapping"][0] == 0, "the source's transparent index stays local 0"
    assert result["mapping"][1] == 8, "and the red maps to the red entry"
    assert result["worst"] == 0
    assert result["local_indices"] == 2


def test_the_bank_choice_prefers_the_entry_that_is_closest() -> None:
    # Two banks: neither uses slot 0 for a colour, because local 0 is transparent. The second holds a near-red
    # at slot 5, so a source red must choose the second bank.
    banks = palette_of([(0, 0, 0)] * 16 + [(0, 0, 0)] * 5 + [(254, 0, 0)] + [(0, 0, 0)] * 10)
    source = palette_of([(0, 0, 0), (255, 0, 0)] + [(0, 0, 0)] * 254)
    result = convert.choose_bank(bytes([1]), banks, source, candidate_banks=range(2))
    assert result["bank"] == 1
    assert result["mapping"][1] == 5
    assert result["worst"] < 100, "near-red is almost exact"


def test_the_engine_copies_size_bytes_so_the_block_is_padded() -> None:
    payload = bytes([0xAB] * 2048)
    padded = convert.pad_to(4096, payload)
    assert len(padded) == 4096
    assert padded[:2048] == payload
    assert padded[2048:] == bytes(2048), "the tail is zero, and it lands in unused tile memory"
    with pytest.raises(ValueError):
        convert.pad_to(1024, payload)


def test_the_bank_rides_in_bits_25_to_27_and_only_three_bits_fit() -> None:
    assert convert.piece_bank_bits(1) == 1 << 25
    assert convert.piece_bank_bits(5) == 5 << 25
    assert convert.piece_bank_bits(7) == 7 << 25
    with pytest.raises(ValueError):
        convert.piece_bank_bits(8)


def test_a_piece_that_is_not_a_whole_number_of_tiles_is_refused() -> None:
    with pytest.raises(ValueError):
        convert.pack_4bpp(bytes(64), 10, 8, {})
