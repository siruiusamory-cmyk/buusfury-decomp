"""UNATTEMPTED-001: measure the 139 ledger rows no ticket has ever tried, and classify them.

The population is every `docs/research/RESIDUAL_LEDGER.csv` row whose `status` is `unmapped` and
whose `attempts` is `none`: 139 rows / 58,359 B at the ticket's base, pinned here and refused when
the census moves. For each row this tool records, in one CSV:

  * its region id and the region's own description (`incbin_census.REGIONS`, T-197's table);
  * its neighbours: the nearest ledger row on either side that is NOT in the population, with that
    row's status and attempts, and whether it touches this one;
  * every reference into it: the ledger's code site, and a 4-byte word of the whole image whose
    value names the row (the site side, with the word count and the chance expectation printed);
  * every existing instrument's verdict: a PACKED container at the row start, a row-bounded JCALG1
    probe, a Thumb entry (source, converted-branch, method, pointer, PUSH prologue), an ARM branch
    out of a converted ARM body, the walk-from-start shape, the strict pointer-table predicate, the
    text/table class of `text_tables.classify`, the fixed record stride, and graphics-block
    membership.

`--nulls` re-runs each firing family against a byte-permuted null on the SIDE THE RULE READS
(P-613): the row itself for a row-shape rule, the site words for a reference rule, every Thumb
source span for the entry rule. A family that fails its null is not converted and is reported with
its numbers.

    python tools/research/unattempted.py                 # the tables
    python tools/research/unattempted.py --nulls         # + every family's null
    python tools/research/unattempted.py --write         # + docs/research/UNATTEMPTED_ROWS.csv
    python tools/research/unattempted.py --check         # the ledger carries no `none` for it
"""
from __future__ import annotations

import argparse
import bisect
import csv
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "webfoot")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import arm_bodies  # noqa: E402
import code_band_entries  # noqa: E402
import incbin_census  # noqa: E402
import jcalg1  # noqa: E402
import raw_remainder  # noqa: E402
import text_tables  # noqa: E402
import thumb_bodies  # noqa: E402

ROM_PATH = os.path.join(ROOT, "baserom.gba")
LEDGER = os.path.join(ROOT, "docs", "research", "RESIDUAL_LEDGER.csv")
CSV_OUT = os.path.join(ROOT, "docs", "research", "UNATTEMPTED_ROWS.csv")
ROM_BASE = thumb_bodies.ROM_BASE
SEED = 20261017
POPULATION = (139, 58359)
REGION_TOTALS = {"R35": (26, 15141), "R09": (22, 7660), "R10": (16, 7612), "R22": (3, 6040),
                 "R07": (2, 5376), "R34": (5, 4616), "R02": (1, 3960), "R18": (8, 3596),
                 "R33": (35, 3456), "R00": (15, 750), "R32": (6, 152)}
STRIDES = (4, 8, 12, 16, 20, 24, 28, 32, 40, 52, 56, 60, 64, 104)
FIELDS = ("start", "end", "bytes", "region", "region_name",
          "prev_start", "prev_bytes", "prev_status", "prev_attempts", "prev_adjacent",
          "next_start", "next_bytes", "next_status", "next_attempts", "next_adjacent",
          "code_site", "words", "word_site", "container", "jcalg1", "thumb_entry", "converted",
          "method", "pointer", "prologue", "arm_branch", "walk_returns", "ptrtable",
          "stride", "text_class", "block", "result")
FLAGS = ("container", "jcalg1", "thumb_entry", "converted", "method", "pointer", "prologue",
         "arm_branch", "walk_returns", "ptrtable")


def read_rom(path=ROM_PATH):
    with open(path, "rb") as handle:
        return handle.read()


def population(path=LEDGER):
    out = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["status"] == "unmapped" and row["attempts"] == "none":
                out.append({"start": int(row["start"], 16), "end": int(row["end"], 16),
                            "bytes": int(row["bytes"]), "region": row["region"],
                            "references": row["references"]})
    out.sort(key=lambda row: row["start"])
    fresh = bool(out)
    if not out and os.path.exists(CSV_OUT):
        out = measured(CSV_OUT)
    assert_population(out)
    return out, fresh


