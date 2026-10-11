"""The text-edit engine on hand-built images, plus the release goldens.

Every rule this engine adds is size arithmetic or an identity check, so a small
synthetic image holds it: the container table names real stored containers, the
record words carry real handles, and the 1,534-slot text table is the real one.
The image is 450 KB of mostly zeroes, which is why the gate stays portable.

The two golden replays read the friend-v3 release images, which are proprietary
bytes and must never be committed, so they skip when those images are absent.
`MINIMUM_DIALOGUE_RECORDS` is lowered for the fixtures: the floor is a property
of a whole retail image, and a fixture carries the records the rule needs.
"""

from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path
from unittest import mock

import pytest

from tests.gates import REPOSITORY_ROOT
from tests.rom_support import canonical_rom_path
from tools.webfoot import textedit
from tools.webfoot.formats import text_tables as tt
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.handles import DialogueHandle, unpack_handle

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


def open_image(image, directory, name: str = "fixture.gba", **kwargs):
    """Open a fixture, whose record words at RECORD_AT are the proven carriers.

    A real image's proven carriers are the event-resource pool; the fixture plants
    its record words at `RECORD_AT`, so the pool is patched to that region while
    the image is validated. The model carries the pool, so a later `plan` call
    needs no patch. A word planted anywhere else in a test is outside the pool and
    must not be written.

    The fixture's container table is also declared to sit at the RETAIL offset, so
    every fixture behaves like an image whose table has not yet been moved aside.
    That is the shape the table guard exists for.
    """
    path = Path(directory) / name
    path.write_bytes(image)
    profile = replace(textedit.engine.PROFILES[0], retail_table=TABLE_AT)
    with mock.patch.object(textedit.engine, "MINIMUM_DIALOGUE_RECORDS", 1), \
            mock.patch.object(textedit.engine, "PROFILES", (profile,)), \
            mock.patch.object(textedit.engine, "PROVEN_HANDLE_POOL",
                              (RECORD_AT, RECORD_AT + 0x1000)):
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


# --- byte coordinates --------------------------------------------------------


def test_an_in_place_edit_keeps_the_record_span_and_pays_the_tail_with_spaces(
        tmp_path: Path) -> None:
    image, model = simple(tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 20, "hello", "hi")])
    assert [item.method for item in built.decisions] == [textedit.IN_PLACE]
    assert len(built.output) == len(image)
    assert slot_payload(built.output, 1)[0x20:0x34].decode("utf-16le") == "Say hi!   "
    container = model.layout.offsets[1]
    changed = {index for index in range(len(image)) if built.output[index] != image[index]}
    assert changed
    assert changed <= set(range(container + 8 + 0x20, container + 8 + 0x34))
    report = textedit.apply(built, tmp_path / "out.gba")
    assert report["output_sha256"] == built.output_sha256
    assert report["in_place"] == 1


def test_a_refused_edit_blocks_the_export_and_writes_nothing(tmp_path: Path) -> None:
    _image, model = simple(tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 20, "hello", "hi"),
                                  textedit.RecordEdit(1, 0x20, 20, "absent", "here")])
    assert [item.method for item in built.decisions] == [textedit.IN_PLACE, textedit.REFUSED]
    assert "0 time(s)" in built.refusals[0].reason
    target = tmp_path / "out.gba"
    with pytest.raises(textedit.TextEditError, match="REFUSED"):
        textedit.apply(built, target)
    assert not target.exists()


# --- the boundary-safe rule --------------------------------------------------


def test_a_span_with_another_record_boundary_inside_it_moves_instead_of_writing(
        tmp_path: Path) -> None:
    text = "hello there everybody, this is"
    image = build(payloads={1: line_payload(text)},
                  records=[(1, 0x20, 0x40), (1, 0x30, 0x10)])
    model = open_image(image, tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 0x40, "hello", "hi")])
    assert built.decisions[0].method == textedit.MOVE
    assert any("boundary inside this span" in warning for warning in built.warnings)
    assert slot_payload(built.output, 1) == slot_payload(image, 1)
    prefix = "hi there everybody, this is".encode("utf-16le")
    assert slot_payload(built.output, 7)[:len(prefix)] == prefix
    assert built.in_place == ()
    assert len(built.placements) == 1
    assert textedit.readback(built) == ()


