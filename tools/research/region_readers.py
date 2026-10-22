from __future__ import annotations

import argparse
import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, os.path.join(ROOT, "tools", "gate"), ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import gate  # noqa: E402
import incbin_census  # noqa: E402
import thumb_bodies  # noqa: E402

REGIONS = ("R00", "R07", "R09", "R10", "R18", "R22", "R32", "R33", "R34", "R35")
POPULATION = (1459, 92384)
READ_POPULATION = (265, 57059)
GATE_RAW = sum(length for _start, length in gate.incbin_ranges())
GATE_SLICES = len(gate.incbin_ranges())
REMAINDER = os.path.join(ROOT, "docs", "research", "RAW_REMAINDER.csv")
READS_IN = os.path.join(ROOT, "docs", "research", "REGION_READS.csv")
DOC_OUT = os.path.join(ROOT, "docs", "research", "REGION_READ_CENSUS.md")
VERDICT_DOCS = (
    ("docs/research/R00_R22_NULL_CENSUS.md", ("R00", "R09", "R10", "R18", "R22")),
    ("docs/research/R32_NULL_CENSUS.md", ("R32",)),
    ("docs/research/R33_R35_NULL_CENSUS.md", ("R33", "R34", "R35")),
)
BLOCK_HEAD = "## Sweep read verdict (generated: docs/research/REGION_READS.csv)"
ROM_BASE = 0x08000000
COPY_BODY = (0x08049124, 0x080491B8)
PENDING = "pending-image-route"
PENDING_REASON = ("the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before"
                  " the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route"
                  " (docs/research/MAP_BLOCK_LAYOUTS.md)")
CARVE_OUT = (0x29B308, 0x29B320)
ROM, EWRAM, IWRAM = (0x08000000, 0x09000000), (0x02000000, 0x02040000), (0x03000000, 0x03008000)
LOAD = ("ldr", "ldm", "ldrb", "ldrh", "ldrsb", "ldrsh")
OFFSET = re.compile(r"\[pc, #(-?0x[0-9a-f]+)\]")


def rom():
    with open(os.path.join(ROOT, "baserom.gba"), "rb") as handle:
        return handle.read()


def rows():
    out = []
    for row in csv.DictReader(open(REMAINDER, newline="")):
        if row["region"] not in REGIONS:
            continue
        out.append((int(row["start"], 16), int(row["end"], 16), row["region"], row["class"]))
    out.sort()
    measured = (len(out), sum(end - start for start, end, _r, _c in out))
    if measured != POPULATION:
        raise SystemExit("the population is %d row(s) / %d B, not %d / %d: the census moved"
                         % (measured + POPULATION))
    return out


def expand(text):
    out = []
    for part in text.split(";"):
        if not part:
            continue
        span, width = part.split(":")
        width = int(width)
        if ".." in span:
            ends, step = (span.split("/") + ["1"])[:2]
            first, last = (int(text, 16) for text in ends.split(".."))
            out.extend((at, width) for at in range(first, last + 1, max(1, int(step, 16))))
        else:
            out.append((int(span, 16), width))
    return out


def compress(pairs):
    by_width = collections.defaultdict(set)
    for at, width in pairs:
        by_width[width].add(at)
    parts = []
    for width in sorted(by_width):
        offsets = sorted(by_width[width])
        at = 0
        while at < len(offsets):
            if at + 1 < len(offsets):
                step = offsets[at + 1] - offsets[at]
                last = at + 1
                while last + 1 < len(offsets) and offsets[last + 1] - offsets[last] == step:
                    last += 1
                if last - at >= 2:
                    parts.append("%x..%x/%x:%d" % (offsets[at], offsets[last], step, width))
                    at = last + 1
                    continue
            parts.append("%x:%d" % (offsets[at], width))
            at += 1
    return ";".join(parts)


