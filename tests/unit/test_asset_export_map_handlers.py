"""Portable tests for the map-layer handler registry.

Synthetic fixtures only: no ROM, no extracted assets. These pin the two facts the
exporter's map classification depends on after ASSET-EXPORT-MAP-HANDLERS-001:

* which record field each screen-entry handler names its container from, and that
  the reader takes that field from the record's own handler word rather than from a
  fixed offset; and
* the class, graphical and composite-blocking predicates for every handler, so a
  handler cannot silently fall back into a class it does not belong to.
"""

from __future__ import annotations

import struct

import pytest

from tools.export import canonical as canon

GBA = 0x08000000
RECORD_ADDRESS = GBA + 0x100
CONTAINER_ADDRESS = GBA + 0x400
OTHER_CONTAINER_ADDRESS = GBA + 0x1000
IMAGE_SIZE = 0x2000
ENTRY_COUNT = canon.SCREENBLOCK_ENTRY_COUNT
PLANE_BYTES = canon.SCREENBLOCK_DECODED_BYTES


def _entries(first: int) -> bytes:
    return b"".join(struct.pack("<H", (first + index) & 0x3FF) for index in range(ENTRY_COUNT))


def _image(*, handler: int, field: int, declared: int = PLANE_BYTES) -> canon.Rom:
    """A minimal image holding one record and two candidate containers."""
    data = bytearray(IMAGE_SIZE)
    struct.pack_into("<I", data, RECORD_ADDRESS - GBA, handler)
    struct.pack_into("<I", data, RECORD_ADDRESS - GBA + field, CONTAINER_ADDRESS)
    # Every other candidate field names a container of a different plane, so a
    # reader that used the wrong field would return recognisably wrong entries.
    for offset in (0x04, 0x08, 0x1C):
        if offset != field:
            struct.pack_into(
                "<I", data, RECORD_ADDRESS - GBA + offset, OTHER_CONTAINER_ADDRESS
            )
    struct.pack_into("<II", data, CONTAINER_ADDRESS - GBA, 0, declared)
    payload = _entries(0)
    data[CONTAINER_ADDRESS - GBA + 8 : CONTAINER_ADDRESS - GBA + 8 + len(payload)] = (
        payload
    )
    struct.pack_into("<II", data, OTHER_CONTAINER_ADDRESS - GBA, 0, PLANE_BYTES)
    other = _entries(1000)
    data[
        OTHER_CONTAINER_ADDRESS - GBA + 8 : OTHER_CONTAINER_ADDRESS - GBA + 8 + len(other)
    ] = other
    return canon.Rom(bytes(data))


def _record(handler: int, chunk_x: int = 2, chunk_y: int = 2) -> canon.LayerRecord:
    address = (
        canon.ABSENT_LAYER_RECORD
        if handler == canon.ABSENT_LAYER_HANDLER
        else RECORD_ADDRESS
    )
    return canon.LayerRecord(
        slot=0,
        address=address,
        handler=handler,
        chunk_x=chunk_x,
        chunk_y=chunk_y,
        chunk_addresses=(),
        null_chunk_count=0,
    )


# --- the handler registry ----------------------------------------------------

def test_the_registry_names_the_two_screen_entry_handlers_and_their_fields():
    assert canon.SCREENBLOCK_HANDLERS == {0x08007B63: 0x04, 0x0800897B: 0x1C}
    assert canon.screenblock_container_offset(0x08007B63) == 0x04
    assert canon.screenblock_container_offset(0x0800897B) == 0x1C


def test_a_handler_that_is_not_a_screen_entry_layer_is_refused():
    for handler in (0x08008087, 0x08007A41, 0x080088BD, 0):
        with pytest.raises(canon.CanonicalError):
            canon.screenblock_container_offset(handler)


def test_the_constructor_buffered_handler_reads_record_plus_0x04():
    rom = _image(handler=0x08007B63, field=0x04)
    assert canon.read_screenblock_entries(rom, RECORD_ADDRESS) == struct.unpack(
        "<1024H", _entries(0)
    )


def test_the_uploaded_handler_reads_record_plus_0x1c():
    """`0x0800897B`'s method 1 loads `record + 0x1C`, not `record + 0x04`."""
    rom = _image(handler=0x0800897B, field=0x1C)
    assert canon.read_screenblock_entries(rom, RECORD_ADDRESS) == struct.unpack(
        "<1024H", _entries(0)
    )


