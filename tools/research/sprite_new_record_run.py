"""SPRITE-NEW-RECORD-RUN-001: emit the record-run variant of the new actor.

SPRITE-NEW-RUNTIME-001 authored identity 307 and put a genuinely new object
record on map 102, and the retail engine resolved and drew it. The actor never
moved, and a runtime read of the engine's own dispatch says why in one line: the
pointer handed to the behaviour constructor 0x0800A7A0 is `record + 0x1C`, and it
arrives from a *different* caller (0x0800A9AA) than the map object loop that named
the record (0x08008CC5). The object array is not where the behaviour comes from.

So this script builds SPRITE-NEW-RUNTIME-001's image and then moves the map's
record run, rather than adding one record next to it:

  * the run prefix image[0x0807830C, 0x080784B4) - the 0x10-byte pre-record and the
    ten 0x2C/0x24-byte object records with their behaviour bodies, byte for byte;
  * the new actor's pair, record and behaviour, appended so it is a contiguous
    member of the run exactly as the retail records are;
  * the eleven-slot object array, whose first ten words are the relocated records;
  * MapEntry+0x14 -> the new array, MapEntry+0x2C -> the new run, MapEntry+0x04 -> 11.

The tail of the slice (0x080784DC..0x08078584) is deliberately NOT moved. It stays
canonical and the two MapEntry fields that name it (+0x10, +0x68) keep their
canonical values, so the change is bounded to the object run and the array.

Everything the identity itself consists of - the relocated 298-entry registry, the
new character structure, the animations, the frames and the containers - is built
by `sprite_new_runtime.build_experiment(target="new-actor")` and is reused
unmodified. This script changes only where the actor's record sits.

Read-only with respect to the canonical image: it is opened for reading and its
digest is checked before anything is planned.

    python tools/research/sprite_new_record_run.py --rom <canonical> --out <gba>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_REPO = _HERE.parents[2]
_TOOLS = _HERE.parents[1]
for candidate in (str(_REPO), str(_TOOLS)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from research import sprite_new_runtime as snr  # noqa: E402

ROM_BASE = 0x08000000
CANONICAL_SHA256 = snr.CANONICAL_SHA256

#: Map 102, West City park. Measured from the canonical image and confirmed at
#: runtime by this ticket's observer (`maps.txt`: count 10, array 0x080784B4,
#: stream 0x0807830C).
MAP_ENTRY_102 = 0x0808F930
MAP_COUNT_FIELD = 0x04
MAP_ARRAY_FIELD = 0x14
MAP_STREAM_FIELD = 0x2C

#: The map's +0x2C slice, bounded by the next map's slice base (0x08078584).
RUN_START = 0x0807830C
RUN_OBJECTS_END = 0x080784B4          # the canonical object array starts here
RUN_SLICE_END = 0x08078584
OBJECT_ARRAY_AT = RUN_OBJECTS_END
CANONICAL_SLOT_COUNT = 10

#: The new actor, carried over from SPRITE-NEW-RUNTIME-001 unchanged. Its record is
#: re-emitted from the base build's own bytes so the identity material is not
#: re-derived here.
ACTOR_POSITION_RAW = 0x024400D1       # x 209, y 580 - the runtime build's position
CLONE_RECORD_ROM = 0x08801F38         # the base build's record, in the expansion
RECORD_HEADER_SIZE = 0x1C
RECORD_TOTAL_SIZE = 0x2C
RECORD_PREV_FIELD = 0x18

BEHAVIOUR_PAIR_SIZE = RECORD_TOTAL_SIZE

#: Where the generated expansion begins, and the fill a generated image has.
EXPANSION_START = 0x08800000
EXPANSION_END = 0x09000000
GENERATED_FILL = 0xFF
ALIGNMENT = 4


class RecordRunError(ValueError):
    """An input this experiment cannot honour."""


def align_up(value: int, alignment: int = ALIGNMENT) -> int:
    return (value + alignment - 1) // alignment * alignment


def u32(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address - ROM_BASE)[0]


def high_water_mark(image: bytes) -> int:
    """The highest generated word that is not the expansion's fill.

    Scanned from the top so the answer is the last byte the base build actually
    used; everything above it is free for this ticket's material.
    """
    address = EXPANSION_END - 4
    while address >= EXPANSION_START:
        if image[address - ROM_BASE: address - ROM_BASE + 4] != bytes([GENERATED_FILL] * 4):
            return address + 4
        address -= 4
    return EXPANSION_START


def rebase_word(value: int, run_addr: int, array_addr: int) -> int:
    """A word that named something inside the run prefix, re-pointed at its copy.

    Only the prefix is rebased. A word naming the array or the slice tail is not
    expected inside the prefix, and one would mean the run carries an internal
    reference this relocation does not model, so it is refused rather than
    silently collapsed onto a single address.
    """
    if RUN_START <= value < RUN_OBJECTS_END:
        return run_addr + (value - RUN_START)
    if RUN_OBJECTS_END <= value < RUN_SLICE_END:
        raise RecordRunError(
            f"the run prefix names 0x{value:08X}, which is outside the prefix; "
            "the relocation does not model that reference")
    return value


def build_variant(base: bytes, canonical: bytes) -> tuple[bytes, dict]:
    """Apply the run relocation to the base build's image."""
    out = bytearray(base)

    run_addr = align_up(high_water_mark(base) + 16)
    pair_addr = run_addr + (RUN_OBJECTS_END - RUN_START)
    array_addr = align_up(pair_addr + BEHAVIOUR_PAIR_SIZE)
    block_end = array_addr + 4 * (CANONICAL_SLOT_COUNT + 1)
    if block_end >= EXPANSION_END:
        raise RecordRunError("the expansion has no room for the relocated run")

    # --- 1. the run prefix, byte for byte, with its internal names re-pointed
    prefix = bytearray(canonical[RUN_START - ROM_BASE: RUN_OBJECTS_END - ROM_BASE])
    for offset in range(0, len(prefix) - 3, 4):
        value = struct.unpack_from("<I", prefix, offset)[0]
        struct.pack_into("<I", prefix, offset, rebase_word(value, run_addr, array_addr))
    out[run_addr - ROM_BASE: run_addr - ROM_BASE + len(prefix)] = prefix

    # --- 2. the new actor's pair: the base build's own record and behaviour bytes
    pair = bytearray(base[CLONE_RECORD_ROM - ROM_BASE:
                          CLONE_RECORD_ROM - ROM_BASE + BEHAVIOUR_PAIR_SIZE])
    if len(pair) != BEHAVIOUR_PAIR_SIZE:
        raise RecordRunError("the base build's record is not the expected size")
    position = struct.unpack_from("<I", pair, 0x08)[0]
    sprite_id = struct.unpack_from("<I", pair, 0x10)[0]
    if position != ACTOR_POSITION_RAW:
        raise RecordRunError(
            f"the base build's record is not at the measured position "
            f"(0x{position:08X}, expected 0x{ACTOR_POSITION_RAW:08X})")
    if sprite_id != snr.NEW_SPRITE_ID:
        raise RecordRunError(
            f"the base build's record names sprite {sprite_id}, not "
            f"{snr.NEW_SPRITE_ID}")
    previous = struct.unpack_from("<I", pair, RECORD_PREV_FIELD)[0]
    struct.pack_into("<I", pair, RECORD_PREV_FIELD,
                     rebase_word(previous, run_addr, array_addr))
    out[pair_addr - ROM_BASE: pair_addr - ROM_BASE + BEHAVIOUR_PAIR_SIZE] = pair

    # --- 3. the object array, one slot longer, all ten canonical words carried
    slots = [u32(canonical, OBJECT_ARRAY_AT + 4 * i) for i in range(CANONICAL_SLOT_COUNT)]
    relocated = [rebase_word(slot, run_addr, array_addr) for slot in slots]
    relocated.append(pair_addr)
    for i, value in enumerate(relocated):
        struct.pack_into("<I", out, array_addr - ROM_BASE + 4 * i, value)

    # --- 4. the three MapEntry fields that name what moved
    count_at = MAP_ENTRY_102 + MAP_COUNT_FIELD
    array_at = MAP_ENTRY_102 + MAP_ARRAY_FIELD
    stream_at = MAP_ENTRY_102 + MAP_STREAM_FIELD
    before = {
        "count": canonical[count_at - ROM_BASE],
        "array": u32(canonical, array_at),
        "stream": u32(canonical, stream_at),
    }
    out[count_at - ROM_BASE] = CANONICAL_SLOT_COUNT + 1
    struct.pack_into("<I", out, array_at - ROM_BASE, array_addr)
    struct.pack_into("<I", out, stream_at - ROM_BASE, run_addr)

    report = {
        "run_source": f"0x{RUN_START:08X}",
        "run_prefix_bytes": RUN_OBJECTS_END - RUN_START,
        "relocated_run": f"0x{run_addr:08X}",
        "new_pair": f"0x{pair_addr:08X}",
        "relocated_array": f"0x{array_addr:08X}",
        "array_slots": len(relocated),
        "block_end": f"0x{block_end:08X}",
        "map_entry_before": {k: (f"0x{v:08X}" if k != "count" else v)
                             for k, v in before.items()},
        "map_entry_after": {"count": CANONICAL_SLOT_COUNT + 1,
                            "array": f"0x{array_addr:08X}",
                            "stream": f"0x{run_addr:08X}"},
        "relocated_slots": [f"0x{v:08X}" for v in relocated],
        "new_record_previous_field": f"0x{struct.unpack_from('<I', pair, RECORD_PREV_FIELD)[0]:08X}",
    }
    return bytes(out), report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rom", required=True, help="the canonical image")
    parser.add_argument("--out", required=True, help="the variant image to write")
    parser.add_argument("--manifest", help="write the delta report here")
    parser.add_argument(
        "--sheet", required=True,
        help="a Cui sheet PNG; the artwork is a private research input and is "
             "not tracked in this repository")
    parser.add_argument("--cell", type=int, default=0)
    args = parser.parse_args(argv)

    canonical = Path(args.rom).read_bytes()
    if hashlib.sha256(canonical).hexdigest() != CANONICAL_SHA256:
        print("refusing: the input is not the canonical image this experiment "
              "was measured against")
        return 2

    from webfoot.profile import RomProfileCatalog
    from webfoot.rom import identify_rom

    catalog = RomProfileCatalog.load(str(_REPO / "config" / "roms.yaml"))
    identification = identify_rom(Path(args.rom), catalog)
    experiment = snr.build_experiment(canonical, identification, Path(args.sheet),
                                      args.cell, target="new-actor")
    base = experiment.output(canonical)

    variant, delta = build_variant(base, canonical)
    Path(args.out).write_bytes(variant)

    report = {
        "ticket": "SPRITE-NEW-RECORD-RUN-001",
        "canonical_sha256": CANONICAL_SHA256,
        "base_sha256": hashlib.sha256(base).hexdigest(),
        "variant_sha256": hashlib.sha256(variant).hexdigest(),
        "variant_size": len(variant),
        "base_identity_report": experiment.report,
        "run_delta": delta,
    }
    if args.manifest:
        Path(args.manifest).write_text(
            json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k != "base_identity_report"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
