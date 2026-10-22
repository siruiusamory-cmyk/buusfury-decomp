"""The `unknown` residual: its region census, every instrument's verdict with a null, and its readers.

    python tools/research/unknown_census.py            # the census doc and its CSV
    python tools/research/unknown_census.py --check     # recompute and assert, write nothing

The population is `raw_remainder.measure()`'s `unknown` class, so the row count and byte total are the
census's own and cannot drift from the gate. Three instruments are statistics (`sample`, `tiles4`,
`tiles8`): each fires only when its retail reading beats the mean of the same statistic over `DRAWS`
seeded permutations of the row. Seven are boolean shape probes (`webfoot`, `jcalg1`, `bios`, `palette`,
`pointers`, `thumb`, `text`): each is evaluated on the retail row and again on ONE seeded permutation,
so the report prints the rate at which the same shape occurs by chance, but the probe is not gated on
it. The report labels the two kinds separately. A probe reading zero is the instrument's reach, not a
measured absence: every probe starts at the row's first byte and stops at the row's end, so a container,
table or codec that begins inside a row is invisible to all of them. Nothing is printed as bytes or
text, only counts, offsets and hashes. The output is a pure function of the retail image and the tracked
tree.
"""

from __future__ import annotations

import argparse
import bisect
import collections
import hashlib
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in ("tools/gate", "tools/research", "tools/mapcontainer", "tools/webfoot", "tools/tilebank"):
    sys.path.insert(0, os.path.join(ROOT, *_path.split("/")))

import assetdir_samples  # noqa: E402
import bios_block_scan  # noqa: E402
import code_xref  # noqa: E402
import incbin_census  # noqa: E402
import jcalg1  # noqa: E402
import raw_remainder  # noqa: E402
import text_tables  # noqa: E402
import thumb_bodies  # noqa: E402

CSV_OUT = os.path.join(ROOT, "docs", "research", "UNKNOWN_CENSUS.csv")
DOC_OUT = os.path.join(ROOT, "docs", "research", "UNKNOWN_CENSUS.md")
CLASS = "unknown"
ROM_BASE = 0x08000000
MARGIN = 0.05
DRAWS = 5
TILE_MINIMUM = 0.60
INSTRUMENTS = ("sample", "webfoot", "jcalg1", "bios", "tiles4", "tiles8", "palette", "pointers",
               "thumb", "text")
STATISTICS = ("sample", "tiles4", "tiles8")
MEANING = {
    "sample": "the signed lag-1 Pearson coherence beats the row's own shuffle null by > %.2f "
              "(assetdir_samples.correlation, the test BF-ASSETDIR-CODEC-001 ran on the known PCM)"
              % MARGIN,
    "webfoot": "a PACKED (kind 1/2) container starts at the row start and ends inside the row "
               "(raw_remainder.webfoot_extent, the census's own extent rule)",
    "jcalg1": "the JCALG1 stream at the row start terminates inside the row (jcalg1.probe)",
    "bios": "a BIOS LZ77/RLE/Huffman/diff block starts at the row start and fits inside it "
            "(bios_block_scan.decode)",
    "tiles4": "the share of horizontally adjacent pixels that repeat, read as 4bpp 8x8 cells, is "
              ">= %.2f and beats the row's own permutation by > %.2f. The control table below shows "
              "the measured graphics blocks do not reach the threshold, so this statistic fails its "
              "own positive control and a fire here is NOT graphics evidence" % (TILE_MINIMUM, MARGIN),
    "tiles8": "the same statistic read as 8bpp cells; it fails the same positive control",
    "palette": "the row is whole halfwords, >= 8 of them, and EVERY halfword has bit 15 clear "
               "(a 15-bit BGR palette word)",
    "pointers": "the wider density rule: >= 16 B, >= 8 grid words, >= 50 % of them ROM/IWRAM/EWRAM "
                "addresses",
    "thumb": "a sequential ARMv4T Thumb decode covers >= 95 % of the row "
             "(raw_remainder.shape_coverage, recorded as non-discriminating)",
    "text": "text_tables.classify names the row a text, record-table or numeric-constant class",
}


