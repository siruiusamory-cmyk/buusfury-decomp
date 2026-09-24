"""ROM-CAPACITY-AND-ALLOCATION-001 Phase A: measured occupancy and region map.

This is a research adapter in the same family as
:mod:`tools.research.free_space_audit` and :mod:`tools.research.capacity_proof`,
and it keeps their discipline:

* it **measures** and **reports**; it promotes nothing;
* production free space is still exactly what `profile.free_regions` declares
  with `CONFIRMED` status, and nothing here can add a byte to it;
* `FF` fill is never called free. A run of fill is a *candidate* until the
  window verifier in `capacity_proof` clears it and a human review writes a
  profile declaration.

What it adds over those two modules is coverage, and one question the prior
tickets asked only of a bounded tail:

1. an **exhaustive partition** of the canonical image into the classes the
   ticket names - `OWNED`, `REFERENCED`, `VERIFIED_FREE` and `UNKNOWN` - every
   byte in exactly one of them. `PADDING_EXPANDED` is reported separately as a
   generated-image *policy* (see :data:`PADDING_EXPANDED`), never as canonical
   occupancy;
2. a **whole-image candidate census** at every byte position (not only
   word-aligned sources, and not only inside `[0x007B89A8, 0x00800000)`), which
   turns "how much of the tail might be promotable" into "how much of the
   *image* survives the established verifier's own checks";
3. free-region geometry: count, sizes, fragmentation, and what alignment and a
   minimum block size cost.

The census is deliberately the **same** procedure `capacity_proof` applies to
one window: the same `FF`-fill requirement, the same known-inbound and
known-overlap exclusions, the same interior-byte candidate-target test at every
alignment, the same `candidate_source` test, and the same clearance margin.
:func:`census_agrees_with_verifier` re-runs the reviewed verifier on a
census-derived window with the model's real annotations and references, so a
drift between the census and the verifier is detected rather than assumed.

Nothing here is reachable from the production allocation path. It imports
`free_space_audit.build_model` so its negatives are measured against the
identical annotation and reference model that produced TOOLKIT-011's positives.
"""
from __future__ import annotations

import argparse
import bisect
from collections import Counter
from dataclasses import dataclass, field
import heapq
import json
from pathlib import Path
import struct

from tools.webfoot.binary import FileOffset, GBA_ROM_BASE
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import RomProfile, RomProfileCatalog, VerificationStatus
from tools.webfoot.rom import identify_rom

# --- classification vocabulary ----------------------------------------------

#: Bytes proven to belong to a known live structure or resource.
OWNED = "OWNED"
#: Bytes reached by a known pointer/reference but not claimed by a structure.
REFERENCED = "REFERENCED"
#: Bytes declared free in the profile, i.e. proven safe by a reviewed ticket.
VERIFIED_FREE = "VERIFIED_FREE"
#: Bytes not proven occupied and not proven free.
UNKNOWN = "UNKNOWN"
#: Bytes outside the canonical image in a generated expanded image. This class
#: is reported by the `expansion` policy block rather than by the canonical
#: partition, because it does not exist in the canonical image: a generated
#: image has no canonical bytes to classify, and folding padding into the
#: partition would report generated capacity as if it were retail bytes.
PADDING_EXPANDED = "PADDING_EXPANDED"

CLASSIFICATIONS = (OWNED, REFERENCED, VERIFIED_FREE, UNKNOWN)

#: Ascending claim strength for the paint sweep. `VERIFIED_FREE` ranks above
#: `OWNED` only so that a free declaration overlapping content is *detected*
#: (`free_region_conflicts`) rather than silently outranked; the module reports
#: that conflict and a caller must not treat such a model as usable.
_RANK = {UNKNOWN: 0, REFERENCED: 1, OWNED: 2, VERIFIED_FREE: 3}
_RANK_NAMES = {0: UNKNOWN, 1: REFERENCED, 2: OWNED, 3: VERIFIED_FREE}

#: The compressed-dialogue selector table: exactly seven words at `0x7B5B64`,
#: a documented structural gate. See :func:`dialogue_selector_offsets`.
DIALOGUE_SELECTOR_TABLE = 0x7B5B64
DIALOGUE_SELECTOR_COUNT = 7

#: Nominal platform window upper bound, derived from the one sanctioned base
#: constant. Named so the report cannot mistake it for a proven engine limit.
GBA_ROM_WINDOW_SIZE = 0x02000000

_POINTER = struct.Struct("<I")


@dataclass(frozen=True, slots=True)
class PointerCensus:
    """Every u32 that addresses the image, as byte maps plus a summary.

    ``observations`` is empty unless a caller asked for the explicit list; the
    counts are always measured, so an uncollected sweep still reports exactly
    how many pointer-shaped words exist and how many are word-aligned.
    """

    targets: bytearray
    sources: bytearray
    observations: tuple
    count: int
    aligned_count: int


@dataclass(frozen=True, slots=True)
class Annotation:
    """One measured claim that a span of canonical bytes belongs to something."""

    start: int
    end: int
    kind: str
    owner: str
    status: str
    source: str

    @property
    def size(self) -> int:
        return self.end - self.start


