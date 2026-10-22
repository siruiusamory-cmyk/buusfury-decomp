from __future__ import annotations

import argparse
import collections
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, os.path.join(ROOT, "tools", "gate"), ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import incbin_census  # noqa: E402
import row_readers  # noqa: E402

REGIONS = ("R20", "R21", "R23", "R24", "R25", "R26", "R27", "R28", "R29", "R30", "R31")
POPULATION = (1129, 328954)
GATE_RAW = 584374
REMAINDER = os.path.join(ROOT, "docs", "research", "RAW_REMAINDER.csv")
READS = os.path.join(ROOT, "docs", "research", "ENDROM_READS.csv")
ROWS_OUT = os.path.join(ROOT, "docs", "research", "ENDROM_ROWS.csv")
DOC_OUT = os.path.join(ROOT, "docs", "research", "ENDROM_NULL_CENSUS.md")
RULES = (
    ("cited", "a cited read names the pc that read a byte of the row"),
    ("read", "a read logged in play names the pc that read a byte of the row"),
    ("pool", "the row's every grid word is the target of a decoded pc-literal load"),
    ("code-null", "a decoded branch enters and an instruction decodes, but the branch channel loses to "
                  "its own permutation null"),
    ("pool-fragment", "a word loaded inside the row ends past its end"),
    ("pool-partial", "some grid words load, the rest have no decoded reader"),
    ("named-data", "a decoded load's literal word names the row and no layout follows"),
    ("after-dispatch", "the row sits after a computed jump and no instruction reads it"),
    ("between", "the row sits between two transcribed code rows, unread"),
    ("unreached", "no decoded reader and no naming word"),
)


def population():
    spans, region_of = [], {}
    for row in csv.DictReader(open(REMAINDER, newline="")):
        if row["region"] not in REGIONS:
            continue
        span = (int(row["start"], 16), int(row["end"], 16))
        spans.append(span)
        region_of[span] = row["region"]
    spans.sort()
    measured = (len(spans), sum(end - start for start, end in spans))
    if measured != POPULATION:
        raise SystemExit("the population is %d row(s) / %d B, not %d / %d: the census moved"
                         % (measured + POPULATION))
    return spans, region_of


def reads(spans):
    cited, play, cited_sites, play_sites = {}, {}, 0, 0
    by_span = {span: span for span in spans}
    for row in csv.DictReader(open(READS, newline="")):
        span = by_span[(int(row["start"], 16), int(row["end"], 16))]
        found = [int(text, 16) for text in row["cited_pcs"].split(";") if text]
        if found:
            cited[span] = found
            cited_sites += len(found)
        found = [int(text, 16) for text in row["play_pcs"].split(";") if text]
        if found:
            play[span] = found
            play_sites += len(found)
    return cited, cited_sites, play, play_sites


def read_pcs(row, cited, play):
    out = [("cited", pc) for pc in cited.get(row, [])]
    out += [("play", pc) for pc in play.get(row, [])]
    return out


def reader_text(entry, cited, play):
    parts = ["%s %08X" % pair for pair in read_pcs(entry["row"], cited, play)[:2]]
    if entry["family"] == "pool" and entry["readers"]:
        parts.append("%s (x%d)" % (entry["readers"][0][2], len(entry["readers"])))
    elif entry["readers"]:
        parts.append("%s (x%d)" % (entry["readers"][0][2], len(entry["readers"])))
    if entry["branches"]:
        parts.append(entry["branches"][0][2])
    if entry["value_sites"]:
        parts.append(entry["value_sites"][0][2])
    if entry["word_names"]:
        parts.append("%d naming word(s)" % entry["word_names"])
    return "; ".join(parts) if parts else "none"


def class_of(entry, cited, play):
    if cited.get(entry["row"]):
        return "cited"
    if play.get(entry["row"]):
        return "read"
    return row_readers.class_of(entry)


def measure(image, spans):
    data = row_readers.measure(image, spans)
    cited, cited_sites, play, play_sites = reads(spans)
    for span in spans:
        data["table"][span]["row"] = span
    data["cited"] = cited
    data["cited_sites"] = cited_sites
    data["play"] = play
    data["play_sites"] = play_sites
    return data


def region_name(region):
    for index, entry in enumerate(incbin_census.REGIONS, 1):
        if "R%02d" % index == region:
            return entry.name
    return "no measured region"


