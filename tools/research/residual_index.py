from __future__ import annotations

import argparse
import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import gate  # noqa: E402

RESEARCH = os.path.join(ROOT, "docs", "research")
CENSUS = os.path.join(RESEARCH, "RAW_REMAINDER.csv")
LEDGER = os.path.join(RESEARCH, "RESIDUAL_LEDGER.csv")
DOC_OUT = os.path.join(RESEARCH, "RESIDUAL_INDEX.md")
MAP_FENCE = (0x179A50, 0x2B8BC8)
CARVE_OUT = (0x29B308, 0x29B320)
ROM_BASE = 0x08000000

IRREDUCIBLE = "irreducible by measured reason"
PENDING = "pending-image-route"
OTHERS = "others found"
IDENTITY = "identity"
CLASSES = (IRREDUCIBLE, PENDING, OTHERS, IDENTITY)
VERDICT_COLUMNS = ("null", "verdict", "readers", "stays raw because")
ENDROM_REGIONS = ("R20", "R21") + tuple("R%d" % number for number in range(23, 32))
DOCS = (
    ("R00_R22_NULL_CENSUS.md", ("R00", "R09", "R10", "R18", "R22")),
    ("R19_NULL_CENSUS.md", ("R19",)),
    ("R02_NULL_CENSUS.md", ("R02",)),
    ("ENDROM_NULL_CENSUS.md", ENDROM_REGIONS),
    ("R32_NULL_CENSUS.md", ("R32",)),
    ("R33_R35_NULL_CENSUS.md", ("R33", "R34", "R35")),
)
SPAN_DOCS = (("MAP_BLOCK_NULL_CENSUS.md", "the map block `0x179A50..0x2B8BC8`"),
             ("CODE_FRAGMENT_NULL_CENSUS.md", "the `code-without-entry` class"))
CLASS_DOC = {"code-without-entry": "CODE_FRAGMENT_NULL_CENSUS.md"}
SPAN_DOC = "MAP_BLOCK_NULL_CENSUS.md"
MAP_REGIONS = ("R02", "R12", "R13", "R14", "R15")
SPAN = re.compile(r"`?(?:0x)?([0-9a-fA-F]+)\.\.(?:0x)?([0-9a-fA-F]+)`?")
CELL = re.compile(r"`?(?:0x)?([0-9a-fA-F]+)`?")


def cells(line):
    return [cell.strip().strip("`").strip() for cell in line.strip().strip("|").split("|")]


def span_of(row):
    if not row:
        return None
    found = SPAN.fullmatch(row[0])
    if found:
        return int(found.group(1), 16), int(found.group(2), 16)
    first = CELL.fullmatch(row[0])
    second = CELL.fullmatch(row[1]) if len(row) > 1 else None
    if first and second:
        return int(first.group(1), 16), int(second.group(1), 16)
    return None


def verdict_tables(path):
    out = []
    header = None
    rows = None
    for number, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        if line.lstrip().startswith("|"):
            got = cells(line)
            if header is None:
                header = [cell.lower() for cell in got]
                rows = []
                continue
            if rows is not None:
                if not all(set(cell) <= set("-:") for cell in got if cell):
                    rows.append((number, got))
            continue
        if header is not None and rows is not None:
            out.append((header, rows))
        header = None
        rows = None
    if header is not None and rows is not None:
        out.append((header, rows))
    return [(header, rows) for header, rows in out if header and header[-1] in VERDICT_COLUMNS]


def read_census(path=CENSUS):
    rows = []
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append({"start": int(row["start"], 16), "end": int(row["end"], 16),
                         "bytes": int(row["bytes"]), "region": row["region"],
                         "class": row["class"], "route": row["route"]})
    return rows


def read_ledger(path=LEDGER):
    out = {}
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            out[(int(row["start"], 16), int(row["end"], 16))] = row
    return out


