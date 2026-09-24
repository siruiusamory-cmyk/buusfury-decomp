"""ROM-CAPACITY-AND-ALLOCATION-001 Checkpoint C: provenance, reopen and authorization.

The allocator's decisions have to survive being written down and read back, and an
expanded span has to be unusable by the writer until an allocation record says
otherwise. Both are proved here with synthetic inputs against the production
abstractions - `GeneratedAllocationProvenance`, `WriteManifest`,
`write.plan_changes` - rather than a new sidecar format.

The reopen cycle these tests drive is the Checkpoint C one:

    allocate -> serialized provenance -> reload -> reservations -> allocate again

and it asserts the discriminating half too: WITHOUT the reopened reservations the
allocator does reuse the span, so the reservation is what prevents it rather than
the span happening to be unreachable.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace

import pytest

from tools.webfoot.allocation import (Addressability, AllocationKind, AllocationRequest,
                                      AllocationError, InsufficientSpaceError,
                                      RegionClass, RegionClassError, StorageModel,
                                      StorageRegion, allocate,
                                      reservations_from_allocations,
                                      reservations_from_manifest)
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import AnchorId, FreeRegion, RomRange
from tools.webfoot.profile import GeneratedExpansionProfile, RomProfile
from tools.webfoot.write import (ByteChange, ChangeValidationError, WriteManifest,
                                 apply_plan, plan_changes)

CANONICAL = 0x1000
EXPANDED = 0x2000
EXPANSION_EVIDENCE = "synthetic generated expansion declaration"


def make_profile(*, canonical=CANONICAL, output=EXPANDED, free=()) -> RomProfile:
    image = bytes(canonical)
    data = {"id": "synthetic-allocation", "game": "synthetic", "region": "test",
            "game_code": "TEST", "size": canonical,
            "sha256": hashlib.sha256(image).hexdigest()}
    profile = RomProfile.from_mapping(data)
    regions = tuple(FreeRegion(RomRange(FileOffset(start), size), evidence)
                    for start, size, evidence in free)
    return replace(profile, free_regions=regions,
                   generated_expansion=GeneratedExpansionProfile(
                       output, 0xFF, EXPANSION_EVIDENCE))


def expanded_request(name="stream", size=0x20):
    return AllocationRequest(AnchorId(name), f"owner:{name}", size, 4,
                             kind=AllocationKind.PACKED_STREAM,
                             evidence="synthetic packed stream")


def place(profile, name="stream", size=0x20):
    return allocate(profile, [expanded_request(name, size)])[0]


def provenance_for(allocation, *, pointer_offset=0x100, domain="compressed_dialogue"):
    return allocation.generated_allocation_provenance(
        domain=domain, resource=allocation.request.anchor.value,
        pointer_offset=pointer_offset,
        source_range=RomRange(FileOffset(0), 4))


def manifest_for(profile, allocations):
    return WriteManifest(
        base_profile_id=profile.id, base_sha256=profile.sha256,
        output_sha256="0" * 64, output_size=profile.generated_expansion.output_size,
        changes=(), generated_allocations=tuple(provenance_for(a) for a in allocations))


# --- the allocation record carries what a writer needs ----------------------


def test_an_expanded_allocation_produces_the_writers_authorization_record():
    profile = make_profile()
    allocation = place(profile)
    record = provenance_for(allocation)
    assert record.owner == allocation.request.owner
    assert record.allocated_range == allocation.range
    assert record.allocated_rom_address == allocation.rom_address == CANONICAL + 0x08000000
    assert record.expansion_evidence == EXPANSION_EVIDENCE
    assert record.allocated_range.start.value >= profile.size
    document = record.to_json()
    assert document["allocation_class"] == "generated_expansion"
    assert document["allocated_range"]["file_offset"] == CANONICAL


def test_a_canonical_allocation_has_no_expansion_provenance_to_give():
    """Asking would mint authorization for bytes outside the declared expansion."""
    profile = make_profile(free=[(0x100, 0x40, "reviewed")])
    canonical = allocate(profile, [AllocationRequest(
        AnchorId("body"), "owner:body", 0x10, 4,
        kind=AllocationKind.PLACEMENT_BODY)])[0]
    assert canonical.is_expanded is False
    with pytest.raises(AllocationError, match="canonical allocation"):
        provenance_for(canonical)


def test_the_allocation_record_is_serializable_and_complete():
    profile = make_profile()
    document = place(profile).to_json()
    for key in ("anchor", "kind", "owner", "size", "alignment", "addressability",
                "file_offset", "end", "rom_address", "storage_class",
                "source_region", "canonical_size", "image_size", "expanded",
                "free_region_evidence", "order", "policy", "constraints"):
        assert key in document, key
    assert document["storage_class"] == RegionClass.PADDING_EXPANDED.value
    assert document["expanded"] is True
    assert document["policy"]


def test_the_allocator_never_returns_a_span_that_straddles_canonical_eof():
    """The CQA-09 boundary is unreachable by construction, not by a later guard."""
    profile = make_profile(free=[(CANONICAL - 0x10, 0x10, "reviewed")])
    allocations = allocate(profile, [
        AllocationRequest(AnchorId("a"), "owner:a", 0x10, 4,
                          kind=AllocationKind.PLACEMENT_BODY),
        expanded_request("b", 0x10)])
    assert {a.is_expanded for a in allocations} == {False, True}
    for allocation in allocations:
        assert not (allocation.range.start.value < CANONICAL < allocation.range.end)


# --- expanded writes require matching authorization -------------------------


def _expanded_plan(profile, allocation, change, provenance):
    base = bytes(profile.size)
    spans = tuple(record.allocated_range for record in provenance)
    generated = profile.generated_expansion.generated_image(profile.size, spans)
    return plan_changes(base, [change], profile_id=profile.id,
                        base_sha256=profile.sha256, generated_image=generated,
                        generated_allocations=provenance)


def test_an_expanded_write_is_accepted_only_with_its_own_allocation_record():
    profile = make_profile()
    allocation = place(profile)
    record = provenance_for(allocation)
    change = ByteChange(allocation.range.start.value,
                        b"\xff" * allocation.range.size,
                        b"Z" * allocation.range.size,
                        allocation.request.owner, "authorized expanded payload")

    plan = _expanded_plan(profile, allocation, change, (record,))
    assert apply_plan(bytes(profile.size), plan)[CANONICAL:CANONICAL + 0x20] \
        == b"Z" * 0x20

    # The same write with no record at all: refused (mutation M5 detects this).
    with pytest.raises(ChangeValidationError, match="allocator-issued expansion provenance"):
        _expanded_plan(profile, allocation, change, ())

    # A record for a DIFFERENT span does not authorize this one.
    elsewhere = replace(allocation, range=RomRange(FileOffset(CANONICAL + 0x100), 0x20))
    with pytest.raises(ChangeValidationError, match="allocator-issued expansion provenance"):
        _expanded_plan(profile, allocation, change, (provenance_for(elsewhere),))


def test_an_expanded_write_by_another_owner_is_refused():
    profile = make_profile()
    allocation = place(profile)
    record = provenance_for(allocation)
    forged = ByteChange(allocation.range.start.value, b"\xff" * 0x20, b"Z" * 0x20,
                        "some-other-domain", "forged")
    with pytest.raises(ChangeValidationError, match="allocator-issued expansion provenance"):
        _expanded_plan(profile, allocation, forged, (record,))


# --- reopen ------------------------------------------------------------------


def test_a_manifest_round_trip_restores_the_allocations_as_reservations():
    profile = make_profile()
    first = place(profile, "stream-one")
    manifest = manifest_for(profile, [first])
    document = json.loads(manifest.dumps())

    reopened = reservations_from_manifest(document)
    assert [r.range for r in reopened] == [first.range]
    assert [r.range for r in reopened] == [r.range for r in
                                           reservations_from_allocations((first,))]
    # The manifest names the SEMANTIC owner; the reservation names what the span
    # is. The spans are what must agree, and they do.
    assert reopened[0].owner == first.request.owner


def test_reopening_prevents_the_next_allocation_from_reusing_the_span():
    profile = make_profile()
    first = place(profile, "stream-one")
    document = json.loads(manifest_for(profile, [first]).dumps())
    reopened = reservations_from_manifest(document)

    # The discriminating half: without the reopened reservations the allocator
    # DOES hand back the same span, so the reservation is what prevents reuse.
    naive = place(profile, "stream-two")
    assert naive.range == first.range

    second = allocate(profile, [expanded_request("stream-two")], occupied=reopened)[0]
    assert second.range != first.range
    assert not second.range.overlaps(first.range)
    assert second.range.start.value == CANONICAL + 0x20


def test_reopen_is_deterministic_and_the_base_identity_is_retained():
    profile = make_profile()
    first = place(profile, "stream-one")
    document = json.loads(manifest_for(profile, [first]).dumps())
    assert document["base"]["sha256"] == profile.sha256
    assert document["base"]["profile_id"] == profile.id
    assert document["output"]["size"] == EXPANDED

    reopened = reservations_from_manifest(document)
    inputs = [expanded_request("a"), expanded_request("b")]
    one = allocate(profile, inputs, occupied=reopened)
    two = allocate(profile, inputs, occupied=reopened)
    assert one == two
    assert [a.to_json() for a in one] == [a.to_json() for a in two]
    # An unchanged rebuild reproduces its own plan.
    repeated = json.loads(manifest_for(profile, [first]).dumps())
    assert repeated == document


def test_relocation_destinations_also_become_reservations_on_reopen():
    profile = make_profile()
    span = RomRange(FileOffset(CANONICAL), 0x20)
    allocation = place(profile)
    document = {
        "schema_version": 1,
        "changes": [],
        "relocations": [{"anchor": "map:0010/placement_references",
                         "owner": "map:0010/placement_references",
                         "new_range": {"file_offset": span.start.value, "size": span.size}}],
    }
    reopened = reservations_from_manifest(document)
    assert [r.range for r in reopened] == [span]
    second = allocate(profile, [expanded_request("stream-two")], occupied=reopened)[0]
    assert second.range.start.value == CANONICAL + 0x20
    assert allocation.range == span


def test_an_unreadable_manifest_is_refused_rather_than_ignored():
    with pytest.raises(AllocationError):
        reservations_from_manifest({"generated_allocations": [{"owner": "x"}]})
    with pytest.raises(AllocationError):
        reservations_from_manifest(None)


def test_reopened_reservations_still_cannot_overlap_each_other():
    profile = make_profile()
    first = place(profile, "stream-one")
    second = allocate(profile, [expanded_request("stream-two")],
                      occupied=reservations_from_allocations((first,)))[0]
    manifest = manifest_for(profile, [first, second])
    document = json.loads(manifest.dumps())
    reopened = reservations_from_manifest(document)
    assert len(reopened) == 2
    for left, right in zip(reopened, reopened[1:]):
        assert not left.range.overlaps(right.range)


# --- one authority -----------------------------------------------------------


def test_there_is_exactly_one_allocator_module():
    """No competing implementation may exist beside the authoritative owner."""
    from pathlib import Path

    modules = sorted(path.name for path in Path("tools/webfoot").glob("allocation*.py"))
    assert modules == ["allocation.py"], modules
    for name in ("new_allocator.py", "production_allocator.py", "allocation2.py"):
        assert not (Path("tools/webfoot") / name).exists(), name


def test_the_allocator_does_not_read_image_bytes():
    """Its whole input is declarations; it never decides from FF/00 patterns.

    Checked structurally rather than by reading the prose: the module opens no
    file, indexes no image buffer, and imports neither the atlas nor the capacity
    research model. `FF` and `00` survive only in text explaining that they are
    NOT evidence.
    """
    import inspect

    from tools.webfoot import allocation as module

    source = inspect.getsource(module)
    for forbidden in ("read_bytes", "read_text", "open(", "image[", "import struct",
                      "from .atlas", "from tools.research"):
        assert forbidden not in source, forbidden
    # No research-model or atlas name is reachable as a module attribute either.
    assert not [name for name in vars(module) if "atlas" in name.lower()]
    assert not [name for name in vars(module) if "capacity" in name.lower()
                and name != "ALLOCATION_POLICY"]
