"""ROM-ATLAS-001: byte-addressable structural map of one verified ROM image.

The existing reference graph in `document` answers "what does this declared
anchor reach". The atlas answers the inverse question an investigation actually
starts from: given these exact bytes, what region contains them, what points at
them, and what is next door. It is deliberately a SEPARATE type from `Anchor`:
`RomDocument.validate` refuses overlapping ownership (document.py:87) because a
declared anchor owns its bytes, while atlas objects may nest and overlap when
the structure genuinely does. Widening `Anchor` would weaken that guarantee.

Four layers, each with a different tolerance for being wrong:

  A. `CoverageMap` - an exhaustive partition of the image. Every byte is
     accounted for exactly once, so "unclassified" is a measurable quantity
     rather than an absence.
  B. `AtlasObject` - located structures. May nest, may overlap.
  C. references - edges. `layout.Reference` where a declared anchor is the
     target; `AtlasReference` where the target is a raw offset nothing has
     claimed yet.
  D. `Observation` - noisy scanner output, capped at CANDIDATE so a heuristic
     can never promote itself into confirmed structure.

No database, no index cache: whole-image passes over this ROM cost about a
second, so the atlas lives in memory and serializes to deterministic JSONL.

`RangeIndex` (S4) is the query surface over those layers: which owners claim
these bytes, which ranges one owner claims, and how many bytes nobody owns. It
is derived from the atlas, so it is not a second partition and it has no
classification vocabulary of its own.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Iterable, Iterator

from .binary import FileOffset
from .handles import recover_handle
from .layout import (LayoutError, Provenance, Reference, ReferenceClass,
                     ReferenceEncoding, RomRange, require_name)


class AtlasError(ValueError):
    """An atlas cannot be justified against its image."""


class Confidence(str, Enum):
    """Ascending evidence strength. These do NOT collapse into each other.

    `OBSERVED` is "a pass saw this shape", `CANDIDATE` is "it survived a filter",
    `INFERRED` is INFERRED in docs/DEVELOPMENT.md, `CONFIRMED` its CONFIRMED, and
    `RUNTIME_CONFIRMED` is CONFIRMED plus a LEVEL 3+ runtime observation. Kept
    distinct because collapsing OBSERVED into CANDIDATE is exactly how a numeric
    coincidence becomes a fact.
    """

    UNKNOWN = "UNKNOWN"
    OBSERVED = "OBSERVED"
    CANDIDATE = "CANDIDATE"
    INFERRED = "INFERRED"
    CONFIRMED = "CONFIRMED"
    RUNTIME_CONFIRMED = "RUNTIME_CONFIRMED"


#: Ascending order. Compare via `strength()`; the enum deliberately has no
#: arithmetic operators, so nothing can average or add two evidence levels.
CONFIDENCE_ORDER: tuple[Confidence, ...] = (
    Confidence.UNKNOWN,
    Confidence.OBSERVED,
    Confidence.CANDIDATE,
    Confidence.INFERRED,
    Confidence.CONFIRMED,
    Confidence.RUNTIME_CONFIRMED,
)


def strength(confidence: Confidence) -> int:
    """Comparable rank of `confidence`. Higher is stronger evidence."""
    if not isinstance(confidence, Confidence):
        raise AtlasError("confidence must be a Confidence member")
    return CONFIDENCE_ORDER.index(confidence)


# Non-semantic classification vocabulary. A scanner naming a shape rather than a
# meaning uses one of these constants so two passes cannot spell the same
# unknown differently, and `unknowns()` can find them all.
UNKNOWN = "UNKNOWN"
UNKNOWN_TEXTLIKE = "UNKNOWN_TEXTLIKE"
UNKNOWN_POINTER_DENSE = "UNKNOWN_POINTER_DENSE"
UNKNOWN_STRUCTURED = "UNKNOWN_STRUCTURED"
UNKNOWN_HIGH_ENTROPY = "UNKNOWN_HIGH_ENTROPY"
UNKNOWN_EXECUTABLE_CANDIDATE = "UNKNOWN_EXECUTABLE_CANDIDATE"
UNKNOWN_COMPRESSED_CANDIDATE = "UNKNOWN_COMPRESSED_CANDIDATE"
PADDING_CANDIDATE = "PADDING_CANDIDATE"
VERIFIED_FREE = "VERIFIED_FREE"

UNKNOWN_CLASSIFICATIONS = frozenset({
    UNKNOWN,
    UNKNOWN_TEXTLIKE,
    UNKNOWN_POINTER_DENSE,
    UNKNOWN_STRUCTURED,
    UNKNOWN_HIGH_ENTROPY,
    UNKNOWN_EXECUTABLE_CANDIDATE,
    UNKNOWN_COMPRESSED_CANDIDATE,
})


def _range(start: int, size: int) -> RomRange:
    try:
        return RomRange(FileOffset(start), size)
    except (LayoutError, ValueError) as exc:
        raise AtlasError(str(exc)) from exc


def _as_range(target: FileOffset | RomRange) -> RomRange:
    if isinstance(target, RomRange):
        return target
    if isinstance(target, FileOffset):
        return RomRange(target, 1)
    raise AtlasError("expected a FileOffset or RomRange")


# --- Layer A: exhaustive coverage partition ---------------------------------


@dataclass(frozen=True, slots=True)
class CoverageSpan:
    range: RomRange
    classification: str
    confidence: Confidence
    provenance: Provenance

    def __post_init__(self) -> None:
        if not isinstance(self.range, RomRange):
            raise AtlasError("coverage span requires a typed RomRange")
        try:
            require_name(self.classification)
        except LayoutError as exc:
            raise AtlasError(f"coverage classification: {exc}") from exc
        strength(self.confidence)
        if not isinstance(self.provenance, Provenance):
            raise AtlasError("coverage span requires typed provenance")

    @property
    def _key(self) -> tuple:
        return (self.classification, self.confidence, self.provenance)

    def to_json(self) -> dict:
        return {"layer": "coverage", "file_offset": self.range.start.value,
                "size": self.range.size, "classification": self.classification,
                "confidence": self.confidence.value,
                "provenance": self.provenance.to_json()}


@dataclass(frozen=True, slots=True)
class CoverageMap:
    """Every byte of the image, classified exactly once."""

    spans: tuple[CoverageSpan, ...]
    image_size: int

    @classmethod
    def single(cls, image_size: int, classification: str, confidence: Confidence,
               provenance: Provenance) -> CoverageMap:
        """The starting state: one span covering the whole image."""
        span = CoverageSpan(_range(0, image_size), classification, confidence, provenance)
        return cls((span,), image_size)

    def validate(self) -> None:
        if type(self.image_size) is not int or self.image_size <= 0:
            raise AtlasError("coverage image size must be a positive integer")
        if not self.spans:
            raise AtlasError("coverage map has no spans")
        # Order first: the endpoint checks read spans[0] and spans[-1], which are
        # only the real endpoints once the tuple is known to be sorted.
        for left, right in zip(self.spans, self.spans[1:]):
            if left.range.start.value >= right.range.start.value:
                raise AtlasError(
                    f"coverage spans out of order at 0x{left.range.start.value:X} "
                    f"then 0x{right.range.start.value:X}")
            if left.range.end != right.range.start.value:
                kind = "gap" if left.range.end < right.range.start.value else "overlap"
                raise AtlasError(
                    f"coverage {kind} between 0x{left.range.end:X} "
                    f"and 0x{right.range.start.value:X}")
        first, last = self.spans[0], self.spans[-1]
        if first.range.start.value != 0:
            raise AtlasError(f"coverage starts at 0x{first.range.start.value:X}, expected 0x0")
        if last.range.end != self.image_size:
            raise AtlasError(
                f"coverage ends at 0x{last.range.end:X}, expected 0x{self.image_size:X}")
        total = 0
        for span in self.spans:
            total += span.range.size
        if total != self.image_size:
            raise AtlasError(
                f"coverage accounts for {total} bytes, image is {self.image_size}")

    def _starts(self) -> list[int]:
        return [span.range.start.value for span in self.spans]

    def at(self, offset: FileOffset) -> CoverageSpan:
        if not isinstance(offset, FileOffset):
            raise AtlasError("coverage lookup requires a typed FileOffset")
        if not 0 <= offset.value < self.image_size:
            raise AtlasError(f"offset 0x{offset.value:X} outside a {self.image_size}-byte image")
        index = bisect_right(self._starts(), offset.value) - 1
        return self.spans[index]

    def overlapping(self, range: RomRange) -> tuple[CoverageSpan, ...]:
        index = max(0, bisect_right(self._starts(), range.start.value) - 1)
        found = []
        for span in self.spans[index:]:
            if span.range.start.value >= range.end:
                break
            if span.range.overlaps(range):
                found.append(span)
        return tuple(found)

    def refine(self, range: RomRange, classification: str, confidence: Confidence,
               provenance: Provenance) -> CoverageMap:
        """Reclassify `range`, refusing to weaken anything already stronger.

        This refusal is the point of the whole layer: a later broad scanner must
        not be able to repaint a CONFIRMED region as UNKNOWN_HIGH_ENTROPY just
        because it ran last.
        """
        if not isinstance(range, RomRange):
            raise AtlasError("refine requires a typed RomRange")
        range.validate(self.image_size)
        incoming = strength(confidence)
        for span in self.overlapping(range):
            if strength(span.confidence) > incoming:
                raise AtlasError(
                    f"refusing to downgrade 0x{span.range.start.value:X}..0x{span.range.end:X} "
                    f"from {span.confidence.value} to {confidence.value}")
            # Freedom needs more than equal evidence to overwrite content: a
            # region is only free if NOTHING occupies it, so a span naming
            # content is evidence the incoming free claim is stale. The reverse
            # stays allowed, because that is a stale free claim being corrected.
            if (classification == VERIFIED_FREE
                    and span.classification != VERIFIED_FREE
                    and strength(span.confidence) == incoming):
                raise AtlasError(
                    f"refusing to free 0x{span.range.start.value:X}..0x{span.range.end:X} "
                    f"over {span.classification} at equal {span.confidence.value}; "
                    f"content on those bytes outranks an equal-strength {VERIFIED_FREE}")

        rebuilt: list[CoverageSpan] = []
        for span in self.spans:
            if not span.range.overlaps(range):
                rebuilt.append(span)
                continue
            start, end = span.range.start.value, span.range.end
            if start < range.start.value:
                rebuilt.append(CoverageSpan(_range(start, range.start.value - start),
                                            span.classification, span.confidence,
                                            span.provenance))
            if end > range.end:
                rebuilt.append(CoverageSpan(_range(range.end, end - range.end),
                                            span.classification, span.confidence,
                                            span.provenance))
        rebuilt.append(CoverageSpan(range, classification, confidence, provenance))
        rebuilt.sort(key=lambda s: s.range.start.value)
        refined = CoverageMap(_coalesce(rebuilt), self.image_size)
        refined.validate()
        return refined


def _coalesce(spans: Iterable[CoverageSpan]) -> tuple[CoverageSpan, ...]:
    """Merge adjacent identical spans so serialization stays canonical."""
    merged: list[CoverageSpan] = []
    for span in spans:
        if merged and merged[-1]._key == span._key and merged[-1].range.end == span.range.start.value:
            previous = merged.pop()
            span = CoverageSpan(_range(previous.range.start.value,
                                       previous.range.size + span.range.size),
                                span.classification, span.confidence, span.provenance)
        merged.append(span)
    return tuple(merged)


# --- Layer B: objects -------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasObject:
    """A located structure. Unlike an `Anchor`, may nest and may overlap."""

    identity: str
    range: RomRange
    kind: str
    confidence: Confidence
    provenance: Provenance
    attributes: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        try:
            require_name(self.identity)
            require_name(self.kind)
        except LayoutError as exc:
            raise AtlasError(f"object identity and kind: {exc}") from exc
        if not isinstance(self.range, RomRange):
            raise AtlasError("object requires a typed RomRange")
        strength(self.confidence)
        if not isinstance(self.provenance, Provenance):
            raise AtlasError("object requires typed provenance")
        if not isinstance(self.attributes, tuple) or any(
                not isinstance(pair, tuple) or len(pair) != 2
                or not isinstance(pair[0], str) or not isinstance(pair[1], str)
                for pair in self.attributes):
            raise AtlasError("object attributes must be a tuple of (str, str) pairs")
        if list(self.attributes) != sorted(self.attributes):
            raise AtlasError("object attributes must be sorted")

    def contains(self, offset: FileOffset) -> bool:
        return self.range.contains(offset)

    def overlaps(self, other: AtlasObject) -> bool:
        return self.range.overlaps(other.range)

    def to_json(self) -> dict:
        return {"layer": "object", "identity": self.identity,
                "file_offset": self.range.start.value, "size": self.range.size,
                "kind": self.kind, "confidence": self.confidence.value,
                "attributes": [list(pair) for pair in self.attributes],
                "provenance": self.provenance.to_json()}


# --- Layer C: references ----------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasReference:
    """An edge to a raw offset nothing has claimed yet.

    `layout.Reference.target` is an `AnchorId` (layout.py:165) and
    `RomDocument.validate` refuses an unknown one (document.py:114), so the
    existing type cannot express the atlas's normal case: a pointer census finds
    58,308 distinct targets, almost none of which are declared anchors. Edges
    whose target IS a declared anchor still use `layout.Reference`.
    """

    source: FileOffset
    target: FileOffset
    width: int
    encoding: ReferenceEncoding
    confidence: Confidence
    provenance: Provenance

    def __post_init__(self) -> None:
        if not isinstance(self.source, FileOffset) or not isinstance(self.target, FileOffset):
            raise AtlasError("atlas reference requires typed file offsets")
        if type(self.width) is not int or self.width <= 0:
            raise AtlasError("atlas reference width must be positive")
        if not isinstance(self.encoding, ReferenceEncoding):
            raise AtlasError("unsupported reference encoding")
        strength(self.confidence)
        if not isinstance(self.provenance, Provenance):
            raise AtlasError("atlas reference requires typed provenance")

    @property
    def source_range(self) -> RomRange:
        return RomRange(self.source, self.width)

    def to_json(self) -> dict:
        return {"layer": "reference", "source_file_offset": self.source.value,
                "target_file_offset": self.target.value, "width": self.width,
                "encoding": self.encoding.value, "confidence": self.confidence.value,
                "provenance": self.provenance.to_json()}


# --- Layer D: observations --------------------------------------------------


@dataclass(frozen=True, slots=True)
class Observation:
    """A scanner's raw note. Capped at CANDIDATE, enforced by the type."""

    range: RomRange
    kind: str
    detail: str
    confidence: Confidence
    provenance: Provenance

    def __post_init__(self) -> None:
        if not isinstance(self.range, RomRange):
            raise AtlasError("observation requires a typed RomRange")
        try:
            require_name(self.kind)
            require_name(self.detail)
        except LayoutError as exc:
            raise AtlasError(f"observation kind and detail: {exc}") from exc
        if strength(self.confidence) > strength(Confidence.CANDIDATE):
            raise AtlasError(
                f"observation confidence {self.confidence.value} exceeds CANDIDATE; "
                "an observation cannot promote itself into confirmed structure")
        if not isinstance(self.provenance, Provenance):
            raise AtlasError("observation requires typed provenance")

    def to_json(self) -> dict:
        return {"layer": "observation", "file_offset": self.range.start.value,
                "size": self.range.size, "kind": self.kind, "detail": self.detail,
                "confidence": self.confidence.value,
                "provenance": self.provenance.to_json()}