@dataclass(frozen=True, slots=True)
class Region:
    """One span of the region map, in exactly one classification."""

    start: int
    end: int
    classification: str
    confidence: str
    evidence: str
    owner: str
    kind: str

    @property
    def size(self) -> int:
        return self.end - self.start

    def to_json(self) -> dict:
        return {
            "start": self.start, "end": self.end, "length": self.size,
            "classification": self.classification, "confidence": self.confidence,
            "evidence": self.evidence, "owner": self.owner, "kind": self.kind,
            "start_hex": f"0x{self.start:06X}", "end_hex": f"0x{self.end:06X}",
        }


@dataclass(slots=True)
class CapacityModel:
    """Everything Phase A measured about one canonical image."""

    profile_id: str
    base_sha256: str
    image_size: int
    expansion_output_size: int | None
    expansion_padding_byte: int | None
    expansion_evidence: str
    regions: tuple[Region, ...]
    annotations: tuple[Annotation, ...]
    references: tuple[dict, ...]
    candidate_observation_count: int
    candidate_observation_aligned_count: int
    candidate_target_bytes: int
    candidate_source_bytes: int
    reference_sources_outside_owned: int
    free_region_conflicts: tuple[str, ...]
    promotable_runs: tuple[tuple[int, int], ...]
    margin: int
    margin_curve: dict = field(default_factory=dict)
    diagnostics: dict = field(default_factory=dict)

    # --- accounting ---------------------------------------------------------

    def bytes_by_class(self) -> dict[str, int]:
        counts = Counter()
        for region in self.regions:
            counts[region.classification] += region.size
        return {name: counts.get(name, 0) for name in CLASSIFICATIONS}

    def accounting(self) -> list[dict]:
        size = self.image_size or 1
        return [
            {"classification": name,
             "bytes": sum(r.size for r in self.regions if r.classification == name),
             "percent": round(100.0 * sum(
                 r.size for r in self.regions if r.classification == name) / size, 4)}
            for name in CLASSIFICATIONS
        ]

    def regions_of(self, classification: str) -> tuple[Region, ...]:
        return tuple(r for r in self.regions if r.classification == classification)

    def reference_targets(self) -> int:
        return len({r["target"] for r in self.references})

    def promotable_bytes(self) -> int:
        return sum(end - start for start, end in self.promotable_runs)

    def to_json(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "base_sha256": self.base_sha256,
            "image_size": self.image_size,
            "expansion": (None if self.expansion_output_size is None else {
                "classification": PADDING_EXPANDED,
                "output_size": self.expansion_output_size,
                "padding_byte": self.expansion_padding_byte,
                "raw_expanded_bytes": self.expansion_output_size - self.image_size,
                "evidence": self.expansion_evidence,
            }),
            "nominal_platform_window_bytes": GBA_ROM_WINDOW_SIZE,
            "accounting": self.accounting(),
            "reference_count": len(self.references),
            "reference_distinct_targets": self.reference_targets(),
            "reference_sources_outside_owned": self.reference_sources_outside_owned,
            "candidate_observations": self.candidate_observation_count,
            "candidate_observations_word_aligned": self.candidate_observation_aligned_count,
            "candidate_target_bytes": self.candidate_target_bytes,
            "candidate_source_bytes": self.candidate_source_bytes,
            "free_region_conflicts": list(self.free_region_conflicts),
            "declared_free_statistics": span_statistics(
                [(r.start, r.end) for r in self.regions
                 if r.classification == VERIFIED_FREE]),
            "promotable_census": {
                "margin": self.margin,
                "runs": len(self.promotable_runs),
                "bytes": self.promotable_bytes(),
                "statistics": span_statistics(self.promotable_runs),
                "by_margin": self.margin_curve,
                "largest": [
                    {"start": s, "end": e, "size": e - s,
                     "start_hex": f"0x{s:06X}", "end_hex": f"0x{e:06X}"}
                    for s, e in sorted(self.promotable_runs,
                                       key=lambda run: (-(run[1] - run[0]), run[0]))[:20]
                ],
            },
            "diagnostics": self.diagnostics,
        }

    def region_map_lines(self):
        for region in self.regions:
            yield json.dumps(region.to_json(), sort_keys=True)


# --- evidence loading -------------------------------------------------------


def dialogue_selector_offsets(image: bytes) -> tuple[int, ...]:
    """The seven compressed-dialogue container offsets, strictly validated.

    ONE reader for this table, so the annotation walk and the size distribution
    cannot disagree about what it contains or how strictly they check it. The
    count is a documented gate, not something to discover by walking:
    `docs/research/LOGX_SYNTHESIS_PROVENANCE.md:263` measures the extent as exactly
    seven words, `tools/webfoot/atlas_producers/seed.py:693` seeds the same 28
    bytes, the consumer at `0x08012242` indexes by the packed handle's low six
    bits scaled by four, and the seed states the gate "must NOT be widened"
    because only seven of the sixty-four encodable values are backed
    (`seed.py:707-711`). Every entry must be a strictly ascending in-image ROM
    pointer, so a shifted or corrupted table fails loudly instead of being
    silently truncated.
    """
    size = len(image)
    offsets = []
    for ordinal in range(DIALOGUE_SELECTOR_COUNT):
        slot = DIALOGUE_SELECTOR_TABLE + 4 * ordinal
        raw = int.from_bytes(image[slot:slot + 4], "little")
        if not GBA_ROM_BASE <= raw < GBA_ROM_BASE + size:
            raise ValueError(
                f"dialogue selector {ordinal} at 0x{slot:06X} is not a ROM pointer")
        offset = raw - GBA_ROM_BASE
        if offsets and offset <= offsets[-1]:
            raise ValueError(f"dialogue selector {ordinal} is not ascending")
        offsets.append(offset)
    return tuple(offsets)


