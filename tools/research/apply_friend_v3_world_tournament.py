"""Write the owner's World Tournament lines that fit without the handle-format change.

WHY EXACT-LENGTH WRITING. A record's span is fixed by its handle, so a shorter line is
written into its own span and the tail is filled with the space unit. That keeps EVERY
offset in the container exactly where it was, so no overlapping record moves, and it is the
same technique the trailing-pad repair uses in reverse. It does leave visible padding on
that line, which is the defect this ticket exists to remove; those lines are therefore
reported as padded, and the successor engine ticket removes the pad by re-laying out the
container.

WHAT IS NOT WRITTEN. A line longer than its record cannot be written this way, and the owner
forbade shortening it. Those records are left byte-identical and listed with their measured
overflow, so they move to the engine ticket with a number attached.

Every site is checked: the record must exist at the named identity, and every handle site that
carries it is rewritten.

Usage:
  python tools/research/apply_friend_v3_world_tournament.py --image IN.gba \
      --expect-sha256 <hex> --out OUT.gba --manifest OUT.json
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

from tools.webfoot import compressed_dialogue as cd  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402
from tools.webfoot.handles import pack_handle  # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

ROM_BASE = 0x08000000
TABLE_LITERAL = 0x123CC
SPACE = 0x0020


class WorldTournamentError(ValueError):
    """The write refused rather than placing a line it could not verify."""


#: The owner's authored script, verbatim (seq 2878 section 2). `None` is a line the owner
#: marked NO CHANGE. Line 18's passage replacement is expressed as (old, new) so the rest of
#: the announcer's speech is preserved exactly.
OWNER_LINES: tuple[tuple[str, str | None], ...] = (
    ("3:7406:136",
     "Hey sis, if you win the tournament, what do you think you'll get with the prize Zeni?"),
    ("3:7542:42", "Uh, tons of okonomiyaki, I guess!"),
    ("3:7584:80", "Sheesh, Videl! How are you not fat?"),
    ("3:7664:60", "EXCUSE ME?! What are you going to get then?"),
    ("3:7724:72", "Candy. Lots and lots of candy."),
    ("3:7796:204", "And you call me fat. Hey, isn't that kind of meta?"),
    ("3:8000:214", "Hey, half pint! We don't take too kindly to your folk around here."),
    ("3:8214:118", "Huh? Do you mean brown people?"),
    ("3:8332:218",
     "What?! No! My mom may be racist, but I'm not! Geez, I meant adopted kids!"),
    ("3:8550:414", None),
    ("3:8964:148", None),
    ("3:9112:62", "You really made me look bad earlier."),
    ("3:9174:114", "Bruh. You were still totally a dick."),
    ("3:9288:282",
     "That's my baby Idasa down there! Oooooo! Idasa! I wish they would match Idasa up with "
     "a whiter kid! This is a disgrace!"),
    ("3:9570:92", None),
    ("3:9662:116", "Get him, Uub! You make that boy sorry his mom is racist!"),
    ("3:9778:114", "Noooo! My baby! That was unfair! That thing cheated!"),
)

#: Line 18: the owner's required passage, and the wording this image holds. The old passage
#: includes the rename's four-unit pad inside "Uub    and" because that is what the record
#: actually reads; matching it without the pad finds nothing.
WT18_RECORD = "3:9892:486"
WT18_OLD = "Championship between eight-year-old Uub    and seven-year-old Videl!"
WT18_NEW = ("Championship between adopted siblings, ten-year-old Uub and "
            "sixteen-year-old Videl!")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def records_of(image: bytes) -> dict[str, tuple[bytes, int, list[int]]]:
    """``key -> (decoded stream, container file offset, handle sites)`` for every record."""
    table = int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    out: dict[str, tuple[bytes, int, list[int]]] = {}
    for selector in range(7):
        pointer = int.from_bytes(image[table + selector * 4:table + selector * 4 + 4],
                                  "little")
        if pointer < ROM_BASE or pointer - ROM_BASE >= len(image):
            continue
        offset = pointer - ROM_BASE
        stream = bytes(webfoot_lz.unpack(image, offset).data)
        for record in cd.dialogue_record_inventory(image, selector, len(stream)):
            key = (f"{selector}:{record.handle.decoded_start}:"
                   f"{record.handle.decoded_length}")
            out[key] = (stream, offset, list(record.sites))
    return out


def plan(image: bytes) -> tuple[list[dict], list[dict]]:
    """``(writes, blocked)``: the lines that fit, and the lines that do not."""
    known = records_of(image)
    writes: list[dict] = []
    blocked: list[dict] = []
    for key, approved in OWNER_LINES:
        if approved is None:
            continue
        found = known.get(key)
        if found is None:
            blocked.append({"record": key, "why": "no record carries this identity"})
            continue
        stream, offset, sites = found
        selector, start, length = (int(part) for part in key.split(":"))
        current = stream[start:start + length].decode("utf-16le", "replace")
        units = len(approved)
        if units * 2 > length:
            blocked.append({"record": key, "why": "grows the record",
                            "current_units": length // 2, "approved_units": units,
                            "need_units": units - length // 2,
                            "current": current, "approved": approved})
            continue
        writes.append({"record": key, "selector": selector, "start": start,
                       "length": length, "sites": sites, "stream_offset": offset,
                       "text": approved + " " * ((length - units * 2) // 2),
                       "pad_units": (length - units * 2) // 2,
                       "current": current, "approved": approved})

    found = known.get(WT18_RECORD)
    if found is None:
        blocked.append({"record": WT18_RECORD, "why": "no record carries this identity"})
    else:
        stream, offset, sites = found
        selector, start, length = (int(part) for part in WT18_RECORD.split(":"))
        current = stream[start:start + length].decode("utf-16le", "replace")
        if WT18_OLD not in current:
            blocked.append({"record": WT18_RECORD, "why": "the passage to replace is absent",
                            "current": current})
        else:
            approved = current.replace(WT18_OLD, WT18_NEW)
            units = len(approved)
            if units * 2 > length:
                blocked.append({"record": WT18_RECORD, "why": "grows the record",
                                "current_units": length // 2, "approved_units": units,
                                "need_units": units - length // 2,
                                "current": current, "approved": approved})
            else:
                writes.append({"record": WT18_RECORD, "selector": selector, "start": start,
                               "length": length, "sites": sites,
                               "text": approved + " " * ((length - units * 2) // 2),
                               "pad_units": (length - units * 2) // 2,
                               "current": current, "approved": approved})
    return writes, blocked


def apply(image: bytes, writes: list[dict]) -> tuple[bytes, list[dict]]:
    out = bytearray(image)
    changes: list[dict] = []
    for entry in writes:
        encoded = entry["text"].encode("utf-16le")
        if len(encoded) != entry["length"]:
            raise WorldTournamentError(f"{entry['record']}: the exact-length text is "
                                       f"{len(encoded)} bytes against {entry['length']}")
        # THE DECODED STREAM BEGINS 8 BYTES INTO THE CONTAINER: file[offset:offset+8] is the
        # kind/size wrapper and is not part of what the reader returns, as measured by
        # comparing the file bytes to the decoded stream. The offset stored per record is the
        # CONTAINER's file offset, so the byte to write is offset + 8 + start.
        base = entry["stream_offset"] + 8 + entry["start"]
        out[base:base + len(encoded)] = encoded
        for site in entry["sites"]:
            word = pack_handle(entry["selector"], entry["start"],
                               entry["length"]).to_bytes(4, "little")
            if bytes(image[site:site + 4]) != word:
                raise WorldTournamentError(
                    f"{entry['record']}: handle site 0x{site:06X} does not carry this "
                    "record's handle; refusing"
                )
        changes.append({"record": entry["record"], "selector": entry["selector"],
                        "bytes_at": base, "bytes": len(encoded),
                        "pad_units": entry["pad_units"]})
    return bytes(out), changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out")
    parser.add_argument("--manifest")
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise WorldTournamentError(f"REFUSED: {source} is {got}, expected "
                                   f"{args.expect_sha256.lower()}")

    writes, blocked = plan(image)
    for entry in blocked:
        print(f"BLOCKED {entry['record']}: {entry['why']}"
              + (f" (needs {entry['need_units']} more unit(s))"
                 if "need_units" in entry else ""))
    print(f"# {len(writes)} line(s) placeable, {len(blocked)} blocked, "
          f"{sum(1 for _key, text in OWNER_LINES if text is None)} no-change")
    for entry in writes:
        print(f"   {entry['record']:<16} pad {entry['pad_units']:>3} unit(s)  "
              f"{entry['approved'][:56]!r}")

    report = {"input": str(source), "input_sha256": got,
              "placeable": [{k: v for k, v in entry.items() if k != "sites"}
                            for entry in writes],
              "blocked": blocked}
    if not args.out:
        if args.manifest:
            Path(args.manifest).write_text(json.dumps(report, indent=2) + "\n",
                                           encoding="utf-8")
        return 0

    output, changes = apply(image, writes)
    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise WorldTournamentError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(output)
    if staged.read_bytes() != output:
        raise WorldTournamentError("REFUSED: the staged write does not match the plan")
    staged.replace(target)
    report.update({"output": str(target), "output_sha256": sha256_bytes(output),
                   "output_bytes": len(output), "changes": changes})
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(report, indent=2) + "\n",
                                       encoding="utf-8")
    print(f"# wrote {target} {len(output)} bytes sha256 {report['output_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
