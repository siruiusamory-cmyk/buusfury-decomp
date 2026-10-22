from __future__ import annotations

import argparse
import collections
import csv
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lint"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "research"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recomp"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "behaviour"))

import audit
import capstone
import harness
import lints
import name_evidence
import romfile

CALL = re.compile(r"^\s+(BLX?)\s+\|([A-Za-z_][A-Za-z0-9_]*)\|")
EQU = re.compile(r"^\s*\|?([A-Za-z0-9_]+)\|?\s+EQU\s+(0x[0-9A-Fa-f]+)", re.I)
SLICE = re.compile(r"inc_0x([0-9A-Fa-f]+)_0x([0-9A-Fa-f]+)")
RAM = ((audit.EWRAM_START, audit.EWRAM_END), (audit.IWRAM_START, audit.IWRAM_END))
CENSUS = "docs/research/FUNCTION_BOUNDS.csv"
ENGINE = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
ENGINE.detail = True
LOADS = ("ldr", "ldrb", "ldrh", "ldrsb", "ldrsh")
STORES = ("str", "strb", "strh")
REGISTERS = {"r%d" % index: index for index in range(13)}


def word(image, address):
    offset = address - 0x08000000
    if not 0 <= offset <= len(image) - 4:
        return None
    return int.from_bytes(image[offset:offset + 4], "little")


def instruction(image, at):
    offset = at - 0x08000000
    if at % 2 or not 0 <= offset <= len(image) - 2:
        return None
    return next(iter(ENGINE.disasm(bytes(image[offset:offset + 4]), at, count=1)), None)


def pointer_sites(image, starts):
    slots = {}
    for start in starts:
        try:
            allowed = harness.body(image, start)
        except ValueError:
            continue
        held = {}
        for at in sorted(allowed):
            found = instruction(image, at)
            if found is None:
                continue
            if found.mnemonic == "ldr" and found.operands and \
                    found.operands[1].type == capstone.arm.ARM_OP_MEM and \
                    found.operands[1].mem.base == capstone.arm.ARM_REG_PC:
                pool = ((at + 4) & ~3) + found.operands[1].mem.disp
                value = word(image, pool)
                target = REGISTERS.get(found.reg_name(found.operands[0].reg))
                if target is None:
                    continue
                if value is not None and any(audit.band(value, low, high) for low, high in RAM):
                    held[target] = (value, "slot")
                else:
                    held.pop(target, None)
                continue
            operands = found.operands
            if found.mnemonic in LOADS + STORES and len(operands) > 1 and \
                    operands[1].type == capstone.arm.ARM_OP_MEM and operands[1].mem.base:
                base = REGISTERS.get(found.reg_name(operands[1].mem.base))
                target = REGISTERS.get(found.reg_name(operands[0].reg)) \
                    if operands[0].type == capstone.arm.ARM_OP_REG else None
                kind = held.get(base)
                if kind is not None:
                    slot, level = kind
                    offset = operands[1].mem.disp
                    entry = slots.setdefault(slot, {"fields": collections.Counter(),
                                                    "loads": collections.Counter(),
                                                    "starts": collections.Counter(),
                                                    "sites": collections.defaultdict(list)})
                    if level == "struct" or found.mnemonic in STORES:
                        entry["fields"][offset] += 1
                        entry["starts"][start] += 1
                        if len(entry["sites"][offset]) < 2:
                            entry["sites"][offset].append("%08X %s %s"
                                                          % (at, found.mnemonic, found.op_str))
                    else:
                        entry["loads"][offset] += 1
                    if found.mnemonic in LOADS and target is not None:
                        held[target] = (slot, "struct")
                    continue
            for operand in operands:
                if operand.type == capstone.arm.ARM_OP_REG and operand.reg in range(13):
                    held.pop(REGISTERS.get(found.reg_name(operand.reg)), None)
    return slots


def bases(image, starts, top, named_words=None):
    slots = pointer_sites(image, starts)
    named_words = named_words or {}
    ranked = sorted(((slot, entry) for slot, entry in slots.items() if slot not in named_words),
                    key=lambda item: (-sum(item[1]["fields"].values()), item[0]))
    print("bases distinct=%d field-sites=%d named=%d"
          % (len(slots), sum(sum(entry["fields"].values()) for entry in slots.values()),
             len(named_words)))
    for slot, entry in ranked[:top]:
        fields = " ".join("+0x%X:%d" % (offset, count) for offset, count in
                          sorted(entry["fields"].items(), key=lambda item: -item[1]))
        print("  0x%08X sites=%d fields=%d functions=%d | %s"
              % (slot, sum(entry["fields"].values()), len(entry["fields"]),
                 len(entry["starts"]), fields))
        for offset, count in sorted(entry["fields"].items(), key=lambda item: -item[1])[:2]:
            print("    +0x%X %s" % (offset, " ; ".join(entry["sites"][offset])))
    return ranked


