"""Scan a GBA image for self-delimiting blocks, and for uniform fill runs.

The four compressed-data formats are the GBA BIOS ones, and every rule here is quoted from
GBATEK "BIOS Decompression Functions"
(https://problemkaputt.de/gbatek-bios-decompression-functions.htm):

    Data header (32bit)
      Bit 0-3   Reserved (LZ77/RLE) or Data size in bit units (Huffman) or
                Data size, 1=Diff8bit/2=Diff16bit (Diff)
      Bit 4-7   Compressed type: 1=LZ77, 2=Huffman, 3=run-length, 8=DiffFiltered
      Bit 8-31  24bit size of decompressed data in bytes

so the header byte is 0x10 (LZ77), 0x24/0x28 (Huffman, 4bit/8bit units), 0x30 (run-length),
0x81 (Diff16bit) or 0x82 (Diff8bit), and the decompressed size is a 24bit little-endian field
in the next three bytes.

A block is a HIT when the decoder consumes input without error, produces EXACTLY the size its
own header states, and the consumed compressed length ends inside the span being scanned. The
decoders are strict where the BIOS is not: a back-reference before the start of the output, or
a block that would overrun the stated size, is an ERROR here, because no compressor emits one.

DiffFiltered carries no compression: GBATEK states "destination data will have exactly the same
size as source data", so its compressed length is a pure function of its own size field and NO
byte string can fail to decode. It is reported but can never be trusted on its own - see the
code-region control in `scan_report`.

Usage:
    python tools/research/bios_block_scan.py --image baserom.gba --spans incbin
    python tools/research/bios_block_scan.py --image baserom.gba --spans ledger --json out.json
"""

import argparse
import collections
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

MIN_FILL = 256
MAX_DECOMPRESSED = 1 << 20
ROM_BASE = 0x08000000
LABEL_LINE = re.compile(r"^\s*\|[A-Za-z_][A-Za-z0-9_]*\|\s*$")
JCALG1_KINDS = (1, 2)
JCALG1_HEADER = 8
HUFF_ORDERS = ("word31", "bytemsb")
MAGIC = {0x10: "lz77", 0x24: "huff4", 0x28: "huff8", 0x30: "rle", 0x81: "diff16", 0x82: "diff8"}
FILL_MAGIC = "fill"


def _size24(image, offset, limit):
    if offset + 4 > limit:
        return None
    size = image[offset + 1] | image[offset + 2] << 8 | image[offset + 3] << 16
    return None if size > MAX_DECOMPRESSED else size


def lz77(image, offset, limit):
    size = _size24(image, offset, limit)
    if size is None:
        return None
    p, out = offset + 4, bytearray()
    while len(out) < size:
        if p >= limit:
            return None
        flags = image[p]
        p += 1
        for k in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> k):
                if p + 1 >= limit:
                    return None
                b0, b1 = image[p], image[p + 1]
                p += 2
                length = (b0 >> 4) + 3
                disp = ((b0 & 0x0F) << 8 | b1) + 1
                if disp > len(out) or len(out) + length > size:
                    return None
                for _ in range(length):
                    out.append(out[-disp])
            else:
                if p >= limit:
                    return None
                out.append(image[p])
                p += 1
    return bytes(out), p - offset


def rle(image, offset, limit):
    size = _size24(image, offset, limit)
    if size is None:
        return None
    p, out = offset + 4, bytearray()
    while len(out) < size:
        if p >= limit:
            return None
        flag = image[p]
        p += 1
        count = flag & 0x7F
        if flag & 0x80:
            count += 3
            if p >= limit or len(out) + count > size:
                return None
            out += bytes([image[p]]) * count
            p += 1
        else:
            count += 1
            if p + count > limit or len(out) + count > size:
                return None
            out += image[p:p + count]
            p += count
    return bytes(out), p - offset


def _bit(image, data, index, order):
    if order == "word31":
        word = data + (index & ~31)
        value = (image[word] | image[word + 1] << 8 | image[word + 2] << 16
                 | image[word + 3] << 24)
        return (value >> (31 - (index & 31))) & 1
    return (image[data + (index >> 3)] >> (7 - (index & 7))) & 1


