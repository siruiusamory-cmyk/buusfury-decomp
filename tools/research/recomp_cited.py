"""Turn a static recompilation's ROM-read log into citations of the runtime target rows.

The recomp reads the same image the emulator does, so one headless run can
carry every read the mGBA launcher needs 194 watchpoint runs for. Its logger writes one line per
ROM read that falls inside a watched range, and this tool applies RUNTIME_READ_PLAN P2 unchanged:

  * the read address lies inside a `docs/research/RUNTIME_TARGETS.csv` row (that row is cited);
  * the reader `pc` lies inside a transcribed row of `work/ledger.csv` (`isa == t`) that is not
    the cited row itself - a hit whose reader is its own row cites nothing, and neither does a hit
    whose reader sits in a raw or unconverted row.

Every (row, reader pc) pair is one citation, carrying the width the read was made at and the
frame it happened on. No ROM byte and no value read is written into the tracked CSV: the columns
are addresses, widths and frames, as `docs/research/RUNTIME_CITED.csv` records them.

    python tools/research/recomp_cited.py --hits build/recomp_read/hits.csv
    python tools/research/recomp_cited.py --hits build/recomp_read/hits.csv --write
    python tools/research/recomp_cited.py --ranges-out build/recomp_read/ranges.txt
"""
from __future__ import annotations

import argparse
import bisect
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TARGETS = os.path.join(ROOT, "docs", "research", "RUNTIME_TARGETS.csv")
LEDGER = os.path.join(ROOT, "work", "ledger.csv")
CSV_OUT = os.path.join(ROOT, "docs", "research", "RECOMP_CITED.csv")
ROM_BASE = 0x08000000
FIELDS = ("group", "start", "end", "address", "pc", "reader_start", "reader_end", "width", "frame")


def read_targets(path=TARGETS, leads=None):
    out = []
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            out.append({"group": row["group"], "start": int(row["start"], 16),
                        "end": int(row["end"], 16)})
    for line in leads or []:
        start, end = (int(text, 16) for text in line.split()[:2])
        out.append({"group": "recomp_lead", "start": start, "end": end})
    return sorted(out, key=lambda row: (row["start"], row["end"]))


def read_ledger(path=LEDGER):
    out = []
    with open(path, newline="") as handle:
        for row in csv.reader(handle):
            offset, length, isa = int(row[0], 16), int(row[1]), row[2]
            out.append((offset, offset + length, isa))
    return sorted(out)


def read_hits(path):
    def number(text):
        return int(text, 16) if text.lower().startswith("0x") else int(text)

    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            yield {"pc": number(row["pc"]), "lr": number(row["lr"]),
                   "addr": number(row["addr"]), "width": number(row["width"]),
                   "frame": number(row["frame"])}


def offset_of(address):
    if ROM_BASE <= address < ROM_BASE + 0x02000000:
        return address - ROM_BASE
    return None


def indexed(rows):
    rows = sorted(rows)
    return rows, [row[0] for row in rows]


def holder(index, offset):
    rows, starts = index
    at = bisect.bisect_right(starts, offset) - 1
    if at >= 0 and rows[at][0] <= offset < rows[at][1]:
        return rows[at]
    return None


def citations(hits, targets, ledger):
    target_index = indexed([(t["start"], t["end"], t["group"]) for t in targets])
    reader_index = indexed(ledger)
    seen = {}
    for hit in hits:
        offset = offset_of(hit["addr"])
        if offset is None:
            continue
        row = holder(target_index, offset)
        if row is None:
            continue
        pc = offset_of(hit["pc"])
        reader = holder(reader_index, pc) if pc is not None else None
        if reader is None or reader[2] != "t" or (reader[0], reader[1]) == (row[0], row[1]):
            continue
        key = (row[0], hit["pc"])
        if key not in seen or hit["frame"] < seen[key]["frame"]:
            seen[key] = {"group": row[2], "start": row[0], "end": row[1],
                         "address": hit["addr"], "pc": hit["pc"],
                         "reader_start": reader[0], "reader_end": reader[1],
                         "width": hit["width"], "frame": hit["frame"]}
    return sorted(seen.values(), key=lambda row: (row["start"], row["pc"]))


