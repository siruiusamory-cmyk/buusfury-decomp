"""Atomic anchor relocation, compiled into the existing attributed write path."""

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

from .allocation import Allocation, AllocationKind, AllocationRequest, allocate
from .binary import FileOffset
from .document import RomDocument
from .layout import AnchorId, LayoutError, OwnedRegion, ReferenceClass
from .write import (ByteChange, ReferenceRewrite, RelocationProvenance, WriteManifest,
                    WritePlan, apply_plan, emit_image, plan_changes)


#: Which semantic allocation kind a relocatable anchor kind asks for. The two
#: production eligible kinds are named; anything else that `plan_relocation` may
#: legitimately move - a synthetic fixture anchor, or a kind a later ticket
#: publishes before it names a class here - is recorded as the conservative
#: generic relocation kind. The fallback is canonical-only, so an unmodelled kind
#: can never acquire expanded storage by being unmodelled.
_ALLOCATION_KIND = {
    "placement_reference_array": AllocationKind.PLACEMENT_REFERENCE_ARRAY,
    "text-string": AllocationKind.TEXT_STRING,
}


def _allocation_kind(anchor) -> AllocationKind:
    return _ALLOCATION_KIND.get(anchor.kind, AllocationKind.RELOCATED_ANCHOR_PAYLOAD)


class CandidateReferenceError(LayoutError):
    pass


@dataclass(frozen=True, slots=True)
class RelocationRequest:
    anchor: AnchorId
    payload: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.anchor, AnchorId):
            raise LayoutError("relocation requires logical anchor identity")
        if type(self.payload) is not bytes or not self.payload:
            raise LayoutError("relocation requires nonempty immutable payload bytes")


@dataclass(frozen=True, slots=True)
class RelocationResult:
    document: RomDocument
    plan: WritePlan
    allocations: tuple[Allocation, ...]

    def to_json(self) -> dict:
        from hashlib import sha256
        manifest = WriteManifest(self.plan.base_profile_id, self.plan.base_sha256,
            sha256(self.document.image).hexdigest(), len(self.document.image),
            self.plan.effective_changes, relocations=self.plan.relocations)
        return {"document": self.document.to_json(),
                "allocations": [a.to_json() for a in self.allocations],
                "manifest": manifest.to_json()}


