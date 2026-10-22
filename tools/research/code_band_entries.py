"""Static entry evidence per row of the residual ledger's `CODE-BAND-004:unreached` set.

The population is every `docs/research/RESIDUAL_LEDGER.csv` row whose `attempts` carries
`CODE-BAND-004:unreached`: 1,174 rows / 35,510 B, R32 1,035 / 32,436 and R00 139 / 3,074, measured
from the CSV. 702 of them / 28,797 B (R32 670 / 27,564, R00 32 / 1,233) are the rows
`docs/research/RAW_REMAINDER.csv` classes `text/tables`; that subset is a COLUMN of this table, not the
denominator (the ticket's 45,882 B and 690 R32 rows match neither file, so the CSVs win).

Six channels, each reported on its own per row - never first-match - and each recording the site that
fired:

  * `source` - a Thumb-state control transfer out of source whose target lands in the row
    (`thumb_bodies.entries`, which prefers a site at the row's own start);
  * `converted` - a branch out of a body this project already converted
    (`thumb_bodies.converted_entries`);
  * `method` - a class-table method slot naming the row (`thumb_bodies.method_entries`), the same
    targets `code_band.method_targets` reports in and outside a region;
  * `pointer` - a word of the `pointer-tables` class naming the row (`pointer_rows`' grid);
  * `pool` - a code pc-relative pool word naming an address in the row (`code_band`'s pool channel);
  * `prologue` - the `0xB5xx` PUSH shape (`thumb_bodies.prologue_entries`), a SHAPE, never an entry.

`entry` is the strongest channel that fired, in the precedence source, converted, method, pointer,
pool, none, and `site` is that channel's site text. The prologue shape stays out of `entry` on
purpose, so a row only the shape names reports `entry=none` with `prologue` true.

`shape` is the split of the rows no channel names, by one stated predicate and its own null: a row is
`code` when the Thumb walk from its own start ends in a return and the SAME walk from the same offset
on the row's byte-permuted copy (fixed seed) does not; else `table-pointer` when its first word is a
value inside the image (a record that starts with an address); else `table`. A row any channel names
is `entry`, and no row is two shapes, so the column closes the population.

    python tools/research/code_band_entries.py            # the summary table
    python tools/research/code_band_entries.py --nulls    # + both byte-permuted nulls
    python tools/research/code_band_entries.py --write    # + docs/research/CODE_BAND_ENTRIES.csv
                                                          #   and ENTRY_ROWS.csv for the converter
"""
from __future__ import annotations

import argparse
import csv
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import code_band  # noqa: E402
import pointer_rows  # noqa: E402
import text_tables  # noqa: E402
import thumb_bodies  # noqa: E402

LEDGER = os.path.join(ROOT, "docs", "research", "RESIDUAL_LEDGER.csv")
REMAINDER = os.path.join(ROOT, "docs", "research", "RAW_REMAINDER.csv")
CSV_OUT = os.path.join(ROOT, "docs", "research", "CODE_BAND_ENTRIES.csv")
CHANNELS = ("source", "converted", "method", "pool", "pointer", "prologue")
ENTRY_ORDER = ("source", "converted", "method", "pointer", "pool")
FIELDS = ("start", "end", "bytes", "region", "text_tables", "source", "converted", "method",
          "pool", "pointer", "prologue", "entry", "site", "shape")
ATTEMPT = "CODE-BAND-004:unreached"
DENOMINATOR = (1173, 35506)
SUBSET = (701, 28793)
SHAPES = ("entry", "code", "table-pointer", "table")
SEED = 20261017
CONVERTER_OUT = os.path.join(ROOT, "docs", "research", "CODE_BAND_ENTRY_ROWS.csv")
POINTER_OUT = os.path.join(ROOT, "docs", "research", "CODE_BAND_POINTER_ROWS.csv")


def population():
    texts = {(int(row["start"], 16), int(row["end"], 16))
             for row in csv.DictReader(open(REMAINDER, newline=""))
             if row["class"] == "text/tables"}
    out = []
    for row in csv.DictReader(open(LEDGER, newline="")):
        if ATTEMPT not in row["attempts"]:
            continue
        span = (int(row["start"], 16), int(row["end"], 16))
        out.append({"start": span[0], "end": span[1], "bytes": int(row["bytes"]),
                    "region": row["region"],
                    "text_tables": "text/tables" if span in texts else ""})
    return out


def first(sites):
    return {row: min(found, key=lambda site: (site[0] != row[0], site[0]))[2]
            for row, found in sites.items()}


def pool_sites():
    wanted = set(code_band.citations())
    out = {}
    for row in csv.DictReader(open(code_band.CITATIONS, newline="")):
        span = (int(row["start"], 16), int(row["end"], 16))
        if row["route"] == "P" and span in wanted:
            out[span] = "code ldr 0x%s pool word" % row["first site"]
    return out


