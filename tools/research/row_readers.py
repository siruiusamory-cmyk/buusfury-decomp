from __future__ import annotations

import argparse
import collections
import csv
import math
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, os.path.join(ROOT, "tools", "gate"), ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import consumer_search  # noqa: E402
import gate  # noqa: E402
import incbin_census  # noqa: E402
import region_readers  # noqa: E402
import residual_index  # noqa: E402
import thumb_bodies  # noqa: E402

REGION = "R32"
POPULATION = (1173, 38182)
GATE_RAW = 585508
REMAINDER = os.path.join(ROOT, "docs", "research", "RAW_REMAINDER.csv")
THUMB_CENSUS = os.path.join(ROOT, "docs", "research", "THUMB_BODIES.csv")
TRANSITIONS = os.path.join(ROOT, "work", "ledger.csv")
ROWS_OUT = os.path.join(ROOT, "docs", "research", "%s_ROWS.csv" % REGION)
DOC_OUT = os.path.join(ROOT, "docs", "research", "%s_NULL_CENSUS.md" % REGION)
FRAGMENT_DOC = os.path.join(ROOT, "docs", "research", "CODE_FRAGMENT_NULL_CENSUS.md")
POOL_OUT = os.path.join(ROOT, "docs", "research", "%s_POOL_ROWS.csv" % REGION)
ROM_BASE = 0x08000000
SEED = 20261017


def rom():
    with open(os.path.join(ROOT, "baserom.gba"), "rb") as handle:
        return handle.read()


def assert_population(spans, expected=POPULATION):
    measured = (len(spans), sum(end - start for start, end in spans))
    if measured != expected:
        raise SystemExit("the population is %d row(s) / %d B, not %d / %d: the census moved"
                         % (measured + expected))


def population():
    current = []
    for row in csv.DictReader(open(REMAINDER, newline="")):
        if row["region"] == REGION:
            current.append((int(row["start"], 16), int(row["end"], 16)))
    current.sort()
    if (len(current), sum(end - start for start, end in current)) == POPULATION:
        return current, True
    if not os.path.exists(ROWS_OUT):
        raise SystemExit("the remainder no longer carries the population and %s is missing"
                         % os.path.relpath(ROWS_OUT, ROOT))
    stored = sorted((int(row["start"], 16), int(row["end"], 16))
                    for row in csv.DictReader(open(ROWS_OUT, newline="")))
    assert_population(stored)
    return stored, False


def region_name(region=REGION):
    for index, entry in enumerate(incbin_census.REGIONS, 1):
        if "R%02d" % index == region:
            return entry.name
    return "no measured region"


def walked_literals(spans, image):
    index = thumb_bodies.Rows(spans)
    sources = []
    for start, end, mode, _insn in thumb_bodies.source_rows():
        if mode == "thumb":
            sources.append(((start, end), start, "ledger row 0x%06X" % start))
    converted = 0
    if os.path.exists(THUMB_CENSUS):
        for entry in csv.DictReader(open(THUMB_CENSUS, newline="")):
            if entry["verdict"] != thumb_bodies.VERDICT_CONVERTED:
                continue
            start, end = int(entry["start"], 16), int(entry["end"], 16)
            found = [int(text, 16) - ROM_BASE
                     for text in thumb_bodies.ENTRY_ADDRESS.findall(entry["entry_site"] or "")]
            inside = [value for value in found if start <= value < end]
            if inside:
                converted += 1
                sources.append(((start, end), inside[-1], "converted 0x%06X..0x%06X" % (start, end)))
    out, sites = {}, 0
    for row, offset, origin in sources:
        body = thumb_bodies.walk(row, [(offset, "walk", origin, "walk")])
        for at, (size, mnemonic, operands) in body.code.items():
            if not mnemonic.startswith("ldr"):
                continue
            found = thumb_bodies.PC_RELATIVE.search(operands)
            if not found:
                continue
            literal = ((ROM_BASE + at + 4) & ~3) + int(found.group(1), 0) - ROM_BASE
            if not 0 <= literal <= len(image) - 4:
                continue
            sites += 1
            target = index.of(literal)
            if target is not None:
                out.setdefault(target, []).append(
                    (literal, ROM_BASE + at, "%08X %s %s" % (ROM_BASE + at, mnemonic, operands)))
    return out, sites, (len(sources), converted)


