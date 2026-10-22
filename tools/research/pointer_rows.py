from __future__ import annotations

import csv
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in ("tools", "tools/gate", "tools/research"):
    sys.path.insert(0, os.path.join(ROOT, *_path.split("/")))

import emitted  # noqa: E402
import gate  # noqa: E402

ROM_BASE = 0x08000000
IWRAM = (0x03000000, 0x03008000)
EWRAM = (0x02000000, 0x02040000)
CLASS = "pointer-tables"
RECORD = os.path.join(ROOT, "docs", "research", "POINTER_ROWS.csv")
REMAINDER = os.path.join(ROOT, "docs", "research", "RAW_REMAINDER.csv")
UNITS = ("buu.s", "GBARam.s", "ewram.s", "iwram.s", "rest_of_the_game.s", "crt0.s")
GENERATED = ("raw_labeled_74d248.s", "raw_labeled_7b5b64.s")
FIELDS = ("row_start", "row_end", "row_file", "row_line", "word", "value", "operand", "kind",
          "row_verdict", "row_reason")
TOKEN = re.compile(r"^(\s*)INCBIN\s+baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted\s*$")
LABEL = re.compile(r"^\s*\|?([A-Za-z_][A-Za-z0-9_]*)\|?\s*$")
EIGHT = re.compile(r"(?:^|[^0-9A-Fa-f])([0-9A-Fa-f]{8})(?:$|[^0-9A-Fa-f])")
SLICE = re.compile(r"^inc_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)$")
RAM = re.compile(r"^unk_([0-9A-F]{8})$")
REFUSED = {0x75F7F4: "build-time mapping-symbol refusal: armlink emits $f at 0x0876CCD4 and tools/symbols names no kind for it",
            0x042BAC: "build-time mapping-symbol refusal: armlink emits $f at 0x08042BBC and tools/symbols names no kind for it",
            0x030EFC: "build-time mapping-symbol refusal: armlink emits $f at 0x08030F04 and tools/symbols names no kind for it",
            0x0B51C: "build-time mapping-symbol refusal: armlink emits $f at 0x0800B524 and tools/symbols names no kind for it"}
NUMERIC_MEASURED = {
    0x6B8028: "3 x u32 pointer array, stride 4 x count 3 at 0x080141D6..0x080141E8 "
              "(0x080141DC lsls r0,r4,#2, 0x080141E6 cmp r4,#3); targets 0x086B7FAC, "
              "0x086B7F3C, 0x086B7ED8 lie inside endrom_container_run_6b7e8c, which carries "
              "no label at them",
}


def image(root=ROOT):
    return open(os.path.join(root, "baserom.gba"), "rb").read()


def rows(root=ROOT):
    path = RECORD if os.path.exists(RECORD) else REMAINDER
    spans = {}
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("class", CLASS) != CLASS:
                continue
            start = int(row.get("row_start") or row["start"], 16)
            end = int(row.get("row_end") or row["end"], 16)
            carrier = row.get("row_file") or row.get("carrier_file") or row["file"]
            spans[(start, end, carrier)] = int(row.get("row_line") or row["line"])
    return [(start, end, carrier, line) for (start, end, carrier), line in sorted(spans.items())]


def index(root=ROOT):
    labels, exported, units = {}, {}, {name: name for name in UNITS}
    for name in sorted(os.listdir(os.path.join(root, "asm"))):
        if not name.endswith(".s"):
            continue
        for line in open(os.path.join(root, "asm", name), errors="replace"):
            found = re.match(r"^\s*INCLUDE\s+(\S+)", line)
            if found:
                units.setdefault(os.path.basename(found.group(1)), name)
            found = re.match(r"^\s*(?:EXPORT|GLOBAL)\s+\|?([A-Za-z_][A-Za-z0-9_]*)\|?\s*$",
                             line.split(";", 1)[0].strip())
            if found:
                exported.setdefault(found.group(1), name)
            found = LABEL.match(line.split(";", 1)[0].strip())
            if not found:
                continue
            text = found.group(1)
            slice_hit = SLICE.match(text)
            if slice_hit:
                labels.setdefault(ROM_BASE + int(slice_hit.group(1), 16), (text, name))
            else:
                digits = EIGHT.search(text)
                if digits:
                    labels.setdefault(int(digits.group(1), 16), (text, name))
    symbols = {}
    path = os.path.join(root, "build", "output", "symbols.json")
    if not os.path.exists(path):
        raise SystemExit("%s is missing: %s has no linker symbols, so every word they name would "
                         "read as unresolved; run rebuild.cmd first" % (path, root))
    for entry in json.load(open(path))["symbols"]:
        symbols.setdefault(int(entry["address"], 16), set()).add(entry["name"])
    return labels, exported, units, symbols


