"""Atomic anchor relocation, compiled into the existing attributed write path."""

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

from .allocation import (Addressability, Allocation, AllocationKind, AllocationRequest,
                         allocate)
from .binary import FileOffset
from .document import RomDocument
from .layout import AnchorId, LayoutError, OwnedRegion, ReferenceClass, RomRange
from .write import (ByteChange, GeneratedAllocationProvenance, ReferenceRewrite,
                    RelocationProvenance, WriteManifest, WritePlan, apply_plan,
                    emit_image, plan_changes)


#: Which semantic allocation kind a relocatable anchor kind asks for. The
#: production eligible kinds are named; anything else that `plan_relocation` may
#: legitimately move - a synthetic fixture anchor, or a kind a later ticket
#: publishes before it names a class here - is recorded as the conservative
#: generic relocation kind. The fallback is canonical-only, so an unmodelled kind
#: can never acquire expanded storage by being unmodelled.
#:
#: GRAPHICS-IMPORT-BOUNDARY-001 made `graphics_container` eligible and names its
#: kind here too, even though the graphics domain plans through its own
#: materializer rather than through `plan_relocation` (that path encodes a
#: reference against the canonical image size, which cannot express a placement
#: above canonical EOF). The entry is what keeps the shared path honest if a
#: graphics anchor is ever handed to it: without it, the anchor would quietly
#: become a canonical-only `RELOCATED_ANCHOR_PAYLOAD` and its payload would be
#: refused rather than placed where this domain actually puts it.
_ALLOCATION_KIND = {
    "placement_reference_array": AllocationKind.PLACEMENT_REFERENCE_ARRAY,
    "text-string": AllocationKind.TEXT_STRING,
    "graphics_container": AllocationKind.GRAPHICS_CONTAINER,
    #: SPRITE-NEW-RUNTIME-001. Without this entry a moved registry would fall
    #: through to the canonical-only `RELOCATED_ANCHOR_PAYLOAD` default and be
    #: refused for want of canonical free space rather than placed where its
    #: domain actually puts it - the same trap the `graphics_container` entry
    #: above exists to avoid.
    "character_pointer_table": AllocationKind.SPRITE_IDENTITY_RECORD,
    #: APPEARANCE-AUTHORING-GATE-001. The appearance-definition table plans
    #: through its own materializer for the same reason the registry does, and
    #: this entry exists for the same reason: without it a moved table would fall
    #: through to the canonical-only default and be refused for want of canonical
    #: free space rather than placed where its domain actually puts it.
    "appearance_record_table": AllocationKind.APPEARANCE_RECORD_TABLE,
    #: MAP-NEW-AUTHORING-001. The MapEntry table plans through its own
    #: materializer, and this entry exists for the same reason the appearance one
    #: does: without it a moved table would fall through to the canonical-only
    #: default and be refused for want of canonical free space rather than placed
    #: where its domain actually puts it.
    "map_entry_table": AllocationKind.MAP_ENTRY_TABLE,
}


def _allocation_kind(anchor) -> AllocationKind:
    return _ALLOCATION_KIND.get(anchor.kind, AllocationKind.RELOCATED_ANCHOR_PAYLOAD)


class CandidateReferenceError(LayoutError):
    pass