def code_rows():
    return [row[:4] for row in gate.ledger_rows(TRANSITIONS) if row[2] in ("thumb", "arm")]


def walked_branches(spans, image):
    index = thumb_bodies.Rows(spans)
    out, instructions = {}, 0
    for start, end, mode, _insn in thumb_bodies.source_rows():
        if mode != "thumb" or not 0 <= start <= len(image) - 2:
            continue
        body = thumb_bodies.walk((start, end), [(start, "walk", "ledger row 0x%06X" % start, "walk")])
        instructions += len(body.code)
        for at, (size, mnemonic, operands) in body.code.items():
            target = thumb_bodies.direct_target(mnemonic, operands)
            if target is None:
                continue
            row = index.of(target - ROM_BASE)
            if row is not None:
                out.setdefault(row, []).append(
                    (target - ROM_BASE, "branch",
                     "%08X %s %s" % (ROM_BASE + at, mnemonic, operands), "walked"))
    return out, instructions


def swept_entries(spans):
    return thumb_bodies.entries(spans)


def value_loads(spans, image, code):
    index = thumb_bodies.Rows(spans)
    out = {}
    loads = consumer_search.literal_loads(image, code, spans)
    for site, literal, target in loads:
        row = index.of(target)
        if row is not None:
            out.setdefault(row, []).append(
                (site, literal, "%08X ldr [pc] 0x%06X = 0x%08X"
                 % (site, literal, ROM_BASE + target)))
    return out, len(loads)


def naming_words(spans, image):
    index = thumb_bodies.Rows(spans)
    out = collections.Counter()
    words = 0
    for at in range(0, len(image) - 3, 4):
        words += 1
        value = struct.unpack_from("<I", image, at)[0]
        if ROM_BASE <= value < ROM_BASE + len(image):
            row = index.of(value - ROM_BASE)
            if row is not None and not row[0] <= at < row[1]:
                out[row] += 1
    return out, words


def byte_stats(image, row):
    blob = image[row[0]:row[1]]
    counts = collections.Counter(blob)
    entropy = -sum((n / len(blob)) * math.log2(n / len(blob)) for n in counts.values()) if blob else 0.0
    entropy = max(entropy, 0.0) or 0.0
    zero = blob.count(0) / len(blob) if blob else 0.0
    words = [struct.unpack_from("<I", image, at)[0] for at in range(row[0], row[1] - 3, 4)]
    inside = sum(1 for value in words if ROM_BASE <= value < ROM_BASE + len(image))
    return entropy, zero, len(words), inside


def dispatch_before(image, row):
    for at in range(max(row[0] - 8, 0), row[0] - 1, 2):
        if struct.unpack_from("<H", image, at)[0] & 0xFF87 == 0x4487:
            return True
    return False


def families(spans, literals, branches):
    pools = {}
    for row, found in literals.items():
        start, end = row
        if start % 4 or (end - start) % 4 or end - start < 4:
            continue
        addresses = {literal for literal, _site, _text in found}
        if all(word in addresses for word in range(start, end - 3, 4)):
            pools[row] = found
    codes = {}
    for row, found in branches.items():
        if thumb_bodies.walk(row, found).code:
            codes[row] = found
    return pools, codes


def classify(spans, literals, branches, values, words, image, pools, codes, code_edges):
    out = {}
    for row in spans:
        start, end = row
        found = literals.get(row, [])
        named = {literal for literal, _site, _text in found}
        grid = list(range(start, end - 3, 4))
        crossing = any(literal + 4 > end for literal in named if start <= literal < end)
        shaped = dispatch_before(image, row)
        between = start in code_edges and end in code_edges
        if row in pools:
            family, reason = "pool", ""
        elif row in codes:
            family, reason = "", "a decoded branch enters and an instruction decodes, but the " \
                                 "branch channel is below its own null"
        elif branches.get(row):
            family, reason = "", "a decoded branch enters and no ARMv4T instruction fits in the row"
        elif crossing:
            family, reason = "", "a loaded word crosses the row boundary"
        elif named and start % 4 == 0 and (end - start) % 4 == 0:
            family, reason = "", "%d of %d word(s) load; the rest have no reader" % (
                len(named & set(grid)), len(grid))
        elif values.get(row):
            family, reason = "", "code loads a word naming this row; its bytes have no layout"
        elif shaped:
            family, reason = "", "the row follows a computed jump and no instruction reads it"
        elif between:
            family, reason = "", "between transcribed code rows and no instruction reads it"
        elif words.get(row):
            family, reason = "", "named by a word; a name is not a consumer"
        else:
            family, reason = "", "no decoded reader and no naming word at half-open bounds"
        out[row] = {"family": family, "reason": reason, "named": len(named & set(grid)),
                    "crossing": crossing, "grid": len(grid), "word_names": words.get(row, 0),
                    "value_sites": values.get(row, []), "readers": found,
                    "branches": branches.get(row, []), "dispatch": shaped, "between": between}
    return out