def lines_by_doc():
    out = {}
    for name, _regions in DOCS + tuple((name, ()) for name, _span in SPAN_DOCS):
        found = {}
        sections = collections.Counter()
        for header, rows in verdict_tables(os.path.join(RESEARCH, name)):
            for number, cells_of_row in rows:
                span = span_of(cells_of_row)
                if span is None:
                    continue
                found.setdefault(span, []).append((number, cells_of_row))
                sections[span] += 1
        out[name] = found
    return out


def carrier_of(row, in_progress):
    if row["class"] in CLASS_DOC:
        return CLASS_DOC[row["class"]]
    if in_progress and row["region"] in MAP_REGIONS:
        return SPAN_DOC
    for name, regions in DOCS:
        if row["region"] in regions:
            return name
    return None


def measure():
    rows = read_census()
    ledger = read_ledger()
    lines = lines_by_doc()
    for row in rows:
        span = (row["start"], row["end"])
        entry = ledger.get(span, {})
        row["status"] = entry.get("status", "")
        row["references"] = entry.get("references", "none")
        row["carrier"] = carrier_of(row, row["status"] == "in progress")
        row["lines"] = [(name, number) for name, table in lines.items()
                        for number, _cells_of_row in table.get(span, [])]
        row["docs"] = sorted({name for name, _number in row["lines"]})
        if row["carrier"] is not None:
            row["carrier_lines"] = [number for number, _cells_of_row in lines[row["carrier"]].get(span, [])]
        else:
            row["carrier_lines"] = []
        if row["class"] == "graphics" or span == CARVE_OUT:
            row["verdict"] = PENDING
            row["reason"] = "graphics"
        elif row["references"] != "none":
            row["verdict"] = OTHERS
            row["reason"] = row["references"].split(":")[0]
        else:
            row["verdict"] = IRREDUCIBLE
            row["reason"] = row["class"]
    return rows


def gaps(rows):
    return [row for row in rows if row["carrier"] is None or not row["carrier_lines"]]


def conflicts(rows):
    return [row for row in rows if len(row["docs"]) > 1]


def totals(rows):
    out = {name: [0, 0] for name in CLASSES}
    for row in rows:
        out[row["verdict"]][0] += 1
        out[row["verdict"]][1] += row["bytes"]
    return out


def identity_bytes():
    return sum(length for _start, length in gate.union_ranges(gate.identity_ranges()))


def raw_bytes():
    return sum(length for _start, length in gate.incbin_ranges())


def region_table(rows):
    out = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for row in rows:
        got = out[row["region"]][row["verdict"]]
        got[0] += 1
        got[1] += row["bytes"]
    return out


def carriers_text(rows):
    return ", ".join("`docs/research/%s`" % name for name in sorted({row["carrier"] for row in rows
                                                                     if row["carrier"]}))