@dataclass(frozen=True, slots=True)
class RelocationRequest:
    """One moved anchor: its logical identity and its complete new payload.

    ``payload`` is not required to be the anchor's current size. A payload larger
    than the anchor is the growth case, and it is the reason the placement can
    land above canonical EOF: a re-encoded container that outgrows its original
    extent has nowhere inside the image to go.

    ``generated`` is the authorization for exactly that placement.
    ``Addressability.EXPANDED_PERMITTED`` is a property of the KIND, so the
    allocator will offer an above-EOF span to any kind that carries it; encoding a
    pointer at an address the canonical image cannot express is a separate
    decision, and a caller makes it by naming the generated-output provenance that
    authorizes the span. Without it an expanded anchor is refused rather than
    written at an address no plan records.

    ``addressability`` overrides what the anchor's kind asks for; a caller that
    leaves it unset gets the kind's own default, which is where the domain
    argument for canonical-only or expanded-permitted storage already lives.
    """

    anchor: AnchorId
    payload: bytes
    addressability: Addressability | None = None
    generated: tuple[str, str, int] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.anchor, AnchorId):
            raise LayoutError("relocation requires logical anchor identity")
        if type(self.payload) is not bytes or not self.payload:
            raise LayoutError("relocation requires nonempty immutable payload bytes")
        if self.addressability is not None and not isinstance(
                self.addressability, Addressability):
            raise LayoutError("relocation addressability must be an Addressability")
        if self.generated is None:
            return
        if (not isinstance(self.generated, tuple) or len(self.generated) != 3
                or not all(isinstance(part, str) and part.strip()
                           for part in self.generated[:2])
                or type(self.generated[2]) is not int or self.generated[2] < 0):
            raise LayoutError(
                "generated allocation authorization requires (domain, resource, "
                "pointer_offset)")


@dataclass(frozen=True, slots=True)
class RelocationResult:
    document: RomDocument
    plan: WritePlan
    allocations: tuple[Allocation, ...]

    def generated_image(self):
        """The write-layer image policy this batch needs, or None.

        ``plan`` already carries it, so this is the one derivation both the write
        path and a caller that wants to inspect or emit the grown image read.
        """
        return self.plan.generated_image

    def to_json(self) -> dict:
        from hashlib import sha256
        # An expanded batch publishes a grown image, not the canonical one, so the
        # manifest's output block describes the artefact the plan would emit.
        output = (self.plan.generated_image.materialize(self.document.image)
                  if self.plan.generated_image is not None else self.document.image)
        manifest = WriteManifest(self.plan.base_profile_id, self.plan.base_sha256,
            sha256(output).hexdigest(), len(output),
            self.plan.effective_changes, relocations=self.plan.relocations,
            generated_image=self.plan.generated_image,
            generated_allocations=self.plan.generated_allocations)
        return {"document": self.document.to_json(),
                "allocations": [a.to_json() for a in self.allocations],
                "manifest": manifest.to_json()}