def assert_population(rows, expected=POPULATION, region_totals=REGION_TOTALS):
    measured = (len(rows), sum(row["bytes"] for row in rows))
    if measured != expected:
        raise SystemExit("the population is %d row(s) / %d B, not %d / %d: the census moved"
                         % (measured + expected))
    got = {}
    for row in rows:
        count, size = got.get(row["region"], (0, 0))
        got[row["region"]] = (count + 1, size + row["bytes"])
    if got != region_totals:
        raise SystemExit("the region split is %r, not %r: the census moved"
                         % (dict(sorted(got.items())), dict(sorted(region_totals.items()))))
    if len({(row["start"], row["end"]) for row in rows}) != len(rows):
        raise SystemExit("the population carries the same span twice")


def region_names():
    out = {"R00": "no measured region"}
    for index, region in enumerate(incbin_census.REGIONS, 1):
        out["R%02d" % index] = region.name
    return out


def ledger_rows(path=LEDGER):
    out = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            out.append({"start": int(row["start"], 16), "end": int(row["end"], 16),
                        "bytes": int(row["bytes"]), "region": row["region"],
                        "status": row["status"], "attempts": row["attempts"]})
    out.sort(key=lambda row: row["start"])
    return out


def neighbours(ledger, rows):
    inside = {(row["start"], row["end"]) for row in rows}
    outside = [row for row in ledger if (row["start"], row["end"]) not in inside]
    starts = [row["start"] for row in outside]
    out = {}
    for row in rows:
        where = bisect.bisect_left(starts, row["start"])
        sides = []
        for entry in (outside[where - 1] if where else None,
                      outside[where] if where < len(outside) else None):
            if entry is None:
                sides.append(None)
                continue
            flag = entry["end"] == row["start"] if entry["start"] < row["start"] \
                else entry["start"] == row["end"]
            sides.append({"start": entry["start"], "bytes": entry["bytes"],
                          "status": entry["status"], "attempts": entry["attempts"],
                          "adjacent": flag})
        out[(row["start"], row["end"])] = tuple(sides)
    return out


def word_index(rom, spans, stride=4):
    owner = {}
    for span in spans:
        for offset in range(span[0], span[1]):
            owner[offset] = span
    hits = {}
    words = 0
    addresses = 0
    for at in range(0, len(rom) - 3, stride):
        words += 1
        value = struct.unpack_from("<I", rom, at)[0]
        if ROM_BASE <= value < ROM_BASE + len(rom):
            addresses += 1
        span = owner.get((value & ~1) - ROM_BASE)
        if span is None or span[0] <= at < span[1]:
            continue
        hits.setdefault(span, []).append((at, value))
    return hits, words, addresses


def walk_returns(rom, span):
    saved = thumb_bodies.ROM
    thumb_bodies.ROM = rom
    try:
        body = thumb_bodies.walk((span[0], span[1]),
                                [(span[0], "shape", "shape", "shape")])
        return bool(thumb_bodies.returns(body))
    finally:
        thumb_bodies.ROM = saved


def permuted(rom, span, seed=SEED):
    blob = bytearray(rom[span[0]:span[1]])
    random.Random(seed + span[0]).shuffle(blob)
    return rom[:span[0]] + bytes(blob) + rom[span[1]:]


def pointer_table(rom, span):
    words, good = raw_remainder.pointer_words(rom, span[0], span[1] - span[0])
    return words >= 2 and good == words


def stride_of(rom, span):
    length = span[1] - span[0]
    for stride in STRIDES:
        if length % stride or length // stride < 2:
            continue
        leaders = [struct.unpack_from("<I", rom, span[0] + at)[0]
                   for at in range(0, length, stride)]
        if all(ROM_BASE <= value < ROM_BASE + len(rom) for value in leaders):
            return stride, length // stride
    return 0, 0