# --- The atlas --------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Atlas:
    profile_id: str
    base_sha256: str
    image_size: int
    coverage: CoverageMap
    objects: tuple[AtlasObject, ...] = ()
    references: tuple[AtlasReference | Reference, ...] = ()
    observations: tuple[Observation, ...] = ()

    def _check_provenance(self, provenance: Provenance, what: str) -> None:
        if (provenance.profile_id, provenance.base_sha256) != (self.profile_id, self.base_sha256):
            raise AtlasError(f"wrong profile provenance on {what}")

    def validate(self) -> None:
        if type(self.image_size) is not int or self.image_size <= 0:
            raise AtlasError("atlas image size must be a positive integer")
        if self.coverage.image_size != self.image_size:
            raise AtlasError(
                f"coverage covers {self.coverage.image_size} bytes, atlas is {self.image_size}")
        self.coverage.validate()
        for span in self.coverage.spans:
            self._check_provenance(span.provenance, f"coverage 0x{span.range.start.value:X}")
        identities = {object.identity for object in self.objects}
        if len(identities) != len(self.objects):
            seen: set[str] = set()
            for object in self.objects:
                if object.identity in seen:
                    raise AtlasError(f"duplicate object identity {object.identity!r}")
                seen.add(object.identity)
        for object in self.objects:
            self._bounds(object.range, f"object {object.identity!r}")
            self._check_provenance(object.provenance, f"object {object.identity!r}")
        for reference in self.references:
            self._bounds(reference.source_range, f"reference at 0x{reference.source.value:X}")
            if isinstance(reference, AtlasReference):
                self._bounds(_range(reference.target.value, 1),
                             f"reference target 0x{reference.target.value:X}")
            self._check_provenance(reference.provenance,
                                   f"reference at 0x{reference.source.value:X}")
        for observation in self.observations:
            self._bounds(observation.range, f"observation {observation.kind!r}")
            self._check_provenance(observation.provenance, f"observation {observation.kind!r}")

    def _bounds(self, range: RomRange, what: str) -> None:
        try:
            range.validate(self.image_size)
        except LayoutError as exc:
            raise AtlasError(f"{what} out of bounds: {exc}") from exc

    # -- serialization --

    def to_jsonl_lines(self) -> Iterator[str]:
        """Deterministic JSONL: sorted keys, stable order, no floats or clocks."""
        rows = [{"layer": "meta", "profile_id": self.profile_id,
                 "base_sha256": self.base_sha256, "image_size": self.image_size}]
        rows.extend(span.to_json() for span in self.coverage.spans)
        rows.extend(object.to_json()
                    for object in sorted(self.objects, key=lambda o: o.identity))
        rows.extend(reference.to_json() for reference in sorted(
            self.references, key=_reference_sort_key))
        rows.extend(observation.to_json() for observation in sorted(
            self.observations, key=lambda o: (o.range.start.value, o.kind, o.detail)))
        for row in rows:
            yield json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"

    @classmethod
    def from_jsonl_lines(cls, lines: Iterable[str]) -> Atlas:
        meta = None
        spans: list[CoverageSpan] = []
        objects: list[AtlasObject] = []
        references: list[AtlasReference | Reference] = []
        observations: list[Observation] = []
        for line in lines:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AtlasError(f"malformed atlas line: {exc}") from exc
            layer = row.get("layer")
            if layer == "meta":
                meta = row
            elif layer == "coverage":
                spans.append(CoverageSpan(
                    _range(row["file_offset"], row["size"]), row["classification"],
                    Confidence(row["confidence"]), _provenance(row)))
            elif layer == "object":
                objects.append(AtlasObject(
                    row["identity"], _range(row["file_offset"], row["size"]), row["kind"],
                    Confidence(row["confidence"]), _provenance(row),
                    tuple((key, value) for key, value in row["attributes"])))
            elif layer == "reference":
                references.append(_reference_from_json(row))
            elif layer == "observation":
                observations.append(Observation(
                    _range(row["file_offset"], row["size"]), row["kind"], row["detail"],
                    Confidence(row["confidence"]), _provenance(row)))
            else:
                raise AtlasError(f"unknown atlas layer {layer!r}")
        if meta is None:
            raise AtlasError("atlas is missing its meta line")
        atlas = cls(meta["profile_id"], meta["base_sha256"], meta["image_size"],
                    CoverageMap(tuple(spans), meta["image_size"]), tuple(objects),
                    tuple(references), tuple(observations))
        atlas.validate()
        return atlas