def load_production_evidence(rom_path, catalog_path=None):
    """The production annotation/reference model, extended with three domains.

    The base layer is `free_space_audit.build_model` verbatim, so this model's
    negatives are comparable with TOOLKIT-011's positives and TOOLKIT-028's
    window verdict. Three domains that audit did not carry are appended from
    their own production readers - script tables and pools, the
    compressed-dialogue selector table and container extents, and the
    placement-type dispatch table - because leaving them out would advertise
    bytes a production loader already reads as UNKNOWN.
    """
    from tools.research.free_space_audit import build_model

    model = build_model(rom_path, catalog_path=catalog_path)
    image = model["image"]
    profile = model["profile"]
    owned = list(model["owned"])
    references = list(model["references"])
    size = len(image)

    def annotate(start, length, kind, owner, status, source):
        end = min(start + length, size)
        if length <= 0 or end <= start:
            return
        owned.append({"start": start, "end": end, "kind": kind,
                      "owner": owner, "status": status, "source": source})

    # 1. Script corpora: every family declares a record table and a pool, and
    #    the disassembler round-trips both against the canonical bytes.
    for script in profile.scripts or ():
        annotate(script.table_address.to_file_offset(size),
                 script.count * script.stride, "script_table",
                 f"script:{script.family}", "DECLARED", "profile.tables.scripts")
        annotate(script.pool_address.to_file_offset(size), script.pool_size,
                 "script_pool", f"script:{script.family}", "DECLARED",
                 "profile.tables.scripts")

    # 2. Compressed dialogue: one selector table of ROM pointers, then each
    #    container's measured packed extent.
    #
    #    The table is EXACTLY seven words, `0x7B5B64..0x7B5B7C`, and that count
    #    is a documented gate rather than something to infer by walking:
    #    `docs/research/LOGX_SYNTHESIS_PROVENANCE.md:263` measures the extent,
    #    `tools/webfoot/atlas_producers/seed.py:693` seeds the same 28 bytes, and
    #    the consumer at `0x08012242` indexes the table by the packed handle's low
    #    six bits scaled by four. The pointers are read from the image and each
    #    must be a strictly ascending in-image ROM pointer; a shape that fails
    #    that is reported rather than silently truncated.
    #
    #    `Container.packed_end` is an ABSOLUTE file offset
    #    (`tools/webfoot/formats/webfoot_lz.py:164`), so the annotation length is
    #    `packed_size` (`:168`), never `packed_end`. Using the end as a length is
    #    exactly the error that made an earlier draft of this model claim seven
    #    containers running to the end of the image.
    from tools.webfoot.formats.webfoot_lz import unpack

    selector_table = DIALOGUE_SELECTOR_TABLE
    pointers = dialogue_selector_offsets(image)
    annotate(selector_table, 4 * DIALOGUE_SELECTOR_COUNT, "dialogue_selector_table",
             "compressed_dialogue", "DECLARED",
             "docs/research/LOGX_SYNTHESIS_PROVENANCE.md:263 exactly seven words")
    for ordinal, offset in enumerate(pointers):
        container = unpack(image, offset)
        annotate(offset, container.packed_size, "dialogue_container",
                 f"compressed_dialogue:selector{ordinal}", "CONFIRMED",
                 "formats.webfoot_lz.Container.packed_size")
        references.append({"source": selector_table + 4 * ordinal,
                           "target": offset,
                           "classification": "CONFIRMED_REFERENCE"})

    # 3. Placement-type dispatch table: the engine's wrapper reads
    #    `table + stride * selector` for every selector it supports.
    placement = profile.placement_types
    if placement is not None:
        annotate(placement.table_address.to_file_offset(size),
                 (placement.max_selector + 1) * placement.stride,
                 "placement_type_table", "placement_types", "DECLARED",
                 "TOOLKIT-009 measured selector bound")

    return model, owned, references, profile


def scan_pointer_observations(image: bytes, *, span_start: int = 0,
                              span_end: int | None = None, collect: bool = False):
    """Every u32 at **every byte position** whose value addresses the span.

    The same method `capacity_proof.scan_candidate_observations` uses for the
    tail, extended to the whole image so the census is not blind outside
    `[0x007B89A8, 0x00800000)`. Unaligned sources are included on purpose:
    overlapping reads are evidence that not all of them can be authoritative,
    never evidence that the value is meaningless.

    Returns :class:`PointerCensus`. The byte maps are what the census sweeps
    cheaply; the explicit observations are only built when a caller needs to
    hand them to a verifier, because the whole image holds six figures of them.
    """
    size = len(image)
    if span_end is None:
        span_end = size
    targets = bytearray(size)
    sources = bytearray(size)
    observations = []
    count = 0
    aligned = 0
    unpack = _POINTER.unpack_from
    base = GBA_ROM_BASE
    limit = base + size
    for source in range(size - 3):
        raw = unpack(image, source)[0]
        if base <= raw < limit:
            target = raw - base
            targets[target] = 1
            sources[source] = 1
            if span_start <= target < span_end:
                count += 1
                if source % 4 == 0:
                    aligned += 1
                if collect:
                    observations.append(
                        {"source": source, "target": target,
                         "source_word_aligned": source % 4 == 0})
    return PointerCensus(targets, sources, tuple(observations), count, aligned)


