from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pytest  # noqa: E402

import row_readers  # noqa: E402


def a_row(start=0x160, end=0x170):
    return (start, end)


def entry(**fields):
    base = {"family": "", "reason": "", "named": 0, "crossing": False, "grid": 0, "word_names": 0,
            "value_sites": [], "readers": [], "branches": [], "dispatch": False, "between": False}
    base.update(fields)
    return base


def test_population_refuses_a_moved_census():
    with pytest.raises(SystemExit) as caught:
        row_readers.assert_population([a_row(0, 16)])
    assert "the census moved" in str(caught.value)


def test_a_whole_word_grid_every_reader_names_is_the_pool_family():
    row = a_row()
    literals = {row: [(0x160, 0, "a"), (0x164, 0, "b"), (0x168, 0, "c"), (0x16C, 0, "d")]}
    pools, _codes = row_readers.families([row], literals, {})
    assert list(pools) == [row]


def test_one_word_with_no_reader_keeps_the_pool_row_out():
    row = a_row()
    literals = {row: [(0x160, 0, "a"), (0x164, 0, "b")]}
    pools, _codes = row_readers.families([row], literals, {})
    assert pools == {}


def test_an_unaligned_row_is_never_the_pool_family():
    row = a_row(0x162, 0x16E)
    literals = {row: [(0x162, 0, "a")]}
    pools, _codes = row_readers.families([row], literals, {})
    assert pools == {}


def test_the_class_order_puts_a_family_before_every_null_reason():
    assert row_readers.class_of(entry(family="pool")) == "pool"
    assert row_readers.class_of(entry(branches=["b"])) == "code-null"
    assert row_readers.class_of(entry(crossing=True)) == "pool-fragment"
    assert row_readers.class_of(entry(named=1)) == "pool-partial"
    assert row_readers.class_of(entry(value_sites=["x"])) == "named-data"
    assert row_readers.class_of(entry(dispatch=True)) == "after-dispatch"
    assert row_readers.class_of(entry(between=True)) == "between"
    assert row_readers.class_of(entry()) == "unreached"


def test_permuted_keeps_each_span_byte_multiset_and_the_rest_of_the_image():
    image = bytes(8) + bytes(range(16)) + bytes(8)
    shuffled = row_readers.permuted(image, [(8, 24)])
    assert len(shuffled) == len(image)
    assert sorted(shuffled[8:24]) == sorted(image[8:24])
    assert shuffled[:8] == image[:8] and shuffled[24:] == image[24:]


def test_byte_statistics_read_the_row_only():
    image = struct.pack("<IIII", 0x08000000, 0xFFFFFFFF, 0, 0x03020100) + bytes(16)
    entropy, zero, words, inside = row_readers.byte_stats(image, (0, 16))
    assert zero == 0.5
    assert words == 4 and inside == 1
    assert 0.0 <= entropy <= 3.0


def test_a_computed_jump_is_found_eight_bytes_before_the_row():
    image = bytes(6) + struct.pack("<H", 0x4487) + bytes(8)
    assert row_readers.dispatch_before(image, (8, 10))
    assert not row_readers.dispatch_before(bytes(16), (8, 10))


def test_the_per_row_line_carries_the_reader_quote_and_the_reason():
    image = bytes(0x180)
    pool = entry(family="pool", readers=[(0x160, 0x08000160, "08000160 ldr r0, [pc, #4]")])
    line = row_readers.row_line((0x160, 0x168), pool, image)
    assert line.startswith("| `0x160` | `0x168` | 8 | 0.00 | 1.00 | 2 | 0 | pool |")
    assert "08000160 ldr r0, [pc, #4] (x1)" in line
    bare = row_readers.row_line((0x160, 0x168), entry(reason="no reader"), image)
    assert "| unreached | none | no reader |" in bare


def test_the_census_text_keeps_a_verdict_section_appended_after_it():
    stored = "census\n\n" + row_readers.region_readers.BLOCK_HEAD + "\n| `0x10` |\n"
    head, tail = row_readers.split_section(stored)
    assert head == "census\n\n"
    assert tail == row_readers.region_readers.BLOCK_HEAD + "\n| `0x10` |\n"
    assert row_readers.split_section("census\n") == ("census\n", "")

