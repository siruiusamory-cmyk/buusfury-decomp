"""ROM-ATLAS-001 assembler proofs. Synthetic artifacts only; no ROM bytes.

Every fixture here is written by `_artifacts` into a tmp directory, so these
tests never open the commercial image and never need a private input.
"""

import json

import pytest

from tools.webfoot import atlas_build as ab
from tools.webfoot.atlas import (Confidence as C, UNKNOWN, UNKNOWN_HIGH_ENTROPY,
                                 VERIFIED_FREE, addr, refs_to, unknowns)
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import RomRange


SIZE = ab.IMAGE_SIZE


def _write(directory, name, rows):
    path = directory / f"{name}.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _artifacts(tmp_path, **overrides):
    """A minimal but complete artifact set. Overrides replace one file's rows."""
    rows = {
        "seed_knowledge": [
            {"file_offset": 0x1000, "size": 0x200, "kind": "record_table",
             "identity": "fixture.table", "confidence": "CONFIRMED",
             "source": "synthetic:1", "evidence": "synthetic", "notes": ""},
            {"file_offset": 0x8000, "size": None, "kind": "function",
             "identity": "fixture.headless", "confidence": "RUNTIME_CONFIRMED",
             "source": "synthetic:2", "evidence": "synthetic", "notes": ""},
            {"file_offset": ab.VERIFIED_FREE_OFFSET, "size": ab.VERIFIED_FREE_SIZE,
             "kind": "free_region", "identity": "free_region.toolkit028",
             "confidence": "CONFIRMED", "source": "synthetic:3",
             "evidence": "synthetic", "notes": ""},
        ],
        "graphics_extents": [
            {"file_offset": 0x2000, "size": 0x100, "kind": "compressed_stream",
             "identity": "graphics.container.0000", "confidence": "CONFIRMED",
             "decoded_size": 1024, "reachable_from": "synthetic", "notes": "",
             "evidence": "synthetic", "source": "synthetic", "gba_address": "0x08002000"},
        ],
        "code_functions": [
            {"file_offset": 0x3000, "size": 0x40, "identity": "func.08003000",
             "confidence": "INFERRED", "fetch_address": "0x08003000", "thumb": True,
             "notes": "", "source": "synthetic"},
        ],
        "code_regions": [
            {"file_offset": 0x3000, "size": 0x40, "classification": "code_reached",
             "confidence": "INFERRED", "coverage_bytes": 0x40, "function_count": 1,
             "notes": ""},
        ],
        "scan_text": [
            {"file_offset": 0x4000, "size": 24, "encoding": "utf16le", "cluster_id": 7,
             "char_count": 11, "prefix": "Hello World", "prose_score": "prose",
             "in_claimed_region": False, "notes": ""},
            {"file_offset": 0x4020, "size": 12, "encoding": "ascii", "cluster_id": 7,
             "char_count": 11, "prefix": "SECOND RUN!", "prose_score": "pattern",
             "in_claimed_region": False, "notes": ""},
        ],
        "scan_pointers": [
            {"file_offset": 0x1000, "source_file_offset": 0x1000,
             "target_file_offset": 0x4000, "source_gba": "0x08001000",
             "target_gba": "0x08004000", "source_in_claimed": True,
             "target_in_claimed": False},
            {"file_offset": 0x1004, "source_file_offset": 0x1004,
             "target_file_offset": 0x2000, "source_gba": "0x08001004",
             "target_gba": "0x08002000", "source_in_claimed": True,
             "target_in_claimed": True},
        ],
        "scan_pointer_tables": [
            {"file_offset": 0x1000, "size": 32, "entry_count": 8, "stride": 4,
             "boundary_sharp": True, "overlaps_claimed": True, "targets_distinct": 8,
             "targets_ascending": False, "target_min": 0, "target_max": 0,
             "target_span": 0, "notes": ""},
        ],
        "scan_entropy": [
            {"file_offset": offset, "size": 4096, "block_size": 4096,
             "entropy_bits": 7.9, "distinct_bytes": 250, "ff_run": False,
             "zero_run": False, "in_claimed_region": False,
             "suggested_class": UNKNOWN_HIGH_ENTROPY}
            for offset in range(0, SIZE, 4096)
        ],
        "scan_compression": [
            {"file_offset": 0x2000, "packed_size": 0x100, "declared_decoded_size": 1024,
             "actual_decoded_size": 1024, "decode_ok": True, "round_trip_ok": True,
             "in_claimed_region": True, "gba_address": "0x08002000", "notes": ""},
        ],
        "scan_code_shape": [
            {"file_offset": 0x3000 & ~0xFFF, "size": 4096,
             "suggested_class": "UNKNOWN_EXECUTABLE_CANDIDATE", "code_shape_score": 500,
             "bl_count": 100, "bl_in_range_count": 100, "literal_load_count": 50,
             "prologue_count": 40, "in_claimed_region": False},
        ],
    }
    rows.update(overrides)
    for name, value in rows.items():
        _write(tmp_path, name, value)
    return tmp_path


