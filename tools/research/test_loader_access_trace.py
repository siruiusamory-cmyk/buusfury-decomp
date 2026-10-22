import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import loader_access_trace as trace  # noqa: E402

BASE = 0x08000000
RANGE = (0x50, 0x60)


def image(size: int = 0x80) -> bytearray:
    return bytearray(size)


def put_halfwords(blob: bytearray, offset: int, values) -> None:
    for index, value in enumerate(values):
        struct.pack_into("<H", blob, offset + 2 * index, value)


def ldr_pc(rd: int, literal: int, address: int) -> int:
    return 0x4800 | (rd << 8) | (((literal - ((address + 4) & ~3)) // 4) & 0xFF)


def body() -> bytearray:
    blob = image()
    put_halfwords(blob, 0x00, (ldr_pc(0, 0x40, 0x00), 0x6881, 0x7041, 0x4770))
    struct.pack_into("<I", blob, 0x40, BASE + 0x50)
    return blob


def test_a_loader_reports_the_accesses_made_through_its_pointer():
    measured = trace.trace(bytes(body()), *RANGE)
    entry = measured["literals"][0]
    assert entry["target"] == 0x50
    assert entry["sites"][0]["site"] == 0x00
    assert entry["sites"][0]["accesses"] == ["ldr r0 +0x8 = 0x58", "strb r0 +0x1 = 0x51"]


def test_the_bytes_a_constant_offset_explains_are_counted_and_percentage_is_reported():
    measured = trace.trace(bytes(body()), *RANGE)
    assert measured["bytes"] == 5
    assert measured["counts"] == {"sites": 1, "in_range_sites": 0, "field_sites": 1,
                                 "indexed_sites": 0, "pass_only_sites": 0}
    assert trace.report(bytes(body()), *RANGE)[-1] == \
        "summary bytes_read_at_a_constant_offset=5 of 16 (31.25 %)"


def test_indexing_a_pointer_by_a_register_is_reported_and_explains_no_byte():
    blob = image()
    put_halfwords(blob, 0x00, (ldr_pc(2, 0x40, 0x00), 0x1881, 0x4770))
    struct.pack_into("<I", blob, 0x40, BASE + 0x50)
    measured = trace.trace(bytes(blob), *RANGE)
    assert measured["literals"][0]["sites"][0]["accesses"] == \
        ["INDEXED base + register (r1, r0, r2)"]
    assert (measured["counts"]["indexed_sites"], measured["bytes"]) == (1, 0)


def test_a_register_overwritten_by_a_load_is_not_read_again_as_the_pointer():
    blob = image()
    put_halfwords(blob, 0x00, (ldr_pc(0, 0x40, 0x00), 0x6840, 0x6881, 0x4770))
    struct.pack_into("<I", blob, 0x40, BASE + 0x50)
    measured = trace.trace(bytes(blob), *RANGE)
    assert measured["literals"][0]["sites"][0]["accesses"] == ["ldr r0 +0x4 = 0x54"]


def test_a_multi_word_load_is_one_access_with_the_register_lists_byte_count():
    blob = image()
    put_halfwords(blob, 0x00, (ldr_pc(0, 0x40, 0x00), 0xC803, 0x4770))
    struct.pack_into("<I", blob, 0x40, BASE + 0x50)
    measured = trace.trace(bytes(blob), *RANGE)
    assert measured["literals"][0]["sites"][0]["accesses"] == ["ldm r0 +0x0 = 0x50 (8 bytes)"]
    assert measured["bytes"] == 8


def test_a_call_clobbers_r0_to_r3_so_a_later_access_through_r0_is_not_reported():
    blob = image()
    put_halfwords(blob, 0x00, (ldr_pc(0, 0x40, 0x00), 0xF000, 0xF800, 0x6801, 0x4770))
    struct.pack_into("<I", blob, 0x40, BASE + 0x50)
    measured = trace.trace(bytes(blob), *RANGE)
    assert measured["literals"][0]["sites"][0]["accesses"] == []
    assert measured["counts"]["pass_only_sites"] == 1


def test_a_loader_whose_own_address_is_inside_the_range_is_flagged():
    blob = image()
    put_halfwords(blob, 0x50, (ldr_pc(0, 0x54, 0x50), 0x6800, 0x4770))
    struct.pack_into("<I", blob, 0x54, BASE + 0x58)
    measured = trace.trace(bytes(blob), *RANGE)
    assert measured["counts"]["in_range_sites"] == 1


def test_an_image_with_no_loader_reports_nothing():
    measured = trace.trace(bytes(image()), *RANGE)
    assert (measured["loaders"], measured["literals"], measured["bytes"]) == (0, [], 0)
