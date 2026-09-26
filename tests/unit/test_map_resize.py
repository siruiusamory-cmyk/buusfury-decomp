"""`map_resize`: the production authority for map structure.

MAP-RESIZE-AND-LAYERS-001. Portable: every image here is synthetic, built in this
file, so nothing needs the commercial ROM. The canonical-image proof lives in
`tests/integration/test_map_resize_rom.py`.
"""

from __future__ import annotations

import hashlib
import struct

import pytest

from tools.webfoot import map_chunk as mc
from tools.webfoot import map_resize as mr
from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.formats import map_graphics as mg
from tools.webfoot.formats import webfoot_lz as lz
from tools.webfoot.formats.map_entry import MAP_ENTRY_SIZE
from tools.webfoot.packaged import packaged_profile
from tools.webfoot.profile import MapEntryTableProfile
from tools.webfoot.project.model import (
    AuthoredChunk,
    AuthoredChunkEntry,
    AuthoredLayer,
    LayerResize,
    LayoutEdits,
    MapStructure,
    ProjectValidationError,
)

GBA = 0x08000000
TABLE = 0x080A0000
COUNT = 4
IMAGE_SIZE = 0x00800000

ROOT = 0x08300000
LAYER = 0x08301000
SECOND_LAYER = 0x08302000
CHUNKS = (0x08310000, 0x08311000, 0x08312000)
#: A second dominant layer whose retail grid is **not square**: 1 column by 3 rows.
#: A square retail grid cannot tell a row stride from a column count, so this is
#: what makes the coordinate transform's stride observable.
NARROW_LAYER = 0x08308000
NARROW_COLUMNS = 1
NARROW_ROWS = 3

#: The retail extent words: extent (90, 186) stored as extent - 1.
EXTENT_X_RAW = 89
EXTENT_Y_RAW = 185

#: The marker a record's ``+0x04`` carries. The template slot uses its own value,
#: so "the emitted record's header is the TEMPLATE's, byte for byte" is a claim a
#: reader can check rather than one that holds because two records happen to agree.
LAYER_SCALAR = 0x00000400
TEMPLATE_SCALAR = 0x00000500


def _place(image: bytearray, address: int, data: bytes) -> None:
    offset = address - GBA
    image[offset:offset + len(data)] = data


def _dominant_record(address: int, columns: int, rows: int, cells, scalar: int = LAYER_SCALAR) -> bytes:
    """A dominant layer record: the 0x18-byte header plus its chunk window.

    The two grid bytes carry an unrelated value before being written, so a test
    that the record states the authored grid cannot pass by inheriting the old one.
    """
    record = bytearray(0x18 + 4 * columns * rows)
    struct.pack_into("<I", record, 0x00, mg.DOMINANT_LAYER_HANDLER)
    struct.pack_into("<I", record, 0x04, scalar)
    struct.pack_into("<I", record, 0x08, 0x00000400)
    struct.pack_into("<H", record, 0x16, 0x0000)
    record[0x14] = columns
    record[0x15] = rows
    for index, cell in enumerate(cells):
        struct.pack_into("<I", record, 0x18 + 4 * index, cell)
    return bytes(record)


def _stored_chunk(entry: int = 0x0015) -> bytes:
    return lz.build_stored(struct.pack("<1024H", *([entry] * 1024)))


def _build_image() -> bytes:
    image = bytearray(IMAGE_SIZE)
    # Every map entry must name a source word: `read_map_entries` dereferences all
    # of them, exactly as the canonical table's 452 non-null sources do. Entries 2
    # and 3 deliberately share one source, so a shared root is a real case.
    root_0 = 0x08304000
    layer_0 = 0x08305000
    source_0 = 0x08306000
    source_2 = 0x08320000
    source_3 = 0x08321000
    root_3 = 0x08307000
    for index, (source, root) in enumerate(
        ((source_0, root_0), (source_0, root_0), (source_2, ROOT), (source_3, root_3))
    ):
        _place(image, TABLE + (index * MAP_ENTRY_SIZE) + 0x2C, struct.pack("<I", source))
    _place(image, source_0, struct.pack("<I", root_0))
    _place(image, source_2, struct.pack("<I", ROOT))
    _place(image, source_3, struct.pack("<I", root_3))

    absent = mg.ABSENT_LAYER_RECORD
    _place(image, absent, struct.pack("<I", mg.ABSENT_LAYER_HANDLER))
    _place(
        image,
        root_0 + 0x14,
        struct.pack("<4I", layer_0, absent, absent, absent),
    )
    _place(image, root_0 + mg.ROOT_EXTENT_X_OFFSET, struct.pack("<H", EXTENT_X_RAW))
    _place(image, root_0 + mg.ROOT_EXTENT_Y_OFFSET, struct.pack("<H", EXTENT_Y_RAW))
    _place(image, root_3 + 0x14, struct.pack("<4I", NARROW_LAYER, absent, absent, absent))
    _place(image, root_3 + mg.ROOT_EXTENT_X_OFFSET, struct.pack("<H", EXTENT_X_RAW))
    _place(image, root_3 + mg.ROOT_EXTENT_Y_OFFSET, struct.pack("<H", EXTENT_Y_RAW))
    _place(
        image,
        ROOT + 0x14,
        struct.pack(
            "<4I",
            LAYER,
            absent,
            SECOND_LAYER,
            absent,
        ),
    )
    _place(image, ROOT + mg.ROOT_EXTENT_X_OFFSET, struct.pack("<H", EXTENT_X_RAW))
    _place(image, ROOT + mg.ROOT_EXTENT_Y_OFFSET, struct.pack("<H", EXTENT_Y_RAW))
    for index, chunk in enumerate(CHUNKS):
        _place(image, chunk, _stored_chunk(0x0010 + index))
    # slot 0 of the first root: a 1x1 grid, so a second slot is genuinely free.
    _place(
        image,
        layer_0,
        _dominant_record(layer_0, 1, 1, (CHUNKS[0],)),
    )
    # slot 0 of the third root: a 1-column by 3-row grid, whose stride a
    # square grid could not discriminate.
    _place(
        image,
        NARROW_LAYER,
        _dominant_record(NARROW_LAYER, NARROW_COLUMNS, NARROW_ROWS, CHUNKS),
    )
    # slot 0: a 2x2 grid using three distinct chunks and one repetition, so it has
    # a vocabulary to paint with and a null cell the reader must not mistake for a
    # chunk.
    _place(
        image,
        LAYER,
        _dominant_record(LAYER, 2, 2, (CHUNKS[0], CHUNKS[1], CHUNKS[2], CHUNKS[0])),
    )
    # slot 1: the same shape, used as the template for an authored layer. Its
    # header carries a marker of its own, so a test can tell the record an authored
    # layer's header was copied from.
    _place(
        image,
        SECOND_LAYER,
        _dominant_record(
            SECOND_LAYER,
            2,
            2,
            (CHUNKS[0], CHUNKS[1], CHUNKS[2], CHUNKS[0]),
            scalar=TEMPLATE_SCALAR,
        ),
    )
    return bytes(image)


