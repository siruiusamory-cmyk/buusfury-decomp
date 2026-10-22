from __future__ import annotations

import os
import struct
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "mapcontainer"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "webfoot"))

import mapcontainer
import residual_causes

ROM = os.path.join(residual_causes.ROOT, "baserom.gba")


def synthetic():
    rom = bytearray(0xA0000)
    base, roots = 0x80000, (0x81000, 0x82000, 0x83000)
    for index in range(mapcontainer.ME_COUNT):
        struct.pack_into("<I", rom, mapcontainer.ME_TABLE + index * mapcontainer.ME_SIZE + 0x2C,
                         mapcontainer.ROM_BASE + base)
    for index, root in enumerate(roots):
        struct.pack_into("<I", rom, base + 4 * index, mapcontainer.ROM_BASE + root)
    struct.pack_into("<I", rom, base + 4 * len(roots), 0)
    for root in roots:
        struct.pack_into("<I", rom, root + 0x4C, mapcontainer.TILE_BANK_TABLE)
    return bytes(rom), base, roots


def test_the_root_walk_reads_its_slots_and_a_byte_rotation_leaves_none():
    rom, base, roots = synthetic()
    assert mapcontainer.root_slots(rom)[0] == list(roots)
    assert mapcontainer.map_roots(rom) == list(roots)
    turned = bytearray(rom)
    turned[base:base + 0x10] = rom[base + 1:base + 0x10] + rom[base:base + 1]
    assert mapcontainer.root_slots(bytes(turned))[0] == []
    with pytest.raises(mapcontainer.MapContainerError):
        mapcontainer.map_roots(bytes(turned))


def test_the_gap_level_null_promotes_nothing_from_a_permuted_gap():
    rom = bytearray(0x400)
    struct.pack_into("<BBH", rom, 0x100, 1, 0, 0x0351)
    struct.pack_into("<I", rom, 0x104, mapcontainer.ROM_BASE + 0x200)
    struct.pack_into("<I", rom, 0x108, mapcontainer.ROM_BASE + 0x100)
    span, claimed, gaps = (0, 0x400), [(0, 0x100)], [(0x100, 0x400)]
    assert mapcontainer.mode_row_sites(bytes(rom), span, claimed) == [(0x100, 12)]
    assert residual_causes.discovered(bytes(rom), span, claimed, gaps) == (0, 0)


def test_a_child_list_names_the_row_it_starts_and_the_permuted_array_names_none():
    rom = bytearray(0x400)
    struct.pack_into("<BBH", rom, 0x100, 2, 0, 0x0351)
    struct.pack_into("<I", rom, 0x104, mapcontainer.ROM_BASE + 0x200)
    struct.pack_into("<I", rom, 0x108, mapcontainer.ROM_BASE + 0x210)
    plan = {"all": {mapcontainer.MODE_ROW: [(0x100, 12)]}}
    rows = [(0x200, 0x240)]
    assert residual_causes.naming(bytes(rom), rows, plan) == ((1, 2), (0, 0))
    assert residual_causes.own_lists(bytes(rom), rows) == {(0x200, 0x240): 0}


@pytest.mark.skipif(not os.path.exists(ROM), reason="the retail image is not in this worktree")
def test_both_converted_causes_beat_their_byte_permuted_null():
    rom = open(ROM, "rb").read()
    rows, cause_of = residual_causes.measured(rom)
    measured = residual_causes.nulls(rom, rows, cause_of)
    assert measured["two"] == (6, 0)
    for name, (real, null) in measured.items():
        assert real > null, (name, real, null)


@pytest.mark.skipif(not os.path.exists(ROM), reason="the retail image is not in this worktree")
def test_the_set_b_naming_measures_48_rows_and_the_null_0():
    rom = open(ROM, "rb").read()
    rows, cause_of = residual_causes.measured(rom)
    assert len(rows) == 48
    measured = residual_causes.nulls(rom, rows, cause_of)
    assert measured["naming"] == (2, 0)
    lists = residual_causes.own_lists(rom, rows)
    named = residual_causes.named(rom, rows)
    assert not any(lists.values()), "a residual row of the block starts with a child-list header"
    assert sum(1 for start, end in rows
               if "map-root-field" not in named[(start, end)][0] and lists[(start, end)]) == 0
