"""Verify a World Tournament split release against the image it was built from.

Read-only. Checks, in order, and fails loudly rather than reporting a soft pass:

  1. every placed record resolves through the ENGINE's own route - the table the literal
     names, indexed by the handle's selector - and reads the approved wording back exactly;
  2. the control prefix the record carried is preserved and the wording is the owner's, not a
     paraphrase;
  3. the bytes that differ from the input are exactly the declared sites: the appended
     container, the one table slot and the handle words;
  4. the three unchanged rows are byte-identical to the input's own record bytes;
  5. every other table slot is byte-identical to the input, so no other container moved.

Usage:
  python tools/research/verify_friend_v3_world_tournament_split.py \
      --image OUT.gba --manifest OUT.json --against IN.gba
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot.dialogue_repack import container_pointers  # noqa: E402
from tools.webfoot.formats import webfoot_lz                  # noqa: E402
from tools.webfoot.handles import unpack_handle                # noqa: E402

ROM_BASE = 0x08000000
TABLE_LITERAL = 0x123CC
TABLE_SLOTS = 64

#: The owner's wording and row 18's passage, imported from the builder so a check of the
#: product cannot be satisfied by the product's own manifest. A manifest is written by the
#: builder; if the verifier read the expected text out of it, a wrong wording would pass.
from tools.research.build_friend_v3_world_tournament_split import (  # noqa: E402
    OWNER_ROWS, WT18_NEW, WT18_OLD, WT18_RECORD)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--against", required=True)
    args = parser.parse_args()

    image = Path(args.image).read_bytes()
    against = Path(args.against).read_bytes()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    problems: list[str] = []

    def check(condition: bool, message: str) -> None:
        print(("PASS " if condition else "FAIL ") + message)
        if not condition:
            problems.append(message)

    table = int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    check(table == manifest["table_file_offset"],
          f"the literal names the same table as the input (file 0x{table:X})")

    # 1 and 2: the engine's route resolves each placed row to the owner's wording. The
    # expected text is recomputed here from the builder's row table, never read out of the
    # manifest, so a manifest carrying a wrong wording cannot satisfy this check.
    approved = {key: text for key, text in OWNER_ROWS}
    for row in manifest["rows"]:
        handle = int.from_bytes(image[row["sites"][0]:row["sites"][0] + 4], "little")
        selector, start, length = unpack_handle(handle)
        check(selector == manifest["table_slot_selector"],
              f"{row['record']} handle names selector {selector}")
        prefix = row["current"][:1] if row["current"][:1] in "#!" else ""
        if row["record"] == WT18_RECORD:
            if WT18_OLD not in row["current"]:
                check(False, f"{row['record']} does not carry the passage to replace")
                continue
            expected = row["current"].replace(WT18_OLD, WT18_NEW)
        else:
            if row["record"] not in approved or approved[row["record"]] is None:
                check(False, f"{row['record']} is not a row the owner approved")
                continue
            expected = prefix + approved[row["record"]]
        pointer = int.from_bytes(image[table + selector * 4:table + selector * 4 + 4],
                                 "little")
        inside = ROM_BASE <= pointer < ROM_BASE + len(image)
        check(inside, f"{row['record']} slot {selector} resolves to "
                      f"0x{pointer:08X} inside the image")
        if not inside:
            continue
        container = webfoot_lz.unpack(image, pointer - ROM_BASE)
        check(container.kind == 0, f"{row['record']} container is the stored form")
        got = bytes(container.data)[start:start + length].decode("utf-16le")
        check(got == expected, f"{row['record']} reads the owner's wording exactly")
        if got != expected:
            print(f"     expected {expected!r}")
            print(f"     got      {got!r}")

    # 4: the three unchanged rows match the input byte for byte.
    for key in ("3:8550:414", "3:8964:148", "3:9570:92"):
        _sel, start, length = (int(part) for part in key.split(":"))
        check(record_bytes(against, start, length) == record_bytes(image, start, length),
              f"{key} unchanged against the input")

    # 5: every other slot WORD is byte-identical to the input's own word at the same index.
    # This compares the table, not the containers: a slot word that moved would change a
    # container's home, and the extent comparison below is what proves the homes did not move.
    old_table = int.from_bytes(against[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    check(old_table == table, "the table base is unchanged, so both slot words sit at the "
                              "same file offsets")
    slot = manifest["table_slot_selector"]
    check(manifest["table_slot_file_offset"] == table + 4 * slot,
          f"the manifest's slot offset is slot {slot} of this table")
    check(image[table + 4 * slot:table + 4 * slot + 4]
          == (ROM_BASE + manifest["container_file_offset"]).to_bytes(4, "little"),
          f"slot {slot} names the appended container")
    others = [index for index in range(TABLE_SLOTS) if index != slot]
    check(all(image[table + 4 * index:table + 4 * index + 4]
              == against[old_table + 4 * index:old_table + 4 * index + 4]
              for index in others),
          f"the other {len(others)} slot words are unchanged; with the table basis unchanged "
          f"that means every other container keeps its home")

    # 3: the differing bytes are exactly the declared sites.
    allowed = set(range(manifest["container_file_offset"],
                        manifest["container_file_offset"] + 8
                        + manifest["container_declared_size"]))
    allowed.update(range(manifest["table_slot_file_offset"],
                         manifest["table_slot_file_offset"] + 4))
    for change in manifest["handle_changes"]:
        allowed.update(range(change["site"], change["site"] + 4))
    if len(image) > len(against):
        allowed.update(range(len(against), len(image)))
    stray = [offset for offset in range(min(len(image), len(against)))
             if image[offset] != against[offset] and offset not in allowed]
    check(not stray, f"0 differing bytes outside the declared sites (found {len(stray)})")
    if stray:
        print(f"     first stray offsets: {[hex(o) for o in stray[:8]]}")
    check(len(image) == manifest["output_bytes"], "the output byte count matches the manifest")

    print(f"\n{'VERIFY PASS' if not problems else 'VERIFY FAIL: ' + str(len(problems))}")
    return 1 if problems else 0


def record_bytes(image: bytes, start: int, length: int) -> bytes:
    """The decoded bytes of the container-3 record at this span, via the live table."""
    pointer = container_pointers(image)[3]
    stream = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)
    return stream[start:start + length]


if __name__ == "__main__":
    sys.exit(main())
