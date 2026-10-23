from __future__ import annotations

import argparse
import os
import random
import re
import sys

import capstone

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
ALLOW = os.path.join(ROOT, "docs", "research", "FUNCTION_ENTRY_ALLOW.csv")
HEADER = "address,kind,limb,parent"
FLAG_HEADER = "address,kind,limb,flags,entry,reason"
LIMBS = ("call", "vector", "table", "prologue", "unreferenced")
FLAGS = ("data", "undecodable", "clobber")
REASONS = ("prefix", "row-start")
EXPORT = re.compile(r"^\s*EXPORT\s+\|([^|]+)\|\s*$")
ADDRESS_FORM = re.compile(r"^(?:sub|loc|dat|unk|g)_([0-9A-Fa-f]{8})$")
SEED = 716
ARGUMENTS = (0, 1, 2, 3)
SAVES = ("push", "stmdb", "stmfd")
TERMINALS = ("bx", "pop", "b")
WRITES = ("add", "sub", "rsb", "mov", "mvn", "and", "eor", "orr", "bic", "adc", "sbc",
          "mul", "lsl", "lsr", "asr", "ror", "ldr", "ldrb", "ldrh", "ldrsb", "ldrsh")
BASE = SAVES + TERMINALS + WRITES + ("bl",)
ENGINES = {mode: capstone.Cs(capstone.CS_ARCH_ARM, getattr(capstone, "CS_MODE_" + mode.upper()))
           for mode in ("thumb", "arm")}
for _engine in ENGINES.values():
    _engine.detail = True
NAMES = {"r%d" % index: index for index in range(13)}
NAMES.update({"sp": 13, "lr": 14, "pc": 15, "ip": 12})


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


def decoded(rom, address, mode):
    offset = address - ROM_BASE
    if not 0 <= offset <= len(rom) - 4:
        return None
    return next(iter(ENGINES[mode].disasm(bytes(rom[offset:offset + 4]), address, count=1)), None)


def operation(found):
    name = found.mnemonic
    return name[:-1] if name.endswith("s") and name[:-1] in BASE else name


def written(found):
    if operation(found) not in WRITES:
        return set()
    first = found.operands[0]
    name = found.reg_name(first.reg) if first.type == 1 else ""
    return {NAMES[name]} if name in NAMES else set()


def leading(rom, address, mode, limit=8):
    out, at = [], address
    while len(out) < limit:
        found = decoded(rom, at, mode)
        if found is None:
            break
        out.append(found)
        at += found.size
        if operation(found) in SAVES or operation(found) in TERMINALS:
            break
    return out, at


def homed(found, register):
    if operation(found) not in ("add", "mov"):
        return False
    if len(found.operands) < 2:
        return False
    target, source = found.operands[0], found.operands[1]
    if target.type != 1 or source.type != 1:
        return False
    name = found.reg_name(target.reg)
    return (name in NAMES and NAMES[name] in (4, 5, 6, 7)
            and NAMES.get(found.reg_name(source.reg)) == register)


def undecodable(rom, found, mode):
    if not found or mode != "thumb":
        return not found
    for one in found:
        offset = one.address - ROM_BASE
        halfword = int.from_bytes(rom[offset:offset + 2], "little")
        if any(low <= halfword <= high for low, high in export_inputs.THUMB_UNDEFINED):
            return True
        if one.size == 4 and operation(one) != "bl":
            return True
    return False


def clobbered(found, after, rom, mode):
    hit = set()
    for one in found:
        if operation(one) in SAVES or operation(one) in TERMINALS:
            break
        hit |= written(one) & set(ARGUMENTS)
    if not hit or not found or operation(found[-1]) not in SAVES:
        return False
    return any(homed(one, register)
               for one in leading(rom, after, mode, limit=2)[0]
               for register in hit)


def entry_of(rom, address, mode):
    at = address
    for _step in range(6):
        one = decoded(rom, at, mode)
        if one is None:
            return None
        if operation(one) in SAVES and (mode != "thumb" or "lr" in one.op_str):
            return at if at > address else None
        if operation(one) in TERMINALS:
            return None
        at += one.size
    return None


