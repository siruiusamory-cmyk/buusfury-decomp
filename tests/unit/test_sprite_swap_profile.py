"""PINMAP-04: the sprite swap tool's targets resolve from a profile, not from a literal.

Every drive here runs over synthetic bytes. The planner reads four addresses - the
character registry, the object palette, the portrait pointer array and the animation
pointer offset - and each of them is the profile's declaration, so the proof that a move
of the profile moves the target needs an image whose own layout is known and a layout
whose addresses sit in it. No image this project ships is read.

**How the falsifier works.** Two synthetic layouts differ in exactly one address. If a
target address were still spelled in the planner, the address it read would not follow
the difference and these nodes would compare equal, or the walk would name another
corpus's offset. The pair of corpora in one image is what makes the observable a value
rather than a refusal.

**The one measurement this module cannot make.** The pinned difference between the
tree census and the published pair in ``INVENTORY.md`` section 4 is a constant of the
census module, and PINMAP-04 moved the tree rather than the publication. That is
recorded where the census pins live, not here.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from tools.webfoot import capability
from tools.webfoot import sprite_swap as ss
from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.formats import webfoot_lz as wl
from tools.webfoot.profile import (ActorSpriteProfile, ProfileConfigError,
                                   RomProfileCatalog)

ROOT = Path(__file__).resolve().parents[2]

PROFILE_ID = "buus_fury_usa_rev0_01c1707f"
PORTRAIT_KEY = "portrait_table_address"

#: The two catalogue paths, which must stay byte-identical (PINMAP-01's contract).
PLANNER_NAME = "tools/webfoot/sprite_swap.py"
PACKAGED_NAME = "tools/webfoot/data/roms.yaml"
DEVELOPMENT_NAME = "config/roms.yaml"
PROFILE_NAME = "tools/webfoot/profile.py"

IMAGE_SIZE = 0x8000
BASE = 0x08000000

#: Corpus A: the registry, the object palette and the portrait pointer array a
#: synthetic layout points at. The regions inside one corpus do not overlap, so the
#: frame record cannot land on the structure's own word.
TABLE_A = 0x1000
STRUCTURE_A = 0x1100
ANIMATION_A = 0x1300
FRAME_A = 0x1400
CONTAINER_A = 0x1C00

#: Corpus B: a second complete sprite declaration of the same shape, so a layout that
#: points here reaches different bytes with no edit to this module.
TABLE_B = 0x3000
STRUCTURE_B = 0x3100
ANIMATION_B = 0x3300
FRAME_B = 0x3400
CONTAINER_B = 0x3C00

PALETTE_A = 0x200
PALETTE_B = 0xA00
BG_PALETTE = 0x800
PORTS = 0x900

#: The animation pointer array's own offset inside a synthetic structure, relative to
#: the field region that carries it. Four-byte aligned, and the layout handed to the
#: walk declares this same number, so the read is the layout's offset either way.
#: A named limit: the shipped structures declare the array at +0, in the same word the
#: composition size occupies, and a synthetic image cannot do both - a pointer stored
#: there makes the composition field read the pointer's own bits. The reads under test
#: are the same regardless: the offset comes from the layout, not from this image.
ANIMATION_OFFSET = 0x54

#: The synthetic addresses the shipped profile does not carry, so "the layout was read"
#: and "a fixed value was read" are different numbers in every assertion.
SHIPPED_TABLE = 0x6B6BDC
SHIPPED_PALETTE = 0x5652C
SHIPPED_PORTS = 0x6F393C

SIDE = 32
FRAMES_PER_FACING = 3
SHEET = "sheet.png"
#: Frames are indexed direction-major: cell ``direction * frames_per_facing + frame``
#: reaches ``DIRECTION_COUNT * FRAMES_PER_FACING`` cells, and the crop of every one of
#: them has to stay inside the sheet.
SHEET_WIDTH = SIDE * sg.DIRECTION_COUNT * FRAMES_PER_FACING
SHEET_HEIGHT = SIDE

#: The two colours the sheet carries, and the index each palette gives them: the SAME
#: colour at a DIFFERENT index, which is what makes the raster a read-out of which
#: palette the walk used. Black resolves to BLACK_A in the first palette and BLACK_B in
#: the second, and the transparent index is a colour of its own so neither is ambiguous.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLACK_A, WHITE_A = 5, 7
BLACK_B, WHITE_B = 6, 66

_CELL = ss.DONOR_GEOMETRY.cell_side
_CROP = ss.DONOR_GEOMETRY.crop_x
_FRAME_W = ss.DONOR_GEOMETRY.frame_width
_FRAME_H = ss.DONOR_GEOMETRY.frame_height


# --- the synthetic world -------------------------------------------------------


def _address(file_offset: int) -> GbaRomAddress:
    """A declared address from a file offset, so the two spellings stay distinct."""
    return GbaRomAddress(BASE + file_offset)


def _shipped_profile():
    """The profile this repository ships, read from the catalogue it packages."""
    catalog = RomProfileCatalog.load(ROOT / DEVELOPMENT_NAME)
    return next(item for item in catalog.profiles if item.id == PROFILE_ID)


#: The shipped layout's own animation pointer offset, so the synthetic image and the
#: layout handed to the walk cannot disagree about where that array begins.
_SHIPPED_OFFSET = _shipped_profile().actor_sprites.animation_pointer_offset


def _layout(table: int, palette: int = PALETTE_A, portrait: int | None = PORTS):
    """One synthetic actor-sprite layout naming the addresses a drive reads."""
    return replace(
        _shipped_profile().actor_sprites,
        character_table_address=_address(table),
        character_count=1,
        animation_pointer_offset=ANIMATION_OFFSET,
        object_palette_address=_address(palette),
        bg_palette_address=_address(BG_PALETTE),
        portrait_table_address=None if portrait is None else _address(portrait),
    )


def _palette_words(black: int, white: int) -> dict[int, int]:
    """The 256 halfwords one palette holds, in the spelling the hardware uses.

    Index 0 is the transparent colour and is left off black on purpose: a black pixel at
    index 0 and at the black index would make the colour ambiguous rather than a
    read-out, and the reader refuses an ambiguous colour instead of guessing it.
    """
    words = {index: index for index in range(sg.PALETTE_ENTRIES)}
    words[0] = sg.pack_gba_colour(8, 8, 8)
    words[2] = sg.pack_gba_colour(24, 0, 0)
    words[black] = sg.pack_gba_colour(*BLACK)
    words[white] = sg.pack_gba_colour(*WHITE)
    return words


def _png(width: int, height: int, row) -> bytes:
    """An 8-bit RGB PNG, written here so no drive needs a fixture on disk."""
    def chunk(kind: bytes, body: bytes) -> bytes:
        return (struct.pack(">I", len(body)) + kind + body
                + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF))

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + row(y) for y in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _sheet_row(y: int) -> bytes:
    """One scanline of a sheet whose every 32-wide cell carries the 16-wide window.

    The window the planner crops is ``cell * side + crop_x`` wide by ``frame_height``
    tall, and a crop that ran off the sheet would be refused rather than padded.
    """
    row = bytearray()
    for x in range(SHEET_WIDTH):
        inside = _CROP <= x % SIDE < _CROP + _FRAME_W
        row += bytes(WHITE if inside else BLACK)
    return bytes(row)


def _packed() -> bytes:
    """The sheet's own window in the indices both palettes give it, swizzled and packed.

    The window is stated from the two colours the sheet's window carries at the indices
    both palettes use, so the packed bytes and the sheet's own crop are the same art.
    """
    window = bytes(WHITE_A if x >= _CROP else BLACK_A
                   for y in range(_FRAME_H) for x in range(_FRAME_W))
    tiles = sg.swizzle_tiles(window, _FRAME_W, _FRAME_H, colour_256=True)
    return wl.pack(tiles, kind=sg.GRAPHICS_CONTAINER_KIND)


def _spec() -> ss.SpriteSwap:
    """One populated slot, three frames per facing, the donor's own geometry."""
    return ss.SpriteSwap(
        sprite_id=ss.SPRITE_ID_BASE,
        slots=(ss.SheetSlot(slot=0, sheet=SHEET,
                            frames_per_facing=FRAMES_PER_FACING),),
    )


