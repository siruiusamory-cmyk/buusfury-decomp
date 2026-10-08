"""Apply dialogue renames to an image without changing one encoded length.

WHY THIS SHAPE. A retail container is ONE packed stream whose record spans
overlap, and the engine copies a record out by its handle's decoded length. The
v3 rename line measured what that means: a record whose decoded byte length
differs from retail hangs the Kibito cutscene, while a record whose bytes merely
move is harmless (the position control survived). So the safe operation is a
replacement that lands on **exactly** the retail unit count, leaving the rebuilt
stream the same length and every offset where retail had it.

WHAT THE TOKENS ARE FOR. A rename usually grows, and padding cannot shrink a
growth. An expansion token replaces two or more stored units with one, so
``encode_to_length`` can spend exactly as many expansions as the record grew by
and land on the retail count with the longer text intact. Records that shrink are
padded with spaces, which is what the shipping 236-rename build already does.

THE RECORD SET IS AN ARGUMENT, NOT A CONSTANT. The map this reads is the private
v3 rename map. It carries dialogue text derived from a proprietary image, so it is
deliberately not tracked and the path is passed in; the tool refuses a map that
does not have the shape it expects rather than guessing.

Nothing here writes to a base image: the derivative is staged and published, and
the base's digest is checked before and after.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import struct
import sys
import tempfile
from pathlib import Path

from tools.webfoot import compressed_dialogue as cd
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.token_dictionary import TokenDictionary, encode_to_length
from tools.webfoot.write import WriteError, ensure_not_source_alias

ROM_BASE = 0x08000000
#: The one word in the image that names the container-pointer table. Measured:
#: exactly one reference, so repointing it is the whole relocation.
TABLE_LITERAL = 0x123CC
#: The table's retail file offset, and how many slots the tool carries forward.
#: The engine indexes by selector with no bounds check, so every slot the retail
#: table had must keep its bytes.
RETAIL_TABLE = 0x7B5B64
TABLE_SLOTS = 64


class SpliceError(ValueError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_map(path: Path) -> dict[str, dict]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not document:
        raise SpliceError("the rename map is not a non-empty object")
    for key, row in document.items():
        if not isinstance(row, dict):
            raise SpliceError(f"{key}: not an object")
        for field in ("old_selector", "old_start", "old_length", "new_text"):
            if field not in row:
                raise SpliceError(f"{key}: no {field}")
        if not isinstance(row["new_text"], str) or not row["new_text"]:
            raise SpliceError(f"{key}: new_text is not a non-empty string")
        if row["old_length"] % 2:
            raise SpliceError(f"{key}: old_length {row['old_length']} is not even")
    return document


def substitution_table(rows: dict[str, dict]) -> dict[str, str]:
    """The word-level substitutions the map performs, taken from the map itself.

    Derived rather than copied from a list, because a list can drift from the data
    it is supposed to describe. Every old side must map to exactly ONE new side: a
    word that two records rename differently means the map is not one consistent
    substitution, and no build can satisfy both.
    """
    seen: dict[str, set[str]] = {}
    for row in rows.values():
        old_words = row["old_text"].split(" ")
        new_words = row["new_text"].split(" ")
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
                None, old_words, new_words, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            seen.setdefault(" ".join(old_words[i1:i2]), set()).add(
                " ".join(new_words[j1:j2]))
    table: dict[str, str] = {}
    for old_side, variants in seen.items():
        if len(variants) != 1:
            raise SpliceError(
                f"the map renames {old_side!r} to {sorted(variants)}; a build can "
                f"only apply one of them"
            )
        table[old_side] = variants.pop()
    return table


def local_replacement(old_side: str, new_side: str,
                      dictionary: TokenDictionary) -> str:
    """`new_side` occupying exactly as many units as `old_side` did.

    Growth is paid for by tokenising INSIDE the new name, so the replacement costs
    the same as what it replaces and nothing after it moves. A shrink is paid for
    with spaces immediately after the name, which keeps every later character where
    retail put it. Paying at the END of the record instead - the obvious thing, and
    what the first version did - keeps the record's total length but slides every
    character after the substitution, and any other record reading those bytes then
    displays shifted text.
    """
    delta = len(new_side) - len(old_side)
    if delta == 0:
        return new_side
    if delta < 0:
        return new_side + " " * -delta
    encoded = encode_to_length(new_side, dictionary, len(old_side))
    if len(encoded) != len(old_side):
        # encode_to_length refuses an unreachable target; this is the belt to that
        # brace, because a wrong count here is exactly the bleed this file exists to
        # prevent.
        raise SpliceError(
            f"{new_side!r} cannot be written in {len(old_side)} units (it needs "
            f"{len(new_side)})"
        )
    return encoded


def substitution_regions(old_text: str, new_text: str, dictionary: TokenDictionary,
                         table: dict[str, str]) -> list[tuple[int, int, str]]:
    """Every substitution as ``(start, length, replacement)`` in UNIT positions.

    This is the whole rename, stated as positions rather than as text: the regions
    say which characters may differ and what they become, and by construction
    everything outside them is copied verbatim. The verifier reads the same regions
    back out of the finished image, which is why they are a function and not a loop
    inside the writer.
    """
    old_words = old_text.split(" ")
    new_words = new_text.split(" ")
    offsets: list[int] = []
    position = 0
    for word in old_words:
        offsets.append(position)
        position += len(word) + 1
    regions: list[tuple[int, int, str]] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, old_words, new_words, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        old_side = " ".join(old_words[i1:i2])
        new_side = " ".join(new_words[j1:j2])
        if table.get(old_side) != new_side:
            raise SpliceError(
                f"{old_side!r} -> {new_side!r} is not the substitution the map's "
                f"other records perform"
            )
        start = offsets[i1]
        length = offsets[i2 - 1] + len(old_words[i2 - 1]) - start
        regions.append((start, length, local_replacement(old_side, new_side, dictionary)))
    return regions


def encode_record(row: dict, dictionary: TokenDictionary,
                  table: dict[str, str]) -> tuple[str, str]:
    """The stored text whose every prefix is the length retail had.

    Only the substitution regions move: everything the table does not name is copied
    character for character, so the result is the retail text with names changed.
    """
    regions = substitution_regions(row["old_text"], row["new_text"], dictionary, table)
    text = row["old_text"]
    for start, length, replacement in sorted(regions, reverse=True):
        text = text[:start] + replacement + text[start + length:]
    if len(text) != len(row["old_text"]):
        raise SpliceError(
            f"the replacement is {len(text)} units where retail had "
            f"{len(row['old_text'])}; that difference is what moves other records"
        )
    kinds = []
    for _, length, replacement in regions:
        if len(replacement) > length:
            kinds.append("padded")
        elif replacement != row["new_text"][:len(replacement)]:
            kinds.append("tokenised")
        else:
            kinds.append("exact")
    return text, "+".join(sorted(set(kinds))) or "none"


def find_text(image: bytes, needle: str) -> list[dict]:
    """Every record whose stored text contains `needle`, for a diagnostic plant."""
    hits: list[dict] = []
    table = RETAIL_TABLE
    for selector in range(TABLE_SLOTS):
        pointer = struct.unpack_from("<I", image, table + selector * 4)[0]
        if pointer == 0 or pointer < ROM_BASE:
            continue
        try:
            container = webfoot_lz.unpack(image, pointer - ROM_BASE)
        except Exception:                                     # noqa: BLE001
            continue
        stream = bytes(container.data)
        for record in cd.dialogue_record_inventory(image, selector, len(stream)):
            # decoded_start and decoded_length are BYTE offsets into the decoded
            # container (tools/webfoot/handles.py: the bit fields count halfwords
            # and unpack_handle multiplies by two). Reading them as units doubles
            # the span and finds a different record that happens to overlap.
            span = stream[record.handle.decoded_start:record.handle.decoded_end]
            try:
                text = span.decode("utf-16le")
            except UnicodeDecodeError:
                continue
            if needle in text:
                hits.append({"selector": selector,
                             "decoded_start": record.handle.decoded_start,
                             "decoded_length": record.handle.decoded_length,
                             "text": text})
    return hits


def splice(base: Path, destination: Path, base_sha256: str, rows: dict[str, dict],
           dictionary: TokenDictionary) -> dict[str, object]:
    try:
        ensure_not_source_alias(base, destination)
    except WriteError as exc:
        raise SystemExit(str(exc)) from exc
    if sha256(base) != base_sha256:
        raise SystemExit(
            f"the base is not the declared image: {sha256(base)} != {base_sha256}"
        )
    original = base.read_bytes()
    image = bytearray(original)

    literal_offset = TABLE_LITERAL
    table_address = struct.unpack_from("<I", original, literal_offset)[0]
    if table_address < ROM_BASE:
        raise SystemExit(f"the table literal at {literal_offset:#x} is not a ROM pointer")

    # 1. the substitution table, then every record encoded to a text whose every
    #    prefix is the length retail had.
    table = substitution_table(rows)
    edits: dict[int, list[tuple[int, int, bytes, str, str]]] = {}
    how: dict[str, str] = {}
    for key in sorted(rows):
        row = rows[key]
        text, method = encode_record(row, dictionary, table)
        how[key] = method
        edits.setdefault(row["old_selector"], []).append(
            (row["old_start"], row["old_length"], text.encode("utf-16le"), key, method)
        )

    placements: dict[int, int] = {}
    report: dict[str, object] = {"selectors": {}, "records": len(rows)}
    table = bytearray(TABLE_SLOTS * 4)
    for index in range(TABLE_SLOTS):
        source = RETAIL_TABLE + index * 4
        table[index * 4:index * 4 + 4] = original[source:source + 4]

    for selector in sorted(edits):
        pointer = struct.unpack_from("<I", image, RETAIL_TABLE + selector * 4)[0]
        stream = bytearray(webfoot_lz.unpack(original, pointer - ROM_BASE).data)
        stream_length = len(stream)
        retail_stream = bytes(stream)
        # A refused rewrite is reverted from the retail bytes, which is exact because
        # two accepted rewrites never overlap.

        # Every prefix of every replacement is the length retail had, so this loop
        # needs no overlap policy: two records that share bytes are writing the same
        # substituted characters there, and the second write is the same bytes as the
        # first. A span that holds neither its retail bytes nor this record's
        # replacement is the one case that cannot be reasoned about, and it is
        # refused rather than written over.
        #
        # The check that this holds across the whole container is not here; it is
        # tools/research/verify_token_splice.py, which reads every record back out of
        # the finished image and compares its visible text with the substitution
        # applied to its retail text. Reading the result is the only way to know.
        conflicts: dict[str, str] = {}
        applied = 0
        for start, old_length, new_bytes, key, _ in sorted(edits[selector], reverse=True):
            if start + old_length > len(stream):
                raise SystemExit(f"{key}: span {start}+{old_length} runs past the stream")
            retail_text = retail_stream[start:start + old_length].decode("utf-16le", "replace")
            if retail_text != rows[key]["old_text"]:
                raise SystemExit(
                    f"{key}: the image's bytes at this span are not old_text, so this "
                    f"map describes a different build"
                )
            current = bytes(stream[start:start + old_length])
            if current not in (retail_stream[start:start + old_length], new_bytes):
                conflicts[key] = "another record's rewrite disagrees at these bytes"
                continue
            stream[start:start + old_length] = new_bytes
            applied += 1

        if len(stream) != stream_length:
            raise SystemExit(
                f"selector {selector}: the rebuilt stream changed length "
                f"({stream_length} -> {len(stream)}); every replacement must be "
                f"prefix-preserving"
            )
        while len(image) % 4:
            image.append(0)
        placements[selector] = ROM_BASE + len(image)
        image += webfoot_lz.build_stored(bytes(stream))
        report["selectors"][str(selector)] = {
            "records": applied, "decoded_bytes": len(stream),
            "rom_address": f"0x{placements[selector]:08X}",
        }
        if conflicts:
            report["refused"] = {**report.get("refused", {}), **conflicts}
            print(f"  selector {selector}: {len(conflicts)} record(s) refused:")
            for key, why in sorted(conflicts.items()):
                print(f"    {key}: {why}")

    # 2. point the relocated table at the rebuilt containers and repoint the literal.
    for selector, address in placements.items():
        struct.pack_into("<I", table, selector * 4, address)
    while len(image) % 4:
        image.append(0)
    table_offset = len(image)
    image += table
    struct.pack_into("<I", image, literal_offset, ROM_BASE + table_offset)

    report["bytes"] = len(image)
    report["applied"] = sum(row["records"] for row in report["selectors"].values())
    report["methods"] = {
        "padded": sum(1 for value in how.values() if value == "padded"),
        "exact": sum(1 for value in how.values() if value == "exact"),
        "tokenised": sum(1 for value in how.values() if value.startswith("tokenised")),
    }

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent,
                                     prefix=destination.name + ".",
                                     suffix=".partial", delete=False) as handle:
        handle.write(bytes(image))
        staged = Path(handle.name)
    staged.replace(destination)
    if sha256(base) != base_sha256:
        raise SystemExit("the base image changed during the build")
    report["sha256"] = sha256(destination)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--base-sha256", required=True)
    parser.add_argument("--map", help="the rename map; required unless --find is used")
    parser.add_argument("--tokens", nargs="*", default=[],
                        help="the dictionary's expansions, in id order")
    parser.add_argument("--out")
    parser.add_argument("--report")
    parser.add_argument("--find", help="print records whose text contains this, then stop")
    args = parser.parse_args()

    base = Path(args.base)
    if args.find:
        image = base.read_bytes()
        if sha256(base) != args.base_sha256.lower():
            raise SystemExit("the base is not the declared image")
        for hit in find_text(image, args.find):
            print(f"selector {hit['selector']}  start {hit['decoded_start']}  "
                  f"length {hit['decoded_length']}  {hit['text']!r}")
        return 0

    if not args.map or not args.out:
        raise SystemExit("--map and --out are required")
    dictionary = TokenDictionary(tuple(args.tokens))
    report = splice(base, Path(args.out), args.base_sha256.lower(),
                    load_map(Path(args.map)), dictionary)
    print(f"derivative     : {args.out}")
    print(f"derivative sha : {report['sha256']}")
    print(f"size           : {report['bytes']} bytes")
    print(f"records        : {report['records']} encoded, {report['applied']} applied  "
          f"padded {report['methods']['padded']}  exact {report['methods']['exact']}  "
          f"tokenised {report['methods']['tokenised']}")
    if report.get("refused"):
        print(f"refused        : {len(report['refused'])} record(s), each with its reason")
    for selector, row in sorted(report["selectors"].items(), key=lambda item: int(item[0])):
        print(f"  selector {selector}: {row['records']} record(s) rebuilt, "
              f"{row['decoded_bytes']} decoded bytes at {row['rom_address']}")
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
