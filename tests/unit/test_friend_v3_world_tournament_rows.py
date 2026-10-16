"""The World Tournament release's own claims, on the row table rather than on a ROM.

What a real image check cannot see is an accident in the row table itself: a dropped row, a
duplicated record key, a shortened wording, or a missing row 18. These assertions are cheap and
they fail before a build starts.
"""

from __future__ import annotations

from tools.research.build_friend_v3_world_tournament_split import (
    OWNER_ROWS, WT18_NEW, WT18_OLD, WT18_RECORD)

#: The owner's eighteen rows as they must read after the record's own control unit is applied.
#: This map is the check: every entry is asserted against the table, so a shortened or altered
#: wording on ANY row fails here, not only on the three sampled before.
OWNER_WORDING = {
    "3:7406:136": "Hey sis, if you win the tournament, what do you think you'll get with the "
                  "prize Zeni?",
    "3:7542:42": "Uh, tons of okonomiyaki, I guess!",
    "3:7584:80": "Sheesh, Videl! How are you not fat?",
    "3:7664:60": "EXCUSE ME?! What are you going to get then?",
    "3:7724:72": "Candy. Lots and lots of candy.",
    "3:7796:204": "And you call me fat. Hey, isn't that kind of meta?",
    "3:8000:214": "Hey, half pint! We don't take too kindly to your folk around here.",
    "3:8214:118": "Huh? Do you mean brown people?",
    "3:8332:218": "What?! No! My mom may be racist, but I'm not! Geez, I meant adopted kids!",
    "3:8550:414": None,
    "3:8964:148": None,
    "3:9112:62": "You really made me look bad earlier.",
    "3:9174:114": "Bruh. You were still totally a dick.",
    "3:9288:282": "That's my baby Idasa down there! Oooooo! Idasa! I wish they would match "
                  "Idasa up with a whiter kid! This is a disgrace!",
    "3:9570:92": None,
    "3:9662:116": "Get him, Uub! You make that boy sorry his mom is racist!",
    "3:9778:114": "Noooo! My baby! That was unfair! That thing cheated!",
}


def test_every_row_names_a_unique_record_identity() -> None:
    keys = [key for key, _approved in OWNER_ROWS]
    assert len(keys) == 17, "the owner's table names seventeen rows before row 18"
    assert len(set(keys)) == len(keys), "a record identity appears twice"
    for key in keys:
        selector, start, length = key.split(":")
        assert int(selector) == 3 and int(start) % 2 == 0 and int(length) % 2 == 0
    assert WT18_RECORD not in keys


def test_row_eighteen_is_planned_and_is_not_an_owner_row() -> None:
    # Row 18 arrives as a passage replacement, so it is not in OWNER_ROWS; a plan that forgot
    # it would still pass the row-table test above without this assertion.
    assert WT18_RECORD == "3:9892:486"
    assert WT18_RECORD not in [key for key, _approved in OWNER_ROWS]


def test_every_approved_wording_is_the_owner_s_exactly() -> None:
    table = dict(OWNER_ROWS)
    assert set(table) == set(OWNER_WORDING)
    for key, text in OWNER_WORDING.items():
        assert table[key] == text, f"{key}: the table's wording differs from the owner's"
    unchanged = [key for key, text in table.items() if text is None]
    assert unchanged == ["3:8550:414", "3:8964:148", "3:9570:92"]


def test_row_eighteen_replaces_only_the_intended_passage() -> None:
    # The pad inside "Uub    and" is what the record actually reads, so the passage that is
    # matched must carry it or nothing would be replaced at all.
    assert "Uub    and" in WT18_OLD
    assert WT18_NEW.startswith("Championship between adopted siblings, ten-year-old Uub and ")
    assert "sixteen-year-old Videl!" in WT18_NEW
    assert "eight-year-old" not in WT18_NEW and "seven-year-old" not in WT18_NEW
