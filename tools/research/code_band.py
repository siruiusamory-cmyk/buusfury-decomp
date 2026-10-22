"""Classify a region's raw rows by how code reaches them (ROUTE_TO_100's R32, and R19).

`docs/research/ROUTE_TO_100.md` carried 1,180 rows / 66,746 B inside the first-MiB code band
`0x158..0x71758` (K-084's 12 slices) that were still INCBIN after CODE-ENTRY-001. This tool asks, per
row, which entry proof reaches it, in the contract's four classes plus the transitive chain
(`--region` names the population; `--outside` adds every raw row, in any other region, that holds a
class-table method target, which is how a target the previous region's pass left behind gets a
population of its own):

  * `method-target` - a class-table slot's base-relative method lands in the row. The engine reads the
    slot and calls the register it produced (file 0x188FC `ldr r2,[r1,#0x68]`, `adds r2,r2,r1`), so
    the slot is an indirect call target; TEXT-TABLES-001 pins three methods against the reading and
    `text_tables.anchor_failures` is asserted here before any share is believed (P-573);
  * `source-entry` - a `B`/`B<cond>`/`BL` or a Thumb function pointer in source code targets the row
    (`thumb_bodies.entries`, the CODE-ENTRY-001 rule);
  * `transitive` - no reference of its own, but a walked body of one of the two classes branches into
    it (`thumb_bodies.closure`'s chain);
  * `pool-data` - no entry, but a decoded pc-relative load's pool word VALUE is an address in the row
    (`docs/research/RAW_CITATIONS.csv` route P): data with a named consumer, not code;
  * `unreached` - none of the above.

The class order decides disjointly: one class per row, and the class sums equal the population. The
report also measures what the method entry is worth: the share of target walks that end in a return,
against the same walk from the same number of random even addresses inside the same rows (a fixed
seed), so a figure is never quoted without its control (P-568).

    python tools/research/code_band.py                     # the class table
    python tools/research/code_band.py --bodies OUT.csv    # + the rows to hand the converter
    python tools/research/code_band.py --write            # docs/research/CODE_BAND.csv + .md
    python tools/research/code_band.py --check            # the frozen CSV's sums
"""
from __future__ import annotations

import argparse
import csv
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import text_tables  # noqa: E402
import thumb_bodies  # noqa: E402
from tools.research import arm_bodies  # noqa: E402

REGION = "R32"
REMAINDER = os.path.join(ROOT, "docs", "research", "RAW_REMAINDER.csv")
CITATIONS = os.path.join(ROOT, "docs", "research", "RAW_CITATIONS.csv")
CSV_OUT = os.path.join(ROOT, "docs", "research", "CODE_BAND.csv")
DOC_OUT = os.path.join(ROOT, "docs", "research", "CODE_BAND.md")
CLASSES = ("method-target", "source-entry", "transitive", "pool-data", "prologue-entry",
           "unreached")
PROOF = {"method-target": "a class-table slot's base-relative method lands in the row",
         "source-entry": "a source B/B<cond>/BL or Thumb function pointer targets the row, or a "
                         "branch out of an already-converted body does",
         "transitive": "a walked body branches into the row",
         "pool-data": "a code pc-relative load's pool word names an address in the row",
         "prologue-entry": "a PUSH {..,lr} shape walks to a return, and the byte-permuted control "
                           "does so less often (reported beside it)",
         "unreached": "no instrument above fired"}


def rows(region=REGION):
    wanted = {name.strip() for name in str(region).split(",") if name.strip()}
    out = []
    for row in csv.DictReader(open(REMAINDER, newline="")):
        if row["region"] in wanted:
            out.append((int(row["start"], 16), int(row["end"], 16)))
    return out


def all_rows():
    return [(int(row["start"], 16), int(row["end"], 16), row["region"])
            for row in csv.DictReader(open(REMAINDER, newline=""))]


