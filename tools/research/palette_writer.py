"""Assemble the runtime palette writer as the draw-loop stub's BODY, verified by a disassembler.

Where it runs: in place of the seven instructions at 0x0800F2B2, after the bank-select half of the body,
with r1 = the OAM entry and r7 = the piece's palette bank (0..7). It copies that bank's 32-byte palette
from the appended table into OBJ palette RAM at `0x05000200 + 32*bank`, then resumes the draw loop.

Two measured facts this file encodes, each learned from a failed run:

* the copy routine at 0x08049144 is a THUMB-TO-ARM THUNK (`bx pc` + `ldr pc,[pc,#-4]` -> an IWRAM ARM
  routine). It must be reached with a Thumb `bl`; a `blx` with the even address switches to ARM before
  executing and hangs the engine (`probe` run `cell-runtime-2`, which stopped at frame 2).
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
COPY_THUNK = 0x08049144
RESUME = 0x0800F2C0
TABLE_BYTES = BANK_COUNT * 8
#: The instruction region of the body: the bank-select prefix plus the palette write's halfwords. The
#: prefix (20 halfwords) is `oam_bank_patch.STUB`; the write is 17 halfwords.
INSTRUCTION_BYTES = 40 + 17 * 2

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


def bl_words(from_address: int, target: int) -> bytes:
    """A Thumb `bl` to `target` from the instruction at `from_address`, as two halfwords."""
    offset = target - (from_address + 4)
    if offset % 2 or not -(1 << 22) <= offset < (1 << 22):
        raise ValueError(f"bl from {from_address:#x} to {target:#x} is out of range: {offset}")
    sign = (offset >> 23) & 1
    imm10 = (offset >> 12) & 0x3FF
    imm11 = (offset >> 1) & 0x7FF
    j1 = 1 if (offset >> 22) & 1 else 0
    j2 = 1 if (offset >> 21) & 1 else 0
    high = 0xF000 | (sign << 10) | imm10
    low = 0xF800 | (j1 << 13) | (j2 << 11) | imm11
    return struct.pack("<HH", high, low)


def normalise(operands: str) -> str:
    """Capstone prints `ldr r3, [r4]` for `ldr r3,[r4,#0]`: compare register/memory form."""
    return re.sub(r"\[(\w+)\]", r"[\1,#0]", operands.replace(" ", "")).lower()


def assemble(body_address: int, table_address: int) -> bytes:
    """The body bytes for a body placed at `body_address`, reading its table from `table_address`.

    The body is the bank-select stub's own sequence FOLLOWED BY the palette write. That order is required,
    not cosmetic: `oam_bank_patch.patch` installs this body as the whole stub, so if the bank-select half
    were left out, r7 would never hold a bank and the palette write would copy whatever happened to be in
    it. A run with only the write half showed exactly that (`cell-runtime-2`: no bank changed).
    """
    from tools.research import oam_bank_patch

    entries: list[tuple[str, int, str, str]] = []
    # The bank-select half, byte for byte as the committed stub carries it.
    prefix = oam_bank_patch.STUB
    if len(prefix) % 2:
        raise AssertionError("the bank-select body must be a whole number of halfwords")
    entries.append(("raw", len(prefix), "PRESET", ""))
    entries += [
        ("h", 0x680B, "ldr", "r3,[r1]"),        # re-read OAM word 0: the bank-select half used r3/r7
        ("h", 0x0E5F, "lsrs", "r7,r3,#0x19"),   # attr1 bits 9..11 -> 0..2, the physical bank
        ("h", 0x2507, "movs", "r5,#7"),
        ("h", 0x402F, "ands", "r7,r5"),         # r7 = bank 0..7
        ("h", 0x4800, "ldr", "r0,[pc,#0]"),     # the address table's absolute address
        ("h", 0x00FC, "lsls", "r4,r7,#3"),      # r4 = bank * 8 (two words per bank)
        ("h", 0x1824, "adds", "r4,r4,r0"),      # r4 = this bank's table row
        ("h", 0x6823, "ldr", "r3,[r4,#0]"),     # destination palette RAM for this bank
        ("h", 0x68A1, "ldr", "r1,[r4,#8]"),     # source palette for this bank
        ("h", 0x1C18, "adds", "r0,r3,#0"),      # destination into r0
        ("h", 0x2220, "movs", "r2,#0x20"),      # 32 bytes, one bank's worth
        ("h", 0xB408, "push", "{r3}"),
        ("h", 0x4F00, "ldr", "r7,[pc,#0]"),     # the copy thunk, WITH bit 0 set: see COPY_THUNK
        ("h", 0x47B8, "blx", "r7"),
        ("h", 0xBC08, "pop", "{r3}"),
        ("h", 0x4C00, "ldr", "r4,[pc,#0]"),     # the resume address
        ("h", 0x4720, "bx", "r4"),
    ]

    offsets = []
    cursor = 0
    for kind, payload, _, _ in entries:
        offsets.append(cursor)
        cursor += payload if kind == "raw" else 2
    literal_table = (cursor + 3) & ~3
    literal_veneer = literal_table + 4
    literal_resume = literal_veneer + 4
    size = literal_resume + 4

    blob = bytearray(size)
    for (kind, payload, _, _), offset in zip(entries, offsets):
        if kind == "raw":
            blob[offset:offset + payload] = prefix
        else:
            struct.pack_into("<H", blob, offset, payload)
    struct.pack_into("<I", blob, literal_table, table_address)
    struct.pack_into("<I", blob, literal_veneer, COPY_THUNK | 1)
    struct.pack_into("<I", blob, literal_resume, RESUME | 1)

    for index, base_halfword, literal in (
            (5, 0x4800, literal_table), (13, 0x4F00, literal_veneer), (16, 0x4C00, literal_resume)):
        offset = offsets[index]
        struct.pack_into("<H", blob, offset, base_halfword | ldr_field(offset, literal))
    verify(bytes(blob), body_address, prefix_halfwords=len(prefix) // 2)
    return bytes(blob)


def body_size() -> int:
    """The assembled body's size, so callers can place the table before knowing the body's bytes."""
    cursor = sum(4 if kind == "bl" else 2 for kind, *_ in _entries_placeholder())
    return ((cursor + 3) & ~3) + 8


def _entries_placeholder():
    return [("h", 0, "", "")] * 10 + [("bl", 0, "", "")] + [("h", 0, "", "")] * 3


def verify(body: bytes, body_address: int, prefix_halfwords: int = 0) -> list[tuple[int, str, str]]:
    """Disassemble the body's own instructions and assert they are the intended ones.

    `prefix_halfwords` skips a raw prefix (the bank-select sequence, which `oam_bank_patch`'s own test
    covers byte for byte).
    """
    start = prefix_halfwords * 2
    wanted = [f"{mnemonic} {operands}" for _, _, mnemonic, operands in _text_entries()]
    got = disassemble(body[start:start + len(wanted) * 2], body_address + start)
    if len(got) != len(wanted):
        raise AssertionError(f"disassembled {len(got)} instruction(s), expected {len(wanted)}: {got}")
    for want, (at, mnemonic, operands) in zip(wanted, got):
        want_mnemonic, _, want_operands = want.partition(" ")
        if mnemonic != want_mnemonic:
            raise AssertionError(f"at 0x{at:08X}: expected `{want_mnemonic}`, got `{mnemonic} {operands}`")
        if want_operands.endswith("[pc,#0]"):
            if "[pc," not in operands:
                raise AssertionError(f"at 0x{at:08X}: expected a PC-relative load, got `{operands}`")
            continue
        if normalise(operands) != normalise(want_operands):
            raise AssertionError(f"at 0x{at:08X}: expected `{want_mnemonic} {want_operands}`, "
                                 f"got `{mnemonic} {operands}`")
    return got


def _text_entries() -> list[tuple[str, int, str, str]]:
    """The body's own instruction text, in order, matching the `("h", ...)` entries of `assemble`."""
    return [
        ("h", 0, "ldr", "r3,[r1]"), ("h", 0, "lsrs", "r7,r3,#0x19"), ("h", 0, "movs", "r5,#7"),
        ("h", 0, "ands", "r7,r5"), ("h", 0, "ldr", "r0,[pc,#0]"), ("h", 0, "lsls", "r4,r7,#3"),
        ("h", 0, "adds", "r4,r4,r0"), ("h", 0, "ldr", "r3,[r4,#0]"), ("h", 0, "ldr", "r1,[r4,#8]"),
        ("h", 0, "adds", "r0,r3,#0"), ("h", 0, "movs", "r2,#0x20"), ("h", 0, "push", "{r3}"),
        ("h", 0, "ldr", "r7,[pc,#0]"), ("h", 0, "blx", "r7"), ("h", 0, "pop", "{r3}"),
        ("h", 0, "ldr", "r4,[pc,#0]"), ("h", 0, "bx", "r4"),
    ]


def build_table(table_address: int) -> bytes:
    """The 16-row address table plus 16 zeroed palette blocks, at `table_address` in ROM space.

    Row `bank` is `(0x05000200 + 32*bank, table_address + TABLE_BYTES + 32*bank)`: both absolute, so the
    body needs no arithmetic beyond `base + 8*bank`.
    """
    table = bytearray(TABLE_BYTES + BANK_COUNT * BANK_BYTES)
    for bank in range(BANK_COUNT):
        struct.pack_into("<II", table, 8 * bank,
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
