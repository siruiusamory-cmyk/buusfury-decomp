"""ROM-ATLAS-001 synthetic proofs. No commercial bytes or private inputs."""

from dataclasses import replace

import pytest

from tools.webfoot.atlas import (Atlas, AtlasError, AtlasObject, AtlasReference,
    CONFIDENCE_ORDER, Confidence as C, CoverageMap, CoverageSpan, Observation,
    PADDING_CANDIDATE, UNKNOWN, UNKNOWN_HIGH_ENTROPY, UNKNOWN_TEXTLIKE,
    VERIFIED_FREE, addr, in_range, objects_of_kind, refs_from, refs_to, strength,
    unknowns)
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import Provenance, ReferenceEncoding as RE, RomRange


SIZE = 0x400
PROFILE_ID = "synthetic-v1"
SHA = "f" * 64
PROOF = Provenance(PROFILE_ID, SHA, "synthetic fixture construction")


def span(start, size):
    return RomRange(FileOffset(start), size)


def base_coverage():
    return CoverageMap.single(SIZE, UNKNOWN, C.UNKNOWN, PROOF)


@pytest.fixture
def atlas():
    coverage = base_coverage().refine(span(0x100, 0x40), UNKNOWN_TEXTLIKE, C.CANDIDATE, PROOF)
    coverage = coverage.refine(span(0x200, 0x20), VERIFIED_FREE, C.CONFIRMED, PROOF)
    objects = (
        AtlasObject("fixture:table", span(0x100, 0x40), "pointer-table", C.INFERRED, PROOF),
        AtlasObject("fixture:entry", span(0x110, 0x8), "pointer-table-slot", C.INFERRED,
                    PROOF, (("index", "4"),)),
        AtlasObject("fixture:pool", span(0x300, 0x40), "text-pool", C.CONFIRMED, PROOF),
    )
    references = (
        AtlasReference(FileOffset(0x110), FileOffset(0x300), 4,
                       RE.ABSOLUTE_ROM_U32_LE, C.CANDIDATE, PROOF),
        AtlasReference(FileOffset(0x080), FileOffset(0x110), 4,
                       RE.ABSOLUTE_ROM_U32_LE, C.CONFIRMED, PROOF),
    )
    observations = (
        Observation(span(0x300, 0x10), "utf16le-run", "8 chars", C.OBSERVED, PROOF),
        Observation(span(0x000, 0x1000 // 16), "entropy-block", "7.9 bits", C.OBSERVED, PROOF),
    )
    result = Atlas(PROFILE_ID, SHA, SIZE, coverage, objects, references, observations)
    result.validate()
    return result


# --- SC3: coverage invariant -------------------------------------------------


def test_single_span_covers_the_whole_image():
    coverage = base_coverage()

    coverage.validate()
    assert coverage.spans[0].range.size == SIZE


def test_coverage_refuses_a_late_start():
    coverage = CoverageMap((CoverageSpan(span(4, SIZE - 4), UNKNOWN, C.UNKNOWN, PROOF),), SIZE)

    with pytest.raises(AtlasError, match="coverage starts at 0x4"):
        coverage.validate()


def test_coverage_refuses_a_short_tail():
    coverage = CoverageMap((CoverageSpan(span(0, SIZE - 4), UNKNOWN, C.UNKNOWN, PROOF),), SIZE)

    with pytest.raises(AtlasError, match=r"coverage ends at 0x3FC, expected 0x400"):
        coverage.validate()


def test_coverage_names_the_offsets_of_a_gap():
    coverage = CoverageMap((
        CoverageSpan(span(0, 0x10), UNKNOWN, C.UNKNOWN, PROOF),
        CoverageSpan(span(0x20, SIZE - 0x20), UNKNOWN, C.UNKNOWN, PROOF),
    ), SIZE)

    with pytest.raises(AtlasError, match=r"coverage gap between 0x10 and 0x20"):
        coverage.validate()


def test_coverage_names_the_offsets_of_an_overlap():
    coverage = CoverageMap((
        CoverageSpan(span(0, 0x20), UNKNOWN, C.UNKNOWN, PROOF),
        CoverageSpan(span(0x10, SIZE - 0x10), UNKNOWN, C.UNKNOWN, PROOF),
    ), SIZE)

    with pytest.raises(AtlasError, match=r"coverage overlap between 0x20 and 0x10"):
        coverage.validate()


def test_coverage_refuses_descending_spans():
    coverage = CoverageMap((
        CoverageSpan(span(0x10, 0x20), UNKNOWN, C.UNKNOWN, PROOF),
        CoverageSpan(span(0, 0x10), UNKNOWN, C.UNKNOWN, PROOF),
        CoverageSpan(span(0x30, SIZE - 0x30), UNKNOWN, C.UNKNOWN, PROOF),
    ), SIZE)

    with pytest.raises(AtlasError, match=r"out of order at 0x10 then 0x0"):
        coverage.validate()


def test_coverage_refuses_a_byte_total_that_misses_the_image():
    coverage = CoverageMap((CoverageSpan(span(0, SIZE), UNKNOWN, C.UNKNOWN, PROOF),), SIZE - 4)

    with pytest.raises(AtlasError, match=r"coverage ends at 0x400, expected 0x3FC"):
        coverage.validate()


# --- SC4: refine -------------------------------------------------------------


def test_refine_splits_one_span_into_three():
    coverage = base_coverage().refine(span(0x100, 0x40), UNKNOWN_TEXTLIKE, C.CANDIDATE, PROOF)

    coverage.validate()
    assert [(s.range.start.value, s.range.size, s.classification) for s in coverage.spans] == [
        (0, 0x100, UNKNOWN), (0x100, 0x40, UNKNOWN_TEXTLIKE), (0x140, SIZE - 0x140, UNKNOWN)]


def test_refine_coalesces_identical_neighbours():
    coverage = base_coverage()
    coverage = coverage.refine(span(0x100, 0x20), PADDING_CANDIDATE, C.CANDIDATE, PROOF)
    coverage = coverage.refine(span(0x120, 0x20), PADDING_CANDIDATE, C.CANDIDATE, PROOF)

    middle = [s for s in coverage.spans if s.classification == PADDING_CANDIDATE]
    assert len(middle) == 1
    assert (middle[0].range.start.value, middle[0].range.size) == (0x100, 0x40)


def test_refine_coalesces_a_hole_back_into_its_neighbours():
    """The gap between two identical spans disappears when it matches them."""
    coverage = base_coverage()
    coverage = coverage.refine(span(0x100, 0x20), PADDING_CANDIDATE, C.CANDIDATE, PROOF)
    coverage = coverage.refine(span(0x140, 0x20), PADDING_CANDIDATE, C.CANDIDATE, PROOF)
    assert len(coverage.spans) == 5

    filled = coverage.refine(span(0x120, 0x20), PADDING_CANDIDATE, C.CANDIDATE, PROOF)

    assert [(s.range.start.value, s.range.size, s.classification) for s in filled.spans] == [
        (0, 0x100, UNKNOWN), (0x100, 0x60, PADDING_CANDIDATE), (0x160, SIZE - 0x160, UNKNOWN)]


def test_refine_refuses_to_downgrade_a_stronger_span():
    coverage = base_coverage().refine(span(0x200, 0x20), VERIFIED_FREE, C.CONFIRMED, PROOF)

    with pytest.raises(AtlasError, match="refusing to downgrade 0x200..0x220"):
        coverage.refine(span(0x1F0, 0x40), UNKNOWN_HIGH_ENTROPY, C.OBSERVED, PROOF)


def test_refine_allows_an_equal_or_stronger_overwrite():
    coverage = base_coverage().refine(span(0x200, 0x20), UNKNOWN_TEXTLIKE, C.INFERRED, PROOF)

    promoted = coverage.refine(span(0x200, 0x20), "text-pool", C.CONFIRMED, PROOF)

    assert promoted.at(FileOffset(0x200)).confidence is C.CONFIRMED


def test_refine_refuses_a_range_past_the_image():
    with pytest.raises(Exception):
        base_coverage().refine(span(SIZE - 4, 0x10), UNKNOWN_TEXTLIKE, C.CANDIDATE, PROOF)


def test_coverage_lookup_and_overlapping(atlas):
    assert atlas.coverage.at(FileOffset(0x120)).classification == UNKNOWN_TEXTLIKE
    assert atlas.coverage.at(FileOffset(0x0FF)).classification == UNKNOWN
    found = atlas.coverage.overlapping(span(0x0F0, 0x20))
    assert [s.classification for s in found] == [UNKNOWN, UNKNOWN_TEXTLIKE]

    with pytest.raises(AtlasError, match="outside"):
        atlas.coverage.at(FileOffset(SIZE))


# --- SC5: observation cap ----------------------------------------------------


@pytest.mark.parametrize("confidence", [C.INFERRED, C.CONFIRMED, C.RUNTIME_CONFIRMED])
def test_observation_refuses_confidence_above_candidate(confidence):
    with pytest.raises(AtlasError, match="exceeds CANDIDATE"):
        Observation(span(0, 4), "entropy-block", "detail", confidence, PROOF)


@pytest.mark.parametrize("confidence", [C.UNKNOWN, C.OBSERVED, C.CANDIDATE])
def test_observation_accepts_confidence_up_to_candidate(confidence):
    assert Observation(span(0, 4), "entropy-block", "detail", confidence, PROOF)


def test_confidence_ladder_does_not_collapse():
    assert len(set(CONFIDENCE_ORDER)) == 6
    assert [strength(c) for c in CONFIDENCE_ORDER] == [0, 1, 2, 3, 4, 5]
    assert not hasattr(C.OBSERVED, "__add__") or C.OBSERVED + "x" == "OBSERVEDx"


# --- SC6: atlas validation ---------------------------------------------------


def test_atlas_refuses_duplicate_object_identity(atlas):
    twin = AtlasObject("fixture:table", span(0x280, 4), "other", C.OBSERVED, PROOF)

    with pytest.raises(AtlasError, match="duplicate object identity 'fixture:table'"):
        replace(atlas, objects=atlas.objects + (twin,)).validate()


def test_atlas_refuses_an_out_of_bounds_object(atlas):
    far = AtlasObject("fixture:far", span(SIZE - 4, 0x10), "other", C.OBSERVED, PROOF)

    with pytest.raises(AtlasError, match="fixture:far.* out of bounds"):
        replace(atlas, objects=atlas.objects + (far,)).validate()


def test_atlas_refuses_an_out_of_bounds_reference_target(atlas):
    stray = AtlasReference(FileOffset(0x90), FileOffset(SIZE + 8), 4,
                           RE.ABSOLUTE_ROM_U32_LE, C.CANDIDATE, PROOF)

    with pytest.raises(AtlasError, match="out of bounds"):
        replace(atlas, references=atlas.references + (stray,)).validate()


@pytest.mark.parametrize("wrong", [
    Provenance("other-profile", SHA, "synthetic"),
    Provenance(PROFILE_ID, "0" * 64, "synthetic"),
])
def test_atlas_refuses_mismatched_provenance(atlas, wrong):
    alien = AtlasObject("fixture:alien", span(0x280, 4), "other", C.OBSERVED, wrong)

    with pytest.raises(AtlasError, match="wrong profile provenance"):
        replace(atlas, objects=atlas.objects + (alien,)).validate()


def test_atlas_refuses_coverage_of_a_different_size(atlas):
    with pytest.raises(AtlasError, match="coverage covers"):
        replace(atlas, image_size=SIZE * 2).validate()


# --- SC7: deterministic round trip -------------------------------------------


def test_jsonl_round_trips_byte_identically(atlas):
    first = "".join(atlas.to_jsonl_lines())

    second = "".join(Atlas.from_jsonl_lines(first.splitlines(keepends=True)).to_jsonl_lines())

    assert first == second


def test_jsonl_uses_explicit_newlines_and_no_carriage_returns(atlas):
    lines = list(atlas.to_jsonl_lines())

    assert all(line.endswith("\n") and "\r" not in line for line in lines)
    assert lines[0].startswith('{"base_sha256"')


def test_jsonl_order_is_stable_against_input_order(atlas):
    shuffled = replace(atlas, objects=tuple(reversed(atlas.objects)),
                       references=tuple(reversed(atlas.references)),
                       observations=tuple(reversed(atlas.observations)))

    assert list(shuffled.to_jsonl_lines()) == list(atlas.to_jsonl_lines())


def test_round_trip_preserves_every_layer(atlas):
    parsed = Atlas.from_jsonl_lines(atlas.to_jsonl_lines())

    assert (parsed.profile_id, parsed.base_sha256, parsed.image_size) == (PROFILE_ID, SHA, SIZE)
    assert parsed.coverage.spans == atlas.coverage.spans
    assert set(parsed.objects) == set(atlas.objects)
    assert set(parsed.references) == set(atlas.references)
    assert set(parsed.observations) == set(atlas.observations)


def test_parser_refuses_an_unknown_layer():
    with pytest.raises(AtlasError, match="unknown atlas layer"):
        Atlas.from_jsonl_lines(['{"layer": "speculation"}'])


def test_parser_refuses_a_missing_meta_line():
    with pytest.raises(AtlasError, match="missing its meta line"):
        Atlas.from_jsonl_lines([])


# --- SC8: query surface ------------------------------------------------------


def test_addr_reports_every_layer_at_one_offset(atlas):
    found = addr(atlas, FileOffset(0x114))

    assert found["coverage"].classification == UNKNOWN_TEXTLIKE
    assert {o.identity for o in found["objects"]} == {"fixture:table", "fixture:entry"}
    assert found["observations"] == ()


def test_addr_includes_a_nested_object_and_its_parent(atlas):
    assert {o.identity for o in addr(atlas, FileOffset(0x100))["objects"]} == {"fixture:table"}
    assert {o.identity for o in addr(atlas, FileOffset(0x117))["objects"]} == {
        "fixture:table", "fixture:entry"}


def test_refs_to_finds_inbound_edges(atlas):
    assert [r.source.value for r in refs_to(atlas, FileOffset(0x300))] == [0x110]
    assert [r.source.value for r in refs_to(atlas, span(0x100, 0x40))] == [0x080]
    assert refs_to(atlas, FileOffset(0x3FF)) == ()


def test_refs_from_finds_outbound_edges(atlas):
    assert [r.target.value for r in refs_from(atlas, FileOffset(0x110))] == [0x300]
    assert [r.target.value for r in refs_from(atlas, span(0x080, 4))] == [0x110]
    # A source FIELD is width bytes wide, so its interior counts as sourced there.
    assert [r.target.value for r in refs_from(atlas, FileOffset(0x112))] == [0x300]


def test_in_range_reports_everything_intersecting(atlas):
    found = in_range(atlas, span(0x300, 0x10))

    assert [s.classification for s in found["coverage"]] == [UNKNOWN]
    assert [o.identity for o in found["objects"]] == ["fixture:pool"]
    assert [r.source.value for r in found["references"]] == [0x110]
    assert [o.kind for o in found["observations"]] == ["utf16le-run"]


def test_unknowns_is_a_largest_first_leaderboard(atlas):
    ranked = unknowns(atlas)

    sizes = [s.range.size for s in ranked]
    assert sizes == sorted(sizes, reverse=True)
    # VERIFIED_FREE and non-vocabulary classifications are not unknowns.
    assert all(s.classification != VERIFIED_FREE for s in ranked)
    assert unknowns(atlas, limit=1) == ranked[:1]
    assert len(ranked) == 4


def test_objects_of_kind_filters_and_orders_by_offset(atlas):
    assert [o.identity for o in objects_of_kind(atlas, "pointer-table")] == ["fixture:table"]
    assert objects_of_kind(atlas, "no-such-kind") == ()


def test_objects_may_nest_and_overlap(atlas):
    table, entry, pool = atlas.objects

    assert table.overlaps(entry) and entry.overlaps(table)
    assert not table.overlaps(pool)
    assert table.contains(FileOffset(0x13F)) and not table.contains(FileOffset(0x140))


def test_object_refuses_unsorted_attributes():
    with pytest.raises(AtlasError, match="sorted"):
        AtlasObject("fixture:x", span(0, 4), "kind", C.OBSERVED, PROOF,
                    (("z", "1"), ("a", "2")))