def spelling(value, unit, names, size):
    labels, exported, units, symbols = names
    if IWRAM[0] <= value < IWRAM[1] or EWRAM[0] <= value < EWRAM[1]:
        return "|unk_%08X|" % value, "ram"
    if not ROM_BASE <= value < ROM_BASE + size:
        return None, "0x%08X is not a ROM or RAM address" % value
    for address, suffix in ((value, ""), (value - 1, "+1")):
        if suffix and not value & 1:
            continue
        if address in labels:
            name, file = labels[address]
            if units.get(file) != unit and name not in exported:
                return None, "0x%08X is named |%s|, which another unit does not export" % (
                    address, name)
            return "|%s|%s" % (name, suffix), "label"
        if address in symbols:
            name = sorted(symbols[address])[0]
            if EIGHT.search(name):
                return "|%s|%s" % (name, suffix), "symbol"
            return None, "0x%08X is named %s, which carries no address" % (address, name)
    return None, "0x%08X lies inside a carrier with no label at it" % value


REASONS = ("off-grid (BF-102B)", "raw_labeled refused",
           "island split breaks text/tables predicate",
           "generated run with no measured target",
           "generated, no label write path", "mid-instruction target")
_SPANS = None


def spans():
    global _SPANS
    if _SPANS is None:
        out = []
        for name in sorted(os.listdir(os.path.join(ROOT, "asm"))):
            if not name.endswith(".s"):
                continue
            text = open(os.path.join(ROOT, "asm", name), errors="replace").read()
            for found in re.finditer(r"INCBIN\s+(\S+)", text):
                token = found.group(1)
                row = re.search(r"_0?x?([0-9a-fA-F]{5,8})_0?x?([0-9a-fA-F]{5,8})"
                                r"\.(?:extracted|bin)", token)
                if row:
                    out.append((int(row.group(1), 16), int(row.group(2), 16),
                                "build" in token.replace("/", "\\")))
        _SPANS = sorted(out)
    return _SPANS


def target_reason(value, names):
    offset = value - ROM_BASE
    for low, high, built in spans():
        if low <= offset < high:
            if not built:
                return "island split breaks text/tables predicate"
            return ("generated, no label write path" if offset == low
                    else "generated run with no measured target")
    if value in names[3] or value - 1 in names[3]:
        return "generated, no label write path"
    return "mid-instruction target"


def grid(start, length, shift=0):
    return [start + at for at in range((-start) % 4 + shift, length - 3, 4)]


def emitted_operand(word):
    operand = word["operand"]
    return operand if operand and not operand.endswith("+1") else word["value"]


def pad_length(rom, row, words):
    start, end = row[0], row[1]
    head = (-start) % 4
    if head == 0 or (end - start - head) % 4 or len(words) != (end - start - head) // 4:
        return 0
    return head if rom[start:start + head] == b"\x00" * head else 0