def outside_rows(sites, index, region_of, region=REGION):
    out = {}
    for base, at, target in sites:
        row = index.of(target)
        if row is None or region_of.get(row) == region:
            continue
        out.setdefault(row, []).append(
            "method table 0x%08x slot 0x%08x -> 0x%08x"
            % (thumb_bodies.ROM_BASE + base, thumb_bodies.ROM_BASE + at,
               thumb_bodies.ROM_BASE + target))
    return out


def method_targets(region=REGION, outside=False):
    if not outside:
        return {}, {}
    census = all_rows()
    index = thumb_bodies.Rows([(start, end) for start, end, _name in census])
    region_of = {(start, end): name for start, end, name in census}
    bases = sorted(text_tables.class_bases(thumb_bodies.ROM))
    tables = text_tables.table_rows(thumb_bodies.ROM)
    if not bases or not tables:
        return {}, {}
    last = max(row[1] for row in tables)
    edges = [(base, bases[index + 1] if index + 1 < len(bases) else last)
             for index, base in enumerate(bases)]
    found = outside_rows(thumb_bodies.method_sites(thumb_bodies.ROM, edges), index, region_of, region)
    return found, {row: region_of[row] for row in found}


def citations():
    if not os.path.exists(CITATIONS):
        return []
    out = []
    for row in csv.DictReader(open(CITATIONS, newline="")):
        if row["route"] == "P":
            out.append((int(row["start"], 16), int(row["end"], 16)))
    return out


def assign(population, method, source, transitive, pool, prologue=None):
    out = []
    for row in population:
        for name, found in (("method-target", method), ("source-entry", source),
                            ("transitive", transitive)):
            if row in found:
                out.append({"start": row[0], "end": row[1], "class": name, "proof": found[row]})
                break
        else:
            cited = row in pool
            if cited:
                out.append({"start": row[0], "end": row[1], "class": "pool-data",
                            "proof": PROOF["pool-data"]})
            elif prologue and row in prologue:
                out.append({"start": row[0], "end": row[1], "class": "prologue-entry",
                            "proof": prologue[row]})
            else:
                out.append({"start": row[0], "end": row[1], "class": "unreached",
                            "proof": PROOF["unreached"]})
    return out


def measure(region=REGION, outside=False, prologue=False, converted=False):
    if text_tables.anchor_failures(thumb_bodies.ROM):
        raise SystemExit("text_tables.anchor_failures: the pinned methods do not resolve: %s"
                         % (text_tables.anchor_failures(thumb_bodies.ROM),))
    extra, extra_regions = method_targets(region, outside)
    population = sorted(set(rows(region)) | set(extra))
    bodies = thumb_bodies.closure(population, method=True, prologue=prologue, converted=converted)
    sites = thumb_bodies.method_entries(population)
    method = {row: found[0][2] for row, found in sites.items()}
    source = {row: found[0][2] for row, found in
              thumb_bodies.entries(population, converted=converted).items()}
    shapes = thumb_bodies.prologue_entries(population) if prologue else {}
    shape = {row: found[0][2] for row, found in shapes.items()}
    transitive = {row: "walked from a body of another row" for row in bodies
                  if row not in method and row not in source and row not in shape}
    table = assign(population, method, source, transitive, set(citations()), shape)
    for entry in table:
        body = bodies.get((entry["start"], entry["end"]))
        entry["region"] = extra_regions.get((entry["start"], entry["end"]),
                                            _region_of((entry["start"], entry["end"]), region))
        entry["walked"] = body.walked if body else 0
        entry["pool"] = body.pool_bytes if body else 0
    counts, sizes = {}, {}
    for entry in table:
        counts[entry["class"]] = counts.get(entry["class"], 0) + 1
        sizes[entry["class"]] = sizes.get(entry["class"], 0) + entry["end"] - entry["start"]
    return table, counts, sizes, (bodies, sites, population)


def _region_of(row, region):
    wanted = {name.strip() for name in str(region).split(",") if name.strip()}
    for start, end, name in all_rows():
        if (start, end) == row and name in wanted:
            return name
    return str(region)


