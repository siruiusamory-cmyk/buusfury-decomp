"""ROM-ATLAS-001 assembler: loose evidence artifacts -> one validated `Atlas`.

Seven discovery passes each wrote a JSONL artifact under `build/atlas/`. None of
them merged, so "what is at this offset" was still unanswerable. This module is
the merge, and it is deliberately a single non-quadratic pass:

`CoverageMap.refine` rebuilds the whole span tuple per call (atlas.py:235), so
calling it once per artifact row would be O(rows * spans). Instead every claim is
reduced to a (start, end, classification, confidence, evidence) tuple, the claims
are painted weakest-first onto one byte-interval sweep, and the resulting span
list is handed to `CoverageMap` directly. `refine`'s anti-downgrade rule
(atlas.py:229) is honoured by the paint order rather than by catching its error:
a stronger claim already on a byte is never repainted by a weaker one, and an
equal-strength claim of a different classification is recorded as a CONFLICT and
resolved by provenance specificity rather than by whichever ran last.
"""

from __future__ import annotations

from array import array
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable, Iterator, Sequence

from .atlas import (Atlas, AtlasObject, AtlasReference, Confidence, CoverageMap,
                    CoverageSpan, Observation, PADDING_CANDIDATE, UNKNOWN,
                    VERIFIED_FREE, strength)
from .binary import FileOffset, GBA_ROM_BASE
from .layout import LayoutError, Provenance, ReferenceEncoding, RomRange


#: The canonical Buu's Fury image the artifacts were measured against. The
#: assembler refuses to stamp any other identity onto their provenance.
PROFILE_ID = "buus_fury_usa_rev0_01c1707f"
BASE_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
IMAGE_SIZE = 8_388_608

#: The ONE region a ticket has proven free (config/roms.yaml, TOOLKIT-028).
#: Anything else claiming VERIFIED_FREE is demoted, because "looks like fill" is
#: not a proof of freedom.
VERIFIED_FREE_OFFSET = 0x007EA400
VERIFIED_FREE_SIZE = 256

ARTIFACTS = ("seed_knowledge", "graphics_extents", "code_functions", "code_regions",
             "scan_text", "scan_pointers", "scan_pointer_tables", "scan_entropy",
             "scan_compression", "scan_code_shape")

#: One stable evidence string per pass. `Provenance.evidence` is part of a span's
#: coalescing key (atlas.py:143), so a per-row string would defeat `_coalesce`
#: and leave tens of thousands of one-row spans.
EVIDENCE = {
    "entropy": "scan_entropy.jsonl: per-block entropy classification",
    "code_shape": "scan_code_shape.jsonl: per-block Thumb code-shape density",
    "code_region": "code_regions.jsonl: recursive Thumb traversal classification",
    "graphics": "graphics_extents.jsonl: load_actor_sprites container walk",
    "seed": "seed_knowledge.jsonl: structures proven by prior tickets",
    "base": "ROM-ATLAS-001 assembly: no pass has classified these bytes",
}


class AtlasBuildError(ValueError):
    """An artifact cannot be assembled into a justified atlas."""


@dataclass(frozen=True, slots=True)
class Conflict:
    """Two equal-strength claims disagreeing about the same bytes.

    Recorded rather than resolved silently: the winner is the more specific
    provenance, and the loser stays visible so a later ticket can arbitrate.
    """

    start: int
    end: int
    kept: str
    kept_evidence: str
    dropped: str
    dropped_evidence: str
    confidence: str

    def to_json(self) -> dict:
        return {"file_offset": self.start, "size": self.end - self.start,
                "confidence": self.confidence, "kept": self.kept,
                "kept_evidence": self.kept_evidence, "dropped": self.dropped,
                "dropped_evidence": self.dropped_evidence}


@dataclass(frozen=True, slots=True)
class BuildReport:
    atlas: Atlas
    conflicts: tuple[Conflict, ...]
    rows_read: tuple[tuple[str, int], ...]


# --- artifact loading --------------------------------------------------------


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise AtlasBuildError(f"missing artifact {path}")
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_artifacts(directory: Path) -> dict[str, list[dict]]:
    """Read exactly the named artifacts. Files another agent adds are ignored."""
    return {name: _read_jsonl(directory / f"{name}.jsonl") for name in ARTIFACTS}


# --- Layer A: coverage -------------------------------------------------------

