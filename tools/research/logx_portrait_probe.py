"""GRAPHICS-COVERAGE-001: deterministic enumerator for the portrait graphics
container population of Buu's Fury.

This is a *research probe*, not a shipping exporter. It reads the canonical image
read-only, refuses any other image by SHA-256, and emits addresses, counts and
sizes only - never a decoded payload.

The portrait population is enumerated SYSTEM-FIRST, from engine code, not from a
byte scan:

1. The appearance-definition consumer ``0x08011F20`` (LOGX-CHAR-001 s11) loads the
   portrait pointer array through a literal in its own constant pool at
   ``0x08012194``. This probe reads that pool word from the ROM to obtain the
   array base, so the base is *derived from the engine*, not hard-coded.
2. The array is walked from slot 8 (``FIRST_ARRAY_SLOT``) to the first slot that
   is not a ROM pointer. LOGX-CHAR-001 established that slots 0..7 are the
   reserved/zero prefix (the accessor returns 0 for indices 0 and 7 without
   reading the array) and the valid pointer run is slots 8..162; slot 163 holds
   ``0x0011E502``, which is not a ROM address, and bounds the array.
3. Each valid slot points at a Webfoot container. The probe decodes each one with
   the accepted project codec (``tools.webfoot.formats.webfoot_lz``) and reports
   the container kind, the declared size and the decoded size.

The population it reproduces (canonical image): **155** portrait containers, all
form 1, each declaring and decoding to exactly 4,096 bytes (INFERRED 64x64 at
8bpp; the container header has no dimension field). This probe enumerates and
self-checks portrait extents only; it does NOT compute disjointness. Whether the
155 are disjoint from every container the accepted sprite / tileset / map graphs
reach (the 11,715-container corpus) is a separate cross-check run by
``logx_gfxscan_probe ... --known``, not this module's output (GRAPHICS-COVERAGE-001).

Graphics identity is reported as CONFIRMED_SHAPE, not CONFIRMED_RENDER: the
consumer ``0x08025056`` passes each pointer to the container dispatcher
``0x0803D940`` (LOGX-CHAR-001 s11.2), every payload decodes to a whole 64x64 8bpp
tile block, and no ROM rendering/palette was captured here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from tools.webfoot.formats import webfoot_lz

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
GBA_BASE = 0x08000000

#: LOGX-CHAR-001 s11: the constant-pool word inside the ``0x08011F20`` accessor
#: that holds the portrait-array base. Reading it from the ROM anchors the array
#: to the engine instead of hard-coding the array address.
PORTRAIT_ARRAY_POOL_WORD = 0x08012194

#: The accessor returns 0 for indices 0 and 7 without touching the array, and its
#: ``cmp r0, #8`` / ``bge`` only reaches the array for indices >= 8, so the first
#: array slot the array path can ever read is slot 8. This bound is the engine's,
#: not a magic number: it is the branch target in the disassembly quoted in
#: LOGX-CHAR-001 s11.1.
FIRST_ARRAY_SLOT = 8

#: Guard against a runaway walk on a corrupt image. The canonical array is 163
#: slots; anything far past that is a bug, not a longer table.
_MAX_SLOTS = 4096


def load_rom(path: str | Path) -> bytes:
    data = Path(path).read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != CANONICAL_SHA256:
        raise SystemExit(
            f"refusing non-canonical image: expected {CANONICAL_SHA256}, got {actual}"
        )
    return data


def _u32(data: bytes, addr: int) -> int:
    off = addr - GBA_BASE
    return struct.unpack_from("<I", data, off)[0]


def _is_rom_ptr(data: bytes, value: int) -> bool:
    return GBA_BASE <= value < GBA_BASE + len(data)


def portrait_array_base(data: bytes) -> int:
    """The portrait-array base, read from the engine accessor's own pool word."""
    base = _u32(data, PORTRAIT_ARRAY_POOL_WORD)
    if not _is_rom_ptr(data, base):
        raise SystemExit(
            f"portrait-array pool word 0x{PORTRAIT_ARRAY_POOL_WORD:08X} = "
            f"0x{base:08X} is not a ROM pointer"
        )
    return base


def portrait_pointers(data: bytes) -> list[int]:
    """Every valid portrait container pointer, in slot order.

    Slots below ``FIRST_ARRAY_SLOT`` are documented zero and are skipped. The walk
    stops at the first slot at or above ``FIRST_ARRAY_SLOT`` that is not a ROM
    pointer, which is how the array bounds itself (slot 163 = 0x0011E502).
    """
    base = portrait_array_base(data)
    pointers: list[int] = []
    slot = FIRST_ARRAY_SLOT
    while slot < _MAX_SLOTS:
        value = _u32(data, base + 4 * slot)
        if not _is_rom_ptr(data, value):
            break
        pointers.append(value)
        slot += 1
    return pointers


def enumerate_portraits(data: bytes) -> dict:
    """Decode every portrait container and summarise the population."""
    base = portrait_array_base(data)
    pointers = portrait_pointers(data)

    kinds: dict[int, int] = {}
    declared_sizes: set[int] = set()
    decoded_sizes: set[int] = set()
    decode_failures = 0
    extents: list[tuple[int, int]] = []
    ascending = all(pointers[i] < pointers[i + 1] for i in range(len(pointers) - 1))

    for ptr in pointers:
        off = ptr - GBA_BASE
        kinds[_u32(data, ptr)] = kinds.get(_u32(data, ptr), 0) + 1
        declared_sizes.add(_u32(data, ptr + 4))
        try:
            container = webfoot_lz.unpack(data, off)
        except webfoot_lz.ContainerError:
            decode_failures += 1
            continue
        decoded_sizes.add(len(container.data))
        extents.append((off, container.packed_end))

    extents.sort()
    overlaps = sum(
        1 for i in range(1, len(extents)) if extents[i][0] < extents[i - 1][1]
    )

    return {
        "rom_sha256": CANONICAL_SHA256.upper(),
        "portrait_array_base": f"0x{base:08X}",
        "portrait_array_pool_word": f"0x{PORTRAIT_ARRAY_POOL_WORD:08X}",
        "portrait_count": len(pointers),
        "pointers_strictly_ascending": ascending,
        "first_pointer": f"0x{pointers[0]:08X}" if pointers else None,
        "last_pointer": f"0x{pointers[-1]:08X}" if pointers else None,
        "container_kinds": kinds,
        "declared_sizes": sorted(declared_sizes),
        "decoded_sizes": sorted(decoded_sizes),
        "decode_failures": decode_failures,
        "packed_extent_overlaps": overlaps,
        "packed_region": (
            f"0x{GBA_BASE + extents[0][0]:08X}..0x{GBA_BASE + extents[-1][1]:08X}"
            if extents
            else None
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", help="canonical Buu's Fury ROM (read-only)")
    parser.add_argument("--json", help="write the report to this path")
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    report = enumerate_portraits(data)
    text = json.dumps(report, indent=2)
    print(text)
    if args.json:
        Path(args.json).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
