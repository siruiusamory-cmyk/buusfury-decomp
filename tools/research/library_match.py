from __future__ import annotations

import argparse
import csv
import io
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
AR_MAGIC = b"!<arch>\n"
ARM_MACHINE = 40
TEXT = 1
REL = 9
SYMTAB = 2
EXECUTABLE = 0x4
GLOBAL = 1
WORD_FIELD = (2, 3)
BRANCH_FIELD = (1, 28, 29)
CALL_FIELD = (10, 30)
NARROW_FIELD = {5: 2, 6: 2, 8: 1}
ANCHOR = 8
MINIMUM = 8
ROM_BASE = 0x08000000
ROM = os.path.join(ROOT, "baserom.gba")
LEDGER = os.path.join("docs", "NAMING_LEDGER.csv")
ASM = "asm"
CLASS = "toolchain-library"
EXPORT = re.compile(r"^\s*EXPORT\s+\|([^|]+)\|\s*$")
ADDRESS_NAME = re.compile(r"^sub_([0-9A-Fa-f]{8})$")


def members(blob):
    found = []
    at = len(AR_MAGIC)
    while at + 60 <= len(blob):
        header = blob[at:at + 60]
        name = header[:16].decode("latin-1").strip()
        size = int(header[48:58].decode("latin-1").strip())
        start = at + 60
        if name not in ("/", "//", "/SYM64/"):
            found.append((name, blob[start:start + size]))
        at = start + size + (size % 2)
    return found


def fields(relocations):
    masked = set()
    for offset, kind in relocations:
        if kind in WORD_FIELD:
            masked.update(range(offset, offset + 4))
        elif kind in BRANCH_FIELD:
            masked.update(range(offset + 1, offset + 4))
        elif kind in CALL_FIELD:
            masked.update(range(offset, offset + 4))
        elif kind in NARROW_FIELD:
            masked.update(range(offset, offset + NARROW_FIELD[kind]))
    return masked


def same(left, right, masked):
    if len(left) != len(right):
        return False
    return all(True if index in masked else left[index] == right[index]
               for index in range(len(left)))


def anchor_of(masked, length):
    for index in range(0, max(length - ANCHOR + 1, 0)):
        if not any(index + step in masked for step in range(ANCHOR)):
            return index
    return None


def matches(text, masked, rom, entries, base, anchor=None):
    if anchor is None:
        anchor = anchor_of(masked, len(text))
    if anchor is None:
        return []
    pattern = text[anchor:anchor + ANCHOR]
    found = []
    for address in entries:
        at = address - base + anchor
        if at < 0 or at + ANCHOR > len(rom) or rom[at:at + ANCHOR] != pattern:
            continue
        start = address - base
        if same(text, rom[start:start + len(text)], masked):
            found.append(address)
    return found


def sections_of(blob):
    if blob[:4] != b"\x7fELF" or struct.unpack_from("<H", blob, 18)[0] != ARM_MACHINE:
        return None
    table = struct.unpack_from("<I", blob, 0x20)[0]
    size, count = struct.unpack_from("<HH", blob, 0x2E)
    found = []
    for index in range(count):
        at = table + index * size
        _name, kind, flags = struct.unpack_from("<III", blob, at)
        body = struct.unpack_from("<I", blob, at + 16)[0]
        length = struct.unpack_from("<I", blob, at + 20)[0]
        link, info = struct.unpack_from("<II", blob, at + 24)
        found.append({"kind": kind, "flags": flags, "body": body, "size": length,
                      "link": link, "info": info})
    return found


def member(blob):
    sections = sections_of(blob)
    if sections is None:
        return None
    text_index = None
    for index, section in enumerate(sections):
        if section["kind"] == TEXT and section["flags"] & EXECUTABLE:
            text_index = index
            break
    if text_index is None:
        return None
    text = blob[sections[text_index]["body"]:sections[text_index]["body"]
                + sections[text_index]["size"]]
    relocations = []
    symbols = []
    for section in sections:
        if section["kind"] == REL and section["info"] == text_index:
            for at in range(section["body"], section["body"] + section["size"], 8):
                offset, info = struct.unpack_from("<II", blob, at)
                relocations.append((offset, info & 0xFF))
        if section["kind"] == SYMTAB and section["link"] < len(sections):
            strings = sections[section["link"]]
            for at in range(section["body"], section["body"] + section["size"], 16):
                name, value, _size, info, _other, index = struct.unpack_from(
                    "<IIIBBH", blob, at)
                if index != text_index or info >> 4 != GLOBAL:
                    continue
                end = blob.find(b"\0", strings["body"] + name)
                symbols.append((value, blob[strings["body"] + name:end].decode("latin-1")))
    return text, relocations, symbols


def exported(symbols):
    for value, name in symbols:
        if value == 0 and name:
            return name
    return None


