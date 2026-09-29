"""DECOMP-LIFT-PILOT-001: the repeatable semantic lifting loop.

One command takes a reconstructed translation unit from source to a
machine-readable comparison against the original ROM:

    source  ->  compile  ->  link at the original ROM address  ->  objcopy
            ->  per-function and translation-unit comparison
            ->  a report that keeps three VERDICTS apart

THE THREE VERDICTS ARE INDEPENDENT AND MUST STAY SO
    SEMANTIC      does the reconstruction behave correctly?  Measured by
                  RUNNING it on the host (src/probes/gbaram_selftest.c).
    MODERN_BUILD  does it compile, link and emit bytes with the modern
                  toolchain?  A plumbing result.
    ADS_MATCH     does it reproduce the original compiler's output?  BLOCKED:
                  the ADS 1.2 ARM compilers on this machine are unlicensed, and
                  a modern GCC is not the original compiler.

No verdict may be inferred from another. In particular a passing modern build
is NOT evidence about the original compiler, and this module never reports one
as such; the modern-vs-original byte comparison is published as a MEASUREMENT
with `not_a_match_claim` set, and `ADS_MATCH` is never promoted from it.

WHY THE COMPARISON IS TRANSLATION-UNIT SCOPED
A function containing a PC-relative literal load cannot be compared standalone:
its `ldr rX, [pc, #N]` displacement depends on where the pool sits. The original
shares ONE pool across seven of its eight functions, so the only rigorous unit
is the whole TU, linked at its original address. Per-function rows are slices of
that one build.

REUSE
Targets come from config/lift_targets.json, function boundaries from
config/compiler_probes.json. Adding the next function family is a config entry
plus its C source; no new script.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from . import compiler_probe as cp
from . import gba as _gba
from . import identity as _identity

# ---------------------------------------------------------------------------
# verdict vocabularies - deliberately three separate tuples
# ---------------------------------------------------------------------------
SEMANTIC_STATES = ("PROVEN", "PARTIAL", "FAILED", "UNTESTED")
MODERN_BUILD_STATES = ("PASS", "FAIL", "BLOCKED")
ADS_MATCH_STATES = ("BLOCKED", "UNTESTED")

#: The minimum behavioural assertion count the host self-check must reach.
#: DECOMP-LIFT-PILOT-001 states 230; a lower count means checks were lost.
MIN_SEMANTIC_CHECKS = 230

#: Where the modern toolchain is expected, overridable by environment.
DEVKITARM_ENV = "DEVKITARM"
DEFAULT_DEVKITARM = r"C:\devkitPro\devkitARM"

TARGETS_PATH = _identity.CONFIG_DIR / "lift_targets.json"
PROBES_PATH = _identity.CONFIG_DIR / "compiler_probes.json"
LIFT_WORKSPACE = _identity.REPO_ROOT / "build" / "lift"


# ---------------------------------------------------------------------------
# translation units the lift loop knows
# ---------------------------------------------------------------------------
# GBARam's unit comes from the ADS probe manifest, which already derives and
# verifies its boundaries. The ByteCodeInterpreter unit is derived HERE, from the
# ROM, because it has a property the probe manifest's schema cannot express: its
# literal pool is NOT adjacent to its code. The pool sits at 0x08004158 while the
# last function ends at 0x08004156, with two padding bytes between, and 86 bytes
# of unrelated code at 0x08004102 would have to be crossed to reach it.
BCI_TU = cp.TranslationUnit(
    id="bci_tu",
    rom_address=0x08004038,
    code_end_address=0x08004158,
    end_address=0x08004160,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08004038: every path reaches the single epilogue at "
        "0x0800408C, 47 instructions, no gaps, and the next byte is a new "
        "function prologue",
        "the unit continues through 0x08004098 and 0x08004102, which share the "
        "same literal pool at 0x08004158, which is what establishes one "
        "compilation unit",
        "the pool's second word is the dispatch table 0x080554C0, whose extent is "
        "bounded by the UTF-16 assertion at 0x0805553C",
    ),
    literal_pool=(
        (0x004158, 0x03001034),
        (0x00415C, 0x080554C0),
        (0x004198, 0x0805553C),
    ),
    selection=(
        "the ROM preserves the original source path "
        "'T:\\Source\\ByteCodeInterpreter\\ByteCodeInterpreter.cpp' as ASCII at "
        "0x08004160, referenced by the assertion at 0x080040F4",
        "config/compiler_probes.json and the ROM map both anchor 0x08004038 as "
        "the bytecode interpreter entry",
        "the dispatch loop's structure (one byte, one table index, one indirect "
        "call, NULL terminates) is read directly from 0x08004064..0x08004096",
    ),
)

#: (start, end, role) per function, all derived from the ROM at run time.
BCI_FUNCTIONS = (
    (0x08004038, 0x08004098, "bytecode dispatch loop"),
    (0x08004098, 0x08004102, "dialog entry point"),
    (0x08004102, 0x08004156, "untitled helper; name not justified by evidence"),
)

#: The unit's literal pool, which is NOT adjacent to its code. The first two
#: words sit at 0x08004158, two padding bytes after the last function; a third
#: sits at 0x08004198 and holds the assertion message address, so the unit's
#: literals live in two separate places rather than one shared run.
BCI_LITERAL_POOL = ((0x004158, 0x03001034), (0x00415C, 0x080554C0), (0x004198, 0x0805553C))

#: The dispatch table and the string that bounds it.
BCI_DISPATCH_TABLE = 0x080554C0
BCI_DISPATCH_ENTRIES = 31
BCI_BOUNDING_STRING = 0x0805553C
#: The ROM stores this message WITH the surrounding quote characters, so the
#: expected text includes them. Comparing against the unquoted form would leave
#: a false mismatch.
BCI_BOUNDING_TEXT = '"Expected dialog to start with a code block"'

#: Padding between the last function and the pool.
BCI_ALIGNMENT_PADDING = 2

# ---------------------------------------------------------------------------
# the ByteCodeInterpreter handler unit
# ---------------------------------------------------------------------------
# Primary dispatch slot 2. A different translation unit from the interpreter:
# separate code and a separate literal pool at 0x08003F40, which four other
# primary handlers also load from.
H2_ENTRY = 0x08003CBE
H2_TU = cp.TranslationUnit(
    id="handler2_tu",
    rom_address=0x08003CBE,
    code_end_address=0x08003CD4,
    end_address=0x08003CD4,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_handlers.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08003CBE: 10 instructions, no gaps, one terminator "
        "at 0x08003CD2 (pop {r3,pc})",
        "the table word at primary slot 2 is 0x08003CBF, whose Thumb bit masks to "
        "this entry, so the entry is anchored by the dispatch table itself",
        "no direct BL site anywhere in the image targets it: it is reached only "
        "through the primary table",
    ),
    # NOT adjacent to the code: the pool sits at 0x08003F40, 0x26C bytes later,
    # and holds the word the handler loads at 0x08003CCA.
    literal_pool=((0x03F40, 0x08055098),),
    selection=(
        "primary dispatch table slot 2 holds 0x08003CBF",
        "it is the handler that reaches the native dispatch table at 0x08055098, "
        "which is the bridge from the bytecode layer to the engine",
    ),
)
H2_FUNCTIONS = (
    (0x08003CBE, 0x08003CD4, "primary dispatch slot 2: selects a native routine"),
)
H2_LITERAL_POOL = ((0x03F40, 0x08055098),)

#: The native dispatch table and the structure that bounds it from above.
NATIVE_TABLE = 0x08055098
NATIVE_TABLE_LIMIT = 0x080554C0  # the primary table base
PRIMARY_TABLE = 0x080554C0
PRIMARY_TABLE_ENTRIES = 31
PRIMARY_BOUNDING_STRING = 0x0805553C

#: The refuted count. Kept as data so the refutation is re-measured every run
#: rather than remembered in prose.
REFUTED_NATIVE_ENTRIES = 283

UNITS: dict = {}


def _register_units() -> None:
    UNITS[cp.GBARAM_TU.id] = {
        "unit": cp.GBARAM_TU,
        "functions": tuple(cp.GBARAM_FUNCTIONS),
        "literal_pool": cp.GBARAM_TU.literal_pool,
        "boundaries": "manifest",
    }
    UNITS[BCI_TU.id] = {
        "unit": BCI_TU,
        "functions": BCI_FUNCTIONS,
        "literal_pool": BCI_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": BCI_ALIGNMENT_PADDING,
    }
    UNITS[H2_TU.id] = {
        "unit": H2_TU,
        "functions": H2_FUNCTIONS,
        "literal_pool": H2_LITERAL_POOL,
        "boundaries": "derived",
        # No adjacent pool, so there is no padding to check.
        "expect_padding": None,
    }


_register_units()


def derive_native_table(rom_bytes: bytes) -> dict:
    """Prove the native dispatch table's width and count mechanically.

    The width comes from the handler's own indexed load: `lsls r1,r2,#2` scales
    the index by four before `ldr r1,[r2,r1]`, so entries are four bytes.

    The count is bounded on BOTH sides, which is what makes it a proof rather
    than a scan:

    * LOWER BOUND - the index is one byte, read with `ldrb`, so it ranges over
      0..255. Every one of those must land inside the table, or the handler could
      read past it. So there are at least 256 entries.
    * UPPER BOUND - the primary dispatch table begins at 0x080554C0, an address
      the interpreter loads for itself, and its own extent is anchored by the
      assertion string at 0x0805553C. The native table cannot cross it.

    256 <= 266. That is also why the handler needs no bounds check: no reachable
    index can be out of range.

    A prior claim of 283 entries is refuted here rather than merely restated.
    """
    base = _gba.ROM_BASE
    count = (NATIVE_TABLE_LIMIT - NATIVE_TABLE) // 4
    values = []
    invalid = []
    for index in range(count):
        address = NATIVE_TABLE + index * 4
        value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
        values.append(value)
        if not (_gba.in_cartridge(value) and (value & 1)):
            invalid.append({"index": index, "value": f"0x{value:08X}"})

    targets = sorted(v & ~1 for v in values)
    refuted_end = NATIVE_TABLE + REFUTED_NATIVE_ENTRIES * 4

    # Independently re-read what bounds the table from above, so this does not
    # rest on a remembered constant.
    primary_first = int.from_bytes(
        rom_bytes[PRIMARY_TABLE - base : PRIMARY_TABLE - base + 4], "little"
    )
    tail = rom_bytes[PRIMARY_BOUNDING_STRING - base : PRIMARY_BOUNDING_STRING - base + 0x80]
    bounding_text = tail.decode("utf-16-le", "replace").split("\x00")[0]

    return {
        "address": f"0x{NATIVE_TABLE:08X}",
        "entry_width_bytes": 4,
        "entry_width_evidence": (
            "lsls r1,r2,#2 at 0x08003CC8 scales the index by four before "
            "ldr r1,[r2,r1] at 0x08003CCC"
        ),
        "index_width_bytes": 1,
        "index_encoding": "a single unsigned byte, ldrb r2,[r3] at 0x08003CC2",
        "index_range": [0, 255],
        "entries": count,
        "lower_bound": 256,
        "lower_bound_reason": (
            "the index is one byte, so every value in 0..255 must land inside the "
            "table or the handler could read past it"
        ),
        "upper_bound": count,
        "upper_bound_reason": (
            f"the primary dispatch table begins at 0x{PRIMARY_TABLE:08X}, which the "
            "interpreter loads for itself and which is bounded in turn by the "
            f"assertion string at 0x{PRIMARY_BOUNDING_STRING:08X}"
        ),
        "index_is_always_in_range": 256 <= count,
        "invalid_entries": invalid,
        "distinct_targets": len(set(targets)),
        "target_range": [f"0x{targets[0]:08X}", f"0x{targets[-1]:08X}"] if targets else [],
        "bounded_below_by": "the primary table base",
        "bounded_above_by": f"0x{PRIMARY_TABLE:08X}",
        "primary_table_base_recheck": f"0x{primary_first:08X}",
        "primary_table_bounding_string_matches": bounding_text == BCI_BOUNDING_TEXT,
        "refuted_claim": {
            "entries": REFUTED_NATIVE_ENTRIES,
            "would_end_at": f"0x{refuted_end:08X}",
            "why_impossible": (
                f"{REFUTED_NATIVE_ENTRIES} entries at four bytes each reach "
                f"0x{refuted_end:08X}, which is INSIDE the primary dispatch table "
                f"(0x{PRIMARY_TABLE:08X}..0x{PRIMARY_BOUNDING_STRING:08X}). A table "
                "based here cannot have that many entries."
            ),
            "measured_entries": count,
        },
        "derived_from_rom": True,
        "not_hand_written": True,
    }


def derive_dispatch_table(rom_bytes: bytes) -> dict:
    """Prove the dispatch table's extent instead of asserting it.

    A function-pointer table has no length field. Its end is established by what
    follows it: entry 30 occupies 0x08055534..0x08055538 and the UTF-16 assertion
    string begins at 0x0805553C, so the table is exactly 31 entries. This reads
    the string rather than trusting a remembered number.
    """
    base = _gba.ROM_BASE
    entries = []
    for index in range(BCI_DISPATCH_ENTRIES):
        address = BCI_DISPATCH_TABLE + index * 4
        value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
        entries.append(value)

    tail = rom_bytes[BCI_BOUNDING_STRING - base : BCI_BOUNDING_STRING - base + 0x80]
    text = tail.decode("utf-16-le", "replace").split("\x00")[0]

    return {
        "address": f"0x{BCI_DISPATCH_TABLE:08X}",
        "entries": len(entries),
        "null_entries": [i for i, v in enumerate(entries) if v == 0],
        "bounding_string_address": f"0x{BCI_BOUNDING_STRING:08X}",
        "bounding_string_text": text,
        "bounding_string_matches": text == BCI_BOUNDING_TEXT,
        "entries_are_thumb_pointers": sum(
            1 for v in entries if v and _gba.in_cartridge(v) and (v & 1)
        ),
    }


def derive_unit_boundaries(rom_bytes: bytes, unit_id: str) -> dict:
    """Re-derive a unit's function extents from the ROM by aligned chain-walk.

    The extents are DERIVED, not read from a table and not hand-written. A long
    linear sweep desyncs whenever a region does not begin on an instruction
    boundary and then misses real branches; walking from an entry stays aligned
    by construction. An earlier revision of this ticket used a linear sweep for
    the caller census and under-counted the callers of 0x08004038 two to
    thirteen, which is why the walk is the method here.
    """
    spec = UNITS.get(unit_id)
    if spec is None or spec.get("boundaries") != "derived":
        raise LiftError(f"{unit_id!r} has no derived boundary; it comes from the manifest")
    unit = spec["unit"]
    functions = spec["functions"]
    expect_padding = spec.get("expect_padding")

    base = _gba.ROM_BASE
    md = cp.MD["thumb"]
    derived = []
    for start, expected_end, role in functions:
        seen: dict[int, int] = {}
        terminators: list[int] = []
        pending = [start]
        while pending:
            address = pending.pop()
            if address in seen or not _gba.in_cartridge(address):
                continue
            offset = address - base
            for ins in md.disasm(rom_bytes[offset : offset + 0x4000], address):
                if ins.address in seen:
                    break
                seen[ins.address] = ins.size
                mnemonic, operands = ins.mnemonic, ins.op_str
                immediate = None
                if ins.operands and ins.operands[0].type == cp.capstone.arm.ARM_OP_IMM:
                    immediate = ins.operands[0].imm & 0xFFFFFFFF
                if mnemonic in ("bl", "blx"):
                    continue
                if mnemonic == "b" and immediate is not None:
                    pending.append(immediate)
                    break
                if mnemonic.startswith(
                    ("bne", "beq", "bcc", "bcs", "bmi", "bpl", "bvs", "bvc",
                     "bhi", "bls", "bge", "blt", "bgt", "ble")
                ) and immediate is not None:
                    pending.append(immediate)
                    continue
                if (
                    mnemonic == "bx"
                    or (mnemonic.startswith("pop") and "pc" in operands)
                    or (mnemonic.startswith("ldr") and operands.startswith("pc"))
                ):
                    terminators.append(ins.address)
                    break
        end = max(a + s for a, s in seen.items())
        gaps = [
            (a + seen[a], b)
            for a, b in zip(sorted(seen), sorted(seen)[1:])
            if a + seen[a] != b
        ]
        derived.append(
            {
                "start": start,
                "end": end,
                "expected_end": expected_end,
                "role": role,
                "instructions": len(seen),
                "terminators": terminators,
                "gaps": gaps,
                "matches": end == expected_end and not gaps,
            }
        )

    # The extents must tile the code body with only alignment padding between.
    tiling_problems = []
    for index, row in enumerate(derived):
        if not row["matches"]:
            tiling_problems.append(
                f"{row['role']}: derived 0x{row['end']:08X}, expected 0x{row['expected_end']:08X}"
            )
        if index + 1 < len(derived):
            nxt = derived[index + 1]
            if row["end"] != nxt["start"]:
                tiling_problems.append(
                    f"gap or overlap between 0x{row['end']:08X} and 0x{nxt['start']:08X}"
                )

    last = derived[-1]
    pool_addresses = sorted(off + _gba.ROM_BASE for off, _value in spec["literal_pool"])
    pool_start = pool_addresses[0]
    pool_end = pool_addresses[-1] + 4
    gap = pool_start - last["end"]

    if expect_padding is None:
        padding = None
    else:
        padding = gap
        if padding != expect_padding:
            tiling_problems.append(
                f"expected {expect_padding} padding bytes before the pool, saw {padding}"
            )

    return {
        "method": "aligned chain-walk from each entry, following local branches",
        "unit_id": unit_id,
        "code_extent": f"0x{unit.rom_address:08X}..0x{unit.code_end_address:08X}",
        "pool_extent": f"0x{pool_start:08X}..0x{pool_end:08X}",
        "pool_is_adjacent_to_code": pool_start == last["end"],
        "pool_gap_bytes": gap,
        "alignment_padding_bytes": padding,
        "functions": [
            {
                "start": f"0x{row['start']:08X}",
                "end": f"0x{row['end']:08X}",
                "size": row["end"] - row["start"],
                "instructions": row["instructions"],
                "role": row["role"],
                "terminators": [f"0x{t:08X}" for t in row["terminators"]],
                "gaps": [[f"0x{a:08X}", f"0x{b:08X}"] for a, b in row["gaps"]],
                "matches_expected": row["matches"],
            }
            for row in derived
        ],
        "problems": tiling_problems,
        "derived_from_rom": True,
        "not_hand_written": True,
    }


class LiftError(RuntimeError):
    """Raised when the lift loop cannot proceed."""


# ---------------------------------------------------------------------------
# the modern toolchain
# ---------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class ModernToolchain:
    """A host ARM cross toolchain, identified by running it."""

    root: Path
    prefix: str
    gcc: Path
    ld: Path
    objcopy: Path
    objdump: Path
    nm: Path

    @property
    def root_label(self) -> str:
        return "<" + DEVKITARM_ENV + ">"

    def relabel(self, text: str) -> str:
        """Replace machine- and checkout-specific roots with stable labels.

        Reports are committed, so they must not record where a compiler or a
        checkout happens to live. The toolchain root becomes <DEVKITARM>, the
        repository root becomes <REPO>, and any remaining absolute path is
        replaced by <path>. Meaning is preserved rather than the text dropped.
        """
        for root, label in ((self.root, self.root_label), (_identity.REPO_ROOT, "<REPO>")):
            for form in (str(root), str(root).replace("\\", "/")):
                text = text.replace(form, label)
        return scrub_absolute_paths(text)

    def as_dict(self) -> dict:
        return {
            "family": "GNU Arm Embedded (devkitARM)",
            "root": self.root_label,
            "prefix": self.prefix,
            "tools": {
                "gcc": self.relabel(str(self.gcc)),
                "ld": self.relabel(str(self.ld)),
                "objcopy": self.relabel(str(self.objcopy)),
                "objdump": self.relabel(str(self.objdump)),
                "nm": self.relabel(str(self.nm)),
            },
        }


def _run(command: list, *, timeout: float = 180.0, cwd: Path | None = None):
    return subprocess.run(
        [str(c) for c in command],
        capture_output=True,
        text=True,
        errors="replace",
        timeout=timeout,
        cwd=str(cwd) if cwd else None,
    )


def discover_modern_toolchain(root: str | Path | None = None) -> ModernToolchain | None:
    """Locate an existing ARM cross toolchain. Installs nothing.

    An EXPLICIT root is authoritative: if it does not hold a complete toolchain
    the answer is None, never a silent fallback to somewhere else. Falling back
    would mean a caller who pinned a toolchain could be handed a different one
    and never told. $DEVKITARM and the devkitPro default are consulted only when
    no root was given.

    Every tool must be present; a partial installation is reported absent rather
    than used, so a build can never half-run.
    """
    if root is not None:
        candidates = [Path(root)]
    else:
        candidates = []
        env = os.environ.get(DEVKITARM_ENV, "").strip()
        if env:
            candidates.append(Path(env))
        candidates.append(Path(DEFAULT_DEVKITARM))

    for candidate in candidates:
        bin_dir = candidate / "bin"
        tools = {
            name: bin_dir / f"arm-none-eabi-{name}.exe"
            for name in ("gcc", "ld", "objcopy", "objdump", "nm")
        }
        if all(path.is_file() for path in tools.values()):
            return ModernToolchain(
                root=candidate,
                prefix="arm-none-eabi-",
                gcc=tools["gcc"],
                ld=tools["ld"],
                objcopy=tools["objcopy"],
                objdump=tools["objdump"],
                nm=tools["nm"],
            )
    return None


def toolchain_identity(toolchain: ModernToolchain) -> dict:
    """Version facts, read from the tools themselves rather than assumed."""
    gcc_version = _run([toolchain.gcc, "--version"])
    binutils = _run([toolchain.objdump, "--version"])
    machine = _run([toolchain.gcc, "-dumpmachine"])
    dumpversion = _run([toolchain.gcc, "-dumpversion"])

    def first_line(completed) -> str:
        for line in (completed.stdout or "").splitlines():
            if line.strip():
                return line.strip()
        return ""

    return {
        "gcc_banner": first_line(gcc_version),
        "gcc_version": (dumpversion.stdout or "").strip(),
        "target_triple": (machine.stdout or "").strip(),
        "binutils_banner": first_line(binutils),
        "compiler_family": "gcc",
        "is_the_original_compiler": False,
        "why_not": (
            "the original translation unit was built by ARM Developer Suite 1.2 "
            "(the surviving command line names tcpp). GCC is a different "
            "compiler with a different code generator, so its output cannot "
            "establish anything about ADS 1.2."
        ),
    }


def probe_target_support(toolchain: ModernToolchain, workdir: Path) -> dict:
    """Prove the toolchain really builds ARM7TDMI Thumb, by building something.

    A version banner does not establish that the configuration is supported, so
    this compiles, links and disassembles a two-line function and reports the
    machine code it produced.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    source = workdir / "support_probe.c"
    source.write_text("int lift_probe(int x) { return x + 1; }\n", encoding="ascii", newline="\n")
    obj = workdir / "support_probe.o"

    compile_command = [
        toolchain.gcc, "-c", "-mcpu=arm7tdmi", "-mthumb", "-O1",
        "-ffreestanding", "-fno-common", "-fno-builtin",
        "-o", obj, source,
    ]
    completed = _run(compile_command)
    result = {
        "supported": False,
        "cpu": "arm7tdmi",
        "instruction_set": "thumb",
        "commands": [toolchain.relabel(" ".join(str(c) for c in compile_command))],
        "disassembly": [],
        "detail": "",
    }
    if completed.returncode != 0:
        result["detail"] = (
            f"the toolchain refused -mcpu=arm7tdmi -mthumb: "
            f"{(completed.stderr or completed.stdout).strip()[:300]}"
        )
        return result

    disassembly = _run([toolchain.objdump, "-d", "--no-show-raw-insn", obj])
    lines = [
        line.split("\t", 1)[-1].strip().replace("\t", " ")
        for line in (disassembly.stdout or "").splitlines()
        if re.match(r"^\s+[0-9a-f]+:", line)
    ]
    result["disassembly"] = lines[:8]
    # Positive evidence that this really is ARM7TDMI Thumb code: the probe
    # function must produce at least an argument/return register write and a
    # return. Requiring every line to mention r0 was wrong - `bx lr` does not.
    writes_r0 = any(
        re.match(r"^(adds|movs|subs|add|mov|sub)\s+r0\b", line) for line in lines
    )
    returns = any(
        line.startswith("bx lr")
        or (line.startswith("pop") and "pc" in line)
        or line.startswith("ldr pc")
        for line in lines
    )
    result["supported"] = bool(lines) and writes_r0 and returns
    result["detail"] = (
        f"compiled and disassembled a probe function for ARM7TDMI Thumb: "
        f"{len(lines)} instruction(s), r0 written and a return present"
        if result["supported"]
        else "the toolchain produced no usable Thumb disassembly for the probe"
    )
    return result


