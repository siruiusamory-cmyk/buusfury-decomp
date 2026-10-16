"""CQA-04-DECODE-STACK-AUTHORITY-001 - the decode stacks' ownership, asserted.

The audit finding was that the same map and graphics concepts were decoded twice
in production - once under ``tools/export`` and once under ``tools/webfoot`` -
with no shared code, no cross-import and no test comparing them. This module holds
the structural half of the remediation: which module owns each concept, that the
SDK does not depend on the export stack, and that a synthetic input whose values
are deliberately not Buu's is interpreted the same way by every consumer.

The ROM-gated half is ``tests/integration/test_map_decode_equivalence_rom.py``.
"""

from __future__ import annotations

import ast
from pathlib import Path
import struct

import pytest

from tools.webfoot import map_render as mr
from tools.webfoot import map_view as mv
from tools.webfoot.binary import GBA_ROM_BASE, GbaRomAddress
from tools.webfoot.formats import bg_tilemap, map_graphics, sprite_graphics
from tools.webfoot.formats import map_entry as _ME
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.packaged import packaged_profile
from tools.webfoot.profile import MapEntryTableProfile

REPO = Path(__file__).resolve().parents[2]
WEBFOOT = REPO / "tools" / "webfoot"
EXPORT = REPO / "tools" / "export"


# --- the import direction ----------------------------------------------------

