"""Packed text-handle decode and recovery for one verified ROM profile.

A decoded string has no ROM address of its own; the durable identity is the
packed u32 an event-resource record stores to address it. These functions
unpack that word's bit layout and walk the record pool to recover the handle a
decoded phrase's span implies. Lifted from `cli.py` so both the CLI and the
Workbench GUI call the same code (WORKBENCH-001).
"""

from __future__ import annotations

import struct

from .binary import GBA_ROM_BASE


#: Bit layout of a packed text handle, corroborated in situ by the
#: `lsls #26 / lsrs #24` pair at 0x08012244/0x08012246: bits 0-5 select the
#: container, bits 6-20 give the decoded start in halfwords, bits 21-31 the
#: decoded length in halfwords. TEXT-HANDLE-001.
HANDLE_SELECTOR_MASK = 0x3F
HANDLE_START_MASK = 0x7FFF
HANDLE_START_SHIFT = 6
HANDLE_LENGTH_SHIFT = 21


def unpack_handle(value: int) -> tuple[int, int, int]:
    """`(selector, decoded start, decoded length)`, the last two in BYTES."""
    return (value & HANDLE_SELECTOR_MASK,
            ((value >> HANDLE_START_SHIFT) & HANDLE_START_MASK) * 2,
            (value >> HANDLE_LENGTH_SHIFT) * 2)


def recover_handle(image: bytes, container_index: int, phrase_start: int,
                   phrase_size: int) -> dict:
    """Name one decoded phrase by the ROM-resident handle that defines it.

    A decoded string has no ROM address of its own — it exists only after
    decompression — so the durable identity is the packed u32 an event-resource
    record stores to address it. This walks the record pool for word-aligned
    occurrences of the handle the phrase's own span implies.

    The span must be the PHRASE's, never the indexed run's. Runs are segmented
    by control units and routinely merge several handle-defined records: the
    real run at decoded offset 0x12A spans nine distinct handles, so keying on
    it would return nine identities for one phrase. That is the same collapse
    the result shape forbids, in mirror image.

    A phrase is a SUBSTRING of the record that holds it — a searcher types part
    of a message, not all of it — so the record is the one whose span CONTAINS
    the phrase's. Containment alone is not enough to name one record, because
    long records overlap short ones: searching the target phrase finds thirteen
    containing records, most of them unrelated messages that merely span the
    same bytes. The narrowest containing record is the answer, being the
    tightest one that still covers every character searched for.

    Returns ONE identity or none. Never a guess: a span no record covers
    reports its absence and says why.
    """
    from .data.placement_contracts import CONTRACTS

    resource = CONTRACTS["buus_fury_usa_rev0_01c1707f"]["event_resource"]
    pool = resource["pool_start"] - GBA_ROM_BASE
    table = resource["table"] - GBA_ROM_BASE
    if not 0 <= pool < table <= len(image):
        return {"packed_handle": None,
                "unrecovered_because": "the event-resource record pool lies "
                                       "outside this image"}

    phrase_end = phrase_start + phrase_size
    sites: dict[int, list[int]] = {}
    handle = None
    narrowest = None
    for offset in range(pool, table, 4):
        value = struct.unpack_from("<I", image, offset)[0]
        selector, start, size = unpack_handle(value)
        if (selector != container_index or not size
                or start > phrase_start or phrase_end > start + size):
            continue
        sites.setdefault(value, []).append(GBA_ROM_BASE + offset)
        # Ties break on the handle value so one image always answers the same
        # way; a search result that reordered between runs would not be citable.
        if narrowest is None or (size, value) < narrowest:
            narrowest, handle = (size, value), value

    references = [] if handle is None else sites[handle]

    if handle is None:
        return {"packed_handle": None,
                "unrecovered_because": "no event-resource record addresses this "
                                       "exact decoded span; the phrase may sit "
                                       "inside a larger record rather than at "
                                       "its boundary"}

    selector, start, size = unpack_handle(handle)
    return {
        "packed_handle": f"0x{handle:08X}",
        "handle_selector": selector,
        "handle_decoded_start": f"0x{start:X}",
        "handle_decoded_length": f"0x{size:X}",
        # One identity, a LIST of sites. The handle NAMES the string; these are
        # the places a patcher would rewrite to repoint it. Collapsing the two
        # would turn one message into several.
        "reference_sites": [f"0x{site:08X}" for site in references],
        "reference_site_count": len(references),
    }