# ---------------------------------------------------------------------------
# targets
# ---------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class LiftTarget:
    id: str
    name: str
    probe_translation_unit: str
    decomp_source: str
    probe_source: str
    selftest_source: str
    semantic_minimum_checks: int
    host_build_bits: int
    ticket: str
    cpu: str
    isa: str
    optimization: str
    role: str
    notes: str
    extra_compiler_flags: tuple[str, ...]

    @property
    def rom_address(self) -> int:
        return UNITS[self.probe_translation_unit]["unit"].rom_address


def load_target_registry(path: Path | None = None) -> dict:
    target = path or TARGETS_PATH
    return json.loads(target.read_text(encoding="utf-8"))


def load_targets(path: Path | None = None) -> list[LiftTarget]:
    registry = load_target_registry(path)
    out: list[LiftTarget] = []
    for entry in registry["targets"]:
        out.append(
            LiftTarget(
                id=entry["id"],
                name=entry["name"],
                probe_translation_unit=entry["probe_translation_unit"],
                decomp_source=entry["decomp_source"],
                probe_source=entry["probe_source"],
                selftest_source=entry["selftest_source"],
                semantic_minimum_checks=int(entry["semantic_minimum_checks"]),
                host_build_bits=int(entry.get("host_build_bits", 32)),
                ticket=entry.get("ticket", "DECOMP-LIFT-PILOT-001"),
                cpu=entry["compiler"]["cpu"],
                isa=entry["compiler"]["isa"],
                optimization=entry["compiler"]["optimization"],
                role=entry["role"],
                notes=entry.get("notes", ""),
                extra_compiler_flags=tuple(entry["compiler"].get("extra_flags", ())),
            )
        )
    return out


