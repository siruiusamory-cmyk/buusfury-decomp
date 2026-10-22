from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import assetdir2  # noqa: E402
from testkit import perturbed_record, refusal_message, rom_bytes  # noqa: E402

ROM = os.path.join(ROOT, "baserom.gba")

REFUSALS = (
    (0, "byte_length", 1,
     "asset_directory_79 record 0 ends at 0x0831b787, the next starts at 0x0831b786"),
    (1, "data_ptr", 1,
     "asset_directory_79 record 0 ends at 0x0831b786, the next starts at 0x0831b787"),
    (78, "byte_length", -1,
     "asset_directory_79 record 78 ends at 0x0836d189, not 0x0836d18a"),
)


@pytest.mark.parametrize("index,field,delta,message", REFUSALS)
def test_a_one_byte_move_of_a_record_is_refused(index, field, delta, message):
    image = perturbed_record(assetdir2, index, field, delta)
    assert refusal_message(lambda: assetdir2.assert_contract(image)) == message


def test_the_directory_holds_79_records_and_its_blocks_tile_343010_bytes():
    rom = rom_bytes(ROM, size=0x800000)
    assert assetdir2.assert_contract(rom) == assetdir2.CONTRACT
    assert assetdir2.CONTRACT == {"records": 79, "bytes": 948, "blocks": 79,
                                  "block_bytes": 343010, "first": 0x3195A8, "last_end": 0x36D18A}


def test_every_record_re_serializes_from_its_parsed_fields():
    rom = rom_bytes(ROM, size=0x800000)
    assert assetdir2.round_trip(rom)[assetdir2.DIRECTORY] == {
        "records": 79, "equal": 79, "bytes": 948}


def test_the_two_bytes_between_the_blocks_and_the_table_stay_outside_both_families():
    rom = rom_bytes(ROM, size=0x800000)
    assert assetdir2.GAP == 2
    blocks = assetdir2.block_rows(rom)
    claimed = set()
    for offset, size in blocks:
        claimed.update(range(offset, offset + size))
    assert len(claimed) == 343010
    assert max(offset + size for offset, size in blocks) == assetdir2.BLOCK_END
    assert not claimed & set(range(assetdir2.BASE, assetdir2.ARRAY_END))