def test_the_container_field_follows_the_records_own_handler_word():
    """Moving the plane to the other handler's field must change what is read.

    This is the regression that matters: the reader takes the field from the
    record's `+0x00` word, so a record cannot be read at the other handler's
    offset.
    """
    uploaded = _image(handler=0x0800897B, field=0x1C)
    assert canon.read_screenblock_entries(uploaded, RECORD_ADDRESS)[0] == 0
    mismatched = _image(handler=0x0800897B, field=0x04)
    assert canon.read_screenblock_entries(mismatched, RECORD_ADDRESS)[0] == 1000


def test_a_plane_of_the_wrong_declared_size_is_refused():
    rom = _image(handler=0x0800897B, field=0x1C, declared=0x400)
    with pytest.raises(canon.CanonicalError) as excinfo:
        canon.read_screenblock_entries(rom, RECORD_ADDRESS)
    # The refusal is the shared reader's: it names the size it decoded and the
    # 0x800 bytes a screen-entry plane declares, which is the same comparison the
    # SDK's map view performs.
    assert "expected 0x800" in str(excinfo.value)
    assert "decoded 0x400" in str(excinfo.value)


# --- the terrain-field record form -------------------------------------------

TERRAIN_RECORD = GBA + 0x2000
TERRAIN_CELL_BYTES = canon.TERRAIN_FIELD_CELL_BYTES
#: Room for the terrain record plus its own container arena, which starts past
#: the screen-entry fixtures this module also builds.
TERRAIN_IMAGE_SIZE = 0x40000


