"""DRAGONBYTE-Z-OWNER-RANGE-INDEX-001: the range index against the atlas.

The synthetic half proves the index's own answers on a hand-built `Atlas`. The
measured half is the acceptance proof: where `build/atlas/atlas.jsonl` exists
locally, sampled offsets are compared against direct `atlas.*` answers, and the
index's unowned byte total against the atlas's own unknown byte sum. The atlas
is read once per session and is never rebuilt here.

The nine real-atlas tests need that locally assembled atlas. CI does not provide
it (no canonical ROM), so they skip there and a green pipeline is not evidence
for the acceptance proof; the proof was measured on a machine holding the image.
"""

from __future__ import annotations

import random
from bisect import bisect_left
from pathlib import Path

import pytest

from tools.webfoot import atlas as atlas_module
from tools.webfoot.atlas import (Atlas, AtlasError, AtlasObject, AtlasReference,
                                 Confidence, CoverageMap, CoverageSpan, RangeIndex,
                                 UNKNOWN, UNKNOWN_HIGH_ENTROPY, VERIFIED_FREE,
                                 in_range, unknowns)
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import LayoutError, Provenance, ReferenceEncoding, RomRange

PROFILE_ID = "synthetic"
BASE_SHA256 = "0" * 64
IMAGE_SIZE = 0x1000
PROOF = Provenance(PROFILE_ID, BASE_SHA256, "synthetic range-index fixture")

#: The identity the assembled atlas must carry, so a stale or foreign local
#: atlas is refused rather than measured against.
REAL_PROFILE_ID = "buus_fury_usa_rev0_01c1707f"
REAL_IMAGE_SIZE = 8388608
REAL_ATLAS = Path("build") / "atlas" / "atlas.jsonl"

#: The sampled-offset population: seeded random offsets, the first byte of this
#: many atlas objects, and the middle of this many unknown spans. The object
#: population steps by len(objects) // SAMPLE_OBJECTS, so it is 129 of 11470
#: objects, not 128. The sample is bounded because each offset is also asked of
#: `atlas.addr` (14.31 ms per call on this image, measured) and `atlas.in_range`.
SAMPLE_SIZE = 256
SAMPLE_SEED = 20261009
SAMPLE_OBJECTS = 128
SAMPLE_UNKNOWNS = 64


def span(start, size):
    return RomRange(FileOffset(start), size)


@pytest.fixture
def atlas():
    objects = (
        AtlasObject("fixture:table", span(0x100, 0x40), "pointer-table",
                    Confidence.INFERRED, PROOF),
        AtlasObject("fixture:entry", span(0x110, 0x8), "pointer-table-slot",
                    Confidence.INFERRED, PROOF),
        AtlasObject("fixture:pool", span(0x300, 0x40), "text-pool",
                    Confidence.CONFIRMED, PROOF),
    )
    references = (
        AtlasReference(FileOffset(0x200), FileOffset(0x110), 4,
                       ReferenceEncoding.ABSOLUTE_ROM_U32_LE, Confidence.CANDIDATE, PROOF),
        AtlasReference(FileOffset(0x104), FileOffset(0x308), 4,
                       ReferenceEncoding.ABSOLUTE_ROM_U32_LE, Confidence.CANDIDATE, PROOF),
    )
    coverage = CoverageMap((
        CoverageSpan(span(0, 0x100), UNKNOWN, Confidence.UNKNOWN, PROOF),
        CoverageSpan(span(0x100, 0x100), UNKNOWN_HIGH_ENTROPY,
                     Confidence.OBSERVED, PROOF),
        CoverageSpan(span(0x200, 0x100), VERIFIED_FREE, Confidence.CONFIRMED, PROOF),
        CoverageSpan(span(0x300, 0x100), UNKNOWN, Confidence.UNKNOWN, PROOF),
        CoverageSpan(span(0x400, 0xC00), UNKNOWN, Confidence.UNKNOWN, PROOF),
    ), IMAGE_SIZE)
    return Atlas(PROFILE_ID, BASE_SHA256, IMAGE_SIZE, coverage, objects, references)


# --- range to owners ---------------------------------------------------------


