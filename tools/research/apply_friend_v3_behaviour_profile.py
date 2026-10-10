"""Give chosen enemies a NEW behaviour profile, as pure data, without touching any shared node.

WHY NOT EDIT THE EXISTING HUB. Olibu's and Hercule's behaviour resolves into one family hub that
twelve enemy selectors share (30, 35, 37, 40, 45, 49, 85, 90, 130, 132, 135, 148). Editing the
hub's parameters in place would change all twelve, which is a global rebalance. Instead this tool
writes a small, self-contained copy of the family's own nodes into the one clean extent of the
image and points ONLY the named records' behaviour rows at it.

WHAT THE PROFILE CHANGES, and why those numbers. The family's own tree is kept node for node; the
copy differs in exactly two things:

* the entry gate, `dist(actor, player) <= r`, which decides whether the enemy is in the fight at
  all. Retail is 10000 (r100).
* the attack arm: retail fires when `dist <= r50` and then only on 12 percent of evaluations
  (7864 of 65536). The copy raises the radius and the chance.

Everything else - the AUX delegation, the two distance-gated transitions, the shared completion
sequence, the spawn payload - is reused by pointer, so this is the family's own behaviour with a
different appetite, not a new AI.

WHERE THE BYTES GO. The block is APPENDED at the end of the image, 4-byte aligned, and the new
rows point at it with absolute addresses. Appending is the route this project already ships for
the split container: the emulator serves the whole file, and the appended region is read. The
in-image clean tail is NOT used: measured, 480 of its last 512 bytes hold real data in this image
and two word-aligned pointers name addresses inside it, so it is not free.

The consequence is stated rather than implied: the appended block sits past the header's declared
8 MiB cart size, exactly like the containers release 2 and 2.1 added. That reads because mGBA
serves the whole file; it is an emulator behaviour, not a hardware claim.

REFUSALS. Each named record's behaviour row must hold the family's own entry node before it is
repointed, and the staged image is read back.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

ROM_BASE = 0x08000000
RECORD_TABLE = 0x711274
RECORD_STRIDE = 0x1C
BEHAVIOUR_FIELD = 0x08
BEHAVIOUR_TABLE = 0x70F514
BEHAVIOUR_ROW_STRIDE = 8

#: The family's own nodes, copied verbatim and patched.
FAMILY_GATE = 0x702218          # DIST-inside r100 -> SET 204
FAMILY_HUB = 0x70235C           # OR of 7, child[1] is the attack arm
FAMILY_ATTACK_DIST = 0x7022A0   # DIST-inside r50 -> RAND
FAMILY_ATTACK_RAND = 0x70228C   # RAND 12% -> SPAWN
FAMILY_ATTACK_SPAWN = 0x70227C  # SPAWN -> SET 206, reused by pointer
#: The action row the swing's own SET pushes. Retuning the swing's cadence means changing this
#: row: the chance leaf and the post-attack wait were both measured and neither moves the rate.
FAMILY_ATTACK_ACTION_ROW = 206
FAMILY_ROW_SECONDARY = 0x08702244   # AUX 210, the family's own secondary node
FAMILY_ENTRY_NODE = 0x08702844      # SET 203, the node the subject rows hold

#: The profile's block, in the clean tail, and the sizes of the nodes it holds.
BLOCK = 0x7FFE00
BLOCK_END = 0x800000
SET_SIZE = 16
GATE_SIZE = 20
HUB_SIZE = 44
LEAF_SIZE = 20

SET_ENTRY = 0x0801890B
SET_UPDATE = 0x08018921
SET_EXIT = 0x08018937


class ProfileError(ValueError):
    """The profile refused rather than writing bytes it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def u32(payload: bytes, offset: int) -> int:
    return struct.unpack_from("<I", payload, offset)[0]


def set_node(row: int) -> bytes:
    """A SET node: 16 bytes carrying the behaviour row it pushes."""
    return struct.pack("<IIII", SET_ENTRY, SET_UPDATE, SET_EXIT, row)


def family_row(image: bytes, selector: int) -> int:
    """The behaviour row a record resolves, refusing a record that is not this family.

    Refusing matters: the profile repoints a record's behaviour row at a copied tree, so running
    it twice would repoint a row at a block the family no longer holds, and running it on another
    enemy would hand that enemy this family's combat tree.
    """
    behaviour_row = u32(image, RECORD_TABLE + selector * RECORD_STRIDE + BEHAVIOUR_FIELD)
    entry = u32(image, BEHAVIOUR_TABLE + behaviour_row * BEHAVIOUR_ROW_STRIDE)
    if entry != FAMILY_ENTRY_NODE:
        raise ProfileError(
            f"REFUSED: selector {selector} resolves row {behaviour_row} whose entry is "
            f"0x{entry:08X}, not the family entry 0x{FAMILY_ENTRY_NODE:08X}; this is not the "
            "family this profile was measured against")
    return behaviour_row