#: A coverage claim, flattened out of whatever artifact produced it.
Claim = tuple[int, int, str, Confidence, str]  # start, end, classification, confidence, evidence


#: Provenance specificity, used only to break an equal-strength tie. A seed cites
#: a ticket and a document line; a whole-block scanner cites a heuristic.
_SPECIFICITY = {EVIDENCE["seed"]: 5, EVIDENCE["graphics"]: 4, EVIDENCE["code_region"]: 3,
                EVIDENCE["code_shape"]: 2, EVIDENCE["entropy"]: 1, EVIDENCE["base"]: 0}


def _clip(start: int, size: int) -> tuple[int, int] | None:
    """Clip a claim to the image, refusing sizes `RomRange` would reject."""
    if not isinstance(start, int) or not isinstance(size, int):
        return None
    end = min(start + size, IMAGE_SIZE)
    start = max(start, 0)
    return (start, end) if end > start else None


def _confidence(value: str, cap: Confidence | None = None) -> Confidence:
    confidence = Confidence(value)
    if cap is not None and strength(confidence) > strength(cap):
        return cap
    return confidence


def _entropy_claims(rows: Iterable[dict]) -> Iterator[Claim]:
    # Only the 4 KiB grid: the 1 KiB rows cover the same bytes, and two grids
    # would be two equal-strength claims per byte for no added information.
    for row in rows:
        if row.get("block_size") != 4096:
            continue
        clipped = _clip(row["file_offset"], row["size"])
        if clipped is None:
            continue
        name = row["suggested_class"]
        # PADDING_CANDIDATE is a shape, never freedom: only the TOOLKIT-028
        # window may claim VERIFIED_FREE, and it arrives through the seeds.
        if name == VERIFIED_FREE:
            name = PADDING_CANDIDATE
        yield (*clipped, name, Confidence.OBSERVED, EVIDENCE["entropy"])


def _code_shape_claims(rows: Iterable[dict]) -> Iterator[Claim]:
    for row in rows:
        if row["suggested_class"] == UNKNOWN:
            continue  # nothing added over the entropy grid
        clipped = _clip(row["file_offset"], row["size"])
        if clipped is not None:
            yield (*clipped, row["suggested_class"], Confidence.OBSERVED,
                   EVIDENCE["code_shape"])


def _code_region_claims(rows: Iterable[dict]) -> Iterator[Claim]:
    for row in rows:
        clipped = _clip(row["file_offset"], row["size"])
        if clipped is not None:
            yield (*clipped, row["classification"],
                   _confidence(row["confidence"], Confidence.INFERRED),
                   EVIDENCE["code_region"])


def _graphics_claims(rows: Iterable[dict]) -> Iterator[Claim]:
    for row in rows:
        clipped = _clip(row["file_offset"], row["size"])
        if clipped is not None:
            yield (*clipped, row["kind"], _confidence(row["confidence"]),
                   EVIDENCE["graphics"])


def _seed_claims(rows: Iterable[dict]) -> Iterator[Claim]:
    for row in rows:
        if row.get("size") is None:
            continue  # no justified extent; it still becomes an object
        clipped = _clip(row["file_offset"], row["size"])
        if clipped is None:
            continue
        kind = row["kind"]
        if kind == "free_region" and (row["file_offset"], row["size"]) != (
                VERIFIED_FREE_OFFSET, VERIFIED_FREE_SIZE):
            raise AtlasBuildError(
                f"unexpected free_region at 0x{row['file_offset']:X}; only the "
                f"TOOLKIT-028 window may claim {VERIFIED_FREE}")
        if kind == "free_region":
            kind = VERIFIED_FREE
        yield (*clipped, kind, _confidence(row["confidence"]), EVIDENCE["seed"])


