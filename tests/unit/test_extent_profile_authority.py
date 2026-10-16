"""CQA-15: the load-bearing extents come from the profile, not from literals.

The defect these cover: the canonical identity and the map/text/stat extents
were restated in three to eight independent places, several of them live, and
nothing asserted they agreed. A test that pins one copy to the local file is not
the same check - it cannot fail when a *second* copy drifts.

So these do not compare a constant to a constant. Each supplies a profile whose
declared values deliberately DIFFER from Buu's and asserts the production reader
follows the profile. Reintroducing a Buu literal into any migrated consumer
breaks the corresponding test, which is what makes the migration real rather
than cosmetic.

No commercial ROM is read: the export-side readers run on synthetic bytes sized
to the declared extent, and the map renderer on the synthetic fixture it already
has.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

import pytest

from tools.export import canonical as canon
from tools.export import map_browser as mb
from tools.export import profile_authority
from tools.webfoot import map_render as mr
from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.formats import map_entry as me
from tools.webfoot.formats import map_graphics
from tools.webfoot.profile import (
    MapEntryTableProfile,
    RecordTableProfile,
    RomProfile,
    RomProfileCatalog,
    TextTableProfile,
)

BUU = "buus_fury_usa_rev0_01c1707f"
IMAGE_SIZE = 8_388_608

#: Where the synthetic profile's tables live. Deliberately NOT Buu's addresses,
#: and inside the ROM window so the profile's own validation accepts them.
SYNTHETIC_MAP_TABLE = 0x08400000
SYNTHETIC_MAP_COUNT = 3
SYNTHETIC_TEXT_TABLE = 0x08410000
SYNTHETIC_TEXT_COUNT = 2
SYNTHETIC_TEXT_POOL = 0x08420000
SYNTHETIC_POOL_SIZE = 64
#: Palette addresses that are NOT the canonical profile's, so a read that finds
#: the fixture's palette proves the address came from the profile.
SYNTHETIC_OBJECT_PALETTE = 0x08430000
SYNTHETIC_BG_PALETTE = 0x08440000
#: The sprite-definition run and the appearance table, likewise not Buu's.
SYNTHETIC_SPRITE_RUN = 0x08450000
SYNTHETIC_SPRITE_DEFINITION = 0x08451000
SYNTHETIC_APPEARANCE_TABLE = 0x08460000
SYNTHETIC_APPEARANCE_SPRITE = 0x1234


def _synthetic_bytes() -> bytes:
    """An image the synthetic profile's TEXT and PALETTE extents describe.

    The map-table half of the parameterization proof uses the complete synthetic
    ROM in `test_map_render`, which is already wired for a readable map
    assembly. The palettes are filled with distinguishable constants so a read
    that lands at the profile's address is recognisable at the byte level.
    """
    image = bytearray(IMAGE_SIZE)

    def put(address: int, data: bytes) -> None:
        offset = address - 0x08000000
        image[offset : offset + len(data)] = data

    # Text pool: two NUL-terminated UTF-16LE strings, tiling the declared size.
    put(SYNTHETIC_TEXT_POOL, "AB\x00".encode("utf-16-le") + "CD\x00".encode("utf-16-le"))
    # Pointer table: two entries pointing at those two strings.
    put(
        SYNTHETIC_TEXT_TABLE,
        (SYNTHETIC_TEXT_POOL).to_bytes(4, "little")
        + (SYNTHETIC_TEXT_POOL + 6).to_bytes(4, "little"),
    )
    # Object palette: 256 BGR555 words, an easily recognisable ramp.
    object_palette = b"".join(
        (index & 0x7FFF).to_bytes(2, "little") for index in range(256)
    )
    put(SYNTHETIC_OBJECT_PALETTE, object_palette)
    # Background palette: 256 RGB888 triples, a distinguishable ramp.
    put(SYNTHETIC_BG_PALETTE, bytes(b for index in range(256) for b in (index, 0, 255 - index)))
    # Sprite-definition run: every pointer resolves to one empty definition.
    put(
        SYNTHETIC_SPRITE_RUN,
        SYNTHETIC_SPRITE_DEFINITION.to_bytes(4, "little") * canon.SPRITE_DEFINITION_COUNT,
    )
    put(
        SYNTHETIC_APPEARANCE_TABLE + canon.APPEARANCE_SPRITE_OFFSET,
        SYNTHETIC_APPEARANCE_SPRITE.to_bytes(4, "little"),
    )
    return bytes(image)


def _synthetic_profile(buu: RomProfile, *, text_count: int = SYNTHETIC_TEXT_COUNT) -> RomProfile:
    """Buu's profile with every load-bearing extent moved to a different value."""
    sprites = buu.actor_sprites
    assert sprites is not None
    return replace(
        buu,
        id="synthetic_extents_profile",
        sha256="cd" * 32,
        map_entries=MapEntryTableProfile(
            address=GbaRomAddress(SYNTHETIC_MAP_TABLE),
            count=SYNTHETIC_MAP_COUNT,
            record_size=me.MAP_ENTRY_SIZE,
        ),
        text_strings=TextTableProfile(
            pointer_table_address=GbaRomAddress(SYNTHETIC_TEXT_TABLE),
            count=text_count,
            pool_address=GbaRomAddress(SYNTHETIC_TEXT_POOL),
            pool_size=SYNTHETIC_POOL_SIZE,
            encoding="utf16le_nul_terminated",
            alignment=2,
            relocatable=False,
            evidence="CQA-03-15 synthetic parameterization fixture",
        ),
        actor_sprites=replace(
            sprites,
            character_table_address=GbaRomAddress(SYNTHETIC_SPRITE_RUN),
            object_palette_address=GbaRomAddress(SYNTHETIC_OBJECT_PALETTE),
            bg_palette_address=GbaRomAddress(SYNTHETIC_BG_PALETTE),
        ),
        appearances=RecordTableProfile(
            address=GbaRomAddress(SYNTHETIC_APPEARANCE_TABLE),
            count=canon.APPEARANCE_COUNT,
            record_size=canon.APPEARANCE_STRIDE,
        ),
    )


