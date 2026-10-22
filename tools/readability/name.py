from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "lint"))

import lints

LEDGER = os.path.join("docs", "NAMING_LEDGER.csv")
INDEX = os.path.join("docs", "ASM_INDEX.csv")
NAMES = os.path.join("docs", "research", "RECOMP_NAMES.csv")
PAGE = os.path.join("docs", "research", "NAME_CENSUS.md")
BASELINE = os.path.join("docs", "NAMING_BASELINE.txt")
README = "README.md"
CENSUS = os.path.join("docs", "research", "FUNCTION_BOUNDS.csv")
KINDS = ("start", "unreferenced")
FOLDERS = ("asm/", "src/", "include/", "docs/")
HOUSE = re.compile(r"^(?:sub|loc|dat|unk|g)_[0-9A-Fa-f]{8}$")
README_FUNCTIONS = re.compile(r"([\d,]+) of the ([\d,]+) functions")


def tracked():
    proc = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True)
    return [name for name in proc.stdout.decode("utf-8", "replace").split("\n") if name]


def read(name):
    with open(os.path.join(ROOT, *name.split("/")), "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write(name, text):
    with open(os.path.join(ROOT, *name.split("/")), "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def census():
    with open(os.path.join(ROOT, *CENSUS.split("/")), newline="", encoding="utf-8") as handle:
        return {int(row["address"], 16): row["kind"] for row in csv.DictReader(handle)}


def index_rows():
    return list(csv.DictReader(io.StringIO(read(INDEX))))


def house_name(address, rows=None):
    for row in rows if rows is not None else index_rows():
        if int(row["address"], 16) == address and row.get("symbol"):
            return row["symbol"]
    return None


def token(name):
    return re.compile(r"\b%s\b" % re.escape(name), re.I)


def rename_text(text, old, new):
    return token(old).sub(new, text)


def row_text(cells):
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="").writerow(cells)
    return buffer.getvalue()


def ledger_insert(path, address, line):
    body = read(path).splitlines()
    at = len(body)
    for number in range(1, len(body)):
        if int(body[number].split(",", 1)[0], 16) > address:
            at = number
            break
    body[at:at] = [line]
    write(path, "\n".join(body) + "\n")


def counts():
    symbols = lints.export_symbols()
    addresses = lints.label_addresses()
    starts, _blocks = lints.census_kinds()
    live, total = lints.naming_counts(starts, addresses, symbols[0])
    retired = len(lints.retired_rows())
    return live, total, retired


def sync_counts():
    live, total, retired = counts()
    write(BASELINE, "%d\n" % (live - retired))
    text = read(README)
    found = README_FUNCTIONS.search(text)
    if found is None:
        raise SystemExit("%s carries no function figure" % README)
    text = text[:found.start()] + "{:,} of the {:,} functions".format(live, total) + \
        text[found.end():]
    write(README, text)
    rows = sorted(csv.DictReader(io.StringIO(read(LEDGER))),
                  key=lambda row: int(row["address"], 16))
    page = ["# Named functions", "",
            "Every name the ledger promotes, with the address the label sits at.", "",
            "| address | name | class |", "| --- | --- | --- |"]
    page += ["| %s | %s | %s |" % (row["address"].lower(), row["new"], row["evidence_class"])
             for row in rows]
    write(PAGE, "\n".join(page) + "\n")
    return live, total, retired


def symbols():
    found = {row["symbol"] for row in index_rows() if row.get("symbol")}
    found.update(row["new"] for row in csv.DictReader(io.StringIO(read(LEDGER)))
                 if row.get("new"))
    return found


def one(row, kinds):
    address = int(row["address"], 16)
    new = row["new"]
    if kinds.get(address) not in KINDS:
        raise SystemExit("0x%08X is not a census start the naming rules cover" % address)
    if not lints.FUNCTION_NAME.match(new):
        raise SystemExit("%s is not a Module_Verb name" % new)
    old = house_name(address)
    if old is None or not HOUSE.match(old):
        raise SystemExit("0x%08X carries no house label" % address)
    if new in symbols():
        raise SystemExit("%s is already a symbol" % new)
    doc = row.get("doc") or PAGE
    if not os.path.exists(os.path.join(ROOT, *doc.split("/"))):
        raise SystemExit("%s is not in the tree" % doc)
    return {"address": address, "old": old, "new": new, "class": row["class"],
            "evidence": row["evidence"], "doc": doc}


def apply(entries):
    changed = []
    names = tracked()
    for name in names:
        if not name.startswith(FOLDERS):
            continue
        text = read(name)
        replaced = text
        for entry in entries:
            replaced = rename_text(replaced, entry["old"], entry["new"])
        if replaced == text:
            continue
        write(name, replaced)
        changed.append(name)
    for entry in entries:
        source = os.path.join(ROOT, "asm", entry["old"] + ".s")
        if not os.path.exists(source):
            continue
        target = os.path.join(ROOT, "asm", entry["new"] + ".s")
        if os.path.exists(target):
            raise SystemExit("%s already exists" % target)
        os.rename(source, target)
        changed.append("asm/%s.s -> asm/%s.s" % (entry["old"], entry["new"]))
    for entry in entries:
        ledger_insert(LEDGER, entry["address"], row_text([
            "0x%08X" % entry["address"], entry["old"], entry["new"], entry["class"],
            entry["evidence"]]))
    lines = read(NAMES).splitlines()
    for entry in entries:
        lines.append("0x%08x,%s,%s" % (entry["address"], entry["new"], entry["doc"]))
    head, tail = lines[:1], sorted(lines[1:], key=lambda line: int(line.split(",", 1)[0], 16))
    write(NAMES, "\n".join(head + tail) + "\n")
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(description="promote house labels to names the ledger carries")
    parser.add_argument("--rows")
    parser.add_argument("--sync", action="store_true",
                        help="rewrite the ratchet and README figures from the tracked tree")
    args = parser.parse_args(argv)
    report = []
    if args.rows:
        rows = json.loads(open(args.rows, encoding="utf-8").read())
        kinds = census()
        entries = [one(row, kinds)
                   for row in sorted(rows, key=lambda item: int(item["address"], 16))]
        report = apply(entries)
    live, total, retired = sync_counts()
    print("live=%d total=%d retired=%d" % (live, total, retired))
    for name in report:
        print("  %s" % name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
