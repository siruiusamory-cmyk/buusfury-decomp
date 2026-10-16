"""The release 3.1 character rename: the approvals it is derived from, and its identity.

What these tests pin is the thing that makes this rename safe rather than merely mechanical: this
image displays the name "Videl" on TWO different actors, so an approval that carried only the two
spellings would merge them. The retail-side occurrence test is therefore part of the approved value
and is asserted here, as is the identity the builder refuses to disagree with.
"""

from __future__ import annotations

import pytest

from tools.research.build_friend_v3_release31 import RenameError, rename_positions
from tools.research.friend_v3_text_approvals import (
    APPROVED_CHARACTER_RENAMES, APPROVED_RELEASES)


def test_a_mixed_record_renames_only_the_retail_actor_occurrence() -> None:
    """The measured defect. Records 3:2184:2112 and 3:1192:2690 hold BOTH actors, and the retail
    counterpart says so position for position: "my daughter!Videl!" is retail Videl and becomes
    Lazuli, while "I want to see Goten and Trunks compete" - which the built image pads to
    "I want to see Videl and Uub    compete" - is the Goten-turned-Videl actor and must stay Videl.
    An earlier version applied one decision per record with a per-occurrence replace, which renamed
    the wrong one."""
    # The real shapes: the built text is the same length as the retail text because the earlier pass
    # padded the shorter words, so offsets correspond exactly.
    counterpart = ("my daughter!Videl! No! Spit it out!" + "x" * 20
                   + "I want to see Goten and Trunks compete.")
    current = ("my daughter!Videl! No! Spit it out!" + "x" * 20
               + "I want to see Videl and Uub    compete.")
    assert len(current) == len(counterpart)
    text, renamed, kept, unclear = rename_positions(current, counterpart)
    assert (renamed, kept, unclear) == (1, 1, 0)
    assert "my daughter!Lazuli! No!" in text
    assert "I want to see Videl and Uub    compete." in text
    assert text.count("Lazuli") == 1 and text.count("Videl") == 1


def test_an_occurrence_whose_retail_actor_cannot_be_established_is_left() -> None:
    """When the two texts are different lengths the offsets do not correspond, so the actor of an
    occurrence is not established and the tool refuses rather than aligning by guess."""
    with pytest.raises(RenameError):
        rename_positions("call me Videl", "call me Videl and somebody else")


def test_the_rename_carries_the_retail_side_occurrence_test() -> None:
    """The old and new spellings alone are not the approval: the test that fixes WHICH occurrences
    move is, because two actors in this image display the same name."""
    assert len(APPROVED_CHARACTER_RENAMES) == 1
    rename = APPROVED_CHARACTER_RENAMES[0]
    assert (rename.old, rename.new) == ("Videl", "Lazuli")
    assert len(rename.new) == len(rename.old) + 1, "Lazuli is one unit longer, which is why no " \
                                                   "occurrence can be written in place"
    assert "canonical ROM" in rename.retail_test
    assert "Goten" in rename.retail_test, "the Goten-turned-Videl actor must be named in the rule"
    assert rename.relocated_slots == (138, 172, 1066)


def test_the_release_31_identity_matches_the_one_the_builder_asserts() -> None:
    """The builder refuses unless its output equals this digest, so a drifted constant would either
    fail every build or certify the wrong image."""
    release = next(r for r in APPROVED_RELEASES if r.name == "release-3.1")
    assert len(release.base_sha256) == 64
    assert len(release.output_sha256) == 64
    assert release.base_sha256 == "521bd0fa0a8bc198f36430e3419184807e335fa588bd718152996c076a8f15fd"
    assert release.stages == ("character-rename",)
    # The image grows by the container's carried payload plus the three relocated strings.
    assert release.output_bytes > release.base_bytes
    assert release.output_bytes - release.base_bytes == 10169982 - 10146136
