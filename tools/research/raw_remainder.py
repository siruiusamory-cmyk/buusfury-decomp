from __future__ import annotations

import csv
import hashlib
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in ("tools/gate", "tools/research", "tools/mapcontainer", "tools/tilebank",
              "tools/webfoot"):
    sys.path.insert(0, os.path.join(ROOT, *_path.split("/")))

import gate  # noqa: E402
import incbin_census  # noqa: E402

ROM = os.path.join(ROOT, "baserom.gba")
CSV_OUT = os.path.join(ROOT, "docs", "research", "RAW_REMAINDER.csv")
DOC_OUT = os.path.join(ROOT, "docs", "research", "ROUTE_TO_100.md")
JCALG1_DIR = os.path.join(ROOT, "build", "jcalg1")
TRANSCRIBED = os.path.join(ROOT, "docs", "research", "TRANSCRIBED_DATA_RUNS.csv")
TOKEN = re.compile(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted")
SITE = re.compile(r"Thumb 0x([0-9a-fA-F]{8})")
ROM_BASE = 0x08000000
MAX_OUTPUT = 0x4000
IWRAM = (0x03000000, 0x03008000)
EWRAM = (0x02000000, 0x02040000)
FILL_VALUES = (0x00, 0xFF)
FILL_MINIMUM = 4

PRIORITY = ("fill/padding", "JCALG1-compressed", "code-without-entry", "other-compressed",
            "graphics", "pointer-tables", "text/tables", "audio", "unknown")

ROUTES = {
    "fill/padding": (
        "fill:uniform",
        "generator",
        "tools/research/fill_promote.py emits a labeled `SPACE n` for the run; the run's own "
        "uniformity is the input and no retail payload travels"),
    "JCALG1-compressed": (
        "jcalg1:span",
        "generator",
        "tools/research/generate_jcalg1.py re-encodes the payload from the container's decoded "
        "payload, a build-time extracted input (extract.cmd writes the gen_<start>.bin token)"),
    "code-without-entry": (
        "code:thumb-entry-band",
        "NONE",
        "CODE-ENTRY-001 converted 556 of the 565 rows its Thumb census refused - the 568 refusals "
        "PATH-100-018 reported were the unrepaired ADS install answering `A1439E: Cannot obtain "
        "license`, and with the repaired toolchain on PATH each row reassembles byte-exact (P-574). "
        "The rows it could not spell are row-boundary fragments - one half of a 4-byte `BL`, or one "
        "byte of a 16-bit instruction - so no instruction can be spelled there. The class holds "
        "nothing else: 9 rows are one halfword of a `BL` and 2 are one byte of a 16-bit "
        "instruction, each with the other half in a neighbouring raw row of another class "
        "(`docs/research/CODE_FRAGMENT_NULL_CENSUS.md`). The three whole spans it also held "
        "(`0x042118..0x042188`, `0x0426D0..0x042750`, `0x042784..0x042876`, 482 B) are source: a "
        "Thumb control transfer from a site in transcribed code enters each, 454 of their bytes are "
        "the walk from those sites and reassemble byte-exact, and the transcribed row ending at "
        "`0x042118` falls through into it, which is the entry CODE-BAND-005 held out for"),
    "other-compressed": (
        "compress:webfoot",
        "decoder+encoder (MEASURED: the 45 packed rows the class held reproduced byte-exactly and "
        "are now carried by the generator; the 46th stays INCBIN)",
        "tools/webfoot/webfoot_lz.py decodes and tools/compress/compress.exe re-encodes. Measured by "
        "`--route-probe` on the class the fixed predicate leaves, by `generate_jcalg1.py "
        "--sweep-class other-compressed` (1 row, 0 promoted, `no byte-exact container at 0x29B308`) "
        "and token by token off both 16-byte bodies: the one kind-1 container 0x29B308 decodes to the "
        "identical 2,048-byte payload but re-encodes to a different, valid tokenization, first "
        "differing byte 16. Retail body tokens: `literal-mode bits=7 base=2`; `lit 0x44`; `lit 0x02`; "
        "`copy code=3 distance=2 length=1278` (output 2); `base-byte 0x02` (output 1280); "
        "`copy code=3 distance=1 length=766` (output 1281); `base-byte 0x02` (output 2047); `end`. "
        "Re-encode body tokens: the same first three; `copy code=3 distance=2 length=1278`; "
        "`copy code=3 distance=1 length=766` from output 1280; `short-copy distance=1` (2046); "
        "`short-copy distance=1` (2047); `end`. One tie decides it: at output 1280 the byte equals "
        "the literal base, so the retail encoder starts a fresh `base-byte` token while compress.exe "
        "extends the distance-1 copy over it and closes with two 1-byte copies; both tokenizations are "
        "valid and both fill the same 16 body bytes, so this is an encoder tie-break, not a decode "
        "error, and nothing in `generate_jcalg1.py` or `tools/compress/main.cpp` selects the other "
        "branch. The two encoders of this tree disagree on every "
        "packed row - webfoot_lz.pack emits kind 2 and its stream differs from retail byte 0 - so the "
        "retail tokenization is `tools/compress/compress.exe`'s and a row it does not reproduce needs "
        "an encoder this tree does not have; this row stays raw"),
    "graphics": (
        "graphics:family-block",
        "generator (the block's parsed members are planned; the residual has none)",
        "the block's own generator FAMILY: tools/mapcontainer/generate_mapcontainer.py "
        "--block map|sprite and tools/tilebank emit the block's PARSED members. These rows are "
        "precisely the bytes that generator does NOT emit - the residual after the parsed members - "
        "so the emitter for the residual does not exist today and the residual's format is still to "
        "be established (K-138 for the asset-directory payload format; the map/sprite block's "
        "residual is the generator's own `retail`/`carve-out` disposition). GRAPHICS-RESIDUAL-002 "
        "measured every row, and GRAPHICS-SPLICE-001 planned the map block's two root-named record "
        "families: 926 x 24 B records from root `+0x24` (count) and `+0x28` (base), code at "
        "0x0800942C / 0x08009452, and 735 x 4 B pointer records from `+0x40` / `+0x44`, code at "
        "0x08012664, spliced as 552 generated runs / 25,164 B. GRAPHICS-RESIDUAL-003 then "
        "converted two of the four causes that were left: a MapEntry `+0x2C` array holds MORE than "
        "one root (accessor 0x080089CC indexes it with the variant number read at 0x08008AB6), so "
        "walking every slot reaches six more roots and the records they name (2,204 B of the cause "
        "`dominant_record_unreached`), and a child-list row (u8 count, u8 word_01, u16 tag, `count` "
        "addresses, the index array naming those lists in order, then 0x18 B handler objects) states "
        "its own length (14,454 B across the map block, 12,564 B of `address_dense` and 96 B of "
        "`container_the_scan_missed`). GRAPHICS-RESIDUAL-004 closed 003's proofs and converted 8,724 B "
        "more of the same family: an object's first word has a SECOND measured constructor "
        "(`0x080072CC` and `0x08007674` both allocate the same 0x18 B object and store a handler "
        "table, 170 objects under the first and 570 under the second), and a gap whose own start is "
        "not a row start still ends on rows - the chain that lands on the gap's end is claimed (109 "
        "rows / 8,724 B, against a byte-permuted null of 0). What is left is per block "
        "tilebank_palette 0 rows / 0 B, tilebank_tiles 0 / 0, sprite 0 / 0 and map 100 / 90,212 "
        "(`tools/research/residual_causes.py --rows` prints the per-row table): 4,740 B / 3 rows whose "
        "leading container is carried by another emitter's JCALG1 run, and 85,472 B / 97 rows that "
        "fire no structural test, 53,664 B / 35 of them named only by ONE word inside them that a "
        "root's `+0x10` points at (the word after it a ROM address, the row otherwise not addresses) "
        "and 31,808 B / 62 that a child list's address word names at the row's own start (57 of the 62, "
        "1,602 address words against a byte-permuted null's 32; GRAPHICS-RESIDUAL-006) but that no "
        "code site reads and that state no length, terminator or count - their format stays "
        "UNESTABLISHED and 0 B of them convert. The ten sprite rows (3,656 B) are emitted by "
        "`--block sprite`: the function at 0x0800EF94 indexes each per-animation cell grid at "
        "`[def+0x50] + 8*frame + 2*direction`, so a grid's extent is 8 B times the frame count of the "
        "animation record its slot names. 126 grids over the ten rows, byte-equal on the gate"),
    "pointer-tables": (
        "ptrtable:every-word",
        "symbolic table",
        "the words are re-emitted as a tracked `DCD` of symbols, no retail byte payload. "
        "PTR-TABLE-001 converted every row whose words are all named - an existing label, a symbol "
        "the linker's table carries, or a house `unk_<ROMADDR>` constant for an IWRAM address - and "
        "its per-word record is `docs/research/POINTER_ROWS.csv`. BF-102B converted 11 of the 29 "
        "rows whose grid words do not cover the row (166 B): their bytes are a pc-relative literal "
        "pool - every word is the target of an `LDR [pc,#imm]` - so the 2-byte zero pad is a `DCB` "
        "and the words are `DCD`, symbol-spelled where a name exists and numeric where none does or "
        "where the operand carries the Thumb bit (the `|sym|+1` form makes armlink emit `$f` at the "
        "row's end, which `tools/symbols` names no kind for). The 18 rows left (259 B) each hold one "
        "halfword of a word on the image grid whose other bytes lie in the neighbouring carrier row, "
        "so no layout inside the row carries them. A row left here otherwise has a word that lies "
        "inside a carrier with no label at it, and naming such a word would be a number spelled as "
        "a name, which this vocabulary refuses. The "
        "predicate is the STRICT one - at least two words on the image's own grid and 100% of them "
        "ROM/IWRAM/EWRAM addresses - not the wider density rule (>= 16 B, >= 8 words, >= 50% "
        "addresses), which measured 433 rows / 39,142 B on the 4,322-row census of PATH-100-019 "
        "(2026-10-16)"),
    "text/tables": (
        "text:transcribed-run",
        "symbolic table",
        "the run is re-emitted as tracked `DCB`/`DCW`/`DCD` directives in its transcribed slice, no "
        "retail byte payload (the route PATH-100-016 walked the other way)"),
    "audio": (
        "audio:record-span",
        "generator (733,911 B)",
        "Both directories are the source route: `tools/mapcontainer/audiodir.py` ties directory 1's "
        "blocks to the fields the mixer reads at `0x0803E0FC`..`0x0803E112`, ties directory 2's to the "
        "music record's `+8` read at `0x0803E542` (indexed by `12 * byte`, stored at `slot+0x28`), and "
        "`assetdirectory.block_blob` re-encodes both streams from their decoded samples at build time. "
        "A row whose span lies inside a record's `data_ptr`..`data_ptr+byte_length` is that block's "
        "bytes. The smoothness statistic (`assetdir_samples.correlation`, the test that measured "
        "those blocks) is NOT the predicate: it beats its own shuffle null on most of this residual's "
        "bytes and on a measurable share of the `text/tables` bytes too, so it names sparseness, not "
        "samples (per-class shares in docs/research/UNKNOWN_CENSUS.md)"),
    "unknown": (
        "unknown:residual",
        "NONE",
        "no route found at this denominator"),
}

METHOD_TEXT = {
    "fill/padding": "a row of at least 4 B whose every byte is one value, and that value is 0x00 or "
                    "0xFF (`len(set(bytes)) == 1`)",
    "JCALG1-compressed": "the row lies inside a `build\\jcalg1\\gen_<start>.bin` run span (start "
                         "from the file name, end = start + its size)",
    "code-without-entry": "the row is outside `docs/research/ARM_BODIES.csv` and "
                          "`thumb_bodies.entries()` reports an entry whose SITE lies in the "
                          "transcribed code band 0x000158..0x071758",
    "other-compressed": "`webfoot_lz.validate_retail_termination(rom, row_start)` succeeds with a "
                        "PACKED kind (1 or 2) and its "
                        "`packed_end` is at or before the row's end (0x4000 output ceiling)",
    "graphics": "the row lies wholly inside a measured graphics block (map block, sprite block, "
                "tilebank tiles or the tilebank palette)",
    "pointer-tables": "every 4-byte word of the row on the image's own grid is a ROM, IWRAM or EWRAM "
                      "address and the row carries at least two words",
    "text/tables": "the row's exact span is a run `docs/research/TRANSCRIBED_DATA_RUNS.csv` classes "
                   "as `data`",
    "audio": "the row lies wholly inside a span one of the 143 records of the two 12-byte asset "
             "directories names (`data_ptr`..`data_ptr+byte_length`; assetdir_samples.entries, the "
             "tiling K-226/K-234 measured twice)",
    "unknown": "no instrument above fired (the residual, stated at its own denominator)",
}

ROUTE_TOKENS = {
    "fill/padding": "generator",
    "JCALG1-compressed": "generator",
    "code-without-entry": "NONE",
    "other-compressed": "decoder+encoder",
    "graphics": "generator-residual",
    "pointer-tables": "symbolic-table",
    "text/tables": "symbolic-table",
    "audio": "generator (733,911 B)",
    "unknown": "NONE",
}

ROUTE_PROBE = {"other-compressed": (0, 1, 0)}

LEDGER_OUT = os.path.join(ROOT, "docs", "research", "RESIDUAL_LEDGER.csv")
LEDGER_DOC = os.path.join(ROOT, "docs", "research", "RESIDUAL_LEDGER.md")
LEDGER_FIELDS = ("start", "end", "bytes", "region", "route", "references", "consumer", "attempts",
                 "status")
STATUSES = ("identified binary", "runtime-pending", "in progress", "unmapped")

IDENTIFIED_REGIONS = tuple("R%d" % number for number in range(20, 32) if number != 22)

BAND_TICKETS = (("CODE_BAND.csv", "CODE-BAND-002"), ("CODE_BAND_R19.csv", "CODE-BAND-003"),
                ("CODE_BAND_R32-R00.csv", "CODE-BAND-004"))

ATTEMPTS = {
    "in progress": "GRAPHICS-RESIDUAL-002:null;GRAPHICS-RESIDUAL-003:residual;"
                   "GRAPHICS-RESIDUAL-004:open@tail",
    "identified binary": "END-ROM-RECON-001:no-format-beats-null",
    "runtime-pending": "citations_in_source:no-code-site;RUNTIME-CONSUMER-002:read",
}
CLASS_ATTEMPTS = {
    "code-without-entry": "CODE-ENTRY-001:9-row-boundary-fragments;BF-503:other-half-in-another-class",
    "other-compressed": "GEN-COMPRESSED-001:tokenization-differs",
    "pointer-tables": "PTR-TABLE-001:unnamed-word;PTR-WORDS-002:no-family",
    "text/tables": "PATH-100-016:data-run-unconverted",
    "graphics": "GRAPHICS-RESIDUAL-002:null",
    "fill/padding": "none",
    "JCALG1-compressed": "none",
    "audio": "none",
    "unknown": "none",
}

METHOD_DETAIL = {
    "fill/padding": "`bios_block_scan.fill_runs`' own uniformity rule (the one "
                    "`tools/research/fill_promote.py:plan` calls), applied per row at a 4 B minimum",
    "JCALG1-compressed": "the 24 `build\\jcalg1\\gen_*.bin` tokens `extract.cmd` writes; a row whose "
                         "span lies inside one is that generator's output",
    "code-without-entry": "`tools/research/thumb_bodies.py:entries()` over the union of the frozen "
                          "census rows and today's INCBIN rows, filtered to rows outside the frozen "
                          "census whose first entry SITE is inside the transcribed code band",
    "other-compressed": "`tools/webfoot/webfoot_lz.py:validate_retail_termination` at the row's own "
                        "start - the extent rule `tools/research/packer_census.py:retail_extent` "
                        "uses",
    "graphics": "the generator modules' own constants: `generate_mapcontainer.MAP`/`.SPRITE`, "
                "`generate_tilebank.BLOCK_START` + `BLOCK_LEN`, `generate_tilebank.PALETTE_FILE`",
    "pointer-tables": "a word-grid read at the image's own 4-byte alignment; the address ranges are "
                      "`transcribed_data.IWRAM`/`EWRAM` and the ROM window",
    "text/tables": "`docs/research/TRANSCRIBED_DATA_RUNS.csv`, column `class`, written by "
                   "`tools/research/transcribed_data.py:classify`",
    "audio": "`tools/mapcontainer/assetdir_samples.py:entries` - the two directories' own 12-byte "
             "records, each `data_ptr` and `byte_length` asserted by `assetdir`/`assetdir2`'s "
             "contract; the block a record names is the block it measures; "
             "`tools/mapcontainer/audiodir.py` reports the code site that reads each table",
    "unknown": "the residual after every other class has taken its bytes; the instruments that "
               "returned nothing here are the same ones that fired elsewhere in this table",
}


def read_rom():
    with open(ROM, "rb") as handle:
        return handle.read()


def slice_tokens():
    out = []
    directory = os.path.join(ROOT, "asm")
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".s"):
            continue
        with open(os.path.join(directory, name), errors="replace") as handle:
            for number, text in enumerate(handle, 1):
                for match in TOKEN.finditer(text):
                    start, end = int(match.group(1), 16), int(match.group(2), 16)
                    out.append((start, end - start, name, number, match.group(0)))
    out.sort()
    spans = gate.incbin_ranges()
    if [(start, length) for start, length, _f, _n, _t in out] != spans:
        raise SystemExit("the asm token scan (%d rows) is not gate.incbin_ranges() (%d rows)"
                         % (len(out), len(spans)))
    return out


