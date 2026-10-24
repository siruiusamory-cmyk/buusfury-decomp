"""Carry the census's promoted runs as LABELED RAW DATA whose bytes come from the retail image.

R-RAW-001 promotes a run that has a cited consumer but no code-derived extent. The bytes are raw
data and no structure is claimed, so the promotion is only honest if the source says which consumer
cites which address and carries the bytes unchanged. PATH-100-015 changes HOW the bytes are carried:

- a fragment is still one INCLUDEd file per run, still split at every cited base into
  `unk_<ROMADDR>` symbols with their citation comments, strides and shapes;
- each symbol's bytes are now ONE `INCBIN` of a build-time extracted slice of baserom.gba -
  `baserom.gba_0x<start>_0x<end>.extracted`, the same mechanism the tree's other retail spans use -
  instead of tracked `DCB`/`DCW`/`DCD` text. No retail byte payload is tracked any more, and
  `gate.incbin_ranges()` counts every one of those bytes as raw data.

`--extract` is the writer of every slice a fragment names (P-436: a name the source mentions needs a
writer, and `tools/extract.cmd` is where a fresh tree gets its retail-derived inputs). It runs before
the gate's cold purge, so `--cold` regenerates them like every other extracted input.

    python tools/build/rawlabeled.py --extract

The loader channel is T-146's sweep, so a site whose own address lies inside the run is data and not
a citation (P-420).
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "research"))

import emitted  # noqa: E402

ROM_BASE = 0x08000000
Run = namedtuple("Run", "file start end shape")
RUNS = (
    Run("raw_labeled_74d248.s", 0x74D248, 0x74F058,
        "container-rich run 0x74D248..0x74F058; the pointers are named, the family layout is NOT"
        " ESTABLISHED"),
    Run("raw_labeled_7b5b64.s", 0x7B5B64, 0x7B79A4,
        "dialogue container table 0x7B5B64 and the heterogeneous run it heads; the family layout is"
        " NOT ESTABLISHED"),
)
_SITES = None


def named_slices(root: str = ROOT) -> dict[tuple[int, int], str]:
    out: dict[tuple[int, int], str] = {}
    directory = os.path.join(root, "asm")
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".s"):
            continue
        text = open(os.path.join(directory, name), errors="replace").read()
        for token in emitted.incbin_tokens(text):
            found = emitted.SLICE.search(token.replace("\\", "/"))
            if found:
                out[(int(found.group(1), 16), int(found.group(2), 16))] = token
    return out


def extract(rom: bytes, root: str = ROOT) -> int:
    written = 0
    total = 0
    for (start, end), token in sorted(named_slices(root).items()):
        if not 0 <= start < end <= len(rom):
            raise SystemExit("%s names %#x..%#x, outside the %d-byte image"
                             % (token, start, end, len(rom)))
        path = os.path.join(root, token)
        blob = rom[start:end]
        if os.path.exists(path) and open(path, "rb").read() == blob:
            total += len(blob)
            continue
        with open(path, "wb") as handle:
            handle.write(blob)
        written += 1
        total += len(blob)
    print("slices named=%d written=%d bytes=%d" % (len(named_slices(root)), written, total))
    return 0


def sites(rom: bytes):
    global _SITES
    if _SITES is None:
        import code_xref
        _SITES = code_xref.scan(rom)
    return _SITES


def cited(rom: bytes, start: int, end: int) -> dict[int, list]:
    import code_xref
    out = {}
    for kind, site, _, value in code_xref.loads_into(rom, sites(rom), ROM_BASE + start,
                                                     ROM_BASE + end):
        out.setdefault(value - ROM_BASE, []).append((kind, site))
    for rows in out.values():
        rows.sort(key=lambda row: row[1])
    return out


def citation_split(rom: bytes, run) -> list[tuple[int, int, list]]:
    rows = cited(rom, run.start, run.end)
    if rows and min(rows) > run.start:
        rows[run.start] = []
    starts = sorted(rows)
    if not starts or starts[0] != run.start:
        raise SystemExit("%#x..%#x: no symbol at the region's own start" % (run.start, run.end))
    ends = starts[1:] + [run.end]
    return [(address, end, rows[address]) for address, end in zip(starts, ends)]


def citation_rows(rom: bytes) -> list[tuple[str, int, int, int]]:
    out = []
    for run in RUNS:
        split = citation_split(rom, run)
        out.append(("0x%06X..0x%06X" % (run.start, run.end), run.end - run.start, len(split),
                    sum(len(rows) for _, _, rows in split)))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", default="baserom.gba")
    parser.add_argument("--extract", action="store_true",
                        help="write every slice the tracked fragments name, from baserom.gba")
    args = parser.parse_args(argv)
    if not args.extract:
        parser.error("give --extract")
    rom = open(args.rom, "rb").read()
    return extract(rom)


if __name__ == "__main__":
    sys.exit(main())
