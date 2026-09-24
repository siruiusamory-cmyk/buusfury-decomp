"""Synthetic safety bounds for generated-ROM capacity."""

from __future__ import annotations

from dataclasses import replace
import hashlib

import pytest

from tools.webfoot.allocation import (Addressability, AllocationKind, AllocationRequest,
                                      InsufficientSpaceError, RegionClass, allocate)
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import AnchorId, RomRange
from tools.webfoot.profile import RomProfile
from tools.webfoot.write import (
    ByteChange,
    ChangeValidationError,
    GeneratedAllocationProvenance,
    apply_plan,
    plan_changes,
)


def profile() -> RomProfile:
    image = b"base-image"
    return RomProfile.from_mapping({
        "id": "synthetic", "game": "synthetic", "region": "test",
        "game_code": "TEST", "size": len(image),
        "sha256": hashlib.sha256(image).hexdigest(),
        "generated_expansion": {
            "output_size": 16, "padding_byte": 0xFF,
            "evidence": "synthetic generated-capacity contract",
        },
    })


def provenance(span: RomRange) -> tuple[GeneratedAllocationProvenance, ...]:
    return (GeneratedAllocationProvenance(
        domain="synthetic",
        resource="payload",
        owner="synthetic:payload",
        source_range=RomRange(FileOffset(0), 1),
        allocated_range=span,
        allocated_rom_address=0x08000000 + span.start.value,
        pointer_offset=0,
        expansion_evidence="synthetic generated-capacity contract",
    ),)


def test_generated_image_is_deterministic_and_canonical_prefix_is_preserved():
    base = b"base-image"
    expansion = profile().generated_expansion
    assert expansion is not None
    span = RomRange(FileOffset(10), 2)
    generated = expansion.generated_image(len(base), (span,))
    plan = plan_changes(base, [ByteChange(10, b"\xff\xff", b"OK", "synthetic:payload", "expansion")],
                        profile_id="synthetic", base_sha256=hashlib.sha256(base).hexdigest(),
                        generated_image=generated, generated_allocations=provenance(span))
    output = apply_plan(base, plan)
    assert output == b"base-image" + b"OK" + b"\xff" * 4
    assert apply_plan(base, plan) == output


def test_generated_image_spec_is_retained_in_the_plan():
    base = b"base-image"
    expansion = profile().generated_expansion
    assert expansion is not None
    span = RomRange(FileOffset(10), 1)
    generated = expansion.generated_image(len(base), (span,))
    plan = plan_changes(base, [ByteChange(10, b"\xff", b"A", "synthetic:payload", "manifest")],
                        profile_id="synthetic", base_sha256=hashlib.sha256(base).hexdigest(),
                        generated_image=generated, generated_allocations=provenance(span))
    assert plan.generated_image == generated


def test_generated_image_fails_closed_outside_declared_capacity():
    base = b"base-image"
    expansion = profile().generated_expansion
    assert expansion is not None
    span = RomRange(FileOffset(10), 2)
    generated = expansion.generated_image(len(base), (span,))
    with pytest.raises(ChangeValidationError, match="extends past"):
        plan_changes(base, [ByteChange(15, b"\xff\xff", b"OK", "synthetic:payload", "bounds")],
                     profile_id="synthetic", base_sha256=hashlib.sha256(base).hexdigest(),
                     generated_image=generated, generated_allocations=provenance(span))


def test_generated_image_refuses_an_unallocated_appended_write():
    base = b"base-image"
    expansion = profile().generated_expansion
    assert expansion is not None
    span = RomRange(FileOffset(10), 1)
    generated = expansion.generated_image(len(base), (span,))
    with pytest.raises(ChangeValidationError, match="allocator-issued"):
        plan_changes(base, [ByteChange(11, b"\xff", b"A", "synthetic:payload", "unallocated")],
                     profile_id="synthetic", base_sha256=hashlib.sha256(base).hexdigest(),
                     generated_image=generated, generated_allocations=provenance(span))


def test_generated_image_requires_provenance_for_every_allocator_span():
    base = b"base-image"
    expansion = profile().generated_expansion
    assert expansion is not None
    generated = expansion.generated_image(len(base), (RomRange(FileOffset(10), 1),))
    with pytest.raises(ChangeValidationError, match="exactly match allocation provenance"):
        plan_changes(base, (), profile_id="synthetic",
                     base_sha256=hashlib.sha256(base).hexdigest(),
                     generated_image=generated)


