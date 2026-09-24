"""ROM-CAPACITY-AND-ALLOCATION-001 Phase A: the occupancy model's own discipline.

Portable and synthetic: these build small images rather than reading a ROM, so
they pin the POLICY the capacity report rests on.

Three things are being protected, and each has a way to be wrong that would not
show up as a crash:

* the partition must be **exhaustive and disjoint** - a class that silently
  stops covering a byte turns "UNKNOWN" into an absence rather than a quantity;
* `UNKNOWN` must never be allocatable and `FF` fill must never be called free -
  the census offers *candidate* windows and nothing here may promote one;
* the census must be the **same procedure** the reviewed window verifier runs,
  or the capacity number would be measured against a second, quieter standard.
"""
from dataclasses import replace
import json
import struct

import pytest

from tools.research.capacity_model import (CLASSIFICATIONS, OWNED, REFERENCED,
                                           UNKNOWN, VERIFIED_FREE, _aligned_capacity,
                                           build_region_map, dialogue_selector_offsets,
                                           extra_promotable_by_margin, fill_runs,
                                           require_consistent, scan_pointer_observations,
                                           span_statistics)
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import FreeRegion, RomRange
from tools.webfoot.profile import ProfileConfigError, RomProfileCatalog, _free_regions

SIZE = 0x4000
CATALOG = RomProfileCatalog.load("config/roms.yaml")
BUU = next(p for p in CATALOG.profiles if p.id == "buus_fury_usa_rev0_01c1707f")


def synthetic(size=SIZE, live_end=0x2000):
    """Live zero bytes below `live_end`, `FF` fill above it."""
    return bytes(live_end) + b"\xff" * (size - live_end)


def profile_with(*free, expansion=None):
    regions = tuple(
        FreeRegion(RomRange(FileOffset(start), size), "synthetic test declaration")
        for start, size in free)
    return replace(BUU, size=SIZE, sha256=BUU.sha256, free_regions=regions,
                   generated_expansion=expansion)


def annotation(start, end, kind="declared_table", owner="t"):
    return {"start": start, "end": end, "kind": kind, "owner": owner,
            "status": "CONFIRMED", "source": "synthetic"}


def reference(source, target, classification="CONFIRMED_REFERENCE"):
    return {"source": source, "target": target, "classification": classification}


def build(image=None, owned=(), references=(), free=(), margin=0x400):
    image = synthetic() if image is None else image
    return build_region_map(image, list(owned), list(references), profile_with(*free),
                            margin=margin)


# --- the partition ----------------------------------------------------------


def test_the_partition_is_exhaustive_and_disjoint():
    model = build(owned=[annotation(0x100, 0x200)],
                  references=[reference(0x10, 0x300)])
    assert sum(r.size for r in model.regions) == SIZE
    for left, right in zip(model.regions, model.regions[1:]):
        assert left.end == right.start
    assert model.regions[0].start == 0
    assert model.regions[-1].end == SIZE
    assert set(model.bytes_by_class()) == set(CLASSIFICATIONS)
    assert sum(model.bytes_by_class().values()) == SIZE


def test_owned_outranks_referenced_on_the_same_byte():
    """A reference target inside a structure is part of the structure."""
    model = build(owned=[annotation(0x100, 0x200)],
                  references=[reference(0x10, 0x150), reference(0x10, 0x300)])
    inside = next(r for r in model.regions if r.start <= 0x150 < r.end)
    outside = next(r for r in model.regions if r.start == 0x300)
    assert inside.classification == OWNED
    assert outside.classification == REFERENCED
    assert model.bytes_by_class()[REFERENCED] == 1


def test_referenced_byte_without_a_structure_is_named_as_an_ownership_gap():
    model = build(references=[reference(0x10, 0x300)])
    region = next(r for r in model.regions if r.start == 0x300)
    assert region.classification == REFERENCED
    assert region.kind == "reference_target_without_covering_structure"


def test_a_reference_field_outside_every_structure_is_counted():
    """The model must report how much of the graph lives in unowned bytes."""
    model = build(owned=[annotation(0x100, 0x200)],
                  references=[reference(0x150, 0x300), reference(0x3000, 0x301)])
    assert model.reference_sources_outside_owned == 1


def test_unknown_is_the_default_and_is_never_promoted():
    model = build()
    assert model.bytes_by_class()[UNKNOWN] == SIZE
    assert model.bytes_by_class()[VERIFIED_FREE] == 0
    assert all(r.confidence == "UNKNOWN" for r in model.regions_of(UNKNOWN))


