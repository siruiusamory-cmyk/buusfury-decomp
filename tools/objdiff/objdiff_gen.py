from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LEDGER = os.path.join(ROOT, "work", "ledger.csv")
CONFIG = os.path.join(ROOT, "objdiff.json")
TARGETS = "build/objdiff/target"
ROM = os.path.join(ROOT, "baserom.gba")
SYMBOLS = "build/output/symbols.json"
BUILD = "rebuild.cmd"
SCHEMA = "https://raw.githubusercontent.com/encounter/objdiff/main/config.schema.json"
ASM = {"b": "asm/buu.s", "G": "asm/GBARam.s", "r": "asm/rest_of_the_game.s"}
INCBIN = re.compile(r"INCBIN\s+baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted")
SLICE = re.compile(r"slice_([0-9a-fA-F]+)\.s$")
COMPILED = re.compile(r"src/[^\s\"]+\.(?:c|cpp)\b")
CODE = ("t", "a")
KINDS = {"thumb": "t", "arm": "a", "data": "d"}
CATEGORIES = ({"id": "code", "name": "Code"}, {"id": "data", "name": "Data"})


def ledger(path=LEDGER):
    rows = []
    for line in open(path, encoding="ascii"):
        parts = line.strip().split(",")
        if len(parts) < 8:
            continue
        rows.append((int(parts[0], 16), int(parts[1]), parts[2], parts[3], parts[4],
                     parts[5], parts[6], int(parts[7])))
    return rows


def slices(root=ROOT):
    found = set()
    for name in sorted(os.listdir(os.path.join(root, "asm"))):
        if not name.endswith(".s"):
            continue
        text = open(os.path.join(root, "asm", name), encoding="ascii", errors="replace").read()
        for match in INCBIN.finditer(text):
            found.add((int(match.group(1), 16), int(match.group(2), 16), "asm/" + name))
    return sorted(found)


def slice_file(root, offset):
    starts = []
    for name in os.listdir(os.path.join(root, "asm")):
        match = SLICE.search(name)
        if match:
            starts.append((int(match.group(1), 16), "asm/" + name))
    starts.sort()
    chosen = None
    for start, name in starts:
        if start <= offset:
            chosen = name
    return chosen


def folder(row, root):
    offset, _length, _isa, _region, source, kind = row[:6]
    if kind == "g":
        return ASM["r"]
    if source == "s":
        return slice_file(root, offset)
    return ASM[source]


def name_of(row, root):
    _offset, _length, _isa, region, source, kind = row[:6]
    if kind == "g":
        return "data/generated/" + region
    if source == "s":
        return "asm/slices/" + region
    return "asm/" + os.path.basename(ASM[source]).rsplit(".", 1)[0] + "/" + region


