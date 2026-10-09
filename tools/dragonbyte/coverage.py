"""The `Coverage` view: the census, read, grouped and counted, never restated.

The census JSON under ``docs/research`` is normative and read-only. It is owned
by its own ticket; this module is a *view* over it, which means three things and
nothing else:

* it reads the file and invents no row, no state and no word the file does not
  already carry;
* every count here is recomputed from ``rows`` - the ``totals`` block is never
  read - so a view that disagrees with the census is a defect in this module
  rather than a disagreement between two stored numbers;
* the six support states keep the census's own tokens, paired with the product's
  own user word for each, which is the pairing the specification already fixes.
  There is no second vocabulary and no second partition.

The title shown is selected by the open image's own profile id: the census
publishes a ``profile_id`` per title, so the mapping is a lookup rather than a
guess about which game a profile is.

No Qt is imported: a test reads the whole view with no window open.
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

#: The census, relative to the repository root. A path, not an absolute
#: location: this application is run from a checkout, and the census travels
#: with the repository it describes.
CENSUS_RELATIVE = Path("docs") / "research" / "rom_editor_coverage.json"

#: The repository root, derived from this file's own location.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: Census state -> the product's user word and its one sentence, from the
#: specification's support model. The census token is the key on purpose: the
#: tokens are the authority and this table adds no state of its own.
PRODUCT_STATE_WORDS: tuple[tuple[str, str, str], ...] = (
    ("FULLY_EDITABLE", "Editable", "You can change this."),
    (
        "PARTIALLY_EDITABLE",
        "Editable with limits",
        "You can change this, and something stays fixed.",
    ),
    ("SEMANTIC_READ_ONLY", "Read-only", "The product can show you this and cannot change it."),
    (
        "KNOWN_BUT_UNSUPPORTED",
        "Not supported yet",
        "It is a real thing in the game and there is no model for it yet.",
    ),
    ("UNKNOWN_UNMAPPED", "Not mapped", "This exists and its meaning is not established yet."),
    (
        "N_A",
        "Not in this game",
        "The evidence says this does not exist in this title.",
    ),
)

_WORDS = {state: (word, sentence) for state, word, sentence in PRODUCT_STATE_WORDS}


class CoverageError(ValueError):
    """The census could not be read or does not carry the title asked for."""


@dataclass(frozen=True, slots=True)
class CoverageGroup:
    """One census state and how many (row, game) cells carry it, for one title."""

    state: str
    word: str
    sentence: str
    cells: int


@dataclass(frozen=True, slots=True)
class CoverageRow:
    """One census row as this title's evidence describes it."""

    row_id: str
    name: str
    area: str
    state: str
    word: str
    basis: str
    engine_knowledge: str
    confidence: str
    evidence: str


@dataclass(frozen=True, slots=True)
class CoverageView:
    """One title's coverage, counted from the census rows themselves."""

    game_id: str
    title: str
    profile_id: str
    groups: tuple[CoverageGroup, ...]
    rows: tuple[CoverageRow, ...]

    @property
    def total_rows(self) -> int:
        return len(self.rows)

    def count(self, state: str) -> int:
        """The cells this title carries for one census state."""
        return next((group.cells for group in self.groups if group.state == state), 0)

    @property
    def modelled_editable(self) -> int:
        """Cells a person can change: the two editable states."""
        return self.count("FULLY_EDITABLE") + self.count("PARTIALLY_EDITABLE")

    @property
    def modelled_read_only(self) -> int:
        """Cells with a model that permits no change."""
        return self.count("SEMANTIC_READ_ONLY")

    @property
    def known_but_unsupported(self) -> int:
        return self.count("KNOWN_BUT_UNSUPPORTED")

    @property
    def unmapped(self) -> int:
        return self.count("UNKNOWN_UNMAPPED")

    @property
    def not_in_this_game(self) -> int:
        return self.count("N_A")

    def summary(self) -> str:
        """One line naming what is modelled, unsupported and unmapped."""
        return (
            f"{self.title}: {self.modelled_editable} of {self.total_rows} rows editable, "
            f"{self.modelled_read_only} read-only, "
            f"{self.known_but_unsupported} known but unsupported, "
            f"{self.unmapped} unmapped, {self.not_in_this_game} not in this game"
        )


def census_path(root: Path | None = None) -> Path:
    """Where the census lives, from the repository root or an override."""
    return Path(root or REPOSITORY_ROOT) / CENSUS_RELATIVE


def load_census(root: Path | None = None) -> dict[str, Any]:
    """Read the census JSON. Never writes it, never repairs it."""
    path = census_path(root)
    try:
        with io.open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError) as exc:
        raise CoverageError(f"{path}: the census could not be read: {exc}") from exc
    if not isinstance(document, dict) or "rows" not in document:
        raise CoverageError(f"{path}: the census carries no rows")
    return document


def game_for_profile(
    document: Mapping[str, Any], profile_id: str
) -> dict[str, Any] | None:
    """The census title whose published profile id is `profile_id`, or None.

    A profile the census does not name is not guessed at: the caller is told
    there is no coverage entry rather than shown another title's numbers.
    """
    for game in document.get("games", ()):
        if game.get("profile_id") == profile_id:
            return dict(game)
    return None


def coverage_view(
    document: Mapping[str, Any], profile_id: str
) -> CoverageView:
    """One title's coverage view, every count recomputed from the rows.

    `totals` is deliberately not consulted. The census's own guard test already
    proves the published totals equal this recomputation, so reading the stored
    numbers here would be a second route to one answer and would hide a view
    that counted something else.
    """
    game = game_for_profile(document, profile_id)
    if game is None:
        raise CoverageError(
            f"the census names no title for profile {profile_id!r}, so there is "
            "nothing to report for the open image"
        )
    game_id = str(game["id"])
    states = tuple(document["vocabularies"]["coverage_states"])
    cells = {state: 0 for state in states}
    rows: list[CoverageRow] = []
    for row in document["rows"]:
        cell = row["games"][game_id]
        state = cell["state"]
        if state not in cells:
            raise CoverageError(
                f"{row['id']}: {state!r} is not a state the census vocabulary declares"
            )
        cells[state] += 1
        word = _WORDS.get(state, (state, ""))[0]
        rows.append(
            CoverageRow(
                row_id=row["id"],
                name=row["name"],
                area=row["area"],
                state=state,
                word=word,
                basis=cell["basis"],
                engine_knowledge=cell["engine_knowledge"],
                confidence=cell["confidence"],
                evidence=row["evidence_authority"],
            )
        )
    groups = tuple(
        CoverageGroup(
            state=state,
            word=_WORDS[state][0],
            sentence=_WORDS[state][1],
            cells=cells[state],
        )
        for state in states
    )
    return CoverageView(
        game_id=game_id,
        title=str(game["title"]),
        profile_id=str(game["profile_id"]),
        groups=groups,
        rows=tuple(sorted(rows, key=lambda item: (item.area, item.row_id))),
    )
