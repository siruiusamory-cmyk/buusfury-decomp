"""Attribute the differing byte runs between two images to the ledger rows that cover them.

  python tools\\match\\compare_rows.py <a.gba> <b.gba> [--ledger work\\ledger.csv]

The gate compares whole images, so a per-function compare needs attribution: this reads the two
images, finds every run of differing bytes, and prints, per run, the ledger row whose span holds it
and the rows that are clean. A row whose span holds no run is matched; a run outside every row is
printed as unattributed. Exit 0 when every run is inside a row and every row is clean, 1 otherwise,
so a caller can use it as a check.

  python tools\\match\\compare_rows.py baserom.gba build\\output\\ROM_START
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import gate


def differing_runs(a, b, limit=0):
    runs = []
    i, n = 0, min(len(a), len(b))
    while i < n:
        if a[i] != b[i]:
            j = i
            while j < n and a[j] != b[j]:
                j += 1
            runs.append((i, j - i, a[i:j], b[i:j]))
            i = j
        else:
            i += 1
    if limit:
        return runs[:limit]
    return runs


def rows_of(path):
    previous = gate.LEDGER
    gate.LEDGER = path
    try:
        return gate.ledger_rows()
    finally:
        gate.LEDGER = previous


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    ledger = gate.LEDGER
    if "--ledger" in sys.argv:
        ledger = sys.argv[sys.argv.index("--ledger") + 1]
        argv = [a for a in argv if a != ledger]
    if len(argv) != 2:
        print(__doc__.strip())
        return 1
    first, second = open(argv[0], "rb").read(), open(argv[1], "rb").read()
    if len(first) != len(second):
        print("SIZE MISMATCH %d vs %d" % (len(first), len(second)))
        return 1
    runs = differing_runs(first, second)
    print("differing bytes=%d in %d run(s)" % (sum(r[1] for r in runs), len(runs)))
    rows = rows_of(ledger)
    print("ledger rows: %d  (%s)" % (len(rows), ledger))
    mismatched, unattributed = [], []
    for off, length, av, bv in runs:
        inside = [r for r in rows if r[0] <= off < r[0] + r[1]]
        if not inside:
            unattributed.append((off, length))
            print("  +0x%06x  %3d B  NOT IN ANY ROW   A=%s  B=%s"
                  % (off, length, av[:16].hex(" "), bv[:16].hex(" ")))
            continue
        row = inside[0]
        mismatched.append(row[3])
        print("  +0x%06x  %3d B  row %-40s (0x%06x..0x%06x)  A=%s  B=%s"
              % (off, length, row[3], row[0], row[0] + row[1], av[:16].hex(" "), bv[:16].hex(" ")))
    print("rows with a differing run: %s" % (", ".join(sorted(set(mismatched))) or "none"))
    print("MATCH" if not runs else "MISMATCH")
    return 0 if not runs else 1


if __name__ == "__main__":
    sys.exit(main())
