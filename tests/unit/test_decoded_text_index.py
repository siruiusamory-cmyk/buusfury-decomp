"""TEXT-INDEX-001 proofs for the decoded-container text index and full-text search.

Synthetic bytes only; no commercial image and no extracted corpus. Every fixture
string here is invented for the test.

Two defects are pinned:

1. `scan_text.jsonl` truncated each run's searchable form at 40 characters, so a
   string longer than that could not be found by its own text.
2. Text living inside a compressed container was decoded during the scan and then
   discarded, so it was invisible to every search surface.

The index's central correctness property is also pinned here: a decoded record
carries its CONTAINER's ROM offset and an offset within the decoded stream, and
never a ROM offset for the text itself, because decompressed bytes have no
address in the image.
"""

from __future__ import annotations

import json
import struct

import pytest

from tools.webfoot.atlas_producers import scan
from tools.webfoot.formats import webfoot_lz as lz


#: Longer than the historical 40-character cut, so a prefix search cannot reach
#: its tail. Invented for this test.
LONG_RUN = "A synthetic sentence written only for this test, well past forty."

#: Two adjacent logical strings with no delimiter between them, which is the
#: shape the real decoded streams have.
DECODED_TEXT = "Alpha phrase here.Beta phrase follows immediately."


def _utf16_run(text: str) -> bytes:
    return text.encode("utf-16le")


def _rows_for(blob: bytes, base: int = 0x00100000) -> list[dict]:
    """Shape `scan_runs` output the way `_text_rows` does, minus its ROM checks.

    `_text_rows` asserts against three known real-ROM offsets, so it refuses
    synthetic bytes by design. This mirrors only its row construction.
    """
    return [{
        "file_offset": base + offset, "gba_address": f"0x{scan.BASE + base + offset:08X}",
        "size": size, "encoding": encoding, "char_count": len(text),
        "prose_score": "prose", "cluster_id": 1, "prefix": text[:40], "text": text,
        "in_claimed_region": False, "notes": "",
    } for offset, size, encoding, text in scan.scan_runs(blob)]


def _rom_with_container(text: str) -> bytes:
    """A synthetic image whose seeded pointer table reaches one real container.

    The container is produced by the project's own packer, so the producer's
    decode-and-round-trip gate is exercised rather than bypassed.
    """
    image = bytearray(scan.IMAGE_SIZE)
    container_offset = 0x00700000
    # A leading control unit, so the run's `decoded_offset` is non-zero and the
    # "never sum container + decoded offset" check below is actually load-bearing.
    packed = lz.pack(b"\x0b\x00" + _utf16_run(text))
    image[container_offset:container_offset + len(packed)] = packed

    # The first table slot points at the container; the rest stay null so the
    # producer sees exactly one reachable container.
    struct.pack_into("<I", image, scan.COMPRESSED_TEXT_TABLE,
                     scan.BASE + container_offset)
    return bytes(image), container_offset


# --- defect 2: the 40-character truncation -----------------------------------


def test_a_raw_run_longer_than_forty_characters_keeps_its_full_text():
    """The regression test for the truncation: `text` is the whole run.

    `_text_rows` asserts a real-ROM self-check and so cannot run on synthetic
    bytes; the row shaping it performs is reproduced here against the same
    shared extractor it uses, which is where the truncation lived.
    """
    assert len(LONG_RUN) > 40, "the fixture must exceed the historical cut"
    blob = _utf16_run(LONG_RUN) + b"\x00\x00"

    runs = list(scan.scan_runs(blob))

    assert [run[3] for run in runs] == [LONG_RUN]
    assert len(runs[0][3]) == len(LONG_RUN)


def test_the_emitted_row_carries_full_text_and_the_prefix_consumers_read():
    """Both fields: `text` is the whole run, `prefix` stays the 40-char preview."""
    rows = _rows_for(_utf16_run(LONG_RUN) + b"\x00\x00")

    assert rows[0]["text"] == LONG_RUN
    assert rows[0]["prefix"] == LONG_RUN[:40]
    assert rows[0]["char_count"] == len(LONG_RUN)


