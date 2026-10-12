"""The dialogue decoder's rules, proven without a ROM.

The functions take bytes, so this test builds records and spans by hand and asserts what the decoder makes of
them: the record fields, the PROVEN handle split, the container lookup, the code-by-equality rule with 0x08's
single argument, the terminator and the rendering. No ROM, no emulator, no retail text.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.research import dialogue_codes as codes  # noqa: E402

ROM_BASE = 0x08000000
IMAGE_SIZE = 0x200000


def plant_record(image: bytearray, site: int, next_index: int, kind: int, operand: int, handle: int) -> None:
    """Pack the eight bytes by hand: `"<HBBBI"` would PAD before the handle and move every field."""
    offset = site - ROM_BASE
    struct.pack_into("<H", image, offset, next_index)
    image[offset + 2] = kind
    image[offset + 3] = operand
    struct.pack_into("<I", image, offset + 4, handle)


def test_a_record_is_eight_bytes_with_the_portrait_as_a_field() -> None:
    image = bytearray(IMAGE_SIZE)
    plant_record(image, ROM_BASE + 0x100, 7, codes.DIALOGUE_KIND, 6, 0x02A4F540)
    entry = codes.record(bytes(image), ROM_BASE + 0x100)
    assert entry["next_index"] == 7
    assert entry["kind"] == codes.DIALOGUE_KIND
    assert entry["portrait_operand"] == 6, (
        "the portrait is a RECORD FIELD: there is no portrait code in the text stream")
    assert entry["handle"] == 0x02A4F540


def test_the_handle_splits_the_way_the_proven_decoder_splits_it() -> None:
    parts = codes.handle_parts(0x02A4F540)
    assert parts["selector"] == 0, "the selector is the LOW SIX BITS, and it is already a byte offset"
    assert parts["start_units"] == 5077, "the start is bits 6..20, a 15-bit field"
    assert parts["start_bytes"] == 10154
    assert parts["length_units"] == 21, "the length is bits 21..31, an 11-bit field"
    assert parts["length_bytes"] == 42


def test_the_handle_agrees_with_the_project_decoder() -> None:
    from tools.webfoot.handles import unpack_handle
    for handle in (0x02A4F540, 0x04EECA00, 0x0301C8C0, 0x00E6AA83, 0x00000021):
        assert codes.handle_parts(handle)["selector"] == unpack_handle(handle)[0]
        assert codes.handle_parts(handle)["start_bytes"] == unpack_handle(handle)[1]
        assert codes.handle_parts(handle)["length_bytes"] == unpack_handle(handle)[2]


def test_the_container_lookup_uses_the_pool_word_as_a_table_base_and_multiplies_once() -> None:
    image = bytearray(IMAGE_SIZE)
    table = ROM_BASE + 0x1000
    struct.pack_into("<I", image, codes.CONTAINER_TABLE_FILE, table)
    struct.pack_into("<I", image, 0x1000, ROM_BASE + 0x2000)
    struct.pack_into("<I", image, 0x1000 + 4, ROM_BASE + 0x3000)
    struct.pack_into("<I", image, 0x1000 + 64, ROM_BASE + 0x8000)
    assert codes.container_address(bytes(image), 0) == ROM_BASE + 0x2000
    assert codes.container_address(bytes(image), 1) == ROM_BASE + 0x3000
    assert codes.container_address(bytes(image), 16) == ROM_BASE + 0x8000, (
        "selector 16 is byte offset 64: the selector is multiplied by four exactly once")


def test_a_code_is_recognised_by_equality_and_0x08_takes_one_argument() -> None:
    units = [0x48, 0x69, 0x08, 0x02, 0x21, 0x00, 0x0A, 0x00, 0x42]
    events = codes.decode_units(units)
    kinds = [(event["kind"], event.get("argument")) for event in events]
    assert kinds == [("glyph", None), ("glyph", None), ("ink", 2), ("box-x", None), ("terminator", None)]
    ink = events[2]
    assert ink["value"] == 0x08 and ink["argument"] == 2
    box = events[3]
    assert box["leading_only"] is True, "0x21 is consumed only as the FIRST unit"
    assert box["position"] == 4, "and its position is reported, because the rule is positional"


def test_the_glyph_run_renders_spaces_and_breaks_and_stops_at_a_terminator() -> None:
    units = [0x48, 0x69, 0x20, 0x0A, 0x79, 0x00, 0x7A]
    events = codes.decode_units(units)
    assert codes.glyph_run(events) == "Hi \ny", (
        "a break point renders as a space, a line break as a newline, and the terminator ends the run")


def test_a_value_at_or_above_the_no_ink_threshold_is_not_a_glyph() -> None:
    events = codes.decode_units([0x41, codes.NO_INK_FROM, 0x0042])
    assert events[1]["kind"] == "unreached-code"
    assert "draws nothing" in events[1]["note"]
    assert events[2]["kind"] == "glyph"


def test_the_leading_only_set_is_the_four_positional_commands() -> None:
    assert codes.LEADING_ONLY == {0x0021, 0x0023, 0x0040, 0x005E}
    for value in codes.LEADING_ONLY:
        assert value in codes.CODES
    assert 0x0050 not in codes.CODES, "the decoder must not invent a portrait code"


def test_the_layout_records_are_the_two_the_engine_has() -> None:
    assert codes.LAYOUTS[0]["wrap_limit"] == 144 and codes.LAYOUTS[0]["art"] == 0x08071758
    assert codes.LAYOUTS[1]["wrap_limit"] == 128 and codes.LAYOUTS[1]["art"] == 0x08071A6C
    assert codes.LAYOUTS[1]["portrait_operand"] == "exactly 7"
