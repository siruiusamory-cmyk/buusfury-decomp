"""The layout domain's pending-edit policy, outside the widget. CQA-27.

The Map Browser used to answer four questions inside its own class: what a staged
value would change, what a write has published, how much work is unsaved, and what
that work is called. This module owns those answers, so the policy is testable
without a GUI and one authority decides them rather than the 7,500-line widget
that also owns layout, painting, mouse handling and the mode strip.

What stays where it is: the staged mappings are the caller's. This object is built
from them and holds the one thing a caller cannot derive, the written baseline the
last Save As or Apply published. `staged_changes` is the comparison every staged
family already made for itself; it lives here so the six families cannot drift.

A key whose staged and committed values agree is not a change: re-writing it would
rewrite an identical document, which is the no-op an Apply must not record.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Hashable, Iterable, Mapping, TypeVar

from .map_layout_edit import LayoutEdit

Key = TypeVar("Key", bound=Hashable)
Value = TypeVar("Value")

#: What names one painted cell across every map of one image.
CellKey = tuple[int, int, int]


def staged_changes(
    staged: Mapping[Key, Value], committed: Mapping[Key, Value]
) -> dict[Key, Value]:
    """The staged entries that would actually change the project.

    The project's own value is the comparison, not the presence of a staged one:
    a cell staged back to what the project already holds is not work, and a batch
    that rewrote it would write a document identical to the one on disk.
    """
    return {
        key: value for key, value in staged.items() if committed.get(key) != value
    }


def _cell_key(edit: LayoutEdit) -> CellKey:
    return (edit.map_index, edit.layer_slot, edit.cell)


@dataclass(frozen=True, slots=True)
class PendingWork:
    """One session's unsaved work: how much there is, and what to call it.

    `paints` and `changes` are separate because the wording differs and the count
    does not: an author who staged one cell paint and one authored chunk has two
    unsaved pieces of work, and a summary that called them two paints would be
    wrong about the more severe half.
    """

    paints: int = 0
    changes: int = 0

    @property
    def count(self) -> int:
        """Every staged piece of work, whatever kind it is."""
        return self.paints + self.changes

    @property
    def noun(self) -> str:
        """What to call it: a paint only while paints are all there is."""
        return "change" if self.changes else "paint"

    @property
    def clean(self) -> bool:
        """Nothing is staged, so a destructive transition has nothing to lose."""
        return self.count == 0


@dataclass(frozen=True, slots=True)
class LayoutSession:
    """The layout domain's session: the written set, and what is pending on it.

    `written` is `(map index, layer slot, cell) -> replacement`, the values a Save
    As or an Apply has published. A painted edit whose replacement differs from it
    is unsaved work; a map, layer or cell the project never wrote has no entry, so
    a paint on it is unsaved from the first gesture.
    """

    written: Mapping[CellKey, int] = field(default_factory=dict)

    def note_saved(self, edits: Iterable[LayoutEdit]) -> "LayoutSession":
        """The session after `edits` are the written set.

        Called with the edits that were written, not with the editor's state, so
        the baseline is the set the write was made from even if the editor has
        moved on.
        """
        return replace(self, written={_cell_key(edit): edit.replacement for edit in edits})

    def cleared(self) -> "LayoutSession":
        """The session after the pending work is discarded.

        The baseline goes with it: "discard pending" leaves the project holding
        what it held, so no painted value is written any more.
        """
        return replace(self, written={})

    def pending_edits(self, edits: Iterable[LayoutEdit]) -> tuple[LayoutEdit, ...]:
        """The painted edits no write has published yet."""
        return tuple(
            edit for edit in edits if self.written.get(_cell_key(edit)) != edit.replacement
        )

    def pending(
        self,
        edits: Iterable[LayoutEdit],
        *,
        paints: Iterable[int] = (),
        changes: Iterable[int] = (),
    ) -> PendingWork:
        """What is unsaved: this session's paints, plus the caller's own families.

        `paints` and `changes` are one count per staged family this object does not
        hold. A paint is a staged cell value; a change is a staged document or a
        structural edit, which is work of another kind and is named as such. The
        caller names each family where it lives rather than sending one number, so
        a family that stops being staged cannot be counted by accident.
        """
        return PendingWork(
            paints=len(self.pending_edits(edits)) + sum(paints),
            changes=sum(changes),
        )
