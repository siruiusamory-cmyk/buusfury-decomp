from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import ainodes  # noqa: E402
import endromcontainer  # noqa: E402
import mapcontainer  # noqa: E402
import rowtable  # noqa: E402
from testkit import rom_bytes  # noqa: E402

ROM = os.path.join(ROOT, "baserom.gba")


def test_the_table_holds_828_rows_of_two_rom_pointers():
    rom = rom_bytes(ROM, size=0x800000)
    assert rowtable.assert_contract(rom) == {"records": 828, "bytes": 6624, "distinct": 1022}
    assert rowtable.rows(rom)[0] == (0x70F514, 8)
    assert rowtable.rows(rom)[-1] == (0x70F514 + 8 * 827, 8)


def test_every_row_re_serializes_from_its_parsed_fields():
    rom = rom_bytes(ROM, size=0x800000)
    assert rowtable.round_trip(rom) == {"records": 828, "equal": 828, "bytes": 6624}


def test_the_table_shares_no_byte_with_the_node_family_or_a_container():
    rom = rom_bytes(ROM, size=0x800000)
    occupied = set()
    for offset, size in ainodes.rows(rom):
        occupied.update(range(offset, offset + size))
    for offset in endromcontainer.container_offsets(rom):
        member = mapcontainer.decode(rom, offset, endromcontainer.MAX_PAYLOAD)
        occupied.update(range(offset, offset + member.stored_size))
    claimed = set()
    for offset, size in rowtable.rows(rom):
        claimed.update(range(offset, offset + size))
    assert not (claimed & occupied)
    assert len(claimed) == 6624