class Image:

    def __init__(self, rom):
        self.image = bytearray(rom)

    def install(self, start, blob):
        self.image[start:start + len(blob)] = blob
        thumb_bodies.ROM = self.image

    def restore(self, start, blob):
        self.image[start:start + len(blob)] = blob
        thumb_bodies.ROM = self.image


def permuted(blob, start, draws=DRAWS):
    rng = random.Random(start)
    out = []
    for _ in range(draws):
        copy = list(blob)
        rng.shuffle(copy)
        out.append(bytes(copy))
    return out


def null_relation(fired, nulled):
    if nulled > fired:
        return "above"
    if nulled < fired:
        return "below"
    return "equal to"


def sample_fires(real, null):
    return real - null > MARGIN and real > 0.0


def coherence(blob, start, draws=DRAWS):
    real = assetdir_samples.correlation(assetdir_samples.signed(blob))
    nulls = [assetdir_samples.correlation(assetdir_samples.signed(copy))
             for copy in permuted(blob, start, draws)]
    return real, sum(nulls) / len(nulls)


def tile_repeat(blob, bpp):
    size, step = (32, 4) if bpp == 4 else (64, 8)
    same = pairs = 0
    for cell in range(0, len(blob) - size + 1, size):
        body = blob[cell:cell + size]
        pixels = []
        for row in range(8):
            line = body[row * step:(row + 1) * step]
            if bpp == 4:
                for byte in line:
                    pixels.append(byte & 0xF)
                    pixels.append(byte >> 4)
            else:
                pixels.extend(line)
        for at in range(63):
            if at % 8 == 7:
                continue
            pairs += 1
            same += pixels[at] == pixels[at + 1]
    return same / pairs if pairs else 0.0


def palette_row(blob):
    if len(blob) < 16 or len(blob) % 2:
        return False
    return all(blob[at + 1] < 0x80 for at in range(0, len(blob), 2))



def measure_row(image, start, length):
    end = start + length
    blob = bytes(image.image[start:end])
    out = {}
    real, null = coherence(blob, start)
    out["sample"] = sample_fires(real, null)
    packed = raw_remainder.webfoot_extent(image.image, start)
    out["webfoot"] = packed is not None and packed[1] <= end
    out["jcalg1"] = jcalg1.probe(image.image, start, end)["ok"]
    out["bios"] = bios_block_scan.decode(image.image, start, end) is not None
    nulls = permuted(blob, start)
    for bpp in (4, 8):
        real_tile = tile_repeat(blob, bpp)
        null_tile = sum(tile_repeat(copy, bpp) for copy in nulls) / len(nulls)
        out["tiles%d" % bpp] = real_tile >= TILE_MINIMUM and real_tile - null_tile > MARGIN
    out["palette"] = palette_row(blob)
    words, good = raw_remainder.pointer_words(image.image, start, length)
    out["pointers"] = length >= 16 and words >= 8 and good * 2 >= words
    out["thumb"] = raw_remainder.shape_coverage(image.image, (start, end)) >= 0.95
    out["text"] = text_tables.classify(image.image, (start, end, "row", 0))[0] != "unknown"
    return out


def sweep(rom, entries):
    image = Image(rom)
    real, null = {}, {}
    for row in entries:
        start, blob = row["start"], rom[row["start"]:row["end"]]
        image.install(start, blob)
        real[start] = measure_row(image, start, row["bytes"])
        for copy in permuted(blob, start, 1):
            image.install(start, copy)
            null[start] = measure_row(image, start, row["bytes"])
        image.restore(start, blob)
    return real, null


def modal_share(blob):
    return max(collections.Counter(blob).values()) / len(blob) if blob else 0.0


def byte_weighted_share(share_bytes):
    pairs = list(share_bytes)
    total = sum(length for _share, length in pairs)
    return sum(share * length for share, length in pairs) / total if total else 0.0


