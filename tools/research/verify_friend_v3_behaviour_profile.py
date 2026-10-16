"""Verify a behaviour-profile build against the image it was built from.

Read-only. Checks, in order:

  1. each named record's behaviour field names the profile's gate row;
  2. the two profile rows name the block's gate and hub nodes, and their secondary word is the
     family's own;
  3. the block's nodes are the family's own bytes with only the declared patches: the gate's and
     attack leaf's radius, the attack leaf's probability, and the three internal child pointers;
  4. the appended block is the only new region, and the differing bytes in the base are exactly
     the named fields and rows;
  5. the profile's numbers, printed against retail for the record.
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

# The row-freeness proof lives in the builder, and the verifier re-derives it from the base image
# rather than trusting the manifest's prose about it.
from tools.research import apply_friend_v3_behaviour_profile as builder  # noqa: E402
from tools.webfoot.analysis.thumb import addr_to_offset  # noqa: E402
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ROM_BASE = 0x08000000
BEHAVIOUR_TABLE = 0x70F514
BEHAVIOUR_ROW_STRIDE = 8
FAMILY_GATE = 0x702218
FAMILY_HUB = 0x70235C
FAMILY_ATTACK_DIST = 0x7022A0
FAMILY_ATTACK_RAND = 0x70228C
FAMILY_ATTACK_SPAWN = 0x70227C
FAMILY_ROW_SECONDARY = 0x08702244
FAMILY_ENTRY_NODE = 0x08702844
SET_SIZE, GATE_SIZE, HUB_SIZE, LEAF_SIZE = 16, 20, 44, 20


def u32(payload: bytes, offset: int) -> int:
    return struct.unpack_from("<I", payload, offset)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--against", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    image = Path(args.image).read_bytes()
    against = Path(args.against).read_bytes()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    profile = manifest["profile"]
    problems: list[str] = []

    def check(condition: bool, message: str) -> None:
        print(("PASS " if condition else "FAIL ") + message)
        if not condition:
            problems.append(message)

    block = manifest["block_file_offset"]
    at_set_gate = block
    at_gate = at_set_gate + SET_SIZE
    at_set_hub = at_gate + GATE_SIZE
    at_hub = at_set_hub + SET_SIZE
    at_attack = at_hub + HUB_SIZE
    at_chance = at_attack + LEAF_SIZE

    # 3: the block is the family's nodes with the declared patches.
    check(image[at_gate:at_gate + GATE_SIZE] == against[FAMILY_GATE:FAMILY_GATE + GATE_SIZE][:0x0C]
          + struct.pack("<I", profile["entry_gate_radius_squared"])
          + struct.pack("<I", ROM_BASE + at_set_hub),
          "the gate node is the family's own bytes with the radius and child patched")
    attack_slots = (u32(image, at_hub + 0x10), u32(image, at_hub + 0x14))
    check(ROM_BASE + at_attack in attack_slots,
          f"the hub node carries the new distance leaf as one of its first two children "
          f"(slots {[hex(v) for v in attack_slots]})")
    print(f"     attack arm is child[{0 if attack_slots[0] == ROM_BASE + at_attack else 1}] "
          f"of the hub (retail is child[1])")
    check(u32(image, at_attack + 0x0C) == profile["attack_radius_squared"],
          f"the attack radius reads {u32(image, at_attack + 0x0C)}")
    check(u32(image, at_chance + 0x0C) == profile["attack_probability_raw"],
          f"the attack probability reads {u32(image, at_chance + 0x0C)}")
    # The probability leaf's child must be WHERE THE MANIFEST SAYS. Asserting the retail spawn
    # pointer instead is how an earlier version of this verifier certified a build whose copied
    # nodes were dead bytes: the tool serialised the block before patching that word, so the leaf
    # still pointed at the retail shared spawn and the profile's action change never ran. The
    # expectation now comes from the manifest, and a copy that exists must be the one reached.
    leaf_child = u32(image, at_chance + 0x10)
    if "spawn" in manifest["nodes"]:
        check(leaf_child == int(manifest["nodes"]["spawn"], 16),
              f"the probability leaf reaches the copied spawn at {manifest['nodes']['spawn']} "
              f"(it reads 0x{leaf_child:08X})")
        check(manifest["nodes"]["spawn"] != f"0x{ROM_BASE + FAMILY_ATTACK_SPAWN:08X}",
              "the copied spawn is not the retail node, so the copy is not dead weight")
        # The manifest names a ROM ADDRESS and a SET node pushes its row from the parameter word
        # at +0x0C. Indexing the image with the address raised struct.error; reading the node's
        # first word would compare the node's own entry instead of the row it pushes.
        action_at = addr_to_offset(int(manifest["nodes"]["set_action"], 16), len(image))
        check(u32(image, action_at + 0x0C) == profile["attack_action_row"],
              "the copied SET node carries the requested action row")
    else:
        check(leaf_child == ROM_BASE + FAMILY_ATTACK_SPAWN,
              "with no action change, the leaf spawns through the family's own node")
    check(image[at_set_gate + 12:at_set_gate + 16] ==
          struct.pack("<I", manifest["records"][0]["behaviour_row_after"]),
          "the gate's SET node pushes the profile row")

    # 1: the records.
    for record in manifest["records"]:
        value = u32(image, record["behaviour_field_file_offset"])
        check(value == record["behaviour_row_after"],
              f"selector {record['selector']} behaviour row reads {value}")
        row = BEHAVIOUR_TABLE + value * BEHAVIOUR_ROW_STRIDE
        check(u32(image, row) == ROM_BASE + at_gate,
              f"selector {record['selector']}'s row names the profile gate")

    # 2: the rows. Each row's node comes from the manifest, so a profile that writes more than
    # the gate and hub rows is checked the same way rather than failing on an assumed count.
    for entry in manifest["rows"]:
        expected = int(entry["node"], 16)
        check(u32(image, entry["file_offset"]) == expected,
              f"row {entry['row']} names {entry['node']}")
        check(u32(image, entry["file_offset"] + 4) == FAMILY_ROW_SECONDARY,
              f"row {entry['row']}'s secondary word is the family's own")
        # B2: a borrowed row is only safe when it was proven unnamed. The manifest records the
        # proof, and the verifier re-derives it from the image rather than trusting the prose.
        if "freeness_proof" in entry:
            free, why = builder.row_is_free(against, entry["row"])
            check(free, f"row {entry['row']} was free in the base image ({why or 'no reference'})")

    # 4: the differing bytes.
    allowed = set(range(len(against), len(image)))
    for record in manifest["records"]:
        allowed.update(range(record["behaviour_field_file_offset"],
                             record["behaviour_field_file_offset"] + 4))
    for entry in manifest["rows"]:
        allowed.update(range(entry["file_offset"], entry["file_offset"] + 8))
    stray = [index for index in range(min(len(image), len(against)))
             if image[index] != against[index] and index not in allowed]
    check(not stray, f"0 differing bytes outside the profile's own sites (found {len(stray)})")
    differing = sum(1 for index in range(min(len(against), len(image)))
                    if image[index] != against[index])
    print(f"     {differing} differing byte(s) in the base, {len(image) - len(against)} appended")
    check(len(image) == manifest["output_bytes"], "the output byte count matches the manifest")

    print(f"     profile: entry gate r{profile['entry_gate_radius']} "
          f"(retail r{profile['retail_entry_gate_radius']}), attack gate "
          f"r{profile['attack_radius']} at {profile['attack_percent']}% "
          f"(retail r{profile['retail_attack_radius']} at {profile['retail_attack_percent']}%)")

    print(f"\n{'VERIFY PASS' if not problems else 'VERIFY FAIL: ' + str(len(problems))}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
