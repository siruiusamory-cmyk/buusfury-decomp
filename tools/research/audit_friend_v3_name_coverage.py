"""Report every character-name occurrence on the friend image's text surfaces.

WHAT THIS IS FOR. The ticket's acceptance is a full coverage report, not a diff: every
discovered character-name occurrence must be accounted for as corrected, intentionally
preserved, or explicitly unresolved. A per-name count cannot do that, for two measured
reasons: the map is not a permutation (the displayed name `Goku` belongs to retail
Krillin, `Gohan` to retail Yamcha), and a rule applied TWICE - retail `Gohan` shown as
`Goku` - looks exactly like a correct rename in a count.

HOW IT DECIDES. For each surface it builds the EXPECTED text: the retail text with every
retail name replaced by the single name it must display as. Expected and displayed are
then aligned token by token, and each retail name is judged by what appears in the run it
aligns to. Pairing the retail name directly with a displayed token instead would mis-pair
a chain that swaps two names in one sentence (retail `Goku and Krillin` displays as
`Yamcha and Goku`), which is a real record in this image.

Two surfaces, two provenances, because they are different corpora:
  * the 1,534-entry text table, whose provenance is the canonical ROM (slot `i` holds the
    retail string at slot `i`; the menu pass rewrote text in place or repointed the slot);
  * the seven compressed dialogue containers, whose provenance is the base image the
    rename map describes.

PROTECTED SPELLINGS are reported as preserved, never as misses: `Grandpa Gohan` is a
different character from Gohan, `planet/Planet Vegeta` is a place, and `Gotenks` and
`Gokuu` carry a mapped name inside a different word. APPROVED lists the occurrences an
owner decision deliberately leaves alone, each with its reason.

THE NAME MAP is stated rather than derived, because two of its rows (`Android 18` ->
`Chi-Chi` from the menu pass, `Bulma` -> `Tulma` from the content pass) never appear in
the 451-row dialogue map, and `Gogeta`/`Vegito` appear there in only a few records.

Exit status is 1 while any occurrence is neither correct, protected nor approved, so the
report can gate a build.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

from tools.research.splice_dialogue_tokens import ROM_BASE, TABLE_LITERAL, sha256
from tools.webfoot import compressed_dialogue as cd
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.formats.text_tables import read_pointer

TABLE_START = 0x0006BCE8
TABLE_COUNT = 1534
DIALOGUE_SLOTS = 7
TOKENS = ("Ya", "ha", "Kr", "in", "Ti", "YA", "HA", "KR", "IN", "TI")
TOKEN_BASE = 0xE000

#: retail name -> the one name it displays as.
NAME_MAP = {"Goku": "Yamcha", "Kakarot": "Yamcha", "Gohan": "Krillin", "Goten": "Videl",
            "Trunks": "Uub", "Vegeta": "Tien", "Krillin": "Goku", "Yamcha": "Gohan",
            "Chi-Chi": "Bulma", "Chi Chi": "Bulma", "Android 18": "Chi-Chi",
            "Android #18": "Chi-Chi", "Gogeta": "Yamien", "Vegito": "Tiencha",
            "Saiyaman": "Soyman", "Bulma": "Tulma"}
#: A mapped name inside one of these is a different character or a place, not a miss.
PROTECTED = ("Grandpa Gohan", "planet Vegeta", "Planet Vegeta", "Gotenks", "Gokuu")
#: Occurrences an owner decision leaves as retail. Each is reported, never hidden.
APPROVED = {
    ("menu", 1033): "content pass's authored twin-sister biography, preserved as approved",
}
#: Control codes separate tokens, so a name carrying one is still one token. Splitting on
#: them keeps the retail and displayed token lists comparable: padding spaces and line
#: breaks both vanish, and `\x08\x07Gohan's` becomes the token `Gohan's`.
SPLIT = re.compile(r"[\s\x00-\x08\x0b\x0c\x0e-\x1f]+")
PUNCT = ".,!?'\")]}\u2026"


class CoverageError(ValueError):
    """The report could not be produced, so nothing was written."""


def expand(text: str) -> str:
    out: list[str] = []
    for character in text:
        index = ord(character) - TOKEN_BASE
        out.append(TOKENS[index] if 0 <= index < len(TOKENS) else character)
    return "".join(out)


def tokens(text: str, expand_tokens: bool = False) -> list[str]:
    if expand_tokens:
        text = expand(text)
    return [part for part in SPLIT.split(text) if part]


def core(word: str) -> str:
    """The word with padding, punctuation and a possessive stripped."""
    word = word.strip().strip(PUNCT)
    return word[:-2] if word.endswith("'s") else word


def protected_in(text: str, name: str) -> bool:
    """True when the word rides inside a protected PHRASE of the retail text."""
    return any(phrase in text and name in phrase for phrase in PROTECTED)


def expected_tokens(retail: list[str]) -> tuple[list[str], list[int]]:
    """The retail tokens with every name replaced, and which retail token produced each."""
    keys = sorted(NAME_MAP, key=lambda key: -len(key.split(" ")))
    out: list[str] = []
    owner: list[int] = []
    index = 0
    while index < len(retail):
        for key in keys:
            size = len(key.split(" "))
            if size > 1 and [core(word) for word in retail[index:index + size]] == \
                    key.split(" "):
                out.append(NAME_MAP[key])
                owner.append(index)
                index += size
                break
        else:
            name = core(retail[index])
            out.append(NAME_MAP.get(name, retail[index]))
            owner.append(index)
            index += 1
    return out, owner


def slot_text(image: bytes, slot: int) -> str:
    offset = read_pointer(image, slot, TABLE_START)
    end = offset
    while image[end:end + 2] != b"\x00\x00":
        end += 2
    return image[offset:end].decode("utf-16le")


def record(before: str, after: str, **where: object) -> list[dict]:
    retail = tokens(before)
    shown = tokens(after, expand_tokens=True)
    expected, owner = expected_tokens(retail)
    matcher = difflib.SequenceMatcher(None, [core(word) for word in expected],
                                      [core(word) for word in shown], autojunk=False)
    out: list[dict] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        run = [core(word) for word in shown[j1:j2]]
        for position in range(i1, i2):
            retail_word = retail[owner[position]]
            name = core(retail_word)
            if name not in NAME_MAP:
                continue
            want = core(expected[position])
            if protected_in(before, name):
                verdict = "protected"
            elif tag == "equal" or want in run:
                verdict = "correct"
            elif name in run:
                verdict = "missed"
            elif any(word in NAME_MAP for word in run):
                verdict = "cascade"
            else:
                verdict = "absent"
            out.append({**where, "retail": retail_word, "expected": want,
                        "displayed": " ".join(shown[j1:j2]), "verdict": verdict,
                        "text": after})
    return out


def menu_surface(canonical: bytes, candidate: bytes) -> list[dict]:
    findings: list[dict] = []
    for slot in range(TABLE_COUNT):
        findings += record(slot_text(canonical, slot), slot_text(candidate, slot),
                           surface="menu", slot=slot)
    return findings


def dialogue_surface(base: bytes, candidate: bytes) -> list[dict]:
    before_all, after_all = all_records(base), all_records(candidate)
    findings: list[dict] = []
    for key, retail in before_all.items():
        if key not in after_all:
            raise CoverageError(f"{key}: present in the base and not in the candidate")
        after = after_all[key]
        if len(after) != len(retail):
            raise CoverageError(f"{key}: stored length changed")
        findings += record(retail, after, surface="dialogue", record=key)
    return findings


def all_records(image: bytes) -> dict[str, str]:
    table = struct.unpack_from("<I", image, TABLE_LITERAL)[0] - ROM_BASE
    out: dict[str, str] = {}
    for selector in range(DIALOGUE_SLOTS):
        pointer = struct.unpack_from("<I", image, table + selector * 4)[0]
        if pointer < ROM_BASE or pointer - ROM_BASE >= len(image):
            continue
        stream = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)
        for entry in cd.dialogue_record_inventory(image, selector, len(stream)):
            handle = entry.handle
            key = f"{selector}:{handle.decoded_start}:{handle.decoded_length}"
            out[key] = stream[handle.decoded_start:handle.decoded_end].decode(
                "utf-16le", "replace")
    return out


def approved(row: dict) -> bool:
    return (row["surface"], row.get("slot")) in APPROVED


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--canonical", required=True,
                        help="the immutable retail image, the menu pool's provenance")
    parser.add_argument("--base", required=True,
                        help="the image the rename map's old_text is read from")
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()

    canonical = Path(args.canonical).read_bytes()
    base = Path(args.base).read_bytes()
    candidate = Path(args.candidate).read_bytes()
    findings = menu_surface(canonical, candidate) + dialogue_surface(base, candidate)
    for row in findings:
        if approved(row):
            row["verdict"] = "approved"

    tally = Counter(f"{row['surface']}:{row['verdict']}" for row in findings)
    per_name = Counter(f"{row['surface']}:{row['retail']}:{row['verdict']}"
                       for row in findings)
    unresolved = [row for row in findings
                  if row["verdict"] not in ("correct", "protected", "approved")]
    report = {
        "canonical_sha256": sha256(Path(args.canonical)),
        "base_sha256": sha256(Path(args.base)),
        "candidate_sha256": sha256(Path(args.candidate)),
        "occurrences": len(findings),
        "verdicts": dict(sorted(tally.items())),
        "by_name": dict(sorted(per_name.items())),
        "approved": {f"{key[0]}:{key[1]}": reason for key, reason in APPROVED.items()},
        "findings": findings,
    }
    print(f"occurrences      : {len(findings)}")
    for key, count in sorted(tally.items()):
        print(f"  {key:<28} {count}")
    print(f"unresolved       : {len(unresolved)}")
    grouped: dict[tuple, int] = defaultdict(int)
    for row in unresolved:
        grouped[(row["surface"], row["verdict"], core(row["retail"]),
                 row["displayed"] or "-")] += 1
    for (surface, verdict, old, new), count in sorted(grouped.items()):
        print(f"  {surface:<9} {verdict:<12} retail {old!r:<12} -> {new!r:<20} x{count}")
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=1, ensure_ascii=False),
                                     encoding="utf-8")
        print(f"report           : {args.report}")
    return 0 if not unresolved else 1


if __name__ == "__main__":
    sys.exit(main())