def edge_reason(rom, row):
    start, end = row[0], row[1]
    head = (-start) % 4
    tail = (end - start - head) % 4
    parts = []
    if head:
        if rom[start:start + head] == b"\x00" * head:
            parts.append("%d zero alignment byte(s) at 0x%06X" % (head, start))
        else:
            first = start - start % 4
            value = struct.unpack_from("<I", rom, first)[0]
            parts.append("%d high byte(s) at 0x%06X of the word 0x%08X at 0x%06X, whose other "
                         "bytes lie before the row" % (head, start, value, first))
    if tail:
        first = end - tail
        value = struct.unpack_from("<I", rom, first)[0]
        parts.append("%d low byte(s) at 0x%06X of the word 0x%08X at 0x%06X, whose other bytes "
                     "lie after the row" % (tail, first, value, first))
    return "; ".join(parts)


def measure(rom, names, shift=0):
    out = []
    for start, end, carrier, line in rows():
        unit = names[2].get(carrier, carrier)
        words, trouble = [], []
        for word in grid(start, end - start, shift):
            value = struct.unpack_from("<I", rom, word)[0]
            operand, kind = spelling(value, unit, names, len(rom))
            words.append((word, value, operand, kind))
            if operand is None:
                trouble.append("%s: 0x%08X" % (target_reason(value, names), value))
        out.append(((start, end, carrier, line), words, trouble))
    return out


def verdict(row, words, trouble, shift=0, rom=None):
    start, end = row[0], row[1]
    if start in REFUSED:
        return False, REFUSED[start]
    if row[2] in GENERATED:
        return False, ("raw_labeled refused: the carrier is a generated fragment whose own check "
                       "pins its byte text (`rawlabeled.citation_check`)")
    residual = (end - start) - 4 * len(words) if not shift else -1
    if start in NUMERIC_MEASURED and residual == 0:
        return True, "measured pointer array: " + NUMERIC_MEASURED[start]
    if residual:
        pad = pad_length(rom, row, words) if shift == 0 and rom is not None else 0
        if pad:
            named = sum(1 for word in words if word[2] and not word[2].endswith("+1"))
            thumb = sum(1 for word in words if word[2] and word[2].endswith("+1"))
            return True, ("literal pool: %d zero alignment byte(s) as DCB, %d word(s) as DCD "
                          "(%d named%s)"
                          % (pad, len(words), named,
                             ", %d Thumb-bit numeric" % thumb if thumb else ""))
        if shift == 0 and rom is not None:
            return False, "off-grid (BF-102B): %s" % edge_reason(rom, row)
        return False, "off-grid (BF-102B): %d byte(s) outside the grid words" % residual
    if trouble:
        return False, sorted(trouble, key=lambda text: REASONS.index(text.split(":")[0]))[0]
    return True, "every word is a symbol reference"


def table(rom, names):
    out = []
    for row, words, trouble in measure(rom, names):
        converted, reason = verdict(row, words, trouble, rom=rom)
        numeric = converted and row[0] in NUMERIC_MEASURED
        for word, value, operand, kind in words:
            if numeric:
                operand, kind = "0x%08X" % value, "address"
            out.append({"row_start": "0x%06X" % row[0], "row_end": "0x%06X" % row[1],
                        "row_file": row[2], "row_line": row[3], "word": "0x%06X" % word,
                        "value": "0x%08X" % value, "operand": operand or "",
                        "kind": kind if operand else "unresolved",
                        "row_verdict": "yes" if converted else "no",
                        "row_reason": reason})
    return out


def control(rom, names):
    out = {}
    for shift in (0, 1, 2, 3):
        out[shift] = sum(1 for row, words, trouble in measure(rom, names, shift)
                         if verdict(row, words, trouble, shift)[0])
    return out


def csv_text(report):
    lines = [",".join(FIELDS)]
    for row in report:
        cells = []
        for field in FIELDS:
            value = str(row[field])
            cells.append('"%s"' % value.replace('"', '""') if "," in value else value)
        lines.append(",".join(cells))
    return "\n".join(lines) + "\n"


def plan(report):
    by_row = {}
    for row in report:
        key = (int(row["row_start"], 16), int(row["row_end"], 16), row["row_file"],
               int(row["row_line"]))
        by_row.setdefault(key, []).append(row)
    out = {}
    for (start, end, carrier, _line), words in sorted(by_row.items()):
        if any(word["row_verdict"] != "yes" for word in words):
            continue
        out.setdefault(carrier, []).append((start, end, [emitted_operand(word)
                                                         for word in words]))
    return out


