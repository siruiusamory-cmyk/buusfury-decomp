"""The draw-loop half: give a piece the bank its palette index maps to at RUNTIME.

Where it runs: in place of the seven instructions at 0x0800F2B2, appended to the bank-select stub
`oam_bank_patch.STUB`, with r1 = the OAM entry and r7 = the piece's palette index (0..7). Index 0 is every
retail piece, so it is left completely alone: the stub's own work on those pieces is inert (retail sets
attr1 bits 9..11 on 0 of 11,005 pieces, and an 8bpp piece ignores the attr2 bank nibble).

WHERE THE BANK COMES FROM. It is not in the piece: the piece carries three bits, so it cannot name a bank
above 7, and the measured free banks in the owner's map-137 scene were 8, 10, 11, 14 and 15. The ONE-SHOT
write (`tools/research/palette_oneshot.py`) therefore leaves a marker halfword at entry 0 of each bank it
filled, and this body finds that marker:

    marker = MARKER_BASE | index      (index 1..3 for the character's three logical banks)

Entry 0 of a bank is the transparent slot of a 4bpp palette, and the marker's bank is one the one-shot
proved nothing visible was drawing from, so the marker changes no pixel. It is written after the scene's
own 512-byte palette load, which clears every prior marker, so a stale one cannot survive a scene change.

THE CODED FALLBACK. If no bank holds the marker (the one-shot found fewer than three free banks and wrote
nothing), the bank is 0: the piece draws through the shared retail palette. That is the 16-colour mapping
for that moment, and it is a branch in this code, not a note in a document.

The resume address must stay absolute: `lr` is LIVE draw-loop state at 0x0800F2C0, where the loop does
`add lr,r0` and reads it as the tile cursor, and a Thumb `b` cannot reach above EOF. Every literal lives in
this body because an earlier revision kept them outside it and jumped to code that was not the writer at
all. Layout is computed by accumulating entry sizes; no offset is hand-written, and `verify` disassembles
the assembled bytes and asserts each instruction is the intended one (P-083).
"""

from __future__ import annotations

import re
import struct
from typing import NamedTuple

ROM_BASE = 0x08000000
PALETTE_RAM = 0x05000200
BANK_BYTES = 32
BANK_COUNT = 16
RESUME = 0x0800F2C0

#: The marker the one-shot leaves at entry 0 of every bank it filled: MARKER_BASE | logical index (1..3).
MARKER_BASE = 0x4B00

SCAN = "scan"
FOUND = "found"
EXIT = "exit"


class Entry(NamedTuple):
    """One instruction.

    `kind` is "word", "branch" or "ldr" (a PC-relative load of `literal`). `label` names this instruction
    so a branch can reach it; `target` is the label a branch jumps to.
    """

    kind: str
    halfword: int
    mnemonic: str
    operands: str
    target: str = ""
    literal: str = ""
    label: str = ""


#: (kind, halfword, mnemonic, operands, target, literal, label). The `ldr ...,[pc,#0]` entries get their
#: imm8 patched, and a branch gets its imm8 from its target label.
ENTRIES: list[Entry] = [
    Entry("word", 0x2F00, "cmp", "r7,#0"),                      # index 0 is every retail piece
    Entry("branch", 0xD000, "beq", "", EXIT),
    Entry("word", 0xB43F, "push", "{r0,r1,r2,r3,r4,r5}"),       # r0 and r4 are live at RESUME
    Entry("word", 0x460D, "mov", "r5,r1"),                      # the OAM entry, before r1 is reused
    Entry("word", 0x023F, "lsls", "r7,r7,#8"),                  # marker = 0x4B00 | index
    Entry("word", 0x234B, "movs", "r3,#0x4b"),
    Entry("word", 0x021B, "lsls", "r3,r3,#8"),
    Entry("word", 0x431F, "orrs", "r7,r3"),
    Entry("word", 0x4C00, "ldr", "r4,[pc,#0]", "", "palette_ram"),
    Entry("word", 0x2200, "movs", "r2,#0"),                     # bank candidate
    Entry("word", 0x2010, "movs", "r0,#0x10"),                  # 16 banks to try
    Entry("word", 0x8823, "ldrh", "r3,[r4]", "", "", SCAN),
    Entry("word", 0x429F, "cmp", "r7,r3"),
    Entry("branch", 0xD000, "beq", "", FOUND),
    Entry("word", 0x3420, "adds", "r4,#0x20"),                  # next bank's entry 0
    Entry("word", 0x3201, "adds", "r2,#1"),
    Entry("word", 0x3801, "subs", "r0,#1"),
    Entry("branch", 0xD100, "bne", "", SCAN),
    Entry("word", 0x2200, "movs", "r2,#0"),                     # FALLBACK: no marker, so the shared bank
    Entry("word", 0x686B, "ldr", "r3,[r5,#4]", "", "", FOUND),  # OAM word 1
    Entry("word", 0x20F0, "movs", "r0,#0xf0"),
    Entry("word", 0x0200, "lsls", "r0,r0,#8"),                  # 0xf000
    Entry("word", 0x4383, "bics", "r3,r0"),
    Entry("word", 0x0312, "lsls", "r2,r2,#0xc"),                # bank -> attr2 bits 12..15
    Entry("word", 0x4313, "orrs", "r3,r2"),
    Entry("word", 0x606B, "str", "r3,[r5,#4]"),
    Entry("word", 0xBC3F, "pop", "{r0,r1,r2,r3,r4,r5}"),
    Entry("word", 0x4C00, "ldr", "r4,[pc,#0]", "", "resume", EXIT),
    Entry("word", 0x4720, "bx", "r4"),
]

#: The absolute words the body loads. `resume` carries the thumb bit.
LITERALS = {
    "palette_ram": PALETTE_RAM,
    "resume": RESUME | 1,
}

