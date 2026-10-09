"""The dialogue engine's guards, and its rule that wording is a locator and never proof.

These build a synthetic image with the real shapes: a stored (kind 0) container, and record
words of the structure the engine's own reader walks. No ROM and no private artwork is needed.
The ambiguity rules are exercised directly, because they are the ones the owner asked for: zero
matches refused, more than one match refused with every candidate named, a stated span that
contradicts the wording refused, and a speaker reported as a claim beside the evidence a human
can check it against.
"""

from __future__ import annotations

import json
import os
import struct

import pytest

from tools.research import apply_tulma_dialogue as td
from tools.webfoot import character_swap, dialogue_edit
from tools.webfoot.dialogue_edit import DialogueEditError, DialogueRewrite, LineEdit
from tools.webfoot.formats import webfoot_lz as wl
from tools.webfoot.handles import pack_handle
from tools.webfoot.write import WriteError

#: The synthetic layout keeps each region clear of the others: the record words that name a
#: record must live OUTSIDE the container's payload, exactly as they do in the real image, or
#: writing a handle would show up as a payload change.
CONTAINER_OFFSET = 0x13000
TABLE_OFFSET = 0x12400
RECORD_SITE = 0x1000
SECOND_RECORD_SITE = 0x1010
THIRD_RECORD_SITE = 0x1020
IMAGE_SIZE = 0x24000
PAYLOAD_SIZE = 61000

BULMA, TULMA = td.TARGETS


def _payload(second_start: int | None = None, duplicate: int | None = None,
             targets: tuple[LineEdit, ...] | None = None) -> bytearray:
    """A decoded stream with both old lines at the offsets the given targets name."""
    payload = bytearray(PAYLOAD_SIZE)
    for edit in targets or td.TARGETS:
        start = edit.decoded_start
        if second_start is not None and edit.speaker == "tulma":
            start = second_start
        text = edit.old_text.encode("utf-16le")
        payload[start:start + len(text)] = text
    if duplicate is not None:
        text = BULMA.old_text.encode("utf-16le")
        payload[duplicate:duplicate + len(text)] = text
    return payload


def _record_word(site: int, selector: int, start: int, length: int) -> bytes:
    """A record word of the shape the dispatch reads: index, 0x00, 0x05, then the handle."""
    return bytes([0x00, 0x00, 0x05, 0x00]) + struct.pack(
        "<I", pack_handle(selector, start, length))


def _image(payload: bytearray | None = None, *, sites: dict[str, int | None] | None = None,
           stored: bool = True, extra: tuple[int, int, int] | None = None,
           targets: tuple[LineEdit, ...] | None = None) -> bytes:
    payload = _payload() if payload is None else payload
    image = bytearray(IMAGE_SIZE)
    body = bytes(payload)
    container = (struct.pack("<II", 0, len(body)) + body if stored
                 else wl.pack(body, kind=1))
    image[CONTAINER_OFFSET:CONTAINER_OFFSET + len(container)] = container
    struct.pack_into("<I", image, TABLE_OFFSET + td.SELECTOR * 4,
                     td.ROM_BASE + CONTAINER_OFFSET)
    struct.pack_into("<I", image, td.TABLE_LITERAL, td.ROM_BASE + TABLE_OFFSET)
    sites = {"bulma": RECORD_SITE, "tulma": SECOND_RECORD_SITE} if sites is None else sites
    for edit in targets or td.TARGETS:
        site = sites.get(edit.speaker)
        if site is None:
            continue
        word = _record_word(site, td.SELECTOR, edit.decoded_start, edit.decoded_length)
        image[site:site + len(word)] = word
    if extra is not None:
        site, start, length = extra
        image[site:site + 8] = _record_word(site, td.SELECTOR, start, length)
    return bytes(image)


def _rewrite(*edits: LineEdit) -> DialogueRewrite:
    return DialogueRewrite(selector=td.SELECTOR, lines=edits)


# --- the write ------------------------------------------------------------------------------


def test_the_two_records_receive_their_own_wording():
    base = _image()
    planned = td.plan(base)
    out = td.apply(base, planned)
    report = td.verify(base, out, planned)
    assert report["read_back"]["bulma"] == BULMA.new_text
    assert report["read_back"]["tulma"] == TULMA.new_text


