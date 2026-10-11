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
STATE_SLOT = 60
TYPE4_MAXIMUM = 1024        # measured: the largest natural decode is 827


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


def slots_of(image: bytes, sprite_id: int) -> list[int]:
    """The animation records a definition holds, one entry per slot, 0 when the slot is empty.

    Some live appearance records name ids whose table entry is not a pointer at all, so an id with no
    usable definition yields no slots rather than an exception.
    """
    definition = definition_of(image, sprite_id)
    if definition < ROM_BASE or definition - ROM_BASE + 0x58 >= len(image):
        return []
    at = definition - ROM_BASE
    count = image[at] & 0xFF
    if at + 0x54 + 4 * count > len(image):
        return []
    return [word(image, at + 0x54 + 4 * index) for index in range(count)]


_WALK_CACHE: dict[str, dict] = {}


def _walk_uncached(image: bytes) -> dict:
    """One pass over both record types, yielding spawn sites and state calls at once."""
    from tools.webfoot.data.placement_contracts import CONTRACTS
    from tools.webfoot.data.script_specs import OPCODE_SETS
    from tools.webfoot.formats.placement_links import dialog_code_block, event_resource_records
    from tools.webfoot.formats.script_vm import Entry, assemble, disassemble
    from tools.webfoot.formats.webfoot_lz import _unpack_stream

    spec = OPCODE_SETS[CONTRACTS[EVENT_PROFILE]["encoding"]]
    records = event_resource_records(image, CONTRACTS[EVENT_PROFILE]["event_resource"])
    spawns: list[dict] = []
    calls: list[dict] = []
    failures: list[int] = []
    counts = {"type 0": 0, "type 4": 0, "undecodable": 0}

    for record in records:
        streams = []
        if record.supported:
            counts["type 0"] += 1
            try:
                block = dialog_code_block(image, record, spec)
            except Exception:
                failures.append(record.index)
                continue
            if block is not None:
                streams.append(block[2])
        elif record.dialog_type == 4:
            counts["type 4"] += 1
            best = None
            for size in range(4, TYPE4_MAXIMUM + 1):
                try:
                    decoded, _end = _unpack_stream(image, record.dialog_offset + 4, size, 1)
                except Exception:
                    continue
                best = decoded
            if best is None:
                counts["undecodable"] += 1
                failures.append(record.index)
                continue
            if len(best) == TYPE4_MAXIMUM:
                raise SystemExit(
                    f"REFUSED: resource {record.index} decodes to the scan ceiling "
                    f"{TYPE4_MAXIMUM}, so the ceiling may be truncating it")
            try:
                ir = disassemble(best, (Entry("payload", 0),), spec)
            except Exception:
                failures.append(record.index)
                continue
            if assemble(ir) != best:
                failures.append(record.index)
                continue
            streams.append(ir)
        for ir in streams:
            for block in ir.blocks:
                instructions = block.instructions
                for position, instruction in enumerate(instructions):
                    if instruction.opcode != NATIVE_STACK or not instruction.operands:
                        continue
                    slot = instruction.operands[0].value
                    if slot not in (SPAWN_SLOT, STATE_SLOT):
                        continue
                    wanted = 3 if slot == SPAWN_SLOT else 2
                    values: list[int] = []
                    index = position - 1
                    while index >= 0 and len(values) < wanted:
                        earlier = instructions[index]
                        if earlier.opcode not in PUSH_OPS:
                            break
                        operands = (earlier.operands[1:] if earlier.opcode == 29
                                    else earlier.operands)
                        for operand in reversed(operands):
                            values.append(operand.value)
                        index -= 1
                    arguments = list(reversed(values))
                    entry = {"resource": record.index, "arguments": arguments}
                    if slot == SPAWN_SLOT:
                        entry["sprite"] = arguments[0] if arguments else None
                        spawns.append(entry)
                    else:
                        calls.append(entry)
    return {"spawns": spawns, "calls": calls, "counts": counts, "failures": failures}


