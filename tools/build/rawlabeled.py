"""Carry the census's promoted runs as LABELED RAW DATA whose bytes come from the retail image.

R-RAW-001 promotes a run that has a cited consumer but no code-derived extent. The bytes are raw
data and no structure is claimed, so the promotion is only honest if the source says which consumer
cites which address and carries the bytes unchanged. PATH-100-015 changes HOW the bytes are carried:

- a fragment is still one INCLUDEd file per run, still split at every cited base (or at the caller's
  explicit citation list, or at a data-stated boundary) into `unk_<ROMADDR>` symbols with their
  citation comments, strides and shapes;
- each symbol's bytes are now ONE `INCBIN` of a build-time extracted slice of baserom.gba -
  `baserom.gba_0x<start>_0x<end>.extracted`, the same mechanism the tree's other retail spans use -
  instead of tracked `DCB`/`DCW`/`DCD` text. No retail byte payload is tracked any more, and
  `gate.incbin_ranges()` counts every one of those bytes as raw data.

`--extract` is the writer of every slice a fragment names (P-436: a name the source mentions needs a
writer, and `tools/extract.cmd` is where a fresh tree gets its retail-derived inputs). It runs before
the gate's cold purge, so `--cold` regenerates them like every other extracted input.

    python tools/build/rawlabeled.py --extract
    python tools/build/rawlabeled.py --convert
    python tools/build/rawlabeled.py --name-rows
    python tools/build/rawlabeled.py --check

    python tools/build/rawlabeled.py --rom baserom.gba --range 0x76CCE4 0x77AE68 \
        --out asm/rawlabeled_76cce4.s
    python tools/build/rawlabeled.py --structured --rom baserom.gba \
        --out asm/rawlabeled_71c90.s --apply-source
    python tools/build/rawlabeled.py --rom baserom.gba --range 0x19C744 0x19C8A8 \
        --citations build/explicit.txt --ticket PATH-100-012 --doc docs/ASM_INDEX.md \
        --out asm/rawlabeled_19c744.s --apply-source
    python tools/build/rawlabeled.py --raw-label --rom baserom.gba

The loader channel is T-146's sweep, so a site whose own address lies inside the run is data and not
a citation (P-420). `--raw-label` carries the two runs PATH-100-001 promoted; its citation channel is
`code_xref.loads_into`, the pc-relative VALUE channel, one level past the pool word a site computes
(P-422). The split contract has TWO sources of interior boundaries - a cited base inside the run and
a listed data-stated boundary - so a fragment with an empty citation set is legitimate (P-457).
"""

from __future__ import annotations

import argparse
import bisect
import os
import re
import sys
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "research"))
sys.path.insert(0, os.path.join(ROOT, "tools", "structured"))

import emitted  # noqa: E402
import loader_access_trace as trace  # noqa: E402
import families  # noqa: E402

