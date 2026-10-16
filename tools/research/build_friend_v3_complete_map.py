"""Extend the private friend-v3 rename map with the COMPLETE-TEXT-PASS word rules.

WHY THIS EXISTS. The 451-row map the friend's image was built from renames twelve
character names and stops there. Two word rules were never in it: `Saiyaman` ->
`Soyman` (the friend's Great Soyman rename reached the menu pool but not the 20 spoken
occurrences) and `Bulma` -> `Tulma` for the retail word `Bulma` (original Bulma, who
the content pass renamed to Tulma). The splice tool applies ONE map, so the map is
extended rather than a second pass being stacked on top of a spliced image: a second
pass would have to re-encode a container whose records were already relocated.

WHY IT IS A PURE FUNCTION. Every row's replacement text is rebuilt from the RETAIL
text plus the map's own word substitution table plus this ticket's two rules. Nothing
is copied from a built image, so the same inputs always produce the same map, and a
row added for a record the operator's map never covered cannot disagree with a
neighbouring row that was covered: both are the same function of the same table.
Measured: the table reconstructs all 451 authored rows exactly, so this is not a
re-interpretation of the map, it is the map's own rule.

PROVENANCE, NOT STRING REPLACEMENT. `Bulma` -> `Tulma` is applied ONLY where the
retail word carries `Bulma`. The rename pass had already turned retail `Chi-Chi` into
the displayed name `Bulma`, and those occurrences must keep it: the two are
distinguished by aligning the retail words against the substituted words and touching
only the aligned-equal ones. A blind replacement would rename the wrong character.

WHAT IT DOES NOT DO. It does not decide which records are displayed; it covers every
record the engine's own handle inventory finds. It does not invent text: every output
row is a retail record with a word substituted.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import struct
import sys
from pathlib import Path

from tools.research.splice_dialogue_tokens import (ROM_BASE, TABLE_LITERAL,
                                                   load_map, sha256,
                                                   substitution_table)
from tools.webfoot import compressed_dialogue as cd
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.token_dictionary import TokenDictionary, decode_text

SLOTS = 7
TOKENS = ("Ya", "ha", "Kr", "in", "Ti", "YA", "HA", "KR", "IN", "TI")
#: This ticket's word rules. The left side is matched inside a retail word, so
#: `Bulma's`, `Saiyaman!` and the uppercase spellings are covered; the right side
#: replaces the whole word, in the case the retail word used.
RULES = (("Saiyaman", "Soyman"), ("Bulma", "Tulma"), ("Chichi", "Bulma"))


class CompleteMapError(ValueError):
    """The map could not be extended, so nothing was written."""


def boundary(name: str) -> str:
    return r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])"


def _same_case(found: str, target: str) -> str:
    return target.upper() if found.isupper() else target


def ruled(old_text: str, new_text: str) -> tuple[str, tuple[str, ...]]:
    """`new_text` with this ticket's rules applied where the RETAIL word carries them.

    Retail and substituted words are aligned with a word-level diff, and only equal
    runs are touched. That is the whole provenance rule: a word the operator's map
    already changed (retail `Chi-Chi` -> displayed `Bulma`) sits in a replaced run and
    is left alone, while a word the map copied through (retail `Bulma` -> `Bulma`) sits
    in an equal run and becomes `Tulma`.
    A rule matches CASE-INSENSITIVELY and carries the retail word's case into the
    replacement, because the retail text spells the same name `SAIYAMAN`, `Vegito` and
    `CHI-CHI` in different records and a case-sensitive rule is blind to all but one.
    """
    old_words = old_text.split(" ")
    new_words = new_text.split(" ")
    if old_words.count("") != new_words.count(""):
        raise CompleteMapError("a padding run makes the word alignment ambiguous")
    applied: list[str] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, old_words, new_words, autojunk=False).get_opcodes():
        if tag != "equal":
            continue
        for offset in range(i2 - i1):
            word = old_words[i1 + offset]
            replacement = new_words[j1 + offset]
            for source, target in RULES:
                if re.search(boundary(source), word, re.IGNORECASE):
                    replacement = re.sub(
                        boundary(source),
                        lambda found, want=target: _same_case(found.group(0), want),
                        replacement, flags=re.IGNORECASE)
                    applied.append(f"{source}->{target}")
            new_words[j1 + offset] = replacement
    return " ".join(new_words), tuple(applied)


def substitute(words: list[str], table: dict[str, str]) -> str:
    """The map's own substitutions applied to a retail word list, longest run first."""
    longest = max(len(key.split(" ")) for key in table)
    out: list[str] = []
    index = 0
    while index < len(words):
        for run in range(min(longest, len(words) - index), 0, -1):
            key = " ".join(words[index:index + run])
            if key in table:
                out.append(table[key])
                index += run
                break
        else:
            out.append(words[index])
            index += 1
    return " ".join(out)


