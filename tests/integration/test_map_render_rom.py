"""Local-ROM MAP-VIS-002 integration proof; no proprietary fixtures committed."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import struct
import time

import pytest

from tools.webfoot import map_render as mr
from tools.webfoot.formats import bg_tilemap, webfoot_lz


ROM = Path(os.environ.get(
    "WEBFOOT_BUU_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"
))

EXPECTED = {
    "map:0039": {
        "descriptor": "0x08294968",
        "selectors": 259,
        "layers": ((1, 768, 512), (2, 768, 512), (3, 1024, 512)),
        "char_sha256": "e0d049253bee77fa39c8fdee10f3db25115f420a4ef2b6bd7ecd4b6f6a75839e",
        "composite_sha256": "35d3b51f0929a9d1d408786b651b314f1458028f4a5d9ae1440d8ba78388ed2b",
    },
    "map:0040": {
        "descriptor": "0x08293474",
        "selectors": 239,
        "layers": ((0, 256, 256), (1, 512, 512), (2, 512, 512), (3, 512, 512)),
        "char_sha256": "486012304609d7552b3390e3fffaf6e19f8d2d802c94794398424046224f14a7",
        "composite_sha256": "21985e5c58150499b13c29696cabadd84956708e7f901b2b6ceb2c9bd6c70f9d",
    },
}


pytestmark = pytest.mark.skipif(not ROM.exists(), reason="canonical Buu ROM not configured")


@pytest.fixture(scope="module")
def canonical_rom() -> bytes:
    data = ROM.read_bytes()
    assert hashlib.sha256(data).hexdigest() == mr.SUPPORTED_ROM_SHA256
    return data


@pytest.mark.parametrize("map_id", tuple(EXPECTED))
def test_rom_only_reconstruction_is_exact_deterministic_and_bounded(
    canonical_rom: bytes, map_id: str
) -> None:
    expected = EXPECTED[map_id]
    before = hashlib.sha256(canonical_rom).hexdigest()
    started = time.perf_counter()
    first = mr.render_map(canonical_rom, map_id)
    elapsed = time.perf_counter() - started
    second = mr.render_map(canonical_rom, map_id)
    assembly = mr.reconstruct_map_assembly(
        canonical_rom, int(expected["descriptor"], 16)
    )

    assert first == second
    assert elapsed < 3.0
    assert first.provenance["descriptor_address"] == expected["descriptor"]
    assert len(assembly.selectors) == expected["selectors"]
    assert tuple((layer.bg, layer.width, layer.height) for layer in first.layers) == expected["layers"]
    assert hashlib.sha256(assembly.char_data).hexdigest() == expected["char_sha256"]
    assert hashlib.sha256(first.composite).hexdigest() == expected["composite_sha256"]
    assert hashlib.sha256(canonical_rom).hexdigest() == before


def test_canonical_rom_file_is_unchanged_after_both_renders(canonical_rom: bytes) -> None:
    before = hashlib.sha256(ROM.read_bytes()).hexdigest()
    mr.render_map(canonical_rom, "map:0039")
    mr.render_map(canonical_rom, "map:0040")
    assert hashlib.sha256(ROM.read_bytes()).hexdigest() == before == mr.SUPPORTED_ROM_SHA256


ORACLES = {
    "map:0039": {
        "path": Path(os.environ.get("WEBFOOT_MAP39_VRAM", "")),
        "origins": {1: (54, 8), 2: (62, 8), 3: (70, 8)},
        "screen_holes": {1: (), 2: (), 3: ()},
        "char_mutations": (
            201, 205, 206, 207, 218, 220, 227, 228, 229, 230, 231, 232,
            233, 234, 235, 237, 238, 239, 240, 241, 242, 243, 249, 250,
            251, 252, 253, 254, 255, 256, 257, 258,
            879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890,
            891, 892, 893, 894, 895,
        ),
    },
    "map:0040": {
        "path": Path(os.environ.get("WEBFOOT_MAP40_VRAM", "")),
        "origins": {0: (0, 0), 1: (0, 9), 2: (0, 9), 3: (0, 9)},
        "screen_holes": {
            0: tuple(y * 32 + x for y in range(3, 8) for x in range(10, 14))
               + tuple(y * 32 + 31 for y in range(24, 29)),
            1: tuple(y * 32 + 31 for y in range(3, 9)),
            2: tuple(y * 32 + 31 for y in range(29, 32)),
            3: tuple(y * 32 + 31 for y in range(32)),
        },
        "char_mutations": tuple(range(234, 259)) + tuple(range(879, 892)),
    },
}


def _word(entry: bg_tilemap.ScreenEntry) -> int:
    return (entry.tile_index | (entry.h_flip << 10) | (entry.v_flip << 11)
            | (entry.palette_bank << 12))


def _physical_window(layer: mr.LogicalLayer, origin: tuple[int, int]) -> tuple[int, ...]:
    """Project one logical 32x32 window into the engine's circular screenblock."""
    x0, y0 = origin
    physical = [0] * 1024
    for dy in range(32):
        for dx in range(32):
            x, y = x0 + dx, y0 + dy
            assert x < layer.width_tiles and y < layer.height_tiles
            physical[(y & 31) * 32 + (x & 31)] = _word(
                layer.entries[y * layer.width_tiles + x]
            )
    return tuple(physical)