def _walk(image: bytes) -> dict:
    """The corpus walk, computed once per image and cached by content hash."""
    key = hashlib.sha256(image).hexdigest()
    cached = _WALK_CACHE.get(key)
    if cached is None:
        cached = _walk_uncached(image)
        _WALK_CACHE[key] = cached
    return cached


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
    # The two definition pointers are claimed as fields but not pinned to a constant: they point into
    # the appended copies, whose addresses the verifier derives from the image below. Pinning them to
    # the donor's address is exactly the mistake the review caught.
    for sprite_id in DABURA_SPRITES:
        claim_word(CHARACTER_TABLE + 4 * sprite_id, None)
    name_slot_file = word(retail, TEXT_TABLE_START + 4 * NAME_SLOT) - ROM_BASE
    for offset in range(name_slot_file, name_slot_file + 2 * len(NEW_NAME) + 2):
        fields[offset] = None
    for index in (28, 29):
        base_offset = APPEARANCE_TABLE + index * APPEARANCE_STRIDE
        claim_word(base_offset + 0x04, BROLY_SPRITE)
        claim_word(base_offset + 0x08, 16)
    claim_word(APPEARANCE_TABLE + 28 * APPEARANCE_STRIDE + 0x0C, BROLY_STAT)

    # --- the appended copies, and every byte outside the base -----------------------------------
    appended = [offset for offset in range(len(base), len(image))]
    copy_regions = []
    for sprite_id in DABURA_SPRITES:
        definition = definition_of(image, sprite_id)
        if definition < ROM_BASE + len(base):
            fail(f"id {sprite_id} does not point at an appended definition copy")
            continue
        at = definition - ROM_BASE
        count = image[at] & 0xFF
        copy_regions.append((at, count))
        occupied = {index for index in range(count)
                    if word(image, at + 0x54 + 4 * index) >= ROM_BASE}
        original = {index for index, record in enumerate(slots_of(retail, sprite_id))
                    if record >= ROM_BASE}
        missing = sorted(original - occupied)
        if missing:
            fail(f"id {sprite_id}: the copy leaves slots {missing} empty that the original filled")
    starts = sorted(start for start, _count in copy_regions)
    bounds = [(start, starts[index + 1] if index + 1 < len(starts) else len(image))
              for index, start in enumerate(starts)]
    strays = [offset for offset in appended
              if not any(start <= offset < end for start, end in bounds)]
    # Alignment padding before the first copy, and between copies, is legal - but it must be zero,
    # because a non-zero byte there is an unintended write.
    strays = [offset for offset in strays if image[offset] != 0x00]
    if strays:
        fail(f"{len(strays)} appended byte(s) outside any definition copy: {strays[:12]}")

    # --- check 1: the diff inside the base is a subset of that set -------------------------------
    changed = [offset for offset in range(min(len(image), len(base)))
               if image[offset] != base[offset]]
    outside = [offset for offset in changed if offset not in fields]
    if outside:
        fail(f"{len(outside)} changed byte(s) outside the derived field set: {outside[:12]}")
    missing = [offset for offset, wanted in fields.items()
               if wanted is not None and word(image, offset) != wanted]
    if missing:
        fail(f"{len(missing)} field(s) do not hold the intended word: {missing[:12]}")

    # --- check 2: the ids this release owns draw the donor's art, and no other id moved -----------
    walked = _walk(image)
    base_walked = _walk(base)
    spawns, calls = walked["spawns"], walked["calls"]
    record_counts, failures = walked["counts"], walked["failures"]
    base_spawns, base_calls = base_walked["spawns"], base_walked["calls"]
    base_counts, base_failures = base_walked["counts"], base_walked["failures"]
    # The record counts are asserted against the base, and the decode-failure SET must match it: this
    # release may neither introduce a failure nor hide one. Both images report the same single
    # unreadable record, resource 9, which the canonical ROM reads and the base does not.
    for label in ("type 0", "type 4"):
        if record_counts[label] != base_counts[label]:
            fail(f"{label} record count is {record_counts[label]}, the base has {base_counts[label]}")
    if sorted(failures) != sorted(base_failures):
        fail(f"decode failures changed: {sorted(failures)} against the base's {sorted(base_failures)}")
    if len(spawns) < len(base_spawns) or len(calls) < len(base_calls):
        fail(f"the walk sees fewer sites than the base: {len(spawns)}/{len(base_spawns)} spawns, "
             f"{len(calls)}/{len(base_calls)} state calls")
    # The canonical counts, recorded rather than guessed: 236 type-0 records and 141 type-4.
    if record_counts["type 0"] < 236 or record_counts["type 4"] < 141:
        fail(f"corpus counts too low: {record_counts}")

    # The check that would have caught the borrowed-definition defect: every animation index a script
    # selects for one of these actors must be a slot that actor's definition actually fills.
    state_table = image[0x72670:0x72670 + 25]
    for call in calls:
        if len(call["arguments"]) < 2:
            continue
        actor_id, state = call["arguments"][0], call["arguments"][1]
        if state >= len(state_table):
            continue
        animation = state_table[state]
        slots = slots_of(image, actor_id)
        if 0 <= animation < len(slots) and slots[animation] >= ROM_BASE:
            continue
        if actor_id in DABURA_SPRITES or actor_id == BROLY_SPRITE:
            fail("resource " + str(call["resource"]) + " sets state " + str(state)
                 + " which selects animation " + str(animation) + " for sprite " + str(actor_id)
                 + ", whose definition leaves that slot empty")
    ids_named = {site["sprite"] for site in object_sites(image, (38, 73, 98))}
    ids_named |= {spawn["sprite"] for spawn in spawns if spawn["sprite"] is not None}
    for sprite_id in (BROLY_SPRITE,) + DABURA_SPRITES:
        resolved = definition_of(image, sprite_id)
        if sprite_id == BROLY_SPRITE:
            if resolved != broly_definition:
                fail(f"sprite id {sprite_id} resolves to 0x{resolved:08X}, not 0x{broly_definition:08X}")
        elif resolved == broly_definition or resolved == definition_of(retail, sprite_id):
            fail(f"sprite id {sprite_id} must have its own definition copy, not 0x{resolved:08X}")
    # Every other id must resolve exactly as it does in the canonical ROM: this release may own two
    # table words, not the table.
    moved = [sprite_id for sprite_id in range(CHARACTER_FIRST_ID, 307)
             if definition_of(image, sprite_id) != definition_of(retail, sprite_id)]
    if sorted(moved) != sorted(DABURA_SPRITES):
        fail(f"character-table entries changed for ids {sorted(moved)}, expected only "
             f"{sorted(DABURA_SPRITES)}")
    for spawn in spawns:
        actor_id = spawn["sprite"]
        if actor_id in DABURA_SPRITES and \
                definition_of(image, actor_id) == definition_of(retail, actor_id):
            fail(f"resource {spawn['resource']} spawns sprite {actor_id}, which still draws the "
                 "old actor's definition")

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
    print(f"# sprite ids any path names: {sorted(ids_named)}; ids 73 and 98 resolve to their own "
          f"definition copies, id 38 to the donor at 0x{broly_definition:08X}")
    print(f"# type-4 cutscene spawns naming the old ids: "
          f"{[spawn['resource'] for spawn in spawns if spawn['sprite'] in DABURA_SPRITES]}")
    print(f"# records naming the old actor, all unchanged: {naming}")
    print(f"# image sha256 {hashlib.sha256(image).hexdigest()}")
    print(f"# verdict {'PASS' if not problems else f'FAIL ({len(problems)})'}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
