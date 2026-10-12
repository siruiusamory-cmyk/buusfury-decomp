"""Every actor-spawn site in every script corpus, with the sprite argument each one pushes.

Read-only. Two corpora place actors in this game and both must be walked, because a census that walks
one and claims completeness is exactly the mistake this tool exists to prevent:

* the map object arrays (an actor that exists when a map loads; the three families with their own
  sprite fields), and
* the event-resource scripts, which can spawn an actor later through native slot 53. Those records
  come in two shapes: type 0, whose code block the repository decodes directly, and type 4, whose
  payload is a headerless Webfoot bitstream that expands at run time through IWRAM. The type-4
  payload is still readable from ROM with the project's own bitstream grammar, using the maximal
  valid decode boundary that docs/research/BUU_EVENT_RESOURCE.md records.

The argument order at a spawn is the order the values were pushed: the first pushed value is the
sprite id, the other two are coordinates (the invariant that page states and that this census
re-checks on every site it finds).

Usage: python -m tools.research.script_spawns --rom ROM.gba [--json OUT.json]
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot.data.placement_contracts import CONTRACTS  # noqa: E402
from tools.webfoot.data.script_specs import OPCODE_SETS  # noqa: E402
from tools.webfoot.formats.placement_links import (  # noqa: E402
    DIALOG_TYPE_CODE_BLOCK, dialog_code_block, event_resource_records)
from tools.webfoot.formats.script_vm import Entry, assemble, decode_instruction, disassemble  # noqa: E402
from tools.webfoot.formats.webfoot_lz import _unpack_stream  # noqa: E402

ROM_BASE = 0x08000000
PROFILE = "buus_fury_usa_rev0_01c1707f"
NATIVE_STACK = 2
PUSH_OPS = {0, 1, 29}
SPAWN_SLOT = 53
DIALOG_CODE_OFFSET = 3
MAP_TABLE = 0x8E2E0
MAP_STRIDE = 0x38
MAP_COUNT = 452
OBJECT_FAMILIES = {0x0800FD55: 0x10, 0x080111A9: 0x0C, 0x08017DA3: 0x10}
TYPE4_MAXIMUM = 2048


def _pushes(instructions, position: int, count: int) -> list[int]:
    """The values a native consumes, in push order.

    `push_many` carries a COUNT as its first operand, which is not a value: it says how many of the
    following operands are pushed. Counting it as a value shifts every argument by one and makes the
    sprite look like a length, which is exactly how a census can miss a spawn.
    """
    values: list[int] = []
    index = position - 1
    while index >= 0 and len(values) < count:
        instruction = instructions[index]
        if instruction.opcode not in PUSH_OPS:
            break
        operands = instruction.operands[1:] if instruction.opcode == 29 else instruction.operands
        for operand in reversed(operands):
            values.append(operand.value)
        index -= 1
    return list(reversed(values))


def _spawns_in(instructions) -> list[dict]:
    found = []
    for position, instruction in enumerate(instructions):
        if instruction.opcode != NATIVE_STACK or not instruction.operands:
            continue
        if instruction.operands[0].value != SPAWN_SLOT:
            continue
        found.append({"position": position,
                      "arguments": _pushes(instructions, position, 3),
                      "source_offset": instruction.source_offset})
    return found


def object_array_sites(image: bytes) -> list[dict]:
    """Every map object slot and the sprite id its own family field carries."""
    sites = []
    for map_index in range(MAP_COUNT):
        entry = MAP_TABLE + MAP_STRIDE * map_index
        runs = image[entry + 0x04]
        array = struct.unpack_from("<I", image, entry + 0x14)[0]
        if array < ROM_BASE or array - ROM_BASE + 4 > len(image):
            continue
        array -= ROM_BASE
        for slot in range(runs):
            pointer = struct.unpack_from("<I", image, array + 4 * slot)[0]
            if pointer < ROM_BASE or pointer - ROM_BASE + 0x1C > len(image):
                continue
            base = pointer - ROM_BASE
            family = struct.unpack_from("<I", image, base)[0]
            if family not in OBJECT_FAMILIES:
                continue
            sites.append({"corpus": "map object array", "map": map_index, "slot": slot,
                          "family": family, "file": base,
                          "sprite": struct.unpack_from("<I", image,
                                                       base + OBJECT_FAMILIES[family])[0]})
    return sites


def type4_payload(image: bytes, dialog: int, kind: int = 1) -> bytes | None:
    """The maximal valid decode of a type-4 payload, or None when nothing decodes."""
    best = None
    for size in range(4, TYPE4_MAXIMUM + 1):
        try:
            decoded, _end = _unpack_stream(image, dialog + 4, size, kind)
        except Exception:
            continue
        best = decoded
    return best


def script_sites(image: bytes) -> tuple[list[dict], list[dict], dict]:
    """Spawn sites in the event-resource corpus, plus every record's decode status."""
    spec = OPCODE_SETS[CONTRACTS[PROFILE]["encoding"]]
    records = event_resource_records(image, CONTRACTS[PROFILE]["event_resource"])
    spawns: list[dict] = []
    undecodable: list[dict] = []
    counts = {"type0": 0, "type4": 0, "type4_undecodable": 0, "other": 0}
    for record in records:
        if record.supported:
            counts["type0"] += 1
            try:
                block = dialog_code_block(image, record, spec)
            except Exception:
                block = None
            if block is None:
                continue
            _start, _raw, ir = block
            for script_block in ir.blocks:
                for spawn in _spawns_in(script_block.instructions):
                    spawns.append({"corpus": "event_resource type 0",
                                   "resource": record.index, "file": record.dialog_offset,
                                   **spawn})
            continue
        if record.dialog_type != 4:
            counts["other"] += 1
            continue
        counts["type4"] += 1
        decoded = type4_payload(image, record.dialog_offset)
        if decoded is None:
            counts["type4_undecodable"] += 1
            undecodable.append({"resource": record.index, "file": record.dialog_offset})
            continue
        try:
            ir = disassemble(decoded, (Entry("payload", 0),), spec)
        except Exception as error:
            undecodable.append({"resource": record.index, "file": record.dialog_offset,
                                "reason": f"not a script: {error}"})
            continue
        if assemble(ir) != decoded:
            undecodable.append({"resource": record.index, "file": record.dialog_offset,
                                "reason": "decoded stream does not round-trip"})
            continue
        for script_block in ir.blocks:
            for spawn in _spawns_in(script_block.instructions):
                spawns.append({"corpus": "event_resource type 4", "resource": record.index,
                               "file": record.dialog_offset, **spawn})
    return spawns, undecodable, counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--json")
    parser.add_argument("--sprite", type=int, action="append", default=[],
                        help="also list the object-array and spawn sites whose sprite is this")
    args = parser.parse_args()
    image = Path(args.rom).read_bytes()
    objects = object_array_sites(image)
    spawns, undecodable, counts = script_sites(image)
    document = {"objects": objects, "spawns": spawns, "undecodable": undecodable,
                "counts": counts}
    print(f"map object slots: {len(objects)}")
    print(f"event resources: type 0 {counts['type0']}, type 4 {counts['type4']} "
          f"({counts['type4_undecodable']} undecodable), other {counts['other']}")
    print(f"native-53 spawn sites: {len(spawns)}")
    for spawn in spawns:
        print(f"  {spawn['corpus']} resource {spawn.get('resource', '-')} "
              f"file 0x{spawn['file']:06X} arguments {spawn['arguments']}")
    for entry in undecodable:
        print(f"  UNDECODABLE resource {entry['resource']} file 0x{entry['file']:06X} "
              f"{entry.get('reason', 'no valid decode')}")
    if args.sprite:
        watched = set(args.sprite)
        print(f"\nsites naming sprite {sorted(watched)}:")
        for site in objects:
            if site["sprite"] in watched:
                print(f"  object map {site['map']} slot {site['slot']} file 0x{site['file']:06X} "
                      f"sprite {site['sprite']}")
        for spawn in spawns:
            if spawn["arguments"] and spawn["arguments"][0] in watched:
                print(f"  spawn {spawn['corpus']} resource {spawn.get('resource', '-')} "
                      f"arguments {spawn['arguments']}")
    if args.json:
        Path(args.json).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        print(f"# wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
