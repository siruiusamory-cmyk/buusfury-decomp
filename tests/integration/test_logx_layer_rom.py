"""Read-only regression evidence for LOGX-LAYER-001.

Only findings independently established in
``docs/research/LOGX_LAYER_PROVENANCE.md`` are encoded here.  Physical facts
(access width, alignment, pointerhood, array shape) are asserted; LOGExtractor's
semantic hypotheses and this ticket's unresolved questions are deliberately not.

The suite skips cleanly when the private canonical ROM is not configured, and
it never writes to it.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools.research.logx_layer_probe import (
    CANONICAL_SHA256,
    ROOT_LAYER_SLOTS,
    analyze_roots,
    in_rom_word,
    read_record,
    scan_handler_words,
)

ROM_BASE = 0x08000000

#: Locally verified constants of the canonical image.
EXPECTED_LAYER_REFERENCES = 1808
EXPECTED_UNIQUE_RECORDS = 1464
EXPECTED_SHARED_RECORDS = 35
EXPECTED_HANDLER_CENSUS = {
    0x08008087: 1420,
    0x0800897B: 41,
    0x08007A41: 1,
    0x08007B63: 1,
    0x080088BD: 1,
}
EXPECTED_REFERENCE_CENSUS = {
    0x08008087: 1516,
    0x0800897B: 41,
    0x08007A41: 249,
    0x08007B63: 1,
    0x080088BD: 1,
}
ABSENT_LAYER_RECORD = 0x080707FC
ABSENT_LAYER_REFERENCES = 249
LAYER_POINTER_MIN = 0x080707FC
LAYER_POINTER_MAX = 0x082B8BC8

#: Representative records measured in the provenance document.
REPRESENTATIVE_RECORDS = {
    # map 0, slot +0x14: a 3x1 dominant-class record
    0x082B84D0: {"handler": 0x08008087, "x": 3, "y": 1},
    # map 39, slot +0x18: a 3x2 dominant-class record
    0x08293BEC: {"handler": 0x08008087, "x": 3, "y": 2},
    # map 39, slot +0x20: a 4x2 dominant-class record
    0x08294628: {"handler": 0x08008087, "x": 4, "y": 2},
    # map 40, slot +0x18: a 2x2 dominant-class record
    0x08292C88: {"handler": 0x08008087, "x": 2, "y": 2},
    # the shared zero-dimension absent-layer record
    0x080707FC: {"handler": 0x08007A41, "x": 0, "y": 0},
    # map 19, slot +0x18: the single 0x08007B63 record
    0x0829F808: {"handler": 0x08007B63, "x": 64, "y": 192},
    # map 19, slot +0x1C: the single 0x080088BD record
    0x082ABF00: {"handler": 0x080088BD, "x": 48, "y": 251},
    # map 8, slot +0x14: a 0x0800897B record whose x byte is zero
    0x082B44C8: {"handler": 0x0800897B, "x": 0, "y": 240},
}

#: Representative root -> four layer slots for maps at the table's beginning,
#: middle and end.  Values measured in the provenance document's census.
REPRESENTATIVE_SLOT_TARGETS = {
    0: (0x082B84D0, 0x082B87C4, 0x082B891C, 0x082B8BC8),
    19: (0x0829F6E4, 0x0829F808, 0x082ABF00, 0x080707FC),
    39: (0x080707FC, 0x08293BEC, 0x082941CC, 0x08294628),
    40: (0x082928C0, 0x08292C88, 0x08293000, 0x082932D0),
}


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return data


@pytest.fixture(scope="module")
def report(canonical_bytes: bytes) -> dict:
    return analyze_roots(canonical_bytes)


def test_all_452_roots_populate_all_four_layer_slots(report: dict) -> None:
    summary = report["summary"]
    assert summary["map_entries"] == 452
    assert summary["valid_roots"] == 452
    assert summary["layer_references"] == EXPECTED_LAYER_REFERENCES
    # The measured fact: no selector-1 root carries a null layer slot.  An
    # unused layer is a zero-dimension record, not a null pointer.
    assert summary["null_layer_slots"] == 0
    assert summary["non_null_references"] == EXPECTED_LAYER_REFERENCES


def test_layer_pointer_census_is_stable(report: dict) -> None:
    summary = report["summary"]
    assert summary["unique_layer_records"] == EXPECTED_UNIQUE_RECORDS
    assert summary["shared_layer_records"] == EXPECTED_SHARED_RECORDS
    assert summary["layer_pointer_min"] == f"{LAYER_POINTER_MIN:#010x}"
    assert summary["layer_pointer_max"] == f"{LAYER_POINTER_MAX:#010x}"
    assert summary["unique_records_unreadable"] == 0


def test_every_layer_slot_target_is_an_aligned_in_rom_word(report: dict) -> None:
    for reference in report["references"]:
        assert reference["slot_state"] == "non_null", reference
        assert in_rom_word(int(reference["layer"]), 0x800000), reference


@pytest.mark.parametrize("slot", ROOT_LAYER_SLOTS)
def test_every_root_slot_is_populated_on_all_452_roots(report: dict, slot: int) -> None:
    usage = report["slot_usage"][f"+0x{slot:02x}"]
    assert usage["references"] == 452
    assert usage["null"] == 0
    assert usage["non_null"] == 452


def test_handler_word_census_matches_the_measured_counts(report: dict) -> None:
    summary = report["summary"]
    assert summary["distinct_handler_words"] == len(EXPECTED_HANDLER_CENSUS)
    census = {
        int(key, 16): value
        for key, value in summary["handler_census_unique_records"].items()
    }
    assert census == EXPECTED_HANDLER_CENSUS
    reference_census = {
        int(key, 16): value
        for key, value in summary["handler_census_references"].items()
    }
    assert reference_census == EXPECTED_REFERENCE_CENSUS


def test_every_handler_word_is_an_odd_thumb_style_code_pointer(report: dict) -> None:
    for record in report["layer_records"].values():
        assert record["handler_is_thumb_bit_set"], record["address"]
        # Physical: the word is odd, i.e. not 4-byte aligned, which is the
        # expected shape of a Thumb entry address.
        assert not record["handler_aligned"], record["address"]


@pytest.mark.parametrize("address,expected", sorted(REPRESENTATIVE_RECORDS.items()))
def test_representative_records_have_the_measured_shape(
    canonical_bytes: bytes, address: int, expected: dict
) -> None:
    record = read_record(canonical_bytes, address)
    assert record["readable"]
    assert record["handler_raw"] == expected["handler"]
    assert record["byte_14_raw"] == expected["x"]
    assert record["byte_15_raw"] == expected["y"]


@pytest.mark.parametrize("map_index,expected", sorted(REPRESENTATIVE_SLOT_TARGETS.items()))
def test_representative_roots_resolve_the_measured_slot_targets(
    report: dict, map_index: int, expected: tuple[int, ...]
) -> None:
    rows = {
        (int(r["index"]), int(r["slot"])): int(r["layer"])
        for r in report["references"]
    }
    actual = tuple(rows[(map_index, slot)] for slot in ROOT_LAYER_SLOTS)
    assert actual == expected, f"map {map_index}"


def test_x_and_y_dimension_bytes_are_separate_one_byte_fields(
    canonical_bytes: bytes,
) -> None:
    """The engine reads them with two distinct ``ldrb`` instructions."""
    # 0x08007BDA adds r0,#0x14        -> r0 = record+0x14
    # 0x08007BDC ldrb r6,[r0]          -> r6 = record+0x14
    # 0x08007BDE ldrb r0,[r0,#1]       -> r0 = record+0x15
    # 0x08007BE0 muls r6,r0,r6
    instruction_bytes = canonical_bytes[0x08007BDA - ROM_BASE : 0x08007BE2 - ROM_BASE]
    assert instruction_bytes == bytes.fromhex("1430067840784643")


def test_the_chunk_pointer_array_is_indexed_at_record_plus_0x18(
    canonical_bytes: bytes,
) -> None:
    """0x08007BEE..0x08007BF2: ``lsls r1,r5,#2`` / ``adds r0,r0,r1`` / ``ldr r0,[r0,#0x18]``."""
    instruction_bytes = canonical_bytes[0x08007BEE - ROM_BASE : 0x08007BF4 - ROM_BASE]
    assert instruction_bytes == bytes.fromhex("a90040188069")