def _profile(image: bytes):
    base = packaged_profile()
    fields = {
        field: getattr(base, field)
        for field in (
            "game", "region", "revision", "game_code", "size", "crc32", "md5",
            "sha1", "sources", "notes", "enemy_stats", "character_base_stats",
            "text_strings", "free_regions", "scripts", "placement_types",
            "actor_sprites", "generated_expansion",
        )
    }
    fields.update(
        id="synthetic_map_resize_profile",
        sha256=hashlib.sha256(image).hexdigest(),
        size=len(image),
        map_entries=MapEntryTableProfile(
            address=GbaRomAddress(TABLE), count=COUNT, record_size=MAP_ENTRY_SIZE
        ),
    )
    return type(base)(**fields)


@pytest.fixture()
def world():
    image = _build_image()
    profile = _profile(image)
    return image, profile, mr.MapResizer(image, profile=profile)


def _structure(*edits) -> MapStructure:
    resizes = {}
    layers = {}
    for edit in edits:
        if isinstance(edit, LayerResize):
            resizes[edit.key] = edit
        else:
            layers[edit.identity] = edit
    return MapStructure(resizes=resizes, layers=layers)


# --- the model a resize rests on ---------------------------------------------

def test_a_layer_record_is_exactly_header_plus_window(world):
    """Measured over the canonical corpus; restated here as the record's contract.

    Nothing follows the window, which is why a grid that grows needs the record
    relocated rather than extended in place.
    """
    image, profile, resizer = world
    assert mg.layer_record_size(1, 1) == 0x18 + 4
    assert mg.layer_record_size(4, 3) == 0x18 + 48
    layer = resizer.target(2).layer(0)
    reader = mg.MapGraphicsReader(image, profile)
    assert mg.layer_record_header(reader, mg.read_layer(reader, ROOT, 0)) == image[
        LAYER - GBA: LAYER - GBA + 0x18
    ]


def test_compose_layer_record_writes_the_grid_bytes_and_the_window():
    header = bytes(0x18)
    record = mg.compose_layer_record(header, 3, 1, (0x08310000, 0x08311000, 0x08312000))
    assert len(record) == 0x18 + 12
    assert record[mg.LAYER_CHUNK_X_OFFSET] == 3
    assert record[mg.LAYER_CHUNK_Y_OFFSET] == 1
    assert struct.unpack_from("<I", record, 0x18)[0] == 0x08310000
    assert struct.unpack_from("<I", record, 0x20)[0] == 0x08312000


@pytest.mark.parametrize(
    "columns,rows,window,match",
    [
        (0, 1, (), "outside the supported"),
        (1, 0, (1,), "outside the supported"),
        (mg.MAX_LAYER_GRID_SIDE + 1, 1, (1,) * 9, "outside the supported"),
        (2, 2, (1, 2), "holds 4 cells"),
        (1, 1, (0,), "names no chunk"),
    ],
)
def test_compose_layer_record_refuses_a_grid_it_cannot_express(columns, rows, window, match):
    with pytest.raises(mg.MapGraphicsError, match=match):
        mg.compose_layer_record(bytes(0x18), columns, rows, window)


def test_the_declared_extent_is_the_camera_maximum(world):
    """The engine's clamp maximum is ``extent - 1``, so a plane of P pixels is
    reachable exactly when the stored value is ``P - viewport``."""
    assert mg.declared_extent_raw(mg.CHUNK_PIXELS, mg.VIEWPORT_PIXELS_X) == 16
    assert mg.declared_extent_raw(3 * mg.CHUNK_PIXELS, mg.VIEWPORT_PIXELS_X) == 528
    assert mg.declared_extent_raw(1, mg.VIEWPORT_PIXELS_X) == 1


# --- what may be resized ------------------------------------------------------

def test_the_facade_reports_the_retail_geometry_and_a_free_slot(world):
    _image, _profile_, resizer = world
    target = resizer.target(2)
    assert target.extent_x == EXTENT_X_RAW + 1
    assert target.extent_y == EXTENT_Y_RAW + 1
    assert target.shared_with == ()
    assert target.editable is True
    assert [layer.slot for layer in target.slots] == [0, 1, 2, 3]
    assert target.slots[0].classification == "dominant"
    assert target.slots[1].absent
    assert not target.slots[1].editable
    assert "author a layer to activate it" in target.slots[1].read_only_reason
    assert target.free_slots == (1, 3)
    assert target.layer(0).columns == 2 and target.layer(0).rows == 2
    assert [choice.ordinal for choice in target.layer(0).vocabulary] == [1, 2, 3]


