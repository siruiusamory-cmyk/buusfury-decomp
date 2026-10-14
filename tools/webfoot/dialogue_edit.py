"""The new text replaces the old inside the stored payload with no re-encode, because webfoot_lz.pack cannot emit kind 0 and the containers this table names are stored verbatim."""
from __future__ import annotations

import hashlib
import struct
from typing import NamedTuple

from tools.webfoot.compressed_dialogue import dialogue_record_inventory
from tools.webfoot.formats import webfoot_lz as wl
from tools.webfoot.handles import pack_handle

#: The live dialogue container table's own literal, as a file offset. On a post-splice image the
#: retail literal at 0x7B5B64 no longer names the live table; this one does.
TABLE_LITERAL = 0x123CC
ROM_BASE = 0x08000000
CONTAINER_HEADER = 8
# The engine's break-point unit, used to fill the rest of a re-laid out region.
SPACE = 0x0020


class DialogueEditError(ValueError):
    """Raised when a guard refuses rather than writing an unproven byte."""


class LineEdit(NamedTuple):
    """The caller's claim about who speaks the line, recorded rather than verified."""

    speaker: str
    old_text: str
    new_text: str
    decoded_start: int | None = None
    decoded_length: int | None = None


class DialogueRewrite(NamedTuple):
    """One container's worth of edits, all applied in a single pass."""

    selector: int
    lines: tuple[LineEdit, ...]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def container_file_offset(image: bytes, selector: int) -> int:
    table = struct.unpack_from("<I", image, TABLE_LITERAL)[0] - ROM_BASE
    word = table + selector * 4
    pointer = struct.unpack_from("<I", image, word)[0]
    if not ROM_BASE <= pointer < ROM_BASE + len(image):
        raise DialogueEditError(f"selector {selector} is not a ROM pointer ({pointer:#010x})")
    return pointer - ROM_BASE


def stored_payload(image: bytes, offset: int) -> bytes:
    """The container's decoded stream, refusing any form that is not stored verbatim."""
    container = wl.unpack(image, offset)
    payload = image[offset + CONTAINER_HEADER: offset + CONTAINER_HEADER + container.declared_size]
    if bytes(container.data) != payload:
        raise DialogueEditError(
            f"the container at {offset:#x} is kind {container.kind} and its payload is not "
            "stored verbatim, so an in-place edit is not proven for it"
        )
    return payload


def find_record(image: bytes, selector: int, old_text: str) -> tuple[int, int]:
    """The one record whose text is exactly old_text, refusing zero matches and more than one because selecting the first would be a guess about identity."""
    offset = container_file_offset(image, selector)
    payload = stored_payload(image, offset)
    wanted = old_text.encode("utf-16le")
    candidates = []
    for record in dialogue_record_inventory(image, selector, len(payload)):
        start = record.handle.decoded_start
        length = record.handle.decoded_length
        if payload[start:start + length] == wanted:
            candidates.append(record)
    if not candidates:
        raise DialogueEditError(
            f"no record in selector {selector} holds the wording {old_text!r}; nothing would be "
            "edited, so this is refused rather than skipped"
        )
    if len(candidates) > 1:
        listed = ", ".join(
            f"({r.handle.decoded_start}, {r.handle.decoded_length}) at "
            f"{[hex(site) for site in r.sites]}" for r in candidates)
        raise DialogueEditError(
            f"{len(candidates)} records in selector {selector} hold the wording {old_text!r}: "
            f"{listed}. Wording does not identify a speaker, so this is refused rather than "
            "resolved by picking one"
        )
    record = candidates[0]
    return record.handle.decoded_start, record.handle.decoded_length


def _resolve(image: bytes, selector: int, edit: LineEdit) -> dict:
    start, length = find_record(image, selector, edit.old_text)
    if edit.decoded_start is not None or edit.decoded_length is not None:
        if (edit.decoded_start, edit.decoded_length) != (start, length):
            raise DialogueEditError(
                f"{edit.speaker}: the wording {edit.old_text!r} is held by the record "
                f"({start}, {length}), but the edit names "
                f"({edit.decoded_start}, {edit.decoded_length}); refusing a contradiction"
            )
    if any(ord(character) < 0x20 for character in edit.new_text):
        raise DialogueEditError(f"{edit.speaker}: the replacement carries a control unit")
    return {"speaker": edit.speaker, "decoded_start": start, "decoded_length": length,
            "old_text": edit.old_text, "new_text": edit.new_text}