def _terrain_image(grid_x: int, grid_y: int, *, stride: int = 4) -> canon.Rom:
    """A synthetic terrain-field record whose cells are recognisable ordinal runs.

    Cell ``n`` decodes to ``bytes(range(n, n + 32))`` repeated to fill its
    declared 0x400 bytes, so a plane that places a cell in the wrong position, or
    a render that resolves the wrong ordinal, is detectable from the result alone.
    """
    data = bytearray(TERRAIN_IMAGE_SIZE)
    struct.pack_into("<I", data, TERRAIN_RECORD - GBA, canon.TERRAIN_FIELD_LAYER_HANDLER)
    data[TERRAIN_RECORD - GBA + canon.TERRAIN_FIELD_GRID_X_OFFSET] = grid_x
    data[TERRAIN_RECORD - GBA + canon.TERRAIN_FIELD_GRID_Y_OFFSET] = grid_y
    cells = grid_x * grid_y
    cursor = CONTAINER_ADDRESS
    for index in range(cells):
        struct.pack_into(
            "<I",
            data,
            TERRAIN_RECORD - GBA + canon.TERRAIN_FIELD_CONTAINER_OFFSET + index * 4,
            cursor,
        )
        struct.pack_into("<II", data, cursor - GBA, 0, TERRAIN_CELL_BYTES)
        fill = bytes((index + step) & 0xFF for step in range(32))
        payload = (fill * (TERRAIN_CELL_BYTES // len(fill) + 1))[:TERRAIN_CELL_BYTES]
        data[cursor - GBA + 8 : cursor - GBA + 8 + TERRAIN_CELL_BYTES] = payload
        cursor += 8 + TERRAIN_CELL_BYTES + stride
    return canon.Rom(bytes(data))


def _char_block(ordinals: int) -> bytes:
    """`ordinals` 8x8 tiles, each filled with that tile's own ordinal value."""
    tile = canon.TILE_PIXELS * canon.TILE_PIXELS
    return bytes(
        value
        for ordinal in range(ordinals)
        for value in bytes([ordinal & 0xFF]) * tile
    )


def test_the_terrain_field_reader_takes_its_grid_from_its_own_record_fields():
    """A terrain-field record states its cell grid at `+0x04`/`+0x05`.

    The dominant form's `+0x14`/`+0x15` hold unrelated bytes on this form - on the
    canonical record they are two bytes of the container pointer run, reading as
    48 x 251 - so a reader that used those offsets would read the wrong grid.
    """
    rom = _terrain_image(3, 2)
    assert canon.read_terrain_field_containers(rom, TERRAIN_RECORD) == tuple(
        CONTAINER_ADDRESS + index * (8 + TERRAIN_CELL_BYTES + 4) for index in range(6)
    )
    probe = canon.read_terrain_field_probe(rom, TERRAIN_RECORD)
    assert (probe["grid_x"], probe["grid_y"]) == (3, 2)
    assert probe["grid_product"] == 6
    assert probe["chunk_targets"] == 6
    assert probe["chunk_decoded_bytes"] == TERRAIN_CELL_BYTES
    assert probe["cell_tiles"] == canon.TERRAIN_FIELD_CELL_TILES
    cells = canon.read_terrain_field_cells(rom, TERRAIN_RECORD)
    assert len(cells) == 6
    assert all(len(cell) == TERRAIN_CELL_BYTES for cell in cells)
    assert cells[0][0] == 0 and cells[5][0] == 5


def test_an_empty_terrain_grid_names_no_containers():
    """A zero-dimension grid is an empty field, not an error."""
    rom = _terrain_image(0, 0)
    assert canon.read_terrain_field_containers(rom, TERRAIN_RECORD) == ()
    assert canon.read_terrain_field_cells(rom, TERRAIN_RECORD) == ()


def test_a_terrain_field_container_outside_the_image_is_refused():
    rom = _terrain_image(2, 1)
    data = bytearray(rom.data)
    struct.pack_into("<I", data, TERRAIN_RECORD - GBA + 0x08, GBA + 0x100000)
    with pytest.raises(canon.CanonicalError) as excinfo:
        canon.read_terrain_field_containers(canon.Rom(bytes(data)), TERRAIN_RECORD)
    assert "outside the image" in str(excinfo.value)


def test_the_terrain_field_plane_places_each_cell_at_its_own_raster_position():
    """Container `y * grid_x + x` supplies the cell at `(x * 32, y * 32)` tiles."""
    from tools.export import render

    rom = _terrain_image(3, 2)
    cells = canon.read_terrain_field_cells(rom, TERRAIN_RECORD)
    width, height, plane = render.read_terrain_field_plane(cells, 3, 2)
    cell = canon.TERRAIN_FIELD_CELL_TILES
    assert (width, height) == (3 * cell, 2 * cell)
    assert len(plane) == width * height
    row_bytes = TERRAIN_CELL_BYTES // cell
    for index in range(6):
        at_x = (index % 3) * cell
        at_y = (index // 3) * cell
        assert plane[at_y * width + at_x] == cells[index][0]
        # the last ordinal of the cell's first raster row
        assert plane[at_y * width + at_x + cell - 1] == (
            cells[index][row_bytes - 1]
        )


def test_the_terrain_field_render_resolves_ordinals_through_the_char_block():
    """The rendered image is the plane's ordinals resolved as 8x8 tiles."""
    from tools.export import render

    rom = _terrain_image(3, 2)
    cells = canon.read_terrain_field_cells(rom, TERRAIN_RECORD)
    block = _char_block(256)
    width, height, pixels = render.render_terrain_field(cells, 3, 2, block)
    cell = canon.TERRAIN_FIELD_CELL_TILES
    assert (width, height) == (
        3 * cell * canon.TILE_PIXELS,
        2 * cell * canon.TILE_PIXELS,
    )
    assert len(pixels) == width * height
    # Every 8x8 tile of the image must be one flat ordinal value - the fixture's
    # character block fills each tile with its own ordinal - and the value at a
    # cell's first tile must be that cell's own ordinal.
    for index in range(6):
        at_x = (index % 3) * cell * canon.TILE_PIXELS
        at_y = (index // 3) * cell * canon.TILE_PIXELS
        assert pixels[at_y * width + at_x] == cells[index][0]
    # Every 8x8 tile of the image is one flat ordinal value: the fixture's
    # character block fills each tile with its own ordinal. Probe a row inside
    # three tiles chosen across the image.
    span = canon.TILE_PIXELS
    for tile_x, tile_y in ((0, 0), (5, 3), (width // span - 1, height // span - 1)):
        row = (tile_y * span + 1) * width + tile_x * span
        assert len(set(pixels[row : row + span])) == 1, (tile_x, tile_y)


def test_a_terrain_field_with_the_wrong_container_count_is_refused():
    from tools.export import render

    rom = _terrain_image(2, 2)
    cells = canon.read_terrain_field_cells(rom, TERRAIN_RECORD)
    block = _char_block(256)
    with pytest.raises(render.RenderError) as excinfo:
        render.render_terrain_field(cells[:3], 2, 2, block)
    assert "needs 4 containers" in str(excinfo.value)


def test_a_terrain_field_container_of_the_wrong_size_is_refused():
    from tools.export import render

    with pytest.raises(render.RenderError) as excinfo:
        render.render_terrain_field((bytes(64),), 1, 1, _char_block(16))
    assert "expected 1024" in str(excinfo.value)


def test_a_terrain_field_with_a_zero_grid_is_refused():
    from tools.export import render

    with pytest.raises(render.RenderError) as excinfo:
        render.render_terrain_field((), 0, 5, _char_block(16))
    assert "positive grid" in str(excinfo.value)


def test_an_ordinal_outside_the_character_block_is_refused():
    """An ordinal that does not resolve must fail closed, not read past the block."""
    from tools.export import render

    rom = _terrain_image(0, 0)
    # one container of ordinal 200 against a 16-tile character block
    payload = bytes([200]) * TERRAIN_CELL_BYTES
    with pytest.raises(render.RenderError) as excinfo:
        render.render_terrain_field((payload,), 1, 1, _char_block(16))
    assert "outside the 16-tile character block" in str(excinfo.value)


# --- the class predicates ----------------------------------------------------

@pytest.mark.parametrize(
    "handler,expected",
    [
        (canon.DOMINANT_LAYER_HANDLER, "dominant"),
        (0x08007B63, "static_graphical_screenblock"),
        (0x0800897B, "static_graphical_screenblock"),
        (0x080088BD, "static_graphical_terrain_field"),
    ],
)
def test_each_handler_gets_its_own_final_class(handler: int, expected: str):
    assert _record(handler).classification == expected


def test_no_known_handler_is_left_unclassified():
    for handler in (0x08008087, 0x08007A41, 0x08007B63, 0x0800897B, 0x080088BD):
        assert _record(handler).classification != "unclassified_handler"


def test_the_absent_placeholder_is_the_only_class_that_draws_nothing():
    assert _record(0x08008087).graphical is True
    assert _record(0x08007B63).graphical is True
    assert _record(0x0800897B).graphical is True
    assert _record(0x080088BD).graphical is True
    assert canon.LayerRecord(
        slot=0,
        address=canon.ABSENT_LAYER_RECORD,
        handler=canon.ABSENT_LAYER_HANDLER,
        chunk_x=0,
        chunk_y=0,
        chunk_addresses=(),
        null_chunk_count=0,
    ).graphical is False
    assert _record(0x08007A41).graphical is False


def test_the_absent_handler_is_only_the_absent_placeholder_on_its_own_record():
    """The shared absent handler at any other record fails closed.

    No such record exists in the canonical image, but the class must not spread
    by handler value alone.
    """
    assert canon.LayerRecord(
        slot=0,
        address=RECORD_ADDRESS,
        handler=canon.ABSENT_LAYER_HANDLER,
        chunk_x=0,
        chunk_y=0,
        chunk_addresses=(),
        null_chunk_count=0,
    ).classification == "unclassified_handler"


def test_a_zero_grid_dominant_record_is_not_a_rendered_layer():
    """The accepted dominant handler with an empty grid is its own class."""
    assert _record(canon.DOMINANT_LAYER_HANDLER, 0, 0).classification == (
        "dominant_zero_grid"
    )
    assert _record(canon.DOMINANT_LAYER_HANDLER, 0, 2).classification == (
        "dominant_partial_zero_grid"
    )
    assert _record(canon.DOMINANT_LAYER_HANDLER, 2, 2).classification == "dominant"


def test_no_record_form_blocks_a_composite():
    """Every handler the engine accounts for now renders, so none withholds.

    The terrain-field form was the last one that drew but could not be
    assembled; ASSET-EXPORT-MAP19-001 recovered its container geometry.
    """
    assert _record(0x08007B63).blocks_composite is False
    assert _record(0x0800897B).blocks_composite is False
    assert _record(0x080088BD).blocks_composite is False
    assert _record(0x08008087).blocks_composite is False


def test_both_screen_entry_handlers_are_renderable():
    assert _record(0x08007B63).renderable is True
    assert _record(0x0800897B).renderable is True
    assert _record(0x080088BD).renderable is True


# --- fail-closed behaviour for an unaccounted record form --------------------

def test_every_handler_the_engine_accounts_for_is_resolved():
    for handler in (0x08008087, 0x08007B63, 0x0800897B, 0x080088BD):
        assert _record(handler).resolved is True


def test_an_unknown_handler_is_not_called_non_graphical():
    """Unknown means unknown: it must withhold, not be treated as drawing nothing.

    Before this, an unaccounted handler reported `graphical=False` and
    `blocks_composite=False`, so a possibly graphical layer neither rendered nor
    blocked - the fail-open the project's semantics rules forbid.
    """
    unknown = _record(0x0800FFFF)
    assert unknown.classification == "unclassified_handler"
    assert unknown.resolved is False
    assert unknown.renderable is False
    assert unknown.blocks_composite is True


def test_a_dominant_record_with_a_zero_grid_is_unresolved_and_withholds():
    for chunk_x, chunk_y in ((0, 0), (0, 2), (2, 0)):
        record = _record(canon.DOMINANT_LAYER_HANDLER, chunk_x, chunk_y)
        assert record.resolved is False
        assert record.blocks_composite is True


def test_the_absent_placeholder_is_resolved_and_does_not_block():
    absent = _record(canon.ABSENT_LAYER_HANDLER, 0, 0)
    assert absent.classification == "absent_placeholder"
    assert absent.resolved is True
    assert absent.blocks_composite is False