def container(rom, span):
    return raw_remainder.webfoot_extent(rom, span[0]) is not None


def probed_container(rom, span):
    return jcalg1.probe(rom, span[0], min(span[1] - span[0], 0x4000)).get("reason") == "ok"


def text_class(rom, span):
    return text_tables.classify(rom, (span[0], span[1], "row", ""))[0]


def arm_branch_targets():
    out = {}
    for _file, _line, _token, start, end in arm_bodies.converted_rows():
        instructions, _gaps = arm_bodies.arm_decode(start, end)
        for offset, _size, mnemonic, operands, _bytes in instructions:
            if mnemonic not in ("b", "bl", "blx") or "#" not in operands:
                continue
            try:
                target = int(operands.split("#")[-1], 16)
            except ValueError:
                continue
            out.setdefault(target - ROM_BASE, "0x%08X %s" % (ROM_BASE + offset, mnemonic))
    return out


def channels(spans, rom):
    arm = arm_branch_targets()
    found = {
        "source": code_band_entries.first(thumb_bodies.entries(spans)),
        "converted": code_band_entries.first(thumb_bodies.converted_entries(spans)),
        "method": code_band_entries.first(thumb_bodies.method_entries(spans)),
        "pointer": code_band_entries.first(thumb_bodies.pointer_entries(spans)),
        "prologue": code_band_entries.first(thumb_bodies.prologue_entries(spans)),
        "arm_branch": {span: arm[target] for span in spans for target in arm
                       if span[0] <= target < span[1]},
    }
    return found, {}


def result_token(entry):
    parts = [entry["entry"] if entry["entry"] != "none" else "no-entry"]
    if entry["walk_returns"]:
        parts.append("walk-returns")
    for flag in ("container", "jcalg1", "ptrtable", "arm_branch"):
        if entry[flag]:
            parts.append(flag)
    if entry["text_class"] == "record table":
        parts.append("text-record-table")
    if entry["words"]:
        parts.append("word-named")
    return ";".join(parts)


def measure(rom=None, ledger_path=LEDGER, population_path=None):
    rom = read_rom() if rom is None else rom
    rows, fresh = population(population_path or ledger_path)
    ledger = ledger_rows(ledger_path)
    names = region_names()
    sides = neighbours(ledger, rows)
    spans = [(row["start"], row["end"]) for row in rows]
    words, scanned, addresses = word_index(rom, spans)
    found, _extra = channels(spans, rom)
    blocks = raw_remainder.graphics_blocks()
    table = []
    for row, span in zip(rows, spans):
        entry, site = code_band_entries.label(span, found)
        stride, records = stride_of(rom, span)
        previous, following = sides[span]
        table.append({
            "start": span[0], "end": span[1], "bytes": row["bytes"], "region": row["region"],
            "region_name": names.get(row["region"], "unknown region"),
            "prev_start": previous["start"] if previous else None,
            "prev_bytes": previous["bytes"] if previous else 0,
            "prev_status": previous["status"] if previous else "",
            "prev_attempts": previous["attempts"] if previous else "",
            "prev_adjacent": bool(previous and previous["adjacent"]),
            "next_start": following["start"] if following else None,
            "next_bytes": following["bytes"] if following else 0,
            "next_status": following["status"] if following else "",
            "next_attempts": following["attempts"] if following else "",
            "next_adjacent": bool(following and following["adjacent"]),
            "code_site": row["references"] if row["references"].startswith("code:") else "",
            "words": len(words.get(span, [])),
            "word_site": ("0x%06X=0x%08X" % words[span][0]) if span in words else "",
            "container": container(rom, span),
            "jcalg1": probed_container(rom, span),
            "entry": entry, "site": site,
            "walk_returns": walk_returns(rom, span),
            "ptrtable": pointer_table(rom, span),
            "stride": "%d/%d" % (stride, records) if stride else "",
            "text_class": text_class(rom, span),
            "block": next((subkind for low, high, subkind, _instrument in blocks
                           if low <= span[0] and span[1] <= high), ""),
            "thumb_entry": span in found["source"],
            **{name: span in found[name] for name in
               ("converted", "method", "pointer", "prologue", "arm_branch")},
        })
        table[-1]["result"] = result_token(table[-1])
    return table, {"words_scanned": scanned, "rows": rows, "hits": words,
                   "addresses": addresses, "fresh": fresh}