def test_a_free_declaration_landing_on_content_is_reported_not_hidden():
    """The model detects a free region overlapping content instead of outranking it."""
    model = build(owned=[annotation(0x1000, 0x1100)], free=[(0x1080, 0x100)])
    assert model.free_region_conflicts
    assert "overlaps" in model.free_region_conflicts[0]
    # The overlap is still visible in the accounting as a conflict, not silently
    # absorbed: the annotation below it changed class.
    assert model.bytes_by_class()[VERIFIED_FREE] == 0x100


def test_a_free_declaration_on_a_bare_reference_target_is_a_conflict():
    """REFERENCED is content too, so a free claim over it must not be swallowed.

    A known reference target with no covering annotation is exactly the byte this
    model reports as an ownership gap. Counting only owned bytes in the conflict
    check would let a declaration quietly claim it - and `verify_window`'s
    `known_inbound` check would catch it per window while the whole-image gate
    said nothing.
    """
    model = build(references=[reference(0x10, 0x2000)], free=[(0x1F00, 0x200)])
    assert model.free_region_conflicts
    assert "reference target" in model.free_region_conflicts[0]
    with pytest.raises(ValueError, match="unusable"):
        require_consistent(model)


def test_annotations_that_are_not_confirmed_or_declared_are_counted_not_ignored():
    """An unbacked row must not be silently treated as ownership - or as absence.

    `build_region_map` accepts only CONFIRMED/DECLARED rows as ownership, which is
    the same bar the verifier's `owned` set uses. A row below that bar is skipped
    and the skip is counted, so a future evidence source that introduces one
    cannot quietly change the partition without showing up in the diagnostics.
    Canonically the count is zero.
    """
    model = build(owned=[annotation(0x100, 0x200),
                         {"start": 0x1000, "end": 0x1100, "kind": "candidate_tail",
                          "owner": "upstream_tail", "status": "CANDIDATE",
                          "source": "synthetic"}])
    assert model.bytes_by_class()[OWNED] == 0x100
    assert model.diagnostics["annotations_skipped_by_status"] == 1
    assert "candidate_tail:upstream_tail(CANDIDATE)" in (
        model.diagnostics["annotations_skipped_examples"])


def test_a_conflicting_model_is_refused_at_the_documented_entry_point():
    """Reporting a conflict is not enough; using the model must fail closed.

    `build_region_map` returns the conflict so it can be investigated, but every
    capacity figure derived from a model carrying one is wrong in the unsafe
    direction, so `require_consistent` - which `audit` applies - refuses it. The
    check is exercised through `audit_image`, the exact path the canonical audit
    takes, so the wiring is covered and not merely the predicate.
    """
    from tools.research.capacity_model import audit_image, require_consistent

    image = synthetic()
    clean_profile = profile_with((0x2000, 0x100))
    clean = audit_image(image, [annotation(0x1000, 0x1100)], [],
                        clean_profile)
    assert clean.free_region_conflicts == ()

    poisoned_profile = profile_with((0x1080, 0x100))
    with pytest.raises(ValueError, match="unusable"):
        audit_image(image, [annotation(0x1000, 0x1100)], [], poisoned_profile)

    # The predicate alone still refuses a directly-built bad model.
    bad = build(owned=[annotation(0x1000, 0x1100)], free=[(0x1080, 0x100)])
    with pytest.raises(ValueError, match="unusable"):
        require_consistent(bad)


def test_region_map_is_deterministic_and_machine_readable():
    first = build(owned=[annotation(0x100, 0x200)],
                  references=[reference(0x10, 0x300)],
                  free=[(0x3000, 0x100)])
    second = build(owned=[annotation(0x100, 0x200)],
                   references=[reference(0x10, 0x300)],
                   free=[(0x3000, 0x100)])
    assert list(first.region_map_lines()) == list(second.region_map_lines())
    row = json.loads(list(first.region_map_lines())[0])
    assert set(row) >= {"start", "end", "length", "classification", "confidence",
                        "evidence", "owner", "kind"}
    assert row["length"] == row["end"] - row["start"]


# --- the census -------------------------------------------------------------


def test_fill_alone_is_a_candidate_and_becomes_promotable_only_when_clear():
    """Everything above `live_end` is fill; only the part clear of the header counts."""
    model = build()
    assert model.promotable_runs
    assert all(start >= 0x158 for start, _ in model.promotable_runs)
    # No candidate targets and no content, so one run reaches the image end.
    assert model.promotable_runs[-1][1] == SIZE