def plan_relocation(document: RomDocument, requests: Iterable[RelocationRequest]) -> RelocationResult:
    """One batch against the verified base; no writes or mutable state on failure.

    Source fields within moved anchors follow their anchors. Interior target
    deltas are preserved. Old source fields within retired content stay intact.
    A result document describes output; it is not a new trusted base profile.
    """
    # Do not accept a forged document, stale image, or already-modified ROM as
    # trusted base. Re-establish full profile identity before using any layout.
    if document.retired:
        raise LayoutError("submit relocations as one batch against the verified base")
    document = RomDocument.from_bytes(document.image, document.profile,
                                     anchors=document.anchors, references=document.references)
    ordered = sorted(requests, key=lambda r: r.anchor)
    if not ordered or len({r.anchor for r in ordered}) != len(ordered):
        raise LayoutError("relocation batch must have unique, nonempty requests")
    moving = {r.anchor: document.anchor(r.anchor) for r in ordered}
    for anchor in moving.values():
        if not anchor.relocatable:
            raise LayoutError(f"non-relocatable anchor: {anchor.identity.value}")
    blocked = [r for r in document.references
               if r.classification is ReferenceClass.CANDIDATE_REFERENCE
               and (r.target in moving or any(a.range.overlaps(r.source_range) for a in moving.values()))]
    if blocked:
        sources = ", ".join(f"0x{r.source.value:08X}" for r in sorted(blocked, key=lambda r: r.source))
        raise CandidateReferenceError(f"unresolved candidate references block relocation: {sources}")
    occupied = [OwnedRegion(a.range, a.owner) for a in document.anchors]
    for ref in document.references:
        if not any(a.range.contains(ref.source) for a in document.anchors):
            occupied.append(OwnedRegion(ref.source_range, f"reference:{ref.target.value}"))
    allocations = allocate(document.profile,
        [AllocationRequest(r.anchor, moving[r.anchor].owner, len(r.payload),
                           moving[r.anchor].alignment,
                           kind=_allocation_kind(moving[r.anchor]),
                           evidence=f"relocated {moving[r.anchor].kind} anchor")
         for r in ordered], occupied=occupied)
    destinations = {a.request.anchor: a for a in allocations}
    buffers = {r.anchor: bytearray(r.payload) for r in ordered}
    anchors = tuple(replace(a, range=destinations[a.identity].range) if a.identity in moving else a
                    for a in document.anchors)
    new_anchors = {a.identity: a for a in anchors}
    references = []
    changes = []
    rewrites = []
    for ref in sorted(document.references, key=lambda r: r.source):
        source_anchor = next((a for a in document.anchors if a.range.contains(ref.source)), None)
        source_moved = source_anchor is not None and source_anchor.identity in moving
        new_source = ref.source
        if source_moved:
            delta = ref.source.value - source_anchor.range.start.value
            allocation = destinations[source_anchor.identity]
            if delta + ref.encoding.width > allocation.range.size:
                raise LayoutError("new payload removes a reference source field")
            new_source = FileOffset(allocation.range.start.value + delta)
        new_ref = replace(ref, source=new_source)
        references.append(new_ref)
        target = new_anchors[ref.target]
        if ref.target_delta >= target.range.size:
            raise LayoutError("new payload strands an interior reference target")
        new_target = FileOffset(target.range.start.value + ref.target_delta)
        if ref.target not in moving and not source_moved:
            continue
        encoded = ref.encoding.encode(new_target, new_source, len(document.image))
        if source_moved:
            buffers[source_anchor.identity][delta:delta + ref.encoding.width] = encoded
        else:
            changes.append(ByteChange(ref.source.value,
                document.image[ref.source.value:ref.source_range.end], encoded,
                target.owner, f"relocation reference: {ref.target.value}"))
        rewrites.append(ReferenceRewrite(ref, new_source.value,
                                        document.target_offset(ref).value, new_target.value))
    provenance = []
    for request in ordered:
        anchor = moving[request.anchor]
        allocation = destinations[request.anchor]
        span = allocation.range
        changes.append(ByteChange(span.start.value, document.image[span.start.value:span.end],
                                  bytes(buffers[request.anchor]), anchor.owner,
                                  f"relocation payload: {request.anchor.value}"))
        provenance.append(RelocationProvenance(request.anchor.value, anchor.owner, anchor.range,
            span, anchor.alignment, allocation.free_region_evidence,
            tuple(r for r in rewrites if r.reference.target == request.anchor
                  or anchor.range.contains(r.reference.source))))
    plan = plan_changes(document.image, changes, profile_id=document.profile.id,
                        base_sha256=document.profile.sha256, relocations=tuple(provenance))
    output = apply_plan(document.image, plan)
    proposed = RomDocument(output, document.profile, anchors, tuple(references),
                          tuple(OwnedRegion(a.range, a.owner) for a in moving.values()))
    proposed.validate()
    for anchor in moving.values():
        span = anchor.range
        if output[span.start.value:span.end] != document.image[span.start.value:span.end]:
            raise LayoutError("relocation modified an old region")
    for allocation in allocations:
        anchor = proposed.anchor(allocation.request.anchor)
        if anchor.range != allocation.range or anchor.owner != allocation.request.owner:
            raise LayoutError("destination ownership mismatch")
    return RelocationResult(proposed, plan, allocations)


def emit_relocation(document: RomDocument, requests: Iterable[RelocationRequest],
                    base_path: str | Path, output_path: str | Path, *,
                    manifest_path: str | Path | None = None) -> WriteManifest:
    """Validate the entire transaction before calling the sole file writer."""
    result = plan_relocation(document, requests)
    return emit_image(base_path, output_path, result.plan, manifest_path=manifest_path)
