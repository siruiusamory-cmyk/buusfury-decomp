"""Rebuild a friend image's stored dialogue containers without the rename padding.

WHY A WHOLE-CONTAINER REBUILD, AND WHAT THE UNIT IS. A retail container is one decoded
stream whose record spans OVERLAP: 1,102 of 2,814 records share bytes with another. A
record's text is read by its handle's decoded length, so a shorter text cannot occupy
the same span unless the characters after it move - and moving them changes what every
overlapping record reads. The unit that can be rewritten safely is therefore not a
record but a CHAIN:

    the maximal runs of the decoded stream that no record boundary cuts.

Every record's span is a union of whole chains, and each chain's entire content is
witnessed by the same set of records, so a chain can be rewritten only if the longest
record covering its tail agrees on the content. Trimming is decided per chain by the
FURTHEST read, never per record: a chain's tail may be dropped only when no record reads
that far, which is exactly the set of units whose only readers are shorter records that
never needed them.

WHAT IT DOES NOT DO. It never inserts, deletes or reorders a byte it was not entitled
to. Chains keep their order, so every record's span remains contiguous and its text is
the concatenation of the chains it covered. If the rebuilt stream does not fit the
container's existing decoded size the rebuild is REFUSED with the overrun, because
naming a new home for a container is an allocation decision with its own evidence.

Every handle site is rewritten, because a length lives in the handle word and one handle
can be carried by several sites.

Usage:
  python -m tools.webfoot.dialogue_repack --image IN.gba --expect-sha256 <hex> \
      --out OUT.gba --manifest OUT.json [--selector N ...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from tools.webfoot import compressed_dialogue as cd
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.handles import HANDLE_START_MAX_BYTES, pack_handle

ROM_BASE = 0x08000000
TABLE_LITERAL = 0x123CC
CONTAINER_HEADER = 8
SPACE = 0x0020
#: How many characters the walk may fail to match before its result is not an alignment.
#: A name substitution is a short run of differing characters; a drifted cursor differs
#: for the rest of the record, so the two are far apart and this limit sits between them.
BLIND_LIMIT = 12
SELECTOR_SLOTS = 64


class RepackError(ValueError):
    """The rebuild refused rather than writing an unproven byte."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def live_table(image: bytes) -> int:
    """The container table's file offset, named by the image's own literal."""
    return int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE


def container_pointers(image: bytes) -> dict[int, int]:
    table = live_table(image)
    out: dict[int, int] = {}
    for selector in range(SELECTOR_SLOTS):
        slot = table + selector * 4
        if slot + 4 > len(image):
            break
        pointer = int.from_bytes(image[slot:slot + 4], "little")
        if ROM_BASE <= pointer < ROM_BASE + len(image):
            out[selector] = pointer
    return out


def chains_of(records) -> list[tuple[int, int]]:
    """Maximal spans that no record boundary cuts, in stream order."""
    edges = sorted({edge for record in records
                    for edge in (record.handle.decoded_start, record.handle.decoded_end)})
    return [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]


def text_of(stream: bytes, start: int, length: int) -> str:
    return stream[start:start + length].decode("utf-16le")


def normalised(text: str) -> str:
    """Whitespace-insensitive form, for comparing a rebuilt view with its intent.

    A pad the rebuild drops may sit INSIDE a record's own span (a shorter record's name
    was paid for at a unit position a longer record also covers), so the rebuilt view can
    legitimately lose interior spaces. What must not change is the words, the punctuation
    and every control unit, and this comparison is what states that.
    """
    return " ".join(part for part in text.split(" ") if part)


