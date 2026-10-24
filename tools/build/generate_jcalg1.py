"""Promote the packed JCALG1 containers the INCBIN ranges still hold, through the tree's own
stored-payload route.

Why this is a promotion and not a labelling. A packed container states its own extent twice over:
its header declares the size of the body's output, and the body runs to its own end code, so the
block delimits itself and needs no consumer citation (the ASSET-002 rule, the same one PATH-100-001
item 1 used for a uniform fill run). What makes it a *promotion* is the re-encoder: this module
stores the DECODED payload, and at build time `tools\\compress\\compress.exe` turns that payload back
into the container, byte for byte, so the bytes in the image are produced by source rather than
carried by an `INCBIN`.

The route is the tile-bank generator's (see `tools/tilebank/generate_tilebank.py`): a payload store
under `assets\\jcalg1\\`, one `compress.exe` run per payload, one generated section file per
contiguous run of containers, and a spliced token list in `asm\\`.

  extract  read the generated runs' own container list out of the source, keep every container that
           re-encodes byte-exactly, store its decoded payload;
  build    re-encode every stored payload, refuse if a byte differs from the image, write one
           section file per run, and byte-check every section from disk;
  --sweep  promote containers the source does NOT name yet: walk the INCBIN slices the census classes
           with `--sweep-class`, keep the ones whose container re-encodes to the image's bytes, and
           splice `build\\jcalg1\\gen_<start>_<end>.bin` tokens plus the retail gaps around them;
  --apply  splice the source and extend `rebuild.cmd` with the new retail gaps.

A run's extent is the token's own name, never the bytes (P-473). A `gen_<start>.bin` token (the
PATH-100-011 shape) takes its end from the next token's own address; a `gen_<start>_<end>.bin` token
carries its end itself, which is the shape `tools/build/rawlabeled.py:gen_name` already uses for
the structured block's runs.
"""

import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import payload_store  # noqa: E402
import encode_cache  # noqa: E402
from tools.research import bios_block_scan as B  # noqa: E402
from tools.research import jcalg1  # noqa: E402

COMPRESS = os.path.join(ROOT, "tools", "compress", "compress.exe")
BLOCK = "jcalg1"
GEN = re.compile(r"build\\%s\\gen_([0-9a-f]+)(?:_([0-9a-f]+))?\.bin$" % BLOCK, re.IGNORECASE)
SECTION = "build\\%s\\" % BLOCK
GAP = re.compile(r"baserom\.gba_0x([0-9a-f]+)_0x([0-9a-f]+)\.extracted$")
SUFFIX = re.compile(r"_([0-9a-fA-F]{2,8})(?:_[0-9a-fA-F]{4,8})?\.(?:bin|s)$")
CENSUS = ""


class PromoteError(ValueError):
    pass


def piece_start(token):
    found = GAP.search(token)
    if found:
        return int(found.group(1), 16)
    found = SUFFIX.search(token)
    return int(found.group(1), 16) if found else None


def tokens_of(text):
    rows = []
    for line in text.split("\n"):
        body = line.split(";")[0].strip()
        if body.startswith("INCBIN") or body.startswith("INCLUDE"):
            token = body.split(None, 1)[-1].strip()
            rows.append((token, piece_start(token)))
    return rows


def run_extents_in(text):
    rows = tokens_of(text)
    extents = []
    for position, (token, start) in enumerate(rows):
        found = GEN.search(token)
        if found is None:
            continue
        if found.group(2) is not None:
            end = int(found.group(2), 16)
            if end <= start:
                raise PromoteError("the generated run %s ends at 0x%X, not past its start 0x%X"
                                   % (token, end, start))
        else:
            if position + 1 == len(rows) or rows[position + 1][1] is None:
                raise PromoteError("the generated run %s is not followed by a token that names its "
                                   "end" % token)
            end = rows[position + 1][1]
        extents.append((start, end, os.path.basename(token)))
    named = [token for token, _start in rows if token.lower().startswith(SECTION.lower())]
    if len(named) != len(extents):
        raise PromoteError("%d token(s) name a %s section, %d resolved to a run: %s"
                           % (len(named), SECTION, len(extents),
                              ", ".join(token for token in named if GEN.search(token) is None)))
    return extents


def run_extents(texts):
    out = []
    for text in texts:
        out.extend(run_extents_in(text))
    return sorted(out)


def source_payloads(image, texts, compress):
    extents = run_extents(texts)
    if not extents:
        raise PromoteError("the source names no generated jcalg1 run, so there is nothing to extract")
    payloads = {}
    for start, end, name in extents:
        offset = start
        while offset < end:
            hit = B.jcalg1_container(image, offset, end, compress)
            if hit is None or not hit.get("byte_exact"):
                raise PromoteError("0x%X is not a byte-exact container of the run %s (0x%X..0x%X)"
                                   % (offset, name, start, end))
            got = jcalg1.decompress(image, offset + B.JCALG1_HEADER, offset + hit["compressed"])
            if got is None or len(got[0]) != hit["decompressed"]:
                raise PromoteError("0x%X stopped decoding after the oracle passed it" % offset)
            payloads[offset] = got[0]
            offset += hit["compressed"]
        if offset != end:
            raise PromoteError("the containers of %s end at 0x%X, the run ends at 0x%X"
                               % (name, offset, end))
    if not payloads:
        raise PromoteError("no container the source's runs name re-encodes to the image's bytes")
    return payloads