def jcalg1_spans():
    out = []
    if not os.path.isdir(JCALG1_DIR):
        return out
    for name in sorted(os.listdir(JCALG1_DIR)):
        match = re.fullmatch(r"gen_([0-9a-fA-F]+)\.bin", name)
        if match:
            start = int(match.group(1), 16)
            out.append((start, start + os.path.getsize(os.path.join(JCALG1_DIR, name))))
    return sorted(out)


def transcribed_runs():
    out = {}
    if not os.path.exists(TRANSCRIBED):
        return out
    with open(TRANSCRIBED, newline="") as handle:
        for row in csv.DictReader(handle):
            out[(int(row["rom_start"], 16), int(row["rom_end"], 16))] = row["class"]
    return out


def graphics_blocks():
    import generate_mapcontainer as generator
    import generate_tilebank as tilebank

    return (
        (tilebank.BLOCK_START, tilebank.BLOCK_START + tilebank.BLOCK_LEN, "tiles",
         "generate_tilebank.BLOCK_START..+BLOCK_LEN, %d banks" % tilebank.BANK_COUNT),
        (tilebank.PALETTE_FILE, tilebank.PALETTE_FILE + 2 * tilebank.PALETTE_ENTRIES, "palettes",
         "generate_tilebank.PALETTE_FILE, %d entries" % tilebank.PALETTE_ENTRIES),
        (generator.MAP.start, generator.MAP.end, "maps",
         "generate_mapcontainer.MAP, the map-container block"),
        (generator.SPRITE.start, generator.SPRITE.end, "tiles",
         "generate_mapcontainer.SPRITE, the sprite block"),
    )