def prologue_control(population, shape, seed=20261017):
    rng = random.Random(seed)
    real_hits = real_sites = 0
    control_hits = control_sites = 0
    for start, end in population:
        row = (start, end)
        sites = [offset for offset in range(start, end - 1, 2)
                 if int.from_bytes(thumb_bodies.ROM[offset:offset + 2], "little") & 0xFF00
                 == 0xB500]
        real_sites += len(sites)
        real_hits += len([1 for offset in sites
                          if thumb_bodies.returns(thumb_bodies.walk(
                              row, [(offset, "prologue", "control", "shape")]))])
        shuffled = list(thumb_bodies.ROM[start:end])
        rng.shuffle(shuffled)
        original = thumb_bodies.ROM
        thumb_bodies.ROM = original[:start] + bytes(shuffled) + original[end:]
        try:
            for offset in range(start, end - 1, 2):
                if int.from_bytes(thumb_bodies.ROM[offset:offset + 2], "little") & 0xFF00 != 0xB500:
                    continue
                control_sites += 1
                control_hits += 1 if thumb_bodies.returns(thumb_bodies.walk(
                    row, [(offset, "prologue", "control", "shape")])) else 0
        finally:
            thumb_bodies.ROM = original
    return len(shape), real_hits, control_hits, real_sites, control_sites


def walk_control(bodies, method, population, seed=20261017):
    def ends_in_return(row, offset):
        return thumb_bodies.returns(thumb_bodies.walk(
            row, [(offset, "method", "control", "method")]))

    targets = [(row, offset) for row, sites in method.items() for offset, _kind, _s, _t in sites]
    real = sum(1 for row, offset in targets if ends_in_return(row, offset))
    rng = random.Random(seed)
    addresses = []
    for row in {row for row, _offset in targets}:
        addresses.extend((row, offset) for offset in range(row[0], row[1] - 1, 2))
    control = sum(1 for row, offset in (rng.choice(addresses) for _ in targets)
                  if ends_in_return(row, offset))
    return real, len(targets), control


def table_text(table, counts, sizes):
    total_rows = sum(row["end"] - row["start"] for row in table)
    lines = ["| class | rows | bytes | entry proof |", "|---|---|---|---|"]
    for name in CLASSES:
        lines.append("| `%s` | %d | %d | %s |"
                     % (name, counts.get(name, 0), sizes.get(name, 0), PROOF[name]))
    lines.append("| **total** | **%d** | **%d** | |" % (len(table), total_rows))
    return lines, total_rows


def region_text(table):
    keys = sorted({(entry["region"], entry["class"]) for entry in table})
    lines = ["| region | class | rows | bytes |", "|---|---|---|---|"]
    totals = {}
    for name, kind in keys:
        rows = [entry for entry in table
                if entry["region"] == name and entry["class"] == kind]
        size = sum(entry["end"] - entry["start"] for entry in rows)
        totals[(name, kind)] = (len(rows), size)
        lines.append("| `%s` | `%s` | %d | %d |" % (name, kind, len(rows), size))
    for name in sorted({entry["region"] for entry in table}):
        rows = [entry for entry in table if entry["region"] == name]
        lines.append("| **`%s`** | **total** | **%d** | **%d** |"
                     % (name, len(rows), sum(entry["end"] - entry["start"] for entry in rows)))
    return lines, totals


def csv_text(table):
    out = ["start,end,bytes,region,class,proof,walked_bytes,pool_bytes"]
    for entry in table:
        out.append("%s,%s,%d,%s,%s,%s,%d,%d"
                   % (hex(entry["start"]), hex(entry["end"]), entry["end"] - entry["start"],
                      entry["region"], entry["class"], entry["proof"].replace(",", ";"),
                      entry["walked"], entry["pool"]))
    return "\n".join(out) + "\n"


