from __future__ import annotations

import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ROW = re.compile(r"^\{0x([0-9a-f]{8})u,g_")
REGIONS = ("rom", "iwram")


def blocks(folder):
    keys = set()
    for path in sorted(glob.glob(os.path.join(folder, "*.c"))):
        with open(path, encoding="ascii", errors="replace") as handle:
            for line in handle:
                found = ROW.match(line)
                if found:
                    keys.add(int(found.group(1), 16))
    return keys


def recorded(path):
    out = []
    for line in open(path, encoding="ascii"):
        part = line.split()
        if len(part) == 3 and part[0] in REGIONS and part[2] in ("a", "t"):
            out.append((int(part[1], 16), "thumb" if part[2] == "t" else "arm", part[0]))
    return out


def uncovered(keys, points):
    return [(addr, mode, region) for addr, mode, region in points
            if (addr | (1 if mode == "thumb" else 0)) not in keys]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Which recorded entry points an emitted block table does not reach.")
    parser.add_argument("--chunks", required=True,
                        help="the directory of emitted C chunks that carries the block tables")
    parser.add_argument("--labels", required=True,
                        help="a recorded label file in the recorder's line format")
    parser.add_argument("--write", help="write the uncovered points to this CSV")
    arguments = parser.parse_args(argv)
    keys = blocks(arguments.chunks)
    points = recorded(arguments.labels)
    if not keys:
        raise SystemExit("%s carries no block table" % arguments.chunks)
    if not points:
        raise SystemExit("%s records no entry point" % arguments.labels)
    missed = uncovered(keys, points)
    print("blocks %d recorded %d covered %d uncovered %d"
          % (len(keys), len(points), len(points) - len(missed), len(missed)))
    for region in REGIONS:
        total = sum(1 for _addr, _mode, one in points if one == region)
        hit = sum(1 for _addr, _mode, one in missed if one == region)
        print("%s %d of %d" % (region, total - hit, total))
    if arguments.write:
        with open(arguments.write, "w", newline="", encoding="ascii") as handle:
            handle.write("address,mode,region\n")
            for addr, mode, region in missed:
                handle.write("%08x,%s,%s\n" % (addr, mode, region))
        print("wrote %s" % arguments.write)
    return 0


if __name__ == "__main__":
    sys.exit(main())
