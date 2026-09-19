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
import json
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
#: Screen-entry handlers. Both deliver a 0x800-byte container holding 1024
#: little-endian screen entries, but they name it from different record fields
#: and reach it by different code, so the field offset is pinned per handler.
#: `0x08007B63`'s constructor decompresses `record + 0x04` into the object's own
#: buffer; `0x0800897B`'s constructor builds a bare marker object and its type's
#: method 1 (`0x080088E6`) uploads `record + 0x1C` to the background screen base.
EXPECTED_SCREENBLOCK_LAYER_HANDLER = 0x08007B63
EXPECTED_UPLOADED_SCREENBLOCK_HANDLER = 0x0800897B
EXPECTED_SCREENBLOCK_CONTAINER_OFFSETS = {
    EXPECTED_SCREENBLOCK_LAYER_HANDLER: 0x04,
    EXPECTED_UPLOADED_SCREENBLOCK_HANDLER: 0x1C,
}
#: Handler `0x080088BD` carries one record whose container geometry
#: ASSET-EXPORT-MAP19-001 recovered: 140 containers of 0x400 decoded bytes laid
#: out as a 14 x 10 cell grid of 32x32 one-byte-per-pixel cells.
EXPECTED_TERRAIN_FIELD_LAYER_HANDLER = 0x080088BD
#: `0x08007B63`'s constructor decompresses the same plane into a second 0x800-byte
#: object buffer from this field. The exporter reads `+0x04`; the two agree on the
#: one canonical record of that handler, which is what makes the plane unambiguous.
SCREENBLOCK_SECOND_BUFFER_OFFSET = 0x08
EXPECTED_NON_DOMINANT_HANDLERS = (
    EXPECTED_UPLOADED_SCREENBLOCK_HANDLER,
    EXPECTED_SCREENBLOCK_LAYER_HANDLER,
    EXPECTED_TERRAIN_FIELD_LAYER_HANDLER,
)

#: Layer `+0x00` handler census over the 1,808 references. Five values, exact.
EXPECTED_HANDLER_CENSUS = {
    0x08008087: 1516,
    0x0800897B: 41,
    0x08007A41: 249,
    0x08007B63: 1,
    0x080088BD: 1,
}

#: Classification over the same references. Every reference carries a final
#: class: nothing is left `unclassified_handler`.
EXPECTED_CLASS_CENSUS = {
    "dominant": 1516,
    "absent_placeholder": 249,
    "static_graphical_screenblock": 42,
    "static_graphical_terrain_field": 1,
}

#: The 43 references that were unresolved before ASSET-EXPORT-MAP-HANDLERS-001,
#: by final class.
EXPECTED_SCREENBLOCK_REFERENCES = 42
EXPECTED_TERRAIN_FIELD_REFERENCES = 1
EXPECTED_UNRESOLVED_REFERENCES_AFTER = 0

#: Rendered map layers and composites. Every non-absent layer renders, so no
#: composite is withheld.
EXPECTED_MAP_LAYERS_RENDERED = 1559
EXPECTED_MAP_COMPOSITES = 452
EXPECTED_MAP_COMPOSITES_WITHHELD = 0

#: The per-layer status the exporter records. Every reference carries exactly one,
#: and the class set is closed: no layer is left without a rendered image or a
#: named structural reason.
EXPECTED_LAYER_STATUS_CENSUS = {
    "rendered": 1559,
    "not_graphical_absent_layer": 249,
}

#: Map 19's `0x08007B63` layer, the one screen-entry layer that was already
#: classified before ASSET-EXPORT-MAP-HANDLERS-001.
EXPECTED_SCREENBLOCK_MAP = 19
EXPECTED_SCREENBLOCK_SLOT = 1
EXPECTED_SCREENBLOCK_DIMENSIONS = (256, 256)
EXPECTED_SCREENBLOCK_MAX_ORDINAL = 538
EXPECTED_TERRAIN_FIELD_MAP = 19
EXPECTED_TERRAIN_FIELD_SLOT = 2
EXPECTED_TERRAIN_FIELD_GRID = (14, 10)
EXPECTED_TERRAIN_FIELD_CONTAINERS = 140
EXPECTED_TERRAIN_FIELD_CELL_BYTES = 1024
EXPECTED_TERRAIN_FIELD_CELL_PIXELS = 32
EXPECTED_TERRAIN_FIELD_DIMENSIONS = (448, 320)
EXPECTED_WITHHELD_COMPOSITES: dict[int, str] = {}