def test_a_record_that_merely_contains_the_span_is_not_a_boundary_conflict(
        tmp_path: Path) -> None:
    image = build(payloads={1: line_payload("hello", 0x30)},
                  records=[(1, 0x20, 0x40), (1, 0x30, 0x10)])
    model = open_image(image, tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x30, 0x10, "hello", "hi")])
    assert built.decisions[0].method == textedit.IN_PLACE
    assert slot_payload(built.output, 1)[0x30:0x40].decode("utf-16le") == "hi      "


# --- the one-reference guard -------------------------------------------------


def test_a_slot_whose_pointer_has_a_second_reference_is_refused(tmp_path: Path) -> None:
    image = build(records=[(1, 0, 4)], slots={1066: "Videl"})
    with mock.patch.object(textedit.engine, "MINIMUM_DIALOGUE_RECORDS", 1):
        first = open_image(image, tmp_path)
        pointer = first.slots[1066].offset
        image[0x9000:0x9004] = (ROM_BASE + pointer).to_bytes(4, "little")
        model = open_image(image, tmp_path)
        built = textedit.plan(model, [textedit.SlotEdit(1066, "Videl", "Lazuli")])
    assert built.decisions[0].method == textedit.REFUSED
    assert "2 word-aligned references" in built.refusals[0].reason
    with pytest.raises(textedit.TextEditError, match="REFUSED"):
        textedit.apply(built, tmp_path / "unused.gba")


def test_a_slot_with_one_reference_moves_and_reads_back(tmp_path: Path) -> None:
    image = build(records=[(1, 0, 4)], slots={1066: "Videl"})
    model = open_image(image, tmp_path)
    built = textedit.plan(model, [textedit.SlotEdit(1066, "Videl", "Lazuli")])
    assert built.decisions[0].method == textedit.MOVE
    assert built.slot_moves[0].at >= len(image)
    assert built.output[built.slot_moves[0].at:built.slot_moves[0].at + 14] == \
        tt.encode_string("Lazuli")
    assert textedit.readback(built) == ()
    textedit.apply(built, tmp_path / "slot.gba")


def test_a_slot_edit_refuses_a_guard_that_does_not_match_the_slot(tmp_path: Path) -> None:
    model = open_image(build(records=[(1, 0, 4)], slots={1066: "Videl"}), tmp_path)
    built = textedit.plan(model, [textedit.SlotEdit(1066, "Goku", "Lazuli")])
    assert built.decisions[0].method == textedit.REFUSED
    assert "not the text this edit replaces" in built.refusals[0].reason


# --- the carry-forward prefix ------------------------------------------------


def test_a_moved_record_is_appended_after_the_carried_payload(tmp_path: Path) -> None:
    carried = "#Hey sis!".encode("utf-16le")
    text = "a short line"
    image = build(payloads={1: line_payload(text)}, records=[(1, 0x20, len(text) * 2)],
                  grown=carried)
    model = open_image(image, tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, len(text) * 2,
                                                      "short", "much longer line")])
    assert built.decisions[0].method == textedit.MOVE
    payload = slot_payload(built.output, 7)
    assert payload[:len(carried)] == carried
    assert payload[len(carried):].decode("utf-16le") == "a much longer line line"
    assert built.placements[0].new_start == len(carried)
    assert textedit.readback(built) == ()


def test_a_carried_record_still_resolves_through_its_own_handle(tmp_path: Path) -> None:
    carried = "#Hey sis!".encode("utf-16le")
    text = "a short line"
    image = build(payloads={1: line_payload(text)},
                  records=[(1, 0x20, len(text) * 2), (7, 0, len(carried))],
                  grown=carried)
    model = open_image(image, tmp_path)
    assert model.record(7, 0, len(carried)).text == "#Hey sis!"
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, len(text) * 2,
                                                      "short", "much longer line")])
    assert 7 in built.rewritten_selectors
    assert textedit.readback(built) == ()
    site = model.record(7, 0, len(carried)).sites[0]
    assert unpack_handle(int.from_bytes(built.output[site:site + 4], "little")) == \
        (7, 0, len(carried))


