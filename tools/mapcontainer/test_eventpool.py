from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import eventpool  # noqa: E402
from testkit import rom_bytes  # noqa: E402

ROM = os.path.join(ROOT, "baserom.gba")


def refusal(call):
    try:
        call()
    except ValueError as error:
        return str(error)
    return None


def dialog_type_offset(rom, index):
    offset, _ = eventpool.record_rows(rom)[index]
    dialog = struct.unpack_from("<I", rom, offset)[0]
    return dialog - eventpool.ROM_BASE + 2


def test_the_pool_tiles_522_records_over_127328_bytes():
    rom = rom_bytes(ROM, size=0x800000)
    assert eventpool.assert_contract(rom) == eventpool.CONTRACT


def test_every_record_re_serializes_from_its_parsed_header():
    rom = rom_bytes(ROM, size=0x800000)
    assert eventpool.round_trip(rom)[eventpool.FAMILY] == {
        "records": 522, "equal": 522, "bytes": 127328}


def test_the_type_is_the_descriptor_byte_the_consumer_reads_through_the_pointer():
    rom = rom_bytes(ROM, size=0x800000)
    for offset, size in eventpool.record_rows(rom)[:64]:
        parsed = eventpool.fields(rom, offset, size)
        assert parsed["dialog_type"] == rom[parsed["dialog"] - eventpool.ROM_BASE + 2]
        assert parsed["dialog_type"] in eventpool.TYPES


def test_a_one_byte_perturbation_of_a_descriptor_type_is_refused():
    rom = rom_bytes(ROM, size=0x800000)
    image = bytearray(rom)
    at = dialog_type_offset(rom, 0)
    image[at] = 8
    assert refusal(lambda: eventpool.assert_contract(image)) == (
        "event_pool_record at 0x77c5a4 dialog 0x0877c510 has TYPE 8, not one of [0, 3, 4, 5, 6, 7]")


def test_a_record_whose_dialog_pointer_leaves_the_rom_is_refused():
    rom = rom_bytes(ROM, size=0x800000)
    image = bytearray(rom)
    offset = eventpool.record_rows(rom)[1][0]
    image[offset:offset + 4] = b"\0\0\0\0"
    assert refusal(lambda: eventpool.assert_contract(image)) == (
        "event_pool_record at 0x77c5fc dialog is 0x00000000, not a ROM address")