#: Maps whose layers include an uploaded screen-entry plane, and the one map
#: whose four slots are all uploaded planes. All 29 carry a composite.
EXPECTED_UPLOADED_SCREENBLOCK_MAP = 8
EXPECTED_UPLOADED_SCREENBLOCK_MAPS = 29
EXPECTED_SCREENBLOCK_MAPS = 30
EXPECTED_UPLOADED_SCREENBLOCK_REFERENCES = 41

#: Representative pixel digests for the screen-entry planes and for composites
#: that contain them, measured once from the corrected classification and pinned.
#: The map 19 digest is the self-buffered `0x08007B63` plane; the rest are
#: `0x0800897B` planes uploaded from `record + 0x1C`.
EXPECTED_SCREENBLOCK_SHA256 = (
    "a9e283ba2fa92ff9661a80cd51fe777021a7a41bb72dbe88b0ba6b7c334d914a"
)
EXPECTED_UPLOADED_SCREENBLOCK_SHA256 = {
    (7, 3): "af95115b48108dbe8355ebb462d34c3cfe334cf63b8c2b8ba9b49bdb4d4d144f",
    (8, 0): "b94d4994fe45a052971868b5be695882672b0eeed3f043c98d081a356aa74372",
    (8, 1): "0f963f1b3c3af941c17fdb6e5bce6b78ae3a5518a7387c7e3cf06c7d79eb3d59",
    (8, 2): "f4ee401463352c6a2994ad411696f9b74e2769da68486dc8083a0c8741ca79a4",
    (8, 3): "63d4131228c6ee8f3d6f77f7ba6a4c3c62e2016cab37fe2af7e1abbebedc0382",
    (20, 3): "6c03e2ee1ce01fe369d8fc40cd268a674f9b2045e8a7b2177562bfdce6eeeea8",
    (390, 3): "3610094b699c1bb83d624a93c373e8e8802dab401850758f9704c8a7766aea4b",
}
EXPECTED_SCREENBLOCK_COMPOSITE_SHA256 = {
    7: "2a72e45888f99a620870fd64e02e28e559fab24e08d56e78710eccebfe60f55e",
    8: "137705240c04ed86fa9a63305eeabe324fdbd6d7c8be247197507a998c71ce90",
    14: "cae11e6743e27d36dbe54318045f9769c52d58ce2f7fb990a5a623c981bc4ff7",
    17: "b716ca1665e8427f6232b6820ba5af47ed946540970506162fb0f073dfd462fb",
    22: "b1e677ac13601e2f661673bfd10b80f001a2c16597d2b44da9028933804d2c83",
    390: "9956105585618937cea2ff3efe7807eab65b4f93dd43b9791a944c2b47750292",
}
EXPECTED_SCREENBLOCK_COMPOSITE_SIZE = {
    7: (256, 256),
    8: (256, 256),
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
    19: "deb8fec4fe627b78f8feaeed8a9d69759eaf967b2195bf240d5c288a73a2d170",
    39: "35d3b51f0929a9d1d408786b651b314f1458028f4a5d9ae1440d8ba78388ed2b",
    40: "21985e5c58150499b13c29696cabadd84956708e7f901b2b6ceb2c9bd6c70f9d",
    125: "718fdc0c8c44f340ec1ee5b16186067a6cdbf64b6a8519d925b353368ad15cbf",
}

EXPECTED_MAP_COMPOSITE_SIZE = {
    0: (1280, 256),
    19: (448, 320),
    39: (1024, 512),
    40: (512, 512),
    125: (256, 512),
}

#: Map 19's recovered terrain field, pinned by pixel digest and size. It is the
#: only record of its handler, so this is the whole population of that form.
EXPECTED_TERRAIN_FIELD_SHA256 = (
    "883f6db20c3b908eb61e7d7bcd0c16fade994e184e95c8d3118d85cbbc4976ec"
)

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


