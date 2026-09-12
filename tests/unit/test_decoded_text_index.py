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


#: The three Latin-1 halfwords that are text, not control units. They are the
#: only units in the seven compressed-text containers whose low byte exceeds
#: PRINT_MAX, and each occurs mid-word, so classifying them as control units
#: split valid words in half. Every fixture phrase below is invented.
LATIN1_ACUTE = "The décor is plain."
LATIN1_DIAERESIS = "A naïve guess only."
LATIN1_NBSP = "Ten thousand units."


def _one_run(text: str):
    runs = list(scan.scan_runs(_utf16_run(text), require_terminator=False))
    assert len(runs) == 1, f"expected one unbroken run, got {[r[3] for r in runs]}"
    return runs[0]


def test_an_acute_e_stays_inside_one_run():
    assert _one_run(LATIN1_ACUTE)[3] == LATIN1_ACUTE
    assert "é" in _one_run(LATIN1_ACUTE)[3]


def test_a_diaeresis_i_stays_inside_one_run():
    assert _one_run(LATIN1_DIAERESIS)[3] == LATIN1_DIAERESIS
    assert "ï" in _one_run(LATIN1_DIAERESIS)[3]


def test_a_non_breaking_space_stays_inside_one_run():
    assert _one_run(LATIN1_NBSP)[3] == LATIN1_NBSP
    assert " " in _one_run(LATIN1_NBSP)[3]


@pytest.mark.parametrize("control", [0x0002, 0x0007, 0x0008, 0x000A, 0x000B])
def test_every_true_control_unit_still_ends_a_run(control):
    """The allowlist is three values wide; the real control units are untouched."""
    blob = (_utf16_run("First fragment") + struct.pack("<H", control)
            + _utf16_run("Second fragment"))

    runs = list(scan.scan_runs(blob, require_terminator=False))

    assert [run[3] for run in runs] == ["First fragment", "Second fragment"]


def test_the_allowlist_is_exactly_the_three_measured_units():
    """A blanket 'zero high byte is printable' rule would sweep in the controls."""
    assert scan.TEXT_LATIN1 == frozenset({0x00A0, 0x00E9, 0x00EF})


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


def _search(tmp_path, phrase, decoded_rows, capsys, raw_rows=(), rom=None):
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

    argv = ["atlas", "--atlas", str(directory / "atlas.jsonl"), "text", phrase]
    if rom is not None:
        argv += ["--rom", str(rom)]
    assert main(argv) == 0
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


# --- TEXT-HANDLE-001: the durable packed-handle identity -----------------------
#
# A decoded string has no ROM address of its own, so its identity is the packed
# u32 an event-resource record stores to address it. Identity is per-TEXT; the
# ROM addresses holding that word are per-SITE. Collapsing the two in either
# direction is the failure these tests pin. Every fixture below is synthetic:
# the handles are built by the same bit layout the recovery reads, and the
# phrases are invented.

from tools.webfoot import cli
from tools.webfoot.binary import GBA_ROM_BASE
from tools.webfoot.data.placement_contracts import CONTRACTS

_RESOURCE = CONTRACTS["buus_fury_usa_rev0_01c1707f"]["event_resource"]
_POOL = _RESOURCE["pool_start"] - GBA_ROM_BASE
_TABLE = _RESOURCE["table"] - GBA_ROM_BASE

#: Invented for this test, and deliberately 8 characters so its packed length
#: (16 bytes) is easy to read in the assertions below.
HANDLE_PHRASE = "Zephyrs!"