def _provenance(row: dict) -> Provenance:
    data = row["provenance"]
    return Provenance(data["profile_id"], data["base_sha256"], data["evidence"])


def _reference_sort_key(reference) -> tuple:
    """Source then target. An AnchorId target sorts by its string identity."""
    return (reference.source.value, str(reference.target.value))


def _reference_from_json(row: dict) -> AtlasReference | Reference:
    if "target_anchor" in row:
        from .layout import AnchorId  # local: only declared-anchor edges need it
        return Reference(
            FileOffset(row["source_file_offset"]), AnchorId(row["target_anchor"]),
            row["target_delta"], ReferenceEncoding(row["encoding"]),
            ReferenceClass(row["classification"]), _provenance(row))
    return AtlasReference(
        FileOffset(row["source_file_offset"]), FileOffset(row["target_file_offset"]),
        row["width"], ReferenceEncoding(row["encoding"]),
        Confidence(row["confidence"]), _provenance(row))


# --- Query surface ----------------------------------------------------------


def addr(atlas: Atlas, offset: FileOffset) -> dict:
    """Everything the atlas knows about one byte."""
    point = _as_range(offset)
    return {
        "coverage": atlas.coverage.at(offset),
        "objects": tuple(o for o in atlas.objects if o.contains(offset)),
        "observations": tuple(o for o in atlas.observations if o.range.overlaps(point)),
    }


