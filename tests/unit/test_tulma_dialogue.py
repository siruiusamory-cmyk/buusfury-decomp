"""FRIEND-V3-TULMA-GRAPHICS-001 dialogue expansion: the dialogue writer's own guards.

These build a synthetic image with the real shapes - a stored (kind 0) container, and record
words of the structure the engine's own dispatch reads - so every refusal and every byte of the
write is checked without a ROM and without the private artwork.
"""

from __future__ import annotations

import struct

import pytest

from tools.research import apply_tulma_dialogue as td
from tools.webfoot.formats import webfoot_lz as wl
from tools.webfoot.handles import pack_handle

#: The synthetic layout keeps each region clear of the others: the record words that name a
#: record must live OUTSIDE the container's payload, exactly as they do in the real image, or
#: writing a handle would show up as a payload change.
CONTAINER_OFFSET = 0x13000
TABLE_OFFSET = 0x12400
RECORD_SITE = 0x1000
SECOND_RECORD_SITE = 0x1010
IMAGE_SIZE = 0x24000
PAYLOAD_SIZE = 61000


def _payload(second_start: int | None = None) -> bytearray:
    """A decoded stream with both old lines at the offsets the writer names."""
    payload = bytearray(PAYLOAD_SIZE)
    for target in td.TARGETS:
        start = target["decoded_start"] if (second_start is None
                                            or target["speaker"] == "bulma") else second_start
        text = target["old_text"].encode("utf-16le")
        payload[start:start + len(text)] = text
    return payload


def _record_word(site: int, selector: int, start: int, length: int) -> bytes:
    """A record word of the shape the dispatch reads: index, 0x00, 0x05, then the handle."""
    return bytes([0x00, 0x00, 0x05, 0x00]) + struct.pack(
        "<I", pack_handle(selector, start, length))


def _image(payload: bytearray | None = None, *, sites: dict[str, int | None] | None = None,
           stored: bool = True) -> bytes:
    payload = _payload() if payload is None else payload
    image = bytearray(IMAGE_SIZE)
    body = bytes(payload)
    if stored:
        container = struct.pack("<II", 0, len(body)) + body
    else:
        container = wl.pack(body, kind=1)
    image[CONTAINER_OFFSET:CONTAINER_OFFSET + len(container)] = container
    struct.pack_into("<I", image, TABLE_OFFSET + td.SELECTOR * 4,
                     td.ROM_BASE + CONTAINER_OFFSET)
    struct.pack_into("<I", image, td.TABLE_LITERAL, td.ROM_BASE + TABLE_OFFSET)
    sites = sites if sites is not None else {"bulma": RECORD_SITE, "tulma": SECOND_RECORD_SITE}
    for target in td.TARGETS:
        site = sites.get(target["speaker"])
        if site is None:
            continue
        word = _record_word(site, td.SELECTOR, target["decoded_start"],
                            target["decoded_length"])
        image[site:site + len(word)] = word
    return bytes(image)


def test_the_two_slots_receive_their_own_speaker_wording():
    planned = td.plan(_image())
    out = td.apply(_image(), planned)
    report = td.verify(_image(), out, planned)
    assert report["read_back"]["tulma"] == td.TARGETS[1]["new_text"]
    assert report["read_back"]["bulma"] == td.TARGETS[0]["new_text"]


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


def test_a_span_that_does_not_hold_the_expected_wording_is_refused():
    payload = _payload()
    payload[td.TARGETS[0]["decoded_start"]] = ord("X")
    with pytest.raises(td.TulmaDialogueError, match="does not hold the wording"):
        td.plan(_image(payload))


def test_records_that_are_not_adjacent_are_refused(monkeypatch):
    """A gap between the two slots means growing one would move every record after it."""
    offset = td.TARGETS[1]["decoded_start"] + 4
    monkeypatch.setitem(td.TARGETS[1], "decoded_start", offset)
    image = _image(_payload(second_start=offset))
    with pytest.raises(td.TulmaDialogueError, match="not adjacent"):
        td.plan(image)


def test_a_pair_with_too_little_room_is_refused(monkeypatch):
    monkeypatch.setitem(td.TARGETS[0], "new_text", "Look at how mad Tulma is! " * 4)
    with pytest.raises(td.TulmaDialogueError, match="region holds"):
        td.plan(_image())


def test_a_replacement_carrying_a_control_unit_is_refused(monkeypatch):
    monkeypatch.setitem(td.TARGETS[1], "new_text", "Line one\nLine two")
    with pytest.raises(td.TulmaDialogueError, match="control unit"):
        td.plan(_image())


def test_a_container_that_is_not_stored_is_refused():
    with pytest.raises(td.TulmaDialogueError, match="not proven"):
        td.plan(_image(stored=False))


def test_a_record_no_word_names_is_refused():
    """With no record word, the reader does not see the record at all, and the plan refuses."""
    image = _image(sites={"bulma": RECORD_SITE, "tulma": None})
    with pytest.raises(td.TulmaDialogueError, match="no record carries"):
        td.plan(image)


def test_a_handle_word_that_is_not_the_one_replaced_is_refused():
    image = bytearray(_image())
    # A legal-looking but different handle at the second site: the stale-base check must fire.
    struct.pack_into("<I", image, SECOND_RECORD_SITE + 4,
                     pack_handle(td.SELECTOR, td.TARGETS[1]["decoded_start"] + 2,
                                 td.TARGETS[1]["decoded_length"]))
    with pytest.raises(td.TulmaDialogueError, match="no record carries|not the one replaced"):
        td.plan(bytes(image))


def test_verify_refuses_a_change_outside_the_region():
    base = _image()
    planned = td.plan(base)
    out = bytearray(td.apply(base, planned))
    out[CONTAINER_OFFSET + 8 + 4] ^= 0xFF
    with pytest.raises(td.TulmaDialogueError, match="outside the region"):
        td.verify(base, bytes(out), planned)


def test_verify_refuses_output_that_still_holds_the_old_wording():
    base = _image()
    planned = td.plan(base)
    out = bytearray(td.apply(base, planned))
    at = planned["region_file_offset"]
    text = td.TARGETS[0]["old_text"].encode("utf-16le")
    out[at:at + len(text)] = text
    with pytest.raises(td.TulmaDialogueError, match="does not read the new line|old wording"):
        td.verify(base, bytes(out), planned)


def test_run_refuses_a_base_whose_digest_is_not_the_expected_one(tmp_path):
    path = tmp_path / "base.gba"
    path.write_bytes(_image())
    with pytest.raises(td.TulmaDialogueError, match="not the base this rewrite was proven"):
        td.run(path, "00" * 32, tmp_path / "out.gba", tmp_path / "report.json")


def test_run_writes_the_image_and_a_report(tmp_path):
    base = _image()
    path = tmp_path / "base.gba"
    path.write_bytes(base)
    report = td.run(path, td.sha256(base), tmp_path / "out.gba", tmp_path / "report.json")
    assert report["output_sha256"] == td.sha256((tmp_path / "out.gba").read_bytes())
    assert report["verification"]["read_back"]["tulma"] == td.TARGETS[1]["new_text"]
    assert (tmp_path / "report.json").exists()