def test_the_first_move_relocates_the_table_and_leaves_every_retail_word_alone(
        tmp_path: Path) -> None:
    text = "hello there everybody, this is"
    image = build(payloads={1: line_payload(text)},
                  records=[(1, 0x20, 0x40), (1, 0x30, 0x10)])
    model = open_image(image, tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 0x40, "hello", "hi")])
    assert built.decisions[0].method == textedit.MOVE
    assert built.output[TABLE_AT:TABLE_AT + TABLE_BYTES] == image[TABLE_AT:TABLE_AT + TABLE_BYTES]
    assert any("container table is copied" in warning for warning in built.warnings)
    table = int.from_bytes(built.output[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    assert table >= len(image)
    for selector in range(7):
        assert built.output[table + selector * 4:table + selector * 4 + 4] == \
            image[TABLE_AT + selector * 4:TABLE_AT + selector * 4 + 4]
    pointer = int.from_bytes(built.output[table + 7 * 4:table + 7 * 4 + 4], "little")
    assert pointer >= ROM_BASE + len(image)
    assert slot_payload(built.output, 7).decode("utf-16le").startswith(
        "hi there everybody, this is")
    assert textedit.readback(built) == ()


def test_a_table_with_more_than_one_reference_is_refused_instead_of_written(
        tmp_path: Path) -> None:
    text = "hello there everybody, this is"
    image = build(payloads={1: line_payload(text)},
                  records=[(1, 0x20, 0x40), (1, 0x30, 0x10)])
    image[0x9000:0x9004] = image[TABLE_LITERAL:TABLE_LITERAL + 4]
    model = open_image(image, tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 0x40, "hello", "hi")])
    assert built.decisions[0].method == textedit.REFUSED
    assert "not proven free" in built.refusals[0].reason
    with pytest.raises(textedit.TextEditError, match="REFUSED"):
        textedit.apply(built, tmp_path / "unused.gba")


def test_an_in_place_edit_and_a_move_from_one_container_both_read_back(
        tmp_path: Path) -> None:
    payload = bytearray(line_payload("hello", 0x20))
    payload[0x40:0x45] = "world".encode("utf-16le")
    image = build(payloads={1: bytes(payload)},
                  records=[(1, 0x20, 0x20), (1, 0x40, 0x20)])
    model = open_image(image, tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 0x20, "hello", "hi"),
                                  textedit.RecordEdit(1, 0x40, 0x20, "world",
                                                      "a much longer line than this")])
    assert [item.method for item in built.decisions] == [textedit.IN_PLACE, textedit.MOVE]
    assert textedit.readback(built) == ()
    textedit.apply(built, tmp_path / "mixed.gba")


def test_a_record_already_in_the_grown_selector_moves_and_reads_back(tmp_path: Path) -> None:
    carried = "#Hey sis!".encode("utf-16le")
    image = build(records=[(7, 0, len(carried))], grown=carried)
    model = open_image(image, tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(7, 0, len(carried), "Hey sis",
                                                      "a much longer greeting")])
    assert built.decisions[0].method == textedit.MOVE
    assert built.placements[0].new_start == len(carried)
    assert textedit.readback(built) == ()
    textedit.apply(built, tmp_path / "grown.gba")


# --- the spacing pass --------------------------------------------------------


def test_the_spacing_pass_collapses_a_chain_shared_run_and_rewrites_every_handle(
        tmp_path: Path) -> None:
    """Two records read the same run, so a record-level fix would re-create it (P-023)."""
    base = build(payloads={1: line_payload("Hi  there")},
                 records=[(1, 0x20, 18), (1, 0x22, 16)])
    retail = open_image(build(payloads={1: line_payload("Hi there")},
                              records=[(1, 0x20, 18), (1, 0x22, 16)]),
                        tmp_path, name="retail.gba")
    model = open_image(base, tmp_path, name="base.gba", canonical=retail.path)
    built = textedit.plan(model, [textedit.SpacingEdit()])
    assert [item.method for item in built.decisions] == [textedit.IN_PLACE]
    assert len(built.spacing) == 1
    row = built.spacing[0]
    assert row.selector == 1
    assert row.deleted == (0x26,)
    assert row.texts["1:32:18"] == "Hi there"
    assert row.texts["1:34:16"] == "i there"
    assert slot_payload(built.output, 1)[0x20:0x30].decode("utf-16le") == "Hi there"
    assert textedit.readback(built) == ()
    assert len(built.output) == len(base)
    table_slot = TABLE_AT + 4
    assert built.output[table_slot:table_slot + 4] == base[table_slot:table_slot + 4]
    textedit.apply(built, tmp_path / "spacing.gba")


