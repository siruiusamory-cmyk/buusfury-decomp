from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, os.path.join(ROOT, "tools", "gate"), os.path.join(ROOT, "tools", "mapcontainer"),
              os.path.join(ROOT, "tools"), ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import pytest  # noqa: E402

import animframe  # noqa: E402
import gate  # noqa: E402
import region_readers  # noqa: E402


def test_offsets_round_trip_a_stride_run():
    pairs = [(0, 4), (4, 4), (8, 4), (12, 4), (16, 1), (18, 1)]
    text = region_readers.compress(pairs)
    assert text == "10:1;12:1;0..c/4:4"
    assert sorted(region_readers.expand(text)) == sorted(pairs)


def test_offsets_round_trip_two_widths():
    pairs = [(0, 1), (1, 1), (2, 2), (8, 4), (12, 4), (16, 4)]
    assert sorted(region_readers.expand(region_readers.compress(pairs))) == sorted(pairs)


def test_duplicate_offsets_do_not_carry_a_zero_step():
    pairs = [(4, 4), (4, 4), (8, 4)]
    text = region_readers.compress(pairs)
    assert "/0" not in text
    assert sorted(set(region_readers.expand(text))) == [(4, 4), (8, 4)]


def test_a_copy_return_is_the_call_site_not_the_routine():
    kind, site, text = region_readers.reader_class(0x08009B31)
    assert kind == "copy return"
    assert site == 0x08009B2C
    assert text.endswith("#0x8049120")


def test_the_copy_routine_body_is_its_own_class():
    assert region_readers.reader_class(0x08049124)[0] == "copy body"


def test_a_load_at_the_pc_is_a_field_load():
    kind, site, text = region_readers.reader_class(0x08009D04)
    assert kind == "field load"
    assert site == 0x08009D04
    assert text == "08009D04 ldr r1, [r1]"


def test_the_read_population_is_the_readers_join():
    read = region_readers.reads()
    census = region_readers.rows()
    spans = {(start, end) for start, end, _region, _klass in census}
    carried = {(section["start"], section["end"]) for section in animframe.read_manifest()}
    assert set(read) <= spans | carried
    joined = {span for span in read if span in spans}
    measured = (len(joined), sum(end - start for start, end in joined))
    assert measured == region_readers.READ_POPULATION


def test_the_population_and_the_gate_agree():
    census = region_readers.rows()
    raw = sum(length for _start, length in gate.incbin_ranges())
    assert raw == region_readers.GATE_RAW
    assert sum(end - start for start, end, _r, _k in census) == region_readers.POPULATION[1]


def test_an_unread_row_states_the_sweep_and_a_read_row_states_its_pcs():
    census = region_readers.rows()
    read = region_readers.reads()
    table = {}
    for start, end, _region, _klass in census:
        span = (start, end)
        table[span] = None if span not in read else ("copy", 0.0, 1, 1, 0, 0)
    unread = next(span for span in table if table[span] is None)
    assert region_readers.verdict(unread, read, None) == "no reader in the 452-map sweep"
    got = next(span for span in table if table[span] is not None)
    assert region_readers.verdict(got, read, table[got]).startswith("read by ")


def test_a_graphics_row_carries_the_pending_image_route_status():
    span = (0x100, 0x200)
    assert region_readers.pending(span, "graphics")
    assert region_readers.pending((0x29B308, 0x29B320), "other-compressed")
    assert not region_readers.pending((0x100, 0x200), "unknown")
    assert region_readers.verdict(span, {}, None, "graphics").startswith(
        "pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM "
        "0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the "
        "image route (docs/research/MAP_BLOCK_LAYOUTS.md); ")


def test_the_census_refuses_a_moved_population():
    with pytest.raises(SystemExit) as caught:
        region_readers.POPULATION = (1, 2)
        region_readers.rows()
    assert "the census moved" in str(caught.value)


def test_a_row_read_through_the_copy_routine_has_no_layout():
    assert "copy" in region_readers.RULES
    assert region_readers.RULES["copy"].endswith("a copy states no field and no length")