def operand_bytes(operand):
    value = emitted.operand_value(operand)
    if value is None:
        raise SystemExit("%r is not an operand the tree's reader resolves" % operand)
    return (value & 0xFFFFFFFF).to_bytes(4, "little")


def constants(report):
    wanted = {}
    for row in report:
        if row["row_verdict"] != "yes":
            continue
        found = RAM.match(row["operand"].strip("|")) if row["operand"] else None
        if found:
            wanted.setdefault(row["operand"].strip("|"), int(found.group(1), 16))
    return wanted


IMPORT_LINE = re.compile(r"^[ \t]*IMPORT[ \t]+\|([A-Za-z_][A-Za-z0-9_]*)\|", re.M)
EQU_LINE = re.compile(r"^[ \t]*\|?([A-Za-z_][A-Za-z0-9_]*)\|?[ \t]+EQU\b", re.M)
NAME = re.compile(r"^\|([A-Za-z_][A-Za-z0-9_]*)\|(?:\+1)?$")


def name_of(operand):
    found = NAME.match(operand) if operand else None
    return found.group(1) if found else None


def tree_index(root):
    parent, defined, files = {}, {}, []
    asm = os.path.join(root, "asm")
    for path in sorted(os.listdir(asm)):
        if not path.endswith(".s"):
            continue
        files.append(path)
        for line in open(os.path.join(asm, path), errors="replace"):
            body = line.split(";", 1)[0].strip()
            found = re.match(r"^INCLUDE\s+(\S+)", body)
            if found:
                parent.setdefault(os.path.basename(found.group(1)), path)
                continue
            found = LABEL.match(body) or EQU_LINE.match(body)
            if found:
                defined.setdefault(found.group(1), path)

    def unit_of(name):
        seen = set()
        while name in parent and name not in seen:
            seen.add(name)
            name = parent[name]
        return name

    return {name: unit_of(name) for name in files}, defined


def declarations(root, report):
    units, defined = tree_index(root)
    wanted = {}
    for row in report:
        if row["row_verdict"] != "yes":
            continue
        name = name_of(row["operand"])
        if name:
            wanted.setdefault(units.get(row["row_file"], row["row_file"]), set()).add(name)
    out = {}
    for unit, names in sorted(wanted.items()):
        text = open(os.path.join(root, "asm", unit), errors="replace").read()
        have = set(IMPORT_LINE.findall(text))
        imports, equals = [], []
        for name in sorted(names):
            owner = defined.get(name)
            if owner is not None and units.get(owner, owner) == unit:
                continue
            if owner is None:
                if not RAM.match(name) or "unk_%08X" % int(name[4:], 16) != name:
                    raise SystemExit("a converted operand names %s, which no source line defines"
                                     % name)
                equals.append("%-16sEQU     0x%s" % (name, name[4:]))
                continue
            if name not in have:
                imports.append("        IMPORT |%s|" % name)
        if imports or equals:
            out[unit] = (imports, equals)
    return out


def insert_after(text, pattern, lines):
    rows = text.split("\n")
    last = -1
    for index, row in enumerate(rows):
        if pattern.match(row):
            last = index
    rows[last + 1:last + 1] = lines
    return "\n".join(rows)


def find_token(lines, carrier, start, end):
    token = "baserom.gba_0x%x_0x%x.extracted" % (start, end)
    for number, line in enumerate(lines):
        found = TOKEN.match(line)
        if found and line.strip().endswith(token):
            return number, found.group(1)
    return None, None


