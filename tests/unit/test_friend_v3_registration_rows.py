"""The registration-row builder, on a hand-built image.

The two failures this tool already made are what these tests pin: a rebuild that drops the
container an earlier release appended, and a container whose declared size does not cover the
offsets its handles name. Both are size arithmetic, so a small synthetic image can hold them.

The selector-7 slot address is patched to a synthetic one, because the real slot lives at file
0x9A9D04 and a synthetic image that reached it would have to be ten megabytes of zeroes. Every
other quantity, including the table literal that names the table, is the real one.
"""

from __future__ import annotations

from unittest import mock

import pytest

from tools.research import apply_friend_v3_registration_rows as builder
from tools.research.apply_friend_v3_registration_rows import (
    TERMINATOR, RegistrationRowError)
from tools.webfoot.handles import DialogueHandle, unpack_handle

ROM_BASE = 0x08000000
TABLE_LITERAL = 0x123CC
TEXT_TABLE_START = 0x6BCE8
BIO_SLOT = 1083
SLOT_AT = 0x6D800                       # synthetic stand-in for file 0x9A9D04
BIO_TEXT = ("Bulma is Yamcha's wife and Krillin and Videl's mother. A genius inventor, she "
            "is the heiress of Capsule Corporation.")
PREVIOUS_PAYLOAD = ("#Hey sis, if you win the tournament, what do you think you'll get with "
                    "the prize Zeni?").encode("utf-16le")
OLD_ROW_TEXT = "Good luck, you guys! This is just like old times!"
NEW_ROW_TEXT = "A replacement line."
ROW_SITE = 0x6D000
CARRIED_SITE = 0x6D010
ROW_START = 0x100


def build() -> tuple[bytearray, dict, dict]:
    """An image with a container 2 record, the approved biography, and a previous
    selector-7 container whose payload an existing handle already names."""
    image = bytearray(0x6E000)
    record = OLD_ROW_TEXT.encode("utf-16le")
    payload_two = bytearray(0x200)
    payload_two[ROW_START:ROW_START + len(record)] = record
    container_two = 0x6D400
    image[container_two:container_two + 4] = (1).to_bytes(4, "little")
    image[container_two + 4:container_two + 8] = len(payload_two).to_bytes(4, "little")
    image[container_two + 8:container_two + 8 + len(payload_two)] = payload_two
    old_word = DialogueHandle(2, ROW_START, len(record)).encode()
    image[ROW_SITE:ROW_SITE + 4] = old_word.to_bytes(4, "little")

    bio_at = 0x6D200
    image[bio_at:bio_at + len(BIO_TEXT.encode("utf-16le")) + 2] = (
        BIO_TEXT.encode("utf-16le") + TERMINATOR)
    image[TEXT_TABLE_START + BIO_SLOT * 4:TEXT_TABLE_START + BIO_SLOT * 4 + 4] = (
        (ROM_BASE + bio_at).to_bytes(4, "little"))

    previous = 0x6D600
    image[previous:previous + 4] = (0).to_bytes(4, "little")
    image[previous + 4:previous + 8] = len(PREVIOUS_PAYLOAD).to_bytes(4, "little")
    image[previous + 8:previous + 8 + len(PREVIOUS_PAYLOAD)] = PREVIOUS_PAYLOAD
    image[SLOT_AT:SLOT_AT + 4] = (ROM_BASE + previous).to_bytes(4, "little")
    image[CARRIED_SITE:CARRIED_SITE + 4] = DialogueHandle(
        7, 0, len(PREVIOUS_PAYLOAD)).encode().to_bytes(4, "little")

    table = 0x6DF00
    image[TABLE_LITERAL:TABLE_LITERAL + 4] = (ROM_BASE + table).to_bytes(4, "little")
    image[table + 2 * 4:table + 2 * 4 + 4] = (ROM_BASE + container_two).to_bytes(4, "little")
    image[table + 7 * 4:table + 7 * 4 + 4] = (ROM_BASE + previous).to_bytes(4, "little")

    bio = {
        "kind": "text slot", "key": f"text:{BIO_SLOT}", "label": "test biography",
        "text": BIO_TEXT, "bytes": len(BIO_TEXT.encode("utf-16le")), "units": len(BIO_TEXT),
        "sites": [TEXT_TABLE_START + BIO_SLOT * 4], "site_kind": "text pointer",
        "old_address": ROM_BASE + bio_at, "approval": "test",
    }
    row = {
        "kind": "dialogue record", "key": f"2:{ROW_START}:{len(record)}",
        "label": "test row", "text": NEW_ROW_TEXT,
        "bytes": len(NEW_ROW_TEXT.encode("utf-16le")), "units": len(NEW_ROW_TEXT),
        "sites": [ROW_SITE], "site_kind": "packed handle", "old_word": old_word,
        "selector": 2, "old_start": ROW_START, "old_length": len(record),
        "current": OLD_ROW_TEXT, "approval": "test",
    }
    return image, bio, row


