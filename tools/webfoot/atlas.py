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
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from enum import Enum
import json
from typing import Iterable, Iterator

from .binary import FileOffset
from .layout import (LayoutError, Provenance, Reference, ReferenceClass,
                     ReferenceEncoding, RomRange, require_name)


class AtlasError(ValueError):
    """An atlas cannot be justified against its image."""


class Confidence(str, Enum):
    """Ascending evidence strength. These do NOT collapse into each other.

    `OBSERVED` is "a pass saw this shape", `CANDIDATE` is "it survived a filter",
    `INFERRED` is docs/DEVELOPMENT.md's INFERRED, `CONFIRMED` its CONFIRMED, and
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