def test_a_shared_root_is_refused_because_its_slots_and_extent_are_shared(world):
    """Editing one map's root would silently change every map that loads it."""
    _image, _profile_, resizer = world
    assert resizer.target(0).shared_with == (1,)
    assert resizer.target(0).editable is False
    with pytest.raises(mr.MapStructureError, match="shared state"):
        resizer.resize(0, 0, 2, 1, 1)


def test_a_resize_refuses_shrink_rather_than_dropping_cells(world):
    """Growth only. A shrink would orphan content whose references this ticket has
    not established, so it is refused instead of silently truncating."""
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError, match="not supported"):
        resizer.resize(2, 0, 1, 2, 1)
    with pytest.raises(mr.MapStructureError, match="not supported"):
        resizer.resize(2, 0, 2, 1, 1)


def test_a_slot_holding_an_authored_layer_can_be_resized_from_its_own_grid(world):
    """The pair is what "grow a layer the project itself created" means.

    MAP-RESIZE-AND-LAYERS-001 first refused this outright - "a slot carries either
    a resize or an authored layer, not both" - which left an author able to create
    a supported layer at a chosen size but never to grow one. The rule is now the
    model the document states: the `[layer]` entry declares the grid the layer was
    CREATED at and the `[resize]` entry the grid it is GROWN to, so the authored
    grid is the resize's shrink floor rather than a bar to authoring it at all.
    """
    image, profile, _resizer = world
    layer = _resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 3, 2, 2)
    structure = _structure(layer)
    resizer = mr.MapResizer(image, structure=structure, profile=profile)
    resize = resizer.resize(2, 1, 4, 2, 1)
    assert (resize.columns, resize.rows) == (4, 2)
    # and the authored 3x2 is the floor: 2x2 would drop a column of its cells
    with pytest.raises(mr.MapStructureError, match="not supported"):
        resizer.resize(2, 1, 2, 2, 1)


def test_a_resize_refuses_a_grid_that_does_not_change(world):
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError, match="already 2x2"):
        resizer.resize(2, 0, 2, 2, 1)


@pytest.mark.parametrize("columns,rows", [(0, 3), (3, 0), (-1, 3), (99, 3), (2.0, 3), ("3", 3)])
def test_an_impossible_dimension_is_refused(world, columns, rows):
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError):
        resizer.resize(2, 0, columns, rows, 1)


@pytest.mark.parametrize("fill", [0, 4, -1, "pad", None])
def test_an_initialization_outside_the_layer_vocabulary_is_refused(world, fill):
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError):
        resizer.resize(2, 0, 3, 2, fill)


def test_an_authored_chunk_identity_is_an_accepted_initialization(world):
    """The two forms a layout cell accepts are the two forms an initialization
    accepts. Whether the named chunk EXISTS is a project-level fact this facade
    cannot see, so it is refused later, with the document that declares it."""
    _image, _profile_, resizer = world
    resize = resizer.resize(2, 0, 3, 2, "chunk:pad")
    assert resize.fill == "chunk:pad"


def test_an_unsupported_slot_is_refused_with_its_own_reason(world):
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError, match="leaves this slot unused"):
        resizer.resize(2, 1, 3, 2, 1)


def test_a_slot_outside_the_engine_four_is_refused(world):
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError, match="no layer slot"):
        resizer.resize(2, 4, 3, 2, 1)


def test_an_out_of_range_map_index_is_refused(world):
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError, match="outside"):
        resizer.target(99)


# --- the coordinate transform -------------------------------------------------

def test_the_old_grid_keeps_its_coordinates_and_the_new_cells_take_the_fill(world):
    """Top-left anchored, stated and checked at the boundary and the corners.

    Old cell ``(x, y)`` lands at new cell ``(x, y)``; every cell the growth adds is
    the initialization chunk. The check is at the exact boundary (the first added
    column, the first added row) and at both new corners, which is what a wrong
    row stride or a wrong anchor breaks.
    """
    image, profile, resizer = world
    resize = resizer.resize(2, 0, 3, 3, 2)
    resolved = mr.resolve_layer_record(image, resize, profile=profile)
    window = [entry[1] for entry in resolved.window]
    assert len(window) == 9
    vocabulary = resizer.vocabulary(2, 0)
    fill = vocabulary[1].address
    # the four retail cells, at their own coordinates in the new 3x3 grid
    assert window[0] == CHUNKS[0]
    assert window[1] == CHUNKS[1]
    assert window[3] == CHUNKS[2]
    assert window[4] == CHUNKS[0]
    # the first added column (x=2), the first added row (y=2), and both new corners
    assert window[2] == fill            # (2, 0)
    assert window[5] == fill            # (2, 1)
    assert window[6] == fill            # (0, 2)
    assert window[7] == fill            # (1, 2)
    assert window[8] == fill            # (2, 2)
    assert resolved.retail_columns == 2 and resolved.retail_rows == 2
    assert resolved.columns == 3 and resolved.rows == 3


def test_a_non_square_retail_grid_maps_by_coordinate_not_by_window_order(world):
    """A 1x3 retail grid grown to 2x4.

    A square retail grid cannot tell a row stride from a column count, so this is
    the case that makes the transform's stride observable: the retail cells keep
    their own coordinates and everything else is the initialization chunk.
    """
    image, profile, resizer = world
    target = resizer.target(3)
    assert (target.layer(0).retail_columns, target.layer(0).retail_rows) == (1, 3)
    resize = resizer.resize(3, 0, 2, 4, 1)
    resolved = mr.resolve_layer_record(image, resize, profile=profile)
    window = [entry[1] for entry in resolved.window]
    assert len(window) == 8
    assert window[0] == CHUNKS[0]      # retail (0, 0)
    assert window[2] == CHUNKS[1]      # retail (0, 1)
    assert window[4] == CHUNKS[2]      # retail (0, 2)
    fill = resizer.vocabulary(3, 0)[0].address
    for index in (1, 3, 5, 6, 7):
        assert window[index] == fill
    assert window[2] != fill and window[4] != fill


