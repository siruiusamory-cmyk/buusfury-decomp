from dataclasses import replace

import pytest

from tests.helpers import make_synthetic_rom, profile_for
from tools.webfoot.formats.map_entry import (
    MAP_ENTRY_LAYOUT,
    MAP_ENTRY_SIZE,
    MapEntry,
    MapEntryLengthError,
    MapEntryProfileError,
    MapEntryValueError,
    read_map_entry_table,
    resolve_map_entry_table_range,
)
from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.profile import MapEntryTableProfile, RomProfileCatalog


ZERO_ENTRY = MapEntry(*([0] * len(MAP_ENTRY_LAYOUT)))


def test_all_zero_record_round_trips():
    encoded = bytes(MAP_ENTRY_SIZE)

    assert MapEntry.from_bytes(encoded) == ZERO_ENTRY
    assert ZERO_ENTRY.to_bytes() == encoded


def test_maximum_width_values_round_trip():
    values = [0xFF] * 12 + [0xFFFFFFFF] * 11
    entry = MapEntry(*values)

    assert MapEntry.from_bytes(entry.to_bytes()) == entry
    assert len(entry.to_bytes()) == MAP_ENTRY_SIZE


def test_distinct_byte_pattern_round_trips_without_normalization():
    original = bytes(range(MAP_ENTRY_SIZE))

    assert MapEntry.from_bytes(original).to_bytes() == original


def test_u32_fields_are_explicitly_little_endian():
    entry = replace(
        ZERO_ENTRY,
        unknown_0c=0x44332211,
        triggers_pointer_raw=0x08012345,
        variation_array_pointer_raw=0,
    )
    encoded = entry.to_bytes()

    assert encoded[0x0C:0x10] == b"\x11\x22\x33\x44"
    assert encoded[0x10:0x14] == b"\x45\x23\x01\x08"
    assert encoded[0x2C:0x30] == b"\x00\x00\x00\x00"


@pytest.mark.parametrize("length", [0, MAP_ENTRY_SIZE - 1, MAP_ENTRY_SIZE + 1])
def test_invalid_input_lengths_are_rejected(length):
    with pytest.raises(MapEntryLengthError, match="exactly"):
        MapEntry.from_bytes(bytes(length))


@pytest.mark.parametrize(
    "field,value",
    [
        ("output_raw", -1),
        ("output_raw", 0x100),
        ("output_raw", True),
        ("music_id_raw", -1),
        ("music_id_raw", 0x1_0000_0000),
    ],
)
def test_out_of_range_serialization_is_rejected(field, value):
    with pytest.raises(MapEntryValueError, match=field):
        replace(ZERO_ENTRY, **{field: value}).to_bytes()


def test_explicit_layout_covers_every_record_byte_exactly_once():
    coverage = [0] * MAP_ENTRY_SIZE
    for item in MAP_ENTRY_LAYOUT:
        for offset in range(item.offset, item.offset + item.width):
            coverage[offset] += 1

    assert len(MAP_ENTRY_LAYOUT) == len(ZERO_ENTRY.__dataclass_fields__)
    assert coverage == [1] * MAP_ENTRY_SIZE


#: A synthetic ROM claims this id so it is matched against a real packaged
#: contract; the point of the spoofing test is that borrowing a packaged id
#: does not buy access, because the hashes still have to match.
PACKAGED_PROFILE_ID = "buus_fury_usa_rev0_01c1707f"


def synthetic_table_rom() -> tuple[bytes, RomProfileCatalog]:
    table_offset = 0xC0
    data = bytearray(make_synthetic_rom(game_code="BG3E", size=0x200))
    first = bytes(range(MAP_ENTRY_SIZE))
    second = bytes(reversed(range(MAP_ENTRY_SIZE)))
    data[table_offset : table_offset + MAP_ENTRY_SIZE] = first
    data[table_offset + MAP_ENTRY_SIZE : table_offset + MAP_ENTRY_SIZE * 2] = second
    frozen = bytes(data)
    profile = profile_for(
        frozen,
        id=PACKAGED_PROFILE_ID,
        tables={
            "map_entries": {
                "address": 0x08000000 + table_offset,
                "count": 2,
                "record_size": MAP_ENTRY_SIZE,
            }
        },
    )
    return frozen, RomProfileCatalog([profile])


def test_spoofed_target_profile_is_rejected(tmp_path):
    """A local profile may not borrow a packaged id to authorise other bytes.

    The catalog here is internally consistent - it hashes the synthetic ROM
    correctly, so identification succeeds - and it names a packaged profile id.
    Access must still be refused, because the packaged contract is what
    authorises the read, not the supplied file.

    The refusal names the table metadata rather than the hashes because the
    supplied extents are compared first; both checks would refuse this ROM, and
    the earlier one is the more specific complaint.
    """
    data, catalog = synthetic_table_rom()
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)

    with pytest.raises(MapEntryProfileError, match="conflicts with the packaged"):
        read_map_entry_table(rom, catalog)


def test_profile_not_in_the_packaged_catalog_is_rejected(tmp_path):
    """A verified profile the packaged catalog does not carry has no contract.

    This replaces TOOLKIT-004's "supports only <one id>" check. The refusal is
    now about the absence of a packaged contract rather than about the profile
    failing to be one specific game, which is what lets a second game be added
    by declaring it rather than by editing this gate.
    """
    data = make_synthetic_rom()
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)
    catalog = RomProfileCatalog(
        [
            profile_for(
                data,
                id="different_profile",
                tables={
                    "map_entries": {
                        "address": 0x080000C0,
                        "count": 1,
                        "record_size": MAP_ENTRY_SIZE,
                    }
                },
            )
        ]
    )

    with pytest.raises(MapEntryProfileError, match="packaged catalog has no"):
        read_map_entry_table(rom, catalog)


def test_verified_profile_without_the_capability_is_rejected(tmp_path):
    """Not declaring the table is refused by name, never by falling through."""
    data = make_synthetic_rom()
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)
    catalog = RomProfileCatalog([profile_for(data, id="different_profile")])

    with pytest.raises(MapEntryProfileError, match="does not declare map_entries"):
        read_map_entry_table(rom, catalog)


def test_table_that_extends_past_rom_is_rejected():
    table = MapEntryTableProfile(
        address=GbaRomAddress(0x080000F0),
        count=1,
        record_size=MAP_ENTRY_SIZE,
    )

    with pytest.raises(MapEntryProfileError, match="beyond"):
        resolve_map_entry_table_range(table, 0x100)


def test_wrong_configured_record_size_is_rejected():
    table = MapEntryTableProfile(
        address=GbaRomAddress(0x080000C0),
        count=1,
        record_size=MAP_ENTRY_SIZE - 1,
    )

    with pytest.raises(MapEntryProfileError, match="size must be"):
        resolve_map_entry_table_range(table, 0x100)