def test_the_record_0x16_field_is_read_signed(canonical_bytes: bytes) -> None:
    """The only signed record load is ``ldrsh r7,[r5,r3]`` with ``r3=0x16``."""
    assert canonical_bytes[0x08007BB4 - ROM_BASE : 0x08007BB8 - ROM_BASE] == bytes.fromhex(
        "1623ef5e"
    )


def test_dominant_class_grid_bytes_are_never_zero_and_products_stay_under_twenty_one(
    report: dict,
) -> None:
    dominant = [
        record
        for record in report["layer_records"].values()
        if int(record["handler_raw"]) == 0x08008087
    ]
    assert len(dominant) == EXPECTED_HANDLER_CENSUS[0x08008087]
    for record in dominant:
        assert 1 <= int(record["byte_14_raw"]) <= 5, record["address"]
        assert 1 <= int(record["byte_15_raw"]) <= 5, record["address"]
        assert int(record["grid_product_raw"]) <= 20, record["address"]


def test_dominant_class_0x18_window_carries_the_product_of_chunk_pointers(
    report: dict,
) -> None:
    """The first ``x*y`` words are all aligned in-ROM words on the clear majority.

    Deliberately not "all": 117 of the 1420 measured records carry an internal
    null before the last expected pointer, and that anomaly is recorded in the
    provenance document rather than hidden by a weaker assertion.
    """
    dominant = [
        record
        for record in report["layer_records"].values()
        if int(record["handler_raw"]) == 0x08008087
    ]
    clean = sum(
        1 for record in dominant if record["window_all_product_words_aligned_in_rom"]
    )
    assert clean == 1303
    with_internal_null = sum(
        1
        for record in dominant
        if not record["window_all_product_words_aligned_in_rom"]
        and any(record["pointer_window"][: int(record["grid_product_raw"])])
    )
    assert with_internal_null == 117
    # The dominant class never has a wholly null window; the only such record in
    # the image is the shared absent-layer placeholder of the other family.
    assert not any(
        not record["pointer_window_non_null"] for record in dominant
    )


