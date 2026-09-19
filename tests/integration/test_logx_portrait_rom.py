"""Read-only ROM-gated evidence for the GRAPHICS-COVERAGE-001 portrait population.

Asserts the measured portrait container population and its disjointness from the
accepted sprite / tileset / map graphs. Every expected value is a count, an
address or a size - no decoded payload is committed. The suite skips cleanly when
the private canonical image is not configured.

Run with ``LOGX_CANONICAL_ROM`` pointing at the image, or place it at the default
``roms/Dragon Ball Z - Buu's Fury (U).gba``.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.research import logx_gfxscan_probe as scan
from tools.research import logx_portrait_probe as pp


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == pp.CANONICAL_SHA256
    return data


def test_portrait_array_base_is_engine_derived(canonical_bytes: bytes) -> None:
    # The base is read from the accessor's own pool word (LOGX-CHAR-001 s11.2).
    assert pp.portrait_array_base(canonical_bytes) == 0x086F393C


def test_portrait_population(canonical_bytes: bytes) -> None:
    report = pp.enumerate_portraits(canonical_bytes)
    assert report["portrait_count"] == 155
    assert report["pointers_strictly_ascending"] is True
    assert report["container_kinds"] == {1: 155}
    assert report["declared_sizes"] == [4096]
    assert report["decoded_sizes"] == [4096]
    assert report["decode_failures"] == 0
    assert report["packed_extent_overlaps"] == 0
    assert report["first_pointer"] == "0x086B880C"
    assert report["last_pointer"] == "0x086F3360"


def test_portraits_disjoint_from_accepted_graphics_corpus(
    canonical_bytes: bytes,
) -> None:
    """No portrait container is reached by the accepted sprite/tileset/map graphs."""
    corpus = scan.build_known_corpus(canonical_bytes)
    known = set(corpus.resources.keys())
    portraits = set(pp.portrait_pointers(canonical_bytes))
    assert portraits & known == set()


# --- PORTRAIT-COMPLETENESS-001 -------------------------------------------------


def test_portrait_field_belongs_to_the_appearance_definition_table(
    canonical_bytes: bytes,
) -> None:
    """The ``+0x08`` the accessor is fed is the 232-record table's, not the run's.

    Asserted from the image's own halfwords, so the binding is re-derived on every
    run rather than inherited from a document.
    """
    evidence = pp.portrait_field_evidence(canonical_bytes)
    assert evidence["table_address"] == "0x0874D380"
    assert evidence["record_count"] == 232
    assert evidence["portrait_offset"] == "0x08"
    assert all(item["matches"] for item in evidence["halfwords"].values())
    # The pool addresses are derived from the instructions, then checked against
    # the expected ones, so neither can drift without failing here.
    assert evidence["consumer_table_pool_word"]["derived_pool_address"] == "0x08025310"
    assert evidence["consumer_table_pool_word"]["expected_pool_address"] == "0x08025310"
    assert evidence["consumer_table_pool_word"]["value"] == "0x0874D380"
    assert evidence["consumer_table_pool_word"]["is_appearance_table"] is True
    assert evidence["consumer_portrait_call_target"] == "0x08011F20"
    assert evidence["portrait_array_pool_word"]["derived_pool_address"] == "0x08012194"
    assert evidence["portrait_array_pool_word"]["expected_pool_address"] == "0x08012194"
    assert evidence["portrait_array_pool_word"]["value"] == "0x086F393C"
    assert evidence["portrait_array_pool_word"]["is_portrait_array_base"] is True


def test_completeness_join_of_the_appearance_definition_portrait_field(
    canonical_bytes: bytes,
) -> None:
    """Every appearance-definition portrait reference resolves inside the run."""
    report = pp.portrait_reference_report(canonical_bytes)
    assert report["appearance_record_count"] == 232
    assert report["run_entry_count"] == 155

    join = report["join"]
    assert join["records"] == 232
    assert join["with_reference"] == 134
    assert join["without_reference"] == 98
    assert join["references"] == 134
    assert join["unique_references"] == 110
    assert join["min_in_run_reference"] == 8
    assert join["max_in_run_reference"] == 162
    assert join["min_non_zero_reference"] == 8
    assert join["max_non_zero_reference"] == 162
    assert join["references_inside_run"] == 134
    assert join["references_outside_run"] == 0
    assert join["outside_values"] == []
    assert join["reserved_references"] == 0
    assert join["reserved_values"] == []
    assert join["run_entries"] == 155
    assert join["run_entries_referenced"] == 110
    assert join["run_entries_unused"] == 45
    assert join["references_outside_run_is_empty"] is True
    # The buckets must account for every non-zero field: a reserved or negative
    # value that vanished from all three would mean the join mis-bucketed.
    assert join["with_reference"] == (
        join["references_inside_run"]
        + join["references_outside_run"]
        + join["reserved_references"]
    )


def test_the_297_entry_run_does_not_carry_portrait_slot_indices(
    canonical_bytes: bytes,
) -> None:
    """The corrected premise: the 297-entry run is not the portrait population."""
    report = pp.portrait_reference_report(canonical_bytes)["second_population"]
    assert report["run_address"] == "0x086B6BDC"
    assert report["run_entries"] == 297
    assert report["zero_values"] == 7
    assert report["non_zero_values_in_portrait_slot_range"] == 0
    assert report["carries_portrait_slot_indices"] is False


def test_no_other_portrait_slot_source_escapes_the_run(
    canonical_bytes: bytes,
) -> None:
    """The party path and every literal site: measured, not argued from a script."""
    sources = pp.portrait_reference_report(canonical_bytes)["other_portrait_slot_sources"]
    assert sources["party_record_table_address"] == "0x086B82EC"
    assert sources["party_record_stride"] == 24
    assert sources["party_records_scanned"] == 54
    assert sources["party_slot_range"] == [1, 6]
    assert sources["party_distinct_values"] == 60
    assert sources["party_min_slot"] == 0
    assert sources["party_max_slot"] == 159
    assert sources["party_values_outside_run"] == []
    # Exactly two literal loads reach the portrait array base, and eight reach
    # the appearance table; both reproduce LOGX-CHAR-001's sites.
    assert sources["array_base_literal_site_count"] == 2
    assert {item["site"] for item in sources["array_base_literal_sites"]} == {
        "0x08011F52",
        "0x0801213E",
    }
    assert all(item["pool"] == "0x08012194" for item in sources["array_base_literal_sites"])
    assert sources["appearance_table_literal_site_count"] == 8
    # The union of the appearance set and this source covers 133 run entries.
    assert sources["union_run_entries_covered"] == 133
    assert sources["run_entries_covered_by_no_source"] == 22
    # The scan's coverage and its deliberate gap are reported, not implied.
    assert sources["scan_encoding_covered"] == "ldr Rt,[pc,#imm] at every even offset"
    assert "register-computed" in sources["scan_gap"]