# --- the partition ----------------------------------------------------------


def build_region_map(image: bytes, owned, references, profile: RomProfile,
                     *, margin: int = 0x400) -> CapacityModel:
    """One exhaustive, disjoint partition, plus the promotable-window census.

    Painting is weakest-first into a rank array, so a stronger claim is never
    overwritten by a weaker one and every byte ends in exactly one class. Runs
    are then attributed back to the innermost covering annotation, so the map
    answers "who owns this" as well as "what class is it".
    """
    size = len(image)
    rank = bytearray(size)
    annotations = []
    skipped = []
    for row in owned:
        start, end = row["start"], row["end"]
        if row["status"] not in ("CONFIRMED", "DECLARED"):
            skipped.append(f"{row['kind']}:{row['owner']}({row['status']})")
            continue
        RomRange(FileOffset(start), end - start).validate(size)
        annotations.append(Annotation(start, end, row["kind"], row["owner"],
                                      row["status"], row.get("source", "production model")))
    annotations.sort(key=lambda a: (a.start, a.end, a.kind, a.owner))

    # REFERENCED first (the weakest non-unknown claim), then OWNED, then the
    # free declarations, so a free region landing on content shows up as a
    # conflict rather than being quietly outranked.
    referenced = bytearray(size)
    for reference in references:
        target = reference["target"]
        if 0 <= target < size:
            if referenced[target] == 0:
                referenced[target] = 1
            if rank[target] < _RANK[REFERENCED]:
                rank[target] = _RANK[REFERENCED]
    for annotation in annotations:
        for offset in range(annotation.start, annotation.end):
            if rank[offset] < _RANK[OWNED]:
                rank[offset] = _RANK[OWNED]

    conflicts = []
    for region in profile.free_regions:
        start, end = region.range.start.value, region.range.end
        RomRange(FileOffset(start), end - start).validate(size)
        clashing = [a for a in annotations if a.start < end and a.end > start]
        owned_bytes = sum(1 for offset in range(start, end)
                          if rank[offset] == _RANK[OWNED])
        # A known reference TARGET is content too: the ticket's rule is that new
        # content never lands on OWNED, REFERENCED or UNKNOWN. Counting only
        # owned bytes here would let a declaration quietly swallow a reference
        # target that no annotation covers - the same class of byte this model
        # reports as an ownership gap - so both are counted.
        referenced_bytes = sum(1 for offset in range(start, end) if referenced[offset])
        if clashing or owned_bytes or referenced_bytes:
            conflicts.append(
                f"declared free region 0x{start:06X}..0x{end:06X} overlaps "
                f"{len(clashing)} annotation(s), {owned_bytes} owned byte(s) and "
                f"{referenced_bytes} known reference target byte(s)")
        for offset in range(start, end):
            rank[offset] = _RANK[VERIFIED_FREE]

    census = scan_pointer_observations(image)
    candidate_targets, candidate_sources = census.targets, census.sources

    # --- the census: which bytes could the reviewed verifier clear? ----------
    # A byte is blocked when any check the verifier runs would fail on a window
    # containing it: it is owned or referenced, it is a candidate target, or it
    # is not the FF fill.
    runs = fill_runs(rank, candidate_targets, candidate_sources, image)

    # Clearance: a window qualifies only when the nearest candidate target on
    # each side is at least `margin` away, because a candidate that IS real
    # means some structure begins there with unknown length.
    target_positions = [i for i in range(size) if candidate_targets[i]]
    promotable = []
    for run_start, run_end in runs:
        run_start = max(run_start, 0x158)
        if run_start >= run_end:
            continue
        index = bisect.bisect_left(target_positions, run_start)
        below = target_positions[index - 1] if index else None
        above = target_positions[index] if index < len(target_positions) else None
        low = (run_start if below is None or run_start - below >= margin
               else below + margin)
        high = (run_end if above is None or above - run_end >= margin
                else above - margin)
        if high > low:
            promotable.append((low, high))

    sources_outside = sum(
        1 for reference in references
        if not (0 <= reference["source"] < size
                and rank[reference["source"]] == _RANK[OWNED]))

    regions = _regions_from_rank(rank, annotations, references, profile, size)
    model = CapacityModel(
        profile_id=profile.id,
        base_sha256=profile.sha256 or "",
        image_size=size,
        expansion_output_size=(None if profile.generated_expansion is None
                               else profile.generated_expansion.output_size),
        expansion_padding_byte=(None if profile.generated_expansion is None
                                else profile.generated_expansion.padding_byte),
        expansion_evidence=("" if profile.generated_expansion is None
                            else profile.generated_expansion.evidence),
        regions=regions,
        annotations=tuple(annotations),
        references=tuple(references),
        candidate_observation_count=census.count,
        candidate_observation_aligned_count=census.aligned_count,
        candidate_target_bytes=sum(candidate_targets),
        candidate_source_bytes=sum(candidate_sources),
        reference_sources_outside_owned=sources_outside,
        free_region_conflicts=tuple(conflicts),
        promotable_runs=tuple(promotable),
        margin=margin,
        margin_curve=extra_promotable_by_margin(
            rank, candidate_targets, candidate_sources, image,
            (0, 0x100, 0x200, 0x400, 0x800, 0x1000, 0x2000)),
    )
    model.diagnostics = {
        "margin": margin,
        "fill_runs_before_margin": len(runs),
        "annotations": len(annotations),
        "annotations_skipped_by_status": len(skipped),
        "annotations_skipped_examples": sorted(skipped)[:8],
        "region_spans": len(regions),
        "image_fill_bytes": sum(1 for byte in image if byte == 0xFF),
        "image_zero_bytes": sum(1 for byte in image if byte == 0x00),
        "census_method": (
            "same checks as tools/research/capacity_proof.verify_window: FF fill, "
            "no owned byte, no known inbound reference, no candidate target at any "
            "alignment, no candidate source, stated clearance margin from the "
            "nearest candidate target on each side"),
        "evidence_base": (
            "tools.research.free_space_audit.build_model (TOOLKIT-011 model) extended "
            "with script tables/pools, compressed-dialogue selector table and container "
            "extents, and the placement-type dispatch table"),
    }
    return model