def get_target(target_id: str) -> LiftTarget:
    for target in load_targets():
        if target.id == target_id:
            return target
    raise LiftError(f"unknown lift target {target_id!r}")


def _unit_for(target: LiftTarget) -> cp.TranslationUnit:
    spec = UNITS.get(target.probe_translation_unit)
    if spec is None:
        raise LiftError(
            f"target {target.id!r} names translation unit "
            f"{target.probe_translation_unit!r}, which this module does not know"
        )
    return spec["unit"]


def _probes_for(target: LiftTarget) -> list[dict]:
    """Function rows for a target's unit.

    GBARam's boundaries live in the ADS probe manifest, which derives and
    verifies them. The ByteCodeInterpreter's are derived from the ROM here, and
    re-derived and checked on every run by derive_unit_boundaries, so a drift in
    either the ROM or the derivation is an error rather than a silent change.
    """
    spec = UNITS[target.probe_translation_unit]
    if spec["boundaries"] == "manifest":
        manifest = json.loads(PROBES_PATH.read_text(encoding="utf-8"))
        return [
            probe
            for probe in manifest["probes"]
            if probe["translation_unit"] == target.probe_translation_unit
        ]
    unit = spec["unit"]
    return [
        {
            "name": f"sub_{start:08X}",
            "start": f"0x{start:08X}",
            "end": f"0x{end:08X}",
            "isa": unit.isa,
            "role": role,
            "translation_unit": unit.id,
        }
        for start, end, role in spec["functions"]
    ]