def test_a_map_whose_layers_are_all_screen_planes_still_gets_a_directory(
    exporter: export.Exporter,
) -> None:
    """Map 8's four slots are all uploaded screen-entry planes.

    The map has no resolved name, so its identity is the numeric `map_008`
    directory - written from its own record, not from a rendered image.
    """
    assert [layer.classification for layer in exporter.layers[8]] == [
        "static_graphical_screenblock"
    ] * 4
    assert [layer.handler for layer in exporter.layers[8]] == [
        EXPECTED_UPLOADED_SCREENBLOCK_HANDLER
    ] * 4
    assert exporter.map_name(8) is None
    assert naming.map_directory(8, None) == "map_008"
    assert naming.map_directory(
        EXPECTED_UPLOADED_SCREENBLOCK_MAP,
        exporter.map_name(EXPECTED_UPLOADED_SCREENBLOCK_MAP),
    ) == "map_008"


# --- ASSET-EXPORT-MAP-HANDLERS-001: the 43 non-dominant references ------------

def test_all_43_non_dominant_references_have_a_final_class(
    exporter: export.Exporter,
) -> None:
    """Zero remaining unresolved references, and no unknown handler anywhere."""
    counted = {"static_graphical_screenblock": 0,
               "static_graphical_terrain_field": 0}
    for records in exporter.layers.values():
        for layer in records:
            assert layer.classification != "unclassified_handler"
            if layer.classification in counted:
                counted[layer.classification] += 1
    assert counted["static_graphical_screenblock"] == EXPECTED_SCREENBLOCK_REFERENCES
    assert counted["static_graphical_terrain_field"] == (
        EXPECTED_TERRAIN_FIELD_REFERENCES
    )
    assert sum(counted.values()) == 43
    reachable = {
        "dominant",
        "absent_placeholder",
        "static_graphical_screenblock",
        "static_graphical_terrain_field",
    }
    unreached = {
        layer.classification
        for records in exporter.layers.values()
        for layer in records
        if layer.classification not in reachable
    }
    assert unreached == set(), sorted(unreached)


def test_screen_entry_slots_render_and_nothing_withholds_a_composite(
    exporter: export.Exporter,
) -> None:
    """A slot's class decides both whether it paints and whether it withholds.

    `absent_placeholder` is the one class established as drawing nothing, so it
    neither paints nor blocks. The dominant, screen-entry and terrain-field
    classes all paint and all render, so after ASSET-EXPORT-MAP19-001 no slot
    withholds a composite.
    """
    for records in exporter.layers.values():
        for layer in records:
            if layer.classification == "absent_placeholder":
                assert layer.graphical is False
                assert layer.blocks_composite is False
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


@pytest.mark.parametrize(
    "map_index", sorted(EXPECTED_SCREENBLOCK_COMPOSITE_SHA256)
)
def test_composites_containing_screen_entry_planes_render_deterministically(
    exporter: export.Exporter, map_index: int
) -> None:
    """Every layer of these maps is rendered and none withholds a composite.

    Rebuilding the composite here from the classified layers must reproduce the
    pinned index plane, so the plane has to be re-assembled from the record's own
    container field rather than carried over from a stored image.
    """
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
    assert (width, height) == EXPECTED_SCREENBLOCK_COMPOSITE_SIZE[map_index]
    composite = render.compose_layers(rendered, width, height)
    assert digest(composite) == EXPECTED_SCREENBLOCK_COMPOSITE_SHA256[map_index]


