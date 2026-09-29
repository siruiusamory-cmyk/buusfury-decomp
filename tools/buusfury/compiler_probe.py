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
            "literal_pool": {
                "rom_address": f"0x{self.literal_pool[0][0] + _gba.ROM_BASE:08X}",
                "file_offset": f"0x{self.literal_pool[0][0]:06X}",
                "byte_length": 4 * len(self.literal_pool),
                "words": [
                    {"file_offset": f"0x{o:06X}", "value": f"0x{v:08X}"}
                    for o, v in self.literal_pool
                ],
            },
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
CONTROLS = (
    {
        "id": "reset_crt",
        "rom_address": "0x080000C0",
        "isa": "arm",
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
        "isa": "arm",
        "role": "control",
        "excluded_because": (
            "the ADS C runtime static-initialiser veneer reached from the reset "
            "path; library code, not engine code"
        ),
    },
    {
        "id": "codec_blob",
        "rom_address": "0x087B79A4",
        "isa": "arm",
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
        "id": "sub_0803D5B8_functions_json_entry",
        "rom_address": "0x0803D5B8",
        "map_claim": "config/functions.json size=620, callees=0x0803D4E8/0x0803D520/0x0803D56A",
        "rejected_because": (
            "config/functions.json's size is analysis.decode_run(limit=0x400).bytes_ok, "
            "so for 0x0803D5B8 it ran 620 bytes past the function end and attributed "
            "three neighbouring functions' calls to it. Its callee lists are used as "
            "a cross-check only, never as boundary input."
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
    """config/functions.json keyed by address, or empty when it is absent.

    Used only as a cross-check. It is never boundary input: its `size` is a
    decode extent, and it is the artefact this ticket is testing against.
    """
    path = _identity.CONFIG_DIR / "functions.json"
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {int(entry["address"], 16) & ~1: entry for entry in raw.get("functions", [])}


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
            "analysis.decode_run(limit=0x400).bytes_ok and overruns small functions.",
            "No semantic name is assigned. Probe names are sub_<address>.",
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


def verify_manifest(data: bytes) -> list[str]:
    """Regenerate the manifest and return every disagreement with the file on disk."""
    try:
        committed = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{MANIFEST_PATH} does not exist"]
    derived = derive_manifest(data)
    problems: list[str] = []

    for key in (
        "source_sha1",
        "counts",
        "probes",
        "translation_units",
        "inventory_gaps",
        "inventory_size_disagreements",
    ):
        if committed.get(key) != derived.get(key):
            problems.append(f"manifest field {key!r} does not match the canonical ROM")
    problems.extend(derived["consistency_problems"])
    return problems


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
    """A structured, deterministic comparison of two machine-code spans."""

    target_size: int
    candidate_size: int
    identical_bytes: int
    first_difference: int | None
    differing_bytes: int
    differing_instructions: int
    compared_instructions: int
    exact_match: bool
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            "target_size": self.target_size,
            "candidate_size": self.candidate_size,
            "identical_bytes": self.identical_bytes,
            "first_difference": (
                f"0x{self.first_difference:X}" if self.first_difference is not None else None
            ),
            "differing_bytes": self.differing_bytes,
            "differing_instructions": self.differing_instructions,
            "compared_instructions": self.compared_instructions,
            "exact_match": self.exact_match,
            "notes": list(self.notes),
        }


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
    differences.extend(range(length, max(len(target), len(candidate))))
    identical = length - sum(1 for d in differences if d < length)

    target_ins = disassemble(target, base_address, isa)
    candidate_ins = disassemble(candidate, base_address, isa)
    differing_instructions = 0
    compared = min(len(target_ins), len(candidate_ins))
    for index in range(compared):
        if target_ins[index][1:] != candidate_ins[index][1:]:
            differing_instructions += 1
    differing_instructions += abs(len(target_ins) - len(candidate_ins))

    return ByteDiff(
        target_size=len(target),
        candidate_size=len(candidate),
        identical_bytes=identical,
        first_difference=differences[0] if differences else None,
        differing_bytes=len(differences),
        differing_instructions=differing_instructions,
        compared_instructions=compared,
        exact_match=bytes(target) == bytes(candidate),
        notes=notes,
    )


# ---------------------------------------------------------------------------
# toolchain
# ---------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class AdsTools:
    """An installed ADS 1.2 toolchain, resolved but never shipped."""

    root: Path
    compiler: Path
    compiler_id: str
    support: dict[str, Path]

    def as_dict(self) -> dict:
        return {
            "root": str(self.root),
            "compiler": self.compiler_id,
            "compiler_path": str(self.compiler),
            "support": {name: str(path) for name, path in sorted(self.support.items())},
            "redistribution": "PROHIBITED: commercial software, located locally, never committed",
        }


def discover_ads(
    root: str | Path | None = None, compiler_id: str = "tcpp"
) -> AdsTools | None:
    """Resolve an ADS 1.2 installation, or None. Never invents a path."""
    resolved = _ads_root(root)
    if resolved is None:
        return None
    compiler = _ads_executable(compiler_id, resolved)
    if compiler is None:
        return None
    support = {}
    for name in ADS_SUPPORT_TOOLS:
        found = _ads_executable(name, resolved)
        if found is not None:
            support[name] = found
    return AdsTools(
        root=resolved, compiler=compiler, compiler_id=compiler_id, support=support
    )


def _ads_root(explicit: str | Path | None) -> Path | None:
    if explicit is not None:
        path = Path(explicit)
        return path if path.is_dir() else None
    env = os.environ.get("ADS12_ROOT", "").strip()
    if env and Path(env).is_dir():
        return Path(env)
    return None


def _ads_executable(tool_id: str, root: Path) -> Path | None:
    for sub in ("Bin", "bin", ""):
        candidate = (root / sub / f"{tool_id}.exe") if sub else (root / f"{tool_id}.exe")
        if candidate.is_file():
            return candidate
    found = shutil.which(tool_id)
    return Path(found) if found else None


def ads_blocked_details(root: str | Path | None = None) -> list[str]:
    """The actionable description of what is missing and what to do about it."""
    resolved = _ads_root(root)
    details = [
        f"ADS12_ROOT: {resolved if resolved else '(unset)'}",
        "Required tools and where they are looked for:",
    ]
    for tool_id in ADS_COMPILE_TOOLS + ADS_SUPPORT_TOOLS:
        found = _ads_executable(tool_id, resolved) if resolved else shutil.which(tool_id)
        details.append(
            f"  {tool_id:<9} {'found: ' + str(found) if found else 'MISSING'}"
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
    probe: str
    translation_unit: str
    frontend: str
    cpu: str
    optimization: str
    status: str  # "MATCH" | "DIFFER" | "BLOCKED" | "CONTROL"
    code: str | None
    diff: ByteDiff | None
    notes: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "probe": self.probe,
            "translation_unit": self.translation_unit,
            "frontend": self.frontend,
            "cpu": self.cpu,
            "optimization": self.optimization,
            "status": self.status,
            "code": self.code,
            "exact_match": bool(self.diff and self.diff.exact_match),
            "diff": self.diff.as_dict() if self.diff else None,
            "notes": list(self.notes),
        }


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

    A missing toolchain is reported as BLOCKED with ``ADS12_UNAVAILABLE``. It is
    never reported as a pass, and no compiler conclusion is attached.
    """
    tools = discover_ads(ads12_root, compiler_id=frontend)
    if tools is None:
        return ProbeResult(
            probe=unit.id,
            translation_unit=unit.id,
            frontend=frontend,
            cpu=cpu,
            optimization=optimization,
            status="BLOCKED",
            code=BLOCK_ADS_UNAVAILABLE,
            diff=None,
            notes=tuple(ads_blocked_details(ads12_root)),
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
            return ProbeResult(
                probe=unit.id,
                translation_unit=unit.id,
                frontend=frontend,
                cpu=cpu,
                optimization=optimization,
                status="BLOCKED",
                code=BLOCK_TOOLCHAIN,
                diff=None,
                notes=(
                    f"command failed: {' '.join(command)}",
                    (completed.stdout or "") + (completed.stderr or ""),
                ),
            )

    binary = workdir / "probe.bin"
    if not binary.is_file():
        return ProbeResult(
            probe=unit.id,
            translation_unit=unit.id,
            frontend=frontend,
            cpu=cpu,
            optimization=optimization,
            status="BLOCKED",
            code=BLOCK_TOOLCHAIN,
            diff=None,
            notes=("the toolchain produced no binary output",),
        )

    target = extract(
        data, unit.rom_address, unit.end_address - unit.rom_address
    )
    candidate = binary.read_bytes()
    notes = (
        "translation-unit scoped comparison: the whole unit including its literal "
        "pool was linked at its original ROM address",
        ORIGIN_ASSUMPTION,
    )
    if len(candidate) > len(target):
        candidate = candidate[: len(target)]
        notes += ("candidate output was truncated to the target length",)
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
    frontend: str = "tcpp",
) -> dict:
    """Test every candidate configuration, or report the whole matrix blocked.

    The first configuration is the historical lead. The rest are the negative
    controls the probe needs in order to be worth anything: a probe set that
    cannot tell two configurations apart has not identified a compiler.
    """
    unit = GBARAM_TU
    configurations: list[dict] = []

    tools = discover_ads(ads12_root, compiler_id=frontend)
    if tools is None:
        for frontend_id, cpu, opt, why in MATRIX_CONFIGS:
            configurations.append(
                {
                    "frontend": frontend_id,
                    "isa": "arm" if frontend_id in ("armcc", "armcpp") else "thumb",
                    "cpu": cpu,
                    "optimization": opt,
                    "other_flags": ["-S", "-c"],
                    "translation_unit": unit.id,
                    "exact_match": False,
                    "matching_instructions": None,
                    "total_instructions": None,
                    "status": "BLOCKED",
                    "code": BLOCK_ADS_UNAVAILABLE,
                    "why": why,
                    "notes": "not executed: ADS 1.2 is not installed",
                }
            )
        return _matrix_document(
            sha1,
            configurations,
            result="COMPILER PROBE: BLOCKED - ADS12_UNAVAILABLE",
            code=BLOCK_ADS_UNAVAILABLE,
            details=ads_blocked_details(ads12_root),
        )

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
            probe_result = ProbeResult(
                probe=unit.id,
                translation_unit=unit.id,
                frontend=frontend_id,
                cpu=cpu,
                optimization=opt,
                status="BLOCKED",
                code=BLOCK_TOOLCHAIN,
                diff=None,
                notes=(str(exc),),
            )
        entry = probe_result.as_dict()
        entry["isa"] = "arm" if frontend_id in ("armcc", "armcpp") else "thumb"
        entry["other_flags"] = ["-S", "-c"]
        entry["why"] = why
        if probe_result.diff is not None:
            entry["matching_instructions"] = (
                probe_result.diff.compared_instructions
                - probe_result.diff.differing_instructions
            )
            entry["total_instructions"] = probe_result.diff.compared_instructions
        configurations.append(entry)

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
            "exact_match": c["exact_match"],
            "matching_instructions": c.get("matching_instructions"),
            "total_instructions": c.get("total_instructions"),
        }
        for c in configurations
    ]
    return {
        "schema": 1,
        "source_sha1": sha1,
        "result": result,
        "code": code,
        "conclusion": "UNTESTED" if code else fingerprint(configurations)["thumb_frontend"],
        "no_compiler_result_claimed": bool(code),
        "generated_by": "tools/buusfury/compiler_probe.py build_matrix()",
        "methodology": ORIGIN_ASSUMPTION,
        "comparison_scope": (
            "translation unit gbaram_tu (0x0803D4D0..0x0803D740): 608 bytes of code "
            "plus its 16-byte literal pool, compared as one span"
        ),
        "configurations": configurations,
        "rows": rows,
        "negative_controls": [
            "tcc vs tcpp: C frontend against C++ frontend",
            "tcpp -O0 vs -O1: optimisation off against the lead",
            "tcpp -O1 vs -O2: the lead against more optimisation",
            "armcc/armcpp: ARM instruction set against the observed Thumb",
        ],
        "fingerprint": fingerprint(configurations) if not code else fingerprint([]),
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


def fingerprint(matrix_results: list[dict]) -> dict:
    """Classify each claim separately. Never invents certainty.

    A claim is PROVEN only on multiple discriminating exact matches under one
    shared configuration; a single tiny function matching proves nothing,
    because a two-instruction getter compiles identically at every -O level.
    """
    exact = [r for r in matrix_results if r.get("exact_match")]
    if not matrix_results:
        state = "UNTESTED"
    elif exact:
        state = "STRONGLY_SUPPORTED" if len(exact) >= 3 else "PLAUSIBLE"
    else:
        state = "REFUTED"
    return {
        "thumb_frontend": state,
        "thumb_optimization": state,
        "thumb_cpu_target": state,
        "arm_frontend": "UNTESTED",
        "arm_optimization": "UNTESTED",
        "c_vs_cpp": state,
        "abi": "UNTESTED",
        "_evidence": {
            "exact_matches": len(exact),
            "configurations_tested": len(matrix_results),
            "success_criterion": (
                "at least 3 discriminating ordinary engine functions matching "
                "exactly under one shared configuration"
            ),
        },
        "_state_meaning": {
            "PROVEN": "multiple discriminating exact matches support the setting",
            "STRONGLY_SUPPORTED": "repeated close or exact matches, some ambiguity",
            "PLAUSIBLE": "evidence consistent but not discriminating",
            "REFUTED": "repeated mismatches despite semantically correct source",
            "UNTESTED": "toolchain unavailable",
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
        "| frontend | ISA | CPU | opt | unit | exact | matching insn | total insn |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in matrix["configurations"]:
        lines.append(
            "| {frontend} | {isa} | {cpu} | {opt} | {unit} | {exact} | {mi} | {ti} |".format(
                frontend=row["frontend"],
                isa=row["isa"],
                cpu=row["cpu"],
                opt=row["optimization"],
                unit=row["translation_unit"],
                exact="yes" if row["exact_match"] else "no",
                mi=row.get("matching_instructions", "-"),
                ti=row.get("total_instructions", "-"),
            )
        )
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
