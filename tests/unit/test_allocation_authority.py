"""ROM-CAPACITY-AND-ALLOCATION-001 Checkpoint C: the ONE allocation authority.

Portable and synthetic throughout. These tests answer the Checkpoint C acceptance
questions about *policy* - what may be allocated, from what, deterministically,
without overlap, at the right alignment, failing closed - and they use synthetic
storage models rather than the canonical ROM because the policy is what is under
test. Checkpoint D owns the real-ROM runtime proof.

The canonical production capacity is unchanged by any of this: the profile still
declares the single 256-byte TOOLKIT-028 window, and the 115 promotable candidate
runs from Phase A are not reachable from here at all - no code path in
`allocation.py` reads a candidate, a fill run or an image byte.
"""

from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from tools.webfoot.allocation import (ALLOCATABLE_REGION_CLASSES, ALLOCATION_POLICY,
                                      Addressability, AllocationError, AllocationKind,
                                      AllocationRequest, InsufficientSpaceError,
                                      RegionClass, RegionClassError, StorageModel,
                                      StorageRegion, allocate, withhold)
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import AnchorId, FreeRegion, LayoutError, OwnedRegion, RomRange
from tools.webfoot.profile import GeneratedExpansionProfile, RomProfile

CANONICAL = 0x1000
EXPANDED = 0x2000


def make_profile(*, canonical=CANONICAL, free=(), expansion=None) -> RomProfile:
    """A synthetic profile with exactly the declared capacity a test needs."""
    image = bytes(canonical)
    data = {
        "id": "synthetic-allocation", "game": "synthetic", "region": "test",
        "game_code": "TEST", "size": canonical,
        "sha256": hashlib.sha256(image).hexdigest(),
    }
    profile = RomProfile.from_mapping(data)
    regions = tuple(FreeRegion(RomRange(FileOffset(start), size), evidence)
                    for start, size, evidence in free)
    return replace(profile, free_regions=regions, generated_expansion=expansion)


def expanded_profile(*, free=(), canonical=CANONICAL, output=EXPANDED,
                     evidence="synthetic generated expansion declaration"):
    return make_profile(canonical=canonical, free=free,
                        expansion=GeneratedExpansionProfile(output, 0xFF, evidence))


def region(start, size, classification, evidence="declared"):
    return StorageRegion(RomRange(FileOffset(start), size), classification, evidence)


#: The default subject: a synthetic canonical image with NO declared free space,
#: for tests that supply their own storage model. Its identity and size are what a
#: model must match.
profile = make_profile()


def request(name="payload", *, size=16, alignment=4,
            kind=AllocationKind.PLACEMENT_BODY, addressability=None, **kwargs):
    return AllocationRequest(AnchorId(name), f"owner:{name}", size, alignment,
                             kind=kind, addressability=addressability, **kwargs)


# --- the request model ------------------------------------------------------


def test_a_request_must_state_its_semantic_kind():
    """A caller says WHAT it is placing; it never asks for N empty bytes."""
    with pytest.raises(TypeError):
        AllocationRequest(AnchorId("x"), "owner", 8, 4)   # kind omitted
    with pytest.raises(AllocationError, match="semantic kind"):
        AllocationRequest(AnchorId("x"), "owner", 8, 4, kind="packed_stream")
    assert request().kind is AllocationKind.PLACEMENT_BODY


def test_addressability_defaults_to_what_the_capacity_evidence_supports():
    """Only the compressed-dialogue domain is proven above canonical EOF."""
    assert request(kind=AllocationKind.PACKED_STREAM).addressability \
        is Addressability.EXPANDED_PERMITTED
    for kind in (AllocationKind.PLACEMENT_BODY, AllocationKind.PLACEMENT_REFERENCE_ARRAY,
                 AllocationKind.TEXT_STRING, AllocationKind.RELOCATED_ANCHOR_PAYLOAD,
                 AllocationKind.AUTHORED_MAP_EXPANSION):
        assert request(kind=kind).addressability is Addressability.CANONICAL_ONLY


@pytest.mark.parametrize("size", [0, -1, 1.5, True])
def test_a_request_with_an_impossible_size_is_refused(size):
    with pytest.raises(AllocationError, match="positive"):
        request(size=size)


@pytest.mark.parametrize("alignment", [0, -1, 3, 6, True])
def test_invalid_alignment_fails_clearly(alignment):
    with pytest.raises(LayoutError, match="alignment"):
        request(alignment=alignment)


def test_constraints_must_be_named_strings():
    assert request(constraints=("canonical-only",)).constraints == ("canonical-only",)
    with pytest.raises(AllocationError, match="constraints"):
        request(constraints=("",))


# --- the storage model ------------------------------------------------------


