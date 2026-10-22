import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import code_xref  # noqa: E402

ROM_BASE = 0x08000000


def image_with(*halfwords):
    return b"".join(h.to_bytes(2, "little") for h in halfwords) + b"\x00" * 0x20


def test_a_thumb_load_finds_its_own_literal():
    rom = image_with(0x4802)
    sites = code_xref.scan(rom)
    assert sites["thumb"] == [(ROM_BASE, ROM_BASE + 0x0C)]


def test_a_thumb_target_is_pc_relative_and_word_aligned():
    rom = image_with(0x0000, 0x0000, 0x0000, 0x4800)
    sites = code_xref.scan(rom)
    assert sites["thumb"] == [(ROM_BASE + 6, ROM_BASE + 8)]


def test_an_arm_pc_relative_load_with_either_sign():
    rom = bytearray(b"\x00" * 0x40)
    rom[0:4] = (0xE59F0008).to_bytes(4, "little")
    rom[4:8] = (0xE51F0004).to_bytes(4, "little")
    sites = code_xref.scan(bytes(rom))
    assert sites["arm"] == [(ROM_BASE, ROM_BASE + 8 + 8),
                            (ROM_BASE + 4, ROM_BASE + 4 + 8 - 4)]
    rom[8:12] = (0xE5910008).to_bytes(4, "little")
    assert len(code_xref.scan(bytes(rom))["arm"]) == 2


def test_a_matcher_that_finds_nothing_is_not_a_negative():
    with pytest.raises(AssertionError):
        code_xref.self_check(image_with(0x0000, 0x0000))


def test_into_is_half_open_and_does_not_invent_targets():
    rom = image_with(0x4802)
    sites = code_xref.scan(rom)
    assert code_xref.into(sites["thumb"], ROM_BASE + 0x0C, ROM_BASE + 0x0D) == \
        [(ROM_BASE, ROM_BASE + 0x0C)]
    assert code_xref.into(sites["thumb"], ROM_BASE + 0x0D, ROM_BASE + 0x20) == []


def test_the_value_route_reads_the_pool_word_not_the_pool_address():
    rom = bytearray(image_with(0x4801))
    rom[0x08:0x0C] = (0x08000040).to_bytes(4, "little")
    sites = code_xref.scan(bytes(rom))
    assert code_xref.loads_into(bytes(rom), sites, 0x08000040, 0x08000041) == \
        [("thumb", ROM_BASE, ROM_BASE + 0x08, 0x08000040)]
    assert code_xref.loads_into(bytes(rom), sites, ROM_BASE + 0x08, ROM_BASE + 0x09) == []


def test_a_pool_word_holding_a_different_value_is_not_a_reference():
    rom = bytearray(image_with(0x4801))
    rom[0x08:0x0C] = (0x03000000).to_bytes(4, "little")
    sites = code_xref.scan(bytes(rom))
    assert code_xref.loads_into(bytes(rom), sites, 0x08000000, 0x08800000) == []
