"""The ONE-SHOT palette write: fill three OBJ palette banks, once, after the scene's own palette load.

WHERE IT RUNS. The scene's video programmer loads the whole 256-entry OBJ palette from the ROM table
0x0805652C with a 512-byte copy through the IWRM veneer 0x08049144. Decoded from the image, that load is
two calls (file 0x00657A and file 0x006586) in the routine at 0x08006570:

    0x08006570  movs r2,#1 ; lsls r2,r2,#9      r2 = 0x200
    0x08006574  movs r0,#5 ; lsls r0,r0,#0x18   r0 = 0x05000000
    0x08006578  ldr  r1,[pc,#0x38]              r1 = 0x0805652C
    0x0800657A  bl   0x08049144                 the BG copy
    0x0800657E  movs r2,#1 ; lsls r2,r2,#9
    0x08006582  ldr  r1,[pc,#0x30]              r1 = 0x0805652C
    0x08006584  ldr  r0,[pc,#0x30]              r0 = 0x05000200
    0x08006586  bl   0x08049144                 THE OBJ COPY
    0x0800658A  movs r0,#0 ; pop {r4,pc}         the routine returns

The hook replaces exactly the four bytes of the OBJ copy call (file 0x006586, `42 F0 DD FD`) with a Thumb
`bl` to this one-shot. The one-shot performs that copy itself, with the caller's own r0/r1/r2, and then
writes the palettes, so the write lands after the scene's palette load by construction. A Thumb `bl` carries
a 25-bit immediate (+/-16 MB), which is what lets a stub above EOF be reached from the code region; the
image must stay inside that window, and the builder asserts it.

THE CHOICE IS MADE AT RUNTIME, from what is actually drawn. Banks are chosen from the palette indices the
VISIBLE OAM entries paint: for every enabled entry, the 8bpp tile at 0x06010000 + 64*tile is scanned and
each non-zero pixel index marks its bank. A 4bpp entry (attr0 bit 13 clear; our own art, and the piece attr
bit 13 is what the engine copies) marks the bank named in attr2 bits 12..15 without reading VRAM. The
LOWEST three free banks are taken.

TWO CODED GUARDS, because the OAM is not yet known to be composed for the new scene at this instant:

* if fewer than MINIMUM_USED banks are marked used, the OAM is treated as not composed and the stub writes
  NOTHING (a stale or empty OAM would otherwise report every bank free and hand the character the shared
  banks 0..2, changing every other actor's colours);
* if fewer than three banks are free, the stub writes NOTHING and the draw-loop body falls back to bank 0,
  the coded 16-colour mapping.

Both the hook point and the "free" premise are HYPOTHESES until a cold-boot run shows the write landing.
The run must count the stub's visits (P-100) and read the palette RAM back.

NO WRITE to the ROM palette table at 0x05652C: the three palettes travel as appended data.

Invoke:
  python -m tools.research.palette_oneshot --image RETAIL.gba --palettes 0x089B0000 --decode 0x08006570
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.research import palette_writer as writer  # noqa: E402

ROM_BASE = 0x08000000

#: The OBJ palette copy call inside the scene palette loader: file 0x006586, `bl 0x08049144`.
HOOK_SITE = 0x08006586
HOOK_BYTES = 4
EXPECTED_HOOK = bytes.fromhex("42f0ddfd")
#: Where the loader returns to after that call: `movs r0,#0` then `pop {r4,pc}`.
RESUME = 0x0800658A
EXPECTED_RESUME = bytes.fromhex("002010bd")
#: The loader's own literals, which identify the site positively rather than by address alone.
LITERAL_TABLE_SITE = 0x080065B4
LITERAL_RAM_SITE = 0x080065B8
OBJ_PALETTE_TABLE = 0x0805652C
OBJ_PALETTE_RAM = 0x05000200
COPY_VENEER = 0x08049144

OAM = 0x07000000
OBJ_VRAM = 0x06010000
BANK_BYTES = writer.BANK_BYTES
BANK_COUNT = writer.BANK_COUNT
TILE_BYTES_8BPP = 64
OAM_ENTRIES = 128
#: The character's logical banks: one 32-byte palette block each, written into one chosen bank each.
BANKS = 3
#: A Thumb `bl` immediate is 25 bits signed, so the stub must sit inside this window of the hook.
BL_REACH = 1 << 24

#: The marker the draw-loop body looks for is `writer.MARKER_BASE | index`; this stub writes it.
MARKER_BASE = writer.MARKER_BASE

#: A scene with fewer marked banks than this is treated as not composed yet and nothing is written.
DEFAULT_MINIMUM_USED = 4


#: The veneer is named because a `bl` from an appended stub must state an absolute destination.
ADDRESSES = {"copy_veneer": COPY_VENEER}


def thumb_bl(from_address: int, to_address: int) -> bytes:
    """The four bytes of a Thumb `bl` from `from_address` (halfword aligned) to `to_address`."""
    offset = to_address - (from_address + 4)
    if offset % 2 or not -BL_REACH <= offset < BL_REACH:
        raise ValueError(f"a Thumb bl from 0x{from_address:08X} cannot reach 0x{to_address:08X}: "
                         f"offset {offset}")
    sign = (offset >> 24) & 1
    i1 = (offset >> 23) & 1
    i2 = (offset >> 22) & 1
    j1 = 1 - (i1 ^ sign)
    j2 = 1 - (i2 ^ sign)
    high = 0xF000 | (sign << 10) | ((offset >> 12) & 0x3FF)
    low = 0xD000 | (j1 << 13) | (j2 << 11) | ((offset >> 1) & 0x7FF)
    return struct.pack("<HH", high, low)


def branch_field(from_offset: int, to_offset: int) -> int:
    gap = to_offset - (from_offset + 4)
    if gap % 2 or not -256 <= gap <= 254:
        raise ValueError(f"branch from {from_offset:#x} to {to_offset:#x} is out of range: {gap}")
    return (gap // 2) & 0xFF


def goto_field(from_offset: int, to_offset: int) -> int:
    gap = to_offset - (from_offset + 4)
    if gap % 2 or not -2048 <= gap <= 2046:
        raise ValueError(f"goto from {from_offset:#x} to {to_offset:#x} is out of range: {gap}")
    return (gap // 2) & 0x7FF


def steps(minimum_used: int) -> list[tuple]:
    """The one-shot's instructions, in order.

    Kinds: ("label", name), ("word", halfword, mnemonic, operands), ("branch", cond_halfword, mnemonic,
    target), ("goto", target), ("ldr", rd, mnemonic, operands, literal), ("bl", target).
    """
    if not 0 <= minimum_used <= 16:
        raise ValueError(f"minimum_used must be 0..16, got {minimum_used}")
    out: list[tuple] = [
        ("word", 0xB5F0, "push", "{r4, r5, r6, r7, lr}"),
        ("bl", "copy_veneer"),                                  # the OBJ palette copy we replaced
        ("word", 0x2400, "movs", "r4, #0"),                     # used-bank mask
        ("word", 0x2500, "movs", "r5, #0"),                     # OAM entry index
        ("ldr", 6, "ldr", "r6, [pc, #0]", "oam"),
        ("label", "OAM_LOOP"),
        ("word", 0x00E8, "lsls", "r0, r5, #3"),
        ("word", 0x1980, "adds", "r0, r0, r6"),
        ("word", 0x8801, "ldrh", "r1, [r0]"),                   # attr0
        ("word", 0x8883, "ldrh", "r3, [r0, #4]"),               # attr2
        ("word", 0x1C0A, "adds", "r2, r1, #0"),
        ("word", 0x0A12, "lsrs", "r2, r2, #8"),
        ("word", 0x2003, "movs", "r0, #3"),
        ("word", 0x4002, "ands", "r2, r0"),
        ("word", 0x2A02, "cmp", "r2, #2"),
        ("branch", 0xD000, "beq", "OAM_NEXT"),                  # mode 2: entry disabled
        ("word", 0x2220, "movs", "r2, #0x20"),
        ("word", 0x0212, "lsls", "r2, r2, #8"),
        ("word", 0x400A, "ands", "r2, r1"),
        ("branch", 0xD000, "beq", "FOUR_BPP"),                  # attr0 bit 13 clear: 16-colour entry
        ("word", 0x059B, "lsls", "r3, r3, #22"),
        ("word", 0x0D9B, "lsrs", "r3, r3, #22"),                # tile number
        ("word", 0x019B, "lsls", "r3, r3, #6"),                 # 64 bytes per 8bpp tile
        ("ldr", 7, "ldr", "r7, [pc, #0]", "vram"),
        ("word", 0x18FF, "adds", "r7, r7, r3"),
        ("word", 0x2200 | TILE_BYTES_8BPP, "movs", "r2, #0x40"),   # pixels per tile
        ("label", "PIXEL_LOOP"),
        ("word", 0x7838, "ldrb", "r0, [r7]"),
        ("word", 0x2800, "cmp", "r0, #0"),
        ("branch", 0xD000, "beq", "PIXEL_NEXT"),                # index 0 is transparent
        ("word", 0x0900, "lsrs", "r0, r0, #4"),                 # bank of this pixel
        ("bl", "SET_BIT"),
        ("label", "PIXEL_NEXT"),
        ("word", 0x3701, "adds", "r7, #1"),
        ("word", 0x3A01, "subs", "r2, #1"),
        ("branch", 0xD100, "bne", "PIXEL_LOOP"),
        ("goto", "OAM_NEXT"),
        ("label", "FOUR_BPP"),
        ("word", 0x1C18, "adds", "r0, r3, #0"),
        ("word", 0x0B00, "lsrs", "r0, r0, #12"),                # attr2 bits 12..15 name the bank
        ("bl", "SET_BIT"),
        ("label", "OAM_NEXT"),
        ("word", 0x3501, "adds", "r5, #1"),
        ("word", 0x2D00 | OAM_ENTRIES, "cmp", "r5, #0x80"),
        ("branch", 0xD100, "bne", "OAM_LOOP"),
        ("word", 0x2300, "movs", "r3, #0"),                     # popcount of the mask
        ("word", 0x1C21, "adds", "r1, r4, #0"),
        ("word", 0x2000 | BANK_COUNT, "movs", "r0, #16"),
        ("label", "POP_LOOP"),
        ("word", 0x0849, "lsrs", "r1, r1, #1"),
        ("word", 0x415B, "adcs", "r3, r3"),                     # 2*r3 + carry
        ("word", 0x3801, "subs", "r0, #1"),
        ("branch", 0xD100, "bne", "POP_LOOP"),
        ("word", 0x2B00 | minimum_used, "cmp", "r3, #%d" % minimum_used),
        ("branch", 0xDB00, "blt", "FALLBACK"),
        ("word", 0x2101, "movs", "r1, #1"),                     # bit cursor
        ("word", 0x2000, "movs", "r0, #0"),                     # bank index
        ("word", 0x2300, "movs", "r3, #0"),                     # banks taken
        ("label", "PICK_LOOP"),
        ("word", 0x1C22, "adds", "r2, r4, #0"),
        ("word", 0x400A, "ands", "r2, r1"),
        ("branch", 0xD100, "bne", "PICK_NEXT"),
        ("word", 0x2B00, "cmp", "r3, #0"),
        ("branch", 0xD100, "bne", "PICK_ONE"),
        ("word", 0x1C05, "adds", "r5, r0, #0"),
        ("goto", "PICK_STORE"),
        ("label", "PICK_ONE"),
        ("word", 0x2B01, "cmp", "r3, #1"),
        ("branch", 0xD100, "bne", "PICK_TWO"),
        ("word", 0x1C06, "adds", "r6, r0, #0"),
        ("goto", "PICK_STORE"),
        ("label", "PICK_TWO"),
        ("word", 0x1C07, "adds", "r7, r0, #0"),
        ("label", "PICK_STORE"),
        ("word", 0x3301, "adds", "r3, #1"),
        ("word", 0x2B00 | BANKS, "cmp", "r3, #3"),
        ("branch", 0xD000, "beq", "PICK_DONE"),
        ("label", "PICK_NEXT"),
        ("word", 0x0049, "lsls", "r1, r1, #1"),
        ("word", 0x3001, "adds", "r0, #1"),
        ("word", 0x2800 | BANK_COUNT, "cmp", "r0, #16"),
        ("branch", 0xD100, "bne", "PICK_LOOP"),
        ("label", "PICK_DONE"),
        ("word", 0x2B00 | BANKS, "cmp", "r3, #3"),
        ("branch", 0xDB00, "blt", "FALLBACK"),
    ]
    for register, index in ((5, 1), (6, 2), (7, 3)):
        out += write_block(register, index)
    out += [
        ("goto", "DONE"),
        ("label", "FALLBACK"),
        ("word", 0x46C0, "mov", "r8, r8"),                      # nothing is written: the 16-colour mapping
        ("label", "DONE"),
        ("word", 0xBCF0, "pop", "{r4, r5, r6, r7}"),
        ("ldr", 3, "ldr", "r3, [pc, #0]", "resume"),
        ("word", 0x4718, "bx", "r3"),
        ("label", "SET_BIT"),
        ("word", 0x2101, "movs", "r1, #1"),
        ("label", "SET_BIT_LOOP"),
        ("word", 0x2800, "cmp", "r0, #0"),
        ("branch", 0xD000, "beq", "SET_BIT_DONE"),
        ("word", 0x0049, "lsls", "r1, r1, #1"),
        ("word", 0x3801, "subs", "r0, #1"),
        ("goto", "SET_BIT_LOOP"),
        ("label", "SET_BIT_DONE"),
        ("word", 0x430C, "orrs", "r4, r1"),
        ("word", 0x4770, "bx", "lr"),
    ]
    return out


def write_block(register: int, index: int) -> list[tuple]:
    """One bank's write: copy the 32-byte palette block, then leave the marker the body reads.

    `register` holds the chosen bank, `index` is the logical index (1..3) and `index - 1` selects the block
    in the appended palette record.
    """
    loop = f"WRITE_{index}_LOOP"
    return [
        ("ldr", 0, "ldr", "r0, [pc, #0]", "palettes"),
        ("word", 0x3000 | ((index - 1) * BANK_BYTES), "adds", "r0, #%d" % ((index - 1) * BANK_BYTES)),
        ("word", 0x1C00 | (register << 3) | 1, "adds", "r1, r%d, #0" % register),
        ("word", 0x0149, "lsls", "r1, r1, #5"),                 # bank * 32
        ("ldr", 2, "ldr", "r2, [pc, #0]", "palette_ram"),
        ("word", 0x1889, "adds", "r1, r1, r2"),
        ("word", 0x2210, "movs", "r2, #16"),                    # 16 halfwords
        ("word", 0x234B, "movs", "r3, #0x4b"),
        ("word", 0x021B, "lsls", "r3, r3, #8"),                 # MARKER_BASE
        ("word", 0x3300 | index, "adds", "r3, #%d" % index),
        ("label", loop),
        ("word", 0x8804, "ldrh", "r4, [r0]"),
        ("word", 0x800C, "strh", "r4, [r1]"),
        ("word", 0x3002, "adds", "r0, #2"),
        ("word", 0x3102, "adds", "r1, #2"),
        ("word", 0x3A01, "subs", "r2, #1"),
        ("branch", 0xD100, "bne", loop),
        ("word", 0x3920, "subs", "r1, #32"),
        ("word", 0x800B, "strh", "r3, [r1]"),                   # the marker, at entry 0 of the bank
    ]


def associate(step_list: list[tuple], literals: dict[str, int]):
    """(offsets by label, places by literal name, total code size in bytes)."""
    offsets: dict[str, int] = {}
    places: dict[str, int] = {}
    offset = 0
    for step in step_list:
        if step[0] == "label":
            offsets[step[1]] = offset
            continue
        offset += 4 if step[0] == "bl" else 2
    code_end = offset
    literal_base = (code_end + 3) & ~3
    for step in step_list:
        if step[0] == "ldr" and step[4] not in places:
            places[step[4]] = literal_base + 4 * len(places)
    unknown = set(places) - set(literals)
    if unknown:
        raise AssertionError(f"the stub loads literal(s) with no value: {sorted(unknown)}")
    return offsets, places, literal_base + 4 * len(places)


def assemble(code_address: int, palettes_address: int, minimum_used: int = DEFAULT_MINIMUM_USED) -> bytes:
    """The one-shot's bytes, with every instruction checked against a disassembly before it is returned.

    `palettes_address` is the first of three contiguous 32-byte palette blocks appended to the image.
    """
    literals = {
        "oam": OAM,
        "vram": OBJ_VRAM,
        "palette_ram": OBJ_PALETTE_RAM,
        "palettes": palettes_address,
        "resume": RESUME | 1,
    }
    step_list = steps(minimum_used)
    offsets, places, size = associate(step_list, literals)
    blob = bytearray(size)
    offset = 0
    listing: list[tuple[int, str, str]] = []
    for step in step_list:
        kind = step[0]
        if kind == "label":
            continue
        at = code_address + offset
        if kind == "word":
            struct.pack_into("<H", blob, offset, step[1])
            listing.append((at, step[2], step[3]))
            offset += 2
        elif kind == "branch":
            halfword = (step[1] & 0xFF00) | branch_field(offset, offsets[step[3]])
            struct.pack_into("<H", blob, offset, halfword)
            listing.append((at, step[2], "#0x%X" % (code_address + offsets[step[3]])))
            offset += 2
        elif kind == "goto":
            halfword = 0xE000 | goto_field(offset, offsets[step[1]])
            struct.pack_into("<H", blob, offset, halfword)
            listing.append((at, "b", "#0x%X" % (code_address + offsets[step[1]])))
            offset += 2
        elif kind == "ldr":
            halfword = 0x4800 | (step[1] << 8) | _ldr_field(offset, places[step[4]])
            struct.pack_into("<H", blob, offset, halfword)
            listing.append((at, step[2], step[3]))
            offset += 2
        elif kind == "bl":
            destination = ADDRESSES.get(step[1])
            if destination is None:
                destination = code_address + offsets[step[1]]
            blob[offset:offset + 4] = thumb_bl(at, destination)
            listing.append((at, "bl", "#0x%X" % destination))
            offset += 4
        else:
            raise AssertionError(f"unknown step kind {kind!r}")
    for name, place in places.items():
        struct.pack_into("<I", blob, place, literals[name])
    verify(bytes(blob[:offset]), listing)
    return bytes(blob)


def _ldr_field(instruction_offset: int, literal_offset: int) -> int:
    pc_value = (instruction_offset + 4) & ~3
    gap = literal_offset - pc_value
    if gap < 0 or gap % 4 or gap // 4 > 0xFF:
        raise ValueError(f"literal at {literal_offset:#x} unreachable from {instruction_offset:#x}: "
                         f"pc {pc_value:#x}, gap {gap}")
    return gap // 4


def canonical(operands: str) -> str:
    """Operands compared by what they mean: spacing, `[rN]` vs `[rN,#0]` and hex vs decimal immediates.

    Capstone prints `#0x16` for a shift of 22 and `#8` for a shift of 8; both are the same field, and the
    point of the check is the field, not its base.
    """
    text = re.sub(r"\[(\w+)\]", r"[\1,#0]", operands.replace(" ", "").lower())
    text = re.sub(r"#0x([0-9a-f]+)", lambda match: "#%d" % int(match.group(1), 16), text)
    return re.sub(r"#(\d+)", lambda match: "#%d" % int(match.group(1)), text)


def verify(code: bytes, listing: list[tuple[int, str, str]]) -> list[tuple[int, str, str]]:
    """Disassemble the assembled bytes and assert every instruction is the intended one (P-083)."""
    got = writer.disassemble(code, listing[0][0])
    if len(got) != len(listing):
        raise AssertionError(f"disassembled {len(got)} instruction(s), expected {len(listing)}: {got}")
    for (want_at, want_mnemonic, want_operands), (at, mnemonic, operands) in zip(listing, got):
        if at != want_at or mnemonic != want_mnemonic:
            raise AssertionError(f"at 0x{at:08X}: expected `{want_mnemonic}`, got `{mnemonic} {operands}`")
        if want_mnemonic == "bl" or want_mnemonic.startswith("b"):
            if canonical(operands) != canonical(want_operands):
                raise AssertionError(f"at 0x{at:08X}: expected `{want_mnemonic} {want_operands}`, "
                                     f"got `{mnemonic} {operands}`")
            continue
        if want_operands.endswith("[pc, #0]"):
            if "[pc," not in operands:
                raise AssertionError(f"at 0x{at:08X}: expected a PC-relative load, got `{operands}`")
            continue
        if canonical(operands) != canonical(want_operands):
            raise AssertionError(f"at 0x{at:08X}: expected `{want_mnemonic} {want_operands}`, "
                                 f"got `{mnemonic} {operands}`")
    return got


def free_banks(used_mask: int, count: int = 3) -> list[int]:
    """The rule the Thumb picker implements, stated once: the LOWEST `count` free banks.

    An empty list means "nothing was written": the draw-loop body then maps every index to bank 0, which is
    the coded 16-colour fallback. This is the reference the stub's own arm is checked against, not a second
    implementation of the write.
    """
    return [bank for bank in range(BANK_COUNT) if not used_mask >> bank & 1][:count]


def hook(image: bytearray, stub_address: int) -> bytes:
    """Replace the scene loader's OBJ palette copy call with a `bl` to the one-shot. Returns what it replaced.

    The guard is the site's own bytes AND the loader's two literals, so a wrong or already patched image
    stops instead of corrupting: an image whose call is already a `bl` to somewhere else is refused.
    """
    offset = HOOK_SITE - ROM_BASE
    found = bytes(image[offset:offset + HOOK_BYTES])
    if found != EXPECTED_HOOK:
        raise AssertionError(
            f"the OBJ palette copy at 0x{HOOK_SITE:08X} is not the retail call, so this image is either "
            f"already patched or not the image this stub was written for; refusing. Found {found.hex()}")
    table = struct.unpack_from("<I", image, LITERAL_TABLE_SITE - ROM_BASE)[0]
    ram = struct.unpack_from("<I", image, LITERAL_RAM_SITE - ROM_BASE)[0]
    if table != OBJ_PALETTE_TABLE or ram != OBJ_PALETTE_RAM:
        raise AssertionError(f"the loader's literals are 0x{table:08X} and 0x{ram:08X}, expected "
                             f"0x{OBJ_PALETTE_TABLE:08X} and 0x{OBJ_PALETTE_RAM:08X}; refusing")
    resume = bytes(image[RESUME - ROM_BASE:RESUME - ROM_BASE + len(EXPECTED_RESUME)])
    if resume != EXPECTED_RESUME:
        raise AssertionError(f"the loader does not return at 0x{RESUME:08X} as measured: {resume.hex()}")
    if not HOOK_SITE - BL_REACH < stub_address < HOOK_SITE + BL_REACH:
        raise AssertionError(f"a Thumb bl from 0x{HOOK_SITE:08X} cannot reach 0x{stub_address:08X}")
    image[offset:offset + HOOK_BYTES] = thumb_bl(HOOK_SITE, stub_address)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path, required=True,
                        help="the image to decode or to build the stub for")
    parser.add_argument("--palettes", type=lambda text: int(text, 0), default=0x089B0000)
    parser.add_argument("--code", type=lambda text: int(text, 0), default=0x089B1000)
    parser.add_argument("--minimum-used", type=int, default=DEFAULT_MINIMUM_USED)
    parser.add_argument("--decode", type=lambda text: int(text, 0), default=None)
    args = parser.parse_args()

    if args.decode is not None:
        image = args.image.read_bytes()
        length = 0x40
        sweep = writer.disassemble(image[args.decode - ROM_BASE:args.decode - ROM_BASE + length],
                                   args.decode)
        for at, mnemonic, operands in sweep:
            print(f"  {at:08X}  {mnemonic:<8} {operands}")
        return 0

    code = assemble(args.code, args.palettes, args.minimum_used)
    print(f"one-shot {len(code)} bytes at 0x{args.code:08X}, palettes at 0x{args.palettes:08X}, "
          f"minimum used banks {args.minimum_used}")
    for at, mnemonic, operands in writer.disassemble(code, args.code):
        print(f"  {at:08X}  {mnemonic:<8} {operands}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