def test_a_run_the_canonical_image_carries_is_kept_and_the_other_collapses(
        tmp_path: Path) -> None:
    base = build(payloads={1: line_payload("Hi  there"), 2: line_payload("Bye  now")},
                 records=[(1, 0x20, 18), (2, 0x20, 16)])
    retail = open_image(build(payloads={1: line_payload("Hi  there"),
                                        2: line_payload("Bye now")},
                              records=[(1, 0x20, 18), (2, 0x20, 16)]),
                        tmp_path, name="retail.gba")
    model = open_image(base, tmp_path, name="base.gba", canonical=retail.path)
    built = textedit.plan(model, [textedit.SpacingEdit()])
    assert [row.selector for row in built.spacing] == [2]
    assert built.spacing[0].kept_retail == ()
    assert any("run(s) kept" in warning and "1:36" in warning for warning in built.warnings)
    assert slot_payload(built.output, 1) == slot_payload(base, 1)
    assert built.spacing[0].texts["2:32:16"] == "Bye now"
    assert slot_payload(built.output, 2)[0x20:0x2E].decode("utf-16le") == "Bye now"
    assert textedit.readback(built) == ()


def test_a_spacing_plan_may_not_carry_another_edit(tmp_path: Path) -> None:
    _image, model = simple(tmp_path)
    with pytest.raises(textedit.TextEditError, match="only edit a plan may carry"):
        textedit.plan(model, [textedit.SpacingEdit(),
                              textedit.RecordEdit(1, 0x20, 20, "hello", "hi")])


def test_a_spacing_pass_without_the_canonical_image_is_refused(tmp_path: Path) -> None:
    _image, model = simple(tmp_path)
    built = textedit.plan(model, [textedit.SpacingEdit()])
    assert [item.method for item in built.decisions] == [textedit.REFUSED]
    assert "canonical image" in built.refusals[0].reason
    with pytest.raises(textedit.TextEditError, match="REFUSED"):
        textedit.apply(built, tmp_path / "unused.gba")


# --- proven carriers ---------------------------------------------------------


def test_a_record_shaped_word_outside_the_pool_is_never_written(tmp_path: Path) -> None:
    """The shape filter is near-random outside the pool; a write there is corruption."""
    base = build(payloads={1: line_payload("Hi  there")}, records=[(1, 0x20, 18)])
    handle = DialogueHandle(1, 0x20, 18).encode().to_bytes(4, "little")
    base[0x9000:0x9004] = RECORD_WORD
    base[0x9004:0x9008] = handle
    retail = open_image(build(payloads={1: line_payload("Hi there")},
                              records=[(1, 0x20, 18)]), tmp_path, name="retail.gba")
    model = open_image(base, tmp_path, name="base.gba", canonical=retail.path)
    assert len(model.record(1, 0x20, 18).sites) == 2
    built = textedit.plan(model, [textedit.SpacingEdit()])
    assert built.output[0x9000:0x9008] == base[0x9000:0x9008]
    assert built.output[0x9004:0x9008] == handle
    assert 0x9004 not in built.spacing[0].handles
    assert RECORD_AT + 4 in built.spacing[0].handles
    assert textedit.readback(built) == ()


def test_a_targeted_edit_refuses_a_record_no_pool_word_names(tmp_path: Path) -> None:
    image = build(payloads={1: line_payload("hello there everybody, this is")})
    handle = DialogueHandle(1, 0x20, 0x40).encode().to_bytes(4, "little")
    image[0x9000:0x9004] = RECORD_WORD
    image[0x9004:0x9008] = handle
    model = open_image(image, tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 0x40, "hello", "hi")])
    assert built.decisions[0].method == textedit.REFUSED
    assert "event-resource pool" in built.refusals[0].reason
    with pytest.raises(textedit.TextEditError, match="REFUSED"):
        textedit.apply(built, tmp_path / "unused.gba")


