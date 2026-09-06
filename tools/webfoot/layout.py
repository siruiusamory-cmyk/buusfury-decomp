"""Pure physical layout contracts, without semantic record-layout knowledge."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

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

    @property
    def width(self) -> int:
        return 4

    def decode(self, data: bytes, source: FileOffset, image_size: int) -> FileOffset:
        if len(data) != self.width:
            raise LayoutError("malformed reference width")
        if self is ReferenceEncoding.ABSOLUTE_ROM_U32_LE:
            return FileOffset(GbaRomAddress(int.from_bytes(data, "little")).to_file_offset(image_size))
        target = source.value + int.from_bytes(data, "little", signed=True)
        if not 0 <= target < image_size:
            raise LayoutError("relative reference target out of bounds")
        return FileOffset(target)

    def encode(self, target: FileOffset, source: FileOffset, image_size: int) -> bytes:
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

    def __post_init__(self) -> None:
        if not isinstance(self.source, FileOffset) or not isinstance(self.target, AnchorId):
            raise LayoutError("reference requires typed source and anchor identity")
        if type(self.target_delta) is not int or self.target_delta < 0:
            raise LayoutError("reference target delta must be non-negative")
        if not isinstance(self.encoding, ReferenceEncoding):
            raise LayoutError("unsupported reference encoding")
        if not isinstance(self.classification, ReferenceClass):
            raise LayoutError("unsupported reference classification")

    @property
    def source_range(self) -> RomRange:
        return RomRange(self.source, self.encoding.width)

    def to_json(self) -> dict:
        return {"source_file_offset": self.source.value, "target_anchor": self.target.value,
                "target_delta": self.target_delta, "encoding": self.encoding.value,
                "classification": self.classification.value,
                "provenance": self.provenance.to_json()}


@dataclass(frozen=True, slots=True)
class FreeRegion:
    """Trusted profile declaration; never inferred from byte fill patterns."""

    range: RomRange
    evidence: str

    def __post_init__(self) -> None:
        require_name(self.evidence)
