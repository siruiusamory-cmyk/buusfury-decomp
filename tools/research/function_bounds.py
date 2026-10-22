from __future__ import annotations

import argparse
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recomp"))
sys.path.insert(0, HERE)

import export_inputs
import lints
import name_evidence
import romfile

ROM_BASE = 0x08000000
ROM_SHA256 = name_evidence.ROM_SHA256
BOUNDS = os.path.join(ROOT, "docs", "research", "FUNCTION_BOUNDS.csv")
HEADER = "address,kind,limb,parent"
LIMBS = ("call", "vector", "table", "prologue", "unreferenced")
EXPORT = re.compile(r"^\s*EXPORT\s+\|([^|]+)\|\s*$")
ADDRESS_FORM = re.compile(r"^(?:sub|loc|dat|unk|g)_([0-9A-Fa-f]{8})$")
SEED = 716


def exports(root=ROOT):
    out = {}
    named = lints.label_addresses()
    folder = os.path.join(root, "asm")
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".s"):
            continue
        for line in open(os.path.join(folder, name), encoding="ascii", errors="replace"):
            found = EXPORT.match(line)
            if not found:
                continue
            digits = ADDRESS_FORM.match(found.group(1))
            if digits is not None:
                out[int(digits.group(1), 16)] = found.group(1)
            elif found.group(1) in named:
                out[named[found.group(1)]] = found.group(1)
    return out


def prologue(rom, address, mode):
    found = name_evidence.decode_one(rom, address, mode)
    if found is None:
        return False
    if mode == "thumb":
        return found.mnemonic == "push" and "lr" in found.op_str
    return found.mnemonic in ("push", "stmdb", "stmfd") and "lr" in found.op_str


def row_of(address, rows):
    low, high = 0, len(rows)
    while low < high:
        middle = (low + high) // 2
        if rows[middle][0] <= address:
            low = middle + 1
        else:
            high = middle
    if low == 0:
        return None
    begin, end, mode = rows[low - 1]
    return (begin, end, mode) if address < end else None


def classify(rom, entries, modes, rows, calls, table, vectors, spans=()):
    rows = [(row[0], row[1], row[2] if len(row) > 2 else "thumb") for row in rows]
    spans = set(spans)
    entries = set(entries) | spans
    if entries and not any(ROM_BASE <= address < ROM_BASE + len(rom) for address in entries):
        raise SystemExit("no candidate lies inside the image, so the address space is wrong")
    limbs_of, bodies, ends, unreferenced = {}, {}, {}, set()
    for address in sorted(entries):
        row = row_of(address, rows)
        if row is None:
            continue
        begin, end, row_mode = row
        mode = modes.get(address) or row_mode
        limbs = []
        if address in calls:
            limbs.append("call")
        if address in vectors:
            limbs.append("vector")
        if address in table:
            limbs.append("table")
        if prologue(rom, address, mode):
            limbs.append("prologue")
        if not limbs and address not in spans:
            continue
        seen = name_evidence.reachable(rom, address, mode, begin - ROM_BASE, end - ROM_BASE)
        if not seen and address not in spans:
            continue
        limbs_of[address] = limbs
        bodies[address] = seen
        if seen:
            ends[address] = max(seen)
        if not limbs:
            unreferenced.add(address)
    starts, contained = {}, 0
    for address in sorted(limbs_of):
        if address not in spans and "prologue" not in limbs_of[address]:
            if any(address in bodies[start] for start in starts if limbs_of[start]):
                contained += 1
                continue
        starts[address] = limbs_of[address]
    blocks = {}
    for address in sorted(entries):
        row = row_of(address, rows)
        if address in starts or row is None:
            continue
        earlier = [start for start in starts
                   if row_of(start, rows) is not None and row_of(start, rows)[0] == row[0]
                   and start < address]
        if earlier:
            blocks[address] = max(earlier)
    return {"entries": sorted(entries), "starts": starts, "bodies": bodies, "ends": ends,
            "blocks": blocks, "unreferenced": unreferenced, "contained": contained}