def refs_to(atlas: Atlas, target: FileOffset | RomRange) -> tuple:
    """References whose target lands inside `target`. Atlas edges only.

    A `layout.Reference` targets an `AnchorId`, whose offset only the owning
    document can resolve, so it is not answerable here.
    """
    wanted = _as_range(target)
    return tuple(r for r in atlas.references
                 if isinstance(r, AtlasReference) and wanted.contains(r.target))


def refs_from(atlas: Atlas, source: FileOffset | RomRange) -> tuple:
    """References whose source field intersects `source`."""
    wanted = _as_range(source)
    return tuple(r for r in atlas.references if r.source_range.overlaps(wanted))


def in_range(atlas: Atlas, range: RomRange) -> dict:
    """Everything intersecting `range`, layer by layer."""
    return {
        "coverage": atlas.coverage.overlapping(range),
        "objects": tuple(o for o in atlas.objects if o.range.overlaps(range)),
        # A reference both sourced and targeted inside the range satisfies both
        # queries, so concatenating them would report it twice.
        "references": tuple(dict.fromkeys(refs_from(atlas, range)
                                          + refs_to(atlas, range))),
        "observations": tuple(o for o in atlas.observations if o.range.overlaps(range)),
    }


def unknowns(atlas: Atlas, limit: int | None = None) -> tuple[CoverageSpan, ...]:
    """The unknown leaderboard: unclassified coverage, largest first."""
    ranked = sorted((s for s in atlas.coverage.spans
                     if s.classification in UNKNOWN_CLASSIFICATIONS),
                    key=lambda s: (-s.range.size, s.range.start.value))
    return tuple(ranked if limit is None else ranked[:limit])