def _sheet_raster(assets: Path, palette: dict) -> bytes:
    """The raster the sheet's first cell is, read through the planner's own reader."""
    return ss.raster_from_png(assets / SHEET, palette, _FRAME_W, _FRAME_H, cell=0,
                              geometry=ss.DONOR_GEOMETRY)


def _frame_record(container: int) -> bytes:
    """One frame: a header bounding one piece, then that piece's 12 bytes.

    The header is the piece count, the bounding rectangle (signed minimum, then
    unsigned extent), then the piece: its own rectangle, its attributes and the
    container it names.
    """
    rect = struct.pack("<bbBB", *ss.DONOR_GEOMETRY.frame_anchor, _FRAME_W, _FRAME_H)
    piece = rect + struct.pack("<II", 0x00002000, BASE + container)
    return struct.pack("<I", 1) + rect + piece


def _corpus(out: bytearray, table: int, structure: int, animation: int, frame: int,
            container: int) -> None:
    """One character-table slot, its structure, its animation and its frame.

    The structure's first word carries the composition size the donor's geometry is
    proven at in its own half. The animation pointer array sits at the offset the layout
    declares past the structure, and every direction slot of every frame names the same
    frame, whose single piece names ``container``.
    """
    struct.pack_into("<I", out, table, BASE + structure)
    struct.pack_into("<I", out, structure, ss.DONOR_GEOMETRY.composition_size << 16)
    struct.pack_into("<I", out, structure + ANIMATION_OFFSET, BASE + animation)
    struct.pack_into("<I", out, animation, FRAMES_PER_FACING)
    record = _frame_record(container)
    for slot in range(sg.DIRECTION_COUNT * FRAMES_PER_FACING):
        struct.pack_into("<I", out, animation + 4 + 4 * slot, BASE + frame)
    for index in range(FRAMES_PER_FACING):
        start = frame + index * len(record)
        out[start:start + len(record)] = record


