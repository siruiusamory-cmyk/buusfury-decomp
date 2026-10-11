"""The behaviour node census reads its structures correctly, proven without a ROM.

Every function in the tool takes bytes, so this test builds a small synthetic image that carries one row
table entry and a handful of nodes, and asserts what the census makes of it. No ROM, no emulator, no
private artifact: the point is that the decoder's own rules (the two node forms, the latched condition
table, the secondary slot, the odd Thumb pointer rule) hold, so a census run over a real image is reading
structures rather than guessing them.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.research import ai_node_census as census  # noqa: E402

ROM_BASE = 0x08000000
#: Big enough to reach the row table, which sits at file offset 0x70F514 and is 828 rows of 8 bytes.
IMAGE_SIZE = 0x711000


def image_with(entries: dict[int, bytes]) -> bytes:
    """An image big enough to hold the row table and whatever the caller places in it."""
    image = bytearray(IMAGE_SIZE)
    for address, payload in entries.items():
        image[address:address + len(payload)] = payload
    return bytes(image)


def plant_row(image: bytearray, selector: int, primary: int, secondary: int) -> None:
    offset = census.row_address(selector) - ROM_BASE
    struct.pack_into("<II", image, offset, primary, secondary)


def test_a_scalar_node_reads_its_param_and_child_from_their_own_slots() -> None:
    handler = 0x080188A8 | 1           # RAND, scalar form
    child = 0x08000400 | 1
    image = bytearray(IMAGE_SIZE)
    struct.pack_into("<IIII", image, 0x100, handler, 0x08000001, 0x08000003, 0x000009C4)
    struct.pack_into("<I", image, 0x110, child)

    entry = census.node(bytes(image), ROM_BASE + 0x100)
    assert entry["form"] == "scalar"
    assert entry["param"] == 0x9C4, "a scalar form keeps its param at +0x0C"
    assert entry["child"] == child, "and its child node pointer at +0x10"
    assert entry["child_slot"] == 0x10
    assert "rand16()" in entry["condition"]


def test_a_pointer_form_node_reads_its_child_from_the_param_slot() -> None:
    handler = 0x08029FE6 | 1           # SPAWN, pointer form
    child = 0x08000400 | 1
    image = bytearray(IMAGE_SIZE)
    struct.pack_into("<IIII", image, 0x200, handler, 0x08000001, 0x08000003, child)

    entry = census.node(bytes(image), ROM_BASE + 0x200)
    assert entry["form"] == "pointer"
    assert entry["child_slot"] == 0x0C
    assert entry["child"] == child, "the pointer form keeps the child in the param slot"
    assert entry["param"] == child, "so the param field and the child are the same word"


def test_the_walk_follows_the_slot_the_form_uses_and_stops_on_a_null_handler() -> None:
    root = 0x08001000 | 1
    child = 0x08002000 | 1
    image = bytearray(IMAGE_SIZE)
    struct.pack_into("<IIII", image, 0x1000, 0x0801920E | 1, 0, 0, 1)   # OR, one child
    struct.pack_into("<I", image, 0x1010, child)
    struct.pack_into("<IIII", image, 0x2000, 0, 0x08000001, 0, 0)        # null handler, real evaluator
    plant_row(image, 3, root, 0)

    entries = census.walk_row(bytes(image), 3)
    addresses = sorted(entry["address"] for entry in entries)
    assert addresses == [ROM_BASE + 0x1000, ROM_BASE + 0x2000]
    assert entries[1]["form"] == "null-handler", (
        "a node whose handler word is zero is reported as such, never followed as code")


def test_the_row_reader_reports_both_words_and_refuses_an_out_of_range_selector() -> None:
    image = bytearray(IMAGE_SIZE)
    plant_row(image, 7, 0x08000301, 0x08000305)
    entry = census.row(bytes(image), 7)
    assert entry == {"selector": 7, "primary": 0x08000301, "secondary": 0x08000305}
    with pytest.raises(ValueError):
        census.row(bytes(image), census.ROW_COUNT)


def test_the_secondary_census_counts_literal_zero_rows_separately() -> None:
    image = bytearray(IMAGE_SIZE)
    struct.pack_into("<I", image, 0x400, 0x08018F90 | 1)     # a real secondary handler (SEQ)
    plant_row(image, 0, 0x08000301, 0x08000401)
    plant_row(image, 1, 0x08000301, 0x00000000)
    counts = census.secondary_handler_census(bytes(image))
    assert counts[-1] == census.ROW_COUNT - 1, "only the planted row has a secondary word at all"
    assert counts.get(0x08018F90) == 1, "the planted secondary is counted by its handler"


def test_the_form_tables_do_not_contradict_each_other() -> None:
    overlap = census.POINTER_FORM_HANDLERS & set(census.LEAF_HANDLERS)
    assert overlap <= {0x08029FE6}, (
        "a handler is either a pointer-form leaf or a named leaf, except SPAWN which is both")
    for handler, (form, class_word, _) in census.CONDITION_HANDLERS.items():
        assert form in ("scalar", "pointer"), handler
        assert ROM_BASE <= class_word < ROM_BASE + 0x1000000, handler