def _paint(claims: Sequence[Claim]) -> tuple[list[CoverageSpan], list[Conflict]]:
    """Paint claims weakest-first onto one per-byte sweep.

    Linear in painted bytes rather than the O(rows * spans) a `refine` loop
    costs, and the weakest-first order is what keeps `refine`'s anti-downgrade
    rule satisfied: nothing ever repaints a stronger byte.

    Deliberately an 8 MiB `array` of palette codes, painted by flat slice
    assignment. An interval tree would only earn its complexity if the image
    grew large enough for the memory to matter; at 8 MiB a flat array is
    simpler and fast enough.
    """
    palette: list[tuple[str, Confidence, str]] = [(UNKNOWN, Confidence.UNKNOWN,
                                                   EVIDENCE["base"])]
    code_of: dict[tuple[str, Confidence, str], int] = {palette[0]: 0}
    owners = array("H", bytes(IMAGE_SIZE * 2))  # palette code per byte
    conflicts: list[Conflict] = []

    def intern(entry: tuple[str, Confidence, str]) -> int:
        code = code_of.get(entry)
        if code is None:
            code = len(palette)
            if code > 0xFFFF:
                raise AtlasBuildError("more than 65536 distinct coverage claims")
            code_of[entry] = code
            palette.append(entry)
        return code

    ordered = sorted(claims, key=lambda c: (strength(c[3]), c[0], c[1]))
    for start, end, classification, confidence, evidence in ordered:
        incoming = (classification, confidence, evidence)
        incoming_code = intern(incoming)
        incoming_rank = _SPECIFICITY.get(evidence, 0)
        cursor = start
        while cursor < end:
            held_code = owners[cursor]
            run = cursor + 1
            while run < end and owners[run] == held_code:
                run += 1
            held = palette[held_code]
            if strength(held[1]) > strength(confidence):
                cursor = run  # anti-downgrade: a stronger claim already owns it
                continue
            if (strength(held[1]) == strength(confidence)
                    and held[0] != classification
                    and held[1] is not Confidence.UNKNOWN):
                held_rank = _SPECIFICITY.get(held[2], 0)
                winner, loser = ((incoming, held) if incoming_rank > held_rank
                                 else (held, incoming))
                conflicts.append(Conflict(cursor, run, winner[0], winner[2],
                                          loser[0], loser[2], confidence.value))
                owners[cursor:run] = array("H", [intern(winner)]) * (run - cursor)
            else:
                owners[cursor:run] = array("H", [incoming_code]) * (run - cursor)
            cursor = run

    # A span boundary can only fall on a claim edge, so only those need checking
    # instead of all 8,388,608 byte positions.
    edges = sorted({0, IMAGE_SIZE} | {c[0] for c in claims} | {c[1] for c in claims})
    spans: list[CoverageSpan] = []
    start, held_code = 0, owners[0]
    for edge in edges:
        if edge <= start or edge > IMAGE_SIZE:
            continue
        code = owners[edge] if edge < IMAGE_SIZE else -1
        if code != held_code:
            classification, confidence, evidence = palette[held_code]
            spans.append(CoverageSpan(
                RomRange(FileOffset(start), edge - start), classification, confidence,
                Provenance(PROFILE_ID, BASE_SHA256, evidence)))
            start, held_code = edge, code
    return spans, conflicts


def _coalesced(spans: Sequence[CoverageSpan]) -> tuple[CoverageSpan, ...]:
    merged: list[CoverageSpan] = []
    for span in spans:
        if merged and merged[-1]._key == span._key:
            previous = merged.pop()
            span = CoverageSpan(
                RomRange(previous.range.start, previous.range.size + span.range.size),
                span.classification, span.confidence, span.provenance)
        merged.append(span)
    return tuple(merged)


# --- Layers B, C, D ----------------------------------------------------------


def _proof(evidence: str) -> Provenance:
    return Provenance(PROFILE_ID, BASE_SHA256, evidence)


def _object(identity: str, start: int, size: int, kind: str, confidence: Confidence,
            evidence: str, attributes: Sequence[tuple[str, str]] = ()) -> AtlasObject | None:
    clipped = _clip(start, size)
    if clipped is None:
        return None
    try:
        return AtlasObject(identity, RomRange(FileOffset(clipped[0]), clipped[1] - clipped[0]),
                           kind, confidence, _proof(evidence),
                           tuple(sorted(attributes)))
    except (ValueError, LayoutError):
        return None


