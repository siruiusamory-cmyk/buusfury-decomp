"""The two asset-directory block runs as a census: 143 entries, their kinds, and what the payload is.

Directory 1 (`assetdir`, 64 records) and directory 2 (`assetdir2`, 79 records) each state a 12-byte
record; `assetdirectory` owns the field map and each instance owns its fingerprints. This module is
the third reader: it walks the entries the two directories tile, counts the bytes per kind, and
measures the payload's structure against a null, so that "a container", "a table" and "a sample
stream" are decided by a measurement rather than by a reading. No byte is printed.

The kinds are the bytes' own: the record's `flags` word is reported as its measured two halves (the
low 16 bits take three values, 0/1/3, and the high 16 bits are zero in 90 records and 1..7,431 in
53, always below `byte_length`), because nothing measured here establishes a name for either half.

    python tools\\mapcontainer\\assetdir_samples.py --rom baserom.gba [--csv OUT.csv]
"""

from __future__ import annotations

import argparse
import collections
import csv
import math
import random
import struct
import sys

import assetdir
import assetdir2

DIRECTORIES = (assetdir, assetdir2)
STRIDES = (2, 4, 8, 16, 32)
SEED = 20261018
COHERENT = 0.05


def entries(rom):
    out = []
    for module in DIRECTORIES:
        module.assert_contract(rom)
        for index, (at, size) in enumerate(module.directory_rows(rom)):
            fields = module.fields(rom, at, size)
            out.append({"directory": module.DIRECTORY, "index": index,
                        "offset": fields["data_ptr"] - module.ROM_BASE,
                        "length": fields["byte_length"], "unit": fields["unit"],
                        "flags": fields["flags"]})
    return out


def kind(flags):
    return "flags=%d" % (flags & 0xFFFF), "aux=0" if not flags >> 16 else "aux=set"


def totals(rows, expected):
    total = sum(row["length"] for row in rows)
    if total != expected:
        raise ValueError("the entries total %d B, the contract says %d" % (total, expected))
    return total


def signed(blob):
    return [value - 256 if value >= 128 else value for value in blob]


def correlation(samples, lag=1):
    count = len(samples)
    if lag != 1 and count <= lag + 2:
        return None
    if count < 3:
        return 0.0
    left, right = samples[:-lag], samples[lag:]
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    numerator = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right))
    denominator = math.sqrt(sum((a - mean_left) ** 2 for a in left) *
                            sum((b - mean_right) ** 2 for b in right))
    return numerator / denominator if denominator else 0.0


def loop_test(rom, rows, draws=20, seed=SEED):
    rng = random.Random(seed)
    stored, offsets, at_lag, at_random = [], [], [], []
    tails = constant = 0
    for row in rows:
        blob = rom[row["offset"]:row["offset"] + row["length"]]
        if len(blob) >= 96 and blob[:-32].find(blob[-32:]) >= 0:
            tails += 1
            constant += 1 if len(set(blob[-32:])) == 1 else 0
        aux = row["flags"] >> 16
        if not 0 < aux < len(blob):
            continue
        samples = signed(blob)
        stored.append(abs(samples[aux - 1] - samples[aux]))
        for _ in range(draws):
            k = rng.randrange(1, len(samples))
            offsets.append(abs(samples[k - 1] - samples[k]))
        at_lag.append(correlation(samples, aux))
        for _ in range(draws):
            value = correlation(samples, rng.randrange(2, len(samples) - 8))
            if value is not None:
                at_random.append(value)
    return {"stored": sum(stored) / len(stored), "random": sum(offsets) / len(offsets),
            "tails": tails, "constant_tails": constant,
            "lag": sum(at_lag) / len(at_lag), "random_lag": sum(at_random) / len(at_random)}


def coherence(rom, rows, draws=5, seed=SEED):
    rng = random.Random(seed)
    out = []
    for row in rows:
        blob = rom[row["offset"]:row["offset"] + row["length"]]
        real = correlation(signed(blob))
        nulls = []
        for _ in range(draws):
            permuted = list(blob)
            rng.shuffle(permuted)
            nulls.append(correlation(signed(permuted)))
        out.append(dict(row, real=real, null=sum(nulls) / len(nulls)))
    return out


def containers(blob):
    if len(blob) < 8:
        return {"webfoot": False, "jcalg1": False, "lz77-tag": False, "rle-tag": False}
    kind, declared = struct.unpack_from("<II", blob, 0)
    return {"webfoot": kind in (0, 1, 2) and 24 <= declared <= len(blob),
            "jcalg1": blob[:4] == b"JCAL",
            "lz77-tag": blob[0] == 0x10,
            "rle-tag": blob[0] == 0x30}


