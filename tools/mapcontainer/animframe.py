from __future__ import annotations

import argparse
import csv
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
ASM = os.path.join(ROOT, "asm")
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "webfoot"))
sys.path.insert(0, os.path.join(TOOLS, "tilebank"))
sys.path.insert(0, os.path.join(TOOLS, "research"))

import animrow
import emitted
import encode_cache
import jcalg1
import pngsheet
import romfile

FAMILY = "map_anim_frame"
BLOCK = animrow.BLOCK
ROM_BASE = 0x08000000
ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
PALETTE_FILE = 0x05652C
PALETTE_ENTRIES = 256
COMPRESS = os.path.join(ROOT, "tools", "compress", "compress.exe")
CACHE = "animframe"
MANIFEST = os.path.join(HERE, "animframe_manifest.csv")
MANIFEST_FIELDS = ("start", "end", "bytes", "frames")
CONSUMER = animrow.CONSUMER + (
    (0x08009B2C, 0xF03F), (0x08009B2E, 0xFAF8),
    (0x08009B36, 0x018A), (0x08009B38, 0x2103), (0x08009B3A, 0x0649),
    (0x08009B3E, 0x1840), (0x08009B40, 0x1C29),
    (0x08009B42, 0xF03F), (0x08009B44, 0xFAF9))
MEASURED = {"rows": 431, "frames": 485, "payload": 84228, "sections": 125, "section_bytes": 83908}


def read_rom(path):
    return romfile.read_rom(path, ROM_SHA256)


