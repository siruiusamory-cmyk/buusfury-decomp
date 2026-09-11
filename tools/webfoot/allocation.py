"""Deterministic first-fit allocation from trusted profile declarations only."""

from dataclasses import dataclass
from typing import Iterable

from .binary import FileOffset
from .layout import (AnchorId, FreeRegion, LayoutError, OwnedRegion, RomRange,
                     check_alignment, require_name)
from .profile import RomProfile


class InsufficientSpaceError(LayoutError):
    pass


@dataclass(frozen=True, slots=True)
class AllocationRequest:
    anchor: AnchorId
    owner: str
    size: int
    alignment: int

    def __post_init__(self) -> None:
        if not isinstance(self.anchor, AnchorId):
            raise LayoutError("allocation requires anchor identity")
        require_name(self.owner)
        check_alignment(self.alignment)
        if type(self.size) is not int or self.size <= 0:
            raise LayoutError("allocation size must be positive")


@dataclass(frozen=True, slots=True)
class Allocation:
    request: AllocationRequest
    range: RomRange
    free_region_evidence: str

    def to_json(self) -> dict:
        return {"anchor": self.request.anchor.value, "owner": self.request.owner,
                "range": self.range.to_json(), "alignment": self.request.alignment,
                "free_region_evidence": self.free_region_evidence}


def withhold(free_regions: Iterable[FreeRegion],
             taken: Iterable[RomRange]) -> tuple[FreeRegion, ...]:
    """The same declared free regions, minus spans already spoken for.

    Subtraction only. A region is split or trimmed around each taken span and is
    never grown, merged or moved, so this can only ever offer LESS capacity than the
    profile declared - it cannot manufacture space that was not already trusted.

    TOOLKIT-036 moved this out of `authored_placements`, where it was private. It
    carries no domain semantics - it is span arithmetic over declared regions - and
    it is the primitive a build-scoped reservation set is threaded with, so every
    allocating domain subtracts what earlier domains already took the same way.
    """
    taken = tuple(taken)
    result = []
    for region in free_regions:
        spans = [(region.range.start.value, region.range.end)]
        for span in taken:
            remaining = []
            for start, end in spans:
                if span.end <= start or span.start.value >= end:
                    remaining.append((start, end))
                    continue
                if start < span.start.value:
                    remaining.append((start, span.start.value))
                if span.end < end:
                    remaining.append((span.end, end))
            spans = remaining
        for start, end in spans:
            result.append(FreeRegion(RomRange(FileOffset(start), end - start), region.evidence))
    return tuple(result)


def allocate(profile: RomProfile, requests: Iterable[AllocationRequest], *,
             occupied: Iterable[OwnedRegion] = ()) -> tuple[Allocation, ...]:
    """Stable identity order, lowest aligned first fit. No mutable allocator state."""
    ordered = sorted(requests, key=lambda r: r.anchor)
    if len({r.anchor for r in ordered}) != len(ordered):
        raise LayoutError("duplicate allocation request")
    reserved = sorted(occupied, key=lambda r: r.range.start.value)
    for region in reserved:
        region.range.validate(profile.size)
    if any(a.range.overlaps(b.range) for a, b in zip(reserved, reserved[1:])):
        raise LayoutError("overlapping allocation ownership")
    free = sorted(profile.free_regions, key=lambda r: r.range.start.value)
    for region in free:
        region.range.validate(profile.size)
    if any(a.range.overlaps(b.range) for a, b in zip(free, free[1:])):
        raise LayoutError("overlapping profile free regions")
    result = []
    for request in ordered:
        selected = None
        for region in free:
            position = region.range.start.value
            while position + request.size <= region.range.end:
                position = ((position + request.alignment - 1) // request.alignment) * request.alignment
                trial = RomRange(FileOffset(position), request.size)
                if trial.end > region.range.end:
                    break
                collision = next((r for r in reserved if trial.overlaps(r.range)), None)
                if collision is not None:
                    position = collision.range.end
                    continue
                selected = Allocation(request, trial, region.evidence)
                break
            if selected is not None:
                break
        if selected is None:
            raise InsufficientSpaceError(f"insufficient declared free space for {request.anchor.value} "
                                         f"({request.size} bytes, alignment {request.alignment})")
        reserved.append(OwnedRegion(selected.range, request.owner))
        reserved.sort(key=lambda r: r.range.start.value)
        result.append(selected)
    return tuple(result)
