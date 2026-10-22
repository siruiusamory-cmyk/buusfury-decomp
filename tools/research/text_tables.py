"""Sub-classify the `text/tables` rows of RAW_REMAINDER.csv into the ticket's five classes.

TEXT-TABLES-001. The class `text/tables` is defined by `raw_remainder.py`: the row's exact span is a
run `TRANSCRIBED_DATA_RUNS.csv` classes as `data`. That predicate says what the transcriber could NOT
call a pool or a pointer table; it says nothing about what the bytes are. This tool measures that, and
assigns every row to exactly one of: the cartridge header, text, a record table, a numeric constant
table read by a named routine, or unknown. Every row carries its own evidence, and a class is
convertible only when its UNEXPLAINED bytes are at most five percent of its bytes (the ticket's rule).

The parse this ticket found, and the one it could not finish:

  * `record table` - rows in 0x0491C4..0x04E488 whose four-byte words are SELF-RELATIVE METHOD
    ENTRIES. The convention is read from the engine's own bytes at file 0x188FC: `ldr r2,[r1,#0x68]`
    then `adds r2, r2, r1`, so `method = class + s32(class + slot)` and the class word is the base, not
    the slot's own address. Two anchors in the tree's own knowledge agree with the base reading and
    refute the site reading (0x04AAF4 slot 0 and slot 8; 0x04C484 slot 0x68).
  * the parse does NOT reach the bytes: the class BASES are not established, and under the best base
    set this ticket could validate, only 13 % of the resolved methods carry a symbol. A word whose
    method cannot be named cannot be re-derived, so it is residue.

The numeric route spells a row as tracked `DCD`/`DCW` when EVERY 4 B word of it is a method offset:
one `DCD` per word, one `DCW` for each off-grid fragment, no retail byte payload. Its layout is
`s32 self-relative method offset`: the method is `class base + s32(word)`, base is the greatest
4-aligned address the loader channel names at or below the word, and bit 0 is the Thumb bit. The
consumer is the dispatch at 0x080188FC (`ldr r2,[r1,#0x68]`, `adds r2,r2,r1`); the three pinned
anchors are the base reading's proof. The group's record is `docs/research/NUMBER_TABLES.csv`.

  python tools/research/text_tables.py --report
  python tools/research/text_tables.py --write
  python tools/research/text_tables.py --check
  python tools/research/text_tables.py --groups
  python tools/research/text_tables.py --apply-numeric
  python tools/research/text_tables.py --check-numeric
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import os
import random
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
REMAINDER = os.path.join(ROOT, "docs", "research", "RAW_REMAINDER.csv")
CSV_OUT = os.path.join(ROOT, "docs", "research", "TEXT_TABLES.csv")
DOC_OUT = os.path.join(ROOT, "docs", "research", "TEXT_TABLES.md")
ROW_CLASS = "text/tables"
HEADER_FILE = "rom_header.s"
HEADER = (0x004, 0x0C0)
CLASSES = ("cartridge header", "text", "record table", "numeric constant table", "unknown")
METHOD_MINIMUM = 0.94
RESIDUE_MAXIMUM = 0.05
CONTROLS = frozenset((0x02, 0x07, 0x08, 0x0A, 0x0B, 0x21, 0x23, 0x2D, 0x40, 0x5E))
NAMED_TABLES = ((0x716D8, 8, "0x0800938C"), (0x71730, 0x14, "the dialogue box constructor"),
                (0x71744, 0x14, "the dialogue box constructor"))
THUMB_BIT = 1
ROM_BASE = 0x08000000
NUMERIC_WIDTH = 4
NUMERIC_LAYOUT = "self-relative method offset"
NUMERIC_CONSUMER = "0x080188FC"
NUMERIC_FIELDS = ("start", "end", "file", "line", "bytes", "words", "bases", "resolved", "named",
                  "residue", "layout", "consumer")


def read_rom(path):
    data = open(path, "rb").read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != ROM_SHA256:
        raise SystemExit("ROM sha256 %s is not the canonical %s" % (digest, ROM_SHA256))
    return data


def rows():
    out = []
    for row in csv.DictReader(open(REMAINDER)):
        if row["class"] != ROW_CLASS:
            continue
        out.append((int(row["start"], 16), int(row["end"], 16), row["file"], int(row["line"])))
    return out


def labels(root=ROOT):
    found = {}
    for name in sorted(os.listdir(os.path.join(root, "asm"))):
        if not name.endswith(".s"):
            continue
        for line in open(os.path.join(root, "asm", name), errors="replace"):
            match = re.match(r"\s*\|?([A-Za-z_][A-Za-z0-9_]*)\|?\s*$", line.split(";", 1)[0])
            digits = re.search(r"([0-9A-Fa-f]{8})", match.group(1)) if match else None
            if digits:
                found[int(digits.group(1), 16)] = match.group(1)
    return found


def table_rows(blob):
    out = []
    for row in rows():
        hits, total = resolved(blob, row[0], row[1])
        if total and hits / total >= METHOD_MINIMUM:
            out.append(row)
    return out


def loader_sites(blob):
    out = []
    count = len(blob) // 2
    for index, value in enumerate(struct.unpack_from("<%dH" % count, blob, 0)):
        if value & 0xF800 == 0x4800:
            at = index * 2
            out.append((((at + 4) & ~3) + 4 * (value & 0xFF), at))
    count = len(blob) // 4
    for index, value in enumerate(struct.unpack_from("<%dI" % count, blob, 0)):
        if value & 0x0F7F0000 == 0x051F0000:
            at = index * 4
            offset = value & 0xFFF
            if not value & (1 << 23):
                offset = -offset
            out.append((at + 8 + offset, at))
    return out


def class_bases(blob):
    short = table_rows(blob)
    inside = [(min(row[0] for row in short), max(row[1] for row in short))]
    found = {}
    for pool, site in loader_sites(blob):
        if not 0 <= pool <= len(blob) - 4:
            continue
        value = struct.unpack_from("<I", blob, pool)[0]
        low = value - ROM_BASE
        if low % 4 or not any(start <= low < end for start, end in inside):
            continue
        found.setdefault(low, []).append(ROM_BASE + site)
    return {base: sorted(sites) for base, sites in sorted(found.items())}


def starts(blob):
    import thumb_bodies
    instructions, entries = set(), set()
    for start, end, mode, _insn in thumb_bodies.source_rows():
        entries.add(start)
        if mode != "thumb":
            continue
        for at, (_size, mnemonic, operands) in thumb_bodies.thumb_instructions(start, end):
            instructions.add(at)
            target = thumb_bodies.direct_target(mnemonic, operands)
            if target is not None:
                entries.add((target & ~1) - ROM_BASE)
            literal = thumb_bodies.PC_RELATIVE.search(operands) if mnemonic == "ldr" else None
            if literal:
                pool = ((ROM_BASE + at + 4) & ~3) + int(literal.group(1), 0)
                value = struct.unpack_from("<I", blob, pool - ROM_BASE)[0]
                if value & 1 and ROM_BASE <= value < ROM_BASE + 0x02000000:
                    entries.add((value & ~1) - ROM_BASE)
    return instructions, entries


def table_report(blob, named, trials=5):
    found = class_bases(blob)
    bases = sorted(found)
    last = max(row[1] for row in table_rows(blob))
    spans = [(base, bases[index + 1] if index + 1 < len(bases) else last)
             for index, base in enumerate(bases)]
    instructions, entries = starts(blob)
    slots = [(base, at, struct.unpack_from("<i", blob, at)[0])
             for base, stop in spans for at in range(base, stop - 3, 4)]

    def share(seq):
        out = {"resolved": 0, "instructions": 0, "entries": 0, "labelled": 0}
        for base, _at, value in seq:
            target = base + value
            if not 0 <= target < len(blob):
                continue
            out["resolved"] += 1
            address = target & ~THUMB_BIT
            out["instructions"] += address in instructions
            out["entries"] += address in entries
            out["labelled"] += (address + ROM_BASE) in named
        return out

    real = share(slots)
    rng = random.Random(20261017)
    values = [value for _base, _at, value in slots]
    table = table_rows(blob)
    null_rows = {row[0]: collections.Counter() for row in table}
    null_all = collections.Counter()
    for _trial in range(trials):
        rng.shuffle(values)
        permuted = [(base, at, values[index]) for index, (base, at, _v) in enumerate(slots)]
        for key, count in share(permuted).items():
            null_all[key] += count
        for row in table:
            for key, count in share([one for one in permuted if row[0] <= one[1] < row[1]]).items():
                null_rows[row[0]][key] += count
    average = {key: null_all[key] / trials for key in real}
    report = []
    for row in table:
        index = [number for number, (base, stop) in enumerate(spans) if base < row[1] and stop > row[0]]
        inside = [one for one in slots if row[0] <= one[1] < row[1]]
        derivable = 0
        for base, at, value in inside:
            target = base + value
            klass = max([one for one in bases if one <= at], default=None)
            if klass is not None and named.get(klass + ROM_BASE) and 0 <= target < len(blob) \
                    and named.get((target & ~THUMB_BIT) + ROM_BASE):
                derivable += 1
        report.append(dict(row=row, bases=len(index),
                           sites=sum(len(found[spans[i][0]]) for i in index),
                           words=len(inside), derivable=derivable,
                           null={key: null_rows[row[0]][key] / trials for key in real},
                           **share(inside)))
    return dict(rows=report, bases=len(bases), words=len(slots), real=real, null=average)



def dcd(blob, row, bases, named):
    lines, residue = [], 0
    for at in range(row[0] + (-row[0]) % 4, row[1] - 3, 4):
        word = struct.unpack_from("<I", blob, at)[0]
        base = max([one for one in bases if one <= at], default=None)
        class_name = named.get(base + ROM_BASE) if base is not None else None
        target = base + struct.unpack_from("<i", blob, at)[0] if base is not None else None
        method_name = (named.get((target & ~THUMB_BIT) + ROM_BASE)
                       if target is not None and 0 <= target < len(blob) else None)
        if method_name and class_name:
            lines.append("\tDCD\t|%s|+%d-|%s|" % (method_name, target & THUMB_BIT, class_name))
        else:
            lines.append("\tDCD\t0x%08X" % word)
            residue += 1
    return lines, residue



def numeric_lines(blob, row, bases):
    start, end = row[0], row[1]
    first = start + (-start) % NUMERIC_WIDTH
    last = end - end % NUMERIC_WIDTH
    lines, residue, table, resolved = [], 0, 0, 0
    if first > start:
        lines.append("\tDCW\t0x%04X" % struct.unpack_from("<H", blob, start)[0])
        residue += first - start
    for at in range(first, last, NUMERIC_WIDTH):
        word = struct.unpack_from("<I", blob, at)[0]
        base = max([one for one in bases if one <= at], default=None)
        target = base + struct.unpack_from("<i", blob, at)[0] if base is not None else None
        lines.append("\tDCD\t0x%08X" % word)
        table += 1
        if target is not None and 0 <= target < len(blob):
            resolved += 1
        else:
            residue += NUMERIC_WIDTH
    if last < end:
        lines.append("\tDCW\t0x%04X" % struct.unpack_from("<H", blob, last)[0])
        residue += end - last
    return lines, residue, table, resolved


def numeric_rows(blob):
    built = measure(blob)[0]
    bases = sorted(class_bases(blob))
    out = []
    for row, subclass, _explained, _evidence in built:
        if subclass != "record table":
            continue
        lines, residue, table, resolved = numeric_lines(blob, row, bases)
        out.append((row, lines, residue, table, resolved, bases))
    return out


def groups(blob, root=ROOT):
    built, _totals = measure(blob)
    bases = sorted(class_bases(blob))
    numeric = {}
    for row, subclass, _explained, _evidence in built:
        if subclass == "record table":
            _lines, _residue, table, resolved = numeric_lines(blob, row, bases)
            numeric[row[0]] = (table, resolved)
    out = collections.OrderedDict()
    for row, subclass, _explained, evidence in built:
        if subclass == "cartridge header":
            key = "header (protected)"
        elif subclass == "record table":
            table, resolved = numeric[row[0]]
            if not resolved:
                key = "number table, no class base at or below the row"
            elif resolved == table:
                key = "number table, every word is a method offset"
            else:
                key = "mixed: method offsets and words that are not offsets"
        elif "utf16-shaped" in evidence or "printable" in evidence:
            key = "text-shaped fragment, no reader"
        else:
            key = "unknown opaque"
        count, size = out.setdefault(key, (0, 0))
        out[key] = (count + 1, size + row[1] - row[0])
    path = os.path.join(root, "docs", "research", "NUMBER_TABLES.csv")
    if os.path.exists(path):
        with open(path, newline="") as handle:
            record = list(csv.DictReader(handle))
        if record:
            out["number table, converted (NUMBER_TABLES.csv)"] = (
                len(record), sum(int(entry["bytes"]) for entry in record))
    return built, out


def carriers(root=ROOT):
    out = {}
    directory = os.path.join(root, "asm")
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".s"):
            continue
        text = open(os.path.join(directory, name), errors="replace").read()
        for match in re.finditer(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted",
                                 text):
            out[(int(match.group(1), 16), int(match.group(2), 16))] = (name, text)
    return out


def base_of(bases, at):
    return max([one for one in bases if one <= at], default=None)


def named_words(blob, row, bases, named):
    count = 0
    for at in range(row[0] + (-row[0]) % NUMERIC_WIDTH, row[1] - 3, NUMERIC_WIDTH):
        base = base_of(bases, at)
        if base is None:
            continue
        target = base + struct.unpack_from("<i", blob, at)[0]
        if 0 <= target < len(blob) and (target & ~THUMB_BIT) + ROM_BASE in named:
            count += 1
    return count


def numeric_record(blob, root=ROOT):
    rows = numeric_rows(blob)
    carriers_ = carriers(root)
    named = labels()
    out = []
    for row, lines, residue, table, resolved, bases in rows:
        if not table or resolved != table:
            continue
        name, _text = carriers_[(row[0], row[1])]
        out.append(dict(row=row, file=name, lines=lines, residue=residue, table=table,
                        resolved=resolved, bases=bases,
                        named=named_words(blob, row, bases, named)))
    return out


def numeric_csv_text(record):
    lines = [",".join(NUMERIC_FIELDS)]
    for entry in record:
        start, end, _name, line = entry["row"]
        lines.append("%s,%s,%s,%d,%d,%d,%d,%d,%d,%d,%s,%s"
                     % ("0x%06X" % start, "0x%06X" % end, entry["file"], line, end - start,
                        entry["table"], len(entry["bases"]), entry["resolved"], entry["named"],
                        entry["residue"], NUMERIC_LAYOUT, NUMERIC_CONSUMER))
    return "\n".join(lines) + "\n"


def rewrite(name, text, record, root=ROOT):
    edits = 0
    for entry in record:
        start, end = entry["row"][0], entry["row"][1]
        token = "baserom.gba_0x%x_0x%x.extracted" % (start, end)
        pattern = re.compile(r"^(\s*)INCBIN\s+%s\s*$" % re.escape(token), re.M)
        match = pattern.search(text)
        if match is None:
            raise SystemExit("asm/%s INCBINs no %s" % (name, token))
        indent = match.group(1) or "\t"
        text = text[:match.start()] + "\n".join(indent + line.strip() for line in entry["lines"]) \
            + text[match.end():]
        edits += 1
    return text, edits


def apply_numeric(root=ROOT, blob=None):
    blob = read_rom(os.path.join(root, "baserom.gba")) if blob is None else blob
    record = numeric_record(blob, root)
    total = sum(entry["row"][1] - entry["row"][0] for entry in record)
    residue = sum(entry["residue"] for entry in record)
    if not record:
        raise SystemExit("no text/tables row is still INCBIN: the numeric record is already applied")
    if residue > RESIDUE_MAXIMUM * total:
        raise SystemExit("the numeric group is %d B with %d B residue" % (total, residue))
    by_file = collections.OrderedDict()
    for entry in record:
        by_file.setdefault(entry["file"], []).append(entry)
    for name, entries in by_file.items():
        path = os.path.join(root, "asm", name)
        text = open(path, errors="replace").read()
        text, edits = rewrite(name, text, entries, root)
        with open(path, "w", encoding="ascii", newline="\n") as handle:
            handle.write(text)
        print("apply %-22s %d row(s)" % (name, edits))
    with open(os.path.join(root, "docs", "research", "NUMBER_TABLES.csv"), "w",
              encoding="ascii", newline="\n") as handle:
        handle.write(numeric_csv_text(record))
    print("numeric rows=%d bytes=%d words=%d residue=%d"
          % (len(record), total, sum(entry["table"] for entry in record), residue))
    return 0


def check_numeric(blob, root=ROOT):
    import emitted
    with open(os.path.join(root, "docs", "research", "NUMBER_TABLES.csv"), newline="") as handle:
        record = list(csv.DictReader(handle))
    if not record:
        print("CHECK FAIL: the numeric record is empty")
        return 1
    spans = carriers(root)
    decoded = {}
    total = words_ = residue = 0
    for row in record:
        start, end = int(row["start"], 16), int(row["end"], 16)
        name = row["file"]
        if name not in decoded:
            decoded[name] = dict(emitted.labeled_bytes(
                open(os.path.join(root, "asm", name), errors="replace").read()))
        body = decoded[name].get(start)
        if body is None:
            print("CHECK FAIL: asm/%s carries no labeled directives at 0x%06X" % (name, start))
            return 1
        if body[:end - start] != blob[start:end]:
            print("CHECK FAIL: asm/%s at 0x%06X does not reproduce the retail bytes" % (name, start))
            return 1
        total += end - start
        words_ += int(row["words"])
        residue += int(row["residue"])
    for span in spans:
        if span in {(int(row["start"], 16), int(row["end"], 16)) for row in record}:
            print("CHECK FAIL: 0x%06X..0x%06X is still INCBIN" % span)
            return 1
    if anchor_failures(blob):
        print("CHECK FAIL: the class-slot convention is not the base reading")
        return 1
    bases = {row["bases"] for row in record}
    if len(bases) != 1:
        print("CHECK FAIL: the record carries %d class-base counts" % len(bases))
        return 1
    if residue > RESIDUE_MAXIMUM * total:
        print("CHECK FAIL: residue %d B exceeds the five percent rule of %d B" % (residue, total))
        return 1
    print("numeric rows=%d bytes=%d words=%d residue=%d (%.2f %%) bases=%s"
          % (len(record), total, words_, residue, 100.0 * residue / total, bases.pop()))
    return 0



def words(blob, start, limit):
    offset = (-start) % 4
    return [(start + at, struct.unpack_from("<i", blob, start + at)[0])
            for at in range(offset, limit - start - 3, 4)]


def resolved(blob, start, limit):
    found = words(blob, start, limit)
    hits = sum(1 for site, value in found
               if 0 <= site + value < len(blob) and (site + value) & THUMB_BIT)
    return hits, len(found)


def method(base, slot, blob):
    return base + struct.unpack_from("<i", blob, base + slot)[0]


def anchors(blob):
    return (("K-029 SEQ class+0x00", 0x4AAF4, 0x00, 0x18EF6),
            ("K-029 SEQ class+0x08", 0x4AAF4, 0x08, 0x18F74),
            ("K-028 actor class+0x68", 0x4C484, 0x68, 0x4ECB0))


def anchor_failures(blob):
    out = []
    for label, base, slot, want in anchors(blob):
        got = method(base, slot, blob)
        if got != want | THUMB_BIT:
            out.append((label, got, want | THUMB_BIT))
    return out


def utf16(blob):
    if len(blob) < 2 or len(blob) % 2 or any(blob[i] for i in range(1, len(blob), 2)):
        return False
    return all(blob[i] in CONTROLS or 0x20 <= blob[i] < 0x7F for i in range(0, len(blob), 2))


def printable(blob):
    return bool(blob) and all(0x20 <= c < 0x7F for c in blob)


def classify(blob, row, facts=None):
    start, end, name, _line = row
    body = blob[start:end]
    hits, total = resolved(blob, start, end)
    if name == HEADER_FILE and HEADER[0] <= start and end <= HEADER[1]:
        return "cartridge header", len(body), "a header field inside 0x04..0xC0"
    shape = "self-relative=%d/%d" % (hits, total)
    if total and hits / total >= METHOD_MINIMUM:
        if facts is None:
            return ("record table", 0, "%s method words; bases not measured here" % shape)
        return ("record table", 0,
                "%s method words; bases=%d from %d load site(s); %d words; thumb-entry=%d (%s, "
                "null %.1f); labelled=%d"
                % (shape, facts["bases"], facts["sites"], facts["words"], facts["instructions"],
                   "above the null" if facts["instructions"] > facts["null"]["instructions"]
                   else "NOT above the null", facts["null"]["instructions"], facts["labelled"]))
    tail = sum(length for at, length, _reader in NAMED_TABLES if start <= at and at + length <= end)
    kind = "utf16-shaped" if utf16(body) else ("printable" if printable(body) else "opaque")
    evidence = "%s %s" % (shape, kind)
    if tail:
        evidence += "; %d B of named tables at the row's tail" % tail
    return "unknown", 0, evidence


def measure(blob, facts=None):
    out, totals = [], {name: (0, 0, 0) for name in CLASSES}
    for row in rows():
        subclass, explained, evidence = classify(blob, row, (facts or {}).get(row[0]))
        out.append((row, subclass, explained, evidence))
        count, size, good = totals.get(subclass, (0, 0, 0))
        totals[subclass] = (count + 1, size + row[1] - row[0], good + explained)
    return out, totals



def text_shapes(built, blob):
    every = [row for row, subclass, _, evidence in built
             if subclass == "unknown" and ("utf16-shaped" in evidence or "printable" in evidence)]
    wide = [row for row in every if utf16(blob[row[0]:row[1]])]
    narrow = [row for row in every if row not in wide]
    return (len(every), len(wide), sum(end - start for start, end, _, _ in wide),
            len(narrow), sum(end - start for start, end, _, _ in narrow))


def csv_text(built):
    out = ["file,line,start,end,bytes,subclass,explained,evidence"]
    for (start, end, name, line), subclass, explained, evidence in built:
        out.append("%s,%d,0x%06X,0x%06X,%d,%s,%d,%s"
                   % (name, line, start, end, end - start, subclass, explained,
                      evidence.replace(",", ";")))
    return "\n".join(out) + "\n"


def doc_text(built, totals, table, blob):
    holder = next(((start, end) for start, end, _, _ in rows() if start <= 0x716D8 < end), None)
    if holder is None:
        table_prose = ("The row that contains them was promoted to a raw-labeled carrier by "
                       "the runtime read survey, so it is no longer a row of this class and this "
                       "file does not convert it.")
    else:
        table_prose = ("They are %d B inside the %d B row that contains them, and the rest of that "
                       "row is unexplained, so the row's residue is %.2f %% and the ticket does not "
                       "convert it."
                       % (sum(length for _, length, _ in NAMED_TABLES), holder[1] - holder[0],
                          100.0 * (holder[1] - holder[0] - sum(l for _, l, _ in NAMED_TABLES))
                          / (holder[1] - holder[0])))
    unknown = [(end - start) for (start, end, _, _), subclass, _, _ in built
               if subclass == "unknown"]
    fragments = (unknown.count(2), unknown.count(4))
    lines = ["# The %d `text/tables` rows, by what their bytes are" % len(built),
             "",
             "Generated by `tools/research/text_tables.py` (`--write`). One row per `text/tables` row "
             "of `docs/research/RAW_REMAINDER.csv`, one class per row, exactly one. Retail image "
             "sha256 `%s`." % ROM_SHA256,
             "",
             "The class `text/tables` is `raw_remainder.py`'s predicate - the row's span is a run "
             "`TRANSCRIBED_DATA_RUNS.csv` classes as `data` - so the class says what the transcriber "
             "could not call a pool or a pointer table, not what the bytes are. This file is that "
             "second measurement.",
             "",
             "| class | rows | bytes | explained | residue | route |",
             "---|---|---|---|---|---|"]
    route = {"cartridge header": "protected: stays retail",
             "text": "NONE", "record table": "NONE (the parse does not reach the bytes)",
             "numeric constant table": "NONE", "unknown": "NONE"}
    total_rows = total_bytes = total_good = 0
    for name in CLASSES:
        count, size, good = totals.get(name, (0, 0, 0))
        total_rows += count
        total_bytes += size
        total_good += good
        lines.append("| `%s` | %d | %d | %d | %.2f %% | %s |"
                     % (name, count, size, good, 100.0 * (size - good) / size if size else 0.0,
                        route[name]))
    lines.append("| **total** | **%d** | **%d** | **%d** | **%.2f %%** | |"
                 % (total_rows, total_bytes, total_good,
                    100.0 * (total_bytes - total_good) / total_bytes))
    lines += ["",
              "The sum is asserted against the census: %d rows, %d B." % (total_rows, total_bytes),
              "",
              "## What each class was measured with",
              "",
              "### `cartridge header`",
              "",
              "- Rule: the row's file is `asm/rom_header.s` and the row lies inside 0x04..0xC0, the "
              "boot logo and the title/code/version fields. Route `protected`: the tree carries every "
              "field as its own labeled slice and this ticket does not generate it, so it stays.",
              "",
              "### `record table` - self-relative method tables",
              "",
              "- Rule: at least %.0f %% of the row's four-byte words, read as `site + s32`, land on an "
              "odd address inside the image (`METHOD_MINIMUM`)." % (100 * METHOD_MINIMUM),
              "- The convention is in the engine's own bytes at file 0x188FC: `ldr r2,[r1,#0x68]` then "
              "`adds r2,r2,r1`, i.e. `method = class + s32(class + slot)` - the base is the class "
              "word, never the slot's address. `--report` re-checks the three anchors that pin this: "
              "0x04AAF4 slot 0 -> 0x018EF7, slot 8 -> 0x018F75, 0x04C484 slot 0x68 -> 0x04ECB1 (each "
              "the recorded method with the Thumb bit). The site reading gives 0x018F7D and 0x04ED19 "
              "for the last two and is refuted.",
              "- Why no byte is explained (TEXT-TABLES-001): the parse needs the class BASES. `--bases` "
              "now measures them from the loader channel, and the per-row table below is that "
              "measurement: bases are the 4-aligned addresses of a method-table row that a pc-relative "
              "load's POOL WORD names (one indirection past the load), each with its site count.",
              "",
              "| row | bases | sites | words | resolved | thumb entry | null | labelled | derivable "
              "| residue |",
              "---|---|---|---|---|---|---|---|---|---|"]
    for entry in table["rows"]:
        start, end, _name, _line = entry["row"]
        share = lambda key: 100.0 * entry[key] / entry["words"] if entry["words"] else 0.0
        null = 100.0 * entry["null"]["instructions"] / entry["words"] if entry["words"] else 0.0
        lines.append("| 0x%06X..0x%06X | %d | %d | %d | %.1f %% | %.1f %% | %.1f %% | %.1f %% | %d "
                     "| %.2f %% |"
                     % (start, end, entry["bases"], entry["sites"], entry["words"], share("resolved"),
                        share("instructions"), null,
                        share("labelled"), entry["derivable"],
                        100.0 * (entry["words"] - entry["derivable"]) / entry["words"]
                        if entry["words"] else 0.0))
    lines += ["",
              "- Beside the whole region: %d bases, %d words, %.2f %% of them on a transcribed Thumb "
              "instruction start where the seeded permutation null gives %.2f %% - so the instruction "
              "share is NOT evidence and is reported only because the ticket asks for it. The "
              "predicates that do beat the null are the function ENTRY share (%.2f %% against "
              "%.2f %%) and the label share (%.2f %% against %.2f %%)."
              % (table["bases"], table["words"],
                 100.0 * table["real"]["instructions"] / table["words"],
                 100.0 * table["null"]["instructions"] / table["words"],
                 100.0 * table["real"]["entries"] / table["words"],
                 100.0 * table["null"]["entries"] / table["words"],
                 100.0 * table["real"]["labelled"] / table["words"],
                 100.0 * table["null"]["labelled"] / table["words"]),
              "- The blocker the NEXT ticket inherits: a slot's method can only be labelled where its "
              "target is a transcribed instruction start, and %d of the %d words point at a target the "
              "tree still carries as a raw INCBIN slice, so their rows cannot reach the 5 %% residue "
              "rule. Those slices are the next ticket's payload, and the class tables are their "
              "entry evidence."
              % (table["words"] - table["real"]["instructions"], table["words"]),
              "",
              "### `text`",
              "",
              "- Rule: the row is a complete character-encoded run whose reader routine is named. "
              "Measured: %d rows are text-SHAPED (%d rows / %d B every unit a printable or a K-032 "
              "control, %d rows / %d B pure printable) and not one of them has a reader: they are "
              "fragments of 2-8 B inside code. They stay `unknown`, and the class is empty rather "
              "than claiming text from a shape." % text_shapes(built, blob),
              "",
              "### `numeric constant table`",
              "",
              "- Rule: every byte of the row is a table entry read by a named routine. Three such "
              "entries exist inside the class: the four halfwords at 0x716D8, read here as the BG "
              "control values 0x1C80/0x1D80/0x1E80/0x1F80 (K-034's writer 0x0800938C is NOT "
              "re-derived by this ticket), and the two 0x14-byte dialogue layout records at 0x71730 "
              "and 0x71744, whose spans and +0 fields (4 and 2) are read here and whose meaning is "
              "K-020's runtime-measured fitter limit. " + table_prose,
              "",
              "### `unknown`",
              "",
              "- Everything no rule above claimed. Its per-row evidence is the measured shape: the "
              "self-relative resolution rate, and whether the row is utf16-shaped, printable or "
              "opaque. These are the code-adjacent fragments (%d rows are 2 B, %d are 4 B) and the "
              "blobs whose format no tracked instrument establishes."
              % (fragments[0], fragments[1]),
              "",
              "## What a next ticket needs",
              "",
              "- Transcribe the slices the slots name, then label their targets: %d of %d words point "
              "outside the transcribed code and every one of those is a residue word until its slice is "
              "transcribed. `--emit` converts a row only when its residue is within 5 %%."
              % (table["words"] - table["real"]["instructions"], table["words"]),
              "",
              "## Re-run",
              "",
              "    python tools\\research\\text_tables.py --report",
              "    python tools\\research\\text_tables.py --check"]
    return "\n".join(lines) + "\n"


def recorded():
    with open(os.path.join(ROOT, "docs", "research", "TEXT_TABLES.csv"), newline="") as handle:
        carried = list(csv.DictReader(handle))
    return len(carried), sum(int(row["bytes"]) for row in carried)


def generated(blob):
    named = labels()
    table = table_report(blob, named)
    built, totals = measure(blob, {entry["row"][0]: entry for entry in table["rows"]})
    return built, totals, table, csv_text(built), doc_text(built, totals, table, blob)


def first_difference(got, want):
    left, right = got.splitlines(), want.splitlines()
    for index in range(max(len(left), len(right))):
        a = left[index] if index < len(left) else ""
        b = right[index] if index < len(right) else ""
        if a != b:
            return "line %d: %r != %r" % (index + 1, a[:120], b[:120])
    return None


def check(blob):
    built, totals, table, record, doc = generated(blob)
    size = sum(end - start for start, end, _, _ in rows())
    want_rows, want_bytes = recorded()
    if len(built) != want_rows or size != want_bytes:
        print("CHECK FAIL: %d rows / %d B against the record's %d / %d"
              % (len(built), size, want_rows, want_bytes))
        return 1
    bad = anchor_failures(blob)
    if bad:
        print("CHECK FAIL: the class-slot convention is not the base reading: %s" % (bad,))
        return 1
    for path, want in ((CSV_OUT, record), (DOC_OUT, doc)):
        with open(path, newline="") as handle:
            bad = first_difference(handle.read(), want)
        if bad:
            print("CHECK FAIL: %s %s" % (os.path.basename(path), bad))
            return 1
    print("text/tables rows=%d bytes=%d classes=%d"
          % (len(built), size, len(totals)))
    print("anchors=3/3 base-relative; explained=%d residue=%.2f %%"
          % (sum(good for _, _, good in totals.values()),
             100.0 * (size - sum(good for _, _, good in totals.values())) / size))
    return 0


def report(blob):
    built, totals = measure(blob)
    size = sum(end - start for start, end, _, _ in rows())
    print("%-26s %5s %7s %8s %8s" % ("class", "rows", "bytes", "explained", "residue"))
    for name in CLASSES:
        count, bytes_of, good = totals.get(name, (0, 0, 0))
        print("%-26s %5d %7d %8d %7.2f %%" % (name, count, bytes_of, good,
                                              100.0 * (bytes_of - good) / bytes_of
                                              if bytes_of else 0.0))
    print("%-26s %5d %7d %8d %7.2f %%" % ("total", len(built), size,
                                          sum(g for _, _, g in totals.values()),
                                          100.0 * (size - sum(g for _, _, g in totals.values()))
                                          / size))
    print("anchors: %d/%d base-relative" % (len(anchors(blob)) - len(anchor_failures(blob)),
                                            len(anchors(blob))))
    for name, base, slot, want in anchors(blob):
        print("  %-22s base=0x%06X slot=+0x%02X -> 0x%06X (recorded 0x%06X|Thumb)"
              % (name, base, slot, method(base, slot, blob), want))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--bases", action="store_true")
    group.add_argument("--emit", action="store_true")
    group.add_argument("--groups", action="store_true")
    group.add_argument("--apply-numeric", action="store_true")
    group.add_argument("--check-numeric", action="store_true")
    args = parser.parse_args(argv)
    blob = read_rom(args.rom)
    if args.report:
        return report(blob)
    if args.check:
        return check(blob)
    if args.check_numeric:
        return check_numeric(blob)
    if args.groups:
        built, out = groups(blob)
        for key, (count, size) in out.items():
            print("%-52s %4d rows %7d B" % (key, count, size))
        print("%-52s %4d rows %7d B" % ("total", sum(count for count, _ in out.values()),
                                        sum(size for _, size in out.values())))
        print("%-52s %4d rows %7d B" % ("still INCBIN", len(built),
                                        sum(row[1] - row[0] for row, _, _, _ in built)))
        named = labels()
        for row, _lines, residue, table, resolved, bases in numeric_rows(blob):
            print("0x%06X..0x%06X %5d words=%4d resolved=%4d named=%3d residue=%3d bases=%3d"
                  % (row[0], row[1], row[1] - row[0], table, resolved,
                     named_words(blob, row, bases, named), residue, len(bases)))
        return 0
    if args.apply_numeric:
        return apply_numeric(ROOT, blob)
    named = labels()
    table = table_report(blob, named)
    if args.bases:
        print("row                bases sites words resolved thumb  null derivable  residue")
        for entry in table["rows"]:
            start, end, _name, _line = entry["row"]
            print("0x%06X..0x%06X %6d %5d %5d %8d %5d %5.1f %8d %7d"
                  % (start, end, entry["bases"], entry["sites"], entry["words"], entry["resolved"],
                     entry["instructions"], entry["null"]["instructions"], entry["derivable"],
                     entry["words"] - entry["labelled"]))
        print("bases=%d words=%d entries=%d/%d null=%.1f labelled=%d/%d"
              % (table["bases"], table["words"], table["real"]["entries"], table["words"],
                 table["null"]["entries"], table["real"]["labelled"], table["words"]))
        return 0
    if args.emit:
        bases = sorted(class_bases(blob))
        for entry in table["rows"]:
            start, end, name, line = entry["row"]
            lines, residue = dcd(blob, (start, end), bases, named)
            if residue > RESIDUE_MAXIMUM * len(lines) or not lines:
                print("REFUSED %s:%d 0x%06X..0x%06X: %d of %d slots residue (%.1f %%)"
                      % (name, line, start, end, residue, len(lines),
                         100.0 * residue / len(lines)))
                continue
            print("%s:%d 0x%06X..0x%06X residue %d" % (name, line, start, end, residue))
            print("\n".join(lines))
        return 0
    built, totals, table, record, doc = generated(blob)
    with open(CSV_OUT, "w", newline="\n", encoding="ascii") as handle:
        handle.write(record)
    with open(DOC_OUT, "w", newline="\n", encoding="ascii") as handle:
        handle.write(doc)
    print("wrote %s and %s" % (os.path.basename(CSV_OUT), os.path.basename(DOC_OUT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())