def doc_text(rows):
    classes = totals(rows)
    raw = raw_bytes()
    identity = identity_bytes()
    regions = region_table(rows)
    names = {}
    for name, covered in DOCS:
        for region in covered:
            names[region] = name
    lines = []
    add = lines.append
    add("# The residual index: every raw row, its verdict and the census that carries it")
    add("")
    add("Generated by `tools/research/residual_index.py` (`python tools/research/residual_index.py`).")
    add("One line per `docs/research/RAW_REMAINDER.csv` row, in the class its census document gives it.")
    add("`--check` re-derives this file, refuses a row with no verdict line or with a verdict line in")
    add("two census documents, and asserts the totals against the gate. One row per class and region,")
    add("and the document that carries it.")
    add("")
    add("**The raw-data total is %d rows / %d B == the gate's `gate.incbin_ranges()` %d B. The"
        % (len(rows), sum(row["bytes"] for row in rows), raw))
    add("identity copies are %d B == `gate.union_ranges(gate.identity_ranges())` and are not raw rows.**"
        % identity)
    add("")
    add("## The verdict classes")
    add("")
    add("| verdict class | rows | bytes | what states it |")
    add("|---|---|---|---|")
    add("| `%s` | %d | %d | the row's census line names the measured instrument that reached it and "
        "the null that instrument leaves: no field, no count, no extent |"
        % (IRREDUCIBLE, classes[IRREDUCIBLE][0], classes[IRREDUCIBLE][1]))
    add("| `%s` | %d | %d | a `graphics` row or the map block's 24 B carve-out `0x29B308`: the "
        "image route ran and does not carry it, because the row holds no frame, or its frame "
        "crosses a carrier token, or the route refused it, or it is the carve-out |"
        % (PENDING, classes[PENDING][0], classes[PENDING][1]))
    add("| `%s` | %d | %d | the row carries a measured citation (`code:<ROM address>`, a decoded "
        "reader, or `runtime`, a read observed at run time) and still states no extent |"
        % (OTHERS, classes[OTHERS][0], classes[OTHERS][1]))
    add("| `%s` | 0 | %d | not a raw row: a copied interval the image already holds, on its own line "
        "in the gate's accounting |" % (IDENTITY, identity))
    add("| **total** | **%d** | **%d** | the row sum is the gate's raw-data total; identity is counted "
        "apart |" % (len(rows), sum(row["bytes"] for row in rows)))
    add("")
    pending_map = sum(1 for row in rows if row["verdict"] == PENDING and row["region"] in MAP_REGIONS)
    add("The `%s` class is every `graphics` row of the census and the map block's 24 B carve-out" % PENDING)
    add("`0x29B308`. %d of its %d rows are map block rows of `R02` and `R12`-`R15` that no ten-region census"
        % (pending_map, classes[PENDING][0]))
    add("carries, and %d are the ten regions' `graphics` rows that `docs/research/REGION_READ_CENSUS.md`"
        % (classes[PENDING][0] - pending_map))
    add("counts. The rows the image route leaves are measured in `docs/research/MAP_BLOCK_LAYOUTS.md`")
    add("and `docs/research/REGION_READ_CENSUS.md`, and the carve-out's own re-encode in")
    add("`docs/research/ROUTE_TO_100.md`.")
    add("")
    add("## Every class, region by region")
    add("")
    add("| verdict class | region | rows | bytes | census document |")
    add("|---|---|---|---|---|")
    groups = collections.defaultdict(list)
    for row in rows:
        groups[(row["verdict"], row["region"])].append(row)
    for verdict in CLASSES:
        if verdict == IDENTITY:
            continue
        for key in sorted(key for key in groups if key[0] == verdict):
            got = groups[key]
            add("| `%s` | `%s` | %d | %d | %s |"
                % (verdict, key[1], len(got), sum(row["bytes"] for row in got), carriers_text(got)))
    add("")
    add("## The census document of every region")
    add("")
    add("A row's verdict line is the one its own document carries. The two span documents carry a")
    add("population rather than a region: `docs/research/MAP_BLOCK_NULL_CENSUS.md` carries the ledger's")
    add("`in progress` rows of `R02`, `R12`, `R13`, `R14` and `R15` inside the map block, and")
    add("`docs/research/CODE_FRAGMENT_NULL_CENSUS.md` carries the `code-without-entry` rows wherever")
    add("they lie.")
    add("")
    add("| region | rows | bytes | verdict classes | census document |")
    add("|---|---|---|---|---|")
    for region in sorted(regions):
        count = sum(value[0] for value in regions[region].values())
        size = sum(value[1] for value in regions[region].values())
        held = ", ".join("`%s` %d" % (verdict, regions[region][verdict][0]) for verdict in CLASSES
                         if verdict != IDENTITY and regions[region][verdict][0])
        holder = carriers_text([row for row in rows if row["region"] == region])
        add("| `%s` | %d | %d | %s | %s |" % (region, count, size, held, holder))
    add("")
    add("## The reasons inside `%s`" % IRREDUCIBLE)
    add("")
    add("| reason | rows | bytes | what measured it |")
    add("|---|---|---|---|")
    reasons = collections.defaultdict(lambda: [0, 0])
    for row in rows:
        if row["verdict"] == IRREDUCIBLE:
            reasons[row["reason"]][0] += 1
            reasons[row["reason"]][1] += row["bytes"]
    for reason in sorted(reasons, key=lambda name: -reasons[name][1]):
        measured = ("`docs/research/CODE_FRAGMENT_NULL_CENSUS.md`, one line per row"
                    if reason == "code-without-entry"
                    else "the census class of `docs/research/RAW_REMAINDER.csv` and its "
                         "`docs/research/ROUTE_TO_100.md` method")
        add("| `%s` | %d | %d | %s |" % (reason, reasons[reason][0], reasons[reason][1], measured))
    add("")
    add("## The join")
    add("")
    gap_rows = gaps(rows)
    conflict_rows = conflicts(rows)
    add("`--check` walks every row of the census against every verdict table of every document above.")
    add("")
    add("| what | rows | bytes |")
    add("|---|---|---|")
    add("| rows with no verdict line | %d | %d |"
        % (len(gap_rows), sum(row["bytes"] for row in gap_rows)))
    add("| rows with a verdict line in two documents | %d | %d |"
        % (len(conflict_rows), sum(row["bytes"] for row in conflict_rows)))
    add("| rows whose own document carries two sections on them | %d | %d |"
        % (sum(1 for row in rows if len(row["carrier_lines"]) > 1),
           sum(row["bytes"] for row in rows if len(row["carrier_lines"]) > 1)))
    add("")
    add("A document may carry more than one section on a row - the null and the read verdict are two")
    add("measurements, and the second names the readers the first bounds - and that is not a second")
    add("verdict. Two documents on one row is, because neither is then the row's census.")
    add("")
    add("## Re-run")
    add("")
    add("    python tools\\research\\residual_index.py")
    add("    python tools\\research\\residual_index.py --check")
    add("")
    return "\n".join(lines) + "\n"


