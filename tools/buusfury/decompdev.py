"""decomp.dev semantic-progress integration.

WHAT THIS MEASURES
------------------
This module produces a progress report for a **semantic reconstruction**, not for
a byte-matching decompilation. A function earns credit only when its committed
lift report establishes

    SEMANTIC = PROVEN

and the reported percentage is the fraction of the project's mechanically
identified executable bytes that such a function accounts for. It is NOT a
compiler-match percentage: `MODERN_BUILD = PASS` earns nothing, a stub earns
nothing, a known boundary earns nothing, and `ADS_MATCH` is BLOCKED for every
target and is deliberately irrelevant here.

WHERE THE NUMBERS COME FROM
---------------------------
Every number is derived from committed project provenance. Nothing is typed in by
hand and nothing is read out of the cartridge at report time, so the report can be
generated in CI with no ROM, no toolchain and no build:

  config/functions.json       candidate function entry points (address + ISA),
                              machine-derived from the ROM by
                              `python -m buusfury rommap`
  config/rom_map.json         the classification of every byte of the image,
                              in particular which byte ranges are executable
  config/lift_targets.json    the reconstruction registry
  config/lift_<id>.json       one report per reconstructed translation unit,
                              carrying its SEMANTIC / MODERN_BUILD / ADS_MATCH
                              verdicts and each function's ORIGINAL byte extent

`config/functions.json` is used ONLY for entry points and instruction sets. Its
`size` field is `analysis.decode_run(..., limit=0x400).bytes_ok`, which is not a
function boundary and overruns small functions; `tools/buusfury/compiler_probe.py`
already says so in-tree. Using it as an extent would inflate the numerator, so it
is not used at all.

THE DENOMINATOR
---------------
The denominator is the executable extent the project has already identified:

  * every `code` / `code_candidate` region of `config/rom_map.json`, whose bytes
    must be accounted for exactly by the units derived from them; plus
  * the code half of the runtime-copied IWRAM overlay, whose extent and whose
    function list come from the committed derivation in
    `config/lift_iwramdispatch.json`.

Within a region the bytes are split between **function units** (one per
mechanically discovered entry point) and a single **unattributed remainder**. A
function unit's tracked size is

  * its committed ORIGINAL byte extent, when a lift report establishes one
    (extent kind `measured`), or
  * the distance to the next entry point in the same region, clipped to the
    region end (extent kind `upper-bound`), otherwise.

The remainder absorbs the difference, so the sum of the units of a region always
equals the region's length exactly. That is what makes the denominator stable:
proving a function replaces an `upper-bound` estimate with a `measured` extent and
the freed bytes move into the remainder, so `total_code` cannot move as a side
effect of reconstruction work. A ticket can therefore never raise its percentage
by shrinking the denominator.

Sources of the ARM code half and of the overlay function list:

  `config/lift_iwramdispatch.json`
      `boundary_evidence.iwram_dispatch.block` gives the overlay's ROM source,
      the IWRAM extent and `code_end_iwram`; `...callgraph.functions` enumerates
      the reachable ARM functions with exact extents and `...unreachable_code_runs`
      adds the complete functions nothing reaches. The 4-byte Thumb `bx r4`
      halfword at IWRAM 0x03000C98 is NOT a function and is left in the
      remainder. Two prose documents say the block holds "20 ARM functions"; no
      committed artifact enumerates 20, so this inventory tracks the 18 the
      committed derivation actually enumerates.

THE REPORT
----------
`objdiff_report()` renders an **objdiff Report version 2** JSON document, which is
what decomp.dev ingests from a GitHub Actions artifact named `<version>_report`
containing `report.json`. Semantic-complete units are reported at
`fuzzy_match_percent = 100.0`, which is the only lever the format gives us:
decomp.dev's headline is `matched_code_percent`, computed from exactly-100%
units. The report version string is `semantic` and is displayed verbatim by
decomp.dev, so the artifact is `semantic_report` and the dashboard labels the
series `(semantic)`. Every unit is also tagged with a category whose display name
says what it is; see `CATEGORIES`.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import identity as _identity

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
#: objdiff's report schema version. `Report::migrate()` REJECTS anything else.
REPORT_VERSION = 2

#: decomp.dev version string. Displayed verbatim by the dashboard, and the
#: Actions artifact must be named `<version>_report`, i.e. `semantic_report`.
#: Some characters are not accepted by decomp.dev's artifact-name regex
#: `^(?P<version>[A-z0-9_.\-]+)[_-]report(?:[_-].*)?$`, so keep it simple.
VERSION_NAME = "semantic"
ARTIFACT_NAME = f"{VERSION_NAME}_report"
#: The file name inside the artifact archive. decomp.dev looks for this stem.
ARTIFACT_FILE_NAME = "report.json"

INVENTORY_PATH = _identity.CONFIG_DIR / "decompdev_inventory.json"
REPORT_PATH = _identity.CONFIG_DIR / "decompdev_report.json"
FUNCTIONS_PATH = _identity.CONFIG_DIR / "functions.json"
ROM_MAP_PATH = _identity.CONFIG_DIR / "rom_map.json"
LIFT_TARGETS_PATH = _identity.CONFIG_DIR / "lift_targets.json"

IWRAM_BASE = 0x03000000

#: Region classifications whose bytes are tracked as executable. This is the
#: project's own claim about which bytes are code; nothing here re-classifies.
TRACKED_CLASSIFICATIONS = ("code", "code_candidate")
TRACKED_ISA = ("arm", "thumb", "mixed")

#: The SEMANTIC verdict that earns credit. The other two verdicts never do.
CREDIT_VERDICT = "PROVEN"

STATUS_COMPLETE = "semantic_complete"
STATUS_UNRECONSTRUCTED = "not_reconstructed"
STATUS_UNATTRIBUTED = "unattributed"

EXTENT_MEASURED = "measured"
EXTENT_UPPER_BOUND = "upper-bound"
EXTENT_UNATTRIBUTED = "unattributed"

#: Category ids and display names. decomp.dev builds its category selector from
#: these and shows the names, so each reconstructed family states plainly that it
#: is a semantic reconstruction. Every unit belongs to EXACTLY ONE category, so
#: the category measures sum to the project measures.
CATEGORIES: tuple[tuple[str, str], ...] = (
    ("script_vm", "Script VM (semantic reconstruction)"),
    ("flag_state", "Flag and bit state (semantic reconstruction)"),
    ("engine_objects", "Engine object collections (semantic reconstruction)"),
    ("allocator", "GBARam heap allocator (semantic reconstruction)"),
    ("iwram_overlay", "IWRAM overlay (runtime-copied, semantic reconstruction)"),
    ("runtime_irq", "IWRAM interrupt dispatch (semantic reconstruction)"),
    ("rom_code", "ROM code - identified, not yet reconstructed"),
    ("rom_code_candidate", "ROM code candidate - not yet reconstructed"),
    ("unattributed", "Unattributed executable bytes"),
)
CATEGORY_NAMES = dict(CATEGORIES)

#: Which reconstruction family each registered lift target belongs to. This is a
#: label over committed evidence (the target registry and its report), not a new
#: claim: a target that is not listed keeps the address-space default.
LIFT_TARGET_CATEGORY = {
    "bci": "script_vm",
    "handler2": "script_vm",
    "operand": "script_vm",
    "stack": "script_vm",
    "arith": "script_vm",
    "use": "script_vm",
    "effect": "script_vm",
    "flagread": "flag_state",
    "booluse": "flag_state",
    "clear": "flag_state",
    "gather": "flag_state",
    "flagmask": "flag_state",
    "native178": "engine_objects",
    "append": "engine_objects",
    "collectionread": "engine_objects",
    "collectionwrite2": "engine_objects",
    "collectioninsert2": "engine_objects",
    "collectionflush3": "engine_objects",
    "gbaram": "allocator",
    "iwramblock": "iwram_overlay",
    "iwramdispatch": "runtime_irq",
}


class DecompDevError(RuntimeError):
    """Raised when the inventory or the report violates a structural invariant."""


def _hex(value: int) -> str:
    return f"0x{value:08X}"


def _sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def _load_json(path: Path) -> tuple[dict, str]:
    """Return (document, sha1 of the exact bytes).

    The digest is taken from the bytes, not from `read_text`, because text mode
    translates newlines and would report a digest the file does not have.
    """
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), _sha1(raw)


def _pct(part: int, whole: int, digits: int = 6) -> float:
    """A percentage, rounded so the committed JSON is stable and readable."""
    if not whole:
        return 0.0
    return round(100.0 * part / whole, digits)


# ---------------------------------------------------------------------------
# inputs
# ---------------------------------------------------------------------------
@dataclass
class LiftFunction:
    """One function row of a committed lift report."""

    address: int
    size: int
    instructions: int
    isa: str
    start: str
    end: str


@dataclass
class LiftReport:
    """One committed `config/lift_<id>.json`."""

    path: Path
    target_id: str
    ticket: str
    isa: str
    source: str
    semantic: str
    modern_build: str
    ads_match: str
    ads_code: str
    functions: list[LiftFunction]
    document: dict
    sha1: str = ""

    @property
    def credited(self) -> bool:
        return self.semantic == CREDIT_VERDICT


@dataclass
class Inputs:
    """Everything the inventory is derived from, all of it committed."""

    rom_sha1: str
    function_entries: list[dict]
    regions: list[dict]
    lift_targets: dict
    lift_reports: list[LiftReport]
    overlay: dict
    overlay_report: Path
    overlay_code_bytes: int = 0
    #: Candidate entry points that fall outside every tracked executable region.
    #: They are counted for transparency and deliberately NOT tracked: they carry
    #: no byte extent the project has classified as code.
    unplaced_entries: int = 0
    digests: dict[str, str] = field(default_factory=dict)


def load_inputs(
    *,
    functions_path: Path | None = None,
    rom_map_path: Path | None = None,
    lift_targets_path: Path | None = None,
    config_dir: Path | None = None,
) -> Inputs:
    """Read the committed provenance. No ROM, no toolchain, no network."""
    functions_path = Path(functions_path or FUNCTIONS_PATH)
    rom_map_path = Path(rom_map_path or ROM_MAP_PATH)
    lift_targets_path = Path(lift_targets_path or LIFT_TARGETS_PATH)
    config_dir = Path(config_dir or _identity.CONFIG_DIR)

    functions, functions_sha1 = _load_json(functions_path)
    rom_map, rom_map_sha1 = _load_json(rom_map_path)
    registry, registry_sha1 = _load_json(lift_targets_path)

    reports: list[LiftReport] = []
    overlay: dict | None = None
    overlay_report: Path | None = None
    for path in sorted(config_dir.glob("lift_*.json")):
        if path.name == "lift_targets.json":
            continue
        document, digest = _load_json(path)
        if "target" not in document or "verdicts" not in document:
            continue
        target = document["target"]
        verdicts = document["verdicts"]
        rows = []
        for row in document.get("functions", []):
            original = row["original"]
            rows.append(
                LiftFunction(
                    address=int(original["start"], 0),
                    size=int(original["size"]),
                    instructions=int(original["instructions"]),
                    isa=original.get("isa") or target.get("isa") or "thumb",
                    start=original["start"],
                    end=original["end"],
                )
            )
        reports.append(
            LiftReport(
                path=path,
                target_id=target["id"],
                ticket=document.get("ticket", ""),
                isa=target.get("isa", "thumb"),
                source=target.get("decomp_source", ""),
                semantic=verdicts["semantic"]["status"],
                modern_build=verdicts["modern_build"]["status"],
                ads_match=verdicts["ads_match"]["status"],
                ads_code=verdicts["ads_match"].get("code", ""),
                functions=sorted(rows, key=lambda f: f.address),
                document=document,
                sha1=digest,
            )
        )
        evidence = document.get("boundary_evidence", {}).get("iwram_dispatch")
        if evidence and "block" in evidence and "callgraph" in evidence:
            if overlay is not None:
                raise DecompDevError(
                    f"more than one lift report carries IWRAM overlay evidence: "
                    f"{overlay_report.name} and {path.name}"
                )
            overlay = evidence
            overlay_report = path

    if overlay is None or overlay_report is None:
        raise DecompDevError(
            "no committed lift report carries boundary_evidence.iwram_dispatch, so "
            "the runtime-copied IWRAM overlay cannot be inventoried. Re-run the "
            "IWRAM dispatch lift before generating a progress report."
        )

    # The ROM identity is carried in the committed configs, not re-measured: this
    # must work with no baserom present.
    rom_sha1 = rom_map.get("source_sha1") or functions.get("source_sha1") or ""
    for report in reports:
        source_sha1 = report.document.get("source_sha1") or ""
        if rom_sha1 and source_sha1 and source_sha1 != rom_sha1:
            raise DecompDevError(
                f"{report.path.name} was produced from ROM {source_sha1} but the map "
                f"describes {rom_sha1}; the provenance disagrees with itself"
            )

    return Inputs(
        rom_sha1=rom_sha1,
        function_entries=sorted(
            functions.get("functions", []), key=lambda f: int(f["address"], 0)
        ),
        regions=sorted(rom_map.get("regions", []), key=lambda r: int(r["file_start"], 0)),
        lift_targets=registry,
        lift_reports=reports,
        overlay=overlay,
        overlay_report=overlay_report or Path(),
        digests={
            "functions.json": functions_sha1,
            "rom_map.json": rom_map_sha1,
            "lift_targets.json": registry_sha1,
        },
    )


# ---------------------------------------------------------------------------
# inventory
# ---------------------------------------------------------------------------
@dataclass
class Unit:
    """One tracked unit: a function, or the unattributed remainder of a region."""

    unit_name: str
    address: int | None
    size: int
    isa: str | None
    extent: str
    status: str
    category: str
    region: str
    classification: str
    confidence: str
    family: str
    lift_target: str | None = None
    evidence: str | None = None
    source: str | None = None
    instructions: int | None = None
    neutral_name: str | None = None
    #: For a runtime-installed overlay unit this is the ROM address whose bytes
    #: the unit is a copy of. Lift reports key their functions on ROM addresses
    #: even when the code executes from IWRAM, so the join needs both.
    rom_address: int | None = None

    @property
    def credited(self) -> bool:
        return self.status == STATUS_COMPLETE

    @property
    def is_function(self) -> bool:
        return self.status != STATUS_UNATTRIBUTED

    def as_dict(self) -> dict:
        return {
            "unit": self.unit_name,
            "address": _hex(self.address) if self.address is not None else None,
            "rom_address": _hex(self.rom_address) if self.rom_address is not None else None,
            "neutral_name": self.neutral_name,
            "isa": self.isa,
            "original_byte_size": self.size,
            "extent": self.extent,
            "status": self.status,
            "category": self.category,
            "family": self.family,
            "region": self.region,
            "region_classification": self.classification,
            "region_confidence": self.confidence,
            "lift_target": self.lift_target,
            "evidence": self.evidence,
            "source": self.source,
            "instructions": self.instructions,
        }


@dataclass
class Inventory:
    units: list[Unit]
    regions: list[dict]
    inputs: Inputs
    problems: list[str] = field(default_factory=list)

    # -- aggregates ------------------------------------------------------
    @property
    def function_units(self) -> list[Unit]:
        return [u for u in self.units if u.is_function]

    @property
    def complete_units(self) -> list[Unit]:
        return [u for u in self.units if u.credited]

    @property
    def tracked_functions(self) -> int:
        return len(self.function_units)

    @property
    def complete_functions(self) -> int:
        return len(self.complete_units)

    @property
    def tracked_executable_bytes(self) -> int:
        return sum(u.size for u in self.units)

    @property
    def measured_bytes(self) -> int:
        return sum(u.size for u in self.units if u.extent == EXTENT_MEASURED)

    @property
    def upper_bound_bytes(self) -> int:
        return sum(u.size for u in self.units if u.extent == EXTENT_UPPER_BOUND)

    @property
    def unattributed_bytes(self) -> int:
        return sum(u.size for u in self.units if u.extent == EXTENT_UNATTRIBUTED)

    @property
    def complete_bytes(self) -> int:
        return sum(u.size for u in self.complete_units)

    def scoped(self, *, iwram: bool) -> list[Unit]:
        if iwram:
            return [u for u in self.units if u.category == "iwram_overlay"
                    or u.category == "runtime_irq"]
        return [u for u in self.units if u.category not in ("iwram_overlay", "runtime_irq")]

    def category_totals(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for unit in self.units:
            slot = out.setdefault(unit.category, {"units": 0, "functions": 0, "bytes": 0, "complete_functions": 0, "complete_bytes": 0})
            slot["units"] += 1
            if unit.is_function:
                slot["functions"] += 1
            slot["bytes"] += unit.size
            if unit.credited:
                slot["complete_functions"] += 1
                slot["complete_bytes"] += unit.size
        return dict(sorted(out.items(), key=lambda kv: (-kv[1]["bytes"], kv[0])))

    # -- invariants ------------------------------------------------------
    def validate(self) -> list[str]:
        """Every structural invariant, as a list of problems (empty is good).

        Collected rather than raised one at a time, so a broken inventory reports
        all of its defects at once.
        """
        problems: list[str] = []

        # 1. one unit per address, and no duplicate unit names
        addresses = [u.address for u in self.units if u.address is not None]
        seen: dict[int, str] = {}
        for unit in self.units:
            if unit.address is None:
                continue
            if unit.address in seen:
                problems.append(
                    f"duplicate unit address {_hex(unit.address)}: "
                    f"{seen[unit.address]} and {unit.unit_name}"
                )
            seen[unit.address] = unit.unit_name
        names = [u.unit_name for u in self.units]
        if len(names) != len(set(names)):
            duplicates = sorted({n for n in names if names.count(n) > 1})
            problems.append(f"duplicate unit names: {duplicates}")

        # 2. no overlapping extents, within an address space
        for space, predicate in (
            ("cartridge", lambda a: a >= 0x08000000),
            ("iwram", lambda a: IWRAM_BASE <= a < 0x04000000),
        ):
            placed = sorted(
                (u for u in self.units if u.address is not None and predicate(u.address)),
                key=lambda u: u.address,
            )
            for before, after in zip(placed, placed[1:]):
                end = before.address + before.size
                if end > after.address:
                    problems.append(
                        f"overlapping {space} units: {before.unit_name} "
                        f"({_hex(before.address)}+{before.size} = {_hex(end)}) runs into "
                        f"{after.unit_name} at {_hex(after.address)}"
                    )

        # 3. every unit has a positive extent and a known category
        for unit in self.units:
            if unit.size <= 0:
                problems.append(f"{unit.unit_name}: non-positive size {unit.size}")
            if unit.category not in CATEGORY_NAMES:
                problems.append(
                    f"{unit.unit_name}: unknown category {unit.category!r}"
                )

        # 4. the regions are reproduced EXACTLY: units plus remainder per region
        for region in self.regions:
            members = [u for u in self.units if u.region == region["id"]]
            total = sum(u.size for u in members)
            if total != region["length"]:
                problems.append(
                    f"region {region['id']}: units total {total} bytes but the region "
                    f"is {region['length']} bytes"
                )
            remainders = [u for u in members if u.status == STATUS_UNATTRIBUTED]
            if len(remainders) > 1:
                problems.append(
                    f"region {region['id']}: {len(remainders)} remainder units"
                )

        # 5. the tracked regions must be disjoint and strictly ordered. They do
        # NOT tile the image: only the byte ranges the project has classified as
        # executable are tracked, and everything else is out of scope.
        previous_end = -1
        for region in self.regions:
            start = int(region["rom_address_start"], 0)
            end = int(region["rom_address_end"], 0)
            if start < previous_end:
                problems.append(f"region {region['id']} overlaps the previous region")
            if end <= start:
                problems.append(f"region {region['id']} has a non-positive extent")
            previous_end = end

        # 6. a semantic-complete unit must carry its evidence
        for unit in self.complete_units:
            if not unit.evidence:
                problems.append(f"{unit.unit_name}: semantic-complete with no evidence")
            if not unit.lift_target:
                problems.append(f"{unit.unit_name}: semantic-complete with no lift target")
            if not unit.source:
                problems.append(f"{unit.unit_name}: semantic-complete with no source file")
            if unit.extent != EXTENT_MEASURED:
                problems.append(
                    f"{unit.unit_name}: semantic-complete but its extent is "
                    f"{unit.extent!r}, not a measured original extent"
                )
            if not unit.instructions:
                problems.append(
                    f"{unit.unit_name}: semantic-complete with no instruction count"
                )

        # 7. every function a lift report claims must be a tracked unit
        by_address = {
            (u.rom_address if u.rom_address is not None else u.address): u
            for u in self.units
            if u.address is not None
        }
        for report in self.inputs.lift_reports:
            for function in report.functions:
                unit = by_address.get(function.address)
                if unit is None:
                    problems.append(
                        f"orphan lift function {_hex(function.address)} from "
                        f"{report.path.name} is not a tracked unit"
                    )
                    continue
                if report.credited and unit.size != function.size:
                    problems.append(
                        f"{unit.unit_name}: the inventory records {unit.size} original "
                        f"bytes but {report.path.name} records {function.size}"
                    )
                if report.credited and not unit.credited:
                    problems.append(
                        f"{unit.unit_name}: {report.path.name} is SEMANTIC "
                        f"{report.semantic} but the unit is {unit.status}"
                    )

        # 8. every registered target must have a report, and vice versa
        registered = {t["id"] for t in self.inputs.lift_targets.get("targets", [])}
        reported = {r.target_id for r in self.inputs.lift_reports}
        for target_id in sorted(registered - reported):
            problems.append(f"registered lift target {target_id!r} has no report")
        for target_id in sorted(reported - registered):
            problems.append(f"lift report {target_id!r} is not in the registry")

        # 9. category measures must sum to the project measures
        totals = self.category_totals()
        if sum(t["bytes"] for t in totals.values()) != self.tracked_executable_bytes:
            problems.append("category byte totals do not sum to the project total")
        if sum(t["functions"] for t in totals.values()) != self.tracked_functions:
            problems.append("category function totals do not sum to the project total")
        if sum(t["complete_bytes"] for t in totals.values()) != self.complete_bytes:
            problems.append("category credited bytes do not sum to the project total")

        # 10. nothing credits more than it tracks
        if self.complete_bytes > self.tracked_executable_bytes:
            problems.append("credited bytes exceed tracked executable bytes")

        # 11. the extent classes partition the tracked bytes
        partition = self.measured_bytes + self.upper_bound_bytes + self.unattributed_bytes
        if partition != self.tracked_executable_bytes:
            problems.append(
                f"extent classes total {partition} bytes but the tracked total is "
                f"{self.tracked_executable_bytes}"
            )

        return problems

    # -- serialisation ---------------------------------------------------
    def as_dict(self) -> dict:
        return {
            "schema": 1,
            "generated_by": "tools/buusfury/decompdev.py",
            "what_this_is": (
                "The committed denominator for the decomp.dev semantic progress "
                "report. One unit per mechanically discovered function plus one "
                "unattributed remainder per tracked region, so the units of a "
                "region sum to the region exactly and the denominator cannot move "
                "as a side effect of reconstruction work."
            ),
            "source_sha1": self.inputs.rom_sha1,
            "inputs": {
                "digests": dict(self.inputs.digests),
                "lift_reports": [
                    {
                        "path": f"config/{r.path.name}",
                        "target": r.target_id,
                        "ticket": r.ticket,
                        "semantic": r.semantic,
                        "modern_build": r.modern_build,
                        "ads_match": r.ads_match,
                        "ads_code": r.ads_code,
                        "credited_functions": len(r.functions) if r.credited else 0,
                        "credit": r.credited,
                        "sha1": r.sha1,
                    }
                    for r in sorted(self.inputs.lift_reports, key=lambda r: r.target_id)
                ],
            },
            "overlay": {
                "source_report": f"config/{self.inputs.overlay_report.name}",
                "rom_source": self.inputs.overlay["block"]["rom_source"],
                "rom_end": _hex(
                    int(self.inputs.overlay["block"]["rom_source"], 0)
                    + int(self.inputs.overlay["block"]["bytes"])
                ),
                "iwram_start": self.inputs.overlay["block"]["iwram_start"],
                "iwram_code_end": self.inputs.overlay["block"]["code_end_iwram"],
                "copied_bytes": self.inputs.overlay["block"]["bytes"],
                "code_bytes": self.inputs.overlay_code_bytes,
                "enumerated_functions": len(
                    [u for u in self.units if u.category in ("iwram_overlay", "runtime_irq")
                     and u.is_function]
                ),
                "note": (
                    "Two prose documents say the block holds 20 ARM functions; no "
                    "committed artifact enumerates 20. This inventory tracks the 18 "
                    "the committed derivation enumerates: 16 reachable functions plus "
                    "2 complete unreachable functions. The 4-byte Thumb halfword at "
                    "IWRAM 0x03000C98 is a return trampoline, not a function, and stays "
                    "in the remainder."
                ),
            },
            "denominator": {
                "tracked_functions": self.tracked_functions,
                "tracked_executable_bytes": self.tracked_executable_bytes,
                "measured_function_bytes": self.measured_bytes,
                "upper_bound_function_bytes": self.upper_bound_bytes,
                "unattributed_bytes": self.unattributed_bytes,
                "tracked_regions": len(self.regions),
                "candidate_entries_outside_tracked_regions": self.inputs.unplaced_entries,
                "extent_rule": (
                    "a function unit's size is its committed ORIGINAL byte extent "
                    "when a lift report establishes one, otherwise the distance to "
                    "the next entry point in the same region clipped to the region "
                    "end; the region remainder absorbs the difference, so a region's "
                    "units always sum to the region and proving a function cannot "
                    "move the denominator"
                ),
            },
            "semantic_credit": {
                "rule": (
                    "credit is granted only when a committed lift report's "
                    "verdicts.semantic.status is PROVEN; MODERN_BUILD and ADS_MATCH "
                    "never grant credit"
                ),
                "complete_functions": self.complete_functions,
                "complete_bytes": self.complete_bytes,
                "complete_percent_of_functions": _pct(
                    self.complete_functions, self.tracked_functions
                ),
                "complete_percent_of_bytes": _pct(
                    self.complete_bytes, self.tracked_executable_bytes
                ),
            },
            "categories": [
                {"id": cid, "name": CATEGORY_NAMES[cid], **totals}
                for cid, totals in self.category_totals().items()
            ],
            "problems": list(self.problems),
            "units": [u.as_dict() for u in self.units],
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2) + "\n"

    def summary_lines(self) -> list[str]:
        """The human-readable summary, in the shape the ticket asks for."""
        total_f = self.tracked_functions
        total_b = self.tracked_executable_bytes
        lines = [
            "Buu's Fury - decomp.dev SEMANTIC reconstruction progress",
            "",
            "Functions: %d / %d (%.3f%%)"
            % (self.complete_functions, total_f, _pct(self.complete_functions, total_f, 3)),
            "Code:      %s / %s original executable bytes (%.3f%%)"
            % (f"{self.complete_bytes:,}", f"{total_b:,}", _pct(self.complete_bytes, total_b, 3)),
        ]
        for label, iwram in (("ROM", False), ("IWRAM", True)):
            members = self.scoped(iwram=iwram)
            functions = [u for u in members if u.is_function]
            credited = [u for u in functions if u.credited]
            bytes_total = sum(u.size for u in members)
            bytes_credited = sum(u.size for u in credited)
            lines.append(
                "%s:       %d / %d functions, %s / %s bytes (%.3f%%)"
                % (
                    label.ljust(8),
                    len(credited),
                    len(functions),
                    f"{bytes_credited:,}",
                    f"{bytes_total:,}",
                    _pct(bytes_credited, bytes_total, 3),
                )
            )
        lines.append(
            "Extent:    %s measured, %s upper-bound, %s unattributed"
            % (
                f"{self.measured_bytes:,}",
                f"{self.upper_bound_bytes:,}",
                f"{self.unattributed_bytes:,}",
            )
        )
        lines.append("Categories:")
        for cid, totals in self.category_totals().items():
            lines.append(
                "  %-20s %3d/%-3d functions  %8s / %-9s bytes  %s"
                % (
                    cid,
                    totals["complete_functions"],
                    totals["functions"],
                    f"{totals['complete_bytes']:,}",
                    f"{totals['bytes']:,}",
                    CATEGORY_NAMES[cid],
                )
            )
        lines += [
            "",
            "This is SEMANTIC source coverage of mechanically identified executable",
            "bytes. It is NOT a byte-identical compiler-match percentage: no",
            "reconstructed function reproduces the original compiler's output",
            "(ADS_MATCH is BLOCKED for every target), and MODERN_BUILD = PASS earns",
            "no credit here. See docs/DECOMP_DEV.md.",
        ]
        return lines


# ---------------------------------------------------------------------------
# derivation
# ---------------------------------------------------------------------------
def _tracked_regions(inputs: Inputs) -> tuple[list[dict], dict]:
    """The regions whose bytes are tracked, and the overlay's source region."""
    overlay_block = inputs.overlay["block"]
    overlay_rom = int(overlay_block["rom_source"], 0)
    overlay_end = overlay_rom + int(overlay_block["bytes"])

    overlay_region = None
    tracked: list[dict] = []
    for region in inputs.regions:
        file_start = int(region["file_start"], 0)
        file_end = int(region["file_end"], 0)
        address_start = int(region["rom_address_start"], 0)
        if file_start == overlay_rom - 0x08000000 and file_end == overlay_end - 0x08000000:
            overlay_region = region
            continue
        if (
            region["classification"] in TRACKED_CLASSIFICATIONS
            and region.get("isa") in TRACKED_ISA
        ):
            tracked.append(
                {
                    "id": region["id"],
                    "address_start": address_start,
                    "address_end": int(region["rom_address_end"], 0),
                    "length": region["length"],
                    "classification": region["classification"],
                    "confidence": region["confidence"],
                    "isa": region.get("isa"),
                }
            )
    if overlay_region is None:
        raise DecompDevError(
            "config/rom_map.json has no region matching the IWRAM overlay's committed "
            f"source extent {_hex(overlay_rom)}..{_hex(overlay_end)}"
        )
    tracked.sort(key=lambda r: r["address_start"])
    return tracked, overlay_region