def test_a_refused_relocation_appends_nothing(tmp_path: Path) -> None:
    """N5: the table is settled before the container is appended, so a refusal is inert.

    The guard refuses when the table's literal has a second owner, which is the
    cheapest way to reach the refusal with a container that has to move. The plan
    must then hold the image it was given, with nothing appended: before the fix the
    relocation appended its container first and the refusal left those bytes in the
    buffer for a caller that never exported them.
    """
    base = build(payloads={1: line_payload("Say hello!")}, records=[(1, 0x20, 20)])
    second = bytearray(base)
    second[0x9000:0x9004] = base[TABLE_LITERAL:TABLE_LITERAL + 4]
    model = open_image(bytes(second), tmp_path)
    original = webfoot_lz.build_stored

    def oversized(payload: bytes) -> bytes:
        return original(bytes(payload) + bytes(64))

    with mock.patch.object(webfoot_lz, "build_stored", oversized):
        built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 20, "hello", "hi")])
    assert built.decisions[0].method == textedit.REFUSED
    assert "more than one owner" in built.decisions[0].reason
    assert len(built.output) == len(second)
    assert built.output == bytes(second)


def test_a_spacing_relocation_leaves_every_retail_table_word_alone(tmp_path: Path) -> None:
    """A container that must move on a retail-table image may not write a retail word."""
    base = build(payloads={1: line_payload("Hi  there")}, records=[(1, 0x20, 18)])
    retail = open_image(build(payloads={1: line_payload("Hi there")},
                              records=[(1, 0x20, 18)]), tmp_path, name="retail.gba")
    model = open_image(base, tmp_path, name="base.gba", canonical=retail.path)
    original = webfoot_lz.build_stored

    def oversized(payload: bytes) -> bytes:
        return original(bytes(payload) + bytes(64))

    with mock.patch.object(webfoot_lz, "build_stored", oversized):
        built = textedit.plan(model, [textedit.SpacingEdit()])
    assert built.decisions[0].method == textedit.IN_PLACE
    assert built.output[TABLE_AT:TABLE_AT + TABLE_BYTES] == base[TABLE_AT:TABLE_AT + TABLE_BYTES]
    table = int.from_bytes(built.output[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    assert table >= len(base)
    entry = int.from_bytes(built.output[table + 4:table + 8], "little")
    assert entry >= ROM_BASE + len(base)
    assert built.output[TABLE_AT + 4:TABLE_AT + 8] == base[TABLE_AT + 4:TABLE_AT + 8]
    assert any("container table is copied" in warning for warning in built.warnings)


def test_an_in_place_relocation_leaves_every_retail_table_word_alone(tmp_path: Path) -> None:
    """F1: the in-place phase used to write the retail table before the table moved."""
    base = build(payloads={1: line_payload("Say hello!")}, records=[(1, 0x20, 20)])
    model = open_image(base, tmp_path)
    original = webfoot_lz.build_stored

    def oversized(payload: bytes) -> bytes:
        return original(bytes(payload) + bytes(64))

    with mock.patch.object(webfoot_lz, "build_stored", oversized):
        built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 20, "hello", "hi")])
    assert built.decisions[0].method == textedit.IN_PLACE
    assert built.output[TABLE_AT:TABLE_AT + TABLE_BYTES] == base[TABLE_AT:TABLE_AT + TABLE_BYTES]
    table = int.from_bytes(built.output[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    assert table >= len(base)
    assert int.from_bytes(built.output[table + 4:table + 8], "little") >= ROM_BASE + len(base)
    assert any("container table is copied" in warning for warning in built.warnings)


# --- the per-occurrence decision ---------------------------------------------


def test_a_record_holding_both_actors_renames_only_the_retail_occurrence() -> None:
    text, renamed, kept, unclear = textedit.rename_positions(
        "I want to see Videl and Videl  compete",
        "I want to see Goten and Videl  compete", old="Videl", new="Lazuli")
    assert text == "I want to see Videl and Lazuli  compete"
    assert (renamed, kept, unclear) == (1, 1, 0)


def test_an_occurrence_with_no_retail_name_is_counted_unclear() -> None:
    text, renamed, kept, unclear = textedit.rename_positions(
        "Videl and Videl", "Videl and      ", old="Videl", new="Lazuli")
    assert text == "Lazuli and Videl"
    assert (renamed, kept, unclear) == (1, 0, 1)


def test_a_rename_refuses_when_the_offsets_do_not_correspond() -> None:
    with pytest.raises(textedit.TextEditError, match="do not correspond"):
        textedit.rename_positions("Videl is here", "Videl was here", old="Videl",
                                  new="Lazuli")


# --- destination refusal -----------------------------------------------------


def test_apply_refuses_the_input_file_as_its_own_destination(tmp_path: Path) -> None:
    _image, model = simple(tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 20, "hello", "hi")])
    before = model.path.read_bytes()
    with pytest.raises(textedit.TextEditError, match="REFUSED"):
        textedit.apply(built, model.path)
    assert model.path.read_bytes() == before