def entry_rows(rom):
    import thumb_bodies

    spans = sorted(set(thumb_bodies.today_rows()) | set(thumb_bodies.frozen_rows()))
    frozen = thumb_bodies.frozen_rows()
    band = next(r for r in incbin_census.REGIONS if r.name == "first-MiB code band")
    low = min(start for start, _end in band.ranges)
    high = max(end for _start, end in band.ranges)
    out = {}
    refused = {}
    for row, found in sorted(thumb_bodies.entries(spans).items()):
        if row in frozen:
            continue
        sites = []
        for _offset, kind, site, tier in found:
            match = SITE.match(site)
            if match and low <= int(match.group(1), 16) - ROM_BASE < high:
                sites.append((int(match.group(1), 16) - ROM_BASE, kind, tier))
        if sites:
            out[row[0]] = (sorted(sites), low, high)
        else:
            refused[row] = found
    return out, refused


def webfoot_extent(rom, start):
    import webfoot_lz

    try:
        container = webfoot_lz.validate_retail_termination(rom, start, maximum_output=MAX_OUTPUT)
    except Exception:
        return None
    if container.kind not in webfoot_lz.PACKED_KINDS:
        return None
    return container.kind, container.packed_end


def audio_spans(rom):
    import assetdir_samples

    return [(row["offset"], row["offset"] + row["length"], row["index"])
            for row in assetdir_samples.entries(rom)]


def pointer_words(rom, start, length):
    words = [start + at for at in range((-start) % 4, length - 3, 4)]
    good = 0
    for word in words:
        value = struct.unpack_from("<I", rom, word)[0]
        if ROM_BASE <= value < ROM_BASE + len(rom) or IWRAM[0] <= value < IWRAM[1] \
                or EWRAM[0] <= value < EWRAM[1]:
            good += 1
    return len(words), good


def shape_coverage(rom, row):
    import thumb_bodies

    start, end = row
    at = start
    covered = 0
    while at + 2 <= end:
        got = thumb_bodies.decode(at)
        if got is None:
            at += 2
            continue
        if at + got[0] > end:
            break
        covered += got[0]
        at += got[0]
    return covered / (end - start) if end > start else 0.0


def matches(rom, row, instruments):
    start, length = row
    end = start + length
    body = rom[start:end]
    out = []
    if length >= FILL_MINIMUM and len(set(body)) == 1 and body[0] in FILL_VALUES:
        out.append(("fill/padding",
                    "all %d bytes are 0x%02X (len(set(bytes)) == 1, length >= 4)"
                    % (length, body[0])))
    for low, high in instruments["jcalg1"]:
        if low <= start and end <= high:
            out.append(("JCALG1-compressed",
                        "inside the generated run 0x%06X..0x%06X (build\\jcalg1\\gen_%x.bin)"
                        % (low, high, low)))
    entry = instruments["code"].get(start)
    if entry is not None:
        sites, low, high = entry
        out.append(("code-without-entry",
                    "thumb_bodies.entries() reports %d Thumb control transfer(s) from source into "
                    "the row, first SITE 0x%06X, inside the transcribed code band 0x%06X..0x%06X"
                    % (len(sites), ROM_BASE + sites[0][0], low, high)))
    packed = webfoot_extent(rom, start)
    if packed is not None and packed[1] <= end:
        out.append(("other-compressed",
                    "webfoot_lz.validate_retail_termination(rom, 0x%06X) returns kind %d ending at "
                    "0x%06X, inside the row" % (start, packed[0], packed[1])))
    for low, high, subkind, instrument in instruments["graphics"]:
        if low <= start and end <= high:
            out.append(("graphics",
                        "wholly inside the measured %s block 0x%06X..0x%06X (%s); no parse claims "
                        "the row's own structure" % (subkind, low, high, instrument)))
    words, good = pointer_words(rom, start, length)
    if words >= 2 and good == words:
        out.append(("pointer-tables",
                    "every one of the row's %d four-byte words on the image's own grid is a "
                    "ROM/IWRAM/EWRAM address (%d/%d)" % (words, good, words)))
    kind = instruments["transcribed"].get((start, end))
    if kind == "data":
        out.append(("text/tables",
                    "the row's exact span is a run docs/research/TRANSCRIBED_DATA_RUNS.csv classes "
                    "as `data` (transcribed_data.classify: not a pc-relative pool, not a pointer "
                    "table)"))
    elif kind is not None:
        out.append(("text/tables",
                    "the row's exact span is a run docs/research/TRANSCRIBED_DATA_RUNS.csv classes "
                    "as `%s`, which is text the tree carries as a directive: the recorded rival to "
                    "this row's class" % kind))
    for low, high, index in instruments["audio"]:
        if low <= start and end <= high:
            out.append(("audio",
                        "wholly inside the span record %d of the asset directories names "
                        "(0x%06X..0x%06X, a `data_ptr`+`byte_length` tiling K-226/K-234 measured "
                        "twice)" % (index, low, high)))
    return out


