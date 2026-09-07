"""Bounded static TOOLKIT-009 evidence; canonical input is always read-only.

Usage: python -m tools.research.placement_type_audit ROM START END
Addresses are explicit GBA fetch addresses; this never normalizes raw pointers.
Capstone is a local research dependency, not a toolkit runtime dependency.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.maps import load_maps
from tools.webfoot.profile import RomProfileCatalog


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("start", type=lambda s: int(s, 0))
    parser.add_argument("end", type=lambda s: int(s, 0))
    args = parser.parse_args()
    maps = load_maps(args.rom, RomProfileCatalog.load("config/roms.yaml"))
    if maps.profile.id != "buus_fury_usa_rev0_01c1707f":
        raise ValueError("TOOLKIT-009 requires the canonical Buu profile")
    data = maps.base_bytes
    start = GbaRomAddress(args.start).to_file_offset(len(data))
    end = GbaRomAddress(args.end).to_file_offset(len(data))
    if start % 2 or end <= start or end - start > 4096:
        raise ValueError("require an even fetch and a bounded <=4096 byte range")
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
    print("Profile:", maps.profile.id, "SHA256:", hashlib.sha256(data).hexdigest())
    for instruction in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(data[start:end], args.start):
        print(f"{instruction.address:08X} {instruction.mnemonic:8s} {instruction.op_str}")
    if hashlib.sha256(args.rom.read_bytes()).digest() != hashlib.sha256(data).digest():
        raise ValueError("canonical input changed during read-only audit")


if __name__ == "__main__":
    main()