def _overlay_units(inputs: Inputs) -> tuple[list[dict], int]:
    """The overlay's ARM functions and its code-half byte count, from evidence."""
    evidence = inputs.overlay
    block = evidence["block"]
    code_start = int(block["iwram_start"], 0)
    code_end = int(block["code_end_iwram"], 0)
    code_bytes = code_end - code_start

    rows: list[dict] = []
    for function in evidence["callgraph"]["functions"]:
        rows.append(
            {
                "address": int(function["iwram"]),
                "rom_address": int(function["rom_address"]),
                "size": int(function["size"]),
                "instructions": int(function["instructions"]),
                "reachable": bool(function.get("externally_reachable")),
            }
        )
    for run in evidence["callgraph"]["unreachable_code_runs"]:
        if not run.get("looks_like_a_complete_function"):
            continue
        rows.append(
            {
                "address": int(run["iwram_start"], 0),
                "rom_address": int(run["rom_start"], 0),
                "size": int(run["bytes"]),
                "instructions": int(run["words"]),
                "reachable": False,
            }
        )
    rows.sort(key=lambda r: r["address"])

    # The evidence must describe a partition of the code half, or the inventory
    # would either double-count bytes or silently lose them.
    cursor = code_start
    for row in rows:
        if row["address"] < cursor:
            raise DecompDevError(
                f"IWRAM overlay functions overlap at {_hex(row['address'])}"
            )
        cursor = row["address"] + row["size"]
    if cursor > code_end:
        raise DecompDevError(
            f"IWRAM overlay functions end at {_hex(cursor)}, past the code half's end "
            f"{_hex(code_end)}"
        )
    return rows, code_bytes