def test_one_owner_claims_a_byte(atlas):
    found = RangeIndex(atlas).spans_at(FileOffset(0x101))
    assert [(item.owner, item.range, item.source) for item in found] == [
        ("fixture:table", span(0x100, 0x40), "atlas-object")]


def test_nested_owners_are_both_reported_in_offset_order(atlas):
    index = RangeIndex(atlas)
    assert [item.owner for item in index.spans_at(FileOffset(0x110))] == [
        "fixture:table", "fixture:entry"]
    assert index.owners_of(span(0x110, 1)) == ("fixture:entry", "fixture:table")


def test_a_byte_no_owner_claims_reports_nothing(atlas):
    index = RangeIndex(atlas)
    assert index.spans_at(FileOffset(0x2FF)) == ()
    assert index.owners_of(span(0x2FF, 1)) == ()


def test_a_byte_before_every_owner_reports_nothing(atlas):
    assert RangeIndex(atlas).spans_at(FileOffset(0x0FF)) == ()


def test_a_byte_past_every_owner_reports_nothing(atlas):
    assert RangeIndex(atlas).spans_at(FileOffset(0xFFF)) == ()


def test_a_range_crossing_two_owners_reports_both(atlas):
    assert RangeIndex(atlas).owners_of(span(0x108, 0x10)) == (
        "fixture:entry", "fixture:table")


def test_declared_extents_are_owners_too(atlas):
    index = RangeIndex(atlas, ((span(0x90, 0x20), "declared:seed-table"),))
    assert [(item.owner, item.source) for item in index.spans_at(FileOffset(0x95))] == [
        ("declared:seed-table", "declared-extent")]


def test_the_profile_declared_tables_are_reported_by_their_own_names(real_atlas):
    """The declaration source is the profile's, so no name is minted here."""
    from tools.dragonbyte.rawbytes import declared_extents
    from tools.webfoot.catalog import load_catalog

    profile = load_catalog(None).profiles[0]
    declared = declared_extents(profile)
    assert declared, "the packaged profile declares at least one table extent"
    index = RangeIndex(real_atlas, declared)
    for extent, name in declared:
        found = index.spans_at(FileOffset(extent.start.value))
        assert name in {item.owner for item in found}, name
        assert (extent.start.value, extent.size) in [
            (item.range.start.value, item.range.size) for item in found], name
    assert index.overview()["declared_extents"] == len(declared)


def test_lookups_require_typed_input(atlas):
    index = RangeIndex(atlas)
    with pytest.raises(AtlasError, match="typed FileOffset"):
        index.spans_at(0x100)
    with pytest.raises(AtlasError, match="typed RomRange"):
        index.spans_overlapping(0x100)


def test_a_range_past_the_image_is_refused(atlas):
    with pytest.raises(LayoutError):
        RangeIndex(atlas).spans_overlapping(span(IMAGE_SIZE - 1, 2))


def test_a_declared_extent_past_the_image_is_refused(atlas):
    """A configuration extent is a claim about this image, so it is bounded too."""
    with pytest.raises(AtlasError, match="out of image"):
        RangeIndex(atlas, ((span(IMAGE_SIZE + 10, 4), "declared:probe"),))


def test_a_declared_extent_ending_past_the_image_is_refused(atlas):
    with pytest.raises(AtlasError, match="out of image"):
        RangeIndex(atlas, ((span(IMAGE_SIZE - 2, 4), "declared:tail"),))


def test_the_candidate_narrowing_never_drops_a_claiming_span(atlas):
    """The bisect bounds are a filter; the brute-force scan is the answer."""
    index = RangeIndex(atlas, ((span(0x105, 0x30), "declared:wide"),))
    everything = index.spans
    for offset in range(0, IMAGE_SIZE):
        expected = [item for item in everything
                    if item.range.start.value <= offset < item.range.end]
        assert list(index.spans_at(FileOffset(offset))) == expected, hex(offset)
    for start in range(0, IMAGE_SIZE - 0x100, 0x80):
        for size in (1, 0x10, 0x100):
            wanted = span(start, size)
            expected = [item for item in everything if item.range.overlaps(wanted)]
            assert list(index.spans_overlapping(wanted)) == expected, (hex(start), size)