def objects_of_kind(atlas: Atlas, kind: str) -> tuple[AtlasObject, ...]:
    return tuple(sorted((o for o in atlas.objects if o.kind == kind),
                        key=lambda o: o.range.start.value))


# --- The owner range index ---------------------------------------------------
#
# S4 (DRAGONBYTE-Z-OWNER-RANGE-INDEX-001). "What owns these bytes" is answered
# from the atlas, never from a second scan: the classification and confidence of
# a byte are read out of `atlas.coverage` (layer A), and an owner is an
# `AtlasObject` identity (layer B) or a declared extent the caller supplies. The
# index adds no vocabulary: a byte nobody owns keeps its atlas classification,
# so an unowned byte reads `UNKNOWN` rather than a word this module invented.

#: The provenance of a declared extent. It is a different kind of claim from a
#: located object, so it is named rather than left blank.
DECLARED_EXTENT = "declared-extent"


def _unknown_bytes(atlas: Atlas, bound: RomRange) -> int:
    """Bytes of `bound` whose atlas classification is one of the unknowns.

    The one place a count of this kind is computed, so `unknowns()`' whole-image
    total and a scan's total over one range cannot be two different calculations
    of the same number.
    """
    counted = 0
    for span in atlas.coverage.overlapping(bound):
        if span.classification in UNKNOWN_CLASSIFICATIONS:
            counted += min(span.range.end, bound.end) - max(span.range.start.value,
                                                            bound.start.value)
    return counted


@dataclass(frozen=True, slots=True)
class OwnerSpan:
    """One extent one owner claims, as the index derived it.

    `source` is `atlas-object` or `declared-extent`, which lets a caller tell a
    located structure from an extent a configuration vouches for.
    """

    range: RomRange
    owner: str
    source: str

    def __post_init__(self) -> None:
        if not isinstance(self.range, RomRange):
            raise AtlasError("owner span requires a typed RomRange")
        try:
            require_name(self.owner)
        except LayoutError as exc:
            raise AtlasError(f"owner span owner: {exc}") from exc
        if self.source not in ("atlas-object", DECLARED_EXTENT):
            raise AtlasError(f"unknown owner span source {self.source!r}")

    def to_json(self) -> dict:
        return {"file_offset": self.range.start.value, "size": self.range.size,
                "owner": self.owner, "source": self.source}


