"""Every dialogue record that names Dabura, with its neighbours, for the owner's rewording.

Read-only. The owner is writing new wording for these lines, so this lists each one in full with the
lines either side of it, which is what shows the scene: a record carries no speaker field (the script
binds the speaker), so nothing here guesses one.

Usage: python -m tools.research.dabura_lines --image IMG.gba [--out FILE.md]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot import compressed_dialogue as cd  # noqa: E402
from tools.webfoot.dialogue_repack import container_pointers, text_of  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402

ROM_BASE = 0x08000000
NAME = "Dabura"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    image = Path(args.image).read_bytes()
    streams = {}
    for selector, pointer in container_pointers(image).items():
        if pointer >= ROM_BASE and pointer - ROM_BASE + 8 < len(image):
            streams[selector] = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)

    rows = []
    for selector, stream in sorted(streams.items()):
        records = [entry for entry in cd.dialogue_record_inventory(image, selector, len(stream))
                   if entry.handle.decoded_start + entry.handle.decoded_length <= len(stream)]
        records.sort(key=lambda entry: entry.handle.decoded_start)
        for position, entry in enumerate(records):
            start, length = entry.handle.decoded_start, entry.handle.decoded_length
            text = text_of(stream, start, length)
            if NAME not in text:
                continue
            before = (text_of(stream, records[position - 1].handle.decoded_start,
                              records[position - 1].handle.decoded_length)
                      if position > 0 else "")
            after = (text_of(stream, records[position + 1].handle.decoded_start,
                             records[position + 1].handle.decoded_length)
                     if position + 1 < len(records) else "")
            rows.append({"handle": f"{selector}:{start}:{length}", "text": text,
                         "before": before, "after": after,
                         "occurrences": text.count(NAME)})

    lines = ["# Dialogue records that name Dabura", "",
             f"Image: {args.image}",
             f"Records: {len(rows)}; total occurrences of the name: "
             f"{sum(row['occurrences'] for row in rows)}", "",
             "A record carries no speaker field: the script binds the speaker. Neighbours are given"
             " because they are what a reader can see.", ""]
    for index, row in enumerate(rows, start=1):
        lines.append(f"## {index}. `{row['handle']}` ({row['occurrences']} occurrence(s))")
        lines.append("")
        if row["before"]:
            lines.append(f"- before: {row['before'][:200]}")
        lines.append(f"- **text**: {row['text']}")
        if row["after"]:
            lines.append(f"- after: {row['after'][:200]}")
        lines.append("")
    output = "\n".join(lines)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(output, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
