"""Verify a boss retune against the image it was built from.

Read-only. Checks, in order:

  1. each retuned record holds exactly the approved values in the three declared fields;
  2. every other byte of the enemy stat extent is byte-identical to the base, so no other
     encounter moved;
  3. the whole image differs from the base only inside those six declared fields;
  4. the derived fight arithmetic, printed for the record: blows to remove the new hit points
     at the measured per-blow damage, and the branch each attack byte feeds.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.friend_v3_text_approvals import APPROVED_BOSS_RETUNES  # noqa: E402

ENEMY_TABLE = 0x711274
ENEMY_STRIDE = 0x1C
ENEMY_COUNT = 141
FIELDS = ((0x04, 3, "hp"), (0x0D, 1, "strength"), (0x0E, 1, "power"))
#: The measured per-blow damage of a normally levelled character (Olibu fight, 2026-10-10).
MEASURED_BLOW = 48


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--against", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    image = Path(args.image).read_bytes()
    against = Path(args.against).read_bytes()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    problems: list[str] = []

    def check(condition: bool, message: str) -> None:
        print(("PASS " if condition else "FAIL ") + message)
        if not condition:
            problems.append(message)

    for retune in APPROVED_BOSS_RETUNES:
        base = retune.file_offset
        for offset, width, field in FIELDS:
            value = int.from_bytes(image[base + offset:base + offset + width], "little")
            check(value == getattr(retune, field),
                  f"{retune.name} {field} reads {value}, expected {getattr(retune, field)}")
        endurance = image[base + 0x0F]
        check(endurance == retune.baseline_endurance,
              f"{retune.name} endurance untouched at {endurance}")
        level = image[base + 0x0C]
        check(level == against[base + 0x0C], f"{retune.name} level untouched at {level}")
        exp = int.from_bytes(image[base + 0x00:base + 0x03], "little")
        check(exp == int.from_bytes(against[base:base + 3], "little"),
              f"{retune.name} experience untouched at {exp}")
        blows = retune.hp / MEASURED_BLOW
        print(f"     {retune.name}: {retune.hp} hit points is about {blows:.0f} blows at the "
              f"measured {MEASURED_BLOW} per blow; strength {retune.strength} feeds branch A's "
              f"attacker term, power {retune.power} feeds branch B's")

    # 2: the rest of the enemy table is untouched.
    changed_records = {retune.selector for retune in APPROVED_BOSS_RETUNES}
    drifted = []
    for index in range(ENEMY_COUNT):
        if index in changed_records:
            continue
        base = ENEMY_TABLE + index * ENEMY_STRIDE
        if image[base:base + ENEMY_STRIDE] != against[base:base + ENEMY_STRIDE]:
            drifted.append(index)
    check(not drifted, f"the other {ENEMY_COUNT - len(changed_records)} enemy records are "
                       f"byte-identical to the base (drifted: {drifted[:8]})")

    # 3: the whole image differs only inside the declared fields.
    allowed = set()
    for retune in APPROVED_BOSS_RETUNES:
        for offset, width, _field in FIELDS:
            allowed.update(range(retune.file_offset + offset,
                                 retune.file_offset + offset + width))
    stray = [index for index in range(min(len(image), len(against)))
             if image[index] != against[index] and index not in allowed]
    check(not stray, f"0 differing bytes outside the declared fields (found {len(stray)})")
    if stray:
        print(f"     first stray offsets: {[hex(o) for o in stray[:8]]}")
    differing = sum(1 for index in range(min(len(image), len(against)))
                    if image[index] != against[index])
    print(f"     {differing} differing byte(s) in the base; declared fields total "
          f"{sum(width for _o, width, _f in FIELDS) * len(APPROVED_BOSS_RETUNES)} bytes")
    check(len(image) == manifest["output_bytes"], "the output byte count matches the manifest")

    print(f"\n{'VERIFY PASS' if not problems else 'VERIFY FAIL: ' + str(len(problems))}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