@dataclass(frozen=True, slots=True)
class RangeIndex:
    """Range to owners, owner to ranges, over one validated `Atlas`.

    `declared` are extents a configuration vouches for, as `(range, owner)`
    pairs, in the order the atlas counts them. They are extents, not a partition:
    a declared table and an atlas object may cover the same byte, and both are
    reported. Declared extents are not wrapped in `AtlasObject` because that
    layer's identities, kinds and confidences are the atlas's to declare.
    """

    atlas: Atlas
    declared: tuple[tuple[RomRange, str], ...] = ()
    _spans: tuple[OwnerSpan, ...] = ()
    _starts: tuple[int, ...] = ()
    _reaches: tuple[int, ...] = ()
    _by_owner: dict[str, tuple[OwnerSpan, ...]] = field(default_factory=dict)
    _edge_starts: tuple[tuple[int, int], ...] = ()
    _edge_reaches: tuple[tuple[int, int], ...] = ()
    _targets: tuple[int, ...] = ()
    _target_positions: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        spans: list[OwnerSpan] = [
            OwnerSpan(object.range, object.identity, "atlas-object")
            for object in self.atlas.objects]
        for extent, owner in self.declared:
            try:
                extent.validate(self.atlas.image_size)
            except LayoutError as exc:
                raise AtlasError(f"declared extent for {owner!r} out of image: {exc}") from exc
            spans.append(OwnerSpan(extent, owner, DECLARED_EXTENT))
        spans.sort(key=lambda span: (span.range.start.value, span.range.size, span.owner))
        reaches: list[int] = []
        furthest = 0
        for span in spans:
            furthest = max(furthest, span.range.end)
            reaches.append(furthest)
        by_owner: dict[str, list[OwnerSpan]] = {}
        for span in spans:
            by_owner.setdefault(span.owner, []).append(span)
        # Reference candidates, so the reference half of a query does not scan
        # every edge in the atlas. Targets and sources are each kept in an array
        # parallel to a start-sorted position array, the source side carrying the
        # prefix maximum of the ends.
        positions = sorted(range(len(self.atlas.references)),
                           key=lambda index: (self.atlas.references[index].source.value,
                                              self.atlas.references[index].source_range.size))
        edge_starts: list[int] = []
        edge_reaches: list[int] = []
        furthest = 0
        for index in positions:
            edge_starts.append(self.atlas.references[index].source.value)
            furthest = max(furthest, self.atlas.references[index].source_range.end)
            edge_reaches.append(furthest)
        targeted = sorted(
            (ref.target.value, index)
            for index, ref in enumerate(self.atlas.references)
            if isinstance(ref, AtlasReference))
        object.__setattr__(self, "_spans", tuple(spans))
        object.__setattr__(self, "_starts", tuple(s.range.start.value for s in spans))
        object.__setattr__(self, "_reaches", tuple(reaches))
        object.__setattr__(self, "_by_owner", {owner: tuple(claimed)
                                               for owner, claimed in by_owner.items()})
        object.__setattr__(self, "_edge_starts", tuple(
            (value, positions[at]) for at, value in enumerate(edge_starts)))
        object.__setattr__(self, "_edge_reaches", tuple(
            (value, positions[at]) for at, value in enumerate(edge_reaches)))
        object.__setattr__(self, "_targets", tuple(value for value, _ in targeted))
        object.__setattr__(self, "_target_positions", tuple(index for _, index in targeted))

    def _references_in_range(self, wanted: RomRange) -> tuple:
        """`refs_from` and `refs_to` for `wanted`, in one pass over candidates.

        The answer is `in_range`'s reference half: an edge sourced in the range or
        targeted in it, each reported once. Candidate selection is the same
        bisect bound the owner half uses, so this resolves an edge only when a
        source or a target could land here.
        """
        edges = self.atlas.references
        # ASSUMPTION: candidates come back in descending source order, which
        # equals atlas order only while a reference field is 4 bytes wide and
        # sources are pairwise disjoint (every reference today). A wider or
        # unaligned field lets two sources share a byte, and then the two
        # orders differ and this must sort the way `in_range` does.
        by_source = tuple(index for index in
                          (self._edge_starts[at][1] for at in
                           range(bisect_left(self._edge_starts, (wanted.end, -1)) - 1,
                                 bisect_right(self._edge_reaches,
                                              (wanted.start.value, len(edges))) - 1,
                                 -1))
                          if edges[index].source_range.overlaps(wanted))
        first, last = (bisect_left(self._targets, wanted.start.value),
                       bisect_left(self._targets, wanted.end))
        by_target = tuple(index for index in
                          (self._target_positions[position]
                           for position in range(first, last))
                          if isinstance(edges[index], AtlasReference)
                          and wanted.contains(edges[index].target))
        return tuple(edges[index] for index in dict.fromkeys(by_source + by_target))

    def _hits(self, start: int, end: int) -> Iterator[int]:
        """Indices of every span that could intersect [start, end), descending.

        `_starts` bounds the candidate set on the left and the prefix maximum of
        the ends on the right, so neither a long span that begins earlier nor a
        short one that begins later is missed. The caller still tests the exact
        predicate it wants; a candidate is not yet an answer.
        """
        index = bisect_left(self._starts, end) - 1
        floor = bisect_right(self._reaches, start)
        while index >= floor:
            yield index
            index -= 1

    @property
    def spans(self) -> tuple[OwnerSpan, ...]:
        """Every claimed extent, in offset order."""
        return self._spans

    def spans_at(self, offset: FileOffset) -> tuple[OwnerSpan, ...]:
        """Every extent claiming one byte. Empty means nobody owns it.

        A point outside the image is not refused, unlike a range: it answers
        "nobody owns this" for the one-byte question, where `spans_overlapping`
        has a whole range to justify.
        """
        if not isinstance(offset, FileOffset):
            raise AtlasError("a range index lookup requires a typed FileOffset")
        return tuple(reversed([self._spans[index]
                               for index in self._hits(offset.value, offset.value + 1)
                               if self._spans[index].range.contains(offset)]))

    def spans_overlapping(self, wanted: RomRange) -> tuple[OwnerSpan, ...]:
        """Every extent intersecting `wanted`, in offset order."""
        if not isinstance(wanted, RomRange):
            raise AtlasError("a range index lookup requires a typed RomRange")
        wanted.validate(self.atlas.image_size)
        return tuple(reversed([self._spans[index]
                               for index in self._hits(wanted.start.value, wanted.end)
                               if self._spans[index].range.overlaps(wanted)]))

    def owners_of(self, range: RomRange) -> tuple[str, ...]:
        """The distinct owners claiming any byte of `range`. Empty means unowned."""
        return tuple(sorted({span.owner for span in self.spans_overlapping(range)}))

    def ranges_of(self, owner: str) -> tuple[RomRange, ...]:
        """Every extent `owner` claims. Empty means the index does not know it."""
        return tuple(item.range for item in self._by_owner.get(owner, ()))

    def spans_of(self, owner: str) -> tuple[OwnerSpan, ...]:
        """Every extent `owner` claims, with the source each one came from."""
        return self._by_owner.get(owner, ())

    def at(self, offset: FileOffset) -> dict:
        """Everything the index knows about one byte.

        Every field is the atlas's own answer: the classification and confidence
        come from the coverage span containing the byte, the owners are the
        extents claiming it, and the references are `in_range`'s reference half
        for the same one-byte range. `owners` empty is an answer, not a gap: the
        byte is unowned and still carries its atlas classification.
        """
        point = RomRange(offset, 1)
        spans = self.spans_at(offset)
        coverage = self.atlas.coverage.at(offset)
        return {
            "offset": offset,
            "classification": coverage.classification,
            "confidence": coverage.confidence,
            "spans": spans,
            "owners": tuple(sorted({span.owner for span in spans})),
            "references": self._references_in_range(point),
        }

    def owner_bytes(self) -> tuple[tuple[str, int], ...]:
        """The owner leaderboard: claimed bytes per owner, largest first.

        Ranges are summed as the index derived them, so an owner of two
        overlapping extents counts those bytes twice; the leaderboard ranks
        owners, and `overview`'s byte totals are what stay exact-once.
        """
        totals: dict[str, int] = {}
        for span in self._spans:
            totals[span.owner] = totals.get(span.owner, 0) + span.range.size
        return tuple(sorted(totals.items(), key=lambda item: (-item[1], item[0])))

    def overview(self) -> dict:
        """Unowned bytes and byte totals per atlas classification.

        `unowned_bytes` counts the bytes `unknowns()` ranks, and the table sums
        the atlas's own coverage spans by classification, so this reports the
        atlas's vocabulary and partition rather than a second of either.
        """
        by_classification: dict[str, int] = {}
        for span in self.atlas.coverage.spans:
            by_classification[span.classification] = (
                by_classification.get(span.classification, 0) + span.range.size)
        return {
            "image_size": self.atlas.image_size,
            "coverage_spans": len(self.atlas.coverage.spans),
            "owners": len(self.owner_bytes()),
            "objects": len(self.atlas.objects),
            "declared_extents": len(self.declared),
            "unowned_bytes": _unknown_bytes(self.atlas,
                                            _range(0, self.atlas.image_size)),
            "by_classification": tuple(sorted(by_classification.items(),
                                              key=lambda item: (-item[1], item[0]))),
        }

    def scan(self, wanted: RomRange) -> dict:
        """Every owner in a range, the way `search_text` returns every phrase hit.

        One entry per distinct owner intersecting `wanted`, each carrying the
        lowest byte that owner claims INSIDE `wanted`, the classification and
        confidence `at` reports for that byte, the owner's own extents, and the
        references intersecting it. A range no owner claims yields `hits: ()` and
        an `unowned_bytes` count, so `UNKNOWN` is a first-class answer with a
        number rather than a silence.

        A hit inside a compressed container would also report the container's
        offset and the offset within its decoded stream; that half needs the
        decoded container index and is not built here.
        """
        wanted.validate(self.atlas.image_size)
        hits = []
        for owner in self.owners_of(wanted):
            claimed = self.spans_of(owner)
            inside = min(max(item.range.start.value, wanted.start.value)
                         for item in claimed if item.range.overlaps(wanted))
            point = self.at(FileOffset(inside))
            hits.append({
                "owner": owner,
                "file_offset": inside,
                "classification": point["classification"],
                "confidence": point["confidence"],
                "spans": claimed,
                "references": self.references(owner),
            })
        return {"range": wanted, "owners": len(hits), "hits": tuple(hits),
                "unowned_bytes": _unknown_bytes(self.atlas, wanted)}

    def references(self, owner: str) -> tuple:
        """Every reference intersecting any extent `owner` claims."""
        edges = []
        for claimed in self.ranges_of(owner):
            edges.extend(refs_from(self.atlas, claimed))
            edges.extend(refs_to(self.atlas, claimed))
        return tuple(dict.fromkeys(edges))