def library_files(directory):
    def preference(path):
        name = os.path.basename(path)
        return (0 if name == "c_t__un.l" else 1 if name.startswith("c_t_") else 2, name)
    return sorted((os.path.join(directory, name) for name in os.listdir(directory)
                   if name.endswith(".l")), key=preference)


def ledger_rows(root=ROOT):
    with open(os.path.join(root, *LEDGER.split("/")), newline="", encoding="utf-8") as handle:
        return [row for row in csv.DictReader(handle)
                if row.get("address") and row.get("old") and row.get("new")]


def entries(root=ROOT):
    out = {}
    exported_names = set()
    folder = os.path.join(root, ASM)
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".s"):
            continue
        for line in open(os.path.join(folder, name), encoding="ascii", errors="replace"):
            found = EXPORT.match(line)
            if found is None:
                continue
            exported_names.add(found.group(1))
            digits = ADDRESS_NAME.match(found.group(1))
            if digits:
                out[int(digits.group(1), 16)] = found.group(1)
    for row in ledger_rows(root):
        if row["new"] in exported_names:
            out[int(row["address"], 16)] = row["new"]
    return out


def census(directory, rom, entries, base):
    rows = []
    for path in library_files(directory):
        blob = open(path, "rb").read()
        for name, body in members(blob):
            parsed = member(body)
            if parsed is None:
                continue
            text, relocations, symbols = parsed
            label = exported(symbols)
            if not label or len(text) < MINIMUM:
                continue
            masked = fields(relocations)
            for address in matches(text, masked, rom, entries, base):
                rows.append((address, os.path.basename(path), name.strip("/"), label,
                             len(text), len(masked), len(text) - len(masked),
                             tuple(sorted(masked))))
    return sorted(rows)


def renamed(text, old, new):
    return text.replace("|%s|" % old, "|%s|" % new)


def row_text(cells):
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="").writerow(cells)
    return buffer.getvalue()


def write_rows(rows, root=ROOT):
    path = os.path.join(root, *LEDGER.split("/"))
    text = open(path, encoding="utf-8", newline="").read()
    ledger = ledger_rows(root)
    taken = {row["new"] for row in ledger}
    folder = os.path.join(root, ASM)
    texts = {}
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".s"):
            continue
        texts[name] = open(os.path.join(folder, name), encoding="latin-1",
                           newline="").read()
        taken.update(found.group(1) for found in
                     (EXPORT.match(line) for line in texts[name].split("\n")) if found)
    added = []
    fresh = []
    for address, library, member_name, symbol, length, masked, compared, _positions in rows:
        old = "sub_%08X" % address
        if symbol in taken or any(row["address"] == "0x%08X" % address for row in ledger):
            continue
        fresh.append((address, row_text([
            "0x%08X" % address, old, symbol, CLASS,
            "armlib/%s, member %s, symbol %s, %d B matched, %d B masked, %d B compared; "
            "tools/research/library_match.py --detail 0x%08X"
            % (library, member_name, symbol, length, masked, compared, address)])))
        taken.add(symbol)
        added.append((address, old, symbol))
    if fresh:
        body = text.splitlines()
        at = len(body)
        for index in range(1, len(body)):
            if int(body[index].split(",", 1)[0], 16) > fresh[0][0]:
                at = index
                break
        body[at:at] = [line for _address, line in fresh]
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(body) + "\n")
    for address, old, symbol in added:
        for name, text in texts.items():
            texts[name] = renamed(text, old, symbol)
    for name, text in texts.items():
        path = os.path.join(folder, name)
        with open(path, encoding="latin-1", newline="") as handle:
            if handle.read() == text:
                continue
        with open(path, "w", encoding="latin-1", newline="") as handle:
            handle.write(text)
    return added


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--lib", default=os.path.join(os.environ.get("ARMLIB", ""), "armlib"))
    parser.add_argument("--rom", default=ROM)
    parser.add_argument("--root", default=ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--detail", type=lambda text: int(text, 0))
    arguments = parser.parse_args(argv)
    if not os.path.isdir(arguments.lib):
        print("pass --lib with the toolchain's armlib directory")
        return 1
    if not os.path.exists(arguments.rom):
        print("the census needs the retail image at %s" % arguments.rom)
        return 1
    rom = open(arguments.rom, "rb").read()
    starts = entries(arguments.root)
    rows = census(arguments.lib, rom, starts, ROM_BASE)
    for row in rows:
        print("0x%08x %s %s %s %d B matched %d B masked" % row[:6])
    print("matches=%d entries=%d" % (len(rows), len(starts)))
    for row in rows:
        if arguments.detail is not None and row[0] == arguments.detail:
            print("0x%08x %s %s %s length=%d masked=%d compared=%d positions=%s"
                  % (row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                     " ".join(str(index) for index in row[7])))
    if arguments.write:
        added = write_rows(rows, arguments.root)
        print("named=%d" % len(added))
    return 0


if __name__ == "__main__":
    sys.exit(main())