def test_the_absent_layer_record_is_the_only_fully_null_window(report: dict) -> None:
    null_windows = [
        int(record["address"])
        for record in report["layer_records"].values()
        if not record["pointer_window_non_null"]
    ]
    assert null_windows == [ABSENT_LAYER_RECORD]
    shared = {
        int(entry["layer"]): int(entry["reference_count"])
        for entry in report["shared_layer_records"]
    }
    assert shared[ABSENT_LAYER_RECORD] == ABSENT_LAYER_REFERENCES
    record = report["layer_records"][f"{ABSENT_LAYER_RECORD:#010x}"]
    assert record["byte_14_raw"] == 0
    assert record["byte_15_raw"] == 0


def test_the_standalone_scan_finds_dominant_records_no_root_references(
    canonical_bytes: bytes, report: dict
) -> None:
    """The record family is larger than the selector-1 root set.

    Measured: 1439 aligned occurrences of ``0x08008087`` in
    ``0x08100000..0x08400000``, of which 1420 are referenced as a record.
    """
    hits = scan_handler_words(canonical_bytes, 0x08008087)
    assert len(hits) == 1439
    referenced = {
        int(reference["layer"])
        for reference in report["references"]
        if reference["slot_state"] == "non_null"
    }
    unreferenced = sorted(set(hits) - referenced)
    assert len(unreferenced) == 19
    # Each unreferenced occurrence still has the dominant record shape.
    for address in unreferenced[:5]:
        record = read_record(canonical_bytes, address)
        assert record["handler_raw"] == 0x08008087
        assert 1 <= int(record["byte_14_raw"]) <= 5


def test_the_0x0800897b_class_does_not_use_the_dominant_grid_dimensions(
    report: dict,
) -> None:
    """This class's ``+0x14``/``+0x15`` pair is not a chunk-grid product.

    Measured: none of the 41 records has all of its first ``x*y`` window words as
    aligned in-ROM pointers, and 30 of them have a zero dimension byte, so the
    dominant class's window reading does not generalise to this class.
    """
    members = [
        record
        for record in report["layer_records"].values()
        if int(record["handler_raw"]) == 0x0800897B
    ]
    assert len(members) == EXPECTED_HANDLER_CENSUS[0x0800897B]
    assert not any(record["window_all_product_words_aligned_in_rom"] for record in members)
    assert sum(1 for record in members if int(record["grid_product_raw"]) == 0) == 29
    # Every one of these records has a null first chunk-pointer word except
    # three; the three are recorded as anomalies in the provenance document.
    assert sum(1 for record in members if record["pointer_window"][0] == 0) == 38


def test_analysis_rejects_a_non_canonical_image() -> None:
    with pytest.raises(ValueError):
        analyze_roots(bytes(0x100))


def test_documented_module_invocation_emits_the_canonical_report(
    canonical_bytes: bytes, tmp_path: Path
) -> None:
    rom = tmp_path / "canonical.gba"
    rom.write_bytes(canonical_bytes)
    before = hashlib.sha256(rom.read_bytes()).hexdigest()
    result = subprocess.run(
        [sys.executable, "-m", "tools.research.logx_layer_probe", str(rom)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert rom.read_bytes() == canonical_bytes
    assert hashlib.sha256(rom.read_bytes()).hexdigest() == before
    payload = json.loads(result.stdout)
    assert payload["sha256"] == CANONICAL_SHA256
    assert payload["summary"]["unique_layer_records"] == EXPECTED_UNIQUE_RECORDS
    assert "references" not in payload
    assert "layer_records" not in payload


def test_the_probe_refuses_a_non_canonical_file(tmp_path: Path) -> None:
    rom = tmp_path / "not-canonical.gba"
    rom.write_bytes(bytes(0x800000))
    result = subprocess.run(
        [sys.executable, "-m", "tools.research.logx_layer_probe", str(rom)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "refusing non-canonical ROM" in (result.stdout + result.stderr)
