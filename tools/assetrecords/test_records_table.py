from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import records_table as codec

COUNT = 3
STRIDE = 52
BASE = 0x08001000
BLOCK = 0x08000000
BLOCK_END = 0x08000800
EXTRA = 0x08000800
EXTRA_END = 0x08001000


def layout():
    real = codec.load_layout()
    real.update(base=BASE, count=COUNT, stride=STRIDE, output="build/fixture.s")
    for field in real["fields"]:
        block = field.get("pointer")
        if block:
            if field["name"] == "extra":
                block.update(label="|unk_08000800|", base=EXTRA, limit=EXTRA_END)
            else:
                block.update(label="|unk_08000000|", base=BLOCK, limit=BLOCK_END)
    return real


def value(field, index):
    if field.get("pointer"):
        if field["name"] == "frame_a":
            return BLOCK + 4 * index
        if field["name"] == "frame_b":
            return BLOCK_END - 4 * (index + 1)
        return EXTRA + index if index else 0
    if field.get("domain"):
        return field["domain"][index % len(field["domain"])]
    return 0x28E + index + field["offset"]


def record(index):
    return {field["name"]: value(field, index) for field in layout()["fields"]}


def test_the_committed_layout_is_18_fields_in_13_words_of_52_bytes():
    real = codec.load_layout()
    assert (len(real["fields"]), len({field["offset"] // 4 for field in real["fields"]}),
            real["stride"]) == (18, 13, 52)


def fixture():
    rom = bytearray(0x2000)
    for index in range(COUNT):
        at = BASE - 0x08000000 + index * STRIDE
        rom[at:at + STRIDE] = codec.blob([record(index)], layout())
    return bytes(rom)


MUSIC = os.path.join(HERE, "musicrecords_layout.json")
ROM = os.path.join(os.path.dirname(os.path.dirname(HERE)), "baserom.gba")


def music_layout():
    return codec.load_layout(MUSIC)


def music_rom():
    return open(ROM, "rb").read()


def test_the_music_layout_is_53_records_of_20_bytes_over_its_row():
    real = music_layout()
    assert (real["base"], real["count"], real["stride"]) == (0x083BB78C, 53, 20)
    assert real["count"] * real["stride"] == 1060 == 0x3BBBB0 - 0x3BB78C


def test_the_music_table_round_trips_the_image():
    real = music_layout()
    rom = music_rom()
    records = codec.parse(rom, real)
    start = real["base"] - 0x08000000
    assert codec.blob(records, real) == rom[start:start + 1060]
    assert codec.reread(codec.source(records, real), real) == rom[start:start + 1060]
    assert all(record["samples"] == 0x0836D18C and record["block"] == 0x0836D540
               and record["pad"] == 0 for record in records)


def test_a_swapped_music_pointer_field_is_not_byte_identical():
    real = music_layout()
    rom = music_rom()
    records = codec.parse(rom, real)
    swapped = [dict(record, entries=record["ramp"], ramp=record["entries"])
               for record in records]
    assert codec.blob(swapped, real) != codec.blob(records, real)


def main():
    tests = [
        test_the_committed_layout_is_18_fields_in_13_words_of_52_bytes,
        test_a_parse_and_emit_round_trip,
        test_the_emitted_source_reads_back_as_the_same_bytes,
        test_a_swapped_pair_of_fields_is_not_byte_identical,
        test_an_out_of_range_pointer_is_refused,
        test_a_perturbed_stride_is_refused,
        test_a_record_count_that_is_not_the_layouts_is_refused,
        test_the_music_layout_is_53_records_of_20_bytes_over_its_row,
        test_the_music_table_round_trips_the_image,
        test_a_swapped_music_pointer_field_is_not_byte_identical,
    ]
    for test in tests:
        test()
        print("PASS %s" % test.__name__)


def test_a_parse_and_emit_round_trip():
    rom = fixture()
    records = codec.parse(rom, layout())
    assert len(records) == COUNT
    assert records[1]["asset_id"] == 0x28E + 1 + 2
    start = BASE - 0x08000000
    assert codec.blob(records, layout()) == rom[start:start + COUNT * STRIDE]


def test_the_emitted_source_reads_back_as_the_same_bytes():
    rom = fixture()
    records = codec.parse(rom, layout())
    text = codec.source(records, layout())
    assert "DCW" in text and "DCD" in text
    assert "|unk_08000000| + 0x0004" in text, text
    start = BASE - 0x08000000
    assert codec.reread(text, layout()) == rom[start:start + COUNT * STRIDE]


def test_a_swapped_pair_of_fields_is_not_byte_identical():
    real = layout()
    swapped = layout()
    free = [field for field in swapped["fields"]
            if field["type"] == "u16" and not field.get("pointer") and "domain" not in field]
    assert len(free) >= 2, "the layout needs two unconstrained u16 fields for this check"
    first, second = free[0], free[1]
    first_at, second_at = swapped["fields"].index(first), swapped["fields"].index(second)
    swapped["fields"][first_at], swapped["fields"][second_at] = (
        swapped["fields"][second_at], swapped["fields"][first_at])
    assert swapped["fields"] != real["fields"]
    assert value(first, 0) != value(second, 0)
    assert codec.blob([record(0)], swapped) != codec.blob([record(0)], real)


def test_an_out_of_range_pointer_is_refused():
    rom = bytearray(fixture())
    at = BASE - 0x08000000 + 24
    struct.pack_into("<I", rom, at, 0x08400000)
    try:
        codec.parse(bytes(rom), layout())
    except ValueError as error:
        assert "frame_a" in str(error), str(error)
    else:
        raise AssertionError("an out-of-range pointer was accepted")


def test_a_perturbed_stride_is_refused():
    try:
        codec.parse(fixture(), layout(), stride=STRIDE + 1)
    except ValueError as error:
        assert "stride" in str(error), str(error)
    else:
        raise AssertionError("a perturbed stride was accepted")


def test_a_record_count_that_is_not_the_layouts_is_refused():
    try:
        codec.parse(fixture(), layout(), count=COUNT - 1)
    except ValueError as error:
        assert "count" in str(error), str(error)
    else:
        raise AssertionError("a count the layout does not name was accepted")


if __name__ == "__main__":
    main()
