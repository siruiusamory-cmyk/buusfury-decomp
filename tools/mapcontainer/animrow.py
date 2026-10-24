from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv  # noqa: E402
import hashlib  # noqa: E402
import emitted  # noqa: E402
import mapcontainer  # noqa: E402
import recordfamily  # noqa: E402

FAMILY = "map_anim_row"
FIELDS = ("frame_count", "vram_units", "vram_slot", "frame")
MAX_FRAMES = 64
ROM_BASE = 0x08000000
ROM_SPAN = 0x02000000
BLOCK = (0x179A50, 0x2B8BC8)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASM = os.path.join(ROOT, "asm")
CONSUMER = ((0x08009B94, 0x68CA), (0x08009BAE, 0x59AD), (0x08009B26, 0x6841),
            (0x08009B32, 0x7841), (0x08009B34, 0x8840), (0x08009BBA, 0x6055),
            (0x08009BBC, 0x886A), (0x08009BC2, 0x1C13), (0x08009CF0, 0x7812),
            (0x08009D02, 0x6849), (0x08009D04, 0x6809))
NULLS = {0x2B7E58: "interior labels at +1 +2 +4 +0x10 inside the 28-byte record"}


def read_u8(rom: bytes, offset: int) -> int:
    return rom[offset]


def u32(rom: bytes, offset: int) -> int:
    return struct.unpack_from("<I", rom, offset)[0]


def fields(rom: bytes, offset: int, size: int = None) -> dict:
    count = read_u8(rom, offset)
    extent = 4 + 4 * count
    if size is not None and size != extent:
        raise ValueError("%s at %#x is %d bytes, not %d" % (FAMILY, offset, extent, size))
    if not 1 <= count <= MAX_FRAMES:
        raise ValueError("%s at %#x frame_count is %d" % (FAMILY, offset, count))
    try:
        parsed = {"frame_count": count,
                  "vram_units": read_u8(rom, offset + 1),
                  "vram_slot": struct.unpack_from("<H", rom, offset + 2)[0],
                  "frame": tuple(u32(rom, offset + 4 + 4 * index) for index in range(count))}
    except struct.error:
        raise ValueError("%s at %#x runs past its buffer" % (FAMILY, offset))
    for pointer in parsed["frame"]:
        if not ROM_BASE <= pointer < ROM_BASE + ROM_SPAN:
            raise ValueError("%s at %#x frame is %#x, outside the image"
                             % (FAMILY, offset, pointer))
    return parsed


def serialize(parsed: dict, size: int = None) -> bytes:
    count = parsed["frame_count"]
    if len(parsed["frame"]) != count or not 1 <= count <= MAX_FRAMES:
        raise ValueError("%s packs %d frames against a count of %d"
                         % (FAMILY, len(parsed["frame"]), count))
    out = bytearray(struct.pack("<BBH", count, parsed["vram_units"], parsed["vram_slot"]))
    for pointer in parsed["frame"]:
        out += struct.pack("<I", pointer)
    if size is not None and len(out) != size:
        raise ValueError("%s packs to %d bytes, not its %d" % (FAMILY, len(out), size))
    return bytes(out)


def parse(rom: bytes, offset: int):
    try:
        return fields(rom, offset)
    except ValueError:
        return None


def sites(rom: bytes) -> dict[int, int]:
    out = {}
    for root in mapcontainer.map_roots(rom):
        count = read_u8(rom, root + 0x0C)
        array = u32(rom, root + 0x10)
        if not 1 <= count <= 32 or not ROM_BASE <= array < ROM_BASE + len(rom):
            continue
        for index in range(count):
            pointer = u32(rom, array - ROM_BASE + 4 * index)
            if not ROM_BASE <= pointer < ROM_BASE + len(rom):
                continue
            offset = pointer - ROM_BASE
            if offset in out or not BLOCK[0] <= offset < BLOCK[1]:
                continue
            parsed = parse(rom, offset)
            if parsed is not None:
                out[offset] = 4 + 4 * parsed["frame_count"]
    return out


