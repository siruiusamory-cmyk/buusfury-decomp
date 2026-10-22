"""Splice the sprite family's emitted sections into asm/rest_of_the_game.s (SPRITE-FULL-001).

The emitter writes one `INCBIN  <path>` line per planned section. This tool parses those line
lists, verifies that the tokens they name tile the same byte span as the current tokens of the
affected blocks, and rewrites only that span. A non-token line inside the span - the label that
names its own address - is carried through at that address. The untouched prefix and suffix bytes
are compared and the tool refuses when they differ.

  python tools/spritecontainer/splice_source.py --check
  python tools/spritecontainer/splice_source.py --apply
"""
from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SOURCE = os.path.join(ROOT, "asm", "rest_of_the_game.s")
TOKEN = re.compile(r"^(\s*)INCBIN\s+(\S+)\s*$")
INCLUDE = re.compile(r"^\s*INCLUDE\s+(\S+)\s*$")
SLICE = re.compile(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted$")
RUN = re.compile(r"_([0-9a-fA-F]{1,8})_([0-9a-fA-F]{1,8})\.bin$")


def token_span(token):
    for pattern in (SLICE, RUN):
        found = pattern.search(token)
        if found:
            return int(found.group(1), 16), int(found.group(2), 16)
    return None


def spans(tokens):
    out = []
    for token in tokens:
        span = token_span(token)
        if span is None:
            raise SystemExit("%s carries no byte range" % token)
        out.append(span)
    return out


def emitted(path):
    if not os.path.exists(path):
        raise SystemExit("%s is missing: run the block's build first" % path)
    return [match.group(2) for match in
            (TOKEN.match(line.rstrip("\r\n")) for line in open(path, errors="replace"))
            if match]


def contiguous_rows(rows):
    for (start, end), (next_start, next_end) in zip(rows, rows[1:]):
        if end != next_start:
            raise SystemExit("tokens do not tile: %#x then %#x" % (end, next_start))
    return rows


def contiguous(tokens):
    return contiguous_rows(spans(tokens))


def included_rows(name):
    path = os.path.join(ROOT, "asm", name)
    if not os.path.exists(path):
        raise SystemExit("%s is included by the span and is missing" % path)
    return spans(emitted(path))


def old_spans(lines, first, last):
    rows = []
    for index in range(first, last + 1):
        match = TOKEN.match(lines[index])
        if match:
            span = token_span(match.group(2))
            if span is None:
                raise SystemExit("%s carries no byte range" % match.group(2))
            rows.append(span)
            continue
        include = INCLUDE.match(lines[index])
        if include:
            rows += included_rows(include.group(1))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--emitted", action="append", required=True,
                        help="an emitter's output directory (its incbin.txt), repeat in span order")
    args = parser.parse_args()

    lists = [emitted(os.path.join(ROOT, path, "incbin.txt")) for path in args.emitted]
    new_rows = []
    for tokens in lists:
        new_rows += contiguous(tokens)
    for (start, end), (next_start, next_end) in zip(new_rows, new_rows[1:]):
        if end != next_start:
            raise SystemExit("the lists do not meet at %#x..%#x and %#x..%#x"
                             % (start, end, next_start, next_end))
    tokens = [token for group in lists for token in group]
    span_start, span_end = new_rows[0][0], new_rows[-1][1]

    original = open(SOURCE, errors="replace").read()
    lines = original.split("\n")
    positions = [(index, match.group(2)) for index, match in
                 ((index, TOKEN.match(line)) for index, line in enumerate(lines)) if match]
    inside = [(index, token) for index, token in positions
              if token_span(token) and span_start <= token_span(token)[0]
              and token_span(token)[1] <= span_end]
    if not inside:
        raise SystemExit("no current token lies inside %#x..%#x" % (span_start, span_end))
    first, last = inside[0][0], inside[-1][0]
    old_rows = contiguous_rows(old_spans(lines, first, last))
    if (old_rows[0][0], old_rows[-1][1]) != (span_start, span_end):
        raise SystemExit("the current tokens span %#x..%#x, the new ones %#x..%#x"
                         % (old_rows[0][0], old_rows[-1][1], span_start, span_end))
    carried = []
    cursor = old_rows[0][0]
    for index in range(first, last + 1):
        match = TOKEN.match(lines[index])
        if match:
            cursor = token_span(match.group(2))[1]
            continue
        include = INCLUDE.match(lines[index])
        if include:
            rows = included_rows(include.group(1))
            cursor = rows[-1][1] if rows else cursor
            continue
        carried.append((cursor, index, lines[index]))

    indent = lines[first][:len(lines[first]) - len(lines[first].lstrip())]
    replacement = []
    pending = list(carried)
    for token, (start, end) in zip(tokens, new_rows):
        while pending and pending[0][0] <= start:
            address, index, text = pending.pop(0)
            if address != start:
                raise SystemExit("line %d at %#x lands inside the token %#x..%#x"
                                 % (index + 1, address, start, end))
            replacement.append(text)
        replacement.append("%sINCBIN  %s" % (indent, token.replace("/", "\\")))
    if pending:
        raise SystemExit("line %d at %#x is past the last token"
                         % (pending[0][1] + 1, pending[0][0]))
    kept = lines[:first] + replacement + lines[last + 1:]
    if kept[:first] != lines[:first] or kept[first + len(replacement):] != lines[last + 1:]:
        raise SystemExit("the splice would move bytes outside the span")
    print("span %#x..%#x (%d bytes)" % (span_start, span_end, span_end - span_start))
    print("old tokens %d (%d retail, %d carried line(s)) -> new tokens %d from %d list(s): %s"
          % (len(inside), sum(1 for _, t in inside if t.startswith("baserom.gba_")),
             len(carried), len(replacement), len(lists),
             ", ".join("%s %d" % (path, len(group))
                       for path, group in zip(args.emitted, lists))))
    at = 0
    for path, group in zip(args.emitted, lists):
        rows = new_rows[at:at + len(group)]
        print("  %-28s new %#x..%#x %d token(s)" % (path, rows[0][0], rows[-1][1], len(rows)))
        at += len(group)
    text = "\n".join(kept)
    if args.check or not args.apply:
        print("CHECK ONLY: no file written (pass --apply)")
        return 0
    with open(SOURCE, "w", encoding="ascii", newline="") as handle:
        handle.write(text)
    print("wrote %s" % SOURCE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