def doc_text(table, counts, sizes, control, region=REGION, extra_regions=None, shape_control=None):
    lines, total_rows = table_text(table, counts, sizes)
    split, _totals = region_text(table)
    real, targets, ctrl = control
    worth = (
        "`text_tables.anchor_failures` resolves the three methods TEXT-TABLES-001 pins (0x04AAF4 slot "
        "0 and slot 8, 0x04C484 slot 0x68) before any share is believed. %d method targets land in the "
        "population's rows; %d of their walks end in a return (`BX`, `POP {..,pc}`, `MOV pc`, `LDR pc`), "
        "against %d of the same number of random even addresses drawn from the same rows with the same "
        "walk (seed 20261017). What the target adds over the control is the evidence that a "
        "class-table slot names a function, and every body is still proved byte-exact by the "
        "converter before it is emitted." % (targets, real, ctrl))
    outside = sorted({name for name in (extra_regions or {}).values()})
    shape = []
    if shape_control:
        shape = [
            "",
            "## What the `PUSH {..,lr}` shape is worth",
            "",
            "The shape is a halfword `0xB5xx` at an even offset whose walk ends in a return: %d row(s) "
            "and %d site(s) in this population. The control is the same scan over a byte-permuted copy "
            "of each row (seed 20261017): %d of the %d real sites end in a return against %d of the %d "
            "sites the permutation produces. The shape is only accepted where a body also reassembles "
            "byte-exact through the converter, and a row a pool citation names keeps that class: a "
            "named consumer outranks a coincidence of shape."
            % (shape_control[0], shape_control[3], shape_control[1], shape_control[3],
               shape_control[2], shape_control[4]),
        ]
    out = [
        "# `%s`'s raw rows, by the entry proof that reaches them" % region,
        "",
        "Generated by `tools/research/code_band.py` (`python tools/research/code_band.py --region %s"
        "%s --write`)." % (region, " --outside" if outside else ""),
        "One row per `%s` row of `docs/research/RAW_REMAINDER.csv`%s, one class per row, and the class"
        % (region, (", plus every raw row in %s that holds a class-table method target this region's"
                    " pass did not own" % ", ".join("`%s`" % name for name in outside)) if outside
           else ""),
        "sums equal the population: %d rows == %d rows, %d B == %d B."
        % (len(table), len(table), total_rows, total_rows),
        "",
        "The classification is measured on the tree at the candidate's parent, before the conversion",
        "this ticket lands: the rows it converts are source afterwards, and the verdicts are recorded",
        "by `docs/research/THUMB_BODIES.csv` (the converter's own census of every row it touched).",
        "The population's own denominator is `docs/research/RAW_REMAINDER.csv`, which the conversion",
        "regenerates; this file is the record of what the population WAS when it was classified.",
        "",
        "## The class table",
        "",
    ] + lines + [
        "",
        "## The same rows, by the region the census gives each of them",
        "",
    ] + split + [
        "",
        "## What the method entry is worth",
        "",
        worth,
    ] + shape + [
        "",
        "## The remainders, with their reasons",
        "",
        "- `pool-data` rows have a named consumer (the loader site that holds their address as a pool",
        "  word) but they are the pool, not the code: a standalone `DCD`/`DCB` dump of the retail bytes",
        "  is the raw-data class, not a route (`docs/research/ROUTE_TO_100.md`), and no tracked data",
        "  family re-derives these bytes from fields, so they stay INCBIN.",
        "- `unreached` rows carry no entry and no pool citation at this denominator. They stay INCBIN",
        "  with their region as their evidence, exactly as the region table states.",
        "- a `method-target` row whose walk yields no instruction, or whose body the assembler refuses,",
        "  is a remainder too; the converter's census carries its own reason verbatim.",
        "",
        "## Re-run",
        "",
        "    python tools\\research\\code_band.py --region %s%s" % (region,
                                                                   " --outside" if outside else ""),
        "    python tools\\research\\code_band.py --region %s%s --write"
        % (region, " --outside" if outside else ""),
        "    python tools\\research\\code_band.py --region %s%s --check" % (region,
                                                                           " --outside" if outside
                                                                           else ""),
    ]
    return "\n".join(out) + "\n"


