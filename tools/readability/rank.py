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

import audit  # noqa: E402
import lints  # noqa: E402

CALL = re.compile(r"^\s+(BLX?)\s+\|([A-Za-z_][A-Za-z0-9_]*)\|")
EQU = re.compile(r"^\s*\|?([A-Za-z0-9_]+)\|?\s+EQU\s+(0x[0-9A-Fa-f]+)", re.I)
SLICE = re.compile(r"inc_0x([0-9A-Fa-f]+)_0x([0-9A-Fa-f]+)")
RAM = ((audit.EWRAM_START, audit.EWRAM_END), (audit.IWRAM_START, audit.IWRAM_END))
CENSUS = "docs/research/FUNCTION_BOUNDS.csv"


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
    args = parser.parse_args(argv)
    calls, call_sites, ram, ram_sites, slices, slice_sites, named_words = scan()
    starts = population()
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