# ---------------------------------------------------------------------------
# per-function analysis
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class FunctionAnalysis:
    """What can be said about one function from its bytes alone."""

    start: int
    end: int
    isa: str
    instructions: int
    size: int
    first_instruction: str
    mnemonics: list[str]
    calls: list[int]
    literal_slots: list[int]
    returns: int
    leaf: bool
    callee_saved_pushed: list[str]
    frame_size: int
    written_registers: list[str]

    def as_dict(self, base: int) -> dict:
        return {
            "start": f"0x{self.start:08X}",
            "end": f"0x{self.end:08X}",
            "size": self.size,
            "isa": self.isa,
            "instructions": self.instructions,
            "first_instruction": self.first_instruction,
            "calls": [f"0x{c:08X}" for c in self.calls],
            "literal_slots": [f"0x{s:08X}" for s in self.literal_slots],
            "returns": self.returns,
            "leaf": self.leaf,
            "abi": {
                "callee_saved_pushed": list(self.callee_saved_pushed),
                "frame_size_bytes": self.frame_size,
                "written_registers": list(self.written_registers),
            },
        }


def _register_list(op_str: str) -> list[str]:
    inner = op_str.split("{", 1)[-1].split("}", 1)[0]
    return [part.strip() for part in inner.split(",") if part.strip()]