@pytest.fixture(scope="module")
def buu() -> RomProfile:
    catalog = RomProfileCatalog.load("config/roms.yaml")
    return next(p for p in catalog.profiles if p.id == BUU)


@pytest.fixture(scope="module")
def image() -> bytes:
    return _synthetic_bytes()


# --- the profile authority itself ---------------------------------------------


def test_the_export_identity_is_the_profiles_declaration(buu):
    """One owner: the hash is read from the catalog, not restated beside it."""
    expected = profile_authority.canonical_export_identity()
    assert expected.sha256 == buu.sha256
    assert expected.profile_id == buu.id
    assert expected.image_size == buu.size
    # And there is no second literal to drift.
    from tools.export import buu_resource_export

    assert buu_resource_export.CANONICAL_ROM_SHA256 == buu.sha256
    assert buu_resource_export.canonical_map_entry_count() == buu.map_entries.count


# --- map table address and count ----------------------------------------------


def test_the_map_entry_count_bound_is_the_profiles(buu, image):
    """`Rom.map_entry_count` follows the supplied profile, not Buu's table."""
    synthetic = _synthetic_profile(buu)
    rom = canon.Rom(image, profile=synthetic)
    assert rom.map_entry_count() == SYNTHETIC_MAP_COUNT
    assert rom.map_entry_table_address() == SYNTHETIC_MAP_TABLE
    assert rom.map_entry_count() != buu.map_entries.count


def _map_table_bytes(count: int) -> bytes:
    """An image where records 0..count-1 of ONE table all have a readable root.

    Every record's `+0x2C` points at a word that points at a shared root
    definition, which is all `read_map_entries` needs to resolve an entry. The
    assembly behind that root is not needed to prove the bound, the address and
    the stride, and building one would only obscure what is being tested.
    """
    image = bytearray(IMAGE_SIZE)

    def put(address: int, data: bytes) -> None:
        offset = address - 0x08000000
        image[offset : offset + len(data)] = data

    root = 0x08500000
    for index in range(count):
        record = SYNTHETIC_MAP_TABLE + index * me.MAP_ENTRY_SIZE
        # The record's own selector source, then the root definition it holds.
        put(record + 0x2C, (0x08510000 + index * 0x100).to_bytes(4, "little"))
        put(0x08510000 + index * 0x100, (root).to_bytes(4, "little"))
    return bytes(image)