def class_of(entry):
    if entry["family"]:
        return entry["family"]
    if entry["branches"]:
        return "code-null"
    if entry["crossing"]:
        return "pool-fragment"
    if entry["named"]:
        return "pool-partial"
    if entry["value_sites"]:
        return "named-data"
    if entry["dispatch"]:
        return "after-dispatch"
    if entry["between"]:
        return "between"
    return "unreached"


def permuted(image, spans, seed=SEED):
    blob = bytearray(image)
    for start, end in spans:
        piece = bytearray(blob[start:end])
        random.Random(seed + start).shuffle(piece)
        blob[start:end] = piece
    return bytes(blob)


def measure(image, spans):
    literals, literal_sites, source_counts = walked_literals(spans, image)
    code = code_rows()
    values, loads = value_loads(spans, image, code)
    words, words_scanned = naming_words(spans, image)
    branches, instructions = walked_branches(spans, image)
    pools, codes = families(spans, literals, branches)
    edges = set()
    for start, length, _mode, _insn in code:
        edges.add(start)
        edges.add(start + length)
    table = classify(spans, literals, branches, values, words, image, pools, codes, edges)
    return {"literal": literals, "literal_sites": literal_sites, "sources": source_counts,
            "values": values, "loads": loads, "words": words, "words_scanned": words_scanned,
            "branches": branches, "instructions": instructions, "pools": pools, "codes": codes,
            "table": table, "code": code, "swept": len(swept_entries(spans))}


def nulls(image, spans, data):
    saved = thumb_bodies.ROM
    source = [(start, end) for start, end, mode, _insn in thumb_bodies.source_rows() if mode == "thumb"]
    shuffled = permuted(image, source)
    thumb_bodies.ROM = shuffled
    try:
        other, _sites, _counts = walked_literals(spans, shuffled)
        other_branches, other_instructions = walked_branches(spans, shuffled)
        swept = len(swept_entries(spans))
    finally:
        thumb_bodies.ROM = saved
    other_pools, _ = families(spans, other, {})
    numbers = {"pool_rows": len(other_pools),
               "pool_bytes": sum(e - s for s, e in other_pools),
               "any_rows": sum(1 for row in spans if other.get(row)),
               "real_any": sum(1 for row in spans if data["literal"].get(row)),
               "branch_rows": len(other_branches),
               "branch_instructions": other_instructions,
               "swept": swept,
               "source_rows": len(source),
               "source_bytes": sum(e - s for s, e in source)}
    chance = data["literal_sites"] * POPULATION[1] / float(len(image))
    lines = [
        "| channel | the site side byte-permuted | the real image |",
        "|---|---|---|",
        "| `literal`: any word of the row | %d row(s) | %d row(s) |"
        % (numbers["any_rows"], numbers["real_any"]),
        "| `literal`: every word of the row | %d row(s) / %d B | %d row(s) / %d B |"
        % (numbers["pool_rows"], numbers["pool_bytes"], len(data["pools"]),
           sum(e - s for s, e in data["pools"])),
        "| `branch` at an instruction boundary inside a walked body | %d row(s) of %d decoded "
        "instruction(s) | %d row(s) of %d |"
        % (numbers["branch_rows"], numbers["branch_instructions"], len(data["branches"]),
           data["instructions"]),
        "",
        "%d decoded literal site(s) over an %d B image: a random target lands in the population %.2f"
        % (data["literal_sites"], len(image), chance),
        "time(s) in total, so a row whose every word carries one is not a coincidence of the sweep.",
        "The permutation shuffles every ledger Thumb row's own bytes (seed 20261017), the side the",
        "literal, branch and walk rules read; the population's own bytes are untouched. The wider",
        "branch sweep `thumb_bodies.entries` fires on %d row(s) of the permuted source, so its count is"
        % numbers["swept"],
        "not evidence and no row is decoded on it.",
    ]
    return lines, numbers


