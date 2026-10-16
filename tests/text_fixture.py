"""One synthetic Buu's Fury image, shared by the engine's tests and the app's.

Every rule the text stack adds is size arithmetic or an identity check, so a small
synthetic image holds it: the container table names real stored containers, the
record words carry real handles, and the 1,534-slot text table is the real one.
The image is 450 KB of mostly zeroes, which is why the gates stay portable and why
the app's tests need no ROM.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace
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


@contextmanager
def proven_handle_pool():
    """The fixture's record words are the proven carriers, as a real image's pool is.

    A real image's proven carriers are the event-resource pool, which sits far above this
    fixture's payload. The fixture plants its record words at `RECORD_AT`, so the pool is
    patched to that region while an image is opened, which is where the engine reads it. The
    model carries the pool, so a later `plan` call needs no patch.
    """
    with mock.patch.object(textedit.engine, "PROVEN_HANDLE_POOL",
                           (RECORD_AT, RECORD_AT + 0x1000)):
        yield

def open_image(image, directory, name: str = "fixture.gba", **kwargs):
    path = Path(directory) / name
    path.write_bytes(image)
    with lowered_record_floor(), proven_handle_pool():
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


# --- the portrait operand and the appearance table ---------------------------


#: Where a fixture puts its appearance table: clear of the text table, which ends
#: at 0x6D4E0, and below the container table at 0x6DF00.
APPEARANCE_AT = 0x6D600


@contextmanager
def appearances(table: int = APPEARANCE_AT, count: int = 4):
    """Point the profile at a fixture's own appearance table."""
    profile = replace(textedit.engine.PROFILES[0], appearance_table=table,
                      appearance_count=count)
    with mock.patch.object(textedit.engine, "PROFILES", (profile,)):
        yield


def with_operand(image, operand: int, record_index: int = 0):
    """Set one record word's portrait operand byte, which sits at word +3."""
    image[RECORD_AT + record_index * 0x10 + 3] = operand
    return image


def with_appearances(image, entries, table: int = APPEARANCE_AT):
    """Write appearance records: each entry is (name slot, portrait slot)."""
    for index, (name_slot, portrait) in enumerate(entries):
        at = table + index * 0x10
        image[at:at + 2] = name_slot.to_bytes(2, "little")
        image[at + 8:at + 12] = portrait.to_bytes(4, "little")
    return image


def speaking_image(text: str = "Say hello!", operand: int = 0x3F,
                   slots: dict[int, str] | None = None, records=None):
    """A fixture whose first record carries a resolvable portrait operand."""
    image = with_operand(
        build(payloads={1: line_payload(text, 0x00)},
              records=records or [(1, 0x00, len(text) * 2)],
              slots=slots or {1066: "Lazuli", 1067: "Kakarot"}),
        operand)
    return with_appearances(image, [(1066, operand), (1067, 0x88)])