def test_the_resized_record_states_the_new_grid_and_the_full_window(world):
    image, profile, _resizer = world
    resizer = mr.MapResizer(image, profile=profile)
    resize = resizer.resize(2, 0, 3, 2, 2)
    resolved = mr.resolve_layer_record(image, resize, profile=profile)
    assert len(resolved.record) == mg.layer_record_size(3, 2)
    assert resolved.record[mg.LAYER_CHUNK_X_OFFSET] == 3
    assert resolved.record[mg.LAYER_CHUNK_Y_OFFSET] == 2
    # every header byte except the two grid bytes is the canonical record's
    assert resolved.record[:0x14] == image[LAYER - GBA: LAYER - GBA + 0x14]
    assert resolved.record[0x16:0x18] == image[LAYER - GBA + 0x16: LAYER - GBA + 0x18]
    for index, entry in enumerate(resolved.window):
        assert struct.unpack_from("<I", resolved.record, 0x18 + 4 * index)[0] == entry[1]


def test_the_extent_is_raised_to_cover_the_grown_plane_and_never_lowered(world):
    image, profile, resizer = world
    resize = resizer.resize(2, 0, 3, 2, 2)
    resolved = mr.resolve_layer_record(image, resize, profile=profile)
    changes = dict((axis, value) for axis, _field, value in resolved.extent_changes)
    assert changes["x"] == mg.declared_extent_raw(3 * mg.CHUNK_PIXELS, mg.VIEWPORT_PIXELS_X)
    assert changes["y"] == mg.declared_extent_raw(2 * mg.CHUNK_PIXELS, mg.VIEWPORT_PIXELS_Y)
    assert changes["x"] > EXTENT_X_RAW and changes["y"] > EXTENT_Y_RAW
    # Growing a plane the retail extent already covered must not lower the word.
    image2 = bytearray(_build_image())
    _place(image2, ROOT + mg.ROOT_EXTENT_X_OFFSET, struct.pack("<H", 0x0FFF))
    image2 = bytes(image2)
    profile2 = _profile(image2)
    resizer2 = mr.MapResizer(image2, profile=profile2)
    resolved2 = mr.resolve_layer_record(
        image2, resizer2.resize(2, 0, 3, 2, 2), profile=profile2
    )
    assert [entry[0] for entry in resolved2.extent_changes] == ["y"]


def test_an_authored_layer_does_not_move_the_map_extent(world):
    """A new visual layer adds content inside the map the author already has;
    changing the camera's reach is not part of adding one."""
    image, profile, resizer = world
    layer = resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 3, 2, 1)
    resolved = mr.resolve_layer_record(image, layer, profile=profile)
    assert resolved.extent_changes == ()
    assert resolved.kind == "layer"
    assert resolved.retail_columns == 0 and resolved.retail_rows == 0


# --- layer authoring ----------------------------------------------------------

def test_an_authored_layer_activates_only_a_slot_the_image_leaves_unused(world):
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError, match="fixed at 4"):
        resizer.authored_layer("overlay", 2, 0, "map:0002/BG1", 3, 2, 1)


def test_an_authored_layers_template_must_be_on_its_own_map(world):
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError, match="another map"):
        resizer.authored_layer("overlay", 2, 1, "map:0002/BG1".replace("0002", "0000"), 3, 2, 1)


def test_a_template_naming_its_own_slot_is_refused(world):
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError, match="the slot it would activate"):
        resizer.authored_layer("overlay", 2, 1, "map:0002/BG1", 3, 2, 1)


@pytest.mark.parametrize("name", ["Overlay", "1x", "has space", "", "a" * 65, 3])
def test_an_invalid_layer_name_is_refused(world, name):
    _image, _profile_, resizer = world
    with pytest.raises(mr.MapStructureError):
        resizer.authored_layer(name, 2, 1, "map:0002/BG2", 3, 2, 1)


def test_a_layer_identity_is_normalized_once(world):
    _image, _profile_, resizer = world
    assert mr.layer_identity("overlay") == "layer:overlay"
    assert mr.layer_identity("layer:overlay") == "layer:overlay"
    assert resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 3, 2, 1).identity == (
        "layer:overlay"
    )


def test_authored_cell_content_overrides_the_initialization_and_must_be_known(world):
    image, profile, resizer = world
    layer = resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 2, 2, 1)
    layout = LayoutEdits(maps={"map:0002": {1: {0: 3, 3: 2}}})
    resolved = mr.resolve_layer_record(image, layer, layout=layout, profile=profile)
    window = [entry[2] for entry in resolved.window]
    assert window[0] == 3 and window[3] == 2 and window[1] == 1
    broken = LayoutEdits(maps={"map:0002": {1: {0: 9}}})
    with pytest.raises(mr.MapStructureError, match="not one of"):
        mr.resolve_layer_record(image, layer, layout=broken, profile=profile)


def test_an_authored_chunk_cell_without_a_placed_body_is_refused(world):
    """A cell that names an authored chunk must name one the build placed."""
    image, profile, resizer = world
    layer = resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 2, 1, 1)
    layout = LayoutEdits(maps={"map:0002": {1: {0: "chunk:pad"}}})
    with pytest.raises(mr.MapStructureError, match="did not place"):
        mr.resolve_layer_record(image, layer, layout=layout, profile=profile)
    resolved = mr.resolve_layer_record(
        image, layer, layout=layout, profile=profile, chunk_addresses={"chunk:pad": 0x08800000}
    )
    assert resolved.window[0][1] == 0x08800000
    assert resolved.record.count(struct.pack("<I", 0x08800000)) == 1