def test_the_diff_is_confined_to_the_region_and_the_handle_words():
    base = _image()
    planned = td.plan(base)
    out = td.apply(base, planned)
    report = td.verify(base, out, planned)
    assert report["image_bytes_changed"] == (report["image_bytes_changed_in_region"]
                                             + report["handle_words_changed"])
    assert report["container_packed_size_before"] == report["container_packed_size_after"]


def test_the_new_handles_are_written_at_every_site_the_reader_reports():
    base = _image()
    planned = td.plan(base)
    out = td.apply(base, planned)
    for handle in planned["handles"]:
        for site in handle["sites"]:
            assert struct.unpack_from("<I", out, site)[0] == handle["new_handle"]
    # The reader reports the HANDLE FIELD's offset, which is the record word plus four.
    assert [h["sites"] for h in planned["handles"]] == [[RECORD_SITE + 4],
                                                        [SECOND_RECORD_SITE + 4]]


# --- wording is a locator, never proof of who speaks ----------------------------------------


def test_a_wording_no_record_holds_is_refused():
    payload = _payload()
    payload[BULMA.decoded_start] = ord("X")
    with pytest.raises(DialogueEditError, match="no record in selector"):
        td.plan(_image(payload))


def test_a_wording_two_records_hold_is_refused_and_every_candidate_is_named():
    """Never pick the first match: an ambiguous wording is refused, with both records listed."""
    copy_at = 30000
    image = _image(_payload(duplicate=copy_at), extra=(THIRD_RECORD_SITE, copy_at, 112))
    with pytest.raises(DialogueEditError) as caught:
        dialogue_edit.find_record(image, td.SELECTOR, BULMA.old_text)
    message = str(caught.value)
    assert "2 records in selector" in message
    assert f"({BULMA.decoded_start}, {BULMA.decoded_length})" in message
    assert f"({copy_at}, 112)" in message


def test_a_stated_span_that_contradicts_the_wording_is_refused():
    wrong = BULMA._replace(decoded_start=BULMA.decoded_start + 2)
    with pytest.raises(DialogueEditError, match="refusing a contradiction"):
        dialogue_edit.plan(_image(), _rewrite(wrong, TULMA))


def test_a_stated_span_that_agrees_with_the_wording_is_accepted():
    """The preset states both spans, so this is the path its own run takes."""
    planned = td.plan(_image())
    assert [h["was"] for h in planned["handles"]] == [[60182, 112], [60294, 138]]


def test_the_speaker_is_reported_as_a_claim_with_the_evidence_a_human_can_check():
    planned = td.plan(_image())
    for handle in planned["handles"]:
        evidence = handle["context"]
        assert evidence["speaker_evidence"].startswith("caller-claim")
        assert evidence["record_sites"], "the record's naming words are the checkable evidence"
        assert evidence["record_sites_hex"] == [hex(site) for site in evidence["record_sites"]]


def test_the_context_reports_an_enclosing_view_that_covers_the_record():
    """A scene view spanning both records is context, not a second target: it holds no line."""
    image = _image(extra=(THIRD_RECORD_SITE, 60000, 400))
    planned = dialogue_edit.plan(image, _rewrite(BULMA, TULMA))
    enclosing = [list(record) for record in planned["handles"][0]["context"]["enclosing_records"]]
    assert [60000, 400] in enclosing


# --- the other guards -----------------------------------------------------------------------


def test_records_that_are_not_adjacent_are_refused():
    offset = TULMA.decoded_start + 4
    shifted = TULMA._replace(decoded_start=offset)
    targets = (BULMA, shifted)
    image = _image(_payload(second_start=offset, targets=targets), targets=targets)
    with pytest.raises(DialogueEditError, match="not adjacent"):
        dialogue_edit.plan(image, _rewrite(BULMA, shifted))


def test_a_group_with_too_little_room_is_refused():
    longer = BULMA._replace(new_text="Look at how mad Tulma is! " * 4)
    with pytest.raises(DialogueEditError, match="region holds"):
        dialogue_edit.plan(_image(), _rewrite(longer, TULMA))


def test_a_replacement_carrying_a_control_unit_is_refused():
    with pytest.raises(DialogueEditError, match="control unit"):
        dialogue_edit.plan(_image(), _rewrite(BULMA, TULMA._replace(new_text="Line\nLine")))


def test_a_container_that_is_not_stored_is_refused():
    with pytest.raises(DialogueEditError, match="not proven"):
        td.plan(_image(stored=False))