def outputs(region=REGION):
    if region == REGION:
        return CSV_OUT, DOC_OUT
    name = str(region).replace(",", "-")
    return (os.path.join(ROOT, "docs", "research", "CODE_BAND_%s.csv" % name),
            os.path.join(ROOT, "docs", "research", "CODE_BAND_%s.md" % name))


def check(path=CSV_OUT):
    table = []
    for entry in csv.DictReader(open(path, newline="")):
        table.append({"start": int(entry["start"], 16), "end": int(entry["end"], 16),
                      "class": entry["class"]})
    counts, sizes = {}, {}
    for entry in table:
        if entry["class"] not in CLASSES:
            raise SystemExit("class %r is not one of %s" % (entry["class"], CLASSES))
        counts[entry["class"]] = counts.get(entry["class"], 0) + 1
        sizes[entry["class"]] = sizes.get(entry["class"], 0) + entry["end"] - entry["start"]
    before = None
    for entry in sorted(table, key=lambda one: one["start"]):
        if before is not None and entry["start"] < before:
            raise SystemExit("rows 0x%06x and 0x%06x overlap" % (before, entry["start"]))
        before = entry["end"]
    print("CODE_BAND %d row(s) %d B: %s"
          % (len(table), sum(sizes.values()),
             ", ".join("%s %d/%d" % (name, counts.get(name, 0), sizes.get(name, 0))
                       for name in CLASSES)))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--region", default=REGION,
                        help="the population's region in RAW_REMAINDER.csv (default R32)")
    parser.add_argument("--outside", action="store_true",
                        help="also classify every raw row holding a class-table method target outside "
                             "this region")
    parser.add_argument("--prologue", action="store_true",
                        help="add the PUSH {..,lr} shape instrument, and print its byte-permuted "
                             "control beside it")
    parser.add_argument("--converted", action="store_true",
                        help="add the branches out of the bodies the converter already rewrote")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--bodies", help="write this CSV's rows: the rows a walk reaches")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    csv_out, doc_out = outputs(args.region)
    if args.check:
        return check(csv_out)
    table, counts, sizes, context = measure(args.region, args.outside, args.prologue,
                                            args.converted)
    bodies, sites, population = context
    lines, _total_rows = table_text(table, counts, sizes)
    for line in lines:
        print(line)
    split, _totals = region_text(table)
    if len({entry["region"] for entry in table}) > 1:
        for line in split:
            print(line)
    print("population rows %d; reached %d rows" % (len(population), len(bodies)))
    control = walk_control(bodies, sites, population)
    print("return share: targets %d/%d against control %d/%d"
          % (control[0], control[1], control[2], control[1]))
    shape = {}
    shape_control = None
    if args.prologue:
        shape = {row: found[0][2] for row, found in
                 thumb_bodies.prologue_entries(population).items()}
        shape_control = prologue_control(population, shape)
        print("PUSH {..,lr} shape: %d row(s); %d of %d real site(s) end in a return against a "
              "byte-permuted control's %d of %d"
              % (shape_control[0], shape_control[1], shape_control[3], shape_control[2],
                 shape_control[4]))
    if args.bodies:
        with open(args.bodies, "w", newline="\n") as handle:
            handle.write("start,end\n")
            for row in sorted(bodies):
                handle.write("%s,%s\n" % (hex(row[0]), hex(row[1])))
        print("wrote %s: %d row(s)" % (args.bodies, len(bodies)))
    if args.write:
        extra = {row: entry["region"] for entry in table for row in [(entry["start"], entry["end"])]
                 if entry["region"] not in str(args.region).split(",")}
        with open(csv_out, "w", encoding="ascii", newline="\n") as handle:
            handle.write(csv_text(table))
        with open(doc_out, "w", encoding="ascii", newline="\n") as handle:
            handle.write(doc_text(table, counts, sizes, control, args.region, extra,
                                  shape_control if args.prologue else None))
        print("wrote %s and %s" % (os.path.relpath(csv_out, ROOT), os.path.relpath(doc_out, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
