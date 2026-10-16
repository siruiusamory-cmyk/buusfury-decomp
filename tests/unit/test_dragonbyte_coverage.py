"""DRAGONBYTE-Z-DATA-SURFACES-001: the Coverage view over the census.

The census JSON is a read-only input owned by another ticket, so these tests
prove two things about the view and nothing about the file: that every count it
reports is recomputed from `rows` rather than read from `totals`, and that it
adds no state, row or vocabulary of its own.

The recomputation below is written out independently of the census guard test on
purpose. Two implementations of one count that agree are evidence; one
implementation asserted against itself is not.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tools.dragonbyte import coverage

GAMES = ("buus_fury", "logii", "log1")
CANONICAL_PROFILE = "buus_fury_usa_rev0_01c1707f"


@pytest.fixture(scope="module")
def document() -> dict:
    return coverage.load_census()


def test_the_view_counts_equal_the_census_recomputed_from_its_rows(document):
    """Roadmap S6: the coverage view's counts equal the census recomputation."""
    for game_id in GAMES:
        view = coverage.coverage_view(
            document, _profile_for(document, game_id)
        )

        states = document["vocabularies"]["coverage_states"]
        expected = {state: 0 for state in states}
        for row in document["rows"]:
            expected[row["games"][game_id]["state"]] += 1

        assert {group.state: group.cells for group in view.groups} == expected
        assert view.total_rows == len(document["rows"])
        assert view.modelled_editable == (
            expected["FULLY_EDITABLE"] + expected["PARTIALLY_EDITABLE"]
        )
        assert view.modelled_read_only == expected["SEMANTIC_READ_ONLY"]
        assert view.known_but_unsupported == expected["KNOWN_BUT_UNSUPPORTED"]
        assert view.unmapped == expected["UNKNOWN_UNMAPPED"]


def test_the_counts_also_equal_the_published_totals(document):
    """The stored totals are the same answer by a second route, not a source."""
    for game_id in GAMES:
        view = coverage.coverage_view(document, _profile_for(document, game_id))
        published = document["totals"]["by_game"][game_id]

        assert {group.state: group.cells for group in view.groups} == {
            state: published[state] for state in document["vocabularies"]["coverage_states"]
        }


def test_every_state_the_view_reports_is_a_census_state_with_a_product_word(document):
    states = tuple(document["vocabularies"]["coverage_states"])
    view = coverage.coverage_view(document, CANONICAL_PROFILE)

    assert tuple(group.state for group in view.groups) == states
    assert tuple(_word(state) for state in states) == tuple(
        group.word for group in view.groups
    )
    for group in view.groups:
        assert group.sentence
    for row in view.rows:
        assert row.state in states
        assert row.word
        assert row.basis and row.engine_knowledge and row.confidence and row.evidence


def test_the_view_names_the_title_from_the_profiles_published_id(document):
    view = coverage.coverage_view(document, CANONICAL_PROFILE)
    game = coverage.game_for_profile(document, CANONICAL_PROFILE)

    assert game is not None
    assert view.profile_id == CANONICAL_PROFILE
    assert view.game_id == game["id"]
    assert view.title == game["title"]
    assert view.summary().startswith(f"{game['title']}:")


def test_a_profile_the_census_does_not_name_is_refused_rather_than_guessed(document):
    assert coverage.game_for_profile(document, "no_such_profile") is None
    with pytest.raises(coverage.CoverageError):
        coverage.coverage_view(document, "no_such_profile")


def test_reading_the_census_never_writes_it(document):
    path = coverage.census_path()
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    coverage.coverage_view(coverage.load_census(), CANONICAL_PROFILE)

    assert hashlib.sha256(path.read_bytes()).hexdigest() == before


def test_a_missing_census_is_a_named_refusal_rather_than_a_traceback(tmp_path):
    with pytest.raises(coverage.CoverageError):
        coverage.load_census(tmp_path)


def test_the_census_path_is_relative_to_the_repository():
    path = coverage.census_path()

    assert path.is_file()
    assert path == Path(coverage.REPOSITORY_ROOT) / coverage.CENSUS_RELATIVE


def _profile_for(document: dict, game_id: str) -> str:
    for game in document["games"]:
        if game["id"] == game_id:
            return str(game["profile_id"])
    raise AssertionError(game_id)


def _word(state: str) -> str:
    return next(word for token, word, _sentence in coverage.PRODUCT_STATE_WORDS if token == state)
