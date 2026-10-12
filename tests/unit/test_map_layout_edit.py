"""Unit tests for the layout-edit session's ROM-free pieces.

Synthetic only: no ROM, no extracted assets. The geometry, the replacement policy
and the fail-closed image gate are pure and are pinned here, so CI (which has no
canonical ROM) still exercises the rules the write and preview paths share. The
ROM-coupled behaviour - real targets, real previews, real saves - is pinned in
``tests/integration/test_map_layout_editor_rom.py``.
"""

from __future__ import annotations

import pytest

from tools.export import canonical as canon
from tools.export import map_browser as mb
from tools.webfoot import map_layout_edit as mle
from tools.webfoot.map_layout_edit import (
    LayoutCell,
    LayoutGrid,
    LayoutSlot,
    LayoutTarget,
    MapLayoutEditError,
    MapLayoutEditor,
)
from tools.webfoot.map_layout_write import (
    MapLayoutWriteError,
    MapLayoutWriter,
    legal_chunk_pointers,
    validate_chunk_replacement,
)

CHUNK = canon.CHUNK_PIXELS  # 256


def _slot(
    slot: int = 1,
    *,
    classification: str = "dominant",
    columns: int = 2,
    rows: int = 2,
    pointers: tuple[int, ...] = (0x082928DC, 0x08292A54, 0x082928DC, 0x08292AFC),
    choices: tuple[int, ...] | None = None,
    reason: str = "",
) -> LayoutSlot:
    grid = LayoutGrid(columns, rows)
    cells = tuple(
        LayoutCell(
            cell=index,
            column=grid.column_of(index) if grid.cell_count else 0,
            row=grid.row_of(index) if grid.cell_count else 0,
            pointer=pointer,
            offset=0x00292CA0 + 4 * index,
        )
        for index, pointer in enumerate(pointers)
    )
    if choices is None:
        choices = tuple(dict.fromkeys(pointer for pointer in pointers if pointer))
    return LayoutSlot(
        slot=slot,
        classification=classification,
        handler=canon.DOMINANT_LAYER_HANDLER,
        grid=grid,
        cells=cells,
        choices=choices,
        read_only_reason=reason,
    )


# --- geometry ---------------------------------------------------------------


def test_grid_geometry_maps_cells_pixels_and_back() -> None:
    grid = LayoutGrid(2, 2)
    assert (grid.cell_count, grid.width, grid.height) == (4, 2 * CHUNK, 2 * CHUNK)
    assert grid.cell_rect(0) == (0, 0, CHUNK, CHUNK)
    assert grid.cell_rect(3) == (CHUNK, CHUNK, CHUNK, CHUNK)
    for cell in range(4):
        x, y, _w, _h = grid.cell_rect(cell)
        assert grid.cell_at(x, y) == cell
        assert grid.cell_at(x + CHUNK - 1, y + CHUNK - 1) == cell
        assert grid.column_of(cell) == cell % 2
        assert grid.row_of(cell) == cell // 2


def test_grid_geometry_rejects_outside_and_non_cells() -> None:
    grid = LayoutGrid(2, 1)
    assert grid.cell_at(CHUNK * 2, 0) is None
    assert grid.cell_at(0, CHUNK) is None
    assert grid.cell_at(-1, 0) is None
    assert not grid.contains(2)
    assert not grid.contains(-1)
    assert not grid.contains(True)  # a bool is not a cell index
    assert not grid.contains(0.0)
    with pytest.raises(MapLayoutEditError):
        grid.cell_rect(2)
    with pytest.raises(MapLayoutEditError):
        grid.column_of(2)


def test_grid_covers_a_row_major_window_exactly() -> None:
    grid = LayoutGrid(5, 4)
    assert grid.cell_count == 20
    seen = {
        grid.cell_at(x, y)
        for y in range(0, grid.height, 7)
        for x in range(0, grid.width, 11)
    }
    assert seen == set(range(20))


# --- replacement policy ------------------------------------------------------


def test_replacement_policy_accepts_any_chunk_of_the_maps_dominant_layers() -> None:
    # The caller supplies the legal set, which is the map's dominant windows:
    # a layer's own chunks and its siblings' are legal on the same terms.
    layer = (0x082928DC, 0x08292A54, 0, 0x082928DC)
    sibling = (0x08292884,)
    legal = legal_chunk_pointers(layer, sibling)
    assert mb.validate_cell_replacement(legal, 0x08292A54) == 0x08292A54
    assert validate_chunk_replacement(legal, 0x082928DC) == 0x082928DC
    assert validate_chunk_replacement(legal, 0x08292884) == 0x08292884


@pytest.mark.parametrize(
    "bad",
    [
        0,           # the null pointer
        0x08299999,  # a real chunk, but not one any layer of this map uses
        True,        # a bool is not an address, even when it equals an int
        1,
        -1,
        0x100000000,
        None,
        "0x08292A54",
    ],
)
def test_replacement_policy_refuses_everything_else(bad) -> None:
    layer = (0x082928DC, 0x08292A54)
    with pytest.raises(mb.MapBrowserError):
        mb.validate_cell_replacement(layer, bad)
    with pytest.raises(MapLayoutWriteError):
        validate_chunk_replacement(layer, bad)


def test_writer_refuses_a_null_replaceable_and_a_null_replacement() -> None:
    # A layer whose window is entirely null accepts no replacement at all.
    with pytest.raises(MapLayoutWriteError):
        validate_chunk_replacement((0, 0), 0)


