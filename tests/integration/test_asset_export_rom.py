"""ROM-gated integration evidence for ASSET-EXPORT-001.

Read-only against the canonical image. The suite skips cleanly when the private
ROM is not configured, and it never writes to it.

**What this module pins.** The accepted populations the exporter must account
for, the per-map layer classification, key diversity, and a set of representative
rendered pixel digests: several complete maps and their individual layers, a map
whose selector stream reaches the `0x3C40`-declaring bank, individual chunks,
individual bank tiles, a bank sheet, single-piece sprite frames, both a 2-piece
and a 4-piece multipart frame, and the two palettes. Every expectation is a
count, an address, an index, a dimension or a digest over decoded pixels; no
decoded asset is committed.

**Why the analysis is done once.** Walking the map graph assembles character
blocks for 452 maps and decodes 3,745 chunk containers, and walking the sprite
graph decodes 7,390 graphics containers. Both are read-only and deterministic, so
the module shares one analysis between every test rather than repeating it.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.export import buu_resource_export as export
from tools.export import canonical as canon
from tools.export import naming
from tools.export import png
from tools.export import render

# --- accepted populations ----------------------------------------------------

EXPECTED_MAP_ENTRIES = 452
EXPECTED_LAYER_REFERENCES = 1808
EXPECTED_DOMINANT_LAYER_HANDLER = 0x08008087
EXPECTED_ABSENT_LAYER_HANDLER = 0x08007A41
EXPECTED_NON_GRAPHICAL_LAYER_HANDLER = 0x0800897B
EXPECTED_SCREENBLOCK_LAYER_HANDLER = 0x08007B63
EXPECTED_UNRESOLVED_ASSEMBLY_LAYER_HANDLER = 0x080088BD
EXPECTED_NON_DOMINANT_HANDLERS = (
    EXPECTED_NON_GRAPHICAL_LAYER_HANDLER,
    EXPECTED_SCREENBLOCK_LAYER_HANDLER,
    EXPECTED_UNRESOLVED_ASSEMBLY_LAYER_HANDLER,
)

#: Layer `+0x00` handler census over the 1,808 references. Five values, exact.
EXPECTED_HANDLER_CENSUS = {
    0x08008087: 1516,
    0x0800897B: 41,
    0x08007A41: 249,
    0x08007B63: 1,
    0x080088BD: 1,
}

#: Classification over the same references, after ASSET-EXPORT-MAP-HANDLERS-001
#: established what each non-dominant constructor does.
EXPECTED_CLASS_CENSUS = {
    "dominant": 1516,
    "absent_placeholder": 249,
    "non_graphical": 41,
    "static_graphical_screenblock": 1,
    "static_graphical_assembly_unresolved": 1,
}

#: The 43 previously unresolved references, by final class.
EXPECTED_NON_GRAPHICAL_REFERENCES = 41
EXPECTED_SCREENBLOCK_REFERENCES = 1
EXPECTED_UNRESOLVED_ASSEMBLY_REFERENCES = 1
EXPECTED_UNRESOLVED_REFERENCES_AFTER = 0

#: Rendered map layers and composites after the classification.
EXPECTED_MAP_LAYERS_RENDERED = 1517
EXPECTED_MAP_COMPOSITES = 450
EXPECTED_MAP_COMPOSITES_WITHHELD = 2

#: Map 19's screenblock layer, and the two maps that stay withheld.
EXPECTED_SCREENBLOCK_MAP = 19
EXPECTED_SCREENBLOCK_SLOT = 1
EXPECTED_SCREENBLOCK_DIMENSIONS = (256, 256)
EXPECTED_SCREENBLOCK_MAX_ORDINAL = 538
EXPECTED_UNRESOLVED_ASSEMBLY_MAP = 19
EXPECTED_UNRESOLVED_ASSEMBLY_SLOT = 2
EXPECTED_UNRESOLVED_ASSEMBLY_GRID = (14, 10)
EXPECTED_UNRESOLVED_ASSEMBLY_CHUNKS = 140
EXPECTED_UNRESOLVED_ASSEMBLY_CHUNK_BYTES = 1024
EXPECTED_WITHHELD_COMPOSITES = {
    8: "withheld_no_renderable_layer",
    19: "withheld_unresolved_layer",
}

#: A map whose four slots are all `non_graphical` renders no image at all.
EXPECTED_ALL_NON_GRAPHICAL_MAP = 8
#: Composites recovered by no longer letting a non-graphical slot block one.
EXPECTED_RECOVERED_COMPOSITES = 28

#: Representative pixel digests for the newly rendered screenblock layer and for
#: composites that the classification recovered, measured once and pinned.
EXPECTED_SCREENBLOCK_SHA256 = (
    "a9e283ba2fa92ff9661a80cd51fe777021a7a41bb72dbe88b0ba6b7c334d914a"
)
EXPECTED_RECOVERED_COMPOSITE_SHA256 = {
    7: "c11d5f986b3333800fccd89e4992c30c92db6929c5a2b1e4818fc927fe7d2e55",
    14: "176b7a84f07caf6a6d23df841be0b3cf048632845072976da40b509451831623",
    17: "e12211f7253e2bc02d0afc7523c8f41f8617f4b0c43cd087f1be5d98803d1bf2",
    22: "406e65d764617dad2d0f536a3b7e053a532787d1054cb77fb277d1410c2c4c4a",
    390: "8b4aedbcc8276fd39e16036b74db122ed5b86d986dc3e7c1adc7fd861a02b122",
}
EXPECTED_RECOVERED_COMPOSITE_SIZE = {
    7: (256, 256),
    14: (256, 256),
    17: (512, 512),
    22: (512, 512),
    390: (512, 512),
}

EXPECTED_CHUNKS = 3745
EXPECTED_CHUNKS_WITH_RENDER_VARIANTS = 1
EXPECTED_TILE_BANKS = 187
EXPECTED_INDIVIDUAL_TILES = 47857
EXPECTED_BANK_186_DECLARED_SIZE = 0x3C40
EXPECTED_BANK_DECLARED_SIZE = 0x4000

EXPECTED_SPRITE_DEFINITIONS = 297
EXPECTED_ANIMATION_SLOTS = 4070
EXPECTED_NON_NULL_ANIMATIONS = 1721
EXPECTED_NULL_ANIMATION_SLOTS = 2349
EXPECTED_UNIQUE_ANIMATIONS = 1017
EXPECTED_UNIQUE_FRAMES = 10980
EXPECTED_SPRITE_PIECES = 11005
EXPECTED_MULTIPART_FRAMES = 21
EXPECTED_STRUCTURED_SPRITE_GRAPHICS = 7390
EXPECTED_DIRECTIONAL_FRAME_IMAGES = 23068
EXPECTED_PIECE_REFERENCES_OVER_ANIMATION_REFERENCES = 23180
EXPECTED_SPRITE_ID_FLOOR = 10
EXPECTED_SPRITE_ID_CEILING = 306

#: Appearance definitions: 232 records, of which 198 name a sprite definition.
EXPECTED_APPEARANCE_DEFINITIONS = 232
EXPECTED_SPRITES_REACHED_BY_APPEARANCE = 198
EXPECTED_SPRITES_WITH_A_RESOLVED_NAME = 198
EXPECTED_DISTINCT_SPRITE_NAME_STRINGS = 147
EXPECTED_SPRITES_WITH_SEVERAL_APPEARANCES = 25
EXPECTED_SPRITES_WHOSE_APPEARANCES_DISAGREE = 8
EXPECTED_MAPS_WITH_A_RESOLVED_NAME = 429
EXPECTED_DISTINCT_MAP_NAME_STRINGS = 69
EXPECTED_MAP_DIRECTORIES = 452
EXPECTED_SPRITE_DIRECTORIES = 297

#: Representative rendered digests, measured once and pinned.
EXPECTED_MAP_LAYER_SHA256 = {
    (0, 0): "07a1c9616e9fadb503aee299e2c5054ae25c1ea5e53c75850b5f4c243364eb7c",
    (0, 1): "01360477dcd4530cc9ca69449261db8f9f48ae358e4360cb52753ad3645d5577",
    (0, 2): "e49f1e7fd9e42d7a3a6340273709df9d14e398b34e2d31ebba9b110c4263d5eb",
    (0, 3): "161388eb64884f8bef7547a4baee26b458fd2d328cbb59e7ee11562db068e279",
    (19, 0): "ce51515046b02d78f845b39d73f01105de23bb2f6a59f47d34f2bab7afe23fa7",
    (39, 1): "feff3ae66958421fdb5c948f7c5c7ef3c235a216f22f4d2ea66f38e44b41e00c",
    (39, 2): "7694f6b6b219a5c9c29652b725b6364091bbb1fb569fe537c42ff84497a63178",
    (39, 3): "1af2467839193b4d903b3eb425fae4ca192a6b9828de18700c9660c60360c465",
    (40, 0): "89647c416d9a63366719324fe824c5088a39b9a296a41845643c1abad8e5e079",
    (40, 1): "943271572aba1594cc19d49ccb6b5ab7066f1c69979b3d4470a68b0e044e80c1",
    (40, 2): "4ca99ca8824e4eebab30de100a7ca3610a2e5b7b5beac096189e0428504fef98",
    (40, 3): "812d808704ddbf122c704fa45ac8c9d8b8bd8cf24813700b9d95b68cf01d9dbd",
    (125, 3): "718fdc0c8c44f340ec1ee5b16186067a6cdbf64b6a8519d925b353368ad15cbf",
}

EXPECTED_MAP_COMPOSITE_SHA256 = {
    0: "ff02d371c5f49035701c3a8d7e5bc178ae7ddd6433c066b5053e6cbcc5117407",
    39: "35d3b51f0929a9d1d408786b651b314f1458028f4a5d9ae1440d8ba78388ed2b",
    40: "21985e5c58150499b13c29696cabadd84956708e7f901b2b6ceb2c9bd6c70f9d",
    125: "718fdc0c8c44f340ec1ee5b16186067a6cdbf64b6a8519d925b353368ad15cbf",
}

EXPECTED_MAP_COMPOSITE_SIZE = {
    0: (1280, 256),
    39: (1024, 512),
    40: (512, 512),
    125: (256, 512),
}

EXPECTED_CHUNK_SHA256 = {
    0x08179A50: "aacfe538786cf8140fc69280a0db4986a15c26f5dce83d7f433c06e14340f6af",
    0x08179C38: "7464272d44c59b3b5d5c1f80737bd8b1f937571ec1426477c47114e432a8ecf7",
    0x08179C54: "75a62dcf5a6468a53cf59c4d0b37a1daa9e0d76f30bedfb9a28bf775ca71eb46",
    0x082B8B94: "05f6909629840842ae89888d79594dd69beccb5fa3c13152e8647892dec13fe5",
    0x082B8BAC: "8b20bf0ff92c308f2caf471af5f5fae27819fc78f591201341cd77d90cb1c465",
}

EXPECTED_GRAPHIC_SHA256 = {
    0x083C34D0: ("0905c525332a178e317b2b82008e8416cdd1ca098fb2da38513118ec51a5aea9", 32, 32),
    0x0854A5C8: ("d11e9d4db78e59763cc976b601fd8e79ad495bf2c4644d9867279c45fe254821", 16, 32),
    0x086A87A8: ("bb47ca4ca0a18c68bbcad016fcb45ddb65bd10e96d4c9c96aae62b282bcbe76e", 32, 32),
}

EXPECTED_BANK_PAYLOAD_SHA256 = {
    0: "ccfa6a39379a38a292504012568d6bd39bd7c50bf5c50cb4e2334fd5370953f0",
    186: "e1c9b6dd8a61ace97e7009f8b7523666150575737933b9ec706108b25e608909",
}
EXPECTED_BANK_TILE_SHA256 = {
    (0, 0): "f5a5fd42d16a20302798ef6ed309979b43003d2320d9f0e8ea9831a92759fb4b",
    (0, 1): "ab6642f1638fe5b7c743b0cc698a9dea8b58850321a1f0002bd7823c8ed70e47",
    (186, 0): "515abd8d590b8adf1ed14e0fbd6c933cecd178fb122bed9e3fa04e56f70fa29b",
    (186, 1): "bfd3532cf1b0a00121f52573db31011fa371dcb6349244ddc83cdc50e9843334",
}
EXPECTED_BANK_SHEET_SHA256 = {
    0: "2cb6c17273f66d826de61effe09e1867f65048e55eabb5f911014b9df3b27980",
}

#: The one 4-piece and the one shared 2-piece frame used as multipart evidence.
FOUR_PIECE_FRAME = 0x08579890
TWO_PIECE_FRAME = 0x08423128
EXPECTED_FOUR_PIECE_SHA256 = (
    "11be11900e4da77976da26e1e4717fe04243078e368a66efe3ae739b46837a38"
)
EXPECTED_TWO_PIECE_SHA256 = (
    "949d00341e7926bcba9379b4e6c56d5dc329ac6050f21c46a1defb072ae1e60e"
)

#: Logical sprite id 10's first animation slot, first frame index, direction 0.
EXPECTED_FIRST_SPRITE_SHA256 = (
    "0905c525332a178e317b2b82008e8416cdd1ca098fb2da38513118ec51a5aea9"
)
EXPECTED_FIRST_SPRITE_FRAME = 0x083C3A24

EXPECTED_BG_PALETTE_SHA256 = (
    "0fdd0d9d84499b27def5c28be3c787cabbba5a2d285722e5c7bcd60a5cb65fab"
)
EXPECTED_OBJECT_PALETTE_SHA256 = (
    "777be7ad352bc0b24905b1da3e946b6d817af8b00658f8f0f26dfbf2d2b5863f"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- fixtures ----------------------------------------------------------------

@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    """The canonical image, read once and identity-checked."""
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert digest(data) == export.CANONICAL_ROM_SHA256
    return data


@pytest.fixture(scope="module")
def exporter(canonical_bytes: bytes, tmp_path_factory) -> export.Exporter:
    """One shared, read-only analysis of both graphs."""
    root = tmp_path_factory.mktemp("asset-export-analysis")
    analysis = export.Exporter(canon.Rom(canonical_bytes), root / "out", root / "audit")
    analysis.writer.enabled = False
    analysis.subsystems = {"maps", "tiles", "sprites"}
    analysis.collect_names()
    analysis.collect_map_graph()
    analysis.collect_sprite_graph()
    return analysis


# --- ROM-derived names -------------------------------------------------------

def test_appearance_definitions_and_the_names_they_carry(
    exporter: export.Exporter,
) -> None:
    assert len(exporter.appearances) == EXPECTED_APPEARANCE_DEFINITIONS
    assert len(exporter.appearances_by_sprite) == (
        EXPECTED_SPRITES_REACHED_BY_APPEARANCE
    )
    assert len(exporter.sprite_names) == EXPECTED_SPRITES_WITH_A_RESOLVED_NAME
    assert len(set(exporter.sprite_names.values())) == (
        EXPECTED_DISTINCT_SPRITE_NAME_STRINGS
    )
    several = sum(
        1 for records in exporter.appearances_by_sprite.values() if len(records) > 1
    )
    assert several == EXPECTED_SPRITES_WITH_SEVERAL_APPEARANCES
    disagree = 0
    for records in exporter.appearances_by_sprite.values():
        names = {
            exporter.rom.text(record.name_text_index)
            for record in records
            if exporter.rom.text(record.name_text_index)
        }
        if len(names) > 1:
            disagree += 1
    assert disagree == EXPECTED_SPRITES_WHOSE_APPEARANCES_DISAGREE


def test_every_appearance_selects_a_sprite_inside_the_run(
    exporter: export.Exporter,
) -> None:
    """The `+0x04` selection is a logical sprite id, and every one resolves."""
    valid = {definition.sprite_id for definition in exporter.definitions}
    for record in exporter.appearances:
        assert record.sprite_id in valid, record.appearance_index


def test_map_names_resolve_from_the_text_table(exporter: export.Exporter) -> None:
    assert len(exporter.map_names) == EXPECTED_MAPS_WITH_A_RESOLVED_NAME
    assert len(set(exporter.map_names.values())) == EXPECTED_DISTINCT_MAP_NAME_STRINGS
    assert exporter.map_name(39) == "Grand Kai's Planet"
    assert exporter.map_name(451) == "Heaven"
    assert exporter.map_name(8) is None


def test_named_directories_are_unique_and_carry_the_numeric_id(
    exporter: export.Exporter,
) -> None:
    map_directories = {
        naming.map_directory(entry.index, exporter.map_name(entry.index))
        for entry in exporter.map_entries
    }
    assert len(map_directories) == EXPECTED_MAP_DIRECTORIES
    sprite_directories = {
        naming.sprite_directory(
            definition.sprite_id, exporter.sprite_name(definition.sprite_id)
        )
        for definition in exporter.definitions
    }
    assert len(sprite_directories) == EXPECTED_SPRITE_DIRECTORIES
    assert naming.map_directory(39, exporter.map_name(39)) == (
        "map_039_grand_kai_s_planet"
    )
    assert naming.sprite_directory(28, exporter.sprite_name(28)) == "sprite_028_babidi"
    for directory in map_directories | sprite_directories:
        assert directory.isascii() and directory == directory.lower()
        assert directory.split("_")[1].isdigit()


def test_a_map_whose_layers_are_all_non_graphical_still_gets_a_directory(
    exporter: export.Exporter,
) -> None:
    """Map 8's four slots are all `non_graphical`, and it is still inventoried.

    Rendering nothing must not remove the identity: the map writes its own record,
    which is what creates the directory. Its composite is withheld for a proven
    structural reason - there is no graphical layer to compose.
    """
    assert [layer.classification for layer in exporter.layers[8]] == [
        "non_graphical"
    ] * 4
    assert exporter.map_name(8) is None
    assert naming.map_directory(8, None) == "map_008"
    assert naming.map_directory(
        EXPECTED_ALL_NON_GRAPHICAL_MAP, exporter.map_name(EXPECTED_ALL_NON_GRAPHICAL_MAP)
    ) == "map_008"


# --- ASSET-EXPORT-MAP-HANDLERS-001: the 43 non-dominant references ------------

def test_all_43_non_dominant_references_have_a_final_class(
    exporter: export.Exporter,
) -> None:
    """Zero remaining unresolved references, and no unknown handler anywhere."""
    counted = {"non_graphical": 0, "static_graphical_screenblock": 0,
               "static_graphical_assembly_unresolved": 0}
    for records in exporter.layers.values():
        for layer in records:
            assert layer.classification != "unclassified_handler"
            if layer.classification in counted:
                counted[layer.classification] += 1
    assert counted["non_graphical"] == EXPECTED_NON_GRAPHICAL_REFERENCES
    assert counted["static_graphical_screenblock"] == EXPECTED_SCREENBLOCK_REFERENCES
    assert counted["static_graphical_assembly_unresolved"] == (
        EXPECTED_UNRESOLVED_ASSEMBLY_REFERENCES
    )
    assert sum(counted.values()) == 43


def test_non_graphical_slots_do_not_block_a_composite(
    exporter: export.Exporter,
) -> None:
    """The whole point of the classification: a slot that draws nothing cannot
    make a static composite unfaithful, so it must stop withholding one."""
    for records in exporter.layers.values():
        for layer in records:
            if layer.classification in ("non_graphical", "absent_placeholder"):
                assert layer.graphical is False
                assert layer.blocks_composite is False
            elif layer.classification == "static_graphical_assembly_unresolved":
                assert layer.graphical is True
                assert layer.blocks_composite is True
            else:
                assert layer.graphical is True
                assert layer.blocks_composite is False


def test_the_screenblock_layer_renders_from_the_maps_own_char_block(
    exporter: export.Exporter,
) -> None:
    """Handler `0x08007B63` decompresses a 0x800-byte screen-entry plane.

    Its tile ordinals must resolve inside the map's own assembled character
    block, which is the structural check that makes the plane renderable at all.
    """
    layer = exporter.layers[EXPECTED_SCREENBLOCK_MAP][EXPECTED_SCREENBLOCK_SLOT]
    assert layer.handler == EXPECTED_SCREENBLOCK_LAYER_HANDLER
    assert layer.classification == "static_graphical_screenblock"
    entries = canon.read_screenblock_entries(exporter.rom, layer.address)
    assert len(entries) == canon.SCREENBLOCK_ENTRY_COUNT
    ordinals = [word & canon.TILE_ENTRY_ORDINAL_MASK for word in entries]
    assert max(ordinals) == EXPECTED_SCREENBLOCK_MAX_ORDINAL
    block = exporter.char_blocks[EXPECTED_SCREENBLOCK_MAP]
    assert block.tile_count == EXPECTED_SCREENBLOCK_MAX_ORDINAL + 1
    pixels = render.render_chunk(entries, block.data)
    assert len(pixels) == (
        EXPECTED_SCREENBLOCK_DIMENSIONS[0] * EXPECTED_SCREENBLOCK_DIMENSIONS[1]
    )
    assert digest(pixels) == EXPECTED_SCREENBLOCK_SHA256
    assert sum(1 for value in pixels if value) == 14336


@pytest.mark.parametrize("map_index", sorted(EXPECTED_RECOVERED_COMPOSITE_SHA256))
def test_composites_recovered_by_the_classification_render_deterministically(
    exporter: export.Exporter, map_index: int
) -> None:
    """Every layer in these maps is now either rendered or proven non-graphical."""
    records = exporter.layers[map_index]
    assert not any(layer.blocks_composite for layer in records)
    rendered = []
    for layer in records:
        if layer.classification == "static_graphical_screenblock":
            pixels = render.render_chunk(
                exporter.screenblock_entries[layer.address],
                exporter.char_blocks[map_index].data,
            )
            width = height = canon.SCREENBLOCK_PIXELS
        elif layer.classification == "dominant":
            pixels = exporter.render_layer(layer, map_index)
            width = layer.chunk_x * canon.CHUNK_PIXELS
            height = layer.chunk_y * canon.CHUNK_PIXELS
        else:
            continue
        addend = exporter.rom.u8(
            exporter.map_entries[map_index].root_address
            + canon.ROOT_BG_ADDEND_OFFSET
            + layer.slot
        )
        rendered.append((addend, layer.slot, width, height, pixels))
    width = max(item[2] for item in rendered)
    height = max(item[3] for item in rendered)
    assert (width, height) == EXPECTED_RECOVERED_COMPOSITE_SIZE[map_index]
    composite = render.compose_layers(rendered, width, height)
    assert digest(composite) == EXPECTED_RECOVERED_COMPOSITE_SHA256[map_index]


def test_the_screenblock_record_names_one_container_twice(
    exporter: export.Exporter,
) -> None:
    """`record + 0x04` and `record + 0x08` are the two buffers the constructor
    fills; on the canonical record they name the same container, which is what
    makes the plane unambiguous."""
    layer = exporter.layers[EXPECTED_SCREENBLOCK_MAP][EXPECTED_SCREENBLOCK_SLOT]
    first = exporter.rom.u32(layer.address + canon.SCREENBLOCK_CONTAINER_OFFSET)
    second = exporter.rom.u32(
        layer.address + canon.SCREENBLOCK_SECOND_CONTAINER_OFFSET
    )
    assert first == second
    assert exporter.rom.offset(first) >= 0


def test_the_unresolved_assembly_record_is_recorded_structurally(
    exporter: export.Exporter,
) -> None:
    """Handler `0x080088BD` streams a grid of 0x400-byte containers.

    The grid product equals the number of container pointers the record carries,
    which is why the record is graphical; the pixel arrangement of a container is
    what stays unresolved.
    """
    layer = exporter.layers[EXPECTED_UNRESOLVED_ASSEMBLY_MAP][
        EXPECTED_UNRESOLVED_ASSEMBLY_SLOT
    ]
    assert layer.handler == EXPECTED_UNRESOLVED_ASSEMBLY_LAYER_HANDLER
    probe = canon.read_unresolved_assembly_probe(exporter.rom, layer.address)
    assert (probe["grid_x"], probe["grid_y"]) == EXPECTED_UNRESOLVED_ASSEMBLY_GRID
    assert probe["chunk_targets"] == EXPECTED_UNRESOLVED_ASSEMBLY_CHUNKS
    assert probe["grid_product"] == EXPECTED_UNRESOLVED_ASSEMBLY_CHUNKS
    assert probe["chunk_decoded_bytes"] == (
        EXPECTED_UNRESOLVED_ASSEMBLY_CHUNK_BYTES
    )
    assert probe["resident_slots"] == canon.UNRESOLVED_ASSEMBLY_RESIDENT_SLOTS


def test_the_unresolved_assembly_containers_decode_at_their_declared_size(
    exporter: export.Exporter,
) -> None:
    layer = exporter.layers[EXPECTED_UNRESOLVED_ASSEMBLY_MAP][
        EXPECTED_UNRESOLVED_ASSEMBLY_SLOT
    ]
    for index in range(EXPECTED_UNRESOLVED_ASSEMBLY_CHUNKS):
        address = exporter.rom.u32(
            layer.address + canon.UNRESOLVED_ASSEMBLY_CHUNK_OFFSET + 4 * index
        )
        container = exporter.rom.container(address)
        assert container.declared_size == EXPECTED_UNRESOLVED_ASSEMBLY_CHUNK_BYTES


def test_composites_recovered_and_withheld(
    exporter: export.Exporter,
) -> None:
    """28 of the 30 previously withheld maps now compose; the two that do not
    carry a proven structural reason instead of an unknown handler."""
    blocking = {
        map_index
        for map_index, records in exporter.layers.items()
        if any(layer.blocks_composite for layer in records)
    }
    assert blocking == {EXPECTED_UNRESOLVED_ASSEMBLY_MAP}
    assert set(EXPECTED_WITHHELD_COMPOSITES) == {
        EXPECTED_UNRESOLVED_ASSEMBLY_MAP,
        EXPECTED_ALL_NON_GRAPHICAL_MAP,
    }
    assert EXPECTED_RECOVERED_COMPOSITES == 28
    for map_index in (7, 14, 17, 20, 21, 22, 116, 270, 390, 414):
        assert any(
            layer.classification == "non_graphical"
            for layer in exporter.layers[map_index]
        )
        assert not any(layer.blocks_composite for layer in exporter.layers[map_index])


# --- completion gates --------------------------------------------------------

def test_zero_decode_and_render_failures(exporter: export.Exporter) -> None:
    assert [failure.as_document() for failure in exporter.failures] == []


def test_map_entries_accounted_for(exporter: export.Exporter) -> None:
    assert len(exporter.map_entries) == EXPECTED_MAP_ENTRIES
    assert len(exporter.layers) == EXPECTED_MAP_ENTRIES
    assert len(exporter.char_blocks) == EXPECTED_MAP_ENTRIES


def test_every_map_layer_slot_is_classified(exporter: export.Exporter) -> None:
    """No silent omissions: all 1,808 references carry a structural class."""
    references = 0
    for records in exporter.layers.values():
        assert len(records) == 4
        for layer in records:
            references += 1
            assert layer.classification
    assert references == EXPECTED_LAYER_REFERENCES


def test_layer_handler_census(exporter: export.Exporter) -> None:
    census: dict[int, int] = {}
    classes: dict[str, int] = {}
    for records in exporter.layers.values():
        for layer in records:
            census[layer.handler] = census.get(layer.handler, 0) + 1
            classes[layer.classification] = classes.get(layer.classification, 0) + 1
    assert census == EXPECTED_HANDLER_CENSUS
    assert classes == EXPECTED_CLASS_CENSUS
    assert set(census) == {
        EXPECTED_DOMINANT_LAYER_HANDLER,
        EXPECTED_ABSENT_LAYER_HANDLER,
        *EXPECTED_NON_DOMINANT_HANDLERS,
    }


def test_the_absent_placeholder_is_one_shared_zero_dimension_record(
    exporter: export.Exporter,
) -> None:
    addresses = set()
    for records in exporter.layers.values():
        for layer in records:
            if layer.classification == "absent_placeholder":
                addresses.add(layer.address)
                assert (layer.chunk_x, layer.chunk_y) == (0, 0)
    assert addresses == {canon.ABSENT_LAYER_RECORD}


def test_no_dominant_layer_has_a_partial_or_empty_grid(
    exporter: export.Exporter,
) -> None:
    for records in exporter.layers.values():
        for layer in records:
            if layer.classification == "dominant":
                assert layer.chunk_x > 0 and layer.chunk_y > 0


def test_chunk_population_and_variant_count(exporter: export.Exporter) -> None:
    assert len(exporter.chunk_entries) == EXPECTED_CHUNKS
    signatures: dict[int, set[bytes]] = {}
    for address, maps in exporter.chunk_maps.items():
        candidates = [m for m in set(maps) if m in exporter.char_blocks]
        signatures[address] = {
            exporter.chunk_render_signature(address, m) for m in candidates
        }
    assert len(signatures) == EXPECTED_CHUNKS
    variants = sum(1 for value in signatures.values() if len(value) > 1)
    assert variants == EXPECTED_CHUNKS_WITH_RENDER_VARIANTS


def test_every_layer_tile_ordinal_is_supplied_by_the_map(
    exporter: export.Exporter,
) -> None:
    """The render itself is the check: an ordinal with no tile raises."""
    rendered = 0
    for map_index, records in exporter.layers.items():
        for layer in records:
            if layer.classification != "dominant":
                continue
            exporter.render_layer(layer, map_index)
            rendered += 1
    assert rendered == EXPECTED_HANDLER_CENSUS[EXPECTED_DOMINANT_LAYER_HANDLER]


def test_bank_table_is_complete(canonical_bytes: bytes) -> None:
    banks = canon.read_banks(canon.Rom(canonical_bytes))
    assert len(banks) == EXPECTED_TILE_BANKS
    assert sum(bank.tile_count for bank in banks) == EXPECTED_INDIVIDUAL_TILES
    assert banks[-1].declared_size == EXPECTED_BANK_186_DECLARED_SIZE
    assert all(
        bank.declared_size == EXPECTED_BANK_DECLARED_SIZE for bank in banks[:-1]
    )
    for index, bank in EXPECTED_BANK_PAYLOAD_SHA256.items():
        assert digest(banks[index].payload) == bank


def test_the_dominant_selector_stream_reaches_bank_186(
    exporter: export.Exporter,
) -> None:
    """The 0x3C40-declaring bank is used, so it must not be assumed 0x4000."""
    highest = 0
    for entry in exporter.map_entries:
        selectors = canon.read_selector_stream(exporter.rom, entry.root_address)
        highest = max(highest, max(value >> 8 for value in selectors))
    assert highest == EXPECTED_TILE_BANKS - 1


def test_sprite_definition_population(exporter: export.Exporter) -> None:
    definitions = exporter.definitions
    assert len(definitions) == EXPECTED_SPRITE_DEFINITIONS
    assert definitions[0].sprite_id == EXPECTED_SPRITE_ID_FLOOR
    assert definitions[-1].sprite_id == EXPECTED_SPRITE_ID_CEILING
    assert sum(d.slots for d in definitions) == EXPECTED_ANIMATION_SLOTS
    assert sum(d.non_null_slots for d in definitions) == EXPECTED_NON_NULL_ANIMATIONS
    assert (
        sum(d.slots - d.non_null_slots for d in definitions)
        == EXPECTED_NULL_ANIMATION_SLOTS
    )
    assert (
        sum(d.slots for d in definitions)
        - sum(d.non_null_slots for d in definitions)
        == EXPECTED_NULL_ANIMATION_SLOTS
    )


def test_sprite_graph_population(exporter: export.Exporter) -> None:
    assert len(exporter.animations) == EXPECTED_UNIQUE_ANIMATIONS
    assert len(exporter.frames) == EXPECTED_UNIQUE_FRAMES
    assert sum(f.piece_count for f in exporter.frames.values()) == EXPECTED_SPRITE_PIECES
    assert (
        sum(1 for f in exporter.frames.values() if f.piece_count > 1)
        == EXPECTED_MULTIPART_FRAMES
    )
    assert len(exporter.graphic_indices) == EXPECTED_STRUCTURED_SPRITE_GRAPHICS


def test_piece_counts_are_bounded_and_directions_are_four(
    exporter: export.Exporter,
) -> None:
    piece_counts: dict[int, int] = {}
    for frame in exporter.frames.values():
        piece_counts[frame.piece_count] = piece_counts.get(frame.piece_count, 0) + 1
    assert piece_counts == {1: 10959, 2: 19, 4: 2}
    for animation in exporter.animations.values():
        assert 1 <= animation.frame_count <= canon.ANIMATION_FRAME_COUNT_MAX
        assert animation.direction_cells == animation.frame_count * canon.DIRECTION_COUNT


def test_graphics_container_extents_match_their_pieces(
    exporter: export.Exporter,
) -> None:
    """Every reachable container is declared `dim_0 * dim_1` bytes and whole tiles."""
    for address, (width, height) in exporter.graphic_extents.items():
        assert width % canon.TILE_PIXELS == 0
        assert height % canon.TILE_PIXELS == 0
        assert len(exporter.graphic_indices[address]) == width * height
        assert exporter.rom.u32(address + 4) == width * height


# --- representative rendered pixel digests -----------------------------------

@pytest.mark.parametrize("map_index", sorted({m for m, _ in EXPECTED_MAP_LAYER_SHA256}))
def test_representative_map_layer_pixels(
    exporter: export.Exporter, map_index: int
) -> None:
    expected = {
        slot: value
        for (index, slot), value in EXPECTED_MAP_LAYER_SHA256.items()
        if index == map_index
    }
    rendered = 0
    for layer in exporter.layers[map_index]:
        if layer.slot not in expected:
            continue
        assert layer.classification == "dominant"
        assert digest(exporter.render_layer(layer, map_index)) == expected[layer.slot]
        rendered += 1
    assert rendered == len(expected)


@pytest.mark.parametrize("map_index", sorted(EXPECTED_MAP_COMPOSITE_SHA256))
def test_representative_map_composites(
    exporter: export.Exporter, map_index: int
) -> None:
    records = exporter.layers[map_index]
    assert all(
        layer.classification in ("dominant", "absent_placeholder") for layer in records
    )
    rendered = [
        (
            exporter.rom.u8(
                exporter.map_entries[map_index].root_address
                + canon.ROOT_BG_ADDEND_OFFSET
                + layer.slot
            ),
            layer.slot,
            layer.chunk_x * canon.CHUNK_PIXELS,
            layer.chunk_y * canon.CHUNK_PIXELS,
            exporter.render_layer(layer, map_index),
        )
        for layer in records
        if layer.classification == "dominant"
    ]
    width = max(item[2] for item in rendered)
    height = max(item[3] for item in rendered)
    assert (width, height) == EXPECTED_MAP_COMPOSITE_SIZE[map_index]
    composite = render.compose_layers(rendered, width, height)
    assert digest(composite) == EXPECTED_MAP_COMPOSITE_SHA256[map_index]


def test_map_19_composite_is_withheld_for_a_proven_reason(
    exporter: export.Exporter,
) -> None:
    """One slot draws, is graphical, and still cannot be assembled faithfully.

    The reason recorded is a structural classification, not "unknown handler".
    """
    classes = [layer.classification for layer in exporter.layers[19]]
    assert classes == [
        "dominant",
        "static_graphical_screenblock",
        "static_graphical_assembly_unresolved",
        "absent_placeholder",
    ]
    assert [layer.blocks_composite for layer in exporter.layers[19]] == [
        False, False, True, False,
    ]
    assert 19 not in EXPECTED_MAP_COMPOSITE_SHA256
    assert EXPECTED_WITHHELD_COMPOSITES[19] == "withheld_unresolved_layer"


def test_null_chunk_cells_are_recorded_structurally(
    exporter: export.Exporter,
) -> None:
    """The unresolved null-cell reading is counted, not hidden.

    The accepted record set carries an internal null in 117 of the 1,420
    dominant layer records, across 86 maps, occupying 156 of the 4,274 grid
    cells - which is exactly the accepted `4274 = 156 null + 4118 non-null`
    arithmetic, measured here over the 452-MapEntry population. What such a cell
    displays is an open question; the exporter renders it as no-data and records
    the population rather than claiming the question is settled.
    """
    records = 0
    cells = 0
    maps = 0
    grid_cells = 0
    for layers in exporter.layers.values():
        touched = False
        for layer in layers:
            if layer.classification != "dominant":
                continue
            grid_cells += layer.chunk_cells
            if layer.null_chunk_count:
                records += 1
                cells += layer.null_chunk_count
                touched = True
        if touched:
            maps += 1
    assert records == 117
    assert cells == 156
    assert maps == 86
    assert grid_cells == 4274
    assert grid_cells - cells == 4118


def test_the_default_chunk_container_carries_no_data(canonical_bytes: bytes) -> None:
    container = canon.Rom(canonical_bytes).container(canon.DEFAULT_CHUNK_CONTAINER)
    assert container.kind == 0
    assert container.declared_size == 0
    assert container.data == b""


def test_map_19_dominant_layer_still_renders(exporter: export.Exporter) -> None:
    assert digest(exporter.render_layer(exporter.layers[19][0], 19)) == (
        EXPECTED_MAP_LAYER_SHA256[(19, 0)]
    )


@pytest.mark.parametrize("address", sorted(EXPECTED_CHUNK_SHA256))
def test_representative_chunk_pixels(
    exporter: export.Exporter, address: int
) -> None:
    map_index = min(
        index for index in set(exporter.chunk_maps[address]) if index in exporter.char_blocks
    )
    pixels = render.render_chunk(
        exporter.chunk_entries[address], exporter.char_blocks[map_index].data
    )
    assert len(pixels) == canon.CHUNK_PIXELS * canon.CHUNK_PIXELS
    assert digest(pixels) == EXPECTED_CHUNK_SHA256[address]


@pytest.mark.parametrize("address", sorted(EXPECTED_GRAPHIC_SHA256))
def test_representative_sprite_graphics(
    exporter: export.Exporter, address: int
) -> None:
    expected, width, height = EXPECTED_GRAPHIC_SHA256[address]
    assert exporter.graphic_extents[address] == (width, height)
    assert digest(exporter.graphic_indices[address]) == expected


@pytest.mark.parametrize("bank_id", sorted({index for index, _ in EXPECTED_BANK_TILE_SHA256}))
def test_representative_bank_tiles(canonical_bytes: bytes, bank_id: int) -> None:
    bank = canon.read_banks(canon.Rom(canonical_bytes))[bank_id]
    expected = {
        tile_id: value
        for (index, tile_id), value in EXPECTED_BANK_TILE_SHA256.items()
        if index == bank_id
    }
    for tile_id, value in expected.items():
        start = tile_id * canon.BANK_TILE_BYTES
        assert digest(bank.payload[start : start + canon.BANK_TILE_BYTES]) == value


@pytest.mark.parametrize("bank_id", sorted(EXPECTED_BANK_SHEET_SHA256))
def test_representative_bank_sheet(canonical_bytes: bytes, bank_id: int) -> None:
    bank = canon.read_banks(canon.Rom(canonical_bytes))[bank_id]
    tiles = tuple(
        bank.payload[index * canon.BANK_TILE_BYTES : (index + 1) * canon.BANK_TILE_BYTES]
        for index in range(bank.tile_count)
    )
    width, height, sheet = render.tile_sheet(tiles, export.BANK_SHEET_COLUMNS)
    assert (width, height) == (128, 128)
    assert digest(sheet) == EXPECTED_BANK_SHEET_SHA256[bank_id]


def test_multipart_frame_assembly(exporter: export.Exporter) -> None:
    frame = exporter.frames[FOUR_PIECE_FRAME]
    assert frame.piece_count == 4
    assert (frame.width, frame.height) == (96, 96)
    assert (frame.min_x, frame.min_y) == (0, -80)
    assert [(p.x, p.y, p.dim_0, p.dim_1) for p in frame.pieces] == [
        (0, -80, 64, 64),
        (64, -80, 32, 64),
        (0, -16, 64, 32),
        (64, -16, 32, 32),
    ]
    assert digest(exporter.assemble(frame)) == EXPECTED_FOUR_PIECE_SHA256


def test_the_other_multipart_frame_shape_assembles(exporter: export.Exporter) -> None:
    frame = exporter.frames[TWO_PIECE_FRAME]
    assert frame.piece_count == 2
    assert (frame.width, frame.height) == (32, 48)
    assert digest(exporter.assemble(frame)) == EXPECTED_TWO_PIECE_SHA256


def test_every_multipart_frame_assembles(exporter: export.Exporter) -> None:
    assembled = 0
    for address, frame in exporter.frames.items():
        if frame.piece_count == 1:
            continue
        pixels = exporter.assemble(frame)
        assert len(pixels) == frame.width * frame.height, hex(address)
        assembled += 1
    assert assembled == EXPECTED_MULTIPART_FRAMES


def test_all_frames_assemble_into_their_own_bounding_box(
    exporter: export.Exporter,
) -> None:
    for frame in exporter.frames.values():
        pixels = exporter.assemble(frame)
        assert len(pixels) == frame.width * frame.height


def test_representative_single_piece_sprite_frame(exporter: export.Exporter) -> None:
    definition = exporter.definitions[0]
    assert definition.sprite_id == EXPECTED_SPRITE_ID_FLOOR
    animation = exporter.animations[definition.animation_pointers[0]]
    address = animation.cell_address(0, 0)
    assert address == EXPECTED_FIRST_SPRITE_FRAME
    frame = exporter.frames[address]
    assert (frame.width, frame.height) == (32, 32)
    assert digest(exporter.assemble(frame)) == EXPECTED_FIRST_SPRITE_SHA256


def test_directional_images_count_matches_the_accepted_arithmetic(
    exporter: export.Exporter,
) -> None:
    directional = 0
    pieces = 0
    for definition in exporter.definitions:
        for pointer in definition.animation_pointers:
            if pointer == 0:
                continue
            animation = exporter.animations[pointer]
            directional += animation.direction_cells
            pieces += sum(
                exporter.frames[address].piece_count
                for address in animation.cell_addresses
            )
    assert directional == EXPECTED_DIRECTIONAL_FRAME_IMAGES
    assert pieces == EXPECTED_PIECE_REFERENCES_OVER_ANIMATION_REFERENCES


def test_palettes_match_their_sources(canonical_bytes: bytes) -> None:
    rom = canon.Rom(canonical_bytes)
    flattened = bytes(
        channel for colour in render.bg_palette_rgb(rom) for channel in colour
    )
    assert digest(flattened) == EXPECTED_BG_PALETTE_SHA256
    flattened = bytes(
        channel for colour in render.object_palette_rgb(rom) for channel in colour
    )
    assert digest(flattened) == EXPECTED_OBJECT_PALETTE_SHA256


# --- determinism -------------------------------------------------------------

def test_the_written_tree_gives_every_map_a_directory_and_a_record(
    exporter: export.Exporter, tmp_path_factory
) -> None:
    """The export writes a directory and a `map.json` for all 452 maps.

    This runs the map side with the writer enabled, which is the only way to
    check the on-disk consequence rather than the inventory it came from. It is
    the regression that a fully unrenderable map once slipped past: map 8 renders
    nothing, so nothing created its directory and the library held 451 map
    directories for 452 identities.
    """
    root = tmp_path_factory.mktemp("asset-export-written")
    written = export.Exporter(canon.Rom(exporter.rom.data), root / "out", root / "audit")
    written.subsystems = {"maps"}
    written.collect_names()
    written.layers = exporter.layers
    written.char_blocks = exporter.char_blocks
    written.selector_counts = exporter.selector_counts
    written.animated_counts = exporter.animated_counts
    written.chunk_entries = exporter.chunk_entries
    written.chunk_maps = exporter.chunk_maps
    written.screenblock_entries = exporter.screenblock_entries
    written.export_maps()

    maps_root = root / "out" / naming.MAPS
    directories = sorted(entry.name for entry in maps_root.iterdir())
    assert len(directories) == EXPECTED_MAP_DIRECTORIES
    assert directories == sorted(
        naming.map_directory(entry.index, written.map_name(entry.index))
        for entry in written.map_entries
    )
    for directory in directories:
        records = list((maps_root / directory).glob(f"{naming.MAP_RECORD_FILE}"))
        assert len(records) == 1, directory
    assert written.counters["map_directories_written"] == EXPECTED_MAP_DIRECTORIES
    assert {
        gate["key"]: gate["accounted"]
        for gate in written.count_document()["gates"]
    } == {
        "map_entries": True,
        "maps_exported": True,
        "map_directories_written": True,
        "map_layers_classified": True,
    }


def test_every_composite_on_disk_is_the_backdrop_flattened_view(
    exporter: export.Exporter, tmp_path_factory
) -> None:
    """A composite file is opaque and equals its index image against the backdrop."""
    root = tmp_path_factory.mktemp("asset-export-composite")
    written = export.Exporter(canon.Rom(exporter.rom.data), root / "out", root / "audit")
    written.subsystems = {"maps"}
    written.collect_names()
    written.layers = exporter.layers
    written.char_blocks = exporter.char_blocks
    written.selector_counts = exporter.selector_counts
    written.animated_counts = exporter.animated_counts
    written.chunk_entries = exporter.chunk_entries
    written.chunk_maps = exporter.chunk_maps
    written.screenblock_entries = exporter.screenblock_entries
    written.export_maps()

    checked = 0
    for map_index in (0, 39, 40, 125):
        records = exporter.layers[map_index]
        rendered = [
            (
                exporter.rom.u8(
                    exporter.map_entries[map_index].root_address
                    + canon.ROOT_BG_ADDEND_OFFSET
                    + layer.slot
                ),
                layer.slot,
                layer.chunk_x * canon.CHUNK_PIXELS,
                layer.chunk_y * canon.CHUNK_PIXELS,
                exporter.render_layer(layer, map_index),
            )
            for layer in records
            if layer.classification == "dominant"
        ]
        width = max(item[2] for item in rendered)
        height = max(item[3] for item in rendered)
        indices = render.compose_layers(rendered, width, height)
        table = render.rgba_table(render.bg_palette_rgb(exporter.rom))
        expected = render.to_rgba(indices, table, backdrop=(0, 0, 0))
        name = written.map_name(map_index)
        path = (
            root / "out" / naming.MAPS / naming.map_directory(map_index, name)
            / naming.COMPOSITE_FILE
        )
        got_width, got_height, got = png.decode_rgba(path.read_bytes())
        assert (got_width, got_height) == (width, height)
        assert got == expected
        assert set(got[3::4]) == {255}
        checked += 1
    assert checked == 4


def test_rendering_the_same_structures_twice_is_byte_identical(
    exporter: export.Exporter,
) -> None:
    for map_index in (0, 19, 39, 40, 125):
        for layer in exporter.layers[map_index]:
            if layer.classification != "dominant":
                continue
            first = exporter.render_layer(layer, map_index)
            second = exporter.render_layer(layer, map_index)
            assert first == second
    for address in sorted(EXPECTED_CHUNK_SHA256):
        map_index = min(
            index
            for index in set(exporter.chunk_maps[address])
            if index in exporter.char_blocks
        )
        entries = exporter.chunk_entries[address]
        char_data = exporter.char_blocks[map_index].data
        assert render.render_chunk(entries, char_data) == render.render_chunk(
            entries, char_data
        )


def test_png_output_is_byte_identical_across_encodes(
    exporter: export.Exporter,
) -> None:

    table = render.rgba_table(render.bg_palette_rgb(exporter.rom))
    for map_index in (0, 39):
        for layer in exporter.layers[map_index]:
            if layer.classification != "dominant":
                continue
            width = layer.chunk_x * canon.CHUNK_PIXELS
            height = layer.chunk_y * canon.CHUNK_PIXELS
            rgba = render.to_rgba(exporter.render_layer(layer, map_index), table)
            first = png.encode_rgba(width, height, rgba)
            second = png.encode_rgba(width, height, rgba)
            assert first == second
            assert png.decode_rgba(first)[2] == rgba
