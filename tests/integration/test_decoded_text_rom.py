"""TEXT-INDEX-001 ROM-gated acceptance: the phrase the toolkit could not find.

This is the one exit criterion that cannot be shown on synthetic data. Text the
game displays lives inside a compressed container, so no offset in the image
holds it; before this ticket every search surface missed it entirely.

The assertions are deliberately a lookup, not a dump: the container's ROM file
offset and the phrase's offset within the decoded stream. No surrounding
dialogue is embedded here, and nothing this test produces is written into
tracked files.

Skips cleanly when the canonical ROM is absent, so the portable suite stays
runnable without proprietary data. The ROM is opened read-only and is verified
unchanged afterwards.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os

import pytest

from tools.webfoot.atlas_producers import scan


CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: The acceptance phrase. A single short in-game line, used as the lookup key.
PHRASE = "Good luck, Goku!"

#: CONFIRMED. The container reached by slot 1 of the seeded compressed-text
#: pointer table, and the byte offset of PHRASE within that container's decoded
#: stream. The decoded offset is NOT a ROM address and must never be added to
#: the container offset to make one.
CONTAINER_FILE_OFFSET = 0x7A04F0
DECODED_OFFSET_OF_PHRASE = 0x132


def _rom_path() -> str:
    matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    if hashlib.sha256(open(matches[0], "rb").read()).hexdigest() != CANONICAL_SHA256:
        pytest.skip("local ROM is not the canonical profile these offsets target")
    return matches[0]


@pytest.fixture
def image() -> bytes:
    with open(_rom_path(), "rb") as stream:
        return stream.read()


def test_the_acceptance_phrase_is_located_in_a_decoded_container(image: bytes):
    """The phrase is indexed, with its container's ROM offset and its own."""
    rows = scan._decoded_text_rows(image)

    hits = [row for row in rows if PHRASE in row["text"]]
    assert len(hits) == 1, f"expected exactly one indexed run carrying the phrase, got {len(hits)}"

    row = hits[0]
    assert row["container_file_offset"] == CONTAINER_FILE_OFFSET
    assert row["decompressor"] == "webfoot_lz"
    assert row["encoding"] == "utf16le"

    # Two UTF-16LE bytes per character, so the character index doubles into the
    # decoded-stream byte offset the phrase starts at.
    found = row["text"].index(PHRASE)
    assert row["decoded_offset"] + found * 2 == DECODED_OFFSET_OF_PHRASE


def test_the_indexed_record_never_claims_a_rom_offset_for_decoded_text(image: bytes):
    """Only the container has a ROM address; the decoded text has none."""
    row = next(r for r in scan._decoded_text_rows(image) if PHRASE in r["text"])

    assert "file_offset" not in row
    assert "gba_address" not in row
    assert row["container_rom_address"] == f"0x{scan.BASE + CONTAINER_FILE_OFFSET:08X}"


def test_the_cli_finds_the_phrase_and_marks_it_decoded(tmp_path, capsys, image: bytes):
    """`atlas text` reports the phrase as a decoded match, not a raw ROM run."""
    from tools.webfoot import atlas_build as ab
    from tools.webfoot.cli import main

    import sys
    sys.path.insert(0, os.path.join("tests", "unit"))
    from test_atlas_build import _artifacts

    directory = _artifacts(tmp_path)
    ab.write_atlas(ab.build_atlas(directory), directory / "atlas.jsonl")

    rows = [r for r in scan._decoded_text_rows(image) if PHRASE in r["text"]]
    (directory / "scan_decoded_text.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    assert main(["atlas", "--atlas", str(directory / "atlas.jsonl"),
                 "text", PHRASE]) == 0
    result = json.loads(capsys.readouterr().out)

    assert result["decoded_matched"] == 1
    hit = result["decoded"][0]
    assert hit["source"] == "decoded-container-text"
    assert hit["match"] == "exact"
    assert hit["container_file_offset"] == f"0x{CONTAINER_FILE_OFFSET:06X}"
    assert hit["decoded_offset_of_phrase"] == f"0x{DECODED_OFFSET_OF_PHRASE:X}"
    assert "NONE" in hit["rom_offset_of_text"]


def test_the_rom_is_unchanged_by_the_scan():
    path = _rom_path()
    before = hashlib.sha256(open(path, "rb").read()).hexdigest()

    scan._decoded_text_rows(open(path, "rb").read())

    assert hashlib.sha256(open(path, "rb").read()).hexdigest() == before
    assert before == CANONICAL_SHA256
