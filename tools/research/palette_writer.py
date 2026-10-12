"""Assemble the runtime palette writer as the draw-loop stub's BODY, verified by a disassembler.

Where it runs: in place of the seven instructions at 0x0800F2B2, after the bank-select half of the body,
with r1 = the OAM entry and r7 = the piece's palette index (0..7). It copies that index's 32-byte palette
from the appended table into OBJ palette RAM and into the OAM entry's palette field, then resumes the draw
loop. Index 0 is every retail piece, so it is left completely alone.

Three measured facts this file encodes, each learned from a failed run:

* the write is an INLINE Thumb loop, not a call to the engine's own copy routine at 0x030007FC (veneer
  0x08049144). That routine is real - it copies r2 bytes, 16 at a time, and it is what the engine's own
  palette load calls - but an earlier revision reached it with `blx r7`, the ARMv5T register form, on an
  ARM7TDMI that has only `bx`; the copy never landed (run `build/toolkit031/copy-body-1`). The same call
  would also have to spend `lr` on a return address, and `lr` is LIVE draw-loop state at the resume address
  0x0800F2C0 (the loop does `add lr,r0` there and reads it as the tile cursor). With the loop inline both
  faults are gone: run `build/toolkit031/copy-body-inline-1` shows the test ramp in palette RAM bank 11.
* the OAM palette field is four bits wide, but a piece record only carries three (attr1 bits 9..11), so the
  bank-select half can address banks 0..7 only. The body therefore takes the physical bank from the TABLE
  destination address - `bank = (dest >> 5) & 0xf` - and writes it into OAM word 1 itself, which is what
  makes the five banks measured free in the owner's scene (8, 10, 11, 14, 15) reachable at all.
* the body must carry its OWN literals. An earlier revision kept them outside the body at offsets derived
  from a separate blob, so the block jumped to code that was not the writer at all (`probe-pal-1`).

Layout is computed by accumulating entry sizes; no offset is hand-written. `verify` disassembles the
assembled bytes and asserts each instruction is the intended one (P-083).
"""

from __future__ import annotations

import re
import struct

ROM_BASE = 0x08000000
PALETTE_RAM = 0x05000200
BANK_BYTES = 32
BANK_COUNT = 16
RESUME = 0x0800F2C0
#: One row per index: two words, (destination palette RAM, source palette), read at 8*index.
TABLE_BYTES = BANK_COUNT * 8

#: Branch targets by label, resolved to entries rather than to numbers.
LOOP = "loop"
EXIT = "exit"

#: (kind, halfword, mnemonic, operands, label). `kind` is "word" or "branch"; the two `ldr ...,[pc,#0]`
#: entries get their imm8 patched, and a branch gets its imm8 from its label.
ENTRIES: list[tuple[str, int, str, str, str]] = [
    ("word", 0x2F00, "cmp", "r7,#0", ""),                  # index 0 is every retail piece
    ("branch", 0xD000, "beq", "", EXIT),
    ("word", 0xB43F, "push", "{r0,r1,r2,r3,r4,r5}", ""),    # r0 and r4 are live at RESUME
    ("word", 0x460D, "mov", "r5,r1", ""),                  # the OAM entry, before r1 becomes the source
    ("word", 0x4C00, "ldr", "r4,[pc,#0]", ""),             # the address table
    ("word", 0x00FB, "lsls", "r3,r7,#3", ""),
    ("word", 0x18E4, "adds", "r4,r4,r3", ""),
    ("word", 0x6820, "ldr", "r0,[r4,#0]", ""),             # destination palette RAM
    ("word", 0x6861, "ldr", "r1,[r4,#4]", ""),             # source palette
    ("word", 0x220F, "movs", "r2,#0xf", ""),
    ("word", 0x0943, "lsrs", "r3,r0,#5", ""),
    ("word", 0x401A, "ands", "r2,r3", ""),                 # bank = (dest >> 5) & 0xf
    ("word", 0x0312, "lsls", "r2,r2,#0xc", ""),
    ("word", 0x686B, "ldr", "r3,[r5,#4]", ""),             # OAM word 1
    ("word", 0x24F0, "movs", "r4,#0xf0", ""),
    ("word", 0x0224, "lsls", "r4,r4,#8", ""),              # 0xf000
    ("word", 0x43A3, "bics", "r3,r4", ""),
    ("word", 0x4313, "orrs", "r3,r2", ""),
    ("word", 0x606B, "str", "r3,[r5,#4]", ""),             # a bank above 7 is now reachable
    ("word", 0x2210, "movs", "r2,#0x10", ""),              # 16 halfwords = one bank
    ("word", 0x880B, "ldrh", "r3,[r1]", LOOP),
    ("word", 0x8003, "strh", "r3,[r0]", ""),
    ("word", 0x3102, "adds", "r1,#2", ""),
    ("word", 0x3002, "adds", "r0,#2", ""),
    ("word", 0x3A01, "subs", "r2,#1", ""),
    ("branch", 0xD100, "bne", "", LOOP),
    ("word", 0xBC3F, "pop", "{r0,r1,r2,r3,r4,r5}", ""),
    ("word", 0x4C00, "ldr", "r4,[pc,#0]", ""),             # resume
    ("word", 0x4720, "bx", "r4", ""),
]

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