def test_read_map_entries_walks_the_profiles_extent(buu):
    """The enumerator reads exactly `count` records at `address`, stride `size`."""
    synthetic = replace(
        buu,
        id="synthetic_map_extent_profile",
        map_entries=MapEntryTableProfile(
            address=GbaRomAddress(SYNTHETIC_MAP_TABLE),
            count=SYNTHETIC_MAP_COUNT,
            record_size=me.MAP_ENTRY_SIZE,
        ),
    )
    entries = canon.read_map_entries(
        canon.Rom(_map_table_bytes(SYNTHETIC_MAP_COUNT), profile=synthetic)
    )
    assert len(entries) == SYNTHETIC_MAP_COUNT
    assert [entry.index for entry in entries] == list(range(SYNTHETIC_MAP_COUNT))
    assert entries[1].address == SYNTHETIC_MAP_TABLE + me.MAP_ENTRY_SIZE
    # A larger declared count reads further into this image - the loop bound is
    # the declaration, so a Buu literal would enumerate 452 records instead.
    larger = canon.read_map_entries(
        canon.Rom(
            _map_table_bytes(SYNTHETIC_MAP_COUNT + 2),
            profile=replace(
                synthetic,
                map_entries=MapEntryTableProfile(
                    address=GbaRomAddress(SYNTHETIC_MAP_TABLE),
                    count=SYNTHETIC_MAP_COUNT + 2,
                    record_size=me.MAP_ENTRY_SIZE,
                ),
            ),
        )
    )
    assert len(larger) == SYNTHETIC_MAP_COUNT + 2


def test_the_map_browser_index_bound_is_the_profiles(buu, image):
    """A map index past the declared count is refused by the profile's bound.

    The bound is the SDK map view's, which is where the browser's index check now
    lives (CQA-04); the export facade calls into it rather than keeping a copy.
    """
    synthetic = _synthetic_profile(buu)
    assert SYNTHETIC_MAP_COUNT < buu.map_entries.count
    reader = map_graphics.MapGraphicsReader(image, synthetic)
    from tools.webfoot.map_view import _check_map_index

    _check_map_index(reader, SYNTHETIC_MAP_COUNT - 1)
    with pytest.raises(mb.MapBrowserError, match=f"0\\.\\.{SYNTHETIC_MAP_COUNT - 1}"):
        _check_map_index(reader, SYNTHETIC_MAP_COUNT)


# --- the live text index bound ------------------------------------------------


def test_the_text_index_bound_is_the_profiles(buu, image):
    """`Rom.text` bounds by the profile's count, not by a module constant.

    This is the copy the audit called out as a LIVE index bound. With the
    synthetic profile declaring 2 entries, index 2 must resolve to None even
    though Buu's table has 1,534 slots at a different address.
    """
    synthetic = _synthetic_profile(buu)
    rom = canon.Rom(image, profile=synthetic)
    assert rom.text_table().count == SYNTHETIC_TEXT_COUNT
    assert rom.text(0) == "AB"
    assert rom.text(1) == "CD"
    assert rom.text(SYNTHETIC_TEXT_COUNT) is None
    assert rom.text(-1) is None

    # The default (canonical) profile does not find these strings at all: its
    # table address is Buu's, which this image leaves zeroed.
    default_rom = canon.Rom(image)
    assert default_rom.text_table().count == buu.text_strings.count
    assert default_rom.text(0) is None


