"""Data model for the independent ROM map and the candidate function inventory.

Two artefacts are produced by analysis.py and consumed by everything else:

  config/rom_map.json    a complete, non-overlapping tiling of the cartridge
  config/functions.json  candidate function entry points with discovery evidence

The model enforces the invariants the ticket requires rather than trusting the
analyser to get them right: tiling, address conversion and length arithmetic are
all validated on load and on write.

CONFIDENCE
    proven   direct, unambiguous evidence (a valid header field, a decoded
             branch target, a compressed stream that self-declares its length
             and reproduces, a structure that tiles exhaustively)
    high     several independent signals agree, or one very strong one
    medium   one strong signal, boundaries approximate
    low      heuristic only (entropy / pattern shape)
    unknown  no defensible evidence; recorded so the byte is accounted for
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from . import gba

CONFIDENCE_LEVELS = ("proven", "high", "medium", "low", "unknown")

#: Ordered strongest-first so that merging can take the weaker of two.
CONFIDENCE_RANK = {level: index for index, level in enumerate(CONFIDENCE_LEVELS)}

#: Top-level classifications actually used. Deliberately small: a classification
#: that no evidence supports is not offered, so it cannot be reached by accident.
CLASSIFICATIONS = (
    "header",             # the GBA cartridge header
    "code",               # executable code, ISA established by evidence
    "code_candidate",     # executable-looking, ISA or boundary uncertain
    "library_data",       # compiler/runtime data (armlib): error strings, tables
    "strings",            # a text pool
    "pointer_table",      # an array of code/data pointers
    "palette",            # 15-bit GBA palette data
    "lookup_table",       # a fixed-stride numeric table
    "structured_data",    # a record structure whose fields are partly established
    "compressed_asset",   # a self-describing compressed stream
    "padding",            # a constant fill run
    "unknown",            # byte-accounted, no semantic claim
)

#: What the build does with a region today.
REPRESENTATIONS = (
    "generated",   # rebuilt from project-owned source/config, byte-exact
    "reproduced",  # rebuilt from a source asset, byte-exact
    "incbin",      # copied verbatim from the baserom
    "derived",     # read directly out of the baserom by the analyser
)

EXECUTABLE_STATES = ("confirmed", "probable", "possible", "none", "unknown")


class RomMapError(RuntimeError):
    """Raised when a ROM map violates a structural invariant."""


def _hex(value: int) -> str:
    return f"0x{value:06X}"


@dataclasses.dataclass
class Region:
    id: str
    start: int
    end: int
    classification: str
    confidence: str
    evidence: list[str] = dataclasses.field(default_factory=list)
    provenance: str = ""
    notes: str = ""
    representation: str = "derived"
    isa: str | None = None
    executable: str = "unknown"

    def __post_init__(self) -> None:
        if self.classification not in CLASSIFICATIONS:
            raise RomMapError(
                f"region {self.id}: unknown classification {self.classification!r}"
            )
        if self.confidence not in CONFIDENCE_LEVELS:
            raise RomMapError(f"region {self.id}: unknown confidence {self.confidence!r}")
        if self.representation not in REPRESENTATIONS:
            raise RomMapError(
                f"region {self.id}: unknown representation {self.representation!r}"
            )
        if self.executable not in EXECUTABLE_STATES:
            raise RomMapError(f"region {self.id}: unknown executable state {self.executable!r}")
        if self.end <= self.start:
            raise RomMapError(
                f"region {self.id}: end {_hex(self.end)} is not after start {_hex(self.start)}"
            )

    @property
    def length(self) -> int:
        return self.end - self.start

    @property
    def address_start(self) -> int:
        return gba.to_address(self.start)

    @property
    def address_end(self) -> int:
        """Exclusive end address."""
        return gba.to_address(self.end - 1) + 1 if self.length else gba.to_address(self.start)

    @property
    def file_span(self) -> str:
        return f"{_hex(self.start)}-{_hex(self.end)}"

    @property
    def address_span(self) -> str:
        return f"0x{self.address_start:08X}-0x{self.address_end:08X}"

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "file_start": _hex(self.start),
            "file_end": _hex(self.end),
            "rom_address_start": f"0x{self.address_start:08X}",
            "rom_address_end": f"0x{self.address_end:08X}",
            "length": self.length,
            "classification": self.classification,
            "confidence": self.confidence,
            "isa": self.isa,
            "executable": self.executable,
            "representation": self.representation,
            "evidence": list(self.evidence),
            "provenance": self.provenance,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(payload: dict) -> "Region":
        return Region(
            id=payload["id"],
            start=int(payload["file_start"], 0),
            end=int(payload["file_end"], 0),
            classification=payload["classification"],
            confidence=payload["confidence"],
            evidence=list(payload.get("evidence", [])),
            provenance=payload.get("provenance", ""),
            notes=payload.get("notes", ""),
            representation=payload.get("representation", "derived"),
            isa=payload.get("isa"),
            executable=payload.get("executable", "unknown"),
        )


@dataclasses.dataclass
class Function:
    address: int
    isa: str
    confidence: str
    size: int | None = None
    discovery: list[str] = dataclasses.field(default_factory=list)
    callers: list[int] = dataclasses.field(default_factory=list)
    callees: list[int] = dataclasses.field(default_factory=list)
    leaf: bool | None = None
    notes: str = ""

    @property
    def name(self) -> str:
        return f"sub_{self.address:08X}"

    def as_dict(self) -> dict:
        return {
            "address": f"0x{self.address:08X}",
            "name": self.name,
            "isa": self.isa,
            "confidence": self.confidence,
            "size": self.size,
            "discovery": list(self.discovery),
            "caller_count": len(self.callers),
            "callers": [f"0x{c:08X}" for c in self.callers],
            "callee_count": len(self.callees),
            "callees": [f"0x{c:08X}" for c in self.callees],
            "leaf": self.leaf,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(payload: dict) -> "Function":
        return Function(
            address=int(payload["address"], 0),
            isa=payload["isa"],
            confidence=payload["confidence"],
            size=payload.get("size"),
            discovery=list(payload.get("discovery", [])),
            callers=[int(c, 0) for c in payload.get("callers", [])],
            callees=[int(c, 0) for c in payload.get("callees", [])],
            leaf=payload.get("leaf"),
            notes=payload.get("notes", ""),
        )


@dataclasses.dataclass
class RomMap:
    regions: list[Region]
    rom_size: int = gba.ROM_SIZE
    source_sha1: str = ""
    generated_by: str = ""
    tooling: dict = dataclasses.field(default_factory=dict)

    # -- invariants --------------------------------------------------------
    def validate(self) -> None:
        """Prove the ten structural invariants the ticket requires.

        Raises RomMapError listing every violation found, rather than the first.
        """
        problems: list[str] = []
        if self.rom_size != gba.ROM_SIZE:
            problems.append(f"rom_size is {self.rom_size}, expected {gba.ROM_SIZE}")

        ordered = sorted(self.regions, key=lambda r: r.start)
        if ordered and ordered[0].start != 0:
            problems.append(f"map does not start at file offset 0x000000 (starts at {_hex(ordered[0].start)})")

        cursor = 0
        for region in ordered:
            if region.start > cursor:
                problems.append(
                    f"gap of {region.start - cursor} bytes at {_hex(cursor)}-{_hex(region.start)}"
                )
            elif region.start < cursor:
                problems.append(
                    f"overlap of {cursor - region.start} bytes at {_hex(region.start)} "
                    f"(region {region.id})"
                )
            cursor = max(cursor, region.end)
            # address conversion must round-trip
            if gba.to_offset(region.address_start) != region.start:
                problems.append(f"region {region.id}: address/offset conversion is inconsistent")
        if cursor != self.rom_size:
            problems.append(f"map ends at {_hex(cursor)}, expected {_hex(self.rom_size)}")

        total = sum(r.length for r in ordered)
        if total != self.rom_size:
            problems.append(f"region lengths sum to {total}, expected {self.rom_size}")

        ids = [r.id for r in ordered]
        if len(ids) != len(set(ids)):
            duplicates = sorted({i for i in ids if ids.count(i) > 1})
            problems.append(f"duplicate region ids: {duplicates}")

        if problems:
            raise RomMapError("ROM map invariants FAILED:\n" + "\n".join(f"  - {p}" for p in problems))

    # -- reporting ---------------------------------------------------------
    def coverage(self) -> dict[str, dict]:
        """Bytes per classification, with a confidence BREAKDOWN.

        Reporting a single confidence per classification would be misleading:
        the `code` class contains both reachability-proven bytes and heuristic
        candidates. The breakdown keeps those visible instead of letting one
        proven region make the whole class look proven.
        """
        totals: dict[str, dict] = {}
        for region in self.regions:
            slot = totals.setdefault(
                region.classification, {"bytes": 0, "regions": 0, "confidence": {}}
            )
            slot["bytes"] += region.length
            slot["regions"] += 1
            slot["confidence"][region.confidence] = slot["confidence"].get(region.confidence, 0) + region.length
        for slot in totals.values():
            slot["confidence"] = dict(
                sorted(slot["confidence"].items(), key=lambda kv: CONFIDENCE_RANK[kv[0]])
            )
            slot["weakest_confidence"] = max(
                slot["confidence"], key=lambda name: CONFIDENCE_RANK[name]
            )
        return dict(sorted(totals.items(), key=lambda kv: -kv[1]["bytes"]))

    def executable_coverage(self) -> dict[str, int]:
        out = {state: 0 for state in EXECUTABLE_STATES}
        for region in self.regions:
            out[region.executable] = out.get(region.executable, 0) + region.length
        return out

    def representation_coverage(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for region in self.regions:
            out[region.representation] = out.get(region.representation, 0) + region.length
        return out

    def isa_coverage(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for region in self.regions:
            if region.classification in ("code", "code_candidate"):
                key = region.isa or "unknown"
                out[key] = out.get(key, 0) + region.length
        return out

    def find(self, offset: int) -> Region | None:
        for region in self.regions:
            if region.start <= offset < region.end:
                return region
        return None

    # -- serialisation -----------------------------------------------------
    def as_dict(self) -> dict:
        return {
            "schema": 1,
            "rom_size": self.rom_size,
            "rom_size_hex": _hex(self.rom_size),
            "source_sha1": self.source_sha1,
            "generated_by": self.generated_by,
            "tooling": self.tooling,
            "confidence_levels": list(CONFIDENCE_LEVELS),
            "classifications": list(CLASSIFICATIONS),
            "coverage": self.coverage(),
            "executable_coverage": self.executable_coverage(),
            "representation_coverage": self.representation_coverage(),
            "isa_coverage": self.isa_coverage(),
            "regions": [r.as_dict() for r in sorted(self.regions, key=lambda r: r.start)],
        }

    def to_json(self) -> str:
        self.validate()
        return json.dumps(self.as_dict(), indent=2) + "\n"

    @staticmethod
    def from_dict(payload: dict) -> "RomMap":
        rom_map = RomMap(
            regions=[Region.from_dict(r) for r in payload["regions"]],
            rom_size=int(payload.get("rom_size", gba.ROM_SIZE)),
            source_sha1=payload.get("source_sha1", ""),
            generated_by=payload.get("generated_by", ""),
            tooling=payload.get("tooling", {}),
        )
        rom_map.validate()
        return rom_map


@dataclasses.dataclass
class FunctionInventory:
    functions: list[Function]
    source_sha1: str = ""
    method: str = ""
    notes: str = ""

    def counts(self) -> dict[str, int]:
        out = {
            "confirmed_arm": 0,
            "probable_arm": 0,
            "confirmed_thumb": 0,
            "probable_thumb": 0,
            "uncertain_isa": 0,
            "total": len(self.functions),
        }
        for function in self.functions:
            isa = function.isa
            if isa == "arm":
                key = "confirmed_arm" if function.confidence in ("proven", "high") else "probable_arm"
            elif isa == "thumb":
                key = "confirmed_thumb" if function.confidence in ("proven", "high") else "probable_thumb"
            else:
                key = "uncertain_isa"
            out[key] += 1
        return out

    def as_dict(self) -> dict:
        return {
            "schema": 1,
            "source_sha1": self.source_sha1,
            "method": self.method,
            "notes": self.notes,
            "counts": self.counts(),
            "functions": [f.as_dict() for f in sorted(self.functions, key=lambda f: f.address)],
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2) + "\n"

    @staticmethod
    def from_dict(payload: dict) -> "FunctionInventory":
        return FunctionInventory(
            functions=[Function.from_dict(f) for f in payload["functions"]],
            source_sha1=payload.get("source_sha1", ""),
            method=payload.get("method", ""),
            notes=payload.get("notes", ""),
        )


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------
def _pct(part: int, whole: int) -> str:
    return f"{100.0 * part / whole:.3f}%" if whole else "0.000%"


def render_rom_map_markdown(rom_map: RomMap, tooling: dict | None = None) -> str:
    rom_map.validate()
    lines: list[str] = []
    add = lines.append

    add("# Buu's Fury - independent ROM map")
    add("")
    add(
        "Generated by `python -m buusfury rommap --write`. Do not edit by hand; "
        "the map is derived from the canonical ROM by "
        "`tools/buusfury/analysis.py` and may be regenerated at any time."
    )
    add("")
    add(f"- ROM size: **{rom_map.rom_size:,} bytes** ({_hex(rom_map.rom_size)})")
    add(f"- Canonical SHA-1: `{rom_map.source_sha1}`")
    add(f"- Top-level regions: **{len(rom_map.regions)}**")
    add(f"- Generator: {rom_map.generated_by}")
    add("")
    add(
        "Every byte of the cartridge belongs to exactly one region. The tiling, "
        "the address conversion and the length arithmetic are asserted by "
        "`tests/test_rom_map.py`, not assumed."
    )
    add("")

    add("## Coverage by classification")
    add("")
    add(
        "The confidence column is a BREAKDOWN per classification, not a single"
    )
    add(
        "value: `code` contains both reachability-proven bytes and heuristic"
    )
    add("candidates, and collapsing them would overstate the proven part.")
    add("")
    add("| Classification | Bytes | % ROM | Regions | Bytes by confidence |")
    add("| --- | ---: | ---: | ---: | --- |")
    for name, slot in rom_map.coverage().items():
        breakdown = ", ".join(
            f"{level} {count:,}" for level, count in slot["confidence"].items()
        )
        add(
            f"| `{name}` | {slot['bytes']:,} | {_pct(slot['bytes'], rom_map.rom_size)} | "
            f"{slot['regions']} | {breakdown} |"
        )
    add(
        f"| **total** | **{rom_map.rom_size:,}** | **100.000%** | "
        f"**{len(rom_map.regions)}** | |"
    )
    add("")

    add("## Coverage by executable status")
    add("")
    add("| Executable | Bytes | % ROM |")
    add("| --- | ---: | ---: |")
    for state, count in rom_map.executable_coverage().items():
        add(f"| `{state}` | {count:,} | {_pct(count, rom_map.rom_size)} |")
    add("")

    add("## Coverage by how the byte is obtained today")
    add("")
    add("| Representation | Bytes | % ROM |")
    add("| --- | ---: | ---: |")
    for name, count in sorted(rom_map.representation_coverage().items(), key=lambda kv: -kv[1]):
        add(f"| `{name}` | {count:,} | {_pct(count, rom_map.rom_size)} |")
    add("")

    isa = rom_map.isa_coverage()
    if isa:
        add("## Identified code by instruction set")
        add("")
        add("| ISA | Bytes | % of all code-classified bytes |")
        add("| --- | ---: | ---: |")
        total_isa = sum(isa.values())
        for name, count in sorted(isa.items(), key=lambda kv: -kv[1]):
            add(f"| {name} | {count:,} | {_pct(count, total_isa)} |")
        add("")

    add("## Regions")
    add("")
    add(
        "| # | id | file extent | ROM address | bytes | classification | ISA | "
        "exec | confidence | representation |"
    )
    add("| ---: | --- | --- | --- | ---: | --- | --- | --- | --- | --- |")
    for index, region in enumerate(sorted(rom_map.regions, key=lambda r: r.start), start=1):
        add(
            f"| {index} | `{region.id}` | `{region.file_span}` | "
            f"`0x{region.address_start:08X}` | {region.length:,} | "
            f"`{region.classification}` | {region.isa or '-'} | {region.executable} | "
            f"{region.confidence} | {region.representation} |"
        )
    add("")

    add("## Evidence per region")
    add("")
    for region in sorted(rom_map.regions, key=lambda r: r.start):
        add(f"### `{region.id}` ({region.file_span}, {region.length:,} bytes)")
        add("")
        add(
            f"- classification `{region.classification}`, confidence **{region.confidence}**"
        )
        if region.isa:
            add(f"- instruction set: {region.isa}")
        add(f"- executable: {region.executable}; representation: `{region.representation}`")
        if region.provenance:
            add(f"- provenance: {region.provenance}")
        if region.notes:
            add(f"- notes: {region.notes}")
        if region.evidence:
            add("- evidence:")
            for item in region.evidence:
                add(f"  - {item}")
        add("")

    if tooling:
        add("## Tooling")
        add("")
        for key, value in tooling.items():
            add(f"- {key}: {value}")
        add("")
    return "\n".join(lines).rstrip() + "\n"