def build_block(image: bytes, block: int, gate_radius: int, attack_radius: int,
                probability: int, row_gate: int, row_hub: int,
                attack_first: bool = False,
                attack_action: int | None = None) -> tuple[bytes, dict]:
    """The node block, laid out as set_gate, gate, set_hub, hub, attack_dist, attack_rand."""
    at_set_gate = block
    at_gate = at_set_gate + SET_SIZE
    at_set_hub = at_gate + GATE_SIZE
    at_hub = at_set_hub + SET_SIZE
    at_attack = at_hub + HUB_SIZE
    at_chance = at_attack + LEAF_SIZE
    end = at_chance + LEAF_SIZE

    gate = bytearray(image[FAMILY_GATE:FAMILY_GATE + GATE_SIZE])
    struct.pack_into("<I", gate, 0x0C, gate_radius)
    struct.pack_into("<I", gate, 0x10, ROM_BASE + at_set_hub)

    hub = bytearray(image[FAMILY_HUB:FAMILY_HUB + HUB_SIZE])
    struct.pack_into("<I", hub, 0x14, ROM_BASE + at_attack)
    if attack_first:
        # The hub is an OR: the FIRST child whose condition is true wins. Retail puts the AUX
        # delegation at child[0] and the attack arm at child[1], so a passive branch can take
        # the decision before the attack is ever considered. Moving the attack arm to the front
        # is the difference between raising the attack's own numbers and letting it be reached.
        first = bytes(hub[0x10:0x14])
        hub[0x10:0x14] = hub[0x14:0x18]
        hub[0x14:0x18] = first

    attack = bytearray(image[FAMILY_ATTACK_DIST:FAMILY_ATTACK_DIST + LEAF_SIZE])
    struct.pack_into("<I", attack, 0x0C, attack_radius)
    struct.pack_into("<I", attack, 0x10, ROM_BASE + at_chance)

    chance = bytearray(image[FAMILY_ATTACK_RAND:FAMILY_ATTACK_RAND + LEAF_SIZE])
    struct.pack_into("<I", chance, 0x0C, probability)

    block_bytes = bytearray(set_node(row_gate) + bytes(gate) + set_node(row_hub) + bytes(hub)
                            + bytes(attack) + bytes(chance))
    offsets = {"set_gate": at_set_gate, "gate": at_gate, "set_hub": at_set_hub,
               "hub": at_hub, "attack_dist": at_attack, "attack_rand": at_chance}

    if attack_action is None:
        # Retail swing chain: the arm spawns through the family's own leaf and its own row.
        struct.pack_into("<I", chance, 0x10, ROM_BASE + FAMILY_ATTACK_SPAWN)
    else:
        # A copy of the swing's chain with a different action row, so the change stays per-enemy.
        # The swing's own row decides which animation the attack plays, and the animation is what
        # bounds the swing rate: neither the chance leaf nor the post-attack wait moved it.
        at_spawn = at_chance + LEAF_SIZE
        at_action = at_spawn + 16
        spawn = bytearray(image[FAMILY_ATTACK_SPAWN:FAMILY_ATTACK_SPAWN + 16])
        struct.pack_into("<I", spawn, 0x0C, ROM_BASE + at_action)
        struct.pack_into("<I", chance, 0x10, ROM_BASE + at_spawn)
        block_bytes += bytes(spawn) + set_node(attack_action)
        offsets.update({"spawn": at_spawn, "set_action": at_action})

    offsets["block_end"] = block + len(block_bytes)
    return bytes(block_bytes), offsets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--gate-radius", type=int, required=True,
                        help="squared radius at which the enemy enters the fight")
    parser.add_argument("--attack-radius", type=int, required=True,
                        help="squared radius at which the attack arm may fire")
    parser.add_argument("--attack-percent", type=float, required=True,
                        help="chance per evaluation of the attack arm firing, 0 to 100")
    parser.add_argument("--row-gate", type=int, default=799)
    parser.add_argument("--row-hub", type=int, default=90)
    parser.add_argument("--attack-first", action="store_true",
                        help="move the attack arm to child[0] of the hub, so the OR reaches it "
                             "before the passive branches")
    parser.add_argument("--attack-action", type=int, default=None,
                        help="point the swing at a different action row of the same family, which "
                             "is the only data lever into the swing animation itself")
    parser.add_argument("--record", type=int, action="append", required=True,
                        help="enemy stat selector whose behaviour row is repointed")
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise ProfileError(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    if not 0 < args.attack_percent <= 100:
        raise ProfileError("attack percent must be inside (0, 100]")
    # The leaf is true when a 16-bit random is BELOW the parameter, so the highest encodable
    # chance is 65535 of 65536 rather than 65536; 100 percent is written as that ceiling and the
    # manifest records the difference.
    probability = min(65535, int(args.attack_percent / 100 * 65536))
    if not 0 < probability <= 65535:
        raise ProfileError(f"attack percent {args.attack_percent} is not encodable")

    block = len(image)
    while block % 4:
        block += 1
    block_bytes, offsets = build_block(image, block, args.gate_radius, args.attack_radius,
                                       probability, args.row_gate, args.row_hub,
                                       attack_first=args.attack_first,
                                       attack_action=args.attack_action)
    out = bytearray(image)
    while len(out) < block:
        out.append(0x00)
    out += block_bytes

    rows = []
    for row, name in ((args.row_gate, "gate"), (args.row_hub, "hub")):
        at = BEHAVIOUR_TABLE + row * BEHAVIOUR_ROW_STRIDE
        before = bytes(image[at:at + 8])
        node = ROM_BASE + offsets[name]
        out[at:at + 4] = node.to_bytes(4, "little")
        out[at + 4:at + 8] = FAMILY_ROW_SECONDARY.to_bytes(4, "little")
        rows.append({"row": row, "file_offset": at, "before": before.hex(),
                     "after": bytes(out[at:at + 8]).hex(), "node": f"0x{node:08X}"})

    records = []
    for selector in args.record:
        base = RECORD_TABLE + selector * RECORD_STRIDE
        field = base + BEHAVIOUR_FIELD
        before = bytes(image[field:field + 4])
        behaviour_row = family_row(image, selector)
        out[field:field + 4] = args.row_gate.to_bytes(4, "little")
        records.append({"selector": selector, "record_file_offset": base,
                        "behaviour_field_file_offset": field,
                        "behaviour_row_before": behaviour_row,
                        "behaviour_row_after": args.row_gate,
                        "before": before.hex(), "after": bytes(out[field:field + 4]).hex()})

    document = {
        "input": str(source), "input_sha256": got, "input_bytes": len(image),
        "profile": {
            "entry_gate_radius_squared": args.gate_radius,
            "entry_gate_radius": round(args.gate_radius ** 0.5, 1),
            "attack_radius_squared": args.attack_radius,
            "attack_radius": round(args.attack_radius ** 0.5, 1),
            "attack_percent": args.attack_percent,
            "attack_probability_raw": probability,
            "retail_entry_gate_radius": 100,
            "retail_attack_radius": 50,
            "retail_attack_percent": 12.0,
            "attack_arm_first": bool(args.attack_first),
            "attack_action_row": args.attack_action,
            "retail_attack_action_row": FAMILY_ATTACK_ACTION_ROW,
        },
        "block_file_offset": block,
        "block_pointer": f"0x{ROM_BASE + block:08X}",
        "block_payload_bytes": len(block_bytes),
        "nodes": {name: f"0x{ROM_BASE + at:08X}" for name, at in offsets.items()
                  if name != "block_end"},
        "rows": rows,
        "records": records,
        "reused_shared_nodes": {
            "attack_spawn": f"0x{ROM_BASE + FAMILY_ATTACK_SPAWN:08X}",
            "hub_children": "the family hub's own child pointers, unchanged except the attack arm",
        },
        "residual_risk": "the write extent is the last 512 bytes of the image; no word-aligned "
                         "pointer in the image addresses it, and a computed reference would not "
                         "be seen by that scan. The runtime attack count settles it.",
        "output_bytes": len(out),
    }

    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise ProfileError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(out)
    if staged.read_bytes() != out:
        raise ProfileError("REFUSED: the staged write does not match the plan")
    staged.replace(target)

    written = target.read_bytes()
    for record in records:
        if u32(written, record["behaviour_field_file_offset"]) != args.row_gate:
            raise ProfileError(f"readback: selector {record['selector']} did not take the row")
    for row in rows:
        if u32(written, row["file_offset"]) != int(row["node"], 16):
            raise ProfileError(f"readback: row {row['row']} does not name {row['node']}")
    document["output"] = str(target)
    document["output_sha256"] = sha256_bytes(written)
    Path(args.manifest).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    for record in records:
        print(f"  selector {record['selector']:>3}: behaviour row "
              f"{record['behaviour_row_before']} -> {record['behaviour_row_after']}")
    for row in rows:
        print(f"  row {row['row']:>3} at file 0x{row['file_offset']:X}: {row['before']} -> "
              f"{row['after']} (node {row['node']})")
    print(f"# profile: entry gate r{document['profile']['entry_gate_radius']}, attack gate "
          f"r{document['profile']['attack_radius']} at {args.attack_percent}% (retail r50 at 12%)")
    print(f"# wrote {target} {len(written)} bytes sha256 {document['output_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
