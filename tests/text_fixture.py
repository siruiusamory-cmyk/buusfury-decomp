"""One synthetic Buu's Fury image, shared by the engine's tests and the app's.

Every rule the text stack adds is size arithmetic or an identity check, so a small
synthetic image holds it: the container table names real stored containers, the
record words carry real handles, and the 1,534-slot text table is the real one.
The image is 450 KB of mostly zeroes, which is why the gates stay portable and why
the app's tests need no ROM.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from tools.webfoot import textedit
from tools.webfoot.formats import text_tables as tt
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.handles import DialogueHandle

ROM_BASE = 0x08000000
GAME_CODE = b"BG3E"
TABLE_LITERAL = 0x123CC
TEXT_TABLE = 0x6BCE8
TEXT_SLOTS = 1534
IMAGE_SIZE = 0x6E000
CONTAINER_AT = 0x1000
CONTAINER_STRIDE = 0x200
PAYLOAD_BYTES = 0x100
RECORD_AT = 0x2000
BODY_AT = 0x60000
TABLE_AT = 0x6DF00
TABLE_BYTES = 64 * 4
GROWN_AT = 0x8000
SPACES = b"\x20\x00" * (PAYLOAD_BYTES // 2)
RECORD_WORD = bytes([0x00, 0x00, 0x05, 0x00])


def build(payloads=None, records=(), slots=None, grown=None):
    """A synthetic image: seven stored containers, record words, the real text table."""
    image = bytearray(IMAGE_SIZE)
    image[0xAC:0xB0] = GAME_CODE
    payloads = dict(payloads or {})
    containers = {}
    for selector in range(7):
        payload = payloads.get(selector, SPACES)
        at = CONTAINER_AT + selector * CONTAINER_STRIDE
        image[at:at + 4] = (0).to_bytes(4, "little")
        image[at + 4:at + 8] = len(payload).to_bytes(4, "little")
        image[at + 8:at + 8 + len(payload)] = payload
        containers[selector] = at
    for index, (selector, start, length) in enumerate(records):
        where = RECORD_AT + index * 0x10
        image[where:where + 4] = RECORD_WORD
        image[where + 4:where + 8] = DialogueHandle(selector, start, length).encode() \
            .to_bytes(4, "little")
    cursor = BODY_AT
    slot_text = dict(slots or {})
    for index in range(TEXT_SLOTS):
        encoded = tt.encode_string(slot_text.get(index, "shared"))
        image[cursor:cursor + len(encoded)] = encoded
        image[TEXT_TABLE + index * 4:TEXT_TABLE + index * 4 + 4] = \
            (ROM_BASE + cursor).to_bytes(4, "little")
        cursor += len(encoded) + 2
    image[TABLE_LITERAL:TABLE_LITERAL + 4] = (ROM_BASE + TABLE_AT).to_bytes(4, "little")
    for selector, at in containers.items():
        image[TABLE_AT + selector * 4:TABLE_AT + selector * 4 + 4] = \
            (ROM_BASE + at).to_bytes(4, "little")
    if grown is not None:
        image[GROWN_AT:GROWN_AT + 4] = (0).to_bytes(4, "little")
        image[GROWN_AT + 4:GROWN_AT + 8] = len(grown).to_bytes(4, "little")
        image[GROWN_AT + 8:GROWN_AT + 8 + len(grown)] = grown
        image[TABLE_AT + 7 * 4:TABLE_AT + 7 * 4 + 4] = (ROM_BASE + GROWN_AT).to_bytes(4, "little")
    return image


@contextmanager
def lowered_record_floor():
    """The one test-only concession: a fixture carries the records a rule needs.

    The floor is a property of a whole retail image, so no fixture can reach it.
    Every caller that opens a fixture goes through here, so the concession is in
    exactly one place.
    """
    with mock.patch.object(textedit.engine, "MINIMUM_DIALOGUE_RECORDS", 1):
        yield


def open_image(image, directory, name: str = "fixture.gba", **kwargs):
    path = Path(directory) / name
    path.write_bytes(image)
    with lowered_record_floor():
        return textedit.open_rom(path, **kwargs)


def slot_payload(image: bytes, selector: int) -> bytes:
    table = int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    pointer = int.from_bytes(image[table + selector * 4:table + selector * 4 + 4], "little")
    return bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)


def line_payload(text: str, at: int = 0x20) -> bytes:
    payload = bytearray(SPACES)
    encoded = text.encode("utf-16le")
    payload[at:at + len(encoded)] = encoded
    return bytes(payload)


def simple(directory, text: str = "Say hello!", at: int = 0x20):
    """One record holding `text`, and its model."""
    image = build(payloads={1: line_payload(text, at)}, records=[(1, at, len(text) * 2)])
    return image, open_image(image, directory)