def class_shares(rom, rows, runs=DRAWS):
    out = {}
    for row in rows:
        blob = rom[row["start"]:row["end"]]
        real, null = coherence(blob, row["start"], runs)
        got = out.setdefault(row["class"], [0, 0, 0, 0, 0])
        got[0] += 1
        got[1] += row["bytes"]
        got[4] += modal_share(blob) * row["bytes"]
        if sample_fires(real, null):
            got[2] += 1
            got[3] += row["bytes"]
    return out


def controls(rom, rows):
    import generate_mapcontainer
    import generate_tilebank

    entries = assetdir_samples.entries(rom)
    sample = [coherence(rom[row["offset"]:row["offset"] + row["length"]], row["offset"])
              for row in entries]
    blocks = {
        "tilebank tiles 0x%06X" % generate_tilebank.BLOCK_START:
            (generate_tilebank.BLOCK_START, generate_tilebank.BLOCK_START + 0x4000),
        "map block 0x%06X" % generate_mapcontainer.MAP.start:
            (generate_mapcontainer.MAP.start, generate_mapcontainer.MAP.start + 0x4000),
    }
    tiles = {}
    for name, (low, high) in blocks.items():
        blob = rom[low:high]
        nulls = permuted(blob, low)
        tiles[name] = (tile_repeat(blob, 4), sum(tile_repeat(copy, 4) for copy in nulls) / DRAWS,
                       tile_repeat(blob, 8), sum(tile_repeat(copy, 8) for copy in nulls) / DRAWS)
    entry_share = byte_weighted_share(
        (modal_share(rom[row["offset"]:row["offset"] + row["length"]]), row["length"])
        for row in entries)
    return {"entries": len(entries),
            "fires": sum(1 for real, null in sample if sample_fires(real, null)),
            "mean_real": sum(real for real, _null in sample) / len(sample),
            "mean_null": sum(null for _real, null in sample) / len(sample),
            "entry_share": entry_share,
            "classes": class_shares(rom, rows),
            "tiles": tiles}


def census(entries, labelled):
    out = {}
    for row in entries:
        got = out.setdefault(row["region"], {"id": row["region_id"], "rows": [], "bytes": 0})
        got["rows"].append(row)
        got["bytes"] += row["bytes"]
    for region in out.values():
        sizes = sorted(row["bytes"] for row in region["rows"])
        low = min(row["start"] for row in region["rows"])
        high = max(row["end"] for row in region["rows"])
        below = bisect.bisect_left(labelled, low)
        above = bisect.bisect_left(labelled, high)
        region["min"], region["max"] = sizes[0], sizes[-1]
        region["median"] = statistics.median(sizes)
        region["aligned4"] = sum(1 for row in region["rows"] if row["start"] % 4 == 0)
        region["aligned2"] = sum(1 for row in region["rows"] if row["start"] % 2 == 0)
        region["below"] = labelled[below - 1] if below else None
        region["above"] = labelled[above] if above < len(labelled) else None
    return out


def readers(rom, entries, sites, regions):
    import struct

    cited = raw_remainder.citation_table()
    spans = sorted((row["start"], row["end"], row["region"]) for row in entries)
    starts = [start for start, _end, _region in spans]
    per = {}
    for kind in ("thumb", "arm"):
        for site, target in sites[kind]:
            offset = target - ROM_BASE
            if not 0 <= offset <= len(rom) - 4:
                continue
            value = struct.unpack_from("<I", rom, offset)[0]
            if not ROM_BASE <= value < ROM_BASE + len(rom):
                continue
            at = value - ROM_BASE
            index = bisect.bisect_right(starts, at) - 1
            if index < 0:
                continue
            low, high, region = spans[index]
            if not low <= at < high:
                continue
            got = per.setdefault(region, {"sites": set(), "addresses": set()})
            got["sites"].add(site)
            got["addresses"].add(at)
    table = {}
    for name, region in regions:
        got = per.get(name, {"sites": set(), "addresses": set()})
        cited_rows = [row for row in region["rows"] if cited.get(row["start"]) is not None]
        table[name] = {
            "id": region["id"], "sites": len(got["sites"]), "addresses": len(got["addresses"]),
            "first_site": min(got["sites"], default=None),
            "address_min": min(got["addresses"], default=None),
            "address_max": max(got["addresses"], default=None),
            "rows_cited": len(cited_rows),
            "bytes_cited": sum(row["bytes"] for row in cited_rows),
        }
    return table