def _image(assets: Path) -> bytes:
    """Two declarations, two palettes and one shared portrait pointer array."""
    out = bytearray(IMAGE_SIZE)
    for palette, black, white in ((PALETTE_A, BLACK_A, WHITE_A),
                                  (PALETTE_B, BLACK_B, WHITE_B)):
        for index, word in _palette_words(black, white).items():
            struct.pack_into("<H", out, palette + 2 * index, word)
    _corpus(out, TABLE_A, STRUCTURE_A, ANIMATION_A, FRAME_A, CONTAINER_A)
    _corpus(out, TABLE_B, STRUCTURE_B, ANIMATION_B, FRAME_B, CONTAINER_B)
    payload = _packed()
    out[CONTAINER_A:CONTAINER_A + len(payload)] = payload
    out[CONTAINER_B:CONTAINER_B + len(payload)] = payload
    struct.pack_into("<I", out, PORTS, BASE + PORTS + 4)
    return bytes(out)


@pytest.fixture()
def world(tmp_path: Path):
    """The sheet, the image built against it, and two layouts one address apart.

    The pair differs in the object palette address only, which is the difference the
    falsifier drive needs; a drive that wants the registry moved builds its own pair.
    """
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / SHEET).write_bytes(_png(SHEET_WIDTH, SHEET_HEIGHT, _sheet_row))
    image = _image(assets)
    return tmp_path, assets, image, _layout(TABLE_A), _layout(TABLE_A, PALETTE_B)


def _only_cell(image: bytes, assets: Path, layout) -> ss.Cell:
    cells = ss.donor_cells(image, assets, _spec(), layout=layout)
    assert len(cells) == sg.DIRECTION_COUNT * FRAMES_PER_FACING
    return cells[0]