def test_a_record_no_word_names_is_refused():
    """With no record word the reader never sees the record, so there is nothing to edit."""
    image = _image(sites={"bulma": RECORD_SITE, "tulma": None})
    with pytest.raises(DialogueEditError, match="no record in selector"):
        td.plan(image)


def test_a_handle_word_that_is_not_the_one_replaced_is_refused():
    image = bytearray(_image())
    # A legal-looking but different handle at the second site: the stale-base check must fire.
    struct.pack_into("<I", image, SECOND_RECORD_SITE + 4,
                     pack_handle(td.SELECTOR, TULMA.decoded_start + 2, TULMA.decoded_length))
    with pytest.raises(DialogueEditError, match="no record in selector|not the one replaced"):
        td.plan(bytes(image))


def test_verify_refuses_a_change_outside_the_region():
    base = _image()
    planned = td.plan(base)
    out = bytearray(td.apply(base, planned))
    out[CONTAINER_OFFSET + 8 + 4] ^= 0xFF
    with pytest.raises(DialogueEditError, match="outside the region"):
        td.verify(base, bytes(out), planned)


def test_verify_refuses_output_that_still_holds_the_old_wording():
    base = _image()
    planned = td.plan(base)
    out = bytearray(td.apply(base, planned))
    at = planned["region_file_offset"]
    text = BULMA.old_text.encode("utf-16le")
    out[at:at + len(text)] = text
    with pytest.raises(DialogueEditError, match="does not read the new line|old wording"):
        td.verify(base, bytes(out), planned)


# --- the command ----------------------------------------------------------------------------


def test_run_refuses_a_base_whose_digest_is_not_the_expected_one(tmp_path):
    path = tmp_path / "base.gba"
    path.write_bytes(_image())
    with pytest.raises(DialogueEditError, match="not the image this swap was proven"):
        td.run(path, "00" * 32, tmp_path / "out.gba", tmp_path / "report.json")


def test_run_writes_the_image_and_a_report(tmp_path):
    base = _image()
    path = tmp_path / "base.gba"
    path.write_bytes(base)
    report = td.run(path, td.sha256(base), tmp_path / "out.gba", tmp_path / "report.json")
    assert report["output_sha256"] == td.sha256((tmp_path / "out.gba").read_bytes())
    assert report["verification"]["read_back"]["tulma"] == TULMA.new_text
    assert (tmp_path / "report.json").exists()


def test_run_refuses_to_write_over_its_own_input(tmp_path):
    """The source-alias rule: a source is an input on every path and an output on none."""
    base = _image()
    path = tmp_path / "base.gba"
    path.write_bytes(base)
    with pytest.raises(WriteError, match="same file"):
        td.run(path, td.sha256(base), path, tmp_path / "report.json")
    assert path.read_bytes() == base


def test_run_refuses_a_hard_link_of_its_own_input(tmp_path):
    """A hard link is the same file, so it must be refused by identity and not by name."""
    base = _image()
    path = tmp_path / "base.gba"
    path.write_bytes(base)
    alias = tmp_path / "candidate.gba"
    os.link(path, alias)
    with pytest.raises(WriteError, match="same file"):
        td.run(path, td.sha256(base), alias, tmp_path / "report.json")
    assert path.read_bytes() == base


def test_run_refuses_a_report_that_is_its_own_input(tmp_path):
    base = _image()
    path = tmp_path / "base.gba"
    path.write_bytes(base)
    with pytest.raises(WriteError, match="same file"):
        td.run(path, td.sha256(base), tmp_path / "out.gba", path)
    assert path.read_bytes() == base


def test_a_spec_driven_rewrite_produces_the_same_bytes_as_the_preset(tmp_path):
    """The invocable front end and the ticket's preset must agree byte for byte."""
    base = _image()
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"operations": [
        {"kind": "dialogue", "selector": td.SELECTOR,
         "lines": [{"speaker": edit.speaker, "old": edit.old_text, "new": edit.new_text,
                    "record": [edit.decoded_start, edit.decoded_length]}
                   for edit in td.TARGETS]}]}), encoding="utf-8")
    spec_out, report = character_swap.apply_spec(base, spec)
    preset_out = td.apply(base, td.plan(base))
    assert spec_out == preset_out
    assert report["passes"][0]["verification"]["read_back"]["tulma"] == TULMA.new_text
