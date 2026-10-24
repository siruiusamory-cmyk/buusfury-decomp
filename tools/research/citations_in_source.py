from __future__ import annotations

import argparse
import bisect
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in ("tools/gate", "tools", "tools/research"):
    sys.path.insert(0, os.path.join(ROOT, *_path.split("/")))

import code_xref  # noqa: E402
import emitted  # noqa: E402
import gate  # noqa: E402

ROM = os.path.join(ROOT, "baserom.gba")
CSV_OUT = os.path.join(ROOT, "build", "raw_citations.csv")
ROM_BASE = 0x08000000
CLASSES = ("cited", "runtime-cited", "unreferenced")

FIELD = re.compile(r"cited by entry at file 0x([0-9A-Fa-f]+), field \+0x([0-9A-Fa-f]+);\s*"
                   r"0x([0-9A-Fa-f]{8})\s+([^|]*)")
RUNTIME = re.compile(r"cited by runtime read")


def read_rom():
    with open(ROM, "rb") as handle:
        return handle.read()


def half_open(start, end, sites):
    return [site for site in sites if start <= site < end]


def spans_index(pairs):
    out = sorted(pairs)
    return [low for low, _high in out], out


def code_index(ledger_rows):
    return spans_index([(row[0], row[0] + row[1]) for row in ledger_rows
                        if row[2] in ("thumb", "arm")])


def generated_index(ledger_rows):
    return spans_index([(row[0], row[0] + row[1]) for row in ledger_rows if row[5] == "generated"])


def row_index(rows):
    return spans_index([(start, start + length) for start, length, _s, _n, _o in rows])


def index_hit(index, offset):
    starts, spans = index
    position = bisect.bisect_right(starts, offset) - 1
    if position >= 0 and spans[position][0] <= offset < spans[position][1]:
        return spans[position]
    return None


def site_class(code, generated, rows, offset):
    if index_hit(code, offset) is not None:
        return "code"
    if index_hit(generated, offset) is not None:
        return "generated"
    if index_hit(rows, offset) is not None:
        return "row"
    return "unledgered"


def comment_forms(text):
    out = {"runtime": False, "recorded": False, "field_site": None}
    for _line, text in text:
        field = FIELD.search(text)
        if field:
            out["recorded"] = True
            out["field_site"] = int(field.group(3), 16) - ROM_BASE
            continue
        if RUNTIME.search(text):
            out["runtime"] = True
    return out


def code_verdict(route_sites, runtime, classify):
    counted = {}
    for route in ("P", "A"):
        sites = sorted(set(offset for offset in route_sites.get(route, ())
                            if classify(offset) == "code"))
        if sites:
            counted[route] = sites
    routes = [route for route in ("P", "A") if route in counted]
    if counted:
        return "cited", routes, min(site for sites in counted.values() for site in sites), "code"
    if runtime:
        return "runtime-cited", [], None, None
    return "unreferenced", [], None, None


def tally(verdicts, sizes):
    out = {name: 0 for name in CLASSES}
    for got, size in zip(verdicts, sizes):
        out[got] += size
    return out


def check_totals(classes, raw, cited):
    total = sum(classes[name] for name in CLASSES)
    if total != raw:
        raise SystemExit("the classes sum to %d, not the raw total %d" % (total, raw))
    if raw != cited:
        raise SystemExit("the row total %d is not gate.incbin_ranges()' %d" % (raw, cited))
    return total


