from __future__ import annotations

import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools", "symbols"))

import gate  # noqa: E402
import generate_symbols  # noqa: E402

LEDGER = os.path.join(ROOT, "work", "ledger.csv")
CENSUS = os.path.join(ROOT, "docs", "research", "TRANSCRIBED_DATA_RUNS.csv")
ROM_BASE = 0x08000000


def census_runs(path=CENSUS):
    if not os.path.exists(path):
        return []
    return [(int(row["rom_start"], 16), int(row["rom_end"], 16))
            for row in csv.DictReader(open(path, newline=""))]


def data_bytes(runs, low, high):
    return sum(min(stop, high) - max(start, low) for start, stop in runs if start < high and low < stop)


def overlaps(low, high, slices):
    return [span for span in slices if span[0] < high and low < span[0] + span[1]]


def pieces_of(low, high, slices):
    edges = {low, high}
    for start, length in slices:
        if low < start < high:
            edges.add(start)
        if low < start + length < high:
            edges.add(start + length)
    ordered = sorted(edges)
    out = []
    for start, stop in zip(ordered, ordered[1:]):
        hit = next((span for span in slices if span[0] == start and span[0] + span[1] == stop), None)
        out.append((start, stop, hit))
    return out


def split(rows, slices, runs, states, apply_changes=False):
    out = []
    changed = dropped_total = 0
    insn_before = insn_after = 0
    for off, length, isa, region, source, kind, evidence, insn in rows:
        insn_before += insn
        hits = overlaps(off, off + length, slices)
        if not hits:
            out.append((off, length, isa, region, source, kind, evidence, insn))
            insn_after += insn
            continue
        changed += 1
        pieces = []
        dropped = 0
        for index, (start, stop, span) in enumerate(pieces_of(off, off + length, slices)):
            if span is not None:
                dropped += stop - start
                continue
            name = region if index == 0 else "%s_%06X" % (region, start)
            state = generate_symbols.state_at(states, start + ROM_BASE)
            pieces.append([start, stop, name,
                           (stop - start) - data_bytes(runs, start, stop), state])
        if not pieces:
            dropped_total += length
            continue
        for start, stop, name, count, state in pieces:
            out.append((start, stop - start, generate_symbols.STATE_KIND[state], name, source, kind,
                        evidence, count))
            insn_after += count
        dropped_total += dropped
    return out, changed, dropped_total, insn_before, insn_after


def read():
    return gate.ledger_rows()


def write(rows):
    gate.write_ledger(rows)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    slices = gate.incbin_ranges()
    runs = census_runs()
    rows = read()
    states = generate_symbols.read_map(os.path.join(ROOT, "build", "buu.map"))[1]
    out, changed, dropped, before, after = split(rows, slices, runs, states, args.apply)
    data_before = sum(length - insn for _, length, _, _, _, _, _, insn in rows)
    data_after = sum(length - insn for _, length, _, _, _, _, _, insn in out)
    print("rows %d -> %d; split %d row(s); dropped %d promoted byte(s); instruction bytes %d -> %d; "
          "data bytes %d -> %d"
          % (len(rows), len(out), changed, dropped, before, after, data_before, data_after))
    if before != after:
        print("the ledger's instruction figure moves by %d B: the bytes it counted as instructions "
              "while the census counted data runs (ARM code spelled as DCW) left with the promoted "
              "ranges" % (after - before))
    bad = [row for row in out if overlaps(row[0], row[0] + row[1], slices)]
    print("pieces overlapping a slice: %d" % len(bad))
    if bad:
        raise SystemExit("a piece still overlaps a slice: %s" % bad[:3])
    if args.apply:
        write(out)
        print("wrote %s" % LEDGER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