def elf(sections):
    names = [""] + [section[0] for section in sections] + [".symtab", ".strtab", ".shstrtab"]
    offsets = {}
    shstr = b""
    for name in names:
        offsets[name] = len(shstr)
        shstr += name.encode("ascii") + b"\0"
    strtab = b"\0"
    locals_ = []
    globals_ = []
    for index, (_name, _flags, _payload, symbols) in enumerate(sections):
        for symbol, offset, _size, isa in symbols:
            mapping = "$" + isa
            strtab += mapping.encode("ascii") + b"\0"
            locals_.append(struct.pack("<IIIBBH", len(strtab) - len(mapping) - 1, offset, 0,
                                       0x00, 0, index + 1))
        for symbol, offset, size, isa in symbols:
            strtab += symbol.encode("ascii") + b"\0"
            kind = 0x12 if isa in CODE else 0x11
            globals_.append(struct.pack("<IIIBBH", len(strtab) - len(symbol) - 1, offset, size,
                                        kind, 0, index + 1))
    symtab = struct.pack("<IIIBBH", 0, 0, 0, 0, 0, 0) + b"".join(locals_) + b"".join(globals_)
    body = b""
    payload_offsets = []
    position = 52
    for _name, _flags, payload, _symbols in sections:
        payload_offsets.append(position)
        padded = payload + b"\0" * ((-len(payload)) % 4)
        body += padded
        position += len(padded)
    off_symtab = position
    off_strtab = off_symtab + len(symtab)
    off_shstr = off_strtab + len(strtab)
    shoff = (off_shstr + len(shstr) + 3) & ~3
    count = len(sections)
    headers = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]
    for index, (name, flags, payload, _symbols) in enumerate(sections):
        headers.append((offsets[name], 1, flags, 0, payload_offsets[index], len(payload), 0, 0, 4, 0))
    headers.append((offsets[".symtab"], 2, 0, 0, off_symtab, len(symtab), count + 2,
                   1 + len(locals_), 4, 16))
    headers.append((offsets[".strtab"], 3, 0, 0, off_strtab, len(strtab), 0, 0, 1, 0))
    headers.append((offsets[".shstrtab"], 3, 0, 0, off_shstr, len(shstr), 0, 0, 1, 0))
    header = struct.pack("<16sHHIIIIIHHHHHH", b"\x7fELF\x01\x01\x01" + b"\0" * 9,
                         1, 40, 1, 0, 0, shoff, 0x02000000, 52, 32, 0, 40, count + 4, count + 3)
    blob = header + body + symtab + strtab + shstr
    blob += b"\0" * (shoff - len(blob))
    return blob + b"".join(struct.pack("<IIIIIIIIII", *row) for row in headers)


def headers(path):
    data = open(path, "rb").read()
    shoff = struct.unpack_from("<I", data, 32)[0]
    shnum, shstrndx = struct.unpack_from("<HH", data, 48)
    sections = [struct.unpack_from("<IIIIIIIIII", data, shoff + index * 40)
                for index in range(shnum)]
    stroff = sections[shstrndx][4]
    strings = data[stroff:stroff + sections[shstrndx][5]]
    out = []
    for section in sections:
        end = strings.find(b"\0", section[0])
        out.append((strings[section[0]:end].decode("ascii", "replace"), section[2], section[1]))
    return out