ROM_BASE = 0x08000000
TRACKED_TEXT_CEILING = 1024 * 1024
TICKET = "PATH-100-005"
DOC = "docs/ASM_INDEX.md"
SCRIPT_FIELD = 21
SCRIPT_READER = "0x08008CEE ldr r1,[r0,#0x30] -> bl 0x08004038 (the opcode interpreter)"
TOKEN = re.compile(r"^(\s*)INCBIN\s+(\S+)\s*$")
EXPLICIT_CHANNEL = "; citation channel: an explicit citation set (--citations), not the loader channel"
RANGED = (re.compile(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted$"),
          re.compile(r"_([0-9a-fA-F]{1,8})_([0-9a-fA-F]{1,8})\.bin$"))
LABEL = re.compile(r"^\s*(?:\|(unk_[0-9A-Fa-f]{8})\||(unk_[0-9A-Fa-f]{8}))\s*$")
EXPORT = re.compile(r"^\s*EXPORT\s+\|unk_[0-9A-Fa-f]+\|\s*$")
STRIDES = {
    0x3BB78C: ("20", "0x080008BE lsls r3,r1,#2; adds r1,r3,r1; lsls r1,r1,#2 -> 20*N"),
    0x3BD2F8: ("52", "0x0800D2F8 / 0x0802BCD2 muls r0,r3,r0 with r3=0x34 -> 52*N, then +0xC"),
    0x71DDC8: ("12", "0x0801A904 lsls r3,r0,#1; adds r0,r3,r0; lsls r0,r0,#2 -> 12*N"),
    0x75043C: ("36", "0x0802A37A lsls r1,r0,#3; adds r1,r1,r0; lsls r1,r1,#2 -> 36*N"),
    0x77B200: ("12", "0x0803C0EA lsls r3,r0,#1; adds r0,r3,r0; lsls r0,r0,#2 -> 12*N"),
    0x77B254: ("12", "0x0803C206 lsls r3,r0,#1; adds r0,r3,r0; lsls r0,r0,#2 -> 12*N"),
    0x77B2A8: ("12", "0x0803C31E lsls r3,r0,#1; adds r0,r3,r0; lsls r0,r0,#2 -> 12*N"),
    0x76E264: ("36", "0x08038458 lsls r1,r0,#3; adds r1,r1,r0; lsls r1,r1,#2 -> 36*N"),
    0x76DFF8: ("48", "0x08037F24 lsls r1,r0,#1; adds r1,r1,r0; lsls r1,r1,#4 -> 48*N"),
    0x770CF4: ("4", "0x08038826/0x08038918 lsls r1,r1,#2; adds r1,r1,r2 -> 4*N"),
    0x77ADD8: ("4", "0x080391C0/0x080391D0 lsls r1,r1,#2; ldr r1,[r2,r1] -> 4*N"),
}
SHAPES = {
    0x3BB78C: "53 x 20 B records: +0/+4 ascending ROM addresses inside the directory-3 payload "
              "(0836E160 / 0836D54E first, 083BB77C / 083BB108 last), +8 = 0836D18C and +0xC = "
              "0836D540 in all 53, +0x10 a count 0x341..0x880. FOUR code sites name this base "
              "(0x080008BC, 0x080041BA, 0x080053F8, 0x08008C86), each computing base + 20*index and "
              "handing the record to 0x0803F110, which reads only the record's +0x10 and +0x11: no "
              "site loads +0 or +4, so the payload those two words name has no code consumer",
    0x3BD2F8: "83 x 52 B records: +0x18 and +0x28 a container address of the chain, +0x30 an "
              "address in 083BBBB0..083BBE70 (23 records) or zero (60), the rest halfword counts and "
              "packed ids. SIXTEEN code sites name this base; the two decoded here "
              "(0x0800D2F4-0x0800D2FE, 0x0802BCCE-0x0802BCD6) scale the index by 0x34 and add +0xC. "
              "The range 083BBBB0..083BBE70 those +0x30 words name is NOT carried: it is its own "
              "census row, no consumer names it, so it stays retail",
    0x76DFF8: "12-byte K-089 piece records, +8 a ROM container pointer (0876CD38, then 0876CD78)",
    0x76E264: "12-byte K-089 piece records, +8 a ROM container pointer (0876E1A4, then 0876E1E4)",
    0x770CF4: "12-byte K-089 piece records, +8 a ROM container pointer (0876E2F4, then 0876E6F4)",
    0x71E984: "12-byte K-089 piece records, +8 a ROM container pointer (0871E684, 0871E784, 0x100 "
              "apart)",
    0x76E0B8: "IWRAM-pointer descriptor block (03003898, 03001C4C, 030019A4, 00000000 ... 000000F0)",
    0x76E0DC: "IWRAM-pointer descriptor block (03001C4C, 030019A4, 00000000 ...)",
    0x71E9A8: "IWRAM-pointer descriptor block (03003300, 03003898, 0807012C, 03001068 ... 00000012)",
    0x71E9D8: "IWRAM-pointer descriptor block (03003300, 03003898, 0807012C, 03001068 ...)",
    0x725048: "IWRAM-pointer descriptor block (03003898, 03001C4C, 030019A4, 00000000 ... 000000F0)",
    0x72A6B4: "IWRAM-pointer descriptor block (03003300, 03003898, 03004A8C, 03001C4C ... 00000078)",
    0x72A6F8: "IWRAM-pointer descriptor block (03003300, 03001C4C, 03002A64, 00000000 ...)",
    0x72BFA4: "IWRAM-pointer descriptor block (03004A8C, 03003898, 03004A8C, 0807012C ...)",
    0x72BFA8: "IWRAM-pointer descriptor block (03003898, 03004A8C, 0807012C, 03001068 ... 00003A98)",
    0x77ADD8: "a table of IWRAM addresses (03001B0C, 03001B58, ...), read as 4*N by 0x080391C0",
    0x77AE38: "32 bytes read whole by 0x08039290-0x080392A2: code pointers and counts (0800FD55, "
              "0000000D, 0000002C, 080555A0, 00000001, 080716EC)",
    0x77AE58: "16 bytes read whole by 0x0803928E: four halfword pairs (000C0008, FFF40008, "
              "0008FFF4, 0008000C)",
}
Run = namedtuple("Run", "file start end shape")
RUNS = (
    Run("raw_labeled_74d248.s", 0x74D248, 0x74F058,
        "container-rich run 0x74D248..0x74F058; the pointers are named, the family layout is NOT"
        " ESTABLISHED"),
    Run("raw_labeled_7b5b64.s", 0x7B5B64, 0x7B79A4,
        "dialogue container table 0x7B5B64 and the heterogeneous run it heads; the family layout is"
        " NOT ESTABLISHED"),
)
CITED_SHOWN = 3
HEADER = re.compile(r"^; (?:([A-Z][A-Z0-9-]+) / R-RAW-001: the (census run|structured block's"
                    r" retail gaps) 0x([0-9a-fA-F]+)\.\.0x([0-9a-fA-F]+) as LABELED RAW DATA"
                    r"|R-RAW-001 raw-labeled: (.*))\.?$")
STALE_HEADER = ("gate.incbin_ranges()", "tools/incbin.bat", "NEVER named here",
                "Generated by tools/research/raw_labeled.py", "appeared in a comment (P-430)",
                "One symbol per cited base", "this file, because gate.incbin_ranges()",
                "carried as DCD words", "tracked-file ceiling", "The gap bytes are data directives",
                "from baserom.gba itself", "the bytes come from the run's EXTRACTED PAYLOAD",
                "Round trip and the run's own record")
KEEP_HEADER = re.compile(r"^; (?:[A-Z][A-Z0-9-]+ / R-RAW-001:|R-RAW-001 raw-labeled:|Citations|"
                         r"Round trip|Citations, strides)")
_SITES = None


def slice_name(start: int, end: int) -> str:
    return "baserom.gba_0x%x_0x%x.extracted" % (start, end)


def token_span(token: str):
    for pattern in RANGED:
        found = pattern.search(token)
        if found:
            return int(found.group(1), 16), int(found.group(2), 16)
    return None


def citations(rom: bytes, start: int, end: int) -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    for entry in trace.trace(rom, start, end)["literals"]:
        base = entry["target"]
        sites = [site for site in entry["sites"] if not (start <= site["site"] < end)]
        if not (start <= base < end) or not sites:
            continue
        listed = sites[:4]
        out[base] = ["0x%08X%s"
                     % (site["site"] + ROM_BASE,
                        "".join(" %s" % access.split(" = ")[0]
                                for access in list(dict.fromkeys(site["accesses"]))[:4]))
                     for site in listed]
        if len(sites) > len(listed):
            out[base][-1] += " (+%d more sites)" % (len(sites) - len(listed))
    return out


def explicit_citations(path: str, start: int, end: int) -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        head, _, comment = line.partition(" ")
        base = int(head, 16)
        if start <= base < end:
            out.setdefault(base, []).append(comment.strip())
    return out


def boundaries(path: str = None) -> list[int]:
    if path is None:
        return []
    out = []
    for line in open(path):
        line = line.split(";", 1)[0].strip()
        if line:
            out.append(int(line, 16))
    return out


def symbols(rom: bytes, start: int, end: int, cited: dict[int, list[str]], extra=()) -> list[dict]:
    source = rom
    bounds = sorted({start} | {base for base in list(cited) + list(extra) if start <= base < end})
    rows = []
    for index, base in enumerate(bounds):
        stop = bounds[index + 1] if index + 1 < len(bounds) else end
        rows.append({"base": base, "size": stop - base,
                     "data": source[base:stop], "citations": cited.get(base, [])})
    return rows


def assert_symbols(rows: list[dict], start: int, end: int, cited: dict[int, list[str]],
                   extra=()) -> int:
    if not rows or rows[0]["base"] != start:
        raise ValueError("symbols start at %s, the run starts at %#x"
                         % (rows[0]["base"] if rows else None, start))
    allowed = {start} | set(cited) | set(extra)
    for row in rows:
        if row["base"] not in allowed:
            raise ValueError("symbol %#x is not the run start and is not a cited base" % row["base"])
        if row["size"] <= 0:
            raise ValueError("symbol %#x has size %d" % (row["base"], row["size"]))
    for row, following in zip(rows, rows[1:]):
        if row["base"] + row["size"] != following["base"]:
            raise ValueError("symbol %#x ends at %#x, the next starts at %#x"
                             % (row["base"], row["base"] + row["size"], following["base"]))
    if rows[-1]["base"] + rows[-1]["size"] != end:
        raise ValueError("the last symbol ends at %#x, the run ends at %#x"
                         % (rows[-1]["base"] + rows[-1]["size"], end))
    for row in rows:
        if len(row["data"]) != row["size"]:
            raise ValueError("symbol %#x carries %d bytes, its extent says %d"
                             % (row["base"], len(row["data"]), row["size"]))
    return sum(row["size"] for row in rows)


def directives(start: int, data: bytes) -> list[str]:
    if not data:
        raise ValueError("%#x carries no byte to name" % start)
    return ["\tINCBIN\t%s" % slice_name(start, start + len(data))]


def label_offset(found) -> int:
    return int((found.group(1) or found.group(2))[4:], 16) - ROM_BASE


def blocks(text: str) -> list[tuple[int, int, str]]:
    return [(start, end, token) for start, end, token, _ in emitted.fragment_symbols(text)]


def slice_bytes(root: str, token: str) -> bytes:
    path = os.path.join(root, token)
    if not os.path.exists(path):
        raise ValueError("%s is missing; run rawlabeled.py --extract (tools/extract.cmd)" % token)
    return open(path, "rb").read()


def compare_bytes(got: bytes, want: bytes, token: str, base: int) -> None:
    if got == want:
        return
    for index, (left, right) in enumerate(zip(got, want)):
        if left != right:
            raise ValueError("byte %#x differs: %#04x in %s, %#04x in the image"
                             % (ROM_BASE + base + index, left, token, right))
    raise ValueError("%s carries %d bytes, the image's range carries %d"
                     % (token, len(got), len(want)))


def verify(rom: bytes, start: int, end: int, text: str, root: str = ROOT) -> int:
    rows = blocks(text)
    if not rows or rows[0][0] != start:
        raise ValueError("the text starts at %s, the run starts at %#x"
                         % (rows[0][0] if rows else None, start))
    total = 0
    for address, stop, token in rows:
        if address != start + total:
            raise ValueError("%s starts at %#x, the run's next byte is %#x"
                             % (token, address, start + total))
        compare_bytes(slice_bytes(root, token), rom[address:stop], token, address)
        total += stop - address
    if total != end - start:
        raise ValueError("the text carries %d bytes, the run carries %d" % (total, end - start))
    return total


def tiled(rows, start: int, end: int) -> bool:
    cursor = start
    for address, stop, _token in rows:
        if address != cursor or stop <= address:
            return False
        cursor = stop
    return bool(rows) and cursor == end


def verify_blocks(rom: bytes, rows, what: str, root: str = ROOT) -> int:
    total = 0
    for address, stop, token in rows:
        if stop <= address:
            raise ValueError("%s: %#x carries no byte" % (what, address))
        compare_bytes(slice_bytes(root, token), rom[address:stop], token, address)
        total += stop - address
    return total


def symbol_text(lines: list[str], base: int, data: bytes, citations: list[str],
                boundary: str) -> None:
    name = "|unk_%08X|" % (ROM_BASE + base)
    lines.append("\tEXPORT\t%s" % name)
    lines.append(name)
    if citations:
        lines.append("; cited by %s" % ", ".join(citations))
    else:
        lines.append("; no citation: %s" % boundary)
    lines.append("")
    lines += directives(base, data)


def emit(rom: bytes, start: int, end: int, extra=(), ticket: str = TICKET, doc: str = DOC,
         cited: dict[int, list[str]] = None) -> str:
    explicit = citations(rom, start, end) if cited is None else cited
    rows = symbols(rom, start, end, explicit, extra)
    total = assert_symbols(rows, start, end, explicit, extra)
    out = ["; %s / R-RAW-001: the census run %#010x..%#010x as LABELED RAW DATA." %
           (ticket, ROM_BASE + start, ROM_BASE + end)]
    if cited is not None:
        out.append(EXPLICIT_CHANNEL)
    out.append("")
    for row in rows:
        symbol_text(out, row["base"], row["data"], row["citations"],
                    "a data-stated boundary (--boundaries)" if row["base"] in extra
                    else "the run's first byte, a label boundary only")
    assert sum(row["size"] for row in rows) == total
    return "\n".join(out)


def split_of(start: int, end: int, cited: dict[int, list[str]]) -> list[int]:
    return sorted({start} | {base for base in cited if start <= base < end})


def region_a_sections(plan) -> list[tuple[str, int, int]]:
    sections = [("generated", start, end) for start, end in plan.runs
                if start < families.REGION_A[1]]
    sections += [("gap", start, end) for start, end in plan.gaps]
    return sorted(sections, key=lambda row: row[1])


def gen_name(start: int, end: int) -> str:
    return "build\\structured\\gen_%x_%x.bin" % (start, end)


def field_citations(rom: bytes, stretches) -> tuple[dict[int, list[str]], int, int]:
    starts = [low for low, _ in stretches]
    out: dict[int, list[str]] = {}
    sites = 0
    rows = families.map_entries(rom)
    for offset, entry in rows:
        value = entry.fields[SCRIPT_FIELD]
        if not ROM_BASE <= value < ROM_BASE + len(rom):
            continue
        target = value - ROM_BASE
        where = bisect.bisect_right(starts, target) - 1
        if where < 0 or not (stretches[where][0] <= target < stretches[where][1]):
            continue
        sites += 1
        out.setdefault(target, []).append("entry at file 0x%06X, field +0x30; %s"
                                          % (offset, SCRIPT_READER))
    return out, sites, len(rows)


def emit_structured(rom: bytes, plan, cited: dict[int, list[str]], sites: int,
                    entries: int) -> str:
    sections = region_a_sections(plan)
    out = ["; %s / R-RAW-001: the structured block's retail gaps %#010x..%#010x as LABELED RAW DATA."
           % (TICKET, ROM_BASE + families.REGION_A[0], ROM_BASE + families.REGION_A[1]),
           ""]
    for kind, start, end in sections:
        if kind == "generated":
            out.append("        INCBIN  %s" % gen_name(start, end))
            continue
        bounds = split_of(start, end, cited)
        for index, base in enumerate(bounds):
            stop = bounds[index + 1] if index + 1 < len(bounds) else end
            symbol_text(out, base, rom[base:stop], cited.get(base, []),
                        "the gap's first byte, a label boundary only")
    return "\n".join(out)


def check_text_ceiling(text: str, path: str) -> int:
    size = len(text.encode())
    if size > TRACKED_TEXT_CEILING:
        raise SystemExit("%s would be %d bytes of source, over the repository's %d-byte tracked-file "
                         "ceiling (tools/lint/lints.py SIZE_LIMIT); refuse it rather than ship it"
                         % (path, size, TRACKED_TEXT_CEILING))
    return size


def structure(rom: bytes, out: str, apply_source: bool, source: str) -> int:
    plan = families.plan(rom)
    cited, sites, entries = field_citations(rom, plan.gaps)
    text = emit_structured(rom, plan, cited, sites, entries) + "\n"
    rows = blocks(text)
    gap_bytes = sum(end - start for start, end in plan.gaps)
    total = verify_blocks(rom, rows, "the emitted gaps")
    if total != gap_bytes:
        raise SystemExit("the emitted text carries %d bytes, the gaps hold %d" % (total, gap_bytes))
    tokens = [line.split(None, 1)[1] for line in text.split("\n")
              if line.strip().startswith("INCBIN")]
    expected = [gen_name(start, end) for kind, start, end in region_a_sections(plan)
                if kind == "generated"]
    if [token for token in tokens if token.startswith("build")] != expected:
        raise SystemExit("the emitted generated tokens are not the plan's runs")
    with open(out, "w", newline="\n") as handle:
        handle.write(text)
    print("%s: %d symbols, %d gap bytes over %d gap(s), %d cited base(s), %d generated token(s)"
          % (out, len(rows), total, len(plan.gaps), len(cited), len(expected)))
    if apply_source:
        splice_source(source, families.REGION_A, out)
    return 0


def splice_source(path: str, span, include_line: str) -> None:
    start, end = span
    lines = open(path, errors="replace").read().split("\n")
    inside = []
    for index, line in enumerate(lines):
        found = TOKEN.match(line)
        if not found:
            continue
        where = token_span(found.group(2))
        if where is None or not (start <= where[0] and where[1] <= end):
            continue
        inside.append((index, found.group(1), found.group(2)))
    if not inside:
        raise SystemExit("no INCBIN token of %s lies inside %#x..%#x" % (path, start, end))
    if [index for index, _, _ in inside] != list(range(inside[0][0], inside[-1][0] + 1)):
        raise SystemExit("a non-token line lies between the tokens of %#x..%#x" % (start, end))
    rows = [token_span(token) for _, _, token in inside]
    if rows[0][0] != start or rows[-1][1] != end:
        raise SystemExit("the tokens span %#x..%#x, not %#x..%#x"
                         % (rows[0][0], rows[-1][1], start, end))
    for (low, high), (next_low, _) in zip(rows, rows[1:]):
        if high != next_low:
            raise SystemExit("the tokens do not tile at %#x" % high)
    replacement = "%sINCLUDE %s" % (inside[0][1], os.path.basename(include_line))
    drop = None
    index = inside[0][0] - 1
    while index >= 0 and (not lines[index].strip() or lines[index].lstrip().startswith(";")):
        index -= 1
    label = LABEL.match(lines[index]) if index >= 0 else None
    if label and label_offset(label) == start:
        drop = index
    head = lines[:inside[0][0]] if drop is None else lines[:drop] + lines[drop + 1:inside[0][0]]
    kept = head + [replacement] + lines[inside[-1][0] + 1:]
    print("splice %s: %d INCBIN token(s) over %#x..%#x -> %s"
          % (path, len(inside), start, end, replacement.strip()))
    with open(path, "w", encoding="ascii", newline="") as handle:
        handle.write("\n".join(kept))


def block_head(lines: list[str], row: int) -> int:
    head = row
    while head > 0:
        body = lines[head - 1].strip()
        if body == "" or body.startswith(";") or EXPORT.match(lines[head - 1]):
            head -= 1
            continue
        if LABEL.match(lines[head - 1]):
            head -= 1
            if head > 0 and EXPORT.match(lines[head - 1]):
                head -= 1
            return head
        return head
    return head


def spliced(text: str, runs, mine: str = None) -> tuple[str, int, list[int]]:
    lines = text.split("\n")
    units = []
    for index, line in enumerate(lines):
        found = TOKEN.match(line)
        if found is None or token_span(found.group(2)) is None:
            continue
        if found.group(2).endswith(".bin"):
            directory = os.path.basename(os.path.dirname(found.group(2).replace("\\", "/")))
            if mine is None or directory != mine:
                continue
        span = token_span(found.group(2))
        units.append({"row": index, "head": block_head(lines, index), "start": span[0],
                      "end": span[1], "prefix": line[:line.index(found.group(2))]})
    regions = []
    for unit in units:
        if regions and unit["start"] != regions[-1][-1]["end"]:
            regions.append([])
        if not regions:
            regions.append([])
        regions[-1].append(unit)
    edits = []
    retired, inserted = [], 0
    for region in regions:
        start, end = region[0]["start"], region[-1]["end"]
        inside = [(low, high, token) for low, high, token in runs if start < high and low < end]
        if not inside:
            continue
        for low, high, _token in inside:
            if not (start <= low and high <= end):
                raise SystemExit("the run %#x..%#x crosses the carrier's rows at %#x..%#x"
                                 % (low, high, start, end))
        bounds = sorted({start, end, *[low for low, _, _ in inside], *[high for _, high, _ in inside],
                         *[unit["start"] for unit in region
                           if not any(low < unit["start"] < high for low, high, _ in inside)]})
        named = {low: token for low, high, token in inside}
        pieces = [(low, high, named.get(low)) for low, high in zip(bounds, bounds[1:])]
        head_of = {unit["start"]: unit for unit in region}
        starts = {low for low, _, _ in pieces}
        retired += [unit["start"] for unit in region if unit["start"] not in starts]
        out = []
        for low, high, token in pieces:
            unit = head_of.get(low)
            if unit is not None:
                out.extend(lines[unit["head"]:unit["row"]])
            else:
                out.append("|unk_%08X|" % (ROM_BASE + low))
            prefix = next(unit["prefix"] for unit in region if unit["start"] <= low < unit["end"])
            out.append(prefix + (token if token is not None else slice_name(low, high)))
            if token is not None:
                inserted += 1
        edits.append((region[0]["head"], region[-1]["row"] + 1, out))
    for head, stop, replacement in reversed(edits):
        lines[head:stop] = replacement
    return "\n".join(lines), inserted, sorted(retired)


def record_runs(sections, families) -> list[tuple[int, int, str]]:
    import generate_mapcontainer as generator

    return [(section.start, section.end,
             generator.section_output(section).replace(os.sep, "\\"))
            for section in sections if section.kind in families]


def splice_records(rom: bytes) -> int:
    sys.path.insert(0, os.path.join(ROOT, "tools", "mapcontainer"))
    import generate_mapcontainer as generator
    import mapcontainer

    generator.set_block("map")
    _, sections, plan = generator.read_plan(rom, os.path.join(
        ROOT, "tools", "mapcontainer", "mapcontainer_manifest.csv"))
    runs = record_runs(sections, plan["families"])
    runs = sorted(runs + [(section.start, section.end,
                           generator.section_output(section).replace(os.sep, "\\"))
                          for section in sections
                          if section.kind == mapcontainer.CONTAINER])
    written = inserted = 0
    retired = []
    for name in sorted(os.listdir(os.path.join(ROOT, "asm"))):
        if not name.endswith(".s"):
            continue
        path = os.path.join(ROOT, "asm", name)
        text = open(path, errors="replace").read()
        before = layout(text)
        new, count, lost = spliced(text, runs, generator.BLOCK.out_dir)
        if new == text:
            continue
        after = layout(new)
        if after != before:
            raise SystemExit("%s: the splice changed the carrier's layout %s -> %s"
                             % (name, before, after))
        inserted += count
        retired += lost
        written += 1
        check_text_ceiling(new, path)
        with open(path, "w", encoding="ascii", newline="\n") as handle:
            handle.write(new)
    print("splice: %d carrier(s) rewritten, %d generated run(s) placed, %d row(s) retired"
          % (written, inserted, len(retired)))
    if retired:
        print("retired labels: %s" % " ".join("%#x" % address for address in retired))
    tokens = {token for token, _ in emitted.token_ranges(emitted.source_text(ROOT, generator.MAP_SOURCE))}
    missing = [token for _, _, token in runs if token not in tokens]
    if missing:
        raise SystemExit("%d of the plan's %d runs are named by no source token, first %s"
                         % (len(missing), len(runs), missing[0]))
    print("every one of the plan's %d generated runs is a source token" % len(runs))
    return 0


def covered(text: str) -> list[tuple[int, int]]:
    spans = []
    for line in text.split("\n"):
        found = TOKEN.match(line)
        span = token_span(found.group(2)) if found else None
        if span is not None:
            spans.append(span)
    return sorted(spans)


def coverage(text: str) -> list[tuple[int, int]]:
    out = []
    for start, end in covered(text):
        if out and start <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], end))
        else:
            out.append((start, end))
    return out