def huff(image, offset, limit, order="word31"):
    size = _size24(image, offset, limit)
    if size is None or offset + 5 > limit:
        return None
    table = offset + 5
    length = (image[offset + 4] + 1) * 2
    if table + length > limit:
        return None
    data = table + length
    out = bytearray()
    node = table
    bits = 0
    while len(out) < size and bits < (limit - data) * 8:
        bit = _bit(image, data, bits, order)
        bits += 1
        if not table <= node < table + length:
            return None
        byte = image[node]
        child = (node & ~1) + (byte & 0x3F) * 2 + 2 + bit
        if (bit == 0 and byte & 0x80) or (bit == 1 and byte & 0x40):
            if not table <= child < table + length:
                return None
            out.append(image[child])
            node = table
            continue
        node = child
    if len(out) != size:
        return None
    return bytes(out), 5 + length + ((bits + 31) // 32) * 4


def diff(image, offset, limit):
    size = _size24(image, offset, limit)
    if size is None or offset + 4 + size > limit:
        return None
    return bytes(image[offset + 4:offset + 4 + size]), 4 + size


def decode(image, offset, limit, order="word31"):
    if offset + 4 > limit:
        return None
    magic = image[offset]
    kind = MAGIC.get(magic)
    if kind is None:
        return None
    if kind == "lz77":
        got = lz77(image, offset, limit)
    elif kind == "rle":
        got = rle(image, offset, limit)
    elif kind == "diff16" or kind == "diff8":
        got = diff(image, offset, limit)
    else:
        got = huff(image, offset, limit, order)
    if got is None:
        return None
    data, consumed = got
    if offset + consumed > limit:
        return None
    return kind, consumed, data


def spans_of(image, span_rows):
    return [(a, b) for a, b in span_rows if 0 <= a < b <= len(image)]


def merge(span_rows):
    out = []
    for start, end in sorted(span_rows):
        if out and start <= out[-1][1]:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return [(a, b) for a, b in out]


def subtract(span_rows, holes):
    out = []
    holes = merge(holes)
    for start, end in merge(span_rows):
        cursor = start
        for hole_start, hole_end in holes:
            if hole_end <= cursor or hole_start >= end:
                continue
            if hole_start > cursor:
                out.append((cursor, min(hole_start, end)))
            cursor = max(cursor, min(hole_end, end))
        if cursor < end:
            out.append((cursor, end))
    return out


def scan(image, span_rows, order="word31"):
    hits = []
    for start, end in spans_of(image, span_rows):
        offset = start + (-start % 4)
        while offset + 4 <= end:
            got = decode(image, offset, end, order)
            if got is not None:
                kind, consumed, data = got
                hits.append({"start": offset, "compressed": consumed, "decompressed": len(data),
                             "format": kind, "span": start})
            offset += 4
    return hits


def fill_runs(image, span_rows, minimum=MIN_FILL):
    runs = []
    for start, end in spans_of(image, span_rows):
        offset = start
        while offset < end:
            value = image[offset]
            cursor = offset + 1
            while cursor < end and image[cursor] == value:
                cursor += 1
            if cursor - offset >= minimum:
                runs.append({"start": offset, "length": cursor - offset, "value": value})
            offset = cursor
    return runs


def lz77_encode(data, window=4096, maximum=18):
    out = bytearray([0x10, len(data) & 0xFF, (len(data) >> 8) & 0xFF, (len(data) >> 16) & 0xFF])
    p = 0
    while p < len(data):
        flags = 0
        body = bytearray()
        for k in range(8):
            if p >= len(data):
                break
            best_len, best_disp = 0, 0
            low = max(0, p - window)
            for candidate in range(low, p):
                length = 0
                while (length < maximum and p + length < len(data)
                       and data[candidate + length] == data[p + length]):
                    length += 1
                if length > best_len:
                    best_len, best_disp = length, p - candidate
                    if length == maximum:
                        break
            if best_len >= 3:
                flags |= 0x80 >> k
                body += bytes([((best_len - 3) << 4) | ((best_disp - 1) >> 8), (best_disp - 1) & 0xFF])
                p += best_len
            else:
                body.append(data[p])
                p += 1
        out.append(flags)
        out += body
    return bytes(out)


def rle_encode(data, minimum=3):
    out = bytearray([0x30, len(data) & 0xFF, (len(data) >> 8) & 0xFF, (len(data) >> 16) & 0xFF])
    cursor = 0
    literals = bytearray()

    def flush():
        while literals:
            take = min(128, len(literals))
            out.append(take - 1)
            out.extend(literals[:take])
            del literals[:take]

    while cursor < len(data):
        value = data[cursor]
        run = 1
        while cursor + run < len(data) and data[cursor + run] == value:
            run += 1
        if run >= minimum:
            flush()
            total = run
            while run:
                take = min(130, run)
                out.append(0x80 | (take - 3))
                out.append(value)
                run -= take
            cursor += total
        else:
            literals.append(value)
            cursor += 1
    flush()
    return bytes(out)


def reencodes(image, start, consumed, kind):
    compressed = image[start:start + consumed]
    got = decode(image, start, start + consumed)
    if got is None:
        return False
    _kind, _consumed, data = got
    if kind == "lz77":
        return lz77_encode(data) == compressed
    if kind == "rle":
        return rle_encode(data) == compressed
    return False


def incbin_spans():
    from tools.gate import gate
    return [(a, a + n) for a, n in gate.incbin_ranges()]


def ledger_code_spans(total):
    from tools.gate import gate
    rows = [r for r in gate.ledger_rows() if r[2] in ("thumb", "arm") and r[1] > 0]
    rows.sort()
    spans = []
    covered = 0
    for off, length, isa, _region, _source, _kind, _evidence, _insn in rows:
        if covered >= total:
            break
        take = min(length, total - covered)
        spans.append((off, off + take))
        covered += take
    return spans


def scan_report(image, span_rows, order="word31"):
    hits = scan(image, span_rows, order)
    by_format = collections.Counter(h["format"] for h in hits)
    return hits, by_format


def promotable(image, hit):
    return (hit["compressed"] < hit["decompressed"]
            and reencodes(image, hit["start"], hit["compressed"], hit["format"]))


def cited_rows(path):
    import csv
    spans = []
    with open(path, newline="") as fh:
        for record in csv.DictReader(fh):
            start = int(record["row_start"], 16)
            end = int(record["row_end"], 16)
            spans.append((start - ROM_BASE if start >= ROM_BASE else start,
                          end - ROM_BASE if end >= ROM_BASE else end))
    return spans


def jcalg1_container(image, offset, limit, compressor=None):
    from tools.research import jcalg1
    if offset + JCALG1_HEADER > limit:
        return None
    kind, declared = struct.unpack_from("<II", image, offset)
    if kind not in JCALG1_KINDS or not 0 < declared <= MAX_DECOMPRESSED:
        return None
    got = jcalg1.decompress(image, offset + JCALG1_HEADER, limit)
    if got is None:
        return None
    data, consumed = got
    stored = JCALG1_HEADER + consumed
    if len(data) != declared or offset + stored > limit:
        return None
    exact = None
    if compressor is not None:
        exact = compressor(data) == image[offset:offset + stored]
    return {"start": offset, "compressed": stored, "decompressed": len(data),
            "format": "jcalg1", "span": offset, "byte_exact": exact}


def scan_jcalg1(image, span_rows, compressor=None):
    hits = []
    for start, end in spans_of(image, span_rows):
        offset = start + (-start % 4)
        while offset + JCALG1_HEADER <= end:
            hit = jcalg1_container(image, offset, end, compressor)
            if hit is not None:
                hits.append(hit)
            offset += 4
    return hits


def container_runs(hits):
    runs = []
    for hit in sorted(hits, key=lambda h: h["start"]):
        if runs and runs[-1][1] == hit["start"]:
            runs[-1][1] = hit["start"] + hit["compressed"]
            runs[-1][2] += 1
        else:
            runs.append([hit["start"], hit["start"] + hit["compressed"], 1])
    return [tuple(r) for r in runs]


def oracle(exe, scratch=None):
    import subprocess
    import tempfile
    scratch = scratch or tempfile.mkdtemp(prefix="jcalg1-oracle-")

    def compress(payload):
        source = os.path.join(scratch, "payload.bin")
        target = os.path.join(scratch, "container.bin")
        with open(source, "wb") as handle:
            handle.write(payload)
        if os.path.exists(target):
            os.remove(target)
        done = subprocess.run([exe, source, target], capture_output=True)
        if done.returncode != 0 or not os.path.exists(target):
            return None
        with open(target, "rb") as handle:
            return handle.read()
    return compress


def gap_name(start, end):
    return "baserom.gba_0x%x_0x%x.extracted" % (start, end)


def replace_slice(text, span, pieces):
    start, end = span
    pattern = re.compile(r"^(\s*)INCBIN\s+%s\s*$" % re.escape(gap_name(start, end)), re.M)
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise ValueError("%s occurs %d time(s), expected exactly one"
                         % (gap_name(start, end), len(matches)))
    cursor = start
    for piece_start, piece_end, _lines in pieces:
        if piece_start != cursor or piece_end > end:
            raise ValueError("pieces do not tile 0x%X..0x%X: next is 0x%X..0x%X"
                             % (start, end, piece_start, piece_end))
        cursor = piece_end
    if cursor != end:
        raise ValueError("pieces stop at 0x%X, before the span end 0x%X" % (cursor, end))
    lines = []
    for _s, _e, piece in pieces:
        for line in ([piece] if isinstance(piece, str) else piece):
            lines.append(line if LABEL_LINE.match(line) else "%s%s" % (matches[0], line))
    return pattern.sub(lambda _match: "\n".join(lines), text, count=1)


def carrier_of(texts, span):
    token = gap_name(*span)
    found = [path for path, text in texts.items()
             if re.search(r"^\s*INCBIN\s+%s\s*$" % re.escape(token), text, re.M)]
    if len(found) != 1:
        raise ValueError("%s is carried by %d file(s), expected exactly one" % (token, len(found)))
    return found[0]


def slice_carriers(asm_dir):
    out = {}
    for name in sorted(os.listdir(asm_dir)):
        if name.endswith(".s"):
            path = os.path.join(asm_dir, name)
            out[path] = open(path, newline="").read()
    return out


def guard(image, span_rows, order="word31"):
    offsets = 0
    candidates = collections.Counter()
    for start, end in spans_of(image, span_rows):
        offset = start + (-start % 4)
        while offset + 4 <= end:
            offsets += 1
            kind = MAGIC.get(image[offset])
            if kind:
                candidates[kind] += 1
            offset += 4
    hits = collections.Counter(hit["format"] for hit in scan(image, span_rows, order))
    return offsets, candidates, hits


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--spans", choices=("incbin", "ledger", "guard"), default="incbin")
    parser.add_argument("--huff-order", choices=HUFF_ORDERS, default="word31")
    parser.add_argument("--exclude", help="CSV with row_start,row_end hex ROM addresses to leave out")
    parser.add_argument("--oracle", help="compress.exe, to test each JCALG1 hit by re-encoding it")
    parser.add_argument("--json")
    args = parser.parse_args(argv)

    image = open(args.image, "rb").read()
    if args.spans == "ledger":
        spans = ledger_code_spans(sum(b - a for a, b in incbin_spans()))
    else:
        spans = incbin_spans()
    if args.exclude:
        holes = cited_rows(args.exclude)
        before = sum(b - a for a, b in spans)
        spans = subtract(spans, holes)
        print("excluded rows=%d bytes=%d ; scanned spans=%d bytes=%d (was %d)"
              % (len(merge(holes)), sum(b - a for a, b in merge(holes)), len(spans),
                 sum(b - a for a, b in spans), before))
    hits, by_format = scan_report(image, spans, args.huff_order)
    runs = fill_runs(image, spans)
    containers = scan_jcalg1(image, spans, oracle(args.oracle) if args.oracle else None)
    exact = [h for h in containers if h.get("byte_exact")]
    print("spans=%d bytes=%d hits=%d fills=%d order=%s"
          % (len(spans), sum(b - a for a, b in spans), len(hits), len(runs), args.huff_order))
    print("  jcalg1 containers=%-4d runs=%-3d stored=%-7d decoded=%-8d byte-exact=%s"
          % (len(containers), len(container_runs(containers)),
             sum(h["compressed"] for h in containers),
             sum(h["decompressed"] for h in containers),
             ("not measured (no --oracle)" if not args.oracle else str(len(exact)))))
    for run in container_runs(containers):
        print("  J-RUN  0x%06X..0x%06X %6d B containers=%d"
              % (run[0], run[1], run[1] - run[0], run[2]))
    for hit in sorted(containers, key=lambda h: -h["compressed"])[:20]:
        print("  %-6s 0x%06X stored=%-7d decoded=%-8d exact=%s"
              % (hit["format"], hit["start"], hit["compressed"], hit["decompressed"],
                 hit.get("byte_exact")))
    for kind, count in sorted(by_format.items(), key=lambda kv: -kv[1]):
        total = sum(h["compressed"] for h in hits if h["format"] == kind)
        print("  %-6s hits=%-5d compressed=%-9d" % (kind, count, total))
    for kind in sorted(by_format):
        subset = [h for h in hits if h["format"] == kind]
        exact = sum(1 for h in subset
                    if reencodes(image, h["start"], h["compressed"], kind))
        good = [h for h in subset if promotable(image, h)]
        print("  %-6s byte-exact=%d/%d decompressed %d..%d promotable=%d"
              % (kind, exact, len(subset),
                 min(h["decompressed"] for h in subset),
                 max(h["decompressed"] for h in subset), len(good)))
    for hit in sorted((h for h in hits if promotable(image, h)),
                      key=lambda h: -h["decompressed"])[:20]:
        print("  PROMOTE %-6s 0x%06X comp=%-7d dec=%-8d span=0x%06X"
              % (hit["format"], hit["start"], hit["compressed"], hit["decompressed"], hit["span"]))
    for run in sorted(runs, key=lambda r: -r["length"])[:20]:
        print("  fill  0x%06X..0x%06X %6d B value=0x%02X"
              % (run["start"], run["start"] + run["length"], run["length"], run["value"]))
    for hit in sorted(hits, key=lambda h: -h["decompressed"])[:20]:
        print("  %-6s 0x%06X comp=%-7d dec=%-8d span=0x%06X"
              % (hit["format"], hit["start"], hit["compressed"], hit["decompressed"], hit["span"]))
    if args.spans == "guard":
        control = ledger_code_spans(sum(b - a for a, b in spans))
        rows = [("incbin", spans), ("code", control)]
        tables = {label: guard(image, rows_, args.huff_order) for label, rows_ in rows}
        for label, rows_ in rows:
            print("control %-7s spans=%d bytes=%d"
                  % (label, len(rows_), sum(b - a for a, b in rows_)))
        print("format   incbin cand/hits/rate          code cand/hits/rate           trusted")
        for kind in ("lz77", "huff4", "huff8", "rle", "diff8", "diff16"):
            cells = []
            for label, _rows in rows:
                _offsets, candidates, counted = tables[label]
                cand = candidates.get(kind, 0)
                count = counted.get(kind, 0)
                cells.append("%6d %5d %8s" % (cand, count, ("%.4f" % (count / cand)) if cand else "-"))
            print("  %-7s %s %s" % (kind, cells[0], cells[1]))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"spans": len(spans), "hits": hits, "fills": runs}, fh, indent=1)
        print("wrote %s" % args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