def test_a_non_fill_byte_splits_a_run():
    image = bytearray(synthetic())
    image[0x3000] = 0x00
    model = build(image=bytes(image))
    assert not [run for run in model.promotable_runs if run[0] < 0x3000 < run[1]]
    assert [run for run in model.promotable_runs if run[1] == 0x3000]


def test_fill_runs_is_the_single_definition_of_blocked():
    """The census and the margin curve must share one policy, not two copies."""
    image = synthetic()
    rank = bytearray(len(image))
    rank[0x2400] = 2
    targets = bytearray(len(image))
    targets[0x2800] = 1
    sources = bytearray(len(image))
    assert fill_runs(rank, targets, sources, image) == [
        (0x2000, 0x2400), (0x2401, 0x2800), (0x2801, len(image))]
    # The census applies the same policy and then the clearance margin. A known
    # reference target blocks its own byte, but with no *candidate* observation
    # there is no clearance requirement, so the runs survive whole.
    model = build(image=image, owned=[annotation(0x2400, 0x2401)],
                  references=[reference(0x10, 0x2800)])
    assert model.promotable_runs == ((0x2000, 0x2400), (0x2401, 0x2800),
                                     (0x2801, 0x4000))

    # An unresolved pointer-shaped word at the same offset does require clearance.
    pointer = bytearray(image)
    struct.pack_into("<I", pointer, 0x40, 0x08002800)
    clipped = build(image=bytes(pointer), owned=[annotation(0x2400, 0x2401)])
    assert clipped.promotable_runs == ((0x2000, 0x2400), (0x2C00, 0x4000))


def test_a_lone_fill_byte_holding_a_pointer_byte_is_not_promotable():
    """The candidate-SOURCE check, which an earlier draft of this model omitted.

    Only the FIRST byte of a word has to sit in a fill pocket for the pocket to be
    unsafe: `ff 06 14 08` is `0x081406FF`, a valid ROM pointer sourced at an `FF`
    byte. `capacity_proof.verify_window` refuses such a window on
    `candidate_source`; a census without this term is a lower standard that offers
    a byte whose write would corrupt a pointer.
    """
    image = bytearray(0x4000)
    image[0x2000:0x2100] = b"\xff" * 0x100          # an otherwise-clean pocket
    image[0x2100] = 0xFF                            # the candidate's first byte
    image[0x2101:0x2104] = bytes((0x00, 0x00, 0x08))  # -> 0x080000FF, target 0xFF
    model = build(image=bytes(image))
    assert 0x2100 not in [offset for start, end in model.promotable_runs
                          for offset in range(start, end)]
    assert model.candidate_source_bytes >= 1
    assert model.candidate_target_bytes >= 1

    from tools.research.capacity_model import census_agrees_with_verifier
    result = census_agrees_with_verifier(model, bytes(image))
    # Every run must survive the reviewed verifier, including any run near the
    # candidate, so the census and the verifier cannot disagree here.
    assert result["verdict"] == "VERIFIED", result


def test_the_dialogue_selector_reader_refuses_a_shifted_table():
    """One strict reader, so the annotation walk and the sizing walk agree.

    Built at the real table offset with the real seven-entry count, so this
    exercises the production path rather than a test-only seam.
    """
    from tools.research.capacity_model import (DIALOGUE_SELECTOR_COUNT,
                                               DIALOGUE_SELECTOR_TABLE)

    image = bytearray(DIALOGUE_SELECTOR_TABLE + 4 * DIALOGUE_SELECTOR_COUNT + 16)
    for index in range(DIALOGUE_SELECTOR_COUNT):
        struct.pack_into("<I", image, DIALOGUE_SELECTOR_TABLE + 4 * index,
                         0x08002000 + index * 4)
    assert dialogue_selector_offsets(bytes(image)) == tuple(
        0x2000 + index * 4 for index in range(DIALOGUE_SELECTOR_COUNT))

    non_pointer = bytearray(image)
    struct.pack_into("<I", non_pointer, DIALOGUE_SELECTOR_TABLE + 4 * 3, 0x03001068)
    with pytest.raises(ValueError, match="not a ROM pointer"):
        dialogue_selector_offsets(bytes(non_pointer))

    unordered = bytearray(image)
    struct.pack_into("<I", unordered, DIALOGUE_SELECTOR_TABLE + 8, 0x08002000)
    with pytest.raises(ValueError, match="not ascending"):
        dialogue_selector_offsets(bytes(unordered))


def test_a_candidate_target_blocks_its_own_bytes():
    """An unresolved pointer-shaped word is not dismissed because the bytes are fill."""
    image = bytearray(synthetic())
    struct.pack_into("<I", image, 0x10, 0x08003000)
    model = build(image=bytes(image))
    assert model.candidate_target_bytes == 1
    assert not [run for run in model.promotable_runs if run[0] <= 0x3000 < run[1]]
    assert model.candidate_observation_count == 1