def pointer_sites(spans):
    index = thumb_bodies.Rows(spans)
    out = {}
    for start, end, _carrier, _line in pointer_rows.rows():
        for word in pointer_rows.grid(start, end - start):
            value = struct.unpack_from("<I", thumb_bodies.ROM, word)[0]
            row = index.of((value & ~1) - thumb_bodies.ROM_BASE)
            if row is None or row in out:
                continue
            out[row] = "pointer table word 0x%06X = 0x%08X" % (word, value)
    return out


def channels(population):
    spans = [(row["start"], row["end"]) for row in population]
    return {"source": first(thumb_bodies.entries(spans)),
            "converted": first(thumb_bodies.converted_entries(spans)),
            "method": first(thumb_bodies.method_entries(spans)),
            "pool": pool_sites(),
            "pointer": pointer_sites(spans),
            "prologue": first(thumb_bodies.prologue_entries(spans))}


def label(row, found):
    for name in ENTRY_ORDER:
        if row in found.get(name, {}):
            return name, found[name][row]
    return "none", ""


def permuted_row(row, seed=SEED):
    rom = bytearray(thumb_bodies.ROM)
    blob = bytearray(rom[row[0]:row[1]])
    random.Random(seed + row[0]).shuffle(blob)
    rom[row[0]:row[1]] = blob
    return bytes(rom)


def returns_at(row):
    return bool(thumb_bodies.returns(thumb_bodies.walk(row, [(row[0], "shape", "shape", "shape")])))


def first_word_inside(row):
    if row[1] - row[0] < 4:
        return False
    word = struct.unpack_from("<I", thumb_bodies.ROM, row[0])[0]
    return bool(word & ~1 and thumb_bodies.ROM_BASE <= (word & ~1)
                < thumb_bodies.ROM_BASE + len(thumb_bodies.ROM))


def shapes(population, found):
    out = {}
    original = thumb_bodies.ROM
    for row in population:
        span = (row["start"], row["end"])
        if label(span, found)[0] != "none":
            out[span] = ("entry", False, False)
            continue
        real = returns_at(span)
        thumb_bodies.ROM = permuted_row(span)
        try:
            null = returns_at(span)
        finally:
            thumb_bodies.ROM = original
        if real and not null:
            out[span] = ("code", real, null)
        elif first_word_inside(span):
            out[span] = ("table-pointer", real, null)
        else:
            out[span] = ("table", real, null)
    return out


def source_null(spans):
    rom = bytearray(thumb_bodies.ROM)
    for start, end, mode, _insn in thumb_bodies.source_rows():
        if mode != "thumb":
            continue
        blob = bytearray(rom[start:end])
        random.Random(SEED + start).shuffle(blob)
        rom[start:end] = blob
    original = thumb_bodies.ROM
    thumb_bodies.ROM = bytes(rom)
    try:
        found = thumb_bodies.entries(spans)
    finally:
        thumb_bodies.ROM = original
    return len(found), sum(end - start for start, end in found)


def pointer_null(spans):
    rom = bytearray(thumb_bodies.ROM)
    words = 0
    for start, end, _carrier, _line in pointer_rows.rows():
        blob = bytearray(rom[start:end])
        random.Random(SEED + start).shuffle(blob)
        rom[start:end] = blob
        words += len(list(pointer_rows.grid(start, end - start)))
    original = thumb_bodies.ROM
    thumb_bodies.ROM = bytes(rom)
    try:
        found = pointer_sites(spans)
    finally:
        thumb_bodies.ROM = original
    return len(found), sum(end - start for start, end in found), words


def census(population, found):
    out = []
    for row in population:
        span = (row["start"], row["end"])
        entry, site = label(span, found)
        out.append(dict(row, entry=entry, site=site, shape="",
                        **{name: span in found.get(name, {}) for name in CHANNELS}))
    return out


def cell(entry, field):
    if field in CHANNELS:
        return "yes" if entry[field] else "no"
    if field in ("start", "end"):
        return "0x%06x" % entry[field]
    if field == "site":
        return " ".join(str(entry["site"]).split()).replace(",", ";")
    return str(entry[field])


def csv_text(table):
    return "\n".join([",".join(FIELDS)]
                     + [",".join(cell(entry, field) for field in FIELDS) for entry in table]) + "\n"


def rows_text(table, entry_name):
    picked = [entry for entry in table if entry["entry"] == entry_name]
    return "\n".join(["start,end"] + ["0x%06x,0x%06x" % (entry["start"], entry["end"])
                                      for entry in picked]) + "\n"