def cell(entry, field):
    value = entry[field]
    if field in ("start", "end", "prev_start", "next_start"):
        return "" if value is None else "0x%06x" % value
    if field in FLAGS or field in ("prev_adjacent", "next_adjacent"):
        return "yes" if value else "no"
    return " ".join(str(value).split()).replace(",", ";")


def csv_text(table):
    return "\n".join([",".join(FIELDS)]
                     + [",".join(cell(entry, field) for field in FIELDS)
                        for entry in table]) + "\n"


def tally(table, predicate):
    hits = [entry for entry in table if predicate(entry)]
    return len(hits), sum(entry["bytes"] for entry in hits)


def summary(table, extras):
    total = tally(table, lambda entry: True)
    lines = ["population: %d row(s) %d B" % total,
             "| region | rows | bytes |", "|---|---|---|"]
    for region in sorted({entry["region"] for entry in table}):
        count, size = tally(table, lambda entry, region=region: entry["region"] == region)
        lines.append("| `%s` | %d | %d |" % (region, count, size))
    lines += ["| reference channel | rows | bytes |", "|---|---|---|"]
    lines.append("| code site (the ledger's own) | %d | %d |"
                 % tally(table, lambda entry: bool(entry["code_site"])))
    lines.append("| a word names the row | %d | %d |"
                 % tally(table, lambda entry: bool(entry["words"])))
    lines.append("| neighbor is adjacent | %d | %d |"
                 % tally(table, lambda entry: entry["prev_adjacent"] or entry["next_adjacent"]))
    lines.append("words scanned: %d, of which %d are ROM addresses; %d word(s) name a row; a random "
                 "ROM address lands in the population with p = 58,359/8,388,608, so the expectation "
                 "is %.1f word(s)" % (extras["words_scanned"], extras["addresses"],
                                      sum(len(sites) for sites in extras["hits"].values()),
                                      extras["addresses"] * 58359 / float(1 << 23)))
    lines += ["| instrument | rows | bytes |", "|---|---|---|"]
    for flag in FLAGS:
        count, size = tally(table, lambda entry, flag=flag: entry[flag])
        lines.append("| `%s` | %d | %d |" % (flag, count, size))
    lines.append("| `stride` (leader words all addresses) | %d | %d |"
                 % tally(table, lambda entry: bool(entry["stride"])))
    lines.append("| `text_class == record table` | %d | %d |"
                 % tally(table, lambda entry: entry["text_class"] == "record table"))
    lines.append("| a graphics block covers it | %d | %d |"
                 % tally(table, lambda entry: bool(entry["block"])))
    return lines


