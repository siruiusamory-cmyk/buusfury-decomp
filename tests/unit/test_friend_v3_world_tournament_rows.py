"""The World Tournament release's own claims, on the row table rather than on a ROM.

What a real image check cannot see is an accident in the row table itself: a dropped row, a
duplicated record key, or an approved wording that was quietly shortened. These assertions are
cheap and they fail before a build starts.
"""

from __future__ import annotations

from tools.research.build_friend_v3_world_tournament_split import (
    OWNER_ROWS, WT18_NEW, WT18_OLD, WT18_RECORD)


def test_every_row_names_a_unique_record_identity() -> None:
    keys = [key for key, _approved in OWNER_ROWS]
    assert len(keys) == 17, "the owner's table names seventeen rows before row 18"
    assert len(set(keys)) == len(keys), "a record identity appears twice"
    for key in keys:
        selector, start, length = key.split(":")
        assert int(selector) == 3 and int(start) % 2 == 0 and int(length) % 2 == 0
    assert WT18_RECORD not in keys


def test_three_rows_are_the_owner_s_no_change_rows() -> None:
    unchanged = [key for key, approved in OWNER_ROWS if approved is None]
    assert unchanged == ["3:8550:414", "3:8964:148", "3:9570:92"]


def test_approved_wordings_are_the_owner_s_and_not_shortened() -> None:
    approved = {key: text for key, text in OWNER_ROWS}
    assert approved["3:7406:136"] == (
        "Hey sis, if you win the tournament, what do you think you'll get with the prize "
        "Zeni?")
    assert approved["3:8332:218"] == (
        "What?! No! My mom may be racist, but I'm not! Geez, I meant adopted kids!")
    assert approved["3:9288:282"].endswith("This is a disgrace!")


def test_row_eighteen_replaces_only_the_intended_passage() -> None:
    # The pad inside "Uub    and" is what the record actually reads, so the passage that is
    # matched must carry it or nothing would be replaced at all.
    assert "Uub    and" in WT18_OLD
    assert WT18_NEW.startswith("Championship between adopted siblings, ten-year-old Uub and ")
    assert "sixteen-year-old Videl!" in WT18_NEW