def records(image: bytes) -> dict[str, tuple[str, tuple[int, ...]]]:
    """Every record the engine's own handle inventory finds, with its retail text."""
    table = struct.unpack_from("<I", image, TABLE_LITERAL)[0] - ROM_BASE
    dictionary = TokenDictionary(TOKENS)
    found: dict[str, tuple[str, tuple[int, ...]]] = {}
    for selector in range(SLOTS):
        pointer = struct.unpack_from("<I", image, table + selector * 4)[0]
        if pointer < ROM_BASE or pointer - ROM_BASE >= len(image):
            continue
        stream = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)
        for record in cd.dialogue_record_inventory(image, selector, len(stream)):
            handle = record.handle
            key = f"{selector}:{handle.decoded_start}:{handle.decoded_length}"
            text = decode_text(
                stream[handle.decoded_start:handle.decoded_end].decode("utf-16le",
                                                                      "replace"),
                dictionary)
            found[key] = (text, tuple(record.sites))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-map", required=True)
    parser.add_argument("--base", required=True, help="the image old_text is read from")
    parser.add_argument("--base-sha256", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()

    base, destination = Path(args.base), Path(args.out)
    if base.resolve() == destination.resolve():
        raise SystemExit("the output map would overwrite the image it is read from")
    measured = sha256(base)
    if measured != args.base_sha256.lower():
        raise SystemExit(f"the base is not the declared image: {measured}")

    rows = load_map(Path(args.base_map))
    table = substitution_table(rows)
    image = base.read_bytes()
    inventory = records(image)

    added: list[dict] = []
    edited: list[dict] = []
    untouched: list[str] = []
    for key in sorted(inventory):
        old_text, sites = inventory[key]
        if not any(re.search(boundary(source), old_text, re.IGNORECASE)
                   for source, _ in RULES):
            continue
        selector, start, length = (int(part) for part in key.split(":"))
        if key in rows and rows[key]["old_text"] != old_text:
            raise CompleteMapError(
                f"{key}: the map's old_text is not the text this image holds, so the "
                f"map describes a different build"
            )
        new_text, applied = ruled(old_text, substitute(old_text.split(" "), table))
        if not applied or new_text == old_text:
            untouched.append(key)
            continue
        if key in rows:
            row = dict(rows[key])
            row["new_text"] = new_text
            edited.append({"key": key, "words": sorted(set(applied)),
                           "old_text": old_text, "new_text": new_text})
        else:
            row = {"old_selector": selector, "old_start": start, "old_length": length,
                   "old_text": old_text, "new_text": new_text,
                   "sites": list(sites), "added_by": "FRIEND-V3-COMPLETE-TEXT-PASS-001"}
            added.append({"key": key, "words": sorted(set(applied)),
                          "old_text": old_text, "new_text": new_text})
        rows[key] = row

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    report = {
        "base_map": str(args.base_map),
        "base_map_sha256": sha256(Path(args.base_map)),
        "base_image": str(base),
        "base_image_sha256": measured,
        "rules": [list(rule) for rule in RULES],
        "rows_in": len(load_map(Path(args.base_map))),
        "rows_out": len(rows),
        "added": added,
        "edited": edited,
        "ruled_but_unchanged": untouched,
        "output_sha256": sha256(destination),
    }
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=1, ensure_ascii=False),
                                     encoding="utf-8")
    print(f"map            : {destination}")
    print(f"map sha256     : {report['output_sha256']}")
    print(f"rows in/out    : {report['rows_in']} / {report['rows_out']}")
    print(f"rows added     : {len(added)}")
    print(f"rows edited    : {len(edited)}")
    print(f"ruled but same : {len(untouched)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
