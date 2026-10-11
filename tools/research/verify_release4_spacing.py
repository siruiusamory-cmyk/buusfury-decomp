"""Verify the release-4 spacing pass from the two images alone.

INDEPENDENT BY CONSTRUCTION. This file imports no part of the builder and none of
the text-edit engine: it reads the literal, the container table, the payloads and
the handle words with the toolkit's own readers, and re-derives every claim from
the base image and the built image.

WHAT IT PROVES.

0. No record-shaped word outside the event-resource pool changed. That filter is
   near-random outside the pool, so a word there is a coincidence until someone
   proves who reads it, and this pass writes only proven carriers.
1. Every handle word the base carries INSIDE the pool still names a record in the
   built image, in the same container, with the same non-space characters in the
   same order and a length no longer than before.
2. Every interior 2+ space run left in the built image sits where the canonical
   image's record at the same identity carries a 2+ space run at the same unit
   offset. Nothing else survives.
3. Every handle in the pool resolves inside its container's decoded payload.
4. Record containment is preserved: if one base record's span held another's, the
   built spans hold the same way (the covering relations the corpus depends on).
5. Every changed byte lies inside a dialogue container's stored extent or inside
   the event-resource pool. The allowed set comes from the placement contract, NOT
   from the shape filter this file also uses to read records, so sharing that
   filter with the builder cannot hide a write. The Release 4A sites are checked
   directly when the 4A manifest is passed in.
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
from tools.webfoot.data.placement_contracts import CONTRACTS  # noqa: E402
from tools.webfoot.dialogue_repack import container_pointers  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402
from tools.webfoot.handles import unpack_handle  # noqa: E402

SPACE_UNIT = b"\x20\x00"
SPACE = " "
ROM_BASE = 0x08000000

#: The proven handle-site range, read from the placement contract rather than from
#: any shape filter. A word outside it is a coincidence this pass must not write.
_EVENT_RESOURCE = CONTRACTS["buus_fury_usa_rev0_01c1707f"]["event_resource"]
POOL = (_EVENT_RESOURCE["pool_start"] - ROM_BASE, _EVENT_RESOURCE["table"] - ROM_BASE)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def payloads(image: bytes) -> tuple[dict[int, bytes], dict[int, int], dict[int, int]]:
    """(decoded payload, file offset, stored extent) for every selector the table names."""
    decoded: dict[int, bytes] = {}
    offsets: dict[int, int] = {}
    extents: dict[int, int] = {}
    for selector, pointer in sorted(container_pointers(image).items()):
        container = webfoot_lz.unpack(image, pointer - ROM_BASE)
        if not container.declared_size:
            continue
        decoded[selector] = bytes(container.data)
        offsets[selector] = container.offset
        extents[selector] = container.packed_end - container.offset
    return decoded, offsets, extents


def site_records(image: bytes, streams: dict[int, bytes]) -> dict[int, tuple[int, int, int]]:
    """site file offset -> (selector, start, length), for every record word the base carries."""
    found: dict[int, tuple[int, int, int]] = {}
    for selector, stream in streams.items():
        for record in cd.dialogue_record_inventory(image, selector, len(stream)):
            for site in record.sites:
                found[site] = (selector, record.handle.decoded_start,
                               record.handle.decoded_length)
    return found


def text_of(stream: bytes, start: int, length: int) -> str:
    return stream[start:start + length].decode("utf-16le")


def interior_runs(text: str) -> list[tuple[int, int]]:
    out = []
    position = 0
    while position < len(text):
        if text[position] != SPACE:
            position += 1
            continue
        end = position
        while end < len(text) and text[end] == SPACE:
            end += 1
        if end - position >= 2 and position != 0 and end != len(text):
            out.append((position, end - position))
        position = end
    return out


def align(base_text: str, built_text: str) -> tuple[dict[int, int], bool]:
    """built index -> base index, and whether every skipped base character was a space."""
    mapping: dict[int, int] = {}
    cursor = 0
    for index, character in enumerate(built_text):
        while cursor < len(base_text) and base_text[cursor] != character:
            if base_text[cursor] != SPACE:
                return {}, False
            cursor += 1
        if cursor >= len(base_text):
            return {}, False
        mapping[index] = cursor
        cursor += 1
    for rest in range(cursor, len(base_text)):
        if base_text[rest] != SPACE:
            return {}, False
    return mapping, True


def retail_predicate(base_streams, canonical_streams, base_records, selector, position) -> bool:
    """Whether the canonical image carries a 2+ run where the base has one at `position`."""
    other = canonical_streams.get(selector, b"")
    for key, record in base_records.items():
        if not record.start <= position < record.start + record.length:
            continue
        if record.start + record.length > len(other):
            continue
        offset = record.start + (position - record.start)
        if other[offset:offset + 2] == SPACE_UNIT and other[offset + 2:offset + 4] == SPACE_UNIT:
            return True
    return False


class Record:
    __slots__ = ("start", "length", "site")

    def __init__(self, start: int, length: int, site: int) -> None:
        self.start = start
        self.length = length
        self.site = site


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--canonical", required=True)
    parser.add_argument("--release4-manifest")
    args = parser.parse_args()

    base = Path(args.base).read_bytes()
    built = Path(args.out).read_bytes()
    canonical = Path(args.canonical).read_bytes()
    problems: list[str] = []
    notes: list[str] = []

    digest = sha256_bytes(built)
    if digest != args.expect_sha256.lower():
        problems.append(f"the built image is {digest}, expected {args.expect_sha256.lower()}")

    base_streams, base_offsets, base_extents = payloads(base)
    built_streams, _built_offsets, _built_extents = payloads(built)
    canonical_streams, _canonical_offsets, _canonical_extents = payloads(canonical)
    base_sites = site_records(base, base_streams)
    built_sites = site_records(built, built_streams)

    in_pool = {site: record for site, record in base_sites.items() if POOL[0] <= site < POOL[1]}
    outside = {site: record for site, record in base_sites.items() if not POOL[0] <= site < POOL[1]}
    built_pool = {site for site in built_sites if POOL[0] <= site < POOL[1]}
    notes.append(f"record words inside the event-resource pool {POOL[0]:#x}..{POOL[1]:#x}: "
                 f"base {len(in_pool)}, built {len(built_pool)}; outside it {len(outside)}")
    if set(in_pool) != built_pool:
        problems.append(f"the in-pool record-word sites differ: "
                        f"{len(set(in_pool) ^ built_pool)} site(s) gained or lost")

    # A shrunken payload can move an out-of-pool coincidence span out of range, so
    # the outside set may drift. Those words are not references, and their bytes
    # must not move.
    drifted = sorted(site for site in set(base_sites) ^ set(built_sites)
                     if not POOL[0] <= site < POOL[1])
    notes.append(f"out-of-pool record-shaped words that appeared or vanished: {len(drifted)}")
    for site in drifted:
        if base[site:site + 4] != built[site:site + 4]:
            problems.append(f"site {site:#06x} is outside the pool, appeared or vanished, and its "
                            f"word changed: {base[site:site + 4].hex()} -> "
                            f"{built[site:site + 4].hex()}")

    # 0. a word outside the pool is a shape coincidence until someone proves who
    #    reads it, so the pass must leave it alone. This is the check the shipped
    #    candidate failed: it rewrote 155 of them, 142 in code and graphics.
    touched = [site for site in outside if base[site:site + 4] != built[site:site + 4]]
    notes.append(f"out-of-pool record-shaped words left byte-identical: "
                 f"{len(outside) - len(touched)} of {len(outside)}")
    for site in touched[:20]:
        problems.append(f"site {site:#06x} is outside the event-resource pool and was rewritten: "
                        f"{base[site:site + 4].hex()} -> {built[site:site + 4].hex()}")

    # 1. every base site INSIDE the pool resolves, same selector, non-space characters unchanged
    checked = 0
    deleted_units = 0
    for site, (selector, start, length) in in_pool.items():
        built_handle = built_sites.get(site)
        if built_handle is None:
            continue
        selector_now, start_now, length_now = built_handle
        if selector_now != selector:
            problems.append(f"site {site:#06x} moved from selector {selector} to {selector_now}")
            continue
        if length_now > length:
            problems.append(f"site {site:#06x} grew from {length} to {length_now} bytes")
        built_text = text_of(built_streams[selector_now], start_now, length_now)
        base_text = text_of(base_streams[selector], start, length)
        mapping, clean = align(base_text, built_text)
        if not clean:
            problems.append(f"site {site:#06x} lost or reordered a non-space character: "
                            f"{base_text[:40]!r} -> {built_text[:40]!r}")
            continue
        checked += 1
        deleted_units += length // 2 - length_now // 2

        # 2. every interior run left in this record must be a retail run
        for offset, count in interior_runs(built_text):
            base_offset = mapping[offset]
            position = start + base_offset * 2
            if not retail_predicate(base_streams, canonical_streams,
                                    base_records(in_pool, base_streams, selector),
                                    selector, position):
                problems.append(f"site {site:#06x} ({selector}:{start_now}:{length_now}) keeps an "
                                f"interior run at unit {offset} that canonical does not carry: "
                                f"{built_text[max(0, offset-16):offset+count+16]!r}")
    notes.append(f"records checked through their own handle word: {checked}")
    notes.append(f"space units removed across them: {deleted_units}")

    # 3. every handle word in the pool resolves inside its payload
    for site in in_pool:
        selector, start, length = built_sites[site]
        stream = built_streams.get(selector)
        if stream is None:
            problems.append(f"site {site:#06x} names selector {selector}, which carries no payload")
            continue
        if start + length > len(stream):
            problems.append(f"site {site:#06x} names {start}:{length} of selector {selector}, "
                            f"past its {len(stream)}-byte payload")

    # 4. containment preserved
    preserved, broken = containment(in_pool, built_sites)
    notes.append(f"containment pairs checked: {preserved}")
    if broken:
        problems.append(f"{broken} containment pair(s) no longer hold")

    # 5. every changed byte is inside a container extent or the event-resource pool.
    #    The allowed set is the CONTRACT's pool range, NOT the site list this file
    #    read with the shape filter: sharing that filter with the builder is the
    #    common-mode failure this check exists to break.
    allowed = set()
    for selector, extent in base_extents.items():
        for at in range(base_offsets[selector], base_offsets[selector] + extent):
            allowed.add(at)
    for at in range(POOL[0], POOL[1]):
        allowed.add(at)
    changed = [at for at in range(min(len(base), len(built))) if base[at] != built[at]]
    stray = [at for at in changed if at not in allowed]
    in_pool_changed = [at for at in changed if POOL[0] <= at < POOL[1]]
    notes.append(f"changed bytes: {len(changed)}, of them inside the event pool "
                 f"{len(in_pool_changed)}")
    if stray:
        problems.append(f"{len(stray)} changed byte(s) outside the dialogue containers and the "
                        f"event-resource pool, first at {stray[0]:#x}")

    # 6. Release 4A content, when its manifest is supplied
    if args.release4_manifest:
        document = json.loads(Path(args.release4_manifest).read_text(encoding="utf-8"))
        ranges: list[tuple[int, int]] = []
        for entry in document.get("changed_ranges", []):
            pairs = entry.get("value", entry) if isinstance(entry, dict) else entry
            ranges.append((int(pairs[0]), int(pairs[1])))
        for key in ("sites", "appearances"):
            for entry in document.get(key, []):
                ranges.append((int(entry["file"]), int(entry["file"])))
        edit = document.get("name_slot_edit")
        if edit:
            ranges.append((int(edit["file"]), int(edit["file"]) + int(edit["bytes"]) - 1))
        for copy in document.get("definition_copies", {}).values():
            start = int(copy["copy_file"])
            ranges.append((start, start + int(copy["copy_bytes"]) - 1))
            ranges.append((int(copy["entry_file"]), int(copy["entry_file"]) + 3))
        touched = []
        for start, end in ranges:
            for at in range(start, end + 1):
                if base[at] != built[at]:
                    touched.append(at)
        notes.append(f"Release 4A sites checked: {len(ranges)} range(s)")
        if touched:
            problems.append(f"Release 4A content changed at {len(touched)} byte(s), "
                            f"first {touched[0]:#x}")
        else:
            notes.append("Release 4A stat selectors, appearances, name slot and definition "
                         "copies are byte-identical")

    for note in notes:
        print(f"  {note}")
    if problems:
        print(f"VERIFY FAIL: {len(problems)} problem(s)")
        for problem in problems[:20]:
            print(f"  {problem}")
        return 1
    print(f"VERIFY PASS: {digest}")
    return 0


def base_records(base_sites, base_streams, selector):
    out = {}
    for site, (record_selector, start, length) in base_sites.items():
        if record_selector == selector:
            out[site] = Record(start, length, site)
    return out


def containment(base_sites, built_sites) -> tuple[int, int]:
    """Every base span that contained another must contain it in the built image too."""
    spans: dict[int, list[tuple[int, int, int]]] = {}
    for site, (selector, start, length) in base_sites.items():
        spans.setdefault(selector, []).append((start, start + length, site))
    built_span = {site: (start, start + length) for site, (_s, start, length) in built_sites.items()}
    checked = broken = 0
    for selector, rows in spans.items():
        rows.sort()
        for index, (start, end, site) in enumerate(rows):
            for other_start, other_end, other_site in rows[:index]:
                if other_end < end or (other_start, other_end) == (start, end):
                    continue
                if site not in built_span or other_site not in built_span:
                    continue
                checked += 1
                outer = built_span[other_site]
                inner = built_span[site]
                if not (outer[0] <= inner[0] and inner[1] <= outer[1]):
                    broken += 1
    return checked, broken


if __name__ == "__main__":
    sys.exit(main())