# --- copy independence and the template ---------------------------------------

def test_the_authored_layer_never_touches_its_template(world):
    """The template is resolved against the immutable image and only a new record
    is emitted, so the source layer's bytes appear in no change of their own."""
    image, profile, resizer = world
    layer = resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 3, 2, 2)
    structure = _structure(layer)
    materialization = mr.materialize_map_structure(image, structure, profile=profile)
    template_bytes = image[SECOND_LAYER - GBA: SECOND_LAYER - GBA + 0x28]
    for change in materialization.changes:
        if change.offset < len(image):
            assert change.old == image[change.offset:change.offset + len(change.old)]
            assert not (
                change.offset < SECOND_LAYER - GBA + 0x28
                and change.offset + len(change.old) > SECOND_LAYER - GBA
            ), "a change overwrote the template layer record"
    assert template_bytes == image[SECOND_LAYER - GBA: SECOND_LAYER - GBA + 0x28]
    # and the authored grid is the authored one, not the template's
    assert layer.columns == 3 and layer.rows == 2


def test_editing_the_authored_layer_leaves_the_source_grid_alone(world):
    image, profile, resizer = world
    layer = resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 3, 2, 1)
    before = resizer.target(2).layer(0).cells
    edited = mr.MapResizer(image, profile=profile).target(2).layer(0).cells
    assert before == edited == (CHUNKS[0], CHUNKS[1], CHUNKS[2], CHUNKS[0])


def test_a_slot_claimed_by_two_layers_is_refused_by_the_document_reader():
    """One slot, one owner. `MapStructure.from_document` is where the check lives,
    because a document is the only place both claims can appear at once.

    A `[layer]` and a `[resize]` on one slot are no longer a double claim: that
    pair means "created at this grid, grown to that one", so the claim this reader
    still refuses is two records of the SAME kind - two layers here, two resizes in
    `test_a_slot_claimed_by_two_resizes_is_refused`.
    """
    document = {
        "layer": {
            "layer:overlay": {
                "map": "map:0002",
                "slot": 0,
                "template": "map:0002/BG2",
                "columns": 3,
                "rows": 2,
                "fill": 1,
            },
            "layer:second": {
                "map": "map:0002",
                "slot": 0,
                "template": "map:0002/BG2",
                "columns": 2,
                "rows": 1,
                "fill": 1,
            },
        },
    }
    with pytest.raises(ProjectValidationError, match="claimed by both"):
        MapStructure.from_document(document, "t")


# --- a created layer that is then grown ---------------------------------------
#
# MAP-RESIZE-AND-LAYERS-001 gap closure. A `[layer]` entry and a `[resize]` entry
# on one slot mean one thing: the layer was CREATED at the layer's grid and GROWN
# to the resize's. The resize's base grid is then the authored layer's, its header
# is the authored layer's template, and the build emits one record for the slot.

AUTHORED_SLOT = 1
AUTHORED_TEMPLATE = "map:0002/BG2"
CREATED_FILL = 1
GROWN_FILL = 3


def _pair(world, created=(1, 2), grown=(2, 2), fill=GROWN_FILL, created_fill=CREATED_FILL):
    """``(image, profile, structure, layer, resize)`` for one grown authored layer.

    The resize is validated against the created layer, exactly as the authoring
    facade does, so the fixture cannot state a pair the SDK would refuse.
    """
    image, profile, _resizer = world
    boot = mr.MapResizer(image, profile=profile)
    layer = boot.authored_layer(
        "overlay", 2, AUTHORED_SLOT, AUTHORED_TEMPLATE, created[0], created[1],
        created_fill,
    )
    staged = mr.MapResizer(image, structure=_structure(layer), profile=profile)
    resize = staged.resize(2, AUTHORED_SLOT, grown[0], grown[1], fill)
    return image, profile, _structure(layer, resize), layer, resize


def test_a_grown_authored_layer_keeps_its_cells_and_fills_only_the_added_ones(world):
    """The authored grid's cells keep their own coordinates in the grown grid.

    The created layer is 1 column by 2 rows and grows to 2x2. Its two cells are at
    (0, 0) and (0, 1) - grown cells 0 and **2** - and only the added column takes
    the resize's initialization. Copying the created window sequentially into the
    grown one would put them at cells 0 and 1, which is exactly what this catches;
    the added cells are checked at both rows.
    """
    image, profile, structure, _layer, resize = _pair(world, created=(1, 2), grown=(2, 2))
    resolved = mr.resolve_layer_record(
        image, resize, structure=structure, profile=profile
    )
    window = [entry[1] for entry in resolved.window]
    assert len(window) == 4
    assert window[0] == CHUNKS[0] and window[2] == CHUNKS[0]   # created (0,0), (0,1)
    assert window[1] == CHUNKS[2] and window[3] == CHUNKS[2]   # added   (1,0), (1,1)
    assert window[0] != window[1]
    # the record states the GROWN grid and the created grid is recorded beside it
    assert (resolved.columns, resolved.rows) == (2, 2)
    assert (resolved.authored_columns, resolved.authored_rows) == (1, 2)
    assert resolved.kind == "resize"
    assert resolved.owner == "layer:overlay" and resolved.authored_layer == "layer:overlay"


