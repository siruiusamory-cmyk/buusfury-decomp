"""Read-only regression evidence for LOGX-MAP-RENDER-001.

Only findings independently established in
``docs/research/LOGX_MAP_RENDER_PROVENANCE.md`` are encoded here.  Field widths
are asserted only where an engine instruction performs that access, and
LOGExtractor's semantic hypotheses are deliberately not asserted.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools.research.logx_map_render_probe import analyze, in_rom_word

SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
ROM_BASE = 0x08000000

#: Representative selector-1 roots proven by the accepted predecessor census.
REPRESENTATIVE_ROOTS = {
    0: 0x082B8C38,
    1: 0x082B5FA0,
    39: 0x08294968,
    100: 0x0826AD50,
    225: 0x08216A18,
    338: 0x081DAD0C,
    451: 0x0817B1B0,
}


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SHA256
    return data


@pytest.fixture(scope="module")
def report(canonical_bytes: bytes) -> dict:
    return analyze(canonical_bytes)


def test_all_452_records_resolve_a_valid_aligned_selector_1_root(report: dict) -> None:
    summary = report["summary"]
    assert summary["records"] == 452
    assert summary["valid_sources"] == 452
    assert summary["valid_selector_1_roots"] == 452
    assert summary["null_or_invalid_roots"] == 0
    assert summary["distinct_roots"] == 421


def test_representative_selector_1_roots_match_the_measured_values(report: dict) -> None:
    roots = {
        record["index"]: record["selector_1_root"] for record in report["records"]
    }
    for index, expected in REPRESENTATIVE_ROOTS.items():
        assert roots[index] == expected, f"map {index}"


def test_selector_1_root_equals_the_first_word_of_the_source_array(
    canonical_bytes: bytes, report: dict
) -> None:
    """The accepted formula collapses to ``source + 0x00`` for selector 1."""
    from tools.research.logx_map_render_probe import _u32le

    for record in report["records"]:
        source = record["source_raw"]
        stored = _u32le(canonical_bytes, source - ROM_BASE)
        assert record["selector_1_root"] == stored, record["index"]
        assert record["selector_1_root"] != source, record["index"]
    by_index = {r["index"]: r for r in report["records"]}
    assert by_index[39]["source_raw"] == 0x080753F0
    assert by_index[39]["selector_1_root"] == 0x08294968


def test_pointer_fields_are_uniformly_aligned_and_in_rom(report: dict) -> None:
    census = report["field_census"]
    for offset in ("+0x14", "+0x18", "+0x1c", "+0x20", "+0x48", "+0x4c"):
        field = census[offset]
        assert field["width"] == 4, offset
        assert field["count"] == 452, offset
        assert field["null_count"] == 0, offset
        assert field["aligned_in_rom_count"] == 452, offset
        assert field["in_rom_not_aligned_count"] == 0, offset
        assert field["out_of_rom_count"] == 0, offset


def test_extent_halfwords_are_nonzero_and_have_engine_observed_width(report: dict) -> None:
    """``+0x08``/``+0x0A`` are the halfwords loaded by ``ldrh`` at 0x0800958A/0x08009592."""
    census = report["field_census"]
    for offset, distinct in (("+0x08", 18), ("+0x0a", 19)):
        field = census[offset]
        assert field["width"] == 2, offset
        assert field["null_count"] == 0, offset
        assert field["min_value"] >= 1, offset
        assert field["distinct_values"] == distinct, offset
    by_index = {r["index"]: r for r in report["records"]}
    assert by_index[39]["fields"]["+0x08"] == 0x0179
    assert by_index[39]["fields"]["+0x0a"] == 0x0109
    assert by_index[2]["fields"]["+0x08"] == 0x0001
    assert by_index[2]["fields"]["+0x0a"] == 0x0001


def test_count_and_pointer_pairs_are_null_coupled(report: dict) -> None:
    """Each recovered (count, pointer) pair is null exactly together."""
    pairs = (("+0x0c", "+0x10", 274), ("+0x24", "+0x28", 230), ("+0x40", "+0x44", 104))
    for count_key, pointer_key, nulls in pairs:
        count_null = 0
        pointer_null = 0
        mismatched = 0
        for record in report["records"]:
            fields = record["fields"]
            count_is_null = fields[count_key] == 0
            pointer_is_null = fields[pointer_key] == 0
            count_null += count_is_null
            pointer_null += pointer_is_null
            mismatched += count_is_null != pointer_is_null
        assert count_null == nulls, count_key
        assert pointer_null == nulls, pointer_key
        assert mismatched == 0, (count_key, pointer_key)


def test_shared_roots_are_the_measured_groups(report: dict) -> None:
    groups = {group["root"]: group for group in report["shared_roots"]}
    assert len(groups) == 11
    assert groups[0x0822CC08]["count"] == 10
    assert groups[0x0822CC08]["map_indices"] == [163, 172, 175, 182, 184, 189, 194, 197, 201, 203]
    assert groups[0x0829C2D8]["map_indices"] == [24, 25, 26, 27, 28]


def test_selector_source_arrays_beyond_the_first_word_exist(report: dict) -> None:
    """55 MapEntries expose more than one selector word; selector range is open."""
    histogram = report["summary"]["source_array_run_histogram"]
    assert histogram["1"] == 397
    assert sum(int(count) for length, count in histogram.items() if length != "1") == 55
    assert histogram["12"] == 1


def test_one_root_word_is_shared_by_every_record(report: dict) -> None:
    """``+0x4C`` is the single engine-global atlas array word on all 452 roots."""
    field = report["field_census"]["+0x4c"]
    assert field["distinct_values"] == 1
    assert field["min_value"] == field["max_value"] == 0x08179764


def test_root_offset_4c_target_lies_inside_the_rom() -> None:
    """The single shared atlas array word at root ``+0x4C`` is an in-ROM address."""
    assert in_rom_word(0x08179764, 0x800000)
    assert REPRESENTATIVE_ROOTS[39] == 0x08294968


def test_documented_module_invocation_emits_the_canonical_report(canonical_bytes: bytes) -> None:
    rom = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    assert rom.read_bytes() == canonical_bytes
    result = subprocess.run(
        [sys.executable, "-m", "tools.research.logx_map_render_probe", str(rom)],
        check=True,
        capture_output=True,
        cwd=Path(__file__).parents[2],
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["sha256"] == SHA256
    assert payload["summary"]["valid_selector_1_roots"] == 452
    assert payload["selector_formula"] == "MapEntry[+0x2C] + 4 * (selector - 1)"


def test_probe_analysis_rejects_a_non_canonical_size() -> None:
    with pytest.raises(ValueError):
        analyze(b"\x00" * 16)