def region_ids():
    out = {"no measured region": "R00"}
    for index, region in enumerate(incbin_census.REGIONS, 1):
        out[region.name] = "R%02d" % index
    return out


def wide_pointer_words(rom, start, length):
    words = [start + at for at in range((-start) % 4, length - 3, 4)]
    good = 0
    for word in words:
        value = struct.unpack_from("<I", rom, word)[0]
        if ROM_BASE <= value < ROM_BASE + len(rom) or IWRAM[0] <= value < IWRAM[1]:
            good += 1
    return length >= 16 and len(words) >= 8 and good * 2 >= len(words)


def measure():
    rom = read_rom()
    tokens = slice_tokens()
    slices = [(start, length) for start, length, _f, _n, _t in tokens]
    census = incbin_census.rows_for(slices, incbin_census.REGIONS)
    ids = region_ids()
    code_rows, code_refused = entry_rows(rom)
    instruments = {
        "jcalg1": jcalg1_spans(),
        "transcribed": transcribed_runs(),
        "graphics": graphics_blocks(),
        "code": code_rows,
        "code_refused": code_refused,
        "audio": audio_spans(rom),
    }
    rows = []
    denominator = "%d rows / %d B" % (len(tokens), sum(token[1] for token in tokens))
    for (start, length, name, line, token), (_s, _l, status, region, _note) in zip(tokens, census):
        found = matches(rom, (start, length), instruments)
        if not found:
            found = [("unknown",
                      "no instrument fired; region `%s` (%s), denominator %s"
                      % (region, status, denominator))]
        chosen = found[0]
        if chosen[0] == "unknown":
            order = found
        else:
            order = sorted(found, key=lambda item: PRIORITY.index(item[0]))
            chosen = order[0]
        others = ["`%s` (%s)" % (kind, predicate.split(";")[0])
                  for kind, predicate in order[1:] if kind != chosen[0]]
        rows.append({
            "file": name, "line": line, "token": token, "start": start, "end": start + length,
            "bytes": length, "region": region, "region_id": ids[region],
            "census_status": status, "class": chosen[0],
            "method": ROUTES[chosen[0]][0], "predicate": chosen[1],
            "alternatives": " ; ".join(others),
            "rivals": tuple(kind for kind, _predicate in order[1:] if kind != chosen[0]),
            "route": ROUTE_TOKENS[chosen[0]],
        })
    controls = {
        "total": sum(row["bytes"] for row in rows),
        "rows": len(rows),
        "jcalg1_runs": len(instruments["jcalg1"]),
        "jcalg1_bytes": sum(end - low for low, end in instruments["jcalg1"]),
        "code_candidates": len(instruments["code"]),
        "code_candidate_bytes": sum(row["bytes"] for row in rows
                                    if row["start"] in instruments["code"]),
        "code_refused": len(instruments["code_refused"]),
        "code_refused_bytes": sum(end - start for start, end in instruments["code_refused"]),
        "code_refused_payload": sum(end - start for start, end in instruments["code_refused"]
                                    if 0x3725C0 <= start and end <= 0x3BB78C),
        "code_also_text": sum(1 for row in rows if row["class"] == "code-without-entry"
                              and "text/tables" in row["rivals"]),
        "coverage": [shape_coverage(rom, (row["start"], row["end"])) for row in rows],
        "uniform_short": sum(1 for row in rows
                             if row["bytes"] < FILL_MINIMUM
                             and len(set(rom[row["start"]:row["end"]])) == 1),
        "alternatives": sum(1 for row in rows if row["alternatives"]),
        "rival_pairs": {},
        "audio_spans": len(instruments["audio"]),
        "audio_bytes": sum(high - low for low, high, _index in instruments["audio"]),
        "wide_pointers": sum(1 for row in rows
                             if wide_pointer_words(rom, row["start"], row["bytes"])),
        "wide_pointer_bytes": sum(row["bytes"] for row in rows
                                  if wide_pointer_words(rom, row["start"], row["bytes"])),
        "region_table": {},
        "fill_values": {},
    }
    for row in rows:
        if row["class"] == "fill/padding":
            value = rom[row["start"]]
            controls["fill_values"][value] = controls["fill_values"].get(value, 0) + 1
        for rival in row["rivals"]:
            key = (row["class"], rival)
            controls["rival_pairs"][key] = controls["rival_pairs"].get(key, 0) + 1
        got = controls["region_table"].setdefault((row["region_id"], row["region"]), [0, 0])
        got[0] += 1
        got[1] += row["bytes"]
    check(rows, controls["total"])
    return rows, controls


def route_probe():
    import itertools
    import subprocess
    import tempfile
    import webfoot_lz

    rows, _controls = measure()
    oracle = os.path.join(ROOT, "tools", "compress", "compress.exe")
    scratch = tempfile.mkdtemp(prefix="raw-remainder-oracle-")
    counter = itertools.count()
    equal = differ = refused = 0
    for row in rows:
        if row["class"] != "other-compressed":
            continue
        start = row["start"]
        try:
            container = webfoot_lz.unpack(read_rom(), start, maximum_output=MAX_OUTPUT)
        except Exception:
            refused += 1
            continue
        stem = os.path.join(scratch, "row%04d" % next(counter))
        with open(stem + ".in", "wb") as handle:
            handle.write(container.data)
        proc = subprocess.run([oracle, stem + ".in", stem + ".out"], capture_output=True)
        if proc.returncode != 0 or not os.path.exists(stem + ".out"):
            refused += 1
            continue
        with open(stem + ".out", "rb") as handle:
            blob = handle.read()
        if blob == read_rom()[start:start + len(blob)]:
            equal += 1
        else:
            differ += 1
        for suffix in (".in", ".out"):
            os.remove(stem + suffix)
    measured = (equal, differ, refused)
    print("route probe other-compressed: byte-exact=%d differ=%d refused=%d (recorded %s)"
          % (measured + (ROUTE_PROBE["other-compressed"],)))
    if measured != ROUTE_PROBE["other-compressed"]:
        raise SystemExit("the other-compressed route probe is %s, not the recorded %s"
                         % (measured, ROUTE_PROBE["other-compressed"]))
    return 0


def totals(rows):
    out = {}
    for row in rows:
        got = out.setdefault(row["class"], [0, 0])
        got[0] += 1
        got[1] += row["bytes"]
    return out


def check(rows, expected=None):
    spans = gate.incbin_ranges()
    want = sum(length for _start, length in spans)
    got = sum(row["bytes"] for row in rows)
    if len(rows) != len(spans):
        raise SystemExit("row count %d is not the slice count %d" % (len(rows), len(spans)))
    if got != want:
        raise SystemExit("class sums %d are not gate.incbin_ranges() %d" % (got, want))
    stray = sorted({row["class"] for row in rows} - set(PRIORITY))
    if stray:
        raise SystemExit("class outside the vocabulary: %s" % stray)
    if expected is not None and expected != got:
        raise SystemExit("recomputed total %d is not the run's %d" % (got, expected))
    return got, want


def csv_text(rows):
    fields = ("file", "line", "token", "start", "end", "bytes", "region", "class", "method",
              "route")
    lines = [",".join(fields)]
    for row in rows:
        cells = []
        for field in fields:
            value = row["region_id"] if field == "region" else row[field]
            if field == "start":
                value = "0x%06X" % value
            elif field == "end":
                value = "0x%06X" % value
            value = str(value)
            if any(ch in value for ch in ',"'):
                value = '"%s"' % value.replace('"', '""')
            cells.append(value)
        lines.append(",".join(cells))
    return "\n".join(lines) + "\n"


def numeric_clause():
    path = os.path.join(ROOT, "docs", "research", "NUMBER_TABLES.csv")
    if not os.path.exists(path):
        return ""
    with open(path, newline="") as handle:
        record = list(csv.DictReader(handle))
    return ("; %d rows / %d B left the class as `docs/research/NUMBER_TABLES.csv` (self-relative "
            "method offsets, consumer 0x080188FC)"
            % (len(record), sum(int(row["bytes"]) for row in record))) if record else ""