def build_inventory(inputs: Inputs) -> Inventory:
    """Derive the tracked unit table from committed provenance."""
    tracked_regions, _overlay_region = _tracked_regions(inputs)
    overlay_block = inputs.overlay["block"]
    overlay_rom_start = int(overlay_block["rom_source"], 0)
    overlay_rom_end = overlay_rom_start + int(overlay_block["bytes"])

    # -- measured extents, from the committed lift reports ------------------
    measured: dict[int, LiftReport] = {}
    measured_row: dict[int, LiftFunction] = {}
    for report in inputs.lift_reports:
        if not report.credited:
            continue
        for function in report.functions:
            measured[function.address] = report
            measured_row[function.address] = function

    # -- entry points, per tracked region ----------------------------------
    entries_by_region: dict[str, list[dict]] = {r["id"]: [] for r in tracked_regions}
    unplaced = 0
    for entry in inputs.function_entries:
        address = int(entry["address"], 0)
        if overlay_rom_start <= address < overlay_rom_end:
            continue  # tracked as an IWRAM overlay unit instead
        region = next(
            (r for r in tracked_regions if r["address_start"] <= address < r["address_end"]),
            None,
        )
        if region is None:
            unplaced += 1
            continue
        entries_by_region[region["id"]].append(
            {"address": address, "isa": entry["isa"], "confidence": entry["confidence"]}
        )

    # A function with committed evidence MUST land in a tracked region. If it did
    # not, its bytes would be credited without being in the denominator.
    for address in sorted(measured):
        if overlay_rom_start <= address < overlay_rom_end:
            continue
        if not any(
            r["address_start"] <= address < r["address_end"] for r in tracked_regions
        ):
            raise DecompDevError(
                f"{_hex(address)} is credited by "
                f"{measured[address].path.name} but lies in no tracked code region"
            )

    units: list[Unit] = []
    for region in tracked_regions:
        entries = entries_by_region[region["id"]]
        known = {e["address"] for e in entries}
        for address, report in measured.items():
            if (
                region["address_start"] <= address < region["address_end"]
                and address not in known
            ):
                entries.append(
                    {"address": address, "isa": report.isa, "confidence": "proven"}
                )
                known.add(address)
        entries.sort(key=lambda e: e["address"])

        accounted = 0
        for index, entry in enumerate(entries):
            address = entry["address"]
            limit = (
                entries[index + 1]["address"]
                if index + 1 < len(entries)
                else region["address_end"]
            )
            report = measured.get(address)
            if report is not None:
                function = measured_row[address]
                size = function.size
                extent = EXTENT_MEASURED
                status = STATUS_COMPLETE
                lift_target = report.target_id
                evidence = f"config/{report.path.name}"
                source = report.source
                instructions = function.instructions
                category = LIFT_TARGET_CATEGORY.get(report.target_id)
                if category is None:
                    category = "rom_code" if region["classification"] == "code" else "rom_code_candidate"
                if address + size > limit:
                    raise DecompDevError(
                        f"{_hex(address)}: the measured extent {size} runs past the next "
                        f"entry point / region end at {_hex(limit)}"
                    )
            else:
                size = limit - address
                extent = EXTENT_UPPER_BOUND
                status = STATUS_UNRECONSTRUCTED
                lift_target = None
                evidence = None
                source = None
                instructions = None
                category = "rom_code" if region["classification"] == "code" else "rom_code_candidate"
            accounted += size
            units.append(
                Unit(
                    unit_name=f"rom/sub_{address:08X}",
                    address=address,
                    size=size,
                    isa=entry["isa"],
                    extent=extent,
                    status=status,
                    category=category,
                    region=region["id"],
                    classification=region["classification"],
                    confidence=entry["confidence"],
                    family=category,
                    lift_target=lift_target,
                    evidence=evidence,
                    source=source,
                    instructions=instructions,
                    neutral_name=f"sub_{address:08X}",
                )
            )
        remainder = region["length"] - accounted
        if remainder < 0:
            raise DecompDevError(
                f"region {region['id']}: units account for {accounted} bytes of "
                f"{region['length']}"
            )
        if remainder:
            units.append(
                Unit(
                    unit_name=f"unattributed/{region['id']}",
                    address=None,
                    size=remainder,
                    isa=None,
                    extent=EXTENT_UNATTRIBUTED,
                    status=STATUS_UNATTRIBUTED,
                    category="unattributed",
                    region=region["id"],
                    classification=region["classification"],
                    confidence=region["confidence"],
                    family="unattributed",
                    neutral_name=f"unattributed_{region['id']}",
                )
            )

    # -- the runtime-copied IWRAM overlay ----------------------------------
    overlay_rows, overlay_code_bytes = _overlay_units(inputs)
    inputs.overlay_code_bytes = overlay_code_bytes
    inputs.unplaced_entries = unplaced
    overlay_accounted = 0
    for row in overlay_rows:
        address = row["address"]
        rom_address = row["rom_address"]
        report = measured.get(rom_address)
        if report is not None and measured_row[rom_address].size != row["size"]:
            raise DecompDevError(
                f"{_hex(address)}: the IWRAM derivation records {row['size']} bytes but "
                f"{report.path.name} records {measured_row[rom_address].size}"
            )
        if report is not None:
            status = STATUS_COMPLETE
            extent = EXTENT_MEASURED
            lift_target = report.target_id
            evidence = f"config/{report.path.name}"
            source = report.source
            category = LIFT_TARGET_CATEGORY.get(report.target_id, "iwram_overlay")
        else:
            status = STATUS_UNRECONSTRUCTED
            extent = EXTENT_MEASURED  # the block derivation measures every function
            lift_target = None
            evidence = None
            source = None
            category = "iwram_overlay"
        overlay_accounted += row["size"]
        units.append(
            Unit(
                unit_name=f"iwram/sub_{address:08X}",
                address=address,
                rom_address=rom_address,
                size=row["size"],
                isa="arm",
                extent=extent,
                status=status,
                category=category,
                region="iwram_overlay",
                classification="code",
                confidence="high",
                family=category,
                lift_target=lift_target,
                evidence=evidence,
                source=source,
                instructions=row["instructions"],
                neutral_name=f"sub_{address:08X}",
            )
        )
    overlay_remainder = overlay_code_bytes - overlay_accounted
    if overlay_remainder < 0:
        raise DecompDevError(
            f"the IWRAM overlay's functions account for {overlay_accounted} bytes of a "
            f"{overlay_code_bytes}-byte code half"
        )
    if overlay_remainder:
        units.append(
            Unit(
                unit_name="iwram/unattributed",
                address=None,
                size=overlay_remainder,
                isa="arm",
                extent=EXTENT_UNATTRIBUTED,
                status=STATUS_UNATTRIBUTED,
                category="iwram_overlay",
                region="iwram_overlay",
                classification="code",
                confidence="high",
                family="iwram_overlay",
                neutral_name="unattributed_iwram_overlay",
            )
        )

    units.sort(key=lambda u: (0, u.address if u.address is not None else 0) if u.is_function else (1, u.region))

    regions = [
        {
            "id": r["id"],
            "rom_address_start": _hex(r["address_start"]),
            "rom_address_end": _hex(r["address_end"]),
            "length": r["length"],
            "classification": r["classification"],
            "confidence": r["confidence"],
            "isa": r["isa"],
        }
        for r in tracked_regions
    ]
    regions.append(
        {
            "id": "iwram_overlay",
            "rom_address_start": _hex(overlay_rom_start),
            "rom_address_end": _hex(overlay_rom_end),
            "length": overlay_code_bytes,
            "classification": "code",
            "confidence": "high",
            "isa": "arm",
        }
    )

    inventory = Inventory(units=units, regions=regions, inputs=inputs)
    inventory.problems = inventory.validate()
    return inventory


