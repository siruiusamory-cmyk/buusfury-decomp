from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "webfoot"))

import webfoot_lz

ROM_BASE = 0x08000000
BLOCK_START = 0x6A88AC
BLOCK_END = 0x7B79A4
MAX_PAYLOAD = 0x10000
KINDS = (1, 2)
BANK_TABLE = 0x6F395C
BANK_COUNT = 155


def container_offsets(rom: bytes) -> list[int]:
    seeds = []
    for offset in range(BLOCK_START, BLOCK_END - 8 + 1, 4):
        kind, declared = struct.unpack_from("<II", rom, offset)
        if kind in KINDS and 1 <= declared <= MAX_PAYLOAD:
            seeds.append(offset)
    seen: set[int] = set()
    for seed in seeds:
        offset = seed
        while offset not in seen and offset < BLOCK_END:
            kind, declared = struct.unpack_from("<II", rom, offset)
            if kind not in KINDS or not 1 <= declared <= MAX_PAYLOAD:
                if kind in KINDS and declared > MAX_PAYLOAD:
                    raise ValueError("kind %d at %#x declares %d, over the %#x bound"
                                     % (kind, offset, declared, MAX_PAYLOAD))
                break
            try:
                container = webfoot_lz.validate_retail_termination(
                    rom, offset, maximum_output=MAX_PAYLOAD)
            except webfoot_lz.ContainerError:
                break
            if not offset < container.packed_end <= BLOCK_END:
                break
            seen.add(offset)
            offset = container.packed_end
    return sorted(seen)