try:
    import capstone

    _CS = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
except Exception as error:  # pragma: no cover - reported, never silently skipped
    _CS = None
    _CS_ERROR = error


def disassemble(code: bytes, address: int) -> list[tuple[int, str, str]]:
    if _CS is None:
        raise RuntimeError(f"capstone is required to verify hand-written opcodes: {_CS_ERROR}")
    return [(ins.address, ins.mnemonic, ins.op_str) for ins in _CS.disasm(code, address)]


def ldr_field(instruction_offset: int, literal_offset: int) -> int:
    """The `imm8*4` field of `ldr rX,[pc,#imm]` reaching `literal_offset` from `instruction_offset`.

    Thumb reads PC as `(instruction_address + 4) & ~3`. Out of range or unaligned is a hard error.
    """
    pc_value = (instruction_offset + 4) & ~3
    gap = literal_offset - pc_value
    if gap < 0 or gap % 4 or gap // 4 > 0xFF:
        raise ValueError(f"literal at {literal_offset:#x} unreachable from {instruction_offset:#x}: "
                         f"pc {pc_value:#x}, gap {gap}")
    return gap // 4


def branch_field(from_offset: int, to_offset: int) -> int:
    """The `imm8` of a Thumb conditional branch from `from_offset` to `to_offset`, both body-relative."""
    gap = to_offset - (from_offset + 4)
    if gap % 2 or not -256 <= gap <= 254:
        raise ValueError(f"branch from {from_offset:#x} to {to_offset:#x} is out of range: {gap}")
    return (gap // 2) & 0xFF


def normalise(operands: str) -> str:
    """Capstone prints `ldr r3, [r4]` for `ldr r3,[r4,#0]`: compare register/memory form."""
    return re.sub(r"\[(\w+)\]", r"[\1,#0]", operands.replace(" ", "")).lower()


def assemble(body_address: int, prefix: bytes | None = None) -> bytes:
    """The body bytes for a body placed at `body_address`.

    The body is the bank-select stub's own sequence FOLLOWED BY the bank lookup. That order is required,
    not cosmetic: `oam_bank_patch.patch` installs this body as the whole stub, and the bank-select half is
    what turns the piece word's bits 25..27 into r7.
    """
    from tools.research import oam_bank_patch

    if prefix is None:
        prefix = oam_bank_patch.STUB
    if len(prefix) % 2:
        raise AssertionError("the bank-select body must be a whole number of halfwords")

    start = len(prefix)
    offsets = {entry.label: start + 2 * index
               for index, entry in enumerate(ENTRIES) if entry.label}
    code_end = start + 2 * len(ENTRIES)
    literal_base = (code_end + 3) & ~3
    places: dict[str, int] = {}
    for entry in ENTRIES:
        if entry.kind == "ldr" and entry.literal not in places:
            places[entry.literal] = literal_base + 4 * len(places)
    unknown = set(places) - set(LITERALS)
    if unknown:
        raise AssertionError(f"body loads literal(s) with no value: {sorted(unknown)}")

    blob = bytearray(literal_base + 4 * len(places))
    blob[0:start] = prefix
    for index, entry in enumerate(ENTRIES):
        offset = start + 2 * index
        halfword = entry.halfword
        if entry.kind == "branch":
            halfword = (halfword & 0xFF00) | branch_field(offset, offsets[entry.target])
        elif entry.kind == "ldr":
            halfword = (halfword & 0xFF00) | ldr_field(offset, places[entry.literal])
        struct.pack_into("<H", blob, offset, halfword)
    for name, offset in places.items():
        struct.pack_into("<I", blob, offset, LITERALS[name])

    verify(bytes(blob), body_address, prefix_halfwords=len(prefix) // 2)
    got = disassemble(bytes(blob[start:start + len(ENTRIES) * 2]), body_address + start)
    for entry, (at, _, operands) in zip(ENTRIES, got):
        if entry.kind == "branch" and int(operands.split("#")[1], 16) != body_address + offsets[entry.target]:
            raise AssertionError(f"at 0x{at:08X}: branch lands on 0x{int(operands.split('#')[1], 16):08X}, "
                                 f"expected 0x{body_address + offsets[entry.target]:08X} ({entry.target})")
    return bytes(blob)


def verify(body: bytes, body_address: int, prefix_halfwords: int = 0) -> list[tuple[int, str, str]]:
    """Disassemble the body's own instructions and assert they are the intended ones.

    `prefix_halfwords` skips a raw prefix (the bank-select sequence, which `oam_bank_patch`'s own test
    covers byte for byte).
    """
    start = prefix_halfwords * 2
    got = disassemble(body[start:start + len(ENTRIES) * 2], body_address + start)
    if len(got) != len(ENTRIES):
        raise AssertionError(f"disassembled {len(got)} instruction(s), expected {len(ENTRIES)}: {got}")
    for entry, (at, mnemonic, operands) in zip(ENTRIES, got):
        if mnemonic != entry.mnemonic:
            raise AssertionError(f"at 0x{at:08X}: expected `{entry.mnemonic}`, got `{mnemonic} {operands}`")
        if entry.kind == "branch":                  # check where it lands, not how it reads
            if not operands.startswith("#"):
                raise AssertionError(f"at 0x{at:08X}: expected a branch target, got `{operands}`")
            continue
        if entry.kind == "ldr":
            if "[pc," not in operands:
                raise AssertionError(f"at 0x{at:08X}: expected a PC-relative load, got `{operands}`")
            continue
        if normalise(operands) != normalise(entry.operands):
            raise AssertionError(f"at 0x{at:08X}: expected `{entry.mnemonic} {entry.operands}`, "
                                 f"got `{mnemonic} {operands}`")
    return got
