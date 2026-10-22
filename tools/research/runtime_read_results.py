"""The ticket's evidence products: per-row status, the citation table and the checked document.

Inputs are tracked and derived only from digests, addresses, widths and frames:

  * `docs/research/RUNTIME_TARGETS.csv` - the 100 plan rows;
  * `docs/research/MAP_ROW_OWNERS.csv`  - which MapEntry reaches each row (`map_row_owners.py`);
  * `docs/research/RUNTIME_READ_RUNS.csv` - one line per logged runtime run (arrival map, the
    liveness count, the log's digest, wall time);
  * `docs/research/RUNTIME_READ_CITATIONS.csv` - the citations `recomp_cited.py`'s rule kept;
  * `docs/research/RUNTIME_READ_ROW_HITS.csv` - per run and row, the hit count and the reader pcs.

Per row: `cited` (a hit whose pc is a transcribed ledger row), `read-uncited` (hits, but every
reader is outside the ledger - named by pc), `silent-live` (no hit while the same run's liveness
fired), `owner-map-not-reached` (no run visited an owner map), `not-run`.

    python tools/research/runtime_read_results.py --import <private run dir>
    python tools/research/runtime_read_results.py            # print the tables
    python tools/research/runtime_read_results.py --write
    python tools/research/runtime_read_results.py --check
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import recomp_cited  # noqa: E402

TARGETS = os.path.join(ROOT, "docs", "research", "RUNTIME_TARGETS.csv")
OWNERS = os.path.join(ROOT, "docs", "research", "MAP_ROW_OWNERS.csv")
RUNS = os.path.join(ROOT, "docs", "research", "RUNTIME_READ_RUNS.csv")
CITATIONS = os.path.join(ROOT, "docs", "research", "RUNTIME_READ_CITATIONS.csv")
ROW_HITS = os.path.join(ROOT, "docs", "research", "RUNTIME_READ_ROW_HITS.csv")
CSV_OUT = os.path.join(ROOT, "docs", "research", "RUNTIME_READ_RESULTS.csv")
DOC_OUT = os.path.join(ROOT, "docs", "research", "RUNTIME_READ_RESULTS.md")
GROUPS = ("set_b", "set_a")
FIELDS = ("group", "start", "end", "bytes", "status", "readers", "offsets", "widths", "frames",
          "owners", "liveness")
RUN_FIELDS = ("run", "scene", "status", "arrival", "witness", "witness_pc", "log_sha256",
              "log_lines", "patched_sha256", "seconds", "note")
DEFAULT_SCENE = "saved-game-warp"
HEX_FIELDS = ("start", "end", "reader_start", "reader_end", "address", "pc")
DECIMAL_FIELDS = ("run", "arrival", "witness", "log_lines", "hits", "width", "frame")


def read_csv(path):
    def value_of(key, value):
        if key in HEX_FIELDS:
            base = 16
        elif key in DECIMAL_FIELDS:
            base = 10
        else:
            return value
        try:
            return int(value, base)
        except ValueError:
            return None

    with open(path, newline="") as handle:
        return [{key: value_of(key, value) for key, value in row.items()}
                for row in csv.DictReader(handle)]


def inputs():
    targets = [row for row in read_csv(TARGETS) if row["group"] in GROUPS]
    owners = {row["start"]: [] for row in targets}
    with open(OWNERS, newline="") as handle:
        for row in csv.DictReader(handle):
            if row["owners"] != "owner unknown":
                owners[int(row["start"], 16)] = [int(token.split(":")[1])
                                                 for token in row["owners"].split(";")]
    runs = read_csv(RUNS)
    citations = read_csv(CITATIONS)
    row_hits = read_csv(ROW_HITS)
    for row in row_hits:
        row["pcs"] = [pc for pc in row.get("pcs", "").split(";") if pc]
    return targets, owners, runs, citations, row_hits


def visitors(runs, owner):
    return [run for run in runs if run["run"] in owner
            and run["status"] == "ok" and run["arrival"] == run["run"]]


def status_of(target, owners, runs, citations, row_hits):
    start, group = target["start"], target["group"]
    mine = [row for row in citations if row["start"] == start]
    hits = [row for row in row_hits if row["start"] == start and row["hits"]]
    covered = visitors(runs, owners.get(start, []))
    live = [run for run in covered if run["witness"]]
    if mine:
        return "cited", mine, live
    if hits:
        return "read-uncited", hits, live
    if covered and live:
        return "silent-live", [], live
    if covered:
        return "silent-dead-log", [], live
    return "owner-map-not-reached", [], live


def table_rows():
    targets, owners, runs, citations, row_hits = inputs()
    out = []
    for target in targets:
        status, evidence, live = status_of(target, owners, runs, citations, row_hits)
        start = target["start"]
        covered = visitors(runs, owners.get(start, []))
        scenes = []
        for run in covered:
            scene = run.get("scene") or DEFAULT_SCENE
            if scene not in scenes:
                scenes.append(scene)
        if status == "cited":
            readers = ";".join("0x%08x" % pc for pc in sorted({row["pc"] for row in evidence}))
        elif status == "read-uncited":
            readers = ";".join(sorted({pc for row in evidence for pc in row["pcs"]}))
        else:
            readers = ""
        out.append({
            "group": target["group"], "start": start, "end": target["end"],
            "bytes": target["end"] - start, "status": status,
            "readers": readers,
            "offsets": ";".join(str(recomp_cited.offset_of(row["address"]) - start)
                                for row in evidence)
            if status == "cited" else "",
            "widths": ";".join(str(row["width"]) for row in evidence) if status == "cited" else "",
            "frames": ";".join(str(row["frame"]) for row in evidence) if status == "cited" else "",
            "owners": ";".join("map:%04d" % index for index in owners.get(start, []))
            or "owner unknown",
            "liveness": "%d run(s) live, %d visitor(s) (%s)"
                        % (len(live), len(covered), ", ".join(scenes) or "-"),
        })
    return out, runs, citations, owners


def csv_text(rows):
    lines = [",".join(FIELDS)]
    for row in rows:
        lines.append(",".join(("0x%06x" % row[field]) if field in ("start", "end")
                              else str(row[field]) for field in FIELDS))
    return "\n".join(lines) + "\n"


def group_lines(rows):
    lines = ["| group | rows | bytes | cited | read-uncited | silent-live | owner-map-not-reached |",
             "|---|---|---|---|---|---|---|"]
    for group in GROUPS:
        mine = [row for row in rows if row["group"] == group]
        count = lambda status: sum(1 for row in mine if row["status"] == status)
        lines.append("| `%s` | %d | %d | %d | %d | %d | %d |"
                     % (group, len(mine), sum(row["bytes"] for row in mine),
                        count("cited"), count("read-uncited"), count("silent-live"),
                        count("owner-map-not-reached")))
    count = lambda status: sum(1 for row in rows if row["status"] == status)
    lines.append("| **total** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** |"
                 % (len(rows), sum(row["bytes"] for row in rows), count("cited"),
                    count("read-uncited"), count("silent-live"), count("owner-map-not-reached")))
    return lines


def boundary_offsets(citations):
    pcs = {}
    for row in citations:
        key = (row["start"], recomp_cited.offset_of(row["address"]) - row["start"])
        pcs.setdefault(key, set()).add(row["pc"])
    return sorted(key for key, seen in pcs.items() if len(seen) > 1)


def doc_text(rows, runs, citations):
    scenes = {}
    for run in runs:
        scene = run.get("scene") or DEFAULT_SCENE
        scenes[scene] = scenes.get(scene, 0) + 1
    lines = ["# RUNTIME-READ-001/002: what reads the map block's 100 rows",
             "",
             "Generated by `tools/research/runtime_read_results.py --write`; `--check` byte-compares",
             "these files with the regeneration from the tracked tables.",
             "",
             "## Method (MEASURED)",
             "",
             "* Instrument: a read-logging GBA runtime outside this repository, its ROM-read logger",
             "  (an output CSV plus a range file of `start end` hex FILE offsets, one CSV line per",
             "  read with `pc,lr,addr,width,frame`), driven headless from one input trace.",
             "* Route: the saved game boots to `map:0038`, and the measured trace walks down through",
             "  `map:0038/transition:0000` (record file offset `0x295C3C`) at frame 1920.",
             "* Reach: that one record is retargeted in a PRIVATE ROM copy per destination map",
             "  (two key bytes at `+0x11`/`+0x12`, guard-checked outside every watched row), and the",
             "  runtime is run with `--rom <copy> --rom-sha1 <copy>`.",
             "* Second scene: a row still silent after the warp is re-run on another entry - the game's",
             "  own opening without a save, or the same map reached and played. The runs table names",
             "  each run's `scene`; a row with no scene is `%s`." % DEFAULT_SCENE,
             "* Citation rule: `tools/research/recomp_cited.py` (RUNTIME_READ_PLAN P2) - the reader",
             "  `pc` must lie in a transcribed ledger row (`isa == t`) that is not the cited row.",
             "* Liveness: the engine's own MapEntry key comparison, `pc 0x08008A0E` reading the table",
             "  head at `0x0808E2E0`, must fire in the same run.",
             "* Runs: %d over the scenes %s."
             % (len(runs), ", ".join("`%s` %d" % pair for pair in sorted(scenes.items()))),
             "",
             "## Per-row status",
             "",
             *group_lines(rows),
             "",
             "| group | row | bytes | status | readers | offsets | widths | frames |",
             "|---|---|---|---|---|---|---|---|"]
    for row in rows:
        lines.append("| `%s` | `0x%06x..0x%06x` | %d | %s | %s | %s | %s | %s |"
                     % (row["group"], row["start"], row["end"], row["bytes"], row["status"],
                        row["readers"] or "-", row["offsets"] or "-", row["widths"] or "-",
                        row["frames"] or "-"))
    lines += ["", "## Runs (MEASURED)", "",
              "* Scene is the entry the run measured; a row with no scene was written before the",
              "  column and is `%s`, the retargeted transition." % DEFAULT_SCENE,
              "",
              "| map | scene | status | arrival | liveness count | log lines | log sha256 | seconds |",
              "|---|---|---|---|---|---|---|---|"]
    for run in runs:
        lines.append("| `map:%04d` | %s | %s | %s | %s | %s | `%s` | %s |"
                     % (run["run"], run.get("scene") or DEFAULT_SCENE, run["status"],
                        run.get("arrival") or "-", run["witness"],
                        run["log_lines"], (run.get("log_sha256") or "-")[:16], run["seconds"]))
    boundaries = boundary_offsets(citations)
    lines += ["", "## Field boundaries a citation marks", "",
              "%d read offset(s) in %d cited row(s) carry two or more distinct reader pcs"
              % (len(boundaries), len({start for start, _offset in boundaries})),
              "(%s); each such offset is a field boundary in the plan's predicate."
              % ", ".join("`0x%06x`+%d" % pair for pair in boundaries), ""]
    return "\n".join(lines) + "\n"


def write(rows, runs, citations):
    with open(CSV_OUT, "w", encoding="ascii", newline="\n") as handle:
        handle.write(csv_text(rows))
    with open(DOC_OUT, "w", encoding="ascii", newline="\n") as handle:
        handle.write(doc_text(rows, runs, citations))


def check():
    rows, runs, citations, _owners = table_rows()
    with open(CSV_OUT, encoding="ascii") as handle:
        if handle.read() != csv_text(rows):
            raise SystemExit("RUNTIME_READ_RESULTS.csv does not match its inputs")
    with open(DOC_OUT, encoding="ascii") as handle:
        if handle.read() != doc_text(rows, runs, citations):
            raise SystemExit("RUNTIME_READ_RESULTS.md does not match its inputs")
    print("CHECK PASS: RUNTIME_READ_RESULTS.csv and .md match the tracked tables")


def migrate(directories):
    if isinstance(directories, str):
        directories = [directories]
    for name, target in (("runs.csv", RUNS), ("citations.csv", CITATIONS),
                         ("row-hits.csv", ROW_HITS)):
        rows, fields, without_scene = [], [], []
        for directory in directories:
            with open(os.path.join(directory, name), newline="") as handle:
                reader = csv.DictReader(handle)
                found = list(reader)
                header = reader.fieldnames or []
            for field in header:
                if field not in fields:
                    fields.append(field)
            if name == "runs.csv" and "scene" not in header:
                without_scene.extend(found)
            rows.extend(found)
        if "scene" in fields:
            fields.remove("scene")
            fields.insert(1, "scene")
            for row in without_scene:
                row["scene"] = DEFAULT_SCENE
        with open(target, "w", encoding="ascii", newline="\n") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print("imported %s -> %s (%d row(s))"
              % (name, os.path.relpath(target, ROOT), len(rows)))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--import", dest="directory", nargs="+")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.directory:
        migrate(args.directory)
        return 0
    rows, runs, citations, _owners = table_rows()
    for line in group_lines(rows):
        print(line)
    if args.check:
        check()
    if args.write:
        write(rows, runs, citations)
        print("wrote %s and %s" % (os.path.relpath(CSV_OUT, ROOT),
                                   os.path.relpath(DOC_OUT, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
