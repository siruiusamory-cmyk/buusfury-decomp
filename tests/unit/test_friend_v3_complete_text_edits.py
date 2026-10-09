"""FRIEND-V3-COMPLETE-TEXT-PASS-001: the map rule and the relocation guard.

Two pieces of non-trivial logic carry this ticket, and each is tested as a function
rather than against the private friend image:

* `build_friend_v3_complete_map.ruled` decides WHICH words the two word rules may touch.
  It must rename retail `Bulma` to `Tulma` while leaving the displayed name `Bulma`,
  which the rename pass put there for retail `Chi-Chi`, exactly where it is. A blind
  string replacement renames the wrong character, which is the defect this test exists
  to prevent.
* `apply_friend_v3_complete_text_edits.apply_relocations` appends a grown string and
  repoints its one table pointer. It must refuse a site that anything else in the image
  also references by address, because repointing the table would leave that other
  reference pointing at the stale copy.
"""

from __future__ import annotations

from tools.research import apply_friend_v3_complete_text_edits as edits
from tools.research import build_friend_v3_complete_map as build

TABLE_START = 0x0006BCE8
COUNT = 1534
POOL = 0x004FF000
TARGET = 0x00480000
IMAGE_SIZE = 0x00500000
NUL = b"\x00\x00"


def make_image(text: str, slot: int = 134, extra_reference: bool = False) -> bytes:
    """A minimal image whose table slot `slot` names `text` at TARGET."""
    image = bytearray(b"\x00" * IMAGE_SIZE)
    image[POOL:POOL + 2] = NUL
    empty = (POOL + 0x08000000).to_bytes(4, "little")
    for index in range(COUNT):
        at = TABLE_START + index * 4
        image[at:at + 4] = empty
    body = text.encode("utf-16le") + NUL
    image[TARGET:TARGET + len(body)] = body
    address = (TARGET + 0x08000000).to_bytes(4, "little")
    image[TABLE_START + slot * 4:TABLE_START + slot * 4 + 4] = address
    if extra_reference:
        image[0x00400000:0x00400004] = address
    return bytes(image)


def test_retail_bulma_becomes_tulma() -> None:
    text, applied = build.ruled("Bulma's Airship", "Bulma's Airship")
    assert text == "Tulma's Airship"
    assert applied == ("Bulma->Tulma",)


def test_displayed_bulma_from_retail_chi_chi_is_left_alone() -> None:
    """The rename pass put this `Bulma` there; it is Chi-Chi's displayed name."""
    text, applied = build.ruled("Chi-Chi", "Bulma")
    assert text == "Bulma"
    assert applied == ()


def test_saiyaman_becomes_soyman_and_keeps_its_punctuation() -> None:
    assert build.ruled("Saiyaman!", "Saiyaman!")[0] == "Soyman!"
    assert build.ruled("Great Saiyaman", "Great Saiyaman")[0] == "Great Soyman"
    assert build.ruled("Saiyan Race", "Saiyan Race") == ("Saiyan Race", ())


def test_relocation_appends_and_repoints_a_single_reference() -> None:
    image = make_image("Vegito")
    result = edits.apply_relocations(
        image, (edits.RelocatedEdit(134, TARGET, "Vegito", "Tiencha"),))
    grown = result["image"]
    pointer_at = TABLE_START + 134 * 4
    new_address = int.from_bytes(grown[pointer_at:pointer_at + 4], "little")
    new_offset = new_address - 0x08000000
    assert grown[new_offset:new_offset + len("Tiencha".encode("utf-16le"))] == \
        "Tiencha".encode("utf-16le")
    assert len(grown) > len(image)
    assert result["changed"] == list(range(pointer_at, pointer_at + 4))
    assert grown[TARGET:TARGET + len("Vegito".encode("utf-16le"))] == \
        "Vegito".encode("utf-16le")


def test_relocation_refuses_a_site_something_else_also_references() -> None:
    image = make_image("Vegito", extra_reference=True)
    try:
        edits.apply_relocations(
            image, (edits.RelocatedEdit(134, TARGET, "Vegito", "Tiencha"),))
    except edits.FriendTextEditError as exc:
        assert "word-aligned references" in str(exc)
    else:
        raise AssertionError("a twice-referenced site must be refused")


def test_relocation_refuses_a_replacement_that_would_fit_in_place() -> None:
    image = make_image("Gogeta")
    try:
        edits.apply_relocations(
            image, (edits.RelocatedEdit(134, TARGET, "Gogeta", "Yamien"),))
    except edits.FriendTextEditError as exc:
        assert "belongs" in str(exc)
    else:
        raise AssertionError("a fitting replacement belongs to the in-place table")


def test_each_table_carries_the_sites_it_is_for() -> None:
    """SECTION_2 fits its span; SECTION_3 does not, which is why it is separate."""
    for edit in edits.SECTION_2:
        span = len(edit.encoded_current())
        assert len(edit.encoded_replacement()) <= span, edit.site
    for edit in edits.SECTION_3:
        span = len(edit.encoded_current())
        assert len(edit.encoded_replacement()) > span, edit.site
