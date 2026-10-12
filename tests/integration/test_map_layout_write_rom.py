"""Canonical-ROM-gated proof of one fixed-size dominant-layer layout edit."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.export import canonical as canon
from tools.export import profile_authority
from tools.export import render
from tools.webfoot import map_view as mv
from tools.webfoot.map_layout_write import MapLayoutWriter, MapLayoutWriteError


MAP = 40
LAYER = 1
CELL = 0
ORIGINAL = 0x082928DC
REPLACEMENT = 0x08292A54
FILE_OFFSET = 0x00292CA0
#: A real chunk address of another map's dominant window, taken from the image.
#: It is not one map:0040 uses anywhere, so it stays the foreign-pointer refusal.
FOREIGN_CHUNK = 0x08179A50
#: A chunk map:0040's dominant layer 1 does not itself use but a sibling record of
#: the same map does: the case the widened rule makes legal.
SIBLING_CHUNK = 0x08292884

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
    from tools.webfoot.formats import bg_tilemap
    from tools.webfoot.formats import map_graphics as mg
    from tools.webfoot.packaged import packaged_profile

    reader = mg.MapGraphicsReader(data, packaged_profile())
    entry = mg.read_map_entries(reader)[MAP]
    layer = mg.read_layer(reader, entry.root_address, LAYER)
    block = mg.assemble_map_char_block(reader, entry.root_address)[0]
    entries = mg.stitch_dominant_entries(reader, layer)
    pixels, _w, _h = bg_tilemap.render_entry_words(
        block.data,
        entries,
        map_width_tiles=layer.chunk_tiles_x,
        map_height_tiles=layer.chunk_tiles_y,
        color_256=True,
    )
    return pixels


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
    for bad in (0, -1, 0x100000000, FOREIGN_CHUNK, True):
        with pytest.raises(MapLayoutWriteError):
            writer.set_chunk_pointer(MAP, LAYER, CELL, bad)
    for map_index, slot, cell in ((-1, LAYER, CELL), (MAP, 4, CELL), (MAP, LAYER, 4), (19, 2, 0)):
        with pytest.raises(MapLayoutWriteError):
            writer.chunk_pointer(map_index, slot, cell)
    with pytest.raises(MapLayoutWriteError):
        MapLayoutWriter(source[:-1])


def test_a_sibling_layers_chunk_is_accepted_and_writes_only_its_own_field(
    canonical_input: tuple[Path, bytes]
) -> None:
    """The widened rule at the write primitive: four bytes in place, nothing else."""
    _, source = canonical_input
    writer = MapLayoutWriter(source)
    assert SIBLING_CHUNK not in writer.read_layer(MAP, LAYER).chunk_addresses
    writer.set_chunk_pointer(MAP, LAYER, CELL, SIBLING_CHUNK)
    built = writer.build()
    # The two values share their upper three bytes, so only the low bytes differ;
    # what matters is that nothing outside this cell's four-byte field does.
    differing = {index for index, (a, b) in enumerate(zip(source, built)) if a != b}
    assert differing
    assert differing <= set(range(FILE_OFFSET, FILE_OFFSET + 4))
    assert built[FILE_OFFSET : FILE_OFFSET + 4] == SIBLING_CHUNK.to_bytes(4, "little")
    # Read back through the accepted reader, not through the writer: the writer's
    # constructor is the identity gate, and an edited image is deliberately not
    # the canonical image it accepts.
    from tools.webfoot.formats import map_graphics as mg
    from tools.webfoot.packaged import packaged_profile

    reader = mg.MapGraphicsReader(built, packaged_profile())
    entry = mg.read_map_entries(reader)[MAP]
    assert (
        mg.read_layer(reader, entry.root_address, LAYER).chunk_addresses[CELL]
        == SIBLING_CHUNK
    )
    assert len(built) == len(source)
    assert hashlib.sha256(source).hexdigest() == SUPPORTED_ROM_SHA256