def scan():
    calls = collections.Counter()
    call_sites = collections.defaultdict(list)
    ram = collections.Counter()
    ram_sites = collections.defaultdict(list)
    slices = collections.Counter()
    slice_sites = collections.defaultdict(list)
    named_words = {}
    for name in audit.tracked(".s") + audit.tracked(".inc"):
        if not name.startswith(audit.ASM):
            continue
        for number, line in enumerate(audit.read(name).splitlines(), 1):
            found = EQU.match(line)
            if found:
                value = int(found.group(2), 16)
                if any(audit.band(value, start, end) for start, end in RAM):
                    if not audit.ADDRESS_NAME.match(found.group(1)):
                        named_words[value] = found.group(1)
                continue
            found = CALL.match(line)
            if found:
                digits = audit.ADDRESS_NAME.match(found.group(2))
                if digits:
                    address = int(found.group(2).split("_")[1], 16)
                    calls[address] += 1
                    if len(call_sites[address]) < 3:
                        call_sites[address].append("%s:%d %s" % (name, number, line.strip()))
            for token in SLICE.finditer(line):
                key = (int(token.group(1), 16), int(token.group(2), 16))
                slices[key] += 1
                if len(slice_sites[key]) < 3:
                    slice_sites[key].append("%s:%d %s" % (name, number, line.strip()))
            for match in audit.HEX.finditer(line):
                value = int(match.group(0), 16)
                if not any(audit.band(value, start, end) for start, end in RAM):
                    continue
                ram[value] += 1
                if len(ram_sites[value]) < 3:
                    ram_sites[value].append("%s:%d %s" % (name, number, line.strip()))
    return calls, call_sites, ram, ram_sites, slices, slice_sites, named_words


def population():
    rows = list(csv.DictReader(io.StringIO(audit.read(CENSUS))))
    return sorted(int(row["address"], 16) for row in rows
                  if row.get("kind") in ("start", "unreferenced"))


def named(starts):
    symbols = lints.export_symbols()
    exports = symbols[0] if symbols else []
    addresses = lints.label_addresses()
    library = lints.library_symbols()
    names = collections.defaultdict(set)
    for name, address in addresses.items():
        names[address].add(name)
    for name, _path, _line in exports:
        address = lints.symbol_address(name, addresses)
        if address is not None:
            names[address].add(name)
    return {start for start in starts
            if any(lints.FUNCTION_NAME.match(name) or name in library
                   for name in names.get(start, ()))}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Rank the address-named population by the number "
                                                 "of places a reader meets it.")
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--rom", default=os.path.join(os.path.dirname(os.path.dirname(HERE)),
                                                      "baserom.gba"))
    parser.add_argument("--bases", action="store_true",
                        help="rank the RAM base pointers by the fields a reader meets through them")
    args = parser.parse_args(argv)
    starts = population()
    if args.bases:
        image = romfile.read_rom(args.rom, name_evidence.ROM_SHA256)
        bases(image, starts, args.top, scan()[6])
        return 0
    calls, call_sites, ram, ram_sites, slices, slice_sites, named_words = scan()
    named_addresses = named(starts)
    candidates = [address for address in starts if address not in named_addresses]
    print("functions starts=%d named=%d address-named=%d call-sites=%d"
          % (len(starts), len(named_addresses), len(candidates), sum(calls.values())))
    for address in sorted(candidates, key=lambda item: (-calls[item], item))[:args.top]:
        print("  0x%08X callers=%d asm/sub_%08X.s | %s"
              % (address, calls[address], address, " ; ".join(call_sites[address]) or "-"))
    words = [(address, count) for address, count in ram.items() if address not in named_words]
    print("ram refs=%d distinct=%d named-words=%d address-named=%d"
          % (sum(ram.values()), len(ram), len(named_words), len(words)))
    for address, count in sorted(words, key=lambda item: (-item[1], item[0]))[:args.top]:
        print("  0x%08X refs=%d | %s" % (address, count, " ; ".join(ram_sites[address])))
    print("tables distinct=%d references=%d" % (len(slices), sum(slices.values())))
    for key, count in sorted(slices.items(), key=lambda item: (-item[1], item[0]))[:args.top]:
        print("  inc_0x%08X_0x%08X refs=%d | %s"
              % (key[0], key[1], count, " ; ".join(slice_sites[key])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