@pytest.fixture
def report(tmp_path):
    return ab.build_atlas(_artifacts(tmp_path))


# --- the coverage invariant survives assembly --------------------------------


def test_assembly_produces_an_exhaustive_partition(report):
    spans = report.atlas.coverage.spans

    report.atlas.validate()
    assert spans[0].range.start.value == 0
    assert spans[-1].range.end == SIZE
    assert sum(s.range.size for s in spans) == SIZE
    assert all(left.range.end == right.range.start.value
               for left, right in zip(spans, spans[1:]))


def test_assembly_never_leaves_a_default_hole(tmp_path):
    """With no entropy grid at all, the base UNKNOWN still covers every byte."""
    atlas = ab.build_atlas(_artifacts(tmp_path, scan_entropy=[])).atlas

    atlas.coverage.validate()
    assert sum(s.range.size for s in atlas.coverage.spans) == SIZE


# --- weakest-first ordering ---------------------------------------------------


def test_a_confirmed_seed_is_not_repainted_by_a_weaker_scan(report):
    """The entropy grid covers 0x1000 too; the seed must still own those bytes."""
    span = report.atlas.coverage.at(FileOffset(0x1000))

    assert (span.classification, span.confidence) == ("record_table", C.CONFIRMED)


def test_a_weak_scan_owns_only_the_bytes_nothing_stronger_claims(report):
    assert report.atlas.coverage.at(FileOffset(0x1200)).confidence is C.OBSERVED
    assert report.atlas.coverage.at(FileOffset(0x2000)).confidence is C.CONFIRMED
    assert report.atlas.coverage.at(FileOffset(0x3000)).confidence is C.INFERRED


def test_claims_are_applied_in_ascending_strength(report):
    """The paint order is the contract; assert it directly rather than by effect."""
    claims = [(0, 4, UNKNOWN, C.CONFIRMED, "a"), (0, 4, UNKNOWN, C.OBSERVED, "b")]

    spans, _ = ab._paint(claims)

    assert spans[0].confidence is C.CONFIRMED


# --- conflicts ----------------------------------------------------------------


def test_an_equal_strength_disagreement_is_recorded_not_dropped():
    claims = [(0, 8, "code_reached", C.INFERRED, ab.EVIDENCE["code_region"]),
              (0, 8, "compressed_stream", C.INFERRED, ab.EVIDENCE["graphics"])]

    spans, conflicts = ab._paint(claims)

    assert len(conflicts) == 1
    conflict = conflicts[0]
    # graphics is the more specific provenance, so it wins and the loser is named.
    assert (conflict.kept, conflict.dropped) == ("compressed_stream", "code_reached")
    assert (conflict.start, conflict.end) == (0, 8)
    assert spans[0].classification == "compressed_stream"


def test_a_stronger_claim_is_an_overwrite_not_a_conflict():
    claims = [(0, 8, "a", C.OBSERVED, ab.EVIDENCE["entropy"]),
              (0, 8, "b", C.CONFIRMED, ab.EVIDENCE["seed"])]

    spans, conflicts = ab._paint(claims)

    assert conflicts == []
    assert spans[0].classification == "b"


def test_identical_claims_never_conflict():
    claims = [(0, 8, "a", C.OBSERVED, ab.EVIDENCE["entropy"])] * 2

    _, conflicts = ab._paint(claims)

    assert conflicts == []


# --- VERIFIED_FREE is not inferrable ------------------------------------------


def test_only_the_proven_window_is_verified_free(report):
    free = [s for s in report.atlas.coverage.spans if s.classification == VERIFIED_FREE]

    assert [(s.range.start.value, s.range.size) for s in free] == [
        (ab.VERIFIED_FREE_OFFSET, ab.VERIFIED_FREE_SIZE)]


def test_an_unproven_free_region_seed_is_refused(tmp_path):
    seeds = [{"file_offset": 0x5000, "size": 0x100, "kind": "free_region",
              "identity": "fixture.claimed_free", "confidence": "CONFIRMED",
              "source": "synthetic", "evidence": "synthetic", "notes": ""}]

    with pytest.raises(ab.AtlasBuildError, match="only the TOOLKIT-028 window"):
        ab.build_atlas(_artifacts(tmp_path, seed_knowledge=seeds))