# ---------------------------------------------------------------------------
# objdiff Report version 2
# ---------------------------------------------------------------------------
def _drop_zero(payload: dict) -> dict:
    """objdiff omits zero / empty fields; mirror that so the JSON looks native."""
    out = {}
    for key, value in payload.items():
        if value is None:
            continue
        if isinstance(value, bool):
            out[key] = value
        elif isinstance(value, (int, float)) and value == 0:
            continue
        elif isinstance(value, (list, dict, str)) and len(value) == 0:
            continue
        else:
            out[key] = value
    return out


def _measures(*, total_code: int, matched_code: int, total_functions: int,
              matched_functions: int, total_units: int | None = None) -> dict:
    """A `Measures` message. u64 fields are JSON strings, as objdiff emits them.

    Zero-valued fields are omitted, which is what objdiff's own serialiser does,
    so a zero has to be dropped BEFORE the u64 fields are stringified (`"0"` is
    not an empty string and would otherwise survive).
    """
    payload = _drop_zero(
        {
            "fuzzy_match_percent": _pct(matched_code, total_code),
            "total_code": total_code,
            "matched_code": matched_code,
            "matched_code_percent": _pct(matched_code, total_code),
            "total_functions": total_functions,
            "matched_functions": matched_functions,
            "matched_functions_percent": _pct(matched_functions, total_functions),
            "total_units": total_units,
        }
    )
    for key in ("total_code", "matched_code"):
        if key in payload:
            payload[key] = str(payload[key])
    return payload