def measure():
    rom = read_rom()
    slices = gate.incbin_ranges()
    census = incbin_census_rows()
    by_start = {row[0]: index for index, row in enumerate(census)}
    ledger = gate.ledger_rows()
    code = code_index(ledger)
    generated = generated_index(ledger)
    rows = row_index(census)
    carriers = emitted.carrier_comments(ROOT)

    cited_bytes = sum(length for _start, length in slices)
    sites = code_xref.scan(rom)
    pool = {}
    for _kind, site, _target, value in code_xref.loads_into(rom, sites, ROM_BASE, ROM_BASE + len(rom)):
        row = index_hit(rows, value - ROM_BASE)
        if row is None:
            continue
        pool.setdefault(by_start.get(row[0]), []).append(site - ROM_BASE)
    address = {}
    for kind in ("thumb", "arm"):
        for site, target in sites[kind]:
            row = index_hit(rows, target - ROM_BASE)
            if row is None:
                continue
            address.setdefault(by_start.get(row[0]), []).append(site - ROM_BASE)

    out = []
    verdicts = []
    recorded = {"rows": 0, "bytes": 0, "classes": {}}
    for index, (start, length, _status, _name, _note) in enumerate(census):
        forms = comment_forms(carriers.get((start, start + length), []))
        got, routes, first, klass = code_verdict(
            {"P": pool.get(index, []), "A": address.get(index, [])}, forms["runtime"],
            lambda offset: site_class(code, generated, rows, offset))
        if forms["recorded"]:
            recorded["rows"] += 1
            recorded["bytes"] += length
            recorded["classes"][got] = recorded["classes"].get(got, 0) + length
        verdicts.append(got)
        out.append((start, length, got, routes, first, klass))
    classes = tally(verdicts, [row[1] for row in out])
    raw = sum(row[1] for row in out)
    check_totals(classes, raw, cited_bytes)
    if len(out) != len(slices):
        raise SystemExit("row count %d is not the slice count %d" % (len(out), len(slices)))
    for start, length in slices:
        if start not in by_start:
            raise SystemExit("the slice 0x%06X carries no census row" % start)
    return out, classes, recorded


def incbin_census_rows():
    import incbin_census
    return incbin_census.rows_for(gate.incbin_ranges(), incbin_census.REGIONS)


def totals_text(classes):
    return "\n".join("%s=%d" % (name.replace("-", "_"), classes[name]) for name in CLASSES)


def csv_text(rows):
    fields = ("row", "start", "end", "bytes", "class", "route", "first site", "site class")
    lines = [",".join(fields)]
    for index, (start, length, got, routes, first, klass) in enumerate(rows):
        lines.append(",".join((
            str(index), "0x%06X" % start, "0x%06X" % (start + length), str(length), got,
            "+".join(routes) or "-",
            "-" if first is None else "0x%08X" % (ROM_BASE + first), klass or "-")))
    return "\n".join(lines) + "\n"


def check_against(path, rows):
    mine = {row[0]: row[2] for row in rows}
    mismatched = 0
    seen = 0
    with open(path, newline="") as handle:
        for listed in csv.DictReader(handle):
            start = int(listed["start"], 16)
            if start not in mine:
                raise SystemExit("the sweep's row 0x%06X is not one of mine" % start)
            seen += 1
            want = "cited" if listed["consumer_verdict"] == "cited" else "unreferenced"
            got = "cited" if mine[start] == "cited" else "unreferenced"
            if got != want:
                mismatched += 1
    if seen != len(mine):
        raise SystemExit("the sweep carries %d rows, this run measured %d" % (seen, len(mine)))
    return mismatched, seen


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--print", dest="print_only", action="store_true")
    parser.add_argument("--check", default="")
    args = parser.parse_args(argv)
    rows, classes, recorded = measure()
    print(totals_text(classes))
    print("rows=%d raw-data=%d" % (len(rows), sum(row[1] for row in rows)))
    print("recorded-citation-only %d rows %d B (a data-stated MapEntry +0x30 field names the row; "
          "excluded from the code-site channels by contract item 5 / P-453)%s"
          % (recorded["rows"], recorded["bytes"],
             "".join(" [%s %d B]" % (name, size) for name, size in
                     sorted(recorded["classes"].items()))))
    if args.check:
        mismatched, seen = check_against(args.check, rows)
        print("disagreements %d of %d" % (mismatched, seen))
        return 1 if mismatched else 0
    if args.print_only:
        print("print only: nothing written")
        return 0
    text = csv_text(rows)
    os.makedirs(os.path.dirname(CSV_OUT), exist_ok=True)
    with open(CSV_OUT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("wrote %s (%d B)" % (os.path.relpath(CSV_OUT, ROOT), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