# --- D1: no numeric target literal remains -------------------------------------


def test_the_planner_spells_none_of_the_three_addresses_it_used_to_carry() -> None:
    """Read from the source itself, in the spellings the value could come back in.

    The census row guards the same surface by count; this node states the claim about
    this file, so a reintroduced literal fails here even while the count is right.
    """
    source = (ROOT / PLANNER_NAME).read_text(encoding="utf-8")
    for spelling in (f"{SHIPPED_TABLE:08X}", f"{SHIPPED_TABLE:08x}",
                     f"{SHIPPED_PALETTE:08X}", f"{SHIPPED_PALETTE:08x}",
                     f"{SHIPPED_PORTS:08X}", f"{SHIPPED_PORTS:08x}"):
        assert spelling not in source, spelling


def test_the_three_names_stay_importable_and_carry_the_profiles_values() -> None:
    """The three names a module outside this surface re-exports still resolve.

    Read through the module attribute path, so a binding that stopped existing fails
    here rather than at the import of a module this change does not own.
    """
    layout = capability.packaged_contract(
        PROFILE_ID, capability.Capability.ACTOR_SPRITES
    ).actor_sprites
    assert ss.REGISTRY_TABLE_ADDRESS == layout.character_table_address.raw == BASE + SHIPPED_TABLE
    assert ss.OBJECT_PALETTE_ADDRESS == layout.object_palette_address.raw == BASE + SHIPPED_PALETTE
    assert ss.PORTRAIT_ARRAY_ADDRESS == layout.portrait_table_address.raw == BASE + SHIPPED_PORTS


# --- D2: the addresses resolve from the profile --------------------------------


def test_each_layout_address_reaches_the_offset_the_layout_declares() -> None:
    """The resolution follows the layout, and the layout's numbers are its own.

    The three synthetic addresses differ from the shipped ones, so an assertion that
    the resolved offset equals the declared offset cannot be satisfied by a fixed value.
    """
    layout = _layout(TABLE_A)
    assert ss.file_offset(layout.character_table_address.raw, IMAGE_SIZE) == TABLE_A
    assert ss.file_offset(layout.object_palette_address.raw, IMAGE_SIZE) == PALETTE_A
    assert ss.file_offset(layout.portrait_table_address.raw, IMAGE_SIZE) == PORTS
    assert TABLE_A != SHIPPED_TABLE
    assert PALETTE_A != SHIPPED_PALETTE
    assert PORTS != SHIPPED_PORTS


def test_a_layout_naming_an_address_off_the_image_is_refused_with_that_address() -> None:
    """The refusal carries the layout's own number, which a fixed address could not."""
    with pytest.raises(ss.SpriteSwapError, match="is outside a 32768-byte image"):
        _only_cell(bytes(IMAGE_SIZE), Path("."), _layout(IMAGE_SIZE))


# --- D3: the portrait array has a declared key ---------------------------------


def test_the_shipped_profile_declares_the_portrait_array_address() -> None:
    layout = _shipped_profile().actor_sprites
    assert layout.portrait_table_address is not None
    assert layout.portrait_table_address.raw == BASE + SHIPPED_PORTS


def test_the_two_catalogue_copies_declare_the_key_identically() -> None:
    """A key added to one copy and not the other is the drift this catches."""
    packaged = (ROOT / PACKAGED_NAME).read_bytes()
    development = (ROOT / DEVELOPMENT_NAME).read_bytes()
    assert packaged == development
    assert b"portrait_table_address: 0x086f393c" in packaged


