from __future__ import annotations

import argparse
import bisect
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import capstone  # noqa: E402
import gate  # noqa: E402
import romfile  # noqa: E402

ROM_BASE = 0x08000000
ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
MEMCPY = {0x08049138: "copy32", 0x08049144: "copy16"}
VRAM = (0x06000000, 0x06020000)
PALETTE = (0x05000000, 0x05000400)
WINDOW = 40


def read_rom(path):
    return romfile.read_rom(path, ROM_SHA256)


def code_rows():
    rows = gate.ledger_rows()
    return sorted((row[0], row[0] + row[1]) for row in rows if row[2] in ("thumb", "arm"))


def in_rows(rows, starts, offset):
    index = bisect.bisect_right(starts, offset) - 1
    return index >= 0 and rows[index][0] <= offset < rows[index][1]


def bl_target(rom, offset):
    high, low = struct.unpack_from("<HH", rom, offset)
    if (high & 0xF800) != 0xF000 or (low & 0xF800) != 0xF800:
        return None
    value = ((high & 0x7FF) << 12) | ((low & 0x7FF) << 1)
    if value & 0x400000:
        value -= 0x800000
    return ROM_BASE + offset + 4 + value


def sites(rom):
    rows = code_rows()
    starts = [start for start, _end in rows]
    found = []
    for offset in range(0, len(rom) - 4, 2):
        target = bl_target(rom, offset)
        if target in MEMCPY and in_rows(rows, starts, offset):
            found.append((ROM_BASE + offset, MEMCPY[target]))
    return found


def decode(rom, address):
    offset = address - ROM_BASE
    for size in (4, 2):
        found = next(iter(capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB).disasm(
            rom[offset:offset + size], address, count=1)), None)
        if found and found.size == size:
            return found.mnemonic, found.op_str
    return None


def window(rom, address, size=2 * WINDOW):
    offset = address - ROM_BASE
    engine = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    for length in range(size, 1, -2):
        start = offset - length
        found = list(engine.disasm(rom[start:offset], ROM_BASE + start))
        if found and found[-1].address + found[-1].size == address:
            return [(item.address, item.mnemonic, item.op_str) for item in found]
    return []


def replay(rom, address):
    state = {}
    for back, mnemonic, operands in window(rom, address):
        parts = [part.strip() for part in operands.split(",")]
        target = parts[0]
        value = set()
        try:
            if mnemonic in ("movs", "mov") and len(parts) == 2 and parts[1].startswith("#"):
                value = {int(parts[1][1:], 0)}
            elif mnemonic == "lsls" and len(parts) == 3:
                shift = int(parts[2][1:], 0)
                value = {v << shift for v in state.get(parts[1], set()) if v << shift < 1 << 32}
            elif mnemonic == "adds" and len(parts) == 3:
                if parts[2].startswith("#"):
                    value = {v + int(parts[2][1:], 0) for v in state.get(parts[1], set())}
                else:
                    left, right = state.get(parts[1], set()), state.get(parts[2], set())
                    value = {a + b for a in left for b in right}
                    if not right:
                        value |= set(left)
                    if not left:
                        value |= set(right)
            elif mnemonic == "subs" and len(parts) == 3 and parts[2].startswith("#"):
                limit = int(parts[2][1:], 0)
                value = {v - limit for v in state.get(parts[1], set()) if v >= limit}
            elif mnemonic == "ldr":
                literal = re.search(r"\[pc, #(0x[0-9a-f]+)\]", operands)
                if literal:
                    at = ((back + 4) & ~3) + int(literal.group(1), 16)
                    value = {struct.unpack_from("<I", rom, at - ROM_BASE)[0]}
        except (ValueError, struct.error):
            value = set()
        if re.fullmatch(r"r\d+|sb|sl|fp|ip", target):
            state[target] = value
    return state


def classify(rom):
    out = []
    for address, family in sites(rom):
        state = replay(rom, address)
        destination = sorted(v for v in state.get("r0", set()) if VRAM[0] <= v < VRAM[1])
        colors = sorted(v for v in state.get("r0", set()) if PALETTE[0] <= v < PALETTE[1])
        source = sorted(v for v in state.get("r1", set()) if ROM_BASE <= v < ROM_BASE + len(rom))
        length = sorted(state.get("r2", set()))
        out.append({"site": address, "family": family, "vram": destination,
                    "palette": colors, "source": source, "length": length})
    return out


def report(rows):
    vram = [row for row in rows if row["vram"]]
    colors = [row for row in rows if row["palette"] and not row["vram"]]
    print("copy sites in transcribed code %d" % len(rows))
    print("VRAM destination base resolved %d, palette destination %d, unresolved %d"
          % (len(vram), len(colors), len(rows) - len(vram) - len(colors)))
    for row in vram:
        print("  %08X %-6s vram %s src %s len %s"
              % (row["site"], row["family"],
                 ",".join("%08X" % v for v in row["vram"]) or "-",
                 ",".join("%08X" % v for v in row["source"]) or "-",
                 ",".join("%d" % v for v in row["length"][:1]) or "-"))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Which code copies a retail byte range to VRAM without a codec, and where.")
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    args = parser.parse_args(argv)
    return report(classify(read_rom(args.rom)))


if __name__ == "__main__":
    raise SystemExit(main())