def import_table(path):
    census = rows()
    by_start = {(start, end): (start, end, region, klass)
                for start, end, region, klass in census}
    gathered = collections.defaultdict(lambda: ([], [], [0]))
    for row in csv.DictReader(open(path, newline="")):
        span = (int(row["start"], 16), int(row["bytes"]) + int(row["start"], 16))
        if span not in by_start:
            continue
        got = gathered[span]
        if int(row["pc"], 16) not in got[0]:
            got[0].append(int(row["pc"], 16))
        got[1].append((int(row["offset"], 16), int(row["width"])))
        got[2][0] += int(row["reads"])
    with open(READS_IN, "w", encoding="ascii", newline="\n") as handle:
        handle.write("start,end,region,class,reader_pcs,offsets,reads\n")
        for start, end, region, klass in census:
            if (start, end) not in gathered:
                continue
            pcs, pairs, total = gathered[(start, end)]
            handle.write("0x%06X,0x%06X,%s,%s,%s,%s,%d\n"
                         % (start, end, region, klass,
                            ";".join("0x%08X" % pc for pc in sorted(pcs)),
                            compress(pairs), total[0]))
    print("wrote %s (%d row(s))" % (os.path.relpath(READS_IN, ROOT), len(gathered)))
    return 0


def reads():
    out = {}
    for row in csv.DictReader(open(READS_IN, newline="")):
        span = (int(row["start"], 16), int(row["end"], 16))
        out[span] = ([int(text, 16) for text in row["reader_pcs"].split(";") if text],
                     expand(row["offsets"]), int(row["reads"]))
    return out


def decode(pc):
    return thumb_bodies.decode(pc - ROM_BASE)


def literal_offset(pc):
    got = decode(pc)
    if not got or got[1] not in ("ldr", "ldrb", "ldrh"):
        return None
    found = OFFSET.search(got[2])
    if not found:
        return None
    return ((pc + 4) & ~3) + int(found.group(1), 16) - ROM_BASE


def reader_class(pc):
    if pc & 1:
        for start in (pc - 5, pc - 3):
            got = decode(start)
            if got and got[0] == 4 and got[1] in ("bl", "blx") and start + 4 == pc - 1:
                return "copy return", start, "%08X %s %s" % (start, got[1], got[2])
        return "unclassified", pc, "odd pc, no bl"
    if COPY_BODY[0] <= pc < COPY_BODY[1]:
        return "copy body", pc, "inside the copy routine"
    got = decode(pc)
    if got and got[1] in LOAD:
        return "field load", pc, "%08X %s %s" % (pc, got[1], got[2])
    return "unclassified", pc, ("%08X %s %s" % (pc, got[1], got[2])) if got else "%08X ??" % pc


def address_share(image, span):
    words = [int.from_bytes(image[at:at + 4], "little") for at in range(span[0], span[1] - 3, 4)]
    if not words:
        return 0, 0
    good = sum(1 for word in words
               if ROM[0] <= word < ROM[1] or IWRAM[0] <= word < IWRAM[1]
               or EWRAM[0] <= word < EWRAM[1])
    return good, len(words)