def summary(table, name):
    total = sum(entry["bytes"] for entry in table)
    lines = ["%s: %d row(s) %d B" % (name, len(table), total),
             "| channel | rows | bytes |", "|---|---|---|"]
    for channel in CHANNELS:
        hits = [entry for entry in table if entry[channel]]
        lines.append("| `%s` | %d | %d |" % (channel, len(hits),
                                             sum(entry["bytes"] for entry in hits)))
    none = [entry for entry in table if entry["entry"] == "none"]
    lines.append("| **`entry=none`** | **%d** | **%d** |" % (len(none),
                                                             sum(e["bytes"] for e in none)))
    labels = {}
    for entry in table:
        labels[entry["entry"]] = labels.get(entry["entry"], 0) + 1
    lines.append("`entry` labels %d row(s) %d B once each: %s"
                 % (len(table), total,
                    ", ".join("%s %d" % (key, labels[key]) for key in sorted(labels))))
    shapes_found = {}
    for entry in table:
        shapes_found[entry["shape"]] = shapes_found.get(entry["shape"], [0, 0])
        shapes_found[entry["shape"]][0] += 1
        shapes_found[entry["shape"]][1] += entry["bytes"]
    lines.append("| shape | rows | bytes |")
    lines.append("|---|---|---|")
    for name_ in SHAPES:
        found = shapes_found.get(name_, [0, 0])
        lines.append("| `%s` | %d | %d |" % (name_, found[0], found[1]))
    return lines


def measure():
    rows = population()
    if text_tables.anchor_failures(thumb_bodies.ROM):
        raise SystemExit("text_tables.anchor_failures: the method channel's table does not resolve, "
                         "so a zero method count would be a dead instrument")
    measured = (len(rows), sum(row["bytes"] for row in rows))
    if measured != DENOMINATOR:
        raise SystemExit("the population is %d row(s) / %d B, not %d / %d: the census moved"
                         % (measured + DENOMINATOR))
    if len({(row["start"], row["end"]) for row in rows}) != len(rows):
        raise SystemExit("the ledger carries the same span twice")
    found = channels(rows)
    table = census(rows, found)
    split = shapes(rows, found)
    for entry in table:
        entry["shape"] = split[(entry["start"], entry["end"])][0]
    subset = [entry for entry in table if entry["text_tables"]]
    if (len(subset), sum(entry["bytes"] for entry in subset)) != SUBSET:
        raise SystemExit("the text/tables subset is %d row(s) / %d B, not %d / %d"
                         % (len(subset), sum(entry["bytes"] for entry in subset)) + SUBSET)
    if [entry["entry"] != "none" for entry in table] != [entry["shape"] == "entry" for entry in table]:
        raise SystemExit("the shape column and the entry column disagree on which rows have an entry")
    return table, rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--nulls", action="store_true")
    args = parser.parse_args(argv)
    table, rows = measure()
    for line in summary(table, "population"):
        print(line)
    for line in summary([entry for entry in table if entry["text_tables"]],
                        "text/tables subset"):
        print(line)
    if args.nulls:
        spans = [(entry["start"], entry["end"]) for entry in table
                 if entry["entry"] in ENTRY_ORDER[:3]]
        real = sum(1 for span in spans if returns_at(span))
        null = 0
        original = thumb_bodies.ROM
        for span in spans:
            thumb_bodies.ROM = permuted_row(span)
            try:
                null += returns_at(span)
            finally:
                thumb_bodies.ROM = original
        print("entry set null (walk ends in a return, real vs the same row permuted): %d of %d, %d"
              % (real, len(spans), null))
        print("source-scan null on the whole population: %d row(s) %d B"
              % source_null([(row["start"], row["end"]) for row in rows]))
        named = [entry for entry in table if entry["pointer"]]
        null_rows, null_bytes, words = pointer_null([(row["start"], row["end"]) for row in rows])
        print("pointer channel: %d row(s) %d B; permuted tables %d row(s) %d B of %d word(s), "
              "chance expectation %.1f"
              % (len(named), sum(entry["bytes"] for entry in named), null_rows, null_bytes, words,
                 words * sum(row["bytes"] for row in rows) / float(1 << 24)))
    if args.write:
        with open(CSV_OUT, "w", encoding="ascii", newline="\n") as handle:
            handle.write(csv_text(table))
        print("wrote %s: %d row(s)" % (os.path.relpath(CSV_OUT, ROOT), len(table)))
        entry_rows = [entry for entry in table if entry["entry"] in ENTRY_ORDER[:3]]
        with open(CONVERTER_OUT, "w", encoding="ascii", newline="\n") as handle:
            handle.write("start,end\n")
            for entry in entry_rows:
                handle.write("0x%06x,0x%06x\n" % (entry["start"], entry["end"]))
        print("wrote %s: %d row(s)" % (os.path.relpath(CONVERTER_OUT, ROOT), len(entry_rows)))
        text = rows_text(table, "pointer")
        with open(POINTER_OUT, "w", encoding="ascii", newline="\n") as handle:
            handle.write(text)
        print("wrote %s: %d row(s)" % (os.path.relpath(POINTER_OUT, ROOT), text.count("\n") - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
