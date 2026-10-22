"""Promote a uniform fill run inside an INCBIN slice to the assembler's own fill directive.

PATH-100-001 item 1 did this for the 292,440-byte tail at 0x7B89A8 (`asm/rest_of_the_game.s`, the
`GBLA`/`SETA`/`WHILE`/`DCB`/`WEND` block) under the ASSET-002 rule: a SELF-DELIMITING format may be
promoted by a real parse without a consumer citation, because its own bytes state its extent. A
uniform run's extent is exactly that - every byte inside the run equals every other, so the run
cannot be lengthened or shortened without the bytes differing.

What this does:
  - `plan` finds every run of one repeated byte at least `MIN_FILL` long inside the image spans,
    merging spans that touch so a fill cut only by a slice boundary is one run;
  - `block` renders the run as a labeled `SPACE` - the assembler's own zero fill - with the measured
    uniformity in its comment, so a line-based source reader and the assembler agree on its bytes
    (P-471; the `WHILE` block this replaces reads as one byte to `tools/emitted.py`);
  - `splice` replaces the covering `INCBIN baserom.gba_<start>_<end>.extracted` line with the
    retail gaps the run does not cover plus one `INCLUDE fill_<start>.s`, refusing unless the
    pieces tile the slice exactly;
  - `apply` writes one `asm/fill_<start>.s` per run, splices the source and adds one
    `call tools\\incbin.bat` line per new retail gap so a fresh worktree regenerates them.

The round trip that matters is the gate: the split slice's retail gaps plus the fill blocks must
rebuild to the same digest. `verify` is the cheap version of it, run before anything is written.
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.research import bios_block_scan as B  # noqa: E402

MIN_FILL = 256
ROM_BASE = 0x08000000
TOKEN = re.compile(r"^(\s*)INCBIN\s+(\S+)\s*$")
SLICE = re.compile(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted$")
LABEL = re.compile(r"\|unk_([0-9A-Fa-f]{8})\|")
FILL = re.compile(r"SPACE\s+(\d+)$")


class FillError(ValueError):
    pass


def plan(image, spans, minimum=MIN_FILL):
    return B.fill_runs(image, B.merge(spans), minimum)


def block(run, label=True):
    if run["value"] != 0:
        raise FillError("a run of 0x%02X cannot be carried by SPACE, which writes zeroes"
                        % run["value"])
    head = ("; 0x%X..0x%X is uniform padding (0 of %d bytes differ, value 0x%02X), so it is a fill "
            "and not data\n") % (run["start"], run["start"] + run["length"], run["length"],
                                 run["value"])
    if not label:
        return head + "\t\tSPACE\t%d\n" % run["length"]
    return head + "%s\n" % name_of(run["start"]) + "\t\tSPACE\t%d\n" % run["length"]


def name_of(start):
    return "|unk_%08X|" % (ROM_BASE + start)


def has_symbol(text, start):
    return name_of(start) in text or ("unk_%08X" % (ROM_BASE + start)) in text


def read_back(text):
    statements = [line.split(";")[0].strip() for line in text.splitlines()]
    statements = [body for body in statements if body]
    if len(statements) == 2:
        if LABEL.fullmatch(statements[0]) is None:
            raise ValueError("not a fill block: %r" % (statements,))
        statements = statements[1:]
    if len(statements) != 1:
        raise ValueError("a fill block is one SPACE with at most one label, got %d"
                         % len(statements))
    found = FILL.search(statements[0])
    if found is None:
        raise ValueError("not a fill block: %r" % (statements,))
    return bytes(int(found.group(1)))


def verify(image, run):
    start, length, value = run["start"], run["length"], run["value"]
    if start < 0 or start + length > len(image):
        raise FillError("run 0x%X..0x%X is outside the image" % (start, start + length))
    retail = image[start:start + length]
    if retail != bytes([value]) * length:
        raise FillError("run 0x%X is not uniform: %d of %d bytes differ from 0x%02X"
                        % (start, sum(1 for b in retail if b != value), length, value))
    if read_back(block(run)) != retail:
        raise FillError("the emitted block does not reproduce 0x%X" % start)


def gap_name(start, end):
    return B.gap_name(start, end)


def splice(text, span, runs):
    start, end = span
    ordered = sorted(runs, key=lambda r: r["start"])
    pieces = []
    cursor = start
    for run in ordered:
        if run["start"] < cursor or run["start"] + run["length"] > end:
            raise FillError("run 0x%X..0x%X is not inside 0x%X..0x%X in order"
                            % (run["start"], run["start"] + run["length"], start, end))
        if run["start"] > cursor:
            pieces.append((cursor, run["start"], "INCBIN  %s" % B.gap_name(cursor, run["start"])))
        pieces.append((run["start"], run["start"] + run["length"],
                       "INCLUDE fill_%x.s" % run["start"]))
        cursor = run["start"] + run["length"]
    if cursor < end:
        pieces.append((cursor, end, "INCBIN  %s" % B.gap_name(cursor, end)))
    try:
        return B.replace_slice(text, span, pieces)
    except ValueError as refusal:
        raise FillError(str(refusal)) from refusal


def cover(image, spans, minimum=MIN_FILL):
    slices = B.merge(spans)
    runs = plan(image, spans, minimum)
    out = []
    for run in runs:
        cover_slice = next(((a, b) for a, b in slices
                            if a <= run["start"] and run["start"] + run["length"] <= b), None)
        if cover_slice is None:
            raise FillError("no slice covers the run at 0x%X" % run["start"])
        out.append((cover_slice, run))
    return sorted(out, key=lambda pair: -pair[1]["length"])


def carrier_for(texts, cover_slice):
    try:
        return B.carrier_of(texts, cover_slice), True
    except ValueError as refusal:
        token = "INCLUDE fill_%x.s" % cover_slice[0]
        found = [path for path, text in texts.items()
                 if re.search(r"^\s*%s\s*$" % re.escape(token), text, re.M)]
        if len(found) == 1:
            return found[0], False
        raise FillError(str(refusal)) from refusal


def apply(image_path, asm_dir, rebuild_path, minimum=MIN_FILL, spans=None):
    image = open(image_path, "rb").read()
    spans = spans if spans is not None else B.incbin_spans()
    pairs = cover(image, spans, minimum)
    written = []
    texts = B.slice_carriers(asm_dir)
    by_slice = {}
    for cover_slice, run in pairs:
        verify(image, run)
        by_slice.setdefault(cover_slice, []).append(run)
    touched = {}
    for cover_slice, runs in sorted(by_slice.items()):
        path, fresh = carrier_for(texts, cover_slice)
        for run in runs:
            fill_path = os.path.join(asm_dir, "fill_%x.s" % run["start"])
            with open(fill_path, "w", newline="") as fh:
                fh.write(block(run, label=not has_symbol(texts[path], run["start"])))
            written.append(fill_path)
        if fresh:
            touched[path] = splice(texts[path], cover_slice, runs)
    for path, text in touched.items():
        with open(path, "w", newline="") as fh:
            fh.write(text)
    if rebuild_path:
        rebuild = open(rebuild_path, newline="").read()
        lines = rebuild.split("\n")
        last = max(i for i, line in enumerate(lines) if "incbin.bat" in line)
        added = []
        for cover_slice, runs in sorted(by_slice.items()):
            cursor = cover_slice[0]
            for run in sorted(runs, key=lambda r: r["start"]):
                if run["start"] > cursor:
                    added.append("call tools\\incbin.bat baserom.gba 0x%x 0x%x"
                                 % (cursor, run["start"]))
                cursor = run["start"] + run["length"]
            if cursor < cover_slice[1]:
                added.append("call tools\\incbin.bat baserom.gba 0x%x 0x%x" % (cursor, cover_slice[1]))
        retired = {"call tools\\incbin.bat baserom.gba 0x%x 0x%x" % span for span in by_slice}
        kept = [line for line in lines if line.strip() not in retired]
        last = max(i for i, line in enumerate(kept) if "incbin.bat" in line)
        kept[last + 1:last + 1] = added
        with open(rebuild_path, "w", newline="") as fh:
            fh.write("\n".join(kept))
    return pairs, written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--asm-dir", default=os.path.join(ROOT, "asm"))
    parser.add_argument("--rebuild", default=os.path.join(ROOT, "rebuild.cmd"))
    parser.add_argument("--minimum", type=int, default=MIN_FILL)
    parser.add_argument("--slice", nargs=2, action="append", metavar=("START", "END"),
                        type=lambda text: int(text, 16),
                        help="restrict the sweep to this slice; repeatable")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    image = open(args.image, "rb").read()
    spans = [tuple(sorted(pair)) for pair in args.slice] if args.slice else B.incbin_spans()
    pairs = cover(image, spans, args.minimum)
    for cover_slice, run in pairs:
        verify(image, run)
        print("fill 0x%06X..0x%06X %6d B value=0x%02X  in slice 0x%06X..0x%06X"
              % (run["start"], run["start"] + run["length"], run["length"], run["value"],
                 cover_slice[0], cover_slice[1]))
    print("fills=%d bytes=%d" % (len(pairs), sum(r["length"] for _s, r in pairs)))
    if args.apply:
        _pairs, written = apply(args.image, args.asm_dir, args.rebuild, args.minimum, spans)
        print("wrote %s" % ", ".join(os.path.relpath(p, ROOT) for p in written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
