from __future__ import annotations

import os
import pytest
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import testkit

import hook_map
import written

PAGE = os.path.join(hook_map.ROOT, hook_map.OUT)


def test_mode_of_finds_the_row_that_holds_the_address():
    table = [(0x08001000, 8, "thumb"), (0x08001008, 16, "arm")]
    assert hook_map.mode_of(0x0800100A, table) == "arm"
    assert hook_map.mode_of(0x08001000, table) == "thumb"


def test_an_address_inside_no_exported_row_is_refused():
    with pytest.raises(SystemExit) as refused:
        hook_map.mode_of(0x08002000, [(0x08001000, 8, "thumb")])
    assert "inside no exported code row" in str(refused.value)


def test_shown_address_is_a_bus_address_for_rom_and_a_file_offset_below_it():
    assert hook_map.shown_address(0x08009B2C) == "0x08009B2C"
    assert hook_map.shown_address(0x757EE8) == "0x757EE8"


def test_a_committed_page_that_differs_is_reported_by_line(tmp_path):
    path = os.path.join(str(tmp_path), "page.md")
    with open(path, "w", encoding="ascii", newline="\n") as handle:
        handle.write("one\ntwo\n")
    assert written.difference(path, "one\ntwo\n") is None
    assert "line 1" in written.difference(path, "ONE\ntwo\n")


def test_the_tracked_hook_map_is_the_one_the_image_and_the_pages_derive():
    testkit.require(hook_map.ROM, "no image, so no instruction can be quoted")
    assert hook_map.main(["--check"]) == 0


def test_every_row_of_the_page_carries_one_of_the_three_statuses():
    cells = [line.rsplit("|", 2)[1].strip()
             for line in open(PAGE, encoding="ascii")
             if line.startswith("| `0x") or line.startswith("| none |")]
    assert cells
    assert set(cells) <= set(hook_map.STATUSES)
    assert set(hook_map.STATUSES) <= set(cells)