def histogram(rom, rows):
    counts = collections.Counter()
    runs = collections.Counter()
    run_bytes = collections.Counter()
    for row in rows:
        blob = rom[row["offset"]:row["offset"] + row["length"]]
        counts.update(blob)
        start = 0
        while start < len(blob):
            end = start + 1
            while end < len(blob) and blob[end] == blob[start]:
                end += 1
            if end - start >= 8:
                runs[blob[start]] += 1
                run_bytes[blob[start]] += end - start
            start = end
    total = sum(counts.values())
    asymmetry = sum(abs(counts[value] - counts[256 - value]) for value in range(1, 128))
    mode, mode_count = counts.most_common(1)[0]
    return {"total": total, "mode": mode, "mode_share": mode_count / total,
            "asymmetry": asymmetry / total, "runs": sum(runs.values()),
            "run_bytes": sum(run_bytes.values()),
            "zero_run_share": run_bytes.get(0, 0) / max(sum(run_bytes.values()), 1)}


def entropy(blob):
    counts = collections.Counter(blob)
    return -sum((count / len(blob)) * math.log2(count / len(blob)) for count in counts.values())


def constrained(rom, rows, strides=STRIDES):
    out = {}
    for stride in strides:
        fixed = 0
        for row in rows:
            blob = rom[row["offset"]:row["offset"] + row["length"]]
            for position in range(stride):
                column = blob[position::stride]
                if len(column) >= 8 and \
                        collections.Counter(column).most_common(1)[0][1] / len(column) > 0.95:
                    fixed += 1
        out[stride] = fixed
    return out


def report(rom, rows, draws=5, seed=SEED):
    total = totals(rows, sum(module.BLOCK_BYTES for module in DIRECTORIES))
    by_directory = collections.Counter(row["directory"] for row in rows)
    print("entries=%d bytes=%d %s" % (len(rows), total, dict(sorted(by_directory.items()))))
    kinds = collections.defaultdict(lambda: [0, 0])
    for row in rows:
        for column, name in enumerate(kind(row["flags"])):
            kinds[name][0] += 1
            kinds[name][1] += row["length"]
    for name in sorted(kinds):
        print("kind %-10s %3d entries %7d bytes" % (name, kinds[name][0], kinds[name][1]))
    tags = collections.Counter()
    for row in rows:
        for name, hit in containers(rom[row["offset"]:row["offset"] + row["length"]]).items():
            tags[name] += 1 if hit else 0
    print("containers at an entry's start %s" % dict(sorted(tags.items())))
    rows = coherence(rom, rows, draws, seed)
    off = [row for row in rows if abs(row["real"] - row["null"]) > COHERENT]
    positive = sum(1 for row in rows if row["real"] - row["null"] > COHERENT)
    print("coherence: mean lag-1 %.3f, mean own-shuffle null %.3f; %d of %d entries lie more than"
          " %.2f from their own null (%d above it, %d below)"
          % (sum(row["real"] for row in rows) / len(rows),
             sum(row["null"] for row in rows) / len(rows), len(off), len(rows), COHERENT,
             positive, len(off) - positive))
    stats = histogram(rom, rows)
    print("histogram: mode %#04x at %.4f, signed asymmetry %.4f, %d constant runs >=8 B (%d B,"
          " %.4f of the run bytes at 0x00)"
          % (stats["mode"], stats["mode_share"], stats["asymmetry"], stats["runs"],
             stats["run_bytes"], stats["zero_run_share"]))
    print("strides: constrained columns %s" % constrained(rom, rows))
    loop = loop_test(rom, rows, 20, seed)
    print("loop test: |delta| at the stored point %.2f against %.2f at a random offset; %d blocks"
          " repeat their last 32 B and %d of those tails are one constant value; autocorrelation at"
          " the stored lag %.3f against %.3f at random lags"
          % (loop["stored"], loop["random"], loop["tails"], loop["constant_tails"],
             loop["lag"], loop["random_lag"]))
    odd = sum(1 for row in rows if row["length"] % 2)
    print("odd block lengths: %d entries, so a 16-bit sample reading cannot tile them"
          % odd)
    return {"entries": len(rows), "bytes": total, "containers": dict(tags),
            "off_null": len(off), "histogram": stats, "loop": loop}


def write_csv(path, rom, rows, draws=5, seed=SEED):
    rows = coherence(rom, rows, draws, seed)
    with open(path, "w", newline="\n", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["directory", "index", "offset", "bytes", "unit", "flags", "low", "aux",
                         "lag1", "shuffle_null", "distinct", "entropy", "containers"])
        for row in rows:
            blob = rom[row["offset"]:row["offset"] + row["length"]]
            writer.writerow([row["directory"], row["index"], "0x%06x" % row["offset"],
                             row["length"], row["unit"], "0x%08x" % row["flags"],
                             row["flags"] & 0xFFFF, row["flags"] >> 16, "%.4f" % row["real"],
                             "%.4f" % row["null"], len(set(blob)), "%.4f" % entropy(blob),
                             ",".join(name for name, hit in containers(blob).items() if hit)])
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", default="baserom.gba")
    parser.add_argument("--csv")
    parser.add_argument("--draws", type=int, default=5)
    args = parser.parse_args(argv)
    rom = open(args.rom, "rb").read()
    rows = entries(rom)
    report(rom, rows, draws=args.draws)
    if args.csv:
        print("wrote %s" % write_csv(args.csv, rom, rows, draws=args.draws))
    return 0


if __name__ == "__main__":
    sys.exit(main())