def layout(text: str) -> tuple[int, list[tuple[int, int]]]:
    spans = covered(text)
    return sum(end - start for start, end in spans), coverage(text)



def fragment_files(root: str = ROOT) -> list[str]:
    directory = os.path.join(root, "asm")
    return [os.path.join(directory, name) for name in sorted(os.listdir(directory))
            if name.endswith(".s")
            and (name.startswith("rawlabeled_") or name.startswith("raw_labeled_"))]


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


def converted(text: str) -> tuple[str, int, int]:
    lines = text.split("\n")
    split = next((index for index, line in enumerate(lines) if not line.startswith(";")), len(lines))
    header, body = lines[:split], lines[split:]
    out = [line for line in header
           if HEADER.match(line) or line == EXPLICIT_CHANNEL]
    address, size, count, total = None, 0, 0, 0

    def flush():
        nonlocal size, total
        if size:
            out.append("\tINCBIN\t%s" % slice_name(address, address + size))
            total += size
            size = 0

    for line in body:
        body_line = line.split(";", 1)[0].strip()
        if line.lstrip().startswith(";"):
            if emitted.CITED.search(line) or emitted.UNCITED.search(line):
                out.append(line)
            continue
        label = LABEL.match(body_line)
        head = body_line.split(None, 1)[0] if body_line else ""
        width = {"DCB": 1, "DCW": 2, "DCD": 4}.get(head)
        space = head == "SPACE"
        token = TOKEN.match(body_line) if head == "INCBIN" else None
        if token is not None and address is not None:
            span = token_span(token.group(2))
            if span is not None and (span == (address, address + size)
                                     or (size == 0 and span[0] == address)):
                total += span[1] - span[0]
                size = 0
                out.append(line)
                continue
        if label or EXPORT.match(body_line) or (
                body_line and not body_line.startswith(";") and width is None and not space):
            flush()
            address = None
        if label:
            address = label_offset(label)
            count += 1
            out.append(line)
            continue
        if width is not None and address is not None:
            size += width * len(body_line.split(None, 1)[1].split(","))
            continue
        if space and address is not None:
            size += int(body_line.split(None, 1)[1], 0)
            continue
        out.append(line)
    flush()
    text = "\n".join(out)
    return (text + "\n" if text and not text.endswith("\n") else text), total, count


