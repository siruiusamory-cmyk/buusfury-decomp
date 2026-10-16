"""CQA-27: the layout domain's pending-edit policy, without a GUI.

The Map Browser used to answer "what is staged", "what has been written" and "what
the unsaved count means" inside the widget, so the policy could only be exercised
by building a window. These tests drive the same rules through
`tools.webfoot.map_layout_session`: no Qt, no ROM, no project.

The widget half is pinned by `tests/unit/test_workbench_unsaved_policy.py`, which
still asserts that the shell's one guard reads this same total.
"""

from __future__ import annotations

from tools.webfoot.map_layout_edit import LayoutEdit
from tools.webfoot.map_layout_session import (
    LayoutSession,
    PendingWork,
    staged_changes,
)


def _edit(
    *, map_index: int = 0, layer_slot: int = 0, cell: int = 0, replacement: int = 2
) -> LayoutEdit:
    return LayoutEdit(
        map_index=map_index,
        layer_slot=layer_slot,
        cell=cell,
        original=1,
        replacement=replacement,
        offset=0x1000 + cell * 4,
    )


# --- what counts as a staged change ------------------------------------------


def test_a_staged_value_the_project_already_holds_is_not_a_change():
    """The no-op an Apply must not record, in the one place it is decided."""
    assert staged_changes({1: "A"}, {1: "A"}) == {}
    assert staged_changes({1: "A"}, {1: "B"}) == {1: "A"}
    assert staged_changes({1: "A"}, {}) == {1: "A"}


def test_the_comparison_is_the_projects_value_and_nothing_else():
    staged = {1: "A", 2: "B", 3: "C"}
    committed = {1: "A", 2: "Z"}

    assert staged_changes(staged, committed) == {2: "B", 3: "C"}


# --- the written baseline -----------------------------------------------------


def test_every_paint_is_pending_until_a_write_publishes_it():
    session = LayoutSession()
    edits = (_edit(cell=0), _edit(cell=1, replacement=3))

    assert session.pending_edits(edits) == edits
    assert session.pending(edits).count == 2


def test_a_published_paint_stops_being_pending():
    session = LayoutSession()
    edits = (_edit(cell=0), _edit(cell=1, replacement=3))

    written = session.note_saved(edits)

    assert written.pending_edits(edits) == ()
    assert written.pending(edits) == PendingWork()
    assert written.pending(edits).clean


def test_a_paint_changed_after_it_was_written_is_pending_again():
    """The comparison is by replacement, not by the presence of an edit."""
    edit = _edit(cell=0, replacement=2)
    session = LayoutSession().note_saved((edit,))

    moved = _edit(cell=0, replacement=9)

    assert session.pending_edits((moved,)) == (moved,)
    assert session.pending_edits((edit,)) == ()


def test_a_write_publishes_only_the_edits_it_was_handed():
    """One map's save does not mark another map's paint as written."""
    saved = _edit(map_index=0, cell=0)
    other = _edit(map_index=1, cell=0)

    session = LayoutSession().note_saved((saved,))

    assert session.pending_edits((saved, other)) == (other,)


def test_note_saved_returns_a_new_session():
    """The baseline is replaced, never mutated in place."""
    session = LayoutSession()
    written = session.note_saved((_edit(cell=0),))

    assert session.written == {}
    assert written.written == {(0, 0, 0): 2}
    assert session is not written


def test_discarding_pending_forgets_the_baseline():
    """After a discard the project holds what it held, so nothing is written."""
    session = LayoutSession().note_saved((_edit(cell=0),))

    cleared = session.cleared()

    assert cleared.written == {}
    assert cleared.pending_edits((_edit(cell=0),)) == (_edit(cell=0),)


# --- the total and its noun ---------------------------------------------------


def test_the_total_is_paints_plus_documents_and_structure():
    session = LayoutSession()

    pending = session.pending(
        (_edit(cell=0), _edit(cell=1)),
        paints=(1,),
        changes=(2, 1),
    )

    assert pending.paints == 3
    assert pending.changes == 3
    assert pending.count == 6


def test_paints_only_work_is_a_paint():
    assert PendingWork(paints=2).noun == "paint"


def test_any_other_kind_of_work_makes_it_a_change():
    """An authored chunk is not a paint, and the wording must not say it is."""
    assert PendingWork(paints=2, changes=1).noun == "change"
    assert PendingWork(changes=1).noun == "change"


def test_clean_is_the_absence_of_every_kind():
    assert PendingWork().clean
    assert not PendingWork(paints=1).clean
    assert not PendingWork(changes=1).clean


def test_a_written_paint_leaves_the_other_families_staged():
    """A Save As writes layout edits only; staged documents stay unsaved work."""
    session = LayoutSession()
    edits = (_edit(cell=0),)

    pending = session.note_saved(edits).pending(edits, changes=(1,))

    assert pending.count == 1
    assert pending.noun == "change"
