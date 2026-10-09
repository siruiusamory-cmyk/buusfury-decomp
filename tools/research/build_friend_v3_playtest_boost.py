"""Build the FRIEND-V3 playtest-boost image from a verified friend foundation.

One image in, one image out. Every change is declared as (offset, expected old
bytes, new bytes); the builder re-reads the foundation and refuses if any
expected byte differs, so it can never patch an image it was not verified
against. The output's changed-byte set must equal the union of the declared
spans exactly: a change the manifest does not name is a refusal, not a warning.

Read-only with respect to its input. The canonical ROM is never an input here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Character base-stat table, Buu's Fury. Layout verified in
# tools/webfoot/formats/stat_tables.py:decode_base_stat_record.
BASE_STAT_TABLE = 0x006FDA4C
BASE_STAT_RECORD_SIZE = 0x12
BASE_STAT_COUNT = 9

# The five base party records. Fusion records (Gotenks, Vegito, Gogeta) derive
# from them and Hercule is not part of the five-character party.
PARTY_RECORDS = (0, 1, 2, 3, 4)
ROSTER_NAMES = ("Goku", "Gohan", "Goten", "Trunks", "Vegeta")

# u8 level, u16 hp, u16 ep, u8 strength, u8 power, u8 endurance, u8 speed.
FIELD_OFFSETS = {
    "level": (0x00, 1, 200),
    "hp": (0x02, 2, 0xFFFF),
    "ep": (0x04, 2, 0xFFFF),
    "strength": (0x06, 1, 0xFF),
    "power": (0x07, 1, 0xFF),
    "endurance": (0x08, 1, 0xFF),
    "speed": (0x09, 1, 0xFF),
}

# Every field is set to the widest value its own encoder accepts. The level
# ceiling of 200 is the game's own: `cmp r6,#0xc8` at 0x08013A00 on the grant
# path (tools/webfoot/stats.py:71-75).
MAXIMUM = {name: ceiling for name, (_, _, ceiling) in FIELD_OFFSETS.items()}


class BoostError(ValueError):
    """A refusal. Nothing is written when this is raised."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def plan(base: bytes) -> tuple[bytes, list[dict]]:
    """Return the boosted image bytes and the manifest of changes."""
    need = BASE_STAT_TABLE + BASE_STAT_COUNT * BASE_STAT_RECORD_SIZE
    if len(base) < need:
        raise BoostError("image is smaller than the character base-stat table")

    out = bytearray(base)
    changes: list[dict] = []
    for name, index in zip(ROSTER_NAMES, PARTY_RECORDS):
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        fields = []
        for field, (rel, width, ceiling) in FIELD_OFFSETS.items():
            offset = record + rel
            was = int.from_bytes(base[offset:offset + width], "little")
            now = MAXIMUM[field]
            if now > ceiling:
                raise BoostError(f"{field}={now} exceeds its {ceiling} ceiling")
            if was != now:
                out[offset:offset + width] = now.to_bytes(width, "little")
            fields.append({"field": field, "offset": offset, "was": was, "now": now})
        changes.append({"record": index, "name": name, "fields": fields})

    boosted = bytes(out)
    _assert_only_declared_bytes_changed(base, boosted, changes)
    return boosted, changes


def _assert_only_declared_bytes_changed(base: bytes, boosted: bytes, changes: list[dict]) -> None:
    declared: set[int] = set()
    for entry in changes:
        for field in entry["fields"]:
            _, width, _ = FIELD_OFFSETS[field["field"]]
            if field["was"] != field["now"]:
                declared.update(range(field["offset"], field["offset"] + width))
    actual = {i for i, (a, b) in enumerate(zip(base, boosted)) if a != b}
    undeclared = actual - declared
    if undeclared:
        raise BoostError(f"{len(undeclared)} byte(s) changed outside the declared spans")
    missed = declared - actual
    if missed:
        raise BoostError(f"{len(missed)} declared byte(s) did not change")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args(argv)

    base = args.image.read_bytes()
    got = sha256_bytes(base)
    if got != args.expect_sha256.lower():
        raise BoostError(f"input digest {got} is not the expected {args.expect_sha256.lower()}")
    if args.out.exists() and args.out.samefile(args.image):
        raise BoostError("output is the input; a boost is never written over its own base")

    boosted, changes = plan(base)
    args.out.write_bytes(boosted)
    report = {
        "input": {"path": str(args.image), "sha256": got, "bytes": len(base)},
        "output": {"path": str(args.out), "sha256": sha256_bytes(boosted), "bytes": len(boosted)},
        "changed_bytes": sum(1 for a, b in zip(base, boosted) if a != b),
        "records": changes,
    }
    if args.manifest:
        args.manifest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['output']['sha256']}  {len(boosted)}  {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