def apply(root, rom, report):
    work = plan(report)
    pending = declarations(root, report)
    converted = moved = 0
    for carrier in sorted(work):
        path = os.path.join(root, "asm", carrier)
        lines = open(path, errors="replace").read().split("\n")
        edited = 0
        for start, end, operands in reversed(work[carrier]):
            head = (-start) % 4
            blob = b"\x00" * head + b"".join(operand_bytes(operand) for operand in operands)
            if blob != rom[start:end]:
                raise SystemExit("0x%06X: the operands do not carry the retail bytes" % start)
            at, indent = find_token(lines, carrier, start, end)
            if at is None:
                continue
            emitted_lines = (["%sDCB\t%s" % (indent, ",".join("0x00" for _ in range(head)))]
                             if head else [])
            lines[at:at + 1] = emitted_lines + ["%sDCD\t%s" % (indent, operand)
                                                for operand in operands]
            converted += 1
            moved += end - start
            edited += 1
        if edited:
            with open(path, "w", encoding="ascii", newline="\n") as handle:
                handle.write("\n".join(lines))
            print("apply %-24s %d row(s)" % (carrier, edited))
    for unit, (imports, equals) in sorted(pending.items()):
        path = os.path.join(root, "asm", unit)
        text = open(path, errors="replace").read()
        if imports:
            text = insert_after(text, IMPORT_LINE, imports)
        if equals:
            text = insert_after(text, EQU_LINE, equals)
        with open(path, "w", encoding="ascii", newline="\n") as handle:
            handle.write(text)
        print("declare %-22s %d import(s) %d constant(s)" % (unit, len(imports), len(equals)))
    print("converted %d row(s), %d byte(s)" % (converted, moved))
    return converted, moved


def check(root, rom, names):
    report = table(rom, names)
    spans = {(row["row_start"], row["row_end"]) for row in report}
    good = {(row["row_start"], row["row_end"]) for row in report if row["row_verdict"] == "yes"}
    total = sum(int(end, 16) - int(start, 16) for start, end in spans)
    moved = sum(int(end, 16) - int(start, 16) for start, end in good)
    if len(spans) != 124 or total != 1641:
        raise SystemExit("the record is %d row(s) / %d B, not 124 / 1641" % (len(spans), total))
    raw = {("0x%06X" % start, "0x%06X" % end) for start, end in gate.incbin_ranges()}
    still = sorted(good & raw)
    pending = declarations(root, report)
    if pending:
        raise SystemExit("a converted row needs a declaration the tree does not carry: %s"
                         % "; ".join("%s: %s" % (unit, ", ".join(imports + equals))
                                     for unit, (imports, equals) in sorted(pending.items())))
    return {"rows": len(spans), "bytes": total, "converted": len(good), "moved": moved,
            "still_incbin": len(still)}


def main(argv):
    rom = image()
    names = index()
    codes = control(rom, names)
    if "--apply" in argv:
        apply(ROOT, rom, table(rom, names))
        names = index()
    report = table(rom, names)
    spans = {(row["row_start"], row["row_end"]) for row in report}
    converted = {row["row_start"] for row in report if row["row_verdict"] == "yes"}
    moved = sum(int(end, 16) - int(start, 16) for start, end in spans if start in converted)
    if "--check" in argv:
        result = check(ROOT, rom, names)
        print("check: %(rows)d row(s) %(bytes)d B, converted %(converted)d row(s) %(moved)d B, "
              "%(still_incbin)d still INCBIN" % result)
        print("control: rows fully resolved at grid shift 0/1/2/3 = %s"
              % "/".join(str(codes[shift]) for shift in (0, 1, 2, 3)))
        return 0
    with open(RECORD, "w", encoding="ascii", newline="\n") as handle:
        handle.write(csv_text(report))
    print("%d row(s) %d B: converted %d row(s) %d B, open %d row(s) %d B"
          % (len(spans), sum(int(e, 16) - int(s, 16) for s, e in spans), len(converted), moved,
             len(spans) - len(converted),
             sum(int(e, 16) - int(s, 16) for s, e in spans) - moved))
    print("control: rows fully resolved at grid shift 0/1/2/3 = %s"
          % "/".join(str(codes[shift]) for shift in (0, 1, 2, 3)))
    print("wrote %s" % os.path.relpath(RECORD, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
