"""The one production allocation authority: 'free' means a reviewed declaration says free, never that these bytes look empty."""
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


ALLOCATION_POLICY = (
    "lowest-aligned-first-fit/v2: requests ordered by anchor identity "
    "(total, no ties); each takes the lowest aligned address that fits in the "
    "first allocatable region, by ascending region start, clear of every reservation"
)


class RegionClass(str, Enum):

    VERIFIED_FREE = "VERIFIED_FREE"
    PADDING_EXPANDED = "PADDING_EXPANDED"
    OWNED = "OWNED"
    REFERENCED = "REFERENCED"
    UNKNOWN = "UNKNOWN"


ALLOCATABLE_REGION_CLASSES = frozenset({RegionClass.VERIFIED_FREE,
                                        RegionClass.PADDING_EXPANDED})


class AllocationKind(str, Enum):

    PACKED_STREAM = "packed_stream"
    PLACEMENT_BODY = "placement_body"
    PLACEMENT_REFERENCE_ARRAY = "placement_reference_array"
    TEXT_STRING = "text_string"
    RELOCATED_ANCHOR_PAYLOAD = "relocated_anchor_payload"
    AUTHORED_MAP_EXPANSION = "authored_map_expansion"
    CHUNK_BODY = "chunk_body"
    LAYER_RECORD = "layer_record"
    TRANSITION_RECORD = "transition_record"
    TRANSITION_POINTER_ARRAY = "transition_pointer_array"
    GRAPHICS_CONTAINER = "graphics_container"
    SPRITE_IDENTITY_RECORD = "sprite_identity_record"
    MAP_OBJECT_RECORD = "map_object_record"
    APPEARANCE_RECORD_TABLE = "appearance_record_table"
    #: the engine's key lookup `0x080089FC` walks `base + 0x38 * i` below a count
    #: it reads from `0x080125E0`, and the byte after the last canonical record is
    #: a live tileset container, so a 453rd row has nowhere canonical to go. The
    #: canonical records are copied verbatim and the one literal-pool word that
    #: names the table is repointed, so the 452 existing rows move as one
    #: indivisible placement.
    MAP_ENTRY_TABLE = "map_entry_table"
    MAP_ROOT_RECORD = "map_root_record"


class Addressability(str, Enum):

    CANONICAL_ONLY = "canonical_only"
    EXPANDED_PERMITTED = "expanded_permitted"
    EXPANDED_ONLY = "expanded_only"


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
#: MAP-WARP-CREATE-PROJECT-001 adds the two transition-creation entries, both
#: `EXPANDED_ONLY`, and states their standing with the same split the two entries
#: above use. What is measured: a map root's ``+0x44`` word and every array element
#: are full 32-bit little-endian GBA addresses over all 452 roots and all 735
#: elements of the canonical image, nothing masks or truncates them, and the
#: profile's expansion maps file offset 0x00800000 to 0x08800000 inside the
#: 0x08000000..0x09FFFFFF Game Pak window - so both fields can ENCODE a record and
#: an array above canonical EOF. What is NOT measured here: whether the retail
#: engine actually follows ``+0x44`` and an array element above EOF at runtime;
#: a human-operated emulator run is the proof that owns that claim, and the
#: capability must not be advanced on the strength of these constants.
#: GRAPHICS-IMPORT-BOUNDARY-001 adds one entry and states both halves separately,
#: because for this domain they came apart. What IS measured: a piece's ``+0x08``
#: container word is a full 32-bit little-endian GBA address over all 11,005
#: canonical piece references - nothing masks or truncates it - so the field can
#: ENCODE an address above canonical EOF, and the profile's declared expansion maps
#: file offset 0x00800000 to 0x08800000 inside the 0x08000000..0x09FFFFFF Game Pak
#: window. What is NOT measured by this constant: whether the retail engine
#: actually decodes a container it reaches above EOF. A human-operated emulator run
#: owns that claim, and the capability must not advance on the strength of this
#: mapping alone.
# The addressability each kind defaults to, from the Phase A addressability matrix; only the compressed-dialogue selector domain is proven above EOF.
DEFAULT_ADDRESSABILITY = {
    AllocationKind.PACKED_STREAM: Addressability.EXPANDED_PERMITTED,
    AllocationKind.PLACEMENT_BODY: Addressability.CANONICAL_ONLY,
    AllocationKind.PLACEMENT_REFERENCE_ARRAY: Addressability.CANONICAL_ONLY,
    AllocationKind.TEXT_STRING: Addressability.CANONICAL_ONLY,
    AllocationKind.RELOCATED_ANCHOR_PAYLOAD: Addressability.CANONICAL_ONLY,
    AllocationKind.AUTHORED_MAP_EXPANSION: Addressability.CANONICAL_ONLY,
    AllocationKind.CHUNK_BODY: Addressability.EXPANDED_PERMITTED,
    AllocationKind.LAYER_RECORD: Addressability.EXPANDED_ONLY,
    AllocationKind.TRANSITION_RECORD: Addressability.EXPANDED_ONLY,
    AllocationKind.TRANSITION_POINTER_ARRAY: Addressability.EXPANDED_ONLY,
    AllocationKind.GRAPHICS_CONTAINER: Addressability.EXPANDED_PERMITTED,
    AllocationKind.SPRITE_IDENTITY_RECORD: Addressability.EXPANDED_ONLY,
    AllocationKind.MAP_OBJECT_RECORD: Addressability.EXPANDED_ONLY,
    AllocationKind.APPEARANCE_RECORD_TABLE: Addressability.EXPANDED_ONLY,
    AllocationKind.MAP_ENTRY_TABLE: Addressability.EXPANDED_ONLY,
    AllocationKind.MAP_ROOT_RECORD: Addressability.EXPANDED_ONLY,
}


