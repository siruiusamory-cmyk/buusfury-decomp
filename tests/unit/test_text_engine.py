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


def open_image(image, directory, **kwargs):
    path = Path(directory) / "fixture.gba"
    path.write_bytes(image)
    with mock.patch.object(textedit.engine, "MINIMUM_DIALOGUE_RECORDS", 1):
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


def test_the_first_use_of_the_grown_slot_warns_that_the_slot_was_taken(tmp_path: Path) -> None:
    text = "hello there everybody, this is"
    image = build(payloads={1: line_payload(text)},
                  records=[(1, 0x20, 0x40), (1, 0x30, 0x10)])
    model = open_image(image, tmp_path)
    built = textedit.plan(model, [textedit.RecordEdit(1, 0x20, 0x40, "hello", "hi")])
    assert any("did not name a container" in warning for warning in built.warnings)
    assert slot_payload(built.output, 7).decode("utf-16le").startswith(
        "hi there everybody, this is")


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


def test_the_release31_rename_replays_byte_identically(tmp_path: Path) -> None:
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
    assert len(built.listed) == 60
    assert len(built.slot_moves) == 3
    assert built.output_sha256 == RELEASE31
    textedit.apply(built, tmp_path / "release31.gba")