def test_authored_cell_content_in_the_grown_grid_keeps_its_coordinates(world):
    """`maps/layout.toml` names cells of the grown grid, and each keeps its place.

    Cell 2 is the created layer's own (0, 1) and cell 3 is the added (1, 1); an
    override on each must land where it names, and each cell's provenance ordinal
    must be the fill that actually applies to it.
    """
    image, profile, structure, _layer, resize = _pair(world, created=(1, 2), grown=(2, 2))
    layout = LayoutEdits(maps={"map:0002": {AUTHORED_SLOT: {2: 3, 3: 2}}})
    resolved = mr.resolve_layer_record(
        image, resize, structure=structure, layout=layout, profile=profile
    )
    assert [(entry[0], entry[1], entry[2]) for entry in resolved.window] == [
        (0, CHUNKS[0], CREATED_FILL),
        (1, CHUNKS[2], GROWN_FILL),
        (2, CHUNKS[2], 3),
        (3, CHUNKS[1], 2),
    ]


def test_the_structural_view_of_a_grown_authored_layer_shows_the_authored_cells(world):
    """The view a Workbench surface drives is the same pair, resolved once.

    The layer listed is the project-authored one at the grid it grew to, its cells
    are the created layer's at their own coordinates with the growth's fill in the
    added column, and the slot's canonical "retail" grid is still the shared
    zero-dimension placeholder rather than the template's 2x2.
    """
    image, profile, structure, _layer, _resize = _pair(world, created=(1, 2), grown=(2, 2))
    layers = mr.structural_layers(image, structure, profile=profile)
    assert len(layers) == 1
    view = layers[0]
    assert view.identity == "layer:overlay"
    assert view.resized is True and view.structural is True
    assert (view.columns, view.rows) == (2, 2)
    assert (view.retail_columns, view.retail_rows) == (0, 0)
    assert view.cells == (CHUNKS[0], CHUNKS[2], CHUNKS[0], CHUNKS[2])
    assert view.authored_cells == (None, None, None, None)
    assert view.editable and not view.read_only_reason
    assert view.label == "BG1 · chunk grid 2×2"
    # and the template's vocabulary is what the grown layer may be composed from
    assert [choice.address for choice in view.vocabulary] == list(CHUNKS)


def test_a_grown_authored_layer_may_initialize_from_two_authored_chunks(world):
    """Both initializations may name project-authored chunks, and both materialize.

    The created cell's body and the added cell's body are two different resources
    named by ONE record, and a structural reference has no cell of its own to tell
    them apart - what distinguishes the two is the chunk each names. A build that
    keyed them by "cell -1" alone would refuse a legal project here.

    The template plane is given a second distinct entry first, because an authored
    chunk may only rearrange screen entries its template's own layer already draws
    and a perfectly uniform template admits no edit at all.
    """
    image, profile, structure, _layer, resize = _pair(
        world, created=(1, 1), grown=(2, 1), fill="chunk:grown",
        created_fill="chunk:pad",
    )
    image = bytearray(image)
    _place(
        image, CHUNKS[0],
        lz.build_stored(struct.pack("<1024H", *([0x0010] * 1023 + [0x0011]))),
    )
    image = bytes(image)
    profile = _profile(image)

    placements = mr.structural_placements(
        image, structure, LayoutEdits(), profile=profile
    )
    assert [(p.identity, p.is_structural, p.cell, p.offset) for p in placements] == [
        ("chunk:pad", True, -1, -1),
        ("chunk:grown", True, -1, -1),
    ]

    chunks = {
        identity: AuthoredChunk(
            identity=identity,
            template="map:0002/layer:2/chunk:1",
            entries=(
                AuthoredChunkEntry(row=0, column=0, prior=0x0010, entry=0x0011),
            ),
        )
        for identity in ("chunk:pad", "chunk:grown")
    }
    materialization = mc.materialize_authored_chunks(
        image, chunks, {}, profile=profile, structural=placements
    )
    assert len(materialization.builds) == 2
    addresses = {build.identity: build.rom_address for build in materialization.builds}
    assert addresses["chunk:pad"] != addresses["chunk:grown"]
    # both bodies are placed and each is referenced from its own cell of the ONE
    # record the pair emits
    resolved = mr.resolve_layer_record(
        image, resize, structure=structure, profile=profile, chunk_addresses=addresses
    )
    assert [entry[1] for entry in resolved.window] == [
        addresses["chunk:pad"], addresses["chunk:grown"],
    ]
    assert struct.unpack_from("<I", resolved.record, 0x18)[0] == addresses["chunk:pad"]
    assert struct.unpack_from("<I", resolved.record, 0x1C)[0] == addresses["chunk:grown"]
    assert len(resolved.record) == mg.layer_record_size(2, 1)
    with pytest.raises(mr.MapStructureError, match="did not place"):
        mr.resolve_layer_record(image, resize, structure=structure, profile=profile)


def test_a_grown_authored_layers_record_header_is_its_templates(world):
    """The header is the authored layer's TEMPLATE, byte for byte.

    The slot's own canonical record is the shared zero-dimension placeholder, so
    there is no retail header to copy and the template's is the only honest source.
    The template carries a marker the other records do not, which the emitted
    record has to carry too.
    """
    image, profile, structure, _layer, resize = _pair(world, created=(1, 1), grown=(2, 1))
    resolved = mr.resolve_layer_record(
        image, resize, structure=structure, profile=profile
    )
    template = image[SECOND_LAYER - GBA: SECOND_LAYER - GBA + 0x18]
    assert resolved.template_address == SECOND_LAYER
    assert resolved.record[:0x14] == template[:0x14]
    assert resolved.record[0x16:0x18] == template[0x16:0x18]
    assert struct.unpack_from("<I", resolved.record, 0x04)[0] == TEMPLATE_SCALAR
    # the two grid bytes are the grown grid's, not the template's own 2x2
    assert (resolved.record[0x14], resolved.record[0x15]) == (2, 1)
    assert resolved.record[:0x18] != image[LAYER - GBA: LAYER - GBA + 0x18]
    assert resolved.record[:0x18] != image[
        mg.ABSENT_LAYER_RECORD - GBA: mg.ABSENT_LAYER_RECORD - GBA + 0x18
    ]
    # and the whole record is exactly header + window
    assert len(resolved.record) == mg.layer_record_size(2, 1)


