from __future__ import annotations

import argparse
import csv
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
SITE = re.compile(r"0x(08[0-9A-Fa-f]{6})")
LEDGER = os.path.join("docs", "NAMING_LEDGER.csv")
BOUNDS = os.path.join("docs", "research", "FUNCTION_BOUNDS.csv")
POOL_IMMEDIATE = re.compile(r"\[pc,\s*#(0x[0-9a-f]+|\d+)\]")
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


def steps(rom, row, mode, end=None):
    start, length = row[0], row[1]
    address = ROM_BASE + start
    stop = ROM_BASE + end if end is not None else address + length
    while address < stop:
        found = instruction(rom, address, mode)
        if found is None:
            address += 2 if mode == "thumb" else 4
            continue
        yield found
        address += found.size


def decode_one(rom, address, mode):
    offset = address - ROM_BASE
    if offset < 0 or offset >= len(rom) or (mode == "arm" and address % 4):
        return None
    found = next(iter(ENGINES[mode].disasm(rom[offset:offset + 4], address, count=1)), None)
    if found is None or found.address != address or found.size not in (2, 4):
        return None
    return found


def reachable(rom, start, mode, low, high, limit=4000):
    seen = set()
    queue = [start]
    while queue and len(seen) < limit:
        address = queue.pop()
        while ROM_BASE + low <= address < ROM_BASE + high and address not in seen:
            found = decode_one(rom, address, mode)
            if found is None:
                break
            seen.add(address)
            if found.mnemonic == "bx" or (found.mnemonic.startswith(("pop", "ldm"))
                                          and "pc" in found.op_str):
                break
            target = TARGET.match(found.op_str.split(",")[0].strip()) \
                if found.mnemonic.startswith("b") else None
            if target is not None:
                where = int(target.group(1), 0)
                if ROM_BASE + low <= where < ROM_BASE + high:
                    queue.append(where)
                if found.mnemonic in ("b", "b.w"):
                    break
            address += found.size
    return seen


def function_end(rom, start, mode, low, high):
    seen = reachable(rom, start, mode, low, high)
    if not seen:
        return start
    last = max(seen)
    found = decode_one(rom, last, mode)
    return last + (found.size if found is not None else 2)


def census(root=ROOT):
    path = os.path.join(root, *BOUNDS.split("/"))
    starts, parents = set(), {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            address = int(row["address"], 16)
            if row["kind"] in ("start", "unreferenced"):
                starts.add(address)
            elif row["kind"] == "block" and row.get("parent"):
                parents.setdefault(int(row["parent"], 16), []).append(address)
    return starts, parents


def pool_address(insn, mode):
    match = POOL_IMMEDIATE.search(insn.op_str)
    if match is None:
        return None
    base = (insn.address + 4) & ~3 if mode == "thumb" else insn.address + 8
    return base + int(match.group(1), 0)


def extent(rom, address, row, starts, parents):
    low, high = row[0], row[0] + row[1]
    later = [at for at in starts if address < at < ROM_BASE + high]
    cap = min(later) - ROM_BASE if later else high
    body = set()
    for begin in [address] + parents.get(address, []):
        if low <= begin - ROM_BASE < cap:
            body |= reachable(rom, begin, row[2], low, cap)
    pools = set()
    for at in sorted(body):
        found = decode_one(rom, at, row[2])
        if found is not None and found.mnemonic in LOAD_WIDTH and "[pc" in found.op_str:
            target = pool_address(found, row[2])
            if target is not None:
                pools.update(range(target, target + LOAD_WIDTH[found.mnemonic]))
    return body - pools


def sites(text):
    return sorted({int(found.group(1), 16) for found in SITE.finditer(text)})


def quote(rom, address, mode, count=3):
    parts = []
    for back in range(count, 0, -1):
        found = instruction(rom, address - back * 2, mode)
        if found is not None and found.address + found.size == address:
            parts.append("%08X %s %s" % (found.address, found.mnemonic, found.op_str))
    found = instruction(rom, address, mode)
    parts.append("%08X %s %s" % (found.address, found.mnemonic, found.op_str))
    return " / ".join(parts)


def profile(rom, row, end=None, body=None):
    start, length, mode = row
    words = {}
    found = []
    stream = (decode_one(rom, at, mode) for at in sorted(body)) if body is not None \
        else steps(rom, row, mode, end)
    for insn in stream:
        if insn is None:
            continue
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


def walk(rom, inside=False, root=ROOT):
    starts, parents = census(root)
    out = []
    for row in code_rows():
        body = extent(rom, ROM_BASE + row[0], row, starts, parents) if inside else None
        accesses = profile(rom, row, None, body)
        if accesses:
            out.append((ROM_BASE + row[0], row[1], row[2], accesses))
    return out


def call_to(rom, site, address):
    for mode in ("thumb", "arm"):
        found = decode_one(rom, site, mode)
        if found is not None and found.mnemonic in ("bl", "blx") \
                and found.op_str.startswith("#"):
            return int(found.op_str[1:], 0) == address
    return False


def audit(rom, root=ROOT):
    rows = code_rows()
    starts, parents = census()

    def containing(offset):
        for start, length, mode in rows:
            if start <= offset < start + length:
                return start, length, mode
        return None

    out = []
    path = os.path.join(root, *LEDGER.split("/"))
    with open(path, newline="", encoding="utf-8") as handle:
        for entry in csv.DictReader(handle):
            address = int(entry["address"], 16)
            row = containing(address - ROM_BASE)
            if row is None:
                out.append({"address": entry["address"], "name": entry["new"],
                            "class": entry["evidence_class"], "end": None, "sites": [],
                            "outside": [], "verdict": "NO ROW"})
                continue
            body = extent(rom, address, row, starts, parents)
            end = max(body) + (2 if row[2] == "thumb" else 4) if body else address
            quoted = [site for site in sites(entry["evidence"]) if site != address]
            if entry["evidence_class"] == "caller-role":
                outside = [site for site in quoted if not call_to(rom, site, address)]
            else:
                outside = [site for site in quoted if site not in body]
            out.append({"address": entry["address"], "name": entry["new"],
                        "class": entry["evidence_class"], "end": end, "sites": quoted,
                        "outside": outside, "verdict": "FAIL" if outside else "PASS"})
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
        if address == wanted:
            report(rom, address, mode, length, accesses)
            return
    starts, parents = census()
    for start, length, mode in code_rows():
        if not (start <= wanted - ROM_BASE < start + length):
            continue
        begin = max([at for at in starts if start <= at - ROM_BASE <= wanted - ROM_BASE]
                    or [ROM_BASE + start])
        body = extent(rom, begin, (start, length, mode), starts, parents)
        step = 2 if mode == "thumb" else 4
        report(rom, wanted, mode, max(body) + step - wanted if body else 0,
               profile(rom, (start, length, mode), None, body))
        return


def report(rom, address, mode, length, accesses):
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
                        choices=("dump", "sole", "swi", "register", "function", "footprint",
                                 "audit"))
    args = parser.parse_args(argv)
    rom = read_rom(args.rom)
    if args.mode == "audit":
        for row in audit(rom):
            print("%s %-26s %-20s end=%s sites=%d outside=%s %s"
                  % (row["address"], row["name"], row["class"],
                     "%08X" % row["end"] if row["end"] else "-", len(row["sites"]),
                     ",".join("%08X" % site for site in row["outside"]) or "-",
                     row["verdict"]))
        return 0
    entries = walk(rom, args.mode in ("function", "footprint"))
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