def test_widening_a_layer_vocabulary_is_what_keeps_the_writer_accepting() -> None:
    """The refusal a single-chunk layer sees is the SET, not the predicate.

    Given only its own window the predicate refuses a sibling chunk, which is why
    the paint and editor surfaces have to hand it the map's set; handed that set,
    the same call accepts. This is the one place the widening could silently stop
    reaching the case it exists for.
    """
    own = (0x08292884, 0x08292A54)
    sibling = 0x082928DC
    with pytest.raises(MapLayoutWriteError):
        validate_chunk_replacement(own, sibling)
    assert validate_chunk_replacement(
        legal_chunk_pointers(own, (sibling,)), sibling
    ) == sibling



# --- slot and target classification -----------------------------------------


def test_slot_identity_helpers() -> None:
    slot = _slot()
    assert slot.editable
    assert slot.label == "BG1 · chunk grid 2×2"
    assert slot.ordinal_of(0x082928DC) == 1
    assert slot.ordinal_of(0x08292A54) == 2
    assert slot.ordinal_of(0x08299999) is None
    assert slot.cells_using(0x082928DC) == (0, 2)
    assert slot.cells_using(0x08292AFC) == (3,)
    assert slot.cells_using(0) == ()


def test_slot_with_a_single_chunk_is_read_only() -> None:
    slot = _slot(
        columns=1,
        rows=1,
        pointers=(0x082928DC,),
        reason="a grid of 1 cell(s) using a single chunk",
    )
    assert not slot.editable
    assert slot.label == "BG1 · chunk grid 1×1"
    assert slot.cells_using(0x082928DC) == (0,)


def test_target_reports_editable_slots_and_a_read_only_reason() -> None:
    editable = _slot(1)
    read_only = _slot(
        2,
        classification="static_graphical_terrain_field",
        columns=0,
        rows=0,
        pointers=(),
        choices=(),
        reason="a terrain-field layer, the special graphical form Map 19 uses",
    )
    target = LayoutTarget(map_index=19, name=None, slots=(read_only, editable))
    assert target.editable
    assert [slot.slot for slot in target.editable_slots] == [1]
    assert target.read_only_reason == ""
    assert target.read_only_kind == ""

    none_editable = LayoutTarget(map_index=19, name=None, slots=(read_only,))
    assert not none_editable.editable
    assert "no editable dominant layer" in none_editable.read_only_reason
    assert "terrain-field" in none_editable.read_only_reason
    assert none_editable.read_only_kind == "unsupported"


def test_read_only_kind_separates_unsupported_forms_from_single_chunk_grids() -> None:
    single = _slot(
        0,
        columns=1,
        rows=1,
        pointers=(0x082928DC,),
        reason="a grid of 1 cell(s) using a single chunk",
    )
    unsupported = _slot(
        1,
        classification="static_graphical_screenblock",
        columns=0,
        rows=0,
        pointers=(),
        choices=(),
        reason="a screen-entry layer, not the dominant chunk grid",
    )
    assert LayoutTarget(0, None, (single,)).read_only_kind == "no_alternative"
    assert LayoutTarget(0, None, (unsupported,)).read_only_kind == "unsupported"
    assert LayoutTarget(0, None, (single, unsupported)).read_only_kind == "mixed"
    # A zero-dimension dominant grid is an unsupported grid, not a missing
    # alternative: it has no cells at all.
    zero = _slot(2, classification="dominant_zero_grid", columns=0, rows=0, pointers=(), reason="zero")
    assert LayoutTarget(0, None, (zero,)).read_only_kind == "unsupported"


def test_every_documented_non_dominant_form_has_a_reason() -> None:
    """The read-only vocabulary covers every classification the readers emit."""
    for classification in (
        "absent_placeholder",
        "static_graphical_screenblock",
        "static_graphical_terrain_field",
        "dominant_zero_grid",
        "dominant_partial_zero_grid",
        "unclassified_handler",
    ):
        assert classification in mle._READ_ONLY_FORMS
        assert mle._READ_ONLY_FORMS[classification]


def test_read_only_reasons_read_as_a_sentence_after_the_slot_name() -> None:
    """`LayoutTarget.read_only_reason` composes "BGn is <reason>"; so must they."""
    for classification, reason in mle._READ_ONLY_FORMS.items():
        assert not reason.startswith("the slot"), classification
        assert reason.endswith(tuple("abcdefghijklmnopqrstuvwxyz)")), reason
    slot = LayoutSlot(
        slot=3,
        classification="absent_placeholder",
        handler=0x08007A41,
        grid=LayoutGrid(0, 0),
        cells=(),
        choices=(),
        read_only_reason=mle._READ_ONLY_FORMS["absent_placeholder"],
    )
    reason = LayoutTarget(19, None, (slot,)).read_only_reason
    assert "BG3 is an empty slot holding no layer" in reason


def test_dominant_reason_explains_a_single_chunk_layer() -> None:
    reason = MapLayoutEditor._dominant_read_only_reason(LayoutGrid(1, 1), (0x082928DC,))
    assert "single chunk" in reason
    assert MapLayoutEditor._dominant_read_only_reason(LayoutGrid(2, 2), (1, 2)) == ""
    zero = MapLayoutEditor._dominant_read_only_reason(LayoutGrid(0, 0), ())
    assert "zero dimension" in zero


# --- fail closed -------------------------------------------------------------


def test_editor_refuses_any_non_canonical_image() -> None:
    with pytest.raises(MapLayoutEditError):
        MapLayoutEditor(b"\x00" * 8_388_608)
    with pytest.raises(MapLayoutEditError):
        MapLayoutEditor(b"")


def test_writer_refuses_a_truncated_image() -> None:
    with pytest.raises(MapLayoutWriteError):
        MapLayoutWriter(b"\x00" * 1024)
