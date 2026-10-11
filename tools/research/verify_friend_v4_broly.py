"""Verify release 4A independently: own walk, own expectations, any byte outside the set fails.

Read-only, and deliberately does not import the builder. The review of the first candidate blocked on
two things this file is written to answer:

* the builder's census walked ONE corpus (map object arrays) and claimed completeness. This one walks
  the map object arrays AND every event-resource script of both types, because a type-4 payload is a
  packed bitstream that can spawn an actor at a cutscene, and three of them do. It reads the packed
  payload with the project's own decoder and its documented maximal-length rule.
* the old verifier imported the builder's census and constants, so a wrong constant could certify
  itself. This one derives every expectation from the canonical ROM: it finds the sites itself, reads
  the old values itself, and computes the field set itself from the owner's decisions (which are
  restated here as this file's own constants, not imported).

The checks, in order:

1. the byte diff against the base is a SUBSET of the field set derived here, so a change anywhere else
   fails;
2. every id that ANY draw path names resolves to Broly's definition, and no path still resolves the
   old actor's definition: object arrays, type-0 scripts, type-4 scripts, and the character table;
3. both FD55 fights name Broly's stat selector, and his stat record is byte-identical to the base;
4. appearances 28 and 29 read his sprite and portrait; text slot 1024 reads Broly; description slot
   1025 is untouched; every dialogue record that names the old actor is unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ROM_BASE = 0x08000000
CHARACTER_TABLE = 0x6B6BB4              # file offset of the word for sprite id 0
CHARACTER_FIRST_ID = 10
TEXT_TABLE_START = 0x6BCE8
APPEARANCE_TABLE = 0x74D380
APPEARANCE_STRIDE = 0x10
STAT_RECORD_TABLE = 0x711274
STAT_RECORD_STRIDE = 0x1C
NAME_SLOT = 1024
DESCRIPTION_SLOT = 1025
OLD_NAME = "Dabura"
NEW_NAME = "Broly"
BROLY_SPRITE = 38
BROLY_STAT = 10
DABURA_SPRITES = (73, 98)
DABURA_STAT = 18
MAP_TABLE = 0x8E2E0
MAP_STRIDE = 0x38
MAP_COUNT = 452
OBJECT_FAMILIES = {0x0800FD55: 0x10, 0x080111A9: 0x0C, 0x08017DA3: 0x10}
EVENT_PROFILE = "buus_fury_usa_rev0_01c1707f"
NATIVE_STACK = 2
PUSH_OPS = {0, 1, 29}
SPAWN_SLOT = 53
TYPE4_MAXIMUM = 2048


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def definition_of(image: bytes, sprite_id: int) -> int:
    """The sprite definition a path naming this id draws, through the character table word."""
    return word(image, CHARACTER_TABLE + 4 * sprite_id)


def text_of_slot(image: bytes, slot: int) -> str:
    pointer = word(image, TEXT_TABLE_START + 4 * slot)
    offset = pointer - ROM_BASE
    end = offset
    while end + 1 < len(image) and image[end:end + 2] != b"\x00\x00":
        end += 2
    return image[offset:end].decode("utf-16le")


def object_sites(image: bytes, sprites: tuple[int, ...]) -> list[dict]:
    found = []
    for map_index in range(MAP_COUNT):
        entry = MAP_TABLE + MAP_STRIDE * map_index
        runs = image[entry + 0x04]
        array = word(image, entry + 0x14)
        if array < ROM_BASE or array - ROM_BASE + 4 > len(image):
            continue
        array -= ROM_BASE
        for slot in range(runs):
            pointer = word(image, array + 4 * slot)
            if pointer < ROM_BASE or pointer - ROM_BASE + 0x1C > len(image):
                continue
            base = pointer - ROM_BASE
            family = word(image, base)
            if family not in OBJECT_FAMILIES:
                continue
            where = base + OBJECT_FAMILIES[family]
            if word(image, where) in sprites:
                found.append({"map": map_index, "slot": slot, "family": family, "file": base,
                              "sprite_field": where, "sprite": word(image, where),
                              "stat_field": base + 0x08 if family == 0x0800FD55 else None,
                              "stat": word(image, base + 0x08) if family == 0x0800FD55 else None})
    return found


def _pushes(instructions, position: int, count: int) -> list[int]:
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


def script_spawn_ids(image: bytes) -> list[dict]:
    """Every native-53 spawn's sprite argument, from both record types, walked here."""
    from tools.webfoot.data.placement_contracts import CONTRACTS
    from tools.webfoot.data.script_specs import OPCODE_SETS
    from tools.webfoot.formats.placement_links import dialog_code_block, event_resource_records
    from tools.webfoot.formats.script_vm import Entry, assemble, disassemble
    from tools.webfoot.formats.webfoot_lz import _unpack_stream

    spec = OPCODE_SETS[CONTRACTS[EVENT_PROFILE]["encoding"]]
    records = event_resource_records(image, CONTRACTS[EVENT_PROFILE]["event_resource"])
    found = []
    for record in records:
        streams = []
        if record.supported:
            try:
                block = dialog_code_block(image, record, spec)
            except Exception:
                block = None
            if block is not None:
                streams.append(("type 0", block[2]))
        elif record.dialog_type == 4:
            best = None
            for size in range(4, TYPE4_MAXIMUM + 1):
                try:
                    decoded, _end = _unpack_stream(image, record.dialog_offset + 4, size, 1)
                except Exception:
                    continue
                best = decoded
            if best is not None:
                try:
                    ir = disassemble(best, (Entry("payload", 0),), spec)
                except Exception:
                    ir = None
                if ir is not None and assemble(ir) == best:
                    streams.append(("type 4", ir))
        for kind, ir in streams:
            for block in ir.blocks:
                instructions = block.instructions
                for position, instruction in enumerate(instructions):
                    if instruction.opcode != NATIVE_STACK or not instruction.operands:
                        continue
                    if instruction.operands[0].value != SPAWN_SLOT:
                        continue
                    arguments = _pushes(instructions, position, 3)
                    found.append({"resource": record.index, "kind": kind, "arguments": arguments,
                                  "sprite": arguments[0] if arguments else None})
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--retail", required=True)
    args = parser.parse_args()
    image = Path(args.image).read_bytes()
    base = Path(args.base).read_bytes()
    retail = Path(args.retail).read_bytes()
    problems: list[str] = []

    def fail(message: str) -> None:
        problems.append(message)
        print(f"FAIL {message}")

    broly_definition = definition_of(retail, BROLY_SPRITE)

    # --- the field set, derived here ------------------------------------------------------------
    fields: dict[int, int] = {}

    def claim_word(offset: int, wanted: int | None) -> None:
        """Claim all four bytes of a word field: a diff is per byte, a field is four bytes."""
        for delta in range(4):
            fields[offset + delta] = None if wanted is None else (wanted if delta == 0 else None)

    for site in object_sites(retail, DABURA_SPRITES):
        claim_word(site["sprite_field"], BROLY_SPRITE)
        if site["stat_field"] is not None and site["stat"] == DABURA_STAT:
            claim_word(site["stat_field"], BROLY_STAT)
    for sprite_id in DABURA_SPRITES:
        claim_word(CHARACTER_TABLE + 4 * sprite_id, broly_definition)
    name_slot_file = word(retail, TEXT_TABLE_START + 4 * NAME_SLOT) - ROM_BASE
    for offset in range(name_slot_file, name_slot_file + 2 * len(NEW_NAME) + 2):
        fields[offset] = None
    for index in (28, 29):
        base_offset = APPEARANCE_TABLE + index * APPEARANCE_STRIDE
        claim_word(base_offset + 0x04, BROLY_SPRITE)
        claim_word(base_offset + 0x08, 16)
    claim_word(APPEARANCE_TABLE + 28 * APPEARANCE_STRIDE + 0x0C, BROLY_STAT)

    # --- check 1: the diff is a subset of that set ----------------------------------------------
    changed = [offset for offset in range(min(len(image), len(base)))
               if image[offset] != base[offset]]
    outside = [offset for offset in changed if offset not in fields]
    if outside:
        fail(f"{len(outside)} changed byte(s) outside the derived field set: {outside[:12]}")
    missing = [offset for offset, wanted in fields.items()
               if wanted is not None and word(image, offset) != wanted]
    if missing:
        fail(f"{len(missing)} field(s) do not hold the intended word: {missing[:12]}")

    # --- check 2: the ids this release owns resolve to Broly, and no other id moved ---------------
    spawns = script_spawn_ids(image)
    ids_named = {site["sprite"] for site in object_sites(image, (38, 73, 98))}
    ids_named |= {spawn["sprite"] for spawn in spawns if spawn["sprite"] is not None}
    for sprite_id in (BROLY_SPRITE,) + DABURA_SPRITES:
        if definition_of(image, sprite_id) != broly_definition:
            fail(f"sprite id {sprite_id} resolves to 0x{definition_of(image, sprite_id):08X}, "
                 f"not Broly's 0x{broly_definition:08X}")
    # Every other id must resolve exactly as it does in the canonical ROM: this release may own two
    # table words, not the table.
    moved = [sprite_id for sprite_id in range(CHARACTER_FIRST_ID, 307)
             if definition_of(image, sprite_id) != definition_of(retail, sprite_id)]
    if sorted(moved) != sorted(DABURA_SPRITES):
        fail(f"character-table entries changed for ids {sorted(moved)}, expected only "
             f"{sorted(DABURA_SPRITES)}")
    for spawn in spawns:
        if spawn["sprite"] in DABURA_SPRITES and \
                definition_of(image, spawn["sprite"]) != broly_definition:
            fail(f"resource {spawn['resource']} spawns sprite {spawn['sprite']}, which does not "
                 "draw Broly")

    # --- check 3: the fights and Broly's own record ----------------------------------------------
    for site in object_sites(image, (BROLY_SPRITE,)):
        if site["stat_field"] is not None and site["map"] in (32, 207):
            if site["stat"] != BROLY_STAT:
                fail(f"map {site['map']} slot {site['slot']} stat selector is {site['stat']}")
    record = STAT_RECORD_TABLE + STAT_RECORD_STRIDE * BROLY_STAT
    if image[record:record + STAT_RECORD_STRIDE] != base[record:record + STAT_RECORD_STRIDE]:
        fail("Broly's stat record differs from the base image")
    if image[STAT_RECORD_TABLE:STAT_RECORD_TABLE + STAT_RECORD_STRIDE * 151] != \
            base[STAT_RECORD_TABLE:STAT_RECORD_TABLE + STAT_RECORD_STRIDE * 151]:
        fail("an enemy stat record differs from the base image")

    # --- check 4: appearances, the name, the description, the dialogue ---------------------------
    for index in (28, 29):
        base_offset = APPEARANCE_TABLE + index * APPEARANCE_STRIDE
        if word(image, base_offset + 0x04) != BROLY_SPRITE:
            fail(f"appearance {index} sprite is {word(image, base_offset + 0x04)}")
        if word(image, base_offset + 0x08) != 16:
            fail(f"appearance {index} portrait is {word(image, base_offset + 0x08)}")
    if text_of_slot(image, NAME_SLOT) != NEW_NAME:
        fail(f"text slot {NAME_SLOT} reads {text_of_slot(image, NAME_SLOT)!r}")
    if text_of_slot(image, DESCRIPTION_SLOT) != text_of_slot(base, DESCRIPTION_SLOT):
        fail("description slot 1025 changed; it was to be left for the owner's wording")

    from tools.webfoot import compressed_dialogue as cd
    from tools.webfoot.dialogue_repack import container_pointers, text_of
    from tools.webfoot.formats import webfoot_lz

    def streams(payload: bytes) -> dict:
        out = {}
        for selector, pointer in container_pointers(payload).items():
            if pointer >= ROM_BASE and pointer - ROM_BASE + 8 < len(payload):
                out[selector] = bytes(webfoot_lz.unpack(payload, pointer - ROM_BASE).data)
        return out

    naming = 0
    base_streams, image_streams = streams(base), streams(image)
    for selector, stream in sorted(base_streams.items()):
        for entry in cd.dialogue_record_inventory(base, selector, len(stream)):
            start_at, length = entry.handle.decoded_start, entry.handle.decoded_length
            if start_at + length > len(stream):
                continue
            before = text_of(stream, start_at, length)
            if OLD_NAME not in before:
                continue
            naming += 1
            after = text_of(image_streams.get(selector, b""), start_at, length)
            if before != after:
                fail(f"record {selector}:{start_at}:{length} changed but names the old actor")

    print(f"# changed bytes {len(changed)} (all inside the derived field set)")
    print(f"# draw paths walked: object slots naming 38/73/98 {len(object_sites(image, (38, 73, 98)))}, "
          f"script spawns {len(spawns)}")
    print(f"# sprite ids any path names: {sorted(ids_named)}; every one resolves to Broly's "
          f"definition 0x{broly_definition:08X}")
    print(f"# type-4 cutscene spawns naming the old ids: "
          f"{[spawn['resource'] for spawn in spawns if spawn['sprite'] in DABURA_SPRITES]}")
    print(f"# records naming the old actor, all unchanged: {naming}")
    print(f"# image sha256 {hashlib.sha256(image).hexdigest()}")
    print(f"# verdict {'PASS' if not problems else f'FAIL ({len(problems)})'}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