def test_a_six_key_construction_still_loads_with_the_key_absent() -> None:
    """The key is optional on the type, so a caller that omits it still builds one.

    Driven through the real dataclass and through a ``replace`` over the shipped
    layout, because those are the two shapes the in-tree callers use; the catalogue
    loader keeps its exact key set (see the test above).
    """
    six = {name for name in ActorSpriteProfile.__dataclass_fields__
           if name != PORTRAIT_KEY}
    assert len(six) == 6
    assert ActorSpriteProfile.__dataclass_fields__[PORTRAIT_KEY].default is None

    built = ActorSpriteProfile(
        character_table_address=_address(TABLE_A), character_count=1,
        animation_pointer_offset=0, object_palette_address=_address(PALETTE_A),
        bg_palette_address=_address(BG_PALETTE), evidence="synthetic six-key build")
    assert built.portrait_table_address is None
    assert replace(built, character_count=2).portrait_table_address is None


# --- D4: one address moves and the observable follows --------------------------


def test_one_address_apart_and_the_walk_reads_a_different_palette(world) -> None:
    """THE FALSIFIER. Same image, same sheet, same spec, one address apart.

    The layouts differ in their object palette address only. The two palettes carry the
    same colour at different indices, so the raster the walk builds is a read-out of
    which palette it read: corpus A's window is BLACK_A and WHITE_A, corpus B's is
    BLACK_B and WHITE_B. A planner that still spelled the object palette address would
    build one raster for both layouts, and every assertion below would fail on it.
    """
    _, assets, image, first, second = world
    assert [name for name in first.__dataclass_fields__
            if getattr(first, name) != getattr(second, name)] == ["object_palette_address"]

    raster_a = _only_cell(image, assets, first).raster
    raster_b = _only_cell(image, assets, second).raster
    table_a = ss.palette_indices(image, PALETTE_A)
    table_b = ss.palette_indices(image, PALETTE_B)

    assert ss.index_for_colour(BLACK, table_a) == BLACK_A
    assert ss.index_for_colour(WHITE, table_a) == WHITE_A
    assert ss.index_for_colour(BLACK, table_b) == BLACK_B
    assert ss.index_for_colour(WHITE, table_b) == WHITE_B
    assert raster_a == _sheet_raster(assets, table_a)
    # Every pixel of this crop window is the sheet's white column band, and the walk read
    # the palette it was handed: the same pixel is WHITE_A in the first run and WHITE_B in
    # the second, and the raster read through the other palette is not either of them.
    assert raster_a[0] == WHITE_A
    assert raster_b[0] == WHITE_B
    assert raster_b != _sheet_raster(assets, table_a)
    assert raster_a != raster_b


def test_one_address_apart_and_the_walk_reaches_a_different_structure(world) -> None:
    """The registry is layout-resolved too, seen through the container the walk reaches.

    Corpus B's registry names a structure whose piece names corpus B's container, so the
    offset the walk reports is corpus B's. A fixed registry address would report corpus
    A's container for both layouts.
    """
    _, assets, image, _, _ = world
    first, second = _layout(TABLE_A), _layout(TABLE_B)
    assert [name for name in first.__dataclass_fields__
            if getattr(first, name) != getattr(second, name)] == ["character_table_address"]

    cell_a = _only_cell(image, assets, first)
    cell_b = _only_cell(image, assets, second)
    assert cell_a.graphic_offset == CONTAINER_A
    assert cell_b.graphic_offset == CONTAINER_B
    assert cell_a.raster == cell_b.raster


# --- D5: a missing portrait key refuses by name --------------------------------


def test_a_portrait_swap_against_a_layout_without_the_key_refuses_by_name(
    world,
) -> None:
    """The refusal names the key and the profile, and falls back to no address."""
    _, assets, image, _, _ = world
    with pytest.raises(ss.SpriteSwapError) as refused:
        ss.swap(image, assets,
                portraits=(ss.PortraitSwap(slot=0, png=SHEET),),
                layout=_layout(TABLE_A, portrait=None))
    message = str(refused.value)
    assert PORTRAIT_KEY in message
    assert PROFILE_ID in message
    assert "no fallback address" in message


