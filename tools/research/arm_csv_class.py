from __future__ import annotations

import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CSV_PATH = os.path.join(ROOT, "docs", "research", "TRANSCRIBED_DATA_RUNS.csv")
MANIFEST = os.path.join(ROOT, "build", "arm_bodies", "manifest.json")
THUMB_MANIFEST = os.path.join(ROOT, "build", "thumb_bodies", "manifest.json")
ARM_CLASS = "arm-body"
THUMB_CLASS = "thumb-body"
NOTE = "; transcribed as ARM source (PATH-100-017)"
THUMB_NOTE = "; transcribed as Thumb source (PATH-100-018)"


def base_rows():
    text = open(os.path.join(HERE, "transcribed_data_runs_base.csv"), encoding="utf-8").read()
    return list(csv.DictReader(text.splitlines()))


def spans(manifest, thumb=False):
    if os.path.exists(manifest):
        data = json.load(open(manifest))
        if not thumb:
            return {(entry["start"], entry["end"]) for entry in data["converted"]}
        out = set()
        for entry in data["rows"]:
            if entry.get("verdict") != "thumb-converted":
                continue
            for start, end in entry.get("runs", []):
                out.add((start, end))
        return out
    if thumb:
        return set()
    import csv as _csv
    frozen = os.path.join(ROOT, "docs", "research", "ARM_BODIES.csv")
    if not os.path.exists(frozen):
        return set()
    return {(int(row["start"], 16), int(row["end"], 16))
            for row in _csv.DictReader(open(frozen, newline="")) if row["verdict"] == "arm"}


def covered(row, spans_):
    start, end = int(row["rom_start"], 16), int(row["rom_end"], 16)
    return any(low <= start and end <= high for low, high in spans_)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    arm = spans(MANIFEST)
    thumb = spans(THUMB_MANIFEST, thumb=True)
    rows = base_rows()
    marked = {"arm-body": 0, "thumb-body": 0}
    for row in rows:
        if covered(row, arm):
            row["class"] = ARM_CLASS
            if not row["evidence"].endswith(NOTE):
                row["evidence"] += NOTE
            marked[ARM_CLASS] += 1
        elif covered(row, thumb):
            row["class"] = THUMB_CLASS
            if not row["evidence"].endswith(THUMB_NOTE):
                row["evidence"] += THUMB_NOTE
            marked[THUMB_CLASS] += 1
    totals = {}
    for row in rows:
        totals[row["class"]] = totals.get(row["class"], 0) + int(row["bytes"])
    print("rows %d; arm-body %d; thumb-body %d; totals %s; sum %d"
          % (len(rows), marked[ARM_CLASS], marked[THUMB_CLASS], totals,
             sum(totals.values())))
    if args.apply:
        fields = ["file", "line_first", "line_last", "rom_start", "rom_end", "bytes", "class",
                  "evidence"]
        with open(CSV_PATH, "w", encoding="ascii", newline="\n") as handle:
            handle.write(",".join(fields) + "\n")
            for row in rows:
                handle.write(",".join(row[field] for field in fields) + "\n")
        print("wrote %s" % CSV_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