def test_apply_refuses_a_destination_inside_the_protected_rom_directory(tmp_path: Path) -> None:
    _image, model = simple(tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 20, "hello", "hi")])
    target = Path(REPOSITORY_ROOT) / "roms" / "textedit-refused-output.gba"
    with pytest.raises(textedit.TextEditError, match="protected ROM input"):
        textedit.apply(built, target)
    assert not target.exists()


def test_apply_refuses_the_canonical_reference_as_its_own_destination(tmp_path: Path) -> None:
    image, _model = simple(tmp_path)
    retail = open_image(image, tmp_path, name="retail.gba")
    model = open_image(image, tmp_path, name="edited.gba", canonical=retail.path)
    assert model.retail_path == retail.path
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 20, "hello", "hi")])
    before = retail.path.read_bytes()
    with pytest.raises(textedit.TextEditError, match="REFUSED"):
        textedit.apply(built, retail.path)
    assert retail.path.read_bytes() == before


def test_apply_refuses_to_overwrite_an_existing_output(tmp_path: Path) -> None:
    _image, model = simple(tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 20, "hello", "hi")])
    target = tmp_path / "existing.gba"
    target.write_bytes(b"already here")
    with pytest.raises(textedit.TextEditError, match="overwrite"):
        textedit.apply(built, target)
    assert target.read_bytes() == b"already here"


# --- detection ---------------------------------------------------------------


def test_an_image_with_a_foreign_game_code_is_refused(tmp_path: Path) -> None:
    image = build()
    image[0xAC:0xB0] = b"BL2E"
    path = tmp_path / "foreign.gba"
    path.write_bytes(image)
    with pytest.raises(textedit.TextEditError, match="game code"):
        textedit.open_rom(path)


def test_an_image_whose_live_selector_is_not_a_container_is_refused(tmp_path: Path) -> None:
    image = build()
    image[TABLE_AT + 3 * 4:TABLE_AT + 3 * 4 + 4] = (ROM_BASE + 0x1230).to_bytes(4, "little")
    path = tmp_path / "broken.gba"
    path.write_bytes(image)
    with pytest.raises(textedit.TextEditError, match="live selector 3"):
        textedit.open_rom(path)


def test_an_image_truncated_inside_the_table_cannot_skip_a_live_selector(tmp_path: Path) -> None:
    image = build()
    path = tmp_path / "truncated.gba"
    path.write_bytes(image[:TABLE_AT + 6 * 4])
    with pytest.raises(textedit.TextEditError, match="does not hold 7 live selectors"):
        textedit.open_rom(path)


# --- the release goldens -----------------------------------------------------

GOLDEN_DIRECTORY = Path(REPOSITORY_ROOT) / "roms"
RELEASE3 = "521bd0fa0a8bc198f36430e3419184807e335fa588bd718152996c076a8f15fd"
RELEASE31 = "f5c9648bbf7a9b448d801866cc775eb76abd270f7c16fb93d4e01630ef236201"
RELEASE3_BASE = "018757c4e0dda9f463364675f32b307dff9e5ad89c7a0b932939aec320032389"
RELEASE3_STAGE_INPUT = "639570e7dd05a963a85750e192ff261d6b498da9225c18d1670bc0c484c49ba9"

#: The five owner-approved wording edits of release 3, in the release's own order.
RELEASE3_EDITS = (
    (1, 38856, 252, "Great Soy Man", "Great Soyman"),
    (1, 58162, 46, "Yamcha", "Bandit"),
    (1, 62104, 138, "Yamcha  also", "Bandit also"),
    (1, 44704, 468, "Yamcha's  boy", "Bandit's boy"),
    (2, 59518, 102, "Yamcha  once", "Bandit once"),
)
#: The window release 3's two non-text stages own: the enemy stat table and the
#: behaviour words the boss retune and the profile write.
RELEASE3_STAT_WINDOW = (0x70F7E4, 0x711BCE)


def golden(name: str) -> Path:
    path = GOLDEN_DIRECTORY / name
    if not path.is_file():
        pytest.skip(f"{name} is not staged under roms/")
    return path


def canonical() -> Path:
    path = canonical_rom_path()
    if path is None:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    return path