def test_the_pair_is_one_record_one_slot_write_and_one_reservation(world):
    """One slot, one record, one root-slot write - however many entries name it.

    The document holds three entries (the created layer, the resize of it, and an
    unrelated retail resize); the build must resolve two records, reserve two
    non-overlapping spans and write the map root's own slot field once per slot.
    """
    image, profile, structure, _layer, resize = _pair(world, created=(1, 1), grown=(2, 1))
    other = mr.MapResizer(image, profile=profile).resize(2, 0, 3, 3, 2)
    structure = _structure(_layer, resize, other)
    materialization = mr.materialize_map_structure(image, structure, profile=profile)

    assert len(materialization.builds) == 2
    assert len(materialization.provenance) == 2
    grown = next(
        build for build in materialization.builds if build.owner == "layer:overlay"
    )
    assert grown.resolved.kind == "resize"
    assert len(grown.resolved.record) == mg.layer_record_size(2, 1)
    assert grown.allocation.range.start.value >= len(image)
    assert grown.record_address >= GBA + len(image)
    assert grown.expanded

    slot_field = (ROOT + mg.ROOT_LAYER_SLOTS[AUTHORED_SLOT]) - GBA
    writes = [c for c in materialization.changes if c.offset == slot_field]
    assert len(writes) == 1
    assert writes[0].old == mg.ABSENT_LAYER_RECORD.to_bytes(4, "little")
    assert writes[0].new == grown.record_address.to_bytes(4, "little")
    assert writes[0].owner == "layer:overlay"

    assert len(materialization.reserved) == 2
    spans = sorted(materialization.reserved, key=lambda span: span.start.value)
    assert spans[0].end <= spans[1].start.value
    assert all(span.start.value >= len(image) for span in spans)


def test_the_manifest_tells_an_authored_layers_resize_from_a_retails(world):
    """Provenance names which of the two a resize is, and the authored identity.

    A manifest reader has to be able to tell a retail layer's resize from a
    project-authored layer's without opening the project, so the authored identity
    and the created grid are recorded - and the keys are additive, not renamed.
    """
    image, profile, structure, _layer, resize = _pair(world, created=(1, 1), grown=(2, 1))
    other = mr.MapResizer(image, profile=profile).resize(2, 0, 3, 3, 2)
    materialization = mr.materialize_map_structure(
        image, _structure(_layer, resize, other), profile=profile
    )
    provenance = {item.owner: item for item in materialization.provenance}

    grown = provenance["layer:overlay"]
    assert grown.kind == "resize"
    assert grown.authored is True
    assert grown.authored_layer == "layer:overlay"
    assert (grown.authored_columns, grown.authored_rows) == (1, 1)
    assert (grown.columns, grown.rows) == (2, 1)
    assert (grown.retail_columns, grown.retail_rows) == (0, 0)
    assert grown.template_address == SECOND_LAYER

    retail = provenance["map:0002/BG0"]
    assert retail.kind == "resize"
    assert retail.authored is False
    assert retail.authored_layer == ""
    assert (retail.authored_columns, retail.authored_rows) == (0, 0)
    assert retail.template_address == LAYER

    document = grown.to_json()
    for key in (
        "kind", "owner", "map_index", "layer_slot", "template_address",
        "template_address_hex", "retail_columns", "retail_rows", "columns", "rows",
        "slot_offset", "slot_offset_hex", "previous_record_address",
        "previous_record_address_hex", "record_address", "record_address_hex",
        "record_size", "allocation_file_offset", "allocation_size", "expanded",
        "expansion_evidence", "record_sha256", "cell_entries", "fills", "extents",
    ):
        assert key in document, key
    assert document["authored_layer"] == "layer:overlay"
    assert document["authored_columns"] == 1 and document["authored_rows"] == 1


def test_a_resize_of_an_authored_layer_that_shrinks_or_does_not_change_is_refused(world):
    """The authored grid is the shrink floor, and a resize must still change it.

    The refusal reasons are the ones a retail resize already gives: an authored
    layer's cells are exactly as unreferenced-by-measurement as a retail layer's.
    """
    image, profile, _resizer = world
    layer = mr.MapResizer(image, profile=profile).authored_layer(
        "overlay", 2, AUTHORED_SLOT, AUTHORED_TEMPLATE, 2, 2, CREATED_FILL
    )
    resizer = mr.MapResizer(image, structure=_structure(layer), profile=profile)
    with pytest.raises(mr.MapStructureError, match="not supported"):
        resizer.resize(2, AUTHORED_SLOT, 1, 2, GROWN_FILL)
    with pytest.raises(mr.MapStructureError, match="not supported"):
        resizer.resize(2, AUTHORED_SLOT, 2, 1, GROWN_FILL)
    with pytest.raises(mr.MapStructureError, match="already 2x2"):
        resizer.resize(2, AUTHORED_SLOT, 2, 2, GROWN_FILL)
    assert resizer.resize(2, AUTHORED_SLOT, 3, 2, GROWN_FILL).columns == 3