def test_a_candidate_anywhere_blocks_its_target_byte():
    """The census is image-wide; a source below the fill still blocks above it."""
    image = bytearray(synthetic())
    struct.pack_into("<I", image, 0x40, 0x08003FF0)
    struct.pack_into("<I", image, 0x50, 0x08002FF0)
    model = build(image=bytes(image))
    blocked = {0x2FF0, 0x3FF0}
    for offset in blocked:
        assert not [run for run in model.promotable_runs if run[0] <= offset < run[1]]


def test_margin_is_what_stops_a_run_sitting_against_a_candidate():
    image = bytearray(synthetic(size=0x8000, live_end=0x1000))
    struct.pack_into("<I", image, 0x10, 0x08004000)
    tight = build(image=bytes(image), margin=0x400)
    flush = build(image=bytes(image), margin=0)
    assert flush.promotable_bytes() > tight.promotable_bytes()
    assert not [run for run in tight.promotable_runs if run[0] == 0x4001]


def test_the_margin_curve_reports_what_the_policy_costs():
    image = bytearray(synthetic(size=0x8000, live_end=0x1000))
    struct.pack_into("<I", image, 0x10, 0x08004000)
    model = build(image=bytes(image), margin=0x400)
    curve = model.margin_curve
    assert set(curve) >= {"0", "1024"}
    assert curve["0"]["bytes"] >= curve["1024"]["bytes"]
    assert curve["0"]["runs"] >= curve["1024"]["runs"]


def test_unknown_bytes_are_never_offered_as_promotable():
    """A run only exists over bytes that are neither owned nor referenced."""
    model = build(owned=[annotation(0x2000, 0x2100)],
                  references=[reference(0x10, 0x2200)])
    for start, end in model.promotable_runs:
        for region in model.regions:
            if region.start >= end or region.end <= start:
                continue
            assert region.classification == UNKNOWN


def test_declared_free_bytes_are_not_counted_as_promotable():
    """Already-declared capacity is not new capacity."""
    plain = build()
    declared = build(free=[(0x2000, 0x800)])
    assert declared.promotable_bytes() == plain.promotable_bytes() - 0x800


# --- scanning and geometry --------------------------------------------------


def test_scan_finds_aligned_and_unaligned_sources_at_every_position():
    image = bytearray(0x2000)
    struct.pack_into("<I", image, 0x100, 0x08001000)
    struct.pack_into("<I", image, 0x205, 0x08001100)
    census = scan_pointer_observations(bytes(image))
    assert census.count == 2
    assert census.aligned_count == 1
    assert census.targets[0x1000] == 1 and census.targets[0x1100] == 1
    collected = scan_pointer_observations(bytes(image), collect=True)
    assert {(o["source"], o["target"]) for o in collected.observations} == {
        (0x100, 0x1000), (0x205, 0x1100)}


def test_scan_ignores_words_outside_the_rom_window():
    image = bytearray(0x2000)
    struct.pack_into("<I", image, 0x100, 0x03001068)   # EWRAM, not ROM
    struct.pack_into("<I", image, 0x200, 0xFFFFFFFF)
    struct.pack_into("<I", image, 0x300, 0x08004000)   # past the image end
    census = scan_pointer_observations(bytes(image))
    assert census.count == 0


def test_aligned_capacity_pays_the_head_slack_and_the_tail_remainder():
    assert _aligned_capacity(0x1000, 0x1100, 4) == 0x100
    assert _aligned_capacity(0x1001, 0x1100, 4) == 0xFC   # 3 bytes head, 1 tail
    assert _aligned_capacity(0x1003, 0x1004, 4) == 0
    assert _aligned_capacity(0x1000, 0x1000, 4) == 0


def test_span_statistics_quantifies_fragmentation_and_minimum_block_loss():
    stats = span_statistics([(0, 8), (0x100, 0x500), (0x1000, 0x2000)])
    assert stats["count"] == 3
    assert stats["total_bytes"] == 8 + 0x400 + 0x1000
    assert stats["largest"][0] == 0x1000
    assert stats["spans_below_32_bytes"] == 1
    assert stats["aligned_4_block1024_bytes"] == 0x1000 + 0x400
    assert stats["aligned_4_block256_bytes"] == 0x1000 + 0x400