def _packed_handle(selector: int, start: int, size: int) -> int:
    """Build a handle the way the ROM stores one, from the documented layout."""
    return (selector | ((start // 2) << cli.HANDLE_START_SHIFT)
            | ((size // 2) << cli.HANDLE_LENGTH_SHIFT))


def _image_with_handles(*sites: tuple[int, int]) -> bytes:
    """A synthetic image carrying handle words at chosen pool offsets."""
    image = bytearray(scan.IMAGE_SIZE)
    for pool_offset, value in sites:
        struct.pack_into("<I", image, _POOL + pool_offset, value)
    return bytes(image)


def test_the_handle_layout_round_trips_through_its_own_unpacker():
    """The three fields survive packing, so the fixtures below are meaningful."""
    handle = _packed_handle(1, 0x132, 0x20)

    assert cli._unpack_handle(handle) == (1, 0x132, 0x20)


def test_a_decoded_match_reports_the_packed_handle_naming_it():
    image = _image_with_handles((0x40, _packed_handle(3, 0x80, 0x10)))

    identity = cli._recover_handle(image, 3, 0x80, 0x10)

    assert identity["packed_handle"] == f"0x{_packed_handle(3, 0x80, 0x10):08X}"
    assert identity["handle_selector"] == 3
    assert identity["handle_decoded_start"] == "0x80"
    assert identity["handle_decoded_length"] == "0x10"


def test_the_identity_is_one_value_while_its_references_are_a_list():
    """The anti-collapse property, stated directly as a shape assertion."""
    handle = _packed_handle(2, 0x200, 0x40)
    image = _image_with_handles((0x10, handle), (0x80, handle), (0x300, handle))

    identity = cli._recover_handle(image, 2, 0x200, 0x40)

    # ONE identity...
    assert isinstance(identity["packed_handle"], str)
    # ...and a LIST of the places that reference it.
    assert isinstance(identity["reference_sites"], list)
    assert identity["reference_sites"] == [
        f"0x{GBA_ROM_BASE + _POOL + offset:08X}" for offset in (0x10, 0x80, 0x300)
    ]
    assert identity["reference_site_count"] == 3


def test_three_references_do_not_become_three_identities():
    """Three sites naming one string stay one message, not three."""
    handle = _packed_handle(1, 0x60, 0x20)
    image = _image_with_handles((0x20, handle), (0x24, handle), (0x400, handle))

    identity = cli._recover_handle(image, 1, 0x60, 0x20)

    assert len({identity["packed_handle"]}) == 1
    assert identity["reference_site_count"] == 3
    # The identity is a single object, not a sequence of them.
    assert isinstance(identity, dict)


def test_a_phrase_resolves_to_at_most_one_identity():
    """The mirror-image collapse: many handles covering one phrase, one answer.

    A real indexed run merges several handle-defined records, and long records
    overlap short ones, so many records contain any given phrase. Recovery
    still names exactly one.
    """
    wanted = _packed_handle(1, 0x100, 0x20)
    image = _image_with_handles(
        (0x00, wanted),
        # Wider records that also contain the phrase, and so would collapse the
        # answer into several identities if containment alone decided it.
        (0x10, _packed_handle(1, 0x0E0, 0x60)),
        (0x20, _packed_handle(1, 0x0C0, 0x400)),
        (0x30, _packed_handle(1, 0x100, 0x80)),
    )

    identity = cli._recover_handle(image, 1, 0x100, 0x20)

    assert identity["packed_handle"] == f"0x{wanted:08X}"
    assert identity["reference_sites"] == [f"0x{GBA_ROM_BASE + _POOL:08X}"]


def test_the_narrowest_containing_record_wins():
    """A phrase is a substring, so the tightest record covering it is its own.

    The searcher types part of a message; the record that IS that message is
    the smallest one spanning every character typed.
    """
    tight = _packed_handle(2, 0x40, 0x20)
    image = _image_with_handles(
        (0x00, _packed_handle(2, 0x00, 0x200)),
        (0x10, tight),
        (0x20, _packed_handle(2, 0x30, 0x80)),
    )

    # The phrase sits inside all three, and starts past the tight record's own
    # start, so an equality rule would find nothing at all here.
    identity = cli._recover_handle(image, 2, 0x48, 0x10)

    assert identity["packed_handle"] == f"0x{tight:08X}"
    assert identity["handle_decoded_length"] == "0x20"


def test_a_hit_with_no_recoverable_handle_degrades_honestly():
    """No record covers this span, so the identity is null and says why."""
    image = _image_with_handles((0x40, _packed_handle(1, 0x100, 0x20)))

    identity = cli._recover_handle(image, 1, 0x900, 0x20)

    assert identity["packed_handle"] is None
    assert "no event-resource record" in identity["unrecovered_because"]


def test_a_phrase_running_past_a_records_end_is_not_covered_by_it():
    """Containment is both-ended: overlapping the start is not enough."""
    image = _image_with_handles((0x00, _packed_handle(1, 0x100, 0x20)))

    identity = cli._recover_handle(image, 1, 0x110, 0x40)

    assert identity["packed_handle"] is None


def test_a_handle_in_another_container_is_never_the_answer():
    """The selector is part of the identity: same span, different container."""
    image = _image_with_handles((0x00, _packed_handle(4, 0x100, 0x20)))

    assert cli._recover_handle(image, 1, 0x100, 0x20)["packed_handle"] is None
    assert cli._recover_handle(image, 4, 0x100, 0x20)["packed_handle"] is not None


def test_a_handle_outside_the_pool_is_not_a_reference_site():
    """The pool bounds the search: an identical word elsewhere is not a site."""
    handle = _packed_handle(1, 0x100, 0x20)
    image = bytearray(scan.IMAGE_SIZE)
    struct.pack_into("<I", image, _TABLE + 0x40, handle)

    identity = cli._recover_handle(bytes(image), 1, 0x100, 0x20)

    assert identity["packed_handle"] is None


def test_a_search_without_a_rom_reports_the_identity_as_unrecovered(
        tmp_path, capsys):
    """The default path opens no image, so it must not invent a handle."""
    rows = [_decoded_row(f"Prelude.{HANDLE_PHRASE}")]

    result = _search(tmp_path, HANDLE_PHRASE, rows, capsys)
    identity = result["decoded"][0]["identity"]

    assert identity["packed_handle"] is None
    assert "no ROM supplied" in identity["unrecovered_because"]


#: A decoded row and a synthetic image that agree: the row's phrase begins at
#: decoded offset 0x20 in container 0, and the image carries a handle whose
#: record covers exactly that span. An exact search therefore recovers the
#: handle, which is what makes the normalized refusal below meaningful.
_SPAN_ROW_TEXT = f"Prelude.{HANDLE_PHRASE}"
_SPAN_HANDLE = _packed_handle(0, 0x20, len(_SPAN_ROW_TEXT) * 2)


def _rom_for_span(tmp_path):
    path = tmp_path / "synthetic.gba"
    path.write_bytes(_image_with_handles((0x100, _SPAN_HANDLE)))
    return path


def test_an_exact_match_recovers_its_handle_through_the_cli(tmp_path, capsys):
    """The positive half: with a ROM and an exact span, the identity resolves."""
    rows = [_decoded_row(_SPAN_ROW_TEXT, index=0, decoded_offset=0x20)]

    result = _search(tmp_path, HANDLE_PHRASE, rows, capsys,
                     rom=_rom_for_span(tmp_path))
    identity = result["decoded"][0]["identity"]

    assert identity["packed_handle"] == f"0x{_SPAN_HANDLE:08X}"
    assert identity["reference_sites"] == [f"0x{GBA_ROM_BASE + _POOL + 0x100:08X}"]


def test_a_normalized_match_recovers_no_handle_rather_than_guessing(
        tmp_path, capsys):
    """Without an exact span there is no way to pick one handle honestly.

    The ROM here is the same image whose handle the exact search above does
    recover, so the null below is a deliberate refusal to guess, not a handle
    that happens to be absent.
    """
    rows = [_decoded_row(_SPAN_ROW_TEXT, index=0, decoded_offset=0x20)]

    result = _search(tmp_path, HANDLE_PHRASE.upper() + "  ", rows, capsys,
                     rom=_rom_for_span(tmp_path))
    hit = result["decoded"][0]

    assert hit["match"] == "normalized"
    assert hit["identity"]["packed_handle"] is None
    assert "exact decoded span" in hit["identity"]["unrecovered_because"]


def test_the_no_rom_address_property_still_holds_alongside_the_identity(
        tmp_path, capsys):
    """The handle names the text; it is not an address FOR the text."""
    rows = [_decoded_row(f"Prelude.{HANDLE_PHRASE}")]

    result = _search(tmp_path, HANDLE_PHRASE, rows, capsys)
    hit = result["decoded"][0]

    assert "NONE" in hit["rom_offset_of_text"]
    assert "file_offset" not in hit
    assert hit["container_rom_address"].startswith("0x")