def doc_text(rows, controls):
    got = sum(row["bytes"] for row in rows)
    want = sum(length for _start, length in gate.incbin_ranges())
    classes = totals(rows)
    coverage = sorted(controls["coverage"])
    denominator = {
        "fill/padding": "%d rows / %d B; value(s) %s, and %d further uniform rows are shorter than "
                        "%d B so they are 1-2 byte rows and belong to the class their region "
                        "supports"
                        % (classes.get("fill/padding", (0, 0))[0], classes.get("fill/padding", (0, 0))[1],
                           ", ".join("0x%02X in %d row(s)" % (value, count)
                                     for value, count in sorted(controls["fill_values"].items())),
                           controls["uniform_short"], FILL_MINIMUM),
        "JCALG1-compressed": "0 rows / 0 B, at the denominator of all %d rows and of the %d generated "
                             "run(s) (%d B): no INCBIN row overlaps one"
                             % (len(rows), controls["jcalg1_runs"], controls["jcalg1_bytes"]),
        "code-without-entry": "%d rows / %d B, at the denominator of the Thumb entry channel over "
                              "today's %d INCBIN rows and the frozen census; the %d rows whose "
                              "entries are all from sites outside the band (%d B) are NOT counted"
                              % (classes.get("code-without-entry", (0, 0))[0],
                                 classes.get("code-without-entry", (0, 0))[1], len(rows),
                                 controls["code_refused"], controls["code_refused_bytes"]),
        "other-compressed": "%d rows / %d B, at the denominator of all %d rows tested at their own "
                            "start (a second container inside a row is not counted; output ceiling "
                            "0x4000); the 45 rows inside `asset directory 2's bank tail` are the "
                            "census's own 45 kind-1 containers 0x3BBE70..0x3BD2F8, found here by an "
                            "independent walk"
                            % (classes.get("other-compressed", (0, 0))[0],
                               classes.get("other-compressed", (0, 0))[1], len(rows)),
        "graphics": "%d rows / %d B, at the denominator of the four measured blocks (map block, "
                    "sprite block, tilebank tiles, tilebank palette), each with its own constant "
                    "from its own generator module"
                    % (classes.get("graphics", (0, 0))[0], classes.get("graphics", (0, 0))[1]),
        "pointer-tables": "%d rows / %d B under the STRICT predicate (>= 2 grid words, 100%% of them "
                          "ROM/IWRAM/EWRAM addresses), at the denominator of all %d rows. The wider "
                          "density predicate this census measured (>= 16 B, >= 8 grid words, "
                          ">= 50%% addresses) gives %d rows / %d B on the same rows, measured here "
                          "as a control: that is a predicate difference, not an error"
                          % (classes.get("pointer-tables", (0, 0))[0],
                             classes.get("pointer-tables", (0, 0))[1], len(rows),
                             controls["wide_pointers"], controls["wide_pointer_bytes"]),
        "text/tables": "%d rows / %d B, at the denominator of the 2,496-row transcribed census "
                       "(`docs/research/TRANSCRIBED_DATA_RUNS.csv`)%s"
                       % (classes.get("text/tables", (0, 0))[0], classes.get("text/tables", (0, 0))[1],
                          numeric_clause()),
        "audio": "%d rows / %d B, at the denominator of the %d spans (%d B) the two 12-byte "
                 "directories' records name and of all %d rows tested against them; every one of "
                 "those spans is already an emitted run, so the predicate fires on none of them. "
                 "All %d B are source: directory 1 through the mixer's field reads, directory 2 "
                 "through the music record's `+8` reader"
                 % (classes.get("audio", (0, 0))[0], classes.get("audio", (0, 0))[1],
                    controls["audio_spans"], controls["audio_bytes"], len(rows),
                    controls["audio_bytes"]),
        "unknown": "%d rows / %d B, at the denominator of all %d rows: every instrument above fired "
                   "on some other bytes of the same set and none fired here; "
                   "`docs/research/ENDROM_NULL_CENSUS.md` carries a measured reader per row for the "
                   "end-of-ROM regions R20/R21/R23-R31"
                   % (classes.get("unknown", (0, 0))[0], classes.get("unknown", (0, 0))[1], len(rows)),
    }
    lines = []
    add = lines.append
    add("# The route to 100 %: every byte the assembler still INCBINs")
    add("")
    add("Generated by `tools/research/raw_remainder.py` (`python tools/research/raw_remainder.py`).")
    add("One row per INCBIN slice in `docs/research/RAW_REMAINDER.csv` (`%d` data rows), one class per"
        % len(rows))
    add("row, exactly one. The text is a pure function of the retail image and the tracked tree, so")
    add("two runs write byte-identical files. ROM `baserom.gba` sha256 `%s`."
        % incbin_census.ROM_SHA256)
    add("")
    add("**The class sum equals the gate's raw-data total: %d B == %d B (`gate.incbin_ranges()`), the"
        % (got, want))
    add("row count equals the slice count (%d == %d), and `--check` asserts both and writes nothing.**"
        % (len(rows), len(gate.incbin_ranges())))
    add("")
    add("Every one of those slices is assembled (P-644 supersedes P-640; K-229), and the identity")
    add("copies are the only other non-source bytes: `gate.source_bytes()` reports source %d B ="
        % gate.source_bytes())
    add("%.4f %% of the image, with %d B of identity copies taken out on their own line."
        % (100.0 * gate.source_bytes() / gate.ROM_SIZE,
           sum(length for _start, length in gate.union_ranges(gate.identity_ranges()))))
    add("")
    add("Each row's census line, and the document that carries it, is joined in")
    add("`docs/research/RESIDUAL_INDEX.md` (`python tools/research/residual_index.py --check`).")
    add("## The priority order (a row belongs to the first class that fires)")
    add("")
    for number, name in enumerate(PRIORITY, 1):
        add("%d. `%s` - %s" % (number, name, METHOD_TEXT[name]))
    add("")
    add("The priority order decides every row; the per-row class, its method token, its route token")
    add("and its region id are in the CSV, and the classes the order took a row from are tallied in")
    add("`## Rows that more than one predicate matched` below. No byte is in two classes.")
    add("")
    add("| class | rows | bytes | method (instrument and predicate) | route | bytes that route moves |")
    add("|---|---|---|---|---|---|")
    for name in PRIORITY:
        count, size = classes.get(name, (0, 0))
        moves = 0 if ROUTES[name][1] == "NONE" else size
        add("| `%s` | %d | %d | `%s` - %s | `%s` | %d |"
            % (name, count, size, ROUTES[name][0], METHOD_TEXT[name], ROUTES[name][1], moves))
    moved = sum(0 if ROUTES[name][1] == "NONE" else classes.get(name, (0, 0))[1] for name in PRIORITY)
    add("| **total** | **%d** | **%d** | | | **%d** |" % (len(rows), got, moved))
    add("")
    add("The last column is the bytes the route would move toward `source` today: 0 for `NONE`, and")
    add("for a route that does not exist yet (`generator (not yet written for the residual)`) it is")
    add("the bytes that route must eventually move, not bytes any tracked tool moves now.")
    add("")
    add("## The method of every class, and its denominator")
    add("")
    add("A class with no measurement would be `unknown`; each line below names the instrument, so a")
    add("reviewer can re-run it, and the denominator it was measured at.")
    add("")
    for name in PRIORITY:
        count, size = classes.get(name, (0, 0))
        add("### `%s` - %d rows, %d B" % (name, count, size))
        add("")
        add("- Instrument: %s" % METHOD_DETAIL[name])
        add("- Predicate: %s" % METHOD_TEXT[name])
        add("- Route: `%s`. %s" % (ROUTES[name][1], ROUTES[name][2]))
        add("- Denominator: %s." % denominator[name])
        add("")
    if controls["fill_values"]:
        add("The fill class's values: %s."
            % ", ".join("%d row(s) 0x%02X" % (count, value)
                        for value, count in sorted(controls["fill_values"].items())))
        add("%d further row(s) are uniform but shorter than %d B; they are 1-2 byte rows and belong "
            "to the class their region supports, not to the fill class." % (controls["uniform_short"],
                                                                             FILL_MINIMUM))
        add("")
    add("## The residual (`unknown`) and the class that is empty on its own measurement (`audio`)")
    add("")
    count, size = classes.get("unknown", (0, 0))
    add("`unknown`: %d rows / %d B. This is the measurement, not a placeholder: every instrument in"
        % (count, size))
    add("the table fired on some other bytes of the same %d-row set and none of them fired here,"
        % len(rows))
    add("so the denominator that makes these rows unknown is the whole raw-data set.")
    add("")
    add("`audio`: %d rows / %d B. The class has a measured predicate: a row wholly inside a span one"
        % (classes.get("audio", (0, 0))[0], classes.get("audio", (0, 0))[1]))
    add("of the %d records of the two 12-byte asset directories names (`data_ptr` + `byte_length`,"
        % controls["audio_spans"])
    add("an exact tiling measured twice, K-226/K-234). It fires on nothing because every one of the")
    add("%d B those records name is already an emitted run and no raw row lies inside one."
        % controls["audio_bytes"])
    add("Directory 1's 64 records (390,901 B) and directory 2's 79 records (343,010 B) are both")
    add("source through the audio decode route: `tools/mapcontainer/audiodir.py` ties the first to")
    add("the fields the mixer reads and the second to a music record's `+8` read at `0x0803E542`,")
    add("and `assetdirectory.block_blob` emits both from the decoded samples.")
    add("")
    add("The smoothness reading those blocks were measured with is reported, and NOT used as a")
    add("predicate: `assetdir_samples.correlation` on the signed bytes beats the row's own shuffle")
    add("null on most of this residual's bytes, and on a measurable share of the `text/tables` and")
    add("`graphics` bytes too, because the rows it fires on here are sparse runs where the known")
    add("sample blocks carry a broad histogram. It measures sparseness, not samples;")
    add("`docs/research/UNKNOWN_CENSUS.md` carries the per-class shares, the per-region table and")
    add("both nulls.")
    add("")
    add("The largest `unknown` rows, with the census region that carries them:")
    add("")
    add("| range | bytes | region |")
    add("|---|---|---|")
    biggest = sorted((row for row in rows if row["class"] == "unknown"),
                     key=lambda row: -row["bytes"])
    for row in biggest[:12]:
        add("| `0x%06X..0x%06X` | %d | %s |" % (row["start"], row["end"], row["bytes"], row["region"]))
    add("| ... | %d more row(s), %d B | |"
        % (len(biggest) - 12, sum(row["bytes"] for row in biggest[12:])))
    add("")
    add("## The census region of every row (`RAW_REMAINDER.csv` column `region`)")
    add("")
    add("The ids are `incbin_census.REGIONS` in its own priority order, `R00` for a row no region")
    add("covers. The region is the census's cited evidence for the row, not its class.")
    add("")
    add("| id | rows | bytes | region |")
    add("|---|---|---|---|")
    for (region_id, name), (count, size) in sorted(controls["region_table"].items()):
        add("| `%s` | %d | %d | %s |" % (region_id, count, size, name))
    add("")
    add("## Rows that more than one predicate matched")
    add("")
    add("The priority order decides; this is what it took the row from. The CSV cannot carry the")
    add("sentence (the 1 MiB tracked-file lint), so the tally lives here and the per-row class is in")
    add("the CSV.")
    add("")
    add("| class that owns the row | rival class that also matched | rows |")
    add("|---|---|---|")
    for (owner, rival), count in sorted(controls["rival_pairs"].items(),
                                        key=lambda item: -item[1]):
        add("| `%s` | `%s` | %d |" % (owner, rival, count))
    add("")
    add("## Controls: what was measured to decide nothing")
    add("")
    add("- Sequential ARMv4T Thumb decode coverage: median %.2f over all %d rows (min %.2f, "
        "max %.2f)," % (coverage[len(coverage) // 2], len(rows), coverage[0], coverage[-1]))
    add("  and 1.00 on the map block, the end-of-ROM block and the uniform fill rows alike, 0.97 on")
    add("  the 299,468 B asset-directory-3 payload. A byte-shape rule therefore decides nothing here")
    add("  and is not used as a class predicate; the entry reference and the family blocks decide.")
    add("- The JCALG1 channel is a negative at this denominator: %d generated run(s) totalling %d B,"
        % (controls["jcalg1_runs"], controls["jcalg1_bytes"]))
    add("  and none of the %d INCBIN rows lies inside one, so this class moves 0 B." % len(rows))
    add("- The Thumb entry channel reports %d candidate rows (%d B) outside the frozen "
        "`docs/research/ARM_BODIES.csv`"
        % (controls["code_candidates"], controls["code_candidate_bytes"]))
    add("  universe, and %d further row(s) (%d B) whose entries all come from sites OUTSIDE the"
        % (controls["code_refused"], controls["code_refused_bytes"]))
    add("  transcribed code band - the 299,468 B asset-directory-3 payload among them (%d B of those"
        % controls["code_refused_payload"])
    add("  rows are that payload). Those rows stay in the class their own bytes support and are NOT")
    add("  called code: a branch out of a data block decoded as code is not a consumer (P-420).")
    add("- %d of the %d `code-without-entry` rows are ALSO a run `docs/research/TRANSCRIBED_DATA_RUNS"
        % (controls["code_also_text"], classes.get("code-without-entry", (0, 0))[0]))
    add("  .csv` calls `data`, so the transcriber and the entry channel disagree about them; the")
    add("  priority order gives them to `code-without-entry`, the rival tally above keeps the")
    add("  losing class, and 018's byte-exact proof converted 0 of them, so the class is a")
    add("  candidate set and not a proof.")
    add("- %d row(s) matched more than one predicate; the losing class is tallied in "
        "`## Rows that more than" % controls["alternatives"])
    add("  one predicate matched` above, since the CSV is kept small for the 1 MiB tracked-file lint.")
    add("- The `other-compressed` route is MEASURED by `--route-probe`, not proposed: decode the")
    add("  container at the row's start, re-encode its payload with `tools/compress/compress.exe`,")
    add("  compare with the retail bytes. Measured split %d byte-exact / %d differ / %d refused out "
        "of 71," % ROUTE_PROBE["other-compressed"])
    add("  and the flag refuses when that split changes. The byte-exact rows are the 45 kind-1")
    add("  containers 0x3BBE70..0x3BD2F8; for the other 26 the route is a CANDIDATE and the row's")
    add("  class rests on the extent rule alone.")
    add("")
    add("## Route vocabulary, and what is NOT a route")
    add("")
    add("- a byte-exact generator from a build-time extracted input (an emitter that reproduces the")
    add("  retail bytes from the tree's own extracted input),")
    add("- a decoder+encoder pair (both sides measured against the retail bytes),")
    add("- symbolic tables (a tracked table of numbers or pointers, no retail byte payload),")
    add("- NONE (no route found).")
    add("")
    add("A tracked `DCB`/`DCD` dump of retail bytes is NOT a route: it is the raw-data class itself,")
    add("and this project forbids ROM bytes in any tracked file.")
    add("")
    add("## Re-run")
    add("")
    add("    python tools\\research\\raw_remainder.py")
    add("    python tools\\research\\raw_remainder.py --check")
    add("    python tools\\research\\raw_remainder.py --route-probe")
    add("")
    return "\n".join(lines) + "\n"


def band_table():
    out = {}
    for name, ticket in BAND_TICKETS:
        path = os.path.join(ROOT, "docs", "research", name)
        if not os.path.exists(path):
            continue
        with open(path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                out[(int(row["start"], 16), int(row["end"], 16))] = (row["class"], row["proof"],
                                                                     ticket)
    return out


def citation_table():
    import citations_in_source

    rows, _classes, _recorded = citations_in_source.measure()
    return {start: (got, first) for start, _length, got, _routes, first, _klass in rows}


def recorded_table():
    import citations_in_source
    import emitted

    out = {}
    for (start, _end), text in emitted.carrier_comments(ROOT).items():
        forms = citations_in_source.comment_forms(text)
        if forms["recorded"]:
            out[start] = forms["field_site"]
    return out


def cause_table(rom):
    import residual_causes

    rows, cause_of = residual_causes.measured(rom)
    return {start: cause_of(start) for start, _end in rows}


def status_of(row, fence, cite):
    if fence[0] <= row["start"] and row["end"] <= fence[1]:
        return "in progress"
    if cite is not None and cite[0] == "runtime-cited":
        return "runtime-pending"
    if row["region_id"] in IDENTIFIED_REGIONS:
        return "identified binary"
    return "unmapped"


def reference_cell(cite, recorded):
    if cite is not None and cite[0] == "cited":
        return "code:0x%08X" % (ROM_BASE + cite[1])
    if cite is not None and cite[0] == "runtime-cited":
        return "runtime"
    if recorded is not None:
        return "data:0x%08X" % (ROM_BASE + recorded)
    return "none"


def consumer_cell(row, band, cause):
    if cause is not None:
        return "map:" + cause
    if band is not None:
        return "band:" + band[0]
    if row["class"] == "graphics":
        return "sprite:0x0800EF94"
    return "none"


def unattempted_cells(path=None):
    path = path or os.path.join(ROOT, "docs", "research", "UNATTEMPTED_ROWS.csv")
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            out[(int(row["start"], 16), int(row["end"], 16))] = row["result"]
    return out


def attempts_cell(status, row, band, unattempted=None):
    if unattempted and (row["start"], row["end"]) in unattempted:
        return "UNATTEMPTED-001:%s" % unattempted[(row["start"], row["end"])]
    if status in ATTEMPTS:
        return ATTEMPTS[status]
    if band is not None:
        return "%s:%s" % (band[2], band[0])
    return CLASS_ATTEMPTS.get(row["class"], "none")


def ledger(rows, rom, raw=None):
    import generate_mapcontainer

    generate_mapcontainer.set_block("map")
    fence = (generate_mapcontainer.MAP.start, generate_mapcontainer.MAP.end)
    bands = band_table()
    cites = citation_table()
    recorded = recorded_table()
    causes = cause_table(rom)
    unattempted = unattempted_cells()
    out = []
    for row in rows:
        band = bands.get((row["start"], row["end"]))
        cite = cites.get(row["start"])
        status = status_of(row, fence, cite)
        out.append({
            "start": row["start"], "end": row["end"], "bytes": row["bytes"],
            "region": row["region_id"], "route": row["route"],
            "references": reference_cell(cite, recorded.get(row["start"])),
            "consumer": consumer_cell(row, band, causes.get(row["start"])),
            "attempts": attempts_cell(status, row, band, unattempted),
            "status": status,
        })
    ledger_check(out, rows, raw)
    return out


def ledger_check(rows, census, raw=None):
    want = sorted((row["start"], row["end"], row["bytes"]) for row in census)
    got = sorted((row["start"], row["end"], row["bytes"]) for row in rows)
    if got != want:
        raise SystemExit("the ledger's intervals are not the census's: %d missing, %d extra"
                         % (len(set(want) - set(got)), len(set(got) - set(want))))
    total = sum(row["bytes"] for row in rows)
    expected = raw if raw is not None else sum(length for _start, length in gate.incbin_ranges())
    if total != expected:
        raise SystemExit("the ledger's bytes sum to %d, not the raw-data total %d"
                         % (total, expected))
    for row in rows:
        if row["status"] not in STATUSES:
            raise SystemExit("the row 0x%06X has status %r, not one of %s"
                             % (row["start"], row["status"], ", ".join(STATUSES)))
        if not row["route"] or not row["attempts"]:
            raise SystemExit("the row 0x%06X is unrouted" % row["start"])
    return total


def tally_status(rows):
    out = {name: [0, 0] for name in STATUSES}
    for row in rows:
        out[row["status"]][0] += 1
        out[row["status"]][1] += row["bytes"]
    return out


def owner_line(rows=None):
    if rows is None:
        rows = ledger(measure()[0], read_rom())
    share = tally_status(rows)
    source = gate.source_bytes()
    return ("source=%d of %d (%.4f %%); identified binary=%d of %d (%.4f %%); "
            "runtime-pending=%d; in-progress=%d; unmapped=%d"
            % (source, gate.ROM_SIZE, 100.0 * source / gate.ROM_SIZE,
               share["identified binary"][1], gate.ROM_SIZE,
               100.0 * share["identified binary"][1] / gate.ROM_SIZE,
               share["runtime-pending"][1], share["in progress"][1], share["unmapped"][1]))


def doc_source(text):
    found = re.search(r"source=(\d+) of %d" % gate.ROM_SIZE, text)
    if not found:
        raise SystemExit("the ledger's owner line states no source total")
    return int(found.group(1))


def ledger_csv_text(rows):
    lines = [",".join(LEDGER_FIELDS)]
    for row in rows:
        cells = []
        for field in LEDGER_FIELDS:
            value = row[field]
            if field in ("start", "end"):
                value = "0x%06X" % value
            value = str(value)
            if any(ch in value for ch in ',"'):
                value = '"%s"' % value.replace('"', '""')
            cells.append(value)
        lines.append(",".join(cells))
    return "\n".join(lines) + "\n"


def ledger_doc_text(rows):
    share = tally_status(rows)
    total = sum(row["bytes"] for row in rows)
    names = {value: key for key, value in region_ids().items()}
    by_region = {}
    for row in rows:
        got = by_region.setdefault(row["region"], {name: [0, 0] for name in STATUSES})
        got[row["status"]][0] += 1
        got[row["status"]][1] += row["bytes"]
    references, consumers, attempts = {}, {}, {}
    for row in rows:
        for tally, key in ((references, row["references"].split(":")[0]),
                           (consumers, row["consumer"].split(":")[0]),
                           (attempts, row["attempts"])):
            tally[key] = tally.get(key, 0) + row["bytes"]
    lines = ["# The residual ledger: every remaining raw interval, its evidence and its status",
             "",
             "Generated by `tools/research/raw_remainder.py` "
             "(`python tools/research/raw_remainder.py`); `--check` asserts and writes nothing. One",
             "row per `docs/research/RAW_REMAINDER.csv` row in `RESIDUAL_LEDGER.csv`, plus this",
             "summary. Every cell comes from a tracked instrument's own output or from a cited",
             "ticket: no byte is converted here and no interval is re-measured.",
             "",
             "**The ledger holds %d rows / %d B, which is the gate's raw-data total, and `--check`"
             % (len(rows), total),
             "refuses a missing, doubled or unrouted interval.**",
             "",
             "## The two-number report",
             "",
             "    " + owner_line(rows),
             "",
             "## Status",
             "",
             "| status | rows | bytes | what it states |",
             "|---|---|---|---|",
             "| `identified binary` | %d | %d | the region is mapped and no format beats its null "
             "(an identity copy is not counted as source) |"
             % (share["identified binary"][0], share["identified binary"][1]),
             "| `runtime-pending` | %d | %d | only a runtime session has cited the byte; a "
             "static channel reaches no code site |"
             % (share["runtime-pending"][0], share["runtime-pending"][1]),
             "| `in progress` | %d | %d | a running ticket owns the bytes (the map block's tail) |"
             % (share["in progress"][0], share["in progress"][1]),
             "| `unmapped` | %d | %d | no region has been mapped to a null yet |"
             % (share["unmapped"][0], share["unmapped"][1]),
             "",
             "The precedence is `in progress` > `runtime-pending` > `identified binary` > "
             "`unmapped`: a row inside the running ticket's block is",
             "`in progress` even when a citation also calls it runtime-read, and a runtime-cited row",
             "inside an identified region is `runtime-pending`. No row is counted twice, so the",
             "four rows above sum to the raw-data total.",
             "",
             "## Per region",
             "",
             "| region | rows | bytes | statuses (rows / bytes) | region name |",
             "|---|---|---|---|---|",
             ]
    for region in sorted(by_region, key=lambda name: int(name[1:])):
        got = by_region[region]
        counted = sum(value[1] for value in got.values())
        lines.append("| `%s` | %d | %d | %s | %s |"
                     % (region, sum(value[0] for value in got.values()), counted,
                        ", ".join("`%s` %d/%d" % (name, got[name][0], got[name][1])
                                  for name in STATUSES if got[name][0]),
                        names.get(region, "no measured region")))
    lines += ["",
              "## The evidence columns",
              "",
              "`region` and `route` are the census row's own (its cited region id and its class's",
              "route token). `references` is the row's strongest measured citation: a ledger code",
              "site (`code:<ROM address>`, `citations_in_source` channels P and A), a runtime read",
              "(`runtime`, the carrier comment's `cited by runtime read`), a data-stated site",
              "(`data:<ROM address>`, the MapEntry +0x30 field a carrier comment records, P-453), or",
              "`none`. `consumer` is the row's measured consumer evidence: the map block's per-row",
              "cause (`residual_causes`, T-190), a code-band verdict (`band:<class>`, T-192), the",
              "sprite block's stride site, or `none`. `attempts` is the ticket that touched the row",
              "and the null it measured; the legend is below.",
              "",
              "| attempts token | the ticket and the null it measured |",
              "|---|---|",
              ]
    legend = {
        "GRAPHICS-RESIDUAL-002:null": "the map block's per-byte causes; the residual's emitter does "
                                      "not exist (T-190)",
        "GRAPHICS-RESIDUAL-003:residual": "the causes re-taken after a conversion removed one "
                                          "operand (T-196)",
        "GRAPHICS-RESIDUAL-004:open@tail": "the running ticket: the map block 0x179A50..0x2B8BC8 "
                                           "is the map-block ticket's",
        "END-ROM-RECON-001:no-format-beats-null": "11 worked regions, the kind-0 candidate cover "
                                                  "measured against a per-row shuffle null",
        "citations_in_source:no-code-site": "no pc-relative site reaches the byte; the runtime class "
                                            "is a comment rule, not an observation (T-178)",
        "RUNTIME-CONSUMER-002:read": "the rule that a read observed at pc plus the exact address "
                                     "is a citation; the rows wait for one runtime session",
        "CODE-BAND-002:pool-data": "the pool citation, and the kind-0 grid control that measured "
                                   "0 of 16 at grids 0-3",
        "CODE-BAND-002:unreached": "no entry proof reaches the row",
        "CODE-BAND-002:method-target": "a class-table method target reaches the row",
        "CODE-BAND-002:source-entry": "a source branch or pointer reaches the row",
        "CODE-BAND-002:transitive": "a transitive walk reaches the row",
        "CODE-BAND-003:unreached": "R19's 574 rows measured data, no byte consumer",
        "CODE-BAND-004:unreached": "the R32 remainder no entry instrument reaches",
        "CODE-BAND-004:pool-data": "the pool citation, with its grid control negative",
        "CODE-BAND-004:method-target": "a class-table method target reaches the row",
        "CODE-BAND-004:source-entry": "a source branch or pointer reaches the row",
        "CODE-BAND-004:prologue-entry": "the `PUSH {..,lr}` shape, the weakest class (18 of 51 "
                                        "sites against the permutation's 4 of 66)",
        "CODE-BAND-004:transitive": "a transitive walk reaches the row",
        "CODE-ENTRY-001:9-row-boundary-fragments": "556 of 565 rows reassembled byte-exact; the "
                                                   "fragments left are halves of one instruction, and "
                                                   "the whole spans wait on an entry that is not "
                                                   "chance-level",
        "GEN-COMPRESSED-001:tokenization-differs": "the payload decodes identically and the tree's "
                                                   "encoder emits a different tokenization",
        "PTR-TABLE-001:unnamed-word": "a grid word lies in a carrier with no label at it",
        "PTR-WORDS-002:no-family": "31 outside rows, no proven pointer-word family",
        "PATH-100-016:data-run-unconverted": "the run is a transcribed-data run, not yet re-emitted "
                                             "as directives",
        "UNATTEMPTED-001:no-entry": "no entry instrument reaches the row (T-206, "
                                    "tools/research/unattempted.py)",
        "UNATTEMPTED-001:converted": "a Thumb branch out of converted source, converted byte-exact",
        "walk-returns": "the Thumb walk from the row's start ends in a return, and the row's own "
                        "bytes permuted returns in fewer rows (T-206's null)",
        "word-named": "a 4-byte word of the image names the row (577 hits against 658.5 expected, "
                      "so the count is not the evidence; the site is)",
        "text-record-table": "text_tables.classify reads the row as a record table",
        "container": "a PACKED container starts at the row start; the row permuted fails",
        "jcalg1": "a row-bounded JCALG1 probe terminates inside the row (0 rows fire)",
        "ptrtable": "every grid word is an address (the strict pointer-table predicate; 0 rows fire)",
        "arm_branch": "a branch out of a converted ARM body reaches the row (0 rows fire)",
        "none": "no instrument fired, and no ticket has claimed the row",
    }
    for token in sorted(attempts):
        lines.append("| `%s` | %s |"
                     % (token, " ".join(legend.get(part, "no legend") for part in token.split(";"))))
    lines += ["",
              "## Controls",
              "",
              "| references | bytes |",
              "|---|---|"]
    for token in sorted(references):
        lines.append("| `%s` | %d |" % (token, references[token]))
    lines += ["",
              "| consumer | bytes |",
              "|---|---|"]
    for token in sorted(consumers):
        lines.append("| `%s` | %d |" % (token, consumers[token]))
    cross = {}
    for row in rows:
        key = (row["status"], row["references"].split(":")[0])
        cross[key] = cross.get(key, 0) + row["bytes"]
    lines += ["",
              "## What each status still knows: the references of its rows",
              "",
              "`unmapped` states that no region is mapped to a null, never that nothing is known: a",
              "row below carries a measured reference and still has no format and no owning ticket.",
              "",
              "| status | references | bytes |",
              "|---|---|---|"]
    for status in STATUSES:
        for prefix in sorted({key[1] for key in cross if key[0] == status}):
            lines.append("| `%s` | `%s` | %d |" % (status, prefix, cross[(status, prefix)]))
    lines += ["",
              "## Re-run",
              "",
              "    python tools\\research\\raw_remainder.py",
              "    python tools\\research\\raw_remainder.py --check",
              ""]
    return "\n".join(lines) + "\n"


def main(argv):
    if "--route-probe" in argv:
        return route_probe()
    rows, controls = measure()
    check(rows, controls["total"])
    classes = totals(rows)
    text = doc_text(rows, controls)
    blob = csv_text(rows)
    blocks = ledger(rows, read_rom(), controls["total"])
    ledger_blob = ledger_csv_text(blocks)
    ledger_text = ledger_doc_text(blocks)
    for name in PRIORITY:
        count, size = classes.get(name, (0, 0))
        print("%-20s %5d row(s) %8d B" % (name, count, size))
    print("total %d row(s) %d B  gate raw-data %d B  EXACT"
          % (len(rows), sum(row["bytes"] for row in rows),
             sum(length for _start, length in gate.incbin_ranges())))
    for name, (count, size) in tally_status(blocks).items():
        print("ledger %-18s %5d row(s) %8d B" % (name, count, size))
    print(owner_line(blocks))
    print("csv sha256=%s" % hashlib.sha256(blob.encode()).hexdigest())
    print("doc sha256=%s" % hashlib.sha256(text.encode()).hexdigest())
    print("ledger csv sha256=%s" % hashlib.sha256(ledger_blob.encode()).hexdigest())
    print("ledger doc sha256=%s" % hashlib.sha256(ledger_text.encode()).hexdigest())
    if "--check" in argv:
        print("check only: nothing written")
        return 0
    for path, content in ((CSV_OUT, blob), (DOC_OUT, text), (LEDGER_OUT, ledger_blob),
                          (LEDGER_DOC, ledger_text)):
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    print("wrote %s (%d B), %s (%d B), %s (%d B) and %s (%d B)"
          % (os.path.relpath(CSV_OUT, ROOT), len(blob), os.path.relpath(DOC_OUT, ROOT), len(text),
             os.path.relpath(LEDGER_OUT, ROOT), len(ledger_blob),
             os.path.relpath(LEDGER_DOC, ROOT), len(ledger_text)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
