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
from tools.export import render

# --- accepted populations ----------------------------------------------------

EXPECTED_MAP_ENTRIES = 452
EXPECTED_LAYER_REFERENCES = 1808
EXPECTED_DOMINANT_LAYER_HANDLER = 0x08008087
EXPECTED_ABSENT_LAYER_HANDLER = 0x08007A41
EXPECTED_UNRESOLVED_HANDLERS = (0x0800897B, 0x08007B63, 0x080088BD)

#: Layer `+0x00` handler census over the 1,808 references. Five values, exact.
EXPECTED_HANDLER_CENSUS = {
    0x08008087: 1516,
    0x0800897B: 41,
    0x08007A41: 249,
    0x08007B63: 1,
    0x080088BD: 1,
}

#: Classification over the same references.
EXPECTED_CLASS_CENSUS = {
    "dominant": 1516,
    "absent_placeholder": 249,
    "unresolved_record_representation": 41,
    "unresolved_handler": 2,
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
    analysis.collect_map_graph()
    analysis.collect_sprite_graph()
    return analysis


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
        *EXPECTED_UNRESOLVED_HANDLERS,
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


def test_map_19_composite_is_withheld_because_two_layers_are_unresolved(
    exporter: export.Exporter,
) -> None:
    """The unresolved handlers are withheld, never silently dropped."""
    classes = [layer.classification for layer in exporter.layers[19]]
    assert classes == [
        "dominant",
        "unresolved_handler",
        "unresolved_handler",
        "absent_placeholder",
    ]
    assert 19 not in EXPECTED_MAP_COMPOSITE_SHA256


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
    from tools.export import png

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