def context(image: bytes, selector: int, start: int, length: int) -> dict:
    """The evidence a human needs to check a speaker claim, with a partial overlap reported rather than written because the planner refuses it."""
    offset = container_file_offset(image, selector)
    payload = stored_payload(image, offset)
    sites: list[int] = []
    enclosing: list[tuple[int, int]] = []
    partial: list[tuple[int, int]] = []
    end = start + length
    for record in dialogue_record_inventory(image, selector, len(payload)):
        record_start = record.handle.decoded_start
        record_end = record_start + record.handle.decoded_length
        if record_start == start and record.handle.decoded_length == length:
            sites = list(record.sites)
        elif record_start <= start and record_end >= end:
            enclosing.append((record_start, record.handle.decoded_length))
        elif record_start < end and record_end > start:
            partial.append((record_start, record.handle.decoded_length))
    return {"record_sites": sites, "record_sites_hex": [hex(site) for site in sites],
            "enclosing_records": enclosing,
            "partial_overlaps": partial,
            "speaker_evidence": "caller-claim; the speaker is the scene's actor, and no evidence "
                                "in the text record establishes it"}


def plan(image: bytes, rewrite: DialogueRewrite) -> dict:
    """The region to rewrite and the handle words to update, each verified against the base."""
    offset = container_file_offset(image, rewrite.selector)
    payload = stored_payload(image, offset)
    base = offset + CONTAINER_HEADER
    targets = [_resolve(image, rewrite.selector, edit) for edit in rewrite.lines]

    ordered = sorted(targets, key=lambda t: t["decoded_start"])
    for left, right in zip(ordered, ordered[1:]):
        if left["decoded_start"] + left["decoded_length"] != right["decoded_start"]:
            raise DialogueEditError(
                f"{left['speaker']} and {right['speaker']} are not adjacent; growing one would "
                "move every record after it, which this engine does not do"
            )
    region_start = ordered[0]["decoded_start"]
    region_end = ordered[-1]["decoded_start"] + ordered[-1]["decoded_length"]
    region_bytes = region_end - region_start
    needed = sum(len(t["new_text"].encode("utf-16le")) for t in ordered)
    if needed > region_bytes:
        raise DialogueEditError(
            f"the group needs {needed} bytes and its region holds {region_bytes}; a container "
            "re-layout is a different mechanism"
        )

    records = {f"{r.handle.decoded_start}:{r.handle.decoded_length}": r
               for r in dialogue_record_inventory(image, rewrite.selector, len(payload))}
    # A record that only PARTLY covers the region would read mixed old and new text once the
    # bytes move under it, and nothing else in this engine would notice. A record that fully
    # contains the region is a scene view and is expected; a partial overlap is refused.
    group = {(target["decoded_start"], target["decoded_length"]) for target in ordered}
    for record in dialogue_record_inventory(image, rewrite.selector, len(payload)):
        start = record.handle.decoded_start
        length = record.handle.decoded_length
        if (start, length) in group:
            continue
        if start < region_end and start + length > region_start:
            if start > region_start or start + length < region_end:
                raise DialogueEditError(
                    f"the record ({start}, {length}) overlaps the rewritten region "
                    f"({region_start}, {region_bytes}) without containing it, so it would read "
                    "mixed old and new text; refusing rather than writing that"
                )
    region = bytearray()
    handles = []
    cursor = region_start
    for target in ordered:
        text = target["new_text"].encode("utf-16le")
        old_handle = pack_handle(rewrite.selector, target["decoded_start"],
                                 target["decoded_length"])
        record = records.get(f"{target['decoded_start']}:{target['decoded_length']}")
        if record is None:
            raise DialogueEditError(
                f"{target['speaker']}: no record carries ({target['decoded_start']}, "
                f"{target['decoded_length']})"
            )
        if not record.sites:
            raise DialogueEditError(
                f"{target['speaker']}: the record is not named by any word, so nothing would "
                "reach the replacement"
            )
        for site in record.sites:
            if struct.unpack_from("<I", image, site)[0] != old_handle:
                raise DialogueEditError(f"the handle word at {site:#x} is not the one replaced")
        handles.append({
            "speaker": target["speaker"],
            "old_text": target["old_text"],
            "new_text": target["new_text"],
            "old_handle": old_handle,
            "old_handle_hex": f"0x{old_handle:08X}",
            "was": [target["decoded_start"], target["decoded_length"]],
            "new_start": cursor,
            "new_length": len(text),
            "new_handle": pack_handle(rewrite.selector, cursor, len(text)),
            "sites": list(record.sites),
            "context": context(image, rewrite.selector, target["decoded_start"],
                               target["decoded_length"]),
        })
        region.extend(text)
        cursor += len(text)
    region.extend(SPACE.to_bytes(2, "little") * ((region_bytes - len(region)) // 2))
    if len(region) != region_bytes:
        raise DialogueEditError("the padded region does not fill the region exactly")

    return {
        "selector": rewrite.selector,
        "container_offset": offset,
        "payload_offset": base,
        "region_start": region_start,
        "region_bytes": region_bytes,
        "region_file_offset": base + region_start,
        "region": bytes(region),
        "handles": handles,
    }


def apply(image: bytes, planned: dict) -> bytes:
    out = bytearray(image)
    at = planned["region_file_offset"]
    length = len(planned["region"])
    out[at:at + length] = planned["region"]
    for handle in planned["handles"]:
        for site in handle["sites"]:
            current = struct.unpack_from("<I", out, site)[0]
            if current != handle["old_handle"]:
                raise DialogueEditError(f"the handle word at {site:#x} moved under this write")
            struct.pack_into("<I", out, site, handle["new_handle"])
    return bytes(out)


def verify(base: bytes, out: bytes, planned: dict) -> dict:
    """Reopen the output and require the new wording, the new handles, and nothing else."""
    selector = planned["selector"]
    offset = container_file_offset(out, selector)
    payload = stored_payload(out, offset)
    records = {f"{r.handle.decoded_start}:{r.handle.decoded_length}": r
               for r in dialogue_record_inventory(out, selector, len(payload))}
    read_back = {}
    for handle in planned["handles"]:
        key = f"{handle['new_start']}:{handle['new_length']}"
        record = records.get(key)
        if record is None:
            raise DialogueEditError(f"the output carries no record for {key}")
        text = payload[handle["new_start"]:handle["new_start"] + handle["new_length"]]
        read_back[f"{handle['new_start']}:{handle['new_length']}"] = text.decode("utf-16le")
        if text.decode("utf-16le") != handle["new_text"]:
            raise DialogueEditError(f"{handle['speaker']}: the output does not read the new line")
        if handle["old_text"] in payload.decode("utf-16le"):
            raise DialogueEditError(f"{handle['speaker']}: the old wording survives")

    before = stored_payload(base, container_file_offset(base, selector))
    # Two coordinate spaces on purpose: the decoded payload is indexed from its own start, and
    # the image is indexed from the file. Mixing them is how a confinement check passes a
    # change it should have caught.
    payload_region = set(range(planned["region_start"],
                               planned["region_start"] + planned["region_bytes"]))
    image_region = set(range(planned["region_file_offset"],
                             planned["region_file_offset"] + planned["region_bytes"]))
    changed_outside_payload = [i for i in range(len(payload))
                               if payload[i] != before[i] and i not in payload_region]
    if changed_outside_payload:
        raise DialogueEditError(
            f"{len(changed_outside_payload)} decoded bytes changed outside the region"
        )
    handle_sites = {site + i for handle in planned["handles"]
                    for site in handle["sites"] for i in range(4)}
    image_diff = [i for i in range(len(out)) if out[i] != base[i]]
    stray = [i for i in image_diff if i not in image_region and i not in handle_sites]
    if stray:
        raise DialogueEditError(
            f"{len(stray)} image bytes changed outside the region and the handle words; "
            f"first at {stray[0]:#x}"
        )
    return {
        "read_back": read_back,
        "image_bytes_changed": len(image_diff),
        "image_bytes_changed_in_region": len([i for i in image_diff if i in image_region]),
        "handle_words_changed": len([i for i in image_diff if i in handle_sites]),
        "container_packed_size_before": wl.unpack(base, offset).packed_size,
        "container_packed_size_after": wl.unpack(out, offset).packed_size,
    }


def rewrite_dialogue(image: bytes, rewrite: DialogueRewrite) -> tuple[bytes, dict]:
    """Apply one rewrite to an image and return the new image and its report."""
    planned = plan(image, rewrite)
    out = apply(image, planned)
    report = {
        "selector": rewrite.selector,
        "container_offset": planned["container_offset"],
        "region_start": planned["region_start"],
        "region_bytes": planned["region_bytes"],
        "region_file_offset": planned["region_file_offset"],
        "handles": planned["handles"],
        "lines": [{"speaker": edit.speaker, "old_text": edit.old_text,
                   "new_text": edit.new_text} for edit in rewrite.lines],
        "verification": verify(image, out, planned),
    }
    return out, report