def objdiff_report(inventory: Inventory) -> dict:
    """Render an objdiff Report version 2 document.

    Semantic-complete units are reported at 100.0 fuzzy match. That is the only
    mechanism the schema offers for a unit to count toward decomp.dev's headline
    (`matched_code_percent`), and it is a claim about THIS project's definition of
    done, which `docs/DECOMP_DEV.md` states explicitly. `metadata.complete` is
    left false everywhere so the dashboard's separate "fully linked" figure stays
    at zero rather than restating the same claim in the language of linking.
    """
    units = []
    for unit in inventory.units:
        item_measures = _measures(
            total_code=unit.size,
            matched_code=unit.size if unit.credited else 0,
            total_functions=1 if unit.is_function else 0,
            matched_functions=1 if unit.credited else 0,
        )
        function_item = {
            "name": unit.neutral_name,
            "size": str(unit.size),
            "fuzzy_match_percent": 100.0 if unit.credited else 0.0,
            "metadata": _drop_zero(
                {
                    "demangled_name": unit.neutral_name,
                    "virtual_address": str(unit.address) if unit.address is not None else None,
                }
            ),
        }
        metadata = _drop_zero(
            {
                "complete": False,
                "module_name": unit.region,
                "source_path": unit.source,
                "progress_categories": [unit.category],
            }
        )
        units.append(
            _drop_zero(
                {
                    "name": unit.unit_name,
                    "measures": item_measures,
                    # A remainder unit is not a function and must not say it is.
                    "functions": [function_item] if unit.is_function else [],
                    "metadata": metadata,
                }
            )
        )

    categories = []
    for category_id, totals in inventory.category_totals().items():
        categories.append(
            {
                "id": category_id,
                "name": CATEGORY_NAMES[category_id],
                "measures": _measures(
                    total_code=totals["bytes"],
                    matched_code=totals["complete_bytes"],
                    total_functions=totals["functions"],
                    matched_functions=totals["complete_functions"],
                ),
            }
        )

    return {
        "measures": _measures(
            total_code=inventory.tracked_executable_bytes,
            matched_code=inventory.complete_bytes,
            total_functions=inventory.tracked_functions,
            matched_functions=inventory.complete_functions,
            total_units=len(inventory.units),
        ),
        "units": units,
        "version": REPORT_VERSION,
        "categories": categories,
    }