def pointer_family(rom, entries, real):
    rows = [row for row in entries if real[row["start"]]["pointers"]]
    words = good = 0
    exact = []
    for row in rows:
        count, addresses = raw_remainder.pointer_words(rom, row["start"], row["bytes"])
        words += count
        good += addresses
        if count == addresses:
            exact.append(row)
    biggest = max(rows, key=lambda row: row["bytes"], default=None)
    labels = 0
    carriers = 0
    for name in sorted(os.listdir(os.path.join(ROOT, "asm"))):
        if name.startswith("assetdir3_") and name.endswith(".s"):
            carriers += 1
            with open(os.path.join(ROOT, "asm", name), errors="replace") as handle:
                labels += sum(1 for line in handle if line.startswith("|"))
    return {"rows": len(rows), "bytes": sum(row["bytes"] for row in rows), "words": words,
            "addresses": good, "exact": len(exact),
            "biggest": biggest["start"] if biggest else None,
            "biggest_words": raw_remainder.pointer_words(rom, biggest["start"], biggest["bytes"])
            if biggest else (0, 0),
            "carriers": carriers, "labels": labels}


def doc_text(entries, classes, regions, real, null, control, read, family):
    total = sum(row["bytes"] for row in entries)
    raw = sum(size for _count, size in classes.values())
    lines = []
    add = lines.append
    add("# The `unknown` residual, region by region")
    add("")
    add("Generated by `tools/research/unknown_census.py` (`python tools/research/unknown_census.py`);")
    add("`--check` recomputes and asserts, writing nothing. ROM `baserom.gba` sha256 `%s`."
        % incbin_census.ROM_SHA256)
    add("")
    add("**The population is `raw_remainder.measure()`'s `unknown` class: %d rows / %d B. U1 and U2"
        % (len(entries), total))
    add("each partition that population and sum to it exactly (`--check` asserts both); U4 covers only")
    add("the top regions, and U5 lists instrument families that overlap, so neither is a partition. It")
    add("is the largest class of the %d raw rows / %d B the assembler still INCBINs. A row's class is"
        % (sum(count for count, _size in classes.values()), raw))
    add("the first predicate that fired; the region is the census's own citation and bounds what the")
    add("row's negatives cover, not a proof that the row is no other format.**")
    add("")
    ordered = sorted(regions.items(), key=lambda item: -item[1]["bytes"])
    head, tail = ordered[:20], ordered[20:]
    add("## U1. The regions, by bytes")
    add("")
    add("| region | id | rows | bytes | row size min..max (median) | 4-aligned | 2-aligned | nearest labelled row below | above |")
    add("|---|---|---|---|---|---|---|---|---|")
    for name, region in head:
        add("| %s | `%s` | %d | %d | %d..%d (%g) | %d | %d | %s | %s |"
            % (name, region["id"], len(region["rows"]), region["bytes"], region["min"], region["max"],
               region["median"], region["aligned4"], region["aligned2"],
               "none" if region["below"] is None else "0x%06X" % region["below"],
               "none" if region["above"] is None else "0x%06X" % region["above"]))
    add("| ... %d further region(s) | | %d | %d | | | | | |"
        % (len(tail), sum(len(region["rows"]) for _name, region in tail),
           sum(region["bytes"] for _name, region in tail)))
    add("| **total** | | **%d** | **%d** | | | | | |" % (len(entries), total))
    add("")
    add("## U2. Every instrument, per region, against its null")
    add("")
    add("Each cell is `rows / bytes` the instrument fired on, then the same instrument on a seeded")
    add("byte permutation of each row. The null means two different things, and the instrument list")
    add("says which kind each column carries:")
    add("")
    add("- statistics (`%s`): the null is the mean of the same statistic over %d seeded"
        % ("`, `".join(STATISTICS), DRAWS))
    add("  permutations of the row, and a fire is the retail reading beating that mean by more than")
    add("  %.2f; these are the only null-adjusted cells in the table;" % MARGIN)
    add("- shape probes (the other seven): the null is the SAME boolean probe on ONE seeded")
    add("  permutation, i.e. the rate at which the shape occurs by chance. A probe fire is not gated")
    add("  on it, so the retail and null counts are two measurements of the probe, not a comparison.")
    add("")
    add("A `0` in a probe's cell is not evidence of absence: every probe starts at the row's first")
    add("byte and stops at the row's end, so a container, table or codec that begins inside a row is")
    add("invisible to all of them, and the tile statistic fails its own positive control below.")
    add("A probe's non-detection is therefore the instrument's reach, not a measured absence (P-661).")
    add("")
    add("| region | rows | bytes | " + " | ".join("`%s`" % name for name in INSTRUMENTS) + " |")
    add("|---" * (3 + len(INSTRUMENTS)) + "|")
    for name, region in head:
        cells = []
        for instrument in INSTRUMENTS:
            fired = [row for row in region["rows"] if real[row["start"]][instrument]]
            nulled = [row for row in region["rows"] if null[row["start"]][instrument]]
            cells.append("%d / %d (null %d / %d)"
                         % (len(fired), sum(row["bytes"] for row in fired),
                            len(nulled), sum(row["bytes"] for row in nulled)))
        add("| %s | %d | %d | %s |" % (name, len(region["rows"]), region["bytes"], " | ".join(cells)))
    add("| ... %d further region(s) | %d | %d |" % (len(tail),
                                                    sum(len(region["rows"]) for _n, region in tail),
                                                    sum(region["bytes"] for _n, region in tail))
        + " |" * len(INSTRUMENTS))
    add("")
    add("The instruments, exactly as re-run:")
    add("")
    for name in INSTRUMENTS:
        add("- `%s`: %s" % (name, MEANING[name]))
    add("")
    add("## The sample-stream test: its controls, and why it is not the class predicate")
    add("")
    add("Positive control: the 143 asset-directory blocks the policy sets as 8-bit signed sample data")
    add("kept as identity copies (K-234). %d of %d entries beat their own shuffle null by more than"
        % (control["fires"], control["entries"]))
    add("%.2f, mean lag-1 %.3f against a mean null of %.3f."
        % (MARGIN, control["mean_real"], control["mean_null"]))
    fired = [row for row in entries if real[row["start"]]["sample"]]
    add("")
    add("Applied to the `unknown` population the same rule fires on **%d rows / %d B**, against %d rows"
        % (len(fired), sum(row["bytes"] for row in fired),
           sum(1 for row in entries if null[row["start"]]["sample"])))
    add("on the permuted copies. It is not specific to samples, which is why it is reported here and")
    add("not used as a class predicate: the same rule over every class of the census, under the")
    add("population's own %d-draw null, reads" % DRAWS)
    add("")
    add("| class | rows | bytes | sample-test fires | fired bytes | share of bytes |")
    add("|---|---|---|---|---|---|")
    for name in raw_remainder.PRIORITY:
        got = control["classes"].get(name)
        if not got:
            continue
        add("| `%s` | %d | %d | %d | %d | %.1f %% |"
            % (name, got[0], got[1], got[2], got[3], 100.0 * got[3] / got[1]))
    add("")
    add("The `unknown` row here is the population paragraph's own measurement: both use the")
    add("population's %d draws, so both read the same fired rows. An earlier three-draw variant of this" % DRAWS)
    add("table read 594; a draw count is part of the protocol, so only the %d-draw reading is quoted and" % DRAWS)
    add("the table and the paragraph are one experiment, not two.")
    add("")
    add("`text/tables` is a class the tree calls data tables and `graphics` one it calls pixels, so a")
    add("statistic that also fires on their bytes does not name samples. Both shares below use one")
    add("aggregation, the byte-weighted mean of each row's modal-byte share: the residual's bytes read")
    add("%.1f %% against %.1f %% for the known sample blocks, which is the quantity this statistic"
        % (100.0 * control["classes"][CLASS][4] / control["classes"][CLASS][1],
           100.0 * control["entry_share"]))
    add("actually separates; the audio class therefore takes the record that names a block, not this")
    add("test.")
    add("")
    add("The tile statistic, on its own controls (real vs its permutation):")
    add("")
    add("| control block | 4bpp real | 4bpp null | 8bpp real | 8bpp null |")
    add("|---|---|---|---|---|")
    for name, (r4, n4, r8, n8) in control["tiles"].items():
        add("| %s | %.3f | %.3f | %.3f | %.3f |" % (name, r4, n4, r8, n8))
    add("")
    add("Both measured graphics controls sit below the %.2f threshold and at or below their own" % TILE_MINIMUM)
    add("permutations: the statistic is an inadequate detector of graphics on these blocks. That is a")
    add("fault in the instrument, not evidence that the rows it fires on are not graphics, and the route")
    add("table below refuses a tile route on the control's failure, never on the absence of a fire (P-665).")
    add("")
    add("## U4. The readers of the top regions")
    add("")
    add("`sites` is the pc-relative literal channel (`code_xref.scan`'s Thumb `ldr rX,[pc,#imm]` and")
    add("ARM literal loads whose word is an address inside ONE OF THE REGION'S OWN ROWS; a region")
    add("that is a scatter of rows is counted row by row, never over its hull). `rows cited` is the")
    add("rows of the region any citation channel reaches (the census's `references`).")
    add("")
    add("| region | id | literal sites | distinct addresses | first site | address range | rows cited | bytes cited |")
    add("|---|---|---|---|---|---|---|---|")
    for name, _region in head:
        got = read[name]
        add("| %s | `%s` | %d | %d | %s | %s..%s | %d | %d |"
            % (name, got["id"], got["sites"], got["addresses"],
               "none" if got["first_site"] is None else "0x%08X" % got["first_site"],
               "none" if got["address_min"] is None else "0x%06X" % got["address_min"],
               "none" if got["address_max"] is None else "0x%06X" % got["address_max"],
               got["rows_cited"], got["bytes_cited"]))
    add("")
    add("A region with a site is a format LEAD, not a format: the channel names the row's address and")
    add("never its length, count or terminator (P-419).")
    add("")
    add("## U5. What a route would need, and what it is missing")
    add("")
    add("**Converted by this ticket: 0 B.** No family below has a route that rebuilds its bytes")
    add("exactly today; each row states the route the tree already owns and the measured blocker.")
    add("")
    add("| family (the instrument that fires) | rows | bytes | route the tree owns | measured blocker |")
    add("|---|---|---|---|---|")
    add("| pointer density | %d | %d | symbolic `DCD` table (PTR-TABLE-001, `tools/research/"
        "pointer_rows.py`) | %d of the %d words are ROM/IWRAM/EWRAM addresses and %d of the %d rows "
        "is 100 %%: the strict predicate refuses every one, and the non-address words have no "
        "established meaning. The largest (0x%06X, %d words, %d addresses) is the 53 x 20 B "
        "asset-directory-3 descriptor, whose address words name emitted payload bytes; the %d carrier "
        "files for that payload carry %d label(s), so naming them would be a number spelled as a "
        "name |"
        % (family["rows"], family["bytes"], family["addresses"], family["words"], family["exact"],
           family["rows"], family["biggest"] or 0, family["biggest_words"][0],
           family["biggest_words"][1], family["carriers"], family["labels"]))
    text_rows = [row for row in entries if real[row["start"]]["text"]]
    add("| text shape | %d | %d | `DCB`/`DCW`/`DCD` in a transcribed slice (PATH-100-016) | 0 of the "
        "rows is a `TRANSCRIBED_DATA_RUNS.csv` run (that class takes exact runs), and the "
        "policy keeps game text out of git: it is emitted at build time by a generator, "
        "and no generator decodes these runs |"
        % (len(text_rows), sum(row["bytes"] for row in text_rows)))
    tiles = [row for row in entries if real[row["start"]]["tiles4"] or real[row["start"]]["tiles8"]]
    add("| flat-run (4bpp/8bpp) | %d | %d | the map/sprite block generator "
        "(`generate_mapcontainer`, `tools/tilebank`) | fails its positive control: the measured "
        "graphics blocks do not reach the threshold (table above), so a fire here cannot be called a "
        "tile and the route is refused. The blocks' RESIDUAL has no emitter either "
        "(GRAPHICS-RESIDUAL-002..006) |"
        % (len(tiles), sum(row["bytes"] for row in tiles)))
    samples = [row for row in entries if real[row["start"]]["sample"]]
    add("| sample coherence | %d | %d | decoder+encoder, or a generator | the PCM policy keeps raw "
        "2026-10-18 keeps raw 8-bit sample data out of source (\"Keep out\"): classification only, "
        "0 B convertible by policy |" % (len(samples), sum(row["bytes"] for row in samples)))
    for name, route in (("jcalg1", "decoder+encoder (jcalg1.py, the packed container's body)"),
                        ("bios", "decoder+encoder (BIOS LZ77/RLE/Huffman)"),
                        ("palette", "none: no consumer and no emitter for a bare palette run")):
        fired = [row for row in entries if real[row["start"]][name]]
        nulled = [row for row in entries if null[row["start"]][name]]
        add("| `%s` | %d | %d | %s | the permutation fires on %d rows / %d B, %s the retail count: "
            "one permutation is not a null distribution, so the retail fires are not container "
            "evidence either way (a statistical reading, not an exclusion) |"
            % (name, len(fired), sum(row["bytes"] for row in fired), route,
               len(nulled), sum(row["bytes"] for row in nulled),
               null_relation(len(fired), len(nulled))))
    add("")
    add("The `thumb` instrument fires on %d rows / %d B against %d / %d on the permutations, so it"
        % (sum(1 for row in entries if real[row["start"]]["thumb"]),
           sum(row["bytes"] for row in entries if real[row["start"]]["thumb"]),
           sum(1 for row in entries if null[row["start"]]["thumb"]),
           sum(row["bytes"] for row in entries if null[row["start"]]["thumb"])))
    add("decides nothing here, exactly as the route doc's own control records.")
    add("")
    add("## Re-run")
    add("")
    add("    python tools\\research\\unknown_census.py")
    add("    python tools\\research\\unknown_census.py --check")
    add("")
    return "\n".join(lines) + "\n"