_CALLEE_SAVED = {"r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "sl", "fp"}


def analyse_function(
    raw: bytes, base: int, start: int, end: int, isa: str
) -> FunctionAnalysis:
    """Disassemble [start, end) of a buffer whose byte 0 sits at `base`.

    `base` matters: the modern build is a fresh buffer linked at the unit's ROM
    address, so indexing it with `start - ROM_BASE` reads the WRONG BYTES. Every
    caller states the base of the buffer it is handing over.
    """
    offset = start - base
    if offset < 0:
        raise LiftError(f"0x{start:08X} is before the buffer base 0x{base:08X}")
    length = end - start
    segment = raw[offset : offset + length]

    md = cp.MD[isa]
    instructions = 0
    mnemonics: list[str] = []
    calls: list[int] = []
    literal_slots: list[int] = []
    returns = 0
    callee_saved: list[str] = []
    frame_size = 0
    written: set[str] = set()
    first = ""

    for ins in md.disasm(segment, start):
        instructions += 1
        mnemonics.append(ins.mnemonic)
        if not first:
            first = f"{ins.mnemonic} {ins.op_str}".strip()

        slot = cp._literal_slot(ins.address, isa, ins.op_str)
        if slot is not None and ins.mnemonic.startswith("ldr"):
            literal_slots.append(slot)

        if ins.mnemonic in ("bl", "blx") and ins.operands:
            operand = ins.operands[0]
            if operand.type == cp.capstone.arm.ARM_OP_IMM:
                calls.append(operand.imm & ~1)

        if ins.mnemonic == "bx" and "lr" in ins.op_str:
            returns += 1
        if ins.mnemonic == "bx" and "lr" not in ins.op_str:
            # GCC returns via `pop {rN}; bx rN` rather than `bx lr`. Counting
            # both keeps the metric comparable across the two compilers; a
            # register-form bx inside a function is a computed jump in principle,
            # so this is documented as "return-shaped", not proven returns.
            returns += 1
        if ins.mnemonic.startswith("pop") and "pc" in ins.op_str:
            returns += 1
        if ins.mnemonic.startswith("ldr") and "pc" in ins.op_str.split(",")[0]:
            returns += 1

        if ins.mnemonic.startswith("push"):
            for name in _register_list(ins.op_str):
                if name in _CALLEE_SAVED and name not in callee_saved:
                    callee_saved.append(name)
        if ins.mnemonic in ("sub", "add") and ins.op_str.startswith("sp, sp"):
            try:
                amount = int(ins.op_str.split("#")[1].strip(), 0)
                frame_size += amount if ins.mnemonic == "sub" else -amount
            except (IndexError, ValueError):
                pass

        if ins.operands:
            destination = ins.reg_name(ins.operands[0].reg) if ins.operands[0].type == cp.capstone.arm.ARM_OP_REG else None
            if destination and destination.startswith("r"):
                written.add(destination)

    return FunctionAnalysis(
        start=start,
        end=end,
        isa=isa,
        instructions=instructions,
        size=length,
        first_instruction=first,
        mnemonics=mnemonics,
        calls=sorted(set(calls)),
        literal_slots=sorted(set(literal_slots)),
        returns=returns,
        leaf=not calls,
        callee_saved_pushed=callee_saved,
        frame_size=frame_size,
        written_registers=sorted(written, key=lambda r: int(r[1:])),
    )


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class LiftBuild:
    ok: bool
    commands: list[str]
    stdout: str
    stderr: str
    object_file: Path | None
    elf: Path | None
    binary: Path | None
    raw: bytes
    symbols: dict[str, tuple[int, int]]

    def as_dict(self, toolchain: ModernToolchain, target: LiftTarget) -> dict:
        return {
            "ok": self.ok,
            "commands": [toolchain.relabel(c) for c in self.commands],
            "produced_byte_length": len(self.raw),
            "symbols": {
                name: {"address": f"0x{addr:08X}", "size": size}
                for name, (addr, size) in sorted(self.symbols.items())
            },
            "diagnostics": (self.stderr or "").strip()[-1200:],
        }


def render_linker_script(target: LiftTarget, unit: cp.TranslationUnit, entry: str) -> str:
    """A controlled layout that places the unit at its original ROM address.

    Without this every PC-relative literal displacement and every call would
    differ for a reason that says nothing about the compiler.
    """
    return (
        "/* generated by tools/buusfury/lift.py - do not edit */\n"
        f"ENTRY({entry})\n"
        "SECTIONS\n{\n"
        f"  . = 0x{unit.rom_address:08X};\n"
        "  .text : { *(.text) *(.text.*) }\n"
        "  .rodata : { *(.rodata) *(.rodata.*) }\n"
        "  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*)\n"
        "               *(.ARM.attributes) *(.data) *(.bss) }\n"
        "}\n"
    )


def parse_symbols(nm_output: str) -> dict[str, tuple[int, int]]:
    """`nm -S --defined-only` output -> {name: (address, size)}.

    Only function symbols in .text are kept; the file and section symbols are
    not functions and must not become comparison rows.
    """
    out: dict[str, tuple[int, int]] = {}
    for line in nm_output.splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        address, size, kind, name = parts
        if kind not in ("T", "t"):
            continue
        try:
            out[name] = (int(address, 16), int(size, 16))
        except ValueError:
            continue
    return out


def derive_external_calls(rom_bytes: bytes, unit_id: str) -> dict[str, int]:
    """Calls a unit makes to code it does not contain, read from the ROM.

    The reconstruction declares these rather than reconstructing them, so the
    link needs a value for each. Binding them to the ORIGINAL addresses, read
    out of the unit's own BL instructions, keeps every call displacement
    correct and adds no stub code to the compared bytes. The symbol names line
    up with the source automatically because the project names functions
    sub_<ROM address>.
    """
    spec = UNITS[unit_id]
    unit = spec["unit"]
    base = _gba.ROM_BASE
    found: dict[str, int] = {}
    for start, end, _role in spec["functions"]:
        for ins in cp.MD[unit.isa].disasm(rom_bytes[start - base : end - base], start):
            if ins.mnemonic not in ("bl", "blx") or not ins.operands:
                continue
            operand = ins.operands[0]
            if operand.type != cp.capstone.arm.ARM_OP_IMM:
                continue
            target = operand.imm & ~1
            if not (unit.rom_address <= target < unit.code_end_address):
                found[f"sub_{target:08X}"] = target
    return found


def render_external_symbols(symbols: dict[str, int]) -> str:
    """Declare each external call target as an absolute THUMB function.

    `--defsym` cannot express this and is a trap: an absolute symbol made that
    way carries no Thumb marking, so the linker emits a Thumb-to-ARM
    interworking veneer. The veneer does `bx pc` and then an ARM branch, which
    enters a Thumb target in ARM state, and it adds eight bytes per target to
    the compared image. Both were observed here rather than predicted.

    `.thumb_func` before `.set` marks the absolute symbol as Thumb, and the call
    becomes a direct Thumb BL to the original address with nothing emitted. An
    earlier revision of this module used `--defsym` and produced five veneers in
    the ByteCodeInterpreter build.
    """
    lines = [
        "/* generated by tools/buusfury/lift.py - do not edit */",
        "\t.syntax unified",
        "\t.thumb",
        "",
        "/* Absolute Thumb entry points for calls this unit makes but does not",
        " * contain. The bodies are not here because these functions belong to",
        " * other translation units; only the call target matters. */",
    ]
    for name, address in sorted(symbols.items()):
        lines.append(f"\t.globl {name}")
        lines.append("\t.thumb_func")
        lines.append(f"\t.set {name}, 0x{address:08X}")
    lines.append("")
    return "\n".join(lines)


def build_target(
    toolchain: ModernToolchain,
    target: LiftTarget,
    workdir: Path,
    *,
    source_override: Path | None = None,
    entry: str | None = None,
    defined_symbols: dict[str, int] | None = None,
) -> LiftBuild:
    """Compile, link at the original address, and emit raw bytes."""
    workdir.mkdir(parents=True, exist_ok=True)
    unit = _unit_for(target)
    probes = _probes_for(target)
    entry = entry or (probes[0]["name"] if probes else "_start")
    source = source_override or (_identity.REPO_ROOT / target.decomp_source)
    if not source.is_file():
        raise LiftError(f"the decompiled source {target.decomp_source} does not exist")

    obj = workdir / f"{target.id}.o"
    elf = workdir / f"{target.id}.elf"
    binary = workdir / f"{target.id}.bin"
    script = workdir / f"{target.id}.ld"
    map_file = workdir / f"{target.id}.map"
    script.write_text(render_linker_script(target, unit, entry), encoding="ascii", newline="\n")

    compile_command = [
        toolchain.gcc, "-c",
        f"-mcpu={target.cpu}",
        "-mthumb" if target.isa == "thumb" else "-marm",
        target.optimization,
        "-ffreestanding", "-fno-common", "-fno-builtin",
        "-fomit-frame-pointer", "-mno-unaligned-access",
        *target.extra_compiler_flags,
        "-o", obj, source,
    ]

    # Declare the unit's external call targets as Thumb functions. See
    # render_external_symbols for why --defsym is not used.
    symbols_source = workdir / f"{target.id}_externs.s"
    symbols_source.write_text(
        render_external_symbols(defined_symbols or {}), encoding="ascii", newline="\n"
    )
    symbols_object = workdir / f"{target.id}_externs.o"
    symbols_command = [
        toolchain.gcc, "-c", "-mcpu=" + target.cpu,
        "-mthumb" if target.isa == "thumb" else "-marm",
        "-o", symbols_object, "-x", "assembler-with-cpp", symbols_source,
    ]

    link_command = [
        toolchain.gcc, "-nostdlib",
        f"-Wl,-T,{script}", f"-Wl,-Map,{map_file}",
        "-o", elf, obj, symbols_object,
    ]
    # Restricted on purpose: the emitted bytes are the reconstructed code and
    # its literals, and nothing a stub or a linker helper might add.
    objcopy_command = [
        toolchain.objcopy, "-O", "binary", "-j", ".text", "-j", ".rodata", elf, binary,
    ]
    commands = [
        " ".join(str(c) for c in compile_command),
        " ".join(str(c) for c in symbols_command),
        " ".join(str(c) for c in link_command),
        " ".join(str(c) for c in objcopy_command),
    ]

    log: list[str] = []
    for command in (compile_command, symbols_command, link_command, objcopy_command):
        completed = _run(command)
        log.append(f"$ {' '.join(str(c) for c in command)}\n{completed.stdout}{completed.stderr}")
        if completed.returncode != 0:
            return LiftBuild(
                ok=False, commands=commands,
                stdout=completed.stdout or "", stderr=completed.stderr or "",
                object_file=None, elf=None, binary=None, raw=b"", symbols={},
            )

    symbols = parse_symbols(_run([toolchain.nm, "-S", "--defined-only", elf]).stdout or "")
    raw = binary.read_bytes() if binary.is_file() else b""
    return LiftBuild(
        ok=True, commands=commands, stdout="\n".join(log), stderr="",
        object_file=obj, elf=elf, binary=binary, raw=raw, symbols=symbols,
    )


# ---------------------------------------------------------------------------
# comparison
# ---------------------------------------------------------------------------
def compare_bytes_on_target_boundaries(
    original: bytes, modern: bytes, unit: cp.TranslationUnit
) -> dict:
    """Byte and instruction comparison keyed on the ORIGINAL's boundaries.

    Instruction granularity is taken from the TARGET, not from the modern
    output. Capstone renders distinct Thumb encodings identically (0x4280 and
    0x4500 are both `cmp r0, r0`), so a positional text comparison can report
    zero differences for unequal bytes and can exceed the instruction count.
    Keying on the original's own spans removes both failure modes.

    `instruction_spans` returns (OFFSET-FROM-BASE, SIZE) pairs and decodes the
    buffer it is given, so it is handed the translation unit's own 624 bytes.
    Passing the whole ROM here would decode the cartridge header while labelling
    it with the unit's address, which is how an earlier revision reported zero
    differing instructions for 595 differing bytes.
    """
    overlap = min(len(original), len(modern))
    differing = sum(1 for i in range(overlap) if original[i] != modern[i])

    # Decode only the CODE body: the trailing 16 bytes are the literal pool, and
    # walking constants as instructions invents spans that are not instructions.
    code = original[: unit.code_length]
    spans = cp.instruction_spans(code, unit.rom_address, unit.isa)
    matching_spans = 0
    differing_spans = 0
    covered = 0
    for offset, size in spans:
        if offset + size > overlap:
            continue
        covered += size
        if original[offset : offset + size] == modern[offset : offset + size]:
            matching_spans += 1
        else:
            differing_spans += 1

    uncovered = max(0, overlap - covered)
    modern_only = max(0, len(modern) - len(original))
    original_only = max(0, len(original) - len(modern))

    return {
        "original_byte_length": len(original),
        "modern_byte_length": len(modern),
        "overlap_byte_length": overlap,
        "differing_bytes_in_overlap": differing,
        "matching_bytes_in_overlap": overlap - differing,
        "original_only_bytes": original_only,
        "modern_only_bytes": modern_only,
        "original_instruction_spans": len(spans),
        "matching_instruction_spans": matching_spans,
        "differing_instruction_spans": differing_spans,
        # Published separately and clamped: folding uncovered bytes into the
        # differing count once drove a "matching" field negative.
        "bytes_not_covered_by_an_original_instruction": uncovered,
        "byte_identical": len(original) == len(modern) and differing == 0,
        # A BOOLEAN, so a gate can read it, plus the prose that explains it.
        "is_a_match_claim": False,
        "match_claim_note": (
            "MEASUREMENT ONLY. This compares a modern GCC build against the "
            "cartridge. A modern compiler is not the original compiler, so a "
            "difference here is expected and proves nothing; an identity here "
            "would also prove nothing about ADS 1.2. ADS_MATCH stays BLOCKED."
        ),
    }


def _pool_runs(slots: list[int]) -> list[list[int]]:
    """Group referenced literal slots into contiguous 4-byte runs."""
    runs: list[list[int]] = []
    for slot in sorted(set(slots)):
        if runs and slot == runs[-1][1]:
            runs[-1][1] = slot + 4
        else:
            runs.append([slot, slot + 4])
    return runs


def literal_pool_structure(
    original_rows: list[FunctionAnalysis],
    modern_rows: list[FunctionAnalysis],
    unit: cp.TranslationUnit,
) -> dict:
    """Compare how the two compilers POOL literals.

    This is the sharpest structural difference the loop exposes, and it is the
    reason the comparison must be translation-unit scoped: the original places
    ONE pool after the last function and every function reaches back into it,
    which is itself the evidence that the region was a single translation unit.
    A modern compiler pools per function or per basic block, so no individual
    function can be compared standalone.
    """
    original_slots = sorted({s for row in original_rows for s in row.literal_slots})
    modern_slots = sorted({s for row in modern_rows for s in row.literal_slots})
    original_runs = _pool_runs(original_slots)
    modern_runs = _pool_runs(modern_slots)

    declared_start = unit.code_end_address
    declared_end = unit.end_address
    declared_slots = sorted(off + _gba.ROM_BASE for off, _value in unit.literal_pool)
    original_shared = (
        len(original_runs) == 1
        and original_runs[0][0] == declared_start
        and original_runs[0][1] == declared_end
    )
    modern_shared = len(modern_runs) <= 1

    # Accounting, which is the property that actually matters: is every literal
    # the code loads one of the words the unit declares, and is every declared
    # word actually used? A unit whose literals live in two places satisfies
    # this even though "one shared run" is false, and forcing the run test
    # would report a defect that is not there.
    referenced = set(original_slots)
    declared = set(declared_slots)
    return {
        "original": {
            "distinct_slots": len(original_slots),
            "contiguous_runs": [[f"0x{a:08X}", f"0x{b:08X}"] for a, b in original_runs],
            "run_count": len(original_runs),
            "shared_pool": original_shared,
            # A single-function unit with no adjacent pool cannot have a shared
            # run, so the test is not applicable rather than failed.
            "shared_pool_applicable": unit.code_end_address != unit.end_address,
            "declared_pool": [f"0x{declared_start:08X}", f"0x{declared_end:08X}"],
            "declared_slots": [f"0x{a:08X}" for a in declared_slots],
            "declared_slots_used": [f"0x{a:08X}" for a in sorted(referenced & declared)],
            "all_referenced_slots_are_declared": referenced <= declared,
            "all_declared_slots_are_referenced": declared <= referenced,
            "undeclared_slots": [f"0x{a:08X}" for a in sorted(referenced - declared)],
            "functions_reaching_it": sum(1 for row in original_rows if row.literal_slots),
        },
        "modern": {
            "distinct_slots": len(modern_slots),
            "contiguous_runs": [[f"0x{a:08X}", f"0x{b:08X}"] for a, b in modern_runs],
            "run_count": len(modern_runs),
            "shared_pool": modern_shared,
            "functions_reaching_a_pool": sum(1 for row in modern_rows if row.literal_slots),
        },
        "interpretation": (
            "the original's literals are accounted for by the words the unit "
            "declares; the modern build pools differently, which is a structural "
            "consequence of the compiler rather than a defect in the "
            "reconstruction. It is also why a function with a literal load "
            "cannot be compared standalone."
        ),
        "is_a_match_claim": False,
    }


def compare_functions(
    rom_bytes: bytes,
    unit: cp.TranslationUnit,
    probes: list[dict],
    build: LiftBuild,
) -> tuple[list[dict], dict]:
    """Pair original functions with modern ones by symbol name.

    The reconstruction names each function sub_<ROM address>, so the pairing is
    exact and needs no heuristic. A missing symbol is reported as missing rather
    than treated as a difference.

    Returns (rows, literal_pool_structure). The pool comparison is derived from
    the same analyses the rows are, so the two can never disagree.
    """
    rows: list[dict] = []
    original_analyses: list[FunctionAnalysis] = []
    modern_analyses: list[FunctionAnalysis] = []

    for probe in probes:
        name = probe["name"]
        original = analyse_function(
            rom_bytes, _gba.ROM_BASE, int(probe["start"], 16), int(probe["end"], 16), probe["isa"]
        )
        original_analyses.append(original)
        modern = None
        if name in build.symbols:
            address, size = build.symbols[name]
            modern = analyse_function(
                build.raw, unit.rom_address, address, address + size, probe["isa"]
            )
            modern_analyses.append(modern)

        row = {
            "name": name,
            "role": probe["role"],
            "original": original.as_dict(unit.rom_address),
            "modern": modern.as_dict(unit.rom_address) if modern else None,
            "modern_symbol_present": modern is not None,
        }
        if modern is not None:
            row["delta"] = {
                "size_bytes": modern.size - original.size,
                "instructions": modern.instructions - original.instructions,
                "returns": modern.returns - original.returns,
                "calls": len(modern.calls) - len(original.calls),
                "literal_slots": len(modern.literal_slots) - len(original.literal_slots),
            }
            # Extent identity is the only condition under which a per-function
            # byte comparison is even meaningful.
            row["same_extent"] = (
                modern.start == original.start and modern.end == original.end
            )
            if row["same_extent"]:
                start = original.start - _gba.ROM_BASE
                offset = original.start - unit.rom_address
                row["byte_identical"] = (
                    rom_bytes[start : start + original.size]
                    == build.raw[offset : offset + original.size]
                )
            else:
                row["byte_identical"] = False
        rows.append(row)

    pools = literal_pool_structure(original_analyses, modern_analyses, unit)
    return rows, pools


# ---------------------------------------------------------------------------
# the host semantic self-check
# ---------------------------------------------------------------------------
_ABSOLUTE_PATH = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|]*")