@pytest.mark.parametrize(
    "map_index,slot", sorted(EXPECTED_UPLOADED_SCREENBLOCK_SHA256)
)
def test_uploaded_screen_entry_planes_render_from_record_plus_0x1c(
    exporter: export.Exporter, map_index: int, slot: int
) -> None:
    """Handler `0x0800897B` builds only a marker object in its constructor.

    Its type's method 1 uploads `record + 0x1C` to `0x0600E000 + slot * 0x800`,
    so the plane's own field is `+0x1C`, not `+0x04`. Rendered through the
    existing screen-entry renderer it must reproduce the pinned plane.
    """
    layer = exporter.layers[map_index][slot]
    assert layer.handler == EXPECTED_UPLOADED_SCREENBLOCK_HANDLER
    assert layer.classification == "static_graphical_screenblock"
    assert canon.screenblock_container_offset(layer.handler) == 0x1C
    entries = canon.read_screenblock_entries(exporter.rom, layer.address)
    assert entries == exporter.screenblock_entries[layer.address]
    assert len(entries) == canon.SCREENBLOCK_ENTRY_COUNT
    assert all(word & canon.TILE_ENTRY_HIGH_NIBBLE == 0 for word in entries)
    pixels = render.render_chunk(
        entries, exporter.char_blocks[map_index].data
    )
    assert len(pixels) == canon.SCREENBLOCK_PIXELS * canon.SCREENBLOCK_PIXELS
    assert digest(pixels) == EXPECTED_UPLOADED_SCREENBLOCK_SHA256[(map_index, slot)]


def test_every_screen_entry_plane_resolves_inside_its_own_maps_char_block(
    exporter: export.Exporter,
) -> None:
    """The structural check that makes a plane renderable at all, over all 42.

    Every one of the 42 screen-entry layers - the 41 uploaded ones and map 19's
    self-buffered one - must carry exactly 1024 entries whose tile ordinals all
    resolve inside the map's own assembled character block, so rendering cannot
    be reading a foreign map's tiles.
    """
    maps = 0
    layers = 0
    for map_index, records in exporter.layers.items():
        block = exporter.char_blocks[map_index]
        touched = False
        for layer in records:
            if layer.classification != "static_graphical_screenblock":
                continue
            layers += 1
            touched = True
            entries = canon.read_screenblock_entries(exporter.rom, layer.address)
            assert len(entries) == canon.SCREENBLOCK_ENTRY_COUNT
            assert all(word & canon.TILE_ENTRY_HIGH_NIBBLE == 0 for word in entries)
            highest = max(word & canon.TILE_ENTRY_ORDINAL_MASK for word in entries)
            assert highest < block.tile_count
        maps += 1 if touched else 0
    assert layers == EXPECTED_SCREENBLOCK_REFERENCES
    assert maps == EXPECTED_SCREENBLOCK_MAPS


def test_the_screen_entry_container_field_is_read_from_the_records_own_handler(
    exporter: export.Exporter,
) -> None:
    """The two screen-entry handlers name their container from different fields.

    The reader takes the field from the record's own `+0x00` handler word, so a
    `0x0800897B` record cannot be read at `+0x04` and vice versa. `0x08007B63`'s
    constructor also fills `record + 0x08`; on the one canonical record of that
    handler the two fields name the same container.
    """
    assert canon.SCREENBLOCK_HANDLERS == EXPECTED_SCREENBLOCK_CONTAINER_OFFSETS
    for handler, offset in EXPECTED_SCREENBLOCK_CONTAINER_OFFSETS.items():
        assert canon.screenblock_container_offset(handler) == offset
    self_buffered = exporter.layers[EXPECTED_SCREENBLOCK_MAP][
        EXPECTED_SCREENBLOCK_SLOT
    ]
    assert self_buffered.handler == EXPECTED_SCREENBLOCK_LAYER_HANDLER
    assert exporter.rom.u32(
        self_buffered.address + SCREENBLOCK_SECOND_BUFFER_OFFSET
    ) == exporter.rom.u32(self_buffered.address + 0x04)
    uploaded = [
        layer
        for records in exporter.layers.values()
        for layer in records
        if layer.handler == EXPECTED_UPLOADED_SCREENBLOCK_HANDLER
    ]
    assert len(uploaded) == EXPECTED_UPLOADED_SCREENBLOCK_REFERENCES
    for layer in uploaded:
        assert exporter.rom.u32(layer.address + 0x1C) != 0
        container = exporter.rom.container(exporter.rom.u32(layer.address + 0x1C))
        assert container.declared_size == canon.SCREENBLOCK_DECODED_BYTES


