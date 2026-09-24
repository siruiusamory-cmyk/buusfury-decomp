"""Synthetic and local-oracle tests for the ROM-only MAP-VIS renderer.

The synthetic tests exercise selector, atlas, layout, palette, and render logic
without committed commercial bytes. Local-ROM and VRAM checks remain gated on
private inputs and retain the older renderer as an independent code-path oracle.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import struct

import pytest

from tools.webfoot import map_render as mr
from tools.webfoot.binary import GBA_ROM_BASE, GbaRomAddress
from tools.webfoot.formats import bg_tilemap, webfoot_lz
from tools.webfoot.profile import MapEntryTableProfile, RomProfile


# --- a deliberately non-Buu map table ----------------------------------------
#
# The fixture ROM's MapEntry table lives somewhere the canonical profile does
# NOT declare, so every test that resolves a descriptor proves the address and
# the record stride came from the supplied profile. Reintroducing a Buu literal
# into `resolve_descriptor` breaks these tests; that is the point of the offset.

_SYNTHETIC_MAP_TABLE_ADDRESS = 0x080A0000
_SYNTHETIC_MAP_TABLE_COUNT = 8
_SYNTHETIC_MAP_INDEX = 3
#: Set once the fixture bytes exist: the profile's own hash for this image, so
#: `render_map`'s identity gate is satisfied by a declared identity rather than
#: by a monkeypatched module constant.
_SYNTHETIC_SHA256 = ""


def synthetic_profile(*, sha256: str | None = None) -> RomProfile:
    """The packaged canonical profile with a different map table and identity.

    Only the two facts these tests must observe are changed; every other
    declaration is the canonical profile's, so the fixture cannot pass by
    accidentally matching a second, independently invented profile.
    """
    base = mr.canonical_profile()
    return replace(
        base,
        id="synthetic_map_render_profile",
        sha256=sha256 if sha256 is not None else _SYNTHETIC_SHA256,
        map_entries=MapEntryTableProfile(
            address=GbaRomAddress(_SYNTHETIC_MAP_TABLE_ADDRESS),
            count=_SYNTHETIC_MAP_TABLE_COUNT,
            record_size=base.map_entries.record_size,
        ),
    )


# --- synthetic ROM (identity + palette only) ---------------------------------

_ROM_SIZE = 0x800000  # 8 MiB, matching the canonical image size.


def _place(rom: bytearray, address: int, data: bytes) -> None:
    offset = address - GBA_ROM_BASE
    rom[offset : offset + len(data)] = data


def _synthetic_rom() -> tuple[bytes, int]:
    """A fake ROM wired for one complete ROM-only map assembly."""
    rom = bytearray(_ROM_SIZE)

    profile = synthetic_profile()
    map_index = _SYNTHETIC_MAP_INDEX
    table = profile.map_entries
    assert table is not None
    map_entry = table.address.raw + map_index * table.record_size
    descriptor = 0x08300000
    scene_pointer_target = 0x08310000
    _place(rom, map_entry + mr.MAP_ENTRY_SCENE_POINTER_OFFSET,
           struct.pack("<I", scene_pointer_target))
    _place(rom, scene_pointer_target, struct.pack("<I", descriptor))

    remap = 0x08320000
    atlas_array = 0x08321000
    atlas = 0x08322000
    layer_record = 0x08330000
    screen = 0x08331000
    # Absolute selectors [0, 1] are delta-coded [0, 0].
    _place(rom, remap, webfoot_lz.build_stored(struct.pack("<2H", 0, 0)))
    _place(rom, atlas_array, struct.pack("<I", atlas))
    atlas_pixels = bytes([5]) * 64 + bytes([9]) * 64 + bytes(0x4000 - 128)
    _place(rom, atlas, webfoot_lz.build_stored(atlas_pixels))
    _place(rom, descriptor + 4, bytes((2, 3, 3, 3)))
    _place(rom, descriptor + 0x0C, struct.pack("<II", 0, 0))
    _place(rom, descriptor + 0x14, struct.pack("<4I", layer_record, 0, 0, 0))
    _place(rom, descriptor + 0x48, struct.pack("<II", remap, atlas_array))
    record = bytearray(0x1C)
    struct.pack_into("<I", record, 0, mr.SUPPORTED_LAYER_HANDLER)
    record[0x14:0x16] = bytes((1, 1))
    struct.pack_into("<I", record, 0x18, screen)
    _place(rom, layer_record, record)
    _place(rom, screen, webfoot_lz.build_stored(struct.pack("<1024H", *([1] * 1024))))

    # Palette: 256 RGB888 triples, a visible ramp so decode is checkable.
    palette = bytearray()
    for i in range(mr.BG_PALETTE_ENTRIES):
        palette += bytes((i, (i * 2) & 0xFF, (i * 3) & 0xFF))
    _place(rom, mr.BG_PALETTE_ADDRESS, bytes(palette))
    return bytes(rom), descriptor


def _synthetic_vram(*, tile_fill: int = 5) -> tuple[bytes, tuple[mr.LayerSpec, ...]]:
    """A tiny VRAM: a 1-tile charblock at base 0 and one screenblock at block 28.

    Every screen entry references tile 0 (the fill), so the rendered layer is a
    flat field of ``tile_fill``. One enabled BG keeps the fixture minimal.
    """
    screen_base_block = 28
    top = (screen_base_block + 1) * bg_tilemap.SCREEN_BLOCK_BYTES
    vram = bytearray(top)
    # Tile 0 at char base 0: 64 bytes of the fill (8bpp).
    vram[0 : bg_tilemap.TILE_BYTES_8BPP] = bytes([tile_fill]) * bg_tilemap.TILE_BYTES_8BPP
    # Screenblock: 1024 entries all referencing tile 0, no flip, bank 0.
    entries = struct.pack("<1024H", *([0] * 1024))
    base = screen_base_block * bg_tilemap.SCREEN_BLOCK_BYTES
    vram[base : base + len(entries)] = entries

    layers = (
        mr.LayerSpec(bg=0, char_base_block=0, screen_base_block=screen_base_block,
                     screen_size_bits=0, priority=2, color_256=True),
    )
    return bytes(vram), layers


@pytest.fixture
def synthetic_rom():
    rom, _ = _synthetic_rom()
    return rom


@pytest.fixture
def profile() -> RomProfile:
    return synthetic_profile()


def _rendering_profile(rom: bytes) -> RomProfile:
    """The synthetic profile, hashed to the fixture bytes it describes.

    `render_map` compares the image against the profile's declared identity, so
    a profile that describes *these* bytes is what makes the positive path
    reachable without stubbing a module constant.
    """
    return synthetic_profile(sha256=hashlib.sha256(rom).hexdigest())


# --- T1: identity + palette (ROM-proven) -------------------------------------

def test_parse_map_id_is_decimal():
    assert mr.parse_map_id("map:0040") == 40
    assert mr.parse_map_id("map:0003") == 3
    assert mr.parse_map_id("map:7") == 7


@pytest.mark.parametrize("bad", ["0040", "map:", "map:xx", "map:-1", "40", None, 40])
def test_parse_map_id_fails_closed(bad):
    with pytest.raises(mr.MapRenderError):
        mr.parse_map_id(bad)


def test_resolve_descriptor_walks_map_entry(synthetic_rom, profile):
    """The descriptor is reached through the row the SUPPLIED profile declares."""
    entry, _pointer, descriptor = mr.resolve_descriptor(
        synthetic_rom, _SYNTHETIC_MAP_INDEX, profile=profile
    )
    table = profile.map_entries
    assert table is not None
    assert entry == table.address.raw + _SYNTHETIC_MAP_INDEX * table.record_size
    assert descriptor == 0x08300000


def test_resolve_descriptor_uses_the_profile_address_not_a_buu_literal(synthetic_rom, profile):
    """A relocated table is found; Buu's address would resolve nothing.

    This is the parameterization proof: the fixture's table is NOT at the
    canonical profile's address, so a reintroduced Buu constant fails here.
    """
    canonical = mr.canonical_profile()
    assert profile.map_entries.address != canonical.map_entries.address
    assert profile.map_entries.address.raw == _SYNTHETIC_MAP_TABLE_ADDRESS
    # The canonical address holds no wired entry in this image, so resolving
    # against the canonical profile cannot produce the fixture's descriptor.
    with pytest.raises(mr.MapRenderError):
        mr.resolve_descriptor(synthetic_rom, _SYNTHETIC_MAP_INDEX, profile=canonical)


def test_map_index_beyond_the_profile_count_is_refused(synthetic_rom, profile):
    with pytest.raises(mr.MapRenderError, match="declared map-entry range"):
        mr.resolve_descriptor(synthetic_rom, _SYNTHETIC_MAP_TABLE_COUNT, profile=profile)


def test_bg_palette_requantises_to_five_bits(synthetic_rom):
    palette = mr.decode_bg_palette(synthetic_rom)
    assert len(palette) == 256

    def display(byte: int) -> int:
        five = byte >> 3
        return (five << 3) | (five >> 2)

    assert palette[2] == (display(2), display(4), display(6))


# --- T2: render from a synthetic VRAM ----------------------------------------

def test_render_map_from_vram_composes_and_prioritises():
    vram, layers = _synthetic_vram(tile_fill=5)
    palette = tuple((i, i, i) for i in range(256))
    result = mr.render_map_from_vram(vram, layers, palette)
    assert result.width == 256 and result.height == 256
    assert len(result.layers) == 1
    # Every tile is the fill (5), so the composite is a solid field of 5.
    assert set(result.composite) == {5}
    assert len(result.composite) == 256 * 256


def test_render_map_from_vram_priority_top_wins():
    """A lower-priority-number (on-top) layer overwrites the layer below it."""
    screen_base_a, screen_base_b = 28, 29
    top = (screen_base_b + 1) * bg_tilemap.SCREEN_BLOCK_BYTES
    vram = bytearray(top)
    # Two tiles: tile 0 = fill 5, tile 1 = fill 9.
    vram[0 : bg_tilemap.TILE_BYTES_8BPP] = bytes([5]) * bg_tilemap.TILE_BYTES_8BPP
    tb = bg_tilemap.TILE_BYTES_8BPP
    vram[tb : 2 * tb] = bytes([9]) * tb
    # Bottom layer (priority 3) references tile 0; top layer (priority 2) tile 1.
    vram[screen_base_a * bg_tilemap.SCREEN_BLOCK_BYTES:
         screen_base_a * bg_tilemap.SCREEN_BLOCK_BYTES + 2048] = struct.pack("<1024H", *([0] * 1024))
    vram[screen_base_b * bg_tilemap.SCREEN_BLOCK_BYTES:
         screen_base_b * bg_tilemap.SCREEN_BLOCK_BYTES + 2048] = struct.pack("<1024H", *([1] * 1024))
    layers = (
        mr.LayerSpec(bg=0, char_base_block=0, screen_base_block=screen_base_b,
                     screen_size_bits=0, priority=2, color_256=True),  # on top
        mr.LayerSpec(bg=1, char_base_block=0, screen_base_block=screen_base_a,
                     screen_size_bits=0, priority=3, color_256=True),  # below
    )
    palette = tuple((i, i, i) for i in range(256))
    result = mr.render_map_from_vram(bytes(vram), layers, palette)
    # Top layer's tile 1 (fill 9) is nonzero everywhere, so it wins the composite.
    assert set(result.composite) == {9}


def test_render_map_from_vram_rejects_non_bytes():
    _vram, layers = _synthetic_vram()
    with pytest.raises(mr.MapRenderError):
        mr.render_map_from_vram("not bytes", layers, tuple((0, 0, 0) for _ in range(256)))


# --- T3: ROM-only assembly ---------------------------------------------------

def test_tile_selector_delta_decode_and_charblock_assembly():
    rom, descriptor = _synthetic_rom()
    assert mr.decode_tile_selectors(rom, descriptor) == (0, 1)
    chars = mr.reconstruct_charblock_from_rom(rom, descriptor)
    assert chars[:64] == bytes([5]) * 64
    assert chars[64:128] == bytes([9]) * 64


def test_multiple_atlases_duplicate_selectors_and_unused_tiles():
    rom, descriptor = _synthetic_rom()
    changed = bytearray(rom)
    remap = 0x08320000
    atlas_array = 0x08321000
    second_atlas = 0x08327000
    # Absolute [0x0000, 0x0100, 0x0100] -> delta [0, 0x00ff, 0xffff].
    _place(changed, remap, webfoot_lz.build_stored(struct.pack("<3H", 0, 0xFF, 0xFFFF)))
    _place(changed, atlas_array, struct.pack("<2I", 0x08322000, second_atlas))
    _place(changed, second_atlas, webfoot_lz.build_stored(bytes([7]) * 64 + bytes(0x4000 - 64)))
    chars = mr.reconstruct_charblock_from_rom(bytes(changed), descriptor)
    assert mr.decode_tile_selectors(bytes(changed), descriptor) == (0, 0x100, 0x100)
    assert chars[:192] == bytes([5]) * 64 + bytes([7]) * 128


def test_render_map_is_rom_only_and_deterministic(synthetic_rom):
    """`render_map` renders against the supplied profile, not the packaged one."""
    profile = _rendering_profile(synthetic_rom)
    first = mr.render_map(synthetic_rom, "map:0003", profile=profile)
    second = mr.render_map(synthetic_rom, "map:0003", profile=profile)
    assert first == second
    assert first.width == first.height == 256
    assert set(first.composite) == {9}
    assert first.provenance["tile_selector_address"] == "0x08320000"
    # The provenance names the row this profile declares, so a Buu literal in
    # the renderer would show up here as well as in the descriptor address.
    assert first.provenance["map_entry_address"] == (
        f"{_SYNTHETIC_MAP_TABLE_ADDRESS + _SYNTHETIC_MAP_INDEX * profile.map_entries.record_size:#010x}"
    )


def test_unsupported_layer_variant_fails_closed():
    rom, descriptor = _synthetic_rom()
    changed = bytearray(rom)
    record = struct.unpack_from("<I", changed, descriptor - GBA_ROM_BASE + 0x14)[0]
    _place(changed, record, struct.pack("<I", 0x08001235))
    with pytest.raises(mr.UnsupportedMapAssemblyVariant, match="layer handler"):
        mr.reconstruct_map_assembly(bytes(changed), descriptor)


def test_render_map_refuses_unverified_rom_bytes(synthetic_rom):
    """A profile whose declared identity is not these bytes is refused."""
    with pytest.raises(mr.MapRenderError, match="SHA-256"):
        mr.render_map(synthetic_rom, "map:0003", profile=synthetic_profile())


def test_tileset_atlas_must_match_the_proven_0x4000_extent():
    rom, descriptor = _synthetic_rom()
    changed = bytearray(rom)
    atlas = 0x08322000
    _place(changed, atlas, webfoot_lz.build_stored(bytes(0x4040)))
    with pytest.raises(mr.UnsupportedMapAssemblyVariant, match="expected 0x4000"):
        mr.reconstruct_map_assembly(bytes(changed), descriptor)


# --- T4: no Qt / Workbench import --------------------------------------------

def test_module_has_no_gui_import():
    source = Path(mr.__file__).read_text(encoding="utf-8")
    for forbidden in ("PySide6", "PyQt", "workbench", "Workbench"):
        assert forbidden not in source, f"map_render must not import {forbidden}"


# --- T5: ROM + dump gated (skipped if either absent) -------------------------

_REPO = Path(__file__).resolve().parents[2]
_CANONICAL_ROM = _REPO / "roms" / "Dragon Ball Z - Buu's Fury (U).gba"
_MAP40_DUMP = _REPO / "build" / "toolkit031" / "mapvis001-map40"


@pytest.mark.skipif(
    not (_CANONICAL_ROM.exists() and (_MAP40_DUMP / "vram.bin").exists()),
    reason="canonical ROM or map40 VRAM dump not present",
)
def test_map40_renders_from_vram_capture():
    rom = _CANONICAL_ROM.read_bytes()
    vram, layers, capture_palette = mr.load_vram_dump(_MAP40_DUMP)
    result = mr.render_map_vram_reference(
        rom, "map:0040", vram,
        layers_spec=layers, capture_palette_rgb=capture_palette,
    )
    assert result.width == 256 and result.height == 256
    assert result.provenance["descriptor_address"] == "0x08293474"
    nonzero = sum(1 for p in result.composite if p)
    assert nonzero > 60000, f"composite nonzero {nonzero} too low"