def defined(path):
    data = open(path, "rb").read()
    shoff = struct.unpack_from("<I", data, 32)[0]
    shnum = struct.unpack_from("<H", data, 48)[0]
    sections = [struct.unpack_from("<IIIIIIIIII", data, shoff + index * 40)
                for index in range(shnum)]
    out = []
    for section in sections:
        if section[1] != 2:
            continue
        offset, table, link, entsize = section[4], section[5], section[6], section[9]
        stroff = sections[link][4]
        for entry in range(table // entsize):
            name_offset, value, size, info, _other, shndx = struct.unpack_from(
                "<IIIBBH", data, offset + entry * entsize)
            end = data.find(b"\0", stroff + name_offset)
            name = data[stroff + name_offset:end].decode("ascii", "replace")
            if shndx and size and (info & 0xf) in (1, 2):
                out.append((name, shndx, value, size))
    return sorted(out, key=lambda item: (item[1], item[2], item[0]))


def image_symbols(root=ROOT):
    data = json.load(open(os.path.join(root, SYMBOLS), encoding="ascii"))
    out = {}
    for row in data["symbols"]:
        size = row.get("size") or 0
        address = int(row["address"], 16) - 0x08000000
        if size and address >= 0:
            out[row["name"]] = (address, KINDS.get(row["kind"], "d"))
    return out


def compiled(root=ROOT):
    text = open(os.path.join(root, BUILD), encoding="ascii", errors="replace").read()
    return sorted(set(COMPILED.findall(text)))


def build(root=ROOT):
    units = []
    taken = set()
    for row in sorted(ledger(os.path.join(root, "work", "ledger.csv")), key=lambda row: row[3]):
        offset, length, isa, region, source, _kind = row[:6]
        taken.add((offset, length))
        if source.startswith("src/"):
            continue
        category = "code" if isa in CODE else "data"
        _source_path = folder(row, root)
        name = name_of(row, root)
        unit = {"name": name, "target_path": TARGETS + "/" + name + ".o",
                "metadata": {"source_path": _source_path, "complete": False,
                             "progress_categories": [category]},
                "options": {"arm_arch_version": "v4t"}}
        units.append((unit, ("row", region, isa, offset, length)))
    for start, end, source_path in slices(root):
        if (start, end - start) in taken:
            continue
        name = "data/incbin/%06x_%06x" % (start, end)
        unit = {"name": name, "target_path": TARGETS + "/" + name + ".o",
                "metadata": {"source_path": source_path, "complete": False,
                             "progress_categories": ["data"]},
                "options": {"arm_arch_version": "v4t"}}
        units.append((unit, ("row", "incbin_%06x_%06x" % (start, end), "d", start, end - start)))
    addresses = image_symbols(root)
    for source in compiled(root):
        stem = os.path.basename(source).rsplit(".", 1)[0]
        base = "build/" + stem + ".o"
        symbols = defined(os.path.join(root, base))
        if not symbols:
            raise SystemExit("%s defines no sized symbol" % base)
        groups = {}
        for name, index, _value, size in symbols:
            if name not in addresses:
                continue
            address, isa = addresses[name]
            groups.setdefault(index, []).append((name, address, size, isa))
        if not groups:
            raise SystemExit("%s has no address in %s" % (base, SYMBOLS))
        isas = {symbol[3] for group in groups.values() for symbol in group}
        unit = {"name": "src/" + stem, "target_path": TARGETS + "/src/" + stem + ".o",
                "base_path": base,
                "metadata": {"source_path": source, "complete": True,
                             "progress_categories": ["code" if isas & set(CODE) else "data"]},
                "options": {"arm_arch_version": "v4t"}}
        ordered = [(index, groups[index]) for index in sorted(groups)]
        units.append((unit, ("sections", base, ordered)))
    units.sort(key=lambda item: item[0]["name"])
    config = {"$schema": SCHEMA, "units": [item[0] for item in units],
              "progress_categories": list(CATEGORIES)}
    return config, units


def write_targets(units, rom):
    image = open(rom, "rb").read()
    for unit, recipe in units:
        if recipe[0] == "row":
            _kind, symbol, isa, offset, length = recipe
            payload = image[offset:offset + length]
            if len(payload) != length:
                raise SystemExit("%s runs past the image at 0x%x" % (symbol, offset))
            sections = [(".text" if isa in CODE else ".data", 0x6 if isa in CODE else 0x2,
                         payload, [(symbol, 0, length, isa)])]
        else:
            _kind, base, groups = recipe
            table = headers(os.path.join(ROOT, base))
            sections = []
            for index, symbols in groups:
                name, flags, _type = table[index]
                low = min(address for _n, address, _s, _i in symbols)
                high = max(address + size for _n, address, size, _i in symbols)
                payload = image[low:high]
                if len(payload) != high - low:
                    raise SystemExit("%s runs past the image at 0x%x" % (unit["name"], low))
                sections.append((name, flags, payload,
                                 [(symbol, address - low, size, isa)
                                  for symbol, address, size, isa in symbols]))
        path = os.path.join(ROOT, unit["target_path"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(elf(sections))


def coverage(units):
    code = data = 0
    for _unit, recipe in units:
        if recipe[0] == "row":
            _kind, _symbol, isa, _offset, length = recipe
            if isa in CODE:
                code += length
            else:
                data += length
        else:
            for _index, symbols in recipe[2]:
                for _name, _address, size, isa in symbols:
                    if isa in CODE:
                        code += size
                    else:
                        data += size
    return code, data


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=ROM)
    parser.add_argument("--targets", action="store_true")
    parser.add_argument("--config", default=CONFIG)
    args = parser.parse_args(argv)
    config, units = build()
    with open(args.config, "w", encoding="ascii", newline="\n") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")
    code, data = coverage(units)
    print("units=%d code_bytes=%d data_bytes=%d" % (len(units), code, data))
    if args.targets:
        if not os.path.exists(args.rom):
            raise SystemExit("no image at %s" % args.rom)
        write_targets(units, args.rom)
        print("target objects written under %s" % TARGETS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
