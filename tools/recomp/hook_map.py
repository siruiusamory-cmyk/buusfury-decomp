from __future__ import annotations

import argparse
import os
import re
import sys

import capstone

import written

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ENTRY_PC = 0x08000000
INPUTS = os.path.join("docs", "research", "RECOMP_INPUTS.toml")
OUT = os.path.join("docs", "research", "RECOMP_HOOKS.md")
ROM = os.path.join(ROOT, "baserom.gba")
STATUSES = ("PROVEN", "CITED", "UNVERIFIED")

AREAS = [
    ("Widescreen", [
        (0x08030EC4, "writes the negated value to `0x04000010`, the BG0 horizontal scroll", "image", 3, "PROVEN"),
        (0x0803372C, "writes `0x04000014`, the BG1 horizontal scroll", "image", 3, "PROVEN"),
        (0x08025D36, "writes `0x04000018`, the BG2 horizontal scroll", "image", 3, "PROVEN"),
        (0x0802E9AC, "writes `0x0400001C`, the BG3 horizontal scroll", "image", 3, "PROVEN"),
        (0x0803FA2C, "a second writer of `0x0400001C`", "image", 3, "PROVEN"),
        (0x0802C918, "reads `0x04000008`, the BG0 control register", "image", 4, "PROVEN"),
        (0x0800938C, "the writer of the four halfwords read as the BG control values",
         "doc", "TEXT_TABLES.md", "CITED"),
        (0x08009B2C, "calls the packed decoder at IWRAM `0x03000040` on `frame+4`",
         "doc", "MAP_BLOCK_LAYOUTS.md", "CITED"),
        (0x08009B42, "copies `vram_units * 64` B of the decoded frame to "
                     "`0x06000000 + vram_slot * 64`", "doc", "MAP_BLOCK_LAYOUTS.md", "CITED"),
        (None, "the actor cull bounds: no tracked page states them", "text",
         "nothing in `docs/research/` bounds where an actor is culled", "UNVERIFIED"),
        (None, "the OAM build: no exported code row loads `0x07000000`, and none forms it as "
               "`movs` `#0x70` then `lsls` `#0x18`", "text",
         "measured over the export's 2,822 rows", "UNVERIFIED"),
    ]),
    ("Frame pacing and fast-forward", [
        (0x0803F3F4, "the prologue of the routine that holds the wait", "image", 3, "PROVEN"),
        (0x0803F422, "`svc #2` inside the wait loop, gated on the halfword at `[r4+0x38]` and "
                     "the mask `r5`: the only `svc #2` inside any exported code row",
         "image", 4, "PROVEN"),
        (None, "the frame counter: no exported row loads `0x03007FFC` to install the interrupt "
               "vector, so its address is not established", "text",
         "measured over the export's 2,822 rows", "UNVERIFIED"),
    ]),
    ("Saves", [
        (None, "the save type", "text",
         "no exported row loads `0x0D000000`, `0x0E000000` or `0x080000C4`/`C6`/`C8`", "UNVERIFIED"),
        (None, "the save write routine", "text", "the same measurement: the path is outside the "
               "exported rows", "UNVERIFIED"),
        (None, "the resume marks", "text",
         "`PLAY_CHECKLIST.md` records a run resumed from the last saved state, with no address",
         "UNVERIFIED"),
    ]),
    ("Text renderer and glyph tables", [
        (0x0803029E, "reads the glyph table row `0x757EE8`", "doc", "ENDROM_RECON_001.md", "CITED"),
        (0x08012240, "the handle chain that reads the dialogue container table `0x7B5B64`",
         "doc", "INCBIN_CENSUS.md", "CITED"),
        (0x08000754, "a read pc of the dialogue container table's run",
         "doc", "UNKNOWN_CENSUS.md", "CITED"),
        (0x757EE8, "the glyph table row itself", "doc", "ENDROM_RECON_001.md", "CITED"),
        (0x71730, "the first dialogue layout record", "doc", "TEXT_TABLES.md", "CITED"),
        (0x71744, "the second dialogue layout record", "doc", "TEXT_TABLES.md", "CITED"),
    ]),
    ("Audio engine entry and mixer", [
        (0x0803E378, "the channel allocator: stores a sample record's address into a free "
                     "channel slot", "doc", "ASSETDIR_SAMPLES.md", "CITED"),
        (0x0803E4E4, "the slot engine's note handler", "doc", "ASSETDIR_SAMPLES.md", "CITED"),
        (0x0803EE84, "the tick dispatcher that runs the slot handlers",
         "doc", "ASSETDIR_SAMPLES.md", "CITED"),
        (0x0803F110, "stores the current music record at `state+0xC`",
         "doc", "ASSETDIR_SAMPLES.md", "CITED"),
        (0x0803E184, "calls the slot's mixing routine through `0x08046AA6`",
         "doc", "ASSETDIR_SAMPLES.md", "CITED"),
        (0x08046AA6, "`bx r3`: the indirect call the mixer path takes", "image", 3, "PROVEN"),
        (0x083192A8, "directory 1's sample table base", "doc", "ASSETDIR_SAMPLES.md", "CITED"),
        (0x0836D18C, "the 79-record music table", "doc", "ASSETDIR_SAMPLES.md", "CITED"),
        (0x7B820C, "file offset of the ARM mixer body copied to IWRAM `0x03000868`",
         "doc", "ASSETDIR_SAMPLES.md", "CITED"),
    ]),
]