def test_the_terrain_field_record_is_read_structurally(
    exporter: export.Exporter,
) -> None:
    """Handler `0x080088BD` streams a grid of 0x400-byte containers.

    The grid product equals the number of container pointers the record carries,
    and each container decodes to exactly the cell size the renderer consumes.
    """
    layer = exporter.layers[EXPECTED_TERRAIN_FIELD_MAP][
        EXPECTED_TERRAIN_FIELD_SLOT
    ]
    assert layer.handler == EXPECTED_TERRAIN_FIELD_LAYER_HANDLER
    assert layer.classification == "static_graphical_terrain_field"
    probe = canon.read_terrain_field_probe(exporter.rom, layer.address)
    assert (probe["grid_x"], probe["grid_y"]) == EXPECTED_TERRAIN_FIELD_GRID
    assert probe["chunk_targets"] == EXPECTED_TERRAIN_FIELD_CONTAINERS
    assert probe["grid_product"] == EXPECTED_TERRAIN_FIELD_CONTAINERS
    assert probe["chunk_decoded_bytes"] == EXPECTED_TERRAIN_FIELD_CELL_BYTES
    assert probe["cell_pixels"] == EXPECTED_TERRAIN_FIELD_CELL_PIXELS
    assert probe["resident_slots"] == canon.TERRAIN_FIELD_RESIDENT_SLOTS
    # The grid the record states at its own `+0x04`/`+0x05` is the cell grid; the
    # dominant form's `+0x14`/`+0x15` hold unrelated bytes on this record, so they
    # are not the grid and are not published as one.
    assert (layer.terrain_grid_x, layer.terrain_grid_y) == (
        EXPECTED_TERRAIN_FIELD_GRID
    )
    assert layer.terrain_cells == EXPECTED_TERRAIN_FIELD_CONTAINERS


def test_the_terrain_field_containers_decode_at_their_declared_size(
    exporter: export.Exporter,
) -> None:
    layer = exporter.layers[EXPECTED_TERRAIN_FIELD_MAP][
        EXPECTED_TERRAIN_FIELD_SLOT
    ]
    for index in range(EXPECTED_TERRAIN_FIELD_CONTAINERS):
        address = exporter.rom.u32(
            layer.address + canon.TERRAIN_FIELD_CONTAINER_OFFSET + 4 * index
        )
        container = exporter.rom.container(address)
        assert container.declared_size == EXPECTED_TERRAIN_FIELD_CELL_BYTES