def _objects(artifacts: dict[str, list[dict]], shop: dict | None) -> tuple[AtlasObject, ...]:
    found: list[AtlasObject] = []
    seen: set[str] = set()

    def add(object: AtlasObject | None) -> None:
        if object is not None and object.identity not in seen:
            seen.add(object.identity)
            found.append(object)

    for row in artifacts["seed_knowledge"]:
        # A seed with no justified extent is still a located thing; it gets a
        # one-byte marker object and an attribute saying the extent is unknown.
        size = row["size"] if row["size"] else 1
        add(_object(f"seed:{row['identity']}", row["file_offset"], size, row["kind"],
                    _confidence(row["confidence"]), EVIDENCE["seed"],
                    (("extent", "measured" if row["size"] else "unknown"),
                     ("source", str(row["source"])))))

    for row in artifacts["graphics_extents"]:
        add(_object(f"graphics:{row['identity']}", row["file_offset"], row["size"],
                    row["kind"], _confidence(row["confidence"]), EVIDENCE["graphics"],
                    (("decoded_size", str(row["decoded_size"])),
                     ("reachable_from", str(row["reachable_from"])))))

    for row in artifacts["code_functions"]:
        size = row["size"] if row.get("size") else 1
        add(_object(f"function:{row['identity']}", row["file_offset"], size, "function",
                    _confidence(row["confidence"], Confidence.INFERRED),
                    "code_functions.jsonl: recursive Thumb traversal",
                    (("extent", "measured" if row.get("size") else "unknown"),
                     ("fetch_address", str(row["fetch_address"])),
                     ("thumb", str(row["thumb"])))))

    for row in artifacts["scan_pointer_tables"]:
        add(_object(f"pointer-table-candidate:{row['file_offset']:08X}", row["file_offset"],
                    row["size"], "pointer-table-candidate", Confidence.CANDIDATE,
                    "scan_pointer_tables.jsonl: aligned in-range u32 run of >= 8",
                    (("entry_count", str(row["entry_count"])),
                     ("stride", str(row["stride"])))))

    # Text runs are clustered by the scanner; one object per cluster, spanning
    # its first byte to its last, is the useful located unit.
    clusters: dict[int, list[dict]] = {}
    for row in artifacts["scan_text"]:
        clusters.setdefault(row["cluster_id"], []).append(row)
    for cluster_id, rows in clusters.items():
        start = min(r["file_offset"] for r in rows)
        end = max(r["file_offset"] + r["size"] for r in rows)
        add(_object(f"text-cluster:{cluster_id:05d}", start, end - start, "text-run-cluster",
                    Confidence.CANDIDATE, "scan_text.jsonl: clustered UTF-16/ASCII runs",
                    (("encodings", ",".join(sorted({r["encoding"] for r in rows}))),
                     ("run_count", str(len(rows))))))

    if shop is not None:
        region = shop.get("declared_region") or {}
        start = region.get("file_offset", 0x0077F09A)
        end = region.get("end_file_offset", 0x007801D4)
        add(_object("shop-dialogue:declared-region", start, end - start, "dialogue_store",
                    Confidence.INFERRED,
                    "shop_dialogue_ownership.json: per-record pointer arrays name these bodies",
                    (("verdict", str(shop.get("conclusion", {}).get("verdict", "UNKNOWN"))),)))
    return tuple(found)


def _references(rows: Iterable[dict]) -> tuple[AtlasReference, ...]:
    # CANDIDATE and no higher: a pointer-shaped aligned word is a numeric
    # coincidence until something proves the engine follows it (docs/DEVELOPMENT.md:153).
    proof = _proof("scan_pointers.jsonl: aligned in-range u32 pointer candidate")
    found = []
    for row in rows:
        source, target = row["source_file_offset"], row["target_file_offset"]
        if not (0 <= source + 4 <= IMAGE_SIZE and 0 <= target < IMAGE_SIZE):
            continue
        found.append(AtlasReference(FileOffset(source), FileOffset(target), 4,
                                    ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                                    Confidence.CANDIDATE, proof))
    return tuple(found)