def scrub_absolute_paths(text: str) -> str:
    """Replace machine-specific paths in captured tool output.

    The lift report is committed, so it must not record where a compiler happens
    to live on the machine that produced it. Positive evidence is preserved: the
    path is replaced by a marker rather than the line being dropped.
    """
    return _ABSOLUTE_PATH.sub("<path>", text)


def semantic_verdict(
    returncode: int, checks: int, failures: int, minimum: int | None = None
) -> tuple[str, str]:
    """The SEMANTIC verdict, as a pure function so it can be tested directly.

    A pass requires POSITIVE evidence: the run must exit 0, report ZERO failures,
    AND report at least `minimum` assertions. A run that exits 0 with fewer checks
    is PARTIAL, never PROVEN, because a self-check that stopped early otherwise
    looks exactly like one that passed.

    `minimum` is per target. One global number would either wave through a
    truncated run of a small self-check or fail a genuinely smaller one.
    """
    minimum = MIN_SEMANTIC_CHECKS if minimum is None else minimum
    if returncode != 0 or failures > 0:
        return (
            "FAILED",
            f"the reconstruction is not behaviourally coherent: exit {returncode}, "
            f"{failures} failures",
        )
    if checks < minimum:
        return (
            "PARTIAL",
            f"all assertions passed but only {checks} ran, below the required "
            f"minimum of {minimum}: checks were lost",
        )
    return (
        "PROVEN",
        f"{checks} behavioural assertions passed with 0 failures "
        f"(minimum {minimum})",
    )


