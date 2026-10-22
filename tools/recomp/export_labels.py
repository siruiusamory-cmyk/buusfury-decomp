from __future__ import annotations

import argparse
import hashlib
import os
import sys

import written

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ENTRY_PC = 0x08000000
INPUTS = os.path.join("docs", "research", "RECOMP_INPUTS.toml")
NAMES = os.path.join("docs", "research", "RECOMP_NAMES.csv")
OUT = os.path.join("docs", "research", "BF_LABELS.toml")
ROM = os.path.join(ROOT, "baserom.gba")
NAME_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")


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


def house(addr):
    return "sub_%08X" % addr


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
        if not name or set(name) - NAME_CHARS or not name[0].isalpha():
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
    for addr in named:
        if addr not in table:
            raise SystemExit("%s names 0x%08X, which no export entry carries"
                             % (NAMES, addr))
    return [(addr, table[addr][0], table[addr][1], named.get(addr) or house(addr))
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
    named = sum(1 for row in table if not row[3].startswith("sub_"))
    print("functions = %d" % len(table))
    print("named = %d" % named)
    print("house named = %d" % (len(table) - named))
    return written.emit(args, text, os.path.join(ROOT, OUT),
                        "the label file is the one the export and the harvest derive")


if __name__ == "__main__":
    sys.exit(main())
