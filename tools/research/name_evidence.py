from __future__ import annotations

import argparse
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import capstone  # noqa: E402
import gate  # noqa: E402
import romfile  # noqa: E402

ROM_BASE = 0x08000000
ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
MMIO = (0x04000000, 0x04000400)
SRAM = (0x0E000000, 0x0E010000)
LOAD_WIDTH = {"ldr": 4, "ldrh": 2, "ldrb": 1, "ldrsb": 1, "ldrsh": 2}
STORE_WIDTH = {"str": 4, "strh": 2, "strb": 1}
LIMM = re.compile(r"\[\s*(\w+)\s*(?:,\s*#(0x[0-9a-f]+|\d+))?\s*\]$")
REGISTER = re.compile(r"^(r\d+|sb|sl|fp|ip|sp|lr|pc|r12)$")
TARGET = re.compile(r"^#?(0x[0-9a-f]+|\d+)$")
THUMB_LDR_LITERAL = 0xF800
THUMB_LDR_BASE = 0x4800
THUMB_SWI = 0xDF00
SWI = (0x0F, 0x00)


def read_rom(path):
    return romfile.read_rom(path, ROM_SHA256)


def code_rows():
    return sorted((row[0], row[1], row[2]) for row in gate.ledger_rows()
                  if row[2] in ("thumb", "arm"))


def instruction(rom, address, mode):
    offset = address - ROM_BASE
    if mode == "arm" and address % 4:
        return None
    found = next(iter(ENGINES[mode].disasm(rom[offset:offset + 4], address, count=1)), None)
    if found is None:
        return None
    if found.size != (2 if mode == "thumb" else 4):
        return None
    return found


def steps(rom, row, mode):
    start, length = row[0], row[1]
    address = ROM_BASE + start
    end = address + length
    while address < end:
        found = instruction(rom, address, mode)
        if found is None:
            address += 2 if mode == "thumb" else 4
            continue
        yield found
        address += found.size


def quote(rom, address, mode, count=3):
    parts = []
    for back in range(count, 0, -1):
        found = instruction(rom, address - back * 2, mode)
        if found is not None and found.address + found.size == address:
            parts.append("%08X %s %s" % (found.address, found.mnemonic, found.op_str))
    found = instruction(rom, address, mode)
    parts.append("%08X %s %s" % (found.address, found.mnemonic, found.op_str))
    return " / ".join(parts)


def profile(rom, row):
    start, length, mode = row
    words = {}
    found = []
    for insn in steps(rom, row, mode):
        parts = [part.strip() for part in insn.op_str.split(",")]
        if insn.mnemonic == "ldr" and "[pc" in insn.op_str:
            match = re.search(r"\[pc,\s*#(0x[0-9a-f]+|\d+)\]", insn.op_str)
            if match:
                at = ((insn.address + 4) & ~3) + int(match.group(1), 0)
                if ROM_BASE <= at < ROM_BASE + len(rom):
                    words[parts[0]] = (struct.unpack_from("<I", rom, at - ROM_BASE)[0],
                                       insn.address)
            else:
                words.pop(parts[0], None)
            continue
        if insn.mnemonic in ("svc", "swi"):
            value = TARGET.match(parts[0])
            if value:
                found.append((insn.address, "swi", int(value.group(1), 0), 0, ""))
            continue
        if insn.mnemonic in LOAD_WIDTH or insn.mnemonic in STORE_WIDTH:
            match = LIMM.search(insn.op_str)
            if match and match.group(1) in words:
                base, loaded_at = words[match.group(1)]
                target = base + (int(match.group(2), 0) if match.group(2) else 0)
                if MMIO[0] <= target < MMIO[1] or SRAM[0] <= target < SRAM[1]:
                    kind = "write" if insn.mnemonic in STORE_WIDTH else "read"
                    width = STORE_WIDTH.get(insn.mnemonic) or LOAD_WIDTH[insn.mnemonic]
                    found.append((insn.address, kind, target, width, loaded_at))
        if parts[0] in words:
            words.pop(parts[0], None)
    return found