def _regions_from_rank(rank, annotations, references, profile,
                       size) -> tuple[Region, ...]:
    """Read the painted rank array back into attributed spans.

    Spans are split at every boundary where the *evidence* changes - an
    annotation's start or end, a free declaration's start or end, or a reference
    target byte - not merely where the rank *class* changes. Splitting on class
    alone was wrong for the purpose this map exists for: two adjacent annotations
    of the same kind coalesce into one span attributed to whichever begins first,
    and a nested annotation disappears entirely, so "who owns this byte" would be
    unanswerable for most of the image. `free_space_audit.occupancy` splits on
    exactly these events for the same reason.

    Within one such interval the rank is constant (rank changes only at those
    boundaries), so each span still carries exactly one classification, and the
    partition stays exhaustive and disjoint.
    """
    free_regions = sorted(profile.free_regions, key=lambda r: r.range.start.value)
    free_starts = [r.range.start.value for r in free_regions]

    # Exact innermost attribution, as an active-set sweep.
    #
    # A bounded backward scan over annotation starts is NOT sufficient: when many
    # annotations begin between a short span and the long one enclosing it, the
    # scan can run out of lookback and report `unattributed` for bytes that ARE
    # owned - silently losing the owner while keeping the classification. The
    # sweep keeps every annotation whose start has been passed and whose end has
    # not, ordered so the greatest start (the innermost) is on top; ties go to the
    # SHORTER span, which is the more specific claim. Cost is O((spans + spans)
    # log annotations) rather than a per-byte scan.
    ordered = sorted(range(len(annotations)),
                     key=lambda index: (annotations[index].start,
                                        annotations[index].end - annotations[index].start,
                                        index))
    active: list[tuple[int, int, int, Annotation]] = []
    cursor = 0

    breaks = {0, size}
    for annotation in annotations:
        breaks.add(annotation.start)
        breaks.add(annotation.end)
    for region in free_regions:
        breaks.add(region.range.start.value)
        breaks.add(region.range.end)
    for reference in references:
        target = reference["target"]
        if 0 <= target < size:
            breaks.add(target)
            breaks.add(target + 1)
    points = sorted(point for point in breaks if 0 <= point <= size)

    def attribution(start: int):
        """The innermost annotation covering `start`, or None."""
        nonlocal cursor
        while (cursor < len(ordered)
               and annotations[ordered[cursor]].start <= start):
            annotation = annotations[ordered[cursor]]
            heapq.heappush(active, (-annotation.start,
                                    annotation.end - annotation.start,
                                    cursor, annotation))
            cursor += 1
        while active and active[0][3].end <= start:
            heapq.heappop(active)
        return active[0][3] if active else None

    def free_at(start: int):
        index = bisect.bisect_right(free_starts, start) - 1
        if index >= 0:
            region = free_regions[index]
            if region.range.start.value <= start < region.range.end:
                return region
        return None

    confidence = {OWNED: "CONFIRMED", REFERENCED: "DECLARED",
                  VERIFIED_FREE: "CONFIRMED", UNKNOWN: "UNKNOWN"}
    evidence_default = {OWNED: "production model", REFERENCED: "production model",
                        VERIFIED_FREE: "profile.free_regions", UNKNOWN: "no evidence"}
    regions = []
    for start, end in zip(points, points[1:]):
        if end <= start:
            continue
        classification = _RANK_NAMES[rank[start]]
        owner, evidence, kind = "unattributed", evidence_default[classification], ""
        annotation = attribution(start)
        if classification in (OWNED, REFERENCED) and annotation is not None:
            owner, evidence, kind = annotation.owner, annotation.source, annotation.kind
        elif classification == VERIFIED_FREE:
            region = free_at(start)
            if region is not None:
                evidence = region.evidence.strip().split()[0]
                owner = "profile.free_regions"
        elif classification == REFERENCED:
            kind = "reference_target_without_covering_structure"
        regions.append(Region(start, end, classification,
                              confidence[classification], evidence, owner, kind))
    return tuple(regions)