def test_a_pass_with_nothing_to_do_refuses_before_any_layout_is_read() -> None:
    """The existing refusal comes first, so no resolution changes its message."""
    with pytest.raises(ss.SpriteSwapError, match="no operation was given"):
        ss.swap(b"", Path("."), layout=None)


# --- D6: an existing profile still loads --------------------------------------


def test_the_shipped_catalogue_loads_with_the_new_key_and_its_own_values() -> None:
    layout = _shipped_profile().actor_sprites
    assert layout.character_table_address.raw == BASE + SHIPPED_TABLE
    assert layout.object_palette_address.raw == BASE + SHIPPED_PALETTE
    assert layout.portrait_table_address.raw == BASE + SHIPPED_PORTS
    assert layout.evidence.strip()


def _catalog_document(actor_sprites: dict) -> str:
    """A whole version-1 catalogue text around one synthetic profile.

    The loader is driven through a real document, so the exact-key guard is exercised
    where it lives rather than through a set this module built for itself.
    """
    mapping = {
        "id": "synthetic_actor_sprites_keys",
        "game": "synthetic",
        "region": "test",
        "game_code": "BG3E",
        "size": IMAGE_SIZE,
        "sha256": "0" * 64,
        "tables": {"actor_sprites": actor_sprites},
    }
    return yaml.safe_dump({"schema_version": 1, "profiles": [mapping]})


def _six_key_mapping() -> dict:
    """The six keys an ``actor_sprites`` declaration carried before this ticket."""
    return {
        "character_table_address": BASE + TABLE_A,
        "character_count": 1,
        "animation_pointer_offset": ANIMATION_OFFSET,
        "object_palette_address": BASE + PALETTE_A,
        "bg_palette_address": BASE + BG_PALETTE,
        "evidence": "synthetic declaration for the optional portrait key",
    }


def test_a_six_key_declaration_still_loads_and_a_stranger_key_is_refused() -> None:
    """The optional key is optional to the loader, and an unknown key is still refused.

    Driven through a real catalogue document so the exact-key guard is exercised: the
    six-key declaration loads with the portrait key None, and the same declaration plus
    one key the contract does not define fails on that guard.
    """
    loaded = RomProfileCatalog.loads(
        _catalog_document(_six_key_mapping()), source="synthetic six-key declaration"
    ).profiles[0]
    assert loaded.actor_sprites.portrait_table_address is None
    assert loaded.actor_sprites.object_palette_address.raw == BASE + PALETTE_A

    stranger = _six_key_mapping()
    stranger["portrait_table_addresses"] = BASE + PORTS
    with pytest.raises(ProfileConfigError, match="actor_sprites requires exact"):
        RomProfileCatalog.loads(
            _catalog_document(stranger), source="synthetic stranger key"
        )


# --- D7 to D9: the change is bounded ------------------------------------------


def test_the_census_row_for_the_planner_states_what_the_file_carries() -> None:
    """The row reason names no removed constant and the counts are the measured ones."""
    import tests.unit.address_literal_census as census

    row = next(item for item in census.EXEMPTIONS if item.path == PLANNER_NAME)
    measured = census.scan([PLANNER_NAME])[PLANNER_NAME]
    assert (row.hex5, row.rom_hex, row.decimal) == measured
    for gone in ("0x086B6BDC", "0x0805652C", "0x086F393C"):
        assert gone not in row.reason
    assert "0x08000000" in row.reason


def test_the_container_the_walk_reaches_declares_the_frames_own_extent(world) -> None:
    """The payload round trips, so the walk's raster is the sheet's window and not noise.

    Without this, the falsifier could pass on two identical refusals instead of two
    different rasters, which is the failure a profile-driven claim most often hides.
    """
    _, assets, image, first, _ = world
    cell = _only_cell(image, assets, first)
    container = wl.unpack(image, cell.graphic_offset)
    assert container.kind == sg.GRAPHICS_CONTAINER_KIND
    assert container.declared_size == _FRAME_W * _FRAME_H
    assert cell.raster == _sheet_raster(assets, ss.palette_indices(image, PALETTE_A))
