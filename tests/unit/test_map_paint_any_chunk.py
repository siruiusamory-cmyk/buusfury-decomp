"""Unit tests for the widened chunk-replacement rule, over synthetic records.

No ROM and no Qt: the legal pointer set, the one predicate, the brush vocabulary
and the read-only reason are pure functions of records, so CI exercises the rule
the write, preview and paint paths share without a canonical image. The
ROM-coupled proofs - the one-chunk layer becoming paintable, the round trip and
provenance - live in ``tests/integration/test_map_tile_paint_rom.py`` and
``tests/integration/test_map_layout_editor_rom.py``.
"""

from __future__ import annotations

import pytest

from tools.export import map_browser as mb
from tools.webfoot import map_paint as mp
from tools.webfoot.formats import map_graphics as mg
from tools.webfoot.map_layout_write import (
    MapLayoutWriteError,
    legal_chunk_pointers,
    validate_chunk_replacement,
)

#: Three chunk addresses and one that no record here uses.
FIRST = 0x08292884
SECOND = 0x082928DC
THIRD = 0x08292A54
FOREIGN = 0x08179A50


def _record(slot: int, window: tuple[int, ...], *, columns: int = 2, rows: int = 1):
    return mg.LayerRecord(
        slot=slot,
        address=0x08340000 + 0x100 * slot,
        handler=mg.DOMINANT_LAYER_HANDLER,
        chunk_x=columns,
        chunk_y=rows,
        chunk_addresses=window,
        null_chunk_count=sum(1 for pointer in window if pointer == 0),
        terrain_x=0,
        terrain_y=0,
    )


# --- the legal set -----------------------------------------------------------


def test_the_legal_set_is_the_maps_layers_in_order_without_duplicates_or_nulls():
    own = (FIRST, SECOND, 0, FIRST)
    sibling = (SECOND, THIRD, 0)
    assert legal_chunk_pointers(own, sibling) == (FIRST, SECOND, THIRD)
    # The first group leads, so a caller can keep an edited layer's own chunks at
    # the low ordinals an existing project already stores.
    assert legal_chunk_pointers(sibling, own) == (SECOND, THIRD, FIRST)
    assert legal_chunk_pointers() == ()
    assert legal_chunk_pointers((0, 0)) == ()


# --- the one predicate -------------------------------------------------------


def test_a_sibling_layers_chunk_is_legal_for_the_layer_being_edited():
    """The widening itself: a chunk from another layer of the same map."""
    allowed = legal_chunk_pointers((FIRST,), (SECOND, THIRD))
    assert validate_chunk_replacement(allowed, THIRD) == THIRD
    assert validate_chunk_replacement(allowed, FIRST) == FIRST


@pytest.mark.parametrize(
    "bad",
    [
        0,           # the null pointer the engine reads as unoccupied
        FOREIGN,     # a real chunk this map does not use
        True,        # a bool is not an address, even when it equals an int
        1,
        -1,
        0x100000000,
        None,
        "0x08292A54",
    ],
)
def test_the_predicate_still_refuses_everything_else(bad):
    allowed = legal_chunk_pointers((FIRST, SECOND))
    with pytest.raises(MapLayoutWriteError):
        validate_chunk_replacement(allowed, bad)
    with pytest.raises(mb.MapBrowserError):
        mb.validate_cell_replacement(allowed, bad)


def test_the_predicates_refusal_names_the_map_not_the_layer():
    with pytest.raises(MapLayoutWriteError) as excinfo:
        validate_chunk_replacement((FIRST,), FOREIGN)
    assert "dominant layer of the same map" in str(excinfo.value)
    assert "same dominant layer" not in str(excinfo.value)


def test_an_empty_legal_set_accepts_nothing():
    with pytest.raises(MapLayoutWriteError, match="dominant layer of the same map"):
        validate_chunk_replacement((), FIRST)
    with pytest.raises(MapLayoutWriteError, match="null chunk pointer"):
        validate_chunk_replacement((), 0)


# --- the brush vocabulary ----------------------------------------------------


def _cells(pointers: tuple[int, ...], *, columns: int = 2):
    return tuple(
        mp.PaintCell(
            cell=index,
            column=index % columns,
            row=index // columns,
            pointer=pointer,
            offset=0,
        )
        for index, pointer in enumerate(pointers)
    )


def test_the_vocabulary_leads_with_the_layers_own_chunks_then_its_siblings():
    record = _record(0, (SECOND, 0))
    records = (record, _record(1, (FIRST, THIRD, SECOND)), _record(2, (0,)))
    vocabulary = mp._vocabulary(record, records, _cells(record.chunk_addresses))
    assert [chunk.pointer for chunk in vocabulary] == [SECOND, FIRST, THIRD]
    assert [chunk.ordinal for chunk in vocabulary] == [1, 2, 3]
    # The borrowed entries say which record they came from, and how many cells of
    # the edited layer hold them.
    assert vocabulary[0].source_slot is None
    assert vocabulary[1].source_slot == 1
    assert vocabulary[2].source_slot == 1
    assert all(chunk.cell_count == 0 for chunk in vocabulary[1:])


