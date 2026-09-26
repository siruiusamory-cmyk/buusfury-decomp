"""The ONE production allocation authority: deterministic placement from declared regions.

There is exactly one allocator in this toolkit, and this is it. Nothing else may
search for space: a second implementation is how a build silently diverges from
the capacity its profile actually declared. Research code may *measure* free space
(`tools/research/capacity_model.py`), but only a reviewed profile declaration and
an explicit expanded-storage declaration can be allocated.

Four rules shape everything below.

**The allocator never inspects bytes.** It does not scan for `FF` or `00` runs, it
does not read the structural atlas, and it does not look at the image at all. Its
input is a :class:`StorageModel` - declared regions with an evidence string each -
so "free" means "a reviewed declaration says free", never "these bytes look
empty". `FF` fill is a candidate until a ticket proves it.

**Only two classes are allocatable.** :data:`ALLOCATABLE_REGION_CLASSES` is the
single decision point: `VERIFIED_FREE` and authorized `PADDING_EXPANDED`.
`OWNED`, `REFERENCED` and `UNKNOWN` are exclusion evidence - `UNKNOWN` most of all,
because it is the class this project's own measurements could not classify.
A model whose allocatable region overlaps an exclusion region is refused at
construction rather than resolved by precedence.

**Expanded storage is not implied by a larger file.** A generated image being
bigger than the canonical ROM authorizes nothing by itself. An expanded region
enters the model only through an explicit declaration
(:meth:`StorageModel.from_profile`, which reads `profile.generated_expansion` and
its recorded evidence), only a request that states
:attr:`Addressability.EXPANDED_PERMITTED` may use one, and the resulting
:class:`Allocation` is what later authorizes the *write*
(:meth:`Allocation.generated_allocation_provenance`). No allocation record, no
expanded write.

**Determinism is a stated policy, not an accident.** :data:`ALLOCATION_POLICY`
names the version and the rule; :func:`allocate` sorts its requests by anchor
identity (a total order, and duplicate identities are refused, so there are no
ties) and takes the lowest aligned first fit. No dict, set or filesystem order is
consulted anywhere.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable, Mapping

from .binary import FileOffset
from .layout import (AnchorId, FreeRegion, LayoutError, OwnedRegion, RomRange,
                     check_alignment, require_name)
from .profile import RomProfile


class AllocationError(LayoutError):
    """A request, a region model or a placement cannot be justified."""


class InsufficientSpaceError(AllocationError):
    """No declared, allocatable region can host the request. Never truncated."""


class RegionClassError(AllocationError):
    """A region model is internally inconsistent or claims unallocatable bytes."""


#: The policy version and rule recorded on every allocation. Bump the version when
#: the rule changes, because a stored allocation was produced under one policy and
#: a rebuild under another must be visible rather than silent.
ALLOCATION_POLICY = (
    "lowest-aligned-first-fit/v2: requests ordered by anchor identity "
    "(total, no ties); each takes the lowest aligned address that fits in the "
    "first allocatable region, by ascending region start, clear of every reservation"
)


class RegionClass(str, Enum):
    """What a span of the image has been *established* to be.

    The vocabulary is the ticket's: a byte is owned by a known structure, reached
    by a known reference, declared free by review, an authorized generated-image
    pad, or none of those. There is no "probably free".
    """

    VERIFIED_FREE = "VERIFIED_FREE"
    PADDING_EXPANDED = "PADDING_EXPANDED"
    OWNED = "OWNED"
    REFERENCED = "REFERENCED"
    UNKNOWN = "UNKNOWN"


#: THE single decision point for what may be allocated. Every other part of this
#: module asks the model, and the model asks this.
ALLOCATABLE_REGION_CLASSES = frozenset({RegionClass.VERIFIED_FREE,
                                        RegionClass.PADDING_EXPANDED})


class AllocationKind(str, Enum):
    """Semantic classes of authored content that ask for storage.

    One member per allocating call site that exists today - nothing speculative.
    A caller states WHAT it is placing, never "find me N empty bytes": the kind is
    what a policy can reason about, and the addressability default that follows
    from it is the one the capacity evidence supports.
    """

    #: A packed container payload (compressed dialogue). The only domain whose
    #: pointer is engine-proven above canonical EOF.
    PACKED_STREAM = "packed_stream"
    #: An authored placement body, descriptor or script payload.
    PLACEMENT_BODY = "placement_body"
    #: The map object array that points at placement bodies.
    PLACEMENT_REFERENCE_ARRAY = "placement_reference_array"
    #: A relocated text-table entry's string body.
    TEXT_STRING = "text_string"
    #: A relocated anchor payload whose anchor kind this build does not model by
    #: name. `layout.RELOCATION_ELIGIBLE_KINDS` is the authority for what MAY be
    #: relocated and `plan_relocation` refuses anything outside it, so this covers
    #: an eligible-but-unmodelled kind - a synthetic fixture anchor, or a kind a
    #: later ticket publishes before it names a class here. It is conservative:
    #: canonical-only, exactly like the two named relocation kinds.
    RELOCATED_ANCHOR_PAYLOAD = "relocated_anchor_payload"
    #: The contiguous whole-map proposal (pointer slots plus every body). Modelled
    #: and pinned by test, but NOT issued by the production transaction, which
    #: allocates the bodies and the array separately so the array can carry the
    #: bodies' finished addresses.
    AUTHORED_MAP_EXPANSION = "authored_map_expansion"
    #: MAP-CHUNK-AUTHORING-001. One project-authored dominant chunk body: the
    #: packed container a map cell's four-byte reference points at.
    CHUNK_BODY = "chunk_body"
    #: MAP-RESIZE-AND-LAYERS-001. One relocated or project-authored dominant layer
    #: record: the header plus the chunk-pointer window a map root's layer slot
    #: points at. A dominant record carries its window inline and the bytes
    #: immediately after the window belong to the next structure, so a grid that
    #: grows cannot stay where it was and the whole record is re-emitted.
    LAYER_RECORD = "layer_record"


class Addressability(str, Enum):
    """Which storage a request's pointer/domain is allowed to reach.

    ROM-CAPACITY-AND-ALLOCATION-001 Phase A inventoried sixteen pointer domains
    and found exactly one engine-proven above canonical EOF. The default is
    therefore the conservative one, and a caller that has not proven otherwise
    cannot silently receive an expanded address.
    """

    #: The domain's pointers are not proven above canonical EOF. Layout still uses
    #: the lowest canonical address, so a canonical result is unchanged.
    CANONICAL_ONLY = "canonical_only"
    #: The domain's pointers are proven able to reach generated expanded storage.
    EXPANDED_PERMITTED = "expanded_permitted"
    #: The domain's pointers are proven above canonical EOF **and** the domain is
    #: placed there by policy rather than by first fit.
    #:
    #: MAP-RESIZE-AND-LAYERS-001 introduces it for the layer-record domain, and the
    #: reason is a property of the domain rather than a preference: a dominant layer
    #: record is ``0x18 + 4 * columns * rows`` bytes, so it grows with the authored
    #: grid, and the canonical image declares exactly one 256-byte VERIFIED_FREE
    #: region. A project may author one record per resize and per authored layer, so
    #: the domain's aggregate demand is unbounded and a policy that spent the single
    #: canonical free region on it would both exhaust it and take a resource other
    #: domains depend on. Placing the domain above EOF is additionally exactly the
    #: addressability this capability has to prove, so the policy and the proof are
    #: the same decision.
    EXPANDED_ONLY = "expanded_only"


#: The addressability each kind defaults to, from the Phase A addressability
#: matrix. Only the compressed-dialogue selector domain is proven above EOF; the
#: other kinds are canonical-only until a bounded experiment says otherwise.
#:
#: MAP-CHUNK-AUTHORING-001 adds one entry, and states its standing precisely
#: because the roadmap's rule is that *encoding-capable* is not *engine-proven*
#: and *engine-proven* is not *runtime-proven*. The dominant layer's chunk window
#: is a full 32-bit little-endian GBA address per cell - measured over all 4,274
#: cells of the canonical image, nothing masks or truncates it - so the field can
#: ENCODE an address above canonical EOF; the profile's declared expansion maps
#: file offset 0x00800000 to 0x08800000 inside the 0x08000000..0x09FFFFFF Game
#: Pak window. The domain is REQUIRED to use expansion rather than merely
#: permitted to: the canonical image declares a single 256-byte VERIFIED_FREE
#: region and a chunk container is at least 0x808 bytes, so no canonical
#: placement exists and a canonical-only request would fail closed with
#: `InsufficientSpaceError` every time. Whether the retail engine actually READS
#: a chunk above EOF is the runtime proof this ticket owns; until that proof
#: lands, capability must not be advanced on the strength of this constant.
DEFAULT_ADDRESSABILITY = {
    AllocationKind.PACKED_STREAM: Addressability.EXPANDED_PERMITTED,
    AllocationKind.PLACEMENT_BODY: Addressability.CANONICAL_ONLY,
    AllocationKind.PLACEMENT_REFERENCE_ARRAY: Addressability.CANONICAL_ONLY,
    AllocationKind.TEXT_STRING: Addressability.CANONICAL_ONLY,
    AllocationKind.RELOCATED_ANCHOR_PAYLOAD: Addressability.CANONICAL_ONLY,
    AllocationKind.AUTHORED_MAP_EXPANSION: Addressability.CANONICAL_ONLY,
    AllocationKind.CHUNK_BODY: Addressability.EXPANDED_PERMITTED,
    AllocationKind.LAYER_RECORD: Addressability.EXPANDED_ONLY,
}


@dataclass(frozen=True, slots=True)
class StorageRegion:
    """One declared span of the image, with the class it was established to be."""

    range: RomRange
    classification: RegionClass
    evidence: str
    source: str = "declaration"

    def __post_init__(self) -> None:
        if not isinstance(self.range, RomRange):
            raise RegionClassError("storage region requires a typed RomRange")
        if not isinstance(self.classification, RegionClass):
            raise RegionClassError(
                f"storage region {self.range.to_json()} has no known classification")
        require_name(self.evidence)
        require_name(self.source)

    def to_json(self) -> dict:
        return {"file_offset": self.range.start.value, "size": self.range.size,
                "end": self.range.end, "classification": self.classification.value,
                "evidence": self.evidence, "source": self.source}


@dataclass(frozen=True, slots=True)
class StorageModel:
    """The declared image the allocator may reason about. Inspected, never scanned.

    `canonical_size` and `image_size` are separate on purpose: expanded bytes are
    outside the canonical image, and a model that could not tell them apart would
    let a canonical-only request land there.

    Invariants, all enforced here because every one of them is a way an allocation
    could otherwise be handed bytes that are not free:

    * regions are sorted and pairwise disjoint, so a span has one class;
    * every region lies inside `image_size`, and a canonical region inside
      `canonical_size`;
    * the expanded region, if any, begins exactly at canonical EOF and lies wholly
      above it - the same append-only contract `write.GeneratedImage` enforces, so
      a model and a write plan cannot disagree about where expansion starts;
    * no allocatable region overlaps an exclusion region.
    """

    canonical_size: int
    image_size: int
    regions: tuple[StorageRegion, ...] = ()

    def __post_init__(self) -> None:
        if type(self.canonical_size) is not int or self.canonical_size <= 0:
            raise RegionClassError("storage model requires a positive canonical size")
        if type(self.image_size) is not int or self.image_size < self.canonical_size:
            raise RegionClassError(
                "storage model image size must include the canonical image")
        ordered = tuple(sorted(self.regions, key=lambda r: (r.range.start.value,
                                                            r.range.end)))
        object.__setattr__(self, "regions", ordered)
        for region in ordered:
            region.range.validate(self.image_size)
            if (region.classification is not RegionClass.PADDING_EXPANDED
                    and region.range.end > self.canonical_size):
                raise RegionClassError(
                    f"canonical region {region.range.to_json()} extends past canonical EOF")
            if region.classification is RegionClass.PADDING_EXPANDED:
                if region.range.start.value != self.canonical_size:
                    raise RegionClassError(
                        "generated expansion must begin at canonical EOF")
                if region.range.end > self.image_size:
                    raise RegionClassError("generated expansion exceeds the image")
        for left, right in zip(ordered, ordered[1:]):
            if left.range.overlaps(right.range):
                raise RegionClassError(
                    f"overlapping storage regions: {left.range.to_json()} and "
                    f"{right.range.to_json()}")
        allocatable = tuple(r for r in ordered if r.classification in ALLOCATABLE_REGION_CLASSES)
        for region in allocatable:
            for other in ordered:
                if other is region:
                    continue
                if region.range.overlaps(other.range):
                    raise RegionClassError(
                        f"allocatable region {region.range.to_json()} overlaps "
                        f"{other.classification.value} {other.range.to_json()}")

    # --- construction -------------------------------------------------------

    @classmethod
    def from_profile(cls, profile: RomProfile) -> "StorageModel":
        """Canonical VERIFIED_FREE plus the profile's authorized expansion.

        The expanded region is added ONLY from `profile.generated_expansion`, which
        carries the evidence a ticket recorded for it. An image that is merely
        larger than the canonical ROM produces no model entry, which is what
        "a bigger file authorizes nothing" means in practice.
        """
        regions = [
            StorageRegion(region.range, RegionClass.VERIFIED_FREE,
                          region.evidence, "profile.free_regions")
            for region in profile.free_regions
        ]
        image_size = profile.size
        expansion = profile.generated_expansion
        if expansion is not None:
            region = expansion.free_region(profile.size)
            regions.append(StorageRegion(region.range, RegionClass.PADDING_EXPANDED,
                                         region.evidence, "profile.generated_expansion"))
            image_size = expansion.output_size
        return cls(profile.size, image_size, tuple(regions))

    # --- queries ------------------------------------------------------------

    def allocatable_regions(self) -> tuple[StorageRegion, ...]:
        """The regions a request may be placed in. THE allocatability decision."""
        return tuple(r for r in self.regions
                     if r.classification in ALLOCATABLE_REGION_CLASSES)

    def classification_at(self, offset: FileOffset) -> RegionClass | None:
        for region in self.regions:
            if region.range.contains(offset):
                return region.classification
        return None

    def region_containing(self, span: RomRange) -> StorageRegion | None:
        for region in self.regions:
            if (region.range.start.value <= span.start.value
                    and span.end <= region.range.end):
                return region
        return None

    def overlapping(self, span: RomRange) -> tuple[StorageRegion, ...]:
        return tuple(r for r in self.regions if r.range.overlaps(span))

    @property
    def expanded_authorized(self) -> bool:
        return any(r.classification is RegionClass.PADDING_EXPANDED for r in self.regions)

    def to_json(self) -> dict:
        return {"canonical_size": self.canonical_size, "image_size": self.image_size,
                "expanded_authorized": self.expanded_authorized,
                "regions": [r.to_json() for r in self.regions]}


@dataclass(frozen=True, slots=True)
class AllocationRequest:
    """A semantic request for storage.

    `kind` is required and keyword-only: a caller must say what it is placing, and
    an omission is a TypeError rather than a silently permissive default. The
    older positional form `(anchor, owner, size, alignment)` still reads naturally;
    what it no longer permits is leaving the semantic class unstated.
    """

    anchor: AnchorId
    owner: str
    size: int
    alignment: int
    kind: AllocationKind = field(kw_only=True)
    addressability: Addressability | None = field(kw_only=True, default=None)
    evidence: str = field(kw_only=True, default="")
    constraints: tuple[str, ...] = field(kw_only=True, default=())

    def __post_init__(self) -> None:
        if not isinstance(self.anchor, AnchorId):
            raise AllocationError("allocation requires anchor identity")
        if not isinstance(self.kind, AllocationKind):
            raise AllocationError(
                f"{self.anchor.value}: allocation requires a semantic kind")
        require_name(self.owner)
        check_alignment(self.alignment)
        if type(self.size) is not int or self.size <= 0:
            raise AllocationError(f"{self.anchor.value}: allocation size must be positive")
        if self.addressability is None:
            object.__setattr__(self, "addressability",
                               DEFAULT_ADDRESSABILITY[self.kind])
        if not isinstance(self.addressability, Addressability):
            raise AllocationError(f"{self.anchor.value}: unsupported addressability")
        if not isinstance(self.constraints, tuple) or not all(
                isinstance(item, str) and item.strip() for item in self.constraints):
            raise AllocationError(f"{self.anchor.value}: constraints must be non-empty strings")
        if self.evidence:
            require_name(self.evidence)

    @property
    def expanded_permitted(self) -> bool:
        return self.addressability is Addressability.EXPANDED_PERMITTED


@dataclass(frozen=True, slots=True)
class Allocation:
    """One placement, with everything needed to justify, serialize and re-reserve it."""

    request: AllocationRequest
    range: RomRange
    free_region_evidence: str
    storage_class: RegionClass
    source_region: RomRange
    canonical_size: int
    image_size: int
    #: Position in the deterministic request sequence. `-1` while a placement is
    #: still provisional: `_place` finds one span without knowing the batch, and
    #: `allocate` stamps the final order on every allocation it returns.
    order: int = -1
    policy: str = ALLOCATION_POLICY

    @property
    def is_expanded(self) -> bool:
        """Whether this allocation lies outside the canonical image."""
        return self.storage_class is RegionClass.PADDING_EXPANDED

    @property
    def rom_address(self) -> int:
        return self.range.start.to_gba_address(self.image_size).raw

    def to_json(self) -> dict:
        return {
            "anchor": self.request.anchor.value,
            "kind": self.request.kind.value,
            "owner": self.request.owner,
            "size": self.range.size,
            "alignment": self.request.alignment,
            "addressability": self.request.addressability.value,
            "constraints": list(self.request.constraints),
            "request_evidence": self.request.evidence,
            # `range` is the existing typed-span spelling this record has always
            # published (the `relocation-proof` CLI contract reads it); the flat
            # fields beside it are the same numbers, stated once each.
            "range": self.range.to_json(),
            "file_offset": self.range.start.value,
            "end": self.range.end,
            "rom_address": self.rom_address,
            "rom_address_hex": f"0x{self.rom_address:08X}",
            "storage_class": self.storage_class.value,
            "source_region": {"file_offset": self.source_region.start.value,
                              "size": self.source_region.size},
            "canonical_size": self.canonical_size,
            "image_size": self.image_size,
            "expanded": self.is_expanded,
            "free_region_evidence": self.free_region_evidence,
            "order": self.order,
            "policy": self.policy,
        }

    def generated_allocation_provenance(self, *, domain: str, resource: str,
                                        pointer_offset: int,
                                        source_range: RomRange):
        """The write-layer authorization for this span, or fail closed.

        This is the ONLY way an expanded span acquires permission to be written:
        `write.plan_changes` refuses an appended change that no
        `GeneratedAllocationProvenance` owns, and this builds that record from the
        allocation the allocator actually made. A canonical allocation needs no
        such authorization - it is ordinary attributed overwriting - and asking
        for one is refused rather than silently returning a span that would
        authorize bytes outside the declared expansion.
        """
        from .write import GeneratedAllocationProvenance

        if not self.is_expanded:
            raise AllocationError(
                f"{self.request.anchor.value}: canonical allocation needs no expansion "
                "provenance")
        return GeneratedAllocationProvenance(
            domain=domain,
            resource=resource,
            owner=self.request.owner,
            source_range=source_range,
            allocated_range=self.range,
            allocated_rom_address=self.rom_address,
            pointer_offset=pointer_offset,
            expansion_evidence=self.free_region_evidence,
        )


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


def _reservation_spans(occupied: Iterable[OwnedRegion]) -> tuple[RomRange, ...]:
    """Reservations in a deterministic order, refusing an inconsistent set.

    Overlapping reservations are refused rather than merged. Two owners claiming
    one span means at least one of them is wrong, and an allocator that quietly
    unioned them would place the next request against a map nobody agreed on.
    """
    spans = tuple(sorted((region.range for region in occupied),
                         key=lambda span: (span.start.value, span.end)))
    for left, right in zip(spans, spans[1:]):
        if left.overlaps(right):
            raise AllocationError(
                f"overlapping reservations: {left.to_json()} and {right.to_json()}")
    return spans


def _candidate_regions(storage: StorageModel,
                       request: AllocationRequest) -> tuple[StorageRegion, ...]:
    """The regions this request may use, in ascending start order.

    Addressability is applied here and nowhere else: a canonical-only request never
    sees the expanded region, so it cannot be handed an address its domain has not
    been proven able to reach.
    """
    allowed = storage.allocatable_regions()
    if request.addressability is Addressability.EXPANDED_ONLY:
        return tuple(region for region in allowed
                     if region.classification is RegionClass.PADDING_EXPANDED)
    if request.expanded_permitted:
        return allowed
    return tuple(region for region in allowed
                 if region.classification is not RegionClass.PADDING_EXPANDED)


def allocate(profile: RomProfile, requests: Iterable[AllocationRequest], *,
             storage: StorageModel | None = None,
             occupied: Iterable[OwnedRegion] = (),
             ) -> tuple[Allocation, ...]:
    """Place `requests` deterministically. No mutable allocator state, no writes.

    The input contract is explicit and complete: a resolved profile (canonical
    identity and size), a :class:`StorageModel` (the declared regions, which may be
    built from the profile or supplied whole by a test), the reservations already
    spoken for, and the requests themselves. Nothing here reads image bytes.

    Policy: see :data:`ALLOCATION_POLICY`. Requests are ordered by anchor identity,
    which is a total order and whose duplicates are refused, so the ordering has no
    ties to break. Each request takes the lowest aligned address that fits, in the
    first allocatable region that can host it, skipping any span that collides with
    a reservation. Every completed placement joins the reservation set before the
    next request is placed, so two requests in one batch cannot overlap.

    Fails closed with :class:`InsufficientSpaceError` when no placement exists. A
    request is never truncated, split or partially satisfied.
    """
    model = StorageModel.from_profile(profile) if storage is None else storage
    if model.canonical_size != profile.size:
        raise AllocationError(
            f"storage model canonical size {model.canonical_size} is not this "
            f"profile's {profile.size}")

    ordered = sorted(requests, key=lambda request: request.anchor)
    if len({request.anchor for request in ordered}) != len(ordered):
        raise AllocationError("duplicate allocation request")
    reserved = _reservation_spans(occupied)

    result = []
    for order, request in enumerate(ordered):
        selected = _place(model, request, reserved)
        if selected is None:
            raise InsufficientSpaceError(
                f"insufficient declared free space for {request.anchor.value} "
                f"({request.size} bytes, alignment {request.alignment}, "
                f"{request.kind.value}, {request.addressability.value})")
        allocation = selected
        reserved = tuple(sorted((*reserved, allocation.range),
                                key=lambda span: (span.start.value, span.end)))
        result.append(replace(allocation, order=order))
    return tuple(result)


def _place(model: StorageModel, request: AllocationRequest,
           reserved: tuple[RomRange, ...]) -> Allocation | None:
    """Lowest aligned first fit for one request, or None. Pure."""
    for region in _candidate_regions(model, request):
        position = region.range.start.value
        while position + request.size <= region.range.end:
            position = ((position + request.alignment - 1) // request.alignment) \
                * request.alignment
            trial = RomRange(FileOffset(position), request.size)
            if trial.end > region.range.end:
                break
            collision = next((span for span in reserved if trial.overlaps(span)), None)
            if collision is not None:
                position = collision.end
                continue
            return Allocation(request=request, range=trial,
                              free_region_evidence=region.evidence,
                              storage_class=region.classification,
                              source_region=region.range,
                              canonical_size=model.canonical_size,
                              image_size=model.image_size)
    return None


# --- reservations from provenance -------------------------------------------


def _span_from_json(value: Mapping) -> RomRange:
    if not isinstance(value, Mapping):
        raise AllocationError("allocation provenance names no span")
    try:
        return RomRange(FileOffset(int(value["file_offset"])), int(value["size"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise AllocationError(f"malformed allocation span: {value!r}") from exc


def reservations_from_allocations(
        allocations: Iterable[Allocation]) -> tuple[OwnedRegion, ...]:
    """The reservations a batch of allocations implies, for the next batch.

    Reopening a derivative means re-establishing what it already owns. This is the
    allocator-side half of that: the spans an earlier run placed become ordinary
    reservations, indistinguishable from any other occupied region, so the next
    allocation cannot be handed the same bytes.
    """
    regions = [OwnedRegion(allocation.range,
                           f"allocated:{allocation.request.anchor.value}")
               for allocation in allocations]
    return tuple(sorted(regions, key=lambda r: (r.range.start.value, r.range.end)))


def reservations_from_manifest(document: Mapping) -> tuple[OwnedRegion, ...]:
    """Reservations recovered from a serialized `WriteManifest` document.

    Reads the established provenance the writer already emits - the generated
    allocation spans and the relocation destinations - and turns them back into
    reservations. No second sidecar format: this is the same document
    `write.WriteManifest.dumps()` produces and `emit_image` publishes.
    """
    if not isinstance(document, Mapping):
        raise AllocationError("a manifest document is required")
    regions = []
    for entry in document.get("generated_allocations", ()) or ():
        owner = entry.get("owner") if isinstance(entry, Mapping) else None
        regions.append(OwnedRegion(_span_from_json(entry.get("allocated_range", {})),
                                   owner or "generated-allocation"))
    for entry in document.get("relocations", ()) or ():
        owner = entry.get("owner") if isinstance(entry, Mapping) else None
        regions.append(OwnedRegion(_span_from_json(entry.get("new_range", {})),
                                   owner or "relocation"))
    return tuple(sorted(regions, key=lambda r: (r.range.start.value, r.range.end)))