def plan_relocation(document: RomDocument, requests: Iterable[RelocationRequest], *,
                    reserved: Iterable[OwnedRegion] = ()) -> RelocationResult:
    """One batch against the verified base; no writes or mutable state on failure.

    Source fields within moved anchors follow their anchors. Interior target
    deltas are preserved. Old source fields within retired content stay intact.
    A result document describes output; it is not a new trusted base profile.

    ``reserved`` are spans earlier domains of the same build already took. They
    are ordinary occupied regions: the batch cannot be handed bytes another
    domain has spoken for, and passing them is how several domains share one
    allocation decision instead of each planning against a blank map.
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
    occupied.extend(reserved)
    allocations = allocate(document.profile,
        [AllocationRequest(r.anchor, moving[r.anchor].owner, len(r.payload),
                           moving[r.anchor].alignment,
                           kind=_allocation_kind(moving[r.anchor]),
                           addressability=r.addressability,
                           evidence=(f"relocated {moving[r.anchor].kind} anchor"
                                     if r.generated is None else
                                     f"relocated {moving[r.anchor].kind} anchor, "
                                     f"generated by {r.generated[0]}"))
         for r in ordered], occupied=occupied)
    destinations = {a.request.anchor: a for a in allocations}
    for request in ordered:
        allocation = destinations[request.anchor]
        if allocation.is_expanded and request.generated is None:
            raise LayoutError(
                f"{request.anchor.value}: the allocator placed this payload above "
                "canonical EOF, but the request names no generated allocation "
                "authorization, so no plan could record the address it was "
                "written at")
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
        # The old target is read from the SOURCE graph. `document.target_offset`
        # would be right for a target that did not move, but it resolves the moved
        # anchor's original range against a reference whose source already points
        # at the destination, which reports a stale offset for any batch that moves
        # a relative reference's own anchor.
        old_target = FileOffset(document.anchor(ref.target).range.start.value
                                + ref.target_delta)
        # The bound is the image the placement was authorized against: an
        # above-EOF anchor is only encodable at the generated image's declared
        # size, which is what the allocator issued. Encoding against the canonical
        # size would refuse every expanded placement, which is exactly what the
        # shared path did before this batch could name its expansion. The bound is
        # read from whichever end of the reference moved; a reference that moved
        # WITH its own anchor but targets an anchor that stayed has no destination
        # entry to read.
        bound = destinations[source_anchor.identity].image_size if source_moved \
            else destinations[ref.target].image_size
        encoded = ref.encoding.encode(new_target, new_source, bound)
        if source_moved:
            buffers[source_anchor.identity][delta:delta + ref.encoding.width] = encoded
        else:
            changes.append(ByteChange(ref.source.value,
                document.image[ref.source.value:ref.source_range.end], encoded,
                target.owner, f"relocation reference: {ref.target.value}"))
        rewrites.append(ReferenceRewrite(ref, new_source.value,
                                        old_target.value, new_target.value))
    provenance = []
    generated = []
    expansion = document.profile.generated_expansion
    for request in ordered:
        anchor = moving[request.anchor]
        allocation = destinations[request.anchor]
        span = allocation.range
        # Above canonical EOF there are no source bytes to preserve: the span is
        # synthesized from the profile's own padding declaration, and the plan
        # refuses these bytes if the padding does not match.
        old = (bytes([expansion.padding_byte]) * span.size if allocation.is_expanded
               else document.image[span.start.value:span.end])
        changes.append(ByteChange(span.start.value, old,
                                  bytes(buffers[request.anchor]), anchor.owner,
                                  f"relocation payload: {request.anchor.value}"))
        references_rewritten = tuple(r for r in rewrites if r.reference.target == request.anchor
                                     or anchor.range.contains(r.reference.source))
        provenance.append(RelocationProvenance(request.anchor.value, anchor.owner, anchor.range,
            span, anchor.alignment, allocation.free_region_evidence, references_rewritten))
        if allocation.is_expanded:
            if expansion is None:
                raise LayoutError(
                    "profile declares no generated expansion to authorize this batch")
            domain, resource, _ = request.generated
            generated.append(allocation.generated_allocation_provenance(
                domain=domain, resource=resource,
                pointer_offset=min(r.new_source_file_offset for r in references_rewritten),
                source_range=anchor.range))
    expanded = tuple(a.allocated_range for a in generated)
    generated_image = (expansion.generated_image(document.profile.size, expanded)
                       if expanded else None)
    plan = plan_changes(document.image, changes, profile_id=document.profile.id,
                        base_sha256=document.profile.sha256, relocations=tuple(provenance),
                        generated_image=generated_image,
                        generated_allocations=tuple(generated))
    # A grown batch's output document is the generated image WITH the changes
    # applied: an expanded destination does not exist in the canonical bytes at
    # all. `plan_changes` already validated every change against that image, so
    # this is the same materialize-then-overwrite `apply_plan` performs.
    output = apply_plan(document.image, plan)
    if generated_image is not None:
        grown = bytearray(generated_image.materialize(document.image))
        for change in plan.changes:
            grown[change.offset:change.end] = change.new
        output = bytes(grown)
    # `RomDocument.validate` ties the image length to the profile's measured
    # canonical size. The generated image is deliberately longer, so the proposed
    # document states that size; the canonical identity was already re-verified
    # against the profile above, and a generated image is not a new trusted base.
    proposed = RomDocument(output,
                           document.profile if len(output) == document.profile.size
                           else replace(document.profile, size=len(output)),
                           anchors, tuple(references),
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