def test_a_scanner_cannot_paint_verified_free(tmp_path):
    blocks = [{"file_offset": 0, "size": 4096, "block_size": 4096, "entropy_bits": 0.0,
               "distinct_bytes": 1, "ff_run": True, "zero_run": False,
               "in_claimed_region": False, "suggested_class": VERIFIED_FREE}]

    atlas = ab.build_atlas(_artifacts(tmp_path, scan_entropy=blocks)).atlas

    assert atlas.coverage.at(FileOffset(0)).classification == "PADDING_CANDIDATE"


# --- scan-derived evidence stays capped ---------------------------------------


def test_every_reference_is_candidate_at_most(report):
    assert {r.confidence for r in report.atlas.references} == {C.CANDIDATE}


def test_every_observation_is_candidate_at_most(report):
    from tools.webfoot.atlas import strength
    assert all(strength(o.confidence) <= strength(C.CANDIDATE)
               for o in report.atlas.observations)


def test_a_seed_with_no_extent_becomes_a_marker_object_not_coverage(report):
    marker = next(o for o in report.atlas.objects if o.identity == "seed:fixture.headless")

    assert marker.range.size == 1
    assert dict(marker.attributes)["extent"] == "unknown"
    # It claimed no bytes, so its neighbours were not repainted at CONFIRMED.
    assert report.atlas.coverage.at(FileOffset(0x8004)).confidence is C.OBSERVED


# --- determinism --------------------------------------------------------------


def test_two_assemblies_serialize_byte_identically(tmp_path):
    directory = _artifacts(tmp_path)

    first = "".join(ab.build_atlas(directory).atlas.to_jsonl_lines())
    second = "".join(ab.build_atlas(directory).atlas.to_jsonl_lines())

    assert first == second


def test_written_atlas_round_trips(tmp_path, report):
    path = tmp_path / "out" / "atlas.jsonl"

    ab.write_atlas(report, path)

    reloaded = ab.load_atlas(path)
    assert list(reloaded.to_jsonl_lines()) == list(report.atlas.to_jsonl_lines())


# --- queries ------------------------------------------------------------------


def test_addr_answers_every_layer(report):
    found = addr(report.atlas, FileOffset(0x1010))

    assert found["coverage"].classification == "record_table"
    assert {o.identity for o in found["objects"]} == {
        "seed:fixture.table", "pointer-table-candidate:00001000"}


def test_refs_to_finds_the_inbound_edge(report):
    inbound = refs_to(report.atlas, RomRange(FileOffset(0x4000), 4))

    assert [r.source.value for r in inbound] == [0x1000]


def test_unknown_leaderboard_is_largest_first(report):
    ranked = unknowns(report.atlas, limit=5)

    sizes = [s.range.size for s in ranked]
    assert sizes == sorted(sizes, reverse=True)
    assert all(s.classification in {UNKNOWN, UNKNOWN_HIGH_ENTROPY,
                                    "UNKNOWN_EXECUTABLE_CANDIDATE"} for s in ranked)


def test_text_runs_carry_their_prefix_for_phrase_search(report):
    hits = [o for o in report.atlas.observations
            if o.kind.startswith("text-run-") and "Hello" in o.detail]

    assert [o.range.start.value for o in hits] == [0x4000]


def test_a_text_cluster_spans_all_of_its_runs(report):
    cluster = next(o for o in report.atlas.objects if o.identity == "text-cluster:00007")

    assert (cluster.range.start.value, cluster.range.end) == (0x4000, 0x402C)
    assert dict(cluster.attributes)["encodings"] == "ascii,utf16le"


def test_coverage_statistics_sum_to_the_image(report):
    stats = ab.coverage_statistics(report.atlas)

    assert sum(row["bytes"] for row in stats["by_confidence"]) == SIZE
    assert sum(row["bytes"] for row in stats["by_classification"]) == SIZE


# --- offset parsing keeps the two address spaces distinct ---------------------


@pytest.mark.parametrize("text,expected", [
    ("0x1000", 0x1000), ("4096", 4096), ("0x08001000", 0x1000),
])
def test_parse_offset_reports_which_space_it_read(text, expected):
    offset, how = ab.parse_offset(text)

    assert offset == expected
    assert ("GBA ROM address" in how) is text.startswith("0x08")


@pytest.mark.parametrize("text", ["0x09000000", "0x7FFFFFF"])
def test_parse_offset_refuses_an_offset_outside_the_image(text):
    with pytest.raises(ab.AtlasBuildError, match="outside"):
        ab.parse_offset(text)


def test_missing_artifact_is_named(tmp_path):
    with pytest.raises(ab.AtlasBuildError, match="missing artifact"):
        ab.build_atlas(tmp_path)
