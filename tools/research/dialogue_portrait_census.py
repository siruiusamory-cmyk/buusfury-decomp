"""Census of the dialogue record word: handler, portrait operand, and the character it resolves to.

Read-only. The text tool needs to group lines by speaker, and the only identity a dialogue record
carries is its portrait operand, so this measures that operand across the whole corpus and reports what
each value can and cannot say.

Record word layout, measured by the static lane (docs/research/FRIEND_V3_IDASA_UUB_DIALOGUE.md and the
portrait consumer read): 8 bytes, `+0x00` u16 index, `+0x02` handler byte into the table at
`0x080728AC`, `+0x03` PORTRAIT OPERAND, `+0x04` packed dialogue handle. The operand is consumed at
`0x080122A6` (`ldrb r2,[r5,#3]`) and means:

* `0` or `7`  - no portrait at all: the constructor takes the `r1 = 0` branch and the text object
  carries no art. There is no default portrait and no fallback to the speaker's own record.
* `1..6`      - the PARTY path: a save/party byte in EWRAM (`[0x08072890] = 0x03001068`, byte
  `+0x50C`), then the party record table `0x086B82EC` (stride 24) byte `0x0F + operand` gives a
  portrait slot. Which character that is depends on the player's save, so it is not statically
  resolvable.
* `>= 8`      - a portrait array index: `0x086F393C + 4*operand`, no clamp and no null test. The
  engine never joins that back to a character; the join is by VALUE (`appearance[+0x08] == operand`)
  and lives in the research harness, not in code.

Candidate records are found by the only test the format itself offers: a handler byte in 0..7 and a
handle word that decodes to a live span of printable text in a live container.
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

from tools.webfoot import compressed_dialogue as cd  # noqa: E402
from tools.webfoot.dialogue_repack import container_pointers, text_of  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402
from tools.webfoot.handles import unpack_handle  # noqa: E402

ROM_BASE = 0x08000000
APPEARANCE_TABLE = 0x74D380
APPEARANCE_STRIDE = 0x10
TEXT_TABLE_START = 0x6BCE8
HANDLER_TABLE = 0x728AC
HANDLER_COUNT = 8
RECORD_BYTES = 8
PORTRAIT_OFFSET = 3
HANDLE_OFFSET = 4


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def text_of_slot(image: bytes, slot: int) -> str:
    pointer = word(image, TEXT_TABLE_START + 4 * slot)
    if pointer < ROM_BASE or pointer - ROM_BASE + 2 > len(image):
        return ""
    offset = pointer - ROM_BASE
    end = offset
    while end + 1 < len(image) and image[end:end + 2] != b"\x00\x00":
        end += 2
    return image[offset:end].decode("utf-16le", "replace")


def classify_operand(value: int) -> str:
    """What a record's portrait operand means, from the consumer's own branches.

    `0x0801206E`/`0x08012072` route 0 and 7 to `r1 = 0` (no art, no default, no fallback);
    `0x0801211C..0x0801213C` route 1..6 through a save/party byte, so the character depends on the
    player's save file; `0x08012118`/`0x0801211A` send 8 and above to the portrait array at
    `0x086F393C + 4*operand` with no clamp and no null test.
    """
    if value in (0, 7):
        return "none"
    if 1 <= value <= 6:
        return "party"
    return "array"


def portrait_to_characters(image: bytes) -> dict[int, list[str]]:
    """Portrait slot -> the character names whose appearance records carry that slot."""
    out: dict[int, list[str]] = {}
    for index in range(232):
        base = APPEARANCE_TABLE + APPEARANCE_STRIDE * index
        slot = word(image, base + 0x08)
        if not slot:
            continue
        name = text_of_slot(image, struct.unpack_from("<H", image, base)[0])
        out.setdefault(slot, []).append(name)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--json")
    args = parser.parse_args()
    image = Path(args.rom).read_bytes()

    streams = {}
    for selector, pointer in container_pointers(image).items():
        if pointer >= ROM_BASE and pointer - ROM_BASE + 8 < len(image):
            streams[selector] = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)
    payload_sizes = {selector: len(stream) for selector, stream in streams.items()}
    characters = portrait_to_characters(image)

    # One pass over every word-aligned word, so a record's reference count is a lookup rather than a
    # scan of the whole image per candidate.
    reference_counts: dict[int, int] = {}
    for at in range(0, len(image) - 4, 4):
        value = word(image, at)
        reference_counts[value] = reference_counts.get(value, 0) + 1

    def read_record(offset: int) -> dict | None:
        """A record word, or None when the bytes do not satisfy the format."""
        if offset < 0 or offset + RECORD_BYTES > len(image):
            return None
        handler = image[offset + 2]
        if handler >= HANDLER_COUNT:
            return None
        try:
            selector, start, length = unpack_handle(word(image, offset + HANDLE_OFFSET))
        except Exception:
            return None
        if selector not in payload_sizes or length == 0:
            return None
        if start + length > payload_sizes[selector]:
            return None
        text = text_of(streams[selector], start, length)
        stripped = text.lstrip("#!")
        if len(stripped) < 4 or not any(character.isalpha() for character in stripped):
            return None
        return {"file": offset, "handler": handler, "operand": image[offset + PORTRAIT_OFFSET],
                "handle": f"{selector}:{start}:{length}", "text": text,
                "references": reference_counts.get(offset + ROM_BASE, 0)}

    # A record counts only as an entry of a record LIST: an array of pointers whose entries are record
    # words, with at least two entries and no valid record pointer immediately before it, so the array
    # start is not itself the middle of a longer run.
    records = []
    lists = []
    at = 0
    while at + 8 <= len(image) - 4:
        first = word(image, at)
        second = word(image, at + 4)
        if first >= ROM_BASE and second >= ROM_BASE:
            head = read_record(first - ROM_BASE)
            tail = read_record(second - ROM_BASE)
            before = read_record(word(image, at - 4) - ROM_BASE) if at >= 4 and \
                word(image, at - 4) >= ROM_BASE else None
            if head is not None and tail is not None and before is None:
                entries = []
                cursor = at
                while cursor + 4 <= len(image) - 4:
                    pointer = word(image, cursor)
                    if pointer < ROM_BASE:
                        break
                    entry = read_record(pointer - ROM_BASE)
                    if entry is None:
                        break
                    entries.append(entry)
                    cursor += 4
                if len(entries) >= 2:
                    lists.append({"array_file": at, "entries": len(entries)})
                    records.extend(entries)
                    at = cursor
                    continue
        at += 4

    by_handler: dict[int, int] = {}
    by_class: dict[str, int] = {"none": 0, "party": 0, "array": 0}
    by_character: dict[str, int] = {}
    unresolved: dict[int, int] = {}
    for record in records:
        by_handler[record["handler"]] = by_handler.get(record["handler"], 0) + 1
        operand = record["operand"]
        record["class"] = classify_operand(operand)
        by_class[record["class"]] += 1
        if record["class"] == "array":
            names = characters.get(operand)
            record["characters"] = names or []
            if names:
                for name in names:
                    by_character[name] = by_character.get(name, 0) + 1
            else:
                unresolved[operand] = unresolved.get(operand, 0) + 1

    referenced = [record for record in records if record["references"]]
    document = {"records": records, "lists": lists, "by_handler": by_handler,
                "by_class": by_class,
                "by_character": by_character, "unresolved_operands": unresolved,
                "records_with_a_reference": len(referenced)}
    print(f"record lists: {len(lists)}; records that are list entries: {len(records)} "
          f"(with at least one word reference: {len(referenced)})")
    print(f"by handler: {dict(sorted(by_handler.items()))}")
    print(f"by operand class: {by_class}")
    print(f"characters named by >= 8 operands: {len(by_character)}")
    for name, count in sorted(by_character.items(), key=lambda item: -item[1])[:20]:
        print(f"  {count:>5}  {name}")
    print(f"operands with no appearance record: {sorted(unresolved.items())[:12]}")
    # Per-handler breakdown, and the dialogue handler on its own: only handler 5 renders dialogue, so
    # the "how often is there no portrait" question is a question about that handler.
    per_handler: dict[int, dict] = {}
    for record in records:
        entry = per_handler.setdefault(record["handler"], {"total": 0, "none": 0, "party": 0,
                                                            "array": 0, "characters": {}})
        entry["total"] += 1
        entry[record["class"]] += 1
        for name in record.get("characters", []):
            entry["characters"][name] = entry["characters"].get(name, 0) + 1
    dialogue = per_handler.get(5, {})
    print("per handler: total / no portrait / party / array")
    for handler in sorted(per_handler):
        entry = per_handler[handler]
        print(f"  handler {handler}: {entry['total']} / {entry['none']} / {entry['party']} / "
              f"{entry['array']}")
    if dialogue:
        total = dialogue["total"]
        print(f"handler 5 (dialogue): {total} records; no portrait {dialogue['none']} "
              f"({100 * dialogue['none'] / total:.0f}%), party {dialogue['party']} "
              f"({100 * dialogue['party'] / total:.0f}%), array {dialogue['array']} "
              f"({100 * dialogue['array'] / total:.0f}%)")
        top = sorted(dialogue["characters"].items(), key=lambda item: -item[1])[:12]
        print(f"handler 5 top characters: {top}")
    document["per_handler"] = per_handler

    if args.json:
        Path(args.json).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        print(f"# wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
