"""Independent structural analysis of the canonical Buu's Fury ROM.

Everything here derives its conclusions from the ROM bytes plus, where stated,
from project-owned reproductions. No boundary is accepted because the public
disassembly asserts it: where this module agrees with that project it is because
the ROM says so, and `docs/ROM_MAP_PROVENANCE.md` records both the agreement and
every disagreement.

METHOD, in order:

1. PROVEN STRUCTURES. Decode what is self-evident: the GBA header, the reset
   path, the text pool and its pointer table, replayable compressed streams,
   constant-fill runs, and compiler-runtime data the reset path itself points at.
   These become fixed anchors with `proven` confidence.

2. SEGMENTATION. Fill the remaining spans with a windowed classifier driven by
   arms that can be validated: how far an instruction stream decodes before it
   becomes implausible, whether its branches land inside itself, whether it loads
   from its own literal pool, pointer density, entropy and constant runs. The
   classifier is calibrated in `tests/test_rom_map.py` against anchors whose
   answer is already known, so a regression in it fails the build.

3. FUNCTION DISCOVERY. Harvest branch targets and literal-pool code pointers
   from the identified code, follow them to a fixpoint, and validate each entry
   by disassembling from it in the ISA its pointer implies.
"""

from __future__ import annotations

import collections
import dataclasses
import hashlib
import math
from pathlib import Path

import capstone
import numpy as np

from . import gba
from . import rommap as rm

# ---------------------------------------------------------------------------
# capstone handles
# ---------------------------------------------------------------------------
MD_ARM = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
MD_THUMB = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

#: Detail mode is required to read decoded operands (branch targets). It is
#: enabled here once rather than per call site so a forgotten flag cannot turn
#: into a runtime CsError deep inside a sweep.
MD_ARM.detail = True
MD_THUMB.detail = True

#: capstone stops iterating at the first undecodable instruction, which is what
#: makes "how far does this decode" a usable signal. Verified by a test.
_MD = {"arm": MD_ARM, "thumb": MD_THUMB}

#: Thumb and ARM words are aligned differently; callers must respect this.
ALIGNMENT = {"arm": 4, "thumb": 2}

#: A window smaller than this cannot support a classification.
DEFAULT_WINDOW = 0x1000

#: Bytes of constants that make a run "padding" rather than coincidence.
PADDING_MIN_RUN = 256


# ---------------------------------------------------------------------------
# instruction-level primitives
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class DecodeRun:
    """How far a byte range decodes as one instruction set before going bad."""

    isa: str
    offset: int
    bytes_ok: int
    instructions: int
    in_range_branches: int
    local_branches: int
    pc_relative_loads: int
    branch_targets: list[int]
    literal_targets: list[int]

    @property
    def ok(self) -> bool:
        return self.bytes_ok > 0


def _is_plausible_arm(ins: capstone.CsInsn, word: int) -> bool:
    """Reject ARM encodings that ordinary compiled code does not emit."""
    if (word >> 28) == 0xF:  # NV condition
        return False
    mnemonic = ins.mnemonic
    if mnemonic.startswith("undefined") or mnemonic in ("udf", "svc", "swi", "bkpt"):
        # The one legitimate SWI in this image is the semihosting trap; treat it
        # as a run terminator here and let the caller look for it explicitly.
        return False
    if mnemonic.startswith(("v", "nv")) and mnemonic not in ("vpush", "vpop"):
        # NEON/VFP does not exist on ARM7TDMI; these are data decodes.
        return False
    return True


def _literal_slot(ins: capstone.CsInsn, isa: str) -> int | None:
    """Address of the literal a PC-relative load reads, or None.

    ARM: PC is instruction + 8. Thumb: PC is (instruction + 4) rounded down to a
    word boundary. Capstone reports the raw displacement in `op_str`, so it is
    parsed here rather than relying on detail-mode operand types. `[pc]` with no
    displacement (the commonest veneer form) means displacement zero.
    """
    if "[pc" not in ins.op_str:
        return None
    tail = ins.op_str.split("[pc", 1)[1]
    if not tail.startswith(","):
        # `[pc]` or `[pc]!` - no displacement field at all.
        disp = 0
    else:
        try:
            disp = int(tail.split("#", 1)[1].split("]")[0].strip(), 0)
        except (IndexError, ValueError):
            return None
    if isa == "arm":
        return ins.address + 8 + disp
    return ((ins.address + 4) & ~3) + disp


def decode_run(data: bytes, offset: int, isa: str, limit: int = 0x1000) -> DecodeRun:
    """Sequentially decode from `offset` until the stream stops being plausible.

    For Thumb this stops at the first encoding capstone rejects; for ARM it stops
    at the first NV-condition or undefined word. Those two rules are what make the
    metric comparable across instruction sets.
    """
    md = _MD[isa]
    align = ALIGNMENT[isa]
    start = offset - (offset % align)
    end = min(len(data), start + limit)
    bytes_ok = 0
    instructions = 0
    in_range = 0
    local = 0
    pcrel = 0
    targets: list[int] = []
    literals: list[int] = []

    for ins in md.disasm(data[start:end], gba.to_address(start)):
        if isa == "arm":
            word = int.from_bytes(ins.bytes, "little")
            if not _is_plausible_arm(ins, word):
                break
        if ins.mnemonic in ("b", "bl", "blx") and ins.operands:
            operand = ins.operands[0]
            if operand.type == capstone.arm.ARM_OP_IMM:
                targets.append(operand.imm & 0xFFFFFFFF)
                if gba.in_cartridge(operand.imm):
                    in_range += 1
                    if abs((operand.imm & ~1) - gba.to_address(start)) < 0x20000:
                        local += 1
        slot = _literal_slot(ins, isa)
        if slot is not None and ins.mnemonic.startswith("ldr"):
            literals.append(slot)
            pcrel += 1
        bytes_ok += ins.size
        instructions += 1
    return DecodeRun(
        isa=isa,
        offset=start,
        bytes_ok=bytes_ok,
        instructions=instructions,
        in_range_branches=in_range,
        local_branches=local,
        pc_relative_loads=pcrel,
        branch_targets=targets,
        literal_targets=literals,
    )