def render_report_json(report: dict) -> str:
    """Serialise deterministically, LF only, first byte `{`.

    objdiff decides JSON-vs-protobuf from the FIRST BYTE, so a BOM or leading
    whitespace would make decomp.dev fail to parse the artifact.
    """
    text = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if not text.startswith("{"):
        raise DecompDevError("the report must start with '{' as its first byte")
    return text


def committed_report_measures(path: Path | None = None) -> dict | None:
    """The `measures` block of the committed report, if there is one."""
    path = Path(path or REPORT_PATH)
    if not path.exists():
        return None
    document = json.loads(path.read_text(encoding="utf-8"))
    return document.get("measures")


# ---------------------------------------------------------------------------
# the README progress block
# ---------------------------------------------------------------------------
#: The front page carries a generated block between these markers, so the public
#: README and the decomp.dev dashboard are produced by ONE command from ONE set of
#: evidence and neither can drift from the other. Nobody edits the block by hand.
README_PATH = _identity.REPO_ROOT / "README.md"
PROGRESS_START = "<!-- progress:start -->"
PROGRESS_END = "<!-- progress:end -->"

_GENERATED_BY = (
    "<!-- Generated by `python -m buusfury decompdev-report --sync-readme` "
    "from the committed reconstruction evidence. Do not edit by hand. -->"
)


def render_progress_block(inventory: Inventory) -> str:
    """The public progress table, from the same evidence as the report."""
    functions = inventory.complete_functions
    total_functions = inventory.tracked_functions
    credited = inventory.complete_bytes
    total_bytes = inventory.tracked_executable_bytes
    return "\n".join(
        [
            PROGRESS_START,
            _GENERATED_BY,
            "",
            "| Metric | Progress |",
            "| --- | ---: |",
            "| Semantically reconstructed functions | %d / %d (%.2f%%) |"
            % (functions, total_functions, _pct(functions, total_functions, 2)),
            "| Reconstructed executable bytes | %s / %s (%.2f%%) |"
            % (f"{credited:,}", f"{total_bytes:,}", _pct(credited, total_bytes, 2)),
            "| Overall semantic code coverage | %.3f%% |"
            % _pct(credited, total_bytes, 3),
            PROGRESS_END,
        ]
    )


def readme_progress_findings(
    inventory: Inventory, path: Path | None = None
) -> list[str]:
    """Problems with the README's generated progress block."""
    path = Path(path or README_PATH)
    if not path.exists():
        return [f"{path.name} is missing; the project needs a front page"]
    text = path.read_text(encoding="utf-8")
    if PROGRESS_START not in text or PROGRESS_END not in text:
        return [
            f"{path.name} has no {PROGRESS_START} ... {PROGRESS_END} block; the "
            "progress table is generated, so the markers must be present"
        ]
    begin = text.index(PROGRESS_START)
    end = text.index(PROGRESS_END) + len(PROGRESS_END)
    current = text[begin:end]
    expected = render_progress_block(inventory)
    if current.strip() != expected.strip():
        return [
            f"{path.name} progress table is stale; regenerate it with "
            "'python -m buusfury decompdev-report --sync-readme'"
        ]
    return []


def sync_readme(inventory: Inventory, path: Path | None = None) -> bool:
    """Rewrite the delimited block in place. True when the file changed."""
    path = Path(path or README_PATH)
    text = path.read_text(encoding="utf-8")
    if PROGRESS_START not in text or PROGRESS_END not in text:
        raise DecompDevError(
            f"{path.name} has no {PROGRESS_START} ... {PROGRESS_END} block to fill in"
        )
    begin = text.index(PROGRESS_START)
    end = text.index(PROGRESS_END) + len(PROGRESS_END)
    updated = text[:begin] + render_progress_block(inventory) + text[end:]
    if updated == text:
        return False
    # newline="" preserves the file's existing endings, so a CRLF checkout is not
    # silently rewritten and the committed block stays byte-stable.
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(updated)
    return True


# ---------------------------------------------------------------------------
# structural validation against the upstream schema
# ---------------------------------------------------------------------------
#: The objdiff Report message, as `objdiff-core/protos/report.proto` defines it.
#: The validator below walks our document against this table, so a misspelled or
#: invented field is a FAILURE rather than something decomp.dev silently drops.
REPORT_SCHEMA: dict[str, set[str]] = {
    "report": {"measures", "units", "version", "categories"},
    "measures": {
        "fuzzy_match_percent",
        "total_code",
        "matched_code",
        "matched_code_percent",
        "total_data",
        "matched_data",
        "matched_data_percent",
        "total_functions",
        "matched_functions",
        "matched_functions_percent",
        "complete_code",
        "complete_code_percent",
        "complete_data",
        "complete_data_percent",
        "total_units",
        "complete_units",
    },
    "unit": {"name", "measures", "sections", "functions", "metadata"},
    "unit_metadata": {
        "complete",
        "module_name",
        "module_id",
        "source_path",
        "progress_categories",
        "auto_generated",
    },
    "item": {"name", "size", "fuzzy_match_percent", "metadata", "address"},
    "item_metadata": {"demangled_name", "virtual_address"},
    "category": {"id", "name", "measures"},
}

#: Every string the report is allowed to contain, by field. A value that is not
#: one of these cannot be produced from the committed provenance, which is what
#: makes "no cartridge bytes travel" a property of the document rather than a
#: promise. `address` and `size` are decimal strings in the objdiff schema.
_ALLOWED_STRINGS: dict[str, re.Pattern[str]] = {
    "function_unit_name": re.compile(r"^(rom|iwram)/sub_[0-9A-F]{8}$"),
    "remainder_unit_name": re.compile(r"^unattributed/[a-z0-9_]+$"),
    "module_name": re.compile(r"^[A-Za-z0-9_]+$"),
    "source_path": re.compile(r"^src/[A-Za-z0-9_./-]+$"),
    "item_name": re.compile(r"^sub_[0-9A-F]{8}$"),
    "decimal": re.compile(r"^[0-9]{1,20}$"),
}

#: Nothing the generator can emit is anywhere near this long. The bound is a
#: second layer behind the value checks: a future field that smuggles content
#: still has to fit through it.
_MAX_STRING_LENGTH = 64