def encoded(image, payloads, compress, extents):
    runs = []
    for start, end, name in extents:
        offset, blob = start, bytearray()
        while offset < end:
            payload = payloads.get(offset)
            if payload is None:
                raise PromoteError("the run %s (0x%X..0x%X) has no stored payload at 0x%X"
                                   % (name, start, end, offset))
            stored = compress(payload)
            if stored is None:
                raise PromoteError("compress.exe refused the %d-byte payload at 0x%X"
                                   % (len(payload), offset))
            if stored != image[offset:offset + len(stored)]:
                raise PromoteError("the re-encoded container at 0x%X is not the image's bytes"
                                   % offset)
            blob += stored
            offset += len(stored)
        if offset != end:
            raise PromoteError("the payloads of %s end at 0x%X, the run ends at 0x%X"
                               % (name, offset, end))
        runs.append((start, end, name, bytes(blob)))
    return runs


def run_name(start, end):
    return "build\\%s\\gen_%x_%x.bin" % (BLOCK, start, end)


def emit(runs, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    written, skipped = [], 0
    for run_start, run_end, name, blob in runs:
        path = os.path.join(out_dir, name)
        if os.path.exists(path):
            with open(path, "rb") as handle:
                if handle.read() == blob:
                    skipped += 1
                    written.append((run_start, run_end, path))
                    continue
        with open(path, "wb") as handle:
            handle.write(blob)
        with open(path, "rb") as handle:
            if handle.read() != blob:
                raise PromoteError("%s does not hold 0x%X..0x%X" % (path, run_start, run_end))
        written.append((run_start, run_end, path))
    return written, skipped


def slices_of(runs, spans):
    slices = B.merge(spans)
    by_span = {}
    for run_start, run_end, _name, _blob in runs:
        covering = [s for s in slices if s[0] <= run_start and run_end <= s[1]]
        if len(covering) != 1:
            raise PromoteError("run 0x%X..0x%X is in %d slices, expected exactly one"
                               % (run_start, run_end, len(covering)))
        by_span.setdefault(covering[0], []).append((run_start, run_end))
    return by_span


def pieces(span, runs):
    start, end = span
    out = []
    cursor = start
    for run_start, run_end in sorted(runs):
        if run_start < cursor or run_end > end:
            raise PromoteError("run 0x%X..0x%X is not inside 0x%X..0x%X in order"
                               % (run_start, run_end, start, end))
        if run_start > cursor:
            out.append((cursor, run_start, "INCBIN  %s" % B.gap_name(cursor, run_start)))
        out.append((run_start, run_end, "INCBIN  %s" % run_name(run_start, run_end)))
        cursor = run_end
    if cursor < end:
        out.append((cursor, end, "INCBIN  %s" % B.gap_name(cursor, end)))
    return out


def carriers(asm_dir):
    return B.slice_carriers(asm_dir)


def carrier_of(texts, span):
    try:
        return B.carrier_of(texts, span)
    except ValueError as refusal:
        raise PromoteError(str(refusal)) from refusal


def apply_sources(texts, by_span):
    gaps = []
    spliced = []
    touched = []
    for span in sorted(by_span):
        path = carrier_of(texts, span)
        span_pieces = pieces(span, by_span[span])
        try:
            texts[path] = B.replace_slice(texts[path], span, span_pieces)
        except ValueError as refusal:
            raise PromoteError(str(refusal)) from refusal
        gaps += [(a, b) for a, b, line in span_pieces if line.startswith("INCBIN  baserom")]
        spliced.append(span)
        if path not in touched:
            touched.append(path)
    return gaps, spliced, touched


def write_rebuild(path, removed, added):
    lines = open(path, newline="").read().split("\n")
    want = {"call tools\\incbin.bat baserom.gba 0x%x 0x%x" % span for span in removed}
    kept = [line for line in lines if line.strip() not in want]
    dropped = len(lines) - len(kept)
    last = max(index for index, line in enumerate(kept) if "incbin.bat" in line)
    kept[last + 1:last + 1] = ["call tools\\incbin.bat baserom.gba 0x%x 0x%x" % gap
                               for gap in added]
    with open(path, "w", newline="") as handle:
        handle.write("\n".join(kept))
    return added, dropped


def census_rows(path, klass, census=CENSUS):
    with open(census if path is None else path, newline="") as handle:
        rows = [(int(row["start"], 16), int(row["end"], 16))
                for row in csv.DictReader(handle) if row["class"] == klass]
    return sorted(rows)


def swept(image, span, compress):
    start, end = span
    runs = []
    offset = start
    while offset + B.JCALG1_HEADER <= end:
        hit = B.jcalg1_container(image, offset, end, compress)
        if hit is None or not hit.get("byte_exact"):
            break
        if runs and runs[-1][1] == offset:
            runs[-1][1] = offset + hit["compressed"]
        else:
            runs.append([offset, offset + hit["compressed"]])
        offset += hit["compressed"]
    return [tuple(run) for run in runs]


def sweep_plan(image, spans, texts, compress):
    promoted, left = [], []
    for span in spans:
        try:
            carrier_of(texts, span)
        except PromoteError as absent:
            left.append((span, str(absent)))
            continue
        runs = swept(image, span, compress)
        if runs:
            promoted.append((span, runs))
        else:
            left.append((span, "no byte-exact container at 0x%X" % span[0]))
    return promoted, left


def write_sources(texts, by_span, rebuild):
    gaps, spliced, touched = apply_sources(texts, by_span)
    for path in touched:
        with open(path, "w", newline="") as handle:
            handle.write(texts[path])
    added, dropped = write_rebuild(rebuild, spliced, gaps)
    print("spliced %d slice(s) into %s, %d retired call(s) dropped, %d new retail gap(s)"
          % (len(spliced), ", ".join(os.path.relpath(path, ROOT) for path in touched),
             dropped, added))
    return spliced


def finish(cache, cache_close, code):
    cache_close()
    print("jcalg1 encode store misses=%d trusted=%d total=%d"
          % (cache["misses"], cache["trusted"], cache["total"]))
    return code


def open_encode_store(compress):
    return encode_cache.cached_compress(
        compress, COMPRESS, os.path.join(encode_cache.default_cache_dir(), BLOCK))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--payloads", default=os.path.join(ROOT, "assets", BLOCK))
    parser.add_argument("--out-dir", default=os.path.join(ROOT, "build", BLOCK))
    parser.add_argument("--asm-dir", default=os.path.join(ROOT, "asm"))
    parser.add_argument("--rebuild", default=os.path.join(ROOT, "rebuild.cmd"))
    parser.add_argument("--sweep-class", help="a RAW_REMAINDER.csv class whose rows --apply walks")
    parser.add_argument("--census", default=CENSUS, help="the census --sweep-class reads (required with it)")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if args.sweep_class and not args.census:
        parser.error("--sweep-class needs --census")

    image = open(args.rom, "rb").read()
    texts = carriers(args.asm_dir)
    compress, cache, cache_close = open_encode_store(B.oracle(COMPRESS))
    if args.sweep_class:
        spans = census_rows(args.census, args.sweep_class)
        promoted, left = sweep_plan(image, spans, texts, compress)
        moved = sum(end - start for _span, runs in promoted for start, end in runs)
        print("sweep %s: rows=%d promoted=%d rows=%d bytes left=%d"
              % (args.sweep_class, len(spans), len(promoted), moved, len(left)))
        for span, runs in promoted:
            print("  promote 0x%06X..0x%06X %6d B in %d container(s) -> %s"
                  % (span[0], span[1], sum(e - s for s, e in runs), len(runs),
                     ", ".join(run_name(s, e) for s, e in runs)))
        for span, why in left[:10]:
            print("  leave   0x%06X..0x%06X  %s" % (span[0], span[1], why))
        if len(left) > 10:
            print("  ... %d further row(s) left" % (len(left) - 10))
        if not args.apply:
            return finish(cache, cache_close, 0)
        write_sources(texts, {span: runs for span, runs in promoted}, args.rebuild)
        return finish(cache, cache_close, 0)

    extents = run_extents(texts.values())
    store = payload_store.path(args.payloads)
    if os.path.exists(store):
        payloads = payload_store.read(store)
        if not payloads:
            raise PromoteError("%s holds no payload: delete it and re-run extract.cmd (P-470)"
                               % store)
    else:
        payloads = source_payloads(image, texts.values(), compress)
        os.makedirs(args.payloads, exist_ok=True)
        payload_store.write(store, sorted(payloads.items()))
    runs = encoded(image, payloads, compress, extents)
    written, skipped = emit(runs, args.out_dir)
    print("containers=%d runs=%d stored=%d decoded=%d"
          % (len(payloads), len(runs), sum(b - a for a, b, _n, _c in runs),
             sum(len(p) for p in payloads.values())))
    print("files rewritten=%d skipped=%d" % (len(written) - skipped, skipped))
    for run_start, run_end, path in written:
        print("  %s  0x%06X..0x%06X %6d B"
              % (os.path.relpath(path, ROOT), run_start, run_end, run_end - run_start))
    if args.apply:
        write_sources(texts, slices_of(runs, B.incbin_spans()), args.rebuild)
    return finish(cache, cache_close, 0)


if __name__ == "__main__":
    raise SystemExit(main())