def assemble(body_address: int, table_address: int) -> bytes:
    """The body bytes for a body placed at `body_address`, reading its table from `table_address`.

    The body is the bank-select stub's own sequence FOLLOWED BY the palette write. That order is required,
    not cosmetic: `oam_bank_patch.patch` installs this body as the whole stub, so if the bank-select half
    were left out, r7 would never hold an index and the write would copy whatever happened to be in it.
    """
    from tools.research import oam_bank_patch

    prefix = oam_bank_patch.STUB
    if len(prefix) % 2:
        raise AssertionError("the bank-select body must be a whole number of halfwords")

    start = len(prefix)
    offsets = {label: start + 2 * index
               for index, (_, _, _, _, label) in enumerate(ENTRIES) if label == LOOP}
    offsets[EXIT] = start + 2 * len(ENTRIES) - 4
    literal_table = (start + 2 * len(ENTRIES) + 3) & ~3
    literal_resume = literal_table + 4
    size = literal_resume + 4

    blob = bytearray(size)
    blob[0:start] = prefix
    for index, (kind, halfword, _, _, label) in enumerate(ENTRIES):
        offset = start + 2 * index
        if kind == "branch":
            halfword = (halfword & 0xFF00) | branch_field(offset, offsets[label])
        struct.pack_into("<H", blob, offset, halfword)
    for index, literal in ((4, literal_table), (len(ENTRIES) - 2, literal_resume)):
        offset = start + 2 * index
        halfword = struct.unpack_from("<H", blob, offset)[0]
        struct.pack_into("<H", blob, offset, (halfword & 0xFF00) | ldr_field(offset, literal))
    struct.pack_into("<I", blob, literal_table, table_address)
    struct.pack_into("<I", blob, literal_resume, RESUME | 1)

    verify(bytes(blob), body_address, prefix_halfwords=len(prefix) // 2)
    got = disassemble(bytes(blob[start:start + len(ENTRIES) * 2]), body_address + start)
    for (kind, _, _, _, label), (at, _, operands) in zip(ENTRIES, got):
        if kind == "branch" and int(operands.split("#")[1], 16) != body_address + offsets[label]:
            raise AssertionError(f"at 0x{at:08X}: branch lands on 0x{int(operands.split('#')[1], 16):08X}, "
                                 f"expected 0x{body_address + offsets[label]:08X} ({label})")
    return bytes(blob)


def normalise(operands: str) -> str:
    """Capstone prints `ldr r3, [r4]` for `ldr r3,[r4,#0]`: compare register/memory form."""
    return re.sub(r"\[(\w+)\]", r"[\1,#0]", operands.replace(" ", "")).lower()


def verify(body: bytes, body_address: int, prefix_halfwords: int = 0) -> list[tuple[int, str, str]]:
    """Disassemble the body's own instructions and assert they are the intended ones.

    `prefix_halfwords` skips a raw prefix (the bank-select sequence, which `oam_bank_patch`'s own test
    covers byte for byte).
    """
    start = prefix_halfwords * 2
    got = disassemble(body[start:start + len(ENTRIES) * 2], body_address + start)
    if len(got) != len(ENTRIES):
        raise AssertionError(f"disassembled {len(got)} instruction(s), expected {len(ENTRIES)}: {got}")
    for (kind, _, want_mnemonic, want_operands, label), (at, mnemonic, operands) in zip(ENTRIES, got):
        if mnemonic != want_mnemonic:
            raise AssertionError(f"at 0x{at:08X}: expected `{want_mnemonic}`, got `{mnemonic} {operands}`")
        if kind == "branch":                        # check where it lands, not how it reads
            if not operands.startswith("#"):
                raise AssertionError(f"at 0x{at:08X}: expected a branch target, got `{operands}`")
            continue
        if want_operands.endswith("[pc,#0]"):
            if "[pc," not in operands:
                raise AssertionError(f"at 0x{at:08X}: expected a PC-relative load, got `{operands}`")
            continue
        if normalise(operands) != normalise(want_operands):
            raise AssertionError(f"at 0x{at:08X}: expected `{want_mnemonic} {want_operands}`, "
                                 f"got `{mnemonic} {operands}`")
    return got


def build_table(table_address: int, rows: dict[int, int] | None = None) -> bytes:
    """The 16-row address table plus 16 zeroed palette blocks, at `table_address` in ROM space.

    Row `index` is `(0x05000200 + 32*bank, table_address + TABLE_BYTES + 32*bank)`, with `bank` taken from
    `rows` and equal to the index otherwise. The body recovers the bank from the destination address, so a
    row may name any of the 16 banks and the piece's three-bit index only has to be distinct and non-zero.
    """
    chosen = {index: index for index in range(BANK_COUNT)}
    if rows:
        chosen.update(rows)
    table = bytearray(TABLE_BYTES + BANK_COUNT * BANK_BYTES)
    for index in range(BANK_COUNT):
        bank = chosen[index]
        struct.pack_into("<II", table, 8 * index,
                         PALETTE_RAM + BANK_BYTES * bank,
                         table_address + TABLE_BYTES + BANK_BYTES * bank)
    return bytes(table)


def fill_palettes(image: bytearray, table_address: int, bank_palettes: dict[int, bytes]) -> None:
    """Write palettes into the table's blocks. A bank absent here keeps its zeroed block."""
    for bank, block in bank_palettes.items():
        if not 0 <= bank < BANK_COUNT:
            raise ValueError(f"bank {bank} is not a 0..{BANK_COUNT - 1} OBJ bank")
        if len(block) != BANK_BYTES:
            raise ValueError(f"bank {bank}: palette is {len(block)} bytes, expected {BANK_BYTES}")
        start = table_address - ROM_BASE + TABLE_BYTES + BANK_BYTES * bank
        image[start:start + BANK_BYTES] = block
