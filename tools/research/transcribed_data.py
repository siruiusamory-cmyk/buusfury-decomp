from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import code_xref  # noqa: E402
import emitted  # noqa: E402
import unknown_consumer_search as search  # noqa: E402

ROM_BASE = 0x08000000
ROM_SIZE = 8388608
IWRAM = (0x03000000, 0x03008000)
EWRAM = (0x02000000, 0x02040000)
DATA = re.compile(r"^(\s*)(DCB|DCW|DCD)(\s+)(.+?)(\s*)$")
LABEL = re.compile(r"^\s*\|?([A-Za-z_][A-Za-z0-9_]*)\|?\s*$")
DIRECTIVES = frozenset((
    "AREA", "CODE16", "CODE32", "END", "MACRO", "MEND", "PROC", "ENDP", "GBLA", "GBLL", "GBLS",
    "SETA", "SETL", "SETS", "WHILE", "WEND", "ALIGN", "SPACE", "IF", "ELSE", "ENDIF", "OPT",
    "LTORG", "IMPORT", "EXPORT", "GET", "INCBIN", "INCLUDE", "EQU", "DCD", "DCB", "DCW", "DS",
))
ABSOLUTE = re.compile(r"([0-9A-Fa-f]{8})")
STRING = re.compile(r'"((?:[^"\\]|\\.)*)"')
SLICE_TOKEN = re.compile(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted$")
WIDTH = {"DCB": 1, "DCW": 2, "DCD": 4}
BASE_ZERO = "rom_header.s"
TRANSCRIBED = ("buu.s", "crt0.s", "GBARam.s", "ewram.s", "iwram.s", "rest_of_the_game.s",
               "rom_header.s")


def lines_of(path):
    return open(path, errors="replace").read().split("\n")


def statements(path):
    out = []
    for number, text in enumerate(lines_of(path), 1):
        body = text.split(";", 1)[0].strip()
        if not body:
            continue
        match = DATA.match(body)
        if match:
            kind = "data"
        else:
            found = LABEL.match(body)
            kind = "label" if found and found.group(1) not in DIRECTIVES else "other"
        out.append((number, body, kind, match))
    return out


def operand_bytes(directive, operands, resolve=None):
    out = bytearray()
    for token in [item.strip() for item in operands.split(",") if item.strip()]:
        text = STRING.match(token)
        if text:
            value = text.group(1)
            out += value.replace('"', "").encode("latin-1", "replace")
            continue
        try:
            value = int(token, 16)
        except ValueError:
            value = emitted.operand_value(token)
            if value is None and resolve is not None:
                value = resolve(token)
            if value is None:
                return None
        try:
            number = int(value)
            out += (number & 0xFFFFFFFF if number < 0 else number).to_bytes(WIDTH[directive], "little")
        except (OverflowError, ValueError):
            return None
    return bytes(out)


def arm_blocks(path):
    pending, paired = [], {}
    for number, body, kind, _ in statements(path):
        if kind != "other":
            continue
        head = body.split(None, 1)[0].upper()
        if head == "CODE32":
            pending.append(number)
        elif head == "CODE16" and pending:
            paired[pending.pop(0)] = True
    return paired


def runs_of(path, resolve=None):
    blocks = arm_blocks(path)
    rows, current, pending, depth, arm = [], None, None, 0, False
    for number, body, kind, match in statements(path):
        if kind == "data":
            if arm:
                pending = None
                continue
            if current is None:
                current = {"first": number, "last": number, "label": pending, "data": bytearray(),
                           "kinds": set(), "ok": True, "lines": [], "loop": depth > 0}
            part = operand_bytes(match.group(2), match.group(4), resolve)
            if part is None:
                current["ok"] = False
            else:
                current["data"] += part
            current["last"] = number
            current["kinds"].add(match.group(2))
            current["lines"].append(number)
            continue
        if current is not None:
            rows.append(current)
            current = None
        head = body.split(None, 1)[0].upper() if kind == "other" else ""
        if head == "WHILE":
            depth += 1
        elif head == "WEND":
            depth = max(0, depth - 1)
        elif head == "CODE32":
            arm = number in blocks
        elif head == "CODE16" and arm:
            arm = False
        pending = None if arm else (body.strip("|") if kind == "label" else None)
    if current is not None:
        rows.append(current)
    return rows


def anchors(path):
    out = []
    for number, body, kind, _ in statements(path):
        if kind != "label":
            continue
        found = ABSOLUTE.search(body)
        if found:
            out.append((number, int(found.group(1), 16) - ROM_BASE))
    return out


def transcribed(root=ROOT):
    directory = os.path.join(root, "asm")
    return [name for name in sorted(os.listdir(directory))
            if name.endswith(".s")
            and not name.startswith("rawlabeled_") and not name.startswith("raw_labeled_")]


def carriers(root=ROOT):
    out = {}
    for name in TRANSCRIBED + tuple(transcribed(root)):
        text = open(os.path.join(root, "asm", name), errors="replace").read()
        for match in re.finditer(r"\|\s*inc_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\s*\|\s*\n\s*"
                                 r"INCLUDE\s+(\S+)", text):
            out[os.path.basename(match.group(3))] = (int(match.group(1), 16),
                                                     int(match.group(2), 16))
    return out


class Run:

    __slots__ = ("file", "first", "last", "label", "start", "end", "data", "kinds", "lines",
                 "proved", "ambiguous", "loop")

    def __init__(self, name, row, start, end, hits):
        self.file = name
        self.first = row["first"]
        self.last = row["last"]
        self.label = row["label"]
        self.start = start
        self.end = end
        self.data = bytes(row["data"])
        self.kinds = tuple(sorted(row["kinds"]))
        self.lines = tuple(row["lines"])
        self.proved = row["ok"] and start is not None
        self.ambiguous = hits > 1
        self.loop = bool(row["loop"])


def assign(rom, root=ROOT, resolve=None, table=None):
    table = table or {}
    rows = []
    for name in transcribed(root):
        path = os.path.join(root, "asm", name)
        marks = anchors(path)
        cursor = 0 if name in BASE_ZERO else None
        for row in runs_of(path, resolve):
            start, end, hits, ordered = None, None, 0, []
            data = bytes(row["data"])
            if row["ok"] and data:
                before = [offset for line, offset in marks if line < row["first"]]
                after = [offset for line, offset in marks if line > row["last"]]
                low = max([cursor or 0] + before)
                high = (after[0] if after else len(rom)) - len(data)
                align = max(WIDTH[kind] for kind in row["kinds"])
                at = low
                while True:
                    where = rom.find(data, at, high + len(data))
                    if where < 0 or where > high:
                        break
                    if where % align == 0:
                        ordered.append(where)
                    at = where + 1
                hits = len(ordered)
                expected = table.get(row["label"]) - ROM_BASE if row["label"] in table else None
                if expected is not None and expected in ordered:
                    start = expected
                elif ordered:
                    abuts = [where for where in ordered
                             if after and where + len(data) == after[0]]
                    start = abuts[-1] if abuts else ordered[0]
                if start is not None:
                    end = start + len(data)
                    cursor = end
            rows.append(Run(name, row, start, end, hits))
    return rows


def channels(rom):
    sites = code_xref.scan(rom)
    targets = set()
    for kind in ("thumb", "arm"):
        for _, target in sites[kind]:
            targets.add(target - ROM_BASE)
    pointed = {}
    for literal, spots in search.loader_targets(rom).items():
        value = struct.unpack_from("<I", rom, literal)[0]
        if ROM_BASE <= value < ROM_BASE + len(rom):
            pointed.setdefault(value - ROM_BASE, []).extend(spots)
    return sites, targets, pointed


def classify(run, sites, targets, pointed):
    offset = (-run.start) % 4
    words = [run.start + at for at in range(offset, len(run.data) - 3, 4)]
    pooled = [word for word in words if word in targets]
    values = [int.from_bytes(run.data[at:at + 4], "little")
              for at in range(offset, len(run.data) - 3, 4)]
    named = [word for word in words if word in pointed]
    addresses = sum(1 for value in values
                    if ROM_BASE <= value < ROM_BASE + ROM_SIZE
                    or IWRAM[0] <= value < IWRAM[1] or EWRAM[0] <= value < EWRAM[1])
    if words and len(pooled) == len(words):
        return "pool", "pooled=%d/%d site=0x%08X" % (len(pooled), len(words),
                                                     probe_sites(sites, pooled[0]))
    if named and named[0] == run.start and values and addresses == len(values):
        return "ptrtable", "pooled=%d/%d start=0x%08X site=0x%08X" % (
            len(pooled), len(words), ROM_BASE + named[0], probe_sites(sites, named[0]))
    cited = "cited=0x%08X/%d" % (ROM_BASE + named[0], len(pointed[named[0]])) if named else "cited=none"
    return "data", "pooled=%d/%d %s" % (len(pooled), len(words), cited)


def probe_sites(sites, word):
    for kind in ("thumb", "arm"):
        for site, target in sites[kind]:
            if target - ROM_BASE == word:
                return site
    return 0


def csv_text(rows):
    out = ["file,line_first,line_last,rom_start,rom_end,bytes,class,evidence"]
    for run, kind, evidence in rows:
        out.append("%s,%d,%d,0x%06x,0x%06x,%d,%s,%s"
                   % (run.file, run.first, run.last, run.start, run.end, len(run.data),
                      kind, evidence.replace(",", ";")))
    return "\n".join(out) + "\n"


def measured(rom, root=ROOT, resolve=None, table=None):
    sites, targets, pointed = channels(rom)
    rows = [run for run in assign(rom, root, resolve, table) if run.proved]
    adr = adr_targets(rom)
    out = []
    totals = {}
    for run in rows:
        kind, evidence = classify(run, sites, targets | adr, pointed)
        if run.loop:
            evidence += "; loop=fill"
        out.append((run, kind, evidence))
        totals[kind] = totals.get(kind, 0) + len(run.data)
    return out, totals


def adr_targets(rom):
    out = set()
    for index in range(len(rom) // 2):
        value = struct.unpack_from("<H", rom, index * 2)[0]
        if value & 0xF800 == 0xA000:
            out.add(((index * 2 + 4) & ~3) + (value & 0xFF) * 4)
    for index in range(len(rom) // 4):
        value = struct.unpack_from("<I", rom, index * 4)[0]
        if (value & 0x0FEF0000) in (0x028F0000, 0x024F0000):
            offset = value & 0xFFF
            out.add(index * 4 + 8 + (-offset if value & 0x00400000 else offset))
    return out


def load_symbols(path):
    if not path or not os.path.exists(path):
        return {}
    table = json.load(open(path))
    return {entry["name"]: int(entry["address"], 16) for entry in table["symbols"]}


ASSEMBLED = ("buu.s", "GBARam.s", "ewram.s", "iwram.s", "rest_of_the_game.s")
EQU = re.compile(r"^\s*\|?([A-Za-z_][A-Za-z0-9_]*)\|?\s+EQU\s+([^;\s]+)")


def units(root=ROOT):
    table = load_symbols(os.path.join(root, "build", "output", "symbols.json"))
    names, owner = {}, {}
    for name in ASSEMBLED:
        text = emitted.source_text(root, os.path.join(root, "asm", name))
        found = {}
        for line in text.split("\n"):
            body = line.split(";", 1)[0].strip()
            if not body:
                continue
            label = LABEL.match(body)
            if label and label.group(1) in table:
                found[label.group(1)] = (table[label.group(1)], body)
                continue
            equ = EQU.match(body)
            if equ:
                try:
                    found[equ.group(1)] = (int(equ.group(2), 0), body.split(None, 1)[0])
                except ValueError:
                    pass
        names[name] = found
    for name in ASSEMBLED:
        text = emitted.source_text(root, os.path.join(root, "asm", name))
        for match in re.finditer(r"INCLUDE\s+(\S+)", text):
            owner.setdefault(os.path.basename(match.group(1)), name)
    return names, owner


def cited_word(run, targets, pointed, sites):
    offset = (-run.start) % 4
    words = [run.start + at for at in range(offset, len(run.data) - 3, 4)]
    for word in words:
        site = probe_sites(sites, word)
        if site:
            return word, site, "a pc-relative load targets 0x%08X" % (ROM_BASE + word)
    for word in words:
        if word in pointed:
            return word, (pointed[word] or [0])[0], "a pool word names 0x%08X" % (ROM_BASE + word)
    return None, 0, "cited=none"


def slice_name(start, end):
    return "baserom.gba_0x%x_0x%x.extracted" % (start, end)


def substitute(operands, reverse):
    out, replaced = [], 0
    for token in [item.strip() for item in operands.split(",")]:
        try:
            number = int(token, 16)
        except ValueError:
            out.append(token)
            continue
        hit = reverse.get(number)
        if hit is not None:
            out.append(hit[1])
            replaced += 1
        elif number and reverse.get(number - 1) is not None:
            out.append("%s+1" % reverse[number - 1][1])
            replaced += 1
        else:
            out.append(token)
    return ", ".join(out), replaced


def unit_symbols(root, table):
    names, owner = {}, {}
    for name in ASSEMBLED:
        text = emitted.source_text(root, os.path.join(root, "asm", name))
        reverse = {}
        for line in text.split("\n"):
            body = line.split(";", 1)[0].strip()
            if not body:
                continue
            label = LABEL.match(body)
            if label and label.group(1) in table:
                reverse[table[label.group(1)]] = (label.group(1), body)
                continue
            equ = EQU.match(body)
            if equ:
                try:
                    reverse[int(equ.group(2), 0)] = (equ.group(1), equ.group(1))
                except ValueError:
                    pass
        names[name] = reverse
        for match in re.finditer(r"INCLUDE\s+(\S+)", text):
            owner.setdefault(os.path.basename(match.group(1)), name)
    return names, owner


def apply(root=ROOT, rom=None, table=None):
    rom = open(os.path.join(root, "baserom.gba"), "rb").read() if rom is None else rom
    symbols = load_symbols(os.path.join(root, "build", "output", "symbols.json"))
    reverse, owner = unit_symbols(root, symbols)
    sites, targets, pointed = channels(rom)
    targets = targets | adr_targets(rom)
    rows, totals = measured(rom, root, symbols.get, symbols)
    per_file = {}
    for run, kind, evidence in rows:
        per_file.setdefault(run.file, []).append((run, kind, evidence))
    converted = substituted = converted_bytes = loops = 0
    for name in sorted(per_file):
        path = os.path.join(root, "asm", name)
        lines = lines_of(path)
        unit = reverse.get(owner.get(name, name), {})
        edits = 0
        for run, kind, evidence in reversed(per_file[name]):
            original = lines[run.first - 1]
            if run.loop:
                loops += 1
                continue
            if kind == "data":
                indent = re.match(r"\s*", original).group(0)
                word, site, why = cited_word(run, targets, pointed, sites)
                keep = [line for line in lines[run.first - 1:run.last]
                        if line.strip().startswith(";")]
                block = []
                if not (run.label or "").startswith("unk_"):
                    block.append("|unk_%08X|" % (run.start + ROM_BASE))
                if word is not None:
                    block.append("; cited by 0x%08X (%s)" % (site, why))
                block.append("%sINCBIN\t%s" % (indent, slice_name(run.start, run.end)))
                lines[run.first - 1:run.last] = keep + block
                converted += 1
                converted_bytes += len(run.data)
                edits += 1
                continue
            for number in run.lines:
                original = lines[number - 1]
                body = original.split(";", 1)[0].strip()
                match = DATA.match(body)
                if not match or match.group(2) != "DCD":
                    continue
                text, count = substitute(match.group(4), unit)
                if count:
                    lead = re.match(r"(\s*%s\s+)" % match.group(2), original).group(1)
                    comment = original.split(";", 1)[1].strip() if ";" in original else ""
                    lines[number - 1] = "%s%s%s" % (lead, text,
                                                    "  ; " + comment if comment else "")
                    substituted += count
                    edits += 1
        if edits:
            with open(path, "w", encoding="ascii", newline="\n") as handle:
                handle.write("\n".join(lines))
            print("apply %-22s %d edit(s)" % (name, edits))
    print("converted %d data run(s), %d byte(s); substituted %d word(s); loop bodies %d"
          % (converted, converted_bytes, substituted, loops))
    return 0


def check(root=ROOT):
    rom = open(os.path.join(root, "baserom.gba"), "rb").read()
    symbols = load_symbols(os.path.join(root, "build", "output", "symbols.json"))
    rows, totals = measured(rom, root, symbols.get, symbols)
    missing = []
    for name in transcribed(root):
        for line in lines_of(os.path.join(root, "asm", name)):
            match = re.match(r"^\s*INCBIN\s+(\S+)\s*$", line)
            if not match:
                continue
            span = SLICE_TOKEN.search(match.group(1))
            if span and not os.path.exists(os.path.join(root, match.group(1))):
                missing.append((name, match.group(1)))
    print("data runs=%d bytes=%d pools=%d ptrtables=%d missing slices=%d"
          % (sum(1 for _, k, _ in rows if k == "data"), totals.get("data", 0),
             totals.get("pool", 0), totals.get("ptrtable", 0), len(missing)))
    for row, kind, evidence in rows:
        if kind == "data":
            print("  left as text: %s:%d..%d 0x%06x %d B  %s"
                  % (row.file, row.first, row.last, row.start, len(row.data), evidence))
    for row in missing[:5]:
        print("  missing", row)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--symbols", default=os.path.join(ROOT, "build", "output", "symbols.json"))
    parser.add_argument("--csv", default="")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    rom = open(args.rom, "rb").read()
    symbols = load_symbols(args.symbols)
    if args.apply:
        return apply(ROOT, rom, symbols)
    if args.check:
        return check(ROOT)
    rows, totals = measured(rom, ROOT, symbols.get, symbols)
    if args.report:
        for kind in sorted(totals):
            print("%-9s runs=%4d bytes=%6d"
                  % (kind, sum(1 for _, k, _ in rows if k == kind), totals[kind]))
        print("runs=%d bytes=%d symbols=%d" % (len(rows), sum(totals.values()), len(symbols)))
        for run in assign(rom, ROOT, symbols.get, symbols):
            if not run.proved:
                print("UNPROVED %s:%d..%d %d B" % (run.file, run.first, run.last, len(run.data)))
    if args.csv:
        with open(args.csv, "w", encoding="ascii", newline="\n") as handle:
            handle.write(csv_text(rows))
        print("wrote %s: %d row(s), %d byte(s)" % (args.csv, len(rows), sum(totals.values())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