def max_literal_target(run: DecodeRun) -> int | None:
    """Highest literal-pool address a run actually loads from."""
    return max(run.literal_targets) if run.literal_targets else None


# ---------------------------------------------------------------------------
# pointer helpers
# ---------------------------------------------------------------------------
def words(data: bytes) -> np.ndarray:
    """Aligned little-endian u32 view of the whole image."""
    return np.frombuffer(data, dtype="<u4").astype(np.uint32)


def find_word_references(data: bytes, value: int, *, limit: int = 64) -> list[int]:
    """File offsets of aligned u32 words equal to `value`."""
    view = words(data)
    hits = np.flatnonzero(view == np.uint32(value & 0xFFFFFFFF))
    return [int(i) * 4 for i in hits[:limit]]


def find_references_in_range(data: bytes, start_addr: int, end_addr: int, *, limit: int = 256) -> list[int]:
    """File offsets of aligned u32 words that point into [start_addr, end_addr)."""
    view = words(data)
    mask = (view >= np.uint32(start_addr)) & (view < np.uint32(end_addr))
    return [int(i) * 4 for i in np.flatnonzero(mask)[:limit]]


def pointer_census(data: bytes) -> dict:
    """Classify every aligned u32 in the image by the GBA space it lands in."""
    view = words(data)
    total = int(view.size)
    by_space: dict[str, int] = {}
    for name, first, last, _width in gba.ADDRESS_SPACES:
        count = int(np.count_nonzero((view >= np.uint32(first)) & (view <= np.uint32(last))))
        if count:
            by_space[name] = count
    in_cartridge = int(
        np.count_nonzero((view >= np.uint32(gba.ROM_BASE)) & (view < np.uint32(gba.ROM_END)))
    )
    ram_words = int(
        np.count_nonzero((view >= np.uint32(0x02000000)) & (view < np.uint32(0x03008000)))
    )
    return {
        "aligned_words": total,
        "rom_words": in_cartridge,
        "rom_word_share": round(in_cartridge / total, 6) if total else 0.0,
        "ewram_or_iwram_words": ram_words,
        "by_space": dict(sorted(by_space.items())),
    }


# ---------------------------------------------------------------------------
# constant fills
# ---------------------------------------------------------------------------
def find_constant_runs(data: bytes, value: int, min_run: int = PADDING_MIN_RUN) -> list[tuple[int, int]]:
    """Maximal runs of one byte value, as [start, end) file ranges."""
    arr = np.frombuffer(data, dtype=np.uint8)
    match = arr == np.uint8(value)
    if not match.any():
        return []
    # Boundaries where the run state changes.
    padded = np.concatenate(([False], match, [False]))
    edges = np.flatnonzero(padded[1:] != padded[:-1])
    runs = [(int(edges[i]), int(edges[i + 1])) for i in range(0, len(edges), 2)]
    return [(s, e) for s, e in runs if e - s >= min_run]


# ---------------------------------------------------------------------------
# compressed streams
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class CompressedStream:
    offset: int
    declared_size: int
    header: bytes


def find_webfoot_compressed_streams(data: bytes) -> list[CompressedStream]:
    """Locate `01 00 00 00 <u32 decompressed size>` stream headers.

    This four-byte prologue is what this engine's compressor writes (see the
    baseline's asset reproduction, which regenerates four of these streams byte
    for byte from their source art). The signature alone is not treated as proof:
    a stream is only promoted to a region when the range it occupies is bounded by
    an independent anchor, and the four known ones are additionally reproduced.
    """
    arr = np.frombuffer(data, dtype=np.uint8)
    if arr.size < 8:
        return []
    sig = (arr[:-7] == 1) & (arr[1:-6] == 0) & (arr[2:-5] == 0) & (arr[3:-4] == 0)
    candidates = np.flatnonzero(sig)
    out: list[CompressedStream] = []
    for index in candidates:
        offset = int(index)
        size = int(np.frombuffer(data[offset + 4 : offset + 8], dtype="<u4")[0])
        if 1024 <= size <= 0x400000:
            out.append(CompressedStream(offset, size, data[offset : offset + 8]))
    return out


# ---------------------------------------------------------------------------
# text pools and their pointer tables
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class TextPoolProof:
    table_start: int
    table_end: int
    pool_start: int
    pool_end: int
    pointers: list[int]
    strings: int

    @property
    def tiled_exactly(self) -> bool:
        return self.pool_end > self.pool_start and self.strings > 0


