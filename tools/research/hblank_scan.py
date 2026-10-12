"""Does the engine already use HBlank interrupts or HBlank DMA, and where?

Mid-frame palette swapping needs HBlank. Two structural facts decide whether it would conflict with the engine:
whether HBlank interrupts are enabled and serviced, and whether any DMA channel starts on HBlank. Both are
register writes, so they are countable:

  * REG_DISPSTAT (0x04000004) bit 4 is the HBlank interrupt enable, bit 3 the VBlank one;
  * REG_IE (0x04000200) bit 1 is the HBlank interrupt, bit 0 the VBlank one;
  * a DMA channel's control word (0x040000BA + 12*n) has start timing in bits 12..13, where 2 means HBlank.

Addresses are counted as literals and as store targets, so the numbers are writers, not references.
"""

from __future__ import annotations

import struct
from pathlib import Path
from tools.research import rom_paths  # noqa: E402

ROM_BASE = 0x08000000
DISPSTAT = 0x04000004
IE = 0x04000200
DMA0_CONTROL = 0x040000BA
DMA_STRIDE = 12
CHANNELS = 4

image = rom_paths.buu_fury().read_bytes()


def literals(target: int) -> list[int]:
    hits = []
    for offset in range(0, len(image) - 4, 4):
        if struct.unpack_from("<I", image, offset)[0] == target:
            hits.append(offset + ROM_BASE)
    return hits


def main() -> int:
    print(f"DISPSTAT 0x{DISPSTAT:08X}: {len(literals(DISPSTAT))} word-aligned literal(s)")
    for address in literals(DISPSTAT)[:6]:
        context = image[address - ROM_BASE:address - ROM_BASE + 12]
        print(f"  0x{address:08X}: following {context.hex()}")
    print(f"REG_IE   0x{IE:08X}: {len(literals(IE))} word-aligned literal(s)")

    print("\nDMA control words (start timing 2 = HBlank, 1 = VBlank):")
    for channel in range(CHANNELS):
        target = DMA0_CONTROL + DMA_STRIDE * channel
        found = literals(target)
        print(f"  channel {channel} control 0x{target:08X}: {len(found)} literal(s)")
        for address in found[:4]:
            context = image[address - ROM_BASE:address - ROM_BASE + 8]
            word = struct.unpack_from("<H", image, address - ROM_BASE - 2)[0] if address > ROM_BASE else 0
            timing = (word >> 12) & 3
            names = {0: "immediate", 1: "VBlank", 2: "HBlank", 3: "special"}
            print(f"    literal at 0x{address:08X}, preceding halfword 0x{word:04X} "
                  f"-> timing {timing} ({names.get(timing, '?')}), following {context.hex()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
