"""Repair trailing space padding in a friend image's dialogue handles.

WHAT THIS DOES, AND WHY IT IS SAFE BY CONSTRUCTION. A record whose last units are
padding spaces can be repaired by REDUCING its handle's decoded length: the engine
copies exactly the handle's length, so the record then reads its text with the pad
gone and NOT ONE OTHER BYTE MOVES. The pad bytes stay in the stream where they were,
so every other record's span still reads exactly what it read before. That is the
opposite of moving the pad, and it is why this needs no container re-layout.

WHAT IT DOES NOT DO. Interior padding - a pad with real text after it - is untouched
and reported. Removing it needs a container re-layout, which is a separate operation
with its own proof. This tool never claims to fix those records.

Every handle site the record carries is rewritten, because a record's length lives in
the handle word and one handle can be carried by more than one site; a half-done edit
is how one message starts reading another.

Usage:
  python -m tools.research.trim_dialogue_padding --image IN.gba --expect-sha256 <hex> \
      --out OUT.gba --manifest OUT.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from tools.webfoot import compressed_dialogue as cd  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402
from tools.webfoot.handles import pack_handle  # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

ROM_BASE = 0x08000000
TABLE_LITERAL = 0x123CC
SPACE = 0x0020


class TrimError(ValueError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_records(image: bytes) -> dict[int, list]:
    table = int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    out: dict[int, list] = {}
    for selector in range(7):
        pointer = int.from_bytes(image[table + selector * 4:table + selector * 4 + 4], "little")
        if pointer < ROM_BASE or pointer - ROM_BASE >= len(image):
            continue
        stream = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)
        out[selector] = list(cd.dialogue_record_inventory(image, selector, len(stream)))
    return out


def trailing_pad(stream: bytes, start: int, length: int) -> int:
    units = stream[start:start + length].decode("utf-16le")
    count = 0
    for character in reversed(units):
        if ord(character) != SPACE:
            break
        count += 1
    return count


def plan(image: bytes) -> tuple[list[dict], list[dict]]:
    """Records whose trailing pad can shrink, and records with interior pad."""
    trims: list[dict] = []
    interior: list[dict] = []
    table = int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE
    for selector, records in read_records(image).items():
        pointer = int.from_bytes(image[table + selector * 4:table + selector * 4 + 4], "little")
        stream = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)
        for record in records:
            start, length = record.handle.decoded_start, record.handle.decoded_length
            pad = trailing_pad(stream, start, length)
            text = stream[start:start + length].decode("utf-16le")
            body = text[:len(text) - pad]
            trimmed_length = length - 2 * pad
            if pad >= 2 and "  " in body:
                interior.append({"key": f"{selector}:{start}:{length}", "pad": pad})
                continue
            if pad >= 2 and trimmed_length >= 2:
                trims.append({
                    "key": f"{selector}:{start}:{length}",
                    "selector": selector,
                    "start": start,
                    "length": length,
                    "pad": pad,
                    "trimmed_length": trimmed_length,
                    "handle": record.handle,
                    "sites": list(record.sites),
                })
    return trims, interior


def apply(image: bytes, trims: list[dict]) -> tuple[bytes, list[dict]]:
    out = bytearray(image)
    changes: list[dict] = []
    for entry in trims:
        new_handle = entry["handle"].replace(decoded_length=entry["trimmed_length"])
        word = new_handle.encode().to_bytes(4, "little")
        for site in entry["sites"]:
            old = bytes(out[site:site + 4])
            if old == word:
                continue
            changes.append({"offset": site, "old": old.hex(), "new": word.hex(),
                            "key": entry["key"],
                            "reason": f"decoded_length {entry['length']} -> "
                                      f"{entry['trimmed_length']}, trailing pad "
                                      f"{entry['pad']} unit(s)"})
            out[site:site + 4] = word
    return bytes(out), changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out")
    parser.add_argument("--manifest")
    parser.add_argument("--report")
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = hashlib.sha256(image).hexdigest()
    if got != args.expect_sha256.lower():
        raise TrimError(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    trims, interior = plan(image)
    report = {
        "input": str(source),
        "input_sha256": got,
        "input_bytes": len(image),
        "trailing_pad_records": len(trims),
        "trailing_pad_units": sum(entry["pad"] for entry in trims),
        "interior_pad_records": len(interior),
        "interior_pad_keys": [entry["key"] for entry in interior],
        "trims": [{key: value for key, value in entry.items() if key != "handle"}
                  for entry in trims],
    }
    print(f"# {source.name}: {len(trims)} record(s) with trailing pad, "
          f"{sum(entry['pad'] for entry in trims)} pad unit(s) to give up")
    print(f"# interior pad with real text after it, NOT touched: {len(interior)} record(s)")

    if not args.out:
        if args.report:
            Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 0

    output, changes = apply(image, trims)
    target = Path(args.out)
    # THE INPUT IS NEVER THE OUTPUT. A run that named its own source would overwrite the
    # verified image it was checked against, so this refuses an alias and stages the write
    # through a temporary path, reading the bytes back before publishing.
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise TrimError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(output)
    if staged.read_bytes() != output:
        raise TrimError(f"REFUSED: the staged write at {staged} does not match the plan")
    staged.replace(target)
    report["output"] = str(target)
    report["output_sha256"] = hashlib.sha256(output).hexdigest()
    report["output_bytes"] = len(output)
    report["changed_word_count"] = len(changes)
    report["changes"] = changes
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"# wrote {target} {len(output)} bytes "
          f"sha256 {report['output_sha256']} ({len(changes)} handle word(s) changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