def convert(root: str = ROOT) -> int:
    for path in fragment_files(root):
        text = open(path, errors="replace").read()
        new, total, count = converted(text)
        if total <= 0:
            raise SystemExit("%s: no symbol carries a byte; the converter read the file wrong" % path)
        check_text_ceiling(new, path)
        if new == text:
            continue
        with open(path, "w", encoding="ascii", newline="\n") as handle:
            handle.write(new)
        print("convert %s: %d symbol(s), %d byte(s) as extracted slices"
              % (os.path.basename(path), count, total))
    return 0


ROW = re.compile(r"^(\s*)INCBIN\s+(baserom\.gba_0x([0-9a-fA-F]+)_0x[0-9a-fA-F]+\.extracted)\s*$")


def named_rows(text: str) -> tuple[str, int]:
    out, added, previous = [], 0, None
    for line in text.split("\n"):
        found = ROW.match(line)
        if found:
            name = "|unk_%08X|" % (ROM_BASE + int(found.group(3), 16))
            if previous != name:
                out.append(name)
                added += 1
            out.append(line)
            previous = name
            continue
        out.append(line)
        stripped = line.strip()
        if stripped:
            previous = stripped
    return "\n".join(out), added


def name_rows(root: str = ROOT, path: str = None) -> int:
    source = path or os.path.join(root, "asm", "rest_of_the_game.s")
    text = open(source, errors="replace").read()
    new, added = named_rows(text)
    if new != text:
        with open(source, "w", encoding="ascii", newline="") as handle:
            handle.write(new)
    print("%s: %d row(s) named, %d retail row(s) in all"
          % (os.path.relpath(source, root), added,
             sum(1 for line in new.split("\n") if ROW.match(line))))
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


