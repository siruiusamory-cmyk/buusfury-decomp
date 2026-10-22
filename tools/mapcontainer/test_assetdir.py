from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import assetdir  # noqa: E402
from testkit import perturbed_record, refusal_message, rom_bytes  # noqa: E402

ROM = os.path.join(ROOT, "baserom.gba")


def test_the_directory_holds_64_records_and_its_blocks_tile_390901_bytes():
    rom = rom_bytes(ROM, size=0x800000)
    assert assetdir.assert_contract(rom) == assetdir.CONTRACT
    assert assetdir.CONTRACT == {"records": 64, "bytes": 768, "blocks": 64,
                                 "block_bytes": 390901, "first": 0x2B9BB0, "last_end": 0x3192A5}


def test_a_record_whose_byte_length_overruns_its_neighbour_is_refused():
    image = perturbed_record(assetdir, 0, "byte_length", 1)
    assert refusal_message(lambda: assetdir.assert_contract(image)) == (
        "asset_directory_64 record 0 ends at 0x082bb324, the next starts at 0x082bb323")


def test_a_record_whose_data_ptr_starts_one_late_is_refused():
    image = perturbed_record(assetdir, 1, "data_ptr", 1)
    assert refusal_message(lambda: assetdir.assert_contract(image)) == (
        "asset_directory_64 record 0 ends at 0x082bb323, the next starts at 0x082bb324")


def test_every_record_re_serializes_from_its_parsed_fields():
    rom = rom_bytes(ROM, size=0x800000)
    assert assetdir.round_trip(rom)[assetdir.DIRECTORY] == {
        "records": 64, "equal": 64, "bytes": 768}


def test_every_block_is_its_record_s_extent_and_none_touches_the_table():
    rom = rom_bytes(ROM, size=0x800000)
    blocks = assetdir.block_rows(rom)
    for (offset, size), record in zip(blocks, (assetdir.fields(rom, at, 12)
                                               for at, _ in assetdir.directory_rows(rom))):
        assert (offset, size) == (record["data_ptr"] - assetdir.ROM_BASE, record["byte_length"])
        assert assetdir.BLOCK_START <= offset and offset + size <= assetdir.BLOCK_END
    claimed = set()
    for offset, size in blocks:
        claimed.update(range(offset, offset + size))
    assert len(claimed) == 390901
    assert not claimed & set(range(assetdir.BASE, assetdir.ARRAY_END))
