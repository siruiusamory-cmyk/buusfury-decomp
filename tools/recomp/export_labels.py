from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import sys

import written

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ENTRY_PC = 0x08000000
INPUTS = os.path.join("docs", "research", "RECOMP_INPUTS.toml")
NAMES = os.path.join("docs", "research", "RECOMP_NAMES.csv")
OUT = os.path.join("docs", "research", "BF_LABELS.toml")
CENSUS = os.path.join("docs", "research", "FUNCTION_BOUNDS.csv")
RUNTIME = os.path.join("docs", "research", "RUNTIME_ENTRIES.csv")
ROM = os.path.join(ROOT, "baserom.gba")
NAME_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")
ADDRESS_FORM = re.compile(r"^(?:sub|loc|dat|unk|g)_[0-9A-F]{8}$")


def blocks(text, kind):
    return text.split("[[%s]]" % kind)[1:]


def field(block, key):
    for line in block.splitlines():
        if line.startswith(key + " = "):
            return line[len(key) + 3:].strip()
    raise SystemExit("a [[functions]] block of %s carries no %s" % (INPUTS, key))


def quotted(text):
    return text.strip('"')


def roots(root=ROOT):
    text = open(os.path.join(root, INPUTS), encoding="ascii", newline="").read()
    out = {}
    for block in blocks(text, "code"):
        addr = int(field(block, "addr"), 16)
        out[addr] = (quotted(field(block, "mode")), addr + int(field(block, "size")))
    for block in blocks(text, "entry"):
        addr = int(field(block, "addr"), 16)
        if addr not in out:
            out[addr] = (quotted(field(block, "mode")), None)
    return out


def interior_blocks(root=ROOT):
    path = os.path.join(root, *CENSUS.split("/"))
    if not os.path.exists(path):
        return frozenset()
    with open(path, newline="", encoding="utf-8") as handle:
        return frozenset(int(row["address"], 16) for row in csv.DictReader(handle)
                         if row["kind"] == "block")


def house(addr, interior=frozenset()):
    return "%s_%08X" % ("loc" if addr in interior else "sub", addr)


def runtime_rows(root=ROOT):
    path = os.path.join(root, *RUNTIME.split("/"))
    if not os.path.exists(path):
        raise SystemExit("no %s, so the labels the runtime recorded would be lost" % RUNTIME)
    out = {}
    with open(path, newline="", encoding="ascii") as handle:
        for number, row in enumerate(csv.DictReader(handle), 2):
            addr = int(row["address"], 16)
            if row["mode"] not in ("arm", "thumb"):
                raise SystemExit("%s:%d gives 0x%08X the mode %r"
                                 % (path, number, addr, row["mode"]))
            if row["provenance"] != "runtime-recorded":
                raise SystemExit("%s:%d gives 0x%08X the provenance %r"
                                 % (path, number, addr, row["provenance"]))
            if addr in out:
                raise SystemExit("%s:%d carries 0x%08X twice" % (path, number, addr))
            out[addr] = row["mode"]
    return out


def names(root=ROOT):
    path = os.path.join(root, NAMES)
    out = {}
    for number, line in enumerate(open(path, encoding="ascii"), 1):
        text = line.strip()
        if not text or text.startswith("address"):
            continue
        parts = text.split(",")
        if len(parts) != 3:
            raise SystemExit("%s:%d is not address,name,evidence_doc" % (path, number))
        addr, name, doc = int(parts[0], 16), parts[1], parts[2]
        if addr in out:
            raise SystemExit("%s:%d names 0x%08X twice" % (path, number, addr))
        if not name or set(name) - NAME_CHARS or not (name[0].isalpha() or name[0] == "_"):
            raise SystemExit("%s:%d has the name %r, which is not an identifier"
                             % (path, number, name))
        if name == house(addr):
            raise SystemExit("%s:%d names 0x%08X with its house name" % (path, number, addr))
        if not os.path.exists(os.path.join(root, *doc.split("/"))):
            raise SystemExit("%s:%d cites %s, which is not in the tree" % (path, number, doc))
        out[addr] = name
    if not out:
        raise SystemExit("%s names nothing" % path)
    if len(set(out.values())) != len(out):
        raise SystemExit("%s carries two rows with the same name" % path)
    return out


def label_set(root=ROOT):
    table = roots(root)
    named = names(root)
    interior = interior_blocks(root)
    for addr, mode in runtime_rows(root).items():
        if addr in table:
            if table[addr][0] != mode:
                raise SystemExit("%s gives 0x%08X the mode %r, and the export gives %r"
                                 % (RUNTIME, addr, mode, table[addr][0]))
            continue
        table[addr] = (mode, None)
    for addr in named:
        if addr not in table:
            raise SystemExit("%s names 0x%08X, which no export entry carries"
                             % (NAMES, addr))
    return [(addr, table[addr][0], table[addr][1], named.get(addr) or house(addr, interior))
            for addr in sorted(table)]


def image_sha256(path=ROM):
    if not os.path.exists(path):
        raise SystemExit("no image at %s, so the label file cannot pin itself" % path)
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def render(root=ROOT, rom=ROM):
    lines = ['format = "gba-labels"', "version = 2", "", "[image]",
             'sha256 = "%s"' % image_sha256(rom)]
    for addr, mode, end, name in label_set(root):
        lines += ["", "[[functions]]", 'name = "%s"' % name,
                  "address = 0x%08x" % addr]
        if end is not None:
            lines.append("end = 0x%08x" % end)
        lines.append('mode = "%s"' % mode)
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="emit the gba-labels v2 file the export and "
                                                 "the tracked name harvest derive")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = render()
    table = label_set()
    named = sum(1 for row in table if not ADDRESS_FORM.match(row[3]))
    print("functions = %d" % len(table))
    print("named = %d" % named)
    print("house named = %d" % (len(table) - named))
    print("interior blocks = %d" % sum(1 for row in table if row[3].startswith("loc_")))
    return written.emit(args, text, os.path.join(ROOT, OUT),
                        "the label file is the one the export and the harvest derive")


if __name__ == "__main__":
    sys.exit(main())