# --- owner to ranges ---------------------------------------------------------


def test_ranges_of_an_owner_returns_its_extents(atlas):
    index = RangeIndex(atlas)
    assert index.ranges_of("fixture:table") == (span(0x100, 0x40),)
    assert index.ranges_of("fixture:pool") == (span(0x300, 0x40),)


def test_ranges_of_an_unknown_owner_is_empty(atlas):
    assert RangeIndex(atlas).ranges_of("fixture:absent") == ()


def test_the_two_directions_agree(atlas):
    index = RangeIndex(atlas)
    for offset in range(0, IMAGE_SIZE, 7):
        for owner in index.owners_of(span(offset, 1)):
            assert any(item.contains(FileOffset(offset))
                       for item in index.ranges_of(owner))


def test_the_owner_leaderboard_counts_bytes_per_owner(atlas):
    assert dict(RangeIndex(atlas).owner_bytes()) == {
        "fixture:table": 0x40, "fixture:entry": 0x8, "fixture:pool": 0x40}


# --- the atlas's own answers -------------------------------------------------


def test_at_reports_the_atlas_coverage_classification_and_confidence(atlas):
    index = RangeIndex(atlas)
    for offset in (0x10, 0x100, 0x200, 0x300, 0x500):
        found = index.at(FileOffset(offset))
        coverage = atlas.coverage.at(FileOffset(offset))
        assert found["classification"] == coverage.classification
        assert found["confidence"] == coverage.confidence


def test_at_owners_are_the_objects_over_that_byte(atlas):
    found = RangeIndex(atlas).at(FileOffset(0x110))
    assert found["owners"] == ("fixture:entry", "fixture:table")
    assert found["classification"] == UNKNOWN_HIGH_ENTROPY


def test_at_references_are_the_atlas_own_in_range_answer(atlas):
    index = RangeIndex(atlas)
    for offset in (0x100, 0x104, 0x110, 0x200, 0x308):
        assert index.at(FileOffset(offset))["references"] == (
            in_range(atlas, span(offset, 1))["references"])


def test_the_index_invents_no_classification(atlas):
    vocabulary = {item.classification for item in atlas.coverage.spans}
    index = RangeIndex(atlas)
    for item in index.spans:
        # A span carries an owner and an extent, never a classification of its own.
        assert not hasattr(item, "classification")
    for offset in range(0, IMAGE_SIZE, 257):
        assert index.at(FileOffset(offset))["classification"] in vocabulary


@pytest.mark.parametrize("start,size", [
    (0x100, 0x100), (0x110, 0x8), (0x120, 0x20), (0x108, 0x10), (0x300, 0x40)])
def test_the_scan_reports_owners_and_the_unowned_count(atlas, start, size):
    wanted = span(start, size)
    result = RangeIndex(atlas).scan(wanted)
    assert result["range"] == wanted
    assert result["owners"] == len(result["hits"])
    for hit in result["hits"]:
        # A hit reports the owner's first byte inside the scanned range, never a
        # byte of that owner outside it.
        assert wanted.start.value <= hit["file_offset"] < wanted.end, hex(start)
        assert hit["spans"], hit["owner"]


def test_the_scan_anchors_a_hit_inside_the_scanned_range(atlas):
    """An owner that begins before the range is anchored at the range's start."""
    index = RangeIndex(atlas, ((span(0x80, 0x100), "declared:wide"),))
    result = index.scan(span(0x100, 0x10))
    hit = next(item for item in result["hits"] if item["owner"] == "declared:wide")
    assert hit["file_offset"] == 0x100
    assert hit["classification"] == UNKNOWN_HIGH_ENTROPY


def test_the_scan_of_an_unowned_range_is_zero_hits_and_a_count(atlas):
    result = RangeIndex(atlas).scan(span(0x400, 0x100))
    assert result["owners"] == 0
    assert result["hits"] == ()
    # UNKNOWN is an answer with a number, not a silence.
    assert result["unowned_bytes"] == 0x100