def test_a_pair_whose_resize_does_not_grow_the_layer_is_refused_by_the_build(world):
    """Even a document assembled past the facade cannot shrink an authored layer."""
    image, profile, _resizer = world
    layer = AuthoredLayer(
        identity="layer:overlay",
        map_index=2,
        layer_slot=AUTHORED_SLOT,
        template=AUTHORED_TEMPLATE,
        columns=2,
        rows=2,
        fill=CREATED_FILL,
    )
    smaller = LayerResize(
        map_index=2, layer_slot=AUTHORED_SLOT, columns=1, rows=2, fill=GROWN_FILL
    )
    # the document refuses to hold it at all ...
    with pytest.raises(ProjectValidationError, match="smaller on neither"):
        MapStructure(resizes={smaller.key: smaller}, layers={layer.identity: layer})
    # ... and the resolver refuses it too, for a caller that reaches it directly
    with pytest.raises(mr.MapStructureError, match="smaller on neither"):
        mr.resolve_layer_record(
            image,
            smaller,
            structure=_structure(layer),
            profile=profile,
        )


# --- placement, reservation and provenance ------------------------------------

def test_every_record_is_placed_above_the_canonical_eof(world):
    """The domain is EXPANDED_ONLY: a record grows with the grid and the canonical
    image declares one 256-byte free region, so canonical placement cannot serve
    the domain's aggregate demand."""
    image, profile, resizer = world
    structure = _structure(
        resizer.resize(2, 0, 3, 2, 2),
        resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 3, 2, 2),
    )
    materialization = mr.materialize_map_structure(image, structure, profile=profile)
    assert len(materialization.builds) == 2
    for build in materialization.builds:
        assert build.allocation.range.start.value >= len(image)
        assert build.record_address >= GBA + len(image)
        assert build.expanded
    assert len(materialization.generated_allocations) == 2


def test_allocation_is_deterministic_and_reservations_do_not_overlap(world):
    """M9: disabling the reservation set would let two records share bytes."""
    image, profile, resizer = world
    structure = _structure(
        resizer.resize(2, 0, 3, 3, 2),
        resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 4, 2, 2),
    )
    first = mr.materialize_map_structure(image, structure, profile=profile)
    second = mr.materialize_map_structure(image, structure, profile=profile)
    assert [b.record_address for b in first.builds] == [b.record_address for b in second.builds]
    spans = sorted(
        (build.allocation.range for build in first.builds),
        key=lambda span: span.start.value,
    )
    for left, right in zip(spans, spans[1:]):
        assert not left.overlaps(right)


def test_the_root_slot_reference_is_the_full_gba_address(world):
    """M10: a truncated reference would address the wrong record."""
    image, profile, resizer = world
    structure = _structure(resizer.resize(2, 0, 3, 2, 2))
    materialization = mr.materialize_map_structure(image, structure, profile=profile)
    build = materialization.builds[0]
    slot_change = next(
        change for change in materialization.changes if change.offset == build.slot_offset
    )
    assert slot_change.new == build.record_address.to_bytes(4, "little")
    assert len(slot_change.new) == 4
    assert struct.unpack("<I", slot_change.new)[0] >= GBA + len(image)
    assert build.slot_offset == (ROOT + mg.ROOT_LAYER_SLOTS[0]) - GBA


def test_the_manifest_records_the_grid_the_record_and_the_extent(world):
    image, profile, resizer = world
    structure = _structure(resizer.resize(2, 0, 3, 2, 2))
    materialization = mr.materialize_map_structure(image, structure, profile=profile)
    provenance = materialization.provenance[0]
    assert provenance.kind == "resize"
    assert provenance.owner == "map:0002/BG0"
    assert (provenance.retail_columns, provenance.retail_rows) == (2, 2)
    assert (provenance.columns, provenance.rows) == (3, 2)
    assert provenance.record_size == mg.layer_record_size(3, 2)
    assert provenance.record_address == materialization.builds[0].record_address
    assert [extent.axis for extent in provenance.extents] == ["x", "y"]
    assert provenance.template_address == LAYER
    assert provenance.expanded and provenance.expansion_evidence
    # the record's own bytes are pinned by digest, so the manifest identifies them
    assert provenance.record_sha256 == hashlib.sha256(
        materialization.builds[0].resolved.record
    ).hexdigest()


def test_a_structural_fill_that_names_an_authored_chunk_is_a_site_less_placement(world):
    image, profile, resizer = world
    structure = _structure(
        resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 2, 2, "chunk:pad")
    )
    placements = mr.structural_placements(image, structure, LayoutEdits(), profile=profile)
    assert len(placements) == 1
    assert placements[0].is_structural
    assert placements[0].offset == -1 and placements[0].cell == -1
    assert placements[0].identity == "chunk:pad"


def test_structural_layers_resolves_every_authored_slot(world):
    image, profile, resizer = world
    structure = _structure(
        resizer.resize(2, 0, 3, 2, 2),
        resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 3, 2, 2),
    )
    layers = mr.structural_layers(image, structure, profile=profile)
    assert [(layer.slot, layer.columns, layer.rows) for layer in layers] == [
        (0, 3, 2),
        (1, 3, 2),
    ]
    assert layers[0].resized and not layers[0].identity
    assert layers[1].identity == "layer:overlay"


# --- the persisted document is what the build resolves ------------------------

def test_the_resize_a_facade_returns_is_exactly_what_the_project_stores(world):
    _image, _profile_, resizer = world
    resize = resizer.resize(2, 0, 3, 2, 2)
    document = resize.to_document()
    assert document == {"columns": 3, "rows": 2, "fill": 2}
    assert LayerResize.from_document(resize.key, document, "t") == resize


def test_describe_names_the_change_for_a_person(world):
    _image, _profile_, resizer = world
    line = resizer.describe(resizer.resize(2, 0, 3, 2, 2))
    assert "map:0002" in line and "BG0" in line and "3×2" in line
    layer = resizer.authored_layer("overlay", 2, 1, "map:0002/BG2", 3, 2, 2)
    line = resizer.describe(layer)
    assert "layer:overlay" in line and "3×2" in line and "map:0002/BG2" in line