def test_a_sibling_that_repeats_the_layers_own_chunk_does_not_add_an_entry():
    record = _record(0, (FIRST, SECOND))
    records = (record, _record(1, (SECOND, FIRST, SECOND)))
    vocabulary = mp._vocabulary(record, records, _cells(record.chunk_addresses))
    assert [chunk.pointer for chunk in vocabulary] == [FIRST, SECOND]
    assert all(chunk.source_slot is None for chunk in vocabulary)


def test_the_label_shows_the_source_record_only_for_a_borrowed_chunk():
    assert mp.PaintChunk(ordinal=1, pointer=FIRST, cell_count=4).label == "Chunk 1"
    borrowed = mp.PaintChunk(ordinal=5, pointer=FIRST, cell_count=0, source_slot=2)
    assert borrowed.label == "Chunk 5 \u00b7 BG2"


# --- the read-only reason ----------------------------------------------------


def test_a_single_chunk_vocabulary_is_the_only_reason_a_grid_has_no_brush():
    one = (mp.PaintChunk(ordinal=1, pointer=FIRST, cell_count=1),)
    reason = mp.MapPainter._read_only_reason(1, 1, one)
    assert "single chunk" in reason
    assert mp.MapPainter._read_only_reason(1, 1, one + (
        mp.PaintChunk(ordinal=2, pointer=SECOND, cell_count=0, source_slot=1),
    )) == ""


def test_a_zero_dimension_grid_is_refused_before_the_vocabulary_is_considered():
    for columns, rows, vocabulary in ((0, 1, ()), (1, 0, ()), (0, 0, ())):
        reason = mp.MapPainter._read_only_reason(columns, rows, vocabulary)
        assert "zero dimension" in reason


# --- the source record on the editing surface --------------------------------


def test_the_layout_slot_carries_the_source_of_each_choice():
    """A chooser over the widened set must be able to say whose record a row is.

    ``LayoutSlot.choices`` is plain pointers, so the layer each fact comes from
    rides beside them in the same order. This is what lets the surface show a
    borrowed chunk's source, which the capability entry publishes.
    """
    from tools.webfoot.map_layout_edit import LayoutSlot

    slot = LayoutSlot(
        slot=1, classification="x", handler=0, grid=None, cells=(),
        choices=(FIRST, SECOND, THIRD), sources=(1, 2, 2), read_only_reason="",
    )
    assert slot.source_of(FIRST) == 1
    assert slot.source_of(SECOND) == 2
    assert slot.source_of(FOREIGN) is None
    # Empty for this layer's own chunk, naming the sibling otherwise, in the same
    # shape PaintChunk.label uses, so the model and the surface agree.
    assert slot.borrowed_note(FIRST) == ""
    assert slot.borrowed_note(SECOND) == " \u00b7 BG2"
    assert slot.borrowed_note(FOREIGN) == ""


def test_a_slot_without_sources_still_answers_without_raising():
    """Every caller written before this change keeps working."""
    from tools.webfoot.map_layout_edit import LayoutSlot

    slot = LayoutSlot(
        slot=0, classification="x", handler=0, grid=None, cells=(),
        choices=(FIRST,), read_only_reason="a reason",
    )
    assert slot.sources == ()
    assert slot.source_of(FIRST) is None
    assert slot.borrowed_note(FIRST) == ""
    assert not slot.editable


# --- the window ordinal, counted per distinct pointer ------------------------


def test_window_ordinals_counts_distinct_pointers_in_first_appearance_order():
    """The one numbering: a repeated pointer keeps its first-appearance ordinal.

    Counting occurrences instead made a choice resolve to a DIFFERENT chunk once the
    sets were widened, because a window may reference one chunk many times while a
    template names the chunk. Measured on the canonical image: 43 choices wrong.
    """
    from tools.webfoot.map_layout_write import window_ordinals

    assert window_ordinals(()) == {}
    assert window_ordinals((0, 0, 0)) == {}
    assert window_ordinals((FIRST,)) == {FIRST: 1}
    # A repeat does NOT take a new ordinal and does not shift the ones after it.
    assert window_ordinals((FIRST, FIRST, SECOND)) == {FIRST: 1, SECOND: 2}
    assert window_ordinals((FIRST, SECOND, FIRST, THIRD)) == {
        FIRST: 1, SECOND: 2, THIRD: 3,
    }
    # Nulls are skipped rather than numbered, as everywhere else.
    assert window_ordinals((0, FIRST, 0, SECOND)) == {FIRST: 1, SECOND: 2}


def test_the_window_ordinal_agrees_with_the_legal_set():
    """One rule for both, so a template ordinal and a stored ordinal cannot drift."""
    from tools.webfoot.map_layout_write import legal_chunk_pointers, window_ordinals

    window = (FIRST, FIRST, SECOND, 0, THIRD, SECOND)
    legal = legal_chunk_pointers(window)
    ordinals = window_ordinals(window)
    assert legal == tuple(ordinals)
    assert [ordinals[p] for p in legal] == [1, 2, 3]
