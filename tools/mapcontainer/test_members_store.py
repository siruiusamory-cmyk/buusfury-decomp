from __future__ import annotations

import dataclasses
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "webfoot"))

import generate_mapcontainer as generator
import mapcontainer

FAKE_ROM = b"the walk and the decode are held, so no real image is read"
FAKE_KEY = "0" * 64
STORED = [mapcontainer.Member(1, 4, b"abcd", 16, 0x6B0000),
          mapcontainer.Member(1, 4, b"efgh", 16, 0x6B0010)]
FRESH = [mapcontainer.Member(1, 4, b"ijkl", 16, 0x6B0020)]


class Walk:

    def __init__(self):
        self.calls = 0
        self.path = None

    def __call__(self, rom):
        self.calls += 1
        return [member.offset for member in STORED]

    def write(self, version=generator.MEMBERS_STORE_VERSION, key=FAKE_KEY):
        with open(self.path, "wb") as handle:
            pickle.dump((version, key, [member.offset for member in STORED], STORED), handle)


def held(monkeypatch, tmp_path, name="fresh"):
    walk = Walk()
    walk.path = str(tmp_path / "members.pickle")
    held_members = {"fresh": FRESH, "stored": STORED}[name]
    block = dataclasses.replace(
        generator.ENDROM, walk=walk, expected_containers=len(held_members),
        expected_marker_union=sum(member.stored_size for member in held_members),
        expected_declared={4: len(held_members)}, expected_early_union=None, expected_tails=None,
        edges=(held_members[0].offset,
               held_members[-1].offset + held_members[-1].stored_size))
    monkeypatch.setattr(generator, "BLOCK", block)
    monkeypatch.setitem(generator.BLOCKS, "endrom", block)
    monkeypatch.setattr(generator, "decode_offsets", lambda rom, offsets, workers: FRESH)
    monkeypatch.setattr(generator, "source_key", lambda rom: FAKE_KEY)
    monkeypatch.setattr(generator, "members_cache", lambda: walk.path)
    return walk


def test_a_held_store_is_returned_without_walking(monkeypatch, tmp_path):
    walk = held(monkeypatch, tmp_path, "stored")
    walk.write()
    assert generator.read_members(FAKE_ROM) == STORED
    assert walk.calls == 0


def test_a_missing_store_walks_decodes_and_stores(monkeypatch, tmp_path):
    walk = held(monkeypatch, tmp_path)
    assert not os.path.exists(walk.path)
    assert generator.read_members(FAKE_ROM) == FRESH
    assert walk.calls == 1
    assert generator.cached_members(FAKE_ROM) == ([member.offset for member in FRESH], FRESH)


def test_a_store_from_another_key_or_layout_walks(monkeypatch, tmp_path):
    walk = held(monkeypatch, tmp_path)
    walk.write(key="1" * 64)
    assert generator.read_members(FAKE_ROM) == FRESH
    assert walk.calls == 1
    walk.write(version=generator.MEMBERS_STORE_VERSION + 1)
    assert generator.read_members(FAKE_ROM) == FRESH
    assert walk.calls == 2


def test_the_store_key_is_taken_from_the_rom_alone():
    assert generator.cached_members.__code__.co_varnames[:1] == ("rom",)


if __name__ == "__main__":
    test_the_store_key_is_taken_from_the_rom_alone()
    print("PASS test_members_store")
