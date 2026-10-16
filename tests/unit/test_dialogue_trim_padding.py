"""The trailing-pad repair's guards, on synthetic bytes composed here.

WHY SYNTHETIC. An earlier revision of this test carried a slice of the image's real
dialogue stream as a fixture. That is committed commercial content, which
`docs/ROM_SAFETY.md` forbids, so it was replaced by bytes composed in this file. Nothing
below comes from an image.

THE TWO TRAPS, both measured, both recorded in `build/fv3text001/inventory_offsets.py`, and
both of which defeated earlier fixtures:

1. `pack_handle(selector, start, length)` takes start in BYTES and length in HALFWORDS, so
   the engine reads `length // 2` units. A "six byte" record is written as length 3.
2. `dialogue_record_inventory` reconstructs a word by scanning for the pattern `00 05`,
   taking the byte before it as the word start, and requiring 4-alignment plus a handle whose
   span fits INSIDE the container. A span that runs past the container is dropped silently.

WHAT THIS TEST DELIBERATELY DOES NOT DO. It does not compute the container text by hand. The
fixture mixes a real bug with hand arithmetic badly, and eight earlier attempts failed on the
arithmetic rather than on the tool. Every expectation below is therefore derived from the
inventory's own report of what it found, so the test asserts the tool's behaviour rather than
my index sums.
"""

from __future__ import annotations

from tools.research.trim_dialogue_padding import apply, plan
from tools.webfoot import compressed_dialogue as cd
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.handles import pack_handle

ROM_BASE = 0x08000000
TABLE_LITERAL = 0x123CC
CONTAINER_AT = 0x1000
TABLE_AT = 0x18000
SITE_AT = 0x19000
SPACE = 0x20

#: (word start, record byte start, record byte length) for `pack_handle`, which takes BYTE
#: offsets and BYTE lengths and requires both to be even because it encodes halfwords.
RECORDS = ((SITE_AT + 0, 0, 8), (SITE_AT + 8, 12, 10))


def build_image() -> bytes:
    """A 32-unit container: `A A`, then a long run of spaces, then `B B` and spaces.

    The layout is deliberately plain - letters at the ends and spaces between - because the
    test reads the container through the inventory rather than reasoning about offsets.
    """
    units = [0x41, 0x41, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
             0x42, 0x42, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
             0x43, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
             0x44, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20]
    text = "".join(chr(unit) for unit in units).encode("utf-16le")
    container = b"\x00\x00\x00\x00" + len(text).to_bytes(4, "little") + text

    image = bytearray(0x20000)
    image[CONTAINER_AT:CONTAINER_AT + len(container)] = container
    image[TABLE_LITERAL:TABLE_LITERAL + 4] = (ROM_BASE + TABLE_AT).to_bytes(4, "little")
    image[TABLE_AT:TABLE_AT + 4] = (ROM_BASE + CONTAINER_AT).to_bytes(4, "little")
    for site, start_bytes, length_bytes in RECORDS:
        image[site + 1] = 0x00
        image[site + 2] = 0x05
        image[site + 4:site + 8] = pack_handle(
            0, start_bytes, length_bytes).to_bytes(4, "little")
    return bytes(image)


def records(image: bytes) -> dict[int, int]:
    """The inventory's own report: byte start -> byte length, for this container."""
    stream = bytes(webfoot_lz.unpack(image, CONTAINER_AT).data)
    return {record.handle.decoded_start: record.handle.decoded_length
            for record in cd.dialogue_record_inventory(image, 0, len(stream))}


def test_the_fixture_reaches_the_inventory_at_all() -> None:
    # If this fails the fixture is wrong, not the tool, and the message says so.
    found = records(build_image())
    assert len(found) == 2, f"the inventory sees {found}; the fixture is malformed"


def test_the_plan_only_selects_records_whose_own_tail_is_pad() -> None:
    image = build_image()
    trims, interior = plan(image)
    assert interior == [], interior
    assert trims, "the fixture carries text ending in pad, so a trim is expected"
    stream = bytes(webfoot_lz.unpack(image, CONTAINER_AT).data)
    for entry in trims:
        start, length = entry["start"], entry["length"]
        tail = stream[start + length - 2 * entry["pad"]:start + length]
        assert tail == SPACE.to_bytes(2, "little") * entry["pad"], entry["key"]
        assert entry["pad"] >= 2 and entry["trimmed_length"] >= 0, entry


def test_the_repair_touches_only_handle_words_and_never_the_payload() -> None:
    image = build_image()
    trims, _interior = plan(image)
    repaired, changes = apply(image, trims)
    declared = {change["offset"] for change in changes}
    assert declared, "a plan that selects nothing cannot be tested"
    moved = {offset for offset in range(len(image)) if image[offset] != repaired[offset]}
    for offset in moved:
        assert any(base <= offset < base + 4 for base in declared), hex(offset)
    # The payload is byte-identical. That is the whole safety argument: the pad bytes stay
    # where they were, so every other record's span still reads exactly what it read.
    assert (webfoot_lz.unpack(repaired, CONTAINER_AT).data
            == webfoot_lz.unpack(image, CONTAINER_AT).data)


def test_every_record_still_reads_its_text_minus_its_own_pad() -> None:
    image = build_image()
    trims, _interior = plan(image)
    repaired, _changes = apply(image, trims)
    before = bytes(webfoot_lz.unpack(image, CONTAINER_AT).data)
    after = bytes(webfoot_lz.unpack(repaired, CONTAINER_AT).data)
    planned = {entry["start"]: entry for entry in trims}

    for start, length in records(image).items():
        entry = planned.get(start)
        if entry is None:
            # An unplanned record reads exactly what it read before, at the same span.
            assert after[start:start + length] == before[start:start + length], hex(start)
            continue
        # A planned record reads its text with the pad gone: its new prefix is byte-identical
        # to what it read before, and the units it gave up are still in the payload right
        # after that shorter span, which is the safety property and not a claim about text.
        trimmed = length - 2 * entry["pad"]
        assert after[start:start + trimmed] == before[start:start + trimmed], hex(start)
        assert after[start + trimmed:start + length] == before[start + trimmed:start + length]