def doc_text(spans, region_of, data, image):
    table = data["table"]
    cited, play = data["cited"], data["play"]
    total = sum(end - start for start, end in spans)
    by_region = collections.defaultdict(lambda: {"rows": 0, "bytes": 0, "cited_rows": 0,
                                                 "cited_bytes": 0, "play_rows": 0,
                                                 "play_bytes": 0, "read_rows": 0,
                                                 "read_bytes": 0})
    for span in spans:
        bucket = by_region[region_of[span]]
        bucket["rows"] += 1
        bucket["bytes"] += span[1] - span[0]
        if cited.get(span):
            bucket["cited_rows"] += 1
            bucket["cited_bytes"] += span[1] - span[0]
        if play.get(span):
            bucket["play_rows"] += 1
            bucket["play_bytes"] += span[1] - span[0]
        if cited.get(span) or play.get(span):
            bucket["read_rows"] += 1
            bucket["read_bytes"] += span[1] - span[0]
    unread = [span for span in spans if not cited.get(span) and not play.get(span)]
    classes = collections.Counter(class_of(table[span], cited, play) for span in spans)
    class_bytes = collections.Counter()
    for span in spans:
        class_bytes[class_of(table[span], cited, play)] += span[1] - span[0]
    stats = {span: row_readers.byte_stats(image, span) for span in spans}
    lines = [
        "# The end-of-ROM regions' raw rows: a reader per row, and its null",
        "",
        "`%s` is %d rows / %d B as `docs/research/RAW_REMAINDER.csv` carries them, the same"
        % ("`/`".join(REGIONS[0:2] + REGIONS[2:]), len(spans), total),
        "figure as `python tools\\research\\raw_remainder.py` reports for the ledger's identified",
        "binary (%d B) against the gate's raw-data (%d B). Data addresses are file offsets,"
        % (POPULATION[1], GATE_RAW),
        "instruction addresses are bus addresses `0x08...`, and every quote is a Thumb decode of the",
        "bytes at that address. The reader for a row is the first pc, in the order the channels below",
        "are listed, that reads a byte of it. No row's null below claims that a byte cannot be",
        "reduced: a reader this census does not hold would move the row.",
        "",
        "## Totals by region",
        "",
        "| region | spans | rows | bytes | rows with a cited pc | cited bytes | rows read in play "
        "| play bytes | rows with a read pc | read bytes | rows without a read pc |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for region in REGIONS:
        bucket = by_region.get(region)
        if not bucket:
            continue
        lines.append("| `%s` | %s | %d | %d | %d | %d | %d | %d | %d | %d | %d |"
                     % (region, region_name(region), bucket["rows"], bucket["bytes"],
                        bucket["cited_rows"], bucket["cited_bytes"], bucket["play_rows"],
                        bucket["play_bytes"], bucket["read_rows"], bucket["read_bytes"],
                        bucket["rows"] - bucket["read_rows"]))
    lines += [
        "| **total** | | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** | "
        "**%d** |"
        % (len(spans), total, sum(b["cited_rows"] for b in by_region.values()),
           sum(b["cited_bytes"] for b in by_region.values()),
           sum(b["play_rows"] for b in by_region.values()),
           sum(b["play_bytes"] for b in by_region.values()),
           len(spans) - len(unread), sum(span[1] - span[0] for span in spans) -
           sum(span[1] - span[0] for span in unread), len(unread)),
        "",
        "| class | rows | bytes | rule |",
        "|---|---|---|---|",
    ] + ["| `%s` | %d | %d | %s |" % (name, classes[name], class_bytes[name], rule)
         for name, rule in RULES] + [
        "| **total** | **%d** | **%d** | |" % (len(spans), total),
        "",
        "`%d` rows / `%d` B have no read pc at any denominator below."
        % (len(unread), sum(span[1] - span[0] for span in unread)),
        "",
        "## What was searched, and its denominator",
        "",
        "| channel | instrument | denominator | result on these rows |",
        "|---|---|---|---|",
        "| cited read of a byte of the row | `docs/research/ENDROM_READS.csv`, cited column | %d "
        "pc(s) | %d row(s) |" % (data["cited_sites"], len(cited)),
        "| read of a byte of the row in play | `docs/research/ENDROM_READS.csv`, play column | %d "
        "pc(s) | %d row(s) |" % (data["play_sites"], len(play)),
        "| decoded `ldr [pc,#imm]` literal address in the row | `row_readers.walked_literals` | %d "
        "walked bod(ies): %d ledger Thumb row(s) | %d row(s) with >= 1 word |"
        % (data["sources"][0], data["sources"][0] - data["sources"][1],
           sum(1 for span in spans if data["literal"].get(span))),
        "| decoded branch at an instruction boundary inside a walked body | `row_readers.walked_branches` "
        "| %d decoded instruction(s) | %d row(s) |" % (data["instructions"], len(data["branches"])),
        "| decoded `ldr` whose literal VALUE names the row | `consumer_search.literal_loads` | %d "
        "code row(s) / %d B, %d load(s) | %d row(s) |"
        % (len(data["code"]), sum(length for _s, length, _m, _i in data["code"]), data["loads"],
           len(data["values"])),
        "| word-aligned word holding an address in the row | `row_readers.naming_words` | %d words | "
        "%d row(s), %d word(s) |" % (data["words_scanned"], len(data["words"]),
                                     sum(data["words"].values())),
        "",
        "Every count is half-open over each row's own span. A naming word is a name, not a consumer",
        "(P-733), and a literal-shaped halfword inside a data stream is not a reader (P-721).",
        "A read of a byte is a consumer whatever register it lands in, and the read table holds one",
        "pc per reader of the row it reached.",
        "",
        "## Byte statistics",
        "",
        "Entropy %.2f..%.2f bits/byte, zero-byte share %.2f..%.2f, %d row(s) are a single halfword,"
        % (min(s[0] for s in stats.values()), max(s[0] for s in stats.values()),
           min(s[1] for s in stats.values()), max(s[1] for s in stats.values()),
           sum(1 for span in spans if span[1] - span[0] == 2)),
        "%d row(s) are not a whole number of words and %d hold at least one word that is an address"
        % (sum(1 for span in spans if (span[1] - span[0]) % 4), sum(1 for s in stats.values() if s[3])),
        "in the image.",
        "",
        "## The per-row null",
        "",
        "Each line: file offsets, region, bytes, entropy, zero-byte share, word-aligned words inside",
        "the row, words of it that are an address in the image, class, the reader with its site, and",
        "why the row stays raw. `none` means no instruction in the channels above names a byte of the",
        "row at the denominators quoted.",
        "",
        "| start | end | region | bytes | ent | zero | words | in | class | readers | null |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for span in spans:
        entry = table[span]
        entropy, zero, words, inside = stats[span]
        lines.append("| `0x%X` | `0x%X` | `%s` | %d | %.2f | %.2f | %d | %d | `%s` | %s | %s |"
                     % (span[0], span[1], region_of[span], span[1] - span[0], entropy, zero,
                        words, inside, class_of(entry, cited, play),
                        reader_text(entry, cited, play),
                        entry["reason"] or "decoded, section above"))
    return "\n".join(lines) + "\n"


def write(spans, region_of, data, image):
    with open(ROWS_OUT, "w", encoding="ascii", newline="\n") as handle:
        handle.write("start,end,region\n")
        for span in spans:
            handle.write("0x%06X,0x%06X,%s\n" % (span[0], span[1], region_of[span]))
    with open(DOC_OUT, "w", encoding="ascii", newline="\n") as handle:
        handle.write(doc_text(spans, region_of, data, image))
    print("wrote %s and %s" % (os.path.relpath(ROWS_OUT, ROOT), os.path.relpath(DOC_OUT, ROOT)))


def check():
    image = row_readers.rom()
    spans, region_of = population()
    data = measure(image, spans)
    if not os.path.exists(DOC_OUT):
        raise SystemExit("%s is missing" % os.path.relpath(DOC_OUT, ROOT))
    with open(DOC_OUT, encoding="ascii") as handle:
        stored = handle.read()
    if stored != doc_text(spans, region_of, data, image):
        raise SystemExit("%s does not match the census re-derived from the image"
                         % os.path.relpath(DOC_OUT, ROOT))
    print("CHECK: %s matches the census, %d row(s)" % (os.path.relpath(DOC_OUT, ROOT), len(spans)))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        return check()
    image = row_readers.rom()
    spans, region_of = population()
    data = measure(image, spans)
    print("population %d row(s) %d B; cited %d row(s); play %d row(s); literal %d row(s); branch %d; "
          "value %d; naming %d row(s)"
          % (len(spans), POPULATION[1], len(data["cited"]), len(data["play"]),
             sum(1 for span in spans if data["literal"].get(span)), len(data["branches"]),
             len(data["values"]), len(data["words"])))
    counts = collections.Counter(class_of(data["table"][span], data["cited"], data["play"])
                                 for span in spans)
    for name in sorted(counts):
        print("  %-14s %4d row(s) %6d B" % (name, counts[name],
                                            sum(span[1] - span[0] for span in spans
                                                if class_of(data["table"][span], data["cited"],
                                                            data["play"]) == name)))
    if args.write:
        write(spans, region_of, data, image)
    return 0


if __name__ == "__main__":
    sys.exit(main())
