"""Release 4A focused tests: the owner-decided swap, its site table and its frozen identity.

These run without the ROM: they pin the things that would silently change the release if someone
edited a constant - which sites move, which stat selector the fights take, that the name edit is a
shrink (so it fits in place), and that the identity the builder refuses to disagree with is the one
recorded as approved.
"""

from __future__ import annotations

from tools.research.build_friend_v4_broly import (
    APPEARANCES, BROLY_STAT_RECORD, NEW_NAME, OLD_NAME, SITES)
from tools.research.friend_v3_text_approvals import APPROVED_RELEASES


def test_the_character_table_is_what_covers_the_whole_corpus() -> None:
    """The two ids are repointed in the character table, which is the mechanism that covers cutscenes
    and every spawn the census cannot enumerate; without them the three type-4 cutscene spawns that
    push sprite 73 would still draw the old actor."""
    labels = {label for label, _offset, _was, _now in SITES}
    assert any("character table id 73" in label for label in labels)
    assert any("character table id 98" in label for label in labels)
    for label, _offset, was, now in SITES:
        if "character table" in label:
            assert was in (0x086AB24C, 0x086AC6A4), "does not start from the old actor definition"
            assert now == 0x086A9B78, "must resolve to Broly own definition"


def test_every_draw_site_moves_from_a_dabura_sprite_to_broly() -> None:
    """The census found five Dabura sites (sprite 73 four times, 98 once). Every one must be here,
    or the 'Broly everywhere' claim is false, and no site may keep a Dabura sprite."""
    sprite_sites = {"map207 slot4 sprite (ship fight, sprite 73 -> 38)",
                    "map32 slot42 sprite (other Dabura fight, 73 -> 38)",
                    "map206 slot3 sprite (ship scene, 73 -> 38)",
                    "map207 slot3 sprite (ship scene, 73 -> 38)",
                    "map451 slot0 sprite (Heaven form, 98 -> 38)"}
    labels = {label for label, _offset, _was, _now in SITES}
    assert sprite_sites <= labels
    for label, _offset, was, now in SITES:
        if label in sprite_sites:
            assert was in (73, 98), f"{label} does not start from a Dabura sprite"
            assert now == 38, f"{label} does not become Broly"


def test_both_fights_take_brolys_own_stat_selector() -> None:
    """Broly's chapter-6 fight is map 390 slot 0, measured with stat selector 10, so both Dabura
    fights must point there and no stat record may be retuned."""
    stats = [(label, was, now) for label, _offset, was, now in SITES if "stat selector" in label]
    assert len(stats) == 2
    for label, was, now in stats:
        assert was == 18, f"{label} does not start from Dabura's selector"
        assert now == BROLY_STAT_RECORD == 10


def test_the_appearances_take_brolys_sprite_and_portrait() -> None:
    wanted = {"appearance 28 sprite 73 -> 38", "appearance 28 portrait 24 -> 16",
              "appearance 29 sprite 98 -> 38", "appearance 29 portrait 32 -> 16"}
    labels = {label for label, _offset, _was, _now in APPEARANCES}
    assert wanted <= labels
    for label, _offset, _was, now in APPEARANCES:
        if "portrait" in label:
            assert now == 16, "Broly's portrait slot is 16"


def test_the_name_edit_is_a_shrink_so_it_fits_in_place() -> None:
    """A longer wording would force the pointer-relocation route; the owner's chosen name is
    shorter, which is why the builder can write it in place and leave the tail."""
    assert len(NEW_NAME) < len(OLD_NAME)


def test_the_release_identity_is_the_approved_one() -> None:
    release = next(record for record in APPROVED_RELEASES if record.name == "release-4a")
    assert release.base_sha256 == "f5c9648bbf7a9b448d801866cc775eb76abd270f7c16fb93d4e01630ef236201"
    assert release.output_sha256 == "569f39345e14c154a7d8bd3ebc30fa436db49db393942975cd70208b8ee386b4"
    assert release.output_bytes == release.base_bytes == 10169982
