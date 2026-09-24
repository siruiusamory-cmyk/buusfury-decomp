"""ROM-CAPACITY-AND-ALLOCATION-001 Phase A against the canonical image.

Read-only: it opens the canonical ROM, measures it and never writes, migrates or
re-identifies anything. It pins the Phase A report's numbers against the image,
so the capacity report cannot silently drift away from what was measured, and it
pins the identity so a differently-revisioned dump cannot satisfy it.

These are the ROM-side half of `tests/unit/test_capacity_model.py`: that file
pins the policy on synthetic images, this one pins the measured result.
"""
import hashlib
from pathlib import Path

import pytest

from tools.research.capacity_model import (OWNED, REFERENCED, UNKNOWN, VERIFIED_FREE,
                                           audit, census_agrees_with_verifier,
                                           require_consistent, resource_distributions)
from tools.research.capacity_proof import scan_candidate_observations
from tools.research.free_space_audit import build_model
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import RomProfileCatalog

SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: The one region a reviewed ticket has declared free in the canonical image.
DECLARED_START, DECLARED_SIZE = 0x7EA400, 256

#: Measured Phase A figures. Every one is a count, not an estimate.
MEASURED = {
    OWNED: 3_037_940,
    REFERENCED: 87,
    VERIFIED_FREE: 256,
    UNKNOWN: 5_350_325,
}
REFERENCE_COUNT = 19_727
REFERENCE_TARGETS = 11_483
REFERENCE_SOURCES_OUTSIDE_OWNED = 11_005
CANDIDATE_OBSERVATIONS = 140_259
CANDIDATE_OBSERVATIONS_ALIGNED = 94_648
CANDIDATE_TARGET_BYTES = 89_516
#: The census after the candidate-SOURCE term was added. The earlier 116 / 23,596
#: figures were one byte too generous: `[0x32EC99, 0x32EC9A)`, a one-byte fill
#: pocket whose following bytes form the word `0x081406FF`, is a candidate source
#: and the reviewed verifier refuses it. These constants pin the corrected run.
PROMOTABLE_RUNS = 115
PROMOTABLE_BYTES = 23_595
#: The largest census run, independently re-verified below.
LARGEST_RUN = (0x7FB408, 0x7FBC60)
#: Region-map spans after spans are split at every evidence boundary rather than
#: only where the classification changes. The map carries all 10,177 distinct
#: annotation owners; class-coalescing used to collapse it to 8,531 spans and
#: drop 5,993 owners.
REGION_SPANS = 27_323


def canonical_rom():
    candidates = sorted(Path("roms").glob("*Buu*.gba"))
    if not candidates:
        pytest.skip("canonical Buu ROM not configured locally")
    rom = candidates[0]
    if hashlib.sha256(rom.read_bytes()).hexdigest() != SHA:
        pytest.skip("local ROM does not match exact canonical Buu identity")
    return rom


@pytest.fixture(scope="module")
def canonical():
    rom = canonical_rom()
    before = (hashlib.sha256(rom.read_bytes()).hexdigest(), rom.stat().st_mtime_ns)
    model = audit(rom, catalog_path="config/roms.yaml")
    yield rom, model
    after = (hashlib.sha256(rom.read_bytes()).hexdigest(), rom.stat().st_mtime_ns)
    assert after == before, "the canonical ROM changed during the capacity audit"


def test_canonical_identity_and_expansion_policy(canonical):
    rom, model = canonical
    assert model.base_sha256 == SHA
    assert model.image_size == 8_388_608
    assert model.free_region_conflicts == ()
    # The declared expansion is a generated-image policy, not canonical space.
    assert model.expansion_output_size == 0x01000000
    assert model.expansion_padding_byte == 0xFF


def test_occupancy_accounting_is_measured_not_estimated(canonical):
    _rom, model = canonical
    accounting = {row["classification"]: row["bytes"] for row in model.accounting()}
    assert accounting == MEASURED
    assert sum(accounting.values()) == model.image_size
    assert model.bytes_by_class() == MEASURED


def test_the_reference_graph_and_its_ownership_gap(canonical):
    """The gap is the finding: much of the graph lives in unclaimed bytes."""
    _rom, model = canonical
    assert len(model.references) == REFERENCE_COUNT
    assert model.reference_targets() == REFERENCE_TARGETS
    assert model.reference_sources_outside_owned == REFERENCE_SOURCES_OUTSIDE_OWNED


def test_the_candidate_census_is_image_wide_not_tail_only(canonical):
    """TOOLKIT-011 scanned one tail; this scans every byte position of the image."""
    rom, model = canonical
    assert model.candidate_observation_count == CANDIDATE_OBSERVATIONS
    assert model.candidate_observation_aligned_count == CANDIDATE_OBSERVATIONS_ALIGNED
    assert model.candidate_target_bytes == CANDIDATE_TARGET_BYTES

    # The same procedure, restricted to the tail, reproduces TOOLKIT-011 exactly,
    # which is what makes the wider scan comparable rather than a new method.
    tail_model = build_model(rom, catalog_path="config/roms.yaml")
    observations = scan_candidate_observations(tail_model["image"], tail_model["tail"])
    assert len(observations) == 516
    assert len({o["target"] for o in observations}) == 475
    assert model.candidate_observation_count > len(observations)


def test_promotable_capacity_is_a_census_not_a_declaration(canonical):
    _rom, model = canonical
    assert len(model.promotable_runs) == PROMOTABLE_RUNS
    assert model.promotable_bytes() == PROMOTABLE_BYTES
    # Nothing is promoted: the profile's declared free space is unchanged.
    assert model.bytes_by_class()[VERIFIED_FREE] == DECLARED_SIZE
    # The margin is what most of the tail's fill fails, not the candidate count.
    assert model.margin_curve["0"]["bytes"] > model.margin_curve["1024"]["bytes"]
    assert model.margin_curve["4096"]["bytes"] == 0