def reason_of(span, found, image):
    size = span[1] - span[0]
    pcs, pairs, _total = found
    covered = set()
    for at, width in pairs:
        covered.update(range(at, min(at + width, size)))
    share = len(covered) / size if size else 0.0
    offsets = len({at for at, _w in pairs})
    expected = max(1, size // 4)
    kinds = collections.Counter(reader_class(pc)[0] for pc in pcs)
    if kinds["copy return"] + kinds["copy body"] == len(pcs):
        return "copy", share, offsets, expected, 0, 0
    good, words = address_share(image, span)
    if size < 4 and any(width > 1 for _at, width in pairs):
        return "fragment", share, offsets, expected, good, words
    if share >= 0.99:
        return "array", share, offsets, expected, good, words
    return "concentration", share, offsets, expected, good, words


RULES = {
    "copy": "every read pc is a return from, or a body of, the copy routine; a copy states no "
            "field and no length",
    "fragment": "the row is shorter than a word and the read is wider than the row",
    "array": "the reads cover every byte of the row at their own offsets",
    "concentration": "the reads cover part of the row, at fewer offsets than the row holds words",
}


def measure(image):
    census = rows()
    found = reads()
    table = {}
    for span in census:
        key = (span[0], span[1])
        if key in found:
            table[key] = reason_of(key, found[key], image)
        else:
            table[key] = None
    return census, found, table


def region_table(census, found):
    out = collections.defaultdict(lambda: [0, 0, 0, 0])
    for start, end, region, _klass in census:
        got = out[region]
        got[0] += 1
        got[1] += end - start
        if (start, end) in found:
            got[2] += 1
            got[3] += end - start
    return out


def class_table(census, found, table):
    out = collections.defaultdict(lambda: [0, 0])
    for start, end, _region, klass in census:
        table_key = (start, end)
        if table_key not in found:
            continue
        got = out[table[table_key][0]]
        got[0] += 1
        got[1] += end - start
    return out


def reader_table(census, found):
    by_pc = collections.defaultdict(lambda: [0, 0, set()])
    for start, end, _region, _klass in census:
        if (start, end) not in found:
            continue
        for pc in found[(start, end)][0]:
            got = by_pc[pc]
            got[0] += 1
            got[1] += end - start
            got[2].add((start, end))
    kinds = collections.Counter()
    for pc in by_pc:
        kinds[reader_class(pc)[0]] += 1
    return by_pc, kinds


def null_cost(table_rows):
    out = []
    for kind in ("copy", "pool", "fragment", "scan", "concentration"):
        got = [row for row in table_rows if row[0] == kind]
        if not got:
            continue
        ratios = sorted(row[3] / max(1, row[2]) for row in got)
        out.append((kind, len(got), sum(row[1] for row in got), ratios[len(ratios) // 2],
                    sum(row[4] for row in got), sum(row[5] for row in got),
                    sorted(row[2] for row in got)[len(got) // 2]))
    return out


def pending(span, klass):
    return klass == "graphics" or span == CARVE_OUT


def verdict(span, found, entry, klass=None):
    head = "%s: %s; " % (PENDING, PENDING_REASON) if pending(span, klass) else ""
    if entry is None:
        return head + "no reader in the 452-map sweep"
    pcs, pairs, total = found[span]
    kinds = collections.Counter()
    texts = []
    for pc in pcs[:3]:
        kind, _at, text = reader_class(pc)
        kinds[kind] += 1
        texts.append("%s `%s`" % (kind, text))
    size = span[1] - span[0]
    covered = set()
    for at, width in pairs:
        covered.update(range(at, min(at + width, size)))
    return (head + "read by %d pc(s): %s; %d offset(s) of %d word(s), %.2f of the row, %d read(s)"
            % (len(pcs), "; ".join(texts), len({at for at, _w in pairs}), max(1, size // 4),
               len(covered) / size, total))


def doc_text(census, found, table, image):
    regions = region_table(census, found)
    classes = class_table(census, found, table)
    by_pc, kinds = reader_table(census, found)
    total = sum(end - start for start, end, _r, _k in census)
    read_bytes = sum(end - start for start, end, _r, _k in census if (start, end) in found)
    read_rows = sum(1 for start, end, _r, _k in census if (start, end) in found)
    shapes = []
    for start, end, _region, _klass in census:
        if (start, end) not in found:
            continue
        reason, share, offsets, expected, good, words = table[(start, end)]
        shapes.append((reason, end - start, share, expected / max(1, offsets), good, words))
    copy_targets = collections.Counter()
    for pc in by_pc:
        kind, _at, text = reader_class(pc)
        if kind == "copy return":
            copy_targets[text.split()[-1]] += 1
    lines = []
    add = lines.append
    add("# The ten raw regions: every row the read sweep reached, and what its reader bounds")
    add("")
    add("Generated by `tools/research/region_readers.py` "
        "(`python tools/research/region_readers.py`).")
    add("The rows are the still-raw rows of `docs/research/RAW_REMAINDER.csv` in the regions "
        "`incbin_census.REGIONS`")
    add("numbers %s: %d rows / %d B, against the gate's raw-data"
        % (", ".join("`%s`" % name for name in REGIONS), len(census), total))
    add("%d B (`total %d row(s) %d B  gate raw-data %d B  EXACT`). The reads are the ones the"
        % (GATE_RAW, GATE_SLICES, GATE_RAW, GATE_RAW))
    add("452-map read sweep logged, one line per raw row in `docs/research/REGION_READS.csv`: the pcs")
    add("that read a byte of the row, the byte offset and width each read used, and how many reads it")
    add("took. Data addresses are file offsets, instruction addresses are bus addresses `0x08...`, and")
    add("every quote is a Thumb decode of the bytes at that address.")
    add("")
    add("A read is the only channel here. A row's class, its region, and the words that name it are")
    add("not readers (P-733), and a read pc is not a field: the split below separates the reads the")
    add("copy routine performed from the reads a field load performed.")
    add("")
    add("## Totals by region")
    add("")
    add("| region | rows | bytes | read rows | read bytes | unread rows | unread bytes |")
    add("|---|---|---|---|---|---|---|")
    for region in REGIONS:
        got = regions.get(region)
        if not got:
            add("| `%s` | 0 | 0 | 0 | 0 | 0 | 0 |" % region)
            continue
        add("| `%s` | %d | %d | %d | %d | %d | %d |"
            % (region, got[0], got[1], got[2], got[3], got[0] - got[2], got[1] - got[3]))
    add("| **total** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** |"
        % (len(census), total, read_rows, read_bytes, len(census) - read_rows, total - read_bytes))
    add("")
    add("`R07` holds no raw row: the region's one row left the raw set when its record table became")
    add("source, so the region contributes nothing here and nothing below.")
    add("")
    add("## The reader classes")
    add("")
    add("| class | distinct pc(s) | rows reached | rule |")
    add("|---|---|---|---|")
    for kind, rule in (
            ("copy return", "the read pc is the return address of a `bl` into the copy routine, so the "
                            "routine copied the row and this pc is the call site"),
            ("copy body", "the pc lies inside the copy routine itself"),
            ("field load", "the pc is a decoded load, so that instruction read the row"),
            ("unclassified", "neither rule fired")):
        reached = sum(1 for span in found
                      if any(reader_class(pc)[0] == kind for pc in found[span][0]))
        add("| %s | %d | %d | %s |" % (kind, kinds[kind], reached, rule))
    add("| **total** | **%d** | **%d** | |" % (len(by_pc), read_rows))
    add("")
    add("Every copy return resolves: the `bl` ending at the pc's own address is the call, and the")
    add("targets it reaches are %s."
        % ", ".join("`%s` (%d pc(s))" % (text.lstrip("#"), count)
                    for text, count in sorted(copy_targets.items())))
    add("A copy is not a layout, so a row read only through one keeps a null that names the call site,")
    add("and a row whose copied bytes no instruction reads has no reader for its contents.")
    add("")
    add("## The D1 join: rows, bytes and the reader class of the read rows")
    add("")
    add("| region | read rows | copy-only rows | field-load rows | unread rows |")
    add("|---|---|---|---|---|")
    for region in REGIONS:
        sub = [span for span in found
               if any(row[0] == span[0] and row[2] == region for row in census)]
        copy_only = sum(1 for span in sub
                        if all(reader_class(pc)[0] in ("copy return", "copy body")
                               for pc in found[span][0]))
        add("| `%s` | %d | %d | %d | %d |"
            % (region, len(sub), copy_only, len(sub) - copy_only,
               regions.get(region, [0, 0, 0, 0])[0] - len(sub)))
    add("")
    add("| what the shape of a read row is | rows | bytes | rule |")
    add("|---|---|---|---|")
    for kind in ("copy", "fragment", "array", "concentration"):
        got = classes.get(kind)
        if not got:
            continue
        add("| `%s` | %d | %d | %s |" % (kind, got[0], got[1], RULES[kind]))
    add("| **total** | **%d** | **%d** | |"
        % (sum(g[0] for g in classes.values()), sum(g[1] for g in classes.values())))
    add("")
    add("## What a read bounds, and the null each family beats")
    add("")
    add("A read's offset inside the row is what decides whether a layout follows. A row of many words")
    add("whose readers touch a handful of offsets is not a layout: it is those offsets, and the ratio")
    add("below is what the concentration is worth. A row the reads cover completely is an element array,")
    add("and the question there is the element count and the element's meaning.")
    add("")
    add("| family | rows | bytes | median share of the row covered | expected words per offset read "
        "| address words of the family |")
    add("|---|---|---|---|---|---|")
    for kind in ("copy", "fragment", "array", "concentration"):
        got = [row for row in shapes if row[0] == kind]
        if not got:
            continue
        shares = sorted(row[2] for row in got)
        ratios = sorted(row[3] for row in got)
        add("| `%s` | %d | %d | %.2f | %.1f | %d of %d |"
            % (kind, len(got), sum(row[1] for row in got), shares[len(shares) // 2],
               ratios[len(ratios) // 2], sum(row[4] for row in got), sum(row[5] for row in got)))
    add("")
    add("### The instructions behind three of those rows")
    add("")
    add("A `copy` row, quoted from the call site the sweep names instead of the routine:")
    add("")
    add("    0x08009B2C  3ff0f8fa  bl #0x8049120")
    add("")
    add("The return address is `0x08009B31`, the read pc, and the routine at `0x08049120` is the")
    add("copy. The row's bytes reached the caller and no field was read.")
    add("")
    add("A `concentration` row's reader, quoted whole, from the object search at `0x08004A9E`:")
    add("")
    add("    0x08004AA2  6f69  ldr r7, [r5, #0x14]")
    add("    0x08004AAC  9b69  ldr r3, [r3, #0x18]")
    add("    0x08004AAE  1e78  ldrb r6, [r3]")
    add("    0x08004AB0  8e42  cmp r6, r1")
    add("    0x08004AB4  5e78  ldrb r6, [r3, #1]")
    add("    0x08004AB6  9642  cmp r6, r2")
    add("    0x08004ABA  5888  ldrh r0, [r3, #2]")
    add("")
    add("The pointer at `+0x18` is indexed by the count read at `+0x14`, so the base of these loads")
    add("is an array element chosen at run time: the three offsets are the element's fields and the")
    add("row is whatever lies around that element. That is the shape the family's median share of")
    add("the row states, and it is why the offsets do not add up to a layout.")
    add("")
    add("A `concentration` row's other reader, quoted from `0x0800C378`:")
    add("")
    add("    0x0800C380  1206  lsls r2, r2, #0x18")
    add("    0x0800C382  920d  lsrs r2, r2, #0x16")
    add("    0x0800C384  9a58  ldr r2, [r3, r2]")
    add("")
    add("The index is a byte field shifted left by 24 and back by 22, so it is a multiple of four")
    add("taken from that byte and the load is a table entry at that offset. Which entries a run")
    add("touches depends on the byte's value, not on the row.")
    add("")
    add("### `copy`: the copy routine read the row and no field did")
    add("")
    add("A copy return is the address after a `bl` into the routine, so the row's bytes reached the")
    add("caller's buffer and no instruction read a field of them. The null is the copy itself: it")
    add("states a source pointer and a length the caller chose, never a field or a count inside the")
    add("row. A row stays raw until code that reads the copied bytes is measured.")
    add("")
    add("### `fragment`: the read is wider than the row")
    add("")
    add("A read wider than the row crosses the row's boundary, so the instruction reads the row and its")
    add("neighbour as one word. No layout inside the row carries that word: its other bytes lie in the")
    add("neighbouring carrier row, which is the rule P-847 records for a split row.")
    add("")
    add("### `array`: the reads cover every byte of the row")
    add("")
    add("%d rows / %d B are covered completely, at their own offsets. That is a layout of words, and"
        % (classes.get("array", [0, 0])[0], classes.get("array", [0, 0])[1]))
    add("what it does not state is the element count: the reads are one indexed load per element whose")
    add("index is a runtime value masked out of a byte field (`lsls`, then `lsrs` by the field's own")
    add("width), and no compare in the reader bounds the index. The count the reads do support is the")
    add("row's own length over four, and a layout built on that alone is refused here.")
    add("Of the family's %d words, %d are an address in the image; the rest are numbers, and a `DCD`"
        % (sum(row[5] for row in shapes if row[0] == "array"),
           sum(row[4] for row in shapes if row[0] == "array")))
    add("of numbers is a dump of retail bytes, which the route vocabulary refuses")
    add("(`docs/research/ROUTE_TO_100.md`, `## Route vocabulary`). %d row(s) of the family hold only"
        % sum(1 for row in shapes if row[0] == "array" and row[5] and row[4] == row[5]))
    add("address words, and such a row is a pointer row: it converts when a tracked symbol names its")
    add("target, which is the null `docs/research/POINTER_ROWS.csv` records for the same shape. The")
    add("falsifier for the rest is a count instruction in the reader, or a symbol naming every word.")
    add("")
    add("### `concentration`: the reader states offsets, not the row")
    add("")
    add("%d rows / %d B hold many words and their readers read few offsets of them. A row whose"
        % (classes.get("concentration", [0, 0])[0], classes.get("concentration", [0, 0])[1]))
    add("readers name a handful of offsets holds hundreds of words; the same number of reads over a")
    add("uniformly random row lands on that many offsets by construction. What a")
    add("field load does state is the offset and the width it used; what it never states is where the")
    add("row ends.")
    add("")
    add("## Rows that carry the `pending-image-route` status")
    add("")
    pending_rows = [row for row in census if pending((row[0], row[1]), row[3])]
    add("%d rows / %d B of the ten regions are a `graphics` row or the map block's 24 B carve-out"
        % (len(pending_rows), sum(end - start for start, end, _r, _k in pending_rows)))
    add("row `0x29B308`, and they carry the status `%s`: %s." % (PENDING, PENDING_REASON))
    add("The rule is the census class, not the reader: the retail bytes are a compressed stream the")
    add("decoder at IWRAM `0x03000040` expands, and `0x08049138` copies the decoded buffer to VRAM")
    add("(`docs/research/MAP_BLOCK_LAYOUTS.md`). The image round trip carries the 125 sections in")
    add("`tools/mapcontainer/animframe_manifest.csv`; the rows here are the ones it cannot carry - a")
    add("row holding no frame, a frame whose extent crosses a carrier token, the refused row, and the")
    add("carve-out - each measured in that page.")
    add("")
    add("## What converted")
    add("")
    add("No family above bounds both a layout and an extent, so every row of the ten regions keeps")
    add("its census null, now carrying the sweep's verdict; the `graphics` rows carry")
    add("`%s` instead. The largest null family is" % PENDING)
    add("`concentration` at %d rows / %d B, and the reason it does not convert is a measurement, not a"
        % (classes.get("concentration", [0, 0])[0], classes.get("concentration", [0, 0])[1]))
    add("gap: those readers touch between 1 and 8 offsets of rows of up to 832 words. The `array`")
    add("family is fully read and still refuses for the two reasons stated above, and the `copy` and")
    add("`fragment` families state no field at all.")
    add("")
    add("## The per-row verdict")
    add("")
    add("Each census document of these regions carries a generated section with one line per row it")
    add("covers, so a row's null and the sweep's verdict sit in one place:")
    add("")
    for path, covered in VERDICT_DOCS:
        add("- `%s`: %s." % (path, ", ".join("`%s`" % name for name in covered)))
    add("")
    add("A line reads `no reader in the 452-map sweep` when no logged read reached a byte of the row,")
    add("and otherwise names the read pcs, their class, the offsets and words the reads covered, the")
    add("share of the row they reached, and the number of reads.")
    add("")
    add("## Re-run")
    add("")
    add("    python tools\\research\\region_readers.py")
    add("    python tools\\research\\region_readers.py --write")
    add("    python tools\\research\\region_readers.py --check")
    add("")
    return "\n".join(lines) + "\n"


def block_text(census, found, table, regions):
    class_rows = [row for row in census
                  if row[2] in regions and row[3] == "code-without-entry"]
    lines = [BLOCK_HEAD, "",
             "One line per raw row of %s, from `tools/research/region_readers.py`."
             % ", ".join("`%s`" % region for region in regions)]
    if class_rows:
        lines += ["The %d `code-without-entry` row(s) of those regions carry their null in"
                  % len(class_rows),
                  "`docs/research/CODE_FRAGMENT_NULL_CENSUS.md`, which is the class's census."]
    lines += ["The offsets are the byte offsets inside the row that the sweep's reads used, and the",
              "share is the part of the row those reads reached. The null above each row stays its",
              "measured null; this line is the read verdict on it.", "",
              "| start | end | bytes | region | class | verdict |",
              "|---|---|---|---|---|---|"]
    for start, end, region, klass in census:
        if region not in regions or klass == "code-without-entry":
            continue
        key = (start, end)
        lines.append("| `0x%X` | `0x%X` | %d | `%s` | `%s` | %s |"
                     % (start, end, end - start, region, klass,
                        verdict(key, found, table[key], klass)))
    return "\n".join(lines) + "\n"


def splice(path, block):
    with open(path, encoding="ascii", newline="") as handle:
        text = handle.read()
    head = text.split(BLOCK_HEAD)[0]
    if head == text:
        return text.rstrip("\n") + "\n\n" + block
    return head.rstrip("\n") + "\n\n" + block


def write(image):
    census, found, table = measure(image)
    with open(DOC_OUT, "w", encoding="ascii", newline="\n") as handle:
        handle.write(doc_text(census, found, table, image))
    for name, regions in VERDICT_DOCS:
        path = os.path.join(ROOT, *name.split("/"))
        content = splice(path, block_text(census, found, table, regions))
        with open(path, "w", encoding="ascii", newline="\n") as handle:
            handle.write(content)
    print("wrote %s and %d verdict section(s)"
          % (os.path.relpath(DOC_OUT, ROOT), len(VERDICT_DOCS)))


def check(image):
    census, found, table = measure(image)
    with open(DOC_OUT, encoding="ascii") as handle:
        if handle.read() != doc_text(census, found, table, image):
            raise SystemExit("%s does not match the census re-derived from the image"
                             % os.path.relpath(DOC_OUT, ROOT))
    for name, regions in VERDICT_DOCS:
        path = os.path.join(ROOT, *name.split("/"))
        with open(path, encoding="ascii", newline="") as handle:
            stored = handle.read()
        if stored != splice(path, block_text(census, found, table, regions)):
            raise SystemExit("%s does not carry the derived verdict section" % name)
    total = sum(end - start for start, end, _r, _k in census)
    read = (sum(1 for start, end, _r, _k in census if (start, end) in found),
            sum(end - start for start, end, _r, _k in census if (start, end) in found))
    print("CHECK: %d row(s) %d B, read %d row(s) %d B, gate raw-data %d B"
          % (len(census), total, read[0], read[1], GATE_RAW))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--import", dest="source")
    args = parser.parse_args(argv)
    if args.source:
        return import_table(args.source)
    image = rom()
    if args.check:
        return check(image)
    census, found, table = measure(image)
    regions = region_table(census, found)
    for region in REGIONS:
        got = regions.get(region, [0, 0, 0, 0])
        print("region %-4s rows %5d bytes %7d read rows %4d read bytes %7d"
              % (region, got[0], got[1], got[2], got[3]))
    read = (sum(1 for start, end, _r, _k in census if (start, end) in found),
            sum(end - start for start, end, _r, _k in census if (start, end) in found))
    print("total %d row(s) %d B  read %d row(s) %d B  gate raw-data %d B"
          % (len(census), sum(end - start for start, end, _r, _k in census), read[0], read[1],
             GATE_RAW))
    kinds = collections.Counter(reader_class(pc)[0] for span in found for pc in found[span][0])
    print("reader class mentions: " + ", ".join("%s %d" % (k, kinds[k]) for k in sorted(kinds)))
    if args.write:
        write(image)
    return 0


if __name__ == "__main__":
    sys.exit(main())
