"""Who uses which palette index: a census over actors, portraits and the box art.

The owner's question is whether a palette can be expanded without changing other actors. That turns on a
single measurement: which of the 256 shared indices each consumer actually paints. Two static lanes
established the sharing structurally (no actor definition and no portrait slot carries a palette pointer,
and every piece is 256-colour mode), and this tool counts the pixel usage that sits underneath it.

Audiences counted separately, because a route decision depends on knowing which ones collide:

* ``actors``    - every piece of every sprite definition reachable through ``0x086B6BB4``
* ``portraits`` - every slot of the portrait array at ``0x086F393C``
* ``box``       - the two dialogue-box surfaces at file ``0x71758`` and ``0x71A6C``

Read-only: the ROM is opened read-only and nothing is written except a caller-named JSON.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot.formats import webfoot_lz  # noqa: E402

ROM_BASE = 0x08000000
DEFINITION_TABLE = 0x6B6BB4
PORTRAIT_ARRAY = 0x6F393C
BOX_SURFACES = (0x71758, 0x71A6C)
FIRST_SPRITE_ID = 10
LAST_SPRITE_ID = 306
PIECE_STRIDE = 12


def pointer(image: bytes, offset: int) -> int | None:
    if offset + 4 > len(image):
        return None
    word = struct.unpack_from("<I", image, offset)[0]
    return word if ROM_BASE <= word < ROM_BASE + len(image) else None


def decode_into(index_bytes: bytes, counter: Counter) -> None:
    counter.update(index_bytes)


#: How far into a frame its container pointers may sit. Measured on sprite 73: the first frame's
#: container is at word 4 of the frame, and a frame with several pieces repeats that spacing.
FRAME_SCAN_WORDS = 64


def sprite_pieces(image: bytes, sprite_id: int) -> list[int]:
    """Candidate graphics containers of one sprite: every ROM pointer inside its frames.

    The piece record's exact layout is NOT established, so this does not pretend to walk it: for each
    frame it scans a bounded window and keeps every word that is a ROM pointer. The decoder then decides
    which of those are really containers, which is a measurement rather than an assumption.
    """
    definition = pointer(image, DEFINITION_TABLE + 4 * sprite_id)
    if definition is None:
        return []
    base = definition - ROM_BASE
    animation_count = image[base] & 0xFF
    containers = []
    array = base + 0x54
    for slot in range(animation_count):
        record_pointer = pointer(image, array + 4 * slot)
        if record_pointer is None:
            continue
        record = record_pointer - ROM_BASE
        if record + 4 > len(image):
            continue
        frame_count = struct.unpack_from("<I", image, record)[0]
        if frame_count == 0 or frame_count > 64:
            continue
        for frame in range(frame_count):
            for direction in range(4):
                entry = record + 4 + 16 * frame + 4 * direction
                frame_pointer = pointer(image, entry)
                if frame_pointer is None:
                    continue
                cursor = frame_pointer - ROM_BASE
                for word in range(FRAME_SCAN_WORDS):
                    if cursor + 4 * word + 4 > len(image):
                        break
                    candidate = pointer(image, cursor + 4 * word)
                    if candidate is not None:
                        containers.append(candidate - ROM_BASE)
    return containers


def decode_container(image: bytes, offset: int) -> bytes | None:
    try:
        return bytes(webfoot_lz.unpack(image, offset).data)
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--json")
    args = parser.parse_args()
    image = Path(args.rom).read_bytes()

    counts = {"actors": Counter(), "portraits": Counter(), "box": Counter()}
    decoded = {"actors": 0, "portraits": 0, "box": 0}
    failed = 0

    # One container may appear in many frames; for a pixel census it must count once.
    visited: set[int] = set()
    for sprite_id in range(FIRST_SPRITE_ID, LAST_SPRITE_ID + 1):
        for offset in sprite_pieces(image, sprite_id):
            if offset in visited:
                continue
            visited.add(offset)
            payload = decode_container(image, offset)
            if payload is None:
                continue
            decode_into(payload, counts["actors"])
            decoded["actors"] += 1

    slot = 0
    while True:
        entry = pointer(image, PORTRAIT_ARRAY + 4 * slot)
        slot += 1
        if entry is None:
            if slot > 200:
                break
            continue
        payload = decode_container(image, entry - ROM_BASE)
        if payload is None:
            failed += 1
            continue
        decode_into(payload, counts["portraits"])
        decoded["portraits"] += 1

    for offset in BOX_SURFACES:
        payload = decode_container(image, offset)
        if payload is None:
            failed += 1
            continue
        decode_into(payload, counts["box"])
        decoded["box"] += 1

    print(f"decoded: {decoded}, failures: {failed}")
    index = range(256)
    used_actors = {i for i in index if counts["actors"][i]}
    used_portraits = {i for i in index if counts["portraits"][i]}
    used_box = {i for i in index if counts["box"][i]}
    print(f"indices painted by actors:    {len(used_actors)}")
    print(f"indices painted by portraits: {len(used_portraits)}")
    print(f"indices painted by the box:   {len(used_box)}")
    print(f"indices painted by actors AND portraits: "
          f"{len(used_actors & used_portraits)}")
    print(f"indices painted by nobody: {sorted(set(index) - used_actors - used_portraits - used_box)}")
    print("\nindex  actors  portraits  box  (top 12 by total pixels)")
    order = sorted(index, key=lambda i: -(counts["actors"][i] + counts["portraits"][i]
                                          + counts["box"][i]))[:12]
    for i in order:
        print(f"{i:>5}  {counts['actors'][i]:>6}  {counts['portraits'][i]:>9}  {counts['box'][i]:>3}")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "decoded": decoded, "failures": failed,
            "used": {"actors": sorted(used_actors), "portraits": sorted(used_portraits),
                     "box": sorted(used_box)},
            "unused": sorted(set(index) - used_actors - used_portraits - used_box),
            "counts": {audience: {str(i): value for i, value in sorted(counter.items())}
                       for audience, counter in counts.items()},
        }, indent=2) + "\n", encoding="utf-8")
        print(f"\n# wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