def prove_text_pool(data: bytes, table_start: int, *, max_entries: int = 20000) -> TextPoolProof | None:
    """Try to prove that `table_start` begins a pointer table over a text pool.

    The proof is exhaustive tiling: every pointer is strictly ascending, every
    pointer lands on a UTF-16LE string start, and each string's NUL terminator
    falls exactly where the next string begins. Nothing weaker is accepted.
    """
    view = words(data)
    start_index = table_start // 4
    if start_index >= view.size:
        return None
    pointers: list[int] = []
    previous = -1
    index = start_index
    while index < view.size and len(pointers) < max_entries:
        value = int(view[index])
        if not gba.in_cartridge(value):
            break
        if value <= previous:
            break
        pointers.append(value)
        previous = value
        index += 1
    if len(pointers) < 64:
        return None

    pool_start = pointers[0]
    # Every pointer must resolve to a UTF-16LE string, and the strings must tile
    # the pool with no gap and no overlap.
    cursor = pool_start
    strings = 0
    for pointer in pointers:
        if pointer != cursor:
            return None
        offset = gba.to_offset(pointer)
        end = offset
        while end + 1 < len(data):
            if data[end] == 0 and data[end + 1] == 0:
                break
            if data[end + 1] != 0:
                return None  # not UTF-16LE Latin text
            end += 2
        else:
            return None
        if end == offset and strings > 0:
            pass
        cursor = end + 2
        strings += 1

    return TextPoolProof(
        table_start=table_start,
        table_end=table_start + 4 * len(pointers),
        pool_start=pool_start,
        pool_end=cursor,
        pointers=pointers,
        strings=strings,
    )


def discover_text_pools(data: bytes, *, min_entries: int = 500) -> list[TextPoolProof]:
    """Find every offset that begins a pointer table over an exhaustively tiled pool.

    Vectorised: candidate table starts are offsets where a long strictly-ascending
    run of ROM pointers begins, which is a cheap necessary condition.
    """
    view = words(data)
    n = int(view.size)
    if n < min_entries + 2:
        return []
    in_rom = (view >= np.uint32(gba.ROM_BASE)) & (view < np.uint32(gba.ROM_END))
    ascending = np.zeros(n, dtype=bool)
    ascending[1:] = view[1:] > view[:-1]
    good = in_rom & ascending
    # A candidate run start is a good word preceded by a non-good word.
    starts = np.flatnonzero(good & np.concatenate(([True], ~good[:-1])))
    proofs: list[TextPoolProof] = []
    for index in starts:
        # Cheap pre-check: walk the run length without building anything.
        run = 0
        j = int(index)
        while j < n and good[j]:
            run += 1
            j += 1
            if run >= min_entries:
                break
        if run < min_entries:
            continue
        proof = prove_text_pool(data, int(index) * 4)
        if proof is not None:
            proofs.append(proof)
    return proofs


# ---------------------------------------------------------------------------
# reset path
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class ResetPath:
    header: gba.GbaHeader
    entry_address: int
    entry_isa: str
    entry_offset: int
    startup_end: int
    handoff_address: int
    handoff_offset: int
    handoff_isa: str
    return_address: int
    library_entry: int
    game_entry: int
    literal_min: int
    literal_max: int
    dma_setups: list[dict]
    evidence: list[str]


