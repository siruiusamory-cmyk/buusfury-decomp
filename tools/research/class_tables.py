from __future__ import annotations

import argparse
import csv
import os
import struct
import sys
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import capstone
import name_evidence
import romfile

ROM_BASE = 0x08000000
OUTPUT = os.path.join(ROOT, "tools", "research", "CLASS_TABLES.csv")
HEADER = ["table", "slot", "off", "target", "function", "slots", "next_base", "installed_by"]
PC_R = capstone.arm.ARM_REG_PC
MEM = capstone.arm.ARM_OP_MEM
REG = capstone.arm.ARM_OP_REG
IMM = capstone.arm.ARM_OP_IMM
MIN_SLOTS = 8
MAX_SLOTS = 128
WRITES_DEST = {
    "add", "adds", "add.w", "adr", "and", "ands", "asr", "asrs", "eor", "eors",
    "ldr", "ldrb", "ldrh", "ldrsb", "ldrsh", "ldr.w", "ldrb.w", "ldrh.w",
    "lsl", "lsls", "lsr", "lsrs", "mov", "movs", "mov.w", "mul", "muls",
    "mvn", "mvns", "neg", "negs", "orr", "orrs", "rsb", "rsbs", "sbc",
    "sub", "subs", "sub.w", "sxtb", "sxth", "uxtb", "uxth",
}


def load_rows(root=ROOT):
    labels = tomllib.load(open(os.path.join(root, "tools", "lint", "BF_LABELS.toml"), "rb"))
    named, ends, modes = {}, {}, {}
    for entry in labels["functions"]:
        address = entry["address"]
        named[address] = entry["name"]
        modes[address] = entry.get("mode", "thumb")
        if "end" in entry:
            ends[address] = entry["end"]
    with open(os.path.join(root, "tools", "lint", "ASM_INDEX.csv"), newline="") as handle:
        symbol = {int(row["address"], 16): row["symbol"] for row in csv.DictReader(handle)}
    with open(os.path.join(root, "tools", "research", "FUNCTION_BOUNDS.csv"), newline="") as handle:
        census = sorted({int(row["address"], 16) for row in csv.DictReader(handle)
                         if row["kind"] == "start"})
    starts = sorted(set(symbol) | set(named) | set(census))
    rows = []
    for index, address in enumerate(starts):
        following = starts[index + 1] if index + 1 < len(starts) else address + 2
        end = min(ends[address], following) if address in ends else following
        rows.append((address, end, modes.get(address) or "thumb",
                     named.get(address) or symbol.get(address) or "0x%08X" % address))
    return rows


def value_of(rom, pool):
    if ROM_BASE <= pool <= ROM_BASE + len(rom) - 4:
        return struct.unpack_from("<I", rom, pool - ROM_BASE)[0]
    return None


def stores_of_row(rom, row, engines):
    start, end, mode, _name = row
    engine = engines[mode]
    values = {}
    found = []
    for insn in engine.disasm(rom[start - ROM_BASE:end - ROM_BASE], start):
        site = insn.address
        mnemonic = insn.mnemonic
        operands = insn.operands
        if mnemonic in ("ldr", "ldr.w") and len(operands) == 2 and operands[1].type == MEM \
                and operands[1].mem.base == PC_R:
            base = ((site + 4) & ~3) if mode != "arm" else site + 8
            values[operands[0].reg] = value_of(rom, base + operands[1].mem.disp)
            continue
        if mnemonic in ("str", "str.w", "strb", "strh") and len(operands) == 2 \
                and operands[1].type == MEM:
            source = values.get(operands[0].reg) if operands[0].type == REG else None
            if source is not None and ROM_BASE <= source < ROM_BASE + len(rom) \
                    and operands[1].mem.disp == 0:
                found.append((source, site))
            continue
        if mnemonic in ("mov", "movs", "mov.w") and len(operands) == 2 \
                and operands[0].type == REG and operands[1].type == REG:
            values[operands[0].reg] = values.get(operands[1].reg)
            continue
        if mnemonic in ("adds", "add", "add.w") and len(operands) == 3 \
                and operands[0].type == REG and operands[1].type == REG \
                and operands[2].type == IMM:
            source = values.get(operands[1].reg)
            values[operands[0].reg] = source + operands[2].imm if source is not None else None
            continue
        if mnemonic in ("pop", "ldm", "ldmia", "ldmdb"):
            for operand in operands:
                if operand.type == REG:
                    values[operand.reg] = None
            continue
        if mnemonic in WRITES_DEST and operands and operands[0].type == REG:
            values[operands[0].reg] = None
    return found