def test_the_terrain_field_renders_from_its_own_containers(
    exporter: export.Exporter,
) -> None:
    """The recovered geometry renders one 448x320 image from the 140 containers.

    Container `y * grid_x + x` supplies the 32x32 cell at `(x * 32, y * 32)`;
    every container is one byte per pixel with 32 bytes per raster row, and no
    ordinal is involved, so the map's character block plays no part.
    """
    layer = exporter.layers[EXPECTED_TERRAIN_FIELD_MAP][
        EXPECTED_TERRAIN_FIELD_SLOT
    ]
    containers = exporter.terrain_field_containers[layer.address]
    assert len(containers) == EXPECTED_TERRAIN_FIELD_CONTAINERS
    width, height, pixels = render.render_terrain_field(
        containers, layer.terrain_grid_x, layer.terrain_grid_y
    )
    assert (width, height) == EXPECTED_TERRAIN_FIELD_DIMENSIONS
    assert len(pixels) == width * height
    # Every cell is placed at its own raster position: check one byte of the
    # first cell against the container it came from, and one byte of the last.
    cell = canon.TERRAIN_FIELD_CELL_PIXELS
    row_bytes = canon.TERRAIN_FIELD_CELL_BYTES // cell
    assert pixels[0] == containers[0][0]
    assert pixels[cell - 1] == containers[0][row_bytes - 1]
    last = len(containers) - 1
    at_x = (last % layer.terrain_grid_x) * cell
    at_y = (last // layer.terrain_grid_x) * cell
    assert pixels[at_y * width + at_x] == containers[last][0]


def test_no_composite_is_withheld_after_the_terrain_field_renders(
    exporter: export.Exporter,
) -> None:
    """No slot blocks a composite, so every map produces one.

    The composite gate is reproduced here - "no blocking layer and at least one
    renderable layer" - so the counts are measured, not restated.
    """
    blocking = {
        map_index
        for map_index, records in exporter.layers.items()
        if any(layer.blocks_composite for layer in records)
    }
    assert blocking == set()
    assert EXPECTED_WITHHELD_COMPOSITES == {}
    producing = sum(
        1
        for records in exporter.layers.values()
        if not any(layer.blocks_composite for layer in records)
        and any(layer.renderable for layer in records)
    )
    assert producing == EXPECTED_MAP_COMPOSITES
    assert len(exporter.layers) - producing == EXPECTED_MAP_COMPOSITES_WITHHELD
    uploaded_maps = {
        map_index
        for map_index, records in exporter.layers.items()
        if any(
            layer.handler == EXPECTED_UPLOADED_SCREENBLOCK_HANDLER
            for layer in records
        )
    }
    assert len(uploaded_maps) == EXPECTED_UPLOADED_SCREENBLOCK_MAPS
    assert EXPECTED_UPLOADED_SCREENBLOCK_MAP in uploaded_maps
    for map_index in sorted(uploaded_maps):
        assert not any(
            layer.blocks_composite for layer in exporter.layers[map_index]
        )


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
        layer.classification
        in (
            "dominant",
            "absent_placeholder",
            "static_graphical_screenblock",
            "static_graphical_terrain_field",
        )
        for layer in records
    )
    composed_forms = (
        "dominant",
        "static_graphical_screenblock",
        "static_graphical_terrain_field",
    )
    rendered = [
        (
            exporter.rom.u8(
                exporter.map_entries[map_index].root_address
                + canon.ROOT_BG_ADDEND_OFFSET
                + layer.slot
            ),
            layer.slot,
            *(
                (canon.SCREENBLOCK_PIXELS, canon.SCREENBLOCK_PIXELS)
                if layer.classification == "static_graphical_screenblock"
                else (
                    canon.TERRAIN_FIELD_CELL_PIXELS * layer.terrain_grid_x,
                    canon.TERRAIN_FIELD_CELL_PIXELS * layer.terrain_grid_y,
                )
                if layer.classification == "static_graphical_terrain_field"
                else (
                    layer.chunk_x * canon.CHUNK_PIXELS,
                    layer.chunk_y * canon.CHUNK_PIXELS,
                )
            ),
            exporter.render_layer(layer, map_index),
        )
        for layer in records
        if layer.classification in composed_forms
    ]
    width = max(item[2] for item in rendered)
    height = max(item[3] for item in rendered)
    assert (width, height) == EXPECTED_MAP_COMPOSITE_SIZE[map_index]
    composite = render.compose_layers(rendered, width, height)
    assert digest(composite) == EXPECTED_MAP_COMPOSITE_SHA256[map_index]


def test_the_terrain_field_layer_pixels_are_pinned(exporter: export.Exporter) -> None:
    """Map 19's recovered layer, pinned by pixel digest and native size."""
    layer = exporter.layers[EXPECTED_TERRAIN_FIELD_MAP][
        EXPECTED_TERRAIN_FIELD_SLOT
    ]
    pixels = exporter.render_layer(layer, EXPECTED_TERRAIN_FIELD_MAP)
    assert len(pixels) == (
        EXPECTED_TERRAIN_FIELD_DIMENSIONS[0] * EXPECTED_TERRAIN_FIELD_DIMENSIONS[1]
    )
    assert digest(pixels) == EXPECTED_TERRAIN_FIELD_SHA256


def test_map_19_composite_is_produced_from_all_its_renderable_layers(
    exporter: export.Exporter,
) -> None:
    """Map 19's four slots carry one class each, and none of them blocks.

    Its slot 2 is the terrain field ASSET-EXPORT-MAP19-001 recovered, so the map
    that was withheld in the previous revision now composes.
    """
    classes = [layer.classification for layer in exporter.layers[19]]
    assert classes == [
        "dominant",
        "static_graphical_screenblock",
        "static_graphical_terrain_field",
        "absent_placeholder",
    ]
    assert [layer.blocks_composite for layer in exporter.layers[19]] == [
        False, False, False, False,
    ]
    withheld = {
        map_index
        for map_index, records in exporter.layers.items()
        if any(layer.blocks_composite for layer in records)
        or not any(layer.renderable for layer in records)
    }
    assert withheld == set(EXPECTED_WITHHELD_COMPOSITES)