def test_a_profile_declaring_a_different_text_count_bounds_differently(buu, image):
    """Moving only the declared count moves only the bound."""
    three = _synthetic_profile(buu, text_count=3)
    rom = canon.Rom(image, profile=three)
    # Index 2 is inside the declared count but the table has no third pointer,
    # so it resolves to nothing rather than raising.
    assert rom.text(2) is None
    assert rom.text_table().count == 3


# --- the map renderer ---------------------------------------------------------


def test_the_map_renderer_address_is_the_profiles():
    """`resolve_descriptor` uses the profile's table address and stride.

    The fixture ROM from `test_map_render` wires its table at a non-Buu address;
    the canonical profile's address holds nothing there, so resolving against it
    cannot produce the fixture's descriptor.
    """
    from tests.unit.test_map_render import (
        _SYNTHETIC_MAP_INDEX,
        _SYNTHETIC_MAP_TABLE_ADDRESS,
        _synthetic_rom,
        synthetic_profile,
    )

    rom_bytes, descriptor = _synthetic_rom()
    synthetic = synthetic_profile()
    entry, _pointer, resolved = mr.resolve_descriptor(
        rom_bytes, _SYNTHETIC_MAP_INDEX, profile=synthetic
    )
    assert entry == (
        _SYNTHETIC_MAP_TABLE_ADDRESS + _SYNTHETIC_MAP_INDEX * me.MAP_ENTRY_SIZE
    )
    assert resolved == descriptor


def test_the_map_renderer_refuses_a_profile_with_no_map_table(buu, image):
    """A profile declaring no map table is refused by name, not defaulted."""
    without = replace(buu, id="no_map_table_profile", map_entries=None)
    with pytest.raises(mr.MapRenderError, match="declares no map_entries"):
        mr.resolve_entry_table(without)


# --- GBA base -----------------------------------------------------------------


def test_the_gba_base_has_one_owner():
    """Address-window semantics live in `binary`; the copies are aliases of it."""
    from tools.webfoot import binary
    from tools.webfoot.formats import ascii_text_tables as att
    from tools.webfoot.formats import map_placements, map_slots, text_tables

    assert att.GBA_ROM_BASE == binary.GBA_ROM_BASE
    assert text_tables.GBA_ROM_BASE == binary.GBA_ROM_BASE
    assert map_placements.ROM_BASE == binary.GBA_ROM_BASE
    assert map_slots.ROM_BASE == binary.GBA_ROM_BASE

    # The aliases are the same object's value, and the export stack agrees.
    from tools.export import webfoot_strict as ws

    assert ws.GBA_ROM_BASE == binary.GBA_ROM_BASE


def test_the_gba_base_round_trips_through_the_sanctioned_helpers():
    """`FileOffset`/`GbaRomAddress` are the conversion, not ad hoc arithmetic."""
    from tools.webfoot.binary import GBA_ROM_BASE, FileOffset, GbaRomAddress

    assert FileOffset(0).to_gba_address(IMAGE_SIZE) == GbaRomAddress(GBA_ROM_BASE)
    assert GbaRomAddress(GBA_ROM_BASE + 0x1234).to_file_offset(IMAGE_SIZE) == 0x1234


# --- stat extents -------------------------------------------------------------


def test_the_stat_extents_come_from_the_profile(buu):
    """The stat readers take address, count and stride from the declaration."""
    from tools.webfoot.formats import stat_tables as st

    enemy = buu.enemy_stats
    characters = buu.character_base_stats
    assert isinstance(enemy, RecordTableProfile)
    assert isinstance(characters, RecordTableProfile)
    # The format layer's strides describe the record shapes and must agree with
    # what the profile declares, or one of the two is wrong.
    assert enemy.record_size == st.ENEMY_RECORD_SIZE
    assert characters.record_size == st.BASE_STAT_RECORD_SIZE
    # The address is the profile's, and it is a GBA address, not a file offset.
    assert enemy.address.raw >= 0x08000000
    assert enemy.address.raw != st.ENEMY_TABLE_START


def test_the_character_identity_bound_is_the_callers(buu):
    """A profile declaring a shorter roster refuses an index it cannot have."""
    from tools.webfoot.formats import stat_tables as st

    count = buu.character_base_stats.count
    assert st.character_identity(count - 1, count).key == count - 1
    with pytest.raises(ValueError):
        st.character_identity(count, count)