def plan_container(image: bytes, selector: int, stream: bytes, records):
    """The rebuilt stream, the chains, and every record's new span.

    Returns a dict with the rebuilt bytes, the chain table, and per-record new spans.
    """
    chains = chains_of(records)
    if not chains:
        raise RepackError(f"selector {selector}: no record spans, nothing to rebuild")

    def read(offset: int) -> int:
        return stream[offset] | (stream[offset + 1] << 8)

    # The furthest end any record reads at each unit position. A chain's tail unit may
    # only be dropped when nothing reads past it, which is what makes the drop invisible
    # to every overlapping record: a unit whose furthest reader ends exactly there is
    # read by nobody who asked for what follows it.
    furthest_end: dict[int, int] = {}
    for record in records:
        for position in range(record.handle.decoded_start, record.handle.decoded_end, 2):
            end = record.handle.decoded_end
            if end > furthest_end.get(position, 0):
                furthest_end[position] = end

    blocks: list[dict] = []
    new_offset = 0
    for start, end in chains:
        readers = [record for record in records
                   if record.handle.decoded_start <= start
                   and end <= record.handle.decoded_end]
        # Every unit at or below reach_bound is inside a record that reads past it, so a
        # unit there can never be dropped whatever it holds. Above it, a trailing pad is
        # read by nobody: the only records covering it end inside or at reach_bound.
        reach_bound = max((record.handle.decoded_end for record in records
                           if record.handle.decoded_end > start
                           and record.handle.decoded_start <= start), default=start)
        keep = end - start
        offset = end - 2
        while (offset >= start and offset >= reach_bound and read(offset) == SPACE
               and furthest_end.get(offset) == offset + 2):
            keep -= 2
            offset -= 2
        units = list(struct.unpack_from(f"<{keep // 2}H", stream, start))
        blocks.append({
            "start": start,
            "end": end,
            "new_offset": new_offset,
            "new_length": keep,
            "units": units,
            "readers": len(readers),
            "reach_bound": reach_bound,
        })
        new_offset += keep

    rebuilt = bytearray()
    for block in blocks:
        rebuilt += struct.pack(f"<{len(block['units'])}H", *block["units"])
    if len(rebuilt) > len(stream):
        raise RepackError(
            f"selector {selector}: the rebuilt stream is {len(rebuilt)} bytes but the "
            f"container decodes to {len(stream)}; naming a new home for a container is an "
            f"allocation decision, not something this rebuild may assume"
        )
    rebuilt += bytes(SPACE.to_bytes(2, "little")) * ((len(stream) - len(rebuilt)) // 2)

    def block_for(offset: int) -> dict | None:
        for block in blocks:
            if block["start"] <= offset < block["end"]:
                return block
        return None

    spans: list[dict] = []
    for record in records:
        start, end = record.handle.decoded_start, record.handle.decoded_end
        first = block_for(start)
        last = block_for(end - 2)
        if first is None or last is None:
            raise RepackError(f"selector {selector}: record 0x{start:X}..0x{end:X} "
                              "does not start and end inside a chain")
        new_start = first["new_offset"] + (start - first["start"])
        new_end = last["new_offset"] + (end - last["start"])
        # The units the record reads must equal the units the chains hold for it.
        original = text_of(stream, start, end - start)
        got = bytes(rebuilt[new_start:new_end]).decode("utf-16le", "replace")
        if normalised(got) != normalised(original):
            raise RepackError(
                f"selector {selector}: record 0x{start:X}..0x{end:X} would read "
                f"{got[:60]!r} after the rebuild, not {original[:60]!r}"
            )
        spans.append({
            "record": f"{selector}:{start}:{end - start}",
            "new_start": new_start,
            "new_length": new_end - new_start,
            "new_key": f"{selector}:{new_start}:{new_end - new_start}",
            "handle": record.handle,
            "sites": list(record.sites),
            "spaces_dropped": original.count(" ") - got.count(" "),
            "target": got,
        })
    return {"rebuilt": bytes(rebuilt), "blocks": blocks, "spans": spans,
            "stream_length": len(stream)}


def target_text(original: str, retail: str | None) -> str:
    """The record's text with the rename's pad runs reduced to one space.

    WHY THIS IS NOT A POSITION-BY-POSITION COMPARISON. The pad exists so that every
    character AFTER the substituted name keeps the position retail gave it, which means
    the text between the name and the rest of the line is what moved - at the pad's own
    index the two images hold different characters by construction. A positional test
    therefore never sees a pad: at `#Get him, Uub![4]You` the retail string has `Trunks!`
    running through that index and reads no space at all.

    The test that does work compares what FOLLOWS the run. A playtest run of two or more
    spaces is the pad when the text right after it is the text right after retail's own
    run at the same index; then the run is reduced to one, and where retail had a longer
    run the run is retail's own spacing and is copied unchanged. Nothing else is touched.

    `retail` may be None, and then the text is returned unchanged: with no baseline there
    is no evidence that any run is a pad.
    """
    if retail is None:
        return original
    out: list[str] = []
    index = 0
    blind = 0
    while index < len(original):
        if original[index] != " ":
            if index >= len(retail) or retail[index] != original[index]:
                blind += 1
            out.append(original[index])
            index += 1
            continue
        run = 0
        while index + run < len(original) and original[index + run] == " ":
            run += 1
        end = index + run
        head = 0
        while index + head < len(retail) and retail[index + head] == " ":
            head += 1
        tail = 0
        while end - 1 - tail >= 0 and retail[end - 1 - tail:end - tail] == " ":
            tail += 1
        # THE TAIL IS WHAT ALIGNS, NOT THE HEAD. The pad exists so that every character
        # after the substituted name keeps retail's position, so the run's first unit
        # lands ON retail's longer name and the run's last unit lands on retail's single
        # space after it. Measured over selectors 0-5: all 302 pad runs read retail run 0
        # at the head and 1 at the tail, and all 31 of retail's own 2+ runs read 2 at
        # both. So a tail of exactly one space is the pad's signature, and where retail
        # has a run of its own the larger of the two ends is what retail displayed.
        out.append(" " * (max(head, tail) or run))
        index = end
    # Second guard, for a pad the two-end test cannot see: a walk that had to guess past
    # this many characters is not an alignment, so its result is discarded.
    if blind > BLIND_LIMIT:
        return original
    return "".join(out)


def reference_text(stream: bytes | None, record) -> str | None:
    """The retail text at the same decoded span, or None when there is no retail image."""
    if stream is None:
        return None
    start, end = record.handle.decoded_start, record.handle.decoded_end
    if end > len(stream):
        return None
    return stream[start:end].decode("utf-16le")


def verify_plan(selector: int, stream: bytes, records, plan: dict) -> list[str]:
    """Every record must read, in the rebuilt stream, exactly its target text.

    This is the check the writer's own intent cannot satisfy: the target text is derived
    from the record's ORIGINAL text plus the retail reference, and the rebuilt bytes are
    read back independently, so an off-by-one in a span, a mis-ordered block or a shared
    byte would appear here as a mismatch.
    """
    problems: list[str] = []
    spans = {span["record"]: span for span in plan["spans"]}
    for record in records:
        start, end = record.handle.decoded_start, record.handle.decoded_end
        key = f"{selector}:{start}:{end - start}"
        span = spans.get(key)
        if span is None:
            problems.append(f"{key}: no span in the plan")
            continue
        got = plan["rebuilt"][span["new_start"]:span["new_start"] + span["new_length"]]
        if len(got) != span["new_length"]:
            problems.append(f"{key}: the rebuilt stream is too short for this span")
            continue
        text = bytes(got).decode("utf-16le")
        # The plan does not recompute the target here: the plan RECORDS the text it meant
        # to place, and this reads the rebuilt bytes back. Two different predicates would
        # only prove they disagree.
        want = span["target"]
        if text != want:
            problems.append(f"{key}: rebuilt text {text[:48]!r} != expected {want[:48]!r}")
    return problems


def plan_selective(selector: int, stream: bytes, records, reference: bytes | None) -> dict:
    """Duplicate the least that a pad repair requires, and share everything else.

    A chain whose units carry a pad a shorter record would drop cannot stay where it is:
    the pad is inside bytes a longer record also reads. The repair therefore copies that
    chain - and then every record that reads it must stop straddling a shared byte and a
    private one, so its OWN chains must be copied too, which pulls in their readers, and
    so on. The set is the closure of the pad chains under "a reader of a copied chain is
    copied". Everything outside the closure keeps its original offsets, so only the
    closure is laid out fresh and the stream grows by the closure's readers, not by the
    whole container.

    This is the layout the handle's 15-bit start field forces: a container may not exceed
    65,534 bytes, so copying every record is not available.
    """
    chains = chains_of(records)
    chain_readers = {chain: [record for record in records
                             if record.handle.decoded_start <= chain[0]
                             and chain[1] <= record.handle.decoded_end]
                     for chain in chains}
    chain_of_offset = {}
    for chain in chains:
        for offset in range(chain[0], chain[1], 2):
            chain_of_offset[offset] = chain

    def has_surplus(record) -> bool:
        start, end = record.handle.decoded_start, record.handle.decoded_end
        text = text_of(stream, start, end - start)
        return text != target_text(text, reference_text(reference, record)).rstrip(" ")

    copied: set[tuple[int, int]] = set()
    for chain in chains:
        for record in chain_readers[chain]:
            if has_surplus(record):
                copied.add(chain)
                break
    changed = True
    while changed:
        changed = False
        for chain in list(copied):
            for record in chain_readers[chain]:
                for offset in range(record.handle.decoded_start,
                                    record.handle.decoded_end, 2):
                    owner = chain_of_offset.get(offset)
                    if owner is not None and owner not in copied:
                        copied.add(owner)
                        changed = True

    if not copied:
        return {"rebuilt": stream, "blocks": [], "spans": [], "stream_length": len(stream),
                "reference": reference, "copied_chains": 0, "copied_bytes": 0}

    # A RECORD MUST BE COPIED AS A WHOLE RUN, NOT AS LOOSE CHAINS. If a record covers
    # chains A, B and C contiguously and all three are copied, then A, B and C must stay
    # adjacent after the layout, or the record reads whatever the new byte order put
    # between them. So any two copied chains with only copied chains between them belong
    # to one group, and the group is what gets a new offset. Measured failure this
    # prevents: a 6-byte `Hi!` inside a chain interior read three spaces when the chains
    # were compacted one by one.
    order = {chain: position for position, chain in enumerate(chains)}
    grouped: set[tuple[int, int]] = set()
    for record in records:
        touched = [chain for chain in chains
                   if chain in copied
                   and record.handle.decoded_start < chain[1]
                   and chain[0] < record.handle.decoded_end]
        if len(touched) < 2:
            continue
        first, last = order[touched[0]], order[touched[-1]]
        for position in range(first, last + 1):
            grouped.add(chains[position])

    groups: list[dict] = []
    for chain in chains:
        if chain not in copied:
            continue
        if grouped and groups and chain[0] == groups[-1]["end"]:
            groups[-1]["end"] = chain[1]
            continue
        groups.append({"start": chain[0], "end": chain[1]})

    blocks: list[dict] = []
    new_offset = 0
    for group in groups:
        units = list(struct.unpack_from(f"<{(group['end'] - group['start']) // 2}H",
                                        stream, group["start"]))
        blocks.append({"start": group["start"], "end": group["end"],
                       "new_offset": new_offset,
                       "new_length": group["end"] - group["start"], "units": units})
        new_offset += group["end"] - group["start"]

    if new_offset > HANDLE_START_MAX_BYTES:
        raise RepackError(
            f"selector {selector}: the copied groups alone need {new_offset} bytes, above "
            f"the {HANDLE_START_MAX_BYTES}-byte ceiling a 15-bit handle start field can "
            "address, so this container's pad cannot be removed by re-layout alone"
        )

    def new_offset_of(offset: int) -> int:
        chain = chain_of_offset[offset]
        if chain not in copied:
            return offset
        block = next(item for item in blocks if item["start"] <= offset < item["end"])
        return block["new_offset"] + (offset - block["start"])

    # THE REBUILD IS THE ORIGINAL STREAM WITH THE COPIED REGION COMPACTED. Every un-copied
    # byte keeps its offset, so a record that touches no copied chain stays valid for free;
    # the copied groups are packed end to end at the start of that region, and the room
    # they free up becomes trailing space units that no record's span contains.
    first = min((chain[0] for chain in copied), default=0)
    last = max((chain[1] for chain in copied), default=0)
    packed = bytearray()
    for block in blocks:
        packed += struct.pack(f"<{len(block['units'])}H", *block["units"])
    rebuilt = bytearray(stream[:first])
    rebuilt += packed
    freed = (last - first) - len(packed)
    if freed < 0:
        raise RepackError(
            f"selector {selector}: the copied groups are larger than the region they came "
            "from, which cannot be compacted in place"
        )
    rebuilt += bytes(SPACE.to_bytes(2, "little")) * (freed // 2)
    rebuilt += stream[last:]

    spans: list[dict] = []
    for record in records:
        start, end = record.handle.decoded_start, record.handle.decoded_end
        target = target_text(text_of(stream, start, end - start),
                             reference_text(reference, record)).rstrip(" ")
        new_start = new_offset_of(start)
        new_end = new_offset_of(end - 2) + 2
        # A record that did not move must read exactly what it read before, including any
        # pad it holds: only a record whose own bytes moved may lose padding. Anything
        # else would be a change nobody asked for.
        if new_start == start and new_end == end:
            expected = text_of(stream, start, end - start)
        else:
            expected = target
        spans.append({
            "record": f"{selector}:{start}:{end - start}",
            "new_start": new_start,
            "new_length": new_end - new_start,
            "new_key": f"{selector}:{new_start}:{new_end - new_start}",
            "handle": record.handle,
            "sites": list(record.sites),
            "spaces_dropped": text_of(stream, start, end - start).count(" ") - target.count(" "),
            "target": expected,
        })
    for span in spans:
        got = bytes(rebuilt[span["new_start"]:span["new_start"] + span["new_length"]])
        text = got.decode("utf-16le", "replace")
        if text != span["target"]:
            raise RepackError(
                f"selector {selector}: {span['record']} would read {text[:40]!r} after the "
                f"selective layout, not {span['target'][:40]!r}"
            )
    return {"rebuilt": bytes(rebuilt), "blocks": blocks, "spans": spans,
            "stream_length": len(stream), "reference": reference,
            "copied_chains": len(copied),
            "copied_bytes": sum(chain[1] - chain[0] for chain in copied)}


def plan_group(selector: int, stream: bytes, records, region: tuple[int, int],
               replacements: dict[str, str] | None = None) -> dict:
    """Re-lay one group of records inside its own region, changing only named wording.

    THE PROBLEM THIS SOLVES, AND WHY IT IS NOT A CONTAINER REBUILD. A record's text can be
    changed in place only when its own span is not read by another record. When it is, the
    group that reads it has to be re-laid out as a unit: the texts are written back to back
    from the region's start, each record's span is recomputed from where its text landed,
    the tail is filled with space units, and NOTHING OUTSIDE THE REGION MOVES, so every
    handle of every record outside it stays valid. That is the mechanism the merged dialog
    editor already uses for two adjacent records; this generalises it to the whole group.

    `replacements` maps a record key (`selector:start:length`) to the wording it must read
    afterwards. Every other record in the region must read exactly what it read before, and
    the rebuild REFUSES rather than writes if that fails.

    The region must not be crossed by a record that is not part of it: such a record would
    have to change content, and no evidence says how the engine expects that expressed.
    """
    start, end = region
    if start % 2 or end % 2 or not start < end <= len(stream):
        raise RepackError(f"selector {selector}: region 0x{start:X}..0x{end:X} is not a "
                          "legal aligned range of the decoded stream")
    # A region is only a group when no record leaves it. Any record that reaches past an
    # edge drags the whole region it belongs to along, so the region is grown until it is
    # closed rather than guessed at; the caller's range is the seed.
    while True:
        grown = [start, end]
        for record in records:
            r_start, r_end = record.handle.decoded_start, record.handle.decoded_end
            if r_start < grown[1] and grown[0] < r_end:
                grown[0] = min(grown[0], r_start)
                grown[1] = max(grown[1], r_end)
        if grown[0] == start and grown[1] == end:
            break
        start, end = grown
    inside, crossing = [], []
    for record in records:
        r_start, r_end = record.handle.decoded_start, record.handle.decoded_end
        if r_start < end and start < r_end:
            if start <= r_start and r_end <= end:
                inside.append(record)
            else:
                crossing.append(record)
    if crossing:
        raise RepackError(
            f"selector {selector}: {len(crossing)} record(s) cross the region boundary, so "
            "the region is not a closed group and a re-layout has no defined answer"
        )
    if not inside:
        raise RepackError(f"selector {selector}: no record lies inside the region")

    # THE REGION IS COMPOSED AS SEGMENTS, NOT OVERWRITTEN RECORD BY RECORD. Writing one
    # record's text at a time cannot work: a record that spans several smaller ones would
    # end up reading whatever the last write left under it. The segment map is the coarsest
    # partition such that every record's span is a run of whole segments, so each record's
    # span is exactly its own wording with the space units its readers expect between them.
    edges = sorted({edge for record in inside
                    for edge in (record.handle.decoded_start, record.handle.decoded_end)})
    segments: dict[tuple[int, int], str | None] = {
        (edges[index], edges[index + 1]): None for index in range(len(edges) - 1)}

    # Collect every claim first, then require the claims about any one unit to agree. A
    # last-write-wins composition would silently let one record's wording win over another
    # that reads the same byte, which is the corruption mode this project measured twice.
    claims: dict[tuple[int, int], str] = {}
    for record in inside:
        key = f"{selector}:{record.handle.decoded_start}:{record.handle.decoded_length}"
        text = text_of(stream, record.handle.decoded_start,
                       record.handle.decoded_length).rstrip(" ")
        text = replacements.get(key, text)
        index = record.handle.decoded_start
        for unit in text:
            segment = (index, index + 2)
            seated = claims.get(segment)
            if seated is not None and seated != unit:
                raise RepackError(
                    f"selector {selector}: records disagree about the unit at 0x{index:X} "
                    f"({seated!r} against {unit!r}); the group has no consistent wording"
                )
            claims[segment] = unit
            index += 2

    rebuilt = bytearray()
    for (seg_start, seg_end), _placeholder in sorted(segments.items()):
        value = "".join(claims[(offset, offset + 2)]
                        for offset in range(seg_start, seg_end, 2)
                        if (offset, offset + 2) in claims)
        if len(value) * 2 == seg_end - seg_start:
            rebuilt += value.encode("utf-16le")
        else:
            # No record reads this run, and the gap is filled with space units, never a
            # terminator: a zero would end an enclosing view early and truncate what
            # follows it.
            rebuilt += SPACE.to_bytes(2, "little") * ((seg_end - seg_start) // 2)

    spans: list[dict] = []
    for record in sorted(inside, key=lambda item: (item.handle.decoded_start,
                                                   item.handle.decoded_length)):
        key = f"{selector}:{record.handle.decoded_start}:{record.handle.decoded_length}"
        target = text_of(stream, record.handle.decoded_start,
                         record.handle.decoded_length).rstrip(" ")
        target = replacements.get(key, target)
        offset = record.handle.decoded_start - start
        got = bytes(rebuilt[offset:offset + len(target) * 2]).decode("utf-16le")
        if got != target:
            raise RepackError(
                f"selector {selector}: {key} would read {got[:48]!r} after the group "
                f"re-layout, not {target[:48]!r}"
            )
        original = text_of(stream, record.handle.decoded_start,
                           record.handle.decoded_length).rstrip(" ")
        spans.append({
            "record": key,
            "new_start": record.handle.decoded_start,
            "new_length": len(target) * 2,
            "handle": record.handle,
            "sites": list(record.sites),
            "target": target,
            "changed": target != original,
        })
    return {"rebuilt": bytes(rebuilt), "spans": spans, "region": (start, end),
            "changed": [span["record"] for span in spans if span["changed"]]}


def plan_duplicated(selector: int, stream: bytes, records, reference: bytes | None) -> dict:
    """One copy of every record's own text, so a shared pad can be dropped for good.

    WHY THIS IS THE ROUTE FOR A SHARED PAD. When a pad unit sits inside a chain a longer
    record also covers, no trimming can remove it: that longer record reads through the
    unit and would lose a character. The pad can only go if the shorter record stops
    sharing its bytes, which means giving it a copy of its own. Records whose spans touch
    no pad keep sharing nothing and are copied once each, because nothing about them is
    ambiguous.

    The price is paid in bytes, not in correctness: the stream becomes roughly the sum of
    the record texts instead of their union. That is a deliberate trade the caller chose
    by asking for duplication, and the caller owns where the grown container lives.
    """
    blocks: list[dict] = []
    new_offset = 0
    spans: list[dict] = []
    for record in sorted(records, key=lambda item: (item.handle.decoded_start,
                                                    item.handle.decoded_length)):
        start, end = record.handle.decoded_start, record.handle.decoded_end
        text = text_of(stream, start, end - start)
        body = target_text(text, reference_text(reference, record)).rstrip(" ")
        units = list(struct.unpack(f"<{len(body)}H", body.encode("utf-16le")))
        blocks.append({"start": start, "end": end, "new_offset": new_offset,
                       "new_length": len(body) * 2, "units": units,
                       "spaces_dropped": text.count(" ") - body.count(" ")})
        spans.append({
            "record": f"{selector}:{start}:{end - start}",
            "new_start": new_offset,
            "new_length": len(body) * 2,
            "new_key": f"{selector}:{new_offset}:{len(body) * 2}",
            "handle": record.handle,
            "sites": list(record.sites),
            "spaces_dropped": text.count(" ") - body.count(" "),
            "target": body,
        })
        new_offset += len(body) * 2
    rebuilt = bytearray()
    for block in blocks:
        rebuilt += struct.pack(f"<{len(block['units'])}H", *block["units"])
    return {"rebuilt": bytes(rebuilt), "blocks": blocks, "spans": spans,
            "stream_length": len(stream), "reference": reference}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out")
    parser.add_argument("--manifest")
    parser.add_argument("--selector", type=int, action="append", default=[])
    parser.add_argument("--duplicate", action="store_true",
                        help="give every record its own copy of its text")
    parser.add_argument("--retail",
                        help="the immutable retail image, whose record text decides "
                             "which space runs are the rename's pad and which are retail's")
    args = parser.parse_args()

    retail_streams: dict[int, bytes] = {}
    if args.retail:
        retail_image = Path(args.retail).read_bytes()
        for selector, pointer in container_pointers(retail_image).items():
            # Any container kind is readable here: `unpack` decodes both the stored form
            # and the packed one, and the reference is only ever read. The retail image
            # holds these containers PACKED, so a stored-only filter would leave the
            # reference empty and silently drop nothing.
            container = webfoot_lz.unpack(retail_image, pointer - ROM_BASE)
            if container.declared_size:
                retail_streams[selector] = bytes(container.data)

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise RepackError(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    pointers = container_pointers(image)
    wanted = args.selector or sorted(pointers)
    output = bytearray(image)
    grown: list[dict] = []
    report: dict = {"input": str(source), "input_sha256": got, "input_bytes": len(image),
                    "containers": [], "handle_changes": [], "container_relocations": []}

    for selector in wanted:
        pointer = pointers.get(selector)
        if pointer is None:
            report["containers"].append({"selector": selector, "skipped": "no container"})
            continue
        container = webfoot_lz.unpack(image, pointer - ROM_BASE)
        if container.kind != 0:
            report["containers"].append(
                {"selector": selector, "skipped": f"container kind {container.kind} is not "
                                                  "the stored form"})
            continue
        stream = bytes(container.data)
        records = cd.dialogue_record_inventory(image, selector, len(stream))
        if not records:
            report["containers"].append({"selector": selector, "skipped": "no records"})
            continue
        if args.duplicate:
            result = plan_duplicated(selector, stream, records, retail_streams.get(selector))
        else:
            result = plan_container(image, selector, stream, records)
        problems = verify_plan(selector, stream, records, result)
        if problems:
            for row in problems[:5]:
                print(f"  PROBLEM {row}")
            raise RepackError(
                f"selector {selector}: {len(problems)} record(s) would not read their own "
                "text after the rebuild; nothing was written"
            )
        if args.out and len(result["rebuilt"]) <= len(stream):
            payload_at = pointer - ROM_BASE + CONTAINER_HEADER
            output[payload_at:payload_at + len(stream)] = result["rebuilt"]
            for span in result["spans"]:
                for site in span["sites"]:
                    # The handle fields are BYTE values; pack_handle divides them into
                    # halfwords itself. Passing halves here wrote half of every start and
                    # length, which the earlier revision did.
                    word = span["handle"].replace(
                        decoded_start=span["new_start"],
                        decoded_length=span["new_length"]).encode().to_bytes(4, "little")
                    before = bytes(image[site:site + 4])
                    if before == word:
                        continue
                    report["handle_changes"].append(
                        {"offset": site, "old": before.hex(), "new": word.hex(),
                         "key": span["record"], "new_key": span["new_key"]})
                    output[site:site + 4] = word
        if args.out and len(result["rebuilt"]) > len(stream):
            grown.append({"selector": selector, "rebuilt": result["rebuilt"],
                          "spans": result["spans"]})
        report["containers"].append({
            "selector": selector,
            "container_file_offset": pointer - ROM_BASE,
            "decoded_size": len(stream),
            "rebuilt_size": len(result["rebuilt"]),
            "blocks": len(result["blocks"]),
            "records": len(result["spans"]),
            "spaces_dropped": sum(span["spaces_dropped"] for span in result["spans"]),
            "spans": [{k: v for k, v in span.items() if k != "handle"}
                      for span in result["spans"]],
        })
        print(f"selector {selector}: {len(stream)} -> {len(result['rebuilt'])} bytes, "
              f"{len(result['blocks'])} chain(s), {len(result['spans'])} record(s), "
              f"{sum(span['spaces_dropped'] for span in result['spans'])} space(s) dropped")

    if args.out:
        # A rebuilt stream longer than the container it replaces cannot go back where it
        # was: it is appended past the end of image and its table slot is repointed. The
        # table itself does not move, so one word per container is the whole relocation,
        # and nothing else in the image shifts.
        for entry in grown:
            offset = len(output)
            while offset % 4:
                output.append(0x00)
                offset += 1
            output += struct.pack("<II", 0, len(entry["rebuilt"]))
            output += entry["rebuilt"]
            table_slot = live_table(image) + entry["selector"] * 4
            word = (ROM_BASE + offset).to_bytes(4, "little")
            report["container_relocations"].append(
                {"selector": entry["selector"], "table_slot": table_slot,
                 "old_pointer": bytes(image[table_slot:table_slot + 4]).hex(),
                 "new_pointer": word.hex(), "file_offset": offset,
                 "bytes": len(entry["rebuilt"])})
            output[table_slot:table_slot + 4] = word
            for span in entry["spans"]:
                for site in span["sites"]:
                    handle = span["handle"].replace(
                        decoded_start=span["new_start"],
                        decoded_length=span["new_length"]).encode().to_bytes(4, "little")
                    before = bytes(image[site:site + 4])
                    if before == handle:
                        continue
                    report["handle_changes"].append(
                        {"offset": site, "old": before.hex(), "new": handle.hex(),
                         "key": span["record"], "new_key": span["new_key"]})
                    output[site:site + 4] = handle
        target = Path(args.out)
        target.write_bytes(bytes(output))
        report["output"] = str(target)
        report["output_sha256"] = sha256_bytes(bytes(output))
        report["output_bytes"] = len(output)
        if args.manifest:
            Path(args.manifest).write_text(json.dumps(report, indent=2) + "\n",
                                           encoding="utf-8")
        print(f"# wrote {target} {len(output)} bytes sha256 {report['output_sha256']}")
        print(f"# handle words rewritten: {len(report['handle_changes'])}")
    return 0


import struct  # noqa: E402  (kept last so the module reads top-down)

if __name__ == "__main__":
    sys.exit(main())
