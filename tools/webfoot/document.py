"""Verified immutable ROM document and reference graph. No filesystem access."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from .binary import BinaryAddressError, FileOffset
from .gba_header import GbaHeader, HEADER_SIZE
from .hashing import hash_stream
from .layout import (Anchor, AnchorId, LayoutError, OwnedRegion, Provenance,
                     Reference, ReferenceClass, ReferenceEncoding, RomRange)
from .profile import RomProfile, RomProfileCatalog, VerificationStatus


@dataclass(frozen=True, slots=True)
class RomDocument:
    image: bytes
    profile: RomProfile
    anchors: tuple[Anchor, ...]
    references: tuple[Reference, ...]
    retired: tuple[OwnedRegion, ...] = ()

    @classmethod
    def from_bytes(cls, image: bytes, profile: RomProfile, *,
                   anchors: tuple[Anchor, ...] = (),
                   references: tuple[Reference, ...] = ()) -> RomDocument:
        """Match all configured identity fields BEFORE accessing the layout."""
        image = bytes(image)
        hashes, header = hash_stream(BytesIO(image), prefix_size=HEADER_SIZE)
        match = RomProfileCatalog([profile]).match(
            size=len(image), hashes=hashes, header=GbaHeader.from_bytes(header))
        if match.status is not VerificationStatus.VERIFIED:
            raise LayoutError(f"wrong ROM/profile: {match.reason}; {match.mismatches}")
        doc = cls(image, profile, tuple(anchors), tuple(references))
        doc.validate()
        # Initial declarations must not call existing content or reference words free.
        occupied = [a.range for a in doc.anchors] + [r.source_range for r in doc.references]
        if any(f.range.overlaps(r) for f in profile.free_regions for r in occupied):
            raise LayoutError("profile free region overlaps existing content/reference")
        return doc

    def anchor(self, identity: AnchorId) -> Anchor:
        for anchor in self.anchors:
            if anchor.identity == identity:
                return anchor
        raise LayoutError(f"unknown anchor {identity}")

    def target_offset(self, reference: Reference) -> FileOffset:
        anchor = self.anchor(reference.target)
        if reference.target_delta >= anchor.range.size:
            raise LayoutError(f"reference at 0x{reference.source.value:08X} target outside anchor")
        return FileOffset(anchor.range.start.value + reference.target_delta)

    def inbound(self, target: AnchorId | RomRange) -> tuple[Reference, ...]:
        """Reverse index view, stable by source, including interior targets."""
        region = self.anchor(target).range if isinstance(target, AnchorId) else target
        return tuple(sorted((r for r in self.references if region.contains(self.target_offset(r))),
                            key=lambda r: r.source.value))

    def _check_provenance(self, provenance: Provenance) -> None:
        if (provenance.profile_id, provenance.base_sha256) != (self.profile.id, self.profile.sha256):
            raise LayoutError("wrong profile provenance")

    def validate(self) -> None:
        if type(self.image) is not bytes or len(self.image) != self.profile.size:
            raise LayoutError("document requires immutable, fixed-size image bytes")
        if len({a.identity for a in self.anchors}) != len(self.anchors):
            raise LayoutError("duplicate anchor identity")
        regions = [OwnedRegion(a.range, a.owner) for a in self.anchors] + list(self.retired)
        for region in regions:
            region.range.validate(len(self.image))
        ordered = sorted(regions, key=lambda r: r.range.start.value)
        for left, right in zip(ordered, ordered[1:]):
            if left.range.overlaps(right.range):
                raise LayoutError(f"overlapping ownership: {left.owner}, {right.owner}")
        free = sorted(self.profile.free_regions, key=lambda f: f.range.start.value)
        for region in free:
            region.range.validate(len(self.image))
        if any(a.range.overlaps(b.range) for a, b in zip(free, free[1:])):
            raise LayoutError("overlapping profile free regions")
        for anchor in self.anchors:
            self._check_provenance(anchor.provenance)
            if anchor.range.start.value % anchor.alignment:
                raise LayoutError("anchor alignment violation")
        refs = sorted(self.references, key=lambda r: r.source.value)
        for previous, current in zip(refs, refs[1:]):
            if previous.source_range.overlaps(current.source_range):
                raise LayoutError("overlapping reference source fields")
        for ref in refs:
            self._check_provenance(ref.provenance)
            ref.source_range.validate(len(self.image))
            for anchor in self.anchors:
                if ref.source_range.overlaps(anchor.range) and not (
                    anchor.range.contains(ref.source) and ref.source_range.end <= anchor.range.end
                ):
                    raise LayoutError("reference field straddles anchor boundary")
            expected = self.target_offset(ref)
            raw = self.image[ref.source.value:ref.source_range.end]
            try:
                actual = ref.encoding.decode(raw, ref.source, len(self.image))
            except (ValueError, BinaryAddressError) as exc:
                raise LayoutError(f"malformed reference at 0x{ref.source.value:08X}: {exc}") from exc
            if actual != expected:
                raise LayoutError(f"malformed reference at 0x{ref.source.value:08X}: target mismatch")

    def to_json(self) -> dict:
        return {"profile_id": self.profile.id,
                "anchors": [a.to_json() for a in sorted(self.anchors, key=lambda a: a.identity)],
                "references": [r.to_json() for r in sorted(self.references, key=lambda r: r.source)],
                "retired": [{"range": r.range.to_json(), "owner": r.owner} for r in self.retired]}


def scan_pointer_candidates(document: RomDocument, scan_range: RomRange, *, stride: int = 4) -> tuple[Reference, ...]:
    """Bounded absolute-u32 numeric scan only; known source fields are excluded.

    This is not complete reference discovery. It confers no relocation authority.
    Callers must add returned candidates to the document to apply the safety gate.
    """
    document.validate()
    scan_range.validate(len(document.image))
    if type(stride) is not int or stride <= 0:
        raise LayoutError("scan stride must be positive")
    found = []
    encoding = ReferenceEncoding.ABSOLUTE_ROM_U32_LE
    for position in range(scan_range.start.value, scan_range.end - encoding.width + 1, stride):
        source = FileOffset(position)
        if any(RomRange(source, 4).overlaps(r.source_range) for r in document.references):
            continue
        try:
            target = encoding.decode(document.image[position:position + 4], source, len(document.image))
        except ValueError:
            continue
        for anchor in document.anchors:
            if anchor.range.contains(target):
                found.append(Reference(source, anchor.identity, target.value - anchor.range.start.value,
                    encoding, ReferenceClass.CANDIDATE_REFERENCE,
                    Provenance(document.profile.id, document.profile.sha256,
                               "numeric absolute-u32 scan; semantics UNKNOWN")))
    return tuple(found)
