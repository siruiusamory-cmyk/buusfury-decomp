"""How a state is shown: one icon, one glyph, one word, one marker shape.

A red-green colourblind reader must be able to read every state, so no state is
carried by hue. The theme supplies the colours; this module supplies the three
channels that do not depend on them, and a test asserts they stay distinct.
"""

from __future__ import annotations

from dataclasses import dataclass

from .session import State


@dataclass(frozen=True, slots=True)
class Presentation:
    """One state, as a reader sees it without relying on colour."""

    #: A Tabler icon name in the bundled set. Drawn beside the word, never instead.
    icon: str
    #: A glyph that needs no icon engine, for text-only surfaces and for a test.
    glyph: str
    #: The word. Always shown, even when the row is narrow.
    word: str
    #: How the row's marker is drawn: the shape channel.
    marker: str


#: The five primary states. `marker` distinguishes them by geometry as well as by
#: word: solid, dashed, a filled block, a double rule, and nothing at all.
PRESENTATION: dict[State, Presentation] = {
    State.UNCHANGED: Presentation("minus", "\u00b7", "UNCHANGED", "none"),
    State.EDITED: Presentation("pencil", "\u270e", "EDITED", "solid"),
    State.WILL_MOVE: Presentation("arrow-up-right", "\u2197", "WILL MOVE", "dashed"),
    State.REFUSED: Presentation("square-x", "\u2612", "REFUSED", "block"),
    State.BASE_CHANGED: Presentation("refresh", "\u2260", "BASE CHANGED", "double"),
    #: The record's row count changed, so its rows no longer line up with it. The word says
    #: what to do rather than only what is wrong, and the marker is the one shape left.
    State.RESTRUCTURED: Presentation("filter", "\u25a4", "RECORD RESTRUCTURED", "hatch"),
}

#: The auxiliary marker. It answers a different question from the primary state -
#: whether this image already differs from the original game - so both can be true
#: at once and neither is allowed to hide the other.
AUXILIARY = Presentation("chevron-down", "\u2260", "DIFFERS FROM RETAIL", "aux")


def presentation(state: State) -> Presentation:
    return PRESENTATION[state]


def label(state: State) -> str:
    """The text a row cell or a tooltip shows: the glyph and the word together."""
    entry = PRESENTATION[state]
    return f"{entry.glyph} {entry.word}"


def auxiliary_label() -> str:
    return f"{AUXILIARY.glyph} {AUXILIARY.word}"
