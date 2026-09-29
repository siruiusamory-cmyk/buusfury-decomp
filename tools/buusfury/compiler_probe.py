"""Compiler probe: establish the ADS 1.2 recipe that reproduces Webfoot machine code.

The question this module exists to answer is narrow and empirical:

    Which ADS 1.2 compiler invocation reproduces the original machine code of
    ordinary Buu's Fury engine functions?

It answers it by compiling reconstructed candidate source and comparing the
emitted bytes against the canonical ROM, byte for byte. Nothing here guesses:
where ARM Developer Suite 1.2 is not installed the whole probe reports
``ADS12_UNAVAILABLE`` (a BLOCKED result) and never a match.

Why the comparison is translation-unit scoped
---------------------------------------------
A Thumb function that loads a constant with ``ldr rX, [pc, #N]`` encodes N as a
displacement to a literal pool. Compiling that function on its own puts the pool
somewhere else and changes N, so a standalone byte comparison would report a
mismatch for correct source. The only rigorous comparison is therefore to
compile the whole original translation unit, place it at its original ROM
address with a controlled linker layout, and compare the entire span including
the literal pool. Per-probe results are slices of that single build.

Modern compilers
----------------
``arm-none-eabi-gcc`` is never evidence about the original compiler. It may only
be used as a labelled DIAGNOSTIC CONTROL that exercises the compile/compare
plumbing, and results produced that way carry
``DIAGNOSTIC_CONTROL_NOT_EVIDENCE`` so they can never be mistaken for a finding.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import capstone

from . import gba as _gba
from . import identity as _identity

# ---------------------------------------------------------------------------
# conclusion vocabulary
# ---------------------------------------------------------------------------

#: The five states a compiler-fingerprint claim may carry. Ordered weakest-first
#: so a report can show how far the evidence actually got.
CONCLUSION_STATES = (
    "UNTESTED",
    "REFUTED",
    "PLAUSIBLE",
    "STRONGLY_SUPPORTED",
    "PROVEN",
)

#: Attached to any result a non-ADS compiler produced. Such a result is plumbing
#: evidence only and must never be reported as a finding about the original build.
DIAGNOSTIC_CONTROL = "DIAGNOSTIC_CONTROL_NOT_EVIDENCE"

#: The two stable blocker codes. A blocked probe is a result, not an error.
BLOCK_ADS_UNAVAILABLE = "ADS12_UNAVAILABLE"
BLOCK_TOOLCHAIN = "TOOLCHAIN_BLOCKED"

#: The lead this ticket starts from, preserved verbatim from asm/GBARam.s line 5.
LEAD_COMMAND_LINE = "tcpp -S -c -cpu ARM7TDMI -O1 src/GBARam.c"

#: ADS 1.2 tool ids, in the order the pipeline needs them.
ADS_COMPILE_TOOLS = ("tcc", "tcpp", "armcc", "armcpp")
ADS_SUPPORT_TOOLS = ("armasm", "armlink", "fromelf")

#: Where probe builds are written. Inside build/, which is gitignored, so no
#: generated object file, linked image or extracted ROM bytes can be committed.
PROBE_WORKSPACE = _identity.REPO_ROOT / "build" / "probes"

MANIFEST_PATH = _identity.CONFIG_DIR / "compiler_probes.json"
MATRIX_PATH = _identity.CONFIG_DIR / "compiler_matrix.json"


class ProbeError(RuntimeError):
    """Raised when a probe cannot be carried out as specified."""


class ToolchainBlocked(RuntimeError):
    """Raised when the compiler needed for a probe is not available.

    Carries a stable ``code`` so callers (and tests) branch on the code rather
    than on message text.
    """

    def __init__(self, code: str, summary: str, details: list[str] | None = None) -> None:
        self.code = code
        self.summary = summary
        self.details = list(details or [])
        super().__init__(f"{code}: {summary}")


# ---------------------------------------------------------------------------
# capstone
# ---------------------------------------------------------------------------
MD = {
    "arm": capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM),
    "thumb": capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB),
}
for _md in MD.values():
    _md.detail = True

ALIGNMENT = {"arm": 4, "thumb": 2}


# ---------------------------------------------------------------------------
# exact function boundaries
# ---------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class FunctionBoundary:
    """One function recovered by chain-walking a translation unit."""

    start: int  #: ROM address
    end: int  #: ROM address, exclusive
    isa: str
    instructions: int
    returns: int
    calls: tuple[int, ...]
    literal_slots: tuple[int, ...]
    problems: tuple[str, ...]
    first: str

    @property
    def size(self) -> int:
        return self.end - self.start

    @property
    def leaf(self) -> bool:
        return not self.calls

    @property
    def name(self) -> str:
        return f"sub_{self.start:08X}"

    def as_dict(self, data: bytes) -> dict:
        offset = self.start - _gba.ROM_BASE
        raw = data[offset : offset + self.size]
        return {
            "name": self.name,
            "rom_address": f"0x{self.start:08X}",
            "file_offset": f"0x{offset:06X}",
            "isa": self.isa,
            "start": f"0x{self.start:08X}",
            "end": f"0x{self.end:08X}",
            "byte_length": self.size,
            "sha1": hashlib.sha1(raw).hexdigest(),
            "instructions": self.instructions,
            "returns": self.returns,
            "leaf": self.leaf,
            "first_instruction": self.first,
            "callees": [f"0x{c:08X}" for c in self.calls],
            "literal_slots": [f"0x{s:08X}" for s in self.literal_slots],
            "problems": list(self.problems),
        }


def _literal_slot(address: int, isa: str, op_str: str) -> int | None:
    """Address of the literal a PC-relative load reads, or None.

    ARM: PC is instruction + 8. Thumb: PC is (instruction + 4) rounded down to a
    word boundary. ``[pc]`` with no displacement is displacement zero - the
    commonest form in a veneer, and the one a displacement-only parser misses.
    """
    if "[pc" not in op_str:
        return None
    if ", #" in op_str:
        try:
            disp = int(op_str.split("[pc, #", 1)[1].split("]", 1)[0].strip(), 0)
        except (IndexError, ValueError):
            return None
    else:
        disp = 0
    if isa == "arm":
        return address + 8 + disp
    return ((address + 4) & ~3) + disp


def chain_walk(
    data: bytes,
    start_address: int,
    end_address: int,
    isa: str,
    *,
    max_instructions: int = 20_000,
) -> list[FunctionBoundary]:
    """Recover exact function boundaries across a contiguous translation unit.

    The algorithm assumes what a compiled translation unit actually is: a
    sequence of functions laid out back to back, each of which terminates on
    every path. It therefore opens a recursive descent at the region start,
    follows conditional joins and tail branches *inside* the unit, treats calls
    as fall-through, and stops a path at ``bx lr``, at ``pop {..., pc}``, or at a
    tail branch that leaves the unit.

    The function ends at the highest-address terminator the descent reached. The
    next function starts immediately after it, because every path of the
    previous one already terminated - which is exactly the property that makes
    the boundary evidence rather than a heuristic window.

    Anything the descent cannot reach or cannot decode is reported as a problem
    on the boundary it belongs to, so a mixed data/code region fails loudly
    instead of silently producing a plausible-looking function list.
    """
    if isa not in MD:
        raise ProbeError(f"unknown isa: {isa}")
    md = MD[isa]
    align = ALIGNMENT[isa]
    if start_address % align or end_address % align:
        raise ProbeError(
            f"unaligned region for {isa}: 0x{start_address:08X}..0x{end_address:08X}"
        )

    boundaries: list[FunctionBoundary] = []
    cursor = start_address

    while cursor < end_address:
        entry = cursor
        todo = [entry]
        body: dict[int, capstone.CsInsn] = {}
        terminals: list[tuple[int, int]] = []
        calls: list[int] = []
        literals: set[int] = set()
        problems: list[str] = []

        while todo:
            address = todo.pop()
            while True:
                if not (entry <= address < end_address):
                    # A path that leaves the unit is a real gap in the boundary
                    # evidence: the reachable body would extend past the reported
                    # end, so it must be reported rather than silently dropped.
                    if body:
                        problems.append(
                            f"flow left the unit at 0x{address:08X}, past the "
                            f"declared end 0x{end_address:08X}"
                        )
                    break
                if address in body:
                    break
                if len(body) > max_instructions:
                    problems.append("instruction cap reached; unit is not linear code")
                    address = end_address
                    break
                offset = address - _gba.ROM_BASE
                if not 0 <= offset < len(data):
                    problems.append(f"0x{address:08X} is outside the image")
                    break
                ins = next(iter(md.disasm(data[offset : offset + 4], address)), None)
                if ins is None:
                    problems.append(f"undecodable instruction at 0x{address:08X}")
                    break
                body[address] = ins
                mnemonic, op_str = ins.mnemonic, ins.op_str
                following = address + ins.size

                slot = _literal_slot(address, isa, op_str)
                if slot is not None and mnemonic.startswith("ldr"):
                    literals.add(slot)

                if mnemonic == "bx" or (mnemonic in ("pop", "ldm", "ldmia", "ldmfd") and "pc" in op_str):
                    terminals.append((address, ins.size))
                    break
                if mnemonic in ("b", "bl", "blx") and op_str.startswith("#"):
                    target = int(op_str[1:], 16)
                    if mnemonic == "b":
                        if entry <= target < end_address:
                            address = target
                            continue
                        terminals.append((address, ins.size))
                        break
                    calls.append(target & ~1)
                    address = following
                    continue
                if mnemonic.startswith("b") and op_str.startswith("#"):
                    target = int(op_str[1:], 16)
                    if entry <= target < end_address:
                        todo.append(target)
                    else:
                        # A conditional branch out of the unit is a tail call or
                        # an early return the unit does not contain. Following it
                        # is impossible and ignoring it silently would let the
                        # reported body be an unannounced lower bound, so it is
                        # recorded: the boundary's "every path terminates inside
                        # the unit" claim has to be earned, not assumed.
                        problems.append(
                            f"conditional branch at 0x{address:08X} leaves the unit "
                            f"for 0x{target:08X}; the body beyond it is not analysed"
                        )
                address = following

        if not body:
            raise ProbeError(
                f"chain walk stalled at 0x{entry:08X}: no instruction decoded"
            )

        if terminals:
            end = max(address + size for address, size in terminals)
        else:
            end = max(address + body[address].size for address in body)
            problems.append("no terminator found: function extent is a lower bound")

        if end <= entry:
            raise ProbeError(f"chain walk made no progress at 0x{entry:08X}")

        first = body[entry]
        boundaries.append(
            FunctionBoundary(
                start=entry,
                end=end,
                isa=isa,
                instructions=len(body),
                returns=len(terminals),
                calls=tuple(sorted(set(calls))),
                literal_slots=tuple(sorted(literals)),
                problems=tuple(problems),
                first=f"{first.mnemonic} {first.op_str}".strip(),
            )
        )
        cursor = end

    return boundaries


# ---------------------------------------------------------------------------
# the manifest
# ---------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class TranslationUnit:
    """A reconstructed original compilation unit, placed at its ROM address.

    ``code_end_address`` separates the executable body from the trailing literal
    pool. They are one comparison unit but only the body is code; walking the
    pool as instructions is what makes a naive linear sweep invent functions out
    of constants.
    """

    id: str
    rom_address: int
    code_end_address: int
    end_address: int
    isa: str
    source: str
    boundary_evidence: tuple[str, ...]
    confidence: str
    literal_pool: tuple[tuple[int, int], ...]  # (file_offset, value)
    selection: tuple[str, ...]

    @property
    def code_length(self) -> int:
        return self.code_end_address - self.rom_address

    @property
    def length(self) -> int:
        return self.end_address - self.rom_address

    def as_dict(self, data: bytes) -> dict:
        offset = self.rom_address - _gba.ROM_BASE
        raw = data[offset : offset + self.length]
        pool = {
            "rom_address": (
                f"0x{self.literal_pool[0][0] + _gba.ROM_BASE:08X}"
                if self.literal_pool
                else None
            ),
            "file_offset": (
                f"0x{self.literal_pool[0][0]:06X}" if self.literal_pool else None
            ),
            "byte_length": 4 * len(self.literal_pool),
            "words": [
                {"file_offset": f"0x{o:06X}", "value": f"0x{v:08X}"}
                for o, v in self.literal_pool
            ],
        }
        return {
            "id": self.id,
            "rom_address": f"0x{self.rom_address:08X}",
            "file_offset": f"0x{offset:06X}",
            "code_end_address": f"0x{self.code_end_address:08X}",
            "end_address": f"0x{self.end_address:08X}",
            "code_byte_length": self.code_length,
            "byte_length": self.length,
            "sha1": hashlib.sha1(raw).hexdigest(),
            "code_sha1": hashlib.sha1(raw[: self.code_length]).hexdigest(),
            "literal_pool_sha1": hashlib.sha1(raw[self.code_length :]).hexdigest(),
            "isa": self.isa,
            "source_candidate": self.source,
            "confidence": self.confidence,
            "boundary_evidence": list(self.boundary_evidence),
            "selection": list(self.selection),
            "literal_pool": pool,
        }


#: The one translation unit a probe corpus can be built on with exact boundaries.
#: Every value here is re-derived from the canonical ROM by verify_manifest();
#: none of it is taken on trust.
GBARAM_TU = TranslationUnit(
    id="gbaram_tu",
    rom_address=0x0803D4D0,
    code_end_address=0x0803D730,
    end_address=0x0803D740,
    isa="thumb",
    source="src/probes/GBARam.c",
    confidence="proven",
    literal_pool=(
        (0x03D730, 0x02000800),
        (0x03D734, 0x03003488),
        (0x03D738, 0x0000FDFE),
        (0x03D73C, 0x7FFFFFFF),
    ),
    selection=(
        "config/rom_map.json classifies 0x03D4D0-0x03D730 as gbaram_code, "
        "confidence high, executable confirmed",
        "the surviving original command line 'tcpp -S -c -cpu ARM7TDMI -O1 src/GBARam.c' "
        "names a source file the reference build reproduces as this region",
        "the literal pool at 0x03D730 holds exactly the four values "
        "DECOMP-ROM-MAP-001 proved as the fixed region gbaram_literals",
        "an independent chain-walk recovers 8 functions with zero gaps and zero "
        "undecodable bytes, so every boundary is evidence rather than a window",
    ),
    boundary_evidence=(
        "chain-walk recursive descent in Thumb from 0x0803D4D0: 8 functions, all "
        "paths terminated, 0 undecodable bytes, 0 gaps, region covered exactly",
        "one literal pool shared by 7 of the 8 functions sits at the region end "
        "(0x03D730-0x03D740), which is why this is one translation unit",
        "internal call graph measured from the disassembly: 0x0803D5B8 -> "
        "0x0803D4E8; 0x0803D63C -> 0x0803D4E8, 0x0803D56A, 0x0803D520",
        "external callers of 0x0803D5B8 exist at 0x0803D7B2, 0x0803DA84, "
        "0x0803E452 and hundreds of identified engine sites, so the module is "
        "ordinary engine code and not an artefact of a decoder",
    ),
)

#: The eight functions inside GBARAM_TU, as declarations. Each start/end is
#: re-derived and asserted; the pairs here are the expected result, not input.
GBARAM_FUNCTIONS = (
    (0x0803D4D0, 0x0803D4E8, "list head and node-0 pool initialiser"),
    (0x0803D4E8, 0x0803D520, "unlink a node from the free list and mark it busy"),
    (0x0803D520, 0x0803D548, "insert a node at the head of the free list"),
    (0x0803D548, 0x0803D56A, "merge a node with its successor"),
    (0x0803D56A, 0x0803D5B8, "merge a node with its predecessor"),
    (0x0803D5B8, 0x0803D63C, "allocate: search the free list for a fitting node"),
    (0x0803D63C, 0x0803D712, "free: return a node and coalesce with neighbours"),
    (0x0803D712, 0x0803D730, "sum the sizes of every free node"),
)

#: Regions that must NOT be used as ordinary-engine compiler evidence, recorded
#: so a later ticket cannot quietly promote one of them.
#:
#: Measured from config/rom_map.json: exactly TWO regions are isa=arm with
#: executable=confirmed (reset_code and codec_blob). The ARM veneer at
#: 0x08049114 is NOT a region start; it lies inside
#: code_candidate_span_6_048F14 (0x08048F14..0x08049324, code_candidate, medium,
#: executable=probable), which is also the one ARM candidate that does not
#: decode as ARM at all. That is why the ARM probe corpus is legitimately empty
#: rather than merely unselected.
CONTROLS = (
    {
        "id": "reset_crt",
        "rom_address": "0x080000C0",
        "region_id": "reset_code",
        "isa": "arm",
        "region_confidence": "proven",
        "region_executable": "confirmed",
        "role": "control",
        "excluded_because": (
            "startup/CRT code. The cartridge header branches here and it hands off "
            "to the ADS C runtime; it is hand-written or library origin and says "
            "nothing about how gameplay C was compiled"
        ),
    },
    {
        "id": "crt_veneer",
        "rom_address": "0x08049114",
        "region_id": "code_candidate_span_6_048F14",
        "isa": "arm",
        "region_confidence": "medium",
        "region_executable": "probable",
        "role": "control",
        "excluded_because": (
            "the ADS C runtime static-initialiser veneer reached from the reset "
            "path; library code, not engine code. NOTE this address is not a region "
            "start: it lies inside code_candidate_span_6_048F14, and the region's "
            "own first word does not decode as ARM."
        ),
    },
    {
        "id": "codec_blob",
        "rom_address": "0x087B79A4",
        "region_id": "codec_blob",
        "isa": "arm",
        "region_confidence": "high",
        "region_executable": "confirmed",
        "role": "control",
        "excluded_because": (
            "may be hand-written or library/codec assembly and is not "
            "representative; its clean ARM prologues (push {r8,r9,r10,r11}) are "
            "not enough to attribute it to the engine's C compiler"
        ),
    },
)

#: Candidates examined and rejected, with the measurement that rejected them.
REJECTIONS = (
    {
        "id": "code_reachable_055324",
        "rom_address": "0x08055324",
        "map_claim": "code, high confidence, executable confirmed, thumb",
        "rejected_because": (
            "DATA, not code. It disassembles only as a repeating pair "
            "'cmp rX, #imm' / 'lsrs r0, r0, #0x20', i.e. a table of halfwords "
            "followed by 0x0808. This is why a map classification of 'high' is "
            "not sufficient evidence to build a probe on."
        ),
    },
    {
        "id": "code_candidate_span_6_048F14",
        "rom_address": "0x08048F14",
        "map_claim": "code_candidate, medium confidence, arm",
        "rejected_because": (
            "does not decode as ARM at all: capstone emits no instruction for the "
            "first word, which is the NV-condition signature of data. No ARM "
            "probe can be built here."
        ),
    },
    {
        "id": "code_candidate_span_5_03D2D0",
        "rom_address": "0x0803D2D0",
        "map_claim": "code_candidate, medium confidence, thumb",
        "rejected_because": (
            "chain-walk reaches an impossible '40 bytes / 137 instructions' entry "
            "and two functions with no terminator, so the span mixes inline data "
            "with code and its boundaries cannot be established."
        ),
    },
    {
        "id": "code_reachable_02E1C0",
        "rom_address": "0x0802E1C0",
        "map_claim": "code, high confidence, executable confirmed, thumb",
        "rejected_because": (
            "reachable and real code, but not independently bounded: the region is "
            "a 4096-byte window and its first function is 1022 bytes with 20 "
            "callees, which is a poor probe (many relocation sites, large control "
            "flow). Deferred, not refuted."
        ),
    },
    {
        "id": "sub_0803D4D0_inventory_entry",
        "rom_address": "0x0803D4D0",
        "map_claim": "config/functions.json size=620",
        "rejected_because": (
            "the size is analysis.decode_run(limit=0x400).bytes_ok, not a boundary. "
            "620 bytes from 0x0803D4D0 runs to 0x0803D73C and spans the whole unit "
            "plus 12 bytes of its literal pool, and its callee list "
            "(0x0803D4E8, 0x0803D520, 0x0803D56A) is those neighbouring functions' "
            "calls attributed to it. The measured boundary is 24 bytes with no calls."
        ),
    },
    {
        "id": "sub_0803D5B8_inventory_entry",
        "rom_address": "0x0803D5B8",
        "map_claim": "config/functions.json size=388",
        "rejected_because": (
            "same defect: 388 bytes from 0x0803D5B8 runs to 0x0803D73C, straight "
            "through 0x0803D63C and 0x0803D712 and into the pool, and carries the "
            "same contaminated callee list. The measured boundary is 132 bytes with "
            "one distinct callee, 0x0803D4E8."
        ),
    },
)

#: Candidate configurations to test once a compiler is present. The first entry
#: is the historical lead and is tried first.
MATRIX_CONFIGS = (
    ("tcpp", "ARM7TDMI", "-O1", "the historical lead, verbatim"),
    ("tcpp", "ARM7TDMI", "-O0", "negative control: optimisation off"),
    ("tcpp", "ARM7TDMI", "-O2", "negative control: more optimisation"),
    ("tcc", "ARM7TDMI", "-O1", "C frontend instead of C++"),
    ("armcpp", "ARM7TDMI", "-O1", "ARM frontend, C++"),
    ("armcc", "ARM7TDMI", "-O1", "ARM frontend, C"),
)


def _file_offset(address: int) -> int:
    return address - _gba.ROM_BASE


def _inventory_index() -> dict[int, dict]:
    """config/functions.json keyed by address, or {} when it is absent.

    Used only as a cross-check. It is never boundary input: its `size` is a
    decode extent, and it is the artefact this ticket is testing against.

    A malformed inventory is reported as a ProbeError rather than a KeyError or
    a JSONDecodeError, because it is an input problem and not a probe defect.
    """
    path = _identity.CONFIG_DIR / "functions.json"
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProbeError(f"{path} is not readable JSON: {exc}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("functions"), list):
        raise ProbeError(f"{path} has no 'functions' list")
    index: dict[int, dict] = {}
    for entry in raw["functions"]:
        try:
            address = int(entry["address"], 16) & ~1
        except (KeyError, TypeError, ValueError) as exc:
            raise ProbeError(f"{path} has an entry without a usable address") from exc
        index[address] = {
            "size": entry.get("size"),
            "confidence": entry.get("confidence"),
            "discovery": entry.get("discovery") or [],
            "isa": entry.get("isa"),
        }
    return index


def _inventory_digest() -> str | None:
    """SHA-1 of config/functions.json, so inventory drift is distinguishable.

    The manifest embeds inventory-derived fields. Without pinning the inventory
    itself, a changed inventory would look like a manifest that disagrees with
    the ROM, and the error message would blame the wrong file.
    """
    path = _identity.CONFIG_DIR / "functions.json"
    if not path.is_file():
        return None
    return hashlib.sha1(path.read_bytes()).hexdigest()


def derive_manifest(data: bytes) -> dict:
    """Rebuild the whole probe manifest from the canonical ROM.

    Every measured field (addresses, lengths, digests, boundaries, callees,
    literal values) is recomputed here, so the committed manifest can be checked
    against the ROM on any machine instead of being believed.
    """
    tu = GBARAM_TU
    boundaries = chain_walk(data, tu.rom_address, tu.code_end_address, tu.isa)
    by_start = {b.start: b for b in boundaries}
    problems: list[str] = []

    if len(boundaries) != len(GBARAM_FUNCTIONS):
        problems.append(
            f"chain walk recovered {len(boundaries)} functions, expected "
            f"{len(GBARAM_FUNCTIONS)}"
        )
    for expected_start, expected_end, _why in GBARAM_FUNCTIONS:
        found = by_start.get(expected_start)
        if found is None:
            problems.append(f"0x{expected_start:08X} was not recovered")
            continue
        if found.end != expected_end:
            problems.append(
                f"0x{expected_start:08X}: recovered end 0x{found.end:08X}, "
                f"expected 0x{expected_end:08X}"
            )
        if found.problems:
            problems.append(f"0x{expected_start:08X}: {'; '.join(found.problems)}")
    if sum(b.size for b in boundaries) != tu.code_length:
        problems.append("recovered functions do not cover the code body exactly")
    if boundaries and boundaries[-1].end != tu.code_end_address:
        problems.append(
            f"code body ends at 0x{boundaries[-1].end:08X}, "
            f"expected 0x{tu.code_end_address:08X}"
        )
    if tu.literal_pool[0][0] != tu.code_end_address - _gba.ROM_BASE:
        problems.append("literal pool does not begin at the end of the code body")

    pool_words = []
    for offset, expected in tu.literal_pool:
        actual = int.from_bytes(data[offset : offset + 4], "little")
        if actual != expected:
            problems.append(
                f"literal at 0x{offset:06X} is 0x{actual:08X}, "
                f"expected 0x{expected:08X}"
            )
        pool_words.append((offset, actual))

    probes = []
    for expected_start, expected_end, role in GBARAM_FUNCTIONS:
        found = by_start.get(expected_start)
        if found is None:
            continue
        entry = found.as_dict(data)
        entry["role"] = role
        entry["translation_unit"] = tu.id
        entry["confidence"] = "proven"
        entry["boundary_evidence"] = [
            "recovered by chain-walk recursive descent over gbaram_tu; every path "
            "terminates, so the next function starts at the terminator's end",
            f"translation unit {tu.id} covers 0x{tu.rom_address:08X}.."
            f"0x{tu.end_address:08X} with zero gaps and zero undecodable bytes",
        ]
        entry["relocations"] = (
            "literal load present; comparison is translation-unit scoped so the "
            "pool displacement is reproduced rather than normalised away"
            if found.literal_slots
            else "none: no PC-relative literal load, so this function is byte "
            "comparable on its own as well"
        )
        probes.append(entry)

    inventory = _inventory_index()
    size_disagreements = []
    for entry in probes:
        address = int(entry["rom_address"], 16)
        recorded = inventory.get(address)
        entry["in_function_inventory"] = recorded is not None
        entry["inventory_confidence"] = recorded["confidence"] if recorded else None
        entry["inventory_discovery"] = recorded["discovery"] if recorded else []
        entry["inventory_size"] = recorded["size"] if recorded else None
        if recorded is not None and recorded["size"] != entry["byte_length"]:
            # EXPECTED, not a fault: the inventory's size is a decode extent
            # capped at 0x400, so it overruns small functions. Reported as a
            # finding in its own field, because a real consistency problem is a
            # contradiction in THIS manifest and must not be diluted by these.
            size_disagreements.append(
                {
                    "name": entry["name"],
                    "inventory_size": recorded["size"],
                    "measured_boundary": entry["byte_length"],
                    "explanation": (
                        "config/functions.json's size is "
                        "analysis.decode_run(limit=0x400).bytes_ok, so it ran past "
                        "the function end. The measured boundary comes from a chain "
                        "walk in which every path terminates."
                    ),
                }
            )

    gaps = [
        {
            "name": entry["name"],
            "rom_address": entry["rom_address"],
            "why_absent": (
                "no BL/BLX site anywhere in the image targets this address, and it "
                "is not a literal-pool code pointer, so the previous ticket's "
                "branch-target inventory could not have found it. It is present in "
                "the image and inside a proven code region."
            ),
            "independent_evidence": [
                f"decodes completely as {entry['isa']} over all "
                f"{entry['byte_length']} bytes with no undecodable or leftover bytes",
                f"terminates on every path ({entry['returns']} return site(s)), which "
                "is what ends the previous function's boundary",
                "lies inside gbaram_tu, whose boundaries are otherwise confirmed by "
                "the shared literal pool and by the surviving build command line",
            ],
            "consequence": (
                "recorded as a measured gap in config/functions.json rather than "
                "dropped, because the function is real and its bytes must be part of "
                "the translation-unit comparison"
            ),
        }
        for entry in probes
        if not entry["in_function_inventory"]
    ]

    return {
        "schema": 1,
        "source_sha1": hashlib.sha1(data).hexdigest(),
        "inventory_sha1": _inventory_digest(),
        "inventory_basis": (
            "config/functions.json is pinned by digest because this manifest embeds "
            "three fields derived from it (per-probe inventory_confidence and "
            "inventory_size, inventory_gaps, and inventory_size_disagreements). It "
            "is a cross-check only and is never boundary input."
        ),
        "generated_by": "tools/buusfury/compiler_probe.py derive_manifest()",
        "method": (
            "chain-walk recursive descent in the translation unit's own instruction "
            "set, following internal conditional joins and tail branches, treating "
            "calls as fall-through, and terminating a path at bx lr, pop {...,pc} or "
            "a tail branch leaving the unit"
        ),
        "notes": [
            "Boundaries are evidence, not a window: the previous function's every "
            "path terminated before the next function starts.",
            "config/functions.json is NOT used for boundaries. Its `size` field is "
            "analysis.decode_run(limit=0x400).bytes_ok and overruns small functions: "
            "it records 620 bytes for 0x0803D4D0 against a measured 24, and 388 bytes "
            "for 0x0803D5B8 against a measured 132. Both spans run to 0x0803D73C, "
            "through neighbouring functions and into the literal pool.",
            "No semantic name is assigned. Probe names are sub_<address>. The `role` "
            "strings describe each function's measured shape (leaf, returns, calls, "
            "literal loads) rather than claiming a semantic name.",
            "The inventory's confidence is its own discovery method's confidence: a "
            "BL-target entry stays `medium` there even when an independent chain "
            "walk proves the boundary. The two are recorded separately on purpose.",
        ],
        "translation_units": [tu.as_dict(data)],
        "probes": probes,
        "controls": list(CONTROLS),
        "rejections": list(REJECTIONS),
        "inventory_gaps": gaps,
        "inventory_size_disagreements": size_disagreements,
        "consistency_problems": problems,
        "counts": {
            "probes": len(probes),
            "thumb": sum(1 for p in probes if p["isa"] == "thumb"),
            "arm": sum(1 for p in probes if p["isa"] == "arm"),
            "leaf": sum(1 for p in probes if p["leaf"]),
            "non_leaf": sum(1 for p in probes if not p["leaf"]),
            "with_literal_load": sum(1 for p in probes if p["literal_slots"]),
            "translation_units": 1,
        },
    }


def verify_manifest(data: bytes, path: Path | None = None) -> list[str]:
    """Regenerate the manifest and return every disagreement with the file on disk.

    The WHOLE document is compared, not a hand-picked subset. An earlier version
    of this function compared six keys and would have accepted a manifest whose
    ``controls``, ``rejections``, ``method``, ``notes``, ``schema`` and
    ``generated_by`` had been rewritten to say anything at all, which is exactly
    the kind of drift a verification step exists to catch.

    Inventory drift is reported separately from ROM drift, because the manifest
    embeds fields derived from ``config/functions.json`` and blaming the ROM for
    a changed inventory would point a reader at the wrong file.
    """
    try:
        committed = json.loads((path or MANIFEST_PATH).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{path or MANIFEST_PATH} does not exist"]
    except json.JSONDecodeError as exc:
        return [f"{path or MANIFEST_PATH} is not readable JSON: {exc}"]

    problems: list[str] = []
    derived = derive_manifest(data)
    problems.extend(derived["consistency_problems"])

    # Inventory drift first: if the inventory changed, the inventory-derived
    # fields in `probes`, `inventory_gaps` and `inventory_size_disagreements`
    # will differ for a reason that is not the ROM.
    committed_digest = committed.get("inventory_sha1")
    current_digest = derived.get("inventory_sha1")
    if committed_digest != current_digest:
        problems.append(
            "INVENTORY DRIFT: config/functions.json has changed since this "
            f"manifest was generated (committed {committed_digest}, current "
            f"{current_digest}). The manifest's inventory-derived fields cannot be "
            "compared meaningfully until it is regenerated with --write-manifest. "
            "This is not evidence about the ROM."
        )

    # Every key of the regenerated document must appear, and match.
    for key in sorted(set(derived) | set(committed)):
        if key == "inventory_sha1":
            continue
        if key not in committed:
            problems.append(f"manifest is missing the field {key!r}")
        elif key not in derived:
            problems.append(f"manifest has an unexpected field {key!r}")
        elif committed[key] != derived[key]:
            problems.append(
                f"manifest field {key!r} disagrees with the value re-derived from "
                "the canonical ROM"
            )
    return problems


def verify_matrix(data: bytes, sha1: str, path: Path | None = None) -> list[str]:
    """Regenerate config/compiler_matrix.json and report every disagreement.

    The matrix had no drift check at all, so a stale one could sit in the repo
    claiming a result no run produced.
    """
    target = path or MATRIX_PATH
    if not target.is_file():
        return [f"{target} does not exist"]
    try:
        committed = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{target} is not readable JSON: {exc}"]
    derived = build_matrix(data, sha1)
    if committed == derived:
        return []
    differing = sorted(
        key for key in set(committed) | set(derived) if committed.get(key) != derived.get(key)
    )
    return [
        f"{target} does not match the matrix re-derived on this machine "
        f"(committed result {committed.get('result')!r}, derived "
        f"{derived.get('result')!r}; differing fields: {', '.join(differing) or 'none'})"
    ]


def load_manifest(path: Path | None = None) -> dict:
    return json.loads((path or MANIFEST_PATH).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# extraction and comparison
# ---------------------------------------------------------------------------
def extract(data: bytes, rom_address: int, length: int) -> bytes:
    """Target machine bytes for a probe, read straight from the canonical image."""
    offset = _file_offset(rom_address)
    if offset < 0 or offset + length > len(data):
        raise ProbeError(
            f"0x{rom_address:08X}+{length} lies outside the image"
        )
    return data[offset : offset + length]


@dataclasses.dataclass(frozen=True)
class ByteDiff:
    """A structured, deterministic comparison of two machine-code spans.

    Instruction counts are derived from the TARGET's instruction boundaries,
    never from a positional walk of both streams. That matters: capstone reports
    different Thumb encodings as the same ``(mnemonic, op_str)`` pair (for
    example ``0x4280`` and ``0x4500`` both render as ``cmp r0, r0``), so a
    positional text comparison can report zero differing instructions for bytes
    that are plainly different, and can report more differences than there are
    instructions once the two streams have different lengths. Counting how many
    of the target's instructions have a non-identical encoding cannot do either.
    """

    target_size: int
    candidate_size: int
    identical_bytes: int
    first_difference: int | None
    differing_bytes: int
    target_instructions: int
    differing_instructions: int
    exact_match: bool
    base_address: int = 0
    notes: tuple[str, ...] = ()

    @property
    def matching_instructions(self) -> int:
        """Target instructions whose encoding is byte-identical in the candidate.

        Never negative: it is ``target_instructions - differing_instructions``
        and differing can never exceed the target's own count.
        """
        return self.target_instructions - self.differing_instructions

    def as_dict(self) -> dict:
        return {
            "target_size": self.target_size,
            "candidate_size": self.candidate_size,
            "identical_bytes": self.identical_bytes,
            "first_difference": (
                f"0x{self.first_difference:X}" if self.first_difference is not None else None
            ),
            "first_difference_address": (
                f"0x{self.base_address + self.first_difference:08X}"
                if self.first_difference is not None
                else None
            ),
            "differing_bytes": self.differing_bytes,
            "target_instructions": self.target_instructions,
            "differing_instructions": self.differing_instructions,
            "matching_instructions": self.matching_instructions,
            "exact_match": self.exact_match,
            "notes": list(self.notes),
        }


def instruction_spans(data: bytes, base_address: int, isa: str) -> list[tuple[int, int]]:
    """Byte spans of every instruction the target decodes to.

    Returns ``(offset_from_base, size)`` pairs. Offsets, not text, are what the
    comparison keys on.
    """
    spans: list[tuple[int, int]] = []
    for ins in MD[isa].disasm(data, base_address):
        spans.append((ins.address - base_address, ins.size))
    return spans


def disassemble(data: bytes, base_address: int, isa: str) -> list[tuple[int, str, str]]:
    """Decode a span to (address, mnemonic, operands) triples.

    Deliberately returns decoded instructions rather than text: comparing
    normalized disassembly is a supplementary view, never the primary evidence.
    """
    if isa not in MD:
        raise ProbeError(f"unknown isa: {isa}")
    out: list[tuple[int, str, str]] = []
    for ins in MD[isa].disasm(data, base_address):
        out.append((ins.address, ins.mnemonic, ins.op_str))
    return out


def compare_bytes(
    target: bytes,
    candidate: bytes,
    base_address: int,
    isa: str,
    *,
    notes: tuple[str, ...] = (),
) -> ByteDiff:
    """Compare a probe's target bytes against a compiled candidate.

    Reports every quantity the ticket asks for, and never reports a mismatch
    that is merely an unresolved relocation: the caller is responsible for
    resolving or linking first, and this function's ``notes`` record which
    methodology was used.
    """
    length = min(len(target), len(candidate))
    differences = [index for index in range(length) if target[index] != candidate[index]]
    differing = len(differences) + abs(len(target) - len(candidate))

    spans = instruction_spans(target, base_address, isa)
    differing_instructions = 0
    for offset, size in spans:
        end = offset + size
        if end > len(candidate) or target[offset:end] != candidate[offset:end]:
            differing_instructions += 1

    return ByteDiff(
        target_size=len(target),
        candidate_size=len(candidate),
        identical_bytes=length - len(differences),
        first_difference=differences[0] if differences else None,
        differing_bytes=differing,
        target_instructions=len(spans),
        differing_instructions=differing_instructions,
        exact_match=bytes(target) == bytes(candidate),
        base_address=base_address,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# toolchain
# ---------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class AdsTools:
    """An installed ADS 1.2 toolchain, resolved and IDENTIFIED but never shipped."""

    root: Path
    compiler: Path
    compiler_id: str
    support: dict[str, Path]
    banner: str
    version: str

    def as_dict(self) -> dict:
        return {
            "root": str(self.root),
            "compiler": self.compiler_id,
            "compiler_path": str(self.compiler),
            "banner": self.banner,
            "version": self.version,
            "support": {name: str(path) for name, path in sorted(self.support.items())},
            "redistribution": "PROHIBITED: commercial software, located locally, never committed",
        }


#: Substrings that identify an ARM Developer Suite / RealView tool banner. A
#: bare name match is not enough: `tcc` is also the name of the Tiny C Compiler,
#: so accepting any executable called `tcc.exe` would let an unrelated tool be
#: used and its mismatches reported as a compiler finding.
_ADS_BANNER_MARKERS = (
    "developer suite",
    "realview",
    "rvct",
    "arm c/c++ compiler",
    "arm c compiler",
    "arm assembler",
    "arm linker",
    "arm c++ compiler",
)


def looks_like_ads(banner: str) -> bool:
    """Whether a tool banner identifies ARM Developer Suite / RealView / RVCT.

    A bare executable-name match is not enough: `tcc` is also the Tiny C
    Compiler, so a tool of that name would be used and its mismatches reported
    as a compiler finding. The banner is the discriminator.
    """
    lowered = banner.lower()
    return any(marker in lowered for marker in _ADS_BANNER_MARKERS)


def identify_ads_tool(exe: Path, *, timeout: float = 20.0) -> str | None:
    """Run a tool for its banner and return it iff it identifies as ARM ADS/RVCT.

    Returns None when the tool cannot be executed, produces nothing, times out,
    or produces a banner without any ADS/RVCT marker. Fails CLOSED: an
    unidentified tool is treated as absent, never as an ARM compiler.
    """
    try:
        completed = subprocess.run(
            [str(exe)],
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return None
    blob = f"{completed.stdout or ''}\n{completed.stderr or ''}"
    if not looks_like_ads(blob):
        return None
    for line in blob.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:200]
    return None


def _banner_version(banner: str) -> str:
    """Pull a version-looking token out of a banner, or say it is unknown."""
    match = re.search(r"\b(\d+\.\d+(?:\.\d+)?)\b", banner)
    return match.group(1) if match else "unknown"


def discover_ads(
    root: str | Path | None = None, compiler_id: str = "tcpp"
) -> AdsTools | None:
    """Resolve and IDENTIFY an ADS 1.2 installation, or None.

    Never invents a path, and never accepts a tool that does not identify as
    ARM ADS/RVCT. When an explicit root is supplied the lookup is confined to
    it: falling back to PATH there would silently substitute an unrelated
    same-named executable for the requested installation.
    """
    resolved = _ads_root(root)
    explicit = root is not None or bool(os.environ.get("ADS12_ROOT", "").strip())

    compiler = _find_ads_tool(compiler_id, resolved, allow_path=not explicit)
    if compiler is None:
        return None
    banner = identify_ads_tool(compiler)
    if banner is None:
        return None
    support: dict[str, Path] = {}
    for name in ADS_SUPPORT_TOOLS:
        found = _find_ads_tool(name, resolved, allow_path=not explicit)
        if found is not None:
            support[name] = found
    return AdsTools(
        root=resolved if resolved is not None else compiler.parent,
        compiler=compiler,
        compiler_id=compiler_id,
        support=support,
        banner=banner,
        version=_banner_version(banner),
    )


def _ads_root(explicit: str | Path | None) -> Path | None:
    if explicit is not None:
        path = Path(explicit)
        return path if path.is_dir() else None
    env = os.environ.get("ADS12_ROOT", "").strip()
    if env and Path(env).is_dir():
        return Path(env)
    return None


def _find_ads_tool(tool_id: str, root: Path | None, *, allow_path: bool) -> Path | None:
    if root is not None:
        for sub in ("Bin", "bin", ""):
            candidate = (root / sub / f"{tool_id}.exe") if sub else (root / f"{tool_id}.exe")
            if candidate.is_file():
                return candidate
    if allow_path:
        found = shutil.which(tool_id)
        return Path(found) if found else None
    return None


def ads_blocked_details(root: str | Path | None = None) -> list[str]:
    """The actionable description of what is missing and what to do about it."""
    resolved = _ads_root(root)
    explicit = root is not None or bool(os.environ.get("ADS12_ROOT", "").strip())
    details = [
        f"ADS12_ROOT: {resolved if resolved else '(unset)'}",
        "A tool counts only if it identifies as ARM ADS/RVCT from its own banner; "
        "a same-named executable is treated as absent (tcc is also Tiny C Compiler).",
        "Required tools and where they are looked for:",
    ]
    for tool_id in ADS_COMPILE_TOOLS + ADS_SUPPORT_TOOLS:
        found = _find_ads_tool(tool_id, resolved, allow_path=not explicit)
        if found is None:
            details.append(f"  {tool_id:<9} MISSING")
            continue
        banner = identify_ads_tool(found)
        details.append(
            f"  {tool_id:<9} found: {found} "
            f"[{'identified: ' + banner if banner else 'NOT IDENTIFIED as ADS/RVCT'}]"
        )
    details.extend(
        [
            "ARM Developer Suite 1.2 is commercial software and is deliberately NOT "
            "bundled, downloaded or vendored by this repository.",
            "Install it locally and set ADS12_ROOT to the installation root; the "
            "tools are then expected at $ADS12_ROOT/Bin/<tool>.exe.",
            "Once supplied, the exact command this probe will run is printed by: "
            "python -m buusfury compiler-probe --plan",
        ]
    )
    return details


def plan_commands(
    tools: AdsTools, source: Path, output_dir: Path, config: tuple[str, str, str]
) -> list[list[str]]:
    """The exact command lines a probe run would execute, in order.

    The shape is the one the surviving lead implies: ``tcpp -S`` emits ASSEMBLY
    (that is why the reference build has a checked-in ``GBARam.s`` carrying the
    command in its header comment), ``armasm`` turns it into an object,
    ``armlink`` places it at its original ROM address through a scatter file,
    and ``fromelf`` extracts the raw bytes.

    Pure construction: nothing is executed, so ``--plan`` is safe to print
    without a compiler and is what a reviewer checks before supplying one.
    """
    frontend, cpu, opt = config
    object_file = output_dir / "probe.o"
    assembly = output_dir / "probe.s"
    elf = output_dir / "probe.axf"
    binary = output_dir / "probe.bin"
    scatter = output_dir / "probe.scatter"
    compiler = tools.support.get(frontend) or tools.compiler

    commands = [
        [str(compiler), "-S", "-c", "-cpu", cpu, opt, "-o", str(assembly), str(source)],
    ]
    asm = tools.support.get("armasm")
    if asm is not None:
        commands.append([str(asm), "-cpu", cpu, "-o", str(object_file), str(assembly)])
    link = tools.support.get("armlink")
    if link is not None:
        commands.append(
            [str(link), "-noremove", "-scatter", str(scatter), "-o", str(elf), str(object_file)]
        )
    fromelf = tools.support.get("fromelf")
    if fromelf is not None:
        commands.append([str(fromelf), str(elf), "-bin", "-o", str(binary)])
    return commands


def planning_tools(frontend: str, root_label: str = "<ADS12_ROOT>") -> AdsTools:
    """A placeholder toolchain used only to render ``--plan`` output.

    It exists so the plan can be printed without any compiler present. It is
    never passed to ``run_probe``, so a placeholder can never be mistaken for an
    identified installation.
    """
    root = Path(root_label)
    return AdsTools(
        root=root,
        compiler=root / "Bin" / f"{frontend}.exe",
        compiler_id=frontend,
        support={
            name: root / "Bin" / f"{name}.exe"
            for name in ("armasm", "armlink", "fromelf")
        },
        banner="(planning placeholder: no installation was identified)",
        version="unknown",
    )


def render_scatter(unit: TranslationUnit) -> str:
    """A controlled probe linker layout that places the unit at its ROM address.

    Without this the unit would link at a default base, every PC-relative
    literal displacement and every call would differ, and the comparison would
    report a mismatch that says nothing about the compiler.
    """
    region = f"0x{unit.rom_address:08X}"
    return (
        "; generated by tools/buusfury/compiler_probe.py - do not edit\n"
        "; places the probe translation unit at its original ROM address so that\n"
        "; PC-relative literal loads and call displacements are comparable.\n"
        f"Probe {region}\n"
        "{\n"
        "    probe.o (+RO)\n"
        "}\n"
    )


#: The linker-layout assumption the byte comparison rests on. It is stated in
#: every report rather than left implicit, because it is the one step of the ADS
#: leg that this machine cannot exercise (no ADS 1.2 is installed).
ORIGIN_ASSUMPTION = (
    "the region start is the candidate origin: fromelf -bin on a scatter file "
    "whose only load region is at the unit's ROM address is taken to emit from "
    "that address. UNEXERCISED on a machine without ADS 1.2, and the first thing "
    "to confirm from the real toolchain's output when one is supplied."
)


# ---------------------------------------------------------------------------
# diagnostic control (never evidence)
# ---------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class DiagnosticCompiler:
    root: Path
    gcc: Path
    objcopy: Path

    def as_dict(self) -> dict:
        return {
            "compiler": "arm-none-eabi-gcc (devkitARM)",
            "gcc": str(self.gcc),
            "objcopy": str(self.objcopy),
            "classification": DIAGNOSTIC_CONTROL,
            "why": (
                "used only to exercise the compile/compare plumbing on a machine "
                "without ADS 1.2. A modern GCC cannot be evidence about the "
                "original Webfoot compiler and no result from it may be reported "
                "as a finding."
            ),
        }


def discover_diagnostic_compiler() -> DiagnosticCompiler | None:
    """Locate devkitARM's GCC purely as a plumbing control, or None."""
    root = os.environ.get("DEVKITARM", "").strip() or r"C:\devkitPro\devkitARM"
    bin_dir = Path(root) / "bin"
    gcc = bin_dir / "arm-none-eabi-gcc.exe"
    objcopy = bin_dir / "arm-none-eabi-objcopy.exe"
    if gcc.is_file() and objcopy.is_file():
        return DiagnosticCompiler(root=Path(root), gcc=gcc, objcopy=objcopy)
    return None