def summary(rows, targets):
    groups = sorted({target["group"] for target in targets})
    lines = ["| group | target rows | target bytes | rows cited | citations | distinct readers |",
             "|---|---|---|---|---|---|"]
    for group in groups:
        mine = [target for target in targets if target["group"] == group]
        cited = {row["start"] for row in rows if row["group"] == group}
        readers = {row["pc"] for row in rows if row["group"] == group}
        lines.append("| `%s` | %d | %d | %d | %d | %d |"
                     % (group, len(mine), sum(t["end"] - t["start"] for t in mine),
                        len(cited), len([r for r in rows if r["group"] == group]), len(readers)))
    lines.append("| **total** | **%d** | **%d** | **%d** | **%d** | **%d** |"
                 % (len(targets), sum(t["end"] - t["start"] for t in targets),
                    len({row["start"] for row in rows}), len(rows),
                    len({row["pc"] for row in rows})))
    return lines


def csv_text(rows):
    lines = [",".join(FIELDS)]
    for row in rows:
        lines.append(",".join(("0x%06x" % row[field]) if field in
                              ("start", "end", "reader_start", "reader_end")
                              else ("0x%08x" % row[field]) if field in ("address", "pc")
                              else str(row[field]) for field in FIELDS))
    return "\n".join(lines) + "\n"


def read_citations_csv(path=CSV_OUT):
    def number(text):
        return int(text, 16)

    with open(path, newline="") as handle:
        return [{field: (number(row[field]) if field != "group" else row[field])
                 for field in FIELDS} for row in csv.DictReader(handle)]


def citation_files(rows, directory):
    os.makedirs(directory, exist_ok=True)
    paths = {}
    for row in rows:
        path = os.path.join(directory, "%x.txt" % row["start"])
        if path not in paths:
            paths[path] = []
        paths[path].append("%x pc 0x%08x read 0x%08x (width %d, frame %d)"
                           % (row["address"] - ROM_BASE, row["pc"], row["address"],
                              row["width"], row["frame"]))
    for path, lines in paths.items():
        with open(path, "w", encoding="ascii", newline="\n") as handle:
            handle.write("\n".join(lines) + "\n")
    return sorted(paths)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--hits", nargs="+",
                        help="the recomp logger's CSV(s) (pc,lr,addr,width,frame,value)")
    parser.add_argument("--targets", default=TARGETS)
    parser.add_argument("--ledger", default=LEDGER)
    parser.add_argument("--leads", help="text file, `start end` hex per line, watched as recomp_lead")
    parser.add_argument("--exclude-cited", nargs="?", const=CSV_OUT,
                        help="drop every target row whose start the tracked citation CSV names")
    parser.add_argument("--write", action="store_true", help="write docs/research/RECOMP_CITED.csv")
    parser.add_argument("--citations-dir", help="one rawlabeled.py --citations list per cited row")
    parser.add_argument("--ranges-out", help="write `start end` hex per line for the logger")
    args = parser.parse_args(argv)
    leads = open(args.leads).read().splitlines() if args.leads else None
    targets = read_targets(args.targets, leads)
    if args.exclude_cited:
        cited = {row["start"] for row in read_citations_csv(args.exclude_cited)}
        targets = [target for target in targets if target["start"] not in cited]
        print("excluded %d cited row start(s)" % len(cited))
    if args.ranges_out:
        with open(args.ranges_out, "w", encoding="ascii", newline="\n") as handle:
            for target in targets:
                handle.write("%x %x\n" % (target["start"], target["end"]))
        print("wrote %s: %d range(s), %d byte(s)"
              % (args.ranges_out, len(targets),
                 sum(target["end"] - target["start"] for target in targets)))
    if not args.hits:
        if args.citations_dir:
            print("wrote %d citation list(s) in %s"
                  % (len(citation_files(read_citations_csv(), args.citations_dir)),
                     args.citations_dir))
        return 0
    rows = citations((hit for path in args.hits for hit in read_hits(path)),
                     targets, read_ledger(args.ledger))
    for line in summary(rows, targets):
        print(line)
    if args.citations_dir:
        print("wrote %d citation list(s) in %s"
              % (len(citation_files(rows, args.citations_dir)), args.citations_dir))
    if args.write:
        with open(CSV_OUT, "w", encoding="ascii", newline="\n") as handle:
            handle.write(csv_text(rows))
        print("wrote %s: %d citation(s)" % (os.path.relpath(CSV_OUT, ROOT), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