def test_the_atlas_observation_detail_is_no_longer_truncated():
    """`atlas text` matches `detail`, so the assembler must copy the full text."""
    from tools.webfoot import atlas_build as ab

    rows = _rows_for(_utf16_run(LONG_RUN) + b"\x00\x00")
    observations = ab._observations({
        "scan_text": rows, "scan_entropy": [], "scan_compression": [],
        "scan_code_shape": [], "graphics_extents": [], "seed_knowledge": [],
        "code_functions": [], "code_regions": [], "scan_pointers": [],
        "scan_pointer_tables": [],
    })

    details = [o.detail for o in observations if o.kind.startswith("text-run-")]
    assert LONG_RUN in details


# --- defect 1: decoded container text -----------------------------------------


def test_decoded_container_text_is_indexed():
    image, container_offset = _rom_with_container(DECODED_TEXT)

    rows = scan._decoded_text_rows(image)

    assert rows, "the reachable container produced no decoded-text rows"
    assert any(DECODED_TEXT in row["text"] for row in rows)
    assert all(row["container_file_offset"] == container_offset for row in rows)


def test_a_decoded_record_carries_container_and_decoded_offsets_but_no_rom_offset():
    """The evidence rule: only the CONTAINER has a ROM address.

    A decoded run must never be given a direct ROM offset, and the container
    offset plus the decoded offset must never be summed into one, because the
    result would name a ROM address that holds compressed bytes, not this text.
    """
    image, container_offset = _rom_with_container(DECODED_TEXT)

    row = next(r for r in scan._decoded_text_rows(image) if r["text"])

    assert row["container_file_offset"] == container_offset
    assert row["container_rom_address"] == f"0x{scan.BASE + container_offset:08X}"
    assert isinstance(row["decoded_offset"], int)
    assert row["decompressor"] == "webfoot_lz"
    assert row["encoding"] == "utf16le"
    assert row["source_kind"] == "decoded-container-text"

    # No key names a ROM location for the text itself, under any spelling.
    assert "file_offset" not in row
    assert "gba_address" not in row

    # The sum is the tempting wrong answer: it looks like a ROM address for the
    # text and is not one, because those ROM bytes are compressed. It must
    # appear nowhere in the record, in either integer or hex-string form.
    assert row["decoded_offset"] > 0, "fixture must not make this check vacuous"
    forbidden = container_offset + row["decoded_offset"]
    assert forbidden not in row.values()
    assert f"0x{scan.BASE + forbidden:08X}" not in row.values()


def test_the_producer_survives_malformed_container_pointers():
    """A wild pointer is recorded, not raised: one bad slot cannot kill a scan."""
    image = bytearray(scan.IMAGE_SIZE)
    # In range and so attempted, but the bytes there are not a container.
    struct.pack_into("<I", image, scan.COMPRESSED_TEXT_TABLE, scan.BASE + 0x00600000)
    # Out of range entirely, and so skipped before any decode.
    struct.pack_into("<I", image, scan.COMPRESSED_TEXT_TABLE + 4, 0x03000000)

    rows = scan._decoded_text_rows(bytes(image))

    assert all(not row["text"] for row in rows)


def test_generation_is_deterministic_for_the_same_input():
    image, _ = _rom_with_container(DECODED_TEXT)

    first = scan._decoded_text_rows(image)
    second = scan._decoded_text_rows(image)

    assert first == second
    assert (json.dumps(first, sort_keys=True)
            == json.dumps(second, sort_keys=True))


# --- the shared run-extraction implementation ---------------------------------


def test_both_surfaces_use_one_run_extraction_implementation():
    """`scan_runs` is the single implementation; neither pass re-implements it."""
    source = scan.__file__
    text = open(source, encoding="utf-8").read()

    assert text.count("def scan_runs(") == 1
    # The control grammar is decoded in exactly one place.
    assert text.count("CONTROL_PREFIX and cursor") == 1


def test_a_terminator_free_stream_needs_no_nul_to_yield_runs():
    """Decoded streams carry no NUL halfwords, so requiring one finds nothing."""
    blob = _utf16_run(DECODED_TEXT)

    assert list(scan.scan_runs(blob, require_terminator=True)) == []

    runs = list(scan.scan_runs(blob, require_terminator=False))
    assert [run[3] for run in runs] == [DECODED_TEXT]