def describe(rom, root=ROOT):
    code_rows = export_inputs.code_rows(root)
    rows = [(ROM_BASE + off, ROM_BASE + off + length, mode)
            for off, length, mode in code_rows]
    entries = exports(root)
    modes = {}
    for address in entries:
        row = row_of(address, rows)
        if row is not None:
            modes[address] = row[2]
    copy_rows, _blocks = export_inputs.copies(root)
    tables = export_inputs.jump_tables(rom)
    bounds = {}
    for off, length, mode in code_rows:
        for position in range(off, off + length, 2):
            bounds[position] = mode
    _words, _raw, accepted = export_inputs.address_taken(rom, bounds, code_rows,
                                                         tables, copy_rows)
    table = set()
    for low, stride, count in tables:
        for index in range(count):
            at = low + stride * index
            table.add(ROM_BASE + at
                      + int.from_bytes(rom[at:at + 4], "little", signed=True) - 1)
    table.update(ROM_BASE + off for off in accepted)
    calls = set(ROM_BASE + off for off in export_inputs.call_targets(rom, code_rows))
    spans = set(ROM_BASE + off for off, _length, _mode in code_rows)
    return classify(rom, entries, modes, rows, calls, table, {ROM_BASE}, spans=spans)


def census(rom, root=ROOT):
    return describe(rom, root)


def counts(found):
    by_limb = {}
    for address in found["starts"]:
        for limb in found["starts"][address]:
            by_limb[limb] = by_limb.get(limb, 0) + 1
    by_limb["unreferenced"] = len(found["unreferenced"])
    return {"entries": len(found["entries"]), "starts": len(found["starts"]),
            "blocks": len(found["blocks"]), "contained": found["contained"],
            "by_limb": by_limb}


def rows_text(found):
    lines = [HEADER]
    for address in found["entries"]:
        if address in found["starts"]:
            limbs = found["starts"][address]
            if limbs:
                lines.append("0x%08x,start,%s," % (address, "+".join(limbs)))
            else:
                lines.append("0x%08x,unreferenced,," % address)
        elif address in found["blocks"]:
            lines.append("0x%08x,block,,0x%08x" % (address, found["blocks"][address]))
    return "\n".join(lines) + "\n"


def sample_text(rom, found, count=10):
    lines = ["address,parent,limb"]
    for address in sorted(random.Random(SEED).sample(sorted(found["blocks"]), count)):
        parent = found["blocks"][address]
        lines.append("0x%08x,0x%08x,%s" % (address, parent,
                                           "+".join(found["starts"][parent])))
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Which exported address is a function start and which is an interior block.")
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--sample", type=int, default=0)
    arguments = parser.parse_args(argv)
    if not os.path.exists(arguments.rom):
        print("the census needs the retail image at %s" % arguments.rom)
        return 1
    rom = romfile.read_rom(arguments.rom, ROM_SHA256)
    found = census(rom)
    tally = counts(found)
    print("entries=%d starts=%d blocks=%d contained=%d"
          % (tally["entries"], tally["starts"], tally["blocks"], tally["contained"]))
    print("by_limb " + " ".join("%s=%d" % (limb, tally["by_limb"].get(limb, 0))
                                for limb in LIMBS))
    if arguments.sample:
        for line in sample_text(rom, found, arguments.sample):
            print(line)
        return 0
    text = rows_text(found)
    if arguments.write:
        with open(BOUNDS, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        print("wrote %s" % os.path.relpath(BOUNDS, ROOT).replace("\\", "/"))
        return 0
    if arguments.check:
        current = open(BOUNDS, encoding="utf-8").read() if os.path.exists(BOUNDS) else None
        if current != text:
            print("BOUNDS FAIL: %s is not what the image gives"
                  % os.path.relpath(BOUNDS, ROOT).replace("\\", "/"))
            return 1
        print("BOUNDS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