def test_every_census_run_survives_the_reviewed_verifier(canonical):
    """The census and TOOLKIT-028's verifier must agree on EVERY run.

    Checking only the largest run is what let a missing candidate-source term
    ship: the largest run was clean while a one-byte run elsewhere was not. So
    this asserts the aggregate verdict over all runs and names the exact byte
    that the corrected census now excludes.
    """
    rom, model = canonical
    image = rom.read_bytes()
    result = census_agrees_with_verifier(model, image)
    assert result["available"] is True
    assert result["runs"] == PROMOTABLE_RUNS
    assert result["runs_verified"] == PROMOTABLE_RUNS
    assert result["rejected"] == [], result
    assert result["failed_check_counts"] == {}
    assert result["verdict"] == "VERIFIED"
    assert (result["largest"]["start"], result["largest"]["end"]) == LARGEST_RUN
    # The census run really is fill, so `fill` is not what carried the verdict.
    assert set(image[LARGEST_RUN[0]:LARGEST_RUN[1]]) == {0xFF}
    # The one byte the corrected census drops, and why: a valid ROM pointer word
    # starts there, so writing it would corrupt a word an unknown consumer reads.
    assert image[0x32EC99] == 0xFF
    assert int.from_bytes(image[0x32EC99:0x32EC9D], "little") == 0x081406FF
    assert 0x32EC99 not in [offset for start, end in model.promotable_runs
                            for offset in range(start, end)]


def test_the_declared_window_is_reproduced_by_the_census_geometry(canonical):
    """TOOLKIT-028's measured clearance is an input this model reproduces.

    Its window sits inside one margin-adjusted interval; the census must find
    exactly the two remaining runs of that interval and nothing else. The
    clearance figures are TOOLKIT-028's own recorded measurements, so this fails
    if the census changes its boundary convention.
    """
    rom, model = canonical
    image = rom.read_bytes()
    assert set(image[DECLARED_START:DECLARED_START + DECLARED_SIZE]) == {0xFF}
    inside = [run for run in model.promotable_runs
              if 0x7E9D4B < run[0] and run[1] < 0x7EB000]
    assert [(start, end) for start, end in inside] == [(0x7EA14B, 0x7EA400),
                                                       (0x7EA500, 0x7EAC00)]
    # TOOLKIT-028's recorded clearances: 1,717 below the window and 2,816 above.
    assert DECLARED_START - 0x7E9D4B == 1717
    assert 0x7EB000 - (DECLARED_START + DECLARED_SIZE) == 2816
    # The census clips from the target byte, so its interval is the target plus
    # the margin, and the two runs plus the declared window fill it exactly.
    assert inside[0][0] == 0x7E9D4B + model.margin
    assert inside[1][1] == 0x7EB000 - model.margin
    assert sum(end - start for start, end in inside) + DECLARED_SIZE == (
        inside[1][1] - inside[0][0])


def test_resource_distributions_are_counted_from_the_image(canonical):
    rom, _model = canonical
    measured = resource_distributions(rom, catalog_path="config/roms.yaml")["measured"]
    # The string bodies tile the declared pool exactly: a count, not a guess.
    assert measured["text_string_bytes"]["total"] == 82_874
    assert measured["text_string_bytes"]["count"] == 1_534
    assert measured["map_entry_record_bytes"] == {"fixed": 0x38, "count": 452}
    assert measured["dialogue_selector_table_bytes"] == {"fixed": 28, "selectors": 7}
    assert measured["dialogue_container_packed_bytes"]["count"] == 7
    # MapEntry's count field is one byte, so 255 is the encoded ceiling.
    assert measured["placement_record_bytes"]["max"] == 44


def test_the_region_map_keeps_every_owner_and_the_partition_exact(canonical):
    """Evidence-boundary splitting must not cost the byte accounting.

    `known <= owners` holds because a span carries exactly one owner and a fully
    shadowed annotation contributes none. If this assertion ever fails, first
    check whether a newly added annotation is wholly shadowed by a later-starting
    (or shorter, same-start) one - that is correct innermost attribution, not a
    sweep bug - and only then suspect the sweep.
    """
    _rom, model = canonical
    assert len(model.regions) == REGION_SPANS
    assert model.bytes_by_class() == MEASURED
    assert sum(r.size for r in model.regions) == model.image_size
    for left, right in zip(model.regions, model.regions[1:]):
        assert left.end == right.start
    owners = {r.owner for r in model.regions}
    # Every annotation owner the model knows must be findable in the map, not
    # coalesced away by a same-class neighbour or lost to a bounded backward scan
    # for the innermost span. The two extra names are the map's own vocabulary.
    known = {a.owner for a in model.annotations}
    assert known <= owners
    assert owners - known == {"unattributed", "profile.free_regions"}
    assert len(owners) == 10_179


def test_a_conflicting_free_declaration_cannot_reach_an_audit(canonical):
    """The canonical model is clean, and the gate that enforces that is wired in."""
    _rom, model = canonical
    assert model.free_region_conflicts == ()
    assert require_consistent(model) is model


def test_nothing_above_canonical_eof_is_claimed_by_this_model(canonical):
    """The canonical partition stops at the canonical image, by construction."""
    _rom, model = canonical
    assert model.regions[-1].end == model.image_size
    assert all(0 <= r.start < r.end <= model.image_size for r in model.regions)