def citation(rows, address: int) -> str:
    if not rows:
        return ("no site names 0x%08X; the census's region boundary, not a cited address"
                % (ROM_BASE + address))
    named = ", ".join("0x%08X" % site for _, site in rows[:CITED_SHOWN])
    more = "" if len(rows) <= CITED_SHOWN else ", +%d more" % (len(rows) - CITED_SHOWN)
    return ("%d ldr-literal site(s) load 0x%08X (%s%s): %s"
            % (len(rows), ROM_BASE + address, named, more,
               ", ".join(sorted({kind for kind, _ in rows}))))


def citation_fragment(rom: bytes, run) -> list[str]:
    split = citation_split(rom, run)
    lines = []
    for addr, end, rows in split:
        lines.append("unk_%08x" % (ROM_BASE + addr))
        lines.append("        ; %s" % citation(rows, addr))
        lines.append("\tINCBIN\t%s" % slice_name(addr, end))
    return lines


def citation_texts(rom: bytes) -> dict:
    return {run: "\n".join(citation_fragment(rom, run)) + "\n" for run in RUNS}


def citation_path(run) -> str:
    return os.path.join(ROOT, "asm", run.file)


def citation_include(run) -> str:
    return "        INCLUDE  %s" % run.file


def citation_token(run) -> str:
    return slice_name(run.start, run.end)


