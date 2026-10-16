"""Retune the Hercule and Olibu enemy stat records into real fights.

THE LEVER, MEASURED. Two static lanes and one runtime fight agree on what an enemy stat record
controls:

* `+0x04` (u24) is the enemy's maximum hit points. The constructor copies it to the actor's
  `+0x28C` shifted left ten, and the damage applier subtracts from there, so this is the length
  of the fight and nothing else.
* `+0x0D` (u8) and `+0x0E` (u8) are copied to the actor's `+0x1B0` and `+0x1B2`, and the damage
  calculator at `0x0800E9D8` consumes one of them as the attacker's attack term. Which one a
  given blow reads is chosen by the attack descriptor's first byte, so both are raised.
* `+0x0F` (u8) is copied to the actor's `+0x1B4` and `+0x1B6`, which the same calculator reads
  as the DEFENDER's defence. For an enemy that means the damage it takes, so this tool does not
  touch it: the hit points already set the fight's length.
* `+0x0C` (level) has no located reader and is left alone. `+0x00` (experience) is left at its
  retail value, because changing it would change progression rather than this fight.

CALIBRATION, MEASURED RATHER THAN GUESSED. On 2026-10-10 a normally levelled character fought
Olibu with the fight observer armed: 46 to 50 hit points per blow, thirteen blows to remove 565,
and 4 to 9 taken per blow in return. The new values keep the same blows-per-fight arithmetic:
Hercule 700 hit points is roughly fourteen blows, Olibu 1400 is roughly twenty-eight, and the
attack bytes are raised about nine- and twelve-fold, which the calculator's own quadratic term
turns into roughly that much more damage per blow.

REFUSALS. Every record must hold the measured baseline before it is written, so the tool cannot
land on a record that has already moved; only the three declared fields change; and the write is
staged and read back.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.friend_v3_text_approvals import APPROVED_BOSS_RETUNES  # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias      # noqa: E402

ENEMY_RECORD_SIZE = 0x1C
#: The three fields this tool writes, as (record offset, width in bytes).
FIELDS = ((0x04, 3, "hp"), (0x0D, 1, "strength"), (0x0E, 1, "power"))


class BossRetuneError(ValueError):
    """The retune refused rather than writing a record it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_field(image: bytes, offset: int, width: int) -> int:
    return int.from_bytes(image[offset:offset + width], "little")


def apply(image: bytes, retunes) -> tuple[bytes, list[dict]]:
    out = bytearray(image)
    report: list[dict] = []
    for retune in retunes:
        base = retune.file_offset
        if base + ENEMY_RECORD_SIZE > len(image):
            raise BossRetuneError(f"{retune.name}: record at file 0x{base:X} is past the image")
        got = {
            "hp": read_field(image, base + 0x04, 3),
            "strength": read_field(image, base + 0x0D, 1),
            "power": read_field(image, base + 0x0E, 1),
            "endurance": read_field(image, base + 0x0F, 1),
        }
        want = {
            "hp": retune.baseline_hp,
            "strength": retune.baseline_strength,
            "power": retune.baseline_power,
            "endurance": retune.baseline_endurance,
        }
        if got != want:
            raise BossRetuneError(
                f"{retune.name}: record at file 0x{base:X} holds {got}, not the measured "
                f"baseline {want}; refusing rather than correcting")
        changes = []
        for offset, width, field in FIELDS:
            before = read_field(image, base + offset, width)
            after = getattr(retune, field)
            if after <= 0 or (width < 3 and after > 0xFF):
                raise BossRetuneError(f"{retune.name}: {field} {after} does not fit its field")
            if width == 3 and after > 0xFFFFFF:
                raise BossRetuneError(f"{retune.name}: {field} {after} exceeds 24 bits")
            out[base + offset:base + offset + width] = after.to_bytes(width, "little")
            if before != after:
                changes.append({"field": field, "record_offset": base + offset,
                                "before": before, "after": after, "width": width})
        report.append({"selector": retune.selector, "name": retune.name,
                       "record_file_offset": base, "baseline": want,
                       "new": {"hp": retune.hp, "strength": retune.strength,
                               "power": retune.power,
                               "endurance": retune.baseline_endurance},
                       "changes": changes, "approval": retune.approval})
    return bytes(out), report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise BossRetuneError(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    output, report = apply(image, APPROVED_BOSS_RETUNES)
    for entry in report:
        print(f"  {entry['name']:<8} selector {entry['selector']:>3} at file "
              f"0x{entry['record_file_offset']:X}: "
              + ", ".join(f"{c['field']} {c['before']} -> {c['after']}" for c in entry["changes"]))
    document = {"input": str(source), "input_sha256": got, "input_bytes": len(image),
                "records": report, "output_bytes": len(output)}
    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise BossRetuneError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(output)
    if staged.read_bytes() != output:
        raise BossRetuneError("REFUSED: the staged write does not match the plan")
    staged.replace(target)
    # Read the finished image back before publishing the manifest.
    written = target.read_bytes()
    for retune in APPROVED_BOSS_RETUNES:
        base = retune.file_offset
        for offset, width, field in FIELDS:
            value = read_field(written, base + offset, width)
            if value != getattr(retune, field):
                raise BossRetuneError(
                    f"readback: {retune.name} {field} reads {value}, not "
                    f"{getattr(retune, field)}")
    document["output"] = str(target)
    document["output_sha256"] = sha256_bytes(written)
    Path(args.manifest).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"# wrote {target} {len(written)} bytes sha256 {document['output_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