def test_the_scan_counts_only_the_overlapping_part_of_a_span(atlas):
    index = RangeIndex(atlas)
    assert index.scan(span(0x180, 0x80))["unowned_bytes"] == 0x80
    assert index.scan(span(0x1C0, 0x80))["unowned_bytes"] == 0x40


def test_overview_unowned_bytes_is_the_atlas_unknown_sum(atlas):
    index = RangeIndex(atlas)
    assert index.overview()["unowned_bytes"] == sum(item.range.size
                                                    for item in unknowns(atlas))
    assert dict(index.overview()["by_classification"]) == {
        UNKNOWN: 0x100 + 0x100 + 0xC00, UNKNOWN_HIGH_ENTROPY: 0x100,
        VERIFIED_FREE: 0x100}


def test_overview_reports_the_atlas_partition_and_not_a_second_one(atlas):
    overview = RangeIndex(atlas).overview()
    assert overview["coverage_spans"] == len(atlas.coverage.spans)
    assert sum(size for _, size in overview["by_classification"]) == IMAGE_SIZE


def test_the_index_never_rewrites_the_atlas(atlas):
    index = RangeIndex(atlas)
    assert [item.range for item in index.spans] == [
        item.range for item in sorted(index.spans, key=lambda s: s.range.start.value)]
    assert index.atlas is atlas
    assert atlas.coverage.spans[0].classification == UNKNOWN
    assert atlas.coverage.spans[0].range == span(0, 0x100)


# --- the assembled atlas: the acceptance proof -------------------------------


@pytest.fixture(scope="session")
def real_atlas():
    if not REAL_ATLAS.is_file():
        pytest.skip("assembled atlas (build/atlas/atlas.jsonl) not present locally")
    with REAL_ATLAS.open(encoding="utf-8") as handle:
        loaded = Atlas.from_jsonl_lines(handle)
    assert loaded.profile_id == REAL_PROFILE_ID
    assert loaded.image_size == REAL_IMAGE_SIZE
    return loaded


@pytest.fixture(scope="session")
def real_index(real_atlas):
    return RangeIndex(real_atlas)


