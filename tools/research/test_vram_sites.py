from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gate"))

import pytest
import vram_sites

ROM = vram_sites.read_rom(os.path.join(vram_sites.ROOT, "baserom.gba"))
ROWS = vram_sites.classify(ROM)


def find(address):
    return next((row for row in ROWS if row["site"] == address), None)


def test_the_copy_sites_are_the_measured_population():
    assert len(ROWS) == 205
    assert sum(1 for row in ROWS if row["vram"]) == 84
    assert sum(1 for row in ROWS if row["palette"] and not row["vram"]) == 34
    assert sum(1 for row in ROWS if not row["vram"] and not row["palette"]) == 87


def test_every_site_lies_in_a_transcribed_code_row():
    rows = vram_sites.code_rows()
    starts = [start for start, _end in rows]
    for row in ROWS:
        assert vram_sites.in_rows(rows, starts, row["site"] - vram_sites.ROM_BASE)


def test_the_animation_copy_resolves_the_background_base():
    row = find(0x08009B42)
    assert row is not None and row["vram"] == [0x06000000]
    assert row["family"] == "copy32"


def test_a_pair_sprite_copy_resolves_the_object_base_and_its_size():
    row = find(0x08035698)
    assert row is not None and row["vram"] == [0x06010000]
    assert row["length"] == [0x40]


def test_a_palette_copy_resolves_both_banks():
    assert find(0x0800657A)["palette"] == [0x05000000]
    assert find(0x08006586)["palette"] == [0x05000200]


def test_a_destination_that_is_not_constant_folded_is_reported_unresolved():
    assert any(not row["vram"] and not row["palette"] for row in ROWS)