def proprietary_payload_findings(report: dict, inventory: "Inventory") -> list[str]:
    """Prove no cartridge content can reach the public artifact.

    The report is built from committed provenance: addresses, sizes, neutral
    symbols and relative source paths. Rather than heuristically hunting for
    "binary-looking" strings, this checks EVERY string value against what the
    generator is able to produce, BY VALUE where the value set is closed (unit
    names are `sub_<address>`, module names and remainder names are region ids,
    category ids are the declared ones). A field that could carry bytes fails the
    check by construction.
    """
    problems: list[str] = []
    region_ids = {region["id"] for region in inventory.regions}
    unit_names = {unit.unit_name for unit in inventory.units}

    def bad(where: str, detail: str) -> None:
        problems.append(f"{where}: {detail}")

    def validate(where: str, key: str, value) -> None:
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                validate(where, sub_key, sub_value)
            return
        if isinstance(value, list):
            for entry in value:
                validate(where, key, entry)
            return
        if isinstance(value, bool) or value is None or isinstance(value, (int, float)):
            return
        if not isinstance(value, str):
            bad(f"{where}.{key}", f"unexpected {type(value).__name__} value")
            return
        if len(value) > _MAX_STRING_LENGTH:
            bad(f"{where}.{key}", f"string is {len(value)} characters long")
            return
        if key == "name":
            # A unit name is one the inventory itself produced; an item name is a
            # neutral symbol. Neither is a free-form string.
            if value in unit_names:
                return
            if _ALLOWED_STRINGS["item_name"].match(value):
                return
            bad(f"{where}.name", f"{value!r} is not a tracked unit or neutral symbol")
        elif key == "id":
            if value not in CATEGORY_NAMES:
                bad(f"{where}.id", f"{value!r} is not a declared category")
        elif key == "demangled_name":
            if not _ALLOWED_STRINGS["item_name"].match(value):
                bad(f"{where}.demangled_name", f"{value!r} is not a symbol name")
        elif key == "module_name":
            if value not in region_ids and value != "iwram_overlay":
                bad(f"{where}.module_name", f"{value!r} is not a tracked region")
        elif key == "source_path":
            if not _ALLOWED_STRINGS["source_path"].match(value):
                bad(f"{where}.source_path", f"{value!r} is not a repository-relative path")
        elif key in ("size", "total_code", "matched_code", "total_data", "matched_data",
                     "complete_code", "complete_data", "virtual_address", "address"):
            if not _ALLOWED_STRINGS["decimal"].match(value):
                bad(f"{where}.{key}", f"{value!r} is not a decimal integer string")
        elif key == "progress_categories":
            if value not in CATEGORY_NAMES:
                bad(f"{where}.progress_categories", f"{value!r} is not a declared category")
        else:
            bad(f"{where}.{key}", f"unexpected string field {value!r}")

    validate("report", "measures", report.get("measures", {}))
    for index, unit in enumerate(report.get("units", [])):
        where = f"units[{index}]"
        for key in ("name", "measures", "functions", "metadata"):
            validate(where, key, unit.get(key))
        for item_index, item in enumerate(unit.get("functions", []) or []):
            item_where = f"{where}.functions[{item_index}]"
            for key in ("name", "size", "fuzzy_match_percent", "metadata"):
                validate(item_where, key, item.get(key))
    for index, category in enumerate(report.get("categories", [])):
        where = f"categories[{index}]"
        validate(where, "id", category.get("id"))
        if category.get("name") != CATEGORY_NAMES.get(category.get("id")):
            bad(
                f"{where}.name",
                f"{category.get('name')!r} does not match the declared name for "
                f"{category.get('id')!r}",
            )
        validate(where, "measures", category.get("measures", {}))
    return problems


def report_schema_findings(report: dict) -> list[str]:
    """Walk the document against the upstream field table.

    `objdiff` decides JSON-vs-protobuf from the first byte, `Report::migrate()`
    rejects any version but 0/1/2, and its deserialiser is generated from the
    proto, so an invented field name is at best ignored and at worst a parse
    failure. This validator makes that a local, testable invariant.
    """
    problems: list[str] = []

    def check_keys(where: str, payload: dict, kind: str) -> None:
        unknown = sorted(set(payload) - REPORT_SCHEMA[kind])
        if unknown:
            problems.append(f"{where}: not objdiff Report fields: {unknown}")

    check_keys("report", report, "report")

    if report.get("version") != REPORT_VERSION:
        problems.append(
            f"report.version is {report.get('version')!r}, objdiff requires "
            f"{REPORT_VERSION}"
        )

    measures = report.get("measures")
    if not isinstance(measures, dict):
        problems.append("report.measures is missing")
    else:
        check_keys("report.measures", measures, "measures")

    units = report.get("units")
    if not isinstance(units, list):
        problems.append("report.units is missing")
        units = []
    seen_names: dict[str, int] = {}
    for index, unit in enumerate(units):
        where = f"units[{index}]"
        if not isinstance(unit, dict):
            problems.append(f"{where}: not an object")
            continue
        check_keys(where, unit, "unit")
        name = unit.get("name")
        if not isinstance(name, str) or not name:
            problems.append(f"{where}: missing name")
        else:
            seen_names[name] = seen_names.get(name, 0) + 1
        if not isinstance(unit.get("measures"), dict):
            problems.append(f"{where}: missing measures")
        else:
            check_keys(f"{where}.measures", unit["measures"], "measures")
        metadata = unit.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            problems.append(f"{where}.metadata: not an object")
        elif isinstance(metadata, dict):
            check_keys(f"{where}.metadata", metadata, "unit_metadata")
        for item_index, item in enumerate(unit.get("functions", []) or []):
            item_where = f"{where}.functions[{item_index}]"
            if not isinstance(item, dict):
                problems.append(f"{item_where}: not an object")
                continue
            check_keys(item_where, item, "item")
            if not isinstance(item.get("size"), str):
                problems.append(f"{item_where}: size must be a JSON string (uint64)")
            item_metadata = item.get("metadata")
            if isinstance(item_metadata, dict):
                check_keys(f"{item_where}.metadata", item_metadata, "item_metadata")

    duplicates = sorted(n for n, count in seen_names.items() if count > 1)
    if duplicates:
        problems.append(f"duplicate unit names in the report: {duplicates}")

    categories = report.get("categories")
    if not isinstance(categories, list):
        problems.append("report.categories is missing")
        categories = []
    for index, category in enumerate(categories):
        where = f"categories[{index}]"
        if not isinstance(category, dict):
            problems.append(f"{where}: not an object")
            continue
        check_keys(where, category, "category")
        if not isinstance(category.get("id"), str) or not category.get("id"):
            problems.append(f"{where}: missing id")
        if not isinstance(category.get("name"), str) or not category.get("name"):
            problems.append(f"{where}: missing name")
        if isinstance(category.get("measures"), dict):
            check_keys(f"{where}.measures", category["measures"], "measures")

    return problems


def category_totals(report: dict) -> list[str]:
    """Category measures must be the sum of their member units' measures."""
    problems: list[str] = []
    per_unit: dict[str, list[int]] = {}
    for unit in report.get("units", []):
        for category_id in unit.get("metadata", {}).get("progress_categories", []) or []:
            measures = unit.get("measures", {})
            slot = per_unit.setdefault(category_id, [0, 0, 0, 0])
            slot[0] += int(measures.get("total_code", 0))
            slot[1] += int(measures.get("matched_code", 0))
            slot[2] += int(measures.get("total_functions", 0))
            slot[3] += int(measures.get("matched_functions", 0))
    for category in report.get("categories", []):
        measures = category.get("measures", {})
        expected = per_unit.get(category.get("id"), [0, 0, 0, 0])
        actual = [
            int(measures.get("total_code", 0)),
            int(measures.get("matched_code", 0)),
            int(measures.get("total_functions", 0)),
            int(measures.get("matched_functions", 0)),
        ]
        if actual != expected:
            problems.append(
                f"category {category.get('id')!r}: measures {actual} do not equal the "
                f"sum of its member units {expected}"
            )
    return problems


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
#: Distinguishes "the caller did not supply the previous measures" from "there is
#: no committed report yet".
_UNSET = object()