def palette(rom):
    words = struct.unpack_from("<%dH" % PALETTE_ENTRIES, rom, PALETTE_FILE)
    return [tuple(((word >> shift) & 31) * 255 // 31 for shift in (0, 5, 10))
            for word in words]


def pinned(rom):
    for address, halfword in CONSUMER:
        found = struct.unpack_from("<H", rom, address - ROM_BASE)[0]
        if found != halfword:
            raise SystemExit("0x%08X holds 0x%04X, not the measured 0x%04X"
                             % (address, found, halfword))


def walk(rom):
    frames = {}
    for row in sorted(animrow.sites(rom)):
        parsed = animrow.parse(rom, row)
        for index, pointer in enumerate(parsed["frame"]):
            site = pointer - ROM_BASE
            if site in frames:
                continue
            if not BLOCK[0] <= site < BLOCK[1]:
                raise SystemExit("frame 0x%08X of 0x%08X is outside the block"
                                 % (pointer, ROM_BASE + row))
            probe = jcalg1.probe(rom, site + 4, len(rom))
            if not probe["ok"]:
                raise SystemExit("frame 0x%08X refuses: %s" % (pointer, probe["reason"]))
            if len(probe["data"]) != parsed["vram_units"] * 64:
                raise SystemExit("frame 0x%08X decodes to %d B, the row states %d"
                                 % (pointer, len(probe["data"]), parsed["vram_units"] * 64))
            frames[site] = {
                "row": row, "index": index, "units": parsed["vram_units"],
                "slot": parsed["vram_slot"],
                "duration": struct.unpack_from("<I", rom, site)[0],
                "decoded": probe["data"], "consumed": probe["consumed"]}
    return frames


def spans(frames):
    return sorted((site, site + 4 + frame["consumed"]) for site, frame in frames.items())


def covers(frames, start, end):
    out = []
    cursor = start
    for site, finish in spans(frames):
        if finish <= cursor or site >= end:
            continue
        if site != cursor:
            return None
        out.append(site)
        cursor = finish
    return out if cursor == end else None


_CARRIERS = []


def carrier_lines():
    if _CARRIERS:
        return _CARRIERS
    for name in sorted(os.listdir(ASM)):
        if not name.endswith(".s"):
            continue
        path = os.path.join(ASM, name)
        lines = open(path, errors="replace").read().split("\n")
        index = {}
        for number, line in enumerate(lines):
            token = emitted.TOKEN.match(line)
            if token and token.group(1) not in index:
                index[token.group(1)] = number
        for token, span in emitted.token_ranges("\n".join(lines)):
            if BLOCK[0] <= span[0] and span[1] <= BLOCK[1] and token in index:
                _CARRIERS.append((path, index[token], token, span[0], span[1]))
    return _CARRIERS


def read_manifest():
    with open(MANIFEST, newline="") as handle:
        return [{"start": int(row["start"], 16), "end": int(row["end"], 16),
                 "bytes": int(row["bytes"]), "frames": int(row["frames"])}
                for row in csv.DictReader(handle)]


def write_manifest(sections):
    with open(MANIFEST, "w", encoding="ascii", newline="\n") as handle:
        handle.write(",".join(MANIFEST_FIELDS) + "\n")
        for section in sections:
            handle.write("0x%06X,0x%06X,%d,%d\n" % (section["start"], section["end"],
                                                    section["bytes"], section["frames"]))


OUT = os.path.join(ROOT, "build", CACHE)


def output(section):
    return os.path.join(OUT, "gen_%06x_%06x.bin" % (section["start"], section["end"]))


def image_path(section):
    return os.path.join(OUT, "images", "gen_%06x_%06x.png" % (section["start"],
                                                              section["end"]))


def encode(rom, section, frames, colors, compress):
    blob = bytearray()
    for site in covers(frames, section["start"], section["end"]):
        frame = frames[site]
        width, height, indices = pngsheet.sheet_of(frame["decoded"], across=frame["units"])
        path = image_path(section)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        pngsheet.write_indexed(path, width, height, indices, colors)
        back = pngsheet.read_indexed(path)
        payload = pngsheet.payload_of(back[2], back[0], back[1], frame["units"],
                                      across=frame["units"])
        if payload != frame["decoded"]:
            raise SystemExit("the image at 0x%08X does not carry its own pixels" % site)
        stored = compress(payload)
        if stored[:8] != struct.pack("<II", 1, len(payload)) or \
                stored[8:] != rom[site + 4:site + 4 + frame["consumed"]]:
            raise SystemExit("the oracle does not reproduce the stream at 0x%08X" % site)
        blob += struct.pack("<I", frame["duration"]) + stored[8:]
    if len(blob) != section["bytes"] or \
            bytes(blob) != rom[section["start"]:section["end"]]:
        raise SystemExit("section 0x%08X does not reproduce its own bytes" % section["start"])
    return bytes(blob)


def store(path, blob):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and open(path, "rb").read() == blob:
        return 0
    with open(path, "wb") as handle:
        handle.write(blob)
    if open(path, "rb").read() != blob:
        raise SystemExit("%s does not hold what was written" % path)
    return 1


def oracle(work_dir):
    os.makedirs(work_dir, exist_ok=True)
    source = os.path.join(work_dir, "oracle.in")
    target = os.path.join(work_dir, "oracle.out")

    def run(payload):
        with open(source, "wb") as handle:
            handle.write(payload)
        result = subprocess.run([COMPRESS, source, target], capture_output=True)
        if result.returncode != 0:
            raise SystemExit("compress.exe exit %d: %s"
                             % (result.returncode, result.stderr.decode("latin-1")[-200:]))
        return open(target, "rb").read()
    return run


def report(rom, frames, sections):
    payload = sum(frame["consumed"] for frame in frames.values())
    found = (len(animrow.sites(rom)), len(frames), payload)
    if found != (MEASURED["rows"], MEASURED["frames"], MEASURED["payload"]):
        raise SystemExit("the walk found %d rows / %d frames / %d B" % found)
    high = max(max(frame["decoded"]) for frame in frames.values())
    if high < 16:
        raise SystemExit("the payloads use index %d at most, so 8bpp is unproven" % high)
    if (len(sections), sum(section["bytes"] for section in sections)) != \
            (MEASURED["sections"], MEASURED["section_bytes"]):
        raise SystemExit("the manifest holds %d section(s) / %d B"
                         % (len(sections), sum(section["bytes"] for section in sections)))
    for section in sections:
        rows = covers(frames, section["start"], section["end"])
        if rows is None or len(rows) != section["frames"]:
            raise SystemExit("section 0x%06X..0x%06X does not tile into %d frame(s)"
                             % (section["start"], section["end"], section["frames"]))
    inside = [item for item in carrier_lines()
              if (item[3], item[4]) in {(section["start"], section["end"])
                                        for section in sections}]
    retail = [item for item in inside if item[2].startswith("baserom.gba_")]
    print("family %s sections %d rows %d frames %d payload %d B"
          % (FAMILY, len(sections), MEASURED["rows"], len(frames), payload))
    print("tokens naming a section %d: retail slice %d, generated slice %d"
          % (len(inside), len(retail), len(inside) - len(retail)))
    print("highest palette index in the decoded payloads: 0x%02X" % high)
    left = [item for item in carrier_lines()
            if (item[3], item[4]) not in {(section["start"], section["end"])
                                          for section in sections}]
    print("carrier tokens left alone: %d, %d B"
          % (len(left), sum(item[4] - item[3] for item in left)))
    return 0


def cmd_census(args):
    rom = read_rom(args.rom)
    pinned(rom)
    frames = walk(rom)
    return report(rom, frames, read_manifest())


def cmd_extract(args):
    rom = read_rom(args.rom)
    frames = walk(rom)
    sections = []
    for path, index, token, start, end in carrier_lines():
        rows = covers(frames, start, end)
        if not rows:
            continue
        sections.append({"start": start, "end": end, "bytes": end - start,
                         "frames": len(rows)})
    write_manifest(sections)
    print("wrote %d section(s) / %d B to %s"
          % (len(sections), sum(section["bytes"] for section in sections), MANIFEST))
    return report(rom, frames, sections)


def cmd_splice(args):
    rom = read_rom(args.rom)
    frames = walk(rom)
    sections = {section["start"]: section for section in read_manifest()}
    changed = 0
    for name in sorted(os.listdir(ASM)):
        if not name.endswith(".s"):
            continue
        path = os.path.join(ASM, name)
        lines = open(path, errors="replace").read().split("\n")
        out = list(lines)
        for index, line in enumerate(lines):
            token = emitted.TOKEN.match(line)
            if not token:
                continue
            for found, span in emitted.token_ranges(line):
                section = sections.get(span[0])
                if section is None or section["end"] != span[1]:
                    continue
                target = os.path.relpath(output(section), ROOT).replace(os.sep, "\\")
                out[index] = line.replace(found, target, 1)
                break
        if out != lines:
            changed += 1
            if args.apply:
                with open(path, "w", encoding="ascii", newline="") as handle:
                    handle.write("\n".join(out))
    print("carriers %d file(s) %s" % (changed, "rewritten" if args.apply else "differ"))
    return 0


def cmd_build(args):
    rom = read_rom(args.rom)
    pinned(rom)
    frames = walk(rom)
    sections = read_manifest()
    report(rom, frames, sections)
    colors = palette(rom)
    work = os.path.join(ROOT, "build", CACHE)
    cached, stats, close = encode_cache.cached_compress(
        oracle(work), COMPRESS, os.path.join(encode_cache.default_cache_dir(), CACHE))
    written = 0
    for section in sections:
        written += store(output(section), encode(rom, section, frames, colors, cached))
    close()
    print("sections=%d generated=%d carve-out=0 retail=0 incbin_lines=%d containers=%d records=%d"
          % (len(sections), len(sections), len(sections), len(frames), len(sections)))
    print("oracle spawns=%d cache hits=%d misses=%d"
          % (stats["spawns"], stats["hits"], stats["misses"]))
    print("encode_cache_misses=%d trusted=%d total=%d"
          % (stats["misses"], stats["trusted"], stats["total"]))
    print("%s: %d section file(s) written, %d B"
          % (FAMILY, written, sum(section["bytes"] for section in sections)))
    return 0


def main(argv=None):
    global OUT
    parser = argparse.ArgumentParser(
        description="Carry a map animation frame as an indexed image and re-encode its retail"
                    " stream.")
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--out-dir", default=os.path.join(ROOT, "build", CACHE))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("command", nargs="?", default="census",
                        choices=("census", "extract", "splice", "build"))
    args = parser.parse_args(argv)
    OUT = os.path.abspath(args.out_dir)
    return {"census": cmd_census, "extract": cmd_extract, "splice": cmd_splice,
            "build": cmd_build}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