def fill_runs(rank, candidate_targets, candidate_sources,
              image: bytes) -> list[tuple[int, int]]:
    """Maximal runs of bytes no verifier check would fail on.

    The ONE definition of "blocked", shared by the census and the margin curve so
    a change to the policy cannot be applied to one and forgotten in the other. A
    byte is blocked when it carries any claim (`rank`), when it is a candidate
    target at any alignment, when it is the FIRST byte of a candidate
    observation, or when it is not the `FF` fill the verifier requires.

    `candidate_sources` is load-bearing and was missing from an earlier draft.
    The tempting argument - "a run is all `FF`, and `0xFFFFFFFF` is not a ROM
    address, so no pointer can start inside it" - is wrong, because only the
    FIRST byte of the word has to be inside the run. A one-byte fill pocket whose
    following bytes read `06 14 08` holds the word `0x081406FF`, a valid ROM
    pointer sourced inside the pocket; writing that byte corrupts a word some
    unknown consumer reads as a pointer. `capacity_proof.verify_window` refuses
    exactly that window on `candidate_source`, so a census without this term is a
    second, quieter standard.
    """
    size = len(image)
    blocked = bytearray(size)
    for offset in range(size):
        if (rank[offset] or candidate_targets[offset] or candidate_sources[offset]
                or image[offset] != 0xFF):
            blocked[offset] = 1
    runs = []
    start = None
    for offset in range(size):
        if blocked[offset]:
            if start is not None:
                runs.append((start, offset))
                start = None
        elif start is None:
            start = offset
    if start is not None:
        runs.append((start, size))
    return runs


def extra_promotable_by_margin(rank, candidate_targets, candidate_sources,
                               image: bytes, margins) -> dict:
    """How much the stated clearance margin alone is costing.

    One sweep of runs, several margins. The margin is a *policy* number, not a
    measurement: it exists because an unresolved candidate that IS real means a
    structure begins there with unknown length. Reporting the curve stops a
    reader mistaking "23 KB promotable" for a property of the ROM rather than a
    property of the policy at 1 KiB.
    """
    size = len(image)
    runs = fill_runs(rank, candidate_targets, candidate_sources, image)
    positions = [i for i in range(size) if candidate_targets[i]]
    result = {}
    for margin in margins:
        total = 0
        count = 0
        for run_start, run_end in runs:
            run_start = max(run_start, 0x158)
            if run_start >= run_end:
                continue
            index = bisect.bisect_left(positions, run_start)
            below = positions[index - 1] if index else None
            above = positions[index] if index < len(positions) else None
            low = (run_start if below is None or run_start - below >= margin
                   else below + margin)
            high = (run_end if above is None or above - run_end >= margin
                    else above - margin)
            if high > low:
                total += high - low
                count += 1
        result[str(margin)] = {"bytes": total, "runs": count}
    return result


# --- measured resource-size distributions -----------------------------------