def terminator(rom, address, mode):
    found = decoded(rom, address, mode)
    if found is None or found.address != address:
        return False
    if operation(found) in ("bx", "b"):
        return True
    return operation(found) == "pop" and "pc" in found.op_str


def gap(rom, address, mode, entry):
    if entry is None or mode != "thumb":
        return False
    at = address - 2
    while at >= address - 32:
        found = decoded(rom, at, mode)
        if found is not None:
            if operation(found) in SAVES:
                return False
            if terminator(rom, at, mode):
                return True
        at -= 2
    return False


def proven(root=ROOT):
    path = os.path.join(root, *export_inputs.RUNTIME.split("/"))
    if not os.path.exists(path):
        return set()
    return {address for address, _mode in export_inputs.runtime_labels(root)}


def flag_rows(rom, found, proven_addresses=None):
    rows = []
    if proven_addresses is None:
        proven_addresses = proven()
    for address in sorted(found["starts"]):
        if address in proven_addresses:
            continue
        mode = found["modes"].get(address) or "thumb"
        entry = entry_of(rom, address, mode)
        fired = []
        if gap(rom, address, mode, entry):
            fired.append("data")
        found_leading, after = leading(rom, address, mode)
        if undecodable(rom, found_leading, mode):
            fired.append("undecodable")
        if clobbered(found_leading, after, rom, mode):
            fired.append("clobber")
        if not fired:
            continue
        kind = "unreferenced" if address in found["unreferenced"] else "start"
        rows.append((address, kind, "+".join(found["starts"][address]), "+".join(fired), entry))
    return rows


def flags_text(rows):
    lines = [FLAG_HEADER]
    for address, kind, limb, flags, entry in rows:
        lines.append("0x%08x,%s,%s,%s,%s,%s"
                     % (address, kind, limb, flags,
                        "0x%08x" % entry if entry is not None else "-",
                        "prefix" if entry is not None else "row-start"))
    return "\n".join(lines) + "\n"


def uncarried(current, derived):
    have = {line.split(",")[0] for line in current.splitlines()[1:] if line}
    for line in derived.splitlines()[1:]:
        if line and line.split(",")[0] not in have:
            return line.split(",")[0]
    return None


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
            "blocks": blocks, "unreferenced": unreferenced, "contained": contained,
            "modes": modes}


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


def save(rom, root=ROOT):
    found = census(rom, root)
    text = rows_text(found)
    flags = flags_text(flag_rows(rom, found))
    for name, body in (("FUNCTION_BOUNDS.csv", text), ("FUNCTION_ENTRY_ALLOW.csv", flags)):
        path = os.path.join(root, "docs", "research", name)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(body)
    return found, len(flags.splitlines()) - 1


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
    flags = flags_text(flag_rows(rom, found))
    print("flagged=%d" % (len(flags.splitlines()) - 1))
    if arguments.write:
        with open(BOUNDS, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        with open(ALLOW, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(flags)
        print("wrote %s" % os.path.relpath(BOUNDS, ROOT).replace("\\", "/"))
        print("wrote %s" % os.path.relpath(ALLOW, ROOT).replace("\\", "/"))
        return 0
    if arguments.check:
        current = open(BOUNDS, encoding="utf-8").read() if os.path.exists(BOUNDS) else None
        if current != text:
            print("BOUNDS FAIL: %s is not what the image gives"
                  % os.path.relpath(BOUNDS, ROOT).replace("\\", "/"))
            return 1
        carried = open(ALLOW, encoding="utf-8").read() if os.path.exists(ALLOW) else ""
        missing = uncarried(carried, flags)
        if missing is not None:
            print("BOUNDS FAIL: %s is flagged and not carried in %s"
                  % (missing, os.path.relpath(ALLOW, ROOT).replace("\\", "/")))
            return 1
        if carried != flags:
            print("BOUNDS FAIL: %s is not what the image gives"
                  % os.path.relpath(ALLOW, ROOT).replace("\\", "/"))
            return 1
        print("BOUNDS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