def trace_reset(data: bytes) -> ResetPath:
    """Decode the header and follow the reset path as far as static evidence goes."""
    evidence: list[str] = []
    header = gba.decode_header(data)
    evidence.append(
        f"header decodes: title={header.title!r} game_code={header.game_code!r} "
        f"checksum=0x{header.header_checksum:02X} "
        f"({'valid' if header.checksum_ok else 'INVALID'})"
    )
    evidence.append(
        f"boot logo at 0x004..0x0A0 is {'the standard GBA constant' if header.logo_is_standard else 'NOT the standard constant'}"
    )

    entry_offset = 0x0000C0
    entry_isa = "arm"
    first = next(MD_ARM.disasm(header.entry_branch, gba.ROM_BASE), None)
    if first is not None and first.mnemonic == "b" and first.operands:
        target = first.operands[0].imm & 0xFFFFFFFF
        entry_offset = gba.to_offset(target & ~1)
        entry_isa = "thumb" if target & 1 else "arm"
        evidence.append(
            f"header entry branch 0x{int.from_bytes(header.entry_branch,'little'):08X} "
            f"decodes as `b 0x{target:08X}` -> entry at 0x{target & ~1:08X} ({entry_isa.upper()})"
        )

    # Decode the startup code, stopping at its tail branch. That is where the
    # literal pool begins, and the pool's own extent is then read off the
    # displacements the code actually uses. Both boundaries come from the ROM.
    startup_insns: list[capstone.CsInsn] = []
    code_end = entry_offset
    for ins in MD_ARM.disasm(data[entry_offset : entry_offset + 0x800], gba.to_address(entry_offset)):
        word = int.from_bytes(ins.bytes, "little")
        if not _is_plausible_arm(ins, word):
            break
        startup_insns.append(ins)
        code_end = (ins.address + ins.size) - gba.ROM_BASE
        if ins.mnemonic == "b":
            break
    literals = [
        slot - gba.ROM_BASE
        for ins in startup_insns
        for slot in [_literal_slot(ins, "arm")]
        if slot is not None and gba.in_cartridge(slot)
    ]
    literal_min = min(literals) if literals else code_end
    literal_max = (max(literals) + 4) if literals else code_end
    evidence.append(
        f"startup decodes as {len(startup_insns)} ARM instructions "
        f"(file 0x{entry_offset:06X}..0x{code_end:06X}), ending at its tail branch"
    )
    evidence.append(
        f"its literal pool is referenced from file 0x{literal_min:06X} to 0x{literal_max:06X} "
        f"({len(literals)} PC-relative loads), so the startup region ends at 0x{literal_max:06X}"
    )
    startup_end = literal_max

    # DMA setups: stores to the DMA3 registers while r0 holds 0x04000000. Recorded
    # as register-level facts; what the transfers accomplish is not claimed.
    dma_setups: list[dict] = []
    for ins in startup_insns:
        if ins.mnemonic in ("str", "strne") and "[r0, #0xd" in ins.op_str:
            dma_setups.append({"at": f"0x{ins.address:08X}", "op": ins.op_str})

    handoff = None
    for ins in startup_insns:
        if ins.mnemonic == "b" and ins.operands and ins.operands[0].type == capstone.arm.ARM_OP_IMM:
            handoff = ins
            break
    handoff_address = 0
    handoff_offset = 0
    handoff_isa = "arm"
    if handoff is not None:
        handoff_address = handoff.operands[0].imm & 0xFFFFFFFF
        handoff_offset = gba.to_offset(handoff_address)
        evidence.append(f"startup tail branch at 0x{handoff.address:08X} -> 0x{handoff_address:08X}")

    # The veneer at the handoff destination loads a code pointer and BXes it.
    library_entry = 0
    if handoff is not None:
        for ins in MD_ARM.disasm(
            data[handoff_offset : handoff_offset + 16], gba.to_address(handoff_offset)
        ):
            slot = _literal_slot(ins, "arm")
            if ins.mnemonic == "ldr" and slot is not None and gba.in_cartridge(slot):
                literal_offset = gba.to_offset(slot)
                value = int.from_bytes(data[literal_offset : literal_offset + 4], "little")
                library_entry = value & ~1
                evidence.append(
                    f"handoff veneer at 0x{handoff_address:08X} loads 0x{value:08X} from "
                    f"file 0x{literal_offset:06X} and BXes it -> library entry "
                    f"0x{library_entry:08X} ({'THUMB' if value & 1 else 'ARM'})"
                )
                break

    # lr is set from the literal pool before the tail branch: that is the return
    # address, i.e. where the C runtime hands control back to the game.
    return_address = 0
    for ins in startup_insns:
        slot = _literal_slot(ins, "arm")
        if ins.mnemonic == "ldr" and ins.op_str.startswith("lr") and slot is not None:
            literal_offset = gba.to_offset(slot)
            return_address = int.from_bytes(data[literal_offset : literal_offset + 4], "little")
            evidence.append(
                f"startup sets lr from file 0x{literal_offset:06X} to 0x{return_address:08X} "
                "before the tail branch, so the C runtime returns there"
            )
            break

    game_entry = return_address & ~1
    return ResetPath(
        header=header,
        entry_address=gba.to_address(entry_offset),
        entry_isa=entry_isa,
        entry_offset=entry_offset,
        startup_end=startup_end,
        handoff_address=handoff_address,
        handoff_offset=handoff_offset,
        handoff_isa="thumb",
        return_address=return_address,
        library_entry=library_entry,
        game_entry=game_entry,
        literal_min=literal_min,
        literal_max=literal_max,
        dma_setups=dma_setups,
        evidence=evidence,
    )


# ---------------------------------------------------------------------------
# windowed classification
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class WindowVerdict:
    start: int
    end: int
    classification: str
    confidence: str
    isa: str | None
    executable: str
    evidence: list[str]

    @property
    def key(self) -> tuple:
        return (self.classification, self.confidence, self.isa, self.executable)


def _entropy(segment: bytes) -> float:
    if not segment:
        return 0.0
    counts = np.bincount(np.frombuffer(segment, dtype=np.uint8), minlength=256).astype(float)
    probabilities = counts[counts > 0] / len(segment)
    return float(-(probabilities * np.log2(probabilities)).sum())


