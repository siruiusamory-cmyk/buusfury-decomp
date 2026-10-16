"""Build the DIALOGUE-RENDER-PATH-001 ordinary-character diagnostic image.

WHAT IT PROVES. The ticket asks for exactly one minimal causal diagnostic that
makes an ORDINARY spoken character visibly change without touching the dialogue
record. The strip-composition path is:

    0x0800B05C  ldrb r0,[r6,#0x4]      x  = strip->x
    0x0800B05E  ldrb r1,[r6,#0x5]      y  = strip->y
    0x0800B060  str  r0,[r5,#0x4]      compose cursor x := x
    0x0800B062  str  r1,[r5,#0x8]      compose cursor y := y
    0x0800B064  ldr  r0,[r4,#0x14]     r0 = source cursor
    0x0800B066  ldrh r1,[r0,#0x0]      r1 = THE SOURCE UNIT (the glyph identity)
    0x0800B068  add  r0,r5,#0x0        r0 = strip descriptor
    0x0800B06A  bl   0x0803DE50        compose_glyph(strip, unit)
    0x0800B06E  ldr  r2,[r4,#0x14]     r2 = source cursor
    0x0800B070  ldrh r0,[r2,#0x0]      r0 = the SAME unit, for the width lookup
    0x0800B08E  strb r0,[r6,#0x4]      strip->x := width(unit)+1+x
    0x0800B092  str  r2,[r4,#0x14]     source cursor += 2  (consume ONE unit)

THE EDIT is the single two-byte instruction at file offset 0x00B066: the load
that takes the glyph identity out of the source unit becomes `movs r1,#0x41`,
so every composed ordinary glyph is the same letter ('A'). The width lookup at
0x0800B070 reads the unit from the cursor a second time, so the advance and the
consume accounting are untouched: the dialogue record, the number of composed
units and the line layout all stay identical, and only the drawn glyph changes.

The control is the unpatched canonical image in the same observer, run
build/runtime-roms/../toolkit031/renderpath-02, on the same savestate.

It refuses unless the canonical digest and the exact canonical bytes at the edit
site both match, and it reads the patch back, because an earlier session shipped
a cave whose displaced instruction was encoded wrong and only an assert from the
ROM bytes caught it.

Nothing here writes to the canonical image.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
EDIT_OFFSET = 0x00B066
CANONICAL_BYTES = bytes([0x01, 0x88])  # ldrh r1,[r0,#0x0] == 0x8801, little-endian
PATCHED_BYTES = bytes([0x41, 0x21])  # movs r1,#0x41 == 0x2141


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(source: Path, destination: Path) -> str:
    digest = sha256(source)
    if digest != CANONICAL_SHA256:
        raise SystemExit(f"source is not the canonical image: {digest}")
    image = bytearray(source.read_bytes())
    original = bytes(image)
    found = bytes(image[EDIT_OFFSET : EDIT_OFFSET + len(CANONICAL_BYTES)])
    if found != CANONICAL_BYTES:
        raise SystemExit(
            f"edit site is not the expected instruction: {found.hex()} "
            f"at 0x{EDIT_OFFSET:06X}"
        )
    image[EDIT_OFFSET : EDIT_OFFSET + len(PATCHED_BYTES)] = PATCHED_BYTES
    if bytes(image[EDIT_OFFSET : EDIT_OFFSET + 2]) != PATCHED_BYTES:
        raise SystemExit("patch did not read back")
    changed = sum(1 for a, b in zip(image, original) if a != b)
    if changed != 2:
        raise SystemExit(f"patch changed {changed} bytes, expected exactly 2")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(bytes(image))
    if sha256(source) != CANONICAL_SHA256:
        raise SystemExit("the canonical image changed during the build")
    return sha256(destination)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    source = root / "roms" / "Dragon Ball Z - Buu's Fury (U).gba"
    destination = root / "build" / "runtime-roms" / "dialogue-glyphpin.gba"
    print(f"source      : {source}")
    print(f"canonical   : {sha256(source)}")
    print(f"destination : {destination}")
    print(f"built sha256: {build(source, destination)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
