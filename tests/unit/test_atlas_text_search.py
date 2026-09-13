"""WORKBENCH-001 T0.4: unit proofs for the extracted text-search API.

`text_match` is pure string logic. `search_text` is exercised against a small
SYNTHETIC `Atlas` (one text-run observation) and a hand-built decoded-row list -
no commercial ROM bytes and no fixture file. `search_text` reads no ROM unless
handed `rom_image`, so the decoded hit's identity is asserted in its
no-ROM-supplied form, which is what these synthetic inputs can justify.
"""

from __future__ import annotations

from tools.webfoot.atlas import (Atlas, Confidence, CoverageMap, CoverageSpan,
                                  Observation, UNKNOWN, search_text, text_match)
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import Provenance, RomRange


PROFILE_ID = "synthetic"
BASE_SHA256 = "0" * 64
IMAGE_SIZE = 0x1000
PROV = Provenance(PROFILE_ID, BASE_SHA256, "synthetic test evidence")


def make_atlas(observations):
    coverage = CoverageMap.single(IMAGE_SIZE, UNKNOWN, Confidence.UNKNOWN, PROV)
    return Atlas(PROFILE_ID, BASE_SHA256, IMAGE_SIZE, coverage,
                 observations=tuple(observations))


def text_run(start, size, detail):
    return Observation(RomRange(FileOffset(start), size), "text-run-utf16",
                       detail, Confidence.CANDIDATE, PROV)


def decoded_row(text, *, container_index=1, decoded_offset=0):
    return {"text": text, "decoded_offset": decoded_offset,
            "container_index": container_index,
            "container_file_offset": 0x77C000, "container_rom_address": "0x0877C000",
            "decompressor": "stack_be16_buu_v1", "encoding": "UTF-16LE",
            "char_count": len(text)}


# --- text_match -------------------------------------------------------------


def test_text_match_exact():
    assert text_match("Goku", "Good luck, Goku!") == "exact"


def test_text_match_normalized_case_and_whitespace():
    # Present only after case folding + whitespace collapse -> a normalized hit.
    assert text_match("good  LUCK", "Good luck, Goku!") == "normalized"


def test_text_match_no_match():
    assert text_match("Vegeta", "Good luck, Goku!") is None


# --- search_text ------------------------------------------------------------


def test_search_text_finds_planted_decoded_phrase():
    # Critical-path test 2: search_text finds the phrase in the decoded index.
    atlas = make_atlas([])
    rows = [decoded_row("Good luck, Goku!"), decoded_row("unrelated message")]
    result = search_text(atlas, "Good luck, Goku!", rows)

    # Documented result shape.
    assert set(result) == {"searched", "matched", "raw_matched",
                           "decoded_matched", "runs", "decoded"}
    assert result["matched"] == 1
    assert result["raw_matched"] == 0
    assert result["decoded_matched"] == 1
    assert len(result["decoded"]) == 1

    hit = result["decoded"][0]
    assert hit["source"] == "decoded-container-text"
    assert hit["match"] == "exact"
    assert hit["text"] == "Good luck, Goku!"
    # No ROM supplied -> the handle is reported null, not guessed.
    assert hit["identity"]["packed_handle"] is None
    assert "no ROM supplied" in hit["identity"]["unrecovered_because"]


def test_search_text_finds_raw_run():
    atlas = make_atlas([text_run(0x200, 0x20, "Good luck, Goku!")])
    result = search_text(atlas, "Goku", [])
    assert result["raw_matched"] == 1
    assert result["decoded_matched"] == 0
    assert result["matched"] == 1
    run = result["runs"][0]
    assert run["source"] == "raw-rom-run"
    assert run["match"] == "exact"
    assert run["file_offset"] == "0x000200"


def test_search_text_no_match_empty_structure():
    atlas = make_atlas([text_run(0x200, 0x20, "Good luck, Goku!")])
    result = search_text(atlas, "Vegeta", [decoded_row("Good luck, Goku!")])
    assert result["matched"] == 0
    assert result["raw_matched"] == 0
    assert result["decoded_matched"] == 0
    assert result["runs"] == []
    assert result["decoded"] == []