def test_a_terminator_free_scan_breaks_on_every_control_unit():
    """Each non-printable unit ends a run, so lines index separately."""
    blob = _utf16_run("First line") + b"\x0a\x00" + _utf16_run("Second line")

    runs = list(scan.scan_runs(blob, require_terminator=False))

    assert [run[3] for run in runs] == ["First line", "Second line"]


# --- search behaviour through the CLI -----------------------------------------


def _search(tmp_path, phrase, decoded_rows, capsys, raw_rows=()):
    """Run `atlas text` against a synthetic atlas directory and parse its JSON.

    The atlas itself is assembled from the same minimal synthetic artifact set
    the assembler's own tests use, so this drives the real command rather than a
    stand-in.
    """
    from tools.webfoot import atlas_build as ab
    from tools.webfoot.cli import main
    from test_atlas_build import _artifacts

    directory = _artifacts(tmp_path, scan_text=list(raw_rows))
    ab.write_atlas(ab.build_atlas(directory), directory / "atlas.jsonl")
    (directory / "scan_decoded_text.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in decoded_rows), encoding="utf-8")

    assert main(["atlas", "--atlas", str(directory / "atlas.jsonl"),
                 "text", phrase]) == 0
    return json.loads(capsys.readouterr().out)


def _decoded_row(text, *, container=0x00700000, decoded_offset=0x20, index=0):
    return {"source_kind": "decoded-container-text", "container_index": index,
            "container_file_offset": container,
            "container_rom_address": f"0x{scan.BASE + container:08X}",
            "decompressor": "webfoot_lz", "container_kind": 1,
            "decoded_size": 4096, "decoded_offset": decoded_offset,
            "size": len(text) * 2, "encoding": "utf16le",
            "char_count": len(text), "text": text, "prose_score": "prose",
            "notes": ""}


def test_every_decoded_match_is_reported(tmp_path, capsys):
    rows = [_decoded_row("Shared phrase, first copy.", decoded_offset=0x20),
            _decoded_row("Shared phrase, second copy.", decoded_offset=0x80),
            _decoded_row("Nothing relevant here.", decoded_offset=0x200)]

    result = _search(tmp_path, "Shared phrase", rows, capsys)

    assert result["decoded_matched"] == 2
    assert len(result["decoded"]) == 2


def test_an_exact_match_is_distinguishable_from_a_normalized_one(tmp_path, capsys):
    rows = [_decoded_row("Exactly This Phrase here.")]

    exact = _search(tmp_path, "Exactly This Phrase", rows, capsys)
    normalized = _search(tmp_path, "exactly   this phrase", rows, capsys)

    assert exact["decoded"][0]["match"] == "exact"
    assert normalized["decoded"][0]["match"] == "normalized"


def test_a_decoded_result_shows_no_rom_address_for_its_text(tmp_path, capsys):
    rows = [_decoded_row("Findable decoded sentence.")]

    result = _search(tmp_path, "Findable decoded sentence", rows, capsys)
    hit = result["decoded"][0]

    assert hit["source"] == "decoded-container-text"
    assert hit["container_file_offset"] == "0x700000"
    assert hit["decoded_offset"] == "0x20"
    assert hit["encoding"] == "utf16le"
    assert "NONE" in hit["rom_offset_of_text"]
    assert "file_offset" not in hit


def test_the_searched_disclaimer_no_longer_claims_a_forty_character_limit(
        tmp_path, capsys):
    result = _search(tmp_path, "anything", [], capsys)

    assert "40 characters" not in result["searched"]
    assert "truncat" in result["searched"].lower()


def test_both_surfaces_are_searched_and_reported_separately(tmp_path, capsys):
    """One phrase, two byte sources; a raw hit keeps its real ROM file offset."""
    raw = _rows_for(_utf16_run("Shared phrase in the raw image.") + b"\x00\x00",
                    base=0x00100000)
    decoded = [_decoded_row("Shared phrase inside a container.")]

    result = _search(tmp_path, "Shared phrase", decoded, capsys, raw_rows=raw)

    assert result["raw_matched"] == 1
    assert result["decoded_matched"] == 1
    assert result["matched"] == 2
    assert result["runs"][0]["source"] == "raw-rom-run"
    assert result["runs"][0]["file_offset"] == "0x100000"
    assert result["decoded"][0]["source"] == "decoded-container-text"