# --- the palette addresses ----------------------------------------------------


def test_the_object_palette_address_is_the_profiles(buu, image):
    """`render.object_palette_rgb` reads the profile's declared address.

    The fixture palette is a ramp that exists only at the synthetic address, so
    a read pinned to Buu's address cannot produce it.
    """
    from tools.export import render as render_sdk

    synthetic = _synthetic_profile(buu)
    rom = canon.Rom(image, profile=synthetic)
    assert rom.object_palette_address() == SYNTHETIC_OBJECT_PALETTE
    assert rom.object_palette_address() != buu.actor_sprites.object_palette_address.raw

    palette = render_sdk.object_palette_rgb(rom)
    assert len(palette) == canon.OBJECT_PALETTE_ENTRIES
    # Entry 1 is BGR555 word 1, which expands to (8, 0, 0) at red 5 bits.
    assert palette[1] == (8, 0, 0)


def test_the_background_palette_address_is_the_profiles(buu, image):
    """Both palette readers use the profile's declared address."""
    from tools.export import render as render_sdk

    synthetic = _synthetic_profile(buu)
    rom = canon.Rom(image, profile=synthetic)
    assert rom.bg_palette_address() == SYNTHETIC_BG_PALETTE
    assert rom.bg_palette_address() != buu.actor_sprites.bg_palette_address.raw

    palette = render_sdk.bg_palette_rgb(rom)
    assert len(palette) == 256
    # RGB888 triple for index 1 is (1, 0, 254); each channel is requantised to
    # 5 bits and expanded back, so 1 -> 0 and 254 -> 255.
    assert palette[1] == (0, 0, 255)


def test_the_map_renderer_palette_address_is_the_profiles(image):
    """`map_render.decode_bg_palette` reads the profile's declared address.

    Driven through `map_render`, not the export stack, so a Buu literal left in
    the renderer fails here.
    """
    synthetic_buu = mr.canonical_profile()
    synthetic = replace(
        synthetic_buu,
        actor_sprites=replace(
            synthetic_buu.actor_sprites,
            bg_palette_address=GbaRomAddress(SYNTHETIC_BG_PALETTE),
        ),
    )
    palette = mr.decode_bg_palette(image, profile=synthetic)
    assert len(palette) == mr.BG_PALETTE_ENTRIES
    assert palette[1] == (0, 0, 255)
    # The canonical profile's address holds nothing in this image, so the two
    # profiles cannot produce the same palette.
    assert mr.decode_bg_palette(image, profile=synthetic_buu) != palette


def test_the_map_renderer_refuses_a_profile_with_no_palette(image, buu):
    """A profile declaring no palette is refused by name, not defaulted."""
    without = replace(buu, id="no_palette_profile", actor_sprites=None)
    with pytest.raises(mr.MapRenderError, match="declares no actor_sprites palette"):
        mr.decode_bg_palette(image, profile=without)


def test_the_sprite_definition_run_address_is_the_profiles(buu, image):
    synthetic = _synthetic_profile(buu)
    rom = canon.Rom(image, profile=synthetic)
    assert rom.sprite_definition_run_address() == SYNTHETIC_SPRITE_RUN
    assert (
        rom.sprite_definition_run_address()
        != buu.actor_sprites.character_table_address.raw
    )

    definitions = canon.read_sprite_definitions(rom)
    assert len(definitions) == canon.SPRITE_DEFINITION_COUNT
    assert {definition.address for definition in definitions} == {
        SYNTHETIC_SPRITE_DEFINITION
    }
    assert [definition.sprite_id for definition in definitions] == [
        canon.SPRITE_ID_FLOOR + index for index in range(canon.SPRITE_DEFINITION_COUNT)
    ]

    with pytest.raises(canon.CanonicalError):
        canon.read_sprite_definitions(canon.Rom(image))