def census(rom, rows):
    words = struct.unpack_from("<%dI" % (len(rom) // 4), rom, 0)

    def at(address):
        index = (address - ROM_BASE) // 4
        return words[index] if 0 <= index < len(words) else None

    def resolves(base, slot):
        delta = at(base + 4 * slot)
        if delta is None:
            return None
        target = (base + delta) & 0xFFFFFFFF
        return target if (target & 1) and ROM_BASE <= target - 1 < 0x087C0000 else None

    installers = {}
    engines = {"thumb": capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB),
               "arm": capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)}
    for engine in engines.values():
        engine.detail = True
    for start, end, mode, _name in rows:
        for table, site in stores_of_row(rom, (start, end, mode, ""), engines):
            installers.setdefault(table, set()).add((start, site))
    tables = [base for base in sorted(installers)
              if all(resolves(base, slot) is not None for slot in range(MIN_SLOTS))]
    slots, counts = [], {}
    for index, base in enumerate(tables):
        following = tables[index + 1] if index + 1 < len(tables) else None
        limit = (following - base) // 4 if following else MAX_SLOTS
        for slot in range(min(limit, MAX_SLOTS)):
            target = resolves(base, slot)
            if target is None:
                break
            slots.append((base, slot, target - 1))
            counts[base] = slot + 1
    return tables, slots, installers, counts


def text(rom, root=ROOT):
    rows = load_rows(root)
    tables, slots, installers, counts = census(rom, rows)
    names = {address: name for address, _end, _mode, name in rows}
    lines = [",".join(HEADER)]
    for index, base in enumerate(tables):
        following = tables[index + 1] if index + 1 < len(tables) else None
        lines.append(",".join(["0x%08X" % base, "", "", "", "", str(counts[base]),
                               "0x%08X" % following if following else "",
                               ";".join("%s@%08X" % (names.get(start, "0x%08X" % start), site)
                                        for start, site in sorted(installers[base]))]))
        for base_slot, slot, target in slots:
            if base_slot != base:
                continue
            lines.append(",".join(["0x%08X" % base, str(slot), "0x%02X" % (4 * slot),
                                   "0x%08X" % target,
                                   names.get(target, "0x%08X" % target), "", "", ""]))
    return "\n".join(lines) + "\n", len(tables), len(slots)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="The class tables the image stores at [object+0], and their slots.")
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    if not os.path.exists(arguments.rom):
        print("the class tables need the retail image at %s" % arguments.rom)
        return 1
    rom = romfile.read_rom(arguments.rom, name_evidence.ROM_SHA256)
    body, table_count, slot_count = text(rom)
    print("tables=%d slots=%d" % (table_count, slot_count))
    if arguments.write:
        with open(OUTPUT, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(body)
        print("wrote %s" % os.path.relpath(OUTPUT, ROOT).replace("\\", "/"))
        return 0
    if arguments.check:
        current = open(OUTPUT, encoding="utf-8").read() if os.path.exists(OUTPUT) else None
        if current != body:
            print("CLASS-TABLES FAIL: %s is not what the image gives"
                  % os.path.relpath(OUTPUT, ROOT).replace("\\", "/"))
            return 1
        print("CLASS-TABLES CHECK: the table matches the image")
        return 0
    print("dry run: pass --write or --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