@dataclass(frozen=True, slots=True)
class StorageRegion:

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
# A larger generated image authorizes nothing by itself; expansion enters only through the profile's declaration.
class StorageModel:
    """The declared image the allocator may reason about. Inspected, never scanned."""

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


    @classmethod
    def from_profile(cls, profile: RomProfile) -> "StorageModel":
        """Adds an expanded region only from the profile's declared generated expansion, so a file that is merely larger than the canonical ROM produces no model entry."""
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

    request: AllocationRequest
    range: RomRange
    free_region_evidence: str
    storage_class: RegionClass
    source_region: RomRange
    canonical_size: int
    image_size: int
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
        """The only way an expanded span acquires permission to be written; a canonical allocation is ordinary attributed overwriting and asking for one is refused."""
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
    """The same declared free regions minus spans already taken: subtraction only, never grown, merged or moved, so it can only ever offer less capacity than the profile declared."""
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


# Overlapping reservations are refused rather than merged, because two owners of one span means at least one is wrong.
def _reservation_spans(occupied: Iterable[OwnedRegion]) -> tuple[RomRange, ...]:
    spans = tuple(sorted((region.range for region in occupied),
                         key=lambda span: (span.start.value, span.end)))
    for left, right in zip(spans, spans[1:]):
        if left.overlaps(right):
            raise AllocationError(
                f"overlapping reservations: {left.to_json()} and {right.to_json()}")
    return spans


def _candidate_regions(storage: StorageModel,
                       request: AllocationRequest) -> tuple[StorageRegion, ...]:
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
    """Fails closed with InsufficientSpaceError and never truncates a request, since a partially satisfied request would place bytes nobody asked for."""
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




def _span_from_json(value: Mapping) -> RomRange:
    if not isinstance(value, Mapping):
        raise AllocationError("allocation provenance names no span")
    try:
        return RomRange(FileOffset(int(value["file_offset"])), int(value["size"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise AllocationError(f"malformed allocation span: {value!r}") from exc


def reservations_from_allocations(
        allocations: Iterable[Allocation]) -> tuple[OwnedRegion, ...]:
    regions = [OwnedRegion(allocation.range,
                           f"allocated:{allocation.request.anchor.value}")
               for allocation in allocations]
    return tuple(sorted(regions, key=lambda r: (r.range.start.value, r.range.end)))


def reservations_from_manifest(document: Mapping) -> tuple[OwnedRegion, ...]:
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
