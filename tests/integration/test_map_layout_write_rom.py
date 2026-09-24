"""Canonical-ROM-gated proof of one fixed-size dominant-layer layout edit."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.export import canonical as canon
from tools.export import map_browser
from tools.export import profile_authority
from tools.export import render
from tools.webfoot.map_layout_write import MapLayoutWriter, MapLayoutWriteError


MAP = 40
LAYER = 1
CELL = 0
ORIGINAL = 0x082928DC
REPLACEMENT = 0x08292A54
FILE_OFFSET = 0x00292CA0

#: The identity every address in this writer's stack is resolved against. Read
#: from the packaged profile, which owns it, rather than from a literal here.
SUPPORTED_ROM_SHA256 = profile_authority.canonical_export_identity().sha256


@pytest.fixture(scope="module")
def canonical_input() -> tuple[Path, bytes]:
    path = Path(os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SUPPORTED_ROM_SHA256
    return path, data


def _render_target_layer(data: bytes) -> bytes:
    rom = canon.Rom(data)
    entry = canon.read_map_entries(rom)[MAP]
    layer = canon.read_layer(rom, entry.root_address, LAYER)
    block, _, _ = canon.assemble_map_char_block(rom, entry.root_address)
    entries = map_browser._stitch_dominant(rom, layer, {})
    return render.render_entries(
        entries, block.data,
        layer.chunk_x * canon.CHUNK_SIDE_TILES,
        layer.chunk_y * canon.CHUNK_SIDE_TILES,
    )


def test_fixed_width_edit_noop_inverse_and_render(
    canonical_input: tuple[Path, bytes], tmp_path: Path
) -> None:
    source_path, source = canonical_input
    source_stat = source_path.stat()
    writer = MapLayoutWriter(source)
    assert writer.chunk_pointer(MAP, LAYER, CELL) == ORIGINAL
    assert writer.chunk_pointer(MAP, LAYER, 1) == REPLACEMENT

    noop = writer.build()
    assert noop == source
    writer.set_chunk_pointer(MAP, LAYER, CELL, REPLACEMENT)
    output_path = tmp_path / "map-layout-test.gba"
    output_path.write_bytes(writer.build())
    edited = output_path.read_bytes()
    changed = [i for i, (old, new) in enumerate(zip(source, edited)) if old != new]
    assert len(edited) == len(source)
    assert changed == [FILE_OFFSET, FILE_OFFSET + 1]
    assert edited[FILE_OFFSET:FILE_OFFSET + 4] == REPLACEMENT.to_bytes(4, "little")
    assert canon.read_layer(
        canon.Rom(edited), canon.read_map_entries(canon.Rom(edited))[MAP].root_address, LAYER
    ).chunk_addresses[CELL] == REPLACEMENT
    assert source[:0xC0] == edited[:0xC0]  # header and checksum bytes

    original_pixels = _render_target_layer(source)
    edited_pixels = _render_target_layer(edited)
    assert original_pixels != edited_pixels
    width = 2 * canon.CHUNK_PIXELS
    assert any(
        original_pixels[y * width:y * width + canon.CHUNK_PIXELS]
        != edited_pixels[y * width:y * width + canon.CHUNK_PIXELS]
        for y in range(canon.CHUNK_PIXELS)
    )
    assert all(
        original_pixels[y * width + canon.CHUNK_PIXELS:(y + 1) * width]
        == edited_pixels[y * width + canon.CHUNK_PIXELS:(y + 1) * width]
        for y in range(canon.CHUNK_PIXELS)
    )
    assert original_pixels[canon.CHUNK_PIXELS * width:] == edited_pixels[canon.CHUNK_PIXELS * width:]

    writer.set_chunk_pointer(MAP, LAYER, CELL, ORIGINAL)
    inverse = writer.build()
    assert inverse == source
    assert hashlib.sha256(inverse).hexdigest() == SUPPORTED_ROM_SHA256
    assert source_path.stat().st_size == source_stat.st_size
    assert source_path.stat().st_mtime_ns == source_stat.st_mtime_ns
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == SUPPORTED_ROM_SHA256


def test_invalid_replacements_fail_closed(canonical_input: tuple[Path, bytes]) -> None:
    _, source = canonical_input
    writer = MapLayoutWriter(source)
    for bad in (0, -1, 0x100000000, 0x08292884, True):
        with pytest.raises(MapLayoutWriteError):
            writer.set_chunk_pointer(MAP, LAYER, CELL, bad)
    for map_index, slot, cell in ((-1, LAYER, CELL), (MAP, 4, CELL), (MAP, LAYER, 4), (19, 2, 0)):
        with pytest.raises(MapLayoutWriteError):
            writer.chunk_pointer(map_index, slot, cell)
    with pytest.raises(MapLayoutWriteError):
        MapLayoutWriter(source[:-1])