def row_line(row, entry, image):
    entropy, zero, words, inside = byte_stats(image, row)
    if entry["family"] == "pool":
        readers = "%s (x%d)" % (entry["readers"][0][2], len(entry["readers"]))
    elif entry["branches"]:
        readers = entry["branches"][0][2]
    elif entry["readers"]:
        readers = "%s (x%d)" % (entry["readers"][0][2], len(entry["readers"]))
    elif entry["value_sites"]:
        readers = entry["value_sites"][0][2]
    elif entry["word_names"]:
        readers = "%d naming word(s)" % entry["word_names"]
    else:
        readers = "none"
    return "| `0x%X` | `0x%X` | %d | %.2f | %.2f | %d | %d | %s | %s | %s |" % (
        row[0], row[1], row[1] - row[0], entropy, zero, words, inside,
        class_of(entry), readers, entry["reason"] or "decoded, section above")


def fragment_rows(path=FRAGMENT_DOC):
    if not os.path.exists(path):
        return set()
    out = set()
    for _header, rows in residual_index.verdict_tables(path):
        for _number, cells in rows:
            span = residual_index.span_of(cells)
            if span:
                out.add(span)
    return out


def doc_text(spans, data, image, numbers):
    table = data["table"]
    total = sum(end - start for start, end in spans)
    pool_bytes = sum(e - s for s, e in data["pools"])
    code_bytes = sum(e - s for s, e in data["codes"])
    classes = collections.Counter(class_of(table[row]) for row in spans)
    class_bytes = collections.Counter()
    for row in spans:
        class_bytes[class_of(table[row])] += row[1] - row[0]
    stats = {row: byte_stats(image, row) for row in spans}
    short = sum(1 for row in spans if row[1] - row[0] == 2)
    odd = sum(1 for row in spans if (row[1] - row[0]) % 4)
    addressy = sum(1 for row in spans if stats[row][3])
    branches = len(data["branches"])
    code_rows_count = len(data["code"])
    code_bytes_ledger = sum(length for _s, length, _m, _i in data["code"])
    fragment = fragment_rows() & set(spans)
    lines = [
        "# `%s`'s raw rows: a per-row null" % REGION,
        "",
        "`%s` is the region `%s`, %d rows / %d B as `docs/research/RAW_REMAINDER.csv` carried them and"
        % (REGION, region_name(), len(spans), total),
        "the same figure as `python tools\\research\\raw_remainder.py` reports against the gate's",
        "raw-data (`total %d row(s) %d B  gate raw-data %d B  EXACT`). Data addresses are file"
        % (len(spans), total, GATE_RAW),
        "offsets, instruction addresses are bus addresses `0x08...`, and every quote is a Thumb decode",
        "of the bytes at that address. The census is measured before the conversion this ticket lands:",
        "the family below becomes source and every other row keeps a measured null.",
        "",
        "## Totals",
        "",
        "| class | rows | bytes | rule |",
        "|---|---|---|---|",
        "| `pool` | %d | %d | a row on the word grid whose every word is a decoded `ldr [pc,#imm]` "
        "literal address |" % (classes["pool"], class_bytes["pool"]),
        "| `code-null` | %d | %d | a decoded branch enters and an instruction decodes, but the branch "
        "channel is below its null |" % (classes["code-null"], class_bytes["code-null"]),
        "| `pool-fragment` | %d | %d | a loaded word crosses the row boundary |"
        % (classes["pool-fragment"], class_bytes["pool-fragment"]),
        "| `pool-partial` | %d | %d | some words of the grid load, the rest have no reader |"
        % (classes["pool-partial"], class_bytes["pool-partial"]),
        "| `named-data` | %d | %d | code loads a word naming the row; its bytes have no layout |"
        % (classes["named-data"], class_bytes["named-data"]),
        "| `after-dispatch` | %d | %d | the row follows a computed jump, unread |"
        % (classes["after-dispatch"], class_bytes["after-dispatch"]),
        "| `between` | %d | %d | between transcribed code rows, unread |"
        % (classes["between"], class_bytes["between"]),
        "| `unreached` | %d | %d | no decoded reader and no naming word |"
        % (classes["unreached"], class_bytes["unreached"]),
        "| **total** | **%d** | **%d** | |" % (len(spans), total),
        "",
        "The rows are exactly `docs/research/%s_ROWS.csv`, written once from that run; the family below"
        % REGION,
        "leaves the remainder and the rest keep their class here.",
        "",
        "## What was searched, and its denominator",
        "",
        "| channel | instrument | denominator | result on these rows |",
        "|---|---|---|---|",
        "| decoded `ldr [pc,#imm]` literal address in the row | `row_readers.walked_literals` | %d "
        "walked bod(ies): %d ledger Thumb row(s) and %d converted | %d row(s) with >= 1 word |"
        % (data["sources"][0], data["sources"][0] - data["sources"][1], data["sources"][1],
           numbers["real_any"]),
        "| decoded branch at an instruction boundary inside a walked body | `row_readers.walked_branches` "
        "| %d decoded instruction(s) | %d row(s) |" % (data["instructions"], branches),
        "| decoded `ldr` whose literal VALUE names the row | `consumer_search.literal_loads` | %d "
        "code row(s) / %d B, %d load(s) | %d row(s) |"
        % (code_rows_count, code_bytes_ledger, data["loads"], len(data["values"])),
        "| word-aligned word holding an address in the row | `row_readers.naming_words` | %d words | "
        "%d row(s), %d word(s) |" % (data["words_scanned"], len(data["words"]),
                                     sum(data["words"].values())),
        "",
        "Every count is half-open over each row's own span (`[start, end)`), never over the interval",
        "that contains the rows (P-738). A naming word is a name, not a consumer (P-733), and a",
        "literal-shaped halfword inside a data stream is not a reader (P-721).",
        "",
        "## Byte statistics",
        "",
        "Entropy %.2f..%.2f bits/byte, zero-byte share %.2f..%.2f, %d row(s) are a single halfword,"
        % (min(s[0] for s in stats.values()), max(s[0] for s in stats.values()),
           min(s[1] for s in stats.values()), max(s[1] for s in stats.values()), short),
        "%d row(s) are not a whole number of words and %d hold at least one word that is an address"
        % (odd, addressy),
        "in the image: most rows are a fragment of a pool or a gap between two bodies, not a body.",
        "",
        "## The `pool` family: a word grid every reader names",
        "",
        "%d rows / %d B start on the word grid, are a whole number of words, and every one of their"
        % (len(data["pools"]), pool_bytes),
        "words is the literal address of a decoded `ldr [pc,#imm]` in a walked body, for example",
        "",
    ]
    for row in sorted(data["pools"])[:4]:
        lines.append("    0x%06X..0x%06X  %s" % (row[0], row[1], data["pools"][row][0][2]))
    lines += [
        "",
        "so the layout is the reader's: one `DCD` per word, in order, at the row's own address (P-732).",
        "The null is the site side permuted:",
        "",
    ] + data["null_lines"] + [
        "",
        "A word of the image is the target of a decoded load by chance with probability %.4f (%d sites x"
        % (data["literal_sites"] * 4 / float(len(image)), data["literal_sites"]),
        "4 B / %d B), so the every-word rule is not what a sweep produces on its own." % len(image),
        "",
        "Falsifier: a row in this family with a word no decoded load reads, or a cold rebuild whose",
        "bytes differ.",
    ]
    lines += [
        "",
        "## The `code-null`: a branch enters and an instruction decodes",
        "",
        "%d rows / %d B are entered by a decoded source branch and decode as Thumb from that entry."
        % (len(data["codes"]), code_bytes),
        "They stay raw because the branch channel is BELOW its own null: the same rule over the",
        "byte-permuted source fires on more rows, so a branch target is not evidence in this band and",
        "no row is promoted on it (P-613). A row here is a branch target whose body the project's",
        "converter would accept, and nothing measures that it is reached.",
        "",
    ]
    for row in sorted(data["codes"]):
        lines.append("    0x%06X..0x%06X entered by %s" % (row[0], row[1], data["codes"][row][0][2]))
    lines += [
        "",
        "The %d other branch-entry rows are one halfword each: no ARMv4T instruction fits."
        % (branches - len(data["codes"])),
        "",
        "## The per-row null",
        "",
        "Each line: file offsets, bytes, entropy, zero-byte share, word-aligned words inside the row,",
        "words of it that are an address in the image, class, the decoded reader with its instruction,",
        "and why the row stays raw. `none` means no decoded instruction in the channels above names a",
        "byte of the row at the denominators quoted." + (
            "" if not fragment else
            " The region's %d `code-without-entry` rows are not in" % len(fragment)),
    ] + ([] if not fragment else [
        "this table: each is one half of an instruction whose other half lies in a neighbouring raw row,",
        "and `docs/research/CODE_FRAGMENT_NULL_CENSUS.md` carries that null per row.",
    ]) + [
        "",
        "| start | end | bytes | ent | zero | words | in | class | readers | null |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines += [row_line(row, table[row], image) for row in spans if row not in fragment]
    return "\n".join(lines) + "\n"


def split_section(text):
    head, found, tail = text.partition(region_readers.BLOCK_HEAD)
    return head, found + tail


def write(data, spans, image, numbers, fresh=True):
    if fresh:
        with open(ROWS_OUT, "w", encoding="ascii", newline="\n") as handle:
            handle.write("start,end\n")
            for row in spans:
                handle.write("0x%06X,0x%06X\n" % row)
    with open(POOL_OUT, "w", encoding="ascii", newline="\n") as handle:
        handle.write("start,end\n")
        for row in sorted(data["pools"]):
            handle.write("0x%06X,0x%06X\n" % row)
    tail = ""
    if os.path.exists(DOC_OUT):
        with open(DOC_OUT, encoding="ascii", newline="") as handle:
            tail = split_section(handle.read())[1]
    with open(DOC_OUT, "w", encoding="ascii", newline="\n") as handle:
        text = doc_text(spans, data, image, numbers)
        handle.write(text.rstrip("\n") + "\n\n" + tail if tail else text)
    print("wrote %s%s and %s"
          % (os.path.relpath(ROWS_OUT, ROOT) + ", " if fresh else "", os.path.relpath(POOL_OUT, ROOT),
             os.path.relpath(DOC_OUT, ROOT)))


def check():
    spans, _fresh = population()
    image = rom()
    data = measure(image, spans)
    _lines, numbers = nulls(image, spans, data)
    data["null_lines"] = _lines
    if not os.path.exists(DOC_OUT):
        raise SystemExit("%s is missing" % os.path.relpath(DOC_OUT, ROOT))
    with open(DOC_OUT, encoding="ascii") as handle:
        stored = split_section(handle.read())[0]
    if stored.rstrip("\n") != doc_text(spans, data, image, numbers).rstrip("\n"):
        raise SystemExit("%s does not match the census re-derived from the image"
                         % os.path.relpath(DOC_OUT, ROOT))
    print("CHECK: %s matches the census, %d row(s)" % (os.path.relpath(DOC_OUT, ROOT), len(spans)))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--nulls", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        return check()
    image = rom()
    spans, fresh = population()
    data = measure(image, spans)
    lines, numbers = nulls(image, spans, data)
    data["null_lines"] = lines
    print("population %d row(s) %d B; pool %d / %d B; code %d / %d B; literal sites %d; the site "
          "side permuted gives %d / %d B"
          % (len(spans), POPULATION[1], len(data["pools"]), sum(e - s for s, e in data["pools"]),
             len(data["codes"]), sum(e - s for s, e in data["codes"]), data["literal_sites"],
             numbers["pool_rows"], numbers["pool_bytes"]))
    counts = collections.Counter(class_of(data["table"][row]) for row in spans)
    for name in sorted(counts):
        print("  %-14s %4d row(s) %6d B" % (name, counts[name],
                                             sum(row[1] - row[0] for row in spans
                                                 if class_of(data["table"][row]) == name)))
    if args.nulls:
        for line in lines:
            print(line)
    if args.write:
        write(data, spans, image, numbers, fresh)
        if not fresh:
            print("the row list %s is frozen: the remainder moved and the doc is re-derived from it"
                  % os.path.relpath(ROWS_OUT, ROOT))


if __name__ == "__main__":
    sys.exit(main())