def _distribution(sizes) -> dict:
    ordered = sorted(sizes)
    if not ordered:
        return {"count": 0}
    return {
        "count": len(ordered),
        "min": ordered[0],
        "median": ordered[len(ordered) // 2],
        "p90": ordered[min(len(ordered) - 1, int(len(ordered) * 0.9))],
        "max": ordered[-1],
        "mean": round(sum(ordered) / len(ordered), 2),
        "total": sum(ordered),
    }


def resource_distributions(rom_path, catalog_path=None) -> dict:
    """Real observed sizes of each authored resource class, from the image.

    Capacity scenarios have to be arithmetic on measured distributions rather
    than on "one megabyte is N maps". Every number here is counted from the
    canonical bytes by the same production readers the allocator will feed, so a
    scenario built on it can be recomputed instead of believed.

    Classes whose extents only exist per-map (a whole new map's graphics
    footprint) are deliberately NOT guessed at: what is measurable is reported,
    and the report states the composition instead of inventing an average.
    """
    from tools.webfoot import graphics
    from tools.webfoot.entities import load_placement_types
    from tools.webfoot.layout import RomRange
    from tools.webfoot.binary import FileOffset

    catalog = RomProfileCatalog.load(
        catalog_path or Path(__file__).resolve().parents[1] / "webfoot/data/roms.yaml")
    identification = identify_rom(rom_path, catalog)
    profile = identification.profile_match.profile
    image = Path(rom_path).read_bytes()
    size = len(image)

    result: dict[str, dict] = {}

    # MapEntry records and the per-map structures they own.
    table = profile.map_entries
    result["map_entry_record_bytes"] = {"fixed": table.record_size, "count": table.count}

    types = load_placement_types(rom_path, catalog)
    maps = types.maps
    result["map_slot_array_bytes"] = _distribution(
        [len(a.array.original_bytes) for a in maps.slot_arrays()])
    result["placement_record_bytes"] = _distribution(
        [len(p.original_bytes) for p in maps.placements()])
    result["map_object_slot_bytes"] = {
        "slot_bytes": 4,
        "slots": sum(len(a.array.original_bytes) // 4 for a in maps.slot_arrays()),
    }
    entry_rows = list(maps.entries())
    result["map_objects_per_map"] = _distribution(
        [len(list(maps.map_placements(row.identity))) for row in entry_rows])

    # Actor sprite graphics containers: packed and decoded.
    sprites = graphics.load_actor_sprites(image, identification)
    containers = list(sprites.graphics())
    result["graphics_container_packed_bytes"] = _distribution(
        [c.packed_size for c in containers])
    result["graphics_container_decoded_bytes"] = _distribution(
        [len(c.pixels) for c in containers])

    # Text: every string body's byte length, measured by walking the verified
    # pointer table rather than by dividing the pool by the entry count.
    text = profile.text_strings
    if text is not None:
        table_offset = text.pointer_table_address.to_file_offset(size)
        pool_offset = text.pool_address.to_file_offset(size)
        bodies = sorted({int.from_bytes(
            image[table_offset + 4 * i:table_offset + 4 * i + 4], "little") - GBA_ROM_BASE
            for i in range(text.count)})
        lengths = []
        for index, body in enumerate(bodies):
            end = bodies[index + 1] if index + 1 < len(bodies) else pool_offset + text.pool_size
            if 0 <= body < end <= size:
                lengths.append(end - body)
        result["text_string_bytes"] = _distribution(lengths)

    # Script corpora: pool extents and the record tables that own them.
    for script in profile.scripts or ():
        result[f"script_pool_bytes[{script.family}]"] = {
            "pool_size": script.pool_size,
            "table_bytes": script.count * script.stride,
            "record_stride": script.stride,
            "records": script.count,
            "slot_count": len(script.slots),
        }

    # Dialogue: the packed containers the selector table names, read through the
    # SAME validated reader the annotation walk uses, so the two cannot disagree
    # about the table or about how strictly they check it.
    from tools.webfoot.formats.webfoot_lz import unpack

    packed, decoded = [], []
    for offset in dialogue_selector_offsets(image):
        container = unpack(image, offset)
        packed.append(container.packed_size)
        decoded.append(len(container.data))
    result["dialogue_container_packed_bytes"] = _distribution(packed)
    result["dialogue_container_decoded_bytes"] = _distribution(decoded)
    result["dialogue_selector_table_bytes"] = {"fixed": 4 * DIALOGUE_SELECTOR_COUNT,
                                               "selectors": DIALOGUE_SELECTOR_COUNT}

    return {"profile_id": profile.id, "base_sha256": profile.sha256,
            "measured": result}


# --- geometry ---------------------------------------------------------------


def _aligned_capacity(start: int, end: int, alignment: int) -> int:
    """Bytes usable from ``[start, end)`` when every block must be aligned.

    The first aligned address at or after ``start`` is the only place a block
    may begin, so the loss is the head slack plus the tail remainder - a real
    loss, not a rounding convenience.
    """
    first = ((start + alignment - 1) // alignment) * alignment
    return max(0, (end - first) // alignment * alignment)


def span_statistics(spans) -> dict:
    """Count, size distribution, fragmentation and alignment cost of spans."""
    ordered = sorted(((s, e) for s, e in spans), key=lambda span: span[0])
    sizes = sorted((e - s for s, e in ordered), reverse=True)
    aligned4 = sum(_aligned_capacity(s, e, 4) for s, e in ordered)
    return {
        "count": len(sizes),
        "total_bytes": sum(sizes),
        "largest": sizes[:16],
        "median_bytes": (sizes[len(sizes) // 2] if sizes else 0),
        "smallest_bytes": (sizes[-1] if sizes else 0),
        "aligned_4_bytes": aligned4,
        "aligned_4_block32_bytes": sum(
            _aligned_capacity(s, e, 4) // 32 * 32 for s, e in ordered),
        "aligned_4_block256_bytes": sum(
            _aligned_capacity(s, e, 4) // 256 * 256 for s, e in ordered),
        "aligned_4_block1024_bytes": sum(
            _aligned_capacity(s, e, 4) // 1024 * 1024 for s, e in ordered),
        "spans_below_32_bytes": sum(1 for size in sizes if size < 32),
        "bytes_in_spans_below_32_bytes": sum(size for size in sizes if size < 32),
    }


# --- cross-checks -----------------------------------------------------------


def census_agrees_with_verifier(model: CapacityModel, image: bytes) -> dict:
    """Re-run the reviewed verifier on EVERY census run; all must accept.

    A census that cannot be reproduced by the procedure it claims to mirror
    would be a second, silently different standard. The model's real annotations
    and references are passed, so the known-overlap and known-inbound checks are
    exercised rather than vacuous.

    The observation set for each window is filtered to targets within ``margin``
    of that window plus every source starting inside it, which is exactly the
    input the verifier's checks read; anything further away cannot change its
    verdict. Targets and sources are pre-indexed once so every run can be checked
    without rescanning the image.

    EVERY run is checked, not just the largest. An earlier version verified only
    the largest run, and that is precisely why a census missing the
    `candidate_source` term shipped: the largest window happened to be clean while
    a one-byte window elsewhere was not.
    """
    from tools.research.capacity_proof import verify_window

    if not model.promotable_runs:
        return {"available": False, "runs": 0, "rejected": [], "verdict": None}
    margin = model.margin
    owned_rows = [{"start": a.start, "end": a.end, "kind": a.kind, "owner": a.owner,
                   "status": a.status} for a in model.annotations]

    by_target: dict[int, list[dict]] = {}
    by_source: dict[int, dict] = {}
    unpack = _POINTER.unpack_from
    limit = GBA_ROM_BASE + len(image)
    for source in range(len(image) - 3):
        raw = unpack(image, source)[0]
        if not GBA_ROM_BASE <= raw < limit:
            continue
        observation = {"source": source, "target": raw - GBA_ROM_BASE,
                       "source_word_aligned": source % 4 == 0}
        by_target.setdefault(observation["target"], []).append(observation)
        by_source[source] = observation
    targets_sorted = sorted(by_target)

    rejected = []
    failed_check_counts: dict[str, int] = {}
    last_checks: dict[str, bool] = {}
    for start, end in model.promotable_runs:
        lo = bisect.bisect_left(targets_sorted, start - margin)
        hi = bisect.bisect_left(targets_sorted, end + margin)
        observations = [obs for target in targets_sorted[lo:hi]
                        for obs in by_target[target]]
        observations.extend(obs for source, obs in by_source.items()
                            if start <= source < end)
        verdict = verify_window(image, RomRange(FileOffset(start), end - start),
                                observations=observations, owned=owned_rows,
                                references=list(model.references), margin=margin)
        last_checks = {name: check["pass"] for name, check in verdict["checks"].items()}
        if verdict["verdict"] != "VERIFIED":
            rejected.append({"start": start, "end": end, "size": end - start,
                             "failed_checks": verdict["failed_checks"]})
            for name in verdict["failed_checks"]:
                failed_check_counts[name] = failed_check_counts.get(name, 0) + 1
    largest = max(model.promotable_runs, key=lambda run: (run[1] - run[0], -run[0]))
    return {"available": True,
            "runs": len(model.promotable_runs),
            "runs_verified": len(model.promotable_runs) - len(rejected),
            "rejected": rejected,
            "largest": {"start": largest[0], "end": largest[1],
                        "size": largest[1] - largest[0]},
            "verdict": "VERIFIED" if not rejected else "REJECTED",
            # Both fields are MEASURED, not synthesised: `checks` is the last
            # run's own per-check results and `failed_check_counts` counts the
            # checks that actually failed, per name, across all runs. A caller
            # must not read an all-True `checks` as proof that every run passed -
            # `verdict` and `rejected` are that proof.
            "checks": last_checks,
            "failed_check_counts": failed_check_counts}


def require_consistent(model: CapacityModel) -> CapacityModel:
    """Refuse a model whose declared free space overlaps measured content.

    :func:`build_region_map` reports such a conflict in `free_region_conflicts`
    rather than hiding it, because a diagnostic is more useful than an exception
    while investigating. But a model carrying one must never be *used*: the free
    declaration would have overwritten owned bytes in the partition, so every
    capacity figure derived from it - free bytes, promotable census, alignment
    totals - is wrong in the unsafe direction. This is the fail-closed gate the
    ticket's "never place new content inside OWNED or REFERENCED" rule needs, and
    `audit` applies it so no caller can forget.
    """
    if model.free_region_conflicts:
        raise ValueError(
            "capacity model is unusable: " + "; ".join(model.free_region_conflicts))
    return model


def audit_image(image: bytes, owned, references, profile: RomProfile, *,
                margin: int = 0x400) -> CapacityModel:
    """Build the model for already-loaded bytes and refuse an unusable one.

    Split out from :func:`audit` so the fail-closed wiring is testable without a
    ROM: this function is where `require_consistent` is applied, so a synthetic
    image with a conflicting free declaration must raise through exactly the path
    the canonical audit takes.
    """
    capacity = build_region_map(image, owned, references, profile, margin=margin)
    if capacity.base_sha256 != profile.sha256:
        raise ValueError("model identity does not match the verified profile")
    return require_consistent(capacity)


def audit(rom_path, *, catalog_path=None, margin: int = 0x400) -> CapacityModel:
    """Full Phase A measurement for one canonical image."""
    catalog = RomProfileCatalog.load(
        catalog_path or Path(__file__).resolve().parents[1] / "webfoot/data/roms.yaml")
    identification = identify_rom(rom_path, catalog)
    profile = identification.profile_match.profile
    if (identification.profile_match.status is not VerificationStatus.VERIFIED
            or profile is None):
        raise ValueError("capacity model requires an exactly verified profile image")
    image = Path(rom_path).read_bytes()
    if len(image) != profile.size:
        raise ValueError("image size does not match the verified profile")
    model, owned, references, resolved = load_production_evidence(
        rom_path, catalog_path=catalog_path)
    if resolved.sha256 != profile.sha256:
        raise ValueError("profile changed while the model was built")
    return audit_image(image, owned, references, profile, margin=margin)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("--catalog", type=Path, default=None)
    parser.add_argument("--margin", type=lambda v: int(v, 0), default=0x400)
    parser.add_argument("--regions", type=Path, default=None,
                        help="write the machine-readable region map here (JSONL)")
    parser.add_argument("--summary", type=Path, default=None,
                        help="write the accounting summary here (JSON)")
    parser.add_argument("--census-check", action="store_true",
                        help="re-run the reviewed window verifier on a census run")
    parser.add_argument("--resources", action="store_true",
                        help="also measure the authored resource-size distributions")
    args = parser.parse_args(argv)

    model = audit(args.rom, catalog_path=args.catalog, margin=args.margin)
    report = model.to_json()
    if args.resources:
        report["resource_distributions"] = resource_distributions(
            args.rom, catalog_path=args.catalog)
    if args.regions is not None:
        args.regions.parent.mkdir(parents=True, exist_ok=True)
        args.regions.write_text("\n".join(model.region_map_lines()) + "\n",
                                encoding="utf-8", newline="\n")
        report["region_map_path"] = str(args.regions)
        report["region_map_spans"] = len(model.regions)
    if args.census_check:
        report["census_check"] = census_agrees_with_verifier(
            model, Path(args.rom).read_bytes())
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