def classify_window(data: bytes, start: int, end: int) -> WindowVerdict:
    """Classify one window using arms that were calibrated against known anchors."""
    span = end - start
    segment = data[start:end]
    evidence: list[str] = []
    if span <= 0:
        return WindowVerdict(start, end, "unknown", "unknown", None, "unknown", ["empty window"])

    # Constant fill.
    for value, name in ((0xFF, "0xFF"), (0x00, "0x00")):
        share = segment.count(value) / span
        if share >= 0.98:
            return WindowVerdict(
                start, end, "padding", "proven", None, "none",
                [f"{share:.1%} of the window is {name}"],
            )

    arm = decode_run(data, start, "arm", limit=span)
    thumb = decode_run(data, start, "thumb", limit=span)
    entropy = _entropy(segment)
    view = np.frombuffer(segment[: len(segment) // 4 * 4], dtype="<u4")
    ptr_rom = float(np.count_nonzero((view >= np.uint32(gba.ROM_BASE)) & (view < np.uint32(gba.ROM_END)))) / max(1, view.size)

    arm_cover = arm.bytes_ok / span
    thumb_cover = thumb.bytes_ok / span
    evidence.append(
        f"sequential decode: ARM {arm.bytes_ok}/{span} B ({arm.in_range_branches} in-range branches), "
        f"Thumb {thumb.bytes_ok}/{span} B ({thumb.in_range_branches} in-range branches)"
    )
    evidence.append(f"entropy {entropy:.2f} bits/byte; ROM-pointer density {ptr_rom:.3f}")

    def code_verdict(run: DecodeRun, cover: float) -> WindowVerdict | None:
        # A stream is code only if it decodes for most of the window AND its
        # branches land inside itself. Decode coverage alone is not enough: this
        # engine's Thumb data decodes at roughly 94%, so a UTF-16LE text pool or
        # a pointer table passes a coverage test outright.
        #
        # Confidence is capped at `medium` ON PURPOSE. A heuristic that cannot
        # separate code from data on this cartridge must never claim `high`;
        # `high` is reserved for recursive reachability, which is evidence.
        if cover < 0.60:
            return None
        if run.local_branches >= 3:
            confidence, executable = "medium", "probable"
        elif run.local_branches >= 1 and run.pc_relative_loads >= 2:
            confidence, executable = "medium", "probable"
        elif run.local_branches >= 1:
            confidence, executable = "low", "possible"
        else:
            return None
        return WindowVerdict(
            start, end, "code", confidence, run.isa, executable,
            list(evidence)
            + [
                f"{run.isa.upper()} decodes {run.instructions} instructions over "
                f"{run.bytes_ok} B ({cover:.0%} of the window) with "
                f"{run.local_branches} branch(es) landing within 128 KiB and "
                f"{run.pc_relative_loads} literal-pool load(s)",
                "classified as code by pattern only; not confirmed by reachability",
            ],
        )

    arm_verdict = code_verdict(arm, arm_cover)
    thumb_verdict = code_verdict(thumb, thumb_cover)
    # Prefer the stronger verdict; on a tie prefer Thumb, which this engine uses
    # far more (measured: the known-Thumb anchors outnumber the known-ARM ones).
    candidates = [v for v in (thumb_verdict, arm_verdict) if v is not None]
    if candidates:
        order = {"high": 0, "medium": 1, "low": 2}
        candidates.sort(key=lambda v: (order[v.confidence], 0 if v.isa == "thumb" else 1))
        best = candidates[0]
        if len(candidates) > 1 and candidates[0].isa != candidates[1].isa:
            best.evidence.append(
                "both instruction sets decode plausibly; Thumb preferred on the tie"
            )
        return best

    if ptr_rom >= 0.15:
        return WindowVerdict(
            start, end, "pointer_table", "medium", None, "possible",
            list(evidence) + [f"{ptr_rom:.0%} of aligned words are in-range ROM addresses"],
        )
    if entropy >= 7.2:
        return WindowVerdict(
            start, end, "unknown", "low", None, "unknown",
            list(evidence) + ["high entropy with no structural signal: likely compressed or packed data"],
        )

    return WindowVerdict(
        start, end, "unknown", "unknown", None, "unknown",
        list(evidence) + ["no classification arm fired; byte-accounted as unknown"],
    )


def classify_range(data: bytes, start: int, end: int, window: int = DEFAULT_WINDOW) -> list[WindowVerdict]:
    """Classify [start, end) window by window, merging neighbours with one verdict."""
    verdicts: list[WindowVerdict] = []
    cursor = start
    while cursor < end:
        stop = min(cursor + window, end)
        verdicts.append(classify_window(data, cursor, stop))
        cursor = stop

    merged: list[WindowVerdict] = []
    for verdict in verdicts:
        if merged and merged[-1].key == verdict.key and merged[-1].end == verdict.start:
            previous = merged[-1]
            merged[-1] = WindowVerdict(
                previous.start, verdict.end, previous.classification, previous.confidence,
                previous.isa, previous.executable,
                previous.evidence[:2] + verdict.evidence[2:] if len(previous.evidence) > 2 else previous.evidence,
            )
        else:
            merged.append(verdict)
    return merged


# ---------------------------------------------------------------------------
# function discovery
# ---------------------------------------------------------------------------
#: Function entry points named by the LOG1-REMAKE corpus, used ONLY as seeds for
#: this project's own traversal. Each is validated here by disassembling from it;
#: nothing is accepted because the corpus says so. `isa=None` means "try Thumb
#: first, then ARM, and keep whichever decodes" - this engine is overwhelmingly
#: Thumb, but the C runtime and the reset path are ARM.
#:
#: Provenance strings name the external document the address came from, so a
#: later reader can tell external hints from this project's own derivations.
EXTERNAL_CODE_SEEDS: tuple[tuple[int, str | None, str], ...] = (
    (0x080000C0, "arm", "cartridge header entry (derived here, not external)"),
    (0x08000158, None, "LOG1-REMAKE reverse-engineering.md:807 sprite-id resolver"),
    (0x080001C6, None, "LOG1-REMAKE BUU_SCRIPT_VM.md:203 actor transform"),
    (0x080007B7, None, "LOG1-REMAKE BUU_SCRIPT_VM.md:143 native slot 27 target"),
    (0x080013F4, None, "LOG1-REMAKE BUU_SCRIPT_VM.md:194 native handler"),
    (0x08002703, None, "LOG1-REMAKE BUU_DIALOG_RUNTIME.md:303 slot 139 handler"),
    (0x08003030, None, "LOG1-REMAKE BUU_DIALOG_RUNTIME.md:119 slot 178 handler"),
    (0x080030F8, None, "LOG1-REMAKE BUU_MAP_EVENT_REFERENCES.md:58 slot 182 handler"),
    (0x0800327E, None, "LOG1-REMAKE BUU_EVENT_RESOURCE.md:87 slot 216 handler"),
    (0x08004038, None, "LOG1-REMAKE BUU_SCRIPT_VM.md:31 script bytecode interpreter loop"),
    (0x08004098, None, "LOG1-REMAKE BUU_SHOP_SCENARIO_MODEL.md:184 dialog entry point"),
    (0x0800421E, None, "LOG1-REMAKE BUU_MAP_SCRIPT_OWNERSHIP.md:86 placement trampoline"),
    (0x08004380, None, "LOG1-REMAKE BUU_MAP_EVENT_REFERENCES.md:84 save-flag set"),
    (0x08004396, None, "LOG1-REMAKE BUU_MAP_EVENT_REFERENCES.md:96 save-flag clear"),
    (0x080046A0, None, "LOG1-REMAKE COLLISION_FORMAT.md:52 gcc indirect-call thunk run"),
    (0x080046AEC, "thumb", "reset path: code pointer the C runtime veneer BXes"),
    (0x08004784, None, "LOG1-REMAKE BUU_PLACEMENT_RUN_RELOCATION.md:108 predicate evaluator"),
    (0x080072CC, None, "LOG1-REMAKE SUBSYSTEM_MAP.md:110 second registry factory"),
    (0x08007674, None, "LOG1-REMAKE PROJECT_STATE.md:112 rectangle-aware object factory"),
    (0x08007A40, None, "LOG1-REMAKE reverse-engineering.md:307 absent-layer allocator"),
    (0x08007B78, None, "LOG1-REMAKE reverse-engineering.md:307 layer constructor"),
    (0x08008086, None, "LOG1-REMAKE reverse-engineering.md:545 dominant layer constructor"),
    (0x080088BC, None, "LOG1-REMAKE ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md:53 handler entry"),
    (0x080089CC, None, "LOG1-REMAKE SUBSYSTEM_MAP.md:13 indexed variation-word resolver"),
    (0x080089FC, None, "LOG1-REMAKE BUU_PLACEMENT_RUN_RELOCATION.md:91 MapEntry lookup"),
    (0x08008B30, None, "LOG1-REMAKE BUU_PLACEMENT_RUN_RELOCATION.md:86 map loader"),
    (0x0800924C, None, "LOG1-REMAKE reverse-engineering.md:625 map driver"),
    (0x0800938C, None, "LOG1-REMAKE reverse-engineering.md:307 background programmer"),
    (0x080094F0, None, "LOG1-REMAKE map_resize.py:39 camera clamp"),
    (0x0800953E, None, "LOG1-REMAKE reverse-engineering.md:373 variation-word consumer"),
    (0x08009670, None, "LOG1-REMAKE SUBSYSTEM_MAP.md:30 population adapter"),
    (0x08009BD4, None, "LOG1-REMAKE ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md:236 chunk loader"),
    (0x0800A93C, None, "LOG1-REMAKE BUU_MAP_SCRIPT_OWNERSHIP.md:50 cursor allocator"),
    (0x0800F68C, None, "LOG1-REMAKE ENTITY_FORMAT.md:132 placement-type constructor"),
    (0x0800FA50, None, "LOG1-REMAKE PROJECT_STATE.md:176 HP writer"),
    (0x0800FD54, None, "LOG1-REMAKE BUU_PLACEMENT_RUN_RELOCATION.md:157 placement factory"),
    (0x080111A8, None, "LOG1-REMAKE BUU_PLACEMENT_RUN_RELOCATION.md:183 sibling factory"),
    (0x08011F20, None, "LOG1-REMAKE reverse-engineering.md:822 portrait accessor"),
    (0x08012230, None, "LOG1-REMAKE BUU_SHOP_SCENARIO_MODEL.md:245 packed-handle consumer"),
    (0x080122B4, None, "LOG1-REMAKE BUU_SHOP_SCENARIO_MODEL.md:245 second handle consumer"),
    (0x080124F8, None, "LOG1-REMAKE BUU_DIALOG_RUNTIME.md:448 dialog dispatcher"),
    (0x08012588, None, "LOG1-REMAKE BUU_EVENT_RESOURCE.md:82 generic constructor"),
    (0x080125E0, None, "LOG1-REMAKE ROM_CAPACITY_AND_ALLOCATION.md:369 count constant"),
    (0x08012664, None, "LOG1-REMAKE SUBSYSTEM_MAP.md:31 registry populate"),
    (0x080126D4, None, "LOG1-REMAKE SUBSYSTEM_MAP.md:35 point query"),
    (0x080141EE, None, "LOG1-REMAKE BUU_SCRIPT_VM.md:97 static40 table walker"),
    (0x0801E164, None, "LOG1-REMAKE BUU_SCRIPT_OWNERSHIP.md:91 static-record script owner"),
    (0x08024F3C, None, "LOG1-REMAKE reverse-engineering.md:756 appearance-record walk"),
    (0x08027948, None, "LOG1-REMAKE reverse-engineering.md:835 appearance lookup"),
    (0x0802BFBC, None, "LOG1-REMAKE BUU_DIALOG_RUNTIME.md:141 text fetch"),
    (0x0803D4D0, "thumb", "region anchor: small-block allocator (proven by this ticket)"),
    (0x0803D5B8, "thumb", "region anchor: allocator sub-run"),
    (0x0803D940, None, "LOG1-REMAKE reverse-engineering.md:658 container wrapper dispatcher"),
    (0x0803DF14, None, "LOG1-REMAKE BUU_SHOP_SCENARIO_MODEL.md:200 assertion helper"),
    (0x08049114, "arm", "reset path tail branch target (derived here)"),
    (0x08049120, "thumb", "LOG1-REMAKE LOGX_CODEC_PROVENANCE.md:200 packed-decoder veneer"),
    (0x087B79A4, "arm", "reset path DMA3 source (derived here)"),
    (0x087B79E4, "arm", "LOG1-REMAKE reverse-engineering.md:689 packed decoder entry"),
)


@dataclasses.dataclass
class ReachabilityResult:
    """Per-byte instruction-set map produced by following control flow."""

    #: 0 = not reached, 1 = ARM, 2 = Thumb
    marks: bytearray
    entries: dict[int, str]
    instructions: int
    visited_addresses: int


def reachable_code(
    data: bytes,
    seeds: list[tuple[int, str | None, str]],
    *,
    max_instructions: int = 400_000,
    run_limit: int = 0x4000,
) -> ReachabilityResult:
    """Follow control flow from the seeds and mark every byte that decodes as code.

    This is the primary code-identification method: a byte is code if it is
    REACHABLE from a known entry point and decodes cleanly in the instruction set
    the traversal chose. That is a much stronger claim than a windowed heuristic,
    and it is a lower bound - unreached code stays unmarked rather than being
    guessed at.

    Literal pools are not marked as code; they are data the code reads, and the
    loader already reports them separately.

    Returns a byte-per-byte map plus the set of entry points actually reached.
    """
    from collections import deque

    marks = bytearray(len(data))
    entries: dict[int, str] = {}
    queue: deque[tuple[int, str]] = deque()
    processed: set[tuple[int, str]] = set()
    count = 0

    def enqueue(address: int, isa: str | None) -> None:
        if not gba.in_cartridge(address):
            return
        base = address & ~1
        if isa is None:
            # Pick the instruction set that decodes best from this address.
            arm = decode_run(data, base - gba.ROM_BASE, "arm", limit=64)
            thumb = decode_run(data, base - gba.ROM_BASE, "thumb", limit=64)
            chosen = "thumb" if thumb.instructions >= arm.instructions else "arm"
        else:
            chosen = isa
        queue.append((base, chosen))

    for address, isa, _why in seeds:
        enqueue(address, isa)

    while queue and count < max_instructions:
        address, isa = queue.popleft()
        offset = address - gba.ROM_BASE
        if not 0 <= offset < len(data):
            continue
        # Skip only if this exact (address, isa) was already EXPANDED. Using the
        # byte marks here instead would silently drop the branch edges of any
        # function that another run had already decoded through.
        key = (address, isa)
        if key in processed:
            continue
        processed.add(key)

        md = _MD[isa]
        align = ALIGNMENT[isa]
        run_start = offset - (offset % align)
        for ins in md.disasm(data[run_start : run_start + run_limit], gba.to_address(run_start)):
            if isa == "arm":
                word = int.from_bytes(ins.bytes, "little")
                if not _is_plausible_arm(ins, word):
                    break
            start = ins.address - gba.ROM_BASE
            for i in range(start, start + ins.size):
                if 0 <= i < len(marks):
                    marks[i] = 1 if isa == "arm" else 2
            count += 1
            entries.setdefault(ins.address, isa)

            if ins.mnemonic in ("b", "bl", "blx") and ins.operands:
                operand = ins.operands[0]
                if operand.type == capstone.arm.ARM_OP_IMM:
                    target = operand.imm & 0xFFFFFFFF
                    if ins.mnemonic == "b":
                        enqueue(target, isa)
                    else:
                        enqueue(target, "thumb" if (target & 1) or isa == "thumb" else "arm")
            if ins.mnemonic == "bx" and ins.operands:
                operand = ins.operands[0]
                if operand.type == capstone.arm.ARM_OP_REG and operand.reg == capstone.arm.ARM_REG_LR:
                    break
            if ins.mnemonic in ("pop", "ldm", "ldmia", "ldmfd") and "pc" in ins.op_str:
                break
            if ins.mnemonic.startswith("ldr") and ins.op_str.startswith("pc"):
                break
            if (
                ins.mnemonic == "b"
                and ins.operands
                and ins.operands[0].type == capstone.arm.ARM_OP_IMM
            ):
                # Unconditional branch: the next word is not on this path.
                break
            if count >= max_instructions:
                break

    return ReachabilityResult(
        marks=marks,
        entries=entries,
        instructions=count,
        visited_addresses=len(entries),
    )


@dataclasses.dataclass
class DiscoveryResult:
    functions: dict[int, rm.Function]
    code_regions: list[tuple[int, int, str]]


def _code_regions(rom_map: rm.RomMap) -> list[tuple[int, int, str]]:
    out = []
    for region in rom_map.regions:
        if region.classification in ("code", "code_candidate") and region.isa in ("arm", "thumb"):
            out.append((region.start, region.end, region.isa))
    return out


def discover_functions(
    data: bytes,
    rom_map: rm.RomMap,
    seeds: list[tuple[int, str, str]],
    *,
    rounds: int = 3,
) -> DiscoveryResult:
    """Harvest candidate function entry points from the identified code.

    Seeds are (address, isa, why). Each round linearly sweeps every code region in
    its own instruction set, collecting BL/BX targets and literal-pool words that
    point at code, then validates each new candidate by disassembling from it. The
    loop runs to a fixpoint, bounded by `rounds`.

    A candidate is accepted at `high` confidence when it is a direct branch target
    from validated code; a literal-pool value ending in an odd halfword is accepted
    at `medium`, because the low bit is a strong but not infallible Thumb marker.
    """
    functions: dict[int, rm.Function] = {}
    for address, isa, why in seeds:
        functions[address & ~1] = rm.Function(
            address=address & ~1,
            isa=isa,
            confidence="proven",
            discovery=[why],
        )

    regions = _code_regions(rom_map)
    if not regions:
        return DiscoveryResult(functions, regions)

    for _round in range(rounds):
        added = 0
        for start, end, isa in regions:
            md = _MD[isa]
            align = ALIGNMENT[isa]
            base = start - (start % align)
            for ins in md.disasm(data[base:end], gba.to_address(base)):
                if isa == "arm":
                    word = int.from_bytes(ins.bytes, "little")
                    if not _is_plausible_arm(ins, word):
                        break
                target = None
                if ins.mnemonic in ("bl", "blx") and ins.operands:
                    operand = ins.operands[0]
                    if operand.type == capstone.arm.ARM_OP_IMM:
                        target = operand.imm & 0xFFFFFFFF
                if target is None or not gba.in_cartridge(target):
                    continue
                callee = target & ~1
                # The callee's instruction set follows the CALLER's, not the
                # target's low bit: a Thumb BL target is even, exactly like an
                # ARM one. Only BLX switches state. Getting this wrong labels
                # every Thumb callee as ARM.
                if ins.mnemonic == "blx":
                    callee_isa = "arm" if isa == "thumb" else "thumb"
                else:
                    callee_isa = isa
                callers = functions.setdefault(
                    callee,
                    rm.Function(
                        address=callee,
                        isa=callee_isa,
                        confidence="medium",
                        discovery=[f"{ins.mnemonic.upper()} target from 0x{ins.address:08X} ({isa})"],
                    ),
                )
                if callers.isa != callee_isa and callers.isa is not None:
                    callers.discovery.append(
                        f"called from both instruction sets: as {callers.isa} elsewhere, "
                        f"as {callee_isa} from 0x{ins.address:08X}"
                    )
                if ins.address not in callers.callers:
                    callers.callers.append(ins.address)
                # A BL target is real evidence but not proof that a FUNCTION
                # starts there: this engine is ~94% decodable as Thumb, so a
                # sweep over Thumb-classified bytes can manufacture call sites
                # out of data. Such entries stay at `medium` and are reported as
                # PROBABLE, not confirmed.
                added += 1
        # Literal pools: a word in a code region that points at code is a
        # function pointer if its low bit is set (Thumb) or it is word-aligned
        # and inside a code region (ARM).
        view = words(data)
        for start, end, isa in regions:
            first = start // 4
            last = min(int(view.size), end // 4)
            for index in range(first, last):
                value = int(view[index])
                if not gba.in_cartridge(value):
                    continue
                if value & 1:
                    candidate = value & ~1
                    candidate_isa = "thumb"
                else:
                    candidate = value
                    candidate_isa = "arm"
                if any(s <= candidate < e for s, e, _ in regions):
                    if candidate not in functions:
                        functions[candidate] = rm.Function(
                            address=candidate,
                            isa=candidate_isa,
                            confidence="medium",
                            discovery=[f"literal-pool code pointer at file 0x{index*4:06X}"],
                        )
                        added += 1
        if added == 0:
            break

    # Validate every candidate by disassembling from it; drop the ones that do not
    # decode at all, and record leaf-ness by looking for a call in its own body.
    validated: dict[int, rm.Function] = {}
    for address, function in functions.items():
        offset = address - gba.ROM_BASE
        if not 0 <= offset < len(data):
            continue
        run = decode_run(data, offset, function.isa, limit=0x400)
        if run.instructions == 0:
            continue
        if run.instructions == 1 and function.confidence != "proven":
            continue
        function.size = run.bytes_ok
        callees: list[int] = []
        calls = 0
        for ins in _MD[function.isa].disasm(
            data[offset : offset + run.bytes_ok], gba.to_address(offset)
        ):
            if ins.mnemonic in ("bl", "blx") and ins.operands:
                operand = ins.operands[0]
                if operand.type == capstone.arm.ARM_OP_IMM:
                    callees.append(operand.imm & ~1)
                    calls += 1
        function.callees = sorted(set(callees))
        # A leaf makes no call at all. When the body could not be walked to a
        # terminator the answer is genuinely unknown, so it stays None.
        function.leaf = (calls == 0) if run.bytes_ok else None
        validated[address] = function

    return DiscoveryResult(validated, regions)


# ---------------------------------------------------------------------------
# proven fixed-format regions
# ---------------------------------------------------------------------------
def prove_gbaram_literals(data: bytes, start: int, end: int) -> dict:
    """Prove that [start, end) is the literal pool of the Thumb code before it."""
    loads: list[int] = []
    for base in (0x03D4D0, 0x03D5B8, 0x03D63C):
        run = decode_run(data, base, "thumb", limit=0x200)
        loads.extend(addr for addr in run.literal_targets if gba.in_cartridge(addr))
    inside = sorted({addr - gba.ROM_BASE for addr in loads if start <= addr - gba.ROM_BASE < end})
    return {
        "literal_loads_into_range": inside,
        "covered": sorted({o & ~3 for o in inside}),
    }


def prove_referenced_table(data: bytes, start: int, end: int) -> dict:
    """Find aligned u32 words anywhere in the image that point into [addr, addr_end)."""
    refs = find_references_in_range(data, gba.to_address(start), gba.to_address(end))
    return {"reference_sites": refs, "count": len(refs)}