def test_a_layer_document_names_the_chunk_grid_only_for_the_dominant_form(
    exporter: export.Exporter, tmp_path_factory
) -> None:
    """`record + 0x14`/`+0x15` are the chunk grid only on the dominant form.

    A non-dominant record must not publish those bytes under the dominant form's
    field names: on `0x0800897B` they are the low halfword of the s32 scale the
    object's method 2 reads, which would otherwise appear as a chunk extent (map
    7 slot 3 reads 171 x 242 = 41382 cells for a single 256x256 plane).
    """
    root = tmp_path_factory.mktemp("asset-export-fields")
    written = export.Exporter(
        canon.Rom(exporter.rom.data), root / "out", root / "audit"
    )
    written.subsystems = {"maps"}
    written.collect_names()
    written.layers = exporter.layers
    written.char_blocks = exporter.char_blocks
    written.selector_counts = exporter.selector_counts
    written.animated_counts = exporter.animated_counts
    written.chunk_entries = exporter.chunk_entries
    written.chunk_maps = exporter.chunk_maps
    written.screenblock_entries = exporter.screenblock_entries
    written.terrain_field_containers = exporter.terrain_field_containers
    written.export_maps()

    grid_keys = {
        "chunk_x", "chunk_y", "chunk_cells", "null_chunk_cells",
        "non_null_chunk_cells",
    }
    seen = {"dominant": 0, "screenblock": 0, "terrain": 0, "absent": 0}
    for entry in written.map_entries:
        path = (
            root / "out" / naming.MAPS
            / naming.map_directory(entry.index, written.map_name(entry.index))
            / naming.MAP_RECORD_FILE
        )
        document = json.loads(path.read_text(encoding="utf-8"))
        for layer in document["layers"]:
            keys = set(layer)
            if layer["classification"] == "dominant":
                assert {"chunk_x", "chunk_y", "chunk_cells",
                        "null_chunk_cells"} <= keys
                seen["dominant"] += 1
            elif layer["classification"] == "static_graphical_screenblock":
                assert not (grid_keys & keys), sorted(grid_keys & keys)
                assert layer["width"] == 256 and layer["height"] == 256
                seen["screenblock"] += 1
            elif layer["classification"] == "static_graphical_terrain_field":
                # The terrain field states its grid at its own record offsets and
                # publishes it under its own names; the dominant grid keys stay
                # off it because `+0x14`/`+0x15` are unrelated bytes on this form.
                assert not (grid_keys & keys), sorted(grid_keys & keys)
                assert layer["cell_grid_x"] == 14
                assert layer["cell_grid_y"] == 10
                assert layer["cell_grid_cells"] == 140
                assert layer["width"] == 448 and layer["height"] == 320
                seen["terrain"] += 1
            else:
                assert layer["classification"] == "absent_placeholder"
                assert not (grid_keys & keys), sorted(grid_keys & keys)
                seen["absent"] += 1
    assert seen == {
        "dominant": 1516,
        "screenblock": 42,
        "terrain": 1,
        "absent": 249,
    }


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
    written.terrain_field_containers = exporter.terrain_field_containers
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
    assert written.counters["map_layers_exported"] == EXPECTED_MAP_LAYERS_RENDERED
    assert written.counters["map_composites"] == EXPECTED_MAP_COMPOSITES
    assert written.counters["map_composites_withheld"] == (
        EXPECTED_MAP_COMPOSITES_WITHHELD
    )
    statuses = {
        key.removeprefix("map_layer_status_"): value
        for key, value in written.counters.items()
        if key.startswith("map_layer_status_")
    }
    assert statuses == EXPECTED_LAYER_STATUS_CENSUS
    assert sum(statuses.values()) == EXPECTED_LAYER_REFERENCES
    for entry in written.map_entries:
        directory = maps_root / naming.map_directory(entry.index, written.map_name(entry.index))
        has_composite = (directory / naming.COMPOSITE_FILE).is_file()
        assert has_composite is True, entry.index
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
    written.terrain_field_containers = exporter.terrain_field_containers
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