# --- Text search ------------------------------------------------------------
#
# These read no ROM by themselves: `search_text` recovers a decoded phrase's
# handle only when the caller hands it `rom_image` bytes, so the atlas module
# still opens no image of its own. Lifted from `cli.py` so the CLI and the
# Workbench GUI search through one implementation (WORKBENCH-001).


def _collapse_whitespace(value: str) -> str:
    """Fold every whitespace run to one space. Conservative: nothing else moves."""
    return " ".join(value.split())


def text_match(phrase: str, haystack: str) -> str | None:
    """`"exact"`, `"normalized"`, or None when the phrase is absent.

    Normalization is comparison-only and deliberately small: case folding and
    whitespace collapsing, nothing fuzzy. A caller must be able to tell which of
    the two happened, because a normalized hit is a weaker claim than an exact
    one and silently conflating them would make the result unciteable.
    """
    if phrase in haystack:
        return "exact"
    if (_collapse_whitespace(phrase).casefold()
            in _collapse_whitespace(haystack).casefold()):
        return "normalized"
    return None


def search_text(atlas: Atlas, phrase: str, decoded_rows,
                *, rom_image: bytes | None = None) -> dict:
    """Phrase search over raw ROM text runs and the decoded-container index.

    Two surfaces, one phrase. A raw hit is a ROM run and reports its real file
    offset. A decoded hit lives inside a decompressed container and reports its
    CONTAINER's ROM offset plus an offset within the decoded stream — never a
    ROM address for the text itself, because the text has none.

    Returns the full `{"searched", "matched", "raw_matched", "decoded_matched",
    "runs", "decoded"}` shape. `runs`/`decoded` are unsliced: the caller applies
    any `[:limit]` and the `0x%06X` field formatting stays where the atlas rows
    already carry it.
    """
    raw_hits = [(o, text_match(phrase, o.detail))
                for o in atlas.observations if o.kind.startswith("text-run-")]
    raw_hits = [(o, how) for o, how in raw_hits if how is not None]
    decoded_hits = [(row, text_match(phrase, row.get("text") or ""))
                    for row in decoded_rows]
    decoded_hits = [(row, how) for row, how in decoded_hits if how is not None]

    def observation_json(observation) -> dict:
        return {"file_offset": f"0x{observation.range.start.value:06X}",
                "size": observation.range.size, "kind": observation.kind,
                "detail": observation.detail,
                "confidence": observation.confidence.value}

    def raw_json(observation, how: str) -> dict:
        return {"source": "raw-rom-run", "match": how,
                **observation_json(observation)}

    def decoded_json(row: dict, how: str) -> dict:
        # No "file_offset" key at this level, deliberately: every other
        # result shape uses that name for a ROM offset, and giving a
        # decoded run one would be a lie a reader could not detect.
        # Where the PHRASE itself sits, when it can be located exactly.
        # A run may hold several logical strings (these streams have no
        # delimiter between some of them), so the run's own start is
        # often not where the searched phrase begins. Both are reported:
        # the run's offset, and the phrase's, each in decoded-stream
        # units. Two UTF-16LE bytes per character is the encoding, so
        # the character index doubles into a byte offset.
        found = row["text"].find(phrase) if how == "exact" else -1
        phrase_offset = (None if found < 0
                         else row["decoded_offset"] + found * 2)

        # The durable identity, where it can be recovered. It is keyed
        # on the PHRASE's span, never the run's: a run merges several
        # handle-defined records, so the run's own span names many
        # identities and the phrase's names one. A normalized match
        # cannot locate the phrase exactly, so it recovers nothing
        # rather than guessing between candidates.
        if rom_image is None:
            identity = {"packed_handle": None,
                        "unrecovered_because":
                            "no ROM supplied; pass --rom to recover the "
                            "handle and its reference sites"}
        elif phrase_offset is None:
            identity = {"packed_handle": None,
                        "unrecovered_because":
                            f"a {how} match cannot locate the phrase's "
                            "exact decoded span, and a span is what "
                            "names the handle"}
        else:
            identity = recover_handle(rom_image,
                                      row["container_index"],
                                      phrase_offset,
                                      len(phrase) * 2)

        return {"source": "decoded-container-text", "match": how,
                # ONE identity object, carrying a LIST of reference
                # sites. Never one row per site: the handle is the
                # message's name, the sites are where it is referenced.
                "identity": identity,
                "container_file_offset":
                    f"0x{row['container_file_offset']:06X}",
                "container_rom_address": row["container_rom_address"],
                "container_index": row["container_index"],
                "decompressor": row["decompressor"],
                "decoded_offset": f"0x{row['decoded_offset']:X}",
                "decoded_offset_of_phrase":
                    None if phrase_offset is None else f"0x{phrase_offset:X}",
                "encoding": row["encoding"],
                "char_count": row["char_count"],
                "text": row["text"],
                "rom_offset_of_text": "NONE: this text exists only after "
                                      "decompression and has no ROM address"}

    return {
        "searched": "raw ROM text runs (scan_text.jsonl, full run text) and "
                    "the decoded-container index (scan_decoded_text.jsonl, "
                    "full decoded run text). Neither is truncated. A "
                    "decoded match reports its container's ROM offset and "
                    "an offset within the decoded stream; the text itself "
                    "has no ROM address. Its durable identity is the "
                    "packed handle naming it, recovered only when --rom "
                    "is given and reported as null otherwise.",
        "matched": len(raw_hits) + len(decoded_hits),
        "raw_matched": len(raw_hits),
        "decoded_matched": len(decoded_hits),
        "runs": [raw_json(o, how) for o, how in
                 sorted(raw_hits, key=lambda item: item[0].range.start.value)],
        "decoded": [decoded_json(row, how) for row, how in
                    sorted(decoded_hits,
                           key=lambda item: (item[0]["container_file_offset"],
                                             item[0]["decoded_offset"]))],
    }
