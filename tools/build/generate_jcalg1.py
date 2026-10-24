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
           section file per run, and byte-check every section from disk.

A run's extent is the token's own name, never the bytes (P-473). A `gen_<start>.bin` token (the
PATH-100-011 shape) takes its end from the next token's own address; a `gen_<start>_<end>.bin` token
carries its end itself.
"""

import argparse
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
    args = parser.parse_args(argv)

    image = open(args.rom, "rb").read()
    texts = B.slice_carriers(os.path.join(ROOT, "asm"))
    compress, cache, cache_close = open_encode_store(B.oracle(COMPRESS))
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
    return finish(cache, cache_close, 0)


if __name__ == "__main__":
    raise SystemExit(main())
