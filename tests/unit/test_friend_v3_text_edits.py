"""FRIEND-V3-CONTENT-PASS-001: the STEP 3.1 span writer refuses what it must.

Four refusals carry the tool's core safety property, and each is tested against a
synthetic pool rather than the friend image. The refusals added to close independent
review findings - a table-named string starting inside the written span, a span two
table slots alias, a slot outside the table, and a report path equal to the base - are
NOT covered here yet; they are recorded as outstanding in the implementation record.

* a base whose digest is not the declared one;
* a site that does not hold the text the edit replaces;
* a replacement longer than its site's span;
* a site no entry of the pointer table starts at.

The span rule itself is tested too, because the first version of it was wrong: a
span measured as "distance to the next string" erased an unenumerated retail copy
of the slot-1033 biography. What a site may be rewritten over is its own text plus
its terminator, and nothing more.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

from tools.research import apply_friend_v3_text_edits as tool

TABLE_START = 0x0006BCE8
COUNT = 1534
#: The empty string every slot points at, and the address the string under test sits
#: at. Every slot must resolve to a ROM address, so the table is filled with POOL
#: first and only the tested slot is repointed.
POOL = 0x004FF000
TARGET = 0x00480000
#: Text placed here is decodable but no table entry names it, which is what the
#: "not a site of this pool" refusal is about.
UNNAMED = 0x00490000
IMAGE_SIZE = 0x00500000
NUL = b"\x00\x00"


def make_image(text: str, *, slot: int = 1032, trailing: bytes = b"") -> bytes:
    """A minimal image: the string under test sits where `slot` points.

    Every slot must resolve to a ROM address, so the table is filled with the empty
    pool string first and only the tested slot is repointed at TARGET.
    """
    image = bytearray(b"\x00" * IMAGE_SIZE)
    image[POOL:POOL + 2] = NUL
    empty = (POOL + 0x08000000).to_bytes(4, "little")
    for index in range(COUNT):
        at = TABLE_START + index * 4
        image[at:at + 4] = empty
    body = text.encode("utf-16le") + NUL
    image[TARGET:TARGET + len(body)] = body
    image[TARGET + len(body):TARGET + len(body) + len(trailing)] = trailing
    address = (TARGET + 0x08000000).to_bytes(4, "little")
    image[TABLE_START + slot * 4:TABLE_START + slot * 4 + 4] = address
    return bytes(image)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_the_span_is_the_sites_own_text_and_terminator() -> None:
    """Not the distance to the next enumerated string.

    The bytes right after a site's terminator belong to this site only if they are
    free space. Here they are a hidden second string, exactly as the retail pool
    holds an orphaned copy of the slot-1033 biography, and the edit must not reach
    them.
    """
    hidden = "Bulma Brief is the daughter of the founder and president."
    image = make_image("Bulma", trailing=hidden.encode("utf-16le") + NUL)
    result = tool.apply_edits(image, (tool.SpanEdit(1032, TARGET, "Bulma", "Tulma"),))
    assert result["changed"] == [TARGET]
    hidden_at = TARGET + len("Bulma".encode("utf-16le")) + 2
    before = image[hidden_at:hidden_at + len(hidden.encode("utf-16le"))]
    after = result["image"][hidden_at:hidden_at + len(hidden.encode("utf-16le"))]
    assert after == before, "the hidden string after the terminator was disturbed"


def test_a_site_whose_text_does_not_match_is_refused() -> None:
    image = make_image("Bulma")
    with pytest.raises(tool.FriendTextEditError) as caught:
        tool.apply_edits(image, (tool.SpanEdit(1032, TARGET, "Vegeta", "Tulma"),))
    assert "this site does not hold the text this edit replaces" in str(caught.value)


def test_a_replacement_longer_than_the_span_is_refused() -> None:
    image = make_image("Saiyaman", slot=1346)
    with pytest.raises(tool.FriendTextEditError) as caught:
        tool.apply_edits(image,
                         (tool.SpanEdit(1346, TARGET, "Saiyaman",
                                        "Great Saiyaman of the planet Earth"),))
    message = str(caught.value)
    assert "replacement needs" in message and "the span is" in message


def test_a_site_the_pointer_table_does_not_name_is_refused() -> None:
    """The offset must be a site the table names, not merely a place text sits."""
    image = make_image("Bulma")
    # Text at UNNAMED is decodable and real, but no table entry points at it, so an
    # edit addressed there is refused: the tool only writes sites it can prove are
    # reachable strings of this pool.
    unnamed = bytearray(image)
    unnamed[UNNAMED:UNNAMED + len("Bulma".encode("utf-16le")) + 2] = (
        "Bulma".encode("utf-16le") + NUL)
    assert UNNAMED not in set(tool.pointer_offsets(bytes(unnamed)))
    with pytest.raises(tool.FriendTextEditError) as caught:
        tool.apply_edits(bytes(unnamed),
                         (tool.SpanEdit(99, UNNAMED, "Bulma", "Tulma"),))
    assert "no entry of the text pointer table starts here" in str(caught.value)


def test_the_base_digest_is_checked_and_the_measured_digest_is_reported(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = tmp_path / "base.gba"
    base.write_bytes(make_image("Bulma"))
    presented = b"\x00" * 64
    monkeypatch.setattr(sys, "argv", [
        "apply_friend_v3_text_edits", "--base", str(base),
        "--base-sha256", presented.hex(), "--out", str(tmp_path / "out.gba"),
    ])
    with pytest.raises(SystemExit) as caught:
        tool.main()
    message = str(caught.value)
    assert "the base is not the declared image" in message
    assert digest(base.read_bytes()) in message, "the measured digest must be reported"
    assert not (tmp_path / "out.gba").exists(), "a refused run must write nothing"


def test_section_7_cannot_be_selected(tmp_path: Path,
                                      monkeypatch: pytest.MonkeyPatch) -> None:
    base = tmp_path / "base.gba"
    base.write_bytes(make_image("Bulma"))
    monkeypatch.setattr(sys, "argv", [
        "apply_friend_v3_text_edits", "--base", str(base),
        "--base-sha256", digest(base.read_bytes()), "--out", str(tmp_path / "out.gba"),
        "--sections", "7",
    ])
    with pytest.raises(SystemExit) as caught:
        tool.main()
    assert "no approved edit table" in str(caught.value)
    assert tool.SECTION_7 == (), "section 7 must stay unauthored until approved"
