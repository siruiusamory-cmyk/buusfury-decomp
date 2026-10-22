from __future__ import annotations

import os
import struct
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "mapcontainer"))

import map_row_owners as owners  # noqa: E402
import mapcontainer  # noqa: E402

ROM = os.path.join(owners.ROOT, "baserom.gba")

ROOT = 0x2000
ARRAY = 0x7000
LIST = 0x4000
LISTS = 0x7100
PAYLOAD = 0x5000


def image():
    rom = bytearray(mapcontainer.ME_TABLE + mapcontainer.ME_COUNT * mapcontainer.ME_SIZE + 0x100)
    for index in range(mapcontainer.ME_COUNT):
        struct.pack_into("<I", rom, mapcontainer.ME_TABLE + index * mapcontainer.ME_SIZE + 0x2C,
                         0x08000000 + ARRAY)
    struct.pack_into("<I", rom, ROOT + 0x4C, mapcontainer.TILE_BANK_TABLE)
    struct.pack_into("<H", rom, ROOT + 0x0C, 1)
    struct.pack_into("<I", rom, ARRAY, 0x08000000 + ROOT)
    struct.pack_into("<I", rom, ROOT + 0x10, 0x08000000 + LISTS)
    struct.pack_into("<I", rom, LISTS, 0x08000000 + LIST)
    rom[LIST], rom[LIST + 1] = 1, 0
    struct.pack_into("<H", rom, LIST + 2, min(mapcontainer.MODE_TAGS))
    struct.pack_into("<I", rom, LIST + 4, 0x08000000 + PAYLOAD)
    return bytes(rom)


def test_a_list_names_the_row_its_payload_starts_in():
    rows = [{"group": "set_b", "start": PAYLOAD, "end": PAYLOAD + 0x100}]
    found = owners.table(image(), rows)
    assert 0 in found[0]["owners"]
    assert found[0]["families"] == ["child_list_row"]


def test_a_row_no_chain_reaches_is_owner_unknown():
    rows = [{"group": "set_a", "start": 0x6000, "end": 0x6100}]
    found = owners.table(image(), rows)
    assert found[0]["owners"] == []
    assert owners.csv_text(found).splitlines()[1].endswith("owner unknown,")


def test_the_committed_owner_table_carries_a_header_and_one_line_per_row():
    with open(owners.CSV_OUT, encoding="ascii") as handle:
        text = handle.read()
    assert text.startswith("group,start,end,bytes,owners,families\n")
    assert len(text.splitlines()) == 101


@pytest.mark.skipif(not os.path.exists(ROM), reason="the retail image is not in this worktree")
def test_the_committed_owner_table_matches_the_measured_chain():
    owners.check(target_rows=owners.rows(), rom_path=ROM)


@pytest.mark.skipif(not os.path.exists(ROM), reason="the retail image is not in this worktree")
def test_the_owner_check_refuses_a_perturbed_table(tmp_path):
    with open(owners.CSV_OUT, encoding="ascii") as handle:
        text = handle.read()
    at = text.index("map:0038")
    broken = text[:at] + "map:0039" + text[at + len("map:0038"):]
    path = tmp_path / "owners.csv"
    path.write_text(broken, encoding="ascii")
    try:
        owners.check(path=str(path), target_rows=owners.rows(), rom_path=ROM)
    except SystemExit as refused:
        assert "does not match the bytes" in str(refused)
    else:
        raise AssertionError("a perturbed owner table was accepted")