def rows(root=ROOT):
    text = open(os.path.join(root, INPUTS), encoding="ascii", newline="").read()
    out = []
    for block in text.split("[[code]]")[1:]:
        addr = int(re.search(r'addr = 0x([0-9a-f]+)', block).group(1), 16)
        size = int(re.search(r'size = (\d+)', block).group(1))
        mode = re.search(r'mode = "(\w+)"', block).group(1)
        out.append((addr, size, mode))
    out.sort()
    return out


def row_of(addr, table):
    for start, size, mode in table:
        if start <= addr < start + size:
            return mode, start, start + size
    raise SystemExit("0x%08X is inside no exported code row, so its mode is not derivable"
                     % addr)


def mode_of(addr, table):
    return row_of(addr, table)[0]


def quote(image, addr, mode, count):
    engine = capstone.Cs(capstone.CS_ARCH_ARM,
                         capstone.CS_MODE_THUMB if mode == "thumb" else capstone.CS_MODE_ARM)
    at = addr - ENTRY_PC
    text = []
    for insn in engine.disasm(image[at:at + 4 * count], addr):
        if len(text) == count:
            break
        text.append("0x%08X %s %s" % (insn.address, insn.mnemonic, insn.op_str))
    if len(text) != count:
        raise SystemExit("0x%08X does not decode to %d instructions" % (addr, count))
    return "`" + "` / `".join(text) + "`"


def shown_address(addr):
    return "0x%08X" % addr if 0x08000000 <= addr < 0x0E000000 else "0x%X" % addr


def render(root=ROOT, rom=ROM):
    if not os.path.exists(rom):
        raise SystemExit("no image at %s, so no instruction can be quoted" % rom)
    image = open(rom, "rb").read()
    table = rows(root)
    lines = ["# Routines and data a mod would take",
             "",
             "Generated by `tools/recomp/hook_map.py` (`--write`). Statuses: PROVEN = the retail "
             "bytes quoted at the address do the stated thing; CITED = a tracked research page "
             "states it and this file does not re-derive it; UNVERIFIED = the tree carries no "
             "evidence. A ROM address is given as a bus address, `0x08000000 + file offset`; an "
             "address below `0x08000000` is the file offset the cited page uses.",
             ""]
    counts = {status: 0 for status in STATUSES}
    for title, area in AREAS:
        lines += ["## %s" % title, "",
                  "| address | what a mod would touch | evidence | status |",
                  "|---|---|---|---|"]
        for addr, role, kind, detail, status in area:
            counts[status] += 1
            shown = "none" if addr is None else "`%s`" % shown_address(addr)
            if kind == "image":
                mode, start, end = row_of(addr, table)
                evidence = "%s, in the exported row `0x%08X..0x%08X`" % (
                    quote(image, addr, mode, detail), start, end)
            elif kind == "doc":
                evidence = "`docs/research/%s`" % detail
            else:
                evidence = detail
            lines.append("| %s | %s | %s | %s |" % (shown, role, evidence, status))
        lines.append("")
    return "\n".join(lines), counts


def main(argv=None):
    parser = argparse.ArgumentParser(description="emit the hook map a mod's enhancement work "
                                                 "starts from")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text, counts = render()
    for status in STATUSES:
        print("%s = %d" % (status, counts[status]))
    print("rows = %d" % sum(counts.values()))
    return written.emit(args, text, os.path.join(ROOT, OUT),
                        "the hook map is the one the image and the pages derive")


if __name__ == "__main__":
    sys.exit(main())
