"""SPRITE-NEW-BEHAVIOR-REGISTRATION-001: emit the one-word registration variant.

The ticket's question is what puts an entry into the behaviour dispatch table at
``actor + 0x1B0`` and why the authored Cui actor does not receive the entry a
comparable retail actor does.  The static answer is that the table is not built at
runtime at all: the actor constructor stores a pointer to a ``{count, ptr[count]}``
array that lives INSIDE the source record, and for the map-102 record family that
array is ``record + 0x14`` -- ``+0x14`` the count, ``+0x18`` the first entry -- so
the dispatched entry is ``*(record + 0x18)``.

This script emits two images from the SAME identity material:

* ``before`` - SPRITE-NEW-RUNTIME-001's image, reproduced byte for byte through
  ``sprite_new_runtime.build_experiment(target="new-actor")``.  Its new record at
  ``0x08801F38`` was cloned from the retail donor record ``0x08078440`` and
  therefore carries the donor's ``+0x18`` unchanged.
* ``after`` - that image with exactly ONE word changed: the new record's ``+0x18``
  is repointed at the record's own behaviour template at ``+0x1C``.

The template at the new record's ``+0x1C`` is a byte-for-byte copy of the template
at ``0x0807845C``, which is the entry the comparable retail record ``0x08078440``'s
successor (``0x0807846C``, also sprite 69) dispatches.  The script asserts that
equality rather than assuming it.

Canonical bytes are never touched and the canonical image is only read.

    python tools/research/sprite_new_behavior_registration.py \
        --rom <canonical> --sheet <Cui sheet png> \
        --before <gba> --after <gba> --manifest <json>
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

#: SPRITE-NEW-RUNTIME-001's recorded build digest, reproduced rather than trusted.
RUNTIME_BUILD_SHA256 = (
    "29f9195a2f7ed9ebb7cf72188dad2d52fec1b5cd1dc7d819432fa2954f946529"
)

#: The new record the runtime ticket authored above canonical EOF.
NEW_RECORD_ROM = 0x08801F38
RECORD_SPRITE_FIELD = 0x10
RECORD_COUNT_FIELD = 0x14
RECORD_ENTRY_FIELD = 0x18
RECORD_BODY_FIELD = 0x1C
RECORD_TOTAL_SIZE = 0x2C

#: The retail template the comparable running record dispatches: retail record 8
#: is at 0x0807846C and its +0x18 is 0x0807845C.
COMPARABLE_RECORD_ROM = 0x0807846C
COMPARABLE_ENTRY_ROM = 0x0807845C


class RegistrationError(ValueError):
    """An input or an image this experiment cannot honour."""


def u32(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address - ROM_BASE)[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rom", required=True, help="the canonical image")
    parser.add_argument("--sheet", required=True, help="the Cui sheet PNG")
    parser.add_argument("--cell", type=int, default=0)
    parser.add_argument("--before", required=True, help="write the baseline image")
    parser.add_argument("--after", required=True, help="write the variant image")
    parser.add_argument("--manifest", required=True)
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
    before = experiment.output(canonical)

    before_sha = hashlib.sha256(before).hexdigest()
    if before_sha != RUNTIME_BUILD_SHA256:
        raise RegistrationError(
            f"the reproduced baseline is {before_sha}, not the recorded runtime "
            f"build {RUNTIME_BUILD_SHA256}")

    sprite_id = u32(before, NEW_RECORD_ROM + RECORD_SPRITE_FIELD)
    if sprite_id != snr.NEW_SPRITE_ID:
        raise RegistrationError(
            f"the new record names sprite {sprite_id}, not {snr.NEW_SPRITE_ID}")
    count = u32(before, NEW_RECORD_ROM + RECORD_COUNT_FIELD)
    entry = u32(before, NEW_RECORD_ROM + RECORD_ENTRY_FIELD)
    body = u32(before, NEW_RECORD_ROM + RECORD_BODY_FIELD)
    body_address = NEW_RECORD_ROM + RECORD_BODY_FIELD

    own_template = before[body_address - ROM_BASE:
                          body_address - ROM_BASE + 0x10]
    retail_template = canonical[COMPARABLE_ENTRY_ROM - ROM_BASE:
                                COMPARABLE_ENTRY_ROM - ROM_BASE + 0x10]
    template_identical = own_template == retail_template
    if not template_identical:
        raise RegistrationError(
            "the new record's own template is not the retail template this "
            "comparison depends on")

    after = bytearray(before)
    struct.pack_into("<I", after, NEW_RECORD_ROM + RECORD_ENTRY_FIELD - ROM_BASE,
                     body_address)
    after_bytes = bytes(after)

    differences = [i for i in range(len(before)) if before[i] != after_bytes[i]]
    changed_words = {i // 4 for i in differences}
    if changed_words != {(NEW_RECORD_ROM - ROM_BASE + RECORD_ENTRY_FIELD) // 4}:
        raise RegistrationError(
            "the variant is not the single aligned word this experiment is "
            f"defined by (changed bytes {[hex(i) for i in differences]})")
    if differences[0] < len(canonical):
        raise RegistrationError(
            "the variant touches a canonical byte, which this experiment forbids")

    Path(args.before).write_bytes(before)
    Path(args.after).write_bytes(after_bytes)

    report = {
        "ticket": "SPRITE-NEW-BEHAVIOR-REGISTRATION-001",
        "canonical_sha256": CANONICAL_SHA256,
        "sheet": Path(args.sheet).name,
        "cell": args.cell,
        "before_sha256": before_sha,
        "before_size": len(before),
        "after_sha256": hashlib.sha256(after_bytes).hexdigest(),
        "after_size": len(after_bytes),
        "new_record_rom": f"0x{NEW_RECORD_ROM:08X}",
        "record_fields_before": {
            "sprite_id": sprite_id,
            "count_at_plus_0x14": f"0x{count:08X}",
            "entry_at_plus_0x18": f"0x{entry:08X}",
            "body_at_plus_0x1C": f"0x{body:08X}",
        },
        "record_fields_after": {
            "count_at_plus_0x14": f"0x{count:08X}",
            "entry_at_plus_0x18": f"0x{body_address:08X}",
        },
        "changed_byte_offsets": [f"0x{i:08X}" for i in differences],
        "canonical_bytes_changed": 0,
        "own_template_equals_retail_template": template_identical,
        "comparable_retail_record_rom": f"0x{COMPARABLE_RECORD_ROM:08X}",
        "comparable_retail_entry_rom": f"0x{COMPARABLE_ENTRY_ROM:08X}",
        "base_identity_report": experiment.report,
    }
    Path(args.manifest).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k != "base_identity_report"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