@pytest.mark.parametrize("map_id", tuple(ORACLES))
def test_vram_oracle_matches_after_enumerated_runtime_state_is_normalized(
    canonical_rom: bytes, map_id: str
) -> None:
    expected = ORACLES[map_id]
    dump_dir = expected["path"]
    if not dump_dir or not (dump_dir / "vram.bin").exists():
        pytest.skip("MAP-VIS-001 VRAM oracle not configured")
    result = mr.render_map(canonical_rom, map_id)
    assembly = mr.reconstruct_map_assembly(
        canonical_rom, int(result.provenance["descriptor_address"], 16)
    )
    vram, specs, _palette = mr.load_vram_dump(dump_dir)
    normalized = bytearray(vram)

    # The selector assembler initially writes every selected tile in sequential
    # destination order. This later gameplay capture differs only at this exact,
    # pinned set of post-load mutable tile destinations (including animation
    # ranges); normalize those bytes to the renderer's static frame-zero view.
    actual_char_mutations = tuple(
        tile for tile in range(len(assembly.char_data) // 64)
        if assembly.char_data[tile * 64:(tile + 1) * 64]
        != vram[tile * 64:(tile + 1) * 64]
    )
    assert actual_char_mutations == expected["char_mutations"]
    for tile in actual_char_mutations:
        start = tile * 64
        normalized[start:start + 64] = assembly.char_data[start:start + 64]

    layer_by_bg = {layer.bg: layer for layer in assembly.layers}
    expected_pixels: dict[int, bytes] = {}
    compared_specs = []
    for spec in specs:
        if spec.bg not in expected["origins"]:
            continue  # runtime-only layer (map 39 BG0)
        layer = layer_by_bg[spec.bg]
        physical_words = _physical_window(layer, expected["origins"][spec.bg])
        live_words = struct.unpack_from(
            "<1024H", vram, spec.screen_base_block * bg_tilemap.SCREEN_BLOCK_BYTES
        )
        holes = tuple(i for i, (wanted, live) in enumerate(zip(physical_words, live_words))
                      if wanted != live)
        assert holes == expected["screen_holes"][spec.bg]
        assert all(live_words[index] == 0 for index in holes)

        # The engine maps a global logical cell into physical screen storage by
        # masking each coordinate to five bits. Replace only the enumerated
        # unpopulated/runtime-cleared cells above; every other captured entry is
        # already the exact ROM word, including flips and palette bits.
        screen = spec.screen_base_block * bg_tilemap.SCREEN_BLOCK_BYTES
        normalized[screen:screen + 0x800] = struct.pack("<1024H", *physical_words)
        entries = tuple(bg_tilemap.ScreenEntry.decode(word) for word in physical_words)
        expected_pixels[spec.bg] = bg_tilemap.render_entries(
            assembly.char_data, entries,
            map_width_tiles=32, map_height_tiles=32, color_256=True,
        )[0]
        oracle_pixels = bg_tilemap.render_layer(
            bytes(normalized), char_base_block=0,
            screen_base_block=spec.screen_base_block,
            map_width_tiles=32, map_height_tiles=32, color_256=True,
        )[0]
        assert expected_pixels[spec.bg] == oracle_pixels
        compared_specs.append(spec)

    # Compare the independently rendered, priority-composited pixel output too.
    oracle = mr.render_map_from_vram(
        bytes(normalized), tuple(compared_specs), result.palette,
        semantic_map_id=map_id,
    )
    expected_composite = bytearray(256 * 256)
    priorities = {spec.bg: spec.priority for spec in compared_specs}
    for bg in sorted(expected_pixels, key=lambda value: (priorities[value], value), reverse=True):
        for index, value in enumerate(expected_pixels[bg]):
            if value:
                expected_composite[index] = value
    assert oracle.composite == bytes(expected_composite)

    # Every high reserved animated-tile range in the gameplay capture equals
    # one ROM frame exactly; no runtime-synthesized graphics are needed.
    descriptor = assembly.descriptor_address
    count = mr._u32(canonical_rom, descriptor + 0x0C)
    array = mr._u32(canonical_rom, descriptor + 0x10)
    for animation_index in range(count):
        animation = mr._u32(canonical_rom, array + animation_index * 4)
        offset = animation - mr.GBA_ROM_BASE
        frame_count = canonical_rom[offset]
        tile_count = canonical_rom[offset + 1]
        destination = struct.unpack_from("<H", canonical_rom, offset + 2)[0]
        live = vram[destination * 64:(destination + tile_count) * 64]
        frames = []
        for frame_index in range(frame_count):
            frame = mr._u32(canonical_rom, animation + 4 + frame_index * 4)
            frames.append(webfoot_lz.unpack_raw_stream(
                canonical_rom, frame - mr.GBA_ROM_BASE + 4, tile_count * 64
            ))
        assert live in frames
