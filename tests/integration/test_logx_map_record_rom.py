"""Read-only regression evidence for LOGX-MAP-RECORD-001."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools.research.logx_map_record_probe import analyze


SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = Path(os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SHA256
    return data


def test_candidate_map_table_has_the_measured_physical_shape(canonical_bytes: bytes) -> None:
    report = analyze(canonical_bytes)
    assert (report["table_offset"], report["record_size"], report["record_count"], report["table_end"]) == (
        0x08E2E0, 0x38, 0x1C4, 0x0945C0
    )
    assert report["preceding_32_bytes"] == "997400080d770008160022004100490000000000ace2080800000000c0e20808"
    assert report["following_32_bytes"] == "0100000000400000fa4f912081c596a691ca01263561563405d82436f82cb6d7"


def test_candidate_fields_have_table_wide_structural_support(canonical_bytes: bytes) -> None:
    report = analyze(canonical_bytes)
    assert report["key_be"] == {
        "unique": 452, "zero": 0, "minimum": 1, "maximum": 0x1601, "duplicates": {}
    }
    assert report["text"] == {
        "all_words_upper16_zero": True, "all_indices_in_range": True,
        "unique_indices": 70, "zero_indices": 23, "empty_decodings": 23,
    }
    assert report["pointer_chain"] == {
        "first_valid": 452, "first_unique": 452, "second_valid": 452, "second_unique": 421,
    }


def test_representatives_preserve_the_observed_bytes_and_text_resolution(canonical_bytes: bytes) -> None:
    rows = {record["index"]: record for record in analyze(canonical_bytes)["representatives"]}
    assert rows[0]["bytes"] == "000102000000000001a commit since folded into its successor00000000000000ff00000000000000cc2807080000000000000000"
    assert rows[39]["key_be"] == 0x010B
    assert rows[39]["text_index_low16"] == 0x0228
    assert rows[39]["text"] == "Grand Kai's Planet"
    assert rows[39]["pointer_2c_raw"] == 0x080753F0
    assert rows[39]["second_word_raw"] == 0x08294968
    assert rows[451]["text"] == "Heaven"


def test_documented_module_invocation_emits_the_canonical_report(canonical_bytes: bytes) -> None:
    rom = Path(os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))
    assert rom.read_bytes() == canonical_bytes
    result = subprocess.run(
        [sys.executable, "-m", "tools.research.logx_map_record_probe", str(rom)],
        check=True,
        capture_output=True,
        cwd=Path(__file__).parents[2],
        text=True,
    )
    assert json.loads(result.stdout)["sha256"] == SHA256