def test_a_model_derives_canonical_free_and_authorized_expansion_from_the_profile():
    model = StorageModel.from_profile(expanded_profile(free=[(0x100, 0x40, "reviewed")]))
    classes = [r.classification for r in model.regions]
    assert classes == [RegionClass.VERIFIED_FREE, RegionClass.PADDING_EXPANDED]
    assert model.canonical_size == CANONICAL and model.image_size == EXPANDED
    assert model.expanded_authorized is True
    assert model.regions[1].range == RomRange(FileOffset(CANONICAL), EXPANDED - CANONICAL)
    assert model.regions[1].evidence == "synthetic generated expansion declaration"


def test_a_larger_image_is_not_authorization_by_itself():
    """No `generated_expansion` declaration, no expanded region, whatever the size."""
    model = StorageModel.from_profile(make_profile(free=[(0x100, 0x40, "reviewed")]))
    assert model.expanded_authorized is False
    assert model.image_size == CANONICAL
    assert all(r.classification is not RegionClass.PADDING_EXPANDED for r in model.regions)


@pytest.mark.parametrize("regions,match", [
    ((region(0x100, 0x40, RegionClass.VERIFIED_FREE),
      region(0x120, 0x40, RegionClass.VERIFIED_FREE)), "overlapping storage"),
    ((region(0xF00, 0x200, RegionClass.VERIFIED_FREE),), "past canonical EOF"),
    ((region(0x1000 + 4, 0x100, RegionClass.PADDING_EXPANDED),), "canonical EOF"),
    ((region(0x100, 0x40, RegionClass.OWNED),
      region(0x100, 0x40, RegionClass.VERIFIED_FREE)), "overlapping"),
])
def test_an_inconsistent_region_model_is_refused_at_construction(regions, match):
    with pytest.raises(RegionClassError, match=match):
        StorageModel(CANONICAL, EXPANDED, regions)


def test_an_allocatable_region_may_not_overlap_an_exclusion_region():
    """OWNED beats a free claim: a model that says both is refused, not resolved."""
    with pytest.raises(RegionClassError, match="overlap"):
        StorageModel(CANONICAL, CANONICAL, (
            region(0x100, 0x100, RegionClass.OWNED),
            region(0x180, 0x100, RegionClass.VERIFIED_FREE),
        ))


def test_the_allocatable_set_is_exactly_verified_free_and_authorized_expansion():
    assert ALLOCATABLE_REGION_CLASSES == {RegionClass.VERIFIED_FREE,
                                          RegionClass.PADDING_EXPANDED}
    model = StorageModel(CANONICAL, EXPANDED, (
        region(0x100, 0x40, RegionClass.VERIFIED_FREE),
        region(0x200, 0x40, RegionClass.OWNED),
        region(0x300, 0x40, RegionClass.REFERENCED),
        region(0x400, 0x40, RegionClass.UNKNOWN),
        region(CANONICAL, EXPANDED - CANONICAL, RegionClass.PADDING_EXPANDED),
    ))
    assert [r.classification for r in model.allocatable_regions()] == [
        RegionClass.VERIFIED_FREE, RegionClass.PADDING_EXPANDED]


# --- class safety -----------------------------------------------------------


@pytest.mark.parametrize("classification", [RegionClass.OWNED, RegionClass.REFERENCED,
                                            RegionClass.UNKNOWN])
def test_a_non_allocatable_class_is_never_allocated(classification):
    """The three classes that are not proven free are exclusion evidence only."""
    model = StorageModel(CANONICAL, CANONICAL,
                         (region(0x100, 0x400, classification),))
    with pytest.raises(InsufficientSpaceError):
        allocate(profile, [request(size=16)], storage=model)


def test_the_canonical_profile_allocates_only_from_its_one_declared_region():
    """The accepted Phase A numbers are unchanged: 256 bytes at 0x7EA400."""
    real = make_profile(canonical=0x800000, free=[
        (0x7EA400, 256, "TOOLKIT-028 bounded window")])
    model = StorageModel.from_profile(real)
    assert model.expanded_authorized is False
    allocation = allocate(real, [request(size=256)])[0]
    assert (allocation.range.start.value, allocation.range.size) == (0x7EA400, 256)
    assert allocation.storage_class is RegionClass.VERIFIED_FREE
    with pytest.raises(InsufficientSpaceError):
        allocate(real, [request(size=257)])


# --- expanded storage and addressability ------------------------------------