def walk(rom):
    out = []
    for row in code_rows():
        accesses = profile(rom, row)
        if accesses:
            out.append((ROM_BASE + row[0], row[1], row[2], accesses))
    return out


def accessors(entries):
    table = {}
    for function, _length, _mode, accesses in entries:
        for site, kind, target, width, loaded_at in accesses:
            table.setdefault((target, kind), []).append((function, site, width))
    return table


def dump(rom, entries):
    print("function,mode,length,kind,target,width,site,loaded_at")
    for function, length, mode, accesses in entries:
        for site, kind, target, width, loaded_at in sorted(accesses):
            print("%08X,%s,%d,%s,0x%08X,%d,%08X,%s"
                  % (function, mode, length, kind, target, width, site,
                     "%08X" % loaded_at if loaded_at else "-"))


def sole(entries):
    table = accessors(entries)
    for (target, kind), places in sorted(table.items()):
        owners = sorted({place[0] for place in places})
        if kind == "swi" or len(owners) == 1:
            print("0x%08X %-5s %s %s" % (target, kind,
                                         ",".join("%08X" % owner for owner in owners),
                                         " ".join("%08X/%d" % (site, width)
                                                  for _f, site, width in sorted(places))))


def swis(entries):
    table = {}
    for function, _length, _mode, accesses in entries:
        for site, kind, target, width, loaded_at in accesses:
            if kind == "swi":
                table.setdefault(target, []).append((function, site))
    for number, places in sorted(table.items()):
        print("0x%02X functions=%d %s" % (number, len({p[0] for p in places}),
                                          " ".join("%08X@%08X" % place
                                                   for place in sorted(places))))


def register(entries, wanted):
    table = accessors(entries)
    for kind in ("read", "write"):
        places = table.get((wanted, kind), [])
        print("0x%08X %s functions=%d" % (wanted, kind, len({p[0] for p in places})))
        for function, site, width in sorted(places):
            print("  function=%08X site=%08X width=%d" % (function, site, width))


def function(rom, entries, wanted):
    for address, length, mode, accesses in entries:
        if address != wanted:
            continue
        print("%08X %s len=%d" % (address, mode, length))
        for site, kind, target, width, loaded_at in sorted(accesses):
            print("  %s" % quote(rom, site, mode, 2))
            print("    %s 0x%08X width=%d literal=%s"
                  % (kind, target, width, "%08X" % loaded_at if loaded_at else "constant"))


def footprint(rom, entries):
    for function, length, mode, accesses in entries:
        print("%08X %s len=%d" % (function, mode, length))
        for site, kind, target, width, loaded_at in sorted(accesses):
            print("  %s" % quote(rom, site, mode, 2))
            print("    %-5s 0x%08X width=%d literal=%s"
                  % (kind, target, width, "%08X" % loaded_at if loaded_at else "constant"))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Which transcribed function drives which hardware register or BIOS call.")
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--register", type=lambda text: int(text, 0))
    parser.add_argument("--function", type=lambda text: int(text, 0))
    parser.add_argument("--mode", default="dump",
                        choices=("dump", "sole", "swi", "register", "function", "footprint"))
    args = parser.parse_args(argv)
    rom = read_rom(args.rom)
    entries = walk(rom)
    if args.mode == "dump":
        dump(rom, entries)
    elif args.mode == "sole":
        sole(entries)
    elif args.mode == "swi":
        swis(entries)
    elif args.mode == "register":
        register(entries, args.register)
    elif args.mode == "footprint":
        footprint(rom, entries)
    else:
        function(rom, entries, args.function)
    return 0


ENGINES = {"thumb": capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB),
           "arm": capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)}

if __name__ == "__main__":
    raise SystemExit(main())