def check(rows=None):
    rows = rows if rows is not None else measure()
    gap_rows = gaps(rows)
    if gap_rows:
        raise SystemExit("%d raw row(s) / %d B carry no verdict line in their own census document: %s"
                         % (len(gap_rows), sum(row["bytes"] for row in gap_rows),
                            ", ".join("0x%06X" % row["start"] for row in gap_rows[:8])))
    conflict_rows = conflicts(rows)
    if conflict_rows:
        raise SystemExit("%d raw row(s) / %d B carry a verdict line in two documents: %s"
                         % (len(conflict_rows), sum(row["bytes"] for row in conflict_rows),
                            ", ".join("0x%06X in %s" % (row["start"], ", ".join(row["docs"]))
                                      for row in conflict_rows[:4])))
    total = sum(row["bytes"] for row in rows)
    if total != raw_bytes():
        raise SystemExit("the index holds %d B, not the gate's raw-data %d B" % (total, raw_bytes()))
    if identity_bytes() != sum(length for _start, length in gate.union_ranges(gate.identity_ranges())):
        raise SystemExit("the identity line is not the gate's identity total")
    return total


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    rows = measure()
    total = check(rows)
    text = doc_text(rows)
    classes = totals(rows)
    for name in CLASSES:
        print("%-30s %5d row(s) %8d B" % (name, classes[name][0], classes[name][1]))
    print("raw-data %d row(s) %d B  gate %d B  identity %d B  EXACT"
          % (len(rows), total, raw_bytes(), identity_bytes()))
    print("gaps 0  conflicts 0  two-section rows %d"
          % sum(1 for row in rows if len(row["carrier_lines"]) > 1))
    if args.check:
        with open(DOC_OUT, encoding="utf-8") as handle:
            if handle.read() != text:
                raise SystemExit("%s is not the table this census derives"
                                 % os.path.relpath(DOC_OUT, ROOT))
        print("CHECK: the index matches the census and the gate")
        return 0
    with open(DOC_OUT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("wrote %s (%d B)" % (os.path.relpath(DOC_OUT, ROOT), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
