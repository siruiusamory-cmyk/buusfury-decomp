"""Read one Tulma001 session's captures and say what the engine actually loaded.

WHY THIS IS A MEASUREMENT. A screenshot can be argued about; the hardware tile bytes cannot.
The candidate's containers decode to hardware-order object tiles, and the engine streams a
container into the object tile region 0x06010000..0x06018000 when it draws that facing. So
"the engine drew the authored art" is the claim that those exact 512-byte blocks are present
in the region during a settled screen, and the check is a search of the dump for them.

The palette dump covers 0x05000000..0x050003FF, both banks, so the object half can be
compared against the image's own palette: this write changes indices and never colours, so a
difference there would be a finding rather than an expected one.

Nothing here writes to the ROM or the run directory unless --report is given, and it never
touches the emulator.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.webfoot.formats import webfoot_lz as wl  # noqa: E402

OBJ_REGION_START = 0x10000  # within a dump taken from 0x06000000
OBJ_REGION_BYTES = 0x8000
PALETTE_BYTES = 0x200  # one bank; the object bank is the second half of the dump
OBJECT_PALETTE_ADDRESS = 0x0805652C


def decode_hardware_tiles(image: bytes, offset: int) -> bytes:
    """The container's decoded payload, which is already in hardware tile order."""
    return wl.unpack(image, offset).data


def settles(run_dir: Path) -> list[tuple[int, Path, Path]]:
    found = []
    for path in sorted(run_dir.glob("settle-*-vram.bin")):
        match = re.match(r"settle-(\d+)-vram\.bin$", path.name)
        if match:
            found.append((int(match.group(1)), path,
                          path.with_name(path.name.replace("-vram.bin", "-palette.bin"))))
    return found


def _colours(bank: bytes) -> tuple[int, ...]:
    """The bank's 256 BGR555 colours, with the spare high bit masked off.

    Compared without bit 15 on purpose. The live object bank differs from the image's table
    at exactly one entry, index 2, where the ROM holds 0xFFFF and the engine holds 0x7FFF:
    the same five colour channels with the unused top bit cleared. Comparing raw halfwords
    reports that as a palette mismatch, which it is not.
    """
    return tuple((bank[2 * i] | (bank[2 * i + 1] << 8)) & 0x7FFF for i in range(256))


def analyse(run_dir: Path, candidate_path: Path, report_path: Path) -> dict:
    image = candidate_path.read_bytes()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    authored = {}
    for record in report["containers"]:
        if not record["owner"].startswith("sprite:"):
            continue
        offset = record.get("new_offset", record["container_offset"])
        authored[record["container_offset"]] = decode_hardware_tiles(image, offset)

    results = []
    for index, vram_path, palette_path in settles(run_dir):
        vram = vram_path.read_bytes()
        region = vram[OBJ_REGION_START:OBJ_REGION_START + OBJ_REGION_BYTES]
        present = sorted(hex(offset) for offset, tiles in authored.items()
                         if tiles in region)
        palette = palette_path.read_bytes() if palette_path.exists() else b""
        object_bank = palette[PALETTE_BYTES:PALETTE_BYTES * 2] if palette else b""
        rom_bank = image[OBJECT_PALETTE_ADDRESS - 0x08000000:
                         OBJECT_PALETTE_ADDRESS - 0x08000000 + PALETTE_BYTES]
        palette_same = _colours(object_bank) == _colours(rom_bank) if object_bank else None
        palette_differences = (
            [i for i in range(256) if _colours(object_bank)[i] != _colours(rom_bank)[i]]
            if object_bank else [])
        results.append({
            "settle": index,
            "vram_bytes": len(vram),
            "object_region_bytes": len(region),
            "authored_containers_present": present,
            "authored_tiles_found": sum(1 for tiles in authored.values() if tiles in region),
            "object_palette_colours_match_image": palette_same,
            "object_palette_differing_entries": palette_differences,
        })
    return {
        "run_dir": str(run_dir),
        "candidate_sha256": report["output_sha256"],
        "authored_containers": len(authored),
        "settles": results,
        "any_authored_tiles_drawn": any(row["authored_tiles_found"] for row in results),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    result = analyse(args.run_dir, args.candidate, args.report)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if result["any_authored_tiles_drawn"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