def _observations(artifacts: dict[str, list[dict]]) -> tuple[Observation, ...]:
    found: list[Observation] = []

    def add(start: int, size: int, kind: str, detail: str, confidence: Confidence,
            evidence: str) -> None:
        clipped = _clip(start, size)
        if clipped is None or not detail.strip():
            return
        found.append(Observation(
            RomRange(FileOffset(clipped[0]), clipped[1] - clipped[0]), kind, detail,
            confidence, _proof(evidence)))

    for row in artifacts["scan_text"]:
        add(row["file_offset"], row["size"], f"text-run-{row['encoding']}",
            row["prefix"], Confidence.CANDIDATE,
            "scan_text.jsonl: decoded run (prefix truncated at 40 characters)")
    for row in artifacts["scan_entropy"]:
        add(row["file_offset"], row["size"], f"entropy-block-{row['block_size']}",
            f"{row['entropy_bits']} bits, {row['distinct_bytes']} distinct",
            Confidence.OBSERVED, EVIDENCE["entropy"])
    for row in artifacts["scan_compression"]:
        add(row["file_offset"], row["packed_size"], "lz-container-probe",
            f"decoded {row['actual_decoded_size']} bytes, "
            f"round_trip={row['round_trip_ok']}", Confidence.CANDIDATE,
            "scan_compression.jsonl: LZ container probe")
    for row in artifacts["scan_code_shape"]:
        add(row["file_offset"], row["size"], "code-shape-block",
            f"score {row['code_shape_score']}, {row['bl_count']} bl, "
            f"{row['prologue_count']} prologues", Confidence.OBSERVED,
            EVIDENCE["code_shape"])
    return tuple(found)


# --- assembly ----------------------------------------------------------------


def build_atlas(directory: Path) -> BuildReport:
    """Assemble every artifact under `directory` into one validated `Atlas`."""
    artifacts = load_artifacts(directory)
    shop_path = directory / "shop_dialogue_ownership.json"
    shop = json.loads(shop_path.read_text(encoding="utf-8")) if shop_path.is_file() else None

    claims: list[Claim] = []
    claims.extend(_entropy_claims(artifacts["scan_entropy"]))
    claims.extend(_code_shape_claims(artifacts["scan_code_shape"]))
    claims.extend(_code_region_claims(artifacts["code_regions"]))
    claims.extend(_graphics_claims(artifacts["graphics_extents"]))
    claims.extend(_seed_claims(artifacts["seed_knowledge"]))

    spans, conflicts = _paint(claims)
    coverage = CoverageMap(_coalesced(spans), IMAGE_SIZE)
    coverage.validate()

    atlas = Atlas(PROFILE_ID, BASE_SHA256, IMAGE_SIZE, coverage,
                  _objects(artifacts, shop), _references(artifacts["scan_pointers"]),
                  _observations(artifacts))
    atlas.validate()
    rows_read = tuple((name, len(rows)) for name, rows in artifacts.items())
    return BuildReport(atlas, tuple(conflicts), rows_read)


def write_atlas(report: BuildReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.writelines(report.atlas.to_jsonl_lines())


def load_atlas(path: Path) -> Atlas:
    with path.open(encoding="utf-8") as handle:
        return Atlas.from_jsonl_lines(handle)


def parse_offset(text: str) -> tuple[int, str]:
    """Parse an offset, reporting which address space it was read in.

    A bare number in the GBA ROM window is converted, and the caller is told, so
    a number is never silently read in the wrong space (docs/DEVELOPMENT.md:108).
    """
    value = int(text, 0)
    if value >= GBA_ROM_BASE:
        offset = value - GBA_ROM_BASE
        if offset >= IMAGE_SIZE:
            raise AtlasBuildError(f"GBA address {text} is outside an {IMAGE_SIZE}-byte image")
        return offset, f"read 0x{value:08X} as a GBA ROM address -> file offset 0x{offset:06X}"
    if value < 0 or value >= IMAGE_SIZE:
        raise AtlasBuildError(f"file offset {text} is outside an {IMAGE_SIZE}-byte image")
    return value, f"read {text} as a file offset 0x{value:06X}"


def coverage_statistics(atlas: Atlas) -> dict:
    """Bytes and percent per confidence level and per classification."""
    by_confidence: dict[str, int] = {}
    by_classification: dict[str, int] = {}
    for span in atlas.coverage.spans:
        by_confidence[span.confidence.value] = (
            by_confidence.get(span.confidence.value, 0) + span.range.size)
        by_classification[span.classification] = (
            by_classification.get(span.classification, 0) + span.range.size)

    def table(counts: dict[str, int]) -> list[dict]:
        return [{"name": name, "bytes": total,
                 "percent": round(total * 100 / atlas.image_size, 4)}
                for name, total in sorted(counts.items(), key=lambda i: -i[1])]

    return {"image_size": atlas.image_size, "spans": len(atlas.coverage.spans),
            "objects": len(atlas.objects), "references": len(atlas.references),
            "observations": len(atlas.observations),
            "by_confidence": table(by_confidence),
            "by_classification": table(by_classification)}