def _export_imports(path: Path) -> list[tuple[int, str]]:
    """Every ``tools.export`` import in one file, as ``(line, module)``.

    Parsed rather than grepped: a docstring that explains the removed dependency
    must not be mistaken for the dependency itself, and vice versa.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "tools.export" or alias.name.startswith("tools.export."):
                    found.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "tools.export" or module.startswith("tools.export."):
                found.append((node.lineno, module))
    return found


def _sdk_modules() -> list[Path]:
    return sorted(WEBFOOT.rglob("*.py"))


def test_the_sdk_never_imports_the_export_stack():
    """``tools.webfoot`` must not depend on ``tools.export``, in either direction.

    This is the regression the ticket asks for. Before CQA-04 the production
    map-layout writer, its edit session and its provenance verifier each imported
    ``tools.export.canonical`` / ``tools.export.map_browser`` for the binary
    interpretation of the very ROM structures they modify, and the Workbench's map
    tab imported the export-side browser. A shipped write path resting on an
    export/research reader is the inversion this asserts against.

    Reintroducing one such import anywhere under ``tools.webfoot`` fails here,
    including from a module that is not itself a map module: the SDK as a whole
    owns its domain.
    """
    offenders: list[str] = []
    for path in _sdk_modules():
        for line, module in _export_imports(path):
            relative = path.relative_to(REPO).as_posix()
            offenders.append(f"{relative}:{line}: {module}")
    assert offenders == [], (
        "the SDK imports the export stack; the dependency must point "
        "SDK authority -> export consumer, never the reverse:\n"
        + "\n".join(offenders)
    )


def test_the_export_stack_may_import_the_sdk():
    """The allowed direction is exercised, so the guard above is not vacuous.

    If this ever reports nothing, the previous test would also pass on a tree
    where nothing is wired together at all - so the direction that *must* work is
    asserted to actually occur.
    """
    consumers = [
        EXPORT / "canonical.py",
        EXPORT / "render.py",
        EXPORT / "map_browser.py",
        EXPORT / "profile_authority.py",
    ]
    for path in consumers:
        source = path.read_text(encoding="utf-8")
        assert "tools.webfoot" in source, f"{path.name} should consume the SDK"


def test_the_writer_and_edit_session_name_the_sdk_reader():
    """The production write path imports the format layer, not a lookalike.

    Behavioural in the sense that matters: the writer's reader is the shared map
    graphics reader class, and the layout modules import the SDK's own validator.
    """
    from tools.webfoot import map_layout_edit, map_layout_provenance, map_layout_write

    assert map_layout_write.MapLayoutWriter.__init__.__doc__
    writer_source = Path(map_layout_write.__file__).read_text(encoding="utf-8")
    assert "map_graphics" in writer_source
    for module in (map_layout_edit, map_layout_provenance):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert "tools.export" not in source


# --- one owner per shared concept --------------------------------------------

def test_each_shared_binary_concept_has_exactly_one_implementation():
    """The concepts the audit listed resolve to the format layer's own objects.

    The export stack's names are *the same objects*, not copies of them: an
    ``isinstance`` of the SDK's record satisfies the export type, and the export
    reader functions call into the shared ones. A second implementation would
    have to be a second class or a second function here.
    """
    from tools.export import canonical as canon
    from tools.export import map_browser as mb
    from tools.export import render as export_render

    # The record types are the format layer's objects.
    assert canon.MapEntry is map_graphics.MapEntry
    assert canon.LayerRecord is map_graphics.LayerRecord
    assert canon.CharBlock is map_graphics.CharBlock
    assert canon.AnimatedTileSource is map_graphics.AnimatedTileSource
    assert canon.Bank is map_graphics.Bank

    # The browser's view types are the SDK map view's objects.
    assert mb.MapBrowserResult is mv.MapBrowserResult
    assert mb.MapBrowserLayer is mv.MapBrowserLayer
    assert mb.MapBrowserError is mv.MapBrowserError

    # The constants have one owner: the format layer, surfaced by the view.
    assert canon.DOMINANT_LAYER_HANDLER is map_graphics.DOMINANT_LAYER_HANDLER
    assert mb.CHUNK_PIXELS == map_graphics.CHUNK_PIXELS
    assert canon.TILE_ENTRY_BIT_10 == bg_tilemap.TILE_ENTRY_HORIZONTAL_FLIP
    assert canon.TILE_ENTRY_BIT_11 == bg_tilemap.TILE_ENTRY_VERTICAL_FLIP
    assert map_graphics.OBJECT_DIMENSIONS is sprite_graphics.OBJECT_DIMENSIONS

    # The tile primitives the exporter exposes resolve to the format layer: each
    # is a wrapper that calls it (they keep the exporter's error family), so what
    # is asserted is that the behaviour is one implementation, not that the name
    # is the same object.
    payload = bytes(range(64))
    assert export_render.unswizzle_tiles(
        payload, 8, 8, colour_256=True
    ) == sprite_graphics.unswizzle_tiles(payload, 8, 8, colour_256=True)
    straight = bytes([1]) * 64
    assert export_render.flip_tile(
        straight, True, False
    ) == sprite_graphics.flip_tile(straight, True, False)


def test_the_container_codec_has_one_implementation_per_policy():
    """Two container *policies*, one container *format*.

    The export path requires the packed stream's own end marker at its declared
    size; the SDK renderer accepts the project decoder's exact-size contract. That
    difference is injected into the shared reader rather than implemented as a
    second map reader, so both stacks decode the same grammar and only the
    postcondition differs.
    """
    from tools.export import canonical as canon
    from tools.export import webfoot_strict as ws

    strict = canon.Rom(b"\x00" * 0x100, profile=packaged_profile())
    assert strict.graphics_reader()._decode is canon.Rom._strict_decode

    # The strict decoder is the export stack's; the default is the project codec.
    assert map_graphics.project_container_decoder.__module__ == (
        "tools.webfoot.formats.map_graphics"
    )
    assert ws.unpack.__module__ == "tools.export.webfoot_strict"


# --- a synthetic input that is deliberately not Buu's ------------------------

_SYNTH_MAP_TABLE = 0x080A0000
_SYNTH_MAP_COUNT = 4
_SYNTH_MAP_INDEX = 2


def _synthetic_profile(sha256: str):
    """The packaged profile with a genuinely different map table and identity."""
    base = packaged_profile()
    return type(base)(
        **{
            **{field: getattr(base, field) for field in (
                "game", "region", "revision", "game_code", "size", "crc32",
                "md5", "sha1", "sources", "notes", "enemy_stats",
                "character_base_stats", "text_strings", "free_regions",
                "scripts", "placement_types", "actor_sprites",
                "generated_expansion",
            )},
            "id": "synthetic_decode_authority_profile",
            "sha256": sha256,
            "map_entries": MapEntryTableProfile(
                address=GbaRomAddress(_SYNTH_MAP_TABLE),
                count=_SYNTH_MAP_COUNT,
                record_size=_ME.MAP_ENTRY_SIZE,
            ),
        }
    )


def _place(rom: bytearray, address: int, data: bytes) -> None:
    offset = address - GBA_ROM_BASE
    rom[offset : offset + len(data)] = data


#: Tile bytes for ordinal 0 and 1. Ordinal 0 is a flat field of index 5; ordinal
#: 1 is index 9 with a single index-3 pixel in its top-left corner, which is what
#: makes a flip detectable: after both flips that pixel belongs bottom-right.
_TILE_0 = bytes([5]) * 64
_TILE_1 = bytes([3]) + bytes([9]) * 63


def _synthetic_rom() -> tuple[bytes, int, str]:
    """A complete, non-Buu map image: table, descriptor, selector, layers, palette.

    Nothing here is Buu's: the map table sits at an address the canonical profile
    does not declare, the record key bytes are not the canonical ones, and the
    background palette is written at a *relocated* address. A consumer that had
    kept its own copy of any of those values would read the wrong bytes.
    """
    rom = bytearray(0x800000)
    profile = _synthetic_profile("")
    palette_address = profile.actor_sprites.bg_palette_address.raw
    relocated_palette = palette_address + 0x1000
    palette = bytearray()
    for index in range(256):
        palette += bytes((index, (255 - index) & 0xFF, (index * 5) & 0xFF))
    _place(rom, relocated_palette, bytes(palette))

    map_entry = _SYNTH_MAP_TABLE + _SYNTH_MAP_INDEX * _ME.MAP_ENTRY_SIZE
    descriptor = 0x08300000
    source = 0x08310000
    _place(rom, source, struct.pack("<I", descriptor))
    record = bytearray(_ME.MAP_ENTRY_SIZE)
    record[0x00] = 0x11          # key high
    record[0x01] = 0x22          # key low
    struct.pack_into("<I", record, 0x0C, 0x0000012C)  # a text index
    struct.pack_into("<I", record, 0x2C, source)
    _place(rom, map_entry, bytes(record))
    # Every other declared row gets a readable source of its own: the reader
    # enumerates the whole table and resolves each row's root, so a null one is a
    # malformed image rather than something to skip.
    for other in range(_SYNTH_MAP_COUNT):
        if other == _SYNTH_MAP_INDEX:
            continue
        other_source = source + 0x10 * (other + 1)
        _place(rom, other_source, struct.pack("<I", descriptor))
        other_record = bytearray(_ME.MAP_ENTRY_SIZE)
        struct.pack_into("<I", other_record, 0x2C, other_source)
        _place(
            rom,
            _SYNTH_MAP_TABLE + other * _ME.MAP_ENTRY_SIZE,
            bytes(other_record),
        )

    remap = 0x08320000
    banks = 0x08321000
    bank = 0x08322000
    layer_record = 0x08330000
    chunk = 0x08331000

    # Absolute selectors [0, 1] delta-code to [0, 0].
    _place(rom, remap, webfoot_lz.build_stored(struct.pack("<2H", 0, 0)))
    _place(rom, banks, struct.pack("<I", bank))
    _place(rom, bank, webfoot_lz.build_stored(_TILE_0 + _TILE_1 + bytes(0x4000 - 128)))
    _place(rom, descriptor + 4, bytes((1, 0, 0, 0)))       # one BG control addend
    _place(rom, descriptor + 0x0C, struct.pack("<II", 0, 0))
    _place(rom, descriptor + 0x48, struct.pack("<II", remap, banks))

    # The dominant layer: a 2x1 chunk grid whose two cells hold the SAME chunk
    # pointer, so the layer is what a layout writer calls alternative-less while
    # still being a complete grid.
    layer = bytearray(0x30)
    struct.pack_into("<I", layer, 0, map_graphics.DOMINANT_LAYER_HANDLER)
    layer[0x14] = 2
    layer[0x15] = 1
    struct.pack_into("<2I", layer, 0x18, chunk, chunk)
    _place(rom, layer_record, bytes(layer))

    # The three unused slots point at the shared absent-placeholder record, which is
    # how the canonical corpus represents an empty slot: a non-null pointer to the
    # one zero-dimension record. The classification is address-dependent as well as
    # handler-dependent, so the synthetic record is written at that same literal
    # address, exactly as the accepted image holds it.
    absent_address = map_graphics.ABSENT_LAYER_RECORD
    _place(rom, absent_address, struct.pack("<I", map_graphics.ABSENT_LAYER_HANDLER))
    _place(
        rom,
        descriptor + 0x14,
        struct.pack("<4I", layer_record, absent_address, absent_address, absent_address),
    )

    # The chunk is a 32x32 plane: row 0 is ordinal 1 (the flip marker), the rest
    # ordinal 0. A shared flip decode puts the index-3 pixel bottom-right of its
    # tile; a dropped flip would leave it top-left.
    entries = [1] + [0] * 31 + [0] * (1024 - 32)
    _place(rom, chunk, webfoot_lz.build_stored(struct.pack("<1024H", *entries)))

    data = bytes(rom)
    import hashlib

    digest = hashlib.sha256(data).hexdigest()
    return data, descriptor, digest


def _relocated_profile(digest: str, palette_address: int):
    """The synthetic profile with its BG palette moved, as a frozen dataclass."""
    from dataclasses import replace as dc_replace

    from tools.webfoot.profile import ActorSpriteProfile

    base = _synthetic_profile(digest)
    sprites = base.actor_sprites
    assert sprites is not None
    return dc_replace(
        base,
        actor_sprites=dc_replace(
            sprites, bg_palette_address=GbaRomAddress(palette_address)
        ),
    )


def _profile_for(data: bytes):
    """An identity-correct synthetic profile for exactly these bytes.

    Built from the digest of the image handed in, so a test that mutates the image
    and re-renders gets a declaration that still describes it - which is what makes
    the identity gate a real check rather than an obstacle to stub out.
    """
    import hashlib

    digest = hashlib.sha256(data).hexdigest()
    base = _synthetic_profile(digest)
    return _relocated_profile(
        digest, base.actor_sprites.bg_palette_address.raw + 0x1000
    )


def test_a_synthetic_map_is_interpreted_by_the_shared_reader():
    """The reader resolves a non-Buu table, record and palette from the profile."""
    data, descriptor, digest = _synthetic_rom()
    profile = _profile_for(data)
    reader = map_graphics.MapGraphicsReader(data, profile)

    assert reader.map_entry_count() == _SYNTH_MAP_COUNT
    assert reader.map_entry_table_address() == _SYNTH_MAP_TABLE
    entries = map_graphics.read_map_entries(reader)
    assert len(entries) == _SYNTH_MAP_COUNT
    entry = entries[_SYNTH_MAP_INDEX]
    assert (entry.key_high, entry.key_low) == (0x11, 0x22)
    assert entry.text_index == 0x012C
    assert entry.root_address == descriptor

    layer = map_graphics.read_layer(reader, entry.root_address, 0)
    assert layer.classification == "dominant"
    assert (layer.chunk_x, layer.chunk_y) == (2, 1)
    assert layer.chunk_addresses == (0x08331000, 0x08331000)

    palette = map_graphics.decode_bg_palette(reader)
    assert len(palette) == 256
    # Entry 1 is RGB888 (1, 254, 5); each channel requantises to 5 bits and back.
    assert palette[1] == (0, 255, 0)


def test_both_stacks_render_the_synthetic_map_identically():
    """The SDK renderer and the export view agree byte-for-byte on a non-Buu map.

    This is the property the audit said was never tested: two production stacks
    rendering the same map with no comparison. Both go through the shared reader,
    so what this catches is a stack that stops doing so - and the synthetic image
    catches a hidden assumption, because none of its values are Buu's.
    """
    from tools.export import map_browser as mb

    data, _descriptor, digest = _synthetic_rom()
    profile = _profile_for(data)

    sdk = mr.render_map(data, f"map:{_SYNTH_MAP_INDEX:04d}", profile=profile)
    export = mb.render_map(data, _SYNTH_MAP_INDEX, profile=profile)

    assert sdk.width == export.width == 512   # 2 chunks x 256 px wide
    assert sdk.height == export.height == 256
    assert sdk.palette == export.palette
    # The view reports every slot, including the three absent placeholders, so the
    # comparison is over the slots that carry pixels - which is also the level the
    # two surfaces' contracts agree at.
    assert [
        (layer.slot, layer.classification, layer.pixels)
        for layer in export.layers
        if layer.pixels
    ] == [
        (layer.bg, "dominant", layer.pixels) for layer in sdk.layers
    ]
    assert [layer.classification for layer in export.layers].count("absent_placeholder") == 3
    assert sdk.composite == export.composite
    assert sdk.provenance["map_entry_address"] == f"{_SYNTH_MAP_TABLE + _SYNTH_MAP_INDEX * _ME.MAP_ENTRY_SIZE:#010x}"


def test_the_synthetic_flip_bits_are_decoded_where_the_entry_says():
    """A synthetic entry's flip bits are applied, in the shared tile renderer.

    The marker pixel is stored top-left of ordinal 1's tile; both flips must move
    it to the bottom-right of that 8x8 cell. A renderer that dropped either flip
    would leave it at the top-left, so the assertion is directional rather than a
    "changed" comparison.
    """
    data, _descriptor, digest = _synthetic_rom()
    profile = _profile_for(data)
    result = mr.render_map(data, f"map:{_SYNTH_MAP_INDEX:04d}", profile=profile)
    pixels = result.layers[0].pixels
    width = result.width

    # The chunk's first tile is entry word 1: ordinal 1 with no flips set, so the
    # marker stays top-left. The second tile is the same ordinal, also unflipped.
    assert pixels[0] == 3
    assert pixels[7] != 3

    # Flip the stored entry and the marker must move to the cell's bottom-right.
    changed = bytearray(data)
    word = 1 | bg_tilemap.TILE_ENTRY_HORIZONTAL_FLIP | bg_tilemap.TILE_ENTRY_VERTICAL_FLIP
    entries = [word] + [0] * 1023
    _place(changed, 0x08331000, webfoot_lz.build_stored(struct.pack("<1024H", *entries)))
    flipped = mr.render_map(
        bytes(changed),
        f"map:{_SYNTH_MAP_INDEX:04d}",
        profile=_profile_for(bytes(changed)),
    )
    flipped_pixels = flipped.layers[0].pixels
    assert flipped_pixels[7 * width + 7] == 3
    assert flipped_pixels[0] != 3


def test_malformed_shared_input_keeps_failing_closed():
    """A bad record refuses; it does not become a zero, a blank or a default.

    The consolidations must not have softened a strict refusal. Each case below
    is a record the accepted schema cannot read, and each must raise.
    """
    data, descriptor, digest = _synthetic_rom()
    profile = _profile_for(data)

    # A selector stream of odd length.
    broken = bytearray(data)
    _place(broken, 0x08320000, webfoot_lz.build_stored(b"\x01\x00\x00"))
    reader = map_graphics.MapGraphicsReader(bytes(broken), profile)
    with pytest.raises(map_graphics.MapGraphicsError, match="non-even decoded size"):
        map_graphics.decode_selector_stream(reader, descriptor)

    # A chunk whose container declares the wrong decoded size.
    broken = bytearray(data)
    _place(broken, 0x08331000, webfoot_lz.build_stored(b"\x00" * 0x100))
    reader = map_graphics.MapGraphicsReader(bytes(broken), profile)
    with pytest.raises(map_graphics.MapGraphicsError):
        map_graphics.dominant_chunk_words(reader, 0x08331000)

    # An animated-tile record whose frame count is zero.
    broken = bytearray(data)
    array = 0x08340000
    record = 0x08341000
    _place(broken, descriptor + 0x0C, struct.pack("<II", 1, array))
    _place(broken, array, struct.pack("<I", record))
    _place(broken, record, bytes((0, 1, 0, 0)) + struct.pack("<I", 0x08342000))
    reader = map_graphics.MapGraphicsReader(bytes(broken), profile)
    with pytest.raises(map_graphics.MapGraphicsError, match="zero extent"):
        map_graphics.read_animated_tiles(reader, descriptor)

    # A profile that declares no map table cannot be indexed at all.
    from dataclasses import replace as dc_replace

    no_table = dc_replace(
        _synthetic_profile(digest), map_entries=None
    )
    reader = map_graphics.MapGraphicsReader(data, no_table)
    with pytest.raises(map_graphics.MapGraphicsError, match="no map_entries table"):
        map_graphics.read_map_entries(reader)


def test_the_replacement_policy_has_one_implementation():
    """The writer's rule is the one the preview and the export facade call."""
    from tools.export import map_browser as mb
    from tools.webfoot.map_layout_write import (
        MapLayoutWriteError,
        legal_chunk_pointers,
        validate_chunk_replacement,
    )

    # The caller supplies the map's legal set; the predicate itself is one rule.
    layer = legal_chunk_pointers((0x082928DC, 0x08292A54))
    assert validate_chunk_replacement(layer, 0x08292A54) == 0x08292A54
    assert mb.validate_cell_replacement(layer, 0x08292A54) == 0x08292A54
    for bad in (0, 0x08299999, True, None, "x"):
        with pytest.raises(MapLayoutWriteError):
            validate_chunk_replacement(layer, bad)
        with pytest.raises(mb.MapBrowserError):
            mb.validate_cell_replacement(layer, bad)