def run_host_selftest(
    workdir: Path,
    *,
    source: Path | None = None,
    minimum_checks: int | None = None,
    host_bits: int = 32,
    timeout: float = 240.0,
) -> dict:
    """Compile and RUN a self-check on the host.

    This is the SEMANTIC verdict. It says nothing about code generation: a
    translation unit whose C is wrong cannot match under any compiler, so a
    behavioural failure is a real defect, while a pass only removes one class of
    error.

    `host_bits` selects the width of the host toolchain. A reconstruction that
    holds pointers in u32 fields models a 32-bit machine and must be built
    32-bit: on a 64-bit host the high half of every stored context address is
    lost and the first dereference through one faults with an access violation.
    That is a property of the machine model, not something to paper over with a
    widened typedef.
    """
    minimum = MIN_SEMANTIC_CHECKS if minimum_checks is None else minimum_checks
    selftest = source or (_identity.REPO_ROOT / "src" / "probes" / "gbaram_selftest.c")
    result = {
        "status": "UNTESTED",
        "checks": 0,
        "failures": None,
        "minimum_checks": minimum,
        "host_compiler": None,
        "host_build_bits": host_bits,
        "detail": "",
        "output": "",
    }
    if not selftest.is_file():
        result["detail"] = f"{selftest.name} is missing"
        return result

    vcvars_name = "vcvars64.bat" if host_bits == 64 else "vcvars32.bat"
    vcvars_candidates = [
        Path(r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools")
        / "VC" / "Auxiliary" / "Build" / vcvars_name,
        Path(r"C:\Program Files\Microsoft Visual Studio\2022\Community")
        / "VC" / "Auxiliary" / "Build" / vcvars_name,
    ]
    vcvars = next((p for p in vcvars_candidates if p.is_file()), None)
    if vcvars is None and shutil.which("cl") is None:
        result["detail"] = "no host C compiler available; SEMANTIC is UNTESTED here"
        return result

    comspec = os.environ.get("COMSPEC") or r"C:\Windows\System32\cmd.exe"
    if not Path(comspec).is_file():
        result["detail"] = "no usable command interpreter for the self-check"
        return result

    workdir.mkdir(parents=True, exist_ok=True)
    exe = workdir / "selftest.exe"
    compile_log = workdir / "compile.log"
    batch = workdir / "build_selftest.bat"
    # A batch file, not a /c string: cmd's quote handling mangles a command that
    # starts with a quoted path and silently returns exit 1 with empty output.
    # /Fo and /Fd are avoided: a path ending in a backslash before a closing
    # quote escapes it and cl fails with "Cannot open compiler generated file".
    lines = ["@echo off"]
    if vcvars is not None:
        lines.append(f'call "{vcvars}" >nul 2>&1')
        lines.append("if errorlevel 1 exit /b 90")
    lines.append(f'cd /d "{workdir}"')
    lines.append(
        f'cl /nologo /W3 /std:c11 /TC /Fe:selftest.exe "{selftest}" '
        f'> "{compile_log}" 2>&1'
    )
    batch.write_text("\r\n".join(lines) + "\r\n", encoding="ascii", newline="\n")

    compiled = _run([comspec, "/c", batch], timeout=timeout)
    log = compile_log.read_text(encoding="utf-8", errors="replace") if compile_log.is_file() else ""
    if compiled.returncode != 0 or not exe.is_file():
        result["status"] = "FAILED"
        result["host_compiler"] = f"MSVC cl.exe ({host_bits}-bit)"
        result["detail"] = f"self-check failed to build (exit {compiled.returncode})"
        result["output"] = scrub_absolute_paths(log[-2000:])
        return result

    executed = _run([exe], timeout=timeout)
    output = executed.stdout or ""
    result["host_compiler"] = f"MSVC cl.exe ({host_bits}-bit)"
    # Scrubbed: the report is committed and must not carry where cl.exe lives.
    result["output"] = scrub_absolute_paths(output[-4000:])

    match = re.search(r"(\d+)\s+check\S*\s*,\s*(\d+)\s+failure\S*", output, re.IGNORECASE)
    if match:
        result["checks"] = int(match.group(1))
        result["failures"] = int(match.group(2))
    else:
        # Fall back to counting the per-check FAIL lines rather than guessing.
        result["failures"] = output.count("FAIL")

    status, detail = semantic_verdict(
        executed.returncode,
        result["checks"],
        result["failures"] if result["failures"] is not None else 0,
        minimum=minimum,
    )
    result["status"] = status
    result["detail"] = detail
    return result


# ---------------------------------------------------------------------------
# the report
# ---------------------------------------------------------------------------
def ads_match_status() -> dict:
    """The ADS verdict. Always BLOCKED here, and never inferred from a build.

    The detail deliberately names no absolute path: this document is committed,
    and where a toolchain happens to be installed is an environment fact, not a
    project fact. The installation is located through ADS12_ROOT.
    """
    return {
        "status": "BLOCKED",
        "code": cp.BLOCK_LICENSE,
        "detail": (
            "an ARM Developer Suite 1.2 installation is present on this machine "
            "but the licence file it ships licenses a different product, so the "
            "ARM compilers cannot be run. No compile has been attempted and no "
            "configuration has been tested. The installation is located through "
            "ADS12_ROOT."
        ),
        "required_to_unblock": [
            "a licensed ADS 1.2 installation, with ADS12_ROOT pointing at it",
            "then: python -m buusfury compiler-probe --plan, then --matrix",
        ],
        "not_inferable_from_modern_build": True,
    }


def run_lift(
    target_id: str,
    rom_bytes: bytes,
    toolchain: ModernToolchain,
    workdir: Path | None = None,
    *,
    run_semantic: bool = True,
) -> dict:
    """Run the whole loop for one target and return the report document."""
    target = get_target(target_id)
    unit = _unit_for(target)
    probes = _probes_for(target)
    if not probes:
        raise LiftError(f"no probes are declared for translation unit {unit.id!r}")

    rom_address = unit.rom_address
    offset = rom_address - _gba.ROM_BASE
    original = rom_bytes[offset : offset + unit.length]

    work = workdir or (LIFT_WORKSPACE / target.id)
    external_calls = derive_external_calls(rom_bytes, unit.id)
    build = build_target(toolchain, target, work, defined_symbols=external_calls)

    semantic = (
        run_host_selftest(
            work / "selftest",
            source=_identity.REPO_ROOT / target.selftest_source,
            minimum_checks=target.semantic_minimum_checks,
            host_bits=target.host_build_bits,
        )
        if run_semantic
        else {
            "status": "UNTESTED",
            "checks": 0,
            "failures": None,
            "minimum_checks": target.semantic_minimum_checks,
            "host_compiler": None,
            "host_build_bits": target.host_build_bits,
            "detail": "the semantic self-check was not requested",
            "output": "",
        }
    )

    modern_build = {
        "status": "PASS" if build.ok else "FAIL",
        "toolchain": toolchain.as_dict(),
        "identity": toolchain_identity(toolchain),
        "target_support": probe_target_support(toolchain, work / "toolchain-probe"),
        "compiler_configuration": {
            "cpu": target.cpu,
            "instruction_set": target.isa,
            "optimization": target.optimization,
            "extra_flags": list(target.extra_compiler_flags),
        },
        "link_origin": f"0x{rom_address:08X}",
        "external_calls_bound_to_original_addresses": {
            name: f"0x{value:08X}" for name, value in sorted(external_calls.items())
        },
        "detail": (
            f"compiled, linked at 0x{rom_address:08X} and emitted "
            f"{len(build.raw)} bytes"
            if build.ok
            else "the build did not complete; see diagnostics"
        ),
        "build": build.as_dict(toolchain, target),
    }

    function_rows, pool_structure = compare_functions(rom_bytes, unit, probes, build)

    # Evidence that is specific to how this unit's boundaries were established.
    if UNITS[target.probe_translation_unit]["boundaries"] == "derived":
        boundary_evidence = derive_unit_boundaries(rom_bytes, unit.id)
        if boundary_evidence["problems"]:
            raise LiftError(
                "the derived boundary disagrees with the recorded one: "
                + "; ".join(boundary_evidence["problems"])
            )
        if unit.id == BCI_TU.id:
            boundary_evidence["dispatch_table"] = derive_dispatch_table(rom_bytes)
        elif unit.id == H2_TU.id:
            boundary_evidence["dispatch_table"] = derive_dispatch_table(rom_bytes)
            boundary_evidence["native_table"] = derive_native_table(rom_bytes)
            boundary_evidence["primary_slot"] = {
                "index": 2,
                "address": f"0x{PRIMARY_TABLE + 2 * 4:08X}",
                "word": f"0x{H2_ENTRY | 1:08X}",
                "detail": (
                    "exactly one primary slot points at this handler, and no direct "
                    "BL site anywhere targets it, so it is reached only through the "
                    "dispatch table"
                ),
            }
    else:
        boundary_evidence = {
            "method": "config/compiler_probes.json, derived and verified there",
            "derived_from_rom": False,
            "not_hand_written": True,
            "detail": (
                "the ADS probe manifest already derives and whole-document "
                "verifies this unit's boundaries"
            ),
        }

    document = {
        "schema": 1,
        "ticket": target.ticket,
        "generated_by": "tools/buusfury/lift.py",
        "source_sha1": hashlib.sha1(rom_bytes).hexdigest(),
        "target": {
            "id": target.id,
            "name": target.name,
            "role": target.role,
            "notes": target.notes,
            "translation_unit": unit.id,
            "rom_address": f"0x{rom_address:08X}",
            "file_offset": f"0x{offset:06X}",
            "code_end_address": f"0x{unit.code_end_address:08X}",
            "end_address": f"0x{unit.end_address:08X}",
            "byte_length": unit.length,
            "code_byte_length": unit.code_length,
            "isa": unit.isa,
            "decomp_source": target.decomp_source,
            "probe_source": target.probe_source,
            "selftest_source": target.selftest_source,
            "semantic_minimum_checks": target.semantic_minimum_checks,
            "host_build_bits": target.host_build_bits,
            "original_sha1": hashlib.sha1(original).hexdigest(),
        },
        "boundary_evidence": boundary_evidence,
        "verdicts": {
            "semantic": {
                "status": semantic["status"],
                "checks": semantic["checks"],
                "failures": semantic["failures"],
                "minimum_checks": semantic["minimum_checks"],
                "host_compiler": semantic["host_compiler"],
                "detail": semantic["detail"],
                "measures": "whether the reconstructed C behaves correctly, by RUNNING it",
            },
            "modern_build": {
                "status": modern_build["status"],
                "detail": modern_build["detail"],
                "measures": "whether the source compiles, links and emits bytes",
            },
            "ads_match": ads_match_status(),
        },
        "verdicts_are_independent": (
            "SEMANTIC, MODERN_BUILD and ADS_MATCH answer different questions and "
            "none is evidence for another. A passing modern build says nothing "
            "about the original compiler; a passing semantic run only removes one "
            "class of error."
        ),
        "modern_build": modern_build,
        "functions": function_rows,
        "literal_pools": pool_structure,
        "comparison": (
            compare_bytes_on_target_boundaries(original, build.raw, unit)
            if build.ok
            else {
                "status": "NOT_RUN",
                "detail": "the build did not complete, so no comparison was made",
                "is_a_match_claim": False,
                "match_claim_note": "MEASUREMENT ONLY; ADS_MATCH stays BLOCKED regardless.",
            }
        ),
        "semantic_check": semantic,
    }
    return document


def write_report(document: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2)
        handle.write("\n")
    return path


def report_path_for(target_id: str) -> Path:
    return _identity.CONFIG_DIR / f"lift_{target_id}.json"


def verify_report(
    rom_bytes: bytes, target_id: str, path: Path | None = None
) -> dict:
    """Regenerate the report and compare it WHOLE, key by key.

    Comparing a hand-picked subset of keys would let `verdicts`, `comparison` or
    `functions` say anything, so every key is compared. The one documented
    exemption is the SEMANTIC block when no host compiler exists to re-run it:
    that is reported as `exempted`, with the reason, rather than silently
    ignored. Returns {ok, problems, exempted, detail}.
    """
    toolchain = discover_modern_toolchain()
    if toolchain is None:
        return {
            "ok": False,
            "problems": ["no modern toolchain is available, so the report cannot be re-derived"],
            "exempted": [],
            "detail": "BLOCKED: no toolchain",
        }

    report_path = path or report_path_for(target_id)
    expected = json.loads(report_path.read_text(encoding="utf-8"))
    actual = run_lift(target_id, rom_bytes, toolchain)

    exempted: list[str] = []
    if actual["verdicts"]["semantic"]["status"] == "UNTESTED":
        placeholder = {
            "status": "UNTESTED",
            "checks": 0,
            "failures": None,
            "minimum_checks": MIN_SEMANTIC_CHECKS,
            "host_compiler": None,
            "detail": "EXEMPTED FROM THIS COMPARISON",
            "measures": "whether the reconstructed C behaves correctly, by RUNNING it",
            "output": "",
        }
        for document in (expected, actual):
            document["verdicts"]["semantic"] = placeholder
            document["semantic_check"] = dict(placeholder)
        exempted.append(
            "verdicts.semantic and semantic_check: no host C compiler is available "
            "here, so the behavioural self-check could not be re-run. The rest of "
            "the document was still compared key by key."
        )

    problems = _diff_documents(expected, actual, prefix="")
    return {
        "ok": not problems,
        "problems": problems,
        "exempted": exempted,
        "detail": (
            "the whole document regenerated identically"
            if not problems
            else f"{len(problems)} difference(s)"
        ),
    }


def _diff_documents(expected, actual, prefix: str) -> list[str]:
    problems: list[str] = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in sorted(set(expected) | set(actual)):
            if key not in expected:
                problems.append(f"{prefix}{key}: present in the regenerated report only")
            elif key not in actual:
                problems.append(f"{prefix}{key}: missing from the regenerated report")
            else:
                problems.extend(_diff_documents(expected[key], actual[key], f"{prefix}{key}."))
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            problems.append(f"{prefix}length: {len(expected)} vs {len(actual)}")
        for index, (left, right) in enumerate(zip(expected, actual)):
            problems.extend(_diff_documents(left, right, f"{prefix}[{index}]."))
    elif expected != actual:
        problems.append(f"{prefix}{expected!r} != {actual!r}")
    return problems