def check(
    inventory: Inventory,
    *,
    report_path: Path | None = None,
    readme_path: Path | None = None,
    previous_measures: object = _UNSET,
) -> tuple[list[str], str]:
    """Every closeout invariant. Returns (problems, decomp.dev report line).

    `previous_measures` lets a caller that is ABOUT TO OVERWRITE the committed
    report capture its old measures first, so the change line reports the real
    movement. Without it, `--out <committed report> --check` would compare the
    fresh document against itself and always answer "unchanged".
    """
    report_path = Path(report_path or REPORT_PATH)
    problems = list(inventory.problems)

    report = objdiff_report(inventory)
    first = render_report_json(report)
    second = render_report_json(objdiff_report(inventory))
    if first != second:
        problems.append("report generation is not deterministic")

    problems += report_schema_findings(report)
    problems += category_totals(report)
    problems += proprietary_payload_findings(report, inventory)
    # The public front page is generated from this same evidence, so a stale
    # README table is a failure and not a documentation nicety.
    problems += readme_progress_findings(inventory, readme_path)

    # The aggregate must equal the units, or the dashboard's headline would not
    # be the sum of what it displays.
    measures = report.get("measures", {})
    if int(measures.get("total_code", 0)) != sum(
        int(u.get("measures", {}).get("total_code", 0)) for u in report["units"]
    ):
        problems.append("aggregate total_code does not equal the sum of the units")
    if int(measures.get("total_functions", 0)) != sum(
        int(u.get("measures", {}).get("total_functions", 0)) for u in report["units"]
    ):
        problems.append("aggregate total_functions does not equal the sum of the units")
    if int(measures.get("matched_code", 0)) != inventory.complete_bytes:
        problems.append("aggregate matched_code does not equal the credited bytes")

    if report_path.exists():
        committed = report_path.read_text(encoding="utf-8")
        if committed != first:
            problems.append(
                f"{report_path.name} is stale: regenerate it with "
                f"'python -m buusfury decompdev-report --out {report_path}'"
            )
    else:
        problems.append(f"{report_path.name} is missing; it is the artifact of record")

    # Absolute local paths must never reach a committed report or a CI artifact.
    if _contains_absolute_path(first):
        problems.append("the report contains an absolute local path")

    previous = (
        committed_report_measures(report_path)
        if previous_measures is _UNSET
        else previous_measures
    )
    line = describe_change(previous, report)
    return problems, line


def _contains_absolute_path(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]:[\\/]", text) or "\\\\" in text)


def describe_change(previous: dict | None, current: dict) -> str:
    """The one-line ticket-report value. Computed, never typed in."""
    new = current.get("measures", {}).get("matched_code_percent", 0.0)
    if previous is None:
        return f"decomp.dev: semantic code {new:.3f}% (report check PASS)"
    old = previous.get("matched_code_percent", 0.0)
    if abs(old - new) < 5e-7:
        return "decomp.dev: unchanged (report check PASS)"
    return f"decomp.dev: semantic code {old:.3f}% -> {new:.3f}% (report check PASS)"


def previous_inventory_totals(path: Path | None = None) -> dict | None:
    """The denominator recorded by the committed inventory, if there is one."""
    path = Path(path or INVENTORY_PATH)
    if not path.exists():
        return None
    document = json.loads(path.read_text(encoding="utf-8"))
    return document.get("denominator")


#: The two denominator quantities that must never fall without review.
DENOMINATOR_KEYS = ("tracked_functions", "tracked_executable_bytes")


def denominator_changes(
    inventory: "Inventory", previous: dict | None
) -> tuple[list[str], list[str]]:
    """Compare the derived denominator with a recorded baseline.

    Returns (changes, problems). A DECREASE is a problem unless the caller has
    explicitly allowed one: a ticket that removes unresolved work would otherwise
    raise its own percentage without reconstructing anything, which is exactly
    the failure mode this whole design exists to prevent.
    """
    changes: list[str] = []
    problems: list[str] = []
    if not previous:
        return changes, problems
    for key in DENOMINATOR_KEYS:
        old = previous.get(key)
        if old is None:
            continue
        new = getattr(inventory, key)
        if new == old:
            continue
        changes.append(f"{key}: {old} -> {new}{' (DECREASE)' if new < old else ''}")
        if new < old:
            problems.append(
                f"DENOMINATOR SHRANK: {key} fell from {old} to {new}. Unresolved work "
                "must stay in the denominator. If the project's executable inventory "
                "legitimately changed, re-run with --allow-denominator-decrease and "
                "record why in the ticket."
            )
    return changes, problems


def compare_inventory(inventory: Inventory, path: Path | None = None) -> list[str]:
    """Differences between the derived inventory and the committed one."""
    path = Path(path or INVENTORY_PATH)
    if not path.exists():
        return [f"{path.name} is missing; run 'python -m buusfury decompdev-inventory --write'"]
    committed = json.loads(path.read_text(encoding="utf-8"))
    derived = inventory.as_dict()
    problems: list[str] = []

    if committed.get("source_sha1") != derived.get("source_sha1"):
        problems.append(
            f"committed inventory describes ROM {committed.get('source_sha1')} but the "
            f"project provenance describes {derived.get('source_sha1')}"
        )

    old_denominator = committed.get("denominator", {})
    new_denominator = derived.get("denominator", {})
    for key in ("tracked_functions", "tracked_executable_bytes"):
        old = old_denominator.get(key)
        new = new_denominator.get(key)
        if old is None or new is None:
            continue
        if new < old:
            problems.append(
                f"DENOMINATOR SHRANK: {key} fell from {old} to {new}. Unresolved work "
                "must stay in the denominator; a reviewed inventory change needs "
                "'decompdev-inventory --write --allow-denominator-decrease'."
            )
        elif new > old:
            problems.append(
                f"denominator grew: {key} rose from {old} to {new}; regenerate the "
                "committed inventory with 'decompdev-inventory --write'"
            )
        elif old != new:
            problems.append(f"{key} changed from {old} to {new}")

    for key in ("complete_functions", "complete_bytes"):
        old = committed.get("semantic_credit", {}).get(key)
        new = derived.get("semantic_credit", {}).get(key)
        if old != new:
            problems.append(
                f"semantic credit changed: {key} {old} -> {new}; regenerate the "
                "committed inventory with 'decompdev-inventory --write'"
            )

    # Keyed by unit name rather than by position, so a table that gained or lost
    # an entry reports the unit that actually moved instead of a one-off
    # comparison of neighbours. Bounded, because a large legitimate change would
    # otherwise bury the reason under hundreds of lines.
    old_units = {unit["unit"]: unit for unit in committed.get("units", [])}
    new_units = {unit["unit"]: unit for unit in derived.get("units", [])}
    if len(old_units) != len(derived.get("units", [])) or len(new_units) != len(
        derived.get("units", [])
    ):
        problems.append("duplicate unit names in the committed inventory")
    added = sorted(set(new_units) - set(old_units))
    removed = sorted(set(old_units) - set(new_units))
    for name in removed[:10]:
        problems.append(
            f"unit removed: {name}; unresolved work must not leave the denominator. "
            "If the executable inventory legitimately changed, review it and re-run "
            "'decompdev-inventory --write --allow-denominator-decrease'"
        )
    if len(removed) > 10:
        problems.append(f"... and {len(removed) - 10} more units removed")
    for name in added[:10]:
        problems.append(
            f"unit added: {name}; regenerate the committed inventory with "
            "'decompdev-inventory --write'"
        )
    if len(added) > 10:
        problems.append(f"... and {len(added) - 10} more units added")
    changed_units = []
    for name in sorted(set(old_units) & set(new_units)):
        before, after = old_units[name], new_units[name]
        if before == after:
            continue
        changed_units.append(
            (name, sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k)))
        )
    for name, fields in changed_units[:10]:
        problems.append(
            f"unit changed: {name} ({', '.join(fields)}); regenerate the committed "
            "inventory with 'decompdev-inventory --write'"
        )
    if len(changed_units) > 10:
        problems.append(f"... and {len(changed_units) - 10} more units changed")

    if committed.get("inputs", {}).get("digests") != derived.get("inputs", {}).get("digests"):
        problems.append(
            "a project provenance file changed since the committed inventory was "
            "generated (config/functions.json, config/rom_map.json or "
            "config/lift_targets.json)"
        )
    # Keyed by path, never by position: a list that gained an entry would
    # otherwise be compared one-off against itself and report "PROVEN -> PROVEN"
    # for a report that did not change at all, while hiding the one that did.
    old_reports = {
        entry["path"]: entry
        for entry in committed.get("inputs", {}).get("lift_reports", [])
    }
    new_reports = {
        entry["path"]: entry
        for entry in derived.get("inputs", {}).get("lift_reports", [])
    }
    for path in sorted(set(new_reports) - set(old_reports)):
        problems.append(
            f"lift report added: {path}; regenerate the committed inventory with "
            "'decompdev-inventory --write'"
        )
    for path in sorted(set(old_reports) - set(new_reports)):
        problems.append(
            f"lift report removed: {path}; a report that no longer exists must not "
            "leave the denominator by accident"
        )
    for path in sorted(set(old_reports) & set(new_reports)):
        before, after = old_reports[path], new_reports[path]
        if before == after:
            continue
        fields = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        details = []
        for field in fields:
            if field in ("semantic", "modern_build", "ads_match", "credit"):
                details.append(f"{field} {before.get(field)!r} -> {after.get(field)!r}")
            else:
                details.append(field)
        problems.append(
            f"lift report changed: {path} ({', '.join(details)}); regenerate the "
            "committed inventory with 'decompdev-inventory --write'"
        )
    return problems