_CLAIMED: dict[str, list[tuple[int, int]]] = {}


def claimed(rom: bytes) -> list[tuple[int, int]]:
    key = hashlib.sha256(rom).hexdigest()
    if key not in _CLAIMED:
        _CLAIMED[key] = _claims(rom)
    return _CLAIMED[key]


def _claims(rom: bytes) -> list[tuple[int, int]]:
    spans = [(offset, offset + mapcontainer.decode(rom, offset).stored_size)
             for offset in mapcontainer.container_offsets(rom)]
    spans += [(offset, offset + length)
              for rows in mapcontainer.record_extents(rom).values() for offset, length in rows]
    spans += [(offset, offset + length) for offset, length
              in mapcontainer.mode_row_sites(rom, BLOCK, spans)]
    return spans


def free(rom: bytes) -> dict[int, int]:
    spans = claimed(rom)
    return {offset: length for offset, length in sites(rom).items()
            if offset not in NULLS
            and not any(offset < end and start < offset + length for start, end in spans)}


def token_spans() -> list[tuple[int, int]]:
    spans = []
    for name in sorted(os.listdir(ASM)):
        if name.endswith(".s"):
            spans += [span for _, span in emitted.token_ranges(
                emitted.source_text(ROOT, os.path.join(ASM, name)))]
    return spans


def table(parsed: dict, offset: int, named: bool = False) -> list[str]:
    words = parsed["frame"]
    address = ROM_BASE + offset
    lines = ["|%s_%08X|" % (FAMILY, address)]
    if named:
        lines.append("|unk_%08X|" % address)
    lines += ["\tDCB 0x%02x,0x%02x" % (parsed["frame_count"], parsed["vram_units"]),
              "\tDCW 0x%04x" % parsed["vram_slot"]]
    for index in range(0, len(words), 8):
        lines.append("\tDCD " + ",".join("0x%08x" % word for word in words[index:index + 8]))
    return lines


def check(rom: bytes) -> dict:
    free_rows = free(rom)
    spans = token_spans()
    problems = []
    for offset, length in sorted(free_rows.items()):
        if any(start <= offset and offset + length <= end for start, end in spans):
            problems.append("%#x is still carried by an INCBIN" % offset)
        if serialize(fields(rom, offset), length) != rom[offset:offset + length]:
            problems.append("%#x does not re-serialize from its fields" % offset)
    for offset in NULLS:
        if not any(start <= offset < end for start, end in spans):
            problems.append("%#x is a null and is no longer carried raw" % offset)
    return {"records": len(free_rows), "bytes": sum(free_rows.values()),
            "anchored": len(sites(rom)),
            "anchored_bytes": sum(sites(rom).values()), "problems": problems}


def assert_contract(rom: bytes) -> dict:
    recordfamily.consumer_pins(rom, FAMILY, [(address - ROM_BASE, halfword)
                                             for address, halfword in CONSUMER])
    result = check(rom)
    if result["problems"]:
        raise SystemExit("%s: %s" % (FAMILY, "; ".join(result["problems"][:5])))
    if (result["records"], result["bytes"]) != (122, 3500):
        raise SystemExit("%s holds %d records / %d B, not the measured 122 / 3500"
                         % (FAMILY, result["records"], result["bytes"]))
    if (result["anchored"], result["anchored_bytes"]) != (431, 12824):
        raise SystemExit("%s walks %d records / %d B, not the measured 431 / 12824"
                         % (FAMILY, result["anchored"], result["anchored_bytes"]))
    return result


    result = assert_contract(rom)
    print("%s records=%d bytes=%d anchored=%d anchored_bytes=%d"
          % (FAMILY, result["records"], result["bytes"], result["anchored"],
             result["anchored_bytes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
