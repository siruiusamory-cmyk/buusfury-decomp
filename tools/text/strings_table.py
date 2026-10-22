from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LAYOUT = os.path.join(HERE, "strings_layout.json")
C_SUFFIXES = (".c", ".cc", ".cpp", ".h", ".hpp")
MIN_RAW_UNITS = 4
WIDE = re.compile(rb'L"((?:[^"\\]|\\.)*)"', re.S)
ESCAPES = {ord("n"): 10, ord("r"): 13, ord("t"): 9, ord("0"): 0,
           ord("\\"): 92, ord('"'): 34, ord("'"): 39}


def load_layout(path=None):
    with open(path or LAYOUT, encoding="ascii") as handle:
        layout = json.load(handle)
    layout["base"] = int(layout["base"], 16)
    layout["count"] = int(layout["count"])
    layout["size"] = int(layout["size"])
    return layout


def region(rom, layout):
    base, size, count = layout["base"], layout["size"], layout["count"]
    offset = base - 0x08000000
    if offset < 0 or offset + size > len(rom):
        raise SystemExit("the strings region %#x..%#x is outside the image" % (base, base + size))
    blob = rom[offset:offset + size]
    table_bytes = count * 4
    area = size - table_bytes
    if area <= 0 or area % 2:
        raise SystemExit("the strings region leaves %d bytes for the strings" % area)
    pointers = list(struct.unpack_from("<%dI" % count, blob, area))
    if not all(base <= word < base + area for word in pointers):
        raise SystemExit("a pointer word names an address outside the strings area")
    starts = [word - base for word in pointers]
    if starts[0] != 0 or starts != sorted(starts) or len(set(starts)) != count:
        raise SystemExit("the pointer words are not the %d string starts in order" % count)
    units = struct.unpack_from("<%dH" % (area // 2), blob, 0)
    texts = []
    for index, start in enumerate(starts):
        if start % 2:
            raise SystemExit("pointer %d names an odd byte offset %#x" % (index, start))
        cursor = start // 2
        if cursor and units[cursor - 1] != 0:
            raise SystemExit("pointer %d does not name a string start" % index)
        end = cursor
        while units[end] != 0:
            end += 1
        texts.append(units[cursor:end])
        if index + 1 < count and starts[index + 1] != (end + 1) * 2:
            raise SystemExit("string %d is not followed by the next string" % index)
    tail = units[starts[-1] // 2 + len(texts[-1]) + 1:]
    if any(tail):
        raise SystemExit("the %d byte(s) after the last terminator are not zero" % (len(tail) * 2))
    return texts, pointers


def literal(units):
    pieces, run = [], []

    def flush():
        if run:
            pieces.append('L"' + "".join(run) + '"')
            run.clear()

    for unit in units:
        if 0x20 <= unit <= 0x7E and unit not in (0x22, 0x5C):
            run.append(chr(unit))
        elif unit == 0x22:
            run.append('\\"')
        elif unit == 0x5C:
            run.append("\\\\")
        else:
            flush()
            pieces.append('L"\\x%04X"' % unit)
    flush()
    return " ".join(pieces) if pieces else 'L""'


def source(texts, layout):
    lines = ["typedef char strings_wchar_t_must_be_two_bytes[sizeof(wchar_t) == 2 ? 1 : -1];\n"]
    for index, units in enumerate(texts):
        lines.append("wchar_t %s%04d[] = %s;\n" % (layout["prefix"], index, literal(units)))
    lines.append("wchar_t* %s[%d] = {\n" % (layout["table"], len(texts)))
    lines.extend("%s%04d,\n" % (layout["prefix"], index) for index in range(len(texts)))
    lines.append("};\n")
    return "".join(lines)


def digest(units):
    return hashlib.sha256(struct.pack("<%dH" % len(units), *units)).digest()


def decode_escapes(raw):
    units, index = [], 0
    while index < len(raw):
        byte = raw[index]
        if byte != 0x5C:
            units.append(byte)
            index += 1
            continue
        escape = raw[index + 1]
        if escape == ord("x"):
            end = index + 2
            while end < len(raw) and chr(raw[end]) in "0123456789abcdefABCDEF":
                end += 1
            units.append(int(raw[index + 2:end], 16))
            index = end
        else:
            units.append(ESCAPES[escape])
            index += 2
    return units


def wide_literals(blob):
    out, current, previous = [], None, None
    for match in WIDE.finditer(blob):
        if previous is None or blob[previous:match.start()].strip(b" \t\r\n"):
            current = []
            out.append(current)
        current.extend(decode_escapes(match.group(1)))
        previous = match.end()
    return out


def tracked_text_hits(root=None):
    root = ROOT if root is None else root
    rom = open(os.path.join(root, "baserom.gba"), "rb").read()
    texts, _pointers = region(rom, load_layout())
    hashes = {digest(units) for units in texts}
    needles = sorted({struct.pack("<%dH" % len(units), *units)
                      for units in texts if len(units) >= MIN_RAW_UNITS})
    prefixes = {}
    for needle in needles:
        prefixes.setdefault(needle[:4], []).append(needle)
    proc = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True)
    hits = []
    for name in proc.stdout.split(b"\0"):
        path = name.decode()
        if not path:
            continue
        try:
            blob = open(os.path.join(root, path), "rb").read()
        except OSError:
            continue
        if path.endswith(C_SUFFIXES) and any(digest(units) in hashes
                                             for units in wide_literals(blob)):
            hits.append(path)
            continue
        for match in re.finditer(rb"[\x20-\x7e]\x00", blob):
            if any(blob.startswith(needle, match.start())
                   for needle in prefixes.get(blob[match.start():match.start() + 4], ())):
                hits.append(path)
                break
    return hits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--layout", default=LAYOUT)
    parser.add_argument("--out")
    parser.add_argument("--hits", action="store_true")
    args = parser.parse_args()
    layout = load_layout(args.layout)
    if args.hits:
        hits = tracked_text_hits(ROOT)
        print("tracked files carrying game text: %s" % (", ".join(hits) if hits else "none"))
        return 1 if hits else 0
    rom = open(args.rom, "rb").read()
    texts, _pointers = region(rom, layout)
    out = args.out or os.path.join(ROOT, *layout["output"].split("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="ascii", newline="\n") as handle:
        handle.write(source(texts, layout))
    print("strings_gen: %d string(s), %d code unit(s), wrote %s"
          % (len(texts), sum(len(units) for units in texts), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