def table_faults(text):
    faults = []

    def flush():
        if not block:
            return
        cells = block[0].count("|")
        for row in block:
            if row.count("|") != cells or not row.rstrip().endswith("|"):
                faults.append((row, cells))
        block.clear()

    block = []
    for line in text.splitlines():
        if line.startswith("|"):
            block.append(line)
        else:
            flush()
    flush()
    return faults


def file_difference(path, text):
    with open(path, "rb") as handle:
        committed = handle.read()
    generated = text.encode()
    if committed == generated:
        return None
    at = next((index for index, (a, b) in enumerate(zip(committed, generated)) if a != b),
              min(len(committed), len(generated)))
    return committed[:at].count(b"\n") + 1


def check_files(pairs):
    ok = True
    for path, content in pairs:
        name = os.path.relpath(path, ROOT)
        line = file_difference(path, content)
        if line is None:
            print("%s: identical to the generated text" % name)
        else:
            print("%s: differs from the generated text at line %d" % (name, line))
            ok = False
    return ok


def summed_tables(text):
    columns = {"## U1.": (3, 4), "## U2.": (2, 3)}
    out, section = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            section = next((name for name in columns if line.startswith(name)), None)
            if section:
                out[section] = [0, 0]
            continue
        if section is None or not line.startswith("|"):
            continue
        cells = line.split("|")
        if cells[1].strip().strip("*") == "total":
            continue
        try:
            out[section][0] += int(cells[columns[section][0]].strip().strip("*"))
            out[section][1] += int(cells[columns[section][1]].strip().strip("*"))
        except (IndexError, ValueError):
            continue
    return {name: tuple(values) for name, values in out.items()}