def test_the_release3_wording_stage_replays_byte_identically(tmp_path: Path) -> None:
    stage = golden("v3-release3.2-profile.gba")
    if hashlib.sha256(stage.read_bytes()).hexdigest() != RELEASE3_STAGE_INPUT:
        pytest.skip("the staged release-3 stage input is not the published one")
    model = textedit.open_rom(stage, canonical=canonical())
    built = textedit.plan(model, [textedit.RecordEdit(*edit) for edit in RELEASE3_EDITS])
    assert all(item.method == textedit.IN_PLACE for item in built.decisions)
    assert built.output_sha256 == RELEASE3
    textedit.apply(built, tmp_path / "release3.gba")


def test_the_release3_edit_list_from_its_base_differs_only_in_the_non_text_stages(
        tmp_path: Path) -> None:
    base = golden("v3-wt-split-2-1-a.gba")
    released = golden("v3-release3.gba")
    if hashlib.sha256(base.read_bytes()).hexdigest() != RELEASE3_BASE:
        pytest.skip("the staged release-3 base is not the published one")
    model = textedit.open_rom(base, canonical=canonical())
    built = textedit.plan(model, [textedit.RecordEdit(*edit) for edit in RELEASE3_EDITS])
    published = released.read_bytes()
    assert len(published) > len(built.output)
    differing = [index for index in range(len(built.output))
                 if built.output[index] != published[index]]
    assert differing
    assert all(RELEASE3_STAT_WINDOW[0] <= index <= RELEASE3_STAT_WINDOW[1]
               for index in differing)
    assert published[len(built.output):] == \
        golden("v3-release3.2-profile.gba").read_bytes()[len(built.output):]


def test_the_canonical_table_words_are_untouched_when_a_record_moves(tmp_path: Path) -> None:
    rom = canonical()
    image = rom.read_bytes()
    table = int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    model = textedit.open_rom(rom)
    target = model.record(1, 38856, 252)
    assert target is not None
    built = textedit.plan(model, [textedit.RecordEdit(1, 38856, 252, target.text,
                                                      target.text + " and more")])
    assert built.decisions[0].method == textedit.MOVE
    assert built.output[table:table + TABLE_BYTES] == image[table:table + TABLE_BYTES]
    moved = int.from_bytes(built.output[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    assert moved >= len(image)
    pointer = int.from_bytes(built.output[moved + 7 * 4:moved + 7 * 4 + 4], "little")
    assert ROM_BASE <= pointer < ROM_BASE + len(built.output)
    assert textedit.readback(built) == ()
    textedit.apply(built, tmp_path / "canonical-move.gba")


def test_the_release31_rename_replays_except_the_release_own_out_of_pool_writes(
        tmp_path: Path) -> None:
    """Release 3.1 wrote nine words the shape filter matched outside the pool.

    Every in-pool handle word it wrote is reproduced byte-identically; the nine are
    a shape coincidence in code and graphics that this engine refuses to write, so
    the published digest is reproduced everywhere except there.
    """
    model = textedit.open_rom(golden("v3-release3.gba"), canonical=canonical())
    built = textedit.plan(model, [textedit.RenameEdit(
        old="Videl", new="Lazuli",
        retail_test="an occurrence is renamed only where the canonical ROM says 'Videl' at the "
                    "same place",
        relocated_slots=(138, 172, 1066))])
    methods = {}
    for item in built.decisions:
        methods[item.method] = methods.get(item.method, 0) + 1
    assert methods == {textedit.MOVE: 37}
    assert len(built.placements) == 34
    assert len(built.slot_moves) == 3
    assert len(built.listed) == 68
    published = golden("v3-release31.gba").read_bytes()
    assert len(built.output) == len(published)
    differing = [index for index in range(len(published))
                 if built.output[index] != published[index]]
    words = sorted({index - index % 4 for index in differing})
    assert words == [0x316A18, 0x40E178, 0x4567CC, 0x46C29C, 0x4D99A8, 0x545A04,
                     0x5C6FB4, 0x725474, 0x726074]
    pool = textedit.PROVEN_HANDLE_POOL
    assert all(not pool[0] <= word < pool[1] for word in words)
    for row in built.placements:
        for site in row.sites:
            assert built.output[site:site + 4] == published[site:site + 4]
    assert textedit.readback(built) == ()
    textedit.apply(built, tmp_path / "release31.gba")
