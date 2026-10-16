"""Pure physical layout contracts, without semantic record-layout knowledge."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .binary import FileOffset, GbaRomAddress


class LayoutError(ValueError):
    """A layout or graph cannot be justified against its image."""


def require_name(value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise LayoutError("identity, owner and provenance must be non-empty strings")


def check_alignment(value: int) -> None:
    if type(value) is not int or value <= 0 or value & (value - 1):
        raise LayoutError("alignment must be a positive power of two")


@dataclass(frozen=True, slots=True, order=True)
class AnchorId:
    value: str

    def __post_init__(self) -> None:
        require_name(self.value)


@dataclass(frozen=True, slots=True)
class RomRange:
    start: FileOffset
    size: int

    def __post_init__(self) -> None:
        if not isinstance(self.start, FileOffset):
            raise LayoutError("range requires a typed file offset")
        if type(self.size) is not int or self.size <= 0:
            raise LayoutError("range size must be positive")

    @property
    def end(self) -> int:
        return self.start.value + self.size

    def contains(self, offset: FileOffset) -> bool:
        return self.start.value <= offset.value < self.end

    def overlaps(self, other: RomRange) -> bool:
        return self.start.value < other.end and other.start.value < self.end

    def validate(self, image_size: int) -> None:
        if self.end > image_size:
            raise LayoutError(f"range {self.to_json()} out of bounds ({image_size})")

    def to_json(self) -> dict:
        return {"file_offset": self.start.value, "size": self.size}


@dataclass(frozen=True, slots=True)
class Provenance:
    profile_id: str
    base_sha256: str
    evidence: str

    def __post_init__(self) -> None:
        for value in (self.profile_id, self.base_sha256, self.evidence):
            require_name(value)

    def to_json(self) -> dict:
        return {"profile_id": self.profile_id, "base_sha256": self.base_sha256,
                "evidence": self.evidence}


@dataclass(frozen=True, slots=True)
class OwnedRegion:
    range: RomRange
    owner: str

    def __post_init__(self) -> None:
        require_name(self.owner)


@dataclass(frozen=True, slots=True)
class Anchor:
    identity: AnchorId
    range: RomRange
    kind: str
    owner: str
    alignment: int
    relocatable: bool
    provenance: Provenance

    def __post_init__(self) -> None:
        if not isinstance(self.identity, AnchorId):
            raise LayoutError("anchor requires a logical AnchorId")
        require_name(self.kind)
        require_name(self.owner)
        check_alignment(self.alignment)
        if self.range.start.value % self.alignment:
            raise LayoutError("anchor range violates alignment")
        if type(self.relocatable) is not bool:
            raise LayoutError("relocatable must be boolean")

    def to_json(self) -> dict:
        return {"anchor": self.identity.value, "range": self.range.to_json(),
                "kind": self.kind, "owner": self.owner, "alignment": self.alignment,
                "relocatable": self.relocatable, "provenance": self.provenance.to_json()}


class ReferenceClass(str, Enum):
    DECLARED_REFERENCE = "DECLARED_REFERENCE"
    CONFIRMED_REFERENCE = "CONFIRMED_REFERENCE"
    CANDIDATE_REFERENCE = "CANDIDATE_REFERENCE"


class ReferenceEncoding(str, Enum):
    """Explicit wire forms. Relative form is signed displacement FROM source.

    No Thumb masking, pointer normalization or game-specific interpretation.
    New encodings must supply both checked encode and decode branches here.
    """

    ABSOLUTE_ROM_U32_LE = "absolute_rom_u32_le"
    RELATIVE_I32_LE = "relative_i32_le"
    INDEX_U32_LE = "index_u32_le"
    INDEX_U8 = "index_u8"

    @property
    def width(self) -> int:
        return 1 if self is ReferenceEncoding.INDEX_U8 else 4

    def decode(self, data: bytes, source: FileOffset, image_size: int) -> FileOffset:
        if self in (ReferenceEncoding.INDEX_U32_LE, ReferenceEncoding.INDEX_U8):
            raise LayoutError("indexed references require their declared table context")
        if len(data) != self.width:
            raise LayoutError("malformed reference width")
        if self is ReferenceEncoding.ABSOLUTE_ROM_U32_LE:
            return FileOffset(GbaRomAddress(int.from_bytes(data, "little")).to_file_offset(image_size))
        target = source.value + int.from_bytes(data, "little", signed=True)
        if not 0 <= target < image_size:
            raise LayoutError("relative reference target out of bounds")
        return FileOffset(target)

    def encode(self, target: FileOffset, source: FileOffset, image_size: int) -> bytes:
        if self in (ReferenceEncoding.INDEX_U32_LE, ReferenceEncoding.INDEX_U8):
            raise LayoutError("indexed references are read-only; reassignment is not verified")
        RomRange(source, self.width).validate(image_size)
        RomRange(target, 1).validate(image_size)
        if self is ReferenceEncoding.ABSOLUTE_ROM_U32_LE:
            return target.to_gba_address(image_size).raw.to_bytes(4, "little")
        displacement = target.value - source.value
        if not -(1 << 31) <= displacement < (1 << 31):
            raise LayoutError("relative reference encoding overflow")
        return displacement.to_bytes(4, "little", signed=True)


@dataclass(frozen=True, slots=True)
class Reference:
    source: FileOffset
    target: AnchorId
    target_delta: int
    encoding: ReferenceEncoding
    classification: ReferenceClass
    provenance: Provenance
    index_base: FileOffset | None = None
    index_stride: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source, FileOffset) or not isinstance(self.target, AnchorId):
            raise LayoutError("reference requires typed source and anchor identity")
        if type(self.target_delta) is not int or self.target_delta < 0:
            raise LayoutError("reference target delta must be non-negative")
        if not isinstance(self.encoding, ReferenceEncoding):
            raise LayoutError("unsupported reference encoding")
        if not isinstance(self.classification, ReferenceClass):
            raise LayoutError("unsupported reference classification")
        if self.encoding in (ReferenceEncoding.INDEX_U32_LE, ReferenceEncoding.INDEX_U8):
            if (not isinstance(self.index_base, FileOffset)
                    or type(self.index_stride) is not int or self.index_stride <= 0):
                raise LayoutError("indexed reference requires a table base and positive stride")
        elif self.index_base is not None or self.index_stride is not None:
            raise LayoutError("index context on a non-index reference")

    def decode_target(self, data: bytes, image_size: int) -> FileOffset:
        if self.encoding not in (ReferenceEncoding.INDEX_U32_LE, ReferenceEncoding.INDEX_U8):
            return self.encoding.decode(data, self.source, image_size)
        if len(data) != self.encoding.width:
            raise LayoutError("malformed index width")
        assert self.index_base is not None and self.index_stride is not None
        target = self.index_base.value + int.from_bytes(data, "little") * self.index_stride
        RomRange(FileOffset(target), 1).validate(image_size)
        return FileOffset(target)

    @property
    def source_range(self) -> RomRange:
        return RomRange(self.source, self.encoding.width)

    def to_json(self) -> dict:
        result = {"source_file_offset": self.source.value, "target_anchor": self.target.value,
                "target_delta": self.target_delta, "encoding": self.encoding.value,
                "classification": self.classification.value,
                "provenance": self.provenance.to_json()}
        if self.index_base is not None:
            result.update(index_base_file_offset=self.index_base.value, index_stride=self.index_stride)
        return result


@dataclass(frozen=True, slots=True)
class FreeRegion:
    """Trusted profile declaration; never inferred from byte fill patterns."""

    range: RomRange
    evidence: str

    def __post_init__(self) -> None:
        require_name(self.evidence)


#: TOOLKIT-026: anchor kinds whose relocation safety this toolkit can decide from
#: the reference graph alone. A kind is listed here only once a ticket has proven
#: that moving one of its anchors requires rewriting nothing except the references
#: the graph already carries - for `placement_reference_array`, TOOLKIT-024 proved
#: the engine reaches the array through exactly two fields (`MapEntry+0x14` for the
#: base, `MapEntry+0x04` for the count) with no sentinel, terminator or suffix, so
#: the array's whole inbound surface is expressible as references.
#:
#: TOOLKIT-036 added `text-string` on the same bar. A string body's whole inbound
#: surface is its pointer-table slot: the engine reaches a string by index through
#: that table and never by a direct pointer, and the canonical image was scanned
#: word-aligned for every body address to confirm it. That scan is what makes the
#: kind admissible, and `webfoot.text` still proves it PER ENTRY before publishing
#: any anchor as relocatable - the five canonical bodies a second aligned word also
#: names are refused by their measured inbound count.
#:
#: GRAPHICS-IMPORT-BOUNDARY-001 added `graphics_container`, and it is the first
#: kind admitted on a *structural* argument rather than a verified inbound scan.
#: What is established: a container is a leaf of the graph. The reference walk
#: publishes no reference sourced inside one (nothing inside a compressed payload
#: is a pointer field this toolkit decodes), so the "every reference sourced
#: inside the anchor" half of :func:`relocation_eligible` is satisfied by
#: construction, and every inbound reference is the CONFIRMED ``+0x08`` container
#: word of a specific 12-byte piece record, published by
#: `webfoot.graphics.ActorSprites.reference_document`.
#:
#: What is NOT established, and must not be implied by membership here: that the
#: published piece set is the COMPLETE set of words in the image that name this
#: payload. A word-aligned scan for a graphics container's address has not been
#: run, so an undiscovered reference is possible in principle. That is why the
#: graphics relocation path keeps the original payload bytes intact rather than
#: retiring them, and why `webfoot.relocation`'s per-anchor
#: :func:`relocation_eligible` gate - not this constant - decides whether any
#: particular container may move.
#:
#: SPRITE-NEW-RUNTIME-001 adds `character_pointer_table`, and it is admitted on a
#: *measured* inbound scan rather than on a structural argument. What is
#: established, against the canonical image: the 297-entry actor-sprite registry
#: at ROM ``0x086B6BDC`` is reached by exactly TWO words in the whole 8 MiB image,
#: both of them Thumb literal-pool entries - file ``0x0003C0``, consumed by
#: ``ldr r1,[pc,#0x260]`` at ``0x0800015E`` in the sprite-id accessor
#: ``0x08000158``, and file ``0x01715C``, consumed by ``ldr r1,[pc,#0x1c]`` at
#: ``0x0801713E`` in the party re-entry path. A stride-4 census repeated at byte
#: alignment returns the same two, so the registry's inbound surface is closed at
#: two CONFIRMED references and no CANDIDATE reference reaches it.
#:
#: What is NOT established by membership here: that a 298-entry registry or any
#: sprite structure, animation or frame record placed above canonical EOF is
#: actually READ by the retail engine at runtime. The pointer fields can ENCODE
#: such an address - the accessor's literal is a full 32-bit word - but that is an
#: encoding claim. The mGBA run owned by SPRITE-NEW-RUNTIME-001 is the proof of
#: the runtime claim, and membership here must not be read as it.
#:
#: MAP-NEW-AUTHORING-001 adds `map_entry_table`, also on a measured scan. Against
#: the canonical image the 452-record MapEntry table at ROM ``0x0808E2E0`` is
#: reached by exactly ONE word in the whole image - file ``0x0008A58``, the
#: literal pool entry of ``ldr r1,[pc,#0x4c]`` at ``0x08008A0A`` in the key
#: lookup ``0x080089FC`` - and that lookup is the only caller of the count helper
#: ``0x080125E0``, which returns the compiled bound ``0x1C4``. A stride-4 census
#: repeated at every byte offset returns the same single word.
#:
#: What membership here does NOT establish: that the retail engine follows a
#: ``MapEntry+0x2C`` word or a root placed above canonical EOF. The field encodes
#: such an address; the mGBA run owned by MAP-NEW-AUTHORING-001 is the proof of
#: the runtime claim.
RELOCATION_ELIGIBLE_KINDS = frozenset({"placement_reference_array", "text-string",
                                       "graphics_container",
                                       "character_pointer_table",
                                       "appearance_record_table",
                                       "map_entry_table"})


def relocation_eligible(anchor: Anchor, references: Iterable[Reference]) -> bool:
    """Whether `anchor` satisfies the existing relocation safety contract.

    This is the SAME contract `relocation.plan_relocation` enforces, evaluated at
    publication time so an anchor is not marked movable on hope. An anchor is
    eligible only when every one of these holds:

      * its kind is one whose inbound surface a ticket has proven the graph fully
        expresses (`RELOCATION_ELIGIBLE_KINDS`) - an unproven kind stays fixed;
      * every inbound reference is DECLARED or CONFIRMED. One CANDIDATE reference
        is an unresolved numeric hit that `plan_relocation` would refuse anyway,
        and refusing it here keeps the flag honest rather than deferring;
      * every inbound reference targets an offset inside the anchor, so no
        reference is stranded when the extent changes;
      * every reference SOURCED inside the anchor is DECLARED or CONFIRMED and
        lies wholly within it, so the payload rewrite carries each source field
        with it instead of leaving one behind in retired bytes.

    Eligibility is decided per anchor from measured references. It never consults
    a map index, an address range, or any other hardcoded identity: an array whose
    graph does not satisfy the contract stays non-relocatable, and so does every
    anchor of an unlisted kind.
    """
    if anchor.kind not in RELOCATION_ELIGIBLE_KINDS:
        return False
    inbound = False
    for reference in references:
        if reference.target == anchor.identity:
            inbound = True
            if reference.classification is ReferenceClass.CANDIDATE_REFERENCE:
                return False
            if reference.target_delta >= anchor.range.size:
                return False
        if anchor.range.contains(reference.source):
            if reference.classification is ReferenceClass.CANDIDATE_REFERENCE:
                return False
            if reference.source_range.end > anchor.range.end:
                return False
    # An anchor nothing points at has no proven owner to rewrite, so moving it
    # would silently orphan whatever actually reaches it.
    return inbound