def sampled_offsets(atlas):
    """Deterministic offsets: atlas objects, unknown spans, then a seeded sample.

    Neither answer dominates: the first byte of `SAMPLE_OBJECTS` objects, the
    middle of `SAMPLE_UNKNOWNS` unknown spans, and `SAMPLE_SIZE` offsets from a
    fixed seed. Every population is stated, so the sample is reproducible.
    """
    chosen = {object.range.start.value
              for object in atlas.objects[::max(1, len(atlas.objects) // SAMPLE_OBJECTS)]}
    chosen.update(item.range.start.value + item.range.size // 2
                  for item in unknowns(atlas)[:SAMPLE_UNKNOWNS])
    generator = random.Random(SAMPLE_SEED)
    chosen.update(generator.randrange(atlas.image_size) for _ in range(SAMPLE_SIZE))
    return tuple(sorted(chosen))


def test_the_sampled_offsets_equal_the_atlas_answers(real_atlas, real_index):
    """The acceptance proof: classification, confidence, owners, references.

    `atlas.addr` supplies the coverage and object answer and `atlas.in_range` the
    reference answer; the index must equal both on every sampled offset. `addr`
    and `in_range` are called once each per offset, and their answers are also
    the two independent implementations the equality is measured against.
    """
    sampled = sampled_offsets(real_atlas)
    assert len(sampled) >= SAMPLE_SIZE
    unowned = 0
    for offset in sampled:
        found = real_index.at(FileOffset(offset))
        reported = atlas_module.addr(real_atlas, FileOffset(offset))
        assert found["classification"] == reported["coverage"].classification, hex(offset)
        assert found["confidence"] == reported["coverage"].confidence, hex(offset)
        assert found["owners"] == tuple(sorted(item.identity
                                               for item in reported["objects"])), hex(offset)
        assert found["references"] == in_range(real_atlas, span(offset, 1))["references"], (
            hex(offset))
        unowned += not found["owners"]
    # The population exercises both answers, so the equality is not proved only
    # where an owner exists.
    assert unowned > 0
    assert unowned < len(sampled)


def test_the_sampled_owners_are_the_atlas_objects_over_that_byte(real_atlas, real_index):
    """The owner half of the same equality, taken from the object layer itself.

    Each object contributes to the sampled offsets it contains, found by bisect,
    so this stays a second independent path to the same answer without
    re-scanning every object per offset.
    """
    sampled = sorted(sampled_offsets(real_atlas))
    expected: dict[int, list[str]] = {offset: [] for offset in sampled}
    for object in real_atlas.objects:
        first = bisect_left(sampled, object.range.start.value)
        last = bisect_left(sampled, object.range.end)
        for position in range(first, last):
            expected[sampled[position]].append(object.identity)
    for offset in sampled:
        assert real_index.at(FileOffset(offset))["owners"] == tuple(
            sorted(expected[offset])), hex(offset)


def test_owner_to_ranges_agrees_with_the_atlas_objects(real_atlas, real_index):
    for object in real_atlas.objects[::97]:
        assert object.range in real_index.ranges_of(object.identity), object.identity


def test_the_real_unknown_total_is_the_atlas_unknown_byte_sum(real_atlas, real_index):
    """The index's unowned total against the atlas's own unknown byte sum."""
    expected = sum(item.range.size for item in unknowns(real_atlas))
    assert real_index.overview()["unowned_bytes"] == expected


def test_an_unknown_span_is_not_automatically_unowned(real_atlas, real_index):
    """`unowned_bytes` counts classifications; an owner is a separate layer."""
    spans = unknowns(real_atlas)[:64]
    assert spans
    for item in spans:
        offset = FileOffset(item.range.start.value)
        found = real_index.at(offset)
        assert found["classification"] in atlas_module.UNKNOWN_CLASSIFICATIONS
        # Whatever the answer, it is an answer: the classification is the
        # atlas's and the owners are the objects over that byte.
        assert found["owners"] == tuple(sorted(
            object.identity for object in real_atlas.objects if object.contains(offset)))


def test_the_reference_index_is_a_filter_and_not_a_second_answer(real_atlas, real_index):
    """`_references_in_range` is brute-forced against `in_range` on real offsets.

    The bisect candidate set is a filter, so the only thing that makes it right is
    the exact predicate applied to every candidate. This walks the whole edge
    layer once per offset and compares, which is the check the candidate set
    cannot make about itself.
    """
    sampled = sampled_offsets(real_atlas)
    wanted = sampled[::max(1, len(sampled) // 64)]
    assert len(wanted) >= 32
    for offset in wanted:
        point = span(offset, 1)
        expected = [ref for ref in real_atlas.references
                    if ref.source_range.overlaps(point)
                    or (isinstance(ref, AtlasReference) and point.contains(ref.target))]
        assert list(real_index._references_in_range(point)) == expected, hex(offset)
        assert real_index.at(FileOffset(offset))["references"] == tuple(
            dict.fromkeys(expected)), hex(offset)


def test_the_real_index_reuses_the_atlas_classification_vocabulary(real_atlas, real_index):
    vocabulary = {item.classification for item in real_atlas.coverage.spans}
    reported = set(dict(real_index.overview()["by_classification"]))
    assert reported <= vocabulary
    assert reported == vocabulary


def test_the_real_scan_hits_are_the_atlas_answers(real_atlas, real_index):
    """`scan` must not compute a classification of its own: `at` is the source."""
    for start in (0x0, 0x1000, 0x80000, 0x400000, 0x7E0000):
        wanted = span(start, 0x100)
        result = real_index.scan(wanted)
        assert result["unowned_bytes"] == sum(
            min(item.range.end, wanted.end) - max(item.range.start.value, wanted.start.value)
            for item in unknowns(real_atlas) if item.range.overlaps(wanted))
        for hit in result["hits"]:
            # The owner may begin far before the range, so a hit outside the
            # scanned range is the defect this asserts against.
            assert wanted.start.value <= hit["file_offset"] < wanted.end, hit["owner"]
            assert hit["owner"] in real_index.owners_of(span(hit["file_offset"], 1))
            assert hit["classification"] == real_index.at(
                FileOffset(hit["file_offset"]))["classification"]
            assert hit["spans"] == real_index.spans_of(hit["owner"])