def citation_read(run) -> str:
    path = citation_path(run)
    return open(path, errors="replace").read() if os.path.exists(path) else ""


def citation_splice(text: str, run) -> tuple[str, str]:
    rows = text.split("\n")
    token = citation_token(run)
    hits = [index for index, row in enumerate(rows) if token in row]
    if len(hits) == 1:
        if rows[hits[0]].strip() != "INCBIN  %s" % token:
            raise SystemExit("asm/rest_of_the_game.s:%d is not the retail INCBIN line: %s"
                             % (hits[0] + 1, rows[hits[0]].strip()))
        rows[hits[0]] = citation_include(run)
        return "\n".join(rows), "spliced"
    if not hits and citation_include(run) in rows:
        return text, "already spliced"
    raise SystemExit("asm/rest_of_the_game.s holds %d line(s) naming %s" % (len(hits), token))


def citation_compare(rom: bytes, run) -> int:
    text = citation_read(run)
    rows = blocks(text)
    split = citation_split(rom, run)
    here = [address for address, _, _ in rows]
    want = [address for address, _, _ in split]
    if here != want:
        raise ValueError("%s symbols %s, the cited split %s"
                         % (run.file, [hex(a) for a in here], [hex(a) for a in want]))
    return verify(rom, run.start, run.end, text)


