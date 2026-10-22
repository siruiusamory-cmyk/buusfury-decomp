from __future__ import annotations

import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tilebank"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "research"))

import animframe
import encode_cache
import pngsheet
import pytest

ROM = animframe.read_rom(os.path.join(animframe.ROOT, "baserom.gba"))


def test_the_consumer_instructions_are_the_retail_halfwords():
    animframe.pinned(ROM)


def test_every_anchored_frame_decodes_to_the_size_its_row_states():
    frames = animframe.walk(ROM)
    assert len(animframe.animrow.sites(ROM)) == animframe.MEASURED["rows"]
    assert len(frames) == animframe.MEASURED["frames"]
    assert sum(frame["consumed"] for frame in frames.values()) == animframe.MEASURED["payload"]
    for site, frame in frames.items():
        assert len(frame["decoded"]) == frame["units"] * 64
        assert frame["consumed"] == len(ROM[site + 4:site + 4 + frame["consumed"]])


def test_the_manifest_tiles_every_section_with_frames():
    frames = animframe.walk(ROM)
    sections = animframe.read_manifest()
    assert (len(sections), sum(section["bytes"] for section in sections)) == \
        (animframe.MEASURED["sections"], animframe.MEASURED["section_bytes"])
    for section in sections:
        rows = animframe.covers(frames, section["start"], section["end"])
        assert rows is not None and len(rows) == section["frames"]


def test_a_section_survives_the_image_and_the_oracle(tmp_path):
    frames = animframe.walk(ROM)
    section = animframe.read_manifest()[0]
    cached, stats, close = encode_cache.cached_compress(
        animframe.oracle(str(tmp_path)), animframe.COMPRESS,
        os.path.join(encode_cache.default_cache_dir(), animframe.CACHE))
    blob = animframe.encode(ROM, section, frames, animframe.palette(ROM), cached)
    close()
    assert blob == ROM[section["start"]:section["end"]]
    assert stats["total"] == section["frames"]
    assert blob[:4] == ROM[section["start"]:section["start"] + 4]


def test_the_image_is_written_below_the_build_directory():
    section = animframe.read_manifest()[0]
    path = animframe.image_path(section)
    assert os.path.abspath(path).startswith(os.path.join(animframe.ROOT, "build") + os.sep)
    assert path.endswith(".png")
    assert not os.path.exists(os.path.join(animframe.ROOT, "assets", "animframe"))


def test_the_palette_is_the_whole_bank():
    colors = animframe.palette(ROM)
    assert len(colors) == 256 and all(len(color) == 3 for color in colors)
    assert pngsheet.TILE_BYTES == 64 and pngsheet.TILE == 8


def test_a_frame_stream_that_differs_is_refused():
    frames = animframe.walk(ROM)
    section = dict(animframe.read_manifest()[0])
    section["bytes"] = section["bytes"] + 2
    with pytest.raises(SystemExit):
        animframe.encode(ROM, section, frames, animframe.palette(ROM),
                         lambda payload: b"\0" * 8 + bytes(len(payload)))


def test_a_changed_pixel_changes_the_re_encoded_stream(tmp_path):
    frames = animframe.walk(ROM)
    section = animframe.read_manifest()[0]
    site = animframe.covers(frames, section["start"], section["end"])[0]
    frame = frames[site]
    path = os.path.join(str(tmp_path), "frame.png")
    width, height, indices = pngsheet.sheet_of(frame["decoded"], across=frame["units"])
    pngsheet.write_indexed(path, width, height, indices, animframe.palette(ROM))
    back = pngsheet.read_indexed(path)
    payload = pngsheet.payload_of(back[2], back[0], back[1], frame["units"],
                                  across=frame["units"])
    assert payload == frame["decoded"]
    edited = bytearray(back[2])
    edited[0] = (edited[0] + 1) & 0xFF
    pngsheet.write_indexed(path, back[0], back[1], edited, back[3])
    after = pngsheet.read_indexed(path)
    changed = pngsheet.payload_of(after[2], after[0], after[1], frame["units"],
                                  across=frame["units"])
    assert changed[0] != payload[0]
    cached, _stats, close = encode_cache.cached_compress(
        animframe.oracle(str(tmp_path)), animframe.COMPRESS,
        os.path.join(encode_cache.default_cache_dir(), animframe.CACHE))
    stored = cached(changed)
    close()
    assert stored[:8] == struct.pack("<II", 1, len(changed))
    assert stored[8:] != ROM[site + 4:site + 4 + frame["consumed"]]
