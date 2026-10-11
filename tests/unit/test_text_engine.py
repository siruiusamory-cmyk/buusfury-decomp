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
from tests.text_fixture import (
    ROM_BASE,
    TABLE_AT,
    TABLE_BYTES,
    TABLE_LITERAL,
    build,
    line_payload,
    open_image,
    simple,
    slot_payload,
)
from tools.webfoot import textedit
from tools.webfoot.formats import text_tables as tt
from tools.webfoot.handles import unpack_handle


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


def test_text_units_split_at_every_control_unit() -> None:
    assert textedit.units("Hey, you!") == (textedit.Text("Hey, you!"),)
    assert textedit.units("Hey\x08\x03you\x0a!") == (
        textedit.Text("Hey"),
        textedit.Control("\x08\x03", 0x08, "\x03"),
        textedit.Text("you"),
        textedit.Control("\x0a", 0x0A),
        textedit.Text("!"),
    )
    # A trailing 0x0008 with no halfword left still reads as one locked unit.
    assert textedit.units("ok\x08") == (textedit.Text("ok"), textedit.Control("\x08", 0x08))
    assert textedit.locked_tokens("Hey\x08\x03you\x0a!") == ("\x08\x03", "\x0a")


def test_every_rename_occurrence_carries_its_own_retail_decision() -> None:
    current = "Videl then Videl then Videl"
    counterpart = "Goten then Videl then ....."
    assert textedit.rename_occurrences(current, counterpart, "Videl") == (
        textedit.Occurrence(at=0, retail="Goten", decision=textedit.KEEP),
        textedit.Occurrence(at=11, retail="Videl", decision=textedit.RENAME),
        textedit.Occurrence(at=22, retail=".....", decision=textedit.UNCLEAR),
    )
    text, renamed, kept, unclear = textedit.rename_positions(
        current, counterpart, old="Videl", new="Lazul")
    assert (text, renamed, kept, unclear) == ("Videl then Lazul then Videl", 1, 1, 1)


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


def test_a_mixed_plan_leaves_the_retail_table_words_alone(tmp_path: Path) -> None:
    """F1: a container relocated in place must not write the image's own table.

    ``1:5498:12`` reads ``Arqua!``; a same-length swap makes container 1 re-pack
    over its room, so the plan both relocates that container in place and moves a
    record. Before the table was relocated first, this wrote retail table slot 1
    at file 0x7B5B68 (f0047a08 -> 00008008) and ``readback`` still returned clean.
    """
    rom = canonical()
    image = rom.read_bytes()
    table = int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    assert table == 0x7B5B64
    model = textedit.open_rom(rom)
    grown = model.record(1, 5498, 12)
    mover = model.record(1, 38856, 252)
    assert grown is not None
    assert mover is not None
    built = textedit.plan(model, [
        textedit.RecordEdit(1, 5498, 12, grown.text, "B" + grown.text[1:]),
        textedit.RecordEdit(1, 38856, 252, mover.text, mover.text + " and more"),
    ])
    assert [item.method for item in built.decisions] == [textedit.IN_PLACE, textedit.MOVE]
    assert [change.what for change in built.changes if "relocated" in change.what] == \
        ["container 1 relocated"]
    assert built.output[table:table + TABLE_BYTES] == image[table:table + TABLE_BYTES]
    assert textedit.readback(built) == ()
    textedit.apply(built, tmp_path / "canonical-mixed.gba")


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
