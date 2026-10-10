"""The approved text-slot write path, on synthetic bytes and on the real images.

The load-bearing behaviour is the relocation guard: a grown site may move only when exactly
one word-aligned word names its old address. A second name means another reader would keep
reading the old text, so the write must refuse. That refusal, and the alignment rule the
reference count depends on, are what these tests pin.
"""

from __future__ import annotations

import struct

import pytest

from tools.research.apply_friend_v3_text_slot import (
    TABLE_START, TERMINATOR, TextSlotError, apply, current_span, references)
from tools.research.friend_v3_text_approvals import APPROVED_REPLACEMENTS, APPROVED_TEXT_SLOTS


def make_image(slot: int, text: str, *, body_at: int = 0x6D000, size: int = 0x6E000
               ) -> bytearray:
    """A synthetic image whose pointer table names one UTF-16LE string.

    The size clears the real table extent: slot 1083's pointer lives at file 0x6BFD4, so a
    smaller image would read a zero word there and the tool would refuse for the wrong reason.
    """
    image = bytearray(size)
    body = text.encode("utf-16le") + TERMINATOR
    image[body_at:body_at + len(body)] = body
    image[TABLE_START + slot * 4:TABLE_START + slot * 4 + 4] = \
        struct.pack("<I", 0x08000000 + body_at)
    return image


def test_the_approved_table_names_the_slot_the_owner_decided() -> None:
    assert [edit.slot for edit in APPROVED_TEXT_SLOTS] == [1083]
    assert APPROVED_REPLACEMENTS[1083].startswith("Bulma is Yamcha's wife and Krillin and ")


def test_a_grown_site_with_one_reference_is_relocated() -> None:
    old = "A short line."
    new = "A considerably longer line than the one it replaces, which cannot fit its span."
    image = make_image(1083, old)
    output, entry = apply(bytes(image), 1083, old, new)
    assert entry["method"] == "relocated"
    assert len(output) > len(image)
    assert output[TABLE_START + 1083 * 4:TABLE_START + 1083 * 4 + 4] == \
        struct.pack("<I", 0x08000000 + entry["new_offset"])
    body = new.encode("utf-16le") + TERMINATOR
    assert bytes(output[entry["new_offset"]:entry["new_offset"] + len(body)]) == body


def test_a_grown_site_with_a_second_reference_refuses() -> None:
    # The failure this prevents: another structure also names the old string, so moving it
    # would leave that reader showing the old text for ever.
    old = "A short line."
    new = "A considerably longer line than the one it replaces, which cannot fit its span."
    image = make_image(1083, old)
    image[0x6D200:0x6D204] = struct.pack("<I", 0x08000000 + 0x6D000)   # a second, aligned name
    with pytest.raises(TextSlotError, match="exactly its own table entry"):
        apply(bytes(image), 1083, old, new)


def test_an_unaligned_second_name_does_not_count() -> None:
    # The reference count is word-aligned, because the engine reads a pointer as a word. A
    # byte-identical run at an odd offset is data, not a name, so the write still proceeds.
    old = "A short line."
    new = "A considerably longer line than the one it replaces, which cannot fit its span."
    image = make_image(1083, old)
    image[0x6D201:0x6D205] = struct.pack("<I", 0x08000000 + 0x6D000)
    assert references(bytes(image), 0x08000000 + 0x6D000) == 1
    output, entry = apply(bytes(image), 1083, old, new)
    assert entry["method"] == "relocated"
    assert len(output) > len(image)


def test_a_text_that_fits_is_written_in_place_and_leaves_the_tail() -> None:
    old = "A line with room to spare in its own span."
    new = "A short line."
    image = make_image(1083, old)
    output, entry = apply(bytes(image), 1083, old, new)
    assert entry["method"] == "in place"
    assert len(output) == len(image)
    offset, span, text = current_span(bytes(output), 1083)
    assert text == new and span == len(new.encode("utf-16le")) + len(TERMINATOR)
    # The bytes past the new terminator are the old tail, untouched by design.
    tail_start = offset + len(new.encode("utf-16le")) + len(TERMINATOR)
    assert output[tail_start:offset + 182] == bytes(image)[tail_start:offset + 182]


def test_a_slot_that_does_not_hold_the_expected_text_refuses() -> None:
    image = make_image(1083, "Something else entirely.")
    with pytest.raises(TextSlotError, match="refusing rather than correcting"):
        apply(bytes(image), 1083, "A short line.", "A longer replacement line.")