def test_expanded_storage_requires_an_expanded_permitted_request():
    """A canonical-only request must not silently receive an expanded address."""
    profile = expanded_profile(free=[(0x100, 0x40, "reviewed")])
    canonical_only = request(name="body", size=0x10,
                             kind=AllocationKind.PLACEMENT_BODY)
    allocation = allocate(profile, [canonical_only])[0]
    assert allocation.is_expanded is False
    assert allocation.range.start.value == 0x100

    # Shrink the canonical region below what the request needs, so the only
    # remaining room is expanded.
    full = replace(profile, free_regions=(
        FreeRegion(RomRange(FileOffset(0x100), 0x8), "reviewed"),))
    with pytest.raises(InsufficientSpaceError):
        allocate(full, [request(name="body", size=0x10,
                                kind=AllocationKind.PLACEMENT_BODY)])
    expanded = allocate(full, [request(name="stream", size=0x10,
                                       kind=AllocationKind.PACKED_STREAM)])[0]
    assert expanded.is_expanded is True
    assert expanded.range.start.value == CANONICAL


def test_an_undeclared_expansion_leaves_a_permitted_request_nowhere_to_go():
    profile = make_profile(free=[(0x100, 0x10, "reviewed")])
    with pytest.raises(InsufficientSpaceError):
        allocate(profile, [request(name="stream", size=0x20,
                                   kind=AllocationKind.PACKED_STREAM)])


def test_the_model_must_be_the_profiles_own_image():
    other = make_profile(canonical=0x2000)
    with pytest.raises(AllocationError, match="canonical size"):
        allocate(other, [request()], storage=StorageModel(CANONICAL, CANONICAL, (
            region(0x100, 0x40, RegionClass.VERIFIED_FREE),)))


# --- determinism ------------------------------------------------------------


def test_identical_inputs_give_identical_allocations():
    profile = make_profile(free=[(0x100, 0x80, "reviewed")])
    batch = [request("a", size=16), request("b", size=32, alignment=8),
             request("c", size=8, alignment=1)]
    first = allocate(profile, batch)
    assert first == allocate(profile, batch)
    assert [a.to_json() for a in first] == [a.to_json() for a in allocate(profile, batch)]


def test_request_order_does_not_change_the_result():
    """The policy orders by anchor identity, so input order is not an input."""
    profile = make_profile(free=[(0x100, 0x80, "reviewed")])
    batch = [request("z", size=16), request("a", size=32, alignment=8),
             request("m", size=8, alignment=1)]
    base = allocate(profile, batch)
    for shuffled in ([batch[2], batch[0], batch[1]], [batch[1], batch[2], batch[0]]):
        assert allocate(profile, shuffled) == base


def test_region_order_does_not_change_the_result():
    forwards = StorageModel(CANONICAL, CANONICAL, (
        region(0x100, 0x40, RegionClass.VERIFIED_FREE),
        region(0x200, 0x40, RegionClass.VERIFIED_FREE)))
    backwards = StorageModel(CANONICAL, CANONICAL, (
        region(0x200, 0x40, RegionClass.VERIFIED_FREE),
        region(0x100, 0x40, RegionClass.VERIFIED_FREE)))
    batch = [request("b", size=16), request("a", size=16), request("c", size=16)]
    assert allocate(profile, batch, storage=forwards) \
        == allocate(profile, batch, storage=backwards)


def test_every_allocation_records_the_policy_and_its_sequence_position():
    profile = make_profile(free=[(0x100, 0x80, "reviewed")])
    allocations = allocate(profile, [request("b", size=8), request("a", size=8)])
    assert [a.request.anchor.value for a in allocations] == ["a", "b"]
    assert [a.order for a in allocations] == [0, 1]
    assert {a.policy for a in allocations} == {ALLOCATION_POLICY}
    assert all("lowest-aligned-first-fit" in a.policy for a in allocations)


def test_duplicate_identity_is_refused():
    profile = make_profile(free=[(0x100, 0x80, "reviewed")])
    with pytest.raises(AllocationError, match="duplicate"):
        allocate(profile, [request("a", size=8), request("a", size=8)])


# --- alignment --------------------------------------------------------------


@pytest.mark.parametrize("alignment", [1, 2, 4, 8, 16, 256])
def test_every_supported_alignment_is_honoured(alignment):
    profile = make_profile(free=[(0x101, 0x400, "reviewed")])
    allocation = allocate(profile, [request(size=alignment, alignment=alignment)])[0]
    assert allocation.range.start.value % alignment == 0
    assert allocation.range.start.value >= 0x101
    assert allocation.range.end <= 0x101 + 0x400


def test_alignment_padding_never_escapes_the_source_region_or_overlaps():
    model = StorageModel(CANONICAL, CANONICAL, (
        region(0x201, 7, RegionClass.VERIFIED_FREE),))
    # 1 byte at alignment 8 must land on 0x208; the region ends at 0x208, so the
    # padded request does not fit even though its raw size does.
    with pytest.raises(InsufficientSpaceError):
        allocate(profile, [request(size=1, alignment=8)], storage=model)
    ok = allocate(profile, [request(size=1, alignment=4)], storage=model)[0]
    assert ok.range.start.value == 0x204
    assert ok.range.end == 0x205