def nulls(rom, table, extras):
    lines = []
    spans = [(entry["start"], entry["end"]) for entry in table]
    by_span = {(entry["start"], entry["end"]): entry for entry in table}

    def run(name, rule):
        real = [span for span in spans if rule(rom, span)]
        real_bytes = sum(span[1] - span[0] for span in real)
        null = [span for span in real if rule(permuted(rom, span), span)]
        null_bytes = sum(span[1] - span[0] for span in null)
        lines.append("%s: real %d row(s) %d B, permuted %d row(s) %d B (real and not permuted "
                     "%d row(s))"
                     % (name, len(real), real_bytes, len(null), null_bytes,
                        len(real) - len(null)))
        return real

    converted = [span for span in spans if by_span[span]["converted"]]
    if converted:
        entry_null = code_band_entries.source_null(converted)
        real = sum(1 for span in converted if walk_returns(rom, span))
        null = sum(1 for span in converted if walk_returns(permuted(rom, span), span))
        lines.append("converted-branch (%d rows %d B): the entry's site side, every Thumb source "
                     "span permuted: %d row(s) %d B; walk shape on the row: real %d, permuted %d"
                     % (len(converted), sum(s[1] - s[0] for s in converted),
                        entry_null[0], entry_null[1], real, null))
    run("walk-returns", lambda image, span: walk_returns(image, span))
    run("container (PACKED at the row start)",
        lambda image, span: container(image, span))
    run("row-bounded JCALG1", lambda image, span: probed_container(image, span))
    run("strict pointer table", lambda image, span: pointer_table(image, span))
    run("record stride", lambda image, span: bool(stride_of(image, span)[0]))
    run("text record table", lambda image, span: text_class(image, span) == "record table")
    named = [entry for entry in table if entry["words"]]
    if named:
        spans_named = [(entry["start"], entry["end"]) for entry in named]
        owner = {}
        for span in spans_named:
            for offset in range(span[0], span[1]):
                owner[offset] = span
        real_hits = sum(len(extras["hits"][span]) for span in spans_named)
        rng = random.Random(SEED)
        reach = set()
        for at in range(0, len(rom) - 3, 4):
            value = rng.getrandbits(32)
            span = owner.get((value & ~1) - ROM_BASE)
            if span is not None and not (span[0] <= at < span[1]):
                reach.add(span)
        lines.append("word-named (%d row(s) %d B): the site side, every grid word's VALUE replaced "
                     "by a uniform random 32-bit one: %d row(s) %d B; %d real word hit(s) against "
                     "%.1f expected of an address landing in the population"
                     % (len(named), sum(entry["bytes"] for entry in named),
                        len(reach), sum(span[1] - span[0] for span in reach), real_hits,
                        extras["addresses"] * 58359 / float(1 << 23)))
    return lines


def measured(path=CSV_OUT):
    with open(path, newline="", encoding="utf-8") as handle:
        return [{"start": int(row["start"], 16), "end": int(row["end"], 16),
                 "bytes": int(row["bytes"]), "region": row["region"],
                 "references": row["code_site"] or "none"}
                for row in csv.DictReader(handle)]


def check(path=CSV_OUT, ledger_path=LEDGER, expected=POPULATION):
    rows = measured(path)
    totals = (len(rows), sum(row["bytes"] for row in rows))
    if totals != expected:
        raise SystemExit("the tracked table is %d row(s) / %d B, not %d / %d"
                         % (totals + expected))
    want = {(row["start"], row["end"]) for row in rows}
    seen, missing = set(), []
    with open(ledger_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            span = (int(row["start"], 16), int(row["end"], 16))
            if span not in want:
                continue
            seen.add(span)
            if not row["attempts"].startswith("UNATTEMPTED-001:"):
                missing.append(span)
    print("CHECK: %d of %d measured row(s) still carry no UNATTEMPTED-001 token"
          % (len(missing), len(want)))
    for span in sorted(missing):
        print("  MISSING 0x%06X..0x%06X" % span)
    gone = sorted(want - seen)
    print("CHECK: %d row(s) are no longer INCBIN (converted): %s"
          % (len(gone), ", ".join("0x%06X" % span[0] for span in gone) or "none"))
    with open(ledger_path, newline="", encoding="utf-8") as handle:
        stale = [row for row in csv.DictReader(handle) if row["attempts"] == "none"]
    print("CHECK: %d ledger row(s) still read attempts `none`" % len(stale))
    return not missing and not stale


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--nulls", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        return 0 if check() else 1
    table, extras = measure()
    for line in summary(table, extras):
        print(line)
    if args.nulls:
        for line in nulls(read_rom(), table, extras):
            print(line)
    if args.write:
        if not extras["fresh"]:
            raise SystemExit("--write refused: the ledger no longer carries the population, so the "
                             "tracked table (%s) is the base's record"
                             % os.path.relpath(CSV_OUT, ROOT))
        with open(CSV_OUT, "w", encoding="ascii", newline="\n") as handle:
            handle.write(csv_text(table))
        print("wrote %s: %d row(s)" % (os.path.relpath(CSV_OUT, ROOT), len(table)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