def compile_diagnostic_control(
    compiler: DiagnosticCompiler,
    source: Path,
    workdir: Path,
    *,
    cpu: str = "arm7tdmi",
    opt: str = "-O1",
    thumb: bool = True,
) -> tuple[bytes, list[list[str]]]:
    """Compile one source file with GCC and return the raw code bytes.

    This exists to prove the harness works end to end. Its output is tagged
    DIAGNOSTIC_CONTROL_NOT_EVIDENCE by every caller.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    object_file = workdir / "control.o"
    binary = workdir / "control.bin"
    commands = [
        [
            str(compiler.gcc),
            "-c",
            "-mcpu=" + cpu,
            "-mthumb" if thumb else "-marm",
            opt,
            "-fno-common",
            "-ffreestanding",
            "-o",
            str(object_file),
            str(source),
        ],
        [
            str(compiler.objcopy),
            "-O",
            "binary",
            "-j",
            ".text",
            str(object_file),
            str(binary),
        ],
    ]
    for command in commands:
        completed = subprocess.run(
            command, capture_output=True, text=True, errors="replace", timeout=180
        )
        if completed.returncode != 0:
            raise ProbeError(
                f"diagnostic control failed: {' '.join(command[:2])}...\n"
                f"{completed.stdout}{completed.stderr}"
            )
    return binary.read_bytes(), commands


# ---------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class ProbeResult:
    """The outcome of comparing one compiled translation unit against the ROM.

    ``comparison_ran`` is the honest predicate for "did this configuration
    actually produce a verdict". A status of MATCH or DIFFER means yes; BLOCKED
    means no, and no compiler conclusion may be drawn from it.
    """

    probe: str
    translation_unit: str
    frontend: str
    cpu: str
    optimization: str
    status: str  # "MATCH" | "DIFFER" | "BLOCKED"
    code: str | None
    diff: ByteDiff | None
    notes: tuple[str, ...]
    probe_matches: tuple[tuple[str, bool], ...] = ()
    dropped_candidate_bytes: int = 0

    @property
    def comparison_ran(self) -> bool:
        return self.status in ("MATCH", "DIFFER") and self.diff is not None

    @property
    def matching_probes(self) -> int:
        return sum(1 for _name, matched in self.probe_matches if matched)

    def as_dict(self) -> dict:
        return {
            "probe": self.probe,
            "translation_unit": self.translation_unit,
            "frontend": self.frontend,
            "cpu": self.cpu,
            "optimization": self.optimization,
            "status": self.status,
            "code": self.code,
            "comparison_ran": self.comparison_ran,
            "exact_match": bool(self.diff and self.diff.exact_match),
            "probe_matches": {name: matched for name, matched in self.probe_matches},
            "matching_probes": self.matching_probes,
            "total_probes": len(self.probe_matches),
            "dropped_candidate_bytes": self.dropped_candidate_bytes,
            "diff": self.diff.as_dict() if self.diff else None,
            "notes": list(self.notes),
        }


def probe_slice_matches(
    target: bytes,
    candidate: bytes,
    unit: TranslationUnit,
    isa: str,
) -> tuple[tuple[str, bool], ...]:
    """Per-function exact-match results, sliced out of ONE translation-unit build.

    The ticket's success criterion is stated per function ("at least three
    unrelated ordinary engine functions match byte-for-byte under the same
    compiler configuration"), so a single unit-level boolean is not enough
    evidence. These slices are not independent builds: they are windows into the
    same linked image, which is the only thing that keeps the shared literal pool
    and its displacements comparable.
    """
    results: list[tuple[str, bool]] = []
    for start, end, _role in GBARAM_FUNCTIONS:
        offset = start - unit.rom_address
        length = end - start
        target_slice = target[offset : offset + length]
        candidate_slice = candidate[offset : offset + length]
        results.append(
            (f"sub_{start:08X}", bytes(target_slice) == bytes(candidate_slice))
        )
    return tuple(results)


#: A STABLE, environment-independent statement of the blocker. The live
#: per-machine tool listing belongs in the CLI's printed output, never in a
#: committed document, or the document would differ between machines and could
#: not be verified.
BLOCKED_STATEMENT = (
    "No configuration produced a comparison: ARM Developer Suite 1.2 was not "
    "found, or what was found did not identify as an ADS/RVCT tool from its own "
    "banner. Run `python -m buusfury compiler-probe --plan` for the live "
    "per-machine tool listing and the exact commands required."
)

#: The same statement, shaped as the notes a blocked probe result carries.
BLOCKED_NOTES = (
    BLOCKED_STATEMENT,
    "No compiler conclusion is drawn from a configuration that ran no comparison.",
)


def _blocked(
    unit: TranslationUnit,
    frontend: str,
    cpu: str,
    optimization: str,
    code: str,
    notes: tuple[str, ...],
) -> ProbeResult:
    return ProbeResult(
        probe=unit.id,
        translation_unit=unit.id,
        frontend=frontend,
        cpu=cpu,
        optimization=optimization,
        status="BLOCKED",
        code=code,
        diff=None,
        notes=notes,
    )


def run_probe(
    data: bytes,
    unit: TranslationUnit,
    *,
    ads12_root: str | Path | None = None,
    frontend: str = "tcpp",
    cpu: str = "ARM7TDMI",
    optimization: str = "-O1",
    source: Path | None = None,
) -> ProbeResult:
    """Compile the unit and compare it, or fail closed with a blocker code.

    A missing or unidentifiable toolchain is reported as BLOCKED with
    ``ADS12_UNAVAILABLE``. It is never reported as a pass, and no compiler
    conclusion is attached.
    """
    tools = discover_ads(ads12_root, compiler_id=frontend)
    if tools is None:
        # Deliberately the stable statement, not the live tool listing: a
        # committed matrix must not embed this machine's environment.
        return _blocked(
            unit, frontend, cpu, optimization, BLOCK_ADS_UNAVAILABLE, BLOCKED_NOTES
        )

    source_path = source or (_identity.REPO_ROOT / unit.source)
    if not source_path.is_file():
        raise ProbeError(f"candidate source not found: {source_path}")

    workdir = PROBE_WORKSPACE / unit.id / f"{frontend}_{optimization.lstrip('-')}"
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "probe.scatter").write_text(
        render_scatter(unit), encoding="utf-8", newline="\n"
    )
    commands = plan_commands(tools, source_path, workdir, (frontend, cpu, optimization))
    for command in commands:
        completed = subprocess.run(
            command, capture_output=True, text=True, errors="replace", timeout=300
        )
        if completed.returncode != 0:
            return _blocked(
                unit,
                frontend,
                cpu,
                optimization,
                BLOCK_TOOLCHAIN,
                (
                    f"command failed: {' '.join(command)}",
                    (completed.stdout or "") + (completed.stderr or ""),
                ),
            )

    binary = workdir / "probe.bin"
    if not binary.is_file():
        return _blocked(
            unit,
            frontend,
            cpu,
            optimization,
            BLOCK_TOOLCHAIN,
            ("the toolchain produced no binary output",),
        )

    target = extract(data, unit.rom_address, unit.end_address - unit.rom_address)
    candidate = binary.read_bytes()
    notes = (
        "translation-unit scoped comparison: the whole unit including its literal "
        "pool was linked at its original ROM address",
        f"toolchain identified from its banner: {tools.banner}",
        ORIGIN_ASSUMPTION,
    )
    dropped = 0
    if len(candidate) > len(target):
        dropped = len(candidate) - len(target)
        candidate = candidate[: len(target)]
        notes += (
            f"candidate output was {dropped} bytes longer than the target span and "
            "was truncated to it; the dropped bytes are counted, not ignored",
        )
    diff = compare_bytes(target, candidate, unit.rom_address, unit.isa, notes=notes)
    return ProbeResult(
        probe=unit.id,
        translation_unit=unit.id,
        frontend=frontend,
        cpu=cpu,
        optimization=optimization,
        status="MATCH" if diff.exact_match else "DIFFER",
        code=None,
        diff=diff,
        notes=notes,
        probe_matches=probe_slice_matches(target, candidate, unit, unit.isa),
        dropped_candidate_bytes=dropped,
    )


def blocked_result(ads12_root: str | Path | None = None) -> dict:
    """The whole-probe BLOCKED report produced when no ADS is installed."""
    manifest = derive_manifest(_read_rom_bytes())
    return {
        "schema": 1,
        "result": "COMPILER PROBE: BLOCKED - ADS12_UNAVAILABLE",
        "code": BLOCK_ADS_UNAVAILABLE,
        "conclusion": "UNTESTED",
        "no_compiler_result_claimed": True,
        "details": ads_blocked_details(ads12_root),
        "prepared": {
            "probe_functions": manifest["counts"]["probes"],
            "translation_units": manifest["counts"]["translation_units"],
            "thumb": manifest["counts"]["thumb"],
            "arm": manifest["counts"]["arm"],
            "leaf": manifest["counts"]["leaf"],
            "non_leaf": manifest["counts"]["non_leaf"],
            "candidate_sources": [GBARAM_TU.source],
            "matrix_configurations": len(MATRIX_CONFIGS),
        },
        "exact_command_required": (
            "set ADS12_ROOT=<installation root> then run "
            "python -m buusfury compiler-probe --matrix --json"
        ),
    }


def _read_rom_bytes() -> bytes:
    rom = _identity.resolve_baserom(None)
    _identity.verify(rom)
    return rom.read_bytes()


# ---------------------------------------------------------------------------
# fingerprint
# ---------------------------------------------------------------------------
def build_matrix(
    data: bytes,
    sha1: str,
    *,
    ads12_root: str | Path | None = None,
) -> dict:
    """Test every candidate configuration, or report the outcome honestly.

    The first configuration is the historical lead. The rest are the negative
    controls the probe needs in order to be worth anything: a probe set that
    cannot tell two configurations apart has not identified a compiler.

    Crucially, this never infers a "complete" run from the mere availability of
    the driver names. Every configuration is resolved and identified on its own;
    if none of them produced a comparison, the document is BLOCKED and no
    fingerprint is published, because a set of failures to run is not evidence
    about the compiler.
    """
    unit = GBARAM_TU
    configurations: list[dict] = []

    for frontend_id, cpu, opt, why in MATRIX_CONFIGS:
        try:
            probe_result = run_probe(
                data,
                unit,
                ads12_root=ads12_root,
                frontend=frontend_id,
                cpu=cpu,
                optimization=opt,
            )
        except ProbeError as exc:
            probe_result = _blocked(
                unit, frontend_id, cpu, opt, BLOCK_TOOLCHAIN, (str(exc),)
            )
        entry = probe_result.as_dict()
        entry["isa"] = "arm" if frontend_id in ("armcc", "armcpp") else "thumb"
        entry["other_flags"] = ["-S", "-c"]
        entry["why"] = why
        entry["matching_instructions"] = (
            probe_result.diff.matching_instructions if probe_result.diff else None
        )
        entry["total_instructions"] = (
            probe_result.diff.target_instructions if probe_result.diff else None
        )
        configurations.append(entry)

    comparisons = sum(1 for c in configurations if c["comparison_ran"])
    if comparisons == 0:
        codes = {c["code"] for c in configurations if c["code"]}
        code = (
            BLOCK_ADS_UNAVAILABLE
            if codes == {BLOCK_ADS_UNAVAILABLE}
            else (next(iter(codes)) if len(codes) == 1 else BLOCK_TOOLCHAIN)
        )
        result = (
            "COMPILER PROBE: BLOCKED - ADS12_UNAVAILABLE"
            if code == BLOCK_ADS_UNAVAILABLE
            else f"COMPILER PROBE: BLOCKED - {code} (no configuration produced a comparison)"
        )
        return _matrix_document(
            sha1,
            configurations,
            result=result,
            code=code,
            details=[BLOCKED_STATEMENT],
        )

    return _matrix_document(
        sha1, configurations, result="COMPILER PROBE: COMPLETE", code=None, details=[]
    )


def _matrix_document(
    sha1: str,
    configurations: list[dict],
    *,
    result: str,
    code: str | None,
    details: list[str],
) -> dict:
    rows = [
        {
            "frontend": c["frontend"],
            "isa": c["isa"],
            "cpu": c["cpu"],
            "optimization": c["optimization"],
            "translation_unit": c["translation_unit"],
            "comparison_ran": c["comparison_ran"],
            "exact_match": c["exact_match"],
            "matching_probes": c.get("matching_probes"),
            "total_probes": c.get("total_probes"),
            "matching_instructions": c.get("matching_instructions"),
            "total_instructions": c.get("total_instructions"),
            "dropped_candidate_bytes": c.get("dropped_candidate_bytes"),
        }
        for c in configurations
    ]
    comparisons = sum(1 for c in configurations if c["comparison_ran"])
    return {
        "schema": 1,
        "source_sha1": sha1,
        "result": result,
        "code": code,
        "conclusion": (
            "UNTESTED" if code else fingerprint(configurations)["thumb_frontend"]
        ),
        "no_compiler_result_claimed": bool(code),
        "comparisons_run": comparisons,
        "generated_by": "tools/buusfury/compiler_probe.py build_matrix()",
        "methodology": ORIGIN_ASSUMPTION,
        "comparison_scope": (
            "translation unit gbaram_tu (0x0803D4D0..0x0803D740): 608 bytes of code "
            "plus its 16-byte literal pool, compared as one span, then sliced into "
            "the 8 declared probe functions"
        ),
        "configurations": configurations,
        "rows": rows,
        "negative_controls": [
            "tcc vs tcpp: C frontend against C++ frontend",
            "tcpp -O0 vs -O1: optimisation off against the lead",
            "tcpp -O1 vs -O2: the lead against more optimisation",
            "armcc/armcpp: ARM instruction set against the observed Thumb",
        ],
        "fingerprint": (
            fingerprint(configurations) if comparisons else fingerprint([])
        ),
        "details": details,
    }


def write_matrix(path: Path | None = None) -> Path:
    """Regenerate config/compiler_matrix.json."""
    target = path or MATRIX_PATH
    data = _read_rom_bytes()
    sha1 = hashlib.sha1(data).hexdigest()
    target.write_text(
        json.dumps(build_matrix(data, sha1), indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return target


def _row(configurations: list[dict], frontend: str, optimization: str) -> dict | None:
    for entry in configurations:
        if (
            entry.get("frontend") == frontend
            and entry.get("optimization") == optimization
            and entry.get("comparison_ran")
        ):
            return entry
    return None


def _claim(winner: dict | None, competitor: dict | None, probe_total: int) -> str:
    """Classify ONE claim from the two configurations that discriminate it.

    The questions this answers are: did the favoured configuration match, how
    many of the probe FUNCTIONS did it match, and did the competing setting
    produce different code? A match that the competitor reproduces exactly is
    non-discriminating and can only ever be PLAUSIBLE.
    """
    if winner is None:
        return "UNTESTED"
    matched = winner.get("matching_probes") or 0
    total = winner.get("total_probes") or probe_total
    if matched == 0:
        return "REFUTED"
    if competitor is not None and (competitor.get("matching_probes") or 0) == matched:
        return "PLAUSIBLE"
    if matched >= 3 and matched == total:
        return "PROVEN"
    return "STRONGLY_SUPPORTED"


def fingerprint(matrix_results: list[dict]) -> dict:
    """Classify each claim SEPARATELY. Never invents certainty.

    Every claim is scored from the two configurations that actually discriminate
    it, and the score counts matching probe FUNCTIONS under one shared
    configuration, not matching configurations. Counting configurations would
    invert the meaning: `-O0`, `-O1` and `-O2` all matching is exactly the
    non-discriminating case, not three independent confirmations.

    `PROVEN` requires that every one of at least three probe functions match and
    that the competing setting differ. A claim whose configurations never
    compared bytes is `UNTESTED`, which is not a weak positive.
    """
    probe_total = len(GBARAM_FUNCTIONS)
    compared = [r for r in matrix_results if r.get("comparison_ran")]

    tcpp_o1 = _row(matrix_results, "tcpp", "-O1")
    tcc_o1 = _row(matrix_results, "tcc", "-O1")
    tcpp_o0 = _row(matrix_results, "tcpp", "-O0")
    tcpp_o2 = _row(matrix_results, "tcpp", "-O2")
    armcpp_o1 = _row(matrix_results, "armcpp", "-O1")
    armcc_o1 = _row(matrix_results, "armcc", "-O1")

    def first_or_none(*rows):
        for row in rows:
            if row is not None:
                return row
        return None

    thumb_frontend = _claim(tcpp_o1, tcc_o1, probe_total)
    thumb_optimization = _claim(tcpp_o1, first_or_none(tcpp_o0, tcpp_o2), probe_total)
    c_vs_cpp = _claim(tcpp_o1, tcc_o1, probe_total)
    arm_frontend = _claim(armcpp_o1, armcc_o1, probe_total)
    arm_optimization = _claim(armcc_o1, armcpp_o1, probe_total)

    # The CPU target never varies in this matrix: every configuration is
    # ARM7TDMI. With nothing to discriminate it, a match can only ever be
    # consistent evidence, so it is capped at PLAUSIBLE rather than promoted.
    thumb_cpu_target = (
        "PLAUSIBLE"
        if (tcpp_o1 or {}).get("matching_probes")
        else ("REFUTED" if tcpp_o1 else "UNTESTED")
    )

    return {
        "thumb_frontend": thumb_frontend,
        "thumb_optimization": thumb_optimization,
        "thumb_cpu_target": thumb_cpu_target,
        "arm_frontend": arm_frontend,
        "arm_optimization": arm_optimization,
        "c_vs_cpp": c_vs_cpp,
        "abi": "UNTESTED",
        "_evidence": {
            "configurations_compared": len(compared),
            "configurations_tested": len(matrix_results),
            "probe_functions_per_configuration": probe_total,
            "lead_matching_probes": (tcpp_o1 or {}).get("matching_probes"),
            "discriminators": {
                "thumb_frontend": "tcpp -O1 against tcc -O1",
                "thumb_optimization": "tcpp -O1 against tcpp -O0 and -O2",
                "c_vs_cpp": "tcpp -O1 against tcc -O1",
                "arm_frontend": "armcpp -O1 against armcc -O1",
                "thumb_cpu_target": (
                    "NONE: the CPU is ARM7TDMI in every configuration, so this "
                    "claim can never be promoted past PLAUSIBLE by this matrix"
                ),
                "abi": "NONE: no ABI-affecting flag is varied",
            },
            "success_criterion": (
                "at least 3 discriminating ordinary engine functions matching "
                "exactly under one shared configuration, with the competing "
                "setting differing"
            ),
        },
        "_state_meaning": {
            "PROVEN": "multiple discriminating exact matches support the setting",
            "STRONGLY_SUPPORTED": "repeated close or exact matches, some ambiguity",
            "PLAUSIBLE": "evidence consistent but not discriminating",
            "REFUTED": "repeated mismatches despite semantically correct source",
            "UNTESTED": "toolchain unavailable, or no configuration compared bytes",
        },
    }


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------
def render_matrix_markdown(matrix: dict) -> str:
    """Render config/compiler_matrix.json as a readable table."""
    lines = [
        "# Compiler configuration matrix",
        "",
        f"Source ROM SHA-1: `{matrix['source_sha1']}`",
        "",
        f"Status: **{matrix['result']}**",
        "",
        f"Configurations that actually compared bytes: {matrix.get('comparisons_run', 0)} "
        f"of {len(matrix['configurations'])}",
        "",
        "| frontend | ISA | CPU | opt | unit | compared | exact | matching probes |"
        " matching insn | total insn |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in matrix["configurations"]:
        lines.append(
            "| {frontend} | {isa} | {cpu} | {opt} | {unit} | {ran} | {exact} | {mp} |"
            " {mi} | {ti} |".format(
                frontend=row["frontend"],
                isa=row["isa"],
                cpu=row["cpu"],
                opt=row["optimization"],
                unit=row["translation_unit"],
                ran="yes" if row["comparison_ran"] else "no",
                exact="yes" if row["exact_match"] else "no",
                mp=f"{row.get('matching_probes')}/{row.get('total_probes')}"
                if row["comparison_ran"]
                else "-",
                mi=row.get("matching_instructions") if row["comparison_ran"] else "-",
                ti=row.get("total_instructions") if row["comparison_ran"] else "-",
            )
        )
    if not matrix.get("comparisons_run"):
        lines += [
            "",
            "No configuration produced a comparison, so the table above records no",
            "result for any row and no compiler conclusion is claimed.",
        ]
    return "\n".join(lines) + "\n"


def write_manifest(path: Path | None = None) -> Path:
    """Regenerate config/compiler_probes.json from the canonical ROM."""
    target = path or MANIFEST_PATH
    data = _read_rom_bytes()
    target.write_text(
        json.dumps(derive_manifest(data), indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return target