def citation_apply(rom: bytes) -> int:
    wanted = citation_texts(rom)
    for run, text in wanted.items():
        with open(citation_path(run), "w", encoding="ascii", newline="\n") as handle:
            handle.write(text)
        print("wrote asm/%s (%d B)" % (run.file, len(text)))
    source = open(os.path.join(ROOT, "asm", "rest_of_the_game.s"), errors="replace").read()
    for run in RUNS:
        source, state = citation_splice(source, run)
        print("%s: %s" % (run.file, state))
    with open(os.path.join(ROOT, "asm", "rest_of_the_game.s"), "w", encoding="ascii",
              newline="") as handle:
        handle.write(source)
    return citation_check(rom)


def citation_check(rom: bytes) -> int:
    ok = True
    wanted = citation_texts(rom)
    for run in RUNS:
        here = citation_read(run)
        if here != wanted[run]:
            ok = False
            print("FAIL asm/%s is not the generated fragment" % run.file)
            continue
        try:
            moved = citation_compare(rom, run)
        except (ValueError, SystemExit) as error:
            ok = False
            print("FAIL %s" % error)
            continue
        split = citation_split(rom, run)
        print("OK   asm/%-22s %4d B %3d symbols %3d sites"
              % (run.file, moved, len(split), sum(len(rows) for _, _, rows in split)))
    source = open(os.path.join(ROOT, "asm", "rest_of_the_game.s"), errors="replace").read()
    for run in RUNS:
        if citation_include(run) not in source.split("\n") or citation_token(run) in source:
            ok = False
            print("FAIL asm/rest_of_the_game.s does not INCLUDE asm/%s" % run.file)
    print("RAW-LABELED %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def citation_rows(rom: bytes) -> list[tuple[str, int, int, int]]:
    out = []
    for run in RUNS:
        split = citation_split(rom, run)
        out.append(("0x%06X..0x%06X" % (run.start, run.end), run.end - run.start, len(split),
                    sum(len(rows) for _, _, rows in split)))
    return out


def citation_report(rom: bytes) -> int:
    rows = citation_rows(rom)
    print("| run | bytes | symbols | loaders cited |")
    print("|---|---|---|---|")
    for name, size, count, loaders in rows:
        print("| `%s` | %d | %d | %d |" % (name, size, count, loaders))
    print("| **total** | **%d** | **%d** | **%d** |"
          % (sum(row[1] for row in rows), sum(row[2] for row in rows),
             sum(row[3] for row in rows)))
    for run in RUNS:
        print("")
        print("%s:" % run.file)
        for addr, end, sites_here in citation_split(rom, run):
            print("  unk_%08x  %#06x..%#06x %5d B  %s"
                  % (ROM_BASE + addr, addr, end, end - addr, citation(sites_here, addr)))
    return 0


def check(rom: bytes, root: str = ROOT) -> int:
    ok = True
    runs = []
    for path in fragment_files(root):
        text = open(path, errors="replace").read()
        match = HEADER.match(text.split("\n")[0]) if text.startswith(";") else None
        rows = blocks(text)
        try:
            if match and match.group(2) == "census run":
                start, end = int(match.group(3), 16) - ROM_BASE, int(match.group(4), 16) - ROM_BASE
                if tiled(rows, start, end):
                    moved = verify(rom, start, end, text, root)
                else:
                    moved = verify_blocks(rom, rows, os.path.basename(path), root)
                runs.append((os.path.basename(path), moved))
            else:
                verify_blocks(rom, rows, os.path.basename(path), root)
                runs.append((os.path.basename(path), sum(end - start for start, end, _ in rows)))
        except ValueError as error:
            ok = False
            print("FAIL %s: %s" % (os.path.basename(path), error))
    for name, size in runs:
        print("OK   asm/%-24s %8d B" % (name, size))
    print("fragments=%d bytes=%d %s" % (len(runs), sum(size for _, size in runs),
                                        "PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None) -> int:
    global TICKET, DOC
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", default="baserom.gba")
    parser.add_argument("--boundaries", help="data-stated boundaries, one hex file offset per line")
    parser.add_argument("--citations", help="explicit citation list, `file offset hex comment` per "
                                            "line, for a cited consumer the loader channel cannot see")
    parser.add_argument("--range", nargs=2, action="append", metavar=("START", "END"),
                        type=lambda text: int(text, 16))
    parser.add_argument("--structured", action="store_true",
                        help="promote the structured block's interleaved retail gaps (PATH-100-003)")
    parser.add_argument("--apply-source", action="store_true",
                        help="rewrite asm/rest_of_the_game.s: the span's tokens become one INCLUDE")
    parser.add_argument("--source", default=os.path.join(ROOT, "asm", "rest_of_the_game.s"))
    parser.add_argument("--ticket", default=TICKET, help="the ticket the emitted header names")
    parser.add_argument("--doc", default=DOC, help="the document the emitted header points at")
    parser.add_argument("--extract", action="store_true",
                        help="write every slice the tracked fragments name, from baserom.gba")
    parser.add_argument("--convert", action="store_true",
                        help="rewrite the tracked fragments: each symbol's bytes become its INCBIN")
    parser.add_argument("--name-rows", action="store_true",
                        help="give every retail INCBIN row of rest_of_the_game.s a |unk_<ROMADDR>|")
    parser.add_argument("--splice-records", action="store_true",
                        help="insert the map plan's record runs between the labelled rows")
    parser.add_argument("--check", action="store_true", help="the tree against the image, no writes")
    parser.add_argument("--raw-label", action="store_true",
                        help="regenerate PATH-100-001's two runs and splice the source")
    parser.add_argument("--report", action="store_true",
                        help="print PATH-100-001's runs' table and every symbol's citation")
    parser.add_argument("--raw-source", default=os.path.join(ROOT, "asm", "rest_of_the_game.s"))
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    TICKET, DOC = args.ticket, args.doc
    rom = open(args.rom, "rb").read()
    modes = [args.structured, bool(args.range), args.extract, args.convert, args.name_rows,
             args.check, args.raw_label, args.report, args.splice_records]
    if sum(1 for mode in modes if mode) > 1:
        parser.error("give one of --structured, --range, --extract, --convert, --name-rows, --check,"
                     " --raw-label, --report, --splice-records")
    if args.extract:
        return extract(rom)
    if args.convert:
        return convert()
    if args.name_rows:
        return name_rows()
    if args.splice_records:
        return splice_records(rom)
    if args.check:
        return check(rom)
    if args.raw_label:
        return citation_apply(rom)
    if args.report:
        return citation_report(rom)
    if args.structured:
        if not args.out:
            parser.error("--structured needs --out")
        return structure(rom, args.out, args.apply_source, args.source)
    if not args.range or not args.out:
        parser.error("give --range with --out, or one of the tree-level modes")
    extra = boundaries(args.boundaries)
    for start, end in args.range:
        explicit = None
        if args.citations:
            explicit = explicit_citations(args.citations, start, end)
            if not explicit:
                raise SystemExit("%s names no base inside %#x..%#x"
                                 % (args.citations, start, end))
        text = emit(rom, start, end, extra, args.ticket, args.doc, explicit)
        verify(rom, start, end, text)
        size = check_text_ceiling(text + "\n", args.out)
        with open(args.out, "w", newline="\n") as handle:
            handle.write(text + "\n")
        found = explicit if explicit is not None else citations(rom, start, end)
        print("%s: %d symbols, %d bytes, %d citations, %d shaped, %d source bytes"
              % (args.out, len(blocks(text)), end - start, len(found),
                 len([base for base in found if base in SHAPES]), size))
        if args.apply_source:
            splice_source(args.source, (start, end), args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
