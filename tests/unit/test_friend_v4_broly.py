"""Release 4A focused tests: the owner-decided swap, its site table and its frozen identity.

These run without the ROM: they pin the things that would silently change the release if someone
edited a constant - which sites move, which stat selector the fights take, that the name edit is a
shrink (so it fits in place), and that the identity the builder refuses to disagree with is the one
recorded as approved.
"""

from __future__ import annotations

from tools.research.build_friend_v4_broly import (
    APPEARANCES, BROLY_STAT_RECORD, BROLY_SPRITE, COPY_SLOTS, NEW_NAME, OLD_NAME, SITES)
from tools.research.friend_v3_text_approvals import APPROVED_RELEASES


def test_each_old_id_gets_its_own_definition_copy() -> None:
    """The ids get COPIES, not the donor definition, and each copy is required to fill the slots the
    scripts can select: resource 490 sets state 12 for the Heaven actor, whose donor definition leaves
    slot 12 empty, so a borrowed definition gave that actor no animation at all."""
    assert COPY_SLOTS[73] == (22,), "the donor leaves the ship actor slot 22 empty"
    assert COPY_SLOTS[98] == (12,), "the donor leaves the Heaven actor slot 12 empty"
    labels = {label for label, _offset, _was, _now in SITES}
    assert not any("character table" in label for label in labels), (
        "the definition pointers are computed addresses now, not static site rows")


def test_the_placed_sites_keep_their_retail_ids() -> None:
    """Scripts find an actor by DEFINITION POINTER, so the id an actor carries must be the id the
    scripts target. Moving the sites to the donor's id made every lookup miss: the Heaven actor's
    resource 490 (98, state 12) and the ship scene's resource 337 (73, natives 71/65) found nothing.
    The art change rides on the character table words instead."""
    labels = {label for label, _offset, _was, _now in SITES}
    assert not any("sprite" in label and "stat" not in label for label in labels), (
        "no placed site's sprite id may move")
    stats = [(label, was, now) for label, _offset, was, now in SITES]
    assert len(stats) == 2, "exactly the two fight stat selectors change"


def test_both_fights_take_brolys_own_stat_selector() -> None:
    """Broly's chapter-6 fight is map 390 slot 0, measured with stat selector 10, so both Dabura
    fights must point there and no stat record may be retuned."""
    stats = [(label, was, now) for label, _offset, was, now in SITES if "stat selector" in label]
    assert len(stats) == 2
    for label, was, now in stats:
        assert was == 18, f"{label} does not start from Dabura's selector"
        assert now == BROLY_STAT_RECORD == 10


def test_the_appearances_keep_their_ids_and_take_the_portrait() -> None:
    """The scanner pairs an actor's sprite id with its stat index, so the appearance record's id must
    stay as the actor carries it; what changes is the portrait the owner sees and the fight's stat."""
    labels = {label for label, _offset, _was, _now in APPEARANCES}
    assert not any("sprite" in label for label in labels), (
        "no appearance sprite id may move")
    for label, _offset, _was, now in APPEARANCES:
        if "portrait" in label:
            assert now == 16, "the donor's portrait slot is 16"
    assert any("stat 18 -> Broly 10" in label for label in labels)


def test_the_name_edit_is_a_shrink_so_it_fits_in_place() -> None:
    """A longer wording would force the pointer-relocation route; the owner's chosen name is
    shorter, which is why the builder can write it in place and leave the tail."""
    assert len(NEW_NAME) < len(OLD_NAME)


def test_the_release_identity_is_the_approved_one() -> None:
    release = next(record for record in APPROVED_RELEASES if record.name == "release-4a")
    assert release.base_sha256 == "f5c9648bbf7a9b448d801866cc775eb76abd270f7c16fb93d4e01630ef236201"
    assert release.output_sha256 == "a21c1e27f7b4f04cbe6952d70eb102b350adac04e6eaba106fa10e2b90a55021"
    assert release.output_bytes == 10170720 and release.base_bytes == 10169982