def test_generated_image_refuses_write_owned_by_another_domain():
    base = b"base-image"
    expansion = profile().generated_expansion
    assert expansion is not None
    span = RomRange(FileOffset(10), 1)
    generated = expansion.generated_image(len(base), (span,))
    with pytest.raises(ChangeValidationError, match="allocator-issued expansion provenance"):
        plan_changes(base, [ByteChange(10, b"\xff", b"A", "other-domain:payload", "forged")],
                     profile_id="synthetic", base_sha256=hashlib.sha256(base).hexdigest(),
                     generated_image=generated, generated_allocations=provenance(span))


def test_shared_allocator_uses_expansion_without_relabeling_retail_free_space():
    """The expanded region is authorized storage, NOT canonical free space.

    Two claims, and the request model keeps them apart: a request whose domain is
    not proven above canonical EOF is refused, and an expanded-permitted request
    gets the appended bytes and is *recorded* as expanded - the profile still
    declares zero canonical free regions throughout.
    """
    item = profile()
    expansion = item.generated_expansion
    assert expansion is not None and item.free_regions == ()

    canonical_only = AllocationRequest(AnchorId("payload"), "payload", 3, 4,
                                       kind=AllocationKind.PLACEMENT_BODY)
    assert canonical_only.addressability is Addressability.CANONICAL_ONLY
    with pytest.raises(InsufficientSpaceError):
        allocate(item, [canonical_only])

    expanded = AllocationRequest(AnchorId("payload"), "payload", 3, 4,
                                 kind=AllocationKind.PACKED_STREAM)
    assert expanded.addressability is Addressability.EXPANDED_PERMITTED
    allocation = allocate(item, [expanded])[0]
    assert allocation.range.start.value == 12
    assert allocation.range.end == 15
    assert allocation.storage_class is RegionClass.PADDING_EXPANDED
    assert allocation.is_expanded is True
    assert allocation.source_region == expansion.free_region(item.size).range
    assert item.free_regions == (), "retail free space was not relabeled"

    # A larger file is not authorization on its own: strip the declaration and
    # the same expanded-permitted request is refused.
    undeclared = replace(item, generated_expansion=None)
    with pytest.raises(InsufficientSpaceError):
        allocate(undeclared, [expanded])


def test_a_change_straddling_canonical_eof_is_refused_even_when_it_is_authorized():
    """CQA-09: the guard nothing else backs.

    A change that begins in the last canonical byte and ends in the appended
    padding has `offset >= len(base)` FALSE, so the allocator-authorization branch
    never runs and the free-region/overlap checks see nothing wrong. This guard is
    the ONLY thing that refuses it, which is why its removal is invisible without
    this case: `test_a_change_inside_the_authorized_span_is_accepted` below is the
    positive control that shows the same authorized span does accept a change that
    does not straddle.

    The ticket's exact shape: 10-byte base, 16-byte generated output, one
    authorized byte in the expanded region, and a 2-byte change at offset 9.
    """
    base = b"base-image"
    expansion = profile().generated_expansion
    assert expansion is not None
    span = RomRange(FileOffset(10), 1)
    generated = expansion.generated_image(len(base), (span,))
    straddle = ByteChange(9, base[9:10] + b"\xff", b"XY", "synthetic:payload",
                          "canonical-EOF straddle")
    with pytest.raises(ChangeValidationError, match="straddles canonical EOF"):
        plan_changes(base, [straddle], profile_id="synthetic",
                     base_sha256=hashlib.sha256(base).hexdigest(),
                     generated_image=generated, generated_allocations=provenance(span))


def test_a_change_inside_the_authorized_span_is_accepted():
    """The positive control for the straddle guard.

    Without this, the refusal above could be explained by any of the other checks
    on that plan rather than by the straddle guard itself.
    """
    base = b"base-image"
    expansion = profile().generated_expansion
    assert expansion is not None
    span = RomRange(FileOffset(10), 1)
    generated = expansion.generated_image(len(base), (span,))
    plan = plan_changes(base, [ByteChange(10, b"\xff", b"X", "synthetic:payload",
                                          "inside the authorized span")],
                        profile_id="synthetic", base_sha256=hashlib.sha256(base).hexdigest(),
                        generated_image=generated, generated_allocations=provenance(span))
    assert [change.offset for change in plan.effective_changes] == [10]
    assert apply_plan(base, plan) == base + b"X" + b"\xff" * 5


@pytest.mark.parametrize("size", [9, 33, 0x02000001])
def test_profile_refuses_unsupported_generated_image_sizes(size):
    base = b"base-image"
    data = {
        "id": "synthetic", "game": "synthetic", "region": "test", "game_code": "TEST",
        "size": len(base), "sha256": hashlib.sha256(base).hexdigest(),
        "generated_expansion": {"output_size": size, "padding_byte": 0xFF, "evidence": "test"},
    }
    with pytest.raises(ValueError):
        RomProfile.from_mapping(data)
