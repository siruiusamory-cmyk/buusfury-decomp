"""One row per interval waiting on the single runtime read session.

Three tracked CSVs in, one CSV out:

  * `docs/research/MAP_BLOCK_ROWS.csv` - the map block's own per-row table. Its `reader` column
    splits the block at the boundary K-217 and K-218 measured: `unproven` is set (b) (62 rows /
    31,808 B, child-list named, read by no instruction), everything else is set (a) (38 rows /
    58,404 B, a root field's data and no reader);
  * `docs/research/RESIDUAL_LEDGER.csv` - the ledger's `runtime-pending` rows (84 rows / 28,800 B,
    2026-10-19; BF-103's sprite rows took 5 rows / 1,480 B out of the class):
    rows a runtime-cited channel names and the block's fence keeps out of `identified binary`;
  * `docs/research/CODE_BAND_ENTRIES.csv` - the five rows CODE-BAND-005's pointer channel named.
    The one that CARRIES the 0x68-byte record family (K-220, `0x0701FA`) is its own group and the
    four other pointer rows are another, because one read answers one question.

Every group's rows and bytes are pinned here, so a moved census is refused rather than quoted; the
two map-block halves must also add up to the block's own total (100 rows / 90,212 B, the number
`residual_causes --check` prints).

    python tools/research/runtime_targets.py            # the group table
    python tools/research/runtime_targets.py --write    # + docs/research/RUNTIME_TARGETS.csv
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

LEDGER = os.path.join(ROOT, "docs", "research", "RESIDUAL_LEDGER.csv")
MAP_ROWS = os.path.join(ROOT, "docs", "research", "MAP_BLOCK_ROWS.csv")
ENTRIES = os.path.join(ROOT, "docs", "research", "CODE_BAND_ENTRIES.csv")
CSV_OUT = os.path.join(ROOT, "docs", "research", "RUNTIME_TARGETS.csv")
FIELDS = ("group", "start", "end", "bytes", "region", "static_negative", "question")
GROUPS = ("set_a", "set_b", "runtime_pending", "pointer_0x68", "pointer_other")
EXPECT = {"set_a": (38, 58404), "set_b": (62, 31808), "runtime_pending": (84, 28800),
          "pointer_0x68": (1, 5470), "pointer_other": (4, 15380)}
MAP_TOTAL = (100, 90212)
NEGATIVE = {"set_a": "K-217", "set_b": "K-218", "runtime_pending": "T-197",
            "pointer_0x68": "K-220", "pointer_other": "K-220"}
QUESTION = {
    "set_a": "does any instruction read these bytes while a map is live, and at what width?",
    "set_b": "does any instruction read this child-list payload, and at what offset from its start?",
    "runtime_pending": "which instruction reads this row, and is the access a read or a write?",
    "pointer_0x68": "what bounds the 0x68-byte record array whose base sits at 0x080716A8?",
    "pointer_other": "which field of the named object is dereferenced, and with what stride?",
}
RECORD_ROW = 0x0701FA


def read_rows(path):
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle))


def group_of_map_row(row):
    return "set_b" if row["reader"] == "unproven" else "set_a"


def table(ledger, map_rows, entries):
    out = []

    def add(group, start, end, region):
        out.append({"group": group, "start": start, "end": end, "bytes": end - start,
                    "region": region, "static_negative": NEGATIVE[group],
                    "question": QUESTION[group]})

    for row in map_rows:
        span = (int(row["start"], 16), int(row["end"], 16))
        add(group_of_map_row(row), span[0], span[1], "map")
    for row in ledger:
        if row["status"] != "runtime-pending":
            continue
        span = (int(row["start"], 16), int(row["end"], 16))
        add("runtime_pending", span[0], span[1], row["region"])
    for row in entries:
        if row["entry"] != "pointer":
            continue
        span = (int(row["start"], 16), int(row["end"], 16))
        add("pointer_0x68" if span[0] == RECORD_ROW else "pointer_other", span[0], span[1],
            row["region"])
    return out


def totals(rows):
    out = {}
    for row in rows:
        count, size = out.get(row["group"], (0, 0))
        out[row["group"]] = (count + 1, size + row["bytes"])
    return out


def check(rows):
    found = totals(rows)
    for name in GROUPS:
        if found.get(name) != EXPECT[name]:
            raise SystemExit("%s measures %s, not %s: the census moved"
                             % (name, found.get(name), EXPECT[name]))
    pair = (found["set_a"][0] + found["set_b"][0], found["set_a"][1] + found["set_b"][1])
    if pair != MAP_TOTAL:
        raise SystemExit("the map block measures %d rows / %d B, not %d / %d"
                         % (pair + MAP_TOTAL))
    return found


def summary(rows):
    found = totals(rows)
    lines = ["| group | rows | bytes | static negative | question |", "|---|---|---|---|---|"]
    for name in GROUPS:
        lines.append("| `%s` | %d | %d | %s | %s |"
                     % (name, found[name][0], found[name][1], NEGATIVE[name], QUESTION[name]))
    lines.append("| **total** | **%d** | **%d** | | |"
                 % (len(rows), sum(row["bytes"] for row in rows)))
    lines.append("map block: set_a + set_b = %d rows / %d B against residual_causes' %d / %d"
                 % (found["set_a"][0] + found["set_b"][0],
                    found["set_a"][1] + found["set_b"][1], MAP_TOTAL[0], MAP_TOTAL[1]))
    return lines


def csv_text(rows):
    lines = [",".join(FIELDS)]
    for row in rows:
        lines.append(",".join(("0x%06x" % row[field]) if field in ("start", "end")
                              else str(row[field]) for field in FIELDS))
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    rows = table(read_rows(LEDGER), read_rows(MAP_ROWS), read_rows(ENTRIES))
    check(rows)
    for line in summary(rows):
        print(line)
    if args.write:
        with open(CSV_OUT, "w", encoding="ascii", newline="\n") as handle:
            handle.write(csv_text(rows))
        print("wrote %s: %d row(s)" % (os.path.relpath(CSV_OUT, ROOT), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