def csv_text(entries, real, null):
    fields = ("start", "end", "bytes", "region") + INSTRUMENTS + ("null_fires",)
    lines = [",".join(fields)]
    for row in entries:
        cells = ["0x%06X" % row["start"], "0x%06X" % row["end"], str(row["bytes"]), row["region_id"]]
        cells += ["1" if real[row["start"]][name] else "0" for name in INSTRUMENTS]
        cells.append(str(sum(1 for value in null[row["start"]].values() if value)))
        lines.append(",".join(cells))
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="recompute and assert, write nothing")
    args = parser.parse_args(argv)
    rom = raw_remainder.read_rom()
    all_rows, _controls = raw_remainder.measure()
    classes = raw_remainder.totals(all_rows)
    entries = [row for row in all_rows if row["class"] == CLASS]
    total = sum(row["bytes"] for row in entries)
    declared = tuple(classes.get(CLASS, (0, 0)))
    if (len(entries), total) != declared:
        raise SystemExit("the unknown population %d / %d B is not the class total %s"
                         % (len(entries), total, declared))
    labelled = sorted(row["start"] for row in all_rows if row["class"] != CLASS)
    regions = census(entries, labelled)
    if sum(region["bytes"] for region in regions.values()) != total:
        raise SystemExit("the region table does not sum to the unknown total")
    real, null = sweep(rom, entries)
    if any(set(real[start]) != set(INSTRUMENTS) for start in real):
        raise SystemExit("an instrument did not report on every row")
    control = controls(rom, all_rows)
    read = readers(rom, entries, code_xref.scan(rom),
                   sorted(regions.items(), key=lambda item: -item[1]["bytes"])[:20])
    family = pointer_family(rom, entries, real)
    text = doc_text(entries, classes, regions, real, null, control, read, family)
    broken = table_faults(text)
    if broken:
        raise SystemExit("the generated doc has %d broken pipe-table row(s): %r"
                         % (len(broken), [row for row, _cells in broken[:3]]))
    summed = summed_tables(text)
    if set(summed) != {"## U1.", "## U2."}:
        raise SystemExit("the partitioned tables are not both present: %s" % sorted(summed))
    for name, (rows, size) in sorted(summed.items()):
        if (rows, size) != (len(entries), total):
            raise SystemExit("%s sums to %d rows / %d B, not the population %d / %d"
                             % (name[3:].rstrip("."), rows, size, len(entries), total))
    blob = csv_text(entries, real, null)
    print("unknown %d rows / %d B in %d regions" % (len(entries), total, len(regions)))
    for name in INSTRUMENTS:
        fired = [row for row in entries if real[row["start"]][name]]
        nulled = [row for row in entries if null[row["start"]][name]]
        print("  %-9s fires on %5d rows / %7d B  (null %4d rows / %7d B)"
              % (name, len(fired), sum(row["bytes"] for row in fired),
                 len(nulled), sum(row["bytes"] for row in nulled)))
    print("sample control: %d of %d known sample blocks fire (mean lag-1 %.3f vs %.3f)"
          % (control["fires"], control["entries"], control["mean_real"], control["mean_null"]))
    print("doc sha256=%s" % hashlib.sha256(text.encode()).hexdigest())
    print("csv sha256=%s" % hashlib.sha256(blob.encode()).hexdigest())
    for name, (rows, size) in sorted(summed.items()):
        print("%s sums to %d rows / %d B" % (name[3:].rstrip("."), rows, size))
    if args.check:
        matched = check_files(((CSV_OUT, blob), (DOC_OUT, text)))
        print("check only: nothing written")
        return 0 if matched else 1
    for path, content in ((CSV_OUT, blob), (DOC_OUT, text)):
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    print("wrote %s (%d B) and %s (%d B)" % (os.path.relpath(CSV_OUT, ROOT), len(blob),
                                             os.path.relpath(DOC_OUT, ROOT), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