def call(image, bio, rows):
    """apply() with the selector-7 slot patched to the synthetic address."""
    with mock.patch.object(builder, "TABLE_SLOT_NEW", SLOT_AT):
        return builder.apply(bytes(image), bio, rows)


def test_the_previous_payload_is_carried_and_its_handle_still_resolves() -> None:
    image, bio, _row = build()
    output, report = call(image, bio, [])
    assert report["carried_prefix_bytes"] == len(PREVIOUS_PAYLOAD)
    container = report["container_file_offset"]
    assert output[container + 8:container + 8 + len(PREVIOUS_PAYLOAD)] == PREVIOUS_PAYLOAD
    assert int.from_bytes(output[SLOT_AT:SLOT_AT + 4], "little") == ROM_BASE + container
    assert unpack_handle(int.from_bytes(output[CARRIED_SITE:CARRIED_SITE + 4], "little")) \
        == (7, 0, len(PREVIOUS_PAYLOAD))


def test_a_new_record_lands_after_the_carried_payload_inside_the_declared_size() -> None:
    image, bio, row = build()
    output, report = call(image, bio, [row])
    container = report["container_file_offset"]
    declared = int.from_bytes(output[container + 4:container + 8], "little")
    assert declared == len(PREVIOUS_PAYLOAD) + row["bytes"]
    selector, start, length = unpack_handle(
        int.from_bytes(output[ROW_SITE:ROW_SITE + 4], "little"))
    assert (selector, start, length) == (7, len(PREVIOUS_PAYLOAD), row["bytes"])
    assert start + length <= declared
    assert output[container + 8 + start:container + 8 + start + length].decode("utf-16le") \
        == NEW_ROW_TEXT


def test_the_biography_moves_to_the_end_and_the_old_copy_is_left_alone() -> None:
    image, bio, _row = build()
    output, report = call(image, bio, [])
    offset = report["string_file_offset"]
    assert offset >= len(image)
    end = offset
    while output[end:end + 2] != TERMINATOR:
        end += 2
    assert output[offset:end].decode("utf-16le") == BIO_TEXT
    assert output[bio["old_address"] - ROM_BASE:
                  bio["old_address"] - ROM_BASE + 4] == \
        image[bio["old_address"] - ROM_BASE:bio["old_address"] - ROM_BASE + 4]


def test_a_site_that_does_not_carry_the_expected_handle_refuses() -> None:
    image, bio, row = build()
    image[ROW_SITE:ROW_SITE + 4] = DialogueHandle(2, 8, 12).encode().to_bytes(4, "little")
    with pytest.raises(RegistrationRowError, match="refusing"):
        call(image, bio, [row])


def test_data_that_is_not_4_aligned_is_padded_before_the_container_not_at_the_end() -> None:
    image, bio, row = build()
    del image[-3:]            # make the image end off the 4-byte boundary
    output, report = call(image, bio, [row])
    assert report["container_file_offset"] % 4 == 0
    # The only bytes of the base that differ are the declared sites; the padding is appended.
    declared = {change["site"] for change in
                [{"site": ROW_SITE}, {"site": SLOT_AT},
                 {"site": TEXT_TABLE_START + BIO_SLOT * 4}]}
    changed = [index for index in range(min(len(image), len(output)))
               if output[index] != image[index]]
    assert set(changed).issubset(
        {offset for site in declared for offset in range(site, site + 4)})
    assert output[SLOT_AT:SLOT_AT + 4] == \
        (ROM_BASE + report["container_file_offset"]).to_bytes(4, "little")