def test_extra_promotable_by_margin_is_monotone():
    image = bytearray(synthetic(size=0x8000, live_end=0x1000))
    struct.pack_into("<I", image, 0x10, 0x08004000)
    targets = bytearray(len(image))
    targets[0x4000] = 1
    sources = bytearray(len(image))
    sources[0x10] = 1
    rank = bytearray(len(image))
    for offset in range(0, 0x1000):
        rank[offset] = 2
    curve = extra_promotable_by_margin(rank, targets, sources, bytes(image),
                                       (0, 0x100, 0x1000))
    assert curve["0"]["bytes"] >= curve["256"]["bytes"] >= curve["4096"]["bytes"]


# --- production discipline --------------------------------------------------


@pytest.mark.parametrize("status", ["CANDIDATE", "UNKNOWN", "OBSERVED",
                                    "WINDOW_VERIFIED_PENDING_REVIEW"])
def test_a_census_result_cannot_be_pasted_into_a_profile(status):
    """The model reports capacity; only a reviewed CONFIRMED entry declares it."""
    with pytest.raises(ProfileConfigError, match="CONFIRMED"):
        _free_regions([{"file_offset": 0x2000, "size": 0x100, "status": status,
                        "evidence": "census candidate only"}], SIZE)


def test_census_agrees_with_the_reviewed_window_verifier():
    """EVERY census run must survive the SAME verifier TOOLKIT-028 used.

    A census that cannot be reproduced by the procedure it claims to mirror is a
    second, quieter standard. Checking only the largest run is not enough: the
    largest happened to be clean while a one-byte run elsewhere was not, which is
    how a missing `candidate_source` term shipped once already.
    """
    from tools.research.capacity_model import census_agrees_with_verifier

    # Two runs, not one, so "every run is checked" is actually exercised.
    image = bytearray(synthetic())
    image[0x3000] = 0x00
    model = build(image=bytes(image))
    result = census_agrees_with_verifier(model, bytes(image))
    assert result["available"] is True
    assert len(model.promotable_runs) == 2
    assert result["runs"] == 2
    assert result["runs_verified"] == 2
    assert result["rejected"] == [], result
    assert result["failed_check_counts"] == {}
    assert result["verdict"] == "VERIFIED"
    assert result["checks"]["candidate_source"] is True


def test_census_verification_covers_a_run_that_is_not_the_largest():
    """The regression that let the candidate-source defect ship must fail here.

    An earlier version verified only the largest run, and the largest run happened
    to be clean. So the poison goes on the SMALLER run: if the loop ever regressed
    to largest-only, the rejected list would be empty and this test would fail.
    """
    from tools.research.capacity_model import census_agrees_with_verifier

    image = bytearray(synthetic())
    image[0x3000] = 0x00            # two runs: [0x2000,0x3000) and [0x3001,0x4000)
    model = build(image=bytes(image))
    by_size = sorted(model.promotable_runs, key=lambda run: (run[1] - run[0], run[0]))
    smallest, largest = by_size[0], by_size[-1]
    assert (largest[1] - largest[0]) > (smallest[1] - smallest[0])

    poisoned = replace(model, references=tuple(model.references) + (
        {"source": 0x10, "target": smallest[0], "classification":
         "CANDIDATE_REFERENCE"},))
    result = census_agrees_with_verifier(poisoned, bytes(image))
    assert result["verdict"] == "REJECTED"
    assert [r["start"] for r in result["rejected"]] == [smallest[0]]
    assert result["failed_check_counts"] == {"known_inbound": 1}
    assert result["runs_verified"] == 1


def test_census_agrees_with_the_verifier_refuses_when_a_run_is_not_clear():
    """Same call, a run that is not actually clear: the verifier must reject it.

    Without this the positive test could pass on a verifier that agrees with
    everything.
    """
    from tools.research.capacity_model import census_agrees_with_verifier

    image = bytearray(synthetic())
    model = build(image=bytes(image))
    # Inject a known inbound reference into the middle of the largest run. The
    # verifier's `known_inbound` check must notice, and the aggregate verdict
    # must NOT be a pass.
    largest = max(model.promotable_runs, key=lambda run: run[1] - run[0])
    poisoned = replace(model, references=tuple(model.references) + (
        {"source": 0x10, "target": largest[0], "classification":
         "CANDIDATE_REFERENCE"},))
    result = census_agrees_with_verifier(poisoned, bytes(image))
    assert result["verdict"] == "REJECTED"
    assert [r["start"] for r in result["rejected"]] == [largest[0]]
    assert "known_inbound" in result["rejected"][0]["failed_checks"]
    assert result["failed_check_counts"] == {"known_inbound": 1}