def test_the_appearance_table_address_is_the_profiles(buu, image):
    synthetic = _synthetic_profile(buu)
    rom = canon.Rom(image, profile=synthetic)
    assert rom.appearance_table_address() == SYNTHETIC_APPEARANCE_TABLE
    assert rom.appearance_table_address() != buu.appearances.address.raw

    records = canon.read_appearances(rom)
    assert len(records) == canon.APPEARANCE_COUNT
    assert records[0].address == SYNTHETIC_APPEARANCE_TABLE
    assert records[-1].address == (
        SYNTHETIC_APPEARANCE_TABLE
        + (canon.APPEARANCE_COUNT - 1) * canon.APPEARANCE_STRIDE
    )
    assert records[0].sprite_id == SYNTHETIC_APPEARANCE_SPRITE
    canonical_address_holds = canon.Rom(image).u32(
        buu.appearances.address.raw + canon.APPEARANCE_SPRITE_OFFSET
    )
    assert canonical_address_holds != SYNTHETIC_APPEARANCE_SPRITE


def test_the_appearance_reader_refuses_a_profile_with_no_appearances(buu, image):
    without = replace(buu, id="no_appearances_profile", appearances=None)
    with pytest.raises(canon.CanonicalError, match="declares no appearances.address"):
        canon.read_appearances(canon.Rom(image, profile=without))


def test_the_sprite_reader_refuses_a_profile_with_no_actor_sprites(buu, image):
    without = replace(buu, id="no_actor_sprites_profile", actor_sprites=None)
    with pytest.raises(
        canon.CanonicalError, match="declares no actor_sprites.character_table_address"
    ):
        canon.read_sprite_definitions(canon.Rom(image, profile=without))


def test_the_map_layout_writer_gate_is_the_profile_identity():
    """The writer owns no hash of its own; its identity comes from the profile."""
    from tools.webfoot import map_layout_write

    assert not hasattr(map_layout_write, "SUPPORTED_ROM_SHA256"), (
        "the writer must not own a second copy of the canonical hash"
    )


def test_the_map_layout_writer_bound_is_the_profiles(buu):
    """`MapLayoutWriter` bounds a map index by the SUPPLIED profile's count.

    Behavioural, not textual: the writer is given a profile declaring a smaller
    map table than the canonical one, and its own gate must refuse an index that
    profile does not have. A reintroduced literal would either admit that index
    (if the literal is larger) or refuse a valid one, so this fails on both.
    """
    from tests.unit.test_map_render import (
        _SYNTHETIC_MAP_TABLE_ADDRESS,
        _synthetic_rom,
    )
    from tools.webfoot.map_layout_write import MapLayoutWriteError, MapLayoutWriter

    rom_bytes, _descriptor = _synthetic_rom()
    table = MapEntryTableProfile(
        address=GbaRomAddress(_SYNTHETIC_MAP_TABLE_ADDRESS),
        count=SYNTHETIC_MAP_COUNT,
        record_size=me.MAP_ENTRY_SIZE,
    )
    # The image's own digest, so the writer's identity gate is satisfied by the
    # supplied declaration rather than by stubbing the packaged profile.
    synthetic = replace(
        buu,
        id="synthetic_writer_profile",
        sha256=hashlib.sha256(rom_bytes).hexdigest(),
        map_entries=table,
    )
    writer = MapLayoutWriter(rom_bytes, profile=synthetic)
    assert writer._reader.map_entry_count() == SYNTHETIC_MAP_COUNT
    assert writer._reader.map_entry_table_address() == _SYNTHETIC_MAP_TABLE_ADDRESS

    # One past the declared count is refused by the writer's own bound. The
    # canonical profile declares far more maps, so a literal bound of 452 or the
    # canonical count would NOT refuse this index.
    assert SYNTHETIC_MAP_COUNT != 452
    with pytest.raises(MapLayoutWriteError, match="declared range"):
        writer._layer(SYNTHETIC_MAP_COUNT, 0)
    with pytest.raises(MapLayoutWriteError, match="declared range"):
        writer._layer(452, 0)