def test_alignment_padding_cannot_overlap_a_reservation():
    """The reservation sits on the first aligned slot, so the next one is used."""
    profile = make_profile(free=[(0x100, 0x40, "reviewed")])
    reserved = (OwnedRegion(RomRange(FileOffset(0x100), 8), "existing"),)
    allocation = allocate(profile, [request(size=4, alignment=8)],
                          occupied=reserved)[0]
    assert allocation.range.start.value == 0x108
    assert allocation.range.start.value % 8 == 0
    assert not allocation.range.overlaps(reserved[0].range)


# --- collisions and reservations --------------------------------------------


def test_an_existing_reservation_is_stepped_over():
    profile = make_profile(free=[(0x100, 0x40, "reviewed")])
    reserved = (OwnedRegion(RomRange(FileOffset(0x100), 0x10), "existing"),)
    allocation = allocate(profile, [request(size=8)], occupied=reserved)[0]
    assert allocation.range.start.value == 0x110
    assert not allocation.range.overlaps(reserved[0].range)


def test_allocations_made_in_one_batch_never_overlap_each_other():
    profile = make_profile(free=[(0x100, 0x40, "reviewed")])
    allocations = allocate(profile, [request(name, size=16) for name in "abcd"])
    for left, right in zip(allocations, allocations[1:]):
        assert not left.range.overlaps(right.range)
    assert len({a.range.start.value for a in allocations}) == 4


def test_a_region_that_only_just_fits_is_used_exactly():
    model = StorageModel(CANONICAL, CANONICAL,
                         (region(0x100, 0x10, RegionClass.VERIFIED_FREE),))
    allocation = allocate(profile, [request(size=0x10)], storage=model)[0]
    assert allocation.range == RomRange(FileOffset(0x100), 0x10)
    with pytest.raises(InsufficientSpaceError):
        allocate(profile, [request(size=0x11)], storage=model)


def test_a_fragmented_capacity_is_filled_before_giving_up():
    """Two regions that individually cannot host the batch, together, can."""
    model = StorageModel(CANONICAL, CANONICAL, (
        region(0x100, 0x10, RegionClass.VERIFIED_FREE),
        region(0x200, 0x10, RegionClass.VERIFIED_FREE)))
    allocations = allocate(profile, [request("a", size=0x10),
                                     request("b", size=0x10)], storage=model)
    assert [a.range.start.value for a in allocations] == [0x100, 0x200]


def test_overlapping_reservations_are_refused_rather_than_merged():
    profile = make_profile(free=[(0x100, 0x40, "reviewed")])
    with pytest.raises(AllocationError, match="overlapping reservations"):
        allocate(profile, [request(size=8)],
                 occupied=(OwnedRegion(RomRange(FileOffset(0x100), 0x10), "one"),
                           OwnedRegion(RomRange(FileOffset(0x108), 0x10), "two")))


# --- fail closed ------------------------------------------------------------


def test_an_impossible_request_fails_closed_and_is_never_truncated():
    model = StorageModel(CANONICAL, CANONICAL,
                         (region(0x100, 0x10, RegionClass.VERIFIED_FREE),))
    with pytest.raises(InsufficientSpaceError) as error:
        allocate(profile, [request(size=0x11)], storage=model)
    message = str(error.value)
    assert "17 bytes" in message and "alignment 4" in message
    assert "placement_body" in message


def test_one_impossible_request_places_nothing_at_all():
    """A batch is all-or-nothing: no partial placement survives a failure."""
    model = StorageModel(CANONICAL, CANONICAL,
                         (region(0x100, 0x20, RegionClass.VERIFIED_FREE),))
    with pytest.raises(InsufficientSpaceError):
        allocate(profile, [request("fits", size=0x10),
                           request("does-not", size=0x20)], storage=model)


def test_an_empty_batch_is_not_an_error():
    assert allocate(profile, []) == ()


# --- withhold is unchanged --------------------------------------------------


def test_withhold_still_only_ever_subtracts():
    regions = (FreeRegion(RomRange(FileOffset(0x1000), 0x100), "reviewed"),)
    assert withhold(regions, (RomRange(FileOffset(0x1040), 0x20),)) == (
        FreeRegion(RomRange(FileOffset(0x1000), 0x40), "reviewed"),
        FreeRegion(RomRange(FileOffset(0x1060), 0xA0), "reviewed"),
    )
    assert withhold(regions, (RomRange(FileOffset(0x1000), 0x100),)) == ()
    assert withhold(regions, (RomRange(FileOffset(0x2000), 8),)) == regions
