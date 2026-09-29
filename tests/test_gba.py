"""Address model and cartridge-header codec.

Portable: needs no ROM. The ROM-gated half of the header check lives in
tests/test_rom_map.py and tests/test_fixed_regions.py.
"""

from __future__ import annotations

import pytest

from buusfury import gba


# ---------------------------------------------------------------------------
# address conversion - the invariant the whole project rests on
# ---------------------------------------------------------------------------
def test_rom_base_and_size():
    assert gba.ROM_BASE == 0x08000000
    assert gba.ROM_SIZE == 8_388_608
    assert gba.ROM_END == 0x08800000


@pytest.mark.parametrize("offset", [0, 1, 4, 0xC0, 0x158, 0x5792C, 0x7B89A8, 0x7FFFFF])
def test_offset_to_address_round_trips(offset):
    address = gba.to_address(offset)
    assert address == 0x08000000 + offset
    assert gba.to_offset(address) == offset


@pytest.mark.parametrize("offset", [0, 0x1234, 0x7FFFFF])
def test_conversion_is_consistent(offset):
    assert gba.to_offset(gba.to_address(offset)) == offset
    assert gba.to_address(gba.to_offset(0x08000000 + offset)) == 0x08000000 + offset


@pytest.mark.parametrize("offset", [-1, gba.ROM_SIZE, gba.ROM_SIZE + 1])
def test_out_of_range_offsets_are_refused(offset):
    with pytest.raises(gba.AddressError):
        gba.to_address(offset)


@pytest.mark.parametrize("address", [0, 0x07FFFFFF, 0x08800000, 0x02000000, 0xFFFFFFFF])
def test_out_of_range_addresses_are_refused(address):
    with pytest.raises(gba.AddressError):
        gba.to_offset(address)


def test_in_cartridge_matches_the_bounds():
    assert gba.in_cartridge(gba.ROM_BASE)
    assert gba.in_cartridge(gba.ROM_END - 1)
    assert not gba.in_cartridge(gba.ROM_BASE - 1)
    assert not gba.in_cartridge(gba.ROM_END)
    assert not gba.in_cartridge(0x03000000)


# ---------------------------------------------------------------------------
# address-space classification
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "value,expected",
    [
        (0x02000000, "ewram"),
        (0x0203FFFF, "ewram"),
        (0x03000000, "iwram"),
        (0x03007FFF, "iwram"),
        (0x04000000, "io"),
        (0x05000000, "palette"),
        (0x06000000, "vram"),
        (0x07000000, "oam"),
        (0x08000000, "rom"),
        (0x087FFFFF, "rom"),
        (0x0E000000, "sram"),
        (0x00000000, "bios"),
    ],
)
def test_classify_address(value, expected):
    assert gba.classify_address(value) == expected


@pytest.mark.parametrize("value", [0x01000000, 0x087000000, 0xFFFFFFFF, 0x12345678])
def test_unmapped_values_are_not_classified(value):
    assert gba.classify_address(value) is None


def test_pointer_spaces_exclude_mmio():
    """MMIO almost never holds a pointer; a census must not treat it as one."""
    assert "io" not in gba.POINTER_SPACES
    assert "palette" not in gba.POINTER_SPACES
    assert "vram" not in gba.POINTER_SPACES
    assert set(gba.POINTER_SPACES) == {"ewram", "iwram", "rom"}


# ---------------------------------------------------------------------------
# code pointers and the Thumb bit
# ---------------------------------------------------------------------------
def test_thumb_bit_selects_the_instruction_set():
    assert gba.is_thumb_pointer(0x0800419D)
    assert not gba.is_thumb_pointer(0x0800419C)
    assert gba.normalise_code_pointer(0x0800419D) == (0x0800419C, "thumb")
    assert gba.normalise_code_pointer(0x0800419C) == (0x0800419C, "arm")


# ---------------------------------------------------------------------------
# header codec
# ---------------------------------------------------------------------------
def test_header_offsets_tile_the_header():
    spans = [
        (gba.ENTRY_BRANCH_OFFSET, gba.ENTRY_BRANCH_END),
        (gba.BOOT_LOGO_OFFSET, gba.BOOT_LOGO_END),
        (gba.TITLE_OFFSET, gba.TITLE_OFFSET + gba.TITLE_LENGTH),
        (gba.GAME_CODE_OFFSET, gba.GAME_CODE_OFFSET + gba.GAME_CODE_LENGTH),
        (gba.MAKER_CODE_OFFSET, gba.MAKER_CODE_OFFSET + gba.MAKER_CODE_LENGTH),
        (gba.FIXED_VALUE_OFFSET, gba.FIXED_VALUE_OFFSET + 1),
        (gba.MAIN_UNIT_CODE_OFFSET, gba.MAIN_UNIT_CODE_OFFSET + 1),
        (gba.DEVICE_TYPE_OFFSET, gba.DEVICE_TYPE_OFFSET + 1),
        (gba.RESERVED_1_OFFSET, gba.RESERVED_1_OFFSET + gba.RESERVED_1_LENGTH),
        (gba.SOFTWARE_VERSION_OFFSET, gba.SOFTWARE_VERSION_OFFSET + 1),
        (gba.HEADER_CHECKSUM_OFFSET, gba.HEADER_CHECKSUM_OFFSET + 1),
        (gba.RESERVED_2_OFFSET, gba.RESERVED_2_OFFSET + gba.RESERVED_2_LENGTH),
    ]
    cursor = 0
    for start, end in spans:
        assert start == cursor, f"header field starts at 0x{start:X}, expected 0x{cursor:X}"
        cursor = end
    assert cursor == gba.HEADER_END == 0x00C0


def test_boot_logo_is_the_mandated_platform_constant():
    """156 bytes, and it must be the standard GBA logo rather than game content."""
    logo = gba.load_boot_logo()
    assert len(logo) == gba.BOOT_LOGO_LENGTH == 156
    # The first eight bytes of the mandated logo. Asserted so that a future edit
    # to data/gba_boot_logo.bin cannot silently make the header non-bootable.
    assert logo[:8] == bytes.fromhex("24ffae51699aa221")
    assert logo[-4:] == bytes.fromhex("21d4f807")


def test_checksum_covers_the_documented_range():
    assert gba.CHECKSUM_FIRST == 0x00A0
    assert gba.CHECKSUM_LAST == 0x00BC
    assert gba.CHECKSUM_SEED == 0x19


def test_checksum_is_the_seeded_negated_sum():
    header = bytearray(0xC0)
    header[0xA0:0xAC] = b"DBZBUUSFURY\x00"
    header[0xAC:0xB0] = b"BG3E"
    header[0xB0:0xB2] = b"70"
    header[0xB2] = 0x96
    expected = (-(0x19 + sum(header[0xA0:0xBD]))) & 0xFF
    assert gba.compute_header_checksum(header) == expected


def test_decode_header_rejects_a_short_buffer():
    with pytest.raises(gba.AddressError):
        gba.decode_header(b"\x00" * 0x40)


def test_encode_ascii_pads_and_refuses_overflow():
    assert gba.encode_ascii("BG3E", 4) == b"BG3E"
    assert gba.encode_ascii("70", 2) == b"70"
    assert gba.encode_ascii("70", 4) == b"70\x00\x00"
    with pytest.raises(gba.AddressError):
        gba.encode_ascii("TOOLONG", 4)
